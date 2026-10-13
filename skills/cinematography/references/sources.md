---
name: cinematography
description: "Sources and evidence labels for the cinematography skill: lens makers, ASC and film-school vocabulary, DP interviews, and AI video camera-prompt guides for Higgsfield, Seedance, Kling, Veo and Runway, with research date and known gaps. Part of the cinematography skill."
---

# Sources and evidence log
Researched 2026-10-13 with web search and page fetches. Content is paraphrased. Labels: (V) vendor-official, (3P) third-party guide, rental house or practitioner article, (K) established craft knowledge not tied to one source, unverified items were resolved on 2026-10-14 (see below). Treat model-specific behavior as a starting point: models and versions change fast; re-test.

## AI video camera prompting
| Source | URL | Used for | Label |
|---|---|---|---|
| Google Cloud, Ultimate prompting guide for Veo 3.1 | https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1 | Formula, vocabulary, first and last frame, ingredients, audio cues, limits | V |
| Runway, AI video prompting guide | https://runway.com/resources/ai-video-prompting-guide | Plain English, one move, positive phrasing, vocabulary, formula | V |
| Higgsfield, How to control camera movement, angles and lens in AI video | https://higgsfield.ai/blog/ai-video-camera-control | Start, end, speed curve, explicit prompt, presets | V |
| Higgsfield Prompt Bank | https://higgsfield.ai/academy/apps/prompt-bank | Speed and easing phrasing | V |
| Higgsfield, Kling 3.0 on Higgsfield | https://higgsfield.ai/blog/Kling-3.0-is-on-Higgsfield-User-Guide-AI-Video-Generation | Start and end frame use | V |
| Kling, AI camera control and movement prompts guide | https://kling.ai/blog/ai-camera-control-movement-prompts-guide | Supported camera options, speed descriptors, modes (partly promotional) | V |
| Kling 3.0 guides: Atlabs, glif, ambienceai, stevenvideo, videoai.me | https://www.atlabs.ai/blog/kling-3-0-prompting-guide-master-ai-video-generation and others | One-move rule, multi-shot timing, orbit limits | 3P |
| Seedance 2.0 guides: promeai, clipdance, seedance.tv, apiyi, sirioberati, cuty | https://www.promeai.pro/blog/seedance-2-0-camera-movement-cheat-sheet/ and others | Camera vocabulary, five cues, move-to-size matching, conflicting stacking advice | 3P |
| Veo 3.1 third-party: VEED, Visla, invideo, GeeLark | https://www.veed.io/learn/veo-3-1-prompts | Lead with camera, lens by effect | 3P |
| Runway Gen-4 third-party tests: genape, filmart, crepal | https://filmart.ai/runway-gen-4-prompts/ | Orbit drift, handheld jitter | 3P |
| prompt-architects camera vocabulary | https://prompt-architects.com/blog/211-camera-movement-vocabulary-for-ai-video-30-terms | Move vocabulary | 3P |
Existing internal references reused, not duplicated: `higgsfield-master/references/cinema-studio.md`, `signature-shots.md`, `visual-language.md` (V and H, dated 2026-10-13); `graphics-rendering/references/lighting-setups.md`; `motion-animation/references/mechanics-animation.md`.

## Shot vocabulary and craft
| Source | URL | Used for | Label |
|---|---|---|---|
| StudioBinder, shot sizes, camera angles, shot list templates | https://www.studiobinder.com/blog/types-of-camera-shots-sizes-in-film/ and https://www.studiobinder.com/camera-shots/camera-angles/ | Size ladder, angles, shot list columns | 3P |
| MasterClass, 180-degree rule | https://www.masterclass.com/articles/understanding-the-180-degree-rule-in-cinematography | 180 and continuity | 3P |
| Frame.io Insider, 180-degree rule | https://blog.frame.io/2016/08/01/180-degree-rule-and-when-to-break-it/ | Breaking the rule | 3P |
| Filmmakers Academy glossary, eyeline match | https://www.filmmakersacademy.com/glossary/eyeline-match/ | Eyeline | 3P |
| Wikipedia, 180-degree rule, Continuity editing, Dolly zoom, Whip pan | https://en.wikipedia.org/wiki/180-degree_rule | 30-degree rule, dolly zoom, whip pan | 3P |
| ASC, Shot Craft: Deep Focus Diopters | https://theasc.com/article/shot-craft-deep-focus-diopters/ | Split diopter | 3P (trade magazine) |
| No Film School, split diopter | https://nofilmschool.com/split-diopter-shot | Split diopter | 3P |
| Screenweaver, film techniques | https://www.screenweaver.ai/film-techniques | Technique index | 3P |

## Lenses, exposure, frame rate
| Source | URL | Used for | Label |
|---|---|---|---|
| Cooke, Spherical vs anamorphic; Introduction to anamorphic | https://cookeoptics.com/news-and-events/spherical-vs-anamorphic-lenses/ | Squeeze, bokeh, edge behavior | V (lens maker) |
| Art Adams, Three lenses (ProVideo Coalition) | https://www.provideocoalition.com/three-lenses-a-look-at-bokeh-depth-of-field-and-geometry/ | Same DOF, different bokeh | 3P (practitioner) |
| ShareGrid, ARRI/Zeiss Master Anamorphic | https://www.sharegrid.com/learn/lens-sets/arri-zeiss-master-anamorphic | Low-distortion anamorphic, flare tints | 3P (rental house, promotional) |
| Cooke, Wes Anderson and Robert Yeoman | https://cookeoptics.com/news-and-events/wes-anderson-and-robert-yeoman-asc-straight-shooting-imagineers/ | Symmetry, anamorphic, centered setup | V (lens maker) |
| DIY Photography, DFI Rentals, PolarPro, Wit and Folly on 180-degree shutter | https://www.diyphotography.net/180-degree-shutter-rule/ | Shutter angle, 120 fps | 3P |
ARRI Alexa Mini LF specs were fetched from arri.com on 2026-10-14; Alexa 65 specs from ARRI Rental via search; Alexa 35 17-stop claim from the ARRI brochure and CineD.

## Color, stocks
| Source | URL | Used for | Label |
|---|---|---|---|
| Kodak Vision3 500T 5219 data sheet | https://www.kodak.com/content/products-brochures/Film/VISION3_5219_7219_Technical-data.pdf | Stock traits, remjet | V |
| Kodak Vision color print film 2383 | https://www.kodak.com/en/motion/product/post/print-films/vision-color-2383-3383/ | Print stock | V |
| Cullen Kelly colorist notes, FilmConvert, analog.cafe | https://cullenkellycolor.com/genesis | Contrast comparisons, halation | 3P (subjective) |
| Fuji Eterna, Portra, Ektachrome descriptions | none fetched | Stock traits | K (resolved 2026-10-14: Kodak sheets for Portra 400 and Ektachrome E100 confirmed; Fuji Eterna from retailers and forums only) |

## Lighting and DPs
| Source | URL | Used for | Label |
|---|---|---|---|
| Roger Deakins coverage: The Reveal, Backstage, British Cinematographer, Filmustage | https://thereveal.film/interview-roger-and-james-deakins-on-cinematography-and-navigating-a-changing-film-world/ | Motivated light, cove light, simplicity, handheld presence | 3P (interview summaries; one quoted line is in a secondary source) |
| Ava Berkofsky ASC, Insecure interviews (Mic, British Cinematographer, DIY Photography) | https://britishcinematographer.co.uk/ava-berkofsky-asc-insecure/ | Dark skin tones: exposure, reflectance, no formula | 3P |
| Bradford Young lighting claims | https://www.guerrillawolf.com/journal/mastering-the-art-of-lighting-black-skin-in-cinematography | Selma lighting blog summary | 3P (The Stranger, CBC and the ASC Camerimage interview confirm the low-light, reflective approach; no exposure figures published in them, 2026-10-14) |

## Indian cinema and regional looks
| Source | URL | Used for | Label |
|---|---|---|---|
| Scroll, Santosh Sivan on Mani Ratnam collaboration | https://scroll.in/reel/873987/santosh-sivan-on-his-lengthy-collaboration-with-mani-ratnam-every-film-is-different | Sun simulation with mirrors and tungsten, practical tricks | 3P (interview) |
| Behindwoods, Santosh Sivan and Ravi K Chandran interviews | https://www.behindwoods.com/tamil-cinematographer/santosh-sivan/an-exclusive-interview-with-padma-shri-santosh-sivan-part-2.html | Rain, sky, natural light | 3P |
| Wikipedia, Cinematic style of S. S. Rajamouli; K. K. Senthil Kumar | https://en.wikipedia.org/wiki/Cinematic_style_of_S._S._Rajamouli | Epic scale, classical approach, large soft night sources | 3P |
| Rolling Stone India, Malayalam cinema visual treat; Film Companion | https://rollingstoneindia.com/malayalam-cinema-visual-treat-cinematography-drishyam-kumbalangi-nights/ | Naturalistic Malayalam look | 3P |
| Grokipedia, Ravi K. Chandran / Indian cinematographers | https://grokipedia.com/page/Ravi_K._Chandran | Tamil realism, Bollywood gloss (single weak source, corroborated only by Wikipedia profiles of Sivan and Sreeram, 2026-10-14) | 3P weak |
Korean drama look: forum, listicle and blog sources only (Dramabeans, Tatler Asia, KOU, In Depth Cine on Chung-hoon Chung); no professional DP analysis found on 2026-10-14, so treated as tendency. Anime look: knowledge only (K).

## Known gaps
- Resolved 2026-10-14: Kodak sheets confirmed for 5219, 5207, Portra 400 and Ektachrome E100; Fuji Eterna has only retailer and forum descriptions because Fujifilm stopped motion picture film in 2013 (checked: Fujifilm Eterna manual PDF, ShotOnWhat, cinematography.com).
- Resolved 2026-10-14 for ARRI and Vantage Hawk (maker pages read); Zeiss and Panavision look claims stay with 3P tests (Art Adams, ShareGrid), described as tendencies.
- Model behaviors (dolly zoom, snorricam, rack focus, FPV): no independent test exists as of 2026-10-14; checked Runway guide, Atlabs, screenweaver, imaginode. Run a 3-variant house test per model.
- Regional Indian looks and Korean drama looks: tendencies, source-limited; marked in `director-styles.md` and `color-and-look.md` with checked-source lists.
- No ASC magazine article was read in full; ASC coverage used: the diopter Shot Craft page via search summary.
- Pricing, credits and model version availability change; confirm in the tool.
- Higgsfield 4.0 limits (30 s, 50 refs, 1080p) re-verified on 2026-10-14 against higgsfield.ai/blog/cinema-studio-4-0 and the Cinema Studio help center page. Prompt character cap: see `prompt-compression.md`.

## Added 2026-10-14 (resolution of unverified items)
| Source | URL | Used for | Label |
|---|---|---|---|
| ARRI Alexa Mini LF | https://www.arri.com/en/camera-systems/cameras/alexa-mini-lf | 36.70 x 25.54 mm, 14+ stops | V |
| ARRI Rental Alexa 65 and CineD camera database | https://www.arrirental.com/en/cameras/digital-65-mm-cameras/alexa-65 | 54.12 x 25.58 mm, 6560 x 3100 | V and 3P |
| CineD lab tests (Alexa 35, Venice 2, URSA Cine 12K LF, C300 III) | https://www.cined.com/arri-alexa-35-lab-test-rolling-shutter-dynamic-range-and-latitude-plus-video/ | Independent dynamic range | 3P lab |
| Film Atlas, GCM Studio, Kodak Film Format PDF, The Pixel Farm | https://www.filmatlas.com/entry/244 | IMAX 15/70 and 65mm frame sizes | 3P and V |
| Forbes and Hollywood Reporter on Filmed for IMAX | https://www.forbes.com/sites/bennyhareven/2020/09/18/new-filmed-in-imax-programme-promises-to-usher-in-full-frame-aspect-ratio-era/ | IMAX digital 1.90 and 1.43 | 3P |
| Vantage Film Hawk V-Lite; B&H Atlas Orion; Wolfcrow Orion review | https://www.vantagefilm.com/en/products/hawk-1-3x/v-lite | Anamorphic specs | V and 3P |
| ProVideo Coalition, Art Adams lens comparisons; StudioBinder Cooke | https://www.provideocoalition.com/four-lenses-a-visual-comparison-part-2/ | Cooke versus Zeiss summary | 3P |
| DPReview, DXOMARK, GSMArena, Apple support | https://support.apple.com/en-by/125090 | Phone sensors and lenses | V and 3P |
| Fujifilm, Nikon, Canon, Sony pages via Newsshooter, CineD, DPReview | https://www.nikonusa.com/p/z-8/1695/overview | X100VI, Z8, Z9, A1 II, R5 II | V and 3P |
| Higgsfield blog Cinema Studio 4.0 and Seedance 2.5 guide | https://higgsfield.ai/blog/cinema-studio-4-0 | Long official prompts, 24 fps, limits | V |
| Gemini API Veo docs; Nano Banana Pro model page; Runway Gen-4 guide | https://ai.google.dev/gemini-api/docs/veo | Prompt limits, 24 fps, negatives | V |
