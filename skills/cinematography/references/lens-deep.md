---
name: cinematography
description: "Deep lens guide extending lenses-and-optics: prime vs zoom, lens families and character, focal length by scene, crop-factor equivalents, minimum focus, breathing, flare and coatings, filters, vintage vs modern, and what to prompt for each look. Part of the cinematography skill."
---

# Lens deep dive
Extends `lenses-and-optics.md` (focal feel, anamorphic, DOF). Labels: (V) vendor, (3P) practitioner test, (K) craft. Disputed points are shown as a summary of sources. Lens character is partly subjective and tests disagree (see below); the model imitates the look from words, it does not simulate glass. (H)

## Prime vs zoom
| Trait | Prime | Zoom |
|---|---|---|
| Speed | Faster (T1.3 to T2.8) | Slower (T2.8 to T4.5 typical) |
| Image | Sharper, smaller, better skin rendering usually | Convenient, more compromises (K) |
| Use | Drama, beauty, low light | Documentary, events, live, handheld coverage |
| AI cue | "35mm prime, locked" | "slow optical zoom" (only if the zoom is the shot) |
Dolly vs zoom: dolly changes perspective, zoom changes only framing. Say "camera physically dollies, focal length constant" to avoid fake zooms (V Higgsfield blog; see `ai-camera-prompting.md`).

## Lens families and character
Opinions differ. Treat as tendencies, not rules.
Cooke versus Zeiss, summary of sources (no controlled colorimetric study exists as of 2026-10-14): StudioBinder and rental commentary repeat the Cooke reputation of warm, soft-contrast, flattering skin. In Art Adams' side-by-side (ProVideo Coalition), the Zeiss Supreme Prime was the contrastiest and sharpest and showed skin texture most, while the Cooke S7 was the softest, which explains the flattering reputation. Adams later reported that colleagues consider both brands slightly cool, so the "warm Cooke" may be perceived warmth from lower micro-contrast and softness. Zeiss lines differ (Super Speeds mid contrast, Ultra Primes sharper). Working view (H): Cooke means softer, kinder faces; Zeiss means cleaner, more detailed. Test your own set, skin tones and grade. [verified provideocoalition.com Art Adams four-lens tests and studiobinder.com Cooke article, 2026-10-14]
| Family | Reported character | Evidence | Prompt |
|---|---|---|---|
| Cooke S4, Panchro | Gentle, three-dimensional faces, soft contrast, "warm"; one ASC-level tester praised faces (3P Hurlbut); another found grey skin (3P Oseman); Art Adams calls Cooke and Zeiss both slightly cool (3P) | Disputed | "Cooke-style gentle lens, creamy skin, soft roll-off" |
| Zeiss Master Prime, Supreme | Clean, sharp, neutral, almost no breathing, "lacks character" (3P Oseman) | Agreed on clinical | "clean sharp modern prime, neutral, precise" |
| Leica Summilux-C | Crisp but slightly creamy, vibrant skin, nice bokeh (3P Oseman, Hurlbut) | Mixed | "crisp modern prime, creamy skin, pleasing bokeh" |
| Canon K35 (vintage) | Low contrast, flare, soft glow, warm vintage (K, 3P) | Widely reported | "vintage Canon K35 glow, soft flare, low contrast" |
| Panavision anamorphic (C, E, G, T series) | Warm amber flare, oval bokeh, scope (3P, `lenses-and-optics.md`) | Widely reported | "Panavision anamorphic, warm amber horizontal flare" |
| ARRI Signature, Master Anamorphic | Large-format, smooth, gentle, low distortion (3P) | Maker positioning | "large-format modern anamorphic, smooth, clean flare" |
| Atlas Orion | 2x anamorphic primes, T2 to T16, Super 35 coverage (31 mm image circle), 14-blade iris, 40, 65, 100 mm in the A set; 1.6x LF extender for full frame; waterfall bokeh, strong controlled flare, disproportionate breathing; one review saw colourful flare artefacts at T2 on the 80 and 100 that eased by T2.8 to T4 (V Atlas via B&H and rental listings, 3P Wolfcrow) [verified bhphotovideo.com Orion pages, camerarentalsnyc.com, wolfcrow.com, 2026-10-14] | Retailers, rental houses, review | "affordable anamorphic, soft edges, blue streak flare" |
| Hawk V-Lite, Vintage | V-Lite 2x: 9 primes 28 to 140 mm, T2.2 to T3.5, Super 35 (22.94 x 19.22 mm), 2.39:1; V-Lite 1.3x: T2.2, 20 to 110 mm and wider, uses nearly the full 16:9 sensor; Vintage '74 adds lower contrast, enhanced flares and kind skin tones (V Vantage Film) [verified vantagefilm.com Hawk V-Lite pages, 2026-10-14]. Flare tint and edge distortion are described by rental houses (3P) | Maker pages | "Hawk anamorphic, blue flare, edge distortion" |
| Sigma Cine | Modern, sharp, good value (3P) | Reviews | "modern sharp cine prime" |
Rule: pick one family per sequence and repeat the same words in every prompt for continuity (H).

## Focal length by scene (full-frame equivalent)
| Scene | Focal | Why |
|---|---|---|
| Establishing landscape or city | 18 to 28mm | Space, context |
| Interior two-shot, dialogue in a room | 28 to 40mm | Natural relationship |
| Walk and talk | 24 to 35mm | Space and motion |
| Over-the-shoulder | 40 to 65mm | Compresses, keeps depth |
| Close-up, emotion | 65 to 100mm | Isolation, flattery |
| Beauty and skincare close-up | 85 to 100mm | Compression, soft falloff |
| Product hero | 50 to 100mm; macro 100mm for texture | Clean edges, little distortion |
| Chase, hand-held tension | 24 to 35mm; long lens for crowd compression | Immediacy or stacked layers |
| Action wide | 14 to 24mm | Scale, speed |
| Festival crowd | 24mm wide and 135 to 200mm for compression | Both scope and density |
| Surveillance, voyeur | 135 to 300mm | Distance, pressure |

## Crop factor and equivalent field of view
Equivalent focal length = actual focal length x crop factor, relative to full frame 36 x 24 mm. Equivalent aperture also scales: f/2 on Super 35 acts like about f/2.8 for depth of field on full frame (K, approximation).
| Sensor or format | Approx crop factor | A 50mm lens frames like |
|---|---|---|
| Medium format 44 x 33 (Hasselblad X2D, GFX) | 0.79 (V Hasselblad) | about 40mm (wider than on full frame) |
| Full frame 36 x 24 | 1.0 | 50mm |
| Super 35 (about 24.9 x 14, Alexa 35 27.99 wide) | about 1.3 to 1.5 (K) | about 70mm |
| APS-C (Fuji X) | 1.5 (K) | 75mm |
| Micro Four Thirds | 2.0 (K) | 100mm |
| Phone main camera (1/1.3 in class, about 9.8 x 7.3 mm) | about 3.5 (K, computed from DPReview sensor sizes) | Phone "1x" is about 23 to 25mm FF equivalent (iPhone 17 Pro 24mm, Galaxy S26 Ultra 23mm) [verified support.apple.com, gsmarena.com, 2026-10-14] |
| 1 inch | about 2.7 (K) | 135mm |
| Super 16 | about 3.9 (K) | about 195mm |
| 65mm 5-perf (52.48 x 23.01 mm) | about 0.75 (K, computed from the diagonal) | about 38mm [verified kodak.com and thepixelfarm.co.uk, 2026-10-14] |
Prompt: write the full-frame equivalent ("85mm equivalent") and let the model pick. For product lookalikes say "large sensor falloff" or "small sensor deep focus". Large-format shows gentler falloff and thinner focus at the same framing (K).

## Minimum focus and macro
Every lens has a nearest sharp distance. Cine primes often focus 0.3 to 0.9 m; macro lenses focus to 1:1 (K). For skincare textures and droplets use macro 90 to 105mm. Extension tubes and diopters allow closer work with some softness. Prompt: "100mm macro, extreme close-up, shallow focus, product texture sharp".

## Focus breathing
Focal length shifts slightly as focus moves, making the frame swell. Master Primes and Leicas are designed with essentially none (3P Oseman); many vintage and zoom lenses breathe heavily (K). A cinematic AI "rack" can show breathing-like zoom. Keep rack focus to one plane, or cut between planes. See failures in `ai-camera-prompting.md`.

## Flare, coatings, ghosting
- Flare: light scattering inside the lens gives streaks, veils and lowered contrast. Anamorphic gives horizontal streaks, blue or amber by design (3P). Older uncoated lenses flare more. Prompt: "controlled flare, warm streak across frame".
- Coatings: modern coatings cut ghosting and raise contrast. Vintage coatings add glow, lifted blacks, colour cast. A matte box and flags control flare in real shooting.
- Ghosting: stray reflections as shapes of the iris, often green or magenta. Add only on request ("small iris ghosts") since they read as artefacts.
- Halation: red-orange glow around highlights (film and CineStill style); see `color-and-look.md`.

## Filters
| Filter | Effect | When | Prompt |
|---|---|---|---|
| Black Pro-Mist | Strongest local highlight glow; lowers contrast; softens skin as side effect (3P) | Romance, memory, music video, period | "Black Pro-Mist glow, soft halation around lights" |
| Glimmerglass | Mildest bloom, retains sharpness, natural skin (3P) | Beauty, drama | "subtle diffusion, retained sharpness" |
| Hollywood Black Magic | Controlled halation, rich blacks (V Schneider, 3P) | Skin and glamour | "controlled glow, rich blacks, soft skin" |
| Polariser | Cuts reflections, deepens sky | Cars, glass, water | "reduced reflections, deep blue sky" |
| Graduated ND | Darkens sky half | Landscape sunsets | "balanced sky and ground exposure" |
| Warm, cool or colour filters | Shifts hue | Period or mood | "warm amber filter cast" |
| Streak filter | Horizontal flares | Fake anamorphic | "blue streak flare" |
Diffusion strength: 1/8 to 1/4 for faces; higher strengths flatten. Diffusion softens real skin texture, so it can overstate a product's effect; for skincare efficacy imagery disclose or avoid, and route claims to compliance (H, flagged by source 3P).

## Vintage vs modern
| Trait | Vintage | Modern |
|---|---|---|
| Contrast | Low, lifted blacks | High |
| Edges | Soft, swirl, vignette | Flat and sharp |
| Skin | Forgiving glow | Honest detail |
| Flare | Frequent, warm | Controlled |
| Prompt | "vintage 1970s prime, lifted blacks, warm bloom" | "clean modern prime, neutral, sharp" |
Higgsfield Cinema Studio 4.0 lens characters: Clean Sharp, Anamorphic, Vintage Anamorphic, Warm Vintage, Halation Vintage (V).

## What to prompt, by look
| Look | Prompt skeleton |
|---|---|
| Premium commercial | "clean sharp 85mm prime, f/2.8, subtle diffusion, controlled highlights" |
| Epic scope | "large-format anamorphic, 2.39:1, horizontal flare, deep focus" |
| Nostalgic memory | "vintage prime, Halation Vintage, lifted blacks, grain, soft bloom" |
| Documentary | "35mm prime, handheld, natural contrast, slight breathing" |
| Beauty macro | "100mm macro, f/4, soft diffusion, clamshell light" |
| Surveillance | "300mm telephoto, compressed layers, shallow focus, cold" |
Keep the lens in the UI where possible (Camera panel), and use a short phrase in the prompt. (V)

## Cautions
- Do not describe two lens families at once; the result averages them (H).
- Anamorphic needs a bright point source for oval bokeh to show.
- Check face distortion at 14mm or below, text on packaging, and hands.
- Atlas and Hawk specs are now sourced (table above). Close focus and weight differ between listings; read the maker sheet before a rental order.
