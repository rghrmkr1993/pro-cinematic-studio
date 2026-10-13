# Subtitles and transliteration for Indian languages

Labels: F sourced (sources.md), 3P third party, E estimate or craft norm, U unverified. Extends `film-studio/references/languages-and-localization.md` section 6 (Netflix general limits, formats, CPS script, forced narrative) and `edit-voice` (captions, transcription). Do not repeat those; add the Indic specifics.

## 1. Reading speed and line length
| Language | Line limit | Adult cps | Children cps | Status |
|---|---|---|---|---|
| Telugu | 42 characters, 2 lines | 22 | 18 | F, Netflix Telugu guide fetched 2026-10-14 |
| Tamil | 42 (fits 42 across screen) | 22 | 18 | 3P summary of the Netflix guide; confirm on the page |
| Kannada | 42 | 22 | 18 | 3P summary; confirm |
| Malayalam | 42 probable | 22 | 18 | 3P summary; confirm |
| Hindi | 42, 2 lines | 22 (SDH may allow 25 adult and 20 children) | 18 | 3P summary; the 25 and 20 wording is ambiguous |
| English (Indian English) | 42 | 20 adult, 17 children | | existing film-studio note |
- The Netflix guides are the strictest common reference; other platforms may differ. Rules from the fetched Telugu guide: max 2 lines, one line unless over 42, bottom-heavy pyramid, one speaker per line with a hyphen and no space, single ellipsis character U+2026, no space before punctuation (F).
- Count grapheme clusters, not code points: "க்ஷ" or "ಸ್ತ್ರೀ" is one visual unit with several code points. A script should use an extended grapheme cluster library (ICU or the regex "\X"). Over-limit lines: split at phrase edges, never inside a word, a conjunct, or a name.
- Indic words are long; prefer shorter synonyms and spoken forms in subtitles; a dub-and-subtitle pair may differ in length on purpose.
- Minimum duration and gaps follow the general rules (5/6 second, 2 frames gap).

## 2. Fonts that shape correctly
- Use Noto Sans or Noto Serif per script: Noto Sans Tamil, Noto Sans Telugu, Noto Sans Kannada, Noto Sans Malayalam, Noto Sans Devanagari; keep Noto Sans (Latin) for English. All are open (SIL OFL) and cover Unicode blocks fully (E; confirm licence per file). Netflix names Gautami as a placeholder for proportional sans in Telugu, not a requirement (F).
- Malayalam alternatives: Manjari, Noto Serif Malayalam (F, r12a); both render chillu and "nta" forms.
- Never let the renderer fall back from a Telugu font to a Kannada font or the reverse; set the font explicitly per track.
- Line height: Tamil and others have tall and low marks; add leading (F, r12a for Tamil).
- Shaping engine: HarfBuzz (and raqm in Pillow) is needed for conjuncts, matra reordering and chillus. Our status (checked 2026-10-14): ffmpeg 9.0.1 has libass, libharfbuzz, libfribidi, fontconfig (OK); Pillow raqm is False, and edit-director currently lacks raqm, so its Pillow text path breaks Indic captions. Burn-in with `subtitles=sub.srt:force_style='FontName=Noto Sans Tamil,FontSize=22'` with `fontsdir=` if fonts are not installed. Or install raqm for Pillow (needs fribidi and harfbuzz libraries; owner: fullstack-engineer). Test every script on the sentence "க்ஷ ஸ்ரீ ന്റ ಕ್ಷ క్ష क्ष" before a job.
- Test in the final renderer, not only in the editor preview; HTML or browser renderers (Remotion, Chromium) shape natively.

## 3. File encoding and clean-up
- SRT and VTT: UTF-8, no ANSI; BOM only if a platform asks (existing note). Line endings consistent. VTT header `WEBVTT`; timestamps with a dot in VTT and a comma in SRT.
- Normalise to NFC before saving; do not remove U+200C and U+200D. Do not apply "smart" quote or ellipsis auto-correction on Indic text.
- Verify: `file -i sub.srt`, a read-back in Python with `encoding="utf-8"`, and a render check. Excel and some editors corrupt scripts or turn text into "?": do not edit subtitles in spreadsheets without UTF-8 export.
- Do not mix scripts without need; keep the English word in Latin when the native audience would see it so (brands, UI words).
- Punctuation: Hindi danda । vs full stop: follow platform guide; Tamil, Telugu, Kannada, Malayalam use the full stop and comma (F).
- Burn-in vs soft track: for burn-in use libass; for soft, platforms render themselves, so supply UTF-8 and check on the target device.

## 4. Transliteration standards vs casual romanisation
| System | What it is | Use for |
|---|---|---|
| ISO 15919 (2001) | International, diacritics, covers Devanagari, Bengali, Tamil, Telugu, Malayalam, Kannada and others (F, Wikipedia); IAST is a subset | Databases, glossaries, academic, round-trip back to the script |
| Hunterian | Government of India and Survey of India style, no diacritics, de facto standard for place names (F, Wikipedia) | Names on maps, official-style place and person names |
| IAST | Sanskrit and Pali, close to ISO 15919 | Sanskrit terms |
| ITRANS, Harvard-Kyoto | ASCII schemes | Input methods, internal tools; ugly on screen |
| Casual romanisation | Tanglish or Hinglish as people text; "zh" for ழ, "aa" for ா, "dh", "th" vary | Social captions, lyrics for non-readers, marketing; not for glossaries |
- Pipeline columns follow film-studio: native script, readable romanised line (ITRANS-like or ISO 15919 stripped of diacritics), English gloss. Use ISO 15919 in cast.md and glossaries, Hunterian-style for names on screen, casual only if the brief wants it.
- TTS input is native script plus pronunciation dictionary. Do not feed ISO 15919 diacritics to an engine, most will misread them.
- Brand and character names: choose one romanisation, record the native script, never mix spellings (Vikram vs Vickram) across subtitles, credits and metadata.
- Lyrics: native-script subtitles for fluent audiences, casual romanisation as an optional second track; confirm lyric rights separately.

## 5. QA checklist
- Open the SRT in the same renderer as the final; scan each script's conjuncts and matras.
- CPS and line-length script over the file, counting grapheme clusters.
- Native reader checks spelling, sandhi, word breaks and register against the audio.
- No tofu boxes, no "?" or "Ã" mojibake, no split conjuncts, no Telugu or Kannada swap.
- English subtitles reviewed by a bilingual reader for tone and politeness level.
