---
name: webgpu-wgsl
description: "Real-time GPU graphics and compute on the web: WebGPU core (adapter, device, buffers, textures, bind groups, pipelines, frame loop, DPR, error scopes, WebGL2 fallback), WGSL language and pitfalls, runnable recipes (fullscreen shader, instancing, 100k+ compute particles, post chain with bloom and tonemapping, SDF raymarching, image filters, GPU charts), three.js WebGPURenderer and TSL, profiling, mobile limits, reduced motion, 2026 browser support. Use when writing shaders or GPU code for browsers; for scene theory use graphics-rendering."
---
Part of the cinematic pipeline: entry point creative-studio


# WebGPU and WGSL

Use for browser GPU work: shaders, compute, large particle or data scenes, post-processing.
Facts dated 2026-10 come from MDN, W3C WebGPU/WGSL specs, webgpufundamentals.org, three.js docs; re-verify on caniuse/MDN before a production commitment.

## Related skills (link, do not repeat)
- Rendering theory (PBR, IBL, shadows, color, engine choice): `graphics-rendering`
- Motion principles, CSS/WAAPI/GSAP/Lottie/Rive choice, reduced motion: `motion-animation`
- Design baseline and when 3D is worth it: `modern-web-design-standards`
- Generative 2D art in code: `anthropic-skills:algorithmic-art`; React animation patterns: `framer-motion-skill`
- Frame-perfect video from code: `motion-reel`, `hyperframes*`, `remotion-*`
- Browser verification of a canvas: `browser-testing-with-devtools` (real Chrome; screenshots can lie about motion)

## Decision gate (do this first)
1. Does the effect need GPU at all? Gradient, blur, parallax, scroll reveal: use CSS. Read `modern-web-design-standards`.
2. Scene graph, loaders, PBR, shadows needed: use three.js (`references/threejs-tsl.md`), not raw WebGPU.
3. Custom compute (particles 100k+, sim, filters, data-viz of 1M points) or one bespoke shader: raw WebGPU.
4. Need to reach everyone: three.js WebGPURenderer with automatic WebGL2 fallback, or raw WebGPU plus a WebGL2 path.
5. Heavy native-class scenes: Unreal or Godot export (see `graphics-rendering/references/engine-choice.md`).

## Workflow
1. Feature-detect: `if (!navigator.gpu) -> fallback`; then `await navigator.gpu.requestAdapter()`; null means no adapter, fallback.
2. Request only features you need (`adapter.features.has(...)`); request raised limits explicitly, defaults are low.
3. Configure canvas context with `navigator.gpu.getPreferredCanvasFormat()`, `alphaMode: "opaque"` unless compositing.
4. Build pipelines once, bind groups once, reuse. Per frame: write uniforms, encode, submit.
5. Size canvas to `clientWidth * devicePixelRatio` (clamp DPR to 2 on mobile), resize via ResizeObserver, never in rAF.
6. Wrap creation in error scopes during development; listen to `device.lost` and `uncapturederror`.
7. Respect `prefers-reduced-motion`; provide a static or paused frame and a keyboard/pause control.
8. Verify in real Chrome plus one non-Chromium browser; measure with timestamp queries, not guesses.

## Hard rules and pitfalls
- Uniform struct layout: `vec3f` aligns to 16 bytes, so pack a `f32` after it; mirror layout in JS with one `Float32Array` and named offsets. See `references/wgsl-reference.md`.
- `bytesPerRow` for texture-to-buffer copies must be a multiple of 256. Dynamic uniform offsets must be multiples of `minUniformBufferOffsetAlignment` (256 default).
- Read-write storage buffers are not usable in vertex stage; read-only storage is.
- `textureSample` needs uniform control flow; use `textureSampleLevel` or `textureLoad` inside branches or loops.
- Presenting: get `context.getCurrentTexture()` each frame, never cache it across frames.
- Destroy buffers and textures you no longer need (`.destroy()`), otherwise memory leaks until GC.
- Color: render HDR in `rgba16float`, tonemap once at the end, output format sRGB-encoded (`-srgb` view or manual encode). Never tonemap twice.
- Pipeline compile stalls: use `createRenderPipelineAsync` and warm up pipelines before the first visible frame.
- Do not read GPU results back per frame (`mapAsync` stalls); keep data on GPU, use indirect draws.
- `ShaderMaterial`, `RawShaderMaterial`, `onBeforeCompile` do not work in three.js WebGPURenderer; use TSL.

## Reference map (open only what the task needs)
| Need | File |
|---|---|
| Setup, buffers, textures, bind groups, pipelines, loop, resize, errors, fallback | `references/webgpu-core.md` |
| WGSL syntax, types, address spaces, alignment, builtins, pitfalls | `references/wgsl-reference.md` |
| Fullscreen shader, instancing, compute particles, GPU-driven animation | `references/recipes-basic.md` |
| Post chain (bloom, tonemap, FXAA, TAA), SDF raymarch, image filters, GPU chart | `references/recipes-advanced.md` |
| three.js WebGPURenderer, TSL, compute in three | `references/threejs-tsl.md` |
| Profiling, timestamp queries, debugging, mobile limits, a11y, support matrix | `references/perf-debug-a11y-support.md` |
| Tiny verified shader | `templates/fullscreen.wgsl`, `templates/fullscreen.html` |

## Learning sources (paraphrased, not copied)
W3C WebGPU and WGSL specs; MDN WebGPU API; webgpufundamentals.org; Chrome developer docs and Dawn; three.js WebGPURenderer manual and TSL wiki; Babylon.js WebGPU docs; wgpu (Rust, same API shape); Inigo Quilez articles (SDF, raymarching); The Book of Shaders; GPU Gems; Learn OpenGL.

## Output contract
Deliver runnable code (single HTML or module), the fallback path, the reduced-motion behavior, the support note with date, and the measured frame cost if a browser was available. State which parts are unverified.
