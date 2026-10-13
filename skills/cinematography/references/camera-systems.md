---
name: cinematography
description: "Camera systems for AI prompting: cinema, film and photography cameras with sensor or film format, look signature, and how to name them in prompts. Includes evidence on whether AI models respond to camera names. Part of the cinematography skill."
---

# Camera systems
Labels: (V) manufacturer or retailer spec page, (3P) review or practitioner, (K) established craft. Researched 2026-10-13, all open items resolved 2026-10-14 (each fact carries a [verified ...] tag or a no-source marker). Sensor figures are nominal and differ by recording mode; confirm on the maker page before quoting them to a client.

## Do AI models respond to camera names?
- No controlled A/B test was found in the 2026 guides. Prompt libraries use "shot on ARRI Alexa 65 with Zeiss Supreme Prime 35mm" and "ARRI Alexa with Panavision C-series anamorphic" in cinematic tests, but none compare with and without the phrase (3P, medium.com prompt list, clipia.ai comparison). Both are promotional. [no public source as of 2026-10-14 for a controlled with/without test; checked: PromptHero, MeiGen, zsky.ai, clipia, medium prompt lists, web search for matched-prompt experiments. Only anecdote exists, and the prompts also stack grain, anamorphic and grade words that confound any camera-name effect]
- Working view (H): a body name is a style token. It nudges colour, softness and depth of field toward the footage the model saw captioned that way. It does not simulate a sensor.
- Camera movement, framing, lens mm and light direction change results more predictably than body brand (3P guides; Higgsfield blog 2026-10-09, V).
- House test before relying on a name: same seed, same prompt, with and without the name, 3 draft clips each. Log the result in shot-list notes.
- On Higgsfield Cinema Studio keep body and lens in the Camera panel (Modern, 35mm Film, 8mm Film, DV Camcorder), not in the prompt text (V).
- Rule: name at most one body plus one lens plus one stock. Stacking three brands adds noise.

## Cinema cameras (digital)
| Camera | Sensor and format | Look signature | Prompt token |
|---|---|---|---|
| ARRI Alexa 35 | Super 35, 27.99 x 19.22 mm open gate, 4.6K, 17 stops claimed (V, ARRI via CineD) | REVEAL colour science, LogC4, gentle highlight roll-off, natural skin; the "ARRI look" is tonality and skin more than sharpness (3P) | "shot on ARRI Alexa 35, soft highlight roll-off, natural skin" |
| ARRI Alexa Mini LF | Large format open gate 36.70 x 25.54 mm, 4448 x 3096, 14+ stops claimed; CineD measured 13.4 stops at SNR 2 (V ARRI; 3P CineD) [verified arri.com Alexa Mini LF page, 2026-10-14] | Large-format falloff, smooth, wide field | "ARRI Alexa Mini LF, large format, shallow smooth falloff" |
| ARRI Alexa 65 | 65mm-class open gate 54.12 x 25.58 mm, 6560 x 3100, over 14 stops claimed (V ARRI Rental; 3P CineD database) [verified arrirental.com Alexa 65 and cined.com camera database, 2026-10-14; one source gives 25.59 mm height and 3102 rows, rounding only] | Epic scale, huge depth falloff, painterly | "ARRI Alexa 65, vast scale, creamy falloff" |
| RED V-Raptor 8K VV | 40.96 x 21.6 mm, 8192 x 4320, rolling shutter (V) | Crisp, high resolution, punchy; sharpness-first reputation (3P) | "shot on RED V-Raptor, crisp high-resolution" |
| RED Komodo 6K | Super 35, 27.03 x 14.26 mm, global shutter (V) | Compact, clean, no skew on fast pans; used for crash and action cams | "RED Komodo, clean sharp, no rolling shutter" |
| Sony Venice 2 | Full frame 8.6K (8640 x 5760), dual base ISO 800 and 3200, 16 stops (V Sony) | Clean, neutral and rich; very clean low light at 3200; S-Cinetone is built on its colour (V) | "Sony Venice 2, clean low-light, rich neutral colour" |
| Sony FX9 / FX6 / FX3 | Full frame; FX3 sensor 35.6 x 23.8 mm; dual base or dual native ISO (V, 3P) | S-Cinetone: soft skin, pleasing contrast; run-and-gun and documentary feel | "Sony FX3, S-Cinetone, handheld documentary" |
| Canon C300 III / C70 | Super 35, DGO sensor, 26.2 x 13.8 mm on C300 III, 16+ stops claimed (V) | Warm, kind skin, Canon Log 2 and 3; documentary and commercial staple (3P) | "Canon cinema camera, warm skin, soft contrast" |
| Canon C500 II | Full frame 5.9K, non-DGO (V) | Large-format option, Canon colour | "Canon C500 II full frame" |
| Blackmagic URSA Cine 12K LF | Full frame 35.64 x 23.32 mm, RGBW 12K, 16 stops claimed (V) | Very high resolution, clean, malleable | "Blackmagic URSA Cine, high-resolution, clean" |
| Blackmagic Pyxis 6K | Full frame 36 x 24 mm, dual native ISO 400 and 3200 (V) | Small body, filmic default | "Blackmagic Pyxis, filmic full frame" |
| IMAX digital (Alexa IMAX, Venice-based) | IMAX-certified digital cameras (Alexa LF, Mini LF, Alexa 65, Venice 1 and 2, V-Raptor, DXL2 and others) shoot 1.90:1 for most digital IMAX screens and 1.43:1 for some dual-laser scenes (3P Forbes, Hollywood Reporter, In Depth Cine) [verified forbes.com 2020-09-18 and hollywoodreporter.com, 2026-10-14] | Huge, immersive, tall frame | "IMAX digital, tall 1.9:1 frame" |
Dual base or native ISO: two circuits, one for bright scenes and one for low light, so night footage stays clean (see `exposure-and-settings.md`).

## Film cameras and formats
| Format or body | Frame size | Look | Prompt token |
|---|---|---|---|
| Super 8 | about 5.8 x 4.0 mm (K) | Heavy grain, gate weave, soft, home-movie warmth | "Super 8 home movie, gate weave, heavy grain" |
| 16mm, Super 16 (ARRI SR3, Aaton XTR) | Super 16 about 12.5 x 7.4 mm (K); SR3 is a Super 16 body (V Panavision) | Visible grain, texture, indie and documentary | "Super 16 grain, soft, organic" |
| 35mm 4-perf (ARRICAM ST and LT, Panavision Millennium XL2) | ARRICAM aperture 0.980 x 0.735 in, about 24.9 x 18.7 mm (V); Millennium XL2 shoots 3 or 4 perf, up to 50 fps (V) | Fine grain, classic cinema | "35mm film, fine grain, 4-perf" |
| 65mm 5-perf | 52.48 x 23.01 mm (Pixel Farm) or 52.15 x 23.07 mm (Kodak infographic), 2.20:1; the two sources differ by under 0.4 mm (V Kodak, 3P) [verified kodak.com Film-Format-Choices PDF and thepixelfarm.co.uk, 2026-10-14] | Rich detail, epic scale | "shot on 65mm film, epic detail" |
| IMAX 15/70 | 70mm wide, 15 perforations per frame, horizontal run; camera aperture 70.41 x 52.63 mm (about 1.34:1), projected frame about 69.6 x 48.5 mm, nominal 1.43:1 (3P Film Atlas, GCM Studio) [verified filmatlas.com and gcmstudio.com, 2026-10-14] | Giant, immersive. "18K equivalent" is a peak or marketing figure; the informal best-case average is about 12K and no MTF measurement is published [no public source for a measured value as of 2026-10-14; checked: IMAX, In Depth Cine, Bohring, forum analyses] | "IMAX 15/70 film, tall 1.43:1 frame" |
Film negative is the base for stock looks: see `color-and-look.md`.

## Photography cameras
| Camera | Sensor | Look signature | Prompt token |
|---|---|---|---|
| Leica M11, Q3 | 60 MP full frame BSI; Q3 has fixed Summilux 28 mm f/1.7 (V B&H) | "Leica look" is subjective: lens rendering plus colour profiles [no public source for a measurable definition as of 2026-10-14; checked: Leica product pages, DXOMARK M11 test (measures sensor DR only), review sites]. Rangefinder street feel, gentle contrast, pleasing tonality | "Leica M, 35mm Summilux, street photograph, natural tonality" |
| Hasselblad X2D 100C, 907X + CFV 100C | 43.8 x 32.9 mm, 100 MP, 16-bit colour, HNCS (V Hasselblad) | Natural colour, smooth gradation, wide tonal range, editorial | "Hasselblad medium format, natural colour, smooth tonal gradation" |
| Fujifilm GFX100 II | 43.8 x 32.9 mm, 102 MP (V) | Medium format detail, Fuji film simulations | "Fujifilm GFX, medium format, fine detail" |
| Fujifilm X100 series | X100VI: APS-C 23.5 x 15.7 mm, 40.2 MP X-Trans CMOS 5 HR, fixed 23mm f/2 (35mm equivalent), 5-axis IBIS, 6.2K 30p and 4K 60p (V Fujifilm via retailers, 3P Newsshooter) [verified shopusa.fujifilm-x.com, newsshooter.com, 2026-10-14] | Compact street look, Classic Chrome simulation | "Fujifilm X100, Classic Chrome, street" |
| Sony A1, A1 II, A7 | A1 II: 50.1 MP stacked full frame, 8K 30p, 4K 120p, AI processing unit AF (3P DPReview, CineD) [verified cined.com and dpreview.com, 2026-10-14] | Sharp, clean, neutral, hybrid stills and video | "Sony A7, clean sharp full frame" |
| Canon R5, R5 Mark II | R5 Mark II: about 45 MP stacked full frame, 8K 60p Cinema RAW Light, 4K 120p (V Canon USA, 3P CineD) [verified usa.canon.com and cined.com, 2026-10-14] | Warm skin, portrait staple | "Canon R5, warm skin, 85mm portrait" |
| Nikon Z8, Z9 | FX 35.9 x 23.9 mm stacked BSI, 45.7 MP, 8.3K 60p N-RAW, both bodies share the sensor (V Nikon, 3P) [verified nikonusa.com Z8 page and Wikipedia Z8 and Z9, 2026-10-14] | Detailed, fast, wildlife and sport | "Nikon Z9, fast sharp detail" |
| Phone (iPhone, Pixel, Galaxy) | Main cameras, current flagships: iPhone 17 Pro 1/1.28 in 48 MP, 24mm f/1.78 (Apple lists lens only; sensor size from DPReview); Galaxy S26 Ultra 1/1.3 in 200 MP, 23mm f/1.4; Pixel 10 Pro 1/1.3 in 50 MP (72 mm2), about 25mm f/1.7 (3P DPReview, DXOMARK, GSMArena) [verified support.apple.com, dxomark.com, dpreview.com, 2026-10-14] | Deep focus, computational HDR, wide-angle, UGC realism | "shot on smartphone, deep focus, computational HDR, handheld" |
Medium format is not "better": larger sensor gives thinner depth of field and gentler falloff at equal framing. See crop table in `lens-deep.md`.

## Look cheat by intent
| Intent | Pick |
|---|---|
| Premium skin, drama | ARRI Alexa 35 or Mini LF plus warm prime |
| Crisp tech or action | RED V-Raptor, clean prime |
| Night, practicals, street | Venice 2 at 3200 or Canon DGO |
| Documentary, run and gun | FX3, FX6, C70 |
| Nostalgia, memory | 16mm, Super 8, 35mm film |
| Epic scale | Alexa 65, 65mm, IMAX |
| Editorial still, cosmetics | Hasselblad X2D, GFX |
| Street, candid | Leica M or Q, X100 |
| UGC authenticity | Phone, deep focus, handheld |

## Prompt pattern
"[Format or body] + [lens] + [stock or grade] + [light] + [subject]". Example: "Shot on ARRI Alexa 35, 40mm spherical prime, Kodak Vision3 500T grain, warm tungsten practicals, a potter at her wheel." Keep to one body.

## Verification log (replaces the old unverified list, 2026-10-14)
- Alexa Mini LF, Alexa 65, IMAX 15/70, 65mm 5-perf, X100VI, Z8, Z9, A1 II, R5 Mark II and phone sensors are now sourced in the tables above.
- Sony Venice 2 8.6K: active 35.9 x 24.0 mm at 8640 x 5760 per Sony's imager-mode table; B&H lists 36.2 x 24.1 mm, which is the 6K and original Venice sensor (3P Newsshooter) [verified pro.sony and newsshooter.com, 2026-10-14].
- Canon C500 II: 38.1 x 20.1 mm, 5952 x 3140 (V Canon Europe) [verified canon-europe.com, 2026-10-14].
- Phone sensor sizes are third-party (DPReview, DXOMARK); Apple does not publish them. Phones change yearly: re-check the model on sale.
- Dynamic range claims versus independent tests: see `exposure-and-settings.md`.
