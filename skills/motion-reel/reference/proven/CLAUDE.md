# motion-studio house rules

## Render contract
- Every film is a pure function of time: `window.seek(t)` paints frame t. No CSS transitions, setTimeout, requestAnimationFrame in render mode, no state between frames.
- Seeded noise only (`Motion.rng`, mulberry32). Never `Math.random`.
- Render with `node render.mjs`: H.264 yuv420p, CRF 16, 60 fps, 4 subframes blended (tmix) for motion blur.
- `lib/motion.js` is a classic script (UMD, `window.Motion`). Do NOT turn it into an ES module: `import` from file:// is blocked in Chrome.
- The 2D context MUST be `getContext('2d', { willReadFrequently: true })` (software raster) or renders are not deterministic. Quantise fast counters with `tq()` (floor to 1/60 s) so tmix blending does not ghost digits.
- A value with several targets = sum of one closed-form spring per change (`Motion.track`). Tiny overshoot on UI, none on type (`crit()`).

## Look
- Canvas 1080x1920, 15 s, loops: last frame equals first (resting dot at (122,1700)).
- One accent `#D97757` on `#141413`. One display face (Bahnschrift Condensed), one UI face (Segoe UI). One left edge (x=96).
- Banned: centered title on gradient, everything fading in, corner labels and frame borders, glow on UI chrome, generic particle bursts, bouncy easing, dead time.
- New visual event every 2 to 4 seconds. Hook in the first 2 seconds. Min text 44 px (readable at 360 px wide).
- Never redraw a real product UI from imagination: crop real screenshots. Real logo, colours, fonts. (This demo brand "kiln" is fictional.)

## Sound
- Synthesized in code (`gen-cues.mjs` -> `cues.json` -> `sfx.mjs`). Hits on the 120 BPM grid (0.5 s). Loudness -14 LUFS (two-pass loudnorm in `mix.mjs`).

## Workflow
1. Edit `index.html` and `gen-cues.mjs` together (visual event times = cue times).
2. `npm run all` (clean, render, cues, beats, mix, critique, verify) or the steps individually.
3. Look at `out/contact.png` and `out/phone.png`, score 1-10 on hook, phone readability, motion, variety, composition, brand accuracy, sound sync. Fix the 3 worst. Repeat until all 8+.
4. API keys live in `.env`, referenced by name only.
