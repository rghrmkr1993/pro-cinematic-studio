# Sources (read 2026-10-13 and 2026-10-14; paraphrased)

Labels: F primary or vendor documentation page, 3P third party or a search-result summary of a page, E estimate, U unverified. Prices, language lists and limits change monthly; re-check before a paid job.

## Script and Unicode
- r12a Malayalam orthography notes (https://r12a.github.io/scripts/mlym/ml.html): chillus, atomic vs ZWJ, conjuncts, line breaking. F.
- r12a Tamil orthography notes (https://r12a.github.io/scripts/taml/ta.html): two-part vowel signs, grantha, ksha and sri, pulli, line breaking. F.
- r12a Telugu notes (https://r12a.github.io/scripts/telu/te.html): aspirates as loan features. 3P (search summary).
- Unicode Standard chapter 12 (https://www.unicode.org/versions/Unicode15.0.0/ch12.pdf): the PDF was not text-extractable; block ranges and ZWJ or ZWNJ behaviour are standard knowledge. E, verify in the charts at unicode.org/charts.
- Local checks 2026-10-14: ffmpeg 9.0.1 build flags libass, libharfbuzz, libfribidi; Pillow raqm False. F (own run).

## Phonology
- Wikipedia: Tamil phonology, Malayalam phonology, Hindustani phonology, Telugu language, Kannada. F-grade encyclopaedic, cross-checked against each other; the Hindustani and Telugu pages were read in part (first 100,000 characters). Wikipedia Voiced retroflex approximant, plosive and flap pages (search results). 3P.
- arXiv 2212.09284 and the existing asian-human-reference file for Indian English traits (cited there). F as cited.
- Pellegrino, Coupe and Marsico 2011, "A cross-language perspective on speech information rate", Language 87(3) (http://www.ddl.cnrs.fr/fulltext/pellegrino/Pellegrino_2011_Language.pdf): rates for 7 languages. 3P via search summary.

## TTS and language support
- ElevenLabs v3 language list (X post and elevenlabs.io/v3 via search): includes Hindi, Tamil, Telugu, Malayalam, Kannada. 3P and vendor; the help centre language page returned HTTP 403 on fetch.
- Sarvam API docs, text-to-speech convert (https://docs.sarvam.ai/api-reference-docs/text-to-speech/convert): 11 language codes including en-IN, ta-IN, te-IN, ml-IN, kn-IN, hi-IN; models bulbul v2, v3, v4-flash; pace 0.5 to 2.0; 2,500 character limit. F.
- Google Cloud Chirp 3 HD docs (https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd): ta-IN, te-IN, ml-IN, kn-IN, hi-IN, en-IN; no Preview label on these. F via search summary.
- Existing voice-studio references: indian-language-tts-options.md for Azure, IndicF5, Cartesia, Smallest, Fish, OpenAI.

## Lipsync and dubbing
- sync.so lipsync model docs (https://sync.so/docs/models/lipsync): lipsync-2, lipsync-2-pro, sync-3 differences. F.
- Higgsfield help centre, lipsync options (https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-lipsync-voiceover-and-aspect-ratios): model list, Translate 18 languages. F (vendor). Higgsfield blog on lipsync across languages (https://geo.higgsfield.ai/blog/recommended/which-ai-lipsync-tool-works-best-across-languages-5183d2): marketing, no language list. 3P.
- Kling 3.0 lip sync guide (https://kling.ai/blog/kling-video-3-omni-native-lip-sync-audio-guide) and fal Kling lipsync listing: five languages named; audio limits. 3P via search summary.
- OmniHuman 1.5 host pages (eachlabs, kie.ai, modelslab, fliki, ElevenLabs video): limits conflict. 3P.
- VEED Fabric 1.0 and Lipsync API (fal.ai, veed.io): limits conflict. 3P.
- ElevenLabs dubbing help centre pages (languages, Dubbing v2): Tamil, Telugu, Kannada, Malayalam, Hindi listed; lip sync not part of dubbing. 3P via search summary; one page flagged as old.
- ITU-R BT.1359-1 (1998): detectability +45 ms to -125 ms, acceptability +90 ms to -185 ms. F via search summary. EBU R37 and ATSC limits. 3P.

## Subtitles and transliteration
- Netflix Telugu timed text style guide (https://partnerhelp.netflixstudios.com/hc/en-us/articles/4482320288787-Telugu-Timed-Text-Style-Guide): 42 characters, 22 and 18 cps, rules. F (read). Tamil, Kannada, Malayalam, Hindi guides: 3P summary only, URLs on partnerhelp.netflixstudios.com; confirm.
- Wikipedia ISO 15919, Devanagari transliteration, Wikipedia Indic transliteration: ISO 15919 and Hunterian roles. 3P.

## Unverified or open
- Tamil, Telugu, Malayalam, Kannada lipsync quality on every tool (no test run, no spend).
- Higgsfield Translate language list.
- Syllable rates for the five Indian languages (estimates only).
- Spoken-form examples, honorific and dialect notes: written from general knowledge, need native review.
- ElevenLabs v3 per-language quality, Sarvam v4-flash independent quality.
- Azure and Cartesia current voices for te, ml, kn.
