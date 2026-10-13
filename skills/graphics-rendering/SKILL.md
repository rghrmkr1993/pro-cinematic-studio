---
name: graphics-rendering
description: "Rendering theory and decisions for real-time graphics: pipeline fundamentals, PBR (metal/rough, energy conservation), image-based lighting, shadows, global illumination options (baked, SSGI, probes, path tracing), color science (linear vs sRGB, ACES/AgX/Neutral tonemapping, HDR), anti-aliasing, materials (skin SSS, hair, cloth, glass, liquids), three-point and studio lighting, 2D vs 3D vs 4D (Gaussian splats, 4DGS, NeRF), glTF compression (Draco, Meshopt, KTX2), and an engine decision tree (three.js, Babylon, raw WebGPU, Unreal, Godot, Blender). Use when choosing how something should look or which engine to use."
---
Part of the cinematic pipeline: entry point creative-studio


# Graphics and rendering

Decide what to render, with which engine, and how to light and shade it. Code for shaders lives in `webgpu-wgsl`; motion lives in `motion-animation`.

## Related skills (link, do not repeat)
- GPU code, WGSL, three.js TSL: `webgpu-wgsl`
- Motion principles, camera grammar, web animation stack: `motion-animation`
- Unreal: `unreal-skill`, `unreal-mcp`, `unreal-create-toolset`; Godot: `godot`
- Photoreal people, skin look in AI images and 3D: `photoreal-humans`
- Design baseline and 3D-or-not rule: `modern-web-design-standards`
- Generative 2D art: `anthropic-skills:algorithmic-art`; video from code: `motion-reel`, `hyperframes*`, `remotion-*`
- Game art direction and asset specs: `art-bible`, `asset-spec`, `asset-audit`

## Triage (answer these in order)
1. Output type: still, video, real-time interactive, or interactive web page? Video or stills: offline render (Blender Cycles/EEVEE, Unreal Movie Render Queue) wins on quality per effort.
2. Target device: desktop only, mobile web, native, XR? Mobile web: budget 1M to 3M triangles visible (estimate), few lights, baked GI, compressed textures.
3. Dimension: can 2D do it (CSS/SVG/canvas/Lottie/Rive)? Prefer 2D unless depth, orbit, or lighting is the point (`references/dimensions-2d-3d-4d-splats.md`).
4. Data source: authored mesh (glTF), scan (splat or photogrammetry), procedural (SDF/shader)?
5. Engine: `references/engine-choice.md`.

## Look decisions in one screen
- Work in linear light; textures: color maps sRGB, data maps (normal, roughness, metal, AO) linear. Tonemap once at the end. Default tonemap for products: Khronos PBR Neutral; filmic scenes: AgX or ACES; UI-like flat color: none. Details `references/shadows-gi-color-aa.md`.
- Shading model: metal/rough PBR (GGX specular, Lambert or Burley diffuse, Smith-GGX visibility, Schlick Fresnel, F0 0.04 for dielectrics). Details `references/pipeline-pbr-ibl.md`.
- Lighting: IBL (HDRI) for ambient and reflections, 1 key directional for shadows; three-point or studio setups in `references/lighting-setups.md`.
- GI budget ladder: baked lightmaps/probes (cheap, static) > SSGI/SSAO (screen-space) > voxel/probe GI > hardware path tracing (offline or high end only).
- Anti-aliasing ladder: MSAA 4x (forward, cheap in WebGPU) > FXAA/SMAA (post) > TAA (best quality, ghosting risk) > DLSS/FSR-type upscalers (native engines, FSR/TAAU nodes exist in three.js r184, reported 2026).
- Materials: skin, hair, cloth, glass, liquid recipes with numbers in `references/materials.md`.
- Assets: glTF 2.0 binary, Meshopt or Draco geometry, KTX2 (Basis) textures, target under 5 MB first-view payload, lazy load rest (`references/assets-gltf.md`).

## Workflow
1. Write the brief: output, device tier, frame/payload budget, brand look (neutral, client-agnostic references only).
2. Pick engine and asset path; prototype the single hardest shot or material first.
3. Build lighting before materials polish; evaluate under neutral grey, then in-context.
4. Optimise with measured numbers (draw calls, triangles, texture MB, GPU ms), see `webgpu-wgsl/references/perf-debug-a11y-support.md`.
5. Provide a fallback (static render, video, lower tier) and reduced-motion state.
6. Review in real hardware: a phone, an integrated GPU laptop, and a wide-gamut display.

## Pitfalls
- Double gamma (washed out) or no gamma (too dark and contrasty): trace color space at each stage.
- Baked normal maps need consistent tangent space; flipping green channel differs between DirectX and OpenGL conventions.
- Energy gain from additive specular on top of full diffuse: use metal/rough workflow so diffuse is scaled by `(1 - F)(1 - metalness)`.
- Shadow acne and peter-panning: tune normal bias before depth bias; tight cascade or light frustum fit.
- Over-bloom and over-fog hide poor materials and look dated; keep subtle.
- Splat or NeRF assets have baked lighting: cannot be relit or physically interacted with.
- Realism of people is perception-driven: eyes, skin SSS and micro-variation matter more than polygon count.

## Reference map
| Topic | File |
|---|---|
| Pipeline, PBR, IBL | `references/pipeline-pbr-ibl.md` |
| Shadows, GI, color science, tonemapping, HDR, anti-aliasing | `references/shadows-gi-color-aa.md` |
| Skin, hair, cloth, glass, liquids | `references/materials.md` |
| Three-point and studio lighting | `references/lighting-setups.md` |
| 2D vs 3D vs 4D, NeRF, Gaussian splats | `references/dimensions-2d-3d-4d-splats.md` |
| glTF, Draco, Meshopt, KTX2 | `references/assets-gltf.md` |
| Engine decision tree | `references/engine-choice.md` |

## Sources consulted (paraphrased)
Learn OpenGL (PBR, IBL, shadows); Real-Time Rendering (Akenine-Moller et al.) concepts; GPU Gems chapters (skin, shadows, water); Khronos glTF and KTX docs; Filament PBR design doc; three.js and Babylon.js docs; Inigo Quilez articles; 3D Gaussian Splatting paper (Kerbl et al. 2023). Numbers marked "estimate" are rules of thumb, not measurements.

## Output contract
A decision note (engine, dimension, look, budgets) plus the minimal setup (lights, tonemap, color spaces, asset pipeline commands), fallback tier, and open risks. Do not claim photoreal parity or device FPS without a measurement.
