# three.js WebGPURenderer and TSL

Sources: three.js manual (WebGPURenderer page), TSL wiki, release notes. Version facts below were reported for r181 to r186 (2026) by secondary summaries; check the official GitHub release notes before pinning.

## Setup
```js
import * as THREE from "three/webgpu";            // WebGPU build, includes node materials and TSL
import { Fn, uniform, time, uv, vec3, color, mix, sin, positionLocal, instanceIndex, storage, float } from "three/tsl";

const renderer = new THREE.WebGPURenderer({ antialias: true, canvas });
await renderer.init();                             // required before first render
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setAnimationLoop(() => renderer.render(scene, camera));   // preferred over manual rAF
console.log(renderer.backend.isWebGPUBackend ? "webgpu" : "webgl2 fallback");
```
- Automatic WebGL2 fallback happens when WebGPU is missing; `forceWebGL: true` tests it.
- Compute does NOT run on the WebGL2 fallback in the general case (reported limits), so gate compute features on `renderer.backend.isWebGPUBackend` and provide a CPU or reduced path.
- `ShaderMaterial`, `RawShaderMaterial`, `onBeforeCompile` are unsupported here; port to TSL node materials. `WebGLRenderer` remains maintained and is still the recommendation for pure WebGL2 apps (per the manual, 2026-10).
- Reported API churn: `*Async` render/compute methods deprecated (r181), `colorBufferType` renamed `outputBufferType` (r182), `PostProcessing` renamed `RenderPipeline` and `Clock` deprecated for `Timer` (r183), non-blocking `compileAsync` (r184). Treat as "verify against the pinned version".

## TSL in one page
TSL is a JS node-graph DSL compiled to WGSL (or GLSL on fallback). You compose nodes, not strings.
```js
const mat = new THREE.MeshStandardNodeMaterial();
const pulse = sin(time.mul(2.0)).mul(0.5).add(0.5);                // time is a node
mat.colorNode = mix(color(0x2244ff), color(0xff8844), pulse);
mat.positionNode = positionLocal.add(vec3(0, sin(positionLocal.x.mul(4).add(time)).mul(0.1), 0));
mat.roughnessNode = float(0.4);
// custom function node
const fresnel = Fn(([n, v, p]) => float(1).sub(n.dot(v).saturate()).pow(p));
```
- Uniforms: `const k = uniform(1.0); k.value = 2.0;` updates without recompiling.
- Textures: `texture(tex, uv())`; varyings are automatic; `Loop`, `If`, `Break` exist as TSL control flow (not JS `if`, which runs at graph build time).
- Material slots: `colorNode, opacityNode, normalNode, emissiveNode, positionNode, roughnessNode, metalnessNode, outputNode, fragmentNode`.
- Debug: `node.debug()` style helpers and `renderer.debug` flags; the generated WGSL can be inspected in the compile logs.

## Compute in three
```js
const N = 200000;
const posBuf = storage(new THREE.StorageInstancedBufferAttribute(N, 3), "vec3", N);
const update = Fn(() => {
  const p = posBuf.element(instanceIndex);
  p.addAssign(vec3(0, time.sin().mul(0.001), 0));
})().compute(N);
renderer.compute(update);                        // per frame (sync form, after the *Async deprecation)
```
Render the same storage attribute through an instanced sprite/mesh node material (`positionNode` reading the buffer). For sorting, atomics, or workgroup memory use `workgroupArray`, `atomicAdd`, `workgroupBarrier` TSL helpers.

## Post-processing
```js
import { pass } from "three/tsl";
import { bloom } from "three/addons/tsl/display/BloomNode.js";
const scenePass = pass(scene, camera);
const out = scenePass.getTextureNode("output");
const post = new THREE.RenderPipeline(renderer, out.add(bloom(out, 0.4, 0.6, 0.9)));   // name per r183; older: PostProcessing
renderer.setAnimationLoop(() => post.render());
```
Prefer built-in nodes (bloom, FXAA, SMAA, TRAA, DoF, SSAO/GTAO, SSR, motion blur, film grain) over hand-rolled passes. Tonemapping: `renderer.toneMapping = THREE.ACESFilmicToneMapping | AgXToneMapping | NeutralToneMapping`, `renderer.toneMappingExposure`. Output color space stays sRGB.

## Choosing three vs raw WebGPU
three: scenes, glTF, PBR, shadows, controls, XR, ecosystem (drei-like helpers via react-three-fiber, which supports WebGPU renderer in recent versions, check). Raw: single bespoke effect, strict bundle size, custom compute pipeline that three does not model, learning. Bundle: three core is heavy (hundreds of KB gz); a raw shader is a few KB.

## Interop with the other skills
Asset prep: `graphics-rendering/references/assets-gltf.md` (Draco, Meshopt, KTX2 loaders). Camera moves and easing: `motion-animation`. Lazy-load the canvas below the fold; ship a poster image; follow `modern-web-design-standards` rules for when 3D is justified.
