---
name: higgsfield-master
description: "Master playbook for Higgsfield (higgsfield.ai): picks the right studio, agent and model for any AI image, video, ad creative, AI influencer, talking avatar, storyboard or faceless-channel job, then drives it with model-native prompts, consistency locks, credit discipline and ad compliance (likeness consent, AI labelling, cosmetic claims). Use first for Cinema Studio, Marketing Studio, Ads Studio, Ad Multiplier, Soul ID, Seedance, Kling, Veo, Nano Banana, Genjutsu, Supercomputer, MCP or CLI work. Research-based, dated 2026-10-13."
license: MIT
user-invocable: true
metadata:
  version: "1.3.0"
  researched: "2026-10-13"
---
Part of the cinematic pipeline: entry point creative-studio

# higgsfield-master

Router and core playbook for Higgsfield. Load this first, then open ONLY the one reference file the job needs (token discipline). Sub-tools that stay in force: `higgsfield-timed-prompts`, `edit-director`, `edit-voice`, `edit-gen`, `create-ads-with-agents`, `faceless-script-writer`, `faceless-video-prompts`, `minimax-h3-motion-design` (installed 2026-10-13 from the creator blog, vetted), `seedance-20` (Seedance prompt dialect), `01-cinematic`..`15-real-estate` (style packs, only when that style is named), `ugc-video-auto`, `ugc-hot-girl`, `higgsfield-image-auto`, `seedance-auto-generate` (Playwright fallback when MCP/CLI is down).
For realistic humans/skin load photoreal-humans.
Labels used in references: (V) vendor-official, (3P) third-party, (U) unverified or conflicting; "[official, 2026-10-13]" marks an item confirmed or corrected by the Academy, help center, guide or blog read on that date. The platform changes weekly: confirm model names, limits and credit cost on the Generate button before relying on any number.

## 1. Decision tree (goal to tool)
| Goal | Use | Open |
|---|---|---|
| Finished product ad from a URL or photo, fast | Marketing Studio (web only), 15s max | ads-studio.md |
| Many static ads from a site URL | Ads Studio (4 credits per ad, 20 per product per run) | ads-studio.md |
| Clone a proven video ad onto our product | Ad Multiplier (ref video 4-30s, up to 20 images) | ads-studio.md |
| Multi-shot scene, film, brand film, up to 30s | Cinema Studio 4.0 (50 refs) | cinema-studio.md |
| Hero spot, maximum photorealism and light | Veo 3.1 (or Cinema Studio) | model-dialects.md |
| Reference-driven product or UGC clip | Seedance 2.0 (4K, 15s) or 2.5 (30s, 1080p, Pro/Plus or above) | model-dialects.md |
| Change one thing in a real or finished clip | Seedance video-to-video, Genjutsu Object Swap, Draw to Edit | academy-lessons.md |
| Cheap variants, camera-directed shots, start/end frames | Kling 3.0 / 3.0 Turbo | model-dialects.md |
| Copy a real performance onto a character | Kling Motion Control or Genjutsu Motion Transfer | tools-a-z.md |
| Persona, ambassador, recurring face | AI Influencer + Soul ID | characters-and-consistency.md |
| People, fashion, UGC stills | Soul 2.0 (+ Soul ID, Moodboard, HEX) | model-dialects.md |
| Cinematic stills, locations | Soul Cinema, Soul Location | visual-language.md |
| Product hero, on-image text, 4K | Nano Banana Pro / 2, GPT Image (sheet edits) | nano-banana-pro-guide.md |
| Edit without regenerating | Seedream, Flux Kontext, Seedance 2.5 Edit, Kling Omni Edit, Edit Video | tools-a-z.md |
| Talking head, voice, dubbing | native audio, Lipsync Studio, Audio tool | tools-a-z.md |
| Storyboard or multi-frame plan | Popcorn (8 frames) | workflows.md |
| Faceless channel, shorts, long agentic job | Supercomputer skills | agents.md |
| Drive Higgsfield from Claude | MCP (web chat) or CLI + skills (Claude Code) | agents.md |
| Clip channel, long video to shorts for income | Katana or edit-director, rights first (claims are creator claims) | clipping-business.md |
Full model table: models-catalog.md. Eleven recipes: workflows.md. Academy curriculum (asset-first pipeline, repair loops): academy-lessons.md. Official plan, credit, refund, ownership and limit facts: help-center-facts.md.

## 2. Creative Director loop (every asset job)
1. READ the brief like an AD: product, tier (drives light, pace, palette), platform, claim risk, absent features (lock as negatives).
2. CONCEPT before prompt: one visual idea, one emotional trigger, why it converts on that platform. Recommend, do not survey.
3. PICK tool and model, state why in one line (section 1).
4. LOCK inputs: brand kit or art-direction bible, Element or Soul ID, product reference (front angle), location reference.
5. PROOF: one cheap shot (720p, short, Fast/Turbo/Lite model). Hardest shot first. Change one variable per iteration.
6. SPOT THE SLOP: frozen-frame QA (checklist below), then fix by edit or reference, not by blind reroll.
7. RENDER finals at target resolution on the premium model, same prompt and references.
8. MULTI-FORMAT from one concept (9:16, 4:5, 1:1, 16:9) with Reframe, Expand, Upscale rather than regenerating.
9. COMPLIANCE gate (section 5), then hand over with a text-free master plus overlay copy.

## 3. Golden rules (top 18, merged with the Academy's own practice)
1. Pick the model first, then write in that model's dialect (model-dialects.md). Never one generic prompt.
2. Image-to-video beats text-to-video for control and cost. Start from a sharp, front-facing, well-lit still.
3. Subject, action, environment, camera, style, constraints, in that order. 60-100 words for Seedance; front-load identity.
4. Separate camera motion from subject motion. One camera move per shot, single direction, smooth. Energy comes from cuts.
5. Specify physical values, not verbs: speed, start/stop distance, start and end pose. "Slow dolly in" alone varies per render.
6. Identity by anchor, not adjectives: Soul ID, Element or reference images (2+ angles). Text faces get reinterpreted every time.
7. Lock lens, light direction and grade identically across a sequence. Change ONE variable between shots.
8. Build locations first as references; location drift is harder to catch than face drift.
9. Chain clips: last frame becomes next first frame. Keep clips under about 30s.
10. One hero product per frame, angle-locked to the real packshot, realistic scale, never enlarged to make a label readable.
11. Hand law: two hands, at most two hand roles per beat, name every contact point. One action per beat; choreograph moves with timings and measurements, never "a dance" or "dramatic".
12. Assets first, prompts second, video third (Academy). Product sheet (front, 3/4, back), character sheet on plain grey with ONE face (erase the duplicate face on the full-body panel), 3/4-angle locations, prop sheets. Test each location with the hero in video before locking.
13. Never bake text, prices or logos into generations. Overlay in editing. Use Nano Banana Pro or GPT Image only when text must be in-frame, and quote it exactly with the font.
14. Anti-AI look: pore-level skin, uneven makeup, muted catchlights, neutral light, deep focus for UGC, then a de-slop pass (Seedream i2i, keep composition, change micro-realism only). Every edit pass softens detail, so check skin after edits.
15. Draft cheap, finish premium: 720p proof, then the same locked prompt at final resolution. Preflight cost every time.
16. Let a prompt-builder skill (Claude) write shot prompts from the script plus the locked assets as images, with one shared style header; edit the header once, not every prompt. Name what is wrong, then change ONE variable.
17. Read failures: 4 of 4 bad takes means rewrite the prompt, a single defect means reroll. Words cannot pin geometry: use a layout map. Keep a take ledger and cut the fragment that solves each job.
18. Compliance is part of quality: consented likeness only, no fabricated testimonials, label realistic AI people, substantiated cosmetic claims. For real footage VFX keep one real anchor and change one thing.

## 4. Quality checklist (frozen-frame QA, every kept clip)
- Hands: count, fingers, grip logic. Product: one only, correct shape, label not gibberish, cap logic.
- Face drift between cuts, teeth, eyes. Wardrobe and background continuity.
- Morphing at 5-8s mark, extra limbs, floating props, impossible physics.
- First frame is mid-motion hook (0.1s law). Audio: lip sync, no hallucinated music or lyrics.
- Safe zones for 9:16 (14% top, 35% bottom, 6% sides, 3P). Legibility at phone size.
- No unsupported claims, no real-person likeness without consent, AI label decided.

## 5. Compliance in one screen (detail: compliance.md; not legal advice)
- Real people: train Soul ID or clone voices only with documented consent; use original characters otherwise. Never a celebrity.
- No fabricated customers, doctors or testimonials; no AI before/after presented as real results. ASCI bans fabricated endorsements even with a label (3P summary of Sep 29 2026 guidance; effective date about late Dec 2026, U).
- Label realistic AI people, virtual influencers and AI product demos ("Video created using AI"). Use Meta AI info and YouTube altered-content controls.
- Cosmetic claims need substantiation and regulatory review by the qualified team; AI visuals must not exaggerate results.
- Terms: outputs are ours, commercial use allowed, but Higgsfield holds a license and may use content to improve its models (Enterprise excluded, only Enterprise has IP indemnity) [official, 2026-10-13]; never upload unreleased formulations, confidential packaging or customer data. Binding Terms of Use prevail.

## 6. Credit discipline (detail: credits-and-budget.md)
Credits: about 20 per $1 on plans, Auto-Refill $1 = 18 [official, 2026-10-13]. Per-model cost is on the Generate button only. Proof at 720p on Fast/Turbo/Lite, finals once. Prefer Unlimited models on the web UI for drafts (MCP, CLI, Canvas, Supercomputer always deduct credits). Never pass an "unlimited" flag or spend money unless the user says so. Failed generations are refunded automatically (not Grok, charged at start) [official, 2026-10-13]. Free accounts are watermarked, paid plans are not; refunds only within 7 days with no credits used.

## 7. Ground rules for agents
- No logins, posting, spending or generation unless the brief asks and the user has approved. Preview-first; `get_cost` preflight when the tool offers it.
- Keep client brands out of other clients' prompts and demos. Text bible per brand, reused verbatim.
- Open one reference file per job. Do not paste reference files into prompts or briefs; summarise.
- Report: tool and model chosen and why, credits estimated, QA result, compliance flags.

## 8. How to run a job (8 steps; owners and gates: references/production-pipeline.md)
1. Brief (growth-marketer): objective, platform, claim list, credit cap, consent status.
2. Concept and moodboard (creative-director): one idea, tool and model (section 1).
3. Prompt pack (creative-director): model dialect, locked assets, negatives.
4. Balance, quote, STOP for the user's yes, then draft cheap (references/mcp-operations.md, section 0 gates).
5. QA review (qa-tester, section 4 checklist and the pipeline pass/fail criteria).
6. Finals once on the premium model, then upscale and reframe (mcp-operations.md workflows 2 to 8).
7. Ad copy and specs (growth-marketer); compliance gate (section 5).
8. Delivery and asset log at C:/Claude Code/company/creative/<client>/<project>/log.md (format in production-pipeline.md).

## 9. Load only what you need (this file plus 1 or 2 references)
| Task | Read |
|---|---|
| Run any job through the MCP | mcp-operations.md |
| Studio roles, QA gates, asset log | production-pipeline.md |
| Product or Ads Studio ads | ads-studio.md, credits-and-budget.md |
| Cinematic scene or brand film | cinema-studio.md, model-dialects.md |
| Prompt in a model's dialect | model-dialects.md |
| Persona, influencer, consistent face | characters-and-consistency.md |
| Product stills, on-image text | nano-banana-pro-guide.md |
| Look, light, camera language | visual-language.md |
| Which model or tool exists | models-catalog.md, tools-a-z.md |
| Cost, plans, budget | credits-and-budget.md, help-center-facts.md |
| Likeness, claims, AI labels | compliance.md |
| Recipes, storyboard, repair loops | workflows.md, academy-lessons.md |
| Agents, CLI, Supercomputer | agents.md |
| Clip channel, repurposing long video to shorts | clipping-business.md |
| Creator techniques (realism, ads, faceless, previz, motion) | creator-playbook-adil.md |

signature-shots.md: 12 named creative camera shots with prompts

Related skills: higgsfield-timed-prompts (timecoded multi-shot Seedance prompts, blocking maps, reframe); edit-director, edit-gen and edit-voice (code-based video editing, captions, generated shots for edits).

References: mcp-operations.md, production-pipeline.md, tools-a-z.md, agents.md, models-catalog.md, credits-and-budget.md, cinema-studio.md, ads-studio.md, characters-and-consistency.md, visual-language.md, model-dialects.md, workflows.md, compliance.md, academy-lessons.md, nano-banana-pro-guide.md, help-center-facts.md, clipping-business.md, creator-playbook-adil.md, sources.md (all in ./references/).
