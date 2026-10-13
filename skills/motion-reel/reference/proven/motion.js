// Classic-script UMD (works from file:// where ES module imports are blocked) and in Node (require / import default).
(function (root) {
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const ramp = (t, a, b) => clamp((t - a) / (b - a));
  const eio = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

  function spring(t, k = 170, d = 26) {            // 0 -> 1, pure function of time
    if (t <= 0) return 0;
    const w0 = Math.sqrt(k), z = d / (2 * w0);
    if (z < 1) {
      const wd = w0 * Math.sqrt(1 - z * z);
      return 1 - Math.exp(-z * w0 * t) * (Math.cos(wd * t) + (z * w0 / wd) * Math.sin(wd * t));
    }
    return 1 - Math.exp(-w0 * t) * (1 + w0 * t);
  }
  function rng(seed) {
    return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  }
  function track(t, keys, k = 170, d = 26) {       // keys: [[time, value], ...]
    let v = keys[0][1];
    for (let i = 1; i < keys.length; i++) v += (keys[i][1] - keys[i - 1][1]) * spring(t - keys[i][0], k, d);
    return v;
  }
  function indicator(t, stops, width = 120) {      // leading edge stiffer than trailing
    const lead = track(t, stops, 320, 30), trail = track(t, stops, 140, 22);
    return { left: Math.min(lead, trail), right: Math.max(lead, trail) + width };
  }
  function swapAlpha(t, tIn, tOut) {
    return Math.min(clamp((t - tIn - 0.08) / 0.12), clamp((tOut - 0.1 - t) / 0.1));
  }
  const loopT = (t, dur) => ((t % dur) + dur) % dur;
  const lerp = (a, b, x) => a + (b - a) * x;

  const M = { clamp, ramp, eio, eo, lerp, spring, rng, track, indicator, swapAlpha, loopT };
  root.Motion = M;
  if (typeof module !== 'undefined') module.exports = M;
})(typeof globalThis !== 'undefined' ? globalThis : this);
