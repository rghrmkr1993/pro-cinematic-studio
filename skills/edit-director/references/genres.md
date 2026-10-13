# Genres: choosing, reading a card, deviations

A genre sets the structure and rhythm before the first iteration. The card is `genres/<slug>.md`: a YAML header (read
by the planner) + 9 text sections (read by you when you make decisions and explain them to the user).
Template for a new card: `genres/_template.md`.

## 15 genres

| genre | slug | cut by | length, s (typical) | what it is about |
|---|---|---|---|---|
| viral | viral | beats | 7–30 (16) | a hook in the first second, dense cutting, trending moves, an ending that loops |
| epic | epic | beats | 15–60 (30) | slow build-up, impacts, slow motion, letterbox, the best shot on the drop |
| dramatic | drama | beats | 15–60 (30) | silence before the impact, speed ramps, black frames, text lines |
| calm | calm | beats | 15–60 (30) | long shots, soft dissolves, grain, warm color |
| product | product | beats | 10–30 (20) | macro, product reveal, callouts with facts, packshot and call to action |
| phonk | phonk | beats | 10–40 (20) | shake and flashes on the beat, ramps, RGB split, reacting to the bass |
| sport | sport | beats | 15–60 (30) | action peaks, freeze frames with text, impacts, stats |
| travel | travel | beats | 15–60 (30) | whip transitions, match cuts, a route, an easy pace |
| fashion | fashion | beats | 10–40 (20) | strobes, flashes, choppy stop motion, stylish typography |
| fan edit | fanedit | beats | 10–60 (20) | sync with the song's lyrics, glows, overlays |
| teaser | teaser | beats | 10–30 (20) | intrigue, text cards, countdown, a reveal at the end |
| clips | clips | words | 15–60 (35) | the best moments of a long video, subtitles, punchlines, translation |
| explainer | explainer | words | 20–90 (45) | infographics, arrows, zooms, subtitles |
| UGC | ugc | words | 15–60 (30) | a talking head with a product: hook, problem, solution, call to action |
| motivation | motivation | words + beats | 15–60 (30) | voiceover, epic cutaways, kinetic typography |

Speech genres (clips, explainer, UGC, motivation) are driven by the **edit-voice** skill: cutting on words, subtitles,
voiceover; this skill renders and checks. The genre list is open: the user can edit genres and add new ones.

## How to tell which genre is needed

The user's words → genre: "epic, cinematic, trailer-like" → epic; "for the feed, trending, viral" → viral;
"phonk, velocity, hard on the bass" → phonk; "cozy, atmospheric, slow" → calm; "product ad, packshot" →
product; "trip, travel, vlog" → travel; "look, outfit, beauty" → fashion; "to a song, anime, game" →
fan edit; "announcement, coming soon, intrigue" → teaser; "from a podcast/interview/stream" → clips; "explain, how-to,
infographics" → explainer; "review, talking head with a product" → UGC; "motivational, voiceover" → motivation.
If it is unclear, offer 2 options with a one-sentence difference and the `find_move.py --genre <slug>` summary.
Words about the look and feel rather than the genre ("clean and expensive", "gritty street", "dreamy retro") pick a
house style, which brings its own genre: `edit.py plan --style "…"` with the words in English
(`references/style-dna.md`).

## How to read a card

Do not load it whole (≈25–35 KB). First, the header summary: `python3 -I $ED/scripts/find_move.py --genre <slug>`.
Then only the section you need (`grep -n '^## ' genres/<slug>.md`, then `sed -n 'a,bp'`):

| task | section |
|---|---|
| plan by seconds, track window, other lengths | "Structure by seconds" |
| shot lengths, cut grid, pauses | "Rhythm" |
| which shot goes where, what not to use, a needed shot is missing | "Shot selection" |
| which moves, parameters, limits per 10 s, bans and why | "Moves by part" |
| sounds, levels relative to the music, ducking | "SFX" |
| the grade in numbers, looks | "Color" |
| font size, position, safe zones, text animation | "Text" |
| self-check thresholds | "Quality checks" |

Header: `structure` (the parts and their shares of the length), `rhythm` (`shot_len_s`, `cut_grid`, `on_beat_share`,
`on_word_share`, `max_shot_s`), `moves` (`hook`/`build`/`drop`/`outro`; `signature` — the genre's signature,
`allowed` — situational, in any part, `forbidden` — breaks the genre), `sfx` by part, `looks`.

The link to moves goes both ways: a move card has a `genres` field (`signature`/`allowed`/`forbidden`). If they
disagree, the **genre card** is right — it is the source of truth.

## Deviating from the genre

- **For one project** ("epic, but without the bars", "more flashes"): planner options first (`--forbid fx.letterbox`,
  `--require`, `--cut-rate`, `--sfx-level`; `references/scenario-genre.md`), recorded in `project.json` → `overrides`;
  do not touch the card. Say what changes and what the risk is ("there will be 5 flashes
  per 10 s — in an epic edit that already looks cheap").
- **Genre mix** ("epic phonk"): one genre is the base (structure and rhythm); from the second one we take moves that
  the base does not forbid. Tell the user which genre is the base.
- **A look on top of a genre**: a house style carries a rotation of 2–3 (`--style "dreamy retro"` → `dreamy_bloom`, the
  next version `film_print`); by hand, any `ed_fx` look on the segments (`film_print`, `home_tape`, `mono_noir`,
  `neon_night`… — `references/style-dna.md` §3, `references/edl-cookbook.md`, Looks); the genre card's `looks` field
  lists the look moves that suit it.
- **Permanently** ("never any text in epic", a new genre): edit a copy of the card in the user's data
  (`references/storage.md`), then run the checks:
  ```bash
  python3 -I $ED/scripts/check_genre.py $ED/genres/<slug>.md      # format and existence of move ids
  ```
  The skill folder may be read-only: keep your own genre versions in `/home/claude/projects/_user/genres/` (`references/storage.md`).
