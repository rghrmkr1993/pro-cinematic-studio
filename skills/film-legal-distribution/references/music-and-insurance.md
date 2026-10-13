# Music licensing in India and E&O insurance

Not legal advice. Labels: (F) official, (3P) law-firm or broker article, (E) estimate, (A) assumption, (U) unverified. Re-check IPRS, PPL and the labels directly.

## 1. Two layers of rights in every recorded track (3P)
- Composition: music and lyrics (the song). Rights sit with authors, composers and publishers; IPRS (Indian Performing Right Society) is the registered copyright society for these performing rights (3P: registered under section 33 of the Copyright Act 1957).
- Sound recording (master): the recorded performance. Rights sit with the label or producer; PPL (Phonographic Performance Ltd) licenses public performance of sound recordings in India (3P).
- A film needs, for a licensed track: a sync licence (composition, from the publisher or label) and a master use licence (recording, from the label). Public performance licences are separate and may be handled by the exhibitor or platform; the sync agreement should say who handles them (3P).
- India has an additional twist: the film producer's rights in film music, and assignment terms between composer, lyricist and label vary by contract; later amendments changed the position on authors' royalties (3P, U). Counsel to confirm.

## 2. Our default: originals
1. Score and songs created for the film, human-composed or generated with a tool whose terms permit commercial use; keep prompts, stems and dates (music-and-sound).
2. Human composer assignment where possible, so the film owns its music with a signed paper.
3. No copyrighted lyrics or melodies, no imitation of a named singer, composer or band, no voice clone of a real singer without written consent.
4. Library music: a licence naming film use, territory and media, with proof of purchase and licence ID; confirm streaming and festival coverage.
5. Licensed commercial tracks: only with a budget and clearance time (weeks to months, E); ask for sync and master quotes early; get media (festival, OTT, theatre, online), territory and term in writing; ask for perpetuity or a long term; confirm streaming and all-media coverage (3P: older licences may predate streaming).

## 3. Process
1. Music cue list from the locked cut: cue id, scene, duration, source type (original, library, licensed), use type (background, visual vocal, theme).
2. For each licensed cue: identify the rights holders, request a quote with the media, territory, term and credit asked, record the date and reply.
3. For original cues: assignment or work-for-hire paper, cue sheet entry.
4. Collecting societies: if composers or lyricists are IPRS members, the performing right is assigned to the society and public performance is licensed through it (3P); for a film's soundtrack, check how the composer's society membership interacts with the producer's assignment (counsel).
5. Cue sheet: title, composer, publisher, society, duration, usage type, timing in the film; delivered with the film for royalty reporting.
6. Credits wording per licence terms (title-and-key-art titles-and-credits.md).
7. Register and file in `ledgers/music_licences/`; the editor does not lock sound without it.
Timeline and budget: ask for quotes before picture lock; sync fees vary widely by track, media and territory (E: no numbers are published here).

## 4. E&O (errors and omissions) insurance (3P, broker guides 2026; mostly US practice, confirm for India)
- Purpose: covers legal claims that the film infringes copyright, defames, invades privacy or similar. Many distributors, broadcasters and streamers require valid E&O before acquiring a film and often want to be named as an additional insured (3P).
- Typical terms quoted by brokers: limits from 1 million per claim and 3 million in aggregate, deductible often capped around 10,000, carrier rating B+ or better, coverage maintained for about 3 years after release (3P, US figures; U for India; terms vary by buyer).
- Bought after the film is complete and a lawyer has reviewed chain of title, music clearances, life-rights and releases; underwriters require a complete chain-of-title review and any errors found must be cured before coverage starts (3P).
- Underwriters ask for: copyright chain of title, script clearance (names, businesses, phone numbers, addresses), a title report, music clearances with streaming coverage, signed releases for everyone on screen, and in 2026 questions on AI-generated likenesses, voices and creative elements (3P).
- Cost: priced as a percentage of budget or a flat package; short films and low-budget films have lower quotes (E: obtain quotes from at least two brokers, India and international).
- India: availability and distributor demand may differ; ask the OTT or aggregator whether they require it and in what form (A).
Our rule: the producer asks the lawyer and a broker for quotes; the user decides and pays; agents never bind coverage.

## 5. Script clearance habits (cheap, prevents claims)
Use fictional names for characters, businesses, products, phone numbers, addresses and licence plates; check names against search results; avoid real brands and logos on screen; use fictional brands (no client brand in another film); pick a unique title and run a title check; avoid depicting living people without consent.

## 6. Cue sheet and licence register (CSV columns)
`cue_id, scene, tc_in, tc_out, title, type(original/library/licensed), composer, lyricist, publisher, label, society, licence_ref, media, territory, term, fee, signed_date, credit_text, status`
Producer owns the file; lawyer checks the licensed rows.
