# Shot tracker schema and statuses

Labels: (3P) secondary, (E) estimate, (A) assumption. File: `tracking/shots.csv`, UTF-8, one row per shot, header in `shot-tracker-template.csv`.

## 1. Columns
| Column | Type | Rule |
|---|---|---|
| shot_id | text | Permanent, S##-SC##-SH### (bibles-and-continuity.md); never reused |
| sequence | text | S## |
| scene | text | SC## (one location, continuous time); used for budgets |
| status | enum | planned, prompted, drafted, approved, final |
| takes | integer | Count of generated takes for the shot, including rejects |
| credits_est | number | From the approved quote for this shot (all takes planned) |
| credits_actual | number | Summed from the take ledger; updated daily |
| model | text | Model and version of the best take (for example the Seedance version string) |
| seed | text | Seed or job id of the approved take, blank when the tool gives none |
| resolution | text | 720p proof or 1080p final, and so on |
| seconds | number | Clip length of the approved take |
| owner | text | Agent role, such as prompt-engineer; one owner per shot |
| approval | enum | pending, approved, rework |
| approved_by | text | Role that approved (creative-director for finals) |
| approved_date | date | YYYY-MM-DD |
| due_date | date | YYYY-MM-DD from the schedule |
| defect_tag | text | face, hand, limb, morph, physics, prop, wardrobe, light, text, lipsync, audio, speed, camera, other |
| last_frame_file | text | Path to the last-frame PNG for chaining |
| notes | text | One line, no commas or quote them |
The tracker script requires: shot_id, scene, status, credits_est, credits_actual, due_date. Other columns are for people and tools.

## 2. Related files
- `ledgers/take_ledger.csv` (shot-production-at-scale.md section 7): one row per take with credits and verdict; `takes` and `credits_actual` are summed from it.
- `ledgers/continuity S##.csv`: continuity checks per sequence.
- `locks/S##.lock.md`: frozen headers, seeds, settings after a sequence is signed.
- `ledgers/music_licences/`, `ledgers/consents/`: rights (film-legal-distribution).
- `log.md`: chronological record (creative-studio section 8).

## 3. Status rules
1. planned: shot in the list; start frame, refs and board known.
2. prompted: prompt file exists, 512 check done, quote line added; waiting for the user's yes or the generation window.
3. drafted: one or more proof takes exist; scorecard run.
4. approved: score at least 85 for a draft or edit use, no critical fail, continuity QA clean; used in the rough cut.
5. final: final render at the delivery quality scored 90 or higher, archived with prompt, seed, references; edit lock references this file.
Allowed moves: forward one step at a time; back to drafted on a failed QA; planned to final directly only for non-generated shots (titles, stock) with a note.
Approval is a column, not a mood: `approval=approved` plus `approved_by` and `approved_date` are required for approved and final.

## 4. Derived measures (computed by tracker.py or by hand)
- Completion: approved plus final over total shots.
- Burn: sum of credits_actual over budget, per scene and total.
- Variance: credits_actual minus credits_est per shot; a shot over 2x its estimate is flagged in the weekly report (E).
- Keep rate: approved or final shots over takes generated (E): a low rate means fix prompts or references, not the dice.
- Overdue: due_date before today and status not approved or final.
- Take efficiency: takes divided by shots; compare with the planning figure of 4 takes per kept shot in film-studio section 4 (E).

## 5. Larger projects
Hundreds of rows: keep one CSV per sequence plus a merged read-only file, or move to Kitsu (open source, supports shots, tasks, statuses, versions, annotated review, playlists; 3P, CGWire) or ShotGrid or ftrack if the user already pays for them. Map statuses explicitly when migrating, because vocabularies differ and hold or waiting states may not map one to one (3P). Keep the CSV export as the audit trail.
