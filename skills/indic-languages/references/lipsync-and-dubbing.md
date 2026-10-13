# Lipsync and dubbing for Indian languages

Labels: F sourced (sources.md), 3P third party or vendor, E estimate or craft norm, U unverified. Snapshot 2026-10-14; tool pages change monthly. No generation was run for this file. Extends `film-studio/references/languages-and-localization.md` section 5 (OV master, dub list, M and E stem); do not repeat it. Credit gate: quote cost, get the user's yes before any paid lipsync or dub call.

## 1. Visemes and Indian phonemes (E, linguistic reasoning; test on footage)
- Lipsync models are audio-driven: they map sounds to mouth shapes, so the language is not a hard limit, but training data skews to English and Chinese (3P). Indic audio can produce plausible but loose mouths; check.
- What the lips show (visible): closure for bilabials, rounding for u o, spread for i e, open jaw for aa, lower lip to upper teeth for labiodentals.
- What the lips do not show: the tongue. Dental त, retroflex ट and alveolar sounds look the same on the face. Retroflex vs dental is therefore audio-only; you cannot lipsync it, but you must still keep it right in the audio (TTS and native review).
| Group | Sounds | Mouth shape | Note |
|---|---|---|---|
| Bilabial closure | p b m (Tamil ப, Hindi प ब म) and aspirated ph bh | Lips fully shut, then release | Aspirates add breath, not a new shape; closure is the sync anchor |
| Geminate bilabial | Malayalam മ്മ പ്പ, Tamil ப்ப, Telugu ప్ప | Closure held longer | About 4 to 6 frames at 25 fps instead of 2 to 3 (E); long vowels also hold the open shape |
| Labiodental | English f v; Hindi व is a soft ʋ; Tamil வ similar | Lower lip near upper teeth, weaker than English | Dub from English "v" to Hindi "व" and the lip touch softens; do not demand a hard bite |
| Rounded | u o ū ō, Hindi ओ | Rounded, forward | Dravidian short u is lighter than English "oo" |
| Spread | i ī e ē | Corners back | Short vs long is mainly duration |
| Open | a ā, ai | Jaw open | Hindi and Dravidian "a" is open and central |
| Retroflex, zha | ட ண ள ழ ற | Neutral lips, mild rounding for ழ | Invisible; no sync cost |
- Source English video with "w" and "th" mouths is the hardest to dub into Indic, because Indic audio lacks those shapes. Prefer source clips with a closed or open-vowel mouth at the cut.

## 2. Syllable rate and why Tamil and Telugu dubs run long
- Cross-language study of 7 languages: Japanese about 7.8 syllables per second, Spanish 7.8, English 6.2, Mandarin 5.2; languages that pack fewer meanings per syllable speak faster (F, Pellegrino et al. 2011). Hindi, Tamil, Telugu, Malayalam, Kannada were not in that study (F, by omission).
- E estimates, measure instead of trusting: Hindi 6.5 to 7.5 syllables per second, Tamil and Telugu 6 to 7.5, Malayalam up to 8 with geminate-heavy rolling speech (U).
- Why dubs run long: Dravidian languages are agglutinative (case, tense, politeness stack onto the word), nearly all syllables are open (CV), and verb-final order moves the key word to the end; a line that is 8 English syllables is often 12 to 16 in Tamil or Telugu (E). Formal written forms add more; spoken forms cut 15 to 25 percent (E).
- Measure: render a TTS test at pace 1.0 for each adapted line, read duration with ffprobe, and compare with the source shot. Target ratio within 0.9 to 1.1 of the English.

## 3. Script adaptation for timing
1. Isochrony: match phrase durations and the start and stop of speech, not syllable counts. Fit by phrase, not by whole line.
2. Anchor closures: if the shot is close and frontal, keep a p, b or m (or a geminate) at the frames where the source closes the lips; add or move a "ba", "ma", "pa" word at that point. Words like அம்மா, ப்ளீஸ், मम्मी, ಅಮ್ಮ and అమ్మ carry closures well.
3. Shorten: use the spoken register, drop honorific chains, use short loans ("OK", "time", "late"), drop repeated subjects (Indic pro-drop).
4. Verb-final order: put the pause where the English ended; do not stretch words.
5. Respect the face: on wide or back-turned shots, timing matters and lip shape does not; edit for rhythm only.
6. Cut away or reaction-shot the longest lines; film-studio rule: rewrite, or cut to a non-lip shot, rather than speeding audio past 1.1x.
7. Native review of each adapted line for meaning and politeness before any paid call.

## 4. Tools compared (language support is what the vendor states; Indic quality U until you test)
| Tool | Input | Language support | Strengths | Failure modes |
|---|---|---|---|---|
| Higgsfield Speak 2.0, Wan 2.5 Speak, Kling Avatars 2.0, Infinite Talk, Kling 2.6 Lipsync | One image plus audio or text | No published list; "multilingual, quality varies, test" (3P, vendor FAQ) | Fast; many models in Lipsync Studio; Infinite Talk and Kling Avatars for long clips | Weak on side profile and tiny faces (E); quality varies by language; model drift over long clips; confirm one speaker |
| Higgsfield Translate (video dubbing) | Source video | 18 languages (list not retrieved; an older post names Hindi among 10) (3P) | Re-locks lip per language | Tamil, Telugu, Malayalam, Kannada not confirmed (U) |
| ElevenLabs dubbing | Source audio or video | Tamil, Telugu, Kannada, Malayalam, Hindi listed in v1 and v2 (F, help centre via search); 90 plus languages | Speaker detection, transcript edit, per-clip regenerate; Studio limit 1 GB and 45 minutes, automatic dub 180 minutes | The help centre says dubbing does not include lip sync (3P, page may be old); translation is literal, so timing and register need a human edit; Tamil naturalness U |
| sync.so lipsync-2 and lipsync-2-pro | Video plus audio | Not specified (F); audio-driven | Pro: better teeth and detail; 512 px face; plans cap at 1 to 30 min | Extreme profile and still frames fail; occlusion needs a flag; timeouts on many cuts; non-human faces unsupported (F) |
| sync-3 (Higgsfield "Sync Lipsync 3") | Video plus audio | Not specified (F) | Profiles, over-the-shoulder, built-in occlusion, 4K output (F) | Very long, cut-heavy video still hard (F); fast speech and teeth not documented (U) |
| OmniHuman 1.5 (ByteDance) | One image plus audio, optional prompt | Audio "any language" (3P, vendor); prompt text only Chinese, English, Japanese, Korean, Spanish, Indonesian (3P) | Body, gesture and emotion from audio; good for talking portraits | Caps 30 to 60 seconds depending on host (3P conflict); character stills only; Indic accuracy U |
| Kling lipsync (video to video) and Kling 3.0 native audio | Video plus audio, or text | Five languages named for native lip sync: Chinese, English, Japanese, Korean, Spanish (3P); Indic by audio-driven route U | Strong English; audio up to 60 seconds against 2 to 10 second clips on fal (3P) | Indic mouths may follow English-like shapes (U); clips are short |
| VEED Fabric 1.0 and Lipsync v2 | Image plus audio; video plus audio | Audio any language (3P); dubbing 30 plus languages (3P) | Cheap; Fabric 480p or 720p, 10 MB limit; Lipsync v2 for forward-facing, one speaker | Side angles beyond medium close-up weak; durations conflict by host (3P) |
Best input for all: frontal or three-quarter face, mouth visible and well lit, one speaker per shot, no hand or microphone over the mouth, clean dry dialogue (no reverb, no music), 48 kHz WAV, shots 3 to 10 seconds.
Typical failure modes: teeth blur, double teeth or a "denture" look; fast or whispered speech dropping closures; side profile and head turns; beards and moustaches hiding the upper lip (common on Indian male characters, E); occlusion; faces under 15 percent of frame height (E).
Routing: Hindi and English, any tool; Dravidian languages, test sync-3 or lipsync-2-pro with the real audio on a 5 second clip first; ElevenLabs for translation plus voice, a lipsync tool afterwards. 3 test takes before committing; no paid run without the user's yes.

## 5. ffmpeg alignment (checked on ffmpeg 9.0.1 locally, 2026-10-14)
1. Probe: `ffprobe -v error -show_entries format=duration -of csv=p=0 vo.wav` and the same for the shot.
2. Conform audio: `ffmpeg -i vo.wav -ar 48000 -ac 1 vo48.wav`.
3. Fit within 0.9 to 1.1: `ffmpeg -i vo48.wav -af "atempo=0.95" fit.wav`. Beyond 1.15 it sounds artificial (E); rewrite instead.
4. Offset: `-af "adelay=120|120"` delays by 120 ms; trim with `-ss`. Pad to length: `-af "apad=whole_dur=5"`, then confirm the duration with ffprobe.
5. Conform picture: `ffmpeg -i in.mp4 -vf fps=25 -c:v libx264 -crf 16 -an v25.mp4`.
6. Mux: `ffmpeg -i v25.mp4 -i fit.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest out.mp4`.
7. Loudness is handled by the music-and-sound and film-studio rules, not here.

## 6. QA: frame-by-frame at 25 fps
- One frame is 40 ms. Detectability thresholds from ITU-R BT.1359-1: audio early by more than about 45 ms or late by more than about 125 ms is noticed (F, via search); acceptability +90 ms to -185 ms. EBU R37 is tighter, +40 and -60 ms; ATSC tighter still (3P). Target within one frame, never more than 2 frames early.
- Contact sheet of closures: `ffmpeg -i out.mp4 -vf "fps=25,scale=160:-1,tile=10x4" -frames:v 1 sheet.png`; then step with a player's frame advance on every p, b, m and geminate in close-ups. Find the audio position of the closure with `silencedetect` or a waveform and compare.
- Pass checklist: mouth starts and stops with the audio; every bilabial closure lands within 1 frame; no teeth ghosting; no mouth movement during silence; no jaw jitter; long vowels hold; consistent across a 3 to 10 second shot; native speaker watches with sound for naturalness.
- Score with the creative-studio master scorecard (85 drafts, 90 finals); fail goes back to script adaptation first, tool second.
