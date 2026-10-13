# Recipes: advanced (post chain, SDF raymarch, filters, data viz)

## 1. Post-processing chain
Order: scene (HDR `rgba16float`, linear) -> bloom -> tonemap + grade -> sRGB output -> FXAA (on LDR) or TAA (before tonemap, on HDR with care).
Targets: scene HDR texture (RENDER_ATTACHMENT | TEXTURE_BINDING), bloom mip chain (half size per level, 5 to 6 levels), final to canvas.

### Bloom (dual filter, Call of Duty style, paraphrased from the public talk)
1. Prefilter: threshold with soft knee: `w = clamp(luma - thr + knee, 0, 2*knee)^2 / (4*knee + 1e-4)`, `c *= max(w, luma - thr) / max(luma, 1e-4)`. Typical thr 1.0 (HDR), knee 0.5.
2. Downsample chain with a 13-tap (or 4-tap bilinear) filter; first level uses a Karis average (weight by `1/(1+luma)`) to kill fireflies.
3. Upsample with a 3x3 tent, additive blend each level into the next larger (`blendOp add`, one + one).
4. Composite: `hdr + bloom * strength` (strength 0.03 to 0.15; more looks cheap). Do it before tonemapping.
```wgsl
@group(0) @binding(0) var src: texture_2d<f32>; @group(0) @binding(1) var smp: sampler;
@group(0) @binding(2) var<uniform> texel: vec2f;           // 1/srcSize
@fragment fn down(@location(0) uv: vec2f) -> @location(0) vec4f {   // uv from fullscreen vs
  var c = textureSampleLevel(src, smp, uv, 0).rgb * 4.0;
  c += textureSampleLevel(src, smp, uv + texel * vec2f(-1, -1), 0).rgb;
  c += textureSampleLevel(src, smp, uv + texel * vec2f( 1, -1), 0).rgb;
  c += textureSampleLevel(src, smp, uv + texel * vec2f(-1,  1), 0).rgb;
  c += textureSampleLevel(src, smp, uv + texel * vec2f( 1,  1), 0).rgb;
  return vec4f(c / 8.0, 1.0);                              // 5-tap approximate dual-Kawase down
}
```
### Tonemapping (one place, once)
```wgsl
fn aces(x: vec3f) -> vec3f {                               // Narkowicz ACES fit, good and cheap
  return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), vec3f(0), vec3f(1)); }
fn reinhard_ext(c: vec3f, wp: f32) -> vec3f { let l = dot(c, vec3f(.2126,.7152,.0722)); return c * (1.0 + l/(wp*wp)) / (1.0 + l); }
fn to_srgb(c: vec3f) -> vec3f { return select(1.055 * pow(c, vec3f(1.0/2.4)) - 0.055, 12.92 * c, c <= vec3f(0.0031308)); }
```
Alternatives: AgX (less hue skew, three.js `AgXToneMapping`), Khronos PBR Neutral (keeps product colors, good for e-commerce). Choice guide: `graphics-rendering/references/shadows-gi-color-aa.md`. Apply exposure (`c *= exp2(ev)`) before the curve. If the canvas format is `-srgb` the hardware encodes; do not also call `to_srgb`.

### FXAA (post-tonemap, LDR, one pass)
Compute luma of centre and 4 neighbours (N,S,E,W) plus corners; if `lumaMax - lumaMin < max(0.0312, 0.125*lumaMax)` return centre; otherwise detect edge orientation, blend along the edge by sub-pixel amount. Write luma into alpha in the previous pass or recompute. Use the public FXAA 3.11 quality preset 12 to 15 structure; it is cheap (about 0.3 ms at 1080p on mid GPUs, estimate).
### TAA (when you need clean thin geometry or temporal effects)
- Jitter projection with Halton(2,3) 8 to 16 samples, offset in NDC by `(j - 0.5) * 2 / res`.
- Motion vectors: write `currNDC - prevNDC` (or in UV) to an `rg16float` target in the geometry pass; moving objects need the previous model matrix.
- Resolve: reproject history by motion, clamp history to neighbourhood AABB (3x3 min/max, preferably in YCoCg, optionally variance clipping), blend `mix(history, current, 0.1)`; raise to 1.0 on disocclusion.
- Ping-pong two history textures. Reset on camera cut and resize. Sharpen lightly after (CAS) to counter blur.

## 2. SDF raymarching (Inigo Quilez techniques, paraphrased)
```wgsl
fn sdSphere(p: vec3f, r: f32) -> f32 { return length(p) - r; }
fn sdBox(p: vec3f, b: vec3f) -> f32 { let q = abs(p) - b; return length(max(q, vec3f(0))) + min(max(q.x, max(q.y, q.z)), 0.0); }
fn smin(a: f32, b: f32, k: f32) -> f32 { let h = max(k - abs(a - b), 0.0) / k; return min(a, b) - h * h * k * 0.25; } // polynomial smooth union
fn map(p: vec3f, t: f32) -> f32 {
  let s = sdSphere(p - vec3f(sin(t) * 0.8, 0, 0), 0.6);
  return smin(s, sdBox(p, vec3f(0.5)) - 0.05, 0.4);
}
fn normal(p: vec3f, t: f32) -> vec3f {                     // tetrahedron gradient, 4 taps
  let e = vec2f(1.0, -1.0) * 0.0005;
  return normalize(e.xyy * map(p + e.xyy, t) + e.yyx * map(p + e.yyx, t) + e.yxy * map(p + e.yxy, t) + e.xxx * map(p + e.xxx, t));
}
@fragment fn fs(@builtin(position) fc: vec4f) -> @location(0) vec4f {
  let uv = (fc.xy * 2.0 - u.res) / u.res.y * vec2f(1, -1);
  let ro = vec3f(0, 0, 3); let rd = normalize(vec3f(uv, -1.5));
  var d = 0.0; var hit = false;
  for (var i = 0; i < 96; i++) { let h = map(ro + rd * d, u.time); if (h < 0.001) { hit = true; break; } d += h; if (d > 10.0) { break; } }
  var col = vec3f(0.02, 0.03, 0.05);
  if (hit) { let p = ro + rd * d; let n = normal(p, u.time);
    let l = normalize(vec3f(0.6, 0.8, 0.4)); col = vec3f(0.9, 0.5, 0.3) * (max(dot(n, l), 0.0) + 0.1); }
  return vec4f(pow(col, vec3f(1.0 / 2.2)), 1.0);
}
```
Techniques: soft shadows via `res = min(res, k*h/t)` along the light ray; ambient occlusion from 5 samples along the normal; bounding volume test first to skip empty pixels; relax step count at distance (cone-based epsilon `0.001*d`); render at 0.5 resolution and upscale on mobile. Domain repetition: `p = mod(p + c/2, c) - c/2`. Do not ray-march complex scenes at full res on phones.

## 3. Image filters (compute + storage textures)
```wgsl
@group(0) @binding(0) var src: texture_2d<f32>;
@group(0) @binding(1) var dst: texture_storage_2d<rgba8unorm, write>;
@compute @workgroup_size(8, 8) fn blur(@builtin(global_invocation_id) id: vec3u) {
  let dim = textureDimensions(src); if (id.x >= dim.x || id.y >= dim.y) { return; }
  var acc = vec4f(0); let r = 4;
  for (var y = -r; y <= r; y++) { for (var x = -r; x <= r; x++) {
    let q = clamp(vec2i(id.xy) + vec2i(x, y), vec2i(0), vec2i(dim) - 1); acc += textureLoad(src, q, 0); } }
  textureStore(dst, vec2i(id.xy), acc / f32((2 * r + 1) * (2 * r + 1)));
}
```
Make it separable (horizontal then vertical, Gaussian weights) and stage a tile in `var<workgroup>` with a halo to cut texture fetches. Dispatch `ceil(w/8), ceil(h/8)`. Other filters: sharpen (unsharp mask), levels/curves via 1D LUT texture, 3D LUT color grading (`texture_3d`, trilinear), Sobel edges, bilateral denoise, histogram with `atomicAdd` into a 256-bin storage buffer. Source and destination must be different textures in the same pass.

## 4. GPU data-viz chart (1M points, scatter or line)
- Data: `Float32Array` of x,y (+ optional color/size channel) uploaded once to a STORAGE buffer; scale/offset (pan and zoom) in a uniform, updated per interaction.
- Vertex shader reads `pts[instance_index]`, maps `(x - view.x0) / (view.x1 - view.x0)` to clip, expands a quad of fixed pixel size (`size_px / res * 2`). Alpha-blend with small alpha (0.05 to 0.3) for density; or additive blend into `rgba16float` and colormap (viridis LUT 256x1 texture) in a final pass for a density heatmap.
- Lines: expand each segment to a quad in the vertex shader using neighbour points; round joins with extra instances. For time series of 10M points, downsample on GPU (min/max per pixel column via compute with atomics).
- Picking: render ids to an `r32uint` target at the pointer only (scissor 1x1) then read back one pixel asynchronously, or do a compute nearest search.
- Axes, ticks, labels, tooltips: draw in DOM/SVG or a 2D canvas overlay, not in WebGPU, so text stays crisp and accessible.
- Accessibility: expose a `<table>` or summary text and keyboard-navigable data, `role="img"` plus `aria-label` on the canvas. See `perf-debug-a11y-support.md`. For general chart design see skill `dataviz`.
