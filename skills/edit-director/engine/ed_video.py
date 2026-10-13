#!/usr/bin/env python3
"""Video primitives for the edit engine: probing, frame streams, shot (cut) detection, per-frame features,
faces (YuNet), person masks (PP-HumanSeg / U^2-Net), screen-recording analysis.

API (pixels are source pixels; boxes are [x0, y0, x1, y1], x1/y1 exclusive)
  probe(path) -> {w, h, fps (nominal, like the renderer), duration, hdr, ...} (cached);
  frames(path, t0, t1, fps, width, height, gray, crop) -> (t, frame); colour like the renderer: HDR tone-mapped to
      SDR BT.709, untagged HD read as BT.709
  sample_frames(path, t0, t1, n, width, gray, crop) -> (times, frames): n frames spread over the range; keyframes
      only (intra decode, fast) when the range has enough of them, else seeks / fps sampling
  shot_cuts(path, t0, t1, box=None, fps=None) -> [t, ...] camera cuts (time of the first frame of each new shot)
  content_box(path, t0=None, t1=None) -> [x0, y0, x1, y1]: the live video area inside a screen recording (browser /
      player UI around it) or inside letterbox / pillarbox bars. Static UI, the player's blurred ambient glow and
      transient pop-ups are excluded: temporal activity of the high-passed image (keyframe samples) -> densest
      rectangle (max-sum) -> each edge refined at full resolution by per-frame step-edge votes. An edge without a
      step in most frames (static picture there: calm sky, dark corner) moves outward to the nearest consistent
      step with a dead strip beyond it (bar, UI), else to the frame border; moving bars (stabilised footage) keep
      their always-black part; a shape no video has (aspect outside 0.45..2.8) keeps only black bars. The box is
      inset by 1 px (anti-aliased border) and rounded inward to even numbers (safe for yuv420 crops). Use it as the
      EDL source "box". Full frame when nothing is found. Results of content_box / static_overlays are cached in
      ~/.cache/edit-studio/video (file path + size + mtime + arguments; cache=False recomputes).
  static_overlays(path, box, t0=None, t1=None) -> [{"box", "kind": "logo"|"text"|"ui", "coverage", "spans"}]: persistent
      graphics inside the content (channel logo, sponsor lower third, watermark, system notice). Evidence =
      pixels whose edges stay identical across different camera angles (frames clustered by thumbnail); a static
      scene element only repeats within its own angle. One-angle footage: only graphics over moving content in the
      border zones. kind: "ui" touches the content edge, "logo" sits in a corner, "text" otherwise (lower thirds,
      captions). coverage = share of sampled frames showing it (>= 0.1: graphics shown for part of the range
      count), spans = [[t0, t1], ...] when it is on screen. Boxes are source px (absolute, like `box`).
      kind "popup": a transient UI panel (a recorder / app window, a toast) that appears or goes while the rest of
      the frame stays, keeps still and looks like UI; reported whatever its coverage, with its spans.
  faces(rgb) -> YuNet faces (+ 5 landmarks);  person_mask(rgb) / person_mask_hq(rgb) -> 0..1 maps
  CLI: python3 -I ed_video.py probe|box|overlays|cuts MEDIA [--t0 S --t1 S] [--box x0,y0,x1,y1]
"""
import os, sys, json, math, subprocess
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, 'models')


HDR_TRANSFERS = {'smpte2084': 'pq', 'arib-std-b67': 'hlg'}
_PROBES = {}


def _rate(s):
    try:
        num, den = str(s or '0/1').split('/') if '/' in str(s or '') else (str(s or 0), '1')
        return float(num) / float(den) if float(den) else 0.0
    except ValueError:
        return 0.0


def nominal_fps(r_fps, avg_fps):
    """r_frame_rate when the average rate is within 0.02 % of it (59.998 -> 60), else the average (VFR phones)."""
    if r_fps > 0 and (avg_fps <= 0 or abs(avg_fps - r_fps) <= 2e-4 * r_fps):
        return float(r_fps)
    return float(avg_fps or r_fps or 0.0)


def probe(path):
    """First video stream (+ audio flag) of a media file, cached per path + size + mtime -> dict(path, duration,
    has_audio, w, h (as displayed, rotation applied), fps (nominal: r_frame_rate when the average rate is within
    0.02 % of it - a screen recording's 59.998 is 60 - else the average; same rule as the renderer), avg_fps, r_fps,
    codec, rotation, nb_frames, pix_fmt, color_space, color_transfer, color_primaries, color_range, hdr ('pq'|'hlg'|
    None))."""
    try:
        st = os.stat(path)
        key = (os.path.abspath(path), st.st_mtime_ns, st.st_size)
    except OSError:
        key = None
    if key is not None and key in _PROBES:
        return dict(_PROBES[key])
    out = subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', path],
                         capture_output=True, check=True).stdout
    j = json.loads(out)
    v = next((s for s in j['streams'] if s['codec_type'] == 'video'), None)
    a = next((s for s in j['streams'] if s['codec_type'] == 'audio'), None)
    info = dict(path=path, duration=float(j['format'].get('duration', 0)), has_audio=a is not None)
    if v:
        r_fps, avg = _rate(v.get('r_frame_rate')), _rate(v.get('avg_frame_rate'))
        fps = nominal_fps(r_fps, avg)
        rot = 0
        for sd in v.get('side_data_list', []) or []:
            if 'rotation' in sd:
                rot = int(float(sd['rotation']))
        rot = int(float(v.get('tags', {}).get('rotate', rot)))
        w, h = int(v['width']), int(v['height'])
        if abs(rot) in (90, 270):
            w, h = h, w
        trc = v.get('color_transfer')
        info.update(w=w, h=h, fps=round(fps, 3), avg_fps=round(avg, 4), r_fps=round(r_fps, 4),
                    codec=v.get('codec_name'), rotation=rot, nb_frames=int(v.get('nb_frames', 0) or 0),
                    pix_fmt=v.get('pix_fmt'), color_space=v.get('color_space'), color_transfer=trc,
                    color_primaries=v.get('color_primaries'), color_range=v.get('color_range'),
                    hdr=HDR_TRANSFERS.get(trc))
    if key is not None:
        _PROBES[key] = dict(info)
    return info


_FFILTERS = []


def _ff_filters():
    if not _FFILTERS:
        try:
            out = subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True).stdout
        except OSError:
            out = ''
        _FFILTERS.append({ln.split()[1] for ln in out.splitlines() if ln.startswith(' ') and len(ln.split()) > 2})
    return _FFILTERS[0]


def _scale_vf(info, width, height, gray=False):
    """scale + colour handling like the renderer (ed_edl.FrameReader): HDR (PQ / HLG) tone-mapped to SDR BT.709
    when ffmpeg has zscale + tonemap, untagged HD (yuv, >= 600 lines) read as BT.709; gray frames take luma."""
    sc = f'scale={width}:{height}:flags=area'
    hdr = info.get('hdr')
    if hdr and not gray and {'zscale', 'tonemap'} <= _ff_filters():
        tin = 'smpte2084' if hdr == 'pq' else 'arib-std-b67'
        pin = info.get('color_primaries') if info.get('color_primaries') not in (None, 'unknown') else 'bt2020'
        mtx = info.get('color_space') if info.get('color_space') not in (None, 'unknown') else 'bt2020nc'
        rin = 'full' if info.get('color_range') == 'pc' else 'limited'
        return [sc, f'zscale=tin={tin}:pin={pin}:min={mtx}:rin={rin}:t=linear:npl=100', 'format=gbrpf32le',
                'zscale=p=bt709', 'tonemap=tonemap=hable:desat=0', 'zscale=t=bt709:m=bt709:r=full', 'format=gbrp']
    if not gray and info.get('color_space') in (None, '', 'unknown') and info.get('h', 0) >= 600 and \
            str(info.get('pix_fmt', '')).startswith('yuv'):
        sc += ':in_color_matrix=bt709'
    return [sc]


def frames(path, t0=0.0, t1=None, fps=None, width=None, height=None, gray=False, crop=None, info=None):
    """Yield (t, frame) decoded by ffmpeg. With fps=None frames come at the source rate (cfr-ized).
    crop = [x0, y0, x1, y1] source px (exact, applied before scaling)."""
    info = info or probe(path)
    W, H = info['w'], info['h']
    vf = []
    if crop is not None:
        x0, y0, x1, y1 = [int(round(v)) for v in crop]
        vf.append(f'crop={x1 - x0}:{y1 - y0}:{x0}:{y0}:exact=1')
        W, H = x1 - x0, y1 - y0
    if width and not height:
        height = int(round(H * width / W / 2) * 2)
    if height and not width:
        width = int(round(W * height / H / 2) * 2)
    width, height = width or W, height or H
    rate = fps or info['fps'] or 25.0
    vf += [f'fps={rate}'] + _scale_vf(info, width, height, gray)
    cmd = ['ffmpeg', '-v', 'error', '-nostdin']
    if t0:
        cmd += ['-ss', f'{t0:.4f}']
    cmd += ['-i', path]
    if t1 is not None:
        cmd += ['-t', f'{max(0.0, t1 - t0):.4f}']
    cmd += ['-an', '-vf', ','.join(vf), '-f', 'rawvideo', '-pix_fmt', 'gray' if gray else 'rgb24', '-']
    ch = 1 if gray else 3
    size = width * height * ch
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=size * 4)
    k = 0
    try:
        while True:
            buf = p.stdout.read(size)
            if len(buf) < size:
                break
            fr = np.frombuffer(buf, np.uint8).reshape(height, width) if gray else np.frombuffer(buf, np.uint8).reshape(height, width, 3)
            yield t0 + k / rate, fr
            k += 1
    finally:
        p.stdout.close()
        p.kill()
        p.wait()


# ---------------------------------------------------------------- per-frame features and cuts

def frame_feats(rgb):
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    hist = cv2.calcHist([hsv], [0, 1, 2], None, [16, 4, 4], [0, 180, 0, 256, 0, 256]).flatten()
    hist /= (hist.sum() + 1e-9)
    return dict(g=g, hist=hist, luma=float(g.mean()), sat=float(hsv[..., 1].mean()),
                sharp=float(cv2.Laplacian(g, cv2.CV_32F).var()))


def bhatt(h1, h2):
    return float(np.sqrt(max(0.0, 1.0 - np.sum(np.sqrt(h1 * h2)))))


def detect_cuts(feats, fps, min_shot=0.12):
    """Hard cuts + flash/black transitions from a list of frame_feats. Returns dict with cut frame indices
    (index of the first frame of the new shot), flash frames, black frames and per-pair scores."""
    n = len(feats)
    hd = np.zeros(n)
    pdiff = np.zeros(n)
    for i in range(1, n):
        hd[i] = bhatt(feats[i - 1]['hist'], feats[i]['hist'])
        pdiff[i] = float(np.abs(feats[i]['g'].astype(np.int16) - feats[i - 1]['g'].astype(np.int16)).mean())
    L = np.array([f['luma'] for f in feats])
    # adaptive thresholds from robust statistics
    med_h, mad_h = np.median(hd), np.median(np.abs(hd - np.median(hd))) + 1e-6
    med_p, mad_p = np.median(pdiff), np.median(np.abs(pdiff - np.median(pdiff))) + 1e-6
    score = (hd - med_h) / (6 * mad_h) + (pdiff - med_p) / (6 * mad_p)
    cand = [i for i in range(1, n) if hd[i] > max(0.25, med_h + 6 * mad_h) and pdiff[i] > max(10.0, med_p + 4 * mad_p)]
    # keep local maxima, enforce minimal shot length
    cuts = []
    gap = max(1, int(round(min_shot * fps)))
    for i in sorted(cand, key=lambda k: -score[k]):
        if all(abs(i - c) >= gap for c in cuts):
            cuts.append(i)
    cuts.sort()
    black = [i for i in range(n) if L[i] < 14]
    white = [i for i in range(n) if L[i] > 225]
    flashes = []
    for i in range(1, n - 1):
        lo = np.median(L[max(0, i - 4):i - 0]) if i > 0 else L[i]
        hi = np.median(L[i + 1:min(n, i + 5)]) if i + 1 < n else L[i]
        if L[i] - max(lo, hi) > 40:
            flashes.append(i)
    return dict(cuts=cuts, black=black, white=white, flashes=flashes, hist_d=hd.round(4).tolist(), pix_d=pdiff.round(2).tolist())


# ---------------------------------------------------------------- detectors

_FACE = None
_SEG = None


def face_detector(w, h):
    global _FACE
    if _FACE is None:
        _FACE = cv2.FaceDetectorYN.create(os.path.join(MODELS, 'face_detection_yunet_2023mar.onnx'), '', (w, h), 0.7, 0.3, 50)
    _FACE.setInputSize((w, h))
    return _FACE


def faces(rgb):
    """Return list of faces: dict(x, y, w, h, score) in pixels of the given frame (largest first)."""
    h, w = rgb.shape[:2]
    det = face_detector(w, h)
    n, f = det.detect(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    out = []
    if f is not None:
        for row in f:
            x, y, fw, fh = row[:4]
            # lm: right eye, left eye, nose tip, right mouth corner, left mouth corner (image px)
            out.append(dict(x=float(x), y=float(y), w=float(fw), h=float(fh), score=float(row[-1]),
                            lm=[[float(row[4 + 2 * k]), float(row[5 + 2 * k])] for k in range(5)]))
    out.sort(key=lambda d: -d['w'] * d['h'])
    return out


def person_mask(rgb):
    """PP-HumanSeg person probability map (0..1) resized to the frame."""
    global _SEG
    if _SEG is None:
        _SEG = cv2.dnn.readNetFromONNX(os.path.join(MODELS, 'human_segmentation_pphumanseg_2023mar.onnx'))
    h, w = rgb.shape[:2]
    x = cv2.resize(rgb, (192, 192), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    x = (x - 0.5) / 0.5
    blob = x.transpose(2, 0, 1)[None]
    _SEG.setInput(blob)
    out = _SEG.forward()[0]                      # (2, 192, 192) logits: background, person
    e = np.exp(out - out.max(axis=0, keepdims=True))
    prob = e[1] / e.sum(axis=0)
    return cv2.resize(prob, (w, h), interpolation=cv2.INTER_LINEAR)


def saliency_center(prev_g, g):
    """Fallback point of interest: centroid of frame difference (motion) and edges."""
    d = cv2.GaussianBlur(cv2.absdiff(prev_g, g), (0, 0), 3).astype(np.float32) if prev_g is not None else None
    e = cv2.GaussianBlur(cv2.Laplacian(g, cv2.CV_32F) ** 2, (0, 0), 5)
    m = (d / (d.max() + 1e-6) if d is not None else 0) + 0.3 * e / (e.max() + 1e-6)
    ys, xs = np.indices(g.shape)
    s = m.sum() + 1e-9
    return float((xs * m).sum() / s / g.shape[1]), float((ys * m).sum() / s / g.shape[0])


_U2 = None
_U2_FAILED = False
U2_URL = 'https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx'
U2_SHA256 = '01eb6a29a5c4d8edb30b56adad9bb3a2a0535338e480724a213e0acfd2d1c73c'
CACHE = os.environ.get('EDIT_STUDIO_CACHE', os.path.join(os.environ.get('ED_ROOT', 'C:/Claude Code/cinema-studio/edit'), 'cache'))


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def u2net_path(download=True):
    """U^2-Net weights: engine/models (dev tree) -> ~/.cache/edit-studio/models -> download from the GitHub release
    (176 MB, sha256-verified). None if unavailable (callers fall back to PP-HumanSeg)."""
    for p in (os.path.join(MODELS, 'u2net_human_seg.onnx'), os.path.join(CACHE, 'models', 'u2net_human_seg.onnx')):
        if os.path.exists(p):
            return p
    if not download:
        return None
    import urllib.request
    dst = os.path.join(CACHE, 'models', 'u2net_human_seg.onnx')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    tmp = dst + '.part'
    try:
        print('[ed_video] downloading U^2-Net human segmentation (176 MB, one time) ...', file=sys.stderr)
        urllib.request.urlretrieve(U2_URL, tmp)
        if _sha256(tmp) != U2_SHA256:
            raise RuntimeError('sha256 mismatch')
        os.replace(tmp, dst)
        return dst
    except Exception as e:                              # offline / blocked: fine mask falls back to PP-HumanSeg
        print(f'[ed_video] U^2-Net unavailable ({e}); using PP-HumanSeg', file=sys.stderr)
        try:
            os.remove(tmp)
        except OSError:
            pass
        return None


def person_mask_hq(rgb):
    """U^2-Net human segmentation (rembg weights, Apache-2.0) -> 0..1 map at frame size. Slower, much finer than
    PP-HumanSeg. Weights are fetched on first use (u2net_path); without them this returns person_mask(rgb)."""
    global _U2, _U2_FAILED
    if _U2 is None and not _U2_FAILED:
        p = u2net_path()
        if p is None:
            _U2_FAILED = True
        else:
            import onnxruntime as ort
            so = ort.SessionOptions()
            so.intra_op_num_threads = 2
            _U2 = ort.InferenceSession(p, so, providers=['CPUExecutionProvider'])
    if _U2 is None:
        return person_mask(rgb)
    h, w = rgb.shape[:2]
    x = cv2.resize(rgb, (320, 320), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    x = x / max(float(x.max()), 1e-6)
    x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    out = _U2.run(None, {_U2.get_inputs()[0].name: x.transpose(2, 0, 1)[None]})[0][0, 0]
    out = (out - out.min()) / max(float(out.max() - out.min()), 1e-6)
    return cv2.resize(out, (w, h), interpolation=cv2.INTER_CUBIC).clip(0, 1)


# ---------------------------------------------------------------- sampling over a time range
def _start_time(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=start_time', '-of', 'csv=p=0', path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip().split(',')[0])
    except (ValueError, IndexError):
        return 0.0


def keyframe_times(path, t0=None, t1=None):
    """Times (s, from the file start) of video keyframes in [t0, t1] - a packet scan, nothing is decoded."""
    st = _start_time(path)
    cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'packet=pts_time,flags',
           '-of', 'csv=p=0']
    if t0 is not None or t1 is not None:
        a = max(0.0, (t0 or 0.0) - 1.0) + st
        cmd += ['-read_intervals', f'{a:.3f}%' + (f'{t1 + st + 0.5:.3f}' if t1 is not None else '')]
    cmd.append(path)
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    ts = []
    for line in out.splitlines():
        p = line.split(',')
        if len(p) >= 2 and 'K' in p[1]:
            try:
                ts.append(float(p[0]) - st)
            except ValueError:
                pass
    lo = -1e-3 if t0 is None else t0 - 1e-3
    hi = 1e18 if t1 is None else t1 + 1e-3
    return sorted(t for t in set(ts) if lo <= t <= hi)


def _even_size(w, h, width):
    width = int(min(width or w, w)) // 2 * 2
    return width, max(2, int(round(h * width / w / 2)) * 2)


def sample_frames(path, t0=None, t1=None, n=32, width=960, gray=True, crop=None, info=None):
    """n frames spread over [t0, t1] -> (times, uint8 array (k, h, w[, 3])), k <= n. Keyframes only (intra decode,
    ~10x cheaper than a full decode) when the range holds enough of them; long ranges -> one seek per sample;
    sparse keyframes -> fps sampling. width=None keeps the full (crop) resolution."""
    info = info or probe(path)
    dur = info['duration'] or 0.0
    a = max(0.0, float(t0 or 0.0))
    b = min(dur, float(t1)) if t1 is not None else dur
    if b <= a:
        b = min(dur, a + 1.0)
    W, H = info['w'], info['h']
    vf = []
    if crop is not None:
        x0, y0, x1, y1 = [int(round(v)) for v in crop]
        vf.append(f'crop={x1 - x0}:{y1 - y0}:{x0}:{y0}:exact=1')
        W, H = x1 - x0, y1 - y0
    w, h = _even_size(W, H, width)
    vf += _scale_vf(info, w, h, gray)
    pix, ch = ('gray', 1) if gray else ('rgb24', 3)
    size = w * h * ch
    shape = (h, w) if gray else (h, w, 3)
    kts = keyframe_times(path, a, b)

    def run(cmd):
        raw = subprocess.run(cmd, capture_output=True).stdout
        k = len(raw) // size
        return np.frombuffer(raw[:k * size], np.uint8).reshape((k,) + shape)
    if max(3, n // 2) <= len(kts) <= 4 * n:
        fr = run(['ffmpeg', '-v', 'error', '-nostdin', '-skip_frame', 'nokey', '-ss', f'{a:.3f}', '-i', path,
                  '-t', f'{b - a + 0.02:.3f}', '-an', '-fps_mode', 'passthrough', '-vf', ','.join(vf),
                  '-f', 'rawvideo', '-pix_fmt', pix, '-'])
        ts = [t for t in kts if t >= a - 1e-3][:len(fr)]
        if len(ts) < len(fr):
            ts += list(np.linspace(a, b, len(fr))[len(ts):])
        pick = np.unique(np.linspace(0, len(fr) - 1, min(n, len(fr))).round().astype(int)) if len(fr) else []
        return [round(float(ts[i]), 3) for i in pick], fr[pick] if len(fr) else fr
    if len(kts) > 4 * n:
        pick = [kts[i] for i in np.unique(np.linspace(0, len(kts) - 1, n).round().astype(int))]
        outs, ts = [], []
        for t in pick:
            fr = run(['ffmpeg', '-v', 'error', '-nostdin', '-skip_frame', 'nokey', '-ss', f'{t:.3f}', '-i', path,
                      '-frames:v', '1', '-an', '-vf', ','.join(vf), '-f', 'rawvideo', '-pix_fmt', pix, '-'])
            if len(fr):
                outs.append(fr[0])
                ts.append(round(float(t), 3))
        return ts, (np.stack(outs) if outs else np.zeros((0,) + shape, np.uint8))
    rate = max(n / max(b - a, 1e-3), 0.05)
    ts, outs = [], []
    for t, fr in frames(path, a, b, fps=rate, width=w, height=h, gray=gray, crop=crop, info=info):
        ts.append(round(float(t), 3))
        outs.append(fr.copy())
        if len(outs) >= n:
            break
    return ts, (np.stack(outs) if outs else np.zeros((0,) + shape, np.uint8))


# ---------------------------------------------------------------- shot cuts
def shot_cuts(path, t0=None, t1=None, box=None, fps=None, width=320, min_shot=0.12, info=None):
    """Camera cuts in [t0, t1] (inside `box` when given): times of the first frame of each new shot, decoded at
    the source rate (fps=None) on small frames, detect_cuts rules (histogram + pixel jump, adaptive thresholds)."""
    info = info or probe(path)
    a = float(t0 or 0.0)
    b = float(t1) if t1 is not None else info['duration']
    rate = fps or info['fps'] or 25.0
    feats, times = [], []
    for t, fr in frames(path, a, b, fps=rate, width=width, crop=box, info=info):
        f = frame_feats(fr)
        f['g'] = cv2.resize(f['g'], (64, 36), interpolation=cv2.INTER_AREA)
        feats.append(f)
        times.append(t)
    if len(feats) < 3:
        return []
    res = detect_cuts(feats, rate, min_shot=min_shot)
    first = math.ceil(a * rate - 1e-4) / rate              # exact time of the first decoded source frame
    return [round(first + i / rate, 3) for i in res['cuts'] if 0 < i < len(times)]


# ---------------------------------------------------------------- result cache (~/.cache/edit-studio/video)
ANALYSIS_VERSION = 5


def _cached(kind, path, args, fn):
    """JSON cache of an analysis result keyed by the file (path, size, mtime) and the arguments."""
    import hashlib
    try:
        st = os.stat(path)
        key = hashlib.sha1(json.dumps([kind, os.path.abspath(path), st.st_size, int(st.st_mtime),
                                       ANALYSIS_VERSION, args]).encode()).hexdigest()[:20]
        cp = os.path.join(CACHE, 'video', f'{kind}_{key}.json')
        if os.path.exists(cp):
            with open(cp) as fh:
                return json.load(fh)
    except (OSError, ValueError, TypeError):
        cp = None
    res = fn()
    if cp:
        try:
            os.makedirs(os.path.dirname(cp), exist_ok=True)
            with open(cp, 'w') as fh:
                json.dump(res, fh)
        except (OSError, TypeError):
            pass
    return res


# ---------------------------------------------------------------- content box (screen recordings, letterbox)
def _max_rect(S):
    """maximum-sum axis-aligned rectangle of a 2-D score map -> (y0, y1, x0, x1) inclusive, sum."""
    H, W = S.shape
    best, arg = -np.inf, (0, H - 1, 0, W - 1)
    for i in range(H):
        cs = np.cumsum(S[i:], axis=0)                      # column sums of rows i..j, one row per j
        P = np.concatenate([np.zeros((cs.shape[0], 1)), np.cumsum(cs, axis=1)], axis=1)
        runmin = np.minimum.accumulate(P, axis=1)
        gain = P[:, 1:] - runmin[:, :-1]
        j, x1 = np.unravel_index(int(np.argmax(gain)), gain.shape)
        if gain[j, x1] > best:
            best = float(gain[j, x1])
            x0 = int(np.argmin(P[j, :x1 + 1]))
            arg = (i, i + j, x0, x1)
    return arg, best


def _edge_votes(stack, axis, lo, hi, span):
    """step-edge position voted over frames. stack: (n, H, W) gray; axis 1 = a vertical edge (x), 0 = horizontal;
    lo..hi: search band (the step lies between index-1 and index); span: (a, b) rows/cols along the edge."""
    votes, weights = [], []
    a, b = span
    for fr in stack:
        if axis == 1:
            band = fr[a:b, lo - 1:hi].astype(np.int16)
            g = np.median(np.abs(np.diff(band, axis=1)), axis=0)
        else:
            band = fr[lo - 1:hi, a:b].astype(np.int16)
            g = np.median(np.abs(np.diff(band, axis=0)), axis=1)
        if not len(g):
            continue
        k = int(np.argmax(g))
        if g[k] >= 2.0 and g[k] >= 2.0 * (np.median(g) + 0.5):
            votes.append(lo + k)
            weights.append(float(g[k]))
    if len(votes) < 2:
        return None, len(votes)
    order = np.argsort(votes)
    v, w = np.array(votes)[order], np.array(weights)[order]
    return int(v[np.searchsorted(np.cumsum(w), w.sum() / 2)]), len(votes)


def _edge_profile(stack, axis, lo, hi, span):
    """per position lo..hi: number of frames with a clear step between index-1 and index."""
    a, b = span
    votes = np.zeros(hi - lo, np.int32)
    for fr in stack:
        g = np.median(np.abs(np.diff(fr[a:b, lo - 1:hi].astype(np.int16), axis=1)), axis=0) if axis == 1 else \
            np.median(np.abs(np.diff(fr[lo - 1:hi, a:b].astype(np.int16), axis=0)), axis=1)
        votes += (g >= 2.0) & (g >= 2.0 * (np.median(g) + 0.5))
    return votes


def _dead_strip(small, axis, side, p, dark=False):
    """True when the strip between the frame border and p (small-frame px) is static and flat (UI, bars); dark=True
    also wants it near black (letterbox bars)."""
    n, h, w = small.shape
    if axis == 1:
        st = small[:, int(0.1 * h):int(0.9 * h), :max(1, p)] if side == 0 else small[:, int(0.1 * h):int(0.9 * h), p:]
    else:
        st = small[:, :max(1, p), int(0.1 * w):int(0.9 * w)] if side == 1 else small[:, p:, int(0.1 * w):int(0.9 * w)]
    if st.size == 0:
        return False
    ok = float(np.median(st.std(axis=0))) < 1.0 and float(st.mean(axis=0).std()) < 6.0
    return ok and (not dark or float(st.mean()) < 30.0)


def content_box(path, t0=None, t1=None, n=24, detail=False, cache=True):
    """The live video area of a screen recording / letterboxed frame -> [x0, y0, x1, y1] (see module doc)."""
    if cache:
        box, det = _cached('box', path, [t0, t1, n], lambda: list(content_box(path, t0, t1, n, True, False)))
        return (box, det) if detail else box
    info = probe(path)
    W, H = info['w'], info['h']
    n = max(8, min(n, int(250e6 // max(1, W * H))))        # full-resolution gray frames stay under ~250 MB
    ts, F = sample_frames(path, t0, t1, n=n, width=None, gray=True, info=info)
    full = [0, 0, W, H]
    if len(F) < 3:
        return (full, dict(reason='too few frames', frames=len(F))) if detail else full
    w, h = _even_size(W, H, 960)
    small = np.stack([cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA) for f in F]).astype(np.float32)
    hp = small - np.stack([cv2.GaussianBlur(f, (0, 0), 1.2) for f in small])
    act = hp.std(axis=0)
    mask = (act > 0.3).astype(np.float32)
    g = 4
    M = cv2.resize(mask, (w // g, h // g), interpolation=cv2.INTER_AREA)
    (ry0, ry1, rx0, rx1), _ = _max_rect(M - 0.5)
    sx, sy = W / (w // g), H / (h // g)
    coarse = [rx0 * sx, ry0 * sy, (rx1 + 1) * sx, (ry1 + 1) * sy]
    # refine every edge at full resolution: step votes in a band around the coarse edge
    band = int(max(sx, sy) * 2 + 8)
    xa, xb = int(coarse[0] + 0.1 * (coarse[2] - coarse[0])), int(coarse[2] - 0.1 * (coarse[2] - coarse[0]))
    ya, yb = int(coarse[1] + 0.1 * (coarse[3] - coarse[1])), int(coarse[3] - 0.1 * (coarse[3] - coarse[1]))
    res, votes = [], []
    for k, (c, axis, size, span) in enumerate(((coarse[0], 1, W, (ya, yb)), (coarse[1], 0, H, (xa, xb)),
                                               (coarse[2], 1, W, (ya, yb)), (coarse[3], 0, H, (xa, xb)))):
        c = int(round(c))
        if c <= 1 or c >= size - 1:                       # the frame border itself
            res.append(0 if k < 2 else size)
            votes.append(None)
            continue
        e, nv = _edge_votes(F, axis, max(1, c - band), min(size - 1, c + band), span)
        votes.append(nv)
        need = max(3, 0.3 * len(F))
        if e is not None and nv >= need:                   # a step seen in most frames: the border
            res.append(e)
            continue
        # static picture near the coarse edge (calm shot, dark corner): look outward for a consistent step with a
        # dead strip beyond it (letterbox bar, UI); none -> the frame border
        lo, hi = (1, min(size - 1, c + band)) if k < 2 else (max(1, c - band), size - 1)
        prof = _edge_profile(F, axis, lo, hi, span)
        cands = sorted((lo + int(i) for i in np.nonzero(prof >= need)[0]), reverse=k < 2)
        pick = 0 if k < 2 else size
        for p in cands:
            if _dead_strip(small, axis, k, int(round(p * (w if axis == 1 else h) / size))):
                pick = p
                break
        else:                                              # moving bars (stabilised footage): the dead part
            if _dead_strip(small, axis, k, int(round(c * (w if axis == 1 else h) / size)), dark=True):
                pick = c
        res.append(pick)
    x0, y0, x1, y1 = res
    # 1 px inset (anti-aliased border), inward to even numbers (yuv420 crops), never outside the frame
    x0 = 0 if x0 <= 0 else x0 + 1 + (x0 + 1) % 2
    y0 = 0 if y0 <= 0 else y0 + 1 + (y0 + 1) % 2
    x1 = W if x1 >= W else (x1 - 1) - (x1 - 1) % 2
    y1 = H if y1 >= H else (y1 - 1) - (y1 - 1) % 2
    box = [int(x0), int(y0), int(x1), int(y1)]
    asp = (box[2] - box[0]) / max(1, box[3] - box[1])
    if box[2] - box[0] < 0.2 * W or box[3] - box[1] < 0.2 * H or not 0.45 <= asp <= 2.8:
        # no video has that shape: a static scene fooled the activity map -> keep only black bars
        keep = []
        for k, v in enumerate(res):
            axis = 1 if k % 2 == 0 else 0
            sz = W if axis == 1 else H
            border = 0 if k < 2 else sz
            ok = v != border and _dead_strip(small, axis, k, int(round(v * (w if axis == 1 else h) / sz)), dark=True)
            keep.append(v if ok else border)
        x0, y0, x1, y1 = keep
        x0 = 0 if x0 <= 0 else x0 + 1 + (x0 + 1) % 2
        y0 = 0 if y0 <= 0 else y0 + 1 + (y0 + 1) % 2
        x1 = W if x1 >= W else (x1 - 1) - (x1 - 1) % 2
        y1 = H if y1 >= H else (y1 - 1) - (y1 - 1) % 2
        box = [int(x0), int(y0), int(x1), int(y1)]
    if detail:
        return box, dict(coarse=[int(round(v)) for v in coarse], votes=votes, frames=len(F), times=ts,
                         active_share=round(float(mask.mean()), 3))
    return box


# ---------------------------------------------------------------- static overlays (logos, lower thirds, watermarks)
def _angle_clusters(G, thr=14.0):
    """greedy clustering of frames into camera angles by blurred 32x18 thumbnails (mean abs diff, levels)."""
    th = [cv2.GaussianBlur(cv2.resize(g, (32, 18), interpolation=cv2.INTER_AREA).astype(np.float32), (0, 0), 1)
          for g in G]
    centers, labels = [], []
    for t in th:
        d = [float(np.abs(t - c[0] / c[1]).mean()) for c in centers]
        k = int(np.argmin(d)) if d else -1
        if k >= 0 and d[k] < thr:
            centers[k][0] += t
            centers[k][1] += 1
            labels.append(k)
        else:
            centers.append([t.copy(), 1])
            labels.append(len(centers) - 1)
    return np.array(labels)


def _grad(g):
    return cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)


def _overlay_kind(rx0, ry0, rx1, ry1, touch):
    if touch or ((rx1 - rx0) > 0.6 and (ry1 - ry0) < 0.06):
        return 'ui'
    if (min(rx0, 1 - rx1) < 0.22) and (min(ry0, 1 - ry1) < 0.22) and (rx1 - rx0) < 0.3 and \
            (rx1 - rx0) * (ry1 - ry0) < 0.05:
        return 'logo'
    return 'text'


def _angle_support(G, labels, idx):
    """cross-angle structure agreement of the frames `idx`: (support, flat-agreement, angle pairs used). A pair whose
    agreement is spread over the frame (> 20 % of a 16 x 9 grid) is one camera angle split in two clusters (same
    studio background), not graphics - skipped."""
    h, w = G.shape[1:]
    angles = sorted(set(labels[idx].tolist()))
    med, grads, stable = [], [], []
    for a in angles:
        Ga = G[[i for i in idx if labels[i] == a]]
        m = np.median(Ga, axis=0)
        med.append(m)
        grads.append(_grad(m))
        stable.append((np.abs(Ga - m[None]) < 10.0).mean(axis=0) >= 0.7)
    agree = np.zeros((h, w), bool)
    used = []
    for i in range(len(angles)):
        mi = np.hypot(*grads[i])
        for j in range(i + 1, len(angles)):
            mj = np.hypot(*grads[j])
            diff = np.hypot(grads[i][0] - grads[j][0], grads[i][1] - grads[j][1])
            ok = (mi > 40.0) & (mj > 40.0) & (diff < 0.35 * np.maximum(mi, mj)) & \
                (np.abs(med[i] - med[j]) < 8.0) & stable[i] & stable[j]
            cells = cv2.resize(ok.astype(np.float32), (16, 9), interpolation=cv2.INTER_AREA)
            if float(np.abs(med[i] - med[j]).mean()) < 10.0 or (cells > 0.004).mean() > 0.2 or \
                    ok.sum() > 0.5 * max(1.0, float(((mi > 40.0) | (mj > 40.0)).sum())):
                continue
            agree |= ok
            used.append((i, j))
    flat = None
    if used:
        ids = sorted({k for pr in used for k in pr})
        meds = np.stack([med[k] for k in ids])
        flat = ((meds.max(axis=0) - meds.min(axis=0)) < 6.0) & np.all(np.stack([stable[k] for k in ids]), axis=0)
    return agree, flat, len(used)


def _still_run(D, m, j, step):
    """sample steps the pixels m stay still (mean change <= 1 grey level) from sample j towards `step`"""
    r = 0
    while 0 <= j + step <= len(D) and float(D[min(j, j + step)][m].mean()) <= 1.0:
        r += 1
        j += step
    return r


def _run_end(D, outside, j):
    """what ends a still run at sample step j: 0 a local change (a popup's other end), 1 the range edge, 2 a change
    of the whole frame (a camera cut)"""
    if j < 0 or j > len(D) - 1:
        return 1
    return 0 if float(np.median(D[j][outside])) <= 1.0 else 2


def _axis_share(g, mask, thr=30.0):
    """share of the strong edges on `mask` that run horizontally / vertically (UI: panels, text ~0.5-1; people,
    faces ~0.3); 0 with too few edges (a plain area)"""
    gf = g.astype(np.float32)
    gx, gy = cv2.Sobel(gf, cv2.CV_32F, 1, 0, ksize=3) / 4.0, cv2.Sobel(gf, cv2.CV_32F, 0, 1, ksize=3) / 4.0
    sel = (np.hypot(gx, gy) > thr) & mask
    if sel.sum() < 40:
        return 0.0
    ang = np.degrees(np.arctan2(gy[sel], gx[sel])) % 90.0
    return float(((ang < 10.0) | (ang > 80.0)).mean())


def _popups(path, crop, a, b, info):
    """Transient UI popups (a recorder / app window, a notification toast) inside crop over [a, b] ->
    [(x0, y0, x1, y1, [[t0, t1], ...]) in crop px, ...]. Frames at 4 / s (2 / s over 15 s): a popup appears or goes
    while the rest of the frame stays (not a camera cut), stays pixel-still for at least 2 samples (UI does not
    move; a person who pauses is caught by the next tests), looks like UI - mostly horizontal / vertical edges - and
    is not what the place shows the rest of the time (the background a person uncovers).
    When the region is still on both sides of the change (a toast over a static wall), the side that a local change
    closes wins over an open one (range edge), an open one over one a camera cut ends, else the shorter. Shown for at
    most 60 % of the range."""
    n = int(min(160, max(16, round((4.0 if b - a <= 15.0 else 2.0) * (b - a)))))
    ts, F = sample_frames(path, a, b, n=n, width=480, gray=True, crop=crop, info=info)
    if len(F) < 3:
        return []
    G = np.stack([cv2.GaussianBlur(f.astype(np.float32), (0, 0), 1.0) for f in F])
    nf, h, w = G.shape
    sx, sy = (crop[2] - crop[0]) / w, (crop[3] - crop[1]) / h
    D = [np.abs(G[k] - G[k + 1]) for k in range(nf - 1)]
    Db = [cv2.blur(d, (5, 5)) for d in D]
    big = np.ones((31, 31), np.uint8)
    found = []
    for k in range(nf - 1):
        ch = Db[k] > 18.0
        if not 0.004 <= ch.mean() <= 0.5:
            continue
        around = cv2.dilate(ch.astype(np.uint8), big) == 0
        if not around.any() or float(np.median(D[k][around])) > 1.0:
            continue                                         # the rest of the frame changes too: a camera cut
        for side in ('after', 'before'):
            j = k + 1 if side == 'after' else k - 1          # still on that side for one more sample
            if not 0 <= j <= nf - 2:
                continue
            S = cv2.morphologyEx((ch & (Db[j] < 2.0)).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
            num, lab, st, _ = cv2.connectedComponentsWithStats(S, connectivity=8)
            for c in range(1, num):
                x, y, cw, chh, area = [int(v) for v in st[c]]
                if area < 0.004 * w * h or cw * chh > 0.5 * w * h:
                    continue
                m = lab == c
                outside = cv2.dilate(m.astype(np.uint8), big) == 0
                if side == 'after':
                    r, other = _still_run(D, m, k + 1, +1), _still_run(D, m, k, -1)
                    end = _run_end(D, outside, k + 1 + r)
                    oend = _run_end(D, outside, k - other - 1)
                    i0, i1, fr = k + 1, k + 1 + r, F[k + 1]
                else:
                    r, other = _still_run(D, m, k, -1), _still_run(D, m, k + 1, +1)
                    end = _run_end(D, outside, k - r - 1)
                    oend = _run_end(D, outside, k + 1 + other)
                    i0, i1, fr = k - r, k, F[k]
                if r < 1 or (other >= 1 and (oend, other) < (end, r)):
                    continue                                 # not still here, or the other side is the popup
                # the popup itself = the changed pixels that stay identical over its run; then it extends while
                # they stay still
                core = m & (np.abs(G[i0] - G[i1]) < 2.0)
                if core.sum() < 0.004 * w * h:
                    continue
                if _axis_share(fr, cv2.dilate(core.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) < 0.42:
                    continue                                 # no UI look (a person, a hand, a plain area)
                if side == 'before':
                    i0 -= _still_run(D, core, i0, -1)
                else:
                    i1 += _still_run(D, core, i1, +1)
                core = cv2.morphologyEx(cv2.morphologyEx(core.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)),
                                        cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) > 0
                ys, xs = np.nonzero(core)
                if len(xs) < 0.004 * w * h:
                    continue
                # a popup is a filled rectangle (a person's outline is not) and not what the place usually shows
                # (the background a person uncovers is)
                X0, Y0, X1, Y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
                cm = core[Y0:Y1, X0:X1]
                fill = len(xs) / float((X1 - X0) * (Y1 - Y0))
                straight = sum(v >= 0.6 for v in (1.0 if Y0 <= 1 else cm[:3].any(axis=0).mean(),
                                                  1.0 if Y1 >= h - 1 else cm[-3:].any(axis=0).mean(),
                                                  1.0 if X0 <= 1 else cm[:, :3].any(axis=1).mean(),
                                                  1.0 if X1 >= w - 1 else cm[:, -3:].any(axis=1).mean()))
                if not (straight >= 3 or (straight >= 1 and fill >= 0.74) or fill >= 0.85):
                    continue                                 # not a panel: its outline is not a rectangle
                rest = [q for q in range(nf) if not i0 <= q <= i1]
                if not rest:
                    continue
                usual = np.median(G[rest][:, Y0:Y1, X0:X1], axis=0)
                if float((np.abs(G[i0][Y0:Y1, X0:X1] - usual)[core[Y0:Y1, X0:X1]] > 15.0).mean()) < 0.5:
                    continue
                t_a = a if i0 == 0 else (ts[i0 - 1] + ts[i0]) / 2
                t_b = b if i1 == nf - 1 else (ts[i1] + ts[i1 + 1]) / 2
                if t_b - t_a > 0.6 * (b - a):
                    continue
                found.append([X0, Y0, X1, Y1, t_a, t_b])
    out = []                                                 # one popup per place: its spans merged
    for x0, y0, x1, y1, t_a, t_b in sorted(found, key=lambda f: f[4]):
        for o in out:
            ix = max(0, min(o[2], x1) - max(o[0], x0)) * max(0, min(o[3], y1) - max(o[1], y0))
            if ix >= 0.5 * min((o[2] - o[0]) * (o[3] - o[1]), (x1 - x0) * (y1 - y0)):
                o[:4] = [min(o[0], x0), min(o[1], y0), max(o[2], x1), max(o[3], y1)]
                if o[4][-1][1] >= t_a - 0.6:
                    o[4][-1][1] = max(o[4][-1][1], t_b)
                    o[4][-1][0] = min(o[4][-1][0], t_a)
                else:
                    o[4].append([t_a, t_b])
                break
        else:
            out.append([x0, y0, x1, y1, [[t_a, t_b]]])
    return [(o[0] * sx, o[1] * sy, o[2] * sx, o[3] * sy, o[4]) for o in out
            if sum(t1_ - t0_ for t0_, t1_ in o[4]) <= 0.6 * (b - a)]


def static_overlays(path, box=None, t0=None, t1=None, n=32, min_coverage=0.1, detail=False, debug=None,
                    cache=True):
    """Persistent graphics inside the content box (see module doc) -> [{"box", "kind", "coverage", "spans"}]; boxes
    are absolute source pixels (like `box`; subtract box[0], box[1] for box-relative coordinates), never a near-full
    share of the content (a background is not an overlay). A graphic on screen for part of the range is reported
    too (coverage >= min_coverage); spans = [[t0, t1], ...] when it is visible. Transient UI popups (kind "popup",
    _popups) are reported at any coverage."""
    if cache and not debug:
        ov, det = _cached('overlays', path, [None if box is None else [int(round(v)) for v in box], t0, t1, n,
                                             min_coverage],
                          lambda: list(static_overlays(path, box, t0, t1, n, min_coverage, True, None, False)))
        return (ov, det) if detail else ov
    info = probe(path)
    W, H = info['w'], info['h']
    bx0, by0, bx1, by1 = [int(round(v)) for v in (box or [0, 0, W, H])]
    bw, bh = bx1 - bx0, by1 - by0
    crop = [bx0, by0, bx1, by1]
    ts, F = sample_frames(path, t0, t1, n=n, width=960, gray=True, crop=crop, info=info)
    if len(F) < 4:
        return ([], dict(reason='too few frames')) if detail else []
    G = F.astype(np.float32)
    inside = np.ones(len(G), bool)
    labels = _angle_clusters(G)
    widened = None
    if len(set(labels.tolist())) < 2 and info.get('duration'):
        # one camera angle in the range: look at the neighbouring shots too (graphics outlive a shot); coverage is
        # still measured on the range itself
        a = float(t0 or 0.0)
        b = float(t1) if t1 is not None else info['duration']
        pad = max(20.0, 2.0 * (b - a))
        wa, wb = max(0.0, a - pad), min(info['duration'], b + pad)
        if wb - wa > (b - a) + 1.0:
            ts2, F2 = sample_frames(path, wa, wb, n=n, width=960, gray=True, crop=crop, info=info)
            out_ = [k for k, t in enumerate(ts2) if not a <= t <= b]
            if out_:
                G = np.concatenate([G, F2[out_].astype(np.float32)])
                ts = list(ts) + [ts2[k] for k in out_]
                inside = np.concatenate([inside, np.zeros(len(out_), bool)])
                labels = _angle_clusters(G)
                widened = [round(wa, 3), round(wb, 3)]
    nf, h, w = G.shape
    sx, sy = bw / w, bh / h
    edges = np.stack([np.hypot(*_grad(g)) for g in G]) > 40.0
    # whole range + thirds (graphics shown only part of the time)
    windows = [list(range(nf))] + ([list(range(k * nf // 3, (k + 1) * nf // 3)) for k in range(3)] if nf >= 12 else [])
    support = np.zeros((h, w), bool)
    flat = np.zeros((h, w), bool)
    pairs = 0
    for idx in windows:
        sup, fl, p = _angle_support(G, labels, idx)
        if p:
            support |= sup
            flat |= fl
            pairs += p
    multi = pairs > 0
    if not multi:                                          # one angle: stable structure over moving content
        m = np.median(G[inside], axis=0)
        stable = (np.abs(G[inside] - m[None]) < 10.0).mean(axis=0) >= 0.7
        act = np.stack([cv2.blur(g, (41, 41)) for g in G[inside]]).std(axis=0)
        support = (np.hypot(*_grad(m)) > 40.0) & stable & (act > 6.0)
        flat = None
    dens = cv2.blur(support.astype(np.float32), (9, 9))
    cand = (support & (dens >= 0.12)).astype(np.uint8)
    k = max(3, int(round(0.012 * w)))
    closed = cv2.morphologyEx(cand, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (2 * k + 1, k + 1)))
    num, lab = cv2.connectedComponents(closed, connectivity=8)
    if debug:
        cv2.imwrite(debug, np.hstack([np.clip(dens * 400, 0, 255), cand * 255.0]).astype(np.uint8))
    comps = []
    for c in range(1, num):
        sel = (lab == c) & (cand > 0)
        ys, xs = np.nonzero(sel)
        if len(xs) < 25:
            continue
        x0c, y0c, x1c, y1c = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
        if flat is not None:                               # grow onto the plate the text sits on
            ex, ey = (x1c - x0c) + 2, (y1c - y0c) + 2
            X0, Y0, X1, Y1 = max(0, x0c - ex), max(0, y0c - ey), min(w, x1c + ex), min(h, y1c + ey)
            fl = flat[Y0:Y1, X0:X1].astype(np.uint8)
            seed = cv2.dilate(sel[Y0:Y1, X0:X1].astype(np.uint8), np.ones((5, 5), np.uint8))
            _, flab = cv2.connectedComponents(fl, connectivity=4)
            for q in set(np.unique(flab[(seed > 0) & (fl > 0)]).tolist()) - {0}:
                qy, qx = np.nonzero(flab == q)
                # a plate is closed: flat area running out of the search window (not at the frame edge) is a
                # uniform background shared by the angles (dark studio, black sky), not part of the graphic
                open_ = (qx.min() == 0 and X0 > 0) or (qy.min() == 0 and Y0 > 0) or \
                    (qx.max() == X1 - X0 - 1 and X1 < w) or (qy.max() == Y1 - Y0 - 1 and Y1 < h)
                if len(qx) >= 12 and not open_:
                    x0c, y0c = min(x0c, X0 + int(qx.min())), min(y0c, Y0 + int(qy.min()))
                    x1c, y1c = max(x1c, X0 + int(qx.max()) + 1), max(y1c, Y0 + int(qy.max()) + 1)
        comps.append([x0c, y0c, x1c, y1c, sel])
    # one text line = one overlay ("logo  name   sponsor"): merge neighbours on a line with gaps < 2.5 x height
    merged = True
    while merged:
        merged = False
        for a in range(len(comps)):
            for b in range(a + 1, len(comps)):
                A, B = comps[a], comps[b]
                hgt = max(A[3] - A[1], B[3] - B[1])
                vov = min(A[3], B[3]) - max(A[1], B[1])
                gap = max(A[0], B[0]) - min(A[2], B[2])
                if vov > 0.5 * min(A[3] - A[1], B[3] - B[1]) and gap < 2.5 * hgt:
                    comps[a] = [min(A[0], B[0]), min(A[1], B[1]), max(A[2], B[2]), max(A[3], B[3]), A[4] | B[4]]
                    del comps[b]
                    merged = True
                    break
            if merged:
                break
    out, dropped = [], 0
    idx_in = np.nonzero(inside)[0]
    for x, y, x1c, y1c, sel in comps:
        cw, chh = x1c - x, y1c - y
        if cw < 6 or chh < 4:
            continue
        if (cw > 0.5 * w and chh > 0.35 * h) or cw * chh > 0.4 * w * h:
            dropped += 1                                   # a background shared by two angles, not an overlay
            continue                                       # (a full-width bar - player controls, ticker - stays)
        # a frame shows the graphic when its structure matches another frame from a different angle (or, with one
        # angle, a frame >= 1.5 s away) on at least half of the graphic's pixels; a frame with (almost) no edges on
        # the graphic's own pixels does not show it, whatever a few stray pixels match
        g = G[:, sel]
        e = edges[:, sel]
        need = 0.15 * g.shape[1]
        pres = np.zeros(nf, bool)
        for i in idx_in:
            if e[i].sum() < need:
                continue
            for j in range(nf):
                if i == j or (multi and labels[i] == labels[j]) or (not multi and abs(ts[i] - ts[j]) < 1.5):
                    continue
                hit = (np.abs(g[i] - g[j]) < 12.0) & e[i] & e[j]
                if hit.sum() >= max(need, 0.5 * min(e[i].sum(), e[j].sum()), 0.25 * e[i].sum()):
                    pres[i] = True
                    break
        cov = float(pres[idx_in].mean()) if len(idx_in) else 0.0
        if cov < min_coverage:
            continue
        # when it is on screen: runs of present samples, each widened to half the gap to its neighbours
        tin = [float(ts[i]) for i in idx_in]
        r0 = float(t0) if t0 is not None else 0.0
        r1 = float(t1) if t1 is not None else float(info.get('duration') or (tin[-1] if tin else 0.0))
        spans, run = [], None
        for k, i in enumerate(idx_in):
            if pres[i]:
                lo = r0 if k == 0 else (tin[k - 1] + tin[k]) / 2
                hi = r1 if k == len(tin) - 1 else (tin[k] + tin[k + 1]) / 2
                if run is not None and run[1] >= lo - 1e-6:
                    run[1] = hi
                else:
                    run = [lo, hi]
                    spans.append(run)
            else:
                run = None
        if not multi:
            cxr, cyr = (x + cw / 2) / w, (y + chh / 2) / h
            if 0.25 < cxr < 0.75 and 0.25 < cyr < 0.75:
                continue
        touch = x <= 2 or y <= 2 or x + cw >= w - 2 or y + chh >= h - 2
        pad = 2 + 0.04 * max(cw, chh)
        X0, Y0 = bx0 + max(0.0, (x - pad)) * sx, by0 + max(0.0, (y - pad)) * sy
        X1, Y1 = bx0 + min(float(w), x + cw + pad) * sx, by0 + min(float(h), y + chh + pad) * sy
        kind = _overlay_kind(x / w, y / h, (x + cw) / w, (y + chh) / h, touch)
        out.append(dict(box=[int(np.floor(X0)), int(np.floor(Y0)), int(np.ceil(X1)), int(np.ceil(Y1))], kind=kind,
                        coverage=round(cov, 2), spans=[[round(a, 3), round(b, 3)] for a, b in spans]))
    # transient UI popups (recorder / app windows, toasts): any coverage, with their spans
    r0 = float(t0) if t0 is not None else 0.0
    r1 = float(t1) if t1 is not None else float(info.get('duration') or 0.0)
    pops = []
    if r1 - r0 >= 1.0:
        try:
            pops = _popups(path, crop, r0, r1, info)
        except Exception:                                    # popups are a bonus: never fail the overlays
            pops = []
    for x0, y0, x1, y1, spans in pops:
        X0, Y0, X1, Y1 = bx0 + x0, by0 + y0, bx0 + x1, by0 + y1
        inside_of = [o for o in out if (min(X1, o['box'][2]) - max(X0, o['box'][0])) *
                     (min(Y1, o['box'][3]) - max(Y0, o['box'][1])) >= 0.5 * (X1 - X0) * (Y1 - Y0) and
                     min(X1, o['box'][2]) > max(X0, o['box'][0]) and
                     all(any(a2 - 0.6 <= a_ and b_ <= b2 + 0.6 for a2, b2 in o['spans']) for a_, b_ in spans)]
        if inside_of:                                        # already covered by a static overlay over that time
            continue
        pad = 2.0
        out.append(dict(box=[int(np.floor(max(bx0, bx0 + x0 - pad))), int(np.floor(max(by0, by0 + y0 - pad))),
                             int(np.ceil(min(bx1, bx0 + x1 + pad))), int(np.ceil(min(by1, by0 + y1 + pad)))],
                        kind='popup', coverage=round(sum(b_ - a_ for a_, b_ in spans) / max(1e-6, r1 - r0), 3),
                        spans=[[round(a_, 3), round(b_, 3)] for a_, b_ in spans]))
    out.sort(key=lambda o: (o['box'][1], o['box'][0]))
    if detail:
        return out, dict(frames=int(inside.sum()), frames_total=nf, angles=int(len(set(labels.tolist()))),
                         angle_pairs=pairs, widened=widened, dropped_large=dropped, popups=len(pops),
                         times=[t for t, k in zip(ts, inside) if k])
    return out


# ---------------------------------------------------------------- CLI
def _box_arg(s):
    return [int(float(v)) for v in s.replace(' ', '').split(',')] if s else None


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description='ed_video: probe, content box, static overlays, camera cuts')
    ap.add_argument('cmd', choices=['probe', 'box', 'overlays', 'cuts'])
    ap.add_argument('media')
    ap.add_argument('--t0', type=float)
    ap.add_argument('--t1', type=float)
    ap.add_argument('--box', help='x0,y0,x1,y1 (overlays/cuts; default: content_box)')
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    if a.cmd == 'probe':
        res = probe(a.media)
    elif a.cmd == 'box':
        box, det = content_box(a.media, a.t0, a.t1, detail=True)
        res = dict(box=box, **det)
    elif a.cmd == 'overlays':
        box = _box_arg(a.box) or content_box(a.media, a.t0, a.t1)
        ov, det = static_overlays(a.media, box, a.t0, a.t1, detail=True)
        res = dict(box=box, overlays=ov, **det)
    else:
        res = dict(cuts=shot_cuts(a.media, a.t0, a.t1, box=_box_arg(a.box)))
    s = json.dumps(res, indent=1)
    if a.out:
        with open(a.out, 'w') as fh:
            fh.write(s)
        print('->', a.out)
    print(s if len(s) < 4000 else s[:4000])


if __name__ == '__main__':
    main()
