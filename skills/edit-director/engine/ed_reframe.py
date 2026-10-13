#!/usr/bin/env python3
"""Reframing for vertical (or any aspect) crops: subject paths, active speaker, talk-clip speaker crops.

crop_path(src, t_in, dur) -> dict(keys=[[t_rel, cx, cy, subj_h], ...], subject='face'|'person'|'motion'|'center')
    cx, cy are fractions of the source frame; subj_h - subject height as a fraction of frame height (face or person).
    Priority: largest face (YuNet) that the frame edge does not cut -> person mask (PP-HumanSeg; a person whose
    head the left / right edge cuts is left out) -> motion/edge saliency -> centre. Smoothing: gap fill, median + gaussian, dead-zone (static crop when the subject barely
    moves), velocity limit.

scan(path, t0, t1, box=None, sample_fps=10) -> dict (cached in ~/.cache/edit-studio/reframe)
    One decode pass of [t0, t1] inside the content box: camera cuts (10 fps candidates refined to the exact source
    frame), YuNet faces with landmarks every 1/sample_fps s, face tracks, and per face sample the mouth
    articulation (motion of the mouth region against the previous sample, best of +-4 px shifts, minus the motion
    of the eye region = head motion).

active_speaker(path, t0, t1, box=None, words=None, sample_fps=10) ->
    {"cuts": [t...], "shots": [{"i", "t0", "t1", "tracks": [{"id", "ids", "presence", "face": [x0,y0,x1,y1], "talk"}],
                                "turns": [[t0, t1, track_id], ...], "utterances": [[t0, t1, track_id, {id: score}]]}]}
    Per shot: the only face, or (two or more faces) the face whose mouth articulation is highest (>= 1.15 x the
    next) during each utterance (word groups split at pauses >= 0.3 s; without words, voice-band sound stretches
    cut into <= 1.5 s windows); undecided utterances keep the previous speaker. Turns switch in the pause before
    the new speaker (<= 0.25 s lead); turns < 1 s are merged. A person re-detected after a gap (tracks that never
    co-occur, same place and size) is one track: "ids" lists the merged scan track ids.

speaker_crop(path, t0, t1, box=None, avoid=None, canvas=(1080, 1920), fps=30, words=None) ->
    [{"t0", "t1", "crop": {"cx", "cy", "z", ("path": [[k, cx, cy, z], ...])}, "shot", "speaker", "face", "subject"}]
    Segments split at camera cuts and speaker turns. crop is the EDL crop of a source with that `box` (box=None:
    the full frame, i.e. a source without "box"): cx, cy = window centre as fractions of the box, z = 1 -> the
    window spans the full box height; path keys k are output frames (fps) from the segment's t0.
    z is the smallest zoom for which, at every sample, the window (a) contains the head (face box widened for
    hair/chin, clipped to the box) with the eyes near 38 % of its height, (b) misses every `avoid` box
    (static_overlays dicts or [x0,y0,x1,y1], source px, + 1.2 % margin) and (c) stays inside the box; at least
    face_min=0.16 of the window height is face (wide shots get closer). Resolution limit max_upscale=2 (box px ->
    canvas px); when the overlays cannot be avoided within it, z may grow to 3x upscale, then the lowest-priority
    avoid boxes ('ui', then 'text', then 'logo') are released and listed in "released" - the face is never cut.
    The path is static when one position fits the whole segment, else a smoothed follow inside the feasible
    corridor. subject: 'face' | 'person' (person-mask fallback) | 'center'.
    sub_crop(item, a, b, fps) re-bases an item's crop for a sub-range [a, b]; crop_pieces(items, a, b, fps) -> the
    items cut to a kept source range (one EDL segment each), e.g. the talk pieces left after removing a sentence.
CLI: python3 -I ed_reframe.py speaker MEDIA T0 T1 [--box x0,y0,x1,y1] [--avoid auto|none] [--words words.json]
     python3 -I ed_reframe.py path MEDIA T_IN DUR      (crop_path, legacy)
"""
import os, sys, json, hashlib
import numpy as np
import cv2
from scipy.ndimage import median_filter, gaussian_filter1d

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ed_video as V  # noqa: E402

VERSION = 4
CACHE = os.path.join(os.environ.get('EDIT_STUDIO_CACHE', os.path.join(os.environ.get('ED_ROOT', 'C:/Claude Code/cinema-studio/edit'), 'cache')), 'reframe')


def _face_cut(f, W, H, m=0.01):
    """True when a face box touches or leaves the frame (left / right / bottom edge, or the top with the eyes in
    the top 4 %): a head cut off by the frame edge."""
    x0, y0, x1, y1 = f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']
    if x0 <= m * W or x1 >= (1 - m) * W or y1 >= (1 - m) * H:
        return True
    eyes = [p[1] for p in (f.get('lm') or [])[:2]]
    return y0 <= m * H and bool(eyes) and min(eyes) <= 0.04 * H


def _whole_person(m, W, H, edge=0.01):
    """person mask -> (ys, xs) of the people whose head the left / right frame edge does not cut (head = top 30 %
    of each blob), None when no such person covers >= 2 % of the frame."""
    if m.mean() <= 0.02:
        return None
    num, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    keep = np.zeros(num, bool)
    for c in range(1, num):
        x, y, w, h = st[c, :4]
        if st[c, 4] < 0.002 * W * H:
            continue
        hy = y + max(1, int(0.3 * h))
        cols = np.nonzero((lab[y:hy, x:x + w] == c).any(axis=0))[0] + x
        keep[c] = cols.size > 0 and cols.min() > edge * W and cols.max() < (1 - edge) * W
    sel = keep[lab] & m
    if sel.mean() <= 0.02:
        return None
    return np.nonzero(sel)


def crop_path(src, t_in, dur, sample_fps=6.0, width=640, out_aspect=9 / 16, deadzone=0.05):
    info = V.probe(src)
    src_aspect = info['w'] / info['h']
    win_w = min(1.0, out_aspect / src_aspect)        # crop width as a fraction of source width (full height)
    pts = []
    prev = None
    kinds = []
    for t, fr in V.frames(src, t0=t_in, t1=t_in + max(dur, 1.0 / sample_fps), fps=sample_fps, width=width):
        g = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY)
        H, W = g.shape
        fs = [f for f in V.faces(fr) if not _face_cut(f, W, H)]    # a head cut by the frame edge is no subject
        if fs:
            f = fs[0]
            cx = (f['x'] + f['w'] / 2) / W
            cy = (f['y'] + f['h'] / 2) / H
            pts.append((t - t_in, cx, cy, f['h'] / H))
            kinds.append('face')
        else:
            pm = V.person_mask(fr)
            pp = _whole_person(pm > 0.5, W, H)
            if pp is not None:
                ys, xs = pp
                top = np.percentile(ys, 5)
                cx = float(np.median(xs)) / W
                cy = float(top + 0.15 * (np.percentile(ys, 95) - top)) / H     # head/upper-body region
                pts.append((t - t_in, cx, cy, float(np.percentile(ys, 95) - top) / H))
                kinds.append('person')
            else:
                sx, sy = V.saliency_center(prev, g)
                pts.append((t - t_in, sx, sy, None))
                kinds.append('motion')
        prev = g
    if not pts:
        return dict(keys=[[0.0, 0.5, 0.5, None]], subject='center', win_w=win_w)
    arr = np.array([[p[0], p[1], p[2]] for p in pts], float)
    subject = max(('face', 'person', 'motion'), key=kinds.count)  # fixed tie order (deterministic)
    # prefer subject samples of the dominant kind; others are treated as gaps
    good = np.array([k == subject for k in kinds])
    if subject == 'motion' and not good.all():
        good[:] = True
    t = arr[:, 0]
    cx = np.interp(t, t[good], arr[good, 1]) if good.any() else np.full(len(t), 0.5)
    cy = np.interp(t, t[good], arr[good, 2]) if good.any() else np.full(len(t), 0.5)
    if len(cx) >= 5:
        cx = median_filter(cx, size=5, mode='nearest')
        cy = median_filter(cy, size=5, mode='nearest')
    if len(cx) >= 3:
        cx = gaussian_filter1d(cx, 1.2, mode='nearest')
        cy = gaussian_filter1d(cy, 1.2, mode='nearest')
    # dead-zone: if the subject stays within ±deadzone of its median, lock the crop (operator-like, no jitter)
    if np.ptp(cx) < 2 * deadzone or dur < 1.5:
        cx[:] = np.median(cx)
    if np.ptp(cy) < 2 * deadzone or dur < 1.5:
        cy[:] = np.median(cy)
    # velocity limit: at most 35 % of the crop width per second
    vmax = 0.35 * win_w / sample_fps
    for i in range(1, len(cx)):
        cx[i] = cx[i - 1] + np.clip(cx[i] - cx[i - 1], -vmax, vmax)
    sh = [p[3] for p in pts if p[3] is not None]
    keys = [[round(float(a), 3), round(float(b), 4), round(float(c), 4), round(float(np.median(sh)), 3) if sh else None]
            for a, b, c in zip(t, cx, cy)]
    return dict(keys=keys, subject=subject, win_w=round(win_w, 4))


# ============================================================================ scan: cuts, faces, mouths
def _patch(gray, x0, y0, x1, y1, size):
    """region resized to `size` (w, h) with a 15 % margin each side (for the shift search); None off-frame."""
    H, W = gray.shape
    mx, my = 0.15 * (x1 - x0), 0.15 * (y1 - y0)
    a, b = int(round(x0 - mx)), int(round(y0 - my))
    c, d = int(round(x1 + mx)), int(round(y1 + my))
    if c - a < 6 or d - b < 4 or a < 0 or b < 0 or c > W or d > H:
        return None
    pw, ph = int(round(size[0] * 1.3)), int(round(size[1] * 1.3))
    p = cv2.resize(gray[b:d, a:c], (pw, ph), interpolation=cv2.INTER_AREA).astype(np.float32)
    return p * (128.0 / max(8.0, float(p.mean())))


def _motion(p, q, size, r=4):
    """min over shifts (+-r px) of the mean abs difference of the centre `size` window of p vs q."""
    if p is None or q is None:
        return None
    w, h = size
    oy, ox = (p.shape[0] - h) // 2, (p.shape[1] - w) // 2
    c = p[oy:oy + h, ox:ox + w]
    best = 1e9
    for dy in range(-min(r, oy), min(r, oy) + 1):
        for dx in range(-min(r, ox), min(r, ox) + 1):
            d = float(np.abs(c - q[oy + dy:oy + dy + h, ox + dx:ox + dx + w]).mean())
            best = min(best, d)
    return best


MOUTH, EYES = (40, 24), (40, 20)


def _face_regions(f):
    """mouth and eye regions (analysis px) of a face dict with x, y, w, h."""
    x, y, w, h = f['x'], f['y'], f['w'], f['h']
    return (x + 0.18 * w, y + 0.60 * h, x + 0.82 * w, y + 0.98 * h), (x + 0.10 * w, y + 0.18 * h, x + 0.90 * w,
                                                                       y + 0.48 * h)


def _iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / u if u > 0 else 0.0


def _cache_key(path, *parts):
    st = os.stat(path)
    raw = json.dumps([os.path.abspath(path), st.st_size, int(st.st_mtime), VERSION] + list(parts), default=str)
    return hashlib.sha1(raw.encode()).hexdigest()[:20]


def _refine_cut(path, ta, tb, box, info):
    """exact first frame of the new shot between samples ta (old shot) and tb (new shot), at the source rate."""
    rate = info['fps'] or 30.0
    feats, times = [], []
    # sample labels of V.frames(fps < source rate) run up to half a sample early: search a wider window
    a = max(0.0, ta - 0.05)
    first = np.ceil(a * rate - 1e-4) / rate                  # exact time of the first decoded source frame
    for k, (_, fr) in enumerate(V.frames(path, a, tb + 0.1, fps=rate, width=256, crop=box, info=info)):
        feats.append(V.frame_feats(fr))
        times.append(float(first + k / rate))
    if len(feats) < 2:
        return tb, 0.0
    sc = [V.bhatt(feats[i - 1]['hist'], feats[i]['hist']) +
          float(np.abs(feats[i]['g'].astype(np.int16) - feats[i - 1]['g'].astype(np.int16)).mean()) / 40.0
          for i in range(1, len(feats))]
    k = int(np.argmax(sc))
    return times[k + 1], float(sc[k])


def scan(path, t0, t1, box=None, sample_fps=10.0, width=1920, cache=True, log=None):
    """Decode [t0, t1] once (see module doc). Returns {"t0", "t1", "box", "fps", "sample_fps", "cuts", "samples":
    [{"t", "faces": [{"box": [x0,y0,x1,y1] source px, "eyes_y", "score", "track", "mouth", "eyes"}]}]}."""
    info = V.probe(path)
    W, H = info['w'], info['h']
    box = [int(v) for v in (box or [0, 0, W, H])]
    key = _cache_key(path, round(t0, 3), round(t1, 3), box, sample_fps, width)
    cp = os.path.join(CACHE, f'scan_{key}.json')
    if cache and os.path.exists(cp):
        try:
            with open(cp) as fh:
                return json.load(fh)
        except (OSError, ValueError):
            pass
    bw, bh = box[2] - box[0], box[3] - box[1]
    aw, ah = V._even_size(bw, bh, width)
    s = bw / aw                                             # source px per analysis px
    dw, dh = V._even_size(aw, ah, 960)
    ds = aw / dw
    samples, feats = [], []
    tracks = {}                                             # id -> (last box analysis px, mouth patch, eye patch)
    next_id = 0
    for t, fr in V.frames(path, t0, t1, fps=sample_fps, width=aw, height=ah, crop=box, info=info):
        gray = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY)
        small = cv2.resize(fr, (dw, dh), interpolation=cv2.INTER_AREA)
        f = V.frame_feats(small)
        f['g'] = cv2.resize(f['g'], (96, 54), interpolation=cv2.INTER_AREA)
        if feats and V.bhatt(feats[-1]['hist'], f['hist']) > 0.35:
            tracks = {}                                     # a hard cut: faces of the new shot get new tracks
        feats.append(f)
        found = []
        for fc in V.faces(small):
            if fc['score'] < 0.75 or fc['h'] * ds < 0.03 * ah:
                continue
            fa = dict(x=fc['x'] * ds, y=fc['y'] * ds, w=fc['w'] * ds, h=fc['h'] * ds)
            bxa = (fa['x'], fa['y'], fa['x'] + fa['w'], fa['y'] + fa['h'])
            mreg, ereg = _face_regions(fa)
            mp, ep = _patch(gray, *mreg, MOUTH), _patch(gray, *ereg, EYES)
            best, bid = 0.3, None
            for tid, (tb, _, _, _) in tracks.items():
                if tid in [x['track'] for x in found]:
                    continue
                o = _iou(bxa, tb)
                if o > best:
                    best, bid = o, tid
            mouth = eyes = None
            if bid is None:
                bid = next_id
                next_id += 1
            else:
                _, pm, pe, _ = tracks[bid]
                mouth, eyes = _motion(mp, pm, MOUTH), _motion(ep, pe, EYES)
            tracks[bid] = (bxa, mp, ep, t)
            eyes_y = (fc['lm'][0][1] + fc['lm'][1][1]) / 2 * ds
            found.append(dict(box=[round(box[0] + bxa[0] * s, 1), round(box[1] + bxa[1] * s, 1),
                                   round(box[0] + bxa[2] * s, 1), round(box[1] + bxa[3] * s, 1)],
                              eyes_y=round(box[1] + eyes_y * s, 1), score=round(fc['score'], 3), track=bid,
                              mouth=None if mouth is None else round(mouth, 3),
                              eyes=None if eyes is None else round(eyes, 3)))
        for tid in [k for k, v in tracks.items() if t - v[3] > 1.0]:   # a track survives 1 s without detections
            del tracks[tid]
        samples.append(dict(t=round(t, 3), faces=found))
    cuts = []
    if len(feats) >= 3:
        res = V.detect_cuts(feats, sample_fps, min_shot=0.12)
        for i in res['cuts']:
            if 0 < i < len(samples):
                tc, _ = _refine_cut(path, samples[i - 1]['t'], samples[i]['t'], box, info)
                cuts.append(round(tc, 3))
    out = dict(version=VERSION, t0=t0, t1=t1, box=box, fps=info['fps'], sample_fps=sample_fps, cuts=sorted(cuts),
               samples=samples, size=[W, H])
    if cache:
        try:
            os.makedirs(CACHE, exist_ok=True)
            with open(cp, 'w') as fh:
                json.dump(out, fh)
        except OSError:
            pass
    return out


# ============================================================================ active speaker
def _utterances(words, t0, t1, gap=0.3):
    ws = sorted((w for w in (words or []) if w.get('t0') is not None and w['t1'] > t0 and w['t0'] < t1),
                key=lambda w: w['t0'])
    out = []
    for w in ws:
        if out and w['t0'] - out[-1][1] < gap:
            out[-1][1] = max(out[-1][1], w['t1'])
        else:
            out.append([w['t0'], w['t1']])
    return out


def _audio_utterances(path, t0, t1):
    try:
        import ed_voice
        audio = ed_voice.load_audio(path, t0=t0, dur=t1 - t0)
        env = ed_voice._voice_env(audio, hop=0.01)
    except Exception:                                       # no audio stream / no ffmpeg audio
        return []
    floor, peak = float(np.percentile(env, 10)), float(np.percentile(env, 99))
    ev = []
    on = env >= max(floor + 15.0, peak - 30.0)
    k = 0
    while k < len(on):
        if on[k]:
            r = k
            while r + 1 < len(on) and on[r + 1]:
                r += 1
            a, b = t0 + k * 0.01, t0 + (r + 1) * 0.01
            if ev and a - ev[-1][1] < 0.3:
                ev[-1][1] = b
            else:
                ev.append([a, b])
            k = r + 1
        else:
            k += 1
    return [e for e in ev if e[1] - e[0] >= 0.15]


def _shots(sc, t0, t1):
    edges = [t0] + [c for c in sc['cuts'] if t0 + 0.05 < c < t1 - 0.05] + [t1]
    return [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]


def _shot_tracks(sc, a, b):
    """tracks inside one shot: id -> list of (t, face dict); first sample of a shot has no motion values."""
    smp = [x for x in sc['samples'] if a - 1e-6 <= x['t'] < b - 1e-6]
    tr = {}
    for x in smp:
        for f in x['faces']:
            tr.setdefault(f['track'], []).append((x['t'], f))
    n = max(1, len(smp))
    # the same person re-detected after a gap: tracks that never co-occur and sit at the same place are one
    ids = sorted(tr, key=lambda k: tr[k][0][0])
    members = {k: [k] for k in ids}
    for i, a_id in enumerate(ids):
        if a_id not in tr:
            continue
        for b_id in ids[i + 1:]:
            if b_id not in tr:
                continue
            ta, tb = {t for t, _ in tr[a_id]}, {t for t, _ in tr[b_id]}
            if ta & tb:
                continue
            ma = np.median([f['box'] for _, f in tr[a_id]], axis=0)
            mb = np.median([f['box'] for _, f in tr[b_id]], axis=0)
            wa, wb = ma[2] - ma[0], mb[2] - mb[0]
            dc = np.hypot((ma[0] + ma[2] - mb[0] - mb[2]) / 2, (ma[1] + ma[3] - mb[1] - mb[3]) / 2)
            if _iou(ma, mb) > 0.3 or (dc < 0.9 * (wa + wb) / 2 and max(wa, wb) < 1.5 * min(wa, wb)):
                tr[a_id] = sorted(tr[a_id] + tr.pop(b_id), key=lambda x: x[0])
                members[a_id] += members.pop(b_id)
    keep = {}
    for tid, items in tr.items():
        if len(items) >= max(2, 0.25 * n):
            first_t = items[0][0]
            keep[tid] = [(t, dict(f, mouth=None if t == first_t else f['mouth'],
                                  eyes=None if t == first_t else f['eyes'])) for t, f in items]
    return keep, n, {k: members[k] for k in keep}


def _articulation(items):
    vals = []
    for t, f in items:
        if f.get('mouth') is None:
            continue
        vals.append((t, max(0.0, f['mouth'] - 0.8 * (f.get('eyes') or 0.0))))
    return vals


def active_speaker(path, t0, t1, box=None, words=None, sample_fps=10.0, scan_data=None, min_turn=1.0):
    """Who is on screen and who talks, per camera shot (see module doc)."""
    sc = scan_data or scan(path, t0, t1, box=box, sample_fps=sample_fps)
    ws = None
    if words is not None:
        ws = words.get('words', []) if isinstance(words, dict) else list(words)
    if ws is not None:
        utt_all = _utterances(ws, t0, t1)
    else:                                                   # no words: sound stretches in <= 1.5 s scoring windows
        utt_all = []
        for u0, u1 in _audio_utterances(path, t0, t1):
            k = max(1, int(np.ceil((u1 - u0) / 1.5)))
            utt_all += [[u0 + (u1 - u0) * i / k, u0 + (u1 - u0) * (i + 1) / k] for i in range(k)]
    shots = []
    for si, (a, b) in enumerate(_shots(sc, t0, t1)):
        tracks, n, members = _shot_tracks(sc, a, b)
        tinfo = []
        for tid, items in tracks.items():
            boxes = np.array([f['box'] for _, f in items])
            art = _articulation(items)
            tinfo.append(dict(id=tid, ids=members[tid], presence=round(len(items) / n, 2),
                              face=[round(float(v), 1) for v in np.median(boxes, axis=0)],
                              talk=round(float(np.mean([v for _, v in art])), 3) if art else None))
        tinfo.sort(key=lambda d: -d['presence'] * (d['face'][3] - d['face'][1]))
        turns, utt_out = [], []
        if len(tinfo) == 1:
            turns = [[a, b, tinfo[0]['id']]]
        elif len(tinfo) >= 2:
            utt = [[max(a, u0), min(b, u1)] for u0, u1 in utt_all if u1 > a and u0 < b]
            arts = {d['id']: _articulation(tracks[d['id']]) for d in tinfo}
            labels, scores = [], []
            for u0, u1 in utt:
                sco = {}
                for k, vals in arts.items():
                    inside = [v for t, v in vals if u0 - 0.05 <= t <= u1 + 0.05]
                    if len(inside) >= 2:
                        sco[k] = float(np.mean(inside))
                scores.append({str(k): round(v, 2) for k, v in sco.items()})
                if not sco:
                    labels.append(None)
                    continue
                order = sorted(sco, key=lambda k: -sco[k])
                if len(order) == 1 or sco[order[0]] >= 1.15 * sco[order[1]]:
                    labels.append(order[0])
                else:
                    labels.append(None)
            # unknown utterances inherit the previous (or the next) speaker; none at all -> the most present face
            for i in range(len(labels)):
                if labels[i] is None:
                    labels[i] = next((labels[j] for j in range(i - 1, -1, -1) if labels[j] is not None), None)
            for i in range(len(labels) - 1, -1, -1):
                if labels[i] is None:
                    labels[i] = next((labels[j] for j in range(i + 1, len(labels)) if labels[j] is not None), None)
            utt_out = [[round(u0, 3), round(u1, 3), lab, sc_] for (u0, u1), lab, sc_ in zip(utt, labels, scores)]
            if not utt or all(x is None for x in labels):
                turns = [[a, b, tinfo[0]['id']]]
            else:
                cur, start = labels[0], a
                for i in range(1, len(utt)):
                    if labels[i] != cur:
                        sw = min(utt[i][0], max(utt[i - 1][1] + 0.05, utt[i][0] - 0.25))
                        turns.append([start, sw, cur])
                        cur, start = labels[i], sw
                turns.append([start, b, cur])
                # merge turns shorter than min_turn into the longer neighbour
                merged = True
                while merged and len(turns) > 1:
                    merged = False
                    for i, (x0, x1, who) in enumerate(turns):
                        if x1 - x0 < min_turn:
                            if i == 0:
                                turns[1][0] = x0
                            elif i == len(turns) - 1 or (turns[i - 1][1] - turns[i - 1][0] >=
                                                         turns[i + 1][1] - turns[i + 1][0]):
                                turns[i - 1][1] = x1
                            else:
                                turns[i + 1][0] = x0
                            del turns[i]
                            merged = True
                            break
                    # neighbours with the same speaker join
                    j = 1
                    while j < len(turns):
                        if turns[j][2] == turns[j - 1][2]:
                            turns[j - 1][1] = turns[j][1]
                            del turns[j]
                        else:
                            j += 1
        shots.append(dict(i=si, t0=round(a, 3), t1=round(b, 3), tracks=tinfo,
                          turns=[[round(x0, 3), round(x1, 3), who] for x0, x1, who in turns],
                          utterances=utt_out))
    return dict(cuts=[c for c in sc['cuts'] if t0 < c < t1], shots=shots)


# ============================================================================ speaker crop
PRIORITY = {'ui': 0, 'text': 1, 'logo': 2}


def _avoid_list(avoid, box):
    out = []
    for a in avoid or []:
        if isinstance(a, dict):
            b, kind = a.get('box'), a.get('kind', 'text')
        else:
            b, kind = a, 'text'
        if b is None:
            continue
        x0, y0, x1, y1 = [float(v) for v in b]
        x0, x1 = max(x0, box[0]) - box[0], min(x1, box[2]) - box[0]
        y0, y1 = max(y0, box[1]) - box[1], min(y1, box[3]) - box[1]
        if x1 > x0 and y1 > y0:
            out.append(dict(box=[x0, y0, x1, y1], kind=kind))
    return out


def _head(face, ww=None):
    """head box (box px) from a face box (box px): hair above, ears at the sides, chin + neck below."""
    x0, y0, x1, y1 = face
    w, h = x1 - x0, y1 - y0
    return [x0 - 0.22 * w, y0 - 0.35 * h, x1 + 0.22 * w, y1 + 0.18 * h]


def _intervals(heads, z, bw, bh, aspect, sides, avoid, margin):
    """per-sample feasible centre intervals for zoom z and one side choice per avoid box."""
    hw = bh / z
    ww = hw * aspect
    xlo = np.maximum(heads[:, 2] - ww / 2, ww / 2)
    xhi = np.minimum(heads[:, 0] + ww / 2, bw - ww / 2)
    ylo = np.maximum(heads[:, 3] - hw / 2, hw / 2)
    yhi = np.minimum(heads[:, 1] + hw / 2, bh - hw / 2)
    if ww >= bw:
        xlo = xhi = np.full(len(heads), bw / 2)
    for side, av in zip(sides, avoid):
        ax0, ay0, ax1, ay1 = av['box']
        if side == 'L':
            xhi = np.minimum(xhi, ax0 - margin - ww / 2)
        elif side == 'R':
            xlo = np.maximum(xlo, ax1 + margin + ww / 2)
        elif side == 'T':
            yhi = np.minimum(yhi, ay0 - margin - hw / 2)
        else:
            ylo = np.maximum(ylo, ay1 + margin + hw / 2)
    return xlo, xhi, ylo, yhi


def _relevant(avoid, heads, z, bw, bh, aspect, margin):
    """avoid boxes a window of zoom z around these heads could touch."""
    hw = bh / z
    ww = hw * aspect
    rx0, rx1 = max(0.0, heads[:, 2].min() - ww) - margin, min(bw, heads[:, 0].max() + ww) + margin
    ry0, ry1 = max(0.0, heads[:, 3].min() - hw) - margin, min(bh, heads[:, 1].max() + hw) + margin
    return [a for a in avoid if a['box'][2] > rx0 and a['box'][0] < rx1 and a['box'][3] > ry0 and a['box'][1] < ry1]


def _solve_z(heads, targets, bw, bh, aspect, avoid, margin, z_lo, z_hi, step=0.01):
    """smallest z (and side choice) with a feasible window at every sample; ties -> closest to the targets."""
    import itertools
    z = z_lo
    while z <= z_hi + 1e-9:
        rel = _relevant(avoid, heads, z, bw, bh, aspect, margin)
        best = None
        for sides in itertools.product('LRTB', repeat=len(rel)):
            xlo, xhi, ylo, yhi = _intervals(heads, z, bw, bh, aspect, sides, rel, margin)
            if np.all(xlo <= xhi + 1e-6) and np.all(ylo <= yhi + 1e-6):
                px = np.clip(targets[:, 0], xlo, np.maximum(xlo, xhi))
                py = np.clip(targets[:, 1], ylo, np.maximum(ylo, yhi))
                cost = float(((px - targets[:, 0]) ** 2).sum() + ((py - targets[:, 1]) ** 2).sum())
                if best is None or cost < best[0]:
                    best = (cost, sides, rel)
        if best is not None:
            return round(z, 3), best[1], best[2]
        z += step
    return None


def _follow(target, lo, hi, sample_fps, span, static_tol):
    """centre track inside [lo, hi] per sample: static when one value fits and the target barely moves, else a
    smoothed follow (gaussian 0.6 s + projection, iterated)."""
    lo, hi = np.asarray(lo, float), np.maximum(np.asarray(lo, float), np.asarray(hi, float))
    L, U = float(lo.max()), float(hi.min())
    spread = float(np.percentile(target, 90) - np.percentile(target, 10)) if len(target) > 2 else 0.0
    if L <= U + 1e-6 and spread <= static_tol:
        return np.full(len(target), float(np.clip(np.median(target), L, max(L, U)))), True
    x = np.clip(np.asarray(target, float), lo, hi)
    if len(x) >= 3:
        x = median_filter(x, size=min(5, len(x) // 2 * 2 + 1), mode='nearest')
    sig = max(1.0, 0.6 * sample_fps)
    for _ in range(25):
        x = np.clip(gaussian_filter1d(x, sig, mode='nearest'), lo, hi)
    return x, False


def _simplify(keys, tol):
    """drop path keys that linear interpolation reproduces within tol (each of cx, cy, z)."""
    if len(keys) <= 2:
        return keys
    out = [keys[0]]
    i = 0
    while i < len(keys) - 1:
        j = i + 1
        while j + 1 < len(keys):
            ok = True
            a, b = keys[i], keys[j + 1]
            for m in range(i + 1, j + 1):
                u = (keys[m][0] - a[0]) / max(1e-9, b[0] - a[0])
                if any(abs(a[c] + (b[c] - a[c]) * u - keys[m][c]) > tol for c in (1, 2, 3)):
                    ok = False
                    break
            if not ok:
                break
            j += 1
        out.append(keys[j])
        i = j
    return out


def _person_head(path, t, box, info):
    """fallback face box (source px) from the person mask at time t."""
    try:
        return _person_head_at(path, t, box, info)
    except Exception:                                       # unreadable frame / no segmentation model
        return None


def _person_head_at(path, t, box, info):
    for _, fr in V.frames(path, t, t + 0.05, fps=10, width=640, crop=box, info=info):
        m = V.person_mask(fr) > 0.5
        if m.mean() < 0.02:
            return None
        ys, xs = np.nonzero(m)
        s = (box[2] - box[0]) / fr.shape[1]
        top = float(np.percentile(ys, 2))
        hgt = 0.18 * (float(np.percentile(ys, 98)) - top) + 8
        cx = float(np.median(xs[ys < top + 2 * hgt])) if (ys < top + 2 * hgt).any() else float(np.median(xs))
        return [box[0] + (cx - 0.4 * hgt) * s, box[1] + (top + 0.35 * hgt) * s, box[0] + (cx + 0.4 * hgt) * s,
                box[1] + (top + 1.35 * hgt) * s]
    return None


def speaker_crop(path, t0, t1, box=None, avoid=None, canvas=(1080, 1920), fps=30, words=None, *, face_min=0.16,
                 face_max=0.42, eye_line=0.38, max_upscale=2.0, sample_fps=10.0, margin=0.012, detail=False):
    """Vertical crops that follow the speaking (or only visible) face, split at camera cuts (see module doc)."""
    info = V.probe(path)
    W, H = info['w'], info['h']
    box = [int(v) for v in (box or [0, 0, W, H])]
    bw, bh = box[2] - box[0], box[3] - box[1]
    aspect = canvas[0] / canvas[1]
    sc = scan(path, t0, t1, box=box, sample_fps=sample_fps)
    sp = active_speaker(path, t0, t1, box=box, words=words, sample_fps=sample_fps, scan_data=sc)
    av = _avoid_list(avoid, box)
    mg = margin * bh
    z_res = max(1.0, bh * max_upscale / canvas[1])
    z_hard = max(z_res, bh * 3.0 / canvas[1])
    out, notes = [], []
    prev_face = None
    for shot in sp['shots']:
        alias = {r: tr['id'] for tr in shot['tracks'] for r in tr.get('ids', [tr['id']])}
        for a, b, who in (shot['turns'] or [[shot['t0'], shot['t1'], None]]):
            items = [(x['t'], f) for x in sc['samples'] if a - 1e-6 <= x['t'] < b - 1e-6
                     for f in x['faces'] if who is not None and alias.get(f['track']) == who]
            subject = 'face'
            if not items:
                fb = _person_head(path, (a + b) / 2, box, info)
                subject = 'person' if fb else 'center'
                if fb is None:
                    fb = prev_face or [box[0] + bw * 0.4, box[1] + bh * 0.2, box[0] + bw * 0.6, box[1] + bh * 0.4]
                items = [(a, dict(box=fb, eyes_y=fb[1] + 0.4 * (fb[3] - fb[1])))]
            ts = np.array([t for t, _ in items])
            faces = np.array([f['box'] for _, f in items], float) - [box[0], box[1], box[0], box[1]]
            eyes = np.array([(f.get('eyes_y') or (f['box'][1] + 0.4 * (f['box'][3] - f['box'][1]))) - box[1]
                             for _, f in items], float)
            if len(faces) >= 3:                              # detector jitter: running median per coordinate
                faces = np.stack([median_filter(faces[:, c], size=3, mode='nearest') for c in range(4)], axis=1)
                eyes = median_filter(eyes, size=3, mode='nearest')
            heads = np.array([_head(f) for f in faces])
            heads = np.clip(heads, 0, [bw, bh, bw, bh])          # what the frame does not show cannot be cut
            fh = float(np.median(faces[:, 3] - faces[:, 1]))
            z_lo = min(max(1.0, face_min * bh / max(fh, 1.0)), z_res)
            z_top = min(z_res, max(1.0, face_max * bh / max(fh, 1.0)))
            z_top = max(z_top, z_lo)

            def targets(z):
                hw = bh / z
                return np.stack([(faces[:, 0] + faces[:, 2]) / 2, eyes + (0.5 - eye_line) * hw], axis=1)
            released = []
            sol = None
            pool = list(av)
            while sol is None:
                tg = targets(z_lo)
                sol = _solve_z(heads, tg, bw, bh, aspect, pool, mg, z_lo, max(z_top, z_res))
                if sol is None:
                    sol = _solve_z(heads, tg, bw, bh, aspect, pool, mg, max(z_top, z_res) + 0.01, z_hard)
                if sol is None:
                    if not pool:
                        sol = (z_lo, (), [])
                        break
                    drop = min(pool, key=lambda x: PRIORITY.get(x['kind'], 1))
                    pool.remove(drop)
                    released.append(drop['kind'])
            z, sides, rel = sol
            tg = targets(z)
            xlo, xhi, ylo, yhi = _intervals(heads, z, bw, bh, aspect, sides, rel, mg)
            hw = bh / z
            ww = hw * aspect
            cxs, static_x = _follow(tg[:, 0], xlo, xhi, sample_fps, b - a, 0.08 * ww)
            cys, static_y = _follow(tg[:, 1], ylo, yhi, sample_fps, b - a, 0.06 * hw)
            n_out = max(1, int(round((b - a) * fps)))
            crop = dict(cx=round(float(cxs[0] / bw), 4), cy=round(float(cys[0] / bh), 4), z=z)
            if not (static_x and static_y) and len(ts) >= 2:
                keys = []
                for t, x, y in zip(ts, cxs, cys):
                    k = int(round((t - a) * fps))
                    if 0 <= k < n_out and (not keys or k > keys[-1][0]):
                        keys.append([k, round(float(x / bw), 4), round(float(y / bh), 4), z])
                if keys and keys[0][0] > 0:
                    keys.insert(0, [0] + keys[0][1:])
                if keys and keys[-1][0] < n_out - 1:
                    keys.append([n_out - 1] + keys[-1][1:])
                keys = _simplify(keys, 0.002)
                moving = any(abs(k[j] - keys[0][j]) > 0.002 for k in keys for j in (1, 2))
                if len(keys) >= 2 and moving:
                    crop['path'] = keys
                    crop['cx'], crop['cy'] = keys[0][1], keys[0][2]
            med_face = [round(float(v), 1) for v in (np.median(faces, axis=0) + [box[0], box[1], box[0], box[1]])]
            prev_face = med_face
            item = dict(t0=round(a, 3), t1=round(b, 3), crop=crop, shot=shot['i'], speaker=who, face=med_face,
                        subject=subject)
            if released:
                item['released'] = released
                notes.append(f'{a:.2f}-{b:.2f}: could not keep {released} out of the frame')
            out.append(item)
    if detail:
        return out, dict(cuts=sc['cuts'], shots=sp['shots'], notes=notes, box=box)
    return out


def sub_crop(item, t0, t1, fps=30):
    """crop of a speaker_crop item for its sub-range [t0, t1] (seconds inside item t0..t1): path re-based to the
    sub-range start (k = 0 at t0); a static crop is returned unchanged."""
    c = dict(item['crop'])
    path = c.pop('path', None)
    if not path:
        return c
    off = (t0 - item['t0']) * fps
    n = max(1, int(round((t1 - t0) * fps)))
    ks = [p[0] for p in path]

    def at(k):
        return [float(np.interp(k, ks, [p[j] for p in path])) for j in (1, 2, 3)]
    keys = [[0] + [round(v, 4) for v in at(off)]]
    for p in path:
        k = p[0] - off
        if 0 < k < n - 1:
            keys.append([int(round(k))] + p[1:])
    keys.append([n - 1] + [round(v, 4) for v in at(off + n - 1)])
    keys = _simplify(keys, 0.002)
    c['cx'], c['cy'], c['z'] = keys[0][1], keys[0][2], keys[0][3]
    if len(keys) >= 2 and any(abs(keys[i][j] - keys[0][j]) > 1e-4 for i in range(len(keys)) for j in (1, 2, 3)):
        c['path'] = keys
    return c


def crop_pieces(items, t0, t1, fps=30):
    """speaker_crop items cut to the source range [t0, t1] -> [{"t0", "t1", "crop", "shot", "speaker"}] (each crop
    re-based with sub_crop) - one EDL segment per piece, in order."""
    out = []
    for it in items:
        a, b = max(t0, it['t0']), min(t1, it['t1'])
        if b - a > 0.5 / fps:
            out.append(dict(t0=round(a, 3), t1=round(b, 3), crop=sub_crop(it, a, b, fps), shot=it.get('shot'),
                            speaker=it.get('speaker')))
    return out


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description='ed_reframe: speaker crops for talk clips, subject crop paths')
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('speaker', help='speaker crops (EDL crop format) over [t0, t1]')
    s.add_argument('media')
    s.add_argument('t0', type=float)
    s.add_argument('t1', type=float)
    s.add_argument('--box', help='x0,y0,x1,y1 | auto (content_box)', default='auto')
    s.add_argument('--avoid', default='auto', help='auto (static_overlays) | none')
    s.add_argument('--words', help='words.json (transcript) for speaker turns')
    s.add_argument('--canvas', default='1080x1920')
    s.add_argument('--fps', type=float, default=30)
    s.add_argument('--out')
    p = sub.add_parser('path', help='legacy subject crop path')
    p.add_argument('media')
    p.add_argument('t_in', type=float)
    p.add_argument('dur', type=float)
    a = ap.parse_args(argv)
    if a.cmd == 'path':
        print(json.dumps(crop_path(a.media, a.t_in, a.dur)))
        return
    box = V.content_box(a.media, a.t0, a.t1) if a.box == 'auto' else [int(float(v)) for v in a.box.split(',')]
    avoid = V.static_overlays(a.media, box, a.t0, a.t1) if a.avoid == 'auto' else []
    words = None
    if a.words:
        with open(a.words) as fh:
            words = json.load(fh)
    cw, ch = [int(v) for v in a.canvas.lower().split('x')]
    segs, det = speaker_crop(a.media, a.t0, a.t1, box=box, avoid=avoid, canvas=(cw, ch), fps=a.fps, words=words,
                             detail=True)
    res = dict(det, avoid=avoid, segments=segs)
    s = json.dumps(res, indent=1)
    if a.out:
        with open(a.out, 'w') as fh:
            fh.write(s)
        print('->', a.out)
    print(json.dumps(dict(box=box, avoid=avoid, cuts=det['cuts'], notes=det['notes'],
                          segments=[{k: v for k, v in x.items() if k != 'crop'} | {'z': x['crop']['z']}
                                    for x in segs]), indent=1))


if __name__ == '__main__':
    main()
