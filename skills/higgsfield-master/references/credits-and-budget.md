# Credits, plans and budget (researched 2026-10-13)
Labels: (V) vendor-official, (3P) third-party, (U) unverified or conflicting. Prices vary by region and change often; confirm on higgsfield.ai/pricing (the page itself did not render for research, so figures below are from help pages and third parties).

## Plans (prices: vendor blog 2026-09-21 agrees with Starter $15, Plus $49, Ultra $129; other cells indicative)
| Plan | Higgsfield blog 2026-10-03 (V) | Krea 2026-09 (3P) | Notes |
|---|---|---|---|
| Free | limited models, no credits | $0, 0 credits, 1 parallel | |
| Starter | $15/mo | $19, 270 credits, 2 video + 4 image parallel | Seedance 2.0 Fast and Mini only |
| Plus | $49/mo ($39 annual) | $59 ($47 annual), 1,200 credits | Seedance 2.5 up to 1080p, 2.0 up to 4K |
| Ultra | $129/mo ($99 annual) | $129 ($99 annual), 3,000 credits | adds Nano Banana Pro unlimited window |
| Team (2-9 seats) | pooled credits | 16 video + 16 image parallel | |
| Scale (5-15) | SSO, spend controls, priority | 32 + 32 parallel | |
| Enterprise | custom, SOC 2, no training on content, IP indemnification (V) | | only plan with indemnity |
Credit value about 20 per USD for plan math (vendor blog 2026-09-21) but Auto-Refill buys at $1 = 18 credits [official, 2026-10-13]. Subscription credits reset each cycle (annual plans every 30 days), no rollover [official, 2026-10-13]. Packs, Auto-Refill and Boost credits last 90 days and stay usable on the free plan after cancelling (corrects the 3P "needs active subscription" claim) [official, 2026-10-13]. Paid plans give watermark-free output; free accounts are watermarked [official, 2026-10-13]. Team 16 image + 16 video parallel, Scale 32 + 32 [official, 2026-10-13]. Help articles publish no per-model credit costs; the Generate button is the only source. See help-center-facts.md.

## Indicative credit costs (3P unless stated; check button)
- Seedance 2.0: 23 (5s 720p), 45 (5s 1080p), 90 (10s 1080p), about 110 (5s 4K). Fast about 12-17 per 5s. Seedance 2.5 about 52 (8s 720p).
- Kling 3.0: 10 (5s 720p), 12.5 (5s 1080p), 20 (10s 720p), 25 (10s 1080p). Veo 3.1: about 29-70 per clip. Wan 2.7: 8 / 13 (5s). Cinema Studio: 25 / 50 (5s).
- Nano Banana Pro about 2 (4K about 4). Soul 2.0 about 0.12. AI Influencer character 1.12 (V). Ads Studio 4 per ad (V). Soul ID training 25 (3P). Genjutsu 15s: 40/104/144 (V). Soul Cast lock about $5 (3P).
- Re-rolls and upscales also cost credits. Sound toggle does not change cost (V). Edit tool costs credits even in an Unlimited window (about 1.5 seen, blog 2026-09-21). Batch size 2 to 4 charges each output [official, 2026-10-13]. Concurrency Boost +4 to +16 parallel for a one-time pack [official, 2026-10-13].

## Unlimited and relaxed modes (V help center)
- Mid and top plans include Unlimited on selected models (zero credits), mostly 365-day windows; newest flagships may get about 7 days; some models give a free-gen pool instead. Window starts at activation, does not restart at renewal; lapses if subscription lapses.
- Web UI only; MCP, CLI, Canvas, Supercomputer always deduct credits [official, 2026-10-13]. Standard queue (slower at peak), 1 video and 2 image at a time on marketplace bundles. Personal human use only: no automation, scripting, sharing or reselling; unusual activity can be slowed or paused [official, 2026-10-13]. Nano Banana 2 and Pro windows cap at 2K, 4K needs credits; window coverage is listed at Manage Account, Subscription.
- Use Unlimited for drafts and look-dev on the web; use credit generations when speed or an agent run is needed. Do not enable or pass any "unlimited" flag unless the user explicitly asks.

## Cheapest path to a final asset (the budget loop)
1. Plan the shot list on paper. Write the concept and the locked prompt.
2. Look-dev stills on a Lite or Unlimited image model (Nano Banana 2 Lite, Soul 2.0 batch 1-4). Pick one hero frame.
3. Lock references: hero frame, Element or Soul ID, location frame, product packshot, brand kit.
4. Proof clip: image-to-video at 480-720p, short (4-5s), Fast/Turbo/Mini model. Hardest shot first.
5. Fix with edits (Edit Video, region edit, Seedream i2i), not blind rerolls. Change one variable per attempt.
6. Final: same prompt and references on the premium model at target resolution, once per shot. Upscale last, only the selected take.
7. Repurpose with Reframe, Expand, Genjutsu swaps, Ad Multiplier rather than new generations.
Note: there is no seed parameter in Cinema Studio (3P), so lock look with hero frame plus start/end frame pinning, not seeds. Where a tool exposes a seed (DoP Advanced), record it.

## Batch strategy
- Test angles before polish: 5 hooks x 1 format at 720p, keep the top 1-2, then re-render finals (3P blog cadence: weekly, 5 variations of the winner, then 10 of top format via Ad Reference).
- Static first: Ads Studio at 4 credits per ad tests angles for the cost of one video second.
- One variable per variant (hook, setting, product, CTA) so results are readable.
- Stagger runs to match concurrency limits; never fire a whole film unproven.

## Avoiding wasted rerolls
Specific prompt, clean front-facing reference, correct duration, supported aspect ratio, no real faces or IP (IP and NSFW blocks are refunded automatically in most cases, verify under Manage Account, Usage [official, 2026-10-13]), avoid contradictions between prompt and image, avoid extreme camera moves, one action per beat, preflight cost, keep a generation ledger (attempt, change, outcome) to learn hit rate (3P after about 30 entries). Failed generations are auto-refunded within minutes [official, 2026-10-13], except Grok, which is charged at start; mediocre ones are never refunded. Queued jobs can be cancelled for an instant refund.

## Budget template per job
Concept 0 | stills 10-30 credits | proofs 3-5 clips x 10-25 | finals shots x cost | repurpose 10 percent | contingency 20 percent. Report the estimate before running; stop for user approval above the agreed cap.

## Claude-side token discipline (agents)
1. Read SKILL.md only; open at most one reference file per task (each under about 150 lines). 2. Summarise reference rules into the brief; never paste files. 3. Use Haiku for search and docs, Sonnet for prompt writing, Opus only for final creative review or compliance sign-off. 4. Keep a per-brand text bible (palette, light, grade, type, mood) of under 12 lines and reuse verbatim. 5. Batch prompt writing: one call writes the whole shot list. 6. Log results in a short ledger, not long prose. 7. Do not re-research the platform per job; re-verify only the items this skill marks (U).
