// node mix.mjs -> out/final.mp4 (silent.mp4 + sfx.wav + music.wav, amix, two-pass loudnorm to -14 LUFS)
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
const V = 'out/silent.mp4', FX = 'out/sfx.wav', MU = 'out/music.wav';
const ins = [FX]; if (existsSync(MU)) ins.push(MU);
const inArgs = ['-i', V, ...ins.flatMap((f) => ['-i', f])];
const mix = ins.length > 1 ? '[1:a][2:a]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.5:level=false[m]' : '[1:a]anull[m]';
const LN = 'I=-14:TP=-1.5:LRA=11';
const p1 = spawnSync('ffmpeg', ['-hide_banner', ...inArgs, '-filter_complex', `${mix};[m]loudnorm=${LN}:print_format=json[o]`, '-map', '[o]', '-f', 'null', '-'], { encoding: 'utf8' });
const m = JSON.parse(p1.stderr.slice(p1.stderr.lastIndexOf('{'), p1.stderr.lastIndexOf('}') + 1));
const meas = `measured_I=${m.input_i}:measured_TP=${m.input_tp}:measured_LRA=${m.input_lra}:measured_thresh=${m.input_thresh}:offset=${m.target_offset}:linear=true`;
const p2 = spawnSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', ...inArgs, '-filter_complex', `${mix};[m]loudnorm=${LN}:${meas},aresample=48000[o]`,
  '-map', '0:v', '-map', '[o]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'out/final.mp4'], { stdio: 'inherit' });
if (p2.status !== 0) process.exit(1);
console.log('mixed out/final.mp4 (pre-measure input_i=' + m.input_i + ' LUFS)');
