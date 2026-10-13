# Styles: house presets, looks, caption presets, reference DNA

Three ways to say "how it should look": a **house style** in plain words ("clean and expensive", "gritty street") —
18 presets on top of the 15 genres; a **look** — a finished picture treatment (grade + texture) any segment can
take; a **reference DNA** — the measured rhythm of a reference edit. Tables on this page are generated from the
engine (`ed_plan.STYLE_PRESETS`, `ed_fx.LOOK_PRESETS`, `ed_text.CAPTION_STYLES`); the engine wins if they ever
disagree: `python3 -I $ED/engine/ed_plan.py styles`, `python3 -I $ED/engine/ed_fx.py registry looks`,
`python3 -I $ED/engine/ed_text.py registry caption_styles`.

## 1. From words to a style

Style words are matched **in English**: translate the user's words first.
```bash
python3 -I $ED/engine/ed_plan.py styles "something clean and expensive, a bit retro"
# {"name": "clean_luxe", "score": 0.6, "genre": "fashion", "matched": true, "why": "matched clean, expensive"}
python3 -I $ED/engine/ed_plan.py styles            # every style with its looks and description
```
`resolve_style(text, genre=None)`: a preset name matches outright; otherwise keywords (phrases count more), the
genre's name and the description's words score each preset. Nothing matches (often: words in another language) →
`matched: false`, score 0, the named genre's default style (else `punchy_pop`) and a why that says so — tell the
user and offer 2–3 presets from the table. Tell the user in one line which preset was picked and why. Use the style
with `edit.py plan --style "…"`, `edit.py storyboard --style "…"`, `edit.py variant … --style "…"` or `"style"` in a
sequence spec (top level or per part). Words such as "very dark", "low key" or "pitch black" in the style words
also allow a very dark picture (the picture limits of §3 relax).

## 2. House styles → genre, looks, captions, SFX

A style supplies: the genre (when none is given), a rotation of `ed_fx` looks (the version's look grade becomes the
shots' grade; its fx join every shot and replace the genre's own vignette, texture, glow and clarity), a transition
palette, preferred / avoided moves, a caption preset, an SFX style and level, pacing (cut rate, transition share).
The genre card's rules and colour targets still apply. Version v takes look v mod n of its rotation (a number =
the look's intensity, 1 when omitted); the talk styles stay natural on v0 and take a subtle look later. Odd versions
switch to the caption preset in brackets.

| style | genre | looks by version (v0 → v1 → v2) | captions (odd versions) | SFX | transitions | words that pick it |
|---|---|---|---|---|---|---|
| `clean_luxe` | fashion | clean_luxe → film_print 0.6 → teal_orange 0.5 | clean (boxed) | clean / light | cut, dissolve, fade | clean, expensive, luxury, luxe, premium |
| `editorial_mono` | fashion | mono_noir 0.8 → silver_bleach 0.9 | boxed (clean) | clean / normal | cut, flash, wipe | black and white, b&w, bw, monochrome, mono |
| `street_grit` | phonk | gritty_contrast → silver_bleach | podcast_caps (podcast_bold) | trap / strong | cut, whip, flash, zoom | gritty, grit, street, urban, raw |
| `neon_drift` | phonk | neon_night → teal_orange 0.9 → gritty_contrast 0.7 | podcast_caps (podcast_bold) | trap / strong | cut, flash, zoom, whip | neon, night, nightlife, cyberpunk, synth |
| `blockbuster` | epic | teal_orange → silver_bleach 0.8 | podcast_bold (podcast_caps) | cinematic / strong | cut, fade, flash, dissolve | epic, cinematic, blockbuster, trailer, movie |
| `dreamy_retro` | calm | dreamy_bloom → film_print | clean (boxed) | clean / light | dissolve, cut, fade | dreamy, dream, retro, vintage, nostalgic |
| `soft_morning` | calm | pastel_fade 0.8 → golden_hour 0.6 → dreamy_bloom 0.6 | clean (boxed) | clean / light | dissolve, cut | calm, peaceful, serene, airy, light |
| `moody_noir` | drama | mono_noir → cold_concrete | clean (boxed) | cinematic / normal | cut, fade, dissolve | moody, noir, sad, melancholic, melancholy |
| `punchy_pop` | viral | vivid_pop → neon_night 0.8 → golden_hour 0.8 | karaoke_highlight (karaoke_box) | trap / normal | cut, whip, zoom, flash | fun, playful, pop, bright, colorful |
| `hype_energy` | sport | vivid_pop 0.7 → teal_orange 0.8 → gritty_contrast 0.6 | podcast_caps (podcast_bold) | trap / strong | cut, flash, zoom, whip | hype, sport, sports, athletic, power |
| `golden_wander` | travel | golden_hour → film_print 0.9 → dreamy_bloom 0.6 | boxed (clean) | cinematic / normal | cut, whip, zoom, dissolve | travel, adventure, wanderlust, journey, trip |
| `fan_glow` | fanedit | teal_orange 0.8 → neon_night 0.8 → dreamy_bloom 0.7 | podcast_caps (podcast_bold) | trap / strong | cut, flash, zoom, dissolve | fan edit, fanedit, character, anime, scene pack |
| `mystery_tease` | teaser | cold_concrete → mono_noir 0.8 | clean (boxed) | cinematic / normal | cut, fade, flash | mystery, mysterious, suspense, teaser, coming soon |
| `studio_crisp` | product | clean_luxe 0.5 → vivid_pop 0.5 → pastel_fade 0.5 | boxed (clean) | clean / normal | cut, flash, wipe, zoom | product, crisp, studio, commercial, ad |
| `rise_grind` | motivation | silver_bleach → gritty_contrast 0.8 → mono_noir 0.8 | podcast_caps (podcast_bold) | cinematic / strong | cut, fade, flash | motivation, motivational, inspiring, inspirational, grind |
| `podcast_punch` | clips | natural → clean_luxe 0.35 → teal_orange 0.3 | podcast_bold (podcast_caps) | clean / light | cut | podcast, clip, clips, interview, talk |
| `calm_explain` | explainer | natural → clean_luxe 0.3 → pastel_fade 0.3 | boxed (clean) | clean / light | cut, dissolve | explain, explainer, tutorial, how to, educational |
| `native_ugc` | ugc | natural → golden_hour 0.35 → vivid_pop 0.3 | karaoke_box (karaoke_highlight) | clean / normal | cut, whip | ugc, authentic, real, phone, selfie |

| style | what it looks like |
|---|---|
| `clean_luxe` | Clean and expensive: unhurried cuts on strong beats, soft dissolves and slow push-ins, a gentle highlight glow, neutral-warm colour with matte shadows; no glitches, shakes or whips. |
| `editorial_mono` | Black-and-white editorial: hard graphic contrast, film grain, quick runway cuts, white flashes and wipes on downbeats. |
| `street_grit` | Gritty street: dark crushed contrast, cold desaturated colour, coarse grain, heavy shakes and punches on the kick, whips and flashes, velocity on the drop. |
| `neon_drift` | Neon night drive: cold shadows with hot highlights, glow on the lights, velocity and flashes on the beat, zoom transitions through the cuts. |
| `blockbuster` | Big-screen cinematic: wide establishing shots, slow motion on the drop, teal shadows and warm highlights, letterbox, dips to black between phrases. |
| `dreamy_retro` | Dreamy retro: warm faded film colour, halation and light leaks, soft long dissolves, slow motion and slow push-ins; nothing hard or digital. |
| `soft_morning` | Soft and airy: bright gentle colour, long dissolves, slow zooms, a light glow; quiet sound. |
| `moody_noir` | Moody and dark: desaturated cold colour, deep shadows, vignette and grain, slow cuts, dips to black; no punches or flashes. |
| `punchy_pop` | Bright and punchy: saturated colour, quick cuts on every beat, punch-ins and whips, zoom transitions, bold word-by-word captions. |
| `hype_energy` | Full-throttle hype: hard contrast, speed ramps into freeze frames, crash zooms, white flashes on downbeats, heavy hits. |
| `golden_wander` | Golden-hour wanderlust: warm saturated colour, light leaks and glow, motion-matched cuts, whip and zoom transitions between places, the odd dissolve. |
| `fan_glow` | Fan edit with a shine: teal grade, glow and film texture, velocity on the drop, punches and RGB splits on accents, flashes and zoom cuts. |
| `mystery_tease` | Mysterious teaser: cold contrasty colour, vignette and grain, slow reveals, dips to black and a single flash per phrase, title cards between beats. |
| `studio_crisp` | Crisp studio product: neutral clean colour, punch-ins on features, quick bursts, flashes and wipes on the beat, slow motion for the hero shot. |
| `rise_grind` | Motivational grind: contrasty muted colour, vignette and grain, slow motion and speed ramps on the key line, dips to black, big cinematic hits. |
| `podcast_punch` | Punchy talk clip: tight speaker crops, jump cuts on pauses, punch-ins on phrase starts, bold captions with keywords in colour. |
| `calm_explain` | Clear explainer: steady framing, plain cuts and the odd dissolve, slow zooms, easy-to-read boxed captions, quiet sound. |
| `native_ugc` | Phone-native creator look: natural colour, quick jump cuts, punch-ins, a whip between ideas, word-by-word boxed captions. |

The SFX column is the sound style (`cinematic`: weighty hits with a hall; `trap`: distorted 808 bodies, bright
whooshes; `clean`: tight, little drive) and the preset level of every event (light −5 dB, normal, strong +4 dB
around each sound's target loudness).

## 3. Looks

A look = a segment grade + image fx (`ed_fx.look(name, intensity)`); styles use them, and any segment can take one by
hand (`references/edl-cookbook.md`, Looks).

| look | label | what it does | aliases |
|---|---|---|---|
| `film_print` | Warm film print | Warm print stock: soft lifted blacks, teal-leaning shadows, red-orange halation round the highlights, fine grain, gentle flicker and gate weave. | film |
| `home_tape` | Home videotape | Camcorder tape: punchy red-leaning colour, soft low-res picture, colour bleeding to the right, scanlines, noise, the odd tracking band and head-switching at the bottom. | vhs, tape |
| `clean_luxe` | Clean luxury | Polished and expensive: deep clean blacks, creamy warm-neutral highlights, restrained saturation, a soft diffusion glow round the highlights, very fine grain. | luxury, clean |
| `dreamy_bloom` | Dreamy bloom | Hazy daydream: lifted pastel blacks, low contrast, wide pink-white bloom, a faint peach leak in the corner. | dreamy |
| `gritty_contrast` | Gritty contrast | Hard street look: crunchy local contrast, deep blacks, bled-out colour with teal shadows, heavy mono grain and a dark vignette. | gritty |
| `mono_noir` | Noir monochrome | High-contrast black and white with crisp mids, silver highlights, coarse grain and a heavy vignette. | noir, bw |
| `neon_night` | Neon night | Electric night: cold blue shadows, magenta highlights, saturated lights that bloom in their own colour, a hint of chromatic fringing. | neon |
| `golden_hour` | Golden hour | Late-sun warmth: amber highlights, honeyed skin, a soft gold leak drifting in from the edge, warm bloom. | golden |
| `silver_bleach` | Silver bleach | Bleach-bypass silver: colour drained to a third, hard contrast, metallic highlights, crisp local contrast and fine grain. | bleach |
| `teal_orange` | Teal and amber | Blockbuster contrast: teal shadows against amber skin, firm contrast, a light highlight bloom. | blockbuster |
| `vivid_pop` | Vivid pop | Bright and punchy: rich clean colour, crisp contrast with open shadows, extra local detail, a little sparkle in the highlights. | pop, vivid, punchy |
| `pastel_fade` | Soft pastel | Airy and light: bright lifted mids, gentle pastel colour, low contrast, a little bloom. | pastel |
| `cold_concrete` | Cold concrete | Bleak and cold: blue-grey palette with colour nearly gone, dimmed whites, soft shadows, light grain. | cold |

When the planner applies a look it fits it to the footage: the colour push eases along the shot's own cast,
near-neutral highlights stay neutral, faces never clip, at most 7 % of the picture is crushed to black and the mean
brightness stays at 60 or more on normal-key footage (low-key footage keeps about 90 % of its own level; "very dark"
requests: 15 % / 35); auto exposure adds at most +0.6 EV to well-exposed footage. `clarity` (local contrast) never
clips.

## 4. Caption presets

For talk parts and speech genres (`"subtitles": "<preset>"` in a sequence spec; styles pick one). Captions never
shrink: lines are fitted by their real rendered width; a chunk that does not fit wraps to more lines up to the
layer's `max_lines` (subtitle presets 3, karaoke 2), then splits in time at a phrase point (`edit-voice`
`references/subtitles.md`).

| preset | kind | what it looks like | aliases | sibling (odd versions) |
|---|---|---|---|---|
| `podcast_bold` | subtitle | Talk-clip captions: heavy white sans, mixed case, thin outline + soft drop shadow, numbers and keywords in yellow, 1-2 lines in the lower middle, clean pop-in per chunk. | aura, podcast, bold, clip | podcast_caps |
| `podcast_caps` | subtitle | Punchy talk-clip captions: condensed black caps, outline + shadow, keywords in yellow, 1-2 short lines, pop-in per chunk. | caps | podcast_bold |
| `clean` | subtitle | Minimal interview captions: semibold white sans, hairline outline and a wide soft dark halo, lower placement, short fade in. | interview, minimal | boxed |
| `boxed` | subtitle | High-contrast captions on busy or bright footage: bold white text on a rounded dark plate per line, keywords in yellow, soft pop-in. | box, plate | clean |
| `karaoke_highlight` | karaoke | Word-by-word captions: 2-3 heavy caps words, the sounding word turns yellow, numbers in green, outline + shadow, pop-in per chunk. | karaoke, highlight, word | karaoke_box |
| `karaoke_box` | karaoke | Word-by-word captions with a yellow plate sliding under the sounding word (black text on it), bold mixed case, soft pop-in. | karaoke_plate | karaoke_highlight |

## 5. Versions inside a style

`edit.py variant EDL --variant N` keeps the style and re-seeds the choices inside it: shots per slot, transition
order and places, accent picks, the speed-ramp rotation (four curves; neighbouring shots never share one), a grade
nuance (small temperature / saturation / contrast offsets), the next look of the rotation and, on odd variants, the
caption sibling. `meta.choices` records what a version picked (`look_pick`: the rotation and the index taken;
`ramps`: the curve per shot); the next version (or `--avoid EDL`) steers away from it. Variant 0 = the preset as
written.

## 6. Reference DNA (a measured style)

"Like reference No. 12": a numeric profile of a reference edit, stored without its frames, text or sound:
```json
{"id": 12, "name": "b&w hands, white flashes", "genre_hint": "fanedit", "duration_s": 17.4, "fps": 30,
 "music": {"bpm": 140, "steady": true, "drop_at": 0.4},
 "shots": {"n": 59, "median_s": 0.23, "p10_s": 0.1, "p90_s": 0.6, "curve": [[0.0, 0.5], [0.5, 0.15], [1.0, 0.8]]},
 "grid": {"downbeat": 0.10, "beat": 0.34, "half_beat": 0.26, "off": 0.30},
 "transitions": {"cut": 0.31, "flash": 0.54, "blur": 0.14}, "moves": {"zoom.punch": 6, "light.flash": 9},
 "color": {"look": "b&w", "contrast": "high"}, "text": {"share": 0.2, "style": "single words in caps, centred"}}
```
- Build it after a remake analysis (`remake/decomposition.json`): shot lengths and their curve over the video, the
  grid shares, the transition palette, moves found via the cards' `detect` field, colour and text in our own words.
  Show the user 4–6 lines and ask for a name.
- Database: `/home/claude/projects/_user/dna/` (`index.json` + `<id>.json`), saved with the user's shared data
  (`references/storage.md`).
- Apply: plan with the closest house style or genre (`genre_hint`), then bring the EDL in line with the profile
  (shot lengths, grid shares, transitions, colour) by edits; compare after QA and name deviations over 20 %. A
  conflict between the DNA and the genre's bans → name it and ask.
