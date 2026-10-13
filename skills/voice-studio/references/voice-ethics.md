# Voice ethics and law

Labels: F sourced (sources.md), 3P third party, E estimate, U unverified. This is practical guidance for production, not legal advice; the user's counsel confirms anything that gates a release. Tool-level rules already exist in `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/elevenlabs.md` (rules 2, 3, 4, 10) and `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/delivery-and-legal.md`; this file adds the consent, law and disclosure detail.

## 1. Hard rules
1. No voice clone, voice conversion or sound-alike of a real person without WRITTEN consent from that person (or the estate and rights holder for the deceased).
2. No celebrity or famous-voice imitation, including "in the style of" a named singer, actor, politician or dubbing artist.
3. No fake testimonial: no synthetic voice for a customer, reviewer, doctor, dermatologist or expert quote.
4. Disclose synthetic voice where platform, broadcaster or law requires it (section 5).
5. No AI voice used to deceive: impersonation of staff, family, officials, or a brand ambassador who did not record it.
6. No confidential scripts, unreleased formulations or customer data sent to a voice tool without the user's yes.
7. Original characters by default; label realistic AI people and voices.

## 2. Consent checklist for any clone or conversion
Written release, signed and dated, covering: person's full name and contact; project and brand; media, territory, term; whether AI cloning, model training, dubbing into other languages and sequels are allowed; payment; right to withdraw and what happens to existing outputs; who owns the recording; deletion on request; revocation process; witness or ID check. Keep with the licence log (project, date, tool, voice ID).
Tools enforce this too: ElevenLabs requires verified consent for every clone and voice verification for PVC (F); Fish Audio requires written permission (3P); IndicF5 states unauthorised voice cloning is prohibited (F); Sarvam clones are consent-based (3P).
Minors: a guardian signs; avoid cloning a minor's voice.
Performers and artists: do not use a guide performance, a breath library or a singer's phrases outside the agreed use; no training a model on their recordings without a separate paid agreement.

## 3. India: personality and performer rights (3P, case law; no single statute)
- India has no dedicated personality-rights statute. Courts build protection case by case from the Copyright Act (performers' rights, section 38B), Trade Marks Act, passing off, IT Act and constitutional privacy (3P).
- Examples (interim orders, not final rules): Anil Kapoor v. Simply Life India, Delhi HC, 2023, protected name, image, likeness, voice and manner of speaking against AI and deepfake misuse; Arijit Singh v. Codible Ventures, Bombay HC, 2024, an early AI voice-cloning ruling; Asha Bhosle v. Mayk Inc., Bombay HC, 2025, interim relief against voice cloning without consent (3P). Other Delhi HC orders in 2025 and 2026 involve Sadhguru, Karan Johar and members of the Bachchan family; actor Shruti Haasan obtained an interim order in 2026 (3P). More suits were reported in 2026 and the Delhi HC is reported to be moving to define personality rights (3P, check status).
- Practical reading (E): a voice that audiences would link to a known person can create liability even if "AI generated". Healthcare-style content with a celebrity voice is treated strictly (3P).
- Skincare and wellness copy: never use a known voice to endorse a product; consumer protection and advertising rules (ASCI, CCPA) apply; claims need substantiation and regulatory sign-off by qualified staff.

## 4. Other law to note (E, U where flagged)
- EU AI Act transparency obligations for synthetic audio start 2026-08-02 (3P). Relevant if the audio is shown to EU audiences.
- US: state right-of-publicity and voice laws vary; synthetic voice in political or robocall use is restricted (U, not this skill's scope).
- Copyright: AI output alone may not be protected; human authorship (the performance, the script, the edit) is what protects your final (see AI music licensing in sound-music-voice.md section 6).
- Data protection: a voice sample is personal data and can be biometric; collect only with a notice and a purpose, store securely, delete on request (India DPDP Act 2023, U on detail).

## 5. Disclosure
- India IT Rules amendment on "synthetically generated information", notified 2026-02-10, in force 2026-02-20 (3P). Covers AI-created or substantially altered audio, visual and audiovisual content that appears authentic, including voice clones. Platforms must show a prominent label and keep metadata; users self-declare uploads; text is out of scope; routine edits such as noise reduction, compression and accessibility changes are excluded (3P). A later April 2026 draft proposing a continuously visible label was reported (3P); check status.
- Action (E): label AI voice in the video or audio, in the upload declaration and in the delivery note, for example "AI-generated voice". Put the line "This audio is synthetically generated" in an audio disclosure for audio-only ads if the platform needs it. Check each platform (YouTube, Meta, broadcasters, OTT).
- Never remove embedded provenance or watermark data.
- Keep a disclosure line in the delivery file and in the licence log.

## 6. Dubbing and translation
- Do not clone the original actor's voice into another language without that actor's consent.
- A translated voice for a living person's statement must carry their approval of the translation.
- Use consented actors or licensed synthetic voices per language.

## 7. Library, designed and open voices
- ElevenLabs library voices: check the voice's licence and commercial terms for the plan; some voices are restricted by use case.
- Voice Design creates a synthetic voice; if it resembles a real person, discard it.
- Open models: read the model licence and the dataset licences (IndicF5 MIT tag plus data conditions, Indic Parler-TTS Apache 2.0 or MIT conflict; 3P) and the reference-audio consent rule.

## 8. Pre-release ethics gate (tick all)
- [ ] Every real-voice source has a signed release on file.
- [ ] No celebrity, no sound-alike, no deceased voice.
- [ ] No synthetic testimonial or expert quote.
- [ ] Disclosure line added where required; platform declaration done.
- [ ] Licence terms snapshot for each tool and plan used (date, tier).
- [ ] Claims match the approved list; regulatory review done by qualified staff.
- [ ] Native speaker reviewed for meaning and respect (no mocking accent).
- [ ] Voice IDs, models and consents logged; confidential material kept off unvetted tools.
