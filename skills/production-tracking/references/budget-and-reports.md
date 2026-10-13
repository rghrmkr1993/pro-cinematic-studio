# Credit budget, burn chart and production reports

Labels: (3P) secondary, (E) estimate, (A) assumption. All credit figures are estimates until the live Generate button or invoice confirms them. Planning rates come from film-studio SKILL.md section 4 (Higgsfield vendor figures about 75 credits for an 8 s 720p shot and about 150 for a 15 s 1080p shot, 20 credits per USD, stated 2026-10-13; recompute before any quote).

## 1. Credit budget per scene
1. Count shots and seconds in the scene from the shot list.
2. For each shot: expected takes (planning 4 per kept shot, optimistic 1.5, pessimistic 10) times credits per proof take, plus one final render at 1080p for kept shots (E).
3. Scene budget = sum over shots, then add the known multipliers: heavy action or non-human leads (use the pessimistic row), many speaking close-ups (lipsync takes), dubbing and audio tools (8 to 12 percent at project level).
4. Contingency: 15 percent held at project level, released by the Manager.
5. Scene budget table (tracking/scene_budgets.csv): scene, credit_budget, start_date, end_date, owner, notes.
6. Project cap: the sum of scene budgets plus contingency must not exceed the cap the user approved; a changed quote needs a new yes.
7. Calibration: the first scene or sequence is the calibration run; re-quote the rest from its actual credits per runtime minute.
Cheaper routes to record in the plan: animatic first, 720p proofs, reuse establishing shots, held shots and cutaways, fewer speaking close-ups per scene.

## 2. Daily production report (tracking/reports/YYYY-MM-DD-daily.md)
```
DAILY REPORT <project> <date>  by producer
Shots: planned N | prompted N | drafted N | approved N | final N (complete X of Y)
Today: generated N takes, approved N shots, finals N
Credits: spent today N | cumulative N | budget N | burn P percent | balance on platform N
Worst scene: SCxx at P percent of budget (flag if over 100)
Overdue: list shot IDs with days late and owner
Blocked: item, who unblocks, needed by
Waste: credits on rejected takes today N (P percent), top defect tag
Backup: last backup date, checksum result
Decisions needed from the user: quote approvals, consents, spend
```
Keep to one screen. The script prints the first four blocks; paste its output.

## 3. Weekly production report (tracking/reports/YYYY-Www-weekly.md)
```
WEEKLY REPORT <project> week <ISO week>
1. Progress: shots complete by sequence (table), runtime assembled, gates passed (G1 to G5, film-legal-distribution G-L1 to G-L3)
2. Burn: spent versus plan this week and to date; burn chart; forecast to complete (spend per completed shot times shots remaining, an estimate); contingency used
3. Quality: first-pass approval rate, average QA score, keep rate, waste rate (target under 25 percent of credits on rejects), top three defect tags and the fix tried
4. Schedule: planned versus actual by sequence; slips and cause; critical path items
5. Rights and legal: consents outstanding, music licences outstanding, CBFC or festival dates, lawyer review status
6. Risks: top three with owner and mitigation
7. Decisions needed from the user: quotes, spends, approvals
```

## 4. Burn chart (text and CSV)
Track cumulative credits actual against cumulative budget per day.
CSV `tracking/burn.csv`: `date,planned_cumulative,actual_cumulative,remaining_budget`.
Text chart (ASCII, paste in reports):
```
SC01 [####################] 100% of 600
SC02 [########............]  38% of 400
TOTAL[###############.....]  75% of 1000
```
Reading it: above the planned line means overspend or ahead of schedule (check shots done); below the line with shots late means a stall. Burn up chart for shots (completed shots versus planned) next to the credit chart shows whether spend buys progress; a rising credit line with a flat shot line means rerolls (fix prompts or references).
Optional: render a chart image with Python's standard tools only if the user wants one (the text version is the default).

## 5. Thresholds (E, adjust per project)
- Scene over 100 percent of budget: stop new generation in that scene, review prompts, request a re-quote and the user's yes.
- Project at 85 percent of cap: warn the Manager the same day.
- Keep rate under 25 percent for two days: stop and fix references or prompts.
- A shot over 2x its estimate: note the cause (hands, crowd, lipsync, long action).
- Any critical fail (unconsented likeness, protected IP) halts the shot and goes to the Manager at once.

## 6. Schedule basics
Plan by sequence: lock locks, produce, QA, sequence lock, then the next. Use `due_date` per shot and per-scene start and end dates; put the user's approval windows (quotes, finals) as schedule items because they are the usual delay. Re-plan weekly; never promise a date without a buffer (E: add 20 percent).

## 7. Reconciling
Before sending a report: the number of shots equals the shot list; credits actual equals the take ledger sum; spend ties to the platform's usage history (A: check the platform's account page, the user's account only); every scene has a budget; every overdue shot has an owner.
