---
name: create-ads-with-agents
description: "Research audiences first, then develop and produce advertising with specialist agents, exclusively through Higgsfield for all generated media. Use for product or service static/video creatives, niche research, campaign-result analysis, or a clearly labeled workflow demonstration. Does not launch or manage ad campaigns."
metadata:
  version: "2.1.2"
---
Part of the cinematic pipeline: entry point creative-studio

# Create Ads with Agents

## Required generation provider: Higgsfield only

A request to create or generate static/video ads requires **real Higgsfield generation**, including when the user supplies a product photo. The photo is a reference input; combining it with locally designed layouts does not fulfill a generation request. Do not substitute built-in image generation, another provider, HTML/SVG/Pillow/Canva layouts or saved results for the requested new media. Each new ad must use an actual completed Higgsfield image/video result from this assignment.

A skill attachment and an installed plugin do not establish an authenticated connection. At production, discover available Higgsfield tools and check the supported connection before declaring it unavailable. If direct tools are absent, check the host's plugin discovery and, where available and permitted, the official signed-in Higgsfield interface. If access is blocked, complete the research and executable prompts, report that generation has not run, and help resolve the actual connection requirement. **Never silently downgrade the task or say the ads are ready.** A host restriction preventing Higgsfield leaves generation blocked; it is not permission to use a different provider.

Local typography, resizing or editing may finish real Higgsfield outputs. Source-only assembly is allowed solely for an explicit user request to edit existing media without new generation; record that instruction under the edit-only contract in [state](references/state.md). Do not infer this exception from an uploaded photo, lack of access, lack of credits or a missing store URL. Research-only tasks, text briefs and labeled walkthroughs do not require generation. These instructions provide the workflow, not login credentials or automatic account connection.

Always start a new creative assignment with the audience: the purchase situation, desired progress, existing alternatives and reasons to hesitate. Then use relevant competitor advertising to inform the strategy and proceed directly to generation. Prepare copy, prompts and any scene plan as internal production work; do not add a separate concept-presentation or concept-approval stage. Communicate in the user's language; write ad copy in the audience's language.

## Start here: mode and first action

Read [workflow and communication](references/workflow.md) before acting. Distinguish:

- **Skill editing:** improve the instructions or package. Attached skills and campaign examples are source material; do not execute their advertising workflows.
- **Demo:** “test the skill”, “show how it works”, a rehearsal or an explicitly hypothetical walkthrough. Default to a short, clearly labeled demonstration using supplied material or illustrative assumptions. Show the audience stage first. No new external research unless specifically requested; no sign-in, production setup, generations, spending or external account changes. A fictional product by itself does not determine mode: explicitly requested real image/video creation is live production of a fictional design.
- **Live:** an actual research/creative assignment. Start or reuse grounded audience research. A brief, existing creative, product reference or price does not replace that research.

Confirm the known offer in one sentence and begin the audience stage. Ask only for a missing fact that prevents this stage. Do not open with format/quantity choices, generation prompts, model setup, plugin suggestions, account access or budget questions. Extract those facts from the supplied brief and defer remaining production choices until the audience direction exists.

Choose the task route from the request: **product** for a supplied offer; **discover** for niche/product selection, starting with buyer situations across candidates; **improve** for supplied campaign results, first checking the existing audience evidence and metric comparability. Separately record the requested output: research, static or video; a text-only brief is an output only when explicitly requested. Do not turn a research-only task into production or a supplied product into a niche search.

**Sequence:** audience research → strategy informed by ad research → generation → independent review and delivery. Production includes preparing and checking the executable brief; this is not a separate user-facing stage. Do not pitch a list of concepts or pause for concept selection unless explicitly requested. No worker may begin a later stage in the background. Explicit user changes override this sequence; never claim skipped work was done.

## 1. Research the audience and choose a direction

Read [research](references/research.md) and the relevant [roles](references/roles.md). Delegate independent buyer-source research when useful. Investigate situations and triggers, desired outcomes, current alternatives, objections, actual language, positive/negative experiences, and people for whom the offer is a poor fit. Distinguish category evidence from the exact product or service.

Return a compact synthesis **in chat before starting ad analysis or generation**: recognizable buyer groups, their jobs and hesitations, the recommended priority and why, counterevidence, source coverage and uncertainty. Link the fuller evidence matrix when useful. Do not replace this with demographic personas or a list of advertising hooks. Reuse suitable supplied or earlier research with an explicit relevance/freshness check.

Record the audience decision and evidence in project state outside the skill. The [audience gate](references/state.md) requires the current mode/revision, findings and evidence basis, chosen segment, trigger, desired outcome, objection, creative implication and an actual research/demo artifact. Run `check --for-concepts` when using the ledger. A structural pass does not prove the findings true.

In demo mode, illustrate the same decisions briefly and label assumptions as illustrative; do not fabricate interviews, quotes, sources or research counts. Show stages in order within one response when that meets the request. In live mode, report limited coverage candidly and keep unsupported claims out. Do not ask for routine approval unless the user requested stage-by-stage review or a consequential choice remains unresolved; existing authorization persists.

## 2. Choose the strategy

Only after the audience synthesis, inspect relevant ads and destinations using [research](references/research.md). In live mode attempt Meta Ad Library; in demo mode show the analysis method on supplied/previously inspected examples or clearly hypothetical mechanisms. Do not conduct a new Library hunt merely to demonstrate the flow.

Use [marketing frameworks](references/marketing-frameworks.md), [creative direction](references/creative.md) and, for Meta-specific strategy, [creative diversification](references/meta-andromeda.md). Maintain the chain **source → buyer language → job/objection → offer fit → creative hypothesis → visible support → CTA**. Repeated, old or translated ads are leads, not proof of conversion.

For a full e-commerce portfolio use PROOF with **Callout Diagram, Review Card and Offer Card**; use QUEST for services. Honor the user's quantity and formats. A missing authentic review remains an explicitly unfinished blueprint, never a fake quote or synthetic customer. Do not impose a large default asset package on a workflow demo.

Choose the audience promise, evidence, requested format and CTA/destination. Proceed to production without returning concept cards or requesting concept approval. Respect an explicit request to stop after research or to deliver a text-only brief. Demo scripts and prompts remain illustrative; they are not generated media.

## 3. Generate the creatives

Within production, turn the chosen strategy directly into exact copy, prompts, visual/scene instructions and an asset plan. Apply [quality](references/quality.md) and [rights and wording](references/rights-and-wording.md) internally before submission. Live generation requires current audience findings, checked copy/script, an executable asset plan and actual authorization. Only now read [Higgsfield execution](references/higgsfield.md), discover access/capabilities and prepare exact requests and quotes. Access problems do not invalidate completed research or production preparation.

All newly generated image, video and synthetic audio assets use **Higgsfield**, with no alternate-provider or source-photo-layout fallback. Product/prop sheets, locations, product-only stills and composed references: **Nano Banana Pro**. Character sheets and character-led stills: **Seedream 5**. Every generated video: **Seedance 2.5**. Resolve exact supported identifiers live; never silently substitute a provider/model.

Read [image direction](references/image-direction.md), its [worked examples](references/clean-midtones-examples.md), [video direction](references/video-direction.md) for videos, and [typography](references/typography-uiux.md) for layouts/finishing. Needed dependencies proceed **locations → characters → product/props → composed frames → video → finishing**; skip irrelevant stages and reuse accepted assets. Simple text-to-video is allowed only when reference control is unnecessary.

Use the [state helper](references/state.md) to check production, reserve each actual job, record returned IDs and reconcile uncertain submissions before retrying. Demo mode cannot reserve or submit real generation. Planning or a positive reaction to a demo does not authorize credits. Prepare the concrete request and actual quote before asking for any missing spending decision.

## 4. Review and deliver

Use a separate **Realism and Anti-Slop Reviewer** on actual outputs, or on the actual written material for a requested text-only brief or demo. Review commercial clarity, supported claims, identity, physics, text/CTA and complete video/audio when accessible. Prompts, thumbnails and sampled frames cannot pass a full-media review. State actual coverage.

Repair the smallest defective unit, at most two planned repair passes per asset within the authorized scope unless the user specifies otherwise. Preserve accepted work and uncertain-job reservations. Return real artifacts or clearly labeled briefs/demos, review results, remaining limitations and what a later test could teach.

The workflow ends at creative delivery. Do not open Ads Manager, publish/launch ads, set advertising budgets, configure tracking, contact customers or create monitoring/scaling routines. A separate explicit campaign request is outside this skill's creative workflow. Analysis of supplied performance can inform a new creative brief without changing campaigns.

Never invent product properties, reviews, ratings, results, discounts, scarcity, guarantees or platform capabilities. A fictional design may contain explicitly proposed features; its visualizations do not establish real performance. Do not describe outputs as automatically legally cleared, policy compliant or profitable.

For behavioral checks, use [evaluation scenarios](references/examples.md).
