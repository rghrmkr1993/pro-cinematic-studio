// Builds cues.json from the beat grid (120 BPM, beat = 0.5 s) + the hand-timed visual events in index.html.
import { writeFileSync } from 'node:fs';
const cues = [];
const add = (t, type, gain, bus = 'fx') => cues.push({ t: +t.toFixed(3), type, gain, bus });
// music bed: kick every beat, hat on offbeats, bass on downbeats (every 2 s)
for (let b = 0; b < 30; b++) { add(b * 0.5, 'kick', b % 2 ? 0.35 : 0.5, 'music'); add(b * 0.5 + 0.25, 'hat', 0.18, 'music'); if (b % 4 === 0) add(b * 0.5, 'bass', 0.35, 'music'); }
// scene 1: three lines land on beats, period arrives, sub line, exit
[0, 0.25, 0.5].forEach((t) => add(t + 0.05, 'thump', 0.6));
add(1.3, 'pop', 0.5); add(1.0, 'click', 0.35); add(1.1, 'click', 0.3);
[1.75, 2.0, 2.25].forEach((t) => add(t, 'click', 0.4));
add(3.0, 'whoosh', 0.4); add(3.5, 'whoosh', 0.7);
// scene 2: tile pops, hot hops, centre lock
for (let k = 0; k < 6; k++) add(4.15 + 0.1 * k, 'click', 0.25);
for (let h = 0; h < 6; h++) add(5.0 + 0.25 * h, 'click', 0.35);
add(6.5, 'thump', 0.7); add(6.75, 'whoosh', 0.4);
// scene 3: card morphs on beats, cursor clicks, typing, bars, tooltip
add(7.0, 'pop', 0.5); add(7.42, 'click', 0.6); add(7.5, 'pop', 0.5);
for (let c = 0; c < 14; c++) add(7.8 + 0.05 * c, 'click', 0.12);
add(8.92, 'click', 0.6); add(9.0, 'pop', 0.5); add(9.5, 'pop', 0.6); add(9.62, 'click', 0.4);
add(10.0, 'thump', 0.6); for (let i = 0; i < 7; i++) add(10.08 + 0.06 * i, 'click', 0.18);
add(10.3, 'pop', 0.45); add(11.0, 'pop', 0.5); add(11.5, 'whoosh', 0.5);
// scene 4: lockup
add(12.0, 'thump', 0.7); add(12.5, 'click', 0.4); add(13.0, 'pop', 0.6); add(14.0, 'whoosh', 0.45); add(14.1, 'thump', 0.4);
cues.sort((a, b) => a.t - b.t);
writeFileSync('cues.json', JSON.stringify(cues, null, 1));
console.log('cues.json', cues.length);
