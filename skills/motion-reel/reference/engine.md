# Engine code (route A: zero dependencies) - PROVEN on Windows 11, Node 22, ffmpeg 9, Python 3.14

Full working files live in `reference/proven/` (copy them into a project: `lib/motion.js` <- motion.js, `lib/browser.mjs` <- browser.mjs, `index.html` <- index.template.html). Layout of a project: `index.html`, `lib/motion.js`, `lib/browser.mjs`, `render.mjs`, `gen-cues.mjs`, `cues.json`, `sfx.mjs`, `beats.py`, `mix.mjs`, `critique.mjs`, `verify.mjs`, `package.json`, `CLAUDE.md`. `npm run all` = clean, render, cues, beats, mix, critique, verify.

## Hard-won rules (each cost a debugging round)
1. Canvas context MUST be `getContext('2d', { willReadFrequently: true })`. Without it Chrome flips between GPU and CPU raster mid-run and text antialiasing changes: 787 of 3600 subframes differed between two passes and the MP4 hash changed. Also call `g.reset()` at the top of `draw()`.
2. `lib/motion.js` must be a classic UMD script (`<script src="lib/motion.js">`, exposes `window.Motion`). `import` of a local file from file:// is blocked by Chrome CORS. It must define `clamp` and `spring` itself.
3. Grab frames with `canvas.toDataURL('image/png')` inside `page.evaluate` (about 16 fps), not `locator.screenshot()` (about 5.6 fps).
4. Quantise fast-changing numbers with `tq = x => Math.floor(x*60 + 1e-6)/60` (tmix averages the 4 subframes ending at each frame, so every subframe of frame k must give the same digit) or the counter ghosts.
5. Guard clipped rise-in text with `if (t < tin) return;` and use an exit offset larger than the glyph height, or slivers show at t=0 and at the end of exits.
6. Playwright may want a chromium revision you do not have: `lib/browser.mjs` falls back to any `%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe`.

## index.html skeleton (seek renderer)
```html
<style>html,body{margin:0;background:#141413}canvas{display:block}</style>
<canvas id="c" width="1080" height="1920"></canvas>
<script src="lib/motion.js"></script>
<script>
const { clamp, ramp, eio, eo, lerp, spring, rng, track, swapAlpha } = Motion;
const W = 1080, H = 1920, DUR = 15;
const g = document.getElementById('c').getContext('2d', { willReadFrequently: true });
function draw(t) {
  g.reset();                                   // no leaked 2D state between frames
  g.fillStyle = '#141413'; g.fillRect(0, 0, W, H);
  // scene1(t); scene2(t); ... each scene is a pure function of t; guard with if (t < from || t >= to) return;
}
window.seek = (t) => { draw(t); return true; };
if (!navigator.webdriver) {                    // live preview only outside headless
  const t0 = performance.now();
  (function loop() { draw(((performance.now() - t0) / 1000) % DUR); requestAnimationFrame(loop); })();
}
</script>
```
Loop: make the last frame equal the first (resting shape at the same position, velocity 0). Verified seam PSNR 62 dB.

## lib/motion.js (classic UMD)
```js
(function (root) {
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const ramp = (t, a, b) => clamp((t - a) / (b - a));
  const eio = (x) => (x < 0.5 ? 4*x*x*x : 1 - Math.pow(-2*x + 2, 3) / 2);
  const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);
  function spring(t, k = 170, d = 26) { if (t <= 0) return 0; const w0 = Math.sqrt(k), z = d / (2*w0);
    if (z < 1) { const wd = w0*Math.sqrt(1 - z*z); return 1 - Math.exp(-z*w0*t)*(Math.cos(wd*t) + (z*w0/wd)*Math.sin(wd*t)); }
    return 1 - Math.exp(-w0*t)*(1 + w0*t); }
  function rng(seed) { /* mulberry32, see proven/motion.js */ }
  function track(t, keys, k = 170, d = 26) { let v = keys[0][1];   // keys: [[time, value], ...]
    for (let i = 1; i < keys.length; i++) v += (keys[i][1] - keys[i-1][1]) * spring(t - keys[i][0], k, d); return v; }
  function indicator(t, stops, width = 120) { const lead = track(t, stops, 320, 30), trail = track(t, stops, 140, 22);
    return { left: Math.min(lead, trail), right: Math.max(lead, trail) + width }; }
  function swapAlpha(t, tIn, tOut) { return Math.min(clamp((t - tIn - 0.08)/0.12), clamp((tOut - 0.1 - t)/0.1)); }
  const loopT = (t, dur) => ((t % dur) + dur) % dur, lerp = (a, b, x) => a + (b - a)*x;
  const M = { clamp, ramp, eio, eo, lerp, spring, rng, track, indicator, swapAlpha, loopT };
  root.Motion = M; if (typeof module !== 'undefined') module.exports = M;
})(typeof globalThis !== 'undefined' ? globalThis : this);
```
Spring presets: snappy (k 320 d 30) buttons/toggles; default (170/26) cards, camera; heavy (140/22) big type, logos; critical `d = 2*sqrt(k)` for type (no overshoot); playful (visible overshoot) mascots.
Container morph: sum of springs per key on cx, cy, w, h, r and fill mix; scale inner content by `min(w/finalW, h/finalH)` so a morphing card never shows an empty frame.

## render.mjs  (`node render.mjs --fps 60 --dur 15 --sub 4 [--from s] [--out file]`)
See `proven/render.mjs`. Key lines:
```js
import { launch } from './lib/browser.mjs';
await page.goto(pathToFileURL(resolve('index.html')).href);            // never 'file://' + cwd on Windows
const vf = `tmix=frames=${SUB},select='eq(mod(n\\,${SUB})\\,${SUB - 1})',setpts=N/${FPS}/TB`;   // spawn args array, no shell
const ff = spawn('ffmpeg', ['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS*SUB),'-i','-','-vf',vf,'-r',String(FPS),
  '-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-fflags','+bitexact','-flags:v','+bitexact','-map_metadata','-1','-movflags','+faststart',OUT],
  { stdio: ['pipe','inherit','inherit'] });
ff.stdin.on('error', (e) => { ffErr = e; });                           // EPIPE if ffmpeg dies
const b64 = await page.evaluate((t) => { window.seek(t); return document.getElementById('c').toDataURL('image/png').slice(22); }, t);
if (!ff.stdin.write(Buffer.from(b64, 'base64'))) await new Promise((r) => ff.stdin.once('drain', r));
```
Determinism check: `certutil -hashfile out\silent.mp4 MD5` after two renders (byte-identical once rule 1 is applied); `node verify.mjs` does it automatically and also checks loudness, true peak, duration and loop seam.

## beats.py  (`python beats.py out/music.wav > beats.json`)
librosa 1.0.0 installs on Python 3.14. `proven/beats.py` falls back to a pure-numpy onset/autocorrelation tracker if librosa is missing or `NO_LIBROSA=1` (tested: 119.7 bpm on the 120 BPM bed). librosa `beat_track` is phase-ambiguous (it locked on offbeat hats); trust `bpm` and `hits`. State changes go on `beats`, big moments on `downbeats`, SFX on `hits`.

## sfx.mjs + gen-cues.mjs  (`node gen-cues.mjs && node sfx.mjs cues.json out/sfx.wav`)
cues `[{t, type, gain, bus}]`; voices click, pop, thump, whoosh, kick, hat, bass; bus `fx` -> out/sfx.wav, bus `music` -> out/music.wav (120 BPM kick/hat/bass bed). 16-bit mono 48 kHz. Keep visual event times and cue times in one head: edit index.html and gen-cues.mjs together.

## mix.mjs  (`node mix.mjs`)
`[1:a][2:a]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.5:level=false`, then two-pass loudnorm (`I=-14:TP=-1.5:LRA=11`, measured values, `linear=true`), AAC 192k. The limiter is required: sparse SFX otherwise land near -15.4 LUFS. Result -14.4 LUFS, -1.3 dBTP, audio 14.997 s vs video 15.000 s.

## Critique commands (`node critique.mjs [stripAtSeconds]`)
Runs with spawn args (no shell quoting). Note `-update 1` on single-image outputs.
```
ffmpeg -i out/final.mp4 -vf "fps=2,scale=270:-1,tile=6x5" -frames:v 1 -update 1 out/contact.png
ffmpeg -ss 4.1 -i out/final.mp4 -vf "scale=320:-1,tile=12x1" -frames:v 1 -update 1 out/strip.png
ffmpeg -i out/final.mp4 -vf "fps=1,scale=360:-1,tile=5x3" -frames:v 1 -update 1 out/phone.png
ffmpeg -stream_loop 1 -i out/final.mp4 -c copy out/loop_check.mp4
ffmpeg -i out/_last.png -i out/_first.png -lavfi psnr -f null -        # loop seam, >40 dB invisible
```
Sizing for phone: nothing under 44 px on a 1080 canvas (about 15 px at 360 wide).

## Windows notes
Bahnschrift Condensed (display) and Segoe UI (UI) ship with Windows 11. `document.fonts.check()` returns true for any name: verify fonts by looking at a frame. Bash heredocs with many quotes/backslashes can fail: write files with the editor tool.

## Route B (frameworks)
Remotion: `npx create-video@latest launch-film`, `npx skills add remotion-dev/skills`, `npx remotion studio`, `npx remotion render Main out/launch.mp4`.
HyperFrames: `npx hyperframes init my-video`, `npx hyperframes skills update`, `npx hyperframes preview && npx hyperframes render`.
