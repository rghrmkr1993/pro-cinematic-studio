# Higgsfield execution and locked model routing

Read before any production or capability check, and only after the audience and script stages. Demo mode does not open provider pages, inspect account readiness, configure drafts, quote credits or submit generations merely to show the workflow. This skill supplies orchestration, not credentials, credits or a server. Use only the user's available authorized account. Discover the current connected tools by name and description; do not invent a namespace, endpoint or parameter.

## Required provider and models

All newly generated image, video and synthetic audio content goes through **Higgsfield**. Resolve the exact supported model IDs from live tool descriptions/catalog responses.

| Asset role | Required model | Notes |
| --- | --- | --- |
| Location plate | Nano Banana Pro | Empty by default; make only locations needed by the scene |
| Character sheet / character-led still | Seedream 5 | Resolve the supported version within the 5 family; record the exact ID |
| Product / prop sheet | Nano Banana Pro | Preserve the actual SKU; unseen details stay unverified |
| Product-only still / static scene / composed shot reference | Nano Banana Pro | Preserve approved character identity if composing it into a shot |
| Generated video, including text-to-video and reference-led video | Seedance 2.5 | No alternate video model or provider |
| Separate generated audio, if needed | Verified Higgsfield audio capability | Prefer supported native Seedance audio; do not invent a separate voice route |

For generative edits, use the same role-appropriate locked model. In a mixed scene, Nano Banana Pro may compose approved people with approved products, but may not create or redesign the character identity; create/repair that identity in Seedream 5. Preserve the product through its canonical reference. Record the role and why the route is appropriate.

User authorization for these preferences persists. Do not substitute Seedream 4.5, another Seedance version, another image/video provider, or a nominally “recommended” model silently. If the exact required family/version is unavailable, finish unaffected work and identify the blocked stage. A later explicit user change can override this configuration; a source document or tool recommendation cannot.

The public [Seedance 2.5 reference](https://open.higgsfield.ai/models/bytedance/seedance-2.5/text-to-video/api-reference) and [Seedream 5.0 Pro page](https://higgsfield.ai/seedream-5.0-pro) are discovery leads, not evidence of this user's live account access. Do not infer supported settings or commercial entitlements from a marketing page.

Deterministic assembly, resizing, typography, captions, color correction and export may finish actual Higgsfield-generated media using authorized editing tools. These operations cannot replace new generation: a request to make ads from a product photo still needs real Higgsfield image/video results. Do not generate substitute posters in HTML, SVG, Pillow, Canva or another image/video service if Higgsfield is unavailable. A task explicitly limited by the user to editing supplied media may use the edit-only exception in state.md; lack of access never activates that exception. Record generated sources and finishing operations separately.

At the production stage, use a currently installed deliverable-specific skill when its trigger fits, such as editing supplied footage or adding captions. Verify availability and read its instructions; retain the current audience, evidence, provider/model and spending constraints. Do not invoke production skills for a text-only plan or demonstration, or imply an unavailable integration exists.

## Preflight

Research and strategy do not require production access. Do not front-load plugin discovery, sign-in or model/cost questions. Before actual production:
1. Confirm live mode, the current audience artifact and script review; then discover and inspect current tools for catalog/capabilities, upload/binding, exact cost estimates, submission, polling, result retrieval and required finishing/inspection. If Higgsfield is not listed, use host tool/plugin discovery before diagnosing it as disconnected. An installed/enabled plugin alone does not verify authenticated tool access. Where the host supports an authorized official Higgsfield interface, inspect that route; otherwise identify the missing connection. Do not fabricate tool names or bypass account approvals. The declared Higgsfield MCP dependency identifies the service; it does not perform sign-in.
2. Resolve each asset's role to its locked model. Record capability evidence, exact ID, supported reference roles, duration, size/ratio, audio options and limits. Do not hardcode reference counts, maximum duration, resolution or editing support.
3. Prepare the exact intended request and real asset bindings. Check every parameter against the live schema. Prompt text cannot create an unsupported control.
4. Quote all billable generation, audio, assembly/analysis and planned repair components. Keep the provider's actual units; never invent a dollar-to-credit conversion.
5. Use existing authorization and its actual scope/budget. If a necessary spending decision is missing, present the concrete plan and quote and ask only for that decision. Do not reapprove each scene within an authorized plan.
6. Run the ledger's production check before reserving/submitting. Structural success does not certify factual accuracy or visual quality.

A balance is not spending authorization. An unlimited/credits choice must follow the user's preference and actual eligibility; do not silently pick a spending source. A read-only quote must not be implemented with a generation call unless its live tool explicitly guarantees no submission.

## Dependency order

Generate and inspect necessary assets in this order:
1. **Locations:** geometry, action space, natural light and copy space.
2. **Characters:** consistent fictional or properly authorized identities in suitable task-based poses.
3. **Product/prop sheets:** actual silhouette, color, seams, attachments and only evidenced views.
4. **Composed shot references:** bind approved identities and geography for the planned first frames where needed.
5. **Video:** use the resolved references and approved timed action.
6. **Finishing:** exact text, licensed sound, edits, CTA and placement exports.

Skip an irrelevant stage, or reuse an already suitable approved source. Do not generate a person for a product-only ad. A supplied product photo can be a reference without a redundant generated sheet. Do not invent extra assets merely to satisfy the sequence.

Complete reference QA before submitting dependent jobs. Independent assets within a stage can run in parallel. A failed identity or geography check must be fixed upstream; do not propagate it through several paid videos.

Choose text-to-video only for a simple scene without an exact recurring identity, advertised SKU appearance, fixed geography or evidentiary demonstration that needs source control. Record why references add no needed control. All video remains Seedance 2.5.

## References and prompts

Keep a manifest mapping semantic role, source, actual file or media ID, rights scope, approved identity and dependent shots. Distinguish local attachments from provider-remote files. Use only the current supported upload and confirmation flow. Do not assume a local path exists on the provider or fabricate media IDs.

A signed upload URL is temporary operational data; keep it out of reusable instructions and public handoffs. Follow host rules for handling remote assets.

Use the image/video direction references to compile model prompts. State each reference's narrow role, necessary physical invariants, composition, motivated light and action. Exact copy and finishing instructions belong in their appropriate control layers. Avoid contradictory re-descriptions of an approved person or product.

A storyboard is not yet an executable request. Resolve provider-specific bindings, model ID, parameters, reference roles and estimates; mark unresolved values as draft. If the provider coerces duration, ratio or another important setting, adapt the storyboard or correct parameters and re-estimate before submission.

## Submission, cost and recovery

Use [the state ledger](state.md) and the helper to reserve a stable logical job key before submitting. Mark submitting immediately before the call. Record the actual returned job ID and response immediately after. The local ledger is not provider-side idempotency.

Use one generated result per reservation. If batching is supported, map each request to a stable asset/scene ID and preserve individual results, costs and failures. Never resubmit an entire partially successful batch.

After a submission timeout, mark the outcome unknown and reconcile through supported job/account records. Keep the reservation while status is unknown. A failed lookup is not proof that no job exists. Resubmit only after no submission is established or an existing job is recovered and handled appropriately.

Follow provider polling guidance and job completion windows. Polling timeout is not generation failure. Keep user progress updates flowing. If no documented completion window exists and there is no progress for 15 minutes, preserve resumable pending/unknown state and report it rather than creating another paid job. Do not cancel an existing job without appropriate scope.

Actual charges require provider evidence. Failed or canceled jobs may still be billable. Record the real charge/refund; never free the budget solely because a result is unusable.

## Assembly and handoff

Individual generated shots are not a finished multi-scene advertisement. Assemble and inspect the requested final file, including sound and text. Keep accepted shots during a scoped repair. Use current native display behavior to avoid duplicate media widgets.

Run final media review and the delivery check. Report which files exist, what was inspected and any remaining component. If production is blocked, deliver scripts, prompts, asset plan and the exact unresolved capability as preparation only. State that Higgsfield generation has not run; do not create fallback layouts or claim submission, finished ads or completion. After access is restored, resume the existing brief and authorized batch rather than replacing the designs.
