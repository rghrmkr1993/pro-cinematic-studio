# Shot types and integration
Labels: (V) vendor-official, (3P) third-party, (H) house rule, (E) estimate, (U) unverified. Researched 2026-10-14 from VFX breakdown articles, Foundry and Blackmagic tool documentation summaries, and 2026 AI VFX workflow write-ups (actionvfx, armox, Runway resources, third-party). Treat workflow claims as 3P until tested on our footage.

## 1. Sky replacement
1. Matte the sky: luminance or colour key for clear sky, AI matte for complex skylines, hand roto for trees and wires. Keep a soft edge.
2. Replacement plate: a generated sky still or loop, or a licensed plate, graded to the scene's time of day. Match direction of the sun with existing shadows.
3. Light: recolour the scene to the new sky only if the sky changes the light (golden hour sky on a noon scene is wrong). Add sky-colour fill to the top edges and reflections in glass and water.
4. Match: contrast, haze (lift the distant buildings toward the sky colour), grain, blur on the sky edge, parallax (a slow drift opposite to camera pan; distant sky moves little).
5. AI route: prompt-based sky edits in Edit Video or Aleph with direction notes ("replace the sky with a sunset, keep camera motion and subject", 3P example). Check shadows and reflections after; models relight loosely (3P).
Failure: halos at the horizon, sky too sharp or too saturated, light does not match faces.

## 2. Set extension and plate expansion
- Extend a frame (outpaint), add height or depth to a location, or build a wide from a medium.
- Method: (a) Expand or Outpaint a keyframe in the image tool, generate a matching plate, then comp; (b) Reframe and Expand tools; (c) build the extension in 3D (Blender or Cinema Studio location Element, 3D Jutsu) with matching lens and perspective.
- Match: horizon line and vanishing point, lens distortion and focal length, depth of field, atmospheric haze, light direction, colour, grain.
- Keep action in the original plate; extension is for edges, background and set.
- Camera moves need a track; if the plate has a solve, project the extension onto cards or a 3D proxy; if it does not, use static or locked frames (cinematography choice before generation).
- Where a scene repeats, build one extension plate and reuse (credits).

## 3. Crowds and extras
- Do not prompt hundreds of unique faces; models give clones and melted faces. Instead: a base plate with a few real-looking foreground people, a midground of simple figures, and a distant crowd as a soft, slow, repeated pattern.
- Tiling: reuse a crowd loop in layers at different scales, speeds and flips (slight, to avoid obvious repeats), with depth blur and atmospheric haze.
- Generated crowd plates: ask for "distant crowd, small and soft focus, varied clothing", Indian setting specifics per asian-human-reference (attire, region), and keep faces non-identifiable and non-real (no real people, H).
- Walk cycles and costumes: check each region's attire (asian-human-reference hair-grooming-attire.md); wrong attire is a critical fail.
- Disclose synthetic crowds in a news or documentary context (consent and disclosure rules, creative-studio section 7).

## 4. Particles, atmosphere, practical-style FX
- Dust, smoke, embers, rain, snow, fog, lens dirt, sparks, light leaks. Sources: stock plates with a licence note, generated plates (black background, particles only), or code-rendered particles (`motion-reel`, `webgpu-wgsl`).
- Blend: screen for light-emitting (fire, sparks, glow), add or lighten; multiply for dark smoke; normal over for dust with alpha.
- Match: scale (particle size vs lens and distance), direction of wind and motion, scene light colour, depth blur, motion blur, grain.
- Atmosphere adds depth and hides seams; subtle (10 to 25 percent) is usually enough (H).
- Product and food clips: steam, droplets and sparkles must not imply efficacy or freshness claims.

## 5. Matching light, grain, motion blur (the checklist that sells the comp)
Light
- Direction: key light from the same side; shadows fall the same way; rim on the element if the BG has a back light.
- Colour temperature and tint: sample the plate's highlights and shadows; push the element toward them; add bounce colour from the surrounding set.
- Contrast and black level: the element's blacks must equal the plate's blacks; lift or crush to match; scopes (color-grading).
- Contact shadow and ambient occlusion where the element touches the ground; reflections in glossy surfaces.
Colour and grade
- Match saturation and white balance; do a rough neutral grade of the element to the plate, then a shared grade on both (colorist later).
Grain and noise
- Remove foreign grain from the element (light degrain), then add the plate's grain over the finished comp so both share one grain structure; AI clips often carry model noise: use one recipe over everything (color-grading section on grain).
Motion blur
- Match the plate's shutter: at 24 fps and a 180-degree shutter, blur is about half the frame interval (cinematography frame-rates-deep.md). Moving elements need blur proportional to speed; static elements should not have it; generated plates may have none or too much.
- ffmpeg approximation of a 180-degree look for sharp element motion: render at a higher frame rate, blend frames, drop to 24 (`minterpolate=fps=96:mi_mode=blend,tmix=frames=4,fps=24`, verified); in Fusion or Nuke use a motion-blur node with the shutter angle.
Lens and optics
- Match depth of field (blur BG elements to the focal plane), lens distortion, vignette, chromatic fringe, bloom or halation on bright elements (color-grading grain-halation-looks-qc.md).
Perspective and scale
- Camera height, horizon, vanishing points; element scale with distance; people height 1.6 to 1.8 m reference.

## 6. CG plus AI integration
- Use CG for what must be exact: product shapes, logos, mechanical motion, a hero object, text and graphs (Blender, 3D Jutsu, code-rendered `webgpu-wgsl`); use AI for the environment, people, texture and atmosphere.
- Pipeline: lock camera and lens from the AI plate (static or a track), build the CG element in the same perspective, render passes (beauty, alpha, shadow, reflection, Z if needed), comp with matched light, grain and blur.
- Colour: Blender uses a view transform (AgX default, or ACES 2.0 in 5.0, 3P). Render to EXR linear for a managed comp or to display-referred Rec.709 PNG for a simple one; tell the colorist which (color-grading pipeline file).
- Shadows and reflections: render shadow catcher and reflection passes, or fake with a darkened, blurred copy of the alpha at the contact point.
- Re-render sparingly: use the CG as a reference for a Genjutsu or Edit Video pass to style it if it looks too clean (3P method; check result for faithfulness).
- Product shots: keep the real product pack as ground truth (higgsfield-master product lock); never let AI redraw the label; comp a true label render.

## 7. AI plus live-action hybrid
- Live-action plate with an AI element, or an AI plate with a real performer (consent). Match frame rate, shutter, lens, grade and noise.
- Real plates are real camera data: if log, convert properly before comping (color-grading pipeline file), and stabilise.
- Real footage that includes any recognizable person or private property needs a signed release (film-legal-distribution skill if present, or the Manager).
- Performance capture hybrid: a real performer's motion drives an AI character (performance-direction skill); then comp the character over a plate with matched light.
- Always label synthetic elements where the platform or ASCI and FTC rules need it; never present fabricated footage as documentary evidence.

## 8. Checks per shot type
| Type | Typical failure | Check |
|---|---|---|
| Sky | Halo, wrong light | Edge at 100 percent, shadows direction |
| Extension | Seam, perspective mismatch | Horizon, lens, vanishing points |
| Crowd | Clones, melted faces | Look at 5 random faces, repeat patterns |
| Particles | Wrong scale or direction | Compare with plate motion |
| CG insert | Floating, no contact shadow, too clean | Shadow, grain, blur |
| Hybrid | Colour, noise mismatch | Neutrals, grain at 100 percent |
