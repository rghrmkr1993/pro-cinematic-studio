# Humanise in post (ffmpeg recipes)

Labels: F standard practice or documented, E starting point to adjust by ear. Recipes were run on test tones with ffmpeg 9.0.1 and all executed without error; the values are untested on real Tamil speech, so listen and adjust. Mixing theory, ducking and loudness live in `${CLAUDE_PLUGIN_ROOT}/skills/music-and-sound/references/mixing-and-mastering.md` and `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/sound-music-voice.md` section 8; the two-pass loudnorm is in `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/editing-and-assembly.md` section 4. Do not repeat them here.

Principle (E): a human voice lives in a space, breathes, and sits in a mix. A dry, perfectly clean, evenly loud AI voice sounds fake. Keep dry stems, then add the space last. Work at 48 kHz, 24-bit WAV (F, film-studio standard). Keep every original take.

## 1. Order of operations
1. Select and splice takes (section 2).
2. Trim and de-click.
3. Clean: high-pass, EQ, de-ess, light compression.
4. Add space: subtle reverb matched to the scene, plus room tone under everything.
5. Add breath and mouth detail where a line lacks it.
6. Mix under music and effects.
7. Measure loudness; deliver stems and the mix.

## 2. Take selection and splicing
- Generate 3 to 5 takes per hero line (seed or setting changes), 1 to 2 for the rest.
- Choose per phrase, not per line: take the best opening of take 2 and the best landing of take 4.
- Cut at a breath or a zero crossing, never mid-word; match pitch at the join.
- Crossfade 20 to 40 ms:
```
ffmpeg -i a.wav -i b.wav -filter_complex "[0:a][1:a]acrossfade=d=0.03:c1=tri:c2=tri[o]" -map "[o]" splice.wav
```
- Keep natural gaps: lines under 300 ms of silence on cuts feel rushed unless scripted; pauses of 250 to 600 ms between ideas read as thought (E).
- Trim leading and trailing silence, keep 80 to 150 ms head and 150 to 300 ms tail for room:
```
ffmpeg -i in.wav -af "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse" trim.wav
```
- Find silence gaps to check pacing: `ffmpeg -i in.wav -af silencedetect=noise=-45dB:d=0.25 -f null -`

## 3. Pace and pitch micro-variation (E)
Even pace is a tell. Nudge phrases by a few percent in different directions; time-stretch with `atempo` (0.5 to 2.0, keep within 0.92 to 1.08):
```
ffmpeg -i line.wav -af "atempo=0.96" slow.wav
```
Do not pitch-shift more than about 1 percent; larger moves sound processed. Never stretch the whole file the same amount.

## 4. Clean: EQ, de-ess, compress
```
ffmpeg -i vo.wav -af "highpass=f=70,deesser=i=0.4:m=0.5:f=0.5,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=4500:t=q:w=1:g=1.5,acompressor=threshold=0.1:ratio=2.5:attack=15:release=120:makeup=1.5" clean.wav
```
- High-pass at 70 to 90 Hz removes rumble. A dip of 1 to 3 dB at 200 to 300 Hz removes boxiness; a gentle lift at 3 to 5 kHz adds presence (E).
- De-ess if sibilants hiss; Tamil has fewer harsh sibilants than English, so go light (E).
- Compression 2:1 to 3:1, gain reduction 2 to 4 dB; do not flatten the dynamics you chose.
- Metallic or ringing TTS artifact: a narrow cut with `equalizer=f=<freq>:t=q:w=8:g=-4` after locating it by ear, or regenerate.

## 5. Room tone (always)
A voice with true digital silence between lines sounds pasted in. Lay a continuous bed under the whole scene (F, film-studio section 4).
```
ffmpeg -i clean.wav -f lavfi -i "anoisesrc=color=pink:amplitude=0.003:r=48000" -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:weights=1 1:normalize=0[o]" -map "[o]" room.wav
```
Better: use a real 20 to 30 s room tone from the recording space or a library, looped with crossfades. Level: about 50 to 60 dB under the voice peaks, audible only when the voice pauses (E).

## 6. Subtle reverb matched to the scene
Blend 10 to 25 percent wet, short decay, rolled off highs. Small room: 20 to 80 ms pre-delay and short echo; bigger space: more wet. Wet signal must not smear consonants.
```
ffmpeg -i clean.wav -filter_complex "[0:a]asplit[d][w];[w]aecho=0.8:0.85:35|60:0.22|0.12,lowpass=f=6000[wet];[d][wet]amix=inputs=2:weights=1 0.25:normalize=0[o]" -map "[o]" room_verb.wav
```
For convincing space use an impulse response with `afir` (room or hall IR, licensed or self-recorded) instead of `aecho`. Match the space to the picture: a kitchen is small and bright, a temple hall is long and dark, a car is dead and close, a phone call is band-limited.
Phone call: `-af "highpass=f=300,lowpass=f=3400"`. Outdoors: no reverb, add ambience (sound-design-and-foley.md in music-and-sound).

## 7. Breath and mouth detail
Real speakers breathe before phrases, and lips and tongue click softly. Many TTS voices drop these.
- Record or license 10 to 20 breath samples (inhale, soft exhale, small lip noise) from a consented speaker or a royalty-free library; keep at about -24 to -30 dB under the voice.
- Place an inhale 150 to 400 ms before a long phrase or after a pause of 0.5 s or more; skip it on rapid lines.
```
ffmpeg -i room.wav -i breath.wav -filter_complex "[1:a]volume=-24dB,adelay=1500|1500[b];[0:a][b]amix=inputs=2:duration=first:normalize=0[o]" -map "[o]" with_breath.wav
```
(`adelay` is milliseconds from the start; repeat for each breath or use a DAW.)
- Do not layer a breath over the same TTS-generated breath; remove duplicates.
- Never record breaths from a real person without their consent (voice-ethics.md).

## 8. Mix under music
Dialogue first, music ducked 3 to 6 dB while speech plays (F, film-studio section 7).
```
ffmpeg -i music.wav -i voice.wav -filter_complex "[0:a]volume=-14dB[m];[1:a]asplit[v][sc];[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[d];[d][v]amix=inputs=2:normalize=0[o]" -map "[o]" mix.wav
```
Roll off music below 200 Hz and cut 1 to 3 kHz by 2 to 3 dB under voice to keep Tamil consonants clear. Check on phone speaker, earbuds, laptop.

## 9. Loudness and delivery
Web voiceover is often mastered about -16 LUFS integrated, true peak -1.5 dBTP (E, check the platform spec in sound-music-voice.md section 8). One-pass quick check, then use the two-pass recipe for finals:
```
ffmpeg -i mix.wav -af "loudnorm=I=-16:TP=-1.5:LRA=7" -ar 48000 final.wav
```
Re-measure after final encode (F). Export stems: dialogue, music, effects (M and E for dubbing).

## 10. Humanising failure fixes
| Symptom | Fix |
|---|---|
| Sounds like a studio-less robot | Room tone plus 15 to 20 percent reverb |
| Too much echo, mushy consonants | Cut wet to 10 percent, low-pass the wet, shorten decay |
| Every line same loudness | Level by phrase (volume automation), 1 to 3 dB variation by emotion |
| Harsh digital top end | Low-pass at 12 to 14 kHz or a 2 dB shelf cut above 8 kHz |
| Clicks at splices | Longer crossfade, cut at zero crossing |
| Breaths sound pasted | Lower to -30 dB, vary samples, align to phrase starts |
| Voice buried by music | Duck 5 to 6 dB, EQ notch, move music to side |

## 11. QA before delivery
Listen on three devices; run the naturalness checklist (SKILL.md section 4); verify no clipping, loudness measured, silence gaps checked, breaths not duplicated, native speaker sign-off.
