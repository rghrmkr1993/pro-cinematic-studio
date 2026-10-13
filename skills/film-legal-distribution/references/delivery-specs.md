# Delivery specs by destination

Not legal advice. Specs change and are often shared only after onboarding; every row below must be re-checked against the live platform document or the aggregator's sheet before delivery. Labels: (F) from an official page read, (3P) secondary, (E) estimate, (A) assumption, (U) unverified. Master and mezzanine basics: film-studio delivery-and-legal.md sections 1 to 3.

## 1. Delivery package, general
Video master, text-free and textless elements, stems (dialogue, music, effects) and an M and E (music and effects) track for dubbing, 5.1 and stereo mixes if made, subtitle and caption files, poster and key art, trailer, stills, metadata sheet, closed captions or SDH, chain-of-title and rights documents, music cue sheet, credits list, QC report, loudness report, AI disclosure note.
Archive with checksums (SHA-256) and a manifest (production-tracking asset library).

## 2. Netflix (via the Partner Help Center; an approved path or aggregator is required)
- Netflix partner pages (read via search 2026-10-14, F where official): IMF packaging to SMPTE ST 2067-21 (Application 2E) for branded and original content; long-play, not split; timed text and extra audio dubs are delivered as secondary assets, not inside the IMF; Netflix recommends high-bit-depth image mezzanines (16-bit TIFF or 10 or 16-bit DPX at UHD or HD) for IMF creation; IMSC1.1 and TTML1 for timed text under the Netflix IMSC 1.1 Text Profile; subtitle events at least 5/6 s and at most 7 s, at most 2 lines (3P read of the Timed Text Style Guide; older pages, U).
- Non-branded spec (third-party copy, v9.3, U): IMF Application 2E and iTunes-packaged ProRes 422 HQ accepted for some deliveries. Check the official version.
- Loudness: dialogue-gated -27 LKFS with true peak -2 dBTP is the number in film-studio notes (3P); confirm in the current audio spec.
- Practical: independent films reach Netflix through a Netflix Preferred Fulfillment Partner, a sales agent or a distributor; a chain-of-title opinion letter and E&O are commonly required (3P). Plan an aggregator.

## 3. Amazon Prime Video (Prime Video Direct specs, older official pages, 3P read 2026-10-14, U for 2026)
- Codecs: H.264 High profile or ProRes 422 HQ in a .mov. H.264 in .mp4, .m2t or .ts; H.264 inside .mov not supported (3P).
- Bitrates: H.264 recommended 30 Mbps for HD (minimum about 20); ProRes 422 HQ about 220 Mbps for HD (3P).
- Keyframe interval 2 s or less; audio AAC or AC-3 for H.264, PCM for ProRes; 48 kHz; all tracks in one language per source; remove music-only, commentary and silent tracks (3P).
- Loudness: sources disagree (-24 to -26 LKFS in one third-party guide); no official Prime Video Direct figure was found (U). Check the help centre.
- Subtitles and captions: SRT, WebVTT or TTML, UTF-8 reported (3P); closed captions expected for English-language audio (3P, U).
- India: Prime Video in India accepts content through content partners and aggregators; direct availability for self-published films may be limited (A: ask).

## 4. YouTube
- Upload: MP4 H.264 High, closed GOP, AAC-LC 48 kHz, moov atom at the front; SDR 4K 24 to 30 fps about 35 to 45 Mbps; 1080p about 8 to 12 Mbps (3P, YouTube recommended encodings; verify).
- Loudness: normalised, with -14 LUFS as the working target; true peak -1 dBTP.
- Thumbnail: 1280x720, under 2 MB (title-and-key-art).
- Captions: upload SRT or VTT; Indic via UTF-8 with correct fonts at burn-in.
- AI: set "altered or synthetic content" when content is realistic and could be mistaken for a real person, place or event; unrealistic content, animation and routine production assistance do not need it (3P, YouTube policy summaries; official Help is the authority). Non-disclosure risks labels, removal or Partner Programme action.
- Premieres, chapters and end screens as marketing steps; publish only on the user's yes.
- Monetisation and reuse rules: re-check YouTube's current policies on AI and "inauthentic content" (U).

## 5. JioHotstar and other Indian OTT
- No public delivery specification found for JioHotstar (search 2026-10-14). Specs are normally shared under NDA after onboarding or through an aggregator (3P). Do not guess; ask for the platform's technical delivery sheet, content guidelines, artwork specs and metadata template.
- Typical asks across Indian OTT (A, generic): high-resolution master (ProRes or high-bit-rate H.264), 24 fps or as the platform states, stereo and 5.1 mixes, English subtitles plus regional subtitles, closed captions, poster and banner sets, synopsis, cast and crew, content advisory, genre keywords, trailer, chain-of-title and music licences, sometimes an E&O certificate or an indemnity clause, and self-declaration of content rating.
- Routes: direct acquisition team of the platform, a licensed aggregator, a sales agent, or a regional distributor. Compare fees, exclusivity, term and revenue splits with counsel.
- Platform context (3P): JioHotstar launched on 14 Feb 2025 combining JioCinema and Disney+ Hotstar and plans regional titles in Tamil, Telugu, Malayalam and others.
- Other Indian platforms (Sun NXT, Aha, ZEE5, SonyLIV, Manorama Max, and others): specs and acquisition rules differ; ask each (U).

## 6. Festivals
- Online screener: H.264 MP4 1080p at 8 to 20 Mbps, stereo, subtitles per the festival, watermark rules per the festival.
- Projection: DCP (2K Flat 1998x1080 or Scope 2048x858, 24 fps, 5.1 or stereo, Interop or SMPTE as the festival asks) or ProRes as stated; subtitles as a separate version file where possible. DCP basics in film-studio delivery-and-legal.md section 3.
- Test the file on a cinema server or lab before the festival date; keep an English subtitle file, a dialogue list and a poster and stills kit.
- A DCP lab quote and a test screening are spend items needing the user's yes.

## 7. QC (producer with continuity-supervisor)
Real-file checks: resolution, frame rate, duration, audio channels and layout, loudness (LUFS and true peak), black frames, A/V sync at start, middle and end, subtitle timing and character limits, credit spelling, text-free elements present, metadata. Record versions of tools and the date; keep the QC report with the delivery.

## 8. Metadata sheet (fields)
Title and local titles (all scripts), logline, short and long synopsis, genres, languages (audio, subtitle), country, year, runtime, rating or intended rating, cast and crew with roles, AI-use statement, music credits, rights holder, copyright line, contacts, key art files, trailer link, awards and festival laurels (only real ones).
