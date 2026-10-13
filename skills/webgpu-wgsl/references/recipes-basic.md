# Recipes: basics (minimal templates, adapt then test)

Assume `device, ctx, format` from `webgpu-core.md` section 1. Each recipe lists WGSL plus the JS delta.

## 1. Fullscreen shader (see also templates/fullscreen.wgsl and .html)
Use one oversized triangle, no vertex buffer.
```wgsl
struct U { res: vec2f, time: f32, _p: f32 };
@group(0) @binding(0) var<uniform> u: U;
@vertex fn vs(@builtin(vertex_index) i: u32) -> @builtin(position) vec4f {
  let p = vec2f(f32((i << 1u) & 2u), f32(i & 2u));       // (0,0) (2,0) (0,2)
  return vec4f(p * 2.0 - 1.0, 0.0, 1.0);
}
@fragment fn fs(@builtin(position) fc: vec4f) -> @location(0) vec4f {
  let uv = (fc.xy * 2.0 - u.res) / min(u.res.x, u.res.y);
  return vec4f(0.5 + 0.5 * cos(u.time + uv.xyx + vec3f(0, 2, 4)), 1.0);
}
```
JS: uniform buffer 16 bytes `[w, h, t, 0]`, `pass.draw(3)`. Output in sRGB canvas needs gamma-correct math: values are written as-is to the canvas, so apply `pow(c, vec3f(1/2.2))` if you compute in linear.

## 2. Instancing (10k to 1M instances, one draw)
```wgsl
struct Inst { pos: vec2f, scale: f32, hue: f32 };
@group(0) @binding(0) var<uniform> u: U;                  // res, time
@group(0) @binding(1) var<storage, read> insts: array<Inst>;
struct VOut { @builtin(position) p: vec4f, @location(0) c: vec3f, @location(1) q: vec2f };
@vertex fn vs(@builtin(vertex_index) v: u32, @builtin(instance_index) i: u32) -> VOut {
  var corners = array<vec2f, 6>(vec2f(-1,-1), vec2f(1,-1), vec2f(-1,1), vec2f(-1,1), vec2f(1,-1), vec2f(1,1));
  let q = corners[v]; let d = insts[i];
  let aspect = vec2f(u.res.y / u.res.x, 1.0);
  var o: VOut; o.p = vec4f((d.pos + q * d.scale) * aspect, 0, 1);
  o.c = 0.5 + 0.5 * cos(6.283 * (d.hue + vec3f(0, .33, .67))); o.q = q; return o;
}
@fragment fn fs(o: VOut) -> @location(0) vec4f {
  let a = smoothstep(1.0, 0.8, length(o.q));              // soft disc
  return vec4f(o.c * a, a);                                // premultiplied alpha
}
```
JS: `pass.draw(6, count)`. Blend premultiplied: `color:{srcFactor:"one", dstFactor:"one-minus-src-alpha"}`, same for alpha. For meshes, pass a vertex buffer for geometry and a second `stepMode:"instance"` buffer for per-instance data. For 3D, store a `mat4x4f` or position+quaternion per instance. Sort translucent instances by depth or use additive blending (order independent).

## 3. Compute particles (100k to 1M+)
Particles live only on GPU: simulate in compute, render read-only from the same buffer.
```wgsl
struct P { pos: vec2f, vel: vec2f };
struct Sim { dt: f32, n: u32, mouse: vec2f };
@group(0) @binding(0) var<uniform> s: Sim;
@group(0) @binding(1) var<storage, read_write> ps: array<P>;
fn hash(x: u32) -> u32 { var h = x * 747796405u + 2891336453u; h = ((h >> ((h >> 28u) + 4u)) ^ h) * 277803737u; return (h >> 22u) ^ h; }
@compute @workgroup_size(64) fn sim(@builtin(global_invocation_id) id: vec3u) {
  let i = id.x; if (i >= s.n) { return; }                  // guard the tail workgroup
  var p = ps[i];
  let d = s.mouse - p.pos; let r2 = max(dot(d, d), 1e-3);
  p.vel += d / r2 * 0.05 * s.dt;                           // attraction
  p.vel *= pow(0.2, s.dt);                                 // frame-rate independent drag
  p.pos += p.vel * s.dt;
  if (abs(p.pos.x) > 1.0 || abs(p.pos.y) > 1.0) {          // respawn without CPU
    let h = hash(i + u32(s.dt * 1e6));
    p.pos = vec2f(f32(h & 1023u), f32((h >> 10u) & 1023u)) / 511.5 - 1.0; p.vel = vec2f(0);
  }
  ps[i] = p;
}
```
Render: same buffer bound `var<storage, read>` in the vertex shader, `draw(6, n)` quads or `topology:"point-list"` with `draw(n)` (points are 1px; quads give size). Dispatch `ceil(n/64)`; 256 is also common. Budget: 1M particles of 16 bytes is 16MB, easily 60fps on desktop GPUs; mobile start at 100k to 200k and measure. In-place update is safe here because each thread owns one element; neighbour interactions need ping-pong buffers or a spatial grid (counting sort with atomics, then 3x3 cell lookup).

## 4. GPU-driven animation
Move transform math off the CPU: upload clip data once, evaluate per frame in the vertex stage.
- Procedural: `pos = base + amp * sin(freq * time + phase)` per instance from the instance index hash; JS only updates `time`.
- Skinning: bone matrices in a storage buffer, vertex attributes `joints: vec4u`, `weights: vec4f`; blend `sum(w_k * bone[j_k])`. For crowds, bake animation into a texture (vertex animation texture, VAT) and sample by `time` and `vertex_index`.
- Morph targets: storage buffer of deltas, weights uniform, `pos += sum(w_k * delta_k[vi])`.
- GPU culling: compute pass tests instance bounds against frustum, appends visible indices with `atomicAdd` into a compact buffer and writes `instanceCount` into an indirect args buffer; then `drawIndirect`. Needs buffer usage `INDIRECT | STORAGE`; layout `[vertexCount, instanceCount, firstVertex, firstInstance]` as four u32. `firstInstance` non-zero requires `indirect-first-instance`.
- Tween on GPU: store `start, end, t0, duration, easing id` per instance and evaluate easing in the shader (see `motion-animation/references/principles-easing-timing.md` for curves). Zero per-frame CPU cost for 100k objects.

## Verification checklist
Console clean (no validation lines); resize keeps aspect; tab switch does not explode `dt`; `n` not multiple of 64 still correct; reduced-motion variant renders a still frame.
