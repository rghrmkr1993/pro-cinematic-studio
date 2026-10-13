#!/usr/bin/env python3
"""Render a first-engine timeline JSON ("clips" format; new projects use the EDL and ed_edl.py) into a video.
Frame-accurate, code-only (numpy/opencv + ffmpeg).

python3 -I ed_render.py <timeline.json> <out.mp4> [--preview] [--labels]

Timeline clip fields used here:
  n, src, src_in, t0, t1, speed
  reframe: {keys: [[t_rel, cx, cy, subj_h], ...], win_w, zoom (base zoom >= 1)}
  moves:  [{id: zoom.*, t0, t1, scale: [s0, s1], ease, blur: bool},
           {id: shake.beat, times: [...], amp, decay, rot},
           {id: fx.rgb_split, times: [...], px, frames}]
  cut_in: {id: cut | trans.flash (frames) | trans.fade (frames) | zoom.punch}
Picture: sources are decoded at most 1280 px wide for previews (area filter); the crop window is warped with bicubic
(previews) or Lanczos (final) interpolation, after an area pre-shrink when the window is shrunk below 0.6x.
Encode like ed_edl: x264 CRF 17 / preset slow (previews CRF 20 / veryfast), BT.709 matrix and tags. Progress lines
(% and ETA) on stderr every ED_PROGRESS_S seconds (default 5).
"""
import os, sys, json, math, time, argparse, subprocess, tempfile
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ed_video as V  # noqa: E402

EASE = {
    'linear': lambda u: u,
    'inQuad': lambda u: u * u, 'outQuad': lambda u: 1 - (1 - u) ** 2,
    'inOutQuad': lambda u: 2 * u * u if u < 0.5 else 1 - (-2 * u + 2) ** 2 / 2,
    'inCubic': lambda u: u ** 3, 'outCubic': lambda u: 1 - (1 - u) ** 3,
    'inOutCubic': lambda u: 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2,
    'inExpo': lambda u: 0 if u == 0 else 2 ** (10 * u - 10), 'outExpo': lambda u: 1 if u == 1 else 1 - 2 ** (-10 * u),
    'inOutExpo': lambda u: 0 if u == 0 else (1 if u == 1 else (2 ** (20 * u - 10) / 2 if u < 0.5 else (2 - 2 ** (-20 * u + 10)) / 2)),
    'hold': lambda u: 0.0 if u < 1 else 1.0,
}


def zoom_at(moves, t):
    """Product of all zoom moves at clip-relative time t (log-space interpolation with easing)."""
    z = 1.0
    for m in moves:
        if not m['id'].startswith('zoom.'):
            continue
        s0, s1 = m['scale']
        t0, t1 = m['t0'], m['t1']
        if t <= t0:
            u = 0.0
        elif t >= t1:
            u = 1.0
        else:
            u = (t - t0) / max(1e-6, t1 - t0)
        e = EASE.get(m.get('ease', 'linear'), EASE['linear'])(u)
        if m['id'] == 'zoom.in_out':      # out and back: s0 -> s1 -> s0
            e = EASE.get(m.get('ease', 'outCubic'))(min(1.0, 2 * u)) if u < 0.5 else 1 - EASE['inCubic'](2 * u - 1)
        z *= math.exp(math.log(s0) + (math.log(s1) - math.log(s0)) * e)
    return z


def shake_at(moves, t, fps, H):
    dx = dy = rot = 0.0
    for m in moves:
        if m['id'] != 'shake.beat':
            continue
        amp = m.get('amp', 0.015) * H
        dec = m.get('decay', 6) / fps
        for k, tt in enumerate(m['times']):
            if 0 <= t - tt < 6 * dec:
                a = math.exp(-(t - tt) / dec)
                ph = (t - tt) * 2 * math.pi * m.get('freq', 9.0)
                rnd = np.random.default_rng(int(tt * 1000) + k)
                sx, sy = rnd.uniform(-1, 1, 2)
                dx += amp * a * sx * math.cos(ph)
                dy += amp * a * sy * math.sin(ph * 1.3)
                rot += m.get('rot', 0.0) * a * math.sin(ph * 0.7)
    return dx, dy, rot


def rgb_at(moves, t, fps):
    px = 0.0
    for m in moves:
        if m['id'] != 'fx.rgb_split':
            continue
        for tt in m['times']:
            k = (t - tt) * fps
            if 0 <= k < m.get('frames', 3):
                px = max(px, m.get('px', 10) * (1 - k / m.get('frames', 3)))
    return px


def interp_keys(keys, t):
    ks = np.array([[k[0], k[1], k[2]] for k in keys], float)
    if len(ks) == 1:
        return float(ks[0, 1]), float(ks[0, 2])
    return float(np.interp(t, ks[:, 0], ks[:, 1])), float(np.interp(t, ks[:, 0], ks[:, 2]))


def warp(frame, cx, cy, zoom, out_w, out_h, rot=0.0, dx=0.0, dy=0.0, interp=cv2.INTER_LINEAR):
    """Crop a window of aspect out_w/out_h, full source height / zoom, centred at (cx, cy) (fractions),
    rotate by rot degrees and shift by (dx, dy) output pixels; return out_w x out_h. A window shrunk below 0.6x is
    area-filtered first (no aliasing)."""
    Hs, Ws = frame.shape[:2]
    ch = Hs / zoom
    cw = ch * out_w / out_h
    if cw > Ws:                       # source narrower than the target aspect: fit width instead
        cw = Ws / zoom
        ch = cw * out_h / out_w
    x = np.clip(cx * Ws, cw / 2, Ws - cw / 2)
    y = np.clip(cy * Hs, ch / 2, Hs - ch / 2)
    s = out_h / ch
    if s < 0.6:                       # pre-shrink by area, then warp near 1:1
        q = min(1.0, 1.5 * s)
        w2, h2 = max(2, int(round(Ws * q))), max(2, int(round(Hs * q)))
        frame = cv2.resize(frame, (w2, h2), interpolation=cv2.INTER_AREA)
        qx, qy = w2 / Ws, h2 / Hs
        x, y, s = (x + 0.5) * qx - 0.5, (y + 0.5) * qy - 0.5, s / qy
        if interp == cv2.INTER_LANCZOS4:
            interp = cv2.INTER_CUBIC
    M = cv2.getRotationMatrix2D((float(x), float(y)), rot, s)
    M[0, 2] += out_w / 2 - x + dx
    M[1, 2] += out_h / 2 - y + dy
    return cv2.warpAffine(frame, M, (out_w, out_h), flags=interp, borderMode=cv2.BORDER_REFLECT101)


def encoder_args(preview):
    """x264 settings shared with ed_edl: final CRF 17 / slow, previews CRF 20 / veryfast; BT.709 matrix and tags."""
    preset, crf, flags = ('veryfast', '20', 'bicubic') if preview else ('slow', '17', 'lanczos+accurate_rnd+full_chroma_int')
    return ['-vf', f'scale=out_color_matrix=bt709:out_range=tv:flags={flags},format=yuv420p', '-c:v', 'libx264',
            '-preset', preset, '-crf', crf, '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709',
            '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart']


def _progress(done, total, t0, last):
    """Progress line on stderr every ED_PROGRESS_S seconds -> time of the last line."""
    every = float(os.environ.get('ED_PROGRESS_S', 5.0))
    now = time.perf_counter()
    if every <= 0 or now - last < every:
        return last
    fps = done / max(now - t0, 1e-9)
    eta = (total - done) / fps if fps > 0 else 0.0
    print(f'[ed_render] {done}/{total} frames ({100.0 * done / max(1, total):.0f}%), {fps:.1f} fps, '
          f'{int(now - t0) // 60}:{int(now - t0) % 60:02d} elapsed, ETA {int(eta) // 60}:{int(eta) % 60:02d}',
          file=sys.stderr, flush=True)
    return now


def draw_label(img, n, t_abs):
    h, w = img.shape[:2]
    sc = h / 960
    cv2.rectangle(img, (0, 0), (int(150 * sc), int(52 * sc)), (0, 0, 0), -1)
    cv2.putText(img, f'#{n}', (int(10 * sc), int(40 * sc)), cv2.FONT_HERSHEY_SIMPLEX, 1.25 * sc, (255, 255, 255), max(1, int(3 * sc)), cv2.LINE_AA)
    tc = f'{int(t_abs // 60)}:{t_abs % 60:05.2f}'
    cv2.rectangle(img, (0, h - int(40 * sc)), (int(170 * sc), h), (0, 0, 0), -1)
    cv2.putText(img, tc, (int(8 * sc), h - int(12 * sc)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 * sc, (255, 255, 0), max(1, int(2 * sc)), cv2.LINE_AA)


def render_video(tl, out_path, preview=False, labels=False):
    W, H, FPS = tl['canvas']['w'], tl['canvas']['h'], tl['canvas']['fps']
    if preview:
        W, H = W // 2, H // 2
    enc = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
    enc += encoder_args(preview) + [out_path]
    p = subprocess.Popen(enc, stdin=subprocess.PIPE)
    clips = sorted(tl['clips'], key=lambda c: c['t0'])
    total = int(round(clips[-1]['t1'] * FPS))
    interp = cv2.INTER_CUBIC if preview else cv2.INTER_LANCZOS4
    written = 0
    t_start = t_last = time.perf_counter()
    for ci, c in enumerate(clips):
        f0, f1 = int(round(c['t0'] * FPS)), int(round(c['t1'] * FPS))
        if ci == len(clips) - 1:
            f1 = total
        info = V.probe(c['src'])
        sfps = info['fps'] or 30.0
        speed = c.get('speed', 1.0)
        work_w = min(info['w'], 1280 if preview else info['w'])
        span = (f1 - f0) / FPS * speed
        gen = V.frames(c['src'], t0=max(0.0, c['src_in'] - 0.04), t1=c['src_in'] + span + 0.25, fps=sfps, width=work_w)
        cur_t, cur = None, None
        nxt = next(gen, None)
        moves = c.get('moves', [])
        rf = c.get('reframe', {'keys': [[0, 0.5, 0.5, None]], 'zoom': 1.0})
        base_zoom = rf.get('zoom', 1.0)
        cut = c.get('cut_in', {'id': 'cut'})
        prev_z = None
        for k in range(f1 - f0):
            t_rel = k / FPS
            ts = c['src_in'] + t_rel * speed
            while nxt is not None and nxt[0] <= ts + 0.5 / sfps:
                cur_t, cur = nxt
                nxt = next(gen, None)
            if cur is None:
                cur_t, cur = nxt if nxt is not None else (ts, np.zeros((H, W, 3), np.uint8))
            cx, cy = interp_keys(rf['keys'], ts - c['src_in'])
            z = base_zoom * zoom_at(moves, t_rel)
            # when zoomed in, let the window move vertically towards the subject (full-height crop can't)
            sdx, sdy, srot = shake_at(moves, t_rel, FPS, H)
            if prev_z is not None and abs(math.log(z / prev_z)) > 0.035 and any(m['id'].startswith('zoom.') and m.get('blur', True) for m in moves):
                acc = np.zeros((H, W, 3), np.float32)
                K = 6
                for j in range(K):
                    zz = math.exp(math.log(prev_z) + (math.log(z) - math.log(prev_z)) * (j + 1) / K)
                    acc += warp(cur, cx, cy, zz, W, H, srot, sdx, sdy)
                out = (acc / K).astype(np.uint8)
            else:
                out = warp(cur, cx, cy, z, W, H, srot, sdx, sdy, interp)
            prev_z = z
            px = rgb_at(moves, t_rel, FPS)
            if px >= 1:
                s = int(round(px * W / 1080))
                out = out.copy()
                out[:, :, 0] = np.roll(out[:, :, 0], s, axis=1)
                out[:, :, 2] = np.roll(out[:, :, 2], -s, axis=1)
            if cut['id'] == 'trans.flash' and k < cut.get('frames', 3):
                a = [0.92, 0.55, 0.25, 0.1][min(k, 3)]
                out = (out.astype(np.float32) * (1 - a) + 255 * a).astype(np.uint8)
            if cut['id'] == 'trans.fade' and k < cut.get('frames', 8):
                a = 1 - k / cut.get('frames', 8)
                out = (out.astype(np.float32) * (1 - a)).astype(np.uint8)
            if labels:
                out = np.ascontiguousarray(out)
                draw_label(out, c['n'], (f0 + k) / FPS)
            p.stdin.write(np.ascontiguousarray(out).tobytes())
            written += 1
            t_last = _progress(written, total, t_start, t_last)
        gen.close()
    p.stdin.close()
    p.wait()
    return written


def render_audio(tl, out_wav):
    """Track segment with fades, two-pass loudness normalisation to the target (default -14 LUFS, TP -1 dBTP)."""
    a = tl['audio']
    dur = a['dur']
    fi, fo = a.get('fade_in', 0.0), a.get('fade_out', 0.25)
    target = a.get('loudnorm', -14)
    pre = []
    if fi > 0:
        pre.append(f'afade=t=in:st=0:d={fi}')
    if fo > 0:
        pre.append(f'afade=t=out:st={max(0.0, dur - fo):.3f}:d={fo}')
    src = ['-ss', f"{a['start']:.4f}", '-t', f'{dur:.4f}', '-i', a['src']]
    first = ','.join(pre + [f'loudnorm=I={target}:TP=-1.0:LRA=11:print_format=json'])
    r = subprocess.run(['ffmpeg', '-v', 'info', '-nostats', '-y'] + src + ['-af', first, '-f', 'null', '-'], capture_output=True, text=True)
    txt = r.stderr
    j = json.loads(txt[txt.rindex('{'):txt.rindex('}') + 1])
    gain = target - float(j['input_i'])
    # static gain + peak limiter, iterated until the integrated loudness lands within 0.5 LU of the target
    for _ in range(4):
        second = ','.join(pre + [f'volume={gain:.2f}dB', 'alimiter=limit=0.84:attack=3:release=60:level=false'])
        subprocess.run(['ffmpeg', '-v', 'error', '-y'] + src + ['-af', second, '-ar', '48000', '-ac', '2', out_wav], check=True)
        r = subprocess.run(['ffmpeg', '-v', 'info', '-nostats', '-i', out_wav, '-af', 'ebur128', '-f', 'null', '-'],
                           capture_output=True, text=True)
        import re
        got = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)
        if not got:
            break
        miss = target - float(got[-1])
        if abs(miss) <= 0.5:
            break
        gain += miss


def render(tl, out_path, preview=False, labels=False):
    tmp = tempfile.mkdtemp(prefix='edr_')
    vid = os.path.join(tmp, 'v.mp4')
    n = render_video(tl, vid, preview, labels)
    if tl.get('audio'):
        wav = os.path.join(tmp, 'a.wav')
        render_audio(tl, wav)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                        '-shortest', '-movflags', '+faststart', out_path], check=True)
    else:
        os.replace(vid, out_path)
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    return n


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('timeline')
    ap.add_argument('out')
    ap.add_argument('--preview', action='store_true')
    ap.add_argument('--labels', action='store_true')
    a = ap.parse_args()
    tl = json.load(open(a.timeline))
    n = render(tl, a.out, a.preview, a.labels)
    print('frames', n)
