#!/usr/bin/env python3
"""Scenario 1 drafter — remake a reference edit with the user's own footage (same timing, same text, same moves).

    draft(reference, footage, out_dir, canvas=(1080, 1920), fps=None, sample_fps=3.0, music=None, music_in=None,
          names=None) -> EDL dict (engine/TIMELINE.md)      footage = one path or a list (several sources)
    repick(edl, out_dir, {slot: time | (source, time)}) -> new EDL     swap slot moments (crop + grade recomputed)
    compare_sheet(reference, remake_mp4, out_jpg, edl=None) -> rows     reference | remake side by side per slot
    survey_sheet(idx, out_jpg) -> (files, tiles)                       every shot of the footage, labelled
    align_music(reference, track) -> {offset, ncc, prominence, aligned}  where the reference audio sits in a track
    measure_effect(clip, fps=None, sheet=None) -> {events, candidates}  a short clip / GIF of one effect -> ranked
          move cards with params and a ready ed_plan.apply command (edit.py measure-ref CLIP --sheet S.jpg)

CLI (python3 -I ed_remake.py -h)
    ed_remake.py REFERENCE FOOTAGE [FOOTAGE ...] OUT_DIR [--music TRACK [--music-in S]] [--canvas 1080x1920]
                 [--fps 30] [--sample-fps 3] [--compare HAND_EDL.json]
    ed_remake.py pick EDL.json OUT_DIR S05=12:34.5 [#7=SOURCE@1:02.0 ...] [--out NEW.json]
    ed_remake.py survey FOOTAGE [FOOTAGE ...] --out-dir DIR      ed_remake.py sheet REFERENCE REMAKE.mp4 OUT.jpg [--edl E]
    ed_remake.py align REFERENCE TRACK      ed_remake.py compare OUT_DIR HAND_EDL.json      ed_remake.py decompose REF DIR
    (edit.py remake runs draft -> preview -> QA -> compare sheet, and --pick for swaps.)

OUT_DIR receives: edl_draft.json, candidates.json (per slot: descriptors + top-5 candidates with source, time, score
terms, crop), decomposition.json (frame-level analysis of the reference), slots.jpg (+ slots_pNN.jpg: reference frame
| top-5 candidate 9:16 crops graded like the EDL would, chosen one framed), survey.jpg (+ survey_pNN.jpg, survey.json:
one tile per sample-level shot of every footage file, 'n source@m:ss.s type', SUBS = burned-in text), and one cached
index per footage file (footage_index[_<source>].npz/.json, reused while file, size, mtime and sampling are unchanged).
slots.jpg shows reference frames: keep OUT_DIR out of anything that is shared or packed.

Several footage files: each is indexed on its own and merged (shots never span two files); EDL sources are named
after the files (one file: 'footage'); candidates, diversity and the no-overlap rule work per source.
Music: --music TRACK replaces the reference mix by a clean track (audio.music). Its in-point is found by
align_music (spectral-flux onset envelopes, normalised cross-correlation, 10 ms grid + parabolic refinement; robust to
voice/SFX on top); a track that does not match (ncc < 0.5) starts at 0 with a warning, --music-in S sets it by hand.

Review flow for choosing shots (the draft is a starting point; a remake with different footage is a translation of
roles, which the matcher cannot know: "hands on a keyboard" may become "hands over a fire"):
 1. Read slots_pNN.jpg: each row = the reference slot and its top-5 candidates (green = chosen). The tag shows the
    slot's subject type/scale and B&W; candidates.json has the numbers behind every tile.
 2. Read survey_pNN.jpg (or survey.json): every shot of the footage with its time. Pick moments that play the same
    role as the reference slot (subject, scale, motion direction, light), not the same object.
 3. Swap: ed_remake.py pick EDL OUT_DIR S05=12:34.5 S07=clip2@0:41 (or edit.py remake --project P --pick ...). The
    time is the in-point (first frame of the slot); crop, grade and blur are recomputed for the new moment, hand-added
    fx and transitions stay. Render the preview and check compare_vN.jpg (reference | remake per slot; red = the look
    differs a lot: luma, contrast or B&W).

Pipeline
 1. Frame-exact decomposition at the reference's fps. Every frame is classified: content | white (opacity a,
    stage pre/post vs text) | black | inverted (negative of its shot; majority polarity, near-ties: brighter = negative)
    | pflash (white silhouette / object highlight, <= 3 frames, picture returns) | insert (A/B flicker inside a shot).
    Boundaries between consecutive content frames are compared on text-masked frames: structure (band-pass NCC,
    LK/ECC-aligned NCC from ed_motion), colour/luma histograms, streak (whip) coherence. Types: cut | regrade
    (same picture structure, new grade -> same source, new grade) | punch (isolated scale jump of the same shot).
    Slots = runs between boundaries; flash/black frames stay in the slot of the previous content frame.
    Per slot: camera move (per frame pair: an LK similarity or ECC fit is used only when it beats the phase-correlation
    shift clearly and stays plausible, <= 3 deg / 12 % per frame, else the shift: no invented rolls on one-directional
    structure; cumulative zoom/shift/rotation + easing), cadence (duplicate frames, holds), blur/streak direction,
    B&W vs colour, grade target (luma quantiles, saturation, cast).
 2. Text without OCR: bright-neutral (pure white or top-hat) and saturated components (adaptive threshold on B&W
    pictures), stroke/fill/contrast filters, grouped into words, tracked; a second pass extends static tracks with
    their glyph template (through flashes, low contrast, inverted frames) and measures colour/blend (difference
    blend = complementary hue over bright background). Overlay = crosses a cut, starts/ends inside a shot,
    saturated on B&W, or belongs to a block of such text. Words that appear together on a line form one item; a line
    that grows ("ONE" -> "ONE MORE") yields one item per new part. Words become placeholders ('X' * glyphs) with
    ids T01.. (texts[].items[].slot) for Claude/user to fill; 'w' = the reference width on the canvas.
 3. Slot descriptors: subject type (face/person/hands/object/landscape/texture: YuNet, PP-HumanSeg, NanoDet when its
    model file is installed - optional), scale, subject position, motion energy/direction, luminance, colour/B&W,
    9:16-window HOG + layout, detail.
 4. Footage index at 2-4 fps (letterbox box + corner logo from keyframes, burned-in subtitle lines, sample-level
    shots - band-pass NCC, colour, LK/ECC- and phase-correlation-aligned NCC -, same descriptors + JPEG thumbs).
    Per slot every term is z-scored over the footage, weighted, aggregated over the slot span; top 5 kept with
    diversity (>= 3 s apart per source, <= 2 per shot). Leaders are assigned greedily without overlapping footage
    and without subtitles; regrade/punch/reused slots follow their leader's source (the reference reuses a shot ->
    the remake reuses one).
 5. EDL: segments (subject-centred 9:16 crop, scale match on faces, reference move mapped to crop 'to', streak ->
    dirblur), grade fitted with ed_edl.apply_grade to the slot's luma quantiles/saturation/cast, ops copied
    frame-exactly (pflash -> mask_flash on people, rect_flash otherwise; flicker -> ghosts from an alternate),
    text layers re-laid out for the canvas (uniform scale from the dominant cap height, block-relative positions,
    safe band), audio = reference mix or the music track. Segments carry 'alts' (other candidates) and a 'note';
    meta.remake_dir points at OUT_DIR (repick reads it).
Measured: self-remake (reference cut from two footage files, 5 slots incl. a white flash): 5/5 cuts exact, true
moment within 1 s in the top 5 of 5/5 slots, music offset 1.992 s for 2.000 s. Speed: the footage index dominates
(about 0.1 s per sample on 2 free cores) and is cached; reference analysis ~30 s for 17 s at 30 fps.
"""
import os, sys, json, math, time, argparse, hashlib, subprocess, tempfile
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ed_video as V        # noqa: E402  probe, YuNet faces, PP-HumanSeg person mask
import ed_motion as M       # noqa: E402  estimate_pair / similarity_from_affine / ease_label

VERSION = 5                   # footage index format (5: phase-aligned NCC in pair[:, 3])
GEOM_VERSION = 2              # letterbox/logo detection (refreshed alone in a cached index)
AW = 384                    # reference analysis width (stored RGB)
GW = 256                    # grey width for pair features
TW_MAX = 960                # text detection width
FW = 480                    # footage analysis width (picture box)
THUMB_W = 384               # footage thumbnail width (JPEG in the index)
WIN_SZ = (48, 84)           # 9:16 window descriptor size (w, h)
HOG_CELL = 12
TYPES = ['face', 'person', 'hands', 'object', 'landscape', 'texture']
COMPAT = np.array([         # slot type (rows) x footage type (cols)
    [1.0, 0.5, 0.2, 0.0, 0.0, 0.1],
    [0.5, 1.0, 0.3, 0.1, 0.2, 0.0],
    [0.1, 0.4, 1.0, 0.5, 0.0, 0.3],
    [0.0, 0.1, 0.5, 1.0, 0.2, 0.6],
    [0.0, 0.3, 0.0, 0.2, 1.0, 0.4],
    [0.0, 0.0, 0.3, 0.6, 0.4, 1.0]], np.float32)
CAP_RATIO = {'sans': 0.73, 'oswald': 0.81}


def log(*a):
    print('[remake]', *a, file=sys.stderr, flush=True)


# =============================================================================================== small helpers
def _ncc(a, b):
    a = a - a.mean()
    b = b - b.mean()
    d = math.sqrt(float((a * a).sum()) * float((b * b).sum())) + 1e-6
    return float((a * b).sum() / d)


def _hp(g):
    """Band-pass structure image (128 px wide) used for structural correlation."""
    s = cv2.resize(g, (128, max(8, int(round(128 * g.shape[0] / g.shape[1])))), interpolation=cv2.INTER_AREA)
    return cv2.GaussianBlur(s, (0, 0), 1.0) - cv2.GaussianBlur(s, (0, 0), 4.0)


def _fill(img, mask, sigma=None):
    """Replace masked pixels by a smooth interpolation of their surroundings (normalized convolution)."""
    if mask is None or not mask.any():
        return img
    m = (mask > 0).astype(np.float32)
    x = img.astype(np.float32)
    sig = sigma or max(3.0, 0.03 * img.shape[1])
    out = x.copy()
    w = 1.0 - m
    for s in (sig, sig * 3, sig * 9):
        if x.ndim == 3:
            num = cv2.GaussianBlur(x * w[..., None], (0, 0), s)
            den = cv2.GaussianBlur(w, (0, 0), s)
            est = num / np.maximum(den, 1e-4)[..., None]
        else:
            num = cv2.GaussianBlur(x * w, (0, 0), s)
            den = cv2.GaussianBlur(w, (0, 0), s)
            est = num / np.maximum(den, 1e-4)
        sel = (m > 0) & (den > 0.02)
        out[sel] = est[sel]
        m = m * (den <= 0.02)
        if not m.any():
            break
    return out if img.dtype == np.float32 else np.clip(out, 0, 255).astype(img.dtype)


def _hist_hsv(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h = cv2.calcHist([hsv], [0, 1, 2], None, [16, 4, 4], [0, 180, 0, 256, 0, 256]).flatten()
    return h / (h.sum() + 1e-9)


def _hist_luma(g):
    h = np.histogram(g, bins=32, range=(0, 256))[0].astype(np.float32)
    h = np.convolve(h, np.array([0.25, 0.5, 0.25], np.float32), mode='same')
    return h / (h.sum() + 1e-9)


def _bhatt(h1, h2):
    return float(np.sqrt(max(0.0, 1.0 - float(np.sum(np.sqrt(h1 * h2))))))


def _runs(idx):
    """Sorted ints -> list of (a, b) inclusive runs."""
    out = []
    for i in sorted(idx):
        if out and i == out[-1][1] + 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return [tuple(r) for r in out]


def _tc(t):
    m, s = divmod(max(0.0, float(t)), 60)
    return f'{int(m)}:{s:05.2f}'


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items() if not str(k).startswith('_')}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return _jsonable(o.tolist())
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        v = float(o)
        return None if not math.isfinite(v) else round(v, 4)
    return o


def _luma01(x):
    return x[..., 0] * 0.2126 + x[..., 1] * 0.7152 + x[..., 2] * 0.0722


def _decode(path, width, fps=None, t0=None, dur=None, crop=None, gray=False, keyframes=False):
    """Yield frames (uint8) decoded by ffmpeg: optional crop box [x0,y0,x1,y1] (source px), scaled to `width`."""
    info = V.probe(path)
    W, H = info['w'], info['h']
    if crop:
        W, H = crop[2] - crop[0], crop[3] - crop[1]
    h = max(2, int(round(H * width / W / 2) * 2))
    vf = []
    if fps:
        vf.append(f'fps={fps}')
    if crop:
        vf.append(f'crop={crop[2] - crop[0]}:{crop[3] - crop[1]}:{crop[0]}:{crop[1]}')
    vf.append(f'scale={width}:{h}:flags=area')
    cmd = ['ffmpeg', '-v', 'error', '-nostdin']
    if keyframes:
        cmd += ['-skip_frame', 'nokey']
    if t0:
        cmd += ['-ss', f'{t0:.4f}']
    cmd += ['-i', path]
    if dur:
        cmd += ['-t', f'{dur:.4f}']
    if keyframes:
        cmd += ['-fps_mode', 'passthrough']
    cmd += ['-an', '-vf', ','.join(vf), '-f', 'rawvideo', '-pix_fmt', 'gray' if gray else 'rgb24', '-']
    ch = 1 if gray else 3
    size = width * h * ch
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=size * 4)
    try:
        while True:
            buf = p.stdout.read(size)
            if len(buf) < size:
                break
            a = np.frombuffer(buf, np.uint8)
            yield a.reshape(h, width) if gray else a.reshape(h, width, 3)
    finally:
        p.stdout.close()
        p.kill()
        p.wait()


_HANN = {}


def _phase_shift(ga, gb):
    """Dominant translation a->b by phase correlation (Hann window) -> (sx, sy, response). Inputs are copied:
    cv2.phaseCorrelate windows its arguments in place."""
    h, w = ga.shape[:2]
    win = _HANN.get((w, h))
    if win is None:
        win = _HANN[(w, h)] = cv2.createHanningWindow((w, h), cv2.CV_32F)
    (sx, sy), resp = cv2.phaseCorrelate(np.array(ga, np.float32, copy=True), np.array(gb, np.float32, copy=True), win)
    return float(sx), float(sy), float(resp)


def _shift_ncc(ga, gb, sx, sy):
    """Band-pass NCC of b against a shifted by (sx, sy), on the overlap only (no border fill)."""
    h, w = ga.shape[:2]
    ix, iy = int(round(sx)), int(round(sy))
    if abs(ix) >= w // 2 or abs(iy) >= h // 2:
        return -1.0
    a = ga[max(0, -iy):h - max(0, iy), max(0, -ix):w - max(0, ix)]
    b = gb[max(0, iy):h - max(0, -iy), max(0, ix):w - max(0, -ix)]
    if a.size < 64:
        return -1.0
    return _ncc(_hp(a.astype(np.float32)), _hp(b.astype(np.float32)))


def _iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    i = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0.0


def _inside(a, b):
    """Fraction of box a inside box b."""
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return ix * iy / max(1e-6, (a[2] - a[0]) * (a[3] - a[1]))


def _streak(g):
    """Directional-blur signature: (coherence of the structure tensor, blur direction deg, fine/mid detail ratio)."""
    g = cv2.GaussianBlur(g.astype(np.float32), (0, 0), 0.8)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    jxx, jyy, jxy = float((gx * gx).mean()), float((gy * gy).mean()), float((gx * gy).mean())
    tr = jxx + jyy
    disc = math.sqrt(max(tr * tr / 4 - (jxx * jyy - jxy * jxy), 0.0))
    coh = (2 * disc) / (tr + 1e-6)
    ang = 0.5 * math.degrees(math.atan2(2 * jxy, jxx - jyy))
    b1 = cv2.GaussianBlur(g, (0, 0), 1.0)
    b3 = cv2.GaussianBlur(g, (0, 0), 3.0)
    br = float(((g - b1) ** 2).mean()) / (float(((b1 - b3) ** 2).mean()) + 1e-3)
    return coh, (ang + 90.0) % 180.0, br


# =============================================================================================== detectors
_NANO = None
_NANO_FILE = 'object_detection_nanodet_2022nov.onnx'
_NANO_MEAN = np.array([103.53, 116.28, 123.675], np.float32)
_NANO_STD = np.array([57.375, 57.12, 58.395], np.float32)


def _nanodet_path():
    """NanoDet-Plus weights: engine/models (dev tree / packages that ship it) -> the user cache. None = not installed."""
    cache = os.environ.get('EDIT_STUDIO_CACHE') or os.path.join(os.environ.get('ED_ROOT', 'C:/Claude Code/cinema-studio/edit'), 'cache')
    for p in (os.path.join(V.MODELS, _NANO_FILE), os.path.join(cache, 'models', _NANO_FILE)):
        if os.path.exists(p) and os.path.getsize(p) > 1_000_000:
            return p
    return None


def _nanodet(rgb, thr=0.4):
    """NanoDet-Plus (COCO): list of dict(cls, score, box=[x0,y0,x1,y1] fractions). Without the model file (it is
    optional) this returns [] and subjects are typed from faces, person masks and saliency only."""
    global _NANO
    if _NANO is None:
        p = _nanodet_path()
        try:
            _NANO = cv2.dnn.readNet(p) if p else False
        except cv2.error as e:
            log(f'object detector unusable ({e}); objects are not typed')
            _NANO = False
        if _NANO is False and not p:
            log(f'object detector {_NANO_FILE} not installed (optional); objects are not typed')
    if _NANO is False:
        return []
    S = 416
    h, w = rgb.shape[:2]
    s = S / max(h, w)
    nh, nw = int(round(h * s)), int(round(w * s))
    top, left = (S - nh) // 2, (S - nw) // 2
    img = np.zeros((S, S, 3), np.uint8)
    img[top:top + nh, left:left + nw] = cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_AREA)
    _NANO.setInput(cv2.dnn.blobFromImage((img.astype(np.float32) - _NANO_MEAN) / _NANO_STD))
    outs = _NANO.forward(_NANO.getUnconnectedOutLayersNames())
    cls = sorted([o[0] for o in outs if o.shape[-1] == 80], key=lambda a: -a.shape[0])
    reg = sorted([o[0] for o in outs if o.shape[-1] == 32], key=lambda a: -a.shape[0])
    boxes, scores = [], []
    for c, r in zip(cls, reg):
        n = c.shape[0]
        fs = int(round(math.sqrt(n)))
        stride = S // fs
        best = c.max(1)
        keep = np.nonzero(best >= thr)[0]
        if not len(keep):
            continue
        d = r[keep].reshape(-1, 4, 8)
        d = np.exp(d - d.max(2, keepdims=True))
        d = (d / d.sum(2, keepdims=True)) @ np.arange(8, dtype=np.float32) * stride
        yy, xx = np.divmod(keep, fs)
        cx, cy = xx * stride, yy * stride
        b = np.stack([cx - d[:, 0], cy - d[:, 1], cx + d[:, 2], cy + d[:, 3]], 1)
        boxes.append(b)
        scores.append(np.stack([best[keep], c[keep].argmax(1)], 1))
    if not boxes:
        return []
    b = np.concatenate(boxes)
    sc = np.concatenate(scores)
    idx = cv2.dnn.NMSBoxes([[float(x0), float(y0), float(x1 - x0), float(y1 - y0)] for x0, y0, x1, y1 in b],
                           sc[:, 0].astype(float).tolist(), thr, 0.5)
    out = []
    for i in np.array(idx).reshape(-1):
        x0, y0, x1, y1 = b[i]
        out.append(dict(cls=int(sc[i, 1]), score=round(float(sc[i, 0]), 3),
                        box=[round(float(np.clip((x0 - left) / nw, 0, 1)), 3), round(float(np.clip((y0 - top) / nh, 0, 1)), 3),
                             round(float(np.clip((x1 - left) / nw, 0, 1)), 3), round(float(np.clip((y1 - top) / nh, 0, 1)), 3)]))
    return out


def _subject(rgb, bw=None, objects=None, faces=None, pm=None):
    """Subject descriptor of one frame: type, scale, position, face/person/skin measures."""
    H, W = rgb.shape[:2]
    if faces is None:
        big = cv2.resize(rgb, (480, max(2, int(480 * H / W)))) if W != 480 else rgb
        fs = V.faces(big)
        sx = W / big.shape[1]
        faces = [dict(x=f['x'] * sx, y=f['y'] * sx, w=f['w'] * sx, h=f['h'] * sx, score=f['score']) for f in fs]
    if pm is None:
        pm = V.person_mask(rgb)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    if bw is None:
        bw = float(np.median(hsv[..., 1])) < 14
    d = dict(face_n=len(faces), face_h=0.0, person=0.0, skin=0.0, objects=[], bw=bool(bw))
    m = pm > 0.5
    cov = float(m.mean())
    d['person'] = round(cov, 4)
    pbox = None
    if cov > 0.005:
        ys, xs = np.nonzero(m)
        pbox = [xs.min() / W, ys.min() / H, (xs.max() + 1) / W, (ys.max() + 1) / H]
        d['pbox'] = [round(float(v), 3) for v in pbox]
        top = np.percentile(ys, 5)
        d['pcx'] = round(float(np.median(xs)) / W, 3)
        d['pcy'] = round(float(top + 0.25 * (np.percentile(ys, 95) - top)) / H, 3)
    if not bw:
        ycc = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCrCb)
        sk = (ycc[..., 1] >= 135) & (ycc[..., 1] <= 175) & (ycc[..., 2] >= 85) & (ycc[..., 2] <= 130) & (ycc[..., 0] > 40)
        d['skin'] = round(float(sk.mean()), 4)
    if objects:
        d['objects'] = [o for o in objects if o['cls'] != 0 and o['score'] >= 0.45][:4]
        pers = [o for o in objects if o['cls'] == 0 and o['score'] >= 0.45]
        if pers:
            d['nano_person'] = max(o['box'][3] - o['box'][1] for o in pers)
    d['_faces'], d['_pm'] = faces, pm
    # saliency fallback: centre-surround contrast centroid (on a 128 px wide copy)
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    sw_ = 128
    sh_ = max(2, int(round(H * sw_ / W)))
    gs = cv2.resize(g, (sw_, sh_), interpolation=cv2.INTER_AREA)
    cs = np.abs(cv2.GaussianBlur(gs, (0, 0), 1) - cv2.GaussianBlur(gs, (0, 0), 0.12 * sw_))
    wgt = np.clip(cs - np.percentile(cs, 85), 0, None)
    if wgt.sum() > 0:
        yy, xx = np.mgrid[0:sh_, 0:sw_]
        d['scx'] = round(float((xx * wgt).sum() / wgt.sum() / sw_), 3)
        d['scy'] = round(float((yy * wgt).sum() / wgt.sum() / sh_), 3)
    else:
        d['scx'], d['scy'] = 0.5, 0.5
    if faces:
        f = max(faces, key=lambda q: q['w'] * q['h'])
        d['face_h'] = round(f['h'] / H, 4)
        d['fcx'] = round((f['x'] + f['w'] / 2) / W, 3)
        d['fcy'] = round((f['y'] + f['h'] / 2) / H, 3)
    # type + scale
    if d['face_h'] >= 0.05:
        t = 'face'
        fh = d['face_h']
        sc = 'ECU' if fh >= 0.45 else 'CU' if fh >= 0.25 else 'MCU' if fh >= 0.13 else 'MS' if fh >= 0.07 else 'WS'
    elif cov >= 0.04:
        ph = pbox[3] - pbox[1]
        touches = pbox[3] > 0.97 or pbox[0] < 0.03 or pbox[2] > 0.97
        body = d.get('nano_person', 0) > 0.5
        if cov >= 0.5 and not body:
            t, sc = 'person', 'ECU'                     # skin / body part filling the frame, no detectable face
        elif touches and not body and (ph < 0.9 or cov < 0.25):
            t, sc = 'hands', 'CU'
        else:
            t = 'person'
            sc = 'MS' if ph >= 0.9 else 'FS' if ph >= 0.5 else 'WS'
    elif d['objects']:
        t, sc = 'object', 'CU'
    else:
        top = g[:H // 3]
        bot = g[2 * H // 3:]
        e_top = float(np.abs(cv2.Laplacian(top, cv2.CV_32F)).mean())
        e_bot = float(np.abs(cv2.Laplacian(bot, cv2.CV_32F)).mean())
        land = top.mean() > bot.mean() + 10 and e_top < 0.5 * e_bot
        t, sc = ('landscape', 'WS') if land else ('texture', 'CU')
    d['type'], d['scale'] = t, sc
    d['conf'] = 1.0 if t == 'face' else (1.0 if (t == 'person' and d.get('nano_person', 0) > 0.5) else
                                          0.7 if t == 'object' else 0.4 if t in ('person', 'hands') else 0.3)
    d['cx'] = d.get('fcx', d.get('pcx', d['scx'])) if t in ('face', 'person', 'hands') else d['scx']
    d['cy'] = d.get('fcy', d.get('pcy', d['scy'])) if t in ('face', 'person', 'hands') else d['scy']
    return d


# =============================================================================================== window descriptors
def _hog(win):
    gx = cv2.Sobel(win, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(win, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)
    b = np.minimum((np.degrees(np.arctan2(gy, gx)) % 180.0 / 20.0).astype(np.int64), 8)
    H, W = win.shape
    cy, cx = H // HOG_CELL, W // HOG_CELL
    b = b[:cy * HOG_CELL, :cx * HOG_CELL]
    mag = mag[:cy * HOG_CELL, :cx * HOG_CELL]
    ci = (np.arange(cy * HOG_CELL) // HOG_CELL)[:, None] * cx + (np.arange(cx * HOG_CELL) // HOG_CELL)[None, :]
    v = np.bincount((ci * 9 + b).ravel(), mag.ravel(), cy * cx * 9).astype(np.float32)
    v = np.sqrt(v)
    return v / (np.linalg.norm(v) + 1e-6)


def _layout(win):
    s = cv2.resize(win, (3, 5), interpolation=cv2.INTER_AREA).astype(np.float32).ravel()
    sd = s.std()
    return (s - s.mean()) / sd if sd > 1.0 else np.zeros_like(s)


def _win_bounds(W, H, cx):
    ww = min(W, H * 9.0 / 16.0)
    x0 = float(np.clip(cx * W - ww / 2, 0, W - ww))
    return int(round(x0)), int(round(x0 + ww))


def _win_desc(g, cx):
    x0, x1 = _win_bounds(g.shape[1], g.shape[0], cx)
    win = cv2.resize(g[:, x0:max(x1, x0 + 2)], WIN_SZ, interpolation=cv2.INTER_AREA)
    return _hog(win), _layout(win)


def _win_positions(W, H, n=5):
    ww = H * 9.0 / 16.0
    if ww >= W * 0.98:
        return [0.5] * n
    lo, hi = ww / 2 / W, 1 - ww / 2 / W
    return [float(v) for v in np.linspace(lo, hi, n)]


def _tone(g):
    return (np.percentile(g[::2, ::2], [5, 25, 50, 75, 95]) / 255.0).astype(np.float32)


def _colhist(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[::2, ::2].reshape(-1, 3).astype(np.int32)
    col = (hsv[:, 1] >= 51) & (hsv[:, 2] >= 38)
    h = np.zeros(17, np.float32)
    if col.any():
        hb = np.minimum(hsv[col, 0] * 8 // 180, 7)
        sb = (hsv[col, 1] >= 128).astype(np.int32)
        h[:16] = np.bincount(hb * 2 + sb, minlength=16)[:16]
    h[16] = (~col).sum()
    return h / max(1.0, h.sum())


def _grade_target(rgb_list):
    """Luma quantiles, saturation and cast of graded-space frames (float 0..1 RGB)."""
    x = np.concatenate([f.reshape(-1, 3)[::3] for f in rgb_list]).astype(np.float32)
    L = _luma01(x)
    q = np.percentile(L, [2, 10, 25, 50, 75, 90, 98])
    mx, mn = x.max(1), x.min(1)
    ok = mx > 0.08
    sat = float(((mx - mn) / np.maximum(mx, 1e-3))[ok].mean()) if ok.any() else 0.0
    m = x[ok].mean(0) if ok.any() else np.array([0.5, 0.5, 0.5])
    cast = [float((m[0] - m[1]) / (m.mean() + 1e-3)), float((m[2] - m[1]) / (m.mean() + 1e-3))]
    return dict(q=[round(float(v), 4) for v in q], sat=round(sat, 4), cast=[round(c, 4) for c in cast])


# =============================================================================================== text candidates
def _text_words(rgb):
    """Text-like components of one frame grouped into words -> (words, mask uint8 0/1 of accepted glyphs)."""
    H, W = rgb.shape[:2]
    r_, g_, b_ = cv2.split(rgb)
    mx = cv2.max(cv2.max(r_, g_), b_)
    mn = cv2.min(cv2.min(r_, g_), b_)
    spread = cv2.subtract(mx, mn)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    grey = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    k = max(9, int(0.036 * H) | 1)
    tophat = cv2.morphologyEx(grey, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_RECT, (k, k)))
    white = (((mn >= 222) & (spread <= 26)) | ((tophat >= 32) & (mn >= 150) & (spread <= 60))).astype(np.uint8)
    s_med = float(np.median(hsv[::4, ::4, 1]))
    bwpic = s_med < 18
    color = ((hsv[..., 1] >= (45 if bwpic else 125)) & (hsv[..., 2] >= 70)).astype(np.uint8)
    hmin = max(7, int(0.012 * H))
    comps = []
    mask = np.zeros((H, W), np.uint8)
    k3 = np.ones((3, 3), np.uint8)
    for cls, m in (('white', white), ('color', color)):
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        keep = []
        for i in range(1, n):
            x, y, w, h, a = (int(v) for v in st[i])
            if h < hmin or h > 0.86 * H or w < 2 or w > 0.75 * W or a < 16:
                continue
            fill = a / float(w * h)
            if fill < 0.10 or w > 3.2 * h:
                continue
            x0, y0, x1, y1 = max(0, x - 3), max(0, y - 3), min(W, x + w + 3), min(H, y + h + 3)
            cm = (lab[y0:y1, x0:x1] == i).astype(np.uint8)
            sw = 2.0 * float(cv2.distanceTransform(cm, cv2.DIST_L2, 3).max())
            if sw / h > 0.42 or sw < 1.5:
                continue
            if fill > 0.88 and h < 2.4 * w:          # solid blob, not a bar glyph (I, l, 1)
                continue
            ring = cv2.dilate(cm, k3, iterations=2) & (1 - cm)
            if ring.sum() < 4:
                continue
            sub = rgb[y0:y1, x0:x1].reshape(-1, 3).astype(np.float32)
            ins, out_ = cm.reshape(-1) > 0, ring.reshape(-1) > 0
            cin = sub[ins].mean(0)
            cout = sub[out_].mean(0)
            if cls == 'white':
                g = grey[y0:y1, x0:x1].reshape(-1).astype(np.float32)
                con = float(g[ins].mean() - g[out_].mean())
                if con < (14 if cin.min() >= 225 else 40):
                    continue
            else:
                con = float(np.linalg.norm(cin - cout))
                ssub = hsv[y0:y1, x0:x1, 1].reshape(-1).astype(np.float32)
                if bwpic:
                    con = max(con, float(ssub[ins].mean() - ssub[out_].mean()))
                if con < (40 if bwpic else 70):
                    continue
            ssat = float(hsv[y0:y1, x0:x1, 1].reshape(-1)[ins].mean())
            comps.append(dict(cls=cls, x0=x, y0=y, x1=x + w, y1=y + h, h=h, sw=sw, rgb=cin, con=con, fill=fill, s=ssat))
            keep.append(i)
        if keep:
            km = np.zeros(n, np.uint8)
            km[keep] = 1
            mask |= km[lab]
    comps.sort(key=lambda c: (c['cls'], c['x0']))
    parent = list(range(len(comps)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i, a in enumerate(comps):
        for j in range(i + 1, len(comps)):
            b = comps[j]
            if b['cls'] != a['cls']:
                break
            if b['x0'] - a['x1'] > 1.2 * max(a['h'], b['h']):
                continue
            ov = min(a['y1'], b['y1']) - max(a['y0'], b['y0'])
            hm = max(a['h'], b['h'])
            gap = max(b['x0'] - a['x1'], a['x0'] - b['x1'])
            if ov >= 0.55 * min(a['h'], b['h']) and 0.55 < a['h'] / b['h'] < 1.8 and abs(a['y1'] - b['y1']) <= 0.3 * hm \
                    and gap <= 0.30 * hm:
                parent[find(j)] = find(i)
    groups = {}
    for i in range(len(comps)):
        groups.setdefault(find(i), []).append(comps[i])
    words = []
    multi = [g for g in groups.values() if len(g) >= 2]
    for g in groups.values():
        hs = np.array([c['h'] for c in g], float)
        hmed = float(np.median(hs))
        if len(g) == 1:
            c = g[0]
            pure = (c['cls'] == 'white' and c['rgb'].min() > 205) or \
                   (c['cls'] == 'color' and ((c['rgb'].max() - c['rgb'].min()) > 120 or (bwpic and c['s'] >= 60)))
            asp = (c['x1'] - c['x0']) / c['h']
            if c['cls'] == 'white':
                # a lone white glyph is kept only next to a word on the same line (a one-letter word, an apostrophe part)
                line = any(abs(np.median([q['y1'] for q in o]) - c['y1']) <= 0.3 * c['h'] and
                           abs(np.median([q['h'] for q in o]) - c['h']) <= 0.3 * c['h'] and
                           min(abs(c['x0'] - max(q['x1'] for q in o)), abs(min(q['x0'] for q in o) - c['x1'])) <= 2.0 * c['h']
                           for o in multi if o[0]['cls'] == 'white')
                if not (line and c['rgb'].min() > 205 and 0.07 <= c['sw'] / c['h'] <= 0.4):
                    continue
            elif not (pure and c['h'] >= 0.05 * H and 0.07 <= c['sw'] / c['h'] <= 0.36 and c['con'] > 40 and asp >= 0.28):
                continue
        elif np.median(np.abs(hs - hmed)) > 0.25 * hmed or \
                np.median([(c['x1'] - c['x0']) / c['h'] for c in g]) < 0.25:
            continue
        x0 = min(c['x0'] for c in g); y0 = min(c['y0'] for c in g)
        x1 = max(c['x1'] for c in g); y1 = max(c['y1'] for c in g)
        if x0 <= 1 or y0 <= 1 or x1 >= W - 1 or y1 >= H - 1:
            continue
        words.append(dict(cls=g[0]['cls'], box=[x0, y0, x1, y1], h=hmed, n=len(g), bwpic=bwpic,
                          base=float(np.median([c['y1'] for c in g])), sw=float(np.median([c['sw'] for c in g])),
                          aspect=float(np.median([(c['x1'] - c['x0']) / c['h'] for c in g]))))
    return words, mask


def _subtitle_line(band):
    """Burned-in subtitle line in a bottom band (pass it upscaled so glyphs are >= 6 px): thin strokes brighter or
    yellower than their surroundings (top-hat on luma / on (R+G)/2-B), aligned on one baseline, centred, >= 7 % of
    the width. Returns the line width as a fraction of the band width (0 = none)."""
    H, W = band.shape[:2]
    rgb = band.astype(np.int16)
    ker = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    th = cv2.morphologyEx(cv2.cvtColor(band, cv2.COLOR_RGB2GRAY), cv2.MORPH_TOPHAT, ker)
    yel = np.clip((rgb[..., 0] + rgb[..., 1]) // 2 - rgb[..., 2], 0, 255).astype(np.uint8)
    thy = cv2.morphologyEx(yel, cv2.MORPH_TOPHAT, ker)
    hsv = cv2.cvtColor(band, cv2.COLOR_RGB2HSV)
    best = 0.0
    for cand in ((th >= 22) & (hsv[..., 2] >= 150) & (hsv[..., 1] < 70), (thy >= 25) & (yel >= 45) & (hsv[..., 2] >= 90)):
        n, _, st, cen = cv2.connectedComponentsWithStats(cand.astype(np.uint8), connectivity=8)
        comps = sorted([(st[i], cen[i]) for i in range(1, n) if 6 <= st[i][3] <= 26 and st[i][4] >= 10
                        and 0.18 <= st[i][4] / float(st[i][2] * st[i][3]) <= 0.8], key=lambda c: c[0][0])
        for i, (sa, ca) in enumerate(comps):
            line = [sa]
            for sb, cb in comps[i + 1:]:
                if abs(cb[1] - ca[1]) <= 0.35 * sa[3] + 2 and sb[0] - (line[-1][0] + line[-1][2]) <= 2.0 * sa[3] \
                        and 0.5 <= sb[3] / sa[3] <= 2.0:
                    line.append(sb)
            x0, x1 = line[0][0], max(q[0] + q[2] for q in line)
            if len(line) >= 2 and x1 - x0 >= 0.07 * W and sum(q[2] for q in line) >= 0.3 * (x1 - x0) \
                    and 0.25 <= (x0 + x1) / 2 / W <= 0.75:
                best = max(best, (x1 - x0) / W)
    return best


def _track_words(words_per_frame, mask_at=None, max_gap=2):
    """Link per-frame words into tracks (same place, same colour class, same glyph shape)."""
    tracks, active = [], []
    cache = {}

    def mk(f):
        if f not in cache:
            if len(cache) > 6:
                cache.pop(min(cache))
            cache[f] = mask_at(f)
        return cache[f]
    for f, words in enumerate(words_per_frame):
        used = set()
        for tr in active:
            best, bi = 0.0, None
            for wi, w in enumerate(words):
                if wi in used or w['cls'] != tr['cls']:
                    continue
                v = _iou(tr['box'], w['box'])
                if v > best:
                    best, bi = v, wi
            if bi is not None and best >= 0.5 and mask_at is not None:
                ub = [min(tr['box'][0], words[bi]['box'][0]), min(tr['box'][1], words[bi]['box'][1]),
                      max(tr['box'][2], words[bi]['box'][2]), max(tr['box'][3], words[bi]['box'][3])]
                m1 = mk(tr['last'])[ub[1]:ub[3], ub[0]:ub[2]] > 0
                m2 = mk(f)[ub[1]:ub[3], ub[0]:ub[2]] > 0
                if (m1 & m2).sum() < 0.5 * max(1, (m1 | m2).sum()):
                    bi = None                                   # other glyphs at the same place (one word replaced by another)
            if bi is not None and best >= 0.5:
                used.add(bi)
                tr['frames'].append(f)
                tr['obs'].append(words[bi])
                tr['box'] = words[bi]['box']
                tr['last'] = f
        for wi, w in enumerate(words):
            if wi not in used:
                tr = dict(cls=w['cls'], box=w['box'], frames=[f], obs=[w], last=f)
                active.append(tr)
                tracks.append(tr)
        active = [t for t in active if f - t['last'] <= max_gap]
    out = []
    for tr in tracks:
        if len(tr['frames']) < 2:
            continue
        bx = np.array([o['box'] for o in tr['obs']], float)
        med = np.median(bx, axis=0)
        out.append(dict(cls=tr['cls'], f0=tr['frames'][0], f1=tr['frames'][-1], frames=list(tr['frames']),
                        box=[int(round(v)) for v in med], jitter=float(np.median(np.abs(bx - med))), obs=tr['obs'],
                        bwpic=float(np.mean([o.get('bwpic', False) for o in tr['obs']])) >= 0.5))
    return out


class Reference:
    """Decoded reference at analysis resolution + per-frame text candidates."""

    def __init__(self, path, fps=None):
        self.path = os.path.abspath(path)
        info = V.probe(path)
        self.info = info
        self.fps = float(fps or info['fps'] or 30.0)
        self.w, self.h = info['w'], info['h']
        self.tw = min(self.w, TW_MAX)
        self.th = int(round(self.h * self.tw / self.w / 2) * 2)
        self.ah = int(round(self.h * AW / self.w / 2) * 2)
        self.gh = int(round(self.h * GW / self.w / 2) * 2)
        rgb, words, masks = [], [], []
        t = time.time()
        for fr in _decode(path, self.tw, fps=self.fps):
            wd, m = _text_words(fr)
            words.append(wd)
            masks.append(np.packbits(m, axis=None))
            rgb.append(cv2.resize(fr, (AW, self.ah), interpolation=cv2.INTER_AREA))
        self.rgb = np.stack(rgb)
        self.n = len(rgb)
        self.words = words
        self._masks = masks
        log(f'reference: {self.n} frames @ {self.fps:g} fps, {self.w}x{self.h}; text candidates in {time.time() - t:.1f}s')

    def tmask(self, f):
        return np.unpackbits(self._masks[f])[:self.tw * self.th].reshape(self.th, self.tw)


def _track_masks(ref, tracks):
    """Persistence glyph mask of every track (text res, cropped to its padded box)."""
    for tr in tracks:
        x0, y0, x1, y1 = tr['box']
        pad = int(0.15 * (y1 - y0)) + 3
        X0, Y0 = max(0, x0 - pad), max(0, y0 - pad)
        X1, Y1 = min(ref.tw, x1 + pad), min(ref.th, y1 + pad)
        fr = tr['frames']
        sel = fr if len(fr) <= 24 else [fr[int(i)] for i in np.linspace(0, len(fr) - 1, 24)]
        acc = np.zeros((Y1 - Y0, X1 - X0), np.float32)
        for f in sel:
            acc += ref.tmask(f)[Y0:Y1, X0:X1]
        inbox = np.zeros_like(acc, bool)
        inbox[max(0, y0 - 2 - Y0):y1 + 2 - Y0, max(0, x0 - 2 - X0):x1 + 2 - X0] = True
        glyph = ((acc / len(sel)) >= 0.5) & inbox
        if glyph.sum() < 10:
            glyph = ((acc / len(sel)) >= 0.25) & inbox
        tr['mbox'] = [X0, Y0, X1, Y1]
        tr['glyph'] = glyph
        ys, xs = np.nonzero(glyph)
        if len(xs):
            tr['box'] = [int(X0 + xs.min()), int(Y0 + ys.min()), int(X0 + xs.max() + 1), int(Y0 + ys.max() + 1)]
        tr['cap'] = float(np.median([o['h'] for o in tr['obs']]))
    return tracks


def _refine_tracks(ref, tracks, reach=75):
    """Second pass at text resolution: extend static tracks with their glyph template (forward/backward, through
    flashes, low contrast and inverted frames), sample glyph colours over the background for colour/blend, then merge
    simultaneous fragments of the same text."""
    cand = [t for t in tracks if t['jitter'] <= 2.5 and t['cap'] >= 0.02 * ref.th]
    k3 = np.ones((3, 3), np.uint8)
    for tr in cand:
        g8 = tr['glyph'].astype(np.uint8)
        core = cv2.erode(g8, k3) > 0
        if core.sum() < 8:
            core = tr['glyph']
        tr['_core'] = core
        gf = tr['glyph'].astype(np.float32)
        tr['_gz'] = (gf - gf.mean()) / (gf.std() + 1e-6)
        tr['st'], tr['samples'], tr['_prev'] = {}, [], None
    want = {}
    for ti, tr in enumerate(cand):
        for f in range(max(0, tr['f0'] - reach), min(ref.n, tr['f1'] + reach + 1)):
            want.setdefault(f, []).append(ti)
    det = [set(t['frames']) for t in cand]
    for f, fr in enumerate(_decode(ref.path, ref.tw, fps=ref.fps)):
        for ti in want.get(f, []):
            tr = cand[ti]
            X0, Y0, X1, Y1 = tr['mbox']
            crop = fr[Y0:Y1, X0:X1]
            core = tr['_core']
            px = crop[core].astype(np.int16)
            mx, mn = px.max(1), px.min(1)
            if tr['cls'] == 'white':
                plane = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY).astype(np.float32)
                p = float(((mn >= 200) & (mx - mn <= 45)).mean())
                pi = float(((mx <= 55) & (mx - mn <= 45)).mean())        # the same glyphs, inverted
                hh = None
            else:
                hsv_c = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
                plane = hsv_c[..., 1].astype(np.float32)
                satp = (mx >= 55) & ((mx - mn) >= 0.25 * np.maximum(mx, 1))
                p, pi = float(satp.mean()), 0.0
                hh = np.bincount((hsv_c[..., 0][core][satp].astype(np.int32) // 10) % 18, minlength=18).astype(np.float32)
            sd = float(plane.std())
            shape = float(((plane - plane.mean()) * tr['_gz']).mean() / (sd + 1e-6)) if sd > 1e-3 else 0.0
            tr['st'][f] = (p, shape, pi, sd, hh)
            if f in det[ti] and len(tr['samples']) < 12:
                gl = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY).astype(np.float32)
                bg = _fill(gl, tr['glyph'], sigma=max(2.0, 0.3 * tr['cap']))[core]
                step = max(1, len(px) // 400)
                tr['samples'].append((crop[core][::step].copy(), bg[::step].copy()))
    occ, frag = {}, {}
    for ti, tr in enumerate(cand):
        for f in tr['frames']:
            occ.setdefault(f, []).append((ti, tr))
    for ti, tr in enumerate(cand):
        st = tr['st']
        href = None
        if tr['cls'] == 'color':
            hs = sum((st[f][4] for f in tr['frames'] if f in st and st[f][4] is not None), np.zeros(18, np.float32))
            if hs.sum() > 0:
                href = int(hs.argmax())

        def state(f):
            if f not in st:
                return 'none'
            p, shape, pi, sd, hh = st[f]
            if href is not None and hh is not None and hh.sum() > 20:
                near = sum(hh[(href + d) % 18] + hh[(href + 9 + d) % 18] for d in (-1, 0, 1)) / hh.sum()
                if near < 0.6:
                    return 'none'
            if (p >= 0.5 and shape >= 0.42) if tr['cls'] == 'white' else (p >= 0.6 and shape >= 0.5):
                return 'strong'
            if tr['cls'] == 'white' and pi >= 0.5 and shape <= -0.42:
                return 'strong'                                  # inverted frame, text inverted with it
            if p >= 0.5 and sd < 12:
                return 'weak'                                    # flat (flash / white background): can't tell
            return 'none'

        def occupied(g):
            for oi, o in occ.get(g, []):
                if oi == ti or not (_inside(o['box'], tr['box']) >= 0.5 or _iou(o['box'], tr['box']) >= 0.3):
                    continue
                if (oi, ti) not in frag:
                    frag[(oi, ti)] = _glyph_overlap(o, tr) >= 0.6
                if not frag[(oi, ti)]:
                    return True                          # other glyphs at this place (one word replaced by another)
            return False

        def extend(f, step, lim):
            last = f
            g = f + step
            while 0 <= g < ref.n and abs(g - f) <= lim:
                if occupied(g):
                    break
                s_ = state(g)
                if s_ == 'strong':
                    last = g
                elif s_ == 'weak':
                    ahead = [h for h in range(g + step, g + 5 * step, step) if 0 <= h < ref.n]
                    if not any(state(h) == 'strong' for h in ahead):
                        break
                else:
                    break
                g += step
            return last
        f1 = extend(tr['f1'], 1, reach)
        f0 = extend(tr['f0'], -1, reach)
        tr['f0'], tr['f1'] = f0, f1
        for k_ in ('_prev', '_core', '_gz'):
            tr.pop(k_, None)
        tr['st'] = {}
    merged = _merge_tracks(cand)
    # line growth: a word that stays while a longer line appears around it ("ONE" -> "ONE MORE") -> the later,
    # bigger track keeps only the new part
    by_area = sorted(merged, key=lambda t: -(t['box'][2] - t['box'][0]) * (t['box'][3] - t['box'][1]))
    for b in merged:
        for a in by_area:
            if a is b or a['cls'] != b['cls'] or _inside(a['box'], b['box']) < 0.7 or not (0.7 <= a['cap'] / b['cap'] <= 1.4):
                continue
            if (a['box'][2] - a['box'][0]) >= 0.9 * (b['box'][2] - b['box'][0]):
                continue
            if min(a['frames']) < min(b['frames']) - 2 and a['f1'] >= min(b['frames']):
                cap = b['cap']
                if a['box'][0] - b['box'][0] < 0.5 * cap:
                    b['box'] = [int(a['box'][2] + 0.15 * cap), b['box'][1], b['box'][2], b['box'][3]]
                elif b['box'][2] - a['box'][2] < 0.5 * cap:
                    b['box'] = [b['box'][0], b['box'][1], int(a['box'][0] - 0.15 * cap), b['box'][3]]
                else:
                    continue
                na = float(np.median([o['n'] for o in a['obs']]))
                b['obs'] = [dict(o, n=max(1, int(round(o['n'] - na)))) for o in b['obs']]
                b['f0'] = max(b['f0'], min(b['frames']))
                break
    return _merge_tracks(merged)


def _glyph_overlap(a, b):
    """Fraction of a's glyph pixels that lie on b's glyph (text-res coordinates, 1 px tolerance)."""
    ax0, ay0, _, _ = a['mbox']
    bx0, by0, _, _ = b['mbox']
    ys, xs = np.nonzero(a['glyph'])
    if not len(xs):
        return 0.0
    gb = cv2.dilate(b['glyph'].astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    X, Y = xs + ax0 - bx0, ys + ay0 - by0
    ok = (X >= 0) & (Y >= 0) & (X < gb.shape[1]) & (Y < gb.shape[0])
    return float(gb[Y[ok], X[ok]].sum()) / len(xs)


def _merge_tracks(cand):
    """Merge tracks of the same text: same place in sequence, or a fragment seen together with a bigger word."""
    cand = sorted(cand, key=lambda t: -(t['box'][2] - t['box'][0]) * (t['box'][3] - t['box'][1]))
    merged = []
    for tr in cand:
        for m in merged:
            if m['cls'] != tr['cls'] or not (0.7 <= tr['cap'] / max(m['cap'], 1e-6) <= 1.4):
                continue
            ov = min(m['f1'], tr['f1']) - max(m['f0'], tr['f0']) + 1
            co = len(set(m['frames']) & set(tr['frames']))
            same_place = _iou(tr['box'], m['box']) >= 0.6
            together = co >= 0.5 * min(len(m['frames']), len(tr['frames'])) or \
                (abs(m['f0'] - tr['f0']) <= 2 and abs(m['f1'] - tr['f1']) <= 3)
            fragment = _inside(tr['box'], m['box']) >= 0.7 and together
            covered = _inside(tr['box'], m['box']) >= 0.7 and m['f0'] - 2 <= tr['f0'] and tr['f1'] <= m['f1'] + 2 and \
                'glyph' in tr and 'glyph' in m and _glyph_overlap(tr, m) >= 0.6
            if (same_place and ov >= -2) or fragment or covered:
                m['f0'], m['f1'] = min(m['f0'], tr['f0']), max(m['f1'], tr['f1'])
                m['frames'] = sorted(set(m['frames']) | set(tr['frames']))
                m['samples'] = m.get('samples', []) + tr.get('samples', [])[:4]
                m['obs'] = m['obs'] + tr['obs']
                break
        else:
            merged.append(tr)
    return merged


def _text_colour(tr):
    """Base colour + blend from glyph samples: difference blend = complementary hue over brighter background."""
    if not tr.get('samples'):
        return [235, 235, 235], 'normal'
    px = np.concatenate([s[0] for s in tr['samples']]).astype(np.float32)
    bg = np.concatenate([s[1] for s in tr['samples']]).astype(np.float32)
    if tr['cls'] == 'white':
        return [int(round(v)) for v in np.median(px, axis=0)], 'normal'
    hsv = cv2.cvtColor(px.reshape(-1, 1, 3).astype(np.uint8), cv2.COLOR_RGB2HSV).reshape(-1, 3).astype(np.float32)
    sat = hsv[:, 1] > 70
    if sat.sum() < 20:
        return [int(round(v)) for v in np.median(px, axis=0)], 'normal'
    hue, b = hsv[sat, 0] * 2.0, bg[sat]
    dark = b <= np.percentile(b, 40)
    ref_h = float(np.median(hue[dark]))
    d = np.abs(((hue - ref_h + 180) % 360) - 180)
    comp = d > 120
    blend = 'normal'
    if comp.mean() > (0.04 if tr.get('bwpic') else 0.08) and (d < 60).mean() > 0.10 and \
            (tr.get('bwpic') or b[comp].mean() > b[~comp].mean() + 25):
        blend = 'difference'
    base = np.median(px[sat][dark & (d < 60)] if blend == 'difference' else px[sat], axis=0)
    return [int(round(v)) for v in base], blend


def text_slots(ref, tracks, dec):
    """Overlay text events: frames, geometry (reference px + fractions), colour, blend, size, blocks."""
    slots = dec['slots']
    kind = dec['kind']
    n = ref.n
    slot_at = np.zeros(n, int)
    for s in slots:
        slot_at[s['f0']:s['f1'] + 1] = s['i']
    content = set(i for i in range(n) if kind[i] in ('content', 'inverted'))
    first_c = {s['i']: min([f for f in range(s['f0'], s['f1'] + 1) if f in content] or [s['f0']]) for s in slots}
    last_c = {s['i']: max([f for f in range(s['f0'], s['f1'] + 1) if f in content] or [s['f1']]) for s in slots}
    bw = {s['i']: s['bw'] for s in slots}
    sx = ref.w / ref.tw
    items, rejected = [], []
    for ti, tr in enumerate(tracks):
        tr['_ti'] = ti
        cap = tr['cap']
        if cap < 0.032 * ref.th or len(tr['frames']) < 3:
            continue
        s0, s1 = slot_at[tr['f0']], slot_at[tr['f1']]
        crosses = any(slots[j]['cut_in']['type'] == 'cut' for j in range(s0 + 1, s1 + 1))
        mid = tr['f0'] > first_c[s0] + 1 or tr['f1'] < last_c[s1] - 1
        sat_bw = tr['cls'] == 'color' and all(bw[j] for j in range(s0, s1 + 1))
        if not (crosses or mid or sat_bw):
            rejected.append(tr)
            continue
        colour, blend = _text_colour(tr)
        x0, y0, x1, y1 = tr['box']
        items.append(dict(src=[ti], f0=int(tr['f0']), f1=int(tr['f1']), det_frames=len(tr['frames']), det=list(tr['frames']), cls=tr['cls'],
                          box=[round(x0 * sx, 1), round(y0 * sx, 1), round(x1 * sx, 1), round(y1 * sx, 1)],
                          cap=round(cap * sx, 1), base=round(float(np.median([o['base'] for o in tr['obs']])) * sx, 1),
                          glyphs=int(round(np.median([o['n'] for o in tr['obs']]))), colour=colour, blend=blend,
                          aspect=round(float(np.median([o['aspect'] for o in tr['obs']])), 3),
                          why=[w for w, c in (('crosses_cut', crosses), ('mid_shot', mid), ('saturated_on_bw', sat_bw)) if c]))
    # block members: same style as an accepted overlay, on screen with it and next to it (a second line that lives
    # exactly as long as a regraded shot)
    added = True
    while added and rejected:
        added = False
        for tr in list(rejected):
            bx = [v * sx for v in tr['box']]
            cap = tr['cap'] * sx
            for it in items:
                if it['cls'] != tr['cls'] or not (0.8 <= cap / it['cap'] <= 1.25):
                    continue
                if min(it['f1'], tr['f1']) - max(it['f0'], tr['f0']) < 0.5 * (tr['f1'] - tr['f0'] + 1):
                    continue
                vg = max(bx[1] - it['box'][3], it['box'][1] - bx[3])
                hg = max(bx[0] - it['box'][2], it['box'][0] - bx[2])
                if vg <= 1.6 * cap and hg <= 3.0 * cap:
                    colour, blend = _text_colour(tr)
                    items.append(dict(src=[tr['_ti']], f0=int(tr['f0']), f1=int(tr['f1']), det_frames=len(tr['frames']), det=list(tr['frames']),
                                      cls=tr['cls'], box=[round(v, 1) for v in bx], cap=round(cap, 1),
                                      base=round(float(np.median([o['base'] for o in tr['obs']])) * sx, 1),
                                      glyphs=int(round(np.median([o['n'] for o in tr['obs']]))), colour=colour, blend=blend,
                                      aspect=round(float(np.median([o['aspect'] for o in tr['obs']])), 3), why=['block_member']))
                    rejected.remove(tr)
                    added = True
                    break
    # words that appear and leave together on one line -> one item ("ONE MORE", "BIG DAY")
    items.sort(key=lambda d: (d['f0'], d['box'][0]))
    merged = []
    for it in items:
        for m in merged:
            if abs(m['f0'] - it['f0']) <= 1 and abs(m['f1'] - it['f1']) <= 6 \
                    and abs(m['base'] - it['base']) <= 0.3 * m['cap'] \
                    and abs(m['cap'] - it['cap']) <= 0.3 * m['cap'] and m['cls'] == it['cls'] \
                    and -0.3 * m['cap'] <= it['box'][0] - m['box'][2] <= 1.6 * m['cap']:
                m['box'] = [min(m['box'][0], it['box'][0]), min(m['box'][1], it['box'][1]),
                            max(m['box'][2], it['box'][2]), max(m['box'][3], it['box'][3])]
                m['glyphs'] += it['glyphs'] + (1 if it['box'][0] - m['box'][2] > 0.25 * m['cap'] else 0)
                m['words'] += 1
                m['det'] = sorted(set(m['det']) | set(it['det']))
                m['src'] = m['src'] + it['src']
                if it['blend'] == 'difference':
                    m['blend'], m['colour'] = 'difference', it['colour'] if m['blend'] != 'difference' else m['colour']
                m['f0'], m['f1'] = min(m['f0'], it['f0']), max(m['f1'], it['f1'])
                break
        else:
            merged.append(dict(it, words=1))
    merged.sort(key=lambda d: (d['f0'], d['box'][1]))
    par = list(range(len(merged)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    for i, a in enumerate(merged):
        for j in range(i + 1, len(merged)):
            b = merged[j]
            if min(a['f1'], b['f1']) < max(a['f0'], b['f0']):
                continue
            cap = max(a['cap'], b['cap'])
            vg = max(b['box'][1] - a['box'][3], a['box'][1] - b['box'][3])
            hg = max(b['box'][0] - a['box'][2], a['box'][0] - b['box'][2])
            if vg <= 1.6 * cap and hg <= 3.0 * cap:
                par[find(j)] = find(i)
    roots = {}
    for i, it in enumerate(merged):
        it['block'] = roots.setdefault(find(i), len(roots))
        it['id'] = f'T{i + 1:02d}'
        it['box_n'] = [round(it['box'][0] / ref.w, 4), round(it['box'][1] / ref.h, 4),
                       round(it['box'][2] / ref.w, 4), round(it['box'][3] / ref.h, 4)]
        it['text'] = 'X' * max(1, it['glyphs'])
    return merged


# =============================================================================================== decomposition
def _white_fit(g, r):
    d = 255.0 - r
    a = float(np.clip(((g - r) * d).sum() / ((d * d).sum() + 1e-6), 0, 1))
    return a, float(np.abs(g - (r + a * d)).mean())


def _black_fit(g, r):
    a = float(np.clip(1.0 - (g * r).sum() / ((r * r).sum() + 1e-6), 0, 1))
    return a, float(np.abs(g - (1 - a) * r).mean())


def _static_text_masks(ref, tracks, width, height):
    """Per frame: dilated union of glyph masks of static tracks, at (width, height) (bool) or None."""
    out = [None] * ref.n
    for tr in tracks:
        X0, Y0, X1, Y1 = tr['mbox']
        g = tr['glyph'].astype(np.uint8)
        k = max(3, int(round(0.3 * (tr['box'][3] - tr['box'][1]))) | 1)
        full = np.zeros((ref.th, ref.tw), np.uint8)
        full[Y0:Y1, X0:X1] = cv2.dilate(g, np.ones((k, k), np.uint8))
        small = cv2.resize(full, (width, height), interpolation=cv2.INTER_AREA) > 0
        for f in range(tr['f0'], tr['f1'] + 1):
            out[f] = small if out[f] is None else (out[f] | small)
    return out


def decompose(ref, tracks):
    """Classify every frame and every boundary; build slots and frame ops."""
    n = ref.n
    G = np.stack([cv2.cvtColor(cv2.resize(ref.rgb[i], (GW, ref.gh), interpolation=cv2.INTER_AREA),
                               cv2.COLOR_RGB2GRAY).astype(np.float32) for i in range(n)])
    L = G.reshape(n, -1).mean(1)
    SD = G.reshape(n, -1).std(1)
    P = np.percentile(G.reshape(n, -1)[:, ::3], [2, 5, 50, 90, 95, 98], axis=1).T
    SAT = np.array([float(cv2.cvtColor(ref.rgb[i], cv2.COLOR_RGB2HSV)[..., 1].mean()) for i in range(n)])
    tm = _static_text_masks(ref, tracks, GW, ref.gh)
    Gf = [(_fill(G[i], tm[i]) if tm[i] is not None else G[i]) for i in range(n)]
    HP = [_hp(g) for g in Gf]
    TINY = [cv2.resize(g, (32, 18), interpolation=cv2.INTER_AREA) for g in Gf]
    RGBs = [cv2.resize(ref.rgb[i], (GW, ref.gh), interpolation=cv2.INTER_AREA) for i in range(n)]
    HS = [_hist_hsv(_fill(RGBs[i], tm[i]) if tm[i] is not None else RGBs[i]) for i in range(n)]
    HL = [_hist_luma(g) for g in Gf]
    Q = [np.percentile(g[::2, ::2], [5, 25, 50, 75, 95]) for g in Gf]
    STK = [_streak(g) for g in Gf]
    kind = ['content'] * n
    info = [dict() for _ in range(n)]
    # ---- white / black frames (opacity from the nearest content neighbour)
    for i in range(n):
        if (L[i] >= 232 and SD[i] <= 14) or P[i, 1] >= 228:
            kind[i] = 'white'
        elif P[i, 3] <= 18 and L[i] <= 14:
            kind[i] = 'black'

    def neighbour(i, step):
        j = i + step
        while 0 <= j < n and kind[j] != 'content':
            j += step
        return j if 0 <= j < n else None
    for i in range(n):
        if kind[i] == 'white':
            a = 1.0
            if SD[i] >= 4:
                j = neighbour(i, -1)
                j = j if j is not None else neighbour(i, 1)
                if j is not None:
                    a = _white_fit(G[i], G[j])[0]
            info[i]['a'] = round(max(a, 0.5), 2)
        elif kind[i] == 'black':
            info[i]['a'] = 1.0
    for i in range(n):        # semi-transparent white / black frames over a visible neighbour
        if kind[i] != 'content' or not (L[i] > 170 or L[i] < 40):
            continue
        for j in (i - 1, i + 1):
            if not (0 <= j < n) or kind[j] != 'content':
                continue
            if L[i] > 170 and L[i] - L[j] > 60:
                a, e = _white_fit(G[i], G[j])
                if a >= 0.55 and e < 10 and _ncc(HP[i], HP[j]) > 0.5:
                    kind[i], info[i] = 'white', dict(a=round(a, 2))
                    break
            if L[i] < 40 and L[j] - L[i] > 30:
                a, e = _black_fit(G[i], G[j])
                if a >= 0.6 and e < 8 and _ncc(HP[i], HP[j]) > 0.5:
                    kind[i], info[i] = 'black', dict(a=round(a, 2))
                    break
    # ---- partial flashes: a region blends towards white (opacity >= .35) against the last normal frame while the
    # rest stays, for <= 3 frames, and the next normal frame looks like the one before
    last, cand = None, {}
    for i in range(n):
        if kind[i] != 'content':
            continue
        if last is not None and i - last <= 4:
            r = G[last]
            d = G[i] - r
            ap = d / np.maximum(255.0 - r, 8.0)
            R = ((d > 30) & (ap > 0.35)).astype(np.uint8)
            if tm[i] is not None:
                R[tm[i]] = 0
            R = cv2.morphologyEx(R, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            fr = float(R.mean())
            if 0.0015 < fr < 0.65:
                Rd = cv2.dilate(R, np.ones((7, 7), np.uint8)) > 0
                rest = np.abs(d)[~Rd]
                sat_r = float(cv2.cvtColor(RGBs[i], cv2.COLOR_RGB2HSV)[..., 1][R > 0].mean())
                if rest.size and float(rest.mean()) < 7.0 and sat_r < 50:
                    cand[i] = (last, R, fr, float(np.clip(np.median(ap[R > 0]), 0, 1)))
                    continue
        last = i
    for a, b in _runs(cand):
        fr_run = list(range(a, b + 1))
        base = cand[fr_run[0]][0]
        j = b + 1
        while j < n and kind[j] != 'content':
            j += 1
        Ru = np.zeros_like(cand[fr_run[0]][1])
        for f in fr_run:
            Ru |= cand[f][1]
        back = j < n and float(np.abs(G[j] - G[base])[Ru > 0].mean()) < 25 and _ncc(HP[j], HP[base]) > 0.6
        if len(fr_run) > 3 or not back:
            continue
        for f in fr_run:
            _, R, fr, ap = cand[f]
            ys, xs = np.nonzero(R)
            kind[f] = 'pflash'
            info[f] = dict(area=round(fr, 4), a=round(ap, 2), base=int(base),
                           box=[round(xs.min() / GW, 3), round(ys.min() / ref.gh, 3), round((xs.max() + 1) / GW, 3),
                                round((ys.max() + 1) / ref.gh, 3)])
    # ---- A/B flicker zones: frames alternate between two looks of the same picture
    alt = []
    for i in range(1, n - 1):
        if kind[i - 1] == kind[i] == kind[i + 1] == 'content':
            if _bhatt(HS[i - 1], HS[i]) > 0.15 and _bhatt(HS[i], HS[i + 1]) > 0.15 and _bhatt(HS[i - 1], HS[i + 1]) < 0.12 \
                    and _ncc(HP[i - 1], HP[i + 1]) > 0.9 and _ncc(HP[i - 1], HP[i]) > 0.5:
                alt.append(i)
    zones = []
    for a, b in _runs(alt):
        if zones and a - zones[-1][1] <= 3:
            zones[-1][1] = b
        else:
            zones.append([a, b])
    flicker = []
    for a, b in zones:
        z0, z1 = a - 1, b + 1
        A, B = z0, a
        bfr = []
        for f in range(z0, n):
            if kind[f] != 'content':
                break
            dA, dB = _bhatt(HS[f], HS[A]), _bhatt(HS[f], HS[B])
            if f > z1 and dB > dA:
                break
            if dB < dA:
                bfr.append(f)
        inserts = [f for f in bfr if f <= z1 and f + 1 <= z1 and (f + 1) not in bfr]
        diff = np.abs(Gf[B] - Gf[A])
        R = cv2.GaussianBlur(diff, (0, 0), 2) > 10
        ys, xs = np.nonzero(R)
        box = [round(xs.min() / GW, 3), round(ys.min() / ref.gh, 3), round((xs.max() + 1) / GW, 3),
               round((ys.max() + 1) / ref.gh, 3)] if len(xs) else None
        for f in inserts:
            kind[f] = 'insert'
            info[f] = dict(box=box)
        flicker.append(dict(frames=bfr, inserts=inserts, box=box))
    # ---- boundaries between consecutive content frames
    seq = [i for i in range(n) if kind[i] == 'content']
    pol, bnd, pair = {}, {}, {}
    logsc = {}
    for k, b in enumerate(seq):
        if k == 0:
            pol[b] = 1
            continue
        a = seq[k - 1]
        s_t = _ncc(TINY[a], TINY[b])
        s_hp = _ncc(HP[a], HP[b])
        dh = _bhatt(HS[a], HS[b])
        dl = _bhatt(HL[a], HL[b])
        dq = float(np.abs(Q[a] - Q[b]).mean() / 255.0)
        rec = dict(tiny=round(s_t, 3), hp=round(s_hp, 3), dh=round(dh, 3), dl=round(dl, 3), dq=round(dq, 3),
                   dL=round(float(L[b] - L[a]), 1), gap=b - a)
        if s_hp <= -0.45 and s_t <= -0.4:                       # same picture, negative
            pol[b] = -pol[a]
            rec['type'] = 'invert'
            pair[b] = rec
            continue
        al, meth, inl, sc = None, 'none', 0.0, 1.0
        if s_hp < 0.6:
            est = M.estimate_pair(Gf[a].astype(np.uint8), Gf[b].astype(np.uint8), np.full(Gf[a].shape, 255, np.uint8))
            meth, inl = est['method'], est['inl']
            if est['M'] is not None:
                wa = cv2.warpAffine(Gf[a], est['M'].astype(np.float32), (Gf[a].shape[1], Gf[a].shape[0]),
                                    flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                al = _ncc(_hp(wa), HP[b])
                sc = M.similarity_from_affine(est['M'])[0]
        rec.update(al=None if al is None else round(al, 3), meth=meth, inl=round(inl, 2), sc=round(sc, 3))
        appear = max(dh, 4.0 * dq)
        lk = meth == 'lk' and al is not None and inl >= 0.3
        S = max(s_hp, al if lk else -1.0, 0.8 * al if (al is not None and meth == 'ecc' and al >= 0.55) else -1.0)
        ca, cb = STK[a], STK[b]
        streaky = ca[0] >= 0.65 and cb[0] >= 0.65 and ca[2] <= 0.3 and cb[2] <= 0.3 and \
            min(abs(ca[1] - cb[1]), 180 - abs(ca[1] - cb[1])) <= 25
        if s_hp >= 0.6 or (lk and al >= 0.6 and inl >= 0.5):
            typ = 'regrade' if appear >= 0.4 else None
            if typ is None and lk and abs(math.log(max(sc, 1e-3))) >= 0.07:
                typ = 'punch?'
        elif lk and al >= 0.45 and abs(math.log(max(sc, 1e-3))) >= 0.07:
            typ = 'punch?'
        elif (S >= 0.35 and appear < 0.35) or (S >= 0.25 and appear < 0.2):
            typ = None
        elif streaky and dh < 0.75:
            typ = None
        else:
            typ = 'cut'
        if lk:
            logsc[b] = math.log(max(sc, 1e-3))
        rec['type'] = typ or 'same'
        rec['streak'] = [round(ca[0], 2), round(cb[0], 2)]
        pair[b] = rec
        if typ:
            bnd[b] = dict(type=typ, **{k2: v for k2, v in rec.items() if k2 != 'type'})
        pol[b] = 1 if typ in ('cut', 'regrade') else pol[a]
    # punches must be isolated scale jumps (continuous zooms are moves), or jumps across a flash frame
    seq_idx = {f: i for i, f in enumerate(seq)}
    for b in [b for b, v in bnd.items() if v['type'] == 'punch?']:
        k = seq_idx[b]
        neigh = []
        for step in (-1, 1):                     # nearest moving (non-duplicate) pair on each side, same shot
            kk = k + step
            while 0 < kk < len(seq) and abs(kk - k) <= 4:
                pr = pair.get(seq[kk], {})
                if pr.get('type') in ('cut', 'regrade'):
                    break
                if seq[kk] in logsc and pr.get('dq', 1) > 0.002:
                    neigh.append(abs(logsc[seq[kk]]))
                    break
                kk += step
        across_flash = bnd[b]['gap'] > 1 and abs(logsc.get(b, 0)) >= 0.15
        if across_flash or not neigh or max(neigh) < 0.035:
            bnd[b]['type'] = 'punch'
        else:
            bnd.pop(b)
    # a regrade that reverts within two frames is a flicker, not a boundary
    for b in [b for b, v in bnd.items() if v['type'] == 'regrade']:
        k = seq_idx[b]
        a = seq[k - 1]
        later = [f for f in seq[k + 1:k + 3]]
        if later and any(_bhatt(HS[f], HS[a]) < 0.12 for f in later):
            bnd.pop(b)
    # weak isolated boundaries: a 1-2 frame slot joined to the neighbour it is separated from by a boundary with
    # almost no colour/luma change (fast move / blur frames, not a shot)
    def weak(b):
        return b in bnd and bnd[b]['type'] == 'cut' and bnd[b]['dh'] < 0.15 and bnd[b]['dq'] < 0.05
    for b in sorted(bnd):
        if b not in bnd:
            continue
        nb = [x for x in sorted(bnd) if x > b]
        end = nb[0] if nb else n
        span = [f for f in seq if b <= f < end]
        if len(span) > 2:
            continue
        if weak(b):                                          # join the previous slot
            pa = pol[seq[seq_idx[b] - 1]]
            for f in span:
                pol[f] = pol[f] * pa
            bnd.pop(b)
        elif nb and weak(end):                               # join the next slot
            pb = pol[span[-1]]
            nxt = [x for x in sorted(bnd) if x > end]
            for f in [f for f in seq if end <= f < (nxt[0] if nxt else n)]:
                pol[f] = pol[f] * pb
            bnd.pop(end)
    # ---- slots
    starts = [0] + sorted(bnd)
    slot_at = np.zeros(n, int)
    slots = []
    for j, st in enumerate(starts):
        en = (starts[j + 1] - 1) if j + 1 < len(starts) else n - 1
        slot_at[st:en + 1] = j
        slots.append(dict(i=j, f0=st, f1=en, cut_in=bnd.get(st, dict(type='start'))))
    # ---- polarity per slot
    for s in slots:
        fr = [f for f in range(s['f0'], s['f1'] + 1) if kind[f] == 'content' and f in pol]
        pos = [f for f in fr if pol[f] > 0]
        neg = [f for f in fr if pol[f] < 0]
        inv = []
        if pos and neg:
            if max(len(pos), len(neg)) >= 3 * min(len(pos), len(neg)):
                inv = pos if len(pos) < len(neg) else neg
            else:
                inv = pos if np.mean([L[f] for f in pos]) > np.mean([L[f] for f in neg]) else neg
        for f in inv:
            kind[f] = 'inverted'
        s['inverted'] = sorted(inv)
        cf = [f for f in range(s['f0'], s['f1'] + 1) if kind[f] in ('content', 'inverted')]
        s['content'] = cf
        s['bw'] = bool(float(np.median([SAT[f] for f in cf] or [0])) < 14)
        s['flicker'] = [z for z in flicker if s['f0'] <= z['frames'][0] <= s['f1']] if flicker else []
    # ---- frame ops (white stage decided later, once text is known)
    frames = []
    for i in range(n):
        d = dict(f=i, kind=kind[i], L=round(float(L[i]), 1), sd=round(float(SD[i]), 1), sat=round(float(SAT[i]), 1),
                 slot=int(slot_at[i]))
        d.update(info[i])
        if i in pair:
            d['pair'] = pair[i]
        frames.append(d)
    return dict(frames=frames, slots=slots, kind=kind, info=info, G=G, Gf=Gf, L=L, SD=SD, SAT=SAT, HS=HS, HP=HP,
                tm=tm, STK=STK, slot_at=slot_at)


def frame_ops(dec, texts):
    """Frame-exact ops from the frame classes (white stage: pre if text is visible on the flash, else post)."""
    n = len(dec['kind'])
    on = np.zeros(n, bool)
    seen = np.zeros(n, bool)
    for t in texts:
        on[t['f0']:t['f1'] + 1] = True
        seen[[f for f in t.get('det', []) if 0 <= f < n]] = True
    ops = []
    kind, info = dec['kind'], dec['info']
    for i in range(n):
        k = kind[i]
        if k == 'white':
            near = (i > 0 and on[i - 1]) or (i + 1 < n and on[i + 1])
            stage = 'pre' if seen[i] else ('post' if (on[i] or near) else 'pre')   # text visible on the flash -> pre
            ops.append(dict(f=[i], op='white', a=info[i].get('a', 1.0), stage=stage))
        elif k == 'black':
            ops.append(dict(f=[i], op='black', a=info[i].get('a', 1.0)))
        elif k == 'inverted':
            ops.append(dict(f=[i], op='invert'))
        elif k == 'pflash':
            ops.append(dict(f=[i], op='pflash', a=info[i]['a'], box=info[i]['box'], area=info[i]['area'], base=info[i]['base']))
    # merge consecutive invert frames of one slot into one op
    out, inv = [], []
    for o in ops:
        if o['op'] == 'invert':
            inv.append(o['f'][0])
        else:
            out.append(o)
    by_slot = {}
    for f in inv:
        by_slot.setdefault(int(dec['slot_at'][f]), []).append(f)
    for fs in by_slot.values():
        out.append(dict(f=fs, op='invert'))
    out.sort(key=lambda o: o['f'][0])
    return out


# =============================================================================================== slot descriptors
def _pair_motion(ga, gb, mask=None):
    """Motion a -> b of two grey float frames with model selection -> dict(model 'dup' | 'sim' | 'shift' | 'none', s,
    rot (deg), tx, ty (px: translation of the frame centre), err (residual after the model), d0 (mean abs difference),
    inl (LK inlier share), resp (phase-correlation response)). A similarity (zoom / roll) from LK or ECC must explain
    the pair clearly better than the plain phase-correlation shift and stay plausible per frame - LK with >= 45 %
    inliers: <= 20 deg, x1.57; weaker LK or ECC (a 6-DOF affine, which invents rotation and scale on one-directional
    structure such as stripes: the aperture problem): <= 3 deg, 12 % - else the shift is used; 'none' = nothing
    explains the pair (a cut, heavy blur)."""
    H, W = ga.shape
    d0 = float(np.abs(ga - gb).mean())
    out = dict(model='dup', s=1.0, rot=0.0, tx=0.0, ty=0.0, err=0.0, d0=d0, inl=0.0, resp=1.0)
    if d0 < 0.6:
        return out
    if mask is None:
        mask = np.full((H, W), 255, np.uint8)
    est = M.estimate_pair(np.clip(ga, 0, 255).astype(np.uint8), np.clip(gb, 0, 255).astype(np.uint8), mask)
    sx, sy, resp = _phase_shift(ga, gb)
    wt = cv2.warpAffine(ga, np.float32([[1, 0, sx], [0, 1, sy]]), (W, H), flags=cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_REFLECT)
    e_t = float(np.abs(wt - gb).mean())
    out.update(inl=float(est.get('inl') or 0.0), resp=resp)
    if est['M'] is not None and (est['method'] == 'lk' or d0 <= 25):
        Mx = est['M']
        wa = cv2.warpAffine(ga, Mx.astype(np.float32), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        e_s = float(np.abs(wa - gb).mean())
        s, rot = M.similarity_from_affine(Mx)
        strong = est['method'] == 'lk' and out['inl'] >= 0.45
        ls = abs(math.log(max(s, 1e-3)))
        plausible = (abs(rot) <= 20.0 and ls <= 0.45) if strong else (abs(rot) <= 3.0 and ls <= 0.12)
        margin = 0.97 if est['method'] == 'lk' else 0.8
        if plausible and e_s < margin * e_t - 0.1:
            c = np.array([(W - 1) / 2.0, (H - 1) / 2.0])
            tc = Mx[:, 2] + Mx[:, :2] @ c - c
            out.update(model='sim', s=float(s), rot=float(rot), tx=float(tc[0]), ty=float(tc[1]), err=e_s)
            return out
    if e_t < 0.9 * d0:
        out.update(model='shift', tx=sx, ty=sy, err=e_t)
        return out
    out.update(model='none', err=d0)
    return out


def _slot_motion(dec, cf, fps, tm):
    """Camera move inside a slot from consecutive content frames (text masked, negatives un-inverted)."""
    Gf, kind = dec['Gf'], dec['kind']
    Z, R, X, Y = [1.0], [0.0], [0.0], [0.0]
    energy, dups, mags = [], 0, []
    pairs = 0
    for a, b in zip(cf[:-1], cf[1:]):
        ga = Gf[a] if kind[a] != 'inverted' else 255.0 - Gf[a]
        gb = Gf[b] if kind[b] != 'inverted' else 255.0 - Gf[b]
        H, W = ga.shape
        pairs += 1
        mask = np.full((H, W), 255, np.uint8)
        if tm[b] is not None:
            mask[tm[b]] = 0
        pm = _pair_motion(ga, gb, mask)
        if pm['model'] == 'dup':
            dups += 1
            Z.append(Z[-1]); R.append(R[-1]); X.append(X[-1]); Y.append(Y[-1])
            energy.append(0.0)
            mags.append(0.0)
            continue
        if pm['model'] == 'none':
            Z.append(Z[-1]); R.append(R[-1]); X.append(X[-1]); Y.append(Y[-1])
            energy.append(pm['d0'])
            mags.append(pm['d0'])
            continue
        s, rot, tc, err = pm['s'], pm['rot'], (pm['tx'], pm['ty']), pm['err']
        Z.append(Z[-1] * s); R.append(R[-1] + rot)
        X.append(X[-1] + tc[0] / W * 100); Y.append(Y[-1] + tc[1] / H * 100)
        energy.append(err)
        mags.append(abs(math.log(max(s, 1e-3))) * 100 + math.hypot(tc[0] / W * 100, tc[1] / H * 100))
    dur = max(len(cf), 1) / fps
    out = dict(zoom=round(Z[-1], 4), rot=round(R[-1], 2), dx=round(X[-1], 2), dy=round(Y[-1], 2),
               zoom_rate=round(math.log(max(Z[-1], 1e-3)) / dur, 4), pan_rate=[round(X[-1] / dur, 2), round(Y[-1] / dur, 2)],
               energy=round(float(np.mean(energy)) * fps if energy else 0.0, 2), dup_ratio=round(dups / max(pairs, 1), 2),
               still=bool(pairs >= 3 and dups >= pairs - 1))
    lz = np.log(np.maximum(np.array(Z), 1e-3))
    if abs(lz[-1]) > 0.03 and len(lz) >= 4:
        curve = (lz - lz[0]) / (lz[-1] - lz[0])
        lab, _ = M.ease_label(curve)
        out['ease'] = 'inout' if 'S-curve' in lab else 'out' if 'ease-out' in lab else 'in' if 'ease-in' in lab else 'linear'
    if len(mags) >= 8:
        k = len(mags) // 3
        m0, m1 = np.mean(mags[:k]) + 0.2, np.mean(mags[-k:]) + 0.2
        if m0 / m1 > 3 or m1 / m0 > 3:
            out['ramp'] = 'decelerates' if m0 > m1 else 'accelerates'
    return out


def describe_slots(ref, dec, tracks, texts):
    """Reference slot descriptors: subject, composition, motion, blur, grade target, 9:16 window HOG/layout.
    Only overlay text (the text slots) is masked here; scene text is part of the picture."""
    over = [tracks[i] for it in texts for i in it.get('src', [])]
    tmA = _static_text_masks(ref, over, AW, ref.ah)
    tmG = _static_text_masks(ref, over, GW, ref.gh)
    hp_over = {}

    def hp_clean(f):
        if f not in hp_over:
            g = dec['G'][f]
            hp_over[f] = _hp(_fill(g, tmG[f]) if tmG[f] is not None else g)
        return hp_over[f]
    STK = dec['STK']
    out = []
    for s in dec['slots']:
        cf = s['content'] or list(range(s['f0'], s['f1'] + 1))
        reps = sorted(set(cf[int(round(p * (len(cf) - 1)))] for p in (0.2, 0.5, 0.8)))
        imgs = []
        for f in reps:
            x = ref.rgb[f]
            if dec['kind'][f] == 'inverted':
                x = 255 - x
            if tmA[f] is not None:
                x = _fill(x, tmA[f])
            imgs.append(x)
        mid = imgs[len(imgs) // 2]
        subj = _subject(mid, bw=s['bw'], objects=_nanodet(mid))
        subj.pop('_faces', None)
        subj.pop('_pm', None)
        hogs, lays = [], []
        for x in imgs:
            g = cv2.cvtColor(x, cv2.COLOR_RGB2GRAY).astype(np.float32)
            h_, l_ = _win_desc(g, subj['cx'])
            hogs.append(h_)
            lays.append(l_)
        hog = np.mean(hogs, 0)
        hog /= np.linalg.norm(hog) + 1e-6
        mot = _slot_motion(dec, cf, ref.fps, dec['tm'])
        coh = float(np.median([STK[f][0] for f in cf]))
        br = float(np.median([STK[f][2] for f in cf]))
        bdir = float(np.median([STK[f][1] for f in cf]))
        blur = 'streak' if (coh >= 0.65 and br <= 0.3) else ('soft' if br <= 0.12 else None)
        tgt = _grade_target([x.astype(np.float32) / 255.0 for x in imgs])
        hsv = [cv2.cvtColor(x, cv2.COLOR_RGB2HSV) for x in imgs]
        hue_c = None
        if not s['bw']:
            hh = np.concatenate([h[..., 0][h[..., 1] > 60].ravel() for h in hsv])
            if len(hh) > 50:
                ang = hh.astype(np.float32) * 2 * np.pi / 180.0
                rlen = float(np.hypot(np.cos(ang).mean(), np.sin(ang).mean()))
                hue_c = round(rlen, 3)                               # 1 = one hue (tinted), 0 = varied
        plain = [f for f in cf if dec['kind'][f] == 'content'] or cf
        d = dict(id=f'S{s["i"] + 1:02d}', i=s['i'], f0=s['f0'], f1=s['f1'], n=s['f1'] - s['f0'] + 1,
                 show=plain[len(plain) // 2],
                 dur=round((s['f1'] - s['f0'] + 1) / ref.fps, 3), cut_in=s['cut_in']['type'], reps=reps,
                 bw=s['bw'], tint=hue_c, inverted=s['inverted'], subject=subj, motion=mot,
                 blur=dict(kind=blur, dir=round(bdir, 1), coh=round(coh, 2), detail=round(br, 3)),
                 L=round(float(np.median([dec['L'][f] for f in cf])), 1), target=tgt,
                 tone=np.median([_tone(cv2.cvtColor(x, cv2.COLOR_RGB2GRAY)) for x in imgs], 0),
                 col=np.mean([_colhist(x) for x in imgs], 0), _hog=hog, _lay=np.mean(lays, 0), _imgs=imgs,
                 flicker=s.get('flicker', []))
        clean = [f for f in cf if tmG[f] is None] or cf
        d['_reuse'] = [hp_clean(clean[int(round(p * (len(clean) - 1)))]) for p in (0.2, 0.5, 0.8)]
        out.append(d)
    _reuse_links(out)
    return out


def _reuse_links(slots):
    """Link slots that show the same source: regrade/punch boundaries continue the previous slot; non-adjacent
    slots whose pictures match (grade- and polarity-invariant structure) reuse the earlier slot's source."""
    for s in slots:
        if s['cut_in'] in ('regrade', 'punch') and s['i'] > 0:
            s['link'] = dict(to=s['i'] - 1, how='continue', why=s['cut_in'])
    for j, b in enumerate(slots):
        if b.get('link'):
            continue
        best, bi = 0.0, None
        for i in range(j - 1, -1, -1):
            v = max(abs(_ncc(x, y)) for x in slots[i]['_reuse'] for y in b['_reuse'])
            if v > best:
                best, bi = v, i
        if bi is not None and best >= 0.8 and bi < j - 1:
            b['link'] = dict(to=bi, how='same' if best >= 0.93 else 'continue', why='reuse', sim=round(best, 3))


# =============================================================================================== footage index
def _footage_geometry(path, info):
    """Letterbox picture box and a static corner logo from keyframes (fast: only I-frames are decoded)."""
    frames = list(_decode(path, 320, keyframes=True))
    if len(frames) < 12:
        frames = list(_decode(path, 320, fps=max(0.05, 40.0 / max(info['duration'], 1.0))))
    G = np.stack([cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) for f in frames]).astype(np.float32)
    lit = G.reshape(len(G), -1).mean(1) > 12
    if lit.sum() >= 6:
        G = G[lit]
    _, h, w = G.shape
    rows = (np.percentile(G, 99, axis=2) < 24).mean(0) >= 0.96
    cols = (np.percentile(G, 99, axis=1) < 24).mean(0) >= 0.96

    def lead(a):
        k = 0
        for v in a:
            if not v:
                break
            k += 1
        return k
    top, bot, left, right = lead(rows), lead(rows[::-1]), lead(cols), lead(cols[::-1])
    if h - top - bot < 0.45 * h:
        top = bot = 0
    if w - left - right < 0.45 * w:
        left = right = 0
    sx, sy = info['w'] / w, info['h'] / h
    ev = lambda v: int(round(v / 2.0)) * 2
    box = [ev(left * sx + (1 if left else 0)), ev(top * sy + (1 if top else 0)),
           info['w'] - ev(right * sx + (1 if right else 0)), info['h'] - ev(bot * sy + (1 if bot else 0))]
    logo = None
    sub = G[:, top:h - bot, left:w - right]
    if len(sub) >= 12:
        mean = sub.mean(0)
        e = np.abs(cv2.Laplacian(cv2.GaussianBlur(mean, (0, 0), 0.7), cv2.CV_32F))
        bh, bw_ = mean.shape
        corner = np.zeros_like(e, bool)
        cy, cx = int(0.25 * bh), int(0.22 * bw_)
        corner[:cy, :cx] = corner[:cy, -cx:] = corner[-cy:, :cx] = corner[-cy:, -cx:] = True
        corner[:3, :] = corner[-3:, :] = corner[:, :3] = corner[:, -3:] = False      # letterbox edge, not a logo
        thr = max(4.0, 6 * float(np.median(e)))
        raw = (e > thr) & corner
        n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(raw.astype(np.uint8), np.ones((5, 5), np.uint8)))
        best = None
        for i in range(1, n):
            x, y, ww, hh, a = st[i]
            strength = float(e[(lab == i) & raw].sum())
            if a >= 12 and ww >= 6 and (best is None or strength > best[0]):
                best = (strength, i)
        if best is not None and best[0] > 40 * thr:
            ys, xs = np.nonzero((lab == best[1]) & raw)
            logo = [ev((left + xs.min() - 1) * sx), ev((top + ys.min() - 1) * sy),
                    ev((left + xs.max() + 2) * sx), ev((top + ys.max() + 2) * sy)]
            # keep it >= 4 px inside the picture box (the renderer's inpaint mask needs that margin)
            logo = [max(box[0] + 4, logo[0]), max(box[1] + 4, logo[1]), min(box[2] - 4, logo[2]), min(box[3] - 4, logo[3])]
    return box, logo


def _sample_shots(pair, flat):
    """Sample-level shot ids from consecutive-sample stats (band-pass NCC, colour distance, LK/ECC-aligned NCC and,
    from index version 5, phase-correlation-aligned NCC: fast pattern motion where LK finds nothing). Slightly
    over-segmented on purpose: a candidate span never crosses a boundary."""
    n = len(pair)
    shot = np.zeros(n, np.int32)
    sid = 0
    for k in range(1, n):
        hp_, dh_, al_ = (float(v) for v in pair[k][:3])
        pc_ = float(pair[k][3]) if len(pair[k]) > 3 else -1.0     # phase-aligned NCC (index version >= 5)
        same = (hp_ >= 0.45) or (al_ >= 0.45 and dh_ < 0.45) or (dh_ < 0.15 and al_ >= 0.2) or \
            (dh_ < 0.3 and (hp_ >= 0.2 or al_ >= 0.3)) or (pc_ >= 0.6 and dh_ < 0.35)
        if not same or flat[k] != flat[k - 1]:
            sid += 1
        shot[k] = sid
    return shot


def _index_key(path, sample_fps):
    st = os.stat(path)
    return hashlib.sha256(json.dumps([os.path.abspath(path), st.st_size, int(st.st_mtime), float(sample_fps), VERSION,
                                      FW, THUMB_W]).encode()).hexdigest()[:16]


def index_footage(path, out_dir, sample_fps=3.0, cache_name='footage_index'):
    """Analyse the footage at `sample_fps` (cached in out_dir/<cache_name>.npz + .json)."""
    key = _index_key(path, sample_fps)
    npz, js = os.path.join(out_dir, cache_name + '.npz'), os.path.join(out_dir, cache_name + '.json')
    if os.path.exists(npz) and os.path.exists(js):
        try:
            meta = json.load(open(js))
            if meta.get('key') == key:
                z = np.load(npz, allow_pickle=False)
                idx = {k: z[k] for k in z.files}
                idx.update(meta)
                idx['shot'] = _sample_shots(idx['pair'], idx['flat'])
                if meta.get('geom_version') != GEOM_VERSION:
                    box, logo = _footage_geometry(path, V.probe(path))
                    if box == meta['box']:                  # samples were cut from the same box: refresh the logo
                        meta.update(logo=logo, geom_version=GEOM_VERSION)
                        json.dump(meta, open(js, 'w'), indent=1)
                        idx.update(logo=logo, geom_version=GEOM_VERSION)
                        log(f'footage index: logo refreshed -> {logo}')
                log(f'footage index: cache hit ({len(idx["t"])} samples)')
                return idx
        except (OSError, ValueError, KeyError):
            pass
    t_start = time.time()
    info = V.probe(path)
    box, logo = _footage_geometry(path, info)
    bw_, bh_ = box[2] - box[0], box[3] - box[1]
    fh = max(2, int(round(FW * bh_ / bw_ / 2) * 2))
    pos = _win_positions(FW, fh)
    log(f'footage: {info["w"]}x{info["h"]} {info["duration"]:.0f}s, picture box {box}, logo {logo}; sampling @ {sample_fps:g} fps')
    T, TONE, COL, SUBJ, HOG, LAY, WCX, MOT, PAIR, STK, SUBS, FLAT, LUM = ([] for _ in range(13))
    thumbs, offs = [], [0]
    prev = None
    objs = []
    nb = int(0.70 * fh)
    last_det = (-99, None, None)                       # (sample, faces, person mask) for reuse on near-identical samples
    last_nano = -99
    for k, fr in enumerate(_decode(path, FW, fps=sample_fps, crop=box)):
        t = k / sample_fps
        g = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY).astype(np.float32)
        Lm, sd = float(g.mean()), float(g.std())
        flat = Lm < 10 or sd < 5
        g160 = cv2.resize(g, (160, max(2, int(160 * fh / FW))), interpolation=cv2.INTER_AREA)
        hp = _hp(g)
        similar = prev is not None and last_det[0] == k - 1 and _ncc(prev[1], hp) >= 0.9
        new_shot = prev is None or _ncc(prev[1], hp) < 0.5
        if not flat and (new_shot or k - last_nano >= 3 * sample_fps):
            objs = _nanodet(fr)
            last_nano = k
        if flat:
            sub = dict(type='texture', scale='CU', cx=0.5, cy=0.5, face_h=0.0, person=0.0, skin=0.0, face_n=0, bw=True)
        elif similar:
            sub = _subject(fr, objects=objs, faces=last_det[1], pm=last_det[2])
        else:
            sub = _subject(fr, objects=objs)
        if not flat:
            last_det = (k, sub.pop('_faces'), sub.pop('_pm'))
        hs, ls, cxs = [], [], []
        for cx in pos + [float(np.clip(sub['cx'], 0, 1))]:
            h_, l_ = _win_desc(g, cx)
            hs.append(h_.astype(np.float16))
            ls.append(l_.astype(np.float16))
            cxs.append(cx)
        hs_hist = _hist_hsv(cv2.resize(fr, (160, g160.shape[0]), interpolation=cv2.INTER_AREA))
        mot = [1.0, 0.0, 0.0, 0.0, 0.0]
        pr = [1.0, 0.0, 0.0, 1.0]
        if prev is not None:
            est = M.estimate_pair(prev[0].astype(np.uint8), g160.astype(np.uint8), np.full(g160.shape, 255, np.uint8))
            al = -1.0
            if est['M'] is not None:
                Mx = est['M']
                s, rot = M.similarity_from_affine(Mx)
                Hh, Ww = g160.shape
                c = np.array([(Ww - 1) / 2.0, (Hh - 1) / 2.0])
                tc = Mx[:, 2] + Mx[:, :2] @ c - c
                wa = cv2.warpAffine(prev[0], Mx.astype(np.float32), (Ww, Hh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                loc = float(np.abs(wa - g160).mean())
                mot = [s, rot, tc[0] / Ww * 100, tc[1] / Hh * 100, loc]
                al = _ncc(_hp(wa), _hp(g160)) if est['method'] == 'lk' else 0.8 * _ncc(_hp(wa), _hp(g160))
            else:
                mot = [1.0, 0.0, 0.0, 0.0, float(np.abs(prev[0] - g160).mean())]
            pc = al
            if al < 0.45:                                    # LK/ECC found no good alignment: try the dominant shift
                psx, psy, _ = _phase_shift(prev[0], g160)
                pc = _shift_ncc(prev[0], g160, psx, psy)
            pr = [_ncc(prev[1], hp), _bhatt(prev[2], hs_hist), al, pc]
        prev = (g160, hp, hs_hist)
        subs = (not flat) and _subtitle_line(cv2.resize(fr[nb:], None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)) > 0
        if not flat and not subs:                       # title cards / burned-in captions anywhere in the picture
            big = [w for w in _text_words(fr)[0] if w['n'] >= 3 and w['h'] >= 0.03 * fh]
            subs = len(big) >= 2 or sum(w['n'] for w in big) >= 8
        th = int(round(THUMB_W * fh / FW))
        _, jpg = cv2.imencode('.jpg', cv2.cvtColor(cv2.resize(fr, (THUMB_W, th), interpolation=cv2.INTER_AREA),
                                                   cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 86])
        thumbs.append(jpg.ravel())
        offs.append(offs[-1] + len(jpg))
        T.append(t)
        TONE.append(_tone(g))
        COL.append(_colhist(fr))
        SUBJ.append([TYPES.index(sub['type']), sub.get('face_h', 0.0), sub['cx'], sub['cy'], sub.get('person', 0.0),
                     sub.get('skin', 0.0), float(sub.get('bw', False)), float(len(sub.get('objects', [])))])
        HOG.append(np.stack(hs))
        LAY.append(np.stack(ls))
        WCX.append(cxs)
        MOT.append(mot)
        PAIR.append(pr)
        STK.append(_streak(g160))
        SUBS.append(subs)
        FLAT.append(flat)
        LUM.append([Lm, sd, float(cv2.cvtColor(fr, cv2.COLOR_RGB2HSV)[..., 1].mean())])
        if k % 300 == 0 and k:
            el = time.time() - t_start
            log(f'  {t:7.1f}s / {info["duration"]:.0f}s  ({el:.0f}s elapsed)')
    n = len(T)
    PAIR = np.array(PAIR, np.float32)
    FLAT = np.array(FLAT, bool)
    shot = _sample_shots(PAIR, FLAT)
    SUBS = np.array(SUBS, bool)
    SUBS = SUBS | (np.r_[False, SUBS[:-1]] & np.r_[False, shot[1:] == shot[:-1]]) | \
        (np.r_[SUBS[1:], False] & np.r_[shot[1:] == shot[:-1], False])     # +-1 sample inside a shot
    idx = dict(t=np.array(T, np.float32), tone=np.array(TONE, np.float32), col=np.array(COL, np.float32),
               subj=np.array(SUBJ, np.float32), hog=np.array(HOG, np.float16), lay=np.array(LAY, np.float16),
               wcx=np.array(WCX, np.float32), mot=np.array(MOT, np.float32), pair=PAIR,
               stk=np.array(STK, np.float32), subs=SUBS, flat=FLAT, lum=np.array(LUM, np.float32),
               shot=shot, thumb_data=np.concatenate(thumbs) if thumbs else np.zeros(0, np.uint8),
               thumb_off=np.array(offs, np.int64))
    meta = dict(key=key, path=os.path.abspath(path), sample_fps=float(sample_fps), box=box, logo=logo, fw=FW, fh=fh,
                src_w=info['w'], src_h=info['h'], src_fps=info['fps'], duration=info['duration'], win_pos=pos,
                n=n, built=round(time.time() - t_start, 1), version=VERSION, geom_version=GEOM_VERSION)
    os.makedirs(out_dir, exist_ok=True)
    np.savez(npz, **idx)
    json.dump(meta, open(js, 'w'), indent=1)
    idx.update(meta)
    log(f'footage index: {n} samples, {shot[-1] + 1 if n else 0} sample-level shots, {time.time() - t_start:.0f}s')
    return idx


def _thumb(idx, k):
    a, b = int(idx['thumb_off'][k]), int(idx['thumb_off'][k + 1])
    im = cv2.imdecode(idx['thumb_data'][a:b], cv2.IMREAD_COLOR)
    return cv2.cvtColor(im, cv2.COLOR_BGR2RGB)


_PER_SAMPLE = ('t', 'tone', 'col', 'subj', 'hog', 'lay', 'wcx', 'mot', 'pair', 'stk', 'subs', 'flat', 'lum')
_SRC_KEYS = ('path', 'box', 'logo', 'fw', 'fh', 'src_w', 'src_h', 'src_fps', 'duration', 'sample_fps', 'key')


def source_names(paths):
    """EDL source names for footage files: one file -> 'footage' (the historical name); several -> short unique
    names from the file stems ('clip1', 'drone', 'hf_20261008_1632' ...)."""
    if len(paths) == 1:
        return ['footage']
    out = []
    for p in paths:
        b = ''.join(ch if (ch.isascii() and ch.isalnum()) else '_' for ch in os.path.splitext(os.path.basename(p))[0].lower())
        b = '_'.join(x for x in b.split('_') if x)[:20] or 'src'
        b = ('s' + b) if b[0].isdigit() else b
        n, k = b, 2
        while n in out:
            n, k = f'{b}_{k}', k + 1
        out.append(n)
    return out


def index_sources(paths, out_dir, sample_fps=3.0, names=None):
    """Index one or several footage files (each cached on its own) and merge them into one sample table.
    Adds idx['src'] (source number per sample) and idx['srcs'] (per source: name, path, box, logo, fw, fh, ...);
    sample-level shot ids never span two sources. One file keeps the historical cache name footage_index.*."""
    paths = [paths] if isinstance(paths, str) else list(paths)
    if not paths:
        raise ValueError('no footage given')
    names = list(names) if names else source_names(paths)
    parts = []
    for i, p in enumerate(paths):
        if not os.path.exists(p):
            raise FileNotFoundError(f'footage not found: {p}')
        cache = 'footage_index' if len(paths) == 1 else f'footage_index_{names[i]}'
        log(f'footage {i + 1}/{len(paths)}: {os.path.basename(p)} -> source "{names[i]}"')
        parts.append(index_footage(p, out_dir, sample_fps, cache_name=cache))
    srcs, k0 = [], 0
    for i, ix in enumerate(parts):
        n = len(ix['t'])
        srcs.append(dict({k: ix.get(k) for k in _SRC_KEYS}, name=names[i], k0=k0, k1=k0 + n))
        k0 += n
    if len(parts) == 1:
        idx = parts[0]
    else:
        idx = {k: np.concatenate([ix[k] for ix in parts]) for k in _PER_SAMPLE}
        shots, base = [], 0
        for ix in parts:
            shots.append(ix['shot'] + base)
            base += int(ix['shot'].max()) + 1 if len(ix['shot']) else 0
        idx['shot'] = np.concatenate(shots)
        offs, base = [], 0
        for ix in parts:
            offs.append(ix['thumb_off'][:-1] + base)
            base += int(ix['thumb_off'][-1])
        idx['thumb_off'] = np.concatenate(offs + [np.array([base], np.int64)])
        idx['thumb_data'] = np.concatenate([ix['thumb_data'] for ix in parts])
        idx.update({k: parts[0].get(k) for k in ('fw', 'fh', 'box', 'logo', 'path', 'win_pos')})
        idx['sample_fps'] = float(sample_fps)
    idx['src'] = np.concatenate([np.full(s['k1'] - s['k0'], i, np.int32) for i, s in enumerate(srcs)])
    idx['srcs'] = srcs
    idx.pop('_sb', None)
    return idx


def _src_of(idx, k):
    """Per-source metadata of footage sample k."""
    srcs = idx.get('srcs')
    if not srcs:
        return dict(name='footage', path=idx.get('path'), box=idx.get('box'), logo=idx.get('logo'), fw=idx['fw'],
                    fh=idx['fh'])
    return srcs[int(idx['src'][k])] if 'src' in idx else srcs[0]


# =============================================================================================== candidate search
def _z(x):
    """Per-slot z-score over all footage samples (mean/std, clipped): terms become comparable and a discrete term
    (subject compatibility) cannot explode the way a MAD-based z does."""
    return np.clip((x - x.mean(axis=-1, keepdims=True)) / (x.std(axis=-1, keepdims=True) + 1e-6), -4, 4)


def score_matrix(slots, idx):
    """Per (slot, footage sample) score from robust-z-scored terms + the best window per pair."""
    hogK = idx['hog'].astype(np.float32)                      # (K, windows, D)
    layK = idx['lay'].astype(np.float32)
    hogS = np.stack([s['_hog'] for s in slots])               # (S, D)
    layS = np.stack([s['_lay'] for s in slots])
    struct = np.einsum('sd,kwd->skw', hogS, hogK) + 0.5 * np.einsum('sd,kwd->skw', layS, layK) / layS.shape[1]
    best_w = struct.argmax(2)
    struct = struct.max(2)
    toneS = np.stack([s['tone'] for s in slots])
    tone = -np.abs(toneS[:, None, :] - idx['tone'][None, :, :]).sum(2)
    colS = np.stack([s['col'] for s in slots])
    col = np.sqrt(colS[:, None, :] * idx['col'][None, :, :]).sum(2)
    styp = np.array([TYPES.index(s['subject']['type']) for s in slots])
    ktyp = idx['subj'][:, 0].astype(int)
    subj = COMPAT[styp][:, ktyp].copy()
    fh_s = np.array([s['subject'].get('face_h', 0.0) for s in slots])
    fh_k = idx['subj'][:, 1]
    both = (fh_s[:, None] > 0.05) & (fh_k[None, :] > 0.05)
    subj += 0.5 * both * np.exp(-np.abs(np.log(np.maximum(fh_s[:, None], 1e-3) / np.maximum(fh_k[None, :], 1e-3))))
    eS = np.array([math.log1p(s['motion']['energy']) for s in slots])
    eK = np.log1p(idx['mot'][:, 4] * idx['sample_fps'])
    mot = -np.abs(eS[:, None] - eK[None, :])
    streakS = np.array([s['blur']['kind'] == 'streak' for s in slots])
    stK = (idx['stk'][:, 0] >= 0.6) & (idx['stk'][:, 2] <= 0.35)
    mot += 0.7 * (streakS[:, None] & stK[None, :])
    # detail / directionality relative to each side's own median (different resolutions and aspect ratios)
    lbr_s = np.array([math.log(max(s['blur']['detail'], 1e-3)) for s in slots])
    lbr_k = np.log(np.maximum(idx['stk'][:, 2], 1e-3))
    coh_s = np.array([s['blur']['coh'] for s in slots])
    coh_k = idx['stk'][:, 0]
    tex = -np.abs((lbr_s - np.median(lbr_s))[:, None] - (lbr_k - np.median(lbr_k))[None, :]) \
        - 1.5 * np.abs((coh_s - np.median(coh_s))[:, None] - (coh_k - np.median(coh_k))[None, :])
    colour_w = np.array([0.0 if s['bw'] else 0.6 for s in slots])
    total = 1.0 * _z(struct) + 0.45 * _z(tone) + colour_w[:, None] * _z(col) + 0.8 * _z(subj) + 0.35 * _z(mot) \
        + 0.2 * _z(tex)
    dark = np.array([s['L'] < 25 for s in slots])
    total -= 3.0 * idx['subs'][None, :]
    total -= np.where(dark[:, None], 0.0, 3.0) * idx['flat'][None, :]
    terms = dict(struct=struct, tone=tone, col=col, subj=subj, mot=mot, tex=tex)
    return total, best_w, terms


def _shot_bounds(idx):
    """Per sample-level shot id: (first sample time, last sample time + 1/fps)."""
    if '_sb' not in idx:
        t, shot, sf = idx['t'], idx['shot'], idx['sample_fps']
        n_sh = int(shot.max()) + 1 if len(shot) else 0
        t0 = np.full(n_sh, np.inf)
        t1 = np.full(n_sh, -np.inf)
        np.minimum.at(t0, shot, t)
        np.maximum.at(t1, shot, t)
        idx['_sb'] = (t0, t1 + 1.0 / sf)
    return idx['_sb']


def _spans(slot_dur, idx, k):
    """In-point for a candidate anchored at sample k: centred on it, kept inside its sample-level shot."""
    t0s, t1s = _shot_bounds(idx)
    sid = idx['shot'][k]
    s0, s1 = float(t0s[sid]), float(t1s[sid])
    sf = idx['sample_fps']
    tin = float(idx['t'][k]) - 0.5 * slot_dur + 0.5 / sf
    tin = min(max(tin, s0), max(s0, s1 - slot_dur))
    return tin, (s1 - s0) >= slot_dur - 1e-3


def rank_candidates(slots, idx, total, best_w, n_top=5):
    """Top-n diverse candidates per slot (score aggregated over the slot span)."""
    t = idx['t']
    sf = idx['sample_fps']
    shot = idx['shot']
    nK = len(t)
    for si, s in enumerate(slots):
        sc = total[si]
        dur = s['dur']
        w = max(1, int(round(dur * sf)))
        agg = sc.copy()
        if w > 1:
            # mean over the samples the span covers (only samples of the same sample-level shot)
            acc = np.zeros(nK)
            cnt = np.zeros(nK)
            for d in range(-(w // 2), w - w // 2):
                src = np.clip(np.arange(nK) + d, 0, nK - 1)
                ok = (shot[src] == shot) & (np.arange(nK) + d >= 0) & (np.arange(nK) + d < nK)
                acc += np.where(ok, sc[src], 0.0)
                cnt += ok
            agg = acc / np.maximum(cnt, 1)
        order = np.argsort(-agg)
        picks, per_shot = [], {}
        full = []
        srcv = idx['src'] if 'src' in idx else np.zeros(nK, np.int32)
        for k in order[:4000]:
            if len(picks) >= n_top and len(full) >= 400:
                break
            tin, fits = _spans(dur, idx, int(k))
            item = dict(k=int(k), t=round(tin, 3), score=round(float(agg[k]), 3), shot=int(shot[k]), fits=bool(fits),
                        win=int(best_w[si, k]), src=int(srcv[k]))
            full.append(item)
            if len(picks) >= n_top:
                continue
            if not fits and dur > 0.6:
                continue
            if per_shot.get(int(shot[k]), 0) >= 2:
                continue
            if any(p['src'] == item['src'] and abs(tin - p['t']) < max(3.0, dur + 1.0) for p in picks):
                continue
            picks.append(item)
            per_shot[int(shot[k])] = per_shot.get(int(shot[k]), 0) + 1
        s['cands'] = picks
        s['_full'] = full[:400]
    return slots


def assign(slots, idx):
    """Choose one candidate per slot: leaders greedily without overlapping footage (per source), linked slots
    follow their leader inside its source."""
    used = []
    srcv = idx['src'] if 'src' in idx else np.zeros(len(idx['t']), np.int32)
    lead = [s for s in slots if not s.get('link')]

    def chain_dur(s):
        d = s['dur']
        for x in slots:
            if x.get('link', {}).get('to') == s['i'] and x['link']['how'] == 'continue' and x['link']['why'] != 'reuse':
                d += chain_dur(x)
        return d
    margin = {s['i']: (s['cands'][0]['score'] - (s['cands'][-1]['score'] if len(s['cands']) > 1 else 0)) if s['cands'] else 0
              for s in lead}
    for s in sorted(lead, key=lambda x: -margin[x['i']]):
        need = chain_dur(s)
        pick = None
        pool = s['cands'] + [c for c in s['_full'] if c not in s['cands']]
        for strict in (True, False):
            for c in pool:
                if need > s['dur'] + 1e-6:                  # chain of linked slots: the whole chain must fit the shot
                    tin, fits = _spans(need, idx, c['k'])
                    if strict and not fits:
                        continue
                    c = dict(c, t=round(tin, 3), fits=fits)
                a, b = c['t'] - 0.25, c['t'] + need + 0.25
                cs = c.get('src', 0)
                if any(us == cs and a < u1 and u0 < b for us, u0, u1 in used):
                    continue
                if strict and idx['subs'][(srcv == cs) & (idx['t'] >= c['t'] - 0.2) & (idx['t'] <= c['t'] + need + 0.2)].any():
                    continue
                pick = c
                break
            if pick:
                break
        pick = pick or (s['cands'][0] if s['cands'] else s['_full'][0])
        used.append((pick.get('src', 0), pick['t'], pick['t'] + need))
        s['chosen'] = dict(pick, how='ranked')
    for s in slots:                                   # followers in order (a link points to an earlier slot)
        if not s.get('link'):
            continue
        L = slots[s['link']['to']]
        base = L['chosen']
        if s['link']['how'] == 'same':
            tin = base['t']
        elif s['link']['why'] == 'reuse':
            tin = base['t'] + L['dur']
        else:
            tin = base['t'] + (s['f0'] - L['f0']) / (L['n'] / L['dur'])
        bs = base.get('src', 0)
        mine = np.nonzero(srcv == bs)[0]
        k = int(mine[np.argmin(np.abs(idx['t'][mine] - (tin + 0.5 * s['dur'])))])
        same = np.nonzero(idx['shot'] == base.get('shot', idx['shot'][k]))[0]
        if len(same):
            s1 = float(idx['t'][same[-1]]) + 1.0 / idx['sample_fps']
            if tin + s['dur'] > s1:
                tin = max(float(idx['t'][same[0]]), s1 - s['dur'])
        s['chosen'] = dict(k=k, t=round(tin, 3), score=None, shot=int(idx['shot'][k]), fits=True, win=base.get('win', 0),
                           src=bs, how=f"linked to {L['id']} ({s['link']['why']})")
    return slots


# =============================================================================================== EDL building
def _fit_grade(target, cand_u8, bw):
    """Grade dict (ed_edl.apply_grade) that maps the candidate crop onto the slot's luma quantiles/sat/cast."""
    import ed_edl as E
    x = cand_u8.astype(np.float32) / 255.0
    st = E.grade_stats([x])
    tq = np.array(target['q'], np.float32)
    wq = np.array([0.6, 1.0, 1.0, 1.3, 1.0, 1.0, 0.6], np.float32)
    base = {'preset': 'bw' if bw else 'color'}
    p = dict(auto=1.0, gamma=1.0, contrast=1.1, gain=1.0, black=0.0)
    if not bw:
        p.update(sat=1.0, temp=0.0, tint=0.0)

    def loss(pp):
        y = E.apply_grade(x, dict(base, **pp), st)
        q = np.percentile(_luma01(y), [2, 10, 25, 50, 75, 90, 98])
        v = float((wq * (q - tq) ** 2).sum())
        if not bw:
            mx, mn = y.max(2), y.min(2)
            ok = mx > 0.08
            if ok.any():
                sat = float(((mx - mn) / np.maximum(mx, 1e-3))[ok].mean())
                m = y[ok].mean(0)
                cast = [(m[0] - m[1]) / (m.mean() + 1e-3), (m[2] - m[1]) / (m.mean() + 1e-3)]
                v += 0.6 * (sat - target['sat']) ** 2 + 0.4 * ((cast[0] - target['cast'][0]) ** 2 + (cast[1] - target['cast'][1]) ** 2)
        return v
    grid = dict(gamma=[0.45, 0.55, 0.65, 0.75, 0.85, 1.0, 1.15, 1.3, 1.5, 1.75, 2.1],
                contrast=[0.8, 0.9, 1.0, 1.1, 1.2, 1.35, 1.5, 1.7, 1.9],
                gain=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                black=[0.0, 0.02, 0.05, 0.08],
                sat=[0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.8],
                temp=[-0.4, -0.25, -0.12, 0.0, 0.12, 0.25, 0.4],
                tint=[-0.25, -0.12, 0.0, 0.12, 0.25])
    cur = loss(p)
    for _ in range(3):
        for key in [k for k in ('gamma', 'contrast', 'gain', 'black', 'sat', 'temp', 'tint') if k in p]:
            for v in grid[key]:
                q = dict(p)
                q[key] = v
                l_ = loss(q)
                if l_ < cur - 1e-6:
                    cur, p = l_, q
    g = dict(base)
    g.update({k: round(float(v), 3) for k, v in p.items() if not (k in ('temp', 'tint', 'black') and v == 0.0)})
    return g, round(cur, 5)


def _canvas_map(box_n, ref_w, ref_h):
    """Reference-frame fractions -> canvas fractions (centre 9:16 window of the reference at full height)."""
    ww = min(1.0, (ref_h * 9.0 / 16.0) / ref_w)
    x0 = 0.5 - ww / 2
    f = lambda x: float(np.clip((x - x0) / ww, 0.0, 1.0))
    return [round(f(box_n[0]), 3), round(box_n[1], 3), round(f(box_n[2]), 3), round(box_n[3], 3)]


def _crop_for(slot, c, idx):
    """Subject-centred 9:16 crop (box fractions) + the reference move mapped onto it."""
    k = c['k']
    ty, fh, scx, scy = idx['subj'][k][:4]
    typ = TYPES[int(ty)]
    cx = float(scx) if typ in ('face', 'person', 'hands') else float(idx['wcx'][k][c.get('win', 2)])
    cy = float(scy)
    z = 1.0
    sf = slot['subject'].get('face_h', 0.0)
    if sf > 0.05 and fh > 0.05:
        z = float(np.clip(sf / fh, 1.0, 1.6))
    sm = _src_of(idx, k)
    W, H = sm['fw'], sm['fh']
    wwf = min(1.0, (H / z) * 9.0 / 16.0 / W)
    px = float(np.clip(0.5 + 0.5 * (slot['subject']['cx'] - 0.5), 0.3, 0.7))
    cx = cx - (px - 0.5) * wwf
    if z > 1.0:
        cy = cy - (slot['subject']['cy'] - 0.5) / z
    crop = dict(cx=round(float(np.clip(cx, 0, 1)), 3), cy=round(float(np.clip(cy, 0, 1)), 3), z=round(z, 3))
    mv = slot['motion']
    to = {}
    if abs(math.log(max(mv['zoom'], 1e-3))) > 0.02:
        to['z'] = round(float(np.clip(z * mv['zoom'], 0.8, 2.6)), 3)
    if abs(mv['dx']) > 1.0:
        to['cx'] = round(float(np.clip(crop['cx'] - mv['dx'] / 100.0 * wwf, 0, 1)), 3)
    if abs(mv['dy']) > 1.0:
        to['cy'] = round(float(np.clip(crop['cy'] - mv['dy'] / 100.0 / z, 0, 1)), 3)
    if abs(mv['rot']) > 0.8:
        to['rot'] = round(-mv['rot'], 2)
    if to:
        crop['to'] = to
        crop['ease'] = mv.get('ease', 'linear')
    return crop


def _crop_pixels(idx, k, crop):
    """The candidate's 9:16 window (thumbnail pixels) at the crop start state."""
    im = _thumb(idx, k)
    H, W = im.shape[:2]
    hw = H / max(crop['z'], 1e-3)
    ww = min(W, hw * 9.0 / 16.0)
    cx = min(max(crop['cx'] * W, ww / 2), W - ww / 2)
    cy = min(max(crop['cy'] * H, hw / 2), H - hw / 2) if hw < H else H / 2
    x0, y0 = int(round(cx - ww / 2)), int(round(cy - min(hw, H) / 2))
    return im[max(0, y0):y0 + int(min(hw, H)), max(0, x0):x0 + int(ww)]


def _text_layers(texts, ref_w, ref_h, W, H, margin=60):
    """9:16 re-layout: one uniform scale from the dominant cap height, per-block fit, block position kept as the
    fraction of free space it had in the reference, vertical placement inside a safe band."""
    if not texts:
        return []
    caps = np.array([t['cap'] for t in texts], float)
    durs = np.array([t['f1'] - t['f0'] + 1 for t in texts], float)
    order = np.argsort(caps)
    cum = np.cumsum(durs[order])
    dom = float(caps[order][np.searchsorted(cum, cum[-1] / 2)])
    s = float(np.clip(0.05 * W / dom, 0.8 * W / ref_w, 2.2 * W / ref_w))
    band0, band1 = 0.16 * H, 0.76 * H
    blocks = {}
    for t in texts:
        blocks.setdefault(t['block'], []).append(t)
    out = []
    for items in blocks.values():
        x0 = min(t['box'][0] for t in items); y0 = min(t['box'][1] for t in items)
        x1 = max(t['box'][2] for t in items); y1 = max(t['box'][3] for t in items)
        bw_, bh_ = x1 - x0, y1 - y0
        sb = min(s, (W - 2 * margin) / max(bw_, 1.0), (band1 - band0) / max(bh_, 1.0))
        fx = x0 / (ref_w - bw_) if ref_w - bw_ > 1 else 0.5
        fy = y0 / (ref_h - bh_) if ref_h - bh_ > 1 else 0.5
        X0 = margin + float(np.clip(fx, 0, 1)) * max(0.0, W - 2 * margin - bw_ * sb)
        Y0 = band0 + float(np.clip(fy, 0, 1)) * max(0.0, (band1 - band0) - bh_ * sb)
        for t in items:
            font = 'oswald' if (t['aspect'] <= 0.62 and t['cap'] >= 0.2 * ref_h) else 'sans'
            size = t['cap'] * sb / CAP_RATIO[font]
            it = dict(text=t['text'], x=round(X0 + (t['box'][0] - x0) * sb, 1), y=round(Y0 + (t['base'] - y0) * sb, 1),
                      size=round(size, 1), color=t['colour'], font=font, blend=t['blend'], anchor='ls',
                      slot=t['id'], chars=t['glyphs'], w=round((t['box'][2] - t['box'][0]) * sb, 1))
            out.append(dict(f0=t['f0'], f1=t['f1'], items=[it]))
    out.sort(key=lambda d: (d['f0'], d['items'][0]['y']))
    return out


def _src_name(idx, c):
    return _src_of(idx, c['k'])['name']


def _segment(s, c, idx, ref_wh):
    """One EDL segment for slot s filled with candidate c (crop, fitted grade, blur fx, note, alternatives,
    flicker ghosts). ref_wh = reference (w, h) for the ghost geometry."""
    crop = _crop_for(s, c, idx)
    try:
        grade, _ = _fit_grade(s['target'], _crop_pixels(idx, c['k'], crop), s['bw'])
    except Exception as e:  # noqa: BLE001 — a failed fit must not stop the draft
        grade = {'preset': 'bw' if s['bw'] else 'color'}
        log(f'grade fit failed for {s["id"]}: {e}')
    fx = []
    if s['blur']['kind'] == 'streak':
        fx.append(dict(type='dirblur', len=round(float(np.clip(0.34 - s['blur']['detail'], 0.08, 0.3)), 3),
                       angle=round(float(s['blur']['dir'] if s['blur']['dir'] <= 90 else s['blur']['dir'] - 180), 1)))
    elif s['blur']['kind'] == 'soft':
        fx.append(dict(type='blur', r=3.0))
    subj = s['subject']
    mv = s['motion']
    note = (f"ref {subj['type']}/{subj['scale']} {'B&W' if s['bw'] else 'colour'}"
            + (f", move z x{mv['zoom']:.2f} dx {mv['dx']:+.0f}% dy {mv['dy']:+.0f}%" if
               abs(mv['zoom'] - 1) > 0.02 or abs(mv['dx']) > 1 or abs(mv['dy']) > 1 else '')
            + (f", {s['blur']['kind']} blur" if s['blur']['kind'] else '') + f"; cand {c.get('how', 'ranked')}"
            + (f" score {c['score']:+.2f}" if c.get('score') is not None else ''))
    name = _src_name(idx, c)
    seg = dict(id=s['id'], f0=s['f0'], f1=s['f1'], src=name, t=round(float(c['t']), 3), speed=1.0, crop=crop,
               grade=grade, fx=fx, note=note,
               alts=[dict(src=_src_name(idx, a), t=a['t'], tc=_tc(a['t']), score=a['score']) for a in s.get('cands', [])
                     if abs(a['t'] - c['t']) > 0.05 or a.get('src', 0) != c.get('src', 0)][:4])
    if s.get('flicker'):
        alt = next((a for a in s.get('cands', []) if abs(a['t'] - c['t']) > 1.0 or a.get('src', 0) != c.get('src', 0)),
                   None)
        for z in s['flicker']:
            if alt is None or not z.get('box'):
                continue
            bx = _canvas_map(z['box'], *ref_wh)
            seg.setdefault('ghosts', []).append(dict(
                src=_src_name(idx, alt), t=alt['t'], speed=1.0, n=max(1, len(z['frames'])), frames=z['frames'],
                crop=_crop_for(s, alt, idx), grade=grade, mode='screen', alpha=0.85,
                ellipse=[round((bx[0] + bx[2]) / 2, 3), round((bx[1] + bx[3]) / 2, 3),
                         round(max(0.08, (bx[2] - bx[0]) / 2), 3), round(max(0.06, (bx[3] - bx[1]) / 2), 3)],
                feather=0.5))
    return seg


def _sources_block(idx):
    srcs = idx.get('srcs') or [_src_of(idx, 0)]
    return {s['name']: dict(path=os.path.abspath(s['path']), box=s['box'], logo=s['logo']) for s in srcs}


def build_edl(ref, slots, texts, ops, idx, canvas, footage=None, music=None):
    """Draft EDL. footage is unused (kept for old callers: sources come from idx['srcs']); music = dict(path, in,
    ...) replaces the reference mix by that track (audio.music) — see align_music."""
    W, H = canvas
    segs = [_segment(s, s['chosen'], idx, (ref.w, ref.h)) for s in slots]
    # frame ops (reference frames -> output frames 1:1)
    eops = []
    for o in ops:
        if o['op'] == 'pflash':
            base = ref.rgb[o['base']]
            pm = V.person_mask(base) > 0.5
            bx = o['box']
            h_, w_ = pm.shape
            sub = pm[int(bx[1] * h_):max(int(bx[1] * h_) + 1, int(bx[3] * h_)), int(bx[0] * w_):max(int(bx[0] * w_) + 1, int(bx[2] * w_))]
            if sub.size and sub.mean() > 0.4:
                eops.append(dict(f=o['f'], op='mask_flash', a=o['a']))
            else:
                r = _canvas_map(bx, ref.w, ref.h)
                eops.append(dict(f=o['f'], op='rect_flash', rect=r, feather=2, a=o['a'], shape='object', thr=0.45, dilate=4))
        else:
            eops.append({k: v for k, v in o.items() if k in ('f', 'op', 'a', 'stage')})
    srcs = idx.get('srcs') or [_src_of(idx, 0)]
    if music and music.get('path'):
        dur = ref.n / ref.fps
        audio = dict(copy=False, music=dict(path=os.path.abspath(music['path']), gain_db=0.0, fade_in=0.0,
                                            fade_out=round(min(1.0, 0.05 * dur), 2), **{'in': round(float(music.get('in') or 0.0), 4)}),
                     voice=[], sfx=[], loudness=dict(lufs=-14, tp=-1))
    else:
        audio = dict(path=ref.path, copy=True)
    lufs, tp_max = -14.0, -1.0
    if audio.get('copy'):                      # the reference mix is muxed as is: QA measures against its own loudness
        il, tp = _loudness(ref.path)
        if il is not None:
            lufs, tp_max = round(il, 1), round(max(-1.0, (tp if tp is not None else -1.0) + 0.3), 1)
    meta = dict(scenario='remake', genre=None, generator='ed_remake', generator_version=VERSION, version=1, reference=ref.path,
                footage=[os.path.abspath(s['path']) for s in srcs] if len(srcs) > 1 else os.path.abspath(srcs[0]['path']),
                notes='Draft: text items are placeholders (slot ids T..), alts = other candidates per segment; '
                      'see candidates.json / slots.jpg / survey.jpg; swap a shot with "ed_remake.py pick".')
    if music:
        meta['music'] = {k: v for k, v in music.items() if k != 'path'}
    fps_out = int(round(ref.fps)) if abs(ref.fps - round(ref.fps)) < 0.01 else ref.fps
    # qa: the cut timing is the reference's by construction (no beat requirement); flashes keep the 3/s safety limit
    edl = dict(canvas=dict(w=W, h=H, fps=fps_out), n_frames=ref.n, sources=_sources_block(idx), audio=audio,
               segments=segs, ops=eops, texts=_text_layers(texts, ref.w, ref.h, W, H),
               qa=dict(genre=None, on_beat_share=0.0,
                       planned_white=[o['f'][0] for o in ops if o['op'] == 'white' and o.get('a', 1) >= 0.9],
                       planned_black=[o['f'][0] for o in ops if o['op'] == 'black'], planned_freeze=[],
                       flash_limit_hz=3.0, safe_zone='tiktok', lufs=lufs, lufs_tol=1.0, tp_max=tp_max),
               meta=meta)
    return edl


# =============================================================================================== outputs
def _label(img, text, colour=(255, 255, 0), scale=0.38):
    out = img.copy()
    cv2.rectangle(out, (0, 0), (out.shape[1], 14), (0, 0, 0), -1)
    cv2.putText(out, text, (2, 10), cv2.FONT_HERSHEY_SIMPLEX, scale, colour, 1, cv2.LINE_AA)
    return out


def _graded(slot, px):
    """Candidate crop with the grade the EDL would give it (preview of the remake look)."""
    import ed_edl as E
    try:
        g, _ = _fit_grade(slot['target'], px, slot['bw'])
        x = px.astype(np.float32) / 255.0
        return (np.clip(E.apply_grade(x, g, E.grade_stats([x])), 0, 1) * 255 + 0.5).astype(np.uint8)
    except Exception:  # noqa: BLE001 — preview only
        return px


def contact_sheet(ref, slots, idx, out_path, per_page=12, th=150):
    """slots.jpg (all slots) + slots_pNN.jpg pages: reference frame | top-5 candidate 9:16 crops (chosen framed)."""
    rows = []
    rw = int(round(th * ref.w / ref.h))
    cw = int(round(th * 9 / 16))
    for s in slots:
        r = cv2.resize(ref.rgb[s['show']], (rw, th), interpolation=cv2.INTER_AREA)
        tag = f"{s['id']} f{s['f0']}-{s['f1']} {s['subject']['type'][:4]}/{s['subject']['scale']}{' bw' if s['bw'] else ''}"
        tiles = [_label(r, tag)]
        cl = s['cands'][:5]
        ch = s['chosen']
        same = lambda a, b: abs(a['t'] - b['t']) < 0.05 and a.get('src', 0) == b.get('src', 0)
        if ch.get('how', '').startswith('linked'):
            cl = [ch] + [c for c in cl if not same(c, ch)][:4]
        multi = len(idx.get('srcs') or []) > 1
        for c in cl:
            crop = _crop_for(s, c, idx)
            px = _crop_pixels(idx, c['k'], crop)
            if px.size:
                px = _graded(s, px)
            im = cv2.resize(px, (cw, th), interpolation=cv2.INTER_AREA) if px.size else np.zeros((th, cw, 3), np.uint8)
            chosen = same(c, ch)
            tag = (f"{_src_name(idx, c)[:8]}@" if multi else '') + _tc(c['t'])
            im = _label(im, tag, (0, 255, 0) if chosen else (255, 255, 255), 0.33)
            if chosen:
                cv2.rectangle(im, (0, 0), (cw - 1, th - 1), (0, 255, 0), 2)
            tiles.append(im)
        while len(tiles) < 6:
            tiles.append(np.zeros((th, cw, 3), np.uint8))
        rows.append(np.hstack([np.pad(t, ((0, 3), (0, 3), (0, 0))) for t in tiles]))
    if not rows:
        return []
    width = max(r.shape[1] for r in rows)
    rows = [np.pad(r, ((0, 0), (0, width - r.shape[1]), (0, 0))) for r in rows]
    files = []

    def sheet(rs, cols):
        blank = np.zeros_like(rs[0])
        rs = rs + [blank] * ((-len(rs)) % cols)
        lines = [np.hstack([np.pad(x, ((0, 0), (0, 12), (0, 0))) for x in rs[i:i + cols]]) for i in range(0, len(rs), cols)]
        return np.vstack(lines)
    cv2.imwrite(out_path, cv2.cvtColor(sheet(rows, 3), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
    files.append(out_path)
    base, ext = os.path.splitext(out_path)
    for p in range(0, len(rows), per_page):
        fn = f'{base}_p{p // per_page + 1:02d}{ext}'
        cv2.imwrite(fn, cv2.cvtColor(sheet(rows[p:p + per_page], 2), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
        files.append(fn)
    return files


def _grid(tiles, cols, gap=4):
    """Tiles (same size, RGB uint8) -> one image, `cols` per row."""
    if not tiles:
        return None
    h, w = tiles[0].shape[:2]
    rows = []
    for i in range(0, len(tiles), cols):
        r = tiles[i:i + cols]
        r = r + [np.zeros((h, w, 3), np.uint8)] * (cols - len(r))
        rows.append(np.hstack([np.pad(t, ((0, gap), (0, gap), (0, 0))) for t in r]))
    return np.vstack(rows)


def _write_pages(tiles, out_path, cols, per_page, cols_all=None):
    """out_path = every tile (cols_all per row); <base>_pNN<ext> = pages of per_page tiles. -> file list."""
    if not tiles:
        return []
    files = []
    img = _grid(tiles, cols_all or cols)
    cv2.imwrite(out_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
    files.append(out_path)
    if len(tiles) > per_page:
        base, ext = os.path.splitext(out_path)
        for p in range(0, len(tiles), per_page):
            fn = f'{base}_p{p // per_page + 1:02d}{ext}'
            cv2.imwrite(fn, cv2.cvtColor(_grid(tiles[p:p + per_page], cols), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
            files.append(fn)
    return files


# =============================================================================================== review flow
def parse_time(s):
    """754.5 | '754.5' | '12:34.5' | '1:02:03.5' -> seconds."""
    if isinstance(s, (int, float)):
        return float(s)
    v = 0.0
    for part in str(s).strip().split(':'):
        v = v * 60 + float(part)
    return v


_SHORT = dict(face='face', person='body', hands='hands', object='object', landscape='wide', texture='plain')


def survey_sheet(idx, out_path, per_page=48, cols=8, tile_w=240, step_s=6.0):
    """Footage survey for choosing shots by eye: one tile per sample-level shot (long shots: one every step_s s),
    taken from the index thumbnails (no decoding), labelled 'n source@m:ss.s type'. Writes out_path (all tiles) +
    <base>_pNN pages (per_page tiles) + <base>.json (the entries as data). Returns (files, entries)."""
    t, shot, sf = idx['t'], idx['shot'], idx['sample_fps']
    multi = len(idx.get('srcs') or []) > 1
    th = int(round(tile_w * 9 / 16))
    entries, tiles = [], []
    for sid in np.unique(shot):
        ks = np.nonzero(shot == sid)[0]
        t0, t1 = float(t[ks[0]]), float(t[ks[-1]]) + 1.0 / sf
        n_rep = max(1, int((t1 - t0) // step_s) + (1 if (t1 - t0) % step_s > step_s / 2 else 0))
        reps = sorted({int(ks[min(len(ks) - 1, int((j + 0.5) * len(ks) / n_rep))]) for j in range(n_rep)})
        for k in reps:
            if idx['flat'][k] and len(ks) < 3:
                continue
            name = _src_of(idx, k)['name']
            typ = TYPES[int(idx['subj'][k][0])]
            e = dict(n=len(entries) + 1, src=name, shot=int(sid), t=round(float(t[k]), 2), tc=_tc(t[k]),
                     shot_t=[round(t0, 2), round(t1, 2)], type=typ, face_h=round(float(idx['subj'][k][1]), 3),
                     luma=round(float(idx['lum'][k][0]), 1), sat=round(float(idx['lum'][k][2]), 1),
                     motion=round(float(np.log1p(idx['mot'][k][4] * sf)), 2), subs=bool(idx['subs'][k]),
                     flat=bool(idx['flat'][k]))
            entries.append(e)
            im = _thumb(idx, k)
            h = max(2, int(round(tile_w * im.shape[0] / im.shape[1])))
            im = cv2.resize(im, (tile_w, min(h, th)), interpolation=cv2.INTER_AREA)
            tile = np.zeros((th + 16, tile_w, 3), np.uint8)
            y0 = 16 + (th - im.shape[0]) // 2
            tile[y0:y0 + im.shape[0]] = im
            tag = f"{e['n']} " + (f"{name[:8]}@" if multi else '') + f"{e['tc']} {_SHORT.get(typ, typ)}" + \
                (' SUBS' if e['subs'] else '')
            cv2.putText(tile, tag, (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0) if not e['subs'] else (255, 90, 90),
                        1, cv2.LINE_AA)
            tiles.append(tile)
    files = _write_pages(tiles, out_path, cols, per_page, cols_all=cols)
    with open(os.path.splitext(out_path)[0] + '.json', 'w') as fh:
        json.dump(_jsonable(dict(sources=[{k: s.get(k) for k in ('name', 'path', 'duration')} for s in (idx.get('srcs') or [])],
                                 tiles=entries)), fh, indent=1)
    return files, entries


def _frames_at(path, width, want):
    """Decode `path` at `width` px (native frame rate) and return {frame index: RGB} for the wanted indices."""
    want = set(int(w) for w in want)
    out = {}
    if not want:
        return out
    last = max(want)
    for i, fr in enumerate(_decode(path, width)):
        if i in want:
            out[i] = fr
        if i >= last:
            break
    return out


def _stats(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    return dict(L=float(g.mean()), sd=float(g.std()), sat=float(hsv[..., 1].mean()) / 255.0,
                bw=bool(float(np.median(hsv[..., 1])) < 14))


def compare_sheet(ref, remake_mp4, out_jpg, edl=None, per_page=24, th=200, cols=3):
    """Reference | remake side by side, one pair per slot (the middle frame of every segment of `edl`; without an EDL,
    the shots detected in the reference). Labels: '#N id m:ss.s', luma / saturation differences of the remake vs the
    reference; red label = the look differs a lot (|dL| > 30, contrast ratio outside 0.6-1.6, B&W mismatch).
    Writes out_jpg (+ _pNN pages when there are more than per_page slots) and <base>.json. Returns the per-slot list.
    ref = reference path or a Reference; edl = EDL dict or path (its fps maps output frames to both videos)."""
    ref_path = ref.path if isinstance(ref, Reference) else ref
    if isinstance(edl, str):
        with open(edl) as fh:
            edl = json.load(fh)
    ri, mi = V.probe(ref_path), V.probe(remake_mp4)
    rfps, mfps = float(ri['fps'] or 30.0), float(mi['fps'] or 30.0)
    if edl:
        fps = float(edl['canvas']['fps'])
        slots = [dict(n=i + 1, id=str(s.get('id', i + 1)), f0=int(s['f0']), f1=int(s['f1']))
                 for i, s in enumerate(sorted(edl['segments'], key=lambda s: s['f0']))]
    else:
        fps = rfps
        feats = [V.frame_feats(fr) for fr in _decode(ref_path, 160)]
        det = getattr(V, 'detect_cuts', None)
        cuts = det(feats, fps)['cuts'] if det and len(feats) > 2 else list(range(0, len(feats), int(round(fps))))
        bounds = [0] + [c for c in cuts if c > 0] + [len(feats)]
        slots = [dict(n=i + 1, id=f'S{i + 1:02d}', f0=a, f1=b - 1) for i, (a, b) in enumerate(zip(bounds[:-1], bounds[1:])) if b > a]
    for s in slots:
        tm = (s['f0'] + s['f1'] + 1) / 2.0 / fps
        s['t'] = round(tm, 3)
        s['rf'] = min(int(round(tm * rfps)), max(0, int(ri.get('nb_frames') or 10 ** 9) - 1))
        s['mf'] = int(round(tm * mfps))
    rw = int(round(th * ri['w'] / ri['h']))
    mw = int(round(th * mi['w'] / mi['h']))
    R_ = _frames_at(ref_path, max(rw, 64) // 2 * 2, [s['rf'] for s in slots])
    M_ = _frames_at(remake_mp4, max(mw, 32) // 2 * 2, [s['mf'] for s in slots])
    tiles, rows = [], []
    for s in slots:
        a, b = R_.get(s['rf']), M_.get(s['mf'])
        A = cv2.resize(a, (rw, th), interpolation=cv2.INTER_AREA) if a is not None else np.zeros((th, rw, 3), np.uint8)
        B = cv2.resize(b, (mw, th), interpolation=cv2.INTER_AREA) if b is not None else np.zeros((th, mw, 3), np.uint8)
        row = dict(n=s['n'], id=s['id'], f0=s['f0'], f1=s['f1'], t=s['t'], tc=_tc(s['t']))
        bad = False
        if a is not None and b is not None:
            sa, sb = _stats(a), _stats(b)
            row.update(dL=round(sb['L'] - sa['L'], 1), contrast=round(sb['sd'] / max(sa['sd'], 1.0), 2),
                       dsat=round(sb['sat'] - sa['sat'], 3), bw_ref=sa['bw'], bw_remake=sb['bw'])
            bad = abs(row['dL']) > 30 or not 0.6 <= row['contrast'] <= 1.6 or sa['bw'] != sb['bw']
        else:
            row['missing'] = 'reference' if a is None else 'remake'
            bad = True
        row['flag'] = bool(bad)
        rows.append(row)
        pair = np.hstack([A, np.zeros((th, 3, 3), np.uint8), B])
        tile = np.zeros((th + 16, pair.shape[1], 3), np.uint8)
        tile[16:] = pair
        tag = f"#{s['n']} {s['id']} {row['tc']}" + (f" dL{row['dL']:+.0f} c{row['contrast']:.2f}" if 'dL' in row else ' missing')
        cv2.putText(tile, tag, (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 80, 80) if bad else (255, 255, 0), 1, cv2.LINE_AA)
        tiles.append(tile)
    _write_pages(tiles, out_jpg, cols, per_page, cols_all=cols)
    with open(os.path.splitext(out_jpg)[0] + '.json', 'w') as fh:
        json.dump(dict(reference=os.path.basename(ref_path), remake=os.path.basename(remake_mp4), fps=fps, slots=rows), fh,
                  indent=1)
    return rows


# ----------------------------------------------------------------------------------------------- music track
def _loudness(path):
    """Integrated loudness (LUFS) and true peak (dBTP) of a file's audio by ffmpeg ebur128 -> (lufs, tp) or Nones."""
    import re
    p = subprocess.run(['ffmpeg', '-v', 'info', '-nostats', '-nostdin', '-i', path, '-vn', '-af', 'ebur128=peak=true',
                        '-f', 'null', '-'], capture_output=True, text=True)
    i_ = re.findall(r'I:\s+(-?[\d.]+) LUFS', p.stderr)
    tp = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', p.stderr)
    return (float(i_[-1]) if i_ else None), (float(tp[-1]) if tp else None)


def _mono(path, sr=8000):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', path, '-vn', '-ac', '1', '-ar', str(sr), '-f', 'f32le',
                        '-'], capture_output=True)
    return np.frombuffer(p.stdout, np.float32).copy()


def _onset_env(x, sr=8000, hop=80, n=512):
    """Spectral-flux onset envelope at sr/hop Hz (10 ms), local mean removed, unit variance."""
    if len(x) < n + hop:
        return np.zeros(0, np.float32)
    win = np.hanning(n).astype(np.float32)
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop]
    L = np.empty((len(fr), n // 2 + 1), np.float32)
    for i in range(0, len(fr), 4096):                    # chunks: bounded memory for long tracks
        L[i:i + 4096] = np.log1p(100.0 * np.abs(np.fft.rfft(fr[i:i + 4096] * win, axis=1)))
    flux = np.r_[0.0, np.maximum(np.diff(L, axis=0), 0).sum(1)]
    k = max(3, int(0.5 * sr / hop) | 1)
    e = np.maximum(flux - np.convolve(flux, np.ones(k) / k, 'same'), 0)
    return (e / (e.std() + 1e-9)).astype(np.float32)


def align_music(reference, music, sr=8000, hop=80):
    """Where the reference's soundtrack sits inside a separate music file: normalised cross-correlation of the
    spectral-flux onset envelopes (10 ms grid, parabolic peak refinement). Returns dict(offset = music second at
    reference t=0 (may be negative: the music starts later), ncc (0..1, >= 0.5 is a confident match),
    prominence (peak / best value 0.5 s away), aligned (bool), method). Robust to a voice / SFX on top of the
    music in the reference and to different masters."""
    out = dict(offset=0.0, ncc=0.0, prominence=0.0, aligned=False, method='onset-xcorr')
    a, b = _onset_env(_mono(reference, sr), sr, hop), _onset_env(_mono(music, sr), sr, hop)
    if len(a) < 50 or len(b) < 50:
        out['method'] = 'no audio'
        return out
    na, nb = len(a), len(b)
    lo, hi = -(na // 2), nb - na // 2                           # lags: music index = reference index + lag
    pad = na // 2
    bp = np.r_[np.zeros(pad, np.float32), b, np.zeros(na, np.float32)]
    nfft = 1 << int(math.ceil(math.log2(len(bp) + na)))
    c = np.fft.irfft(np.conj(np.fft.rfft(a, nfft)) * np.fft.rfft(bp, nfft), nfft)[:hi - lo + 1]
    e2 = np.r_[0.0, np.cumsum(bp.astype(np.float64) ** 2)]
    win_e = e2[na:na + len(c)] - e2[:len(c)]
    ncc = c / np.sqrt(float((a.astype(np.float64) ** 2).sum()) * np.maximum(win_e, 1e-9))
    ncc[win_e < 0.25 * float((a.astype(np.float64) ** 2).sum())] = 0.0      # mostly silence / outside the music
    i = int(np.argmax(ncc))
    frac = 0.0
    if 0 < i < len(ncc) - 1:
        y0, y1, y2 = ncc[i - 1], ncc[i], ncc[i + 1]
        den = y0 - 2 * y1 + y2
        frac = float(0.5 * (y0 - y2) / den) if abs(den) > 1e-9 else 0.0
    far = np.abs(np.arange(len(ncc)) - i) > int(0.5 * sr / hop)
    second = float(ncc[far].max()) if far.any() else 0.0
    out.update(offset=round((i + lo + frac) * hop / sr, 4), ncc=round(float(ncc[i]), 3),
               prominence=round(float(ncc[i]) / max(second, 1e-3), 2))
    out['aligned'] = bool(out['ncc'] >= 0.5 and out['prominence'] >= 1.25)
    return out


# ----------------------------------------------------------------------------------------------- re-pick a slot
def _slot_from_candidates(sl):
    """A slot record of candidates.json -> the fields _crop_for / _segment / _fit_grade need."""
    s = {k: sl.get(k) for k in ('id', 'f0', 'f1', 'dur', 'bw', 'subject', 'motion', 'blur', 'target', 'flicker')}
    s['flicker'] = s.get('flicker') or []
    s['cands'] = [dict(k=c['sample'], t=c['t'], score=c.get('score'), src=c.get('src_i', 0)) for c in sl.get('candidates', [])]
    return s


def repick(edl, out_dir, picks, log_fn=None):
    """Swap the footage moment of remake slots: picks = {slot: time | (source name, time)}; slot = segment id ('S05')
    or its 1-based number ('#5' / 5); time = seconds or 'm:ss.s' (the in-point: the first frame of the slot).
    Crop (subject-centred 9:16, the reference move mapped on it), grade (fitted to the slot's look) and blur fx are
    recomputed from out_dir/candidates.json + the cached footage index; other fields of the segment (transitions,
    extra fx, notes added by hand) are kept. Returns a new EDL (deep copy, meta.history appended)."""
    import copy as _copy
    say = log_fn or log
    with open(os.path.join(out_dir, 'candidates.json')) as fh:
        cj = json.load(fh)
    m = cj['meta']
    footage = m.get('footage_list') or ([m['footage']] if isinstance(m.get('footage'), str) else m.get('footage'))
    idx = index_sources(footage, out_dir, m.get('sample_fps', 3.0), names=m.get('source_names'))
    names = [s['name'] for s in idx['srcs']]
    new = _copy.deepcopy(edl)
    segs = sorted(new['segments'], key=lambda s: s['f0'])
    by_id = {str(s.get('id')): s for s in segs}
    slots = {str(s['id']): s for s in cj['slots']}
    hist = []
    for key, val in picks.items():
        k_ = str(key).strip()
        if k_.lstrip('#').isdigit() and k_ not in by_id:
            j = int(k_.lstrip('#')) - 1
            if not 0 <= j < len(segs):
                raise ValueError(f'slot {key}: the edit has {len(segs)} segments')
            k_ = str(segs[j]['id'])
        if k_ not in by_id or k_ not in slots:
            raise ValueError(f'slot {key}: no such remake slot (ids: {", ".join(list(slots)[:6])} ...)')
        src_name, tv = (val if isinstance(val, (list, tuple)) else (None, val))
        if isinstance(tv, str) and '@' in tv and src_name is None:
            src_name, tv = tv.split('@', 1)
        si = 0 if src_name is None else (names.index(src_name) if src_name in names else -1)
        if si < 0:
            raise ValueError(f'unknown source {src_name!r} (sources: {", ".join(names)})')
        t_in = parse_time(tv)
        s = _slot_from_candidates(slots[k_])
        dur = float(s['dur'])
        sm = idx['srcs'][si]
        if not -1e-6 <= t_in <= float(sm.get('duration') or 1e9) - min(dur, 0.1):
            raise ValueError(f"slot {k_}: {t_in:.2f} s is outside {sm['name']} (0-{float(sm.get('duration') or 0):.2f} s)")
        mine = np.arange(sm['k0'], sm['k1'])
        k = int(mine[np.argmin(np.abs(idx['t'][mine] - (t_in + 0.5 * dur)))])
        c = dict(k=k, t=round(t_in, 3), score=None, src=si, win=len(idx['wcx'][k]) - 1, how='picked by hand')
        seg = _segment(s, c, idx, tuple(m.get('ref_size') or (1920, 1080)))
        old = by_id[k_]
        auto = {'dirblur', 'blur'}
        seg['fx'] = seg['fx'] + [f for f in old.get('fx', []) if f.get('type') not in auto]
        for kk, vv in old.items():
            if kk not in seg:
                seg[kk] = vv
        old.clear()
        old.update(seg)
        hist.append(dict(op='pick', slot=k_, src=sm['name'], t=round(t_in, 3)))
        say(f"{k_}: {sm['name']}@{_tc(t_in)} crop {seg['crop']} grade {seg['grade'].get('preset')}")
    for s in idx['srcs']:
        new.setdefault('sources', {}).setdefault(s['name'], dict(path=os.path.abspath(s['path']), box=s['box'], logo=s['logo']))
    meta = new.setdefault('meta', {})
    meta['version'] = int(meta.get('version', 1)) + 1
    meta.setdefault('history', []).append(dict(cmd=dict(op='pick', picks=hist), at=time.strftime('%Y-%m-%dT%H:%M:%S')))
    return new


# =============================================================================================== effect measurement
MOVES_DIR = os.path.join(os.path.dirname(HERE), 'moves')
SHAKE_BLUR_CAL = 1.6        # displacements read on motion-blurred frames come out ~0.6x (calibrated: blur_shutter 0.5)
_SHAKE_PRESETS = {'impact': dict(amp=0.025, rot=0.0, tau=0.067), 'heavy': dict(amp=0.05, rot=1.5, tau=0.11),
                  'rot': dict(amp=0.004, rot=2.5, tau=0.067), 'micro': dict(amp=0.005, rot=0.15, tau=0.067)}


def _known_move(mid):
    """True when the move card exists (or the move folder is not shipped next to the engine)."""
    return not os.path.isdir(MOVES_DIR) or os.path.exists(os.path.join(MOVES_DIR, mid + '.yaml'))


def _scale_between(ga, gb, smin=0.25, smax=8.0, n=96):
    """Scale of b relative to a about the frame centre (zoom-in > 1) by search: a scaled by s, then shifted by phase
    correlation, best normalised correlation wins. Works across x5 zooms and heavy blur where pair tracking fails.
    -> (scale, ncc)."""
    h, w = ga.shape
    a = ga.astype(np.float32)
    b = gb.astype(np.float32)
    best = (1.0, -1.0)
    for s in np.geomspace(smin, smax, n):
        M_ = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), 0.0, float(s))
        wa = cv2.warpAffine(a, M_, (w, h), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        sx, sy, _ = _phase_shift(wa, b)
        v = _shift_ncc(wa, b, sx, sy)
        if v > best[1]:
            best = (float(s), float(v))
    return best


def _effect_curves(ref, dec):
    """Per-frame measurements of a short clip: pair motion between consecutive content frames of the same slot
    (model-selected: log zoom, roll, centre shift as fractions of the frame), residual, streak (coherence, axis,
    detail), luma; and the span velocity (phase-correlation shift over +-3 content frames) for speed changes."""
    n = ref.n
    Gf, kind = dec['Gf'], dec['kind']
    H, W = Gf[0].shape
    nan = lambda: np.full(n, np.nan)                       # noqa: E731
    C = dict(logz=nan(), rot=nan(), tx=nan(), ty=nan(), err=nan(), d0=nan(), inl=nan(), resp=nan(), vel=nan(),
             model=[None] * n, coh=np.array([s[0] for s in dec['STK']]), ang=np.array([s[1] for s in dec['STK']]),
             det=np.array([s[2] for s in dec['STK']]), L=np.asarray(dec['L'], float), W=W, H=H)
    g = lambda i: Gf[i] if kind[i] != 'inverted' else 255.0 - Gf[i]      # noqa: E731
    for s in dec['slots']:
        cf = s['content']
        for a, b in zip(cf[:-1], cf[1:]):
            mask = np.full((H, W), 255, np.uint8)
            if dec['tm'][b] is not None:
                mask[dec['tm'][b]] = 0
            pm = _pair_motion(g(a), g(b), mask)
            C['model'][b] = pm['model']
            for k in ('err', 'd0', 'inl', 'resp'):
                C[k][b] = pm[k]
            if pm['model'] in ('sim', 'shift', 'dup'):
                C['logz'][b] = math.log(max(pm['s'], 1e-3))
                C['rot'][b] = pm['rot']
                C['tx'][b] = pm['tx'] / W
                C['ty'][b] = pm['ty'] / H
        h = 3
        for j in range(h, len(cf) - h):
            a, b = cf[j - h], cf[j + h]
            sx, sy, resp = _phase_shift(g(a), g(b))
            if resp >= 0.08:
                C['vel'][cf[j]] = math.hypot(sx / W, sy / H) / max(1, b - a)
    return C


def _runs_of(idx, gap=1):
    out = []
    for i in sorted(idx):
        if out and i - out[-1][-1] <= gap + 1:
            out[-1].append(i)
        else:
            out.append([i])
    return out


def _cut_frames(dec):
    return [s['f0'] for s in dec['slots'][1:] if s['cut_in']['type'] == 'cut']


def _ev_light(ref, dec, C, fps):
    """White / black frames and luma flashes -> events (opacity curve, decay tau, colour, at a cut or not)."""
    n, L, kind = ref.n, C['L'], dec['kind']
    content = [i for i in range(n) if kind[i] in ('content', 'inverted')]
    base = np.array([np.median([L[j] for j in content if abs(j - i) <= 8 and kind[j] == 'content'] or [L[i]]) for i in range(n)])
    hot = [i for i in range(n) if kind[i] == 'white' or (kind[i] == 'content' and L[i] >= base[i] + 28)]
    dark = [i for i in range(n) if kind[i] == 'black' or (kind[i] == 'content' and L[i] <= base[i] - 45 and L[i] < 40)]
    cuts = _cut_frames(dec)
    out = []
    for kind_, frames in (('flash', hot), ('dip', dark)):
        for run in _runs_of(frames, gap=0):
            a, b = run[0], run[-1]
            j = b + 1                                      # the decaying tail: brighter than what follows
            after = [k for k in range(b + 1, min(n, b + 12)) if kind[k] == 'content']
            lv = float(np.median([L[k] for k in after[-4:]])) if after else float(base[a])
            while kind_ == 'flash' and j < n and kind[j] == 'content' and L[j] > lv + 6:
                j += 1
            end = j - 1
            if kind_ == 'flash':
                op = [float(np.clip((L[k] - lv) / max(255.0 - lv, 1.0), 0, 1)) for k in range(a, end + 1)]
            else:
                before = [k for k in range(max(0, a - 8), a) if kind[k] == 'content']
                lb = float(np.median([L[k] for k in before])) if before else lv
                op = [float(np.clip(1.0 - L[k] / max(lb, 1.0), 0, 1)) for k in range(a, end + 1)]
            peak = int(np.argmax(op))
            pk = sum(1 for v in op if v >= 0.9)
            tail = [(k, v) for k, v in enumerate(op[peak:]) if 0.06 <= v <= 0.9]
            tau = None
            if len(tail) >= 2:
                ks = np.array([k for k, _ in tail], float)
                lv_ = np.log(np.array([v for _, v in tail]))
                slope = np.polyfit(ks, lv_, 1)[0]
                if slope < -1e-3:
                    tau = round(float(-1.0 / (fps * slope)), 3)
            rgb = ref.rgb[a + peak].reshape(-1, 3).mean(0)
            colour = '#ffffff' if kind_ == 'flash' and rgb.min() > 200 else ('#000000' if kind_ == 'dip' else
                                                                           '#%02x%02x%02x' % tuple(int(v) for v in rgb))
            near = [c for c in cuts if a - 3 <= c <= end + 2]
            out.append(dict(type=kind_, f0=a, f1=end, t0=round(a / fps, 3), t1=round((end + 1) / fps, 3), frames=end - a + 1,
                            peak_frames=pk, opacity=[round(v, 3) for v in op], tau=tau, color=colour, at_cut=near[0] if near else None))
    return out


def _axis(angles):
    """Axial (0-180) circular mean and spread of streak angles -> (mean deg, spread deg)."""
    a = np.radians(np.asarray(angles, float) * 2.0)
    c, s = float(np.cos(a).mean()), float(np.sin(a).mean())
    r = math.hypot(c, s)
    return (math.degrees(math.atan2(s, c)) / 2.0) % 180.0, math.degrees(math.sqrt(max(0.0, -2 * math.log(max(r, 1e-6))))) / 2.0


def _axdiff(a, b):
    d = abs(float(a) - float(b)) % 180.0
    return min(d, 180.0 - d)


def _ev_whip(dec, C, fps, used):
    """Directional streak blur over >= 2 frames (with consistent axis) -> whip events, at a cut or inside a shot.
    Strong streak frames seed a run; neighbours with a weaker streak on the same axis join it (hysteresis). Below
    20 fps a whip may be a single strong frame at a cut."""
    n = len(dec['kind'])
    kind = dec['kind']
    coh, ang = C['coh'], C['ang']
    content = [i for i in range(n) if kind[i] in ('content', 'inverted')]
    det_med = float(np.median([C['det'][i] for i in content])) if content else 0.1
    # baseline = the lower quartile of the shot's own coherence around the frame (the neighbourhood when the frame sits
    # in a tiny slot, as whip frames often do): oriented content (stripes, railings) has a high coherence of its own,
    # a whip is a short rise above it
    own = {}
    for s_ in dec['slots']:
        for f in s_['content']:
            own[f] = s_['content'] if len(s_['content']) >= 6 else None
    base = {}
    for f in content:
        pool = own.get(f) or content
        base[f] = float(np.percentile([coh[x] for x in pool if abs(x - f) <= 15], 25))
    seeds = [i for i in content if coh[i] >= 0.55 and coh[i] - base[i] >= 0.3 and i not in used
             and (C['det'][i] <= 0.85 * det_med or coh[i] >= 0.65 or coh[i] - base[i] >= 0.45)]   # (dithering adds detail)
    streak = set(seeds)
    for i in seeds:
        for step in (-1, 1):
            j = i + step
            while (0 <= j < n and j not in streak and j not in used and kind[j] in ('content', 'inverted')
                   and coh[j] >= 0.45 and coh[j] - base[j] >= 0.2 and _axdiff(ang[j], ang[i]) <= 20):
                streak.add(j)
                j += step
    cuts = _cut_frames(dec)
    longest = max(4, int(round(0.5 * fps))) + 2
    out = []
    for run in _runs_of(sorted(streak), gap=1):
        if len(run) < 2 and not (fps < 20 and coh[run[0]] >= 0.65 and any(abs(c - run[0]) <= 1 for c in cuts)):
            continue
        if run[-1] - run[0] + 1 > longest:
            continue                                         # seconds of streaks: a blurred pan, not a whip
        mean, spread = _axis([C['ang'][i] for i in run])
        if spread > 25:
            continue
        horiz = min(mean, 180 - mean) <= 35
        vert = abs(mean - 90) <= 35
        a, b = run[0], run[-1]
        win = range(max(1, a - 3), min(n, b + 4))
        comp = 'tx' if horiz else 'ty'
        vals = [(C[comp][i], (C['inl'][i] if C['model'][i] == 'sim' else C['resp'][i])) for i in win
                if C['model'][i] in ('sim', 'shift') and np.isfinite(C[comp][i]) and
                ((C['model'][i] == 'sim' and C['inl'][i] >= 0.45) or C['resp'][i] >= 0.3)]
        mv = sum(v * w for v, w in vals)
        if horiz:
            d = ('right' if mv < 0 else 'left') if abs(mv) > 1e-3 else None
        elif vert:
            d = ('down' if mv < 0 else 'up') if abs(mv) > 1e-3 else None
        else:
            d = None
        near = [c for c in cuts if a - 3 <= c <= b + 3]
        speed = max([abs(v) for v, _ in vals] or [0.0])
        out.append(dict(type='whip', f0=a, f1=b, t0=round(a / fps, 3), t1=round((b + 1) / fps, 3), frames=b - a + 1,
                        axis='horizontal' if horiz else ('vertical' if vert else 'diagonal'), angle=round(mean, 1),
                        dir=d, speed=round(speed, 3), at_cut=near[0] if near else None,
                        coherence=round(float(np.mean([C['coh'][i] for i in run])), 2)))
    return out


def _ev_zoom(ref, dec, C, fps):
    """Runs of consistent per-frame scale change -> crash / punch / in_out / slow / out events (scale measured
    directly between the frames around a run, so blur in the middle does not lose it)."""
    out = []
    cuts = _cut_frames(dec)
    Gf, kind = dec['Gf'], dec['kind']
    g = lambda i: Gf[i] if kind[i] != 'inverted' else 255.0 - Gf[i]      # noqa: E731
    for s in dec['slots']:
        cf = s['content']
        if len(cf) < 3:
            continue
        lz = np.array([C['logz'][i] for i in cf])
        fin = np.isfinite(lz)
        act = [j for j in range(1, len(cf)) if fin[j] and abs(lz[j]) >= 0.012]
        gaps = set()       # frames where pair tracking failed (a big per-frame scale step at a low frame rate, heavy
        for a, b in zip(act[:-1], act[1:]):      # blur) between two zoom frames of the same sign belong to the move
            if 1 < b - a <= 4 and not fin[a + 1:b].any() and np.sign(lz[a]) == np.sign(lz[b]):
                gaps.update(range(a + 1, b))
        act = sorted(set(act) | gaps)
        runs = []
        for r in _runs_of(act, gap=1):
            cur = [r[0]]
            for j in r[1:]:
                last = next(np.sign(lz[x]) for x in reversed(cur) if fin[x])
                if not fin[j] or np.sign(lz[j]) == last:
                    cur.append(j)
                else:
                    runs.append(cur)
                    cur = [j]
            runs.append(cur)
        info = []
        for r in runs:
            j0, j1 = r[0], r[-1]
            sg = np.sign(lz[j0])
            while j0 - 1 >= 1 and np.isfinite(lz[j0 - 1]) and np.sign(lz[j0 - 1]) == sg and abs(lz[j0 - 1]) >= 0.002:
                j0 -= 1                                      # the eased start / landing of the move belongs to it
            while j1 + 1 < len(cf) and np.isfinite(lz[j1 + 1]) and np.sign(lz[j1 + 1]) == sg and abs(lz[j1 + 1]) >= 0.002:
                j1 += 1
            tot = float(np.nansum(lz[j0:j1 + 1]))
            if abs(tot) >= math.log(1.3) or np.isnan(lz[j0:j1 + 1]).any():
                sc, v = _scale_between(g(cf[j0 - 1]), g(cf[j1]))
                if v >= 0.35 and np.sign(math.log(sc)) == np.sign(tot):
                    tot = math.log(sc)
            seg = lz[j0:j1 + 1].copy()
            miss = ~np.isfinite(seg)
            if miss.any():                                   # the untracked frames carry the rest of the measured scale
                seg[miss] = (tot - float(np.nansum(seg))) / int(miss.sum())
            cum = np.cumsum(seg)
            ease = None
            if len(cum) >= 4 and abs(cum[-1]) > 1e-3:
                lab, _ = M.ease_label(np.concatenate([[0.0], cum]) / cum[-1])
                ease = 'inout' if 'S-curve' in lab else 'out' if 'ease-out' in lab else 'in' if 'ease-in' in lab else 'linear'
            info.append(dict(j0=j0, j1=j1, f0=cf[j0 - 1], f1=cf[j1], tot=tot, n=j1 - j0 + 1, ease=ease))
        for q in info:          # small per-frame scale readings on periodic / changing texture: confirm directly
            if abs(q['tot']) < math.log(1.3) and np.isfinite(lz[q['j0']:q['j1'] + 1]).all():
                sc, v = _scale_between(g(q['f0']), g(q['f1']), smin=0.6, smax=1.7, n=48)
                if q['n'] <= 3:     # a punch must show in the frames themselves
                    q['ok'] = bool(v >= 0.5 and np.sign(math.log(sc)) == np.sign(q['tot'])
                                   and abs(math.log(sc)) >= 0.5 * abs(q['tot']))
                else:               # a longer run: only a confident 'no zoom' overrules the per-frame steps
                    q['ok'] = not (v >= 0.5 and abs(math.log(sc)) < 0.4 * abs(q['tot']))
        info = [q for q in info if q.get('ok', True)]
        steady = [j for j in range(1, len(cf)) if fin[j] and abs(lz[j]) >= 0.0015]
        for sg in (1, -1):      # a steady slow zoom (Ken Burns): small, same-sign steps over >= 0.5 s
            for r in _runs_of([j for j in steady if np.sign(lz[j]) == sg], gap=1):
                tot = float(np.nansum(lz[r[0]:r[-1] + 1]))
                if (r[-1] - r[0] + 1 >= max(8, int(round(0.5 * fps))) and abs(tot) >= math.log(1.04)
                        and not any(q['j0'] <= r[-1] and q['j1'] >= r[0] for q in info)):
                    info.append(dict(j0=r[0], j1=r[-1], f0=cf[r[0] - 1], f1=cf[r[-1]], tot=tot, n=r[-1] - r[0] + 1, ease=None))
        info.sort(key=lambda q: q['j0'])
        skip = set()
        for qi, q in enumerate(info):
            if qi in skip:
                continue
            S = math.exp(q['tot'])
            dur = q['n'] / fps
            nxt = info[qi + 1] if qi + 1 < len(info) else None
            back = nxt if (nxt and np.sign(nxt['tot']) != np.sign(q['tot']) and (nxt['f0'] - q['f1']) / fps <= 0.6
                           and abs(nxt['tot']) >= 0.5 * abs(q['tot'])) else None
            near = [c for c in cuts if q['f0'] - 1 <= c <= q['f1'] + 2]
            ev = dict(type='zoom', f0=q['f0'], f1=q['f1'], t0=round(q['f0'] / fps, 3), t1=round((q['f1'] + 1) / fps, 3),
                      scale=round(S, 3), dur=round(dur, 3), ease=q['ease'], at_cut=near[0] if near else None)
            if q['n'] <= 2 and abs(q['tot']) >= math.log(1.07):
                ev.update(kind='punch', mode='bounce' if back else 'hold',
                          release=round((back['f1'] - q['f1']) / fps, 3) if back else None)
            elif abs(q['tot']) >= math.log(1.3) and dur <= 1.0:
                ev.update(kind='crash' if q['tot'] > 0 else 'crash_out')
                if back:
                    ev['back'] = dict(after=round((back['f0'] - q['f1']) / fps, 3), dur=round(back['n'] / fps, 3))
            elif back and abs(q['tot']) >= math.log(1.08) and 0.5 <= abs(back['tot'] / q['tot']) <= 2.0:
                ev.update(kind='in_out' if q['tot'] > 0 else 'out_in', f1=back['f1'], t1=round((back['f1'] + 1) / fps, 3))
            elif abs(q['tot']) >= math.log(1.04):
                ev.update(kind=('slow' if abs(q['tot']) / max(dur, 1e-3) <= 0.5 else 'in') if q['tot'] > 0 else 'out')
            else:
                continue
            if back and ev['kind'] in ('punch', 'in_out', 'out_in', 'crash'):
                skip.add(qi + 1)
            out.append(ev)
    return out


def _ev_roll(dec, C, fps):
    out = []
    cuts = _cut_frames(dec)
    for s in dec['slots']:
        cf = s['content']
        rr = np.array([C['rot'][i] if np.isfinite(C['rot'][i]) else 0.0 for i in cf])
        act = [j for j in range(1, len(cf)) if abs(rr[j]) >= 0.4]
        for r in _runs_of(act, gap=1):
            tot = float(rr[r[0]:r[-1] + 1].sum())
            alt = sum(1 for a, b in zip(r[:-1], r[1:]) if rr[a] * rr[b] < 0)
            if abs(tot) < 6 or alt > len(r) // 3:
                continue
            f0, f1 = cf[r[0] - 1], cf[r[-1]]
            near = [c for c in cuts if f0 - 2 <= c <= f1 + 2]
            out.append(dict(type='roll', f0=f0, f1=f1, t0=round(f0 / fps, 3), t1=round((f1 + 1) / fps, 3),
                            angle=round(tot, 1), dur=round((f1 - f0) / fps, 3), at_cut=near[0] if near else None))
    return out


def _ev_shake(dec, C, fps, used):
    """Bursts of alternating, decaying frame displacements (a camera shake on a hit) or a continuous jitter."""
    out = []
    W, H = C['W'], C['H']
    short = min(W, H)
    for s in dec['slots']:
        cf = s['content']
        if len(cf) < 5:
            continue
        # only trusted readings: tracked points (LK inliers) or a clear phase peak. A similarity fitted by ECC alone on
        # one-directional texture (stripes) invents motion along the edges (the aperture problem)
        ok = np.array([bool(np.isfinite(C['tx'][i]) and (C['model'][i] == 'dup' or (C['model'][i] == 'sim' and C['inl'][i] >= 0.45)
                                                       or (C['model'][i] == 'shift' and C['resp'][i] >= 0.3))) for i in cf])
        ok[0] = False                                        # no pair before the slot's first frame
        if ok.sum() < 3:
            continue
        D = np.array([[C['tx'][i] * W, C['ty'][i] * H, C['rot'][i]] if o else [np.nan] * 3 for i, o in zip(cf, ok)])
        xs = np.arange(len(cf))
        for c in range(3):                                   # untrusted frames: interpolated, so they add no jolt
            D[~ok, c] = np.interp(xs[~ok], xs[ok], D[ok, c])
        from scipy.ndimage import median_filter
        D = D - median_filter(D, size=(7, 1), mode='nearest')     # a steady pan / drift is not a shake
        D[~ok] = 0.0
        D, R = D[:, :2], D[:, 2]
        mag = np.hypot(D[:, 0], D[:, 1])
        # above the slot's own noise floor (frame-rate conversion judder on a pan, tracking noise)
        thr = max(0.8, 0.004 * short, 2.5 * float(np.median(mag[ok])))
        j = 1
        while j < len(cf):
            if mag[j] < thr or cf[j] in used:
                j += 1
                continue
            k = j
            quiet = 0
            while k + 1 < len(cf) and quiet < 2:
                k += 1
                quiet = quiet + 1 if mag[k] < max(0.35 * thr, 0.08 * mag[j:k].max()) else 0
            k -= quiet
            pk = max(range(j, k + 1), key=lambda x: mag[x])
            j = next(x for x in range(j, pk + 1) if mag[x] >= 0.5 * mag[pk])   # starts at the jolt, not at judder
            seg = list(range(j, k + 1))
            alt = sum(1 for a, b in zip(seg[:-1], seg[1:])
                      if (float(D[a] @ D[b]) < 0 and min(mag[a], mag[b]) >= 0.3 * thr) or
                      (R[a] * R[b] < 0 and min(abs(R[a]), abs(R[b])) >= 0.3))
            calm = [mag[x] for x in range(max(1, j - 3), j)]
            if calm and max(calm) >= 0.5 * mag[j]:
                alt = 0                                      # no rest before the jolt: continuous motion
            m = len(seg)
            third = max(1, m // 3)
            decays = m / fps >= 1.0 or float(mag[seg[:third]].max()) >= 1.4 * float(np.median(mag[seg[-third:]]))
            if m >= 3 and alt >= 2 and decays:               # a hit shake dies away; even judder (a pan stepping
                peak = float(mag[seg].max())                 # 1 px / 2 px) does not
                q = 0.08 ** (1.0 / m)
                amp = min(0.2, SHAKE_BLUR_CAL * peak / (1.0 + q) / short)
                disp = np.cumsum(R[seg])
                rot = round(SHAKE_BLUR_CAL * float(np.abs(disp).max()), 2) if np.abs(R[seg]).max() >= 0.3 else 0.0
                tau = round(m / (fps * 2.526), 3)
                if m / fps < 1.0 and amp < 0.01 and rot < 0.5:
                    j = k + 1                                # a hit shake moves >= 1 % of the frame; less is judder
                    continue                                 # or sharpening noise on a pan (continuous jitter aside)
                out.append(dict(type='shake', f0=cf[j], f1=cf[k], t0=round(cf[j] / fps, 3), t1=round((cf[k] + 1) / fps, 3),
                                frames=m, amp=round(amp, 4), rot=rot, tau=tau, peak_px=round(peak, 2), alternations=alt,
                                continuous=bool(m / fps >= 1.0 and amp < 0.012)))
            j = k + 1
    return out


def _moving(C, f):
    """Picture motion (not just a brightness change) between frame f and the previous content frame."""
    v = lambda k: abs(C[k][f]) if np.isfinite(C[k][f]) else 0.0          # noqa: E731
    return math.hypot(v('tx'), v('ty')) >= 0.002 or v('logz') >= 0.004 or v('rot') >= 0.1 or v('vel') >= 0.002


def _ev_speed(dec, C, fps, zoomed, used=()):
    """Speed changes inside one shot from the span velocity: fast and slow stretches (ratio >= 3) = a speed ramp;
    runs of identical frames after the picture's own motion = a freeze (motion that belongs to another event - the
    tail of a whip or a flash - does not count, so a still shot after a transition is not a freeze)."""
    out = []
    used = set(used)
    for s in dec['slots']:
        cf = s['content']
        if any(z['f0'] <= cf[-1] and z['f1'] >= cf[0] for z in zoomed):
            continue
        dups = [cf[j] for j in range(1, len(cf)) if C['model'][cf[j]] == 'dup']
        pos = {f: j for j, f in enumerate(cf)}
        k = max(3, int(round(0.15 * fps)))             # the picture moves on its own for >= 0.15 s, then stops dead
        for r in _runs_of(dups, gap=0):
            j0 = pos[r[0]]
            before = [cf[j] for j in range(j0 - k, j0)] if j0 - k >= 1 else []
            moving = bool(before) and all(f not in used and _moving(C, f) for f in before)
            if moving and len(r) + 1 >= max(6, int(0.25 * fps)):      # the action stops: not a static shot
                out.append(dict(type='freeze', f0=r[0] - 1, f1=r[-1], t0=round((r[0] - 1) / fps, 3), t1=round((r[-1] + 1) / fps, 3),
                                dur=round(len(r) / fps, 3)))
        if len(cf) < 12:
            continue
        v = np.array([C['vel'][i] for i in cf])
        ok = np.isfinite(v)
        if ok.sum() < 8:
            continue
        vv = v.copy()
        vv[~ok] = np.interp(np.nonzero(~ok)[0], np.nonzero(ok)[0], v[ok])
        from scipy.ndimage import median_filter
        vs = median_filter(vv, size=5, mode='nearest')
        vmax = float(vs.max())
        if vmax < 0.004:
            continue
        fast = vs >= 0.65 * vmax
        slow = vs <= vmax / 3.0
        if fast.sum() < 3 or slow.sum() < 4:
            continue
        if float(np.median(vs[slow])) < vmax / 25.0:
            continue                                         # a static stretch, not slow motion
        stat = sum(1 for j in np.nonzero(slow)[0] if C['model'][cf[j]] == 'dup')
        if stat > 0.5 * slow.sum():
            continue
        ratio = float(np.median(vs[fast]) / max(float(np.median(vs[slow])), vmax / 12.0))
        if ratio < 3.0:
            continue
        sl = np.nonzero(slow)[0]
        a, b = int(sl[0]), int(sl[-1])
        fa = np.nonzero(fast[:a])[0]
        fb = np.nonzero(fast[b + 1:])[0]
        ramp_in = (a - int(fa[-1])) if len(fa) else None
        ramp_out = int(fb[0]) + 1 if len(fb) else None
        fast_r, slow_r = 2.5, round(float(np.clip(2.5 / ratio, 0.08, 1.0)), 2)
        rel = (vs / vmax).round(3)
        f_in = cf[int(fa[-1])] if len(fa) else cf[0]
        pts = ([[0, fast_r], [f_in - cf[0], fast_r]] if len(fa) else []) + [[cf[a] - cf[0], slow_r], [cf[b] - cf[0], slow_r]]
        if len(fb):
            pts += [[cf[b + 1 + int(fb[0])] - cf[0], fast_r]]
        if pts[0][0] > 0:
            pts.insert(0, [0, pts[0][1]])
        if pts[-1][0] < cf[-1] - cf[0]:
            pts += [[cf[-1] - cf[0], pts[-1][1]]]
        curve = [q for k, q in enumerate(pts) if k == 0 or q != pts[k - 1]]
        out.append(dict(type='speed', f0=cf[0], f1=cf[-1], t0=round(cf[0] / fps, 3), t1=round((cf[-1] + 1) / fps, 3),
                        ratio=round(ratio, 2), slow=[cf[a], cf[b]], ramp_in_frames=ramp_in, ramp_out_frames=ramp_out,
                        fast_rate=fast_r, slow_rate=slow_r, speed_curve=curve,
                        profile=[[cf[j], float(rel[j])] for j in range(0, len(cf), 2)]))
    return out


def _ev_rgb(ref, dec, fps):
    """Red / blue channel misregistration (phase correlation of the channels) -> rgb split events."""
    kind = dec['kind']
    offs = {}
    for i in range(ref.n):
        if kind[i] != 'content':
            continue
        x = ref.rgb[i].astype(np.float32)
        if float(x.std()) < 8:
            continue
        sx, sy, resp = _phase_shift(x[..., 0], x[..., 2])
        if resp >= 0.15 and math.hypot(sx, sy) >= 1.5:
            offs[i] = (sx, sy)
    out = []
    for r in _runs_of(list(offs), gap=1):
        mx = max(math.hypot(*offs[i]) for i in r)
        sx, sy = offs[max(r, key=lambda i: math.hypot(*offs[i]))]
        out.append(dict(type='rgb_split', f0=r[0], f1=r[-1], t0=round(r[0] / fps, 3), t1=round((r[-1] + 1) / fps, 3),
                        frames=len(r), offset_px=round(mx, 2), angle=round(math.degrees(math.atan2(sy, sx)), 1),
                        px_1080=int(round(mx / 2.0 * 1080.0 / ref.rgb.shape[2]))))
    return out


def _nf(k, word):
    return f"{k} {word}{'' if k == 1 else 's'}"


def _cand(move, score, params, why, ev, apply=None):
    return dict(move=move, score=round(float(np.clip(score, 0, 1)), 3), params=params, why=why, at=ev.get('t0'),
                event=ev.get('i'), apply=apply)


def _candidates(events, fps):
    """Events -> move-card candidates with params in ed_plan.apply_command's vocabulary ('apply' = a ready command;
    fill "at" / "between" / the segment id for your edit)."""
    C = []
    for ev in events:
        t = ev['type']
        if t == 'flash':
            p = dict(color=ev['color'], frames=ev['frames'])
            if ev.get('tau'):
                p['tau'] = ev['tau']
            if ev['at_cut'] is not None:
                long_ = ev['frames'] >= 10 and ev['peak_frames'] >= 3
                dk = f", decay tau {ev['tau']} s" if ev.get('tau') else ''
                C.append(_cand('trans.flash', 0.92 if not long_ else 0.55, p,
                               f"{_nf(ev['frames'], 'bright frame')} at the cut (peak {_nf(ev['peak_frames'], 'frame')}{dk})",
                               ev, dict(op='transition', move='trans.flash', between=None, params=p)))
                if long_:
                    C.append(_cand('trans.fade', 0.8, dict(color=ev['color'], frames=ev['frames']), 'a long fade through white at the cut',
                                   ev, dict(op='transition', move='trans.fade', between=None, params=dict(frames=ev['frames']))))
            else:
                C.append(_cand('light.flash', 0.85, p, f"{_nf(ev['frames'], 'bright frame')} inside the shot (no cut)", ev,
                               dict(op='add', move='light.flash', at=None, params=dict(color=ev['color']))))
        elif t == 'dip':
            p = dict(color='#000000', frames=ev['frames'])
            C.append(_cand('trans.fade', 0.85 if ev['at_cut'] is not None else 0.5, p,
                           _nf(ev['frames'], 'dark frame') + (' at the cut' if ev['at_cut'] is not None else ''), ev,
                           dict(op='transition', move='trans.fade', between=None, params=dict(frames=ev['frames']))))
        elif t == 'whip':
            p = dict(dir=ev['dir'] or ('right' if ev['axis'] == 'horizontal' else 'down'), frames=max(4, ev['frames'] + ev['frames'] % 2))
            sc = 0.55 + 0.25 * min(1.0, ev['coherence']) + (0.1 if ev['dir'] else 0.0)
            if ev['at_cut'] is not None:
                C.append(_cand('trans.whip', sc + 0.05, p, f"{ev['frames']} frames of {ev['axis']} streak blur (coherence "
                               f"{ev['coherence']}) around the cut, camera moving {ev['dir'] or '?'}", ev,
                               dict(op='transition', move='trans.whip', between=None, params=p)))
            else:
                mid = 'tilt.whip' if ev['axis'] == 'vertical' else 'pan.whip'
                C.append(_cand(mid, sc, dict(dir=p['dir'], frames=ev['frames']), f"{ev['axis']} streak blur inside one shot", ev))
                C.append(_cand('trans.whip', sc - 0.25, p, 'the same blur used as a transition', ev,
                               dict(op='transition', move='trans.whip', between=None, params=p)))
        elif t == 'zoom':
            k = ev['kind']
            S = ev['scale']
            if k == 'crash':
                p = dict(scale=round(S, 2), dur=round(ev['dur'], 2))
                if ev.get('back'):
                    p['back'] = ev['back']
                sc = 0.62 + 0.25 * min(1.0, math.log(S / 1.3) / math.log(3)) + (0.08 if ev['ease'] in ('in', 'inout') else 0)
                C.append(_cand('zoom.crash', sc - (0.12 if ev['at_cut'] is not None else 0), p,
                               f"zoom x{S:.2f} in {ev['dur']:.2f} s ({ev['ease'] or '?'} ease)", ev,
                               dict(op='add', move='zoom.crash', at=None, params=dict(scale=p['scale'], dur=p['dur']))))
                if ev['at_cut'] is not None:
                    C.append(_cand('trans.zoom', sc + 0.05, dict(frames=max(6, int(round(ev['dur'] * fps)))),
                                   'the push-in ends on a cut', ev,
                                   dict(op='transition', move='trans.zoom', between=None, params=dict(frames=max(6, int(round(ev['dur'] * fps)))))))
            elif k == 'crash_out':
                C.append(_cand('zoom.out', 0.75, dict(scale=round(1 / S, 2)), f"fast zoom-out x{1 / S:.2f} in {ev['dur']:.2f} s", ev,
                               dict(op='add', move='zoom.out', at=None, params=dict(scale=round(1 / S, 2)))))
            elif k == 'punch':
                p = dict(scale=round(S, 2), mode=ev['mode'])
                if ev.get('release'):
                    p['release'] = ev['release']
                C.append(_cand('zoom.punch', 0.88, p, f"scale jump x{S:.2f} over {_nf(int(round(ev['dur'] * fps)), 'frame')}, "
                               + ('springs back' if ev['mode'] == 'bounce' else 'holds'), ev,
                               dict(op='add', move='zoom.punch', at=None, params=p)))
            elif k in ('in_out', 'out_in'):
                C.append(_cand('zoom.in_out', 0.8, dict(scale=round(max(S, 1 / S), 2)), 'zoom in and back out', ev,
                               dict(op='add', move='zoom.in_out', at=None, params=dict(scale=round(max(S, 1 / S), 2)))))
            elif k == 'slow':
                C.append(_cand('zoom.slow', 0.7, dict(scale=round(S, 3)), f"slow zoom-in x{S:.2f} over {ev['dur']:.1f} s", ev,
                               dict(op='add', move='zoom.slow', at=None, params=dict(scale=round(S, 3)))))
            elif k in ('in', 'out'):
                mid = 'zoom.in' if k == 'in' else 'zoom.out'
                sv = round(S if k == 'in' else 1 / S, 3)
                C.append(_cand(mid, 0.65, dict(scale=sv), f"zoom x{S:.2f} over {ev['dur']:.2f} s", ev,
                               dict(op='add', move=mid, at=None, params=dict(scale=sv))))
        elif t == 'roll':
            a = ev['angle']
            if ev['at_cut'] is not None and abs(a) >= 45 and ev['dur'] <= 0.8:
                C.append(_cand('trans.spin', 0.85, dict(angle=round(a), frames=max(6, int(round(ev['dur'] * fps)))),
                               f"{a:.0f} deg rotation through the cut", ev,
                               dict(op='transition', move='trans.spin', between=None, params=dict(angle=round(a)))))
            elif abs(a) >= 60 and ev['dur'] <= 0.6:
                C.append(_cand('roll.whip', 0.8, dict(angle=round(a), dur=ev['dur']), f"fast {a:.0f} deg roll", ev))
            else:
                C.append(_cand('roll.camera', 0.65, dict(angle=round(a, 1), dur=ev['dur']), f"{a:.1f} deg roll over {ev['dur']:.2f} s", ev,
                               dict(op='set', path='segments.<ID>.crop.to.rot', value=round(-a, 1))))
        elif t == 'shake':
            if ev['continuous']:
                prof = 'micro'
            elif ev['rot'] >= 0.8 and ev['amp'] < 0.015:
                prof = 'rot'
            elif ev['amp'] >= 0.035 or ev['rot'] >= 0.8:
                prof = 'heavy'
            else:
                prof = 'impact'
            p = dict(profile=prof, amp=round(ev['amp'], 3), rot=ev['rot'], tau=ev['tau'])
            sc = 0.6 + 0.08 * min(4, ev['alternations']) - (0.1 if ev['continuous'] else 0)
            C.append(_cand('shake.beat', sc, p, f"{ev['frames']} frames of alternating jolts (peak {ev['peak_px']} px, "
                           f"{ev['alternations']} reversals), decay tau ~{ev['tau']} s", ev,
                           dict(op='add', move='shake.beat', at=None, params=p)))
        elif t == 'speed':
            span = max(1, ev['speed_curve'][-1][0])
            p = dict(fast=ev['fast_rate'], slow=ev['slow_rate'], ratio=ev['ratio'], speed_curve=ev['speed_curve'],
                     speed_curve_rel=[[round(f / span, 3), r] for f, r in ev['speed_curve']])
            C.append(_cand('time.speed_ramp', 0.6 + 0.1 * min(3.0, ev['ratio'] / 3.0), p,
                           f"motion {ev['ratio']}x faster in the fast stretches than in the slow one (frames "
                           f"{ev['slow'][0]}-{ev['slow'][1]}); rates assume the card's fast 2.5x; speed_curve counts the "
                           f"clip's frames, speed_curve_rel x your segment's length fits it to a segment", ev,
                           dict(op='set', path='segments.<ID>.speed_curve', value=ev['speed_curve'])))
        elif t == 'freeze':
            C.append(_cand('time.freeze', 0.75, dict(dur=ev['dur']), f"{ev['dur']:.2f} s of identical frames", ev))
        elif t == 'rgb_split':
            p = dict(px=max(2, ev['px_1080']), angle=ev['angle'])
            C.append(_cand('fx.rgb_split', 0.6 + min(0.3, ev['frames'] * 0.05), p,
                           f"red/blue channels {ev['offset_px']} px apart on {_nf(ev['frames'], 'frame')}", ev,
                           dict(op='add', move='fx.rgb_split', at=None, params=p)))
    C = [c for c in C if _known_move(c['move'])]
    C.sort(key=lambda c: -c['score'])
    best = {}
    for c in C:
        if c['move'] not in best:
            best[c['move']] = dict(c, count=1, at_all=[c['at']])
        else:
            best[c['move']]['count'] += 1
            best[c['move']]['at_all'].append(c['at'])
    return sorted(best.values(), key=lambda c: -c['score'])


def measure_effect(path, fps=None, sheet=None, max_s=30.0, start=0.0, end=None):
    """Measure a short reference clip (or GIF) of a named effect / transition -> {"path", "duration", "fps", "frames",
    "events": [...], "candidates": [{"move", "score", "params", "why", "at", "count", "apply"}]} (best first).
    Uses the remake decomposition (cuts, white / black / inverted frames) plus per-frame curves: model-selected pair
    motion (log zoom, roll, centre shift), span velocity, streak blur, luma, R/B channel offsets. Events: cut,
    flash / dip (opacity curve, decay tau, colour), whip (streak axis, camera direction, frames), zoom (crash /
    punch / in_out / slow / in / out with scale measured directly across the run, duration, easing), roll, shake
    (amp as a fraction of the short side, rot, tau from the burst length), speed (fast / slow ratio, speed_curve),
    freeze, rgb_split. Params use ed_plan.apply_command's vocabulary; 'apply' is a ready command where a point edit
    can place the move (fill "at", "between" or the segment id), else a low-level edit template.
    Measured on the engine's own renders (tests/test_remake.py), as MP4 and as 25 fps dithered GIF: zoom.crash
    x2.9-3.0 for x3.0 / 0.4 s, trans.whip direction right, trans.flash 1 peak frame + decay, time.speed_ramp ratio ~8
    for 2.5 -> 0.3, shake.beat heavy; a still clip gives no candidates.
    sheet = a jpg path: frames with event marks + the curves. start / end (s) measure a window of a longer clip
    (times in the result stay on the clip's own timeline; frames count from the window's start); at most max_s
    seconds are measured."""
    info = V.probe(path)
    rate = float(fps or info.get('fps') or 30.0)
    if not rate or rate > 120:
        rate = 30.0
    clip = path
    tmp = None
    start = max(0.0, float(start or 0.0))
    span = min(max_s, (float(end) - start) if end is not None else max_s)
    if span <= 0:
        raise ValueError(f'measure_effect: empty window {start}-{end} s')
    paletted = (info.get('codec') in ('gif', 'apng', 'webp') or str(info.get('pix_fmt') or '').startswith('pal')
                or path.lower().endswith(('.gif', '.apng', '.webp')))
    if (info.get('duration') or 0) > start + span or start > 0 or paletted:
        # GIF palettes are dithered: the noise reads as fine detail and breaks the streak-blur measures, so a
        # paletted clip is softened by a 0.9 px blur (measured on GIFs of the engine's own whip / flash / crash /
        # shake renders); a window / a long clip is cut out. Constant rate = the measuring rate.
        fd, tmp = tempfile.mkstemp(suffix='.mp4', prefix='.measure_')
        os.close(fd)
        vf = (['gblur=sigma=0.9'] if paletted else []) + ['format=yuv444p']
        subprocess.run(['ffmpeg', '-v', 'error', '-y'] + (['-ss', f'{start:.3f}'] if start > 0 else []) +
                       ['-i', path, '-t', f'{span:.3f}', '-an', '-vf', ','.join(vf), '-r', f'{rate:.6g}', '-c:v', 'libx264',
                        '-preset', 'veryfast', '-crf', '8', tmp], check=True)
        clip = tmp
    try:
        ref = Reference(clip, fps=rate)
        tracks = _refine_tracks(ref, _track_masks(ref, _track_words(ref.words, ref.tmask)))
        dec = decompose(ref, tracks)
        C = _effect_curves(ref, dec)
        fps_ = ref.fps
        events = [dict(type='cut', f0=f, f1=f, t0=round(f / fps_, 3), t1=round(f / fps_, 3)) for f in _cut_frames(dec)]
        zslots = []           # a 'punch' slot boundary of the decomposition is a scale step inside one shot: the zoom
        for s in dec['slots']:            # analysis runs across it (a crash zoom is often split there)
            if zslots and s['cut_in']['type'] == 'punch' and s['content']:
                b = s['content'][0]
                if not np.isfinite(C['logz'][b]):
                    C['logz'][b] = math.log(max(float(s['cut_in'].get('sc') or 1.0), 1e-3))
                zslots[-1] = dict(zslots[-1], f1=s['f1'], content=list(zslots[-1]['content']) + list(s['content']))
            else:
                zslots.append(dict(s))
        light = _ev_light(ref, dec, C, fps_)
        used = {f for e in light for f in range(e['f0'], e['f1'] + 1)}
        whips = _ev_whip(dec, C, fps_, used)
        used |= {f for e in whips for f in range(e['f0'] - 1, e['f1'] + 2)}
        zooms = _ev_zoom(ref, dict(dec, slots=zslots), C, fps_)
        used |= {f for e in zooms if e.get('kind') in ('crash', 'crash_out', 'punch') for f in range(e['f0'], e['f1'] + 1)}
        events += light + whips + zooms + _ev_roll(dec, C, fps_) + _ev_shake(dec, C, fps_, used) + \
            _ev_speed(dec, C, fps_, [z for z in zooms if z.get('kind') != 'slow'], used) + _ev_rgb(ref, dec, fps_)
        events.sort(key=lambda e: (e['f0'], e['type']))
        for i, e in enumerate(events):
            e['i'] = i
        cands = _candidates([e for e in events if e['type'] != 'cut'], fps_)
        n_cuts = sum(1 for e in events if e['type'] == 'cut')
        short = [s for s in dec['slots'] if s['f1'] - s['f0'] + 1 <= 2]
        if n_cuts >= 4 and len(short) >= 3 and _known_move('cut.flash'):
            cands.append(dict(move='cut.flash', score=0.7, params=dict(frames_per_image=2), at=0.0, count=len(short),
                              why=f'{len(short)} images of <= 2 frames', event=None, apply=None, at_all=[0.0]))
            cands.sort(key=lambda c: -c['score'])
        if start > 0:                                        # times back on the clip's own timeline
            for e in events:
                e['t0'], e['t1'] = round(e['t0'] + start, 3), round(e['t1'] + start, 3)
            for c in cands:
                c['at'] = None if c.get('at') is None else round(c['at'] + start, 3)
                c['at_all'] = [None if x is None else round(x + start, 3) for x in c.get('at_all') or []]
        res = dict(path=os.path.abspath(path), duration=round(ref.n / fps_, 3), fps=fps_, frames=ref.n,
                   size=[ref.w, ref.h], window=[round(start, 3), round(start + ref.n / fps_, 3)],
                   events=_jsonable(events), candidates=_jsonable(cands))
        if sheet:
            effect_sheet(ref, dec, C, events, sheet)
            res['sheet'] = sheet
        return res
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)


def effect_sheet(ref, dec, C, events, out, max_tiles=36, tile_w=150):
    """Frames of the measured clip (event frames first) with marks + plotted curves (cumulative zoom, roll, shift,
    luma, streak coherence, span velocity) and the event spans."""
    n = ref.n
    marks = {}
    for e in events:
        for f in range(e['f0'], e['f1'] + 1):
            marks.setdefault(f, []).append(e['type'])
    want = sorted({g for f in marks for g in range(f - 2, f + 3) if 0 <= g < n})        # events with context
    if len(want) > max_tiles:
        want = [want[int(i)] for i in np.linspace(0, len(want) - 1, max_tiles)]
    rest = [f for f in range(n) if f not in set(want)]
    room = max_tiles - len(want)
    fill = [rest[int(i)] for i in np.linspace(0, len(rest) - 1, room)] if (room > 0 and rest) else []
    frames = sorted(set(want) | set(fill))
    th = int(round(tile_w * ref.ah / AW))
    tiles = []
    for f in frames:
        im = cv2.resize(ref.rgb[f], (tile_w, th), interpolation=cv2.INTER_AREA)
        lab = np.zeros((16, tile_w, 3), np.uint8)
        txt = f"{f} {','.join(sorted(set(marks.get(f, []))))}"
        cv2.putText(lab, txt[:24], (2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 220, 60) if f in marks else (200, 200, 200), 1,
                    cv2.LINE_AA)
        tiles.append(np.vstack([lab, im]))
    cols = 6
    grid = _grid(tiles, cols)
    pw, ph = grid.shape[1], 70
    series = [('zoom (cum log)', np.nancumsum(np.nan_to_num(C['logz'])), (90, 200, 255)),
              ('roll (cum deg)', np.nancumsum(np.nan_to_num(C['rot'])), (255, 140, 90)),
              ('shift x (cum)', np.nancumsum(np.nan_to_num(C['tx'])), (120, 255, 120)),
              ('shift y (cum)', np.nancumsum(np.nan_to_num(C['ty'])), (60, 200, 60)),
              ('luma', C['L'], (240, 240, 240)), ('streak coherence', C['coh'], (255, 90, 200)),
              ('speed (span)', np.nan_to_num(C['vel']), (255, 255, 90))]
    plots = []
    for name, y, col in series:
        im = np.full((ph, pw, 3), 18, np.uint8)
        for e in events:
            if e['type'] == 'cut':
                x = int(e['f0'] / max(1, n - 1) * (pw - 1))
                cv2.line(im, (x, 0), (x, ph - 1), (90, 90, 90), 1)
            else:
                x0, x1 = int(e['f0'] / max(1, n - 1) * (pw - 1)), int(e['f1'] / max(1, n - 1) * (pw - 1))
                cv2.rectangle(im, (x0, 0), (max(x0 + 1, x1), ph - 1), (45, 45, 70), -1)
        y = np.asarray(y, float)
        lo, hi = float(np.nanmin(y)), float(np.nanmax(y))
        if hi - lo < 1e-9:
            hi = lo + 1.0
        pts = np.array([[int(i / max(1, n - 1) * (pw - 1)), int((1 - (v - lo) / (hi - lo)) * (ph - 14)) + 12]
                        for i, v in enumerate(y)], np.int32)
        cv2.polylines(im, [pts], False, col, 1, cv2.LINE_AA)
        cv2.putText(im, f'{name}  [{lo:.3g} .. {hi:.3g}]', (4, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, col, 1, cv2.LINE_AA)
        plots.append(im)
    img = np.vstack([grid] + plots)
    cv2.imwrite(out, cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
    return out


def compare(out_dir, hand_path, tol=1.0):
    """Draft vs a hand-made EDL: exact cut frames, and how often the top-5 contain the hand-picked moment."""
    draft_ = json.load(open(os.path.join(out_dir, 'edl_draft.json')))
    cands = json.load(open(os.path.join(out_dir, 'candidates.json')))
    hand = json.load(open(hand_path))
    fps = draft_['canvas']['fps']
    mine = sorted(s['f0'] for s in draft_['segments'])
    hb = set(s['f0'] for s in hand['segments'])
    for s in hand['segments']:
        for g in s.get('grades', []) or []:
            if g.get('k0', 0) > 0:
                hb.add(s['f0'] + g['k0'])
    hb = sorted(hb)
    ms = set(mine)
    rep = dict(draft_boundaries=len(mine), hand_boundaries=len(hb), exact=sorted(ms & set(hb)),
               only_hand=sorted(set(hb) - ms), only_draft=sorted(ms - set(hb)))
    frames = {d['f']: d for d in cands.get('frames', [])}
    why = {}
    for f in rep['only_hand']:
        prev = f - 1
        k = frames.get(prev, {}).get('kind') if frames else None
        pr = frames.get(f, {}).get('pair', {})
        why[f] = (f"previous frame {prev} is {k}; " if k and k != 'content' else '') + \
            (f"pair {pr.get('type')} hp {pr.get('hp')} dh {pr.get('dh')}" if pr else frames.get(f, {}).get('kind', ''))
    rep['only_hand_why'] = why
    slots = cands['slots']
    shot_of = None
    npz = os.path.join(out_dir, 'footage_index.npz')
    if os.path.exists(npz):
        z = np.load(npz, allow_pickle=False)
        ts, sh = z['t'], z['shot']
        shot_of = lambda tt: int(sh[int(np.argmin(np.abs(ts - tt)))])
    hits, hits1, hits_shot, rows = 0, 0, 0, []
    for h in hand['segments']:
        sl = next((s for s in slots if s['f0'] <= h['f0'] <= s['f1']), None)
        if sl is None:
            continue
        th = h['t'] - (h['f0'] - sl['f0']) / fps * h.get('speed', 1.0)     # hand moment at my slot start
        c5 = sl['candidates'][:5]
        ok = [abs(c['t'] - th) <= tol for c in c5]
        ch = sl['chosen']
        hit1 = abs(ch['t'] - th) <= tol
        same_shot = False
        if shot_of is not None:
            hs = shot_of(th + 0.5 * sl['dur'])
            same_shot = any(shot_of(c['t'] + 0.5 * sl['dur']) == hs for c in c5 + [ch])
        hits += any(ok) or hit1
        hits1 += hit1
        hits_shot += same_shot or any(ok) or hit1
        rows.append(dict(hand=h['id'], f0=h['f0'], hand_t=round(h['t'], 2), slot=sl['id'], top5=any(ok) or hit1,
                         rank=(ok.index(True) + 1) if any(ok) else None, chosen=hit1, same_shot=same_shot,
                         nearest=round(min([abs(c['t'] - th) for c in c5] + [abs(ch['t'] - th)]), 2)))
    rep.update(hand_segments=len(rows), top5_hits=hits, top1_hits=hits1, top5_same_shot=hits_shot, tolerance_s=tol,
               per_segment=rows)
    json.dump(_jsonable(rep), open(os.path.join(out_dir, 'compare.json'), 'w'), indent=1)
    return rep


def _music_block(reference, music, music_in=None):
    """audio.music for a separate track: the given in-point, else the offset found by align_music."""
    if not music:
        return None
    if music_in is not None:
        return dict(path=os.path.abspath(music), align='given', **{'in': float(music_in)})
    al = align_music(reference, music)
    if al['aligned']:
        if al['offset'] < 0:
            log(f"music starts {-al['offset']:.2f} s after the reference: it is placed from its first second")
        log(f"music aligned to the reference soundtrack: in = {max(0.0, al['offset']):.3f} s (ncc {al['ncc']}, "
            f"prominence {al['prominence']})")
        return dict(path=os.path.abspath(music), align=al, **{'in': max(0.0, al['offset'])})
    log(f"music does not match the reference soundtrack (ncc {al['ncc']}, prominence {al['prominence']}): it starts "
        f"at 0 s and the cuts keep the reference timing; pass music_in to set the in-point")
    return dict(path=os.path.abspath(music), align=al, **{'in': 0.0})


def draft(reference, footage, out_dir, canvas=(1080, 1920), fps=None, sample_fps=3.0, music=None, music_in=None,
          names=None, survey=True):
    """Reference edit + user footage (one path or a list) -> EDL draft (dict) + edl_draft.json, candidates.json,
    decomposition.json, slots.jpg (+ pages), survey.jpg (+ pages, survey.json). music = a separate track that
    replaces the reference mix (aligned automatically unless music_in is given); names = EDL source names."""
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    paths = [footage] if isinstance(footage, str) else list(footage)
    ref = Reference(reference, fps=fps)
    tracks = _track_masks(ref, _track_words(ref.words, ref.tmask))
    tracks = _refine_tracks(ref, tracks)
    dec = decompose(ref, tracks)
    texts = text_slots(ref, tracks, dec)
    ops = frame_ops(dec, texts)
    log(f'decomposition: {len(dec["slots"])} slots, {len(ops)} ops, {len(texts)} text slots ({time.time() - t0:.0f}s)')
    slots = describe_slots(ref, dec, tracks, texts)
    idx = index_sources(paths, out_dir, sample_fps=sample_fps, names=names)
    total, best_w, terms = score_matrix(slots, idx)
    rank_candidates(slots, idx, total, best_w)
    assign(slots, idx)
    mus = _music_block(reference, music, music_in)
    edl = build_edl(ref, slots, texts, ops, idx, canvas, music=mus)
    edl['meta']['remake_dir'] = os.path.abspath(out_dir)
    json.dump(_jsonable(edl), open(os.path.join(out_dir, 'edl_draft.json'), 'w'), indent=1)
    # candidates.json: everything needed to review and swap
    cj = []
    for si, s in enumerate(slots):
        def cinfo(c):
            k = c['k']
            return dict(t=c['t'], tc=_tc(c['t']), src=_src_name(idx, c), src_i=int(idx['src'][k]), score=c.get('score'),
                        sample=k, shot=c.get('shot'), fits=c.get('fits'),
                        type=TYPES[int(idx['subj'][k][0])], face_h=round(float(idx['subj'][k][1]), 3),
                        subs=bool(idx['subs'][k]), crop=_crop_for(s, c, idx),
                        terms={n_: round(float(v[si, k]), 3) for n_, v in terms.items()})
        cj.append(dict(id=s['id'], f0=s['f0'], f1=s['f1'], frames=s['n'], dur=s['dur'], cut_in=s['cut_in'],
                       link=s.get('link'), bw=s['bw'], tint=s['tint'], L=s['L'], subject=s['subject'], motion=s['motion'],
                       blur=s['blur'], inverted=s['inverted'], flicker=s['flicker'], target=s['target'],
                       chosen=dict(cinfo(s['chosen']), how=s['chosen']['how']),
                       candidates=[cinfo(c) for c in s['cands']]))
    srcs = idx['srcs']
    meta = dict(reference=ref.path, footage=os.path.abspath(paths[0]) if len(paths) == 1 else [os.path.abspath(p) for p in paths],
                footage_list=[os.path.abspath(p) for p in paths], source_names=[s['name'] for s in srcs],
                fps=ref.fps, n_frames=ref.n, ref_size=[ref.w, ref.h], canvas=list(canvas), sample_fps=sample_fps,
                box=srcs[0]['box'], logo=srcs[0]['logo'],
                sources={s['name']: dict(box=s['box'], logo=s['logo'], duration=s.get('duration')) for s in srcs},
                music={k: v for k, v in mus.items()} if mus else None)
    json.dump(_jsonable(dict(meta=meta, slots=cj, texts=texts, ops=ops, frames=dec['frames'])),
              open(os.path.join(out_dir, 'candidates.json'), 'w'), indent=1)
    json.dump(_jsonable(dict(meta=meta, slots=[{k: v for k, v in s.items() if k not in ('cands',) and not k.startswith('_')}
                                               for s in slots], texts=texts, ops=ops, frames=dec['frames'])),
              open(os.path.join(out_dir, 'decomposition.json'), 'w'), indent=1)
    files = contact_sheet(ref, slots, idx, os.path.join(out_dir, 'slots.jpg'))
    if survey:
        sv, entries = survey_sheet(idx, os.path.join(out_dir, 'survey.jpg'))
        files += sv
    log(f'draft: {len(edl["segments"])} segments, {len(edl["texts"])} text items -> {out_dir} ({time.time() - t0:.0f}s); '
        f'sheets {len(files)}')
    return edl


_USAGE = """ed_remake.py - remake a reference edit with your own footage (see the module docstring)

  ed_remake.py REFERENCE FOOTAGE [FOOTAGE ...] OUT_DIR [--music TRACK [--music-in S]] [--canvas 1080x1920] [--fps N]
               [--sample-fps 3] [--compare HAND_EDL.json]                draft EDL + review sheets
  ed_remake.py pick EDL.json OUT_DIR S05=12:34.5 [#7=clip2@1:02.0 ...] [--out NEW.json]   swap slot moments
  ed_remake.py survey FOOTAGE [FOOTAGE ...] --out-dir OUT_DIR [--sample-fps 3]          footage survey sheet only
  ed_remake.py sheet REFERENCE REMAKE.mp4 OUT.jpg [--edl EDL.json]      reference | remake side by side per slot
  ed_remake.py align REFERENCE TRACK                                    where the reference audio sits in TRACK
  ed_remake.py compare OUT_DIR HAND_EDL.json [--tol 1.0]                draft vs a hand-made EDL
  ed_remake.py decompose REFERENCE OUT_DIR [--fps N]                    reference analysis only
"""


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else ''
    if cmd in ('', '-h', '--help'):
        print(_USAGE)
        return 0
    if cmd == 'compare':
        ap = argparse.ArgumentParser(prog='ed_remake.py compare', description='draft vs a hand-made EDL')
        ap.add_argument('out_dir')
        ap.add_argument('hand')
        ap.add_argument('--tol', type=float, default=1.0)
        a = ap.parse_args(argv[1:])
        r = compare(a.out_dir, a.hand, a.tol)
        print(json.dumps({k: v for k, v in r.items() if k != 'per_segment'}, indent=1))
        return 0
    if cmd == 'decompose':
        ap = argparse.ArgumentParser(prog='ed_remake.py decompose', description='reference analysis only')
        ap.add_argument('reference')
        ap.add_argument('out_dir')
        ap.add_argument('--fps', type=float)
        a = ap.parse_args(argv[1:])
        os.makedirs(a.out_dir, exist_ok=True)
        ref = Reference(a.reference, fps=a.fps)
        tracks = _refine_tracks(ref, _track_masks(ref, _track_words(ref.words, ref.tmask)))
        dec = decompose(ref, tracks)
        texts = text_slots(ref, tracks, dec)
        ops = frame_ops(dec, texts)
        json.dump(_jsonable(dict(slots=[{k: v for k, v in s.items() if k != 'content'} for s in dec['slots']],
                                 texts=texts, ops=ops, frames=dec['frames'])),
                  open(os.path.join(a.out_dir, 'decomposition.json'), 'w'), indent=1)
        print('slots', len(dec['slots']), 'cuts', [s['f0'] for s in dec['slots']], 'texts', len(texts))
        return 0
    if cmd == 'pick':
        ap = argparse.ArgumentParser(prog='ed_remake.py pick', description='swap the footage moment of remake slots')
        ap.add_argument('edl')
        ap.add_argument('out_dir', help='the draft folder (candidates.json + footage index)')
        ap.add_argument('picks', nargs='+', help='SLOT=TIME or SLOT=SOURCE@TIME; SLOT = S05 | #5 | 5; TIME = s | m:ss.s')
        ap.add_argument('--out', help='new EDL path (default: overwrite EDL)')
        a = ap.parse_args(argv[1:])
        with open(a.edl) as fh:
            edl = json.load(fh)
        new = repick(edl, a.out_dir, parse_picks(a.picks))
        out = a.out or a.edl
        with open(out, 'w') as fh:
            json.dump(_jsonable(new), fh, indent=1)
        print(out)
        return 0
    if cmd == 'survey':
        ap = argparse.ArgumentParser(prog='ed_remake.py survey', description='footage survey sheet (one tile per shot)')
        ap.add_argument('footage', nargs='+')
        ap.add_argument('--out-dir', required=True)
        ap.add_argument('--sample-fps', type=float, default=3.0)
        a = ap.parse_args(argv[1:])
        os.makedirs(a.out_dir, exist_ok=True)
        idx = index_sources(a.footage, a.out_dir, a.sample_fps)
        files, entries = survey_sheet(idx, os.path.join(a.out_dir, 'survey.jpg'))
        print(json.dumps(dict(files=files, tiles=len(entries)), indent=1))
        return 0
    if cmd == 'sheet':
        ap = argparse.ArgumentParser(prog='ed_remake.py sheet', description='reference | remake side by side per slot')
        ap.add_argument('reference')
        ap.add_argument('remake')
        ap.add_argument('out')
        ap.add_argument('--edl')
        a = ap.parse_args(argv[1:])
        rows = compare_sheet(a.reference, a.remake, a.out, edl=a.edl)
        print(json.dumps(dict(out=a.out, slots=len(rows), flagged=[r['id'] for r in rows if r.get('flag')]), indent=1))
        return 0
    if cmd == 'align':
        ap = argparse.ArgumentParser(prog='ed_remake.py align', description='find the reference audio inside a track')
        ap.add_argument('reference')
        ap.add_argument('track')
        a = ap.parse_args(argv[1:])
        print(json.dumps(align_music(a.reference, a.track), indent=1))
        return 0
    ap = argparse.ArgumentParser(prog='ed_remake.py', usage=_USAGE)
    ap.add_argument('paths', nargs='+', help='REFERENCE FOOTAGE [FOOTAGE ...] OUT_DIR')
    ap.add_argument('--out-dir', help='output folder (then every path after REFERENCE is footage)')
    ap.add_argument('--music', help='separate music track: replaces the reference mix, aligned automatically')
    ap.add_argument('--music-in', type=float, help='music second at output 0 (skips the automatic alignment)')
    ap.add_argument('--canvas', default='1080x1920')
    ap.add_argument('--fps', type=float)
    ap.add_argument('--sample-fps', type=float, default=3.0)
    ap.add_argument('--compare')
    a = ap.parse_args(argv)
    if a.out_dir:
        reference, footage, out_dir = a.paths[0], a.paths[1:], a.out_dir
    else:
        if len(a.paths) < 3:
            ap.error('need REFERENCE FOOTAGE [FOOTAGE ...] OUT_DIR (or --out-dir)')
        reference, footage, out_dir = a.paths[0], a.paths[1:-1], a.paths[-1]
    if not footage:
        ap.error('no footage given')
    w, h = (int(v) for v in a.canvas.lower().split('x'))
    edl = draft(reference, footage, out_dir, canvas=(w, h), fps=a.fps, sample_fps=a.sample_fps, music=a.music,
                music_in=a.music_in)
    print(os.path.join(out_dir, 'edl_draft.json'), 'segments', len(edl['segments']), 'texts', len(edl['texts']))
    if a.compare:
        r = compare(out_dir, a.compare)
        print(json.dumps({k: v for k, v in r.items() if k != 'per_segment'}, indent=1))
    return 0


def parse_picks(items):
    """['S05=12:34.5', '#7=clip2@1:02'] -> {'S05': '12:34.5', '#7': ('clip2', '1:02')}."""
    out = {}
    for it in items:
        if '=' not in it:
            raise ValueError(f'pick {it!r}: use SLOT=TIME or SLOT=SOURCE@TIME')
        k, v = it.split('=', 1)
        out[k.strip()] = tuple(v.split('@', 1)) if '@' in v else v.strip()
    return out


if __name__ == '__main__':
    sys.exit(main())
