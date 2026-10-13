---
name: cinematography
description: "Exposure and camera settings for film and AI prompts: exposure triangle, aperture and depth of field, shutter and 180-degree rule, ISO and dual native ISO, ND, white balance, dynamic range, log and LUT, monitoring tools, frame rates, resolution vs format, aspect ratios. Part of the cinematography skill."
---

# Exposure and settings
Labels: (V) vendor, (3P) practitioner, (K) craft, (H) house rule. AI models do not take these as parameters; they take the words and the visual result. Translate every setting into a visible look. (H)

## Exposure triangle
Exposure = light reaching the sensor. Three controls, each with a side effect. (K)
| Control | Changes | Side effect |
|---|---|---|
| Aperture (stop) | Light and depth of field | Thin or deep focus, diffraction when tiny |
| Shutter | Light and motion blur | Smooth or staccato motion |
| ISO or EI | Sensor gain | Noise and grain |
One stop is a doubling or halving of light. Cinema adds ND filters as a fourth control to keep aperture and shutter where the look needs them.

## Aperture
- f-stop is the geometric ratio, T-stop is measured light transmission; match T-stops across lenses for equal exposure (K). Cinema lenses are rated in T.
- Full stops: 1.4, 2, 2.8, 4, 5.6, 8, 11, 16. Each step halves light.
- Depth of field grows with higher f-number, shorter focal length, longer subject distance, smaller sensor (K).
- Practical DOF: at 85mm, f/1.8, subject 2 m, focus falls off within roughly a hand's depth on a full-frame sensor; at 24mm, f/8, subject 3 m, nearly everything from 1.5 m to infinity is acceptable (K, approximation).
- Hyperfocal idea: focus at one distance so everything from half that distance to infinity is acceptably sharp. Stopping down shrinks the hyperfocal distance. The far background sits at the edge of acceptable, so distant detail may soften (V Cambridge in Colour). Use for landscapes and establishing wides.
- Diffraction: past a sensor-dependent limit, smaller apertures lose sharpness; about f/11 on a high-resolution full-frame sensor is where it begins to show (V Cambridge in Colour, limit depends on pixel size). Cinema sets rarely go past T/8 to T/11 for this reason.
- Bokeh: round blades give round discs; anamorphic gives oval; swirl comes from vintage designs. Bokeh needs bright points in frame (see `lenses-and-optics.md`).
- Prompt: "f/1.4, razor-thin focus, creamy bokeh" or "f/11, deep focus, everything sharp".

## Shutter
- Shutter speed sets motion blur per frame. Shutter angle is the same idea per frame interval: 180 degrees = exposure of half the frame time (1/48 s at 24 fps) (K).
- 180-degree rule: natural motion blur that looks "right" to the eye. Formula: speed = 1 / (2 x fps). 25 fps gives 1/50; 30 fps gives 1/60; 60 fps gives 1/120 (K).
- Narrow angle (45 to 90 degrees): crisp, staccato, nervous; action and war (K). Wide angle (270 to 360): smeary, dreamy, more light.
- Flicker: shoot 1/50 (or 172.8 degrees at 24 fps) under 50 Hz lighting, which matters in India, to avoid banding on LEDs and fluorescents (K). Check the tube or LED, not just the mains.
- Rolling shutter skew shows on fast pans with rolling sensors; global shutter cameras (RED Komodo, V-Raptor [X]) avoid it (V).
- Prompt: "natural 180-degree shutter motion blur" or "short shutter, crisp staccato action, little blur" or "long shutter smear, dreamy streaks".

## ISO, dual native ISO, noise
- Base ISO gives best dynamic range; raising ISO adds noise and sometimes lowers range (K).
- Dual base or native ISO: a second circuit gives clean high-ISO. Venice 2: 800 and 3200 (V Sony). Pyxis 6K: 400 and 3200 (V). FX6 and FX3: 800 and 12,800 in S-Log3 (3P, check Sony manual).
- Cinema cameras use EI (exposure index): a metering value, not the real sensor gain (K).
- Noise vs grain: noise is digital and ugly; film grain is organic. Model-side: say "fine film grain, no digital noise" for filmic texture (H).
- Prompt: "low-light, clean high ISO, subtle grain" or "pushed film, heavy visible grain".

## ND filters
Neutral density cuts light without changing colour or look. Use it to keep a wide aperture in daylight (ND 0.3 = 1 stop, 0.6 = 2, 0.9 = 3, 1.2 = 4 stops) (K). Venice 2 has built-in ND to 8 stops (V Sony); URSA Cine 12K LF has 2, 4 and 6 stop ND (V). Variable ND can add colour cast or cross-polarisation (3P). IR contamination in strong ND tints black blue or magenta unless IR-cut is used (K). Polariser removes reflections and deepens skies, and loses about 1.5 stops.

## White balance and Kelvin
- White balance sets which Kelvin value is neutral. Daylight 5600K, tungsten 3200K, overcast about 6500K (K). See Kelvin table in `lighting-for-film.md`.
- Mixed light needs a decision: balance to the key and let the rest go warm or cool for story.
- AI wording: "neutral 5600K daylight" for clean, "warm 3200K tungsten glow" for interior.
- Skincare and product honesty: neutral white balance, no cast, no flattering filter that implies results (H).

## Dynamic range and stops
Dynamic range is the span from darkest usable shadow to brightest highlight, in stops. Maker claims versus independent tests (stops):
| Camera | Maker claim | Independent | Source |
|---|---|---|---|
| ARRI Alexa 35 | 17 (V ARRI) | 15.1 at SNR 2, 16.3 at SNR 1 (Imatest); about 16 on a Xyla waveform | CineD lab test, 2022-08-17 |
| ARRI Alexa Mini LF | 14+ (V ARRI) | 13.4 and 14.7 | CineD |
| Sony Venice 2 | 16 (V Sony) | 11.7 to 13.2 at SNR 2 depending on codec; 14.2 best (4K ProRes HQ) | CineD Venice 2 lab test |
| Blackmagic URSA Cine 12K LF | 16 (V) | 12.6 to 13.6 at SNR 2 | CineD lab test and PYXIS 12K test |
| Canon C300 Mark III | 16+ (V) | 12.8 at SNR 2 (pre-production unit) | CineD |
| Hasselblad X2D 100C | 15 (V) | about 12.3 to 12.5 (PDR scale) | Photons to Photos via DPReview forum, PetaPixel |
| Leica M11 | up to 15 at ISO 64 (V) | 14.8 EV (DXOMARK landscape scale, normalised to 8 MP, not comparable with PDR) | DXOMARK |
Rule: independent figures at SNR 2 run 1 to 4 stops under the claim because the thresholds differ. Quote the independent number in client work and say which threshold. Scales differ (Imatest SNR, PDR, DXO) so never compare across rows with different sources. [verified cined.com lab tests, dxomark.com, petapixel.com 2025-11-21, 2026-10-14]
Practical use: protect highlights, then pull up shadows. Windows, sky and lamps are the usual clipping points. Prompt: "soft highlight roll-off, shadow detail retained".

## Log, RAW, LUT
- Log profiles hold a flat, wide image for grading: ARRI LogC (LogC4 on Alexa 35), Sony S-Log3, Canon Log 2 and 3, Blackmagic Film (V, K).
- RAW (ARRIRAW, REDCODE, Blackmagic RAW, X-OCN) keeps sensor data; ISO and WB can change later with less penalty (K).
- LUT: a colour transform to Rec.709 or a look; "show LUT" lets the set see a final image while recording log (K).
- AI wording: "flat log look, low contrast, desaturated" gives a gradeable base; "Rec.709 neutral" gives finished video.
- Cinema Studio 4.0 post controls: temperature, contrast, saturation, sharpness, grain, highlights, exposure (V).

## Monitoring tools
| Tool | Reads | Rule of thumb |
|---|---|---|
| Histogram | Brightness distribution | Avoid a spike at either wall unless intentional |
| Waveform | Level per scan line | Skin sits mid-range, not at the top; ranges vary by tone |
| Zebras | Over-threshold highlights | 100 IRE flags clipping; 70 IRE is a Rec.709 skin guide for lighter skin and is not a rule for all skin (3P) |
| False colour | Colour-coded exposure map | Check skin and highlights separately |
| Focus peaking | Edge sharpness | Verify on the eye, not the hair |
| Skin check | Eyes, catchlights, texture | Ashy highlights or crushed shadows flag a tone problem (see `lighting-for-film.md`) |

## Frame rates
Full guide, with the content-type table, slow-motion speeds, 50 Hz flicker rules and per-model AI output fps: `frame-rates-deep.md`. Default: shoot and edit at the delivery rate (24 cinema and OTT, 25 Indian TV and web, 30 Reels), 180-degree shutter (172.8 degrees or 1/50 on 50 Hz mains).

## Resolution vs format
Resolution is pixel count (4K, 6K, 8K); format is the sensor or film area (Super 35, full frame, medium format, 65mm). More pixels do not make a bigger look; more area does (K). Higher resolution shows more skin detail, so lens diffusion and lighting matter more. AI video outputs are typically 720p to 1080p with upscaling later (V Cinema Studio 4.0, 1080p). Plan composition for the crop you will deliver.

## Aspect ratios and use
| Ratio | Name | Story use |
|---|---|---|
| 1.33:1 | Academy, 4:3 | Intimate, nostalgic, period, portraits |
| 1.66:1 | European widescreen | Gentle, balanced, arthouse |
| 1.85:1 | Flat | Standard cinema, comfortable drama |
| 2.00:1 | Univisium | Modern streaming, balanced |
| 2.39:1 | Scope | Epic, landscape, isolation in space |
| 1.43:1 | IMAX 15/70 (nominal; camera frame is 1.34:1) | Immersive, tall [verified filmatlas.com, 2026-10-14] |
| 16:9 | HD | Default TV, web, YouTube |
| 9:16 | Vertical | Reels, Shorts, phone-first; centre action, keep safe margins for UI |
| 4:5 | Feed portrait | Instagram feed, ads, product stills |
| 1:1 | Square | Product, grid |
Set ratio in the tool UI, not only in text. A "2.39:1" word in a 16:9 render can add bars instead of true scope; treat it as a composition cue only and crop to 2.39:1 in post. [no vendor doc for text-ratio behaviour as of 2026-10-14; checked: Veo and Runway guides, Morphic glossary, Pixverse guide; run a with/without test per model] (see `lenses-and-optics.md`)
Platform rule: no TikTok for Indian clients (house rule); use Reels and Shorts. Vertical needs tight, centred framing and large faces.

## Prompt translation table
| Setting intent | Words |
|---|---|
| Dreamy | f/1.4, wide shutter, glow, lifted blacks |
| Crisp action | f/5.6, short shutter, 25 fps feel |
| Natural doc | 35mm, f/4, 180-degree shutter, available light |
| Night | f/1.4 look, high ISO grain, practicals, no blown highlights |
| Product clinical | f/8 to f/11, neutral 5600K, flat log base |
