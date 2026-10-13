---
name: indic-languages
description: "Write, voice, lipsync and subtitle scripts correctly in Tamil, Telugu, Malayalam, Hindi, Kannada and Indian English. Gives a per-language quick card and one reference per language (script and Unicode rendering pitfalls, phonology, spoken vs written register, dialects, code-mixing such as Tanglish and Hinglish, TTS mispronunciation fixes, honorifics and sensitive phrases, tool support, sample spoken lines), plus lipsync and dubbing (visemes, syllable rates, timing adaptation, tool comparison, ffmpeg alignment, frame-by-frame QA at 25 fps) and subtitles (cps, line length, Noto fonts, UTF-8, ISO 15919 vs Hunterian). Load for any Indian-language script, voiceover, dub, lipsync, caption or transliteration job, and before a native-speaker review."
license: MIT
user-invocable: true
metadata:
  version: "1.0"
  built: "2026-10-14"
---
Part of the cinematic pipeline: entry point creative-studio

# Indic languages (script, voice, lipsync, subtitles)

Owners: screenwriter (script), voice-director (voice), editor (lipsync fit, captions), continuity-supervisor (QA). Labels: F fact (sourced in references/sources.md), 3P third party, E estimate, U unverified. AI drafts are drafts: a qualified native speaker reviews every final. Not a substitute for lab, legal or regulatory review; claims in scripts come only from the approved claims list.

Do not duplicate; link to:
- Language notes, cultural checklist, subtitle general rules, dub list: `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/languages-and-localization.md`
- Indian accents, honorifics, code-switching basics: `${CLAUDE_PLUGIN_ROOT}/skills/asian-human-reference/references/speech-and-voice.md`
- Voice routes, credits ladder, naturalness score, spoken-Tamil script rules: `${CLAUDE_PLUGIN_ROOT}/skills/voice-studio/SKILL.md` and `references/script-for-voice.md`, `references/indian-language-tts-options.md`
- App and website UI strings in English, Tamil, Hindi: `~/.claude/skills/i18n-tamil-hindi/SKILL.md` (this skill is for spoken and film text, not UI strings)
- Captions, transcription: `${CLAUDE_PLUGIN_ROOT}/skills/edit-voice/SKILL.md`; mixing: `${CLAUDE_PLUGIN_ROOT}/skills/music-and-sound/SKILL.md`

## 1. Router (open ONE reference per job)
| Need | Open |
|---|---|
| Tamil script, voice, dialect, sample lines | `references/tamil.md` |
| Telugu | `references/telugu.md` |
| Malayalam (hardest script rendering) | `references/malayalam.md` |
| Hindi, Hinglish, schwa deletion, nukta | `references/hindi.md` |
| Kannada | `references/kannada.md` |
| Indian English, lakh and crore, accent casting | `references/indian-english.md` |
| Lipsync, dubbing, timing, ffmpeg fit, sync QA | `references/lipsync-and-dubbing.md` |
| Subtitles, fonts, UTF-8, transliteration standards | `references/subtitles-and-transliteration.md` |
| Sources, dates, unverified list | `references/sources.md` |

## 2. Quick card per language (E unless marked; confirm with native reviewers)
| | Tamil | Telugu | Malayalam | Hindi | Kannada | Indian English |
|---|---|---|---|---|---|---|
| Script, block | Tamil U+0B80 | Telugu U+0C00 | Malayalam U+0D00 | Devanagari U+0900 | Kannada U+0C80 | Latin |
| Shaping risk | Medium (two-part vowels, sri) | High (subscripts) | Highest (chillu, conjuncts) | High (matra, reph, nukta) | High (ottakshara) | None |
| Signature sound | ழ zha, ற, ட vs த | Geminates, no native aspirates | ഴ zha, ള, chillus, geminates | Aspirates, ड़, schwa deletion | ಳ, short and long e/o | Retroflex t d, even rhythm |
| Register gap | Large: centamil vs pechu | Medium: grandhika vs spoken | Large: formal vs colloquial | Medium: shuddh, Hindustani, Urdu | Medium: written vs spoken | Small |
| Polite you | நீங்க | మీరు | നിങ്ങൾ | आप | ನೀವು | you, sir, ji |
| Mix | Tanglish | Tenglish | Malayalam-English | Hinglish | Kanglish | any |
| Dub length vs English | Long (E) | Long (E) | Long, fast delivery (E) | Medium (E) | Medium to long (E) | Same |
| TTS leaders | Bulbul, ElevenLabs v3, Google | ElevenLabs v3, Bulbul, Google | ElevenLabs v3, Bulbul, Google | ElevenLabs, Bulbul, Google | Bulbul, ElevenLabs v3, Google | Bulbul en-IN, Google, ElevenLabs |
| Tool status | Listed (F) | Listed (F) | Listed (F) | Listed (F) | Listed (F) | Listed (F) |
Listed means the vendor docs name the language: ElevenLabs v3 (official list), Sarvam Bulbul (ta, te, ml, kn, hi, en-IN, F docs), Google Chirp 3 HD (all six, F docs). Quality is U until a native listener scores a test. Lipsync tools are audio-driven; none documents Indic quality (U).

## 3. Pipeline: script to voice to lipsync
1. Brief: language, region, character age, class, register, who listens (audience), where it plays (ad, film, social).
2. Script (screenwriter): write in the target language and script, spoken register, 6 to 14 words per line, one breath each. Three columns per line: native script, readable romanisation, English gloss (film-studio rule). English words inside the line: decide Latin or native script per tool.
3. Native review of the script (gate 1). Fix register, honorifics, dialect, taboo, product claims.
4. Pronunciation sheet (voice-director): names, brand and English words, numbers as words, acronyms, risky sounds (ழ, ഴ, schwa, aspirates). Respell per engine; store in the dictionary.
5. Test line (credits ladder rung 1, voice-studio): the hardest sentence on 2 or 3 engines, 2 takes each; the user's yes before any paid call. Native blind score.
6. Takes: Tamil v3 with at most one audio tag, 3 takes before committing; other languages 3 takes as well. Pick, splice, clean (voice-studio humanize-post.md).
7. Time fit (editor): compare duration with the shot; adapt the script, not the speed (see lipsync-and-dubbing.md section 3). Speed change only within 0.9 to 1.1.
8. Lipsync: choose by shot type and tool; 5 second test with the real audio before the full clip; no paid run without the user's yes (lipsync-and-dubbing.md section 4).
9. Sync QA at 25 fps, frame by frame; fix within one frame; contact sheet saved (lipsync-and-dubbing.md section 6).
10. Subtitles: same script, shortened to cps limits, UTF-8, correct font, libass or browser burn-in, never PIL without raqm (subtitles-and-transliteration.md).
11. Native review of the final picture and sound (gate 2), then continuity-supervisor scorecard, then creative-director sign-off.
12. Delivery: cast.md notes engine, voice, settings, consent and AI label; consent-log.md; the review sign-off name and date.

## 4. Hard rules
- Spend: quote first; no generation while researching or building; no paid call without the user's yes.
- Consent: no real-person voice or face without written consent; label AI voices; follow voice-studio voice-ethics.md.
- Mark untested language and tool combinations U; never claim a tool "supports" a language beyond what a source states.
- Never write English first and translate, unless the film is an adaptation.
- No accent as a joke; match accent to character and region, not to ethnicity.
- Do not strip ZWJ or ZWNJ; normalise NFC; UTF-8 for every text file.
- Subtitle and caption tools need HarfBuzz/raqm shaping. ffmpeg with libass and libharfbuzz is fine here; edit-director's Pillow has no raqm (checked 2026-10-14), so route Indic captions through libass or a browser renderer.
- Client-neutral: never reuse one client's script, voice or brand for another. No living public figures, film stars or politicians as names or voices.
- No TikTok for Indian clients.
- Rewrite, never rush: a line that does not fit is rewritten, then cut to a non-lip shot, before audio goes past 1.1x.

## 5. QA checklist for the native-speaker reviewer
Give the reviewer the script with the three columns, the audio, and the final cut. Ask for pass or fix on each item and record name and date.
1. Meaning: the line says what the English gloss says; no machine-translation tone.
2. Register: spoken, one register per character; no news-reader Tamil, no over-Sanskritised Hindi in casual scenes.
3. Dialect: matches the place and character (Chennai, Madurai, Kongu, Jaffna; Telangana vs Andhra; Thrissur vs Kochi vs Malabar; Dharwad vs Mysore; Delhi vs Mumbai).
4. Honorifics and address: age, gender, relation, community terms correct; verb agreement in Hindi.
5. Sounds: Tamil and Malayalam zha, retroflex vs dental, aspirates (Hindi), schwa deletion, geminate length, vowel length; the brand name.
6. Prosody: questions rise, statements fall, emotion fits, pauses carry meaning.
7. Code-mixing: natural, phrase-edge switches, particles in small doses.
8. Numbers, dates, currency, units spoken as a native would (lakh, crore).
9. Sensitive content: religion, caste, regional politics, community stereotypes, sacred text; escalate to the Manager if unsure.
10. Lipsync: mouth starts and stops with audio; closures p b m land; no teeth artefacts; still natural at normal speed.
11. Subtitles: spelling, script shaping (no broken conjuncts), line breaks at phrase edges, cps within limits, correct font.
12. Names and transliteration: one romanisation per name, native script recorded.
13. Claims: product claims match the approved list; no testimonial voiced by a synthetic voice.
14. Disclosure: AI voice labelled where required; consent log complete.
Scoring: use the voice-studio naturalness checklist (8 or more ships) and the creative-studio scorecard (drafts 85, finals 90).

## 6. Known gaps (see references/sources.md)
No lipsync test has run for any Dravidian language; syllable rates for the five Indian languages are estimates; Higgsfield Translate language list not retrieved; all sample lines are own drafts needing native review; Azure and Cartesia current voices for Telugu, Malayalam and Kannada unconfirmed.
