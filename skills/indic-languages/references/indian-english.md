# Indian English (en-IN)

Labels: F sourced (sources.md), 3P third party, E estimate or craft norm, U unverified. Extends `asian-human-reference/references/speech-and-voice.md` (traits by region, honorifics, code-switching, dialogue basics); read it first and do not repeat it. Indian English is a family of accents, not one; no accent as a joke.

## 1. Script
- Latin script, so no shaping problem for the English itself. Pitfalls arise at the mix: Indic words in Latin (romanised) and English words inside Indic text. Rules for mixed-script lines are in each language file and in subtitles-and-transliteration.md.
- Spelling: Indian publishing mostly follows British spelling (colour, centre); keep one standard per project. Currency "Rs." or "₹" (U+20B9); engines read "₹" inconsistently, so write "rupees". Dates dd/mm/yyyy; write them as words in voice scripts.

## 2. Phonology (builds on the traits in the existing file)
- Retroflex /t d/ in place of alveolar; dental stops for "th"; v and w sometimes merged; syllable-timed rhythm with less vowel reduction; aspiration of p t k lighter (existing file, F via OED and arXiv 2212.09284). New cues to direct:
  - Pure monophthongs for "face" and "goat" (a clean e and o, not diphthongs) (E, widely described).
  - "Trap" and "bath" the same vowel, "cot" and "caught" often merged (E).
  - Word stress can differ from British or American norms on some words; list the brand and key words and check them with a native reviewer (U).
  - Rhoticity: varies; southern and urban-young speakers often pronounce r (existing file).
  - Intonation: rises and level tones mid-sentence; question tags "no?", "na", "isn't it?"; "only" and "itself" for emphasis; "yaar", "re", "da" borrowed from the mother tongue.
- Regional accent bases to cast, not mimic: Hindi-belt, Punjabi, Bengali, Gujarati and Marathi, Tamil, Telugu, Malayalam and Kannada English, Anglo-Indian, urban neutral or call-centre. Match to character (existing rule 3).

## 3. Spoken vs written register
- Formal written Indian English keeps Indian idiom ("kindly do the needful", "prepone", "out of station", "revert back") that Indians know and others find odd. Spoken: contractions, tags, fillers ("actually", "basically", "no?"), present continuous for habit. A brand ad needs the neutral-urban register; a village character needs the mother-tongue shaped one.
- Grammar flavours to use sparingly: "I am having a doubt", "What is your good name?" (comic-coded; avoid unless the scene wants it), "He is knowing", "Tell me only". Over-sprinkling reads as mockery.

## 4. Code-mixing
- English is the matrix in many metro speech patterns, Indic words as inserts: Hinglish, Tanglish, Tenglish, Manglish (Malayalam-English; write "Malayalam-English" to avoid the Malaysian clash), Kanglish. Insert Indic words as quoted single units ("yaar", "aiyo", "arre", "macha") and switch at clause edges. When the line is mostly English with Indic fillers, keep the script in Latin; when mostly Indic, use native script and Latin for the English words.

## 5. TTS pronunciation fixes
| Problem | Fix |
|---|---|
| Lakh and crore read as hundred thousand and ten million | Write words: "one lakh fifty thousand rupees"; check Indian grouping 1,50,000 |
| ₹, Rs., % misread | Spell: "rupees", "percent" |
| Acronyms (GST, UPI, KYC, OTP) | Letters with spaces or hyphens: G S T; test |
| Indian names | Respell with hyphens or a pronunciation dictionary; check ElevenLabs and Bulbul |
| American stress and flat "r" | Choose an Indian-accent voice (Bulbul en-IN, ElevenLabs Indian voices, Google en-IN) |
| Retroflex t and d heard as American | Choose a native Indian voice; do not fix by respelling |
| Rushed pacing | Slow to 0.9 to 0.95 on Bulbul pace; do not add "fast-talking" cues |
| "v" and "w" blurred | Not a defect for a character; fix only if the brand name is hit |
| Long numbers | Group by two digits; read as words |

## 6. Honorifics and sensitivities
- sir, madam, ji, bhai, didi, uncle, aunty are English-in-India address; "sir" for any senior (existing file). Over-formal "respected sir" is a stereotype; use for a character with that background only.
- Sensitive: call-centre accent mockery, "Apu" type caricature, caste and regional stereotypes, skin tone and accent pairing (never tie them), "Hinglish for the south" assumptions.

## 7. Tools (snapshot 2026-10-14; test every one)
| Tool | Status |
|---|---|
| Sarvam Bulbul v3 and v4-flash | en-IN supported (F, API docs); default speaker "shubh" in v3, v4-flash personas such as shubh_enhi_ads (F) |
| Google Chirp 3 HD | en-IN supported (F, docs) |
| ElevenLabs | Indian-accent English voices in the library (E); v3 tags; test accent per voice |
| Azure neural | en-IN voices (E, check live list) |
| Cartesia, Smallest | en-IN U; test |
| Higgsfield audio, Kling lipsync, OmniHuman | English is the best-supported language for each (E); Kling lists English among its 5 (3P) |
English lipsync is the safest of the six, but an Indian-accent audio on a model trained mostly on American speech can show weak retroflex timing; check frame by frame (lipsync-and-dubbing.md).

## 8. Five spoken lines (own drafts, native review required)
Line | plain-English meaning | TTS note
1. "Arre, you came so late today, no?" | Hey, you are very late today, right? | "Arre" is a-ray; keep the "no?" rise.
2. "Please come, sit, I'll just get some tea." | Welcome, sit down, I will bring tea. | Even stress, no reduction on "just".
3. "This one is really good, only. You must try." | Honestly this is very good; try it. | "only" is emphasis, falls.
4. "Let's meet tomorrow morning, nine sharp, okay?" | Meet at 9 a.m. tomorrow. | Write "nine" as a word; clear "sharp".
5. "I didn't like it, but I was scared to tell him." | I disliked it but feared saying so. | Soft, slowing end; one breath before "but".
