---
name: motion-reel
description: "Make a product launch video, showreel, motion ad, animated explainer, kinetic type or UI-morph film rendered from code (deterministic seek(t) canvas + Playwright + ffmpeg, synthesized beat-synced sound, self-critique loop). Use for any video, reel, launch film or motion graphics request, even if the user never names this skill. Sources: 0xMovez course and ridark_eth article on Opus 5.5 motion studios (Sep/Oct 2026), proven on Windows 11."
---
Part of the cinematic pipeline: entry point creative-studio


# Motion reel (code-rendered video studio)

The prompt is 10% of the video, the harness is 90%. A model cannot emit an MP4: it writes a program, a headless browser draws every frame, ffmpeg encodes. Quality comes from a reference, a deterministic render engine, a beat grid, and a critique loop where the model LOOKS at its own frames. Default failure is always: no reference, no engine, no self-review.

Files: `reference/proven/` (tested working studio, START HERE), `reference/engine.md` (explained engine code), `reference/prompts.md` (templates). Tested studio folder: `C:\Claude Code\motion-studio` (`npm run all` = render, cues, mix, critique).

## Token budget pre-flight (MANDATORY on every video request)
Before spawning any agent or rendering, reply with a short estimate and wait for the user's go (or a changed plan). Format:
`Video plan: [duration, formats, tier]. Estimated usage: ~X to Y tokens total (main ~a, agents ~b), ~N critique rounds, ~M min wall time. Biggest cost drivers: [...]. Cheaper option: [...]. Go?`
Tiers (calibrated on the measured test film: first build from scratch plus 3 critique rounds used about 290k agent tokens, about 40 min; the other benchmark, a 45 s hand-painted film, used 62.7M tokens, 96% cache reads, 163 calls; all numbers are ESTIMATES, state them as such and re-quote if scope changes):
- Light (template reuse, 10 to 15 s, one format, synthesized sound, 3 critique rounds): about 150k to 350k tokens, 30 to 60 min.
- Standard brand film (20 to 30 s, URL asset capture, 3 formats, voice-free): about 400k to 1M tokens, 1 to 2 h.
- Heavy (45 to 60 s, custom character/mascot, generated base footage via Higgsfield, ElevenLabs voice, 5+ rounds): about 2M to 8M tokens plus generation credits, 3 to 6 h.
- Flagship overnight (2 min+, multi-chapter, parallel subagents): 20M to 60M+ tokens; quote the range and offer a staged plan with a stop after the animatic.
Adjust up for: no reference supplied, many UI screens to capture, extra formats (+15% each), voice/mascot (+30%), opus final review (+10%). Adjust down for: reusing the same brand session (about -30%), preview-only renders.
Always also list non-token costs (Higgsfield/ElevenLabs credits, render time) and what the user can cut to save limits. After delivery, report actual usage versus the estimate in one line (use the agents' reported usage) so future estimates improve; save any large miss to memory.

## Operating protocol (best result, lowest token cost)
1. Intake in ONE message from the user's plain request: product + URL, duration, formats, reference, music, metric, CTA. Fill gaps with defaults (20s, 9:16 first, synthesized 120 BPM, one accent). Ask only for true blockers (URL, logo, approval for spend).
2. Never rewrite the engine. Copy `motion-studio` to a new project folder and change only scenes, assets, cues. Do not re-read engine.md unless something breaks.
3. Cheap loops: iterate with `--dur 5 --sub 1` previews, re-render only affected seconds, full `--sub 4` render only for the final. Look at sheets (contact/strip/phone) instead of playing video.
4. Models: ui-designer sonnet (style guide, shotlist, 3 storyboard variants), fullstack-engineer sonnet (scenes, render, audio), qa-tester sonnet (checks and scores). Opus only for the final critique of a flagship piece or launch film. Haiku for asset gathering and repetitive re-renders. Reuse a running agent via SendMessage rather than spawning cold.
5. One session/project per brand so renderer, synth and export pipeline are reused (second video is faster).
6. Agent reports: scores table, file paths, hashes, open issues, under 150 words.
7. Deliver: out/final.mp4 (every requested format), loop_check.mp4, poster.png, contact.png, README, plus one line on what to improve next. Never publish or send anything without the user's yes.

## Setup (already done on this machine, 2026-10-06)
Node 22, ffmpeg 9, Python 3.14 with numpy/librosa 1.0/soundfile, Playwright chromium (if it wants a revision that is not installed, launch with `executablePath` of the installed one). Effort: medium for small fixes, xhigh for new films, max for launch pieces. Optional: `npx skills add remotion-dev/skills`, `npx skills add heygen-com/hyperframes`, plugin `claude-animation` (buildwithhanif). Name a framework explicitly only when reuse (series, data-driven) needs it; Opus defaults to zero-dependency route A and writes magic-number code, so ask for named constants and lib/motion.js when maintainability matters.

## Render contract (also the project CLAUDE.md)
- Film = pure function of time: `window.seek(t)` paints frame t. No CSS transitions, timers, rAF in render mode, no carried state. Seeded noise (mulberry32), never Math.random.
- H.264 yuv420p CRF 16, 60 fps, 4 subframes blended for motion blur.
- Banned: centered title on gradient, everything fading in, corner labels, frame borders, glow on UI chrome, generic particle bursts, bouncy easing, dead time.
- One display face, one UI face, one accent. New thing every 2 to 4 s. Hook in first 2 s.
- Closed-form springs only; multi-target values = sum of one spring per change (`track()`). Presets: snappy 320/30, default 170/26, heavy 140/22, playful with visible overshoot. Tiny overshoot on UI, none on type.
- Sound synthesized in code unless a track is supplied; hits on measured beat grid; -14 LUFS.
- Real product UI only (Playwright screenshots, real logo, colours, fonts into ./assets). Never invent screens. Keys in `.env` by variable name, never in a prompt.
- Layout function, not hard-coded pixels, so 9:16, 1:1, 16:9 render from one timeline; reframe type and UI per format, never crop 16:9 to vertical.

## Pipeline
1. Assets from the URL. 2. Reference: ffmpeg frame every 0.5 s, write `docs/style_guide.md` (palette hex, type, shot lengths, transitions, camera, grain, text entry/exit); take grammar, never content. A named style beats adjectives (sources: whatships.com, Dribbble motion, competitor launch films, client archive). 3. Three storyboard variants + one still per scene before animating; notes in camera words ("slow every zoom to 0.7x"); first render is about 80%. 4. Music: measure with beats.py or synthesize. 5. `docs/shotlist.md` on the beat grid. 6. Build scenes. 7. Critique loop. 8. Final render, mix, deliver.

## Critique loop (mandatory, minimum 3 rounds)
Make contact sheet (2 fps, 6 across), strip around fast actions, phone sheet (360 px), loop check. View them with Read. Score 1-10: hook in 2 s, phone readability, motion quality, variety, composition, brand accuracy, sound sync. Log in docs/review_log.md, fix the 3 worst, re-render only affected seconds, repeat until ALL 8+. Lesson from the test film: it stalled at 7 on hook, phone, composition, brand after 2 rounds. Work on: first 2 s impact, bigger type for 360 px, balanced composition, no empty frames (an unfilled card at 11.5 s is a defect), counters quantised to the 60 fps frame.
Hunt for: text overlap during swaps, sliding instead of easing, blurry scaled text (no will-change on camera-scaled elements), dead beats, loop-seam stutter (last frame = first, cursor position and velocity included).

## Windows-proven corrections (override engine.md where they differ)
1. lib/motion.js is a classic global/UMD script, not `export` (file:// blocks modules); define spring and clamp inside.
2. Capture with `page.evaluate(t => { seek(t); return canvas.toDataURL('image/png').slice(22) })` and decode base64 (3x faster than locator.screenshot). Use pathToFileURL, handle stdin error/drain, ffmpeg `-fflags +bitexact -map_metadata -1` for byte-identical output.
3. Loudness: `alimiter=limit=0.5` before two-pass loudnorm (single pass landed -15.4 LUFS).
4. `-update 1` on single-image ffmpeg outputs.
5. librosa beat phase can lock onto offbeats: trust `bpm` and `hits`.
6. Counters: `const tq = x => Math.ceil(x*60 - 1e-6)/60` to stop ghosting under subframe blending.
7. Create the 2D context with `getContext('2d',{willReadFrequently:true})`: without it Chrome flips canvas between GPU and CPU raster mid-run, text antialiasing changes and two renders stop matching (this broke determinism once).
8. Hash on Windows: `certutil -hashfile out\silent.mp4 MD5` (two renders must match; measured byte-identical).
Test film final: all 7 scores 8 after 3 rounds, silent.mp4 MD5 identical on 2 full renders, -14.4 LUFS, -1.3 dBTP, loop 62.5 dB. Weakest area: tile captions read about 15 px at 360 px width, go bigger. beats.py has a numpy fallback (`NO_LIBROSA=1`).
Measured: 15 s render takes about 70 to 110 s; final -14.4 LUFS; loop seam 63 dB PSNR.

## Patterns by job
- Showreel one-liner ("dynamic 15-second motion graphics video that shows what an incredible motion designer you are, like a showreel for a resume, go all out") is only a smoke test; hundreds of identical prompts produce look-alike reels ("brief contagion"). Always add reference, real brand, state list.
- Brand film: URL + "use actual product screenshot, logo, assets" + "must have music" replaced a $1,000+ agency video in under 30 min. Beats: 5-word hook, UI assembles, 3 features with a cursor doing real actions, one proof number, logo + CTA.
- UI morph spec (XML: inputs, direction, structure on 120 BPM, build, gotchas): one container never cuts, morphs size/radius/fill across 8 to 12 states, cursor drives every change, last frame = first. Write the state list, not the vibe.
- Overnight director's brief (about 9,500 chars): logline, references, tools+keys+budget, character bible, beat sheet, on-screen text rules, gates (plan, rig, stills, animatic, full, polish, audio, render), critique loop, deliverables. One subagent per chapter after writing `ANIMATION_GUIDE.md` and `STORYBOARD.md`.
- Generate-then-trace: video model (Seedance via Higgsfield) renders base shots, code redraws on top so only the code layer shows: motion you cannot hand-code plus an ownable style.
- Voice/mascot: ElevenLabs key by `.env` name; character with identity lock.

## Cost and pricing anchors
Watercolor 45 s short: 62.7M tokens (96% cache reads), 163 model calls, about $34 API list, about 6.75 h (1.5 h hands-on), 12 min laptop render: budget iteration, not one-shots. Agency launch video was about $1,000+; here 30 to 45 min agent time for a 20 to 40 s film plus critique rounds. Productised offer: music, mascot in any style, product features, closing offer, any language, up to 3 edits. For the user's India clients quote in INR and cap scope at 3 edits. Benchmarks: Steve Jobs film (about 8.7k lines, 23 transitions, 3,570 frames in under 5 min), "Small print" (one index.html, no image assets).

## Repos
JohnHeibel/PDoomVideo, JohnHeibel/ClaudeAnimationBase, buildwithhanif/claude-animation-skill, heygen-com/hyperframes, remotion.dev/docs/ai/skills, WinterArc21/Battle-of-Austerlitz-Film, guanmo-ai/awesome-ai-motion, athemeroy/awesome-opus-5-5-videos.
