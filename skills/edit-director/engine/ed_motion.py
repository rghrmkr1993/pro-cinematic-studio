#!/usr/bin/env python3
"""Global camera/image motion inside one shot (used by ed_analyze, ed_plan, ed_remake).

Per frame pair it estimates a similarity transform prev->next (scale, rotation, translation about the frame
centre) from tracked features (LK + forward/backward check + RANSAC), falling back to ECC. `analyse()` also
measures luma, saturation, sharpness, black bars, frame difference and hard cuts, then detects events: zoom in/out
runs (with easing and zoom centre), rotation runs, pans/tilts, shake, flashes, black frames, holds/freezes, strobe.

API:
  estimate_pair(gray_a, gray_b, mask) -> dict(s, rot, M, method, n, inl, resid, nonrigid)   (a -> b)
  similarity_from_affine(M) -> (scale, rotation_deg)
  ease_label(curve) -> (label, half_at)          curve: normalised progress samples 0..1
  analyse(meta, frames) -> (summary, pairs, curves)
      meta: {"n": total frames, "src": [w, h], "durs": [ms per frame], "id": "label"(opt)}
      frames: {frame_index: RGB uint8 image}
  fmt(summary) -> human-readable text
"""
import math
import numpy as np
import cv2

LK = dict(winSize=(21, 21), maxLevel=3,
          criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))


def frame_stats(img):
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    rows_dark = (g.max(axis=1) < 24)
    cols_dark = (g.max(axis=0) < 24)

    def run(a):
        k = 0
        for v in a:
            if v:
                k += 1
            else:
                break
        return k
    h, w = g.shape
    bars = dict(top=run(rows_dark) / h, bottom=run(rows_dark[::-1]) / h,
                left=run(cols_dark) / w, right=run(cols_dark[::-1]) / w)
    sharp = float(cv2.Laplacian(g, cv2.CV_64F).var())
    return dict(luma=float(g.mean()), luma_sd=float(g.std()), sat=float(hsv[..., 1].mean()),
                sharp=sharp, bars=bars,
                rgb=[float(img[..., k].mean()) for k in range(3)])


def hist_dist(a, b):
    ha = cv2.calcHist([cv2.cvtColor(a, cv2.COLOR_RGB2HSV)], [0, 1, 2], None, [12, 4, 4], [0, 180, 0, 256, 0, 256])
    hb = cv2.calcHist([cv2.cvtColor(b, cv2.COLOR_RGB2HSV)], [0, 1, 2], None, [12, 4, 4], [0, 180, 0, 256, 0, 256])
    cv2.normalize(ha, ha)
    cv2.normalize(hb, hb)
    return float(cv2.compareHist(ha, hb, cv2.HISTCMP_BHATTACHARYYA))


def similarity_from_affine(M):
    A = M[:, :2]
    s = math.sqrt(abs(np.linalg.det(A)))
    rot = math.degrees(math.atan2(A[1, 0] - A[0, 1], A[0, 0] + A[1, 1]))
    return s, rot


def estimate_pair(ga, gb, mask):
    """Return dict(s, rot, M, method, n, inl, resid, nonrigid) mapping a->b."""
    pts = cv2.goodFeaturesToTrack(ga, maxCorners=600, qualityLevel=0.004, minDistance=4,
                                  blockSize=5, mask=mask)
    res = dict(method='none', n=0, inl=0.0, resid=None, nonrigid=None, M=None)
    if pts is not None and len(pts) >= 12:
        p1, st1, _ = cv2.calcOpticalFlowPyrLK(ga, gb, pts, None, **LK)
        p0r, st2, _ = cv2.calcOpticalFlowPyrLK(gb, ga, p1, None, **LK)
        fb = np.linalg.norm((pts - p0r).reshape(-1, 2), axis=1)
        good = (st1.reshape(-1) == 1) & (st2.reshape(-1) == 1) & (fb < 1.0)
        a = pts.reshape(-1, 2)[good]
        b = p1.reshape(-1, 2)[good]
        res['n'] = int(good.sum())
        if len(a) >= 10:
            M, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=1.2,
                                                 maxIters=3000, confidence=0.995, refineIters=20)
            if M is not None:
                inl = inl.reshape(-1).astype(bool)
                pred = (a @ M[:, :2].T) + M[:, 2]
                err = np.linalg.norm(pred - b, axis=1)
                flow = np.linalg.norm(b - a, axis=1)
                res.update(M=M, method='lk', inl=float(inl.mean()),
                           resid=float(np.median(err[inl])) if inl.any() else None,
                           nonrigid=float(np.median(err) / (np.median(flow) + 0.5)))
                if inl.sum() >= 10 and inl.mean() >= 0.3:
                    return res
    # ECC fallback
    try:
        warp = np.eye(2, 3, dtype=np.float32)
        crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 80, 1e-5)
        _, warp = cv2.findTransformECC(ga.astype(np.float32), gb.astype(np.float32), warp,
                                       cv2.MOTION_AFFINE, crit, mask, 5)
        res.update(M=warp.astype(np.float64), method='ecc')
    except cv2.error:
        if res['M'] is None:
            res['method'] = 'fail'
    return res


def runs(mask, gap=1, barrier=None):
    """Return list of (start, end) inclusive runs of True, bridging gaps <= gap (never across barrier idx)."""
    if barrier:
        out, start = [], 0
        for b in sorted(barrier) + [len(mask)]:
            for a, c in runs(mask[start:b], gap):
                out.append((a + start, c + start))
            start = b + 1
        return out
    out, i, n = [], 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while True:
                k = j + 1
                while k < n and not mask[k] and k - j - 1 < gap:
                    k += 1
                if k < n and mask[k] and k - j - 1 <= gap:
                    j = k
                else:
                    break
            out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out


def ease_label(curve):
    """curve: normalised progress samples 0..1 at 0..100% of the run."""
    c = np.asarray(curve)
    t = np.linspace(0, 1, len(c))
    half = float(np.interp(0.5, c, t)) if c[-1] > c[0] else 0.5
    q1 = float(np.interp(0.25, t, c))
    q3 = float(np.interp(0.75, t, c))
    if half < 0.38:
        lab = 'ease-out (fast start, settles)'
    elif half > 0.62:
        lab = 'ease-in (slow start, accelerates)'
    elif q1 < 0.18 and q3 > 0.82:
        lab = 'ease-in-out (S-curve)'
    else:
        lab = 'near-linear'
    return lab, half


def _label(meta):
    if meta.get('id'):
        return str(meta['id'])
    parts = [str(meta[k]) for k in ('slug', 'sec') if meta.get(k) not in (None, '')]
    key = meta.get('key', meta.get('i'))
    return ('#'.join(parts) or 'clip') + (f'/{key}' if key is not None else '')


def analyse(meta, frames):
    idxs = sorted(frames)
    tw = min(frames[i].shape[1] for i in idxs)
    th = min(frames[i].shape[0] for i in idxs)
    imgs = [cv2.resize(frames[i], (tw, th), interpolation=cv2.INTER_AREA)
            if frames[i].shape[1] != tw else frames[i] for i in idxs]
    grays = [cv2.cvtColor(im, cv2.COLOR_RGB2GRAY) for im in imgs]
    durs = meta.get('durs') or []
    acc = 0
    allt = []
    for d in durs:
        allt.append(acc)
        acc += d
    total_ms = acc
    t_ms = [allt[i] if i < len(allt) else None for i in idxs]
    n = len(imgs)
    stats = [frame_stats(im) for im in imgs]
    # static-overlay mask (pixels that never change while the rest moves)
    stack = np.stack(grays).astype(np.float32)
    tsd = stack.std(axis=0)
    mask = np.full(grays[0].shape, 255, np.uint8)
    static = tsd < 1.5
    if 0.0 < static.mean() < 0.55:
        mask[static] = 0
    hh, ww = grays[0].shape
    y0, y1 = int(max(s['bars']['top'] for s in stats) * hh), int(hh - max(s['bars']['bottom'] for s in stats) * hh)
    x0, x1 = int(max(s['bars']['left'] for s in stats) * ww), int(ww - max(s['bars']['right'] for s in stats) * ww)
    if y1 - y0 > hh * 0.3 and x1 - x0 > ww * 0.3:
        mask[:y0, :] = 0
        mask[y1:, :] = 0
        mask[:, :x0] = 0
        mask[:, x1:] = 0
    cx, cy = (ww - 1) / 2.0, (hh - 1) / 2.0
    pairs = []
    for k in range(n - 1):
        a, bimg = imgs[k], imgs[k + 1]
        diff = float(np.abs(grays[k].astype(np.int16) - grays[k + 1].astype(np.int16)).mean())
        hd = hist_dist(a, bimg)
        est = estimate_pair(grays[k], grays[k + 1], mask)
        rec = dict(a=idxs[k], b=idxs[k + 1], gap=idxs[k + 1] - idxs[k], diff=diff, hist=hd,
                   method=est['method'], n=est['n'], inl=est['inl'], resid=est['resid'],
                   nonrigid=est['nonrigid'])
        cut = (hd > 0.5 and diff > 18) or (est['method'] in ('fail',) and diff > 25) or \
              (est['method'] == 'ecc' and hd > 0.4 and diff > 22)
        if est['M'] is not None and not cut:
            M = est['M']
            s, rot = similarity_from_affine(M)
            A = M[:, :2]
            c = np.array([cx, cy])
            tc = M[:, 2] + A @ c - c  # translation of the frame centre
            rec.update(s=s, rot=rot, tx=float(tc[0] / ww * 100), ty=float(tc[1] / hh * 100))
            if abs(s - 1) > 0.03:
                try:
                    fp = np.linalg.solve(np.eye(2) - A, M[:, 2])
                    rec['zc'] = [float(fp[0] / ww), float(fp[1] / hh)]
                except np.linalg.LinAlgError:
                    pass
        else:
            rec.update(s=1.0, rot=0.0, tx=0.0, ty=0.0)
        rec['cut'] = bool(cut)
        pairs.append(rec)
    # second pass: cuts that keep the palette (same location, new angle) show as a collapse of
    # trackable points together with an unusually large frame difference
    if pairs:
        med_n = float(np.median([p['n'] for p in pairs])) or 1.0
        med_d = float(np.median([p['diff'] for p in pairs])) or 1.0
        for p in pairs:
            if not p['cut'] and p['n'] < 0.3 * med_n and p['diff'] > max(15.0, 1.8 * med_d):
                p['cut'] = True
                p.update(s=1.0, rot=0.0, tx=0.0, ty=0.0)
                p.pop('zc', None)
    # cumulative within segments
    Z, R, X, Y = [1.0], [0.0], [0.0], [0.0]
    for p in pairs:
        if p['cut']:
            Z.append(1.0); R.append(0.0); X.append(0.0); Y.append(0.0)
        else:
            Z.append(Z[-1] * p['s']); R.append(R[-1] + p['rot'])
            X.append(X[-1] + p['tx']); Y.append(Y[-1] + p['ty'])
    events = []
    zoom_spans = []
    cut_pairs = [k for k, p in enumerate(pairs) if p['cut']]
    gaps = np.array([max(1, p['gap']) for p in pairs], dtype=float)
    ls = np.array([math.log(p['s']) if not p['cut'] else 0.0 for p in pairs])
    lr = ls / gaps  # per-source-frame log zoom rate
    for sign, name in ((1, 'ZOOM-IN (image magnifies)'), (-1, 'ZOOM-OUT (image shrinks)')):
        for s0, s1 in runs(list(sign * lr > 0.004), gap=1, barrier=cut_pairs):
            seg = ls[s0:s1 + 1]
            tot = math.exp(seg.sum())
            if sign * math.log(tot) < 0.03:
                continue
            cum = np.concatenate([[0], np.cumsum(seg)])
            curve = cum / cum[-1] if cum[-1] != 0 else cum
            lab, half = ease_label(curve)
            rseg = lr[s0:s1 + 1]
            pk = int(np.argmax(sign * rseg)) + s0
            zcs = [pairs[k]['zc'] for k in range(s0, s1 + 1) if 'zc' in pairs[k]]
            zcs = [z for z in zcs if -0.5 < z[0] < 1.5 and -0.5 < z[1] < 1.5]
            zc = [round(float(np.median([z[0] for z in zcs])), 2), round(float(np.median([z[1] for z in zcs])), 2)] if zcs else None
            zpath = [[round(z[0], 2), round(z[1], 2)] for z in (zcs[0], zcs[-1])] if len(zcs) >= 2 else None
            zoom_spans.append((s0, s1))
            nr = [pairs[k]['nonrigid'] for k in range(s0, s1 + 1) if pairs[k]['nonrigid'] is not None]
            sh = [stats[k + 1]['sharp'] for k in range(s0, s1 + 1)]
            base_sh = float(np.median([s['sharp'] for s in stats])) or 1.0
            fa, fb_ = idxs[s0], idxs[s1 + 1]
            dur = (allt[fb_] - allt[fa]) if fb_ < len(allt) else None
            events.append(dict(type=name, frames=[fa, fb_], nfr=fb_ - fa, ms=dur, factor=round(tot, 3),
                               peak_rate=round(math.exp(float(rseg.max() if sign > 0 else rseg.min())), 3),
                               peak_at=idxs[pk + 1], ease=lab, half_at=round(half, 2),
                               curve=[round(float(v), 2) for v in np.interp(np.linspace(0, 1, 6), np.linspace(0, 1, len(curve)), curve)],
                               center=zc, center_path=zpath, nonrigid=round(float(np.median(nr)), 3) if nr else None,
                               sharp_ratio=round(float(np.min(sh)) / base_sh, 2),
                               conf='low (local motion/parallax dominates)' if (nr and float(np.median(nr)) > 0.35) else 'ok'))
    rot = np.array([p['rot'] if not p['cut'] else 0.0 for p in pairs])
    rotr = rot / gaps
    for sign, name in ((1, 'ROTATE (clockwise on screen)'), (-1, 'ROTATE (counter-clockwise on screen)')):
        for s0, s1 in runs(list(sign * rotr > 0.3), gap=1, barrier=cut_pairs):
            tot = float(rot[s0:s1 + 1].sum())
            if abs(tot) < 2.0:
                continue
            fa, fb_ = idxs[s0], idxs[s1 + 1]
            events.append(dict(type=name, frames=[fa, fb_], nfr=fb_ - fa,
                               ms=(allt[fb_] - allt[fa]) if fb_ < len(allt) else None,
                               degrees=round(tot, 1), peak_deg_per_fr=round(float(np.abs(rotr[s0:s1 + 1]).max()), 2)))
    for axis, key, pos, neg in (('x', 'tx', 'content moves RIGHT (camera pans left)', 'content moves LEFT (camera pans right)'),
                                ('y', 'ty', 'content moves DOWN (camera tilts up)', 'content moves UP (camera tilts down)')):
        v = np.array([p[key] if not p['cut'] else 0.0 for p in pairs])
        vr = v / gaps
        for sign, name in ((1, pos), (-1, neg)):
            for s0, s1 in runs(list(sign * vr > 0.4), gap=1, barrier=cut_pairs):
                tot = float(v[s0:s1 + 1].sum())
                if abs(tot) < 4:
                    continue
                # a shift that happens inside a zoom run is mostly the zoom centre being off-centre
                inside = sum(1 for k in range(s0, s1 + 1) if any(a <= k <= b for a, b in zoom_spans))
                fa, fb_ = idxs[s0], idxs[s1 + 1]
                events.append(dict(type='SHIFT ' + name + (' [during zoom: off-centre zoom/reframe]' if inside > (s1 - s0 + 1) / 2 else ''),
                                   frames=[fa, fb_], nfr=fb_ - fa,
                                   ms=(allt[fb_] - allt[fa]) if fb_ < len(allt) else None,
                                   pct=round(tot, 1), peak_pct_per_fr=round(float(np.abs(vr[s0:s1 + 1]).max()), 1)))
    # shake: high-pass jitter of translation outside zoom runs (camera shake / handheld / beat shake)
    tx = np.array([p['tx'] if not p['cut'] else 0.0 for p in pairs])
    ty = np.array([p['ty'] if not p['cut'] else 0.0 for p in pairs])
    keep = np.array([not any(a <= k <= b for a, b in zoom_spans) for k in range(len(pairs))])
    if len(tx) >= 3:
        hp = np.abs(tx[1:-1] - (tx[:-2] + tx[2:]) / 2) + np.abs(ty[1:-1] - (ty[:-2] + ty[2:]) / 2)
        hp = hp[keep[1:-1]] if keep[1:-1].any() else hp
        flips = int(np.sum((np.sign(tx[1:]) != np.sign(tx[:-1])) & (np.abs(tx[1:]) > 0.8) & (np.abs(tx[:-1]) > 0.8)))
        shake = dict(jitter_pct=round(float(np.median(hp)), 2), p90_pct=round(float(np.percentile(hp, 90)), 2), x_dir_flips=flips)
    else:
        shake = dict(jitter_pct=0.0, p90_pct=0.0, x_dir_flips=0)
    # flashes (local luma spikes vs neighbours) / black / strobe
    L = np.array([s['luma'] for s in stats])
    med = float(np.median(L))
    flash = []
    for k in range(n):
        left = [L[j] for j in range(max(0, k - 5), k - 1)]
        right = [L[j] for j in range(k + 2, min(n, k + 6))]
        sides = [float(np.median(x)) for x in (left, right) if x]
        if sides and all(L[k] - b > 30 and L[k] > 1.25 * b for b in sides):
            flash.append(idxs[k])
    black = [idxs[k] for k in range(n) if L[k] < 12]
    whiteish = [idxs[k] for k in range(n) if L[k] > 225]
    dL = np.diff(L)
    strobe = int(np.sum((np.abs(dL[:-1]) > 35) & (np.abs(dL[1:]) > 35) & (np.sign(dL[:-1]) != np.sign(dL[1:])))) if n > 3 else 0
    holds = [(idxs[a], idxs[b + 1]) for a, b in runs([p['diff'] < 0.6 and not p['cut'] for p in pairs], gap=0) if b - a + 1 >= 2]
    cuts = [p['b'] for p in pairs if p['cut']]
    bars = {k: round(float(np.median([s['bars'][k] for s in stats])), 3) for k in ('top', 'bottom', 'left', 'right')}
    rgb = np.array([s['rgb'] for s in stats])
    fps = (len(durs) * 1000.0 / total_ms) if total_ms else None
    summary = dict(id=_label(meta), n=meta.get('n', n), analysed=n, src=meta.get('src', [tw, th]),
                   tile=[tw, th], fps=round(fps, 2) if fps else None, ms=total_ms, cuts=cuts,
                   events=events, shake=shake, flashes=flash, black=black, white=whiteish, strobe=strobe,
                   holds=holds, bars=bars, luma_med=round(med, 1),
                   sat_med=round(float(np.median([s['sat'] for s in stats])), 1),
                   rgb_med=[round(float(v), 1) for v in np.median(rgb, axis=0)],
                   method_counts={m: sum(1 for p in pairs if p['method'] == m) for m in ('lk', 'ecc', 'fail', 'none')},
                   overlay_masked=round(float((mask == 0).mean()), 2))
    curves = dict(frames=idxs, t_ms=t_ms, Z=Z, R=R, X=X, Y=Y, luma=L.tolist(),
                  sharp=[s['sharp'] for s in stats], diff=[0.0] + [p['diff'] for p in pairs])
    return summary, pairs, curves


def fmt(summary):
    s = summary
    out = [f"{s['id']}: {s['n']} fr ({s['analysed']} analysed) @ {s['fps']} fps = {(s['ms'] or 0)/1000:.2f}s, src {s['src'][0]}x{s['src'][1]}, "
           f"cuts at {s['cuts'] or 'none'}, methods {s['method_counts']}, overlay-mask {s['overlay_masked']}"]
    for e in s['events']:
        t = e['type']
        dur = f"{e['nfr']} fr" + (f"/{e['ms']}ms" if e.get('ms') is not None else '')
        if t.startswith('ZOOM'):
            out.append(f"  {t}: x{e['factor']} over fr {e['frames'][0]}->{e['frames'][1]} ({dur}); peak x{e['peak_rate']}/fr at fr {e['peak_at']}; "
                       f"{e['ease']} (50% at {e['half_at']}); curve {e['curve']}; centre {e['center']} path {e['center_path']}; "
                       f"nonrigid {e['nonrigid']}; min sharpness x{e['sharp_ratio']}; conf {e['conf']}")
        elif t.startswith('ROTATE'):
            out.append(f"  {t}: {e['degrees']} deg over fr {e['frames'][0]}->{e['frames'][1]} ({dur}); peak {e['peak_deg_per_fr']} deg/fr")
        else:
            out.append(f"  {t}: {e['pct']}% of frame over fr {e['frames'][0]}->{e['frames'][1]} ({dur}); peak {e['peak_pct_per_fr']}%/fr")
    if not s['events']:
        out.append('  no significant global zoom/rotation/shift (static camera or local motion only)')
    extra = []
    if s['flashes']: extra.append(f"flash frames {s['flashes']}")
    if s['black']: extra.append(f"black frames {s['black']}")
    if s['white']: extra.append(f"white frames {s['white']}")
    if s['strobe']: extra.append(f"strobe flips {s['strobe']}")
    if s['holds']: extra.append(f"holds {s['holds']}")
    if any(v > 0.04 for v in s['bars'].values()): extra.append(f"bars {s['bars']}")
    extra.append(f"shake {s['shake']}")
    extra.append(f"luma {s['luma_med']} sat {s['sat_med']} rgb {s['rgb_med']}")
    out.append('  ' + '; '.join(extra))
    return '\n'.join(out)
