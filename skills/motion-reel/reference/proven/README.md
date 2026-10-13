# motion-studio

15 s, 1080x1920, 60 fps looping film ("kiln", fictional brand) rendered from code: `index.html` exposes `window.seek(t)`, Playwright grabs frames, ffmpeg encodes (4 subframes blended for motion blur), sound is synthesized.

## One command from a clean state
```
npm install
npm run all     # clean (deletes out/) -> render -> cues -> beats -> mix -> critique -> verify
```
`verify` renders a second time and checks MD5 equality, -14 LUFS +/-1, true peak <= -1 dBTP, a/v duration, loop seam, and exits non-zero on failure. Takes about 6-7 minutes (two software-raster renders).

## Individual steps (from C:\Claude Code\motion-studio, PowerShell or Git Bash)
```
npm install                          # playwright only
pip install numpy librosa soundfile  # works on Python 3.14 (librosa 1.0.0)
npm run render:test                  # 5 s, sub 1 -> out/test.mp4
node render.mjs --dur 5 --sub 4 --out out/a.mp4
npm run render                       # 15 s, sub 4 -> out/silent.mp4 (+ .framehash), about 70-110 s
npm run cues                         # gen-cues.mjs -> cues.json -> out/sfx.wav + out/music.wav
npm run beats                        # beats.py on out/music.wav -> beats.json
npm run mix                          # amix + alimiter + 2-pass loudnorm -14 LUFS -> out/final.mp4
npm run critique                     # contact/strip/phone/poster/loop_check + loop seam PSNR (node critique.mjs 10.5 = strip at 10.5 s)
npm run verify                       # determinism + loudness + duration + seam
NO_LIBROSA=1 python beats.py out/music.wav   # force the numpy fallback (tested: 119.7 bpm)
certutil -hashfile out\silent.mp4 MD5
```
Edit visual event times in `index.html` and the matching times in `gen-cues.mjs` together.

## Determinism
`npm run verify` renders twice and compares MD5 of `silent.mp4` (last run: 153831e4574e7e2e5aaa0604710e97c9 both). render.mjs uses `-fflags +bitexact -map_metadata -1`.

## Windows gotchas found
- NONDETERMINISM: Chrome switches a canvas between GPU and CPU raster mid-run, changing text antialiasing (787 of 3600 subframes differed between two passes). `getContext('2d', { willReadFrequently: true })` forces software raster and made renders byte-identical. Also `g.reset()` at the top of draw().
- Playwright 1.63 wants chromium revision 1243 but only 1234 was installed: `lib/browser.mjs` falls back to any `%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win64\chrome.exe`. No download needed.
- `locator('#c').screenshot()` ran at 5.6 fps; `canvas.toDataURL('image/png')` inside `page.evaluate` runs at about 16 fps (3x faster) and is deterministic.
- `import` of lib/motion.js from file:// is blocked by Chrome CORS: lib/motion.js is a classic UMD script.
- Use `pathToFileURL(resolve('index.html'))`, not `'file://' + cwd` (backslashes, spaces).
- spawn ffmpeg with an args array (no shell): the select filter needs `\\,` in JS (becomes `\,`); no extra quoting. Listen to `ff.stdin.on('error')` (EPIPE) and wait for `drain`.
- ffmpeg image outputs need `-update 1` for single files, otherwise a pattern warning.
- `document.fonts.check()` returns true for any family; confirm fonts by looking at a frame. Bahnschrift Condensed and Segoe UI ship with Windows 11.
- Bash heredocs with many quotes/backslashes failed inside the tool; write files with the editor instead.
- librosa `beat_track` is phase-ambiguous: on this track it locked on the hats (offbeats) at 119.7 bpm. Trust `bpm` and `hits`, not beat phase.
- Quantise fast-changing numbers to the 60 fps frame (`tq`) so subframe blending does not ghost digits.
