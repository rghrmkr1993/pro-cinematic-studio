# WGSL reference (W3C WGSL spec, webgpufundamentals.org)

## Types and syntax
- Scalars: `bool, i32, u32, f32`, `f16` (needs `enable f16;` and `shader-f16` feature). No implicit conversions: `f32(i)`, `u32(x)`, `bitcast<u32>(f)`.
- Vectors: `vec2f vec3f vec4f vec2i vec3u vec4<f32>`. Matrices: `mat4x4f` (column-major, `m * v`). Swizzle: `v.xyz`, `c.rgb`.
- Arrays: `array<T, N>` fixed, `array<T>` runtime-sized (storage only; `arrayLength(&buf)`).
- Declarations: `let` immutable, `var` mutable, `const` compile-time, `override` pipeline-time constant.
- Functions: `fn name(a: f32) -> vec4f { ... }`; entry points: `@vertex`, `@fragment`, `@compute @workgroup_size(64)`.
- No recursion, no pointers to arbitrary memory (`ptr<function, T>` params allowed), no `while` break rules beyond `break/continue`. `for (var i = 0u; i < n; i++)`. `switch` needs a `default`.
- Struct members need `@location(n)` (stage IO) or builtin attributes; trailing commas fine.

## Address spaces
| Space | Declared as | Access | Notes |
|---|---|---|---|
| function | `var x` in function | rw | per invocation |
| private | `var<private> x` | rw | per invocation, module scope |
| workgroup | `var<workgroup> t: array<f32,64>` | rw | shared in workgroup, compute only; needs `workgroupBarrier()` |
| uniform | `@group(0) @binding(0) var<uniform> u: U` | read | 64KB default max, strict layout |
| storage | `var<storage, read>` / `var<storage, read_write>` | r / rw | large (128MB default binding cap); rw not in vertex stage |
| handle | textures, samplers | | `@group @binding` only |

## Alignment and size (host layout must match)
| Type | Align | Size |
|---|---|---|
| f32, i32, u32 | 4 | 4 |
| vec2f | 8 | 8 |
| vec3f | 16 | 12 |
| vec4f | 16 | 16 |
| mat4x4f | 16 | 64 |
| mat3x3f | 16 | 48 (three padded columns) |
| struct | max member align | rounded up to align |
| array<T,N> | align(T) | N * roundUp(align(T), size(T)) |

Rules that bite:
- A `vec3f` followed by `f32` packs: `{ v: vec3f, s: f32 }` is 16 bytes. Two vec3f need padding between them.
- In `uniform`, array element stride must be a multiple of 16: `array<f32, 8>` fails; use `array<vec4f, 2>` and index `.x/.y` or a `vec4f` wrapper.
- Struct member offsets are rounded up to member align: `{ a: f32, b: vec2f }` puts `b` at offset 8.
- Prefer `vec4f` or explicit `_pad: f32` members. Verify offsets with a helper:
```js
function pack(fields){ // fields: [["time",1],["res",2],["mouse",2]] sizes in floats; add pads manually per table
  const a = new Float32Array(fields.reduce((s,f)=>s+f[1],0)); return a; }
```
- Storage buffers share these alignment rules for structs (only the array stride relaxation differs). Safest: make every struct member `vec4f` or `f32` pairs and test with a readback once.

## Built-ins
Vertex in: `@builtin(vertex_index) vi: u32`, `@builtin(instance_index) ii: u32`. Vertex out: `@builtin(position) pos: vec4f`.
Fragment in: `@builtin(position) frag: vec4f` (pixel coords, origin top-left, +0.5 centres), `@builtin(front_facing)`, `@builtin(sample_index)`. Out: `@location(0) vec4f`, optional `@builtin(frag_depth)`.
Compute in: `global_invocation_id`, `local_invocation_id`, `workgroup_id`, `local_invocation_index`, `num_workgroups`.

## Functions you use daily
Math: `abs, sign, floor, ceil, fract, mix, step, smoothstep, clamp, saturate, min, max, pow, exp, log, sqrt, inverseSqrt, sin, cos, atan2, length, distance, dot, cross, normalize, reflect, refract, fma`.
Textures: `textureSample(t,s,uv)` (fragment, uniform control flow), `textureSampleLevel(t,s,uv,lod)`, `textureLoad(t, vec2i, lod)`, `textureStore(st, vec2i, color)`, `textureDimensions(t)`, `textureGather`.
Sync/atomic: `workgroupBarrier()`, `storageBarrier()`, `atomicAdd(&a, v)`, `atomicMax`, `atomicLoad/Store` on `atomic<u32|i32>`.
Derivatives (fragment, uniform flow): `dpdx, dpdy, fwidth`.
Pack: `pack4x8unorm`, `unpack4x8unorm`, `pack2x16float`.

## Coordinate conventions
- Clip space: x,y in [-1,1], z in [0,1] (not [-1,1] as in OpenGL). Y up in clip, framebuffer origin top-left. UV (0,0) top-left of texture.
- Use a projection matrix built for 0..1 depth (e.g. gl-matrix `perspectiveZO`, wgpu-matrix `mat4.perspective`).
- Reverse-Z with `depthCompare: "greater"` and clear depth 0 improves far precision; use `depth32float`.

## Common pitfalls
1. Missing `@location` or mismatched vertex/fragment IO: validation error naming the stage.
2. `textureSample` inside `if` or loop on non-uniform data: error. Compute `textureSampleLevel` instead.
3. Integer divide or modulo by zero yields an unspecified value, not a trap; guard it.
4. `f32` modulo `%` has sign of the dividend; use `x - y*floor(x/y)` for GLSL-style `mod`.
5. `select(f, t, cond)` argument order is false-value first. Both branches always evaluate.
6. Uniform `array<f32,N>` stride error (see above). Matrices in uniforms need 16-byte alignment.
7. Workgroup memory is uninitialised; zero it yourself. Total workgroup memory default cap 16KB.
8. Race conditions: threads writing neighbours in place need ping-pong buffers or barriers.
9. Using `var` for constants inside hot loops is fine, but `let` helps the compiler; `const` arrays can be indexed dynamically only after copying to `var`.
10. Precision: `f32` time values above about 1e5 seconds lose sub-frame precision; wrap with `fract` or pass `time % period` from JS.
11. `discard` demotes the invocation to a helper (derivatives still work, writes are dropped); for soft cutouts prefer alpha blending or alpha-to-coverage.
12. Name clashes with reserved words (`filter`, `target`, `sample`, `mod`, `const_assert` family): rename the variable.
13. Entry point names must be unique per module only when used by the same stage; use explicit `entryPoint` in JS.
14. Builtin `position` in fragment is pixel space, in vertex output it is clip space. Divide by resolution for UV.

## Minimal mental model of a frame
Vertex stage maps vertices to clip space, rasteriser makes fragments, fragment writes color(s), blending and depth test merge into attachments. Compute runs independently, communicating only via storage buffers or storage textures. Order inside one command buffer is preserved; barriers are implicit between passes.
