# glTF asset pipeline and compression

glTF 2.0 (Khronos) is the "JPEG of 3D": ship `.glb` (binary, single file). Spec and extension registry on github.com/KhronosGroup/glTF.

## Authoring rules
- Units: meters, Y up, right-handed, -Z forward. Apply scale/rotation (Blender: Ctrl+A) before export. Pivot at base for products.
- One material per distinct look; merge meshes sharing materials; avoid scale on animated nodes. Triangles only, no n-gons.
- Budgets (web, estimates): hero product 50k to 200k triangles, scene 300k to 1M visible, mobile 100k to 300k; draw calls under 100 to 200; textures: total under 20 MB GPU memory per hero, 1k to 2k per map (4k for hero only); first-view payload under 5 MB (hero) to 10 MB.
- Texture packing: baseColor (sRGB, alpha if needed), ORM (R occlusion, G roughness, B metallic; linear), normal (linear, OpenGL green-up per glTF), emissive (sRGB). Share one ORM per material.
- Use glTF extensions instead of custom shaders: `KHR_materials_clearcoat|sheen|transmission|volume|ior|specular|iridescence|anisotropy|emissive_strength`, `KHR_texture_transform`, `KHR_lights_punctual`, `KHR_materials_unlit`, `KHR_mesh_quantization`, `EXT_meshopt_compression`, `KHR_draco_mesh_compression`, `KHR_texture_basisu`.

## Compression stack (pick by goal)
| Layer | Tool | Effect | Notes |
|---|---|---|---|
| Geometry: Draco | `gltf-transform draco` / `gltf-pipeline -d` | 90%+ smaller geometry on static meshes | decode cost on load (WASM, 20 to 200 ms), poor for animated morph/skin data, quantised attributes |
| Geometry: Meshopt | `gltf-transform meshopt` (EXT_meshopt_compression, meshoptimizer) | 50 to 70% vs raw, plus vertex cache/fetch optimisation; fast decode (can be streamed after gzip/brotli) | works on animations, morph targets, instancing; good default for runtime speed |
| Quantisation | KHR_mesh_quantization | smaller attributes without decoders | used by Meshopt filters |
| Textures: KTX2 + Basis Universal | `gltf-transform ktx` / `toktx` / `basisu` | GPU-compressed in VRAM (4 to 8x less), small download | ETC1S (smallest, lower quality, good for albedo/ORM) vs UASTC (higher quality, normals, larger); transcodes at load to BC7/ASTC/ETC2 per device |
| Textures: WebP/AVIF | `gltf-transform webp|avif` (EXT_texture_webp/avif) | smallest download, but decoded to raw RGBA in VRAM | good for download-bound, memory-light scenes only |
| Mip-mapping | KTX2 includes mips | needed for quality | |
Rules of thumb: Meshopt + KTX2 is the modern default; Draco only for the smallest download of static geometry. Normals: UASTC or 16-bit; avoid ETC1S for normal maps. Always compare visually and re-measure file sizes.

## Pipeline commands (gltf-transform CLI, verify flags against installed version)
```
npx gltf-transform inspect model.glb
npx gltf-transform optimize in.glb out.glb --compress meshopt --texture-compress ktx2   # one-shot
# manual:
npx gltf-transform dedup in.glb a.glb && npx gltf-transform prune a.glb b.glb
npx gltf-transform simplify b.glb c.glb --ratio 0.5 --error 0.001                       # LOD / decimate
npx gltf-transform resize c.glb d.glb --width 2048 --height 2048
npx gltf-transform ktx d.glb e.glb --slots "{normalTexture,occlusionTexture,metallicRoughnessTexture}" --mode uastc
npx gltf-transform ktx e.glb f.glb --slots "{baseColorTexture,emissiveTexture}" --mode etc1s
npx gltf-transform meshopt f.glb out.glb --level high
```
Other tools: Blender export (glTF 2.0 add-on, Draco option), glTF Validator (validate before shipping), gltfpack (meshoptimizer CLI: `gltfpack -i in.glb -o out.glb -cc -tc`), glTF-Sample-Viewer and Khronos sample models for QA, Don McCurdy's glTF Transform, Babylon Sandbox/three editor for preview.

## Loading in engines
- three.js: `GLTFLoader` + `DRACOLoader.setDecoderPath()` + `MeshoptDecoder` + `KTX2Loader.setTranscoderPath().detectSupport(renderer)`; host decoder/transcoder files yourself (CSP aware), do not hot-link.
- Babylon: glTF loader plugin with Draco/Meshopt/KTX2 support built in or configured via URLs.
- Native engines: Unreal imports glTF via Interchange, Godot has first-class glTF import; compression mostly unnecessary natively.
- Stream and prioritise: load low LOD or poster first, then hero; `loading=lazy`-style via IntersectionObserver; HTTP cache with immutable hashes; brotli on `.glb` if not already Meshopt-compressed.

## QA checklist
Validator passes with zero errors; sizes recorded before/after; normal map orientation correct; sRGB flags correct per slot; no extreme texture sizes; animations loop; bounding boxes sane (culling); license of models and HDRIs (CC0/CC-BY, attribute properly); asset names client-neutral in public repos.
