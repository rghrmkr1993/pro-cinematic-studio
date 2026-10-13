# Previs, storyboard and animatic (Phase 2)

Planning is cheaper than fixing: a board frame costs cents, a rejected 30 s clip costs dollars (Higgsfield vendor figures: Popcorn 8 frames about 5 credits, a 30 s 720p Cinema Studio clip about 210 credits, 2026-10-13, 3P). Owner: creative-director, with tech-writer keeping the shot list and fullstack-engineer building the animatic.

## 1. Terms
- Story reel (animation): boards cut to temp voice and music to test story, then redrawn. Animatic: timed boards with sound, shot-length accurate. Previs: rough 3D or AI-motion version of action and camera. Layout: locked staging and camera per shot before final animation or generation. In AI films the animatic plus 720p proof clips play the role of previs and layout.
- Animated features run story reel to animatic to layout; photoreal films run boards to previs for action sequences only.

## 2. Shot list format (one row per intended shot)
Columns: id, scene, location id, characters on screen, wardrobe id, shot size (ECU, CU, MCU, MS, MWS, WS, EWS), angle (eye, low, high, dutch, OTS, POV), lens mm and aperture, camera move (static, push-in, pull-out, pan, tilt, track, orbit, crane, handheld; one move per shot, one direction), subject action (one), dialogue line id, intended length (s), start frame source (new, last frame of ID), end frame target, transition out (cut, dissolve, match cut, smash), sound note, model, risk (hands, crowd, text, fast action), status.
Coverage plan per dialogue scene: master (WS), two singles (MCU), OTS pair, insert, reaction, cutaway. Cover each action scene with: establishing, action wide, action close, reaction, insert, exit.
Camera craft vocabulary: use the `cinematography` skill, and higgsfield-master visual-language.md and signature-shots.md.

## 3. Shot-length budget
Target average shot length (ASL, estimate): drama 6 to 9 s, animation 4 to 7 s, action 2 to 4 s, documentary style 6 to 12 s, music film 2 to 4 s (follows tempo). Feature of 90 min at ASL 6 s is 900 shots. Mark which shots are generated from scratch and which are reused (establishing and plate shots) to estimate cost.

## 4. Storyboard via image models
1. Per scene, upload character sheet, location plate and prop (up to four references for Popcorn type tools, 3P) and write the scene arc in 3 to 5 sentences with the style header.
2. Generate a 4, 6 or 8 frame sequence per scene as one generation so face, light and space carry across frames (Popcorn type tool, or Nano Banana, Seedream with references). Auto coverage first, manual placement of key beats second.
3. Fix with edits (Kontext, Seedream, Nano Banana Pro) rather than regenerating the set.
4. Save as `02_previs/boards/S03-SC07/SH020.png`, name = shot ID. Add a one-line caption: action, camera, dialogue ref.
5. Board approval: creative-director checks story clarity, eyelines, screen direction and the 180-degree line.
6. Text in frames: do not bake; arrows and notes go in overlay layers.
Style frames: before boards, produce 6 to 12 look frames and lock the style bible.
Non-image option: thumbnail sketches by hand for action; photograph them as references.

## 5. Animatic assembly (fullstack-engineer)
Inputs: board images per shot ID, shot list lengths, temp dialogue (TTS or scratch voice), temp music, ambience.
Steps:
1. Build a CSV `id,image,seconds` from the shot list.
2. Make one clip per board with `-loop 1 -t <sec>` (recipe below), same size and fps as the final.
3. Concat the clips, mix the temp audio, burn a timecode and shot ID overlay (drawtext).
4. Review: runtime within 5 percent of target; every scene readable without dialogue; pacing curve (long shots after fast ones); cut or merge dull shots now.
5. Re-time the shot list from the animatic; shot lengths in the list become generation targets (add 1 to 2 s handles per clip for cutting).
Recipes (verified on ffmpeg 9.0.1, 2026-10-14):
```
ffmpeg -loop 1 -framerate 24 -t 4.5 -i SH020.png -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,format=yuv420p" -c:v libx264 -r 24 SH020.mp4
ffmpeg -f concat -safe 0 -i list.txt -c copy animatic_noaudio.mp4
ffmpeg -i animatic_noaudio.mp4 -i temp_mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -shortest animatic_v01.mp4
ffmpeg -i animatic_v01.mp4 -vf "drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='%{pts\:hms}':x=20:y=20:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.5" -c:a copy animatic_tc.mp4
```
On Windows `fontfile` is needed (no default fontconfig; colon escaped as `C\:/`), on Linux point it to a TTF path. Concat with `-c copy` requires identical codec, size, fps and timebase; otherwise re-encode.
Animatic versions: `v01, v02`, with a change list; the approved animatic is the G2 evidence and the runtime contract.

## 6. Previs for action and complex camera (only where needed)
- Block the action as a low-cost proof: one 720p clip per beat with the cheapest capable model, or a simple 3D blockout in Blender or a game engine if geometry must be exact (graphics-rendering skill for lighting and engine choice).
- Words cannot pin geometry: draw a layout map (top-down) and attach it as a reference; use start and end frames to pin poses.
- Record camera path as numbers (start distance, end distance, speed, height) in the shot list.
- Use proofs to decide which shots become montage, silhouette or cutaway.

## 7. Voice and sound in the animatic
Scratch dialogue with a TTS voice per character (sound-music-voice.md) so timing is real; temp music from licensed or library tracks marked TEMP in the file name; never ship temp tracks, log them for replacement.

## 8. Gate G2 checklist
Boards for every scene; shot list complete; animatic approved with runtime; risk shots flagged; cost quote computed from the shot list (shot count x takes x credits per take, SKILL.md section 4); consent and IP checks clean; the user's yes on the quote.

## 9. Anti-patterns
Starting generation before boards. One giant prompt per scene. Boards that skip reaction and insert shots. Ignoring screen direction. Shots with three simultaneous hard problems (crowd, hands, text): split them.
