# 3D skin rendering (researched 2026-10-13)
Labels: (V) vendor-official docs, (P) peer-reviewed or primary paper, (3P) community or tutorial, (E) estimate or rule of thumb, (U) unverified. Values are starting points to tune by eye against a real reference photo under the same light; they are not measurements of any real person or product. For general engine, shader and pipeline work load the graphics-rendering skill (`${CLAUDE_PLUGIN_ROOT}/skills/graphics-rendering/SKILL.md`, built separately and possibly not yet present). This file covers only the skin-specific layer; do not duplicate the generic material.

## 1. What skin does optically
Light enters, scatters in the epidermis (melanin absorbs) and dermis (hemoglobin absorbs), and exits blurred and tinted; red scatters farthest, blue least, so shadow edges glow warm and thin parts (ears, nostrils, fingers, lips) transmit red when backlit. On top sits a thin oily film giving sharp specular, and fine vellus hair giving a soft rim. Models therefore need: a diffuse colour base, a subsurface blur wider for red than for blue, dual-scale specular, micro-detail normals and a thin sheen layer. Reference: d'Eon and Luebke (GPU Gems 3 ch. 14) fit skin diffusion profiles with a sum of six Gaussians shared across RGB with per-channel weights summing to 1, and a Fresnel F0 of 0.028 for an IOR of 1.4; red profile width is about 16 mm (P, read 2026-10-13). Exact per-Gaussian weights are in the chapter's figure; fetch them there if needed (not copied here, unverified).

## 2. Physiological parameters (Donner and Jensen line of work, P)
Six spatially varying parameters: melanin fraction (typical range 0 to 0.5), melanin type blend (eumelanin versus pheomelanin), epidermal hemoglobin (0 to 0.05), and dermal blood and thickness parameters. Use them to author diversity: melanin raises absorption and darkens base colour and reduces scattered brightness; hemoglobin adds red and blue-red in lips, cheeks, ears. Do not make darker skin by multiplying albedo grey; raise melanin, keep warm undertone and specular. Deep skin has the same pores, translucency and sheen, with lower diffuse brightness and more visible specular.

## 3. SSS algorithm choices
| Method | Use | Notes |
|---|---|---|
| Sum-of-Gaussians texture-space diffusion (d'Eon 2007) | offline-quality real-time on a UV unwrapped head | about 6 separable passes (P) |
| Separable SSS (Jimenez et al., 2012 and 2015) | real-time screen-space; 2 separable 1D passes; reported cost about 1 ms (2012) and under 0.5 ms (2015) per frame (P) | needs diffuse and depth buffers; fixed maximum scatter distance can over-blur low-reflectance areas (3P critique) |
| Random walk "skin" (Cycles) | offline Cycles | volumetric, adjusts radius from the colour texture, matches measured skin better than the faster approximation (V) |
| Christensen-Burley | fast approximation | less accurate (V) |
| Unreal Subsurface Profile | real-time and path tracer | screen-space; per-material profile (V) |
| Fake: wrap lighting, thickness-based translucency | web, mobile | cheap, glass or wax risk if overdone |

## 4. Layered skin material (recipe)
1. Albedo (base colour): hand-painted or scan-based, even-ish diffuse without baked lighting or baked specular; vary melanin, redness (cheeks, nose, ears, knuckles), blue-green under veins and eyes. Linear workflow: sRGB albedo, linear data maps. Keep albedo away from pure white or black (E: skin albedo mid values).
2. Normal map, two scales: macro (large wrinkles, brow and nasolabial folds, from sculpt) and micro (pores, fine lines, tiling) blended; use a detail normal tiled several times per UV island. Micro detail should fade with distance (mip).
3. Roughness: a map, not a constant. Epic's skin guide starts at about 0.4 and adjusts for scale, age and moisture, and notes that mip levels should get rougher at a distance (V). Typical zone values (E): T-zone and nose 0.3 to 0.4, cheeks 0.45 to 0.55, forehead 0.35 to 0.45, lips 0.3 to 0.4 when moist, dry skin and neck 0.5 to 0.6, ears 0.45. Roughness varies with oil, sweat, age; add pore-scale variation so highlights break up.
4. Specular: F0 about 0.028 for skin (P), or Blender 4.x Specular IOR Level near 0.5 with IOR near 1.4 (3P); avoid specular tint colour; use a specular intensity map (less on lips edges, more on oily zones, near zero in hair-covered areas). A dual-lobe specular (a tight and a wide lobe) gives the "broken" oil gloss (E, common practice).
5. SSS mask or thickness: thin at ears, nostrils, eyelids and fingers, thicker on cheeks and forehead. Unreal reads a mask where white scatters most (V). Three.js reads a thickness map from the green channel (V).
6. Cavity and AO: darken pores, creases and nasal folds only a little; baked AO on skin looks dirty if strong.
7. Sheen or fuzz: a faint, warm, low-roughness sheen mimics peach fuzz rim (E; three.js `sheen` and `sheenColor`, Unreal fuzz channel in the MetaHuman SRMF texture, V).
8. Oil or coat layer: thin clear coat, low weight, low roughness, for sebum; weight keep small (E).
9. Details: moles, freckles, scars, redness, veins as separate masks or decals, with randomised strength; lip texture with vertical creases; eyelids wet at the edge.
10. Wet maps: tears, sweat or oil as a roughness lowering mask, never a global gloss.

## 5. Lighting for skin in 3D
- Large soft area lights (key plus fill plus rim); a single point light gives hard specular and plastic highlights.
- Image-based lighting: an HDRI with a soft key and bounce; add a warm bounce from below for realism; avoid a studio box HDRI with hard, tiny highlights.
- Key about 45 degrees and above eye line, fill 2 to 4 stops lower, rim behind to light vellus and ears (photography ratios from portrait guides, 3P).
- Backlight check: ears, nostrils and fingers must glow warm; if not, raise SSS radius or thickness there.
- Colour: match a real portrait's white balance; avoid saturated coloured lights on skin; add subtle skin-colour bounce from clothing and walls.
- Eyes: lit like in photography; catchlight from the key light; cornea highlight sharp; wet meniscus.
- Camera: portrait focal length (70 to 100 mm equivalent), shallow depth of field, slight chromatic aberration and vignette, film grain, motion blur at 180 degree shutter in animation.

## 6. Blender Cycles
- Principled BSDF with Subsurface method Random Walk (Skin); IOR about 1.4 (3P consensus; the 4.x default is 1.5 for specular and 1.4 for the subsurface IOR, U, verify in your version); anisotropy 0.4 to 0.8 (3P, forum, U).
- Subsurface radius is per channel (R, G, B), true distance equals Radius x Scale, and units are Blender units; real skin scatters a few mm, so scale to the model size. Starting radii from artist forums: (1.0, 0.2, 0.1) default-like, (1.0, 0.18, 0.08) or (1.0, 0.3, 0.2) as brighter variants (3P). Real-scale values reported around (0.04, 0.002, 0.001) at weight 0.9 (U, anecdotal).
- Blue patches on ears or nose mean the radius is too large; reduce weight or radius. Subsurface weight is often 1 for skin (3P).
- Roughness map 0.3 to 0.55, Specular IOR Level 0.5, Coat weight small, Sheen weight about 0.05 to 0.2 with a warm tint for fuzz (E).
- Hair: Principled Hair BSDF (Huang) with melanin for dark hair and a low random colour value; add flyaways as separate sparse curves.
- Eyes: separate cornea with IOR 1.336 (P, physiology), iris with fibre texture, sclera with SSS and vessels, a wet meniscus mesh.
- Render: path tracing at 256 to 1024 samples with denoise, AgX or Filmic view transform, depth of field on, a 100 mm portrait camera, light path caustics off.
- Test: render the head under a neutral HDRI beside a real photo with the same angle; compare cheek tone, ear glow, specular breakup.

## 7. Unreal Engine and MetaHuman
- Skin uses the Subsurface Profile shading model; the profile controls Mean Free Path Color (per channel depth) scaled by Mean Free Path Distance in cm; lower values give tighter, sharper scatter, higher values blurrier; Epic notes visible scatter in light skin is about 1.2 cm (V). Very large distances produce multi-image artifacts and banding (V, an extreme value of 50 tested).
- The effect is screen-space; it needs the light in front of the surface; enable transmission on the light for ear and nostril bleed-through (community answer, 3P). Subsurface Profile may need more light intensity and can be noisy under Lumen (3P). Path tracing gives the best result for stills (3P).
- MetaHuman: Materials > Skin controls cover tone, texture, freckles, accents (area redness) and custom textures; baked pipelines expose BaseColor, Specular, Roughness, Scatter and Normal globals; SRMF packs specular, roughness, metallic and fuzz; scatter bakes to a 512 x 512 map (V).
- Tuning: skin tone and accents first, then roughness global, then scatter; check with a neutral grey chart and a real reference; groom hair with the hair strands shader and flyaway cards.
- Related skills: `unreal-mcp` to drive the editor, `unreal-skill` for engine API work.

## 8. three.js and web
- MeshPhysicalMaterial: `map` albedo, `normalMap` (two-scale blend via a detail normal in a custom chunk), `roughnessMap`, `sheen` and `sheenColor` for fuzz, `clearcoat` small for oil, `thickness` plus `thicknessMap` (green channel) and a low `transmission` (about 0.05 to 0.2, E) with a red `attenuationColor` as a cheap SSS fake; transmission is refraction not true SSS, so high values look like glass or wax; always supply an environment map; physical material costs more per pixel (V docs, E for values).
- Better: inject a wrap-lighting or thickness translucency term via `onBeforeCompile` (the official subsurface scattering example shows this approach, 3P), or run a Jimenez-style separable blur as a post pass for real-time heads.
- Colour management: sRGB for albedo, linear for other maps; use AgX or Neutral tone mapping, renderer output sRGB; soft area lighting or an HDRI environment (RectAreaLight needs its uniforms library).
- WebGPU and TSL node materials may allow fuller SSS; check the current release; skill `webgpu-wgsl` covers the browser GPU stack.
- Budget: texture sizes 2k to 4k for a hero head, KTX2 compression, one SSS pass; fall back to wrap lighting on mobile.

## 9. Digital human QA
Side by side with a reference photo: cheek tone, ear glow, nose highlight shape, lip colour, eye wetness, brow hair direction, pore visibility at the target distance, hair edge softness. Rotate the light around the head: skin should not turn to wax at grazing angles; specular should not be a uniform sheet. Run the realism-qa-checklist tells 1 to 8 on a still.

## 10. Honesty
A render of skin with a product on it is illustration, not evidence of effect; keep any result-implying visual out of ads unless real data and the qualified team back it (see ethics-and-consent.md).
