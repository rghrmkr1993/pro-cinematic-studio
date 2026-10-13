// Fullscreen animated shader. One oversized triangle, no vertex buffer.
// Uniform layout (16 bytes): res (vec2f, offset 0), time (f32, offset 8), _pad (f32, offset 12).
// Syntax checked by reading only; not compiled in a browser.

struct U {
  res: vec2f,
  time: f32,
  _pad: f32,
};
@group(0) @binding(0) var<uniform> u: U;

@vertex
fn vs(@builtin(vertex_index) i: u32) -> @builtin(position) vec4f {
  let p = vec2f(f32((i << 1u) & 2u), f32(i & 2u)); // (0,0) (2,0) (0,2)
  return vec4f(p * 2.0 - 1.0, 0.0, 1.0);
}

@fragment
fn fs(@builtin(position) fc: vec4f) -> @location(0) vec4f {
  let uv = (fc.xy * 2.0 - u.res) / min(u.res.x, u.res.y);
  let t = u.time;
  let d = length(uv);
  let ring = 0.5 + 0.5 * cos(8.0 * d - 2.0 * t + vec3f(0.0, 2.0, 4.0));
  let col = ring * smoothstep(1.4, 0.2, d);
  return vec4f(col, 1.0); // canvas format is non-srgb in this template, values are display-ready
}
