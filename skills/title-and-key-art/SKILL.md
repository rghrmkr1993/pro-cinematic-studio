---
name: title-and-key-art
description: "Titles and key art for AI films, series, shorts and ads: opening title sequences, end credits format and order, posters and key art composition, YouTube and OTT thumbnails, teaser and trailer structure (15s, 30s, 60s, 2 min), and typography for Indian scripts (Tamil, Hindi, Telugu, Malayalam, Kannada). Gives how to make each piece with Higgsfield stills, motion-reel, hyperframes and ffmpeg, with specs, hierarchy rules and a QA list. Load after the picture is graded and before delivery, or any time a film needs a title card, poster, thumbnail, trailer or credits roll. Not legal advice; billing and credit placement follow contracts."
license: MIT
user-invocable: true
metadata:
  version: "1.0.0"
  researched: "2026-10-14"
---
Part of the cinematic pipeline: entry point creative-studio

# title-and-key-art

This skill designs the words and the sales image of a film: titles, credits, poster, thumbnail, trailer. It does not repeat craft that exists elsewhere: camera and light in `cinematography`, prompts and credits in `higgsfield-master`, code-rendered motion in `motion-reel` (default) or `hyperframes`, banner sizes in `banner-design`, brand voice in `brand`, Indian script rules in `indic-languages`. Read those, do not copy them.

Owner: title-designer agent (runs after the colorist, in parallel with the editor's final conform). Trailer cut: editor with growth-marketer. Sign-off: creative-director. Never publish or spend without the user's yes.

## 1. Intake (default, state defaults in one line)
1. Piece: title sequence, end credits, poster, thumbnail, teaser or trailer, or a set.
2. Film facts: title (all languages and scripts), logline, genre, runtime, release date or "TBA", rating if known.
3. Look: palette and type from the film's style bible (film-studio bibles-and-continuity.md section 1). One look family; titles must match the grade.
4. Credits source: approved billing block and cast list. Contracts decide order; never invent names or reorder for looks.
5. Targets: YouTube, OTT, festival, theatre, social. Default: YouTube plus festival.
6. Languages and scripts of title and subtitles. Default: original title plus English.
7. Credit cap for stills (Higgsfield) and the deadline.

## 2. Pieces and where the detail lives
| Piece | Open | Make with |
|---|---|---|
| Opening titles, title card, end credits | references/titles-and-credits.md | motion-reel or hyperframes for type; ffmpeg libass for subtitle-style Indic text |
| Poster, key art, thumbnails, social cut-downs | references/key-art-and-thumbnails.md | Higgsfield stills (plate and hero), then type in code or a design tool |
| Teaser and trailer (15, 30, 60, 120 s) | references/trailers.md | editor cut in ffmpeg or edit-director; music via music-and-sound |
| Indic type, fonts, shaping, tools, QA | references/indic-type-and-tools.md | indic-languages for the language card |
Load this file plus at most two references per step.

## 3. Principles (apply to every piece)
1. Narrative job first: a title sequence sets tone, world or theme; a poster sells one idea; a trailer sells a feeling and a question. Write that job in one sentence before designing.
2. One hero: one image, one title treatment, one message. Two competing focal points read flat (3P, poster guides).
3. Type signals genre; placement changes meaning. Pick type from the film's world, not from a default list (3P, Art of the Title interviews).
4. Image, type, credit and sound are one composition in time; keep credit windows readable.
5. Read at thumbnail size first. If the title is not legible at 120 px wide, redesign.
6. Brand and look locks: palette, type and logo rules from the bible; no other client's marks or names ever.
7. No generated text in a final. AI image models garble type, especially Indic scripts: generate the plate without text and set type in code, a design tool or libass.
8. Originals only: no imitation of a real film's title style by name, no protected logos or fonts without a licence (film-legal-distribution).

## 4. Workflow (cheapest first)
1. Brief block and one-sentence narrative job (0 credits).
2. Type study: 3 title treatments in HTML or SVG, in the film's script(s), at 3 sizes (0 credits).
3. Plate and key art stills on Higgsfield image models, draft tier, then one final (quote, balance check, user's yes first; creative-studio section 7).
4. Compose: type over plate in code (motion-reel static frame or hyperframes), export layers, keep the text-free version.
5. Motion titles: build in motion-reel (deterministic seek(t) canvas, Playwright, ffmpeg) or hyperframes (HTML composition); Indic text via the browser engine, which shapes it correctly.
6. Render alpha or burned-in versions; check at start, middle and end of each card.
7. Self-review with the QA list (section 5), then hand to creative-director.
Record each piece in `06_delivery/` and `log.md` (creative-studio section 8): file, version, fonts and their licences, prompt refs, credits spent.

## 5. QA list (pass or fix; max 2 repair rounds)
- Spelling of every name against the approved billing block, in every script shown.
- Legible at phone size and inside safe margins (9:16 safe zones: 14 percent top, 35 percent bottom, 6 percent sides).
- Contrast: body credits at least 4.5:1 against the plate; no text on busy midtones without a scrim.
- Indic: conjuncts, matras, vowel signs and numerals render correctly; the font has the script; native-speaker check before delivery (indic-languages).
- Frame rate and aspect match the master; alpha edges clean; no baked-in text from the generator.
- Credits roll: speed readable (titles-and-credits.md), no names cut by the title-safe area.
- Disclosure: AI-use credit line and platform AI label decided (film-legal-distribution).
- Fonts and music in credits licensed; licence terms logged.

## 6. Specs at a glance (re-check live sources; (3P) unless stated)
- YouTube thumbnail: 1280x720, 16:9, JPG PNG or GIF, under 2 MB (one source says the cap differs by device); channel verification required.
- Theatrical one-sheet: 27x40 in portrait; 24x36 for frames; 300 dpi for print; keep a text-free version.
- Digital posters and OTT key art: sizes come from the platform or aggregator art spec (A, shared on onboarding); typical sets are 2:3 portrait and 16:9 landscape plus a logo-free variant.
- Trailers: master 24 fps matching the film; social cut-downs 9:16, 1:1, 16:9 with burned captions.

## 7. Rules that never bend
- Spend: quote, balance, the user's explicit yes (creative-studio section 7). Publish, upload or send only on the user's yes.
- Real names, faces and voices only with written consent (film-legal-distribution releases).
- Billing and credit order are contractual: use the approved block, not convention. Not legal advice; a lawyer reviews billing obligations.
- Client neutrality: never carry one client's brand, client-licensed fonts or names into another film.
- Cosmetic or product claims in a poster tagline need the qualified team's sign-off.

## 8. Report to the Manager (10 lines max)
Pieces done with paths, versions and credits spent versus quote, QA result, fonts and licence notes, open risks (billing, consent, Indic native review), what the user must approve.
