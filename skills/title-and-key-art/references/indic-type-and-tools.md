# Indic type and tools

Labels: (F) source, (3P) secondary, (E) estimate, (A) assumption. Language detail lives in indic-languages (tamil.md, hindi.md, telugu.md, malayalam.md, kannada.md, subtitles-and-transliteration.md); read it before setting any Indic title.

## 1. Rules for Indic titles and credits
1. Shaping: Indic scripts need a shaping engine (conjuncts, matras, vowel reordering). Browsers and libass shape correctly; Pillow without raqm does not (editor rule: burn Indic captions with ffmpeg libass).
2. Never generate Indic text with an image model; set it as live text.
3. Fonts: use families that carry the script and have a licence for film and advertising use. Open families such as Noto Sans Tamil or Noto Sans Devanagari are a safe baseline (OFL, 3P: confirm per family); display fonts need a licence scope check (A).
4. Size: Indic scripts often need larger point sizes than Latin for the same legibility; start 10 to 15 percent larger (E) and check at phone size.
5. Line height: taller than Latin to protect stacked marks (E: 1.3 to 1.5).
6. Mixed-script lock-ups: align on one baseline or cap line consistently; match visual weight per script, not the same numeric weight.
7. Numerals: choose Arabic or native numerals once per film, matching the subtitles.
8. Letter spacing: do not track Indic text out as you would Latin; spacing can break ligature feel (A).
9. Transliteration: follow the film's scheme (ISO 15919 or Hunterian); names are spelled as the person writes them.
10. Native review: a speaker checks every card in each language before delivery. Mark unreviewed text as unverified in the delivery note.

## 2. Title treatments in Indic scripts
- Custom lettering: have a designer or type specialist draw it in vector; test the conjuncts that appear in the title.
- Dual-script titles: Latin and native script stacked or side by side, same visual weight, native script not smaller.
- Subtitles versus titles: titles may use display faces; subtitles need a readable sans (see the indic-languages subtitles reference: Noto, characters-per-second limits).

## 3. Tools by task
| Task | Tool | Notes |
|---|---|---|
| Plate and key art stills | Higgsfield image models via higgsfield-master | Draft first, one final; quote and yes first; no text in the prompt |
| Animated titles, kinetic type, credits roll | motion-reel (default) | Deterministic seek(t) canvas, Playwright, ffmpeg; Indic shaped by the browser |
| HTML timeline, captions, slideshows | hyperframes | Alternative engine; hyperframes-motion-graphics for title cards |
| Static posters and banners | banner-design plus code-rendered PNG | Sizes per platform; brand skill for the lock |
| Subtitle-style burns, Indic | ffmpeg libass with ASS and Noto fonts | Not Pillow |
| Cut and conform | ffmpeg, edit-director | The editor owns the final conform |
| Music for trailers | music-and-sound | Originals only |
| Brand lock | brand | One client at a time |
| Voice for trailers | voice-studio (consent, quote) | Human artist for finals where possible |
Pitfalls: font fallback in headless Chrome (load the font file explicitly and verify glyphs in a frame grab); alpha edges with premultiplied colour (render over a test background); frame rate mismatch (render at the master rate).

## 4. ffmpeg snippets (A: verify on your build)
- Burn an ASS file: `ffmpeg -i in.mp4 -vf "ass=titles.ass" -c:v libx264 -crf 16 -c:a copy out.mp4` (set fontsdir if fonts are not installed).
- Overlay a title clip with alpha: `ffmpeg -i bg.mov -i title.mov -filter_complex "[0][1]overlay=enable='between(t,5,9)'" out.mov`.
- Scrolling credits from a tall PNG: `ffmpeg -loop 1 -i credits.png -vf "crop=1920:1080:0:'t*120'" -t 120 -pix_fmt yuv420p roll.mp4` (120 is pixels per second).
Test every command on a short clip first and record the ffmpeg version in the log.
