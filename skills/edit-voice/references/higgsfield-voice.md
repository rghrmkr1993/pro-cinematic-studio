# Voice via Higgsfield: dubbing, voiceover, cloning, voice change

Everything here is paid. The order is always the same: free preparation → question with the price → explicit
"yes" → run → result into the project → check. The consent rules are in this skill's SKILL.md.

## Tools

| task | tool | price in advance |
|---|---|---|
| speech translation + synthesis + lip sync | `dubbing(params={video_id, target_language})` | **no** — charged after the fact |
| change the timbre, keeping the timing | `voice_change(params={video_id, voice_id, voice_type})` | **no** |
| clone a voice | `create_voice` (record/upload widget) or `create_voice_from_confirmed_audio(audio_media_id, name)` | **no**, charged on success |
| voice a text | `generate_audio(params={model, prompt, voice_id, voice_type})` | `get_cost: true` |
| list of voices | `list_voices` → `voice_id` + `voice_type` (`preset` or `element`), sample `preview_url` | free |
| balance and charges | `balance`, `transactions` | free |

Dubbing languages (18): eng, cmn, fra, hin, ita, jpn, kor, por, rus, tur, spa, deu, ara, pol, ind, fil, swe, fin
(mapping to the recognition codes: `ed_voice.HF_DUB_LANG`).

## Upload and download

- **Files made by the engine** (dub master, fragment, render): `media_upload(filename="dub_master.mp4")` →
  run the returned PUT command (curl) from the sandbox → `media_confirm(media_id=…, type="video")` → `media_id`.
- **The user's original file** that Higgsfield needs as is: `media_upload_widget(type="video")` — the user picks
  the file in the widget (remote tools cannot read chat attachments).
- **Result**: wait for the job (`jobs_wait` for batch jobs; for single ones, the tool's response), then download it
  from the result link: `curl -sSfL "<url>" -o $PROJ/voice/dub_en.mp4`.
If an upload or download fails, tell the user and ask for the file.

## Dubbing (lip sync, 18 languages)

1. **Dub master**: a render from the timeline of only the speech pieces with the **original voice, without music
   and SFX** (remove `music` and `sfx` from `audio`), H.264/AAC, the shortest span that covers the speech — the price
   and the lip-sync quality depend on the length. Faces are visible and not mirrored where the lips matter.
2. Question with the price: "dubbing 34 s into English and Spanish — the price can't be calculated in advance; it
   is charged after the fact; balance N credits. Without dubbing — subtitles in these languages. Shall I run it?"
3. After the "yes": upload the master → `dubbing` for each language → download.
4. **Bring it back into the project**: `ed_voice.import_dub(edl['audio'], 'dub_en.mp4', at=<output time of the master's start>)` —
   the dubbed voice goes into `audio.voice`; the original voice is removed (`mode='replace'`) or stays 15–18 dB lower
   (`mode='voiceover'`, interview style). Music and SFX stay as they were, ducked under the voice. Where the lips
   matter, take the picture of those pieces from the dub (the segment's `src` = the dub file). Signature: `import_dub(audio, dubbed, at=0.0, mode="replace", orig_gain_db=-16, gain_db=0, out_wav=None, duck_db=None)`.
5. Subtitles for the language version come from recognizing the **new** voice (`transcribe(dub, lang=…)`).
6. Preview → the user judges lip sync and sound; you check the numbers (loudness, subtitle timings).

## Languages outside the 18 — voiceover without lip sync

Translation (you) → phrase by phrase, `generate_audio` with a preset or cloned voice (`get_cost` for each phrase,
the total goes into the question) → the phrases go into `audio.voice` at the times of their chunks; if one does not
fit, speed it up to ×1.15 or re-edit the picture.
Warn honestly: the lips will not match. The default model is the one named in the `generate_audio` description;
another engine only on request (`models_explore(type='audio')`), which also shows which languages the model supports.
Check the voiceover model's language list in the model description (`models_explore`) before ordering.
`generate_audio` makes speech only: do not generate music or sound effects — the engine synthesizes SFX.

## Voice clone

- Only the user's own voice or the voice of a person who has explicitly agreed. We do not clone the voices of
  famous people.
- Recording: clean speech, 10 s – 3 min, no music. The `create_voice` widget records or uploads and creates the
  voice by itself; do not call `create_voice_from_confirmed_audio` again after the widget.
- The clone is ready when `list_voices` shows it with status `completed` and `is_audio_eligible`; do not voice
  anything with it before that. After that, use `voice_type: "element"` in `generate_audio` and `voice_change`.

## Voice change

`voice_change` keeps the timing and the picture and changes the timbre (preset or clone). Input: a video with the
voice; better without music (the same dub master), then mix the music and SFX with the engine.

## If a job fails

Report the reason from the tool's response; on a timeout do not resubmit — first check the status by `job_id`
(a retry may charge twice). Repeating a paid step again requires a "yes".
