#!/usr/bin/env python3
"""Sound effects + soundtrack mixer for the edit engine (TIMELINE.md section 4). SFX are synthesized by code
(numpy/scipy, 48 kHz stereo, deterministic by seed) or come from the user's own sound files; recipes follow the move
cards moves/sfx.whoosh|riser|impact|sub_drop|glitch.yaml, layered for weight and punch.

API (contract, used by ed_edl.py):
  synth(kind, variant=None, sr=48000, dur=None, seed=0, **params) -> float32 (N, 2), peak -6 dBFS
  synth_ex(...) -> (float32 (N, 2), meta)      meta: attack / peak sample index, gates, stop, style, ...
  mix(audio, total_s, out_wav, sr=48000) -> {"lufs", "tp", "sfx_count", "gain_db", "gr_max_db", "music_lufs",
           "program_lufs", "sfx_level", "sfx_style", "events": [...], "audibility": [...], "limiter": {...}, "key",
           "warnings": [...]}
  encode_audio(wav, out, codec='aac', bitrate='320k', tp_max=-1.0, lufs=None, lufs_tol=0.5) -> {"path", "codec",
           "bitrate", "lufs", "tp", "lufs_in", "tp_in", "ceil_db", "gain_db", "lowpass_hz", "iters", "ok"}: the
           delivery encode; lossy coding overshoots inter-sample peaks (AAC +0.3-2 dB on noise bursts), so the PCM is
           band-limited to what the codec keeps (aac 320k: 18.5 kHz, zero-phase) and re-limited until the ENCODED file
           measures true peak <= tp_max, loudness kept within lufs_tol of `lufs` (default: the WAV's own).
  The audibility contract shared with ed_qa: QA_MIN_LU {family: LU at the normal preset}, QA_FAMILY, qa_need(kind,
           level), qa_event_need(event, audio) (None = not judged), audibility(recs, sfx, prog, voice) (ed_qa's
           measurement on arrays); event_anchor(event) -> where an event lands (s; ranges below);
           validate_audio(audio, total_s) -> (errors, warnings) for the EDL validators; VOICE_GROUPS = True (voice
           clips of one file share one gain).
  load_sample(path, sr, trim_db=-50, pitch=0, rate=1, stretch=1, reverse=False, dur=None) -> (y, meta)
  pick_sample(sfx_dir, kind, variant=None, seed=0, avoid=None) -> path | None   (filename / folder keywords)
  style_of(style_or_genre) -> 'cinematic' | 'trap' | 'clean';  level_name(level), level_offset(level)
  voice_duck_curve(vact, depth_db, attack_ms, hold_ms, release_ms, gap_ms, regions=None) -> dB reduction per ms
  KINDS {kind: {"default", "align", "variants": {name: spec}}};  ALIASES;  STYLES;  LEVELS;  NORMAL_LU
  Music ops on a timeline-aligned (N, 2) track: audio_stutter, tape_stop, scratch_track, music_filter, music_crush,
  music_gate.  key_root(track) -> key + confidence;  music_grid(track) -> bpm / beats / downbeats (ed_audio).

Styles (event "style", audio "sfx_style", else audio "genre" / the EDL's meta.genre passed by ed_edl):
  cinematic (default; epic, drama, teaser, motivation, travel): click + snap + saturated pitch-dropping body + knock +
            crunch + phase-locked sub tail + hall; whooshes with a low body and a doppler whistle; risers with a glide.
  trap (phonk, viral, sport, fanedit, hip-hop): distorted 808 body (asymmetric drive, still decaying), clap snap,
            short room; brighter, faster whooshes with a 5-14 kHz sizzle; rolls in risers; growling sub drops.
  clean (product, explainer, ugc, calm, fashion, clips): tight, little drive, short room, no crunch.
  Every hit is mono below 150 Hz and reads on phones (180 Hz high-pass loses <= ~6 LU of its loudness).

Audio spec (TIMELINE.md section 4 + extensions; times are output seconds):
 "audio": {
  "copy": false,                 true: decode "path" (reference audio) untouched, nothing is mixed
  "music": {"path", "in": 0, "at": 0, "dur": null, "gain_db": 0, "fade_in": 0, "fade_out": 0.5, "speed": 1.0},
           the used part is normalised to loudness.lufs first, then gain_db; speed != 1 = sped-up/slowed version
           (pitch follows).  No music: SFX levels are relative to loudness.lufs.
  "voice": [{"path", "at": 0, "in": 0, "dur": null, "gain_db": 0, "lufs": null, "norm": "source"}],  clips of one
           file share one gain that brings them together to lufs (default loudness.lufs; the source's balance between
           speakers is kept; "norm": "clip" = this clip alone); 6 ms fades at cut edges, none where the next clip
           continues the same file seamlessly; one 80 Hz high-pass over the voice bus.
  "sfx_level": "normal",         default preset of every event: light | normal | strong (aliases: subtle, heavy, ...)
  "sfx_style": null, "genre": null,   see Styles
  "sfx_dir": null,               a folder of the user's sounds: an event without "file" takes the best file for its
                                 kind / variant by filename and folder keywords (impact|hit|boom|punch..., whoosh|
                                 swoosh|swipe..., riser|uplifter..., sub|808|drop...); none matches -> synthesized
  "sfx": [{"kind", "variant", "at" | "t": [t0, t1], "align": "attack"|"peak"|"start"|"end", "offset_ms": 0, "dur",
           "level": "normal", "lu": null, "rel_lu": null, "gain_db": 0, "pan": 0 | [p0, p1], "width": 1, "seed",
           "style": null, "duck": null|true|false|{...}, "file": null, "pitch": 0, "rate": 1, "stretch": 1,
           "reverse": false, "trim_db": -50, "synth": false, "params": {}}],
           at + offset_ms is where the anchor lands: attack = first sample above -20 dB of the peak, peak = the
           recipe's designed peak (whoosh: max of the 10 ms RMS; riser / reverse sounds: the cut at the end).
           "t": [t0, t1] (no "at") = a RANGE the event fills; "dur" defaults to t1 - t0.  Attack / start aligned
           events (hits, glitches, clicks, the music kinds, "align": "start") start on t0; peak / end aligned ones
           (whooshes, risers, reverse sounds, swells, "align": "end") build across the range and land their peak /
           end on t1, the hit: a synth is lengthened until its build starts on t0 (a whoosh peaks at ~60 % of its
           length, so its tail runs on past t1); a sample keeps its length.  "at" given as well = "at" is the
           anchor.  event_anchor(event) = the landing time (the record's "at").
           LEVEL = event loudness minus the PROGRAM's (music + voice, after the ducks, without SFX), K-weighted, in
           the variant's window (impact punch: 100 ms from the attack and >= target - 4 LU over 400 ms; boom: 400 ms;
           whoosh: +-200 ms around the peak; riser: the last 400 ms; ...); the reference never drops below the
           program's integrated loudness - 12 LU.  Target, first match:
             "lu": absolute LU (no preset, no floor);
             the event's own "level" (a preset beats rel_lu: planners put the cards' numbers in rel_lu);
             "rel_lu" without an event level (legacy EDLs): the cards' scale (punch -6, boom -2, whoosh -6, ...)
             moved by audio.sfx_level, i.e. preset target + (rel_lu - card value);
             else audio.sfx_level.  Preset target = NORMAL_LU[kind, variant] + LEVELS[level] (light -5 dB,
             strong +4 dB; a number = dB relative to normal).  gain_db = extra trim.
           AUDIBILITY (ed_qa's sfx check, one definition): events whose anchors lie within 150 ms form a group; the
           group's SFX loudness = its loudest 400 ms (window centres every 25 ms over the members' span) of the SFX
           bus as heard (after the master gain and the limiter); reference = the 3 s short-term loudness of the
           program (music + voice, after every duck and dip) after the group when it holds an impact / sub drop /
           click / glitch, centred on it otherwise.  Need = QA_MIN_LU[family] (impact 3, whoosh / reverse whoosh 0,
           riser 0 LU) + the level preset (light -5, strong +4) + gain_db, the strictest member's; auto-level
           whoosh / riser / swell / glitch / click groups under a voice need 6 LU less; no need for sub drops,
           swells, glitches, clicks, samples without a kind, "lu" events and hit-stops; QA warns below need - 1 LU.
           The mixer aims at need + QA_MARGIN (0.5 LU): first estimate per group leader at placement, then (step 6)
           it measures the final mix exactly like ed_qa and, while a group is short: raises its leaders within their
           headroom -> dips the music deeper under the group's hit (<= +3 dB) -> lets a strong leader clip <= 2 dB
           more -> raises the other members; re-masters and re-measures (<= 6 rounds).  Every record gets st_lu (the
           group's LU over the program as QA measures it), need_lu and floor_db (the dB the floor added above the
           level rules, at placement + step 6; 0.0 = the preset alone was loud enough); mix() returns the group rows
           ("audibility": t, kinds, events, span, need_lu, rel_lu, sfx_lufs, program_st_lufs, under_voice, ok).
           Card rules applied to presets only (not to "lu" / legacy rel_lu, and never below the need): impact +
           sub_drop on one attack -> both -1.5 dB; impacts in a series (< 2.1 s apart) -1.5 dB each (card window);
           whoosh/riser/glitch/click under voice -6 dB and HPF 300 Hz.
           Headroom: an event may exceed the SFX bus ceiling by light 3 / normal 4 / strong 6 dB of true peak (its
           transients are soft-clipped right away and the lost loudness made up), above that it is capped (note);
           impacts get denser per preset (peak-to-loudness light 11 / normal 10 / strong 8.5 dB, cinematic), so the
           same peak carries more body.  On one of the track's strongest kicks an impact's body moves above the kick
           (x1.6, >= 75 Hz; no sub tail, HPF 45 Hz) instead of masking it.
           "file": the user's sound (wav / mp3 / aiff / flac / ogg / m4a ...; any kind, or no kind = generic hit,
           400 ms level window): silence trimmed, attack / peak found like a synth, the same level rules; pitch =
           semitones sampler-style, rate = speed, stretch = duration with pitch kept, reverse (then aligned on its end).
           Kinds stutter / tape_stop / scratch, glitch:crush and riser:filter process the music itself (track at
           0 dB, the original is replaced), everything else is added on the SFX bus.
  "music_fx": [{"op": "filter", "kind": "hp"|"lp", "f": [20, 400], "t": [t0, t1], "q": 1.0, "ease": "inQuad",
                "reset_at": t1},
               {"op": "crush", "t": [t0, t1], "bits": 8, "sr_hz": 11025, "mix": 0.8},
               {"op": "stutter", "at", "slice": "1/16"|0.125, "repeats": 8, "accel": null|"default"|[[note, n]..],
                "xfade_ms": 2, "pitch_step_st": 0, "end_at": null},
               {"op": "tape_stop", "at", "dur": 0.6, "curve": 1.5, "resume_at": null|t|"next_downbeat",
                "start": false},
               {"op": "scratch", "at", "dur": 0.35, "rate_hz": 4.5, "amp": 2.5},
               {"op": "mute", "t": [t0, t1]}, {"op": "gate", "holes": [[t0, t1], ...], "depth_db": -40},
               music LEVEL automation (one absolute curve; holds min-combine, level / swell override their span):
               {"op": "gain", "t": [t0, t1], "db": -18, "attack_ms": 10, "release_ms": 10, "curve": "hold"|"ramp"},
               {"op": "level", "points": [[t, db], ...], "ease": "linear"|"smooth"|"inQuad"|...},
               {"op": "swell", "at": t_drop, "dur": 1.5, "from_db": null, "to_db": 0, "ease": "inQuad"}
                   rise INTO t_drop (from_db null = the level there before the swell, e.g. the talk level),
               {"op": "fade_out", "at", "dur": 0.5, "curve": "cos"|"lin"|"exp", "until": null}  silent after it,
               {"op": "fade_in", "at", "dur": 0.5, "from": 0}  silent from `from` to at],
  "duck": [{"under": "voice", "depth_db": 8, "mode": "smooth", "attack_ms": 120, "hold_ms": 200, "release_ms": 500,
            "gap_ms": 700, "band": null},   smooth (default): pauses < gap_ms bridged (no pumping between words), the
            duck starts attack_ms BEFORE the first word, holds, releases with raised-cosine ramps, and never outlives
            the voice clip it is in (talk -> drop: the music hits at full level where the talk part ends); attack >= 40,
            release >= 250 ms; "mode": "fast" = the old one-pole duck on raw voice activity.
           {"under": "sfx" | "sfx:<kind>", ...overrides of the card's duck for those events},
           {"t": [t0, t1], "to": -60, "attack_ms": 10, "release_ms": 10}   (= a gain hold)],
           Under events (scaled by their level preset): impact 30-150 Hz -4 dB, sub_drop 25-150 Hz -6 dB (follows the
           sub), riser 2-10 kHz -3 dB in the last quarter, whoosh 1-6 kHz -2.5 dB (from 'normal' up); every impact /
           sub drop also dips the whole music (light 1 / 2, normal 3 / 4, strong 5 / 6 dB regular / main hit, 3 ms
           attack starting 5 ms early, hold 80 / 120 ms) - room for the hit; on a DROP (the music >= 3 LU louder in
           the second after the hit) or a strong main hit the dip is light 2 / normal 4 / strong 6 dB, held 150 ms
           and released over 600 ms (the music breathes back in), deepened by step 6 when the group is still short;
           event "duck": false disables all of it.
  "key": {"root": "A", "mode": "minor"} | null,    else detected from the music (key_root; used when conf >= 0.6:
           sub drop ends on the tonic in 27.5-55 Hz, tonal riser / swell chord / chord hit in key; otherwise the
           cards' fallbacks: f1 32 Hz and D <= 1 s, noise riser, swell without chord, boom without chord)
  "grid": {"bpm", "beats": [...], "downbeats": [...]} | null,   timeline s; else estimated (ed_audio.analyze)
  "loudness": {"lufs": -14, "tp": -1, "max_gr_db": 8},
  "base_dir": null,                 relative paths (music, voice, sfx files, sfx_dir) resolve against it
  "debug": {"stems": "<dir>"}       optional: music.wav / voice.wav / sfx.wav (float, after the master gain, before
                                    the limiter) + limiter_gr_db.npy: (music + voice + sfx) x db(-gr) = the mix to
                                    float precision, bit-identical from run to run (ed_qa re-mixes to get them)
 }
mix() also returns per-event placement ("events": i, kind, variant, at, start, end, level, lu, gain_db, ref_lufs, win,
st_lu, need_lu, floor_db, file or style, notes; music kinds: music=true), "audibility" (the group rows above),
"limiter" ({gain_db, ceil_db, gr_max_db, slow_gr_max_db, gr: [[t, dB], ...] at 100 Hz where it acts}) and
"warnings" (skipped events, groups under their need, the cards' frequency limits such as <= 3 whooshes per 10 s).
Master: music bed + voice + SFX bus (HPF 30 Hz, 4x-oversampled soft clip with a 3 dB knee at -2 dBTP after the
master gain, then a safety limiter) -> ffmpeg ebur128 measurement -> static gain -> 4x-oversampled look-ahead
true-peak limiter, iterated until |I - target| <= 0.1 LU and TP <= target; the limiter has two releases: hit-length
overs (<= FAST_MS 150 ms after merging overs within 30 ms: drums, hits, clicks) get 1 ms look-ahead and 6 ms release
(no hole after the hit), sustained overs 2.5 ms / 80 ms.  Impacts / sub drops that the limiter holds down (20 ms
average) by more than 4 dB (main) / 3 dB (+1 dB for strong) are lowered by the excess (step 6 may fold it back).
A program that would need more than max_gr_db of sustained limiting, hits limited by more than max_gr_db +
FAST_EXTRA_DB (6), or more than +20 dB of gain (+12 dB without music / voice) stays quieter than the target, with a
warning, instead of being squashed.

CLI:
  python3 -I ed_sfx.py list
  python3 -I ed_sfx.py synth <kind> <out.wav> [--variant v] [--dur s] [--seed n] [--param k=v ...]  (style=trap ...)
  python3 -I ed_sfx.py mix <audio.json> <total_s> <out.wav>
  python3 -I ed_sfx.py encode <mix.wav> <out.m4a> [--codec aac] [--bitrate 320k] [--tp -1] [--lufs -14]
  python3 -I ed_sfx.py demo <out_dir>           every kind/variant as WAV + a spectrogram/envelope sheet per kind
"""
import os, sys, re, json, math, argparse, subprocess, tempfile, functools
import numpy as np
from scipy import signal as ss
from scipy.ndimage import maximum_filter1d, uniform_filter1d

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

SR = 48000
PEAK = 0.5                 # synth() output peak (-6 dBFS); mix() re-levels every event anyway
TAU = 2 * np.pi
CR = 1000.0                # control rate (Hz) of gain automation (ducking, gates, mutes)


# ============================================================================ small helpers
def db(x):
    return 10.0 ** (np.asarray(x, float) / 20.0)


def _n(t, sr):
    return max(1, int(round(float(t) * sr)))


def _u(n):
    return np.linspace(0.0, 1.0, n) if n > 1 else np.zeros(max(n, 1))


def _rng(seed, *k):
    return np.random.default_rng(np.random.SeedSequence([int(seed) % (2 ** 32)] + [int(v) for v in k]))


def _st(x):
    x = np.asarray(x, float)
    return np.stack([x, x], 1) if x.ndim == 1 else x


def _norm(y, peak=PEAK):
    m = float(np.max(np.abs(y))) if y.size else 0.0
    return y * (peak / m) if m > 0 else y


def _fit(y, n):
    """Pad with zeros or trim along axis 0 to n samples."""
    if len(y) >= n:
        return y[:n]
    return np.pad(y, [(0, n - len(y))] + [(0, 0)] * (y.ndim - 1))


def curve(n, pts, log=False):
    """Per-sample curve through (u, value) points, u = fraction of the length; log=True interpolates in log."""
    u = _u(n)
    us = np.array([p[0] for p in pts], float)
    vs = np.array([p[1] for p in pts], float)
    if log:
        return np.exp(np.interp(u, us, np.log(vs)))
    return np.interp(u, us, vs)


EASE = {'linear': lambda u: u, 'inQuad': lambda u: u * u, 'outQuad': lambda u: 1 - (1 - u) ** 2,
        'inOutQuad': lambda u: np.where(u < 0.5, 2 * u * u, 1 - (-2 * u + 2) ** 2 / 2),
        'inCubic': lambda u: u ** 3, 'outCubic': lambda u: 1 - (1 - u) ** 3,
        'inExpo': lambda u: np.where(u <= 0, 0.0, 2.0 ** (10 * u - 10)),
        'outExpo': lambda u: np.where(u >= 1, 1.0, 1 - 2.0 ** (-10 * u))}


# ============================================================================ building blocks
def noise(n, color='white', rng=None):
    """Unit-RMS noise: white, pink (-3 dB/oct) or brown (-6 dB/oct), spectrally shaped in the FFT domain."""
    rng = rng if rng is not None else np.random.default_rng(0)
    w = rng.standard_normal(n)
    if color != 'white' and n > 4:
        X = np.fft.rfft(w)
        k = np.arange(len(X), dtype=float)
        k[0] = 1.0
        X *= k ** (-0.5 if color == 'pink' else -1.0)
        X[0] = 0.0
        w = np.fft.irfft(X, n)
    return w / (np.std(w) + 1e-12)


def _sos(kind, f, sr, order=2):
    nyq = sr / 2.0
    if kind == 'bp':
        lo, hi = max(1.0, float(f[0])), min(float(f[1]), 0.49 * sr)
        return ss.butter(order, [lo / nyq, hi / nyq], 'bandpass', output='sos')
    return ss.butter(order, min(float(f), 0.49 * sr) / nyq, 'lowpass' if kind == 'lp' else 'highpass', output='sos')


def filt(x, kind, f, sr=SR, order=2, zero_phase=False):
    """Static Butterworth filter along axis 0: kind 'lp' | 'hp' (f in Hz) | 'bp' (f = (lo, hi))."""
    sos = _sos(kind, f, sr, order)
    if zero_phase:
        return ss.sosfiltfilt(sos, x, axis=0)
    return ss.sosfilt(sos, x, axis=0)


def hp(x, f, sr=SR, order=2):
    return filt(x, 'hp', f, sr, order)


def lp(x, f, sr=SR, order=2):
    return filt(x, 'lp', f, sr, order)


def bp(x, f1, f2, sr=SR, order=2):
    return filt(x, 'bp', (f1, f2), sr, order)


def _rbj(kind, f, q, sr):
    """RBJ cookbook biquads (vectorised over f, q): lp, hp, bp (constant 0 dB peak gain)."""
    w = TAU * np.asarray(f, float) / sr
    cw, sw = np.cos(w), np.sin(w)
    al = sw / (2 * np.asarray(q, float))
    a0 = 1 + al
    if kind == 'lp':
        b = np.stack([(1 - cw) / 2, 1 - cw, (1 - cw) / 2], -1)
    elif kind == 'hp':
        b = np.stack([(1 + cw) / 2, -(1 + cw), (1 + cw) / 2], -1)
    else:
        b = np.stack([al, np.zeros_like(al), -al], -1)
    a = np.stack([a0, -2 * cw, 1 - al], -1)
    return b / a0[..., None], a / a0[..., None]


def biquad(x, kind, f, q=0.7071, sr=SR):
    b, a = _rbj(kind, f, q, sr)
    return ss.lfilter(b, a, x, axis=0)


def tv_filter(x, kind, fc, q=0.7071, sr=SR, block=64, steady=False):
    """Time-varying RBJ biquad (bp_sweep / hp_sweep / lp_sweep): coefficients recomputed every `block` samples
    (64 = 1.3 ms) while the filter state is kept. x: (N,) or (N, C); fc, q: scalars or per-sample arrays.
    steady=True starts from the steady state of the first input sample (no start-up transient on music)."""
    x = np.asarray(x, float)
    mono = x.ndim == 1
    X = x[None, :] if mono else x.T
    C, N = X.shape
    fc = np.broadcast_to(np.asarray(fc, float), (N,))
    q = np.broadcast_to(np.asarray(q, float), (N,))
    nb = (N + block - 1) // block
    idx = np.minimum(np.arange(nb) * block + block // 2, N - 1)
    B, A = _rbj(kind, np.clip(fc[idx], 5.0, 0.47 * sr), np.maximum(q[idx], 0.05), sr)
    Y = np.empty_like(X)
    if steady:
        zi = ss.lfilter_zi(B[0], A[0])[None, :] * X[:, :1]
    else:
        zi = np.zeros((C, 2))
    for i in range(nb):
        s = slice(i * block, min(N, (i + 1) * block))
        Y[:, s], zi = ss.lfilter(B[i], A[i], X[:, s], axis=-1, zi=zi)
    return Y[0] if mono else Y.T


def _phase(f, sr):
    """Accumulated phase of a per-sample frequency curve, starting at exactly 0."""
    f = np.asarray(f, float)
    return TAU * (np.cumsum(f) - f) / sr


def _blep(t, dt):
    y = np.zeros_like(t)
    m = t < dt
    u = t[m] / dt[m]
    y[m] = 2 * u - u * u - 1
    m = t > 1 - dt
    u = (t[m] - 1) / dt[m]
    y[m] = u * u + 2 * u + 1
    return y


def osc(f, sr=SR, wave='sine', phase0=0.0, duty=0.5):
    """Oscillator over a per-sample frequency curve f (chirp): sine, saw, square (duty) with PolyBLEP anti-aliasing."""
    f = np.asarray(f, float)
    ph = _phase(f, sr) + phase0
    if wave == 'sine':
        return np.sin(ph)
    t = np.mod(ph / TAU, 1.0)
    dt = np.clip(np.abs(f) / sr, 1e-9, 0.5)
    if wave == 'saw':
        return 2 * t - 1 - _blep(t, dt)
    if wave == 'square':
        y = np.where(t < duty, 1.0, -1.0) + _blep(t, dt) - _blep(np.mod(t - duty + 1.0, 1.0), dt)
        return y - (2 * duty - 1)
    raise ValueError(wave)


def env_ar(n, a, a_curve=2.0, r_curve=1.6):
    """Attack over a samples (u^a_curve), release over the remaining n - a samples ((1 - u)^r_curve), no sustain."""
    a = int(np.clip(a, 1, n - 1)) if n > 2 else 1
    e = np.zeros(n)
    e[:a] = (np.arange(a) / a) ** a_curve
    r = n - a
    e[a:] = (1 - np.arange(r) / r) ** r_curve
    return e


def env_exp(n, sr, decay, attack=0.001, hold=0.0):
    """Raised-cosine attack, hold, exponential decay exp(-t / decay)."""
    t = np.arange(n) / sr
    e = np.exp(-np.maximum(t - attack - hold, 0.0) / max(decay, 1e-4))
    na = int(round(attack * sr))
    if na > 1:
        e[:na] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(na) / na)
    return e


def am(rate, depth, sr=SR):
    """Amplitude modulation 1 - depth * (0.5 - 0.5 cos phi), phi = 2 pi * integral(rate) (snare-roll pulses)."""
    return 1 - np.asarray(depth) * (0.5 - 0.5 * np.cos(_phase(rate, sr)))


def drive(x, k):
    """tanh saturation with drive k, output peak = input peak."""
    m = float(np.max(np.abs(x))) + 1e-12
    return np.tanh(k * x / m) / np.tanh(k) * m


def sat(x, k, asym=0.0, os_=2):
    """Saturation with drive k on the peak-normalised signal (output peak = input peak): tanh, asym > 0 adds even
    harmonics (an offset tanh with the DC removed), 2x oversampled so high drives do not alias."""
    x = np.asarray(x, float)
    m = float(np.max(np.abs(x))) + 1e-12
    if k <= 0:
        return x
    up = ss.resample_poly(x / m, os_, 1, axis=0) if os_ > 1 else x / m
    y = np.tanh(k * up + asym) - np.tanh(asym)
    y = ss.resample_poly(y, 1, os_, axis=0)[:len(x)] if os_ > 1 else y
    if asym:
        y = filt(y, 'hp', 12.0, SR, 2)                # the rectified DC of the even harmonics
    return y / (float(np.max(np.abs(y))) + 1e-12) * m


def soft_clip(x, ceil=1.0, knee_db=6.0, os_=4):
    """Transparent-ish soft clipper: linear below ceil - knee, then a tanh knee that approaches ceil (C1 at the
    knee); 4x oversampled. Shaves the first milliseconds of transients by a few dB instead of a limiter's gain dip."""
    x = np.asarray(x, float)
    th = ceil * 10 ** (-knee_db / 20.0)
    if float(np.max(np.abs(x))) <= th:
        return x
    up = ss.resample_poly(x, os_, 1, axis=0)
    a = np.abs(up)
    over = a > th
    up[over] = np.sign(up[over]) * (th + (ceil - th) * np.tanh((a[over] - th) / (ceil - th)))
    return ss.resample_poly(up, 1, os_, axis=0)[:len(x)]


def peq(x, f0, gain_db, q=0.9, sr=SR):
    """RBJ peaking EQ (bell) at f0 with gain_db."""
    if not gain_db:
        return x
    A = 10 ** (gain_db / 40.0)
    w = TAU * f0 / sr
    al = math.sin(w) / (2 * q)
    b = np.array([1 + al * A, -2 * math.cos(w), 1 - al * A])
    a = np.array([1 + al / A, -2 * math.cos(w), 1 - al / A])
    return ss.lfilter(b / a[0], a / a[0], x, axis=0)


def shelf(x, f0, gain_db, high=True, sr=SR):
    """RBJ shelving EQ (slope 1): high shelf (high=True) or low shelf above / below f0."""
    if not gain_db:
        return x
    A = 10 ** (gain_db / 40.0)
    w = TAU * f0 / sr
    cw, al = math.cos(w), math.sin(w) / 2 * math.sqrt(2)
    s = 2 * math.sqrt(A) * al
    if high:
        b = np.array([A * ((A + 1) + (A - 1) * cw + s), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - s)])
        a = np.array([(A + 1) - (A - 1) * cw + s, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - s])
    else:
        b = np.array([A * ((A + 1) - (A - 1) * cw + s), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - s)])
        a = np.array([(A + 1) + (A - 1) * cw + s, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - s])
    return ss.lfilter(b / a[0], a / a[0], x, axis=0)


def click(sr=SR, dur_ms=1.5, fc=None, q=1.2, hp_hz=None, rng=None, tail_ms=6.0):
    """Short white-noise burst in a cosine window, band-passed at fc (Q) or high-passed; peak 1."""
    n = _n(dur_ms / 1000.0, sr)
    x = noise(n, 'white', rng) * np.hanning(n + 2)[1:-1]
    x = np.concatenate([x, np.zeros(_n(tail_ms / 1000.0, sr))])
    if fc:
        x = biquad(x, 'bp', fc, q, sr)
    elif hp_hz:
        x = hp(x, hp_hz, sr, 2)
    return x / (np.max(np.abs(x)) + 1e-12)


def partials(n, sr, f0, ratios, decays, rng):
    """Inharmonic partials with individual exponential decays and random phases (metal ring)."""
    t = np.arange(n) / sr
    y = np.zeros(n)
    for r, d in zip(ratios, decays):
        y += np.sin(TAU * f0 * r * t + rng.uniform(0, TAU)) * np.exp(-t / d)
    return y / (np.max(np.abs(y)) + 1e-12)


def fm(n, sr, fc, ratio, index, amp):
    """Two-operator FM: sin(2 pi fc t + index(t) sin(2 pi ratio fc t)) * amp(t); fc may be a curve."""
    fc = np.broadcast_to(np.asarray(fc, float), (n,))
    return np.sin(_phase(fc, sr) + np.asarray(index) * np.sin(_phase(fc * ratio, sr))) * amp


def chord(n, sr, root, ratios, voices=2, detune_c=3.0, wave='saw', rng=None, stereo=False):
    """Chord of oscillators (each note `voices` voices detuned +-detune_c cents); stereo spreads the voices."""
    rng = rng if rng is not None else np.random.default_rng(0)
    y = np.zeros((n, 2))
    for r in ratios:
        for v in range(voices):
            c = detune_c * (np.linspace(-1, 1, voices)[v] if voices > 1 else 0.0)
            s = osc(np.full(n, root * r * 2 ** (c / 1200.0)), sr, wave, phase0=rng.uniform(0, TAU))
            p = (np.linspace(-0.6, 0.6, voices)[v] if (stereo and voices > 1) else 0.0)
            y += pan(s, p)
    y /= len(ratios) * voices
    return y if stereo else y.mean(axis=1)


def bell(x, width):
    """Bell weight over x (e.g. log2(f / 500)) with width (sigma) in the same units."""
    return np.exp(-0.5 * (np.asarray(x) / width) ** 2)


def crush(x, bits=8, sr_hz=None, sr=SR):
    """Bit crusher: sample-and-hold to sr_hz without anti-aliasing, then quantise to `bits` (peak-relative)."""
    y = np.asarray(x, float)
    if sr_hz and sr_hz < sr:
        step = sr / float(sr_hz)
        idx = (np.floor(np.arange(len(y)) / step) * step).astype(int)
        y = y[np.minimum(idx, len(y) - 1)]
    pk = float(np.max(np.abs(y))) + 1e-12
    q = 2.0 ** (bits - 1)
    return np.round(y / pk * q) / q * pk


def pan(y, p):
    """Equal-power pan / balance (centre = unity); p scalar or per-sample in [-1, 1]; mono in -> stereo out."""
    th = (np.clip(p, -1, 1) + 1) * np.pi / 4
    gl, gr = np.sqrt(2) * np.cos(th), np.sqrt(2) * np.sin(th)
    if np.ndim(y) == 1:
        return np.stack([y * gl, y * gr], 1)
    return np.stack([y[:, 0] * gl, y[:, 1] * gr], 1)


def pan_move(y, pts, n=None):
    """Pan along a path of (u, p) points (u = fraction of length)."""
    return pan(y, curve(len(y) if n is None else n, pts))


def width(y, w):
    """Mid/side width multiplier (0 = mono, 1 = unchanged)."""
    m = (y[:, 0] + y[:, 1]) / 2
    s = (y[:, 0] - y[:, 1]) / 2 * w
    return np.stack([m + s, m - s], 1)


def spread(c, s1, s2, w):
    """Centre layer + two uncorrelated side copies at width w (no delays: no comb filter in mono)."""
    w = np.asarray(w, float)
    return np.stack([c + w * s1, c + w * s2], 1)


@functools.lru_cache(maxsize=12)
def _verb_ir(sr, rt60, damp_hz, seed):
    rng = _rng(seed, 77)
    nir = _n(min(rt60 * 1.1, 6.0), sr)
    t = np.arange(nir) / sr
    ir = np.stack([noise(nir, 'white', rng), noise(nir, 'white', rng)], 1) * np.exp(-6.91 * t / rt60)[:, None]
    ir = lp(ir, damp_hz, sr, 2)
    fi = min(nir, _n(0.003, sr))
    ir[:fi] *= np.linspace(0, 1, fi)[:, None]
    ir /= np.sqrt(np.sum(ir ** 2, axis=0, keepdims=True)) + 1e-12
    ir.setflags(write=False)
    return ir


def verb(x, sr=SR, rt60=1.0, wet_db=-12.0, pre_ms=12.0, damp_hz=6000.0, hp_hz=150.0, seed=0, tail=True):
    """Convolution reverb with a synthetic response: two decorrelated noises x exp(-6.91 t / RT60), low-passed at
    damp_hz (damper), unit energy, pre-delay; the send is mono-summed and high-passed (hp_hz).
    Returns dry + wet; tail=False keeps the input length (tail cut)."""
    x = _st(x)
    ir = _verb_ir(int(sr), round(float(rt60), 4), float(damp_hz), int(seed))
    nir = len(ir)
    npre = int(round(pre_ms * sr / 1000.0))
    src = x.mean(axis=1)
    if hp_hz:
        src = hp(src, hp_hz, sr, 2)
    wet = np.stack([ss.oaconvolve(src, ir[:, c]) for c in range(2)], 1) * db(wet_db)
    n_out = len(x) + npre + nir if tail else len(x)
    y = np.zeros((n_out, 2))
    y[:len(x)] += x[:n_out]
    m = max(0, min(n_out - npre, len(wet)))
    y[npre:npre + m] += wet[:m]
    return y


def reverse(y):
    return np.ascontiguousarray(y[::-1])


def fade(y, sr=SR, in_ms=0.0, out_ms=0.0):
    """Raised-cosine fade in / out (ms)."""
    y = np.array(y, float)
    n = len(y)
    for ms, head in ((in_ms, True), (out_ms, False)):
        k = min(n, int(round(ms * sr / 1000.0))) if ms > 0 else 0
        if k > 1:
            w = 0.5 - 0.5 * np.cos(np.pi * np.arange(k) / k)
            w = w if head else w[::-1]
            if y.ndim == 2:
                w = w[:, None]
            if head:
                y[:k] *= w
            else:
                y[n - k:] *= w
    return y


def mono_below(y, f=150.0, sr=SR):
    """Everything below f in mono (centre), the rest untouched (zero-phase split)."""
    lo = filt(y, 'lp', f, sr, 4, zero_phase=True)
    return (y - lo) + lo.mean(axis=1, keepdims=True)


# ============================================================================ loudness (ITU-R BS.1770)
def _kw_coefs(sr):
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = math.tan(math.pi * f0 / sr)
    Vh, Vb = 10 ** (G / 20), (10 ** (G / 20)) ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    b1 = np.array([(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0])
    a1 = np.array([1.0, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0])
    f0, Q = 38.13547087602444, 0.5003270373238773
    K = math.tan(math.pi * f0 / sr)
    a2 = np.array([1.0, 2 * (K * K - 1) / (1 + K / Q + K * K), (1 - K / Q + K * K) / (1 + K / Q + K * K)])
    return (b1, a1), (np.array([1.0, -2.0, 1.0]), a2)


def kweight(x, sr=SR):
    """K-weighting (pre-filter shelf + RLB high-pass) along axis 0."""
    (b1, a1), (b2, a2) = _kw_coefs(sr)
    return ss.lfilter(b2, a2, ss.lfilter(b1, a1, np.asarray(x, float), axis=0), axis=0)


def _ms_db(yk):
    """Loudness (LUFS) of an already K-weighted block: -0.691 + 10 log10(sum over channels of mean square)."""
    if len(yk) == 0:
        return -np.inf
    p = float(np.mean(np.sum(_st(yk) ** 2, axis=1)))
    return -0.691 + 10 * math.log10(p) if p > 1e-20 else -np.inf


def lufs_integrated(x, sr=SR):
    """BS.1770-4 integrated loudness (400 ms blocks, 75 % overlap, -70 LUFS absolute and -10 LU relative gates)."""
    yk = _st(kweight(x, sr))
    p = np.sum(yk ** 2, axis=1)
    blk, hop = int(0.4 * sr), int(0.1 * sr)
    if len(p) < blk:
        return _ms_db(yk)
    cs = np.concatenate([[0.0], np.cumsum(p)])
    st = np.arange(0, len(p) - blk + 1, hop)
    z = (cs[st + blk] - cs[st]) / blk
    with np.errstate(divide='ignore'):
        L = -0.691 + 10 * np.log10(np.maximum(z, 1e-30))
    za = z[L > -70]
    if not len(za):
        return -np.inf
    thr = -0.691 + 10 * math.log10(za.mean()) - 10
    zg = z[(L > -70) & (L > thr)]
    return -0.691 + 10 * math.log10(zg.mean())


def true_peak_db(x, sr=SR):
    up = ss.resample_poly(_st(x), 4, 1, axis=0)
    m = float(np.max(np.abs(up))) if up.size else 0.0
    return 20 * math.log10(m) if m > 0 else -np.inf


def phone_delta(y, sr=SR, win=0.4):
    """Card phone check: loudness of the first `win` s after a 4th-order 180 Hz high-pass minus the full loudness."""
    seg = _st(y)[:_n(win, sr)]
    return _ms_db(kweight(hp(seg, 180, sr, 4), sr)) - _ms_db(kweight(seg, sr))


# ============================================================================ analysis helpers (tests / demo)
def rms_env(y, sr=SR, win_ms=10.0):
    """Sliding RMS (centered, window win_ms) of the channel sum, per sample."""
    m = np.mean(_st(y), axis=1) if np.ndim(y) == 2 else np.asarray(y, float)
    return np.sqrt(np.maximum(uniform_filter1d(m * m, max(1, int(win_ms * sr / 1000)), mode='constant'), 0.0))


def centroid(y, sr=SR, n_fft=2048, hop=256, fmin=20.0):
    """Spectral centroid per STFT frame -> (t, Hz)."""
    m = np.mean(_st(y), axis=1)
    f, t, Z = ss.stft(m, sr, nperseg=n_fft, noverlap=n_fft - hop, boundary=None, padded=False)
    S = np.abs(Z)
    k = f >= fmin
    c = (S[k] * f[k, None]).sum(0) / (S[k].sum(0) + 1e-12)
    return t, c


def _attack_idx(y, rel_db=-20.0):
    a = np.max(np.abs(_st(y)), axis=1)
    thr = a.max() * db(rel_db)
    i = np.nonzero(a >= thr)[0]
    return int(i[0]) if len(i) else 0


def _rms_peak_idx(y, sr):
    return int(np.argmax(rms_env(y, sr, 10.0)))


# ============================================================================ keys and pitch
_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
_KK_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
_KK_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def _pc(root):
    """Pitch class (C = 0) from 'A', 'C#', 'Db', 'F#m', 'A minor', an int, or a key dict; None if unknown."""
    if root is None or isinstance(root, bool):
        return None
    if isinstance(root, dict):
        return _pc(root.get('pc', root.get('root')))
    if isinstance(root, (int, np.integer)):
        return int(root) % 12
    m = re.match(r'^\s*([A-Ga-g])\s*([#b\u266f\u266d]?)', str(root))
    if not m:
        return None
    return (_PC[m.group(1).upper()] + {'#': 1, '\u266f': 1, 'b': -1, '\u266d': -1}.get(m.group(2), 0)) % 12


def _mode(root, mode=None):
    if mode:
        return 'minor' if str(mode).lower().startswith('min') else 'major'
    if isinstance(root, dict):
        return _mode(root.get('root'), root.get('mode'))
    s = str(root or '')
    return 'minor' if re.match(r'^\s*[A-Ga-g][#b\u266f\u266d]?\s*(m(?!aj)|min)', s) else 'major'


def _root_hz(root, lo, hi):
    """Frequency of a root (name / pitch class / Hz as float / key dict) moved into the octave [lo, hi)."""
    if root is None or isinstance(root, bool):
        return None
    if isinstance(root, (float, np.floating)):
        f = float(root)
    else:
        pc = _pc(root)
        if pc is None:
            return None
        f = 440.0 * 2 ** ((pc - 9) / 12.0)
    while f >= hi:
        f /= 2
    while f < lo:
        f *= 2
    return f


def chroma_profile(track, sr=SR):
    """Pitch-class profile (C = 0) of a track: ed_audio's decoder / sample rate (22.05 kHz), but a long STFT
    (8192 = 2.7 Hz bins, 55 Hz - 2 kHz, log magnitudes, triangular weight around each semitone): ed_audio's own
    chroma (1024-point FFT, 21.5 Hz bins) cannot separate bass notes (E2 lands in the F bin)."""
    import ed_audio as A
    if isinstance(track, str):
        y = A.load_audio(track)
    else:
        m = np.mean(_st(track), axis=1)
        y = ss.resample_poly(m, 147, 320) if sr == 48000 else ss.resample_poly(m, A.SR, sr)
    if len(y) < A.SR or float(np.max(np.abs(y))) < 1e-5:
        return None
    f, _, Z = ss.stft(y, A.SR, nperseg=8192, noverlap=8192 - 2048, boundary=None, padded=False)
    M = np.abs(Z)
    k = (f >= 55) & (f <= 2000)
    midi = 69 + 12 * np.log2(f[k] / 440.0)
    r = np.round(midi)
    pc = (r % 12).astype(int)
    L = np.log1p(100 * M[k] / (M.max() + 1e-12)) * np.maximum(0.0, 1 - 2 * np.abs(midi - r))[:, None]
    return np.array([L[pc == p].sum() for p in range(12)])


def key_root(track, sr=SR):
    """Key of the music: Krumhansl-Kessler correlation of chroma_profile() with the 24 key profiles.
    -> {"root": "A", "pc": 9, "mode": "minor", "conf", "r", "margin", "f1_hz", "alt"} or None.
    conf = r_best * min(1, margin / 0.1), margin = r_best - best r with another tonic: the raw correlation is high
    even when wrong (relative keys share the chords), the margin is what makes the tonic trustworthy. The cards use
    the key only when conf >= 0.6 (else sub drop f1 = 32 Hz, no tonal riser / chord layers)."""
    prof = chroma_profile(track, sr)
    if prof is None or prof.sum() <= 0:
        return None
    best = []
    for mode, kk in (('major', _KK_MAJ), ('minor', _KK_MIN)):
        for t in range(12):
            best.append((float(np.corrcoef(prof, np.roll(kk, t))[0, 1]), t, mode))
    best.sort(reverse=True)
    r, t, mode = best[0]
    alt = next(b for b in best[1:] if b[1] != t)
    margin = r - alt[0]
    return dict(root=NOTE_NAMES[t], pc=t, mode=mode, conf=round(max(0.0, r) * min(1.0, margin / 0.1), 3),
                r=round(r, 3), margin=round(margin, 3), f1_hz=round(_root_hz(t, 27.5, 55.0), 2),
                alt=dict(root=NOTE_NAMES[alt[1]], mode=alt[2], r=round(alt[0], 3)))


def music_grid(track, sr=SR):
    """bpm / beats / downbeats (seconds from the start of `track`) via ed_audio.analyze."""
    import ed_audio as A
    fd, path = tempfile.mkstemp(suffix='.wav', prefix='edsfx_')
    os.close(fd)
    try:
        _write_wav(path, _st(track), sr, codec='pcm_s16le')
        r = A.analyze(path)
        return dict(bpm=r['bpm'], beats=r['beats'], downbeats=r['downbeats'], steady=r['steady'])
    finally:
        os.remove(path)


def _note_len(note, bpm=None, beats=None, at=None):
    """'1/16' -> seconds (whole note = 4 beats; local beat interval from real beats when given), float -> float."""
    if isinstance(note, (int, float, np.floating)):
        return float(note)
    m = re.match(r'^\s*(\d+)\s*/\s*(\d+)\s*$', str(note))
    if not m:
        raise ValueError(f'bad note length {note!r}')
    frac = int(m.group(1)) / int(m.group(2))
    beat = 60.0 / (bpm or 120.0)
    if beats is not None and len(beats) >= 3 and at is not None:
        b = np.asarray(beats, float)
        i = int(np.clip(np.searchsorted(b, at), 1, len(b) - 1))
        d = np.diff(b[max(0, i - 2):i + 2])
        if len(d) and np.all(d > 0):
            beat = float(np.median(d))
    return 4 * beat * frac


# ============================================================================ recipes
# Each recipe returns (y (N, 2) float64, meta) with meta['peak'] = designed peak sample when it differs from
# the 10 ms RMS maximum (risers, reverse sounds: the cut at the end).
# Styles (params style=...): 'cinematic' (default: big transient + body + sub + hall), 'trap' (distorted 808 body,
# clap snap, short room; phonk / hip-hop / sport edits) and 'clean' (tight, little drive, short room; product,
# explainer, UGC). style_of() also accepts genre names.
STYLES = ('cinematic', 'trap', 'clean')
_STYLE_ALIASES = {
    'cinematic': 'cinematic', 'epic': 'cinematic', 'trailer': 'cinematic', 'film': 'cinematic', 'drama': 'cinematic',
    'teaser': 'cinematic', 'motivation': 'cinematic', 'travel': 'cinematic', 'action': 'cinematic',
    'trap': 'trap', 'phonk': 'trap', 'hiphop': 'trap', 'hip-hop': 'trap', 'hip_hop': 'trap', 'drill': 'trap',
    'viral': 'trap', 'sport': 'trap', 'fanedit': 'trap', 'edm': 'trap', '808': 'trap',
    'clean': 'clean', 'minimal': 'clean', 'product': 'clean', 'explainer': 'clean', 'ugc': 'clean', 'calm': 'clean',
    'fashion': 'clean', 'clips': 'clean', 'corporate': 'clean', 'vlog': 'clean', 'podcast': 'clean', 'talk': 'clean'}


def style_of(s, default='cinematic'):
    """'cinematic' | 'trap' | 'clean' from a style or genre name (None / unknown -> default)."""
    if s is None:
        return default
    return _STYLE_ALIASES.get(str(s).strip().lower(), default)


def _vary(P, rng, st=2.0):
    """Card variation per placement: frequencies x 2^(+-st/12), decays / length +-15 %, level +-1.5 dB."""
    if not P.get('vary', True):
        return 1.0, 1.0, 0.0
    u = rng.uniform(-1, 1, 3)
    return 2 ** (u[0] * st / 12.0), 1 + 0.15 * u[1], 1.5 * u[2]


def _demo_source(sr, dur, seed=0):
    """Stand-in 'track' for music-based kinds when synth() is called without a source: 120 BPM kick/hat/chord."""
    n = _n(dur, sr)
    t = np.arange(n) / sr
    y = np.zeros(n)
    rng = _rng(seed, 55)
    for b in np.arange(0, dur, 0.5):
        k = int(b * sr)
        m = min(n - k, _n(0.4, sr))
        tt = np.arange(m) / sr
        y[k:k + m] += 0.9 * np.sin(_phase(45 + 100 * np.exp(-tt / 0.03), sr)) * np.exp(-tt / 0.15)
    for b in np.arange(0.25, dur, 0.5):
        k = int(b * sr)
        m = min(n - k, _n(0.06, sr))
        y[k:k + m] += 0.25 * hp(noise(m, 'white', rng), 7000) * np.exp(-np.arange(m) / sr / 0.015)
    y += 0.25 * chord(n, sr, 220.0, [1, 1.189, 1.498], 2, 6, 'saw', rng) * (0.6 + 0.4 * np.cos(TAU * 2 * t))
    return _st(lp(y, 9000) * 0.6)


# ---------------------------------------------------------------- whoosh (sfx.whoosh)
WHOOSH = {
    'air': dict(D=0.5, color='pink', fc=(450, 3200, 700), q=(1.5, 2.5, 1.5), peak=0.6, ac=2.0, rc=1.6, w=0.5,
                hp=120, lp=12000, verb=(0.4, -14, 12, 6000, 150), pan=0.4),
    'swish': dict(D=0.22, color='white', fc=(1500, 6500, 4000), q=(3.5, 3.5, 3.5), peak=0.7, ac=2.5, rc=1.3,
                  w=0.6, hp=400, lp=14000, verb=(0.2, -18, 8, 8000, 300), pan=0.4, tone=-18),
    'heavy': dict(D=1.1, color='pink', fc=(220, 1800, 320), q=(1.1, 1.1, 1.1), peak=0.62, ac=2.0, rc=1.6, w=0.7,
                  hp=40, lp=12000, verb=(1.0, -10, 20, 6000, 150), pan=0.4, sub=(85, 70, 42), sub_db=-8, drive=2.0),
    'orbit': dict(D=2.5, color='pink', fc=(220, 1800, 320), q=(1.1, 1.1, 1.1), peak=0.62, ac=2.0, rc=1.6, w=0.7,
                  hp=40, lp=12000, verb=(1.5, -10, 20, 6000, 150), pan=0.5, sub=(85, 70, 42), sub_db=-8, drive=2.0),
}


# whoosh layers on top of the moving air band: body (low noise swelling with the pass, weight), whistle (narrow
# resonant noise riding a doppler curve: high while approaching, falling past the peak) and, in trap style, a
# 5-14 kHz sizzle with a sharper envelope; mild saturation and a presence shelf. (dB relative to the air layer)
_WHOOSH_STYLE = {
    'cinematic': dict(body=dict(air=-10.0, swish=None, heavy=-4.0, orbit=-6.0), whistle=-20.0, top=None, drive=1.6,
                      shelf=2.0, fmul=1.0, dmul=1.0),
    'trap': dict(body=dict(air=-14.0, swish=None, heavy=-6.0, orbit=-8.0), whistle=-14.0, top=-8.0, drive=2.5,
                 shelf=3.0, fmul=1.2, dmul=0.85, verb=(0.3, -16, 8, 9000, 300)),
    'clean': dict(body=dict(air=None, swish=None, heavy=-12.0, orbit=-12.0), whistle=None, top=None, drive=0.0,
                  shelf=1.0, fmul=1.0, dmul=1.0, verb=(0.3, -18, 8, 7000, 200)),
}


def _whoosh(variant, sr, D, seed, P):
    s = dict(WHOOSH[variant])
    st = _WHOOSH_STYLE[style_of(P.get('style'))]
    for k in ('fc', 'q', 'peak'):
        if k in P:
            s[k] = P[k]
    fmul, dmul, lvl = _vary(P, _rng(seed, 1), 2.0)
    fmul *= st['fmul'] if 'fc' not in P else 1.0
    D = float(D) if D else s['D'] * dmul * st['dmul']
    n = _n(D, sr)
    pk = int(round(float(s['peak']) * (n - 1)))
    pu = pk / max(n - 1, 1)
    fc = curve(n, [(0, s['fc'][0] * fmul), (pu, s['fc'][1] * fmul), (1, s['fc'][2] * fmul)], log=True)
    q = curve(n, [(0, s['q'][0]), (pu, s['q'][1]), (1, s['q'][2])])
    rn = _rng(seed, 2)
    X = tv_filter(np.stack([noise(n, s['color'], rn) for _ in range(3)], 1), 'bp', fc, q, sr)
    e = env_ar(n, pk, s['ac'], s['rc'])
    X *= e[:, None]
    X /= np.max(np.abs(X[:, 0])) + 1e-12
    c = X[:, 0].copy()
    u = _u(n)
    if 'tone' in s:                                   # swish whistle: sine on fc * 0.5 at -18 dB
        c += db(s['tone']) * np.sin(_phase(fc * 0.5, sr)) * e
    if 'sub' in s:                                    # heavy low layer 85 -> 70 -> 42 Hz at -8 dB
        fs = curve(n, [(0, s['sub'][0] * fmul), (pu, s['sub'][1] * fmul), (1, s['sub'][2] * fmul)], log=True)
        c += db(s['sub_db']) * np.sin(_phase(fs, sr)) * e
    bdb = st['body'].get(variant)
    if bdb is not None and P.get('body', True):       # weight: low noise swelling with the pass
        fb = curve(n, [(0, 140 * fmul), (pu, 420 * fmul), (1, 170 * fmul)], log=True)
        B = tv_filter(noise(n, 'pink', _rng(seed, 6)), 'lp', fb, 0.8, sr) * e ** 1.3
        c += db(bdb) * B / (np.max(np.abs(B)) + 1e-12)
    side = np.zeros(n)
    if st['whistle'] is not None and P.get('whistle', True):
        dop = 1.0 + 0.3 * np.tanh(6.0 * (pu - u))     # doppler: high on approach, falls past the peak
        W = tv_filter(noise(n, 'white', _rng(seed, 7)), 'bp', np.clip(fc * 1.6 * dop, 300, 0.4 * sr), 7.0, sr) * e
        c += db(st['whistle']) * W / (np.max(np.abs(W)) + 1e-12)
    if st['top'] is not None:                         # trap sizzle: 5-14 kHz, sharper envelope, wide
        T = bp(noise(n, 'white', _rng(seed, 8)), 5000, 14000, sr, 2) * env_ar(n, pk, 3.0, 2.2)
        side = db(st['top']) * T / (np.max(np.abs(T)) + 1e-12)
    y = spread(c, X[:, 1] + side, X[:, 2] - side, s['w'] * float(P.get('width', 1.0)))
    k = max(float(s.get('drive') or 0.0), st['drive'])
    if k > 0:
        y = sat(y, k)
    # pan -p -> 0 (at the peak) -> +p along the camera direction; scalar 'pan' = offset, list = explicit path
    pp = P.get('pan', 0.0)
    if isinstance(pp, (list, tuple)):
        p0, p1 = float(pp[0]), float(pp[-1])
        path = [(0, p0), (pu, (p0 + p1) / 2), (1, p1)]
    else:
        d = float(P.get('dir', 1.0))
        p = s['pan'] * (1 if d >= 0 else -1)
        path = [(0, -p + float(pp)), (pu, float(pp)), (1, p + float(pp))]
    path = [(u_, float(np.clip(v, -0.6, 0.6))) for u_, v in path]
    y = pan_move(y, path)
    y = lp(hp(y, s['hp'], sr, 2), s['lp'], sr, 4)
    y = shelf(y, 3000.0, st['shelf'], True, sr)
    rt, wet, pre, damp, vhp = st.get('verb') or s['verb']
    y = verb(y, sr, P.get('rt60', rt), P.get('wet_db', wet), pre, damp, vhp, seed=seed)
    return y, dict(peak=pk, lvl=lvl, dur=D)


def _reverse_whoosh(variant, sr, D, seed, P):
    """Forward: pink noise -> band-pass 3.2 kHz -> 450 Hz (Q 1.4), attack 3 ms, decay exp(-t / 0.22 D), reverb
    RT60 0.7 D at -4 dB; reversed; the cut (2-6 ms) is the anchor. Styles: cinematic adds a low body (-8 dB),
    trap a 4-12 kHz top (-6 dB) and more drive; a short 'snap' at the cut makes the end land."""
    st = style_of(P.get('style'))
    fmul, dmul, lvl = _vary(P, _rng(seed, 1), 2.0)
    D = float(D) if D else 0.9 * dmul * (0.85 if st == 'trap' else 1.0)
    n = _n(D, sr)
    t = np.arange(n) / sr
    rn = _rng(seed, 2)
    fc = curve(n, [(0, 3200 * fmul * (1.2 if st == 'trap' else 1.0)), (1, 450 * fmul)], log=True)
    X = tv_filter(np.stack([noise(n, 'pink', rn) for _ in range(3)], 1), 'bp', fc, 1.4, sr)
    env = env_exp(n, sr, 0.22 * D, attack=0.003)
    X *= env[:, None]
    X /= np.max(np.abs(X[:, 0])) + 1e-12
    c = X[:, 0].copy()
    if st == 'cinematic' and P.get('body', True):
        B = lp(noise(n, 'pink', _rng(seed, 6)), 400, sr, 2) * env_exp(n, sr, 0.3 * D, attack=0.003)
        c += db(-8.0) * B / (np.max(np.abs(B)) + 1e-12)
    side = np.zeros(n)
    if st == 'trap':
        T = bp(noise(n, 'white', _rng(seed, 8)), 4000, 12000, sr, 2) * np.exp(-t / (0.15 * D))
        side = db(-6.0) * T / (np.max(np.abs(T)) + 1e-12)
    y = spread(c, X[:, 1] + side, X[:, 2] - side, 0.5 * float(P.get('width', 1.0)))
    y = verb(y, sr, 0.7 * D, P.get('wet_db', -4.0), 10, 6000, 150, seed=seed, tail=False)
    y = lp(hp(y, 120 if st != 'cinematic' else 60, sr, 2), 12000, sr, 4)
    y = reverse(y)
    if st != 'clean':
        y = sat(y, 2.2 if st == 'trap' else 1.5)
    y = shelf(y, 3000.0, 2.0 if st != 'clean' else 0.0, True, sr)
    y = fade(y, sr, in_ms=15, out_ms=float(P.get('cut_ms', 4.0)))
    return y, dict(peak=len(y) - 1, lvl=lvl, dur=D)


# ---------------------------------------------------------------- riser + swell (sfx.riser)
def _agc(X, sr, win=0.05):
    """Flatten the running RMS (the swept filters' own gain change) so the level curve alone sets the level."""
    p = np.mean(_st(X) ** 2, axis=1) if X.ndim == 2 else X ** 2
    r = np.sqrt(np.maximum(uniform_filter1d(p, max(1, int(win * sr)), mode='nearest'), 0.0)) + 1e-9
    return X / (r[:, None] if X.ndim == 2 else r)


def _roll(n, sr, bpm, depth=0.6):
    """Snare-roll pulses: 1/4 -> 1/8 -> 1/16 -> 1/32 notes by quarters of the length, depth 0 -> 0.6."""
    u = _u(n)
    q = np.minimum((u * 4).astype(int), 3)
    rate = (bpm / 60.0) * np.array([1.0, 2.0, 4.0, 8.0])[q]
    return am(rate, depth * u, sr)


def _noise_riser(n, sr, seed, P, bpm):
    u = _u(n)
    fc = 400.0 * 20.0 ** (u ** 1.3)                   # 400 Hz -> 8 kHz, faster towards the end
    q = 0.8 + 2.2 * u ** 1.5
    rn = _rng(seed, 2)
    X = tv_filter(np.stack([noise(n, 'white', rn) for _ in range(3)], 1), 'bp', fc, q, sr)
    X = tv_filter(X, 'hp', np.maximum(150.0, 0.5 * fc), 0.7071, sr)
    X = tv_filter(X, 'lp', np.minimum(np.maximum(1500.0, 3 * fc), 0.45 * sr), 0.7071, sr)
    X = _agc(X, sr)
    g = db(-30.0 * (1 - u ** 1.5))                    # level curve: -30 dB -> 0 dB
    if P.get('roll'):
        g = g * _roll(n, sr, bpm)
    y = spread(X[:, 0], X[:, 1], X[:, 2], (0.2 + 0.7 * u) * float(P.get('width', 1.0)))
    return y * g[:, None]


def _sweep_layer(n, sr, seed, f0=180.0, f1=1800.0):
    """Uplifter glide: two detuned saws sweeping f0 -> f1 (exponential, faster at the end), low-passed above them,
    level-flattened; a glissando, so it does not clash with the track's key."""
    u = _u(n)
    f = f0 * (f1 / f0) ** (u ** 1.4)
    rn = _rng(seed, 9)
    x = sum(osc(f * 2 ** (c / 1200.0), sr, 'saw', rn.uniform(0, TAU)) for c in (-9.0, 9.0)) / 2
    x = tv_filter(x, 'lp', np.minimum(3.0 * f, 0.45 * sr), 0.9, sr)
    return _agc(x, sr)


_RISER_SWEEP = {'cinematic': -14.0, 'trap': -10.0, 'clean': None}


def _riser(variant, sr, D, seed, P):
    bpm = float(P.get('bpm') or 120.0)
    st = style_of(P.get('style'))
    if P.get('roll') is None and st == 'trap' and variant in ('noise', 'tonal'):
        P = dict(P, roll=True)                        # trap builds roll
    if variant == 'endless':
        return _endless(sr, D, seed, P)
    if variant == 'reverse_cymbal':
        return _reverse_cymbal(sr, D, seed, P)
    D = float(D) if D else {'short': 0.5}.get(variant, 2.0)
    n = _n(D, sr)
    u = _u(n)
    if variant == 'tonal':
        root = _root_hz(P.get('root'), 110.0, 220.0) or 110.0
        f = root * 2.0 ** (float(P.get('oct', 2.0)) * u ** 1.3)
        voices = int(P.get('voices', 5))
        rn = _rng(seed, 3)
        x = sum(osc(f * 2 ** (c / 1200.0), sr, 'saw', rn.uniform(0, TAU)) for c in np.linspace(-12, 12, voices))
        x = tv_filter(x / voices, 'lp', 600.0 * 15.0 ** u, 0.7071, sr)
        x = _agc(x, sr) * db(-30.0 * (1 - u ** 1.5))
        if P.get('roll'):
            x = x * _roll(n, sr, bpm)
        y = _st(x) + db(-6) * _noise_riser(n, sr, seed, P, bpm)
        rt = 1.2
    else:                                             # noise / short
        y = _noise_riser(n, sr, seed, P, bpm)
        rt = 1.5 if variant == 'noise' else 0.8
        sw = _RISER_SWEEP[st] if P.get('sweep', True) else None
        if sw is not None:
            g = db(-30.0 * (1 - u ** 1.5)) * (_roll(n, sr, bpm) if P.get('roll') else 1.0)
            y = y + db(sw) * _st(_sweep_layer(n, sr, seed) * g)
    if st == 'trap':
        y = sat(y, 1.8)
    y = verb(y, sr, rt, -12.0, 15, 7000, 300, seed=seed, tail=False)
    y = fade(y, sr, in_ms=5, out_ms=float(P.get('cut_ms', 10.0)))   # reverb tail cut at the anchor
    return y, dict(peak=n - 1, dur=D)


def _reverse_cymbal(sr, D, seed, P):
    """6 square oscillators at 205 Hz x (1, 1.48, 1.8, 2.55, 2.63, 3.9) + white noise, HPF 5.5 kHz,
    exp(-t / 0.45 s) + reverb 1.2 s, reversed: rises 1-2.5 s and stops dead."""
    D = float(D) if D else 1.5
    n = _n(D, sr)
    rn = _rng(seed, 2)
    sq = sum(osc(np.full(n, 205.0 * r), sr, 'square', rn.uniform(0, TAU)) for r in (1, 1.48, 1.8, 2.55, 2.63, 3.9)) / 6
    X = np.stack([sq + 0.6 * noise(n, 'white', rn), sq + 0.6 * noise(n, 'white', rn)], 1)
    X = lp(hp(X, 5500, sr, 4), 16000, sr, 2) * env_exp(n, sr, 0.45, attack=0.002)[:, None]
    y = verb(X, sr, 1.2, -6.0, 8, 12000, 2000, seed=seed, tail=False)
    y = fade(reverse(y), sr, in_ms=20, out_ms=3)
    return y, dict(peak=n - 1, dur=D)


def _endless(sr, D, seed, P):
    """Endless-rise riser: 7 sines an octave apart, f_k = 40 * 2^((k + rate t) mod 7), bell weight over log2(f / 500)
    (width 1.3 oct) x sin^2 window over the 7 octaves (zero at the wrap: no seam); constant level."""
    D = float(D) if D else 4.0
    n = _n(D, sr)
    t = np.arange(n) / sr
    rate = float(P.get('rate', 0.5))
    y = np.zeros(n)
    for k in range(7):
        pos = np.mod(k + rate * t, 7.0)
        f = 40.0 * 2.0 ** pos
        y += np.sin(_phase(f, sr)) * bell(np.log2(f / 500.0), 1.3) * np.sin(np.pi * pos / 7.0) ** 2
    y = fade(y, sr, in_ms=300, out_ms=300)
    y = verb(_st(y), sr, 1.5, -14.0, 15, 6000, 200, seed=seed, tail=False)
    return y, dict(peak=n - 1, dur=D)


def _swell(variant, sr, D, seed, P):
    """Pink noise (LPF 2.5 kHz) + chord (tonic, third, fifth, octave; 2 voices +-3 cents) 50/50, sin^2 rise over
    0.7 D then exp(-t / 0.35 s), width 0.9, reverb 2.5 s at -8 dB, no cut. Peak at 0.7 D."""
    D = float(D) if D else 2.0
    nb = _n(D, sr)
    n = nb + _n(1.0, sr)
    t = np.arange(n) / sr
    a = int(0.7 * nb)
    e = np.where(np.arange(n) < a, np.sin(0.5 * np.pi * np.arange(n) / max(a, 1)) ** 2,
                 np.exp(-np.maximum(t - a / sr, 0) / 0.35))
    rn = _rng(seed, 2)
    X = lp(np.stack([noise(n, 'pink', rn) for _ in range(3)], 1), 2500, sr, 2)
    X /= np.sqrt(np.mean(X[:, 0] ** 2)) + 1e-12
    y = spread(X[:, 0], X[:, 1], X[:, 2], 0.9 * float(P.get('width', 1.0))) * 0.5
    root = _root_hz(P.get('root'), 110.0, 220.0)
    if P.get('chord', True):
        root = root or 130.81
        third = 2 ** (3 / 12) if _mode(P.get('root'), P.get('mode')) == 'minor' else 2 ** (4 / 12)
        ch = lp(chord(n, sr, root, [1, third, 1.5, 2.0], 2, 3.0, 'saw', _rng(seed, 3), stereo=True), 2500, sr, 2)
        ch /= np.sqrt(np.mean(np.sum(ch ** 2, 1) / 2)) + 1e-12
        y = y + 0.5 * ch
    y = y * e[:, None]
    y = verb(y, sr, 2.5, -8.0, 20, 5000, 200, seed=seed, tail=True)
    y = fade(y[:nb + _n(2.0, sr)], sr, out_ms=500)
    return y, dict(peak=a, dur=D)


# ---------------------------------------------------------------- impact (sfx.impact)
# Layered hit: click (0-3 ms) + snap / clap (1-6 kHz, 5-40 ms) + saturated pitch-dropping body + knock (150-900 Hz,
# the "thud" small speakers reproduce) + crunch (distorted 0.3-3.5 kHz debris) + phase-locked sub tail + ring / chord
# + reverb; body and sub are saturated alone (harmonics, no intermodulation of the transients), a light glue
# saturation and a presence bell go over the sum, everything below 150 Hz is mono.
# body = (f_end, f_drop, tau_f, tau_a): f(t) = f_end + f_drop exp(-t / tau_f), amplitude exp(-t / tau_a).
IMPACT = {
    'punch': dict(D=0.6, body=(52, 113, 0.028, 0.20), drive=3.0, click=-6.0, snap=(1500, 6000, 0.02, -6.0),
                  knock=(150, 700, 0.07, -3.0), verb=(0.5, -16, 8, 6000, 200), pres=(3000, 3.0), glue=2.0,
                  fade=0.06, phone=-6.0),
    'boom': dict(D=3.0, body=(42, 83, 0.06, 0.38), drive=3.0, click=-5.0, snap=(1200, 5000, 0.018, -5.0),
                 knock=(120, 600, 0.08, -5.0), crunch=(300, 3500, 0.12, -7.0), sub=(40, 0.03, 0.7, -5.0),
                 verb=(2.5, -10, 20, 5000, 200), pres=(2500, 2.0), glue=1.4, fade=0.25, phone=-6.0),
    'soft': dict(D=0.7, body=(55, 35, 0.03, 0.15), drive=1.3, click=None, knock=(250, 900, 0.04, -3.0), lp=2500,
                 verb=(0.4, -18, 8, 5000, 150), glue=1.1, fade=0.08, phone=-10.0),
}
IMPACT['metal'] = dict(IMPACT['boom'], D=3.5, ring=-6.0, verb=(3.0, -10, 20, 6000, 200), fade=0.3)
IMPACT['stretched'] = dict(IMPACT['boom'], D=5.0, body=(28, 58, 0.12, 0.76), sub=(28, 0.03, 1.4, -5.0),
                           snap=(900, 3500, 0.03, -10.0), crunch=(200, 2500, 0.24, -12.0), click=-9.0,
                           verb=(4.0, -8, 25, 4500, 200), fade=0.4)
IMPACT['chord'] = dict(IMPACT['boom'], chord=-6.0)
IMPACT['stop'] = dict(IMPACT['punch'], stop=0.5)

# style changes applied on top of the (cinematic) recipe: 'mul' scales tau_a of the body
_IMPACT_STYLE = {
    'trap': dict(drive=6.0, asym=0.15, body_end=48.0, mul=1.8, click=-3.0,
                 clap=(900, 6500, 0.035, -3.0, (0.0, 0.009, 0.018)), knock_db=-8.0, crunch=None, sub=None,
                 verb_short=(0.35, -18, 6, 6000, 250), verb_long=(0.9, -14, 10, 6000, 250), pres=(3500, 3.0), glue=1.8),
    'clean': dict(drive=1.5, mul=0.8, click=-8.0, snap=(2000, 7000, 0.006, -9.0), knock_db=-4.0, crunch=None,
                  verb_short=(0.35, -20, 6, 6000, 200), verb_long=(0.6, -18, 8, 6000, 200), pres=(3000, 1.5),
                  glue=1.15, boom_D=1.2, sub_db=-9.0, sub_tau=0.4),
}


_PLR_TARGET = {'cinematic': 10.0, 'trap': 9.5, 'clean': 11.0}


def _impact_spec(variant, style, mud=False):
    s = _impact_spec_style(variant, style)
    if mud:                                           # the track has a strong kick here: leave it the sub octave
        fb, fa, tf, ta = s['body']
        s['body'] = (max(75.0, fb * 1.6), fa, tf, ta)
        s.pop('sub', None)
    return s


def _impact_spec_style(variant, style):
    s = dict(IMPACT[variant])
    m = _IMPACT_STYLE.get(style)
    if not m or variant == 'soft':
        return s
    fb, fa, tf, ta = s['body']
    long_ = s['verb'][0] > 1.0
    if style == 'trap':
        s['body'] = (m['body_end'] * fb / 42.0 if fb < 42 else m['body_end'], fa, tf, ta * m['mul'])
        s.update(drive=m['drive'], asym=m['asym'], click=m['click'], glue=m['glue'], pres=m['pres'])
        s.pop('snap', None)
        s['clap'] = m['clap']
        s['knock'] = s['knock'][:3] + (m['knock_db'],)
        s.pop('crunch', None)
        s.pop('sub', None)
        s['verb'] = m['verb_long'] if long_ else m['verb_short']
        s['post'] = 0.45 if long_ else 0.2
        if long_:
            s['D'] = min(s['D'], 2.0)
            s['fade'] = 0.2
    else:                                             # clean
        s['body'] = (fb, fa, tf, ta * m['mul'])
        s.update(drive=m['drive'], click=m['click'], snap=m['snap'], glue=m['glue'], pres=m['pres'])
        s['knock'] = s['knock'][:3] + (m['knock_db'],)
        s.pop('crunch', None)
        if 'sub' in s:
            f, att, _, _ = s['sub']
            s['sub'] = (f, att, m['sub_tau'], m['sub_db'])
        s['verb'] = m['verb_long'] if long_ else m['verb_short']
        if long_:
            s['D'] = min(s['D'], m['boom_D'] if variant != 'stretched' else 2.5)
            s['fade'] = 0.15
    return s


def _burst(n, sr, lo, hi, tau, rn, starts=(0.0,), width=0.5, attack=0.0003):
    """Stereo band-passed noise burst(s) with exponential decay tau (clap: several starts 9 ms apart)."""
    t = np.arange(n) / sr
    e = np.zeros(n)
    for k, t0 in enumerate(starts):
        tt = np.maximum(t - t0, 0.0)
        g = np.exp(-tt / (tau if k == len(starts) - 1 else min(tau, 0.006))) * (t >= t0)
        na = max(2, int(attack * sr))
        i0 = int(round(t0 * sr))
        if i0 < n:
            g[i0:i0 + na] *= np.linspace(0, 1, min(na, n - i0))
        e = np.maximum(e, g)
    X = bp(np.stack([noise(n, 'white', rn) for _ in range(3)], 1), lo, hi, sr, 2) * e[:, None]
    X /= np.max(np.abs(X[:, 0])) + 1e-12
    return spread(X[:, 0], X[:, 1], X[:, 2], width)


def _impact(variant, sr, D, seed, P):
    style = style_of(P.get('style'))
    s = _impact_spec(variant, style, bool(P.get('mud')))
    fmul, dmul, lvl = _vary(P, _rng(seed, 1), 1.0)       # tone +-1 semitone, decays +-15 %
    D = float(D) if D else s['D']
    n = _n(D, sr)
    t = np.arange(n) / sr
    rn = _rng(seed, 2)
    nz_click = click(sr, 2.0, hp_hz=2000, rng=rn, tail_ms=0)
    hn = min(n, _n(0.6, sr))                            # transient layers live in the first 0.6 s
    snap = None
    if s.get('clap'):
        lo, hi, tau, dbv, starts = s['clap']
        snap = (_burst(hn, sr, lo * fmul, hi * fmul, tau * dmul, rn, starts, 0.45), dbv)
    elif s.get('snap'):
        lo, hi, tau, dbv = s['snap']
        snap = (_burst(hn, sr, lo * fmul, hi * fmul, tau * dmul, rn, (0.0,), 0.5), dbv)
    knock = None
    if s.get('knock'):
        lo, hi, tau, dbv = s['knock']
        k = bp(noise(hn, 'white', rn), lo * fmul, hi * fmul, sr, 2) * np.exp(-t[:hn] / (tau * dmul))
        knock = (k / (np.max(np.abs(k)) + 1e-12), dbv)
    crunch = None
    if s.get('crunch'):
        lo, hi, tau, dbv = s['crunch']
        gr = np.abs(lp(noise(n, 'white', _rng(seed, 5)), 60.0, sr, 2))        # granular debris
        gr = 0.35 + gr / (np.max(gr) + 1e-12)
        X = bp(np.stack([noise(n, 'pink', rn) for _ in range(3)], 1), lo, hi, sr, 2)
        X = sat(X * (np.exp(-t / (tau * dmul)) * gr)[:, None], 3.0)
        X /= np.max(np.abs(X[:, 0])) + 1e-12
        crunch = (spread(X[:, 0], X[:, 1], X[:, 2], 0.6), dbv)
    ring_f0 = float(P.get('f0') or rn.uniform(180, 400)) * fmul
    ring_ph = _rng(seed, 4)
    root = _root_hz(P.get('root'), 110.0, 220.0)

    fb, fa, tf, ta = s['body']
    ph_body = _phase(fmul * (fb + fa * np.exp(-t / (tf * dmul))), sr)
    body = np.sin(ph_body) * env_exp(n, sr, ta * dmul, 0.0008)
    if s.get('drive'):
        body = sat(body, s['drive'], s.get('asym', 0.0))
    if s.get('post'):                                 # trap: the distorted 808 still decays
        body = body * np.exp(-t / (s['post'] * dmul))
    if 'sub' in s and s['sub'] and P.get('sub_tail', True):
        # sub tail at the body's end frequency, phase-locked to the body: no beating / cancellation
        _, att, dec, dbv = s['sub']
        body = body + db(dbv) * np.sin(ph_body) * env_exp(n, sr, dec * dmul, att)
    tonal = np.zeros(n)
    if 'ring' in s:
        if P.get('ring_mode', 'partials') == 'fm':
            r = fm(n, sr, ring_f0, 1.41, 8 * np.exp(-t / 0.3), np.exp(-t / (0.9 * dmul)))
        else:
            r = partials(n, sr, ring_f0, [1, 1.47, 2.09, 2.56, 3.14, 3.87], np.linspace(1.2, 0.4, 6) * dmul, ring_ph)
        r = bp(r, 300, 5000, sr, 2)
        tonal += db(s['ring']) * r / (np.max(np.abs(r)) + 1e-12)
    if 'chord' in s and root:
        ch = chord(n, sr, root, [1, 1.5, 2.0], 2, 10.0, 'saw', _rng(seed, 3)) * env_exp(n, sr, 0.4 * dmul, 0.005)
        ch = lp(ch, 4000, sr, 2)
        tonal += db(s['chord']) * ch / (np.max(np.abs(ch)) + 1e-12)

    def render(boost):
        y = _st(body + tonal)                         # weight layers -> glue saturation
        if knock is not None:
            m = min(n, len(knock[0]))
            y[:m] += _st(db(knock[1] + boost) * knock[0][:m])
        if crunch is not None:
            m = min(n, len(crunch[0]))
            y[:m] += db(crunch[1] + boost) * crunch[0][:m]
        y = sat(y, s.get('glue', 1.2))
        if s.get('click') is not None:                # transients stay clean on top
            c = np.zeros(n)
            c[:len(nz_click)] = nz_click[:n]
            y = y + _st(db(s['click'] + boost) * c)
        if snap is not None:
            m = min(n, len(snap[0]))
            y[:m] += db(snap[1] + boost) * snap[0][:m]
        if s.get('pres'):
            y = peq(y, s['pres'][0], s['pres'][1], 0.8, sr)
        if s.get('lp'):
            y = lp(y, s['lp'], sr, 2)
        return y

    def finish(y):
        rt, wet, pre, damp, vhp = s['verb']
        y = verb(y, sr, rt * (dmul if rt > 1 else 1.0), wet, pre, damp, vhp, seed=seed, tail=False)
        y = mono_below(y, 150.0, sr)
        return fade(y, sr, out_ms=s['fade'] * 1000)

    boost = 0.0
    dry = render(boost)
    head = _n(0.45, sr)                                # the phone check only looks at the first 400 ms (causal)
    while P.get('phone_fix', True) and phone_delta(finish(dry[:head]), sr) < s['phone'] and boost < 10.0:
        boost += 2.0                                   # raise the transient / knock layers until it reads on phones
        dry = render(boost)
    y = finish(dry)
    meta = dict(lvl=lvl, dur=D, phone_boost_db=boost, style=style)
    stop = P.get('stop', s.get('stop'))
    if stop:
        meta['stop'] = stop
    return y, meta


# ---------------------------------------------------------------- sub drop (sfx.sub_drop)
SUB = {'classic': dict(f0=110.0, f1=32.0, tau=0.35, decay=0.55, D=2.0),
       'short': dict(f0=90.0, f1=36.0, tau=0.15, decay=0.3, D=0.9),
       'long': dict(f0=70.0, f1=24.0, tau=0.8, decay=1.2, D=3.5, rumble=-14.0),
       'reverse': dict(f0=28.0, f1=70.0, D=0.9)}


def _sub_drop(variant, sr, D, seed, P):
    s = SUB[variant]
    D = float(D) if D else s['D']
    n = _n(D, sr)
    t = np.arange(n) / sr
    u = _u(n)
    f1 = P.get('f1') or _root_hz(P.get('root'), 27.5, 55.0)
    if variant == 'reverse':
        f = curve(n, [(0, float(P.get('f0', s['f0']))), (1, float(f1 or s['f1']) if P.get('f1') else s['f1'])], log=True)
        env = db(-30.0 * (1 - u))
    else:
        f1 = float(f1 or s['f1'])
        f0 = float(P.get('f0', s['f0']))
        f = f1 + (f0 - f1) * np.exp(-t / float(P.get('tau', s['tau'])))
        env = env_exp(n, sr, float(P.get('decay', s['decay'])), attack=0.005, hold=0.08)
    ph = _phase(f, sr)                                  # starts at zero phase: no click
    st = style_of(P.get('style'))
    hdb = list(P.get('harm_db', {'clean': [0, -12, -18, -24, -30], 'trap': [0, -6, -9, -13, -17]}.get(
        st, [0, -8, -12, -16, -20])))
    asym = 0.25 if st == 'trap' else 0.0
    lpf = 900 if st == 'trap' else 600

    def render(boost, k):
        x = sum(db(h + (boost if i else 0.0)) * np.sin((i + 1) * ph) for i, h in enumerate(hdb))
        if variant == 'reverse':                       # env_db after the drive: the -30 -> 0 dB rise stays exact
            x = (sat(x, k, asym) if asym else drive(x, k)) * env
        else:
            x = sat(x * env, k, asym) if asym else drive(x * env, k)
        x = hp(lp(x, lpf, sr, 4), 22, sr, 2)
        if 'rumble' in s:
            r = lp(noise(n, 'brown', _rng(seed, 2)), 90, sr, 2) * env
            x = x + db(s['rumble']) * r / (np.max(np.abs(r)) + 1e-12) * np.max(np.abs(x))
        return _st(fade(x, sr, out_ms=5 if variant == 'reverse' else 50))

    boost, k = 0.0, float(P.get('drive', {'trap': 4.5, 'clean': 1.5}.get(st, 2.5)))
    y = render(boost, k)
    lim = {'trap': -9.0, 'clean': -14.0}.get(st, -12.0)
    while P.get('phone_fix', variant != 'reverse') and phone_delta(y, sr) < lim and boost < 6:
        boost += 2.5                                   # card: harmonics +2-3 dB or drive up to 3
        k = min(3.0, k + 0.25)
        y = render(boost, k)
    meta = dict(dur=D, f_end=float(f[-1]), phone_boost_db=boost, style=st)
    if variant == 'reverse':
        meta['peak'] = n - 1
    return y, meta


# ---------------------------------------------------------------- glitch, click (sfx.glitch)
def _edge(x, sr, ms=0.2):
    return fade(x, sr, in_ms=ms, out_ms=ms)


def _glitch(variant, sr, D, seed, P):
    r = _rng(seed, 3)
    if variant == 'burst':
        return _glitch_burst(sr, D, seed, P, r)
    if variant == 'static':
        D = float(D) if D else 0.2
        n = _n(D, sr)
        X = hp(np.stack([noise(n, 'white', r), noise(n, 'white', r)], 1), 1000, sr, 2)
        steps, k = np.zeros(n), 0
        while k < n:                                   # stepped envelope, steps 5-20 ms
            m = _n(r.uniform(0.005, 0.02), sr)
            steps[k:k + m] = r.uniform(0.15, 1.0)
            k += m
        X *= steps[:, None]
        crack = np.zeros(n)
        nimp = int(r.uniform(100, 300) * D)            # sparse crackle impulses 100-300 / s
        crack[r.integers(0, n, max(nimp, 1))] = r.uniform(1.0, 2.5, max(nimp, 1)) * r.choice([-1, 1], max(nimp, 1))
        crack = hp(crack, 1500, sr, 2) * 4.0
        y = X / (np.max(np.abs(X)) + 1e-12) + _st(crack)
        y = fade(y, sr, in_ms=0.2, out_ms=3)
        holes = int(min(r.integers(1, 4), max(1, D // 0.045)))
        gate, reg = [], D / holes
        for h in range(holes):                         # 1-3 separate cuts of 30-120 ms in the music
            L = min(r.uniform(0.03, 0.12), 0.8 * reg)
            a = h * reg + r.uniform(0, max(reg - L, 0.0))
            gate.append((round(a, 4), round(a + L, 4), -40.0))
        return y, dict(dur=D, gate=gate)
    if variant == 'hiss':                              # tape hiss bed: pink noise, HPF 2 kHz, flat
        D = float(D) if D else 4.0
        n = _n(D, sr)
        y = hp(np.stack([noise(n, 'pink', r), noise(n, 'pink', r)], 1), 2000, sr, 2)
        return fade(y, sr, in_ms=50, out_ms=50), dict(dur=D)
    if variant == 'transition':                        # swish -> bitcrush 6 bit / 8 kHz -> 2-3 holes of 15-30 ms
        D = float(D) if D else 0.36
        n = _n(D, sr)
        pk = int(0.7 * (n - 1))
        fc = curve(n, [(0, 1500), (pk / (n - 1), 6500), (1, 4000)], log=True)
        X = tv_filter(np.stack([noise(n, 'white', r) for _ in range(3)], 1), 'bp', fc, 3.5, sr)
        X *= env_ar(n, pk, 2.5, 1.3)[:, None]
        y = spread(X[:, 0], X[:, 1], X[:, 2], 0.6 * float(P.get('width', 1.0)))
        y = np.stack([crush(y[:, c], int(P.get('bits', 6)), 8000, sr) for c in range(2)], 1)
        for _ in range(int(r.integers(2, 4))):
            L = _n(r.uniform(0.015, 0.03), sr)
            choices = [a for a in range(0, n - L, _n(0.005, sr)) if abs(a + L / 2 - pk) > _n(0.03, sr)]
            if choices:
                a = int(r.choice(choices))
                y[a:a + L] = 0.0
        return hp(y, 200, sr, 2), dict(peak=pk, dur=D)
    if variant == 'trill':                             # clicks 12-24 / s, centre 2-6 kHz, +-3 dB + 6-bit grain -12 dB
        D = float(D) if D else 1.0
        rate = float(P.get('rate_hz', 16.0))
        n = _n(D, sr)
        y = np.zeros(n)
        for tk in np.arange(0, D, 1.0 / rate):
            c = click(sr, 1.5, fc=r.uniform(2000, 6000), q=1.2, rng=r) * db(r.uniform(-3, 3))
            k = int(tk * sr)
            m = min(len(c), n - k)
            y[k:k + m] += c[:m]
        g = np.stack([crush(0.3 * noise(n, 'white', r), 6, 12000, sr) for _ in range(2)], 1)
        y = _st(y) + db(-12) * g / (np.max(np.abs(g)) + 1e-12)
        return hp(fade(y, sr, in_ms=2, out_ms=5), 200, sr, 2), dict(dur=D)
    if variant == 'blips':                             # 8-bit arpeggio: 3-4 square steps of 30-60 ms
        steps = int(P.get('steps', r.integers(3, 5)))
        D = float(D) if D else 0.04 * steps
        duty = float(P.get('duty', r.choice([0.5, 0.125])))
        base = float(P.get('freq', r.uniform(500, 900)))
        semis = [0, 4, 7, 12, 16][:steps]
        if str(P.get('dir', 'up')) == 'down':
            semis = semis[::-1]
        L = _n(D / steps, sr)
        y = np.concatenate([fade(osc(np.full(L, base * 2 ** (s_ / 12.0)), sr, 'square', duty=duty), sr, 1, 1)
                            for s_ in semis])
        return _st(y), dict(dur=D)
    if variant == 'censor':                            # 1 kHz sine for the word, 5 ms fades; the word is muted
        D = float(D) if D else 0.4
        n = _n(D, sr)
        y = np.sin(TAU * float(P.get('freq', 1000.0)) * np.arange(n) / sr)
        return _st(fade(y, sr, 5, 5)), dict(dur=D, mute_voice=bool(P.get('mute_voice', True)))
    if variant == 'crush':                             # preview only; in mix() it bit-crushes the track itself
        D = float(D) if D else 1.0
        src = P.get('source')
        src = _demo_source(sr, D, seed) if src is None else _fit(np.asarray(src, float), _n(D, sr))
        y = (1 - P.get('mix', 0.8)) * src + P.get('mix', 0.8) * np.stack(
            [crush(src[:, c], int(P.get('bits', 8)), P.get('sr_hz', 11025), sr) for c in range(2)], 1)
        return y, dict(dur=D)
    raise KeyError(f'glitch variant {variant!r}')


def _glitch_burst(sr, D, seed, P, r):
    """40-400 ms chain of 8-40 ms slices: bit-crushed noise / square or FM bleep / retrigger of the track from the
    attack / silence; level -6..0 dB, pan +-0.7; hard 0.2 ms edges; HPF 200 Hz. meta gate: music gated to -40 dB
    in silent slices, -4.5 dB elsewhere."""
    D = float(D) if D else 0.25
    n = _n(D, sr)
    mixw = dict(P.get('mix') or {'crush': 0.3, 'bleep': 0.25, 'retrig': 0.25, 'gap': 0.2})
    src = P.get('source')
    if P.get('bounds'):
        cuts = sorted({0, n} | {int(round(b * sr)) for b in P['bounds'] if 0 < b < D})
    else:
        cuts, k = [0], 0
        while k < n:
            k = min(n, k + _n(r.choice([0.008, 0.012, 0.016, 0.024, 0.032, 0.04]), sr))
            cuts.append(k)
        if len(cuts) > 2 and cuts[-1] - cuts[-2] < _n(0.004, sr):
            cuts.pop(-2)
    names = list(mixw)
    p = np.array([mixw[k] for k in names], float)
    p /= p.sum()
    y = np.zeros((n, 2))
    gate, kinds = [], []
    first = None
    for j, (a, b) in enumerate(zip(cuts[:-1], cuts[1:])):
        L = b - a
        typ = str(r.choice(names, p=p))
        if j == 0 and typ in ('gap', 'retrig'):        # hard entry at full level on the first frame
            typ = 'crush' if src is None else 'retrig'
        if typ == 'retrig' and src is None:            # no track given: retrigger the burst's own first slice
            seg = np.resize(first, L) if first is not None else noise(L, 'white', r)
            seg = seg / (np.max(np.abs(seg)) + 1e-12)
            y[a:b] = pan(_edge(seg, sr), float(r.uniform(-0.7, 0.7))) * float(db(r.uniform(-6, 0)))
            gate.append((a / sr, b / sr, -4.5))
            kinds.append('retrig')
            continue
        lvl = 1.0 if j == 0 else float(db(r.uniform(-6, 0)))
        pj = float(r.uniform(-0.7, 0.7))
        if typ == 'crush':
            seg = crush(noise(L, 'white', r) * 0.5, int(r.integers(4, 7)), sr / float(r.integers(4, 13)), sr)
        elif typ == 'bleep':
            f = float(np.exp(r.uniform(np.log(300), np.log(3000))))
            if r.random() < 0.5:
                seg = osc(np.full(L, f), sr, 'square')
            else:
                seg = fm(L, sr, f, 2.7, r.uniform(2, 6), 1.0)
        elif typ == 'retrig':
            seg = np.asarray(src, float)[:L]
            seg = _fit(_st(seg), L)
        else:
            seg = np.zeros(L)
        seg = seg / (np.max(np.abs(seg)) + 1e-12) if typ != 'gap' else seg
        if first is None and typ != 'gap':
            first = seg if seg.ndim == 1 else seg.mean(axis=1)
        y[a:b] = pan(_edge(seg, sr), pj) * lvl
        gate.append((a / sr, b / sr, -40.0 if typ == 'gap' else -4.5))
        kinds.append(typ)
    return hp(y, 200, sr, 2), dict(dur=D, gate=gate, slices=kinds)


def _click(variant, sr, D, seed, P):
    r = _rng(seed, 3)
    if variant == 'tick':                              # 1.5 ms noise burst -> band-pass 2-5 kHz, Q 1.2
        fc = float(P.get('fc') or r.uniform(2000, 5000))
        y = click(sr, float(P.get('dur_ms', 1.5)), fc=fc, q=float(P.get('q', 1.2)), rng=r)
        if P.get('body', True):                        # a 1.2-2 kHz "tock" under it: reads as a tick, not a spike
            m = _n(0.004, sr)
            tb = np.arange(m) / sr
            bdy = np.sin(TAU * r.uniform(1200, 2000) * tb) * np.exp(-tb / 0.0012)
            y = np.concatenate([y, np.zeros(max(0, m - len(y)))])
            y[:m] += db(-6) * bdy
            y /= np.max(np.abs(y)) + 1e-12
        return _st(y), dict(dur=len(y) / sr, fc=fc)
    if variant == 'shutter':                           # 3 kHz click + 1.5 kHz click at +40 ms (-4 dB) + 180 Hz 15 ms
        n = _n(0.075, sr)
        y = np.zeros(n)
        c1, c2 = click(sr, 1.5, fc=3000, q=1.2, rng=r), click(sr, 1.5, fc=1500, q=1.2, rng=r)
        y[:len(c1)] += c1
        k = _n(0.04, sr)
        y[k:k + len(c2)] += db(-4) * c2
        m = _n(0.015, sr)
        y[:m] += db(-10) * np.sin(TAU * 180 * np.arange(m) / sr) * np.hanning(m)
        return _st(y), dict(dur=n / sr)
    if variant == 'pop':                               # short pitch-dropping blip (UI "pop")
        n = _n(0.04, sr)
        t = np.arange(n) / sr
        y = np.sin(_phase(380 + 720 * np.exp(-t / 0.006), sr)) * env_exp(n, sr, 0.012, attack=0.0005)
        c = click(sr, 1.0, fc=4000, q=1.0, rng=r)
        y[:len(c)] += db(-12) * c
        return _st(y), dict(dur=n / sr)
    raise KeyError(f'click variant {variant!r}')


# ---------------------------------------------------------------- music-based kinds (preview via synth)
def _src_or_demo(P, sr, dur, seed):
    src = P.get('source')
    if src is None:
        return _demo_source(sr, dur + 0.5, seed)
    return _st(np.asarray(src, float))


def _scratch(variant, sr, D, seed, P):
    D = float(D) if D else 0.35
    src = _src_or_demo(P, sr, 0.5, seed)
    y = scratch_track(_fit(src, max(len(src), _n(D + 0.3, sr))), 0.0, D, sr, float(P.get('rate_hz', 4.5)),
                      float(P.get('amp', 2.5)))
    return y[:_n(D, sr)], dict(dur=D)


def _tape_stop_kind(variant, sr, D, seed, P):
    D = float(D) if D else (0.3 if variant == 'start' else 0.6)
    src = _src_or_demo(P, sr, D, seed)
    src = _fit(src, max(len(src), _n(D + 0.1, sr)))
    y = tape_stop(src, 0.0, D, sr, float(P.get('curve', 1.5)), start=(variant == 'start'))
    return y[:_n(D, sr)], dict(dur=D)


def _stutter_kind(variant, sr, D, seed, P):
    bpm = float(P.get('bpm') or 120.0)
    accel = P.get('accel', 'default' if variant == 'build' else None)
    slots = _stutter_slots(P.get('slice', '1/16'), int(P.get('repeats', 4 if variant == 'build' else 8)), accel, bpm,
                           P.get('beats'), 0.0)
    total = sum(slots)
    src = _src_or_demo(P, sr, total, seed)
    src = _fit(src, max(len(src), _n(total + 0.1, sr)))
    y = audio_stutter(src, 0.0, P.get('slice', '1/16'), int(P.get('repeats', 4 if variant == 'build' else 8)), sr,
                      accel=accel, xfade_ms=float(P.get('xfade_ms', 2.0)),
                      pitch_step_st=float(P.get('pitch_step_st', 0.0)), bpm=bpm)
    return y[:_n(total, sr)], dict(dur=total)


def _filter_build_kind(variant, sr, D, seed, P):
    D = float(D) if D else 2.0
    src = _src_or_demo(P, sr, D, seed)
    y = music_filter(_fit(src, _n(D, sr)), 'hp', P.get('f', (20, 400)), (0.0, D), sr, q=float(P.get('q', 1.0)),
                     ease=P.get('ease', 'inQuad'), reset_at=D + 1)
    return y, dict(peak=_n(D, sr) - 1, dur=D)


# ============================================================================ registry
def _win(anchor, lo=None, hi=None):
    return (anchor, lo, hi)


_DUCK_IMPACT = dict(band=(30, 150), depth_db=4.0, attack_ms=2, hold_ms=60, release_ms=200, mode='fixed')
_DUCK_BOOM = dict(_DUCK_IMPACT, release_ms=400, wide_db=1.5)
_DUCK_SUB = dict(band=(25, 150), depth_db=6.0, attack_ms=5, release_ms=60, mode='follow')
_DUCK_RISER = dict(band=(2000, 10000), depth_db=3.0, attack_ms=50, release_ms=0, mode='follow', last=0.25)
_DUCK_WHOOSH = dict(band=(1000, 6000), depth_db=2.5, attack_ms=30, release_ms=150, mode='follow')

KINDS = {
    'whoosh': dict(default='air', align='peak', fn=_whoosh, doc='moving-air noise sweep, peak on the cut', variants={
        'air': dict(dur=0.5, range=(0.35, 0.8), rel_lu=-6, win=_win('peak', -0.2, 0.2), duck=_DUCK_WHOOSH, duck_on=False),
        'swish': dict(dur=0.22, range=(0.15, 0.3), rel_lu=-10, win=_win('peak', -0.2, 0.2), duck=_DUCK_WHOOSH, duck_on=False),
        'heavy': dict(dur=1.1, range=(0.8, 1.5), rel_lu=-4, win=_win('peak', -0.2, 0.2), duck=_DUCK_WHOOSH, duck_on=False),
        'orbit': dict(dur=2.5, range=(1.5, 3.0), rel_lu=-4, win=_win('peak', -0.2, 0.2), duck=_DUCK_WHOOSH, duck_on=False)}),
    'reverse_whoosh': dict(default='reverse', align='peak', fn=_reverse_whoosh, doc='reversed whoosh, cut on the event', variants={
        'reverse': dict(dur=0.9, range=(0.6, 1.5), rel_lu=-8, win=_win('peak', -0.4, 0.0), duck=_DUCK_WHOOSH, duck_on=False)}),
    'riser': dict(default='noise', align='peak', fn=_riser, doc='build-up ending on the resolution point', variants={
        'noise': dict(dur=2.0, range=(0.5, 4.0), rel_lu=-6, win=_win('peak', -0.4, 0.0), duck=_DUCK_RISER, duck_on=True),
        'short': dict(dur=0.5, range=(0.2, 1.0), rel_lu=-6, win=_win('peak', -0.4, 0.0), duck=_DUCK_RISER, duck_on=True),
        'tonal': dict(dur=2.0, range=(0.5, 4.0), rel_lu=-6, win=_win('peak', -0.4, 0.0), duck=_DUCK_RISER, duck_on=True, keyed=True),
        'reverse_cymbal': dict(dur=1.5, range=(1.0, 2.5), rel_lu=-6, win=_win('peak', -0.4, 0.0), duck=_DUCK_RISER, duck_on=True),
        'endless': dict(dur=4.0, range=(2.0, 30.0), rel_lu=-12, win=_win('all')),
        'filter': dict(dur=2.0, range=(1.0, 4.0), music=True)}),
    'swell': dict(default='swell', align='peak', fn=_swell, doc='soft warm rise of noise + chord, no hit', variants={
        'swell': dict(dur=2.0, range=(1.0, 3.0), rel_lu=-10, win=_win('peak', -0.2, 0.2), keyed=True)}),
    'impact': dict(default='punch', align='attack', fn=_impact, doc='low hit: click + falling body + tail', variants={
        'punch': dict(dur=0.6, rel_lu=-6, win=_win('attack', 0.0, 0.1), win2=(0.4, -4.0), duck=_DUCK_IMPACT, duck_on=True),
        'boom': dict(dur=3.0, rel_lu=-2, win=_win('attack', 0.0, 0.4), duck=_DUCK_BOOM, duck_on=True, main=True),
        'soft': dict(dur=0.7, rel_lu=-10, win=_win('attack', 0.0, 0.1), win2=(0.4, -4.0), duck=_DUCK_IMPACT, duck_on=True),
        'metal': dict(dur=3.5, rel_lu=-4, win=_win('attack', 0.0, 0.4), duck=_DUCK_BOOM, duck_on=True, main=True),
        'stretched': dict(dur=5.0, rel_lu=-4, win=_win('attack', 0.0, 0.4), duck=_DUCK_BOOM, duck_on=True, main=True),
        'chord': dict(dur=3.0, rel_lu=-4, win=_win('attack', 0.0, 0.4), duck=_DUCK_BOOM, duck_on=True, main=True, keyed=True),
        'stop': dict(dur=0.6, rel_lu=-6, win=_win('attack', 0.0, 0.1), win2=(0.4, -4.0), duck=_DUCK_IMPACT, duck_on=True)}),
    'sub_drop': dict(default='classic', align='attack', fn=_sub_drop, doc='falling sub sine with harmonics', variants={
        'classic': dict(dur=2.0, range=(1.0, 3.5), rel_lu=-6, win=_win('attack', 0.0, 0.4), duck=_DUCK_SUB, duck_on=True, keyed=True, main=True),
        'short': dict(dur=0.9, range=(0.6, 1.2), rel_lu=-6, win=_win('attack', 0.0, 0.4), duck=_DUCK_SUB, duck_on=True, keyed=True, main=True),
        'long': dict(dur=3.5, range=(2.0, 3.5), rel_lu=-6, win=_win('attack', 0.0, 0.4), duck=_DUCK_SUB, duck_on=True, keyed=True, main=True),
        'reverse': dict(dur=0.9, range=(0.6, 1.2), rel_lu=-6, win=_win('peak', -0.4, 0.0), align='peak')}),
    'glitch': dict(default='burst', align='attack', fn=_glitch, doc='digital glitch textures synced to picture', variants={
        'burst': dict(dur=0.25, range=(0.04, 0.4), rel_lu=-6, win=_win('attack', 0.0, 0.1)),
        'static': dict(dur=0.2, range=(0.08, 0.3), rel_lu=-10, win=_win('attack', 0.0, 0.1)),
        'transition': dict(dur=0.36, range=(0.3, 0.4), rel_lu=-6, win=_win('peak', -0.2, 0.2), align='peak'),
        'trill': dict(dur=1.0, range=(0.5, 2.0), rel_lu=-12, win=_win('all')),
        'blips': dict(dur=0.12, range=(0.06, 0.2), rel_lu=-10, win=_win('attack', 0.0, 0.1)),
        'censor': dict(dur=0.4, range=(0.1, 2.0), rel_lu=-6, win=_win('all')),
        'hiss': dict(dur=4.0, range=(0.5, 120.0), rel_lu=-27, win=_win('all')),
        'crush': dict(dur=1.0, range=(0.1, 8.0), music=True)}),
    'click': dict(default='tick', align='attack', fn=_click, doc='1-5 ms tick on a cut / element', variants={
        'tick': dict(dur=0.0015, rel_lu=-14, win=_win('attack', 0.0, 0.1)),
        'shutter': dict(dur=0.075, rel_lu=-14, win=_win('attack', 0.0, 0.1)),
        'pop': dict(dur=0.04, rel_lu=-14, win=_win('attack', 0.0, 0.1))}),
    'scratch': dict(default='scratch', align='attack', fn=_scratch, doc='the track scratched back and forth', variants={
        'scratch': dict(dur=0.35, range=(0.2, 0.45), music=True)}),
    'tape_stop': dict(default='stop', align='attack', fn=_tape_stop_kind, doc='the track slows to a stop (or spins up)', variants={
        'stop': dict(dur=0.6, range=(0.3, 1.0), music=True),
        'start': dict(dur=0.3, range=(0.2, 0.4), music=True)}),
    'stutter': dict(default='repeat', align='attack', fn=_stutter_kind, doc='beat repeat of a 1/16 slice of the track', variants={
        'repeat': dict(dur=None, music=True),
        'build': dict(dur=None, music=True)}),
}
KINDS['riser']['variants']['filter']['fn'] = _filter_build_kind
KINDS['glitch']['variants']['crush']['fn'] = _glitch

# other names used by move cards -> (kind, variant)
ALIASES = {
    'swish': ('whoosh', 'swish'), 'woosh': ('whoosh', 'air'), 'boom': ('impact', 'boom'), 'hit': ('impact', 'punch'),
    'beep': ('glitch', 'censor'), 'static': ('glitch', 'static'), 'tape_hiss': ('glitch', 'hiss'),
    'chiptune_blip': ('glitch', 'blips'), 'blip': ('glitch', 'blips'), 'shutter': ('click', 'shutter'),
    'pop': ('click', 'pop'), 'tick': ('click', 'tick'), 'crush': ('glitch', 'crush'), 'bitcrush': ('glitch', 'crush'),
    'reverse_cymbal': ('riser', 'reverse_cymbal'), 'beat_repeat': ('stutter', 'repeat'),
    'tape_start': ('tape_stop', 'start'), 'filter_build': ('riser', 'filter'), 'uplifter': ('riser', 'noise'),
}
# variant aliases inside a kind -> (kind, variant)
_VARIANT_ALIASES = {('whoosh', 'reverse'): ('reverse_whoosh', 'reverse'), ('riser', 'swell'): ('swell', 'swell'),
                    ('whoosh', 'whoosh'): ('whoosh', 'air'), ('sub_drop', 'suck'): ('sub_drop', 'reverse'),
                    ('glitch', 'click'): ('click', 'tick'), ('glitch', 'shutter'): ('click', 'shutter'),
                    ('glitch', 'stutter'): ('stutter', 'repeat'), ('glitch', 'tape_stop'): ('tape_stop', 'stop'),
                    ('glitch', 'scratch'): ('scratch', 'scratch'), ('impact', 'cinematic'): ('impact', 'boom'),
                    ('stutter', 'accel'): ('stutter', 'build'), ('click', 'click'): ('click', 'tick'),
                    ('glitch', 'beep'): ('glitch', 'censor'), ('glitch', 'bleep'): ('glitch', 'blips'),
                    ('glitch', 'tape_hiss'): ('glitch', 'hiss')}


def resolve(kind, variant=None):
    """(kind, variant) after aliases; KeyError for unknown kinds / variants."""
    kind = str(kind).strip().lower()
    if kind.startswith('sfx.'):
        kind = kind[4:]
    if kind not in KINDS:
        if kind not in ALIASES:
            raise KeyError(f'unknown sfx kind {kind!r}')
        kind, v0 = ALIASES[kind]
        variant = variant or v0
    variant = (str(variant).strip().lower() if variant else None) or KINDS[kind]['default']
    if (kind, variant) in _VARIANT_ALIASES:
        kind, variant = _VARIANT_ALIASES[(kind, variant)]
    if variant not in KINDS[kind]['variants']:
        raise KeyError(f'unknown variant {variant!r} of {kind!r} (have {sorted(KINDS[kind]["variants"])})')
    return kind, variant


def spec_of(kind, variant=None):
    kind, variant = resolve(kind, variant)
    s = dict(KINDS[kind]['variants'][variant])
    s.setdefault('align', KINDS[kind]['align'])
    s.setdefault('lu', NORMAL_LU.get((kind, variant), s.get('rel_lu', -6)))
    return kind, variant, s


# ============================================================================ level presets
# An event's loudness target is "event minus program" in LU: K-weighted loudness of the event minus that of the
# program without SFX (music + voice) in the variant's window (KINDS 'win'); the reference never drops below the
# program's integrated loudness - 12 LU. NORMAL_LU = the 'normal' target per variant: clearly audible (hits dominate
# their moment by >= +3 LU momentary, whooshes / riser ends sit on top of the music). Presets shift it:
LEVELS = {'light': -5.0, 'normal': 0.0, 'strong': 4.0}
_LEVEL_ALIASES = {'soft': 'light', 'low': 'light', 'subtle': 'light', 'quiet': 'light', 'medium': 'normal',
                  'default': 'normal', 'genre': 'normal', 'heavy': 'strong', 'loud': 'strong', 'hard': 'strong',
                  'high': 'strong'}
NORMAL_LU = {
    ('whoosh', 'air'): 2.0, ('whoosh', 'swish'): 0.0, ('whoosh', 'heavy'): 3.0, ('whoosh', 'orbit'): 1.0,
    ('reverse_whoosh', 'reverse'): 1.0,
    ('riser', 'noise'): 2.0, ('riser', 'short'): 1.0, ('riser', 'tonal'): 2.0, ('riser', 'reverse_cymbal'): 1.0,
    ('riser', 'endless'): -8.0, ('swell', 'swell'): -3.0,
    ('impact', 'punch'): 7.0, ('impact', 'boom'): 4.0, ('impact', 'soft'): 0.0, ('impact', 'metal'): 4.0,
    ('impact', 'stretched'): 4.0, ('impact', 'chord'): 4.0, ('impact', 'stop'): 3.0,
    ('sub_drop', 'classic'): 2.0, ('sub_drop', 'short'): 2.0, ('sub_drop', 'long'): 2.0, ('sub_drop', 'reverse'): 1.0,
    ('glitch', 'burst'): 2.0, ('glitch', 'static'): -2.0, ('glitch', 'transition'): 1.0, ('glitch', 'trill'): -6.0,
    ('glitch', 'blips'): -2.0, ('glitch', 'censor'): 0.0, ('glitch', 'hiss'): -20.0,
    ('click', 'tick'): -4.0, ('click', 'shutter'): -4.0, ('click', 'pop'): -3.0,
}
# music ducking under events, by preset: scale of the card ducks + broadband dip under hits (dB, regular / main)
_DUCK_SCALE = {'light': 0.6, 'normal': 1.0, 'strong': 1.4}
_HIT_DIP = {'light': (1.0, 2.0), 'normal': (3.0, 4.0), 'strong': (5.0, 6.0)}
# dB an event's true peak may exceed the SFX bus ceiling (its transients are soft-clipped); above it: capped
CLIP_ALLOW = {'light': 3.0, 'normal': 4.0, 'strong': 6.0}
# a user sample of unknown kind: level window = 400 ms from the attack
SAMPLE_SPEC = dict(align='attack', win=('attack', 0.0, 0.4), rel_lu=0.0, lu=0.0, dur=None)
# THE audibility rule, shared with ed_qa (its sfx check reads QA_MIN_LU and the same LEVELS): events within 150 ms
# form a group; the group's loudest 400 ms of SFX (window centres every 25 ms over the members' spans) minus the
# 3 s short-term loudness of the program without SFX (music + voice, as mixed: after every duck and the limiter)
# after the group for hits (impact, sub drop, click, glitch), centred on it otherwise, must reach the need:
# QA_MIN_LU[family] at 'normal' + the level preset (LEVELS: light -5, strong +4; a number = dB relative to normal),
# the strictest member counts; auto-level whooshes / risers / glitches / clicks under a voice need 6 dB less.
# ed_qa flags weak below need - QA_TOL; the mixer verifies the final stems and raises short groups to need +
# QA_MARGIN (within each event's headroom), deepening the music dip under hits when that is not enough.
QA_MIN_LU = {'impact': 3.0, 'whoosh': 0.0, 'riser': 0.0}
QA_FAMILY = {'impact': 'impact', 'whoosh': 'whoosh', 'reverse_whoosh': 'whoosh', 'riser': 'riser'}
QA_ATTACK = ('impact', 'sub_drop', 'click', 'glitch')
QA_UNDER_VOICE = ('whoosh', 'reverse_whoosh', 'riser', 'swell', 'glitch', 'click')
QA_GROUP_S, QA_TOL, QA_MARGIN = 0.15, 1.0, 0.5
# drop dip: the whole music under a hit that lands on a drop (music >= 3 LU louder in the second after it than in
# the second before), a main hit or a strong one: depth by preset, hold 150 ms, release 0.9 s
_DROP_DIP = {'light': 2.0, 'normal': 4.0, 'strong': 6.0}
VOICE_GROUPS = True    # voice clips of one file share one gain (the source's balance); "norm": "clip" = per clip


def qa_need(kind, level=None):
    """Audibility need (LU over the program's 3 s short-term) of one event, ed_qa's rule; None = not judged."""
    fam = QA_FAMILY.get(kind)
    if fam is None:
        return None
    try:
        off = level_offset(level if level is not None else 'normal')
    except KeyError:
        off = 0.0
    return QA_MIN_LU[fam] + off


def qa_event_need(ev, audio=None):
    """The need of one audio.sfx entry exactly as the mixer enforces it (one source of truth for ed_qa): None when not
    judged (no family: sub drop, swell, glitch, click, music kinds, a sample without a known kind; an explicit "lu"),
    else QA_MIN_LU[family] + the level preset (event level, else audio.sfx_level) + the event's gain_db trim."""
    if not isinstance(ev, dict) or ev.get('lu') is not None:
        return None
    try:
        kind, _, spec = spec_of(ev.get('kind', ''), ev.get('variant'))
    except KeyError:
        return None
    if spec.get('music'):
        return None
    lv = ev.get('level')
    lv = (audio or {}).get('sfx_level', 'normal') if lv is None else lv
    need = qa_need(kind, lv)
    return None if need is None else need + float(ev.get('gain_db', 0.0) or 0.0)


def _range_of(ev):
    """An event's "t": [t0, t1] as a sorted (t0, t1) tuple, or None."""
    t = ev.get('t') if isinstance(ev, dict) else None
    if not (isinstance(t, (list, tuple)) and len(t) == 2):
        return None
    try:
        return tuple(sorted((float(t[0]), float(t[1]))))
    except (TypeError, ValueError):
        return None


def event_anchor(ev):
    """Where an audio.sfx event lands, in output seconds (= the mixer's record 'at'): "at" + offset_ms; for a range
    "t": [t0, t1] without "at": t1 when the event is peak / end aligned (whooshes, risers, reverse sounds, swells:
    the build fills the range and lands on t1), else t0 (hits, glitches, clicks, "align": "start": they start the
    range). None = no time. (A riser / reversed sound picked from audio.sfx_dir also lands on t1.)"""
    if not isinstance(ev, dict):
        return None
    off = float(ev.get('offset_ms', 0.0) or 0.0) / 1000.0
    if ev.get('at') is not None:
        return float(ev['at']) + off
    r = _range_of(ev)
    if r is None:
        return None
    align = ev.get('align')
    if not align:
        fpath = ev.get('file') or (ev.get('params') or {}).get('file')
        try:
            align = 'attack' if (fpath and not ev.get('kind')) else spec_of(ev.get('kind', ''), ev.get('variant'))[2][
                'align']
        except KeyError:
            align = 'attack'
        if fpath and ev.get('reverse'):
            align = 'end'
    return (r[1] if align in ('peak', 'end') else r[0]) + off


_EVENT_KEYS = {'kind', 'variant', 'at', 't', 'align', 'offset_ms', 'dur', 'level', 'lu', 'rel_lu', 'gain_db', 'pan',
               'width', 'seed', 'style', 'duck', 'file', 'pitch', 'rate', 'stretch', 'reverse', 'trim_db', 'synth',
               'params', 'move', 'why', 'id', 'note', 'notes', 'group', 'part'}
_MUSIC_OPS = {'filter', 'crush', 'stutter', 'tape_stop', 'scratch', 'mute', 'gate', 'gain', 'level', 'swell',
              'fade_out', 'fade_in', 'fade'}


def validate_audio(audio, total_s=None, base_dir=None):
    """The audio block against this mixer's schema -> (errors, warnings), for ed_edl.validate / ed_plan validators.
    sfx events: a known kind / variant (aliases) OR a "file" (kind optional; then it must exist); "at" or "t":
    [t0, t1] inside the timeline; align attack|peak|start|end; level light|normal|strong (aliases) or a number;
    lu / rel_lu / gain_db / pitch / rate / stretch numbers; music_fx ops and duck rules known. Errors: the sound or op
    would be lost (unknown kind / op, missing file, no time, bad numbers); warnings: the mixer falls back (unknown
    level -> normal, unknown key ignored, unknown duck mode -> smooth, no sfx_dir -> synthesized)."""
    E, W = [], []
    au = audio or {}
    base = base_dir or au.get('base_dir')
    msg = lambda e: e.args[0] if getattr(e, 'args', None) else str(e)   # noqa: E731

    def full(p):
        p = os.path.expanduser(str(p))
        return p if (os.path.isabs(p) or not base) else os.path.join(str(base), p)
    for i, ev in enumerate(au.get('sfx') or []):
        where = f'audio.sfx[{i}]'
        if not isinstance(ev, dict):
            E.append(f'{where}: not an object')
            continue
        f = ev.get('file') or (ev.get('params') or {}).get('file')
        if f:
            if not os.path.exists(full(f)):
                E.append(f'{where}: file not found: {f}')
            if ev.get('kind'):
                try:
                    resolve(ev['kind'], ev.get('variant'))
                except KeyError:
                    W.append(f"{where}: kind {ev['kind']!r} unknown - the file plays as a generic hit")
        else:
            try:
                resolve(ev.get('kind', ''), ev.get('variant'))
            except KeyError as e:
                E.append(f'{where}: {msg(e)} (the event would be skipped)')
        at = ev.get('at')
        rng_t = _range_of(ev)
        if at is not None and (not isinstance(at, (int, float)) or isinstance(at, bool)):
            E.append(f'{where}: "at" must be a number of seconds')
        elif at is None and rng_t is None:
            E.append(f'{where}: needs "at" (seconds) or "t": [t0, t1]')
        elif total_s is not None:
            for x in ([float(at)] if at is not None else list(rng_t)):
                if not (-0.5 <= x <= float(total_s) + 0.5):
                    E.append(f'{where}: at {x:g} outside the timeline (0 .. {float(total_s):.2f} s)')
                    break
        if ev.get('align') not in (None, 'attack', 'peak', 'start', 'end'):
            E.append(f"{where}: align must be attack|peak|start|end (got {ev.get('align')!r})")
        if ev.get('level') is not None:
            try:
                level_name(ev['level'])
            except KeyError as e:
                W.append(f'{where}: {msg(e)} - normal used')
        for k in ('lu', 'rel_lu', 'gain_db', 'pitch', 'rate', 'stretch', 'dur', 'offset_ms', 'trim_db'):
            v = ev.get(k)
            if v is not None and (not isinstance(v, (int, float)) or isinstance(v, bool)):
                E.append(f'{where}: {k} must be a number')
        for k in ('rate', 'stretch'):
            if isinstance(ev.get(k), (int, float)) and ev[k] <= 0:
                E.append(f'{where}: {k} must be > 0')
        extra = set(ev) - _EVENT_KEYS
        if extra:
            W.append(f"{where}: unknown keys {sorted(extra)} ignored")
    if au.get('sfx_level') is not None:
        try:
            level_name(au['sfx_level'])
        except KeyError as e:
            W.append(f'audio.sfx_level: {msg(e)} - normal used')
    if au.get('sfx_dir') and not os.path.isdir(full(au['sfx_dir'])):
        W.append(f"audio.sfx_dir not found: {au['sfx_dir']} - sounds are synthesized")
    for i, op in enumerate(au.get('music_fx') or []):
        if not isinstance(op, dict) or op.get('op') not in _MUSIC_OPS:
            E.append(f"audio.music_fx[{i}]: unknown op {op.get('op') if isinstance(op, dict) else op!r}")
    for i, r in enumerate(au.get('duck') or []):
        if not isinstance(r, dict):
            E.append(f'audio.duck[{i}]: not an object')
        elif r.get('under') is None and (r.get('t') is None or r.get('to') is None):
            E.append(f'audio.duck[{i}]: needs "under" (voice | sfx | sfx:<kind>) or "t" + "to"')
        elif r.get('mode') not in (None, 'smooth', 'fast'):
            W.append(f"audio.duck[{i}]: mode {r.get('mode')!r} unknown - smooth used")
    return E, W


def level_name(level):
    """Preset name for a level value: 'light' | 'normal' | 'strong' (aliases), numbers -> nearest preset."""
    if level is None:
        return 'normal'
    if isinstance(level, (int, float)) and not isinstance(level, bool):
        return min(LEVELS, key=lambda k: abs(LEVELS[k] - float(level)))
    s = str(level).strip().lower()
    s = _LEVEL_ALIASES.get(s, s)
    if s not in LEVELS:
        raise KeyError(f'unknown sfx level {level!r} (have {sorted(LEVELS)})')
    return s


def level_offset(level):
    """dB offset of a level preset (or a number of dB relative to 'normal')."""
    if level is None:
        return 0.0
    if isinstance(level, (int, float)) and not isinstance(level, bool):
        return float(level)
    return LEVELS[level_name(level)]


# ============================================================================ synth
def synth_ex(kind, variant=None, sr=SR, dur=None, seed=0, **params):
    """Render one SFX -> (float32 (N, 2) at peak -6 dBFS, meta). meta['attack'] = first sample above -20 dB of the
    peak; meta['peak'] = designed peak (whoosh / swell / transition), the cut (risers, reverse sounds) or the 10 ms
    RMS maximum. Common params: pan (scalar offset or [p0, p1]), width (multiplier), hp / lp (extra filters, Hz),
    vary (seeded card variation, default True). Music-based kinds take source=(M, 2) track from the event on."""
    kind, variant, spec = spec_of(kind, variant)
    P = dict(params)
    fn = spec.get('fn', KINDS[kind]['fn'])
    y, meta = fn(variant, sr, dur, int(seed), P)
    y = _st(y)
    if kind != 'whoosh':
        w = P.get('width', 1.0)
        if w is not None and float(w) != 1.0 and kind not in ('reverse_whoosh', 'riser', 'swell', 'glitch'):
            y = width(y, float(w))
        p = P.get('pan', 0.0)
        if not isinstance(p, (list, tuple)) and p and kind not in ('sub_drop',):
            y = pan(y, float(np.clip(p, -1, 1)))
    if P.get('hp'):
        y = hp(y, float(P['hp']), sr, 2)
    if P.get('lp'):
        y = lp(y, float(P['lp']), sr, 2)
    if kind in ('impact', 'sub_drop'):
        y = mono_below(y, 150.0, sr) if kind == 'impact' else _st(y.mean(axis=1))
    meta = dict(meta)
    if kind == 'impact' and P.get('clip', True):
        # transient control (drum-bus style clipping, after any hp / lp): true peak at most _PLR_TARGET dB over the
        # loudest 400 ms, at most 4 dB shaved off the first milliseconds - denser hits that reach their loudness
        # inside the master's headroom
        plr = true_peak_db(y, sr) - _max_momentary(kweight(y, sr), 1.0, sr)
        tgt = float(P.get('plr', _PLR_TARGET.get(meta.get('style'), 10.0)))
        cd = float(np.clip(plr - tgt, 0.0, float(P.get('clip_max', 4.0))))
        if cd > 0.1:
            y = soft_clip(y, float(np.max(np.abs(y))) * db(-cd), 2.0)
        meta['clip_db'] = round(cd, 2)
    y = _norm(y) if not spec.get('music') or P.get('normalize', True) else y
    meta.update(kind=kind, variant=variant, n=len(y), sr=sr, attack=_attack_idx(y))
    if 'peak' not in meta:
        meta['peak'] = _rms_peak_idx(y, sr)
    meta['start'], meta['end'] = 0, len(y) - 1
    return y.astype(np.float32), meta


def synth(kind, variant=None, sr=SR, dur=None, seed=0, **params):
    """Render one SFX (see synth_ex) -> float32 (N, 2)."""
    return synth_ex(kind, variant, sr, dur, seed, **params)[0]


# ============================================================================ music ops (on a timeline track)
def _interp(src, pos):
    """Linear interpolation of a (M, 2) track at fractional sample positions (zeros outside)."""
    i0 = np.floor(pos).astype(int)
    fr = (pos - i0)[:, None]
    M = len(src)
    a = np.where(((i0 >= 0) & (i0 < M))[:, None], src[np.clip(i0, 0, M - 1)], 0.0)
    b = np.where(((i0 + 1 >= 0) & (i0 + 1 < M))[:, None], src[np.clip(i0 + 1, 0, M - 1)], 0.0)
    return a * (1 - fr) + b * fr


def _stutter_slots(slice_, repeats, accel, bpm, beats, at):
    L0 = _note_len(slice_, bpm, beats, at)
    slots = [L0] * int(repeats)
    if accel:
        if accel == 'default' or accel is True:
            accel = [('1/16', 2), ('1/32', 4), ('1/64', 8)]
        for item in accel:
            if isinstance(item, (list, tuple)):
                note, cnt = item[0], item[1]
            else:
                note, cnt = item, 1
            slots += [_note_len(note, bpm, beats, at)] * int(cnt)
    return slots


def audio_stutter(track, at, slice='1/16', repeats=8, sr=SR, accel=None, xfade_ms=2.0, pitch_step_st=0.0,
                  bpm=None, beats=None, src=None, end_at=None):
    """Beat repeat: the slice of the track starting at `at` (1/16 note = 125 ms at 120 BPM, or seconds) replaces
    the music `repeats` times, then the optional acceleration (accel='default' = 2x1/16 -> 4x1/32 -> 8x1/64); the
    track resumes at its own timeline position (grid kept). end_at: place the stutter so it releases exactly there.
    xfade_ms: crossfade at the joins (0 = dirty on purpose); pitch_step_st: +n semitones per repeat."""
    y = np.array(track, float, copy=True)
    src = y.copy() if src is None else np.asarray(src, float)
    slots = _stutter_slots(slice, repeats, accel, bpm, beats, at if end_at is None else end_at)
    if end_at is not None:
        at = end_at - sum(slots)
    s0 = at * sr
    bounds = np.round((at + np.concatenate([[0.0], np.cumsum(slots)])) * sr).astype(int)
    xf = float(xfade_ms) / 2
    for j in range(len(slots)):
        a, b = bounds[j], bounds[j + 1]
        if b <= 0 or a >= len(y):
            continue
        rate = 2.0 ** (j * float(pitch_step_st) / 12.0)
        seg = _interp(src, s0 + np.arange(b - a) * rate)
        seg = fade(seg, sr, xf, xf) if xf > 0 else seg
        lo, hi = max(a, 0), min(b, len(y))
        y[lo:hi] = seg[lo - a:hi - a]
    return y


def tape_stop(track, at, dur=0.6, sr=SR, curve=1.5, resume_at=None, start=False, src=None):
    """Tape stop: read speed r(u) = (1 - u)^curve over `dur` (pitch falls with it), level ~ r, LPF 18 kHz * r,
    then silence until resume_at (None = to the end). start=True: spin-up r = u^curve over `dur` that lands on
    the track's own timeline position at at + dur."""
    y = np.array(track, float, copy=True)
    src = y.copy() if src is None else np.asarray(src, float)
    i0, n = int(round(at * sr)), _n(dur, sr)
    u = np.arange(n) / n
    r = u ** curve if start else (1 - u) ** curve
    adv = np.cumsum(r) - r
    pos = (i0 + n - adv[-1] - r[-1] + adv) if start else (i0 + adv)
    seg = _interp(src, pos)
    seg = tv_filter(seg, 'lp', np.maximum(18000.0 * r, 40.0), 0.7071, sr, steady=True) * r[:, None]
    seg = hp(seg, 20, sr, 2)
    seg = fade(seg, sr, in_ms=3 if start else 0, out_ms=0 if start else 5)
    lo, hi = max(i0, 0), min(i0 + n, len(y))
    if hi > lo:
        y[lo:hi] = seg[lo - i0:hi - i0]
    if not start:
        j = len(y) if resume_at is None else int(round(resume_at * sr))
        if j > hi:
            y[hi:j] = 0.0
            k = min(len(y) - j, _n(0.001, sr))
            if k > 1:
                y[j:j + k] *= np.linspace(0, 1, k)[:, None]
    return y


def scratch_track(track, at, dur=0.35, sr=SR, rate_hz=4.5, amp=2.5, src=None):
    """Record scratch: the track from `at` is read at speed amp * sin(2 pi rate_hz t) (forward then back, the
    head swings ~2 * amp / (2 pi rate) s), band 200 Hz - 4 kHz; the music under it is replaced."""
    y = np.array(track, float, copy=True)
    src = y.copy() if src is None else np.asarray(src, float)
    i0, n = int(round(at * sr)), _n(dur, sr)
    t = np.arange(n) / sr
    pos = i0 + sr * amp / (TAU * rate_hz) * (1 - np.cos(TAU * rate_hz * t))
    lo_s, hi_s = max(0, i0 - 10), min(len(src), i0 + int(sr * 2 * amp / (TAU * rate_hz)) + sr // 10)
    band = np.zeros_like(src)
    band[lo_s:hi_s] = lp(src[lo_s:hi_s], 4000, sr, 4)           # anti-alias before the fast reads
    seg = lp(hp(_interp(band, pos), 200, sr, 2), 4000, sr, 2)
    seg = fade(seg, sr, 3, 3)
    lo, hi = max(i0, 0), min(i0 + n, len(y))
    if hi > lo:
        y[lo:hi] = seg[lo - i0:hi - i0]
    return y


def music_filter(track, kind='hp', f=(20, 400), t=(0.0, 1.0), sr=SR, q=1.0, ease='inQuad', reset_at=None):
    """Filter build on the track: 12 dB/oct HP (or LP) whose cutoff moves f[0] -> f[1] over t (log-frequency,
    eased), held until reset_at (default t[1]) and released there (5 ms crossfade back to the dry track).
    kind='lp', f=(300, 20000): the reverse "out from under water"."""
    y = np.array(track, float, copy=True)
    t0, t1 = float(t[0]), float(t[1])
    tr = t1 if reset_at is None else float(reset_at)
    i0, i1, ir = int(round(t0 * sr)), int(round(t1 * sr)), int(round(tr * sr))
    i0, ir = max(0, i0), min(len(y), ir)
    if ir - i0 < 16:
        return y
    u = np.clip((np.arange(i0, ir) - i0) / max(i1 - i0, 1), 0, 1)
    e = EASE.get(ease, EASE['linear'])(u)
    fc = float(f[0]) * (float(f[1]) / float(f[0])) ** e
    seg = tv_filter(y[i0:ir], kind, fc, q, sr, steady=True)
    k = min(_n(0.005, sr), (ir - i0) // 2)
    w = np.ones(ir - i0)
    w[:k] = np.linspace(0, 1, k)
    if ir < len(y) and reset_at is not None or ir < len(y):
        w[-k:] = np.minimum(w[-k:], np.linspace(1, 0, k))
    y[i0:ir] = y[i0:ir] * (1 - w[:, None]) + seg * w[:, None]
    return y


def music_crush(track, t, bits=8, sr_hz=11025, mix=0.8, sr=SR):
    """Bit-crush the track over t = [t0, t1] (6-10 bits, sample-and-hold to sr_hz, wet mix), 5 ms crossfades."""
    y = np.array(track, float, copy=True)
    i0, i1 = max(0, int(round(t[0] * sr))), min(len(y), int(round(t[1] * sr)))
    if i1 - i0 < 16:
        return y
    seg = y[i0:i1]
    wet = np.stack([crush(seg[:, c], int(bits), sr_hz, sr) for c in range(seg.shape[1])], 1)
    w = fade(np.ones(i1 - i0), sr, 5, 5) * float(mix)
    y[i0:i1] = seg * (1 - w[:, None]) + wet * w[:, None]
    return y


def music_gate(track, holes, depth_db=-40.0, attack_ms=1.0, release_ms=5.0, sr=SR):
    """Gate the track to depth_db inside holes [[t0, t1], ...] (attack 1 ms, release 5 ms)."""
    lane = _Lanes(len(track), sr)
    lane.add(None, lane.window_target(holes, -float(depth_db)), attack_ms, release_ms)
    return lane.apply(np.array(track, float, copy=True))


# ============================================================================ gain automation lanes
def _ar_smooth(x, att_ms, rel_ms, cr=CR):
    """Asymmetric one-pole smoothing at the control rate (attack when rising, release when falling)."""
    a = math.exp(-1.0 / (att_ms * cr / 1000.0)) if att_ms and att_ms > 0 else 0.0
    r = math.exp(-1.0 / (rel_ms * cr / 1000.0)) if rel_ms and rel_ms > 0 else 0.0
    out = np.empty_like(x)
    s = 0.0
    for i, v in enumerate(x):
        c = a if v > s else r
        s = c * s + (1 - c) * v
        out[i] = s
    return out


class _Lanes:
    """dB reduction curves at the control rate, one per band (None = full band), max-combined; applied to a track
    as gain (full band) or as a zero-phase band split: out = x - (1 - g) * band(x)."""

    def __init__(self, n_samples, sr):
        self.sr = sr
        self.N = n_samples
        self.n = int(math.ceil(n_samples / sr * CR)) + 2
        self.lanes = {}

    def window_target(self, wins, red):
        tgt = np.zeros(self.n)
        for w in wins:
            a, b = int(round(w[0] * CR)), int(round(w[1] * CR))
            v = red if len(w) < 3 or w[2] is None else -float(w[2])
            tgt[max(a, 0):max(min(b, self.n), 0)] = np.maximum(tgt[max(a, 0):max(min(b, self.n), 0)], v)
        return tgt

    def add(self, band, target, att_ms=0.0, rel_ms=0.0, span=None):
        """target: dB reduction (>= 0) at the control rate; smoothed with attack / release; span = (i0, i1) control
        indices limits the (slow) smoothing loop to where the target lives."""
        if span is None:
            nz = np.nonzero(target > 0)[0]
            if not len(nz):
                return
            span = (nz[0], nz[-1] + 1)
        i0 = max(0, int(span[0]) - 2)
        i1 = min(self.n, int(span[1]) + int(5 * (rel_ms or 0)) + 10)
        sm = np.zeros(self.n)
        sm[i0:i1] = _ar_smooth(target[i0:i1], att_ms, rel_ms)
        key = None if band is None else (float(band[0]), float(band[1]))
        if key is not None:                            # overlapping bands share one lane (max, not sum):
            for k in self.lanes:                       # impact 30-150 Hz + sub drop 25-150 Hz -> one low lane
                if k is not None:
                    lo, hi = max(k[0], key[0]), min(k[1], key[1])
                    narrow = min(math.log(k[1] / k[0]), math.log(key[1] / key[0]))
                    if hi > lo and math.log(hi / lo) >= 0.5 * narrow:
                        key = k
                        break
        cur = self.lanes.get(key)
        self.lanes[key] = sm if cur is None else np.maximum(cur, sm)

    def apply(self, x):
        """Apply every lane to x (only over the span where the lane is active, + 0.5 s filter context)."""
        if not self.lanes:
            return x
        x = np.array(x, float, copy=True)
        for key, red in self.lanes.items():
            act = np.nonzero(red > 1e-4)[0]
            if not len(act):
                continue
            a = max(0, int((act[0] - 1) / CR * self.sr))
            b = min(len(x), int((act[-1] + 2) / CR * self.sr))
            if b <= a:
                continue
            g = db(-np.interp(np.arange(a, b) / self.sr * CR, np.arange(self.n), red))
            if key is None:
                x[a:b] *= g[:, None]
                continue
            lo, hi = key
            pa, pb = max(0, a - self.sr // 2), min(len(x), b + self.sr // 2)
            seg = x[pa:pb]
            if lo <= 20:
                comp = filt(seg, 'lp', hi, self.sr, 2, zero_phase=True)
            elif hi >= 0.45 * self.sr:
                comp = filt(seg, 'hp', lo, self.sr, 2, zero_phase=True)
            else:
                comp = filt(seg, 'bp', (lo, hi), self.sr, 2, zero_phase=True)
            x[a:b] -= comp[a - pa:b - pa] * (1 - g)[:, None]
        return x


# ============================================================================ I/O + measurement
def _load(path, sr, start=0.0, dur=None, speed=1.0):
    """Decode any audio/video file to float (M, 2) at sr via ffmpeg (from `start` s, `dur` s of the output)."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    cmd = ['ffmpeg', '-v', 'error', '-nostdin']
    if start and start > 0:
        cmd += ['-ss', f'{start:.4f}']
    cmd += ['-i', path]
    af = []
    if speed and abs(speed - 1.0) > 1e-6:
        af = [f'asetrate={sr * speed:.3f}', f'aresample={sr}']
    if dur:
        cmd += ['-t', f'{dur * (speed or 1.0):.4f}']
    cmd += ['-vn', '-ac', '2', '-ar', str(sr)] + (['-af', ','.join(af)] if af else []) + ['-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    y = np.frombuffer(raw, np.float32).astype(np.float64)
    return y.reshape(-1, 2)


def _write_wav(path, y, sr, codec='pcm_s24le'):
    y = np.ascontiguousarray(_st(y), dtype=np.float32)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', 'pipe:0',
                    '-c:a', codec, path], input=y.tobytes(), check=True)


def _parse_ebur(txt):
    I = re.findall(r'I:\s+(-?[\d.]+|-inf|nan) LUFS', txt)
    P = re.findall(r'Peak:\s+(-?[\d.]+|-inf|nan) dBFS', txt)
    f = lambda v: float(v) if v not in ('-inf', 'nan') else -np.inf
    return (f(I[-1]) if I else -np.inf), (f(P[-1]) if P else -np.inf)


def measure(y_or_path, sr=SR):
    """ffmpeg ebur128 (true peak) -> (integrated LUFS, true peak dBTP) of an array or a file."""
    if isinstance(y_or_path, str):
        cmd = ['ffmpeg', '-hide_banner', '-nostats', '-i', y_or_path]
        inp = None
    else:
        cmd = ['ffmpeg', '-hide_banner', '-nostats', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', 'pipe:0']
        inp = np.ascontiguousarray(_st(y_or_path), dtype=np.float32).tobytes()
    cmd += ['-af', 'ebur128=peak=true:framelog=quiet', '-f', 'null', '-']
    r = subprocess.run(cmd, input=inp, capture_output=True)
    return _parse_ebur(r.stderr.decode('utf-8', 'replace'))


def _release(H, tau):
    """R[n] = max(H[n], R[n-1] * exp(-1 / tau)) vectorised in the log domain (exponential release of dB GR)."""
    n = len(H)
    k = np.arange(n, dtype=np.float64)
    gam = 1.0 / max(tau, 1.0)
    with np.errstate(divide='ignore'):
        lh = np.where(H > 0, np.log(np.maximum(H, 1e-300)), -np.inf) + k * gam
    lc = np.maximum.accumulate(lh)
    with np.errstate(invalid='ignore', over='ignore'):
        R = np.where(np.isfinite(lc), np.exp(lc - k * gam), 0.0)
    return np.maximum(R, H)


def _tp_block(yt, os_):
    n = yt.shape[1]
    up = ss.resample_poly(yt, os_, 1, axis=1)
    a = np.maximum(np.abs(up[0]), np.abs(up[1]))[:n * os_].reshape(n, os_)
    pk = np.maximum(np.abs(yt[0]), np.abs(yt[1]))
    for k in range(os_):
        pk = np.maximum(pk, a[:, k])
    return pk


def tp_envelope(y, os_=4, floor=None):
    """Per-sample true-peak envelope: max |x| of the 4x-oversampled signal (both channels) around each sample.
    floor (linear): only regions whose sample peak exceeds it are oversampled (with 64 samples of context);
    elsewhere the sample peak is used (inter-sample overs of real audio stay far below the 6 dB margin callers use)."""
    yt = np.ascontiguousarray(_st(y).T)
    n = yt.shape[1]
    if floor is None or n < 4096:
        return _tp_block(yt, os_)
    sp = np.maximum(np.abs(yt[0]), np.abs(yt[1]))
    cand = maximum_filter1d((sp > floor).astype(np.uint8), 129) > 0
    if not cand.any():
        return sp
    pk = sp.copy()
    edges = np.diff(np.concatenate([[0], cand.astype(np.int8), [0]]))
    starts, ends = np.nonzero(edges == 1)[0], np.nonzero(edges == -1)[0]
    # merge runs closer than 2048 samples to keep the number of resampling calls small
    runs = []
    for a, b in zip(starts, ends):
        if runs and a - runs[-1][1] < 2048:
            runs[-1][1] = b
        else:
            runs.append([a, b])
    for a, b in runs:
        a0, b0 = max(0, a - 64), min(n, b + 64)
        pk[a:b] = _tp_block(yt[:, a0:b0], os_)[a - a0:b - a0]
    return pk


def tp_limit(y, sr=SR, ceil_db=-1.2, look_ms=2.5, rel_ms=80.0, os_=4, fast_ms=None):
    """Look-ahead true-peak limiter: 4x-oversampled peak envelope -> needed gain reduction (dB) -> max over
    +-look -> exponential release -> moving average over +-look (gain is down before every peak) -> applied.
    fast_ms: hit-length overs (clicks, hits: runs <= fast_ms after merging overs closer than 30 ms) get a 1 ms
    look-ahead and a 6 ms release instead (the gain follows the hit instead of leaving a hole after it); sustained
    overs keep the slow release (no distortion on held bass / pads). The gain reduction stays a gain:
    y_limited = y x db(-gr) exactly.
    Returns (y_limited, gain_reduction_db per sample)."""
    yl, S, _ = tp_limit2(y, sr, ceil_db, look_ms, rel_ms, os_, fast_ms)
    return yl, S


def _gr_env(gr, L, rel):
    H = maximum_filter1d(gr, size=2 * L + 1, mode='nearest')
    R = _release(H, rel)
    return np.maximum(uniform_filter1d(R, size=2 * L + 1, mode='nearest'), 0.0)


def tp_limit2(y, sr=SR, ceil_db=-1.2, look_ms=2.5, rel_ms=80.0, os_=4, fast_ms=None):
    """tp_limit() -> (y_limited, gr_db, gr_slow_db): gr_slow_db = the part done with the slow release (sustained
    limiting, what squashes music); gr_db = the total applied."""
    y = _st(y)
    n = len(y)
    c = 10 ** (ceil_db / 20.0)
    pk = tp_envelope(y, os_, floor=c * 0.5)
    with np.errstate(divide='ignore'):
        gr = np.maximum(0.0, 20 * np.log10(np.maximum(pk, 1e-12) / c))
    if not np.any(gr > 0):
        z = np.zeros(n)
        return y, z, z
    L = max(1, int(look_ms * sr / 1000.0))
    if not fast_ms:
        S = _gr_env(gr, L, rel_ms * sr / 1000.0)
        return y * db(-S)[:, None], S, S
    over = gr > 0
    merged = maximum_filter1d(over.astype(np.uint8), size=max(1, int(0.03 * sr)) | 1) > 0
    short = np.zeros(n, bool)
    lim = int(float(fast_ms) * sr / 1000.0)
    for a, b in _runs(merged):
        if b - a <= lim:
            short[a:b] = True
    g_fast, g_slow = np.where(short, gr, 0.0), np.where(short, 0.0, gr)
    Ss = _gr_env(g_slow, L, rel_ms * sr / 1000.0) if np.any(g_slow > 0) else np.zeros(n)
    Sf = _gr_env(g_fast, max(1, int(0.001 * sr)), 0.006 * sr) if np.any(g_fast > 0) else np.zeros(n)
    S = np.maximum(Ss, Sf)
    return y * db(-S)[:, None], S, Ss


FAST_MS = 150.0        # master limiter: hit-length overs (<= 150 ms after merging within 30 ms) get the fast release
FAST_EXTRA_DB = 6.0    # ... and may be pulled down max_gr + 6 dB (shaped hits); sustained limiting stays <= max_gr


def master(pre, sr=SR, lufs=-14.0, tp=-1.0, max_iter=6, tol=0.1, gain0=None, ceil0=None, max_gr=8.0,
           max_gain=20.0):
    """Static gain + true-peak limiter, iterated on ffmpeg ebur128 measurements (like ed_render.render_audio):
    gain += target - measured until |I - target| <= tol and TP <= tp (the limiter ceiling drops if TP misses).
    The start gain comes from the numpy BS.1770 meter, which already accounts for the limiter's loudness loss.
    A program too dynamic for the target (sustained limiting above max_gr dB, or hit-length overs above max_gr +
    FAST_EXTRA_DB) or too sparse (gain above max_gain) stays quieter instead of being squashed: 'capped' says why.
    -> (y, dict(lufs, tp, gain_db, gr (per-sample dB), slow_max_db (the sustained part), ceil_db, iters, capped))."""
    ceil = tp - 0.3 if ceil0 is None else ceil0
    capped, slow_max = None, 0.0

    def clamp(g):
        nonlocal capped
        if g > max_gain:
            capped = capped or 'gain'
            return max_gain
        return g

    def limit(g):
        """Limit at gain g (isolated transients with a fast release, see tp_limit), backing the gain off while the
        sustained (slow-release) limiting would pull more than max_gr dB or a hit more than max_gr + FAST_EXTRA_DB."""
        nonlocal capped, slow_max
        y, gr, slow = tp_limit2(pre * db(g), sr, ceil, fast_ms=FAST_MS)
        for _ in range(4):
            over = max(float(np.max(slow)) - max_gr, float(np.max(gr)) - max_gr - FAST_EXTRA_DB) if len(gr) else 0.0
            if over <= 0.1:
                break
            g -= over
            capped = 'gr'
            y, gr, slow = tp_limit2(pre * db(g), sr, ceil, fast_ms=FAST_MS)
        slow_max = float(np.max(slow)) if len(slow) else 0.0
        return y, gr, g

    if gain0 is None:
        I0 = lufs_integrated(pre, sr)
        if not np.isfinite(I0):
            return pre, dict(lufs=-np.inf, tp=-np.inf, gain_db=0.0, gr=np.zeros(len(pre)), slow_max_db=0.0,
                             ceil_db=ceil, iters=0, capped=None)
        gain0 = clamp(lufs - I0)
        for _ in range(3):                             # cheap pre-iteration: the limiter costs loudness
            yl, _, gain0 = limit(gain0)
            miss = lufs - lufs_integrated(yl, sr)
            if abs(miss) < 0.05 or (capped and miss > 0):
                break
            gain0 = clamp(gain0 + miss)
    gain = gain0
    best = None
    for it in range(max_iter):
        y, gr, gain = limit(gain)
        I, TP = measure(y, sr)
        if not np.isfinite(I) or I <= -69.9:           # below the gate (too short / silent): keep the estimate
            return y, dict(lufs=I, tp=TP, gain_db=gain, gr=gr, slow_max_db=slow_max, ceil_db=ceil, iters=it + 1,
                           capped=capped)
        score = abs(I - lufs) + 10 * max(0.0, TP - tp)
        if best is None or score < best[0]:
            best = (score, y, dict(lufs=I, tp=TP, gain_db=gain, gr=gr, slow_max_db=slow_max, ceil_db=ceil,
                                   iters=it + 1, capped=capped))
        if abs(I - lufs) <= tol and TP <= tp - 0.05:
            break
        if capped and I < lufs and TP <= tp - 0.05:     # cannot get louder without squashing
            break
        if TP > tp - 0.05:
            ceil -= TP - (tp - 0.15)
        gain = clamp(gain + lufs - I)
    return best[1], best[2]


# ============================================================================ delivery encode
_CODECS = {'aac': ('aac', '.m4a'), 'mp3': ('libmp3lame', '.mp3'), 'libmp3lame': ('libmp3lame', '.mp3'),
           'opus': ('libopus', '.opus'), 'libopus': ('libopus', '.opus'), 'flac': ('flac', '.flac'),
           'pcm': ('pcm_s24le', '.wav'), 'wav': ('pcm_s24le', '.wav')}


def _encode_file(y, sr, out, codec, bitrate):
    lib = _CODECS.get(codec, (codec, None))[0]
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', 'pipe:0', '-c:a', lib]
    if bitrate and lib not in ('flac', 'pcm_s24le', 'pcm_s16le'):
        cmd += ['-b:a', str(bitrate)]
    if lib == 'aac':
        cmd += ['-movflags', '+faststart'] if out.lower().endswith(('.m4a', '.mp4', '.mov')) else []
    cmd += ['-ar', str(sr), out]
    subprocess.run(cmd, input=np.ascontiguousarray(_st(y), dtype=np.float32).tobytes(), check=True,
                   capture_output=True)


def _codec_lowpass(codec, bitrate):
    """Band limit before a lossy encode (Hz, None = keep): content the codec would quantise coarsely anyway (the top
    octave of noise bursts, cymbals) is what overshoots after AAC; an 18.5 kHz zero-phase low-pass at 320k keeps the
    encoded true peak within ~0.2 dB of the PCM's (measured: up to +2 dB without it on transient-rich mixes)."""
    lib = _CODECS.get(codec, (codec,))[0]
    if lib in ('flac', 'pcm_s24le', 'pcm_s16le'):
        return None
    try:
        kbps = float(str(bitrate).lower().rstrip('k'))
    except ValueError:
        kbps = 320.0
    if lib == 'libopus':
        return 19000.0
    return 18500.0 if kbps >= 256 else (17000.0 if kbps >= 160 else 15500.0)


def encode_audio(wav, out, codec='aac', bitrate='320k', tp_max=-1.0, lufs=None, lufs_tol=0.5, sr=48000,
                 max_iter=5):
    """Encode a mixed WAV for delivery (the file ed_edl muxes into the MP4) so that the DECODED result still meets
    the targets. Lossy coding overshoots inter-sample peaks (AAC +0.3-2 dB on transient-rich mixes): the PCM is
    band-limited to what the codec keeps (_codec_lowpass, zero-phase) and re-limited with a lower ceiling (true-peak
    limiter, hits with the fast release) until the encoded file measures true peak <= tp_max, with a make-up gain
    so its integrated loudness stays within lufs_tol of `lufs` (default: the WAV's own loudness, i.e. kept). Both
    are measured by ffmpeg ebur128 on the encoded file. codec: 'aac' (default, .m4a), 'mp3', 'opus', 'flac' / 'pcm'
    (lossless: one pass, no band limit).
    -> {"path", "codec", "bitrate", "lufs", "tp", "lufs_in", "tp_in", "ceil_db", "gain_db", "lowpass_hz", "iters",
        "ok", "target_lufs", "tp_max"}"""
    sr = int(sr)
    y = _load(wav, sr)
    I_in, TP_in = measure(wav)
    target = float(lufs) if lufs is not None else I_in
    fl = _codec_lowpass(codec, bitrate)
    if fl and fl < 0.48 * sr:
        y = ss.sosfiltfilt(ss.butter(8, fl / (sr / 2.0), output='sos'), y, axis=0)
    if not np.isfinite(target):
        _encode_file(y, sr, out, codec, bitrate)
        I, TP = measure(out)
        return dict(path=out, codec=codec, bitrate=bitrate, lufs=I, tp=TP, lufs_in=I_in, tp_in=TP_in, ceil_db=None,
                    gain_db=0.0, lowpass_hz=fl, iters=1, ok=bool(not np.isfinite(TP) or TP <= tp_max))
    I_lp = lufs_integrated(y, sr)
    gain = (target - I_lp) if np.isfinite(I_lp) else 0.0             # the band limit may cost a little loudness
    tp_lp = true_peak_db(y, sr)
    ceil = min(tp_max - 0.3, tp_lp + gain if np.isfinite(tp_lp) else tp_max - 0.3)
    lossless = fl is None
    best = None
    tmp = out + '.part' + os.path.splitext(out)[1]
    for it in range(1 if lossless else int(max_iter)):
        x = y * db(gain)
        if true_peak_db(x, sr) > ceil:
            x, _ = tp_limit(x, sr, ceil, fast_ms=FAST_MS)
        _encode_file(x, sr, tmp, codec, bitrate)
        I, TP = measure(tmp)
        ok = (TP <= tp_max + 1e-6) and abs(I - target) <= lufs_tol
        score = max(0.0, TP - tp_max) * 10 + abs(I - target)
        if best is None or score < best[0]:
            best = (score, dict(lufs=I, tp=TP, ceil_db=round(ceil, 2), gain_db=round(gain, 2), iters=it + 1, ok=ok))
            os.replace(tmp, out)
        if ok and abs(I - target) <= 0.2:
            break
        if TP > tp_max - 0.05:
            ceil -= (TP - tp_max) + 0.15
        if abs(I - target) > 0.1:
            gain += target - I
    if os.path.exists(tmp):
        os.remove(tmp)
    r = best[1]
    return dict(path=out, codec=codec, bitrate=bitrate, lufs=round(r['lufs'], 2), tp=round(r['tp'], 2),
                lufs_in=round(I_in, 2), tp_in=round(TP_in, 2), ceil_db=r['ceil_db'], gain_db=r['gain_db'],
                lowpass_hz=fl, iters=r['iters'], ok=bool(r['ok']), target_lufs=round(target, 2), tp_max=tp_max)


# ============================================================================ mixer
class _Ctx:
    def __init__(self, audio, sr, N, bed0, has_music, warn):
        self.audio, self.sr, self.N, self.bed0, self.has_music, self.warn = audio, sr, N, bed0, has_music, warn
        self._key = self._grid = None
        self._key_done = self._grid_done = False

    def key(self):
        if not self._key_done:
            self._key_done = True
            k = self.audio.get('key')
            if k:
                k = {'root': k} if not isinstance(k, dict) else dict(k)
                k.setdefault('conf', 1.0)
                k['pc'] = _pc(k.get('root'))
                k['mode'] = _mode(k.get('root'), k.get('mode'))
                self._key = k if k['pc'] is not None else None
            elif self.has_music:
                try:
                    self._key = key_root(self.bed0, self.sr)
                except Exception as e:                  # analysis must never break the render
                    self.warn.append(f'key detection failed: {e}')
        return self._key

    def confident_key(self):
        k = self.key()
        return k if (k and float(k.get('conf', 0)) >= 0.6) else None

    def grid(self):
        if not self._grid_done:
            self._grid_done = True
            g = self.audio.get('grid')
            if g:
                self._grid = dict(g)
            elif self.has_music:
                try:
                    self._grid = music_grid(self.bed0, self.sr)
                except Exception as e:
                    self.warn.append(f'beat analysis failed: {e}')
        return self._grid

    def bpm(self):
        g = self.grid()
        return float(g['bpm']) if g and g.get('bpm') else 120.0

    def next_downbeat(self, t):
        g = self.grid() or {}
        d = [x for x in (g.get('downbeats') or []) if x > t + 1e-3]
        if d:
            return float(d[0])
        bar = 4 * 60.0 / self.bpm()
        return t + bar - (t % bar) if g.get('bpm') else None


def _music_bed(m, N, sr, T_I, warn):
    """Music placed on the timeline: in-point, at, dur, speed, loudness-normalised to T_I + gain_db, fades."""
    if not m or not m.get('path'):
        return None, None
    at, t_in = float(m.get('at', 0.0)), float(m.get('in', 0.0))
    speed = float(m.get('speed', 1.0) or 1.0)
    a = int(round(at * sr))
    need = N - a
    if m.get('dur'):
        need = min(need, _n(float(m['dur']), sr))
    if need <= 0:
        return None, None
    y = _load(m['path'], sr, start=t_in, dur=need / sr + 0.05, speed=speed)[:need]
    if len(y) < need:
        warn.append(f"music shorter than the timeline by {(need - len(y)) / sr:.2f} s")
    I = lufs_integrated(y, sr) if len(y) else -np.inf
    g = (T_I - I if np.isfinite(I) else 0.0) + float(m.get('gain_db', 0.0))
    y = y * db(g)
    bed = np.zeros((N, 2))
    bed[a:a + len(y)] = y
    end = a + len(y)
    fi, fo = float(m.get('fade_in', 0.0) or 0), float(m.get('fade_out', 0.0) or 0)
    if fi > 0:
        bed[a:end] = fade(bed[a:end], sr, in_ms=fi * 1000)
    if fo > 0:
        bed[a:end] = fade(bed[a:end], sr, out_ms=fo * 1000)
    return bed, dict(I_raw=I, gain_db=g, at=at, t_in=t_in, len_s=len(y) / sr)


def _voices(vs, N, sr, T_I, warn, fade_ms=6.0):
    """Voice clips on the timeline, high-passed at 80 Hz. Loudness: clips of one file share one gain (the source's
    own balance between speakers and phrases is kept), computed over all of them to reach their lufs (default
    loudness.lufs); "norm": "clip" on a clip normalises it alone; gain_db trims. Clip edges get fade_ms raised-cosine
    fades (no clicks at the cuts) except where the next clip continues the same file seamlessly."""
    bus = np.zeros((N, 2))
    items = []
    for v in vs or []:
        if not v or not v.get('path'):
            continue
        at = float(v.get('at', 0.0))
        a = int(round(at * sr))
        if a >= N:
            continue
        dur = float(v['dur']) if v.get('dur') else (N - a) / sr
        y = _load(v['path'], sr, start=float(v.get('in', 0.0)), dur=dur)[:N - max(a, 0)]
        if len(y):
            items.append(dict(v=v, a=a, y=y))

    def seamless(p, q):
        if p['v']['path'] != q['v']['path']:
            return False
        dp = len(p['y']) / sr
        return (abs((q['a'] - p['a']) / sr - dp) < 0.002 and
                abs(float(q['v'].get('in', 0.0)) - float(p['v'].get('in', 0.0)) - dp) < 0.002)

    items.sort(key=lambda it: it['a'])
    groups = {}
    for it in items:
        key = ('clip', id(it)) if str(it['v'].get('norm', 'source')) == 'clip' else ('src', it['v']['path'],
                                                                                    it['v'].get('lufs'))
        groups.setdefault(key, []).append(it)
    for key, its in groups.items():
        I = lufs_integrated(np.concatenate([it['y'] for it in its]), sr)
        tgt = float(its[0]['v'].get('lufs') or T_I)
        for it in its:
            it['g'] = (tgt - I if np.isfinite(I) else 0.0) + float(it['v'].get('gain_db', 0.0))
    for j, it in enumerate(items):
        fi = 0.0 if (j > 0 and seamless(items[j - 1], it)) else fade_ms
        fo = 0.0 if (j + 1 < len(items) and seamless(it, items[j + 1])) else fade_ms
        y = fade(it['y'] * db(it['g']), sr, in_ms=fi, out_ms=fo)
        a = it['a']
        lo = max(a, 0)
        bus[lo:lo + len(y) - (lo - a)] += y[lo - a:]
    return hp(bus, 80, sr, 2) if items else bus      # one filter over the bus: seamless joins stay seamless


def _voice_regions(vs, N, sr):
    """Union of the voice clips' [at, at + dur] spans in seconds (merged when closer than 50 ms)."""
    iv = []
    for v in vs or []:
        if not v or not v.get('path'):
            continue
        a = float(v.get('at', 0.0))
        b = a + float(v['dur']) if v.get('dur') else N / sr
        iv.append((a, min(b, N / sr)))
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1] + 0.05:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def _voice_activity(bus, sr):
    """Voice activity at the control rate (0/1): 20 ms RMS above max(peak - 35 dB, -60 dBFS)."""
    m = np.mean(bus, axis=1)
    hop = int(sr / CR)
    n = int(math.ceil(len(m) / sr * CR)) + 2
    r = np.sqrt(np.maximum(uniform_filter1d(m * m, int(0.02 * sr), mode='constant'), 0.0))[::hop]
    with np.errstate(divide='ignore'):
        L = 20 * np.log10(np.maximum(r, 1e-9))
    if not len(L) or L.max() < -70:
        return np.zeros(n)
    act = (L > max(L.max() - 35, -60)).astype(float)
    return _fit(act, n)


def _runs(mask):
    """[(i0, i1), ...] of the True runs of a boolean array (i1 exclusive)."""
    d = np.diff(np.concatenate([[0], mask.astype(np.int8), [0]]))
    return list(zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]))


def _rc(k):
    """Raised-cosine ramp 0 -> 1 over k control steps."""
    return 0.5 - 0.5 * np.cos(np.pi * np.arange(k) / max(k, 1))


def voice_duck_curve(vact, depth_db=8.0, attack_ms=120.0, hold_ms=200.0, release_ms=500.0, gap_ms=700.0,
                     min_ms=60.0, regions=None):
    """Smooth ducking under speech (dB reduction per control step, CR = 1 kHz): pauses shorter than gap_ms are
    bridged and blips shorter than min_ms ignored, so the music stays down through a phrase instead of pumping
    between words; the duck starts attack_ms BEFORE the first word (offline look-ahead), holds hold_ms after the
    last one and comes back over release_ms, raised-cosine ramps in dB. regions = [[t0, t1], ...] voice clip spans:
    a duck never outlives the clip span it is in (release squeezed into its end + 30 ms) - the music hits at full
    level right where a talk part ends (talk -> drop)."""
    act = np.asarray(vact) > 0.5
    n = len(act)
    gap, mn = int(gap_ms * CR / 1000), int(min_ms * CR / 1000)
    runs = [(a, b) for a, b in _runs(act) if b - a >= mn]
    merged = []
    for a, b in runs:
        if merged and a - merged[-1][1] <= gap:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    out = np.zeros(n)
    ka, kh, kr = max(1, int(attack_ms * CR / 1000)), int(hold_ms * CR / 1000), max(1, int(release_ms * CR / 1000))
    ends = [(int(r0 * CR), int(r1 * CR)) for r0, r1 in (regions or [])]
    for a, b in merged:
        seg = np.zeros(n)
        lo = max(0, a - ka)
        seg[lo:a] = _rc(ka)[ka - (a - lo):] * depth_db
        lim = next((r1 for r0, r1 in ends if r0 - 50 <= b <= r1 + 50), None)
        e, kr2 = min(n, b + kh), kr
        if lim is not None and e + kr > lim + 30:
            e = max(b, min(e, lim - 30))
            kr2 = max(1, lim + 30 - e)
        seg[a:e] = depth_db
        r1 = min(n, e + kr2)
        seg[e:r1] = (1 - _rc(kr2))[:r1 - e] * depth_db
        out = np.maximum(out, seg)
    return out


class _Level:
    """Absolute music level automation in dB at the control rate: gain holds / ramps (min-combined), 'level'
    breakpoints and swells (override their span), fades (on top). Applied as one gain curve."""

    def __init__(self, n_samples, sr):
        self.sr, self.N = sr, n_samples
        self.n = int(math.ceil(n_samples / sr * CR)) + 2
        self.base = np.zeros(self.n)
        self.over = []                                   # (i0, i1, curve) overrides, in order
        self.fades = np.zeros(self.n)
        self.used = False

    def _i(self, t):
        return int(np.clip(round(float(t) * CR), 0, self.n))

    def hold(self, t, level_db, attack_ms=10.0, release_ms=10.0):
        """level_db over t = [t0, t1]: ramps down over attack_ms from t0, back up over release_ms from t1."""
        v = float(level_db)
        if not v or not t:
            return
        a, b = self._i(t[0]), self._i(t[1])
        ka, kr = max(1, int(float(attack_ms or 0) * CR / 1000)), max(1, int(float(release_ms or 0) * CR / 1000))
        c = np.zeros(self.n)
        c[a:b] = v
        c[a:min(b, a + ka)] = v * _rc(ka)[:min(b, a + ka) - a]
        c[b:min(self.n, b + kr)] = v * (1 - _rc(kr))[:min(self.n, b + kr) - b]
        self.base = np.minimum(self.base, c) if v < 0 else np.maximum(self.base, c)
        self.used = True

    def ramp(self, t, level_db, until=None):
        """Old 'ramp' curve: linear dB from 0 at t0 to level_db at t1, held to `until` (default: the end)."""
        a, b = self._i(t[0]), self._i(t[1])
        c = np.zeros(self.n)
        if b > a:
            c[a:b] = np.linspace(0.0, float(level_db), b - a)
        c[b:self._i(until) if until is not None else self.n] = float(level_db)
        self.base = np.minimum(self.base, c) if float(level_db) < 0 else np.maximum(self.base, c)
        self.used = True

    def points(self, pts, ease='linear'):
        """Breakpoints [[t, dB], ...] override the level inside their span; ease shapes each segment."""
        pts = sorted((float(p[0]), float(p[1])) for p in pts)
        if not pts:
            return
        if len(pts) == 1:
            pts = [pts[0], (pts[0][0] + 1.0 / CR, pts[0][1])]
        i0, i1 = self._i(pts[0][0]), self._i(pts[-1][0])
        cur = np.zeros(max(1, i1 - i0 + 1))
        f = EASE.get(ease, EASE['linear']) if ease != 'smooth' else (lambda u: 0.5 - 0.5 * np.cos(np.pi * u))
        for (ta, va), (tb, vb) in zip(pts[:-1], pts[1:]):
            a, b = self._i(ta) - i0, self._i(tb) - i0
            if b <= a:
                continue
            u = np.arange(b - a + 1) / max(b - a, 1)
            cur[a:b + 1] = va + (vb - va) * f(u)
        self.over.append((i0, i0 + len(cur), cur))
        self.used = True

    def swell(self, at, dur=1.5, from_db=None, to_db=0.0, ease='inQuad'):
        """Rise into `at` over dur: from from_db (None = the level there before the swell) to to_db."""
        a, b = self._i(float(at) - float(dur)), self._i(at)
        if b <= a:
            return
        start = self.value(a) if from_db is None else float(from_db)
        u = np.arange(b - a + 1) / max(b - a, 1)
        self.over.append((a, b + 1, start + (float(to_db) - start) * EASE.get(ease, EASE['inQuad'])(u)))
        self.used = True

    def fade(self, at, dur, out=True, curve='cos', until=None, start=None):
        """Fade out from `at` over dur to silence (held to `until`, default the end), or fade in over [at, at + dur]
        from silence (from `start`, default 0)."""
        a, b = self._i(at), self._i(float(at) + float(dur))
        k = max(1, b - a)
        u = np.arange(k) / k
        amp = {'lin': u, 'exp': u ** 3, 'cos': 0.5 - 0.5 * np.cos(np.pi * u)}.get(curve, 0.5 - 0.5 * np.cos(np.pi * u))
        g = 20 * np.log10(np.maximum(amp[::-1] if out else amp, 1e-6))
        if out:
            self.fades[a:a + k] = np.minimum(self.fades[a:a + k], g[:max(0, min(k, self.n - a))])
            self.fades[a + k:self._i(until) if until is not None else self.n] = -120.0
        else:
            s0 = self._i(start or 0.0)
            self.fades[s0:a] = -120.0
            self.fades[a:a + k] = np.minimum(self.fades[a:a + k], g[:max(0, min(k, self.n - a))])
        self.used = True

    def value(self, i):
        c = self.curve()
        return float(c[int(np.clip(i, 0, self.n - 1))])

    def curve(self):
        c = self.base.copy()
        for a, b, cur in self.over:
            b = min(b, self.n)
            if b > a:
                c[a:b] = cur[:b - a]
        return c + self.fades

    def apply(self, x):
        if not self.used:
            return x
        c = self.curve()
        g = db(np.interp(np.arange(len(x)) / self.sr * CR, np.arange(self.n), c))
        return x * g[:, None]


# ---------------------------------------------------------------- user samples
_AUDIO_EXT = ('.wav', '.mp3', '.aif', '.aiff', '.flac', '.ogg', '.oga', '.m4a', '.aac', '.opus', '.wma', '.caf')


@functools.lru_cache(maxsize=48)
def _decoded(path, mtime, sr):
    y = _load(path, sr)
    y.setflags(write=False)
    return y


def _atempo(y, tempo, sr):
    """Time-stretch by ffmpeg atempo (tempo > 1 = shorter, pitch kept); chained for factors outside 0.5-2."""
    chain, t = [], float(tempo)
    while t > 2.0:
        chain.append('atempo=2.0')
        t /= 2.0
    while t < 0.5:
        chain.append('atempo=0.5')
        t /= 0.5
    chain.append(f'atempo={t:.6f}')
    r = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', 'pipe:0',
                        '-af', ','.join(chain), '-f', 'f32le', '-'],
                       input=np.ascontiguousarray(y, dtype=np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).astype(np.float64).reshape(-1, 2)


def load_sample(path, sr=SR, trim_db=-50.0, pitch=0.0, rate=1.0, stretch=1.0, reverse=False, dur=None,
                fade_ms=30.0):
    """A user's sound file as an SFX buffer -> (float (N, 2), meta). Any format ffmpeg reads (wav / mp3 / aiff /
    flac / ...; mono -> stereo). Leading and trailing silence trimmed (below trim_db dBFS or 45 dB under the peak;
    1 ms kept before the first sound, 10 ms after the last). pitch: semitones, sampler-style (speed and pitch
    together, like rate = 2^(st/12)); rate: speed factor; stretch: duration factor with the pitch kept (ffmpeg
    atempo); reverse: played backwards (its end becomes the cut); dur: cut to dur s with a fade_ms fade-out.
    meta: attack (first sample above -20 dB of the peak), peak (10 ms RMS maximum), end, n, trim_s."""
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    y = np.array(_decoded(os.path.abspath(path), os.path.getmtime(path), int(sr)), float)
    if not len(y):
        raise ValueError(f'{path}: no audio')
    a = np.max(np.abs(y), axis=1)
    pk = float(a.max())
    if pk <= 0:
        raise ValueError(f'{path}: silent')
    thr = max(10 ** (float(trim_db) / 20.0), pk * 10 ** (-45 / 20.0))
    nz = np.nonzero(a > thr)[0]
    i0 = max(0, int(nz[0]) - _n(0.001, sr))
    i1 = min(len(y), int(nz[-1]) + _n(0.010, sr))
    trim = i0 / sr
    y = y[i0:i1]
    r = float(rate or 1.0) * 2 ** (float(pitch or 0.0) / 12.0)
    if abs(r - 1.0) > 1e-4:
        from fractions import Fraction
        fr = Fraction(r).limit_denominator(400)
        y = ss.resample_poly(y, fr.denominator, fr.numerator, axis=0)
    if stretch and abs(float(stretch) - 1.0) > 1e-3:
        y = _atempo(y, 1.0 / float(stretch), sr)
    if reverse:
        y = reverse_(y)
    if dur and len(y) > _n(dur, sr):
        y = fade(y[:_n(dur, sr)], sr, out_ms=fade_ms)
    y = fade(y, sr, in_ms=0.5 if not reverse else 15.0, out_ms=5.0 if not reverse else 2.0)
    meta = dict(attack=_attack_idx(y), peak=_rms_peak_idx(y, sr), n=len(y), start=0, end=len(y) - 1,
                trim_s=round(trim, 4), sr=sr, file=path)
    if reverse:
        meta['peak'] = len(y) - 1
    return y, meta


def reverse_(y):
    return np.ascontiguousarray(np.asarray(y)[::-1])


_KIND_WORDS = {
    'impact': ['impact', 'hit', 'boom', 'punch', 'slam', 'thud', 'smash', 'bang', 'stomp', 'knock', 'braam', 'thump'],
    'whoosh': ['whoosh', 'woosh', 'swoosh', 'swish', 'swoop', 'swipe', 'whip', 'passby', 'flyby', 'sweep',
               'transition'],
    'reverse_whoosh': ['reverse', 'reversed', 'rev', 'suck', 'inhale'],
    'riser': ['riser', 'rise', 'rising', 'uplifter', 'uplift', 'buildup', 'build', 'tension'],
    'swell': ['swell', 'bloom'],
    'sub_drop': ['subdrop', 'sub', 'drop', '808', 'bassdrop', 'downlifter'],
    'glitch': ['glitch', 'stutter', 'digital', 'error', 'static', 'bitcrush', 'crush', 'zap', 'data'],
    'click': ['click', 'tick', 'pop', 'shutter', 'ui', 'tap', 'blip'],
}
_VARIANT_WORDS = {
    ('impact', 'boom'): ['boom', 'cinematic', 'trailer', 'big', 'epic', 'huge', 'deep'],
    ('impact', 'punch'): ['punch', 'short', 'tight', 'dry'], ('impact', 'soft'): ['soft', 'knock', 'light', 'gentle'],
    ('impact', 'metal'): ['metal', 'metallic', 'clang', 'anvil', 'pipe'], ('impact', 'stop'): ['stop'],
    ('impact', 'stretched'): ['stretched', 'slow', 'long'], ('whoosh', 'swish'): ['swish', 'swipe', 'fast', 'short'],
    ('whoosh', 'heavy'): ['heavy', 'big', 'deep', 'low'], ('whoosh', 'orbit'): ['orbit', 'long', 'spin'],
    ('riser', 'short'): ['short'], ('riser', 'reverse_cymbal'): ['cymbal', 'crash'], ('riser', 'tonal'): ['tonal', 'synth'],
    ('sub_drop', 'short'): ['short'], ('sub_drop', 'long'): ['long'], ('click', 'pop'): ['pop'],
    ('click', 'shutter'): ['shutter', 'camera'], ('glitch', 'static'): ['static', 'noise'],
}


@functools.lru_cache(maxsize=8)
def _scan_dir(root, mtime):
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = sorted(d for d in dn if not d.startswith('.'))[:200]
        if dp[len(root):].count(os.sep) > 4:
            continue
        for f in sorted(fn):
            if f.lower().endswith(_AUDIO_EXT) and not f.startswith('.'):
                out.append(os.path.join(dp, f))
                if len(out) >= 5000:
                    return tuple(out)
    return tuple(out)


def _tokens(path, root):
    rel = os.path.relpath(path, root)
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', os.path.splitext(rel)[0])
    s = re.sub(r'(\d+)', r' \1 ', s).lower()
    return [t for t in re.split(r'[^a-z0-9]+', s) if t]


def _word_hit(tokens, words):
    return sum(1 for w in words if any(t == w or (len(w) >= 4 and t.startswith(w)) for t in tokens))


def pick_sample(sfx_dir, kind, variant=None, seed=0, avoid=None):
    """File from a user's sample folder for an SFX kind: filename / folder keywords (kind words x2, variant words
    x3, other kinds' words -1), the best-scoring files rotate by seed (never `avoid`, the previous pick). None if no
    file matches the kind."""
    root = os.path.abspath(os.path.expanduser(str(sfx_dir)))
    if not os.path.isdir(root):
        return None
    files = _scan_dir(root, os.path.getmtime(root))
    best, cands = 0, []
    for f in files:
        tk = _tokens(f, root)
        k = _word_hit(tk, _KIND_WORDS.get(kind, [kind]))
        if not k:
            continue
        sc = 2 * k + 3 * _word_hit(tk, _VARIANT_WORDS.get((kind, variant), [variant] if variant else []))
        sc -= sum(1 for k2, ws in _KIND_WORDS.items() if k2 != kind and _word_hit(tk, ws) and not
                  set(ws) & set(_KIND_WORDS.get(kind, [])))
        if sc > best:
            best, cands = sc, [f]
        elif sc == best and sc > 0:
            cands.append(f)
    if not cands:
        return None
    if avoid in cands and len(cands) > 1:
        cands = [c for c in cands if c != avoid]
    return cands[int(seed) % len(cands)]


# ---------------------------------------------------------------- event list
def _expand_events(audio, warn):
    """Normalise the sfx list: resolve kinds, defaults, t-ranges, dedupe seeds, alternate whoosh pans; samples
    (event 'file' or audio 'sfx_dir'), level preset, style."""
    out, last_key, wcount = [], {}, 0
    lvl0 = audio.get('sfx_level', 'normal')
    style0 = audio.get('sfx_style') or audio.get('genre')
    sdir = audio.get('sfx_dir')
    last_pick = {}
    for i, ev in enumerate(audio.get('sfx') or []):
        fpath = ev.get('file') or (ev.get('params') or {}).get('file')
        try:
            if fpath and not ev.get('kind'):
                kind, variant, spec = 'sample', None, dict(SAMPLE_SPEC)
            else:
                kind, variant, spec = spec_of(ev.get('kind', ''), ev.get('variant'))
        except KeyError as e:
            if not fpath:
                warn.append(f'sfx #{i}: {e} - skipped')
                continue
            kind, variant, spec = 'sample', None, dict(SAMPLE_SPEC)
        at, dur = ev.get('at'), ev.get('dur')
        rng_t = _range_of(ev)
        if rng_t is not None and dur is None:
            dur = rng_t[1] - rng_t[0]                    # a range sets the length (the event fills it)
        if at is None and rng_t is None:
            warn.append(f'sfx #{i}: no time - skipped')
            continue
        level = ev.get('level', lvl0)
        if level is None:
            level = lvl0
        try:
            lname, loff = level_name(level), level_offset(level)
        except KeyError as e:
            warn.append(f'sfx #{i}: {e} - normal used')
            lname, loff = 'normal', 0.0
        P = dict(ev.get('params') or {})
        for k in ('pan', 'width'):
            if ev.get(k) is not None:
                P[k] = ev[k]
        for k in ('hp', 'lp'):                           # 'hp_hz' / 'lp_hz' spellings used by planners
            if P.get(k + '_hz') is not None and P.get(k) is None:
                P[k] = P.pop(k + '_hz')
        P['style'] = style_of(ev.get('style') or P.get('style') or style0)
        if kind == 'whoosh' and not isinstance(P.get('pan'), (list, tuple)) and 'dir' not in P:
            P['dir'] = 1 if wcount % 2 == 0 else -1        # a series alternates its pan direction
            wcount += 1
        seed = int(ev['seed']) if ev.get('seed') is not None else i + 1
        sig = (kind, variant, seed, dur)
        if last_key.get(kind) == sig:                    # never the same buffer twice in a row
            seed += 7919
        last_key[kind] = (kind, variant, seed, dur)
        if not fpath and sdir and not ev.get('synth') and not spec.get('music'):
            fpath = pick_sample(sdir, kind, variant, seed, last_pick.get(kind))
            if fpath:
                last_pick[kind] = fpath
        smp = None
        if fpath:
            if spec.get('music'):
                warn.append(f'sfx #{i}: {kind}/{variant} processes the music; "file" ignored')
            else:
                g = lambda k, d=None: ev.get(k, P.get(k, d))
                smp = dict(path=fpath, pitch=float(g('pitch', 0.0) or 0.0), rate=float(g('rate', 1.0) or 1.0),
                           stretch=float(g('stretch', 1.0) or 1.0), reverse=bool(g('reverse', False)),
                           trim_db=float(g('trim_db', -50.0)))
        align = ev.get('align') or spec['align']
        if smp and not ev.get('align') and (kind in ('riser', 'reverse_whoosh') or smp['reverse']):
            align = 'end'                                # a sample riser / reversed sound ends on the event
        fit = None
        if at is None:                                   # a range: builds land on t1, hits / starts on t0
            at = rng_t[1] if align in ('peak', 'end') else rng_t[0]
            if align in ('peak', 'end') and ev.get('dur') is None and smp is None and rng_t[1] - rng_t[0] >= 0.02:
                fit = rng_t[1] - rng_t[0]                # mix() lengthens the synth so its build starts on t0
        out.append(dict(i=i, kind=kind, variant=variant, spec=spec, at=float(at), fit=fit,
                        dur=float(dur) if dur is not None else None, align=align,
                        offset=float(ev.get('offset_ms', 0.0)) / 1000.0, rel_lu=ev.get('rel_lu'), lu=ev.get('lu'),
                        level=lname, level_db=loff, level_set=ev.get('level') is not None,
                        gain_db=float(ev.get('gain_db', 0.0)), seed=seed, duck=ev.get('duck'), params=P, sample=smp))
    return out


def _music_op_from_event(e, ctx):
    """Kinds that process the music itself -> a music_fx op."""
    k, v, P, at = e['kind'], e['variant'], e['params'], e['at'] + e['offset']
    if k == 'stutter':
        op = dict(op='stutter', at=at, slice=P.get('slice', '1/16'), repeats=P.get('repeats', 4 if v == 'build' else 8),
                  accel=P.get('accel', 'default' if v == 'build' else None), xfade_ms=P.get('xfade_ms', 2.0),
                  pitch_step_st=P.get('pitch_step_st', 0.0))
        if e['align'] in ('peak', 'end'):
            op['end_at'] = at
        return op
    if k == 'tape_stop':
        return dict(op='tape_stop', at=at, dur=e['dur'] or e['spec']['dur'], curve=P.get('curve', 1.5),
                    resume_at=P.get('resume_at', 'next_downbeat'), start=(v == 'start'))
    if k == 'scratch':
        return dict(op='scratch', at=at, dur=e['dur'] or 0.35, rate_hz=P.get('rate_hz', 4.5), amp=P.get('amp', 2.5))
    if k == 'glitch' and v == 'crush':
        d = e['dur'] or 1.0
        return dict(op='crush', t=[at, at + d], bits=P.get('bits', 8), sr_hz=P.get('sr_hz', 11025), mix=P.get('mix', 0.8))
    if k == 'riser' and v == 'filter':
        d = e['dur'] or 2.0
        t0 = at - d if e['align'] in ('peak', 'end') else at
        return dict(op='filter', kind='hp', f=P.get('f', [20, 400]), t=[t0, t0 + d], q=P.get('q', 1.0),
                    ease=P.get('ease', 'inQuad'), reset_at=t0 + d)
    return None


_LEVEL_OPS = ('gain', 'level', 'swell', 'fade_out', 'fade_in', 'fade')


def _apply_music_ops(ops, bed, bed0, ctx, lanes, level=None):
    """Music ops in time order; level automation ops go to `level` (a _Level), mutes / gates to `lanes`."""
    sr = ctx.sr
    level = level if level is not None else _Level(len(bed), sr)

    def key(o):
        for k in ('at', 't', 'points'):
            v = o.get(k)
            if v is None:
                continue
            if k == 'points':
                return float(min(p[0] for p in v)) if v else 0.0
            return float(v[0]) if isinstance(v, (list, tuple)) else float(v)
        return 0.0
    for op in sorted(ops, key=key):
        k = op.get('op')
        try:
            if k == 'filter':
                bed = music_filter(bed, op.get('kind', 'hp'), op.get('f', (20, 400)), op['t'], sr, float(op.get('q', 1.0)),
                                   op.get('ease', 'inQuad'), op.get('reset_at'))
            elif k == 'crush':
                bed = music_crush(bed, op['t'], op.get('bits', 8), op.get('sr_hz', 11025), op.get('mix', 0.8), sr)
            elif k == 'stutter':
                g = ctx.grid() if isinstance(op.get('slice', '1/16'), str) else None
                bed = audio_stutter(bed, float(op.get('at', 0.0)), op.get('slice', '1/16'), int(op.get('repeats', 8)), sr,
                                    accel=op.get('accel'), xfade_ms=float(op.get('xfade_ms', 2.0)),
                                    pitch_step_st=float(op.get('pitch_step_st', 0.0)),
                                    bpm=op.get('bpm') or (g or {}).get('bpm') or 120.0,
                                    beats=(g or {}).get('beats') if not op.get('bpm') else None,
                                    src=bed0, end_at=op.get('end_at'))
            elif k == 'tape_stop':
                ra = op.get('resume_at')
                end = float(op['at']) + float(op.get('dur', 0.6))
                if ra == 'next_downbeat':
                    ra = ctx.next_downbeat(end - 1e-3)
                elif ra in ('never', 'end'):
                    ra = None
                bed = tape_stop(bed, float(op['at']), float(op.get('dur', 0.6)), sr, float(op.get('curve', 1.5)),
                                resume_at=ra, start=bool(op.get('start')), src=bed0)
            elif k == 'scratch':
                bed = scratch_track(bed, float(op['at']), float(op.get('dur', 0.35)), sr, float(op.get('rate_hz', 4.5)),
                                    float(op.get('amp', 2.5)), src=bed0)
            elif k == 'mute':
                lanes.add(None, lanes.window_target([op['t']], 120.0), op.get('attack_ms', 2), op.get('release_ms', 2))
            elif k == 'gate':
                lanes.add(None, lanes.window_target(op.get('holes', []), -float(op.get('depth_db', -40))),
                          op.get('attack_ms', 1), op.get('release_ms', 5))
            elif k in _LEVEL_OPS:
                _level_op(level, op)
            else:
                ctx.warn.append(f'music op {k!r} unknown - skipped')
        except Exception as e:
            ctx.warn.append(f'music op {k!r} failed: {e}')
    return bed


def _level_op(level, op):
    k = op.get('op', 'gain')
    if k == 'gain':
        v = op.get('db', op.get('to', 0.0))
        if op.get('curve', 'hold') == 'ramp':
            level.ramp(op['t'], v, op.get('until'))
        else:
            level.hold(op['t'], v, op.get('attack_ms', 10), op.get('release_ms', 10))
    elif k == 'level':
        level.points(op.get('points') or [], op.get('ease', 'linear'))
    elif k == 'swell':
        at = op.get('at', op.get('to_t'))
        if at is None and op.get('t'):
            at, dur = op['t'][1], op['t'][1] - op['t'][0]
        else:
            dur = op.get('dur', 1.5)
        level.swell(float(at), float(dur), op.get('from_db'), float(op.get('to_db', 0.0)), op.get('ease', 'inQuad'))
    elif k in ('fade_out', 'fade_in', 'fade'):
        out = k == 'fade_out' or (k == 'fade' and op.get('dir', 'out') == 'out')
        at = op.get('at', (op.get('t') or [None])[0])
        dur = op.get('dur', (op['t'][1] - op['t'][0]) if op.get('t') else 0.5)
        level.fade(float(at), float(dur), out=out, curve=op.get('curve', 'cos'), until=op.get('until'),
                   start=op.get('from'))


def _event_window(e, meta, sr):
    """The card's level window, in samples relative to the event buffer (may reach outside it: silence there)."""
    anchor, lo, hi = e['spec'].get('win', ('all', None, None))
    n = meta['n']
    if anchor == 'all' or lo is None:
        return 0, n
    base = meta['attack'] if anchor == 'attack' else meta['peak']
    return base + int(round(lo * sr)), max(base + int(round(hi * sr)), base + 1)


def _win_db(yk, a, b):
    """Loudness (LUFS) of K-weighted samples [a, b) of yk, zeros outside the array (window length = b - a)."""
    if b <= a:
        return -np.inf
    a2, b2 = max(a, 0), min(b, len(yk))
    if b2 <= a2:
        return -np.inf
    p = float(np.sum(_st(yk[a2:b2]) ** 2)) / (b - a)
    return -0.691 + 10 * math.log10(p) if p > 1e-20 else -np.inf


class _LowBand:
    """Music low end for the cards' mud rules: 30-150 Hz onset strength (low_flux, 10 ms frames) and 30-120 Hz
    power over the whole bed."""

    def __init__(self, bed, sr):
        m = np.mean(bed, axis=1)
        self.sr = sr
        self.hop = int(0.01 * sr)
        lo = filt(m, 'bp', (30, 150), sr, 2)
        e = np.maximum(uniform_filter1d(lo * lo, int(0.02 * sr), mode='constant'), 0)[::self.hop]
        le = np.log10(e + 1e-10)
        self.flux = np.maximum(0.0, np.diff(le, prepend=le[:1]))
        self.e = e
        active = e > e.max() * 1e-4
        self.p98 = float(np.percentile(self.flux[active], 98)) if active.any() else np.inf
        lo2 = filt(m, 'bp', (30, 120), sr, 2)
        self.p120 = lo2 * lo2
        nz = self.p120 > 0
        self.mean120 = float(self.p120.mean()) if nz.any() else 0.0

    def kick_at(self, t, tol=0.03):
        """True when the track has one of its strongest low hits (top 2 % low_flux) within +-tol of t."""
        a, b = int((t - tol) * 100), int((t + tol) * 100) + 1
        seg = self.flux[max(0, a):max(0, min(b, len(self.flux)))]
        return bool(len(seg) and seg.max() >= self.p98 and self.p98 > 0.05)

    def bar_excess_db(self, t, bar):
        """30-120 Hz power of the bar starting at t over the track's mean power (dB)."""
        a, b = int(t * self.sr), int((t + bar) * self.sr)
        seg = self.p120[max(0, a):max(0, min(b, len(self.p120)))]
        if not len(seg) or self.mean120 <= 0:
            return None
        return 10 * math.log10((seg.mean() + 1e-20) / self.mean120)


def _max_momentary(yk, horizon=3.0, sr=SR):
    """Loudest 400 ms (10 ms hop) of an already K-weighted event within its first `horizon` s (zeros after it)."""
    pw = np.sum(_st(yk)[:_n(horizon, sr)] ** 2, axis=1)
    W, hop = _n(0.4, sr), _n(0.01, sr)
    cs = np.concatenate([[0.0], np.cumsum(np.concatenate([pw, np.zeros(W)]))])
    k = len(pw) // hop + 1
    best = float(np.max(cs[W::hop][:k] - cs[:-W:hop][:k])) / W
    return -0.691 + 10 * math.log10(best) if best > 1e-20 else -np.inf


BUS_TP = -2.0          # SFX bus true-peak ceiling (dBTP after the master gain): soft clip + safety limiter
_HIT_KINDS = ('impact', 'sub_drop')


def mix(audio, total_s, out_wav, sr=48000):
    """Render the soundtrack of an EDL (TIMELINE.md section 4) to out_wav (48 kHz stereo 24-bit WAV), normalised to
    loudness.lufs (-14 LUFS integrated) with true peak <= loudness.tp (-1 dBTP), measured by ffmpeg ebur128.
    -> {"lufs", "tp", "sfx_count", "gain_db", "gr_max_db", "events": [...], "key", "warnings": [...]}"""
    audio = _resolve_paths(dict(audio or {}))
    sr = int(sr)
    N = max(1, int(round(float(total_s) * sr)))
    loud = audio.get('loudness') or {}
    T_I, T_TP = float(loud.get('lufs', -14.0)), float(loud.get('tp', -1.0))
    warn = []
    if audio.get('copy'):
        src = audio.get('path') or (audio.get('music') or {}).get('path')
        y = _fit(_load(src, sr), N)
        _write_wav(out_wav, y, sr)
        I, TP = measure(out_wav)
        return dict(lufs=I, tp=TP, sfx_count=0, copied=True, warnings=warn)

    bed0, minfo = _music_bed(audio.get('music'), N, sr, T_I, warn)
    has_music = bed0 is not None
    if bed0 is None:
        bed0 = np.zeros((N, 2))
    ctx = _Ctx(audio, sr, N, bed0, has_music, warn)
    events = _expand_events(audio, warn)

    # 1) music ops (music_fx + kinds that process the track), level automation, voice ducking -> bed
    pre = _Lanes(N, sr)
    level = _Level(N, sr)
    ops = list(audio.get('music_fx') or [])
    for e in events:
        if e['spec'].get('music'):
            op = _music_op_from_event(e, ctx)
            if op:
                ops.append(op)
    bed = _apply_music_ops(ops, bed0.copy(), bed0, ctx, pre, level) if ops else bed0.copy()
    for rule in audio.get('duck') or []:
        if not rule.get('under') and rule.get('t') is not None and rule.get('to') is not None:
            level.hold(rule['t'], rule['to'], rule.get('attack_ms', 10), rule.get('release_ms', 10))
    bed = level.apply(bed)
    voice = _voices(audio.get('voice'), N, sr, T_I, warn)
    vact = _voice_activity(voice, sr) if np.any(voice) else None
    for rule in audio.get('duck') or []:
        if rule.get('under') == 'voice' and vact is not None:
            depth = float(rule.get('depth_db', 8.0))
            if str(rule.get('mode', 'smooth')) == 'fast':
                tgt = vact * depth
                if rule.get('hold_ms'):
                    tgt = maximum_filter1d(tgt, size=int(rule['hold_ms']) * 2 + 1)
                pre.add(rule.get('band'), tgt, rule.get('attack_ms', 15), rule.get('release_ms', 250))
            else:
                tgt = voice_duck_curve(vact, depth, max(40.0, float(rule.get('attack_ms', 120))),
                                       float(rule.get('hold_ms', 200)), max(250.0, float(rule.get('release_ms', 500))),
                                       float(rule.get('gap_ms', 700)), regions=_voice_regions(audio.get('voice'), N, sr))
                pre.add(rule.get('band'), tgt, 0, 0)
    bed = pre.apply(bed)
    I_music = lufs_integrated(bed, sr) if has_music else -np.inf
    I_music = I_music if np.isfinite(I_music) else None
    duck_rules = [r for r in (audio.get('duck') or []) if str(r.get('under', '')).startswith('sfx')]
    filt_wins = [o['t'] for o in ops if o.get('op') == 'filter' and o.get('t')]

    # 2) SFX events: buffers, placement, music ducks / gates (levels come after the ducks: the reference is the
    #    program the event is heard with)
    duck_l, cut_l = _Lanes(N, sr), _Lanes(N, sr)
    items, n_ok = [], 0
    key_used = None
    stacked = set()
    att = [(e['i'], e['kind'], e['at'] + e['offset']) for e in events if e['kind'] in _HIT_KINDS]
    for i, k, t in att:
        if any(abs(t - t2) <= 0.02 and k != k2 for _, k2, t2 in att):
            stacked.add(i)
    vmutes, music_recs = [], []
    low = _LowBand(bed, sr) if has_music else None
    bed_cs = np.concatenate([[0.0], np.cumsum(np.sum(kweight(bed, sr) ** 2, axis=1))]) if has_music else None

    def is_drop(t, jump=3.0):
        """The music (as automated, before the event ducks) is >= jump LU louder in the second after t."""
        if bed_cs is None:
            return False
        a, c, b = int(round((t - 1.0) * sr)), int(round(t * sr)), int(round((t + 1.0) * sr))
        if a < 0 or b > N:
            return False
        p0, p1 = (bed_cs[c] - bed_cs[a]) / (c - a), (bed_cs[b] - bed_cs[c]) / (b - c)
        return p1 > 1e-12 and (p0 <= 1e-12 or 10 * math.log10(p1 / p0) >= jump)
    for e in events:
        if e['spec'].get('music'):
            if not has_music:
                warn.append(f"sfx #{e['i']} {e['kind']}/{e['variant']} processes the music, but there is none - skipped")
                continue
            n_ok += 1
            music_recs.append(dict(i=e['i'], kind=e['kind'], variant=e['variant'], at=round(e['at'] + e['offset'], 4),
                                   music=True))
            continue
        k, v, spec, P = e['kind'], e['variant'], e['spec'], dict(e['params'])
        dur = e['dur']
        notes = []
        anchor_t = e['at'] + e['offset']
        if e['sample'] is None:
            if spec.get('keyed') and P.get('root') is None and P.get('f1') is None:
                kk = ctx.confident_key()
                if kk:
                    P['root'], P['mode'] = kk.get('root'), kk.get('mode')
                    key_used = kk
                elif k == 'sub_drop':
                    dur = min(dur or spec['dur'], 1.0)          # card: unknown key -> f1 32 Hz and D <= 1 s
                    notes.append('no key: f1 32 Hz, D<=1 s')
                elif k == 'riser':
                    v = 'noise'
                    notes.append('no key: tonal -> noise')
                elif k == 'swell':
                    P['chord'] = False
                    notes.append('no key: swell without chord')
                elif k == 'impact':
                    notes.append('no key: chord hit = boom only')
            if k == 'riser' and (P.get('roll') or (P.get('roll') is None and P.get('style') == 'trap')) \
                    and not P.get('bpm'):
                P['roll'] = True
                P['bpm'] = ctx.bpm()
            if e['i'] in stacked and k == 'impact':
                P['sub_tail'] = False
            if k == 'impact' and 'plr' not in P:          # denser hits for louder presets (same peak, more body)
                P['plr'] = _PLR_TARGET.get(P.get('style'), 10.0) + {'light': 1.0, 'strong': -1.5}.get(e['level'], 0.0)
                P['clip_max'] = 5.5 if e['level'] == 'strong' else 4.0
            if k == 'glitch' and v == 'burst' and 'source' not in P and has_music:
                a0 = int(round(anchor_t * sr))
                P['source'] = bed[max(0, a0):max(0, a0) + _n(0.5, sr)]
        # mud guards (cards): one of the track's strongest kicks on this beat -> impact body above the kick;
        # heavy track sub in the bar of the sub drop (30-120 Hz >= track mean + 3 dB) -> sub drop -6 dB, <= 0.8 s
        if low is not None and P.get('mud_guard', True) and e['sample'] is None:
            if k == 'impact' and low.kick_at(anchor_t):
                P['mud'] = True                          # body above the track's kick, no sub tail, HPF 45 Hz
                P['hp'] = max(float(P.get('hp') or 0), 45.0)
                notes.append('strong track kick here: impact body moved above it (x1.6, >= 75 Hz), HPF 45 Hz')
            if k == 'sub_drop' and v != 'reverse':
                ex = low.bar_excess_db(anchor_t, 4 * 60.0 / ctx.bpm())
                if ex is not None and ex >= 3.0:
                    dur = min(dur or spec['dur'], 0.8)
                    e = dict(e, gain_db=e['gain_db'] - 6.0)
                    notes.append(f'heavy track sub (+{ex:.1f} dB): sub drop -6 dB, <=0.8 s')
        try:
            if e['sample'] is not None:
                s_ = e['sample']
                buf, meta = load_sample(s_['path'], sr, s_['trim_db'], s_['pitch'], s_['rate'], s_['stretch'],
                                        s_['reverse'], dur)
                if P.get('hp'):
                    buf = hp(buf, float(P['hp']), sr, 2)
                if P.get('lp'):
                    buf = lp(buf, float(P['lp']), sr, 2)
                p = P.get('pan', 0.0)
                if p and not isinstance(p, (list, tuple)):
                    buf = pan(buf, float(np.clip(p, -1, 1)))
                meta.setdefault('lvl', 0.0)
                if k == 'impact' and (P.get('stop') or v == 'stop'):
                    meta['stop'] = P.get('stop') or 0.5
            else:
                buf, meta = synth_ex(k, v, sr, dur, e['seed'], **P)
                al = e['align'] if e['align'] in ('attack', 'peak', 'start', 'end') else spec['align']
                L = e.get('fit')
                if L and al in ('peak', 'end'):
                    pre = float(meta[al]) / sr           # buffer start -> peak / end; the range wants L
                    if pre > 0.02 and abs(pre - L) > max(0.01, 0.02 * L):
                        d2 = float(dur or L) * L / pre
                        buf, meta = synth_ex(k, v, sr, d2, e['seed'], **P)
                        notes.append(f'range {L:.2f} s: {d2:.2f} s long, so it builds from t0 and lands on t1')
        except Exception as ex:
            warn.append(f"sfx #{e['i']} {k}/{v}: {ex} - skipped")
            continue
        buf = buf.astype(np.float64)
        align = e['align'] if e['align'] in ('attack', 'peak', 'start', 'end') else spec['align']
        start = int(round(anchor_t * sr)) - int(meta[align])
        if min(N, start + len(buf)) <= max(0, start):
            warn.append(f"sfx #{e['i']} {k}/{v} at {anchor_t:.2f}s is outside the timeline - skipped")
            continue
        w0, w1 = _event_window(e, meta, sr)
        # event-driven music changes: glitch gates, impact stop (not part of the level reference), ducking
        for (g0, g1, gdb) in meta.get('gate') or []:
            cut_l.add(None, cut_l.window_target([(start / sr + g0, start / sr + g1)], -gdb), 1, 5)
        stop_to = None
        if meta.get('stop'):
            st = meta['stop']
            te = ctx.next_downbeat(anchor_t + 0.25) if st in ('next_downbeat', True) else anchor_t + float(st)
            stop_to = te if te is not None else anchor_t + 0.5
            cut_l.add(None, cut_l.window_target([(anchor_t, stop_to)], 120.0), 2, 1)
        if meta.get('mute_voice'):
            vmutes.append((anchor_t, anchor_t + len(buf) / sr))
        if has_music:
            dk = _duck_for(e, spec, duck_rules)
            if dk:
                if k == 'riser' and any(f[0] < anchor_t and f[1] > anchor_t - (meta['peak'] - meta['attack']) / sr
                                        for f in filt_wins):
                    dk = dict(dk, depth_db=float(dk.get('depth_db', 3.0)) / 2)   # not both at full with a filter build
                _add_sfx_duck(duck_l, dk, buf, start, meta, sr)
            dip_t = None
            if k in _HIT_KINDS and v != 'reverse' and e.get('duck') is not False:
                ta = (start + meta['attack']) / sr
                if is_drop(ta) or (spec.get('main') and e['level'] == 'strong'):
                    dip, hold, rel = _DROP_DIP[e['level']], 0.15, 600   # a drop: the music breathes in after it
                    notes.append(f'drop: music dips {dip:g} dB')
                else:
                    dip = _HIT_DIP[e['level']][1 if spec.get('main') else 0]
                    hold, rel = (0.12, 450) if spec.get('main') else (0.08, 300)
                if dip > 0:                              # make room: the whole music dips under the hit
                    duck_l.add(None, duck_l.window_target([(ta - 0.005, ta + hold)], dip), 3, rel)
                    dip_t = ta
        else:
            dip_t = None
        items.append(dict(e=e, k=k, v=v, spec=spec, buf=buf, meta=meta, start=start, w=(w0, w1), notes=notes,
                          align=align, anchor=anchor_t, stop_to=stop_to, P=P, dip_t=dip_t))

    bed_pre = bed                                     # step 6 may deepen dips and redo the event ducks
    bed = duck_l.apply(bed_pre)
    prog = bed + voice
    I_prog = lufs_integrated(prog, sr) if (has_music or np.any(voice)) else -np.inf
    I_prog = I_prog if np.isfinite(I_prog) else None
    prog_k = kweight(prog, sr) if I_prog is not None else None
    prog_cs = np.concatenate([[0.0], np.cumsum(np.sum(prog_k ** 2, axis=1))]) if prog_k is not None else None
    bed = cut_l.apply(bed)

    def st_lufs(t0, t1):
        """The program's (music + voice, after the ducks) loudness over [t0, t1] - the audibility reference."""
        a, b = max(0, int(round(t0 * sr))), min(N, int(round(t1 * sr)))
        if prog_cs is None or b - a < 16:
            return None
        p = (prog_cs[b] - prog_cs[a]) / (b - a)
        return -0.691 + 10 * math.log10(p) if p > 1e-12 else -70.0
    if vmutes:
        vl = _Lanes(N, sr)
        vl.add(None, vl.window_target(vmutes, 120.0), 5, 5)
        voice = vl.apply(voice)
    ceil_lin = 10 ** (BUS_TP / 20.0)

    # 3) levels: event loudness vs the program in the event's window + the audibility floor (QA's rule)
    placed = []
    series_t, series_db = None, 0.0
    # QA groups (anchors within QA_GROUP_S): the floor goes to the member(s) with the strictest need - a riser
    # ending on a hit is carried by the hit, not pushed up itself
    lead = set()
    order = sorted(range(len(items)), key=lambda j: items[j]['anchor'])
    grp = []
    for j in order + [None]:
        if j is not None and grp and items[j]['anchor'] - items[grp[-1]]['anchor'] <= QA_GROUP_S:
            grp.append(j)
            continue
        if grp:
            nd = {m: (QA_MIN_LU[QA_FAMILY[items[m]['k']]] + items[m]['e']['level_db'] + items[m]['e']['gain_db'])
                  for m in grp if QA_FAMILY.get(items[m]['k']) and items[m]['e']['lu'] is None}
            if nd:
                top = max(nd.values())
                lead |= {m for m, v in nd.items() if v >= top - 1e-6}
        grp = [j] if j is not None else []
    for jj, it in enumerate(items):
        e, k, v, spec, buf, meta, start = it['e'], it['k'], it['v'], it['spec'], it['buf'], it['meta'], it['start']
        w0, w1 = it['w']
        anchor_t, notes = it['anchor'], it['notes']
        base = float(spec.get('lu', spec.get('rel_lu', -6))) + e['level_db']
        fam = QA_FAMILY.get(k)
        qa_auto = e['lu'] is None and e['rel_lu'] is None
        need = None if (fam is None or e['lu'] is not None) else QA_MIN_LU[fam] + e['level_db'] + e['gain_db']
        if e['lu'] is not None:
            target, auto = float(e['lu']), False
        elif e['rel_lu'] is not None and not e['level_set']:   # legacy: the cards' scale, moved by the preset
            target, auto = base + float(e['rel_lu']) - float(spec.get('rel_lu', -6)), False
        else:                                             # the preset decides (an event 'level' beats rel_lu)
            target, auto = base, True
        extra = e['gain_db'] + float(meta.get('lvl', 0.0))
        if auto and e['i'] in stacked:
            extra -= 1.5                                  # impact + sub drop on one attack: both -1.5 dB
        series = 0.0
        if k == 'impact' and auto:
            if series_t is not None and anchor_t - series_t < 2.1:
                series_db = max(series_db - 1.5, -6.0)    # series: each next one 1.5 dB quieter (card window)
            else:
                series_db = 0.0
            series_t = anchor_t
            series = series_db
        need_eff = need
        if qa_auto and vact is not None and k in QA_UNDER_VOICE:
            c0, c1 = int((start + w0) / sr * CR), int((start + w1) / sr * CR)
            if c1 > c0 and np.mean(vact[max(c0, 0):max(min(c1, len(vact)), 0)] if c1 > 0 else [0]) > 0.3:
                extra -= 6.0                              # under voice: -6 dB and HPF 300 Hz
                buf = hp(buf, 300, sr, 2)
                notes.append('under voice: -6 dB, HPF 300 Hz')
                need_eff = None if need is None else need - 6.0
        buf_k = kweight(buf, sr)
        L_s = _win_db(buf_k, w0, w1)
        if not np.isfinite(L_s):
            L_s = _ms_db(buf_k)
        if I_prog is not None:
            L_p = _win_db(prog_k, start + w0, start + w1)
            ref = max(L_p, I_prog - 12.0)
        else:
            L_p, ref = None, T_I
        # every level rule is a loudness the event must reach in a window: (required LUFS, meter on the event)
        needs = [(ref + target + extra + series, lambda yk: _win_db(yk, w0, w1))]
        if spec.get('win2') and I_prog is not None:     # short hits: also >= target + off over 400 ms (momentary)
            span, off = spec['win2']
            a2 = int(meta['attack'])
            b2 = a2 + int(round(float(span) * sr))
            ref2 = max(_win_db(prog_k, start + a2, start + b2), I_prog - 12.0)
            needs.append((ref2 + target + float(off) + extra + series, lambda yk, a2=a2, b2=b2: _win_db(yk, a2, b2)))
        st_ref, st_i = None, None
        if need_eff is not None and jj in lead and not meta.get('stop') and I_prog is not None:
            # audibility floor, first estimate (step 6 verifies the final mix): loudest 400 ms >= the program's 3 s
            # short-term (after a hit, centred otherwise) + need + margin
            ta = (start + meta['attack']) / sr if k in QA_ATTACK else anchor_t
            st_ref = st_lufs(ta, ta + 3.0) if k in QA_ATTACK else st_lufs(ta - 1.5, ta + 1.5)
            if st_ref is not None and st_ref > -60:
                needs.append((st_ref + need_eff + QA_MARGIN, _max_momentary))
                st_i = len(needs) - 1
        gains = [req - L(buf_k) for req, L in needs]
        gains = [g if np.isfinite(g) else -np.inf for g in gains]
        g_db = max(gains)
        if not np.isfinite(g_db):
            g_db = ref + target - L_s + extra + series
        g_rules = max(gains[:st_i]) if st_i is not None else g_db   # what the level rules alone ask for
        floor_on = st_i is not None and np.isfinite(gains[st_i]) and gains[st_i] > g_rules
        tp_buf = true_peak_db(buf, sr)
        cap = BUS_TP + CLIP_ALLOW[e['level']] - tp_buf if np.isfinite(tp_buf) else np.inf
        if g_db > cap:                                    # headroom: clip transients, never squash the body
            notes.append(f'headroom: {cap - g_db:.1f} dB under its target')
            g_db = cap
        y = buf * db(g_db)
        if np.isfinite(tp_buf) and tp_buf + g_db > BUS_TP - 3.0:
            # the bus soft clip would cost this event loudness: clip it here and make the loss up (<= the cap)
            for _ in range(3):
                yc = soft_clip(y, ceil_lin, 3.0)
                yck = kweight(yc, sr)
                short = max(req - L(yck) for req, L in needs)
                if not np.isfinite(short) or short < 0.2 or g_db >= cap - 0.05:
                    break
                g_db = min(cap, g_db + short)
                y = buf * db(g_db)
            y = soft_clip(y, ceil_lin, 3.0)
        n_ok += 1
        # floor_db: dB the audibility floor added on top of the level rules (here, then step 6 adds its lifts)
        floor0 = max(0.0, g_db - min(g_rules, cap)) if floor_on and np.isfinite(g_rules) else 0.0
        rec = dict(i=e['i'], kind=k, variant=v, at=round(anchor_t, 4), start=round(start / sr, 4),
                   end=round((start + len(y)) / sr, 4), align=it['align'], level=e['level'], lu=round(target, 2),
                   rel_lu=round(target, 2), gain_db=round(g_db, 2), ref_lufs=round(ref, 2),
                   music_lufs=None if L_p is None else round(L_p, 2), seed=e['seed'],
                   win=[round((start + w0) / sr, 4), round((start + w1) / sr, 4)], main=bool(spec.get('main')),
                   need_lu=None if need is None else round(need, 2), auto=qa_auto, stop=bool(meta.get('stop')))
        if e['sample'] is not None:
            rec['file'] = e['sample']['path']
        else:
            rec['style'] = it['P'].get('style')
        if it['stop_to'] is not None:
            rec['stop_to'] = round(it['stop_to'], 3)
        if notes:
            rec['notes'] = notes
        placed.append(dict(rec=rec, y=y, start=start, buf=buf, g=g_db, cap=cap, tp=tp_buf, dip_t=it['dip_t'],
                           dip=0.0, lead=jj in lead, floor=floor0))

    def place_again(p):
        y = p['buf'] * db(p['g'])
        if np.isfinite(p['tp']) and p['tp'] + p['g'] > BUS_TP - 3.0:
            y = soft_clip(y, ceil_lin, 3.0)
        p['y'] = y
        p['rec']['gain_db'] = round(p['g'], 2)

    # 4) SFX bus: HPF 30 Hz, soft clip + safety limiter at BUS_TP after the master gain
    def build_bus(trims):
        b = np.zeros((N, 2))
        for j, p in enumerate(placed):
            yy, start = p['y'], p['start']
            b0, b1 = max(0, start), min(N, start + len(yy))
            b[b0:b1] += yy[b0 - start:b1 - start] * db(trims.get(j, 0.0))
        if not np.any(b):
            return b
        b = hp(b, 30, sr, 2)
        I_pre = lufs_integrated(bed + voice + b, sr)
        G_est = T_I - I_pre if np.isfinite(I_pre) else 0.0
        b = soft_clip_regions(b, 10 ** ((BUS_TP - G_est) / 20.0), 3.0)
        return tp_limit(b, sr, BUS_TP + 0.5 - G_est, look_ms=1.0, rel_ms=60)[0]

    bus = build_bus({})
    dbg = audio.get('debug') or {}
    mkw = dict(max_gr=float(loud.get('max_gr_db', 8.0)), max_gain=20.0 if (has_music or np.any(voice)) else 12.0)
    y, mi = master(bed + voice + bus, sr, T_I, T_TP, **mkw)

    # 5) headroom: the master limiter may hold a hit down (20 ms average) by <= 4 dB (main) / 3 dB, else lower it
    trims = {}
    gr_s = uniform_filter1d(mi['gr'], max(1, int(0.02 * sr))) if len(mi['gr']) else mi['gr']
    for j, p in enumerate(placed):
        rec = p['rec']
        if rec['kind'] not in _HIT_KINDS:
            continue
        a0 = max(0, int(round(rec['at'] * sr)))
        gmax = float(np.max(gr_s[a0:a0 + int(0.1 * sr)])) if a0 < N else 0.0
        lim = (4.0 if rec['main'] else 3.0) + (1.0 if rec.get('level') == 'strong' else 0.0)
        if gmax > lim + 0.05:
            trims[j] = -(gmax - lim)
            rec['gain_db'] = round(rec['gain_db'] + trims[j], 2)
            rec.setdefault('notes', []).append(f'limiter {gmax:.1f} dB > {lim} dB: {trims[j]:.1f} dB')
    if trims:
        bus = build_bus(trims)
        y, mi = master(bed + voice + bus, sr, T_I, T_TP, gain0=mi['gain_db'], ceil0=mi['ceil_db'], **mkw)

    # 6) audibility as ed_qa measures it, on the final mix (after the master gain and the limiter): groups under
    #    their need + QA_MARGIN are raised within their headroom, then the music dips deeper under their hits
    recs = [p['rec'] for p in placed]

    def as_heard():
        g = db(mi['gain_db'])
        gl = (db(-mi['gr']) if len(mi['gr']) else np.ones(N))[:, None] * g
        return bus * gl, (bed + voice) * gl, voice * gl

    audit = audibility(recs, *as_heard(), sr=sr) if recs else []
    for _ in range(6):
        short = [r for r in audit if r.get('need_lu') is not None and r.get('rel_lu') is not None
                 and r['rel_lu'] < r['need_lu'] + QA_MARGIN - 0.05]
        if not short:
            break
        raised, dipped = False, False

        def lift(js, d):
            nonlocal raised
            got = 0.0
            for j in js:
                p = placed[j]
                if trims.get(j):                          # the floor beats the limiter preference: fold the trim in
                    p['g'] += trims[j]
                    trims[j] = 0.0
                    place_again(p)
                up = min(d, max(0.0, p['cap'] - p['g']))
                if up > 0.05:
                    p['g'] += up
                    p['floor'] += up
                    place_again(p)
                    raised = True
                got = max(got, up)
            return got

        for r in short:
            # order: the group's leaders (strictest need) up within their headroom -> the music dips deeper under the
            # group's hits (<= +3 dB) -> strong leaders past their headroom (<= +2 dB more transient clipping) ->
            # the other members (a quieter riser end hardly moves the group's loudest 400 ms)
            d = r['need_lu'] + QA_MARGIN - r['rel_lu'] + 0.15
            leaders = [j for j in r['members'] if placed[j]['lead']] or list(r['members'])
            d -= lift(leaders, d)
            if d > 0.3:
                for j in r['members']:
                    p = placed[j]
                    if p['dip_t'] is not None and p['dip'] < 3.0:
                        x = 3.0 - p['dip']                # a dip moves the 3 s reference far less than its depth
                        p['dip'] += x
                        base_dip = _DROP_DIP.get(p['rec']['level'], 4.0)
                        duck_l.add(None, duck_l.window_target([(p['dip_t'] - 0.005, p['dip_t'] + 0.2)],
                                                              base_dip + p['dip']), 3, 600)
                        p['rec'].setdefault('notes', []).append(f"audibility: music dips {p['dip']:.1f} dB more")
                        dipped = True
                        d = 0.0
                        break
            if d > 0.3:
                for j in leaders:
                    p = placed[j]
                    if p['rec'].get('level') == 'strong' and p.get('over', 0.0) < 2.0:
                        x = min(2.0 - p.get('over', 0.0), d)
                        p['over'] = p.get('over', 0.0) + x
                        p['cap'] += x
                        p['rec'].setdefault('notes', []).append(f"audibility: +{p['over']:.1f} dB past the headroom")
                if lift(leaders, d) > 0.05:
                    d = 0.0
            if d > 0.3:
                lift([j for j in r['members'] if j not in leaders], d)
        if not raised and not dipped:
            break
        if dipped:
            bed = cut_l.apply(duck_l.apply(bed_pre))
        bus = build_bus(trims)
        y, mi = master(bed + voice + bus, sr, T_I, T_TP, gain0=mi['gain_db'], ceil0=mi['ceil_db'], **mkw)
        audit = audibility(recs, *as_heard(), sr=sr)
    for p in placed:
        p['rec']['floor_db'] = round(float(p['floor']), 2)
    for r in music_recs:
        r['floor_db'] = 0.0
    for r in audit:
        for j in r['members']:
            recs[j]['st_lu'] = r.get('rel_lu')
            recs[j]['need_lu'] = r.get('need_lu')
        r['ok'] = None if (r.get('need_lu') is None or r.get('rel_lu') is None) else bool(
            r['rel_lu'] >= r['need_lu'] - QA_TOL)
        if r['ok'] is False:
            warn.append(f"sfx at {r['t']:.2f} s ({'+'.join(r['kinds'])}): {r['rel_lu']:.1f} LU over the program, needs "
                        f"{r['need_lu']:.1f} (headroom exhausted)")
    if dbg.get('stems'):
        os.makedirs(dbg['stems'], exist_ok=True)
        g = db(mi['gain_db'])
        for name, sgn in (('music', bed), ('voice', voice), ('sfx', bus)):
            _write_wav(os.path.join(dbg['stems'], f'{name}.wav'), sgn * g, sr, codec='pcm_f32le')
        np.save(os.path.join(dbg['stems'], 'limiter_gr_db.npy'), mi['gr'].astype(np.float32))
    _write_wav(out_wav, y, sr)
    I, TP = measure(out_wav)
    if mi.get('capped') == 'gr':
        warn.append(f"program too dynamic for {T_I:g} LUFS with <= {mkw['max_gr']:g} dB of sustained limiting (hits "
                    f"<= {mkw['max_gr'] + FAST_EXTRA_DB:g} dB): {I:.1f} LUFS (raise loudness.max_gr_db to force it)")
    elif mi.get('capped') == 'gain':
        warn.append(f"program too sparse/quiet: master gain capped at +{mkw['max_gain']:g} dB, {I:.1f} LUFS")
    all_recs = recs + music_recs
    warn.extend(_qa_limits(all_recs, ctx.bpm))
    for r in audit:
        r.pop('members', None)
    return dict(lufs=I, tp=TP, sfx_count=n_ok, gain_db=round(mi['gain_db'], 2),
                gr_max_db=round(float(np.max(mi['gr'])) if len(mi['gr']) else 0.0, 2), iters=mi['iters'],
                music_lufs=None if I_music is None else round(I_music, 2),
                program_lufs=None if I_prog is None else round(I_prog, 2),
                sfx_level=audio.get('sfx_level', 'normal'),
                sfx_style=style_of(audio.get('sfx_style') or audio.get('genre')),
                key=key_used or (ctx._key if ctx._key_done else None),
                events=sorted(all_recs, key=lambda r: r['i']), audibility=audit,
                limiter=dict(gain_db=round(mi['gain_db'], 2), ceil_db=round(mi['ceil_db'], 2),
                             gr_max_db=round(float(np.max(mi['gr'])) if len(mi['gr']) else 0.0, 2),
                             slow_gr_max_db=round(float(mi.get('slow_max_db', 0.0)), 2),
                             gr=_gr_points(mi['gr'], sr)), warnings=warn)


def _gr_points(gr, sr=SR, hz=100):
    """Limiter gain reduction as [[t, dB], ...] at `hz` (max-pooled), only where it acts (> 0.05 dB) plus the zero
    points around each run: compact enough for the render sidecar, exact enough to re-apply to stems."""
    if gr is None or not len(gr):
        return []
    hop = max(1, int(sr // hz))
    k = len(gr) // hop
    if k < 1:
        return []
    m = np.max(np.asarray(gr[:k * hop], float).reshape(k, hop), axis=1)
    on = m > 0.05
    out = []
    for a, b in _runs(on):
        if a > 0:
            out.append([round((a - 1) * hop / sr, 3), 0.0])
        out += [[round(i * hop / sr, 3), round(float(m[i]), 2)] for i in range(a, b)]
        if b < k:
            out.append([round(b * hop / sr, 3), 0.0])
    return out


def _qa_loud(y, sr=SR):
    """(cumsum of K-weighted power, n) for _QALoud-style window loudness (the same arithmetic as ed_qa.Loud)."""
    k = kweight(_st(y), sr) if len(y) else np.zeros((0, 2))
    return np.concatenate([[0.0], np.cumsum((k * k).sum(1))]), len(k)


def _ql(c, n, t0, t1, sr=SR):
    a, b = max(0, int(round(t0 * sr))), min(n, int(round(t1 * sr)))
    if b - a < 16:
        return None
    p = (c[b] - c[a]) / (b - a)
    return -0.691 + 10 * math.log10(p) if p > 1e-12 else -70.0


def _ql_max_momentary(c, n, t0, t1, win=0.4, hop=0.025, sr=SR):
    best, t = None, t0
    while t <= t1 + 1e-9:
        v = _ql(c, n, t - win / 2, t + win / 2, sr)
        if v is not None and (best is None or v > best):
            best = v
        t += hop
    return best


def audibility(recs, sfx, prog, voice=None, sr=SR):
    """ed_qa's sfx check on arrays as heard (after the master gain and the limiter): recs = mix() event records
    (i, kind, at, start, end, need_lu, auto); sfx = the SFX bus, prog = music + voice. Events within QA_GROUP_S form
    a group (strictest need; auto-level QA_UNDER_VOICE groups under a voice need 6 dB less); rel_lu = the loudest
    400 ms of the SFX over the members' span minus the program's 3 s short-term after the group (hits) or around it.
    -> [{"t", "kinds", "events", "members", "span", "need_lu", "rel_lu", "sfx_lufs", "program_st_lufs",
         "under_voice"}]"""
    N = len(prog)
    dur = N / sr
    items = sorted([(r['at'], j, r) for j, r in enumerate(recs) if r.get('at') is not None and not r.get('music')
                    and r.get('start') is not None], key=lambda x: (x[0], x[1]))
    groups = []
    for at, j, r in items:
        if groups and at - groups[-1][-1][0] <= QA_GROUP_S:
            groups[-1].append((at, j, r))
        else:
            groups.append([(at, j, r)])
    cs, ns = _qa_loud(sfx, sr)
    cp, npg = _qa_loud(prog, sr)
    cv = _qa_loud(voice, sr) if voice is not None and np.any(voice) else None
    rows = []
    for g in groups:
        rr = [x[2] for x in g]
        at = min(x[0] for x in g)
        s0, s1 = min(r['start'] for r in rr), max(r['end'] for r in rr)
        attack = any(r['kind'] in QA_ATTACK for r in rr)
        ref = (at, min(dur, at + 3.0)) if attack else (max(0.0, at - 1.5), min(dur, at + 1.5))
        needs = [r.get('need_lu') for r in rr if r.get('need_lu') is not None]
        need = max(needs) if needs else None
        uv = False
        if need is not None and cv is not None and all(r['kind'] in QA_UNDER_VOICE and r.get('auto') for r in rr):
            lv, lp_ = _ql(cv[0], cv[1], s0, s1, sr), _ql(cp, npg, s0, s1, sr)
            if lv is not None and lp_ is not None and lv > -60 and lv >= lp_ - 3.0:
                need, uv = need - 6.0, True
        row = dict(t=round(at, 3), kinds=sorted({r['kind'] for r in rr}), events=[r['i'] for r in rr],
                   members=[x[1] for x in g], span=[round(s0, 3), round(s1, 3)],
                   need_lu=None if need is None else round(need, 2), under_voice=uv)
        bs = _ql_max_momentary(cs, ns, max(0.2, s0), max(0.2, s1), sr=sr)
        lm = _ql(cp, npg, *ref, sr=sr)
        if bs is not None and lm is not None and lm > -60:
            row.update(sfx_lufs=round(bs, 2), program_st_lufs=round(lm, 2), rel_lu=round(bs - lm, 2))
        elif bs is not None:
            row.update(sfx_lufs=round(bs, 2), note='no music or voice around the event')
        rows.append(row)
    return rows


def soft_clip_regions(x, ceil, knee_db=6.0, os_=4):
    """soft_clip() only where |x| comes within knee_db of ceil (with 64 samples of context): long buses stay cheap."""
    th = ceil * 10 ** (-knee_db / 20.0)
    a = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    cand = maximum_filter1d((a > th).astype(np.uint8), 129) > 0
    if not cand.any():
        return x
    y = np.array(x, float, copy=True)
    for a0, b0 in _runs(cand):
        lo, hi = max(0, a0 - 64), min(len(x), b0 + 64)
        seg = soft_clip(x[lo:hi], ceil, knee_db, os_)
        y[a0:b0] = seg[a0 - lo:b0 - lo]
    return y


# card limits per sliding window: (kind, variant filter or None, max count, window s, label)
_LIMITS = [('whoosh', None, 3, 10.0, 'whoosh <= 3 per 10 s (series of transitions up to 5)'),
           ('reverse_whoosh', None, 3, 10.0, 'reverse whoosh <= 3 per 10 s'),
           ('impact', None, 3, 10.0, 'impacts <= 3 per 10 s (drop of phonk/sport: 1 per beat for <= 2 bars)'),
           ('impact', ('boom', 'metal', 'stretched', 'chord'), 1, 15.0, 'main hit (boom) <= 1 per 15 s'),
           ('riser', ('noise', 'tonal', 'reverse_cymbal'), 1, 20.0, 'long riser <= 1 per 20-30 s'),
           ('riser', ('short',), 1, 10.0, 'short riser <= 1 per 10 s'),
           ('swell', None, 1, 8.0, 'swell <= 1 per 8 s'),
           ('sub_drop', None, 2, 30.0, 'sub drop <= 2 per 30 s'),
           ('glitch', ('burst', 'static', 'transition'), 2, 10.0, 'glitch bursts <= 2 per 10 s outside series'),
           ('click', None, 8, 1.0, 'clicks <= 8 per second'),
           ('stutter', None, 2, 30.0, 'stutter 1-2 per 30 s'),
           ('tape_stop', ('stop',), 1, 1e9, 'tape stop once per video')]


def _qa_limits(recs, bpm_fn=lambda: 120.0):
    """Warnings for the cards' frequency limits (events as placed); bpm_fn is called only when needed."""
    out = []
    for kind, vs, mx, win, label in _LIMITS:
        ts = sorted(r['at'] for r in recs if r['kind'] == kind and (vs is None or r['variant'] in vs))
        for i in range(len(ts)):
            j = np.searchsorted(ts, ts[i] + win - 1e-9)
            if j - i > mx:
                out.append(f'limit: {label} ({j - i} from {ts[i]:.2f} s)')
                break
    subs = sorted(r['at'] for r in recs if r['kind'] == 'sub_drop')
    if len(subs) > 1 and any(b - a < 8 * 4 * 60.0 / bpm_fn() for a, b in zip(subs, subs[1:])):
        out.append('limit: two sub drops closer than 8 bars')
    return out


def _resolve_paths(audio):
    """Relative paths resolve against audio['base_dir'] when given."""
    base = audio.get('base_dir')
    if not base:
        return audio
    fix = lambda p: p if (not p or os.path.isabs(p)) else os.path.join(base, p)
    audio = dict(audio)
    if audio.get('music'):
        audio['music'] = dict(audio['music'], path=fix(audio['music'].get('path')))
    if audio.get('voice'):
        audio['voice'] = [dict(v, path=fix(v.get('path'))) for v in audio['voice']]
    if audio.get('path'):
        audio['path'] = fix(audio['path'])
    if audio.get('sfx_dir'):
        audio['sfx_dir'] = fix(audio['sfx_dir'])
    if audio.get('sfx'):
        audio['sfx'] = [dict(e, file=fix(e['file'])) if e.get('file') else e for e in audio['sfx']]
    return audio


def _duck_for(e, spec, rules):
    """Duck params for an event: event 'duck' (true / dict / false) > matching 'under: sfx[:kind]' rules > card default
    (depth scaled by the event's level preset; whooshes duck their band from 'normal' up)."""
    card = spec.get('duck')
    ev = e.get('duck')
    if ev is False:
        return None
    lv = e.get('level', 'normal')
    d = None
    if card and (spec.get('duck_on') or (e['kind'] in ('whoosh', 'reverse_whoosh') and lv != 'light')):
        d = dict(card)
        d['depth_db'] = float(d.get('depth_db', 4.0)) * _DUCK_SCALE.get(lv, 1.0)
    for r in rules:
        u = r.get('under')
        if u == 'sfx' or u == f"sfx:{e['kind']}" or u == f"sfx:{e['kind']}/{e['variant']}":
            base = dict(card) if card else dict(band=None, depth_db=4.0, attack_ms=10, release_ms=200, mode='follow')
            base.update({k: v for k, v in r.items() if k != 'under'})
            d = base
    if ev is True:
        d = d or (dict(card) if card else dict(band=None, depth_db=4.0, attack_ms=10, release_ms=200, mode='follow'))
    elif isinstance(ev, dict):
        d = dict(d or card or dict(band=None, depth_db=4.0, attack_ms=10, release_ms=200, mode='follow'))
        d.update(ev)
    return d


def _add_sfx_duck(lanes, d, y, start, meta, sr):
    """Sidechain the music under one event: fixed (attack / hold / release from the attack) or follow (the event's
    own envelope: 0 dB at its peak -> no duck at -20 dB; risers only in their last quarter, released at the cut)."""
    depth = float(d.get('depth_db', 4.0))
    if depth <= 0:
        return
    band = d.get('band')
    c0 = int(math.floor(start / sr * CR))
    if d.get('mode', 'follow') == 'fixed':
        ta = (start + meta['attack']) / sr
        hold = float(d.get('hold_ms', 60)) / 1000.0
        tgt = lanes.window_target([(ta - 0.004, ta + hold + 0.002)], depth)
        lanes.add(band, tgt, d.get('attack_ms', 2), d.get('release_ms', 200))
        if d.get('wide_db'):
            lanes.add(None, lanes.window_target([(ta - 0.004, ta + hold + 0.002)], float(d['wide_db'])),
                      d.get('attack_ms', 2), d.get('release_ms', 200))
        return
    hop = int(sr / CR)
    r = rms_env(y, sr, 10.0)[::hop]
    with np.errstate(divide='ignore'):
        L = 20 * np.log10(np.maximum(r, 1e-9))
    env = np.clip((L - L.max() + 20.0) / 20.0, 0, 1)
    if d.get('last'):
        pk = meta['peak'] // hop
        span = int(round((meta['peak'] - meta['attack']) / hop * float(d['last'])))
        m = np.zeros_like(env)
        m[max(0, pk - max(span, 1)):pk + 1] = 1
        env = env * m
    tgt = np.zeros(lanes.n)
    i0, i1 = max(c0, 0), min(c0 + len(env), lanes.n)
    if i1 > i0:
        tgt[i0:i1] = env[i0 - c0:i1 - c0] * depth
    lanes.add(band, tgt, d.get('attack_ms', 30), d.get('release_ms', 150))


# ============================================================================ demo / CLI
def _sheet(items, out_png, sr=SR, title=''):
    """Spectrogram (log frequency) + 10 ms RMS envelope (dB) + spectral centroid for each (label, y, meta)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    k = len(items)
    fig, ax = plt.subplots(k, 2, figsize=(14, 2.3 * k), squeeze=False, gridspec_kw=dict(width_ratios=[1.4, 1]))
    for i, (label, y, meta) in enumerate(items):
        m = np.mean(_st(y), axis=1)
        nper = 1024 if len(m) > 4096 else 256
        f, t, S = ss.spectrogram(m, sr, nperseg=nper, noverlap=nper * 3 // 4)
        S = 10 * np.log10(S + 1e-14)
        a = ax[i, 0]
        a.pcolormesh(t, np.maximum(f, 10), S, vmin=S.max() - 80, vmax=S.max(), shading='auto', cmap='magma')
        a.set_yscale('log')
        a.set_ylim(20, sr / 2)
        a.set_ylabel(label, fontsize=8)
        if len(m) > 2048:
            tc, c = centroid(y, sr, 1024, 256)
            a.plot(tc, c, color='c', lw=0.8)
        for nm, col in (('attack', 'lime'), ('peak', 'w')):
            if meta and nm in meta:
                a.axvline(meta[nm] / sr, color=col, lw=0.8, ls='--')
        r = rms_env(y, sr, 10.0)
        tt = np.arange(len(r)) / sr
        b = ax[i, 1]
        with np.errstate(divide='ignore'):
            b.plot(tt, 20 * np.log10(np.maximum(r, 1e-6)), color='k', lw=0.8)
        b.set_ylim(-80, 0)
        b.grid(alpha=0.3)
        if meta:
            for nm, col in (('attack', 'g'), ('peak', 'r')):
                if nm in meta:
                    b.axvline(meta[nm] / sr, color=col, lw=0.8, ls='--')
            b.set_title(f"{len(y) / sr * 1000:.0f} ms  attack {meta.get('attack', 0) / sr * 1000:.1f} ms  "
                        f"peak {meta.get('peak', 0) / sr * 1000:.0f} ms", fontsize=8)
    if title:
        fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(out_png, dpi=80)
    plt.close(fig)


def demo(out_dir, sr=SR):
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for kind, K in KINDS.items():
        items = []
        for v in K['variants']:
            P = {}
            if (kind, v) in (('riser', 'tonal'), ('impact', 'chord'), ('swell', 'swell')):
                P['root'] = 'A'
            if kind == 'riser' and v == 'noise':
                P['roll'] = True
            y, meta = synth_ex(kind, v, sr, None, 1, **P)
            _write_wav(os.path.join(out_dir, f'{kind}.{v}.wav'), y, sr)
            items.append((f'{kind}.{v}', y, meta))
            res[f'{kind}.{v}'] = dict(dur=round(len(y) / sr, 3), attack_ms=round(meta['attack'] / sr * 1000, 1),
                                      peak_ms=round(meta['peak'] / sr * 1000, 1))
        _sheet(items, os.path.join(out_dir, f'sheet_{kind}.png'), sr, kind)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd')
    sub.add_parser('list')
    a = sub.add_parser('synth')
    a.add_argument('kind')
    a.add_argument('out')
    a.add_argument('--variant')
    a.add_argument('--dur', type=float)
    a.add_argument('--seed', type=int, default=0)
    a.add_argument('--param', action='append', default=[])
    b = sub.add_parser('mix')
    b.add_argument('spec')
    b.add_argument('total_s', type=float)
    b.add_argument('out')
    c = sub.add_parser('demo')
    c.add_argument('out_dir')
    d = sub.add_parser('encode')
    d.add_argument('wav')
    d.add_argument('out')
    d.add_argument('--codec', default='aac')
    d.add_argument('--bitrate', default='320k')
    d.add_argument('--tp', type=float, default=-1.0)
    d.add_argument('--lufs', type=float)
    args = ap.parse_args()
    if args.cmd == 'list':
        for k, K in KINDS.items():
            print(f"{k:15s} {K['doc']}")
            for v, s in K['variants'].items():
                print(f"   {v:15s} dur={s.get('dur')} normal_lu={NORMAL_LU.get((k, v), s.get('rel_lu'))} "
                      f"card_rel_lu={s.get('rel_lu')} {'(processes the music)' if s.get('music') else ''}")
        print('levels:', LEVELS, ' styles:', ', '.join(STYLES))
        print('aliases:', ', '.join(f'{a}->{k}/{v}' for a, (k, v) in ALIASES.items()))
    elif args.cmd == 'synth':
        P = {}
        for kv in args.param:
            k, v = kv.split('=', 1)
            try:
                P[k] = json.loads(v)
            except ValueError:
                P[k] = v
        y, meta = synth_ex(args.kind, args.variant, SR, args.dur, args.seed, **P)
        _write_wav(args.out, y, SR)
        print(json.dumps({k: v for k, v in meta.items() if isinstance(v, (int, float, str))}))
    elif args.cmd == 'mix':
        spec = json.load(open(args.spec))
        spec = spec.get('audio', spec)
        r = mix(spec, args.total_s, args.out)
        print(json.dumps({k: r[k] for k in ('lufs', 'tp', 'sfx_count', 'gain_db', 'gr_max_db', 'warnings')}))
    elif args.cmd == 'demo':
        print(json.dumps(demo(args.out_dir), indent=1))
    elif args.cmd == 'encode':
        print(json.dumps(encode_audio(args.wav, args.out, args.codec, args.bitrate, args.tp, args.lufs)))
    else:
        ap.print_help()


if __name__ == '__main__':
    main()
