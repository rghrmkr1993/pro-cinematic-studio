# Shared project state and recovery

Read for multi-step projects and all production. Keep one canonical project outside the skill directory. Resolve this skill's installed path dynamically; reconciliation or sharing may rename its folder.

The producer is the only writer of the canonical brief. Workers return separate artifacts. The operator alone changes submission records, sequentially through the helper. Do not run manual edits concurrently with helper operations.

## Contract

Initialize project.json with scripts/workflow_state.py. Extend its objects with the actual task data:

- brief: revision, mode (`live` or `demo`, default `live`), production_mode (`fresh_generation`, default for media, or explicitly authorized `edit_only`), edit_only_authorization when applicable, route, deliverable (`research`, `concepts`, `static` or `video`), product/offer, market, audience language, goal, constraints, assets and missing inputs. Demo means a workflow walkthrough with no real generation, even if a quote or budget is available; an explicitly requested real production for a fictional product is live work with the fictional status disclosed.
- audience_research: current brief_revision and mode, status, evidence_basis, actual artifact_refs, findings with their evidence, chosen_segment, trigger, desired_outcome, objection and creative_implication. Limited research also records limitations and missing_fields. Apply the audience gate below before production preparation.
- capabilities: actual availability of web, browser, agents, provider, editing and media inspection; check date and limits.
- sources: id, title, URL/file reference, retrieval date, evidence type, owner, market and inspected coverage.
- claims: id, proposition, status, source_ids, scope, contradictions and allowed wording. Status separates observed, user-provided, inferred, proposed and unsupported.
- concepts: id, persuasive idea, audience situation, evidence references, offer, CTA, funnel and hypothesis.
- scenes: id, concept_id, start_s, end_s, claim_ids, actions, narration, text, references, production method and review criteria. Static scenes may omit both timing fields; if either is supplied, both must be valid.
- script_review: verdict, brief_revision, reviewer and artifact_refs to the actual review. Keep detailed verdicts under reviews.
- budget: authorized, authorization_note, cap_credits and unit. Copy actual user authorization; never invent it.
- jobs: stable logical key, reserved cost, current quote/request references, actual provider ID, status, result reference, confirmed charges and history.
- generation_plan: current brief_revision and ordered assets using the exact production schema below.
- deliverables: each final creative's concept, type, generated asset IDs and/or supplied source references, CTA and eventual result reference.
- final_review: current revision, independent reviewer, actual review/output references and separate overall/anti-slop verdicts. This is a delivery gate, not a prerequisite for generating the media it must inspect.
- repair_passes: cumulative count by affected asset, linked concept, issue and scenes. Producer enforces the default two-pass cap per affected asset; the helper does not judge creative quality or repair necessity.
- experiments: actual measurement windows, inputs, denominators, outcomes and next hypothesis.

For Meta work, extend the existing objects with task-specific fields (no new ledger is required):

- brief: platform, placements, optimization/business event and measurement assumptions.
- sources/claims: platform evidence class (engineering fact, advertiser guidance or team hypothesis), source publication/check date and coverage.
- concepts: concept_family_id, variant_id when applicable, motivation, proof approach, meaningful difference, placement, test priority/reason and failure hypothesis.
- scenes: opening/proof/payoff role, what new information the beat adds, identity/context cues and visible acceptance criteria.
- reviews: separate factual, creative and technical verdicts; exact visual/motion/audio coverage; unresolved issues and corrections after user feedback.
- experiments: exploration versus controlled refinement, held constants, changed variables, concept/variant IDs, outcome definitions, denominators, exposure imbalance and uncertainty.

Use meta-andromeda.md for the actual requirements. These fields record reasoning and review; the existing helper does not automatically validate their truth or creative quality.

Increment brief.revision whenever the offer, audience, market, script, planned input assets, mode or material instructions change. This invalidates old gate metadata and the generation plan. Recording a generated result, correcting a typo in a note or updating administrative metadata does not by itself change the brief revision. A material revision requires a current plan/review; preserve previous plans and jobs. Research can be reused when its audience decisions and evidence still apply: explicitly review that fit, preserve the old record, add a reuse_review with from_brief_revision, reviewer, reason and artifact_refs to the reuse assessment, then mark audience_research.brief_revision current. Do not rerun unchanged research merely because a downstream script or asset changed. A demo-to-live switch requires an actual live evidence assessment and a record with mode live; illustrative demo assumptions cannot be relabeled as live evidence. Preserve prior reviews and observations instead of silently overwriting their meaning. Do not place credentials or signed upload secrets in project artifacts.

## Audience research gate

The internal names `concepts`, `concept_id`, the text-only `concepts` deliverable type and `--for-concepts` remain for compatibility with existing ledgers. They represent creative metadata or a requested brief/demo, not a separate concept stage or approval. Populate the required metadata within production preparation; do not create a concept presentation to satisfy the schema.

Run `check --for-concepts` after audience research and before preparing production scripts or prompts. This readiness check does not require creative metadata to exist yet. It checks the following record, and every production/reservation/delivery gate checks it again:

- `brief_revision` equals `brief.revision`; `mode` equals `brief.mode` (an omitted brief mode in an old project means live).
- `status` is `complete` for adequate actual evidence, or `limited` for a candidly scoped result. `limited` requires nonempty `limitations` text and a nonempty `missing_fields` list. Insufficient coverage must remain visible; it cannot be hidden behind a complete label.
- `artifact_refs` is a nonempty list of references to the actual research/synthesis artifacts. The artifact records scope, reviewed material and limitations.
- `chosen_segment`, `trigger`, `desired_outcome`, `objection` and `creative_implication` are nonempty strings. They capture a concrete audience situation and its consequence for the creative, not a demographic label alone.
- `findings` is a nonempty list of objects with nonempty `finding` text. For `evidence_basis: "inspected_sources"` or `"supplied_research"`, every finding has nonempty `source_refs` containing actual URLs, supplied file references or source IDs traceable to the source registry. Supplied research may be reused after inspecting its coverage and fit. Never create a source URL or testimonial to satisfy the gate.
- Live mode requires `evidence_basis: "inspected_sources"` or `"supplied_research"`. Demo mode may use either actual evidence basis with the same source requirements, or `"illustrative"`. With illustrative evidence, every finding needs nonempty `demo_basis` that explicitly describes its invented/assumed basis, status must be limited, and limitations/missing_fields must state the absent live verification. Illustrative assumptions are not reviews, observed customer facts or verified research.

Initialization creates an unverified, empty audience record. Populate it with the real work; a prefilled example is not evidence. The helper validates the contract but cannot authenticate sources, measure research quality or prove that a typed limitation is candid. The producer and reviewer must inspect the cited material.

Demo mode never passes `--for-production`, `reserve` or a new `reserved` → `submitting` transition. `--for-delivery` in demo mode supports only a reviewed text walkthrough/brief (stored as `concepts`); it cannot validate a static/video deliverable. A passed demo audience check reports mode demo and does not establish live readiness. Changing mode makes the previous research record ineligible until assessed for the new mode.

Ordinary `check`, `summary` and reconciliation of already-submitted jobs do not demand new research. In particular, recording truthful outcomes for `submitting`, `pending` or `unknown` jobs remains possible when research is absent or stale. Before an old reservation can move from `reserved` to `submitting`, the full current production gate is required. Never replay research or resubmit a job as a workaround for recovery.

## Production schema

The file remains `schema_version: 1`. Ordinary `check`, `summary` and recovery of existing jobs remain compatible with old projects. Before new reservations, complete the audience gate and add the fields below; old metadata alone cannot pass the strengthened production gate. The helper uses family names as policy labels; **never copy the example model IDs into a real request**. Read actual IDs and supported families from current Higgsfield discovery and preserve that response as evidence.

```json
{
  "capabilities": {
    "higgsfield": {
      "available": true,
      "checked_at": "ACTUAL_ISO_DATETIME",
      "evidence_refs": ["/project/work/higgsfield-discovery.json"],
      "models": [
        {"model_id": "ACTUAL_NANO_BANANA_PRO_ID", "family": "nano_banana_pro", "verified": true, "evidence_refs": ["/project/work/nano-capability.json"]},
        {"model_id": "ACTUAL_SEEDREAM_5_ID", "family": "seedream_5", "verified": true, "evidence_refs": ["/project/work/seedream-capability.json"]},
        {"model_id": "ACTUAL_SEEDANCE_2_5_ID", "family": "seedance_2_5", "verified": true, "evidence_refs": ["/project/work/seedance-capability.json"]}
      ]
    }
  },
  "generation_plan": {
    "brief_revision": 1,
    "assets": [
      {"id": "LOCATION-1", "role": "location", "provider": "higgsfield", "model_id": "ACTUAL_NANO_BANANA_PRO_ID", "depends_on": [], "input_refs": []},
      {"id": "CHARACTER-1", "role": "character", "provider": "higgsfield", "model_id": "ACTUAL_SEEDREAM_5_ID", "depends_on": [], "input_refs": []},
      {"id": "PRODUCT-1", "role": "product", "provider": "higgsfield", "model_id": "ACTUAL_NANO_BANANA_PRO_ID", "depends_on": [], "input_refs": ["/project/work/user-product.png"]},
      {"id": "FRAME-1", "role": "composed_frame", "provider": "higgsfield", "model_id": "ACTUAL_NANO_BANANA_PRO_ID", "depends_on": ["LOCATION-1", "CHARACTER-1", "PRODUCT-1"], "input_refs": []},
      {"id": "VIDEO-1", "role": "video", "provider": "higgsfield", "model_id": "ACTUAL_SEEDANCE_2_5_ID", "depends_on": ["FRAME-1"], "input_refs": []}
    ]
  },
  "deliverables": [
    {"id": "AD-1", "type": "video", "concept_id": "CONCEPT-1", "asset_ids": ["VIDEO-1"], "cta": {"text": "Shop the bag", "destination": "https://example.com/exact-product"}}
  ]
}
```

Only include stages and discovered models the actual creative needs. A static creative can contain a single `static` asset from Nano Banana Pro, or a `character` asset from Seedream 5 for a character-led still. A supplied location, person, prop or product reference goes in `input_refs`; it need not be regenerated. A video from an already supplied composed frame can use that file in `input_refs` and omit unnecessary preparatory generation. Preserve approved identity when composing a frame in Nano Banana Pro. Do not use a different provider or silently substitute another family when a required model is unavailable.

Prefer verified native Seedance 2.5 audio when it serves the scene. If separate audio generation is necessary, use `role: "audio"`, `provider: "higgsfield"` and an actual discovered model ID. This role has no locked family; its model record must have a nonempty verified `family`, evidence references and `output_types: ["audio"]` supporting the requested operation. Audio can appear wherever its explicit dependencies allow; it has no fixed image/video stage. Record separate audio jobs and charges through the same helper. A model name alone does not establish voice or music capability.

Required fields and checks:

- `capabilities.higgsfield`: `available: true`, nonempty `checked_at`, nonempty `evidence_refs`, and `models` array. Every used model has a unique actual `model_id`, nonempty verified `family`, `verified: true` and nonempty `evidence_refs`. Visual roles require the exact family labels in the example; separate audio additionally requires `output_types` containing `"audio"`. Only claim verified after inspecting the supporting response; the helper cannot authenticate it.
- `generation_plan.brief_revision` equals `brief.revision`. `assets` is nonempty, ordered and has unique string IDs. Each asset has `id`, `role`, `provider: "higgsfield"`, discovered `model_id`, `depends_on` (unique earlier asset IDs) and `input_refs` (supplied reference strings, possibly empty). The operator must pass the actual upstream results and supplied references into provider requests, not just record names in this plan.
- Role/model/order mapping: `location` → Nano Banana Pro; `character` → Seedream 5; `prop` and `product` → Nano Banana Pro; `composed_frame` and `static` → Nano Banana Pro; `video` → Seedance 2.5. Order these five visual stages as listed. Skip unnecessary stages. Jobs in a stage may be independent, but all included earlier visual stages and every explicit dependency must have recorded completed jobs before reserving a downstream visual asset. Separate `audio` follows its dependencies and verified audio capability.
- `deliverables`: nonempty array with unique `id`, `type` matching `brief.deliverable`, valid `concept_id`, and `cta: {"text": "...", "destination": "..."}`. In `fresh_generation`, every media output needs nonempty `asset_ids` referencing actual Higgsfield generations for this assignment: a `video` asset for video, or a `static`/`composed_frame`/`character`/`product` asset for static. `source_refs` may supplement these results but cannot replace the requested new main visual. In explicit `edit_only`, actual supplied/previously approved media may be recorded in nonempty `source_refs` without generation assets. A generated product sheet can therefore become a finished static ad through deterministic composition and CTA; no redundant static generation is required. For an explicit edit-only task, supplied video may be assembled with an existing end card without a synthetic video job; fresh video creation still requires a real Higgsfield video result. State a proposed destination honestly when no live page exists; do not invent a working URL.
- Every new job stores `asset_id`, `provider`, `model_id` and `plan_revision` automatically from the reservation. Completion stores its `result_ref` on the matching current-plan asset. Old jobs remain readable; a newly required result cannot be satisfied by an unrelated historic job or a manually typed reference alone.

For a brief revision, previous assets may be reused as supplied `input_refs` with their actual retained files/results. Archive their provenance and review; do not relabel old jobs as newly generated jobs. Planned but abandoned assets may be removed in a revised plan; retain their spending/history.

## Delivery schema and gate

Set `deliverables[].result_ref` to the actual final image, video or concept document after assembly. A final export may differ from an individual generation result; the deliverable links both. Deterministic local assembly, captions and export need no fabricated generation job: generation jobs cover the generated source assets, and the final export has its own actual reference. Then record the independent review of those exact outputs:

```json
{
  "final_review": {
    "verdict": "pass",
    "anti_slop_verdict": "pass",
    "brief_revision": 1,
    "reviewer": "ACTUAL_INDEPENDENT_REVIEWER",
    "review_ref": "/project/work/final-review.md",
    "deliverable_ids": ["AD-1"],
    "artifact_refs": ["/project/outputs/ad-1.mp4"]
  }
}
```

Both verdicts may be `pass`, `revise` or `unverified`; only `pass` passes delivery. `artifact_refs` must include every current final `result_ref`, and `deliverable_ids` must cover every delivered ID. The actual review records creative specificity, coherence, progression, product continuity, CTA and the inspected modalities/coverage under the quality and creative references. Metadata cannot replace viewing the assets. Review a changed final export again, even if its filename is reused.

Only an explicit user request to edit existing media without new generation permits source-only delivery. Set `brief.production_mode: "edit_only"` and retain `brief.edit_only_authorization: {"user_instruction": "ACTUAL_USER_INSTRUCTION", "source_ref": "ACTUAL_MESSAGE_OR_BRIEF_REFERENCE"}`. A generic “make ads from this photo” request remains `fresh_generation`. Lack of access, credits or product URL is not an edit-only authorization. The helper can require this record but cannot verify the instruction; the operator and reviewer must do so.

For example, when the user explicitly requests only a CTA overlay on their existing photo, record the source directly on the deliverable, with no generation plan or fictitious provider job:

```json
{
  "id": "AD-PHOTO-1",
  "type": "static",
  "concept_id": "CONCEPT-1",
  "asset_ids": [],
  "source_refs": ["/project/work/supplied-product-photo.png"],
  "cta": {"text": "Explore the bag", "destination": "Proposed exact-product page"},
  "result_ref": "/project/outputs/product-photo-with-cta.png"
}
```

Use `input_refs` on a generation-plan asset when supplied material is an input to a new generation request; use `source_refs` on the deliverable when existing media is used directly in assembly. Preserve provenance and prior approval for reused media. Never hide a newly generated asset in `source_refs` to evade its model, cost or job tracking.

`check --for-delivery` always requires current audience research, a current script review, final/anti-slop review, CTA and actual reviewed output references. If any deliverable has nonempty `asset_ids`, it additionally validates the generation plan and completed provider jobs/result references for those assets and their dependencies. In `fresh_generation`, every media row must retain the required generation checks, even when supplied media is also present. Only explicit `edit_only` allows supplied-only rows and delivery without generation capabilities or a generation plan. `edit_only` cannot authorize or reserve new generations; if new generation is requested, update the brief and production plan under the normal provider gates. The helper cannot authenticate supplied files or prior approval; the actual reviewer must inspect them. It does not require unused planned assets to be complete. For `concepts`, use `type: "concepts"` and the reviewed document as `result_ref`; generation capabilities and assets are not required. This flag is for creative delivery, not research reports, which retain their evidence-review workflow.

`check --for-production` and `reserve` require live mode, current audience research, an authorized static/video generation request, budget, discovered capabilities and a nonempty current generation plan. Supplied-only delivery cannot bypass those checks or authorize a new generation call.

Do not use `--for-delivery` before generation or assembly: final media review can only occur after media exists. A successful production check does not claim that the final deliverable passed anti-slop review.

## Helper use

Requires Python 3 and fcntl (Linux/macOS). On other hosts maintain the same contract with one sequential writer; disclose that automatic ledger checks are unavailable. The helper is local, makes no network calls and never submits jobs.

Examples below use a project path outside the installed skill. Replace the skill path with the actual package root and the project path with the host's chosen working path.

```sh
python3 /path/to/skill/scripts/workflow_state.py init /path/to/project/project.json --route product --deliverable concepts --market USA --language en-US
python3 /path/to/skill/scripts/workflow_state.py check /path/to/project/project.json
```

Use optional `--mode demo` on init only for a requested walkthrough; omitted mode defaults to live. After recording the audience research and before new creative development, run:

```sh
python3 /path/to/skill/scripts/workflow_state.py check /path/to/project/project.json --for-concepts
```

For authorized production, initialize with `--deliverable static` or `--deliverable video`, `--cap ACTUAL_AUTHORIZED_CREDITS`, `--authorize` and `--authorization-note` pointing to the actual user request. The cap may be the bounded total of a specific quote the user already accepted; it need not be a separately requested round-number budget. Record the quote, included jobs/repairs and authorization source. Existing sufficient authorization does not require another confirmation. For a resumed project update the existing budget and deliverable only when user authorization supports it; never reinitialize to erase prior spending.

Fill audience_research, sources, claims, concepts, scenes, the actual script_review, discovered capabilities, generation_plan and deliverables before production. Every scene needs a valid concept and claim references; video scenes additionally need start/end times. Then:

```sh
python3 /path/to/skill/scripts/workflow_state.py check /path/to/project/project.json --for-production
python3 /path/to/skill/scripts/workflow_state.py reserve /path/to/project/project.json --key concept1.location1.rev2.pass0 --asset-id LOCATION-1 --credits ACTUAL_QUOTE --quote /path/to/current-quote.json --request-ref /path/to/request.json
python3 /path/to/skill/scripts/workflow_state.py record /path/to/project/project.json --key concept1.location1.rev2.pass0 --status submitting
```

Submit the actual provider call only after reservation succeeds. Immediately record pending with --job-id ACTUAL_RETURNED_ID. Completion requires --status completed and --result ACTUAL_RESULT_REFERENCE. Record --charged and --charge-evidence only when the provider confirms the amount; a quote is not a receipt.

On uncertain transport failure record unknown with available evidence. On known no-job response use no_submission with --evidence. Do not label a lookup failure no_submission. Failed/canceled jobs retain their reservation until actual cost or refund evidence exists. The helper permits truthful actual costs above a cap so the overrun remains visible, but rejects additional reservations exceeding it.

Use summary to resume. Duplicate logical keys and conflicting provider IDs are rejected. An asset with a reserved, submitting, pending or unknown job cannot receive a new reservation. An unknown or submitting record must be reconciled; a new key is not a workaround. For an explicitly confirmed no-submission outcome, preserve the record and use a new attempt key only for the corrected request. Preserve usable results and reserve only the smallest required repair within the existing authorization.

After assembly and actual final review:

```sh
python3 /path/to/skill/scripts/workflow_state.py check /path/to/project/project.json --for-delivery
```

## What validation does and does not establish

The helper checks references, minimal scene structure, current script-review metadata, authorization/cap presence, held costs, job transitions and duplicate IDs. Concept readiness, production and delivery additionally require current audience-research metadata, decisions and evidence references, with explicit live/demo distinctions. Production checks require recorded Higgsfield discovery, the role/model plan, dependency order and a CTA per deliverable, and reject demo mode. Delivery checks require actual recorded Higgsfield image/video results for each fresh creative, or supplied source references for explicitly authorized edit-only work, plus current final/anti-slop review metadata; demo delivery permits only concepts documents. Atomic writes and a lock protect its own updates. It does not open references, authenticate capability or audience evidence, verify actual user consent/pricing, inspect media, prove artistic quality or enforce every timeline constraint. A producer cannot replace independent review with a successful command.

The ledger cannot enforce permissions on direct MCP calls or provide provider-side idempotency. The sole-operator rule, truthful job reconciliation and host permissions remain necessary. Preserve project state across context changes and save final user artifacts according to the host's storage rules.
