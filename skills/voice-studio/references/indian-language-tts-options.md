# Indian-language TTS options (Tamil first)

Labels: F documented by the vendor or a primary page, 3P third party or vendor-run test, E estimate, U unverified. Prices and language lists change monthly; snapshot date 2026-10-13. Tamil naturalness reviews are scarce and mostly vendor-run: treat every score as a hint, then run your own blind test (section 3).

## 1. Comparison (Tamil focus)
| Tool | Tamil | Cost model | Licence and access | Notes |
|---|---|---|---|---|
| ElevenLabs v3 and v4 | Library has 20+ Tamil voices (owner-checked); v4 Tamil not named on the page (U) | Paid credits; free tier about 10 minutes a month, personal use (F) | Commercial on paid plans (E, confirm Terms); PVC needs consent | Best emotion and tag control, deepest voice library, STS, dubbing. 3P test: weaker Tamil name pronunciation than Bulbul |
| Sarvam AI Bulbul v3 and v4 | Yes, ta-IN, plus Tanglish code-mix (F) | Paid API: v3 Rs 30 per 10,000 characters (F); v4 price not yet listed separately (3P); free credits Rs 1,000 (3P, sources conflict) | Hosted API; get commercial terms in writing (3P advice) | 35 to 39 voices across 11 languages (counts conflict); speed 0.5x to 2.0x; consent clone from 30 to 60 s (v4, 3P); REST limit 2,500 characters |
| AI4Bharat IndicF5 | Yes, 11 languages (F) | Free, self-host (needs GPU, E) | MIT tag on the model page (F); training data and F5 base may add limits (U) | Needs a reference clip plus its transcript, 24 kHz output; "unauthorised voice cloning strictly prohibited" (F). Quality varies; Indic-Speak (22 languages) recommended by the page |
| AI4Bharat Indic Parler-TTS | Yes (F) | Free, self-host | Apache 2.0 on Hugging Face vs MIT on a gov listing (conflict, check repo); data CC BY 4.0 attribution (3P) | Describe voice with text prompt; good for draft and private use |
| Google Cloud Chirp 3 HD | ta-IN, not Preview (F) | Paid; free tier up to 1M characters per month, then $30 per 1M (F) | Standard Cloud terms | Reliable, cheap, flatter emotion (3P MOS 3.6); custom pronunciation allowed; Instant Custom Voice exists (F, consent) |
| Azure neural TTS | ta-IN Pallavi (F) and Valluvar (F); ta-LK, ta-MY, ta-SG pairs (F) | Paid per character, free tier (E) | Standard Azure terms; HD only via custom voice for Tamil (F) | One female and one male per locale; SSML control (breaks, prosody) works; sounds more neutral and older generation (E) |
| OpenAI gpt-4o-mini-tts | No official Tamil confirmation (U); one source advises against it for Tamil | $0.60 per 1M text tokens plus $12 per 1M audio tokens (F, 3P mirror) | Standard API | Steerable `instructions`; model may be deprecated (U), check before building |
| Cartesia Sonic 3.6 | Yes, `ta`, 44 languages (F) | Paid API, free demo | Standard terms; cloning exists, test Tamil similarity (F) | Built for real-time agents; low latency; naturalness for Tamil U |
| Hume Octave | No (F) | n/a | TTS and EVI APIs sunset 2026-11-13 (F) | Do not use |
| Fish Audio S2.1 Pro | Claims 83 languages, Tamil unconfirmed (U) | Free tier non-commercial; API about $15 per 1M bytes; plans $11 to $749 (conflict) | S2 open weights, licence unread (U); written consent needed for clones | 10 to 30 s clone; keep confidential scripts off the hosted tier |
| Smallest.ai Lightning v3.1 | Yes, 13 Tamil voices; recommended jeevan (M), rajeshwari (F) (F) | About $0.175 per 10,000 characters (3P conflict) | Standard terms | Marketing says Tamil is a best language; test it |
| Higgsfield audio | TTS says 70+ languages with Eleven v3, MiniMax Speech 2.8 HD, VibeVoice (3P); Tamil unconfirmed; dubbing list of 18 languages excludes Tamil (3P) | Credits | Platform terms | Convenient inside video jobs; voice change and Create Voice (up to 3 custom voices); use only for compare per elevenlabs.md rule 6 |

## 2. Naturalness evidence (read with care)
- 3P vendor benchmark (Caller Digital, 12 native raters per language, vendor sells a router): Tamil MOS Bulbul 4.4, AI4Bharat 3.9, ElevenLabs 3.8, Google 3.6; Tamil-English code switch Bulbul 4.2, ElevenLabs 3.5; name pronunciation Bulbul 88 percent, ElevenLabs 60 percent. Authors disclose interest; no confidence intervals.
- 3P Sarvam claims a blind Josh Talks study (500+ annotators, 20,000+ votes, 11 languages) preferring Bulbul V3 for naturalness; vendor-reported, not Tamil-only.
- 3P MediaNama hands-on (Bulbul v2, 2025): Bulbul had near-real Indian accent and accurate pronunciation but little emotion; ElevenLabs lacked Indian accents but gave tones and emotion.
- Reading: Bulbul likely leads on Tamil accent, names and Tanglish; ElevenLabs likely leads on emotional range, tag control, clone and STS tooling. Bulbul V4 (2026-07-30, 3P) claims richer emotion; no independent test found (U).
- Cost per spoken minute (3P estimate, about 400 characters a minute): AI4Bharat self-host Rs 0.10 to 0.30, Google Neural2 Rs 1.2, Bulbul Rs 1.5 to 2, ElevenLabs Rs 2.5 to 3.5. A short Tamil test line costs a few rupees on any engine, so testing three is cheap.

## 3. Our blind test (rung 1 of the credits ladder)
1. One test paragraph in spoken Tamil, 150 to 250 characters: a retroflex-heavy word (ழ, ற, ண), a number, a brand name, an English word, a question, an emotional beat.
2. Engines: ElevenLabs v4 (2 voices), Sarvam Bulbul (2 voices), plus Google or Smallest. 2 takes each.
3. Strip names, randomise order, 3 native listeners score with the naturalness checklist in SKILL.md.
4. Record winner per use: narration, character, Tanglish, emotional. Log engine, voice, settings, date, price.
5. Mixed route is fine: Bulbul for narration and names, ElevenLabs for emotional scenes and STS.

## 4. Choosing by need
- Warm brand narration in Tamil: ElevenLabs Tamil narrator, or Bulbul; test both.
- Explainers with English product words (Tanglish): Bulbul first (3P), ElevenLabs with Tamil-script respelling second.
- Emotional character scenes: ElevenLabs v4 with tags, or STS from a human actor.
- Free or private drafts: IndicF5 or Indic Parler-TTS self-hosted (licence and consent rules apply; confidential scripts stay local).
- Real-time or IVR bot: Bulbul, Cartesia, Smallest (not this skill's main scope).
- Lowest cost at volume: Google Chirp 3 HD or Bulbul, with more post work.

## 5. Open, free, paid
- Open and free (self-host): IndicF5, Indic Parler-TTS, AI4Bharat VITS models (Apache 2.0, 3P); some MMS-TTS models are CC BY-NC, non-commercial (3P).
- Free tier only for testing: ElevenLabs, Fish Audio (non-commercial), Sarvam credits, Smallest $1 credit.
- Paid: ElevenLabs, Sarvam, Google, Azure, OpenAI, Cartesia, Smallest, Fish paid plans, Higgsfield credits.

## 6. Checks before using any engine commercially
- Read the live terms page and keep a snapshot (date, plan) in the licence log.
- Free tiers are often personal use only (ElevenLabs free, Fish free): do not ship client work from them.
- Cloned voices: written consent first (voice-ethics.md).
- Do not upload confidential or unreleased scripts to hosted tools without the user's yes (elevenlabs.md rule 10).
- Native Tamil review of every final, including brand names and ingredient terms.
