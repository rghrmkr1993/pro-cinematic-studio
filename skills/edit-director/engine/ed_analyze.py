#!/usr/bin/env python3
"""Analyse a reference edit (-> template of shots/cuts/moves on the beat grid) and source footage
(-> shots with per-moment features for shot selection).

CLI:
  python3 -I ed_analyze.py reference <ref.mp4> <out_dir> [--track track.json]
  python3 -I ed_analyze.py source <src.mp4> <out_dir> [--fps 8]
"""
import os, sys, json, math, argparse
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ed_video as V          # noqa: E402
import ed_audio as A          # noqa: E402
import ed_motion as M         # noqa: E402  global motion estimator


def _motion_events(frames_rgb, fps, label):
    """Run the motion analyser (ed_motion) on a list of RGB frames (one shot)."""
    if len(frames_rgb) < 3:
        return dict(events=[], shake={}, flashes=[], holds=[], cuts=[])
    meta = dict(slug='shot', sec=label, key=0, n=len(frames_rgb), src=[frames_rgb[0].shape[1], frames_rgb[0].shape[0]],
                durs=[1000.0 / fps] * len(frames_rgb))
    summary, pairs, curves = M.analyse(meta, {i: f for i, f in enumerate(frames_rgb)})
    keep = ('events', 'shake', 'flashes', 'black', 'white', 'strobe', 'holds', 'bars', 'luma_med', 'sat_med', 'rgb_med')
    out = {k: summary[k] for k in keep if k in summary}
    out['motion_energy'] = round(float(np.mean([p['diff'] for p in pairs])) if pairs else 0.0, 2)
    out['zoom_curve'] = [round(float(z), 3) for z in curves['Z']]
    return out


def _scale_class(face_h_frac):
    if face_h_frac is None:
        return 'wide/no-face'
    if face_h_frac > 0.33:
        return 'extreme-close'
    if face_h_frac > 0.18:
        return 'close'
    if face_h_frac > 0.08:
        return 'medium'
    return 'wide'


def _shot_faces(frames_rgb):
    mid = frames_rgb[len(frames_rgb) // 2]
    big = cv2.resize(mid, (640, int(640 * mid.shape[0] / mid.shape[1])), interpolation=cv2.INTER_LINEAR)
    fs = V.faces(big)
    if not fs:
        return None
    f = fs[0]
    H, W = big.shape[:2]
    return dict(n=len(fs), cx=round((f['x'] + f['w'] / 2) / W, 3), cy=round((f['y'] + f['h'] / 2) / H, 3),
                h=round(f['h'] / H, 3))


def _transition_at(feats, cut, fps, flashes, black):
    """Classify how shot boundary `cut` is made: flash / dip-to-black / blur (whip, zoom-through) / hard cut."""
    win = range(max(0, cut - 3), min(len(feats), cut + 3))
    if any(i in flashes for i in win):
        return 'flash'
    if any(i in black for i in win):
        return 'dip_black'
    sh = np.array([f['sharp'] for f in feats])
    a, b = max(0, cut - 6), min(len(feats), cut + 6)
    base = np.median(sh[max(0, cut - 20):min(len(sh), cut + 20)]) + 1e-6
    if sh[max(0, cut - 2):min(len(sh), cut + 2)].min() < 0.25 * base:
        return 'blur'
    return 'cut'


def analyze_reference(path, out_dir, track_json=None, width=320):
    os.makedirs(out_dir, exist_ok=True)
    info = V.probe(path)
    fps = min(info['fps'] or 30.0, 60.0)
    feats, rgb = [], []
    for t, fr in V.frames(path, fps=fps, width=width):
        feats.append(V.frame_feats(fr))
        rgb.append(fr)
    n = len(rgb)
    cut_info = V.detect_cuts(feats, fps)
    cuts = cut_info['cuts']
    bounds = [0] + cuts + [n]
    # music of the reference itself
    aud = A.analyze(path) if info.get('has_audio') else None
    beats = np.array(aud['beats']) if aud else np.array([])
    downs = np.array(aud['downbeats']) if aud else np.array([])
    period = 60.0 / aud['bpm'] if aud else None
    shots = []
    for k in range(len(bounds) - 1):
        a, b = bounds[k], bounds[k + 1]
        if b - a < 1:
            continue
        t0, t1 = a / fps, b / fps
        fr = rgb[a:b]
        mot = _motion_events(fr, fps, f'shot{k + 1}')
        face = _shot_faces(fr)
        s = dict(i=k + 1, f0=a, f1=b, t0=round(t0, 3), t1=round(t1, 3), dur=round(t1 - t0, 3),
                 scale=_scale_class(face['h'] if face else None), face=face, motion=mot,
                 sharp=round(float(np.median([f['sharp'] for f in feats[a:b]])), 1),
                 luma=round(float(np.mean([f['luma'] for f in feats[a:b]])), 1),
                 sat=round(float(np.mean([f['sat'] for f in feats[a:b]])), 1))
        if k > 0:
            s['cut_in'] = dict(type=_transition_at(feats, a, fps, cut_info['flashes'], cut_info['black']))
            # punch-in/out across the cut: next shot is a rescaled continuation of the previous one
            est = M.estimate_pair(cv2.cvtColor(rgb[a - 1], cv2.COLOR_RGB2GRAY), cv2.cvtColor(rgb[a], cv2.COLOR_RGB2GRAY),
                                  np.full(rgb[a].shape[:2], 255, np.uint8))
            if est['M'] is not None and est['method'] == 'lk' and est['n'] >= 25 and est['inl'] >= 0.45:
                sc, rot = M.similarity_from_affine(est['M'])
                if abs(sc - 1) > 0.07:
                    s['cut_in']['type'] = 'punch_in' if sc > 1 else 'punch_out'
                    s['cut_in']['scale'] = round(sc, 3)
        if aud and len(beats):
            j = int(np.argmin(np.abs(beats - t0)))
            off = t0 - beats[j]
            frac = (t0 - beats[j]) / period
            s['beat'] = dict(idx=j, offset_ms=round(off * 1000), downbeat=bool(np.min(np.abs(downs - beats[j])) < 0.02) if len(downs) else False,
                             sub=('on' if abs(frac) < 0.12 else ('half' if abs(abs(frac) - 0.5) < 0.12 else 'off')),
                             len_beats=round((t1 - t0) / period, 2))
        shots.append(s)
    # summary
    durs = np.array([s['dur'] for s in shots])
    on = [s for s in shots[1:] if s.get('beat')]
    summary = dict(n_shots=len(shots), mean_dur=round(float(durs.mean()), 3), median_dur=round(float(np.median(durs)), 3),
                   min_dur=round(float(durs.min()), 3), max_dur=round(float(durs.max()), 3),
                   on_beat_share=round(sum(1 for s in on if s['beat']['sub'] == 'on') / max(1, len(on)), 2),
                   half_beat_share=round(sum(1 for s in on if s['beat']['sub'] == 'half') / max(1, len(on)), 2),
                   transitions={t: sum(1 for s in shots if s.get('cut_in', {}).get('type') == t)
                                for t in ('cut', 'flash', 'dip_black', 'blur', 'punch_in', 'punch_out')},
                   scales={c: sum(1 for s in shots if s['scale'] == c) for c in ('extreme-close', 'close', 'medium', 'wide', 'wide/no-face')})
    tpl = dict(kind='reference', path=path, info=info, fps=fps, n_frames=n, audio=aud, shots=shots, summary=summary,
               flashes=cut_info['flashes'], black=cut_info['black'], white=cut_info['white'])
    json.dump(tpl, open(os.path.join(out_dir, 'reference.json'), 'w'))
    contact_sheet(rgb, shots, os.path.join(out_dir, 'reference_shots.jpg'), fps)
    return tpl


def contact_sheet(rgb, shots, out, fps, cols=8, tile_w=200):
    tiles = []
    for s in shots:
        fr = rgb[(s['f0'] + s['f1']) // 2]
        th = int(tile_w * fr.shape[0] / fr.shape[1])
        t = cv2.resize(fr, (tile_w, th), interpolation=cv2.INTER_AREA).copy()
        lab = f"#{s['i']} {s['dur']:.2f}s"
        if s.get('cut_in'):
            lab += ' ' + s['cut_in']['type'][:5]
        cv2.rectangle(t, (0, 0), (tile_w, 16), (0, 0, 0), -1)
        cv2.putText(t, lab, (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)
        tiles.append(t)
    if not tiles:
        return
    th = max(t.shape[0] for t in tiles)
    rows = math.ceil(len(tiles) / cols)
    sheet = np.zeros((rows * th, cols * tile_w, 3), np.uint8)
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        sheet[r * th:r * th + t.shape[0], c * tile_w:(c + 1) * tile_w] = t
    cv2.imwrite(out, cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])


def analyze_source(path, out_dir, fps=8.0, width=320):
    """Shots + per-sample features of long source footage (sampled at `fps`)."""
    os.makedirs(out_dir, exist_ok=True)
    info = V.probe(path)
    feats, times, small = [], [], []
    face_rows, person_rows = [], []
    prev_g = None
    cam = []
    for k, (t, fr) in enumerate(V.frames(path, fps=fps, width=width)):
        f = V.frame_feats(fr)
        feats.append(f)
        times.append(t)
        g = f['g']
        # camera motion between consecutive samples
        if prev_g is not None:
            est = M.estimate_pair(prev_g, g, np.full(g.shape, 255, np.uint8))
            if est['M'] is not None:
                sc, rot = M.similarity_from_affine(est['M'])
                cam.append((float(sc), float(rot), float(est['M'][0, 2]) / width, float(est['M'][1, 2]) / g.shape[0], est['n'], est['inl']))
            else:
                cam.append((1.0, 0.0, 0.0, 0.0, 0, 0.0))
        else:
            cam.append((1.0, 0.0, 0.0, 0.0, 0, 0.0))
        # faces every sample (YuNet is fast at 640px), person mask every ~1 s
        big = cv2.resize(fr, (640, int(640 * fr.shape[0] / fr.shape[1])), interpolation=cv2.INTER_LINEAR)
        fs = V.faces(big)
        H, W = big.shape[:2]
        face_rows.append([(round((x['x'] + x['w'] / 2) / W, 3), round((x['y'] + x['h'] / 2) / H, 3), round(x['h'] / H, 3), round(x['score'], 2)) for x in fs[:3]])
        if k % max(1, int(round(fps))) == 0:
            pm = V.person_mask(fr)
            cov = float((pm > 0.5).mean())
            if cov > 0.01:
                ys, xs = np.nonzero(pm > 0.5)
                person_rows.append((round(t, 3), round(cov, 3), round(float(xs.mean() / fr.shape[1]), 3), round(float(ys.min() / fr.shape[0]), 3)))
            else:
                person_rows.append((round(t, 3), 0.0, None, None))
        small.append(cv2.resize(fr, (160, int(160 * fr.shape[0] / fr.shape[1])), interpolation=cv2.INTER_AREA))
        prev_g = g
    n = len(feats)
    cut_info = V.detect_cuts(feats, fps, min_shot=0.5)
    bounds = [0] + cut_info['cuts'] + [n]
    pdiff = np.array(cut_info['pix_d'])
    shots = []
    for k in range(len(bounds) - 1):
        a, b = bounds[k], bounds[k + 1]
        if b - a < 2:
            continue
        sh = np.array([f['sharp'] for f in feats[a:b]])
        nfaces = [len(face_rows[i]) for i in range(a, b)]
        fh = [face_rows[i][0][2] for i in range(a, b) if face_rows[i]]
        shots.append(dict(i=len(shots) + 1, f0=a, f1=b, t0=round(times[a], 3), t1=round(times[b - 1] + 1 / fps, 3),
                          dur=round((b - a) / fps, 3), motion=round(float(pdiff[a + 1:b].mean()) if b - a > 1 else 0.0, 2),
                          sharp=round(float(np.median(sh)), 1), luma=round(float(np.mean([f['luma'] for f in feats[a:b]])), 1),
                          face_share=round(float(np.mean([x > 0 for x in nfaces])), 2),
                          face_h=round(float(np.median(fh)), 3) if fh else None,
                          scale=_scale_class(float(np.median(fh)) if fh else None)))
    series = dict(t=[round(x, 3) for x in times], motion=pdiff.round(2).tolist(),
                  sharp=[round(f['sharp'], 1) for f in feats], luma=[round(f['luma'], 1) for f in feats],
                  cam=[[round(c[0], 4), round(c[1], 3), round(c[2], 4), round(c[3], 4), c[4], round(c[5], 2)] for c in cam],
                  faces=face_rows, person=person_rows)
    src = dict(kind='source', path=path, info=info, fps=fps, n=n, shots=shots, series=series, cuts=cut_info['cuts'])
    json.dump(src, open(os.path.join(out_dir, 'source.json'), 'w'))
    # contact sheet: middle frame of each shot
    fake = [dict(i=s['i'], f0=s['f0'], f1=s['f1'], dur=s['dur']) for s in shots]
    contact_sheet(small, fake, os.path.join(out_dir, 'source_shots.jpg'), fps, cols=10, tile_w=160)
    return src


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    r = sub.add_parser('reference')
    r.add_argument('src')
    r.add_argument('out')
    s = sub.add_parser('source')
    s.add_argument('src')
    s.add_argument('out')
    s.add_argument('--fps', type=float, default=8.0)
    a = ap.parse_args()
    if a.cmd == 'reference':
        tpl = analyze_reference(a.src, a.out)
        print(json.dumps(tpl['summary'], ensure_ascii=False))
        if tpl['audio']:
            print('bpm', tpl['audio']['bpm'], 'steady', tpl['audio'].get('steady'), 'drops', [d['t'] for d in tpl['audio']['drops']])
    elif a.cmd == 'source':
        src = analyze_source(a.src, a.out, fps=a.fps)
        print('shots', len(src['shots']), 'duration', src['info']['duration'])


if __name__ == '__main__':
    main()
