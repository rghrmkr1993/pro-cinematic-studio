# Scenario 3: adapting a finished edit with translation

A finished video → versions in other languages: subtitles in any language (free), voice — lip-sync dubbing
(18 languages) or synthesis without lip sync (all other languages), on-screen text — by replacing the layer or with
a cover box.

## 0. What kind of video

| video | on-screen text | voice |
|---|---|---|
| **built by our skill** (`edl_vN.json` exists) | a layer → translation = layer replacement, the edit does not change | dubbing or synthesis; our engine mixes the music and SFX |
| **someone else's, or no project** | burned into the picture → a cover box over it or a version without text | dub the whole video, or subtitles on top |

For someone else's video, create a wrapper project: an EDL with one segment for the whole video, `audio.copy: true` —
subtitles and cover boxes are then added as layers.

## 1. Speech and text

1. Transcript of the original → `voice/words.json` (`references/transcription.md`). In a music edit with no speech,
   skip this step.
2. On-screen text: in our video, the list of `layers`/`texts`; in someone else's, find the titles on a contact sheet
   (`ed_edl.py … --stills … --at 0:N:10`) and note the time and area of each.
3. You do the translation yourself: `ed_voice.translate_plan(chunks, target_lang)` → a table of chunks → your
   translation → `apply_translation(plan, texts)` (subtitle layers); on-screen titles — by replacing the text in
   their layers. Keep the meaning and length close to the original. Names, terms, the user's slogans — confirm them;
   show questionable spots as a list.

## 2. Voice

| need | how | price |
|---|---|---|
| a language from the 18 + matching lips | `dubbing(video_id, target_language)` | no cost preview → explicit "yes" |
| a language not on the list | voiceover of the translated text with `generate_audio` (own voice — a clone, otherwise a preset) over the picture, no lip sync | `get_cost` → "yes" |
| no voice needed | subtitles only | free |

Dubbing languages: eng, cmn, fra, hin, ita, jpn, kor, por, rus, tur, spa, deu, ara, pol, ind, fil, swe, fin.

**Our video and dubbing.** What gets dubbed is not the finished video with music but the **dub master**: the speech
pieces with the original voice, without music and SFX — cleaner translation, more accurate lip sync, cheaper. The dub
comes back into the project via `ed_voice.import_dub`: the new voice goes into `audio.voice`, the music and SFX are
our mix, and the picture of the talking pieces comes from the dub where the lips matter. Someone else's video is
dubbed whole (there is nothing to separate its voice from its music with).
Check the duration of the dub result against the input (`ffprobe`); if it does not match frame for frame, fit the
segments to the audio. Tool details, upload and download: `references/higgsfield-voice.md`.

## 3. Subtitles and on-screen text in the new version

- After dubbing or voiceover the word timings are different: recognize the **new** voice (`transcribe(lang=<language>)`)
  and build the subtitles from it; the subtitle text is your translation, aligned to the new words.
- Our video: layers with the translated text, same style; for longer languages, a smaller font size and 1–2 words
  per karaoke chunk.
- Someone else's video with burned-in text: a cover box over the text area (the frame's background color or a
  blur) + the translation on it; if a version without text exists, it is better. We do not touch third-party logos.
- Check font coverage for the language (Cyrillic, CJK, Arabic, Devanagari) — `references/subtitles.md`.

## 4. Versions and delivery

- A language version is a branch of the base one: `edl_v7.en.json` → `final_v7.en.mp4`; the base does not
  change.
- Several languages — one question about the paid part with the list of languages and the total, then one at a time.
- QA for each version: loudness, subtitle sync with the new voice (±1 frame), reading speed, text in the safe
  zone. The user judges lip sync and sound — ask them to watch the preview.
- Delivery: `/mnt/user-data/outputs/<project>_v7.<language>.mp4`; publishing — per
  `edit-director/references/publish.md`.
