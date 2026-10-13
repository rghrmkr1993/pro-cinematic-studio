---
name: production-tracking
description: "Production tracking for AI films, series, shorts and ad campaigns: a shot tracker schema (shot ID, scene, status planned/prompted/drafted/approved/final, takes, credits estimate vs actual, model, seed, owner, approval), asset library structure, versioning and 3-2-1 backup rules, a credit budget per scene with a burn chart, and daily and weekly production reports. Includes a ready CSV template and a standard-library Python script (references/tracker.py) that prints status counts, credits spent vs budget and overdue shots. Load at project start, during every shooting-equivalent day, and for any budget, schedule, status or backup question. Never spends credits itself."
license: MIT
user-invocable: true
metadata:
  version: "1.0.0"
  researched: "2026-10-14"
---
Part of the cinematic pipeline: entry point creative-studio

# production-tracking

The control layer for a pile of generated shots: what exists, what state it is in, what it cost, who owns it, and what is late. Owner: producer agent. Readers: creative-director, prompt-engineer, editor, continuity-supervisor, the Manager.

It extends, and does not repeat: film-studio `shot-production-at-scale.md` (manifest, take ledger, folder tree, locks, retakes), `bibles-and-continuity.md` (shot IDs, ledgers), `film-legal-distribution` (rights and release gates), `higgsfield-master` `credits-and-budget.md` (credit prices). Credits are quoted and spent only with the user's yes; this skill records and reports, it never generates.

Concepts follow the big production trackers (ShotGrid or Flow Production Tracking, ftrack, Kitsu) in a small, file-based form: projects hold sequences, scenes and shots; shots have tasks, versions (takes), statuses, owners and review notes (3P, vendor docs and comparison articles). A CSV is enough for a short film; move to Kitsu (open source, self-hostable, 3P) when many people need live review.

## 1. Router
| Need | Open |
|---|---|
| Shot tracker columns, status rules, take ledger link | references/schema-and-statuses.md |
| Asset library folders, naming, versions, 3-2-1 backup | references/asset-library-and-backup.md |
| Credit budget per scene, burn chart, daily and weekly reports | references/budget-and-reports.md |
| Run the report | references/tracker.py (with shot-tracker-template.csv, scene-budget-template.csv) |
Load this file plus at most two references per step.

## 2. Setup (day 0, no credits)
1. Folder tree: film-studio shot-production-at-scale.md section 6, plus `tracking/` at the project root.
2. Copy `references/shot-tracker-template.csv` to `tracking/shots.csv` and `scene-budget-template.csv` to `tracking/scene_budgets.csv`.
3. Fill one row per planned shot from the shot list (shot IDs are permanent: S03-SC07-SH012). Fill `credits_est` from the approved quote; `due_date` from the schedule.
4. Set scene budgets from the quote (SKILL film-studio section 4 planning rates, an estimate) plus 15 percent contingency held at project level, not per scene.
5. Mark the first sequence as the calibration run; re-quote the rest from its actual burn.
6. Create `tracking/reports/` for dated daily and weekly reports.

## 3. Status ladder (one direction; a step back needs a note)
planned > prompted > drafted > approved > final.
- planned: shot exists in the list; refs and boards ready or pending.
- prompted: prompt written, 512 check done, quoted; not yet generated or waiting for the yes.
- drafted: at least one take generated at proof tier.
- approved: a take passed the scorecard (85 drafts) and continuity QA; creative-director initial in `approval`.
- final: final-quality render passed 90 and is in the edit lock; archived with prompt, seed and refs.
Gates: no `prompted` to `drafted` without the user's yes on spend; no `approved` to `final` without the final quote and yes. Failed QA moves back to `drafted` with a defect tag.

## 4. Daily routine (producer, 10 minutes)
1. Collect results from the take ledger and `log.md`; update `takes`, `credits_actual`, `status`, `seed`, `model`.
2. Run `python -I references/tracker.py tracking/shots.csv --budgets tracking/scene_budgets.csv` and read the three blocks: status counts, credits versus budget, overdue.
3. Write the daily report (budget-and-reports.md section 2) in `tracking/reports/YYYY-MM-DD-daily.md`.
4. Flag anything over 100 percent of a scene budget or 85 percent of the project cap to the Manager the same day.
5. Back up the day's approved assets (asset-library-and-backup.md section 4).

## 5. Weekly routine (producer, 30 minutes)
Weekly report (budget-and-reports.md section 3): progress by sequence, burn versus plan, waste rate (target under 25 percent of credits on rejected outputs, an estimate), top defect tags, re-forecast to complete, schedule risks, legal and rights status (film-legal-distribution gates), decisions needed from the user.

## 6. Rules
- Source of truth: the tracker CSV plus take ledger; chat is not a record.
- Never delete takes before delivery and archive; keep approved plus the last two rejects per shot (film-studio rule).
- Credits are estimates until the live Generate button or invoice confirms them; mark estimates as such.
- No client names or brands in sample data or in another project's tracker.
- Confidential files stay in the project folder; do not upload tracking data containing scripts or personal data to outside tools without the user's approval.
- Spend, publish, delete: the user's yes via the Manager.

## 7. Check before reporting
Run the script on the real CSV, confirm total shots equals the shot list, no unknown statuses, no unreadable dates, budgets present for every scene. A report that cannot reconcile to the shot list is not sent.

## 8. Report to the Manager (10 lines max)
Shots by status, credits spent versus budget (total and worst scene), overdue shots, waste rate, forecast to complete, backup status, risks, decisions needed.
