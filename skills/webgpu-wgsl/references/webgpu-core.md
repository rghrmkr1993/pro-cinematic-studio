# WebGPU core

Concept map (spec: W3C WebGPU; tutorials: webgpufundamentals.org, MDN).
Adapter = a physical/software GPU. Device = logical connection, owns every resource. Queue = submits command buffers.

## 1. Init with detection and fallback
```js
async function initGPU(canvas) {
  if (!navigator.gpu) return { kind: "none" };            // go to WebGL2 path
  const adapter = await navigator.gpu.requestAdapter({ powerPreference: "high-performance" });
  if (!adapter) return { kind: "none" };
  const want = ["timestamp-query", "float32-filterable", "shader-f16"].filter(f => adapter.features.has(f));
  const device = await adapter.requestDevice({
    requiredFeatures: want,
    requiredLimits: {                                       // defaults are low; ask only for what you use
      maxStorageBufferBindingSize: Math.min(adapter.limits.maxStorageBufferBindingSize, 1 << 30),
      maxBufferSize: Math.min(adapter.limits.maxBufferSize, 1 << 30),
    },
  });
  device.lost.then(info => { console.warn("device lost", info.reason); /* if reason!=="destroyed": re-init */ });
  device.addEventListener("uncapturederror", e => console.error(e.error.message));
  const ctx = canvas.getContext("webgpu");
  const format = navigator.gpu.getPreferredCanvasFormat(); // rgba8unorm or bgra8unorm
  ctx.configure({ device, format, alphaMode: "opaque" });
  return { kind: "webgpu", device, ctx, format, features: device.features };
}
```
Feature names (dated 2026-10, verify per browser): `timestamp-query`, `float32-filterable`, `shader-f16`, `indirect-first-instance`, `bgra8unorm-storage`, `texture-compression-bc|etc2|astc`, `depth-clip-control`, `rg11b10ufloat-renderable`, `subgroups` (newer, check support), `dual-source-blending`.

## 2. WebGL2 fallback pattern
Keep one interface: `{ resize(w,h), frame(t), destroy() }`. Pick the implementation at startup.
- Fullscreen or simple effects: port WGSL to GLSL ES 3.00; same math, `gl_FragCoord` replaces `@builtin(position)`.
- Compute is not available: do particles with transform feedback or float-texture ping-pong, lower count (10k to 50k), or ship a static image or video poster.
- Easiest route: three.js `WebGPURenderer` falls back to WebGL2 automatically (see `threejs-tsl.md`).
- Last tier: a pre-rendered poster/video (`motion-reel`) and a `<noscript>`/no-GPU message. Never a blank canvas.

## 3. Buffers
Usage flags combine: `VERTEX, INDEX, UNIFORM, STORAGE, INDIRECT, COPY_SRC, COPY_DST, MAP_READ, MAP_WRITE, QUERY_RESOLVE`.
```js
const buf = device.createBuffer({ size: bytes, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST });
device.queue.writeBuffer(buf, 0, float32Array);            // simplest upload path
const init = device.createBuffer({ size, usage: GPUBufferUsage.VERTEX, mappedAtCreation: true });
new Float32Array(init.getMappedRange()).set(data); init.unmap(); // big one-time init, no staging copy
```
Size must be a multiple of 4. Readback: copy to a `MAP_READ|COPY_DST` buffer, `await mapAsync(GPUMapMode.READ)`, copy out, `unmap()`. Debug and screenshots only.

## 4. Textures and samplers
```js
const tex = device.createTexture({ size:[w,h], format:"rgba8unorm",
  usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST | GPUTextureUsage.RENDER_ATTACHMENT });
const bmp = await createImageBitmap(blob, { colorSpaceConversion: "none" });
device.queue.copyExternalImageToTexture({ source: bmp }, { texture: tex }, [w, h]);
const smp = device.createSampler({ magFilter:"linear", minFilter:"linear", addressModeU:"repeat" });
```
- Use `rgba8unorm-srgb` for color albedo (hardware decodes to linear), `rgba8unorm` for data (normals, masks).
- Mipmaps: WebGPU has no `generateMipmap`; blit with a small render pass per level (or a library) and set `mipLevelCount`.
- HDR targets: `rgba16float` (renderable, blendable); `rgba32float` is not filterable without `float32-filterable`.
- Storage textures: `texture_storage_2d<rgba8unorm, write>`; usage `STORAGE_BINDING`. `bgra8unorm` storage needs the feature.
- Video: `device.importExternalTexture({ source: videoEl })` valid for the current frame only; rebuild the bind group each frame.
- Compressed textures (KTX2 Basis to BC7/ASTC/ETC2): pick format by `adapter.features`; see `graphics-rendering/references/assets-gltf.md`.

## 5. Bind groups and layouts
Group by update frequency: group 0 per-frame (camera, time), group 1 per-material, group 2 per-object. `layout: "auto"` is fine for single pipelines; use explicit layouts when several pipelines share bind groups. Max 4 bind groups by default. Bind groups are immutable: to change a resource, create a new bind group (cheap, cache them).

## 6. Pipelines
```js
const module = device.createShaderModule({ code: wgsl });
const pipeline = await device.createRenderPipelineAsync({
  layout: "auto",
  vertex:   { module, entryPoint: "vs", buffers: [] },
  fragment: { module, entryPoint: "fs", targets: [{ format }] },
  primitive: { topology: "triangle-list", cullMode: "back" },
  depthStencil: { format: "depth24plus", depthWriteEnabled: true, depthCompare: "less" },
  multisample: { count: 4 },                                // MSAA is 1 or 4 only
});
const compute = await device.createComputePipelineAsync({ layout:"auto", compute:{ module, entryPoint:"main" } });
```
Check `await module.getCompilationInfo()` in dev for WGSL errors with line numbers. Override constants (`override`) specialise shaders without string edits.

## 7. Frame loop and resizing
```js
const ro = new ResizeObserver(([e]) => {
  const dpr = Math.min(devicePixelRatio, 2);
  const size = e.devicePixelContentBoxSize?.[0];            // exact device pixels where supported
  canvas.width  = Math.max(1, Math.min(device.limits.maxTextureDimension2D, size ? size.inlineSize : Math.round(e.contentRect.width * dpr)));
  canvas.height = Math.max(1, Math.min(device.limits.maxTextureDimension2D, size ? size.blockSize  : Math.round(e.contentRect.height * dpr)));
  recreateSizeDependentTextures();                          // depth, HDR, bloom chain
});
ro.observe(canvas, { box: "device-pixel-content-box" });
let last = 0;
function frame(now) {
  const dt = Math.min((now - last) / 1000, 0.05); last = now; // clamp dt after tab switch
  device.queue.writeBuffer(uniformBuf, 0, uniforms);
  const enc = device.createCommandEncoder();
  const pass = enc.beginRenderPass({ colorAttachments: [{
    view: ctx.getCurrentTexture().createView(), clearValue: [0,0,0,1], loadOp: "clear", storeOp: "store" }] });
  pass.setPipeline(pipeline); pass.setBindGroup(0, bg); pass.draw(3); pass.end();
  device.queue.submit([enc.finish()]);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
```
Pause on `document.hidden` and when the canvas is off-screen (IntersectionObserver). Render on demand for static scenes.

## 8. Error scopes
```js
device.pushErrorScope("validation");
const p = device.createRenderPipeline(desc);
const err = await device.popErrorScope();
if (err) console.error(err.message);
```
Filters: `"validation"`, `"out-of-memory"`, `"internal"`. Validation errors are otherwise logged and the failing command becomes a no-op, so a black canvas often means a swallowed validation error: open the console first.

## 9. Compute dispatch
```js
const pass = enc.beginComputePass(); pass.setPipeline(compute); pass.setBindGroup(0, bg);
pass.dispatchWorkgroups(Math.ceil(n / 64)); pass.end();   // limit 65535 per dimension, fold into 2D for more
```
Indirect: `pass.dispatchWorkgroupsIndirect(buf, offset)` and `renderPass.drawIndirect(buf, offset)` let the GPU decide counts (GPU-driven culling, see `recipes-basic.md`).

## 10. Render bundles and lifecycle
Pre-record static draws with `device.createRenderBundleEncoder` and replay with `pass.executeBundles`. On `device.lost` with reason other than `"destroyed"`, rebuild adapter, device, and all resources. Call `device.destroy()` on teardown (SPA route change).
