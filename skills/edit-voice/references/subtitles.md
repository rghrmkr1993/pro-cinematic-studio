# Captions: presets, chunking, fonts, translation

Captions are `ed_text` layers of kind `subtitle` or `karaoke` in the timeline, built from the word timestamps by
`ed_voice.subtitle_chunks`. Sequence talk parts and speech-genre plans build them by themselves; this page is for
choosing the look, building them by hand and checking them.

## 1. Presets

| preset | kind | what it looks like | aliases | sibling (odd versions) |
|---|---|---|---|---|
| `podcast_bold` | subtitle | Talk-clip captions: heavy white sans, mixed case, thin outline + soft drop shadow, numbers and keywords in yellow, 1-2 lines in the lower middle, clean pop-in per chunk. | aura, podcast, bold, clip | podcast_caps |
| `podcast_caps` | subtitle | Punchy talk-clip captions: condensed black caps, outline + shadow, keywords in yellow, 1-2 short lines, pop-in per chunk. | caps | podcast_bold |
| `clean` | subtitle | Minimal interview captions: semibold white sans, hairline outline and a wide soft dark halo, lower placement, short fade in. | interview, minimal | boxed |
| `boxed` | subtitle | High-contrast captions on busy or bright footage: bold white text on a rounded dark plate per line, keywords in yellow, soft pop-in. | box, plate | clean |
| `karaoke_highlight` | karaoke | Word-by-word captions: 2-3 heavy caps words, the sounding word turns yellow, numbers in green, outline + shadow, pop-in per chunk. | karaoke, highlight, word | karaoke_box |
| `karaoke_box` | karaoke | Word-by-word captions with a yellow plate sliding under the sounding word (black text on it), bold mixed case, soft pop-in. | karaoke_plate | karaoke_highlight |

In a sequence spec: `"subtitles": "podcast_bold"` (or `"subtitle"` / `"karaoke"` / `null`, or `{"kind", "style",
"pos", "max_chars", "max_lines", "max_words", "pace": true}`); default = the house style's preset, else
`podcast_bold`. Plans: `edit.py plan … --subtitles karaoke|subtitle|none`, the look from the style. On odd versions a
style switches to the sibling preset. One accent colour per video; a key-word accent (numbers keep their unit: "4
million", "$10,000") at most once per chunk.

| the user says | preset |
|---|---|
| "normal subtitles", "clean" | `clean` (or `podcast_bold` for talk clips) |
| "bold podcast captions", "like the clip pages" | `podcast_bold` / `podcast_caps` |
| "word by word", "TikTok captions" | `karaoke_highlight` / `karaoke_box` |
| "captions on a box", "readable on a bright background" | `boxed` |
| "shorter lines" | the preset + `"max_chars"` (e.g. 18–22) |
| "no captions" | `null` (still offer an `.srt` for platforms with their own captions) |

## 2. Chunking: by phrase, around the cuts

`subtitle_chunks` splits the speech where a reader would: sentence and clause punctuation and real pauses are cheap
break points; a modifier stays with its noun ("four million dollars", "at home"), a name stays whole, a subject stays
with its verb, a line or chunk does not end on an article, preposition or conjunction, and the last word of a
sentence is not left alone for the next chunk (English word lists; punctuation and pauses work for any language).
Within that it keeps every chunk readable — ≤ 20 characters/s and ≥ 0.7 s on screen: a chunk takes time from the
pause after it, starts a little early, borrows from a neighbour, or merges; filler-only chunks join a neighbour or
stay unshown; ASR splits like "$10" ",000" are joined.

Cuts: **jump cuts and part ends are hard breaks** (`breaks`) — no chunk holds words from both sides or is shown
across one. **Camera cuts over continuous speech are soft** (`soft_breaks`): a chunk ends there when the phrase
allows, but a sentence may run across a camera cut rather than leave a too-short or too-fast chunk.

```python
words_out, inside = ed_voice.remap_words(words, edl['segments'], fps)      # source -> output time; inside = cuts in words
layers = ed_voice.subtitle_chunks(words_out, style='podcast_bold', canvas=(1080, 1920), fps=30,
                                  breaks=[jump_cut_times...], soft_breaks=[camera_cut_times...])
open(f'{PROJ}/voice/subs.srt', 'w').write(ed_voice.to_srt(layers))       # optional SRT for platforms
```
The command line does the same with hard breaks only:
```bash
python3 -I $ED/engine/edit.py voice subs WORDS --style podcast_bold --canvas 1080x1920 --breaks 4.2,9.75 \
    --out subs.json --srt subs.srt --ass subs.ass        # --kind, --max-chars, --max-lines, --horizontal, --fps
```
`--style` takes a preset name or alias (line length, line count and kind follow it); `--canvas` the output size
(default 1080x1920, `--horizontal` 1920x1080); `--breaks` the output seconds of jump cuts and part joins.

## 3. Fit: captions never shrink, never overflow

Lines are measured with the real font exactly as the renderer wraps them: `ed_text.text_fits(text, style, canvas)`
→ `{fits, lines, width_px, max_px, …}`, and `ed_text.caption_hints(name, ow, oh, text=transcript)` sizes
`max_chars` from the glyph widths of the actual words. With `fit: "reflow"` (default) every chunk keeps the
preset's size: it wraps to more lines up to the layer's `max_lines` (presets 3, karaoke 2); still too long, its time
span splits in two at a phrase point (after a sentence end or a comma, before a conjunction, never inside "4
million" or "at home"; both parts ≥ 0.7 s, inside the layer's own frames). Only a single word wider than the line
shrinks. `fit: "shrink"` = smaller text instead. `ed_text.split_caption_layer(layer, ow, oh, fps)` returns the chunks
exactly as displayed — QA counts these. A caption should therefore never run past the safe zone; if one does, give
shorter lines (`"subtitles": {"style": …, "max_chars": 20}` in a sequence spec, `--max-chars` on the command line).

## 4. Timing and placement (9:16, H = 1920)

- A chunk appears ~2 frames before its first word; the karaoke highlight ~1 frame before each word; no blinking
  across short pauses.
- Size 4.2–5.5 % of H, bold sans; block around x 0.47, y 0.58–0.78; below the chin on a close face (`avoid: "face"`:
  the chunk moves off the face and keeps its outline and the pop-in's peak inside the safe zone); never over the mouth
  or eyes, never over a screen recording's own captions or lower thirds.
- Safe zone: top 12 %, bottom 20 %, right 12 % (x 0.06–0.88); the genre card's "Text" section wins.

## 5. Translating captions

You translate, chunk by chunk: meaning → length → timing. `translate_plan(words, target_lang)` → a table with
per-language budgets; `apply_translation(plan, texts)` → the layer. Longer languages: tighten the wording, 1–2 words
per karaoke chunk, a smaller size down to 4.2 % of H. After dubbing or a voice-over, rebuild captions from the
**new** voice's transcript.

## 6. Fonts and scripts

Fonts are the engine's own OFL files, chosen by role (`style.font`: `grotesk`, `grotesk_condensed`, `geometric`,
`rounded`, `wide`, `serif`, `script`…); never name typefaces to the user. Missing characters fall back per
character. Chinese / Japanese / Korean: the matching CJK faces (OFL) are downloaded on first use into
`~/.cache/edit-studio/fonts` (`ED_NO_DOWNLOAD=1` disables; then boxes appear and a warning). Arabic, Hebrew and
Devanagari need raqm shaping (`edit.py doctor` shows it). Check a text before rendering:
```bash
python3 -I $ED/engine/edit.py fonts --text "$(cat $PROJ/voice/subs_text.txt)" [--font grotesk] [--lang ja] [--no-download]
```
It lists the faces that will set the text, missing characters and shaping warnings. Never render "tofu" boxes: say so
and offer a covered language or the user's own OFL font (file + licence).

## 7. Checks

QA `speech` (characters per second, time on screen, lines ≤ `max_lines`, as displayed), `safe_zone`, `faces`; a still
sheet at the middle of a few chunks, or one frame at full size (`edit.py frame EDL T --out f.png`): legible, not on a
face, not in the interface zone, no missing glyphs.
