# Production pipeline: studio SOP (2026-10-13)
Eight steps, each with an owner agent, inputs, outputs and a gate. The Manager sequences; no step spends credits without the user's yes (mcp-operations.md section 0). Brand names stay inside their own project.

## 1. Brief (growth-marketer, or revenue-strategist for paid pitches)
Inputs: client request, product facts, platform, audience, budget cap, deadline, claim list approved by the regulatory reviewer.
Outputs: one-page brief: objective, KPI, platform and ratio, tier, must-haves, must-nots (absent features, banned claims), territory (India: no TikTok), credit cap.
Gate: PASS if objective, platform, claims, cap and consent status are all stated. FAIL (return) if any is missing.

## 2. Creative concept and moodboard (creative-director)
Inputs: brief, brand kit or text bible, product packshots.
Outputs: one concept (visual idea, emotional trigger, why it converts), moodboard of 4-6 look-dev stills or references, tool and model choice with a one-line reason, credit estimate.
Gate: PASS if one concept only, product angle-locked to the real packshot, palette matches the brand hex values. FAIL if a survey of options or a generic style.

## 3. Prompt pack (creative-director)
Inputs: concept, locked assets (product sheet, character sheet, location refs), model dialect (model-dialects.md).
Outputs: shared style header, per-shot prompts in model dialect, negatives, shot list with duration, aspect, start and end frames, take ledger template.
Gate: PASS if each prompt follows subject, action, environment, camera, style, constraints; one camera move; no baked text, prices or logos. FAIL otherwise.

## 4. Draft generation (creative-director; needs the user's yes after the quote)
Inputs: prompt pack, balance, quote.
Outputs: hardest-shot proof at 720p on a cheap model, then remaining proofs; job ids in the log.
Gate: stop at the budget cap; 4 of 4 bad takes means rewrite the prompt, not reroll.

## 5. Review (qa-tester, using the higgsfield-master QA checklist)
Inputs: draft frames and clips, claim list, brand kit.
Outputs: scored review with frame references; fix list.
Pass/fail criteria (all must pass):
- Product fidelity: one product, correct shape, scale, cap and label logic against the packshot; label not gibberish; never enlarged to be readable.
- Text legibility: any in-frame text exact and readable at phone size; otherwise none (overlay later). 9:16 safe zones: 14 percent top, 35 percent bottom, 6 percent sides.
- Hands and skin: correct hand count and fingers, grip logic, pore-level skin, no plastic sheen, no face drift between cuts, no morphing at the 5-8s mark.
- Brand colours: key colours within visual tolerance of the brand hex values under a neutral grade; consistent grade across shots.
- Compliance: no fabricated testimonial or result, no exaggerated effect, consent on file for any real likeness, AI label decided, claims on the approved list, no formulation or customer data visible.
Gate: PASS needs zero fails. Any fail goes back to step 3 or 4 with ONE variable changed. Max 3 review rounds, then escalate to the Manager.

## 6. Final generation and upscale (creative-director; user yes on the final quote)
Inputs: approved prompt pack and refs, final quote.
Outputs: premium-model finals at target resolution, once per shot; chosen takes upscaled; formats via reframe and outpaint; de-slop pass if needed.
Gate: second QA pass by qa-tester on the finals (same criteria). Skin re-checked after every edit pass.

## 7. Ad copy and specs (growth-marketer)
Inputs: approved masters, brief, claim list.
Outputs: headlines, primary text, CTA, overlay copy, platform spec sheet (ratio, length, file size, safe zones, AI label wording), naming convention, UTM plan.
Gate: PASS if every claim maps to the approved list and the spec fits the platform. FAIL if invented stats, ratings or reviews. Meta ads are delivered paused; TikTok excluded for India.

## 8. Delivery and asset log (creative-director; Manager signs off)
Inputs: finals, overlay copy, log.
Outputs: files in the project folder, text-free masters plus captioned versions, log closed with credits spent versus quote, KPI note (cost per approved asset, approval rate).
Gate: PASS if the log is complete, files are named and the user has the handover. Publishing or posting happens only on the user's explicit yes.

## 9. Asset log format
Path: C:/Claude Code/company/creative/<client>/<project>/log.md (one folder per client; never mix clients). Create on the first job.
```
# <project> asset log
Brief: <one line> | Platform: <ratio, length> | Credit cap: <n> | Consent: <none needed | file ref>
Concept: <one line> | Tool/model: <names> | Brand lock: <element or Soul ID ids>
| # | Date | Step | Tool and model | Prompt ref | Job id | Credits | Result | QA | Notes |
|---|------|------|----------------|------------|--------|---------|--------|----|-------|
Quote: <credits> approved by user on <date> | Spent: <credits> | Balance after: <n>
Approved assets: <count> of <total generated> | Handover: <date, location>
```
Rules: one row per generation attempt, failures included; record the seed if the tool exposes one; update after every step, not at the end.
