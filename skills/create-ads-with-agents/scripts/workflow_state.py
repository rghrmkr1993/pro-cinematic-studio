#!/usr/bin/env python3
"""Local project ledger; never submits jobs or grants provider permissions."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import sys
import tempfile


STATES = {
    "reserved": {"reserved", "submitting", "no_submission"},
    "submitting": {"submitting", "pending", "completed", "failed", "unknown", "no_submission"},
    "pending": {"pending", "completed", "failed", "canceled", "unknown"},
    "unknown": {"unknown", "pending", "completed", "failed", "canceled", "no_submission"},
    "completed": {"completed"},
    "failed": {"failed"},
    "canceled": {"canceled"},
    "no_submission": {"no_submission"},
}

# These are policy families, not guessed provider IDs. Actual IDs come from discovery.
ROLE_MODELS = {
    "location": (0, "nano_banana_pro"),
    "character": (1, "seedream_5"),
    "prop": (2, "nano_banana_pro"),
    "product": (2, "nano_banana_pro"),
    "composed_frame": (3, "nano_banana_pro"),
    "static": (3, "nano_banana_pro"),
    "video": (4, "seedance_2_5"),
    # Separate audio has no locked family or fixed position; explicit dependencies still apply.
    "audio": (None, None),
}
MEDIA_DELIVERABLES = {"static", "video"}
PRODUCTION_MODES = {"fresh_generation", "edit_only"}
AUDIENCE_DECISIONS = ("chosen_segment", "trigger", "desired_outcome", "objection", "creative_implication")


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def references(value, required=False):
    return (isinstance(value, list) and (bool(value) or not required)
            and all(nonempty(ref) for ref in value))


def production_mode(data):
    # An uploaded photo is a generation input, not an implicit request for local layouts.
    return data["brief"].get("production_mode", "fresh_generation")


def validate_production_mode(data, production=False):
    if data["brief"].get("deliverable") not in MEDIA_DELIVERABLES:
        return []
    mode = production_mode(data)
    if mode not in PRODUCTION_MODES:
        return ["Invalid production_mode; use fresh_generation or explicit edit_only"]
    if mode != "edit_only":
        return []
    errors = []
    authorization = data["brief"].get("edit_only_authorization", {})
    if (not isinstance(authorization, dict)
            or not nonempty(authorization.get("user_instruction"))
            or not nonempty(authorization.get("source_ref"))):
        errors.append("edit_only requires the explicit user_instruction and its source_ref; unavailable Higgsfield is not authorization")
    if production:
        errors.append("edit_only does not authorize generation; update the brief from an actual user generation request")
    return errors


def validate_audience_research(data):
    """Check the recorded evidence contract, not the truth of research artifacts."""
    errors = []
    brief = data["brief"]
    mode = brief.get("mode", "live")  # Existing projects are live unless explicitly marked demo.
    research = data.get("audience_research")
    if not isinstance(research, dict):
        return ["Current audience research is required before concepts, production or delivery"]
    if research.get("brief_revision") != brief.get("revision"):
        errors.append("Audience research must match the current brief revision; review reuse explicitly")
    if research.get("mode") != mode:
        errors.append("Audience research mode must match the brief; demo evidence cannot qualify live work")
    status = research.get("status")
    if status not in {"complete", "limited"}:
        errors.append("Audience research must be complete or candidly limited")
    if not references(research.get("artifact_refs"), required=True):
        errors.append("Audience research needs actual artifact_refs")
    for field in AUDIENCE_DECISIONS:
        if not nonempty(research.get(field)):
            errors.append(f"Audience research needs {field}")
    if status == "limited":
        if (not nonempty(research.get("limitations"))
                or not references(research.get("missing_fields"), required=True)):
            errors.append("Limited audience research needs candid limitations and nonempty missing_fields")
    basis = research.get("evidence_basis")
    if mode == "live" and basis not in {"inspected_sources", "supplied_research"}:
        errors.append("Live audience research needs inspected_sources or supplied_research evidence")
    if mode == "demo":
        if basis not in {"inspected_sources", "supplied_research", "illustrative"}:
            errors.append("Demo audience research needs an explicit evidence_basis")
        elif basis == "illustrative" and status != "limited":
            errors.append("Illustrative demo research must be limited, with missing live verification recorded")
    findings = research.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("Audience research needs nonempty findings")
    else:
        for finding in findings:
            if not isinstance(finding, dict) or not nonempty(finding.get("finding")):
                errors.append("Every audience finding needs nonempty finding text")
                continue
            if basis in {"inspected_sources", "supplied_research"} and not references(finding.get("source_refs"), required=True):
                errors.append("Every evidence-based audience finding needs actual inspected/supplied source_refs")
            if mode == "demo" and basis == "illustrative" and not nonempty(finding.get("demo_basis")):
                errors.append("Every demo audience finding needs an explicit illustrative demo_basis")
    return errors


def current_script_review(data):
    review = data.get("script_review", {})
    return (isinstance(review, dict) and review.get("verdict") == "pass"
            and review.get("brief_revision") == data["brief"].get("revision")
            and nonempty(review.get("reviewer"))
            and references(review.get("artifact_refs"), required=True))


def completed_asset(data, asset):
    """A reference alone does not establish that a planned generation completed."""
    return nonempty(asset.get("result_ref")) and any(
        job.get("asset_id") == asset.get("id") and job.get("status") == "completed"
        and job.get("plan_revision") == data["generation_plan"].get("brief_revision")
        and job.get("provider") == "higgsfield" and job.get("model_id") == asset.get("model_id")
        and job.get("result_ref") == asset.get("result_ref") and nonempty(job.get("job_id"))
        for job in data.get("jobs", []))


def validate_generation(data):
    errors = []
    capabilities = data.get("capabilities", {})
    provider = capabilities.get("higgsfield", {}) if isinstance(capabilities, dict) else {}
    if not isinstance(provider, dict):
        provider = {}
    if (provider.get("available") is not True or not nonempty(provider.get("checked_at"))
            or not references(provider.get("evidence_refs"), required=True)):
        errors.append("Higgsfield capability discovery needs availability, date and evidence references")
    models = {}
    rows = provider.get("models", [])
    if not isinstance(rows, list):
        rows = []
        errors.append("Higgsfield models must be a list")
    for model in rows:
        if not isinstance(model, dict) or not nonempty(model.get("model_id")):
            errors.append("Each discovered model needs its actual provider model_id")
            continue
        model_id = model["model_id"]
        if model_id in models:
            errors.append(f"Duplicate discovered model ID: {model_id}")
        if (not nonempty(model.get("family"))
                or model.get("verified") is not True
                or not references(model.get("evidence_refs"), required=True)):
            errors.append(f"Model {model_id} needs a verified family and evidence references")
        models[model_id] = model
    plan = data.get("generation_plan", {})
    if not isinstance(plan, dict):
        plan = {}
    if plan.get("brief_revision") != data["brief"].get("revision"):
        errors.append("Generation plan must match the current brief revision")
    assets = plan.get("assets")
    if not isinstance(assets, list) or not assets:
        return errors + ["Generation plan needs an ordered nonempty assets list"]
    seen, previous_stage = set(), -1
    for asset in assets:
        if not isinstance(asset, dict) or not nonempty(asset.get("id")):
            errors.append("Planned assets need nonempty IDs")
            continue
        asset_id = asset["id"]
        if asset_id in seen:
            errors.append(f"Duplicate planned asset ID: {asset_id}")
        role = asset.get("role")
        if role not in ROLE_MODELS:
            errors.append(f"Unknown generation role for asset {asset_id}")
        else:
            stage, family = ROLE_MODELS[role]
            if stage is not None and stage < previous_stage:
                errors.append("Plan order must be locations, characters, props/products, frames/statics, videos")
            if stage is not None:
                previous_stage = max(previous_stage, stage)
            model = models.get(asset.get("model_id"), {})
            if role == "audio":
                if (model.get("verified") is not True
                        or not references(model.get("output_types"), required=True)
                        or "audio" not in model["output_types"]):
                    errors.append(f"Audio asset {asset_id} needs a verified Higgsfield audio capability")
            elif model.get("family") != family or model.get("verified") is not True:
                errors.append(f"Asset {asset_id} requires a verified {family} model ID")
        if asset.get("provider") != "higgsfield":
            errors.append(f"Asset {asset_id} must use Higgsfield")
        deps = asset.get("depends_on")
        if not references(deps) or len(deps) != len(set(deps)) or any(dep not in seen for dep in deps):
            errors.append(f"Asset {asset_id} dependencies must be unique earlier asset IDs")
        if not references(asset.get("input_refs")):
            errors.append(f"Asset {asset_id} needs input_refs for supplied assets (empty is allowed)")
        seen.add(asset_id)
    return errors


def validate_deliverables(data, delivery=False):
    errors = []
    rows = data.get("deliverables")
    if not isinstance(rows, list) or not rows:
        return ["Creative output needs a nonempty deliverables list"]
    plan = data.get("generation_plan", {})
    plan_assets = plan.get("assets", []) if isinstance(plan, dict) else []
    if not isinstance(plan_assets, list):
        plan_assets = []
    assets = {asset["id"]: asset for asset in plan_assets
              if isinstance(asset, dict) and nonempty(asset.get("id"))}
    concepts = {concept["id"] for concept in data["concepts"]}
    ids, results = set(), set()
    for row in rows:
        if not isinstance(row, dict) or not nonempty(row.get("id")):
            errors.append("Deliverables need nonempty IDs")
            continue
        output_id = row["id"]
        if output_id in ids:
            errors.append(f"Duplicate deliverable ID: {output_id}")
        ids.add(output_id)
        if row.get("type") != data["brief"].get("deliverable"):
            errors.append(f"Deliverable {output_id} type must match the requested deliverable")
        if row.get("concept_id") not in concepts:
            errors.append(f"Deliverable {output_id} needs a valid concept_id")
        cta = row.get("cta", {})
        if not isinstance(cta, dict) or not nonempty(cta.get("text")) or not nonempty(cta.get("destination")):
            errors.append(f"Deliverable {output_id} needs CTA text and a destination")
        asset_ids = row.get("asset_ids", [])
        if row.get("type") in MEDIA_DELIVERABLES:
            fresh = production_mode(data) == "fresh_generation"
            source_refs = row.get("source_refs", [])
            if not references(source_refs):
                errors.append(f"Deliverable {output_id} source_refs must be a list of actual supplied/approved references")
                source_refs = []
            if not references(asset_ids) or any(ref not in assets for ref in asset_ids):
                errors.append(f"Deliverable {output_id} needs valid generation asset_ids")
                continue
            if not asset_ids and not source_refs:
                errors.append(f"Deliverable {output_id} needs generated asset_ids or supplied source_refs")
            roles = {assets[ref].get("role") for ref in asset_ids}
            if fresh and not asset_ids:
                errors.append(f"Fresh deliverable {output_id} requires Higgsfield generation; supplied photos or local layouts cannot replace it")
            if fresh and row["type"] == "video" and "video" not in roles:
                errors.append(f"Fresh video deliverable {output_id} needs a generated video asset")
            if (fresh and row["type"] == "static"
                    and not roles.intersection({"static", "composed_frame", "character", "product"})):
                errors.append(f"Fresh static deliverable {output_id} needs a generated static, composed_frame, character or product visual")
            if not fresh and not source_refs and row["type"] == "video" and "video" not in roles:
                errors.append(f"Video deliverable {output_id} needs a generated video asset or supplied media")
            if (not fresh and not source_refs and row["type"] == "static"
                    and not roles.intersection({"static", "composed_frame", "character", "product"})):
                errors.append(f"Static deliverable {output_id} needs a static, composed_frame, character or product asset, or supplied media")
            if delivery:
                required = set(asset_ids)
                pending = list(asset_ids)
                while pending:
                    deps = assets[pending.pop()].get("depends_on", [])
                    if not references(deps):
                        continue  # The generation-plan gate reports malformed dependencies.
                    for dep in deps:
                        if dep in assets and dep not in required:
                            required.add(dep)
                            pending.append(dep)
                for asset_id in sorted(required):
                    if not completed_asset(data, assets[asset_id]):
                        errors.append(f"Delivery requires a completed provider job and result for asset {asset_id}")
        if delivery:
            if not nonempty(row.get("result_ref")):
                errors.append(f"Deliverable {output_id} needs an actual final result_ref")
            else:
                results.add(row["result_ref"])
    if delivery:
        review = data.get("final_review", {})
        if not isinstance(review, dict):
            review = {}
        if (review.get("verdict") != "pass" or review.get("anti_slop_verdict") != "pass"
                or review.get("brief_revision") != data["brief"].get("revision")
                or not nonempty(review.get("reviewer")) or not nonempty(review.get("review_ref"))
                or not references(review.get("artifact_refs"), required=True)
                or not references(review.get("deliverable_ids"), required=True)):
            errors.append("Delivery needs a current final review with pass, anti_slop_verdict pass, reviewer and review/output references")
        else:
            if not ids.issubset(set(review["deliverable_ids"])) or not results.issubset(set(review["artifact_refs"])):
                errors.append("Final review must cover every deliverable ID and its actual result_ref")
    return errors


def now():
    return datetime.now(timezone.utc).isoformat()


def credits(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Credits must be a finite nonnegative number") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("Credits must be a finite nonnegative number")
    return result


def project_path(value):
    path = Path(value).expanduser().resolve()
    root = Path(__file__).resolve().parents[1]
    if path == root or root in path.parents:
        raise ValueError("Store project data outside the reusable skill directory")
    return path


@contextmanager
def locked(path):
    # Linux/macOS helper. On hosts without fcntl use one sequential writer.
    try:
        import fcntl
    except ImportError as exc:
        raise ValueError("This helper requires fcntl; use a sequential manual ledger on this host") from exc
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path) + ".lock", "a", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def save(path, data):
    data["updated_at"] = now()
    fd, tmp = tempfile.mkstemp(prefix=".ad-state-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def load(path):
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Unsupported project schema")
    return data


def committed(data):
    return sum((credits(j.get("charged_credits", j["reserved_credits"]))
                for j in data["jobs"]), Decimal("0"))


def summary(data):
    total = committed(data)
    cap = data["budget"]["cap_credits"]
    return {
        "route": data["brief"]["route"],
        "deliverable": data["brief"]["deliverable"],
        "job_count": len(data["jobs"]),
        "committed_credits": str(total),
        "cap_credits": cap,
        "remaining_credits": None if cap is None else str(credits(cap) - total),
        "over_budget": cap is not None and total > credits(cap),
        "uncertain_keys": [j["key"] for j in data["jobs"]
                           if j["status"] in {"submitting", "unknown"}],
        "note": "Committed includes held estimates where actual charges are unknown.",
    }


def validate(data, production=False, delivery=False, concepts=False):
    errors = []
    brief = data.get("brief", {})
    if brief.get("route") not in {"product", "discover", "improve"}:
        errors.append("Invalid route")
    if brief.get("deliverable") not in {"research", "concepts", "static", "video"}:
        errors.append("Invalid deliverable")
    if brief.get("mode", "live") not in {"live", "demo"}:
        errors.append("Invalid brief mode")
    if not isinstance(brief.get("revision"), int) or brief["revision"] < 1:
        errors.append("Invalid brief revision")
    registries = {}
    for field in ("sources", "claims", "concepts", "scenes"):
        rows = data.get(field)
        if not isinstance(rows, list) or any(not isinstance(r, dict) or not r.get("id") for r in rows):
            errors.append(f"{field} must contain objects with nonempty IDs")
            registries[field] = set()
            continue
        ids = [r["id"] for r in rows]
        if any(not isinstance(i, str) for i in ids):
            errors.append(f"{field} IDs must be strings")
            registries[field] = set()
        else:
            registries[field] = set(ids)
            if len(ids) != len(set(ids)):
                errors.append(f"Duplicate IDs in {field}")
    if errors:
        return errors
    for claim in data["claims"]:
        refs = claim.get("source_ids", [])
        if not isinstance(refs, list) or any(r not in registries["sources"] for r in refs):
            errors.append(f"Claim {claim['id']} has invalid source references")
        if claim.get("status") == "observed" and not refs:
            errors.append(f"Observed claim {claim['id']} needs a source")
    for scene in data["scenes"]:
        if scene.get("concept_id") not in registries["concepts"]:
            errors.append(f"Scene {scene['id']} has an invalid concept")
        refs = scene.get("claim_ids", [])
        if not isinstance(refs, list) or any(r not in registries["claims"] for r in refs):
            errors.append(f"Scene {scene['id']} has invalid claim references")
        if brief.get("deliverable") != "static" or "start_s" in scene or "end_s" in scene:
            try:
                start, end = credits(scene.get("start_s")), credits(scene.get("end_s"))
                if end <= start:
                    raise ValueError()
            except ValueError:
                errors.append(f"Scene {scene['id']} needs valid start/end seconds")
    jobs = data.get("jobs")
    budget = data.get("budget", {})
    if not isinstance(jobs, list) or any(not isinstance(j, dict) for j in jobs):
        errors.append("jobs must be a list of objects")
        return errors
    keys, job_ids = set(), set()
    for job in jobs:
        key = job.get("key")
        if not isinstance(key, str) or not key or key in keys:
            errors.append("Missing or duplicate job key")
        keys.add(str(key))
        if job.get("status") not in STATES:
            errors.append(f"Invalid job state: {key}")
        jid = job.get("job_id")
        if jid and jid in job_ids:
            errors.append("Duplicate provider job ID")
        if jid:
            job_ids.add(jid)
        try:
            credits(job.get("reserved_credits"))
            if "charged_credits" in job:
                credits(job["charged_credits"])
                if not job.get("charge_evidence"):
                    errors.append(f"Charge needs evidence: {key}")
        except ValueError as exc:
            errors.append(str(exc))
        if job.get("status") in {"pending", "completed"} and not jid:
            errors.append(f"Provider job ID missing: {key}")
        if job.get("status") == "completed" and not job.get("result_ref"):
            errors.append(f"Completed result missing: {key}")
    try:
        if budget.get("cap_credits") is not None:
            credits(budget["cap_credits"])
    except ValueError as exc:
        errors.append(str(exc))
    if concepts or production or delivery:
        errors.extend(validate_audience_research(data))
    if production:
        if brief.get("mode", "live") == "demo":
            errors.append("Demo mode is a walkthrough and cannot authorize generation or submission")
        if brief.get("deliverable") not in MEDIA_DELIVERABLES:
            errors.append("The requested deliverable does not authorize production")
        if budget.get("authorized") is not True or not budget.get("authorization_note"):
            errors.append("Generation authorization and its source are required")
        if budget.get("cap_credits") is None:
            errors.append("A bounded authorized credit cap, including one from an accepted quote, is required")
    if production or delivery:
        errors.extend(validate_production_mode(data, production=production))
        if delivery and brief.get("mode", "live") == "demo" and brief.get("deliverable") != "concepts":
            errors.append("Demo delivery supports a concepts document only, not static or video assets")
        if not data["concepts"] or not data["scenes"]:
            errors.append("Creative validation requires concepts and scenes")
        if not current_script_review(data):
            errors.append("Current script review must pass with reviewer and artifact references")
        if brief.get("deliverable") in MEDIA_DELIVERABLES:
            rows = data.get("deliverables", [])
            needs_generation = (isinstance(rows, list)
                                and any(isinstance(row, dict) and row.get("asset_ids") for row in rows))
            if production or production_mode(data) == "fresh_generation" or needs_generation:
                errors.extend(validate_generation(data))
        elif delivery and brief.get("deliverable") != "concepts":
            errors.append("Delivery validation supports concepts, static and video outputs")
        errors.extend(validate_deliverables(data, delivery=delivery))
    return errors


def initialize(args):
    if args.authorize and (args.cap is None or not args.authorization_note):
        raise ValueError("Authorization requires --cap and --authorization-note from actual user intent")
    mode = getattr(args, "production_mode", "fresh_generation")
    edit_instruction = getattr(args, "edit_only_user_instruction", None)
    edit_source = getattr(args, "edit_only_source_ref", None)
    if mode == "edit_only" and (not nonempty(edit_instruction) or not nonempty(edit_source)):
        raise ValueError("edit_only requires --edit-only-user-instruction and --edit-only-source-ref from actual user intent")
    brief = {"revision": 1, "route": args.route, "deliverable": args.deliverable,
             "mode": getattr(args, "mode", "live"),
             "market": args.market, "language": args.language, "product": None, "goal": None}
    if args.deliverable in MEDIA_DELIVERABLES:
        brief["production_mode"] = mode
        if mode == "edit_only":
            brief["edit_only_authorization"] = {"user_instruction": edit_instruction, "source_ref": edit_source}
    return {
        "schema_version": 1, "created_at": now(),
        "brief": brief,
        "budget": {"unit": "credits", "cap_credits": None if args.cap is None else str(credits(args.cap)),
                   "authorized": args.authorize, "authorization_note": args.authorization_note},
        "capabilities": {}, "sources": [], "claims": [], "concepts": [], "scenes": [],
        "audience_research": {"brief_revision": 1, "mode": getattr(args, "mode", "live"),
                              "status": "unverified", "evidence_basis": None,
                              "artifact_refs": [], "findings": [],
                              **{field: None for field in AUDIENCE_DECISIONS},
                              "limitations": None, "missing_fields": []},
        "script_review": {"verdict": "unverified"}, "reviews": [], "jobs": [],
        "generation_plan": {"brief_revision": 1, "assets": []}, "deliverables": [],
        "final_review": {"verdict": "unverified", "anti_slop_verdict": "unverified"},
        "repair_passes": {}, "experiments": [],
    }


def reserve(data, args):
    errors = validate(data, production=True)
    if errors:
        raise ValueError("; ".join(errors))
    if not all(value.strip() for value in (args.key, args.quote, args.request_ref)):
        raise ValueError("Key, quote and request references must be nonempty")
    if any(j["key"] == args.key for j in data["jobs"]):
        raise ValueError("Key already exists: reconcile or resume it; do not submit a duplicate")
    assets = {asset["id"]: asset for asset in data["generation_plan"]["assets"]}
    asset_id = getattr(args, "asset_id", None)
    if asset_id not in assets:
        raise ValueError("Reservation requires --asset-id naming a generation-plan asset")
    asset = assets[asset_id]
    if any(j.get("asset_id") == asset_id and j["status"] in {"reserved", "submitting", "pending", "unknown"}
           for j in data["jobs"]):
        raise ValueError("Asset has an unresolved job: reconcile or resume it before another reservation")
    if any(not completed_asset(data, assets[dep]) for dep in asset["depends_on"]):
        raise ValueError("Complete and record upstream dependency assets before reserving this asset")
    stage = ROLE_MODELS[asset["role"]][0]
    if stage is not None and any(ROLE_MODELS[upstream["role"]][0] is not None
           and ROLE_MODELS[upstream["role"]][0] < stage and not completed_asset(data, upstream)
           for upstream in assets.values()):
        raise ValueError("Complete all included earlier generation stages before reserving this asset")
    amount = credits(args.credits)
    if committed(data) + amount > credits(data["budget"]["cap_credits"]):
        raise ValueError("Reservation exceeds the authorized cap")
    data["jobs"].append({"key": args.key, "status": "reserved", "reserved_credits": str(amount),
                         "quote_ref": args.quote, "request_ref": args.request_ref,
                         "asset_id": asset_id, "provider": "higgsfield", "model_id": asset["model_id"],
                         "plan_revision": data["generation_plan"]["brief_revision"],
                         "history": [{"status": "reserved", "at": now()}]})


def record(data, args):
    matches = [j for j in data["jobs"] if j["key"] == args.key]
    if len(matches) != 1:
        raise ValueError("Expected exactly one reserved job key")
    job = matches[0]
    if args.status not in STATES.get(job["status"], set()):
        raise ValueError(f"Invalid transition: {job['status']} -> {args.status}")
    if job["status"] == "reserved" and args.status == "submitting":
        errors = validate(data, production=True)
        if errors:
            raise ValueError("; ".join(errors))
    if args.job_id:
        if job.get("job_id") and job["job_id"] != args.job_id:
            raise ValueError("Cannot replace an existing provider job ID")
        if any(j.get("job_id") == args.job_id for j in data["jobs"] if j is not job):
            raise ValueError("Provider job ID already belongs to another key")
        job["job_id"] = args.job_id
    if args.result:
        job["result_ref"] = args.result
    if args.status in {"pending", "completed"} and not job.get("job_id"):
        raise ValueError("This state requires the actual provider job ID")
    if args.status == "completed" and not job.get("result_ref"):
        raise ValueError("Completion requires an actual result reference")
    if args.status == "no_submission":
        if job.get("job_id") or not args.evidence:
            raise ValueError("No-submission requires supporting evidence and no provider job ID")
        job["charged_credits"], job["charge_evidence"] = "0", args.evidence
    if args.charged is not None:
        if not args.charge_evidence:
            raise ValueError("Actual charge requires provider evidence")
        if args.status == "no_submission" and credits(args.charged) != 0:
            raise ValueError("No-submission cannot have a positive charge")
        job["charged_credits"] = str(credits(args.charged))
        job["charge_evidence"] = args.charge_evidence
    job["status"] = args.status
    job["history"].append({"status": args.status, "at": now(), "evidence": args.evidence,
                           "charged_credits": args.charged, "charge_evidence": args.charge_evidence})
    plan = data.get("generation_plan", {})
    if args.status == "completed" and job.get("plan_revision") == plan.get("brief_revision"):
        for asset in plan.get("assets", []):
            if asset.get("id") == job.get("asset_id") and asset.get("model_id") == job.get("model_id"):
                asset["result_ref"] = job["result_ref"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("path")
    init.add_argument("--route", choices=["product", "discover", "improve"], required=True)
    init.add_argument("--deliverable", choices=["research", "concepts", "static", "video"], required=True)
    init.add_argument("--mode", choices=["live", "demo"], default="live")
    init.add_argument("--production-mode", choices=sorted(PRODUCTION_MODES), default="fresh_generation")
    init.add_argument("--edit-only-user-instruction")
    init.add_argument("--edit-only-source-ref")
    init.add_argument("--market")
    init.add_argument("--language")
    init.add_argument("--cap")
    init.add_argument("--authorize", action="store_true")
    init.add_argument("--authorization-note")
    check = sub.add_parser("check")
    check.add_argument("path")
    check.add_argument("--for-concepts", action="store_true")
    check.add_argument("--for-production", action="store_true")
    check.add_argument("--for-delivery", action="store_true")
    summ = sub.add_parser("summary")
    summ.add_argument("path")
    res = sub.add_parser("reserve")
    res.add_argument("path")
    for arg in ("key", "credits", "quote", "request-ref"):
        res.add_argument("--" + arg, required=True)
    res.add_argument("--asset-id", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("path")
    rec.add_argument("--key", required=True)
    rec.add_argument("--status", choices=list(STATES), required=True)
    for arg in ("job-id", "result", "charged", "charge-evidence", "evidence"):
        rec.add_argument("--" + arg)
    args = parser.parse_args()
    try:
        path = project_path(args.path)
        with locked(path):
            if args.command == "init":
                if path.exists():
                    raise ValueError("Project exists; resume it instead of overwriting")
                data = initialize(args)
                save(path, data)
            else:
                data = load(path)
                errors = validate(data, production=getattr(args, "for_production", False),
                                  delivery=getattr(args, "for_delivery", False),
                                  concepts=getattr(args, "for_concepts", False))
                if errors:
                    raise ValueError("; ".join(errors))
                if args.command == "reserve":
                    reserve(data, args)
                    save(path, data)
                elif args.command == "record":
                    record(data, args)
                    save(path, data)
            output = summary(data)
            if args.command == "check":
                output["structurally_valid"] = True
                if args.for_concepts or args.for_production or args.for_delivery:
                    output["audience_gate"] = {"mode": data["brief"].get("mode", "live"),
                                               "status": data["audience_research"]["status"],
                                               "evidence_basis": data["audience_research"]["evidence_basis"]}
                output["note"] = "Structure only; factual support and media quality require actual review."
            print(json.dumps(output, ensure_ascii=False))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
