#!/usr/bin/env python3
"""Music analysis for the edit engine (no librosa): tempo, beats, downbeats, energy, sections, drops,
and alignment of two recordings (reference edit audio vs. the user's track, incl. sped-up/slowed versions).

CLI:
  python3 -I ed_audio.py analyze <audio_or_video> <out.json> [--plot out.png] [--bpm-hint 140]
  python3 -I ed_audio.py align <a> <b>          # where does recording a sit inside b (offset, stretch)
"""
import sys, json, math, argparse, subprocess
import numpy as np
from scipy import signal as ss
from scipy.ndimage import gaussian_filter1d, median_filter

SR = 22050
HOP = 256                      # 11.6 ms per frame
FPS_A = SR / HOP
ONSET_LAG = 0.010   # seconds added to detected beats (calibrated in tests)


def load_audio(path, sr=SR, start=None, dur=None):
    cmd = ['ffmpeg', '-v', 'error', '-nostdin']
    if start:
        cmd += ['-ss', f'{start:.3f}']
    cmd += ['-i', path]
    if dur:
        cmd += ['-t', f'{dur:.3f}']
    cmd += ['-vn', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def mel_filterbank(n_fft, sr, n_mels=64, fmin=30.0, fmax=8000.0):
    def hz2mel(f):
        return 2595.0 * np.log10(1.0 + f / 700.0)

    def mel2hz(m):
        return 700.0 * (10 ** (m / 2595.0) - 1.0)
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    pts = mel2hz(np.linspace(hz2mel(fmin), hz2mel(fmax), n_mels + 2))
    fb = np.zeros((n_mels, len(freqs)), np.float32)
    for i in range(n_mels):
        lo, c, hi = pts[i], pts[i + 1], pts[i + 2]
        up = (freqs - lo) / max(c - lo, 1e-9)
        dn = (hi - freqs) / max(hi - c, 1e-9)
        fb[i] = np.maximum(0, np.minimum(up, dn))
    return fb, freqs


def spectrogram(y, n_fft=1024, hop=HOP):
    pad = n_fft // 2
    yp = np.pad(y, pad, mode='reflect')
    frames = np.lib.stride_tricks.sliding_window_view(yp, n_fft)[::hop]
    win = np.hanning(n_fft).astype(np.float32)
    S = np.empty((frames.shape[0], n_fft // 2 + 1), np.float32)
    for i in range(0, frames.shape[0], 512):           # chunked to bound memory
        S[i:i + 512] = np.abs(np.fft.rfft(frames[i:i + 512] * win, axis=1))
    return S


def features(y):
    S = spectrogram(y)
    fb, freqs = mel_filterbank(1024, SR)
    M = S @ fb.T                                          # (frames, mels)
    logM = np.log1p(100.0 * M)
    flux = np.maximum(0.0, np.diff(logM, axis=0, prepend=logM[:1]))
    onset = flux.mean(axis=1)
    onset = onset - gaussian_filter1d(onset, 16)          # remove slow trend
    onset = np.maximum(onset, 0)
    onset /= (onset.max() + 1e-9)
    low = (freqs >= 30) & (freqs <= 150)
    low_e = S[:, low].sum(axis=1)
    low_flux = np.maximum(0.0, np.diff(np.log1p(low_e), prepend=np.log1p(low_e[:1])))
    mid = (freqs >= 1500) & (freqs <= 6000)
    mid_e = S[:, mid].sum(axis=1)
    mid_flux = np.maximum(0.0, np.diff(np.log1p(mid_e), prepend=np.log1p(mid_e[:1])))
    rms = np.sqrt(np.mean(np.lib.stride_tricks.sliding_window_view(np.pad(y, 512), 1024)[::HOP] ** 2, axis=1))[:len(onset)]
    cent = (S * freqs[None, :]).sum(axis=1) / (S.sum(axis=1) + 1e-9)
    hb = (freqs >= 80) & (freqs <= 4000)
    pc = np.round(12 * np.log2(np.maximum(freqs[hb], 1e-6) / 440.0)).astype(int) % 12
    chroma = np.zeros((S.shape[0], 12), np.float32)
    for k in range(12):
        chroma[:, k] = S[:, hb][:, pc == k].sum(axis=1)
    chroma /= (chroma.sum(axis=1, keepdims=True) + 1e-9)
    return dict(onset=onset.astype(np.float32), low_flux=low_flux.astype(np.float32), mid_flux=mid_flux.astype(np.float32), rms=rms.astype(np.float32),
                low_e=low_e.astype(np.float32), centroid=cent.astype(np.float32), logM=logM, chroma=chroma)


def estimate_tempo(onset, bpm_min=60, bpm_max=200, prior_bpm=120.0, hint=None):
    n = len(onset)
    max_lag = int(FPS_A * 60 / bpm_min) + 2
    x = onset[:int(FPS_A * 90)].astype(np.float64)
    x = x - x.mean()
    nfft = 1 << (2 * len(x) - 1).bit_length()
    X = np.fft.rfft(x, nfft)
    ac = np.fft.irfft(np.abs(X) ** 2)[:max_lag + 1]
    lags = np.arange(len(ac))
    with np.errstate(divide='ignore'):
        bpm = 60.0 * FPS_A / np.maximum(lags, 1e-9)
    valid = (bpm >= bpm_min) & (bpm <= bpm_max)
    centre = hint or prior_bpm
    prior = np.exp(-0.5 * (np.log2(np.maximum(bpm, 1e-9) / centre) / (0.6 if hint else 1.0)) ** 2)
    score = np.where(valid, np.maximum(ac, 0) * prior, 0)
    # harmonic enhancement: add half/double lag evidence
    enh = score.copy()
    for k in (2, 3):
        idx = (lags * k).clip(0, len(ac) - 1)
        enh += 0.5 * np.where(valid, np.maximum(ac[idx], 0) * prior, 0)
    best = int(np.argmax(enh))
    # parabolic refinement
    if 1 <= best < len(enh) - 1:
        a, b, c = enh[best - 1], enh[best], enh[best + 1]
        off = 0.5 * (a - c) / (a - 2 * b + c + 1e-12)
    else:
        off = 0.0
    lag = best + off
    tempo = 60.0 * FPS_A / lag
    srt = np.sort(enh[valid])[::-1]
    conf = float(srt[0] / (srt[min(5, len(srt) - 1)] + 1e-9)) if len(srt) > 1 else 1.0
    return float(tempo), conf


def track_beats(onset, tempo, tightness=120.0):
    period = 60.0 * FPS_A / tempo
    local = gaussian_filter1d(onset, max(1.0, period / 32.0))
    n = len(local)
    window = np.arange(-int(round(2 * period)), -int(round(period / 2)) + 1)
    txwt = -tightness * (np.log(-window / period)) ** 2
    cum = np.zeros(n)
    back = np.full(n, -1, int)
    for i in range(n):
        z = i + window
        ok = z >= 0
        if ok.any():
            cand = txwt[ok] + cum[z[ok]]
            j = int(np.argmax(cand))
            cum[i] = local[i] + cand[j]
            back[i] = z[ok][j]
        else:
            cum[i] = local[i]
    # last beat: max cumulative score within the final period, among frames with real onset energy
    tail = np.arange(max(0, n - int(period * 1.5)), n)
    last = int(tail[np.argmax(cum[tail])])
    beats = [last]
    while back[beats[-1]] >= 0:
        beats.append(int(back[beats[-1]]))
    beats = np.array(beats[::-1])
    # trim weak leading/trailing beats (silence)
    strength = local[beats]
    thr = 0.1 * np.median(strength[strength > 0]) if (strength > 0).any() else 0
    keep = np.where(strength > thr)[0]
    if len(keep):
        beats = beats[keep[0]:keep[-1] + 1]
    return beats


def refine_beats(beats, onset, tempo):
    """Sub-frame refinement of tracked beats + steady-grid fit. If the music has a steady tempo (median residual
    < 20 ms) the fitted grid replaces the tracked beats (more precise for electronic/pop); otherwise tracked beats stay."""
    period = 60.0 * FPS_A / tempo
    sm = gaussian_filter1d(onset, 1.0)
    r = max(2, int(period * 0.12))
    ref = []
    for b in beats:
        a, c = max(1, b - r), min(len(sm) - 2, b + r)
        j = a + int(np.argmax(sm[a:c + 1]))
        y0, y1, y2 = sm[j - 1], sm[j], sm[j + 1]
        off = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-12)
        ref.append((j + float(np.clip(off, -0.5, 0.5))) / FPS_A)
    ref = np.array(ref)
    k = np.arange(len(ref))
    if len(ref) < 8:
        return ref, tempo, ref, 1.0
    # robust linear fit (two passes, drop outliers)
    A = np.polyfit(k, ref, 1)
    res = ref - np.polyval(A, k)
    keep = np.abs(res) < max(0.03, 2.5 * np.median(np.abs(res)))
    A = np.polyfit(k[keep], ref[keep], 1)
    grid = np.polyval(A, k)
    resid = float(np.median(np.abs(ref - grid)))
    bpm = 60.0 / A[0]
    if resid < 0.02:
        return grid, bpm, grid, resid
    return ref, 60.0 / float(np.median(np.diff(ref))), grid, resid


def downbeat_phase(beats, onset, low_flux, logM=None, rms=None, meter=4, mid_flux=None):
    """Vote over 4 phases using: low-band accents (kick/bass), harmonic/spectral change at the beat (chords change
    on downbeats), and energy jumps (sections and drops start on downbeats)."""
    lf = gaussian_filter1d(low_flux, 2)
    on = gaussian_filter1d(onset, 2)
    acc = np.array([0.6 * lf[b] / (lf.max() + 1e-9) + 0.4 * on[b] for b in beats])
    votes = np.zeros(meter)
    kick = np.array([lf[b] for b in beats]) / (lf.max() + 1e-9)
    sn = gaussian_filter1d(mid_flux, 2) if mid_flux is not None else on
    snare = np.array([sn[b] for b in beats]) / (sn.max() + 1e-9)
    for p in range(meter):
        k1 = kick[p::meter].mean() if len(kick[p::meter]) else 0
        k3 = kick[(p + 2) % meter::meter].mean() if len(kick[(p + 2) % meter::meter]) else 0
        s2 = snare[(p + 1) % meter::meter].mean() if len(snare[(p + 1) % meter::meter]) else 0
        s4 = snare[(p + 3) % meter::meter].mean() if len(snare[(p + 3) % meter::meter]) else 0
        s1 = snare[p::meter].mean() if len(snare[p::meter]) else 0
        s3 = snare[(p + 2) % meter::meter].mean() if len(snare[(p + 2) % meter::meter]) else 0
        votes[p] += 0.5 * (k1 + 0.5 * k3) + 0.5 * (s2 + s4 - s1 - s3)
    if logM is not None and len(beats) > 8:
        w = max(4, int(np.median(np.diff(beats)) / 2))
        chg = []
        for b in beats:
            a0, a1, b1 = max(0, b - w), b, min(len(logM), b + w)
            chg.append(float(np.abs(logM[a1:b1].mean(0) - logM[a0:a1].mean(0)).sum()) if a1 > a0 and b1 > a1 else 0.0)
        chg = np.array(chg)
        chg = (chg - chg.mean()) / (chg.std() + 1e-9)
        for p in range(meter):
            votes[p] += 0.15 * max(0.0, chg[p::meter].mean())
    if rms is not None and len(beats) > 16:
        e = 20 * np.log10(gaussian_filter1d(rms, 8) + 1e-6)
        eb = e[beats]
        jumps = np.diff(eb, prepend=eb[0])
        big = np.where(jumps > max(3.0, np.percentile(jumps, 97)))[0]
        for i in big:
            votes[i % meter] += 0.5
    phase = int(np.argmax(votes))
    srt = sorted(votes, reverse=True)
    conf = float(srt[0] / (srt[1] + 1e-9))
    return phase, conf, acc


def _unused_downbeat_phase(beats, onset, low_flux, meter=4):
    acc = []
    lf = gaussian_filter1d(low_flux, 2)
    on = gaussian_filter1d(onset, 2)
    for b in beats:
        acc.append(0.6 * lf[b] / (lf.max() + 1e-9) + 0.4 * on[b])
    acc = np.array(acc)
    scores = [acc[p::meter].mean() if len(acc[p::meter]) else 0 for p in range(meter)]
    phase = int(np.argmax(scores))
    srt = sorted(scores, reverse=True)
    conf = float(srt[0] / (srt[1] + 1e-9))
    return phase, conf, acc


def bar_features(beats_t, downbeats_t, feats, duration):
    rms = feats['rms']
    low = feats['low_e']
    on = feats['onset']
    cent = feats['centroid']
    bars = []
    edges = list(downbeats_t) + [duration]
    for i in range(len(edges) - 1):
        a, b = int(edges[i] * FPS_A), int(edges[i + 1] * FPS_A)
        if b <= a:
            continue
        r = float(np.sqrt(np.mean(rms[a:b] ** 2)) + 1e-9)
        bars.append(dict(i=i, t0=round(edges[i], 3), t1=round(edges[i + 1], 3), rms_db=round(20 * math.log10(r), 2),
                         low_db=round(10 * math.log10(float(low[a:b].mean()) + 1e-9), 2),
                         onset=round(float(on[a:b].mean()), 4), centroid=round(float(cent[a:b].mean()), 1)))
    return bars


def sections_and_drops(bars):
    if len(bars) < 4:
        return [], []
    E = np.array([b['rms_db'] for b in bars])
    L = np.array([b['low_db'] for b in bars])
    O = np.array([b['onset'] for b in bars])
    z = lambda v: (v - v.mean()) / (v.std() + 1e-9)
    F = np.stack([z(E), z(L), z(O)], axis=1)
    # novelty: distance between mean feature of previous k bars and next k bars
    k = 4 if len(bars) >= 12 else 2
    nov = np.zeros(len(bars))
    for i in range(k, len(bars) - k + 1):
        nov[i] = np.linalg.norm(F[i:i + k].mean(0) - F[i - k:i].mean(0))
    peaks, _ = ss.find_peaks(nov, distance=k, height=np.percentile(nov, 70) if len(nov) > 5 else None)
    bounds = [0] + [int(p) for p in peaks] + [len(bars)]
    secs = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        if b - a < 1:
            continue
        secs.append(dict(bar0=a, bar1=b, t0=bars[a]['t0'], t1=bars[b - 1]['t1'], rms_db=round(float(E[a:b].mean()), 2),
                         low_db=round(float(L[a:b].mean()), 2)))
    if secs:
        lo, hi = min(s['rms_db'] for s in secs), max(s['rms_db'] for s in secs)
        for s in secs:
            r = (s['rms_db'] - lo) / (hi - lo + 1e-9)
            s['energy'] = round(r, 2)
            s['label'] = 'high' if r > 0.66 else ('mid' if r > 0.33 else 'low')
    drops = []
    for i in range(2, len(bars)):
        prev = E[max(0, i - 4):i].mean()
        prevL = L[max(0, i - 4):i].mean()
        jump, jumpL = E[i] - prev, L[i] - prevL
        if jump > 3.0 and jumpL > 3.0 and E[i] >= np.percentile(E, 60):
            if not drops or bars[i]['t0'] - drops[-1]['t'] > 8:
                drops.append(dict(t=bars[i]['t0'], bar=i, jump_db=round(float(jump), 2), low_jump_db=round(float(jumpL), 2)))
    return secs, drops


def analyze(path, bpm_hint=None):
    y = load_audio(path)
    duration = len(y) / SR
    f = features(y)
    tempo, tconf = estimate_tempo(f['onset'], hint=bpm_hint)
    beats = track_beats(f['onset'], tempo)
    beat_t, tempo, grid_t, grid_resid = refine_beats(beats, f['onset'], tempo)
    beat_t = beat_t + ONSET_LAG
    beats = np.clip(np.round(beat_t * FPS_A).astype(int), 0, len(f['onset']) - 1)
    phase, dconf, acc = downbeat_phase(beats, f['onset'], f['low_flux'], f['chroma'], f['rms'], mid_flux=f['mid_flux'])
    down_t = beat_t[phase::4]
    bars = bar_features(beat_t, down_t, f, duration)
    secs, drops = sections_and_drops(bars)
    env_t = np.arange(len(f['onset'])) * HOP / SR
    rms_db = 20 * np.log10(gaussian_filter1d(f['rms'], 4) + 1e-6)
    return dict(path=path, duration=round(duration, 3), bpm=round(float(tempo), 2), tempo_conf=round(tconf, 2),
                steady=bool(grid_resid < 0.02), grid_resid_ms=round(grid_resid * 1000, 1),
                beats=[round(float(t), 4) for t in beat_t], beat_strength=[round(float(a), 3) for a in acc],
                downbeat_phase=phase, downbeat_conf=round(dconf, 2), downbeats=[round(float(t), 4) for t in down_t],
                bars=bars, sections=secs, drops=drops,
                envelope=dict(fps=round(FPS_A, 4), onset=[round(float(v), 3) for v in f['onset'][::2]],
                              rms_db=[round(float(v), 1) for v in rms_db[::2]], step=2))


def onset_env(path, start=None, dur=None):
    y = load_audio(path, start=start, dur=dur)
    return features(y)['onset']


def align(a_path, b_path, stretches=(0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35)):
    """Find where recording `a` (e.g. audio of a reference edit) sits inside `b` (full track).
    Returns offset (seconds in b where a starts) for the best time-stretch factor (a plays `stretch`× faster than b)."""
    ea, eb = onset_env(a_path), onset_env(b_path)
    best = None
    for s in stretches:
        # a sped up by s means a's timeline is compressed: resample a to b's tempo by factor s
        n = int(len(ea) * s)
        if n < 32:
            continue
        ra = np.interp(np.linspace(0, len(ea) - 1, n), np.arange(len(ea)), ea)
        ra = (ra - ra.mean()) / (ra.std() + 1e-9)
        bb = (eb - eb.mean()) / (eb.std() + 1e-9)
        if len(bb) < len(ra):
            c = ss.correlate(ra, bb, mode='full', method='fft')
            lag = int(np.argmax(c)) - (len(bb) - 1)
            off = -lag
        else:
            c = ss.correlate(bb, ra, mode='valid', method='fft')
            off = int(np.argmax(c))
        c = c / (min(len(ra), len(bb)))
        pk = float(c.max())
        srt = np.sort(c)[::-1]
        second = float(srt[int(FPS_A * 2)]) if len(srt) > FPS_A * 2 else 0.0
        cand = dict(stretch=s, offset_s=round(off * HOP / SR, 3), peak=round(pk, 4), ratio=round(pk / (abs(second) + 1e-9), 2))
        if best is None or cand['peak'] > best['peak']:
            best = cand
    best['same_music'] = bool(best['peak'] > 0.35 and best['ratio'] > 1.6)
    return best


def plot(res, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    env = res['envelope']
    t = np.arange(len(env['onset'])) * env['step'] / env['fps']
    fig, ax = plt.subplots(2, 1, figsize=(14, 5), sharex=True)
    ax[0].plot(t, env['onset'], lw=0.6, color='#555')
    for b in res['beats']:
        ax[0].axvline(b, color='#3b82f6', lw=0.4, alpha=0.6)
    for d in res['downbeats']:
        ax[0].axvline(d, color='#ef4444', lw=0.8)
    ax[0].set_title(f"{res['bpm']} BPM (conf {res['tempo_conf']}), downbeat phase {res['downbeat_phase']} (conf {res['downbeat_conf']})", fontsize=9)
    ax[1].plot(t, env['rms_db'], lw=0.8, color='#111')
    for s in res['sections']:
        ax[1].axvspan(s['t0'], s['t1'], alpha=0.15 + 0.35 * s['energy'], color='#f59e0b')
    for d in res['drops']:
        ax[1].axvline(d['t'], color='#dc2626', lw=2)
    ax[1].set_xlabel('s')
    fig.tight_layout()
    fig.savefig(out, dpi=90)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    a = sub.add_parser('analyze')
    a.add_argument('src')
    a.add_argument('out')
    a.add_argument('--plot')
    a.add_argument('--bpm-hint', type=float)
    b = sub.add_parser('align')
    b.add_argument('a')
    b.add_argument('b')
    args = ap.parse_args()
    if args.cmd == 'analyze':
        res = analyze(args.src, args.bpm_hint)
        json.dump(res, open(args.out, 'w'))
        if args.plot:
            plot(res, args.plot)
        print(json.dumps({k: res[k] for k in ('duration', 'bpm', 'tempo_conf', 'downbeat_phase', 'downbeat_conf')}),
              f"beats={len(res['beats'])} bars={len(res['bars'])} sections={[(s['t0'], s['label']) for s in res['sections']]} drops={[d['t'] for d in res['drops']]}")
    elif args.cmd == 'align':
        print(json.dumps(align(args.a, args.b)))


if __name__ == '__main__':
    main()
