# Speech recognition

Local and free, the `ed_voice` module of the edit-director engine: Whisper (int8 ONNX) on onnxruntime, a voice
activity detector (VAD) and a CTC forced aligner for word times (~1 frame at 30 fps on clean speech) — no torch and
no pip.

```bash
python3 -I $ED/engine/edit.py transcribe SRC $PROJ/voice/words.json [--lang en]
python3 -I $ED/engine/edit.py voice transcribe SRC --out $PROJ/voice/words.json [--lang en] [--model auto|turbo|small|base|tiny|omni] \
        [--timing auto|ctc|dtw] [--prompt "names, terms"] [--text script.txt] [--srt subs.srt] [--srt-out out.srt] [--no-cache]
```
`transcribe(path, lang=None, model='auto', *, prompt=None, text=None, srt=None, timing='auto', cache=True)` →
`{"lang", "lang_prob", "model", "source": "asr|text|srt", "timing", "duration", "words": [{"w", "t0", "t1", "p",
("suspect")}], "segments", "speech", "warnings", "stats"}`; times are source seconds.
- `lang`: if not given, detected from the speech (confirm with the user). `model='omni'`: a language Whisper does
  not know (lowercase, no punctuation).
- `prompt`: names and terms (the user's product, people's names) — better spelling; `vocab` in a sequence spec does
  the same and joins split names for matching and captions.
- `text=` / `--text`: a known script or lyrics aligned to the audio; `srt=`: existing subtitles.
- Cached by the file's hash and the options: a repeat costs nothing.

## Models: downloaded on the first call

| model | download | on disk | RAM | quality |
|---|---|---|---|---|
| `turbo` (default) | ~560 MB | ~1 GB | ~1.7 GB | best, including Russian |
| `small` | ~640 MB | ~360 MB | ~1.0 GB | fallback |
| `base` / `tiny` | ~210 / ~120 MB | ~150 / ~100 MB | ~0.5 / ~0.4 GB | drafts; weak on Russian |

Cache: `~/.cache/edit-studio/asr` (or `$ED_VOICE_CACHE`); source: the model releases on GitHub. `model='auto'` falls
back along the chain turbo → small → base → tiny if the download or memory does not allow. Unpacking turbo on one
core takes about a minute; in the sandbox this repeats in every new session.
If the models cannot be downloaded, tell the user and offer: uploading the model archive as a file (instructions in
the `ed_voice` docstring), sending an existing text or subtitles (`text=`, `srt=`), or subtitles without word-level
precision.

## Procedure

1. Input: video or audio; the audio is extracted automatically; pauses and music without speech are not decoded
   (VAD).
2. Long material (an hour-long podcast): run it detached — `edit.py voice transcribe SRC --out
   $PROJ/voice/words.json --background` returns at once (log + job file next to `--out`); poll with
   `edit.py status $PROJ/voice`. A foreground run that outlives the tool's time limit is killed. The transcript is
   cached per file: the sequence planner and later runs reuse it.
3. Save `voice/words.json` in the project — it goes into the project archive (`edit-director/references/storage.md`).
4. Locate the user's quoted words: `python3 -I $ED/engine/edit.py voice phrase $PROJ/voice/words.json "…" --all`
   (case, punctuation and number format do not matter) and print the transcript line around each hit before using it
   as an in or out point (`references/speech-genres.md`, Word anchors).
A one-minute fragment transcribes in under a minute on 2 cores (about twice that on 1 core), plus the one-time model
download; tell the user before starting.

## Checking and correcting

- Words with a low `p` are error candidates. Fix what is obvious from context yourself, do not touch the timings,
  mark them `"fixed": true`. The user's names, brands and terms, and numbers — **do not guess**: a list of
  questionable spots with timecodes and a question. Re-running recognition with `prompt` (a list of names) is often
  better than manual fixes.
- Do not change the meaning: the transcript is the basis for the subtitles and for editing by words.
- You add punctuation and sentence boundaries when assembling the subtitles: a boundary is a pause ≥ 0.4 s plus
  meaning.
- If an existing text is available (script, song, the user's subtitles), it takes priority:
  `align_text(words, known_text, path=SRC)` places its words at the times in the audio; show the discrepancies.
- `task='translate'`: English text straight from the speech (into English only); for other languages, translate
  yourself.

## Several speakers

There is no voice diarization. On screen, `ed_reframe.active_speaker` decides per camera shot whose mouth moves
during each utterance (turns switch in the pause before the new speaker), and `speaker_crop` frames that face. Other
cues: the voice changing at pauses, the user's markup ("for the first 10 minutes it's me, then the guest"). Different speakers get a different subtitle
color or their name on a label.
