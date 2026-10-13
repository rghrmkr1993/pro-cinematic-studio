// node critique.mjs [stripAtSeconds=4.1] -> out/contact.png strip.png phone.png poster.png loop_check.mp4 + loop seam PSNR
import { spawnSync } from 'node:child_process';
const at = process.argv[2] || '4.1';
const F = 'out/final.mp4';
const ff = (args) => { const r = spawnSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', ...args], { encoding: 'utf8' }); if (r.status) { console.error(r.stderr); process.exit(1); } return r; };
ff(['-i', F, '-vf', 'fps=2,scale=270:-1,tile=6x5', '-frames:v', '1', '-update', '1', 'out/contact.png']);
ff(['-ss', at, '-i', F, '-vf', 'scale=320:-1,tile=12x1', '-frames:v', '1', '-update', '1', 'out/strip.png']);   // 12 consecutive frames
ff(['-i', F, '-vf', 'fps=1,scale=360:-1,tile=5x3', '-frames:v', '1', '-update', '1', 'out/phone.png']);
ff(['-ss', '0.9', '-i', F, '-frames:v', '1', '-update', '1', 'out/poster.png']);
ff(['-stream_loop', '1', '-i', F, '-c', 'copy', 'out/loop_check.mp4']);
// loop seam: last frame vs first frame
ff(['-i', F, '-frames:v', '1', '-update', '1', 'out/_first.png']);
ff(['-sseof', '-0.05', '-i', F, '-update', '1', '-frames:v', '1', 'out/_last.png']);
const r = spawnSync('ffmpeg', ['-hide_banner', '-i', 'out/_last.png', '-i', 'out/_first.png', '-lavfi', 'psnr', '-f', 'null', '-'], { encoding: 'utf8' });
console.log('loop seam last->first:', (r.stderr.match(/average:[^\s]+/) || ['n/a'])[0], '(inf = identical, >40 dB = invisible)');
