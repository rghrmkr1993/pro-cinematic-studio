# Audience-first workflow, demo mode and communication

## Intent and continuity

An instruction-editing request is not a campaign request. Read attached workflows as source material and change the requested skill; do not research their example products or execute their account actions. If the user redirects an active campaign into skill editing or a demo, stop its pending later-stage work and retire irrelevant sign-in/spending questions.

Record `brief.mode` as `live` or `demo`. A request to test/show/rehearse the skill defaults to demo unless the user explicitly wants actual research or asset creation. State this assumption once and start; do not make the user answer an intake form just to see the workflow. A real product may be used as a demo example; a fictional product may be the subject of real media production. Distinguish execution mode from product reality.

Stay in demo mode through “yes”, “continue”, “looks good”, corrections and simulated review replies. Change mode only on an explicit request for actual execution, retaining useful work but rechecking its evidence. Illustrative audience findings never become real findings merely by changing a mode flag. If the user requests real research within a walkthrough, perform that read-only portion honestly while keeping generation simulated until actual media is explicitly requested.

Resume at the established stage after a status question or interruption. Reuse a relevant audience analysis; do not research again just because the conversation resumed. A material change to product, market, segment or evidence basis needs a refreshed audience decision. A punctuation/CTA correction to an existing accepted creative normally reuses its audience basis; inspect and record reuse instead of conducting an unrelated market study. Reconciliation of already-submitted jobs proceeds even if new-production gates are not ready.

## First response and minimal intake

Read the supplied brief before asking. Confirm what is known and begin audience work, e.g. “First I’ll look at when people buy this, what they compare it with and what makes them hesitate.” Do not lead with “static or video?”, an invented hero design, a product sheet, a provider login or a credit quote.

For an actual assignment, a useful description often suffices to start category/buyer research. Ask a narrow question only if the category or essential business context cannot be inferred. State market/language limitations; do not infer geography from a file path. Use a price already supplied but do not demand a store URL, budget or ad account to begin.

For a demo with no product, choose a plainly hypothetical ordinary example and say so; if the user supplied one, use it. Product specifications in a fictional design can be proposed after the audience stage. Do not manufacture feedback from fictional customers.

## Stage boundary

| Current stage | Permitted work | What waits |
|---|---|---|
| Audience | Read brief; identify alternatives; inspect buyer sources or demonstrate that method; evidence synthesis; segment fit | Ad Library creative hunt; generation prompts; product/character generation; provider/account setup; spending questions |
| Strategy | Inspect ads/destinations in live mode; choose the message, evidence, format and CTA for the audience | Generation until the audience basis is ready |
| Generation | Prepare and check copy, prompts, scene instructions and assets internally; resolve tools/costs; generate and assemble authorized media | Campaign/account launch and management are outside this skill |
| Delivery | Show actual artifacts or labeled demos or explicitly requested text-only briefs, review coverage and remaining limitations | No automatic publication, campaign activation or monitoring |

Delegation follows these boundaries. Parallelize independent audience sources during the audience stage; parallelize ad analysis only after the audience direction is visible. Do not let a producer/operator start provider setup in the background while the researcher is still working.

There is no separate concept stage. Move from strategy into production preparation and generation; do not deliver concept cards, pitch options or ask for concept selection unless the user explicitly requests that output. Script/claim checks remain internal production work and do not create a new approval checkpoint.

An audience synthesis must answer: **who in what situation; what progress; what alternative; what hesitation; why this offer; what evidence and counterevidence; what creative consequence**. Show it inline before entering the next stage. An internal file alone is insufficient. This is a substantive checkpoint, not a compulsory permission ritual. Continue authorized work after presenting it unless the user asked to review each stage or a required decision remains unresolved. Respect a specific user request to stop after research.

## Short demonstration

The purpose is to make the causal flow visible, not to recreate a full campaign or prove a market. Default to a compact walkthrough, typically a few paragraphs or a small table:

1. **Audience, illustrative:** one or two plausible purchase situations, alternatives and objections, with supplied evidence distinguished from assumptions. Explain what real research would verify. Do not invent a quotation, an interview count, a linked source or a “research completed” claim.
2. **Strategic choice:** choose one priority and explain how the situation and objection determine the angle.
3. **Ad analysis:** demonstrate what to compare in an available example, or describe a hypothetical mechanism without naming it as an observed ad.
4. **Generation and review:** proceed directly from the selected strategy to a concise explanation of the necessary assets, model roles and final result. Do not insert a concept card or intermediate pitch. Keep any example prompt/copy inside this production explanation only when useful. The full e-commerce trio need not be forced into a short demo; a requested full portfolio still requires authentic reviews. Describe the media checks. Say explicitly that no media was generated. Do not call models, open generation drafts, request sign-in, solicit credit approval, resize/export imaginary assets or start automations.

A staged demonstration may stop at a requested checkpoint. A request to “show the whole flow” may receive all stages in order in the same response. Do not ask for permission between the same simulated steps unless interactive rehearsal was requested. Offline regression checks are a separate mode of evaluation: no network or external mutations, with untested live capabilities labeled.

## Research depth

Live research should be sufficient to support a meaningful choice, with traceable buyer material and contrary evidence, rather than a fixed persona quota. Deep research can use the coverage targets in research.md; a small live creative task can use a smaller clearly reported set. Do not import the old workflow's 30 records per subsegment or default five-plus-five assets. Stop when the requested depth is met or repeated targeted searches add no useful evidence; report gaps and propose only what the evidence supports. Missing evidence narrows claims; it is not permission to fill the ledger with invented facts.

## User-facing language

Keep progress, scripts, demonstrations, handoffs and client-facing documents about the work and its result. Examples:

- “I’m comparing buyer reviews and recurring purchase objections.”
- “I’m checking the available ads and their destination pages.”
- “The inspected ads help inform the message; their sales results are not public.”
- “The page requires sign-in, so that part remains unverified.”
- “The research points to this angle; next I’ll prepare the creative.”

Do not narrate internal task dispatch, reviewer/worker identifiers, validation commands, regression-test results or enforcement mechanisms in ordinary progress and completion messages. Describe the substantive audience finding, creative decision or delivered artifact instead. Keep evaluation records internal unless the user asks for them. Do not echo application-generated tool notifications into the response; the skill cannot control those interface labels. This wording rule does not remove the audience-first sequence or its internal checks.

Do not proactively name internal execution surfaces such as Computer Use, browser automation, clicking/screen control, MCP, runtimes or tool identifiers in ordinary public narration. It is fine to name the relevant source or requested production service, such as Meta Ad Library or Higgsfield. Keep exact mechanisms and identifiers in internal operational records when needed.

This is an editorial rule, not a secrecy promise. If the user directly asks how something was accessed, answer truthfully. Follow any host-required skill notices, permission prompts or disclosures; never hide a needed access request. Do not falsely claim an API integration, installed connection, inspected page, completed research, generated file or fully automatic end-to-end capability. Describe genuine access failures concisely. Internal tool selection remains governed by host rules: use appropriate connectors/APIs first and allowed UI access when needed; do not bypass safeguards to avoid naming a tool.

## Generation requests are not layout-only tasks

For requested new static/video ads, keep `brief.production_mode: "fresh_generation"` (the default). A supplied photo and missing provider access do not change the requested production method. If Higgsfield cannot run after discovery, finish independent research and prompt preparation, then report the specific blocked stage. Do not substitute locally designed posters, other generators or old assets and call the assignment complete. A missing store URL is a destination/claim limitation, not a reason to avoid image generation for a supplied concept.

Use `edit_only` solely when the user explicitly requests only edits/assembly of existing media; retain the actual instruction and its source. Record each newly generated visual with the real Higgsfield job and result. In either mode, do not invent provider calls, progress or completion.

## End of scope

Deliver creative research, strategy, scripts, media and review coverage. Do not carry over launch readiness, Ads Manager setup, pixel/payment checks, ad-account budgets, publishing, optimization actions or automated monitoring from another skill. Supplied metrics can support creative diagnosis. A user who separately requests campaign execution needs that separately scoped task; creative approval never implies it.
