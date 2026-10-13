# Languages and localisation

Any language is possible; quality depends on native review. Labels: (F) fact from a source, (3P) third-party, (E) estimate or craft norm, (A) assumption to verify. For faces, attire, hair, gesture and speech cadence of Indian and Asian characters, load `asian-human-reference` (regions-and-appearance.md, speech-and-voice.md, prompt-library.md); do not repeat its content here.

Deep per-language guides (script, phonology, dialect, TTS, lipsync, subtitles) for Tamil, Telugu, Malayalam, Hindi, Kannada and Indian English: `${CLAUDE_PLUGIN_ROOT}/skills/indic-languages/SKILL.md`.

## 1. Principle: write in the language, not through English
1. Write the screenplay natively in the target language and script (Tamil script, Devanagari, Telugu, Malayalam, Kannada, Bengali script, Latin, others). Do not write English first and translate unless the film is an adaptation.
2. Keep the slugline convention (INT./EXT.) in English or the local convention, consistently; keep character names in one agreed romanisation plus native script.
3. Maintain three columns for every spoken line: native script, romanised (ITRANS-like, readable), English gloss. The prompt stage uses the romanised and gloss lines; subtitles use translation; voice casting uses the native script.
4. Native-speaker review (script writer, dialogue editor and voice reviewer) is a gate for every language. AI drafts are drafts.
5. Fix the register per character: formal, colloquial, rural, urban, class, age; do not flatten to one neutral voice.

## 2. Language notes (E; confirm with native reviewers)
| Language | Script | Writing and speech notes | Common pitfalls |
|---|---|---|---|
| English | Latin | Indian English has its own rhythm and idiom; choose Indian, British, American deliberately | Defaulting to American idiom for an Indian setting |
| Hindi | Devanagari | Register spectrum from Hindustani to Sanskritised; honorific pronouns (aap, tum, tu) signal relationship; code-switching with English is normal in urban speech | Over-Sanskritised dialogue; wrong honorifics; gendered verb forms |
| Tamil | Tamil script | Large gap between formal written (centamil) and spoken (koduntamil) register; regional dialects (Chennai, Madurai, Kongu, Tirunelveli, Sri Lankan Tamil); honorifics and kinship terms strongly used | Literary Tamil in casual scenes; wrong dialect for the place |
| Telugu | Telugu script | Spoken and literary registers differ; regional variants (Coastal Andhra, Telangana, Rayalaseema); honorific suffix -andi | Mixing Telangana and Andhra idiom without intent |
| Malayalam | Malayalam script | Dialects vary strongly by region and religion community; spoken form compact; heavy use of idioms and sarcasm in dialogue | Using Thrissur, Kannur and Kochi forms interchangeably |
| Kannada | Kannada script | Regional dialects (Dharwad, Mysore, Mangalore, Kalaburagi); respectful forms (neevu, nimma) | Standardising away dialect; wrong honorific |
| Bengali | Bengali script | Sadhu versus cholito register (cholito is standard now); Kolkata versus Bangladesh forms; kinship terms are specific (dida, thakuma, mashi, pishi) | Mixing West Bengal and Bangladesh vocabulary |
| Other Indian (Marathi, Gujarati, Punjabi, Odia, Assamese, Urdu) | various | Same rule: native script, dialect, register, kinship terms | Machine translation tone |
| East and Southeast Asian (Japanese, Korean, Mandarin, Thai, Indonesian, Vietnamese) | various | Honorific systems (keigo, jondaemal) shape dialogue; use `asian-human-reference` for culture | Flat register, wrong politeness level |
| Other world languages | various | Appoint a native dialogue editor before scripting | Translating idioms literally |

## 3. Cultural adaptation checklist
- Kinship terms and forms of address; honorifics; greetings and gestures per region (asian-human-reference body-language file).
- Food, festivals, religious symbols, ritual accuracy; avoid mixing regional rituals; consult an adviser for sacred material.
- Clothing, hair, jewellery by region, caste and class (not stereotypes); weather and architecture by place.
- Humour: puns and wordplay rarely survive; rewrite the joke rather than translate it.
- Taboos: sensitive caste, religion, community, sexuality, historical, political content (flag to the Manager for legal and certification review).
- Names: real-sounding, not famous; avoid names of living public figures; check meanings.
- Numbers, dates, units, currency by period and place.
- Gestures: head wobble, namaste, touching feet, eye-contact norms; correct per region.
- Skin tone and appearance: state it per character, never lighten (creative-studio section 7).

## 4. Voice and TTS caveats per language (3P, 2026-10-13)
- Hindi has the strongest model support; Tamil, Telugu, Malayalam, Kannada and Bengali support varies by tool and changes often; ElevenLabs reports 90 plus languages for dubbing (audio only), HeyGen claims 175 plus for lipsync, Dubverse is cited for Indian languages; none of the sources read confirmed Tamil or Telugu support. Test each language with a 3-line sample and a native listener; record the result as supported, partial or unverified.
- Check: retroflex consonants, long vowels, gemination, stress, code-switching, names and numerals, dialect colour.
- Prefer human voice actors for lead roles when quality fails; consented clones only.

## 5. Dubbing and versions
- Original language version (OV) is the master. Dubbed versions are derived; keep the M and E stem (sound-music-voice.md section 9).
- Lip-sync strategy: time-fit the translation to mouth length; for dubbed versions in languages with different syllable counts, rewrite lines, or cut to non-lip shots.
- Dub list per language: lines, speakers, timecodes, adapted text, voice id, review status, sign-off.
- Songs: re-write lyrics in the target language with the same meaning and rhythm; do not machine translate; rights for any translated lyrics belong in the licence log.
- Titles, on-screen text and graphics: text-free master plus a language layer for titles; never bake text into generations.

## 6. Subtitles (F, Netflix timed text guides, read 2026-10-13; check the language page of the platform you deliver to)
- General: 42 characters per line (Latin script), max 2 lines, minimum duration 5/6 second (20 frames at 24 fps), maximum 7 seconds, 2 frames gap minimum. Reading speed English about 20 cps adult and 17 children (third-party sources disagree, 17 is a common value); Hindi, Tamil and Kannada guides list up to 22 cps adult and 18 children; Telugu, Malayalam, Bengali figures were not retrieved, so check the guide (assume 17 cps until confirmed (A)).
- Indic script lines: count grapheme clusters or follow the platform's character counter; combining marks and conjuncts make "characters" ambiguous. Keep lines shorter than the Latin limit when unsure.
- Style: split at phrase boundaries; do not break a name or a verb phrase; dialogue dashes per the platform guide; italics for off-screen voice or inner thought; song lyrics marked with the platform's symbol; sound cues in captions for the deaf and hard of hearing (SDH) in brackets.
- Formats: SRT (index, `HH:MM:SS,mmm --> HH:MM:SS,mmm`, text), WebVTT (`WEBVTT`, dot decimal, optional cues and styling), TTML or IMSC (OTT), ASS (styling, burn-in). Converting: `ffmpeg -i s.srt s.vtt` (verified 2026-10-14). Encoding UTF-8 with BOM only if the platform wants it.
- CPS check script: for each cue, chars divided by duration; flag over the limit and under 1 s. Use a script from fullstack-engineer, not eyeballing.
- Burned-in (hard) subtitles for social cuts, soft subs for YouTube, OTT and festivals (DCP: separate subtitle reel in a version file).
- Forced narrative subtitles: for on-screen foreign text and foreign-language lines inside a film; supply a separate track.
- Indian subtitle practice: many festivals ask for English subtitles; theatrical in India often wants regional plus English.
- Accessibility: CBFC rules for feature films require accessibility features for disabled persons (F, 2024 Rules per PIB and secondary summaries; check the portal for the form of captions and audio description).

## 7. Multi-language release plan template
`language | script | writer | dialogue editor | voice cast | tool | lipsync (y/n) | subtitle (y/n) | reviewer | status | licence`
Start with the OV plus English subtitles; add dubs per demand after OV picture lock; do not translate before lock.

## 8. Linking
Characters and appearance: asian-human-reference regions-and-appearance.md, hair-grooming-attire.md, speech-and-voice.md, prompt-library.md. Photoreal faces and skin: photoreal-humans. Scripts per language: story-and-script.md section 4 and 5. Voice and loudness: sound-music-voice.md.
