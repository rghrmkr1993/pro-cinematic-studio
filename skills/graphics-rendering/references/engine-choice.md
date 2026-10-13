# Engine choice: decision tree

Answer in order; stop at first match.

1. Output is a video or still (ad, hero loop, product film)? Use offline render: Blender (Cycles quality, EEVEE speed) or Unreal Movie Render Queue for virtual production. Deliver video/image to web. Code-driven motion graphics: `motion-reel`, `hyperframes*`, `remotion-*`.
2. Output is a single bespoke GPU effect (shader background, particles, filter, data-viz) on a web page? Raw WebGPU with WebGL2 fallback: `webgpu-wgsl`. Tiny bundle, full control.
3. Needs a web scene graph (models, PBR, shadows, controls) and wide reach?
   - Default: three.js. Largest ecosystem, WebGPURenderer with auto WebGL2 fallback, TSL, react-three-fiber for React. See `webgpu-wgsl/references/threejs-tsl.md`.
   - Need an engine-like toolset on web (inspector, node material editor, GUI, XR, physics, strong TypeScript, WebGPU first-class): Babylon.js. Good for configurators and enterprise apps; heavier but batteries included.
   - Need an editor-driven workflow in browser with splats and team collaboration: PlayCanvas.
   - Marketing 3D without code: Spline (hosted runtime, lock-in, heavier payload) acceptable for simple scenes.
4. Native or installable interactive 3D (desktop, mobile apps, high fidelity, large worlds)?
   - Photoreal/high-end, Nanite/Lumen, virtual production, big teams: Unreal (`unreal-skill`; automation `unreal-mcp`, `unreal-create-toolset`). Web delivery only via pixel streaming (server GPU cost) or video.
   - 2D/3D indie games, small footprint, open licence, quick iteration, web export (WASM, WebGL2 today; WebGPU in progress, verify): Godot (`godot`). Web builds are 10+ MB.
   - Mobile-first games and AR: Unity (not covered by a skill here) or native platform SDKs.
5. Learning, research, or custom pipeline (compute-heavy sim, novel renderer)? Raw WebGPU, or Rust `wgpu` for native + web (WASM) from one codebase.
6. Needs authoring and baking of assets for any of the above? Blender (modelling, UV, bake lightmaps/AO, rig, export glTF), with `assets-gltf.md` pipeline.

## Comparison table (2026-10 view, verify before commitment)
| Option | Best for | Reach | Fidelity ceiling | Payload | Team skill |
|---|---|---|---|---|---|
| CSS/SVG/Canvas/Lottie/Rive | UI, illustration | everywhere | 2D | KB | web dev |
| three.js | web 3D | WebGL2 everywhere, WebGPU where available | high (PBR, post) | 150 to 600 KB lib + assets | JS dev, moderate |
| Babylon.js | web apps/configurators | same | high | larger lib (about 1 MB+) | TS dev |
| PlayCanvas | web, splats, editor | same | high | small runtime | web + editor |
| Raw WebGPU | custom effects/compute | WebGPU only + custom fallback | custom | KB | graphics dev |
| Godot | games, interactive apps | native, web export | medium-high | 10+ MB web | gamedev |
| Unreal | AAA, film, archviz | native, pixel streaming | highest real-time | GBs | specialist |
| Blender | offline renders, assets | n/a (export) | highest (Cycles) | n/a | 3D artist |

## Risk notes
- Lock-in: hosted no-code tools hide runtime cost; confirm export and licence.
- Licence checks: Unreal royalties, engine EULAs, HDRI and model licences.
- Web delivery risk: WebGPU gaps (Linux, older Safari, Firefox Android as of 2026-10) require fallbacks; keep a poster/video.
- Staffing: three.js has the biggest hire pool for web; raw WebGPU and Unreal need specialists.
- Maintenance: pin library versions (three.js API churn each quarter, e.g. renderer pipeline renames in 2026).
- Performance honesty: test on a mid-range phone before promising an interactive 3D hero.

## Escalation
When the brief is ambiguous (scope, device tier, budget) ask the Manager; do not assume Unreal for a web page or three.js for a TV-quality video.
