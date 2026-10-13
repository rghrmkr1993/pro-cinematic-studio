# VFX shot breakdown template
Copy into `C:/Claude Code/company/creative/<client>/<project>/vfx/vfx-breakdown.md`. One row per shot, one block per complex shot. Client-neutral: replace the placeholder text with the project's own names.

## 1. Project header
- Project, client folder, version, date, vfx-artist, reviewer (creative-director).
- Frame rate, resolution, working format (ProRes 422 HQ or 4444), colour space tag, delivery tag.
- Credit cap, quote, date of the user's yes. Free methods used so far.
- Source takes folder (read-only) and output folder.

## 2. Shot table
| Shot ID | Seq | Dur (s) | Source take and model | Issue or VFX need | Rung (free / edit / comp / regen) | Method and tool | Credits est | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| S01-SC02-SH003 | | | | | | | | | todo | |
Rung key: 1 free local fix, 2 targeted edit (Draw to Edit, inpaint, Edit Video), 3 plate replace or composite, 4 regenerate.
Status values: todo, plate prepped, in progress, internal review, approved, delivered to editor, locked.
Priority: A (hero shot or critical fail), B (visible defect), C (polish).

## 3. Per-shot block (complex shots)
- Shot ID and description (one line).
- Frames needing work (in and out) and what is wrong or needed.
- Reference frames: good frame from the same take, the hero frame of the scene, any asset lock (character, product, location).
- Plan: step 1, step 2, step 3 (with the rung and tool each).
- Elements: licensed or generated, source, licence note, consent note if any person.
- Matching notes: light direction and colour, black level, grain, motion blur and shutter, lens and DoF, perspective.
- Skin tone check: patch values before and after (luma, hue, saturation), pass or fail.
- Attempts log: pass number, tool, prompt or settings, credits, result, decision.
- Outputs: clean plate, matte (raw and feathered), comp, before and after stills, notes file.

## 4. Review checklist (per shot)
- [ ] Fix is invisible at 100 percent, in motion, at phone size.
- [ ] Light, colour, grain and blur match neighbours.
- [ ] No new artifacts (halo, shimmer, extra limb, text glitch).
- [ ] Skin tone within tolerance; face identity matches the lock.
- [ ] Product shape and label correct; real label used where needed.
- [ ] No unlicensed element, no real-person likeness without consent, no protected IP.
- [ ] Frame rate, size, tags match the project spec; handles (8 frames each end) kept.
- [ ] Files named by shot ID and version; originals untouched; log.md updated.

## 5. Handoff note to the editor
For each delivered shot: new file name and version, what changed, which frames, any speed or length change (none unless noted), and a before and after still. Picture lock does not start until the editor accepts the versions. After lock, no VFX change without a change note.

## 6. Summary table (end of file)
| Metric | Value |
|---|---|
| Shots in breakdown | |
| Rung 1 / 2 / 3 / 4 count | |
| Credits quoted vs spent | |
| Shots approved | |
| Open risks (consent, licence, resolution) | |
