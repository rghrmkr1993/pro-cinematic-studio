#!/usr/bin/env python3
"""Frame-exact EDL renderer — the Edit Studio core (contract: engine/TIMELINE.md).

python3 -I ed_edl.py EDL.json OUT.mp4 [--preview] [--labels] [--frames 0:120] [--interp nearest|blend|flow]
                     [--workers N] [--fast] [--no-sidecar]
python3 -I ed_edl.py EDL.json --stills SHEET.jpg [--at 5,40,100:160:4 | first] [--preview] [--labels]
python3 -I ed_edl.py EDL.json --validate          # problems (error / warning) of the EDL; exit 1 on errors

API: Renderer(edl, preview, labels, frame_interp, workers, chunk, sidecar, fast).render(out, frame_range, stills,
progress=callable(done, total));
render_edl(edl, out, ...); validate(edl) -> [dict(level 'error'|'warning', where, msg)] (unknown fx / transition /
layer kinds via the ed_fx / ed_text registries, bad ranges, overlaps, missing files...); shift(edl, from_f, delta)
-> new EDL with delta frames inserted before output frame from_f (delta < 0: removed), everything addressed in
output frames or seconds after it moved (music and its beat grid stay; a segment cut by a delete keeps what its
remaining frames showed: in point, speed_curve / crop.path keys, grades, fx frames rebased and trimmed);
probe_source(path) -> stream info; vector_blur(img, flow, span, ...) -> motion blur along an optical flow.

Per output frame f (frame numbers are output frames, inclusive ranges; k = frame index inside a segment):
  segment -> source time (speed | speed_curve | times; continued past f1 / started early inside transition windows)
  -> source frame (nearest | blend | flow interpolation) -> logo inpaint -> crop warp (crop + camera fx folded in;
  motion blur = sub-frame accumulation over the shutter) -> unsharp mask when upscaled -> grade -> image fx -> ghosts
  -> transition_in blend of two segments -> ops (stage pre) -> texts -> layers -> ops (stage post) -> post_text_fx
  -> preview label (big '#N' clip number + output timecode; small: segment id, frame, source time, active moves;
  the sidecar's label_box = its extent in canvas px)
Audio: audio.copy or a legacy {"path"} block -> muxed as is; otherwise ed_sfx.mix() renders a WAV (meta.genre picks
the SFX style) and ed_sfx.encode_audio() makes the delivery AAC 320k whose DECODED true peak / loudness are re-checked
(both in a thread parallel to the video), stream-copied into the MP4; the sidecar 'audio' block has the mix and
'encode' measurements (fallback: the music bed only, loudness-normalised like ed_render.render_audio).
Optional modules (ed_fx, ed_text, ed_sfx) are used when importable; a missing module or function, or a call that
raises, falls back to the built-in code below and is logged once.
Sidecars of a render OUT.mp4: OUT.mp4.render.json (per-frame segment ids, transitions, ops / fx / moves applied,
text and layer bboxes in canvas px, timing, module status) and OUT.boxes.json, the format ed_qa reads: {"canvas":
[W, H], "frames": {"<f>": [[x0, y0, x1, y1, id, kind, flags...]]}} in canvas px — layer ink boxes (kind = layer
kind; 'full' = covers the frame, 'opaque' = hides what is under it) and frame-op boxes (id 'op<i>:<op>', flag 'op',
+ 'full' / 'opaque').
Stage 1 (source, flow interpolation, camera + warp, grade) runs in a thread pool; stage 2 (fx, transitions, ops,
text, layers, labels) runs in output order, so results are identical for any worker count and for partial renders.
Progress on stderr every ED_PROGRESS_S seconds (default 5, 0 = off): frames done / total, %, fps, elapsed, ETA.

Decoding (new EDLs; legacy EDLs keep the first engine's whole-span decode): each segment reads its source through a
FrameReader at its own decode geometry — only the box region its crop windows sample over all its frames (camera
fx, shake, rotation, transition extensions + margin), scaled inside ffmpeg (area filter) to the resolution its most
zoomed-in frame needs, never above the source's: a 4K source in a 540x960 preview is decoded at ~650x1070. The box
crop is exact for any box (even-aligned crop + exact mapping: odd widths no longer skew the picture). Timing is
exact: frame i = time i / fps (fps = the nominal rate when the average is within 0.02 % of it), passthrough sync,
seeks to the midpoint before the wanted frame, so a frame is the same picture whatever the seek point; frames behind
the window or > 2 s ahead are reached by seeking, never by re-reading from the start. Short or non-monotonic spans
(<= ED_HOLD_MB, default 256 MB) stay decoded whole, longer ones stream through a sliding window read ahead by a
background thread. Exposure probes (auto grade) are the segment's own frames at its key frames (decoded alone) or at
k = 0, n/2, n-1: the grade does not depend on the decoding strategy, partial renders or --fast. HDR sources (PQ /
HLG) are tone-mapped to SDR BT.709 in the decode chain (zscale + tonemap, Hable; numpy fallback); untagged HD is
read as BT.709. A still picture can be a source.
Interpolation: segments with a whole number of source frames per output frame (60 fps at 30, speed 1) show source
frames as is; elsewhere 'flow' = DIS optical flow (<= 960 px; --fast <= 480 px) both ways with forward-backward
consistency: visibility-weighted blend of the two warped frames (occlusions taken from the frame that sees them),
the nearest frame at a cut (rebuilding dropped frames of real footage: error 3.0 levels vs 4.1 blend, 5.5 nearest).
Picture: one resampling from the decoded picture to the output (Lanczos near 1:1, bicubic when shrinking, a
half-resolution area level below 0.6x); post-upscale sharpening when a crop is enlarged > 1.1x (sharpen_upscaled:
gentle, from the scale and the source's noise / texture floor, held inside the source's local range — no halo, no
ringing, the Lanczos upscale's own ringing removed too; 'sharpen': 'auto' | false | amount, top level or per
segment; motion-blurred frames stay soft; 'blend' cross-fades are sharpened without coring). Motion
blur: segment 'shutter' (fraction of the frame interval) blurs crop / camera motion (sub-frame warps) and, on frames
played at >= 1.3x (speed ramps, velocity), source time too: the nearer source frame moved along its optical flow
(coarse DIS, <= 480 px) to the moments of shutter x the frame's source step and averaged (vector_blur: one sample
per ~2 output px of motion, at most 24 / 12 preview / 6 --fast) — a smear, not the double contours of cross-faded
neighbour frames (legacy EDLs keep that); move id time.motion_blur; 'time_blur': false | a shutter of its own;
legacy EDLs never get it automatically. Grading as
a fused function + 4096-entry tone table (apply_grade_fast, within 1/16 level of apply_grade). Encode: final = x264
CRF 17, preset slow (ED_CRF / ED_X264_PRESET), previews CRF 20 veryfast (--fast ultrafast); RGB -> YUV 4:2:0 with
the BT.709 matrix, BT.709 tags; canvas fps 23.976 / 29.97 / 59.94 are encoded at the exact 24000/1001 ... rates.
--fast (previews): flow at <= 480 px, 6 motion-blur samples, ultrafast encode; the grade is the same.
Sources: {"path", "box" (picture region, any size), "logo" (inpainted when a crop window comes near it, also at the
picture edge), "mask" (path | {"path", "invert", "channel": "luma"|"alpha", "offset" s, "fps"}: an external subject
matte decoded and warped like the picture; layers get it as ctx person_mask / mask, op mask_flash fills it, ed_fx
gets ctx['mask']), "fps" (override)}.

Legacy EDL (no "meta" block) — fx types of the first engine keep their built-in implementations, so old projects
re-render identically (set "fx_impl": "auto" | "local" to override):
{
 "canvas": {"w": 1080, "h": 1920, "fps": 30}, "n_frames": 521,
 "audio": {"path": "ref.mp4", "copy": true},
 "sources": {"film": {"path": "footage.mp4", "box": [0, 90, 1280, 630], "logo": [1128, 105, 1267, 128]}},
 "segments": [{"id": "A1", "f0": 0, "f1": 13, "src": "film", "t": 303.0, "speed": 1.0,
               "crop": {"cx": .4, "cy": .5, "z": 1.2, "to": {"z": 1.3}, "ease": "inout"},
               "grade": {"preset": "bw_hi", "contrast": 1.3}, "fx": [{"type": "dirblur", "len": .06}]}],
 "ops": [{"f": [0, 6], "op": "invert"}, {"f": [129], "op": "white", "a": .93}],
 "texts": [{"f0": 94, "f1": 96, "items": [{"text": "WHAT", "font": "sans", "size": 78, "x": 318, "y": 700,
            "color": [235, 235, 235], "blend": "normal"}]}]
}
crop: cx, cy are fractions of the picture box (letterbox removed); z = 1 means the 9:16 window spans the full
picture height. "to" animates any of cx/cy/z/rot to the end of the segment (ease: linear|in|out|inout).
New in v2: speed_curve, camera fx, transition_in, layers, op "flash", mixed audio, "shutter" (segment motion blur).
"""
import os, sys, json, math, subprocess, argparse, hashlib, zlib, threading, time, inspect, importlib, tempfile, re
from collections import OrderedDict, deque
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ed_video as V  # noqa: E402

FONT_DIR = os.path.join(HERE, 'assets', 'fonts')
def _sys_or_bundled(sys_path, bundled, var=None):
    """System DejaVu when installed (keeps older renders identical), else a bundled OFL font."""
    return (sys_path, None) if os.path.exists(sys_path) else (os.path.join(FONT_DIR, bundled), var)


FONTS = {
    'sans': _sys_or_bundled('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',
                            'firasansextracondensed_FiraSansExtraCondensed-Bold.ttf'),
    'sans_wide': _sys_or_bundled('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'inter_Inter-VF.ttf', 'Bold'),
    'mono': _sys_or_bundled('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 'jetbrainsmono_JetBrainsMono-VF.ttf', 'Bold'),
    'oswald': (os.path.join(FONT_DIR, 'oswald_Oswald-VF.ttf'), 'Bold'),
    'oswald_semi': (os.path.join(FONT_DIR, 'oswald_Oswald-VF.ttf'), 'SemiBold'),
    'anton': (os.path.join(FONT_DIR, 'anton_Anton-Regular.ttf'), None),
    'bebas': (os.path.join(FONT_DIR, 'bebasneue_BebasNeue-Regular.ttf'), None),
    'montserrat': (os.path.join(FONT_DIR, 'montserrat_Montserrat-VF.ttf'), 'ExtraBold'),
}
_font_cache = {}
_PIL_LOCK = threading.RLock()      # FreeType faces are not thread-safe: all PIL text drawing goes through this lock
_MASK_LOCK = threading.Lock()      # person segmentation models (global sessions in ed_video)
_TEXT_EXT_LOCK = threading.RLock()  # ed_text keeps unsynchronised caches


def font(name, size):
    key = (name, int(size))
    f = _font_cache.get(key)
    if f is None:
        with _PIL_LOCK:
            f = _font_cache.get(key)
            if f is None:
                path, var = FONTS.get(name, (name, None))
                f = ImageFont.truetype(path, int(size))
                if var:
                    f.set_variation_by_name(var)
                _font_cache[key] = f
    return f


# ----------------------------------------------------------------------------- logging / optional modules
_LOGGED = set()
_LOG_LOCK = threading.Lock()


def log(msg):
    print(f'[ed_edl] {msg}', file=sys.stderr, flush=True)


def log_once(key, msg):
    with _LOG_LOCK:
        if key in _LOGGED:
            return
        _LOGGED.add(key)
    log(msg)


def _pool(*entries):
    """Named values for an optional-module call: entries (name, value, 'alias alias ...') -> (values, alias->name)."""
    vals, roots = {}, {}
    for name, value, aliases in entries:
        for a in (name, *aliases.split()):
            if a not in vals:
                vals[a], roots[a] = value, name
    return vals, roots


_BINDABLE = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD,
             inspect.Parameter.KEYWORD_ONLY)


def _bind_call(fn, pool, order, cache):
    """Call fn binding every declared parameter by name from the pool (aliases included); a required parameter with
    an unknown name takes the next unused value of `order` (the documented positional convention)."""
    vals, roots = pool
    params = cache.get(fn, False)
    if params is False:
        try:
            params = [(p.name, p.kind, p.default is not p.empty) for p in inspect.signature(fn).parameters.values()]
        except (TypeError, ValueError):
            params = None
        cache[fn] = params
    if params is None or not any(k in _BINDABLE for _, k, _ in params):
        return fn(*[vals[o] for o in order])
    used = {roots[name] for name, kind, _ in params if kind in _BINDABLE and name in vals}
    queue = [o for o in order if o not in used]
    args, kw = [], {}
    for name, kind, has_default in params:
        if kind not in _BINDABLE:
            continue
        if name in vals:
            v = vals[name]
        elif not has_default:
            if not queue:
                raise TypeError(f'cannot bind parameter {name!r}')
            v = vals[queue.pop(0)]
        else:
            continue
        if kind == inspect.Parameter.POSITIONAL_ONLY:
            args.append(v)
        else:
            kw[name] = v
    return fn(*args, **kw)


class Ext:
    """Optional engine modules owned by other agents, behind guarded imports. A missing module or function, or a
    call that raises, makes the caller fall back to built-in behaviour; each distinct problem is logged once."""

    def __init__(self):
        self._mods, self._sigs, self.stats = {}, {}, {}
        self._lock = threading.RLock()

    def module(self, name):
        if name not in self._mods:
            with self._lock:
                if name not in self._mods:
                    try:
                        m = importlib.import_module(name)
                    except Exception as e:  # missing, or half-written by its owner right now
                        log_once(('import', name), f'{name} not available ({type(e).__name__}: {e}); built-in fallback')
                        m = None
                    self._mods[name] = m
        return self._mods[name]

    def set_module(self, name, mod):
        """Install / replace a module (tests, embedding); None = treat as missing."""
        with self._lock:
            self._mods[name] = mod
            self._sigs.clear()

    def reset(self):
        with self._lock:
            self._mods.clear()
            self._sigs.clear()
            self.stats.clear()

    def fn(self, mod, name):
        m = self.module(mod)
        if m is None:
            return None
        f = getattr(m, name, None)
        if not callable(f):
            log_once(('fn', mod, name), f'{mod}.{name}() not found; built-in fallback')
            return None
        return f

    def attr(self, mod, name, default=None):
        m = self.module(mod)
        return getattr(m, name, default) if m is not None else default

    def has(self, mod, name):
        return self.fn(mod, name) is not None

    def call(self, mod, name, pool, order, check=None, key=None):
        """-> (ok, result). ok False = unavailable or failed (caller falls back)."""
        f = self.fn(mod, name)
        if f is None:
            return False, None
        try:
            res = _bind_call(f, pool, order, self._sigs)
            if check is not None:
                res = check(res)
        except Exception as e:
            with self._lock:
                st = self.stats.setdefault(f'{mod}.{name}', dict(ok=0, fail=0))
                st['fail'] += 1
                st['error'] = f'{type(e).__name__}: {e}'[:300]
            log_once(('call', mod, name, key), f'{mod}.{name}({key or ""}) failed ({type(e).__name__}: {e}); '
                                               f'built-in fallback')
            return False, None
        with self._lock:
            st = self.stats.setdefault(f'{mod}.{name}', dict(ok=0, fail=0))
            st['ok'] += 1
        return True, res

    def status(self):
        out = {}
        for name in ('ed_fx', 'ed_text', 'ed_sfx'):
            m = self._mods.get(name, 'unused')
            out[name] = 'unused' if m == 'unused' else ('ok' if m is not None else 'missing')
        out['calls'] = {k: dict(v) for k, v in sorted(self.stats.items())}
        return out


EXT = Ext()


def _img_check(ref):
    shape = ref.shape

    def chk(y):
        if y is None:
            raise ValueError('returned None')
        y = np.asarray(y)
        if y.shape != shape:
            raise ValueError(f'returned shape {y.shape}, expected {shape}')
        if y.dtype == np.uint8:
            return y.astype(np.float32) / 255.0
        return y if y.dtype == np.float32 else y.astype(np.float32)
    return chk


def _chk_cam(res):
    """ed_fx.camera() -> dict(zoom, dx, dy (output px), rot (deg), blur: None | {'samples': [state, ...], ...})."""
    blur = None
    if isinstance(res, dict):
        v = [float(res.get('zoom', 1.0)), float(res.get('dx', 0.0)), float(res.get('dy', 0.0)), float(res.get('rot', 0.0))]
        b = res.get('blur')
        if isinstance(b, dict) and b.get('samples'):
            blur = b
    else:
        v = [float(a) for a in list(res)[:4]]
        if len(v) < 4:
            raise ValueError(f'camera() returned {res!r}')
    if not all(math.isfinite(a) for a in v) or v[0] <= 0:
        raise ValueError(f'camera() returned {v!r}')
    return dict(zoom=v[0], dx=v[1], dy=v[2], rot=v[3], blur=blur)


def _chk_layer(res):
    if res is None:
        return None
    if isinstance(res, np.ndarray):
        rgba, blend = res, None
    elif isinstance(res, (tuple, list)) and res and isinstance(res[0], np.ndarray):
        rgba, blend = res[0], (res[1] if len(res) > 1 else None)
    else:
        raise ValueError(f'render_layer() returned {type(res).__name__}')
    if rgba.ndim != 3 or rgba.shape[2] != 4:
        raise ValueError(f'layer rgba shape {rgba.shape}')
    return rgba, blend or 'normal'


# ----------------------------------------------------------------------------- easing / helpers
_EASE_ALIAS = {'inquad': 'in', 'outquad': 'out', 'inoutquad': 'inout', 'smooth': 'inout', 'ease': 'inout',
               'outexpo': 'expo_out', 'expoout': 'expo_out'}


def ease(p, kind='linear'):
    p = min(max(p, 0.0), 1.0)
    if kind and kind not in ('linear', 'in', 'out', 'inout', 'expo_out'):
        kind = _EASE_ALIAS.get(str(kind).lower().replace('_', '').replace('-', ''), kind)
    if kind == 'in':
        return p * p
    if kind == 'out':
        return 1 - (1 - p) ** 2
    if kind == 'inout':
        return p * p * (3 - 2 * p)
    if kind == 'expo_out':
        return 1 - 2 ** (-10 * p) if p < 1 else 1.0
    if kind in ('in_cubic', 'incubic'):
        return p ** 3
    if kind in ('out_cubic', 'outcubic'):
        return 1 - (1 - p) ** 3
    if kind in ('inout_cubic', 'inoutcubic'):
        return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2
    if kind in ('in_expo', 'inexpo', 'expo_in'):
        return 0.0 if p == 0 else 2 ** (10 * p - 10)
    if kind == 'hold':
        return 0.0 if p < 1 else 1.0
    return p


def frange(spec):
    """int -> [int]; 'a:b' -> a..b inclusive; list of ints/'a:b' strings -> flattened."""
    if spec is None:
        return []
    if isinstance(spec, (int, np.integer)):
        return [int(spec)]
    if isinstance(spec, float):
        return [int(round(spec))]
    if isinstance(spec, str):
        if ':' in spec:
            a, b = spec.split(':')[:2]
            return list(range(int(a), int(b) + 1))
        return [int(spec)]
    out = []
    for v in spec:
        out += frange(v)
    return out


def luma(x):
    return x[..., 0] * 0.2126 + x[..., 1] * 0.7152 + x[..., 2] * 0.0722


NAMED_COLORS = {'white': (1, 1, 1), 'black': (0, 0, 0), 'red': (1, 0.1, 0.1), 'green': (0.1, 1, 0.2),
                'blue': (0.15, 0.3, 1), 'yellow': (1, 0.9, 0.1), 'cyan': (0.1, 0.95, 1), 'magenta': (1, 0.15, 0.85),
                'orange': (1, 0.55, 0.1), 'warm': (1, 0.82, 0.6), 'cool': (0.65, 0.8, 1)}


def color01(c, default=(1.0, 1.0, 1.0)):
    """[r, g, b] in 0..1 or 0..255, '#rrggbb' or a basic colour name -> float32 (3,)."""
    if c is None:
        return np.array(default, np.float32)
    if isinstance(c, str):
        s = c.strip().lower()
        if s in NAMED_COLORS:
            return np.array(NAMED_COLORS[s], np.float32)
        if s.startswith('#') and len(s) in (4, 7):
            s = s[1:]
            if len(s) == 3:
                s = ''.join(ch * 2 for ch in s)
            return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0
        return np.array(default, np.float32)
    if isinstance(c, (int, float)):
        c = [c, c, c]
    v = np.array(list(c)[:3], np.float32)
    return v / 255.0 if v.max() > 1.0 else v


def move_id(d, fallback=None):
    return str(d.get('move') or d.get('id') or d.get('type') or d.get('op') or d.get('kind') or fallback or '?')


# ----------------------------------------------------------------------------- time mapping
def _rate_G(pts, x):
    """Signed integral of a piecewise-linear rate (held flat outside its keys) from the first key to x."""
    k0, r0 = pts[0]
    if x <= k0:
        return r0 * (x - k0)
    acc = 0.0
    for (ka, ra), (kb, rb) in zip(pts, pts[1:]):
        if x <= kb:
            rx = ra + (rb - ra) * (x - ka) / (kb - ka) if kb > ka else rb
            return acc + (ra + rx) * 0.5 * (x - ka)
        acc += (ra + rb) * 0.5 * (kb - ka)
    kl, rl = pts[-1]
    return acc + rl * (x - kl)


def rate_integral(curve, k):
    """Integral of the rate curve [[k, rate], ...] (segment-relative k, linear between keys, flat outside) over
    [0, k], in output frames; negative k integrates backwards."""
    pts = sorted((float(p[0]), float(p[1])) for p in curve)
    return _rate_G(pts, float(k)) - _rate_G(pts, 0.0)


def seg_time(seg, k, fps):
    """Source time (s) of segment-relative output frame k (int or fractional, may lie outside 0..n-1:
    transitions continue a segment past f1 and start the next one early at its edge rate)."""
    ts = seg.get('times')
    if ts:
        n = len(ts)
        sp = seg.get('speed', 1.0)
        if 0 <= k <= n - 1:
            if float(k).is_integer():
                return float(ts[int(k)])
            return float(np.interp(k, np.arange(n), np.asarray(ts, float)))
        if k < 0:
            return float(ts[0]) + k * sp / fps
        return float(ts[-1]) + (k - (n - 1)) * sp / fps
    curve = seg.get('speed_curve')
    if curve:
        return seg['t'] + rate_integral(curve, k) / fps
    return seg['t'] + (k / fps) * seg.get('speed', 1.0)


def seg_times(seg, fps, k0=0, k1=None):
    """Source times of frames k0..k1 (default the whole segment)."""
    if k1 is None:
        k1 = seg['f1'] - seg['f0']
    return [seg_time(seg, k, fps) for k in range(k0, k1 + 1)]


# ----------------------------------------------------------------------------- source probing
_PROBES, _PROBE_LOCK = {}, threading.Lock()
_KEYFRAMES, KF_CHUNK_S = {}, 60.0          # (path, chunk) -> key-frame times (s) of that 60 s chunk
HDR_TRANSFERS = {'smpte2084': 'pq', 'arib-std-b67': 'hlg'}
IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff')
_IMAGE_FORMATS = ('image2', 'png_pipe', 'jpeg_pipe', 'webp_pipe', 'bmp_pipe', 'tiff_pipe')


def _rate(s):
    """'num/den' or a number -> float (0.0 when unknown)."""
    try:
        if isinstance(s, str) and '/' in s:
            a, b = s.split('/', 1)
            return float(a) / float(b) if float(b) else 0.0
        return float(s or 0.0)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


def probe_source(path):
    """First video stream of a media file (cached per path + mtime) -> dict(w, h (as displayed: rotation applied,
    like ffmpeg's autorotate), fps (nominal: r_frame_rate when the average rate is within 0.02 % of it — a screen
    recording's 59.998 is 60 — else the average), duration, nb_frames, t_off (video start - file start, s), pix_fmt,
    codec, color_space, color_transfer, color_primaries, color_range, rotation, hdr ('pq' | 'hlg' | None),
    image (a still picture), has_audio)."""
    try:
        st = os.stat(path)
        key = (os.path.abspath(path), st.st_mtime_ns, st.st_size)
    except OSError:
        key = (os.path.abspath(path), None, None)
    with _PROBE_LOCK:
        hit = _PROBES.get(key)
    if hit is not None:
        return hit
    r = subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', path],
                       capture_output=True)
    if r.returncode:
        raise RuntimeError(f"ffprobe failed on {path}: {r.stderr.decode(errors='replace')[-300:]}")
    j = json.loads(r.stdout or b'{}')
    streams = j.get('streams') or []
    v = next((s for s in streams if s.get('codec_type') == 'video'), None)
    if v is None:
        raise RuntimeError(f'no video stream in {path}')
    fmt = j.get('format') or {}
    rot = 0
    for sd in v.get('side_data_list') or []:
        if 'rotation' in sd:
            rot = int(float(sd['rotation']))
    rot = int(float((v.get('tags') or {}).get('rotate', rot)))
    w, h = int(v['width']), int(v['height'])
    if abs(rot) % 180 == 90:
        w, h = h, w
    r_fps, avg = _rate(v.get('r_frame_rate')), _rate(v.get('avg_frame_rate'))
    fps = r_fps if r_fps > 0 and (avg <= 0 or abs(avg - r_fps) <= 2e-4 * r_fps) else (avg or r_fps or 25.0)
    nb = int(v.get('nb_frames') or 0)
    dur = float(fmt.get('duration') or v.get('duration') or 0.0)
    image = (str(path).lower().endswith(IMAGE_EXT) or fmt.get('format_name') in _IMAGE_FORMATS
             or (nb == 1 and dur <= 0.1))
    trc = v.get('color_transfer')
    info = dict(path=path, w=w, h=h, fps=float(fps), avg_fps=avg, r_fps=r_fps, duration=dur, nb_frames=nb,
                t_off=max(0.0, float(v.get('start_time') or 0.0) - float(fmt.get('start_time') or 0.0)),
                pix_fmt=v.get('pix_fmt'), codec=v.get('codec_name'), color_space=v.get('color_space'),
                color_transfer=trc, color_primaries=v.get('color_primaries'), color_range=v.get('color_range'),
                rotation=rot, hdr=HDR_TRANSFERS.get(trc), image=bool(image),
                has_audio=any(s.get('codec_type') == 'audio' for s in streams))
    with _PROBE_LOCK:
        _PROBES[key] = info
    return info


_FILTERS = []


def ff_filters():
    """Names of the filters of the installed ffmpeg (cached)."""
    if not _FILTERS:
        try:
            out = subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True).stdout
        except OSError:
            out = ''
        _FILTERS.append({ln.split()[1] for ln in out.splitlines() if ln.startswith(' ') and len(ln.split()) > 2})
    return _FILTERS[0]


# PQ / HLG -> SDR BT.709 in numpy (used when ffmpeg has no zscale + tonemap): linear light (1.0 = 100 nits),
# BT.2020 -> BT.709 primaries, Hable curve on the max component (calibrated to the ffmpeg chain), BT.709 transfer.
_M2020_709 = np.array([[1.6605, -0.5876, -0.0728], [-0.1246, 1.1329, -0.0083], [-0.0182, -0.1006, 1.1187]], np.float32)


def _hable(x):
    A, B, C, D, E, F = 0.15, 0.50, 0.10, 0.20, 0.02, 0.30
    return (x * (A * x + C * B) + D * E) / (x * (A * x + B) + D * F) - E / F


def tonemap_np(rgb16, hdr):
    """rgb48 (H, W, 3) uint16 in the HDR signal domain (PQ or HLG, BT.2020) -> SDR BT.709 rgb24 uint8."""
    e = rgb16.astype(np.float32) / 65535.0
    if hdr == 'pq':
        m1, m2, c1, c2, c3 = 0.1593017578125, 78.84375, 0.8359375, 18.8515625, 18.6875
        p = np.power(np.clip(e, 0, 1), 1.0 / m2)
        lin = np.power(np.maximum(p - c1, 0) / (c2 - c3 * p), 1.0 / m1) * 100.0       # 1.0 = 100 nits
    else:                                                                            # HLG, 1000-nit display
        a, b, c = 0.17883277, 0.28466892, 0.55991073
        s = np.where(e <= 0.5, e * e / 3.0, (np.exp((e - c) / a) + b) / 12.0)
        y = np.maximum(s @ np.array([0.2627, 0.6780, 0.0593], np.float32), 1e-6)[..., None]
        lin = s * np.power(y, 0.2) * 10.0
    lin = np.maximum(lin @ _M2020_709.T, 0.0)
    sig = np.maximum(lin.max(axis=2, keepdims=True), 1e-6)       # like ffmpeg's tonemap: scale by the max component
    sdr = np.clip(lin * (_hable(sig) / _hable(np.float32(4.5)) / sig), 0, 1)   # ~ zscale+tonemap (+-8 levels)
    v = np.where(sdr < 0.018, 4.5 * sdr, 1.099 * np.power(sdr, 0.45) - 0.099)
    return (np.clip(v, 0, 1) * 255.0 + 0.5).astype(np.uint8)


def fps_arg(fps):
    """ffmpeg rate for an output fps: NTSC rates given as 23.976 / 29.97 / 59.94 -> 24000/1001 ... (exact), else the
    number."""
    fps = float(fps)
    n = round(fps * 1.001)
    if n > 0 and abs(fps - n * 1000.0 / 1001.0) < 5e-3 and abs(fps - round(fps)) > 1e-6:
        return f'{n * 1000}/1001'
    return str(int(fps)) if float(fps).is_integer() else repr(fps)


def compose(M, D):
    """2x3 affine M applied after the 2x3 affine D (M o D)."""
    M, D = np.asarray(M, np.float64), np.asarray(D, np.float64)
    return np.hstack([M[:, :2] @ D[:, :2], (M[:, :2] @ D[:, 2] + M[:, 2])[:, None]])


def _even_in(a, b):
    """Even-aligned [a', b') inside [a, b) (crops of 4:2:0 pictures stay exact); [a, b) when too small."""
    a2, b2 = int(math.ceil(a / 2.0)) * 2, int(math.floor(b / 2.0)) * 2
    return (a2, b2) if b2 > a2 else (int(math.floor(a)), int(math.ceil(b)))


class Geom:
    """What a frame reader delivers: the region (x, y, w, h) of the file's picture (file px, as displayed) scaled to
    (dw, dh). dec_to_box() maps delivered px to source-box px (pixel centres aligned like ffmpeg's scaler; k = source
    frame px per file px, 1 except for masks of another resolution)."""
    __slots__ = ('x', 'y', 'w', 'h', 'dw', 'dh', 'sx', 'sy', 'bx', 'by', 'kx', 'ky', 'key')

    def __init__(self, x, y, w, h, dw=None, dh=None, bx=0, by=0, kx=1.0, ky=1.0):
        self.x, self.y, self.w, self.h = int(x), int(y), max(1, int(w)), max(1, int(h))
        self.dw, self.dh = max(1, int(dw or self.w)), max(1, int(dh or self.h))
        self.sx, self.sy = self.dw / self.w, self.dh / self.h
        self.bx, self.by, self.kx, self.ky = bx, by, float(kx), float(ky)
        self.key = (self.x, self.y, self.w, self.h, self.dw, self.dh)

    @property
    def scaled(self):
        return (self.dw, self.dh) != (self.w, self.h)

    def dec_to_box(self):
        ax, ay = self.kx / self.sx, self.ky / self.sy
        return np.array([[ax, 0.0, 0.5 * ax + self.x * self.kx - 0.5 - self.bx],
                         [0.0, ay, 0.5 * ay + self.y * self.ky - 0.5 - self.by]])

    def box_edges(self, x0, y0, x1, y1):
        """Box-px rectangle (pixel edges) -> delivered-px rectangle (floats)."""
        fx, fy = self.sx / self.kx, self.sy / self.ky
        return ((x0 + self.bx) * fx - self.x * self.sx, (y0 + self.by) * fy - self.y * self.sy,
                (x1 + self.bx) * fx - self.x * self.sx, (y1 + self.by) * fy - self.y * self.sy)


def _read_exact(fh, n):
    """n bytes from a pipe (None at end of stream)."""
    buf = bytearray(n)
    view, got = memoryview(buf), 0
    while got < n:
        k = fh.readinto(view[got:])
        if not k:
            return None
        got += k
    return buf


def _kill(proc):
    if proc is not None:
        try:
            proc.stdout.close()
        except (OSError, AttributeError):
            pass
        try:
            proc.kill()
            proc.wait()
        except OSError:
            pass


class FrameReader:
    """Frames of one media file at one decode geometry, by global frame index (time = index / fps from the first
    frame of the stream).

    A background thread reads one ffmpeg process sequentially into a window: from `keep` frames behind the furthest
    request to `ahead` frames beyond it (hold=True: every frame from the start index on, for short spans that are
    re-read: exposure probes, reverse play, ghosts). A frame behind the window, or more than JUMP_S seconds ahead of
    the read position, is reached by seeking — an accurate seek to the midpoint before the wanted frame, so a frame
    is the same picture whatever the seek point — never by re-reading from the start. Crop and scale happen inside
    ffmpeg (exact even-aligned crop, area scaling), HDR (PQ / HLG) is tone-mapped to SDR BT.709, untagged HD is read
    as BT.709. kind: 'rgb' (H, W, 3) | 'gray' | 'alpha' (H, W) uint8."""
    JUMP_S = 2.0

    def __init__(self, path, info, geom, fps=None, start=0, keep=48, ahead=6, hold=False, kind='rgb', hq=False):
        self.path, self.info, self.geom = path, info, geom
        self.fps = float(fps or info['fps'])
        self.start, self.keep, self.ahead, self.hold = max(0, int(start)), int(keep), max(2, int(ahead)), bool(hold)
        self.kind, self.hq = kind, bool(hq)
        self.np_hdr = kind == 'rgb' and info.get('hdr') and not {'zscale', 'tonemap'} <= ff_filters()
        self.ch = 3 if kind == 'rgb' else 1
        self.nbytes = geom.dw * geom.dh * self.ch * (2 if self.np_hdr else 1)
        self.cv = threading.Condition()
        self.buf = {}
        self.pos, self.want, self.eof, self.err = None, -1, None, None
        self.proc, self.gen = None, 0
        self.side, self.side_lock = OrderedDict(), threading.Lock()
        self.n_decoded, self.n_seeks, self.n_starts, self.decode_s = 0, 0, 0, 0.0
        self._still = None

    # ------------------------------------------------------------------ ffmpeg command
    def vf(self):
        g, info = self.geom, self.info
        W, H = info['w'], info['h']
        chain = []
        if (g.x, g.y, g.w, g.h) != (0, 0, W, H):
            chain.append(f'crop={g.w}:{g.h}:{g.x}:{g.y}:exact=1')
        hdr = info.get('hdr') if self.kind == 'rgb' else None
        flags = 'area+accurate_rnd+full_chroma_int' if self.hq else 'area'
        if hdr and not self.np_hdr:
            if g.scaled:
                chain.append(f'scale={g.dw}:{g.dh}:flags={flags}')
            tin = 'smpte2084' if hdr == 'pq' else 'arib-std-b67'
            pin = info.get('color_primaries') if info.get('color_primaries') not in (None, 'unknown') else 'bt2020'
            mtx = info.get('color_space') if info.get('color_space') not in (None, 'unknown') else 'bt2020nc'
            rin = 'full' if info.get('color_range') == 'pc' else 'limited'
            chain += [f'zscale=tin={tin}:pin={pin}:min={mtx}:rin={rin}:t=linear:npl=100', 'format=gbrpf32le',
                      'zscale=p=bt709', 'tonemap=tonemap=hable:desat=0', 'zscale=t=bt709:m=bt709:r=full',
                      'format=gbrp', 'format=rgb24']
            return ','.join(chain)
        sc = f'scale={g.dw}:{g.dh}:flags={flags}'
        if self.kind == 'rgb':
            cs = info.get('color_space')
            if self.np_hdr:
                sc += ':in_color_matrix=bt2020'
            elif cs in (None, '', 'unknown') and info['h'] >= 600 and str(info.get('pix_fmt', '')).startswith('yuv'):
                sc += ':in_color_matrix=bt709'           # untagged HD: BT.709, like players assume
        chain.append(sc)
        if self.kind == 'alpha':
            chain.append('alphaextract')
        chain.append({'rgb': 'format=rgb48le' if self.np_hdr else 'format=rgb24'}.get(self.kind, 'format=gray'))
        return ','.join(chain)

    def cmd(self, i0, count=None, keyframes=False):
        t = self.info.get('t_off', 0.0) + (i0 - 0.5) / self.fps
        c = ['ffmpeg', '-v', 'error', '-nostdin']
        if keyframes:
            c += ['-skip_frame', 'nokey']
        if i0 > 0 and t > 0:
            c += ['-ss', f'{t:.6f}']
        c += ['-i', self.path, '-map', '0:v:0', '-an', '-sn', '-dn', '-vf', self.vf(), '-fps_mode', 'passthrough']
        if count:
            c += ['-frames:v', str(int(count))]
        pix = 'rgb48le' if self.np_hdr else ('rgb24' if self.kind == 'rgb' else 'gray')
        return c + ['-f', 'rawvideo', '-pix_fmt', pix, '-']

    def _frame(self, raw):
        g = self.geom
        if self.np_hdr:
            return tonemap_np(np.frombuffer(raw, '<u2').reshape(g.dh, g.dw, 3), self.info['hdr'])
        a = np.frombuffer(raw, np.uint8)
        return a.reshape(g.dh, g.dw, 3) if self.ch == 3 else a.reshape(g.dh, g.dw)

    def _popen(self, cmd):
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)

    # ------------------------------------------------------------------ sequential stream
    def _restart(self, i0):
        """(lock held) Kill the running process, start a new one at frame i0."""
        self.gen += 1
        _kill(self.proc)
        if not self.hold:
            self.buf.clear()
        self.proc = self._popen(self.cmd(i0))
        self.pos, self.n_starts = i0, self.n_starts + 1
        threading.Thread(target=self._pump, args=(self.proc, self.gen, i0), daemon=True,
                         name='edl-reader').start()

    def _pump(self, proc, gen, i):
        try:
            while True:
                with self.cv:
                    while gen == self.gen and i > self.want + self.ahead:
                        self.cv.wait()
                    if gen != self.gen:
                        return
                tic = time.perf_counter()
                raw = _read_exact(proc.stdout, self.nbytes)
                fr = self._frame(raw) if raw is not None else None
                dt = time.perf_counter() - tic
                with self.cv:
                    if gen != self.gen:
                        return
                    self.decode_s += dt
                    if fr is None:
                        self.eof = i - 1
                        self.cv.notify_all()
                        return
                    self.buf[i] = fr
                    self.n_decoded += 1
                    i += 1
                    self.pos = i
                    if not self.hold:
                        lo = self.want - self.keep
                        for j in [j for j in self.buf if j < lo]:
                            del self.buf[j]
                    self.cv.notify_all()
        except Exception as e:  # noqa: BLE001 — surfaced to the caller of get()
            with self.cv:
                if gen == self.gen:
                    self.err = e
                    self.cv.notify_all()

    def still(self):
        """The single frame of a picture file."""
        if self._still is None:
            p = subprocess.run(self.cmd(0, count=1), capture_output=True)
            raw = p.stdout[:self.nbytes] if len(p.stdout) >= self.nbytes else None
            if raw is None:
                raise RuntimeError(f'cannot decode {self.path}')
            self._still = self._frame(raw)
        return self._still

    def get(self, i):
        """Frame with global index i (None past the end of the stream)."""
        if self.info.get('image'):
            return self.still()
        i = max(0, int(i))
        jump = self.JUMP_S * self.fps
        with self.cv:
            while True:
                f = self.buf.get(i)
                if f is not None:
                    return f
                if self.err is not None:
                    raise RuntimeError(f'decoding {self.path} failed: {self.err!r}')
                if self.eof is not None and i > self.eof:
                    return None
                if self.pos is None:                         # nothing running: start at the span start if near
                    near = self.start <= i and (self.hold or i <= self.start + jump)
                    self._restart(self.start if near else i)
                elif i >= self.pos:
                    if i > self.pos + jump and not self.hold:     # far ahead: seek instead of decoding through
                        self._restart(i)
                else:
                    break                                    # behind the window (evicted / before the start): seek
                self.want = max(self.want, i)
                self.cv.notify_all()
                self.cv.wait(5.0)
        with self.side_lock:
            f = self.side.get(i)
        if f is not None:
            return f
        last, self._last_fetch = getattr(self, '_last_fetch', None), i
        if last is not None and 0 < last - i <= 2:           # walking backwards: decode a chunk behind it at once
            return self.fetch(range(max(0, i - 23), i + 1), keep_side=64).get(i)
        return self.fetch([i]).get(i)

    def fetch(self, idx, keep_side=16):
        """Frames idx (any order) by seeking: one accurate seek per run of nearby indices -> {i: frame}."""
        if self.info.get('image'):
            return {int(i): self.still() for i in idx}
        want = sorted({max(0, int(i)) for i in idx})
        out = {}
        with self.side_lock:
            for i in want:
                if i in self.side:
                    out[i] = self.side[i]
                    self.side.move_to_end(i)
            need = [i for i in want if i not in out]
            runs = []
            for i in need:
                if runs and i - runs[-1][-1] <= 12:
                    runs[-1].append(i)
                else:
                    runs.append([i])
            for run in runs:
                tic = time.perf_counter()
                p = self._popen(self.cmd(run[0], count=run[-1] - run[0] + 1))
                try:
                    for j in range(run[0], run[-1] + 1):
                        raw = _read_exact(p.stdout, self.nbytes)
                        if raw is None:
                            with self.cv:
                                self.eof = j - 1 if self.eof is None else min(self.eof, j - 1)
                            break
                        if j in run:
                            out[j] = self.side[j] = self._frame(raw)
                finally:
                    _kill(p)
                with self.cv:
                    self.n_seeks += 1
                    self.decode_s += time.perf_counter() - tic
            while len(self.side) > max(keep_side, len(want)):
                self.side.popitem(last=False)
        return out

    def keyframe_list(self, t0, t1):
        """Indices of the key frames with source time in [t0, t1], from the container index (nothing decoded;
        read per 60 s chunk of the file and cached for every reader of the file)."""
        off = self.info.get('t_off', 0.0)
        ks = set()
        for c in range(max(0, int(math.floor(t0 / KF_CHUNK_S))), int(math.floor(t1 / KF_CHUNK_S)) + 1):
            key = (os.path.abspath(self.path), c)
            with _PROBE_LOCK:
                pts = _KEYFRAMES.get(key)
            if pts is None:
                a, b = off + c * KF_CHUNK_S, off + (c + 1) * KF_CHUNK_S
                r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-read_intervals',
                                    f'{max(0.0, a - 0.5):.3f}%{b + 0.5:.3f}', '-show_entries', 'packet=pts_time,flags',
                                    '-of', 'csv=p=0', self.path], capture_output=True, text=True)
                pts = []
                for ln in r.stdout.split():
                    parts = ln.split(',')
                    if len(parts) >= 2 and 'K' in parts[1] and parts[0] not in ('', 'N/A'):
                        pts.append(float(parts[0]) - off)
                with _PROBE_LOCK:
                    _KEYFRAMES[key] = pts
            for t in pts:
                i = int(round(t * self.fps))
                if t0 - 0.5 / self.fps <= i / self.fps <= t1 + 0.5 / self.fps:
                    ks.add(i)
        return sorted(ks)

    def decode_keyframes(self, ks, sel):
        """Key frames sel (a subset of the consecutive key-frame list ks) decoded alone (-skip_frame nokey: no other
        frame is decoded): one pass over ks, or one seek per selected key frame when ks is much longer
        -> {index: frame}; {} if the stream disagrees with the list."""
        groups = [list(ks)] if len(ks) <= 3 * len(sel) else [[i] for i in sel]
        out = {}
        for g in groups:
            tic = time.perf_counter()
            p = self._popen(self.cmd(g[0], count=len(g), keyframes=True))
            got = []
            try:
                while len(got) < len(g):
                    raw = _read_exact(p.stdout, self.nbytes)
                    if raw is None:
                        break
                    got.append(raw)
            finally:
                _kill(p)
            with self.cv:
                self.n_seeks += 1
                self.decode_s += time.perf_counter() - tic
            if len(got) != len(g):
                return {}
            out.update({i: self._frame(raw) for i, raw in zip(g, got) if i in sel})
        return out

    def close(self):
        with self.cv:
            self.gen += 1
            _kill(self.proc)
            self.proc = None
            self.buf.clear()
            self.pos = None
            self.cv.notify_all()
        with self.side_lock:
            self.side.clear()

    def __del__(self):
        try:
            _kill(self.proc)
        except Exception:  # noqa: BLE001
            pass


# ----------------------------------------------------------------------------- source access
class Source:
    """One entry of EDL "sources": the file, its picture box (letterbox / UI removed), logo, external mask.
    legacy decode (span / _decode) = whole spans of the full box, as the first engine did; new EDLs read through
    FrameReader with a per-segment geometry (region of interest, scale)."""
    CACHE_BYTES = int(float(os.environ.get('ED_DECODE_CACHE_MB', 160)) * 2 ** 20)

    def __init__(self, cfg, name=None):
        self.name = name
        self.path = cfg['path']
        self.info = info = probe_source(self.path)
        self.fps = float(cfg.get('fps') or info['fps'])
        self.W, self.H = info['w'], info['h']
        self.image = bool(info.get('image'))
        bx = [int(round(float(v))) for v in (cfg.get('box') or [0, 0, self.W, self.H])]
        bx = [min(max(bx[0], 0), self.W - 1), min(max(bx[1], 0), self.H - 1), min(bx[2], self.W), min(bx[3], self.H)]
        if bx[2] <= bx[0] or bx[3] <= bx[1]:
            raise ValueError(f'source {name or self.path}: empty box {cfg.get("box")}')
        self.box = bx
        x0, y0, x1, y1 = self.box
        self.w, self.h = x1 - x0, y1 - y0
        lg = cfg.get('logo')
        self.logo = None if not lg else [lg[0] - x0, lg[1] - y0, lg[2] - x0, lg[3] - y0]
        mk = cfg.get('mask')
        mk = {'path': mk} if isinstance(mk, str) else (dict(mk) if isinstance(mk, dict) and mk.get('path') else None)
        self.mask = mk
        self.mask_info = probe_source(mk['path']) if mk else None
        self._cache = OrderedDict()           # (t0, t1) requested -> (times, frames); LRU by bytes
        self._bytes = 0
        self._lock = threading.Lock()
        self.decodes, self.hits, self.decode_s = 0, 0, 0.0
        self.readers = []                     # FrameReaders opened for this source (stats)

    def geom(self, x0, y0, x1, y1, scale=1.0):
        """Geom of the box-px region [x0, x1) x [y0, y1) (clipped to the box, even-aligned inside it) at `scale`
        delivered px per source px."""
        bx, by = self.box[0], self.box[1]
        fx0, fx1 = _even_in(bx + max(0.0, x0), bx + min(float(self.w), x1))
        fy0, fy1 = _even_in(by + max(0.0, y0), by + min(float(self.h), y1))
        w, h = fx1 - fx0, fy1 - fy0
        s = min(1.0, float(scale))
        dw, dh = (w, h) if s >= 0.999 else (max(2, int(round(w * s))), max(2, int(round(h * s))))
        return Geom(fx0, fy0, w, h, dw, dh, bx=bx, by=by)

    def mask_geom(self, g):
        """Geom of the external mask covering the same picture region as g, delivered at g's size."""
        mi = self.mask_info
        kx, ky = self.W / float(mi['w']), self.H / float(mi['h'])
        x0, y0 = int(math.floor(g.x / kx)), int(math.floor(g.y / ky))
        x1, y1 = int(math.ceil((g.x + g.w) / kx)), int(math.ceil((g.y + g.h) / ky))
        x1, y1 = min(x1, mi['w']), min(y1, mi['h'])
        return Geom(x0, y0, x1 - x0, y1 - y0, g.dw, g.dh, bx=self.box[0], by=self.box[1], kx=kx, ky=ky)

    def reader(self, geom, **kw):
        r = FrameReader(self.path, self.info, geom, fps=self.fps, **kw)
        with self._lock:
            self.readers.append(r)
        return r

    def mask_reader(self, geom, **kw):
        mk = self.mask
        kind = 'alpha' if mk.get('channel') == 'alpha' else 'gray'
        r = FrameReader(mk['path'], self.mask_info, self.mask_geom(geom), fps=float(mk.get('fps') or self.mask_info['fps']),
                        kind=kind, **kw)
        with self._lock:
            self.readers.append(r)
        return r

    def stats(self):
        with self._lock:
            rs = list(self.readers)
        return dict(decodes=self.decodes + sum(r.n_starts + r.n_seeks for r in rs), cache_hits=self.hits,
                    frames=sum(r.n_decoded for r in rs), seeks=sum(r.n_seeks for r in rs),
                    s=round(self.decode_s + sum(r.decode_s for r in rs), 2))

    @staticmethod
    def _crop_vf(x, y, w, h, W, H):
        """ffmpeg crop exact for any pixel format: an even-aligned region containing the box (ffmpeg's crop rounds
        odd sizes and offsets of 4:2:0 pictures down: an odd-width box skewed every row of the raw frames) ->
        (filter, (dx, dy) of the box inside it, (cw, ch))."""
        ex0, ey0 = x - x % 2, y - y % 2
        ex1, ey1 = min(W, x + w + (x + w) % 2), min(H, y + h + (y + h) % 2)
        return f'crop={ex1 - ex0}:{ey1 - ey0}:{ex0}:{ey0}:exact=1', (x - ex0, y - ey0), (ex1 - ex0, ey1 - ey0)

    def span(self, t0, t1, legacy=False, hint=None):
        """Decoded [t0, t1] of the picture box: (times, frames uint8 [N,h,w,3]). Served from the decode cache when a
        cached span covers the request (ghosts, continuations, stills); hint = a wider (t0, t1) to decode on a miss so
        neighbouring segments hit the cache. legacy=True reproduces the first engine's decode of exactly this request
        (see below) so old EDLs re-render identically."""
        t0 = max(0.0, t0)
        hit = None
        with self._lock:
            for (a, b), val in reversed(self._cache.items()):
                if a <= t0 + 1e-9 and b >= t1 - 1e-9:
                    self._cache.move_to_end((a, b))
                    self.hits += 1
                    hit = val
                    break
        if hit is None:
            a, b = (max(0.0, min(t0, hint[0])), max(t1, hint[1])) if hint else (t0, t1)
            hit = self._decode(a, b)
            with self._lock:
                if (a, b) not in self._cache and hit[1].nbytes <= self.CACHE_BYTES:
                    self._cache[(a, b)] = hit
                    self._bytes += hit[1].nbytes
                    while self._bytes > self.CACHE_BYTES and len(self._cache) > 1:
                        _, (_, old) = self._cache.popitem(last=False)
                        self._bytes -= old.nbytes
        st, fr = hit
        if not legacy:
            return st, fr
        # The first engine decoded with ffmpeg's default CFR sync, which duplicates the first frame when the seek
        # point lies >= half a source frame before it: frame i then showed the picture of time st[i] - 1/fps.
        t0r, dur = float(f'{t0:.4f}'), float(f'{max(t1 - t0, 1.0 / self.fps):.4f}')
        first = math.ceil(t0r * self.fps - 1e-4) / self.fps
        i = max(0, int(round((first - st[0]) * self.fps)))
        sub = fr[i:i + max(1, int(math.ceil((t0r + dur - first) * self.fps - 1e-6)))]
        if len(sub) and (first - t0r) * self.fps >= 0.5:
            sub = np.concatenate([sub[:1], sub])
        return first + np.arange(len(sub)) / self.fps, sub

    def _decode(self, t0, t1):
        """Whole-box frames with source time >= t0 (time = index / fps from the first frame of the stream) up to
        t1, as (times, frames [N, h, w, 3]). Seeks to the midpoint before the first wanted frame and keeps
        passthrough timing (no duplicated / dropped frames), so frame i is the same whatever the seek point. The crop
        is exact for any box (odd sizes and offsets included)."""
        tic = time.perf_counter()
        x0, y0, _, _ = self.box
        first = int(math.ceil(t0 * self.fps - 1e-4))
        count = int(math.ceil((t0 + max(t1 - t0, 1.0 / self.fps)) * self.fps - 1e-6)) - first + 1
        crop, (dx, dy), (cw, ch) = self._crop_vf(x0, y0, self.w, self.h, self.W, self.H)
        ts = self.info.get('t_off', 0.0) + (first - 0.5) / self.fps
        cmd = ['ffmpeg', '-v', 'error', '-nostdin'] + (['-ss', f'{ts:.6f}'] if first > 0 and ts > 0 else [])
        cmd += ['-i', self.path, '-map', '0:v:0', '-an', '-sn', '-dn', '-frames:v', str(max(1, count)), '-vf', crop,
                '-fps_mode', 'passthrough', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
        raw = subprocess.run(cmd, capture_output=True).stdout
        n = len(raw) // (cw * ch * 3)
        fr = np.frombuffer(raw[:n * cw * ch * 3], np.uint8).reshape(n, ch, cw, 3)
        if (dx, dy, cw, ch) != (0, 0, self.w, self.h):
            fr = np.ascontiguousarray(fr[:, dy:dy + self.h, dx:dx + self.w])
        times = (first + np.arange(n)) / self.fps
        with self._lock:
            self.decodes += 1
            self.decode_s += time.perf_counter() - tic
        return times, fr

    def clean_logo(self, fr, win, geom=None):
        """Inpaint the logo (box px) when the crop window (win = x0, y0, x1, y1 in box px) comes within 6 px of it.
        fr = the whole box picture, or a picture delivered by a FrameReader of `geom`. A logo touching (or crossing)
        the picture edge is handled: only the part inside the picture is masked."""
        if self.logo is None:
            return fr
        lx0, ly0, lx1, ly1 = self.logo
        if win[2] < lx0 - 6 or win[0] > lx1 + 6 or win[3] < ly0 - 6 or win[1] > ly1 + 6:
            return fr
        h, w = fr.shape[:2]
        pad, mg, rad = 24, 3, 6
        if geom is not None:
            s = min(geom.sx, geom.sy)
            ex0, ey0, ex1, ey1 = geom.box_edges(lx0, ly0, lx1, ly1)
            lx0, ly0, lx1, ly1 = int(math.floor(ex0)), int(math.floor(ey0)), int(math.ceil(ex1)), int(math.ceil(ey1))
            pad, mg, rad = max(6, int(round(24 * s))), max(1, int(round(3 * s))), max(3, int(round(6 * s)))
        lx0, ly0, lx1, ly1 = max(lx0, 0), max(ly0, 0), min(lx1, w), min(ly1, h)
        if lx1 <= lx0 or ly1 <= ly0:
            return fr                                       # the logo is outside this picture
        X0, Y0 = max(0, lx0 - pad), max(0, ly0 - pad)
        X1, Y1 = min(w, lx1 + pad), min(h, ly1 + pad)
        sub = np.ascontiguousarray(fr[Y0:Y1, X0:X1])
        m = np.zeros(sub.shape[:2], np.uint8)
        m[max(0, ly0 - Y0 - mg):ly1 - Y0 + mg + 1, max(0, lx0 - X0 - mg):lx1 - X0 + mg + 1] = 255
        if m.all():
            return fr                                       # nothing around the logo to fill it from
        out = fr.copy()
        out[Y0:Y1, X0:X1] = cv2.inpaint(sub, m, rad, cv2.INPAINT_TELEA)
        return out


# ----------------------------------------------------------------------------- crop / warp
def crop_state(seg, k, n):
    c = dict(cx=0.5, cy=0.5, z=1.0, rot=0.0, dx=0.0, dy=0.0)
    c.update({kk: v for kk, v in (seg.get('crop') or {}).items() if kk in c})
    path = (seg.get('crop') or {}).get('path')
    if path:
        # keyframes [[k, cx, cy, z], ...] (k = frame offset inside the segment), linear in between
        ks = [p[0] for p in path]
        for j, name in enumerate(('cx', 'cy', 'z')):
            c[name] = float(np.interp(k, ks, [p[j + 1] for p in path]))
        return c
    to = (seg.get('crop') or {}).get('to')
    if to and n > 1:
        p = ease(k / (n - 1), (seg.get('crop') or {}).get('ease', 'linear'))
        for kk, v in to.items():
            if kk in c:
                c[kk] = c[kk] + (v - c[kk]) * p
    return c


def window(src, c, ow, oh):
    hw = src.h / max(c['z'], 1e-3)
    ww = hw * ow / oh
    cx = min(max(c['cx'] * src.w, ww / 2), src.w - ww / 2) if ww < src.w else src.w / 2
    cy = min(max(c['cy'] * src.h, hw / 2), src.h - hw / 2) if hw < src.h else src.h / 2
    return cx, cy, ww, hw


def affine(cx, cy, hw, ow, oh, rot=0.0, dx=0.0, dy=0.0):
    """Source-box -> output 2x3 matrix of the crop window centred at (cx, cy), height hw, rotated by rot degrees,
    shifted by (dx, dy) output px."""
    s = oh / hw
    M = cv2.getRotationMatrix2D((cx, cy), rot, s)
    M[0, 2] += ow / 2 - cx + dx
    M[1, 2] += oh / 2 - cy + dy
    return M


def warp(fr, cx, cy, ww, hw, ow, oh, rot=0.0, dx=0.0, dy=0.0, interp=cv2.INTER_CUBIC, border='reflect'):
    return warp_m(fr, affine(cx, cy, hw, ow, oh, rot, dx, dy), ow, oh, interp, border)


def warp_m(fr, M, ow, oh, interp=cv2.INTER_CUBIC, border='reflect'):
    """Picture -> (oh, ow) by the 2x3 matrix M; border 'black' or mirrored."""
    if border == 'black':
        return cv2.warpAffine(fr, M, (ow, oh), flags=interp, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    return cv2.warpAffine(fr, M, (ow, oh), flags=interp, borderMode=cv2.BORDER_REFLECT101)


def _mip_fn(f):
    """Lazy half-resolution level of picture f (area filter) -> () -> (half, 2x3 map half px -> f px)."""
    box = []

    def get():
        if not box:
            h, w = f.shape[:2]
            w2, h2 = max(1, w // 2), max(1, h // 2)
            ax, ay = w / w2, h / h2
            box.append((cv2.resize(f, (w2, h2), interpolation=cv2.INTER_AREA),
                        np.array([[ax, 0.0, 0.5 * ax - 0.5], [0.0, ay, 0.5 * ay - 0.5]])))
        return box[0]
    return get


_K3 = np.ones((3, 3), np.uint8)


def _smoothstep(x):
    x = min(max(float(x), 0.0), 1.0)
    return x * x * (3.0 - 2.0 * x)


def noise_floor(gray):
    """Noise of a uint8 luma picture in levels: the quietest 10 % of its 8x8 blocks in the finest band (texture-free
    regions: sensor / compression noise; ~0.3 for clean digital or generated footage, 1 = visible grain)."""
    g = gray.astype(np.float32)
    hp = g - cv2.GaussianBlur(g, (0, 0), 1.0)
    h, w = hp.shape[:2]
    e = cv2.resize(hp * hp, (max(1, w // 8), max(1, h // 8)), interpolation=cv2.INTER_AREA)
    return float(np.sqrt(max(float(np.percentile(e, 10)), 0.0))) / 0.87


def sharpen_upscaled(w, src, M, u, amount=None, border='reflect', coring=True):
    """Post-upscale sharpening of uint8 RGB picture w, warped from picture src by the 2x3 matrix M with u output px
    per src px (src None: bounds from w itself). Luma detail band y - blur(y, 0.6 u px), softly cored above the
    frame's own noise / fine-texture floor (2.5 x its median), added with `amount` (default: 0.4 x smoothstep
    (u 1.1 .. 2.0), x 0.7 on clean or generated sources — noise floor < 1 level — up to x 1 from 3 levels, whose noise
    the coring keeps out), then held at every pixel inside the 3x3 range of the source pixels around it: the result
    never overshoots what the source has there — no halo, no ringing (the Lanczos upscale's own ringing goes too).
    coring=False (cross-faded pictures: coring would favour the stronger of their two copies of a moving contour and
    shift the picture frame to frame): the band is added linearly, x 0.7 on clean sources down to x 0.4 from 3 levels
    of noise. The luma change is added to R, G, B alike (no colour shift)."""
    oh, ow = w.shape[:2]
    y8 = cv2.cvtColor(w, cv2.COLOR_RGB2GRAY)
    y = y8.astype(np.float32)
    if src is not None:
        sy = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY) if src.ndim == 3 else src
        bm = cv2.BORDER_CONSTANT if border == 'black' else cv2.BORDER_REFLECT101
        lo = cv2.warpAffine(cv2.erode(sy, _K3), M, (ow, oh), flags=cv2.INTER_LINEAR, borderMode=bm)
        hi = cv2.warpAffine(cv2.dilate(sy, _K3), M, (ow, oh), flags=cv2.INTER_LINEAR, borderMode=bm)
        noise = noise_floor(sy)
    else:
        lo, hi, noise = cv2.erode(y8, _K3), cv2.dilate(y8, _K3), 1.0
    d = cv2.subtract(y, cv2.GaussianBlur(y, (0, 0), 0.6 * max(float(u), 1.0)))
    t = max(0.75, 2.5 * 1.4826 * float(np.median(np.abs(d[::4, ::4])))) if coring else 0.0
    noisy = _smoothstep((noise - 1.0) / 2.0)
    if amount is None:
        amount = 0.4 * _smoothstep((u - 1.1) / 0.9) * ((0.7 + 0.3 * noisy) if coring else (0.7 - 0.3 * noisy))
    if coring:
        d2 = cv2.multiply(d, d)
        d = cv2.divide(cv2.multiply(d2, d), cv2.add(d2, float(t * t)))         # d^3 / (d^2 + t^2): soft coring
    ys = cv2.scaleAdd(d, float(amount), y)
    ys = cv2.min(cv2.max(ys, lo.astype(np.float32)), hi.astype(np.float32))
    d16 = np.rint(cv2.subtract(ys, y)).astype(np.int16)
    return cv2.add(w, cv2.merge([d16, d16, d16]), dtype=cv2.CV_8U)


# ----------------------------------------------------------------------------- camera fx (folded into the warp)
CAMERA_FX = {'zoom.punch', 'zoom.crash', 'zoom.in_out', 'shake.beat', 'roll', 'drift'}
TIME_BLUR_FX = {'motion_blur', 'time.motion_blur'}   # mode 'frames': source-time blur on fast frames (stage 1)
CAM_ID = (1.0, 0.0, 0.0, 0.0, 0.0)


def snap(t, fps):
    """Frame of an event at absolute time t (same rule as ed_fx): floor(t * fps + 0.4)."""
    return int(math.floor(float(t) * float(fps) + 0.4))


def fx_window(fx, n, f0, fps):
    """Active window of a segment fx: (ka, kb, frame set | None), segment-relative inclusive frames.
    'frames' = [k, ...] | 'a:b' (segment-relative); 'f' = absolute frames; 'k' = [k0, k1]; 't' = [t0, t1] absolute
    output seconds (snapped like ed_fx); otherwise the whole segment."""
    if fx.get('frames') is not None:
        ks = frange(fx['frames'])
        return (min(ks), max(ks), set(ks)) if ks else (0, -1, set())
    if fx.get('f') is not None:
        ks = [v - f0 for v in frange(fx['f'])]
        return (min(ks), max(ks), set(ks)) if ks else (0, -1, set())
    kr = fx.get('k')
    if isinstance(kr, (list, tuple)) and len(kr) == 2:
        return int(kr[0]), int(kr[1]), None
    t = fx.get('t')
    if isinstance(t, (list, tuple)) and len(t) == 2:
        return snap(t[0], fps) - f0, snap(t[1], fps) - f0, None
    return 0, n - 1, None


def _has_window(fx):
    return any(fx.get(key) is not None for key in ('frames', 'f', 'k', 't'))


def camera_local(fx, k, ka, kb, fps, H, hits=None):
    """Built-in camera moves (used when ed_fx.camera is unavailable) -> (zoom_mult, dx, dy, rot_deg, blur).
    dx/dy in canvas px, blur = shutter fraction for the sub-frame motion blur. The fx window [ka, kb] is the move."""
    t = fx.get('type')
    amt = float(fx.get('amt', 1.0))
    u = min(max((k - ka) / max(kb - ka, 1), 0.0), 1.0)
    inside = ka <= k <= kb
    zm, dx, dy, rot, blur = 1.0, 0.0, 0.0, 0.0, 0.0
    if t == 'zoom.punch':                       # instant (or eased over `attack` frames) scale jump, held
        if inside:
            att, rel = float(fx.get('attack', 0)), float(fx.get('release', 0))
            e = 1.0
            if att > 0 and k - ka < att:
                e, blur = ease((k - ka + 1) / att, fx.get('ease', 'out')), float(fx.get('blur', 0.5))
            if rel > 0 and kb - k < rel:
                e, blur = min(e, ease((kb - k) / rel, 'inout')), float(fx.get('blur', 0.5))
            zm = float(fx.get('scale', 1.2)) ** e
    elif t == 'zoom.crash':                     # accelerating zoom over the window, held after it
        if k >= ka:
            zm = float(fx.get('scale', 1.8)) ** ease(u, fx.get('ease', 'in'))
            blur = float(fx.get('blur', 0.6)) if inside else 0.0
    elif t == 'zoom.in_out':                    # out and back inside the window
        if inside:
            zm = float(fx.get('scale', 1.3)) ** math.sin(math.pi * u)
            blur = float(fx.get('blur', 0.3))
    elif t == 'shake.beat':                     # decaying shake from every hit
        amp = float(fx.get('amp', 0.02)) * H
        dec = max(float(fx.get('decay', 6.0)), 0.5)
        fq, rr, seed = float(fx.get('freq', 9.0)), float(fx.get('rot', 0.6)), int(fx.get('seed', 1))
        for i, kh in enumerate(hits if hits is not None else [ka]):
            d = k - kh
            if 0 <= d < 6 * dec:
                a = math.exp(-d / dec)
                ph = d / fps * 2 * math.pi * fq
                sx, sy = np.random.default_rng([seed, i]).uniform(-1, 1, 2)
                dx += amp * a * sx * math.cos(ph)
                dy += amp * a * sy * math.sin(ph * 1.3)
                rot += rr * a * math.sin(ph * 0.7)
        blur = float(fx.get('blur', 0.0))
    elif t == 'roll':                           # rotation ramp: deg or [d0, d1]
        deg = fx.get('deg', 6.0)
        d0, d1 = (float(deg[0]), float(deg[1])) if isinstance(deg, (list, tuple)) else (0.0, float(deg))
        if k >= ka:
            rot = d0 + (d1 - d0) * ease(u, fx.get('ease', 'inout'))
        blur = float(fx.get('blur', 0.0)) if inside else 0.0
    elif t == 'drift':                          # slow push: dx/dy canvas px and zoom z reached at the window end
        e = ease(u, fx.get('ease', 'linear'))
        dx, dy = float(fx.get('dx', 40.0)) * e, float(fx.get('dy', 0.0)) * e
        zm = float(fx.get('z', 1.0)) ** e
    if amt != 1.0:
        zm, dx, dy, rot = zm ** amt, dx * amt, dy * amt, rot * amt
    return zm, dx, dy, rot, blur


def fold_camera(c, cam):
    """Crop state + camera state (ed_fx contract): zoom multiplies the crop zoom (the window shrinks), rot adds
    (degrees, OpenCV sign, about the output centre), dx/dy are OUTPUT px added after the warp."""
    c = dict(c)
    c['z'] = c['z'] * cam['zoom']
    c['rot'] = c['rot'] + cam['rot']
    c['odx'] = c.get('odx', 0.0) + cam['dx']
    c['ody'] = c.get('ody', 0.0) + cam['dy']
    return c


def lerp_cam(a, b, u):
    """Camera state between two states (zoom in log space)."""
    return dict(zoom=math.exp(math.log(a['zoom']) * (1 - u) + math.log(b['zoom']) * u),
                rot=a['rot'] + (b['rot'] - a['rot']) * u, dx=a['dx'] + (b['dx'] - a['dx']) * u,
                dy=a['dy'] + (b['dy'] - a['dy']) * u)


# ----------------------------------------------------------------------------- grading
PRESETS = {
    # B&W: luma, auto exposure, contrast curve
    'bw': dict(mono=1, auto=1.0, contrast=1.15, gamma=1.0),
    'bw_hi': dict(mono=1, auto=1.0, contrast=1.45, gamma=0.95, black=0.04),
    'bw_dark': dict(mono=1, auto=0.8, contrast=1.25, gamma=1.35, gain=0.85),
    'bw_soft': dict(mono=1, auto=1.0, contrast=1.0, gamma=0.95, fade=0.04),
    'color': dict(auto=0.6, sat=1.1, contrast=1.08),
    'natural': dict(auto=0.0, sat=1.0, contrast=1.0),
    'warm': dict(auto=0.7, sat=1.15, temp=0.25, contrast=1.1),
    'cool': dict(auto=0.7, sat=0.85, temp=-0.25, contrast=1.05),
    'teal': dict(auto=0.7, sat=1.0, temp=-0.15, tint=-0.05, split=([0.0, 0.35, 0.4], [1.0, 0.85, 0.7], 0.35), contrast=1.1),
    'desat': dict(auto=0.8, sat=0.35, contrast=1.1),
}


def grade_params(g):
    p = dict(PRESETS.get((g or {}).get('preset', 'natural'), {}))
    p.update({k: v for k, v in (g or {}).items() if k != 'preset'})
    return p


def grade_stats(frames_f, skip_black=False):
    """Exposure stats over a few graded-space frames (float 0..1)."""
    L = np.concatenate([luma(f).ravel()[::7] for f in frames_f])
    if skip_black and (L > 0.004).any():
        L = L[L > 0.004]
    return dict(lo=float(np.percentile(L, 0.5)), hi=float(np.percentile(L, 99.6)), mid=float(np.median(L)))


def apply_grade(x, g, st):
    p = dict(PRESETS.get(g.get('preset', 'natural'), {}))
    p.update({k: v for k, v in g.items() if k != 'preset'})
    a = p.get('auto', 0.0)
    if a > 0 and st:
        lo, hi = st['lo'], max(st['hi'], st['lo'] + 0.05)
        lo = lo * p.get('auto_lo', 1.0)
        xn = (x - lo) / (hi - lo)
        x = x * (1 - a) + xn * a
    if p.get('exposure'):
        x = x * (2.0 ** p['exposure'])
    x = np.clip(x, 0, 1.5)
    mono1 = False
    if p.get('mono'):
        L = luma(x)
        mix = p.get('mono_rgb')
        if mix:
            L = x[..., 0] * mix[0] + x[..., 1] * mix[1] + x[..., 2] * mix[2]
        # no channel-mixing step follows: run the per-pixel tone curve on one channel, expand at the end (exact)
        mono1 = not any(p.get(key) for key in ('temp', 'tint', 'mult', 'duo', 'split'))
        x = L if mono1 else np.repeat(L[..., None], 3, axis=2)
    else:
        s = p.get('sat', 1.0)
        if s != 1.0:
            L = luma(x)[..., None]
            x = L + (x - L) * s
    t = p.get('temp', 0.0)
    tn = p.get('tint', 0.0)
    if t or tn:
        x = x * np.array([1 + 0.35 * t, 1 + 0.25 * tn, 1 - 0.35 * t], np.float32)
    if p.get('mult'):
        x = x * np.array(p['mult'], np.float32)
    if p.get('duo'):
        sh, hi_c, amt = p['duo']
        L = np.clip(luma(x), 0, 1)[..., None]
        tone = np.array(sh, np.float32) + (np.array(hi_c, np.float32) - np.array(sh, np.float32)) * L
        x = x * (1 - amt) + tone * amt
    if p.get('split'):
        sh, hi_c, amt = p['split']
        L = np.clip(luma(x), 0, 1)[..., None]
        tone = np.array(sh, np.float32) * (1 - L) + np.array(hi_c, np.float32) * L
        x = x * (1 - amt) + (x * tone * 2.0) * amt
    x = np.clip(x, 0, 1)
    gm = p.get('gamma', 1.0)
    if gm != 1.0:
        x = x ** gm
    c = p.get('contrast', 1.0)
    if c != 1.0:
        piv = p.get('pivot', 0.5)
        # smooth S-curve: blend of linear contrast and a sigmoid keeps highlights from clipping hard
        y = (x - piv) * c + piv
        sg = 1 / (1 + np.exp(-(x - piv) * 4.0 * c))
        s0, s1 = 1 / (1 + math.exp(piv * 4.0 * c)), 1 / (1 + math.exp(-(1 - piv) * 4.0 * c))
        sg = (sg - s0) / (s1 - s0)
        x = np.clip(y * 0.5 + sg * 0.5, 0, 1)
    if p.get('black'):
        b = p['black']
        x = np.clip((x - b) / (1 - b), 0, 1)
    gain = p.get('gain', 1.0)
    lift = p.get('lift', 0.0)
    if gain != 1.0 or lift:
        x = lift + x * (gain - lift)
    if p.get('fade'):
        x = p['fade'] + x * (1 - p['fade'])
    if p.get('bleach'):
        b = p['bleach']
        x = x * (1 - b) + b
    x = np.clip(x, 0, 1)
    return np.repeat(x[..., None], 3, axis=2) if mono1 else x


_LUMA_M = np.array([[0.2126, 0.7152, 0.0722]], np.float32)
_TAIL_LUTS, _TAIL_KEYS = OrderedDict(), ('gamma', 'contrast', 'pivot', 'black', 'gain', 'lift', 'fade', 'bleach')
_TAIL_N = 4096


def _luma_cv(x):
    return cv2.transform(x, _LUMA_M)


def _tail_lut(p):
    """Per-channel tail of apply_grade (gamma, contrast S-curve, black, gain / lift, fade, bleach, clip) sampled on
    4096 points of 0..1, or None when the tail is the identity."""
    key = tuple((k, json.dumps(p.get(k))) for k in _TAIL_KEYS)
    if key in _TAIL_LUTS:
        return _TAIL_LUTS[key]
    q = {k: p[k] for k in _TAIL_KEYS if k in p}
    ident = (q.get('gamma', 1.0) == 1.0 and q.get('contrast', 1.0) == 1.0 and not q.get('black')
             and q.get('gain', 1.0) == 1.0 and not q.get('lift') and not q.get('fade') and not q.get('bleach'))
    lut = None
    if not ident:
        grid = np.linspace(0.0, 1.0, _TAIL_N, dtype=np.float32)[:, None]
        lut = apply_grade(grid, dict(q, preset='natural'), None)[:, 0].astype(np.float32)
    _TAIL_LUTS[key] = lut
    while len(_TAIL_LUTS) > 64:
        _TAIL_LUTS.popitem(last=False)
    return lut


def apply_grade_fast(x, g, st):
    """apply_grade for new EDLs, same result within 1/16 of an 8-bit level and 2-4x faster: auto exposure +
    exposure folded into one multiply-add, saturation / temperature / split toning fused, the per-channel tail as a
    4096-entry table."""
    p = dict(PRESETS.get(g.get('preset', 'natural'), {}))
    p.update({k: v for k, v in g.items() if k != 'preset'})
    m, b = 1.0, 0.0
    a = p.get('auto', 0.0)
    if a > 0 and st:
        lo, hi = st['lo'], max(st['hi'], st['lo'] + 0.05)
        lo = lo * p.get('auto_lo', 1.0)
        m, b = (1 - a) + a / (hi - lo), -a * lo / (hi - lo)
    if p.get('exposure'):
        e = 2.0 ** p['exposure']
        m, b = m * e, b * e
    y = np.multiply(x, np.float32(m), dtype=np.float32)
    if b:
        y += np.float32(b)
    np.clip(y, 0, 1.5, out=y)
    mono1 = False
    if p.get('mono'):
        mix = p.get('mono_rgb')
        L = cv2.transform(y, np.array([mix[:3]], np.float32)) if mix else _luma_cv(y)
        mono1 = not any(p.get(key) for key in ('temp', 'tint', 'mult', 'duo', 'split'))
        y = L if mono1 else np.repeat(L[..., None], 3, axis=2)
    else:
        s = p.get('sat', 1.0)
        if s != 1.0:
            L = _luma_cv(y)
            y *= np.float32(s)
            y += (np.float32(1.0 - s) * L)[..., None]
    t, tn = p.get('temp', 0.0), p.get('tint', 0.0)
    vec = np.ones(3, np.float32)
    if t or tn:
        vec *= np.array([1 + 0.35 * t, 1 + 0.25 * tn, 1 - 0.35 * t], np.float32)
    if p.get('mult'):
        vec *= np.array(p['mult'], np.float32)
    if not np.all(vec == 1.0):
        y *= vec
    if p.get('duo'):
        sh, hi_c, amt = p['duo']
        sh, hi_c = np.array(sh, np.float32), np.array(hi_c, np.float32)
        L = np.clip(_luma_cv(y), 0, 1)[..., None]
        y = y * np.float32(1 - amt) + (sh + (hi_c - sh) * L) * np.float32(amt)
    if p.get('split'):
        sh, hi_c, amt = p['split']
        sh, hi_c = np.array(sh, np.float32), np.array(hi_c, np.float32)
        L = np.clip(_luma_cv(y), 0, 1)[..., None]
        y *= (np.float32(1 - amt) + np.float32(2 * amt) * sh) + (np.float32(2 * amt) * (hi_c - sh)) * L
    np.clip(y, 0, 1, out=y)
    lut = _tail_lut(p)
    if lut is not None:
        idx = np.multiply(y, np.float32(_TAIL_N - 1), dtype=np.float32)
        idx += np.float32(0.5)
        y = np.take(lut, idx.astype(np.int32))
    return np.repeat(y[..., None], 3, axis=2) if mono1 else y


# ----------------------------------------------------------------------------- image fx (built-in fallback)
def dirblur(x, length_px, angle=0.0):
    L = int(max(1, round(length_px)))
    if L < 2:
        return x
    if abs(angle) < 0.5:
        return cv2.blur(x, (L, 1))
    if abs(abs(angle) - 90) < 0.5:
        return cv2.blur(x, (1, L))
    k = np.zeros((L, L), np.float32)
    c = (L - 1) / 2
    dx, dy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    for i in range(L):
        t = i - c
        k[int(round(c + t * dy)), int(round(c + t * dx))] = 1
    k /= k.sum()
    return cv2.filter2D(x, -1, k)


def zoomblur(x, amount, cx=0.5, cy=0.5, n=8):
    h, w = x.shape[:2]
    acc = np.zeros_like(x)
    for i in range(n):
        s = 1 + amount * i / max(n - 1, 1)
        M = cv2.getRotationMatrix2D((cx * w, cy * h), 0, s)
        acc += cv2.warpAffine(x, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    return acc / n


def _shift_edge(a, d, axis):
    """Shift a 2-D array by d px along axis, repeating the edge row/column (no wrap-around)."""
    n = a.shape[axis]
    d = max(-n, min(n, int(d)))
    if d == 0:
        return a.copy()
    out = np.empty_like(a)
    if axis == 1:
        if d > 0:
            out[:, d:] = a[:, :n - d]
            out[:, :d] = a[:, :1]
        else:
            out[:, :n + d] = a[:, -d:]
            out[:, n + d:] = a[:, -1:]
    else:
        if d > 0:
            out[d:] = a[:n - d]
            out[:d] = a[:1]
        else:
            out[:n + d] = a[-d:]
            out[n + d:] = a[-1:]
    return out


def chroma(x, px, vertical=False):
    """Chromatic offset: red shifted by +px, blue by -px; the frame edge is repeated, never wrapped around."""
    if not px:
        return x
    px = int(round(px))
    out = x.copy()
    ax = 0 if vertical else 1
    out[..., 0] = _shift_edge(x[..., 0], px, ax)
    out[..., 2] = _shift_edge(x[..., 2], -px, ax)
    return out


_GRID_CACHE = {}


def _norm_grid(oh, ow):
    key = (oh, ow)
    g = _GRID_CACHE.get(key)
    if g is None:
        yy, xx = np.mgrid[0:oh, 0:ow].astype(np.float32)
        g = _GRID_CACHE[key] = (yy, xx)
    return g


LEGACY_FX = {'dirblur', 'zoomblur', 'chroma', 'smear', 'blur', 'shake', 'grain', 'vignette', 'exposure', 'bloom',
             'invert', 'bleach'}
LOCAL_FX = LEGACY_FX | {'rgb_split', 'glow', 'letterbox', 'posterize', 'pixelate', 'duotone'}


def apply_fx_one(x, fx, k, n, ow, oh, rng):
    """One built-in image fx on frame k of n (amt / amt_to ramp over the segment). Timing is the caller's job."""
    p = k / max(n - 1, 1)
    t = fx['type']
    amt = fx.get('amt', 1.0)
    if 'amt_to' in fx:
        amt = amt + (fx['amt_to'] - amt) * ease(p, fx.get('ease', 'linear'))
    if t == 'dirblur':
        x = dirblur(x, fx.get('len', 0.05) * ow * amt, fx.get('angle', 0.0))
    elif t == 'zoomblur':
        x = zoomblur(x, fx.get('amount', 0.12) * amt, fx.get('cx', 0.5), fx.get('cy', 0.5), fx.get('n', 8))
    elif t == 'chroma':
        x = chroma(x, fx.get('px', 6) * amt * ow / 1080, fx.get('vertical', False))
    elif t == 'rgb_split':
        a = math.radians(fx.get('angle', 0.0))
        px = fx.get('px', 10) * amt * ow / 1080
        x = chroma(x, px * math.cos(a)) if abs(math.cos(a)) > 0.01 else x
        x = chroma(x, px * math.sin(a), vertical=True) if abs(math.sin(a)) > 0.01 else x
    elif t == 'smear':
        x = dirblur(x, fx.get('len', 0.25) * ow * amt, fx.get('angle', 0.0))
        x = chroma(x, fx.get('px', 14) * amt * ow / 1080)
        L = luma(x)[..., None]
        x = np.clip(L + (x - L) * fx.get('sat', 1.6), 0, 1)
    elif t == 'blur':
        r = fx.get('r', 6) * amt * ow / 1080
        if r > 0.3:
            x = cv2.GaussianBlur(x, (0, 0), r)
    elif t == 'shake':
        a = fx.get('px', 12) * ow / 1080 * amt
        dx, dy = rng.uniform(-a, a), rng.uniform(-a, a)
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        x = cv2.warpAffine(x, M, (ow, oh), borderMode=cv2.BORDER_REFLECT101)
    elif t == 'grain':
        g = rng.normal(0, fx.get('sigma', 0.035), (oh // 2, ow // 2)).astype(np.float32)
        g = cv2.resize(g, (ow, oh), interpolation=cv2.INTER_LINEAR)
        x = np.clip(x + g[..., None] * amt, 0, 1)
    elif t == 'vignette':
        yy, xx = _norm_grid(oh, ow)
        d = ((xx / ow - 0.5) ** 2 / 0.25 + (yy / oh - 0.5) ** 2 / 0.25)
        x = x * (1 - fx.get('amount', 0.35) * np.clip(d, 0, 1.5)[..., None] * amt)
    elif t == 'exposure':
        x = np.clip(x * (2.0 ** (fx.get('ev', 0.0) * amt)), 0, 1)
    elif t in ('bloom', 'glow'):
        thr = fx.get('thr', 0.7)
        hi = np.clip(x - thr, 0, None) / max(1 - thr, 1e-3)
        r = fx.get('r', 30) * ow / 1080
        x = np.clip(x + cv2.GaussianBlur(hi, (0, 0), r) * fx.get('strength', 0.6) * amt, 0, 1)
    elif t == 'invert':
        x = 1 - x
    elif t == 'bleach':
        x = x * (1 - fx.get('a', 0.5) * amt) + fx.get('a', 0.5) * amt
    elif t == 'letterbox':                      # bars to an aspect ratio (w/h), e.g. 2.39
        ratio = float(fx.get('ratio', 2.39))
        bar = int(round(max(0.0, (oh - ow / ratio) / 2) * min(max(amt, 0.0), 1.0)))
        if bar > 0:
            x = x.copy()
            x[:bar] = 0
            x[oh - bar:] = 0
    elif t == 'posterize':
        lv = max(2, int(fx.get('levels', 5)))
        x = x * (1 - amt) + (np.floor(x * lv) / (lv - 1)).clip(0, 1) * amt
    elif t == 'pixelate':
        sz = max(1, int(round(fx.get('size', 24) * ow / 1080 * amt)))
        if sz > 1:
            sm = cv2.resize(x, (max(1, ow // sz), max(1, oh // sz)), interpolation=cv2.INTER_AREA)
            x = cv2.resize(sm, (ow, oh), interpolation=cv2.INTER_NEAREST)
    elif t == 'duotone':
        sh, hi_c = color01(fx.get('shadows', [0.05, 0.05, 0.25])), color01(fx.get('highlights', [1.0, 0.85, 0.4]))
        L = np.clip(luma(x), 0, 1)[..., None]
        x = x * (1 - amt) + (sh + (hi_c - sh) * L) * amt
    return x


def apply_fx(x, fxs, k, n, ow, oh, rng):
    """Built-in image fx list on frame k ('frames' = segment-relative k list). Kept for callers of the old API."""
    for fx in fxs or []:
        if fx.get('frames') is not None and k not in frange(fx['frames']):
            continue
        if fx.get('type') in LOCAL_FX:
            x = apply_fx_one(x, fx, k, n, ow, oh, rng)
    return x


# ----------------------------------------------------------------------------- transitions / flash (fallbacks)
TRANS_LOCAL = {'dissolve', 'dip', 'fade', 'flash', 'whip'}


def _push(a, b, off, horiz, sign):
    """a leaves by off px, b enters behind it (sign +1: towards left/up, -1: towards right/down)."""
    n = a.shape[1] if horiz else a.shape[0]
    off = max(0, min(n, off))
    out = np.empty_like(a)
    if horiz:
        if sign > 0:
            out[:, :n - off], out[:, n - off:] = a[:, off:], b[:, :off]
        else:
            out[:, off:], out[:, :off] = a[:, :n - off], b[:, n - off:]
    else:
        if sign > 0:
            out[:n - off], out[n - off:] = a[off:], b[:off]
        else:
            out[off:], out[:off] = a[:n - off], b[n - off:]
    return out


def transition_local(kind, a, b, p, params=None, seam=None):
    """Built-in transitions (dissolve, dip, fade, flash, whip); anything else dissolves. p in (0, 1) =
    (j + 0.5) / window length; seam = True on frames from the cut (first frame of the incoming segment) on."""
    params = params or {}
    oh, ow = a.shape[:2]
    if seam is None:
        seam = p >= 0.5
    if kind in ('dip', 'fade'):
        col = color01(params.get('color'), (0.0, 0.0, 0.0))
        hold = min(max(float(params.get('hold', 0.0)), 0.0), 0.9)
        h0, h1 = 0.5 - hold / 2, 0.5 + hold / 2
        e = params.get('ease', 'inout')
        if p < h0:
            q = ease(p / h0, e)
            return a * (1 - q) + col * q
        if p <= h1:
            return np.broadcast_to(col, a.shape).astype(np.float32)
        q = ease((p - h1) / (1 - h1), e)
        return col * (1 - q) + b * q
    if kind == 'flash':                         # white peak mid-window, a before the cut, b from it
        col = color01(params.get('color'), (1.0, 1.0, 1.0))
        base = b if seam else a
        w = float(params.get('peak', 1.0)) * (1 - abs(p - 0.5) * 2) ** float(params.get('gamma', 1.5))
        if params.get('blend') == 'add':
            return np.clip(base + col * w, 0, 1)
        y = 1 - (1 - base) * (1 - col) if params.get('blend', 'screen') == 'screen' else col
        return base * (1 - w) + y * w
    if kind == 'whip':                          # push with a directional smear peaking mid-transition
        d = params.get('direction', 'left')
        horiz = d in ('left', 'right')
        size = ow if horiz else oh
        out = _push(a, b, int(round(ease(p, params.get('ease', 'inout')) * size)), horiz,
                    1 if d in ('left', 'up') else -1)
        L = int(float(params.get('blur', 0.25)) * size * math.sin(math.pi * p))
        if L >= 2:
            out = cv2.blur(out, (L, 1) if horiz else (1, L))
        return out
    q = ease(p, params.get('ease', 'linear'))   # dissolve (and the fallback for every other kind)
    return a * (1 - q) + b * q


def flash_curve(op):
    curve = op.get('curve')
    if curve:
        return [float(v) for v in curve]
    if op.get('decay'):
        return [math.exp(-i / float(op['decay'])) for i in range(max(1, int(op.get('len', 6))))]
    return [1.0, 0.55, 0.25, 0.1]


def flash_local(x, op, j):
    """Op 'flash' (fallback for ed_fx.flash_op): opacity curve[j] (j = index of the frame inside the op's frame
    list, 0 past the curve; default curve [1, .55, .25, .1] or exp(-i/decay)), colour (default white),
    blend normal | screen | add."""
    curve = flash_curve(op)
    a = (curve[j] if 0 <= j < len(curve) else 0.0) * float(op.get('a', 1.0))
    if a <= 0:
        return x
    col = color01(op.get('color'), (1.0, 1.0, 1.0))
    blend = op.get('blend', 'normal')
    if blend == 'add':
        return np.clip(x + col * a, 0, 1)
    y = 1 - (1 - x) * (1 - col) if blend == 'screen' else col
    return x * (1 - a) + y * a


# ----------------------------------------------------------------------------- masks
def person_alpha(rgb_u8, box=None, refine=True):
    """Person mask 0..1 at frame size. box=(x0,y0,x1,y1) px: segment inside it at higher effective resolution."""
    h, w = rgb_u8.shape[:2]
    m = np.zeros((h, w), np.float32)
    with _MASK_LOCK:
        if box:
            x0, y0, x1, y1 = [int(v) for v in box]
            sub = rgb_u8[y0:y1, x0:x1]
            m[y0:y1, x0:x1] = V.person_mask(sub)
        else:
            m = V.person_mask(rgb_u8).astype(np.float32)
    if refine:
        guide = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
        m = guided_filter(guide, m.astype(np.float32), max(4, w // 120), 1e-3)
    return np.clip(m, 0, 1)


def guided_filter(I, p, r, eps):
    """He et al. guided filter (grey guide): edge-aware refinement of a coarse mask."""
    k = (2 * r + 1, 2 * r + 1)
    bf = lambda a: cv2.boxFilter(a, -1, k, normalize=True, borderType=cv2.BORDER_REFLECT)  # noqa: E731
    mI, mp = bf(I), bf(p)
    vI = bf(I * I) - mI * mI
    cIp = bf(I * p) - mI * mp
    a = cIp / (vI + eps)
    b = mp - a * mI
    return bf(a) * I + bf(b)


def ellipse_mask(ow, oh, cx, cy, rx, ry, feather=0.25):
    yy, xx = _norm_grid(oh, ow)
    d = np.sqrt(((xx - cx * ow) / (rx * ow)) ** 2 + ((yy - cy * oh) / (ry * oh)) ** 2)
    return np.clip((1 - d) / max(feather, 1e-3), 0, 1)


# ----------------------------------------------------------------------------- text
class TextLayer:
    """Static text items (EDL "texts"). groups() -> [(colour, blend, opacity, alpha HxWx1)] (also used by ed_qa);
    bboxes() -> per-item ink box [x0, y0, x1, y1] in canvas px."""

    def __init__(self, ow, oh, scale):
        self.ow, self.oh, self.s = ow, oh, scale
        self.cache = {}
        self._ink = {}

    def _build(self, items):
        key = hashlib.md5(json.dumps(items, sort_keys=True).encode()).hexdigest()
        hit = self.cache.get(key)
        if hit is not None:
            return hit
        with _PIL_LOCK:
            groups, boxes = {}, []
            for it in items:
                g = (tuple(it.get('color', [235, 235, 235])), it.get('blend', 'normal'), it.get('opacity', 1.0))
                if g not in groups:
                    groups[g] = Image.new('L', (self.ow, self.oh), 0)
                d = ImageDraw.Draw(groups[g])
                f = font(it.get('font', 'sans'), it['size'] * self.s)
                x, y = it['x'] * self.s, it['y'] * self.s
                anchor = it.get('anchor', 'lt')
                tr = it.get('tracking', 0)
                bb = None
                if tr:
                    cx = x
                    for ch in it['text']:
                        d.text((cx, y), ch, font=f, fill=255, anchor=anchor)
                        b = d.textbbox((cx, y), ch, font=f, anchor=anchor)
                        bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
                        cx += f.getlength(ch) + tr * self.s
                else:
                    d.text((x, y), it['text'], font=f, fill=255, anchor=anchor)
                    bb = d.textbbox((x, y), it['text'], font=f, anchor=anchor)
                boxes.append([round(v / self.s, 1) for v in bb] if bb else None)
            out = [(np.array(c, np.float32) / 255.0, b, o, np.asarray(m, np.float32)[..., None] / 255.0 * o)
                   for (c, b, o), m in groups.items()]
            self.cache[key] = (out, boxes)
            self._ink[key] = [m.getbbox() for m in groups.values()]   # (x0, y0, x1, y1) of each group's mask
            if len(self._ink) > 40:
                self._ink.pop(next(iter(self._ink)))
            if len(self.cache) > 40:
                self.cache.pop(next(iter(self.cache)))
        return out, boxes

    def groups(self, items):
        return self._build(items)[0]

    def bboxes(self, items):
        return self._build(items)[1]

    def composite(self, x, items):
        """Text over x (returns a new array). Only the ink box of each group is computed: outside it alpha is 0
        and every blend leaves x unchanged, so this equals the full-frame formula."""
        groups = self.groups(items)
        key = hashlib.md5(json.dumps(items, sort_keys=True).encode()).hexdigest()
        inks = self._ink.get(key) or [None] * len(groups)
        x = np.array(x, np.float32)
        for (col, blend, _, a), bb in zip(groups, inks):
            if bb is None:
                if not np.any(a):
                    continue
                bb = (0, 0, x.shape[1], x.shape[0])
            x0, y0, x1, y1 = bb
            xs, ar = x[y0:y1, x0:x1], a[y0:y1, x0:x1]
            if blend == 'difference':
                xs[...] = xs * (1 - ar) + np.abs(xs - col) * ar
            elif blend == 'multiply':
                xs[...] = xs * (1 - ar) + xs * col * ar
            elif blend == 'screen':
                xs[...] = xs * (1 - ar) + (1 - (1 - xs) * (1 - col)) * ar
            else:
                xs[...] = xs * (1 - ar) + col * ar
        return x


def _alpha_bbox(a, thr=1.0 / 255):
    rows = np.flatnonzero(a.max(axis=1) > thr)
    if not len(rows):
        return None
    cols = np.flatnonzero(a.max(axis=0) > thr)
    return (int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1)


def composite_local(x, rgba, blend='normal'):
    """Premultiplied layer over x (fallback for ed_text.composite)."""
    if rgba.shape[:2] != x.shape[:2]:
        rgba = cv2.resize(np.asarray(rgba, np.float32), (x.shape[1], x.shape[0]), interpolation=cv2.INTER_LINEAR)
    c, a = rgba[..., :3], rgba[..., 3:4]
    b = (blend or 'normal').lower()
    if b == 'add':
        return np.clip(x + c, 0, 1)
    if b == 'screen':
        return x + c * (1 - x)
    if b == 'multiply':
        return x * (1 - a) + x * c
    if b == 'difference':
        return x * (1 - a) + np.abs(x * a - c)
    return x * (1 - a) + c


def _px(v, full):
    v = float(v)
    return v * full if abs(v) <= 1.0 else v


def layer_local(L, f, fps, ow, oh, scale):
    """Minimal stand-in for ed_text.render_layer: text / items / counter / words (subtitle chunks or current word)
    as plain static type -> (rgba premultiplied, blend) | None."""
    t = f / fps
    kind = L.get('kind', 'static')
    style = L.get('style')
    st = dict(style) if isinstance(style, dict) else {}      # a preset name (str) carries no fields usable here
    st.update({k: v for k, v in L.items() if k in ('font', 'size', 'color', 'x', 'y', 'anchor', 'opacity')})
    text = None
    if isinstance(L.get('text'), str):
        text = L['text']
    elif L.get('items'):
        text = ' '.join(str(it.get('text', '')) for it in L['items'])
    elif kind == 'counter':
        f0, f1 = int(L.get('f0', f)), int(L.get('f1', f))
        u = 1.0 if f1 <= f0 else (f - f0) / (f1 - f0)
        a, b = float(L.get('from', 0)), float(L.get('to', 100))
        text = f"{L.get('prefix', '')}{a + (b - a) * ease(u, 'out'):,.{int(L.get('decimals', 0))}f}{L.get('suffix', '')}"
    elif L.get('words') or L.get('chunks'):
        if L.get('chunks'):
            cur = [c for c in L['chunks'] if float(c['t0']) <= t < float(c['t1'])]
            text = cur[0]['text'] if cur else None
        else:
            ws = L['words']
            if kind in ('subtitle', 'karaoke'):
                per = max(1, int((L.get('chunk') or {}).get('words', 3)))
                for i in range(0, len(ws), per):
                    ch = ws[i:i + per]
                    if float(ch[0]['t0']) <= t < float(ch[-1]['t1']):
                        text = ' '.join(w['w'] for w in ch)
            else:
                cur = [w for w in ws if float(w['t0']) <= t < float(w.get('t1', w['t0'] + 0.4))]
                text = cur[-1]['w'] if cur else None
    if not text:
        return None
    W, H = ow / scale, oh / scale

    def num(v, default):                                      # style values may be names ('center', 'big'): defaults
        try:
            return float(v)
        except (TypeError, ValueError):
            return default
    sub = kind in ('subtitle', 'karaoke')
    size = _px(num(st.get('size'), 0.045), H)
    x = _px(num(st.get('x'), 0.5), W) * scale
    y = _px(num(st.get('y'), 0.78 if sub else 0.5), H) * scale
    fname = st.get('font') if isinstance(st.get('font'), str) and st.get('font') in FONTS else 'sans'
    anchor = st.get('anchor') if isinstance(st.get('anchor'), str) and len(st.get('anchor')) == 2 else 'mm'
    m = Image.new('L', (ow, oh), 0)
    with _PIL_LOCK:
        fnt = font(fname, max(6, size * scale))
        try:
            ImageDraw.Draw(m).text((x, y), str(text), font=fnt, fill=255, anchor=anchor,
                                   stroke_width=max(1, int(size * scale * 0.06)), stroke_fill=255)
        except ValueError:                                   # an anchor PIL does not know
            ImageDraw.Draw(m).text((x, y), str(text), font=fnt, fill=255, anchor='mm',
                                   stroke_width=max(1, int(size * scale * 0.06)), stroke_fill=255)
    a = np.asarray(m, np.float32)[..., None] / 255.0 * min(max(num(st.get('opacity'), 1.0), 0.0), 1.0)
    try:
        col = color01(st.get('color'), (1.0, 1.0, 1.0)) if not isinstance(st.get('color'), dict) else color01(None)
    except (TypeError, ValueError):
        col = color01(None)
    return np.concatenate([a * col, a], axis=2).astype(np.float32), L.get('blend', 'normal')


# ----------------------------------------------------------------------------- HUD (own design timecode panel)
def draw_hud_tc(x, tc, s, accent=(0.86, 0.16, 0.12), invert=False):
    """Timecode panel (op hud_tc), laid out for a 1080 px wide frame and scaled to the actual width (s is kept for
    the old signature: at 1080 / 540 px wide it equals the render scale)."""
    oh, ow = x.shape[:2]
    s = ow / 1080.0
    img = Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8))
    with _PIL_LOCK:
        d = ImageDraw.Draw(img, 'RGBA')
        fm = font('mono', 112 * s)
        fs = font('sans', 34 * s)
        cy = int(oh * 0.47)
        d.rounded_rectangle([int(70 * s), cy - int(150 * s), ow - int(70 * s), cy + int(170 * s)], radius=int(26 * s),
                            fill=(14, 16, 18, 205), outline=(255, 255, 255, 40), width=max(1, int(2 * s)))
        d.text((ow // 2, cy - int(10 * s)), tc, font=fm, fill=(236, 236, 236, 255), anchor='mm')
        # track row: badge + lane + playhead
        by = cy + int(95 * s)
        d.rounded_rectangle([int(120 * s), by - int(26 * s), int(200 * s), by + int(26 * s)], radius=int(8 * s),
                            fill=tuple(int(v * 255) for v in accent) + (255,))
        d.text((int(160 * s), by), 'V1', font=fs, fill=(255, 255, 255, 255), anchor='mm')
        d.rectangle([int(225 * s), by - int(18 * s), ow - int(120 * s), by + int(18 * s)], fill=(60, 66, 72, 255))
        fr = int(tc.split(':')[-1]) if tc.split(':')[-1].isdigit() else 0
        px = int(225 * s + (ow - 345 * s) * (0.35 + fr / 60.0))
        d.rectangle([px - max(1, int(2 * s)), by - int(40 * s), px + max(1, int(2 * s)), by + int(40 * s)],
                    fill=tuple(int(v * 255) for v in accent) + (255,))
    out = np.asarray(img, np.float32) / 255.0
    return 1 - out if invert else out


# ----------------------------------------------------------------------------- label
def draw_label(x, text, s, box_out=None):
    """Preview label, top-left. text = dict(num, tc, small, moves) (Renderer._label): a big clip number '#N'
    (yellow) and the output timecode (white) on the first line, then small: segment id, frame and source time
    (light grey) and the active move ids (cyan). A str / list of str draws the old one-line style. Only the label
    box is touched (the rest of the frame keeps its exact values); box_out (list) receives [0, 0, x1, y1] in px."""
    if isinstance(text, dict):
        rows = [[(text.get('num', ''), 'sans', 64, (255, 225, 0)), (text.get('tc', ''), 'mono', 40, (255, 255, 255))]]
        rows += [[(text[k], 'mono', 22, col)] for k, col in (('small', (215, 215, 215)), ('moves', (120, 225, 255)))
                 if text.get(k)]
    else:
        lines = [text] if isinstance(text, str) else [ln for ln in text if ln]
        rows = [[(ln, 'mono', 26, (255, 225, 0) if i == 0 else (120, 225, 255))] for i, ln in enumerate(lines)]
    pad, gap = 10 * s, 5 * s
    with _PIL_LOCK:
        lay, y, wmax = [], 4 * s, 0.0                        # first glyph tops 4 px below the frame top
        for row in rows:
            fonts = [font(name, size * s) for _, name, size, _ in row]
            boxes = [fo.getbbox(txt or ' ', anchor='ls') for (txt, _, _, _), fo in zip(row, fonts)]
            top, bot = min(b[1] for b in boxes), max(b[3] for b in boxes)
            base = y - top
            xx = pad
            for (txt, _, _, col), fo in zip(row, fonts):
                lay.append((xx, base, txt, fo, col))
                xx += fo.getlength(txt) + 14 * s
            wmax = max(wmax, xx - 14 * s)
            y = base + max(bot, 0) + gap
        x1, y1 = int(math.ceil(wmax + pad)), int(math.ceil(y))
        bw, bh = min(x.shape[1], x1 + 1), min(x.shape[0], y1 + 1)
        img = Image.fromarray((np.clip(x[:bh, :bw], 0, 1) * 255).astype(np.uint8))
        d = ImageDraw.Draw(img, 'RGBA')
        d.rectangle([0, 0, x1, y1], fill=(0, 0, 0, 170))
        for xx, base, txt, fo, col in lay:
            d.text((int(round(xx)), int(round(base))), txt, font=fo, fill=col + (255,), anchor='ls')
    out = x if (x.flags.writeable and x.dtype == np.float32) else np.array(x, np.float32)
    out[:bh, :bw] = np.asarray(img, np.float32) / 255.0
    if box_out is not None:
        box_out.append([0, 0, bw, bh])
    return out


def tcode(t):
    m, s = divmod(t, 60)
    return f'{int(m)}:{s:05.2f}'


# ----------------------------------------------------------------------------- audio
MP4_AUDIO = {'aac', 'mp3', 'alac', 'ac3', 'eac3', 'opus', 'flac'}


def audio_codec(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_name',
                        '-of', 'csv=p=0', path], capture_output=True, text=True)
    return r.stdout.strip() or None


def audio_mode(au):
    """'ref' (mux audio['path'] as is: copy, or legacy {"path"}), 'mix' (ed_sfx / music bed) or None."""
    if not au:
        return None
    mixed = any(au.get(k) for k in ('music', 'voice', 'sfx'))
    if au.get('path') and (au.get('copy') is True or not mixed):
        return 'ref'
    return 'mix' if mixed else None


def _ebur128(path):
    r = subprocess.run(['ffmpeg', '-v', 'info', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    i_ = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)
    tp = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)
    return (float(i_[-1]) if i_ else None), (float(tp[-1]) if tp else None)


def mix_music_only(au, total_s, out_wav, sr=48000):
    """Fallback mix: the music bed only (in / fades / gain), loudness loop of ed_render.render_audio: measure,
    static gain + limiter, re-measure until within 0.5 LU of the target."""
    m = au.get('music') or ({'path': au['path']} if au.get('path') else None)
    lo = au.get('loudness') or {}
    target = float(lo.get('lufs', au.get('loudnorm', -14)))
    tp = float(lo.get('tp', -1.0))
    if au.get('voice') or au.get('sfx'):
        log_once(('mix_drop',), 'ed_sfx.mix unavailable: voice / sfx dropped, music bed only')
    if not m or not m.get('path'):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'anullsrc=r={sr}:cl=stereo',
                        '-t', f'{total_s:.4f}', out_wav], check=True)
        return dict(lufs=None, tp=None, sfx_count=0, note='no music: silence')
    src = ['-ss', f"{float(m.get('in', 0.0)):.4f}", '-t', f'{total_s:.4f}', '-i', m['path']]
    fi, fo = float(m.get('fade_in', 0.0)), float(m.get('fade_out', 0.25))
    pre = [f'apad=whole_dur={total_s:.4f}']
    if fi > 0:
        pre.append(f'afade=t=in:st=0:d={fi}')
    if fo > 0:
        pre.append(f'afade=t=out:st={max(0.0, total_s - fo):.3f}:d={fo}')
    if m.get('gain_db'):
        pre.append(f"volume={float(m['gain_db']):.2f}dB")
    r = subprocess.run(['ffmpeg', '-v', 'info', '-nostats', '-y'] + src +
                       ['-af', ','.join(pre + [f'loudnorm=I={target}:TP={tp}:LRA=11:print_format=json']), '-f', 'null', '-'],
                       capture_output=True, text=True)
    try:
        j = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
        gain = target - float(j['input_i'])
        gain = gain if math.isfinite(gain) else 0.0
    except (ValueError, KeyError):
        gain = 0.0
    limit = min(1.0, 10 ** ((tp - 0.5) / 20))
    got = gtp = None
    for _ in range(4):
        chain = ','.join(pre + [f'volume={gain:.2f}dB', f'alimiter=limit={limit:.3f}:attack=3:release=60:level=false'])
        subprocess.run(['ffmpeg', '-v', 'error', '-y'] + src + ['-af', chain, '-ar', str(sr), '-ac', '2', out_wav], check=True)
        got, gtp = _ebur128(out_wav)
        if got is None or abs(target - got) <= 0.5:
            break
        gain += target - got
    return dict(lufs=got, tp=gtp, sfx_count=0)


AUDIO_CODEC, AUDIO_BITRATE = 'aac', '320k'


def encode_mix(wav, out, au=None, sr=48000):
    """Mixed WAV -> delivery AAC (out, .m4a) for the stream-copy mux: ed_sfx.encode_audio re-limits until the
    DECODED file still has true peak <= loudness.tp and the loudness of the WAV; fallback: plain ffmpeg AAC.
    -> dict(method, codec, bitrate, lufs, tp, ...) measured on the encoded file."""
    lo = (au or {}).get('loudness') or {}
    tp = float(lo.get('tp', -1.0))
    ok, res = EXT.call('ed_sfx', 'encode_audio',
                       _pool(('wav', wav, 'src in_wav path'), ('out', out, 'out_path dst'),
                             ('codec', AUDIO_CODEC, ''), ('bitrate', AUDIO_BITRATE, ''), ('tp_max', tp, 'tp'),
                             ('sr', sr, 'rate sample_rate')),
                       ('wav', 'out'), key='encode')
    if ok and isinstance(res, dict) and os.path.exists(out) and os.path.getsize(out) > 256:
        enc = {k: v for k, v in res.items() if isinstance(v, (int, float, str, bool, type(None))) and k != 'path'}
        enc['method'] = 'ed_sfx.encode_audio'
        return enc
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-c:a', 'aac', '-b:a', AUDIO_BITRATE, '-ar', str(sr),
                    out], check=True)
    got, gtp = _ebur128(out)
    return dict(method='ffmpeg', codec='aac', bitrate=AUDIO_BITRATE, lufs=got, tp=gtp)


def build_audio(au, total_s, out_wav, sr=48000, genre=None, enc_out=None):
    """Mixed soundtrack -> out_wav via ed_sfx.mix(audio, total_s, out_wav, sr) or the music-only fallback; the EDL's
    meta.genre picks the SFX style unless audio.sfx_style / audio.genre say otherwise. enc_out: also encode the
    delivery AAC there (encode_mix; runs in the audio thread, parallel to the video). -> sidecar 'audio' block."""
    tic = time.perf_counter()
    if genre and isinstance(au, dict) and not au.get('genre'):
        au = dict(au, genre=genre)
    ok, res = EXT.call('ed_sfx', 'mix',
                       _pool(('audio', au, 'spec cfg au a'), ('total_s', float(total_s), 'total dur duration seconds length'),
                             ('out_wav', out_wav, 'out out_path path wav dst'), ('sr', sr, 'rate sample_rate')),
                       ('audio', 'total_s', 'out_wav', 'sr'), key='mix')
    if ok and os.path.exists(out_wav) and os.path.getsize(out_wav) > 1024:
        res = res if isinstance(res, dict) else {}
        info = {k: v for k, v in res.items() if isinstance(v, (int, float, str, type(None)))}
        info['method'] = 'ed_sfx'
        if isinstance(res.get('warnings'), list):
            info['warnings'] = [str(w) for w in res['warnings']][:20]
        if isinstance(res.get('events'), list):
            # placed sfx: index in audio.sfx, kind, time, level preset, measured loudness over the program (st_lu,
            # the audibility rule ed_qa checks), its need and the dB the audibility floor added (floor_db, 0 = the
            # preset alone was enough); music-processing kinds carry music=true
            info['events'] = [{k: e.get(k) for k in ('i', 'kind', 'variant', 'at', 'start', 'end', 'level', 'lu',
                                                     'gain_db', 'need_lu', 'st_lu', 'floor_db', 'music', 'file',
                                                     'style')
                               if e.get(k) is not None} for e in res['events'] if isinstance(e, dict)][:300]
        if isinstance(res.get('audibility'), list):
            info['audibility'] = [{k: g.get(k) for k in ('t', 'kinds', 'events', 'span', 'need_lu', 'rel_lu',
                                                         'sfx_lufs', 'program_st_lufs', 'under_voice', 'ok', 'note')
                                   if g.get(k) is not None} for g in res['audibility'] if isinstance(g, dict)][:200]
        if isinstance(res.get('limiter'), dict):
            info['limiter'] = res['limiter']              # master gain, ceiling, gain reduction [[t, dB], ...]
    else:
        if ok:
            log_once(('mix_nofile',), 'ed_sfx.mix wrote no audio file; music-only fallback')
        info = mix_music_only(au, total_s, out_wav, sr)
        info['method'] = 'fallback-music'
    info['s'] = round(time.perf_counter() - tic, 2)
    if enc_out:
        t1 = time.perf_counter()
        try:
            info['encode'] = encode_mix(out_wav, enc_out, au, sr)
            info['encode']['s'] = round(time.perf_counter() - t1, 2)
        except Exception as e:  # the mux falls back to encoding the WAV itself
            info['encode'] = dict(method='failed', error=f'{type(e).__name__}: {e}'[:300])
    return info


# ----------------------------------------------------------------------------- timing
class _Timer:
    """Per-thread stage timers (thread time summed over workers)."""

    def __init__(self):
        self._loc = threading.local()
        self._all = []
        self._lock = threading.Lock()

    def add(self, key, dt):
        d = getattr(self._loc, 'd', None)
        if d is None:
            d = self._loc.d = {}
            with self._lock:
                self._all.append(d)
        d[key] = d.get(key, 0.0) + dt

    def __call__(self, key):
        return _Tick(self, key)

    def totals(self):
        out = {}
        for d in list(self._all):
            for k, v in list(d.items()):
                out[k] = out.get(k, 0.0) + v
        return {k: round(v, 3) for k, v in sorted(out.items())}


def _mmss(s):
    if s is None or not math.isfinite(s):
        return '--:--'
    s = int(round(s))
    return f'{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}' if s >= 3600 else f'{s // 60}:{s % 60:02d}'


class _Progress:
    """Render progress on stderr every ED_PROGRESS_S seconds (default 5; 0 = off): frames done / total, %, frames
    per second over the last interval, elapsed time and ETA."""

    def __init__(self, total, label):
        self.total, self.label = int(total), label
        self.every = float(os.environ.get('ED_PROGRESS_S', 5.0))
        self.t0 = self.last = time.perf_counter()
        self.done = self.done_last = 0
        self.printed = False

    def tick(self, n=1):
        self.done += n
        now = time.perf_counter()
        if self.every > 0 and now - self.last >= self.every and self.done < self.total:
            rate = (self.done - self.done_last) / max(now - self.last, 1e-9)
            avg = self.done / max(now - self.t0, 1e-9)
            speed = 0.5 * (rate + avg) if self.done_last else avg
            eta = (self.total - self.done) / speed if speed > 0 else None
            log(f'{self.label}: {self.done}/{self.total} frames ({100.0 * self.done / max(1, self.total):.0f}%), '
                f'{rate:.1f} fps, {_mmss(now - self.t0)} elapsed, ETA {_mmss(eta)}')
            self.last, self.done_last, self.printed = now, self.done, True

    def finish(self):
        if self.printed:
            el = time.perf_counter() - self.t0
            log(f'{self.label}: {self.done}/{self.total} frames (100%), {self.done / max(el, 1e-9):.1f} fps, '
                f'{_mmss(el)} total')


class _Tick:
    __slots__ = ('t', 'key', 't0')

    def __init__(self, t, key):
        self.t, self.key = t, key

    def __enter__(self):
        self.t0 = time.perf_counter()

    def __exit__(self, *a):
        self.t.add(self.key, time.perf_counter() - self.t0)


# ----------------------------------------------------------------------------- optical flow (new EDLs)
def flow_pair(f0, f1, fast=False, coarse=False):
    """DIS optical flow (medium preset) both ways between two uint8 RGB pictures, checked by forward-backward
    consistency -> (F01, F10, conf (H, W) float32 0..1 or None when consistent everywhere, ok). Computed at <= 960 px
    (fast previews: <= 480 px; interpolation error vs the true in-between frame 1.39 vs 1.36 levels at full size,
    a blend 2.9; coarse = <= 480 px, fast preset, half the time: 1.46 — frames with source-time blur) and scaled back.
    ok is False when the flow fails broadly (a cut or a flash between the frames, motion beyond the search range):
    the caller shows the nearest frame instead."""
    h, w = f0.shape[:2]
    s = min(1.0, (480.0 if fast or coarse else 960.0) / max(h, w))
    g0, g1 = cv2.cvtColor(f0, cv2.COLOR_RGB2GRAY), cv2.cvtColor(f1, cv2.COLOR_RGB2GRAY)
    if s < 1.0:
        sz = (max(8, int(round(w * s))), max(8, int(round(h * s))))
        g0, g1 = cv2.resize(g0, sz, interpolation=cv2.INTER_AREA), cv2.resize(g1, sz, interpolation=cv2.INTER_AREA)
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_FAST if coarse else cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    F01, F10 = dis.calc(g0, g1, None), dis.calc(g1, g0, None)
    hh, ww = g0.shape
    gx, gy = _pixel_grid(hh, ww)

    def occluded(Fa, Fb):            # pixels of frame a whose flow to b does not come back: not visible in b
        back = cv2.remap(Fb, gx + Fa[..., 0], gy + Fa[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        err = np.hypot(Fa[..., 0] + back[..., 0], Fa[..., 1] + back[..., 1])
        mag = np.hypot(Fa[..., 0], Fa[..., 1]) + np.hypot(back[..., 0], back[..., 1])
        return err > 1.0 + 0.15 * mag

    o01, o10 = occluded(F01, F10), occluded(F10, F01)
    share = 0.5 * float(o01.mean() + o10.mean())
    small = [cv2.resize(g, (32, 18), interpolation=cv2.INTER_AREA).astype(np.float32) for g in (g0, g1)]
    a0, a1 = small[0] - small[0].mean(), small[1] - small[1].mean()
    corr = float((a0 * a1).mean() / (a0.std() * a1.std() + 1e-6))
    ok = not (share > 0.6 or (share > 0.4 and corr < 0.5))   # a cut (or unrelated pictures): no interpolation
    vis = None
    if ok and share > 0.002:
        vis = tuple(cv2.GaussianBlur(1.0 - o.astype(np.float32), (0, 0), 1.0) for o in (o01, o10))
    if s < 1.0:
        F01 = cv2.resize(F01, (w, h), interpolation=cv2.INTER_LINEAR)
        F10 = cv2.resize(F10, (w, h), interpolation=cv2.INTER_LINEAR)
        np.multiply(F01, np.float32(w / ww), out=F01)
        np.multiply(F10, np.float32(w / ww), out=F10)
        if vis is not None:
            vis = tuple(cv2.resize(v, (w, h), interpolation=cv2.INTER_LINEAR) for v in vis)
    return F01, F10, vis, ok


def flow_interp(f0, f1, a, fl):
    """Picture at fraction a between f0 and f1 from flow_pair(): both frames warped to the intermediate time and
    blended by (1 - a, a), weighted by visibility (forward-backward consistency carried through the same warps):
    content hidden in one frame comes from the other; the nearest frame at a cut."""
    F01, F10, vis, ok = fl
    if not ok:
        return f0 if a < 0.5 else f1
    h, w = f0.shape[:2]
    gx, gy = _pixel_grid(h, w)
    af, bf = np.float32(a), np.float32(1.0 - a)
    m0x, m0y = gx - af * F01[..., 0], gy - af * F01[..., 1]
    m1x, m1y = gx - bf * F10[..., 0], gy - bf * F10[..., 1]
    w0 = cv2.remap(f0, m0x, m0y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    w1 = cv2.remap(f1, m1x, m1y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    if vis is None:
        return cv2.addWeighted(w0, 1 - a, w1, a, 0)
    v01 = cv2.remap(vis[0], m0x, m0y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)   # f0 content seen in f1
    v10 = cv2.remap(vis[1], m1x, m1y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)   # f1 content seen in f0
    A, B = bf * (0.05 + 0.95 * v10), af * (0.05 + 0.95 * v01)
    S = A + B
    out = (w0.astype(np.float32) * (A / S)[..., None] + w1.astype(np.float32) * (B / S)[..., None] + 0.5)
    return out.astype(np.uint8)


def vector_blur(img, v, span, scale=1.0, cap=24, step=2.0, offset=0.0):
    """Motion blur of source picture img along its own motion v (its optical flow to the next frame, px per source
    frame) over `span` source frames centred `offset` source frames after its time: the mean of img sampled at
    x - (offset + s) v(x), s at the midpoints of n equal parts of [-span/2, span/2]. Every sample is the picture moved
    along its flow to a moment inside the shutter, so moving edges smear smoothly (averaging neighbour frames shows
    each edge twice). Sample count from the motion: one per `step` output px of the longest blur (99.5th percentile;
    scale = output px per picture px), 2 .. cap (1 = a plain flow warp to `offset` when the blur is < 0.75 px); only
    the region moving >= 0.25 output px is resampled. -> (picture, samples used; 0 = nothing moves visibly)."""
    h, w = img.shape[:2]
    sub = v[::4, ::4]
    mag = np.sqrt(sub[..., 0] * sub[..., 0] + sub[..., 1] * sub[..., 1])
    top = float(np.percentile(mag, 99.5))
    reach = (abs(float(offset)) + 0.5 * float(span)) * float(scale)    # output px moved per px / frame of motion
    if not top * reach >= 0.25:
        return img, 0
    L = top * float(span) * float(scale)                                 # longest blur, output px
    n = 1 if L < 0.75 else int(min(max(math.ceil(L / step), 2), max(2, int(cap))))
    ys, xs = np.nonzero(mag * reach >= 0.25)
    y0, y1 = max(0, int(ys.min()) * 4 - 4), min(h, int(ys.max()) * 4 + 8)
    x0, x1 = max(0, int(xs.min()) * 4 - 4), min(w, int(xs.max()) * 4 + 8)
    vv = np.ascontiguousarray(v[y0:y1, x0:x1])
    gx, gy = _pixel_grid(h, w)
    grid = np.dstack([gx[y0:y1, x0:x1], gy[y0:y1, x0:x1]])
    acc = np.zeros((y1 - y0, x1 - x0) + img.shape[2:], np.float32)
    m = np.empty(vv.shape, np.float32)
    for s in ((np.arange(n) + 0.5) / n - 0.5) * float(span):
        cv2.scaleAdd(vv, -(float(offset) + float(s)), grid, dst=m)     # sample positions x - (offset + s) v(x)
        cv2.accumulate(cv2.remap(img, m, None, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE), acc)
    out = img.copy()
    out[y0:y1, x0:x1] = cv2.convertScaleAbs(acc, alpha=1.0 / n)
    return out, n


# ----------------------------------------------------------------------------- per-segment state
CAM_IDENT = dict(zoom=1.0, dx=0.0, dy=0.0, rot=0.0, blur=None, shutter=0.0, ids=[])


class SegState:
    """What one segment (or ghost) shares across its frames and render threads: decoded source span, optical
    flows, exposure stats, camera states, fx windows. Frame k may lie outside 0..n-1 (transition extensions)."""

    def __init__(self, R, seg, klo, khi, key, req=None, hint=None, ghosts=True):
        self.R, self.seg, self.key = R, seg, key
        self.src = R.sources[seg.get('src', 'film')]
        self.f0 = int(seg.get('f0', 0))
        self.n = int(seg['f1']) - self.f0 + 1
        self.klo, self.khi = min(klo, 0), max(khi, self.n - 1)
        self.mode = seg.get('interp', R.frame_interp)
        self.seed = zlib.crc32(str(seg.get('id', '')).encode())
        self.req, self.hint = req, hint
        self._span, self._stats, self._stats_ready = None, None, False
        self._span_lock, self._stats_lock = threading.Lock(), threading.Lock()
        self.flows, self._flow_locks, self._flow_lru = OrderedDict(), {}, threading.Lock()
        self._roi = False
        self.probe_raw, self.cam_cache = {}, {}
        fxs = list(seg.get('fx') or [])
        self.tblur = [fx for fx in fxs if fx.get('type') in TIME_BLUR_FX and fx.get('mode', 'frames') == 'frames']
        self.cam_fx = [fx for fx in fxs if R.is_camera(fx)]
        self.img_fx = [fx for fx in fxs if not R.is_camera(fx) and fx.get('type') not in TIME_BLUR_FX]
        self.cam_ext = [fx for fx in self.cam_fx if R.cam_ext(fx)]
        self.cam_loc = [fx for fx in self.cam_fx if not R.cam_ext(fx)]
        self.win, self.hits = {}, {}
        for fx in fxs + list(seg.get('post_text_fx') or []):
            self.win[id(fx)] = fx_window(fx, self.n, self.f0, R.fps)
            if fx.get('type') == 'shake.beat':
                if fx.get('hits') is not None or fx.get('beats') is not None:
                    self.hits[id(fx)] = frange(fx.get('hits') if fx.get('hits') is not None else fx['beats'])
                elif fx.get('times') is not None:
                    self.hits[id(fx)] = [snap(t, R.fps) - self.f0 for t in fx['times']]
        sh = seg.get('shutter', seg.get('motion_blur'))
        cam_mb = [fx for fx in fxs if fx.get('type') in TIME_BLUR_FX and fx.get('mode') == 'camera']
        if sh is None and cam_mb:
            sh = cam_mb[0].get('shutter', 0.5)
        self.shutter = None if sh is None else (0.5 if sh is True else float(sh or 0.0))
        tbl = seg.get('time_blur')
        try:
            fast = abs(float(seg.get('speed', 1.0))) >= 1.3
        except (TypeError, ValueError):
            fast = False
        auto = (tbl is None and self.shutter is None and self.mode != 'nearest'
                and bool(seg.get('speed_curve') or seg.get('times') or fast))
        if (not self.tblur and not R.legacy_decode and tbl is not False and self.shutter != 0.0
                and (tbl or (self.shutter or 0.0) > 1e-3 or auto)):
            # source-time motion blur on fast frames (speed ramps, velocity, fast-forward): automatic for speed
            # changes, and the segment shutter covers source motion too; 'time_blur': false / 'shutter': 0 /
            # frame_interp 'nearest' keep exact frames, a number sets its own shutter
            sh_t = float(tbl) if isinstance(tbl, (int, float)) and not isinstance(tbl, bool) else (self.shutter or 0.5)
            if sh_t > 1e-3:
                self.tblur = [dict(type='motion_blur', mode='frames', shutter=sh_t, move='time.motion_blur',
                                   min_rate=float(seg.get('time_blur_min_rate', 1.3)))]
        self.ghost_frames = [frange(gh.get('frames', [])) for gh in (seg.get('ghosts') or [])] if ghosts else []
        self.grade = seg.get('grade', {'preset': 'natural'})
        self.grades = seg.get('grades') or []
        self.v2 = not R.legacy_decode
        self.reader = self.mreader = self.geom = None
        self.smax = 1.0
        self.snap = self.v2 and self._whole_step()

    def time(self, k):
        return seg_time(self.seg, k, self.R.fps)

    # ------------------------------------------------------------------ source frames
    STREAM_MIN = int(os.environ.get('ED_STREAM_MIN', 96))   # legacy decode: spans of neighbours shared up to this

    def _whole_step(self):
        """Constant speed with a whole number of source frames per output frame (60 fps shown at 30, speed 1; equal
        rates; speed 2 at equal rates): every output frame shows one source frame as is — no interpolation."""
        s = self.seg
        if s.get('times') or s.get('speed_curve') or self.src.image:
            return bool(self.src.image)
        step = abs(float(s.get('speed', 1.0))) * self.src.fps / float(self.R.fps)
        return step >= 0.999 and abs(step - round(step)) < 1e-3

    def open(self):
        """(new EDLs) This segment's FrameReader(s), opened on first use (Renderer._open_reader)."""
        if self.reader is None:
            with self._span_lock:
                if self.reader is None:
                    self.reader, self.mreader = self.R._open_reader(self)
        return self.reader

    def get(self, i):
        """(new EDLs) Source frame with global index i; past the end of the stream the last frame."""
        D = self.open()
        f = D.get(i)
        if f is None:
            last = D.eof if D.eof is not None else int(i) - 1
            f = D.get(max(0, min(last, int(i) - 1)))
            if f is None:
                raise RuntimeError(f"no frames for segment {self.seg.get('id')} at frame {i} of {self.src.path}")
        return f

    def frame_at(self, t, mode, flows=None, probe=False):
        """Source picture (uint8) at source time t. Legacy decode: from the whole decoded span (box size). New EDLs:
        from the segment's reader (its decode geometry): the nearest frame for whole-step segments, positions within
        6 % of a frame and mode 'nearest'; else a linear blend or optical-flow interpolation (flow_interp)."""
        if not self.v2:
            st, fr = self.span()
            return Renderer.source_frame(fr, st, t, self.src.fps, mode, flows)
        pos = t * self.src.fps
        i0 = int(math.floor(pos + 1e-9))
        a = pos - i0
        if mode == 'nearest' or self.snap or a < 0.06 or a > 0.94:
            return self.get(int(math.floor(pos + 0.5)))
        f0 = self.get(i0)
        f1 = self.open().get(i0 + 1)
        if f1 is None:
            return f0
        if mode == 'blend':
            return cv2.addWeighted(f0, 1 - a, f1, a, 0)
        return flow_interp(f0, f1, a, self.flow_pair(i0, f0, f1))

    def blur_source(self, t):
        """(new EDLs; frames with source-time blur) The source frame nearer to time t, its motion (optical flow to the
        next frame, px per source frame) and the time from it to t in source frames -> (picture, field, offset) for
        vector_blur(), which moves the picture along its flow: no cross-fade of two frames under the blur. Without
        usable flow (a still, a cut, the stream end): (the picture at t as frame_at() shows it, None, 0). The flow is
        the coarse one (flow_pair coarse: <= 480 px, DIS fast preset)."""
        if self.src.image:
            return self.frame_at(t, self.mode), None, 0.0
        pos = t * self.src.fps
        i0 = int(math.floor(pos + 1e-9))
        a = pos - i0
        f0 = self.get(i0)
        f1 = self.open().get(i0 + 1)
        if f1 is None:
            return self.frame_at(t, self.mode), None, 0.0
        fl = self.flow_pair(i0, f0, f1, coarse=True)
        if not fl[3]:
            return self.frame_at(t, self.mode), None, 0.0
        if self.mode == 'nearest' or self.snap or a < 0.06 or a > 0.94:
            a = 0.0 if a < 0.5 else 1.0                 # frame_at shows the nearest frame: centred on it
        return (f0, fl[0], a) if a < 0.5 else (f1, -fl[1], a - 1.0)

    def flow_pair(self, i0, f0, f1, coarse=False):
        """(new EDLs) flow_pair() of source frames i0, i0 + 1, cached (LRU of FLOW_KEEP pairs). coarse=True (frames
        with source-time blur): the coarse flow, always (a frame never depends on what the cache holds)."""
        key = (i0, 'coarse') if coarse else i0
        with self._flow_lru:
            fl = self.flows.get(key)
            if fl is not None:
                self.flows.move_to_end(key)
                return fl
            lk = self._flow_locks.setdefault(key, threading.Lock())
        with lk:
            fl = self.flows.get(key)
            if fl is None:
                with self.R.T('flow'):
                    fl = flow_pair(f0, f1, fast=self.R.fast, coarse=coarse)
                with self._flow_lru:
                    self.flows[key] = fl
                    while len(self.flows) > self.FLOW_KEEP:
                        old, _ = self.flows.popitem(last=False)
                        self._flow_locks.pop(old, None)
        return fl

    def mask_at(self, t):
        """(new EDLs) External mask frame (uint8, mask reader geometry) at source time t, or None."""
        if self.mreader is None:
            return None
        mk = self.src.mask
        i = int(math.floor((t + float(mk.get('offset', 0.0))) * self.mreader.fps + 0.5))
        f = self.mreader.get(i)
        if f is None and self.mreader.eof is not None:
            f = self.mreader.get(self.mreader.eof)
        return f

    def close(self):
        for r in (self.reader, self.mreader):
            if r is not None:
                r.close()

    def span(self):
        if self._span is None:
            with self._span_lock:
                if self._span is None:
                    if self.req:
                        t0, t1 = self.req
                    else:
                        ts = [self.time(k) for k in range(self.klo, self.khi + 1)]
                        t0, t1 = min(ts) - 0.02, max(ts) + 1.5 / self.src.fps
                    with self.R.T('decode'):
                        st, fr = self.src.span(t0, t1, legacy=self.R.legacy_decode, hint=self.hint)
                    if len(fr) == 0:
                        raise RuntimeError(f"no frames for segment {self.seg.get('id')} at {t0:.3f}")
                    self._span = (st, fr)
        return self._span

    FLOW_KEEP = 8      # optical-flow pairs kept per segment (LRU; a recomputed pair is identical)

    def roi(self):
        """fast mode: source-box region the crop windows of this segment sample (all frames incl. extensions,
        camera fx, rotation; + margin) -> (x0, y0, x1, y1), or None when it is most of the frame."""
        if self._roi is False:
            R = self.R
            pts = np.float32([[0, 0], [R.ow, 0], [0, R.oh], [R.ow, R.oh]])
            lo, hi = np.array([np.inf, np.inf]), np.array([-np.inf, -np.inf])
            for k in range(self.klo, self.khi + 1):
                c = crop_state(self.seg, k, self.n)
                if self.cam_fx:
                    c = fold_camera(c, R._cam_state(self, k))
                cx, cy, ww, hw = window(self.src, c, R.ow, R.oh)
                M = affine(cx, cy, hw, R.ow, R.oh, c['rot'], c['dx'] * R.scale + c.get('odx', 0.0),
                           c['dy'] * R.scale + c.get('ody', 0.0))
                Mi = cv2.invertAffineTransform(M)
                q = pts @ Mi[:, :2].T + Mi[:, 2]
                lo, hi = np.minimum(lo, q.min(axis=0)), np.maximum(hi, q.max(axis=0))
            m = 48 + 0.08 * max(hi[0] - lo[0], hi[1] - lo[1])
            x0, y0 = int(max(0, math.floor(lo[0] - m))), int(max(0, math.floor(lo[1] - m)))
            x1, y1 = int(min(self.src.w, math.ceil(hi[0] + m))), int(min(self.src.h, math.ceil(hi[1] + m)))
            area = max(0, x1 - x0) * max(0, y1 - y0)
            self._roi = (x0, y0, x1, y1) if 0 < area < 0.6 * self.src.w * self.src.h else None
        return self._roi

    def flow_full(self, i0, f0, f1):
        return self.flow(i0, f0, f1, full=True)

    def flow(self, i0, f0, f1, full=False):
        full = full or not self.R.fast
        key = i0 if full else (i0, 'roi')
        with self._flow_lru:
            fl = self.flows.get(key)
            if fl is not None:
                self.flows.move_to_end(key)
                return fl
        lk = self._flow_locks.setdefault(key, threading.Lock())
        with lk:
            fl = self.flows.get(key)
            if fl is None:
                with self.R.T('flow'):
                    roi = None if full else self.roi()
                    if roi is not None:
                        x0, y0, x1, y1 = roi
                        f0, f1 = f0[y0:y1, x0:x1], f1[y0:y1, x0:x1]
                    g0 = cv2.cvtColor(f0, cv2.COLOR_RGB2GRAY)
                    g1 = cv2.cvtColor(f1, cv2.COLOR_RGB2GRAY)
                    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
                    fl = (dis.calc(g0, g1, None), dis.calc(g1, g0, None))
                    if roi is not None:
                        fl = fl + (roi,)
                with self._flow_lru:
                    self.flows[key] = fl
                    while len(self.flows) > self.FLOW_KEEP:
                        self.flows.popitem(last=False)
        return fl

    def stats(self):
        if not self._stats_ready:
            with self._stats_lock:
                if not self._stats_ready:
                    self._stats = self.R._grade_stats(self)
                    self._stats_ready = True
        return self._stats

    def grade_at(self, k):
        gk = self.grade
        for gr in self.grades:
            if gr['k0'] <= k <= gr['k1']:
                gk = gr['grade']
        return gk


_GRIDS, _GRIDS_LOCK = OrderedDict(), threading.Lock()


def _pixel_grid(h, w):
    """Pixel coordinate grids (gx, gy) float32 of an h x w picture (cached: the last 12 sizes)."""
    with _GRIDS_LOCK:
        g = _GRIDS.get((h, w))
        if g is not None:
            _GRIDS.move_to_end((h, w))
            return g
    g = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    with _GRIDS_LOCK:
        _GRIDS[(h, w)] = g
        while len(_GRIDS) > 12:
            _GRIDS.popitem(last=False)
    return g


def _beat_ctx(edl):
    """beats / downbeats / kicks (absolute output seconds) from the EDL: top level, meta, or meta.grid (ed_plan)."""
    out = {}
    meta = edl.get('meta') or {}
    grid = meta.get('grid') or {}
    for key in ('beats', 'downbeats', 'kicks'):
        for d in (edl, meta, edl.get('music') or {}, edl.get('analysis') or {}):
            if isinstance(d, dict) and d.get(key) is not None:
                out[key] = [float(v) for v in d[key]]
                break
    if 'beats' not in out and grid.get('beats'):
        out['beats'] = [float(v) for v in grid['beats']]
    if grid.get('beats') and 'downbeats' not in out and grid.get('pos'):
        out['downbeats'] = [float(b) for b, p in zip(grid['beats'], grid['pos']) if p == 0]
    if grid.get('beats') and 'kicks' not in out and grid.get('kick'):
        out['kicks'] = [float(b) for b, kk in zip(grid['beats'], grid['kick']) if kk]
    return out


# ----------------------------------------------------------------------------- main render
class Renderer:
    """Stage 1 (thread pool; pure): source frame -> camera fx + crop warp (+ motion blur) -> grade.
    Stage 2 (calling thread, output order): image fx, ghosts, transitions, ops, texts, layers, labels — every step
    that may keep sequential state (ed_fx temporal fx, ed_text caches) runs exactly as in a single-threaded render,
    so the output does not depend on the worker count."""

    def __init__(self, edl, preview=False, labels=False, interp=None, frame_interp=None, workers=None, chunk=None,
                 sidecar=True, max_blur_samples=None, fast=False):
        self.e = edl
        self.fast = bool(fast)          # previews: cheaper flow / warp / motion-blur sampling (not exact)
        self.frame_interp = frame_interp or edl.get('frame_interp', 'blend' if preview else 'flow')
        cv = edl['canvas']
        self.preview = bool(preview)
        self.scale = 0.5 if preview else 1.0
        self.ow, self.oh = int(cv['w'] * self.scale), int(cv['h'] * self.scale)
        self.W, self.H = int(cv['w']), int(cv['h'])
        self.fps = cv['fps']
        self.n = edl['n_frames']
        self.labels = labels
        legacy = 'meta' not in edl
        self.fx_impl = edl.get('fx_impl') or ('legacy' if legacy else 'auto')
        self.legacy_decode = edl.get('decode', 'legacy' if legacy else 'exact') == 'legacy'
        self.interp = interp or (cv2.INTER_CUBIC if preview else cv2.INTER_LANCZOS4)
        self.workers = max(1, int(workers or os.environ.get('ED_WORKERS', 0) or min(4, os.cpu_count() or 1)))
        self.chunk = max(1, int(chunk or os.environ.get('ED_CHUNK', 0) or 4))
        fb = self.ow * self.oh * 3 * 5             # stage-1 result: float32 frame + uint8 raw
        budget = int(float(os.environ.get('ED_LOOKAHEAD_MB', 160)) * 2 ** 20)
        self.lookahead = int(min(32, max(self.workers * 2, budget // fb)))
        self.sidecar = sidecar
        self.max_blur_samples = int(max_blur_samples or ((6 if self.fast else 12) if preview else 24))
        self.sharpen = edl.get('sharpen', 'auto')   # auto | false | amount: unsharp mask on upscaled crops
        self.T = _Timer()
        self.sources = {k: Source(v, k) for k, v in edl['sources'].items()}
        self.seg_decode = {}
        self._ext_masks, self._ext_lock = OrderedDict(), threading.Lock()
        self.label_box = None
        self.text = TextLayer(self.ow, self.oh, self.scale)
        self._mask_cache = {}
        self._pmask_cache = OrderedDict()
        reg = EXT.attr('ed_fx', 'FX_TYPES')
        self.fx_types = reg if isinstance(reg, dict) else None
        act = EXT.attr('ed_fx', 'active')
        self.fx_active = act if callable(act) else None
        ext_cam = EXT.attr('ed_fx', 'CAMERA_TYPES')
        if not isinstance(ext_cam, (set, frozenset, list, tuple, dict)):
            ext_cam = [t for t, fn in (self.fx_types or {}).items() if getattr(fn, 'kind', '') == 'camera']
        self.ext_cam_types = set(ext_cam)
        self.camera_types = set(CAMERA_FX) | self.ext_cam_types
        self.beat_ctx = _beat_ctx(edl)
        # ops by frame (+ index of the frame inside the op's own frame list, for curves)
        self.ops, self._op_j, self._op_index = {}, {}, {}
        for oi, op in enumerate(edl.get('ops', [])):
            self._op_index[id(op)] = oi
            for j, f in enumerate(frange(op['f'])):
                self.ops.setdefault(f, []).append(op)
                self._op_j[(id(op), f)] = j
        self.text_at = {}
        for tb in edl.get('texts', []):
            for f in range(tb['f0'], tb['f1'] + 1):
                self.text_at.setdefault(f, []).extend(tb['items'])
        self.segs = edl['segments']
        self.seg_of = {}
        for si, sg in enumerate(self.segs):
            for f in range(sg['f0'], sg['f1'] + 1):
                self.seg_of[f] = si
        self._plan_transitions()
        self.clip_no = {si: pos + 1 for pos, si in enumerate(self.order)}     # preview label '#N'
        self._plan_spans()
        self._plan_layers()
        self._states, self._ghost_states = {}, {}
        self._states_lock = threading.Lock()
        self.streamed = set()
        self.report = None

    # ---------------------------------------------------------------------------------------------- planning
    def _plan_transitions(self):
        """transition_in windows -> self.trans_at {f: info}; segment extensions (frames rendered before f0 /
        after f1); last output frame that needs each segment."""
        segs = self.segs
        order = sorted(range(len(segs)), key=lambda i: (segs[i]['f0'], i))
        self.order = order
        self.trans_at, self.windows = {}, []
        self.ext_pre, self.ext_post = [0] * len(segs), [0] * len(segs)
        last_w1 = -1
        for pos, si in enumerate(order):
            sg = segs[si]
            tr = sg.get('transition_in')
            if not tr or int(tr.get('frames', 6)) <= 0:
                continue
            F = int(tr.get('frames', 6))
            f0 = int(sg['f0'])
            w0 = f0 - F // 2 if tr.get('align', 'center') == 'center' else f0
            w1 = w0 + F - 1
            prev = order[pos - 1] if pos > 0 else None
            if prev is not None and int(segs[prev]['f1']) < f0 - 1:
                prev = None                                   # gap before the segment: blend from black
            w0 = max(w0, last_w1 + 1, 0, int(segs[prev]['f0']) if prev is not None else 0)
            w1 = min(w1, int(sg['f1']), self.n - 1)
            if w1 < w0:
                log_once(('trans_empty', si), f"transition_in of {sg.get('id', si)}: empty window, ignored")
                continue
            if w1 - w0 + 1 < F:
                log_once(('trans_clip', si), f"transition_in of {sg.get('id', si)}: window clipped to {w1 - w0 + 1} frames")
            info = dict(a=prev, b=si, F=w1 - w0 + 1, w0=w0, w1=w1, seam=min(max(f0 - w0, 0), w1 - w0 + 1), tr=tr)
            for f in range(w0, w1 + 1):
                self.trans_at[f] = info
            self.ext_pre[si] = max(self.ext_pre[si], f0 - w0)
            if prev is not None:
                self.ext_post[prev] = max(self.ext_post[prev], w1 - int(segs[prev]['f1']))
            last_w1 = w1
            self.windows.append(dict(kind=tr.get('kind', 'dissolve'), a=segs[prev].get('id', prev) if prev is not None else None,
                                     b=sg.get('id', si), w0=w0, w1=w1, align=tr.get('align', 'center')))
        self.last_f = [int(sg['f1']) + self.ext_post[i] for i, sg in enumerate(segs)]

    def _plan_spans(self):
        """Decode request per segment (the first engine's request, widened by transition extensions) and a shared
        decode hint: neighbours in time that read the same source within 0.5 s (continuation cuts, punch-ins) are
        decoded once."""
        self.span_req, self.span_hint = {}, {}
        reqs = []
        for si in self.order:
            sg = self.segs[si]
            src = self.sources.get(sg.get('src', 'film'))
            if src is None:
                continue
            n = int(sg['f1']) - int(sg['f0']) + 1
            ts = [seg_time(sg, k, self.fps) for k in range(-self.ext_pre[si], n + self.ext_post[si] + 1)]
            if self.legacy_decode:          # the first engine's request, exactly (legacy decode emulation)
                r = [si, sg.get('src', 'film'), min(ts[:-1]) - 0.02, max(ts[:-1]) + 1.5 / src.fps]
            else:                           # every interpolation pair (and temporal-blur sample) well inside
                pad = 0.0
                if any(fx.get('type') in TIME_BLUR_FX for fx in sg.get('fx') or []):
                    sh = max(float(fx.get('shutter', 0.5)) for fx in sg['fx'] if fx.get('type') in TIME_BLUR_FX)
                    pad = max(abs(b - a) for a, b in zip(ts, ts[1:])) * sh / 2
                r = [si, sg.get('src', 'film'), min(ts) - pad - 1.5 / src.fps, max(ts) + pad + 3.0 / src.fps]
            self.span_req[si] = (r[2], r[3])
            reqs.append(r)
        groups = []
        for r in reqs:
            g = groups[-1] if groups else None
            fps_src = self.sources[r[1]].fps
            short = (r[3] - r[2]) * fps_src <= SegState.STREAM_MIN       # long spans stream: never widened
            union = (max(r[3], max(x[3] for x in g)) - min(r[2], min(x[2] for x in g))) if g else 0.0
            if (g and short and g[0][1] == r[1] and r[2] <= max(x[3] for x in g) + 0.5
                    and r[3] >= min(x[2] for x in g) - 0.5 and union * fps_src <= SegState.STREAM_MIN):
                g.append(r)
            else:
                groups.append([r] if short else [])
                if not short:
                    groups.append([])
        for g in groups:
            if len(g) > 1:   # (empty groups separate long segments)
                t0, t1 = max(0.0, min(x[2] for x in g)), max(x[3] for x in g)
                for x in g:
                    self.span_hint[x[0]] = (t0, t1)

    def _plan_layers(self):
        """Animated layers (ed_text) indexed by frame span; static ctx for ed_text."""
        self.layers = list(self.e.get('layers') or [])
        q = self.e.get('qa') or {}
        ctx = dict(safe_zone=q.get('safe_zone') or self.e.get('safe_zone'), flash_limit_hz=q.get('flash_limit_hz'),
                   cuts=sorted({int(sg['f0']) for sg in self.segs if int(sg['f0']) > 0}), fps=self.fps,
                   canvas=dict(self.e['canvas']), n_frames=self.n)
        ctx.update(self.beat_ctx)
        for d in (self.e, self.e.get('meta') or {}):
            if isinstance(d, dict) and d.get('words') is not None:
                ctx['words'] = d['words']
                break
        self.text_ctx = {k: v for k, v in ctx.items() if v is not None}
        self.layer_spans = []
        for li, L in enumerate(self.layers):
            span = None
            if EXT.has('ed_text', 'layer_span'):
                with _TEXT_EXT_LOCK:
                    ok, res = EXT.call('ed_text', 'layer_span', _pool(('layer', L, 'spec item L cfg'), ('fps', self.fps, 'rate'),
                                                                     ('ctx', dict(self.text_ctx), 'context info')),
                                       ('layer', 'fps', 'ctx'), key=str(L.get('kind')))
                if ok and res is not None:
                    try:
                        span = (int(res[0]), int(res[1]))
                    except (TypeError, ValueError, IndexError):
                        span = None
            if span is None:
                f0 = L.get('f0', round(float(L['t0']) * self.fps) if L.get('t0') is not None else 0)
                f1 = L.get('f1', round(float(L['t1']) * self.fps) if L.get('t1') is not None else self.n - 1)
                span = (int(f0), int(f1))
            self.layer_spans.append(span)

    def layers_at(self, f):
        return [li for li, (a, b) in enumerate(self.layer_spans) if a <= f <= b]

    # ---------------------------------------------------------------------------------------------- routing
    def is_camera(self, fx):
        t = fx.get('type')
        if self.fx_impl == 'legacy' and t in LEGACY_FX:
            return False
        return t in self.camera_types or fx.get('family') == 'camera' or fx.get('camera') is True

    def _use_ext(self, d):
        impl = d.get('impl') or self.fx_impl
        if impl == 'local':
            return False
        return not (impl == 'legacy' and d.get('type') in LEGACY_FX)

    def cam_ext(self, fx):
        return (self._use_ext(fx) and EXT.has('ed_fx', 'camera')
                and (fx.get('type') in self.ext_cam_types if self.ext_cam_types else True))

    def img_ext(self, fx):
        if not self._use_ext(fx) or not EXT.has('ed_fx', 'apply'):
            return False
        if self.fx_types is None:
            return True
        fn = self.fx_types.get(fx.get('type'))
        return fn is not None and getattr(fn, 'kind', 'image') == 'image'

    # ---------------------------------------------------------------------------------------------- states
    def _state(self, si):
        S = self._states.get(si)
        if S is None:
            with self._states_lock:
                S = self._states.get(si)
                if S is None:
                    sg = self.segs[si]
                    S = SegState(self, sg, -self.ext_pre[si], int(sg['f1']) - int(sg['f0']) + self.ext_post[si], si,
                                 self.span_req.get(si), self.span_hint.get(si))
                    self._states[si] = S
        return S

    def _ghost_state(self, S, gi):
        key = (S.key, gi)
        G = self._ghost_states.get(key)
        if G is None:
            with self._states_lock:
                G = self._ghost_states.get(key)
                if G is None:
                    gh = (S.seg.get('ghosts') or [])[gi]
                    gseg = dict(gh)
                    gseg.setdefault('f0', 0)
                    gseg['f1'] = gh.get('n', 1) - 1
                    G = SegState(self, gseg, 0, gseg['f1'] - gseg['f0'], key, ghosts=False)
                    self._ghost_states[key] = G
        return G

    def _release_before(self, f):
        """Drop segment states (decoders, decoded frames, flows) that no frame >= f needs any more."""
        with self._states_lock:
            for si in [si for si in self._states if isinstance(si, int) and self.last_f[si] < f]:
                self._states.pop(si).close()
                for key in [k for k in self._ghost_states if k[0] == si]:
                    self._ghost_states.pop(key).close()

    # ---------------------------------------------------------------------------------------------- decoding plan
    HOLD_MB = float(os.environ.get('ED_HOLD_MB', 256))     # spans up to this size stay decoded whole

    def _box_affine(self, S, c):
        """2x3 matrix: source-box px -> output px for crop(+camera) state c."""
        cx, cy, ww, hw = window(S.src, c, self.ow, self.oh)
        return affine(cx, cy, hw, self.ow, self.oh, c['rot'], c['dx'] * self.scale + c.get('odx', 0.0),
                      c['dy'] * self.scale + c.get('ody', 0.0))

    def seg_geom(self, S):
        """Decode geometry of a segment (new EDLs): the box region its crop windows sample over all its frames —
        camera fx, rotation, shake and transition extensions included, plus a margin for the resampling kernel and
        optical flow — at the resolution its most zoomed-in frame needs (never above the source's; >= 85 % of it =
        full resolution). Also sets S.smax = output px per source px of that frame."""
        src = S.src
        pts = np.float64([[0, 0], [self.ow, 0], [0, self.oh], [self.ow, self.oh]])
        lo, hi, smax = np.array([np.inf, np.inf]), np.array([-np.inf, -np.inf]), 1e-6
        for k in range(S.klo, S.khi + 1):
            c = crop_state(S.seg, k, S.n)
            if S.cam_fx:
                c = fold_camera(c, self._cam_state(S, k))
            M = self._box_affine(S, c)
            Mi = cv2.invertAffineTransform(M)
            q = pts @ Mi[:, :2].T + Mi[:, 2]
            lo, hi = np.minimum(lo, q.min(axis=0)), np.maximum(hi, q.max(axis=0))
            smax = max(smax, math.sqrt(abs(np.linalg.det(M[:, :2]))))
        S.smax = smax
        span = float(max(hi - lo))
        m = 8.0 + 4.0 / smax + 0.04 * span
        x0, y0, x1, y1 = lo[0] - m, lo[1] - m, hi[0] + m, hi[1] + m
        if (min(x1, src.w) - max(x0, 0)) * (min(y1, src.h) - max(y0, 0)) > 0.8 * src.w * src.h:
            x0, y0, x1, y1 = 0, 0, src.w, src.h
        scale = min(1.0, smax)
        return src.geom(x0, y0, x1, y1, 1.0 if scale >= 0.85 else scale)

    def _open_reader(self, S):
        """FrameReader(s) of a segment (new EDLs): its decode geometry, the source-frame range of all its frames
        (+ temporal-blur reach), whole-span hold for short or non-monotonic spans, else a sliding window."""
        geom = self.seg_geom(S)
        S.geom = geom
        src = S.src
        fps = src.fps
        ts = [S.time(k) for k in range(S.klo, S.khi + 2)]
        steps = [abs(b - a) for a, b in zip(ts, ts[1:])] or [1.0 / self.fps]
        pad = max(steps) * max([float(fx.get('shutter', 0.5)) for fx in S.tblur] or [0.0])
        lo = max(0, int(math.floor((min(ts) - pad) * fps + 1e-9)) - 1)
        hi = int(math.floor((max(ts) + pad) * fps + 1e-9)) + 2
        rate = max(steps) * fps                                       # source frames per output frame
        mono = all(b >= a - 1e-9 for a, b in zip(ts, ts[1:]))
        nbytes = (hi - lo + 1) * geom.dw * geom.dh * 3
        hold = src.image or nbytes <= self.HOLD_MB * 2 ** 20 * (1 if mono else 4)   # reverse / jumps: 4x budget
        keep = hi - lo + 1 if hold else int(max(48, math.ceil((self.lookahead + 2 * self.chunk) * rate) + 16))
        ahead = int(max(4, math.ceil(2 * rate) + 2))
        rd = src.reader(geom, start=lo, keep=keep, ahead=ahead, hold=hold, hq=not self.preview)
        mr = None
        if src.mask:
            off, mfps = float(src.mask.get('offset', 0.0)), float(src.mask.get('fps') or src.mask_info['fps'])
            mr = src.mask_reader(geom, start=max(0, int(math.floor((min(ts) + off) * mfps)) - 1), keep=keep,
                                 ahead=ahead, hold=hold)
        if not hold:
            self.streamed.add(S.key)
        if isinstance(S.key, int):
            self.seg_decode[S.key] = dict(region=[geom.x, geom.y, geom.w, geom.h], size=[geom.dw, geom.dh],
                                          frames=[lo, hi], hold=bool(hold))
        return rd, mr

    # ---------------------------------------------------------------------------------------------- stage 1
    @staticmethod
    def source_frame(fr, st, t, fps, mode, flows):
        """Source frame at an arbitrary time: nearest, linear blend or optical-flow interpolation. flows: dict cache
        or callable (i0, f0, f1) -> (F01, F10)."""
        pos = (t - st[0]) * fps
        i0 = int(np.clip(math.floor(pos), 0, len(fr) - 1))
        a = pos - i0
        if mode == 'nearest' or i0 + 1 >= len(fr) or a < 0.06 or a > 0.94:
            return fr[int(np.clip(round(pos), 0, len(fr) - 1))]
        f0, f1 = fr[i0], fr[i0 + 1]
        if mode == 'blend':
            return cv2.addWeighted(f0, 1 - a, f1, a, 0)
        # 'flow': DIS optical flow both ways, warp both frames to the intermediate time and blend
        if callable(flows):
            fl = flows(i0, f0, f1)
            if len(fl) == 3:            # fast mode: flow inside the sampled region, linear blend outside it
                F01, F10, (x0, y0, x1, y1) = fl
                out = cv2.addWeighted(f0, 1 - a, f1, a, 0)
                out[y0:y1, x0:x1] = Renderer.source_frame(np.stack([f0[y0:y1, x0:x1], f1[y0:y1, x0:x1]]),
                                                          np.array([0.0, 1.0 / fps]), a / fps, fps, 'flow',
                                                          lambda *_: (F01, F10))
                return out
            F01, F10 = fl
        else:
            if i0 not in flows:
                g0 = cv2.cvtColor(f0, cv2.COLOR_RGB2GRAY)
                g1 = cv2.cvtColor(f1, cv2.COLOR_RGB2GRAY)
                dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
                flows[i0] = (dis.calc(g0, g1, None), dis.calc(g1, g0, None))
            F01, F10 = flows[i0]
        h, w = f0.shape[:2]
        gx, gy = _pixel_grid(h, w)
        a = float(a)
        b = np.float32(1 - a)
        af = np.float32(a)
        w0 = cv2.remap(f0, (gx - af * F01[..., 0]).astype(np.float32), (gy - af * F01[..., 1]).astype(np.float32),
                       cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        w1 = cv2.remap(f1, (gx - b * F10[..., 0]).astype(np.float32), (gy - b * F10[..., 1]).astype(np.float32),
                       cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        return cv2.addWeighted(w0, 1 - a, w1, a, 0)

    def _fx_ctx(self, S, k, raw=None, **extra):
        """ctx for ed_fx: ow, oh (output px), fps, f_abs, seg_f0, rng, beats, downbeats (absolute s), scale (+ more)."""
        d = dict(ow=self.ow, oh=self.oh, w=self.ow, h=self.oh, W=self.W, H=self.H, fps=float(self.fps),
                 f_abs=S.f0 + int(math.floor(k)), seg_f0=S.f0, scale=self.scale, rng=self._rng(S, k), k=k, n=S.n,
                 seg_id=S.seg.get('id'), seed=S.seed, preview=self.preview, raw=raw)
        d.update(self.beat_ctx)
        face = S.seg.get('_center') or (S.seg.get('crop') or {}).get('center')
        if face is not None:
            d['face'] = face
        m = self.ext_mask(S, k)
        if m is not None:
            d['mask'] = m                        # external subject mask (sources.<name>.mask), output size
        d.update(extra)
        return d

    def _rng(self, S, k):
        return np.random.default_rng([S.seed, int(math.floor(k)) + (1 << 20)])

    def _fx_on(self, S, fx, k):
        ka, kb, ks = S.win.get(id(fx)) or fx_window(fx, S.n, S.f0, self.fps)
        return (k in ks) if ks is not None else (ka <= k <= kb)

    def _cam_state(self, S, k):
        """Camera fx of segment S at integer frame k -> dict(zoom, dx, dy (output px), rot, blur (ed_fx sample
        spec | None), shutter (built-in moves), ids)."""
        st = S.cam_cache.get(k)
        if st is not None:
            return st
        zoom, dx, dy, rot, blur, shutter = 1.0, 0.0, 0.0, 0.0, None, 0.0
        loc = S.cam_loc
        if S.cam_ext:
            ok, cam = EXT.call('ed_fx', 'camera', _pool(
                ('fx_list', S.cam_ext, 'fxs fx items moves effects'), ('k', k, 'i j idx'),
                ('n', S.n, 'nk n_frames length count'), ('ctx', self._fx_ctx(S, k), 'context info'),
                ('fps', float(self.fps), 'rate')), ('fx_list', 'k', 'n', 'ctx'), check=_chk_cam, key='camera')
            if ok:
                zoom, dx, dy, rot, blur = cam['zoom'], cam['dx'], cam['dy'], cam['rot'], cam['blur']
            else:
                loc = S.cam_fx
        for fx in loc:
            if fx.get('type') not in CAMERA_FX:
                log_once(('cam_none', fx.get('type')), f"camera fx {fx.get('type')!r}: no built-in fallback; skipped")
                continue
            ka, kb, _ = S.win[id(fx)]
            z, x_, y_, r_, b_ = camera_local(fx, k, ka, kb, self.fps, self.H, S.hits.get(id(fx)))
            zoom, dx, dy, rot = zoom * z, dx + x_ * self.scale, dy + y_ * self.scale, rot + r_
            shutter = max(shutter, b_)
        moving = abs(zoom - 1.0) > 1e-4 or abs(dx) > 0.05 or abs(dy) > 0.05 or abs(rot) > 0.01
        ids = [move_id(fx) for fx in S.cam_fx
               if (self._fx_on(S, fx, k) if _has_window(fx) else moving)]   # event-driven moves: while moving
        st = dict(zoom=zoom, dx=dx, dy=dy, rot=rot, blur=blur, shutter=shutter, ids=ids)
        if len(S.cam_cache) > 512:
            S.cam_cache.clear()
        S.cam_cache[k] = st
        return st

    def _cam_at(self, S, kk):
        """Camera state at a fractional frame (between the integer states, zoom in log space)."""
        k0 = int(math.floor(kk))
        a = self._cam_state(S, k0)
        u = kk - k0
        return a if u < 1e-9 else lerp_cam(a, self._cam_state(S, k0 + 1), u)

    def _warp_c(self, S, f, c, interp, border, mip=None):
        """Warp picture f of segment S to the output for crop(+camera) state c. New EDLs: f is a picture of the
        segment's decode geometry (its mapping is composed into the matrix); when the warp shrinks it below 0.6x a
        half-resolution, area-filtered level (mip()) is warped instead (no aliasing); Lanczos only near 1:1."""
        M = self._box_affine(S, c)
        g = S.geom
        if g is not None and f.shape[:2] == (g.dh, g.dw):
            M = compose(M, g.dec_to_box())
            fac = math.sqrt(abs(np.linalg.det(M[:, :2])))
            if fac < 0.6 and mip is not None:
                f, D = mip()
                M = compose(M, D)
                fac *= 2.0
            if interp == cv2.INTER_LANCZOS4 and fac < 0.9:
                interp = cv2.INTER_CUBIC
        return warp_m(f, M, self.ow, self.oh, interp, border)

    def _sharpen(self, S, w, c, f=None):
        """Post-upscale sharpening (new EDLs) of picture w, warped from the decoded picture f by crop state c:
        sharpen_upscaled() when this render enlarges the picture more than 1.1x (output px per decoded px) — gentle
        (0.24 at 1.78x on clean / generated footage), adaptive to the scale, the source's noise floor and the frame's
        fine-texture floor, never past the source's local range (no halo or ringing). Segments interpolated by 'blend'
        (cross-fades: previews) are sharpened without coring (coring=False), all their frames alike. Motion-blurred
        frames are not sharpened. 'sharpen' (EDL top level or segment): 'auto' (default) | false | a fixed amount
        (any scale)."""
        mode = S.seg.get('sharpen', self.sharpen)
        if not S.v2 or mode is False or mode in (None, 0, 'off', 'none', 'false'):
            return w
        M = self._box_affine(S, c)
        g = S.geom
        if f is not None and g is not None and f.shape[:2] == (g.dh, g.dw):
            M = compose(M, g.dec_to_box())
        else:
            f = None
        u = math.sqrt(abs(np.linalg.det(np.asarray(M)[:, :2])))           # output px per picture px
        fixed = isinstance(mode, (int, float)) and not isinstance(mode, bool)
        if not fixed and u <= 1.1:
            return w
        with self.T('sharpen'):
            return sharpen_upscaled(w, f, M, u, float(mode) if fixed else None, S.seg.get('border', 'reflect'),
                                    coring=not (S.mode == 'blend' and not S.snap))

    def _store_mask(self, S, k, c):
        """External mask (sources.<name>.mask) of frame k warped like the picture (state c), kept for stage 2."""
        if S.mreader is None:
            return
        fr = S.mask_at(S.time(k))
        if fr is None:
            return
        M = compose(self._box_affine(S, c), S.mreader.geom.dec_to_box())
        m = cv2.warpAffine(fr, M, (self.ow, self.oh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                           borderValue=0).astype(np.float32) / 255.0
        if S.src.mask.get('invert'):
            m = 1.0 - m
        with self._ext_lock:
            self._ext_masks[(S.key, int(k))] = m
            while len(self._ext_masks) > 3 * self.lookahead + 8:
                self._ext_masks.popitem(last=False)

    def ext_mask(self, S, k):
        """External subject mask (oh, ow) float32 0..1 of segment S frame k, or None."""
        if S is None or S.mreader is None:
            return None
        with self._ext_lock:
            return self._ext_masks.get((S.key, int(math.floor(k))))

    def _raw_plain(self, S, k, probe=False):
        """Warped source frame without camera fx (legacy decode: also the exposure probes, which always use
        full-frame flow so fast previews grade exactly like the final; identical to the first engine's raw frame)."""
        c = crop_state(S.seg, k, S.n)
        cx, cy, ww, hw = window(S.src, c, self.ow, self.oh)
        with self.T('source'):
            f = S.frame_at(S.time(k), S.mode, S.flow_full if probe else S.flow, probe=probe)
            f = S.src.clean_logo(f, (cx - ww / 2, cy - hw / 2, cx + ww / 2, cy + hw / 2), S.geom)
        with self.T('warp'):
            w = self._warp_c(S, f, c, self.interp, S.seg.get('border', 'reflect'), _mip_fn(f))
        if S.v2 and not probe:
            self._store_mask(S, k, c)
            w = self._sharpen(S, w, c, f)
        return w

    def _raw(self, S, k):
        """-> (warped uint8 frame, source time, active camera move ids). Camera fx are folded into the crop warp;
        motion blur = mean of warps at the camera's sample states (ed_fx) or at sub-frame positions over the
        shutter (built-in moves, segment 'shutter')."""
        t_src = S.time(k)
        tb = self._time_blur(S, k) if S.tblur else None
        if not S.cam_fx and S.shutter is None and tb is None:
            raw = S.probe_raw.get(k)
            return (raw if raw is not None else self._raw_plain(S, k)), t_src, []
        cam = self._cam_state(S, k) if S.cam_fx else CAM_IDENT
        c0 = crop_state(S.seg, k, S.n)
        c = fold_camera(c0, cam)
        cx, cy, ww, hw = window(S.src, c, self.ow, self.oh)
        with self.T('source'):
            if tb is None:
                f = S.frame_at(t_src, S.mode, S.flow)
            elif S.v2:      # motion-compensated: the picture blurred along its optical flow over the shutter span
                f = self._vector_blur(S, t_src, tb, c)
            else:           # legacy: mean of linearly blended source frames over the shutter span
                acc = None
                for ts in tb[0]:
                    fr = S.frame_at(ts, 'nearest' if S.mode == 'nearest' else 'blend', None)
                    acc = fr.astype(np.float32) if acc is None else acc + fr
                f = (acc / len(tb[0]) + 0.5).astype(np.uint8)
            f = S.src.clean_logo(f, (cx - ww / 2, cy - hw / 2, cx + ww / 2, cy + hw / 2), S.geom)
        border = S.seg.get('border', 'reflect')
        mip = _mip_fn(f)
        with self.T('warp'):
            samples = None
            if S.shutter is not None:
                samples = self._sub_samples(S, k, S.shutter) if S.shutter > 1e-3 else None
            elif cam['blur']:
                samples = [fold_camera(c0, s) for s in cam['blur']['samples']]
            elif cam['shutter'] > 1e-3:
                samples = self._sub_samples(S, k, cam['shutter'])
            if samples and len(samples) > 1:
                flags = cv2.INTER_LINEAR if len(samples) > 2 else self.interp
                acc = np.zeros((self.oh, self.ow, 3), np.float32)
                for cs in samples:
                    acc += self._warp_c(S, f, cs, flags, border, mip)
                w = (acc / len(samples) + 0.5).astype(np.uint8)
            else:
                w = self._warp_c(S, f, c, self.interp, border, mip)
        if S.v2:
            self._store_mask(S, k, c)
            if not (samples and len(samples) > 1) and tb is None:      # motion-blurred frames stay soft
                w = self._sharpen(S, w, c, f)
        return w, t_src, cam['ids'] + ([tb[1]] if tb else [])

    def _time_blur(self, S, k):
        """Temporal motion blur of fast frames (move time.velocity / time.motion_blur, same rule as
        ed_fx.shutter_spec): rate r = source s per output s at k; when |r| >= min_rate the shutter spans
        |r| shutter / fps_out source seconds centred on the frame's source time -> (sample times, move id, span in
        source frames, sample cap) | None. New EDLs blur along the optical flow (_vector_blur: samples from the
        motion, cap = fx max_n or max_blur_samples); legacy EDLs average n = clamp(ceil(2 |r| shutter fps_src /
        fps_out), 2, max_n 12) linearly blended source frames at the sample times."""
        for fx in S.tblur:
            if not self._fx_on(S, fx, k):
                continue
            r = (S.time(k + 1) - S.time(k)) * self.fps
            sh, mr = float(fx.get('shutter', 0.5)), float(fx.get('min_rate', 1.2))
            if abs(r) < mr or sh <= 0:
                continue
            n = int(min(max(math.ceil(2 * abs(r) * sh * S.src.fps / self.fps), 2), int(fx.get('max_n', 12))))
            span = abs(r) * sh / self.fps
            t = S.time(k)
            return ([t + float(o) for o in np.linspace(-span / 2, span / 2, n)], move_id(fx), span * S.src.fps,
                    int(fx.get('max_n') or self.max_blur_samples))
        return None

    def _vector_blur(self, S, t, tb, c):
        """Source-time motion blur of new EDLs (_time_blur spec tb, crop state c): the source frame nearer to t
        moved along its optical flow to the moments of the shutter span around t and averaged (vector_blur) — one
        sample per ~2 output px of motion, at most tb cap (24 final, 12 preview, 6 --fast by default); the picture
        at t unblurred at a cut."""
        pic, v, off = S.blur_source(t)
        if v is None:
            return pic
        M = self._box_affine(S, c)
        if S.geom is not None and pic.shape[:2] == (S.geom.dh, S.geom.dw):
            M = compose(M, S.geom.dec_to_box())
        u = math.sqrt(abs(np.linalg.det(np.asarray(M)[:, :2])))           # output px per picture px
        with self.T('time_blur'):
            return vector_blur(pic, v, tb[2], u, tb[3], offset=off)[0]

    def _sub_samples(self, S, k, shutter):
        """Crop+camera states at sub-frame positions k - shutter .. k (trailing shutter, like ed_fx); count from the
        frame-corner displacement (None = no visible motion)."""
        ka = k - min(float(shutter), 1.0)

        def c_at(kk):
            c = crop_state(S.seg, kk, S.n)
            return fold_camera(c, self._cam_at(S, kk)) if S.cam_fx else c

        def mat(c):
            cx, cy, ww, hw = window(S.src, c, self.ow, self.oh)
            return affine(cx, cy, hw, self.ow, self.oh, c['rot'], c['dx'] * self.scale + c.get('odx', 0.0),
                          c['dy'] * self.scale + c.get('ody', 0.0))

        Ma, Mb = mat(c_at(ka)), mat(c_at(k))
        pts = np.float32([[0, 0], [self.ow, 0], [0, self.oh], [self.ow, self.oh], [self.ow / 2, self.oh / 2]])
        Ia = cv2.invertAffineTransform(Ma)
        disp = float(np.abs((pts @ Ia[:, :2].T + Ia[:, 2]) @ Mb[:, :2].T + Mb[:, 2] - pts).max())
        N = int(min(self.max_blur_samples, max(1, math.ceil(disp / 1.5))))
        if N <= 1:
            return None
        return [c_at(ka + (k - ka) * j / (N - 1)) for j in range(N)]

    def _grade_stats(self, S):
        """Exposure stats of a segment from up to 5 frames spread over 0..n-1, rendered like the frames themselves
        (no camera fx), so partial renders, stills and ghosts grade like a full render (new EDLs: _grade_stats_v2)."""
        g = S.grade
        if not any(grade_params(gg).get('auto', 0.0) > 0 for gg in [g] + [gr['grade'] for gr in S.grades]):
            return None
        if S.v2:
            return self._grade_stats_v2(S)
        n = S.n
        probe_k = sorted(set(int(round(v)) for v in np.linspace(0, n - 1, min(5, n))))
        probe = []
        for k in probe_k:
            raw = self._raw_plain(S, k, probe=True)
            S.probe_raw[k] = raw
            probe.append(raw)
        stats = grade_stats([cv2.resize(p, (self.ow // 4, self.oh // 4)).astype(np.float32) / 255.0 for p in probe],
                            skip_black=S.seg.get('border') == 'black')
        if g.get('stats'):
            stats.update(g['stats'])
        return stats

    def _grade_stats_v2(self, S):
        """Exposure stats (new EDLs) from up to 5 frames of the segment, each warped by its crop window (no camera
        fx) to 1/4 of the output size: the key frames inside its source span when there are 3 or more (decoded alone,
        no extra pass over the span), else the frames at k = 0, n/2, n-1. The probe frames are the segment's own
        decoded pictures (held span, key-frame decode or seek: the same pixels), so the grade does not depend on the
        decoding strategy, the worker count, partial renders or --fast."""
        n, fps = S.n, S.src.fps
        D = S.open()
        g = S.geom
        tk = np.array([S.time(k) for k in range(n)])
        ta, tb = float(tk.min()), float(tk.max())
        kf = [] if S.src.image else D.keyframe_list(ta, tb)
        if len(kf) >= 3:
            idx = sorted({kf[int(round(j))] for j in np.linspace(0, len(kf) - 1, min(5, len(kf)))})
            ks = [int(np.argmin(np.abs(tk - i / fps))) for i in idx]
        else:
            ks = sorted({0, n // 2, n - 1})
            idx = [int(math.floor(tk[k] * fps + 0.5)) for k in ks]
        got = {}
        if not D.hold and len(kf) >= 3:
            got = D.decode_keyframes(kf[kf.index(idx[0]):kf.index(idx[-1]) + 1], idx)
        if not D.hold and not got:
            got = D.fetch(idx)
        probes = []
        for k, i in zip(ks, idx):
            fr = got.get(i) if got else S.get(i)
            if fr is not None:
                probes.append((k, fr))
        if not probes:
            return None
        sw, sh = max(8, self.ow // 4), max(8, self.oh // 4)
        ax, ay = sw / self.ow, sh / self.oh
        D4 = np.array([[ax, 0.0, 0.5 * ax - 0.5], [0.0, ay, 0.5 * ay - 0.5]])
        border = S.seg.get('border', 'reflect')
        ims = []
        for k, fr in probes:
            c = crop_state(S.seg, k, S.n)
            cx, cy, ww, hw = window(S.src, c, self.ow, self.oh)
            fr = S.src.clean_logo(fr, (cx - ww / 2, cy - hw / 2, cx + ww / 2, cy + hw / 2), g)
            M = compose(D4, compose(self._box_affine(S, c), g.dec_to_box()))
            fac = math.sqrt(abs(np.linalg.det(M[:, :2])))
            if fac < 0.5:                                    # area-filter first: no aliasing in the statistics
                q = min(1.0, 2.0 * fac)
                h0, w0 = fr.shape[:2]
                w2, h2 = max(2, int(round(w0 * q))), max(2, int(round(h0 * q)))
                fr = cv2.resize(fr, (w2, h2), interpolation=cv2.INTER_AREA)
                qx, qy = w0 / w2, h0 / h2
                M = compose(M, np.array([[qx, 0.0, 0.5 * qx - 0.5], [0.0, qy, 0.5 * qy - 0.5]]))
            ims.append(warp_m(fr, M, sw, sh, cv2.INTER_LINEAR, border).astype(np.float32) / 255.0)
        stats = grade_stats(ims, skip_black=border == 'black')
        if S.grade.get('stats'):
            stats.update(S.grade['stats'])
        return stats

    def _pre_seg(self, S, k):
        """Stage 1 of segment frame k: source -> warp -> grade (+ the same for ghosts shown on this frame)."""
        stats = S.stats()
        raw, t_src, cam_ids = self._raw(S, k)
        with self.T('grade'):
            if S.v2:
                x = apply_grade_fast(np.multiply(raw, np.float32(1.0 / 255.0), dtype=np.float32), S.grade_at(k), stats)
            else:
                x = apply_grade(raw.astype(np.float32) / 255.0, S.grade_at(k), stats)
        gh = None
        if S.ghost_frames:
            f = S.f0 + k
            for gi, fl in enumerate(S.ghost_frames):
                if f in fl:
                    spec = S.seg['ghosts'][gi]
                    n_g = spec.get('n', 1)
                    j = fl.index(f) % n_g if spec.get('cycle') else min(fl.index(f), n_g - 1)
                    GS = self._ghost_state(S, gi)
                    gh = gh or {}
                    gh[gi] = (GS, j, self._pre_seg(GS, j))
        return x, raw, t_src, cam_ids, gh

    def _pre_frame(self, f):
        """Stage 1 of output frame f (one segment, or both sides of a transition)."""
        T = self.trans_at.get(f)
        if T is not None:
            B = self._state(T['b'])
            out = {'b': self._pre_seg(B, f - B.f0)}
            if T['a'] is not None:
                A = self._state(T['a'])
                out['a'] = self._pre_seg(A, f - A.f0)
            return out
        si = self.seg_of.get(f)
        if si is None:
            return {}
        S = self._state(si)
        return {'s': self._pre_seg(S, f - S.f0)}

    # ---------------------------------------------------------------------------------------------- stage 2
    def _image_fx(self, S, x, k, fxs=None, raw=None, rng=None):
        """Image fx on frame k in list order: ed_fx.apply for the types it registers, else the built-in ones."""
        fxs = S.img_fx if fxs is None else fxs
        ids = []
        ctx = None
        for fx in fxs:
            if self.is_camera(fx):
                continue
            typ = fx.get('type')
            ext = self.img_ext(fx)
            if ext:
                ctx = ctx or self._fx_ctx(S, k, raw)
                on = self._fx_on(S, fx, k)
                if self.fx_active is not None:
                    try:
                        on = bool(self.fx_active(fx, k, S.n, ctx))
                    except Exception as e:
                        log_once(('fx_active', typ), f'ed_fx.active({typ}) failed ({type(e).__name__}: {e})')
                if not on:
                    continue
                ok, y = EXT.call('ed_fx', 'apply', _pool(
                    ('x', x, 'img image frame rgb'), ('fx_list', [fx], 'fxs fx items effects'), ('k', k, 'i j idx'),
                    ('n', S.n, 'nk n_frames length count'), ('ctx', ctx, 'context info')),
                    ('x', 'fx_list', 'k', 'n', 'ctx'), check=_img_check(x), key=typ)
                if ok:
                    x = y
                    ids.append(move_id(fx))
                    continue
            elif not self._fx_on(S, fx, k):
                continue
            if typ not in LOCAL_FX:
                log_once(('fx_none', typ), f'fx {typ!r}: no implementation (ed_fx missing or failed); skipped')
                continue
            x = apply_fx_one(x, fx, k, S.n, self.ow, self.oh, rng if rng is not None else self._rng(S, k))
            ids.append(move_id(fx))
        return x, ids

    def _post_seg(self, S, k, pre):
        """Stage 2 of segment frame k: image fx (may keep sequential state), ghosts -> (x, fx ids)."""
        x, raw, _, _, gh = pre
        fx_ids = []
        if S.img_fx:
            with self.T('fx'):
                x, fx_ids = self._image_fx(S, x, k, raw=raw)
        if gh:
            with self.T('ghost'):
                x = self._ghosts(x, S, k, gh)
        return x, fx_ids

    def _seg_frame(self, S, k):
        pre = self._pre_seg(S, k)
        x, fx_ids = self._post_seg(S, k, pre)
        return x, pre[1], pre[2], pre[3], fx_ids

    def seg_frames(self, sg, only=None):
        """{k: (x float32, raw uint8, source t)} for one segment dict (API of the first engine; no ghosts)."""
        n = int(sg['f1']) - int(sg.get('f0', 0)) + 1
        S = SegState(self, sg, 0, n - 1, ('adhoc', id(sg)), ghosts=False)
        ks = range(n) if only is None else [k for k in only if 0 <= k < n]
        try:
            return {k: self._seg_frame(S, k)[:3] for k in ks}
        finally:
            S.close()

    def _ghosts(self, x, S, k, gh):
        for gi, spec in enumerate(S.seg.get('ghosts') or []):
            if gi not in gh:
                continue
            GS, j, gpre = gh[gi]
            gx = self._post_seg(GS, j, gpre)[0]
            m = np.ones(x.shape[:2], np.float32)
            if spec.get('dark_mask'):
                thr = spec.get('thr', 0.18)
                m = np.clip((thr - luma(x)) / thr, 0, 1)
                m = cv2.GaussianBlur(m, (0, 0), max(1.0, 3 * self.scale))
            if spec.get('ellipse'):
                cx, cy, rx, ry = spec['ellipse']
                m = m * ellipse_mask(self.ow, self.oh, cx, cy, rx, ry, spec.get('feather', 0.35))
            a = (m * spec.get('alpha', 1.0))[..., None]
            mode = spec.get('mode', 'screen')
            if mode == 'screen':
                y = 1 - (1 - x) * (1 - gx)
            elif mode == 'add':
                y = np.clip(x + gx, 0, 1)
            else:
                y = gx
            x = x * (1 - a) + y * a
        return x

    def overlay_ghost(self, x, sg, k, base_u8=None):
        """API of the first engine: ghosts of segment dict sg on its frame k."""
        n = int(sg['f1']) - int(sg['f0']) + 1
        S = SegState(self, sg, 0, n - 1, ('adhoc', id(sg)))
        try:
            gh = self._pre_seg(S, k)[4]
            return self._ghosts(x, S, k, gh) if gh else x
        finally:
            S.close()
            for key in [key for key in self._ghost_states if key[0] == S.key]:
                self._ghost_states.pop(key).close()

    def frame_ops(self, x, f, raw_u8, sg, stage='pre', applied=None, mask=None, boxes=None):
        """Frame ops of frame f at one stage; mask = external subject mask of the frame (mask_flash uses it
        instead of the person segmentation); boxes (list) receives where each applied op draws (_op_box)."""
        for op in self.ops.get(f, []):
            if op.get('stage', 'pre') != stage:
                continue
            o = op['op']
            op_mask = None
            if o == 'invert':
                x = 1 - x
            elif o == 'white':
                a = op.get('a', 1.0)
                x = x * (1 - a) + a
            elif o == 'black':
                x = x * (1 - op.get('a', 1.0))
            elif o == 'mask_flash':
                base = (np.clip(x, 0, 1) * 255).astype(np.uint8)
                key = (sg.get('id') if sg else None, f)
                if mask is not None:
                    self._mask_cache[key] = mask
                if key not in self._mask_cache:
                    with _MASK_LOCK:
                        m = V.person_mask_hq(base).astype(np.float32)
                    m = cv2.morphologyEx((m > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)).astype(np.float32) * 0.6 + m * 0.4
                    m = guided_filter(cv2.cvtColor(base, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0, m, max(2, self.ow // 270), 1e-3)
                    self._mask_cache[key] = np.clip(m, 0, 1)
                m = self._mask_cache[key]
                if op.get('mask_fn'):
                    m = m * (m > op.get('mask_thr', 0.5))
                if op.get('clip_box'):
                    cb = op['clip_box']
                    cm = np.zeros_like(m)
                    cm[int(cb[1] * self.oh):int(cb[3] * self.oh), int(cb[0] * self.ow):int(cb[2] * self.ow)] = 1
                    m = m * cm
                a = (np.clip((m - 0.35) / 0.3, 0, 1) * op.get('a', 1.0))[..., None]
                col = np.array(op.get('color', [1, 1, 1]), np.float32)
                x = x * (1 - a) + col * a
                op_mask = m
            elif o == 'rect_flash':
                r = op['rect']
                m = np.zeros((self.oh, self.ow), np.float32)
                cv2.rectangle(m, (int(r[0] * self.ow), int(r[1] * self.oh)), (int(r[2] * self.ow), int(r[3] * self.oh)), 1.0, -1)
                if op.get('feather'):
                    m = cv2.GaussianBlur(m, (0, 0), op['feather'] * self.scale)
                if op.get('shape') == 'object':
                    # fill the bright object inside the rect (luminance key, dilated) instead of a flat box
                    L = luma(x)
                    sel = (L > op.get('thr', 0.2)).astype(np.uint8)
                    d = int(op.get('dilate', 3) * self.scale * 2) + 1
                    sel = cv2.dilate(sel, np.ones((d, d), np.uint8)).astype(np.float32)
                    sel = cv2.GaussianBlur(sel, (0, 0), max(0.8, 1.5 * self.scale))
                    m = m * np.maximum(sel, op.get('floor', 0.0))
                a = (m * op.get('a', 1.0))[..., None]
                x = x * (1 - a) + a
            elif o == 'hud_tc':
                x = draw_hud_tc(x, op['tc'], self.scale, invert=op.get('invert', False))
            elif o == 'flash':
                j = self._op_j.get((id(op), f), 0)
                ok = False
                if (op.get('impl') or self.fx_impl) != 'local':
                    ctx = dict(ow=self.ow, oh=self.oh, fps=float(self.fps), f_abs=f, scale=self.scale, **self.beat_ctx)
                    ok, y = EXT.call('ed_fx', 'flash_op', _pool(
                        ('x', x, 'img image frame rgb'), ('op', op, 'spec item cfg params fx'),
                        ('j', j, 'i k idx step index'), ('ctx', ctx, 'context info')),
                        ('x', 'op', 'j', 'ctx'), check=_img_check(x), key='flash')
                    if ok:
                        x = y
                if not ok:
                    x = flash_local(x, op, j)
            else:
                log_once(('op_unknown', o), f'op {o!r}: unknown, skipped')
                continue
            if applied is not None:
                applied.append(move_id(op, o) if op.get('move') else o)
            if boxes is not None:
                ob = self._op_box(op, o, f, op_mask)
                if ob is not None:
                    boxes.append(ob)
        return x

    def _op_box(self, op, o, f, mask=None):
        """Where an applied frame op draws (canvas px) for the boxes sidecar: dict(id 'op<i>:<name>', kind, bbox,
        flags ['op', 'full'?, 'opaque'?]) — full-frame ops (invert / white / black / flash), rect_flash rectangles,
        the hud_tc panel, mask_flash mask extent."""
        W, H = self.W, self.H
        oid = f"op{self._op_index.get(id(op), '?')}:{o}"
        a = float(op.get('a', 1.0))
        if o == 'flash':
            curve = flash_curve(op)
            j = self._op_j.get((id(op), f), 0)
            a *= curve[j] if 0 <= j < len(curve) else 0.0
        flags = ['op']
        if o in ('invert', 'white', 'black', 'flash'):
            box = [0.0, 0.0, float(W), float(H)]
            flags.append('full')
            if o != 'invert' and a >= 0.9 and (o != 'flash' or op.get('blend', 'normal') == 'normal'):
                flags.append('opaque')
        elif o == 'rect_flash' and op.get('rect'):
            r_ = op['rect']
            box = [float(r_[0]) * W, float(r_[1]) * H, float(r_[2]) * W, float(r_[3]) * H]
            if a >= 0.9 and op.get('shape') != 'object':
                flags.append('opaque')
        elif o == 'hud_tc':                          # draw_hud_tc geometry (1080 px wide design, scaled)
            k_, cy = W / 1080.0, 0.47 * H
            box = [70.0 * k_, cy - 150.0 * k_, W - 70.0 * k_, cy + 170.0 * k_]
            flags.append('opaque')
        elif o == 'mask_flash' and mask is not None:
            bb = _alpha_bbox(np.asarray(mask, np.float32), 0.35)
            if bb is None:
                return None
            box = [v / self.scale for v in bb]
        else:
            return None
        return dict(id=oid, kind=o, bbox=[round(v, 1) for v in box], flags=flags)

    def _trans_frame(self, f, T, pre):
        """Frame f inside a transition window: both segments (the previous one continued past its f1, this one
        started early), blended by ed_fx.transition or the built-in fallback; p = (j + 0.5) / window length."""
        B = self._state(T['b'])
        kb = f - B.f0
        xb, fxb = self._post_seg(B, kb, pre['b'])
        _, rawb, tb, camb, _ = pre['b']
        if T['a'] is not None:
            A = self._state(T['a'])
            xa, fxa = self._post_seg(A, f - A.f0, pre['a'])
            _, rawa, ta, cama, _ = pre['a']
            a_id = A.seg.get('id', T['a'])
        else:
            xa, rawa, ta, cama, fxa, a_id = np.zeros_like(xb), None, None, [], [], None
        j, F = f - T['w0'], T['F']
        p = (j + 0.5) / F
        seam = j >= T['seam']
        tr = T['tr']
        kind = tr.get('kind', 'dissolve')
        params = {k: v for k, v in tr.items() if k not in ('kind', 'frames', 'align', 'params', 'impl', 'move', 'id')}
        params.update(tr.get('params') or {})
        impl = 'local'
        with self.T('transition'):
            y = None
            if (tr.get('impl') or self.fx_impl) != 'local':
                ctx = self._fx_ctx(B, kb, rawb, tj=j, tn=F, tseam=T['seam'], a_id=a_id, b_id=B.seg.get('id'),
                                   a_raw=rawa, b_raw=rawb, f_abs=f)
                ok, y = EXT.call('ed_fx', 'transition', _pool(
                    ('kind', kind, 'type name'), ('a', xa, 'x0 img_a frame_a A out_img'),
                    ('b', xb, 'x1 img_b frame_b B in_img'), ('p', p, 'progress u'),
                    ('params', params, 'cfg opts options'), ('ctx', ctx, 'context info')),
                    ('kind', 'a', 'b', 'p', 'params', 'ctx'), check=_img_check(xb), key=kind)
                impl = 'ed_fx' if ok else 'local'
                if not ok:
                    y = None
            if y is None:
                if kind not in TRANS_LOCAL:
                    log_once(('trans_none', kind), f'transition {kind!r}: no implementation (ed_fx missing or failed); dissolve')
                y = transition_local(kind, xa, xb, p, params, seam)
        late = seam or T['a'] is None
        info = dict(seg=B.seg.get('id', T['b']), k=kb, t_src=round(tb if late else ta, 4),
                    trans=dict(kind=kind, a=a_id, b=B.seg.get('id', T['b']), p=round(p, 3), impl=impl))
        cam = list(dict.fromkeys(cama + camb))
        fxs = list(dict.fromkeys(fxa + fxb))
        if cam:
            info['cam'] = cam
        if fxs:
            info['fx'] = fxs
        return y, (rawb if late else rawa), (tb if late else ta), info

    def _person_mask(self, key, raw, ext=None):
        """Subject mask of a frame: the external mask when the source has one, else person segmentation of raw."""
        if ext is not None:
            return ext
        m = self._pmask_cache.get(key)
        if m is None and raw is not None:
            with _MASK_LOCK:
                m = np.clip(V.person_mask(raw), 0, 1).astype(np.float32)
            self._pmask_cache[key] = m
            while len(self._pmask_cache) > 8:
                self._pmask_cache.popitem(last=False)
        return m

    def _layers(self, x, f, raw, mask=None):
        """Animated layers on frame f (ed_text.render_layer + composite, or the minimal built-in) -> x, records."""
        recs = []
        ctx = dict(self.text_ctx, f=f, frame=raw,
                   person_mask=lambda ff, _r=raw, _f=f, _m=mask: self._person_mask(_f, _r, _m))
        if mask is not None:
            ctx['mask'] = mask
        for li in self.layers_at(f):
            L = self.layers[li]
            with _TEXT_EXT_LOCK:
                ok, res = EXT.call('ed_text', 'render_layer', _pool(
                    ('layer', L, 'spec item L cfg'), ('f', f, 'frame fi'), ('fps', self.fps, 'rate'),
                    ('ow', self.ow, 'w W width'), ('oh', self.oh, 'h H height'), ('scale', self.scale, 's'),
                    ('ctx', ctx, 'context info')), ('layer', 'f', 'fps', 'ow', 'oh', 'scale'),
                    check=_chk_layer, key=str(L.get('kind')))
            impl = 'ed_text'
            if not ok:
                impl = 'local'
                res = layer_local(L, f, self.fps, self.ow, self.oh, self.scale)
            if res is None:
                continue
            rgba, blend = res
            same = rgba.shape[:2] == x.shape[:2]
            bb = getattr(rgba, 'bbox', None) if same else None
            if bb is None:
                bb = _alpha_bbox(rgba[..., 3] if same else cv2.resize(np.asarray(rgba[..., 3], np.float32), (x.shape[1], x.shape[0])))
            if bb is None:
                continue
            done = False
            if impl == 'ed_text':
                if not (x.flags.writeable and x.dtype == np.float32 and x.flags.c_contiguous):
                    x = np.array(x, np.float32)
                with _TEXT_EXT_LOCK:
                    done, y = EXT.call('ed_text', 'composite', _pool(
                        ('x', x, 'img image base dst bg frame'), ('rgba', rgba, 'layer src over overlay fg premult'),
                        ('blend', blend, 'mode blend_mode')), ('x', 'rgba', 'blend'), check=_img_check(x), key='composite')
                if done:
                    x = y
            if not done:
                x = composite_local(x, rgba, blend)
            x0, y0, x1, y1 = [int(v) for v in bb]
            ah, aw = x.shape[:2]
            flags = []
            if x0 <= 0.02 * aw and y0 <= 0.02 * ah and x1 >= 0.98 * aw and y1 >= 0.98 * ah:
                flags.append('full')
            try:
                al = rgba[..., 3] if same else cv2.resize(np.asarray(rgba[..., 3], np.float32), (aw, ah))
                if x1 > x0 and y1 > y0 and float(np.asarray(al[y0:y1, x0:x1], np.float32).mean()) >= 0.95:
                    flags.append('opaque')                       # a card / band that hides what is under it
            except (TypeError, ValueError, IndexError):
                pass
            rec = dict(i=li, id=str(L.get('id', f'layers[{li}]')), kind=L.get('kind', 'static'), impl=impl,
                       bbox=[round(float(v) / self.scale, 1) for v in bb])
            if flags:
                rec['flags'] = flags
            recs.append(rec)
        return x, recs

    def _label(self, f, sg, t_src, rec):
        """Preview label of frame f -> dict(num '#N' (clip number in output order; '#4>#5' inside a transition),
        tc (output timecode), small (segment id, frame, source time), moves (active move ids))."""
        si = self.seg_of.get(f)
        sid = str(sg.get('id', ''))
        if sg.get('slot') is not None and str(sg['slot']) != sid:
            sid = f"{sid}[{sg['slot']}]"
        tr = rec.get('trans')
        idx = {str(s.get('id', i)): i for i, s in enumerate(self.segs)}
        if tr:
            na = self.clip_no.get(idx.get(str(tr['a']))) if tr['a'] is not None else None
            nb = self.clip_no.get(idx.get(str(tr['b'])))
            num = f"#{na}>#{nb}" if na else f"#{nb}"
            sid = f"{tr['a'] or 'black'}>{tr['b']}"
        else:
            num = f"#{self.clip_no.get(si if si is not None else idx.get(sid), '?')}"
        small = f"{sid} f{f}" + (f" src {tcode(t_src)}" if t_src is not None else '')
        moves = [f"trans.{tr['kind']} {tr['p']:.2f}"] if tr else []
        moves += rec.get('cam', []) + rec.get('fx', []) + rec.get('ops', [])
        line = ' '.join(moves)
        if len(line) > 44:
            line = line[:43] + '~'
        return dict(num=num, tc=tcode(f / float(self.fps)), small=small, moves=line)

    def _finish_frame(self, f, pre):
        """Stage 2 of output frame f -> (uint8 HxWx3, record)."""
        rec = {'f': f}
        T = self.trans_at.get(f)
        si = self.seg_of.get(f)
        sg = self.segs[si] if si is not None else None
        raw_u8, t_src = None, None
        mask = None
        if T is not None:
            x, raw_u8, t_src, info = self._trans_frame(f, T, pre)
            rec.update(info)
            if sg is None:
                sg = self.segs[T['b']]
            late = (f - T['w0']) >= T['seam'] or T['a'] is None
            P = self._state(T['b'] if late else T['a'])
            mask = self.ext_mask(P, f - P.f0)
        elif si is None:
            x = np.zeros((self.oh, self.ow, 3), np.float32)
        else:
            S = self._state(si)
            k = f - S.f0
            x, fx_ids = self._post_seg(S, k, pre['s'])
            _, raw_u8, t_src, cam_ids, _ = pre['s']
            rec.update(seg=sg.get('id', si), k=k, t_src=round(t_src, 4))
            if cam_ids:
                rec['cam'] = cam_ids
            if fx_ids:
                rec['fx'] = fx_ids
            mask = self.ext_mask(S, k)
        ops, op_boxes = [], []
        with self.T('ops'):
            x = self.frame_ops(x, f, raw_u8, sg, 'pre', ops, mask=mask, boxes=op_boxes)
        if f in self.text_at:
            with self.T('text'):
                items = self.text_at[f]
                x = self.text.composite(x, items)
                rec['texts'] = self.text.bboxes(items)
        if self.layer_spans:
            with self.T('layers'):
                x, lrec = self._layers(x, f, raw_u8, mask)
            if lrec:
                rec['layers'] = lrec
        with self.T('ops'):
            x = self.frame_ops(x, f, raw_u8, sg, 'post', ops, mask=mask, boxes=op_boxes)
        if ops:
            rec['ops'] = ops
        if op_boxes:
            rec['op_boxes'] = op_boxes
        post = (sg or {}).get('post_text_fx')
        if post:
            with self.T('fx'):
                S = self._state(si) if si is not None else self._state(T['b'])
                x, pids = self._image_fx(S, x, f - S.f0, fxs=post, raw=raw_u8, rng=np.random.default_rng(f))
            if pids:
                rec['fx'] = rec.get('fx', []) + pids
        if self.labels and sg is not None:
            with self.T('label'):
                box = []
                x = draw_label(x, self._label(f, sg, t_src, rec), self.scale, box)
                if box:
                    b = [int(math.ceil(v / self.scale)) for v in box[0]]
                    lb = self.label_box
                    self.label_box = b if lb is None else [0, 0, max(lb[2], b[2]), max(lb[3], b[3])]
        return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), rec

    def _render_frame(self, f):
        """One output frame, single-threaded -> (uint8 HxWx3, record)."""
        return self._finish_frame(f, self._pre_frame(f))

    def _iter_frames(self, frames):
        """Yield (f, uint8, record) in order: stage 1 in a thread pool (chunks, bounded look-ahead), stage 2 here."""
        if self.workers <= 1:
            for f in frames:
                u8, rec = self._render_frame(f)
                yield f, u8, rec
            return
        chunks = [frames[i:i + self.chunk] for i in range(0, len(frames), self.chunk)]
        ex = ThreadPoolExecutor(self.workers, thread_name_prefix='edl')
        pending = deque()
        it = iter(chunks)

        def pre_chunk(ch):
            return [self._pre_frame(f) for f in ch]

        def submit():
            ch = next(it, None)
            if ch is not None:
                pending.append((ch, ex.submit(pre_chunk, ch)))
            return ch is not None

        try:
            for _ in range(max(2, self.lookahead // self.chunk)):
                if not submit():
                    break
            while pending:
                ch, fut = pending.popleft()
                pres = fut.result()
                submit()
                for f, pre in zip(ch, pres):
                    u8, rec = self._finish_frame(f, pre)
                    yield f, u8, rec
        finally:
            for _, fut in pending:
                fut.cancel()
            ex.shutdown(wait=True, cancel_futures=True)

    def _venc(self):
        """Video encoder settings: final = x264 CRF 17, preset slow; previews = CRF 20, preset veryfast (--fast:
        ultrafast). RGB -> YUV 4:2:0 with the BT.709 matrix, limited range, BT.709 tags (players show the colours
        that were rendered). ED_CRF / ED_X264_PRESET override the final settings."""
        if self.preview:
            preset, crf, flags = ('ultrafast' if self.fast else 'veryfast'), '20', 'bicubic'
        else:
            preset, crf = os.environ.get('ED_X264_PRESET', 'slow'), os.environ.get('ED_CRF', '17')
            flags = 'lanczos+accurate_rnd+full_chroma_int'
        return ['-vf', f'scale=out_color_matrix=bt709:out_range=tv:flags={flags},format=yuv420p',
                '-c:v', 'libx264', '-preset', preset, '-crf', crf, '-pix_fmt', 'yuv420p',
                '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
                '-movflags', '+faststart']

    def render(self, out_path, frame_range=None, stills=None, progress=None):
        """Render frames (all, frame_range (a, b) inclusive, or the still list) to out_path (None: stills only).
        progress: optional callable(done, total) after every frame (progress lines on stderr are printed anyway)."""
        tic = time.perf_counter()
        self._cpu0 = time.process_time()
        fr0, fr1 = frame_range or (0, self.n - 1)
        if stills is None:
            frames = list(range(max(0, fr0), min(self.n - 1, fr1) + 1))
        else:
            frames = sorted({int(f) for f in stills if 0 <= int(f) < self.n})
        au = self.e.get('audio')
        mode = audio_mode(au) if (out_path and frame_range is None and stills is None) else None
        proc, tmp_video, audio_job, audio_info, ref_copy = None, None, None, None, False
        if mode == 'mix':
            fd, tmp_video = tempfile.mkstemp(prefix='.edl_v_', suffix='.mp4', dir=os.path.dirname(os.path.abspath(out_path)))
            os.close(fd)
            audio_job = dict(wav=tmp_video[:-4] + '.wav', enc=tmp_video[:-4] + '.m4a')

            def _mix():
                try:
                    audio_job['info'] = build_audio(au, self.n / self.fps, audio_job['wav'],
                                                    genre=(self.e.get('meta') or {}).get('genre'),
                                                    enc_out=audio_job['enc'])
                except Exception as e:  # keep the video; report the audio failure
                    audio_job['error'] = f'{type(e).__name__}: {e}'
            audio_job['thread'] = threading.Thread(target=_mix, daemon=True)
            audio_job['thread'].start()
        if out_path:
            cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{self.ow}x{self.oh}',
                   '-r', fps_arg(self.fps), '-i', '-']
            if mode == 'ref':
                ref_copy = au.get('copy', True) and audio_codec(au['path']) in MP4_AUDIO   # pcm etc.: re-encode
                cmd += ['-i', au['path'], '-map', '0:v', '-map', '1:a']
                cmd += ['-c:a', 'copy'] if ref_copy else ['-c:a', 'aac', '-b:a', AUDIO_BITRATE]
            cmd += self._venc()
            if mode == 'ref':
                cmd += ['-t', f'{self.n / self.fps:.4f}']
            cmd += [tmp_video or out_path]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        want = set(frames) if stills is not None else None
        out_stills, records = {}, []
        prog = _Progress(len(frames), 'stills' if stills is not None else os.path.basename(out_path or 'render'))
        try:
            for f, u8, rec in self._iter_frames(frames):
                if proc:
                    with self.T('write'):
                        proc.stdin.write(memoryview(u8))
                if want is not None:
                    out_stills[f] = u8
                records.append(rec)
                self._release_before(f + 1)
                prog.tick()
                if progress is not None:
                    try:
                        progress(len(records), len(frames))
                    except Exception as e:  # noqa: BLE001 — a broken callback never stops the render
                        log_once(('progress_cb',), f'progress callback failed ({type(e).__name__}: {e}); ignored')
                        progress = None
        except BaseException:
            if proc:
                proc.kill()
                proc.wait()
            if audio_job:
                audio_job['thread'].join()
            for p in (tmp_video, audio_job and audio_job.get('wav'), audio_job and audio_job.get('enc')):
                if p and os.path.exists(p):
                    os.remove(p)
            raise
        finally:
            with self._states_lock:
                for S in list(self._states.values()) + list(self._ghost_states.values()):
                    S.close()
                self._states.clear()
                self._ghost_states.clear()
        prog.finish()
        if proc:
            proc.stdin.close()
            proc.wait()
            if proc.returncode:
                raise RuntimeError(f'ffmpeg encoder failed ({proc.returncode})')
        if audio_job:
            audio_job['thread'].join()
            audio_info = audio_job.get('info') or dict(method='failed', error=audio_job.get('error'))
            if audio_job.get('info'):
                enc = audio_job['enc'] if (os.path.exists(audio_job['enc']) and
                                           (audio_info.get('encode') or {}).get('method') != 'failed') else None
                # delivery AAC already encoded and checked (encode_mix): stream copy; else encode the WAV here
                acodec = ['-c:a', 'copy'] if enc else ['-c:a', 'aac', '-b:a', AUDIO_BITRATE]
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp_video, '-i', enc or audio_job['wav'],
                                '-map', '0:v', '-map', '1:a', '-c:v', 'copy'] + acodec +
                               ['-t', f'{self.n / self.fps:.4f}', '-movflags', '+faststart', out_path], check=True)
                os.remove(tmp_video)
            else:
                log(f"audio mix failed ({audio_job.get('error')}); video written without audio")
                os.replace(tmp_video, out_path)
            for p in (audio_job['wav'], audio_job['enc']):
                if os.path.exists(p):
                    os.remove(p)
        elif mode == 'ref':
            audio_info = dict(method='copy' if ref_copy else 'ref-aac', path=au['path'])
        wall = time.perf_counter() - tic
        self.report = self._report(out_path, frames, records, audio_info, wall, stills is not None)
        if out_path and self.sidecar:
            self.write_sidecars(out_path)
        return out_stills

    # ---------------------------------------------------------------------------------------------- sidecar
    def _report(self, out_path, frames, records, audio_info, wall, stills):
        segs = []
        for si, sg in enumerate(self.segs):
            n = int(sg['f1']) - int(sg['f0']) + 1
            try:
                ta, tb = seg_time(sg, 0, self.fps), seg_time(sg, n - 1, self.fps)
            except (KeyError, TypeError):
                ta = tb = None
            segs.append(dict(id=sg.get('id', si), f0=sg['f0'], f1=sg['f1'], src=sg.get('src', 'film'),
                             t0=None if ta is None else round(ta, 4), t1=None if tb is None else round(tb, 4),
                             ext=[self.ext_pre[si], self.ext_post[si]], stream=si in self.streamed))
            if si in self.seg_decode:
                segs[-1]['decode'] = self.seg_decode[si]
        dec = {k: s.stats() for k, s in self.sources.items()}
        try:
            edl_md5 = hashlib.md5(json.dumps(self.e, sort_keys=True, default=str).encode()).hexdigest()
        except (TypeError, ValueError):
            edl_md5 = None
        return dict(
            version=2, out=out_path, edl_md5=edl_md5, canvas=dict(self.e['canvas']), scale=self.scale,
            size=[self.ow, self.oh], fps=self.fps, n_frames=self.n, preview=self.preview, labels=bool(self.labels),
            frame_interp=self.frame_interp, fast=self.fast, fx_impl=self.fx_impl,
            decode='legacy' if self.legacy_decode else 'exact',
            bbox_units='canvas_px', label_box=self.label_box if self.labels else None,
            encode=self._venc(),
            rendered=dict(frames=len(frames), first=frames[0] if frames else None, last=frames[-1] if frames else None,
                          stills=stills),
            segments=segs, transitions=self.windows, frames=records, audio=audio_info, modules=EXT.status(),
            timing=dict(wall_s=round(wall, 2), fps=round(len(frames) / max(wall, 1e-9), 2), workers=self.workers,
                        chunk=self.chunk, cpu_s=round(time.process_time() - self._cpu0, 2), peak_rss_mb=_peak_rss_mb(),
                        stages_thread_s=self.T.totals(), decode=dec))

    def write_sidecars(self, out_path):
        """<out>.render.json (full report) and <out without ext>.boxes.json: {"canvas": [W, H], "frames": {"<f>":
        [[x0, y0, x1, y1, id, kind, flags...], ...]}} in canvas px — layer ink boxes (kind = layer kind; flags 'full'
        when it covers the frame, 'opaque' when it hides what is under it) and frame-op boxes (id 'op<i>:<op>',
        flags 'op' (+ 'full', 'opaque'))."""
        rep = self.report
        if rep is None:
            return None
        path = sidecar_path(out_path)
        with open(path + '.tmp', 'w') as fh:
            json.dump(rep, fh, separators=(',', ':'))
        os.replace(path + '.tmp', path)
        if self.layers or any(r.get('op_boxes') for r in rep['frames']):
            boxes = {}                       # [x0, y0, x1, y1, id, kind, flags...] (canvas px; ed_qa format)
            for r in rep['frames']:
                for lr in r.get('layers', []) + r.get('op_boxes', []):
                    boxes.setdefault(str(r['f']), []).append(lr['bbox'] + [lr['id'], lr.get('kind')]
                                                              + list(lr.get('flags', [])))
            bpath = os.path.splitext(out_path)[0] + '.boxes.json'
            with open(bpath + '.tmp', 'w') as fh:
                json.dump(dict(canvas=[self.W, self.H], frames=boxes), fh, separators=(',', ':'))
            os.replace(bpath + '.tmp', bpath)
        return path


def _peak_rss_mb():
    try:
        import resource
        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
    except (ImportError, OSError, ValueError):
        return None


def sidecar_path(out_path):
    return out_path + '.render.json'


# ----------------------------------------------------------------------------- EDL editing helpers
def _shift_f(f, from_f, delta):
    """Output frame f after the edit (None = removed)."""
    f = int(f)
    if f < from_f:
        return f
    if delta >= 0:
        return f + delta
    return None if f < from_f - delta else f + delta


def _shift_range(a, b, from_f, delta):
    """Inclusive output-frame range after the edit -> (a', b') | None (nothing left). A range containing the edit
    point grows (insert) or loses the removed frames."""
    a, b = int(a), int(b)
    if delta >= 0:
        return (a + delta, b + delta) if a >= from_f else (a, b + delta if b >= from_f else b)
    end = from_f - delta
    a2 = a if a < from_f else (from_f if a < end else a + delta)
    b2 = b if b < from_f else (from_f - 1 if b < end else b + delta)
    return (a2, b2) if b2 >= a2 else None


def _shift_t(t, t0, dt):
    """Output time (s) after the edit (None = removed)."""
    t = float(t)
    if t < t0 - 1e-9:
        return t
    if dt >= 0:
        return t + dt
    return None if t < t0 - dt - 1e-9 else t + dt


def _shift_trange(a, b, t0, dt):
    a, b = float(a), float(b)
    if dt >= 0:
        return (a + dt, b + dt) if a >= t0 - 1e-9 else (a, b + dt if b >= t0 - 1e-9 else b)
    end = t0 - dt
    a2 = a if a < t0 - 1e-9 else (t0 if a < end - 1e-9 else a + dt)
    b2 = b if b < t0 - 1e-9 else (t0 if b < end - 1e-9 else b + dt)
    return (a2, b2) if b2 > a2 - 1e-9 else None


def _shift_fspec(spec, from_f, delta):
    """Frame spec (int | 'a:b' | list of those) after the edit; None when every frame was removed."""
    if spec is None:
        return None
    if isinstance(spec, (int, float, np.integer)) and not isinstance(spec, bool):
        return _shift_f(spec, from_f, delta)
    if isinstance(spec, str):
        if ':' in spec:
            a, b = spec.split(':')[:2]
            r = _shift_range(int(a), int(b), from_f, delta)
            return None if r is None else f'{r[0]}:{r[1]}'
        return _shift_f(int(spec), from_f, delta)
    out = [v for v in (_shift_fspec(x, from_f, delta) for x in spec) if v is not None]
    return out or None


def _cut_kspec(spec, h, n):
    """Segment-relative frame spec (k | 'a:b' | list of those) of a segment that keeps its old frames h .. h + n - 1
    -> the same frames rebased by -h, frames outside 0 .. n - 1 dropped (None = nothing left)."""
    if spec is None or isinstance(spec, bool):
        return spec
    if isinstance(spec, (int, float, np.integer)):
        k = int(round(float(spec))) - h
        return k if 0 <= k <= n - 1 else None
    if isinstance(spec, str):
        if ':' in spec:
            a, b = (int(x) - h for x in spec.split(':')[:2])
            a, b = max(a, 0), min(b, n - 1)
            return f'{a}:{b}' if b >= a else None
        return _cut_kspec(int(spec), h, n)
    if isinstance(spec, (list, tuple)):
        out = [v for v in (_cut_kspec(x, h, n) for x in spec) if v is not None]
        return out or None
    return spec


def _cut_keys(keys, h, n):
    """Keyframes [[k, value, ...], ...] (segment-relative k, linear between keys, held outside) of a segment that
    keeps its old frames h .. h + n - 1 -> rebased by -h; keys outside 0 .. n - 1 give way to end keys at 0 / n - 1
    interpolated from the old curve (the kept frames are unchanged)."""
    pts = sorted((list(p) for p in keys), key=lambda p: float(p[0]))
    width = min(len(p) for p in pts)
    ks = [float(p[0]) for p in pts]
    lo, hi = float(h), float(h + n - 1)

    def at(k):
        return [round(float(np.interp(k, ks, [float(p[j]) for p in pts])), 6) for j in range(1, width)]
    inside = [[p[0] - h] + list(p[1:width]) for p in pts if lo - 1e-9 <= float(p[0]) <= hi + 1e-9]
    out = []
    if ks[0] < lo - 1e-9 and not (inside and abs(float(inside[0][0])) < 1e-9):
        out.append([0] + at(lo))
    out += inside
    if ks[-1] > hi + 1e-9 and not (inside and abs(float(inside[-1][0]) - (n - 1)) < 1e-9):
        out.append([n - 1] + at(hi))
    return out


def _cut_segment(s, old, h, n, fps):
    """shift(): segment s (a copy of `old`) keeps old frames h .. h + n - 1 — a delete cut its head (h > 0: the in
    point moves on) and / or its end. Segment-relative values follow so every kept frame shows what it showed:
    t / times / speed_curve, crop.path keys (rebased, cut to 0 .. n - 1, end keys interpolated), crop 'to' (starts /
    ends at the kept frames' states), grades k0 / k1, fx frames / k / hits / beats (an fx left without frames goes)."""
    n_old = int(old['f1']) - int(old['f0']) + 1
    if h > 0 and s.get('t') is not None:
        s['t'] = round(seg_time(old, h, fps), 6)
    if old.get('times'):
        ts = [float(v) for v in old['times']]
        s['times'] = ts[h:h + n] + [seg_time(old, k, fps) for k in range(max(h, len(ts)), h + n)]
    if old.get('speed_curve'):
        s['speed_curve'] = _cut_keys(old['speed_curve'], h, n)
    cr = s.get('crop')
    if isinstance(cr, dict):
        if cr.get('path'):
            cr['path'] = _cut_keys(cr['path'], h, n)
        elif isinstance(cr.get('to'), dict) and n_old > 1:
            if h > 0:
                st = crop_state(old, h, n_old)
                cr.update({x: round(st[x], 6) for x in cr['to'] if x in st})
            if h + n < n_old:
                en = crop_state(old, h + n - 1, n_old)
                cr['to'] = {x: (round(en[x], 6) if x in en else v) for x, v in cr['to'].items()}
    if isinstance(s.get('grades'), list):
        gl = []
        for gr in s['grades']:
            try:
                a, b = int(gr['k0']) - h, int(gr['k1']) - h
            except (KeyError, TypeError, ValueError):
                gl.append(gr)
                continue
            if b >= 0 and a <= n - 1:
                gl.append(dict(gr, k0=max(0, a), k1=min(n - 1, b)))
        s['grades'] = gl
    for key in ('fx', 'post_text_fx'):
        if not isinstance(s.get(key), list):
            continue
        kept = []
        for fx in s[key]:
            gone = False
            for wk in ('frames', 'hits', 'beats'):
                if fx.get(wk) is not None:
                    fx[wk] = _cut_kspec(fx[wk], h, n)
                    gone = gone or fx[wk] is None
            kr = fx.get('k')
            if isinstance(kr, (list, tuple)) and len(kr) == 2:
                a, b = int(kr[0]) - h, int(kr[1]) - h
                gone = gone or b < 0 or a > n - 1
                fx['k'] = [max(0, a), min(n - 1, b)]
            if not gone:
                kept.append(fx)
        s[key] = kept


def _shift_words(ws, t0, dt):
    out = []
    for w in ws or []:
        a = _shift_t(w.get('t0', 0.0), t0, dt)
        if a is None:
            continue
        w = dict(w, t0=round(a, 4))
        if w.get('t1') is not None:
            b = _shift_t(w['t1'], t0, dt)
            w['t1'] = round(a if b is None else max(a, b), 4)
        out.append(w)
    return out


def shift(edl, from_f, delta):
    """Ripple edit: insert `delta` frames before output frame from_f (delta > 0) or remove the frames from_f ..
    from_f - delta - 1 (delta < 0), moving everything addressed in output frames or output seconds after the edit
    point -> a new EDL (the input is not modified).
    Moved: segments (a segment containing from_f grows at its end on insert, 'times' lists extended; a segment inside
    a removed range is dropped; a delete that cuts into a segment shortens it: a cut starting inside it keeps its in
    point and drops its end, a cut over its head moves its in point on by the removed frames — 'times', speed_curve
    and crop.path keys, crop 'to', grades and fx frames / k / hits / beats follow (rebased, cut to the new length,
    end keys interpolated), so every kept frame shows what it showed and the result validates), segment fx with
    absolute 'f' / 't' / 'times', ghosts[].frames, ops[].f, texts f0/f1, layers f0/f1 / t0/t1 / words / chunks,
    audio.voice[].at, audio.sfx[].at, audio.music_fx[].t, qa planned_black / planned_white / planned_freeze / words,
    top-level and meta words, meta.parts f0/f1; n_frames += delta. Not moved: the music and its beat grid (the
    picture follows the track), segment-relative values of segments that keep all their frames, transition_in.
    Items whose point in time is removed are dropped. Fill inserted frames with a new segment afterwards (or split
    a segment first, like edit.py delete_range, to cut out its middle as a jump cut)."""
    import copy
    e = copy.deepcopy(edl)
    from_f, delta = int(from_f), int(delta)
    if delta == 0:
        return e
    fps = float(e['canvas']['fps'])
    t0, dt = from_f / fps, delta / fps
    segs = []
    for s in e.get('segments') or []:
        r = _shift_range(s['f0'], s['f1'], from_f, delta)
        if r is None:
            continue
        old = copy.deepcopy(s)
        n_old = int(s['f1']) - int(s['f0']) + 1
        s['f0'], s['f1'] = r
        n_new = r[1] - r[0] + 1
        h = from_f - delta - int(old['f0']) if delta < 0 and from_f <= int(old['f0']) < from_f - delta else 0
        if h > 0 or n_new < n_old:                       # a delete cut into it: its head and / or its end
            _cut_segment(s, old, h, n_new, fps)
        elif s.get('times') and n_new > len(s['times']):
            ts = [float(v) for v in s['times']]
            s['times'] = ts + [seg_time(old, k, fps) for k in range(len(ts), n_new)]
        if isinstance(s.get('ghosts'), list):            # ghost frames are output frames
            ghs = []
            for gh in s['ghosts']:
                if isinstance(gh, dict) and gh.get('frames') is not None:
                    fr = _shift_fspec(gh['frames'], from_f, delta)
                    if fr is None:
                        continue
                    gh['frames'] = fr
                ghs.append(gh)
            s['ghosts'] = ghs
        for key in ('fx', 'post_text_fx'):
            if not isinstance(s.get(key), list):
                continue
            kept = []
            for fx in s[key]:
                if fx.get('f') is not None:
                    fx['f'] = _shift_fspec(fx['f'], from_f, delta)
                    if fx['f'] is None:
                        continue                         # all its frames were removed
                if isinstance(fx.get('t'), (list, tuple)) and len(fx['t']) == 2:
                    tr = _shift_trange(fx['t'][0], fx['t'][1], t0, dt)
                    if tr is None:
                        continue
                    fx['t'] = [round(tr[0], 4), round(tr[1], 4)]
                if isinstance(fx.get('times'), list):
                    fx['times'] = [round(v, 4) for v in (_shift_t(x, t0, dt) for x in fx['times']) if v is not None]
                kept.append(fx)
            s[key] = kept
        segs.append(s)
    e['segments'] = segs
    e['n_frames'] = max(0, int(e.get('n_frames', 0)) + delta)
    ops = []
    for op in e.get('ops') or []:
        f = _shift_fspec(op.get('f'), from_f, delta)
        if f is not None:
            op['f'] = f
            ops.append(op)
    if 'ops' in e:
        e['ops'] = ops
    texts = []
    for tb in e.get('texts') or []:
        r = _shift_range(tb['f0'], tb['f1'], from_f, delta)
        if r is not None:
            tb['f0'], tb['f1'] = r
            texts.append(tb)
    if 'texts' in e:
        e['texts'] = texts
    layers = []
    for L in e.get('layers') or []:
        if L.get('f0') is not None or L.get('f1') is not None:
            r = _shift_range(L.get('f0', 0), L.get('f1', e['n_frames'] - delta - 1), from_f, delta)
            if r is None:
                continue
            if L.get('f0') is not None:
                L['f0'] = r[0]
            if L.get('f1') is not None:
                L['f1'] = r[1]
        if L.get('t0') is not None and L.get('t1') is not None:
            tr = _shift_trange(L['t0'], L['t1'], t0, dt)
            if tr is None:
                continue
            L['t0'], L['t1'] = round(tr[0], 4), round(tr[1], 4)
        for key in ('words', 'chunks'):
            if isinstance(L.get(key), list):
                L[key] = _shift_words(L[key], t0, dt)
        layers.append(L)
    if 'layers' in e:
        e['layers'] = layers
    au = e.get('audio')
    if isinstance(au, dict):
        for key in ('voice', 'sfx'):
            if isinstance(au.get(key), list):
                kept = []
                for it in au[key]:
                    a = _shift_t(it.get('at', 0.0), t0, dt)
                    if a is not None:
                        kept.append(dict(it, at=round(a, 4)))
                au[key] = kept
        if isinstance(au.get('music_fx'), list):
            kept = []
            for it in au['music_fx']:
                t = it.get('t')
                if isinstance(t, (list, tuple)) and len(t) == 2:
                    tr = _shift_trange(t[0], t[1], t0, dt)
                    if tr is None:
                        continue
                    it = dict(it, t=[round(tr[0], 4), round(tr[1], 4)])
                kept.append(it)
            au['music_fx'] = kept
    q = e.get('qa')
    if isinstance(q, dict):
        for key in ('planned_black', 'planned_white'):
            if q.get(key) is not None:
                q[key] = _shift_fspec(q[key], from_f, delta) or []
        if isinstance(q.get('planned_freeze'), list):
            q['planned_freeze'] = [list(r) for r in (_shift_range(a, b, from_f, delta) for a, b in q['planned_freeze'])
                                   if r is not None]
        if isinstance(q.get('words'), list):
            q['words'] = _shift_words(q['words'], t0, dt)
    if isinstance(e.get('words'), list):
        e['words'] = _shift_words(e['words'], t0, dt)
    meta = e.get('meta')
    if isinstance(meta, dict):
        if isinstance(meta.get('words'), list):
            meta['words'] = _shift_words(meta['words'], t0, dt)
        if isinstance(meta.get('parts'), list):
            parts = []
            for p in meta['parts']:
                if p.get('f0') is not None and p.get('f1') is not None:
                    r = _shift_range(p['f0'], p['f1'], from_f, delta)
                    if r is None:
                        continue
                    p = dict(p, f0=r[0], f1=r[1])
                parts.append(p)
            meta['parts'] = parts
    return e


_KNOWN_OPS = {'invert', 'white', 'black', 'mask_flash', 'rect_flash', 'hud_tc', 'flash'}


def validate(edl):
    """Renderer-side check of an EDL -> [dict(level 'error' | 'warning', where, msg)] (empty = fine).
    error: the render fails or is wrong — missing / unreadable source, box outside the picture, bad canvas or frame
    ranges, overlapping segments, unknown source name, wrong 'times' length, unsorted speed_curve, z <= 0, malformed
    or unsorted crop.path, missing audio or mask file. warning: rendered with a fallback — unknown fx type (skipped),
    transition kind (dissolve), layer kind, op (skipped) — checked against the registries of ed_fx (FX_TYPES,
    CAMERA_TYPES, TRANSITIONS) and ed_text (LAYER_KINDS) when they import, else against the built-in sets; gaps
    (black frames), source time past the end of the file (last frame held), items outside 0 .. n_frames - 1,
    speed_curve / crop.path keys or fx frames outside their segment."""
    P = []

    def add(level, where, msg):
        P.append(dict(level=level, where=where, msg=msg))

    cv = edl.get('canvas') or {}
    if not all(isinstance(cv.get(k), (int, float)) and not isinstance(cv.get(k), bool) and cv.get(k) > 0
               for k in ('w', 'h', 'fps')):
        add('error', 'canvas', 'canvas needs positive w, h, fps')
    n = edl.get('n_frames')
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        add('error', 'n_frames', f'n_frames must be a positive int (got {n!r})')
        n = None
    if edl.get('frame_interp', 'flow') not in ('nearest', 'blend', 'flow'):
        add('error', 'frame_interp', 'frame_interp must be nearest | blend | flow')
    fps = float(cv.get('fps') or 30)
    infos = {}
    for name, sc in (edl.get('sources') or {}).items():
        where = f'sources.{name}'
        p = (sc or {}).get('path')
        if not p or not os.path.exists(p):
            add('error', where, f'file not found: {p}')
            continue
        try:
            info = infos[name] = probe_source(p)
        except Exception as ex:  # noqa: BLE001
            add('error', where, f'cannot read: {ex}')
            continue
        box = sc.get('box')
        if box is not None:
            ok = isinstance(box, (list, tuple)) and len(box) == 4
            if ok:
                x0, y0, x1, y1 = [float(v) for v in box]
                ok = 0 <= x0 < x1 <= info['w'] and 0 <= y0 < y1 <= info['h']
            if not ok:
                add('error', where, f"box {box} is not inside the {info['w']}x{info['h']} picture")
        lg = sc.get('logo')
        if lg is not None and box is not None and len(lg) == 4 and len(box) == 4:
            if lg[2] <= box[0] or lg[0] >= box[2] or lg[3] <= box[1] or lg[1] >= box[3]:
                add('warning', where, f'logo {lg} is outside the box {box}: not cleaned')
        mk = sc.get('mask')
        mp = mk if isinstance(mk, str) else (mk or {}).get('path') if isinstance(mk, dict) else None
        if mk is not None and (not mp or not os.path.exists(mp)):
            add('error', where, f'mask file not found: {mp}')
    fx_known = set(LOCAL_FX) | set(CAMERA_FX) | set(TIME_BLUR_FX)
    reg = EXT.attr('ed_fx', 'FX_TYPES')
    fx_known |= set(reg) if isinstance(reg, dict) else set()
    cam = EXT.attr('ed_fx', 'CAMERA_TYPES')
    fx_known |= set(cam) if isinstance(cam, (set, frozenset, list, tuple, dict)) else set()
    tr_known = set(TRANS_LOCAL)
    for attr in ('TRANSITIONS', '_TR_ALIAS'):
        v = EXT.attr('ed_fx', attr)
        tr_known |= set(v) if isinstance(v, dict) else set()
    kinds = EXT.attr('ed_text', 'LAYER_KINDS')
    kind_of = EXT.attr('ed_text', 'kind_of')
    segs = edl.get('segments') or []
    if not segs:
        add('error', 'segments', 'no segments')
    ids, spans = {}, []
    for i, s in enumerate(segs):
        sid = s.get('id', i)
        where = f'segments[{i}] ({sid})'
        if sid in ids:
            add('warning', where, f'segment id {sid!r} also used by segments[{ids[sid]}]')
        ids.setdefault(sid, i)
        f0, f1 = s.get('f0'), s.get('f1')
        if not all(isinstance(v, int) and not isinstance(v, bool) for v in (f0, f1)) or f1 < f0:
            add('error', where, f'f0 / f1 must be ints with f0 <= f1 (got {f0!r}, {f1!r})')
            continue
        if f0 < 0 or (n is not None and f1 > n - 1):
            add('error', where, f'frames {f0}..{f1} outside 0..{(n or 1) - 1}')
        spans.append((f0, f1, where))
        src = s.get('src', 'film')
        if src not in (edl.get('sources') or {}):
            add('error', where, f'unknown source {src!r}')
        m = f1 - f0 + 1
        if s.get('times') is not None and len(s['times']) != m:
            add('error', where, f"times has {len(s['times'])} values for {m} frames")
        sc_ = s.get('speed_curve')
        if sc_ is not None:
            try:
                ks = [float(p[0]) for p in sc_]
                rates = [float(p[1]) for p in sc_]
                if ks != sorted(ks) or not rates:
                    add('error', where, 'speed_curve keys must be sorted (and not empty)')
                elif ks[0] != 0 or ks[-1] > m - 1:
                    add('warning', where, f'speed_curve keys {ks[0]:g}..{ks[-1]:g} should run 0..{m - 1} '
                                          '(the rate is held flat outside its keys)')
            except (TypeError, ValueError, IndexError):
                add('error', where, 'speed_curve must be [[k, rate], ...]')
        cr = s.get('crop') or {}
        if cr.get('z') is not None and float(cr['z']) <= 0:
            add('error', where, 'crop.z must be > 0')
        for key in ('cx', 'cy'):
            if cr.get(key) is not None and not 0.0 <= float(cr[key]) <= 1.0:
                add('warning', where, f'crop.{key} {cr[key]} outside 0..1 (clamped to the picture)')
        if cr.get('path'):
            try:
                pk = [[float(v) for v in p] for p in cr['path']]
                if any(len(p) != 4 or p[3] <= 0 for p in pk) or [p[0] for p in pk] != sorted(p[0] for p in pk):
                    add('error', where, 'crop.path must be sorted [[k, cx, cy, z > 0], ...]')
                elif pk[0][0] < 0 or pk[-1][0] > m - 1:
                    add('warning', where, f'crop.path keys {pk[0][0]:g}..{pk[-1][0]:g} outside the segment 0..{m - 1}')
            except (TypeError, ValueError):
                add('error', where, 'crop.path must be [[k, cx, cy, z], ...]')
        for j, fx in enumerate(s.get('fx') or []):
            try:
                fr = frange(fx.get('frames'))
            except (TypeError, ValueError):
                add('error', f'{where}.fx[{j}]', f"bad frames {fx.get('frames')!r}")
                continue
            if fr and (min(fr) < 0 or max(fr) > m - 1):
                add('warning', f'{where}.fx[{j}]', f'frames outside the segment 0..{m - 1}')
        if src in infos and not infos[src].get('image') and (s.get('t') is not None or s.get('times')):
            try:
                ts = [seg_time(s, k, fps) for k in range(0, m, max(1, m // 16))] + [seg_time(s, m - 1, fps)]
                dur = infos[src]['duration']
                if min(ts) < -1e-6:
                    add('warning', where, f'source time {min(ts):.3f} s < 0 (first frame shown)')
                if dur and max(ts) > dur + 0.05:
                    add('warning', where, f'source time {max(ts):.2f} s past the end of {src} ({dur:.2f} s): '
                                          'last frame held')
            except (KeyError, TypeError, ValueError):
                add('error', where, 'source time not computable (t / speed / speed_curve / times)')
        for j, fx in enumerate(s.get('fx') or []):
            t = fx.get('type')
            if t not in fx_known:
                add('warning', f'{where}.fx[{j}]', f'unknown fx type {t!r}: skipped')
        tr = s.get('transition_in')
        if tr:
            kind = str(tr.get('kind', 'dissolve')).split('(')[0].strip()
            if kind not in tr_known:
                add('warning', f'{where}.transition_in', f'unknown transition kind {kind!r}: dissolve')
    spans.sort()
    for (a0, a1, wa), (b0, b1, wb) in zip(spans, spans[1:]):
        if b0 <= a1:
            add('error', wb, f'overlaps {wa} (frames {b0}..{min(a1, b1)})')
        elif b0 > a1 + 1:
            add('warning', wb, f'gap of {b0 - a1 - 1} frames before it (black)')
    if spans and spans[0][0] > 0:
        add('warning', spans[0][2], f'frames 0..{spans[0][0] - 1} have no segment (black)')
    if spans and n is not None and max(b for _, b, _ in spans) < n - 1:
        add('warning', 'segments', f'frames after {max(b for _, b, _ in spans)} have no segment (black)')
    for i, op in enumerate(edl.get('ops') or []):
        if op.get('op') not in _KNOWN_OPS:
            add('warning', f'ops[{i}]', f"unknown op {op.get('op')!r}: skipped")
        try:
            fr = frange(op.get('f'))
        except (TypeError, ValueError):
            add('error', f'ops[{i}]', f"bad frame spec {op.get('f')!r}")
            continue
        if n is not None and fr and (min(fr) < 0 or max(fr) > n - 1):
            add('warning', f'ops[{i}]', f'frames outside 0..{n - 1}')
    for i, tb in enumerate(edl.get('texts') or []):
        if n is not None and (tb.get('f0', 0) < 0 or tb.get('f1', 0) > n - 1):
            add('warning', f'texts[{i}]', f'frames outside 0..{n - 1}')
    for i, L in enumerate(edl.get('layers') or []):
        if isinstance(kinds, dict) and callable(kind_of):
            try:
                k = kind_of(L)
            except Exception:  # noqa: BLE001
                k = L.get('kind')
            if k not in kinds:
                add('warning', f'layers[{i}]', f"unknown layer kind {L.get('kind')!r}")
    au = edl.get('audio') or {}
    if isinstance(au, dict):
        paths = [('audio.path', au.get('path'))] if au.get('path') else []
        if isinstance(au.get('music'), dict) and au['music'].get('path'):
            paths.append(('audio.music', au['music']['path']))
        paths += [(f'audio.voice[{i}]', v.get('path')) for i, v in enumerate(au.get('voice') or []) if v.get('path')]
        paths += [(f'audio.sfx[{i}]', v.get('file')) for i, v in enumerate(au.get('sfx') or []) if v.get('file')]
        for where, p in paths:
            if not os.path.exists(p):
                add('error', where, f'file not found: {p}')
    return P


def render_edl(edl, out_path, preview=False, labels=False, frame_range=None, **kw):
    """Convenience: EDL dict or path -> rendered file; returns the render report (also in <out>.render.json)."""
    if isinstance(edl, str):
        with open(edl) as fh:
            edl = json.load(fh)
    r = Renderer(edl, preview=preview, labels=labels, **kw)
    r.render(out_path, frame_range=frame_range)
    return r.report


def contact(stills, out, cols=8, width=270, edl=None):
    keys = sorted(stills)
    ims = []
    for f in keys:
        im = stills[f]
        h = int(im.shape[0] * width / im.shape[1])
        t = cv2.resize(im, (width, h), interpolation=cv2.INTER_AREA)
        t = np.vstack([np.zeros((18, width, 3), np.uint8), t])
        lab = str(f)
        if edl:
            for sg in edl['segments']:
                if sg['f0'] <= f <= sg['f1']:
                    lab = f"{f} {sg.get('id', '')}"
        cv2.putText(t, lab, (3, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 0), 1, cv2.LINE_AA)
        ims.append(t)
    rows = []
    for i in range(0, len(ims), cols):
        r = ims[i:i + cols]
        r += [np.zeros_like(ims[0])] * (cols - len(r))
        rows.append(np.hstack([np.pad(a, ((0, 0), (0, 3), (0, 0))) for a in r]))
    cv2.imwrite(out, cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])


def parse_at(spec, edl):
    if spec == 'first':
        return [sg['f0'] + min(2, sg['f1'] - sg['f0']) for sg in edl['segments']]
    if spec:
        at = []
        for part in spec.split(','):
            if ':' in part:
                x0, x1, *st = part.split(':')
                at += list(range(int(x0), int(x1) + 1, int(st[0]) if st else 1))
            else:
                at.append(int(part))
        return at
    return list(range(0, edl['n_frames'], 6))


def main(argv=None):
    ap = argparse.ArgumentParser(description='Render an EDL (engine/TIMELINE.md).')
    ap.add_argument('edl')
    ap.add_argument('out', nargs='?')
    ap.add_argument('--preview', action='store_true')
    ap.add_argument('--labels', action='store_true')
    ap.add_argument('--frames')
    ap.add_argument('--stills')
    ap.add_argument('--at')
    ap.add_argument('--cols', type=int, default=8)
    ap.add_argument('--width', type=int, default=270)
    ap.add_argument('--interp', choices=['nearest', 'blend', 'flow'])
    ap.add_argument('--workers', type=int)
    ap.add_argument('--chunk', type=int)
    ap.add_argument('--no-sidecar', action='store_true')
    ap.add_argument('--fast', action='store_true', help='previews: cheaper optical flow, warp and motion blur')
    ap.add_argument('--validate', action='store_true', help='only check the EDL (exit 1 on errors)')
    a = ap.parse_args(argv)
    with open(a.edl) as fh:
        edl = json.load(fh)
    if a.validate:
        probs = validate(edl)
        for p in probs:
            print(f"{p['level']:7s} {p['where']}: {p['msg']}")
        n_err = sum(p['level'] == 'error' for p in probs)
        print('validate:', 'OK' if not probs else f'{n_err} errors, {len(probs) - n_err} warnings')
        return 1 if n_err else 0
    r = Renderer(edl, preview=a.preview, labels=a.labels, frame_interp=a.interp, workers=a.workers, chunk=a.chunk,
                 sidecar=not a.no_sidecar, fast=a.fast)
    if a.stills:
        st = r.render(None, stills=parse_at(a.at, edl))
        contact(st, a.stills, cols=a.cols, width=a.width, edl=edl)
        print('stills', len(st), '->', a.stills)
    else:
        if not a.out:
            ap.error('OUT.mp4 (or --stills SHEET.jpg) is required')
        rng = tuple(map(int, a.frames.split(':'))) if a.frames else None
        r.render(a.out, frame_range=rng)
        t = r.report['timing']
        print('->', a.out, f"{r.report['rendered']['frames']} frames in {t['wall_s']} s ({t['fps']} fps, "
                           f"{t['workers']} workers)")


if __name__ == '__main__':
    sys.exit(main())
