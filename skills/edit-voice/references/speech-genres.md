# Speech genres: clips, explainer, UGC, motivation — and talk parts

Cut **on words**, not on beats: the time axis is speech. Genre cards in edit-director (`genres/clips.md`,
`explainer.md`, `ugc.md`, `motivation.md`; summary `find_move.py --genre clips`); house styles for them:
`podcast_punch`, `calm_explain`, `native_ugc`, `rise_grind` (edit-director `references/style-dna.md`).
`E="python3 -I $ED/engine"`.

## 1. Common pipeline

1. **Transcript** → `$PROJ/voice/words.json` (`references/transcription.md`).
2. **Read it by phrase** (a break at pauses ≥ 0.4 s; this is your strength — meaning, hooks, payoffs):
   ```bash
   python3 -I -c "
   import json; w=json.load(open('$PROJ/voice/words.json'))['words']; line=[]; t0=w[0]['t0']
   for i,x in enumerate(w):
       line.append(x['w'])
       if i+1==len(w) or w[i+1]['t0']-x['t1']>=0.4:
           m,s=divmod(t0,60); print(f'[{int(m)}:{s:05.2f}] '+' '.join(line)); line=[]; t0=w[i+1]['t0'] if i+1<len(w) else 0
   "
   ```
   An hour of podcast ≈ 9,000 words — read it in 10–15 minute parts.
3. **The moment**: the user's quotes (§2), or candidates (§3).
4. **Build**: a talk part of a composite (`edit.py sequence`, §4) — exact in/out by words, reactions kept, speaker
   crops, captions — or a speech-genre plan: `$E/edit.py plan --footage talk.mp4 broll.mp4 --genre clips --from "…"
   --to "…" --project $PROJ` (jump cuts at pauses and fillers, B-roll over the running voice, punch-ins on phrase
   starts, karaoke or subtitles from the style's preset; `--src-in/--src-out`, `--words`, `--lang`, `--subtitles`).
5. **Draft preview → QA** (`speech`, `parts`, `rhythm` on word spans) → fixes per edit-director's rules.

## 2. Word anchors: the user's in and out points

Users name boundaries by words: "from where she says …", "up to 'three million'", "after he laughs".
```bash
$E/edit.py voice phrase $PROJ/voice/words.json "three million" --all     # every occurrence: t0, t1, score, text
$E/edit.py voice reaction $PROJ/media/talk.mp4 31.20 --words $PROJ/voice/words.json   # end of the reaction after 31.20 s
```
- `find_phrase(words, text, after=None, before=None, min_score=0.7)`: case-, punctuation- and number-format-
  insensitive ("4 million" = "4,000,000" = "four million" = "4M"; "$10,000" = "10 000 dollars"), tolerant to ASR
  splits ("life style" = "lifestyle"); a different number is a different phrase. Read the transcript line around
  each hit; found twice → `occurrence` (spec) / `--after` (CLI); not found → show the nearest lines, do not guess.
- "Up to X" ends after X's last word at the next quiet point; "until the reaction to X" → `"end": "after_reaction"`:
  `reaction_end` finds the end of the sigh, laugh, breath or one-word "wow" after X, just before the next sentence
  (≤ 4 s). The reaction is the payoff — never trim it. The listener may be on another camera: the speaker crop
  follows the visible face after each camera cut.
- "Without the bit about Y" → `remove` the whole sentence (quote it) with its pauses; the joined pause stays short.
  Check the seam reads naturally (no half sentence, no dangling "and").
- Only the end named ("the bit that ends with his laugh") → no `from`: the first clean sentence (sources up to
  ~90 s; a fragment cut off by the recording, or a start whose picture is hidden by a pop-up or shows no face, is
  skipped), or on longer sources the best setup sentence at most 25 s before the end — `ed_voice.setup_starts(words,
  end_t, max_s=25)` ranks sentence starts after a pause, questions and topic openers first and penalises a leading
  "and / but / because" or a pronoun pointing back. `"from": {"auto": true, "max_s": 25}` asks for it on any
  source. `ed_sequence.py resolve` prints the chosen start: quote it to the user.

## 3. Finding moments in a long video

```bash
$E/edit.py voice clips $PROJ/voice/words.json --media $PROJ/media/talk.mp4 --min-s 15 --max-s 60 -n 5
```
Ranked 15–60 s windows: start at a self-contained sentence, end at a sentence end + pause or reaction; score = hook ×
payoff × speech density. Offer the user 3 with time, first line, payoff and why it lands; they pick. Rules for a good
clip: makes sense without context (no "as I said", no unexplained "he"), a hook in the first seconds (a question, a
number, a bold claim, emotion), a payoff (a punchline, a conclusion, a reaction). Flash-forward (1–3 s of the payoff
first) on request.

## 4. Talk parts (composites)

A talk part is built by edit-director's sequence planner (`references/scenario-composite.md` there); this skill
supplies the speech side:
- `from` / `to` / `remove` by phrases (§2); `tighten_pauses` only when the user wants it fast (a moment followed by a
  hype edit usually keeps its natural pauses — the reaction needs air);
- `crop: "speaker"`: the content box and static overlays are detected and kept out (§5);
- `subtitles`: a caption preset (`references/subtitles.md`) — only over the talk part, chunked by phrase with jump
  cuts (removed text) and the part's ends as hard breaks and camera cuts as soft, preferred ones;
- lip sync: measured per source and corrected when the estimate is confident (≥ 2 frames); `av_offset` overrides
  (`0` keeps the recording); the planner's note says what was done;
- `music_db` −18…−24 (the track's build under the talk, swelling into the edit part's drop);
- `punch_ins: true` / `push: true` for motivated zooms on long camera shots;
- QA: 0 cuts inside words, the first word ≤ 0.3 s after the part starts, pauses, captions as displayed, the face
  whole, overlays outside the crop.

## 5. Screen recordings (a player inside a browser or app)

The picture is a window. `ed_video.content_box(path, t0, t1)` finds the live video area (browser / player UI, the
player's glow and pop-ups excluded); `ed_video.static_overlays(path, box, t0, t1)` finds the logo, lower thirds,
watermarks and notices inside it (`kind`: `logo` / `text` / `ui`, plus `popup` for a transient app window or toast;
`coverage`, and `spans` — when each is on screen: a pop-up is kept out of the crop only while it shows, and QA
judges every overlay only inside its spans); `ed_reframe.speaker_crop(…, box=box, avoid=overlays)` keeps them out of
every 9:16 window while keeping the face whole (`references/scenario-vertical.md`).
Quick look: `$E/ed_video.py box SRC`, `$E/ed_video.py overlays SRC --box x0,y0,x1,y1`, `$E/ed_video.py cuts SRC`.
Burned-in captions of the source are overlays too — ours must not sit on them. A 4K recording of a 1080p player is
still a 1080p picture: a tight crop looks soft.

## 6. Explainer, UGC, motivation

- **Explainer**: key points → visual support for each (a cutaway, a callout, a counter, key words); captions
  mandatory; 9:16 or 16:9 (`references/scenario-vertical.md` for infographics).
- **UGC ad**: hook (problem or result in the first second) → problem → solution / demo → call to action; jump cuts with
  punch-ins, product cutaways, word-by-word captions. Claims only as the user gave them.
- **Motivation**: a voice-over over epic cutaways on the beats (`edit.py plan --track T --footage … --voice VO.wav
  --genre motivation --project P`);
  cuts on the phrase boundary nearest a beat; kinetic key words.

## 7. What not to do

A cut inside a word; speech squeezed above ~4.5 words/s; the pause before a punchline removed; captions drifting from
the voice; two graphics layers at once over captions; a translation that changes the meaning; someone else's slogans
or brand names in on-screen text.
