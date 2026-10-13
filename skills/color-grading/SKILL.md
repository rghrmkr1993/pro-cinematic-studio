---
name: color-grading
description: "Colour pipeline and grading for AI film and ad footage: log to display, ACES and AgX, Rec.709 versus DCI-P3 versus HDR, primary and secondary correction, shot matching across clips from different AI models, skin tone line and vectorscope (correct Indian and South Asian skin, never lightened), looks by genre, creating and applying LUTs (ffmpeg lut3d, DaVinci Resolve free), grain and halation, and a final colour QC checklist. Use after picture lock and before QA, or whenever clips from several models must look like one film."
license: MIT
user-invocable: true
metadata:
  version: "1.0.0"
  researched: "2026-10-14"
---
Part of the cinematic pipeline: entry point creative-studio

# color-grading

Grading is the last picture decision: it makes many generated clips read as one film. Owner agent: colorist (after the editor's picture lock, before continuity-supervisor QA). Labels: (V) vendor-official, (3P) third-party or colourist commentary, (H) house rule, (E) estimate, (U) unverified.

## 1. Scope and boundaries (do not duplicate)
- Look intent and prompt words (palette, stocks, genre looks, grain words): `cinematography` references/color-and-look.md. Read it, do not copy it.
- Conform, ffmpeg assembly, LUT one-liner, loudness: `film-studio` references/editing-and-assembly.md sections 4 to 5.
- Skin realism in the generation itself: `photoreal-humans`; tone ranges per region: `asian-human-reference`.
- This skill adds: pipeline theory, correction order, matching across models, skin and scopes, LUT authoring, grain and halation craft, and colour QC.

## 2. Reality of AI footage (read first)
- Clips arrive as 8-bit, Rec.709 or sRGB, with contrast and a look baked in. There is no true log and no highlight recovery (E, H). Plan a restrained grade: match, balance, one look, grain.
- A log-style prompt ("flat log look") gives a low-contrast clip, not real log data; treat it as display-referred (H).
- ACES, HDR and wide gamut do not add information to 8-bit SDR clips. Use them only when the deliverable or CG plates demand it (pipeline-and-colour-spaces.md).
- Models drift in white balance and contrast shot to shot, even with the same prompt. Matching is most of the work.

## 3. Pipeline in order (one pass, no stacking)
1. Conform: one fps (24 unless the brief says otherwise), one size, one tag set. See editing-and-assembly.md section 3.
2. Input tag per source: sRGB or Rec.709 per what the tool exported; never guess from filenames; test with a chart frame (H).
3. Primary balance per shot: exposure, white balance, contrast, saturation.
4. Skin check on every shot with a face: vectorscope line and waveform level (correction-matching-skin.md).
5. Shot match inside each scene, then scene to scene to the hero frame.
6. Secondaries: sky, product, background, vignette. Keep them subtle and tracked.
7. One look LUT or one look node (luts-and-ffmpeg.md); never two creative LUTs.
8. Grain and halation last, after the look, same recipe for the whole film (grain-halation-looks-qc.md).
9. Export per deliverable, tag the colour metadata, run the QC checklist.

## 4. Hard rules
- Skin-tone fidelity: the tone in the asset lock is the tone in the master. Never lighten, desaturate toward grey, or warm-shift skin for a "glow" or a beauty look. Measure before and after (correction-matching-skin.md section 4). This is a critical fail in the studio scorecard.
- Product and cosmetic colour honesty: true white balance, no teal skin cast, no grade that implies a result or hides a texture. Any claim stays with the qualified team.
- Grade the hero frame first; match the rest to it. Do not grade each shot to taste.
- Grade on a calibrated display with scopes. A laptop panel or phone is a check, not the reference (3P, H).
- Every look is a documented recipe in grade-notes.md: LUT id, node order, grain settings. No undocumented tweaks.
- No spend. Free tools first (ffmpeg, Resolve free). Paid plugins or Resolve Studio need the Manager and the user's yes.

## 5. Router: which reference to open
| Need | Open |
|---|---|
| Log to display, ACES, AgX, Rec.709 vs P3 vs HDR, tagging, tone-mapping | references/pipeline-and-colour-spaces.md |
| Primary and secondary correction, scopes, matching AI clips, skin tone line, Indian skin | references/correction-matching-skin.md |
| Make, apply and test LUTs, ffmpeg recipes, Resolve free steps | references/luts-and-ffmpeg.md |
| Looks by genre, grain, halation, bloom, final QC checklist | references/grain-halation-looks-qc.md |
Open at most two references per step.

## 6. Quick recipes
1. Match a clip to the hero frame: signalstats on a neutral patch in both, adjust gain and white balance until YAVG and U/V means agree (luts-and-ffmpeg.md section 5).
2. Apply a look in batch: `ffmpeg -i in.mp4 -vf "lut3d=file=look.cube:interp=tetrahedral" ...` after conforming to Rec.709 (verified, ffmpeg 9.0.1).
3. Add film texture last: grain at 4 to 8 on the `noise` filter plus a subtle highlight halation (recipe in grain-halation-looks-qc.md section 2).
4. Mixed-model film: one corrective LUT per model to the style frames, then one unified look (correction-matching-skin.md section 3).
5. Indian skin on a warm or golden-hour look: keep hue on the line, hold skin luma, let the grade move the background, not the face.

## 7. Outputs
In `C:/Claude Code/company/creative/<client>/<project>/`: grade-notes.md (pipeline, LUT ids, node order, grain recipe, per-scene notes), graded master, flat QC copy, LUT files, before and after stills of every skin check, colour QC table.

## 8. Related skills
`cinematography` (look intent), `film-studio` (conform and delivery), `edit-director` (code edits, ffmpeg engine), `photoreal-humans` (skin tells), `asian-human-reference` (regional skin ranges), `vfx-compositing` (matching plates before grade), `higgsfield-master` (what each model bakes in).

## 9. Report format (8 lines max)
Pipeline used, sources tagged, looks applied (LUT id), skin check result (pass or fail, numbers), matching status per scene, QC table result, open risks (HDR, display calibration, Resolve edition), what needs the user's yes.
