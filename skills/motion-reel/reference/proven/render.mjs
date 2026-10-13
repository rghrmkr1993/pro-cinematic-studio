// node render.mjs --fps 60 --dur 15 --sub 4 [--from 0] [--out out/silent.mp4] [--w 1080 --h 1920]
import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { resolve, dirname } from 'node:path';
import { launch } from './lib/browser.mjs';
const argv = process.argv;
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i > 0 ? Number(argv[i + 1]) : d; };
const sarg = (k, d) => { const i = argv.indexOf('--' + k); return i > 0 ? argv[i + 1] : d; };
const FPS = arg('fps', 60), DUR = arg('dur', 15), SUB = arg('sub', 4), FROM = arg('from', 0);
const W = arg('w', 1080), H = arg('h', 1920);
const OUT = sarg('out', 'out/silent.mp4');
mkdirSync(dirname(resolve(OUT)), { recursive: true });
const browser = await launch();
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on('pageerror', (e) => { console.error('PAGE ERROR', e.message); process.exitCode = 2; });
page.on('console', (m) => { if (m.type() === 'error') console.error('PAGE CONSOLE', m.text()); });
await page.goto(pathToFileURL(resolve('index.html')).href);   // Windows safe (file:///C:/...)
await page.evaluate(() => document.fonts.ready);
const vf = SUB > 1 ? `tmix=frames=${SUB},select='eq(mod(n\,${SUB})\,${SUB - 1})',setpts=N/${FPS}/TB` : `setpts=N/${FPS}/TB`;
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS * SUB), '-i', '-',
  '-vf', vf, '-r', String(FPS), '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p',
  '-fflags', '+bitexact', '-flags:v', '+bitexact', '-map_metadata', '-1', '-movflags', '+faststart', OUT],
  { stdio: ['pipe', 'inherit', 'inherit'] });
let ffErr = null;
ff.stdin.on('error', (e) => { ffErr = e; });                  // EPIPE if ffmpeg dies early
const done = new Promise((r) => ff.on('close', r));
const hash = createHash('md5');
const total = Math.round(DUR * FPS * SUB);
const t0 = Date.now();
for (let i = 0; i < total && !ffErr; i++) {
  const b64 = await page.evaluate((t) => { window.seek(t); return document.getElementById('c').toDataURL('image/png').slice(22); }, FROM + i / (FPS * SUB));
  const png = Buffer.from(b64, 'base64');
  hash.update(png);
  if (!ff.stdin.write(png)) await new Promise((r) => ff.stdin.once('drain', r));
  if (i % (FPS * SUB) === 0) process.stderr.write(`\r${(i / SUB / FPS).toFixed(0)}s / ${DUR}s  `);
}
ff.stdin.end();
const code = await done;
await browser.close();
const fh = hash.digest('hex');
writeFileSync(OUT + '.framehash', fh + '\n');
console.log(`\nrendered ${OUT} in ${((Date.now() - t0) / 1000).toFixed(1)}s ffmpeg=${code} subframe-png-md5=${fh}`);
if (code !== 0 || ffErr) { console.error('ffmpeg failed', ffErr && ffErr.message); process.exit(1); }
