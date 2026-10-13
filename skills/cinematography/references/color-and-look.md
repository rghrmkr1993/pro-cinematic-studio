---
name: cinematography
description: "Color and look for AI prompting: palettes and color psychology, teal and orange, bleach bypass, film stocks (Kodak 5219, 5207, 2383 print emulation, Portra, Ektachrome, Fuji Eterna), grain, halation, LUT looks, and genre looks including thriller, romance, horror, period, sci-fi, Indian commercial cinema, Korean drama and anime. Part of the cinematography skill."
---

# Color and look
Labels: (K) craft, (V) vendor-official (Kodak data sheets), (3P) third-party or colorist commentary, (H) house rule. Stock descriptions are partly subjective colorist and reviewer opinion; for critical decisions check Kodak data sheets. (3P)

## Palette and psychology
| Color family | Common association | Use |
|---|---|---|
| Warm amber, orange | Comfort, nostalgia, danger (fire) | Home, memory, desire |
| Red | Passion, danger, power | Accent, 10 percent of palette |
| Teal, cyan | Cold, tech, calm, detachment | Sci-fi, thriller, night |
| Blue | Sadness, isolation, trust | Night, hospitals, melancholy |
| Green | Nature, sickness, envy | Natural or uneasy (sickly green fluorescents) |
| Pastel | Whimsy, innocence, irony | Stylized comedy, memory |
| Desaturated | Realism, bleakness | War, drama |
| Gold and deep red | Royalty, festival, period | Epic, Indian ceremonial |
Meaning is cultural: red is auspicious in India and China and danger in much of the West; verify for the audience. (K)
Palette rule: three colors, 60:30:10 (dominant, secondary, accent) (V Higgsfield Academy). Prompt: "palette of cream, sage green and a single amber accent".
Name hex or paint words rather than adjectives where the tool supports hex (Soul HEX, Cinema Studio palettes, V).

## Contrast and tone
- Lifted blacks: faded, nostalgic, indie. Crushed blacks: dramatic, punchy. Soft roll-off in highlights: filmic. Clipped highlights: video look. (K)
- Saturation: muted for realism, rich for fantasy and commercial.
- Prompt: "soft highlight roll-off, gently lifted blacks, muted saturation".

## Named looks
| Look | Traits | Prompt | Best for |
|---|---|---|---|
| Teal and orange | Skin orange against teal shadows, complementary | "teal and orange grade, warm skin, cool shadows" | Blockbuster, action; use with restraint, skip for skincare (H) |
| Bleach bypass | Silver retained: low saturation, high contrast, gritty | "bleach bypass, desaturated, high contrast, gritty" | War, dystopia, hard drama |
| High-key clean | Bright, low contrast, minimal shadow | "high-key beauty, bright, airy, neutral white balance" | Cosmetics, lifestyle |
| Low-key noir | Deep blacks, single source | "low-key noir, deep shadows, hard light" | Crime |
| Warm film | Amber highlights, grain, halation | "warm film look, halation, gentle grain" | Memory, romance |
| Pastel stylized | Flat planes, curated hues | "pastel palette, flat symmetrical, soft light" | Whimsy |
| Day-for-night blue | Blue cast, low exposure | "cool moonlit grade" | Night |
| Sepia / monochrome | Single hue | "sepia monochrome, 1930s" | Period flashback |
| Cross-processed | Shifted color curves | "cross-processed, green-cyan highlights" | Music video |

## Film stocks and emulsions
| Stock | Type | Look (mostly 3P) | Prompt |
|---|---|---|---|
| Kodak Vision3 500T 5219 | Tungsten color negative, fast | Rich color, fine grain for its speed, tungsten balance; a colorist places it slightly lower in contrast than other Vision3 stocks (3P); Kodak sheet: EI 500 tungsten, EI 320 daylight with an 85 filter, at least 3.5 stops over for highlights (V) [verified kodak.com 5219 data sheet, 2026-10-14] | "shot on Kodak Vision3 500T 5219, tungsten night interiors, visible grain" |
| Kodak Vision3 250D 5207 | Daylight, medium speed | Fine grain, high highlight latitude, reduced shadow grain (V Kodak claims); described as the highest-contrast stock in the family (3P colorist); Kodak sheet: EI 250 daylight, EI 64 tungsten with an 80A filter (V) [verified kodak.com 5207 data sheet, 2026-10-14] | "Kodak Vision3 250D 5207 daylight, clean fine grain, rich color" |
| Kodak 2383 print | Print film for projection | Rich blacks, neutral highlights, strong midtone contrast, "film print" feel (V and 3P) | "2383 print emulation grade, rich blacks, smooth highlights" |
| Kodak Portra 160 / 400 / 800 | Still negative | Kodak E-4050 sheet: finest grain high-speed colour negative, natural skin tones, strong saturation across lighting conditions (V); the soft pastel and wide latitude (reviews quote anywhere from about 2 to 6 stops over) are photographer opinion (3P) [verified business.kodakmoments.com E-4050, 2026-10-14] | "Portra 400 look, warm skin, soft pastel" |
| Kodak Ektachrome | Reversal slide | Kodak E100: ISO 100 daylight reversal, extremely fine grain, moderately enhanced saturation, neutral tone scale, natural skin (V); "cool clean blues" is reviewer opinion (3P) [verified kodak.com Ektachrome E100 page, 2026-10-14] | "Ektachrome slide look, saturated, vivid blues" |
| Kodak Tri-X / B&W | Black and white | Gritty grain, contrast | "Tri-X black and white, grainy" |
| Fuji Eterna (motion picture) | Cinema negative | Eterna 500T: pastel colour, fine grain, natural skin, shot Slumdog Millionaire; Eterna Vivid 500: saturated, contrasty (3P retailers, forums). Production ended in 2013 (3P), so stock today is old [verified shotonwhat.com, thecelluloidcollective.com, cinematography.com, 2026-10-14] | "Fuji Eterna look, muted cool greens, soft contrast" |
| Fuji Velvia / Superia | Still | Velvia saturated, Superia green cast (K) | "Fuji Superia, green cast, drugstore film" |
| CineStill 800T | Remjet-removed Vision3 | Red halation around lights (3P) | "CineStill 800T, red halation around neon" |
| 16mm / 8mm | Format | Heavy grain, gate weave, soft | "Super 8 home movie, gate weave" |
Models know stock names as style tokens; they do not simulate chemistry. Name one stock only, plus grain and halation words, rather than stacking three. (H)
Higgsfield camera bodies: 35mm Film, 8mm Film, DV Camcorder, Modern; Fine Film and Raw 16mm in 3.5 (V and 3P; see `higgsfield-master`).

## Grain, halation, bloom
- Grain: fine (35mm, 250D), medium (500T), heavy (16mm, 8mm, push-processed). Grain also hides AI plastic smoothness. (K, H)
- Halation: red-orange glow around bright highlights caused by light scattering back through the film; stock backing normally suppresses it, and removing the layer shows it (CineStill, 3P). Prompt: "subtle red halation around streetlights".
- Bloom and diffusion: Pro-Mist glow; "soft bloom on highlights".
- Gate weave, dust, scratches: for period or archive looks only.
- Too many effects together look fake; choose one signature (grain or halation or bloom).

## LUT and grading language
- A LUT is a color transform; "Rec.709 neutral", "log flat", "film print LUT" are common names. Tell the model "flat log look, low contrast, desaturated" for a raw-log image that you will grade later. (3P)
- Grade the hero frame first, match the rest to it (V Higgsfield visual language).
- Cinema Studio 4.0 post controls: temperature, contrast, saturation, sharpness, grain, highlights, exposure (V).
- White balance: say "neutral 5600K" for clean daylight, "warm 3200K tungsten" for interiors.

## Genre looks
| Genre | Palette | Light | Camera and lens | Prompt seed |
|---|---|---|---|---|
| Thriller | Desaturated teal and steel, sodium accents | Low key, hard, shadows, fluorescents | Long lens, handheld, slow push | "cool desaturated thriller grade, hard side light, deep shadows" |
| Romance | Warm pastel, golden amber, soft pink | Soft backlight, golden hour, glow | 50 to 85mm shallow, gentle gimbal | "warm romantic glow, backlit hair, soft diffusion, shallow focus" |
| Horror | Sick green, cold blue, black | Underexposed, practicals only, shadows | Wide lens, static or slow creep | "dark underexposed, single dim practical, long shadows, static frame" |
| Period | Muted earth, candlelight, sepia | Candles, window, no modern sources | Vintage anamorphic or spherical, grain | "period drama, candlelight, muted earth tones, film grain" |
| Sci-fi | Cold cyan, neon accents, clean white | Rim and practicals, glow, haze | Wide anamorphic, symmetrical, slow dolly | "cold cyan sci-fi, neon rim light, wide anamorphic, haze" |
| Western / desert epic | Dusty ochre, bleached sky | Hard sun, long lens heat shimmer | Wide anamorphic, tableau | "dusty ochre grade, harsh sun, wide anamorphic" |
| Indian commercial cinema | Saturated, rich color, red, gold, teal-orange pops, glossy | Hero backlight, beauty fill, rim; song sequences very lit | Wide scope, crane, slow-mo, dramatic zooms | "rich saturated glossy grade, hero backlight, rim light, slow motion, wide scope" |
| Indian realist (Malayalam, indie Tamil) | Natural earth, lived-in, subtle | Natural light, practicals, handheld | 35mm, observational | "natural light realism, muted palette, handheld, lived-in" |
| Korean drama | Soft pastels, gentle warm/cool split, clean skin | Soft window light, backlit glow (one Korean DP, Chung-hoon Chung, known for harder backlight with soft fill, 3P) | Primes, shallow focus, bokeh lights | "soft pastel K-drama grade, window light, creamy shallow focus, clean skin" |
| Anime | Flat cel colors, high-saturation skies, painterly | Strong rim, lens flare, dramatic clouds | Dynamic angles, still held frames, speed lines | "anime film look, painted sky, cel shading, strong rim light" (see `08-anime-action`) |
| Documentary | Neutral, true | Natural | Handheld 35mm | "documentary natural color, handheld, available light" |
| Luxury commercial | Black and gold, dark neutral | Controlled, rim, slow glide | Macro, slow dolly | "dark premium grade, gold rim, slow glide" |
Genre cues from K-drama and regional cinema summaries are 3P blogs and Wikipedia-grade sources; they describe tendencies, not rules. K-drama: romance in soft pastel and warm high white balance, suspense in cool blue, period in deep red and gold, heavy bokeh from prime lenses, and exceptions exist (Mr. Sunshine melancholic gold, My Mister dim); on-screen glossy skin comes from makeup, diffusion light and retouch, so never imply a skincare product alone gives it (3P Dramabeans, Tatler Asia, KOU) [verified dramabeans.com and tatlerasia.com, 2026-10-14; no professional DP analysis found, checked: Elle India, Soompi, Review Geek]. Regional Indian looks: see `director-styles.md`.

## Color continuity across shots
- Repeat the same 3 palette words and the same stock and grain in every prompt of a sequence. (H)
- Environment anchors (wall color, costume color) carry the palette better than adjectives. (H)
- Regrade the finished clips in an editor to match; do not rely on the model to hold color. (H)

## Skincare and product color honesty
Show product and skin color as true as possible: neutral white balance, no teal skin cast, no filter that implies results. (H)
