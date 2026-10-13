# Performance, debugging, mobile, accessibility, support

## Profiling with timestamp queries
Needs feature `timestamp-query` (requested at device creation). Chrome quantises timestamps for security unless the "WebGPU developer features" flag is on, so values are coarse (about 100 us, estimate); average over many frames.
```js
const qs = device.createQuerySet({ type: "timestamp", count: 2 });
const resolve = device.createBuffer({ size: 16, usage: GPUBufferUsage.QUERY_RESOLVE | GPUBufferUsage.COPY_SRC });
const read = device.createBuffer({ size: 16, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
const pass = enc.beginRenderPass({ colorAttachments, timestampWrites: { querySet: qs, beginningOfPassWriteIndex: 0, endOfPassWriteIndex: 1 } });
// ... after pass.end():
enc.resolveQuerySet(qs, 0, 2, resolve, 0); enc.copyBufferToBuffer(resolve, 0, read, 0, 16);
// later, when previous frame's read buffer is free:
await read.mapAsync(GPUMapMode.READ); const [a, b] = new BigUint64Array(read.getMappedRange().slice(0)); read.unmap();
const ms = Number(b - a) / 1e6;
```
Keep a small pool of read buffers (skip a frame if still mapped). Never block the frame on it.

## Frame budget
60 fps = 16.7 ms, 120 fps = 8.3 ms total including JS, GPU, and compositor. Target GPU time of 8 ms at 60 fps for headroom on laptops, 4 ms on phones (estimate). Measure CPU (`performance.now` around encode) and GPU separately.

## Optimisation order
1. Resolution: render at 0.5 to 0.75 scale and upscale for heavy fragment work; dynamic resolution on frame-time overrun.
2. Overdraw and fragment cost (raymarch steps, big blurs, many translucent layers). Half-res bloom and SSAO.
3. Draw calls: instancing, merged geometry, render bundles. 1 draw for 1M instances beats 1000 draws.
4. Bandwidth: `rgba16float` only where needed, `rg11b10ufloat` for bloom chain where renderable, compressed textures (KTX2), mipmaps, smaller storage structs (pack to u32/f16).
5. Compute: workgroup size 64 or 128 is a safe default; check occupancy by trying 32/64/128/256; coalesced access (adjacent threads read adjacent elements); avoid atomics contention (per-workgroup partials, then merge).
6. CPU: avoid per-frame object creation, reuse typed arrays and bind groups, batch `writeBuffer` into one big write.
7. Pipeline compile hitches: warm up all variants during load.

## Debugging
- Black canvas: console validation errors first; `getCompilationInfo()`; wrong `format` between pass and pipeline; forgot `pass.end()`; swapchain texture not re-fetched; depth texture size mismatch after resize; NaN in uniforms.
- Tools: Chrome DevTools Performance panel (GPU track) and Chrome `chrome://gpu`; Spector.js is WebGL only; WebGPU Inspector extension (record and replay frames, view buffers); `device.label` and `pass.pushDebugGroup("bloom")` names appear in captures. Native debugging via wgpu or Dawn with RenderDoc or PIX when reproducible outside the browser.
- Debug views: output normals, depth, UVs, overdraw as color; readback one buffer in dev builds (never production).
- Floating errors: NaN propagates into bloom and TAA (whole screen goes black). Clamp inputs with `max(x, 0)` and `select(c, vec3f(0), c != c)`.
- Device lost: simulate with `device.destroy()` and test your recovery path.

## Mobile and low-end limits (estimates unless noted)
- Default limits are conservative on mobile: texture dimension 8192 typical, 4 bind groups, 16KB workgroup storage, 256 invocations per workgroup, 8 sampled textures per stage min. Query `adapter.limits` and degrade gracefully.
- Thermal throttling hits after 10 to 30 s: cap DPR at 2 (1.5 on low-end), 30 fps option, pause offscreen, reduce particle count by device tier.
- Memory: full-screen `rgba16float` at 1440x3120 (about 4.5 MP) is 36 MB per target; count your targets.
- Tile-based GPUs (most phones): avoid many render passes with load/store of big targets; prefer fewer passes, `loadOp: "clear"`, `storeOp: "discard"` for depth you do not read.
- Tier detection: combine `adapter.limits`, `navigator.hardwareConcurrency`, `deviceMemory` (Chromium only), and a 1 s warm-up frame-time probe; then pick quality preset. Persist the choice.
- Battery: use `powerPreference: "low-power"` for ambient decorative canvases.

## Accessibility
- `prefers-reduced-motion: reduce`: render a single still frame or very slow, low-amplitude motion; stop particle and camera animation; keep interactions that the user starts. `matchMedia("(prefers-reduced-motion: reduce)")` and listen to `change`.
- Provide Pause/Play control (WCAG 2.2.2 for motion over 5 s) and never flash more than 3 times per second (WCAG 2.3.1); avoid large-area strobing and fast parallax or vection effects (vestibular triggers).
- Canvas is opaque to assistive tech: `role="img"` with `aria-label` for decorative or informative scenes; for interactive 3D give keyboard controls (arrows to orbit, +/- zoom), visible focus, and a text alternative or data table. Decorative: `aria-hidden="true"`.
- Contrast of overlaid text over animated backgrounds must hold at the worst frame; keep text in DOM, not in the shader.
- Also honour `prefers-contrast` and `prefers-color-scheme` where the scene carries UI. Shared guidance: `motion-animation/references/performance-a11y.md`.

## Browser support matrix (as of 2026-10-13; secondary sources, verify on caniuse/MDN)
| Browser | WebGPU | Notes |
|---|---|---|
| Chrome / Edge desktop | Yes since 113 (2023-04) | Windows, macOS, ChromeOS; Linux limited to certain GPUs/drivers (reported Intel Gen12+, recent NVIDIA) |
| Chrome Android | Yes (Android 12+, Qualcomm/ARM per Chrome docs, verify) | Samsung Internet 24+ inherits Chromium |
| Safari | Yes, Safari 26 (shipped 2025-09) on macOS Tahoe 26, iOS 26, iPadOS 26 | Older OS versions have no WebGPU |
| Firefox | Yes from 141 on Windows (2025-07); 145 on Apple Silicon macOS 26 | Linux and Android not default as of this date; Android reported as late-2026 target |
| Others | Opera, Brave, Vivaldi follow Chromium | |
Some commentary calls this "Baseline 2026"; treat as unconfirmed until MDN's Baseline data says so. WebGL2 is near-universal; keep it as the fallback. Related platform features (dated 2026-10): CSS scroll-driven animations are in Chrome 115+, Safari 26, still flagged in Firefox 152 stable; see `motion-animation/references/web-stack.md`.
Check availability at runtime, never by user-agent sniffing: `navigator.gpu` plus a successful `requestAdapter()`. WebGPU requires a secure context (HTTPS or localhost) and may be blocked in cross-origin iframes without `allow` policy.
