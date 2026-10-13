---
name: vfx-compositing
description: "VFX and compositing for AI film and ad shots: alpha, mattes, roto and keying basics, AI cleanup of hands, text and artifacts with inpaint, Higgsfield edit tools and image-model edits, sky replacement, set extension, crowds, particles, CG plus AI integration, AI plus live-action hybrids, matching light, grain and motion blur, free tools (Fusion in Resolve, Natron, ffmpeg overlay and chromakey) versus paid ones, and a VFX shot breakdown template. Use after generation and before the edit lock whenever a take is nearly right but needs a fix, an element, or a plate swap."
license: MIT
user-invocable: true
metadata:
  version: "1.0.0"
  researched: "2026-10-14"
---
Part of the cinematic pipeline: entry point creative-studio

# vfx-compositing

Fix or build the shot after generation, before the picture lock. Owner agent: vfx-artist (between prompt-engineer's takes and the editor). Labels: (V) vendor-official, (3P) third-party, (H) house rule, (E) estimate, (U) unverified.

## 1. Principle: repair before regenerate
Regenerating costs credits and risks losing the good parts of a take. Order of attack (cheapest first):
1. Free local fix: crop, reframe, speed, ffmpeg or Fusion comp, cutaway or insert instead of the broken moment (editor).
2. Targeted edit: mask a region and re-generate only that (Higgsfield Draw to Edit, inpaint, Edit Video; image-model edit of a keyframe).
3. Plate replacement or composite: keep the good plate, add or swap an element.
4. Full regeneration with a fixed prompt, only after 1 to 3 fail. Never reroll blindly (creative-studio rule).
Spend on 2 to 4 needs a credit quote and the user's yes. Free steps (1 and local comps) spend nothing.

## 2. Boundaries (do not duplicate)
- Single-clip prompting and hands law: `higgsfield-master`, `photoreal-humans` (realism-qa-checklist.md).
- Camera and lighting intent: `cinematography`. Colour after VFX: `color-grading`.
- Edit tool names and credits: higgsfield-master references/tools-a-z.md (Edit tools, Draw to Edit, Genjutsu, Relight, Upscale).
- Real-footage cutting and ffmpeg conform: `film-studio` editing-and-assembly.md, `edit-director`.
- 3D rendering and engines: `graphics-rendering`, `webgpu-wgsl`.

## 3. Hard rules
- Originals and consent: no real person's face or voice without written consent; no copyrighted characters, plates or logos; stock plates need a licence record.
- No misleading composite: a before and after or a result shot must not be faked with VFX; skincare and cosmetic claims stay with the qualified team.
- Skin tone: composites and relights must not lighten or shift a face (see color-grading skin check).
- Keep every original take; work on copies (originals folder read-only). Name outputs by shot ID plus version.
- Match before polish: light direction, colour, grain, motion blur and perspective first; edge quality second.
- Log each fix and its credits in log.md; never expand scope beyond the shot list.
- Free tools by default; paid plugins or subscriptions need the Manager and the user's yes.

## 4. Router: which reference to open
| Need | Open |
|---|---|
| Alpha, premultiply, mattes, roto, keying, tool choice and free versus paid | references/compositing-basics-and-tools.md |
| Fix hands, text, faces, artifacts, flicker, object removal with AI | references/ai-cleanup-and-fixes.md |
| Sky replacement, set extension, crowds, particles, CG plus AI, hybrid, matching light and grain | references/shot-types-and-integration.md |
| Shot breakdown, status tracking, QC | references/breakdown-template.md |
Open at most two per step.

## 5. Workflow
1. Triage the take: what is wrong, what is good, which frames matter (frozen-frame review, first, middle, last, plus motion).
2. Choose the rung from section 1; write a one-line fix plan per shot in the breakdown.
3. Prepare plates: conform to the project fps, size and a 10-bit intermediate (ProRes) if compositing more than once (H). Export image sequences only when a tool needs them.
4. Do the work (cleanup, matte, comp), then match light, colour, grain, blur (shot-types-and-integration.md section 5).
5. Review at 100 percent, in motion, and at phone size; compare with the neighbouring shots in context.
6. Deliver plate versions (clean, comp, matte, notes) to the editor; keep a before and after pair.
7. Colour and grain are finalised by the colorist after lock; do not bake a heavy look in the comp.

## 6. Quick recipes (ffmpeg verified on 9.0.1, 2026-10-14)
- Key and place an element: `ffmpeg -i bg.mp4 -i fg_green.mp4 -filter_complex "[1:v]chromakey=0x00ff00:0.15:0.05,despill=type=green:mix=0.5[k];[0:v][k]overlay" out.mp4`.
- Alpha from a mask video: `alphamerge` (colour plus grey matte) into ProRes 4444 or FFV1 (`-pix_fmt yuva444p10le`).
- Fake shutter or soften steppy motion: `minterpolate=fps=96:mi_mode=blend,tmix=frames=4,fps=24`.
- Stabilise a hybrid plate: `vidstabdetect` then `vidstabtransform` (present in this build).
- More: compositing-basics-and-tools.md section 6.

## 7. Outputs
In `C:/Claude Code/company/creative/<client>/<project>/vfx/`: vfx-breakdown.md, per-shot clean plate, comp, matte, notes and before and after stills, log.md entries with credits.

## 8. Related skills
`higgsfield-master`, `photoreal-humans`, `asian-human-reference`, `cinematography`, `color-grading`, `film-studio`, `edit-director`, `graphics-rendering`.

## 9. Report format (8 lines max)
Shots fixed of total, method rung used per shot, credits spent versus quote, matching checks done (light, grain, blur), open risks (consent, licence, resolution), files, what needs the user's yes.
