#!/usr/bin/env python3
"""ed_fx - camera fx, image fx, transitions and flash frame-ops for the Edit Studio renderer (ed_edl.py).

Contract (ed_edl.py calls exactly this - keep stable):

  camera(fx_list, k, n, ctx)             -> dict(zoom=1.0, dx=0.0, dy=0.0, rot=0.0, blur=None)
  apply(x, fx_list, k, n, ctx)           -> x       float32 HxWx3 0..1; image fx only (camera types are ignored)
  transition(kind, a, b, p, params, ctx) -> frame   float32 HxWx3 0..1
  flash_op(x, op, j, ctx)                -> x       TIMELINE.md section 3 op 'flash'; j = index of this frame in op['f']
  FX_TYPES      {name: callable}; callable.kind is 'camera' (fn(fx, k, n, ctx) -> (lnz, rot, dx, dy))
                or 'image' (fn(x, fx, k, n, ctx) -> x); every callable has a docstring with its params
  TRANSITIONS   {kind: callable(a, b, p, params, ctx)}
  Both are machine-readable Registry dicts (still {name: callable}, aliases included): .spec(name) -> {name, kind,
  desc (one line), params {name: default the code uses; None = unset / derived}, choices, aliases, doc};
  .describe(kind=None) -> JSON-ready {name: spec} of canonical entries; .names(kind); .canonical(alias);
  .common (params every entry accepts: gates frames / f / k / t, amt, amt_to, amt_keys, ease, and for image fx
  region / behind / feather / expand / auto_mask). describe(what='all') -> {'fx', 'transitions', 'looks', 'common'};
  CLI: python3 -I ed_fx.py registry [fx|transitions|looks|all] [--md].

Looks (LOOK_PRESETS, our own names): finished picture treatments = a segment grade (ed_edl grade params) + image fx
appended to the segment's fx: film_print, home_tape, clean_luxe, dreamy_bloom, gritty_contrast, mono_noir,
neon_night, golden_hour, silver_bleach, teal_orange, vivid_pop, pastel_fade, cold_concrete (aliases in LOOK_ALIASES:
film, vhs, luxury, dreamy, gritty, noir, bw, neon, golden, bleach, blockbuster, pop, pastel, cold, ...). Each entry:
{label, desc, tags, suits (genres), grade, fx}. look(name, intensity=1.0) -> {'name', 'grade', 'fx'} (deep copies;
intensity scales grade numbers toward neutral, split / duo amounts, mult and every fx's amt; auto exposure and mono
stay; each fx carries 'look': name); look_for(words, genre=None) -> {'name', 'score', 'why'} picks one from plain
words. Planner use: seg['grade'] = {**look['grade'], **own overrides}; seg['fx'] += look['fx'].

Subject regions: any image fx takes region='background' | 'subject' | 'all' (or behind=True = background): it only
changes that part of the picture, weighted by subject_matte(x, ctx, fx) - ctx['mask'] (the external matte of
sources.<name>.mask, warped like the picture, output size; ed_edl passes it), else ctx['person_mask'] (array or
callable f_abs -> array), else (auto_mask=True) ed_video.person_mask on the frame; feather (default 0.004 of the short
side) softens and expand (+ grows the subject) moves the edge; no matte -> the whole frame. region_weight(x, fx, ctx)
returns the weight map. Subject-aware fx: contour_glow (rim glow round the matte), defocus (lens blur, usually
region='background'), saturation (sat 0 = black and white; region='background' = colour pop); finishing fx: clarity
(local contrast), tape (home-videotape texture).

Colours: every colour param (flash / op color, tint, palette, shadows / highlights, letterbox color, rim_color,
divider) goes through color(): '#rgb' / '#rrggbb' / '#rrggbbaa' (with or without '#', '0x...'), 'rgb(r, g, b)',
a name (white black warm red cyan magenta acid amber navy grey yellow green blue gold orange purple pink cream teal),
[r, g, b(, a)] list / tuple / ndarray (0..1, or 0..255 when any channel > 1), int 0xRRGGBB, {'r', 'g', 'b'}; an
unreadable spec falls back to the default with a one-time warning (never fails the frame). palette(spec, named)
takes a palette name, one colour or a list of colours.

Speed ramps (time.speed_ramp): speed_ramp(n, fps, fast, slow, brake_at, exit_at, ...) -> {speed_curve (dense,
eased in log rate: inOutCubic brake, inCubic exit), fx [time.motion_blur (shutter 0.75: source-time blur on frames
with rate >= 1.3)], interp 'flow', src_span, notes}; ramp_curve(keys, n) and source_span(curve, n, fps) are the
building blocks. The renderer blurs source time on fast frames by itself (segment 'shutter', or automatically on
speed changes; 'time_blur': false turns it off); an explicit time.motion_blur fx replaces that blur (never both),
and the segment shutter still blurs crop / camera motion.

ctx: ow, oh (output px; preview already scaled), fps, f_abs (absolute output frame), seg_f0, rng, beats, downbeats
(absolute seconds), scale. Optional: beat_strength (per beat 0..1), bass_env {'t': [...], 'v': [...]} (30-150 Hz
envelope), face [x, y] (fractions, zoom/rotation centre for center='face'), cam_vel (dx, dy px/frame, for
rgb_split mode='motion'), mask (subject matte HxW 0..1 or 0..255, any size - region fx, contour_glow),
person_mask (array or callable f_abs -> array). Transitions also read tj (frame index inside the window), tn (window length) and tseam
(window index of the first frame of the incoming segment = the cut); p = (tj + 0.5) / tn.

Determinism: ctx['rng'] is accepted but never consumed - all randomness is hashed from (fx seed, absolute frame),
so a partial render (stills, --frames) equals the full render. Fx with memory (rgb_split temporal, datamosh,
pixel_sort update='hold2'/'freeze', pixel_art hold) need sequential frames; out of order they fall back to the
stateless result.

camera(): zoom multiplies the crop zoom (the window shrinks); rot is in degrees with the OpenCV sign (+ = counter-
clockwise on screen) about the output centre; dx/dy are OUTPUT pixels added after the warp, exactly like
ed_edl.warp's dx/dy (already scaled - do not multiply by ctx['scale']). cam_matrix(cam, ow, oh) gives the
equivalent 2x3 output-space affine. blur is None or {'kind': 'camera', 'shutter', 'n', 'trail_px', 'from': state,
'samples': [state, ...]} (state = dict(zoom, dx, dy, rot)): the exact render is the mean of n warps of the source
at the sample states; camera_blur(x, cam, ctx) approximates it on the rendered frame (3-4 warps).

Units: sizes "@1080" in the move cards scale with the short side of the output (min(ow, oh) / 1080); event times
are absolute output seconds; an event's peak frame is floor(t * fps + 0.4) (move cards: zoom.punch peak_frame).
Fx parameters follow the move cards' params/engine fields (moves/<id>.yaml).

Renderer integration sketch (ed_edl.Renderer.seg_frames):
    ctx = dict(ow=self.ow, oh=self.oh, fps=self.fps, seg_f0=sg['f0'], f_abs=sg['f0'] + k, rng=rng,
               beats=beats, downbeats=downbeats, scale=self.scale)
    cam = ed_fx.camera(sg.get('fx'), k, n, ctx)
    crop z *= cam['zoom']; rot += cam['rot']; warp dx/dy += cam['dx'], cam['dy']    (exact while the crop itself
        has no dx/dy offset; otherwise compose ed_fx.cam_matrix(cam, ow, oh) after the crop affine)
    if cam['blur']: frame = mean of the warps at cam['blur']['samples'] (same composition per sample)
                    or ed_fx.camera_blur(frame, cam, ctx)
    x = ed_fx.apply(graded_x, sg.get('fx'), k, n, ctx)          (handles the legacy apply_fx types too)
  transition_in window of N frames, tseam = window index of the cut (center: N // 2, end: 0):
    x = ed_fx.transition(kind, a, b, (j + .5) / N, params, dict(ctx, f_abs=f, tj=j, tn=N, tseam=tseam))
  ops: {'op': 'flash'} -> ed_fx.flash_op(x, op, op_frames.index(f), ctx); ed_fx.flash_ops(f_cut, fps, ...) builds
    the ops for a cut flash (pre ramp on A, peak on the cut frame, exp tail on B).
  time.velocity: ed_fx.velocity_times(beats, fps, n, seg_f0, src_t0, anchors) -> segment 'times' / 'speed_curve';
    ed_fx.shutter_spec(times, fps_out, fps_src) -> per-frame sub-frame offsets to average (motion blur).
"""
import math
import json
import re
import hashlib
from collections import OrderedDict
import numpy as np
import cv2

F32 = np.float32
_STATE = OrderedDict()   # LRU: per-size grids/masks/banks and per-segment sequential state


# ============================================================================= small helpers
def _state(key, limit=40):
    st = _STATE.get(key)
    if st is None:
        while len(_STATE) >= limit:
            _STATE.popitem(last=False)
        st = _STATE[key] = {}
    else:
        _STATE.move_to_end(key)
    return st


def reset_state():
    """Forget sequential caches (temporal fx, datamosh, holds, per-shot thresholds and palettes)."""
    _STATE.clear()


def _fxkey(fx):
    return hashlib.blake2b(json.dumps(fx, sort_keys=True, default=str).encode(), digest_size=8).hexdigest()


def _seed(*parts):
    return int.from_bytes(hashlib.blake2b(repr(parts).encode(), digest_size=8).digest(), 'little')


def _rng(*parts):
    return np.random.default_rng(_seed(*parts))


def _hash_u01(seed, idx):
    """Vectorised splitmix64: uniform [0, 1) for integer indices (random access, order independent)."""
    with np.errstate(over='ignore'):
        z = np.asarray(idx).astype(np.int64).astype(np.uint64) + np.uint64(seed & 0xFFFFFFFFFFFFFFFF)
        z = z * np.uint64(0x9E3779B97F4A7C15)
        z ^= z >> np.uint64(30)
        z = z * np.uint64(0xBF58476D1CE4E5B9)
        z ^= z >> np.uint64(27)
        z = z * np.uint64(0x94D049BB133111EB)
        z ^= z >> np.uint64(31)
    return (z >> np.uint64(11)).astype(np.float64) / float(1 << 53)


def _hash_normal(seed, idx):
    u1 = np.clip(_hash_u01(seed, idx), 1e-12, 1.0)
    u2 = _hash_u01(seed ^ 0x5DEECE66D, idx)
    return np.sqrt(-2.0 * np.log(u1)) * np.cos(2 * np.pi * u2)


def _f32(x):
    if x.dtype == F32 and x.flags['C_CONTIGUOUS']:
        return x
    return np.ascontiguousarray(x, dtype=F32)


def _fps(ctx):
    return float(ctx.get('fps') or 30.0)


def _short(ctx):
    return float(min(int(ctx['ow']), int(ctx['oh'])))


def _u(ctx):
    return _short(ctx) / 1080.0


def _abs_frame(ctx, k):
    f0 = ctx.get('seg_f0')
    if f0 is not None and k is not None:
        return int(f0) + int(k)
    return int(ctx.get('f_abs', k or 0))


def snap(t, fps):
    """Peak frame of an event at absolute time t: floor(t*fps + 0.4) (earlier by <= 0.6 frame, later by <= 0.4)."""
    return int(math.floor(float(t) * float(fps) + 0.4))


def ease(p, kind='linear'):
    """Easing 0..1 -> 0..1. Card names (inQuad ... inOutExpo, inSine.., outBack, hold) and ed_edl names
    (in, out, inout = smoothstep, expo_out)."""
    p = 0.0 if p != p else min(max(float(p), 0.0), 1.0)
    k = kind or 'linear'
    if k in ('linear', 'lin', 'none'):
        return p
    if k == 'hold':
        return 1.0 if p >= 1.0 else 0.0
    if k in ('in', 'inQuad'):
        return p * p
    if k in ('out', 'outQuad'):
        return 1 - (1 - p) ** 2
    if k == 'inout':
        return p * p * (3 - 2 * p)
    if k == 'inOutQuad':
        return 2 * p * p if p < 0.5 else 1 - (-2 * p + 2) ** 2 / 2
    if k == 'inCubic':
        return p ** 3
    if k == 'outCubic':
        return 1 - (1 - p) ** 3
    if k == 'inOutCubic':
        return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2
    if k == 'inQuart':
        return p ** 4
    if k == 'outQuart':
        return 1 - (1 - p) ** 4
    if k == 'inQuint':
        return p ** 5
    if k == 'outQuint':
        return 1 - (1 - p) ** 5
    if k == 'inOutQuint':
        return 16 * p ** 5 if p < 0.5 else 1 - (-2 * p + 2) ** 5 / 2
    if k == 'inExpo':
        return 0.0 if p <= 0 else 2 ** (10 * p - 10)
    if k in ('outExpo', 'expo_out'):
        return 1.0 if p >= 1 else 1 - 2 ** (-10 * p)
    if k == 'inOutExpo':
        if p <= 0 or p >= 1:
            return p
        return 2 ** (20 * p - 10) / 2 if p < 0.5 else (2 - 2 ** (-20 * p + 10)) / 2
    if k == 'inSine':
        return 1 - math.cos(p * math.pi / 2)
    if k == 'outSine':
        return math.sin(p * math.pi / 2)
    if k == 'inOutSine':
        return -(math.cos(math.pi * p) - 1) / 2
    if k == 'outBack':
        c1 = 1.70158
        return 1 + (c1 + 1) * (p - 1) ** 3 + c1 * (p - 1) ** 2
    return p


_NAMED = {'white': '#ffffff', 'black': '#000000', 'warm': '#fff1dc', 'red': '#ff2a2a', 'cyan': '#29e6ff',
          'magenta': '#ff2bd6', 'acid': '#b6ff2b', 'amber': '#ffb02e', 'navy': '#0b1020', 'grey': '#808080',
          'gray': '#808080', 'yellow': '#ffe14a', 'green': '#45f06b', 'blue': '#3f7bff', 'gold': '#eebb14',
          'orange': '#ff7d00', 'purple': '#7a3cff', 'pink': '#ff1f4b', 'cream': '#f2ede4', 'teal': '#14b8a6'}
_WARNED = set()


def _warn_once(key, msg):
    if key not in _WARNED:
        _WARNED.add(key)
        import sys
        print(f'[ed_fx] {msg}', file=sys.stderr)


def _parse_hex(s):
    s = s.strip().lower()
    if s.startswith('0x'):
        s = s[2:]
    s = s.lstrip('#')
    if len(s) in (3, 4):
        s = ''.join(ch * 2 for ch in s)
    if len(s) not in (6, 8) or any(ch not in '0123456789abcdef' for ch in s):
        return None
    return [int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]


def color(c, default=(1.0, 1.0, 1.0)):
    """Any colour spec -> float32[3] 0..1 (alpha is ignored). Accepts '#rgb' | '#rgba' | '#rrggbb' | '#rrggbbaa'
    (with or without '#', or '0x…') | 'rgb(255, 0, 0)' / 'rgba(…)' | a name (white black warm red cyan magenta acid
    amber navy grey yellow green blue gold orange purple pink cream teal) | [r, g, b(, a)] list / tuple / ndarray
    (0..1 floats; 0..255 when any channel > 1) | int 0xRRGGBB | {'r', 'g', 'b'} | None (default). An unreadable spec
    falls back to `default` with a one-time warning instead of failing the frame."""
    if c is None:
        return np.array(default, F32)
    if isinstance(c, bool):
        return np.array(default, F32)
    if isinstance(c, str):
        s = c.strip()
        key = s.lower().replace(' ', '').replace('_', '')
        if key in _NAMED:
            s = _NAMED[key]
        elif s.lower() in _NAMED:
            s = _NAMED[s.lower()]
        if s.lower().startswith(('rgb(', 'rgba(')) and s.endswith(')'):
            try:
                return color([float(v) for v in s[s.index('(') + 1:-1].split(',')][:3], default)
            except ValueError:
                pass
        v = _parse_hex(s)
        if v is None:
            _warn_once(('color', s), f'unknown colour {c!r} -> {list(default)}')
            return np.array(default, F32)
        return np.array(v, F32)
    if isinstance(c, (int, np.integer)):
        v = int(c) & 0xFFFFFF
        return np.array([(v >> 16) & 255, (v >> 8) & 255, v & 255], F32) / 255.0
    if isinstance(c, dict):
        return color([c.get('r', 0), c.get('g', 0), c.get('b', 0)], default)
    try:
        a = np.array(c, F32).reshape(-1)[:3]
    except (TypeError, ValueError):
        _warn_once(('color', repr(c)), f'unknown colour {c!r} -> {list(default)}')
        return np.array(default, F32)
    if a.size == 1:
        a = np.repeat(a, 3)
    if a.size < 3 or not np.isfinite(a).all():
        _warn_once(('color', repr(c)), f'unknown colour {c!r} -> {list(default)}')
        return np.array(default, F32)
    return np.clip(a / 255.0 if a.max() > 1.0 else a, 0.0, 1.0).astype(F32)


def is_color(c):
    """True when c is a single colour spec (not a list of colours): str, int, dict, or 3-4 numbers."""
    if isinstance(c, (str, dict)) or (isinstance(c, (int, np.integer)) and not isinstance(c, bool)):
        return True
    if isinstance(c, np.ndarray):
        return c.ndim == 1 and c.size in (3, 4)
    return isinstance(c, (list, tuple)) and len(c) in (3, 4) and all(_num(v) for v in c)


def palette(spec, named=None, default=None):
    """Colour list spec -> list of float32[3]: a name from `named` | one colour (any color() spec) | [colour, ...]."""
    if spec is None:
        spec = default
    if isinstance(spec, str) and named and spec in named:
        spec = named[spec]
    if spec is None:
        return []
    if is_color(spec):
        return [color(spec)]
    return [color(c) for c in spec]


def _ints(spec):
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
        out += _ints(v)
    return out


def _num(v):
    return isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool)


_ANIM_T = {'letterbox', 'zoom.crash', 'roll', 'drift', 'light_leak', 'handheld', 'lens_warp', 'glow', 'pixel_art',
           'pixel_sort', 'datamosh'}


def active(fx, k, n, ctx):
    """Gate: 'frames' (segment-relative k, ints or 'a:b'), 'f' (absolute frames), 'k': [k0, k1], 't': [t0, t1]
    (absolute seconds, frames snap(t0)..snap(t1)). For fx that animate over 't' (letterbox, crash, roll, drift,
    light_leak, ...) 't' is the animation window, not a gate."""
    if fx.get('frames') is not None and int(k) not in set(_ints(fx['frames'])):
        return False
    if fx.get('f') is not None and _abs_frame(ctx, k) not in set(_ints(fx['f'])):
        return False
    kr = fx.get('k')
    if isinstance(kr, (list, tuple)) and len(kr) == 2 and not (kr[0] <= k <= kr[1]):
        return False
    t = fx.get('t')
    if (t is not None and _canon(fx.get('type')) not in _ANIM_T and isinstance(t, (list, tuple)) and len(t) == 2
            and _num(t[0]) and _num(t[1])):
        f = _abs_frame(ctx, k)
        fps = _fps(ctx)
        if not (snap(t[0], fps) <= f <= snap(t[1], fps)):
            return False
    return True


def amount(fx, k, n, ctx, key='amt'):
    """amt (default 1) * ramp to amt_to over the segment (ease) * amt_keys [[t_abs, v], ...]."""
    a = float(fx.get(key, 1.0))
    if key + '_to' in fx:
        a = a + (float(fx[key + '_to']) - a) * ease(k / max(n - 1, 1), fx.get('ease', 'linear'))
    keys = fx.get(key + '_keys')
    if keys:
        t = _abs_frame(ctx, k) / _fps(ctx)
        a *= float(np.interp(t, [q[0] for q in keys], [q[1] for q in keys]))
    return a


def anim(v, fx, k, n, ctx, ease_kind=None):
    """Scalar param that may be animated: number, or [v0, v1, ...] keys spread evenly over fx['t'] (absolute s;
    explicit key times in fx['t_keys']) or over the segment; eased per span by fx['ease']."""
    if not isinstance(v, (list, tuple)):
        return float(v)
    vals = [float(q) for q in v]
    if len(vals) == 1:
        return vals[0]
    e = ease_kind or fx.get('ease', 'linear')
    f = _abs_frame(ctx, k)
    fps = _fps(ctx)
    tk = fx.get('t_keys')
    if tk:
        times = [float(q) for q in tk]
    else:
        t = fx.get('t')
        if isinstance(t, (list, tuple)) and len(t) == 2 and _num(t[0]):
            times = list(np.linspace(float(t[0]), float(t[1]), len(vals)))
        else:
            f0 = ctx.get('seg_f0', 0) or 0
            times = list(np.linspace(f0 / fps, (f0 + max(n - 1, 1)) / fps, len(vals)))
    tt = f / fps
    if tt <= times[0]:
        return vals[0]
    if tt >= times[-1]:
        return vals[-1]
    i = int(np.searchsorted(times, tt, side='right')) - 1
    i = min(max(i, 0), len(vals) - 2)
    u = (tt - times[i]) / max(times[i + 1] - times[i], 1e-9)
    return vals[i] + (vals[i + 1] - vals[i]) * ease(u, e)


# ============================================================================= beats, events, envelopes
def beat_period(ctx):
    b = ctx.get('beats') or []
    if len(b) < 2:
        return None
    return float(np.median(np.diff(np.asarray(b, float))))


def _bar_positions(beats, downs):
    if len(beats) == 0:
        return np.zeros(0, int)
    if len(downs) == 0:
        return np.arange(len(beats)) % 4
    di = np.searchsorted(downs, beats + 0.03, side='right') - 1
    bi = np.searchsorted(beats, downs - 0.03, side='left')
    pos = np.zeros(len(beats), int)
    for i in range(len(beats)):
        pos[i] = (i - bi[0]) % 4 if di[i] < 0 else i - bi[di[i]]
    return pos


def resolve_times(spec, ctx, window=None):
    """Event times (absolute s): number | list | 'beats'/'1/4' | 'downbeats'/'bars' | '1/2' (beats 1 and 3) |
    'snare' (beats 2 and 4) | '1/8' | 'offbeat' | {'every': spec, 't': [t0, t1]}; window [t0, t1] filters."""
    beats = np.asarray(ctx.get('beats') or [], float)
    downs = np.asarray(ctx.get('downbeats') or [], float)
    if spec is None:
        out = []
    elif _num(spec):
        out = [float(spec)]
    elif isinstance(spec, dict):
        return resolve_times(spec.get('every', 'beats'), ctx, spec.get('t') or window)
    elif isinstance(spec, str):
        s = spec.strip().lower()
        mids = list((beats[:-1] + beats[1:]) / 2) if len(beats) > 1 else []
        if s in ('beats', 'beat', '1/4', 'kick', 'kicks'):
            out = list(beats)
        elif s in ('downbeats', 'downbeat', 'bars', 'bar', '1/1'):
            out = list(downs) if len(downs) else list(beats[::4])
        elif s in ('1/2', 'half'):
            out = list(beats[_bar_positions(beats, downs) % 2 == 0])
        elif s in ('snare', 'snares', 'backbeat', '2&4'):
            out = list(beats[_bar_positions(beats, downs) % 2 == 1])
        elif s == '1/8':
            out = sorted(list(beats) + mids)
        elif s in ('offbeat', 'offbeats', '&'):
            out = mids
        elif s in ('', 'none'):
            out = []
        else:
            out = [float(s)]
    else:
        out = []
        for v in spec:
            out += resolve_times(v, ctx)
    out = sorted(float(v) for v in out)
    if window and len(window) == 2:
        out = [v for v in out if window[0] - 1e-6 <= v <= window[1] + 1e-6]
    return out


def events(fx, ctx, default=None, key='times'):
    """[(t, peak_frame, weight, index)] for fx[key] (default spec when absent); weight from beat_strength when
    fx['by'] == 'onset_strength'."""
    spec = fx.get(key, default)
    if spec is None:
        return []
    ts = resolve_times(spec, ctx, fx.get('section'))
    fps = _fps(ctx)
    ws = None
    if fx.get('by') in ('onset_strength', 'strength') and ctx.get('beat_strength') and ctx.get('beats'):
        bt = np.asarray(ctx['beats'], float)
        bs = np.asarray(ctx['beat_strength'], float)
        bs = (bs - bs.min()) / max(bs.max() - bs.min(), 1e-9)
        ws = []
        for t in ts:
            i = int(np.argmin(np.abs(bt - t)))
            ws.append(float(bs[i]) if abs(bt[i] - t) < 0.06 else 1.0)
    return [(t, snap(t, fps), (ws[i] if ws else 1.0), i) for i, t in enumerate(ts)]


def env_value(d, attack=0, hold=1, tau=2.0, decay='exp', cutoff=0.02):
    """Pulse envelope at d frames from the peak frame: linear attack over `attack` frames before it, `hold` frames
    at 1 (>= 1, the peak frame itself), then exp(-(d - hold + 1)/tau) | 'step' 1/2 per frame | 'lin'; < cutoff -> 0."""
    if d < -attack:
        return 0.0
    if d < 0:
        return (d + attack + 1) / (attack + 1)
    h = max(int(round(hold)), 1)
    if d < h:
        return 1.0
    m = d - h + 1
    if decay == 'step':
        v = 0.5 ** m
    elif decay == 'lin':
        v = 1 - m / (tau + 1)
    elif decay in ('none', 'hold'):
        v = 1.0
    else:
        v = math.exp(-m / tau) if tau > 0 else 0.0
    return v if v >= cutoff else 0.0


def pulse(fx, k, ctx, attack=0, hold=1, tau=2.0, decay='exp', cutoff=0.02, default_times=None):
    """(value 0..1, event) of event-driven fx (fx['times'] + fx['env'] overrides, frames @25 rescaled to fps);
    (1.0, None) when the fx has no times (constant fx)."""
    if fx.get('times', default_times) is None:
        return 1.0, None
    env = dict(attack=attack, hold=hold, tau=tau, decay=decay, cutoff=cutoff)
    env.update(fx.get('env') or {})
    sc = _fps(ctx) / 25.0
    a = int(round(float(env['attack']) * sc))
    h = max(1, int(round(float(env['hold']) * sc)))
    tu = float(env['tau']) * sc
    f = _abs_frame(ctx, k)
    best, bev = 0.0, None
    for ev in events(fx, ctx, default_times):
        d = f - ev[1]
        if d < -a or d > h + 12 * max(tu, 1):
            continue
        v = ev[2] * env_value(d, a, h, tu, env['decay'], env['cutoff'])
        if v > best:
            best, bev = v, ev
    return best, bev


def _env_fn(fx, ctx):
    """Bass envelope t -> 0..1 (normalised with p10/p95): fx['env_t'] [[t, v], ...] | ctx['bass_env'] | synthetic
    from beats (instant attack, 0.12 s release)."""
    src = fx.get('env_t') or ctx.get('bass_env')
    if src:
        if isinstance(src, dict):
            ts, vs = np.asarray(src['t'], float), np.asarray(src['v'], float)
        else:
            arr = np.asarray(src, float)
            ts, vs = arr[:, 0], arr[:, 1]
        sec = fx.get('section')
        sel = (ts >= sec[0]) & (ts <= sec[1]) if sec else np.ones(len(ts), bool)
        p10, p95 = np.percentile(vs[sel] if sel.any() else vs, [10, 95])
        rngv = max(p95 - p10, 1e-9)
        return lambda t: float(np.clip((np.interp(t, ts, vs) - p10) / rngv, 0, 1))
    beats = np.asarray(ctx.get('beats') or [], float)
    rel = float(fx.get('release', 0.12))
    if len(beats) == 0:
        return lambda t: 1.0

    def fn(t):
        i = int(np.searchsorted(beats, t + 1e-6, side='right')) - 1
        return 0.0 if i < 0 else math.exp(-(t - beats[i]) / rel)
    return fn


def _vnoise_t(seed, x):
    """Smooth 1-D value noise (Catmull-Rom over hashed lattice), ~unit variance."""
    i = math.floor(x)
    fr = x - i
    v = _hash_normal(seed, np.arange(i - 1, i + 3))
    p0, p1, p2, p3 = v
    return float(0.5 * ((2 * p1) + (-p0 + p2) * fr + (2 * p0 - 5 * p1 + 4 * p2 - p3) * fr * fr +
                        (-p0 + 3 * p1 - 3 * p2 + p3) * fr ** 3)) * 1.35


def _smooth_noise_f(seed, f, sigma=1.0):
    """Per-frame N(0,1) smoothed in time with a Gaussian of sigma frames, renormalised to std 1."""
    if sigma <= 0.05:
        return float(_hash_normal(seed, np.array([f]))[0])
    r = int(math.ceil(3 * sigma))
    js = np.arange(f - r, f + r + 1)
    w = np.exp(-0.5 * ((js - f) / sigma) ** 2)
    return float((w * _hash_normal(seed, js)).sum() / math.sqrt((w * w).sum()))


# ============================================================================= image helpers
def _luma(x):
    return cv2.transform(_f32(x), np.array([[0.2126, 0.7152, 0.0722]], F32))


def _gray3(m):
    return cv2.merge([m, m, m])


def _mix(a, b, m):
    """a*(1-m) + b*m with a 1-channel mask m (0..1)."""
    m = _f32(m)
    return cv2.blendLinear(_f32(a), _f32(b), _f32(1.0 - m), m)


def _lerp(a, b, t):
    if t <= 0:
        return a
    if t >= 1:
        return b
    return cv2.addWeighted(_f32(a), 1.0 - float(t), _f32(b), float(t), 0.0)


def _clip01(x):
    return np.clip(x, 0.0, 1.0, out=x)


def _solid(h, w, col):
    out = np.empty((h, w, 3), F32)
    out[:] = color(col)
    return out


def _grid(h, w):
    key = ('grid', h, w)
    st = _state(key)
    if not st:
        gx, gy = np.meshgrid(np.arange(w, dtype=F32), np.arange(h, dtype=F32))
        st['gx'], st['gy'] = gx, gy
    return st['gx'], st['gy']


def _sim_matrix(s, rot, cx, cy, dx=0.0, dy=0.0):
    M = cv2.getRotationMatrix2D((float(cx), float(cy)), float(rot), float(s))
    M[0, 2] += dx
    M[1, 2] += dy
    return M


def _warp(x, M, w=None, h=None, border='reflect', interp=cv2.INTER_LINEAR, value=0.0):
    h = h or x.shape[0]
    w = w or x.shape[1]
    if border == 'black' or border == 'constant':
        return cv2.warpAffine(_f32(x), np.asarray(M, np.float64), (w, h), flags=interp,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=(value, value, value))
    if border == 'replicate':
        return cv2.warpAffine(_f32(x), np.asarray(M, np.float64), (w, h), flags=interp,
                              borderMode=cv2.BORDER_REPLICATE)
    return cv2.warpAffine(_f32(x), np.asarray(M, np.float64), (w, h), flags=interp,
                          borderMode=cv2.BORDER_REFLECT101)


def _down(x, f):
    h, w = x.shape[:2]
    return cv2.resize(x, (max(1, int(round(w / f))), max(1, int(round(h / f)))), interpolation=cv2.INTER_AREA)


def _up(x, w, h, interp=cv2.INTER_LINEAR):
    return cv2.resize(x, (w, h), interpolation=interp)


def dir_blur(x, length, angle=0.0):
    """Box motion blur of `length` px along `angle` degrees (0 = horizontal). Long blurs run at reduced
    resolution (the result is smooth along the line anyway)."""
    L = float(length)
    if L < 1.5:
        return x
    h, w = x.shape[:2]
    a = float(angle) % 180.0
    f = 1.0
    if L > 24:
        f = min(8.0, L / 16.0)
    xs = _down(x, f) if f > 1 else x
    Ls = max(1, int(round(L / f)))
    if Ls >= 2:
        if a < 1.0 or a > 179.0:
            ys = cv2.blur(xs, (Ls, 1))
        elif abs(a - 90.0) < 1.0:
            ys = cv2.blur(xs, (1, Ls))
        else:
            kk = np.zeros((Ls, Ls), F32)
            c = (Ls - 1) / 2.0
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            for i in range(Ls * 2):
                t = (i / (Ls * 2 - 1) - 0.5) * (Ls - 1)
                kk[int(round(c + t * sa)), int(round(c + t * ca))] = 1.0
            kk /= kk.sum()
            ys = cv2.filter2D(xs, -1, kk, borderType=cv2.BORDER_REFLECT101)
    else:
        ys = xs
    return _up(ys, w, h) if f > 1 else ys


def _sim_power(M, v):
    """Fractional power M^v of a 2x3 similarity transform (geodesic interpolation from identity)."""
    A = M[:, :2]
    t = M[:, 2]
    s = math.sqrt(max(abs(np.linalg.det(A)), 1e-12))
    th = math.atan2(A[0, 1], A[0, 0])
    sv, thv = s ** v, th * v
    Av = np.array([[sv * math.cos(thv), sv * math.sin(thv)], [-sv * math.sin(thv), sv * math.cos(thv)]])
    IA = np.eye(2) - A
    if abs(np.linalg.det(IA)) < 1e-9:
        tv = t * v
    else:
        p = np.linalg.solve(IA, t)
        tv = p - Av @ p
    return np.hstack([Av, tv[:, None]])


def _path_blur_raw(y, M, n, border):
    steps = int(round(math.log2(n)))
    d = 1.0 / (n - 1)
    for i in range(steps):
        Mi = _sim_power(M, d * (2 ** i))
        y = cv2.addWeighted(y, 0.5, _warp(y, Mi, border=border), 0.5, 0.0)
    return y


def path_blur(x, M_full, n=8, border='reflect'):
    """Mean of x warped by M_full^v, v = 0..1 (n samples, rounded to a power of two) via repeated doubling:
    log2(n) warps. M_full: 2x3 similarity from the current frame to the shutter-start frame. Trails above 8 px are
    computed at half resolution; pixels whose own trail is under ~4 px (around the zoom/rotation fixed point) keep
    the full-resolution frame."""
    x = _f32(x)
    h, w = x.shape[:2]
    M = np.asarray(M_full, np.float64)
    A, t = M[:, :2], M[:, 2]
    D = A - np.eye(2)
    corners = np.array([[0, 0], [w, 0], [0, h], [w, h]], float)
    dmax = float(np.max(np.linalg.norm(corners @ D.T + t, axis=1)))
    if dmax < 0.75:
        return x
    n = int(2 ** max(1, round(math.log2(max(2, n)))))
    if dmax <= 8 or min(h, w) < 128:
        return _path_blur_raw(x, M, min(n, 4) if dmax <= 8 else n, border)
    Ms = M.copy()
    Ms[:, 2] *= 0.5
    yb = cv2.resize(_path_blur_raw(_down(x, 2), Ms, n, border), (w, h), interpolation=cv2.INTER_LINEAR)
    hq, wq = max(4, h // 8), max(4, w // 8)
    gx, gy = np.meshgrid(np.linspace(0, w, wq), np.linspace(0, h, hq))
    dq = np.hypot(D[0, 0] * gx + D[0, 1] * gy + t[0], D[1, 0] * gx + D[1, 1] * gy + t[1])
    m = np.clip((dq - 2.0) / 4.0, 0, 1).astype(F32)
    if float(m.min()) >= 1.0:
        return yb
    return _mix(x, yb, cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR))


def warp_blur(img, M_main, G, n=8, border='reflect'):
    """img warped by the 2x3 forward map M_main, motion-blurred along G (2x3 similarity from the warped frame to the
    shutter-start frame). Heavy trails are rendered at half resolution; only the region whose trail stays under
    ~4 px (around the fixed point) is warped at full resolution."""
    img = _f32(img)
    h, w = img.shape[:2]
    G = np.asarray(G, np.float64)
    A, t = G[:, :2], G[:, 2]
    D = A - np.eye(2)
    corners = np.array([[0, 0], [w, 0], [0, h], [w, h]], float)
    dmax = float(np.max(np.linalg.norm(corners @ D.T + t, axis=1)))
    if dmax <= 8 or min(h, w) < 128:
        return path_blur(_warp(img, M_main, border=border), G, n, border)
    n = int(2 ** max(1, round(math.log2(max(2, n)))))
    Mm = np.asarray(M_main, np.float64).copy()
    Mh = Mm.copy()
    Mh[:, 2] *= 0.5
    Gh = G.copy()
    Gh[:, 2] *= 0.5
    ys = _path_blur_raw(_warp(_down(img, 2), Mh, border=border), Gh, n, border)
    yb = cv2.resize(ys, (w, h), interpolation=cv2.INTER_LINEAR)
    hq, wq = max(4, h // 8), max(4, w // 8)
    gx, gy = np.meshgrid(np.linspace(0, w, wq), np.linspace(0, h, hq))
    dq = np.hypot(D[0, 0] * gx + D[0, 1] * gy + t[0], D[1, 0] * gx + D[1, 1] * gy + t[1])
    m = np.clip((dq - 2.0) / 4.0, 0, 1).astype(F32)
    if float(m.min()) >= 1.0:
        return yb
    ys_, xs_ = np.nonzero(m < 1.0)
    x0 = int(max(0, np.floor(xs_.min() * w / (wq - 1)) - 8))
    x1 = int(min(w, np.ceil(xs_.max() * w / (wq - 1)) + 8))
    y0 = int(max(0, np.floor(ys_.min() * h / (hq - 1)) - 8))
    y1 = int(min(h, np.ceil(ys_.max() * h / (hq - 1)) + 8))
    Mr = Mm.copy()
    Mr[:, 2] -= (x0, y0)
    roi = cv2.warpAffine(img, Mr, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    roi = _path_blur_raw(roi, _shift_sim(G, x0, y0), 2, border) if dmax > 0 else roi
    mf = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
    yb[y0:y1, x0:x1] = _mix(roi, np.ascontiguousarray(yb[y0:y1, x0:x1]), np.ascontiguousarray(mf[y0:y1, x0:x1]))
    return yb


def _shift_sim(G, x0, y0):
    """Express a 2x3 transform in the coordinates of an ROI starting at (x0, y0)."""
    T = np.array([[1, 0, x0], [0, 1, y0], [0, 0, 1]], float)
    Ti = np.array([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]], float)
    return (Ti @ np.vstack([G, [0, 0, 1]]) @ T)[:2]


def zoom_blur(x, ratio, cx=0.5, cy=0.5, n=8):
    """Radial blur: mean of x scaled by ratio^v about (cx, cy) (fractions), v = 0..1."""
    if abs(math.log(max(ratio, 1e-6))) < 1e-3:
        return x
    h, w = x.shape[:2]
    return path_blur(x, cv2.getRotationMatrix2D((cx * w, cy * h), 0.0, float(ratio)), n)


def spin_blur(x, dtheta, cx=0.5, cy=0.5, n=8, scale=1.0):
    """Rotational blur over dtheta degrees (OpenCV sign) about (cx, cy)."""
    if abs(dtheta) < 0.05 and abs(scale - 1) < 1e-3:
        return x
    h, w = x.shape[:2]
    return path_blur(x, cv2.getRotationMatrix2D((cx * w, cy * h), float(dtheta), float(scale)), n)


# ============================================================================= camera fx
_ATT = {0: [], 1: [0.25], 2: [0.11, 0.44]}
ZERO = (0.0, 0.0, 0.0, 0.0)


def _center(fx, ctx, key='center'):
    c = fx.get(key, [0.5, 0.5])
    if isinstance(c, str):
        c = ctx.get(c) or ctx.get('face') or [0.5, 0.5]
    return float(c[0]), float(c[1])


def _fixed_point(fx, ctx, s, rot=0.0, key='center'):
    """Shift that keeps the fx centre in place under zoom s / rotation rot about the frame centre."""
    cx, cy = _center(fx, ctx, key)
    px, py = (cx - 0.5) * ctx['ow'], (cy - 0.5) * ctx['oh']
    if rot:
        a = math.radians(rot)
        rx = s * (math.cos(a) * px + math.sin(a) * py)
        ry = s * (-math.sin(a) * px + math.cos(a) * py)
    else:
        rx, ry = s * px, s * py
    return px - rx, py - ry


def _hold_ends(fx, ev, ctx):
    hu = fx.get('hold_until', 'cut')
    fps = _fps(ctx)
    beats = sorted(ctx.get('beats') or [])
    ends = []
    for j, (t, k0, w, i) in enumerate(ev):
        nxt = ev[j + 1][1] if j + 1 < len(ev) else None
        if hu in ('next', 'next_event'):
            e = nxt if nxt is not None else 10 ** 9
        elif hu == 'next_beat':
            nb = [b for b in beats if b > t + 0.06]
            e = snap(nb[0], fps) if nb else 10 ** 9
        elif _num(hu):
            e = snap(hu, fps)
        else:
            e = 10 ** 9
        ends.append(e)
    return ends


def cam_zoom_punch(fx, k, n, ctx):
    """zoom.punch / beat_punch - digital punch-in x1.1-1.35 landing exactly on the beat frame floor(t*fps+0.4).
    times='beats'|'downbeats'|'1/2'|'snare'|[t...]; scale=1.2; mode='bounce'|'hold'|'spring'|'ladder'|'out';
    attack=0|1|2 frames before the beat (ln S fractions .25 / .11,.44); release=0.32 s (bounce: ln s = ln S (1-k/D)^3,
    D=round(release*fps) capped at 0.7 beat); hold_until='cut'|'next'|'next_beat'|t; spring={settle:1.15, tau:0.1,
    period:0.2}; ladder={step:1.12, per:'1/4'|'1/8', count, reset:'downbeat'|t, max_total:1.5};
    center=[0.5,0.5]|'face'; blur_shutter=0.5 (radial blur on frames with |d ln s| >= 0.02; 0 = clean)."""
    fps = _fps(ctx)
    f = _abs_frame(ctx, k)
    S = float(fx.get('scale', 1.2))
    lnS = math.log(max(S, 1e-3))
    mode = fx.get('mode', 'bounce')
    ev = events(fx, ctx, 'beats')
    if mode == 'ladder' and 'times' not in fx:
        ev = _ladder_events(fx, ctx)
    if not ev:
        return ZERO
    att = min(max(int(fx.get('attack', 0)), 0), 2)
    af = _ATT[att]
    lnz = 0.0
    if mode == 'bounce':
        D = int(fx.get('release_frames') or max(1, round(float(fx.get('release', 0.32)) * fps)))
        bp = beat_period(ctx)
        if bp and fx.get('cap_release', True):
            D = min(D, max(2, int(math.floor(0.7 * bp * fps))))
        for t, k0, w, i in ev:
            d = f - k0
            if -att <= d < 0:
                v = af[att + d]
            elif 0 <= d <= D:
                v = (1.0 - d / D) ** 3
            else:
                continue
            lnz = max(lnz, v * lnS * w) if lnS >= 0 else min(lnz, v * lnS * w)
    elif mode in ('hold', 'speech'):
        for (t, k0, w, i), end in zip(ev, _hold_ends(fx, ev, ctx)):
            d = f - k0
            if -att <= d < 0:
                lnz = max(lnz, af[att + d] * lnS * w)
            elif k0 <= f < end:
                lnz = max(lnz, lnS * w)
    elif mode == 'spring':
        sp = dict(settle=1.15, tau=0.1, period=0.2)
        sp.update(fx.get('spring') or {})
        Sh, tau_f, P = float(sp['settle']), float(sp['tau']) * fps, float(sp['period']) / 2.0 * fps
        cur = None
        for (t, k0, w, i), end in zip(ev, _hold_ends(fx, ev, ctx)):
            d = f - k0
            if -att <= d < 0:
                cand = af[att + d] * lnS * w
            elif 0 <= d and f < end:
                env = (S - Sh) * math.exp(-d / tau_f)
                s = Sh + (env * math.cos(math.pi * d / P) if abs(env) >= 0.004 else 0.0)   # settled (card table)
                cand = math.log(max(s, 1e-3)) * w
            else:
                continue
            if cur is None or k0 >= cur[0]:
                cur = (k0, cand)
        lnz = cur[1] if cur else 0.0
    elif mode == 'ladder':
        lad = dict(step=1.12, reset='downbeat', max_total=1.5)
        lad.update(fx.get('ladder') or {})
        kr = _ladder_reset(lad, ev, ctx)
        if kr is None or f < kr:
            m = sum(1 for e in ev if e[1] <= f)
            lnz = min(m * math.log(float(lad['step'])), math.log(float(lad['max_total'])))
    elif mode in ('out', 'punch_out'):
        k0 = ev[0][1]
        start = snap(fx['from'], fps) if 'from' in fx else -10 ** 9
        lnz = lnS if start <= f < k0 else 0.0
    s = math.exp(lnz)
    dx, dy = _fixed_point(fx, ctx, s)
    return (lnz, 0.0, dx, dy)


def _ladder_events(fx, ctx):
    lad = dict(step=1.12, per='1/4')
    lad.update(fx.get('ladder') or {})
    reset = lad.get('reset')
    if not _num(reset):
        return []
    beats = [b for b in (ctx.get('beats') or []) if b < float(reset) - 0.05]
    if lad.get('per') == '1/8':
        last2 = beats[-2:]
        bp = beat_period(ctx) or 0.5
        ts = sorted(last2 + [b + bp / 2 for b in last2])
    else:
        cnt = int(lad.get('count', 3 if float(lad['step']) >= 1.115 else 4))
        ts = beats[-cnt:]
    fps = _fps(ctx)
    return [(t, snap(t, fps), 1.0, i) for i, t in enumerate(ts)]


def _ladder_reset(lad, ev, ctx):
    r = lad.get('reset', 'downbeat')
    fps = _fps(ctx)
    if _num(r):
        return snap(r, fps)
    if r in ('downbeat', 'drop') and ev:
        last = ev[-1][0]
        dn = [d for d in (ctx.get('downbeats') or []) if d > last + 0.05]
        if dn:
            return snap(dn[0], fps)
    return None


_SHAKE = {'impact': dict(amp=0.025, rot=0.0, tau=0.067), 'heavy': dict(amp=0.05, rot=1.5, tau=0.11),
          'micro': dict(amp=0.005, rot=0.15), 'rot': dict(amp=0.004, rot=2.5, tau=0.067),
          'kick_tilt': dict(amp=0.0, rot=4.0, tau=0.1), 'bass': dict(amp=0.015, rot=0.0, gamma=1.75)}
_SHAKE_ALIAS = {'rotational': 'rot', 'kick-tilt': 'kick_tilt', 'kicktilt': 'kick_tilt', 'bass_follow': 'bass',
                'bass-follow': 'bass'}


def _shake_params(fx):
    prof = _SHAKE_ALIAS.get(fx.get('profile', 'impact'), fx.get('profile', 'impact'))
    P = dict(_SHAKE.get(prof, _SHAKE['impact']))
    for key in ('amp', 'rot', 'tau', 'gamma'):
        if key in fx:
            P[key] = float(fx[key])
    return prof, P


def shake_table(tau, fps, alternating=True, cutoff=0.08):
    """Impulse profile g(k): (-q)^k (or q^k), q = exp(-1/(tau*fps)), cut where |g| < cutoff."""
    q = math.exp(-1.0 / (tau * fps))
    out = []
    for kk in range(200):
        g = ((-q) ** kk) if alternating else q ** kk
        if abs(g) < cutoff:
            break
        out.append(g)
    return out


def _shake_dirs(seed, i, dir_spec, dtheta, m):
    rng = _rng(seed, 'shake', i)
    if _num(dir_spec):
        a0 = float(dir_spec)
    elif dir_spec == 'random':
        a0 = rng.uniform(0, 360)
    elif dir_spec == 'horizontal':
        a0 = float(rng.choice([0.0, 180.0])) + rng.uniform(-20, 20)
    elif dir_spec == 'up':
        a0 = 270.0 + rng.uniform(-20, 20)
    else:
        a0 = 90.0 + rng.uniform(-20, 20)
    angs = [a0]
    for _ in range(1, m):
        angs.append(angs[-1] + float(rng.choice([-1.0, 1.0])) * rng.uniform(max(0.0, dtheta - 10), dtheta + 10))
    return [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in angs]


def cam_shake(fx, k, n, ctx):
    """shake.beat / beat_shake - beat-locked shake: full displacement A on the beat frame (unit direction, vertical
    and rotation also on that frame), alternating rebound g(k)=(-q)^k, q=exp(-1/(tau*fps)), direction turning
    +-dtheta each frame, exact rest afterwards. profile='impact' (amp .025 of the short side, tau .067 s) | 'heavy'
    (.05, rot 1.5 deg, tau .11) | 'micro' (continuous .005, smoothed noise, A*(0.4+0.6 env)) | 'rot' (rot 2.5,
    amp .004) | 'kick_tilt' (rot 4 deg * exp(-k/(0.1 s)), no rebound) | 'bass' (continuous, A=.015*norm(env)^1.75,
    direction AR(1) 0.5); times='beats'; dir='bass_down'|'horizontal'|'random'|'up'|deg; dtheta=30; seed;
    section=[t0,t1]; blur_shutter=0.5 (directional blur along the jump); cover='auto'|'reframe'|number|'reflect'
    (constant zoom margin for the whole clip, applied by camera())."""
    prof, P = _shake_params(fx)
    fps = _fps(ctx)
    f = _abs_frame(ctx, k)
    Spx = _short(ctx)
    A = float(P.get('amp', 0.0)) * Spx
    R = float(P.get('rot', 0.0))
    seed = _seed('shake', fx.get('seed', 0))
    sec = fx.get('section')
    if sec and not (snap(sec[0], fps) <= f <= snap(sec[1], fps)):
        return ZERO
    dx = dy = rot = 0.0
    if prof in ('micro', 'bass'):
        t = f / fps
        envf = _env_fn(fx, ctx) if (prof == 'bass' or fx.get('env_t') or ctx.get('bass_env')) else None
        if prof == 'micro':
            e = envf(t) if envf else 1.0
            a = A * (0.4 + 0.6 * e)
            sg = float(fx.get('smooth', 1.0))
            dx = a * _smooth_noise_f(seed + 1, f, sg)
            dy = a * _smooth_noise_f(seed + 2, f, sg)
            rot = R * _smooth_noise_f(seed + 3, f, sg)
        else:
            e = envf(t) ** float(P.get('gamma', 1.75))
            js = np.arange(f - 8, f + 1)
            wts = 0.5 ** (f - js)
            vx = float((wts * _hash_normal(seed + 4, js)).sum())
            vy = float((wts * _hash_normal(seed + 5, js)).sum())
            nv = math.hypot(vx, vy) or 1.0
            dx, dy = A * e * vx / nv, A * e * vy / nv
            rot = R * e * _smooth_noise_f(seed + 6, f, 1.0)
    else:
        tau = float(P.get('tau', 0.067))
        tbl = shake_table(tau, fps, alternating=(prof != 'kick_tilt'))
        m = len(tbl)
        dir_spec = fx.get('dir', 'horizontal' if fx.get('times') == 'snare' else 'bass_down')
        dth = float(fx.get('dtheta', 30.0))
        for t, k0, w, i in events(fx, ctx, 'beats'):
            d = f - k0
            if not 0 <= d < m:
                continue
            g = tbl[d]
            if A > 0:
                ux, uy = _shake_dirs(seed, i, dir_spec, dth, m)[d]
                dx += A * w * g * ux
                dy += A * w * g * uy
            if R:
                sgn = 1.0 if i % 2 == 0 else -1.0
                rot += R * w * g * sgn * float(fx.get('rot_sign', 1.0))
    if rot and fx.get('center') is not None:
        ex, ey = _fixed_point(fx, ctx, 1.0, rot)
        dx, dy = dx + ex, dy + ey
    return (0.0, rot, dx, dy)


def shake_cover(fx, ctx):
    """Constant zoom margin hiding the edges for a shake fx (shake.beat params.cover)."""
    cov = fx.get('cover', 'auto')
    if _num(cov):
        return float(cov)
    if cov in (None, 'reflect', 'none', False):
        return 1.0
    prof, P = _shake_params(fx)
    A = float(P.get('amp', 0.0)) * (2.5 if prof == 'micro' else 1.0)
    R = math.radians(abs(float(P.get('rot', 0.0))) * (2.5 if prof == 'micro' else 1.0))
    asp = max(ctx['ow'], ctx['oh']) / min(ctx['ow'], ctx['oh'])
    if cov == 'reframe':
        return (1 + 1.125 * A) * (math.cos(R) + 0.56 * math.sin(R))
    return (1 + 2 * A) * (math.cos(R) + asp * math.sin(R))


def cam_zoom_crash(fx, k, n, ctx):
    """zoom.crash - lightning zoom x2.5-9 (scale=4) over dur=0.4 s (8-16 frames @25) eased inOutCubic in log scale,
    landing at at=t (or t=[t0,t1]; default: segment start) and holding; center=[x,y]|'face' stays fixed (the
    frame 'slides' toward it); stages=2 (two jerks, pause=3 frames); back={after:0.4, dur:0.4} mirrored return;
    blur_shutter=0.5 (radial blur on fast frames)."""
    fps = _fps(ctx)
    f = _abs_frame(ctx, k)
    S = float(fx.get('scale', 4.0))
    lnS = math.log(max(S, 1e-3))
    D = float(fx.get('dur', 0.4))
    if 'at' in fx:
        t1 = float(fx['at'])
        t0 = t1 - D
    elif isinstance(fx.get('t'), (list, tuple)):
        t0, t1 = float(fx['t'][0]), float(fx['t'][1])
    else:
        t0 = (ctx.get('seg_f0') or 0) / fps
        t1 = t0 + D
    k0, k1 = snap(t0, fps), snap(t1, fps)
    E = fx.get('ease', 'inOutCubic')
    st = int(fx.get('stages', 1))
    if st >= 2:
        pause = int(fx.get('pause', 3))
        L = max(1, (k1 - k0 - pause) // 2)
        u1 = (f - k0) / L
        u2 = (f - (k0 + L + pause)) / max(1, (k1 - k0 - pause - L))
        v = 0.5 * ease(u1, E) + 0.5 * ease(u2, E)
    else:
        v = ease((f - k0) / max(k1 - k0, 1), E)
    back = fx.get('back')
    if back:
        bd = float(back.get('dur', D))
        kb0 = snap(t1 + float(back.get('after', 0.4)), fps)
        kb1 = kb0 + max(1, int(round(bd * fps)))
        v *= 1.0 - ease((f - kb0) / max(kb1 - kb0, 1), back.get('ease', E))
    lnz = lnS * v
    dx, dy = _fixed_point(fx, ctx, math.exp(lnz))
    return (lnz, 0.0, dx, dy)


def cam_zoom_in_out(fx, k, n, ctx):
    """zoom.in_out / beat_pulse - zoom in on the beat (outCubic) and back to x1.0 (inCubic, mirror); scale=1.3;
    times='beats'; stroke = half a beat (s); stroke_out; hold=0 s at the peak; cycles=N (first N events);
    center; blur_shutter: 0.5 when the stroke < 0.35 s else 0."""
    fps = _fps(ctx)
    f = _abs_frame(ctx, k)
    S = float(fx.get('scale', 1.3))
    lnS = math.log(max(S, 1e-3))
    ev = events(fx, ctx, 'beats')
    if fx.get('cycles'):
        ev = ev[:int(fx['cycles'])]
    bp = beat_period(ctx)
    stroke = float(fx.get('stroke') or ((bp / 2) if bp else 0.25))
    nin = max(1, int(round(stroke * fps)))
    nout = max(1, int(round(float(fx.get('stroke_out', stroke)) * fps)))
    hold = int(round(float(fx.get('hold', 0.0)) * fps))
    ei, eo = fx.get('ease_in', 'outCubic'), fx.get('ease_out', 'inCubic')
    lnz = 0.0
    for t, k0, w, i in ev:
        d = f - k0
        if 0 <= d < nin:
            v = ease((d + 1) / nin, ei)
        elif nin <= d < nin + hold:
            v = 1.0
        elif nin + hold <= d < nin + hold + nout:
            v = 1.0 - ease((d - nin - hold + 1) / nout, eo)
        else:
            continue
        lnz = max(lnz, v * lnS * w)
    dx, dy = _fixed_point(fx, ctx, math.exp(lnz))
    return (lnz, 0.0, dx, dy)


def _window_u(fx, k, n, ctx):
    fps = _fps(ctx)
    t = fx.get('t')
    if isinstance(t, (list, tuple)) and len(t) == 2 and _num(t[0]):
        k0, k1 = snap(t[0], fps), snap(t[1], fps)
        return (_abs_frame(ctx, k) - k0) / max(k1 - k0, 1)
    return k / max(n - 1, 1)


def _keys(v, u, e):
    if not isinstance(v, (list, tuple)):
        return float(v)
    if len(v) == 1:
        return float(v[0])
    u = min(max(u, 0.0), 1.0)
    pos = u * (len(v) - 1)
    i = min(int(pos), len(v) - 2)
    return float(v[i]) + (float(v[i + 1]) - float(v[i])) * ease(pos - i, e)


def cam_roll(fx, k, n, ctx):
    """roll / roll.camera - digital roll: angle=[a0, a1] deg (or a1; dir='cw' flips the sign, OpenCV + = ccw) over
    t=[t0,t1] or the segment, ease='inOutCubic'; scale='auto' (cover |cos|+aspect|sin|) | number | [keys];
    blur_shutter=0.5 (arc blur only above 6 deg/frame)."""
    u = _window_u(fx, k, n, ctx)
    e = fx.get('ease', 'inOutCubic')
    ang = fx.get('angle', [0, 180])
    if _num(ang):
        ang = [0.0, float(ang)]
    a = _keys(ang, u, e)
    if fx.get('dir') == 'cw':
        a = -a
    sc = fx.get('scale', 'auto')
    if sc == 'auto':
        asp = max(ctx['ow'], ctx['oh']) / min(ctx['ow'], ctx['oh'])
        r = math.radians(a)
        s = abs(math.cos(r)) + asp * abs(math.sin(r))
    else:
        s = _keys(sc, u, e)
    return (math.log(max(s, 1e-3)), a, 0.0, 0.0)


def cam_drift(fx, k, n, ctx):
    """drift - slow digital move: dx=[x0,x1] (fractions of width), dy=[y0,y1] (of height), zoom=[z0,z1],
    rot=[r0,r1] deg over t=[t0,t1] or the segment (ease='linear'); wobble={amp:0.004 (short side), rot:0.3,
    freq:1.0 Hz, seed} adds smooth handheld-like noise."""
    u = _window_u(fx, k, n, ctx)
    e = fx.get('ease', 'linear')
    dx = _keys(fx.get('dx', 0.0), u, e) * ctx['ow']
    dy = _keys(fx.get('dy', 0.0), u, e) * ctx['oh']
    z = _keys(fx.get('zoom', 1.0), u, e)
    rot = _keys(fx.get('rot', 0.0), u, e)
    wb = fx.get('wobble')
    if wb:
        fps = _fps(ctx)
        t = _abs_frame(ctx, k) / fps
        sd = _seed('wobble', wb.get('seed', 0))
        fr = float(wb.get('freq', 1.0))
        a = float(wb.get('amp', 0.004)) * _short(ctx)
        dx += a * _vnoise_t(sd + 1, t * fr)
        dy += a * _vnoise_t(sd + 2, t * fr)
        rot += float(wb.get('rot', 0.3)) * _vnoise_t(sd + 3, t * fr * 0.8)
    return (math.log(max(z, 1e-3)), rot, dx, dy)


_HANDHELD = {'calm': dict(amp=0.004, rot=0.4, freq=1.2, yfreq=1.2, cover=1.05),
             'walk': dict(amp=0.018, rot=1.2, freq=0.9, yfreq=2.0, cover=1.10),
             'chaos': dict(amp=0.02, rot=3.0, freq=2.5, yfreq=2.5, cover=1.15)}


def cam_handheld(fx, k, n, ctx):
    """handheld / destabilize - smooth handheld drift: profile='calm'|'walk'|'chaos' (handheld.shaky params: RMS
    amp of the short side, roll deg, freq Hz, vertical freq), seed; cover applied by camera()."""
    P = dict(_HANDHELD.get(fx.get('profile', 'calm'), _HANDHELD['calm']))
    for key in ('amp', 'rot', 'freq', 'yfreq'):
        if key in fx:
            P[key] = float(fx[key])
    fps = _fps(ctx)
    t = _abs_frame(ctx, k) / fps
    sd = _seed('handheld', fx.get('seed', 0))
    a = P['amp'] * _short(ctx)
    dx = a * (0.7 * _vnoise_t(sd + 1, t * P['freq']) + 0.3 * _vnoise_t(sd + 4, t * P['freq'] * 2.3))
    dy = a * (0.7 * _vnoise_t(sd + 2, t * P['yfreq']) + 0.3 * _vnoise_t(sd + 5, t * P['yfreq'] * 2.1))
    rot = P['rot'] * _vnoise_t(sd + 3, t * P['freq'] * 0.7)
    return (0.0, rot, dx, dy)


cam_zoom_punch.blur_thr = dict(dlnz=0.02)
cam_zoom_crash.blur_thr = dict(dlnz=0.02)
cam_zoom_in_out.blur_thr = dict(dlnz=0.02)
cam_shake.blur_thr = dict(dpx=1.0, drot=0.25)
cam_roll.blur_thr = dict(drot=6.0)
cam_drift.blur_thr = dict(dpx=6.0, drot=3.0, dlnz=0.03)
cam_handheld.blur_thr = dict(dpx=0.02 * 1080, drot=3.0)
for _fn in (cam_zoom_punch, cam_zoom_crash, cam_shake, cam_roll):
    _fn.default_shutter = 0.5
cam_zoom_in_out.default_shutter = None
cam_drift.default_shutter = 0.0
cam_handheld.default_shutter = 0.5

CAMERA_FX = {'zoom.punch': cam_zoom_punch, 'shake.beat': cam_shake, 'zoom.crash': cam_zoom_crash,
             'zoom.in_out': cam_zoom_in_out, 'roll': cam_roll, 'drift': cam_drift, 'handheld': cam_handheld}
_CAM_ALIAS = {'beat_punch': 'zoom.punch', 'punch': 'zoom.punch', 'beat_shake': 'shake.beat', 'shake_beat': 'shake.beat',
              'crash': 'zoom.crash', 'crash_zoom': 'zoom.crash', 'in_out': 'zoom.in_out', 'beat_pulse': 'zoom.in_out',
              'yoyo': 'zoom.in_out', 'roll.camera': 'roll', 'handheld.shaky': 'handheld', 'destabilize': 'handheld'}


def _moved(s0, s1, thr, ow, oh):
    dl = abs(s1[0] - s0[0])
    dr = abs(s1[1] - s0[1])
    dp = math.hypot(s1[2] - s0[2], s1[3] - s0[3])
    half = 0.5 * math.hypot(ow, oh)
    if 'dlnz' in thr and dl >= thr['dlnz']:
        return True
    if 'drot' in thr and dr >= thr['drot']:
        return True
    if 'dpx' in thr and dp >= thr['dpx'] * min(ow, oh) / 1080.0:
        return True
    return 'dlnz' not in thr and 'drot' not in thr and 'dpx' not in thr and (dl * half + dp > 1.0)


def _compose(states):
    """Compose (lnz, rot, dx, dy) similarity steps in list order (first = innermost)."""
    L = th = 0.0
    d = np.zeros(2)
    for lnz, rot, dx, dy in states:
        s = math.exp(lnz)
        a = math.radians(rot)
        Rm = np.array([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]])
        d = np.array([dx, dy]) + s * (Rm @ d)
        L += lnz
        th += rot
    return L, th, d


def cam_matrix(cam, ow, oh):
    """2x3 output-space affine of a camera() result (maps the unmoved frame to the camera frame)."""
    return _sim_matrix(cam.get('zoom', 1.0), cam.get('rot', 0.0), ow / 2.0, oh / 2.0, cam.get('dx', 0.0),
                       cam.get('dy', 0.0))


def _blur_spec(st0, st1, shutter, ctx):
    ow, oh = ctx['ow'], ctx['oh']
    u = 1.0 - shutter

    def interp(v):
        return dict(zoom=math.exp(math.log(st0['zoom']) * (1 - v) + math.log(st1['zoom']) * v),
                    rot=st0['rot'] * (1 - v) + st1['rot'] * v, dx=st0['dx'] * (1 - v) + st1['dx'] * v,
                    dy=st0['dy'] * (1 - v) + st1['dy'] * v)
    sa = interp(u)
    M1 = np.vstack([cam_matrix(st1, ow, oh), [0, 0, 1]])
    Ma = np.vstack([cam_matrix(sa, ow, oh), [0, 0, 1]])
    G = (Ma @ np.linalg.inv(M1))[:2]
    corners = np.array([[0, 0], [ow, 0], [0, oh], [ow, oh], [ow / 2, oh / 2]], float)
    moved = corners @ G[:, :2].T + G[:, 2]
    trail = float(np.max(np.linalg.norm(moved - corners, axis=1)))
    if trail < 1.0:
        return None
    nn = 4 if trail < 12 else (8 if trail < 40 else 16)
    samples = [interp(v) for v in np.linspace(u, 1.0, nn)]
    return dict(kind='camera', shutter=float(shutter), n=nn, trail_px=round(trail, 2), **{'from': sa},
                samples=samples)


def camera(fx_list, k, n, ctx):
    """Camera fx of a segment at frame k -> dict(zoom, dx, dy, rot, blur). See module docstring for units."""
    out = dict(zoom=1.0, dx=0.0, dy=0.0, rot=0.0, blur=None)
    cams = [fx for fx in (fx_list or []) if _canon(fx.get('type')) in CAMERA_FX]
    if not cams:
        return out
    cover = 1.0
    cur, prev = [], []
    shutter = 0.0
    for fx in cams:
        fn = CAMERA_FX[_canon(fx['type'])]
        if fn in (cam_shake, cam_handheld):
            cover *= shake_cover(fx, ctx) if fn is cam_shake else float(
                fx.get('cover', _HANDHELD.get(fx.get('profile', 'calm'), _HANDHELD['calm'])['cover']))
        sts = []
        for kk in (k, k - 1):
            if not active(fx, kk, n, ctx):
                sts.append(ZERO)
                continue
            lnz, rot, dx, dy = fn(fx, kk, n, ctx)
            a = amount(fx, kk, n, ctx)
            sts.append((lnz * a, rot * a, dx * a, dy * a))
        cur.append(sts[0])
        prev.append(sts[1])
        sh = fx.get('blur_shutter', getattr(fn, 'default_shutter', 0.0))
        if sh is None:
            sh = 0.5 if (fn is cam_zoom_in_out and float(fx.get('stroke') or ((beat_period(ctx) or 0.5) / 2)) < 0.35) \
                else 0.0
        if float(sh) > 0 and _moved(sts[1], sts[0], fn.blur_thr, ctx['ow'], ctx['oh']):
            shutter = max(shutter, min(float(sh), 1.0))
    L1, th1, d1 = _compose(cur)
    out.update(zoom=cover * math.exp(L1), dx=float(d1[0]), dy=float(d1[1]), rot=float(th1))
    if shutter > 0:
        L0, th0, d0 = _compose(prev)
        st0 = dict(zoom=cover * math.exp(L0), dx=float(d0[0]), dy=float(d0[1]), rot=float(th0))
        out['blur'] = _blur_spec(st0, out, shutter, ctx)
    return out


def camera_blur(x, cam, ctx, n=None):
    """Approximate camera motion blur on an already rendered frame (path_blur towards cam['blur']['from'])."""
    b = cam.get('blur') if cam else None
    if not b:
        return x
    ow, oh = x.shape[1], x.shape[0]
    M1 = np.vstack([cam_matrix(cam, ow, oh), [0, 0, 1]])
    Ma = np.vstack([cam_matrix(b['from'], ow, oh), [0, 0, 1]])
    G = (Ma @ np.linalg.inv(M1))[:2]
    return path_blur(x, G, n or b.get('n', 8))


def apply_camera(x, cam, ctx, border='reflect', blur=True):
    """Post-warp fallback: apply a camera() result to a rendered frame (+ camera_blur)."""
    if not cam:
        return x
    h, w = x.shape[:2]
    if abs(cam.get('zoom', 1) - 1) > 1e-6 or abs(cam.get('rot', 0)) > 1e-6 or cam.get('dx') or cam.get('dy'):
        x = _warp(x, cam_matrix(cam, w, h), border=border)
    return camera_blur(x, cam, ctx) if blur else x


# ============================================================================= time.velocity helpers
def velocity_times(beats, fps, n, seg_f0=0, src_t0=0.0, anchors=None, rate_mean=2.5, influence=0.85,
                   curve='inOutCubic', bias=0.0, grid='1/4', rate_min=0.2, rate_max=8.0, cap_uniform=True):
    """time.velocity speed curve -> per-frame source times for a segment of n frames starting at output frame
    seg_f0. s(t) = a_i + r_i*T*[(1-m)u + m E(u)], u = (t - b_i)/T (bias: u -> u^(1+bias)); b_i = beat frames
    floor(t*fps+0.4)/fps on the grid ('1/4' | '1/2' | '1/8'); anchors a_i = source times shown on the beats
    (action peaks; one per cycle boundary of the returned 'beats' = last beat <= segment start .. first beat >= its
    end; see velocity_anchors) or 'uniform'/None from src_t0 with rate_mean (influence capped 0.7 unless
    cap_uniform=False). Returns dict(times (source s per frame -> segment 'times'), rate (frame k->k+1, source s per
    output s), speed_curve [[k, rate]], cycles, anchors, beats)."""
    b = np.asarray(sorted(beats), float)
    if grid == '1/2':
        b = b[::2]
    elif grid == '1/8' and len(b) > 1:
        b = np.sort(np.concatenate([b, (b[:-1] + b[1:]) / 2]))
    bf = np.array([snap(t, fps) for t in b], float) / fps
    t_seg0, t_seg1 = seg_f0 / fps, (seg_f0 + n) / fps
    if len(bf) < 2:
        times = [src_t0 + rate_mean * (k / fps) for k in range(n)]
        return dict(times=times, rate=[rate_mean] * n, speed_curve=[[0, rate_mean], [n - 1, rate_mean]],
                    cycles=[], anchors=[])
    period = float(np.median(np.diff(bf)))
    ext = list(bf)
    while ext[0] > t_seg0 - 1e-9:
        ext.insert(0, ext[0] - period)
    while ext[-1] < t_seg1 + 1e-9:
        ext.append(ext[-1] + period)
    lo = int(np.searchsorted(ext, t_seg0 + 1e-9, side='right')) - 1
    hi = int(np.searchsorted(ext, t_seg1 - 1e-9, side='left'))
    bb = np.array(ext[lo:hi + 1])
    if anchors is None or (isinstance(anchors, str) and anchors == 'uniform'):
        m = min(influence, 0.7) if cap_uniform else influence
        aa = rate_mean * (bb - bb[0])
        anchors = None
    else:
        m = influence
        aa = np.asarray(anchors, float)[:len(bb)]
        if len(aa) < len(bb):
            last_r = (aa[-1] - aa[-2]) / max(bb[len(aa) - 1] - bb[len(aa) - 2], 1e-6) if len(aa) > 1 else rate_mean
            extra = [aa[-1] + last_r * (bb[j] - bb[len(aa) - 1]) for j in range(len(aa), len(bb))]
            aa = np.concatenate([aa, extra])

    def E(u):
        return ease(u, curve)

    times, cyc = [], []
    for kk in range(n + 1):
        t = (seg_f0 + kk) / fps
        i = int(np.clip(np.searchsorted(bb, t + 1e-9, side='right') - 1, 0, len(bb) - 2))
        T = bb[i + 1] - bb[i]
        u = (t - bb[i]) / T
        if bias:
            u = min(max(u, 0.0), 1.0) ** (1 + bias)
        r = (aa[i + 1] - aa[i]) / T
        r = min(max(r, rate_min), rate_max) if anchors is None else r
        times.append(aa[i] + r * T * ((1 - m) * u + m * E(u)))
        cyc.append(i)
    if anchors is None:
        off = src_t0 - times[0]
        times = [v + off for v in times]
    rate = [(times[kk + 1] - times[kk]) * fps for kk in range(n)]
    return dict(times=[round(v, 6) for v in times[:n]], rate=[round(v, 4) for v in rate],
                speed_curve=[[kk, round(rate[kk], 4)] for kk in range(n)], cycles=cyc[:n],
                anchors=[round(float(v) + (off if anchors is None else 0.0), 4) for v in aa],
                beats=[round(float(v), 4) for v in bb])


def speed_curve(times, fps):
    """Per-frame source times -> TIMELINE speed_curve [[k, rate], ...] (segment-relative k, linear between)."""
    t = np.asarray(times, float)
    if len(t) < 2:
        return [[0, 1.0]]
    r = np.diff(t) * fps
    r = np.append(r, r[-1])
    return [[k, round(float(v), 4)] for k, v in enumerate(r)]


def shutter_spec(times, fps_out, fps_src, shutter=0.5, min_rate=1.2):
    """time.velocity params.motion_blur: per frame None (rate < min_rate) or dict(n, span, offsets) - average n
    sub-frames over r*shutter source frames centred on s(k): n = clamp(ceil(2 r shutter fps_src/fps_out), 2, 12),
    span in source seconds, offsets relative to s(k)."""
    t = np.asarray(times, float)
    out = []
    for kk in range(len(t)):
        if kk + 1 < len(t):
            r = (t[kk + 1] - t[kk]) * fps_out
        else:
            r = (t[kk] - t[kk - 1]) * fps_out if kk else 1.0
        if abs(r) < min_rate or shutter <= 0:
            out.append(None)
            continue
        nn = int(min(max(math.ceil(2 * abs(r) * shutter * fps_src / fps_out), 2), 12))
        span = abs(r) * shutter / fps_out
        offs = list(np.linspace(-span / 2, span / 2, nn))
        out.append(dict(n=nn, span=round(span, 6), offsets=[round(float(o), 6) for o in offs]))
    return out


def ramp_curve(keys, n, ease_kind='inOutCubic'):
    """Dense TIMELINE speed_curve from rate keys [[k, rate], ...] or [[k, rate, ease], ...] (ease of the move INTO
    that key; default ease_kind): one [k, rate] per output frame 0..n-1, eased between keys, flat outside. The
    renderer interpolates speed_curve linearly, so dense keys keep the easing exact."""
    ks = sorted([float(q[0]), float(q[1]), (q[2] if len(q) > 2 else ease_kind)] for q in keys)
    out = []
    for k in range(int(n)):
        if k <= ks[0][0]:
            r = ks[0][1]
        elif k >= ks[-1][0]:
            r = ks[-1][1]
        else:
            i = max(j for j in range(len(ks)) if ks[j][0] <= k)
            a, b = ks[i], ks[i + 1]
            u = (k - a[0]) / max(b[0] - a[0], 1e-9)
            # ease in log-rate: a brake from x2.4 to x0.3 decelerates evenly instead of collapsing in one frame
            la, lb = math.log(max(a[1], 1e-3)), math.log(max(b[1], 1e-3))
            r = math.exp(la + (lb - la) * ease(u, b[2]))
        out.append([k, round(r, 4)])
    return out


def source_span(curve, n, fps):
    """Source seconds consumed by a segment of n output frames with a TIMELINE speed_curve (trapezoid sum of the
    linear-between-keys rate, like the renderer)."""
    pts = sorted((float(p[0]), float(p[1])) for p in curve)
    ks = np.arange(int(n), dtype=float)
    r = np.interp(ks, [p[0] for p in pts], [p[1] for p in pts])
    return float(np.trapezoid(r, ks) / fps) if hasattr(np, 'trapezoid') else float(np.trapz(r, ks) / fps)


def speed_ramp(n, fps, fast=2.5, slow=0.3, brake_at=None, brake=None, exit_at=None, exit_frames=None,
               fast_out=None, ease_down='inOutCubic', ease_up='inCubic', src_fps=None, shutter=0.75, min_rate=1.3):
    """time.speed_ramp (card params) for a segment of n output frames -> dict(speed_curve, fx, interp, src_span,
    keys, notes): fast -> brake over `brake` frames (0.12-0.32 s, default 0.2 s, inOutCubic in log rate) reaching
    `slow` exactly on output frame brake_at (the action peak / downbeat; default 30 % into the segment) -> slow hold ->
    speed-up from exit_at over exit_frames (0.12-0.24 s, inCubic) to fast_out (default fast; exit_at None = no exit).
    fx = [time.motion_blur] (frame-blend trails on frames with rate >= min_rate, shutter 0.75 = trails over 3/4 of a
    frame interval; the renderer's segment 'shutter' only blurs crop / camera motion, not the content); interp 'flow'
    (deep slow motion needs flow interpolation; notes warn when the source is too slow for the requested rate)."""
    n = int(n)
    fps = float(fps)
    bf = max(2, int(round((0.2 if brake is None else float(brake)) * fps)))
    k_slow = int(round(0.3 * (n - 1))) if brake_at is None else int(brake_at)
    k_slow = min(max(k_slow, 0), n - 1)
    keys = []
    if fast and k_slow > 0:
        keys.append([0, float(fast)])
        keys.append([max(0, k_slow - bf), float(fast)])
    keys.append([k_slow, float(slow), ease_down])
    fo = float(fast_out if fast_out is not None else (fast or 2.5))
    if exit_at is not None and int(exit_at) < n - 1:
        ef = max(2, int(round(0.18 * fps))) if exit_frames is None else max(1, int(exit_frames))
        ka = max(int(exit_at), k_slow + 1)
        keys.append([ka, float(slow)])
        keys.append([min(n - 1, ka + ef), fo, ease_up])
    curve = ramp_curve(keys, n)
    notes = []
    if src_fps:
        step = float(slow) * float(src_fps) / fps
        if step < 0.35:
            notes.append(f'slow {slow} on a {src_fps:g} fps source = {step:.2f} source frames per output frame: '
                         f'flow interpolation needed and may smear; an HFR source or slow >= '
                         f'{0.4 * fps / float(src_fps):.2f} is cleaner')
    fx = [dict(type='time.motion_blur', mode='frames', shutter=float(shutter), min_rate=float(min_rate))]
    return dict(speed_curve=curve, fx=fx, interp='flow', src_span=round(source_span(curve, n, fps), 4),
                keys=keys, notes=notes)


def action_peaks(frames, fps, min_gap=0.25, width=160):
    """Action peaks of a clip (time.velocity anchors): times (s from the first frame) where the median DIS flow
    drops right after a maximum (stop / contact) - or the max acceleration when it does not drop."""
    if len(frames) < 4:
        return []
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_ULTRAFAST)
    prev = None
    mag = []
    for fr in frames:
        g = fr if fr.ndim == 2 else cv2.cvtColor(np.asarray(fr, np.uint8), cv2.COLOR_RGB2GRAY)
        h, w = g.shape
        g = cv2.resize(g, (width, max(8, int(round(h * width / w)))), interpolation=cv2.INTER_AREA)
        if prev is not None:
            fl = dis.calc(prev, g, None)
            mag.append(float(np.median(np.hypot(fl[..., 0], fl[..., 1]))))
        prev = g
    m = np.convolve(np.asarray(mag), [0.25, 0.5, 0.25], mode='same')
    acc = np.gradient(m)
    peaks = []
    gap = max(1, int(round(min_gap * fps)))
    i = 1
    while i < len(m) - 1:
        if m[i] >= m[i - 1] and m[i] > m[i + 1] and m[i] > np.median(m) * 1.1:
            j = i + 1
            while j < len(m) - 1 and m[j + 1] < m[j] and j - i < int(0.5 * fps):
                j += 1
            lo_ = max(0, i - gap)
            cand = j + 1 if m[j] < 0.6 * m[i] else int(np.argmax(np.abs(acc[lo_:i + 1]))) + lo_ + 1
            if not peaks or cand - peaks[-1] >= gap:
                peaks.append(cand)
            i = j + 1
        else:
            i += 1
    return [round(p / fps, 4) for p in peaks]


def velocity_anchors(peaks, beats, a0=None, rate_lo=1.5, rate_hi=4.0, rate_mean=2.5):
    """Dynamic programming: one anchor per beat from the action peaks (or a virtual uniform anchor) so that each
    cycle's mean rate stays in [rate_lo, rate_hi], maximising the number of real peaks and staying near rate_mean."""
    peaks = sorted(float(p) for p in peaks)
    b = list(beats)
    if len(b) < 2:
        return [a0 if a0 is not None else (peaks[0] if peaks else 0.0)]
    INF = 1e18
    cands = [list(peaks) for _ in b]
    start = [a0] if a0 is not None else (peaks[:8] if peaks else [0.0])
    cands[0] = start
    cost = [dict() for _ in b]
    back = [dict() for _ in b]
    for a in cands[0]:
        cost[0][a] = 0.0 if (a in peaks or a0 is not None) else 1.0
    for i in range(1, len(b)):
        T = b[i] - b[i - 1]
        for a_prev, c_prev in cost[i - 1].items():
            opts = [(a, 0.0) for a in cands[i] if rate_lo <= (a - a_prev) / T <= rate_hi]
            opts.append((a_prev + rate_mean * T, 1.0))
            for a, pen in opts:
                c = c_prev + pen + 0.05 * abs((a - a_prev) / T - rate_mean)
                if c < cost[i].get(a, INF):
                    cost[i][a] = c
                    back[i][a] = a_prev
    a = min(cost[-1], key=cost[-1].get)
    out = [a]
    for i in range(len(b) - 1, 0, -1):
        a = back[i][a]
        out.append(a)
    return out[::-1]


# ============================================================================= image fx
def fx_rgb_split(x, fx, k, n, ctx):
    """rgb_split (fx.rgb_split) - R and B shifted apart around G, no wrap-around (BORDER_REFLECT101, subpixel).
    px=8 (each outer channel @1080 short side; R-B distance = 2 px) | [keys]; angle=0 deg; mode='linear' (R -px,
    B +px) | 'anaglyph' (R -px/2, G+B +px/2) | 'radial' (k=0.008: R scale 1+k, B 1-k about center) | 'motion'
    (angle and px from ctx cam_vel or fx vel=(vx,vy) px/frame: 0.5 px per 1 %/frame, cap 24) | 'temporal' (delay=1:
    R from t, G t-d, B t-2d; sequential) | 'jitter' (random angle, px*0.5-1 per frame); times + env={attack:0,
    hold:1, tau:2 (frames @25), decay:'exp'|'step'} pulses; alternate_sign; mix=1.0; soften=0 (px);
    overscan=1.0|'auto' (x(1+2px/W) above 16 px); seed."""
    mode = fx.get('mode', 'linear')
    env, ev = pulse(fx, k, ctx, attack=0, hold=1, tau=2.0, cutoff=0.04)
    a = amount(fx, k, n, ctx) * env
    if a <= 0:
        return x
    h, w = x.shape[:2]
    u = _u(ctx)
    f = _abs_frame(ctx, k)
    if mode == 'temporal':
        return _rgb_temporal(x, fx, k, ctx, a)
    if mode == 'radial':
        kk = anim(fx.get('k', 0.008), fx, k, n, ctx) * a
        cx, cy = _center(fx, ctx)
        chs = [np.ascontiguousarray(x[..., c]) for c in range(3)]
        for c, s in ((0, 1 + kk), (2, 1 - kk)):
            chs[c] = cv2.warpAffine(chs[c], cv2.getRotationMatrix2D((cx * w, cy * h), 0, s), (w, h),
                                    flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
        return cv2.merge(chs)
    px = anim(fx.get('px', 8.0), fx, k, n, ctx)
    ang = float(fx.get('angle', 0.0))
    if mode == 'motion':
        v = fx.get('vel') or ctx.get('cam_vel') or (0.0, 0.0)
        sp = math.hypot(v[0], v[1]) / w * 100.0
        px = min(0.5 * sp, 24.0)
        ang = math.degrees(math.atan2(v[1], v[0]))
    if mode == 'jitter':
        r = _rng(fx.get('seed', 0), 'rgbj', f)
        ang = float(r.uniform(0, 360))
        px *= float(r.uniform(0.5, 1.0))
    px = px * u * a
    if ev is not None and fx.get('alternate_sign') and ev[3] % 2:
        px = -px
    if abs(px) < 0.25:
        return x
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    shifts = (-0.5, 0.5, 0.5) if mode == 'anaglyph' else (-1.0, 0.0, 1.0)
    ov = fx.get('overscan', 1.0)
    ov = (1 + 2 * abs(px) / w) if (ov == 'auto' and abs(px) > 16 * u) else (float(ov) if _num(ov) else 1.0)
    mix = float(fx.get('mix', 1.0))
    soft = float(fx.get('soften', 0.0)) * u
    out = []

    def shifted(ch, m):
        M = np.float32([[ov, 0, (1 - ov) * w / 2 + m * px * ca], [0, ov, (1 - ov) * h / 2 + m * px * sa]])
        return cv2.warpAffine(ch, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    for c in range(3):
        ch = np.ascontiguousarray(x[..., c])
        m = shifts[c]
        if m == 0:
            out.append(ch if ov == 1.0 else shifted(ch, 0.0))
            continue
        y = shifted(ch, m)
        if soft > 0.2:
            y = cv2.GaussianBlur(y, (0, 0), soft)
        if mix < 1.0:
            y = cv2.addWeighted(ch if ov == 1.0 else shifted(ch, 0.0), 1 - mix, y, mix, 0)
        out.append(y)
    return cv2.merge(out)


def _rgb_temporal(x, fx, k, ctx, a):
    d = max(1, int(fx.get('delay', 1)))
    f = _abs_frame(ctx, k)
    st = _state(('rgbt', ctx.get('seg_f0'), _fxkey(fx)))
    st[f] = x.copy()
    for old in [q for q in st if isinstance(q, int) and q < f - 2 * d]:
        del st[old]
    g = st.get(f - d, x)
    b = st.get(f - 2 * d, x)
    out = cv2.merge([np.ascontiguousarray(x[..., 0]), np.ascontiguousarray(g[..., 1]),
                     np.ascontiguousarray(b[..., 2])])
    return _lerp(x, out, a) if a < 1 else out


# ----------------------------------------------------------------------------- glow
def _smoothstep(e0, e1, v):
    t = np.clip((v - e0) / max(e1 - e0, 1e-6), 0, 1)
    return t * t * (3 - 2 * t)


def _glow_key(xs, key):
    if key == 'luma':
        return _luma(xs)
    mx = xs.max(axis=2)
    if key == 'value':
        return mx
    mn = xs.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1e-4)
    return mx * (0.5 + 0.5 * sat)


def _pyr_sum(img, sigmas_lvl, weights):
    """Weighted sum of Gaussian blurs (sigma in px of img) computed on a pyramid (sigma per level 2.5-5 px)."""
    h, w = img.shape[:2]
    levels = {1: img}

    def lvl(fct):
        if fct not in levels:
            pr = lvl(fct // 2)
            levels[fct] = cv2.resize(pr, (max(1, pr.shape[1] // 2), max(1, pr.shape[0] // 2)),
                                     interpolation=cv2.INTER_AREA)
        return levels[fct]
    by = {}
    for sg, wt in zip(sigmas_lvl, weights):
        if wt == 0:
            continue
        fct = 1
        while sg / (fct * 2) >= 2.5 and fct < 32:
            fct *= 2
        by.setdefault(fct, []).append((max(sg / fct, 0.3), float(wt)))
    acc = None
    for fct in sorted(by, reverse=True):          # coarse -> fine collapse: one upsample per used level
        src = lvl(fct)
        if acc is not None:
            acc = cv2.resize(acc, (src.shape[1], src.shape[0]), interpolation=cv2.INTER_LINEAR)
        for sgl, wt in by[fct]:
            b = cv2.GaussianBlur(src, (0, 0), sgl)
            acc = b * F32(wt) if acc is None else cv2.scaleAdd(b, wt, acc)
    if acc is None:
        return np.zeros_like(img)
    if acc.shape[:2] != (h, w):
        acc = cv2.resize(acc, (w, h), interpolation=cv2.INTER_LINEAR)
    return acc


def _soft_clip(v, kk=0.9):
    """min(v, k) + (1-k)(1 - exp(-(v-k)/(1-k))) above k (soft shoulder, never reaches 1); 5 passes, reuses v."""
    v = _f32(v)
    c = -1.0 / (1.0 - kk)
    o = cv2.addWeighted(v, c, v, 0.0, -kk * c)
    np.minimum(o, 0, out=o)
    cv2.exp(o, o)
    np.minimum(v, kk, out=v)
    return cv2.addWeighted(o, -(1.0 - kk), v, 1.0, 1.0 - kk)


def _shot_percentile(x, fx, ctx, pct):
    st = _state(('thr', ctx.get('seg_f0'), _fxkey(fx)))
    if 'v' not in st:
        st['v'] = float(np.percentile(_luma(_down(x, 4)), pct))
    return st['v']


def fx_glow(x, fx, k, n, ctx):
    """glow (fx.glow) - highlights bloom in their own colour, blacks stay black. threshold=0.72 | 'p95' (per-shot
    percentile, cached) | [keys]; knee=0.1; key='luma'|'value'|'value_sat'; radii=[.004,.015,.04,.10] (short side)
    weights=[.35,.3,.2,.15]; strength=0.3 | [keys over t]; tint=None|'#ff3cac', tint_mix=0.6; sat=1.0;
    blend='screen'|'add' (linear light, soft shoulder above soft_clip=0.9); pulses: times + base=0.2, peak=1.0,
    radius_mul=1.6, env {attack 0, hold 0, tau 3 @25}; breathe={amp:0.3, period:2.0}; streak={threshold:0.9,
    length:0.1 (of W), thickness:0.002, tint:'#7fb2ff', strength:0.4} anamorphic lines. Linear light uses a gamma-2
    approximation; layers above 0.6 % S are blurred on a 1/2..1/32 pyramid."""
    S = _short(ctx)
    h, w = x.shape[:2]
    strength = anim(fx.get('strength', 0.3), fx, k, n, ctx)
    rmul = 1.0
    if fx.get('times') is not None:
        env, ev = pulse(fx, k, ctx, attack=0, hold=0, tau=3.0, cutoff=0.01)
        base, peak = float(fx.get('base', 0.2)), float(fx.get('peak', 1.0))
        strength = base + (peak - base) * env
        rmul = 1.0 + (float(fx.get('radius_mul', 1.6)) - 1.0) * env
    br = fx.get('breathe')
    if br:
        t = _abs_frame(ctx, k) / _fps(ctx)
        strength *= 1.0 + float(br.get('amp', 0.3)) * math.sin(2 * math.pi * t / float(br.get('period', 2.0)))
    strength *= amount(fx, k, n, ctx)
    thr = fx.get('threshold', 0.72)
    if isinstance(thr, str) and thr.startswith('p'):
        thr = _shot_percentile(x, fx, ctx, float(thr[1:] or 95))
    else:
        thr = anim(thr, fx, k, n, ctx)
    knee = float(fx.get('knee', 0.1))
    out = x
    if strength > 1e-3:
        xs = _down(x, 2)
        keyv = _glow_key(xs, fx.get('key', 'luma'))
        m = _smoothstep(thr - knee, thr + knee, keyv).astype(F32)
        lin = cv2.multiply(xs, xs)
        hi = cv2.multiply(lin, _gray3(m))
        sat = float(fx.get('sat', 1.0))
        if sat != 1.0:
            L = _luma(hi)
            hi = cv2.addWeighted(hi, sat, _gray3(L), 1 - sat, 0)
        if fx.get('tint'):
            tc = color(fx['tint'])
            tc = tc / max(float(tc @ np.array([0.2126, 0.7152, 0.0722], F32)), 1e-3)
            tm = float(fx.get('tint_mix', 0.6))
            L = _luma(hi)
            hi = cv2.addWeighted(hi, 1 - tm, cv2.multiply(_gray3(L), np.full(hi.shape, tc, F32)), tm, 0)
        radii = fx.get('radii', [0.004, 0.015, 0.04, 0.10])
        wts = fx.get('weights', [0.35, 0.3, 0.2, 0.15])
        g = _pyr_sum(hi, [r * S * rmul / 2.0 for r in radii], wts)
        g *= F32(strength)
        bl = fx.get('blend', 'screen')
        if bl != 'add':
            np.minimum(g, 1.0, out=g)
        out = _glow_blend(x, g, bl, float(fx.get('soft_clip', 0.9)))
    sk = fx.get('streak')
    if sk:
        out = _streak(out, sk, S, amount(fx, k, n, ctx))
    return out


def _glow_blend(x, g, blend, kk=0.9):
    """Blend a linear-light layer g (any resolution, upsampled here) onto sRGB-ish x (gamma-2 approximation):
    screen 1-(1-L)(1-g) or add with a soft shoulder above kk; for screen g must be <= 1."""
    x = _f32(x)
    h, w = x.shape[:2]
    lin = cv2.multiply(x, x)
    if blend == 'add':
        gu = g if g.shape[:2] == (h, w) else cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR)
        o = _soft_clip(cv2.add(lin, gu, dst=lin), kk)
    else:
        q = cv2.addWeighted(g, -1.0, g, 0.0, 1.0)
        qu = q if q.shape[:2] == (h, w) else cv2.resize(q, (w, h), interpolation=cv2.INTER_LINEAR)
        o = cv2.multiply(lin, qu, dst=lin)
        cv2.subtract(o, qu, dst=o)
        cv2.addWeighted(o, 1.0, o, 0.0, 1.0, dst=o)
    return cv2.sqrt(o)


def _streak(x, sk, S, a=1.0):
    h, w = x.shape[:2]
    fxs, fys = 16.0, 2.0
    xs = cv2.resize(x, (max(1, int(w / fxs)), max(1, int(h / fys))), interpolation=cv2.INTER_AREA)
    thr = float(sk.get('threshold', 0.9))
    m = _smoothstep(thr - 0.05, thr + 0.05, xs.max(axis=2)).astype(F32)
    hi = cv2.multiply(cv2.multiply(xs, xs), _gray3(m))
    sx = float(sk.get('length', 0.1)) * w / fxs
    sy = max(float(sk.get('thickness', 0.002)) * S / fys, 0.3)
    b = cv2.GaussianBlur(hi, (0, 0), sigmaX=sx, sigmaY=sy)
    L = _luma(b)
    tc = color(sk.get('tint', '#7fb2ff'))
    b = np.clip(L[..., None] * tc[None, None, :] * F32(float(sk.get('strength', 0.4)) * a * 6.0), 0, 1).astype(F32)
    return _glow_blend(x, b, 'screen')


def fx_bloom(x, fx, k, n, ctx):
    """bloom (legacy ed_edl) - thr=0.7, r=30 (px @1080 width, ow/1080 scaling as ed_edl), strength=0.6, added in
    gamma; computed on a pyramid (fast)."""
    a = amount(fx, k, n, ctx)
    thr = float(fx.get('thr', 0.7))
    r = float(fx.get('r', 30)) * ctx['ow'] / 1080.0
    h, w = x.shape[:2]
    xs = _down(x, 2)
    hi = np.clip(xs - thr, 0, None) / max(1 - thr, 1e-3)
    g = _pyr_sum(hi.astype(F32), [r / 2.0], [1.0])
    g = cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR)
    return _clip01(cv2.scaleAdd(g, float(fx.get('strength', 0.6)) * a, _f32(x)))


# ----------------------------------------------------------------------------- noise fields
def _vfield(h, w, cell, seed, octaves=1):
    """Smooth value-noise field (std ~1) of size h x w with cell size `cell` px; fbm over octaves."""
    acc = np.zeros((h, w), F32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = max(cell / (2 ** o), 2.0)
        gh, gw = int(math.ceil(h / c)) + 3, int(math.ceil(w / c)) + 3
        lat = _rng(seed, 'vf', o).standard_normal((gh, gw)).astype(F32)
        up = cv2.resize(lat, (int(gw * c), int(gh * c)), interpolation=cv2.INTER_CUBIC)
        acc += up[int(c):int(c) + h, int(c):int(c) + w] * F32(amp)
        tot += amp * amp
        amp *= 0.5
    return acc / F32(math.sqrt(tot))


def _field_at(field, ox, oy, h, w):
    """Crop h x w of a larger field at subpixel offset (ox, oy) (wrapping)."""
    fh, fw = field.shape
    ox %= (fw - w - 2)
    oy %= (fh - h - 2)
    M = np.float32([[1, 0, -ox], [0, 1, -oy]])
    return cv2.warpAffine(field, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)


# ----------------------------------------------------------------------------- light leak
_LEAK_PAL = {'amber': ['#fff1d0', '#ff6a10', '#ff2a0a'], 'magenta': ['#ffe6ea', '#ff4f7b', '#d81b60'],
             'gold': ['#fff6d8', '#ffc84a', '#f08c0a'], 'peach': ['#ffe8dc', '#ff9a8b', '#ff5e62'],
             'cool': ['#eefcff', '#6fd6ff', '#1a4dff']}
_ANCHORS = {'left': (0.0, 0.5), 'right': (1.0, 0.5), 'top': (0.5, 0.0), 'bottom': (0.5, 1.0), 'tl': (0.0, 0.0),
            'tr': (1.0, 0.0), 'bl': (0.0, 1.0), 'br': (1.0, 1.0), 'center': (0.5, 0.5)}


def _leak_env(fx, f, fps, seg=None):
    """Light-leak envelope 0..1 at absolute frame f (ambient window: fx t, else the segment span `seg`)."""
    mode = fx.get('mode', 'ambient')
    env = dict(fx.get('env') or {})
    if mode == 'ambient' and 'at' not in fx:
        t = fx.get('t') or seg or [0.0, 4.5]
        t0, t1 = float(t[0]), float(t[1])
        at_, rl = float(env.get('attack', 1.0)), float(env.get('release', 1.5))
        tt = f / fps
        if tt < t0 or tt > t1:
            return 0.0
        if tt < t0 + at_:
            return ease((tt - t0) / at_, 'inOutSine')
        if tt > t1 - rl:
            return ease((t1 - tt) / rl, 'inOutSine')
        return 1.0
    sc = fps / 25.0
    if mode == 'transition':
        att, hold, rel = env.get('attack', 8), env.get('hold', 3), env.get('release', 10)
    else:
        att, hold, rel = env.get('attack', 4), env.get('hold', 1), env.get('release', 10)
    att, hold, rel = max(1, round(att * sc)), max(1, round(hold * sc)), max(1, round(rel * sc))
    kc = snap(float(fx.get('at', 0.0)), fps)
    h0 = kc - hold // 2
    d = f - h0
    if d < -att or d >= hold + rel:
        return 0.0
    if d < 0:
        return ease((d + att + 1) / (att + 1), 'inQuad')
    if d < hold:
        return 1.0
    return 1.0 - ease((d - hold + 1) / (rel + 1), 'outQuad')


def _leak_layer(fx, envv, f, ctx, h, w):
    """Synthesise the leak layer (RGB 0..~1.5) at h x w (quarter resolution)."""
    fps = _fps(ctx)
    tt = f / fps
    S = float(min(h, w))
    seed = _seed('leak', fx.get('seed', 0))
    shape = fx.get('shape', 'burst' if fx.get('mode') == 'transition' else 'edge')
    anchor = fx.get('anchor', 'right' if shape == 'burst' else 'left')
    t0 = float((fx.get('t') or [fx.get('at', 0.0)])[0]) if (fx.get('t') or 'at' in fx) else 0.0
    dt = tt - t0
    ax, ay = _ANCHORS[anchor] if isinstance(anchor, str) else (float(anchor[0]), float(anchor[1]))
    drift = fx.get('drift', [0.04, 0.02])
    sgx = -1.0 if ax > 0.5 else 1.0
    sgy = -1.0 if ay > 0.5 else 1.0
    if shape in ('edge', 'corner', 'burst'):
        px = ax * w + sgx * drift[0] * w * dt * (0.3 if shape == 'edge' and anchor in ('left', 'right') else 1.0)
        py = ay * h + (drift[1] * h * dt if anchor in ('left', 'right') else sgy * drift[1] * h * dt)
    else:
        px = ax * w + drift[0] * w * dt
        py = ay * h + drift[1] * h * dt
    key = ('leakfield', seed, h, w)
    st = _state(key)
    if not st:
        wp = fx.get('warp') or {}
        cell = float(wp.get('scale', 0.45)) * S
        big_h, big_w = h * 2 + 8, w * 2 + 8
        st['wx'] = _vfield(big_h, big_w, cell, seed + 1, int(wp.get('octaves', 3)))
        st['wy'] = _vfield(big_h, big_w, cell, seed + 2, int(wp.get('octaves', 3)))
        st['gr'] = _vfield(big_h, big_w, 2.0, seed + 3, 1)
    wp = fx.get('warp') or {}
    amt = float(wp.get('amount', 0.1)) * S * (0.25 if shape == 'streak' else 1.0)   # a light band stays straight-ish
    spd = float(wp.get('speed', 0.04)) * w
    ox, oy = spd * tt + 3.0, 0.6 * spd * tt + 5.0
    wx = _field_at(st['wx'], ox, oy, h, w) * F32(amt)
    wy = _field_at(st['wy'], ox * 0.8 + 17, oy * 1.1 + 9, h, w) * F32(amt)
    gx, gy = _grid(h, w)
    X = gx + wx - F32(px)
    Y = gy + wy - F32(py)
    size = float(fx.get('size', 0.95 if shape == 'burst' else 0.32)) * S
    el = float(fx.get('elong', 1.8))
    if shape == 'burst':
        size = size * (0.15 + 0.85 * envv) * 1.6
    sd = None
    if shape in ('edge', 'burst') and isinstance(anchor, str) and anchor in ('left', 'right'):
        d = cv2.magnitude(X, Y / F32(el))
    elif shape in ('edge', 'burst') and isinstance(anchor, str) and anchor in ('top', 'bottom'):
        d = cv2.magnitude(X / F32(el), Y)
    elif shape == 'streak':          # band 15-35 % S wide, tilted `angle` deg from vertical, sweeping along its normal
        ang = math.radians(float(fx.get('angle', 30.0)))
        nx, ny = math.cos(ang), math.sin(ang)
        sp = float(fx.get('streak_speed', 0.5)) * w
        sd = X * F32(nx) + Y * F32(ny) - F32(sp * dt - 0.5 * w)
        d = np.abs(sd)
        size = float(fx.get('size', 0.25)) * S * 0.5
    else:
        d = cv2.magnitude(X, Y)
    fo = float(fx.get('falloff', 1.5))
    p = np.exp(-np.power(d / F32(size), F32(fo))).astype(F32)
    q = np.power(p, F32(0.7))
    pal = fx.get('palette', 'amber')
    if pal == 'prism':               # spectral 0-300 deg across the band (or across the spot), pale core
        across = sd if sd is not None else (X * F32(0.7071) + Y * F32(0.7071))
        hue = (np.clip(across / F32(2.2 * size) + 0.5, 0, 1) * 300.0).astype(F32)
        hsv = cv2.merge([hue, np.full_like(hue, 0.6), np.ones_like(hue)])
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        col = cv2.addWeighted(rgb, 0.8, _gray3(q), 0.35, 0)
    else:
        cs = palette(pal, _LEAK_PAL, 'amber') or palette('amber', _LEAK_PAL)
        while len(cs) < 3:
            cs.append(cs[-1])
        core, mid, edge = cs[0], cs[1], cs[2]
        q3 = q[..., None]
        lo = edge[None, None, :] + (mid - edge)[None, None, :] * np.clip(q3 * 2, 0, 1)
        hi = mid[None, None, :] + (core - mid)[None, None, :] * np.clip(q3 * 2 - 1, 0, 1)
        col = np.where(q3 < 0.5, lo, hi).astype(F32)
    fl = fx.get('flicker', {'amp': 0.08, 'hz': 1.5})
    flk = 1.0 + (float(fl.get('amp', 0.08)) * _vnoise_t(seed + 9, tt * float(fl.get('hz', 1.5))) if fl else 0.0)
    peak = float(fx.get('peak', 1.3 if fx.get('mode') == 'transition' else 0.9))
    gr = float(fx.get('grain', 0.03))
    tex = 1.0 + gr * _field_at(st['gr'], 13 * f, 7 * f, h, w)
    lay = col * (p * F32(peak * envv * flk) * tex)[..., None]
    return lay.astype(F32)


def _dither(x, f, amp=0.5 / 255):
    """+-0.5 LSB triangular dither before 8-bit output (cached per frame size; sign alternates per frame)."""
    h, w = x.shape[:2]
    key = ('dither', h, w)
    st = _state(key)
    if not st:
        r = _rng('dither')
        st['t'] = (r.random((h, w, 3), dtype=F32) - r.random((h, w, 3), dtype=F32)).astype(F32)
    return cv2.scaleAdd(st['t'], amp if f % 2 == 0 else -amp, _f32(x))


def _blend_layer(x, lay, blend, lay_small=None):
    """Overlay layer (display values, may exceed 1) onto x: screen (default) | add (linear light; the shoulder is
    the linear-light screen 1-(1-L)(1-l^2), soft by construction, white at layer >= 1) | lighten | soft_light (tints
    without lifting where the layer is 0). lay_small: the same layer before upsampling (cheaper squaring)."""
    x = _f32(x)
    if blend == 'add':
        src = lay_small if lay_small is not None else lay
        g = np.minimum(cv2.multiply(src, src), 1.0)
        return _glow_blend(x, g, 'screen')
    np.minimum(lay, 1.0, out=lay)
    if blend == 'lighten':
        return cv2.max(x, lay)
    if blend == 'soft_light':
        bl = 0.5 + 0.5 * lay
        return np.clip((1 - 2 * bl) * x * x + 2 * bl * x, 0, 1).astype(F32)
    xl = cv2.multiply(x, lay)
    return cv2.subtract(cv2.add(x, lay, dst=lay), xl)


def fx_light_leak(x, fx, k, n, ctx):
    """light_leak (fx.light_leak) - procedural warm film leak, independent of the picture. mode='ambient' (t=[t0,t1],
    env {attack 1.0, hold, release 1.5} s, inOutSine) | 'accent' (at=t, env frames @25 {attack 4, hold 1,
    release 10}) | 'transition' (at=cut, {8, 3, 10}, burst, add, peak 1.3); shape='edge'|'corner'|'blob'|'streak'|
    'burst'; anchor='left'|'right'|'top'|'bottom'|'tl'|'tr'|'bl'|'br'|[x,y]; palette='amber'|'magenta'|'gold'|
    'peach'|'cool'|'prism'|[hex,hex,hex] (core, mid, edge); peak=0.9; size=0.32 (short side); falloff=1.5;
    elong=1.8; drift=[0.04, 0.02] (W, H per s); warp={scale:.45, amount:.1, octaves:3, speed:.04};
    flicker={amp:.08, hz:1.5}; blend='screen'|'add'|'lighten'|'soft_light'; grain=0.03; dither=True; seed.
    Synthesised at 1/4 resolution, bicubic upscale."""
    f = _abs_frame(ctx, k)
    fps = _fps(ctx)
    f0 = (ctx.get('seg_f0') or 0)
    if not fx.get('t') and 'at' not in fx:
        fx = dict(fx, t=[f0 / fps, (f0 + n - 1) / fps])
    envv = _leak_env(fx, f, fps) * amount(fx, k, n, ctx)
    if envv <= 1e-3:
        return x
    h, w = x.shape[:2]
    hs, ws = max(8, h // 4), max(8, w // 4)
    lay_s = _leak_layer(fx, envv, f, ctx, hs, ws)
    bl = fx.get('blend', 'add' if fx.get('mode') == 'transition' else 'screen')
    lay = None if bl == 'add' else cv2.resize(lay_s, (w, h), interpolation=cv2.INTER_LINEAR)
    out = _blend_layer(_f32(x), lay, bl, lay_s)
    if fx.get('dither', True):
        out = _dither(out, f)
    return _clip01(out)


# ----------------------------------------------------------------------------- film overlay
_FILM_LEVELS = {
    1: dict(grain=2.5, size=1.5, flicker=0.007, weave=1.0, dust=0, hair=0.0, scratch=0, every=None),
    2: dict(grain=4.5, size=2.0, flicker=0.02, weave=3.0, dust=5, hair=0.25, scratch=1, every=(4, 8)),
    3: dict(grain=8.0, size=2.4, flicker=0.045, weave=8.0, dust=15, hair=1.5, scratch=2, every=(1, 3)),
}
_SOCIAL = {1: dict(grain=3.0, size=2.0), 2: dict(grain=5.5, size=2.2), 3: dict(grain=8.0, size=2.5)}


_GRAIN_FWHM = ([1.0, 1.008, 1.095, 1.353, 1.802, 2.359, 2.738, 3.056, 3.359, 4.004, 5.013, 6.676],
               [0.0, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5, 2.0])


def _grain_sigma_b(size_px):
    """cv2.GaussianBlur sigma giving white-noise grain an autocorrelation FWHM of size_px (measured table)."""
    return float(np.interp(size_px, *_GRAIN_FWHM))


def _grain_bank(sigma_b, corr, mono, n_tiles=8, size=512):
    key = ('grainbank', round(sigma_b, 3), round(corr, 2), mono)
    st = _state(key)
    if not st:
        rng = _rng('grain', key)
        tiles = []
        pad = 8
        for _ in range(n_tiles):
            def field():
                z = rng.standard_normal((size + 2 * pad, size + 2 * pad), dtype=F32)
                if sigma_b > 0.05:
                    z = cv2.GaussianBlur(z, (0, 0), sigma_b)
                z = z[pad:-pad, pad:-pad]
                return (z / max(float(z.std()), 1e-6)).astype(F32)
            L = field()
            if mono:
                tiles.append(np.ascontiguousarray(np.repeat(L[..., None], 3, axis=2)))
            else:
                cs = [corr * L + math.sqrt(max(1 - corr * corr, 0)) * field() for _ in range(3)]
                tiles.append(np.ascontiguousarray(np.stack(cs, axis=2).astype(F32)))
        st['tiles'] = tiles
    return st['tiles']


def _grain_frame(h, w, f, seed, sigma_b, corr, mono):
    tiles = _grain_bank(sigma_b, corr, mono)
    nt = len(tiles)
    r = _hash_u01(seed, np.arange(f * 8, f * 8 + 6))
    idx = int((f * 3 + int(r[0] * 3)) % nt)
    t = tiles[idx]
    if r[1] < 0.5:
        t = t[::-1]
    if r[2] < 0.5:
        t = t[:, ::-1]
    sz = t.shape[0]
    oy, ox = int(r[3] * sz), int(r[4] * sz)
    out = np.empty((h, w, 3), F32)
    yy = 0
    sy = oy
    while yy < h:
        hh = min(sz - sy, h - yy)
        xx, sx = 0, ox
        while xx < w:
            ww = min(sz - sx, w - xx)
            out[yy:yy + hh, xx:xx + ww] = t[sy:sy + hh, sx:sx + ww]
            xx += ww
            sx = 0
        yy += hh
        sy = 0
    return out


_GRAIN_W = np.interp(np.arange(256) / 255.0, [0.0, 0.3, 0.6, 0.9, 1.0], [0.6, 1.0, 1.0, 0.3, 0.3]).astype(F32)


def add_grain(x, sigma255, size_px, f, seed=0, corr=0.8, mono=False, response=True, gain=1.0):
    """Film grain: tile bank of blurred normalised noise (FWHM ~ size_px), new tile/offset/flip every frame,
    weighted by luma response (mids 1.0, shadows 0.6, highlights 0.3), added in gamma; x*gain first."""
    h, w = x.shape[:2]
    x = _f32(x)
    G = _grain_frame(h, w, f, _seed('grainf', seed), _grain_sigma_b(size_px), corr, mono)
    if response:
        Y = cv2.convertScaleAbs(_luma(x), alpha=255.0)
        wt = cv2.LUT(Y, (_GRAIN_W * F32(sigma255 / 255.0)).reshape(1, 256))
        cv2.multiply(G, _gray3(wt), dst=G)
    else:
        G *= F32(sigma255 / 255.0)
    out = cv2.scaleAdd(x, float(gain), G, dst=G) if gain != 1.0 else cv2.add(x, G, dst=G)
    return _clip01(out)


def _blot(img, cx, cy, r, val, alpha, rng, blur=0.5):
    h, w = img.shape[:2]
    R = int(math.ceil(r * 2 + 3))
    x0, y0, x1, y1 = int(cx) - R, int(cy) - R, int(cx) + R + 1, int(cy) + R + 1
    if x1 <= 0 or y1 <= 0 or x0 >= w or y0 >= h:
        return
    m = np.zeros((y1 - y0, x1 - x0), F32)
    for _ in range(int(rng.integers(1, 5))):
        ox, oy = rng.normal(0, r * 0.6, 2)
        rr = max(0.5, r * float(rng.uniform(0.4, 1.0)))
        cv2.circle(m, (int(round(cx - x0 + ox)), int(round(cy - y0 + oy))), int(round(rr)), 1.0, -1, cv2.LINE_AA)
    if blur > 0:
        m = cv2.GaussianBlur(m, (0, 0), blur)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
    mm = m[ya - y0:yb - y0, xa - x0:xb - x0, None] * F32(alpha)
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - mm) + F32(val) * mm


def _draw_dust(x, f, seed, per_frame, u, sticky=0.05):
    if per_frame <= 0:
        return
    h, w = x.shape[:2]
    rng = _rng(seed, 'dust', f)
    nd = int(rng.poisson(per_frame))
    specs = [(rng, nd)]
    for back in range(1, 6):
        r2 = _rng(seed, 'sticky', f - back)
        if r2.random() < sticky * per_frame and back < int(r2.integers(2, 7)):
            specs.append((r2, 1))
    for r_, cnt in specs:
        for _ in range(cnt):
            cx, cy = r_.uniform(0, w), r_.uniform(0, h)
            sz = float(r_.choice([1, 1, 2, 2, 3, 4, 6])) * u * 0.5
            dark = r_.random() < 0.75
            bg = float(x[int(min(cy, h - 1)), int(min(cx, w - 1))].mean())
            val = 0.06 if (dark and bg > 0.25) else 0.92
            _blot(x, cx, cy, max(sz, 0.5), val, float(r_.uniform(0.4, 0.9)), r_, blur=0.5 * max(u, 0.5))


def _draw_hair(x, f, fps, seed, per_s, u, S):
    if per_s <= 0:
        return
    h, w = x.shape[:2]
    for back in range(0, int(3 * fps) + 1):
        fs = f - back
        r = _rng(seed, 'hair', fs)
        if r.random() >= per_s / fps:
            continue
        edge = r.random() < 0.3
        life = int(r.integers(int(fps), int(3 * fps) + 1)) if edge else int(r.integers(1, 5))
        if back >= life:
            continue
        L = float(r.uniform(0.02, 0.08)) * S
        if edge:
            side = int(r.integers(0, 4))
            cx = [r.uniform(0, 0.04), r.uniform(0.96, 1.0), r.uniform(0, 1), r.uniform(0, 1)][side] * w
            cy = [r.uniform(0, 1), r.uniform(0, 1), r.uniform(0, 0.04), r.uniform(0.96, 1.0)][side] * h
        else:
            cx, cy = r.uniform(0, w), r.uniform(0, h)
        a0 = r.uniform(0, 2 * math.pi)
        bend = r.uniform(-2.5, 2.5, 2)
        ts = np.linspace(0, 1, 24)
        ang = a0 + bend[0] * ts + bend[1] * ts ** 2
        pts = np.cumsum(np.stack([np.cos(ang), np.sin(ang)], 1) * (L / 23), axis=0)
        pts = pts - pts.mean(0) + [cx, cy]
        x0, y0 = np.floor(pts.min(0)).astype(int) - 3
        x1, y1 = np.ceil(pts.max(0)).astype(int) + 4
        xa, ya, xb, yb = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
        if xb <= xa or yb <= ya:
            continue
        m = np.zeros((y1 - y0, x1 - x0), F32)
        cv2.polylines(m, [np.round((pts - [x0, y0]) * 4).astype(np.int32)], False, 1.0,
                      max(1, int(round(u))), cv2.LINE_AA, shift=2)
        mm = m[ya - y0:yb - y0, xa - x0:xb - x0, None] * F32(r.uniform(0.5, 0.9))
        val = 0.05 if float(x[ya:yb, xa:xb].mean()) > 0.25 else 0.9
        x[ya:yb, xa:xb] = x[ya:yb, xa:xb] * (1 - mm) + F32(val) * mm


def _draw_scratches(x, f, fps, seed, max_n, every, u):
    if not max_n or not every:
        return
    h, w = x.shape[:2]
    slot = float(sum(every)) / 2.0
    t = f / fps
    s_now = int(math.floor(t / slot))
    drawn = 0
    for s in range(s_now - 2, s_now + 1):
        for j in range(max_n):
            r = _rng(seed, 'scr', s, j)
            if j > 0 and r.random() < 0.5:
                continue
            ts = (s + r.random()) * slot
            life = float(r.uniform(0.3, 1.5))
            if not ts <= t < ts + life or drawn >= max_n:
                continue
            drawn += 1
            xx = r.uniform(0.05, 0.95) * w + float(r.uniform(-5, 5)) * u * (t - ts)
            rj = _rng(seed, 'scrj', s, j, f)
            xx += float(rj.uniform(-2, 2)) * u
            wd = float(r.uniform(1, 2)) * u
            y0 = r.uniform(0, 0.3) * h
            y1 = y0 + r.uniform(0.4, 1.0) * h
            xi = int(xx)
            xa, xb = max(0, xi - 4), min(w, xi + 5)
            if xb <= xa:
                continue
            col = np.zeros((h, xb - xa), F32)
            cv2.line(col, (int(round((xx - xa) * 4)), int(y0 * 4)), (int(round((xx - xa) * 4)), int(min(y1, h) * 4)),
                     1.0, max(1, int(round(wd))), cv2.LINE_AA, shift=2)
            gaps = _hash_u01(_seed(seed, s, j), np.arange(h // 16 + 1))
            col *= np.repeat((gaps > 0.12).astype(F32), 16)[:h, None]
            mm = col[..., None] * F32(r.uniform(0.4, 0.7))
            x[:, xa:xb] = x[:, xa:xb] * (1 - mm) + F32(r.uniform(0.85, 0.95)) * mm


def fx_film_overlay(x, fx, k, n, ctx):
    """film_overlay (fx.film_overlay) - procedural film texture, no colour change: level=1|2|3 presets (grain sigma
    2.5/4.5/8 levels, size 1.5/2.0/2.4 px @1080, dust 0/5/15 per frame, hair 0/.25/1.5 per s, scratches 0/1/2 with a
    new one every 4-8 / 1-3 s, flicker .007/.02/.045, gate weave swing 1/3/8 px); delivery='social' (default: grain size
    >= 2 px and sigma 3/5.5/8 so it survives platform re-encoding) | 'master'; overrides: grain=sigma, size, corr=0.8,
    mono, dust, hair, scratch, every=[a,b], flicker, weave (px @1080), weave_rot=0.05; seed (hashed with the absolute
    frame - repeatable)."""
    lvl = int(fx.get('level', 2))
    P = dict(_FILM_LEVELS.get(lvl, _FILM_LEVELS[2]))
    if fx.get('delivery', 'social') == 'social':
        P.update(_SOCIAL.get(lvl, {}))
    for key in ('grain', 'size', 'dust', 'hair', 'scratch', 'every', 'flicker', 'weave'):
        if key in fx:
            P[key] = fx[key]
    a = amount(fx, k, n, ctx)
    f = _abs_frame(ctx, k)
    fps = _fps(ctx)
    u = _u(ctx)
    S = _short(ctx)
    seed = _seed('film', fx.get('seed', 0))
    h, w = x.shape[:2]
    out = _f32(x)
    wv = 0.5 * float(P['weave']) * u * a          # card 'weave' = swing (peak) -> noise sigma ~ swing / 2
    if wv > 0.15:
        t = f / fps
        jx = 0.25 * _smooth_noise_f(seed + 11, f, 0.0)
        jy = 0.25 * _smooth_noise_f(seed + 12, f, 0.0)
        dx = wv * 0.55 * (_vnoise_t(seed + 1, t * 1.3) + jx)
        dy = wv * (_vnoise_t(seed + 2, t * 1.7) + jy)
        rot = float(fx.get('weave_rot', 0.05 * min(lvl, 2))) * _vnoise_t(seed + 3, t * 0.9) * a
        ov = 1.0 + 2.2 * wv / min(h, w)
        out = _warp(out, _sim_matrix(ov, rot, w / 2, h / 2, dx, dy))
    else:
        out = out.copy()
    _draw_dust(out, f, seed, float(P['dust']) * a, u)
    _draw_hair(out, f, fps, seed, float(P['hair']) * a, u, S)
    _draw_scratches(out, f, fps, seed, int(P['scratch']) if a > 0.3 else 0, P['every'], u)
    fl = float(P['flicker']) * a
    gain = 1.0 + fl * _smooth_noise_f(seed + 21, f, 0.5) if fl > 0 else 1.0
    if float(P['grain']) * a > 0.05:
        out = add_grain(out, float(P['grain']) * a, float(P['size']) * u, f, seed, float(fx.get('corr', 0.8)),
                        bool(fx.get('mono', False)), gain=gain)
    elif gain != 1.0:
        out = _clip01(out * F32(gain))
    return out


def fx_grain(x, fx, k, n, ctx):
    """grain (legacy ed_edl + engine grain(amount, size)) - sigma=0.035 (0..1 units, legacy) or sigma255; size=2.0
    px @1080; corr=0.8; mono; response=True. Uses the film grain tile bank (fast, hashed per frame)."""
    a = amount(fx, k, n, ctx)
    s255 = float(fx.get('sigma255', float(fx.get('sigma', 0.035)) * 255.0)) * a
    if s255 <= 0.05:
        return x
    return add_grain(x, s255, float(fx.get('size', 2.0)) * _u(ctx), _abs_frame(ctx, k), fx.get('seed', 0),
                     float(fx.get('corr', 0.8)), bool(fx.get('mono', False)), bool(fx.get('response', True)))


# ----------------------------------------------------------------------------- pixel sort
def _sort_key(img, key):
    if key == 'luma':
        return _luma(img)
    if key in ('r', 'g', 'b'):
        return np.ascontiguousarray(img[..., 'rgb'.index(key)])
    hsv = cv2.cvtColor(np.clip(img, 0, 1), cv2.COLOR_RGB2HSV)
    return (hsv[..., 0] / 360.0).astype(F32) if key == 'hue' else np.ascontiguousarray(hsv[..., 1])


def sort_columns(img, keyv, mask, desc=False, min_len=2, max_len=None):
    """Sort pixels of every vertical run of `mask` by keyv (ascending downwards unless desc); pixels outside the
    mask stay. One argsort over (run id, key) for the whole frame."""
    H, W = keyv.shape
    K = np.ascontiguousarray(keyv.T).ravel()
    M = np.ascontiguousarray(mask.T).ravel()
    idx = np.flatnonzero(M)
    if idx.size < 2:
        return img
    brk = np.empty(idx.size, bool)
    brk[0] = True
    brk[1:] = (np.diff(idx) != 1) | (idx[1:] % H == 0)
    seg = np.cumsum(brk) - 1
    if max_len:
        start = np.flatnonzero(brk)
        pos = np.arange(idx.size) - start[seg]
        brk2 = brk | ((pos % int(max_len)) == 0)
        seg = np.cumsum(brk2) - 1
    lens = np.bincount(seg)
    keep = lens[seg] >= min_len
    idx, seg = idx[keep], seg[keep]
    if idx.size < 2:
        return img
    kq = np.clip(K[idx], 0, 1)
    kq = (kq * 65535).astype(np.int64)
    if desc:
        kq = 65535 - kq
    comp = (seg.astype(np.int64) << 17) | kq
    order = np.argsort(comp, kind='stable')
    flat = np.ascontiguousarray(img.transpose(1, 0, 2)).reshape(-1, 3)
    out = flat.copy()
    out[idx] = flat[idx[order]]
    return np.ascontiguousarray(out.reshape(W, H, 3).transpose(1, 0, 2))


def _ps_lo(fx, k, ctx, lo):
    """Pulse keys for pixel_sort: keys={lo: [[0, .95], [.08, .6], [.48, .95]]} (s from each event), eases."""
    ev = events(fx, ctx, None)
    if not ev:
        return lo
    keys = (fx.get('keys') or {}).get('lo') or [[0, 0.95], [0.08, 0.6], [0.48, 0.95]]
    es = fx.get('pulse_ease') or ['outExpo', 'inQuad']
    f = _abs_frame(ctx, k)
    fps = _fps(ctx)
    best = keys[0][1]
    for t, k0, w, i in ev:
        dt = (f - k0) / fps
        if dt < 0 or dt > keys[-1][0] + 1e-6:
            continue
        for j in range(len(keys) - 1):
            if keys[j][0] <= dt <= keys[j + 1][0]:
                uu = (dt - keys[j][0]) / max(keys[j + 1][0] - keys[j][0], 1e-6)
                v = keys[j][1] + (keys[j + 1][1] - keys[j][1]) * ease(uu, es[min(j, len(es) - 1)])
                best = min(best, v)
    return best


def pixel_sort_frame(x, mask='bright', lo=0.62, hi=1.0, axis='y', direction='down', key='luma', angle=None,
                     min_len=0.01, max_len=0.6, random_len=(0.02, 0.25), share=0.45, jitter=0.04, work_res=540,
                     upscale='bicubic', seed=0, sweep=None, exclude_bars=True, edges=None):
    """Stateless pixel sort of one frame (see fx_pixel_sort)."""
    h, w = x.shape[:2]
    short = min(h, w)
    fct = 1.0 if (work_res in ('full', None) or short <= work_res) else short / float(work_res)
    xs = _down(x, fct) if fct > 1 else _f32(x)
    rot = None
    if angle:
        hs, ws = xs.shape[:2]
        D = int(math.ceil(math.hypot(hs, ws)))
        M = cv2.getRotationMatrix2D((ws / 2, hs / 2), -float(angle), 1.0)
        M[0, 2] += (D - ws) / 2
        M[1, 2] += (D - hs) / 2
        valid = cv2.warpAffine(np.ones((hs, ws), F32), M, (D, D), flags=cv2.INTER_NEAREST) > 0.5
        xs = cv2.warpAffine(xs, M, (D, D), flags=cv2.INTER_LINEAR)
        rot = (M, hs, ws)
    else:
        valid = None
    work = xs
    if axis == 'x':
        work = np.ascontiguousarray(xs.transpose(1, 0, 2))
        valid = valid.T if valid is not None else None
    hh, ww = work.shape[:2]
    kv = _sort_key(work, key)
    rng = _rng(seed, 'ps')
    if mask == 'full':
        m = np.ones((hh, ww), bool)
    elif mask == 'random':
        cut = rng.random((hh, ww)) < 1.0 / max(2.0, float(np.mean(random_len)) * hh)
        cut[0] = True
        sid = np.cumsum(cut, axis=0) + np.arange(ww)[None, :] * (hh + 1)
        m = _hash_u01(_seed(seed, 'psr'), sid) < share
    elif mask == 'edges':
        ed = edges or {}
        g8 = cv2.convertScaleAbs(cv2.GaussianBlur(kv, (0, 0), float(ed.get('blur', 1.5))), alpha=255)
        e = cv2.Canny(g8, int(ed.get('lo', 50)), int(ed.get('hi', 150))) > 0
        m = ~e
    else:
        jt = (rng.random(ww).astype(F32) - 0.5) * 2 * F32(jitter)
        if mask == 'dark':
            m = (kv >= 0.03) & (kv <= hi + jt[None, :])
        elif mask == 'band':
            m = (kv >= lo + jt[None, :]) & (kv <= hi + jt[None, :])
        else:
            m = kv >= lo + jt[None, :]
    if valid is not None:
        m &= valid
    if exclude_bars:
        rowmax = (kv.max(axis=1) if axis != 'x' else kv.max(axis=0))
        if axis != 'x':
            m &= (rowmax > 0.03)[:, None]
        else:
            m &= (rowmax > 0.03)[None, :]
    if sweep is not None:
        yb = int(sweep * hh)
        m[yb:] = False
    desc = direction in ('up', 'left')
    sorted_ = sort_columns(work, kv, m, desc=desc, min_len=max(2, int(min_len * hh)),
                           max_len=max(2, int(max_len * hh)) if max_len else None)
    mm = m.astype(F32)
    if axis == 'x':
        sorted_ = np.ascontiguousarray(sorted_.transpose(1, 0, 2))
        mm = np.ascontiguousarray(mm.T)
    if rot is not None:
        M, hs, ws = rot
        Mi = cv2.invertAffineTransform(M)
        sorted_ = cv2.warpAffine(sorted_, Mi, (ws, hs), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
        mm = cv2.warpAffine(mm, Mi, (ws, hs), flags=cv2.INTER_NEAREST)
    if fct > 1:
        it = cv2.INTER_NEAREST if upscale == 'nearest' else cv2.INTER_CUBIC
        sorted_ = cv2.resize(sorted_, (w, h), interpolation=it)
        mm = cv2.resize(mm, (w, h), interpolation=cv2.INTER_NEAREST)
    return _mix(x, np.clip(sorted_, 0, 1), mm)


def fx_pixel_sort(x, fx, k, n, ctx):
    """pixel_sort (glitch.pixel_sort) - pixels of each column run inside the mask sorted by key (a permutation).
    mask='bright' (lo=0.62..hi) | 'dark' (0.03..hi=0.3) | 'band' (lo..hi) | 'edges' | 'random' (random_len,
    share=0.45) | 'full'; axis='y'|'x'; dir='down'|'up'|'left'|'right' (asc along the direction); angle=None|35;
    key='luma'|'hue'|'sat'|'r'|'g'|'b'; min_len=0.01, max_len=0.6 (of the line); jitter=0.04 per column;
    work_res=540 (short side) | 'full'; upscale='bicubic'|'nearest'; pulses: times + keys={lo: [[0,.95],[.08,.6],
    [.48,.95]]} (s from the event, eases outExpo then inQuad); sweep=[t0, t1] (zone grows top->bottom, inOutQuad);
    update='live'|'hold2'|'freeze' (freeze_frames=4); seed."""
    a = amount(fx, k, n, ctx)
    if a <= 0:
        return x
    f = _abs_frame(ctx, k)
    fps = _fps(ctx)
    lo = float(anim(fx.get('lo', 0.62), fx, k, n, ctx))
    if fx.get('times') is not None:
        lo = _ps_lo(fx, k, ctx, 0.95)
        if lo >= 0.949:
            return x
    upd = fx.get('update', 'live')
    st = None
    if upd in ('hold2', 'freeze'):
        hold = 2 if upd == 'hold2' else int(fx.get('freeze_frames', 4))
        st = _state(('psort', ctx.get('seg_f0'), _fxkey(fx)))
        anchor = f - (f % hold)
        if st.get('anchor') == anchor and st.get('f') == f - 1 and 'out' in st:
            st['f'] = f
            return st['out']
    sw = fx.get('sweep')
    sweep = None
    if sw:
        k0, k1 = snap(sw[0], fps), snap(sw[1], fps)
        sweep = ease((f - k0) / max(k1 - k0, 1), 'inOutQuad')
    dirn = fx.get('dir', 'down')
    axis = fx.get('axis', 'x' if dirn in ('left', 'right') else 'y')
    hi = float(fx.get('hi', 1.0 if fx.get('mask') != 'dark' else 0.3))
    out = pixel_sort_frame(x, fx.get('mask', 'bright'), lo, hi,
                           axis, dirn, fx.get('key', 'luma'), fx.get('angle'), float(fx.get('min_len', 0.01)),
                           float(fx.get('max_len', 0.6)), fx.get('random_len', (0.02, 0.25)),
                           float(fx.get('share', 0.45)), float(fx.get('jitter', 0.04)), fx.get('work_res', 540),
                           fx.get('upscale', 'bicubic'), _seed(fx.get('seed', 0), f), sweep,
                           fx.get('exclude_bars', True), fx.get('edges'))
    if a < 1:
        out = _lerp(x, out, a)
    if st is not None:
        st.update(anchor=f - (f % (2 if upd == 'hold2' else int(fx.get('freeze_frames', 4)))), f=f, out=out)
    return out


# ----------------------------------------------------------------------------- pixel art / pixelate / posterize
_PALETTES = {'green4': ['#2a5b10', '#598516', '#83a80b', '#a8cf34'], 'duo': ['#1c0e2f', '#bbd8da'],
             '1bit': ['#010101', '#fdfdfd'], 'neon5': ['#05030c', '#116dca', '#412b6a', '#b433cc', '#ead7f6']}
_BAYER4 = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], F32) + 0.5) / 16.0 - 0.5
_CHECK2 = np.array([[0.25, -0.25], [-0.25, 0.25]], F32)


def _quantize(img, pal, dither='none', strength=0.4):
    """Nearest palette colour per pixel (small images), optional ordered dither (bayer4 / checker)."""
    h, w = img.shape[:2]
    v = img.reshape(-1, 3)
    if dither in ('bayer4', 'bayer', 'checker') and len(pal) > 1:
        d = np.sqrt(((pal[:, None, :] - pal[None, :, :]) ** 2).sum(-1))
        d[d == 0] = 9
        spread = float(np.median(d.min(axis=1)))
        pat = _BAYER4 if dither != 'checker' else _CHECK2
        ph, pw = pat.shape
        tile = np.tile(pat, (h // ph + 1, w // pw + 1))[:h, :w]
        v = (img + (tile * F32(spread * strength * 2))[..., None]).reshape(-1, 3)
    d2 = ((v[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
    return pal[np.argmin(d2, axis=1)].reshape(h, w, 3).astype(F32)


def _kmeans_palette(img, k, seed=0):
    smp = img.reshape(-1, 3).astype(F32)
    if len(smp) > 20000:
        smp = smp[_rng(seed, 'km').choice(len(smp), 20000, replace=False)]
    cv2.setRNGSeed(int(seed) & 0x7FFFFFFF)
    k = int(min(max(k, 2), len(smp)))
    _, _, cen = cv2.kmeans(smp, k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1e-3), 2,
                           cv2.KMEANS_PP_CENTERS)
    return np.clip(cen, 0, 1).astype(F32)


def pixelate_frame(x, block, prefilter=True, palette=None, dither='none', strength=0.4):
    h, w = x.shape[:2]
    b = max(1, int(round(block)))
    if b <= 1 and palette is None:
        return x
    src = cv2.medianBlur(_f32(x), 3) if prefilter else _f32(x)
    cw, ch = int(math.ceil(w / b)), int(math.ceil(h / b))
    small = cv2.resize(src, (cw, ch), interpolation=cv2.INTER_AREA)
    if palette is not None:
        small = _quantize(small, palette, dither, strength)
    big = cv2.resize(small, (cw * b, ch * b), interpolation=cv2.INTER_NEAREST)
    return np.ascontiguousarray(big[:h, :w])


def fx_pixelate(x, fx, k, n, ctx):
    """pixelate / mosaic (fx.mosaic) - square blocks on a screen grid: size=0.035 (of output height) | px=N;
    prefilter=False. Block mean colour, nearest upscale."""
    a = amount(fx, k, n, ctx)
    b = fx.get('px') or anim(fx.get('size', 0.035), fx, k, n, ctx) * ctx['oh']
    b = 1 + (float(b) - 1) * a
    return pixelate_frame(x, b, bool(fx.get('prefilter', False)))


def fx_pixel_art(x, fx, k, n, ctx):
    """pixel_art (fx.pixel_art) - integer screen-grid blocks, reduced palette, no smoothing: block=0.008 (of output
    height, rounded to whole px) or px; prefilter median3; colors=12 (k-means per shot, cached) | palette='green4'|
    'duo'|'1bit'|'neon5'|[hex...]; dither='none'|'checker'|'bayer4' (strength 0.4); res_ramp={t:[t0,t1],
    ease:'outCubic'} block 1 -> target (entry) or reverse=True (exit); hold=2 (step_print: frames held, sequential)."""
    f = _abs_frame(ctx, k)
    fps = _fps(ctx)
    a = amount(fx, k, n, ctx)
    B = float(fx.get('px') or round(float(fx.get('block', 0.008)) * ctx['oh']))
    rr = fx.get('res_ramp')
    if rr:
        t0, t1 = rr.get('t', [0, 0.4])
        uu = ease((f / fps - t0) / max(t1 - t0, 1e-6), rr.get('ease', 'outCubic'))
        if rr.get('reverse'):
            uu = 1 - uu
        a *= uu
    if a <= 0:
        return x
    hold = int(fx.get('hold', 1))
    st = _state(('pxart', ctx.get('seg_f0'), _fxkey(fx)))
    if hold > 1 and st.get('f') == f - 1 and (f % hold) != 0 and 'out' in st:
        st['f'] = f
        return st['out']
    blk = max(1, int(round(1 + (B - 1) * a)))
    pal = fx.get('palette')
    if (isinstance(pal, str) and pal in _PALETTES) or isinstance(pal, (list, tuple, np.ndarray)):
        P = np.array(palette(pal, _PALETTES), F32)
    else:
        if 'pal' not in st:
            hgt, wid = x.shape[:2]
            bb = max(1, int(B))
            small = cv2.resize(_f32(x), (max(2, wid // bb), max(2, hgt // bb)), interpolation=cv2.INTER_AREA)
            st['pal'] = _kmeans_palette(small, int(fx.get('colors', 12)), fx.get('seed', 0))
        P = st['pal']
    dith = fx.get('dither', 'bayer4' if len(P) <= 2 else 'none')
    out = pixelate_frame(x, blk, fx.get('prefilter', True), P if blk > 1 else None, dith,
                         float(fx.get('strength', 0.4)))
    if blk <= 1 and a < 1:
        out = x
    st.update(f=f, out=out)
    return out


def fx_posterize(x, fx, k, n, ctx):
    """posterize - levels=4 per channel (mode='rgb') or on luma keeping chroma ratios (mode='luma'); dither='none'|
    'bayer4'; amt mixes with the original."""
    a = amount(fx, k, n, ctx)
    L = max(2, int(round(anim(fx.get('levels', 4), fx, k, n, ctx))))
    lut = (np.round(np.arange(256) / 255.0 * (L - 1)) / (L - 1)).astype(F32).reshape(1, 256)
    xx = _f32(x)
    if fx.get('dither') in ('bayer4', 'bayer'):
        h, w = xx.shape[:2]
        tile = np.tile(_BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w] * F32(1.0 / (L - 1))
        xx = cv2.add(xx, _gray3(np.ascontiguousarray(tile)))
    if fx.get('mode') == 'luma':
        Y = _luma(xx)
        Yq = cv2.LUT(cv2.convertScaleAbs(Y, alpha=255), lut)
        ratio = Yq / np.maximum(Y, 1e-3)
        out = np.clip(xx * ratio[..., None], 0, 1).astype(F32)
    else:
        out = cv2.LUT(cv2.convertScaleAbs(xx, alpha=255), lut)
    return _lerp(x, out, a) if a < 1 else out


def fx_duotone(x, fx, k, n, ctx):
    """duotone - luma mapped to a shadows->highlights gradient (optional mid): shadows='#1c0e2f',
    highlights='#ffd27a', mid=None, contrast=1.0, gamma=1.0, amount=1.0 (or amt)."""
    a = amount(fx, k, n, ctx) * float(fx.get('amount', 1.0))
    sh, hi = color(fx.get('shadows', '#1c0e2f')), color(fx.get('highlights', '#ffd27a'))
    mid = fx.get('mid')
    v = np.arange(256, dtype=F32) / 255.0
    c = float(fx.get('contrast', 1.0))
    if c != 1.0:
        v = np.clip((v - 0.5) * c + 0.5, 0, 1)
    g = float(fx.get('gamma', 1.0))
    if g != 1.0:
        v = v ** g
    if mid is not None:
        mc = color(mid)
        lut = np.where(v[:, None] < 0.5, sh + (mc - sh) * (v[:, None] * 2), mc + (hi - mc) * (v[:, None] * 2 - 1))
    else:
        lut = sh + (hi - sh) * v[:, None]
    lut = lut.astype(F32).reshape(1, 256, 3)
    Y8 = cv2.convertScaleAbs(_luma(x), alpha=255)
    tone = cv2.LUT(cv2.merge([Y8, Y8, Y8]), lut)
    return _lerp(x, tone, a) if a < 1 else tone


# ----------------------------------------------------------------------------- glitch bursts / datamosh
def glitch_frame(x, seed, intensity=1.0, kinds=('slices', 'rgb', 'smear', 'blocks', 'invert'), u=1.0,
                 invert_ok=True, wrap=True):
    """One glitch state (fx.glitch): slices shifted sideways (wrap), RGB split, row smear, block shuffle, invert."""
    rng = _rng(seed)
    h, w = x.shape[:2]
    out = _f32(x).copy()
    I = float(intensity)
    if 'slices' in kinds:
        ns = int(rng.integers(3, 4 + int(7 * I)))
        for _ in range(ns):
            hh = int(rng.uniform(0.02, 0.15) * h)
            y0 = int(rng.integers(0, max(1, h - hh)))
            sh = int(rng.choice([-1, 1]) * rng.uniform(0.02, 0.05 + 0.25 * I) * w)
            if wrap:
                out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], sh, axis=1)
            else:
                band = np.zeros_like(out[y0:y0 + hh])
                if sh > 0:
                    band[:, sh:] = out[y0:y0 + hh, :w - sh]
                else:
                    band[:, :w + sh] = out[y0:y0 + hh, -sh:]
                out[y0:y0 + hh] = band
    if 'smear' in kinds and rng.random() < 0.6:
        nr = int(rng.uniform(0.1, 0.1 + 0.3 * I) * h)
        rows = rng.choice(h, nr, replace=False)
        y0 = int(rng.integers(0, h))
        rows = np.clip((rows % max(1, int(h * 0.3))) + y0, 0, h - 1)
        x0s = rng.integers(0, w, len(rows))
        rightward = rng.random() < 0.5
        for r_, x0 in zip(rows, x0s):
            if rightward:
                out[r_, x0:] = out[r_, x0]
            else:
                out[r_, :x0 + 1] = out[r_, x0]
    if 'blocks' in kinds and rng.random() < 0.7:
        # 8-32 px blocks (@1080) copied from elsewhere (or garbage colour) on 5-20 % of the area, clustered in a band
        # (compressed-stream look) instead of uniform confetti
        bs = max(4, int(rng.choice([16, 24, 32]) * u))
        area = rng.uniform(0.05, 0.05 + 0.15 * I)
        band_y = int(rng.integers(0, max(1, h - h // 3)))
        band_h = max(bs, int(h * rng.uniform(0.15, 0.4)))
        nb = int(area * (h * w) / (bs * bs))
        for _ in range(nb):
            ya = int(np.clip(band_y + rng.integers(0, band_h), 0, max(0, h - bs))) // bs * bs
            xa = int(rng.integers(0, max(1, w - bs))) // bs * bs
            yb, xb = int(rng.integers(0, max(1, h - bs))), int(rng.integers(0, max(1, w - bs)))
            if rng.random() < 0.08:
                out[ya:ya + bs, xa:xa + bs] = rng.random(3).astype(F32)
            else:
                out[ya:ya + bs, xa:xa + bs] = x[yb:yb + bs, xb:xb + bs]
    if 'rgb' in kinds and rng.random() < 0.55:
        px = float(rng.uniform(0.005, 0.005 + 0.02 * I) * w)
        chs = [np.ascontiguousarray(out[..., c]) for c in range(3)]
        for c, m in ((0, -1), (2, 1)):
            chs[c] = cv2.warpAffine(chs[c], np.float32([[1, 0, m * px], [0, 1, 0]]), (w, h),
                                    flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
        out = cv2.merge(chs)
    if 'invert' in kinds and invert_ok:
        if rng.random() < 0.5:
            out = 1.0 - out
        else:
            out = np.ascontiguousarray(out[..., list(rng.permutation(3))])
    return out


def fx_glitch(x, fx, k, n, ctx):
    """glitch / glitch_blocks (fx.glitch) - discrete digital-glitch bursts: times (events) + burst=4 frames
    (1-8 @25), hold=2 (frames per state, 1-3); without times the gated frames are one continuous burst;
    kinds=['slices','rgb','smear','blocks','invert'] (slices: 3-10 bands 2-15 % H shifted 2-30 % W with wrap; rgb
    0.5-2.5 % W; smear 10-40 % rows; blocks 8-32 px on 5-20 % area; invert/channel swap once per burst);
    intensity=0.3-1.0; wrap=True; seed."""
    a = amount(fx, k, n, ctx)
    if a <= 0:
        return x
    f = _abs_frame(ctx, k)
    hold = max(1, int(fx.get('hold', 2)))
    sc = _fps(ctx) / 25.0
    burst = max(1, int(round(float(fx.get('burst', 4)) * sc)))
    base = _seed('glitch', fx.get('seed', 0))
    ev = events(fx, ctx, None)
    if ev:
        cur = None
        for e in ev:
            if 0 <= f - e[1] < burst:
                cur = e
        if cur is None:
            return x
        d = f - cur[1]
        state = d // hold
        sd = _seed(base, cur[3], state)
        inv_state = int(_hash_u01(_seed(base, cur[3], 'inv'), np.array([0]))[0] * max(1, (burst + hold - 1) // hold))
    else:
        d = k
        state = f // hold
        sd = _seed(base, state)
        inv_state = -1 if (state % 7) else state
    kinds = fx.get('kinds', ['slices', 'rgb', 'smear', 'blocks', 'invert'])
    return glitch_frame(x, sd, float(fx.get('intensity', 0.7)) * a, kinds, _u(ctx),
                        invert_ok=('invert' in kinds and state == inv_state), wrap=fx.get('wrap', True))


def _block_flow(prev_g, cur_g, block):
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_ULTRAFAST)
    fl = dis.calc(prev_g, cur_g, None)
    h, w = prev_g.shape
    bw, bh = max(1, w // block), max(1, h // block)
    return cv2.resize(fl, (bw, bh), interpolation=cv2.INTER_AREA)


def mosh_step(prev_out, prev_g, cur, cur_g, block, refresh, seed, holes=0.0, frozen=None):
    """One datamosh step: blocks of prev_out move along the block flow of cur (or the frozen field), a `refresh`
    share of blocks takes the new frame; returns (out, flow_blocks)."""
    h, w = cur.shape[:2]
    gh, gw = cur_g.shape
    fb = frozen if frozen is not None else _block_flow(prev_g, cur_g, block)
    sx, sy = w / float(gw), h / float(gh)
    fullv = cv2.resize(fb, (w, h), interpolation=cv2.INTER_NEAREST)
    gx, gy = _grid(h, w)
    mx = gx - fullv[..., 0] * F32(sx)
    my = gy - fullv[..., 1] * F32(sy)
    warped = cv2.remap(_f32(prev_out), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    bh, bw = fb.shape[:2]
    ids = np.arange(bh * bw).reshape(bh, bw)
    rmask = (_hash_u01(seed, ids) < refresh).astype(F32)
    if holes > 0:
        hm = _hash_u01(seed ^ 0xABCDEF, ids) < holes
        warped_small_hole = cv2.resize(hm.astype(F32), (w, h), interpolation=cv2.INTER_NEAREST)
        warped = _mix(warped, np.full_like(warped, 0.12), warped_small_hole)
    m = cv2.resize(rmask, (w, h), interpolation=cv2.INTER_NEAREST)
    return _mix(warped, cur, m), fb


def fx_datamosh(x, fx, k, n, ctx):
    """datamosh (glitch.datamosh, method='flow') - pixels of the held frame move in 16 px blocks (work 1/2 res) along
    the motion of the incoming frames; mode='continuous' (refresh=0.02 per frame) | 'bloom' (one motion field
    repeated, repeats=15, then clean) | 'melt' (refresh grows inQuad 0.02 -> 1 over dur=1.2 s from the first frame);
    block=16; holes=0.0 (share of grey blocks); seed. Sequential: the first frame (or a gap) restarts clean."""
    a = amount(fx, k, n, ctx)
    f = _abs_frame(ctx, k)
    fps = _fps(ctx)
    st = _state(('mosh', ctx.get('seg_f0'), _fxkey(fx)))
    h, w = x.shape[:2]
    g = cv2.cvtColor(cv2.convertScaleAbs(_down(x, 2), alpha=255), cv2.COLOR_RGB2GRAY)
    if st.get('f') != f - 1 or 'out' not in st or a <= 0:
        st.update(f=f, out=_f32(x).copy(), g=g, f0=f, frozen=None)
        return x
    mode = fx.get('mode', 'continuous')
    blk = int(fx.get('block', 16))
    el = f - st['f0']
    frozen = None
    if mode == 'bloom':
        if el > int(fx.get('repeats', 15)):
            st.update(f=f, out=_f32(x).copy(), g=g)
            return x
        frozen = st.get('frozen')
        refresh = 0.0
    elif mode == 'melt':
        refresh = 0.02 + 0.98 * ease(el / max(1.0, float(fx.get('dur', 1.2)) * fps), 'inQuad')
    else:
        refresh = float(fx.get('refresh', 0.02))
    out, fb = mosh_step(st['out'], st['g'], x, g, blk, refresh, _seed(fx.get('seed', 0), f),
                        float(fx.get('holes', 0.0)), frozen)
    if mode == 'bloom' and st.get('frozen') is None:
        st['frozen'] = fb
    st.update(f=f, out=out, g=g)
    return _lerp(x, out, a) if a < 1 else out


# ----------------------------------------------------------------------------- lens warp
def _lens_grid(h, w, cx, cy):
    key = ('lensgrid', h, w, round(cx, 4), round(cy, 4))
    st = _state(key)
    if not st:
        gx, gy = _grid(h, w)
        st['X'] = gx - F32(cx)
        st['Y'] = gy - F32(cy)
        st['r2'] = st['X'] * st['X'] + st['Y'] * st['Y']
    return st['X'], st['Y'], st['r2']


def lens_maps(h, w, mode, strength, center=(0.5, 0.5), radius=1.0, k2=0.0, fill=1.0, direction=1.0):
    """remap maps for lens_warp (trans.lens_distort formulas). bulge/pinch: r_src = r(1-(1-1/M)(1-u^2)^2), u=r/R;
    twirl: phi_src = phi - theta(1-u)^2; barrel/pincushion: r_src = r(1+k1 rho^2+k2 rho^4)/fill, rho=r/half-diag."""
    cx, cy = center[0] * w, center[1] * h
    X, Y, r2 = _lens_grid(h, w, cx, cy)
    hd2 = 0.25 * (w * w + h * h)
    if mode in ('bulge', 'pinch', 'sphere'):
        M = max(float(strength), 1e-3)
        R2 = (radius * radius) * hd2
        t = np.clip(1.0 - r2 * F32(1.0 / R2), 0, None)
        fct = 1.0 - F32(1.0 - 1.0 / M) * t * t
        return (X * fct + F32(cx)).astype(F32), (Y * fct + F32(cy)).astype(F32)
    if mode == 'twirl':
        th = math.radians(float(strength)) * direction
        R = radius * math.sqrt(hd2)
        uu = np.clip(1.0 - np.sqrt(r2) * F32(1.0 / R), 0, None)
        ang = F32(-th) * uu * uu
        c, s = np.cos(ang), np.sin(ang)
        return (X * c - Y * s + F32(cx)).astype(F32), (X * s + Y * c + F32(cy)).astype(F32)
    k1 = float(strength)
    rho2 = r2 * F32(1.0 / hd2)
    fct = (1.0 + F32(k1) * rho2 + F32(k2) * rho2 * rho2) * F32(1.0 / fill)
    return (X * fct + F32(cx)).astype(F32), (Y * fct + F32(cy)).astype(F32)


def barrel_fill(k1, k2, h, w):
    """Fill zoom for barrel k1/k2 that keeps the long-edge midpoints inside the picture (only the corners mirror,
    hidden by the blur near the peak); the card's quick variant is 1 + 0.5-0.6 k1, full cover 1 + k1 + k2."""
    rho2 = (max(h, w) / 2.0) ** 2 / (0.25 * (h * h + w * w))
    return max(1.0, 1.0 + k1 * rho2 + k2 * rho2 * rho2)


def lens_warp_frame(x, mode, strength, center=(0.5, 0.5), radius=1.0, k2=0.0, fill=1.0, direction=1.0, half=True):
    h, w = x.shape[:2]
    if half and h >= 64:
        mx, my = lens_maps(h // 2, w // 2, mode, strength, center, radius, k2, fill, direction)
        mx = cv2.resize(mx, (w, h), interpolation=cv2.INTER_LINEAR) * F32(w / float(w // 2))
        my = cv2.resize(my, (w, h), interpolation=cv2.INTER_LINEAR) * F32(h / float(h // 2))
    else:
        mx, my = lens_maps(h, w, mode, strength, center, radius, k2, fill, direction)
    return cv2.remap(_f32(x), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)


def fx_lens_warp(x, fx, k, n, ctx):
    """lens_warp - mode='bulge'|'pinch'|'twirl'|'barrel'|'pincushion'|'sphere'; strength = M (bulge 1.8-3, pinch
    0.5-0.65, sphere 1.5) | theta deg (twirl, dir='cw'|'ccw') | k1 (barrel +0.3..0.9, pincushion -0.3..-0.5) |
    [keys over t]; k2=0.05; center=[.5,.5]|'face'; radius=1.0 (half-diagonals); fill='auto' (barrel: long-edge
    midpoints stay inside, see barrel_fill) | number; chroma=0 (R/B strength x(1 +- chroma)); vignette=0."""
    a = amount(fx, k, n, ctx)
    mode = fx.get('mode', 'bulge')
    dflt = {'bulge': 2.0, 'pinch': 0.6, 'sphere': 1.5, 'twirl': 180.0, 'barrel': 0.45, 'pincushion': -0.4}[mode]
    s = anim(fx.get('strength', dflt), fx, k, n, ctx)
    if mode in ('bulge', 'pinch', 'sphere'):
        s = math.exp(math.log(max(s, 1e-3)) * a)
    else:
        s *= a
    fill = fx.get('fill', 'auto')
    if fill == 'auto':
        fill = barrel_fill(s, float(fx.get('k2', 0.05)), x.shape[0], x.shape[1]) if mode == 'barrel' else 1.0
    c = _center(fx, ctx)
    dr = -1.0 if fx.get('dir') == 'cw' else 1.0
    rad = float(fx.get('radius', 1.0))
    out = lens_warp_frame(x, mode, s, c, rad, float(fx.get('k2', 0.05 if mode == 'barrel' else 0)), float(fill), dr)
    ch = float(fx.get('chroma', 0.0)) * a
    if ch > 0:
        chs = [np.ascontiguousarray(out[..., i]) for i in range(3)]
        for ci, mul in ((0, 1 + ch), (2, 1 - ch)):
            ss = math.exp(math.log(max(s, 1e-3)) * mul) if mode in ('bulge', 'pinch', 'sphere') else s * mul
            chs[ci] = np.ascontiguousarray(lens_warp_frame(x, mode, ss, c, rad, 0.0, float(fill), dr)[..., ci])
        out = cv2.merge(chs)
    vg = float(fx.get('vignette', 0.0)) * a
    if vg > 0:
        out = cv2.multiply(out, _gray3(_vig_mask(x.shape[0], x.shape[1], vg)))
    return out


# ----------------------------------------------------------------------------- vignette / letterbox / misc
def _vig_dist(h, w, center, aspect, shape):
    key = ('vigd', h, w, tuple(round(float(c), 4) for c in center), aspect, shape)
    st = _state(key)
    if not st:
        gx, gy = _grid(h, w)
        if shape == 'legacy':
            d = ((gx / w - center[0]) ** 2 / 0.25 + (gy / h - center[1]) ** 2 / 0.25)
            st['d'] = np.clip(d, 0, 1.5).astype(F32)
        else:
            st['d'] = (np.sqrt(((gx - center[0] * w) / float(aspect)) ** 2 + (gy - center[1] * h) ** 2) / h).astype(F32)
    return st['d']


def _vig_mask(h, w, amount_, radius=None, feather=None, center=(0.5, 0.5), aspect=None, shape='legacy'):
    """Multiplier mask: legacy ed_edl ellipse 1 - amount*clip(d, 0, 1.5), or lens.vignette circle/ellipse with
    radius/feather in frame heights (smoothstep edge). Distance fields are cached, the amount is applied per call."""
    if shape == 'legacy' or radius is None:
        d = _vig_dist(h, w, center, None, 'legacy')
        return cv2.addWeighted(d, -float(amount_), d, 0.0, 1.0)
    d = _vig_dist(h, w, center, 1.0 if aspect is None else float(aspect), 'lens')
    m = np.clip((d - F32(radius)) * F32(1.0 / max(feather or 0.15, 1e-3)), 0, 1)
    m = m * m * (3 - 2 * m)
    return cv2.addWeighted(m, -float(amount_), m, 0.0, 1.0)


def fx_vignette(x, fx, k, n, ctx):
    """vignette (legacy ed_edl amount=0.35 elliptical) or lens.vignette: radius=0.38 (of H), feather=0.15 (of H),
    center=[.5,.48], aspect=1.0 (circle in px), amount=1.0 (corners to black) | [keys]; amt."""
    a = amount(fx, k, n, ctx)
    h, w = x.shape[:2]
    am = float(anim(fx.get('amount', 0.35), fx, k, n, ctx)) * a
    if 'radius' in fx:
        rad = float(anim(fx['radius'], fx, k, n, ctx))
        m = _vig_mask(h, w, am, rad, float(fx.get('feather', 0.15)), tuple(_center(fx, ctx)), fx.get('aspect', 1.0),
                      'lens')
    else:
        m = _vig_mask(h, w, am)
    return cv2.multiply(_f32(x), _gray3(m))


def fx_letterbox(x, fx, k, n, ctx):
    """letterbox (fx.letterbox) - bars animate between aspect ratios (absolute time, through cuts): ratio=[r0, r1, ..]
    (2.39 | 2.2 | 1.78 | 1.33 | 0.8 | 1.0 ...; above the frame aspect -> top/bottom bars, below -> side bars) over
    t=[t0, t1] (or t_keys), ease='linear'; holds r0 before / last after; anchor=[0.5, 0.5] (y 0.33 = closing to the
    eyes: the lower bar moves twice as fast); color='#000000'; antialiased edges."""
    f = _abs_frame(ctx, k)
    fps = _fps(ctx)
    h, w = x.shape[:2]
    rs = fx.get('ratio', [1.78, 2.39])
    if _num(rs):
        rs = [float(rs)]
    times = fx.get('t_keys')
    if not times:
        t = fx.get('t')
        if isinstance(t, (list, tuple)) and len(t) == 2:
            times = list(np.linspace(float(t[0]), float(t[1]), len(rs)))
        else:
            t0 = (ctx.get('seg_f0') or 0) / fps
            times = list(np.linspace(t0, t0 + max(n - 1, 1) / fps, len(rs)))
    tt = f / fps
    e = fx.get('ease', 'linear')
    if len(rs) == 1 or tt <= times[0]:
        r = float(rs[0])
    elif tt >= times[-1]:
        r = float(rs[-1])
    else:
        i = min(int(np.searchsorted(times, tt, side='right')) - 1, len(rs) - 2)
        uu = (tt - times[i]) / max(times[i + 1] - times[i], 1e-9)
        r = float(rs[i]) + (float(rs[i + 1]) - float(rs[i])) * ease(uu, e)
    ax, ay = fx.get('anchor', [0.5, 0.5])
    col = color(fx.get('color', '#000000'))
    asp = w / float(h)
    if abs(r - asp) <= 0.005 * asp:          # '1.78' means the frame's own 16:9 (no sliver bars)
        return x
    out = _f32(x).copy()
    if r > asp + 1e-6:
        vis = w / r
        tot = h - vis
        top, bot = tot * ay, tot * (1 - ay)
        _bar(out, top, h - bot, axis=0, col=col)
    elif r < asp - 1e-6:
        vis = h * r
        tot = w - vis
        lft, rgt = tot * ax, tot * (1 - ax)
        _bar(out, lft, w - rgt, axis=1, col=col)
    return out


def _bar(out, a, b, axis, col):
    """Paint everything outside [a, b) along axis with col; fractional edges antialiased."""
    n = out.shape[axis]
    ai, bi = int(math.floor(a)), int(math.ceil(b))
    sl = [slice(None)] * 3
    if ai > 0:
        sl[axis] = slice(0, ai)
        out[tuple(sl)] = col
    if ai < n and a > ai:
        sl[axis] = slice(ai, ai + 1)
        fr = F32(a - ai)
        out[tuple(sl)] = out[tuple(sl)] * (1 - fr) + col * fr
    if bi < n:
        sl[axis] = slice(bi, n)
        out[tuple(sl)] = col
    if 0 < bi <= n and b < bi:
        sl[axis] = slice(bi - 1, bi)
        fr = F32(bi - b)
        out[tuple(sl)] = out[tuple(sl)] * (1 - fr) + col * fr


def fx_dirblur(x, fx, k, n, ctx):
    """dirblur (legacy) - len=0.05 (of output width), angle=0 deg; long blurs computed at reduced resolution."""
    return dir_blur(_f32(x), float(fx.get('len', 0.05)) * ctx['ow'] * amount(fx, k, n, ctx), fx.get('angle', 0.0))


def fx_zoomblur(x, fx, k, n, ctx):
    """zoomblur (legacy) - amount=0.12 (scale spread), cx, cy, n=8 (doubling: log2(n) warps)."""
    am = float(fx.get('amount', 0.12)) * amount(fx, k, n, ctx)
    return zoom_blur(_f32(x), 1.0 + am, float(fx.get('cx', 0.5)), float(fx.get('cy', 0.5)), int(fx.get('n', 8)))


def fx_chroma(x, fx, k, n, ctx):
    """chroma (legacy ed_edl) - px=6 (scaled ow/1080 like ed_edl), vertical=False; R +px, B -px like ed_edl but with
    reflected edges instead of np.roll wrap-around."""
    px = float(fx.get('px', 6)) * amount(fx, k, n, ctx) * ctx['ow'] / 1080.0
    return fx_rgb_split(x, dict(px=-px / _u(ctx), angle=90.0 if fx.get('vertical') else 0.0), 0, 1, ctx)


def fx_smear(x, fx, k, n, ctx):
    """smear (legacy) - dirblur(len=0.25) + chroma(px=14) + saturation x1.6."""
    a = amount(fx, k, n, ctx)
    y = dir_blur(_f32(x), float(fx.get('len', 0.25)) * ctx['ow'] * a, fx.get('angle', 0.0))
    y = fx_chroma(y, dict(px=fx.get('px', 14), amt=a), k, n, ctx)
    L = _luma(y)
    s = float(fx.get('sat', 1.6))
    return _clip01(cv2.addWeighted(y, s, _gray3(L), 1 - s, 0))


def fx_blur(x, fx, k, n, ctx):
    """blur (legacy) - r=6 (px @1080 width, ow/1080); large radii on a pyramid."""
    r = float(fx.get('r', 6)) * amount(fx, k, n, ctx) * ctx['ow'] / 1080.0
    if r <= 0.3:
        return x
    if r < 6:
        return cv2.GaussianBlur(_f32(x), (0, 0), r)
    h, w = x.shape[:2]
    return cv2.resize(_pyr_sum(_f32(x), [r], [1.0]), (w, h))


def fx_shake_img(x, fx, k, n, ctx):
    """shake (legacy image-space) - px=12 (@1080 width) random offset per frame (hashed, deterministic)."""
    a = float(fx.get('px', 12)) * ctx['ow'] / 1080.0 * amount(fx, k, n, ctx)
    r = _rng(fx.get('seed', 0), 'shk', _abs_frame(ctx, k))
    M = np.float32([[1, 0, r.uniform(-a, a)], [0, 1, r.uniform(-a, a)]])
    return _warp(x, M)


def fx_exposure(x, fx, k, n, ctx):
    """exposure (legacy) - ev=0 stops."""
    return _clip01(_f32(x) * F32(2.0 ** (float(fx.get('ev', 0.0)) * amount(fx, k, n, ctx))))


def fx_invert(x, fx, k, n, ctx):
    """invert (legacy) - negative (amt < 1 mixes)."""
    a = amount(fx, k, n, ctx)
    y = 1.0 - _f32(x)
    return _lerp(x, y, a) if a < 1 else y


def fx_bleach(x, fx, k, n, ctx):
    """bleach (legacy) - a=0.5 mix toward white."""
    b = float(fx.get('a', 0.5)) * amount(fx, k, n, ctx)
    return cv2.addWeighted(_f32(x), 1 - b, _f32(x), 0, b)


def fx_flash(x, fx, k, n, ctx):
    """flash (image fx) - flash pulses on explicit events: times (required), color='#ffffff', tau=0.06 s,
    peak_frames=1, cutoff=0.05, mode='solid'|'add'|'screen'|'black'|'invert'|'exposure' (see flash_op)."""
    fps = _fps(ctx)
    f = _abs_frame(ctx, k)
    curve = flash_curve(fps, float(fx.get('tau', 0.06)), int(fx.get('peak_frames', 1)), float(fx.get('cutoff', 0.05)))
    best = 0.0
    for t, k0, w, i in events(fx, ctx, None):       # explicit times only (no strobe on every beat by default)
        d = f - k0
        if 0 <= d < len(curve):
            best = max(best, curve[d] * w)
    if best <= 0:
        return x
    op = dict(fx)
    op['curve'] = [best * amount(fx, k, n, ctx)]
    return flash_op(x, op, 0, ctx)


# ============================================================================= subject matte and subject-aware fx
_REGIONS = {'background': 'bg', 'bg': 'bg', 'behind': 'bg', 'back': 'bg', 'backdrop': 'bg', 'subject': 'fg',
            'person': 'fg', 'fg': 'fg', 'foreground': 'fg', 'all': None, 'frame': None, 'full': None}


def subject_matte(x, ctx, fx=None):
    """Subject (person) matte (h, w) float32 0..1 of the current frame, or None. Sources in order: ctx['mask'] (the
    external matte of sources.<name>.mask, warped like the picture, output size), ctx['person_mask'] (array, or
    callable f_abs -> array), else - unless fx auto_mask=False - ed_video.person_mask(frame) (PP-HumanSeg, cached
    per frame). Probability maps of any size are resized to x; uint8 maps are scaled to 0..1."""
    h, w = x.shape[:2]
    ctx = ctx or {}
    m = ctx.get('mask')
    if m is None:
        pm = ctx.get('person_mask')
        if callable(pm):
            try:
                m = pm(int(ctx.get('f_abs', 0) or 0))
            except Exception:
                m = None
        elif pm is not None:
            m = pm
    if m is None and (fx is None or fx.get('auto_mask', True)):
        st = _state(('automask', int(ctx.get('f_abs', -1) or -1), h, w), limit=60)
        if 'm' not in st:
            try:
                import importlib
                V = importlib.import_module('ed_video')
                st['m'] = V.person_mask((np.clip(_f32(x), 0, 1) * 255.0 + 0.5).astype(np.uint8))
            except Exception as e:                      # no model / no module: the fx covers the whole frame
                st['m'] = None
                _warn_once(('automask', type(e).__name__), f'no subject matte ({type(e).__name__}: {e}); '
                                                           f'region fx apply to the whole frame')
        m = st['m']
    if m is None:
        return None
    m = np.asarray(m, F32)
    if m.ndim == 3:
        m = np.ascontiguousarray(m[..., 0])
    if m.size and float(m.max()) > 1.5:
        m = m * F32(1.0 / 255.0)
    if m.shape != (h, w):
        m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
    return np.clip(m, 0.0, 1.0)


def region_weight(x, fx, ctx):
    """Where an fx with region applies (h, w) 0..1: region 'background' (or behind=True) = 1 - matte, 'subject' =
    matte; expand (fraction of the short side, + grows the subject) and feather (Gaussian, default 0.004) shape the
    edge. None = everywhere (no region, region 'all', or no matte available)."""
    reg = fx.get('region')
    if reg is None and fx.get('behind'):
        reg = 'background'
    r = _REGIONS.get(str(reg).strip().lower()) if reg else None
    if r is None:
        return None
    m = subject_matte(x, ctx, fx)
    if m is None:
        return None
    S = float(min(x.shape[:2]))
    ex = float(fx.get('expand', 0.0)) * S
    if abs(ex) >= 0.5:
        kk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(round(abs(ex))) * 2 + 1,) * 2)
        m = cv2.dilate(m, kk) if ex > 0 else cv2.erode(m, kk)
    fe = float(fx.get('feather', 0.004)) * S
    if fe > 0.3:
        m = cv2.GaussianBlur(m, (0, 0), fe)
    return m if r == 'fg' else cv2.subtract(np.ones_like(m), m)


def fx_contour_glow(x, fx, k, n, ctx):
    """contour_glow (fx.glow contour) - a coloured glow hugging the subject's outline (needs a subject matte: ctx
    mask / person_mask / auto): color='#8a5cff', width=0.005 (lit rim, of the short side), radius=0.03 (glow spread),
    strength=0.8, inner=0.15 (share of the glow also inside the outline), blend='screen'|'add'; pulses with times +
    env like glow (base=0.3, peak=1.0)."""
    m = subject_matte(x, ctx, fx)
    if m is None:
        return x
    S = _short(ctx) if ctx.get('ow') else float(min(x.shape[:2]))
    a = amount(fx, k, n, ctx)
    if fx.get('times') is not None:
        env, ev = pulse(fx, k, ctx, attack=0, hold=0, tau=3.0, cutoff=0.01)
        a *= float(fx.get('base', 0.3)) + (float(fx.get('peak', 1.0)) - float(fx.get('base', 0.3))) * env
    if a <= 1e-3:
        return x
    wd = max(1, int(round(float(fx.get('width', 0.005)) * S)))
    kk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * wd + 1, 2 * wd + 1))
    edge = cv2.subtract(cv2.dilate(m, kk), cv2.erode(m, kk))
    r = float(fx.get('radius', 0.03)) * S
    g = _pyr_sum(edge, [max(r * 0.35, 0.5), r], [0.55, 0.45]) if r > 1 else edge
    g = cv2.add(g * F32(1.6), edge * F32(0.6))
    inner = float(fx.get('inner', 0.15))
    g = cv2.multiply(g, cv2.addWeighted(m, inner - 1.0, m, 0.0, 1.0))      # mostly outside the outline
    g = np.clip(g * F32(float(fx.get('strength', 0.8)) * a), 0, 1)
    lay = (g[..., None] * color(fx.get('color', '#8a5cff'))[None, None, :]).astype(F32)
    if fx.get('blend', 'screen') == 'add':
        return _clip01(cv2.add(_f32(x), lay))
    return cv2.subtract(cv2.add(_f32(x), lay), cv2.multiply(_f32(x), lay))


def fx_defocus(x, fx, k, n, ctx):
    """defocus (focus.shallow, bg blur) - lens-like blur: a disc kernel in linear light at reduced resolution:
    amount=0.012 (disc radius, of the short side) | [keys]; highlights=1.5 (extra weight of bright spots inside their
    disc: small highlights open into bright bokeh discs while flat areas keep their level; 0 = plain disc blur).
    Usually with region='background' (the subject stays sharp; matte from ctx mask)."""
    S = float(min(x.shape[:2]))
    r = anim(fx.get('amount', 0.012), fx, k, n, ctx) * S * amount(fx, k, n, ctx)
    if r < 0.75:
        return x
    h, w = x.shape[:2]
    f = max(1.0, r / 5.0)
    xs = _down(_f32(x), f) if f > 1.0 else _f32(x)
    rs = max(1, int(round(r / f)))
    lin = cv2.multiply(xs, xs)
    kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * rs + 1, 2 * rs + 1)).astype(F32)
    kern /= float(kern.sum())
    hb = float(fx.get('highlights', 1.5))
    if hb > 0:
        # highlights weigh more inside their disc (normalised convolution): small bright spots open into bokeh
        # discs while flat areas, bright ones included, keep their level
        wgt = (1.0 + hb * _smoothstep(0.75, 1.0, _luma(xs))).astype(F32)
        y = cv2.filter2D(cv2.multiply(lin, _gray3(wgt)), -1, kern, borderType=cv2.BORDER_REFLECT101)
        y = cv2.divide(y, _gray3(cv2.filter2D(wgt, -1, kern, borderType=cv2.BORDER_REFLECT101)))
    else:
        y = cv2.filter2D(lin, -1, kern, borderType=cv2.BORDER_REFLECT101)
    y = cv2.sqrt(np.clip(y, 0, None))
    if f > 1.0:
        y = cv2.resize(y, (w, h), interpolation=cv2.INTER_LINEAR)
    return _clip01(y)


def fx_clarity(x, fx, k, n, ctx):
    """clarity - local contrast on luma (a large-radius unsharp mask on the midtones): amount=0.4 (-1..1; negative
    softens skin-like detail) | [keys]; radius=0.02 (of the short side). The weight 4L(1-L) is 0 at black and at
    white, and the change is a per-pixel exposure (hue and saturation kept) that eases toward black and toward the
    brightest channel reaching 1, so clarity never adds clipped pixels."""
    a = anim(fx.get('amount', 0.4), fx, k, n, ctx) * amount(fx, k, n, ctx)
    if abs(a) < 1e-3:
        return x
    xx = _f32(x)
    L = np.clip(_luma(xx), 0.0, 1.0)
    r = float(fx.get('radius', 0.02)) * float(min(x.shape[:2]))
    B = _pyr_sum(L, [max(r, 0.5)], [1.0])
    w = cv2.multiply(L * F32(4.0), cv2.subtract(np.ones_like(L), L))          # 0 at black and at white
    dL = cv2.multiply(cv2.subtract(L, B), w) * F32(a * 1.6)
    Ls = np.maximum(L, F32(1e-4))
    e = F32(1.0 / 255.0)                     # keep one 8-bit level of room at both ends
    mn = np.maximum(xx.min(axis=2), F32(1e-6))
    mx = np.maximum(xx.max(axis=2), F32(1e-6))
    up = np.maximum(Ls * ((F32(1.0) - e) / mx - F32(1.0)), F32(1e-7))     # gain before the top channel nears 1
    dn = np.maximum(Ls * (F32(1.0) - e / mn), F32(1e-7))                   # loss before the low channel nears 0
    # soft bounds (first order: dL unchanged): the darkest channel never reaches 0, the brightest never 1
    dL = np.where(dL >= 0, up * (F32(1.0) - np.exp(-np.maximum(dL, F32(0.0)) / up)),
                  dn * (np.exp(np.minimum(dL, F32(0.0)) / dn) - F32(1.0))).astype(F32)
    g = F32(1.0) + dL / Ls
    return _clip01(cv2.multiply(xx, _gray3(g.astype(F32))))


def fx_saturation(x, fx, k, n, ctx):
    """saturation - colour intensity: sat=0.0 (0 = black and white, 1 = unchanged, > 1 boosted) | [keys]; hue=0.0
    (rotation, degrees). With region='background' it is the colour-pop look (the subject keeps its colour)."""
    a = amount(fx, k, n, ctx)
    s = 1.0 + (anim(fx.get('sat', 0.0), fx, k, n, ctx) - 1.0) * a
    xx = _f32(x)
    hue = float(anim(fx.get('hue', 0.0), fx, k, n, ctx)) * a
    if abs(hue) > 0.05:
        hsv = cv2.cvtColor(np.clip(xx, 0, 1), cv2.COLOR_RGB2HSV)
        hsv[..., 0] = (hsv[..., 0] + F32(hue)) % F32(360.0)
        xx = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    if abs(s - 1.0) < 1e-4:
        return xx
    L = _gray3(_luma(xx))
    return _clip01(cv2.addWeighted(xx, s, L, 1.0 - s, 0.0))


def fx_tape(x, fx, k, n, ctx):
    """tape (look.vhs) - home-videotape texture: soft low-resolution picture (res=0.36 of the width, vres=0.6 of the
    height), luma smear=0.0015 (of W), chroma bleed (chroma_blur=3, x the luma smear) shifted right
    (chroma_shift=0.004 of W), scanlines (depth=0.07, period 2 px @1080), luma noise=0.03, line jitter=0.0008 (of W),
    a tracking band now and then (band={height: 0.05, every: [3, 7] s, dur: 0.3 s, shift: 0.012}; band=None
    disables), head-switching noise at the bottom (head=0.02 of H), soft white point white=0.94 and black=0.016;
    seed. Deterministic per absolute frame; amt mixes with the clean picture."""
    a = amount(fx, k, n, ctx)
    if a <= 1e-3:
        return x
    xx = _f32(x)
    h, w = xx.shape[:2]
    f = _abs_frame(ctx, k)
    fps = _fps(ctx)
    seed = _seed('tape', fx.get('seed', 0))
    u = min(h, w) / 1080.0
    rw = max(16, int(round(w * float(fx.get('res', 0.36)))))
    rh = max(16, int(round(h * float(fx.get('vres', 0.6)))))
    lo = cv2.resize(xx, (rw, rh), interpolation=cv2.INTER_AREA)
    sm = max(1, int(round(float(fx.get('smear', 0.0015)) * w * rw / w)))
    ycc = cv2.cvtColor(lo, cv2.COLOR_RGB2YCrCb)
    Y = np.ascontiguousarray(ycc[..., 0])
    C = np.ascontiguousarray(ycc[..., 1:])
    if sm > 1:
        Y = cv2.blur(Y, (sm, 1))
    cb = max(1, int(round(sm * float(fx.get('chroma_blur', 3.0)))))
    C = cv2.blur(C, (cb * 2 + 1, 1))
    shift = float(fx.get('chroma_shift', 0.004)) * rw
    C = cv2.warpAffine(C, np.float32([[1, 0, shift], [0, 1, 0]]), (rw, rh), flags=cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_REPLICATE)
    lo = cv2.cvtColor(cv2.merge([Y, C[..., 0], C[..., 1]]), cv2.COLOR_YCrCb2RGB)
    out = cv2.resize(lo, (w, h), interpolation=cv2.INTER_LINEAR)
    # line jitter: each row slides a little (hashed per frame)
    jit = float(fx.get('jitter', 0.0008)) * w
    rows = np.arange(h)
    if jit > 0.05:
        js = (_hash_u01(_seed(seed, 'jit', f), rows // max(1, int(2 * u))) - 0.5) * F32(2 * jit)
        gx, gy = _grid(h, w)
        out = cv2.remap(out, gx + js.astype(F32)[:, None], gy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    # tracking band
    band = fx.get('band', {'height': 0.05, 'every': [3, 7], 'dur': 0.3, 'shift': 0.012})
    if band:
        ev = band.get('every', [3, 7])
        dur = float(band.get('dur', 0.3))
        t = f / fps
        slot = 0.5 * (float(ev[0]) + float(ev[1]))
        s_now = int(math.floor(t / slot))
        for s in (s_now - 1, s_now):
            r_ = _rng(seed, 'band', s)
            t0 = (s + float(r_.uniform(0.0, 1.0))) * slot
            if not t0 <= t < t0 + dur:
                continue
            p = (t - t0) / dur
            bh = max(2, int(float(band.get('height', 0.05)) * h))
            yc = int((float(r_.uniform(0.15, 0.85)) + 0.25 * p) * h) % h
            y0, y1 = max(0, yc - bh // 2), min(h, yc + bh // 2)
            if y1 > y0:
                env = math.sin(math.pi * p)
                sh = float(band.get('shift', 0.012)) * w * env
                seg = out[y0:y1]
                seg = cv2.warpAffine(seg, np.float32([[1, 0, sh], [0, 1, 0]]), (w, y1 - y0),
                                     borderMode=cv2.BORDER_REPLICATE)
                nz = _hash_u01(_seed(seed, 'bn', f), np.arange((y1 - y0) * (w // 4 + 1))).reshape(y1 - y0, -1)
                nz = cv2.resize(nz.astype(F32), (w, y1 - y0), interpolation=cv2.INTER_NEAREST)
                streak = (nz > 1.0 - 0.06 * env).astype(F32) * F32(0.55 * env)
                seg = cv2.add(seg * F32(1.0 + 0.12 * env), _gray3(streak))
                out[y0:y1] = seg
    # head switching at the bottom
    hd = int(float(fx.get('head', 0.02)) * h)
    if hd >= 2:
        r_ = _rng(seed, 'head', f)
        sh = float(r_.uniform(0.004, 0.02)) * w
        seg = cv2.warpAffine(out[h - hd:], np.float32([[1, 0, sh], [0, 1, 0]]), (w, hd), borderMode=cv2.BORDER_REPLICATE)
        out[h - hd:] = cv2.addWeighted(seg, 0.85, _solid(hd, w, (0.5, 0.5, 0.5)), 0.15, 0.0)
    # noise (blotchy: quarter-res luma noise) and scanlines
    nz = float(fx.get('noise', 0.03))
    if nz > 0:
        g = _hash_normal(_seed(seed, 'nz', f), np.arange((h // 2) * (w // 3))).reshape(h // 2, w // 3).astype(F32)
        g = cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR) * F32(nz)
        out = cv2.add(out, _gray3(g))
    dep = float(fx.get('depth', 0.07))
    if dep > 0:
        per = max(2, int(round(2 * u)))
        sl = np.where((rows % per) < per / 2.0, 1.0, 1.0 - dep).astype(F32)
        out = cv2.multiply(out, _gray3(np.ascontiguousarray(np.repeat(sl[:, None], w, axis=1))))
    wp, bp = float(fx.get('white', 0.94)), float(fx.get('black', 0.016))
    out = cv2.addWeighted(_soft_clip(np.clip(out, 0, None), 0.85), wp - bp, out, 0.0, bp)
    out = _clip01(out)
    return _lerp(xx, out, a) if a < 1 else out


# ============================================================================= flash frame op (section 3)
_FLASH_COLORS = {'white': '#ffffff', 'warm': '#fff1dc', 'red': '#ff2a2a', 'cyan': '#29e6ff', 'magenta': '#ff2bd6',
                 'acid': '#b6ff2b', 'amber': '#ffb02e'}


def flash_color(c):
    """Flash colour: a flash name (white warm red cyan magenta acid amber) or any color() spec - hex, list, tuple,
    'rgb(...)', int (the TIMELINE op may carry [1, 1, 1])."""
    if isinstance(c, str) and c.strip().lower() in _FLASH_COLORS:
        c = _FLASH_COLORS[c.strip().lower()]
    return color(c, (1.0, 1.0, 1.0))


def flash_curve(fps, tau=0.06, peak_frames=1, cutoff=0.05):
    """trans.flash decay: peak_frames x 1.0 then exp(-t/tau) per frame, stop below cutoff (tau 0 -> strike)."""
    out = [1.0] * max(1, int(peak_frames))
    if tau <= 0:
        return out
    m = 1
    while True:
        v = math.exp(-m / (tau * fps))
        if v < cutoff:
            break
        out.append(round(v, 4))
        m += 1
    return out


def flash_ops(f_seam, fps, tau=0.06, peak_frames=1, pre_frames=0, pre=(0.35, 0.65), color_='#ffffff',
              blend='normal', cutoff=0.05, stage='pre'):
    """EDL ops for a cut flash (trans.flash): optional pre ramp on the last frames of A, peak on the cut frame
    (= beat frame) and the exp(tau) tail on B. Returns a list of {'f', 'op': 'flash', 'color', 'curve', 'blend'}."""
    ops = []
    if pre_frames:
        pv = list(pre)[-pre_frames:]
        ops.append(dict(f=list(range(f_seam - pre_frames, f_seam)), op='flash', color=color_, curve=pv, blend=blend,
                        stage=stage))
    cv = flash_curve(fps, tau, peak_frames, cutoff)
    ops.append(dict(f=list(range(f_seam, f_seam + len(cv))), op='flash', color=color_, curve=cv, blend=blend,
                    stage=stage))
    return ops


def _palette_flash_color(b, seed=0):
    small = cv2.resize(_f32(b), (64, 64), interpolation=cv2.INTER_AREA)
    cen = _kmeans_palette(small, 5, seed)
    hsv = cv2.cvtColor(cen.reshape(1, -1, 3), cv2.COLOR_RGB2HSV)[0]
    i = int(np.argmax(hsv[:, 1]))
    hh = float(hsv[i, 0])
    out = cv2.cvtColor(np.array([[[hh, 0.85, 1.0]]], F32), cv2.COLOR_HSV2RGB)[0, 0]
    return out.astype(F32)


def _flash_apply(x, a, mode, col, ctx=None, ev_peak=None):
    if a <= 0:
        return x
    x = _f32(x)
    if mode in ('solid', 'normal', 'color'):
        return cv2.addWeighted(x, 1 - a, _solid(x.shape[0], x.shape[1], col), a, 0)
    if mode == 'add':
        return _clip01(cv2.scaleAdd(_solid(x.shape[0], x.shape[1], col), float(a), x))
    if mode == 'screen':
        c = _solid(x.shape[0], x.shape[1], col) * F32(a)
        return cv2.subtract(cv2.add(x, c), cv2.multiply(x, c))
    if mode == 'black':
        return cv2.multiply(x, np.full(x.shape, 1 - a, F32))
    if mode == 'invert':
        return cv2.addWeighted(x, 1 - a, 1.0 - x, a, 0)
    if mode == 'exposure':
        evp = ev_peak if ev_peak is not None else _ev_peak(x)
        return _exposure_frame(x, evp * a, 0.6 * a, 0.3 if (evp >= 4 and a >= 0.99) else 0.0)
    return x


def _ev_peak(x):
    """trans.flash exposure: EV = log2(0.85 / median linear luma), clamped to +2..+5."""
    L = _luma(_down(_f32(x), 8))
    med = float(np.median(L * L))
    return min(max(math.log2(0.85 / max(med, 1e-5)), 2.0), 5.0)


def _exposure_frame(x, ev, glow_k=0.0, white=0.0):
    """Linear-light exposure push (soft shoulder) + glow (threshold 0.7, radius 3 % of height) + white mix."""
    h, w = x.shape[:2]
    xx = _f32(x)
    lin = cv2.multiply(xx, xx, scale=2.0 ** ev)
    y = cv2.sqrt(_soft_clip(lin, 0.9))
    if glow_k > 0.02:
        r = 0.03 * h / float(min(h, w))
        y = fx_glow(y, dict(threshold=0.7, radii=[r * 0.5, r], weights=[0.4, 0.6], strength=glow_k), 0, 1,
                    dict(ow=w, oh=h, fps=25))
    if white > 0:
        y = cv2.addWeighted(y, 1 - white, _solid(h, w, (1, 1, 1)), white, 0)
    return _clip01(y)


def flash_op(x, op, j, ctx):
    """Frame op 'flash' (TIMELINE section 3): {f, op:'flash', color='#ffffff'|'warm'|'red'|..., curve=[1, .55, .25,
    .1] (opacity per listed frame, j = index of this frame in op['f']; or tau/peak_frames to build it),
    blend='normal'|'screen'|'add'|'black'|'invert'|'exposure'}."""
    curve = op.get('curve')
    if curve is None:
        curve = flash_curve(_fps(ctx), float(op.get('tau', 0.06)), int(op.get('peak_frames', 1)),
                            float(op.get('cutoff', 0.05)))
    a = float(curve[j]) if 0 <= j < len(curve) else 0.0
    a *= float(op.get('a', 1.0))
    mode = op.get('blend', op.get('mode', 'normal'))
    if mode == 'solid':
        mode = 'normal'
    return _flash_apply(x, a, mode, flash_color(op.get('color', '#ffffff')), ctx)


# ============================================================================= transitions
def _tpos(p, params, ctx, q_seam):
    N = ctx.get('tn') or params.get('frames') or params.get('n')
    if not N:
        return None
    N = int(N)
    j = ctx.get('tj')
    if j is None:
        j = int(min(max(round(p * N - 0.5), 0), N - 1))
    js = ctx.get('tseam')
    if js is None:
        js = int(round(N * q_seam))
    return int(j), N, int(min(max(int(js), 0), N))


def _side(p, params, ctx, q_seam=0.5):
    """('A', u, du) before the cut / ('B', u, du) from the cut: u in (0, 1] - A reaches 1 on its last frame, B goes
    1/nB .. 1 (1 on the last window frame); du = progress per frame on that side."""
    pos = _tpos(p, params, ctx, q_seam)
    if pos is None:
        if p < q_seam:
            return 'A', p / q_seam, 0.15
        return 'B', (p - q_seam) / max(1 - q_seam, 1e-6), 0.15
    j, N, js = pos
    if j < js:
        return 'A', (j + 1) / float(js), 1.0 / js
    nb = max(N - js, 1)
    return 'B', (j - js + 1) / float(nb), 1.0 / nb


def _wstart(ctx):
    if ctx.get('tj') is not None and ctx.get('f_abs') is not None:
        return int(ctx['f_abs']) - int(ctx['tj'])
    return int(ctx.get('f_abs', 0) or 0)


def _frames_or_color(a, b, params):
    col = params.get('color', '#000000')
    if a is None and b is None:
        raise ValueError('transition needs at least one frame')
    ref = a if a is not None else b
    if a is None:
        a = _solid(ref.shape[0], ref.shape[1], col)
    if b is None:
        b = _solid(ref.shape[0], ref.shape[1], col)
    return _f32(a), _f32(b)


def tr_dissolve(a, b, p, params, ctx):
    """dissolve (trans.dissolve) - curve='linear'|'inOutSine'|'outQuad' on p."""
    a, b = _frames_or_color(a, b, params)
    return _lerp(a, b, ease(p, params.get('curve', 'linear')))


def tr_fade(a, b, p, params, ctx):
    """fade / dip (trans.fade) - A -> colour -> B: out/hold/in in seconds (out_frames/hold_frames/in_frames also),
    curve=['linear','linear']|['inQuad','outQuad']; color='#000000' (dip(#0b1020), white for fade-to-white);
    mode='dip'|'in' (from colour; pre-roll) |'out' (to colour and hold; fade-out); grain_keep=0.4 (grain on the held
    colour, sigma 4 levels); hard_in. Frame rule: the last out-frame is pure colour, B share = k/(N+1)."""
    fps = _fps(ctx)
    mode = params.get('mode', 'dip')
    a, b = _frames_or_color(a, b, params)
    col = color(params.get('color', '#000000'))
    cv = params.get('curve', ['linear', 'linear'])
    if isinstance(cv, str):
        cv = [cv, cv]

    def fr(name, dflt):
        if name + '_frames' in params:
            return int(params[name + '_frames'])
        return int(round(float(params.get(name, dflt)) * fps))
    o, hd, i_ = fr('out', 0.24), fr('hold', 0.0 if mode == 'dip' else 0.0), fr('in', 0.28)
    if mode == 'in':
        o, hd = 0, 0
    if mode == 'out':
        i_ = 0
    tot = max(o + hd + i_, 1)
    pos = _tpos(p, params, ctx, (o + hd) / tot)
    if pos is None:
        N = tot
        j = int(min(max(round(p * N - 0.5), 0), N - 1))
        js = o + hd
    else:
        j, N, js = pos
    if mode == 'in':
        js = 0
    if mode == 'out':
        js = N
    hd2 = min(hd, max(js - 1, 0)) if mode != 'out' else min(hd, max(N - 1, 0))
    o2 = max(js - hd2, 0) if mode != 'out' else max(N - hd2, 1)
    i2 = N - js
    h, w = a.shape[:2]
    solid = _solid(h, w, col)
    if j < js or mode == 'out':
        if j < o2:
            mlt = 1.0 - ease((j + 1) / float(o2), cv[0])
            out = cv2.addWeighted(a, mlt, solid, 1 - mlt, 0)
        else:
            out = solid
    else:
        if params.get('hard_in'):
            out = b
        else:
            share = ease((j - js + 1) / float(i2 + 1), cv[1])
            out = cv2.addWeighted(b, share, solid, 1 - share, 0)
    gk = float(params.get('grain_keep', 0.0))
    if gk > 0:
        darkness = 1.0 - float(cv2.mean(cv2.absdiff(out, solid))[0]) * 4
        if darkness > 0:
            out = add_grain(out, 4.0 * gk * darkness, 2.0 * min(h, w) / 1080.0, _abs_frame(ctx, None), 7)
    return out


def tr_flash(a, b, p, params, ctx):
    """flash (trans.flash) - pre_frames=0..2 on A (white share pre=[.35,.65]), peak_frames=1 on the cut frame (first
    B frame = beat frame), tail exp(-t/tau) tau=0.06 s cut below 0.05 (tau 0 = strike, 0.11 = memory);
    color='#ffffff'|'warm'|'red'|'cyan'|'magenta'|'acid'|'amber'|'palette' (most saturated k-means cluster of B,
    S .85 V 1); mode='solid'|'add'|'exposure'|'black'|'invert'. Seam = ctx tseam (default: after the pre frames)."""
    fps = _fps(ctx)
    a, b = _frames_or_color(a, b, params)
    pre = int(params.get('pre_frames', 0))
    pv = list(params.get('pre', [0.35, 0.65]))
    pk = int(params.get('peak_frames', 1))
    tau = float(params.get('tau', 0.06))
    cutoff = float(params.get('cutoff', 0.05))
    curve = flash_curve(fps, tau, pk, cutoff)
    tot = pre + len(curve)
    pos = _tpos(p, params, ctx, pre / max(tot, 1))
    if pos is None:
        j = int(min(max(round(p * tot - 0.5), 0), tot - 1))
        js = pre
    else:
        j, N, js = pos
    mode = params.get('mode', 'solid')
    cname = params.get('color', '#ffffff')
    if isinstance(cname, str) and cname in ('palette', 'auto'):
        st = _state(('flashcol', _wstart(ctx)))
        if 'c' not in st:
            st['c'] = _palette_flash_color(b)
        col = st['c']
    else:
        col = flash_color(cname)
    if mode == 'black':
        col = np.zeros(3, F32)
    d = j - js
    if mode == 'exposure':
        if d < 0:
            evs = [1.0, 2.0][-pre:] if pre else []
            return _exposure_frame(a, evs[pre + d]) if -pre <= d < 0 and pre else a
        st = _state(('flashev', _wstart(ctx)))
        if 'ev' not in st:
            st['ev'] = _ev_peak(b)
        evp = st['ev']
        if d < pk:
            return _exposure_frame(b, evp, 0.6, 0.3 if evp >= 4 else 0.0)
        ev = evp * math.exp(-(d - pk + 1) / (0.08 * fps))
        return _exposure_frame(b, ev, 0.6 * ev / evp) if ev > 0.05 * evp else b
    if d < 0:
        pvs = pv[-pre:] if pre else []
        av = pvs[pre + d] if -pre <= d < 0 and pre else 0.0
        if mode in ('black', 'invert'):
            av = 0.0
        return _flash_apply(a, av, 'normal' if mode in ('solid', 'black', 'color') else mode, col)
    av = curve[d] if d < len(curve) else 0.0
    m = {'solid': 'normal', 'color': 'normal', 'black': 'normal'}.get(mode, mode)
    out = _flash_apply(b, av, m, col)
    bl = params.get('bloom')
    if bl and av > 0:
        gfx = dict(threshold=bl.get('thr', 0.7), radii=[bl.get('r', 0.03)], weights=[1.0],
                   strength=float(bl.get('k', 0.6)) * av)
        out = fx_glow(out, gfx, 0, 1, dict(ow=out.shape[1], oh=out.shape[0], fps=fps))
    return out


def _dir_vec(params, default='right'):
    d = params.get('dir', default)
    if 'angle' in params and params.get('angle') is not None and not isinstance(d, str):
        ang = float(params['angle'])
    elif _num(d):
        ang = float(d)
    else:
        ang = {'right': 180.0, 'left': 0.0, 'up': 90.0, 'down': 270.0, 'rtl': 180.0, 'ltr': 0.0}.get(d, 180.0)
        if 'angle' in params and params.get('angle'):
            ang += float(params['angle'])
    return math.cos(math.radians(ang)), math.sin(math.radians(ang)), ang


def tr_whip(a, b, p, params, ctx):
    """whip (trans.whip) - digital whip pan: dir='right' (camera pans right, content moves left) | 'left' | 'up' |
    'down' | content angle; split=0.5 (share of the window before the cut); travel=1.2 (frame extents);
    ease=['inExpo','outExpo']; shutter=0.7; blur_max=0.4 (of the extent); seam_mix=1 (one dissolve frame inside
    the blur); mirrored edges."""
    a, b = _frames_or_color(a, b, params)
    h, w = a.shape[:2]
    vx, vy, ang = _dir_vec(params, 'right')
    ext = abs(vx) * w + abs(vy) * h
    tr = float(params.get('travel', 1.2))
    es = params.get('ease', ['inExpo', 'outExpo'])
    sh = float(params.get('shutter', 0.7))
    bmax = float(params.get('blur_max', 0.4)) * ext
    side, u, du = _side(p, params, ctx, float(params.get('split', 0.5)))

    def render(img, off, step):
        L = min(sh * abs(step), bmax)
        if L > 24:              # heavy smear: shift and blur at reduced resolution
            f = min(8.0, L / 16.0)
            xs = _down(img, f)
            ys = _warp(xs, np.float64([[1, 0, off * vx / f], [0, 1, off * vy / f]]))
            ys = dir_blur(ys, L / f, ang)
            return cv2.resize(ys, (w, h), interpolation=cv2.INTER_LINEAR)
        return dir_blur(_warp(img, np.float64([[1, 0, off * vx], [0, 1, off * vy]])), L, ang)
    if side == 'A':
        pos = tr * ease(u, es[0]) * ext
        prv = tr * ease(max(u - du, 0), es[0]) * ext
        return render(a, pos, pos - prv)
    pos = -tr * (1 - ease(u, es[1])) * ext
    prv = -tr * (1 - ease(max(u - du, 0), es[1])) * ext
    out = render(b, pos, pos - prv)
    if int(params.get('seam_mix', 1)) >= 1 and u <= du + 1e-6:
        pa = tr * ext
        pa0 = tr * ease(1 - du, es[0]) * ext
        out = cv2.addWeighted(out, 0.5, render(a, pa, pa - pa0), 0.5, 0)
    return out


def tr_zoom(a, b, p, params, ctx):
    """zoom (trans.zoom) - A zooms in x out_scale=3 (inExpo) to the cut with radial blur, B: mode='through' (continues
    in from 1/in_scale, in_scale=1.5, outExpo, mirrored edges) | 'punch' (from x1.35 back to 1, outCubic);
    center=[.5,.5] (A) / center_b; split=0.55; shutter=0.5; filler='white' + filler_frames (cut frames washed)."""
    a, b = _frames_or_color(a, b, params)
    h, w = a.shape[:2]
    side, u, du = _side(p, params, ctx, float(params.get('split', 0.55)))
    es = params.get('ease', ['inExpo', 'outExpo'])
    sh = float(params.get('shutter', 0.5))
    if side == 'A':
        cx, cy = params.get('center', [0.5, 0.5])
        L = math.log(float(params.get('out_scale', 3.0)))
        l1, l0 = L * ease(u, es[0]), L * ease(max(u - du, 0), es[0])
        img = a
    else:
        cx, cy = params.get('center_b', params.get('center', [0.5, 0.5]))
        if params.get('mode', 'through') == 'punch':
            L = math.log(float(params.get('in_scale', 1.35)))
            l1, l0 = L * (1 - ease(u, 'outCubic')), L * (1 - ease(max(u - du, 0), 'outCubic'))
        else:
            L = math.log(float(params.get('in_scale', 1.5)))
            l1, l0 = -L * (1 - ease(u, es[1])), -L * (1 - ease(max(u - du, 0), es[1]))
        img = b
    M = cv2.getRotationMatrix2D((cx * w, cy * h), 0, math.exp(l1))
    G = cv2.getRotationMatrix2D((cx * w, cy * h), 0, math.exp((l0 - l1) * sh))
    y = warp_blur(img, M, G, 16 if abs(l0 - l1) > 0.15 else 8)
    ff = int(params.get('filler_frames', 0))
    if params.get('filler') == 'white' and ff:
        if (side == 'A' and u >= 1 - du * (ff / 2.0) + 1e-6) or (side == 'B' and u <= du * (ff - ff // 2) + 1e-6):
            y = cv2.addWeighted(y, 0.25, _solid(h, w, (1, 1, 1)), 0.75, 0)
    return y


def tr_spin(a, b, p, params, ctx):
    """spin (trans.spin) - A rolls 0 -> out_angle=120 deg with scale 1 -> 1.4 (inCubic), cut, B from in_angle=-120 ->
    0, scale 1.4 -> 1 (outCubic); dir='cw'|'ccw'; center=[.5,.5]; split=0.4; shutter=0.75 (rotational blur)."""
    a, b = _frames_or_color(a, b, params)
    h, w = a.shape[:2]
    side, u, du = _side(p, params, ctx, float(params.get('split', 0.4)))
    sg = -1.0 if params.get('dir', 'cw') == 'cw' else 1.0
    es = params.get('ease', ['inCubic', 'outCubic'])
    sc = math.log(float(params.get('scale', 1.4)))
    cx, cy = params.get('center', [0.5, 0.5])
    sh = float(params.get('shutter', 0.75))
    if side == 'A':
        A_ = float(params.get('out_angle', 120.0))
        e1, e0 = ease(u, es[0]), ease(max(u - du, 0), es[0])
        th1, th0 = A_ * e1, A_ * e0
        s1, s0 = sc * e1, sc * e0
        img = a
    else:
        A_ = float(params.get('in_angle', -120.0))
        e1, e0 = ease(u, es[1]), ease(max(u - du, 0), es[1])
        th1, th0 = A_ * (1 - e1), A_ * (1 - e0)
        s1, s0 = sc * (1 - e1), sc * (1 - e0)
        img = b
    M = cv2.getRotationMatrix2D((cx * w, cy * h), sg * th1, math.exp(s1))
    dth = sg * (th0 - th1) * sh
    G = cv2.getRotationMatrix2D((cx * w, cy * h), float(dth), math.exp((s0 - s1) * sh))
    return warp_blur(img, M, G, 16 if abs(dth) > 8 else 8)


def _shape_dist(h, w, shape, center, params):
    """Normalised distance field for wipe shapes (1.0 ~ just covers the frame from the centre)."""
    key = ('shape', h, w, shape, tuple(center), params.get('points', 5), params.get('inner', 0.45))
    st = _state(key)
    if not st:
        gx, gy = _grid(h, w)
        X = (gx - center[0] * w) / F32(h)
        Y = (gy - center[1] * h) / F32(h)
        cxp, cyp = center[0] * w, center[1] * h
        far = max(math.hypot(cxp - xx, cyp - yy) for xx in (0, w) for yy in (0, h)) / h
        if shape in ('circle', 'iris'):
            d = cv2.magnitude(X, Y) / F32(far)
        elif shape == 'diamond':
            farl1 = max(abs(cxp - xx) + abs(cyp - yy) for xx in (0, w) for yy in (0, h)) / h
            d = (np.abs(X) + np.abs(Y)) / F32(farl1)
        elif shape == 'star':          # straight-edged star polygon, one point up
            npt = int(params.get('points', 5))
            inner = float(params.get('inner', 0.45))
            r = cv2.magnitude(X, Y)
            sec = 2 * math.pi / npt
            s = (np.arctan2(Y, X) + F32(math.pi / 2)) % F32(sec)
            s = np.minimum(s, F32(sec) - s)                     # fold to [0, pi/n]: outer vertex at 0, inner at pi/n
            dxe, dye = inner * math.cos(sec / 2) - 1.0, inner * math.sin(sec / 2)
            rs = F32(dye) / (np.cos(s) * F32(dye) - np.sin(s) * F32(dxe))
            d = r / rs / F32(far / inner)
        elif shape == 'box':
            d = np.maximum(np.abs(X) / F32(w / h / 2), np.abs(Y) / F32(0.5))
        else:
            d = cv2.magnitude(X, Y) / F32(far)
        st['d'] = d.astype(F32)
    return st['d']


def tr_wipe(a, b, p, params, ctx):
    """wipe (trans.wipe / trans.iris) - shape='linear' (dir='rtl'|'ltr'|'ttb'|'btt' or angle, feather=0.08) |
    'circle'|'iris'|'diamond'|'star'|'box' (mode='open' grows B from center, r0=0.08..r1=1.0 of the cover radius,
    ease 'linear', feather=0 (hard antialiased edge); mode='close' shrinks A (scale_content=True)) | 'clock' (radial
    sweep) | 'barn' (split from the centre, axis='h'|'v') | 'strips' (count=7, angle = frame diagonal, ease outQuad)
    | 'lids' (eyelids close/open: close=0.35, hold=0.15 shares of the window, feather 0.1) | 'occluder' (a dark or
    light out-of-focus pass: tone='dark'|'light', width=1.3, blur=0.1, ease inOutQuad, full cover at the cut)."""
    a, b = _frames_or_color(a, b, params)
    h, w = a.shape[:2]
    shape = params.get('shape', 'linear')
    e = ease(p, params.get('ease', 'linear' if shape in ('circle', 'iris', 'diamond', 'star', 'box') else 'inOutQuad'))
    fe = float(params.get('feather', 0.0 if shape in ('circle', 'iris', 'diamond', 'star', 'box') else 0.08))
    gx, gy = _grid(h, w)
    if shape in ('circle', 'iris', 'diamond', 'star', 'box'):
        c = params.get('center', [0.5, 0.5])
        d = _shape_dist(h, w, 'circle' if shape == 'iris' else shape, c, params)
        aa = 1.5 / min(h, w)
        if params.get('mode', 'open') == 'close':
            r0, r1 = float(params.get('r0', 0.65)), float(params.get('r1', 0.0))
            r = r0 + (r1 - r0) * e
            src = a
            if params.get('scale_content', True) and r > 1e-3:
                s = r / r0
                src = _warp(a, cv2.getRotationMatrix2D((c[0] * w, c[1] * h), 0, s), border='black')
            m = np.clip((r - d) / F32(max(fe, aa)) + 0.5, 0, 1).astype(F32)
            return _mix(b, src, m)
        r0, r1 = float(params.get('r0', 0.08)), float(params.get('r1', 1.0))
        r = r0 + (r1 + fe - r0) * e if p > 0 else 0.0
        m = np.clip((r - d) / F32(max(fe, aa)) + 0.5, 0, 1).astype(F32)
        return _mix(a, b, m)
    if shape == 'clock':
        c = params.get('center', [0.5, 0.5])
        ang = (np.arctan2(gy - c[1] * h, gx - c[0] * w) + F32(math.pi / 2)) % F32(2 * math.pi) / F32(2 * math.pi)
        m = np.clip((F32(e * (1 + fe)) - ang) / F32(max(fe, 1e-3)), 0, 1).astype(F32)
        return _mix(a, b, m)
    if shape == 'barn':
        if params.get('axis', 'v') == 'v':
            dd = np.abs(gx - w / 2) / F32(w / 2)
        else:
            dd = np.abs(gy - h / 2) / F32(h / 2)
        m = np.clip((F32(e * (1 + fe)) - dd) / F32(max(fe, 1e-3)), 0, 1).astype(F32)
        return _mix(a, b, m)
    if shape == 'strips':
        cnt = int(params.get('count', 7))
        an = math.atan2(h, w) if params.get('angle') is None else math.radians(float(params['angle']))
        nx, ny = -math.sin(an), math.cos(an)
        proj = gx * F32(nx) + gy * F32(ny)
        pmin, pmax = float(proj.min()), float(proj.max())
        q = (proj - F32(pmin)) / F32(pmax - pmin) * F32(cnt)
        si = np.floor(q)
        loc = q - si
        e2 = ease(p, params.get('ease', 'outQuad'))
        stag = float(params.get('stagger', 0.5))
        prog = np.clip(F32(e2 * (1 + stag)) - si / F32(cnt) * F32(stag), 0, 1)
        m = (loc < prog).astype(F32)
        return _mix(a, b, m)
    if shape == 'lids':
        cl, ho = float(params.get('close', 0.35)), float(params.get('hold', 0.15))
        fe = float(params.get('feather', 0.1))
        if p < cl:
            cov, img = ease(p / cl, 'inQuad'), a
        elif p < cl + ho:
            cov, img = 1.0, a
        else:
            cov, img = 1.0 - ease((p - cl - ho) / max(1 - cl - ho, 1e-6), 'outQuad'), b
        if cov >= 0.999:
            return _solid(h, w, (0, 0, 0))
        # each lid edge sits at distance (0.5 + fe) * (1 - cov) - fe/2 from the frame centre line
        edge = (0.5 + fe) * (1.0 - cov) - fe / 2
        dy = np.abs(gy / F32(h) - 0.5)
        m = np.clip((dy - F32(edge)) / F32(max(fe, 1e-3)) + 0.5, 0, 1).astype(F32)
        return _mix(img, _solid(h, w, (0, 0, 0)), m)
    if shape == 'occluder':
        return _occluder(a, b, p, params, ctx)
    vx, vy, ang = _dir_vec(params, 'rtl')      # direction the edge travels; B is behind the edge
    proj = (gx / F32(w)) * F32(vx) + (gy / F32(h)) * F32(vy)
    pmin, pmax = float(proj.min()), float(proj.max())
    pr = (proj - F32(pmin)) / F32(pmax - pmin)
    edge = -fe + (1 + 2 * fe) * e
    m = np.clip((F32(edge) - pr) / F32(max(fe, 1.0 / max(w, h))) + 0.5, 0, 1).astype(F32)
    return _mix(a, b, m)


def _occluder(a, b, p, params, ctx):
    h, w = a.shape[:2]
    vx, vy, ang = _dir_vec(params, 'rtl')
    tone = params.get('tone', 'dark')
    col = (0.06, 0.06, 0.07) if tone == 'dark' else (0.82, 0.8, 0.78)
    width = float(params.get('width', 1.3))
    bl = float(params.get('blur', 0.1))
    e = ease(p, params.get('ease', 'inOutQuad'))
    hq, wq = max(8, h // 4), max(8, w // 4)
    gx, gy = _grid(hq, wq)
    proj = (gx / F32(wq)) * F32(vx) + (gy / F32(hq)) * F32(vy)
    pmin, pmax = float(proj.min()), float(proj.max())
    pr = (proj - F32(pmin)) / F32(pmax - pmin)
    lead = -bl + (1 + width + 2 * bl) * e
    trail = lead - width
    occ = np.clip((F32(lead) - pr) / F32(bl) + 0.5, 0, 1) * np.clip((pr - F32(trail)) / F32(bl) + 0.5, 0, 1)
    behind = np.clip((F32(trail + bl / 2) - pr) / F32(bl), 0, 1).astype(F32)
    base = _mix(a, b, cv2.resize(behind, (w, h), interpolation=cv2.INTER_LINEAR))
    st = _state(('occl', hq, wq))
    if not st:
        st['nz'] = (1.0 + 0.06 * _vfield(hq, wq, 6, 3)).astype(F32)
    occ_img = (np.asarray(col, F32)[None, None, :] * st['nz'][..., None]).astype(F32)
    occ_img = cv2.resize(occ_img, (w, h), interpolation=cv2.INTER_LINEAR)
    return _mix(base, occ_img, cv2.resize((occ * 0.97).astype(F32), (w, h), interpolation=cv2.INTER_LINEAR))


def tr_luma(a, b, p, params, ctx):
    """luma (trans.liquid luma / burn) - B appears where A is darkest first: source='A'|'noise'; order='dark_first'|
    'light_first'; softness=0.08; noise={scale:0.05, amount:0.15}; curve='linear'; burn: source='noise', scale=0.04,
    edge='grain', dip='black' (brightness dips to ~18/255 mid-way, burnt rim)."""
    a, b = _frames_or_color(a, b, params)
    h, w = a.shape[:2]
    S = min(h, w)
    e = ease(p, params.get('curve', 'linear' if params.get('source', 'A') == 'A' else 'inOutCubic'))
    sd = _seed('luma', params.get('seed', 0), _wstart(ctx))
    nz = params.get('noise', {'scale': 0.05, 'amount': 0.15})
    hs, ws = max(8, h // 4), max(8, w // 4)
    if params.get('source', 'A') == 'noise':
        key = ('lumanoise', sd, hs, ws)
        st = _state(key)
        if 'k' not in st:
            v = _vfield(hs, ws, float(params.get('scale', 0.04)) * S / 4, sd, 3)
            st['k'] = ((v - v.min()) / max(float(v.max() - v.min()), 1e-6)).astype(F32)
        kv = st['k']
    else:
        kv = _luma(_down(a, 4))
        if params.get('order', 'dark_first') == 'light_first':
            kv = 1.0 - kv
        if nz:
            st = _state(('lumafield', sd, hs, ws))
            if 'n' not in st:
                st['n'] = _vfield(kv.shape[0], kv.shape[1], float(nz.get('scale', 0.05)) * S / 4, sd, 2)
            kv = kv + st['n'][:kv.shape[0], :kv.shape[1]] * F32(float(nz.get('amount', 0.15)) * 0.5)
        lo, hi = np.percentile(kv, [1, 99])
        kv = np.clip((kv - lo) / max(hi - lo, 1e-6), 0, 1).astype(F32)
    sf = float(params.get('softness', 0.08))
    thr = -sf + (1 + 2 * sf) * e
    m = np.clip((F32(thr) - kv) / F32(sf) + 0.5, 0, 1).astype(F32)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
    out = _mix(a, b, m)
    if params.get('dip') == 'black' or params.get('edge') == 'grain':
        rim = np.clip(1 - np.abs(F32(thr) - kv) / F32(sf * 1.5), 0, 1).astype(F32)
        rim = cv2.resize(rim, (w, h), interpolation=cv2.INTER_LINEAR)
        if params.get('edge') == 'grain':
            gr = _hash_u01(sd, np.arange(h * w // 16)).reshape(h // 4, w // 4).astype(F32)
            gr = cv2.resize(gr, (w, h), interpolation=cv2.INTER_NEAREST)
            rim = rim * (0.6 + 0.8 * gr)
        burn = color(params.get('rim_color', '#2a0d02'))
        out = _mix(out, _solid(h, w, burn), np.clip(rim, 0, 1).astype(F32))
        if params.get('dip') == 'black':
            dip = 1.0 - 0.6 * math.sin(math.pi * e)
            out = out * F32(dip)
    return _clip01(_f32(out))


def tr_liquid(a, b, p, params, ctx):
    """liquid (trans.liquid) - mode='blob' (one soft drop grows from the darkest region of A, radius outCubic,
    wobble=0.04, rim={width:0.015, glow:0.7}) | 'melt' (whole frame ripples like glass: amp peak 0.015 W at the
    middle, scale=0.1, A and B mixed linearly; light_peak=None|240) | 'luma'/'burn' (see luma)."""
    mode = params.get('mode', 'blob')
    if mode in ('luma', 'burn'):
        pp = dict(params)
        if mode == 'burn':
            pp.update(source='noise', edge='grain', dip='black')
        return tr_luma(a, b, p, pp, ctx)
    a, b = _frames_or_color(a, b, params)
    h, w = a.shape[:2]
    S = min(h, w)
    ws_ = _wstart(ctx)
    sd = _seed('liquid', params.get('seed', 0), ws_)
    if mode == 'melt':
        amp = math.sin(math.pi * min(max(p, 0), 1)) * float(params.get('amp', 0.015)) * w * 3.0
        st = _state(('melt', sd, h // 4, w // 4))
        if 'fx' not in st:
            sc = float(params.get('scale', 0.1)) * S / 4
            st['fx'] = _vfield(h // 4 * 2 + 8, w // 4 * 2 + 8, sc, sd + 1, 2)
            st['fy'] = _vfield(h // 4 * 2 + 8, w // 4 * 2 + 8, sc, sd + 2, 2)
        t = p * 6.0
        fxs = _field_at(st['fx'], t * 7, t * 5, h // 4, w // 4)
        fys = _field_at(st['fy'], t * 6 + 11, t * 8 + 3, h // 4, w // 4)
        gx, gy = _grid(h, w)
        mx = cv2.scaleAdd(cv2.resize(fxs, (w, h), interpolation=cv2.INTER_LINEAR), float(amp), gx)
        my = cv2.scaleAdd(cv2.resize(fys, (w, h), interpolation=cv2.INTER_LINEAR), float(amp), gy)
        aw = cv2.remap(a, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
        bw = cv2.remap(b, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
        out = _lerp(aw, bw, ease(p, params.get('curve', 'linear')))
        lp = params.get('light_peak')
        if lp:
            out = _lerp(out, _solid(h, w, (1, 1, 1)), math.sin(math.pi * p) ** 4 * float(lp) / 255.0)
        return out
    st = _state(('blob', sd))
    if 'c' not in st:
        L = cv2.GaussianBlur(_luma(_down(a, 8)), (0, 0), 3)
        thr = np.percentile(L, 15)
        ys, xs = np.nonzero(L <= thr)
        if len(xs):
            st['c'] = (float(xs.mean()) * 8 / w, float(ys.mean()) * 8 / h)
        else:
            st['c'] = (0.5, 0.5)
    c = params.get('center') or st['c']
    q = 4
    hq, wq = max(8, h // q), max(8, w // q)
    gx, gy = _grid(hq, wq)
    X, Y = gx - F32(c[0] * wq), gy - F32(c[1] * hq)
    far = max(math.hypot(c[0] * wq - xx, c[1] * hq - yy) for xx in (0, wq) for yy in (0, hq))
    r = far * 1.08 * ease(p, params.get('ease', 'outCubic'))
    wob = float(params.get('wobble', 0.04))
    ph = np.arctan2(Y, X)
    rs = _rng(sd, 'wob')
    mod = np.zeros_like(ph)
    for kk, amp_ in ((3, 1.0), (5, 0.6), (8, 0.35)):
        mod += F32(amp_) * np.sin(F32(kk) * ph + F32(rs.uniform(0, 2 * math.pi) + p * kk))
    dd = cv2.magnitude(X, Y) / (1 + F32(wob) * mod / 1.95)
    soft = max(0.006 * S / q, 0.75)
    m = np.clip((F32(r) - dd) / F32(soft) + 0.5, 0, 1).astype(F32)
    out = _mix(a, b, cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR))
    rim = params.get('rim', {'width': 0.015, 'glow': 0.7})
    if rim and 0 < r < far * 1.05:
        rw = max(float(rim.get('width', 0.015)) * S / q, 0.75)
        band = np.clip(1 - np.abs(dd - F32(r)) / F32(rw), 0, 1).astype(F32)
        band = cv2.resize(band, (w, h), interpolation=cv2.INTER_LINEAR)
        out = _mix(out, _solid(h, w, (1, 1, 1)), band * F32(float(rim.get('glow', 0.7))))
    return out


def tr_lens(a, b, p, params, ctx):
    """lens (trans.lens_distort) - mode='bulge' (peak M=2.4) | 'pinch' (M=0.55) | 'twirl' (theta=300, dir='cw') |
    'barrel' (k1=0.9, k2=0.05, fill auto) | 'pincushion' (k1=-0.4); out=6/in=7 frames @25 split (inCubic /
    outCubic); from='mirror'|'through'; center, radius=1.0; blur samples=4 (sub-frames between neighbouring
    strengths, 1/2 res); chroma=0.04 and vignette=0.25 on the frames near the peak."""
    a, b = _frames_or_color(a, b, params)
    h, w = a.shape[:2]
    mode = params.get('mode', 'bulge')
    o, i_ = int(params.get('out', 6)), int(params.get('in', 7))
    side, u, du = _side(p, params, ctx, o / float(o + i_))
    pk = params.get('peak') or {}
    c = params.get('center', [0.5, 0.5])
    R = float(params.get('radius', 1.0))
    dr = -1.0 if params.get('dir', 'cw') == 'cw' else 1.0
    through = params.get('from', 'mirror') == 'through'
    if mode in ('bulge', 'pinch'):
        Mp = float(pk.get('M', 2.4 if mode == 'bulge' else 0.55))
        lnM = math.log(Mp)
    elif mode == 'twirl':
        Mp = float(pk.get('theta', 300.0))
    else:
        Mp = float(pk.get('k1', 0.9 if mode == 'barrel' else -0.4))

    def strength(side_, uu):
        if side_ == 'A':
            e = ease(uu, 'inCubic')
            if mode in ('bulge', 'pinch'):
                return math.exp(lnM * e)
            return Mp * e
        e = 1 - ease(uu, 'outCubic')
        if mode in ('bulge', 'pinch'):
            return math.exp((-lnM if through else lnM) * e)
        if mode == 'twirl':
            return -Mp * e
        return Mp * e

    lm = 'twirl' if mode == 'twirl' else ('barrel' if mode in ('barrel', 'pincushion') else 'bulge')
    k2 = float(pk.get('k2', 0.05)) if lm == 'barrel' else 0.0

    def fill_of(s):
        if lm != 'barrel':
            return 1.0
        f_ = pk.get('fill', 'auto')
        return barrel_fill(s, k2, h, w) if (f_ == 'auto' and s > 0) else (float(f_) if _num(f_) else 1.0)
    img = a if side == 'A' else b
    s1, s0 = strength(side, u), strength(side, max(u - du, 0))
    ns = int((params.get('blur') or {}).get('samples', 4))
    near = (side == 'A' and u > 0.5) or (side == 'B' and u < 0.5)
    if ns > 1 and near:
        hs = _down(img, 2)
        acc = None
        for v in np.linspace(0, 1, ns):
            s = s0 + (s1 - s0) * v if lm != 'bulge' else math.exp(math.log(s0) + (math.log(s1) - math.log(s0)) * v)
            y = lens_warp_frame(hs, lm, s, c, R, k2, fill_of(s), dr, half=True)
            acc = y if acc is None else cv2.add(acc, y, dst=acc)
        out = cv2.resize(acc * F32(1.0 / ns), (w, h), interpolation=cv2.INTER_LINEAR)
    else:
        out = lens_warp_frame(img, lm, s1, c, R, k2, fill_of(s1), dr)
    peakness = u if side == 'A' else 1 - u
    if peakness > 0.66:
        ch = float(params.get('chroma', 0.04)) * 0.25
        if ch > 0:     # colour fringe growing to the edges: R and B scaled +-ch about the lens centre
            out = fx_rgb_split(out, dict(mode='radial', k=ch * peakness, center=list(c)), 0, 1,
                               dict(ow=w, oh=h, fps=_fps(ctx)))
        vg = float(params.get('vignette', 0.25))
        if vg > 0:
            out = cv2.multiply(out, _gray3(_vig_mask(h, w, vg * peakness)))
    return out


def tr_glitch(a, b, p, params, ctx):
    """glitch (fx.glitch transition) - streaks='vertical': columns of A drip down revealing B (5-6 frames), glitch
    states (slices, rgb) around the cut, B settles from a decaying burst; split=0.5; intensity=0.8; seed."""
    a, b = _frames_or_color(a, b, params)
    h, w = a.shape[:2]
    side, u, du = _side(p, params, ctx, float(params.get('split', 0.5)))
    ws_ = _wstart(ctx)
    sd = _seed('trglitch', params.get('seed', 0), ws_)
    I = float(params.get('intensity', 0.8))
    j = int(round(u / max(du, 1e-6)))
    if side == 'A':
        if params.get('streaks', 'vertical') == 'vertical':
            cw = max(2, int(6 * min(h, w) / 1080.0))
            nc = w // cw + 1
            spd = 0.8 + 0.9 * _hash_u01(sd, np.arange(nc))             # columns drip at different speeds
            dl = np.clip(u * spd - 0.3 * _hash_u01(sd + 1, np.arange(nc)), 0, None) ** 2.2 * h
            drow = np.repeat(dl, cw)[:w].astype(F32)
            gx, gy = _grid(h, w)
            my = gy - drow[None, :]
            aw = cv2.remap(a, gx, my, cv2.INTER_NEAREST, borderMode=cv2.BORDER_REPLICATE)
            m = (gy < drow[None, :]).astype(F32)
            out = _mix(aw, b, m)
        else:
            out = a
        if u > 0.5:
            out = glitch_frame(out, _seed(sd, j), I * u, ('slices', 'rgb'), min(h, w) / 1080.0, invert_ok=False)
        return out
    if u < 0.6:
        return glitch_frame(b, _seed(sd, 'b', j), I * (1 - u), ('slices', 'rgb', 'blocks'), min(h, w) / 1080.0,
                            invert_ok=False)
    return b


def tr_pixel_sort(a, b, p, params, ctx):
    """pixel_sort transition (glitch.pixel_sort) - out=4 / peak=2 / in=5 frames: A sorts with lo 0.95 -> 0 (full
    sort), cut at the peak, B from lo 0 -> 0.95; mask='band'|'bright', axis='y', dir='down', work_res=540."""
    a, b = _frames_or_color(a, b, params)
    o, pk, i_ = int(params.get('out', 4)), int(params.get('peak', 2)), int(params.get('in', 5))
    tot = o + pk + i_
    side, u, du = _side(p, params, ctx, (o + pk / 2.0) / tot)
    if side == 'A':
        lo = 0.95 * (1 - ease(min(u * (o + pk / 2.0) / o, 1.0), 'outQuad'))
        img = a
    else:
        nb = i_ + pk / 2.0
        uu = max(0.0, (u * nb - pk / 2.0) / i_)
        lo = 0.95 * ease(uu, 'inQuad')
        img = b
    if lo >= 0.95:
        return img
    mask = params.get('mask', 'bright')
    return pixel_sort_frame(img, mask, lo, 1.0, params.get('axis', 'y'), params.get('dir', 'down'), 'luma', None,
                            0.01, 1.0 if lo < 0.05 else 0.6, (0.02, 0.25), 0.45, 0.04, params.get('work_res', 540),
                            'bicubic', _seed('trps', _wstart(ctx)), None, True)


def tr_light_leak(a, b, p, params, ctx):
    """light_leak / leak transition (fx.light_leak mode='transition') - a burst leak grows from anchor='right' over
    attack=8 frames @25, holds 3 frames around the cut (at the maximum) and fades over release=10 frames; palette
    'amber', peak 1.3, size 0.95 S, blend 'add'."""
    a, b = _frames_or_color(a, b, params)
    fps = _fps(ctx)
    env = dict(params.get('env') or {})
    sc = fps / 25.0
    att, hold, rel = env.get('attack', 8) * sc, env.get('hold', 3) * sc, env.get('release', 10) * sc
    tot = att + hold + rel
    pos = _tpos(p, params, ctx, (att + hold / 2) / tot)
    if pos is None:
        j = int(round(p * tot - 0.5))
        js = int(round(att + hold / 2))
    else:
        j, N, js = pos
    d = j - js
    hl = int(round(hold))
    h0 = -(hl // 2)
    if d < h0:
        ev = ease((d - h0 + att + 1) / (att + 1), 'inQuad')
    elif d < h0 + hl:
        ev = 1.0
    else:
        ev = 1.0 - ease((d - h0 - hl + 1) / (rel + 1), 'outQuad')
    ev = max(0.0, min(1.0, ev))
    img = a if d < 0 else b
    fxp = dict(mode='transition', shape=params.get('shape', 'burst'), anchor=params.get('anchor', 'right'),
               palette=params.get('palette', 'amber'), peak=params.get('peak', 1.3), size=params.get('size', 0.95),
               blend=params.get('blend', 'add'), seed=params.get('seed', 0) + _wstart(ctx) % 997)
    h, w = img.shape[:2]
    if ev <= 1e-3:
        return img
    lay_s = _leak_layer(fxp, ev, _abs_frame(ctx, None), ctx, max(8, h // 4), max(8, w // 4))
    lay = None if fxp['blend'] == 'add' else cv2.resize(lay_s, (w, h), interpolation=cv2.INTER_LINEAR)
    out = _blend_layer(img, lay, fxp['blend'], lay_s)
    return _clip01(_dither(out, _abs_frame(ctx, None)))


def tr_push(a, b, p, params, ctx):
    """push / slide - dir='left' (B enters from the right moving left) | 'right' | 'up' | 'down'; push: both move;
    slide: B slides over a static A (reveal=True: A slides off over B); ease='inOutCubic'; shutter=0.5 directional
    blur; divider={width:0.0, color:'#000000'}."""
    a, b = _frames_or_color(a, b, params)
    h, w = a.shape[:2]
    d = params.get('dir', 'left')
    sgn, axis = {'left': (-1, 1), 'right': (1, 1), 'up': (-1, 0), 'down': (1, 0)}.get(d, (-1, 1))
    ext = w if axis == 1 else h
    es = params.get('ease', 'inOutCubic')
    pos = _tpos(p, params, ctx, 0.5)
    dp = (1.0 / pos[1]) if pos else 0.08
    e, e0 = ease(p, es), ease(p - dp, es)
    kind = params.get('_kind', 'push')
    sh = float(params.get('shutter', 0.5))
    dv = params.get('divider') or {}
    dw = int(round(float(dv.get('width', 0.0)) * ext)) if kind == 'push' else 0
    span = ext + dw                        # A | divider | B strip travels this far
    off = int(round(e * span))
    blur = sh * abs(e - e0) * span
    ang = 0 if axis == 1 else 90

    def blit(dst, src, shift):             # src displaced by `shift` px along the axis (integer, crisp)
        if abs(shift) >= ext:
            return
        sl_d = [slice(None)] * 2
        sl_s = [slice(None)] * 2
        if shift >= 0:
            sl_d[axis], sl_s[axis] = slice(shift, ext), slice(0, ext - shift)
        else:
            sl_d[axis], sl_s[axis] = slice(0, ext + shift), slice(-shift, ext)
        dst[tuple(sl_d)] = src[tuple(sl_s)]

    def mv(img):
        return dir_blur(img, blur, ang) if blur > 1.5 else img
    if kind == 'slide' and params.get('reveal'):
        out = b.copy()
        blit(out, mv(a), sgn * off)
        return out
    if kind == 'slide':
        out = a.copy()
    else:
        out = _solid(h, w, color(dv.get('color', '#000000'))) if dw else np.empty_like(a)
        blit(out, mv(a), sgn * off)
    blit(out, mv(b), sgn * (off - span))
    return out


def tr_slide(a, b, p, params, ctx):
    """slide - see push (B slides over A; reveal=True slides A off)."""
    pp = dict(params)
    pp['_kind'] = 'slide'
    return tr_push(a, b, p, pp, ctx)


def tr_datamosh(a, b, p, params, ctx):
    """datamosh transition (glitch.datamosh method='flow') - the cut has no key frame: A's pixels move in blocks along
    B's motion; refresh grows inQuad 0.02 -> 1 over the B frames; holes=0.0; sequential (falls back to dissolve)."""
    a, b = _frames_or_color(a, b, params)
    side, u, du = _side(p, params, ctx, float(params.get('split', 0.0)))
    if side == 'A':
        return a
    f = int(ctx.get('f_abs', 0) or 0)
    st = _state(('trmosh', _wstart(ctx)))
    g = cv2.cvtColor(cv2.convertScaleAbs(_down(b, 2), alpha=255), cv2.COLOR_RGB2GRAY)
    refresh = 0.02 + 0.98 * ease(u, 'inQuad')
    if st.get('f') != f - 1:
        # first incoming frame: no key frame - A stays on screen; later frames move A's blocks along B's own motion.
        # Out of order (stills / partial renders): stateless block refresh of A by B, then continue from there.
        if u <= du + 1e-6:
            out = _f32(a).copy()
        else:
            h, w = a.shape[:2]
            blk = max(4, int(params.get('block', 16)) * 2)
            bh, bw = max(1, h // blk), max(1, w // blk)
            ids = np.arange(bh * bw).reshape(bh, bw)
            m = cv2.resize((_hash_u01(_seed('trm', _wstart(ctx)), ids) < refresh).astype(F32), (w, h),
                           interpolation=cv2.INTER_NEAREST)
            out = _mix(a, b, m)
        st.update(f=f, out=out, g=g)
        return out
    out, _ = mosh_step(st['out'], st['g'], b, g, int(params.get('block', 16)), refresh, _seed('trm', f),
                       float(params.get('holes', 0.0)))
    st.update(f=f, out=out, g=g)
    return out


TRANSITIONS = {'dissolve': tr_dissolve, 'dip': tr_fade, 'fade': tr_fade, 'flash': tr_flash, 'whip': tr_whip,
               'zoom': tr_zoom, 'spin': tr_spin, 'wipe': tr_wipe, 'luma': tr_luma, 'lens': tr_lens,
               'glitch': tr_glitch, 'pixel_sort': tr_pixel_sort, 'light_leak': tr_light_leak, 'liquid': tr_liquid,
               'push': tr_push, 'slide': tr_slide, 'datamosh': tr_datamosh}
_TR_ALIAS = {'leak': 'light_leak', 'iris': 'wipe', 'cross': 'dissolve', 'crossfade': 'dissolve', 'mix': 'dissolve',
             'lens_distort': 'lens', 'burn': 'liquid', 'melt': 'liquid', 'blob': 'liquid', 'mosh': 'datamosh',
             'swish': 'whip', 'whip_pan': 'whip', 'roll': 'spin', 'pixelsort': 'pixel_sort'}
_TR_ARG = {'dip': 'color', 'fade': 'color', 'wipe': 'shape', 'lens': 'mode', 'liquid': 'mode', 'luma': 'order',
           'flash': 'color', 'whip': 'dir', 'push': 'dir', 'slide': 'dir', 'zoom': 'mode', 'spin': 'dir'}
_TR_DEFAULTS = {'dip': dict(out=0.16, hold=0.04, **{'in': 0.24}), 'iris': dict(shape='circle'),
                'burn': dict(mode='burn'), 'melt': dict(mode='melt'), 'blob': dict(mode='blob')}


def seam_fraction(kind, params=None, fps=25.0):
    """Natural share of a transition window before its cut (renderer: tseam = round(frames * this) when the window
    is laid out freely; 'center' alignment uses frames // 2)."""
    params = params or {}
    base = kind.split('(')[0].strip()
    base = _TR_ALIAS.get(base, base)
    if base == 'lens':
        o, i_ = int(params.get('out', 6)), int(params.get('in', 7))
        return o / float(o + i_)
    if base == 'flash':
        pre = int(params.get('pre_frames', 0))
        c = flash_curve(fps, float(params.get('tau', 0.06)), int(params.get('peak_frames', 1)))
        return pre / float(pre + len(c))
    if base in ('spin',):
        return float(params.get('split', 0.4))
    if base in ('zoom',):
        return float(params.get('split', 0.55))
    if base == 'datamosh':
        return 0.0
    return float(params.get('split', 0.5))


def transition(kind, a, b, p, params=None, ctx=None):
    """Blend from the outgoing frame a into the incoming frame b at progress p (0..1) -> float32 frame.
    kind: name or 'name(arg)' (dip(#0b1020), wipe(circle), lens(twirl), liquid(melt), ...); params per kind (see
    TRANSITIONS[kind].__doc__); ctx: ow, oh, fps, f_abs, + tj, tn, tseam (frame-exact phases; see module doc).
    a or b may be None (= params color, e.g. fade in from black / out to black)."""
    params = dict(params or {})
    ctx = ctx or {}
    k = (kind or 'dissolve').strip()
    arg = None
    if '(' in k and k.endswith(')'):
        k, arg = k[:-1].split('(', 1)
        k, arg = k.strip(), arg.strip().strip('\'"')
    for dk, dv in _TR_DEFAULTS.get(k, {}).items():
        params.setdefault(dk, dv)
    base = _TR_ALIAS.get(k, k)
    if arg:
        params.setdefault(_TR_ARG.get(base, 'arg'), arg)
    if base == 'dip':
        params.setdefault('mode', 'dip')
    fn = TRANSITIONS.get(base, tr_dissolve)
    ref = a if a is not None else b
    if 'ow' not in ctx and ref is not None:
        ctx = dict(ctx, ow=ref.shape[1], oh=ref.shape[0])
    out = fn(a, b, float(p), params, ctx)
    return _f32(np.clip(out, 0, 1) if (out.max() > 1.0 or out.min() < 0.0) else out)


# ============================================================================= registry / apply
def _canon(t):
    if not t:
        return t
    t = str(t)
    if t in CAMERA_FX or t in FX_TYPES:
        return t
    if t in _CAM_ALIAS:
        return _CAM_ALIAS[t]
    if t in _IMG_ALIAS:
        return _IMG_ALIAS[t]
    return t


FX_TYPES = {
    'rgb_split': fx_rgb_split, 'glow': fx_glow, 'light_leak': fx_light_leak, 'film_overlay': fx_film_overlay,
    'pixel_sort': fx_pixel_sort, 'pixel_art': fx_pixel_art, 'pixelate': fx_pixelate, 'glitch': fx_glitch,
    'glitch_blocks': fx_glitch, 'datamosh': fx_datamosh, 'lens_warp': fx_lens_warp, 'letterbox': fx_letterbox,
    'duotone': fx_duotone, 'posterize': fx_posterize, 'vignette': fx_vignette, 'grain': fx_grain, 'bloom': fx_bloom,
    'dirblur': fx_dirblur, 'zoomblur': fx_zoomblur, 'chroma': fx_chroma, 'smear': fx_smear, 'blur': fx_blur,
    'shake': fx_shake_img, 'exposure': fx_exposure, 'invert': fx_invert, 'bleach': fx_bleach, 'flash': fx_flash,
    'contour_glow': fx_contour_glow, 'defocus': fx_defocus, 'clarity': fx_clarity, 'saturation': fx_saturation,
    'tape': fx_tape,
}
for _fn in set(FX_TYPES.values()):
    _fn.kind = 'image'
for _name, _fn in CAMERA_FX.items():
    _fn.kind = 'camera'
    FX_TYPES[_name] = _fn
for _a, _t in _CAM_ALIAS.items():
    FX_TYPES.setdefault(_a, CAMERA_FX[_t])
_IMG_ALIAS = {'fx.rgb_split': 'rgb_split', 'chroma_ab': 'rgb_split', 'fx.glow': 'glow', 'fx.light_leak': 'light_leak',
              'leak': 'light_leak', 'fx.film_overlay': 'film_overlay', 'film': 'film_overlay',
              'glitch.pixel_sort': 'pixel_sort', 'fx.pixel_art': 'pixel_art', 'fx.mosaic': 'pixelate',
              'mosaic': 'pixelate', 'fx.glitch': 'glitch', 'glitch.datamosh': 'datamosh', 'fx.letterbox': 'letterbox',
              'lens.vignette': 'vignette', 'lens.fisheye': 'lens_warp', 'lens_distort': 'lens_warp',
              'zoom_blur': 'zoomblur', 'outline_glow': 'contour_glow', 'rim_glow': 'contour_glow',
              'bg_blur': 'defocus', 'focus.shallow': 'defocus', 'lens_blur': 'defocus', 'local_contrast': 'clarity',
              'color_pop': 'saturation', 'desaturate': 'saturation', 'vhs': 'tape', 'look.vhs': 'tape'}
for _a, _t in _IMG_ALIAS.items():
    FX_TYPES.setdefault(_a, FX_TYPES[_t])
CAMERA_TYPES = set(CAMERA_FX) | set(_CAM_ALIAS)


# ============================================================================= machine-readable specs
# params: {name: default} with the defaults the code really uses (None = not set / derived from other params; see
# the callable's docstring); choices: allowed values of enumerated params. Checked by tests/test_fx.py: an fx given
# its listed non-None defaults renders exactly like the bare fx.
COMMON_FX_PARAMS = {
    'type': None, 'amt': 1.0, 'amt_to': None, 'amt_keys': None, 'ease': 'linear', 'frames': None, 'f': None,
    'k': None, 't': None, 'region': None, 'behind': False, 'feather': 0.004, 'expand': 0.0, 'auto_mask': True,
}
COMMON_FX_DOC = ('type: fx name or alias; amt: strength 0..1 (amt_to ramps it over the segment with ease, amt_keys '
                 '[[t_abs, v], ...] multiplies it); gates: frames (segment-relative k list or "a:b"), f (absolute '
                 'frames), k [k0, k1], t [t0, t1] absolute seconds (for animated fx t is the animation window); '
                 'region: "background" | "subject" (behind=true = background) limits an image fx to that part of the '
                 'picture using the subject matte (ctx mask from sources.<name>.mask, else person_mask, else an '
                 'automatic person matte unless auto_mask=false), feather / expand: matte edge (of the short side)')
_ENV_PULSE = {'attack': 0, 'hold': 1, 'tau': 2.0, 'decay': 'exp'}
_TIMES = ['beats', 'downbeats', '1/2', 'snare', '1/8', 'offbeat', '[t, ...]']
FX_SPECS = {
    # ---- camera fx (change the crop warp; camera() -> zoom, dx, dy, rot, blur)
    'zoom.punch': dict(
        kind='camera', desc='Digital punch-in x1.1-1.35 landing exactly on beat frames (bounce, hold, spring, ladder).',
        params=dict(times='beats', scale=1.2, mode='bounce', attack=0, release=0.32, release_frames=None,
                    cap_release=True, hold_until='cut', spring={'settle': 1.15, 'tau': 0.1, 'period': 0.2},
                    ladder={'step': 1.12, 'per': '1/4', 'reset': 'downbeat', 'max_total': 1.5}, center=[0.5, 0.5],
                    blur_shutter=0.5, **{'from': None}),
        choices=dict(mode=['bounce', 'hold', 'speech', 'spring', 'ladder', 'out'], attack=[0, 1, 2],
                     hold_until=['cut', 'next', 'next_beat', '<t>'], times=_TIMES)),
    'shake.beat': dict(
        kind='camera', desc='Beat-locked camera shake: full jolt on the beat frame, alternating rebound, exact rest.',
        params=dict(profile='impact', times='beats', amp=None, rot=None, tau=None, gamma=None, dir=None,
                    dtheta=30.0, rot_sign=1.0, smooth=1.0, seed=0, section=None, center=None, cover='auto',
                    env_t=None, release=0.12, blur_shutter=0.5),
        choices=dict(profile=['impact', 'heavy', 'micro', 'rot', 'kick_tilt', 'bass'],
                     dir=['bass_down', 'horizontal', 'random', 'up', '<deg>'],
                     cover=['auto', 'reframe', 'reflect', '<number>'], times=_TIMES)),
    'zoom.crash': dict(
        kind='camera', desc='Lightning zoom x2.5-9 over ~0.4 s toward a fixed point, landing on `at` and holding.',
        params=dict(scale=4.0, dur=0.4, at=None, t=None, ease='inOutCubic', stages=1, pause=3, back=None,
                    center=[0.5, 0.5], blur_shutter=0.5)),
    'zoom.in_out': dict(
        kind='camera', desc='Zoom in on the beat and back out (yoyo), half a beat each way by default.',
        params=dict(scale=1.3, times='beats', stroke=None, stroke_out=None, hold=0.0, cycles=None,
                    ease_in='outCubic', ease_out='inCubic', center=[0.5, 0.5], blur_shutter=None),
        choices=dict(times=_TIMES)),
    'roll': dict(
        kind='camera', desc='Digital camera roll between angles over t (or the segment) with auto cover zoom.',
        params=dict(angle=[0, 180], dir='ccw', t=None, ease='inOutCubic', scale='auto', blur_shutter=0.5),
        choices=dict(dir=['ccw', 'cw'])),
    'drift': dict(
        kind='camera', desc='Slow digital move: pan dx/dy, zoom and rotation keys over t, optional handheld wobble.',
        params=dict(dx=0.0, dy=0.0, zoom=1.0, rot=0.0, t=None, ease='linear', wobble=None, blur_shutter=0.0)),
    'handheld': dict(
        kind='camera', desc='Smooth handheld drift (calm, walk, chaos) with a constant cover zoom.',
        params=dict(profile='calm', amp=None, rot=None, freq=None, yfreq=None, seed=0, cover=None,
                    blur_shutter=0.5),
        choices=dict(profile=['calm', 'walk', 'chaos'])),
    # ---- image fx (work on the rendered float frame)
    'rgb_split': dict(
        kind='image', desc='Chromatic split: R and B shifted apart around G (linear, anaglyph, radial, motion, '
                           'temporal, jitter), constant or pulsed on events.',
        params=dict(px=8.0, angle=0.0, mode='linear', k=0.008, center=[0.5, 0.5], delay=1, vel=None, times=None,
                    env=_ENV_PULSE, alternate_sign=False, mix=1.0, soften=0.0, overscan=1.0, seed=0),
        choices=dict(mode=['linear', 'anaglyph', 'radial', 'motion', 'temporal', 'jitter'], times=_TIMES)),
    'glow': dict(
        kind='image', desc='Highlight bloom in their own colour (blacks stay black), optional pulses, breathe, '
                           'anamorphic streaks.',
        params=dict(threshold=0.72, knee=0.1, key='luma', radii=[0.004, 0.015, 0.04, 0.10],
                    weights=[0.35, 0.3, 0.2, 0.15], strength=0.3, tint=None, tint_mix=0.6, sat=1.0, blend='screen',
                    soft_clip=0.9, times=None, base=0.2, peak=1.0, radius_mul=1.6, breathe=None, streak=None),
        choices=dict(key=['luma', 'value', 'value_sat'], blend=['screen', 'add'], threshold=['<0..1>', 'p95'])),
    'light_leak': dict(
        kind='image', desc='Procedural warm film light leak (ambient window, accent pulse or transition burst).',
        params=dict(mode='ambient', at=None, env=None, shape='edge', anchor='left', palette='amber', peak=0.9,
                    size=0.32, falloff=1.5, elong=1.8, drift=[0.04, 0.02],
                    warp={'scale': 0.45, 'amount': 0.1, 'octaves': 3, 'speed': 0.04},
                    flicker={'amp': 0.08, 'hz': 1.5}, blend='screen', grain=0.03, dither=True, angle=30.0,
                    streak_speed=0.5, seed=0),
        choices=dict(mode=['ambient', 'accent', 'transition'], shape=['edge', 'corner', 'blob', 'streak', 'burst'],
                     anchor=['left', 'right', 'top', 'bottom', 'tl', 'tr', 'bl', 'br', 'center', '[x, y]'],
                     palette=['amber', 'magenta', 'gold', 'peach', 'cool', 'prism', '[core, mid, edge]'],
                     blend=['screen', 'add', 'lighten', 'soft_light'])),
    'film_overlay': dict(
        kind='image', desc='Procedural film texture without colour change: grain, dust, hair, scratches, flicker, '
                           'gate weave (levels 1-3).',
        params=dict(level=2, delivery='social', grain=None, size=None, corr=0.8, mono=False, dust=None, hair=None,
                    scratch=None, every=None, flicker=None, weave=None, weave_rot=None, seed=0),
        choices=dict(level=[1, 2, 3], delivery=['social', 'master'])),
    'pixel_sort': dict(
        kind='image', desc='Pixel sorting of column runs inside a luminance/edge mask, constant, pulsed or swept.',
        params=dict(mask='bright', lo=0.62, hi=None, axis=None, dir='down', angle=None, key='luma', min_len=0.01,
                    max_len=0.6, random_len=[0.02, 0.25], share=0.45, jitter=0.04, work_res=540, upscale='bicubic',
                    times=None, keys=None, pulse_ease=['outExpo', 'inQuad'], sweep=None, update='live',
                    freeze_frames=4, exclude_bars=True, edges=None, seed=0),
        choices=dict(mask=['bright', 'dark', 'band', 'edges', 'random', 'full'], axis=['y', 'x'],
                     dir=['down', 'up', 'left', 'right'], key=['luma', 'hue', 'sat', 'r', 'g', 'b'],
                     update=['live', 'hold2', 'freeze'], upscale=['bicubic', 'nearest'])),
    'pixel_art': dict(
        kind='image', desc='Integer screen-grid pixel art with a reduced palette (k-means or named), optional dither '
                           'and resolution ramp.',
        params=dict(block=0.008, px=None, prefilter=True, colors=12, palette=None, dither=None, strength=0.4,
                    res_ramp=None, hold=1, seed=0),
        choices=dict(palette=['green4', 'duo', '1bit', 'neon5', '[colour, ...]'],
                     dither=['none', 'checker', 'bayer4'])),
    'pixelate': dict(
        kind='image', desc='Mosaic: square blocks of mean colour on a screen grid.',
        params=dict(size=0.035, px=None, prefilter=False)),
    'glitch': dict(
        kind='image', desc='Discrete digital-glitch bursts on events: slices, RGB split, row smear, block shuffle, '
                           'invert.',
        params=dict(times=None, burst=4, hold=2, kinds=['slices', 'rgb', 'smear', 'blocks', 'invert'],
                    intensity=0.7, wrap=True, seed=0),
        choices=dict(kinds=['slices', 'rgb', 'smear', 'blocks', 'invert'], times=_TIMES)),
    'datamosh': dict(
        kind='image', desc='Datamosh: held pixels move in blocks along the motion of the incoming frames '
                           '(sequential).',
        params=dict(mode='continuous', refresh=0.02, repeats=15, dur=1.2, block=16, holes=0.0, seed=0),
        choices=dict(mode=['continuous', 'bloom', 'melt'])),
    'lens_warp': dict(
        kind='image', desc='Lens distortion: bulge, pinch, sphere, twirl, barrel, pincushion (+ chroma, vignette).',
        params=dict(mode='bulge', strength=None, k2=None, center=[0.5, 0.5], radius=1.0, fill='auto', dir='ccw',
                    chroma=0.0, vignette=0.0),
        choices=dict(mode=['bulge', 'pinch', 'sphere', 'twirl', 'barrel', 'pincushion'], dir=['ccw', 'cw'])),
    'letterbox': dict(
        kind='image', desc='Animated letterbox / pillarbox bars between aspect ratios over absolute time.',
        params=dict(ratio=[1.78, 2.39], t=None, t_keys=None, ease='linear', anchor=[0.5, 0.5], color='#000000')),
    'duotone': dict(
        kind='image', desc='Luma mapped onto a shadows -> highlights colour gradient (optional mid colour).',
        params=dict(shadows='#1c0e2f', highlights='#ffd27a', mid=None, contrast=1.0, gamma=1.0, amount=1.0)),
    'posterize': dict(
        kind='image', desc='Posterize to N levels per channel or on luma, optional ordered dither.',
        params=dict(levels=4, mode='rgb', dither='none'),
        choices=dict(mode=['rgb', 'luma'], dither=['none', 'bayer4'])),
    'vignette': dict(
        kind='image', desc='Vignette: legacy elliptical darkening, or a lens vignette when radius is given.',
        params=dict(amount=0.35, radius=None, feather=0.15, center=[0.5, 0.5], aspect=1.0)),
    'grain': dict(
        kind='image', desc='Film grain from a hashed tile bank, weighted by luma response.',
        params=dict(sigma=0.035, sigma255=None, size=2.0, corr=0.8, mono=False, response=True, seed=0)),
    'bloom': dict(kind='image', desc='Legacy bloom: thresholded highlights blurred and added in gamma.',
                  params=dict(thr=0.7, r=30, strength=0.6)),
    'dirblur': dict(kind='image', desc='Directional (motion) blur of a given length and angle.',
                    params=dict(len=0.05, angle=0.0)),
    'zoomblur': dict(kind='image', desc='Radial zoom blur about a centre.',
                     params=dict(amount=0.12, cx=0.5, cy=0.5, n=8)),
    'chroma': dict(kind='image', desc='Legacy chromatic offset (R +px, B -px) with reflected edges.',
                   params=dict(px=6, vertical=False)),
    'smear': dict(kind='image', desc='Legacy smear: directional blur + chroma offset + saturation boost.',
                  params=dict(len=0.25, angle=0.0, px=14, sat=1.6)),
    'blur': dict(kind='image', desc='Gaussian blur (radius in px @1080 width).', params=dict(r=6)),
    'shake': dict(kind='image', desc='Legacy image-space shake: random offset per frame (deterministic).',
                  params=dict(px=12, seed=0)),
    'exposure': dict(kind='image', desc='Exposure change in stops.', params=dict(ev=0.0)),
    'invert': dict(kind='image', desc='Negative image (amt < 1 mixes with the original).', params={}),
    'bleach': dict(kind='image', desc='Mix toward white.', params=dict(a=0.5)),
    'flash': dict(
        kind='image', desc='Flash pulses on explicit event times (solid, add, screen, black, invert, exposure).',
        params=dict(times=None, color='#ffffff', tau=0.06, peak_frames=1, cutoff=0.05, blend='normal'),
        choices=dict(blend=['normal', 'solid', 'add', 'screen', 'black', 'invert', 'exposure'],
                     color=['white', 'warm', 'red', 'cyan', 'magenta', 'acid', 'amber', '#hex', '[r, g, b]'])),
}
FX_SPECS.update({
    'contour_glow': dict(
        kind='image', desc='Coloured glow hugging the subject outline (needs a subject matte), optional beat pulses.',
        params=dict(color='#8a5cff', width=0.005, radius=0.03, strength=0.8, inner=0.15, blend='screen', times=None,
                    base=0.3, peak=1.0),
        choices=dict(blend=['screen', 'add'], times=_TIMES)),
    'defocus': dict(
        kind='image', desc='Lens-like disc blur in linear light, small highlights open into bokeh discs; with '
                           'region background = shallow focus.',
        params=dict(amount=0.012, highlights=1.5)),
    'clarity': dict(kind='image', desc='Local contrast on luma (large-radius unsharp mask on the midtones); never adds '
                                       'clipped blacks or whites.',
                    params=dict(amount=0.4, radius=0.02)),
    'saturation': dict(kind='image', desc='Saturation and hue rotation; with region background = colour pop.',
                       params=dict(sat=0.0, hue=0.0)),
    'tape': dict(
        kind='image', desc='Home-videotape texture: soft low-res picture, chroma bleed and shift, scanlines, noise, '
                           'tracking band, head switching.',
        params=dict(res=0.36, vres=0.6, smear=0.0015, chroma_blur=3.0, chroma_shift=0.004, depth=0.07, noise=0.03,
                    jitter=0.0008, band={'height': 0.05, 'every': [3, 7], 'dur': 0.3, 'shift': 0.012}, head=0.02,
                    white=0.94, black=0.016, seed=0)),
})
FX_SPECS['glitch_blocks'] = dict(FX_SPECS['glitch'], desc='Alias of glitch (card name glitch_blocks).')

COMMON_TRANSITION_PARAMS = {'kind': 'dissolve', 'frames': 6, 'align': 'center', 'params': {}}
COMMON_TRANSITION_DOC = ('segment transition_in: {kind: name | "name(arg)" (dip(#0b1020), wipe(circle), lens(twirl), '
                         'liquid(melt)), frames: window length, align: center | end, params: {...}}; the window is '
                         'centred on the cut (center) or ends frames after it (end)')
TRANSITION_SPECS = {
    'dissolve': dict(desc='Cross-dissolve A -> B.', params=dict(curve='linear'),
                     choices=dict(curve=['linear', 'inOutSine', 'outQuad'])),
    'dip': dict(desc='Dip through a colour: A -> colour -> B (short out / hold / in, seconds).',
                params={'color': '#000000', 'out': 0.16, 'hold': 0.04, 'in': 0.24, 'out_frames': None,
                        'hold_frames': None, 'in_frames': None, 'curve': ['linear', 'linear'], 'mode': 'dip',
                        'grain_keep': 0.0, 'hard_in': False},
                choices=dict(mode=['dip', 'in', 'out'])),
    'fade': dict(desc='Fade through a colour, or fade in from / out to it (mode in | out; seconds).',
                 params={'color': '#000000', 'out': 0.24, 'hold': 0.0, 'in': 0.28, 'out_frames': None,
                         'hold_frames': None, 'in_frames': None, 'curve': ['linear', 'linear'], 'mode': 'dip',
                         'grain_keep': 0.0, 'hard_in': False},
                 choices=dict(mode=['dip', 'in', 'out'])),
    'flash': dict(desc='Flash cut: optional pre-ramp on A, peak on the cut frame, exponential tail on B.',
                  params=dict(color='#ffffff', mode='solid', pre_frames=0, pre=[0.35, 0.65], peak_frames=1,
                              tau=0.06, cutoff=0.05, bloom=None),
                  choices=dict(mode=['solid', 'add', 'screen', 'exposure', 'black', 'invert'],
                               color=['white', 'warm', 'red', 'cyan', 'magenta', 'acid', 'amber', 'palette', '#hex',
                                      '[r, g, b]'])),
    'whip': dict(desc='Whip pan: A smears out, B smears in, the cut hidden inside the blur.',
                 params=dict(dir='right', angle=None, split=0.5, travel=1.2, ease=['inExpo', 'outExpo'],
                             shutter=0.7, blur_max=0.4, seam_mix=1),
                 choices=dict(dir=['right', 'left', 'up', 'down', '<content angle>'])),
    'zoom': dict(desc='Zoom-through: A zooms in with radial blur to the cut, B continues (through) or punches back.',
                 params=dict(mode='through', out_scale=3.0, in_scale=None, center=[0.5, 0.5], center_b=None,
                             split=0.55, ease=['inExpo', 'outExpo'], shutter=0.5, filler=None, filler_frames=0),
                 choices=dict(mode=['through', 'punch'])),
    'spin': dict(desc='Spin: A rolls out with scale, B rolls in from the opposite angle, rotational blur.',
                 params=dict(dir='cw', out_angle=120.0, in_angle=-120.0, scale=1.4, center=[0.5, 0.5], split=0.4,
                             ease=['inCubic', 'outCubic'], shutter=0.75),
                 choices=dict(dir=['cw', 'ccw'])),
    'wipe': dict(desc='Wipes: linear, iris shapes (circle, diamond, star, box), clock, barn, strips, lids, '
                      'occluder.',
                 params=dict(shape='linear', dir='rtl', angle=None, feather=None, ease=None, mode='open', r0=None,
                             r1=None, center=[0.5, 0.5], scale_content=True, axis='v', count=7, stagger=0.5,
                             close=0.35, hold=0.15, tone='dark', width=1.3, blur=0.1, points=5, inner=0.45),
                 choices=dict(shape=['linear', 'circle', 'iris', 'diamond', 'star', 'box', 'clock', 'barn',
                                     'strips', 'lids', 'occluder'], dir=['rtl', 'ltr', 'ttb', 'btt'],
                              mode=['open', 'close'], axis=['v', 'h'], tone=['dark', 'light'])),
    'luma': dict(desc='Luma key: B appears where A is darkest (or lightest) first; noise source for a burn.',
                 params=dict(source='A', order='dark_first', softness=0.08, noise={'scale': 0.05, 'amount': 0.15},
                             curve=None, scale=0.04, edge=None, dip=None, rim_color='#2a0d02', seed=0),
                 choices=dict(source=['A', 'noise'], order=['dark_first', 'light_first'], edge=[None, 'grain'],
                              dip=[None, 'black'])),
    'lens': dict(desc='Lens-distort transition: A deforms to a peak at the cut, B relaxes from it.',
                 params={'mode': 'bulge', 'out': 6, 'in': 7, 'peak': None, 'from': 'mirror', 'center': [0.5, 0.5],
                         'radius': 1.0, 'dir': 'cw', 'blur': {'samples': 4}, 'chroma': 0.04, 'vignette': 0.25},
                 choices=dict(mode=['bulge', 'pinch', 'twirl', 'barrel', 'pincushion'], **{'from': ['mirror',
                                                                                                    'through']})),
    'glitch': dict(desc='Glitch transition: A drips down in columns with glitch states, B settles from a burst.',
                   params=dict(streaks='vertical', split=0.5, intensity=0.8, seed=0)),
    'pixel_sort': dict(desc='Pixel-sort transition: A sorts to a full sort at the cut, B un-sorts.',
                       params={'out': 4, 'peak': 2, 'in': 5, 'mask': 'bright', 'axis': 'y', 'dir': 'down',
                               'work_res': 540},
                       choices=dict(mask=['bright', 'band'])),
    'light_leak': dict(desc='Light-leak burst that peaks on the cut and hides it.',
                       params=dict(env={'attack': 8, 'hold': 3, 'release': 10}, shape='burst', anchor='right',
                                   palette='amber', peak=1.3, size=0.95, blend='add', seed=0)),
    'liquid': dict(desc='Liquid: a soft blob grows from the darkest region of A (blob), glassy ripple (melt), or '
                        'luma / burn (these two take the luma params).',
                   params=dict(mode='blob', wobble=0.04, rim={'width': 0.015, 'glow': 0.7}, ease='outCubic',
                               center=None, amp=0.015, scale=0.1, curve='linear', light_peak=None, seed=0),
                   choices=dict(mode=['blob', 'melt', 'luma', 'burn'])),
    'push': dict(desc='Push: A and B move together along a direction (crisp, with directional blur).',
                 params=dict(dir='left', ease='inOutCubic', shutter=0.5, divider={'width': 0.0, 'color': '#000000'}),
                 choices=dict(dir=['left', 'right', 'up', 'down'])),
    'slide': dict(desc='Slide: B slides over a static A (reveal: A slides off over B).',
                  params=dict(dir='left', ease='inOutCubic', shutter=0.5, reveal=False),
                  choices=dict(dir=['left', 'right', 'up', 'down'])),
    'datamosh': dict(desc='Datamosh cut: no key frame, A\'s pixels move along B\'s motion until B refreshes in.',
                     params=dict(split=0.0, block=16, holes=0.0)),
}


class Registry(dict):
    """{name: callable} (aliases included, exactly as before) + machine-readable specs.
    spec(name) -> {name, kind, desc, params {name: default}, choices, aliases, doc} (aliases resolve);
    canonical(name) -> registry name; names(kind=None) -> canonical names; describe(kind=None) -> JSON-ready
    {name: spec} of canonical entries; common -> params every entry accepts (gates, amt / transition fields)."""

    def __init__(self, items=(), specs=None, aliases=None, common=None, common_doc='', family='fx'):
        super().__init__(items)
        self.specs, self.alias_of, self.family = dict(specs or {}), dict(aliases or {}), family
        self.common, self.common_doc = dict(common or {}), common_doc

    def canonical(self, name):
        n = str(name or '').split('(')[0].strip()
        if n in self.specs:
            return n
        return self.alias_of.get(n, n) if self.alias_of.get(n, n) in self.specs else None

    def names(self, kind=None):
        return sorted(n for n, s in self.specs.items() if kind is None or s.get('kind') == kind)

    def spec(self, name):
        c = self.canonical(name)
        if c is None:
            return None
        s = self.specs[c]
        fn = dict.get(self, c)
        params = dict(s.get('params') or {})
        return dict(name=c, kind=s.get('kind', self.family), desc=s['desc'], params=params,
                    choices=dict(s.get('choices') or {}),
                    aliases=sorted(a for a, t in self.alias_of.items() if t == c and a != c),
                    doc=' '.join((getattr(fn, '__doc__', None) or '').split()))

    def describe(self, kind=None):
        return {n: self.spec(n) for n in self.names(kind)}


def _fx_aliases():
    out = {a: t for a, t in _CAM_ALIAS.items()}
    out.update(_IMG_ALIAS)
    return out


FX_TYPES = Registry(FX_TYPES, FX_SPECS, _fx_aliases(), COMMON_FX_PARAMS, COMMON_FX_DOC, 'fx')
TRANSITIONS = Registry(TRANSITIONS, TRANSITION_SPECS, _TR_ALIAS, COMMON_TRANSITION_PARAMS, COMMON_TRANSITION_DOC,
                       'transition')
for _n in TRANSITION_SPECS:
    TRANSITION_SPECS[_n].setdefault('kind', 'transition')


# ============================================================================= looks (grade + fx stacks)
# A look is a finished picture treatment: a segment grade (ed_edl grade params: auto, exposure, mono, sat, temp,
# tint, mult, split, duo, gamma, contrast, pivot, black, gain, lift, fade, bleach) plus image fx appended to the
# segment's fx list. Our own names; the planner's style presets reference them by name. look(name, intensity)
# returns a copy scaled toward neutral; look_for(words) picks one from plain words.
LOOK_PRESETS = {
    'film_print': dict(
        label='Warm film print', tags=['film', 'analog', 'warm', 'nostalgic', 'cinematic', 'retro', 'grain'],
        suits=['drama', 'travel', 'calm', 'fashion', 'teaser'],
        desc='Warm print stock: soft lifted blacks, teal-leaning shadows, red-orange halation round the highlights, '
             'fine grain, gentle flicker and gate weave.',
        grade=dict(auto=0.6, sat=0.86, temp=0.18, tint=0.02, contrast=1.05, fade=0.05, gain=0.96,
                   split=([0.45, 0.53, 0.52], [0.57, 0.5, 0.41], 0.65)),
        fx=[dict(type='glow', threshold=0.74, strength=0.22, tint='#ff6a3a', tint_mix=0.8,
                 radii=[0.003, 0.01, 0.03], weights=[0.4, 0.35, 0.25]),
            dict(type='film_overlay', level=2, dust=2, hair=0.1, scratch=0),
            dict(type='vignette', amount=0.2)]),
    'home_tape': dict(
        label='Home videotape', tags=['vhs', 'tape', 'camcorder', 'retro', '90s', 'lofi', 'found footage'],
        suits=['fanedit', 'viral', 'ugc', 'teaser'],
        desc='Camcorder tape: punchy red-leaning colour, soft low-res picture, colour bleeding to the right, '
             'scanlines, noise, the odd tracking band and head-switching at the bottom.',
        grade=dict(auto=0.5, sat=1.35, mult=[1.07, 0.99, 0.94], contrast=1.06, black=0.015, gain=0.95, fade=0.025),
        fx=[dict(type='tape', res=0.3, chroma_shift=0.005)]),
    'clean_luxe': dict(
        label='Clean luxury', tags=['clean', 'luxury', 'expensive', 'premium', 'minimal', 'elegant', 'polished'],
        suits=['fashion', 'product', 'explainer', 'clips'],
        desc='Polished and expensive: deep clean blacks, creamy warm-neutral highlights, restrained saturation, a '
             'soft diffusion glow round the highlights, very fine grain.',
        grade=dict(auto=0.75, sat=0.86, temp=0.05, tint=0.015, contrast=1.2, black=0.025, gain=0.965,
                   split=([0.48, 0.5, 0.53], [0.54, 0.5, 0.45], 0.4)),
        fx=[dict(type='glow', threshold=0.7, knee=0.25, strength=0.16, radii=[0.01, 0.03, 0.07],
                 weights=[0.35, 0.4, 0.25], tint='#fff0e0', tint_mix=0.3),
            dict(type='vignette', amount=0.1),
            dict(type='grain', sigma=0.006, size=1.6, mono=True)]),
    'dreamy_bloom': dict(
        label='Dreamy bloom', tags=['dreamy', 'soft', 'haze', 'romantic', 'ethereal', 'pastel', 'glow', 'dream'],
        suits=['calm', 'fashion', 'travel', 'fanedit'],
        desc='Hazy daydream: lifted pastel blacks, low contrast, wide pink-white bloom, a faint peach leak in the '
             'corner.',
        grade=dict(auto=0.5, sat=0.9, temp=0.1, tint=0.08, contrast=0.86, fade=0.07, gain=0.95),
        fx=[dict(type='glow', threshold=0.5, knee=0.2, strength=0.62, radii=[0.01, 0.03, 0.08],
                 weights=[0.3, 0.4, 0.3], tint='#ffd6e8', tint_mix=0.35),
            dict(type='light_leak', palette='peach', shape='corner', anchor='tr', peak=0.45, size=0.5),
            dict(type='vignette', amount=0.12)]),
    'gritty_contrast': dict(
        label='Gritty contrast', tags=['gritty', 'street', 'raw', 'hard', 'urban', 'dark', 'rough', 'phonk'],
        suits=['phonk', 'sport', 'motivation', 'fanedit'],
        desc='Hard street look: crunchy local contrast, deep blacks, bled-out colour with teal shadows, heavy mono '
             'grain and a dark vignette.',
        grade=dict(auto=0.85, sat=0.66, temp=0.0, tint=-0.06, contrast=1.38, black=0.05,
                   split=([0.42, 0.55, 0.52], [0.54, 0.53, 0.46], 0.5)),
        fx=[dict(type='clarity', amount=0.6, radius=0.018),
            dict(type='film_overlay', level=3, mono=True, dust=2, hair=0, scratch=0, flicker=0.01),
            dict(type='vignette', amount=0.4)]),
    'mono_noir': dict(
        label='Noir monochrome', tags=['black and white', 'bw', 'noir', 'monochrome', 'moody', 'classic', 'editorial'],
        suits=['drama', 'fashion', 'teaser', 'motivation'],
        desc='High-contrast black and white with crisp mids, silver highlights, coarse grain and a heavy vignette.',
        grade=dict(mono=1, auto=0.9, contrast=1.42, gamma=1.05, black=0.03),
        fx=[dict(type='clarity', amount=0.3, radius=0.02),
            dict(type='grain', sigma=0.03, size=2.2, mono=True),
            dict(type='vignette', amount=0.45)]),
    'neon_night': dict(
        label='Neon night', tags=['neon', 'night', 'cyber', 'club', 'electric', 'synth', 'city lights'],
        suits=['phonk', 'viral', 'fanedit', 'teaser'],
        desc='Electric night: cold blue shadows, magenta highlights, saturated lights that bloom in their own '
             'colour, a hint of chromatic fringing.',
        grade=dict(auto=0.7, sat=1.2, temp=-0.2, tint=0.07, contrast=1.16, black=0.02,
                   split=([0.45, 0.4, 0.66], [0.6, 0.44, 0.56], 0.55)),
        fx=[dict(type='glow', key='value_sat', threshold=0.58, strength=0.5, radii=[0.006, 0.02, 0.06],
                 weights=[0.35, 0.35, 0.3]),
            dict(type='rgb_split', px=1.5),
            dict(type='vignette', amount=0.25)]),
    'golden_hour': dict(
        label='Golden hour', tags=['golden', 'sunset', 'warm', 'summer', 'sunny', 'travel', 'glow'],
        suits=['travel', 'calm', 'viral', 'ugc'],
        desc='Late-sun warmth: amber highlights, honeyed skin, a soft gold leak drifting in from the edge, warm '
             'bloom.',
        grade=dict(auto=0.6, sat=1.08, temp=0.32, tint=0.02, contrast=1.04, fade=0.02,
                   split=([0.5, 0.49, 0.5], [0.58, 0.5, 0.4], 0.35)),
        fx=[dict(type='light_leak', palette='gold', shape='edge', anchor='right', peak=0.6, size=0.5),
            dict(type='glow', threshold=0.7, strength=0.22, tint='#ffb347', tint_mix=0.5),
            dict(type='vignette', amount=0.15)]),
    'silver_bleach': dict(
        label='Silver bleach', tags=['bleach bypass', 'silver', 'desaturated', 'war', 'harsh', 'metallic'],
        suits=['epic', 'drama', 'sport', 'motivation'],
        desc='Bleach-bypass silver: colour drained to a third, hard contrast, metallic highlights, crisp local '
             'contrast and fine grain.',
        grade=dict(auto=0.8, sat=0.32, contrast=1.28, temp=-0.04, black=0.03, gamma=0.94),
        fx=[dict(type='clarity', amount=0.4, radius=0.02),
            dict(type='grain', sigma=0.018, size=1.8, mono=True),
            dict(type='vignette', amount=0.25)]),
    'teal_orange': dict(
        label='Teal and amber', tags=['blockbuster', 'cinematic', 'teal', 'orange', 'action', 'epic', 'trailer'],
        suits=['epic', 'sport', 'teaser', 'fanedit'],
        desc='Blockbuster contrast: teal shadows against amber skin, firm contrast, a light highlight bloom.',
        grade=dict(auto=0.7, sat=1.2, temp=0.04, tint=-0.02, contrast=1.14, black=0.01,
                   split=([0.24, 0.54, 0.6], [0.68, 0.48, 0.34], 0.75)),
        fx=[dict(type='glow', threshold=0.8, strength=0.12),
            dict(type='vignette', amount=0.22)]),
    'vivid_pop': dict(
        label='Vivid pop', tags=['vivid', 'pop', 'punchy', 'bright', 'colorful', 'saturated', 'hype', 'energy', 'fun'],
        suits=['viral', 'ugc', 'product', 'sport'],
        desc='Bright and punchy: rich clean colour, crisp contrast with open shadows, extra local detail, a little '
             'sparkle in the highlights.',
        grade=dict(auto=0.85, sat=1.25, temp=0.03, contrast=1.12, gamma=0.94, black=0.01),
        fx=[dict(type='clarity', amount=0.28, radius=0.015),
            dict(type='glow', threshold=0.85, strength=0.1, radii=[0.004, 0.012, 0.03], weights=[0.4, 0.35, 0.25]),
            dict(type='vignette', amount=0.08)]),
    'pastel_fade': dict(
        label='Soft pastel', tags=['pastel', 'soft', 'airy', 'light', 'cute', 'fresh', 'bright'],
        suits=['calm', 'ugc', 'product', 'viral'],
        desc='Airy and light: bright lifted mids, gentle pastel colour, low contrast, a little bloom.',
        grade=dict(auto=0.5, sat=0.72, temp=-0.05, tint=0.06, contrast=0.84, fade=0.1, gain=0.98, gamma=0.82),
        fx=[dict(type='glow', threshold=0.75, strength=0.12),
            dict(type='grain', sigma=0.008, size=1.4, mono=True)]),
    'cold_concrete': dict(
        label='Cold concrete', tags=['cold', 'bleak', 'dystopian', 'grey', 'industrial', 'winter', 'serious'],
        suits=['drama', 'teaser', 'explainer'],
        desc='Bleak and cold: blue-grey palette with colour nearly gone, dimmed whites, soft shadows, light grain.',
        grade=dict(auto=0.8, sat=0.38, temp=-0.18, contrast=0.96, black=0.03, gain=0.92),
        fx=[dict(type='grain', sigma=0.015, size=1.8, mono=True),
            dict(type='vignette', amount=0.3)]),
}
LOOK_ALIASES = {'film': 'film_print', 'vhs': 'home_tape', 'tape': 'home_tape', 'luxury': 'clean_luxe',
                'clean': 'clean_luxe', 'dreamy': 'dreamy_bloom', 'gritty': 'gritty_contrast', 'noir': 'mono_noir',
                'bw': 'mono_noir', 'neon': 'neon_night', 'golden': 'golden_hour', 'bleach': 'silver_bleach',
                'blockbuster': 'teal_orange', 'pastel': 'pastel_fade', 'cold': 'cold_concrete', 'pop': 'vivid_pop',
                'vivid': 'vivid_pop', 'punchy': 'vivid_pop'}
_GRADE_NEUTRAL = {'sat': 1.0, 'contrast': 1.0, 'temp': 0.0, 'tint': 0.0, 'gamma': 1.0, 'gain': 1.0, 'lift': 0.0,
                  'fade': 0.0, 'black': 0.0, 'bleach': 0.0, 'exposure': 0.0}


def look_name(name):
    """Look name or alias -> LOOK_PRESETS key (None when unknown)."""
    n = str(name or '').strip().lower().replace('-', '_').replace(' ', '_')
    n = LOOK_ALIASES.get(n, n)
    return n if n in LOOK_PRESETS else None


def look(name, intensity=1.0):
    """A look's {'name', 'grade', 'fx'} (deep copies) at an intensity: 1 = as designed, 0 = no look (grade numbers
    move linearly toward neutral, split / duo amounts, mult and every fx's amt scale; auto exposure and mono stay).
    The grade goes into the segment's 'grade', the fx are appended to its 'fx' (each tagged 'look': name). Unknown
    name -> ValueError listing the looks."""
    n = look_name(name)
    if n is None:
        raise ValueError(f'unknown look {name!r}; known: {sorted(LOOK_PRESETS)} (aliases {sorted(LOOK_ALIASES)})')
    P = json.loads(json.dumps(LOOK_PRESETS[n]))
    a = max(0.0, float(intensity))
    g = {}
    for k_, v in P['grade'].items():
        if k_ in _GRADE_NEUTRAL and _num(v):
            g[k_] = round(_GRADE_NEUTRAL[k_] + (float(v) - _GRADE_NEUTRAL[k_]) * a, 4)
        elif k_ in ('split', 'duo') and isinstance(v, (list, tuple)) and len(v) == 3:
            g[k_] = [v[0], v[1], round(float(v[2]) * min(a, 1.5), 4)]
        elif k_ == 'mult' and isinstance(v, (list, tuple)):
            g[k_] = [round(1.0 + (float(q) - 1.0) * a, 4) for q in v]
        else:
            g[k_] = v
    fx = []
    for f_ in P['fx']:
        f_ = dict(f_)
        if a != 1.0:
            f_['amt'] = round(float(f_.get('amt', 1.0)) * a, 4)
        f_.setdefault('look', n)
        fx.append(f_)
    return {'name': n, 'grade': g, 'fx': fx}


def look_for(words, genre=None):
    """Plain words ("gritty street", "dreamy retro") -> {'name', 'score', 'why'}: best tag / label / description
    overlap (genre fit breaks ties); no overlap -> the look that suits the genre, else 'clean_luxe'."""
    text = ' ' + re.sub(r'[^a-z0-9 ]+', ' ', str(words or '').lower()) + ' '
    best, bs, why = None, 0.0, ''
    for n, P in LOOK_PRESETS.items():
        sc, hits = 0.0, []
        for t in dict.fromkeys(P['tags'] + n.split('_')):
            if f' {t} ' in text or (len(t) > 4 and t in text):
                sc += 1.5 if t in n.split('_') else 1.0          # the look's own name words weigh more
                hits.append(t)
        for wd in set(text.split()):
            if len(wd) > 3 and wd in P['desc'].lower() and wd not in hits:
                sc += 0.25
        if genre and genre in P['suits']:
            sc += 0.3
        if sc > bs:
            best, bs, why = n, sc, ', '.join(hits)
    if best is None or bs < 0.5:
        for n, P in LOOK_PRESETS.items():
            if genre and genre in P['suits']:
                return {'name': n, 'score': 0.0, 'why': f'genre {genre}'}
        return {'name': 'clean_luxe', 'score': 0.0, 'why': 'default'}
    return {'name': best, 'score': round(bs, 2), 'why': why}


def describe(what='all'):
    """JSON-ready registry: {'fx': {...}, 'transitions': {...}, 'looks': {...}, 'common': {...}} (what = 'fx' |
    'transitions' | 'looks' | 'all'); fx / transition entries {name, kind, desc, params {name: default}, choices,
    aliases, doc}; look entries {name, label, desc, tags, suits, grade, fx}."""
    out = {}
    if what in ('fx', 'all'):
        out['fx'] = FX_TYPES.describe()
    if what in ('transitions', 'all'):
        out['transitions'] = TRANSITIONS.describe()
    if what in ('looks', 'all'):
        out['looks'] = {n: dict(name=n, label=P['label'], desc=P['desc'], tags=list(P['tags']), suits=list(P['suits']),
                                grade=json.loads(json.dumps(P['grade'])), fx=json.loads(json.dumps(P['fx'])),
                                aliases=sorted(a for a, t in LOOK_ALIASES.items() if t == n))
                        for n, P in LOOK_PRESETS.items()}
    out['common'] = {'fx': {'params': COMMON_FX_PARAMS, 'doc': COMMON_FX_DOC},
                     'transition': {'params': COMMON_TRANSITION_PARAMS, 'doc': COMMON_TRANSITION_DOC}}
    return out


def _md_table(entries):
    rows = ['| name | kind | description | params (defaults) |', '|---|---|---|---|']
    for n, s in entries.items():
        ps = ', '.join(f'{k}={json.dumps(v)}' for k, v in s['params'].items() if v is not None)
        al = f" (aliases: {', '.join(s['aliases'])})" if s['aliases'] else ''
        rows.append(f"| `{n}`{al} | {s['kind']} | {s['desc']} | {ps} |")
    return '\n'.join(rows)


def apply(x, fx_list, k, n, ctx):
    """Apply the image fx of a segment (in order) to frame x (float32 HxWx3 0..1) at segment frame k of n.
    Camera types and unknown types are skipped; each fx is gated by frames/f/k/t (see active()). An fx with
    region='background' | 'subject' (or behind=True) only changes that part of the picture (subject_matte: ctx
    mask, person_mask or an automatic person matte; feather / expand shape the edge)."""
    if not fx_list:
        return x
    y = _f32(x)
    for fx in fx_list:
        t = _canon(fx.get('type'))
        if t in CAMERA_FX:
            continue
        fn = FX_TYPES.get(t)
        if fn is None or getattr(fn, 'kind', 'image') != 'image':
            continue
        if not active(fx, k, n, ctx):
            continue
        z = _f32(fn(y, fx, k, n, ctx))
        if fx.get('region') is not None or fx.get('behind'):
            wgt = region_weight(y, fx, ctx or {})
            if wgt is not None:
                z = _mix(y, z, wgt)
        y = z
    return y


def _main(argv=None):
    """CLI: python3 -I ed_fx.py registry [fx|transitions|looks|all] [--md]  -> the machine-readable registry (JSON or
    markdown tables) for docs and planners."""
    import argparse
    ap = argparse.ArgumentParser(prog='ed_fx.py', description='Edit Studio fx registry')
    sub = ap.add_subparsers(dest='cmd')
    r = sub.add_parser('registry', help='print FX_TYPES / TRANSITIONS specs')
    r.add_argument('what', nargs='?', default='all', choices=['fx', 'transitions', 'looks', 'all'])
    r.add_argument('--md', action='store_true', help='markdown tables instead of JSON')
    a = ap.parse_args(argv)
    if a.cmd != 'registry':
        ap.print_help()
        return 2
    d = describe(a.what)
    if a.md:
        if 'fx' in d:
            print('### fx (segment "fx" list)\n\nCommon: ' + COMMON_FX_DOC + '\n\n' + _md_table(d['fx']) + '\n')
        if 'transitions' in d:
            print('### transitions (segment "transition_in")\n\nCommon: ' + COMMON_TRANSITION_DOC + '\n\n'
                  + _md_table(d['transitions']) + '\n')
        if 'looks' in d:
            print('### looks (segment grade + fx; ed_fx.look(name, intensity))\n\n| name | look | tags | grade | fx |'
                  '\n|---|---|---|---|---|')
            for n_, L_ in d['looks'].items():
                print(f"| `{n_}` | {L_['label']}: {L_['desc']} | {', '.join(L_['tags'][:5])} | "
                      f"{json.dumps(L_['grade'])} | {', '.join(f_['type'] for f_ in L_['fx'])} |")
    else:
        print(json.dumps(d, indent=1, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    import sys as _sys
    _sys.exit(_main())
