---
name: cinematography
description: "Frame rates in depth: temporal resolution, 180-degree shutter, fps by content type for India and the US, HFR history, slow-motion speeds, conform rules, 50 Hz flicker, AI model output fps, interpolation, and the edit timeline rule. Part of the cinematography skill."
---

# Frame rates, deep guide
Labels: (V) vendor-official, (3P) third-party, (K) craft, (H) house rule. Researched and verified 2026-10-14. Short version lives in `exposure-and-settings.md`.

## Fundamentals
- Frame rate is temporal resolution: how many still moments per second the viewer gets. More frames means smoother motion and less strobing; fewer means each frame carries more blur and the motion reads as "film" (K).
- 180-degree shutter: exposure time is half the frame time, 1/48 s at 24 fps, 1/50 s at 25. It gives motion blur that reads natural. Narrower shutter (90 degrees) gives crisp, staccato action; wider smears (K, 3P DIY Photography).
- Shutter angle = 360 x fps x exposure time. 1/50 s at 24 fps is 172.8 degrees (3P Indie Cinema Academy).
- The "film look" is a bundle: 24 fps cadence, 180-degree blur, shallow depth, grain, grade. Viewers learned the 24 fps cadence over a century, so higher rates read as "video" or "soap opera" even when the image is better (3P AVS Forum, SVC). Rate alone does not make a shot cinematic (K).
- AI models do not take fps as a setting; they imitate cadence and blur from the prompt and the training video (see AI section).

## fps by content type
| Content | Shoot and deliver | Notes |
|---|---|---|
| Feature film, cinema (global) | 24 (DCI) | The default. Shoot 23.976 only if the post chain is NTSC-timed. [no India-specific theatrical spec found 2026-10-14; checked: broadcast format lists, Peach India spec; 24 is the global DCI norm] |
| Indian theatrical | 24 | Same as above; confirm with the DCP vendor. |
| OTT, India and global | Native rate of the shoot: 23.976, 24 or 25 | Netflix requires the native capture rate, no pulldown, accepts 23.976 to 60 progressive (V Netflix Partner Help via 3P summaries). Never speed 24 to 25. |
| TV, India | 25p or 1080i25 (50 fields), PAL | Delivery spec lists 1080/50i at 25 fps (3P Peach India spec). 24p played on PAL runs 4.16 percent fast. Shoot 25 and avoid 50 Hz flicker. |
| TV, US | 29.97 (30000/1001), 23.976 for film-like drama | NTSC family. |
| Documentary | 24 or 25 as the broadcaster asks; 50 or 60 for actuality that needs slow-down | Keep one rate per project. |
| Sports | 50 or 60 (India 50, US 59.94), 120 and 240 for replays | Crisp motion, less blur. |
| Music video | 24 for a film feel; 25 or 30 for social cuts; 120 for performance slow-mo | Match the platform cut. |
| Ads | 24 or 25 for film look; 30 for social-first | One master rate, then conform. |
| YouTube | Upload at the recorded rate: 24, 25, 30, 48, 50, 60 are all fine (V YouTube Help) | Deinterlace first. Higher-rate bitrate tier above 30 fps. |
| Instagram Reels and Shorts | 30 (accepts 24 to 60; 30 is the standard, 3P guides) | 1080x1920. Meta help pages not read; confirm. |
| Gaming capture | 60 | Interface and motion read best at 60. |
| Animation, western | 24 on ones (24 drawings) for fast action, on twos (12) for most movement | Mix ones and twos per beat (3P). |
| Anime | Played at 24; drawn mostly on twos (12) or threes (8), back to ones for fast action | Pulled down to 30 for old NTSC broadcast (3P). |
| Stop motion | 12 to 15 captures per second on ones, or 24 on twos | Digital capture at 12 to 15 gives the twos look; conform to 24, 25 or 30 (3P Stop Motion Magazine). Forum claims about Aardman and Laika are anecdotal. |
| HFR cinema | 48, 60, 120 | See next section. |

## HFR cases and reaction
- The Hobbit, 48 fps, 2012: many viewers called it distracting and "soap opera", too real, sets looked like sets. Some liked the clarity. Explained as conditioning to 24 (3P High-Def Digest, SVC, AVS Forum).
- Billy Lynn (2016) and Gemini Man (2019), Ang Lee, 120 fps: split reaction. Critics compared the look to video games or soap opera; some found the extra rate helped action and 3D, and worst for static dialogue. Most home releases are 24 or 60 versions (3P Wikipedia list, AVS Forum).
- Lesson (H): HFR suits action, sport and immersive formats; it hurts drama, skin and period work. Do not ask for "HFR" for a premium brand film.

## Slow motion
- Slow factor = shoot fps / playback fps. 120 shot, 24 played = 5x slower; 240 / 24 = 10x (K).
- Keep the 180-degree shutter at the shoot rate (1/240 at 120) and add light, because exposure per frame drops (K).
| Moment | Shoot | Why |
|---|---|---|
| Hair flip, fabric, dupatta | 60 to 120 | 2.5x to 5x lets motion float without looking frozen |
| Water splash, droplets, powder | 120 to 240 | Fast detail needs 5x to 10x |
| Product pour, cream, oil, serum | 120 (240 for a thin liquid) | Viscous pours look rich at 5x |
| Fight, impact | 60 to 120 for flow, 240 for a single hit | Ramp in and out; keep most of the fight at speed |
| Walk, hero reveal | 48 to 60 | Gentle 2x float |
- Speed ramp: shoot 120 or more, then ramp 100 to 20 percent speed in the edit.

## Mixed-rate pitfalls and conform
- Never mix 23.976, 24, 25 and 30 on one timeline without a decision. Pick the timeline rate once, conform everything to it (H).
- 24 to 25: speeds picture 4 percent and raises audio pitch unless pitch-corrected. 24 to 30 needs cadence; 23.976 to 29.97 uses 3:2 pulldown, and Netflix forbids pulldown flags (V).
- Same rate with a 0.1 percent offset (24 vs 23.976) drifts audio over long cuts; conform with a rate change, not a stretch.
- Convert rate by dropping or duplicating frames for graphics; use optical flow only for slow motion, and check hands and edges.
- Timecode, captions and music must be timed to the final rate.

## Flicker on 50 Hz mains (India)
- Mains lights flicker at 100 Hz. A flicker-safe shutter is an integer multiple of the flicker period: 1/50 and 1/100 are safe; 1/48 is not (3P Urban Video, toolsforfilm).
- At 24 fps, 1/50 is 172.8 degrees, 1/100 is 86.4 degrees. At 25 fps the normal 180 degrees is already 1/50, so shoot 25 for Indian TV and web with practicals.
- Rule holds for tungsten, tubes and HMI. LED fixtures, cheap bulbs and PWM-dimmed lights can flicker at other frequencies: test on a monitor, try clear-scan or nearby shutter values, dim through the fixture not PWM, or swap the tube (3P).
- LED walls and volume panels: scan rate and refresh produce banding or rolling bars with the wrong shutter. Sync the camera (genlock) or pick a shutter that matches the panel scan, and test before the day (K, no single vendor source read; confirm with the wall vendor).
- Screens in frame (phones, TVs, monitors) need a clear-scan setting or a test; do not trust the eye.

## AI video specifics
Verified 2026-10-14. Rates are what the clip file contains; most tools expose no fps control.
| Model | Output fps | Settable? | Source |
|---|---|---|---|
| Seedance 2.0 | 24 | No fps parameter found | BytePlus LAS docs list 24 fps (V) |
| Seedance 2.5 | 24 fixed, 4 to 30 s, 480p to 1080p | No | Sogni docs, BytePlus listing (3P and V) |
| Kling 3.0 | Not stated in Kling pages. Resellers claim 24, 30 or 60; one fal Standard test measured 24 | Unconfirmed | [no official fps as of 2026-10-14; checked: kling.ai quickstart, Kling API doc (client-rendered), Cliprise, Curious Refuge, aijustdropped]. Run ffprobe on a real clip |
| Veo 3.1 | 24 | No, no fps parameter; 4, 6 or 8 s, 720p, 1080p, 4K | Gemini API docs (V) |
| Higgsfield Cinema Studio 4.0 | 24 (API billing assumes 24 fps) | No fps control; Higgsfield prompts write "24fps" in text | open.higgsfield.ai pricing note, Seedance 2.5 guide (V) |
| MiniMax H3 | 24, up to 2K, 4 to 15 s | No | Morphic and Artificial Analysis (3P); API reference silent |
| Runway Gen-4.5 | 24 or 25 | Yes, Advanced settings | Runway help center (V, via search; page blocks fetch) |
- Slow motion vs real-time: write the playback result, not the capture rate. Slow: "slow motion, 120 fps look, each droplet sharp, played at 24 fps" (Higgsfield's own guide uses "120fps deep slow motion played at 24fps"). Real-time: "real-time 24fps, normal motion blur, no slow motion, no speed ramps" (V Higgsfield Seedance 2.5 guide). Keep one speed per shot.
- Use the tool's speed ramps (Cinema Studio 3.0 has Slow-mo, Bullet Time, Impact) when you want a controlled ramp (V).
- Interpolation: models give 24 fps. For a 25, 30 or 60 deliverable, interpolate; for a ramp, interpolate before slowing.
  - Tools: RIFE via Flowframes (free, fast), Topaz Chronos (stable linear motion, about 4x), Apollo (handheld, organic motion), Aion (beyond 8x) (3P Topaz docs, unifab); Higgsfield's FLUX 3 Video Upscaler goes to 4K 60 fps (V). Topaz's own guide recommends Chronos Fast for 24 or 25 to 60.
  - When: slow motion, 60 fps social, smoothing a pan. When not: a locked-down real-time shot at 24; it adds the "soap" look.
  - AI clips already have flicker and morph, which interpolation magnifies. Test a short segment and check hands, edges, text and fine texture frame by frame.
- Edit timeline rule: set the timeline once, conform everything. In edit-director put it in the EDL canvas (`"canvas": {"w", "h", "fps"}`, 9:16 default 30) and let `frame_interp: "flow"` retime sources that differ. With ffmpeg: `ffmpeg -i in.mp4 -vf fps=25 out.mp4` for plain conform, `-vf "minterpolate=fps=60:mi_mode=mci"` for interpolation, and `ffprobe -v error -select_streams v -show_entries stream=r_frame_rate,avg_frame_rate -of csv=p=0 in.mp4` to check every source first (variable fps from phones is common).

## Crew default rule (one line)
Shoot, generate and edit at the delivery rate (24 cinema, OTT and ads; 25 Indian TV and web with practicals; 30 Reels), 180-degree shutter (1/50 on 50 Hz mains), set the edit timeline fps once, and ffprobe every clip before conforming.
