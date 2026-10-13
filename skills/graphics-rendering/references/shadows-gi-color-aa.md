# Shadows, global illumination, color science, anti-aliasing

## Shadows
- Shadow mapping: render depth from the light, compare in the main pass. Variants: PCF (soft edges, 3x3 to 5x5 or Poisson), PCSS (contact-hardening using blocker search), VSM/ESM (filterable, light bleeding), cascaded shadow maps for large outdoor scenes (3 to 4 cascades, practical split `lambda ~0.7`), cube maps for point lights (6 faces: costly, limit count).
- Artifacts: acne (self-shadow): add slope-scaled depth bias and a normal-offset bias (move lookup along the normal by about 1 texel); peter-panning (floating shadows): reduce bias, render back faces into the map; aliasing: fit the light frustum tightly, snap to texel increments to stop shimmering when the camera moves; resolution 1024 to 2048 per cascade on web.
- Cheap alternatives: baked lightmaps (static), contact shadows via screen-space ray march for small details, blob/AO decal under characters on mobile, analytic shadows from SDF for few shapes.
- Ray-traced shadows exist in native engines (Unreal hardware RT, Lumen); not available in browsers as of 2026-10.

## Global illumination options
| Approach | Dynamic | Cost | Notes |
|---|---|---|---|
| Baked lightmaps (Blender/Unreal/Lightmass, three.js lightmap or AO map) | no | zero at runtime | best quality per ms on web; UV2 required; re-bake on layout change |
| Light probes (SH grids) | lights static, objects move | low | for dynamic objects in baked scenes; blend between probes |
| Reflection probes / cubemaps | rarely | low | specular environment per room |
| SSAO/GTAO, bent normals | yes | low to mid | contact darkening only, not true GI |
| SSGI / SSR | yes | mid | screen-space, misses off-screen light; temporal denoise needed |
| Voxel cone tracing / SDFGI / DDGI (probe-based RT) | yes | high | native engines (Godot SDFGI/VoxelGI, Unreal Lumen is hybrid), possible but heavy on WebGPU |
| Path tracing | yes | very high | offline (Blender Cycles) or high-end GPUs with denoising; progressive accumulation for still product views in browser is feasible |
Rule: static architecture or product scenes on web: bake. Dynamic day-night or destructible: probes or SSGI at reduced resolution. Spend effort where eyes look (faces, hero product).

## Color science
- Light math is linear; displays expect gamma-encoded sRGB (transfer curve approx 2.2, exact piecewise). Convert on texture load (`*-srgb` formats do it in hardware) and on output (sRGB framebuffer or manual encode).
- Linear for: albedo after decode, lighting, blending, blur. Never blur or blend in sRGB (dark fringes, muddy gradients).
- Gamuts: sRGB (Rec.709 primaries) is the web default; Display-P3 is about 25% wider and common on Apple and many phones (`color(display-p3 ...)` in CSS, canvas `colorSpace: "display-p3"`); Rec.2020 for HDR video. Do authoring in a wide working space (ACEScg) for film pipelines, convert at output.
- HDR: scene values exceed 1.0 (sun 1000x a lit wall). Store in `rgba16float`. HDR display output on the web (canvas `toneMapping: { mode: "extended" }`, CSS `dynamic-range-limit`, `color-gamut`) is partial and platform dependent (verify, 2026-10). Always keep an SDR path.
### Tonemapping operators
| Operator | Character | Use |
|---|---|---|
| Reinhard (extended) | simple, desaturates highlights | quick previews |
| ACES (Narkowicz fit or full RRT/ODT) | high contrast, saturated, hue shifts (blue to purple, orange to yellow) | filmic cinematic look |
| AgX (Blender 4 default) | neutral, graceful desaturation to white, fewer hue skews | general 3D, bright lights, three.js `AgXToneMapping` |
| Khronos PBR Neutral | preserves base color below highlights, compresses only bright parts | e-commerce, product configurators, brand-colour fidelity |
| Uncharted2/Hable, Filmic | warm filmic | games legacy |
Apply: exposure in EV first (`c * 2^EV`), then operator, then output transfer. Do not tonemap UI or video textures that are already display-referred. White balance and grade (lift/gamma/gain, LUT 33^3) after tonemap or on log-encoded data.
Banding in gradients: add 1 LSB triangular dither (blue noise) before 8-bit output.

## Anti-aliasing
| Method | Handles | Cost | Caveat |
|---|---|---|---|
| MSAA 2x/4x | geometry edges | mid bandwidth | no shader aliasing or alpha-test aliasing; WebGPU supports 1 and 4 samples |
| FXAA | all edges post | very low | slight blur |
| SMAA (1x, T2x) | edges, sharper than FXAA | low | needs LUTs |
| TAA / TRAA | geometry, shader, specular shimmer | low to mid | needs motion vectors, jitter, history clamp; ghosting and blur |
| Supersampling (render at 1.5x to 2x) | everything | huge | best for stills |
| Upscalers (FSR, TAAU, DLSS, XeSS) | render low, output high | saves GPU | engine-level; three.js has FSR1/TAAU nodes (reported r184) |
| Alpha-to-coverage | foliage and cutouts with MSAA | low | needs MSAA |
Specular aliasing: filter normal map and roughness (Toksvig or normal-variance to roughness) and mipmap normal maps correctly. Thin geometry: TAA or conservative LOD. Pick MSAA 4x + FXAA-free for simple web scenes; TAA when using screen-space effects.
