# 2D vs 3D vs "4D", NeRF and Gaussian splats

## 2D options (cheapest, most accessible)
| Tech | Strength | Limits | Pick when |
|---|---|---|---|
| CSS/SVG | crisp vector, accessible DOM, CSS animation, filters | thousands of nodes slow | UI, icons, illustrations, charts under 1k marks |
| Canvas 2D | immediate mode, many sprites, pixel effects | CPU-bound beyond ~10k shapes; no layout | generative art, particles up to ~10k (`algorithmic-art`), image manipulation |
| Sprite sheets / WebGL sprites (PixiJS) | 10k+ sprites via GPU batching | asset pipeline | 2D games, rich effects |
| Lottie (vector JSON) / dotLottie | designer-authored, tiny | limited interactivity, effects subset | icon and illustrative animations |
| Rive (state machines) | interactive vector, runtime in WASM/Canvas/WebGL | editor dependency | interactive mascots, UI with states |
| Video (WebM/AV1/H.264) | photoreal motion cheaply | no interactivity, bitrate | hero loops (see `motion-reel`, `hyperframes*`) |
Choose the lowest dimension that carries the idea. 2.5D (layered parallax, depth maps) often delivers "3D feel" at CSS cost.

## 3D on the web
Triggers: orbit/inspect products, configurators, spatial storytelling, data in 3D, lighting interplay. Engines `engine-choice.md`. Costs: payload 1 to 10 MB, GPU battery, a11y work, SEO via text alternatives. A hero that is pure decoration usually should be video or 2D (see `modern-web-design-standards`).

## "4D" has three meanings; clarify which one is meant
1. Time-varying 3D (3D + time): animated or volumetric video. Methods: skeletal/morph/VAT animation (assets in `motion-animation`), alembic/point-cache playback, volumetric video (depth meshes, 4DGS), fluid caches, medical/scientific 4D volumes (sparse 3D textures per frame, sampled via `texture_3d` and raymarched).
2. 4D geometry (true fourth spatial dimension): tesseract, 4D polytopes, 4D fractals (Julia sets). Technique: represent vertices as vec4, rotate with 4x4 rotations in the planes XW, YW, ZW (six planes total), project 4D to 3D by perspective division by `(d - w)` (or stereographic), then normal 3D camera. Render wireframe or slices (cross-section at w = c). Educational/art; shader or CPU, trivial cost.
3. Marketing "4D" (3D with motion, haptics, scent): not a technical term; ask what is wanted.

## Radiance fields on the web
- NeRF (2020): MLP maps position+direction to colour and density; volumetric rendering. Slow to train and render originally; Instant-NGP (hash grids) made training minutes. Real-time web NeRF is niche; baked variants exist (MobileNeRF: textured polygons, SNeRG). Prefer splats now.
- 3D Gaussian Splatting (Kerbl et al., SIGGRAPH 2023): scene = millions of anisotropic 3D Gaussians (position, covariance as scale+rotation, opacity, view-dependent colour via spherical harmonics). Render: project to 2D ellipses, depth sort, alpha blend front to back at real-time rates; training from photos plus SfM (COLMAP) in tens of minutes on a desktop GPU.
- 4D Gaussian Splatting (4DGS): adds time: deform Gaussians per frame with a learned deformation field (Wu et al. 2023) or 4D covariance with temporal slice (Yang et al. 2023); used for volumetric video of people and scenes; files are large (tens to hundreds of MB), streaming and per-frame compression active research (2026, estimate).
- Formats: `.ply` (raw, huge: about 240 bytes per splat), `.splat` (compact, about 32 bytes), `.ksplat`, `.spz` (Niantic, compressed about 10x), SOG/`.compressed.ply` (PlayCanvas SuperSplat), emerging glTF extension `KHR_gaussian_splatting` (proposal stage, verify status 2026-10).
- Web viewers: PlayCanvas (engine and SuperSplat editor), Spark (three.js splat renderer), Luma/Gaussian-splats-3d (three.js), Babylon.js splat support, Needle, Polycam/Luma capture apps. Typical budgets: 0.5M to 3M splats on desktop browsers, 200k to 1M on phones (estimates). Sorting on GPU (radix sort in compute) is the key cost; WebGPU helps, WebGL uses worker sorting.
- Pipeline: capture (200 to 400 overlapped photos or video frames, fixed exposure) -> pose (COLMAP/GLOMAP) -> train (gsplat, Nerfstudio splatfacto, PostShot, Luma) -> clean/crop floaters in SuperSplat -> compress (spz/sog, quantise SH to degree 0 or 1) -> LOD/chunk -> viewer with progressive load -> poster + fallback video.
- Limits: baked lighting (cannot relight), no collision geometry (provide a proxy mesh), floaters, view extrapolation breaks, licensing/privacy of captured people and places. Not good for crisp text or reflective/transparent objects.
- Product use: scan-based hero of a physical product (turntable capture) beats low-poly 3D for realism of texture; for transparent or glossy packaging, use authored PBR instead.

## Decision shortcut
Need relight, physics, edit, small payload: authored 3D/glTF. Need photographic realism of a captured real place or object, view-limited: splat. Need person in motion, user-chosen viewpoint: 4DGS (heavy) or video plus depth parallax (cheap). Need flat motion: 2D (Lottie/Rive/CSS) or video.
