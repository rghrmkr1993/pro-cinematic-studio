# Asset library, versioning and backup

Labels: (3P) secondary, (E) estimate, (A) assumption. Root: `C:/Claude Code/company/creative/<client>/<film>/` (use "internal" when there is no client). Base tree: film-studio shot-production-at-scale.md section 6; this file adds the library layer.

## 1. Library layout
```
00_dev/   01_bibles/   02_previs/   03_shots/   04_audio/   05_edit/   06_delivery/
ledgers/  locks/       tracking/    legal/      library/    log.md
legal/     chain_of_title/, releases/, consents/, music_licences/, cbfc/, eo/
tracking/  shots.csv, scene_budgets.csv, reports/
library/   style_frames/, characters/, locations/, props/, wardrobe/, luts/, fonts/, plates/, reusable_shots/, prompts_that_worked/
```
- `library/` holds cross-sequence assets that several scenes reuse; bibles reference them by ID, never by a copy.
- `reusable_shots/` for establishing shots and cutaways; record in the tracker with notes so reuse is not billed twice.
- `prompts_that_worked/` mirrors winning prompts to `C:/Claude Code/company/creative/prompt-library.md` (creative-studio learning loop).
- Client-neutral: one client's assets never sit in another project's library.

## 2. Naming
`<shot_id>_<kind>_v<NN>[_<tag>].<ext>` for shot files: `S03-SC07-SH012_take_v03.mp4`, `S03-SC07-SH012_last_v03.png`, `S03-SC07-SH012_approved_v01.mp4`.
Assets: `CHAR-001_front_v02.png`, `LOC-004_plate_v01.png`, `WARD-002_sheet_v01.png`, `STYLE_header_v03.txt`.
Rules: lowercase kind, zero-padded versions, ASCII only, no spaces, ISO dates (YYYY-MM-DD) when a date is needed, no "final_final".

## 3. Versioning
- Files are immutable once written: a change creates v+1; the old version stays until delivery and archive.
- A change note in the sequence log: what changed, why, who approved.
- Text assets (prompts, bibles, scripts, EDLs, tracker CSVs) go in git or a similar version history (A: a local repo, no cloud push without the user's yes); binary media is versioned by filename plus the manifest.
- Lock files (`locks/S##.lock.md`): freeze style header, prompts, seeds, settings, reference hashes, model version at the sequence signing. A model update mid-film is handled as in shot-production-at-scale.md section 5.
- Manifest: `manifest.sha256` per folder (path and SHA-256), refreshed before every backup; the delivery master has its own checksum line.
- Never edit an approved file in place; export a copy.

## 4. Backup: 3-2-1 (widely used rule, 3P)
- 3 copies of anything you cannot regenerate for free: the working copy plus two backups.
- 2 different media or systems: for example the working disk plus an external drive or a NAS.
- 1 copy off-site or in a separate location: a cloud storage bucket or a drive kept elsewhere. Put confidential unreleased material only where the user approved, with encryption (A: client approval and terms check; no upload to a generator or any tool without it).
Priorities by value:
| Tier | What | Frequency |
|---|---|---|
| A (irreplaceable or costly) | approved and final takes, prompts, seeds, references, character and style sheets, voice recordings and stems, music masters, EDL and project files, legal and consent files, tracker CSVs | at least daily, plus at each sequence lock |
| B (reproducible at a cost) | rejected takes kept for repair, proxies, intermediate renders | weekly |
| C (cheap) | caches, temporary renders | not backed up |
Rules:
1. Daily: copy the day's Tier A changes to backup 1; weekly: sync to the off-site copy.
2. Verify with the checksum manifest after each backup run; record date and result in `log.md`.
3. Test a restore each month: restore one sequence folder to a scratch folder and play it.
4. Keep the generator's own history out of the plan: platform libraries can expire or change terms; download approved outputs as soon as they pass QC.
5. Retention: keep everything until delivery and the archive lock; then keep the archive for the contractual term (E: at least 3 years, the length of typical E&O coverage after release, 3P).
6. Deletion needs the user's explicit yes; never delete takes before delivery and archive.
7. Encrypt the off-site copy of unreleased work; store keys separately from the backup.

## 5. Archive at delivery
Archive package: master and mezzanine, stems, textless elements, subtitles, DCP, EDL and project files, prompts, seeds, lock files, references, tracker CSVs, take ledger, consent and rights file, music licences, QC report, a README listing contents and the date. Checksum the package; store 3-2-1.

## 6. Handover and access
- One owner per folder (producer for tracking and legal, editor for 05_edit, prompt-engineer for 03_shots, and so on).
- Read-only access for reviewers where the system allows.
- Handoff note updated after each milestone (the standing continuity rule).
