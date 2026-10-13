// node sfx.mjs cues.json out/sfx.wav
// cues: [{t, type, gain?, bus?}]. Writes sfx.wav (bus fx) and music.wav (bus music) beside it. 16-bit mono 48 kHz.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
const SR = 48000, TAIL = 0.6, TAU = Math.PI * 2;
const [cuesPath = 'cues.json', outPath = 'out/sfx.wav'] = process.argv.slice(2);
const cues = JSON.parse(readFileSync(cuesPath, 'utf8'));
const DUR = Number(process.env.DUR || 15);
const rng = (seed) => () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
// voice: length in seconds + sample function of seconds-since-start
const V = {
  click: { len: 0.12, f: (x) => Math.sin(TAU * 1800 * x) * Math.exp(-x * 60) },
  pop: { len: 0.2, f: (x) => Math.sin(TAU * (300 + 900 * (1 - Math.exp(-x * 40))) * x) * Math.exp(-x * 22) },
  thump: { len: 0.6, f: (x) => Math.sin(TAU * (90 - 40 * x) * x) * Math.exp(-x * 7) * 1.2 },
  whoosh: { len: 0.7, f: (x, r) => (r() * 2 - 1) * Math.sin(Math.PI * Math.min(1, x / 0.7)) ** 2 * 0.6 },
  kick: { len: 0.3, f: (x) => Math.sin(TAU * (50 + 90 * Math.exp(-x * 30)) * x) * Math.exp(-x * 12) },
  hat: { len: 0.06, f: (x, r) => (r() * 2 - 1) * Math.exp(-x * 90) * 0.5 },
  bass: { len: 0.45, f: (x) => (Math.sin(TAU * 55 * x) + 0.3 * Math.sin(TAU * 110 * x)) * Math.exp(-x * 5) * 0.8 },
};
function render(bus) {
  const buf = new Float32Array(Math.ceil((DUR + TAIL) * SR));
  cues.filter((c) => (c.bus || 'fx') === bus).forEach((c, n) => {
    const v = V[c.type]; if (!v) throw new Error('unknown voice ' + c.type);
    const r = rng(1000 + n), s0 = Math.round(c.t * SR), g = c.gain ?? 0.5, len = Math.round(v.len * SR);
    for (let i = 0; i < len && s0 + i < buf.length; i++) buf[s0 + i] += v.f(i / SR, r) * g;
  });
  return buf;
}
function wav(buf) {
  const pcm = Buffer.alloc(buf.length * 2);
  let peak = 0; for (const s of buf) peak = Math.max(peak, Math.abs(s));
  const norm = peak > 0.95 ? 0.95 / peak : 1;
  buf.forEach((s, i) => pcm.writeInt16LE(Math.round(Math.max(-1, Math.min(1, s * norm)) * 32767), i * 2));
  const h = Buffer.alloc(44);
  h.write('RIFF', 0); h.writeUInt32LE(36 + pcm.length, 4); h.write('WAVEfmt ', 8); h.writeUInt32LE(16, 16);
  h.writeUInt16LE(1, 20); h.writeUInt16LE(1, 22); h.writeUInt32LE(SR, 24); h.writeUInt32LE(SR * 2, 28);
  h.writeUInt16LE(2, 32); h.writeUInt16LE(16, 34); h.write('data', 36); h.writeUInt32LE(pcm.length, 40);
  return Buffer.concat([h, pcm]);
}
mkdirSync(dirname(outPath), { recursive: true });
writeFileSync(outPath, wav(render('fx')));
if (cues.some((c) => c.bus === 'music')) writeFileSync(join(dirname(outPath), 'music.wav'), wav(render('music')));
console.log('wrote', outPath, cues.length, 'cues');
