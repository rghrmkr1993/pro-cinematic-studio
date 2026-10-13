#!/usr/bin/env python3
"""QA after a render. The engine cannot watch or listen, so it measures the file it wrote and reports.

  python3 -I ed_qa.py EDL.json RENDER.mp4 OUT_DIR [--no-faces] [--no-source] [--quiet]
  run(edl_path, video_path, out_dir, faces=True, source_check=True, sheets=True) -> dict   (also OUT_DIR/qa.json)

Input: an EDL (TIMELINE.md). An old ed_plan timeline ({"clips": [...]}) is converted on the fly. Thresholds come from
the EDL `qa` block (TIMELINE.md §6); missing keys fall back to the genre card (genres/<slug>.md: `kind`,
`on_beat_share`, `qa_reading_speed(max_cps=..)`, `qa_visual_change(max_gap=..)`) and then to the defaults below.
Source time of every frame = ed_edl.seg_time (the renderer's own mapping: times | speed_curve integral | speed).
Optional inputs next to the render: <render>.render.json (transition windows as rendered, the preview label's box, the
mixer's and the encoder's audio numbers) and <render without extension>.boxes.json (layer boxes; "Renderer sidecars").
Preview labels (ed_edl --labels: clip number, timecode, segment, moves) are scrubbed before any picture measurement:
exactly the sidecar's label_box (each column takes the picture row below it), else a yellow-label heuristic.

PARTS. Composite edits are split into parts: meta.parts [{"id", "type", "f0", "f1", ...}] (ed_sequence; type talk |
speech | interview | podcast = talk, clip = a source fragment (word rules only), anything else, e.g. edit = music;
an edit part's genre / style / variant / engine are reported, its drop_frame is where its drop is checked).
Without meta.parts they are inferred: frames where audio.voice plays from a file that is also a picture source (sync
sound) are talk, the rest music; a speech genre is one talk part; anything else one music part (no composite checks).

GAPS. A storyboard (ed_plan.plan_storyboard: every slot a slate placeholder with an edit-gen brief, meta.gaps items of
kind 'storyboard'; ed_plan.fill_gaps removes the filled ones) is QA'd as an animatic: the slots still to fill come first
(verdict line 'GAPS', qa.json gaps / gaps_to_fill / storyboard {slots, to_fill, filled}, qa.md "Gaps to fill" table:
frames, time, need, part / role, shot, subject, camera), and slates are not judged as pictures - boundaries next to a
slate are not judged for visibility ('gap', still planned cuts for the rhythm), slate holds are planned freezes, slate
segments get no image stats, look targets or subject checks. Sound, timing, transitions' flashes and text are checked
as usual. Other planner gaps (missing / stretched / reused / weak shots) are listed as planner_gaps.

Outputs in OUT_DIR:
  qa.json          machine report: status, verdict lines, parts, gaps, checks{...}, files{...}, timing, plus the legacy
                   top-level keys (duration, cuts_on_grid_share, lufs, true_peak, verdict) that edit.py prints
  qa.md            short human summary, verdict lines first (then the gaps to fill, the look across segments)
  qa_cuts_N.jpg    contact sheets: last visible frame before | cut frame | next frame, for every EDL boundary and every
                   unexpected cut; the cut frame is framed by status (green exact, blue hidden / transition, grey
                   invisible by design / slate, red off-frame, orange missing / flash frame / soft transition rendered
                   hard, magenta unexpected)
  qa_issues.jpg    annotated frames for the flagged problems (safe zone, faces, subject loss, black, frozen, flashes,
                   talk framing: the render next to what the EDL's crop of the source should show)
  qa_rhythm.png    cuts against the beat/half-beat grid (music parts) and word spans (talk parts)
  qa_loudness.png  momentary and short-term loudness vs the target band, true peak per 100 ms, cut markers

Checks (each one: ok | warn | fail | skipped)
  1 format     decoded frame count, duration, fps, size and aspect vs the EDL (n_frames, canvas, preview scale)
  2 cuts       two signals between consecutive frames, both medians over ~9x16 cells of (1 - NCC)/2: raw, and
               motion-compensated (min over the zero shift and the strongest phase-correlation shifts: pans and shakes
               drop to ~0, cuts stay high). Invert ops are undone, opaque op frames (white/black/flash, a >= 0.5)
               bridged. Every segment boundary must show its cut on frame f0, as a clear step over the within-shot
               change on both sides in either signal: exact | masked (hidden under an op frame, consistent) | offset
               (cut 1-4 frames off: renderer timing bug, fail) | soft (continuous source and same framing, invisible
               by design) | flash_frame (two picture changes one frame apart at the boundary: a single-frame shot,
               e.g. the source's own camera cut one frame off the planned reframe; warn, with the fix when the
               boundary is in qa.source_cuts) | accent (no clear step, but the EDL makes the cut visible by
               construction: a crop scale change >= x1.08 across it or a zoom.punch >= 1.08 / a shake firing on the
               cut frame - a wide, dark shot can hide a punch from the pixel signals) | missing | gap (next to a
               storyboard slate, not judged). Transitions
               are judged inside their window (laid out like the renderer, or read from render.json): the pictures
               before and after it must differ (else transition_weak / soft); soft kinds (dissolve, dip, fade, wipe,
               luma, liquid, push, slide) must blend gradually - one textured frame pair carrying a cut-sized step =
               'hard' (warn: rendered as a hard cut); hard kinds (flash, whip, zoom, spin, lens, glitch, pixel_sort,
               light_leak, datamosh) switch on one frame: frames inside the window are classified as the outgoing or
               incoming picture (flat white / black frames skipped) and the switch range must contain f0 (3+ frames
               off = 'offset', fail). Isolated steps away from boundaries and planned look changes (grades, fx frames,
               ghosts, partial ops, text) are unexpected cuts; each is verified on the source (consecutive source
               frames between the two shown times): a shot change there stays an unexpected cut with its exact source
               time and the in/out-point fix, a continuous source (speed ramps, camera fx) moves it to look_changes.
    rhythm     cut events: detected cut frames; a transition counts at its boundary frame f0 (the seam / the start
               of the blend), its detected switch when off; a 'gap' boundary at its EDL frame. Music parts: share of
               cuts within ±qa.grid_tol_frames of the beat/half-beat grid vs qa.on_beat_share; the grid comes from
               the rendered audio, or - when the mix carries a voice or the edit has talk parts - from the music file
               placed on the timeline (whole file analysed, mapped through in / at / speed). Talk parts (and speech
               genres): share of cuts not inside a word (qa.words) vs qa.on_word_share (default 1.0 = none inside a
               word); the source's own camera cuts (qa.source_cuts, ±1 frame) are not editorial cuts and are left out
               (reported as source_cuts_exempt).
  3 loudness   measured on the MP4 itself (ffmpeg ebur128 after the AAC encode, never the mixer's WAV): integrated
               LUFS within qa.lufs ± qa.lufs_tol, true peak <= qa.tp_max. The renderer's own numbers are reported next
               to it: the delivered AAC (render.json audio.encode {lufs, tp}; the mix WAV's audio {lufs, tp} for older
               renders) with the deltas, and a note when the MP4 is more than 0.5 LU / dB off them (audio replaced or
               re-encoded after the render); music_sync = lag of the music bed in the mix against its EDL position.
  4 frames     black = >= 98 % of pixels at luma <= 0.08, white = >= 98 % at >= 0.92, frozen = a hold of identical
               frames >= qa.freeze_min_s (0.3 s). Exempt: qa.planned_black / planned_white / planned_freeze, frames
               covered by ops or transition windows, segments whose source time does not advance (speed 0, times),
               storyboard slates; a hold whose source frames are themselves static (median step < 0.6 levels) is the
               footage ('static source shot'), not a renderer freeze. Slow motion below 0.4x from a source of <= 30 fps
               (speed / speed_curve / times; the synthesized frames show - the cards' rule, the planner's slow floor)
               = warn, unless the edit accepts deep interpolated slow motion (qa.interp, meta.interp).
  5 flashes    WCAG-style general flashes (relative luminance change >= 10 % on >= 25 % of the frame, darker state
               < 0.8, pairs of opposing transitions) and red flashes, counted in every 1 s window; fail above
               qa.flash_limit_hz (red: qa.red_flash_limit_hz, default the same). Worst window reported.
  6 safe zone  ink boxes of every text item rasterised with the renderer's own TextLayer (texts), ed_text.render_layer
               (layers) or read from the renderer's boxes sidecar; checked against qa.safe_zone ('tiktok' = x
               0.06-0.88, y 0.12-0.80 of the canvas; or {"x0", "x1", "y0", "y1"} fractions). Not text placement, so
               not checked: full-frame boxes (backgrounds, inverted / flashed frames, opaque cards), frame ops, items
               hidden by a post-stage opaque op; an edge-to-edge band is checked on its other axis only.
  7 faces      YuNet on rendered frames: faces cut by the frame edge, text over faces. Source side: the main face of
               the source frame vs the crop window of the segment (subject cut or lost by the crop; not on slates).
  8 image      per segment: luma mean/p1/p50/p99 (0-255), crushed shadows / clipped highlights %, HSV saturation
               mean/p95 (0-1), mono flag. Optional ranges in qa.color, e.g. {"p1": [4, 10], "sat_mean": [0, .35]},
               judged with a measurement tolerance (_COLOR_TOL: 5 luma levels, 0.03 saturation, 1 % clipping);
               segments wholly under ops ('covered') and storyboard slates ('gap') are not judged; fx.letterbox bars
               (geometry from the segment's letterbox fx at each measured frame: ratio keys, t / t_keys, ease,
               anchor) are left out - only the picture area between them is measured. Brightness jumps: at every
               hard cut inside a music part (not part boundaries, not transitions) the mean luma of the last / first 6
               clean frames of the two shots (picture area) may change by at most 20 % (and >= 6 levels) - warn.
 10 speech     when there are words, talk parts, audio.voice or a speech genre (talk parts; else the whole edit).
               The voice is measured on its audio (voice_activity: 20 ms RMS every 10 ms of the verified voice stem,
               else the audio.voice clips placed on the timeline, else the mix when it holds only the voice; active =
               louder than max(noise floor + 8 dB, speech level - 26 dB), gaps < 60 ms filled, blips < 40 ms dropped):
               first word of every talk part (voice onset; the words name it) <= qa.first_word_max after its start
               (and the part must not start inside a word); pauses = silences of the voice > qa.max_pause inside a
               talk part: containing a jump cut (the source jumps) = warn unless inside qa.allowed_pauses, across a
               camera change with a continuous source = a reaction by design (reported), inside shots = warn beyond
               qa.planned_pauses where the edit shortens pauses (speech genres; declared talk parts only with
               tighten_pauses) (no voice-only signal: the gaps between qa.words instead);
               caption chunks AS DISPLAYED (layers of kind subtitle / karaoke / caption through
               ed_text.split_caption_layer: reflowed up to the layer's max_lines, a chunk that still does not fit
               split in time - each part judged on its own; an unsplit single chunk's span from the boxes sidecar):
               characters / s <= qa.max_cps, on screen >= qa.min_sub_s, lines <= the layer's max_lines (preset;
               subtitle 3, karaoke 2) or qa.max_sub_lines when set; longest stretch
               of a talk part without a visual change (planned cut or reframe; a boundary with a continuous source
               time that still shows a camera change - a visible step or qa.source_cuts; a shot change of the source
               inside a segment; non-subtitle graphic; camera-fx event) <= qa.max_static_s; clicks at audio seams
               (cuts where a voice entry starts / ends or the source jumps): 2 ms RMS of the > 3 kHz signal within
               ±5 ms over the 90th percentile of ±150 ms, > qa.click_db = warn; voice over music during speech
               (stems), warn below qa.voice_over_music_db when set; lip sync of every talk part measured on the render
               itself (ed_sequence.estimate_av_offset: mouth motion vs the speech envelope) - the audio lagging the
               picture by more than 2 frames (confident estimate) = warn (fix: the part's av_offset).
 11 parts      composite edits: declared parts tile the timeline, every part boundary is a segment boundary and a
               visible cut; into a music part the strongest downbeat / drop of the placed music within ±2 bars
               (sustained energy jump, full band + low end, on the music file's downbeats) must land on the boundary
               ±qa.drop_tol_frames (no clear drop: the nearest downbeat must) - or on the part's meta.parts drop_frame
               when the sequence put its drop elsewhere; qa.drop_f / qa.drop_at checks any other frame the same way.
               Talk framing (talk sources of talk parts, 1-4 samples per segment): the render must match the EDL's
               crop of the source frame (fidelity = cell NCC of render vs expected, > 0.30 = render mismatch:
               garbled / shifted / wrong-time picture; fail in >= 2 samples or 20 %), the speaker's face must be fully
               inside the crop window and found in the render where the crop puts it (share < 0.75 fail, < 1 warn; a
               face turned away or covered while a person fills the window - person segmentation - is reported as
               face_hidden, not flagged). Static overlays (ed_video.static_overlays: logo, lower third, UI, also
               graphics on screen for part of the range; plus sources[..].overlays) must stay outside the crop
               windows of every talk frame while they are on screen - only frames whose source time lies inside the
               overlay's spans count (no spans: overlays with coverage < 0.5 are ignored) - (>= 25 % of an overlay
               visible = fail, less = warn; the declared corner `logo` is inpainted by the renderer).
 12 sfx        audibility of every audio.sfx event on the rendered soundtrack, by ONE rule shared with the mixer
               (ed_sfx.QA_MIN_LU / qa_event_need / audibility; QA calls them, a built-in copy is the fallback); every
               event is placed where the mixer places it (ed_sfx.event_anchor: "at" + offset_ms; a range "t": [t0, t1]
               lands on t1 for peak / end aligned builds - whooshes, risers, reverse sounds - else on t0); events
               whose anchors lie within 150 ms form a group; SFX loudness = the group's loudest 400 ms (window centres
               every 25 ms over the members' spans) of the SFX bus as heard (after the master gain and the limiter);
               reference = the 3 s short-term loudness of the program without SFX (music + voice, after every duck and
               dip) after the group when it holds an impact / sub drop / click / glitch, centred on it otherwise. Need
               = QA_MIN_LU[family] at the normal preset (impact +3 LU, whoosh / reverse whoosh 0, riser 0) + the level
               preset (light -5, strong +4) + the event's gain_db, the strictest member's; auto-level whoosh / riser /
               swell / glitch / click groups under a voice need 6 LU less; not judged: sub drops, swells, glitches,
               clicks, samples without a kind, explicit "lu" events, music-processing kinds; weak = more than QA_TOL
               (1 LU) under the need. The arrays: QA re-runs ed_sfx.mix on the same audio block with debug stems (the
               mix is deterministic) and accepts them only when stems x limiter match the MP4 (corr >= 0.95, or
               >= 0.95 outside the sfx spans when only the sfx differ); per group the re-mix must also match the MP4 in
               the event's span (residual < -12 dB of the sfx, < 12 kHz),
               else the group is measured on the MP4 minus the music / voice stems (an upper bound: weak there =
               weak, loud enough there = 'unverified', typically a render made by another mixer version). The mixer's
               own claims (render.json audio.audibility rel_lu / need_lu / ok, audio.events st_lu) are attached per
               group (more than 1 LU apart = mixer_disagrees), and floor_db - the dB the mixer's audibility floor
               added above the level rules (render.json audio.events, else QA's own re-mix records): a weak group
               says how far the floor already lifted it (floor_lifted lists them all). No stems: skipped
               (mix_jump_lu reported).
  9 sheets     contact sheets and plots (files above).

qa keys (all optional; TIMELINE.md §6):
  genre, kind ('speech' | 'music'), words (list or JSON path; OUTPUT-time word timestamps {w, t0, t1})
  on_beat_share (card, 0.85), on_word_share (speech: 1.0), grid_tol_frames (1)
  source_cuts (output frames, or {"f"} / {"t": s} items: the source's own camera cuts, not judged against the words,
               counted as visual changes)
  lufs (-14), lufs_tol (1), tp_max (-1)
  planned_black / planned_white (frames or 'a:b' / [a, b] ranges), planned_freeze ([[a, b]]), freeze_min_s (0.3),
  black_luma (0.08), white_luma (0.92), frame_ratio (0.98)
  flash_limit_hz (3), red_flash_limit_hz (= flash_limit_hz), flash_area (0.25), flash_delta (0.10)
  safe_zone ('tiktok' | 'title_safe' | 'none' | {x0, x1, y0, y1}), color ({stat: [lo, hi]} per segment)
  first_word_max (0.3 s), max_pause (0.35 s), allowed_pauses ([[t0, t1]] output s: a pause whose span, centre or jump
  cut lies inside one is by design), planned_pauses (2), max_cps (card or 20), min_sub_s (0.7), max_sub_lines (the
  caption layer's own max_lines),
  max_static_s (card or 4.0), click_db (6.0), voice_over_music_db (none: reported only)
  interp (false): deep interpolated slow motion accepted (no warning for < 0.4x from <= 30 fps sources)
  drop_tol_frames (1.0), drop_f (frame) / drop_at (output s): where the strongest drop of the music must land
  sfx_min_lu ({"impact": 3, "whoosh": 0, "riser": 0} at the normal preset, or {"light": {"impact": -2}, ...}: replaces
               the mixer's QA_MIN_LU / qa_event_need for this edit)
  parts ([{"id", "on_beat_share" | "on_word_share"}]: per-part rhythm thresholds, the strictest of each kind applies)
  Planner keys QA does not read (cuts, shot_len_s, max_shot_s, genre_checks, speech, ...) are ignored.

Renderer sidecars (optional): <render>.render.json (ed_edl report: "transitions" [{a, b, w0, w1}], "labels" /
  "label_box" [x0, y0, x1, y1] canvas px, "audio" {lufs, tp (mix WAV), encode {lufs, tp, ...} (delivered AAC), events
  [{i, kind, at, start, end, level, need_lu, st_lu, floor_db, ...}], audibility [{t, events, need_lu, rel_lu, ok}]},
  "edl_md5": transitions and audio events are ignored when the EDL changed since the render) and <render without
  extension>.boxes.json = {"canvas": [w, h], "frames": {"<f>": [[x0, y0, x1, y1, "<id>", ("<kind>"), ("opaque" | "full"
  | "op")...] | {"box", "id", "kind", "opaque", "full", "op"}, ...]}}  (canvas px), used for layers when present.
"""
import os, sys, json, math, re, time, argparse, subprocess, glob
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ed_video as V  # noqa: E402

try:
    import ed_edl as E  # renderer: TextLayer, crop_state, window (same geometry as the render)
except Exception as _e:  # pragma: no cover - degraded mode
    E = None
    _EDL_IMPORT_ERROR = repr(_e)

DEFAULTS = dict(on_beat_share=0.85, on_word_share=None, flash_limit_hz=3.0, red_flash_limit_hz=None, flash_area=0.25,
                flash_delta=0.10, safe_zone='tiktok', lufs=-14.0, lufs_tol=1.0, tp_max=-1.0, freeze_min_s=0.3,
                grid_tol_frames=1.0, black_luma=0.08, white_luma=0.92, frame_ratio=0.98)
SAFE_ZONES = {'tiktok': dict(x0=0.06, x1=0.88, y0=0.12, y1=0.80),
              'title_safe': dict(x0=0.05, x1=0.95, y0=0.05, y1=0.95)}
OPAQUE_A = 0.5            # op opacity from which the frame content is treated as hidden
ANALYSIS_LONG = 320       # analysis frames: long side in px (540x960 -> 180x320)
DECODE_MAX_W = 540        # decode width cap (faces / tiles); finals are decoded downscaled
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
if not os.path.exists(FONT):                       # no system DejaVu: bundled OFL mono
    FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts', 'jetbrainsmono_JetBrainsMono-VF.ttf')
LEVELS = {'ok': 0, 'skipped': 0, 'warn': 1, 'fail': 2}
# boundary statuses that show a picture change
VISIBLE_CUTS = ('exact', 'masked', 'offset', 'transition', 'hard', 'flash_frame', 'accent')


# ============================================================================ small helpers
def frange(spec):
    """int -> [int]; 'a:b' -> a..b inclusive; list of ints / 'a:b' strings -> flattened (as ed_edl.frange)."""
    if spec is None:
        return []
    if isinstance(spec, (bool, np.bool_)):
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


def frame_set(spec):
    """qa.planned_* lists: ints, 'a:b' strings or [a, b] ranges (inclusive)."""
    out = set()
    for v in spec or []:
        if isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
            out.update(range(int(v[0]), int(v[1]) + 1))
        else:
            out.update(frange(v))
    return out


def runs(mask):
    """Boolean array -> list of (start, end) inclusive index ranges where it is True."""
    m = np.asarray(mask, bool)
    if not m.any():
        return []
    d = np.diff(np.concatenate([[0], m.astype(np.int8), [0]]))
    return list(zip(np.where(d == 1)[0].tolist(), (np.where(d == -1)[0] - 1).tolist()))


def r(x, nd=3):
    if x is None:
        return None
    try:
        if not np.isfinite(x):
            return None
    except TypeError:
        return x
    return round(float(x), nd)


def check(status, **kw):
    kw['status'] = status
    return kw


# transition kinds (ed_fx.TRANSITIONS + aliases): 'soft' kinds blend gradually over their window, 'hard' kinds switch
# pictures on one frame inside it (the seam = the boundary frame f0), usually hidden under a flash, blur or warp
_TR_ALIAS = {'leak': 'light_leak', 'iris': 'wipe', 'cross': 'dissolve', 'crossfade': 'dissolve', 'mix': 'dissolve',
             'lens_distort': 'lens', 'burn': 'liquid', 'melt': 'liquid', 'blob': 'liquid', 'mosh': 'datamosh',
             'swish': 'whip', 'whip_pan': 'whip', 'roll': 'spin', 'pixelsort': 'pixel_sort'}
HARD_TRANSITIONS = {'flash', 'whip', 'zoom', 'spin', 'lens', 'glitch', 'pixel_sort', 'light_leak', 'datamosh'}


def transition_class(kind):
    """'hard' (flash, whip, zoom, spin, lens, glitch, pixel_sort, light_leak, datamosh: one switch frame inside the
    window) or 'soft' (dissolve, dip, fade, wipe, luma, liquid, push, slide and unknown kinds, which the renderer
    dissolves)."""
    base = str(kind or 'dissolve').split('(')[0].strip().lower()
    base = base[6:] if base.startswith('trans.') else base
    return 'hard' if _TR_ALIAS.get(base, base) in HARD_TRANSITIONS else 'soft'


# ============================================================================ EDL loading / config
def timeline_to_edl(tl):
    """Old ed_plan timeline ({"clips": [{n, src, src_in, t0, t1, speed, cut_in}]}) -> minimal EDL."""
    fps = tl['canvas']['fps']
    clips = sorted(tl['clips'], key=lambda c: c['t0'])
    total = int(round(clips[-1]['t1'] * fps))
    segs, ops, sources = [], [], {}
    for i, c in enumerate(clips):
        f0, f1 = int(round(c['t0'] * fps)), int(round(c['t1'] * fps)) - 1
        if i == len(clips) - 1:
            f1 = total - 1
        src = c.get('src') or tl.get('source') or 'src'
        key = os.path.basename(src)
        sources.setdefault(key, {'path': src})
        segs.append(dict(id=f"#{c.get('n', i + 1)}", f0=f0, f1=f1, src=key, t=float(c.get('src_in', 0.0)),
                         speed=float(c.get('speed', 1.0))))
        cut = c.get('cut_in') or {}
        if cut.get('id') == 'trans.flash':          # ed_render: white over the first frames, a = .92 .55 .25 .1
            for k in range(min(cut.get('frames', 3), f1 - f0 + 1)):
                ops.append({'f': [f0 + k], 'op': 'white', 'a': [0.92, 0.55, 0.25, 0.1][min(k, 3)]})
        elif cut.get('id') == 'trans.fade':         # dip from black, a = 1 - k / frames
            nfr = cut.get('frames', 8)
            for k in range(min(nfr, f1 - f0 + 1)):
                ops.append({'f': [f0 + k], 'op': 'black', 'a': round(1 - k / nfr, 3)})
    return dict(canvas=tl['canvas'], n_frames=total, segments=segs, ops=ops, texts=[], layers=[], sources=sources,
                audio=tl.get('audio'), qa=tl.get('qa') or {}, meta={'genre': tl.get('genre'), 'format': 'timeline',
                                                                      'crop_model': 'ed_render'})


def load_edl(path):
    d = json.load(open(path))
    if 'segments' in d:
        return d, 'edl'
    if 'clips' in d:
        return timeline_to_edl(d), 'timeline'
    raise ValueError(f'{path}: neither an EDL (segments) nor a timeline (clips)')


_CARDS = None


def genre_cards():
    global _CARDS
    if _CARDS is None:
        _CARDS = []
        for p in sorted(glob.glob(os.path.join(HERE, '..', 'genres', '*.md'))):
            try:
                txt = open(p, encoding='utf-8').read()
            except OSError:
                continue
            if not txt.startswith('---'):
                continue
            fm = txt.split('---', 2)[1]
            card = {'file': os.path.basename(p)}
            for key in ('genre', 'slug', 'kind', 'on_beat_share'):
                m = re.search(rf'^\s*{key}:\s*([^#\n]+)', fm, re.M)
                if m:
                    card[key] = m.group(1).strip().strip('"\'')
            _CARDS.append(card)
    return _CARDS


def genre_card(genre):
    if not genre:
        return {}
    g = str(genre).strip().lower()
    for c in genre_cards():
        if g in {c.get('slug', '').lower(), c.get('genre', '').lower(), c['file'][:-3].lower()}:
            out = dict(c)
            k = c.get('kind', '').lower()
            out['kind'] = 'speech' if k.startswith('speech') else 'music'
            try:
                out['on_beat_share'] = float(c['on_beat_share']) if 'on_beat_share' in c else None
            except ValueError:
                out['on_beat_share'] = None
            return out
    return {}


def qa_config(edl, edl_dir):
    qa = edl.get('qa') or {}
    meta = edl.get('meta') or {}
    q = dict(DEFAULTS)
    genre = qa.get('genre') or meta.get('genre')
    card = genre_card(genre)
    if card.get('on_beat_share') is not None:
        q['on_beat_share'] = card['on_beat_share']
    q.update({k: v for k, v in qa.items() if v is not None})
    kind = qa.get('kind') or card.get('kind') or 'music'
    q['mode'] = 'speech' if (qa.get('on_word_share') is not None or kind == 'speech') else 'music'
    if q['mode'] == 'speech' and q.get('on_word_share') is None:
        q['on_word_share'] = 1.0                   # speech cards: cuts inside words = 0
    q['genre'], q['genre_card'] = genre, card.get('file')
    if q.get('red_flash_limit_hz') is None:
        q['red_flash_limit_hz'] = q['flash_limit_hz']
    words = qa.get('words')
    if isinstance(words, str):
        p = words if os.path.isabs(words) else os.path.join(edl_dir, words)
        try:
            words = json.load(open(p))
        except (OSError, ValueError):
            words = None
    if isinstance(words, dict):
        words = words.get('words')
    q['words'] = [w for w in (words or []) if 't0' in w and 't1' in w]
    return q


# ============================================================================ what the EDL says about every frame
def _rate_integral(curve, k):
    """Integral over [0, k] (output frames) of a piecewise-linear rate [[k, rate], ...], flat outside its keys
    (the renderer's ed_edl.rate_integral, copied for the degraded mode)."""
    pts = sorted((float(p[0]), float(p[1])) for p in curve)

    def G(x):
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
    return G(float(k)) - G(0.0)


def seg_time(sg, k, fps):
    """Source time (s) the renderer shows on segment frame k: ed_edl.seg_time (times | speed_curve integral | speed),
    or the same mapping computed locally when ed_edl is not importable."""
    if E is not None and hasattr(E, 'seg_time'):
        try:
            return float(E.seg_time(sg, k, fps))
        except Exception:  # malformed segment: fall through to the local copy
            pass
    ts = sg.get('times')
    if ts:
        n, sp = len(ts), float(sg.get('speed', 1.0))
        if 0 <= k <= n - 1:
            return float(np.interp(k, np.arange(n), np.asarray(ts, float)))
        return float(ts[0]) + k * sp / fps if k < 0 else float(ts[-1]) + (k - (n - 1)) * sp / fps
    t0 = float(sg.get('t', 0.0))
    if sg.get('speed_curve'):
        return t0 + _rate_integral(sg['speed_curve'], k) / fps
    return t0 + k / fps * float(sg.get('speed', 1.0))


def seg_times(sg, fps):
    """Source time shown on each frame of a segment (seg_time for k = 0 .. n-1)."""
    n = int(sg['f1']) - int(sg['f0']) + 1
    return [seg_time(sg, k, fps) for k in range(n)]


def crop_at(sg, k):
    n = int(sg['f1']) - int(sg['f0']) + 1
    if E is not None:
        try:
            return E.crop_state(sg, k, n)
        except Exception:
            pass
    c = dict(cx=0.5, cy=0.5, z=1.0)
    c.update({kk: v for kk, v in (sg.get('crop') or {}).items() if kk in c})
    return c


class Plan:
    """Per-frame facts derived from the EDL: segment index, ops, planned frames, expected look changes, boundaries."""

    def __init__(self, edl, q, n, rendered_windows=None):
        self.edl, self.n = edl, n
        self.rendered_windows = rendered_windows
        self.fps = fps = float(edl['canvas']['fps'])
        self.segs = segs = edl.get('segments', [])
        self.seg_of = np.full(n, -1, int)
        for si in sorted(range(len(segs)), key=lambda i: segs[i]['f0']):
            sg = segs[si]
            self.seg_of[max(0, sg['f0']):max(0, min(n, sg['f1'] + 1))] = si
        self.opaque = np.zeros(n, bool)
        self.inverted = np.zeros(n, bool)
        self.op_any = np.zeros(n, bool)
        self.op_names = {}
        self.events = {}            # frame -> causes of an expected visual change between f-1 and f
        self.trans_win = np.zeros(n, bool)

        def ev(f, cause):
            if 0 < f < n:
                self.events.setdefault(int(f), set()).add(cause)

        for op in edl.get('ops', []) or []:
            name = op.get('op', '?')
            fl = [f for f in frange(op.get('f')) if 0 <= f < n]
            curve = op.get('curve') or [1.0]
            for i, f in enumerate(fl):
                a = float(op.get('a', 1.0))
                if name == 'flash':
                    a *= float(curve[min(i, len(curve) - 1)])
                self.op_any[f] = True
                self.op_names.setdefault(f, []).append(name)
                if name == 'invert':
                    self.inverted[f] = not self.inverted[f]      # undone before measuring: not a look change
                elif name in ('white', 'black', 'flash') and a >= OPAQUE_A:
                    self.opaque[f] = True                        # bridged over: not a look change either
                else:
                    ev(f, 'op:' + name)                          # partial ops (mask_flash, rect_flash, hud_tc, a < .5)
                    ev(f + 1, 'op:' + name)
        self.planned_black = {f for f in frame_set(q.get('planned_black')) if 0 <= f < n}
        self.planned_white = {f for f in frame_set(q.get('planned_white')) if 0 <= f < n}
        self.planned_freeze = {f for f in frame_set(q.get('planned_freeze')) if 0 <= f < n}
        self.derived_freeze = set()
        for sg in segs:
            f0, f1 = int(sg['f0']), int(sg['f1'])
            ts = seg_times(sg, fps)
            for k in range(1, len(ts)):
                if abs(ts[k] - ts[k - 1]) < 1e-6:
                    self.derived_freeze.update({f0 + k - 1, f0 + k})
            for gr in sg.get('grades') or []:
                if gr.get('k0', 0) > 0:
                    ev(f0 + gr['k0'], 'grade')
                if f0 + gr.get('k1', f1 - f0) < f1:
                    ev(f0 + gr.get('k1', f1 - f0) + 1, 'grade')
            for fx in (sg.get('fx') or []) + (sg.get('post_text_fx') or []):
                ks = None
                if fx.get('frames') is not None:
                    ks = set(frange(fx['frames']))         # ints or 'a:b' strings (ed_fx frames gate)
                elif fx.get('t') is not None and len(fx['t']) == 2:
                    ks = set(range(int(round(fx['t'][0] * fps)), int(round(fx['t'][1] * fps)) + 1))
                for k in ks or []:
                    if k - 1 not in ks:
                        ev(f0 + k, 'fx:' + str(fx.get('type')))
                    if k + 1 not in ks:
                        ev(f0 + k + 1, 'fx:' + str(fx.get('type')))
            for gh in sg.get('ghosts') or []:
                fl = set(frange(gh.get('frames', [])))
                for f in fl:
                    if f - 1 not in fl:
                        ev(f, 'ghost')
                    if f + 1 not in fl:
                        ev(f + 1, 'ghost')
        for tb in edl.get('texts', []) or []:
            ev(tb['f0'], 'text')
            ev(tb['f1'] + 1, 'text')
        for ly in edl.get('layers', []) or []:
            if 'f0' in ly:
                ev(ly['f0'], 'layer')
                ev(ly.get('f1', ly['f0']) + 1, 'layer')
        for a, b in runs(self.seg_of < 0):
            ev(a, 'gap')
            ev(b + 1, 'gap')
        self.boundaries = self._boundaries()

    def _windows(self, rendered=None):
        """transition_in windows {segment index: (w0, w1)} exactly as ed_edl.Renderer._plan_transitions lays them out
        (centre / end alignment, clipped to the previous window, the previous segment and the canvas); the render
        sidecar's own windows win when given (`rendered`: its "transitions" list)."""
        segs, n = self.segs, self.n
        order = sorted(range(len(segs)), key=lambda i: (segs[i]['f0'], i))
        out, last_w1 = {}, -1
        for pos, si in enumerate(order):
            sg = segs[si]
            tr = sg.get('transition_in')
            if not tr or int(tr.get('frames', 6)) <= 0:
                continue
            F, f0 = int(tr.get('frames', 6)), int(sg['f0'])
            w0 = f0 - F // 2 if tr.get('align', 'center') == 'center' else f0
            w1 = w0 + F - 1
            prev = order[pos - 1] if pos > 0 else None
            if prev is not None and int(segs[prev]['f1']) < f0 - 1:
                prev = None
            w0 = max(w0, last_w1 + 1, 0, int(segs[prev]['f0']) if prev is not None else 0)
            w1 = min(w1, int(sg['f1']), n - 1)
            if w1 < w0:
                continue
            out[si] = (w0, w1)
            last_w1 = w1
        if rendered:
            by_id = {str(sg.get('id', i)): i for i, sg in enumerate(segs)}
            for w in rendered:
                si = by_id.get(str(w.get('b')))
                if si is not None and w.get('w0') is not None and w.get('w1') is not None:
                    out[si] = (int(w['w0']), int(w['w1']))
        return out

    def _boundaries(self):
        segs, fps, n = self.segs, self.fps, self.n
        order = sorted(range(len(segs)), key=lambda i: segs[i]['f0'])
        wins = self._windows(self.rendered_windows)
        out = []
        for j in range(1, len(order)):
            p, c = segs[order[j - 1]], segs[order[j]]
            b = int(c['f0'])
            if b <= 0 or b >= n:
                continue
            rec = dict(f=b, prev=p.get('id', str(order[j - 1])), next=c.get('id', str(order[j])), kind='cut',
                       pi=order[j - 1], ci=order[j])
            if b <= int(p['f1']):
                rec['overlap'] = int(p['f1']) - b + 1
            tr = c.get('transition_in')
            if tr and order[j] in wins:
                a, z = wins[order[j]]
                rec.update(kind='transition', transition=tr.get('kind'), window=[a, z], align=tr.get('align', 'center'),
                           tclass=transition_class(tr.get('kind')))
                self.trans_win[a:z + 1] = True
                for f in range(max(1, a), min(n, z + 2)):
                    self.events.setdefault(f, set()).add('transition')
            # continuity: is this boundary visible by design?
            np_ = int(p['f1']) - int(p['f0']) + 1
            t_last = seg_time(p, np_ - 1, fps)
            step = (t_last - seg_time(p, np_ - 2, fps)) if np_ > 1 else float(p.get('speed', 1.0)) / fps
            dt = seg_time(c, 0, fps) - (t_last + step)
            same_src = p.get('src', 'film') == c.get('src', 'film')
            cp, cc = crop_at(p, int(p['f1']) - int(p['f0'])), crop_at(c, 0)
            same_crop = (abs(cp['cx'] - cc['cx']) < 0.04 and abs(cp['cy'] - cc['cy']) < 0.04
                         and abs(math.log(max(cc['z'], 1e-3) / max(cp['z'], 1e-3))) < math.log(1.04)
                         and p.get('border') == c.get('border'))
            same_look = (json.dumps(p.get('grade'), sort_keys=True) == json.dumps(c.get('grade'), sort_keys=True)
                         and [f.get('type') for f in p.get('fx') or []] == [f.get('type') for f in c.get('fx') or []])
            if same_src and abs(dt) < 0.2 and same_crop and same_look:
                rec['continuity'] = 'continuous'
            elif same_src and abs(dt) < 0.5:
                rec['continuity'] = 'reframe'
            else:
                rec['continuity'] = 'new'
            rec['src_jump_s'] = r(dt, 3) if same_src else None
            out.append(rec)
        return out

    def seg_id(self, f):
        si = self.seg_of[f] if 0 <= f < self.n else -1
        return self.segs[si].get('id', str(si)) if si >= 0 else None

    def src_time(self, f):
        si = self.seg_of[f] if 0 <= f < self.n else -1
        if si < 0:
            return None
        sg = self.segs[si]
        return seg_time(sg, f - int(sg['f0']), self.fps)


# ============================================================================ decoding
def analysis_size(w, h):
    if h >= w:
        ah = ANALYSIS_LONG
        aw = max(20, int(round(w * ah / h / 4)) * 4)
    else:
        aw = ANALYSIS_LONG
        ah = max(20, int(round(h * aw / w / 4)) * 4)
    return aw, ah


def decode(video, info, keep, sync=('-fps_mode', 'passthrough')):
    """One pass over the render. Returns small analysis frames (N, ah, aw, 3) uint8, kept full frames
    {f: (dh, dw, 3)}, the per-frame share of yellow label pixels in the top-left corner."""
    W, H = info['w'], info['h']
    dw, dh = (W, H) if W <= DECODE_MAX_W else (DECODE_MAX_W, int(round(H * DECODE_MAX_W / W / 2)) * 2)
    aw, ah = analysis_size(dw, dh)
    cmd = ['ffmpeg', '-v', 'error', '-nostdin', '-i', video, '-map', '0:v:0', '-an', '-sn']
    if (dw, dh) != (W, H):
        cmd += ['-vf', f'scale={dw}:{dh}:flags=area']
    cmd += list(sync) + ['-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    size = dw * dh * 3
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=size * 2)
    small, full, label = [], {}, []
    lh, lw = max(4, int(round(dh * 22 / 960))), max(8, int(dw * 0.5))
    try:
        while True:
            buf = p.stdout.read(size)
            if len(buf) < size:
                break
            fr = np.frombuffer(buf, np.uint8).reshape(dh, dw, 3)
            i = len(small)
            small.append(cv2.resize(fr, (aw, ah), interpolation=cv2.INTER_AREA))
            reg = fr[:lh, :lw]
            label.append(float(((reg[..., 0] > 200) & (reg[..., 1] > 170) & (reg[..., 2] < 90)).mean()))
            if i in keep:
                full[i] = fr.copy()
    finally:
        p.stdout.close()
        p.wait()
    if not small and sync[0] == '-fps_mode':                 # ffmpeg < 5.1 has no -fps_mode
        return decode(video, info, keep, sync=('-vsync', '0'))
    return (np.stack(small) if small else np.zeros((0, ah, aw, 3), np.uint8)), full, np.array(label), (dw, dh)


def label_region(side):
    """The burnt-in preview label's extent from the render sidecar: label_box [x0, y0, x1, y1] in canvas px when the
    render has labels, False when the sidecar says it has none, None when unknown (no sidecar / older renderer)."""
    if not isinstance(side, dict) or 'labels' not in side:
        return None
    lb = side.get('label_box')
    if not side.get('labels'):
        return False
    if isinstance(lb, (list, tuple)) and len(lb) == 4 and all(isinstance(v, (int, float)) for v in lb):
        return [float(v) for v in lb]
    return None


def _scrub(frames, x0, y0, x1, y1):
    """Each column of the region takes the pixel row just below it (or above it at the bottom edge): the region then
    follows the picture instead of becoming a constant block that would read as black, frozen or a flat cell."""
    h = frames.shape[-3]
    if y1 < h:
        frames[..., y0:y1, x0:x1, :] = frames[..., y1:y1 + 1, x0:x1, :]
    elif y0 > 0:
        frames[..., y0:y1, x0:x1, :] = frames[..., y0 - 1:y0, x0:x1, :]


def scrub_label(small, label_frac, box=None, canvas=None, full=None):
    """Preview renders carry a burnt-in label (ed_edl --labels: clip number, timecode, segment, moves) in the top-left
    corner; its timecode changes every frame and its clip number at every cut, so it must not count as picture (cuts,
    freeze, black, flashes, image stats, faces). box = the sidecar's label_box (canvas px, see label_region): exactly
    that region (+1 px) is scrubbed in the analysis frames and in the kept full frames; box False = no label; box None
    = the older heuristic (yellow label pixels in the top-left strip on most frames). -> region in analysis px | None."""
    n, ah, aw, _ = small.shape
    if box is False:
        return None
    if box is not None and canvas and canvas.get('w') and canvas.get('h'):
        def to(fw, fh):
            sx, sy = fw / float(canvas['w']), fh / float(canvas['h'])
            return (max(0, int(math.floor(box[0] * sx)) - 1), max(0, int(math.floor(box[1] * sy)) - 1),
                    min(fw, int(math.ceil(box[2] * sx)) + 1), min(fh, int(math.ceil(box[3] * sy)) + 1))
        x0, y0, x1, y1 = to(aw, ah)
        if x1 <= x0 or y1 <= y0 or (x1 - x0) * (y1 - y0) > 0.25 * aw * ah:
            return None                                  # degenerate or implausibly large: leave the frames alone
        _scrub(small, x0, y0, x1, y1)
        for f, fr in (full or {}).items():
            fh, fw = fr.shape[:2]
            _scrub(fr, *to(fw, fh))
        return [x0, y0, x1, y1]
    if len(label_frac) == 0 or np.mean(label_frac > 0.004) < 0.5:
        return None
    hh = max(2, int(math.ceil(ah * 22 / 960)) + 1)
    ww = int(aw * 0.5)
    small[:, :hh, :ww] = small[:, hh:hh + 1, :ww]
    return [0, 0, ww, hh]


# ============================================================================ 2 cuts
def _cell_d(a, b, cs):
    """Median over cs x cs cells of (1 - NCC)/2 for textured cells, else the mean change / 40 (0..1)."""
    h, w = a.shape
    ny, nx = h // cs, w // cs
    if ny < 2 or nx < 2:
        return 1.0
    A = a[:ny * cs, :nx * cs].reshape(ny, cs, nx, cs).transpose(0, 2, 1, 3).reshape(ny, nx, -1)
    B = b[:ny * cs, :nx * cs].reshape(ny, cs, nx, cs).transpose(0, 2, 1, 3).reshape(ny, nx, -1)
    ma, mb, sa, sb = A.mean(-1), B.mean(-1), A.std(-1), B.std(-1)
    ncc = ((A - ma[..., None]) * (B - mb[..., None])).mean(-1) / (sa * sb + 1e-6)
    tex = (sa > 3) & (sb > 3)
    return float(np.median(np.where(tex, (1 - ncc) / 2, np.minimum(1.0, np.abs(ma - mb) / 40.0))))


def _cell_d_tex(a, b, cs, thr=3.0):
    """(median of (1 - NCC)/2 over cs x cs cells textured in both frames, share of such cells); (nan, share) when
    fewer than 6 cells qualify."""
    h, w = a.shape
    ny, nx = h // cs, w // cs
    if ny < 2 or nx < 2:
        return float('nan'), 0.0
    A = a[:ny * cs, :nx * cs].reshape(ny, cs, nx, cs).transpose(0, 2, 1, 3).reshape(ny, nx, -1)
    B = b[:ny * cs, :nx * cs].reshape(ny, cs, nx, cs).transpose(0, 2, 1, 3).reshape(ny, nx, -1)
    ma, mb, sa, sb = A.mean(-1), B.mean(-1), A.std(-1), B.std(-1)
    tex = (sa > thr) & (sb > thr)
    share = float(tex.mean())
    if tex.sum() < 6:
        return float('nan'), share
    ncc = ((A - ma[..., None]) * (B - mb[..., None])).mean(-1) / (sa * sb + 1e-6)
    return float(np.median(((1 - ncc) / 2)[tex])), share


class CutSignal:
    """Two dissimilarities between frames, both medians over a ~9x16 grid of cells of (1 - NCC)/2 (gain/offset
    invariant, so partial exposure flashes do not read as cuts; flat cells use the mean change):
      raw - frames as they are (catches reframe jumps, sensitive);
      mc  - the minimum over the zero shift and the strongest phase-correlation shifts, so pans and shakes
            drop to ~0 while a cut stays high (nothing aligns unrelated pictures)."""

    def __init__(self, gray, inverted):
        n, ah, aw = gray.shape
        qw, qh = max(10, aw // 4), max(10, ah // 4)
        q = gray[:, :qh * 4, :qw * 4].reshape(n, qh, 4, qw, 4).mean(axis=(2, 4), dtype=np.float32)   # 4x4 block mean
        q[inverted[:n]] = 255.0 - q[inverted[:n]]
        cs = 5
        ny, nx = qh // cs, qw // cs
        q = q[:, :ny * cs, :nx * cs]
        self.c = q.reshape(n, ny, cs, nx, cs).transpose(0, 1, 3, 2, 4).reshape(n, ny, nx, cs * cs)
        self.mu = self.c.mean(-1)
        self.sd = self.c.std(-1)
        hw, hh = aw // 2, ah // 2                    # half-size frames for the motion-compensated signal
        self.h = gray[:, :hh * 2, :hw * 2].reshape(n, hh, 2, hw, 2).mean(axis=(2, 4), dtype=np.float32)
        self.h[inverted[:n]] = 255.0 - self.h[inverted[:n]]
        self.hcs = max(4, min(hh, hw) // 9)
        self.win = np.outer(np.hanning(hh), np.hanning(hw)).astype(np.float32)

    def pair(self, a, b):
        ca, cb = self.c[a] - self.mu[a][..., None], self.c[b] - self.mu[b][..., None]
        ncc = (ca * cb).mean(-1) / (self.sd[a] * self.sd[b] + 1e-6)
        tex = (self.sd[a] > 3) & (self.sd[b] > 3)
        d = np.where(tex, (1 - ncc) / 2, np.minimum(1.0, np.abs(self.mu[a] - self.mu[b]) / 40.0))
        return float(np.median(d))

    def pair_mc(self, a, b, peaks=3, max_frac=0.25):
        A, B = self.h[a], self.h[b]
        H, W = A.shape
        best = _cell_d(A, B, self.hcs)
        if best < 0.02:
            return best
        fa = np.fft.rfft2((A - A.mean()) * self.win)
        fb = np.fft.rfft2((B - B.mean()) * self.win)
        R = fa * np.conj(fb)
        corr = np.fft.irfft2(R / (np.abs(R) + 1e-6), s=(H, W))
        cf = corr.ravel()
        top = np.argpartition(cf, -peaks * 4)[-peaks * 4:]
        flat = top[np.argsort(cf[top])[::-1]]
        tried = set()
        for idx in flat:
            dy, dx = divmod(int(idx), W)
            dy = dy - H if dy > H // 2 else dy
            dx = dx - W if dx > W // 2 else dx
            if (dy, dx) == (0, 0) or abs(dy) > max_frac * H or abs(dx) > max_frac * W:
                continue
            for sy, sx in ((dy, dx), (-dy, -dx)):
                if (sy, sx) in tried:
                    continue
                tried.add((sy, sx))
                a_ = A[max(0, sy):H + min(0, sy), max(0, sx):W + min(0, sx)]
                b_ = B[max(0, -sy):H + min(0, -sy), max(0, -sx):W + min(0, -sx)]
                best = min(best, _cell_d(a_, b_, self.hcs))
            if len(tried) >= 2 * peaks:
                break
        return best

    def pair_tex(self, a, b, peaks=3, max_frac=0.25):
        """(d, share): the median of (1 - NCC)/2 over cells textured in BOTH frames (flat, white or black cells
        say nothing about which picture is shown), minimised over the zero shift and the strongest phase-correlation
        shifts; share = fraction of textured cells (d is nan when too few)."""
        A, B = self.h[a], self.h[b]
        H, W = A.shape
        best, share = _cell_d_tex(A, B, self.hcs)
        if not np.isfinite(best) or best < 0.02:
            return best, share
        fa = np.fft.rfft2((A - A.mean()) * self.win)
        fb = np.fft.rfft2((B - B.mean()) * self.win)
        R = fa * np.conj(fb)
        cf = np.fft.irfft2(R / (np.abs(R) + 1e-6), s=(H, W)).ravel()
        top = np.argpartition(cf, -peaks * 4)[-peaks * 4:]
        tried = set()
        for idx in top[np.argsort(cf[top])[::-1]]:
            dy, dx = divmod(int(idx), W)
            dy = dy - H if dy > H // 2 else dy
            dx = dx - W if dx > W // 2 else dx
            if (dy, dx) == (0, 0) or abs(dy) > max_frac * H or abs(dx) > max_frac * W:
                continue
            for sy, sx in ((dy, dx), (-dy, -dx)):
                if (sy, sx) in tried:
                    continue
                tried.add((sy, sx))
                a_ = A[max(0, sy):H + min(0, sy), max(0, sx):W + min(0, sx)]
                b_ = B[max(0, -sy):H + min(0, -sy), max(0, -sx):W + min(0, -sx)]
                d, _ = _cell_d_tex(a_, b_, self.hcs)
                if np.isfinite(d):
                    best = min(best, d)
            if len(tried) >= 2 * peaks:
                break
        return best, share

    def consecutive(self):
        n = len(self.c)
        D = np.full(n, np.nan)
        for s in range(1, n, 128):                  # chunked, vectorised
            e = min(n, s + 128)
            a, b = self.c[s - 1:e - 1], self.c[s:e]
            ma, mb = self.mu[s - 1:e - 1], self.mu[s:e]
            sa, sb = self.sd[s - 1:e - 1], self.sd[s:e]
            ncc = ((a - ma[..., None]) * (b - mb[..., None])).mean(-1) / (sa * sb + 1e-6)
            tex = (sa > 3) & (sb > 3)
            d = np.where(tex, (1 - ncc) / 2, np.minimum(1.0, np.abs(mb - ma) / 40.0))
            D[s:e] = np.median(d.reshape(e - s, -1), axis=1)
        return D


def analyse_cuts(sig, plan, nv):
    n = min(nv, plan.n)
    src_cuts = source_cut_frames(plan.edl.get('qa') or {}, plan.fps)
    valid = ~plan.opaque[:n]
    raw = sig.consecutive()[:n]
    mc = np.full(n, np.nan)
    bridge = {}
    for f in range(1, n):
        if not valid[f]:
            raw[f] = np.nan
            continue
        p = f - 1
        if not valid[p]:                         # opaque op frames in between: compare across them
            while p >= 0 and not valid[p]:
                p -= 1
            if p < 0:
                raw[f] = np.nan
                continue
            raw[f] = sig.pair(p, f)
            bridge[f] = p
        mc[f] = sig.pair_mc(p, f) if raw[f] >= 0.06 else raw[f]     # small changes need no motion search
    S = {'mc': mc, 'raw': raw}
    near_b = np.zeros(n, bool)
    for rec in plan.boundaries:
        lo, hi = rec.get('window', [rec['f'], rec['f']])
        near_b[max(0, lo - 2):min(n, hi + 3)] = True
    evt = np.zeros(n, bool)
    for f in plan.events:
        if f < n:
            evt[max(0, f - 1):min(n, f + 2)] = True
    segof = plan.seg_of[:n]
    quiet = valid & np.isfinite(raw) & ~near_b & ~evt
    quiet[0] = False
    qi = np.where(quiet)[0]
    base = {}
    for k, X in S.items():                      # local within-shot change level (median of quiet pairs within ±8)
        g = float(np.median(X[quiet])) if len(qi) >= 5 else 0.01
        b_ = np.full(n, g)
        for f in range(1, n):
            sel = qi[(qi >= f - 8) & (qi <= f + 8) & (np.abs(qi - f) > 1)]
            if len(sel) >= 3:
                b_[f] = float(np.median(X[sel]))
        base[k] = b_

    def span(c):
        return bridge.get(c, c - 1), c          # the change happened somewhere in frames (p, c]

    def side_ref(k, p, c):
        """Within-shot change next to the pair (p, c): the pair ending at p and the pair (c, c+1), each only if it
        lies inside one segment. A cut that sits a frame off makes one of them the real cut, so it fails."""
        X, vals = S[k], []
        if p >= 1 and np.isfinite(X[p]) and segof[span(p)[0]] == segof[p]:
            vals.append(X[p])
        if c + 1 < n and np.isfinite(X[c + 1]) and segof[c] == segof[c + 1]:
            vals.append(X[c + 1])
        return max(vals) if vals else base[k][min(c, n - 1)]

    def judge(p, c, a=1.25, m=0.02, floor=0.05, d=None):
        """Which signals show a clear step on the pair (p, c), plus the scores and thresholds."""
        out, info = [], {}
        for k in ('mc', 'raw'):
            v = S[k][c] if d is None else d[k]
            if not np.isfinite(v):
                continue
            t_ = max(floor, a * side_ref(k, p, c) + m)
            info[k] = (r(v), r(t_))
            if v >= t_:
                out.append(k)
        return out, info

    def put(rec, info):
        if 'mc' in info:
            rec['score'], rec['thr'] = info['mc']
        if 'raw' in info:
            rec['score_raw'], rec['thr_raw'] = info['raw']

    def judge_transition(rec):
        """A transition is judged inside its window. Across it (last frame before vs first frame after) the pictures
        must differ. Soft kinds must blend gradually: no single pair of textured frames inside the window may carry a
        cut-sized step (status 'hard' = rendered as a hard cut). Hard kinds switch pictures on one frame: frames
        inside the window are classified as showing the outgoing (A) or incoming (B) picture (flat white / black /
        blurred frames say nothing and are skipped); the switch range must contain the boundary frame f0 (more than
        2 frames away = 'offset', a renderer timing bug)."""
        a, z = rec['window']
        b = rec['f']
        p, qn = a - 1, z + 1
        while p >= 0 and not valid[p]:
            p -= 1
        while qn < n and not valid[qn]:
            qn += 1
        if p < 0 or qn >= n:
            rec['status'] = 'transition'
            rec['note'] = 'window touches the start or end of the render'
            return
        by, info = judge(p, qn, a=2.0, m=0.05, floor=0.08, d={'mc': sig.pair_mc(p, qn), 'raw': sig.pair(p, qn)})
        put(rec, info)
        rec['status'] = 'transition' if by else ('soft' if rec['continuity'] == 'continuous' else 'transition_weak')
        across, _ = sig.pair_tex(p, qn)
        rec['d_across'] = r(across)
        if rec.get('tclass', 'soft') == 'soft':
            steps = []
            prev = p
            for c in range(p + 1, qn + 1):
                if not valid[c]:
                    continue
                if c - prev == 1:                     # a step bridged over opaque op frames is masked by design
                    d, share = sig.pair_tex(prev, c)
                    if np.isfinite(d) and share >= 0.3:
                        steps.append((d, c))
                prev = c
            if steps and np.isfinite(across):
                dmax, cmax = max(steps)
                rest = [d for d, c in steps if c != cmax]
                lvl = float(np.median(rest)) if rest else 0.0
                rec['max_step'] = dict(f=int(cmax), d=r(dmax), others=r(lvl))
                if by and dmax >= max(0.2, 0.6 * across) and dmax >= 3.0 * lvl + 0.04:
                    rec.update(status='hard', detected=int(cmax))
            return
        last_a, first_b, seq = p, qn, []
        for j in range(p + 1, qn):
            if not valid[j]:
                continue
            da, sa = sig.pair_tex(p, j)
            db, sb = sig.pair_tex(j, qn)
            if not (np.isfinite(da) and np.isfinite(db)) or min(sa, sb) < 0.3:
                continue
            # decisive only: (nearly) the same picture as one side and clearly not the other - fast speed ramps and
            # look-alike shots (sky / snow) make anything in between ambiguous
            if da < 0.1 and db > 0.25:
                seq.append((j, 'A'))
            elif db < 0.1 and da > 0.25:
                seq.append((j, 'B'))
        a_like = [j for j, s in seq if s == 'A']
        b_like = [j for j, s in seq if s == 'B']
        if a_like:
            last_a = max(a_like)
        if b_like:
            first_b = min(b_like)
        if first_b <= last_a:                      # A after B: effect frames, no clear switch
            rec['switch'] = None
            return
        rec['switch'] = [int(last_a + 1), int(first_b)]
        off = 0 if last_a < b <= first_b else ((last_a + 1 - b) if b <= last_a else (first_b - b))
        if off:
            rec['seam_offset'] = int(off)
        wrong = sum(1 for j in a_like if j >= b) if off > 0 else sum(1 for j in b_like if j < b)
        if by and abs(off) >= 3 and wrong >= 2:
            rec.update(status='offset', offset=int(off), detected=int(last_a + 1 if off > 0 else first_b))

    claimed = {}
    recs = []
    for rec in plan.boundaries:
        rec = dict(rec)
        b = rec['f']
        if b >= n:
            rec['status'] = 'not_rendered'
            recs.append(rec)
            continue
        if rec['kind'] == 'transition':
            judge_transition(rec)
            recs.append(rec)
            continue
        c = b                                    # the only pair whose span covers b: first valid frame >= b
        while c < n and not valid[c]:
            c += 1
        if c < n and np.isfinite(raw[c]):
            p = span(c)[0]
            by, info = judge(p, c)
            put(rec, info)
            if p < b and by:
                rec.update(status='exact' if c - p == 1 else 'masked', detected=c, by=by)
                if c - p > 1:
                    rec['hidden'] = [p + 1, c - 1]
                claimed[c] = b
        recs.append(rec)

    def is_peak(c):
        for k in ('mc', 'raw'):
            X = S[k]
            nb = [X[x] for x in (c - 1, c + 1) if 0 < x < n and x not in claimed and np.isfinite(X[x])]
            if np.isfinite(X[c]) and X[c] >= max(0.08, 2.0 * max(nb or [base[k][c]]) + 0.03):
                return True
        return False

    for rec in recs:                              # second pass: a clear unclaimed peak near b -> offset
        if rec.get('status'):
            continue
        b = rec['f']
        best = None
        for c in range(max(1, b - 4), min(n, b + 5)):
            if valid[c] and np.isfinite(raw[c]) and c not in claimed and not plan.trans_win[c] and is_peak(c):
                if best is None or (abs(c - b), -np.nan_to_num(mc[c])) < (abs(best - b), -np.nan_to_num(mc[best])):
                    best = c
        if best is not None:
            p, c = span(best)
            off = (c - b) if c < b else (p + 1 - b)
            rec.update(status='offset', detected=best, offset=int(off), score=r(mc[best]), score_raw=r(raw[best]))
            claimed[best] = b
            continue
        # two picture changes one frame apart at the boundary: a single-frame shot between them (flash frame) - e.g.
        # the source's own camera cut one frame after the planned reframe shows the old camera in the new framing
        dbl = None
        for c1 in (b, b - 1):
            c2 = c1 + 1
            if c1 >= 1 and c2 < n and all(valid[x] and x not in claimed and np.isfinite(mc[x])
                                          and mc[x] >= max(0.15, 3.0 * base['mc'][x] + 0.05) for x in (c1, c2)):
                dbl = (c1, c2)
                break
        acc = planned_accent(plan, rec) if dbl is None else None
        if acc:
            rec.update(status='accent', accent=acc, note='visible by construction: a planned ' + acc + ' on the cut frame')
            continue
        if dbl is not None:
            c1, c2 = dbl
            rec.update(status='flash_frame', detected=c1, flash=c1, steps=[c1, c2], score=r(mc[c1]), score2=r(mc[c2]))
            near_src = any(abs(s - b) <= 1 for s in src_cuts)
            rec['hint'] = (f"frame {c1} is a single-frame shot between picture changes at {c1} and {c2}"
                           + (f"; the source's own camera cut shows at {c2 if c1 == b else c1}, one frame "
                              f"{'after' if c1 == b else 'before'} the planned cut {b} (qa.source_cuts): move the boundary "
                              f"to {c2 if c1 == b else c1}" if near_src else ''))
            claimed[c1] = claimed[c2] = b
        else:
            rec['status'] = 'soft' if rec['continuity'] == 'continuous' else 'missing'
    unexpected, look = [], []
    M0 = np.nan_to_num(mc)
    for c in range(1, n):
        if not np.isfinite(mc[c]) or c in claimed or not valid[c] or plan.trans_win[c]:
            continue
        nb = max([M0[x] for x in (c - 1, c + 1) if 0 < x < n and x not in claimed] + [0.0])
        if mc[c] >= max(0.25, 4.0 * base['mc'][c] + 0.08) and mc[c] >= 2.5 * nb and raw[c] >= 0.2:
            item = dict(f=c, t=r(c / plan.fps, 3), seg=plan.seg_id(c), score=r(mc[c]), score_raw=r(raw[c]))
            causes = set()
            for f in (c - 1, c, c + 1):
                causes |= plan.events.get(f, set())
            if causes:
                item['cause'] = sorted(causes)
                look.append(item)
                continue
            si = plan.seg_of[c]
            if si >= 0:
                sg = plan.segs[si]
                k, nseg = int(c - sg['f0']), int(sg['f1'] - sg['f0'] + 1)
                item.update(k=k, src_t=r(plan.src_time(c), 3))
                if k <= 3:
                    item['hint'] = (f"first {k} frame(s) of {sg.get('id')} come from the previous shot of the source: "
                                    f"set t >= {plan.src_time(c):.3f}")
                elif k >= nseg - 3:
                    item['hint'] = (f"last {nseg - k} frame(s) of {sg.get('id')} come from the next shot of the source: "
                                    f"end it at frame {c - 1} or move t back by {(nseg - k) / plan.fps:.3f} s")
                else:
                    item['hint'] = f"{sg.get('id')} crosses a shot change in its source at about {plan.src_time(c):.3f} s"
            unexpected.append(item)
    st = {}
    for rec in recs:
        st[rec['status']] = st.get(rec['status'], 0) + 1
    n_off = st.get('offset', 0)
    n_miss = st.get('missing', 0) + st.get('transition_weak', 0) + st.get('hard', 0) + st.get('flash_frame', 0)
    status = 'fail' if n_off or st.get('not_rendered') else ('warn' if n_miss or unexpected else 'ok')
    return check(status, n_boundaries=len(recs), counts=st, boundaries=recs, unexpected=unexpected, look_changes=look,
                 signal_baseline=r(float(np.median(base['mc'])), 4)), mc, raw


def storyboard_gaps(edl):
    """Storyboard slots still to fill: meta.gaps items of kind 'storyboard' (ed_plan.plan_storyboard: every slot a
    slate placeholder with an edit-gen brief; fill_gaps removes the filled ones) -> (gaps [{id, slot, f, t, dur, need_s,
    part, role, shot, subject, camera, generate_s}], {segment index}, other planner gaps [{id, kind, reason}])."""
    meta = edl.get('meta') or {}
    segs = edl.get('segments') or []
    fps = float((edl.get('canvas') or {}).get('fps') or 30)
    by_id = {str(sg.get('id')): i for i, sg in enumerate(segs)}
    out, idx, other = [], set(), []
    for g in meta.get('gaps') or []:
        if not isinstance(g, dict):
            continue
        if g.get('kind') != 'storyboard' or g.get('fill'):
            other.append({k: g.get(k) for k in ('id', 'slot', 'kind', 'reason', 'fill') if g.get(k) is not None})
            continue
        si = by_id.get(str(g.get('id')))
        if si is None and isinstance(g.get('slot'), int) and 0 <= g['slot'] < len(segs):
            si = g['slot']
        if si is None:
            continue
        sg, b = segs[si], g.get('brief') if isinstance(g.get('brief'), dict) else {}
        f0, f1 = int(sg['f0']), int(sg['f1'])
        out.append(dict(id=sg.get('id'), slot=g.get('slot', si), f=[f0, f1], t=[r(f0 / fps, 3), r((f1 + 1) / fps, 3)],
                        dur=r((f1 - f0 + 1) / fps, 3), need_s=g.get('need_s'), part=g.get('part'), role=g.get('role'),
                        shot=b.get('shot_size'), subject=b.get('subject'), camera=b.get('camera'),
                        generate_s=(b.get('duration') or {}).get('generate_s') if isinstance(b.get('duration'), dict) else None))
        idx.add(si)
    return out, idx, other


def mark_gap_boundaries(cuts, plan):
    """Boundaries next to a storyboard slate are not judged for visibility (two slates differ in a few lines of text):
    missing / weak / hard -> 'gap' (they still count as planned cuts for the rhythm); unexpected steps inside a slate
    segment are moved to look_changes. Recomputes the cuts status."""
    gaps = getattr(plan, 'gap_segs', None)
    if not gaps:
        return cuts
    ids = {str(plan.segs[i].get('id', i)) for i in gaps}
    for rec in cuts['boundaries']:
        if (str(rec['prev']) in ids or str(rec['next']) in ids) and rec['status'] in ('missing', 'transition_weak', 'hard'):
            rec.update(judged=rec['status'], status='gap', note='next to a storyboard slate: the shot is still to be generated')
    keep = []
    for u in cuts['unexpected']:
        si = plan.seg_of[u['f']] if 0 <= u['f'] < plan.n else -1
        if si in gaps:
            cuts['look_changes'].append(dict(u, cause=['storyboard slate']))
        else:
            keep.append(u)
    cuts['unexpected'] = keep
    st = {}
    for rec in cuts['boundaries']:
        st[rec['status']] = st.get(rec['status'], 0) + 1
    cuts['counts'] = st
    n_miss = st.get('missing', 0) + st.get('transition_weak', 0) + st.get('hard', 0) + st.get('flash_frame', 0)
    cuts['status'] = 'fail' if st.get('offset') or st.get('not_rendered') else ('warn' if n_miss or keep else 'ok')
    return cuts


_PUNCH_FX = {'zoom.punch', 'beat_punch', 'punch'}
_SHAKE_FX = {'shake.beat', 'beat_shake', 'shake_beat', 'shake'}


def _fx_event_frames(fx, plan, sg):
    """Output frames where an event-driven camera fx fires: 'times' = output seconds (numbers, or 'beats' /
    'downbeats' from audio.grid; peak frame floor(t * fps + 0.4)), else its frame gates ('frames' segment-relative,
    'f' absolute), else every frame of the segment (an fx without events applies throughout)."""
    fps, f0, f1 = plan.fps, int(sg['f0']), int(sg['f1'])
    tms = fx.get('times')
    if tms is not None:
        grid = (plan.edl.get('audio') or {}).get('grid') or {}
        if isinstance(tms, str):
            tms = grid.get('downbeats' if tms.startswith('down') else 'beats') if tms in ('beats', 'downbeats') else []
        return {int(math.floor(float(t) * fps + 0.4)) for t in tms or [] if isinstance(t, (int, float))}
    if fx.get('frames') is not None:
        return {f0 + k for k in frange(fx['frames'])}
    if fx.get('f') is not None:
        return set(frange(fx['f']))
    return set(range(f0, f1 + 1))


def planned_accent(plan, rec):
    """A cut the EDL makes visible by construction: a punch (crop scale change >= x1.08 across the boundary, or a
    zoom.punch of scale >= 1.08 firing on the cut frame) or a shake on the cut frame -> 'punch x1.12' | 'shake' | None.
    A wide, dark shot can hide the step from the pixel signals; the planned jolt still reads."""
    pi, ci = rec.get('pi'), rec.get('ci')
    if pi is None or ci is None:
        return None
    p, c = plan.segs[pi], plan.segs[ci]
    try:
        zp = float(crop_at(p, int(p['f1']) - int(p['f0']))['z'])
        zc = float(crop_at(c, 0)['z'])
        ratio = max(zp, zc) / max(1e-6, min(zp, zc))
        if ratio >= 1.08 - 1e-6:
            return f'punch x{ratio:.2f}'
    except (KeyError, TypeError, ValueError):
        pass
    b = rec['f']
    for fx in (c.get('fx') or []):
        if not isinstance(fx, dict):
            continue
        t = str(fx.get('type') or '').lower()
        if t not in _PUNCH_FX and t not in _SHAKE_FX:
            continue
        if not any(abs(e - b) <= 1 for e in _fx_event_frames(fx, plan, c)):
            continue
        if t in _PUNCH_FX:
            sc = float(fx.get('scale', 1.2) or 1.2)
            if sc >= 1.08 - 1e-6:
                return f'punch x{sc:.2f}'
        else:
            return 'shake'
    return None


_PROBE = {}


def probe_cached(path):
    if path not in _PROBE:
        _PROBE[path] = V.probe(path)
    return _PROBE[path]


def source_steps(cfg, t_a, t_b, pad=4, width=160):
    """Shot change in the source between the frames the renderer shows at source times t_a and t_b? Decodes the
    source picture box from `pad` frames before to `pad` frames after (small, gray) and measures every consecutive
    step with the textured, shift-compensated cell NCC. -> dict(cut=bool, src_t=time of the first frame after the
    largest step inside, d=that step, level=median step around it), or None when the source cannot be read."""
    path = cfg.get('path', '')
    if not os.path.exists(path):
        return None
    try:
        inf = probe_cached(path)
    except (subprocess.CalledProcessError, OSError, ValueError, KeyError):
        return None
    sfps = float(cfg.get('fps') or inf.get('fps') or 25.0)
    box = cfg.get('box') or [0, 0, inf['w'], inf['h']]
    bw, bh = int(box[2] - box[0]), int(box[3] - box[1])
    w = min(width, bw)
    h = max(16, int(round(bh * w / bw / 2)) * 2)
    lo, hi = sorted((renderer_time(t_a, sfps), renderer_time(t_b, sfps)))
    t0 = max(0.0, lo - pad / sfps)
    dur = hi - t0 + (pad + 0.5) / sfps
    cmd = ['ffmpeg', '-v', 'error', '-nostdin', '-ss', f'{t0:.4f}', '-i', path, '-t', f'{dur:.4f}', '-an',
           '-vf', f'crop={bw}:{bh}:{int(box[0])}:{int(box[1])},scale={w}:{h}:flags=area', '-fps_mode', 'passthrough',
           '-f', 'rawvideo', '-pix_fmt', 'gray', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    k = len(raw) // (w * h)
    if k < 3:
        return None
    g = np.frombuffer(raw[:k * w * h], np.uint8).reshape(k, h, w)
    times = math.ceil(t0 * sfps - 1e-4) / sfps + np.arange(k) / sfps
    sig = CutSignal(g, np.zeros(k, bool))
    steps = np.array([sig.pair_tex(i - 1, i)[0] for i in range(1, k)], float)        # step i-1 -> i at index i-1
    eps = 0.25 / sfps
    inside = [i for i in range(1, k) if lo + eps < times[i] <= hi + eps]
    if not inside:
        inside = [i for i in (int(np.argmin(np.abs(times - hi))),) if i >= 1]
    if not inside:
        return None
    vals = np.nan_to_num(steps, nan=0.0)
    i_best = max(inside, key=lambda i: vals[i - 1])
    other = [vals[i - 1] for i in range(1, k) if abs(i - i_best) > 1]
    level = float(np.median(other)) if other else 0.0
    d = float(vals[i_best - 1])
    return dict(cut=bool(d >= 0.25 and d >= 2.5 * level + 0.05), src_t=r(times[i_best], 3), d=r(d), level=r(level))


def verify_unexpected(cuts, plan, sources=None):
    """Unexpected cuts are steps inside a segment. Each one is checked against its source: a real shot change in
    the source between the two shown source frames stays an unexpected cut (with its exact source time); a source
    that is continuous there (fast speed ramps, camera fx, warps) moves the step to look_changes."""
    keep, srcs = [], sources if sources is not None else (plan.edl.get('sources') or {})
    for u in cuts['unexpected']:
        si = plan.seg_of[u['f']] if 0 <= u['f'] < plan.n else -1
        cfg = srcs.get(plan.segs[si].get('src', 'film')) if si >= 0 else None
        res = None
        if cfg:
            sg = plan.segs[si]
            k = u['f'] - int(sg['f0'])
            try:
                res = source_steps(cfg, seg_time(sg, k - 1, plan.fps), seg_time(sg, k, plan.fps))
            except (OSError, ValueError, subprocess.SubprocessError):
                res = None
        if res is None:
            u['source_check'] = 'unavailable'
            keep.append(u)
        elif res['cut']:
            u['source_check'] = res
            u['hint'] = (u.get('hint') or '') + f" (shot change in the source at {res['src_t']:.3f} s)"
            keep.append(u)
        else:
            u['source_check'] = res
            u['cause'] = ['source continuous: speed / fx / warp']
            cuts['look_changes'].append(u)
    cuts['unexpected'] = keep
    if not keep and cuts['status'] == 'warn':
        st = cuts['counts']
        if not (st.get('missing') or st.get('transition_weak') or st.get('hard') or st.get('flash_frame')):
            cuts['status'] = 'ok'
    return cuts


def verify_frozen(fr_chk, plan, sources, width=160):
    """An unplanned frozen run whose source time advances is checked on the source: when the source frames over that
    time are themselves (nearly) identical (a static shot: mean step < 0.6 levels), the hold is the footage, not a
    renderer freeze -> planned_by 'static source shot'."""
    changed = False
    for x in fr_chk['frozen']:
        if 'unplanned' not in x:
            continue
        a, b = x['unplanned']
        si = plan.seg_of[a] if 0 <= a < plan.n else -1
        if si < 0 or plan.seg_of[min(b, plan.n - 1)] != si:
            continue
        sg = plan.segs[si]
        cfg = sources.get(sg.get('src', 'film'))
        path = (cfg or {}).get('path') or ''
        if not os.path.exists(path):
            continue
        t0, t1 = sorted((seg_time(sg, a - int(sg['f0']), plan.fps), seg_time(sg, b - int(sg['f0']), plan.fps)))
        try:
            inf = probe_cached(path)
        except (subprocess.CalledProcessError, OSError, ValueError, KeyError):
            continue
        sfps = float(cfg.get('fps') or inf.get('fps') or 25.0)
        if t1 - t0 < 1.5 / sfps:
            continue                                   # the source does not advance: a real hold
        box = cfg.get('box') or [0, 0, inf['w'], inf['h']]
        bw, bh = int(box[2] - box[0]), int(box[3] - box[1])
        w = min(width, bw)
        h = max(16, int(round(bh * w / bw / 2)) * 2)
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-ss', f'{max(0.0, t0):.4f}', '-i', path, '-t',
                              f'{t1 - t0 + 0.5 / sfps:.4f}', '-an', '-vf',
                              f'crop={bw}:{bh}:{int(box[0])}:{int(box[1])},scale={w}:{h}:flags=area', '-fps_mode',
                              'passthrough', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
        k = len(raw) // (w * h)
        if k < 2:
            continue
        g = np.frombuffer(raw[:k * w * h], np.uint8).reshape(k, h, w).astype(np.int16)
        step = float(np.median(np.abs(np.diff(g, axis=0)).reshape(k - 1, -1).mean(1)))
        x['source_step'] = r(step, 2)
        if step < 0.6:
            del x['unplanned']
            x['planned_by'] = ['static source shot']
            changed = True
    if changed:
        uf = [x for x in fr_chk['frozen'] if 'unplanned' in x]
        fr_chk['unplanned_frozen'] = len(uf)
        if fr_chk['status'] == 'fail' and not (uf or fr_chk['unplanned_black'] or fr_chk['edl_gaps']):
            fr_chk['status'] = 'warn' if fr_chk['unplanned_white'] else 'ok'
    return fr_chk


# ============================================================================ rhythm (beats / words)
def cut_events(cuts, plan):
    """Visible cuts as rhythm events: the detected cut frame of hard cuts; for a transition its boundary frame f0
    (the seam of hard kinds, the start / centre of soft blends: the frame the planner put on the beat or word gap),
    or the detected switch frame when it is off."""
    ev = []
    for rec in cuts['boundaries']:
        if rec['status'] in ('soft', 'not_rendered'):
            continue
        if rec['kind'] == 'transition':
            f = rec.get('detected', rec['f']) if rec['status'] in ('offset', 'hard') else rec['f']
        else:
            f = rec.get('detected', rec['f']) if rec['status'] in ('exact', 'offset') else rec['f']
        ev.append(dict(f=int(f), id=f"{rec['prev']}|{rec['next']}", kind='edl'))
    for u in cuts['unexpected']:
        ev.append(dict(f=u['f'], id=f"unexpected@{u['seg']}", kind='unexpected'))
    return sorted(ev, key=lambda e: e['f'])


def beat_grid(aud, dur):
    beats = np.array(aud.get('beats') or [], float)
    if len(beats) < 2:
        return np.array([]), np.array([], object)
    per = float(np.median(np.diff(beats)))
    pts, kinds = list(beats), ['beat'] * len(beats)
    pts += list((beats[:-1] + beats[1:]) / 2)
    kinds += ['half'] * (len(beats) - 1)
    t = beats[0] - per / 2
    k = 'half'
    while t > -per:
        pts.append(t)
        kinds.append(k)
        t -= per / 2
        k = 'beat' if k == 'half' else 'half'
    t, k = beats[-1] + per / 2, 'half'
    while t < dur + per:
        pts.append(t)
        kinds.append(k)
        t += per / 2
        k = 'beat' if k == 'half' else 'half'
    o = np.argsort(pts)
    return np.array(pts)[o], np.array(kinds, object)[o]


def source_cut_frames(q, fps):
    """qa.source_cuts -> set of output frames: the source's own camera cuts that the edit shows (frames, or {"f"} /
    {"t": seconds} items). An editor does not choose where they fall, so they are not judged against the words."""
    out = set()
    for x in q.get('source_cuts') or []:
        try:
            if isinstance(x, dict):
                f = int(round(float(x['f']))) if x.get('f') is not None else int(round(float(x['t']) * fps))
            elif isinstance(x, (int, float)) and not isinstance(x, bool):
                f = int(round(float(x)))
            else:
                continue
        except (KeyError, TypeError, ValueError):
            continue
        out.add(f)
    return out


def _rhythm_words(events, words, fps, tol, need, source_cuts=()):
    if not words:
        return check('skipped', mode='words', note='no word timestamps in qa.words')
    tol_s = tol / fps
    inside, exempt, judged = [], [], []
    for e in events:
        t = e['f'] / fps
        w = next((w for w in words if w['t0'] + tol_s < t < w['t1'] - tol_s), None)
        if any(abs(e['f'] - s) <= 1 for s in source_cuts):
            exempt.append(dict(f=e['f'], t=r(t, 3), id=e['id'], inside_word=w.get('w') if w else None))
            continue
        judged.append(e)
        if w:
            inside.append(dict(f=e['f'], t=r(t, 3), word=w.get('w'), w_t0=w['t0'], w_t1=w['t1'], id=e['id']))
    share = 1 - len(inside) / len(judged) if judged else 1.0
    return check('fail' if share < need - 1e-9 else 'ok', mode='words', n_cuts=len(judged), share=r(share),
                 threshold=need, cuts_inside_words=inside, source_cuts_exempt=exempt)


def analyse_rhythm(events, plan, q, aud, dur, parts=None):
    """Speech edits: cuts against word spans. Music edits: cuts against the beat / half-beat grid. Composite edits
    (talk + music parts): cuts inside talk parts against the words, cuts inside music parts against the grid of the
    music bed (aud = analysis of the music file placed on the timeline when the mix carries a voice)."""
    fps = plan.fps
    tol = float(q['grid_tol_frames'])
    types = {p['type'] for p in parts or []}
    if parts and len(parts) > 1 and 'music' in types and types & {'talk', 'clip'}:
        talk_ev = [e for e in events if (part_at(parts, e['f']) or {}).get('type') in ('talk', 'clip')]
        music_ev = [e for e in events if (part_at(parts, e['f']) or {}).get('type') == 'music']
        need_w = float(q['on_word_share']) if q.get('on_word_share') is not None else 1.0
        # per-part thresholds (qa.parts [{"id", "on_beat_share" | "on_word_share"}], ed_sequence): the strictest applies
        pq = {str(x.get('id')): x for x in q.get('parts') or [] if isinstance(x, dict)}
        ws = [float(pq[p['id']]['on_word_share']) for p in parts if p['type'] in ('talk', 'clip')
              and pq.get(p['id'], {}).get('on_word_share') is not None]
        bs = [float(pq[p['id']]['on_beat_share']) for p in parts if p['type'] == 'music'
              and pq.get(p['id'], {}).get('on_beat_share') is not None]
        need_w = max(ws) if ws else need_w
        rw = _rhythm_words(talk_ev, q['words'], fps, tol, need_w, source_cut_frames(q, fps))
        q2 = dict(q, mode='music', on_beat_share=max(bs) if bs else q['on_beat_share'])
        rb = analyse_rhythm(music_ev, plan, q2, aud, dur)
        st = max((rw['status'], rb['status']), key=lambda s: LEVELS[s])
        out = check(st, mode='parts', words=rw, beats=rb, n_cuts=len(events))
        for k in ('share', 'bpm', 'tempo_conf', 'on_grid', 'threshold', 'tol_frames', 'off_grid', 'cuts', 'chance_share',
                  'share_quarter_grid', 'grid_source'):
            if k in rb:
                out[k] = rb[k]
        out['cuts_inside_words'] = rw.get('cuts_inside_words', [])
        out['source_cuts_exempt'] = rw.get('source_cuts_exempt', [])
        return out
    if q['mode'] == 'speech':
        if not q['words']:
            return check('skipped', mode='words', note='speech genre: no word timestamps in qa.words; beat check off')
        return _rhythm_words(events, q['words'], fps, tol, float(q['on_word_share']), source_cut_frames(q, fps))
    if not aud:
        return check('skipped', mode='beats', note='no audio stream in the render')
    if aud.get('error'):
        return check('skipped', mode='beats', note='audio analysis failed: ' + aud['error'])
    grid, kinds = beat_grid(aud, dur)
    if not len(grid):
        return check('skipped', mode='beats', note='no beats found in the rendered audio')
    rows = []
    for e in events:
        t = e['f'] / fps
        i = int(np.argmin(np.abs(grid - t)))
        off = (t - grid[i]) * fps
        rows.append(dict(f=e['f'], t=r(t, 3), offset_frames=r(off, 2), grid=str(kinds[i]), on=bool(abs(off) <= tol + 1e-6),
                         id=e['id']))
    on = sum(x['on'] for x in rows)
    share = on / len(rows) if rows else 1.0
    need = float(q['on_beat_share'])
    quarter = np.sort(np.concatenate([grid, (grid[:-1] + grid[1:]) / 2]))          # context only: 1/16 grid
    q_on = sum(1 for x in rows if np.min(np.abs(quarter - x['t'])) * fps <= tol + 1e-6)
    return check('fail' if rows and share < need - 1e-9 else 'ok', mode='beats', bpm=aud.get('bpm'),
                 tempo_conf=aud.get('tempo_conf'), steady=aud.get('steady'), n_cuts=len(rows), on_grid=on, share=r(share),
                 threshold=need, tol_frames=tol, share_quarter_grid=r(q_on / len(rows)) if rows else None,
                 chance_share=r(min(1.0, (2 * tol + 1) / max(1e-6, fps * float(np.median(np.diff(grid)))))),
                 off_grid=[x for x in rows if not x['on']], cuts=rows, grid_source=aud.get('source', 'rendered audio'))


# ============================================================================ 3 loudness
def loudness(video):
    p = subprocess.run(['ffmpeg', '-v', 'info', '-nostats', '-nostdin', '-i', video, '-vn', '-filter_complex',
                        'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    txt = p.stderr
    summ = txt.split('Summary:')[-1] if 'Summary:' in txt else ''
    I = re.search(r'I:\s+(-?[\d.]+|-inf) LUFS', summ)
    lra = re.search(r'LRA:\s+(-?[\d.]+) LU', summ)
    tp = re.search(r'Peak:\s+(-?[\d.]+|-inf) dBFS', summ)
    fl = lambda m: (float(m.group(1)) if m and m.group(1) != '-inf' else None)
    series = dict(t=[], M=[], S=[], tpk=[])
    for m in re.finditer(r't:\s*([\d.]+)\s+TARGET:.*?M:\s*(-?[\d.]+|-inf)\s+S:\s*(-?[\d.]+|-inf).*?FTPK:\s*([-\d. inf]+?)\s*dBFS',
                         txt):
        series['t'].append(float(m.group(1)))
        series['M'].append(max(-70.0, float(m.group(2))) if m.group(2) != '-inf' else -70.0)
        series['S'].append(max(-70.0, float(m.group(3))) if m.group(3) != '-inf' else -70.0)
        pk = [float(v) for v in m.group(4).split() if v not in ('-inf', 'inf')]
        series['tpk'].append(max(pk) if pk else -70.0)
    return dict(lufs=fl(I), lra=fl(lra), true_peak=fl(tp), series=series)


def judge_loudness(L, q, side=None):
    """Integrated loudness and true peak measured on the MP4 itself (ffmpeg ebur128, after the AAC encode); the
    render sidecar's own numbers (the mixer's WAV) are reported next to them, never used for the verdict."""
    if L is None:
        return check('skipped', note='no audio stream in the render')
    if L.get('lufs') is None:
        return check('fail', note='loudness could not be measured', **{k: L.get(k) for k in ('lufs', 'true_peak')})
    bad = []
    if abs(L['lufs'] - q['lufs']) > q['lufs_tol'] + 1e-9:
        bad.append('lufs')
    if L.get('true_peak') is not None and L['true_peak'] > q['tp_max'] + 1e-9:
        bad.append('true_peak')
    S = [v for v in L['series']['S'] if v > -69]
    M = [v for v in L['series']['M'] if v > -69]
    out = dict(lufs=L['lufs'], lufs_target=q['lufs'], lufs_tol=q['lufs_tol'], lra=L.get('lra'),
               true_peak=L.get('true_peak'), tp_max=q['tp_max'], max_momentary=r(max(M), 1) if M else None,
               max_short_term=r(max(S), 1) if S else None, out_of_range=bad, measured_on='mp4')
    if isinstance(side, dict) and side:
        sc = {k: side.get(k) for k in ('method', 'lufs', 'tp', 'gain_db', 'gr_max_db', 'music_lufs', 'sfx_count', 'codec',
                                        'bitrate') if side.get(k) is not None}
        enc = side.get('encode') if isinstance(side.get('encode'), dict) else None
        if enc:
            sc['encode'] = {k: v for k, v in enc.items() if isinstance(v, (int, float, str)) and k != 's'}
        if sc:
            out['sidecar'] = sc
            # the delivered AAC (audio.encode: what the renderer measured on the file it muxed) is the comparable
            # number; the mix WAV's is the fallback for renders without an encode block
            ref = enc if enc and isinstance(enc.get('lufs'), (int, float)) else sc
            out['sidecar_ref'] = 'encode' if ref is enc else 'mix'
            if isinstance(ref.get('lufs'), (int, float)):
                out['sidecar_delta_lufs'] = r(L['lufs'] - ref['lufs'], 2)
            if isinstance(ref.get('tp'), (int, float)) and L.get('true_peak') is not None:
                out['sidecar_delta_tp'] = r(L['true_peak'] - ref['tp'], 2)
            dl, dt = out.get('sidecar_delta_lufs'), out.get('sidecar_delta_tp')
            if ref is enc and (abs(dl or 0) > 0.5 or abs(dt or 0) > 0.5):
                out['sidecar_mismatch'] = ('the MP4 measures ' + ', '.join(
                    f'{v:+.2f} {u}' for v, u in ((dl, 'LU'), (dt, 'dB true peak')) if v is not None)
                    + " off the renderer's encode numbers (audio re-encoded or replaced after the render?)")
    return check('fail' if bad else 'ok', **out)


# ============================================================================ 4 black / white / frozen
def still_pairs(gray):
    """Pair (f-1, f) shows the same picture: 90th percentile of 20 px cell mean differences < 0.35 and >= 97 % of
    pixels within ±1 level (a held frame survives H.264 almost bit-exact; real static shots do not)."""
    n, ah, aw = gray.shape
    cs = 20
    ny, nx = ah // cs, aw // cs
    out = np.zeros(n, bool)
    p90 = np.full(n, np.nan)
    for s in range(1, n, 64):
        e = min(n, s + 64)
        d = np.abs(gray[s:e].astype(np.int16) - gray[s - 1:e - 1].astype(np.int16))
        frac = (d <= 1).reshape(e - s, -1).mean(1)
        cells = d[:, :ny * cs, :nx * cs].reshape(e - s, ny, cs, nx, cs).mean(axis=(2, 4)).reshape(e - s, -1)
        pc = np.percentile(cells, 90, axis=1)
        p90[s:e] = pc
        out[s:e] = (pc < 0.35) & (frac >= 0.97)
    return out, p90


def analyse_frames(gray, plan, q, nv):
    n = min(nv, plan.n)
    fps = plan.fps
    g = gray[:n]
    blk = (g <= q['black_luma'] * 255).reshape(n, -1).mean(1)
    wht = (g >= q['white_luma'] * 255).reshape(n, -1).mean(1)
    is_b, is_w = blk >= q['frame_ratio'], wht >= q['frame_ratio']
    exempt = plan.op_any[:n] | plan.trans_win[:n]
    pb = np.zeros(n, bool)
    pb[[f for f in plan.planned_black if f < n]] = True
    pw = np.zeros(n, bool)
    pw[[f for f in plan.planned_white if f < n]] = True
    gaps = runs(plan.seg_of[:n] < 0)

    def report(mask, planned):
        out = []
        for a, b in runs(mask):
            fr = np.arange(a, b + 1)
            un = fr[~(planned[fr] | exempt[fr])]
            item = dict(f0=a, f1=b, t0=r(a / fps, 3), frames=int(b - a + 1), segs=sorted({plan.seg_id(f) or 'gap' for f in fr}))
            if len(un):
                item['unplanned'] = [int(un[0]), int(un[-1])]
                item['unplanned_frames'] = int(len(un))
            out.append(item)
        return out

    black, white = report(is_b, pb), report(is_w, pw)
    still, p90 = still_pairs(g)
    hold_min = max(2, int(math.ceil(q['freeze_min_s'] * fps - 1e-6)))
    ok_freeze = np.zeros(n, bool)
    slate = set(getattr(plan, 'slate_frames', ()) or ())
    ok_freeze[[f for f in plan.planned_freeze | plan.derived_freeze | slate if f < n]] = True
    ok_freeze |= exempt | pb | pw | is_b | is_w
    frozen = []
    for a, b in runs(still):                   # pairs a..b -> held frames a-1..b
        f0, f1 = a - 1, b
        length = f1 - f0 + 1
        if length < hold_min:
            continue
        fr = np.arange(f0, f1 + 1)
        un = [(a_ + f0, b_ + f0) for a_, b_ in runs(~ok_freeze[fr]) if b_ - a_ + 1 >= hold_min]
        item = dict(f0=int(f0), f1=int(f1), t0=r(f0 / fps, 3), dur_s=r(length / fps, 3), segs=sorted({plan.seg_id(f) or 'gap' for f in fr}))
        if un:
            a_, b_ = max(un, key=lambda x: x[1] - x[0])
            item['unplanned'] = [int(a_), int(b_)]
        else:
            item['planned_by'] = sorted({'storyboard slate' if f in slate else 'qa.planned_freeze' if f in plan.planned_freeze else
                                         ('edl speed 0' if f in plan.derived_freeze else 'op/black/white') for f in fr.tolist()})
        frozen.append(item)
    ub = [x for x in black if 'unplanned' in x]
    uw = [x for x in white if 'unplanned' in x]
    uf = [x for x in frozen if 'unplanned' in x]
    status = 'fail' if (ub or uf or gaps) else ('warn' if uw else 'ok')
    return check(status, black=black, white=white, frozen=frozen, unplanned_black=len(ub), unplanned_white=len(uw),
                 unplanned_frozen=len(uf), edl_gaps=[list(g_) for g_ in gaps], freeze_min_frames=hold_min,
                 planned_black=len(plan.planned_black), planned_white=len(plan.planned_white),
                 planned_freeze=len(plan.planned_freeze), derived_freeze=len(plan.derived_freeze)), still


# ============================================================================ 5 flashes (photosensitivity)
_LIN = ((np.arange(256) / 255.0 + 0.055) / 1.055) ** 2.4
_LIN[:11] = np.arange(11) / 255.0 / 12.92
_LIN = _LIN.astype(np.float32)


def transitions(sig_up, sig_dn, area):
    """Frame-level transition directions from per-frame up/down area fractions; ramps merge into one transition."""
    n = len(sig_up)
    d = np.zeros(n, int)
    d[(sig_up > area) & (sig_up >= sig_dn)] = 1
    d[(sig_dn > area) & (sig_dn > sig_up)] = -1
    out = []
    for f in range(1, n):
        if d[f] and not (d[f - 1] == d[f]):
            out.append((f, int(d[f])))
    return out


def alternating(trans):
    """Collapse runs of same-direction transitions (a staircase is not a flash)."""
    out = []
    for f, d in trans:
        if not out or out[-1][1] != d:
            out.append((f, d))
    return out


def window_flashes(trans, n, win):
    """Flashes in every 1 s window = alternating transitions inside it // 2 (a flash = a pair of opposing changes).
    Returns per-window-start counts (len n - win + 1, at least 1)."""
    fr = np.array([f for f, _ in trans], int)
    starts = max(1, n - win + 1)
    out = np.zeros(starts, int)
    for s in range(starts):
        sel = [trans[i] for i in np.where((fr >= s) & (fr <= s + win - 1))[0]]
        out[s] = len(alternating(sel)) // 2
    return out


def analyse_flashes(small, plan, q, nv):
    n = min(nv, plan.n)
    fps = plan.fps
    win = int(round(fps))
    delta, area = float(q['flash_delta']), float(q['flash_area'])
    up, dn, rup, rdn = (np.zeros(n) for _ in range(4))
    _, ah, aw, _ = small.shape
    hh, hw = ah // 2, aw // 2
    Yp = Rp = Sp = None                                 # last two frames of the previous chunk
    for s0 in range(0, n, 64):                          # differences vectorised over chunks of 64 frames
        s1 = min(n, s0 + 64)
        lin = _LIN[np.stack([cv2.resize(x, (hw, hh), interpolation=cv2.INTER_AREA) for x in small[s0:s1]])]
        Y = lin[..., 0] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 2] * 0.0722
        tot = lin.sum(-1)
        rs = (tot > 1e-4) & (lin[..., 0] >= 0.8 * np.maximum(tot, 1e-6))
        rv = np.maximum(0.0, lin[..., 0] - lin[..., 1] - lin[..., 2]) * 320.0
        if Yp is not None:
            Y, rs, rv = np.concatenate([Yp, Y]), np.concatenate([Sp, rs]), np.concatenate([Rp, rv])
        off = 0 if Yp is None else len(Yp)              # index of frame s0 inside the stacked arrays
        for k in (1, 2):                                # f vs f-1, and f vs f-2 (two-frame ramps)
            a = max(off, k)
            if a >= len(Y):
                continue
            cur, prv = Y[a:], Y[a - k:len(Y) - k]
            dY = cur - prv
            dark = np.minimum(cur, prv) < 0.8
            fidx = np.arange(s0 + a - off, s1)
            up[fidx] = np.maximum(up[fidx], ((dY >= delta) & dark).mean(axis=(1, 2)))
            dn[fidx] = np.maximum(dn[fidx], ((dY <= -delta) & dark).mean(axis=(1, 2)))
            dR = rv[a:] - rv[a - k:len(rv) - k]
            red = rs[a:] | rs[a - k:len(rs) - k]
            rup[fidx] = np.maximum(rup[fidx], ((dR > 20) & red).mean(axis=(1, 2)))
            rdn[fidx] = np.maximum(rdn[fidx], ((dR < -20) & red).mean(axis=(1, 2)))
        Yp, Sp, Rp = Y[-2:], rs[-2:], rv[-2:]
    out = {}
    bset = {rec['f'] for rec in plan.boundaries}
    for name, (u, d_), limit in (('general', (up, dn), q['flash_limit_hz']), ('red', (rup, rdn), q['red_flash_limit_hz'])):
        tr = transitions(u, d_, area)
        per = window_flashes(tr, n, win)
        worst = int(per.max()) if len(per) else 0
        at = int(np.argmax(per)) if worst > 0 else None
        over = np.zeros(n, bool)
        for s in np.where(per > limit)[0]:
            over[s:s + win] = True
        src = {'ops': 0, 'cuts': 0, 'content': 0}
        for f, _ in tr:
            if plan.op_any[f] or plan.op_any[f - 1]:
                src['ops'] += 1
            elif f in bset or f - 1 in bset or f + 1 in bset:
                src['cuts'] += 1
            else:
                src['content'] += 1
        alt = alternating(tr)
        onsets = [alt[i][0] for i in range(0, len(alt) - 1, 2)]
        gaps = np.diff(onsets).tolist() if len(onsets) > 1 else []
        w1 = min(n - 1, at + win - 1) if at is not None else None
        out[name] = dict(limit_hz=limit, transitions=len(tr), flashes=len(alt) // 2, worst_per_s=worst,
                         worst_window=[at, w1] if at is not None else None,
                         worst_t=[r(at / fps, 2), r((w1 + 1) / fps, 2)] if at is not None else None,
                         over_limit_ranges=[list(x) for x in runs(over)], seconds_over_limit=r(over.sum() / fps, 2),
                         transition_frames=[[f, d] for f, d in tr], min_gap_frames=int(min(gaps)) if gaps else None,
                         transition_source=src, fail=bool(worst > limit))
    status = 'fail' if out['general']['fail'] or out['red']['fail'] else 'ok'
    return check(status, area=area, delta=delta, **out)


# ============================================================================ 6 safe zone
def safe_zone_box(q, canvas):
    sz = q.get('safe_zone', 'tiktok')
    if isinstance(sz, dict):
        return dict(x0=float(sz.get('x0', 0)), x1=float(sz.get('x1', 1)), y0=float(sz.get('y0', 0)),
                    y1=float(sz.get('y1', 1))), 'custom'
    if sz in (None, 'none', False):
        return None, 'none'
    name = str(sz)
    if canvas['w'] > canvas['h'] and name == 'tiktok':
        name = 'title_safe'                         # the 9:16 UI zone does not apply to landscape canvases
    return dict(SAFE_ZONES.get(name, SAFE_ZONES['tiktok'])), name


def ink_box(alpha, thr=0.12):
    ys, xs = np.where(alpha > thr)
    if not len(xs):
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def read_boxes_sidecar(path, canvas):
    """Renderer sidecar <render>.boxes.json -> {id: [(frame, [x0, y0, x1, y1] canvas px, kind | None, flags tuple)]}.
    Entries: [x0, y0, x1, y1, id, (kind), (flags...)] or {"box"|"bbox": [...], "id", "kind", "opaque": bool,
    "full": bool, "op": bool} (flags: 'opaque', 'full', 'op')."""
    sc = json.load(open(path))
    sw, sh = sc.get('canvas', [canvas['w'], canvas['h']])
    kx, ky = canvas['w'] / float(sw), canvas['h'] / float(sh)
    per = {}
    for f, bxs in (sc.get('frames') or {}).items():
        for bx in bxs:
            if isinstance(bx, dict):
                b = bx.get('box') or bx.get('bbox')
                key, kind = str(bx.get('id', 'layer')), bx.get('kind')
                flags = tuple(sorted(k for k in ('opaque', 'full', 'op') if bx.get(k)))
            else:
                b = bx[:4]
                key = str(bx[4]) if len(bx) > 4 else 'layer'
                kind = bx[5] if len(bx) > 5 and isinstance(bx[5], str) else None
                flags = tuple(sorted(str(x) for x in bx[6:] if isinstance(x, str)))
            if not b or len(b) < 4:
                continue
            per.setdefault(key, []).append((int(f), [b[0] * kx, b[1] * ky, b[2] * kx, b[3] * ky], kind, flags))
    return per


def sidecar_frames(video, canvas):
    """{layer id: [frames on screen]} from the boxes sidecar (None when absent)."""
    side = os.path.splitext(video)[0] + '.boxes.json'
    if not os.path.exists(side):
        return None
    try:
        return {k: [x[0] for x in v] for k, v in read_boxes_sidecar(side, canvas).items()}
    except (OSError, ValueError, IndexError, TypeError, KeyError):
        return None


def text_boxes(edl, scale, video):
    """Ink boxes (canvas px) of every text item / layer over its frame range."""
    cv_ = edl['canvas']
    W, H = int(round(cv_['w'] * scale)), int(round(cv_['h'] * scale))
    items, notes = [], []
    if edl.get('texts'):
        if E is None:
            notes.append(f'ed_edl not importable ({_EDL_IMPORT_ERROR}); texts not rasterised')
        else:
            tl = E.TextLayer(W, H, scale)
            for bi, tb in enumerate(edl['texts']):
                for ii, it in enumerate(tb.get('items', [])):
                    try:
                        grp = tl.groups([it])
                    except Exception as e:  # font missing etc.
                        notes.append(f'text {bi}.{ii}: {e!r}')
                        continue
                    a = np.max(np.concatenate([g[3] for g in grp], axis=-1), axis=-1) if grp else np.zeros((H, W))
                    bb = ink_box(a)
                    if bb is None:
                        continue
                    items.append(dict(kind='text', id=f'texts[{bi}].items[{ii}]', text=it.get('text', ''), f0=int(tb['f0']),
                                      f1=int(tb['f1']), box=[round(v / scale, 1) for v in bb]))
    layers = edl.get('layers') or []
    side = os.path.splitext(video)[0] + '.boxes.json'
    if layers and os.path.exists(side):
        try:
            per = read_boxes_sidecar(side, cv_)
            by_id = {str(L.get('id', f'layers[{i}]')): L for i, L in enumerate(layers)}
            for key, lst in per.items():
                L = by_id.get(key, {})
                run = None
                for f, bx, kind, flags in sorted(lst, key=lambda x: x[0]):
                    if run and f == run['f1'] + 1 and max(abs(a - b) for a, b in zip(bx, run['box'])) <= 1.0 \
                            and flags == run.get('flags'):
                        run['f1'] = f
                        continue
                    run = dict(kind='layer', id=key, layer_kind=kind or L.get('kind'), text=str(L.get('text', ''))[:40],
                               f0=f, f1=f, box=[round(v, 1) for v in bx])
                    if flags:
                        run['flags'] = flags
                    items.append(run)
            layers = []
            notes.append(f'layer boxes read from {os.path.basename(side)}')
        except (OSError, ValueError, IndexError, TypeError, KeyError) as e:
            notes.append(f'sidecar {side} unreadable: {e!r}')
    if layers:
        try:
            import ed_text as T
        except Exception:
            T = None
            notes.append(f'{len(layers)} layers present but ed_text is not importable; layers not checked')
        if T is not None:
            ls = min(scale, 0.5)
            lw_, lh_ = int(round(cv_['w'] * ls)), int(round(cv_['h'] * ls))
            for li, ly in enumerate(layers):
                f0, f1 = int(ly.get('f0', 0)), int(ly.get('f1', ly.get('f0', 0)))
                step = max(1, (f1 - f0) // 24)
                for f in sorted(set(range(f0, f1 + 1, step)) | {f1}):
                    try:
                        res = T.render_layer(ly, f, cv_['fps'], lw_, lh_, ls)
                    except Exception as e:
                        notes.append(f'layer {li} frame {f}: {e!r}')
                        break
                    if not res:
                        continue
                    bb = ink_box(np.asarray(res[0])[..., 3])
                    if bb:
                        items.append(dict(kind='layer', id=f'layers[{li}]:{ly.get("kind")}', text=str(ly.get('text', ''))[:40],
                                          f0=f, f1=min(f1, f + step - 1), box=[round(v / ls, 1) for v in bb]))
    return items, notes


def analyse_safe_zone(edl, q, scale, video, n):
    cv_ = edl['canvas']
    zone, name = safe_zone_box(q, cv_)
    items, notes = text_boxes(edl, scale, video)
    if zone is None:
        return check('skipped', zone=name, items=len(items), notes=notes)
    if not items:
        return check('ok' if not notes else 'skipped', zone=name, zone_box=zone, items=0, notes=notes)
    W, H = cv_['w'], cv_['h']
    zx0, zx1, zy0, zy1 = zone['x0'] * W, zone['x1'] * W, zone['y0'] * H, zone['y1'] * H
    hidden = set()                                  # frames covered by an opaque op drawn over the text (stage post)
    for op in edl.get('ops') or []:
        if op.get('stage') == 'post' and op.get('op') in ('white', 'black', 'flash'):
            fl = frange(op.get('f'))
            curve = op.get('curve') or [1.0]
            for i, f in enumerate(fl):
                a = float(op.get('a', 1.0)) * (float(curve[min(i, len(curve) - 1)]) if op['op'] == 'flash' else 1.0)
                if a >= 0.9:
                    hidden.add(f)
    bad, exempt = [], {}
    frames_bad = np.zeros(n, bool)
    for it in items:
        x0, y0, x1, y1 = it['box']
        it['box_frac'] = [r(x0 / W), r(y0 / H), r(x1 / W), r(y1 / H)]
        bleed_x = x0 <= 0.02 * W and x1 >= 0.98 * W
        bleed_y = y0 <= 0.02 * H and y1 >= 0.98 * H
        flags = set(it.get('flags') or ())
        why = None
        if 'op' in flags or str(it.get('id', '')).startswith('op') or it.get('layer_kind') == 'op':
            why = 'frame op'
        elif (bleed_x and bleed_y) or 'full' in flags or ('opaque' in flags and (bleed_x or bleed_y)):
            why = 'full frame'                      # backgrounds, inverted / flashed frames, cards: not text placement
        elif hidden and all(f in hidden for f in range(int(it['f0']), int(it['f1']) + 1)):
            why = 'hidden by an opaque op'
        if why:
            it['exempt'] = why
            exempt[why] = exempt.get(why, 0) + 1
            continue
        over = {k: round(v, 1) for k, v in (('left', zx0 - x0), ('right', x1 - zx1), ('top', zy0 - y0),
                                              ('bottom', y1 - zy1)) if v > 0.5
                and not (bleed_x and k in ('left', 'right')) and not (bleed_y and k in ('top', 'bottom'))}
        if bleed_x or bleed_y:
            it['full_bleed'] = 'x' if bleed_x else 'y'   # an edge-to-edge band: only the other axis is checked
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            it['off_canvas'] = True
        if over:
            it['outside_px'] = over
            bad.append(it)
            frames_bad[max(0, it['f0']):min(n, it['f1'] + 1)] = True
    return check('fail' if bad else 'ok', zone=name, zone_box=zone, items=len(items), violations=bad,
                 frames_outside=[list(x) for x in runs(frames_bad)], n_frames_outside=int(frames_bad.sum()), notes=notes,
                 exempt=exempt, all_items=items)


# ============================================================================ 7 faces
class FaceDet:
    def __init__(self):
        self.d = None

    def __call__(self, rgb):
        h, w = rgb.shape[:2]
        if self.d is None:
            self.d = cv2.FaceDetectorYN.create(os.path.join(V.MODELS, 'face_detection_yunet_2023mar.onnx'), '', (w, h),
                                               0.7, 0.3, 50)
        self.d.setInputSize((w, h))
        _, f = self.d.detect(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        out = []
        for row in (f if f is not None else []):
            out.append(dict(x=float(row[0]), y=float(row[1]), w=float(row[2]), h=float(row[3]), score=float(row[-1])))
        return sorted(out, key=lambda d: -d['w'] * d['h'])


def face_samples(plan, nv):
    """Render frames to check for faces: middle of every segment (+ near both ends of long ones), not on op frames."""
    out = {}
    for si, sg in enumerate(plan.segs):
        f0, f1 = max(0, int(sg['f0'])), min(nv, plan.n) - 1 if int(sg['f1']) >= min(nv, plan.n) else int(sg['f1'])
        if f1 < f0:
            continue
        want = [(f0 + f1) // 2] + ([f0 + 3, f1 - 3] if f1 - f0 >= 45 else [])
        for f in want:
            for d in (0, 1, -1, 2, -2, 3, -3):
                g = f + d
                if f0 <= g <= f1 and not plan.op_any[g]:
                    out[g] = si
                    break
    return out


def analyse_faces_render(full, samples, plan, text_items, scale):
    det = FaceDet()
    issues, n_faces, overlaps = [], 0, []
    for f in sorted(samples):
        fr = full.get(f)
        if fr is None:
            continue
        h, w = fr.shape[:2]
        s = 320.0 / w if w > 320 else 1.0       # faces that matter in a 9:16 crop are >= 8 % of the width
        sm = cv2.resize(fr, (int(round(w * s)), int(round(h * s))), interpolation=cv2.INTER_AREA) if s < 1 else fr
        faces = [dict(x=d['x'] / s, y=d['y'] / s, w=d['w'] / s, h=d['h'] / s, score=d['score']) for d in det(sm)]
        faces = [d for d in faces if d['score'] >= 0.75 and d['w'] >= 0.08 * w]
        n_faces += len(faces)
        for d in faces:
            sides = [k for k, v in (('left', d['x'] < 2), ('top', d['y'] < 2), ('right', d['x'] + d['w'] > w - 2),
                                    ('bottom', d['y'] + d['h'] > h - 2)) if v]
            if sides:
                vis_w = min(w, d['x'] + d['w']) - max(0, d['x'])
                vis_h = min(h, d['y'] + d['h']) - max(0, d['y'])
                cut = 1 - max(0, vis_w) * max(0, vis_h) / max(1.0, d['w'] * d['h'])
                # close-ups (face >= half the frame width) are cut by design; a few % at the edge is not a cut face
                if cut >= 0.15 and d['w'] < 0.5 * w:
                    issues.append(dict(f=f, seg=plan.seg_id(f), sides=sides, face_frac_outside=r(cut, 2),
                                       box=[r(d['x'] / w), r(d['y'] / h), r((d['x'] + d['w']) / w), r((d['y'] + d['h']) / h)]))
            for it in text_items:
                if it['f0'] <= f <= it['f1']:
                    x0, y0, x1, y1 = [v * scale for v in it['box']]
                    ix = max(0, min(x1, d['x'] + d['w']) - max(x0, d['x']))
                    iy = max(0, min(y1, d['y'] + d['h']) - max(y0, d['y']))
                    if ix * iy > 0.15 * d['w'] * d['h']:
                        overlaps.append(dict(f=f, seg=plan.seg_id(f), text=it.get('text', '')[:30], id=it['id']))
    return dict(frames_checked=len(samples), faces=n_faces, edge_cut=issues, text_over_face=overlaps)


def source_requests(plan, nv, min_frames=6, cap=None):
    """One source frame per segment (middle) for the crop-vs-subject check. Long segments first when capped
    (default cap: 1.5 per second of edit, at least 16, so the check stays well under realtime)."""
    edl = plan.edl
    if (edl.get('meta') or {}).get('crop_model') == 'ed_render' or E is None:
        return []
    if cap is None:
        cap = int(max(16, 1.5 * plan.n / plan.fps))
    srcs = edl.get('sources') or {}
    reqs = []
    gaps = getattr(plan, 'gap_segs', None) or set()
    for si, sg in enumerate(plan.segs):
        n = int(sg['f1']) - int(sg['f0']) + 1
        if n < min_frames or int(sg['f0']) >= min(nv, plan.n) or si in gaps:
            continue
        cfg = srcs.get(sg.get('src', 'film'))
        if not cfg or not os.path.exists(cfg.get('path', '')):
            continue
        k = n // 2
        reqs.append(dict(si=si, k=k, n=n, src=sg.get('src', 'film'), t=seg_times(sg, plan.fps)[k]))
    reqs.sort(key=lambda d: -d['n'])
    return reqs[:cap]


def renderer_time(t, sfps):
    """Source frame time the renderer shows for source time t (ed_edl.Source.span(t - .02, ..) + nearest pick)."""
    first = math.ceil((t - 0.02) * sfps - 1e-4) / sfps
    k = max(0, int(round((t - first) * sfps)))
    return first + k / sfps


def stream_start(path):
    try:
        out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=start_time',
                              '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip().split('\n')[0]
        return float(out)
    except ValueError:
        return 0.0


def fetch_source_frames(reqs, sources, width=720):
    """Decode the requested source frames (picture box only). One persistent OpenCV decoder per source; the frame
    shown by the renderer at time rt (= its pts) is decoder index round((rt - stream start) * fps). Falls back to
    ffmpeg calls (clustered by time) when OpenCV cannot read the file."""
    out, info_cache = {}, {}
    by_src = {}
    for i, rq in enumerate(reqs):
        by_src.setdefault(rq['src'], []).append((rq['t'], i))
    for name, lst in by_src.items():
        cfg = sources[name]
        path = cfg['path']
        if path not in info_cache:
            info_cache[path] = V.probe(path)
        inf = info_cache[path]
        sfps = float(cfg.get('fps') or inf['fps'] or 25.0)
        box = cfg.get('box') or [0, 0, inf['w'], inf['h']]
        bw, bh = box[2] - box[0], box[3] - box[1]
        ow = min(width, bw)
        oh = int(round(bh * ow / bw / 2)) * 2
        lst.sort()
        cap = cv2.VideoCapture(path, cv2.CAP_FFMPEG)
        if cap.isOpened():
            st0 = stream_start(path)
            pos = None
            for t, i in lst:
                idx = int(round((renderer_time(t, sfps) - st0) * sfps))
                if pos is None or not (0 <= idx - pos <= 48):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                    pos = idx
                while pos < idx and cap.grab():
                    pos += 1
                ok, fr = cap.read()
                if not ok:
                    pos = None
                    continue
                pos += 1
                fr = cv2.cvtColor(fr[box[1]:box[3], box[0]:box[2]], cv2.COLOR_BGR2RGB)
                out[i] = dict(frame=cv2.resize(fr, (ow, oh), interpolation=cv2.INTER_AREA), scale=ow / bw, box_wh=(bw, bh))
            cap.release()
            lst = [(t, i) for t, i in lst if i not in out]
            if not lst:
                continue
        clusters, cur = [], [lst[0]]
        for item in lst[1:]:
            if item[0] - cur[-1][0] <= 2.0:
                cur.append(item)
            else:
                clusters.append(cur)
                cur = [item]
        clusters.append(cur)
        for cl in clusters:
            t0 = max(0.0, cl[0][0] - 0.02)
            dur = cl[-1][0] - t0 + 1.5 / sfps
            cmd = ['ffmpeg', '-v', 'error', '-nostdin', '-threads', '1', '-ss', f'{t0:.4f}', '-i', path, '-t', f'{dur:.4f}',
                   '-an', '-vf', f'crop={bw}:{bh}:{box[0]}:{box[1]},scale={ow}:{oh}:flags=area', '-f', 'rawvideo',
                   '-pix_fmt', 'rgb24', '-']
            raw = subprocess.run(cmd, capture_output=True).stdout
            k = len(raw) // (ow * oh * 3)
            if k == 0:
                continue
            frs = np.frombuffer(raw[:k * ow * oh * 3], np.uint8).reshape(k, oh, ow, 3)
            first = math.ceil(t0 * sfps - 1e-4) / sfps
            st = first + np.arange(k) / sfps
            for t, i in cl:
                j = int(np.argmin(np.abs(st - t)))
                out[i] = dict(frame=frs[j].copy(), scale=ow / bw, box_wh=(bw, bh))
    return out


def source_job(plan, reqs, canvas):
    """Background job: decode the source frames and compare their main face with the crop windows."""
    t0 = time.time()
    got = fetch_source_frames(reqs, plan.edl.get('sources') or {})
    rows, issues = analyse_subject(plan, reqs, got, canvas)
    return rows, issues, got, round(time.time() - t0, 2)


def analyse_subject(plan, reqs, got, canvas):
    det = FaceDet()              # own detector instance: runs in a worker thread
    rows, issues = [], []

    class _S:  # minimal stand-in for ed_edl.Source (box size only) for E.window
        pass

    for i, rq in enumerate(reqs):
        g = got.get(i)
        if g is None:
            continue
        sg = plan.segs[rq['si']]
        S = _S()
        S.w, S.h = g['box_wh']
        c = crop_at(sg, rq['k'])
        cx, cy, ww, hw = E.window(S, c, canvas['w'], canvas['h'])
        win = [max(0, cx - ww / 2), max(0, cy - hw / 2), min(S.w, cx + ww / 2), min(S.h, cy + hw / 2)]
        s = g['scale']
        faces = [dict(x=d['x'] / s, y=d['y'] / s, w=d['w'] / s, h=d['h'] / s, score=d['score']) for d in det(g['frame'])]
        faces = [d for d in faces if d['score'] >= 0.75 and d['w'] >= 0.025 * S.w]
        row = dict(seg=sg.get('id'), f=int(sg['f0']) + rq['k'], src_t=r(rq['t'], 3), window=[r(v, 1) for v in win],
                   faces=len(faces))
        if faces:
            m = faces[0]
            ix = max(0, min(win[2], m['x'] + m['w']) - max(win[0], m['x']))
            iy = max(0, min(win[3], m['y'] + m['h']) - max(win[1], m['y']))
            cov = ix * iy / max(1.0, m['w'] * m['h'])
            row.update(main_face=[r(m['x'], 1), r(m['y'], 1), r(m['x'] + m['w'], 1), r(m['y'] + m['h'], 1)], coverage=r(cov, 2))
            others_in = [d for d in faces[1:] if d['w'] * d['h'] >= 0.5 * m['w'] * m['h']
                         and d['x'] >= win[0] and d['x'] + d['w'] <= win[2]]
            if m['w'] >= 0.8 * (win[2] - win[0]) or m['h'] >= 0.8 * (win[3] - win[1]):
                row['status'] = 'ok'
                row['note'] = 'face about as large as the crop window (close-up): cut by design'
            elif cov < 0.15 and not others_in:
                row['status'] = 'subject_lost'
            elif 0.15 <= cov < 0.85:
                row['status'] = 'subject_cut'
            else:
                row['status'] = 'ok'
            if row['status'] != 'ok':
                issues.append(dict(row, _i=i))
        else:
            row['status'] = 'no_face'
        rows.append(row)
    return rows, issues


# ============================================================================ parts of a composite edit
TALK_TYPES = {'talk', 'speech', 'interview', 'podcast', 'voice', 'dialogue', 'monologue'}
SUB_KINDS = {'subtitle', 'subtitles', 'karaoke', 'caption', 'captions'}


def _resolve(p, base):
    """Relative media paths: as given when they exist (renderer CWD), else relative to `base` (project / EDL dir)."""
    if not p or os.path.isabs(p) or os.path.exists(p) or not base:
        return p
    alt = os.path.join(base, p)
    return alt if os.path.exists(alt) else p


def _same_file(a, b):
    try:
        return bool(a) and bool(b) and os.path.realpath(a) == os.path.realpath(b)
    except (TypeError, ValueError):
        return False


def edl_parts(edl, q, n, edl_dir):
    """Parts of the edit -> (parts, talk sources). Declared: meta.parts [{id, type, f0, f1}] (type talk | speech |
    interview | podcast -> 'talk', 'clip' -> 'clip' (a source fragment: word rules only), anything else, e.g.
    'edit', -> 'music'). Inferred otherwise: frames where
    audio.voice plays from a file that is also a picture source (sync sound: the speaker is on screen) are talk, the
    rest music (snapped to segments); a speech genre without such voice entries is one talk part; anything else is one
    music part. Talk sources: sources of that sync voice, else the sources covering >= 30 % of the talk frames."""
    segs = edl.get('segments') or []
    meta = edl.get('meta') or {}
    au = edl.get('audio') or {}
    srcs = edl.get('sources') or {}
    fps = float(edl['canvas']['fps'])
    base = au.get('base_dir') or edl_dir
    src_path = {name: _resolve(cfg.get('path'), edl_dir) for name, cfg in srcs.items() if isinstance(cfg, dict)}
    sync = []
    for v in au.get('voice') or []:
        if isinstance(v, dict) and v.get('path'):
            vp = _resolve(v['path'], base)
            names = {nm for nm, sp in src_path.items() if _same_file(sp, vp)}
            if names:
                a = float(v.get('at', 0.0))
                b = a + float(v['dur']) if v.get('dur') else n / fps
                sync.append((int(round(a * fps)), min(n - 1, int(round(b * fps)) - 1), names))
    talk_src = set().union(*[s[2] for s in sync]) if sync else set()
    parts = []
    declared = meta.get('parts') if isinstance(meta.get('parts'), list) and meta.get('parts') else None
    if declared:
        for i, p in enumerate(declared):
            try:
                f0, f1 = int(p['f0']), int(p['f1'])
            except (KeyError, TypeError, ValueError):
                continue
            raw = str(p.get('type', 'edit')).lower()
            typ = 'talk' if raw in TALK_TYPES else ('clip' if raw == 'clip' else 'music')
            item = dict(id=str(p.get('id', f'part{i + 1}')), type=typ, raw_type=raw, f0=f0, f1=f1, declared=True)
            # ed_sequence extras: the edit part's genre / house style / version, where its drop must land, its sections
            for k in ('genre', 'style', 'variant', 'engine'):
                if p.get(k) is not None and isinstance(p.get(k), (str, int, float)):
                    item[k] = p[k]
            if p.get('tighten_pauses'):                    # a talk part whose pauses the edit shortens
                item['tighten_pauses'] = p['tighten_pauses']
            try:
                if p.get('drop_frame') is not None:
                    item['drop_frame'] = int(p['drop_frame'])
            except (TypeError, ValueError):
                pass
            if isinstance(p.get('sections'), dict):
                item['sections'] = {str(k): v for k, v in p['sections'].items() if isinstance(v, (list, tuple)) and len(v) == 2}
            parts.append(item)
    elif sync:
        merged = []
        for a, b, _ in sorted(sync, key=lambda s: s[0]):
            if merged and a <= merged[-1][1] + int(0.5 * fps) + 1:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        for sg in sorted(segs, key=lambda s: s['f0']):
            f0, f1 = int(sg['f0']), int(sg['f1'])
            inside = sum(max(0, min(f1, b) - max(f0, a) + 1) for a, b in merged)
            t = 'talk' if inside >= 0.5 * (f1 - f0 + 1) else 'music'
            if parts and parts[-1]['type'] == t:
                parts[-1]['f1'] = max(parts[-1]['f1'], f1)
            else:
                k = sum(1 for p in parts if p['type'] == t) + 1
                parts.append(dict(id=f'{t}{k}', type=t, raw_type=t, f0=f0, f1=f1, declared=False))
    elif q.get('mode') == 'speech':
        parts = [dict(id='talk1', type='talk', raw_type='speech', f0=0, f1=n - 1, declared=False)]
    if not parts:
        parts = [dict(id='edit1', type='music', raw_type='music', f0=0, f1=n - 1, declared=False)]
    parts.sort(key=lambda p: p['f0'])
    for p in parts:
        p['segs'] = [i for i, sg in enumerate(segs) if p['f0'] <= int(sg['f0']) <= p['f1']]
    if not talk_src:
        cover = {}
        for p in parts:
            if p['type'] == 'talk':
                for i in p['segs']:
                    sg = segs[i]
                    cover[sg.get('src', 'film')] = cover.get(sg.get('src', 'film'), 0) + int(sg['f1']) - int(sg['f0']) + 1
        tot = sum(cover.values())
        talk_src = {s for s, c in cover.items() if tot and c >= 0.3 * tot}
    return parts, talk_src


def part_at(parts, f):
    for p in parts:
        if p['f0'] <= f <= p['f1']:
            return p
    return None


# ============================================================================ audio references (music / voice / stems)
SR_A = 48000
_KW_B = (np.array([1.53512485958697, -2.69169618940638, 1.19839281085285]),
         np.array([1.0, -2.0, 1.0]))
_KW_A = (np.array([1.0, -1.69065929318241, 0.73248077421585]),
         np.array([1.0, -1.99004745483398, 0.99007225036621]))


def decode_audio(path, sr=SR_A, start=0.0, dur=None, speed=1.0):
    """Any audio / video file -> float32 (N, 2) at sr (ffmpeg; from `start` s, `dur` s of output; speed != 1 =
    resampled like ed_sfx: pitch follows). Empty array when there is no audio."""
    cmd = ['ffmpeg', '-v', 'error', '-nostdin']
    if start and start > 0:
        cmd += ['-ss', f'{start:.4f}']
    cmd += ['-i', path]
    if dur:
        cmd += ['-t', f'{dur * (speed or 1.0):.4f}']
    af = [f'asetrate={sr * speed:.3f}', f'aresample={sr}'] if speed and abs(speed - 1.0) > 1e-6 else []
    cmd += ['-vn', '-ac', '2', '-ar', str(sr)] + (['-af', ','.join(af)] if af else []) + ['-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    y = np.frombuffer(raw[:len(raw) // 8 * 8], np.float32)
    return y.reshape(-1, 2).copy()


def kweight(y):
    """BS.1770 K-weighting (48 kHz coefficients) of a (N, 2) signal."""
    from scipy.signal import lfilter
    out = np.empty_like(y, dtype=np.float64)
    for ch in range(y.shape[1]):
        x = lfilter(_KW_B[0], _KW_A[0], y[:, ch].astype(np.float64))
        out[:, ch] = lfilter(_KW_B[1], _KW_A[1], x)
    return out


class Loud:
    """Sliding K-weighted loudness of a (N, 2) signal: lufs(a, b) for any sample window (cumulative sums)."""

    def __init__(self, y, sr=SR_A):
        self.sr = sr
        k = kweight(y) if len(y) else np.zeros((0, 2))
        self.c = np.concatenate([[0.0], np.cumsum((k * k).sum(1))])
        self.n = len(k)

    def lufs(self, t0, t1):
        a, b = max(0, int(round(t0 * self.sr))), min(self.n, int(round(t1 * self.sr)))
        if b - a < 16:
            return None
        p = (self.c[b] - self.c[a]) / (b - a)
        return -0.691 + 10 * math.log10(p) if p > 1e-12 else -70.0

    def max_momentary(self, t0, t1, win=0.4, hop=0.025):
        """Highest 400 ms loudness among windows whose centre lies in [t0, t1]."""
        best, t = None, t0
        while t <= t1 + 1e-9:
            v = self.lufs(t - win / 2, t + win / 2)
            if v is not None and (best is None or v > best[0]):
                best = (v, t)
            t += hop
        return best


def _place(y, at, N, sr=SR_A):
    out = np.zeros((N, 2), np.float32)
    a = int(round(at * sr))
    if a < N and len(y):
        lo = max(a, 0)
        seg = y[lo - a:lo - a + N - lo]
        out[lo:lo + len(seg)] = seg
    return out


def _read_wav(path):
    from scipy.io import wavfile
    sr, y = wavfile.read(path)
    y = np.asarray(y)
    if y.dtype.kind in 'iu':
        y = y.astype(np.float32) / float(np.iinfo(y.dtype).max)
    y = y.astype(np.float32)
    return sr, (y if y.ndim == 2 else np.repeat(y[:, None], 2, 1))


def _xcorr_lag(a, b, max_lag, sr):
    """Lag (s) of b relative to a (b[t] ~ a[t - lag]) and the normalised peak, on 4 kHz mono envelopes-free signals."""
    from scipy.signal import resample_poly, fftconvolve
    d = max(1, sr // 4000)
    x = resample_poly(a.mean(1), 1, d) if d > 1 else a.mean(1)
    z = resample_poly(b.mean(1), 1, d) if d > 1 else b.mean(1)
    n = min(len(x), len(z))
    x, z = x[:n] - x[:n].mean(), z[:n] - z[:n].mean()
    if n < 64 or not np.any(x) or not np.any(z):
        return None, 0.0
    c = fftconvolve(z, x[::-1], mode='full')[n - 1 - int(max_lag * sr / d):n + int(max_lag * sr / d)]
    i = int(np.argmax(c))
    lag = (i - int(max_lag * sr / d)) * d / sr
    return lag, float(c[i] / (np.sqrt((x * x).sum() * (z * z).sum()) + 1e-12))


class AudioCtx:
    """What the soundtrack of the render is made of, for the speech / parts / sfx checks:
      mix       the rendered audio (decoded from the MP4, 48 kHz stereo) - every verdict is measured on it
      music     the music file placed on the timeline (audio.music in / at / dur / speed; raw level) - drop and beat
                grid; its sync with the mix is verified by cross-correlation
      voices    [(at, samples)] of audio.voice entries (raw level)
      stems     music / voice / sfx after the master gain (ed_sfx.mix debug stems, re-rendered by QA with the same
                audio block: the mix is deterministic) - accepted only when stems x limiter match the MP4 (corr)
      events    ed_sfx.mix placement records (start / end / anchor of every sfx event) from that re-mix."""

    def __init__(self, edl, edl_dir, video, out_dir, n_frames, fps, want_stems=True, log=None):
        self.notes, self.T = [], {}
        self.sr, self.fps = SR_A, fps
        self.N = int(round(n_frames / fps * SR_A))
        au = dict(edl.get('audio') or {})
        self.audio = au
        self.base = au.get('base_dir') or edl_dir
        t0 = time.time()
        self.mix = decode_audio(video)[:self.N]
        if len(self.mix) < self.N:
            self.mix = np.concatenate([self.mix, np.zeros((self.N - len(self.mix), 2), np.float32)])
        self.T['decode_mix'] = round(time.time() - t0, 2)
        self.music, self.music_cfg, self.voices = None, None, []
        self.stems, self.events, self.mix_info = None, None, None
        self.gain, self.stems_corr, self.stems_lag = None, None, None
        self.sync = None
        m = au.get('music') or (dict(path=au['path']) if au.get('path') and not au.get('copy') else None)
        if au.get('copy') and au.get('path'):
            m = None                                  # reference audio muxed as is: no separate music
        if m and m.get('path'):
            p = _resolve(m['path'], self.base)
            if os.path.exists(p):
                sp = float(m.get('speed', 1.0) or 1.0)
                at = float(m.get('at', 0.0))
                need = self.N - int(round(at * SR_A))
                if m.get('dur'):
                    need = min(need, int(round(float(m['dur']) * SR_A)))
                if need > 0:
                    y = decode_audio(p, start=float(m.get('in', 0.0)), dur=need / SR_A + 0.05, speed=sp)[:need]
                    self.music = _place(y, at, self.N)
                    self.music_cfg = dict(path=p, t_in=float(m.get('in', 0.0)), at=at, speed=sp)
        for v in au.get('voice') or []:
            if isinstance(v, dict) and v.get('path'):
                p = _resolve(v['path'], self.base)
                if os.path.exists(p):
                    at = float(v.get('at', 0.0))
                    dur = float(v['dur']) if v.get('dur') else max(0.0, self.N / SR_A - at)
                    y = decode_audio(p, start=float(v.get('in', 0.0)), dur=dur)
                    self.voices.append((at, y[:int(round(dur * SR_A))]))
        self.T['decode_refs'] = round(time.time() - t0, 2)
        if self.music is not None:
            lag, peak = _xcorr_lag(self.music, self.mix, 0.25, SR_A)
            self.sync = dict(lag_ms=r(lag * 1000 if lag is not None else None, 1), corr=r(peak, 3))
        if want_stems and not au.get('copy') and (au.get('sfx') or (au.get('voice') and self.music is not None)):
            self._stems(edl, out_dir)

    def voice_track(self):
        out = np.zeros((self.N, 2), np.float32)
        for at, y in self.voices:
            out += _place(y, at, self.N)
        return out

    def _align(self, pred, max_lag=256):
        """Sample lag of the decoded MP4 audio against the re-mix (AAC priming): searched on the loudest 2 s, then the
        mix is shifted so that residuals (mix - stems) are meaningful. -> lag in samples (applied)."""
        m = pred.mean(1)
        x = self.mix.mean(1)
        w = 2 * SR_A
        if len(m) < w + 2 * max_lag:
            return 0
        e = np.convolve(m * m, np.ones(SR_A // 10, np.float32), mode='valid')[::SR_A // 20]
        c = int(np.argmax(e)) * (SR_A // 20) + SR_A // 20
        c = min(max(c, max_lag), len(m) - w - max_lag)
        ref = m[c:c + w].astype(np.float64)
        best, lag = -np.inf, 0
        for L in range(-max_lag, max_lag + 1):
            v = float(np.dot(ref, x[c + L:c + L + w]))
            if v > best:
                best, lag = v, L
        if lag:
            self.mix = np.roll(self.mix, -lag, axis=0)
            if lag > 0:
                self.mix[-lag:] = 0
            else:
                self.mix[:-lag] = 0
        return lag

    def _stems(self, edl, out_dir):
        """Re-run ed_sfx.mix with debug stems (same audio block -> same mix), verify against the MP4."""
        t0 = time.time()
        try:
            import ed_sfx as X
        except Exception as e:  # mixer unavailable: no stems
            self.notes.append(f'ed_sfx not importable ({e!r}): no stems')
            return
        import copy
        import shutil
        work = os.path.join(out_dir, '_qa_stems')
        os.makedirs(work, exist_ok=True)
        try:
            au = copy.deepcopy(self.audio)
            if not au.get('base_dir'):
                au['base_dir'] = self.base
            genre = (edl.get('meta') or {}).get('genre')
            if genre and not au.get('genre'):
                au['genre'] = genre                      # as ed_edl.build_audio: meta.genre picks the sfx style
            au['debug'] = dict(au.get('debug') or {}, stems=work)
            info = X.mix(au, self.N / SR_A, os.path.join(work, 'mix.wav'), sr=SR_A)
            st = {}
            for name in ('music', 'voice', 'sfx'):
                p = os.path.join(work, f'{name}.wav')
                if os.path.exists(p):
                    sr, y = _read_wav(p)
                    if sr == SR_A:
                        y = y[:self.N]
                        st[name] = np.concatenate([y, np.zeros((self.N - len(y), 2), np.float32)]) if len(y) < self.N else y
            gp = os.path.join(work, 'limiter_gr_db.npy')
            gr = np.load(gp)[:self.N] if os.path.exists(gp) else None
            if not st:
                self.notes.append('ed_sfx.mix wrote no stems')
                return
            for name in ('music', 'voice', 'sfx'):
                st.setdefault(name, np.zeros((self.N, 2), np.float32))
            gain = np.ones(self.N, np.float32)
            if gr is not None and len(gr) >= 1:
                gain[:len(gr)] = (10 ** (-np.asarray(gr, np.float64)[:self.N] / 20.0)).astype(np.float32)
            pred = (st['music'] + st['voice'] + st['sfx']) * gain[:, None]
            lag = self._align(pred)

            def _corr(a, b):
                a, b = a - a.mean(), b - b.mean()
                return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
            corr = _corr(pred.mean(1), self.mix.mean(1))
            accept = corr >= 0.95
            self.mix_info = {k: v for k, v in (info or {}).items() if k != 'events'}
            self.events = (info or {}).get('events')
            if not accept and self.events:
                # the sfx may differ (another mixer version) while music and voice still match: judge those alone,
                # outside the events; each event is then verified on its own span (analyse_sfx)
                keep = np.ones(self.N, bool)
                for e in self.events:
                    if isinstance(e, dict) and e.get('start') is not None and e.get('end') is not None:
                        keep[max(0, int((float(e['start']) - 0.3) * SR_A)):max(0, int((float(e['end']) + 0.3) * SR_A))] = False
                if keep.sum() > SR_A:
                    other = ((st['music'] + st['voice']) * gain[:, None]).mean(1)
                    self.stems_corr_outside_sfx = _corr(other[keep], self.mix.mean(1)[keep])
                    if self.stems_corr_outside_sfx >= 0.95:
                        accept = True
                        self.notes.append(f're-mixed sfx differ from the render (mix corr {corr:.3f}), music / voice match '
                                          f'({self.stems_corr_outside_sfx:.3f}): sfx verified per event')
            self.stems_corr, self.stems_lag = corr, lag
            if accept:
                self.stems, self.gain = st, gain
            else:
                self.notes.append(f're-mixed stems do not match the rendered audio (corr {corr:.3f}): the render was '
                                  f'mixed from another audio block or mixer version; stems not used')
        except Exception as e:  # any mixer failure: measure without stems
            self.notes.append(f're-mix for stems failed: {e!r}')
        finally:
            shutil.rmtree(work, ignore_errors=True)
            self.T['stems'] = round(time.time() - t0, 2)


def music_grid(actx, log=None):
    """Beat grid of the placed music in timeline seconds: ed_audio.analyze of the whole music file (an excerpt can
    lock to a wrong tempo), mapped through in / at / speed."""
    if actx is None or actx.music_cfg is None:
        return None
    try:
        import ed_audio as A
        mc = actx.music_cfg
        hint = ((actx.audio.get('grid') or {}).get('bpm'))
        an = A.analyze(mc['path'], bpm_hint=hint) if hint else A.analyze(mc['path'])
    except Exception as e:  # analysis failure: no grid
        return {'error': repr(e)}
    sp = mc['speed'] or 1.0
    tl = lambda t: (t - mc['t_in']) / sp + mc['at']  # noqa: E731
    dur = actx.N / SR_A
    out = dict(an)
    out['beats'] = [round(tl(t), 4) for t in an.get('beats', []) if -1.0 <= tl(t) <= dur + 1.0]
    out['downbeats'] = [round(tl(t), 4) for t in an.get('downbeats', []) if -4.0 <= tl(t) <= dur + 4.0]
    out['bpm'] = round(float(an.get('bpm', 0)) * sp, 2) if an.get('bpm') else an.get('bpm')
    out['source'] = 'music file'
    out['envelope'] = an.get('envelope') or {}
    out['envelope_offset'] = tl(0.0)
    out['envelope_speed'] = sp
    return out


# ============================================================================ drop on a part boundary
def drop_strengths(music, sr, downbeats, bar):
    """Per downbeat: sustained energy jump (dB) = power over the next 1 and 2 bars over the previous ones (means of
    the two), full band plus half the 30-150 Hz band (sections and drops start on a downbeat with more low end)."""
    from scipy.signal import butter, sosfilt
    m = (music.mean(1) if music.ndim == 2 else music).astype(np.float64)
    bands = ((np.concatenate([[0.0], np.cumsum(m * m)]), 1.0),
             (np.concatenate([[0.0], np.cumsum(sosfilt(butter(2, [30, 150], btype='band', fs=sr, output='sos'), m) ** 2)]), 0.5))
    n = len(m)

    def pw(c, a, b):
        a, b = max(0, a), min(n, b)
        return (c[b] - c[a]) / (b - a) if b - a > sr * 0.05 else None
    out = []
    for d in downbeats:
        i = int(round(d * sr))
        tot, ok = 0.0, True
        for c, w in bands:
            js = []
            for k in (1, 2):
                bb = int(round(k * bar * sr))
                after, before = pw(c, i, i + bb), pw(c, i - bb, i)
                if after is None or before is None:
                    continue
                js.append(10 * math.log10((after + 1e-12) / (before + 1e-12)))
            if not js:
                ok = False
                break
            tot += w * float(np.mean(js))
        out.append(tot if ok else float('nan'))
    return out


def analyse_drop(actx, grid, b, fps, tol_frames=1.0, span_bars=2):
    """The strongest downbeat / drop of the placed music within +-span_bars bars of boundary frame b must land on b
    (+-tol_frames). No clear drop there (strength < 1.5 dB or < 1.3 x the runner-up): the nearest downbeat must."""
    if actx is None or actx.music is None:
        return dict(status='skipped', note='no music in the audio block')
    if not grid or grid.get('error') or not grid.get('downbeats'):
        return dict(status='skipped', note='no beat grid for the music' + (f" ({grid.get('error')})" if grid and grid.get('error') else ''))
    bpm = float(grid.get('bpm') or 120.0)
    bar = 4 * 60.0 / bpm
    tb = b / fps
    dbs = [d for d in grid['downbeats'] if abs(d - tb) <= span_bars * bar + 1e-6]
    if not dbs:
        return dict(status='warn', boundary=b, note='no downbeat of the music near the boundary')
    st = drop_strengths(actx.music, SR_A, dbs, bar)
    cand = sorted([(s, d) for s, d in zip(st, dbs) if np.isfinite(s)], reverse=True)
    near = min(dbs, key=lambda d: abs(d - tb))
    res = dict(boundary=b, boundary_t=r(tb, 3), bpm=r(bpm, 2), candidates=[dict(t=r(d, 3), offset_frames=r((d - tb) * fps, 2),
                                                                              strength_db=r(s, 2)) for s, d in cand[:4]],
               nearest_downbeat=r(near, 3), nearest_offset_frames=r((near - tb) * fps, 2), tol_frames=tol_frames)
    clear = bool(cand) and cand[0][0] >= 1.5 and (len(cand) < 2 or cand[0][0] >= 1.3 * max(cand[1][0], 1e-6))
    if clear:
        d = cand[0][1]
        off = (d - tb) * fps
        res.update(drop_t=r(d, 3), drop_track_t=r((d - actx.music_cfg['at']) * actx.music_cfg['speed'] + actx.music_cfg['t_in'], 3),
                   offset_frames=r(off, 2), strength_db=r(cand[0][0], 2), clear=True)
        res['status'] = 'ok' if abs(off) <= tol_frames + 0.25 else 'fail'
    else:
        off = (near - tb) * fps
        res.update(clear=False, offset_frames=r(off, 2), note='no clear drop near the boundary: checked the nearest downbeat')
        res['status'] = 'ok' if abs(off) <= tol_frames + 0.25 else 'warn'
    return res


# ============================================================================ speech
def _card_number(card_file, pattern):
    if not card_file:
        return None
    try:
        txt = open(os.path.join(HERE, '..', 'genres', card_file), encoding='utf-8').read()
    except OSError:
        return None
    m = re.search(pattern, txt)
    return float(m.group(1)) if m else None


def _text_mod():
    try:
        import ed_text as T
        return T
    except Exception:  # text engine unavailable: the producer's chunks / lines
        return None


def caption_max_lines(L, T=None):
    """Most lines a caption layer shows at full size (ed_text: the layer's / its preset's max_lines, else the kind's
    default - subtitle 3, karaoke 2); a chunk that needs more is split in time by the renderer."""
    kind = str(L.get('kind', '')).lower()
    if T is not None:
        try:
            R = T.resolve_preset(L) if hasattr(T, 'resolve_preset') else L
            if R.get('max_lines') is not None:
                return int(R['max_lines'])
            k = T.kind_of(R) if hasattr(T, 'kind_of') else kind
            v = T.LAYER_KINDS.spec(k)['params'].get('max_lines')
            if v is not None:
                return int(v)
        except Exception:  # unknown preset / kind: the defaults below
            pass
    if L.get('max_lines') is not None:
        return int(L['max_lines'])
    return 2 if kind == 'karaoke' else 3


def subtitle_items(edl, fps, sidecar_frames=None):
    """Caption chunks AS DISPLAYED: every subtitle / karaoke / caption layer goes through ed_text.split_caption_layer
    (the renderer's own reflow up to the layer's max_lines and its split in time of a chunk that still does not fit)
    -> one item per displayed part [{id, f0, f1, text, n_lines, max_lines, dur_s, cps, split, span_from}]; an unsplit
    layer keeps its own chunks / lines (the producer's lines are kept when they fit). Without ed_text: the producer's
    chunks and lines. The on-screen span of an unsplit single-chunk layer is read from the render sidecar boxes."""
    T = _text_mod()
    split_fn = getattr(T, 'split_caption_layer', None) if T is not None else None
    cv_ = edl.get('canvas') or {}
    ow, oh = int(cv_.get('w') or 1080), int(cv_.get('h') or 1920)
    out = []
    for li, L in enumerate(edl.get('layers') or []):
        if not isinstance(L, dict) or str(L.get('kind', '')).lower() not in SUB_KINDS:
            continue
        lid = str(L.get('id', f'layers[{li}]'))
        max_lines = caption_max_lines(L, T)
        parts = None
        if callable(split_fn):
            try:
                parts = split_fn(L, ow, oh, fps)
            except Exception:  # a layer the text engine cannot lay out: the producer's chunks
                parts = None
        split = bool(parts) and len(parts) > 1
        chunks = L.get('chunks') if isinstance(L.get('chunks'), list) else None
        items = parts if split else (chunks or [L])
        for ci, c in enumerate(items):
            text = c.get('text')
            if text is None and c.get('words'):
                text = ' '.join(str(w.get('w', '')) for w in c['words'])
            text = str(text or '').strip()
            if not text:
                continue
            f0 = c.get('f0', int(round(float(c.get('t0', 0)) * fps)))
            f1 = c.get('f1', int(round(float(c.get('t1', 0)) * fps)) - 1)
            f0, f1 = int(f0), int(f1)
            src = 'ed_text split' if split else 'edl'
            if sidecar_frames and not chunks and not split:
                on = sorted(f for f in sidecar_frames.get(lid, []) if f0 - 3 <= f <= f1 + 3)
                if on:
                    f0, f1, src = on[0], on[-1], 'render'
            lines = c.get('lines') if isinstance(c.get('lines'), list) else [x for x in text.split('\n') if x.strip()]
            nl, reflowed = len(lines), False
            if T is not None and not split and nl > max_lines:
                # producer lines that do not fit are re-flowed by the renderer (never more than max_lines; a chunk that
                # needs more is split in time, which split_caption_layer would have shown)
                nl, reflowed = max_lines, True
            dur = (f1 - f0 + 1) / fps
            out.append(dict(id=lid + (f'.part[{ci}]' if split else (f'.chunks[{ci}]' if chunks else '')), f0=f0, f1=f1,
                            text=text[:60], n_lines=nl, max_lines=max_lines, dur_s=r(dur, 3),
                            cps=r(len(text.replace('\n', ' ')) / max(dur, 1e-6), 1), split=split, span_from=src,
                            **({'reflowed_from': len(lines)} if reflowed else {})))
    return out


def click_at(mix, t, sr=SR_A, hp=3000.0):
    """Click / pop at a seam: max 2 ms RMS of the > hp Hz signal within +-5 ms of t over the 90th percentile of the
    2 ms RMS in +-150 ms around it (excluding +-10 ms). dB, or None when silent."""
    from scipy.signal import butter, sosfiltfilt
    a, b = int((t - 0.2) * sr), int((t + 0.2) * sr)
    if a < 0 or b > len(mix):
        return None
    x = sosfiltfilt(butter(4, hp, btype='high', fs=sr, output='sos'), mix[a:b].mean(1).astype(np.float64))
    w = int(0.002 * sr)
    e = np.sqrt(np.convolve(x * x, np.ones(w) / w, mode='same'))
    c = int(0.2 * sr)
    near = e[c - int(0.005 * sr):c + int(0.005 * sr) + 1]
    ring = np.concatenate([e[c - int(0.15 * sr):c - int(0.01 * sr)], e[c + int(0.01 * sr):c + int(0.15 * sr)]])
    ref = float(np.percentile(ring, 90))
    if ref < 1e-6 and near.max() < 1e-5:
        return None
    return 20 * math.log10((near.max() + 1e-9) / (ref + 1e-9))


def voice_signal(actx):
    """Voice-only signal for the pause and first-word measurements -> (N x 2 array, source name) | (None, None): the
    verified voice stem (as mixed), else the audio.voice clips placed on the timeline (raw source audio), else the mix
    itself when it carries nothing but the voice (no music, no sfx)."""
    if actx is None:
        return None, None
    st = getattr(actx, 'stems', None)
    if st and 'voice' in st and np.any(st['voice']):
        g = getattr(actx, 'gain', None)
        return (st['voice'] * g[:, None] if g is not None else st['voice']), 'voice stem'
    if getattr(actx, 'voices', None):
        return actx.voice_track(), 'voice clips'
    au = getattr(actx, 'audio', None) or {}
    if getattr(actx, 'music', None) is None and not au.get('sfx') and getattr(actx, 'mix', None) is not None:
        return actx.mix, 'mix (voice only)'
    return None, None


def voice_activity(y, spans_s, sr=SR_A, hop=0.01):
    """Frame-wise voice activity (10 ms hop, 20 ms RMS) inside the talk spans [(t0, t1)] s: active = louder than
    max(noise floor + 8 dB, speech level - 26 dB) with speech level / noise floor = 90th / 5th percentile of the
    non-silent frames inside the spans; activity runs < 40 ms are dropped and gaps < 60 ms filled (stop consonants).
    -> (active bool array over the whole timeline, levels dict) | (None, None) when there is no voice."""
    m = (y.mean(1) if y.ndim == 2 else y).astype(np.float64)
    h, w = int(hop * sr), int(0.02 * sr)
    nfr = len(m) // h
    if nfr < 5:
        return None, None
    c = np.concatenate([[0.0], np.cumsum(m * m)])
    a = np.clip(np.arange(nfr) * h + h // 2 - w // 2, 0, len(m))
    b = np.clip(a + w, 0, len(m))
    db = 10 * np.log10((c[b] - c[a]) / np.maximum(b - a, 1) + 1e-14)
    inside = np.zeros(nfr, bool)
    for t0, t1 in spans_s:
        inside[max(0, int(t0 / hop)):max(0, int(t1 / hop))] = True
    ok = inside & (db > -80)
    if ok.sum() < 20:
        return None, None
    speech, noise = float(np.percentile(db[ok], 90)), float(np.percentile(db[ok], 5))
    thr = max(noise + 8.0, speech - 26.0)
    act = db > thr
    for a_, b_ in runs(~act):                            # fill short gaps
        if b_ - a_ + 1 < 6 and a_ > 0 and b_ < nfr - 1:
            act[a_:b_ + 1] = True
    for a_, b_ in runs(act):                             # drop short blips
        if b_ - a_ + 1 < 4:
            act[a_:b_ + 1] = False
    return act, dict(speech_db=r(speech, 1), noise_db=r(noise, 1), threshold_db=r(thr, 1), hop_s=hop)


def _word_at(words, t, side):
    """The word around a pause centred at t: the last one starting before t (side 'before') / the first one starting
    after it ('after') - word ends of ASR often run into the silence. Its text or None."""
    if not words:
        return None
    if side == 'before':
        w = max((w for w in words if w['t0'] < t), key=lambda w: w['t0'], default=None)
    else:
        w = min((w for w in words if w['t0'] >= t), key=lambda w: w['t0'], default=None)
    return w.get('w') if w else None


def analyse_lipsync(video, parts, fps):
    """Lip sync of the render's talk parts, measured on the rendered file itself with ed_sequence.estimate_av_offset
    (mouth motion of single speaking faces vs the speech envelope; offset = how much the audio lags the picture beyond
    the natural lead, 0 when in sync, not confident or under 2 frames). -> [{part, t0, t1, offset_s, offset_frames,
    measured_s, r, confident, why}] | None when the estimator is not available."""
    try:
        import ed_sequence as S
    except Exception:  # sequence planner unavailable: no lip-sync measurement
        return None
    fn = getattr(S, 'estimate_av_offset', None)
    if not callable(fn):
        return None
    out = []
    for p in parts:
        if p['type'] != 'talk':
            continue
        t0, t1 = p['f0'] / fps, (p['f1'] + 1) / fps
        if t1 - t0 < 2.0:
            continue
        try:
            res = fn(video, t0, t1, cache_dir=None, fps_out=fps) or {}
        except Exception as e:  # estimator failure: reported, not judged
            out.append(dict(part=p['id'], t0=r(t0, 3), t1=r(t1, 3), error=repr(e)[:200]))
            continue
        off = float(res.get('offset') or 0.0)
        out.append(dict(part=p['id'], t0=r(t0, 3), t1=r(t1, 3), offset_s=r(off, 3), offset_frames=r(off * fps, 1),
                        measured_s=r(res.get('measured'), 3), lag_s=r(res.get('lag'), 3), r=r(res.get('r'), 2),
                        confident=bool(res.get('confident')), why=str(res.get('why') or '')[:200]))
    return out


def analyse_speech(plan, q, parts, cuts, actx, edl, sidecar_frames, n, av=None):
    """Speech checks (talk parts; the whole edit for speech genres): first word timing, pauses left at jump cuts,
    subtitle reading speed / on-screen time / lines, longest stretch of a talk part without a visual change, clicks
    at audio seams, voice over music level. Pauses and the first word are measured on the voice audio itself (voice
    stem, else the placed voice clips; voice_activity) - word timestamps (OUTPUT-time qa.words) only name the words
    around them; without a voice-only signal they fall back to the word timestamps."""
    fps = plan.fps
    words = sorted(q['words'], key=lambda w: w['t0'])
    talk = [p for p in parts if p['type'] == 'talk']
    has_voice = bool((edl.get('audio') or {}).get('voice'))
    if not (words or talk or has_voice or q['mode'] == 'speech'):
        return check('skipped', note='no speech: no qa.words, no talk part, no audio.voice')
    spans = [(p['f0'], p['f1']) for p in talk] or [(0, n - 1)]
    card = q.get('genre_card')
    max_pause = float(q.get('max_pause') or 0.35)
    first_max = float(q.get('first_word_max') or 0.3)
    max_cps = float(q.get('max_cps') or _card_number(card, r'qa_reading_speed\(max_cps=([\d.]+)\)') or 20.0)
    min_sub = float(q.get('min_sub_s') or 0.7)
    max_lines = int(q['max_sub_lines']) if q.get('max_sub_lines') else None    # else each layer's own max_lines
    max_static = float(q.get('max_static_s') or _card_number(card, r'qa_visual_change\(max_gap=([\d.]+)\)') or 4.0)
    click_db = float(q.get('click_db') or 6.0)
    allowed = [tuple(x) for x in q.get('allowed_pauses') or [] if isinstance(x, (list, tuple)) and len(x) == 2]
    res = dict(talk_parts=[[a, b] for a, b in spans], thresholds=dict(max_pause=max_pause, first_word_max=first_max,
               max_cps=max_cps, min_sub_s=min_sub, max_sub_lines=max_lines, max_static_s=max_static, click_db=click_db))
    warn, notes = [], []
    brec = {rec['f']: rec for rec in cuts['boundaries']}
    # ---- the voice itself: activity from the audio (pauses, first word)
    vsig, vsrc = voice_signal(actx)
    act, vlev = (voice_activity(vsig, [(a / fps, (b + 1) / fps) for a, b in spans]) if vsig is not None else (None, None))
    hop = (vlev or {}).get('hop_s', 0.01)
    if act is not None:
        res['voice_activity'] = dict(vlev, signal=vsrc)
    # ---- first word of every talk part
    fw = []
    for a, b in spans:
        ta, tb = a / fps, (b + 1) / fps
        inside = [w for w in words if w['t1'] > ta + 1.0 / fps and w['t0'] < tb]
        item = dict(part_f0=a)
        if inside:
            w0 = inside[0]
            item.update(word=w0.get('w'), t0=r(w0['t0'], 3), lag_s=r(w0['t0'] - ta, 3), lag_from='words')
            if w0['t0'] < ta - 1.0 / fps:
                item['issue'] = 'the part starts inside this word'
        if act is not None:
            i0, i1 = int(round(ta / hop)), min(len(act), int(round(tb / hop)))
            on = np.where(act[i0:i1])[0]
            if len(on):
                item.update(onset_s=r((i0 + on[0]) * hop, 3), lag_s=r((i0 + on[0]) * hop - ta, 3), lag_from='audio')
        if item.get('lag_s') is None:
            continue
        if not item.get('issue') and item['lag_s'] > first_max + 1e-6:
            item['issue'] = f"first word {item['lag_s']:.2f} s after the part starts (max {first_max:g})"
        fw.append(item)
    res['first_word'] = fw
    warn += [f"first word at f{x['part_f0']}: {x['issue']}" for x in fw if x.get('issue')]
    if not words and act is None:
        notes.append('no word timestamps (qa.words) and no voice-only signal: first word and pauses not checked')
    # ---- pauses: silences of the voice > max_pause; at jump cuts (the source jumps) = left by the edit
    pauses = []

    def classify(t_a, t_b, fa, fb):
        cand = [rec for f, rec in brec.items() if fa <= f <= fb + 1 and rec['status'] != 'not_rendered']
        jump = [rec for rec in cand if rec.get('src_jump_s') is not None and abs(rec['src_jump_s']) > 0.04]
        cut = [rec for rec in cand if rec not in jump and rec.get('continuity') != 'continuous']
        item = dict(t0=r(t_a, 3), t1=r(t_b, 3), dur_s=r(t_b - t_a, 3), f=[fa, fb])
        mid = (t_a + t_b) / 2
        if any((p0 <= t_a and t_b <= p1) or p0 <= mid <= p1 or any(p0 <= rec['f'] / fps <= p1 for rec in jump)
               for p0, p1 in allowed):
            item['allowed'] = True
        if jump:
            item['jump_cut'] = jump[0]['f']
        elif cut:
            item['cut'] = cut[0]['f']
            item['note'] = 'across a camera change (continuous source): a reaction / pause by design'
        return item
    if act is not None:
        for a, b in spans:
            i0, i1 = int(round(a / fps / hop)), min(len(act), int(round((b + 1) / fps / hop)))
            for s0, s1 in runs(~act[i0:i1]):
                if s0 == 0 or s1 == i1 - i0 - 1:
                    continue                             # lead-in / tail of the part: the first-word check's business
                t_a, t_b = (i0 + s0) * hop, (i0 + s1 + 1) * hop
                if t_b - t_a <= max_pause + 1e-6:
                    continue
                item = classify(t_a, t_b, int(math.floor(t_a * fps)), int(math.ceil(t_b * fps)))
                item.update(after=_word_at(words, (t_a + t_b) / 2, 'before'), before=_word_at(words, (t_a + t_b) / 2, 'after'),
                            measured='audio')
                pauses.append(item)
        res['pauses'] = pauses
    elif words:
        for w1, w2 in zip(words, words[1:]):
            gap = w2['t0'] - w1['t1']
            if gap <= max_pause + 1e-6:
                continue
            fa, fb = int(round(w1['t1'] * fps)), int(round(w2['t0'] * fps))
            if not any(a <= fa <= b for a, b in spans):
                continue
            item = classify(w1['t1'], w2['t0'], fa, fb)
            item.update(after=w1.get('w'), before=w2.get('w'), measured='words')
            pauses.append(item)
        res['pauses'] = pauses
        notes.append('pauses from the word timestamps (no voice-only signal to measure)')
    if act is not None or words:
        bad = [p for p in pauses if p.get('jump_cut') is not None and not p.get('allowed')]
        warn += [f"pause {p['dur_s']:.2f} s left at the jump cut f{p['jump_cut']} ('{p.get('after')}' -> '{p.get('before')}')"
                 for p in bad]
        # pauses inside shots count only where the edit shortens pauses: a speech-genre edit (inferred talk part) or a
        # declared talk part with tighten_pauses; a composite's talk part that keeps the speaker's rhythm keeps them
        tight = [(p['f0'], p['f1']) for p in talk if not p.get('declared') or p.get('tighten_pauses')] if talk else spans
        if q['mode'] == 'speech' and tight:
            other = [p for p in pauses if p.get('jump_cut') is None and p.get('cut') is None and not p.get('allowed')
                     and any(a <= p['f'][0] <= b for a, b in tight)]
            for p in pauses:
                if p.get('jump_cut') is None and p.get('cut') is None and p not in other and not p.get('allowed'):
                    p['note'] = "inside a shot of a talk part that keeps the speaker's pauses (no tighten_pauses)"
            if len(other) > int(q.get('planned_pauses', 2)):
                warn.append(f"{len(other)} pauses > {max_pause:g} s inside shots (f{other[0]['f'][0]}...; the card allows "
                            f"{int(q.get('planned_pauses', 2))} planned ones)")
    # ---- subtitles
    subs = subtitle_items(edl, fps, sidecar_frames)
    sub_bad = []
    for s in subs:
        why = []
        if s['cps'] > max_cps + 0.05:
            why.append(f"{s['cps']} cps > {max_cps:g}")
        if s['dur_s'] < min_sub - 1e-6:
            why.append(f"on screen {s['dur_s']:.2f} s < {min_sub:g}")
        lim = max_lines if max_lines is not None else s.get('max_lines') or 3
        if s['n_lines'] > lim:
            why.append(f"{s['n_lines']} lines > {lim}")
        if why:
            sub_bad.append(dict(s, issues=why))
    res['subtitles'] = dict(items=len(subs), bad=sub_bad, split_parts=sum(1 for x in subs if x.get('split')))
    if sub_bad:
        warn.append(f"subtitles: {len(sub_bad)} of {len(subs)} chunks " + '; '.join(
            f"f{x['f0']}-{x['f1']} '{x['text'][:18]}' {', '.join(x['issues'])}" for x in sub_bad[:3]))
    # ---- visual change inside talk parts
    vis = []
    if talk:
        cam_types = set(getattr(E, 'CAMERA_FX', ())) if E is not None else set()
        src_cuts = source_cut_frames(q, fps)
        for p in talk:
            ev = {p['f0'], p['f1'] + 1}
            for rec in cuts['boundaries']:
                # planned cuts (their visibility is the cuts check's business), and boundaries with a continuous
                # source time that still show a camera change: the source's own cut (qa.source_cuts) or a visible step
                if p['f0'] < rec['f'] <= p['f1'] and (rec.get('continuity') != 'continuous' or rec.get('status') in VISIBLE_CUTS
                                                     or any(abs(rec['f'] - s) <= 1 for s in src_cuts)):
                    ev.add(rec['f'])
            ev.update(s for s in src_cuts if p['f0'] < s <= p['f1'])
            for u in cuts.get('unexpected') or []:  # shot changes inside a segment (the source's own camera cuts)
                if p['f0'] < u['f'] <= p['f1']:
                    ev.add(int(u['f']))
            for li, L in enumerate(edl.get('layers') or []):
                if str(L.get('kind', '')).lower() not in SUB_KINDS and 'f0' in L and p['f0'] < int(L['f0']) <= p['f1']:
                    ev.add(int(L['f0']))
            for i in p['segs']:
                sg = plan.segs[i]
                for fx in sg.get('fx') or []:
                    if fx.get('type') in cam_types and fx.get('frames'):
                        ev.update(int(sg['f0']) + int(k) for k in frange(fx['frames']) if p['f0'] < int(sg['f0']) + int(k) <= p['f1'])
            ev = sorted(ev)
            gaps = [(b_ - a_, a_, b_ - 1) for a_, b_ in zip(ev, ev[1:])]
            g = max(gaps) if gaps else (0, p['f0'], p['f1'])
            item = dict(part=p['id'], longest_s=r(g[0] / fps, 2), frames=[int(g[1]), int(g[2])], changes=len(ev) - 2)
            if g[0] / fps > max_static + 1e-6:
                item['issue'] = True
                long_ = [(a_, b_) for d_, a_, b_ in gaps if d_ / fps > max_static + 1e-6]
                item['over'] = [[int(a_), int(b_)] for a_, b_ in long_]
                warn.append(f"talk part {p['id']}: {len(long_)} stretch(es) without a visual change > {max_static:g} s "
                            f"({', '.join(f'f{a_}-{b_} {(b_ - a_ + 1) / fps:.1f} s' for a_, b_ in long_[:3])})")
            vis.append(item)
        res['visual_change'] = vis
    # ---- seams: clicks on the rendered audio at cuts inside talk parts
    seams = []
    if actx is not None and talk:
        vb = sorted({int(round(at * fps)) for at, _ in actx.voices} |
                    {int(round((at + len(y) / SR_A) * fps)) for at, y in actx.voices})
        for rec in cuts['boundaries']:
            f = rec['f']
            if not any(a < f <= b for a, b in spans) or rec['status'] == 'not_rendered':
                continue
            edited = any(abs(f - v) <= 1 for v in vb) or (rec.get('src_jump_s') is not None and abs(rec['src_jump_s']) > 0.02)
            if not edited:
                continue
            best = None
            for tt in {f / fps} | {v / fps for v in vb if abs(f - v) <= 1}:
                c = click_at(actx.mix, tt)
                if c is not None and (best is None or c > best[0]):
                    best = (c, tt)
            if best is None:
                continue
            item = dict(f=f, t=r(best[1], 4), spike_db=r(best[0], 1))
            if best[0] > click_db:
                item['click'] = True
            seams.append(item)
        res['seams'] = seams
        clicks = [s for s in seams if s.get('click')]
        if clicks:
            warn.append(f"clicks at {len(clicks)} audio seam(s): " + ', '.join(f"f{s['f']} +{s['spike_db']:.0f} dB" for s in clicks[:4]))
    # ---- voice over music during speech (stems)
    if actx is not None and actx.stems and words and 'voice' in actx.stems and 'music' in actx.stems:
        mask = np.zeros(actx.N, bool)
        for w in words:
            if any(a <= w['t0'] * fps <= b for a, b in spans):
                mask[int(w['t0'] * SR_A):int(w['t1'] * SR_A)] = True
        if mask.sum() > 0.5 * SR_A:
            def lk(y):
                k = kweight(y[mask])
                p = float((k * k).sum(1).mean())
                return -0.691 + 10 * math.log10(p) if p > 1e-12 else -70.0
            lv, lm = lk(actx.stems['voice']), lk(actx.stems['music'])
            res['voice_over_music_db'] = r(lv - lm, 1)
            need = q.get('voice_over_music_db')
            if need is not None and lv - lm < float(need):
                warn.append(f"voice only {lv - lm:.1f} dB above the music during speech (need {float(need):g})")
    # ---- lip sync of the render's talk parts (ed_sequence.estimate_av_offset on the rendered file)
    if av is not None:
        res['lip_sync'] = av
        for x in av:
            if x.get('confident') and abs(x.get('offset_frames') or 0.0) > 2.0 + 1e-6:
                warn.append(f"lip sync: the audio lags the picture by {x['offset_s']:.2f} s ({x['offset_frames']:.1f} frames, "
                            f"r {x.get('r')}) in talk part {x['part']} - set its av_offset")
    res['issues'], res['notes'] = warn, notes
    return check('warn' if warn else 'ok', **res)


# ============================================================================ talk framing (faces, fidelity, overlays)
def talk_samples(plan, parts, talk_src, max_n=24):
    """Rendered frames checked in talk parts: per segment of a talk source 1 + one per 1.5 s (at most 4) evenly
    spread frames, not on op frames or inside transition windows. -> {frame: segment index}"""
    fps, out = plan.fps, {}
    for p in parts:
        if p['type'] != 'talk':
            continue
        for si in p['segs']:
            sg = plan.segs[si]
            if sg.get('src', 'film') not in talk_src:
                continue
            f0, f1 = max(0, int(sg['f0'])), min(plan.n - 1, int(sg['f1']))
            if f1 - f0 < 4:
                continue
            cnt = min(4, 1 + int((f1 - f0 + 1) / (1.5 * fps)))
            for f in sorted({int(f0 + (i + 0.5) * (f1 - f0 + 1) / cnt) for i in range(cnt)}):
                for d in (0, 1, -1, 2, -2, 3, -3):
                    g = f + d
                    if f0 + 1 <= g <= f1 - 1 and not plan.op_any[g] and not plan.trans_win[g]:
                        out[g] = si
                        break
    if len(out) > max_n:
        keys = sorted(out)
        keep = {keys[int(round(i))] for i in np.linspace(0, len(keys) - 1, max_n)}
        out = {f: out[f] for f in keys if f in keep}
    return out


def talk_requests(plan, samples):
    reqs = []
    for f, si in sorted(samples.items()):
        sg = plan.segs[si]
        k = f - int(sg['f0'])
        reqs.append(dict(si=si, k=k, n=int(sg['f1']) - int(sg['f0']) + 1, src=sg.get('src', 'film'),
                         t=seg_time(sg, k, plan.fps), f=f, talk=True))
    return reqs


class _Box:
    pass


def crop_window(sg, k, box_wh, canvas):
    """Crop window (box px) of segment frame k: [x0, y0, x1, y1] + the state (renderer geometry)."""
    S = _Box()
    S.w, S.h = box_wh
    c = crop_at(sg, k)
    if E is not None:
        cx, cy, ww, hw = E.window(S, c, canvas['w'], canvas['h'])
    else:
        hw = S.h / max(c['z'], 1e-3)
        ww = hw * canvas['w'] / canvas['h']
        cx = min(max(c['cx'] * S.w, ww / 2), S.w - ww / 2) if ww < S.w else S.w / 2
        cy = min(max(c['cy'] * S.h, hw / 2), S.h - hw / 2) if hw < S.h else S.h / 2
    return [cx - ww / 2, cy - hw / 2, cx + ww / 2, cy + hw / 2], (cx, cy, ww, hw, c)


def expected_view(frame, scale, box_wh, sg, k, canvas, ow, oh):
    """What the renderer should show on segment frame k (before grade, fx and text): the source picture-box frame
    (decoded at `scale` of the box) warped through the crop window, at ow x oh."""
    _, (cx, cy, ww, hw, c) = crop_window(sg, k, box_wh, canvas)
    sx = ow / float(canvas['w'])
    if E is not None:
        M = E.affine(cx, cy, hw, ow, oh, float(c.get('rot', 0.0)), float(c.get('dx', 0.0)) * sx, float(c.get('dy', 0.0)) * sx)
    else:
        M = cv2.getRotationMatrix2D((cx, cy), float(c.get('rot', 0.0)), oh / hw)
        M[0, 2] += ow / 2 - cx
        M[1, 2] += oh / 2 - cy
    M = M.copy()
    M[:, :2] /= scale
    border = cv2.BORDER_CONSTANT if sg.get('border') == 'black' else cv2.BORDER_REFLECT101
    return cv2.warpAffine(frame, M, (ow, oh), flags=cv2.INTER_AREA, borderMode=border)


def fidelity(render_g, expect_g, masks=()):
    """Render vs expected picture: the median of (1 - NCC)/2 over cells (12 x ~21 grid) textured in the expected
    picture (NCC per cell ignores grade gain / offset and vignettes), cells under text excluded. ~0.05-0.15 for a
    faithful render (grade, vignette, compression), ~0.4-0.5 for an unrelated / garbled / shifted picture; nan when
    the picture is too flat to tell."""
    h, w = render_g.shape
    a = render_g.astype(np.float32)
    b = expect_g.astype(np.float32)
    keep = np.ones((h, w), bool)
    for x0, y0, x1, y1 in masks:
        keep[max(0, int(y0)):max(0, int(y1)), max(0, int(x0)):max(0, int(x1))] = False
    if keep.sum() < 0.3 * h * w:
        return float('nan')
    cs = max(6, w // 12)
    ny, nx = h // cs, w // cs
    vals = []
    for iy in range(ny):
        for ix in range(nx):
            sl = (slice(iy * cs, (iy + 1) * cs), slice(ix * cs, (ix + 1) * cs))
            if not keep[sl].all():
                continue
            ca, cb = a[sl], b[sl]
            sa, sb = ca.std(), cb.std()
            if sb < 4 or sa < 1:
                continue
            vals.append((1 - ((ca - ca.mean()) * (cb - cb.mean())).mean() / (sa * sb + 1e-6)) / 2)
    return float(np.median(vals)) if len(vals) >= 10 else float('nan')


def _iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - ix * iy
    return ix * iy / u if u > 0 else 0.0


FID_BAD = 0.30


def person_share(frame, win):
    """Share of the window [x0, y0, x1, y1] (frame px) covered by a person (PP-HumanSeg), None when unavailable."""
    try:
        m = V.person_mask(frame)
    except Exception:  # model missing
        return None
    x0, y0, x1, y1 = [int(round(v)) for v in win]
    sub = m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)]
    return float((sub > 0.5).mean()) if sub.size else None


# image fx that keep the picture's structure (cell NCC stays meaningful): fidelity is measured through them
FAITHFUL_FX = {'vignette', 'lens.vignette', 'grain', 'exposure', 'bloom', 'glow', 'letterbox', 'fx.letterbox'}


def analyse_talk_framing(plan, reqs, got, full, small, canvas, text_items, label_box, scale, full_frames=()):
    """Per talk sample: the source frame's faces vs the crop window (the speaker's face must be fully inside), the
    rendered frame's faces (the expected face must be found where the crop puts it, not cut by the frame edge) and
    the render's fidelity to the expected crop (a garbled, shifted or wrong-time picture fails even when a face is
    still detected)."""
    det = FaceDet()
    W, H = canvas['w'], canvas['h']
    ah, aw = small.shape[1], small.shape[2]
    rows = []
    for i, rq in enumerate(reqs):
        f = rq['f']
        g = got.get(i)
        row = dict(f=f, seg=plan.segs[rq['si']].get('id'), src_t=r(rq['t'], 3))
        if g is None or f >= len(small):
            row['status'] = 'no_source_frame'
            rows.append(row)
            continue
        sg = plan.segs[rq['si']]
        bw, bh = g['box_wh']
        win, _ = crop_window(sg, rq['k'], (bw, bh), canvas)
        row['window'] = [r(v, 1) for v in win]
        s = g['scale']
        sf = [dict(x=d['x'] / s, y=d['y'] / s, w=d['w'] / s, h=d['h'] / s, score=d['score']) for d in det(g['frame'])]
        sf = [d for d in sf if d['score'] >= 0.75 and d['w'] >= 0.025 * bw]
        # fidelity: render vs the expected crop of the source frame
        cam = any(fx.get('type') in getattr(E, 'CAMERA_FX', ()) for fx in sg.get('fx') or []) if E is not None else False
        odd = [fx.get('type') for fx in (sg.get('fx') or []) + (sg.get('post_text_fx') or [])
               if str(fx.get('type')) not in FAITHFUL_FX and fx.get('type') not in getattr(E, 'CAMERA_FX', ())]
        if cam or odd or f in full_frames:
            row['fidelity_skipped'] = 'camera fx' if cam else ('fx ' + ', '.join(map(str, odd)) if odd else 'full-frame layer')
        else:
            exp = expected_view(g['frame'], s, (bw, bh), sg, rq['k'], canvas, aw, ah)
            masks = [(it['box'][0] * aw / W, it['box'][1] * ah / H, it['box'][2] * aw / W, it['box'][3] * ah / H)
                     for it in text_items if it['f0'] <= f <= it['f1']]
            if label_box:
                masks.append(tuple(label_box))
            row['fidelity'] = r(fidelity(cv2.cvtColor(small[f], cv2.COLOR_RGB2GRAY), cv2.cvtColor(exp, cv2.COLOR_RGB2GRAY),
                                         masks), 3)
        # source faces vs window
        if sf:
            big = max(d['w'] * d['h'] for d in sf)
            cov = []
            for d in sf:
                if d['w'] * d['h'] < 0.5 * big:
                    continue
                if d['w'] >= 0.8 * (win[2] - win[0]) or d['h'] >= 0.8 * (win[3] - win[1]):
                    cov.append((1.0, d))            # close-up: larger than the window, cut by design
                    continue
                ix = max(0, min(win[2], d['x'] + d['w']) - max(win[0], d['x']))
                iy = max(0, min(win[3], d['y'] + d['h']) - max(win[1], d['y']))
                cov.append((ix * iy / max(1.0, d['w'] * d['h']), d))
            inside = [d for c_, d in cov if c_ >= 0.85]
            cut = [c_ for c_, d in cov if 0.15 <= c_ < 0.85]
            row['src_faces'] = len(sf)
            if cut:
                row['crop'] = 'cuts_face'
                row['face_cut_cov'] = r(max(cut), 2)
            elif not inside:
                # every detected face is outside: is a person in the window anyway (face turned away / behind a hand)?
                pm = person_share(g['frame'], [v * s for v in win])
                row['person_in_window'] = r(pm, 2)
                row['crop'] = 'no_face' if pm is not None and pm >= 0.15 else 'misses_face'
            else:
                row['crop'] = 'ok'
                d = max(inside, key=lambda d: d['w'] * d['h'])
                # where the crop puts that face on the canvas
                cx, cy = (win[0] + win[2]) / 2, (win[1] + win[3]) / 2
                k_ = H / (win[3] - win[1])
                row['expected_face'] = [r((d['x'] - cx) * k_ + W / 2, 1), r((d['y'] - cy) * k_ + H / 2, 1),
                                        r((d['x'] + d['w'] - cx) * k_ + W / 2, 1), r((d['y'] + d['h'] - cy) * k_ + H / 2, 1)]
        else:
            row['src_faces'] = 0
            row['crop'] = 'no_face'
        # rendered faces
        fr = full.get(f)
        if fr is not None:
            hh, ww = fr.shape[:2]
            ss_ = 320.0 / ww if ww > 320 else 1.0
            sm = cv2.resize(fr, (int(round(ww * ss_)), int(round(hh * ss_))), interpolation=cv2.INTER_AREA) if ss_ < 1 else fr
            rf = [d for d in det(sm) if d['score'] >= 0.6]
            k2 = W / (ww * ss_)
            rboxes = [[d['x'] * k2, d['y'] * k2, (d['x'] + d['w']) * k2, (d['y'] + d['h']) * k2] for d in rf]
            row['render_faces'] = [[r(v, 1) for v in bx] for bx in rboxes[:3]]
            ef = row.get('expected_face')
            if ef:
                row['face_match'] = r(max([_iou(ef, bx) for bx in rboxes] or [0.0]), 2)
            row['render_face_cut'] = any(bx[0] < 2 or bx[1] < 2 or bx[2] > W - 2 or bx[3] > H - 2 for bx in rboxes)
        fid = row.get('fidelity')
        if fid is not None and fid > FID_BAD:
            row['status'] = 'render_mismatch'
        elif row['crop'] in ('cuts_face', 'misses_face'):
            row['status'] = 'crop_' + row['crop']
        elif row['crop'] == 'ok' and row.get('face_match') is not None and row['face_match'] < 0.2 and (fid is None or fid > 0.2):
            row['status'] = 'face_not_in_render'
        else:
            row['status'] = 'ok' if row['crop'] == 'ok' else 'no_face'
        rows.append(row)
    return rows


def overlay_boxes(cfg, path, t0, t1, canvas):
    """Static overlays inside the picture box of a talk source, in box px: ed_video.static_overlays (persistent logos,
    lower thirds, UI) when available, plus sources[...].overlays declared in the EDL. The declared corner `logo` is
    inpainted by the renderer when the window touches it and is reported separately."""
    out, notes = [], []
    box = cfg.get('box')
    fn = getattr(V, 'static_overlays', None)
    if callable(fn):
        try:
            got = fn(path, box, t0, t1) or []
            for o in got:
                bx = o.get('box') if isinstance(o, dict) else o
                if not bx or len(bx) != 4:
                    continue
                bx = [float(v) for v in bx]
                if box:                     # ed_video returns source px (like `box` itself): to box px
                    bx = [bx[0] - box[0], bx[1] - box[1], bx[2] - box[0], bx[3] - box[1]]
                spans = None
                if isinstance(o, dict) and isinstance(o.get('spans'), list):
                    spans = [[float(a), float(b)] for a, b in (x for x in o['spans'] if isinstance(x, (list, tuple))
                                                                 and len(x) == 2)]
                out.append(dict(box=bx, kind=(o.get('kind') if isinstance(o, dict) else None) or 'overlay',
                                coverage=o.get('coverage') if isinstance(o, dict) else None, spans=spans,
                                source='ed_video'))
        except Exception as e:  # detector failure: report, keep the declared ones
            notes.append(f'ed_video.static_overlays failed: {e!r}')
    else:
        notes.append('ed_video.static_overlays not available: declared overlays only')
    for o in cfg.get('overlays') or []:
        bx = o.get('box') if isinstance(o, dict) else o
        if bx and len(bx) == 4:
            bx = [float(v) for v in bx]
            if box:
                bx = [bx[0] - box[0], bx[1] - box[1], bx[2] - box[0], bx[3] - box[1]]
            out.append(dict(box=bx, kind=(o.get('kind') if isinstance(o, dict) else None) or 'overlay', source='edl'))
    return out, notes


def analyse_overlays(plan, parts, talk_src, canvas, budget_s=120.0):
    """Static overlays of every talk source must stay outside the crop windows of its talk segments (every frame):
    -> list of {src, kind, box (box px), frames [[a, b]], max_share (of the overlay inside the window)}."""
    srcs = plan.edl.get('sources') or {}
    out, notes, t_start = [], [], time.time()
    for name in sorted(talk_src):
        cfg = srcs.get(name)
        if not cfg:
            continue
        path = _resolve(cfg.get('path'), plan.edl_dir)
        if not path or not os.path.exists(path):
            continue
        segs = [plan.segs[i] for p in parts if p['type'] == 'talk' for i in p['segs'] if plan.segs[i].get('src', 'film') == name]
        if not segs:
            continue
        ts = [seg_time(sg, k, plan.fps) for sg in segs for k in (0, int(sg['f1']) - int(sg['f0']))]
        if time.time() - t_start > budget_s:
            notes.append(f'{name}: overlay detection skipped (time budget)')
            continue
        ovs, nn = overlay_boxes(cfg, path, max(0.0, min(ts)), max(ts), canvas)
        notes += [f'{name}: {x}' for x in nn]
        notes.append(f"{name}: {len(ovs)} static overlay(s) found" + (' (' + ', '.join(
            f"{o['kind']} {[int(v) for v in o['box']]}" for o in ovs[:4]) + ', box px)' if ovs else ''))
        try:
            inf = probe_cached(path)
        except (subprocess.CalledProcessError, OSError, ValueError, KeyError):
            continue
        box = cfg.get('box') or [0, 0, inf['w'], inf['h']]
        bw, bh = box[2] - box[0], box[3] - box[1]
        logo = cfg.get('logo')
        logo_b = [logo[0] - box[0], logo[1] - box[1], logo[2] - box[0], logo[3] - box[1]] if logo else None
        for o in ovs:
            spans = o.get('spans')
            if spans is None and o.get('coverage') is not None and float(o['coverage']) < 0.5:
                continue                              # no spans (older detector) and shown in under half the frames
            ob = o['box']
            area = max(1.0, (ob[2] - ob[0]) * (ob[3] - ob[1]))
            frames, worst = [], 0.0
            for sg in segs:
                n_ = int(sg['f1']) - int(sg['f0']) + 1
                for k in range(n_):
                    if spans is not None:            # only while the graphic is on screen in the source
                        t_ = seg_time(sg, k, plan.fps)
                        if not any(a_ <= t_ <= b_ for a_, b_ in spans):
                            continue
                    w, _ = crop_window(sg, k, (bw, bh), canvas)
                    ix = max(0.0, min(w[2], ob[2]) - max(w[0], ob[0]))
                    iy = max(0.0, min(w[3], ob[3]) - max(w[1], ob[1]))
                    sh = ix * iy / area
                    if sh > 0.02 and ix * iy > 0.001 * (w[2] - w[0]) * (w[3] - w[1]):
                        frames.append(int(sg['f0']) + k)
                        worst = max(worst, sh)
            if not frames:
                continue
            item = dict(src=name, kind=o['kind'], box=[r(v, 1) for v in ob], frames=[list(x) for x in _frame_runs(frames)],
                        n_frames=len(frames), max_share=r(worst, 2), source=o.get('source'))
            if spans is not None:
                item.update(spans=[[r(a_, 3), r(b_, 3)] for a_, b_ in spans], coverage=r(o.get('coverage'), 2))
            if logo_b and _iou(logo_b, ob) > 0.3:
                item['inpainted'] = True             # the renderer paints the declared logo out
            out.append(item)
    return out, notes


def _frame_runs(frames):
    fr = sorted(set(frames))
    out = []
    for f in fr:
        if out and f == out[-1][1] + 1:
            out[-1][1] = f
        else:
            out.append([f, f])
    return out


def analyse_parts(parts, talk_src, plan, cuts, actx, grid, talk_rows, overlays, q, n):
    """Composite edits (meta.parts, or talk + music parts inferred from sync voice): parts tile the timeline, every
    part boundary is a visible cut, the strongest downbeat / drop of the music lands on the boundary into a music part,
    talk framing (faces, render fidelity) and static overlays outside the talk crops."""
    composite = len(parts) > 1 or any(p['type'] == 'talk' for p in parts)
    if not composite:
        return check('skipped', note='single music part')
    fps = plan.fps
    issues, warn = [], []
    declared = any(p['declared'] for p in parts)
    rows = [dict(id=p['id'], type=p['type'], raw_type=p.get('raw_type'), f0=p['f0'], f1=p['f1'], segs=len(p['segs']),
                 **{k: p[k] for k in ('genre', 'style', 'variant', 'engine', 'drop_frame') if p.get(k) is not None})
            for p in parts]
    if declared:
        if parts[0]['f0'] != 0:
            issues.append(f"first part starts at f{parts[0]['f0']}, not 0")
        for a, b in zip(parts, parts[1:]):
            if b['f0'] != a['f1'] + 1:
                issues.append(f"parts {a['id']}|{b['id']}: {'gap' if b['f0'] > a['f1'] + 1 else 'overlap'} "
                              f"f{a['f1']}..f{b['f0']}")
        if parts[-1]['f1'] != n - 1:
            issues.append(f"last part ends at f{parts[-1]['f1']}, the edit at f{n - 1}")
    seg_f0 = {int(sg['f0']) for sg in plan.segs}
    bounds = []
    for a, b in zip(parts, parts[1:]):
        f = b['f0']
        item = dict(f=f, t=r(f / fps, 3), prev=a['id'], next=b['id'], into=b['type'])
        if f not in seg_f0:
            issues.append(f"part boundary f{f} ({a['id']}|{b['id']}) is not a segment boundary")
        rec = next((x for x in cuts['boundaries'] if x['f'] == f), None)
        item['cut'] = rec['status'] if rec else None
        if rec and rec['status'] in ('missing', 'transition_weak', 'offset', 'not_rendered'):
            issues.append(f"part boundary f{f}: cut {rec['status']}")
        if b['type'] == 'music' and f > 0 and (b.get('drop_frame') is None or abs(int(b['drop_frame']) - f) <= 1):
            dr = analyse_drop(actx, grid, f, fps, float(q.get('drop_tol_frames') or 1.0))
            item['drop'] = dr
            if dr['status'] == 'fail':
                issues.append(f"music drop {dr['offset_frames']:+.1f} frames from the part boundary f{f} (strongest "
                              f"downbeat at {dr['drop_t']:.3f} s, +{dr['strength_db']:.1f} dB)")
            elif dr['status'] == 'warn':
                warn.append(f"part boundary f{f}: {dr.get('note')} ({dr.get('offset_frames')} frames)")
        bounds.append(item)
    for p in parts:                              # the sequence put a part's drop elsewhere (meta.parts drop_frame)
        df = p.get('drop_frame')
        if p['type'] != 'music' or df is None or (p['f0'] > 0 and abs(int(df) - p['f0']) <= 1):
            continue
        dr = analyse_drop(actx, grid, int(df), fps, float(q.get('drop_tol_frames') or 1.0))
        bounds.append(dict(f=int(df), t=r(int(df) / fps, 3), requested=f"meta.parts {p['id']}.drop_frame", drop=dr))
        if dr['status'] == 'fail':
            issues.append(f"music drop {dr['offset_frames']:+.1f} frames from {p['id']}'s drop frame f{df} (strongest "
                          f"downbeat at {dr['drop_t']:.3f} s, +{dr['strength_db']:.1f} dB)")
        elif dr['status'] == 'warn':
            warn.append(f"{p['id']} drop frame f{df}: {dr.get('note')} ({dr.get('offset_frames')} frames)")
    for key in ('drop_f', 'drop_at'):
        if q.get(key) is not None:
            fb = int(round(float(q[key]) * (1 if key == 'drop_f' else fps)))
            dr = analyse_drop(actx, grid, fb, fps, float(q.get('drop_tol_frames') or 1.0))
            bounds.append(dict(f=fb, requested=key, drop=dr))
            if dr['status'] == 'fail':
                issues.append(f"music drop {dr['offset_frames']:+.1f} frames from qa.{key} (f{fb})")
            break
    res = dict(parts=rows, declared=declared, talk_sources=sorted(talk_src), boundaries=bounds)
    # talk framing
    if talk_rows:
        st = {}
        for x in talk_rows:
            st[x['status']] = st.get(x['status'], 0) + 1
        with_face = [x for x in talk_rows if x.get('src_faces')]
        mism = [x for x in talk_rows if x['status'] == 'render_mismatch']
        crop_bad = [x for x in talk_rows if x['status'] in ('crop_cuts_face', 'crop_misses_face')]
        lost = [x for x in talk_rows if x['status'] == 'face_not_in_render']
        fids = [x['fidelity'] for x in talk_rows if x.get('fidelity') is not None]
        res['talk_framing'] = dict(samples=len(talk_rows), counts=st, median_fidelity=r(float(np.median(fids)), 3) if fids else None,
                                   rows=talk_rows)
        nf = max(1, len([x for x in talk_rows if x['status'] != 'no_source_frame']))
        if mism and (len(mism) >= 2 or len(mism) / nf >= 0.2):
            issues.append(f"talk framing: the render does not show the EDL's crop in {len(mism)}/{nf} samples (fidelity "
                          f"{np.median([x['fidelity'] for x in mism]):.2f} > {FID_BAD}; garbled / shifted / wrong-time picture) at "
                          + ', '.join(f"f{x['f']}" for x in mism[:6]))
        if with_face:
            share = 1 - (len(crop_bad) + len(lost)) / len(with_face)
            # faces turned away / covered while the person fills the window: neither shown nor a framing error
            hidden = [x for x in with_face if x['status'] == 'no_face']
            res['talk_framing']['crop_keeps_face_share'] = r(1 - len(crop_bad) / len(with_face), 2)
            res['talk_framing']['face_in_frame_share'] = r(sum(1 for x in with_face if x['status'] == 'ok')
                                                           / max(1, len(with_face) - len(hidden)), 2)
            res['talk_framing']['face_hidden'] = len(hidden)
            if crop_bad or lost:
                where = ', '.join('f%d %s' % (x['f'], x['status']) for x in (crop_bad + lost)[:5])
                msg = (f"talk framing: the speaker's face is cut or outside the frame in {len(crop_bad) + len(lost)}/"
                       f"{len(with_face)} samples ({where})")
                (issues if share < 0.75 else warn).append(msg)
    if overlays is not None:
        ov, ov_notes = overlays
        res['overlays'] = ov
        res['overlay_notes'] = ov_notes
        for o in ov:
            if o.get('inpainted'):
                continue
            msg = (f"static {o['kind']} of {o['src']} inside the talk crop in {o['n_frames']} frames "
                   f"({', '.join(f'{a}-{b}' for a, b in o['frames'][:3])}; up to {int(o['max_share'] * 100)}% of it)")
            (issues if o['max_share'] >= 0.25 else warn).append(msg)
    res['issues'], res['warnings'] = issues, warn
    return check('fail' if issues else ('warn' if warn else 'ok'), **res)


# ============================================================================ sfx audibility
# THE audibility rule is shared with the mixer (ed_sfx: QA_MIN_LU, QA_FAMILY, qa_event_need, audibility - one
# definition; QA calls them when present and falls back to the identical built-in copy below). Events whose anchors
# lie within 150 ms form a group; the group's SFX loudness = its loudest 400 ms (window centres every 25 ms over the
# members' spans) of the SFX bus as heard (after the master gain and the limiter); reference = the 3 s short-term
# loudness of the program without SFX (music + voice, after every duck and dip) after the group when it holds an impact
# / sub drop / click / glitch, centred on it otherwise. Need = QA_MIN_LU[family] at 'normal' (impact 3, whoosh /
# reverse whoosh 0, riser 0 LU) + the level preset (light -5, strong +4) + the event's gain_db, the strictest member's;
# auto-level whoosh / riser / swell / glitch / click groups under a voice need 6 LU less; not judged: sub drops,
# swells, glitches, clicks, samples without a kind, explicit "lu" events, music-processing kinds. Weak = rel_lu <
# need - QA_TOL (1 LU).
SFX_MIN_LU = {'impact': 3.0, 'whoosh': 0.0, 'riser': 0.0}
SFX_TOL_LU = 1.0          # measurement / design tolerance: weak = more than 1 LU under the need (ed_sfx.QA_TOL)
SFX_GROUP_S = 0.15
SFX_LEVELS = {'light': -5.0, 'normal': 0.0, 'strong': 4.0}
_SFX_FAMILY = {'impact': 'impact', 'whoosh': 'whoosh', 'reverse_whoosh': 'whoosh', 'riser': 'riser'}
_ATTACK_KINDS = {'impact', 'sub_drop', 'click', 'glitch'}
_UNDER_VOICE = {'whoosh', 'reverse_whoosh', 'riser', 'swell', 'glitch', 'click'}


def _sfx_mod():
    try:
        import ed_sfx as X
        return X
    except Exception:  # mixer not importable: built-in rule
        return None


def _level(level):
    """(preset name, dB offset) of an event level: ed_sfx.level_name / level_offset (aliases, numbers) when present."""
    X = _sfx_mod()
    try:
        if X is not None and hasattr(X, 'level_offset') and hasattr(X, 'level_name'):
            return X.level_name(level), float(X.level_offset(level))
    except Exception:  # unknown alias: built-in presets
        pass
    if isinstance(level, (int, float)) and not isinstance(level, bool):
        return min(SFX_LEVELS, key=lambda k: abs(SFX_LEVELS[k] - float(level))), float(level)
    name = str(level or 'normal').lower()
    return (name, SFX_LEVELS[name]) if name in SFX_LEVELS else ('normal', 0.0)


def sfx_thresholds(q):
    """{'base': {'impact': LU, 'whoosh': LU, 'riser': LU} at the normal preset (ed_sfx.QA_MIN_LU when present),
    'per_level', 'levels', 'tol', 'source'}; qa.sfx_min_lu overrides them, either flat ({"impact": 4}) or per preset
    ({"light": {"impact": -1}} = absolute values for that preset)."""
    base, per, src = dict(SFX_MIN_LU), {}, 'ed_qa'
    X = _sfx_mod()
    ext = getattr(X, 'QA_MIN_LU', None) if X is not None else None
    if isinstance(ext, dict):
        base.update({str(k): float(v) for k, v in ext.items() if isinstance(v, (int, float))})
        src = 'ed_sfx.QA_MIN_LU'
    over = q.get('sfx_min_lu')
    if isinstance(over, dict):
        src = 'qa.sfx_min_lu'
        for k, v in over.items():
            if isinstance(v, (int, float)):
                base[str(k)] = float(v)
            elif isinstance(v, dict):
                per[str(k)] = {str(a): float(b) for a, b in v.items() if isinstance(b, (int, float))}
    tol = getattr(X, 'QA_TOL', SFX_TOL_LU) if X is not None else SFX_TOL_LU
    return dict(base=base, per_level=per, levels=dict(SFX_LEVELS), tol=float(tol), source=src)


def sfx_need(tab, family, level):
    if not family:
        return None
    name, off = _level(level)
    if family in tab['per_level'].get(name, {}):
        return tab['per_level'][name][family]
    v = tab['base'].get(family)
    return None if v is None else v + off


def event_need(ev, audio, kind, tab):
    """Need (LU over the program) of one audio.sfx event: ed_sfx.qa_event_need (the mixer's own rule) unless
    qa.sfx_min_lu overrides the table; None = not judged (no family, an explicit "lu")."""
    if ev.get('lu') is not None:
        return None
    X = _sfx_mod()
    fn = getattr(X, 'qa_event_need', None) if X is not None else None
    if callable(fn) and tab.get('source') != 'qa.sfx_min_lu':
        try:
            return fn(ev, audio)
        except Exception:  # an event the mixer cannot parse: built-in rule
            pass
    need = sfx_need(tab, _SFX_FAMILY.get(kind), ev.get('level', (audio or {}).get('sfx_level')))
    return None if need is None else need + float(ev.get('gain_db', 0.0) or 0.0)


def _sfx_kind(ev):
    kind = str(ev.get('kind', '')).lower()
    kind = kind[4:] if kind.startswith('sfx.') else kind
    variant, spec = ev.get('variant'), {}
    X = _sfx_mod()
    try:
        if X is not None:
            kind, variant, spec = X.spec_of(kind, variant)
    except Exception:  # unknown kind: keep the given name
        pass
    return kind, variant, spec


def event_anchor(ev, spec=None):
    """Where an audio.sfx event lands (output s, = the mixer's record 'at'): ed_sfx.event_anchor when present (range
    events "t": [t0, t1]: t1 for peak / end aligned builds - whooshes, risers, reverse sounds, swells - else t0), else
    the same rule built in. None = no time."""
    X = _sfx_mod()
    fn = getattr(X, 'event_anchor', None) if X is not None else None
    if callable(fn):
        try:
            return fn(ev)
        except Exception:  # an event the mixer cannot parse: built-in rule
            pass
    off = float(ev.get('offset_ms', 0.0) or 0.0) / 1000.0
    if ev.get('at') is not None:
        return float(ev['at']) + off
    t = ev.get('t')
    if not (isinstance(t, (list, tuple)) and len(t) == 2):
        return None
    align = ev.get('align') or (spec or {}).get('align') or 'attack'
    return float(t[1] if align in ('peak', 'end') else t[0]) + off


def sfx_groups(recs):
    """Records [{i, kind, at, start, end, need_lu, auto}] -> groups [[(at, j, rec), ...]]: anchors within 150 ms."""
    items = sorted([(r_['at'], j, r_) for j, r_ in enumerate(recs) if r_.get('at') is not None and not r_.get('music')
                    and r_.get('start') is not None], key=lambda x: (x[0], x[1]))
    groups = []
    for at, j, r_ in items:
        if groups and at - groups[-1][-1][0] <= SFX_GROUP_S:
            groups[-1].append((at, j, r_))
        else:
            groups.append([(at, j, r_)])
    return groups


def audibility_rows(recs, sfx, prog, voice=None):
    """The audibility rule on arrays (as heard): ed_sfx.audibility when the mixer has it (one definition), else the
    identical built-in copy. -> (rows [{t, kinds, events, members, span, need_lu, rel_lu, sfx_lufs,
    program_st_lufs, under_voice}], implementation name)."""
    X = _sfx_mod()
    fn = getattr(X, 'audibility', None) if X is not None else None
    if callable(fn):
        try:
            return fn(recs, sfx, prog, voice, sr=SR_A), 'ed_sfx.audibility'
        except Exception as e:  # incompatible mixer version: built-in copy
            impl = f'ed_qa (ed_sfx.audibility failed: {e!r})'
    else:
        impl = 'ed_qa'
    dur = len(prog) / SR_A
    Ls, Lp = Loud(sfx), Loud(prog)
    Lv = Loud(voice) if voice is not None and np.any(voice) else None
    rows = []
    for g in sfx_groups(recs):
        rr = [x[2] for x in g]
        at = min(x[0] for x in g)
        s0, s1 = min(x['start'] for x in rr), max(x['end'] for x in rr)
        attack = any(x['kind'] in _ATTACK_KINDS for x in rr)
        ref = (at, min(dur, at + 3.0)) if attack else (max(0.0, at - 1.5), min(dur, at + 1.5))
        needs = [x.get('need_lu') for x in rr if x.get('need_lu') is not None]
        need = max(needs) if needs else None
        uv = False
        if need is not None and Lv is not None and all(x['kind'] in _UNDER_VOICE and x.get('auto') for x in rr):
            lv, lp_ = Lv.lufs(s0, s1), Lp.lufs(s0, s1)
            if lv is not None and lp_ is not None and lv > -60 and lv >= lp_ - 3.0:
                need, uv = need - 6.0, True
        row = dict(t=round(at, 3), kinds=sorted({x['kind'] for x in rr}), events=[x['i'] for x in rr],
                   members=[x[1] for x in g], span=[round(s0, 3), round(s1, 3)],
                   need_lu=None if need is None else round(need, 2), under_voice=uv)
        bs = Ls.max_momentary(max(0.2, s0), max(0.2, s1))
        lm = Lp.lufs(*ref)
        if bs is not None and lm is not None and lm > -60:
            row.update(sfx_lufs=round(bs[0], 2), program_st_lufs=round(lm, 2), rel_lu=round(bs[0] - lm, 2))
        elif bs is not None:
            row.update(sfx_lufs=round(bs[0], 2), note='no music or voice around the event')
        rows.append(row)
    return rows, impl


def _mixer_rows(side_audio):
    """The renderer sidecar's own audibility numbers: group rows (rel_lu, need_lu, ok) and placed events (st_lu,
    need_lu, floor_db) of the mix that was muxed."""
    sa = side_audio if isinstance(side_audio, dict) else {}
    rows = [g for g in sa.get('audibility') or [] if isinstance(g, dict)]
    evs = {int(e['i']): e for e in sa.get('events') or [] if isinstance(e, dict) and isinstance(e.get('i'), int)}
    return rows, evs


def analyse_sfx(edl, q, actx, fps, side_audio=None):
    """Audibility of every audio.sfx event on the rendered soundtrack, by the shared rule above. The arrays: QA re-mixes
    the audio block with debug stems (verified against the MP4 by AudioCtx); per group the re-mixed SFX must match
    the render in the event's span (residual < -12 dB of the sfx, < 12 kHz), else the event is measured on the MP4
    minus the music / voice stems (an upper bound). The mixer's own numbers from the render sidecar (audibility rows,
    st_lu / floor_db of the placed events) are reported next to QA's. Without verified stems nothing is judged (only
    mix_jump_lu, the jump of the mix at the event)."""
    au = edl.get('audio') or {}
    evs = au.get('sfx') or []
    if not evs:
        return check('skipped', note='no audio.sfx events')
    if actx is None:
        return check('skipped', note='no audio in the render')
    tab = sfx_thresholds(q)
    remix = {}
    for e in actx.events or []:
        if isinstance(e, dict) and 'i' in e:
            remix[int(e['i'])] = e
    items = []
    for i, ev in enumerate(evs):
        kind, variant, spec = _sfx_kind(ev)
        if spec.get('music') or kind in ('stutter', 'tape_stop', 'scratch'):
            items.append(dict(i=i, kind=kind, variant=variant, skipped='processes the music'))
            continue
        at = event_anchor(ev, spec)
        if at is None:
            continue
        rec = remix.get(i)
        rng_ = ev.get('t') if isinstance(ev.get('t'), (list, tuple)) and len(ev.get('t')) == 2 else None
        dur = float(ev.get('dur') or (float(rng_[1]) - float(rng_[0]) if rng_ else 0) or spec.get('dur') or 0.5)
        align = ev.get('align') or spec.get('align') or ('attack' if kind in _ATTACK_KINDS else 'peak')
        if rec and rec.get('start') is not None:
            s0, s1 = float(rec['start']), float(rec['end'])
        elif align in ('attack', 'start'):
            s0, s1 = at - 0.02, at + dur
        elif align == 'end' or kind == 'riser':
            s0, s1 = at - dur, at + 0.05
        else:
            s0, s1 = at - dur / 2, at + dur / 2
        lvl = ev.get('level', au.get('sfx_level'))
        items.append(dict(i=i, kind=kind, variant=variant, at=at, start=s0, end=s1, need_lu=event_need(ev, au, kind, tab),
                          auto=ev.get('lu') is None and ev.get('rel_lu') is None,
                          level=lvl if isinstance(lvl, (int, float)) else str(lvl or 'normal')))
    meas = [x for x in items if 'skipped' not in x]
    recs = [{k: x[k] for k in ('i', 'kind', 'at', 'start', 'end', 'need_lu', 'auto')} for x in meas]
    stems = actx.stems if actx.stems and 'sfx' in actx.stems and 'music' in actx.stems else None
    Lmix = Loud(actx.mix)
    side_rows, side_evs = _mixer_rows(side_audio)
    tol = tab['tol']
    impl = None
    if stems:
        from scipy.signal import butter, sosfiltfilt
        gl = actx.gain if getattr(actx, 'gain', None) is not None else np.ones(actx.N, np.float32)
        sfx_p = stems['sfx'] * gl[:, None]                                   # as rendered: after the limiter gain
        prog_p = (stems['music'] + stems.get('voice', 0)) * gl[:, None]
        voice_p = stems['voice'] * gl[:, None] if 'voice' in stems and np.any(stems['voice']) else None
        rows_st, impl = audibility_rows(recs, sfx_p, prog_p, voice_p)
        rows_rr, _ = audibility_rows(recs, actx.mix - prog_p, prog_p, voice_p)   # the render's own sfx bus estimate
        lp = butter(4, 12000, fs=SR_A, output='sos')
    else:
        rows_st = rows_rr = [dict(t=round(min(x[0] for x in g), 3), kinds=sorted({x[2]['kind'] for x in g}),
                                  events=[x[2]['i'] for x in g], span=[round(min(x[2]['start'] for x in g), 3),
                                                                       round(max(x[2]['end'] for x in g), 3)],
                                  need_lu=max([x[2]['need_lu'] for x in g if x[2]['need_lu'] is not None], default=None))
                             for g in sfx_groups(recs)]
    out, weak = [], []
    for row_st, row_rr in zip(rows_st, rows_rr):
        s0, s1 = row_st['span']
        row = dict(f=int(round(row_st['t'] * fps)), t=row_st['t'], kinds=row_st['kinds'], events=row_st['events'],
                   span=row_st['span'])
        if row_st.get('need_lu') is not None:
            row['need_lu'] = row_st['need_lu']
        if row_st.get('under_voice'):
            row['under_voice'] = True
        mm = Lmix.max_momentary(max(0.2, s0), max(0.2, s1))
        pre = Lmix.lufs(max(0.0, s0 - 0.45), max(0.05, s0 - 0.05))
        if mm is not None and pre is not None:
            row['mix_jump_lu'] = r(mm[0] - pre, 1)           # as heard: loudest 400 ms vs the 400 ms before
        if stems:
            a, b = max(0, int(s0 * SR_A)), min(actx.N, int(s1 * SR_A))
            if b - a > 64:
                # does the render carry these stems here? residual (render - stems) vs the sfx stem, < 12 kHz (codec)
                res_ = sosfiltfilt(lp, (actx.mix[a:b] - prog_p[a:b] - sfx_p[a:b]).astype(np.float64), axis=0)
                ref_e = sosfiltfilt(lp, sfx_p[a:b].astype(np.float64), axis=0)
                row['residual_db'] = r(10 * math.log10((res_ * res_).sum() + 1e-12) - 10 * math.log10((ref_e * ref_e).sum() + 1e-12), 1)
            verified = row.get('residual_db') is not None and row['residual_db'] <= -12.0
            src = row_st if verified else row_rr
            row['method'] = 'stems' if verified else 'render_residual'
            if not verified:
                row['note'] = ('the re-mixed sfx differ from the render here (residual '
                               f"{row.get('residual_db')} dB): measured on the render minus the music / voice stems")
            for k in ('sfx_lufs', 'program_st_lufs', 'rel_lu'):
                if src.get(k) is not None:
                    row[k] = r(src[k], 2)
            if src.get('note') and 'rel_lu' not in row:
                row['note'] = src['note']
        else:
            row['method'] = 'none'
        # the mixer's own claim for this group (render sidecar)
        sr_ = next((g for g in side_rows if sorted(g.get('events') or []) == sorted(row['events'])), None) or \
            next((g for g in side_rows if g.get('t') is not None and abs(float(g['t']) - row['t']) <= 0.05), None)
        if sr_ is not None:
            row['mixer'] = {k: sr_.get(k) for k in ('rel_lu', 'need_lu', 'ok') if sr_.get(k) is not None}
        # floor_db: the dB the mixer's audibility floor added above the level rules (0 = the preset was enough) -
        # from the render sidecar's placed events, else from QA's own re-mix records (same deterministic mix)
        fl = [side_evs[i].get('floor_db') for i in row['events'] if i in side_evs and side_evs[i].get('floor_db') is not None]
        if fl:
            row.update(floor_db=r(max(float(v) for v in fl), 2), floor_from='render sidecar')
        else:
            fr_ = [remix[i].get('floor_db') for i in row['events'] if i in remix and remix[i].get('floor_db') is not None]
            if fr_:
                row.update(floor_db=r(max(float(v) for v in fr_), 2), floor_from='re-mix')
        st_ = [side_evs[i].get('st_lu') for i in row['events'] if i in side_evs and side_evs[i].get('st_lu') is not None]
        if st_:
            row.setdefault('mixer', {})['st_lu'] = max(st_)
        mr = (row.get('mixer') or {}).get('rel_lu', (row.get('mixer') or {}).get('st_lu'))
        if mr is not None and row.get('rel_lu') is not None and abs(float(mr) - row['rel_lu']) > 1.0:
            row['mixer_delta_lu'] = r(row['rel_lu'] - float(mr), 2)
        if row.get('need_lu') is not None and row.get('rel_lu') is not None and row['rel_lu'] < row['need_lu'] - tol - 1e-6:
            row['weak'] = True
            weak.append(row)
        out.append(row)
    res = dict(events=len(evs), measured_groups=len(out), groups=out, skipped=[x for x in items if 'skipped' in x],
               thresholds=tab, rule=impl or 'ed_qa', stems=bool(stems), stems_corr=r(getattr(actx, 'stems_corr', None), 4),
               notes=list(actx.notes))
    if not stems:
        res['note'] = ('no verified stems (' + ('; '.join(actx.notes) or 'mixer not run') + '): audibility not '
                       'measured, only the jump of the mix at each event (mix_jump_lu)')
        return check('skipped', **res)
    res['weak'] = [dict(f=x['f'], kinds=x['kinds'], rel_lu=x['rel_lu'], need_lu=x['need_lu'],
                        **({'floor_db': x['floor_db']} if x.get('floor_db') is not None else {})) for x in weak]
    lifted = [x for x in out if (x.get('floor_db') or 0) > 0.05]
    if lifted:
        res['floor_lifted'] = [dict(f=x['f'], floor_db=x['floor_db'], src=x.get('floor_from')) for x in lifted]
    # measured on the render minus the re-mixed program (the re-mix differs there): an upper bound - weak there is
    # weak, loud enough there is not proven (typically a render made by another mixer version: re-render to verify)
    res['unverified'] = [x['f'] for x in out if x.get('method') == 'render_residual' and not x.get('weak')
                         and x.get('need_lu') is not None]
    disagree = [x for x in out if x.get('mixer_delta_lu') is not None]
    if disagree:
        res['mixer_disagrees'] = [dict(f=x['f'], qa_rel_lu=x.get('rel_lu'), mixer=x.get('mixer')) for x in disagree]
    return check('warn' if weak else 'ok', **res)


# ============================================================================ 8 image stats
# measurement tolerance of the qa.color ranges (preview frames, compression, label scrub): luma levels, saturation, %
_COLOR_TOL = dict(luma_mean=5.0, p1=3.0, p50=5.0, p99=5.0, sat_mean=0.03, sat_p95=0.03, clip_lo=1.0, clip_hi=1.0)


SLOW_FLOOR = 0.4          # deepest slow motion from <= 30 fps sources unless deep interpolation is accepted
JUMP_LIM, JUMP_MIN_LEVELS = 0.20, 6.0


def slow_ramps(plan, q, sources):
    """Slow motion deeper than 0.4x from a source of <= 30 fps: each source frame would cover ~3 output frames, the
    synthesized frames show (the cards' rule and the planner's slow floor). Not judged when the edit accepts deep
    interpolated slow motion (qa.interp, meta.interp / meta.opts.interp - the planner's interp option), nor holds
    (rate ~0) or storyboard slates. -> [{seg, f0, f1, min_rate, at, src_fps}]"""
    meta = plan.edl.get('meta') or {}
    if q.get('interp') or meta.get('interp') or (meta.get('opts') or {}).get('interp'):
        return []
    gaps = getattr(plan, 'gap_segs', None) or set()
    fps, out = plan.fps, []
    for si, sg in enumerate(plan.segs):
        if si in gaps:
            continue
        try:
            ts = seg_times(sg, fps)
        except (KeyError, TypeError, ValueError):
            continue
        rates = [(abs(b - a) * fps, k) for k, (a, b) in enumerate(zip(ts, ts[1:])) if abs(b - a) * fps > 0.05]
        if not rates:
            continue
        mn, k = min(rates)
        if mn >= SLOW_FLOOR - 1e-3:
            continue
        cfg = sources.get(sg.get('src', 'film')) or {}
        sfps = cfg.get('fps')
        if not sfps and cfg.get('path') and os.path.exists(cfg['path']):
            try:
                sfps = probe_cached(cfg['path']).get('fps')
            except (subprocess.CalledProcessError, OSError, ValueError, KeyError):
                sfps = None
        if not sfps or float(sfps) > 30.5:
            continue
        out.append(dict(seg=sg.get('id', str(si)), f0=int(sg['f0']), f1=int(sg['f1']), min_rate=r(mn, 3),
                        at=int(sg['f0']) + k, src_fps=r(float(sfps), 2)))
    return out


def brightness_jumps(small, plan, cuts, parts, nv, win=6):
    """Mean luma of the outgoing vs the incoming shot at every hard cut inside a music part (not a part boundary, not a
    transition): the last / first `win` clean frames of each side (no ops, transition windows, planned black / white),
    picture area only (letterbox bars out, label scrubbed). More than 20 % (and >= 6 levels) = warn: adjacent shots
    should stay within ~15 % brightness unless the contrast is planned. -> [{f, prev, next, before, after, change}]"""
    n = min(nv, plan.n)
    out = []
    for rec in cuts['boundaries']:
        if rec.get('kind') != 'cut' or rec.get('status') in ('not_rendered', 'gap'):
            continue
        f = rec['f']
        p = part_at(parts, f) if parts else None
        if p is None or p['type'] != 'music' or f == p['f0']:
            continue
        pi, ci = rec.get('pi'), rec.get('ci')
        if pi is None or ci is None:
            continue

        def side(frames):
            vals = []
            for g in frames:
                if not 0 <= g < n or plan.op_any[g] or plan.trans_win[g] or g in plan.planned_black or g in plan.planned_white:
                    continue
                x = picture_area(small[g][::2, ::2], letterbox_rect(plan, g)).reshape(-1, 3).astype(np.float32)
                vals.append(float((x[:, 0] * 0.2126 + x[:, 1] * 0.7152 + x[:, 2] * 0.0722).mean()))
            return float(np.mean(vals)) if vals else None
        sp, sc = plan.segs[pi], plan.segs[ci]
        before = side(range(max(int(sp['f0']), f - win), f))
        after = side(range(f, min(int(sc['f1']) + 1, f + win)))
        if before is None or after is None:
            continue
        ch = (after - before) / max(before, 1.0)
        if abs(ch) > JUMP_LIM and abs(after - before) >= JUMP_MIN_LEVELS:
            out.append(dict(f=f, prev=rec['prev'], next=rec['next'], before=r(before, 1), after=r(after, 1), change=r(ch, 3)))
    return out


def _is_letterbox(fx):
    t = str((fx or {}).get('type') or '').lower()
    return t in ('letterbox', 'fx.letterbox')


def _fx_gate(fx, k, f):
    """ed_fx.active's frame gates for an animated fx: 'frames' (segment-relative), 'f' (absolute), 'k': [k0, k1]
    ('t' is the letterbox's animation window, not a gate)."""
    if fx.get('frames') is not None and int(k) not in set(frange(fx['frames'])):
        return False
    if fx.get('f') is not None and int(f) not in set(frange(fx['f'])):
        return False
    kr = fx.get('k')
    if isinstance(kr, (list, tuple)) and len(kr) == 2 and not (kr[0] <= k <= kr[1]):
        return False
    return True


def letterbox_rect(plan, f):
    """Picture area [x0, y0, x1, y1] (fractions of the frame) that the segment's fx.letterbox bars leave at output frame
    f - ed_fx.fx_letterbox's geometry: ratio keys over t_keys / t / the segment's span (ease), above the frame aspect =
    top / bottom bars, below = side bars, split by anchor; within 0.5 % of the frame aspect = no bars. None: no bars."""
    si = plan.seg_of[f] if 0 <= f < plan.n else -1
    if si < 0:
        return None
    sg = plan.segs[si]
    fxs = [fx for fx in (sg.get('fx') or []) + (sg.get('post_text_fx') or []) if isinstance(fx, dict) and _is_letterbox(fx)]
    if not fxs:
        return None
    cv_ = plan.edl.get('canvas') or {}
    asp = float(cv_.get('w') or 1080) / float(cv_.get('h') or 1920)
    fps = plan.fps
    f0, f1 = int(sg['f0']), int(sg['f1'])
    k, n = f - f0, f1 - f0 + 1
    try:
        import ed_fx as Fx
        ease_fn = getattr(Fx, 'ease', None)
    except Exception:  # no fx module: linear ramps
        ease_fn = None
    rect = [0.0, 0.0, 1.0, 1.0]
    for fx in fxs:
        if not _fx_gate(fx, k, f):
            continue
        rs = fx.get('ratio', [1.78, 2.39])
        rs = [float(rs)] if isinstance(rs, (int, float)) else [float(v) for v in rs]
        if not rs:
            continue
        times = fx.get('t_keys')
        if not times:
            t = fx.get('t')
            if isinstance(t, (list, tuple)) and len(t) == 2:
                times = list(np.linspace(float(t[0]), float(t[1]), len(rs)))
            else:
                times = list(np.linspace(f0 / fps, f0 / fps + max(n - 1, 1) / fps, len(rs)))
        tt = f / fps
        if len(rs) == 1 or tt <= times[0]:
            ratio = rs[0]
        elif tt >= times[-1]:
            ratio = rs[-1]
        else:
            i = min(int(np.searchsorted(times, tt, side='right')) - 1, len(rs) - 2)
            u = (tt - times[i]) / max(times[i + 1] - times[i], 1e-9)
            try:
                u = float(ease_fn(u, fx.get('ease', 'linear'))) if callable(ease_fn) else u
            except Exception:  # unknown ease name: linear
                pass
            ratio = rs[i] + (rs[i + 1] - rs[i]) * u
        if ratio <= 0 or abs(ratio - asp) <= 0.005 * asp:
            continue
        ax, ay = (fx.get('anchor') or [0.5, 0.5])[:2]
        if ratio > asp:                                  # top / bottom bars
            tot = 1.0 - asp / ratio
            rect[1], rect[3] = max(rect[1], tot * float(ay)), min(rect[3], 1.0 - tot * (1.0 - float(ay)))
        else:                                            # side bars
            tot = 1.0 - ratio / asp
            rect[0], rect[2] = max(rect[0], tot * float(ax)), min(rect[2], 1.0 - tot * (1.0 - float(ax)))
    return rect if rect != [0.0, 0.0, 1.0, 1.0] else None


def picture_area(img, rect):
    """The frame cropped to the picture area rect (fractions; one more pixel inward for the antialiased bar edges)."""
    if rect is None:
        return img
    h, w = img.shape[:2]
    y0, y1 = int(math.ceil(rect[1] * h)) + (1 if rect[1] > 0 else 0), int(math.floor(rect[3] * h)) - (1 if rect[3] < 1 else 0)
    x0, x1 = int(math.ceil(rect[0] * w)) + (1 if rect[0] > 0 else 0), int(math.floor(rect[2] * w)) - (1 if rect[2] < 1 else 0)
    if y1 - y0 < 2 or x1 - x0 < 2:
        return img
    return img[y0:y1, x0:x1]


def image_stats(small, plan, q, nv):
    n = min(nv, plan.n)
    rows = []
    rng_keys = {k: v for k, v in (q.get('color') or {}).items() if isinstance(v, (list, tuple)) and len(v) == 2}
    bad_rows = []

    def stats(frames):
        x = np.concatenate([f.reshape(-1, 3) for f in frames]).astype(np.float32)
        Y = x[:, 0] * 0.2126 + x[:, 1] * 0.7152 + x[:, 2] * 0.0722
        hsv = np.concatenate([cv2.cvtColor(f, cv2.COLOR_RGB2HSV).reshape(-1, 3) for f in frames])
        S = hsv[:, 1].astype(np.float32) / 255.0
        p1, p50, p99 = np.percentile(Y, [1, 50, 99])
        return dict(luma_mean=r(Y.mean(), 1), p1=r(p1, 1), p50=r(p50, 1), p99=r(p99, 1), clip_lo=r((Y <= 2).mean() * 100, 2),
                    clip_hi=r((Y >= 253).mean() * 100, 2), sat_mean=r(S.mean(), 3), sat_p95=r(np.percentile(S, 95), 3),
                    mono=bool(S.mean() < 0.04))

    allf = []
    gaps = getattr(plan, 'gap_segs', None) or set()
    for si, sg in enumerate(plan.segs):
        f0, f1 = max(0, int(sg['f0'])), min(n - 1, int(sg['f1']))
        if f1 < f0:
            continue
        if si in gaps:                         # a storyboard slate: no picture yet, nothing to grade
            rows.append(dict(seg=sg.get('id', str(si)), f0=f0, f1=f1, gap=True))
            continue
        fr = [f for f in range(f0, f1 + 1) if not plan.op_any[f] and not plan.trans_win[f]
              and f not in plan.planned_black and f not in plan.planned_white]
        covered = not fr                       # the whole segment is under ops / planned black or white: not its look
        fr = fr or list(range(f0, f1 + 1))
        pick = [fr[int(round(i))] for i in np.linspace(0, len(fr) - 1, min(8, len(fr)))]
        # fx.letterbox bars are design, not the picture's shadows: only the picture area is measured
        lb = {f: letterbox_rect(plan, f) for f in pick}
        st = stats([np.ascontiguousarray(picture_area(small[f][::2, ::2], lb[f])) for f in pick])
        row = dict(seg=sg.get('id', str(si)), f0=f0, f1=f1, **st)
        if any(v is not None for v in lb.values()):
            row['letterbox'] = [r(v, 3) for v in next(v for v in lb.values() if v is not None)]
        out = {} if covered else {k: st[k] for k, (lo, hi) in rng_keys.items() if k in st and st[k] is not None
                                  and not (lo - _COLOR_TOL.get(k, 0.0) <= st[k] <= hi + _COLOR_TOL.get(k, 0.0))}
        if covered:
            row['covered'] = True
        if out:
            row['out_of_range'] = out
            bad_rows.append(row['seg'])
        rows.append(row)
        if not covered:
            allf += pick
    overall = stats([np.ascontiguousarray(picture_area(small[f][::2, ::2], letterbox_rect(plan, f)))
                     for f in allf[::max(1, len(allf) // 48)]]) if allf else {}
    status = 'warn' if bad_rows else 'ok'
    return check(status, overall=overall, segments=rows, ranges=rng_keys or None, out_of_range_segments=bad_rows)


# ============================================================================ sheets & plots
def _font(size):
    try:
        from PIL import ImageFont
        return ImageFont.truetype(FONT, size)
    except Exception:
        from PIL import ImageFont
        return ImageFont.load_default()


def _tile(img, tw):
    h, w = img.shape[:2]
    th = int(round(h * tw / w))
    return cv2.resize(img, (tw, th), interpolation=cv2.INTER_AREA)


COL = dict(exact=(60, 200, 90), masked=(120, 170, 255), soft=(170, 170, 170), transition=(120, 170, 255),
           offset=(255, 60, 60), missing=(255, 150, 40), transition_weak=(255, 150, 40), unexpected=(255, 60, 200),
           not_rendered=(255, 60, 60), hard=(255, 150, 40), flash_frame=(255, 90, 40), gap=(150, 150, 150))


def _num(d, xy, text, font, fill=(255, 255, 0)):
    """Frame number with a dark backing so it reads on white frames too."""
    x, y = xy
    w = int(d.textlength(text, font=font)) if hasattr(d, 'textlength') else 7 * len(text)
    d.rectangle([x - 1, y - 1, x + w + 2, y + 12], fill=(0, 0, 0))
    d.text((x, y), text, fill=fill, font=font)


def cut_sheets(small, cuts, plan, out_dir, nv, tw=128, per_page=24, cols=4):
    """Per cut: last visible frame of the old shot | cut frame (coloured by status) | next frame."""
    from PIL import Image, ImageDraw
    n = min(nv, plan.n)
    items = []
    for rec in cuts['boundaries']:
        if rec['f'] >= n:
            continue
        f = rec.get('detected', rec['f'])
        before = rec['hidden'][0] - 1 if rec.get('hidden') else f - 1
        extra = (f" {rec['offset']:+d} (cut at {rec['detected']})" if rec.get('offset') else '')
        extra += f" d{rec['score']:.2f}/{rec['thr']:.2f}" if rec.get('score') is not None and rec.get('thr') is not None else ''
        if rec.get('hidden'):
            extra += f" hid {rec['hidden'][0]}-{rec['hidden'][1]}" if rec['hidden'][1] > rec['hidden'][0] else f" hid {rec['hidden'][0]}"
        items.append(dict(fr=(before, f, f + 1), f=rec['f'], label=f"{rec['f']} {rec['prev']}|{rec['next']}",
                          status=rec['status'], extra=extra))
    items += [dict(fr=(u['f'] - 1, u['f'], u['f'] + 1), f=u['f'], label=f"{u['f']} inside {u['seg']}", status='unexpected',
                   extra=f" d{u['score']:.2f} src~{u.get('src_t')}") for u in cuts['unexpected']]
    items.sort(key=lambda d: d['f'])
    if not items:
        return []
    th = int(round(small.shape[1] * tw / small.shape[2]))
    head = 30
    cw = 3 * tw + 10
    ch = th + head + 6
    f_small = _font(11)
    paths = []
    for pi in range(0, len(items), per_page):
        page = items[pi:pi + per_page]
        rows = math.ceil(len(page) / cols)
        img = Image.new('RGB', (cols * cw, rows * ch), (18, 18, 18))
        d = ImageDraw.Draw(img)
        for j, it in enumerate(page):
            R, C = divmod(j, cols)
            x0, y0 = C * cw, R * ch
            for m, f in enumerate(it['fr']):
                if 0 <= f < n:
                    img.paste(Image.fromarray(_tile(small[f], tw)), (x0 + m * tw, y0 + head))
                    _num(d, (x0 + m * tw + 3, y0 + head + 3), str(f), f_small)
            col = COL.get(it['status'], (220, 220, 220))
            d.rectangle([x0 + tw, y0 + head, x0 + 2 * tw - 1, y0 + head + th - 1], outline=col, width=2)
            d.text((x0 + 2, y0 + 2), it['label'][:52], fill=(235, 235, 235), font=f_small)
            d.text((x0 + 2, y0 + 15), (it['status'] + it['extra'])[:52], fill=col, font=f_small)
        p = os.path.join(out_dir, f'qa_cuts_{pi // per_page + 1}.jpg')
        img.save(p, quality=86)
        paths.append(p)
    return paths


def flash_strip(small, fl, n, cols=10, tw=58):
    """All frames of the worst 1 s flash window; up transitions framed yellow, down ones blue."""
    from PIL import Image, ImageDraw
    a, b = fl['worst_window']
    dirs = {f: d for f, d in fl['transition_frames']}
    frames = list(range(a, min(n - 1, b) + 1))
    th = int(round(small.shape[1] * tw / small.shape[2]))
    rows = math.ceil(len(frames) / cols)
    img = Image.new('RGB', (cols * (tw + 2), rows * (th + 2)), (8, 8, 8))
    d = ImageDraw.Draw(img)
    fnt = _font(10)
    for j, f in enumerate(frames):
        R, C = divmod(j, cols)
        x, y = C * (tw + 2), R * (th + 2)
        img.paste(Image.fromarray(_tile(small[f], tw)), (x, y))
        if f in dirs:
            d.rectangle([x, y, x + tw - 1, y + th - 1], outline=(255, 220, 0) if dirs[f] > 0 else (60, 140, 255), width=3)
        _num(d, (x + 3, y + 3), str(f), fnt)
    return np.asarray(img)


def issue_sheet(tiles, out_dir, tw=200, cols=6, gap=4):
    """tiles: [(rgb image, title, [(box px in that image, rgb), ...], span in columns), ...] packed row by row."""
    from PIL import Image, ImageDraw
    if not tiles:
        return None
    f_small = _font(11)
    ims = []
    for im, title, boxes, span in tiles[:30]:
        im = np.ascontiguousarray(im)
        h, w = im.shape[:2]
        width = span * tw + (span - 1) * gap
        s = width / w
        t = Image.fromarray(_tile(im, width))
        d = ImageDraw.Draw(t)
        for bx, col in boxes:
            d.rectangle([bx[0] * s, bx[1] * s, bx[2] * s, bx[3] * s], outline=col, width=2)
        per_line = max(10, width // 7)
        lines = [title[i:i + per_line] for i in range(0, len(title), per_line)][:2]
        canvas = Image.new('RGB', (width, t.size[1] + 30), (18, 18, 18))
        canvas.paste(t, (0, 30))
        dd = ImageDraw.Draw(canvas)
        for li, ln in enumerate(lines):
            dd.text((3, 2 + li * 13), ln, fill=(235, 235, 235), font=f_small)
        ims.append((canvas, span))
    rows, cur, used = [], [], 0
    for im, span in ims:
        if used + span > cols and cur:
            rows.append(cur)
            cur, used = [], 0
        cur.append(im)
        used += span
    if cur:
        rows.append(cur)
    H = sum(max(i.size[1] for i in row) + gap for row in rows)
    sheet = Image.new('RGB', (cols * (tw + gap), H), (8, 8, 8))
    y = 0
    for row in rows:
        x = 0
        for im in row:
            sheet.paste(im, (x, y))
            x += im.size[0] + gap
        y += max(i.size[1] for i in row) + gap
    p = os.path.join(out_dir, 'qa_issues.jpg')
    sheet.save(p, quality=86)
    return p


def talk_tiles(rows, reqs, got, small, plan, canvas, max_n=4):
    """Issue tiles for the talk framing: the rendered frame next to what the EDL's crop of the source should show
    (render mismatch), or the source frame with the crop window (green) and the faces it cuts (crop issues)."""
    tiles = []
    ah, aw = small.shape[1], small.shape[2]
    by_f = {rq['f']: (i, rq) for i, rq in enumerate(reqs)}
    for row in [x for x in rows if x['status'] in ('render_mismatch', 'face_not_in_render', 'crop_cuts_face',
                                                     'crop_misses_face')][:max_n]:
        i, rq = by_f.get(row['f'], (None, None))
        g = got.get(i) if i is not None else None
        if g is None:
            continue
        sg = plan.segs[rq['si']]
        if row['status'] in ('render_mismatch', 'face_not_in_render'):
            exp = expected_view(g['frame'], g['scale'], g['box_wh'], sg, rq['k'], canvas, aw, ah)
            pair = np.concatenate([small[row['f']], np.full((ah, 4, 3), 20, np.uint8), exp], axis=1)
            tiles.append((pair, f"talk f{row['f']} {row['seg']}: {row['status']} - render (left) vs the EDL crop of the "
                          f"source (right), fidelity {row.get('fidelity')}", [], 2))
        else:
            s_ = g['scale']
            wb = [v * s_ for v in row['window']]
            span = 3 if g['frame'].shape[1] > 1.5 * g['frame'].shape[0] else 2
            tiles.append((g['frame'], f"talk f{row['f']} {row['seg']}: {row['status']} - crop window (green), source "
                          f"{row['src_t']} s", [(wb, (60, 200, 90))], span))
    return tiles


def _plt():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    return plt


def plot_rhythm(rh, aud, events, fps, dur, out, words=None, parts=None):
    plt = _plt()
    fig, ax = plt.subplots(figsize=(14, 2.8))
    mode = rh.get('mode')
    brh = rh if mode == 'beats' else (rh.get('beats') if mode == 'parts' else None)
    titles = []
    for p in parts or []:
        if p['type'] == 'talk' and mode == 'parts':
            ax.axvspan(p['f0'] / fps, (p['f1'] + 1) / fps, color='#fde68a', alpha=0.25)
    if brh and brh.get('status') != 'skipped' and aud and not aud.get('error'):
        env = aud.get('envelope') or {}
        if env.get('onset'):
            t = np.arange(len(env['onset'])) * env['step'] / env['fps']
            t = t / float(aud.get('envelope_speed', 1.0)) + float(aud.get('envelope_offset', 0.0))
            sel = (t >= -0.5) & (t <= dur + 0.5)
            ax.plot(t[sel], np.asarray(env['onset'], float)[sel], color='#888', lw=0.6)
        grid, kinds = beat_grid(aud, dur)
        for g, k in zip(grid, kinds):
            if 0 <= g <= dur:
                ax.axvline(g, color='#3b82f6', lw=0.5 if k == 'beat' else 0.4, alpha=0.55 if k == 'beat' else 0.25,
                           ls='-' if k == 'beat' else ':')
        for dbt in aud.get('downbeats', []):
            if 0 <= dbt <= dur:
                ax.axvline(dbt, color='#1d4ed8', lw=1.2, alpha=0.8)
        for c in brh.get('cuts', []):
            col = '#16a34a' if c['on'] else '#dc2626'
            ax.axvline(c['t'], color=col, lw=1.6, ymin=0.55)
            if not c['on']:
                ax.text(c['t'], 1.02, f"{c['offset_frames']:+.1f}", color=col, fontsize=7, ha='center')
        titles.append(f"cuts on beat/half-beat grid (±{brh.get('tol_frames')} fr): {brh.get('on_grid')}/{brh.get('n_cuts')} = "
                      f"{brh.get('share')} (need {brh.get('threshold')}) · {aud.get('bpm')} BPM conf {aud.get('tempo_conf')}"
                      f"{' steady' if aud.get('steady') else ''}")
    wrh = rh if mode == 'words' else (rh.get('words') if mode == 'parts' else None)
    if wrh is not None or (brh is None and words):
        for w in words or []:
            ax.axvspan(w['t0'], w['t1'], ymin=0.1, ymax=0.5, color='#93c5fd', alpha=0.6)
        bad = {c['f'] for c in (wrh or rh).get('cuts_inside_words', [])}
        beat_f = {c['f'] for c in (brh or {}).get('cuts', [])} if brh else set()
        for e in events:
            if e['f'] in beat_f:
                continue
            ax.axvline(e['f'] / fps, color='#dc2626' if e['f'] in bad else '#16a34a', lw=1.4, ymin=0.55)
        titles.append(f"cuts vs words: not inside a word {(wrh or rh).get('share')} (need {(wrh or rh).get('threshold')})")
    ax.set_title(' · '.join(titles) + ' · green ok, red off / inside a word', fontsize=9)
    ax.set_xlim(0, dur)
    ax.set_ylim(0, 1.1)
    ax.set_xlabel('s')
    fig.tight_layout()
    fig.savefig(out, dpi=90)
    plt.close(fig)


def plot_loudness(L, q, events, fps, dur, out):
    plt = _plt()
    s = L['series']
    fig, ax = plt.subplots(figsize=(14, 2.8))
    if s['t']:
        nan = lambda v: [x if x > -69 else np.nan for x in v]      # no value until the 0.4 s / 3 s window is full
        ax.plot(s['t'], nan(s['M']), color='#94a3b8', lw=0.7, label='momentary 400 ms')
        ax.plot(s['t'], nan(s['S']), color='#111827', lw=1.3, label='short-term 3 s')
    ax.axhspan(q['lufs'] - q['lufs_tol'], q['lufs'] + q['lufs_tol'], color='#22c55e', alpha=0.15, label='target band')
    if L.get('lufs') is not None:
        ax.axhline(L['lufs'], color='#2563eb', lw=1.2, ls='--', label=f"integrated {L['lufs']} LUFS")
    for e in events:
        ax.axvline(e['f'] / fps, color='#f59e0b', lw=0.5, alpha=0.5)
    lo = min([v for v in s['M'] if v > -69] + [q['lufs'] - 8])
    ax.set_ylim(max(-50, lo - 3), max(0, q['lufs'] + 6))
    ax.set_ylabel('LUFS')
    ax2 = ax.twinx()
    if s['t']:
        ax2.plot(s['t'], s['tpk'], color='#dc2626', lw=0.6, alpha=0.8)
    ax2.axhline(q['tp_max'], color='#dc2626', lw=0.8, ls=':')
    ax2.set_ylim(-30, 3)
    ax2.set_ylabel('true peak dBTP', color='#dc2626')
    ax.set_xlim(0, dur)
    ax.legend(loc='lower left', fontsize=7, ncol=4)
    ax.set_title(f"loudness: integrated {L.get('lufs')} LUFS (target {q['lufs']} ± {q['lufs_tol']}), true peak "
                 f"{L.get('true_peak')} dBTP (max {q['tp_max']}), LRA {L.get('lra')} LU", fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=90)
    plt.close(fig)


# ============================================================================ report
def verdict_lines(res):
    c = res['checks']
    lines = []

    def add(level, text):
        lines.append((LEVELS[level], level.upper() if level != 'ok' else 'ok', text))

    if res.get('gaps'):                           # storyboard: what is still to generate comes first
        g = res['gaps']
        n_slots = (res.get('storyboard') or {}).get('slots') or len(g)
        lines.append((9, 'GAPS', f"storyboard: {len(g)} of {max(n_slots, len(g))} slots still to fill (edit-gen briefs in "
                      f"meta.gaps; slates are not judged as pictures): " + '; '.join(
                          f"{x['id']} f{x['f'][0]}-{x['f'][1]} {x['dur']:.1f} s"
                          + (f" {str(x.get('shot'))[:28]}" if x.get('shot') else '') for x in g[:6])
                      + (' ...' if len(g) > 6 else '')))
    f = c['format']
    add(f['status'], f"format: {f['frames']} frames (EDL {f['n_frames']}), {f['size'][0]}x{f['size'][1]} @{f['fps']}"
        + (f" — {'; '.join(f['problems'])}" if f['problems'] else ''))
    k = c['cuts']
    cnt = k.get('counts', {})
    msg = (f"cuts: {cnt.get('exact', 0)} exact, {cnt.get('masked', 0)} hidden under ops, {cnt.get('soft', 0)} invisible by design"
           f"{', ' + str(cnt.get('transition', 0)) + ' transitions' if cnt.get('transition') else ''}"
           f"{', ' + str(cnt.get('gap', 0)) + ' next to a storyboard slate (not judged)' if cnt.get('gap') else ''}"
           f"{', ' + str(cnt.get('accent', 0)) + ' visible by a planned punch / shake' if cnt.get('accent') else ''}"
           f" of {k['n_boundaries']} boundaries")
    if cnt.get('offset'):
        offs = [f"{b['f']}{b['offset']:+d}" for b in k['boundaries'] if b['status'] == 'offset'][:6]
        msg += f"; OFF-FRAME {cnt['offset']}: {', '.join(offs)}"
    if cnt.get('missing') or cnt.get('transition_weak'):
        ms = [str(b['f']) for b in k['boundaries'] if b['status'] in ('missing', 'transition_weak')][:6]
        msg += f"; not visible: {', '.join(ms)}"
    if cnt.get('hard'):
        hs = [f"{b['f']} {b.get('transition')}" for b in k['boundaries'] if b['status'] == 'hard'][:4]
        msg += f"; soft transitions rendered as a hard cut: {', '.join(hs)}"
    if cnt.get('flash_frame'):
        ff = [b for b in k['boundaries'] if b['status'] == 'flash_frame'][:4]
        msg += '; single-frame flash at ' + ', '.join(
            f"{b['flash']} (changes at {b['steps'][0]} and {b['steps'][1]}"
            + (', the source cut is a frame off the planned cut' if 'qa.source_cuts' in (b.get('hint') or '') else '') + ')'
            for b in ff)
    if k['unexpected']:
        msg += '; unexpected cuts: ' + '; '.join(f"f{u['f']} ({u.get('hint') or u['seg']})" for u in k['unexpected'][:4])
    add(k['status'], msg)
    rh = c['rhythm']

    def beats_line(b):
        offs = ', '.join(f"{x['f']}({x['offset_frames']:+.1f})" for x in b['off_grid'][:6])
        return (f"{b['on_grid']}/{b['n_cuts']} cuts on beat/half-beat ±{b['tol_frames']:g} fr = {b['share']} "
                f"(need {b['threshold']}; random cutting would score ~{b['chance_share']}; on the 1/16 grid "
                f"{b['share_quarter_grid']}; {b['bpm']} BPM, conf {b['tempo_conf']}, grid from the "
                f"{b.get('grid_source', 'rendered audio')})" + (f"; off: {offs}" if offs else ''))

    def words_line(w):
        ex = w.get('source_cuts_exempt') or []
        return (f"{w['share']} of cuts outside words (need {w['threshold']})"
                + (f"; inside words at {', '.join(str(x['f']) for x in w['cuts_inside_words'][:6])}" if w['cuts_inside_words'] else '')
                + (f"; {len(ex)} source camera cut(s) not judged ({', '.join(str(x['f']) for x in ex[:4])})" if ex else ''))
    if rh['status'] == 'skipped':
        add('skipped', f"rhythm: skipped — {rh.get('note')}")
    elif rh['mode'] == 'parts':
        parts_ = []
        if rh['words']['status'] != 'skipped':
            parts_.append('talk parts: ' + words_line(rh['words']))
        else:
            parts_.append('talk parts: ' + str(rh['words'].get('note')))
        if rh['beats']['status'] != 'skipped':
            parts_.append('music parts: ' + beats_line(rh['beats']))
        else:
            parts_.append('music parts: ' + str(rh['beats'].get('note')))
        add(rh['status'], 'rhythm: ' + ' | '.join(parts_))
    elif rh['mode'] == 'beats':
        add(rh['status'], 'rhythm: ' + beats_line(rh))
    else:
        add(rh['status'], 'rhythm: ' + words_line(rh))
    L = c['loudness']
    if L['status'] == 'skipped':
        add('skipped', f"loudness: skipped — {L.get('note')}")
    else:
        extra = ''
        sc = L.get('sidecar') or {}
        enc = sc.get('encode') or {}
        if isinstance(enc.get('lufs'), (int, float)):
            extra = (f"; renderer's delivered AAC {enc.get('lufs')} LUFS / {enc.get('tp')} dBTP (mix WAV {sc.get('lufs')} / "
                     f"{sc.get('tp')})")
        elif sc:
            extra = f"; mixer sidecar {sc.get('lufs')} LUFS / {sc.get('tp')} dBTP"
        if L.get('sidecar_mismatch'):
            extra += f" — {L['sidecar_mismatch']}"
        if L.get('music_sync') and L['music_sync'].get('lag_ms') is not None and abs(L['music_sync']['lag_ms']) > 1000 / 30.0:
            extra += f"; music {L['music_sync']['lag_ms']:+.0f} ms off its EDL position"
        add(L['status'], f"loudness (measured on the MP4): {L.get('lufs')} LUFS (target {L.get('lufs_target')} ± "
            f"{L.get('lufs_tol')}), true peak {L.get('true_peak')} dBTP (max {L.get('tp_max')})" + extra)
    fr = c['frames']
    parts = []
    for name in ('black', 'white', 'frozen'):
        un = [x for x in fr[name] if 'unplanned' in x]
        if un:
            parts.append(f"unplanned {name} " + ', '.join(f"{x['unplanned'][0]}-{x['unplanned'][1]}" for x in un[:4]))
    if fr['edl_gaps']:
        parts.append('EDL gaps ' + ', '.join(f'{a}-{b}' for a, b in fr['edl_gaps'][:4]))
    if fr.get('slow_ramps'):
        parts.append('slow motion below 0.4x from <= 30 fps sources (synthesized frames show): ' + ', '.join(
            f"{x['seg']} {x['min_rate']:g}x at f{x['at']} ({x['src_fps']:g} fps)" for x in fr['slow_ramps'][:4]))
    planned = sum(1 for nm in ('black', 'white', 'frozen') for x in fr[nm] if 'unplanned' not in x)
    add(fr['status'], 'black/white/frozen: ' + ('; '.join(parts) if parts else f'none unplanned ({planned} planned runs)'))
    fl = c['flashes']
    g, rd = fl['general'], fl['red']
    msg = f"flashes: worst {g['worst_per_s']}/s"
    if g['worst_t']:
        msg += f" at {g['worst_t'][0]}-{g['worst_t'][1]} s (frames {g['worst_window'][0]}-{g['worst_window'][1]})"
    msg += f", limit {g['limit_hz']:g}/s; red worst {rd['worst_per_s']}/s (limit {rd['limit_hz']:g})"
    if g['over_limit_ranges']:
        msg += f"; over the limit in frames {', '.join(f'{a}-{b}' for a, b in g['over_limit_ranges'][:4])}"
    add(fl['status'], msg)
    sz = c['safe_zone']
    ex = sz.get('exempt') or {}
    ex_txt = (' (not checked: ' + ', '.join(f'{v} {k}' for k, v in ex.items()) + ')') if ex else ''
    if sz['status'] == 'skipped':
        add('skipped', f"safe zone: skipped {'; '.join(sz.get('notes') or [])}")
    elif sz['status'] == 'fail':
        v = sz['violations']
        add('fail', f"safe zone ({sz['zone']}): {len(v)} of {sz['items']} text items outside{ex_txt} — " + '; '.join(
            f"'{(x.get('text') or x.get('id', ''))[:14]}' f{x['f0']}-{x['f1']} "
            f"{','.join(f'{k} {v_:.0f}px' for k, v_ in x['outside_px'].items())}" for x in v[:4]))
    else:
        add('ok', f"safe zone ({sz['zone']}): {sz['items'] - sum(ex.values())} text items inside{ex_txt}"
            + (f" ({'; '.join(sz['notes'])})" if sz.get('notes') else ''))
    fc = c['faces']
    if fc['status'] == 'skipped':
        add('skipped', f"faces: skipped — {fc.get('note')}")
    else:
        parts = []
        if fc['render']['edge_cut']:
            parts.append(f"{len(fc['render']['edge_cut'])} faces cut by the frame edge ("
                         + ', '.join(f"f{x['f']} {x['seg']}" for x in fc['render']['edge_cut'][:4]) + ')')
        if fc['render']['text_over_face']:
            parts.append(f"text over a face at {', '.join('f' + str(x['f']) for x in fc['render']['text_over_face'][:4])}")
        si = fc.get('subject_issues') or []
        if si:
            parts.append('crop cuts or drops the main face of the source in ' + ', '.join(
                f"{x['seg']} ({int(x['coverage'] * 100)}% inside)" for x in si[:5]))
        add(fc['status'], 'faces: ' + ('; '.join(parts) if parts else
                                        f"{fc['render']['faces']} faces in {fc['render']['frames_checked']} frames, none cut; "
                                        f"{len(fc.get('subject') or [])} source frames checked"))
    im = c['image']
    o = im['overall']
    ng = sum(1 for s in im.get('segments') or [] if s.get('gap'))
    if o:
        msg = (f"image: luma mean {o.get('luma_mean')}, p1 {o.get('p1')}, p99 {o.get('p99')}, clipped {o.get('clip_lo')}% / "
               f"{o.get('clip_hi')}%, saturation {o.get('sat_mean')}") + (f" ({ng} slate segments not measured)" if ng else '')
    else:
        msg = f"image: nothing measured ({ng} slate segments)" if ng else 'image: nothing measured'
    if im['out_of_range_segments']:
        msg += f"; outside qa.color in {', '.join(im['out_of_range_segments'][:6])}"
    if im.get('brightness_jumps'):
        msg += '; brightness jumps > 20 % at hard cuts: ' + ', '.join(
            f"f{x['f']} {x['prev']}|{x['next']} {x['change'] * 100:+.0f} %" for x in im['brightness_jumps'][:5])
    add(im['status'], msg)
    sp = c.get('speech') or {}
    if sp.get('status') == 'skipped' or not sp:
        add('skipped', f"speech: skipped — {sp.get('note')}")
    else:
        bits = []
        fw = sp.get('first_word') or []
        if fw:
            bits.append('first word ' + ', '.join(f"{x['lag_s']:+.2f} s" for x in fw[:3]))
        pa = sp.get('pauses')
        if pa is not None:
            jc = [p for p in pa if p.get('jump_cut') is not None and not p.get('allowed')]
            how = 'measured on the voice audio' if sp.get('voice_activity') else 'from word timestamps'
            bits.append(f"{len(jc)} pauses > {sp['thresholds']['max_pause']:g} s at jump cuts ({how})"
                        + (f" ({len(pa) - len(jc)} others: by design / allowed / inside shots)" if len(pa) > len(jc) else ''))
        st = sp.get('subtitles') or {}
        bits.append(f"{st.get('items', 0)} subtitle chunks, {len(st.get('bad') or [])} too fast / short / long")
        vc = sp.get('visual_change') or []
        if vc:
            bits.append('longest talk stretch without a visual change ' + ', '.join(f"{x['longest_s']} s" for x in vc[:3]))
        if sp.get('seams') is not None:
            bits.append(f"{sum(1 for s in sp['seams'] if s.get('click'))} clicks at {len(sp['seams'])} audio seams")
        if sp.get('voice_over_music_db') is not None:
            bits.append(f"voice {sp['voice_over_music_db']:+.1f} dB over the music")
        ls_ = [x for x in sp.get('lip_sync') or [] if 'offset_frames' in x]
        if ls_:
            bits.append('lip sync ' + ', '.join(
                (f"audio {x['offset_frames']:+.1f} fr late" if x.get('confident') else f"no clear lag (r {x.get('r')})")
                + f" ({x['part']})" for x in ls_[:3]))
        add(sp['status'], 'speech: ' + '; '.join(bits) + (' — ' + '; '.join(sp['issues']) if sp.get('issues') else ''))
    pt = c.get('parts') or {}
    if pt.get('status') == 'skipped' or not pt:
        add('skipped', f"parts: skipped — {pt.get('note')}")
    else:
        ps = ' | '.join(f"{p['id']} {p['type']} {p['f0']}-{p['f1']}"
                        + (f" ({', '.join(str(p[k]) for k in ('style', 'variant') if p.get(k) is not None)})"
                           if p.get('style') is not None or p.get('variant') is not None else '') for p in pt['parts'])
        bits = [ps + ('' if pt.get('declared') else ' (inferred from audio.voice)')]
        for b in pt.get('boundaries') or []:
            d = b.get('drop') or {}
            if d.get('status') in ('ok', 'fail', 'warn') and d.get('offset_frames') is not None:
                where = f"f{b['f']} cut {b.get('cut')}" if not b.get('requested') else f"f{b['f']} ({b['requested']})"
                bits.append(f"{where}, music {'drop' if d.get('clear') else 'downbeat'} "
                            f"{d['offset_frames']:+.1f} fr" + (f" (+{d['strength_db']:.1f} dB)" if d.get('strength_db') else ''))
            elif b.get('cut'):
                bits.append(f"f{b['f']} cut {b['cut']}" + (f", drop: {d.get('note')}" if d.get('note') else ''))
        tf = pt.get('talk_framing')
        if tf:
            bits.append(f"talk framing: {tf['samples']} samples, median render fidelity {tf.get('median_fidelity')} "
                        f"(<= {FID_BAD} = the EDL's crop), crop keeps the face {tf.get('crop_keeps_face_share')}, "
                        f"face shown in the render {tf.get('face_in_frame_share')}"
                        + (f" ({tf['face_hidden']} with the face turned away / covered, person in the crop)"
                           if tf.get('face_hidden') else ''))
        if pt.get('overlays') is not None:
            found = sum(int(m_.group(1)) for n_ in pt.get('overlay_notes') or [] for m_ in [re.search(r'(\d+) static overlay', n_)] if m_)
            bits.append(f"static overlays: {found} found in the talk sources, "
                        f"{len([o for o in pt['overlays'] if not o.get('inpainted')])} inside the talk crops")
        problems = (pt.get('issues') or []) + (pt.get('warnings') or [])
        add(pt['status'], 'parts: ' + '; '.join(bits) + (' — ' + '; '.join(problems) if problems else ''))
    sx = c.get('sfx') or {}
    if sx.get('status') == 'skipped' or not sx:
        add('skipped', f"sfx: skipped — {sx.get('note')}")
    else:
        nv_ = sum(1 for g_ in sx.get('groups') or [] if g_.get('method') == 'stems')
        msg = (f"sfx: {sx['events']} events in {sx['measured_groups']} groups ({nv_} on re-mixed stems verified against "
               f"the MP4, {sx['measured_groups'] - nv_} on the MP4 minus the music / voice stems; mix corr {sx.get('stems_corr')})")
        if sx.get('weak'):
            msg += '; weak: ' + ', '.join(f"f{w['f']} {'+'.join(w['kinds'])} {w['rel_lu']:+.1f} LU (need {w['need_lu']:+g}"
                                          + (f", the mixer's floor already lifted it {w['floor_db']:+.1f} dB"
                                             if (w.get('floor_db') or 0) > 0.05 else '') + ')'
                                          for w in sx['weak'][:5])
        elif not sx.get('unverified'):
            msg += '; all checked events loud enough over the music'
        if sx.get('unverified'):
            msg += (f"; {len(sx['unverified'])} group(s) only as an upper bound, not proven loud enough (the re-mix differs "
                    f"from the render there: another mixer version? re-render to verify): "
                    + ', '.join(f'f{f}' for f in sx['unverified'][:5]))
        if sx.get('mixer_disagrees'):
            msg += '; the mixer measured otherwise at ' + ', '.join(
                f"f{x['f']} (QA {x['qa_rel_lu']:+.1f}, mixer {float((x.get('mixer') or {}).get('rel_lu', (x.get('mixer') or {}).get('st_lu', 0))):+.1f} LU)"
                for x in sx['mixer_disagrees'][:3])
        add(sx['status'], msg)
    lines.sort(key=lambda x: -x[0])
    return [f'{lab} {txt}' for _, lab, txt in lines]


def write_md(res, path):
    c = res['checks']
    L = []
    L.append(f"# QA {os.path.basename(res['video'])} vs {os.path.basename(res['edl'])}")
    L.append('')
    nf = sum(1 for v in c.values() if v.get('status') == 'fail')
    nw = sum(1 for v in c.values() if v.get('status') == 'warn')
    L.append(f"**{res['status'].upper()}** ({nf} fail, {nw} warn) · genre {res['config'].get('genre') or 'not set'} "
             f"({res['config']['mode']} rules) · {c['format']['frames']} frames, {c['format']['duration']} s · analysed in "
             f"{res['timing']['total']} s")
    L.append('')
    for v in res['verdict_lines']:
        L.append(f'- {v}')
    L.append('')
    if res.get('gaps'):
        L.append(f"## Gaps to fill ({len(res['gaps'])} storyboard slots: generate with edit-gen, then ed_plan.fill_gaps / "
                 f"edit.py fill)")
        L.append('')
        L.append('| slot | frames | time s | needs s | part / role | shot | subject | camera |')
        L.append('|---|---|---|---|---|---|---|---|')
        for x in res['gaps']:
            L.append(f"| {x['id']} | {x['f'][0]}-{x['f'][1]} | {x['t'][0]}-{x['t'][1]} | {x.get('need_s')} | "
                     f"{x.get('part')} / {x.get('role')} | {x.get('shot') or ''} | {str(x.get('subject') or '')[:48]} | "
                     f"{x.get('camera') or ''} |")
        L.append('')
    segs = [s for s in c['image']['segments'] if 'luma_mean' in s]
    if segs:
        def spread(k):
            v = [s[k] for s in segs if s.get(k) is not None]
            return f"{min(v)}-{max(v)} (median {round(float(np.median(v)), 3)})" if v else '-'
        L.append('## Look across segments (luma 0-255, saturation 0-1; per-segment table in qa.json checks.image)')
        L.append('')
        L.append(f"luma mean {spread('luma_mean')} · p1 {spread('p1')} · p99 {spread('p99')} · clipped shadows % "
                 f"{spread('clip_lo')} · highlights % {spread('clip_hi')} · saturation {spread('sat_mean')} · "
                 f"mono {sum(bool(s.get('mono')) for s in segs)}/{len(segs)}")
        bad = [s for s in segs if s.get('out_of_range')]
        if bad:
            L.append('')
            L.append('| seg | frames | outside qa.color |')
            L.append('|---|---|---|')
            for s in bad:
                L.append(f"| {s['seg']} | {s['f0']}-{s['f1']} | {', '.join(f'{k} {v}' for k, v in s['out_of_range'].items())} |")
        L.append('')
    L.append('## Files')
    L.append('')
    for k, v in res['files'].items():
        if v:
            L.append(f"- {k}: {', '.join(os.path.basename(x) for x in (v if isinstance(v, list) else [v]))}")
    L.append('')
    open(path, 'w', encoding='utf-8').write('\n'.join(L))


# ============================================================================ main
def _unreadable(edl_path, video_path, out_dir, n_edl, nv, info):
    """The render cannot be measured (missing, not a video, < 2 frames): one FAIL line, same files and keys."""
    msg = f'FAIL format: {nv} frames could be decoded from {os.path.basename(video_path)} (EDL has {n_edl})'
    res = dict(version=2, edl=os.path.abspath(edl_path), video=os.path.abspath(video_path), status='fail',
               checks={'format': check('fail', frames=nv, n_frames=n_edl, problems=[msg[13:]])}, verdict=[msg],
               verdict_lines=[msg], duration=(info or {}).get('duration'), cuts_on_grid_share=None, lufs=None,
               true_peak=None, files={'json': os.path.join(out_dir, 'qa.json'), 'md': os.path.join(out_dir, 'qa.md')})
    json.dump(res, open(res['files']['json'], 'w'), indent=1, ensure_ascii=False)
    open(res['files']['md'], 'w', encoding='utf-8').write(f"# QA {os.path.basename(video_path)}\n\n**FAIL**\n\n- {msg}\n")
    return res


def load_render_sidecar(video_path):
    """<render>.render.json written by ed_edl (transition windows, audio mix info), or {}."""
    p = video_path + '.render.json'
    if not os.path.exists(p):
        return {}
    try:
        d = json.load(open(p))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def run(edl_path, video_path, out_dir, faces=True, source_check=True, sheets=True):
    T = {}
    t_all = time.time()
    os.makedirs(out_dir, exist_ok=True)
    edl, fmt = load_edl(edl_path)
    edl_dir = os.path.dirname(os.path.abspath(edl_path))
    q = qa_config(edl, edl_dir)
    fps = float(edl['canvas']['fps'])
    n_edl = int(edl.get('n_frames') or (max(s['f1'] for s in edl['segments']) + 1))
    try:
        info = V.probe(video_path)
    except (subprocess.CalledProcessError, OSError, ValueError, KeyError):
        info = None
    if not info or not info.get('w'):
        return _unreadable(edl_path, video_path, out_dir, n_edl, 0, info)
    side = load_render_sidecar(video_path)
    if side.get('edl_md5') and fmt == 'edl':
        try:
            import hashlib
            if hashlib.md5(json.dumps(edl, sort_keys=True, default=str).encode()).hexdigest() != side['edl_md5']:
                side = dict(side, transitions=None, stale=True)      # rendered from another version of the EDL
        except (TypeError, ValueError):
            pass
    plan = Plan(edl, q, n_edl, rendered_windows=side.get('transitions'))
    plan.edl_dir = edl_dir
    # storyboard slots still to fill (slates): reported as gaps, not measured as pictures
    sb_gaps, gap_idx, planner_gaps = storyboard_gaps(edl) if fmt == 'edl' else ([], set(), [])
    plan.gap_segs = gap_idx
    plan.slate_frames = {f for si in gap_idx for f in range(int(plan.segs[si]['f0']), int(plan.segs[si]['f1']) + 1)}
    srcs_res = {k: dict(v, path=_resolve(v.get('path'), edl_dir)) for k, v in (edl.get('sources') or {}).items()
                if isinstance(v, dict)}
    parts, talk_src = edl_parts(edl, q, n_edl, edl_dir)
    composite = len(parts) > 1 or any(p['type'] == 'talk' for p in parts)
    au = edl.get('audio') or {}
    has_voice = bool(au.get('voice'))
    pool = ThreadPoolExecutor(max_workers=2)

    def audio_job():
        if not info.get('has_audio'):
            return None, None, None, None
        t0 = time.time()
        L = loudness(video_path)
        T['loudness'] = round(time.time() - t0, 2)
        actx, grid, aud = None, None, None
        need_ctx = not au.get('copy') and (au.get('sfx') or has_voice or composite or q.get('drop_f') is not None
                                           or q.get('drop_at') is not None)
        if need_ctx:
            try:
                actx = AudioCtx(edl, edl_dir, video_path, out_dir, n_edl, fps, want_stems=bool(au.get('sfx') or has_voice))
                T.update({f'audio_{k}': v for k, v in actx.T.items()})
                if actx.music is not None:
                    t1 = time.time()
                    grid = music_grid(actx)
                    T['music_grid'] = round(time.time() - t1, 2)
            except Exception as e:  # references unreadable: the checks that need them are skipped
                actx = None
                T['audio_ctx_error'] = repr(e)
        try:
            if q['mode'] == 'music' or composite:
                if (has_voice or composite) and grid and not grid.get('error'):
                    aud = grid                                         # the voice would mislead the beat tracker
                else:
                    import ed_audio as A
                    aud = A.analyze(video_path)
        except Exception as e:
            aud = {'error': repr(e)}
        T['audio'] = round(time.time() - t0, 2)
        return L, aud, actx, grid

    samples = talk_samples(plan, parts, talk_src) if (faces and source_check and fmt == 'edl' and composite) else {}
    talk_segs = set(samples.values())
    reqs = [rq for rq in source_requests(plan, n_edl) if rq['si'] not in talk_segs] \
        if (faces and source_check and fmt == 'edl') else []                  # talk segments: denser talk framing
    treqs = talk_requests(plan, samples)
    for rq in treqs:
        if srcs_res.get(rq['src']) is None or not os.path.exists(srcs_res[rq['src']].get('path') or ''):
            rq['skip'] = True
    treqs = [rq for rq in treqs if not rq.get('skip')]

    def src_job():
        t0 = time.time()
        out = dict(subject=([], [], {}), talk={}, overlays=None)
        if reqs:
            got = fetch_source_frames(reqs, srcs_res)
            rows, issues = analyse_subject(plan, reqs, got, edl['canvas'])
            out['subject'] = (rows, issues, got)
        if treqs:
            out['talk'] = fetch_source_frames(treqs, srcs_res)
        if source_check and fmt == 'edl' and any(p['type'] == 'talk' for p in parts):
            out['overlays'] = analyse_overlays(plan, parts, talk_src, edl['canvas'])
            t1 = time.time()
            try:
                out['lipsync'] = analyse_lipsync(video_path, parts, fps)
            except Exception as e:  # never let the lip-sync estimate break QA
                out['lipsync'] = [dict(error=repr(e)[:200])]
            T['lipsync'] = round(time.time() - t1, 2)
        out['t'] = round(time.time() - t0, 2)
        return out

    fut_src = pool.submit(src_job) if (reqs or treqs or (source_check and composite)) else None
    fut_audio = pool.submit(audio_job)

    # ---- one pass over the render
    t0 = time.time()
    keep = (set(face_samples(plan, n_edl)) | set(samples)) if faces else set()
    small, full, label_frac, (dw, dh) = decode(video_path, info, keep)
    nv = len(small)
    if nv < 2:                                     # nothing to measure: report and stop
        pool.shutdown(wait=False, cancel_futures=True)
        return _unreadable(edl_path, video_path, out_dir, n_edl, nv, info)
    label_box = scrub_label(small, label_frac, label_region(side), edl['canvas'], full)
    gray = np.stack([cv2.cvtColor(x, cv2.COLOR_RGB2GRAY) for x in small])
    T['decode'] = round(time.time() - t0, 2)
    n = min(nv, n_edl)

    # ---- 1 format
    cv_ = edl['canvas']
    scale = info['w'] / cv_['w'] if cv_['w'] else 1.0
    probs = []
    if nv != n_edl:
        probs.append(f'{nv} frames decoded, EDL has {n_edl}')
    if abs(info['fps'] - fps) > 0.01:
        probs.append(f"fps {info['fps']} vs EDL {fps:g}")
    if abs(info['w'] / info['h'] - cv_['w'] / cv_['h']) > 0.01:
        probs.append(f"aspect {info['w']}x{info['h']} vs canvas {cv_['w']}x{cv_['h']}")
    dur_exp = n_edl / fps                          # the decoded frame count is the exact length check
    a_dur = None
    if info.get('has_audio'):
        try:
            a_dur = float(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
                                          'stream=duration', '-of', 'csv=p=0', video_path],
                                         capture_output=True, text=True).stdout.strip().split('\n')[0])
            if abs(a_dur - dur_exp) > 0.1:
                probs.append(f'audio {a_dur:.3f}s vs video {dur_exp:.3f}s')
        except ValueError:
            pass
    overlaps = [f"{b['prev']}|{b['next']} by {b['overlap']}" for b in plan.boundaries if b.get('overlap')]
    if overlaps:
        probs.append('overlapping segments ' + ', '.join(overlaps[:4]))
    fmt_status = 'fail' if any(p_.startswith(('fps', 'aspect')) or 'frames decoded' in p_ for p_ in probs) else ('warn' if probs else 'ok')
    checks = {}
    checks['format'] = check(fmt_status, frames=nv, n_frames=n_edl, fps=info['fps'], size=[info['w'], info['h']],
                             canvas=[cv_['w'], cv_['h']], scale=r(scale, 3), duration=r(info['duration'], 3),
                             audio_duration=r(a_dur, 3), problems=probs, source_format=fmt,
                             label_overlay=bool(label_box))

    # ---- 2 cuts
    t0 = time.time()
    sig = CutSignal(gray[:n], plan.inverted)
    checks['cuts'], D, D_raw = analyse_cuts(sig, plan, nv)
    mark_gap_boundaries(checks['cuts'], plan)
    if source_check and fmt == 'edl' and checks['cuts']['unexpected']:
        verify_unexpected(checks['cuts'], plan, srcs_res)
    T['cuts'] = round(time.time() - t0, 2)

    # ---- 4 frames, 5 flashes, 8 image
    t0 = time.time()
    checks['frames'], still = analyse_frames(gray, plan, q, nv)
    if source_check and fmt == 'edl' and checks['frames']['unplanned_frozen']:
        verify_frozen(checks['frames'], plan, srcs_res)
    if fmt == 'edl':
        sr_ = slow_ramps(plan, q, srcs_res)
        if sr_:
            checks['frames']['slow_ramps'] = sr_
            if checks['frames']['status'] == 'ok':
                checks['frames']['status'] = 'warn'
    T['frames'] = round(time.time() - t0, 2)
    t0 = time.time()
    checks['flashes'] = analyse_flashes(small, plan, q, nv)
    T['flashes'] = round(time.time() - t0, 2)
    t0 = time.time()
    checks['image'] = image_stats(small, plan, q, nv)
    bj = brightness_jumps(small, plan, checks['cuts'], parts, nv)
    if bj:
        checks['image']['brightness_jumps'] = bj
        if checks['image']['status'] == 'ok':
            checks['image']['status'] = 'warn'
    T['image'] = round(time.time() - t0, 2)

    # ---- 6 safe zone
    t0 = time.time()
    checks['safe_zone'] = analyse_safe_zone(edl, q, scale, video_path, n_edl)
    T['safe_zone'] = round(time.time() - t0, 2)
    text_items = [it for it in checks['safe_zone'].get('all_items') or [] if not it.get('exempt')]

    # ---- 7 faces (+ the source side of the talk framing, overlays: source thread)
    t0 = time.time()
    sj = None
    if fut_src is not None:
        try:
            sj = fut_src.result()
            T['source_job'] = sj.get('t')
        except Exception as e:  # source unreadable etc.
            sj = dict(error=repr(e), subject=([dict(error=repr(e))], [], {}), talk={}, overlays=None)
    if faces:
        fr_res = analyse_faces_render(full, face_samples(plan, nv), plan, text_items, dw / cv_['w'])
        subj_rows, subj_issues, got = sj['subject'] if sj else ([], [], {})
        st = 'warn' if (fr_res['edge_cut'] or fr_res['text_over_face'] or subj_issues) else 'ok'
        checks['faces'] = check(st, render=fr_res, subject=subj_rows,
                                subject_issues=[{k: v for k, v in x.items() if k != '_i'} for x in subj_issues])
    else:
        checks['faces'] = check('skipped', note='disabled')
        subj_issues, got = [], {}
    talk_rows = []
    if treqs and sj is not None:
        ff = {f for it in checks['safe_zone'].get('all_items') or [] if it.get('exempt') == 'full frame'
              for f in range(int(it['f0']), int(it['f1']) + 1)}
        talk_rows = analyse_talk_framing(plan, treqs, sj.get('talk') or {}, full, small, cv_, text_items, label_box, scale,
                                         ff)
    T['faces'] = round(time.time() - t0, 2)

    # ---- 3 loudness + rhythm (audio thread)
    t0 = time.time()
    try:
        L, aud, actx, grid = fut_audio.result()
    except Exception as e:  # ffmpeg / analysis failure must not kill the other checks
        L, aud, actx, grid = None, {'error': repr(e)}, None, None
    pool.shutdown(wait=False)
    T['audio_wait'] = round(time.time() - t0, 2)
    checks['loudness'] = judge_loudness(L, q, side.get('audio'))
    if actx is not None and actx.sync is not None:
        checks['loudness']['music_sync'] = actx.sync
    events = cut_events(checks['cuts'], plan)
    checks['rhythm'] = analyse_rhythm(events, plan, q, aud, n_edl / fps, parts if composite else None)

    # ---- 10 speech, 11 parts, 12 sfx
    t0 = time.time()
    sfr = sidecar_frames(video_path, cv_)
    try:
        checks['speech'] = analyse_speech(plan, q, parts, checks['cuts'], actx, edl, sfr, n,
                                          av=(sj or {}).get('lipsync'))
    except Exception as e:  # a broken speech check must not hide the others
        checks['speech'] = check('skipped', note=f'speech check failed: {e!r}')
    try:
        checks['parts'] = analyse_parts(parts, talk_src, plan, checks['cuts'], actx, grid, talk_rows,
                                        sj.get('overlays') if sj else None, q, n_edl)
    except Exception as e:
        checks['parts'] = check('skipped', note=f'parts check failed: {e!r}')
    try:
        checks['sfx'] = analyse_sfx(edl, q, actx, fps, side.get('audio') if not side.get('stale') else None)
    except Exception as e:
        checks['sfx'] = check('skipped', note=f'sfx check failed: {e!r}')
    T['speech_parts_sfx'] = round(time.time() - t0, 2)

    # legacy keys + verdict
    res = dict(version=3, edl=os.path.abspath(edl_path), video=os.path.abspath(video_path), config={
        k: v for k, v in q.items() if k not in ('words',)}, checks=checks)
    res['config']['n_words'] = len(q['words'])
    res['parts'] = [{k: v for k, v in p.items() if k != 'segs'} for p in parts]
    if sb_gaps:
        sb = (edl.get('meta') or {}).get('storyboard') or {}
        n_slots = len([s_ for s_ in sb.get('slots') or [] if isinstance(s_, dict) and s_.get('kind') != 'black'])
        res['storyboard'] = dict(slots=max(n_slots, len(sb_gaps)), to_fill=len(sb_gaps),
                                 filled=len(sb.get('filled') or {}))
        res['gaps'] = sb_gaps
        res['gaps_to_fill'] = len(sb_gaps)
    if planner_gaps:
        res['planner_gaps'] = planner_gaps
    if side.get('stale'):
        res.setdefault('notes', []).append('render sidecar is from another version of the EDL: its windows were ignored')
    order = ['format', 'cuts', 'rhythm', 'loudness', 'frames', 'flashes', 'safe_zone', 'faces', 'image', 'speech',
             'parts', 'sfx']
    res['checks'] = {k: checks[k] for k in order}
    worst = max(LEVELS[v['status']] for v in checks.values())
    res['status'] = {0: 'pass', 1: 'warn', 2: 'fail'}[worst]

    # ---- 9 sheets & plots
    t0 = time.time()
    files = dict(json=os.path.join(out_dir, 'qa.json'), md=os.path.join(out_dir, 'qa.md'))
    if sheets and nv:
        files['cuts'] = cut_sheets(small, checks['cuts'], plan, out_dir, nv)
        tiles = []
        H_, W_ = small.shape[1], small.shape[2]
        sx = W_ / cv_['w']
        zone = checks['safe_zone'].get('zone_box')
        zb = [zone['x0'] * W_, zone['y0'] * H_, zone['x1'] * W_, zone['y1'] * H_] if zone else None
        for v in (checks['safe_zone'].get('violations') or [])[:6]:
            f = min(n - 1, (v['f0'] + v['f1']) // 2)
            bx = [c_ * sx for c_ in v['box']]
            tiles.append((small[f], f"safe zone f{f}: '{v.get('text', '')[:16]}' out {','.join(v['outside_px'])}",
                          ([(zb, (60, 200, 90))] if zb else []) + [(bx, (255, 40, 40))], 1))
        for x in checks['faces'].get('render', {}).get('edge_cut', [])[:4] if faces else []:
            f = x['f']
            bx = [x['box'][0] * W_, x['box'][1] * H_, x['box'][2] * W_, x['box'][3] * H_]
            tiles.append((small[f], f"face cut by {','.join(x['sides'])} edge f{f} {x['seg']}", [(bx, (255, 40, 40))], 1))
        for x in subj_issues[:4]:
            g = got.get(x['_i'])
            if g is None:
                continue
            s_ = g['scale']
            wbox = [v * s_ for v in x['window']]
            fbox = [v * s_ for v in x['main_face']]
            span = 3 if g['frame'].shape[1] > 1.5 * g['frame'].shape[0] else 2
            tiles.append((g['frame'], f"{x['seg']} f{x['f']}: crop (green) keeps {int(x['coverage'] * 100)}% of the main face "
                          f"(red), source {x['src_t']} s", [(wbox, (60, 200, 90)), (fbox, (255, 40, 40))], span))
        for name in ('black', 'white', 'frozen'):
            for x in [y for y in checks['frames'][name] if 'unplanned' in y][:3]:
                f = x['unplanned'][0]
                if f < n:
                    tiles.append((small[f], f"unplanned {name} f{x['unplanned'][0]}-{x['unplanned'][1]} "
                                  f"{','.join(map(str, x['segs']))[:24]}", [], 1))
        for key in ('general', 'red'):
            g = checks['flashes'][key]
            if g['fail'] and g['worst_window']:
                tiles.append((flash_strip(small, g, n), f"{key} flashes: worst window f{g['worst_window'][0]}-"
                              f"{g['worst_window'][1]}, {g['worst_per_s']}/s (yellow up, blue down)", [], 3))
        tiles += talk_tiles(talk_rows, treqs, (sj or {}).get('talk') or {}, small, plan, cv_)
        files['issues'] = issue_sheet(tiles, out_dir)
        try:
            dur = n_edl / fps
            if checks['rhythm']['status'] != 'skipped' or q['mode'] == 'speech':
                files['rhythm'] = os.path.join(out_dir, 'qa_rhythm.png')
                plot_rhythm(checks['rhythm'], aud, events, fps, dur, files['rhythm'], q['words'], parts)
            if L is not None:
                files['loudness'] = os.path.join(out_dir, 'qa_loudness.png')
                plot_loudness(L, q, events, fps, dur, files['loudness'])
        except Exception as e:  # plotting must never break QA
            res.setdefault('notes', []).append(f'plot failed: {e!r}')
    T['sheets'] = round(time.time() - t0, 2)
    T['total'] = round(time.time() - t_all, 2)
    res['timing'] = T
    res['files'] = files
    res['verdict_lines'] = verdict_lines(res)
    res['verdict'] = [v for v in res['verdict_lines'] if not v.startswith(('ok ', 'SKIPPED'))] or ['ok']
    # legacy top-level keys (edit.py prints these)
    res['duration'] = checks['format']['duration']
    res['expected'] = r(n_edl / fps, 3)
    res['cuts_on_grid_share'] = checks['rhythm'].get('share') if checks['rhythm'].get('mode') in ('beats', 'parts') else None
    res['lufs'] = checks['loudness'].get('lufs')
    res['true_peak'] = checks['loudness'].get('true_peak')
    if L is not None:
        res['loudness_series'] = dict(t=L['series']['t'], S=L['series']['S'])
    res['cut_signal'] = dict(mc=[r(v, 3) for v in D.tolist()], raw=[r(v, 3) for v in D_raw.tolist()])
    json.dump(res, open(files['json'], 'w'), indent=1, ensure_ascii=False)
    write_md(res, files['md'])
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('edl', help='EDL json (or old timeline json)')
    ap.add_argument('video', help='rendered file')
    ap.add_argument('out', help='output dir')
    ap.add_argument('--no-faces', action='store_true', help='skip face / subject checks')
    ap.add_argument('--no-source', action='store_true', help='skip decoding source frames for the crop-vs-subject check')
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    res = run(a.edl, a.video, a.out, faces=not a.no_faces, source_check=not a.no_source)
    if not a.quiet:
        print('\n'.join([f"QA {res['status'].upper()} ({res['timing']['total']} s) -> {res['files']['md']}"] + res['verdict_lines']))
    sys.exit(0)


if __name__ == '__main__':
    main()
