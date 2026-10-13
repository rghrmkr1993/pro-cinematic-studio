# Sources and confidence (researched 2026-10-14)

Labels: (V) vendor-official, (P) primary document or standard, (3P) third-party article or blog, (L) local test. Vendor blogs are marketing; numbers are claims. Re-check before relying on any spec, price or law.

## AI film production
- (3P, V-blog) Higgsfield, How to Make a Short Film With AI, full pipeline: https://higgsfield.ai/blog/ai-short-film-pipeline (15 to 25 shots for 2 min, 8 s 720p and 15 s 1080p clips, credits per step, 5 min example about 3,000 credits)
- (3P, V-blog) Higgsfield, How to Make an AI Animated Short Film: https://higgsfield.ai/blog/ai-animated-short-film-2026 (style locking, sheets per style, Cinema Studio 4.0 up to 30 s and 50 references)
- (3P, V-blog) Higgsfield script to storyboard: https://higgsfield.ai/blog/script-to-storyboard-ai ; previsualization tools: https://higgsfield.ai/blog/ai-previsualization-tools (Popcorn 4, 6 or 8 frames)
- (3P) CineD, Hell Grind: https://www.cined.com/hell-grind-the-95-minute-ai-feature-cannes-2026-says-it-never-screened/ ; Wikipedia Hell Grind: https://en.wikipedia.org/wiki/Hell_Grind ; itsbetterwithai breakdown: https://itsbetterwithai.com/i/ai-feature-film-cannes/ (15 people, 14 days, 3 to 4 kept per 20, long prompts, editing director). "First AI feature" claims are contested.
- (3P) Variety, Tribeca and Dreams of Violets: https://variety.com/2026/film/festivals/tribeca-festival-ai-film-dreams-of-violets-fountain-0-1236759724/ (75 min, three months, about 2,000 USD, company-stated)
- (3P) ImagineArt AI filmmaking guide: https://www.imagine.art/blogs/ai-filmmaking-guide ; model comparisons: https://www.buildfastwithai.com/blogs/seedance-2-5-vs-veo-3-1-vs-kling-3-0-best-ai-video-2026 ; https://www.screenweaver.ai/blog/kling-3-vs-seedance-2 (specs differ across sources, verify on tool)
- Local skills read: creative-studio, higgsfield-master (SKILL.md, workflows.md, production-pipeline), photoreal-humans, asian-human-reference, seedance-20, motion-reel, cinematography.

## Screenwriting
- (3P) Save the Cat 15 beats and pages: https://www.screenweaver.ai/blog/save-the-cat-15-beats-page-numbers ; https://novela.so/en/blog/save-the-cat-beat-sheet (Catalyst page 10 or 12 varies)
- (3P) Hero's Journey 12 stages: https://www.storyflint.com/blog/heros-journey-christopher-vogler ; Vogler, The Writer's Journey (book, not read)
- (3P) Eight sequences: https://thescriptlab.com/screenwriting/structure/the-sequence/45-the-eight-sequences/ ; https://www.finaldraft.com/blog/8-sequence-structure-the-best-kept-screenwriting-secret ; Gulino, Screenwriting: The Craft of the Sequence Approach (book)
- Screenplay format specifics (margins, Courier 12) are industry convention from general knowledge (A), not re-verified in 2026.

## Editing, colour, sound
- (L) ffmpeg 9.0.1 (gyan.dev build) recipes run 2026-10-14: concat demuxer, xfade plus acrossfade, loudnorm two pass, subtitles burn, mov_text soft sub, MKV srt, srt to vtt, lut3d with a .cube, adelay J-cut, sidechaincompress with amix, image loop animatic, drawtext with fontfile, last-frame grab, blackdetect and silencedetect, ProRes 422 HQ.
- (P) ffmpeg filters documentation: https://ffmpeg.org/ffmpeg-filters.html (acrossfade options read; xfade and loudnorm option lists read with `ffmpeg -h filter=` locally)
- (3P) Loudness standards: https://www.production-expert.com/production-expert-1/loudness-everything-you-need-to-know ; https://www.forasoft.com/learn/audio-for-video/articles-audio/loudness-normalization-ebu-r128-bs1770-atsc-a85 (ATSC A/85 -24 LKFS -2 dBTP, EBU R128 -23 LUFS -1 dBTP, Netflix -27 LKFS dialogue-gated, YouTube about -14 LUFS unofficial). Verify against EBU R128, ATSC A/85 and Netflix sound specs.
- (3P) Colour and LUT practice: general craft knowledge (A); no single source.

## Music, voice, dubbing
- (3P) AI music licensing: https://blog.dubspot.com/ai-music-licensing-explained-2026 ; https://www.musicbusinessworldwide.com/warner-music-group-settles-with-suno-strikes-first-of-its-kind-deal-with-ai-song-generator/ ; https://dynamoi.com/learn/ai-music-distribution/ai-music-copyright-cases-timeline (settlements, ongoing UMG and Sony cases, conflicts between sources)
- (3P) Dubbing tools: https://www.heygen.com/blog/best-ai-dubbing-tools (vendor ranking itself first) ; https://elevenlabs.io/docs/overview/capabilities/dubbing (V, 90 plus languages, audio dubbing; Dubbing Studio in maintenance mode) ; Tamil and Telugu support not confirmed.

## Subtitles
- (V) Netflix Timed Text Style Guides: https://partnerhelp.netflixstudios.com/hc/en-us/articles/219375728-Timed-Text-Style-Guide-Subtitle-Templates ; Hindi https://partnerhelp.netflixstudios.com/hc/en-us/articles/115003196707-Hindi-Timed-Text-Style-Guide ; Tamil https://partnerhelp.netflixstudios.com/hc/en-us/articles/4481912003987-Tamil-Timed-Text-Style-Guide ; Telugu https://partnerhelp.netflixstudios.com/hc/en-us/articles/4482320288787-Telugu-Timed-Text-Style-Guide ; Kannada https://partnerhelp.netflixstudios.com/hc/en-us/articles/4482685308819-Kannada-Timed-Text-Style-Guide (search summaries only; pages not opened; Malayalam and Bengali figures not retrieved)
- (3P) 42 characters, 2 lines, 5/6 s to 7 s, 17 to 20 cps: https://subtitlesedit.com/blog/netflix-subtitle-guidelines-line-length-characters

## Delivery and legal
- (3P) DCP specs: https://c-istudios.com/essential-dcp-technical-specifications-every-filmmaker-should-know/ ; https://en.wikipedia.org/wiki/Digital_Cinema_Package ; https://artdocfest.com/en/content/technical-requirements/ (Interop vs SMPTE disagreement noted)
- (3P) YouTube encoding: https://swarmify.com/blog/what-you-need-to-know-about-the-video-bitrate/ ; disclosure policy summaries: https://influencermarketinghub.com/ai-disclosure-rules/ ; https://ytzolo.com/blog/youtube-altered-synthetic-content-policy-2026/ (YouTube Help not opened)
- (3P) Copyright Office Part 2 (Jan 2025): https://www.jonesday.com/en/insights/2025/02/copyrightability-of-ai-outputs-us-copyright-office-analyzes-human-authorship-requirement ; primary at copyright.gov (not opened)
- (3P) India IT Rules amendment 2026: https://www.legal500.com/intelligence/india/media-telecoms-it-entertainment/2026-it-rules-amendments-ai-content-labelling-and-intermediary-obligations ; https://www.lexology.com/library/detail.aspx?g=adb2714c-1188-43e3-b62b-eb6649727f6e (law-firm summaries; gazette G.S.R. 120(E) not opened)
- (P/3P) CBFC: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2014950 (Certification Rules 2024) ; https://cbfcindia.gov.in/cbfcAdmin/film-certification-process.php ; PIB Feb 2026 release on e-Cinepramaan timings: https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2227704&reg=3&lang=2 ; portal ecinepramaan.cbfcindia.gov.in
- (3P) Festival and Oscar AI rules: https://deadline.com/2026/05/oscar-rules-changes-2026-acting-international-film-1236878201/ ; https://dancefilmperformance.com/mag/festivals-and-ai-generated-film/ ; https://blog.promise.legal/ai-generated-content-film-legal-compliance-2026/ (secondary; read the rulebook)

## Not researched (gaps)
Primary YouTube Help, EBU, ATSC, Netflix sound spec pages; US Copyright Office PDF and Part 3; Indian copyright law on AI works; SAG-AFTRA and Indian union rules; Runway and Luma long-form workflows (search returned no detailed case); real-time breakdowns with retake rates and budgets beyond press claims; Malayalam and Bengali subtitle limits; Indian-language TTS and lipsync quality per tool; period-research source lists per era; DCP tool licences. Treat these as open items for the next scan.
