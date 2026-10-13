# Shot production at scale (Phase 3)

Real-world scale evidence (3P, vendor and press, unaudited): a 95-minute AI feature (Hell Grind) was made by about 15 people in about 14 days; generation in 15 s segments, typically 3 to 4 kept from every 20 generated; one big action sequence used 4,000 to 5,000 generations, later quiet scenes a dozen or two; prompts averaged about 3,000 words with the style and voice description repeated; an "editing director" owned the master file because several directors generated in parallel. A separate 75-minute AI film was reported at about 2,000 USD and three months (3P, contested claims). Plan with the model in SKILL.md section 4, not with press headlines.

## 1. Batching
- Work one sequence at a time, one scene at a time inside it, one location per batch (the plate is loaded once).
- Order inside a scene: hardest shot first (hands, crowd, motion), then masters, then singles, then inserts and cutaways.
- Batch size: 10 to 20 shots per approval round; proofs at 720p on the cheapest capable tier, then finals once.
- Parallel lanes (several agents or chats) only on different scenes, never on the same scene; one editing owner holds the master timeline.
- fullstack-engineer keeps a manifest (CSV or JSON) per sequence: `shot_id, prompt_file, refs[], model, resolution, seconds, status, take, credits, job_id`. Tools read the manifest; no hand-typed settings.
- Every job logged in `log.md` (creative-studio section 8). Quote first, wait for the yes (SKILL.md section 5).

## 2. Prompt structure per shot (assembled by tooling, not retyped)
`[STYLE HEADER] + [LOCATION block] + [CHARACTER blocks, front-loaded] + [WARDROBE ids] + [ACTION one beat] + [CAMERA: size, lens, one move with numbers] + [LIGHT and grade words from bible] + [DIALOGUE with voice profile] + [NEGATIVES]`
Order: subject, action, setting, camera, light, constraints (higgsfield-master golden rules 3 and 4). Seedance dialect for narrative shots, 60 to 100 words per shot excluding the shared headers (model-dialects.md). Long prompt headers are fine if they are stable text blocks; per-shot text stays short.

## 3. Reference chaining
1. Anchors: character sheets, location plates, prop sheets, style frames (bibles-and-continuity.md). Up to 50 references per generation on Seedance 2.5 or Cinema Studio 4.0, up to 9 images on Seedance 2.0, 3 on Veo 3.1 (3P, verify on the tool).
2. Shot start frame = approved board frame for the shot, or last frame of the previous approved take inside the same scene.
3. Master shot first; singles generated from the master frame or the same plates so light matches.
4. For a new angle of the same moment, use the plate plus character references, and the master as a style reference.
5. Do not chain more than 3 to 4 generations without re-anchoring on the reference set (compounding drift).
6. Records: for each shot keep the start frame file, reference list and end frame file in `03_shots/.../refs/`.

## 4. Last-frame continuation
- Export the last frame (not the last 0.2 s, which often blurs): `ffmpeg -sseof -0.1 -i in.mp4 -frames:v 1 -q:v 2 last.png` (or `-vf "select=eq(n\,N)"` for an exact frame).
- Compare last frame of N with first frame of N+1 side by side (qa-tester): face, hair, wardrobe, props, light, position.
- If the clip ended with motion blur, take the previous sharp frame and trim the clip in the edit.
- Clips under 30 s; chain by cuts where possible: continuity by cutting beats continuity by extension.
- Extension tools (Veo scene extension chaining many clips, 3P) are good for one-take effects, risky for long scenes; prefer separate shots plus cuts.

## 5. Per-sequence locks
Before generating sequence N: locks for characters, locations, wardrobe, props, style header, grade LUT, voice profiles, model version (bibles-and-continuity.md section 10).
During: no edits to bibles; changes go through a change note.
After: qa-tester signs the sequence (G3), fullstack-engineer freezes the lock file and archives final prompts and settings, creative-director picks selects.
Model update mid-film (the platform changes weekly, 3P): finish the sequence on the old version, test the new one on 3 hard shots against the style frames before adopting; never mix versions inside a scene.

## 6. Folder structure
Root `C:/Claude Code/company/creative/<client>/<film>/` (use "internal" as client when none; never another client's brand):
```
00_dev/        logline, treatment, beat sheet, screenplay, budget, legal checklist
01_bibles/     style, characters, world, locations, wardrobe, props, voices, refs/
02_previs/     boards/S##-SC##/, animatic/, shot_list.csv
03_shots/S##/SC##/   SH###/  prompt.txt  refs/  T01.mp4 T02.mp4 ... approved.mp4  last.png  notes.md
04_audio/      dialogue/, foley/, ambience/, score/, stems/, mix/, temp/
05_edit/       conform/, proxies/, assembly_v##/, lock/, grade/ (LUTs), subtitles/
06_delivery/   master/, youtube/, ott/, festival/, dcp/, trailer/, press/
ledgers/       continuity S##.csv, take_ledger.csv, credits.csv, consents/, music_licences/
locks/         S##.lock.md
log.md
```
Never delete takes until the film is delivered and archived; keep approved plus the last two rejects per shot for repair.

## 7. Take ledger (`ledgers/take_ledger.csv`)
`shot_id, take, model, res, secs, credits, job_id, verdict (keep/repair/reject), defect tag, fix tried, note`
Defect tags: face, hand, limb, morph, physics, prop, wardrobe, light, text, lipsync, audio, speed, camera, other. Review counts monthly: a tag over 30 percent of rejects means fix the prompt or reference, not the dice.

## 8. Retake policy
1. Score the take with the creative-studio scorecard; 85 or higher and no critical fail = keep.
2. One defect (a single bad hand, one flicker): repair with video-to-video, Genjutsu or Object Swap, or reroll once.
3. Two to three defects: change ONE variable (reference, camera word, duration) and retry; log the variable.
4. Four of four bad takes: rewrite the prompt or restage (simpler action, new angle, cutaway); do not keep rolling.
5. Cap per shot: 6 takes at proof, 3 at final; at the cap escalate to the creative-director to cut, reframe or replace with an insert. Hero shots: cap 12.
6. Budget guard: if a sequence burns over 125 percent of its quote, stop and re-quote with the user.
7. Edit around problems: shorter shot, crop-in (check resolution headroom), reaction cutaway, speed ramp only if scripted.
8. Never fix identity by wording alone; use reference images.

## 9. Repair toolbox (3P tool names, confirm availability)
Video-to-video edit (Seedance edit, Kling Omni Edit), Genjutsu Object Swap (props, outfits), Motion Transfer (copy a real performance onto a character), Lipsync Studio, Seedream or Flux Kontext on a single frame then re-animate, upscale and frame interpolation last. Each pass can soften detail: check skin and line quality after edits. Keep one real anchor in VFX.

## 10. Production rhythm for a 90 minute feature (E)
Weeks 1 to 2 calibration sequence (pick the hardest and an easy one, measure burn and keep rate); weeks 3 to 10 one sequence per 3 to 5 working days with parallel lanes; QA and sequence rough cuts as each locks; weeks 9 to 12 audio and dubbing overlap with the last sequences. Total compressed schedules are possible with more agents (press reports 14 days for a human team of 15, 3P), but QA and the user's approvals are the bottleneck: schedule approval windows.

## 11. Daily checklist (product-analyst)
Credits spent versus quote; shots approved versus planned; open repairs; sequences blocked on references; contingency left; next approval needed from the user.
