# Editing and assembly (Phase 4)

Recipes below were run on ffmpeg 9.0.1 (Windows build) on 2026-10-14 with synthetic test clips. Filter option lists were checked with `ffmpeg -h filter=<name>`. Re-run on your build before delivery. Owner: fullstack-engineer assembles; creative-director approves cuts; qa-tester checks sync and loudness.

## 1. Cut grammar (craft)
- Cut on action or on a change of attention (a look, a sound). Motivated cuts only.
- Match cut: same shape, motion or position across a cut (a spinning fan to a turning wheel) to bridge time or theme. Graphic match for montage.
- Jump cut: deliberate, for stress or time compression; otherwise change angle more than 30 degrees and size one step.
- J-cut: next scene's audio starts before its picture; L-cut: current audio continues over the next picture. Use for dialogue, scene transitions and to hide AI picture seams.
- Smash cut: abrupt tonal contrast. Cutaway and insert: hide drift and set rhythm.
- Cross-cut: parallel action, equalise tempo of both lines as the climax nears.
- Rules of space: 180-degree line, eyeline match, screen-direction continuity, 30-degree rule.
- Dissolves for time passing, fades to black for act endings only; avoid effect transitions (wipes, spins) in drama.
- Hold on faces after a line lands; start scenes late, leave early.
- Cut on the dialogue's breath, not on the AI clip's boundary.

## 2. Pacing per genre (E, ASL = average shot length)
| Genre | ASL | Notes |
|---|---|---|
| Photoreal drama | 6 to 9 s | long dialogue masters, reaction shots, slow push-ins |
| Animated feature | 4 to 7 s | gag timing, music-driven montages, held emotional beats |
| Anime | 3 to 6 s | held frames, limited motion, impact frames |
| Action, sci-fi, fantasy epic | 2 to 5 s | geography clarity first; wide establishing, then close |
| Documentary style | 6 to 12 s | interview holds with b-roll cutaways |
| Music film | 2 to 4 s, follows tempo | cut on downbeat or phrase; beat map first |
| Horror, thriller | alternate 2 s and 10 s | quiet holds build dread |
Shape per feature: 3 to 5 pacing peaks, and a quiet scene after every big set piece. Cut each sequence to its target duration from the animatic.

## 3. Assembly workflow
1. Conform: normalise every approved take to one spec (resolution, fps 24, pixel format, audio 48 kHz). Mixed sources (various models) must be transcoded to a house intermediate: `ffmpeg -i in.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,fps=24,format=yuv420p" -c:v libx264 -crf 12 -c:a pcm_s24le -ar 48000 conform/SH020.mov`.
2. Rough cut per sequence from the animatic order; replace boards with approved takes by shot ID.
3. Fine cut: trim handles, add J and L cuts, reaction inserts, speed changes (only scripted).
4. Sequence rough cuts to the editing owner; full assembly; picture lock (G4). After lock no picture changes without a change note; sound and grade follow lock.
5. Keep an EDL-like CSV (`shot_id, in, out, track, transition, note`) as the source of truth, and generate ffmpeg commands from it. For manual cutting, use a GUI editor (DaVinci Resolve or similar) when judgement is needed; use ffmpeg for conform, assembly, exports and checks.

## 4. ffmpeg recipes (verified 2026-10-14)
Concat without re-encode (identical codecs, size, fps, timebase):
```
printf "file 'a.mp4'\nfile 'b.mp4'\n" > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy out.mp4
```
Cross-dissolve video and audio (xfade offset = clip1 duration minus transition duration; both clips need the same size, fps, timebase and pixel format):
```
ffmpeg -i a.mp4 -i b.mp4 -filter_complex "[0:v][1:v]xfade=transition=fade:duration=1:offset=3[v];[0:a][1:a]acrossfade=d=1[a]" -map "[v]" -map "[a]" -c:v libx264 -pix_fmt yuv420p -c:a aac out.mp4
```
Other xfade names (build lists them with `ffmpeg -h filter=xfade`): fadeblack, fadewhite, dissolve, wipeleft, slideleft, circleopen, smoothleft, radial and more. For chains of many clips, offset accumulates (offset_n = sum of durations so far minus sum of transitions so far); generate commands by script.
J-cut (picture of clip b starts at 3 s, its audio starts 1 s earlier; build the audio on its own timeline with adelay in milliseconds, per channel):
```
ffmpeg -i a.mp4 -i b.mp4 -filter_complex "[0:v]trim=0:3,setpts=PTS-STARTPTS[v0];[1:v]trim=0:3,setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0[v];[1:a]atrim=0:3,asetpts=PTS-STARTPTS,adelay=2000|2000[a]" -map "[v]" -map "[a]" -c:v libx264 -c:a aac jcut.mp4
```
(For real films cut audio and picture on separate tracks in a multitrack mix, then render; adelay moves a whole stem.)
Audio mix from stems (levels in linear gain or dB; sidechain ducking of music under dialogue):
```
ffmpeg -i dlg.wav -i music.wav -i amb.wav -filter_complex "[1:a]volume=-12dB[m];[2:a]volume=-20dB[b];[m][0:a]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400[md];[0:a][md][b]amix=inputs=3:normalize=0:duration=longest[mix]" -map "[mix]" -c:a pcm_s24le mix.wav
```
Check sidechaincompress and amix with `ffmpeg -h filter=<name>` for your build; a DAW mix is preferred for the final.
Loudness normalise, two-pass (loudnorm options: I, TP, LRA, measured_I, measured_TP, measured_LRA, measured_thresh, offset, linear, print_format):
```
ffmpeg -hide_banner -i master.mov -af loudnorm=I=-24:TP=-2:LRA=11:print_format=json -f null -
ffmpeg -i master.mov -af "loudnorm=I=-24:TP=-2:LRA=11:measured_I=<x>:measured_TP=<x>:measured_LRA=<x>:measured_thresh=<x>:offset=<x>:linear=true" -c:v copy -c:a aac -b:a 320k out.mp4
```
Targets by destination: sound-music-voice.md section 8. Note loudnorm resamples to 192 kHz internally; add `-ar 48000` after the filter.
Subtitles:
```
# burn in (hard sub); style uses ASS fields; &H colours are BGR
ffmpeg -i in.mp4 -vf "subtitles=s.srt:force_style='FontName=Arial,FontSize=22,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=2,MarginV=40'" -c:v libx264 -pix_fmt yuv420p -c:a copy burn.mp4
# soft sub in MP4 (mov_text) or MKV (srt), language tagged
ffmpeg -i in.mp4 -i s.srt -map 0 -map 1 -c copy -c:s mov_text -metadata:s:s:0 language=eng soft.mp4
ffmpeg -i in.mp4 -i s.srt -map 0 -map 1 -c copy -metadata:s:s:0 language=eng soft.mkv
# convert SRT to WebVTT
ffmpeg -i s.srt s.vtt
```
For Indic scripts burn-in, set `FontName` to an installed font with the script (Noto Sans Tamil, Noto Sans Devanagari, Noto Sans Telugu, Noto Sans Malayalam, Noto Sans Kannada, Noto Sans Bengali) and pass `fontsdir=` if needed. Verify shaping (conjuncts) visually; if broken, render subtitles to PNG or use a libass build with HarfBuzz.
LUT apply (.cube 3D LUT; `lut3d=file=...:interp=tetrahedral`; convert colour space first if the LUT expects log or Rec.709):
```
ffmpeg -i in.mp4 -vf "lut3d=file=look.cube:interp=tetrahedral" -c:v libx264 -pix_fmt yuv420p -c:a copy graded.mp4
```
Colour space tags on export: `-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv` for SDR web.
Resize and frame to DCP container (Flat 1998x1080) and fps:
```
ffmpeg -i in.mp4 -vf "scale=1998:1080:force_original_aspect_ratio=decrease,pad=1998:1080:-1:-1,fps=24" -c:v libx264 -pix_fmt yuv420p out.mp4
```
Last frame: `ffmpeg -sseof -0.1 -i in.mp4 -frames:v 1 -q:v 2 last.png`.
Proxies for review: `-vf scale=1280:-2 -crf 23` and keep names equal to shot IDs.
Black and silence detection for QC: `ffmpeg -i f.mp4 -vf blackdetect=d=0.1:pix_th=0.10 -af silencedetect=n=-50dB:d=2 -f null -`.

## 5. Colour pipeline and LUTs
- Source reality: AI clips are 8-bit sRGB or Rec.709 with baked contrast; no true log, so deep grading is limited (E). Plan a restrained grade: shot matching, contrast, one look LUT, film grain and halation for unity.
- Order: conform to Rec.709 (SDR) at 24 fps, shot match per scene (exposure, white balance, saturation), sequence look, then film LUT, then grain, then export. Grade in a tool with scopes (DaVinci Resolve); ffmpeg for batch LUT application.
- LUT: a `.cube` file (size 17, 33 or 65). A creative LUT designed for Rec.709 input only; do not stack two creative LUTs. Keep LUT ids in the lock file.
- Mixed models: grade each model's clips to the style frames first, then unify; give each model a corrective LUT.
- Era looks: 35 mm print, 16 mm, 8 mm, VHS, early colour (Technicolor-like), bleach bypass, via grade plus grain plus gate weave; do not rely on the generator to hold the era grade.
- HDR is optional: AI clips are SDR; inverse tone-mapping gives fake HDR, so deliver SDR unless the platform demands it.
- Deliver a flat QC copy and the graded copy; check on a calibrated display.

## 6. QC checks before G4
Duration equals the EDL, no black frames, no frozen frames, A/V sync at 0, 50 and 100 percent (clap or beep test in leader), loudness in range, true peak under the ceiling, subtitles timed to picture, credits spelled and in the right order, temp music removed, safe margins for subtitles (bottom 8 percent).
