# Sources (accessed 2026-10-13; paraphrased; no lyrics reproduced)

Labels: F official or standards, 3P third-party and subject to change, E general craft knowledge without a single source. Re-check tool terms live before spending credits or shipping.

## AI music and sound tools
- ElevenLabs Music overview (models music_v2 and music_v2_5, 3 s to 10 min, MP3 export, reference audio limit, vocal languages listed): https://elevenlabs.io/docs/eleven-creative/products/music (F)
- ElevenLabs composition plans (chunks, positive_styles, negative_styles, duration_ms): https://elevenlabs.io/docs/eleven-api/guides/how-to/music/composition-plans (F)
- ElevenLabs help center, best practices for prompting Eleven Music: https://help.elevenlabs.io/hc/en-us/articles/37781425844369-Are-there-any-best-practices-for-prompting-Eleven-Music (page returned 403 to the fetch tool; points taken from search summary only, 3P)
- ElevenLabs Music v2 practical guide (credits per minute, stems cost, licence notes, weaknesses): https://www.gradually.ai/en/elevenlabs-music/ (3P)
- ElevenLabs Sound effects product guide: https://elevenlabs.io/docs/eleven-creative/playground/sound-effects (F); third-party prompt guides: https://fuser.studio/articles/elevenlabs-sound-effects-guide, https://aiproductivity.ai/guides/elevenlabs-sound-effects-guide/ (3P)
- Higgsfield audio: https://higgsfield.ai/blog/higgsfield-audio (3P/vendor marketing; sources conflict on standalone music and SFX)
- Field test 2026-10-13: owner judgement on ElevenLabs Music v2.5 Tamil vocals and Tamil TTS (eleven_v4, eleven_v3): robotic (FT, internal).

## Loudness and mixing
- EBU R 128 (-23 LUFS +/- 0.5, true peak -1 dBTP): https://en.wikipedia.org/wiki/EBU_R_128 and https://www.forasoft.com/learn/audio-for-video/glossary/terms-audio/ebu-r128 (F summaries; primary spec at tech.ebu.ch)
- AES TD1004 streaming loudness (-16 to -20 LUFS recommended window, 2015) as reported in https://production-expert.com/production-expert-1/loudness-everything-you-need-to-know and https://apu.software/loudness-standards/ (3P summaries; primary AES document not fetched)
- iZotope EQ cheat sheet (instrument frequency ranges, dynamic EQ with sidechain): https://www.izotope.com/en/learn/eq-cheat-sheet.html and https://www.izotope.com/en/learn/5-ways-to-use-dynamic-eq-with-sidechain.html (F as vendor guidance)
- Sonicbids 2026 EQ guide: https://sonicbids.com/blog/eq-cheat-sheet-mixing-frequencies-by-instrument/ (3P)
- Sound on Sound guides were searched but not fetched; mixing ratio and timing values in mixing-and-mastering.md are E.
- Platform loudness table and ffmpeg loudnorm: internal `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/sound-music-voice.md` and `editing-and-assembly.md`.

## Film scoring
- Berklee Online Film Scoring 101 and Film Score Analysis (spotting, ins and outs, hit points, source music, thematic variation): https://online.berklee.edu/courses/film-scoring-101 and https://online.berklee.edu/courses/film-score-analysis (F course outlines)
- Complete Guide to Film Scoring, Davis and Plante, Berklee Press (core text): https://www.halleonard.com/product/1450038/complete-guide-to-film-scoring-3rd-edition (F)
- Cue sheet formats: not fetched; the template in film-scoring.md section 12 is E. Check the local performing-rights society format before filing.

## Indian and Tamil music
- Melakarta (72 scheme, chakras, katapayadi): https://en.wikipedia.org/wiki/Melakarta and https://artiumacademy.com/blogs/melakarta-ragas-in-carnatic-music/ (F and 3P)
- Kalyani: https://en.wikipedia.org/wiki/Kalyani_(raga); Hindolam: https://en.wikipedia.org/wiki/Hindolam; Shivaranjani: https://en.wikipedia.org/wiki/Shivaranjani; Kapi: https://en.wikipedia.org/wiki/Kapi_(raga); Mohanam and Kalyani overview: https://www.acharyanet.com/mohanam-and-kalyani-my-favourite-ragas/ (F structure; mood labels are traditional and subjective)
- Hindustani thaats, raga times, teental: https://en.wikipedia.org/wiki/Bhoopali, https://en.wikipedia.org/wiki/Bhimpalasi, https://en.wikipedia.org/wiki/Malkauns, https://en.wikipedia.org/wiki/Todi_(raga) (F summaries)
- Tamil film music eras and Kollywood indie and gaana: https://www.spardhaschoolofmusic.com/blog/top-tamil-music-directors, https://www.esplanade.com/offstage/arts/musicians-shaking-up-kollywoods-indie-scene, https://en.wikipedia.org/wiki/Music_of_Tamil_Nadu, https://en.wikipedia.org/wiki/Indian_film_music (3P; used for era sound only; composers deliberately not named in prompts)
- Tamil folk forms (therukoothu, oppari, villupattu, kuthu, naattupura paattu), devotional forms, Bollywood, Malayalam, Telugu, Kannada traits: E from general knowledge; not individually sourced in this build; have a native reviewer verify before client-facing use (U).

## Music theory
- Scales, modes, progressions, meter, forms: standard theory (E and F, textbook level; Berklee and general music-theory references). No single page sourced; claims are common to all textbooks.

## Gaps and next checks
- Tamil vocal support in ElevenLabs Music is not documented; field test says robotic. Re-test after model releases.
- AES TD1004 primary text, EBU R128 primary text, ElevenLabs Music Terms page (artist-name rule and film/TV exclusion) should be read in primary form before a client delivery.
- Sound on Sound and Berklee guides for ducking numbers and cue sheet layout were not fetched.

## 2026-10-14 additions (deep Carnatic and vocal research via web search summaries; 3P, paraphrased)
- Kattai mapping and ranges: rasikas.org threads (male vs female sruti), regionalkaraoke.com sruthi guide; one Artium Academy page contradicts them (U).
- Gamaka types: Wikipedia Gamaka and Glossary of Carnatic music, G. Swift ornamentation and violin article (carnaticcorner.com), carnaticmusicexams.wordpress.com Panchadasa Gamakas; definitions differ (U).
- Tala 35 and 175 schemes: acharyanet.com, carnaticmusicexams.in, mridangams.com chart.
- Nadaswaram: Wikipedia, carnatica.net, sembanarkovilbrothers.com; reed material and base pitch differ (U).
- Carnatic violin tuning and posture: sruti.com, maddy06 blog, SAPA India guide.
- Ghatam, kanjira, morsing: Wikipedia Ghatam and Kanjira, ipassio, spardhaschoolofmusic.
- Harmonium and the All India Radio ban 1940 to 1971: Rahaim (Experts@Minnesota), Outlook India, Heritage Times; mostly Hindustani (U for Carnatic).
- Parai, oppari, thappu, urumi, udukkai, pambai, kombu: Wikipedia (Urumi, Udukai, Tharai, Paraiyar), The Better India, The Federal, ResearchGate oppari paper; origin accounts differ (U).
- Vocal science: voicescience.org (Singer's Formant, Vibrato, Voice Classification), PMC9605961, PMC12370702.
- Tamil phonology and zha: Wikipedia Tamil phonology, arXiv 1001.4190, arXiv 2604.25476.
- Singer technique: outstandingkerala.com profile (journalistic), course pages. No first-hand masterclass found (gap).
