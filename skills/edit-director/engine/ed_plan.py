#!/usr/bin/env python3
"""Genre planner — scenario 2: track + user footage + genre card -> finished edit as an EDL (engine/TIMELINE.md).

  python3 -I ed_plan.py plan --track T.wav --footage a.mp4 b.mp4 ... --genre phonk --out edl.json
                             [--style WORDS|NAME] [--variant N] [--avoid v1.json v2.json]   (--genre optional with --style)
                             [--dur 20] [--fps 30] [--canvas 1080x1920] [--cache DIR] [--seed 1]
                             [--title TEXT] [--word WORD] [--outro-text TEXT] [--no-reframe]
                             [--n-shots N] [--order auto|given] [--require IDS] [--forbid IDS] [--music-in S]
                             [--drop-at S] [--drop-t S] [--bpm B] [--bars N] [--cut-rate X] [--sfx-level L]
                             speech genres: [--words W.json] [--lang xx] [--src-in S --src-out S | --from P --to P]
                             [--subtitles karaoke|subtitle|none]   motivation: [--voice VOICE.wav]   (--track optional)
  python3 -I ed_plan.py storyboard --track T.wav (--genre G | --style WORDS) [--brief TEXT] [--character TEXT]
                             [--dur S] [--n-shots N] --out storyboard.json       # every slot a gap with an edit-gen brief
  python3 -I ed_plan.py fill EDL.json MAP.json [--out EDL2.json]     # {slot: clip | {path, t}} into the gap slots
  python3 -I ed_plan.py styles [WORDS]                               # the house styles, or which one the words mean
  python3 -I ed_plan.py apply EDL.json CMD.json [--out EDL2.json]   # point edit from a structured command
  python3 -I ed_plan.py validate EDL.json                            # contract check against TIMELINE.md
  python3 -I ed_plan.py explain EDL.json                             # slot table with the reasoning (composites: per part)
  python3 -I ed_plan.py remake ...                                   # legacy scenario-1 planner (legacy_plan.py)

plan_genre(track, footage, genre, canvas, fps, dur=None, **opts) — opts (norm_opts validates them):
  n_shots N          exactly N shots; a cut always lands on the drop beat; even lengths on the beat grid (one bar each
                     when N divides the bars)
  order 'given'      shot i comes from footage item i (repeating in order when there are fewer clips); the window
                     inside the clip is still chosen (action peak on the accent); 'auto' = scored assignment
  require_moves      ids or families that must appear: allowed everywhere even over the card's own ban; time.speed_ramp
                     = a ramp on every shot of an n_shots plan (else on the drop shots, 1 per bar), time.slow_motion /
                     time.velocity / time.freeze set speeds; a missing accent goes on the drop's first inner beat
  forbid_moves       ids or families never placed (genre_view removes them from every list, sounds included)
  music_in (start)   track second shown at output 0 (start offset; snapped to a beat within 60 ms)
  drop_at            output second where the strongest drop lands (drop_t overrides the detector's drop); with
                     music_in it names the drop beat; parts are then cut around it (empty hook / build allowed)
  bars / dur         length in whole bars or seconds;  bpm  tempo hint for the beat tracker
  cut_rate X         x the card's cutting rate: plain shots split at strong beats (X > 1) or merge (X < 1)
  sfx_level          none | light (the section switch only: the hits on the drop) | genre = normal (card program + a low
                     thump on every speed-ramp brake + a whoosh into the switch - a card without whooshes: its short
                     riser; hype genres: strong drop / accent hits, whooshes under fast transitions) | heavy = strong
                     (+ a whoosh on every ramp speed-up, a riser into every section, a hit on every downbeat cut of the
                     drop, a sub drop under the drop hit); every sound carries ed_sfx `level`; event times through
                     ed_sfx.event_anchor (ev_at: "at" events and "t" ranges)
  interp             True: deep slow motion from < 50 fps sources is accepted (optical-flow frames): the ramps' slow
                     floor drops from 0.4x to 0.25x (slow_floor; 50+ fps sources always allow 0.25x)
  in_sequence        first | middle | last: a part of an ed_sequence composite — the opening structure (fade / flash in,
                     opening ops, titles) only on the first part, the closing one (fade to black, black tail, music
                     stop, end titles) only on the last, never letterbox changes
  footage items      paths or {path, name, role (hero | broll | aroll | voice), weight, t0, t1} (several sources;
                     t0/t1 limit a source range; a hero clip is preferred for the drop / hook / freeze)
  speech genres      words (list | transcript | JSON path), lang, asr_model, src_in/src_out or from/to phrases,
                     subtitles, music_db, fillers; motivation: voice (voice-over file) or a footage item role 'voice'
  check_dark         True (default): chosen windows whose analysis dips dark are decoded at the source rate and graded
                     like the render; a window that goes near-black (the QA's black test) is re-picked (_dark_check)
  fit_grades         True (default): every shot's grade is fitted to the card's colour targets (COLOR_TARGETS: p1 / p99 /
                     mean luma / saturation, the qa.color ranges) on decoded frames of its crop (_fit_grades); a face
                     never goes into clipping (face p99 <= 238) and no more of the picture clips than the start (~1 %);
                     picture limits (PICTURE_LIMITS) for every look: <= 7 % of pixels crushed to black and a mean luma
                     >= 60 on normal-key footage (low-key keeps ~90 % of its own level); footage-aware looks: the
                     look's colour push eases along the shot's own cast and its highlight tone toward neutral where the
                     highlights are near-neutral (_footage_aware_grade); auto exposure on well-exposed footage is
                     capped at +0.6 EV (_exposure_cap); cards that ask for it (LUMA_MATCH_GENRES) keep neighbouring
                     shots at a plain cut inside one part within 15 % mean luma (_match_luma_jumps)
  dark               True: the user asked for a very dark picture ('very dark', 'low key', 'pitch black' in the style
                     words set it too): the limits relax to 15 % crushed / mean 35 (PICTURE_LIMITS_DARK)
  check_cuts         True (default): every chosen window is decoded at the source rate (64 px gray); a camera cut the
                     6 fps analysis missed (frame structure breaks between two stretches that hold together) bans that
                     instant and the slot is re-picked (_cut_check)
  check_flash        True (default): velocity / ramp / stutter shots are counted with the QA's flash metric on their own
                     graded frames at the QA's resolution; a window reaching limit - 1 flashes/s is re-picked (a
                     velocity shot that keeps flickering plays at normal speed) (_flash_check)
  style              a house style (STYLE_PRESETS) by name or plain words (resolve_style): its genre when no genre is
                     given, its ed_fx look (LOOK_PRESETS by name: the look's grade is the shots' grade, its fx join every
                     shot, replacing the genre's own constant vignette / texture / glow / clarity), a transition palette
                     and share, preferred / avoided moves, the caption preset, sfx style and level, pacing (cut_rate);
                     the card rules and colour targets hold
  variant N          another version inside the same rules: shot choice (score noise), cut-grid tie-breaks, transition
                     palette order and places, accent picks (punch / shake / in-out and their character), where the
                     speed-ramp rotation starts (within one plan adjacent ramps never share a curve: RAMP_PATTERNS =
                     brake beat, slow depth, fast-in, braking / speed-up frames, exit; meta.choices.ramps), grade
                     nuance, the next look of the style's rotation
                     (look_pick: main + 1-2 alternates, version v takes look v mod n; speech styles: natural on 0, a
                     subtle look <= 0.4 later; meta.choices.look_pick) and the caption sibling on odd versions; 0 = as
                     written (versions of a plain genre plan vary the same way)
  avoid [EDLs]       earlier versions (dicts or paths): their meta.choices are steered away from (the next unused
                     variant, other shots per slot, unused transitions first)

plan_genre() pipeline (music genres; motivation = music edit + voice-over)
 1. music   — ed_audio.analyze + per-beat kick / snare / onset / fill strengths; the window is a whole number of bars,
              scored by where the drop lands vs the genre structure, energy arc, phrase start/end, loop closure (viral);
              parts hook/build/drop/outro snap to bars, the drop part starts on drops[0] (or the most energetic section).
              music_in / drop_at give a fixed window instead (fixed_window, map_parts_fixed).
 2. footage — one decode pass per clip (cached): shots, per-sample sharpness (whole frame and per vertical strip:
              what the 9:16 crop shows), camera-compensated motion, camera motion (pan, jitter), faces, person mask,
              luma/contrast/colour; per-shot action peaks; duplicates; ranks. Window features classify the subject
              the crop shows: face | person | scene | texture (blur, dark blob, surface) + readability.
 3. slots   — per-part cut grid from the card rhythm (shot lengths in beats at the cards' 120-BPM reference) by a DP
              over the half-beat grid that penalises cuts off downbeats / weak onsets; genre recipes add the hero
              shot on the drop, black pauses, stutter, 1/8 burst, crash clip, ramp-to-freeze, ladder lengths;
              n_shots (slots_n) and cut_rate (apply_cut_rate) override the count.
 4. assign  — candidate source windows scored by the genre's "Shot selection" profile, greedy by slot importance (drop
              first) with no-overlap / repeat (one use per shot while the footage allows) / adjacency / duplicate /
              scale-variety rules; hero slots need a readable subject, establishing slots a real scene; ramps need
              real motion and a peak at the braking beat (a static ramp shot plays at normal speed); action peaks are
              aligned to accents; 1/8 bursts alternate two angles in real time; 9:16 crop paths from ed_reframe,
              shifted so no face is cut by the frame edge. Windows that dip dark are checked on real frames under the
              genre grade and re-picked when they would render near-black. A cut must read: a window that looks like
              its neighbour at the cut (Footage.similarity: structure inside the crop band and brightness) or sits in
              the footage's busiest motion at its edges loses score. Slots the footage cannot serve -> meta.gaps.
 5. moves   — a genre program places moves from parts / signature / allowed with the cards' limits and parameters,
              emitting segment fx, transition_in, ops, layers and audio.sfx; forbidden moves are never placed;
              then required moves, calm transition edges (a hard transition is the hit: no camera accent moves the
              picture in the two frames just outside its window), the density cap (one camera accent per beat, two
              accent kinds per shot, image accents one per bar) and the sound pass (sfx_level, levels per genre).
 6. qa      — thresholds from the genre card (flash_limit_hz = the cards' photosensitivity limit, qa_flash_hz: 3 per
              second, drama / calm 1 — not the trans.flash budget FLASH_LIMIT_HZ);  7. meta — reasoning per slot
              (labelled preview, point edits).
plan_speech() — clips / ugc / explainer, cut by words: transcript (ed_voice.transcribe, model 'omni' for languages
  Whisper lacks, or words=) -> excerpt (src range | from/to phrases | the sentence-aligned window nearest the target
  length that does not start mid-thought) -> jump cuts at pauses / fillers / repeats on word boundaries
  (ed_voice.speech_segments; the pause before the payoff keeps 0.3-0.4 s) -> shots split at source camera cuts,
  speaker turns and phrase boundaries (<= max_shot_s; a source camera cut lands on the first output frame of the new
  shot), framing alternating medium <-> close inside one camera shot -> crops kept off static overlays
  (ed_video.static_overlays -> speaker_crop avoid, then _clear_overlays as a safety net) ->
  crops from ed_reframe.speaker_crop (content box, overlays kept out) -> B-roll inserts over the running voice ->
  punches on phrase starts, a crash zoom on the payoff -> karaoke / subtitle layers from the remapped words
  (ed_voice.subtitle_chunks with the ed_text caption preset and the jump cuts as breaks; the speaker's face track as
  the layers' `faces`, so a chunk moves off the face; talk crops keep the chin above 58 % of the height when the
  picture box and the overlays allow - _caption_headroom) -> music
  bed ducked under the voice -> qa for the speech checks (words, on_word_share, first word, pauses, reading speed,
  source_cuts = the source's own camera cuts).
STYLE_PRESETS {name: {look {name | None, intensity, alt [{name, intensity}]}, description, genre, looks, transitions,
  moves {prefer, avoid}, grade, caption_style, sfx_style, sfx_level, pacing {cut_rate, transitions}, keywords}} (18 house
  styles over the 15 genres); resolve_style(text, genre=None) -> {name, score, genre, why}; style_context / style_grade
  (variant nuance); look_rotation(preset) / look_pick(style context) / style_look: the look of a version.
plan_storyboard(track, genre=None, style=None, dur=None, brief=None, canvas, fps, n_shots=None, character=None) — the
  whole video to generate: the genre plan over stand-in shots, every slot a slate image (animatic) and a gap with an
  edit-gen brief (shot_size, subject, action, camera, duration {slot_s, source_s, handles_s, generate_s}, continuity,
  look, speed, aspect, fps, prompt); meta.storyboard keeps the slot timing / speed mapping / zooms / grade.
fill_gaps(edl, {slot: path | {path, t}}) — plugs clips in: best window for the slot's role and speed mapping (or t), a
  short clip slowed to fit (gap 'stretched'), crop following the subject with the planned zooms, grade + exposure +
  colour fit, punch / crash centres on the subject; version + 1.
apply_command(edl, cmd) — structured point edit (add / replace / remove a move at a time or clip, transition between
clips, any move of a family, swap a clip); Claude turns the user's words into the command dict. Works on composites
(ed_sequence: meta.parts is a list; "part" = a part id, "id.section" or a section of the edit part at the time) and on
timelines with no or an unknown genre (no card rules; the edit part's genre rules inside a composite).

Emitted EDL (TIMELINE.md) — what the consumers read:
  sources[name].box       picture box inside letterbox bars (detected); crop cx/cy are fractions of the box
  segments[].crop         cx, cy, z, path [[k, cx, cy, z]] (ed_reframe subject path; zoom.slow / zoom.out baked into z;
                          shake / dutch cover multiplied in), rot (angle.dutch), center (subject in output fractions,
                          for punch / crash centres), subject
  segments[].speed | speed_curve [[k, rate]] + times [per-frame source s]   (velocity, ramps, freeze, stutter: times
                          are exact; speed_curve given where monotonic)
  segments[].fx           event fx carry `times` (absolute output s; peak frame floor(t·fps+0.4)) — zoom.punch,
                          shake.beat, zoom.in_out, rgb_split, glitch_blocks; zoom.crash `at` = landing; letterbox
                          `t` = animation window; constant fx (vignette, film_overlay, bloom, glow) have no times;
                          every entry has `move` (card id) for point edits
  segments[].transition_in  flash / dissolve / fade / dip / whip / zoom with ed_fx param names (dip: *_frames)
  ops                     black ramps (fades, pauses), flash (hook frame 0)
  layers                  title_card / beat_text / kinetic only when the user gives text (title / word / outro_text);
                          speech genres: karaoke / subtitle chunks (ed_voice.subtitle_chunks); kinds are validated
                          against ed_text's registry (layer_kinds)
  audio                   music {path, in, gain_db, fade_out} (optional for speech genres), voice [{path, at, in, dur}]
                          (speech: one per kept range, running under B-roll inserts), duck [{under: voice, ...}],
                          sfx [kind, variant, at, align, level light|normal|strong (the only loudness: ed_sfx presets),
                          dur, params, move, why], grid {bpm, beats, downbeats} in output time, loudness
  qa                      card thresholds + planned_black / white / freeze + cut grid + color ranges (COLOR_TARGETS) +
                          genre_checks;
                          speech: kind 'speech', words (output time), on_word_share, first_word_max, max_pause,
                          allowed_pauses, max_cps, source_cuts, speech (planner-side speech_qa summary)
  meta                    track window and reason, parts, beat grid, per-slot reasoning (score, ranks, tags, alternatives,
                          moves with why), skipped moves with reasons, footage index, options, window_mode
                          (fixed | chosen), gaps [{slot, part, role, kind missing|stretched|reused|weak|storyboard,
                          reason, fill, t, f, dur, need_s, brief}] (a brief per gap for edit-gen), history of point
                          edits; style, variant, choices (what this version picked: transitions, looks, grade, nuance,
                          caption_style, sfx_style, shots per slot), grade_fit {seg: {after (the QA's numbers: luma
                          levels, clip_lo / clip_hi in %, sat 0-1), changed}}, storyboard;
                          speech: kind 'speech', source {path, range, why, keep, removed, camera_cuts, transcript}
"""
import os, sys, re, json, math, copy, hashlib, argparse, time, inspect
import numpy as np
import yaml
import cv2
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ed_audio as A          # noqa: E402
import ed_video as V          # noqa: E402
import ed_reframe as RF       # noqa: E402
from legacy_plan import plan_remake, map_timeline, candidate_windows  # noqa: E402,F401  (edit.py uses plan_remake)

GENRES_DIR = os.path.join(ROOT, 'genres')
MOVES_DIR = os.path.join(ROOT, 'moves')
PLANNER = 'ed_plan.genre/1'
PARTS = ('hook', 'build', 'drop', 'outro')
REF_BEAT = 0.5                 # genre cards give seconds for 120 BPM (beat = 0.5 s)
MUSIC_VERSION = 2
FOOTAGE_VERSION = 8                # 8: per-strip sharpness / contrast (what the 9:16 crop actually shows)
SIZE_RANK = {'extreme-close': 4, 'close': 3, 'detail': 3, 'medium': 2, 'wide': 1, 'wide/no-face': 0}
TRANSITION_KINDS = {'dissolve', 'dip', 'flash', 'fade', 'whip', 'zoom', 'spin', 'wipe', 'luma', 'lens', 'glitch',
                    'pixel_sort', 'light_leak', 'liquid', 'push', 'slide'}
OP_KINDS = {'invert', 'white', 'black', 'mask_flash', 'rect_flash', 'hud_tc', 'flash'}
SFX_KINDS = {'whoosh', 'riser', 'impact', 'sub_drop', 'glitch', 'click', 'swell', 'reverse_whoosh', 'scratch', 'tape_stop'}
LAYER_KINDS = {'static', 'kinetic', 'beat_text', 'subtitle', 'karaoke', 'title_card', 'lower_third', 'callout', 'counter',
               'intertitle', 'margin_note', 'repeat', 'route_map', 'behind_subject'}     # fallback when ed_text is absent
CAMERA_FX = {'zoom.punch', 'shake.beat', 'zoom.crash', 'zoom.in_out', 'roll', 'drift'}
_LAYER_REG = []


def layer_kinds():
    """(kinds, kind_of): the layer registry of ed_text (LAYER_KINDS + its aliases / 'type.' card ids) when importable,
    else the static set above."""
    if not _LAYER_REG:
        try:
            import ed_text as _T
            reg = getattr(_T, 'LAYER_KINDS', None)
            kof = getattr(_T, 'kind_of', None)
            if isinstance(reg, dict) and reg and callable(kof):
                _LAYER_REG.append((set(reg), kof))
        except Exception:                 # ed_text missing or broken: the static set still validates
            pass
        if not _LAYER_REG:
            def kof(L):
                k = str(L.get('kind') or L.get('type') or 'static').strip()
                return k.split('.', 1)[1] if k.startswith(('type.', 'gfx.')) else k
            _LAYER_REG.append((set(LAYER_KINDS), kof))
    return _LAYER_REG[0]

# ---- library vocabulary (machine values of the move / genre cards); genre slug -> display name
GENRE_NAMES = {'viral': 'viral', 'epic': 'epic', 'drama': 'dramatic', 'calm': 'calm', 'product': 'product',
               'phonk': 'phonk', 'sport': 'sport', 'travel': 'travel', 'fashion': 'fashion', 'fanedit': 'fan edit',
               'teaser': 'teaser', 'clips': 'clips', 'explainer': 'explainer', 'ugc': 'UGC', 'motivation': 'motivation'}
GENRE_ALIASES = {'velocity': 'phonk', 'fan-edit': 'fanedit', 'fan_edit': 'fanedit', 'fan edit': 'fanedit',
                 'dramatic': 'drama'}
KINDS = ('music', 'speech')
SECTIONS = ('Goal and platform', 'Structure by seconds', 'Rhythm', 'Shot selection', 'Moves by part', 'SFX', 'Color',
            'Text', 'Quality checks')
NOT_IN_PART = 'not in part'      # move_allowed() reason prefix: allowed in the genre, only not listed for this part


# ============================================================================ small helpers
def frame_at(t, fps):
    """Frame that shows a musical event at t (cards: k0 = floor(t*fps + 0.4), early bias ≤ 0.6 frame)."""
    return int(math.floor(t * fps + 0.4))


def _band(x, lo, hi, soft):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return 0.0
    if x < lo:
        return max(0.0, 1.0 - (lo - x) / max(soft, 1e-9))
    if x > hi:
        return max(0.0, 1.0 - (x - hi) / max(soft, 1e-9))
    return 1.0


def _rank(sorted_vals, v):
    if sorted_vals is None or len(sorted_vals) == 0 or v is None or (isinstance(v, float) and math.isnan(v)):
        return 0.5
    return float(np.searchsorted(sorted_vals, v, side='right')) / len(sorted_vals)


def _file_key(path, extra=''):
    st = os.stat(path)
    return hashlib.md5(f'{os.path.abspath(path)}|{st.st_size}|{int(st.st_mtime)}|{extra}'.encode()).hexdigest()[:16]


def tcode(t):
    m, s = divmod(max(0.0, t), 60)
    return f'{int(m)}:{s:05.2f}'


def parse_time(v):
    """7 | 7.5 | '0:07' | '0:07.5' | '7s' -> seconds."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().lower().replace(',', '.').rstrip('s')
    if ':' in s:
        parts = [float(x) for x in s.split(':')]
        t = 0.0
        for p in parts:
            t = t * 60 + p
        return t
    return float(s)


def _ease(p, kind='linear'):
    p = min(max(p, 0.0), 1.0)
    if kind in ('in', 'inQuad'):
        return p * p
    if kind in ('out', 'outQuad'):
        return 1 - (1 - p) ** 2
    if kind == 'outCubic':
        return 1 - (1 - p) ** 3
    if kind == 'inCubic':
        return p ** 3
    if kind in ('inout', 'inOutCubic'):
        return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2
    if kind == 'inOutQuint':
        return 16 * p ** 5 if p < 0.5 else 1 - (-2 * p + 2) ** 5 / 2
    return p


def _exp_curve(tau_s, fps, peak_frames=1, cutoff=0.05):
    """Per-frame opacities of a flash: peak frames at 1.0, then exp(-t/tau) until < cutoff (trans.flash params.decay)."""
    out = [1.0] * peak_frames
    k = 1
    while tau_s > 0:
        a = math.exp(-k / fps / tau_s)
        if a < cutoff:
            break
        out.append(round(a, 3))
        k += 1
    return out


def _dump_atomic(obj, path, indent=None):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=indent, ensure_ascii=False)
    os.replace(tmp, path)


def _load_json(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _clean_name(p, taken):
    base = re.sub(r'[^A-Za-z0-9_]+', '_', os.path.splitext(os.path.basename(p))[0]).strip('_')[:40] or 'clip'
    name, k = base, 2
    while name in taken:
        name, k = f'{base}_{k}', k + 1
    taken.add(name)
    return name


# ============================================================================ options (plan_genre **opts)
SFX_LEVELS = ('none', 'light', 'genre', 'heavy')
SFX_LEVEL_ALIAS = {'normal': 'genre', 'medium': 'genre', 'default': 'genre', 'strong': 'heavy', 'max': 'heavy', 'off': 'none'}
HYPE_GENRES = {'phonk', 'epic', 'sport', 'viral', 'motivation', 'teaser', 'fanedit'}   # audible hits / whooshes
QUIET_GENRES = {'calm', 'drama', 'explainer'}                                          # restrained sound design
ORDERS = ('auto', 'given')
# Whisper's 99 language codes (openai-whisper tokenizer, MIT); other languages are recognised by ed_voice model='omni'
WHISPER_LANGS = set('en zh de es ru ko fr ja pt tr pl ca nl ar sv it id hi fi vi he uk el ms cs ro da hu ta no th ur hr '
                    'bg lt la mi ml cy sk te fa lv bn sr az sl kn et mk br eu is hy ne mn bs kk sq sw gl mr pa si km sn '
                    'yo so af oc ka be tg sd gu am yi lo uz fo ht ps tk nn mt sa lb my bo tl mg as tt haw ln ha ba jw su '
                    'yue'.split())


def _move_list(v):
    """Move ids / families from a list or a comma-separated string ('time.speed_ramp, glitch')."""
    if not v:
        return []
    if isinstance(v, str):
        v = v.split(',')
    out = []
    for x in v:
        x = str(x).strip()
        if x and x not in out:
            out.append(x)
    return out


def norm_opts(opts, g=None):
    """Validated plan options (aliases, types, defaults). Raises ValueError on contradictions.
      n_shots   exact number of shots (int)            order   'auto' | 'given' (footage order = shot order)
      require_moves / forbid_moves   move ids or families ('glitch')     sfx_level  none | light | genre | heavy
      music_in (alias start)  track second shown at output 0          drop_at  output second of the strongest drop
      drop_t    track second of the drop (overrides the detector)     bpm      tempo hint for the beat tracker
      cut_rate  multiplier of the card's cutting rate (2 = twice as many cuts)   bars  length in whole bars"""
    o = dict(opts or {})
    n = o.get('n_shots')
    o['n_shots'] = int(n) if n not in (None, '') else None
    if o['n_shots'] is not None and o['n_shots'] < 1:
        raise ValueError('n_shots must be >= 1')
    order = str(o.get('order') or 'auto').strip().lower()
    if order not in ORDERS:
        raise ValueError(f'order must be one of {ORDERS}, not {order!r}')
    o['order'] = order
    o['require'] = _move_list(o.get('require_moves') or o.get('require'))
    o['forbid'] = _move_list(o.get('forbid_moves') or o.get('forbid'))
    both = [m for m in o['require'] if m in o['forbid']]
    if both:
        raise ValueError(f'moves both required and forbidden: {both}')
    mi = o.get('music_in', o.get('start'))
    o['music_in'] = parse_time(mi) if mi not in (None, '') else None
    o['drop_at'] = parse_time(o['drop_at']) if o.get('drop_at') not in (None, '') else None
    o['drop_t'] = parse_time(o['drop_t']) if o.get('drop_t') not in (None, '') else None
    if o['music_in'] is not None and o['music_in'] < 0:
        raise ValueError('music_in must be >= 0')
    if o['drop_at'] is not None and o['drop_at'] < 0:
        raise ValueError('drop_at must be >= 0')
    lvl = str(o.get('sfx_level') or 'genre').strip().lower()
    lvl = SFX_LEVEL_ALIAS.get(lvl, lvl)
    if lvl not in SFX_LEVELS:
        raise ValueError(f'sfx_level must be one of {SFX_LEVELS}, not {lvl!r}')
    o['sfx_level'] = lvl
    it = o.get('interp')
    o['interp'] = bool(it) and str(it).strip().lower() not in ('0', 'false', 'no', 'none', 'off')
    cr = float(o.get('cut_rate') or 1.0)
    o['cut_rate'] = min(4.0, max(0.25, cr))
    o['bpm'] = float(o['bpm']) if o.get('bpm') else None
    o['bars'] = int(o['bars']) if o.get('bars') else None
    seq = o.get('in_sequence')
    seq = 'middle' if seq is True else (None if not seq else str(seq).strip().lower())
    if seq not in (None, 'first', 'middle', 'last', 'only'):
        raise ValueError("in_sequence must be 'first' | 'middle' | 'last' | 'only' (or true / false)")
    o['in_sequence'] = None if seq == 'only' else seq
    return o


def genre_view(g, require=(), forbid=()):
    """Copy of a loaded genre with the user's required moves allowed everywhere (also over the cards' own bans:
    the user asked) and the forbidden moves / families removed from every list."""
    if not require and not forbid:
        return g
    g2 = copy.deepcopy({k: v for k, v in g.items() if k != 'body'})
    g2['body'] = g.get('body', {})
    every = set(g['allowed']) | set(g['forbidden']) | set(g['signature']) | {m for v in (g.get('sfx') or {}).values()
                                                                            for m in (v or [])}
    for p in PARTS:
        every |= set(g['part_moves'].get(p, []))
    fam = lambda m, x: m == x or ('.' not in x and m.split('.')[0] == x)   # noqa: E731
    banned = set()
    for x in forbid:
        banned |= {m for m in every if fam(m, x)}
        if '.' in x:
            banned.add(x)
    req = []
    for x in require:
        if '.' in x:
            req.append(x)
        else:                                  # a family: its moves this genre already knows, else nothing to force
            req += sorted(m for m in every if fam(m, x) and m not in banned)
    strip = lambda lst: [m for m in lst if m not in banned]   # noqa: E731
    g2['forbidden'] = sorted((set(g['forbidden']) | banned) - set(req))
    g2['allowed'] = sorted((set(strip(g['allowed'])) | set(req)) - set(m for m in req if m.startswith('sfx.')))
    g2['signature'] = strip(g['signature']) + [m for m in req if m not in g['signature'] and not m.startswith('sfx.')]
    g2['allowed_extra'] = strip(g['allowed_extra']) + [m for m in req if not m.startswith('sfx.')]
    g2['part_moves'] = {p: strip(g['part_moves'].get(p, [])) for p in PARTS}
    for p in ('build', 'drop'):                    # the programs place what the part lists name
        g2['part_moves'][p] += [m for m in req if not m.startswith('sfx.') and m not in g2['part_moves'][p]]
    sf = {p: strip(list((g.get('sfx') or {}).get(p) or [])) for p in PARTS}
    for m in req:
        if m.startswith('sfx.'):
            for p in PARTS:
                if m not in sf[p]:
                    sf[p].append(m)
    g2['sfx'] = sf
    g2['required'] = req
    g2['user_forbidden'] = sorted(banned)
    return g2


# ============================================================================ genre + move library
_GENRES, _CARDS = {}, {}


def _front_matter(path):
    with open(path, encoding='utf-8') as fh:
        txt = fh.read()
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', txt, re.S)
    if not m:
        raise ValueError(f'{path}: no YAML front matter')
    return yaml.safe_load(m.group(1)), m.group(2)


def genre_key(name):
    """Genre key of a card value (move card `genres:` key, genre card `genre:`): the slug, lowercased; unknown names
    (a user's own genre) are kept."""
    s = str(name).strip().lower()
    return GENRE_ALIASES.get(s, s)


def position(v):
    """Move position in a genre: signature | allowed | forbidden; None stays None."""
    return None if v is None else str(v).strip().lower()


def genre_kind(v):
    """Genre card `kind`: music | speech (anything else counts as music)."""
    k = str(v or '').strip().lower()
    return k if k in KINDS else 'music'


def genre_index():
    out = {}
    for fn in sorted(os.listdir(GENRES_DIR)):
        if fn.endswith('.md') and not fn.startswith('_'):
            fm, _ = _front_matter(os.path.join(GENRES_DIR, fn))
            out[fm['slug']] = fm['genre']
    return out


def resolve_genre(name):
    idx = genre_index()
    n = str(name).strip().lower()
    if n in idx:
        return n
    for slug, gname in idx.items():
        if n == str(gname).lower():
            return slug
    alias = GENRE_ALIASES.get(n)
    if alias in idx:
        return alias
    raise KeyError(f'unknown genre {name!r}; known: {sorted(idx)}')


def load_genre(name):
    slug = resolve_genre(name)
    if slug in _GENRES:
        return _GENRES[slug]
    fm, body = _front_matter(os.path.join(GENRES_DIR, slug + '.md'))
    sections = {}
    for chunk in re.split(r'\n(?=## )', '\n' + body):
        chunk = chunk.strip('\n')
        if chunk.startswith('## '):
            title, _, text = chunk[3:].partition('\n')
            sections[title.strip()] = text.strip()
    typical = float(fm['format']['typical_s'])
    parts = []
    for s in fm['structure']:
        m = re.search(r'\(\s*([\d.,]+)\s*[–-]\s*([\d.,]+)\s*%', str(s['t']))
        if m:
            a, b = float(m.group(1).replace(',', '.')) / 100, float(m.group(2).replace(',', '.')) / 100
        else:
            m2 = re.search(r'([\d.,]+)\s*[–-]\s*([\d.,]+)', str(s['t']))
            a, b = float(m2.group(1).replace(',', '.')) / typical, float(m2.group(2).replace(',', '.')) / typical
        parts.append(dict(part=s['part'], f0=a, f1=b, goal=s.get('goal', '')))
    mv = fm.get('moves') or {}
    part_moves = {p: list(mv.get(p) or []) for p in PARTS}
    forb = set(mv.get('forbidden') or [])
    allowed = set(mv.get('signature') or []) | set(mv.get('allowed') or [])
    for p in PARTS:
        allowed |= set(part_moves[p])
    g = dict(fm)
    g.update(slug=slug, parts=parts, body=sections, part_moves=part_moves, signature=list(mv.get('signature') or []),
             allowed_extra=list(mv.get('allowed') or []), forbidden=sorted(forb), allowed=sorted(allowed - forb),
             kind=genre_kind(fm.get('kind')),
             genre_name=GENRE_NAMES.get(slug) or GENRE_NAMES.get(genre_key(fm.get('genre', slug)))
             or str(fm.get('genre', slug)))
    _GENRES[slug] = g
    return g


_CARD_POS = {}


def card_positions(mid):
    """{genre key: signature | allowed | forbidden} of a move card (keys = slugs), {} when there is no card."""
    if mid not in _CARD_POS:
        c = move_card(mid) or {}
        _CARD_POS[mid] = {genre_key(k): position(v) for k, v in (c.get('genres') or {}).items()}
    return _CARD_POS[mid]


def move_card(mid):
    """Card by id: moves/<id>.yaml (library tree) or the family bundle moves/<family>.yaml (packaged skill:
    one multi-document YAML per family)."""
    if mid not in _CARDS:
        p = os.path.join(MOVES_DIR, mid + '.yaml')
        if os.path.exists(p):
            with open(p, encoding='utf-8') as fh:
                _CARDS[mid] = yaml.safe_load(fh)
        else:
            _CARDS[mid] = None
            b = os.path.join(MOVES_DIR, mid.split('.')[0] + '.yaml')
            if os.path.exists(b):
                with open(b, encoding='utf-8') as fh:
                    bundle = list(yaml.safe_load_all(fh))
                for c in bundle:
                    if isinstance(c, dict) and c.get('id'):
                        _CARDS.setdefault(c['id'], c)
                        if c['id'] == mid:
                            _CARDS[mid] = c
    return _CARDS[mid]


def move_allowed(g, mid, part=None):
    """(ok, reason): genre card lists (parts / signature / allowed / forbidden, sfx per part) + the move card's own
    position for the genre ('forbidden' wins) + existence of the card; the user's require / forbid lists
    (genre_view) win over both."""
    if mid in g.get('user_forbidden', ()):
        return False, 'forbidden by the user'
    if mid in g.get('required', ()):
        return (move_card(mid) is not None), ('required by the user' if move_card(mid) is not None else 'no move card')
    if mid in g['forbidden']:
        return False, 'forbidden by the genre card'
    c = move_card(mid)
    if c is None:
        return False, 'no move card'
    cp = card_positions(mid)
    pos = cp.get(g['slug']) or cp.get(genre_key(g.get('genre', g['slug'])))
    if pos == 'forbidden':
        return False, 'the move card forbids this genre'
    if mid.startswith('sfx.'):
        sf = g.get('sfx') or {}
        lst = (sf.get(part) or []) if part else [x for v in sf.values() for x in (v or [])]
        return (mid in lst), ('genre sound' if mid in lst else f'not in the genre sfx for {part or "the video"}')
    if mid not in g['allowed']:
        return False, 'not in the genre parts / allowed'
    if part and mid not in g['part_moves'].get(part, []) and mid not in g['allowed_extra']:
        return False, f'{NOT_IN_PART} {part} (nor in allowed)'
    return True, pos or 'in the genre lists'


def moves_of_family(g, family, part=None):
    out = []
    for mid in g['allowed']:
        if mid.split('.')[0] == family and move_allowed(g, mid, part)[0]:
            out.append(mid)
    return out


# ============================================================================ 1. music
def analyze_music(track, cache_dir=None, bpm_hint=None):
    """ed_audio.analyze + per-beat strengths of kick (30–150 Hz flux), snare (1.5–6 kHz flux), onset, 16th fills,
    beat energy, bar chroma (loop closure). Cached by file key."""
    track = os.path.abspath(track)
    cp = None
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
        cp = os.path.join(cache_dir, f'music_{_file_key(track, f"m{MUSIC_VERSION}|{bpm_hint}")}.json')
        hit = _load_json(cp) if os.path.exists(cp) else None
        if hit:
            return hit
    res = A.analyze(track, bpm_hint)
    y = A.load_audio(track)
    f = A.features(y)
    fa = A.FPS_A

    def nrm(v):
        v = np.asarray(v, np.float64)
        pos = v[v > 0]
        return v / (np.percentile(pos, 99) + 1e-9 if len(pos) else 1.0)
    low = gaussian_filter1d(nrm(f['low_flux']), 1.0)
    mid = gaussian_filter1d(nrm(f['mid_flux']), 1.0)
    on = gaussian_filter1d(nrm(f['onset']), 1.0)
    rms_db = 20 * np.log10(gaussian_filter1d(f['rms'], 2) + 1e-6)

    def pk(arr, t, w=0.04):
        i0, i1 = max(0, int((t - w) * fa)), min(len(arr), int((t + w) * fa) + 1)
        return float(arr[i0:i1].max()) if i1 > i0 else 0.0
    beats = res['beats']
    per = 60.0 / res['bpm']
    res['beat_kick'] = [round(min(pk(low, b), 2.0), 3) for b in beats]
    res['beat_snare'] = [round(min(pk(mid, b), 2.0), 3) for b in beats]
    res['beat_onset'] = [round(min(pk(on, b), 2.0), 3) for b in beats]
    res['half_onset'] = [round(min(pk(on, b + per / 2), 2.0), 3) for b in beats]
    res['beat_fill'] = [round(min(max(pk(on, b + per / 4, 0.02), pk(on, b + 3 * per / 4, 0.02)), 2.0), 3) for b in beats]
    res['beat_db'] = [round(float(rms_db[max(0, int(b * fa)):max(1, int((b + per) * fa))].mean()), 2) for b in beats]
    res['bar_chroma'] = []
    for bt in res['bars']:
        i0, i1 = int(bt['t0'] * fa), max(int(bt['t0'] * fa) + 1, int(bt['t1'] * fa))
        res['bar_chroma'].append([round(float(x), 4) for x in f['chroma'][i0:i1].mean(0)])
    res['track'] = track
    res['planner_music_version'] = MUSIC_VERSION
    if cp:
        _dump_atomic(res, cp)
    return res


class Grid:
    """Beat grid of the whole track, extended by the period before the first / after the last tracked beat (trackers
    often miss the very first hit), with per-beat strengths aligned to the extended indices."""

    def __init__(self, mus):
        b = np.asarray(mus['beats'], float)
        p = float(np.median(np.diff(b))) if len(b) > 2 else 60.0 / mus['bpm']
        pre, t = [], b[0] - p
        while t > -0.045:
            pre.insert(0, max(0.0, t))
            t -= p
        post, t = [], b[-1] + p
        while t < mus['duration'] + 8 * p:
            post.append(t)
            t += p
        self.t = np.concatenate([pre, b, post])
        self.n0, self.nb = len(pre), len(b)
        self.period = p
        self.duration = float(mus['duration'])
        d0 = mus['downbeats'][0] if mus.get('downbeats') else b[0]
        self.phase = int(np.argmin(np.abs(self.t - d0))) % 4

        def ext(key, fill=0.0):
            v = mus.get(key) or [fill] * len(b)
            return np.concatenate([[fill] * len(pre), np.asarray(v, float), [fill] * len(post)])
        self.kick, self.snare, self.onset = ext('beat_kick'), ext('beat_snare'), ext('beat_onset')
        self.half, self.fill = ext('half_onset'), ext('beat_fill')
        env = mus.get('envelope') or {}
        self._env_db = np.asarray(env.get('rms_db') or [], float)
        self._env_dt = (env.get('step', 2) / env.get('fps', A.FPS_A)) if env else 0.0232

    def is_down(self, j):
        return (j - self.phase) % 4 == 0

    def time(self, j):
        """time of fractional beat index j (linear between beats, extrapolated past the ends)"""
        j0 = int(math.floor(j))
        if j0 < 0:
            return float(self.t[0] + j * self.period)
        if j0 >= len(self.t) - 1:
            return float(self.t[-1] + (j - len(self.t) + 1) * self.period)
        return float(self.t[j0] + (j - j0) * (self.t[j0 + 1] - self.t[j0]))

    def energy_db(self, t0, t1):
        if not len(self._env_db):
            return -30.0
        i0, i1 = int(max(0, t0) / self._env_dt), int(max(0, t1) / self._env_dt)
        i1 = max(i1, i0 + 1)
        seg = self._env_db[i0:i1]
        return float(seg.mean()) if len(seg) else -60.0


def choose_window(mus, grid, g, dur=None):
    """Whole bars of the track. Score: where the drop anchor lands relative to the genre's drop part, energy arc
    (drop louder than build), phrase-aligned start/end, loop closure for 'viral', small preference for early starts."""
    p = grid.period
    bar = 4 * p
    lo_s, hi_s = g['format']['duration_s']
    want = float(dur) if dur else float(g['format']['typical_s'])
    if not dur:
        want = min(max(want, lo_s), hi_s)
    n_bars = max(2, int(round(want / bar)))
    drop_part = next((x for x in g['parts'] if x['part'] == 'drop'), None)
    p_drop = drop_part['f0'] if drop_part else 0.4
    short_rule = g['slug'] == 'phonk' and n_bars * bar <= 12.5
    if short_rule:
        p_drop = 1.0 / n_bars                       # phonk card: a video ≤ 12 s starts one bar before the drop
    build_part = next((x for x in g['parts'] if x['part'] == 'build'), None)
    anchor, kind = None, None
    if mus.get('drops'):
        anchor, kind = float(mus['drops'][0]['t']), 'drop'
    elif mus.get('sections'):
        secs = [s for s in mus['sections'] if s['t0'] > bar]
        if secs:
            s = max(secs, key=lambda s: s.get('energy', 0))
            anchor, kind = float(s['t0']), 'reveal'
    sec_bounds = sorted({round(float(s['t0']), 3) for s in mus.get('sections', [])} |
                        {round(float(s['t1']), 3) for s in mus.get('sections', [])})
    downs = [j for j in range(len(grid.t)) if grid.is_down(j)]
    j_anchor = int(np.argmin(np.abs(grid.t - anchor))) if anchor is not None else None
    chroma = mus.get('bar_chroma') or []
    bar_t0 = [b['t0'] for b in mus.get('bars', [])]

    def bar_vec(t):
        if not bar_t0:
            return None
        i = int(np.argmin(np.abs(np.asarray(bar_t0) - t)))
        return np.asarray(chroma[i]) if i < len(chroma) and abs(bar_t0[i] - t) < p else None
    for nb in range(n_bars, 1, -1):
        cands = []
        for di, j in enumerate(downs):
            t0, t1 = grid.time(j), grid.time(j + 4 * nb)
            if t0 < -0.05 or t1 > grid.duration + 0.08:
                continue
            T = t1 - t0
            sc, why = 0.0, []
            if anchor is not None:
                rel = (anchor - t0) / T
                inside = t0 + 0.9 * bar <= anchor <= t1 - 0.9 * bar
                sc += -6.0 * abs(rel - p_drop) - (0.0 if inside else 4.0)
                why.append(f'{kind} at {rel:.0%} (target {p_drop:.0%})')
                if inside and j_anchor is not None:
                    if (j_anchor - j) % 16 == 0:
                        sc += 0.4
                    if (j + 4 * nb - j_anchor) % 16 == 0 or (j + 4 * nb - j_anchor) % 8 == 0:
                        sc += 0.25
            if build_part and drop_part and not short_rule:
                e_b = grid.energy_db(t0 + build_part['f0'] * T, t0 + build_part['f1'] * T)
                e_d = grid.energy_db(t0 + drop_part['f0'] * T, t0 + drop_part['f1'] * T)
                sc += float(np.clip(0.15 * (e_d - e_b), -1.5, 1.5))
            if any(abs(t0 - b) < 0.08 for b in sec_bounds):
                sc += 0.5
                why.append('starts on a section')
            if any(abs(t1 - b) < 0.08 for b in sec_bounds) or t1 >= grid.duration - 0.08:
                sc += 0.5
                why.append('ends on a section / track end')
            if g['slug'] == 'viral':
                va, vb = bar_vec(t0), bar_vec(t1)
                if va is not None and vb is not None:
                    sim = float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-9))
                    sc += 1.2 * sim
                    why.append(f'loop similarity {sim:.2f}')
            sc -= 0.01 * di
            cands.append(dict(j0=j, j1=j + 4 * nb, t_in=round(t0, 4), t_out=round(t1, 4), n_bars=nb, score=round(sc, 3),
                              why='; '.join(why)))
        if cands:
            cands.sort(key=lambda c: -c['score'])
            best = dict(cands[0])
            best.update(bar=bar, anchor=anchor, anchor_kind=kind, requested_bars=n_bars,
                        top=[{k: c[k] for k in ('t_in', 't_out', 'score')} for c in cands[:4]])
            if nb < n_bars:
                best['why'] += f'; track too short for {n_bars} bars'
            return best
    raise ValueError('track too short for a 2-bar edit')


def map_parts(win, grid, g):
    """hook/build/drop/outro in bars of the window; the drop part starts on the anchor bar when it is inside."""
    B = win['n_bars']
    fr = {x['part']: x for x in g['parts']}
    cut = [0, round(fr['hook']['f1'] * B), round(fr['build']['f1'] * B), round(fr['drop']['f1'] * B), B]
    if win.get('anchor') is not None:
        ab = int(round((win['anchor'] - win['t_in']) / win['bar']))
        if 1 <= ab <= B - 1:
            cut[2] = ab
    if B >= 3:
        d = min(max(1, cut[2]), B - 2)                 # drop starts on the anchor bar, ≥ 1 bar of hook before it
        h = min(max(1, cut[1]), d)                     # the build may be empty (short videos: hook -> drop)
        o = min(max(cut[3], d + 1), B - 1)             # drop ≥ 1 bar, outro ≥ 1 bar
        cut = [0, h, d, o, B]
    else:
        cut = [0, 1, 1, 2, 2]
    parts = {}
    for i, name in enumerate(PARTS):
        b0, b1 = cut[i], cut[i + 1]
        parts[name] = dict(bar0=b0, bar1=b1, beat0=4 * b0, beat1=4 * b1,
                           t0=max(0.0, round(grid.time(win['j0'] + 4 * b0) - win['t_in'], 4)),
                           t1=max(0.0, round(grid.time(win['j0'] + 4 * b1) - win['t_in'], 4)))
    return parts


def drop_anchor(mus, grid, drop_t=None):
    """(track second, kind) of the strongest drop: the user's drop_t (snapped to a downbeat within half a beat),
    drops[0] from the analysis, else the start of the most energetic section after the first bar; (None, None)."""
    p = grid.period
    if drop_t is not None:
        downs = [grid.t[j] for j in range(len(grid.t)) if grid.is_down(j)]
        near = min(downs, key=lambda x: abs(x - drop_t)) if downs else drop_t
        return (float(near) if abs(near - drop_t) <= p / 2 else float(drop_t)), 'user'
    if mus.get('drops'):
        return float(mus['drops'][0]['t']), 'drop'
    secs = [s for s in mus.get('sections', []) if s['t0'] > 4 * p]
    if secs:
        s = max(secs, key=lambda s: s.get('energy', 0))
        return float(s['t0']), 'reveal'
    return None, None


def fixed_window(mus, grid, g, T=None, music_in=None, drop_at=None, drop_t=None, bars=None):
    """Track window from the user's / sequence's constraints instead of the search in choose_window:
    music_in = track second at output 0; drop_at = output second where the drop (drop_t or the detected one) lands.
    The start snaps to a beat within 60 ms; T = dur, or whole bars, or the card's typical length (track end clips it).
    Returns the choose_window dict + fixed=True, drop_beat (window-relative beat index of the drop or None),
    n_beats (float) and notes."""
    p = grid.period
    notes = []
    anchor, kind = drop_anchor(mus, grid, drop_t)
    if music_in is not None:
        t_in = float(music_in)
        why = f'music_in {t_in:.3f} s (given)'
    elif drop_at is not None:
        if anchor is None:
            anchor, kind = float(grid.t[max(0, grid.n0)]), 'first beat'
            notes.append('no drop found in the track: the first beat is used as the drop')
        t_in = anchor - float(drop_at)
        why = f'{kind} at {anchor:.3f} s placed at output {float(drop_at):.3f} s'
        if t_in < 0:
            notes.append(f'the track has only {anchor:.2f} s before the drop: the output starts at track 0 and the drop '
                         f'lands at {anchor:.2f} s instead of {float(drop_at):.2f} s')
            t_in = 0.0
    else:
        t_in = 0.0
        why = 'track start'
    j_near = int(np.argmin(np.abs(grid.t - t_in)))
    if abs(grid.t[j_near] - t_in) <= 0.06:
        t_in = float(grid.t[j_near])
        j0 = j_near
    else:
        j0 = int(np.searchsorted(grid.t, t_in - 1e-3))
    t_in = max(0.0, t_in)
    if bars:
        T = grid.time(j0 + 4 * int(bars)) - grid.time(j0) if abs(grid.t[min(j0, len(grid.t) - 1)] - t_in) < 1e-3 \
            else 4 * int(bars) * p
    if not T:
        lo_s, hi_s = g['format']['duration_s']
        T = min(max(float(g['format']['typical_s']), lo_s), hi_s)
    t_out = t_in + float(T)
    if t_out > grid.duration + 1e-3:
        notes.append(f'the track ends at {grid.duration:.2f} s: the edit is {grid.duration - t_in:.2f} s instead of {float(T):.2f} s')
        t_out = grid.duration
    if t_out - t_in < 4 * p:
        raise ValueError(f'track window {t_in:.2f}–{t_out:.2f} s is shorter than a bar')
    # window-relative fractional beat position of an output time
    rel_beat = lambda t: float(np.interp(t_in + t, grid.t, np.arange(len(grid.t)))) - j0   # noqa: E731
    nb = rel_beat(t_out - t_in)
    jd = None
    if drop_at is not None and music_in is None:
        jd = int(round(rel_beat(anchor - t_in)))          # = drop_at unless the start was clipped to the track start
    elif drop_at is not None:
        jd = int(round(rel_beat(float(drop_at))))
    elif anchor is not None and t_in + p <= anchor <= t_out - p:
        jd = int(round(rel_beat(anchor - t_in)))
    if jd is not None and not (0 <= jd < nb - 0.5):
        notes.append(f'the drop (beat {jd}) is outside the window: parts follow the card proportions')
        jd = None
    return dict(j0=j0, j1=j0 + int(math.ceil(nb - 1e-6)), t_in=round(t_in, 4), t_out=round(t_out, 4), n_bars=nb / 4,
                bar=4 * p, anchor=anchor, anchor_kind=kind, requested_bars=bars, n_beats=nb, drop_beat=jd, fixed=True,
                why=why + ('; ' + '; '.join(notes) if notes else ''), notes=notes, score=None, top=[])


def map_parts_fixed(win, grid, g):
    """Parts of a fixed window in beats: hook / build before the drop beat, drop / outro after it, in the card's
    proportions, boundaries on downbeats where possible; parts may be empty (a part that starts on the drop)."""
    nb = win['n_beats']
    NB = int(math.ceil(nb - 1e-6))
    fr = {x['part']: x for x in g['parts']}
    jd = win.get('drop_beat')
    if jd is None:
        jd = int(round(fr['drop']['f0'] * nb))
    j0 = win['j0']

    def snap(b, lo, hi):              # nearest downbeat to beat b inside [lo, hi], else b
        b = int(round(min(max(b, lo), hi)))
        cands = [x for x in range(lo, hi + 1) if grid.is_down(j0 + x)]
        return min(cands, key=lambda x: (abs(x - b), x)) if cands else b
    pre, post = jd, NB - jd
    hb = fr['hook']['f1'] / max(fr['drop']['f0'], 1e-6)                 # hook share of the part before the drop
    h = 0 if pre <= 0 else (pre if pre <= 4 else snap(pre * hb, 4, pre))
    dr = (fr['drop']['f1'] - fr['drop']['f0']) / max(1e-6, 1 - fr['drop']['f0'])
    d1 = NB if post < 12 else snap(jd + post * dr, jd + 4, NB - 4)      # outro only when ≥ 3 bars follow the drop
    cut = [0, h, jd, d1, NB]
    parts = {}
    for i, name in enumerate(PARTS):
        b0, b1 = cut[i], cut[i + 1]
        t0 = max(0.0, grid.time(j0 + b0) - win['t_in'])
        t1 = max(0.0, grid.time(j0 + b1) - win['t_in']) if b1 < NB else win['t_out'] - win['t_in']
        parts[name] = dict(bar0=b0 // 4, bar1=b1 // 4, beat0=b0, beat1=b1, t0=round(t0, 4), t1=round(min(t1, win['t_out'] - win['t_in']), 4))
    return parts


# ============================================================================ 2. footage
def _scale_class(face_h):
    if face_h is None:
        return 'wide/no-face'
    if face_h > 0.33:
        return 'extreme-close'
    if face_h > 0.18:
        return 'close'
    if face_h > 0.08:
        return 'medium'
    return 'wide'


def detect_box(path, info, n=16, width=320, thr=14, share=0.85):
    """Picture box inside letterbox / pillarbox bars: a row (column) is a bar when its 90th-percentile luma stays
    below `thr` in ≥ `share` of n frames spread over the clip (burned-in subtitles in a bar don't break it).
    Returns [x0, y0, x1, y1] in source pixels (full frame when there are no bars ≥ 2 %)."""
    W, H = info.get('w') or 0, info.get('h') or 0
    if not W or not H:
        return None
    dur = max(float(info.get('duration') or 1.0), 0.1)
    rows, cols = [], []
    for _, fr in V.frames(path, fps=max(0.05, n / dur), width=width):
        g = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY)
        rows.append(np.percentile(g, 90, axis=1) < thr)
        cols.append(np.percentile(g, 90, axis=0) < thr)
        if len(rows) >= n:
            break
    if not rows:
        return [0, 0, W, H]
    rb = np.mean(rows, axis=0) >= share
    cb = np.mean(cols, axis=0) >= share
    h, w = len(rb), len(cb)

    def span(b, m):
        a = 0
        while a < m and b[a]:
            a += 1
        z = m
        while z > a and b[z - 1]:
            z -= 1
        return a, z
    y0, y1 = span(rb, h)
    x0, x1 = span(cb, w)
    if y1 - y0 < 0.3 * h or x1 - x0 < 0.3 * w:
        return [0, 0, W, H]

    def sym(a, z, m):
        # real bars come in symmetric pairs; a dark sky / dark side of the scene is one-sided -> not a bar
        lo, hi = a, m - z
        if min(lo, hi) < 0.015 * m:
            return 0, m
        b_ = min(lo, hi)
        return b_, m - b_
    y0, y1 = sym(y0, y1, h)
    x0, x1 = sym(x0, x1, w)
    Y0, Y1 = (int(round(y0 * H / h)), int(round(y1 * H / h))) if (y0 >= 0.02 * h or h - y1 >= 0.02 * h) else (0, H)
    X0, X1 = (int(round(x0 * W / w)), int(round(x1 * W / w))) if (x0 >= 0.02 * w or w - x1 >= 0.02 * w) else (0, W)
    # keep the box a little inside the bar edge (soft edges, encoder ringing)
    if Y0 > 0:
        Y0 += 2
    if Y1 < H:
        Y1 -= 2
    if X0 > 0:
        X0 += 2
    if X1 < W:
        X1 -= 2
    return [X0, Y0, X1, Y1]


def analyze_clip(path, cache_dir=None, fps=6.0, width=320):
    """One decode pass: per-sample luma/percentiles, saturation, warmth, sharpness, highlight clipping, sky band,
    camera motion (LK similarity, ed_motion), camera-compensated residual motion ('action'), faces (YuNet),
    person mask (PP-HumanSeg, every 0.5 s), cut scores. Shots + per-shot features. Cached (json + npz thumbs)."""
    import ed_motion as M       # global motion estimator
    path = os.path.abspath(path)
    key = _file_key(path, f'v{FOOTAGE_VERSION}|{fps}|{width}')
    cp = os.path.join(cache_dir, f'clip_{key}.json') if cache_dir else None
    c = _load_json(cp) if (cp and os.path.exists(cp)) else None
    if c and os.path.exists(cp[:-5] + '.npz'):
        c['_gray'] = np.load(cp[:-5] + '.npz')['gray']
        _dark_cuts(c)
        return c
    info = V.probe(path)
    box = detect_box(path, info) or [0, 0, info.get('w') or 1, info.get('h') or 1]
    rows, grays = [], []
    prev_g = prev_h = None
    every_p = max(1, int(round(fps / 2)))
    full = None
    for n, (t, fr) in enumerate(V.frames(path, fps=fps, width=width)):
        sx, sy = fr.shape[1] / float(info.get('w') or fr.shape[1]), fr.shape[0] / float(info.get('h') or fr.shape[0])
        fr = np.ascontiguousarray(fr[int(round(box[1] * sy)):int(round(box[3] * sy)), int(round(box[0] * sx)):int(round(box[2] * sx))])
        g = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY)
        h, w = g.shape
        if full is None:
            full = np.full(g.shape, 255, np.uint8)
        hsv = cv2.cvtColor(fr, cv2.COLOR_RGB2HSV)
        hist = cv2.calcHist([hsv], [0, 1, 2], None, [16, 4, 4], [0, 180, 0, 256, 0, 256]).flatten()
        hist /= hist.sum() + 1e-9
        pc = np.percentile(g, [1, 5, 50, 95, 99])
        m = fr.reshape(-1, 3).mean(0) / 255.0
        top = g[:max(2, h // 7)]
        lap = cv2.Laplacian(g, cv2.CV_32F)
        sl = [slice(int(i * w / 8), int((i + 1) * w / 8)) for i in range(8)]
        row = dict(t=round(float(t), 3), luma=round(float(g.mean()), 1), p1=float(pc[0]), p5=float(pc[1]), p50=float(pc[2]),
                   p95=float(pc[3]), p99=float(pc[4]), sat=round(float(hsv[..., 1].mean()) / 255, 3),
                   warm=round(float(m[0] - m[2]), 3), sharp=round(float(lap.var()), 1),
                   strip_sharp=[round(float(lap[:, x].var()), 1) for x in sl],
                   strip_ct=[round(float(np.subtract(*np.percentile(g[:, x], [95, 5]))) / 255, 3) for x in sl],
                   clip=round(float((g >= 250).mean()), 4), sky=round(float(top.mean()) / 255, 3),
                   sky_tex=round(float(cv2.Laplacian(top, cv2.CV_32F).var()), 1),
                   strips=[round(float(v), 1) for v in g.reshape(h, 8, -1).mean(axis=(0, 2))] if w % 8 == 0 else
                   [round(float(g[:, int(i * w / 8):int((i + 1) * w / 8)].mean()), 1) for i in range(8)])
        if prev_g is not None:
            pdiff = float(np.abs(g.astype(np.int16) - prev_g.astype(np.int16)).mean())
            hd = V.bhatt(prev_h, hist)
            est = M.estimate_pair(prev_g, g, full)
            if est['M'] is not None and est['method'] == 'lk' and est['inl'] >= 0.3 and est['n'] >= 12:
                sc, rot = M.similarity_from_affine(est['M'])
                tx, ty = float(est['M'][0, 2]) / w, float(est['M'][1, 2]) / h
                wp = cv2.warpAffine(prev_g, est['M'], (w, h), borderMode=cv2.BORDER_REPLICATE)
                b = 6
                resid = float(np.abs(wp[b:-b, b:-b].astype(np.int16) - g[b:-b, b:-b].astype(np.int16)).mean())
                cam_ok = 1
            else:
                sc, rot, tx, ty, resid, cam_ok = 1.0, 0.0, 0.0, 0.0, pdiff, 0
        else:
            pdiff = hd = 0.0
            sc, rot, tx, ty, resid, cam_ok = 1.0, 0.0, 0.0, 0.0, 0.0, 0
        row.update(pdiff=round(pdiff, 2), hd=round(float(hd), 4), resid=round(resid, 2), sc=round(float(sc), 4),
                   rot=round(float(rot), 3), tx=round(tx, 5), ty=round(ty, 5), cam_ok=cam_ok)
        big = cv2.resize(fr, (640, int(round(640 * h / w))), interpolation=cv2.INTER_LINEAR)
        H2 = big.shape[0]
        fs = V.faces(big)
        sc_ = w / 640.0

        def face_luma(x):            # brightness of the face itself (a face in a dark hood is not "readable")
            x0, y0 = int(max(0, x['x'] * sc_)), int(max(0, x['y'] * sc_))
            x1, y1 = int(min(w, (x['x'] + x['w']) * sc_)), int(min(h, (x['y'] + x['h']) * sc_))
            return round(float(g[y0:y1, x0:x1].mean()), 1) if (x1 > x0 and y1 > y0) else 0.0
        row['faces'] = [[round((x['x'] + x['w'] / 2) / 640, 3), round((x['y'] + x['h'] / 2) / H2, 3), round(x['h'] / H2, 3),
                         round(x['score'], 2), face_luma(x)] for x in fs[:3]]
        if n % every_p == 0:
            pm = V.person_mask(fr) > 0.5
            cov = float(pm.mean())
            if cov > 0.01:
                ys, xs = np.nonzero(pm)
                row['person'] = [round(cov, 3), round(float(xs.mean()) / w, 3), round(float(ys.min()) / h, 3),
                                 round(float(ys.max()) / h, 3)]
            else:
                row['person'] = [0.0, None, None, None]
        else:
            row['person'] = None
        rows.append(row)
        grays.append(cv2.resize(g, (32, 18), interpolation=cv2.INTER_AREA))
        prev_g, prev_h = g, hist
    if not rows:
        raise RuntimeError(f'no frames decoded from {path}')
    # ---- shot boundaries (same rule as ed_video.detect_cuts, on streaming scores + residual after camera motion)
    hd = np.array([r['hd'] for r in rows])
    pdf = np.array([r['pdiff'] for r in rows])
    rs = np.array([r['resid'] for r in rows])
    med_h, mad_h = np.median(hd), np.median(np.abs(hd - np.median(hd))) + 1e-6
    med_p, mad_p = np.median(pdf), np.median(np.abs(pdf - np.median(pdf))) + 1e-6
    score = (hd - med_h) / (6 * mad_h) + (pdf - med_p) / (6 * mad_p)
    cand = [i for i in range(1, len(rows)) if hd[i] > max(0.25, med_h + 6 * mad_h) and pdf[i] > max(10.0, med_p + 4 * mad_p)
            and (rows[i]['cam_ok'] == 0 or rs[i] > 8.0)]
    cuts, gap = [], max(1, int(round(0.5 * fps)))
    for i in sorted(cand, key=lambda k: -score[k]):
        if all(abs(i - c) >= gap for c in cuts):
            cuts.append(i)
    cuts.sort()
    for c in cuts:                       # the first sample of a shot carries the cut diff, not motion
        if c + 1 < len(rows):
            for k in ('resid', 'pdiff'):
                rows[c][k] = rows[c + 1][k]
            rows[c].update(tx=0.0, ty=0.0, sc=1.0, rot=0.0)
    if len(rows) > 1:
        rows[0]['resid'], rows[0]['pdiff'] = rows[1]['resid'], rows[1]['pdiff']
    clip = dict(path=path, info=info, box=box, fps_sample=fps, width=width, version=FOOTAGE_VERSION, rows=rows, cuts=cuts)
    clip['_gray'] = np.stack(grays)
    clip['shots'] = _shots(clip, clip['_gray'])
    _dark_cuts(clip)
    if cp:
        os.makedirs(cache_dir, exist_ok=True)
        np.savez_compressed(cp[:-5] + '.npz', gray=np.stack(grays))
        _dump_atomic({k: v for k, v in clip.items() if not k.startswith('_')}, cp)
    clip['_gray'] = np.stack(grays)
    return clip


def _dark_cuts(clip):
    """Cuts the absolute pixel-difference rule misses: two dark scenes (or a moving clip whose median difference
    is high) still change their histogram and their structure at a cut. On the cached 32x18 thumbnails: a strong
    histogram change, structure decorrelated across the cut (normalised correlation < 0.3) while each side is
    coherent (both neighbouring pairs correlate >= 0.3 more), and a brightness-normalised difference > 0.4.
    Adds them to clip['cuts'] and recomputes the shots; returns the added sample indices."""
    G = clip.get('_gray')
    rows = clip['rows']
    if G is None or len(G) < 4 or len(G) != len(rows):
        return []
    G = G.astype(np.float32).reshape(len(G), -1)
    m = G.mean(1)
    z = (G - m[:, None]) / (G.std(1)[:, None] + 2.0)
    corr = np.ones(len(G))
    corr[1:] = (z[1:] * z[:-1]).mean(1)
    nd = np.zeros(len(G))
    nd[1:] = np.abs(G[1:] - G[:-1]).mean(1) / (0.5 * (m[1:] + m[:-1]) + 6.0)
    hd = np.array([r.get('hd', 0.0) for r in rows])
    med_h, mad_h = np.median(hd), np.median(np.abs(hd - np.median(hd))) + 1e-6
    fps = clip.get('fps_sample') or 6.0
    gap = max(1, int(round(0.5 * fps)))
    have = list(clip.get('cuts') or [])
    add = []
    for i in range(2, len(G) - 1):
        if hd[i] > max(0.3, med_h + 6 * mad_h) and corr[i] < 0.3 and nd[i] > 0.4 and \
                min(corr[i - 1], corr[i + 1]) >= corr[i] + 0.3 and all(abs(i - c) >= gap for c in have + add):
            add.append(i)
    if add:
        for c in add:                       # the first sample of a shot carries the cut diff, not motion
            if c + 1 < len(rows):
                for k in ('resid', 'pdiff'):
                    rows[c][k] = rows[c + 1][k]
                rows[c].update(tx=0.0, ty=0.0, sc=1.0, rot=0.0)
        clip['cuts'] = sorted(have + add)
        clip.pop('_np', None)
        clip['shots'] = _shots(clip, clip['_gray'])
    return add


def _series(clip):
    if '_np' in clip:
        return clip['_np']
    rows = clip['rows']
    S = {k: np.array([r[k] for r in rows], float) for k in ('t', 'luma', 'p1', 'p5', 'p95', 'p99', 'sat', 'warm', 'sharp',
                                                               'clip', 'sky', 'sky_tex', 'pdiff', 'resid', 'sc', 'rot', 'tx',
                                                               'ty', 'cam_ok')}
    S['contrast'] = (S['p95'] - S['p5']) / 255.0
    S['strips'] = np.array([r.get('strips') or [r['luma']] * 8 for r in rows], float)     # luma of 8 vertical strips
    S['strip_sharp'] = np.array([r.get('strip_sharp') or [r['sharp']] * 8 for r in rows], float)
    S['strip_ct'] = np.array([r.get('strip_ct') or [(r['p95'] - r['p5']) / 255.0] * 8 for r in rows], float)
    S['nfaces'] = np.array([len(r['faces']) for r in rows], float)
    S['face_h'] = np.array([r['faces'][0][2] if r['faces'] else np.nan for r in rows], float)
    S['face_cx'] = np.array([r['faces'][0][0] if r['faces'] else np.nan for r in rows], float)
    S['face_cy'] = np.array([r['faces'][0][1] if r['faces'] else np.nan for r in rows], float)
    S['face_luma'] = np.array([r['faces'][0][4] if (r['faces'] and len(r['faces'][0]) > 4) else np.nan for r in rows], float)
    S['face_spread'] = np.array([(max(f[0] for f in r['faces']) - min(f[0] for f in r['faces'])) if len(r['faces']) > 1 else 0.0
                                 for r in rows], float)
    S['person'] = np.array([r['person'][0] if r['person'] else np.nan for r in rows], float)
    S['p_top'] = np.array([r['person'][2] if (r['person'] and r['person'][2] is not None) else np.nan for r in rows], float)
    S['p_cx'] = np.array([r['person'][1] if (r['person'] and r['person'][1] is not None) else np.nan for r in rows], float)
    clip['_np'] = S
    return S


def _shots(clip, grays):
    S = _series(clip)
    fps = clip['fps_sample']
    n = len(S['t'])
    bounds = [0] + list(clip['cuts']) + [n]
    shots = []
    for k in range(len(bounds) - 1):
        a, b = bounds[k], bounds[k + 1]
        if b - a < 2:
            continue
        r = S['resid'][a:b]
        rsm = gaussian_filter1d(r, 1.0) if len(r) > 3 else r
        prom = max(1.0, 0.5 * float(np.std(rsm)))
        pk, props = find_peaks(rsm, prominence=prom, distance=max(1, int(round(0.3 * fps))))
        peaks = [[round(float(S['t'][a + i]), 3), round(float(rsm[i]), 2)] for i in pk]
        fh = S['face_h'][a:b]
        fh = fh[~np.isnan(fh)]
        face_share = float(np.mean(S['nfaces'][a:b] > 0))
        pers = S['person'][a:b]
        pers = pers[~np.isnan(pers)]
        sig = grays[a:b][np.linspace(0, b - a - 1, min(3, b - a)).astype(int)].astype(np.float32).mean(0)
        sig = (sig - sig.mean()) / (sig.std() + 1e-6)
        shots.append(dict(i=len(shots) + 1, a=a, b=b, t0=round(float(S['t'][a]), 3), t1=round(float(S['t'][b - 1]) + 1.0 / fps, 3),
                          dur=round((b - a) / fps, 3), motion=round(float(r.mean()), 2), peaks=peaks,
                          sharp=round(float(np.median(S['sharp'][a:b])), 1), luma=round(float(S['luma'][a:b].mean()), 1),
                          contrast=round(float(S['contrast'][a:b].mean()), 3), sat=round(float(S['sat'][a:b].mean()), 3),
                          warm=round(float(S['warm'][a:b].mean()), 3), face_share=round(face_share, 2),
                          face_h=round(float(np.median(fh)), 3) if len(fh) else None,
                          person=round(float(np.median(pers)), 3) if len(pers) else None,
                          scale=_scale_class(float(np.median(fh)) if (len(fh) and face_share >= 0.3) else None),
                          sig=[round(float(v), 2) for v in sig.ravel()]))
    return shots


class Footage:
    """All user clips: shots with ids 'name#i', global feature distributions (for ranks), duplicate groups,
    window features and candidate generation."""

    def __init__(self, paths, cache_dir=None, fps=6.0, log=print, clips=None):
        """paths: file paths or dicts {"path", "name", "role" ('hero': preferred for the drop / hook / freeze slots,
        'broll': kept out of them; speech genres: 'aroll' / 'voice'), "weight" (score bonus x0.3 per unit above 1),
        "t0", "t1" (use only this source range)}; several sources mix freely (shot ids are 'name#i').
        clips: already analysed clip dicts (analyze_clip format) instead of paths (tests, other planners)."""
        self.clips, taken = [], set()
        items = [p if isinstance(p, dict) else dict(path=p) for p in (paths or [])]
        if clips is not None:
            items = [dict(_clip=c, path=c.get('path', f'clip{i}'), **{k: c[k] for k in ('name', 'role', 'weight', 't0', 't1')
                                                                    if k in c}) for i, c in enumerate(clips)]
        for it in items:
            t = time.time()
            c = it.get('_clip') or analyze_clip(it['path'], cache_dir, fps)
            c['name'] = _clean_name(it.get('name') or it['path'], taken)
            c['role'] = it.get('role')
            c['weight'] = float(it.get('weight') or 1.0)
            c['range'] = [float(it['t0']) if it.get('t0') is not None else None,
                          float(it['t1']) if it.get('t1') is not None else None]
            _series(c)
            self.clips.append(c)
            if log:
                log(f'[footage] {c["name"]}: {c["info"]["duration"]:.1f}s {len(c["shots"])} shots ({time.time() - t:.0f}s)')
        self.shots = []
        for ci, c in enumerate(self.clips):
            r0, r1 = c['range']
            for s in c['shots']:
                s = dict(s)
                if r0 is not None or r1 is not None:            # the user's source range: shots clipped to it
                    a, b = max(s['t0'], r0 if r0 is not None else -1), min(s['t1'], r1 if r1 is not None else 1e9)
                    if b - a < 0.3:
                        continue
                    s['t0'], s['t1'], s['dur'] = round(a, 3), round(b, 3), round(b - a, 3)
                    s['peaks'] = [p for p in s['peaks'] if a <= p[0] <= b]
                s.update(ci=ci, id=f'{c["name"]}#{s["i"]}', src=c['name'], src_fps=float(c['info'].get('fps') or 25.0),
                         weight=c['weight'], role=c.get('role'))
                self.shots.append(s)
        if not self.shots:
            raise ValueError('no usable shots in the footage (empty files or source ranges shorter than 0.3 s)')
        cat = lambda k: np.sort(np.concatenate([c['_np'][k] for c in self.clips]))
        self.dist = {k: cat(k) for k in ('resid', 'sharp', 'contrast', 'sat', 'luma', 'warm')}
        self.dist['strip_sharp'] = np.sort(np.concatenate([c['_np']['strip_sharp'].ravel() for c in self.clips]))
        self._dups()
        self.heterogeneous = len({(c['info'].get('w'), c['info'].get('h'), round(c['info'].get('fps') or 0)) for c in self.clips}) > 1

    @classmethod
    def from_clips(cls, clips, log=None):
        """Footage from analysed clip dicts (analyze_clip output, or synthetic ones in tests)."""
        return cls(None, log=log, clips=clips)

    def _dups(self):
        """Near-duplicate shots (same footage re-encoded / re-cropped / a sub-range of another clip): any pair of
        textured 32×18 samples (≈1 per second of each shot) correlating > 0.93 puts both shots in one group."""
        n = len(self.shots)
        parent = list(range(n))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        vecs, owner = [], []
        for si, s in enumerate(self.shots):
            c = self.clips[s['ci']]
            gr = c.get('_gray')
            if gr is None:
                continue
            step = max(1, int(round(c['fps_sample'])))
            for r in range(s['a'], s['b'], step)[:12]:
                v = gr[r].astype(np.float32).ravel()
                if v.std() < 6:                       # flat / black frames match anything
                    continue
                vecs.append((v - v.mean()) / v.std())
                owner.append(si)
        if len(vecs) > 1:
            X = np.stack(vecs)
            C = (X @ X.T) / X.shape[1]
            own = np.asarray(owner)
            ii, jj = np.nonzero(np.triu(C > 0.93, 1))
            for i, j in zip(ii, jj):
                if own[i] != own[j]:
                    parent[find(int(own[j]))] = find(int(own[i]))
        for i, s in enumerate(self.shots):
            s['dup'] = int(find(i))
        self.dup_groups = {}
        for s in self.shots:
            self.dup_groups.setdefault(s['dup'], []).append(s['id'])

    def shot(self, sid):
        return next(s for s in self.shots if s['id'] == sid)

    def win(self, sh, w0, w1):
        """Features of source window [w0, w1] inside shot sh (ranks against all footage)."""
        c = self.clips[sh['ci']]
        S = c['_np']
        a = int(np.searchsorted(S['t'], w0 - 1e-6))
        b = int(np.searchsorted(S['t'], w1 + 1e-6))
        a = min(max(a, sh['a']), sh['b'] - 1)
        b = min(max(b, a + 1), sh['b'])
        sl = slice(a, b)
        fps = c['fps_sample']
        r = S['resid'][sl]
        fh = S['face_h'][sl]
        has_f = ~np.isnan(fh)
        face_share = float(has_f.mean())
        face_h = float(np.median(fh[has_f])) if has_f.any() else None
        pers = S['person'][sl]
        pers = pers[~np.isnan(pers)]
        ptop = S['p_top'][sl]
        ptop = ptop[~np.isnan(ptop)]
        ok = S['cam_ok'][sl] > 0
        tx, ty = S['tx'][sl][ok], S['ty'][sl][ok]
        if len(tx) >= 4:
            # positional noise of the picture (% of frame): per-sample translation minus its smooth trend (pan),
            # robust σ (MAD) / √2 (a sample-to-sample difference of i.i.d. offsets has √2 σ); drift-free
            hx, hy = tx - gaussian_filter1d(tx, 1.5), ty - gaussian_filter1d(ty, 1.5)
            mad = lambda v: 1.4826 * float(np.median(np.abs(v - np.median(v))))
            jitter = float(np.hypot(mad(hx), mad(hy))) / math.sqrt(2) * 100
        else:
            jitter = 0.0
        pan = float(np.hypot(S['tx'][sl].mean(), S['ty'][sl].mean())) * fps / 30.0 * 100
        zoom = float(np.log(np.clip(S['sc'][sl], 0.5, 2.0)).mean()) * fps
        i_pk = int(np.argmax(r)) if len(r) else 0
        peaks_in = [p for p in sh['peaks'] if w0 <= p[0] <= w1]
        luma = float(S['luma'][sl].mean())
        # luma where the 9:16 window will actually be (it follows the face / the centre): vertical strips around it
        bx = c.get('box') or [0, 0, c['info'].get('w') or 16, c['info'].get('h') or 9]
        ww_ = min(1.0, (9 / 16) / ((bx[2] - bx[0]) / max(1, bx[3] - bx[1])))
        pcx = S['p_cx'][sl] if 'p_cx' in S else np.array([np.nan])
        fcx = float(np.nanmedian(S['face_cx'][sl])) if (~np.isnan(S['face_cx'][sl])).any() else \
            (float(np.nanmedian(pcx)) if (~np.isnan(pcx)).any() else 0.5)
        lo_s, hi_s = int(np.clip(math.floor((fcx - ww_ / 2) * 8), 0, 7)), int(np.clip(math.ceil((fcx + ww_ / 2) * 8) - 1, 0, 7))
        # the crop follows the face sample by sample: its luma comes from the strips around each sample's face
        # (a dark sweep through a following window shows up here, not in the median position)
        fc = S['face_cx'][sl].copy()
        last = fcx
        for i in range(len(fc)):
            last = fc[i] = last if np.isnan(fc[i]) else fc[i]
        st = S['strips'][sl]
        crop_l = np.array([st[i, int(np.clip(math.floor((fc[i] - ww_ / 2) * 8), 0, 7)):int(np.clip(math.ceil((fc[i] + ww_ / 2) * 8) - 1, 0, 7)) + 1].mean()
                           for i in range(len(fc))]) if len(fc) else S['strips'][sl][:, lo_s:hi_s + 1].mean(axis=1)
        # the strip under the subject (the centre a punch-in / crash zoom fills the screen with): a whip pan or a
        # subject leaving the frame shows here as a near-black dip that the crop average hides
        mid_l = np.array([st[i, int(np.clip(fc[i] * 8, 0, 7))] for i in range(len(fc))]) if len(fc) else crop_l
        sharp_c = float(np.median(S['strip_sharp'][sl][:, lo_s:hi_s + 1].mean(axis=1)))     # inside the crop window
        contrast_c = float(np.mean(S['strip_ct'][sl][:, lo_s:hi_s + 1]))
        W = dict(motion=float(r.mean()), peak=float(r.max()) if len(r) else 0.0, luma_c=float(crop_l.mean()), luma_c_min=float(crop_l.min()),
                 luma_mid_min=float(mid_l.min()) if len(mid_l) else float(crop_l.min()),
                 sharp_c=sharp_c, contrast_c=contrast_c, crop_cx=fcx,
                 peak_pos=float((S['t'][a + i_pk] - w0) / max(w1 - w0, 1e-6)) if len(r) else 0.5,
                 n_peaks=len(peaks_in), peaks_per_s=len(peaks_in) / max(w1 - w0, 0.25),
                 sharp=float(np.median(S['sharp'][sl])), sharp0=float(S['sharp'][a]), sharp_max=float(S['sharp'][sl].max()),
                 luma=luma, luma_min=float(S['luma'][sl].min()), contrast=float(S['contrast'][sl].mean()), sat=float(S['sat'][sl].mean()),
                 warm=float(S['warm'][sl].mean()),
                 clip=float(S['clip'][sl].mean()), p99=float(S['p99'][sl].mean()), sky=float(S['sky'][sl].mean()),
                 face_share=face_share, face_h=face_h, face_cx=float(np.nanmedian(S['face_cx'][sl])) if has_f.any() else None,
                 face_luma=float(np.nanmedian(S['face_luma'][sl])) if (has_f.any() and not np.isnan(S['face_luma'][sl]).all()) else None,
                 face_cy=float(np.nanmedian(S['face_cy'][sl])) if has_f.any() else None,
                 nfaces=float(S['nfaces'][sl].max()), face_spread=float(S['face_spread'][sl].max()),
                 person=float(np.median(pers)) if len(pers) else None, person_top=float(np.median(ptop)) if len(ptop) else None,
                 jitter=jitter, pan=pan, zoom=zoom, tx_end=float(S['tx'][max(a, b - 2):b].mean()),
                 tx_start=float(S['tx'][a:min(b, a + 2)].mean()), src_fps=sh['src_fps'],
                 edge_in=float(r[:2].mean()) if len(r) else 0.0, edge_out=float(r[-2:].mean()) if len(r) else 0.0)
        d = self.dist
        W.update(sharp_c_r=_rank(d.get('strip_sharp'), sharp_c) if d.get('strip_sharp') is not None else None)
        W.update(edge_in_r=_rank(d['resid'], W['edge_in']), edge_out_r=_rank(d['resid'], W['edge_out']))
        W.update(motion_r=_rank(d['resid'], W['motion']), peak_r=_rank(d['resid'], W['peak']), sharp_r=_rank(d['sharp'], W['sharp']),
                 sharp0_r=_rank(d['sharp'], W['sharp0']), sharpmax_r=_rank(d['sharp'], W['sharp_max']),
                 contrast_r=_rank(d['contrast'], W['contrast']), sat_r=_rank(d['sat'], W['sat']), luma_r=_rank(d['luma'], luma),
                 warm_r=_rank(d['warm'], W['warm']))
        if face_h is not None and face_share >= 0.3:
            W['size'] = _scale_class(face_h)
        elif W['person'] is not None and W['person'] > 0.3:
            W['size'] = 'medium'
        elif W['person'] is not None and W['person'] > 0.03:
            W['size'] = 'wide'
        else:
            W['size'] = 'wide/no-face'
        # what a viewer can read in the window: a lit face, a person, a scene (sky band / sharp structure) or only
        # texture (no subject: fire, fur, snow, blur). Texture never goes to hero / establishing slots.
        pers = W['person'] or 0.0
        sky_band = W['sky'] > luma / 255 + 0.06
        sc_r = W['sharp_c_r'] if W.get('sharp_c_r') is not None else W['sharp_r']   # detail inside the 9:16 window
        ct_c = W.get('contrast_c', W['contrast'])
        W['static'] = _band(W['jitter'], 0, 0.15, 0.3) * _band(W['pan'], 0, 0.08, 0.2)
        if _face_ok(W, 0.04, 40):
            subj = 'face'
        elif pers >= 0.05 and W['luma_c'] >= 30 and (sc_r >= 0.2 or ct_c >= 0.3):
            subj = 'person'
        elif (sky_band and sc_r >= 0.3 and ct_c >= 0.15) or (sc_r >= 0.55 and ct_c >= 0.3) \
                or (W['luma_c'] >= 70 and W['static'] >= 0.5 and W['motion_r'] <= 0.5 and pers <= 0.05):
            subj = 'scene'                                 # (last: a bright, still, subject-less frame = fog / snow / sky)
        else:
            subj = 'texture'                               # what the crop shows is a blur, a dark blob or a surface
        W['subject'] = subj
        W['scenic'] = 1.0 if (subj == 'scene' or (subj == 'person' and pers <= 0.12)) else 0.0
        dark = 1.0 if W['luma_c'] >= 40 else (0.75 if W['luma_c'] >= 25 else 0.45)
        W['readable'] = round({'face': 1.0, 'person': 0.75, 'scene': 0.6, 'texture': 0.15}[subj] * dark *
                              (0.6 + 0.4 * sc_r), 3)
        if subj == 'texture' and W['size'] in ('wide', 'wide/no-face'):
            W['size'] = 'detail'                           # no subject and no scene: a texture close-up, not a wide shot
        W['ews'] = 1.0 if (face_share < 0.15 and (W['person'] is None or W['person'] <= 0.05) and subj == 'scene') else 0.0
        W['low_angle'] = 1.0 if (W['person_top'] is not None and W['person_top'] < 0.2 and W['sky'] > luma / 255 + 0.05) else 0.0
        W['weight'] = float(sh.get('weight', 1.0))
        W['role'] = sh.get('role')
        return W

    def thumb(self, ci, t):
        """32x18 gray thumbnail of clip ci nearest to source time t (the analysis cache), float32; None without one."""
        c = self.clips[ci]
        G = c.get('_gray')
        if G is None or not len(G):
            return None
        S = c['_np']
        i = int(np.clip(np.searchsorted(S['t'], t), 0, len(G) - 1))
        if i > 0 and abs(S['t'][i - 1] - t) < abs(S['t'][i] - t):
            i -= 1
        return G[i].astype(np.float32)

    def similarity(self, ci_a, t_a, ci_b, t_b, cx_a=None, cx_b=None, ww=0.32):
        """How alike two moments look at a cut (0..1): structure correlation of the thumbnails (inside the crop band
        at cx when given) times how close their brightness is. Near 1 = the cut would not read."""
        a, b = self.thumb(ci_a, t_a), self.thumb(ci_b, t_b)
        if a is None or b is None:
            return 0.0

        def band(g, cx):
            if cx is None:
                return g
            w = g.shape[1]
            half = max(2, int(round(ww * w / 2)))
            c = int(round(min(max(cx, ww / 2), 1 - ww / 2) * w))
            return g[:, max(0, c - half):min(w, c + half)]
        a, b = band(a, cx_a), band(b, cx_b)
        if a.shape != b.shape:
            b = cv2.resize(b, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_AREA)
        da, db = a - a.mean(), b - b.mean()
        corr = float((da * db).mean() / math.sqrt((float((da * da).mean()) + 16.0) * (float((db * db).mean()) + 16.0)))
        if a.std() < 6.0 and b.std() < 6.0:              # two flat frames (dark / foggy): structure says nothing
            corr = 1.0
        return max(0.0, corr) * max(0.0, 1.0 - abs(float(a.mean()) - float(b.mean())) / 40.0)

    def crop_luma(self, ci, w0, w1, cx, win_w):
        """mean luma (0–255) of the source window [w0, w1] inside the vertical band the 9:16 crop sees (cx ± win_w/2)."""
        S = self.clips[ci]['_np']
        a = int(np.searchsorted(S['t'], w0 - 1e-6))
        b = max(a + 1, int(np.searchsorted(S['t'], w1 + 1e-6)))
        lo, hi = int(np.clip(math.floor((cx - win_w / 2) * 8), 0, 7)), int(np.clip(math.ceil((cx + win_w / 2) * 8) - 1, 0, 7))
        v = S['strips'][a:b, lo:hi + 1]
        return float(v.mean()) if v.size else float(S['luma'][a:b].mean())

    def candidates(self, need, h_in=0.0, h_out=0.0, accent_offsets=(), margin=0.2, max_per_shot=10):
        """Source windows of length `need` (+ handles) inside shots: a regular grid plus windows whose action peaks
        land on the slot's accent offsets (window start solved from peak time)."""
        out = []
        for sh in self.shots:
            lo, hi = sh['t0'] + margin + h_in, sh['t1'] - margin - h_out - need
            if hi < lo - 1e-6:
                continue
            starts = set()
            if hi - lo < 0.05:
                starts.add(round(lo, 3))
            else:
                k = int(min(max_per_shot, max(2, (hi - lo) / max(0.25, need / 3) + 1)))
                for v in np.linspace(lo, hi, k):
                    starts.add(round(float(v), 3))
            aligned = set()
            for p_t, _ in sh['peaks']:
                for o in accent_offsets:
                    w0 = p_t - o
                    if lo - 1e-6 <= w0 <= hi + 1e-6:
                        aligned.add(round(w0, 3))
            for w0 in sorted(starts | aligned):
                out.append((sh, w0, w0 in aligned))
        return out


# ============================================================================ 3. slots (cut grid)
def _lens_from_card(g, part, period, fast_ok=True):
    lo_s, hi_s = g['rhythm']['shot_len_s'][part]
    lo_b, hi_b = lo_s / REF_BEAT, hi_s / REF_BEAT
    unit = 0.5 if (lo_b < 1.0 and fast_ok) else 1.0
    lens = [x for x in np.arange(unit, max(hi_b, unit) + 1e-6, unit) if lo_b - 1e-6 <= x <= hi_b + 1e-6]
    if period < 0.43:                                   # ≥ 140 BPM: no cuts faster than a beat outside bursts
        lens = [x for x in lens if x >= 1.0] or [1.0, 2.0]
    if not lens:
        lens = [max(1.0, round(hi_b))]
    return lens, (lo_b + hi_b) / 2


def tile(b0, b1, lens, target, grid, j0, rng, half_pen=0.35, down_bonus=0.25, accent_w=0.6):
    """Cover window beats [b0, b1) with shot lengths from `lens` (beats). DP over the half-beat grid:
    cost = Σ((L − target)/target)² + per cut: accent_w·(1 − onset strength at the cut) + down_bonus if the cut is not
    on a downbeat + half_pen on half beats. Cuts are penalised where weak (never rewarded), so the number of cuts
    follows the card's shot lengths and strong beats / downbeats only decide where they go."""
    unit = 0.5
    N = int(round((b1 - b0) / unit))
    if N <= 0:
        return []
    lu = sorted({int(round(L / unit)) for L in lens if L > 0})
    INF = 1e18
    cost, prev = [INF] * (N + 1), [-1] * (N + 1)
    cost[0] = 0.0
    for i in range(N):
        if cost[i] >= INF:
            continue
        for u in lu:
            j = i + u
            if j > N:
                break
            L = u * unit
            c = ((L - target) / target) ** 2 + rng.uniform(0, 0.04)
            if j < N:
                pos = b0 + j * unit
                jb = j0 + int(math.floor(pos))
                if abs(pos - round(pos)) > 1e-6:
                    hs = float(grid.half[jb]) if 0 <= jb < len(grid.half) else 0.0
                    c += half_pen + down_bonus + accent_w * (1.0 - min(1.0, hs))
                else:
                    jj = j0 + int(round(pos))
                    if 0 <= jj < len(grid.t):
                        c += accent_w * (1.0 - min(1.0, float(max(grid.kick[jj], grid.onset[jj]))))
                        if not grid.is_down(jj):
                            c += down_bonus
            if cost[i] + c < cost[j]:
                cost[j], prev[j] = cost[i] + c, i
    if cost[N] >= INF:
        L = max(lens)
        out, s = [], b0
        while s < b1 - 1e-6:
            out.append((s, min(b1, s + L)))
            s += L
        return out
    out, j = [], N
    while j > 0:
        i = prev[j]
        out.append((b0 + i * unit, b0 + j * unit))
        j = i
    return out[::-1]


def _slot(part, role, b0, b1, kind='shot', **kw):
    d = dict(part=part, role=role, b0=float(b0), b1=float(b1), kind=kind, speed=dict(mode='normal'))
    d.update(kw)
    return d


def build_slots(g, parts, grid, win, rng, opts):
    """Genre recipes (phonk, epic, calm) + a generic recipe for the other cards."""
    slug = g['slug']
    P = {k: (v['beat0'], v['beat1']) for k, v in parts.items()}
    j0 = win['j0']
    period = grid.period
    fn = {'phonk': _slots_phonk, 'epic': _slots_epic, 'calm': _slots_calm}.get(slug, _slots_generic)
    slots = fn(g, P, grid, j0, period, rng, opts)
    for i, s in enumerate(slots):
        s['i'] = i
    return slots


def _tile_part(g, P, part, grid, j0, period, rng, role, b0=None, b1=None, lens=None, **kw):
    a, b = P[part]
    a = a if b0 is None else b0
    b = b if b1 is None else b1
    if b - a <= 0:
        return []
    L, target = _lens_from_card(g, part, period)
    if lens:
        L = lens
        target = kw.pop('target', sum(lens) / len(lens))
    else:
        target = kw.pop('target', target)
    return [_slot(part, role, x, y) for x, y in tile(a, b, L, target, grid, j0, rng, **kw)]


def _slots_phonk(g, P, grid, j0, period, rng, opts):
    S = []
    fast = period < 0.43
    # hook: one plan per bar (or a cut on beat 3)
    S += _tile_part(g, P, 'hook', grid, j0, period, rng, 'hook', lens=[2.0, 4.0], target=4.0)
    # build: one plan per 2 beats; last bar each beat; last 2 beats cut.stutter
    b0, b1 = P['build']
    if b1 - b0 >= 4:
        S += _tile_part(g, P, 'build', grid, j0, period, rng, 'build', b0, b1 - 4, lens=[2.0], target=2.0)
        S += [_slot('build', 'build', b1 - 4, b1 - 3), _slot('build', 'build', b1 - 3, b1 - 2)]
        S.append(_slot('build', 'stutter', b1 - 2, b1, kind='stutter', speed=dict(mode='stutter')))
    elif b1 > b0:
        S += _tile_part(g, P, 'build', grid, j0, period, rng, 'build', lens=[1.0, 2.0], target=2.0)
    # drop: velocity clips 1–3 beats (2–4 at 140+), cuts only on beats; one 1/8 burst bar (cut.quick); one clip that
    # spans a downbeat in the second half for zoom.crash (run-up ≥ 0.4 s before the landing); last beat -> outro ramp
    d0, d1 = P['drop']
    o0, o1 = P['outro']
    end = d1 - 1 if o1 > o0 else d1
    nbars = (end - d0) // 4
    reserved = []
    if nbars >= 3:
        cand = list(range(d0 // 4 + 1, (end // 4) - 1))
        if cand:
            k = max(cand, key=lambda br: float(np.mean(grid.onset[j0 + 4 * br:j0 + 4 * br + 4]) + np.mean(grid.half[j0 + 4 * br:j0 + 4 * br + 4])))
            reserved.append(('burst', 4 * k, 4 * k + (2 if fast else 4)))
    if nbars >= 2:
        lead = 1 if period >= 0.4 else 2
        half_bar = d0 // 4 + max(1, nbars // 2)
        for kc in range(half_bar, end // 4):
            a_, b_ = 4 * kc - lead, 4 * kc + 2
            if b_ <= end and a_ > d0 and all(b_ <= r[1] or a_ >= r[2] for r in reserved):
                reserved.append(('crash', a_, b_))
                break
    reserved.sort(key=lambda r: r[1])
    vlens = [2.0, 3.0, 4.0] if fast else [1.0, 2.0, 3.0]
    x = d0
    first = True
    for kind, a_, b_ in reserved + [('end', end, end)]:
        if a_ > x:
            for u, v in tile(x, a_, vlens, 2.0, grid, j0, rng, half_pen=5.0):
                S.append(_slot('drop', 'drop_first' if first else 'drop', u, v, speed=dict(mode='velocity')))
                first = False
        if kind == 'burst':
            for k in range(int((b_ - a_) / 0.5)):
                S.append(_slot('drop', 'burst', a_ + 0.5 * k, a_ + 0.5 * (k + 1), kind='burst'))
        elif kind == 'crash':
            S.append(_slot('drop', 'crash', a_, b_, crash=True))
        x = max(x, b_)
    S.sort(key=lambda s: s['b0'])
    # outro: ramp into a freeze on the last hit, black tail ≤ 1 s
    if o1 > o0:
        hold = 3.0 if (o1 - o0) >= 4 else max(1.0, o1 - o0 - 1)
        S.append(_slot('outro', 'freeze', end, o1, kind='freeze',
                       speed=dict(mode='ramp_freeze', ramp_beats=float(o0 - end), hold_beats=hold),
                       black_from=o0 + hold if o0 + hold < o1 else None))
    return S


def _slots_epic(g, P, grid, j0, period, rng, opts):
    S = []
    h0, h1 = P['hook']
    if h1 - h0 >= 8:
        S += [_slot('hook', 'hook', h0, h0 + 4), _slot('hook', 'hook2', h0 + 4, h1)]
    else:
        S.append(_slot('hook', 'hook', h0, h1))
    b0, b1 = P['build']
    nb = (b1 - b0) // 4
    if nb >= 3:
        n4 = max(1, int(math.ceil((nb - 2) / 2)))
        n2 = max(0, nb - 2 - n4)
        x = b0
        S += [_slot('build', 'build', x + 4 * k, x + 4 * k + 4) for k in range(n4)]
        x += 4 * n4
        S += [_slot('build', 'build', x + 2 * k, x + 2 * k + 2) for k in range(2 * n2)]
        x += 4 * n2
        S += [_slot('build', 'build', x + k, x + k + 1, dip=(k % 2 == 0)) for k in range(4)]   # trailer pulse: dips on beats 1, 3
        x += 4
        S += [_slot('build', 'build', x + k, x + k + 1) for k in range(3)]
        S.append(_slot('build', 'black', x + 3, x + 4, kind='black'))                          # black breath
    elif b1 > b0:
        S += _tile_part(g, P, 'build', grid, j0, period, rng, 'build', lens=[2.0, 4.0], target=3.0)
    d0, d1 = P['drop']
    nd = (d1 - d0) // 4
    slow_first = 0.45
    S.append(_slot('drop', 'drop_first', d0, d0 + 4, speed=dict(mode='slow', rate=slow_first)))
    x = d0 + 4
    last = d1 - 4 if nd >= 3 else d1
    if last > x:
        # every 2 beats; one bar of beat cuts on the strongest drum bar (≤ 2 bars per the card)
        bars = list(range(x // 4, last // 4))
        hot = max(bars, key=lambda br: float(np.mean(grid.onset[j0 + 4 * br:j0 + 4 * br + 4]))) if len(bars) >= 2 else None
        for br in bars:
            if br == hot:
                S += [_slot('drop', 'drop', 4 * br + k, 4 * br + k + 1) for k in range(4)]
            else:
                S += [_slot('drop', 'drop', 4 * br, 4 * br + 2), _slot('drop', 'drop', 4 * br + 2, 4 * br + 4)]
        if (last - x) % 4:
            S.append(_slot('drop', 'drop', 4 * (last // 4), last))
    if nd >= 3:
        S.append(_slot('drop', 'drop_wide', d1 - 4, d1, speed=dict(mode='slow', rate=0.5)))
    o0, o1 = P['outro']
    if o1 - o0 > 8:
        S += [_slot('outro', 'outro2', o0, o1 - 8), _slot('outro', 'outro', o1 - 8, o1)]
    elif o1 > o0:
        S.append(_slot('outro', 'outro', o0, o1))
    # slow motion on 1–2 shots of the first half of the build (≤ 50 % of the build)
    build = [s for s in S if s['part'] == 'build' and s['kind'] == 'shot']
    half = [s for s in build if s['b1'] <= (b0 + b1) / 2 + 1e-6 and s['b1'] - s['b0'] >= 4]
    for s in half[:2]:
        s['speed'] = dict(mode='slow', rate=0.5)
    # speed ramps on drop 2-beat shots: ≤ 1 per bar, ≤ 2 per 10 s
    T = grid.time(j0 + P['outro'][1]) - grid.time(j0)
    budget = max(1, int(2 * T / 10))
    ramps = [s for s in S if s['role'] == 'drop' and abs(s['b1'] - s['b0'] - 2) < 1e-6]
    used_bars = set()
    for s in ramps[::2]:
        if budget <= 0:
            break
        br = int(s['b0'] // 4)
        if br in used_bars:
            continue
        s['speed'] = dict(mode='ramp', fast=2.2, slow=0.35, at_beat=1.0)
        used_bars.add(br)
        budget -= 1
    S.sort(key=lambda s: s['b0'])
    return S


def _slots_calm(g, P, grid, j0, period, rng, opts):
    S = []
    max_b = g['rhythm'].get('max_shot_s', 6) / REF_BEAT
    h0, h1 = P['hook']
    if h1 - h0 <= max_b:
        S.append(_slot('hook', 'hook', h0, h1))
    else:
        S += _tile_part(g, P, 'hook', grid, j0, period, rng, 'hook', lens=[4.0, 8.0], target=8.0, down_bonus=2.0)
    b0, b1 = P['build']
    S += [s for s in _tile_part(g, P, 'build', grid, j0, period, rng, 'build', lens=[4.0, 8.0], target=6.0, down_bonus=2.0)]
    d0, d1 = P['drop']
    first = min(d1, d0 + (12 if d1 - d0 >= 16 else 8))
    S.append(_slot('drop', 'drop_first', d0, first, speed=dict(mode='slow', rate=0.6)))
    if d1 > first:
        S += _tile_part(g, P, 'drop', grid, j0, period, rng, 'drop', first, d1, lens=[8.0, 12.0] if d1 - first >= 8 else [d1 - first],
                        target=8.0, down_bonus=2.0)
    o0, o1 = P['outro']
    if o1 - o0 <= max_b:
        S.append(_slot('outro', 'outro', o0, o1))
    elif o1 > o0:
        S += [_slot('outro', 'outro2', o0, o1 - 8), _slot('outro', 'outro', o1 - 8, o1)]
    return S


def _slots_generic(g, P, grid, j0, period, rng, opts):
    """Other cards: card shot lengths per part; drop: hero first shot (slow-mo / velocity per the card), a 1/8 burst
    bar when cut.quick is listed, a clip spanning a downbeat for zoom.crash, ramps for time.speed_ramp;
    outro: ramp into a freeze when time.freeze is listed there."""
    pm = g['part_moves']
    sig = set(g['signature'])
    S = []
    fast = period < 0.43
    for part in ('hook', 'build'):
        a, b = P[part]
        if b > a:
            S += _tile_part(g, P, part, grid, j0, period, rng, part)
    d0, d1 = P['drop']
    o0, o1 = P['outro']
    freeze_end = 'time.freeze' in pm['outro'] and o1 - o0 >= 4
    end = d1 - 1 if freeze_end else d1
    reserved = []
    nbars = (end - d0) // 4
    if ('cut.quick' in pm['drop'] or 'cut.quick' in sig) and nbars >= 3:
        cand = list(range(d0 // 4 + 1, (end // 4) - 1))
        if cand:
            k = max(cand, key=lambda br: float(np.mean(grid.onset[j0 + 4 * br:j0 + 4 * br + 4])))
            reserved.append(('burst', 4 * k, 4 * k + (2 if fast else 4)))
    if 'zoom.crash' in pm['drop'] and nbars >= 2:
        lead = 1 if period >= 0.4 else 2
        for kc in range(d0 // 4 + max(1, nbars // 2), end // 4):
            a_, b_ = 4 * kc - lead, 4 * kc + 2
            if b_ <= end and a_ > d0 and all(b_ <= r[1] or a_ >= r[2] for r in reserved):
                reserved.append(('crash', a_, b_))
                break
    reserved.sort(key=lambda r: r[1])
    L, target = _lens_from_card(g, 'drop', period)
    x, first = d0, True
    for kind, a_, b_ in reserved + [('end', end, end)]:
        if a_ > x:
            for u, v in tile(x, a_, L, target, grid, j0, rng):
                S.append(_slot('drop', 'drop_first' if first else 'drop', u, v))
                first = False
        if kind == 'burst':
            S += [_slot('drop', 'burst', a_ + 0.5 * k, a_ + 0.5 * (k + 1), kind='burst') for k in range(int((b_ - a_) / 0.5))]
        elif kind == 'crash':
            S.append(_slot('drop', 'crash', a_, b_, crash=True))
        x = max(x, b_)
    drop = [s for s in S if s['part'] == 'drop' and s['kind'] == 'shot' and s['role'] != 'crash']
    if drop:
        if 'time.slow_motion' in pm['drop'] or 'time.slow_motion' in sig:
            drop[0]['speed'] = dict(mode='slow', rate=0.5)
        elif 'time.velocity' in pm['drop']:
            for s_ in drop:
                s_['speed'] = dict(mode='velocity')
        if 'time.speed_ramp' in pm['drop'] or 'time.speed_ramp' in sig:
            used_bars = set()
            for s_ in drop[1:]:
                if s_['speed']['mode'] == 'normal' and s_['b1'] - s_['b0'] >= 2 and int(s_['b0'] // 4) not in used_bars and len(used_bars) < 2:
                    s_['speed'] = dict(mode='ramp', fast=2.2, slow=0.35)
                    used_bars.add(int(s_['b0'] // 4))
    if o1 > o0:
        if freeze_end:
            S.append(_slot('outro', 'freeze', end, o1, kind='freeze', speed=dict(mode='ramp_freeze', ramp_beats=1.0, hold_beats=o1 - o0)))
        else:
            S += _tile_part(g, P, 'outro', grid, j0, period, rng, 'outro')
    S.sort(key=lambda s: s['b0'])
    return S


def tile_exact(b0, b1, k, grid, j0, unit=None):
    """Exactly k shots over window beats [b0, b1) (b1 may be fractional: the window end). DP over the beat
    (or half-beat) grid: equal lengths first, then cuts on downbeats and strong onsets."""
    if k <= 0 or b1 - b0 <= 1e-6:
        return []
    if k == 1:
        return [(float(b0), float(b1))]
    target = (b1 - b0) / k
    unit = unit or (1.0 if target >= 1.5 else 0.5)
    pos = [b0 + i * unit for i in range(int(math.floor((b1 - b0) / unit + 1e-6)) + 1)]
    if b1 - pos[-1] > 1e-6:
        pos.append(b1)
    else:
        pos[-1] = b1
    N = len(pos) - 1
    if N < k:                                       # too short for k shots on this grid: halve the unit
        return tile_exact(b0, b1, k, grid, j0, unit / 2) if unit > 0.25 else \
            [(b0 + i * (b1 - b0) / k, b0 + (i + 1) * (b1 - b0) / k) for i in range(k)]

    def cut_cost(i):
        if i == N:
            return 0.0
        p_ = pos[i]
        if abs(p_ - round(p_)) > 1e-6:
            jb = j0 + int(math.floor(p_))
            hs = float(grid.half[jb]) if 0 <= jb < len(grid.half) else 0.0
            return 0.6 + 0.4 * (1.0 - min(1.0, hs))
        jj = j0 + int(round(p_))
        if not (0 <= jj < len(grid.t)):
            return 0.5
        c = 0.4 * (1.0 - min(1.0, float(max(grid.kick[jj], grid.onset[jj]))))
        return c + (0.0 if grid.is_down(jj) else 0.35)
    INF = 1e18
    cost = [[INF] * (N + 1) for _ in range(k + 1)]
    prev = [[-1] * (N + 1) for _ in range(k + 1)]
    cost[0][0] = 0.0
    lo, hi = 0.34 * target, 3.0 * target
    for c in range(1, k + 1):
        for j in range(1, N + 1):
            cc = cut_cost(j)
            for i in range(j - 1, -1, -1):
                L = pos[j] - pos[i]
                if L > hi:
                    break
                if L < lo - 1e-9 or cost[c - 1][i] >= INF:
                    continue
                v = cost[c - 1][i] + 2.0 * ((L - target) / target) ** 2 + cc
                if v < cost[c][j]:
                    cost[c][j], prev[c][j] = v, i
    if cost[k][N] >= INF:
        return [(b0 + i * (b1 - b0) / k, b0 + (i + 1) * (b1 - b0) / k) for i in range(k)]
    out, j = [], N
    for c in range(k, 0, -1):
        i = prev[c][j]
        out.append((pos[i], pos[j]))
        j = i
    return out[::-1]


def slots_n(n, parts, grid, win, g):
    """Exactly n shots over the window (the user's / sequence's shot count): a cut always lands on the drop beat,
    shots before / after it in proportion to the time, lengths as even as the beat grid allows (one bar per shot
    when n divides the bars)."""
    j0 = win['j0']
    nb = float(win.get('n_beats') or (win['j1'] - win['j0']))
    jd = parts['drop']['beat0'] if parts['drop']['beat1'] > parts['drop']['beat0'] else None
    regions = []
    if jd is not None and 0 < jd < nb - 0.5 and n >= 2:
        n1 = int(min(n - 1, max(1, round(n * jd / nb))))
        regions = [(0.0, float(jd), n1), (float(jd), nb, n - n1)]
    else:
        regions = [(0.0, nb, n)]
    S = []
    for a, b, k in regions:
        for x, y in tile_exact(a, b, k, grid, j0):
            part = next((p for p in PARTS if parts[p]['beat0'] - 1e-6 <= x < parts[p]['beat1'] - 1e-6), 'outro' if x > 0 else 'hook')
            S.append(_slot(part, part, x, y))
    for s in S:
        if jd is not None and abs(s['b0'] - jd) < 1e-6:
            s['role'] = 'drop_first'
    if S and S[0]['role'] == 'drop' and not any(s['role'] == 'drop_first' for s in S):
        S[0]['role'] = 'drop_first'
    return S


def apply_cut_rate(slots, rate, grid, j0, g):
    """The user's cutting-rate multiplier on any recipe: rate > 1 splits plain shots at beats (strongest onsets
    nearest the even split), rate < 1 merges neighbouring plain shots of one part. Hero, burst, stutter, crash,
    freeze, black and speed-changed slots keep their length."""
    if abs(rate - 1.0) < 0.05:
        return slots
    plain = lambda s: (s['kind'] == 'shot' and s['speed']['mode'] == 'normal' and s['role'] not in ('drop_first', 'crash', 'freeze')
                       and not s.get('crash') and not s.get('dip'))   # noqa: E731
    min_len = 0.5 if min(v[0] for v in g['rhythm']['shot_len_s'].values()) < 0.5 else 1.0
    out = [dict(s) for s in slots]
    n_plain = sum(1 for s in out if plain(s))
    if not n_plain:
        return out
    goal = max(1, int(round(n_plain * rate)))
    if rate > 1:
        while sum(1 for s in out if plain(s)) < goal:
            cand = [i for i, s in enumerate(out) if plain(s) and s['b1'] - s['b0'] >= 2 * min_len - 1e-6]
            if not cand:
                break
            i = max(cand, key=lambda i: (out[i]['b1'] - out[i]['b0'], -i))
            s = out[i]
            halves = tile_exact(s['b0'], s['b1'], 2, grid, j0, unit=min_len)
            out[i:i + 1] = [dict(s, b0=x, b1=y, speed=dict(s['speed'])) for x, y in halves]
        return out
    max_b = g['rhythm'].get('max_shot_s', 4) * 1.5 / REF_BEAT
    while sum(1 for s in out if plain(s)) > goal:
        pairs = [i for i in range(len(out) - 1) if plain(out[i]) and plain(out[i + 1]) and out[i]['part'] == out[i + 1]['part']
                 and out[i + 1]['b1'] - out[i]['b0'] <= max_b + 1e-6]
        if not pairs:
            break
        i = min(pairs, key=lambda i: (out[i + 1]['b1'] - out[i]['b0'], i))
        out[i:i + 2] = [dict(out[i], b1=out[i + 1]['b1'])]
    return out


def ramp_speed(slot_beats, period, last=False, src_fps=25.0, require=False):
    """time.speed_ramp parameters for a slot (card: fast 2-5, brake 3-8 frames into 0.2-0.4 at the action peak on
    a beat, slow hold 0.4-1.5 s, speed-up 3-6 frames into the next cut). Shots of >= 3 beats get the exit ramp
    (fast-slow-fast); the last shot of a run brakes and stays slow. The plan then gives every ramp its own curve
    (_ramp_patterns) above the slow floor (slow_floor: 0.4x from < 50 fps sources)."""
    slow = slow_floor(src_fps)
    sp = dict(mode='ramp', fast=2.4, slow=slow, at_beat=1.0, required=bool(require))
    if slot_beats >= 3 and not last:
        sp.update(exit_beat=slot_beats - 1.0, fast_out=2.6)
    return sp


# ---------------------------------------------------------------------------- speed curves
def speed_times(slot, fps, beat_rel, rbar=2.5, m=0.85, ease='inOutCubic'):
    """Source time offsets (s, from the window start) for every output frame of the slot.
    normal / slow(rate) / velocity (time.velocity: s = a_i + r̄·T·[(1−m)u + m·E(u)] per beat cycle, anchors on beats) /
    ramp (time.speed_ramp: fast -> slow at a beat) / ramp_freeze (rate 1 -> 0.2 then hold) / stutter (1/16 loop) /
    freeze."""
    n = slot['f1'] - slot['f0'] + 1
    sp = slot['speed']
    mode = sp['mode']
    k = np.arange(n) / fps
    if mode == 'normal':
        return k
    if mode == 'slow':
        return k * sp['rate']
    if mode == 'freeze':
        return np.zeros(n)
    if mode == 'velocity':
        dur = n / fps
        cyc = [0.0] + [b for b in beat_rel if 1e-3 < b < dur - 1e-3] + [dur]
        out = np.zeros(n)
        a = 0.0
        for c0, c1 in zip(cyc[:-1], cyc[1:]):
            T = c1 - c0
            sel = (k >= c0 - 1e-9) & (k < c1 - 1e-9)
            u = (k[sel] - c0) / T
            E = np.array([_ease(x, ease) for x in u])
            out[sel] = a + rbar * T * ((1 - m) * u + m * E)
            a += rbar * T
        return out
    if mode == 'ramp':
        tb = sp.get('at') or (beat_rel[0] if beat_rel else n / fps / 2)     # slow motion starts on this beat
        fast, slow = sp.get('fast', 2.2), sp.get('slow', 0.35)
        dec = sp.get('dec_frames', 5) / fps                                 # braking 5 frames, inOutCubic
        rates = np.where(k < tb - dec, fast, np.where(k >= tb, slow, 0.0)).astype(float)
        mid = (k >= tb - dec) & (k < tb)
        rates[mid] = fast + (slow - fast) * np.array([_ease((x - (tb - dec)) / dec, 'inOutCubic') for x in k[mid]])
        te = sp.get('exit')                                                  # speed-up into the next cut (fast-slow-fast)
        if te is not None and te > tb:
            acc = sp.get('acc_frames', 5) / fps
            fo = sp.get('fast_out', fast)
            up = (k >= te) & (k < te + acc)
            rates[up] = slow + (fo - slow) * np.array([_ease((x - te) / acc, 'inCubic') for x in k[up]])
            rates[k >= te + acc] = fo
        return np.concatenate([[0.0], np.cumsum(rates[:-1]) / fps])
    if mode == 'ramp_freeze':
        tr = sp.get('ramp_beats', 1.0) * (beat_rel[1] - beat_rel[0] if len(beat_rel) > 1 else 0.5)
        rates = np.where(k < tr, 1.0 - 0.8 * np.array([_ease(x / max(tr, 1e-6), 'inCubic') for x in k]), 0.0)
        return np.concatenate([[0.0], np.cumsum(rates[:-1]) / fps])
    if mode == 'stutter':
        frag = max(2, int(round(sp.get('frag_s', 0.125) * fps)))
        return (np.arange(n) % frag) / fps
    raise ValueError(mode)


# ============================================================================ 4. selection profiles ("Shot selection")
def _face_ok(W, h_min=0.0, luma_min=45):
    """a detected face that reads on screen: present in ≥ 30 % of samples, big enough, and lit (not a black hood)."""
    return (W['face_h'] or 0) >= h_min and W['face_share'] >= 0.3 and (W.get('face_luma') or 0) >= luma_min


def _hero(W):
    if _face_ok(W):
        return 1.0
    p = W['person']
    return _band(p, 0.05, 0.40, 0.1) if p is not None else 0.0


def score_window(slug, role, W, slot, prog):
    """Genre-specific score of a source window for a slot role. Returns (score, tags). `prog` = position 0..1 inside
    the part (build ladders). Terms follow each card's "Shot selection" (ranks are percentiles over the user's footage)."""
    tags = []
    s = 0.0
    face_big = _face_ok(W, 0.25, 40)
    if W['luma_c'] < 12:
        s -= 1.5
        tags.append('too dark')
    elif W['luma_c_min'] < (30 if slug == 'phonk' else 14) and slug != 'calm':
        s -= 1.2 if W['luma_c_min'] < 20 else 0.8           # the window passes through near-black: unplanned black frames (QA)
        tags.append('dips into black')
    if W['face_spread'] > 0.4:
        s -= 0.3                                            # two faces far apart: 9:16 crop cuts one of them
    if W['sharp_r'] < 0.1 and W['contrast_r'] < 0.2 and W['motion_r'] < 0.15:
        s -= 1.0                                            # featureless: flat, soft, nothing happens
        tags.append('flat and soft')
    if W['jitter'] > 2.0 and slug not in ('epic', 'calm'):
        s -= 0.4 * min(3.0, W['jitter'] - 1.0)              # handheld jitter > 2 % reads as a mistake (viral: only after stabilize)
        tags.append(f'jitter {W["jitter"]:.1f} %')
    # readability (all genres): the hero slots need a subject the viewer can read in the 9:16 crop; establishing
    # slots need a real scene; a subject-less texture (fire, fur, snow, blur) only as a passing cutaway
    subj = W.get('subject')
    wide_role = role in ('hook2', 'drop_wide', 'outro', 'outro2') or (role == 'hook' and slug in ('epic', 'calm', 'travel')) \
        or (slug == 'calm' and role in ('drop_first', 'drop'))
    if role in ('drop_first', 'freeze', 'crash') or (role == 'hook' and not wide_role):
        s += 1.2 * W.get('readable', 0.5)
        if subj == 'texture':
            s -= 1.0
            tags.append('no readable subject')
    elif wide_role and subj == 'texture':
        s -= 1.5
        tags.append('texture, not a scene')
    if wide_role:                                           # an establishing / closing shot needs light and a readable image
        s += 0.6 * W.get('readable', 0.5) - (0.8 if W['luma_c'] < 45 else 0.0)
    elif subj == 'texture' and role in ('drop', 'build', 'outro', 'hook2'):
        s -= 0.35
    if slug == 'phonk':
        s += 0.6 * _band(W['luma_c'], 35, 120, 40) + 0.3 * W['contrast_r'] - 0.15 * W['sat_r']
        if W['luma_c'] < 34:
            s -= 1.2                                     # the teal grade (gamma 1.15, black .05) crushes it: card QA wants 40–90
            tags.append('darker than 34 — goes to black after the grade')
        if W['luma_c'] > 170 and W['contrast_r'] < 0.45:
            s -= 2.5
            tags.append('bright and flat — not phonk')
        if role == 'hook':
            face = (1.0 - W['motion_r']) if face_big else 0.0
            sil = 1.0 if W['low_angle'] else (0.7 if (W['person'] or 0) > 0.05 and W['luma'] < 70 and W['contrast_r'] > 0.6 else 0.0)
            act = W['peak_r']
            best = max(face, sil, act)
            s += 1.4 * best + 0.3 * W['sharp_r']
            tags.append({face: 'face to camera', sil: 'silhouette / low angle', act: 'action peak'}[best])
        elif role == 'build':
            s += 1.0 * _band(W['motion_r'], 0.2, 0.6, 0.25) + 0.3 * W['sharp_r'] + 0.2 * (W['size'] in ('medium', 'wide', 'wide/no-face'))
        elif role in ('drop', 'drop_first'):
            s += 1.3 * W['motion_r'] + 0.4 * min(1.0, W['peaks_per_s']) + 0.3 * W['sharp0_r'] + (0.5 * W['peak_r'] if role == 'drop_first' else 0)
            if face_big:
                s -= 0.5
                tags.append('big face in velocity — smeared')
        elif role == 'burst':
            s += 0.9 * W['peak_r'] + 0.3 * (W['size'] in ('extreme-close', 'close')) + 0.3 * W['sharp_r']
        elif role == 'crash':                                # zoom.crash "into a face or a detail": needs a readable target
            face = _face_ok(W, 0.1, 50)
            s += 1.2 * face + 0.5 * W['sharp_r'] + 0.6 * _band(W['luma'], 60, 170, 40) + 0.4 * W['contrast_r'] + 0.3 * W['motion_r']
            if not face and (W['face_h'] or 0) >= 0.1:
                s -= 0.6                                     # a face that does not read: the crash would land in darkness
            tags.append('face for the crash zoom' if face else 'detail for the crash zoom')
        elif role == 'freeze':
            s += 1.2 * W['sharpmax_r'] + 0.5 * _face_ok(W, 0.18, 45) + 0.3 * W['contrast_r'] + 0.2 * _hero(W)
        elif role == 'stutter':
            s += 1.0 * W['motion_r'] + 0.3 * W['sharp_r']
    elif slug == 'epic':
        if W['jitter'] > 1.0:
            s -= 2.5
            tags.append('jitter > 1 %')
        s += 0.2 * W['contrast_r']
        calm_cam = 0.5 * _band(W['pan'], 0, 0.5, 0.5) + 0.5 * _band(W['jitter'], 0, 0.3, 0.5)
        if role == 'hook':
            s += 1.5 * W['ews'] + 0.4 * W['sharp_r'] + 0.5 * calm_cam + 0.3 * W['contrast_r'] - 0.8 * ((W['face_h'] or 0) > 0.12)
            tags.append('scale (EWS)' if W['ews'] else 'wide shot')
        elif role == 'hook2':
            s += 0.9 * (W['size'] in ('wide', 'wide/no-face')) + 0.3 * W['sharp_r'] + 0.3 * calm_cam
        elif role == 'build':
            lo, hi = (0.3, 0.6) if prog < 0.5 else (0.6, 0.85)
            s += 1.0 * _band(W['motion_r'], lo, hi, 0.2) + 0.4 * (W['size'] in ('medium', 'close', 'extreme-close')) + 0.3 * W['sharp_r'] \
                + 0.3 * W['low_angle']
            if ((slot or {}).get('speed') or {}).get('mode') == 'slow':
                s += 0.4 * (W['src_fps'] >= 50) + 0.3 * _band(W['peak_pos'], 0.4, 0.7, 0.3)
        elif role == 'drop_first':
            E = 0.40 * W['peak_r'] + 0.25 * W['sharp_r'] + 0.20 * _hero(W) + 0.15 * W['contrast_r']
            s += 2.5 * E + 0.3 * (W['src_fps'] >= 50) + 0.3 * _band(W['peak_pos'], 0.0, 0.3, 0.3)
            tags.append(f'E={E:.2f}')
        elif role == 'drop':
            s += 1.0 * _band(W['motion_r'], 0.75, 1.0, 0.3) + 0.3 * W['sharp_r'] + 0.3 * W['peak_r']
        elif role == 'drop_wide':
            s += 0.9 * (W['size'] in ('wide', 'wide/no-face')) + 0.4 * W['ews'] + 0.3 * _band(W['motion_r'], 0.3, 0.8, 0.3)
        elif role in ('outro', 'outro2'):
            s += 1.0 * (W['size'] in ('wide', 'wide/no-face')) + 0.6 * _band(W['motion_r'], 0, 0.4, 0.3) + 0.4 * calm_cam \
                + 0.3 * W['warm_r']
    elif slug == 'calm':
        if W['jitter'] > 0.5:
            s -= 2.5
            tags.append('jitter > 0.5 %')
        if W['clip'] > 0.02:
            s -= 0.5
        if W['nfaces'] >= 3:
            s -= 0.4
        smooth = 0.5 * _band(W['pan'], 0, 0.25, 0.3) + 0.5 * _band(W['jitter'], 0, 0.1, 0.4)
        if role == 'hook':
            s += 1.0 * W['static'] + 0.8 * _band(W['motion_r'], 0, 0.3, 0.3) + 0.4 * W['sharp_r'] + 0.3 * W['warm_r'] \
                + 0.3 * (W['size'] in ('wide', 'wide/no-face'))
        elif role == 'build':
            s += 0.6 * (W['size'] in ('close', 'extreme-close')) + 0.6 * _band(W['motion_r'], 0.1, 0.5, 0.2) + 0.4 * smooth \
                + 0.3 * W['sharp_r']
        elif role in ('drop_first', 'drop'):
            light = 0.6 * W['warm_r'] + 0.4 * _band(W['contrast'], 0.35, 0.7, 0.25)
            C = 0.35 * light + 0.25 * W['sharp_r'] + 0.25 * (W['size'] in ('wide', 'wide/no-face')) + 0.15 * smooth
            s += (2.0 if role == 'drop_first' else 1.0) * C + 0.5 * _band(W['motion_r'], 0.2, 0.6, 0.25)
            tags.append(f'C={C:.2f}')
        elif role in ('outro', 'outro2'):
            s += 1.0 * (W['size'] in ('wide', 'wide/no-face')) + 0.8 * _band(W['motion_r'], 0, 0.3, 0.3) + 0.3 * smooth
    else:                                                    # generic profile for the other music genres
        if W['jitter'] > 2.0:
            s -= 1.0
        if role == 'hook':
            if slug in ('drama', 'fanedit'):
                s += 1.0 * face_big + 0.4 * W['sharp_r'] + 0.3 * (1 - W['motion_r'])
            elif slug in ('travel',):
                s += 0.8 * W['sat_r'] + 0.6 * (W['size'] in ('wide', 'wide/no-face')) + 0.4 * W['sharp_r']
            elif slug == 'teaser':
                s += 0.8 * (1 - W['luma_r']) + 0.6 * (W['size'] in ('extreme-close',)) + 0.3 * W['sharp_r']
            else:
                s += 0.4 * W['motion_r'] + 0.3 * _face_ok(W, 0.18, 45) + 0.3 * W['sharp_r'] + 0.3 * _band(W['peak_pos'], 0, 0.3, 0.3)
        elif role == 'build':
            s += 1.0 * _band(W['motion_r'], 0.3, 0.7, 0.25) + 0.3 * W['sharp_r']
        elif role == 'drop_first':
            s += 1.5 * (0.5 * W['peak_r'] + 0.3 * W['sharp_r'] + 0.2 * _hero(W))
        elif role == 'drop':
            s += 1.0 * _band(W['motion_r'], 0.6, 1.0, 0.3) + 0.3 * W['sharp0_r']
        elif role == 'burst':                                # 1/8 cuts: the motion has to read in 7 frames
            s += 0.9 * W['peak_r'] + 0.4 * W['motion_r'] + 0.3 * W['sharp_r']
        elif role == 'crash':                                # a face or a detail to land in
            s += 1.0 * _face_ok(W, 0.1, 50) + 0.5 * W['sharp_r'] + 0.4 * W['contrast_r'] + 0.3 * W['motion_r']
        elif role == 'freeze':                               # the sharpest peak frame, a face when there is one
            s += 1.2 * W['sharpmax_r'] + 0.5 * _face_ok(W, 0.18, 45) + 0.3 * W['contrast_r']
        else:
            s += 0.6 * _band(W['motion_r'], 0, 0.5, 0.3) + 0.4 * W['sharp_r']
    return s, tags


ROLE_PRIORITY = {'drop_first': 0, 'hook': 1, 'freeze': 2, 'outro': 3, 'crash': 4, 'drop': 4, 'hook2': 5, 'drop_wide': 6, 'outro2': 7,
                 'build': 8, 'stutter': 9, 'burst': 10}


def _assign_bursts(slots, F, g, ctx):
    """cut.quick bursts as two angles of one moment instead of eight unrelated shots: a run of burst slots
    alternates between the two best long-enough shots (different sources, not used elsewhere), each one running on
    in real time under the cuts (multicam feel). Leaves the run to the per-slot assignment when no two shots fit."""
    runs, cur = [], []
    for s in slots:
        if s['role'] == 'burst' and not s.get('pick'):
            if cur and s['i'] != cur[-1]['i'] + 1:
                runs.append(cur)
                cur = []
            cur.append(s)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    used_dups = {F.shot(s['pick']['shot'])['dup'] for s in slots if s.get('pick')}
    used_rng = [(s['pick']['ci'], s['pick']['w0'], s['pick']['w1']) for s in slots if s.get('pick')]
    for run in runs:
        t0 = run[0]['t0']
        need = (run[-1]['t1'] - t0) + 0.1
        cands = []
        for sh in F.shots:
            lo, hi = sh['t0'] + 0.12, sh['t1'] - 0.12 - need
            if hi < lo:
                continue
            for w0 in sorted({round(lo, 3), round((lo + hi) / 2, 3), round(hi, 3)} | {round(p[0] - 0.1, 3) for p in sh['peaks'] if lo <= p[0] - 0.1 <= hi}):
                if any(ci == sh['ci'] and w0 < b + 0.3 and w0 + need > a - 0.3 for ci, a, b in used_rng):
                    continue
                if any(ci == sh['ci'] and w0 < b - 0.05 and w0 + need > a + 0.05 for ci, a, b in ctx.get('banned', ())):
                    continue
                W = F.win(sh, w0, w0 + need)
                sc, _ = score_window(g['slug'], 'burst', W, run[0], 0.5)
                sc += 0.5 * W.get('readable', 0.5) - (1.0 if sh['dup'] in used_dups else 0.0)
                if ctx.get('noise') is not None:
                    sc += ctx['noise'](run[0], sh, w0)
                sc -= 0.3 * sum(1 for _, ashot, _ in ctx.get('avoid_win') or () if ashot == sh['id'])
                cands.append((sc, sh, w0, W))
        cands.sort(key=lambda x: -x[0])
        if not cands:
            continue
        # the second angle of the same moment: a different shot of similar brightness (dark / bright alternating
        # every half beat reads as flicker and counts as flashes)
        first, second, best = cands[0], None, None
        L0 = max(first[3]['luma_c'], 1.0)
        for c in cands[1:]:
            if c[1]['dup'] == first[1]['dup']:
                continue
            v = c[0] - 1.2 * abs(math.log2(max(c[3]['luma_c'], 1.0) / L0))
            if best is None or v > best:
                best, second = v, c
        if second is None:
            continue
        picks = [first, second]
        for k, s in enumerate(run):
            sc, sh, w0, W = picks[k % 2]
            sw0 = w0 + (s['t0'] - t0)
            s['pick'] = dict(shot=sh['id'], ci=sh['ci'], src=sh['src'], w0=round(sw0, 3), w1=round(sw0 + s['src_need'], 3),
                             score=round(sc, 3), W=F.win(sh, sw0, sw0 + s['src_need']), tags=['burst: two angles alternate, real time'],
                             n_cands=len(cands), alts=[])
        used_dups |= {p[1]["dup"] for p in picks}
        used_rng += [(p[1]["ci"], p[2], p[2] + need) for p in picks]


def assign(slots, F, g, ctx, log=print):
    """Greedy assignment by slot importance with relaxation levels (repeat limits, adjacency). ctx['given']
    {slot i: clip index} pins slots to clips (order='given'); the window inside the clip is still scored."""
    slug = g['slug']
    given = ctx.get('given') or {}
    group_bursts = not given and not ctx.get('_bursts_done')
    order = sorted([s for s in slots if s['kind'] != 'black' and not s.get('pick') and not (group_bursts and s['role'] == 'burst')],
                   key=lambda s: (ROLE_PRIORITY.get(s['role'], 9), -ctx['beat_db_of'](s), s['b0']))
    used = [dict(ci=s['pick']['ci'], dup=F.shot(s['pick']['shot'])['dup'], w0=s['pick']['w0'], w1=s['pick']['w1'], i=s['i'],
                 t_out=s['t0']) for s in slots if s.get('pick')]
    n_need = sum(1 for s in slots if s['kind'] != 'black')
    # one use per source shot while the footage allows it (repeats read as filler); viral loops and long videos 2-3
    max_uses = 3 if (slug == 'viral' and ctx['T'] > 20) else (1 if len(F.shots) >= 1.2 * n_need and ctx['T'] <= 40 else 2)
    by_i = {s['i']: s for s in slots}
    for s in order:
        need, h_in, h_out = s['src_need'], s.get('handle_in', 0.0), s.get('handle_out', 0.0)
        cands = F.candidates(need, h_in, h_out, s.get('accent_offsets', ()))
        pin = given.get(s['i'])
        if pin is not None:
            cands = [c for c in cands if c[0]['ci'] == pin]
        part = ctx['parts'][s['part']]
        prog = (s['b0'] - part['beat0']) / max(1.0, part['beat1'] - part['beat0'])
        best = None
        scored = []
        for relax in (0, 1, 2, 3):
            scored = []
            for sh, w0, aligned in cands:
                w1 = w0 + need
                bad = False
                n_same = 0
                overlap = 0
                for u in used:
                    if u['ci'] == sh['ci'] and w0 - h_in < u['w1'] + 0.5 and w1 + h_out > u['w0'] - 0.5:
                        if relax < 3 or abs(u['i'] - s['i']) <= 1:
                            bad = True              # level 3 (too little footage): reuse a range, never next to itself
                            break
                        overlap += 1
                    if u['dup'] == sh['dup'] and pin is None:
                        n_same += 1
                        if relax < 2 and abs(u['i'] - s['i']) == 1:
                            bad = True
                            break
                        if relax < 1 and slug in ('epic', 'calm') and abs(u['t_out'] - s['t0']) < 8.0:
                            bad = True
                            break
                if not bad and any(ci == sh['ci'] and w0 < b1 - 0.05 and w1 > b0 + 0.05 for ci, b0, b1 in ctx.get('banned', ())):
                    bad = True                  # goes near-black under the grade (_dark_check)
                if bad or (relax < 2 and n_same >= max_uses + relax):
                    continue
                W = F.win(sh, w0, w1)
                sc, tags = score_window(slug, s['role'], W, s, prog)
                if aligned:
                    sc += 0.25 * W['peak_r']
                    tags = tags + ['peak on the accent']
                if s['speed']['mode'] in ('ramp', 'ramp_freeze'):
                    # a ramp brakes on an action peak: real motion and a peak at the braking point, never a static shot
                    sc += 0.8 * W['peak_r'] + 0.5 * W['motion_r'] + 0.4 * W['sharp_r'] + (0.4 if aligned else 0.0)   # slow motion shows blur
                    if W['motion_r'] < 0.3:
                        sc -= 1.2
                        tags = tags + ['static for a ramp']
                sc += 0.3 * (W.get('weight', 1.0) - 1.0)
                if W.get('role') == 'hero' and s['role'] in ('drop_first', 'hook', 'freeze', 'crash'):
                    sc += 1.0                    # the user's hero clip goes to the hero slots
                elif W.get('role') == 'broll' and s['role'] in ('drop_first', 'hook'):
                    sc -= 0.3
                sc -= 0.8 * n_same + 2.0 * overlap
                if overlap:
                    tags = tags + ['reused range']
                if s['kind'] != 'burst':               # a hard cut must read: not the same framing / light as a neighbour
                    sim = 0.0
                    for nb, t_mine, end in ((s['i'] - 1, w0 + 0.05, True), (s['i'] + 1, w1 - 0.05, False)):
                        o = by_i.get(nb)
                        if o is None or not o.get('pick') or o['kind'] == 'burst':
                            continue
                        opk = o['pick']
                        sim = max(sim, F.similarity(sh['ci'], t_mine, opk['ci'], (opk['w1'] - 0.05) if end else (opk['w0'] + 0.05),
                                                    W.get('crop_cx'), opk['W'].get('crop_cx')))
                    if sim > 0.7:
                        sc -= 2.0 * (sim - 0.7) / 0.3
                        tags = tags + [f'looks like its neighbour ({sim:.2f})']
                    # ... and a cut reads against the shots' own motion: an edge in the footage's busiest motion
                    # (top ~15 %) blurs the cut (and a transition laid on it); the peak belongs inside the window
                    busy = (max(0.0, W.get('edge_in_r', 0.0) - 0.85) if by_i.get(s['i'] - 1) is not None else 0.0) + \
                        (max(0.0, W.get('edge_out_r', 0.0) - 0.85) if by_i.get(s['i'] + 1) is not None else 0.0)
                    if busy > 0:
                        sc -= (2.0 if s['speed']['mode'] in ('ramp', 'ramp_freeze', 'velocity') else 5.0) * busy
                        tags = tags + ['busy at the cut']
                nz = ctx.get('noise')
                if nz is not None:
                    sc += nz(s, sh, w0)                  # another version: close calls go another way
                for ai, ashot, aw0 in ctx.get('avoid_win') or ():
                    if ashot == sh['id']:
                        same_slot = ai == s['i'] and (aw0 is None or abs(aw0 - w0) < need + 0.5)
                        sc -= 0.9 if same_slot else 0.2  # an earlier version used this shot (here)
                for nb in (s['i'] - 1, s['i'] + 1):
                    o = by_i.get(nb)
                    if o is None or o.get('pick') is None:
                        continue
                    OW = o['pick']['W']
                    if OW['size'] == W['size']:
                        sc -= 0.6 if (slug == 'epic' and s['part'] == 'drop') else 0.25
                    if slug == 'calm' and OW['luma'] > 0 and abs(math.log(max(W['luma'], 1) / max(OW['luma'], 1))) > math.log(1.5):
                        sc -= 0.8
                    if slug == 'epic' and s['part'] in ('build', 'drop') and nb == s['i'] - 1:
                        if abs(OW['tx_end']) > 0.004 and np.sign(OW['tx_end']) == np.sign(W['tx_start']):
                            sc += 0.3                    # cut.vector_match: same direction across the seam
                scored.append((sc, sh, w0, W, tags))
            if scored:
                break
        if not scored:
            s['pick'] = None
            ctx['notes'].append(f'slot {s["i"]} ({s["role"]}): no suitable window in the source footage')
            continue
        scored.sort(key=lambda x: -x[0])
        sc, sh, w0, W, tags = scored[0]
        s['pick'] = dict(shot=sh['id'], ci=sh['ci'], src=sh['src'], w0=round(w0, 3), w1=round(w0 + need, 3), score=round(sc, 3), W=W,
                         tags=tags, n_cands=len(scored),
                         alts=[dict(shot=x[1]['id'], w0=round(x[2], 3), score=round(x[0], 3)) for x in scored[1:4]])
        used.append(dict(ci=sh['ci'], dup=sh['dup'], w0=w0, w1=w0 + need, i=s['i'], t_out=s['t0']))
    if group_bursts:                    # bursts last (lowest priority), as alternating angles; leftovers one by one
        _assign_bursts(slots, F, g, ctx)
        if any(s['role'] == 'burst' and not s.get('pick') for s in slots):
            assign(slots, F, g, dict(ctx, _bursts_done=True), log)
    return slots


def _loop_end(g, slots, F, ctx):
    """viral "loop ending" (card "Shot selection" 5): the last shot is the same source shot as the first one and ends
    exactly where the first begins, so the end flows into frame 0 when the video loops."""
    if 'loop.end' not in g['part_moves'].get('outro', []):
        return
    first = next((s for s in slots if s.get('pick')), None)
    last = next((s for s in reversed(slots) if s.get('pick') and s['kind'] == 'shot'), None)
    if not first or not last or first is last or last['speed']['mode'] != 'normal':
        return
    sh = F.shot(first['pick']['shot'])
    w1 = first['pick']['w0']
    w0 = w1 - last['src_need']
    if w0 < sh['t0'] + 0.05:
        ctx['notes'].append('loop.end: the first shot has no footage before its start — the loop is not closed')
        return
    for s in slots:
        pk = s.get('pick')
        if s is not last and s is not first and pk and pk['ci'] == sh['ci'] and w0 < pk['w1'] and w1 > pk['w0']:
            return
    W = F.win(sh, w0, w1)
    last['pick'] = dict(last['pick'], shot=sh['id'], ci=sh['ci'], src=sh['src'], w0=round(w0, 3), w1=round(w1, 3), W=W,
                        tags=['loop: the hook shot up to its start'], alts=last['pick'].get('alts', []))
    last['loop_end'] = True


def _match_burst_exposure(segs, by_seg):
    """The two angles of a burst alternate every half beat: unequal brightness reads as flicker (and the QA counts it
    as flashes). Each source of a burst run gets one exposure, pulled to the run's common graded luma (geometric
    mean of the sources), at most 0.3 EV brighter than the per-shot exposure allowed (highlights)."""
    k = 0
    while k < len(segs):
        if (by_seg.get(k) or {}).get('role') != 'burst':
            k += 1
            continue
        j = k
        while j < len(segs) and (by_seg.get(j) or {}).get('role') == 'burst':
            j += 1
        run = [i for i in range(k, j) if segs[i].get('_crop_luma')]
        lum = {}
        for i in run:
            lum.setdefault(segs[i]['src'], []).append((float(segs[i]['_crop_luma']), float(segs[i]['grade'].get('exposure', 0.0))))
        if len(run) >= 2:
            graded = {src: float(np.median([l * 2 ** e for l, e in v])) for src, v in lum.items()}
            target = float(np.exp(np.mean(np.log([max(x, 1.0) for x in graded.values()]))))
            for src, v in lum.items():
                base = float(np.median([l for l, _ in v]))
                ev = max(-0.8, min(max(e for _, e in v) + 0.3, math.log2(target / max(base, 1.0))))
                for i in run:
                    if segs[i]['src'] == src:
                        if abs(ev) >= 0.05:
                            segs[i]['grade']['exposure'] = round(ev, 2)
                        else:
                            segs[i]['grade'].pop('exposure', None)
        k = j


def _even_rect(r, info):
    """A decode crop on even pixel bounds inside the picture: ffmpeg's exact crop at odd offsets misplaces the chroma
    planes of 4:2:0 sources (10-bit HEVC turns into false colour)."""
    W0, H0 = int(info.get('w') or 1 << 15), int(info.get('h') or 1 << 15)
    x0, y0 = max(0, int(math.floor(r[0] / 2.0)) * 2), max(0, int(math.floor(r[1] / 2.0)) * 2)
    x1, y1 = min(W0 - W0 % 2, int(math.ceil(r[2] / 2.0)) * 2), min(H0 - H0 % 2, int(math.ceil(r[3] / 2.0)) * 2)
    return [x0, y0, max(x0 + 2, x1), max(y0 + 2, y1)]


def _graded_luma(fr, slug, ev=0.0):
    """Luma (0..1) of uint8 RGB frames after the genre grade the renderer applies (ed_edl.apply_grade when present;
    otherwise gamma / contrast / black point / gain only)."""
    g = dict(GRADES.get(slug, dict(preset='color')))
    if ev:
        g['exposure'] = ev
    x = fr.astype(np.float32) / 255.0
    try:
        import ed_edl as E
        ag, gs = getattr(E, 'apply_grade', None), getattr(E, 'grade_stats', None)
    except Exception:
        ag = gs = None
    if ag is not None:
        try:
            st = gs(list(x[::max(1, len(x) // 6)]), skip_black=True) if gs is not None else None
            y = np.stack([ag(f, g, st) for f in x])
            return y[..., 0] * 0.2126 + y[..., 1] * 0.7152 + y[..., 2] * 0.0722
        except Exception:
            pass
    L = (x[..., 0] * 0.2126 + x[..., 1] * 0.7152 + x[..., 2] * 0.0722) * 2.0 ** ev
    L = np.clip(L, 0, 1) ** g.get('gamma', 1.0)
    L = np.clip((L - 0.5) * g.get('contrast', 1.0) + 0.5, 0, 1)
    b = g.get('black', 0.0)
    return np.clip((L - b) / (1 - b), 0, 1) * g.get('gain', 1.0)


def _dark_check(slots, F, g, ctx, fps, log=None):
    """Real-frame check of the chosen windows whose 6 fps analysis dips dark (a whip pan through shadow lasts 2-3
    frames and falls between samples): decode the shown span at the source rate (small, the subject band only),
    apply the genre grade and count near-black frames (>= 95 % of the band <= 0.08 after the grade, the QA's black
    test). A window with >= 2 such frames is banned (ctx['banned']; the whole source shot when it is mostly black)
    and its slot cleared for re-assignment. Returns the cleared slots."""
    crush = g['slug'] in GRADES and (GRADES[g['slug']].get('contrast', 1.0) >= 1.25 or GRADES[g['slug']].get('black', 0) >= 0.04)
    cleared = []
    for s in slots:
        pk = s.get('pick')
        if s['kind'] == 'black' or not pk or s.get('gap') or s.get('_dark_ok'):
            continue
        W = pk['W']
        if W['luma_c_min'] >= (45 if crush else 30) and W.get('luma_mid_min', 255) >= (32 if crush else 22):
            continue
        clip = F.clips[pk['ci']]
        info = clip['info']
        bx = clip.get('box') or [0, 0, info.get('w') or 16, info.get('h') or 9]
        bw, bh = bx[2] - bx[0], bx[3] - bx[1]
        ww = min(1.0, (9 / 16) / (bw / max(1, bh)))
        cx = W.get('crop_cx', 0.5)
        x0, x1 = bx[0] + max(0.0, cx - 0.4 * ww) * bw, bx[0] + min(1.0, cx + 0.4 * ww) * bw
        times = pk['w0'] + s['_times']
        t0, t1 = float(times.min()), float(times.max()) + 1.0 / max(1.0, float(info.get('fps') or 25.0))
        try:
            frs = [fr for _, fr in V.frames(clip['path'], t0=t0, t1=t1, width=48, crop=_even_rect([x0, bx[1] + 0.12 * bh, x1, bx[1] + 0.88 * bh], info),
                                            info=info)]
        except Exception:
            continue
        if not frs:
            continue
        L = _graded_luma(np.stack(frs), g['slug'], exposure_ev(g['slug'], W['luma_c'], W.get('p99'),
                                                               W.get('face_luma') if (W.get('face_share') or 0) >= 0.3 else None))
        dark = (L <= 0.08).reshape(len(L), -1).mean(1) >= 0.95
        run = best = 0
        for d in dark:
            run = run + 1 if d else 0
            best = max(best, run)
        if best >= 2:
            sh = F.shot(pk['shot'])
            # mostly black: the whole source shot is out; a short dip: only this window
            ctx.setdefault('banned', []).append((pk['ci'], sh['t0'], sh['t1']) if dark.mean() >= 0.5 else (pk['ci'], pk['w0'], pk['w1']))
            ctx['notes'].append(f"slot {s['i']} ({s['role']}): {pk['shot']} {pk['w0']:.2f}–{pk['w1']:.2f} s goes near-black for "
                                f"{best} frames under the grade — re-picked")
            s['pick'] = None
            cleared.append(s)
        else:
            s['_dark_ok'] = True
    return cleared


def _cut_check(slots, F, ctx, log=None, ncc_cut=0.35, ncc_shot=0.6):
    """Hidden source cuts: the 6 fps analysis can miss a camera cut between two similar shots (dark, fast, the same
    colours), and a window across one shows an unplanned cut off the beat (the QA's unexpected cut). The shown span of
    every chosen window is decoded at the source rate (64 px gray); a frame pair whose structure breaks (NCC <
    ncc_cut) between two stretches that each hold together (>= ncc_shot) is a cut: that instant is banned
    (ctx['banned']: no window may cross it) and the slot cleared for re-assignment. Returns the cleared slots."""
    cleared = []
    for s in slots:
        pk = s.get('pick')
        if s['kind'] == 'black' or not pk or s.get('gap') or s.get('_times') is None or \
                s.get('_cut_ok') == (pk['ci'], round(float(pk['w0']), 3)):
            continue
        clip = F.clips[pk['ci']]
        info = clip['info']
        times = pk['w0'] + s['_times']
        sfps = float(info.get('fps') or 25.0)
        t0, t1 = float(times.min()), float(times.max()) + 1.0 / sfps
        try:
            got = list(V.frames(clip['path'], t0=t0, t1=t1, width=64, info=info))
        except Exception:
            continue
        if len(got) < 3:
            s['_cut_ok'] = (pk['ci'], round(float(pk['w0']), 3))
            continue
        ts = [t for t, _ in got]
        G = [cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY).astype(np.float32) for _, fr in got]
        Z = []
        for g_ in G:
            d = g_ - g_.mean()
            Z.append((d, float(np.sqrt((d * d).sum())), float(g_.std())))
        ncc = [float((a[0] * b[0]).sum() / (a[1] * b[1] + 1e-6)) if min(a[2], b[2]) >= 4.0 else 1.0 for a, b in zip(Z, Z[1:])]
        cut = None
        for i, v in enumerate(ncc):
            if v < ncc_cut and (i == 0 or ncc[i - 1] >= ncc_shot) and (i + 1 >= len(ncc) or ncc[i + 1] >= ncc_shot):
                cut = 0.5 * (ts[i] + ts[i + 1])
                break
        if cut is None:
            s['_cut_ok'] = (pk['ci'], round(float(pk['w0']), 3))
            continue
        ctx.setdefault('banned', []).append((pk['ci'], cut - 0.1, cut + 0.1))
        ctx['notes'].append(f"slot {s['i']} ({s['role']}): {pk['shot']} {pk['w0']:.2f}–{pk['w1']:.2f} s crosses a camera cut of "
                            f"the source at {cut:.2f} s that the analysis missed — re-picked")
        s['pick'] = None
        cleared.append(s)
    return cleared


_LIN8 = None


def _qa_flashes(frames8, fps, delta=0.1, area=0.25):
    """The QA's general-flash count on a frame sequence (ed_qa.analyse_flashes): linear luminance at 90 px wide,
    changes >= delta on >= area of the frame against the previous and the one before (darker state < 0.8), opposing
    transitions in pairs, worst 1 s window. -> worst flashes per second"""
    global _LIN8
    if _LIN8 is None:
        lin = ((np.arange(256) / 255.0 + 0.055) / 1.055) ** 2.4
        lin[:11] = np.arange(11) / 255.0 / 12.92
        _LIN8 = lin.astype(np.float32)
    if len(frames8) < 3:
        return 0
    h, w = frames8[0].shape[:2]
    hw, hh = 90, max(2, int(round(90 * h / w)))
    Y = []
    for fr in frames8:
        lin = _LIN8[cv2.resize(fr, (hw, hh), interpolation=cv2.INTER_AREA)]
        Y.append(lin[..., 0] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 2] * 0.0722)
    n = len(Y)
    up, dn = np.zeros(n), np.zeros(n)
    for k in range(1, n):
        for kk in (1, 2):
            if k - kk < 0:
                continue
            d = Y[k] - Y[k - kk]
            dark = np.minimum(Y[k], Y[k - kk]) < 0.8
            up[k] = max(up[k], float(((d >= delta) & dark).mean()))
            dn[k] = max(dn[k], float(((d <= -delta) & dark).mean()))
    dirs = np.zeros(n, int)
    dirs[(up > area) & (up >= dn)] = 1
    dirs[(dn > area) & (dn > up)] = -1
    tr = [(f, int(dirs[f])) for f in range(1, n) if dirs[f] and dirs[f - 1] != dirs[f]]
    win = max(1, int(round(fps)))
    best = 0
    for s0 in range(0, max(1, n - win + 1)):
        alt = []
        for f, d in tr:
            if s0 <= f <= s0 + win - 1 and (not alt or alt[-1] != d):
                alt.append(d)
        best = max(best, len(alt) // 2)
    return best


def _flash_check(slots, F, g, ctx, fps, sty=None, limit=3.0):
    """Flash safety of the speed-changed shots at the QA's resolution: the frames a velocity / ramp / stutter slot
    shows (its crop band, graded like the render) counted with the QA's flash metric. A window whose content alone
    reaches limit - 1 flashes per second (a speed-up across dark <-> bright composition changes) is banned and its
    slot re-assigned; the second time a velocity slot plays at normal speed instead. Returns the cleared slots."""
    try:
        import ed_edl as E
    except Exception:
        return []
    cleared = []
    for s in slots:
        pk = s.get('pick')
        mode = (s.get('speed') or {}).get('mode')
        if s['kind'] == 'black' or not pk or s.get('_flash_ok') or mode not in ('velocity', 'ramp', 'ramp_freeze', 'stutter'):
            continue
        clip = F.clips[pk['ci']]
        info = clip['info']
        bx = clip.get('box') or [0, 0, info.get('w') or 16, info.get('h') or 9]
        bw, bh = bx[2] - bx[0], bx[3] - bx[1]
        ww = min(1.0, (9 / 16) / (bw / max(1, bh)))
        cx = min(max(pk['W'].get('crop_cx', 0.5), ww / 2), 1 - ww / 2)
        rect = _even_rect([bx[0] + (cx - ww / 2) * bw, bx[1], bx[0] + (cx + ww / 2) * bw, bx[3]], info)
        times = pk['w0'] + s['_times']
        sfps = float(info.get('fps') or 25.0)
        try:
            got = list(V.frames(clip['path'], t0=float(times.min()), t1=float(times.max()) + 1.0 / sfps, width=180, crop=rect, info=info))
        except Exception:
            continue
        if len(got) < 3:
            continue
        ts = np.array([t for t, _ in got])
        seq = [got[int(np.argmin(np.abs(ts - t)))][1] for t in times]
        gr = style_grade(g['slug'], sty)
        Wp = pk['W']
        ev = exposure_ev(g['slug'], Wp['luma_c'], Wp.get('p99'), Wp.get('face_luma') if (Wp.get('face_share') or 0) >= 0.3 else None)
        if ev:
            gr = dict(gr, exposure=ev)                   # the shot's own exposure, as the segment will get it
        xs = [f.astype(np.float32) / 255.0 for f in seq]
        st = E.grade_stats([xs[0], xs[len(xs) // 2], xs[-1]], skip_black=False)
        graded = [(np.clip(E.apply_grade(x, gr, st), 0, 1) * 255 + 0.5).astype(np.uint8) for x in xs]
        fl = _qa_flashes(graded, fps)
        if fl >= limit - 1:
            n_try = s.get('_flash_tries', 0) + 1
            s['_flash_tries'] = n_try
            ctx.setdefault('banned', []).append((pk['ci'], pk['w0'], pk['w1']))
            if n_try >= 2 and mode == 'velocity' and not s['speed'].get('required'):
                s['speed'] = dict(mode='normal')
                s['_speed_reset'] = True
            ctx['notes'].append(f"slot {s['i']} ({s['role']}): {pk['shot']} {pk['w0']:.2f}-{pk['w1']:.2f} s flickers at {mode} "
                                f"({fl} flashes/s at the QA's resolution) - " + ('normal speed' if s.get('_speed_reset') else 're-picked'))
            s['pick'] = None
            cleared.append(s)
        else:
            s['_flash_ok'] = True
    return cleared


# ============================================================================ 5. moves
P_PUNCH = dict(bounce=dict(scale=1.18, mode='bounce', attack=0, release=0.33, blur_shutter=0.5),
               strong=dict(scale=1.27, mode='bounce', attack=0, release=0.33, blur_shutter=0.5),
               hold=dict(scale=1.3, mode='hold', attack=0, hold_until='cut', blur_shutter=0.5))
P_SHAKE = dict(impact=dict(profile='impact', amp=0.025, rot=0.0, tau=0.067, dir='bass_down', dtheta=30, blur_shutter=0.5),
               heavy=dict(profile='heavy', amp=0.05, rot=1.5, tau=0.11, dir='bass_down', dtheta=30, blur_shutter=0.5),
               soft=dict(profile='impact', amp=0.0125, rot=0.0, tau=0.067, dir='random', dtheta=30, blur_shutter=0.5))
P_RGB = dict(micro=dict(px=3, angle=0, mode='linear', env=dict(attack=0, hold=1, decay='exp', tau=2), mix=1.0, soften=0, edge='reflect'),
             normal=dict(px=10, angle=0, mode='linear', env=dict(attack=0, hold=1, decay='exp', tau=2), mix=1.0, soften=0, edge='reflect'),
             heavy=dict(px=16, angle=0, mode='linear', env=dict(attack=0, hold=1, decay='exp', tau=2), mix=1.0, soften=0, edge='reflect'),
             extreme=dict(px=20, angle=0, mode='linear', env=dict(attack=0, hold=1, decay='exp', tau=3), mix=1.0, soften=0, edge='reflect'))
GRADES = {
    'phonk': dict(preset='teal', contrast=1.35, sat=0.72, temp=-0.12, tint=-0.02, gamma=1.15, black=0.05, gain=0.95),
    'epic': dict(preset='teal', auto=0.7, contrast=1.2, sat=1.0, temp=0.0, tint=0.0,
                 split=[[0.05, 0.40, 0.45], [1.0, 0.82, 0.62], 0.12], black=0.02),
    'calm': dict(preset='warm', auto=0.6, contrast=0.95, sat=0.9, temp=0.18, tint=0.02, lift=0.07, gain=0.95),
    'viral': dict(preset='color', contrast=1.12, sat=1.12), 'drama': dict(preset='desat', contrast=1.2, sat=0.6),
    'sport': dict(preset='color', contrast=1.15, sat=1.1), 'travel': dict(preset='warm', sat=1.15, contrast=1.08),
    'fashion': dict(preset='color', contrast=1.12, sat=0.95), 'fanedit': dict(preset='teal', contrast=1.2, sat=0.95),
    'teaser': dict(preset='cool', contrast=1.25, sat=0.8, gamma=1.1), 'product': dict(preset='natural', contrast=1.05, sat=1.02),
}
TARGET_LUMA = {'phonk': 82, 'epic': 92, 'calm': 118, 'drama': 80, 'teaser': 75, 'fanedit': 85}   # source mean luma the grade expects


def exposure_ev(slug, luma, p99=None, face_luma=None):
    """Per-segment exposure compensation (grade 'exposure', stops) so graded shots land in the card's luma band and
    neighbors match ("neighboring shots: mean brightness differs by ≤ 15 %"); dark sources are lifted at most +1.2 EV,
    and never further than the highlights allow (p99 of the window: a dark frame with a bright sky or fire would
    clip to white and show its compression blocks)."""
    target = TARGET_LUMA.get(slug, 100)
    ev = 0.75 * math.log2(target / max(float(luma), 10.0))
    ev = max(-0.6, min(1.2, ev))
    if ev > 0 and p99 is not None:
        ev = min(ev, max(0.0, math.log2(250.0 / max(float(p99), 60.0)) + 0.15))   # the grades' curves roll the top off
    if face_luma is not None:
        # a backlit face (bright sky, dark face) reads by the face, not by the frame mean: lift up to +0.9 EV even
        # when the sky clips (the subject matters more than the sky)
        evf = 0.75 * math.log2(max(70.0, target) / max(float(face_luma), 10.0))
        if evf > ev:
            ev = max(ev, min(evf, 0.9))
    return round(ev, 2) if abs(ev) >= 0.15 else 0.0


# photosensitivity limit the QA applies (general flashes per 1 s window: pairs of opposing brightness changes > 10 % over
# > 25 % of the frame): the cards' "flashes <= 3 per second" (WCAG); drama ("<= 1 per second outside cuts") and calm
# stay stricter. FLASH_LIMIT_HZ below is the budget of the trans.flash move itself, a different thing.
QA_FLASH_HZ = {'drama': 1.0, 'calm': 1.0}


def qa_flash_hz(slug):
    return QA_FLASH_HZ.get(slug, 3.0)


# the cards' "Color" / "Quality checks" numbers each graded shot should measure (ed_qa image check: Rec.709 luma
# levels p1 / p99 / mean, HSV saturation); _fit_grades moves the grade of every shot into them, qa.color carries them
COLOR_TARGETS = {
    'phonk': dict(luma_mean=[40, 90], p1=[0, 6], p99=[0, 245], sat_mean=[0, 0.35]),
    'epic': dict(p1=[4, 10], p99=[235, 248]),
    'calm': dict(p1=[14, 26], p99=[228, 242]),
    'drama': dict(p1=[2, 8], p99=[215, 235]),
    'travel': dict(p1=[6, 12], p99=[238, 250]),
    'teaser': dict(p1=[0, 8], p99=[200, 248]),
}
# how far the fit may move each grade parameter (absolute bounds; a look's own value outside them is kept)
FIT_BOUNDS = dict(exposure=(-0.8, 1.4), auto=(0.0, 1.0), black=(0.0, 0.12), lift=(0.0, 0.12), gain=(0.85, 1.0), sat=(0.4, 1.4),
                  gamma=(0.75, 1.35))
FIT_COST = dict(exposure=0.4, auto=0.6, black=4.0, lift=4.0, gain=4.0, sat=1.0, gamma=0.8)   # per unit away from the genre grade
# what every graded shot keeps on a phone screen: at most ~7 % of the picture crushed to black, a mean luma of 60+ on
# normal-key footage (a low-key source keeps 90 % of its own mean); "very dark" requests (dark=True) relax both
PICTURE_LIMITS = dict(clip_lo=0.07, luma_floor=60.0, normal_key=65.0)
PICTURE_LIMITS_DARK = dict(clip_lo=0.15, luma_floor=35.0, normal_key=65.0)
DARK_WORDS = re.compile(r'very dark|pitch[- ]black|low[- ]?key|darkest|as dark as|super dark|really dark')
_PROBE_INFO = {}


def _probe_info(path):
    if path not in _PROBE_INFO:
        _PROBE_INFO[path] = V.probe(path)
    return _PROBE_INFO[path]


def _crop_window(edl, seg, k):
    """Source pixel rect [x0, y0, x1, y1] the segment's crop shows at segment frame k (no camera fx)."""
    src = edl['sources'][seg['src']]
    info = _probe_info(src['path'])
    W0, H0 = info.get('w') or 16, info.get('h') or 9
    bx = src.get('box') or [0, 0, W0, H0]
    bw, bh = bx[2] - bx[0], bx[3] - bx[1]
    cr = seg.get('crop') or {}
    if cr.get('path'):
        ks = [p_[0] for p_ in cr['path']]
        cx, cy, z = (float(np.interp(k, ks, [p_[i] for p_ in cr['path']])) for i in (1, 2, 3))
    else:
        cx, cy, z = float(cr.get('cx', 0.5)), float(cr.get('cy', 0.5)), float(cr.get('z', 1.0))
    out_a = edl['canvas']['w'] / edl['canvas']['h']
    box_a = bw / max(1, bh)
    ww, wh = ((out_a / box_a) / z, 1.0 / z) if out_a <= box_a else (1.0 / z, (box_a / out_a) / z)
    ww, wh = min(1.0, ww), min(1.0, wh)
    cx, cy = min(max(cx, ww / 2), 1 - ww / 2), min(max(cy, wh / 2), 1 - wh / 2)
    return [bx[0] + (cx - ww / 2) * bw, bx[1] + (cy - wh / 2) * bh, bx[0] + (cx + ww / 2) * bw, bx[1] + (cy + wh / 2) * bh]


def _probe_ks(seg, fps, n_probe=3):
    """Segment frames that represent a segment: 20 / 50 / 80 %, 10 / 30 / 50 / 70 / 90 % from 1.5 s on (a long shot
    can change its light on the way), the middle of a short one."""
    n = seg['f1'] - seg['f0'] + 1
    qs = ((0.1, 0.3, 0.5, 0.7, 0.9) if n >= 1.5 * fps else (0.2, 0.5, 0.8)) if (n_probe >= 3 and n >= 15) else (0.5,)
    return sorted({min(n - 1, max(0, int(round(q * (n - 1))))) for q in qs})


def _probe_plan(edl, seg, n_probe=3):
    """(source times, crop rects, segment frames) of the frames that represent a segment (_probe_ks): its crop windows
    without camera fx (the fit applies the shot's camera moves to them like the renderer)."""
    fps = edl['canvas']['fps']
    ks = _probe_ks(seg, fps, n_probe)
    if seg.get('times'):
        tk = [float(seg['times'][k]) for k in ks]
    else:
        tk = [float(seg.get('t', 0.0)) + k / fps * float(seg.get('speed', 1.0) or 0.0) for k in ks]
    return tk, [_crop_window(edl, seg, k) for k in ks], ks


def _probe_segments(edl, segs, width=None, span_max=8.0, keys=None):
    """{segment id: [uint8 RGB frames]} of what each segment's crop shows (no camera fx), in segment-frame order, at
    `width` px (the renderer's grade-stats scale). One decode pass per source and cluster of nearby times (long GOPs
    make every seek decode from a key frame). keys: a dict that receives each segment's probe frames ({id: [k]})."""
    width = width or max(32, int(edl['canvas']['w']) // 4)      # the renderer measures its grade stats at 1/4 size
    want = []
    for sg in segs:
        try:
            tk, rects, ks = _probe_plan(edl, sg)
        except Exception:
            continue
        for t, r, k in zip(tk, rects, ks):
            want.append((edl['sources'][sg['src']]['path'], t, r, sg['id'], k))
    got_k = {}
    by_src = {}
    for w in want:
        by_src.setdefault(w[0], []).append(w)
    hh = int(round(width * edl['canvas']['h'] / edl['canvas']['w']))
    for path, items in by_src.items():
        info = _probe_info(path)
        sfps = float(info.get('fps') or 25.0)
        items.sort(key=lambda x: x[1])
        clusters, cur = [], []
        for it in items:
            if cur and it[1] - cur[0][1] > span_max:
                clusters.append(cur)
                cur = []
            cur.append(it)
        if cur:
            clusters.append(cur)
        for cl in clusters:
            u = _even_rect([min(x[2][0] for x in cl), min(x[2][1] for x in cl), max(x[2][2] for x in cl), max(x[2][3] for x in cl)], info)
            rw = min(x[2][2] - x[2][0] for x in cl)
            uw = int(min(info.get('w') or 1920, max(16, round(width * (u[2] - u[0]) / max(1.0, rw)))))
            t0, t1 = cl[0][1], cl[-1][1] + 1.0 / sfps
            rate = min(sfps, 8.0) if t1 - t0 > 0.5 else sfps
            try:
                got = list(V.frames(path, t0=t0, t1=t1, fps=rate, width=uw - uw % 2, crop=u, info=info))     # (abs t, frame)
            except Exception:
                got = []
            if not got:
                continue
            for _, t, r, sid, k in cl:
                fr = min(got, key=lambda x: abs(x[0] - t))[1]
                h, w = fr.shape[:2]
                sx, sy = w / max(1.0, u[2] - u[0]), h / max(1.0, u[3] - u[1])
                x0, y0 = int(round((r[0] - u[0]) * sx)), int(round((r[1] - u[1]) * sy))
                x1, y1 = max(x0 + 2, int(round((r[2] - u[0]) * sx))), max(y0 + 2, int(round((r[3] - u[1]) * sy)))
                got_k.setdefault(sid, []).append((k, cv2.resize(np.ascontiguousarray(fr[y0:y1, x0:x1]), (width, hh), interpolation=cv2.INTER_AREA)))
    out = {}
    for sid, items in got_k.items():
        items.sort(key=lambda x: x[0])
        out[sid] = [f for _, f in items]
        if keys is not None:
            keys[sid] = [k for k, _ in items]
    return out


def _color_stats(frames8):
    """The image numbers ed_qa measures: Rec.709 luma levels on RGB (mean, p1, p99) and mean HSV saturation."""
    x = np.concatenate([f.reshape(-1, 3) for f in frames8]).astype(np.float32)
    Y = x[:, 0] * 0.2126 + x[:, 1] * 0.7152 + x[:, 2] * 0.0722
    S = np.concatenate([cv2.cvtColor(f, cv2.COLOR_RGB2HSV).reshape(-1, 3) for f in frames8])[:, 1].astype(np.float32) / 255.0
    p1, p99 = np.percentile(Y, [1, 99])
    return dict(luma_mean=float(Y.mean()), p1=float(p1), p99=float(p99), sat_mean=float(S.mean()), clip_hi=float((Y >= 253).mean()),
                clip_lo=float((Y <= 2).mean()))


LOOK_FX = ('vignette', 'bloom', 'glow', 'light_leak', 'clarity')   # constant looks that move the numbers the QA measures


def _camera_probes(frames8, fx, seg, ks, fps, beat_ctx=None):
    """The probe frames through the shot's camera moves at their segment frames (ed_fx.camera + apply_camera, the
    renderer's own composition): a held punch-in, a landed crash zoom or a shake's cover zoom changes what the grade
    has to hold."""
    cams = [d for d in (fx or []) if str(d.get('type', '')).startswith(('zoom.', 'shake.')) or d.get('type') in ('roll', 'drift', 'handheld')]
    if not seg or not cams or not ks or len(ks) != len(frames8):
        return frames8
    try:
        import ed_fx as FX
    except Exception:
        return frames8
    n = seg['f1'] - seg['f0'] + 1
    out = []
    for fr, k in zip(frames8, ks):
        h, w = fr.shape[:2]
        ctx = dict(ow=w, oh=h, w=w, h=h, fps=float(fps), f_abs=int(seg['f0']) + int(k), seg_f0=int(seg['f0']), k=k, n=n,
                   seg_id=seg.get('id'), **(beat_ctx or {}))
        ctr = (seg.get('crop') or {}).get('center')
        if ctr is not None:
            ctx['face'] = ctr
        try:
            cam = FX.camera(fx, k, n, ctx)
            y = FX.apply_camera(fr.astype(np.float32) / 255.0, cam, ctx, border=seg.get('border', 'reflect'), blur=False)
            out.append((np.clip(y, 0, 1) * 255.0 + 0.5).astype(np.uint8))
        except Exception:
            out.append(fr)
    return out


def _fit_one(frames8, grade, tgt, vignette=0.0, skip_black=False, measure_w=180, fx=None, seg=None, fps=30, face=None, limits=None,
             ks=None, beat_ctx=None, ev_cap=None):
    """Coordinate search on the grade (exposure, auto levels, black point, lift, gain, saturation, inside FIT_BOUNDS)
    until the shot's graded numbers sit inside the targets; the change from the genre grade is kept small.
    Returns (grade, stats before, stats after)."""
    import ed_edl as E
    xs = [f.astype(np.float32) / 255.0 for f in frames8]
    st = E.grade_stats(xs, skip_black=skip_black)       # auto-level stats at the renderer's scale (1/4), no camera fx
    if ks is not None:                                  # ... the picture itself through the shot's camera moves
        frames8 = _camera_probes(frames8, fx, seg, ks, fps, beat_ctx)
        xs = [f.astype(np.float32) / 255.0 for f in frames8]
    if measure_w and frames8[0].shape[1] > measure_w:   # the numbers at the QA's scale: its 320-px analysis frames
        mh = int(round(frames8[0].shape[0] * measure_w / frames8[0].shape[1]))      # sampled every 2nd pixel
        xs = [cv2.resize(x, (measure_w, mh), interpolation=cv2.INTER_AREA)[::2, ::2] for x in xs]
        frames8 = [cv2.resize(f, (measure_w, mh), interpolation=cv2.INTER_AREA)[::2, ::2] for f in frames8]
    stack = np.concatenate(xs, axis=0)                  # the grade is per pixel (auto uses st): one call for all
    h, w = frames8[0].shape[:2]
    looks = []                                          # the shot's constant looks, applied like the renderer does
    try:
        import ed_fx as FX
        n_ = (seg['f1'] - seg['f0'] + 1) if seg else 1
        ctx = dict(ow=w, oh=h, fps=fps, seg_f0=seg['f0'] if seg else 0)
        for d in fx or []:
            fn = FX.FX_TYPES.get(d.get('type'))
            if fn is not None and d.get('type') in LOOK_FX and not d.get('times') and not d.get('frames'):
                looks.append((fn, d, n_, ctx))
        if vignette and not any(d.get('type') == 'vignette' for _, d, _, _ in looks):
            looks.append((FX.FX_TYPES['vignette'], dict(type='vignette', amount=float(vignette)), 1, ctx))
    except Exception:
        looks = []
    scale = dict(luma_mean=10.0, p1=4.0, p99=6.0, sat_mean=0.04)
    # aim a little inside each range: the probes are a sample and the render adds grain / encoding (QA - fit, measured
    # over the test footage: sat +0.02, luma +-4)
    margin, top = dict(luma_mean=3.0, p1=0.5, p99=2.0, sat_mean=0.025), dict(luma_mean=255.0, p1=255.0, p99=255.0, sat_mean=1.0)

    def inside(k, lo, hi):
        lo2 = lo + margin.get(k, 0.0) if lo > 0 else lo
        hi2 = hi - margin.get(k, 0.0) if hi < top.get(k, 1e9) else hi
        return (lo2, hi2) if lo2 <= hi2 else ((lo + hi) / 2.0, (lo + hi) / 2.0)
    tgt = {k: inside(k, lo, hi) for k, (lo, hi) in tgt.items()}
    lim = limits or {}
    src_mean = float(np.mean([(f.astype(np.float32) * [0.2126, 0.7152, 0.0722]).sum(-1).mean() for f in frames8]))
    floor = 0.0
    if lim.get('luma_floor'):                           # normal-key footage keeps a readable mean, low-key its own
        floor = lim['luma_floor'] if src_mean >= lim.get('normal_key', 65.0) else min(lim['luma_floor'], 0.9 * src_mean)

    fbox = None
    if face is not None:                                # face box in the probe frames (fractions) -> pixel slices
        fx0, fy0, fx1, fy1 = face
        fbox = (int(fy0 * h), max(int(fy0 * h) + 1, int(math.ceil(fy1 * h))), int(fx0 * w), max(int(fx0 * w) + 1, int(math.ceil(fx1 * w))))

    def measure(gr):
        y = np.clip(E.apply_grade(stack, gr, st), 0, 1).astype(np.float32)
        if looks:
            parts = []
            for i in range(len(xs)):
                fr = np.ascontiguousarray(y[i * h:(i + 1) * h])
                for fn, d, n_, cx in looks:
                    try:
                        fr = np.clip(fn(fr, d, n_ // 2, n_, cx), 0, 1)
                    except Exception:
                        pass
                parts.append(fr)
            y = np.concatenate(parts, axis=0)
        y8 = (np.clip(y, 0, 1) * 255.0 + 0.5).astype(np.uint8)
        m = _color_stats([y8])
        if fbox is not None:
            fr_ = np.concatenate([y8[i * h + fbox[0]:i * h + fbox[1], fbox[2]:fbox[3]] for i in range(len(xs))], axis=0).astype(np.float32)
            Yf = fr_[..., 0] * 0.2126 + fr_[..., 1] * 0.7152 + fr_[..., 2] * 0.0722
            m['face_p99'] = float(np.percentile(Yf, 99)) if Yf.size else 0.0
        return m

    def cost(m, gr):
        c = 0.0
        for k, (lo, hi) in tgt.items():
            v = m.get(k)
            if v is None:
                continue
            c += max(0.0, lo - v) / scale[k] + max(0.0, v - hi) / scale[k]
        for k, w in FIT_COST.items():                       # stay close to the genre grade
            c += w * abs(float(gr.get(k, base_v(k))) - base_v(k))
        # protection: never clip more of the picture than the genre grade did, never push a face into clipping
        c += 400.0 * max(0.0, m['clip_hi'] - clip_cap)
        if 'face_p99' in m:                                 # a face first: its highlights outrank the p99 target
            c += max(0.0, m['face_p99'] - face_cap) * 1.5
        if lim.get('clip_lo') is not None:                  # a look keeps its character, not a crushed picture
            c += 300.0 * max(0.0, m['clip_lo'] - lim['clip_lo'])
        c += max(0.0, floor - m['luma_mean']) / 6.0
        return c

    def base_v(k):
        return float(base.get(k, {'gain': 1.0, 'sat': 1.0, 'gamma': 1.0}.get(k, 0.0)))

    pre = E.grade_params(grade)
    base = dict(pre)
    g = dict(grade)
    m0 = measure(g)
    clip_cap = max(min(m0['clip_hi'], 0.01) + 0.002, 0.005)   # at most ~1 % of clipped picture, whatever the start
    face_cap = 238.0                                    # a face never goes into clipping
    best_c = cost(m0, g)
    m = m0
    moves = [('exposure', (0.15, -0.15, 0.4, -0.4, 0.08, -0.08)), ('auto', (0.15, 0.3, -0.15)), ('black', (0.02, 0.04, -0.02, -0.04)),
             ('lift', (0.02, -0.02, 0.04)), ('gain', (-0.03, 0.03)), ('gamma', (-0.08, 0.08))] + \
        ([('sat', (-0.1, -0.2, 0.1))] if 'sat_mean' in tgt else [])
    for _ in range(6):
        if all(lo <= m.get(k, lo) <= hi for k, (lo, hi) in tgt.items()) and m['clip_hi'] <= clip_cap \
                and m.get('face_p99', 0.0) <= face_cap and m['clip_lo'] <= lim.get('clip_lo', 1.0) and m['luma_mean'] >= floor:
            break
        improved = False
        for k, deltas in moves:
            for d in deltas:
                cur = float(g.get(k, pre.get(k, {'gain': 1.0, 'sat': 1.0, 'gamma': 1.0}.get(k, 0.0))))
                lo_b, hi_b = FIT_BOUNDS[k]
                if k == 'exposure':                         # at most -0.6 / +0.8 EV from the shot's own exposure
                    lo_b, hi_b = max(lo_b, base_v(k) - 0.6), min(hi_b, base_v(k) + 0.8)
                    if ev_cap is not None:                  # well-exposed footage: the cap holds
                        hi_b = min(hi_b, max(ev_cap, base_v(k)))
                else:                                       # a look outside the bounds keeps its value (sat: -30 %)
                    lo_b, hi_b = min(lo_b, base_v(k) * (0.7 if k == 'sat' else 1.0)), max(hi_b, base_v(k))
                v = round(min(hi_b, max(lo_b, cur + d)), 3)
                if abs(v - cur) < 1e-6:
                    continue
                g2 = dict(g, **{k: v})
                m2 = measure(g2)
                c2 = cost(m2, g2)
                if c2 < best_c - 1e-6:
                    best_c, g, m, improved = c2, g2, m2, True
        if not improved:
            break
    return g, m0, m


def E_grade_mono(grade):
    """True when the grade (or its preset) renders black and white."""
    try:
        import ed_edl as E
        return bool(E.grade_params(grade).get('mono'))
    except Exception:
        return bool(grade.get('mono'))


def _face_in_probe(edl, sg, face):
    """(cx, cy, h) of a face (fractions of the source box) -> its box in the segment's probe frames (fractions)."""
    if not face:
        return None
    cx, cy, fh = face
    src = edl['sources'][sg['src']]
    info = _probe_info(src['path'])
    bx = src.get('box') or [0, 0, info.get('w') or 16, info.get('h') or 9]
    bw, bh = bx[2] - bx[0], bx[3] - bx[1]
    r = _crop_window(edl, sg, (sg['f1'] - sg['f0']) // 2)
    px, py, ph = bx[0] + cx * bw, bx[1] + cy * bh, fh * bh
    pw = 0.8 * ph
    rw, rh = max(1.0, r[2] - r[0]), max(1.0, r[3] - r[1])
    box = [(px - pw / 2 - r[0]) / rw, (py - 0.55 * ph - r[1]) / rh, (px + pw / 2 - r[0]) / rw, (py + 0.55 * ph - r[1]) / rh]
    box = [min(1.0, max(0.0, v)) for v in box]
    return box if (box[2] - box[0]) > 0.02 and (box[3] - box[1]) > 0.02 else None


# genres whose cards ask neighbouring shots to match in brightness (<= 15 % mean-luma difference at a plain cut);
# hype genres (phonk, fan edit, viral, sport) live on light contrast
LUMA_MATCH_GENRES = ('epic', 'calm', 'travel', 'drama', 'fashion', 'teaser', 'product', 'motivation')
LUMA_JUMP_MAX = 1.15
EXPOSURE_CAP_WELL_EXPOSED = 0.6       # EV: auto exposure on footage that already spans the range (generated, lit)


def _grade_push(grade):
    """The colour a grade adds to neutral grey (auto levels and exposure left out): mean R-B and G-(R+B)/2 over
    grey 0.3-0.95 -> (warm push, green push)."""
    import ed_edl as E
    g = {k: v for k, v in (grade or {}).items() if k not in ('exposure', 'auto')}
    ramp = np.linspace(0.3, 0.95, 14, dtype=np.float32)
    y = np.asarray(E.apply_grade(np.repeat(ramp[:, None], 3, axis=1)[None], g, None), np.float32)[0]
    return float((y[:, 0] - y[:, 2]).mean()), float((y[:, 1] - 0.5 * (y[:, 0] + y[:, 2])).mean())


def _footage_aware_grade(grade, frames8):
    """A look on footage that already has a colour cast (warm interiors, generated shots): the shot's own cast
    (mean R-B and G-magenta of its mid-tones) and the share of its bright area that is near-neutral (walls, whites)
    are measured; the look's colour push (temp, tint, mult, the split's highlight tone) is reduced along the
    footage's own cast (cast 0.05 -> x0.9, 0.15 -> x0.4, >= 0.2 -> x0.25) and the highlight tone moves toward
    neutral with the near-neutral share of the highlights. Contrast, saturation and the shadow tone stay.
    -> (grade, note | None)"""
    g = dict(grade or {})
    x = np.concatenate([f.reshape(-1, 3) for f in frames8]).astype(np.float32) / 255.0
    Y = x @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    mid = (Y > 0.2) & (Y < 0.9)
    if mid.sum() < 50 or g.get('mono'):
        return g, None
    cast_rb = float((x[mid, 0] - x[mid, 2]).mean())
    cast_gm = float((x[mid, 1] - 0.5 * (x[mid, 0] + x[mid, 2])).mean())
    bright = Y > 0.6
    chroma = x.max(1) - x.min(1)
    nn = float((bright & (chroma < 0.22)).sum() / bright.sum()) if bright.sum() >= 50 else 0.0
    try:
        push_rb, push_gm = _grade_push(g)
    except Exception:
        return g, None
    f_rb = max(0.25, 1.0 - (abs(cast_rb) - 0.03) / 0.2) if (cast_rb * push_rb > 0 and abs(cast_rb) > 0.03) else 1.0
    f_gm = max(0.25, 1.0 - (abs(cast_gm) - 0.02) / 0.12) if (cast_gm * push_gm > 0 and abs(cast_gm) > 0.02) else 1.0
    h = 1.0 - 0.6 * nn
    did = []
    if g.get('temp') and f_rb < 1.0 and float(g['temp']) * cast_rb > 0:
        g['temp'] = round(float(g['temp']) * f_rb, 4)
        did.append('temp')
    if g.get('tint') and f_gm < 1.0 and float(g['tint']) * cast_gm > 0:
        g['tint'] = round(float(g['tint']) * f_gm, 4)
        did.append('tint')
    m = g.get('mult')
    if isinstance(m, (list, tuple)) and len(m) == 3 and f_rb < 1.0 and (float(m[0]) - float(m[2])) * cast_rb > 0:
        g['mult'] = [round(1.0 + (float(v) - 1.0) * f_rb, 4) for v in m]
        did.append('mult')
    sp = g.get('split')
    if isinstance(sp, (list, tuple)) and len(sp) == 3:
        sh, hi, amt = sp
        fh = (f_rb if (float(hi[0]) - float(hi[2])) * cast_rb > 0 else 1.0) * h
        if fh < 0.95:
            g['split'] = [list(sh), [round(0.5 + (float(c) - 0.5) * fh, 4) for c in hi], amt]
            did.append('highlight tone')
    if not did:
        return g, None
    return g, (f"look push x{min(f_rb, f_gm):.2f} along the shot's own cast (R-B {cast_rb:+.2f}), near-neutral highlights "
               f"{100 * nn:.0f} %: {', '.join(did)} eased")


def _exposure_cap(frames8):
    """Auto exposure cap (EV) for footage that is already well exposed - mean luma >= 45 and highlights >= 150 of
    255 (it spans the range): EXPOSURE_CAP_WELL_EXPOSED; None (no cap) for dark footage."""
    x = np.concatenate([f.reshape(-1, 3) for f in frames8]).astype(np.float32)
    Y = x @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    return EXPOSURE_CAP_WELL_EXPOSED if (Y.mean() >= 45.0 and np.percentile(Y, 99) >= 150.0) else None


def _fit_grades(edl, slug, targets=None, log=None, faces=None, limits=PICTURE_LIMITS, cut_pairs=None):
    """Per-shot grade fit against the card's color targets (COLOR_TARGETS) and the picture limits every graded shot
    keeps (PICTURE_LIMITS: black crush, mean luma on normal-key footage): what each segment's crop shows is decoded
    (3-5 small frames), moved by the shot's camera fx, graded with the renderer's own apply_grade (+ its look fx) and
    the grade moved inside them.
    Returns {segment id: {before, after, changed}} for meta."""
    tgt = dict(targets if targets is not None else (COLOR_TARGETS.get(slug) or {}))
    if not tgt and not limits:
        return {}
    try:
        import ed_edl  # noqa: F401
    except Exception:
        return {}
    segs = [sg for sg in edl['segments'] if sg.get('speed') != 0.0 and sg.get('src') in edl['sources']]
    keys = {}
    probes = _probe_segments(edl, segs, keys=keys)
    gr = (edl.get('audio') or {}).get('grid') or (edl.get('meta') or {}).get('grid') or {}
    bctx = {k: [float(v) for v in gr[k]] for k in ('beats', 'downbeats') if gr.get(k)}
    out, ctx_fit = {}, {}
    for sg in segs:
        frames = probes.get(sg['id'])
        if not frames:
            continue
        mono = bool(E_grade_mono(sg.get('grade') or {}))
        tg = {k: v for k, v in tgt.items() if not (mono and k == 'sat_mean')}
        g0 = dict(sg.get('grade') or {})
        g_in, note = _footage_aware_grade(g0, frames)
        cap = _exposure_cap(frames)
        if cap is not None and float(g_in.get('exposure', 0.0)) > cap:
            g_in['exposure'] = cap                      # well-exposed footage: no +1 EV push that blows the walls out
        kw = dict(skip_black=sg.get('border') == 'black', fx=sg.get('fx'), seg=sg, fps=edl['canvas']['fps'],
                  face=_face_in_probe(edl, sg, (faces or {}).get(sg['id'])), limits=limits, ks=keys.get(sg['id']),
                  beat_ctx=bctx, ev_cap=cap)
        g2, m0, m1 = _fit_one(frames, g_in, tg, **kw)
        ctx_fit[sg['id']] = (frames, tg, kw, m0)
        changed = {k: g2[k] for k in g2 if g2.get(k) != g0.get(k)}
        if changed:
            sg['grade'] = g2
        out[sg['id']] = dict(before={k: round(v, 3) for k, v in m0.items()}, after={k: round(v, 3) for k, v in m1.items()},
                             changed=changed, **({'look': note} if note else {}), **({'ev_cap': cap} if cap is not None else {}))
    if cut_pairs:
        _match_luma_jumps(edl, cut_pairs, out, ctx_fit, log)
    return out


def _relax_p99_for_capped(edl, fit):
    """Well-exposed footage keeps its highlights where the exposure cap leaves them: when a capped shot ends below the
    card's p99 floor, qa.color's floor follows it (never under 215) and qa.color_note says why."""
    col = (edl.get('qa') or {}).get('color') or {}
    p99 = col.get('p99')
    if not fit or not p99:
        return
    low = [float(r['after']['p99']) for r in fit.values() if r.get('ev_cap') is not None and r.get('after')
           and float(r['after'].get('p99', 999)) < p99[0]]
    if low:
        new = max(215, int(math.floor(min(low))) - 2)
        if new < p99[0]:
            edl['qa']['color_note'] = (f"p99 floor {p99[0]} -> {new}: well-exposed footage keeps its highlights under the "
                                       f"auto-exposure cap (+{EXPOSURE_CAP_WELL_EXPOSED} EV) instead of being pushed to the card's floor")
            p99[0] = new


def _op_frames_of(op):
    f = op.get('f')
    if isinstance(f, int):
        return {f}
    if isinstance(f, str) and ':' in f:
        a, b = f.split(':', 1)
        return set(range(int(a), int(b) + 1))
    if isinstance(f, (list, tuple)):
        return {int(x) for x in f if isinstance(x, (int, float))}
    return set()


def _plain_cut_pairs(edl, by_seg):
    """(segment id, segment id) of every plain cut inside one music part: no transition, no flash / dip / black op
    within 2 frames of the cut, neither side a black pause, crash or freeze - the cuts where a brightness jump is
    not intended."""
    segs = edl['segments']
    opf = set()
    for op in edl.get('ops') or []:
        opf |= _op_frames_of(op)
    out = []
    for i in range(len(segs) - 1):
        a, b = segs[i], segs[i + 1]
        sa, sb = by_seg.get(i) or {}, by_seg.get(i + 1) or {}
        if sa.get('part') != sb.get('part') or (b.get('transition_in') or {}).get('kind') not in (None, 'cut'):
            continue
        if any(s_.get('kind') in ('black', 'freeze') or s_.get('crash') or s_.get('dip') for s_ in (sa, sb)):
            continue
        if any(f in opf for f in range(int(b['f0']) - 2, int(b['f0']) + 3)):
            continue
        out.append((a['id'], b['id']))
    return out


def _match_luma_jumps(edl, pairs, out, ctx_fit, log=None, passes=2):
    """Neighbouring shots at a plain cut inside one music part keep their mean brightness within LUMA_JUMP_MAX
    (cards: <= 15 %): of the two, the one farther from the part's median brightness is refitted with a mean-luma band
    around its neighbour (the card targets and picture limits still hold). Updates the grades and `out`."""
    by_id = {sg['id']: sg for sg in edl['segments']}
    lum = lambda sid: float(out[sid]['after']['luma_mean'])     # noqa: E731
    for _ in range(passes):
        moved = False
        for a, b in pairs:
            if a not in out or b not in out or a not in ctx_fit or b not in ctx_fit:
                continue
            la, lb = lum(a), lum(b)
            if max(la, lb) / max(1.0, min(la, lb)) <= LUMA_JUMP_MAX + 0.005:
                continue
            group = [lum(x) for x in out if x in ctx_fit]
            med = float(np.median(group)) if group else 0.5 * (la + lb)
            sid, other = (a, b) if abs(math.log(max(la, 1.0) / max(med, 1.0))) > abs(math.log(max(lb, 1.0) / max(med, 1.0))) else (b, a)
            lo_, hi_ = lum(other) / (LUMA_JUMP_MAX - 0.02), lum(other) * (LUMA_JUMP_MAX - 0.02)
            frames, tg, kw, m0 = ctx_fit[sid]
            tg2 = dict(tg)
            if 'luma_mean' in tg2:
                lo_, hi_ = max(lo_, tg2['luma_mean'][0]), min(hi_, tg2['luma_mean'][1])
            if lo_ > hi_:
                continue
            tg2['luma_mean'] = [lo_, hi_]
            sg = by_id[sid]
            g2, _, m1 = _fit_one(frames, sg.get('grade') or {}, tg2, **kw)
            if abs(float(m1['luma_mean']) - lum(sid)) < 0.5:
                continue
            old = lum(sid)
            sg['grade'] = g2
            out[sid]['after'] = {k: round(v, 3) for k, v in m1.items()}
            out[sid]['changed'] = dict(out[sid].get('changed') or {}, **{k: g2[k] for k in ('exposure', 'auto', 'black', 'lift', 'gain', 'gamma')
                                                                          if k in g2})
            out[sid]['matched'] = f'mean luma {old:.0f} -> {float(m1["luma_mean"]):.0f} next to {other} ({lum(other):.0f})'
            moved = True
        if not moved:
            break


FLASH_LIMIT_HZ = {'phonk': 3.0, 'viral': 3.0, 'fanedit': 3.0, 'fashion': 3.0, 'sport': 2.0, 'teaser': 2.0, 'epic': 0.3,
                  'drama': 0.5, 'calm': 0.0, 'travel': 1.0, 'product': 1.0}


class Placer:
    """Move placement context: segments, beat events, accent accounting (≤ 2 per beat, 4 on the hook / drop first beat),
    flash spacing, logs every placement and every skipped move with its reason (meta)."""

    def __init__(self, g, edl, slots, beats, parts, fps, T, music_in):
        self.g, self.e, self.slots, self.beats, self.parts, self.fps, self.T = g, edl, slots, beats, parts, fps, T
        self.music_in = music_in
        self.segs = edl['segments']
        self.acc = {}
        self.multi_ok = set()
        self.flash_frames = []
        self.skipped = []
        self.count = {}
        self.seed = 1

    def ok(self, mid, part=None, why_ctx=''):
        ok, reason = move_allowed(self.g, mid, part)
        if not ok:
            key = (mid, part)
            if key not in {(x['move'], x.get('part')) for x in self.skipped}:
                self.skipped.append(dict(move=mid, part=part, reason=reason + (f' ({why_ctx})' if why_ctx else '')))
        return ok

    def skip(self, mid, reason, part=None):
        self.skipped.append(dict(move=mid, part=part, reason=reason))

    def seg_at(self, f):
        for i, s in enumerate(self.segs):
            if s['f0'] <= f <= s['f1']:
                return i
        return None

    def beats_in(self, si, inner=False):
        s = self.segs[si]
        out = [b for b in self.beats if s['f0'] <= b['f'] <= s['f1']]
        return [b for b in out if b['f'] > s['f0']] if inner else out

    def n_acc(self, f):
        return len(self.acc.get(f, []))

    def can_acc(self, f, n=1):
        lim = 4 if f in self.multi_ok else 2
        return self.n_acc(f) + n <= lim

    def _log(self, si, mid, k, why):
        if mid == 'angle.low' and self.count.get(mid, 0) >= 2:      # footage label: "1–2 shots" per the cards
            return
        self.count[mid] = self.count.get(mid, 0) + 1
        sl = self.slots_by_seg.get(si)
        if sl is not None:
            sl.setdefault('moves', []).append(dict(id=mid, k=k, f=self.segs[si]['f0'] + (k or 0), why=why))

    def fx(self, si, mid, fx, k=None, why='', accent=None):
        s = self.segs[si]
        if accent and k is not None:
            f = s['f0'] + k
            if not self.can_acc(f):
                self.skip(mid, f'accent limit per beat (frame {f})')
                return False
            self.acc.setdefault(f, []).append(accent)
        d = _to_events(fx, s['f0'], self.fps)
        d.setdefault('move', mid)
        s.setdefault('fx', []).append(d)
        self._log(si, mid, k, why)
        return True

    def transition(self, si, mid, tr, why=''):
        s = self.segs[si]
        if tr['kind'] == 'flash':
            if not self.flash_ok(s['f0']):
                self.skip(mid, f'flash spacing (frame {s["f0"]})')
                return False
            self.flash_frames.append(s['f0'])
        d = dict(tr)
        d['move'] = mid
        s['transition_in'] = d
        self._log(si, mid, 0, why)
        return True

    def flash_ok(self, f):
        """trans.flash budget: gap ≥ 10 frames @30 (9 @25), ≤ flash_limit_hz per second (per 10 s when < 1 Hz)."""
        gap = 10 if self.fps >= 30 else 9
        lim = FLASH_LIMIT_HZ.get(self.g['slug'], 2.0)
        if lim <= 0 or any(abs(f - x) < gap for x in self.flash_frames):
            return False
        span = self.fps * (1.0 if lim >= 1 else 10.0)
        cap = lim * (1.0 if lim >= 1 else 10.0)
        near = [x for x in self.flash_frames if abs(x - f) < span]
        return len(near) + 1 <= max(1, int(round(cap)))

    def op(self, mid, op, why='', si=None):
        d = dict(op)
        d['move'] = mid
        self.e['ops'].append(d)
        if si is not None:
            self._log(si, mid, None, why)
        else:
            self.count[mid] = self.count.get(mid, 0) + 1

    def sfx(self, mid, kind, at, why='', **kw):
        if not (-1e-6 <= float(at) <= self.T + 0.01):
            self.skip(mid, f'{kind} at {float(at):.2f} s falls outside the edit (0–{self.T:.2f} s)')
            return False
        d = dict(kind=kind, at=round(max(0.0, float(at)), 4), seed=self.seed, move=mid, why=why)
        d.update(kw)
        self.seed += 1
        self.e['audio']['sfx'].append(d)
        self.count[mid] = self.count.get(mid, 0) + 1
        return True

    def layer(self, mid, layer, why=''):
        d = dict(layer)
        d['move'] = mid
        d['why'] = why
        self.e['layers'].append(d)
        self.count[mid] = self.count.get(mid, 0) + 1


EVENT_FX = {'zoom.punch', 'shake.beat', 'zoom.in_out', 'rgb_split', 'glitch_blocks', 'glitch', 'flash', 'glow'}


def _to_events(fx, f0, fps):
    """ed_fx reads event-driven fx from `times` (absolute output seconds, peak frame = floor(t*fps + 0.4)) and treats
    `frames` as a gate. The planner works in segment frames k; convert here: frames=[k..] -> times, glitch burst
    length -> burst, zoom.crash start frame -> landing time `at`."""
    d = dict(fx)
    fr = d.get('frames')
    if not isinstance(fr, list) or not fr:
        return d
    t = d.get('type')
    if t == 'zoom.crash':
        d.pop('frames')
        d['at'] = round((f0 + int(fr[0])) / fps + float(d.get('dur', 0.4)), 4)
    elif t == 'light_leak':
        d.pop('frames')
        d['at'] = round((f0 + int(fr[0])) / fps, 4)
    elif t in ('glitch_blocks', 'glitch'):
        d.pop('frames')
        d['times'] = [round((f0 + int(fr[0])) / fps, 4)]
        d['burst'] = len(fr)
    elif t in EVENT_FX:
        d.pop('frames')
        d['times'] = [round((f0 + int(k)) / fps, 4) for k in fr]
    return d


def _crash_scale(P, si, want, max_up=4.5):
    """Crash-zoom scale the source resolution can carry: the landing frame is held, so the total upscale (9:16 crop
    of the source x the zoom) stays <= max_up (720p sources land at about x1.7, 4K at the card's x2.5-3.5)."""
    s = P.segs[si]
    h = s.get('_src_h')
    if not h:
        return want
    base = P.e['canvas']['h'] / float(h)                 # upscale of the crop window itself
    return round(max(1.5, min(want, max_up / max(base, 1e-6))), 2)


def _center(seg):
    c = seg.get('_center')
    return c if c else [0.5, 0.45]


def _crop_cover(seg, z):
    """Constant safety scale (shake / tilt cover): multiplies every z of the crop (path included)."""
    cr = seg['crop']
    cr['z'] = round(cr.get('z', 1.0) * z, 4)
    if cr.get('path'):
        cr['path'] = [[p[0], p[1], p[2], round(p[3] * z, 4)] for p in cr['path']]
    cr['cover'] = round(cr.get('cover', 1.0) * z, 4)


MAX_UPSCALE = 3.0      # total source -> canvas upscale a crop zoom may reach (720p in 9:16 is x2.67 before any zoom)


def _crop_zoom(seg, z0, z1, ease='linear'):
    """zoom.slow / zoom.out baked into the crop path (z multiplies over the segment). The zoom is capped by the
    source resolution (MAX_UPSCALE over the crop window's own upscale): a pull-out from x1.6 on 720p is mush."""
    if seg.get('_src_h') and seg.get('_out_h'):
        cap = max(1.05, MAX_UPSCALE / (seg['_out_h'] / float(seg['_src_h'])))
        if max(z0, z1) > cap:
            k = (cap - 1.0) / max(max(z0, z1) - 1.0, 1e-6)          # keep the move's shape, shrink its amplitude
            z0, z1 = 1.0 + (z0 - 1.0) * k, 1.0 + (z1 - 1.0) * k
    cr = seg['crop']
    n = seg['f1'] - seg['f0'] + 1
    path = cr.get('path') or [[0, cr.get('cx', 0.5), cr.get('cy', 0.5), cr.get('z', 1.0)], [n - 1, cr.get('cx', 0.5), cr.get('cy', 0.5), cr.get('z', 1.0)]]
    ks = sorted(set([p[0] for p in path] + list(range(0, n, 3)) + [n - 1]))
    kk = [p[0] for p in path]
    out = []
    for k in ks:
        cx = float(np.interp(k, kk, [p[1] for p in path]))
        cy = float(np.interp(k, kk, [p[2] for p in path]))
        zb = float(np.interp(k, kk, [p[3] for p in path]))
        zm = z0 + (z1 - z0) * _ease(k / max(n - 1, 1), ease)
        out.append([int(k), round(cx, 4), round(cy, 4), round(zb * zm, 4)])
    cr['path'] = out
    cr['z'] = out[0][3]


def _letterbox_fx(t_anim, ratio, ease='linear'):
    return dict(type='letterbox', ratio=[round(ratio[0], 4), round(ratio[1], 4)], t=[round(t_anim[0], 4), round(t_anim[1], 4)],
                ease=ease, color='#000000', anchor=[0.5, 0.5], through_cuts=True)


def _black_ops(P, f0, f1, a0=1.0, a1=1.0, mid='trans.fade', why='', stage='post'):
    n = f1 - f0 + 1
    if n <= 0:
        return
    if abs(a0 - a1) < 1e-6:
        P.op(mid, dict(f=f'{f0}:{f1}', op='black', a=round(a1, 3), stage=stage), why)
        return
    for k in range(n):
        a = a0 + (a1 - a0) * (k + 1) / n
        P.e['ops'].append(dict(f=[f0 + k], op='black', a=round(min(1.0, max(0.0, a)), 3), stage=stage, move=mid))
    P.count[mid] = P.count.get(mid, 0) + 1


def program_phonk(P):
    g, fps, segs, beats = P.g, P.fps, P.segs, P.beats
    pt = P.parts
    is_part = lambda si, name: P.slots_by_seg[si]['part'] == name
    # lens.vignette (allowed): light constant vignette, corners ×0.7
    if P.ok('lens.vignette'):
        for si, s in enumerate(segs):
            P.fx(si, 'lens.vignette', dict(type='vignette', amount=0.3, shape='ellipse'), why='dark phonk: constant light vignette')
    # ---- hook: combo on the first hit
    b0 = beats[0]
    P.multi_ok.add(b0['f'])
    si0 = P.seg_at(b0['f'])
    k0 = b0['f'] - segs[si0]['f0']
    if P.ok('shake.beat', 'hook'):
        P.fx(si0, 'shake.beat', dict(type='shake.beat', frames=[k0], **P_SHAKE['heavy'], seed=0), k0, 'combo on the first hit: heavy shake', 'shake')
    if P.ok('trans.flash', 'hook'):
        curve = _exp_curve(0.06, fps)
        P.op('trans.flash', dict(f=f'{b0["f"]}:{b0["f"] + len(curve) - 1}', op='flash', color='#ffffff', curve=curve, blend='normal',
                                 stage='pre'), 'frame 0 comes out of white (τ 60 ms)', si0)
        P.acc.setdefault(b0['f'], []).append('flash')
        P.flash_frames.append(b0['f'])
    if P.ok('fx.rgb_split', 'hook'):
        P.fx(si0, 'fx.rgb_split', dict(type='rgb_split', frames=[k0], **P_RGB['heavy']), k0, 'hook combo: heavy RGB 16 px', 'rgb')
    if P.ok('zoom.punch', 'hook'):
        nxt = [b for b in P.beats_in(si0, inner=True) if b['pos'] in (2, 0) and b['f'] - segs[si0]['f0'] >= int(0.3 * fps)]
        if nxt:
            b = nxt[0]
            k = b['f'] - segs[si0]['f0']
            P.fx(si0, 'zoom.punch', dict(type='zoom.punch', frames=[k], **P_PUNCH['hold'], center=_center(segs[si0])), k,
                 'punch ×1.3 hold on the next downbeat inside the shot (frame 0 is taken by the combo)', 'punch')
    # angle.dutch: digital tilt in hook (if not a real low angle) and in build, sides alternate
    sign = 1
    for si, s in enumerate(segs):
        sl = P.slots_by_seg[si]
        if sl['part'] not in ('hook', 'build') or sl['kind'] in ('stutter',):
            continue
        if sl['part'] == 'hook' and (sl.get('pick') or {}).get('W', {}).get('low_angle'):
            P._log(si, 'angle.low', 0, 'real low angle from the source')
            continue
        if not P.ok('angle.dutch', sl['part']):
            continue
        native_v = s.get('_src_aspect', 16 / 9) < 1.0
        theta = (11.0 if native_v else (15.0 if sl['part'] == 'hook' else 12.0)) * sign
        S = math.cos(math.radians(abs(theta))) + (1.78 if native_v else 0.5625) * math.sin(math.radians(abs(theta)))
        s['crop']['rot'] = round(theta, 2)
        _crop_cover(s, S)
        P._log(si, 'angle.dutch', 0, f'digital dutch tilt {theta:+.0f}°, crop cover ×{S:.2f}')
        sign = -sign
    # ---- build
    inout_left = 2
    for si, s in enumerate(segs):
        sl = P.slots_by_seg[si]
        if sl['part'] != 'build' or sl['kind'] == 'stutter':
            continue
        for b in P.beats_in(si):
            k = b['f'] - s['f0']
            if b['pos'] in (1, 3):
                if P.ok('fx.rgb_split', 'build'):
                    P.fx(si, 'fx.rgb_split', dict(type='rgb_split', frames=[k], **P_RGB['micro']), k, 'micro RGB 3 px on the snare', 'rgb')
                if inout_left > 0 and k > 0 and k + int(0.5 * P.period * fps) <= s['f1'] - s['f0'] and P.ok('zoom.in_out', 'build'):
                    P.fx(si, 'zoom.in_out', dict(type='zoom.in_out', frames=[k], scale=1.3, stroke=round(P.period / 2, 3),
                                                  ease=['outCubic', 'inCubic'], hold=0, center=_center(s)), k, 'zoom in-and-out ×1.3 on the snare', 'punch')
                    inout_left -= 1
    stut = [si for si, s in enumerate(segs) if P.slots_by_seg[si]['kind'] == 'stutter']
    for si in stut:
        if P.ok('cut.stutter', 'build'):
            s = segs[si]
            P._log(si, 'cut.stutter', 0, 'stutter 1/16 × 8 on the last 2 beats of the build')
            if P.ok('sfx.glitch', 'build'):
                P.sfx('sfx.glitch', 'glitch', s['f0'] / fps, 'track stutter 1/16 under the stutter cut (replaces the music)', variant='stutter',
                      align='attack', dur=round((s['f1'] - s['f0'] + 1) / fps, 3),
                      params=dict(slice='1/16', repeats=int(round((s['f1'] - s['f0'] + 1) / fps / (P.period / 4))), xfade_ms=2))
    # riser before the drop only if the track does not rise by itself
    d_t0 = pt['drop']['t0']
    if P.ok('sfx.riser', 'build') and P.rise_db < 3.0:
        bar = 4 * P.period
        P.sfx('sfx.riser', 'riser', d_t0, f'the track does not build by itself (+{P.rise_db:.1f} dB over 2 bars)', variant='noise', align='peak',
              dur=round(2 * bar, 3), rel_lu=-6, params=dict(roll=True))
    elif P.rise_db >= 3.0:
        P.skip('sfx.riser', f'the track rises by itself by {P.rise_db:.1f} dB over the 2 bars before the drop', 'build')
    # ---- drop
    drop_segs = [si for si, s in enumerate(segs) if P.slots_by_seg[si]['part'] == 'drop']
    if drop_segs:
        fd = drop_segs[0]
        P.multi_ok.add(segs[fd]['f0'])
        if P.ok('trans.flash', 'drop'):
            P.transition(fd, 'trans.flash', dict(kind='flash', frames=len(_exp_curve(0.06, fps, 2)), align='end',
                                                 params=dict(color='#ffffff', mode='solid', peak_frames=2, pre_frames=0, tau=0.06,
                                                             cutoff=0.05, curve=_exp_curve(0.06, fps, 2))),
                         'first beat of the drop: 2-frame flash')
            P.acc.setdefault(segs[fd]['f0'], []).append('flash')
        if P.ok('shake.beat', 'drop'):
            P.fx(fd, 'shake.beat', dict(type='shake.beat', frames=[0], **P_SHAKE['heavy'], seed=1), 0, 'first beat of the drop: heavy shake', 'shake')
        if P.ok('fx.rgb_split', 'drop'):
            P.fx(fd, 'fx.rgb_split', dict(type='rgb_split', frames=[0], **P_RGB['heavy']), 0, 'first beat of the drop: RGB 16 px', 'rgb')
        nb = P.beats_in(fd, inner=True)
        if nb and P.ok('zoom.punch', 'drop'):
            k = nb[0]['f'] - segs[fd]['f0']
            P.fx(fd, 'zoom.punch', dict(type='zoom.punch', frames=[k], **P_PUNCH['strong'], center=_center(segs[fd])), k,
                 'no punch on the cut beat — punch on the next beat', 'punch')
        if P.ok('sfx.impact', 'drop'):
            # the card's "click only through a 150 Hz high-pass" stayed under the program (QA: weak hit); the mixer's mud
            # guard already moves the hit's body above a strong 808 kick on that beat, so the hit keeps its body
            P.sfx('sfx.impact', 'impact', segs[fd]['f0'] / fps, 'hit on the first beat of the drop (mud guard: the 808 keeps the lows)',
                  variant='punch', align='attack', rel_lu=-10)
    # alternate per bar: shake on kicks / punches on inner beats; RGB on snares; flashes on downbeat cuts
    d_bar0 = pt['drop']['beat0'] // 4
    cuts_drop = [si for si in drop_segs[1:] if P.slots_by_seg[si]['kind'] != 'burst']
    n_flash_max = int(0.4 * max(1, len(drop_segs) - 1))
    n_flash = 0
    rgb_sign = 1
    crash_done = False
    for si in drop_segs:
        s = segs[si]
        sl = P.slots_by_seg[si]
        if sl['kind'] == 'burst':
            continue
        for b in P.beats_in(si):
            k = b['f'] - s['f0']
            if b['f'] in P.multi_ok:
                continue
            bar_rel = b['bar'] - d_bar0
            if bar_rel % 2 == 0:
                if P.ok('shake.beat', 'drop') and b['kick'] >= 0.35:
                    P.fx(si, 'shake.beat', dict(type='shake.beat', frames=[k], **P_SHAKE['impact'], seed=b['j']), k,
                         f'impact shake on the kick (bar {bar_rel + 1} of the drop)', 'shake')
            elif k > 0 and P.ok('zoom.punch', 'drop'):
                prm = P_PUNCH['strong'] if b['pos'] == 0 else P_PUNCH['bounce']
                P.fx(si, 'zoom.punch', dict(type='zoom.punch', frames=[k], **prm, center=_center(s)), k,
                     f'bounce punch ×{prm["scale"]} (shake bars alternate with punch bars)', 'punch')
            if b['pos'] in (1, 3) and P.ok('fx.rgb_split', 'drop'):
                prm = dict(P_RGB['normal'])
                prm['angle'] = 0 if rgb_sign > 0 else 180
                rgb_sign = -rgb_sign
                P.fx(si, 'fx.rgb_split', dict(type='rgb_split', frames=[k], **prm), k, 'RGB 10 px on the snare, alternating direction', 'rgb')
        if si in cuts_drop and n_flash < n_flash_max:
            b = next((x for x in beats if x['f'] == s['f0']), None)
            if b and b['pos'] == 0 and P.ok('trans.flash', 'drop'):
                if P.transition(si, 'trans.flash', dict(kind='flash', frames=len(_exp_curve(0.06, fps)), align='end',
                                                        params=dict(color='#ffffff', mode='solid', peak_frames=1, pre_frames=0,
                                                                    tau=0.06, cutoff=0.05, curve=_exp_curve(0.06, fps))),
                                '1-frame flash on a downbeat cut'):
                    n_flash += 1
                    P.acc.setdefault(s['f0'], []).append('flash')
    # zoom.crash: one per 8 bars, second half of the drop, lands on a downbeat inside its clip (≥ 0.4 s of run-up)
    if P.ok('zoom.crash', 'drop'):
        order = [si for si in drop_segs if P.slots_by_seg[si].get('crash')] + [si for si in drop_segs if not P.slots_by_seg[si].get('crash')]
        for si in order:
            s = segs[si]
            if P.slots_by_seg[si]['kind'] == 'burst':
                continue
            land = [b for b in P.beats_in(si, inner=True) if b['pos'] == 0 and b['f'] - s['f0'] >= int(0.4 * fps)]
            if not land:
                continue
            b = land[0]
            k1 = b['f'] - s['f0']
            k0 = k1 - int(round(0.4 * fps))
            t1 = round(b['f'] / fps, 4)
            gone = [x for x in s.get('fx', []) if x['type'] in ('zoom.punch', 'shake.beat') and any(abs(t - t1) < 0.5 / fps for t in x.get('times', []))]
            s['fx'] = [x for x in s.get('fx', []) if x not in gone]
            for x in gone:
                P.count[x['move']] -= 1
            P.slots_by_seg[si]['moves'] = [m for m in P.slots_by_seg[si].get('moves', []) if not (m['k'] == k1 and m['id'] in ('zoom.punch', 'shake.beat'))]
            P.acc[b['f']] = [a for a in P.acc.get(b['f'], []) if a not in ('punch', 'shake')]
            Wc = (P.slots_by_seg[si].get('pick') or {}).get('W', {})
            has_face = bool(Wc) and _face_ok(Wc, 0.1, 50)
            sc_ = _crash_scale(P, si, 3.5 if has_face else 2.5)
            P.fx(si, 'zoom.crash', dict(type='zoom.crash', frames=[k0], scale=sc_, dur=0.4, ease='inOutCubic', blur_shutter=0.5,
                                        center=_center(s)), k0, f'crash zoom ×{sc_} over 0.4 s {"into a face" if has_face else "into a detail"}, landing on the downbeat', None)
            P.acc.setdefault(b['f'], []).append('crash')
            if P.ok('sfx.whoosh', 'drop'):
                P.sfx('sfx.whoosh', 'whoosh', b['f'] / fps, 'whoosh under the crash zoom, peak on the landing', variant='air', align='peak', dur=0.7, rel_lu=-6)
            crash_done = True
            break
        if not crash_done:
            P.skip('zoom.crash', 'no clip with a downbeat inside (needs a run-up ≥ 0.4 s)', 'drop')
    # fx.glitch: bursts on fills at phrase ends, ≤ 1 per 2 bars
    if P.ok('fx.glitch', 'drop'):
        last_bar = -10
        for b in beats:
            if b['part'] != 'drop' or b['pos'] != 3 or b['fill'] < 0.25 or b['bar'] - last_bar < 2:
                continue
            si = P.seg_at(b['f'])
            if si is None or P.slots_by_seg[si]['kind'] == 'burst':
                continue
            k = b['f'] - segs[si]['f0']
            if P.n_acc(b['f']) >= 2:
                continue
            if P.fx(si, 'fx.glitch', dict(type='glitch_blocks', frames=list(range(k, min(k + 3, segs[si]['f1'] - segs[si]['f0'] + 1))),
                                           kinds=['slices', 'rgb', 'blocks'], intensity=0.6, hold=1), k, '3-frame glitch on the track fill', 'glitch'):
                last_bar = b['bar']
                if P.ok('sfx.glitch', 'drop'):
                    P.sfx('sfx.glitch', 'glitch', b['t'], 'burst in sync with fx.glitch', variant='burst', align='attack',
                          dur=round(3 / fps, 3), rel_lu=-6)
    # velocity: motion blur on fast frames (time.velocity / time.motion_blur)
    for si in drop_segs:
        if segs[si].get('_mode') == 'velocity':
            P._log(si, 'time.velocity', 0, 'velocity: r̄ 2.5, m 0.85, inOutCubic, anchors on beats')
            segs[si].setdefault('fx', []).append(dict(type='motion_blur', mode='frames', shutter=0.5, adaptive='rate', min_rate=1.2,
                                                      move='time.velocity'))
    if any(P.slots_by_seg[si]['kind'] == 'burst' for si in drop_segs):
        bs = [si for si in drop_segs if P.slots_by_seg[si]['kind'] == 'burst']
        if P.ok('cut.quick', 'drop'):
            P._log(bs[0], 'cut.quick', 0, f'1/8 burst × {len(bs)} on the densest bar of the drop')
    # ---- outro: ramp into the freeze on the last hit, heavy shake + RGB 20 px, black tail, music stop
    fr = [si for si, s in enumerate(segs) if P.slots_by_seg[si]['kind'] == 'freeze']
    if fr:
        si = fr[0]
        s = segs[si]
        sl = P.slots_by_seg[si]
        fhit = frame_at(pt['outro']['t0'], fps)
        k = fhit - s['f0']
        P.multi_ok.add(fhit)
        P._log(si, 'time.speed_ramp', 0, 'ramp 1.0 → 0.2 into the freeze')
        P._log(si, 'time.freeze', k, 'freeze frame on the last hit')
        if P.ok('shake.beat', 'outro'):
            P.fx(si, 'shake.beat', dict(type='shake.beat', frames=[k], **P_SHAKE['heavy'], seed=99), k, 'heavy shake on the freeze frame', 'shake')
        if P.ok('fx.rgb_split', 'outro'):
            P.fx(si, 'fx.rgb_split', dict(type='rgb_split', frames=[k], **P_RGB['extreme']), k, 'RGB 20 px on the freeze', 'rgb')
        if sl.get('black_from') is not None:
            fb = frame_at(P.beat_time(sl['black_from']), fps)
            _black_ops(P, fb, P.e['n_frames'] - 1, mid='trans.fade', why='hard cut to black on the 808 tail')
            P.planned_black += list(range(fb, P.e['n_frames']))
        P.planned_freeze.append([fhit, s['f1']])
        if P.ok('sfx.impact', 'outro'):
            P.sfx('sfx.impact', 'impact', pt['outro']['t0'], 'stop hit: the music cuts out until the end of the video', variant='stop',
                  align='attack', rel_lu=-6, params=dict(stop=round(P.T - pt['outro']['t0'], 3)))
    # hook impact only on a cold start (no kick on the first hit)
    if P.ok('sfx.impact', 'hook') and beats[0]['kick'] < 0.3:
        P.sfx('sfx.impact', 'impact', 0.0, 'cold start without a kick', variant='boom', align='attack', rel_lu=-4)


def program_epic(P):
    g, fps, segs, beats, pt = P.g, P.fps, P.segs, P.beats, P.parts
    T = P.T
    for si in range(len(segs)):                      # "Color": vignette 15–25 % towards the edges
        segs[si].setdefault('fx', []).append(dict(type='vignette', amount=0.2, shape='ellipse', move='grade'))
    if P.heterogeneous and P.ok('fx.film_overlay'):
        for si in range(len(segs)):
            P.fx(si, 'fx.film_overlay', dict(type='film_overlay', level=1, delivery='social'), None,
                 'mixed sources: level-1 grain glues them together')
    # ---- hook: open from black, letterbox in, zoom.out reveal, title
    hook = [si for si in range(len(segs)) if P.slots_by_seg[si]['part'] == 'hook']
    if hook and P.ok('trans.fade', 'hook'):
        nf = 9 if fps >= 30 else 8
        P.transition(hook[0], 'trans.fade', dict(kind='fade', frames=nf, align='end', params=dict(color='#000000', mode='in', in_frames=nf,
                                                                                                  curve=['linear', 'outQuad'])),
                     'open from black ≤ 9 frames')
    lb = P.ok('fx.letterbox', 'hook')
    lb_hook = (0.0, min(2.0, pt['hook']['t1']))
    t_drop = pt['drop']['t0']
    for si, s in enumerate(segs):
        part = P.slots_by_seg[si]['part']
        t0, t1 = s['f0'] / fps, (s['f1'] + 1) / fps
        if not lb:
            break
        if part == 'hook':
            P.fx(si, 'fx.letterbox', _letterbox_fx(lb_hook, (0.5625, 0.8)), None, 'bars close in 9:16 → 4:5 over 2 s')
        elif part == 'build':
            P.fx(si, 'fx.letterbox', _letterbox_fx((t0, t1), (0.8, 0.8)), None, '4:5 bars hold')
        elif part == 'drop' and t0 < t_drop + 1.5:
            P.fx(si, 'fx.letterbox', _letterbox_fx((t_drop, t_drop + 1.5), (0.8, 0.5625)), None, 'bars open 4:5 → 9:16 over 1.5 s')
        elif part == 'outro':
            to = pt['outro']['t0']
            P.fx(si, 'fx.letterbox', _letterbox_fx((to, to + 2.0), (0.5625, 1.0)), None, 'bars close 9:16 → 1:1 over 2 s')
    for n, si in enumerate(hook):
        s = segs[si]
        W = (P.slots_by_seg[si].get('pick') or {}).get('W', {})
        static = W.get('pan', 0) <= 0.5 and W.get('jitter', 0) <= 0.3
        if n == 0 and static and P.ok('zoom.out', 'hook'):
            _crop_zoom(s, 1.3, 1.0, 'linear')
            P._log(si, 'zoom.out', 0, 'reveal: crop ×1.3 → 1.0 over the shot')
        elif static and P.ok('zoom.slow'):
            _crop_zoom(s, 1.0, 1.08, 'linear')
            P._log(si, 'zoom.slow', 0, 'slow zoom-in ×1.08 on a static shot')
        lab = 'shot.extreme_wide' if W.get('ews') else None
        if lab:
            P._log(si, lab, 0, 'extreme wide shot from the source footage')
    if P.title and P.ok('type.title_card', 'hook'):
        tb = next((b for b in beats if b['pos'] == 0 and b['bar'] == 1), None)
        if tb:
            P.layer('type.title_card', dict(kind='title_card', f0=tb['f'], f1=min(P.e['n_frames'] - 1, tb['f'] + int(1.9 * fps)),
                                            lines=[dict(role='title', text=P.title.upper())], text=P.title.upper(), layout='center_block',
                                            type_class='grotesk_extended', font='grotesk_extended', caps=True,
                                            size={'fit_width': 0.76, 'max': 0.055, 'min': 0.03}, tracking=0.3, color='#F2EDE4',
                                            pos=[0.48, 0.45], anim_in=dict(kind='fade', dur=0.6, ease='outQuad'),
                                            anim_out=dict(kind='fade', dur=0.75), safe_zone='tiktok'),
                    'title on the downbeat of bar 2, 1.9 s, inside the 4:5 bars')
    if hook and P.ok('sfx.impact', 'hook') and beats[0]['onset'] < 0.9:
        P.sfx('sfx.impact', 'impact', 0.0, 'low hit on the first downbeat', variant='boom', align='attack', rel_lu=-2)
    # ---- build: zoom.slow on static shots ≥ 2 s, trailer pulse dips, black breath, riser
    for si, s in enumerate(segs):
        sl = P.slots_by_seg[si]
        if sl['part'] != 'build' or sl['kind'] != 'shot':
            continue
        W = (sl.get('pick') or {}).get('W', {})
        dur = (s['f1'] - s['f0'] + 1) / fps
        if dur >= 1.9 and W.get('pan', 0) <= 0.5 and P.ok('zoom.slow', 'build'):
            _crop_zoom(s, 1.0, 1.1, 'linear')
            P._log(si, 'zoom.slow', 0, 'zoom-in ×1.1 on a static shot ≥ 2 s')
        if sl['speed']['mode'] == 'slow':
            P._log(si, 'time.slow_motion', 0, f'slow motion {sl["speed"]["rate"]} in the first half of the build')
        if W.get('low_angle'):
            P._log(si, 'angle.low', 0, 'low angle from the source footage')
        if sl.get('dip') and P.ok('trans.fade', 'build'):
            P.transition(si, 'trans.fade', dict(kind='dip', frames=10, align='center', params=dict(color='#000000', out_frames=3,
                                                                                                    hold_frames=2, in_frames=5)),
                         'trailer pulse: dip to black on the beat')
            P.planned_black += [s['f0'] - 1, s['f0']]
            if P.ok('sfx.impact', 'build') and P.n_build_impacts < 3:
                P.sfx('sfx.impact', 'impact', s['f0'] / fps, '"punch" hit in the black of the dip', variant='punch', align='attack', rel_lu=-6)
                P.n_build_impacts += 1
    for si, s in enumerate(segs):
        if P.slots_by_seg[si]['kind'] == 'black':
            _black_ops(P, s['f0'], s['f1'], mid='trans.fade', why='black breath pause before the drop')
            P.planned_black += list(range(s['f0'], s['f1'] + 1))
            P._log(si, 'trans.fade', 0, '1-beat black pause before the drop')
    if P.ok('sfx.riser', 'build') and t_drop >= 4 * P.period:
        if P.rise_db < 3.0:
            P.sfx('sfx.riser', 'riser', t_drop - P.period / 4, f'the track does not build by itself (+{P.rise_db:.1f} dB)', variant='noise', align='peak',
                  dur=round(min(8 * P.period, t_drop - P.period / 4), 3), rel_lu=-6, params=dict(roll=True))
        else:
            P.skip('sfx.riser', f'the track rises by itself by {P.rise_db:.1f} dB over the 2 bars before the drop', 'build')
    # ---- drop
    drop = [si for si in range(len(segs)) if P.slots_by_seg[si]['part'] == 'drop']
    if drop:
        fd = drop[0]
        P.multi_ok.add(segs[fd]['f0'])
        if P.slots_by_seg[fd]['speed']['mode'] == 'slow':
            P._log(fd, 'time.slow_motion', 0, f'best shot of the video in slow motion {P.slots_by_seg[fd]["speed"].get("rate")} for a whole bar')
        if P.ok('trans.flash', 'drop'):
            P.transition(fd, 'trans.flash', dict(kind='flash', frames=len(_exp_curve(0.06, fps, 2)), align='end',
                                                 params=dict(color='#ffffff', mode='solid', peak_frames=2, pre_frames=0, tau=0.06,
                                                             cutoff=0.05, curve=_exp_curve(0.06, fps, 2))),
                         'out of black — white flash, 2-frame peak')
            P.acc.setdefault(segs[fd]['f0'], []).append('flash')
        if P.ok('shake.beat', 'drop'):
            prm = dict(P_SHAKE['heavy'])
            prm['amp'] = 0.045
            P.fx(fd, 'shake.beat', dict(type='shake.beat', frames=[0], **prm, seed=1), 0, 'the only heavy shake of the video', 'shake')
        if P.ok('sfx.sub_drop', 'drop'):
            P.sfx('sfx.sub_drop', 'sub_drop', t_drop, 'sub drop on the first beat (−3 dB from the norm when paired)', variant='classic', align='attack',
                  rel_lu=-9)
        if P.ok('sfx.impact', 'drop'):
            P.sfx('sfx.impact', 'impact', t_drop, 'boom on the first beat of the drop', variant='boom', align='attack', rel_lu=-5)
        # main hits: flashes ≤ 3 per 10 s and ≤ 25 % of drop cuts; impact shake ≤ 1 per bar
        n_cuts = max(1, len(drop) - 1)
        flash_left = max(0, min(int(0.25 * n_cuts), int(3 * (pt['drop']['t1'] - pt['drop']['t0']) / 10)))
        shake_bars = set()
        cands = sorted([si for si in drop[1:]], key=lambda si: -max((b['kick'] + b['onset'] for b in P.beats_in(si) if b['f'] == segs[si]['f0']),
                                                                   default=0))
        for si in cands:
            s = segs[si]
            sl = P.slots_by_seg[si]
            b = next((x for x in beats if x['f'] == s['f0']), None)
            if b is None:
                continue
            if flash_left > 0 and b['pos'] == 0 and P.ok('trans.flash', 'drop'):
                if P.transition(si, 'trans.flash', dict(kind='flash', frames=len(_exp_curve(0.06, fps)), align='end',
                                                        params=dict(color='#ffffff', mode='solid', peak_frames=1, pre_frames=0,
                                                                    tau=0.06, cutoff=0.05, curve=_exp_curve(0.06, fps))),
                                '1-frame flash on a main hit'):
                    flash_left -= 1
                    P.acc.setdefault(s['f0'], []).append('flash')
            if b['bar'] not in shake_bars and sl['role'] != 'drop_wide' and P.ok('shake.beat', 'drop'):
                if P.fx(si, 'shake.beat', dict(type='shake.beat', frames=[0], **dict(P_SHAKE['impact'], amp=0.02), seed=b['j']), 0,
                        'impact shake 2 % on a main hit (≤ 1 per bar)', 'shake'):
                    shake_bars.add(b['bar'])
        for si in drop:
            sl = P.slots_by_seg[si]
            if sl['speed']['mode'] == 'ramp':
                sp = sl['speed']
                P._log(si, 'time.speed_ramp', 0, f'ramp ×{sp.get("fast", 2.2)} → {sp.get("slow", 0.35)}, slow motion from the beat at the '
                                                 f'action peak' + (' → fast into the next cut' if sp.get('exit') else ''))
            if sl['role'] == 'drop_wide':
                P._log(si, 'time.slow_motion', 0, 'last bar of the drop — wide shot in slow motion')
            W = (sl.get('pick') or {}).get('W', {})
            if W.get('low_angle'):
                P._log(si, 'angle.low', 0, 'hero from a low angle')
    # ---- outro: zoom.out, letterbox closes, final card, fade to black on the last note
    outro = [si for si in range(len(segs)) if P.slots_by_seg[si]['part'] == 'outro']
    for si in outro:
        if P.slots_by_seg[si]['speed']['mode'] in ('ramp', 'velocity'):
            continue                                  # a ramp already moves the shot; a pull-out on top is noise
        if P.ok('zoom.out', 'outro'):
            _crop_zoom(segs[si], 1.6, 1.0, 'outCubic')
            P._log(si, 'zoom.out', 0, 'pull-out: scale 1.6 → 1.0, outCubic')
    if outro and P.ok('trans.fade', 'outro'):
        f_end = P.e['n_frames'] - 1
        fb = frame_at(T - 0.5, fps)
        fa = frame_at(T - 1.75, fps)
        _black_ops(P, fa, fb - 1, 0.0, 1.0, why='fade to black 1.25 s on the last note')
        _black_ops(P, fb, f_end, why='black holds 0.5 s')
        P.planned_black += list(range(fb, f_end + 1))
        P.e['audio']['music']['fade_out'] = round(T - (fa / fps), 3)
        P._log(outro[-1], 'trans.fade', None, 'fade to black and the music down to −60 dB')
    if outro and P.outro_text and P.ok('type.title_card', 'outro'):
        f0 = frame_at(pt['outro']['t0'] + 0.5, fps)
        P.layer('type.title_card', dict(kind='title_card', f0=f0, f1=frame_at(T - 0.6, fps), text=P.outro_text.upper(),
                                        lines=[dict(role='title', text=P.outro_text.upper())], layout='center_block',
                                        type_class='grotesk_extended', font='grotesk_extended', caps=True,
                                        size={'fit_width': 0.76, 'max': 0.045, 'min': 0.03}, tracking=0.3, color='#F2EDE4',
                                        pos=[0.48, 0.46], anim_in=dict(kind='fade', dur=0.75, ease='outQuad'), anim_out=dict(kind='cut'),
                                        safe_zone='tiktok'), 'end card inside the bars, leaves with the fade to black')
    if outro and P.ok('sfx.impact', 'outro'):
        P.sfx('sfx.impact', 'impact', pt['outro']['t0'], 'stretched boom on the last phrase', variant='stretched', align='attack', rel_lu=-5)


def program_calm(P):
    g, fps, segs, beats, pt = P.g, P.fps, P.segs, P.beats, P.parts
    T = P.T
    for si in range(len(segs)):
        segs[si].setdefault('fx', []).append(dict(type='bloom', thr=0.8, r=48, strength=0.15, move='grade'))   # "Color": highlight glow
        if P.ok('fx.film_overlay'):
            P.fx(si, 'fx.film_overlay', dict(type='film_overlay', level=2, delivery='social', grain=6, size=2.2, corr=0.8, dust=4,
                                               flicker=0.015, weave=2), None, 'film level 2 (grain σ 6, 2.2 px) from the first frame to the end')
    if segs and P.ok('trans.fade', 'outro'):
        P.transition(0, 'trans.fade', dict(kind='fade', frames=12, align='end', params=dict(color='#000000', mode='in', in_frames=12,
                                                                                            curve=['linear', 'outQuad'])),
                     'open from black 0.4 s')
    direction = 1
    for si, s in enumerate(segs):
        sl = P.slots_by_seg[si]
        W = (sl.get('pick') or {}).get('W', {})
        dur = (s['f1'] - s['f0'] + 1) / fps
        if si > 0 and P.ok('trans.dissolve', sl['part']):
            n = s['f1'] - s['f0'] + 1
            prev_n = segs[si - 1]['f1'] - segs[si - 1]['f0'] + 1
            sec = 2.0 if sl['role'] == 'drop_first' else (1.75 if sl['part'] in ('drop', 'outro') else 1.25)
            fr = int(min(sec * fps, 0.8 * min(n, prev_n)))
            fr -= fr % 2
            P.transition(si, 'trans.dissolve', dict(kind='dissolve', frames=fr, align='center', params=dict(curve='inOutSine')),
                         f'dissolve {fr / fps:.2f} s, centered on the downbeat')
        if sl['part'] == 'outro' and sl['role'] == 'outro' and P.ok('zoom.out', 'outro'):
            _crop_zoom(s, 1.15, 1.0, 'linear')
            P._log(si, 'zoom.out', 0, 'slow zoom-out ×1.15 → 1.0 over the whole shot')
        elif P.ok('zoom.slow'):
            rate = 1.08 if sl['role'] in ('drop_first', 'hook') else 1.06
            z0, z1 = (1.0, rate) if direction > 0 else (rate, 1.0)
            if sl['role'] == 'drop_first':
                z0, z1 = 1.0, 1.1
            _crop_zoom(s, z0, z1, 'linear')
            P._log(si, 'zoom.slow', 0, f'slow {"zoom-in" if z1 > z0 else "zoom-out"} ×{max(z0, z1):.2f} over the shot ({dur:.1f} s)')
            direction = -direction
        if sl['part'] == 'build' and P.ok('light.haze', 'build'):
            gr = s.setdefault('grade', {})
            gr['lift'] = round(gr.get('lift', 0.0) + 0.04, 3)
            gr['sat'] = round(gr.get('sat', 1.0) * 0.85, 3)
            P.fx(si, 'light.haze', dict(type='glow', threshold=0.7, strength=0.2, radii=[0.01, 0.03, 0.06, 0.1]), None,
                 'haze of one strength per episode: black lift +0.04, saturation ×0.85, diffusion')
        if sl['part'] == 'build' and W.get('size') in ('wide', 'wide/no-face') and W.get('static', 0) > 0.5 and P.ok('pan.basic', 'build'):
            cr = s['crop']
            if cr.get('path'):
                n = s['f1'] - s['f0'] + 1
                shift = 0.03 * dur * (s.get('_win_w') or 0.32)
                cr['path'] = [[p[0], round(min(0.98, max(0.02, p[1] + shift * (p[0] / max(n - 1, 1) - 0.5))), 4), p[2], p[3]] for p in cr['path']]
                P._log(si, 'pan.basic', 0, 'slow pan 3 % of the width per second')
        if sl['role'] == 'drop_first':
            if sl['speed']['mode'] == 'slow':
                P._log(si, 'time.slow_motion', 0, f'gentle slow motion {sl["speed"]["rate"]}')
            if W.get('p99', 0) >= 225 and P.ok('light.halation', 'drop'):
                P.fx(si, 'light.halation', dict(type='glow', threshold=0.85, knee=0.1, strength=[0.15, 0.35],
                                                t=[round(s['f0'] / fps, 3), round(s['f0'] / fps + 1.2, 3)], ease='inOutQuad',
                                                radii=[0.006, 0.015, 0.03, 0.06], tint='#ff5a1a', tint_mix=0.45, blend='screen'),
                     None, 'highlight glow rises 0.15 → 0.35 over 1.2 s into the climax (red halation wider)')
            elif P.ok('light.halation', 'drop'):
                P.skip('light.halation', 'the best shot has no highlights (p99 < 225)', 'drop')
            if P.ok('sfx.riser', 'drop'):
                if P.rise_db < 3.0:
                    P.sfx('sfx.riser', 'swell', s['f0'] / fps, 'swell, peak at the middle of the dissolve into the best shot', variant='swell', align='peak',
                          dur=2.0, rel_lu=-10)
                else:
                    P.skip('sfx.riser', f'the track opens up by itself (+{P.rise_db:.1f} dB over 2 bars)', 'drop')
    # text: 0–3 quiet lines (title / place in the hook, a caption in the outro), thin type, top third, ≥ 3 s, fades ~1 s
    for txt, part, y in ((P.title, 'hook', 0.26), (P.outro_text, 'outro', 0.26)):
        if not txt or not P.ok('type.title_card', part):
            continue
        b0 = next((b for b in beats if b['part'] == part and b['pos'] in (0, 2) and b['t'] >= pt[part]['t0'] + (0.5 if part == 'hook' else 1.0)), None)
        if b0 is None:
            continue
        f1 = min(frame_at(pt[part]['t1'], fps) - 1, b0['f'] + int(3.5 * fps))
        if part == 'outro':
            f1 = min(f1, frame_at(T - 2.6, fps))
        if (f1 - b0['f']) / fps < 2.5:
            continue
        P.layer('type.title_card', dict(kind='title_card', f0=b0['f'], f1=f1, text=txt, lines=[dict(role='title', text=txt)],
                                        layout='sky_top', type_class='grotesk_light_geo', font='grotesk_light_geo', caps=False,
                                        size={'fit_width': 0.7, 'max': 0.035, 'min': 0.025}, tracking=0.08, color='#F5EEDF', opacity=0.9,
                                        shadow=dict(dx=0, dy=0.01, blur=0.08, alpha=0.3, color='#000000'),   # card: soft shadow on light skies
                                        pos=[0.47, y], anim_in=dict(kind='fade', dur=1.0), anim_out=dict(kind='fade', dur=1.0),
                                        safe_zone='tiktok'),
                f'quiet on-screen text in the {part}: light grotesque 3.5 % H, upper third, 1 s fade-in, on the downbeat')
    if segs and P.ok('trans.fade', 'outro'):
        f_end = P.e['n_frames'] - 1
        fa = frame_at(T - 2.5, fps)
        _black_ops(P, fa, f_end, 0.0, 1.0, why='fade to black 2.5 s with the last note')
        P.planned_black += [f_end]
        P.e['audio']['music']['fade_out'] = 2.5
        P._log(len(segs) - 1, 'trans.fade', None, 'final fade to black 2.5 s, the music fades with the picture')


def program_generic(P):
    """Other genre cards: the generically implementable moves listed per part (and the signature), with the cards'
    common limits: punches on inner strong beats (≤ 1 per bar outside the drop), impact shake on drop kicks in
    alternating bars, flashes on downbeat cuts (≤ 40 %), RGB on drop snares, one crash per 8 bars, whip / zoom
    transitions ≤ 1 per 2 bars with a whoosh, glow, film texture, fades, slow zooms, ramps / freeze / burst logs."""
    g, fps, segs, beats, pt = P.g, P.fps, P.segs, P.beats, P.parts
    pm, sig = g['part_moves'], set(g['signature'])
    lst = lambda part: set(pm.get(part, [])) | (sig & set(pm.get(part, [])))
    if P.ok('fx.film_overlay') and ('fx.film_overlay' in sig or any('fx.film_overlay' in pm[p] for p in PARTS)):
        for si in range(len(segs)):
            P.fx(si, 'fx.film_overlay', dict(type='film_overlay', level=1), None, 'film texture per the genre card')
    if segs and 'trans.fade' in pm['hook']:
        P.transition(0, 'trans.fade', dict(kind='fade', frames=8, align='end', params=dict(color='#000000', mode='in', in_frames=8)),
                     'open from black')
    drop = [si for si in range(len(segs)) if P.slots_by_seg[si]['part'] == 'drop']
    d_bar0 = pt['drop']['beat0'] // 4
    if drop:
        fd = drop[0]
        P.multi_ok.add(segs[fd]['f0'])
        if 'trans.flash' in lst('drop') and P.ok('trans.flash', 'drop'):
            P.transition(fd, 'trans.flash', dict(kind='flash', frames=len(_exp_curve(0.06, fps, 2)), align='end',
                                                 params=dict(color='#ffffff', mode='solid', peak_frames=2, tau=0.06,
                                                             curve=_exp_curve(0.06, fps, 2))), 'into the drop: 2-frame flash')
            P.acc.setdefault(segs[fd]['f0'], []).append('flash')
        if 'shake.beat' in lst('drop') and P.ok('shake.beat', 'drop'):
            P.fx(fd, 'shake.beat', dict(type='shake.beat', frames=[0], **P_SHAKE['heavy'], seed=1), 0, 'into the drop: heavy shake', 'shake')
        if P.ok('sfx.impact', 'drop'):
            P.sfx('sfx.impact', 'impact', segs[fd]['f0'] / fps, 'hit on the first beat of the drop', variant='punch', align='attack', rel_lu=-6)
        if P.ok('sfx.sub_drop', 'drop'):
            P.sfx('sfx.sub_drop', 'sub_drop', segs[fd]['f0'] / fps, 'sub drop on the first beat', variant='short', align='attack', rel_lu=-9)
    n_flash_max = int(0.4 * max(1, len(drop) - 1))
    n_flash, last_trick_bar, rgb_sign = 0, -10, 1
    for si, s in enumerate(segs):
        sl = P.slots_by_seg[si]
        part = sl['part']
        L = lst(part)
        dur = (s['f1'] - s['f0'] + 1) / fps
        W = (sl.get('pick') or {}).get('W', {})
        if sl['kind'] == 'black':
            continue
        if 'zoom.slow' in L and dur >= 1.9 and W.get('pan', 0) <= 0.5 and P.ok('zoom.slow', part):
            _crop_zoom(s, 1.0, 1.08)
            P._log(si, 'zoom.slow', 0, 'slow zoom-in ×1.08 on a static shot')
        if 'zoom.out' in L and part == 'outro' and sl['kind'] == 'shot' and P.ok('zoom.out', part):
            _crop_zoom(s, 1.3, 1.0, 'outCubic')
            P._log(si, 'zoom.out', 0, 'zoom-out ×1.3 → 1.0 at the end')
        if 'fx.glow' in L and part in ('hook', 'outro') and P.ok('fx.glow', part):
            P.fx(si, 'fx.glow', dict(type='glow', threshold=0.72, strength=0.3), None, 'highlight glow')
        if si > 0 and 'trans.dissolve' in L and P.ok('trans.dissolve', part):
            fr = int(min(1.0 * fps, 0.6 * min(s['f1'] - s['f0'] + 1, segs[si - 1]['f1'] - segs[si - 1]['f0'] + 1)))
            P.transition(si, 'trans.dissolve', dict(kind='dissolve', frames=max(2, fr - fr % 2), align='center', params=dict(curve='linear')),
                         'dissolve')
        if sl['kind'] == 'burst':
            continue
        for b in P.beats_in(si, inner=True):
            k = b['f'] - s['f0']
            bar_rel = b['bar'] - d_bar0
            if part == 'hook' and 'zoom.punch' in L and b['pos'] in (0, 2) and k >= int(0.3 * fps) and not any(m['id'] == 'zoom.punch' for m in sl.get('moves', [])):
                if P.ok('zoom.punch', part):
                    P.fx(si, 'zoom.punch', dict(type='zoom.punch', frames=[k], **dict(P_PUNCH['hold'], scale=1.25), center=_center(s)), k,
                         'punch ×1.25 on the first downbeat inside the shot', 'punch')
            elif part == 'build' and 'zoom.punch' in L and b['pos'] == 1 and P.ok('zoom.punch', part):
                P.fx(si, 'zoom.punch', dict(type='zoom.punch', frames=[k], **P_PUNCH['bounce'], center=_center(s)), k, 'punch on the snare (≤ 1 per bar)', 'punch')
            elif part == 'build' and 'zoom.in_out' in L and b['pos'] == 3 and P.ok('zoom.in_out', part):
                P.fx(si, 'zoom.in_out', dict(type='zoom.in_out', frames=[k], scale=1.3, stroke=round(P.period / 2, 3), hold=0, center=_center(s)), k,
                     'zoom in-and-out on the snare', 'punch')
            if part != 'drop' or sl.get('crash'):
                continue
            both = 'zoom.punch' in L and 'shake.beat' in L
            if 'shake.beat' in L and (not both or bar_rel % 2 == 0) and b['kick'] >= 0.35 and P.ok('shake.beat', part):
                P.fx(si, 'shake.beat', dict(type='shake.beat', frames=[k], **P_SHAKE['impact'], seed=b['j']), k, 'shake on the kick', 'shake')
            elif 'zoom.punch' in L and (not both or bar_rel % 2 == 1) and P.ok('zoom.punch', part):
                prm = P_PUNCH['strong'] if b['pos'] == 0 else P_PUNCH['bounce']
                P.fx(si, 'zoom.punch', dict(type='zoom.punch', frames=[k], **prm, center=_center(s)), k, f'punch ×{prm["scale"]} on the beat', 'punch')
            if 'fx.rgb_split' in L and b['pos'] in (1, 3) and P.ok('fx.rgb_split', part):
                prm = dict(P_RGB['normal'], angle=0 if rgb_sign > 0 else 180)
                rgb_sign = -rgb_sign
                P.fx(si, 'fx.rgb_split', dict(type='rgb_split', frames=[k], **prm), k, 'RGB on the snare', 'rgb')
        cut_b = next((x for x in beats if x['f'] == s['f0']), None)
        if si > 0 and cut_b is not None and part in ('build', 'drop'):
            trick = [m for m in ('trans.whip', 'trans.zoom') if m in L and P.ok(m, part)]
            if trick and cut_b['pos'] == 0 and cut_b['bar'] - last_trick_bar >= 2 and not s.get('transition_in'):
                mid = trick[(cut_b['bar'] // 2) % len(trick)]
                prevW = (P.slots_by_seg[si - 1].get('pick') or {}).get('W', {})
                if mid == 'trans.whip':
                    dirn = 'left' if prevW.get('tx_end', 0) > 0 else 'right'
                    tr = dict(kind='whip', frames=6 if fps >= 30 else 5, align='center', params=dict(dir=dirn, shutter=0.7))
                else:
                    tr = dict(kind='zoom', frames=12, align='center', params=dict(out_scale=3, in_scale=1.5, mode='through'))
                if P.transition(si, mid, tr, f'{mid} on a downbeat cut (≤ 1 per 2 bars)'):
                    last_trick_bar = cut_b['bar']
                    if P.ok('sfx.whoosh', part):
                        P.sfx('sfx.whoosh', 'whoosh', s['f0'] / fps, f'whoosh under {mid}, peak on the cut', variant='air', align='peak', dur=0.5, rel_lu=-6)
                    continue
            if part == 'drop' and si != (drop[0] if drop else None) and 'trans.flash' in L and cut_b['pos'] == 0 and n_flash < n_flash_max \
                    and P.ok('trans.flash', part):
                if P.transition(si, 'trans.flash', dict(kind='flash', frames=len(_exp_curve(0.06, fps)), align='end',
                                                        params=dict(color='#ffffff', mode='solid', peak_frames=1, tau=0.06,
                                                                    curve=_exp_curve(0.06, fps))), 'flash on a downbeat cut'):
                    n_flash += 1
        mode = sl['speed']['mode']
        if mode == 'slow':
            P._log(si, 'time.slow_motion', 0, f'slow motion {sl["speed"]["rate"]}')
        elif mode == 'ramp':
            P._log(si, 'time.speed_ramp', 0, 'ramp ×2.2 → 0.35 from the beat')
        elif mode == 'velocity':
            P._log(si, 'time.velocity', 0, 'velocity: r̄ 2.5, m 0.85')
            s.setdefault('fx', []).append(dict(type='motion_blur', mode='frames', shutter=0.5, adaptive='rate', min_rate=1.2, move='time.velocity'))
        elif mode == 'ramp_freeze':
            fhit = frame_at(pt['outro']['t0'], fps)
            P._log(si, 'time.freeze', fhit - s['f0'], 'ramp into a freeze frame on the final beat')
            P.planned_freeze.append([fhit, s['f1']])
    for si in range(len(segs)):
        if P.slots_by_seg[si].get('loop_end') and P.ok('loop.end', 'outro'):
            P._log(si, 'loop.end', 0, 'the last shot is the same shot as the first, up to its start: a seamless loop')
    bursts = [si for si in drop if P.slots_by_seg[si]['kind'] == 'burst']
    if bursts and P.ok('cut.quick', 'drop'):
        P._log(bursts[0], 'cut.quick', 0, f'1/8 burst × {len(bursts)}')
    crash = [si for si in drop if P.slots_by_seg[si].get('crash')]
    if crash and P.ok('zoom.crash', 'drop'):
        si = crash[0]
        s = segs[si]
        land = [b for b in P.beats_in(si, inner=True) if b['pos'] == 0 and b['f'] - s['f0'] >= int(0.4 * fps)]
        if land:
            k1 = land[0]['f'] - s['f0']
            Wc = (P.slots_by_seg[si].get('pick') or {}).get('W', {})
            sc_ = _crash_scale(P, si, 3.5 if (bool(Wc) and _face_ok(Wc, 0.1, 50)) else 2.5)
            P.fx(si, 'zoom.crash', dict(type='zoom.crash', frames=[k1 - int(round(0.4 * fps))], scale=sc_, dur=0.4, ease='inOutCubic',
                                        blur_shutter=0.5, center=_center(s)), k1, f'crash zoom ×{sc_}, landing on the downbeat', None)
            if P.ok('sfx.whoosh', 'drop'):
                P.sfx('sfx.whoosh', 'whoosh', land[0]['f'] / fps, 'whoosh under the crash zoom', variant='air', align='peak', dur=0.7, rel_lu=-6)
    if P.ok('sfx.riser', 'build') and P.rise_db < 3.0 and drop:
        P.sfx('sfx.riser', 'riser', segs[drop[0]]['f0'] / fps, 'riser into the drop (the track does not build by itself)', variant='noise', align='peak',
              dur=round(8 * P.period, 3), rel_lu=-6)
    if segs and 'trans.fade' in pm['outro']:
        f_end = P.e['n_frames'] - 1
        fa = frame_at(P.T - 1.2, fps)
        _black_ops(P, fa, f_end, 0.0, 1.0, why='fade to black at the end')
        P.planned_black += [f_end]
        P.e['audio']['music']['fade_out'] = 1.2


PROGRAMS = {'phonk': program_phonk, 'epic': program_epic, 'calm': program_calm}


# ---------------------------------------------------------------------------- required moves / density / sound
def _required_speeds(slots, g, o, period):
    """Speed moves the user required: time.speed_ramp (every shot of an n_shots plan - the composite 'speed ramps on
    the drop' - else the drop shots of >= 2 beats, one per bar, at least one), time.slow_motion (the first drop shot),
    time.velocity (the drop shots). Required speeds survive the static-shot and budget rules."""
    req = set(g.get('required') or ())
    vis = [s for s in slots if s['kind'] == 'shot']
    if not vis or not req:
        return
    L = lambda s: s['b1'] - s['b0']   # noqa: E731
    if 'time.speed_ramp' in req:
        if o.get('n_shots'):
            targets = list(vis)
        else:
            targets, bars = [], set()
            for s in vis:
                if s['part'] == 'drop' and L(s) >= 2 - 1e-6 and s['speed']['mode'] in ('normal', 'ramp') and int(s['b0'] // 4) not in bars:
                    targets.append(s)
                    bars.add(int(s['b0'] // 4))
            if not targets:
                targets = [max(vis, key=L)]
        for s in targets:
            s['speed'] = ramp_speed(L(s), period, last=(s is vis[-1]), require=True)
    if 'time.slow_motion' in req:
        s = next((x for x in vis if x['role'] == 'drop_first'), None) or next((x for x in vis if x['part'] == 'drop'), vis[0])
        if s['speed']['mode'] == 'normal':
            s['speed'] = dict(mode='slow', rate=0.5, required=True)
    if 'time.velocity' in req:
        for s in vis:
            if s['part'] == 'drop' and s['speed']['mode'] == 'normal' and L(s) >= 1 - 1e-6:
                s['speed'] = dict(mode='velocity', required=True)


RAMP_PATTERNS = (    # brake beat, slow depth over the floor, fast in, braking / speed-up frames, exit, fast out
    dict(name='brake on 1, deep, exit', at_beat=1, depth=0.0, fast=2.4, dec=4, acc=4, exit=True, fast_out=2.6),
    dict(name='brake on 2, mid, snap out', at_beat=2, depth=0.05, fast=2.0, dec=6, acc=3, exit=True, fast_out=3.0),
    dict(name='brake on 1, light, hold', at_beat=1, depth=0.1, fast=2.2, dec=3, acc=5, exit=False, fast_out=None),
    dict(name='brake on 2, deep, long exit', at_beat=2, depth=0.0, fast=2.6, dec=5, acc=6, exit=True, fast_out=2.2),
)


def slow_floor(src_fps, interp=False):
    """Deepest slow motion a speed ramp brakes into: 0.4x from < 50 fps sources (the cards: deeper shows the
    synthesized frames), 0.25x from 50+ fps; interp=True (the user accepts optical-flow frames) allows 0.25x from
    any source."""
    return 0.25 if (interp or float(src_fps or 0) >= 50.0) else 0.4


def _ramp_patterns(slots, sty, o, floor=0.4):
    """Speed ramps never repeat a curve on adjacent shots: every ramp of the plan takes the next pattern of
    RAMP_PATTERNS (a version starts the rotation further on) - the brake beat (1st / 2nd inner beat), the slow depth
    (the floor, +0.05, +0.1), the fast-in rate, braking and speed-up frames, the exit (fast-slow-fast, or brake and
    hold into the cut) and its rate. A shot too short for the pattern brakes on beat 1; the last shot of the plan
    brakes and stays slow. -> [[slot, pattern, at_beat, fast, slow, dec, acc, exit_beat, fast_out]] (meta.choices)"""
    variant = int((sty or {}).get('variant') or o.get('variant') or 0)
    vis = [s for s in slots if s['kind'] == 'shot']
    last = vis[-1] if vis else None
    out, prev = [], None
    for j, s in enumerate([x for x in slots if (x.get('speed') or {}).get('mode') == 'ramp']):
        sp = s['speed']
        L = int(round(s['b1'] - s['b0']))
        pat = RAMP_PATTERNS[(j + variant) % len(RAMP_PATTERNS)]
        at = pat['at_beat'] if L >= pat['at_beat'] + 1 else 1
        ex = (L - 1) if (pat['exit'] and s is not last and L - 1 > at) else None
        cur = dict(at_beat=float(at), slow=round(floor + pat['depth'], 3), fast=pat['fast'], dec_frames=pat['dec'],
                   acc_frames=pat['acc'])
        if prev is not None and (cur['at_beat'], cur['slow'], ex) == (prev[0], prev[1], prev[2]):
            cur['slow'] = round(cur['slow'] + 0.05, 3)            # a short shot fell back onto its neighbour's curve
        sp.update(cur, pattern=pat['name'])
        for key in ('exit_beat', 'fast_out', 'exit'):
            sp.pop(key, None)
        if ex is not None:
            sp.update(exit_beat=float(ex), fast_out=pat['fast_out'])
        prev = (cur['at_beat'], cur['slow'], ex)
        out.append([s['i'], pat['name'], cur['at_beat'], cur['fast'], cur['slow'], cur['dec_frames'], cur['acc_frames'],
                    sp.get('exit_beat'), sp.get('fast_out')])
    return out


def _first_inner_beat(P, si):
    s = P.segs[si]
    inner = [b for b in P.beats_in(si, inner=True) if b['f'] - s['f0'] >= 3]
    return (inner[0]['f'] - s['f0']) if inner else (s['f1'] - s['f0']) // 2


def _require_moves(P):
    """Every move the user required appears at least once: speed moves are logged where the slots carry them, a
    missing camera / image accent goes on the first inner beat of the drop's first shot, a missing transition on
    the first cut into the drop, a missing sound on the drop; text moves need the user's text."""
    req = P.g.get('required') or []
    if not req:
        return
    fps, segs = P.fps, P.segs
    drop = [si for si in range(len(segs)) if P.slots_by_seg[si]['part'] == 'drop'] or list(range(len(segs)))
    for mid in req:
        if mid == 'time.speed_ramp':
            for si, sl in P.slots_by_seg.items():
                if sl['speed']['mode'] == 'ramp' and not any(m['id'] == mid for m in sl.get('moves', [])):
                    sp = sl['speed']
                    P._log(si, mid, 0, f'ramp x{sp.get("fast")} -> {sp.get("slow")} on the beat at the action peak'
                           + (' -> fast into the next cut' if sp.get('exit') else '') + ' (required)')
            continue
        if mid in ('time.slow_motion', 'time.velocity'):
            mode = 'slow' if mid == 'time.slow_motion' else 'velocity'
            for si, sl in P.slots_by_seg.items():
                if sl['speed']['mode'] == mode and not any(m['id'] == mid for m in sl.get('moves', [])):
                    P._log(si, mid, 0, f'{mode} (required)')
            continue
        if P.count.get(mid, 0) > 0:
            continue
        if mid == 'time.freeze':
            si = len(segs) - 1
            s = segs[si]
            n = s['f1'] - s['f0'] + 1
            hold = min(n - 2, int(round(0.6 * fps)))
            if hold >= 3:
                times = s.get('times') or [round(s['t'] + k / fps * float(s.get('speed', 1.0)), 4) for k in range(n)]
                k0 = n - hold
                s['times'] = [times[min(k, k0)] for k in range(n)]
                s.pop('speed_curve', None)
                P.planned_freeze.append([s['f0'] + k0, s['f1']])
                P._log(si, mid, k0, 'freeze frame on the last 0.6 s (required)')
            continue
        if mid.startswith('sfx.'):
            kind = mid.split('.', 1)[1]
            t = P.parts['drop']['t0'] if P.parts['drop']['beat1'] > P.parts['drop']['beat0'] else 0.0
            P.sfx(mid, kind, t, 'required by the user', align='peak' if kind in ('whoosh', 'riser', 'reverse_whoosh', 'swell') else 'attack')
            continue
        if mid.startswith('type.'):
            P.skip(mid, 'required, but a text move needs the text (title / word / outro_text)')
            continue
        si = drop[0]
        s = segs[si]
        if mid.startswith(('trans.', 'glitch.transition')):
            si = next((x for x in drop if x > 0), 1 if len(segs) > 1 else None)
            if si is None:
                P.skip(mid, 'required, but the edit has a single shot (no cut for a transition)')
                continue
            kind, d = _move_fx(mid, fps, None, P.period, 0)
            if kind == 'transition' and P.transition(si, mid, d, 'required by the user'):
                continue
            P.skip(mid, 'required, but no cut accepts it here')
            continue
        k = _first_inner_beat(P, si)
        kind, d = _move_fx(mid, fps, _center(s), P.period, k)
        if kind == 'fx':
            P.fx(si, mid, d, k, 'required by the user')
        elif kind == 'crop':
            if 'rot' in d:
                th = float(d['rot'])
                s['crop']['rot'] = th
                _crop_cover(s, math.cos(math.radians(abs(th))) + 0.5625 * math.sin(math.radians(abs(th))))
            else:
                _crop_zoom(s, d['z0'], d['z1'], d['ease'])
            P._log(si, mid, 0, 'required by the user')
        elif kind == 'op':
            curve = d.pop('curve')
            f = s['f0'] + k
            P.op(mid, dict(d, f=f'{f}:{min(P.e["n_frames"] - 1, f + len(curve) - 1)}', curve=curve, stage='pre'), 'required by the user', si)
        else:
            P.skip(mid, f'required, but the planner cannot place it automatically ({d})')


ACCENT_PRIO = {'zoom.crash': 6, 'transition': 5, 'shake.beat': 4, 'zoom.punch': 4, 'zoom.in_out': 3, 'rgb_split': 2,
               'glitch_blocks': 2, 'glitch': 2, 'light_leak': 2}
CAMERA_ACC = {'zoom.punch', 'shake.beat', 'zoom.in_out', 'zoom.crash'}


def _cap_fx(P):
    """Effect density (stacked effects read as random / cheap): per beat at most one camera accent (two plus one
    image accent on the combo frames: hook first hit, first beat of the drop); per shot at most two kinds of accent
    (three on the first drop shot) and about one accent per beat of its length; image accents (RGB split, glitch)
    at most one per bar. The lowest-priority accents go first; their logged moves and synced sounds go with them."""
    fps, segs = P.fps, P.segs
    bar_f = 4 * P.period * fps
    removed = []
    img_bars = {}
    calm = P.g['slug'] in QUIET_GENRES
    for si, s in enumerate(segs):
        sl = P.slots_by_seg.get(si) or {}
        ev = []                                          # (frame, kind, fx index or None)
        for fi, fx in enumerate(s.get('fx', [])):
            typ = fx.get('type')
            if typ not in ACCENT_PRIO:
                continue
            if typ == 'zoom.crash':
                ev.append((int(round(float(fx.get('at', 0)) * fps)), typ, fi, None))
            elif fx.get('times'):
                for t in fx['times']:
                    ev.append((frame_at(float(t), fps), typ, fi, t))
        if s.get('transition_in'):
            ev.append((s['f0'], 'transition', None, None))
        if not ev:
            continue
        combo = any(f in P.multi_ok for f, *_ in ev)
        n_beats = (s['f1'] - s['f0'] + 1) / max(1.0, P.period * fps)
        cap_n = max(1, int(round(n_beats))) + (1 if combo else 0)
        cap_kinds = 3 if (combo and sl.get('part') == 'drop') else 2
        if calm:
            cap_n, cap_kinds = min(cap_n, 2), 1
        keep, drop_ev = [], []
        per_frame = {}
        for e in sorted(ev, key=lambda e: (-ACCENT_PRIO[e[1]], e[0])):
            f, typ = e[0], e[1]
            fr = per_frame.setdefault(f, [])
            cam = sum(1 for x in fr if x in CAMERA_ACC)
            img = sum(1 for x in fr if x not in CAMERA_ACC and x != 'transition')
            kinds = {x[1] for x in keep}
            ok = len(keep) < cap_n and (typ in kinds or len(kinds) < cap_kinds)
            if typ in CAMERA_ACC and cam >= (2 if f in P.multi_ok else 1):
                ok = False
            if typ not in CAMERA_ACC and typ != 'transition':
                bar = int((f - P.e['segments'][0]['f0']) // max(1.0, bar_f))
                if img >= 1 or (img_bars.get(bar, 0) >= 1 and f not in P.multi_ok):
                    ok = False
            if typ == 'transition':
                ok = True                                # cuts carry their own transition; others yield to it
            if ok:
                keep.append(e)
                fr.append(typ)
                if typ not in CAMERA_ACC and typ != 'transition':
                    bar = int((f - P.e['segments'][0]['f0']) // max(1.0, bar_f))
                    img_bars[bar] = img_bars.get(bar, 0) + 1
            else:
                drop_ev.append(e)
        if not drop_ev:
            continue
        gone_fx = set()
        for f, typ, fi, t in drop_ev:
            fx = s['fx'][fi]
            if typ == 'zoom.crash' or not fx.get('times') or len(fx['times']) <= 1:
                gone_fx.add(fi)
            else:
                fx['times'] = [x for x in fx['times'] if x != t]
            mv = fx.get('move', typ)
            P.count[mv] = max(0, P.count.get(mv, 1) - 1)
            k = f - s['f0']
            if sl.get('moves'):
                for m in sl['moves']:
                    if m['id'] == mv and m.get('k') == k:
                        sl['moves'].remove(m)
                        break
            removed.append(dict(f=f, move=mv))
        s['fx'] = [fx for fi, fx in enumerate(s['fx']) if fi not in gone_fx]
    if removed:
        ts = {round(r['f'] / fps, 2) for r in removed if r['move'] in ('fx.glitch',)}
        P.e['audio']['sfx'] = [x for x in P.e['audio']['sfx'] if not (x.get('move') == 'sfx.glitch' and round(ev_at(x, -99.0), 2) in ts
                                                                       and x.get('variant') == 'burst')]
        P.skipped.append(dict(move='density', part=None, reason=f'{len(removed)} stacked accents removed (≤ 1 camera accent per beat, '
                                                                f'≤ 2 kinds per shot, image accents ≤ 1 per bar)'))
    P.fx_removed = removed


SFX_LEVEL_LU = {'light': -4.0, 'normal': 0.0, 'strong': 3.0}


def _sequence_context(P, mode):
    """A music part inside a composite (ed_sequence): the opening structure (fade / flash in on frame 0, opening ops,
    titles) only on the first part, the closing structure (fade to black, black tail, music stop, end titles) only
    on the last; letterbox bars never change inside a sequence. The beat-level moves stay."""
    if not mode:
        return
    e, fps, segs = P.e, P.fps, P.segs
    opening = mode == 'first'
    closing = mode == 'last'
    n = e['n_frames']
    gone = []
    for s in segs:
        lb = [fx for fx in s.get('fx', []) if fx.get('type') == 'letterbox']
        if lb:
            s['fx'] = [fx for fx in s['fx'] if fx.get('type') != 'letterbox']
            gone += [fx.get('move', 'fx.letterbox') for fx in lb]
    if not opening:
        tr = segs[0].get('transition_in') if segs else None
        if tr and tr.get('kind') in ('fade', 'flash'):
            gone.append(tr.get('move', tr['kind']))
            segs[0].pop('transition_in')
        early = [o for o in e['ops'] if _op_f0(o) <= 2 and o.get('op') in ('flash', 'black', 'white')]
        e['ops'] = [o for o in e['ops'] if o not in early]
        gone += [o.get('move', o['op']) for o in early]
        P.planned_black = [f for f in P.planned_black if f > 2]
        e['layers'] = [L for L in e['layers'] if not (L.get('kind') == 'title_card' and L['f0'] < n // 2)]
    if not closing:
        late = [o for o in e['ops'] if o.get('op') == 'black' and _op_f0(o) >= n - int(3.0 * fps)]
        e['ops'] = [o for o in e['ops'] if o not in late]
        if late:
            gone.append('trans.fade')
        P.planned_black = [f for f in P.planned_black if f < n - int(3.0 * fps)]
        if e['audio'].get('music'):
            e['audio']['music']['fade_out'] = 0.0
        e['audio']['sfx'] = [x for x in e['audio']['sfx'] if not (x.get('variant') == 'stop' or (x.get('params') or {}).get('stop'))]
        e['layers'] = [L for L in e['layers'] if not (L.get('kind') in ('title_card', 'kinetic') and L['f0'] >= n // 2 and L.get('move') != 'type.beat_text')]
    if closing:
        _scale_closing_fade(P)
    for mv in gone:
        P.count[mv] = max(0, P.count.get(mv, 1) - 1)
    # structural moves are counted from what is left in the EDL (fades are many op frames, one move)
    for mv in ('trans.fade', 'trans.flash', 'fx.letterbox'):
        if mv in P.count:
            n_tr = sum(1 for s in segs if (s.get('transition_in') or {}).get('move') == mv)
            n_fx = sum(1 for s in segs for fx in s.get('fx', []) if fx.get('move') == mv)
            n_op = 1 if any(o.get('move') == mv for o in e['ops']) else 0
            P.count[mv] = n_tr + n_fx + n_op
    for si, sl in P.slots_by_seg.items():           # the slot logs follow the EDL
        s = segs[si]
        has_tr = bool(s.get('transition_in'))
        sl['moves'] = [m for m in sl.get('moves', []) if not (m['id'] == 'fx.letterbox'
                       or (si == 0 and not opening and m['id'] in ('trans.fade', 'trans.flash') and not has_tr)
                       or (not closing and m['id'] == 'trans.fade' and m.get('k') is None))]
    if gone:
        P.skipped.append(dict(move='structure', part=None, reason=f'part of a sequence ({mode}): {len(gone)} opening / closing / letterbox moves left '
                                                                  f'to the sequence'))


def _style_levels(edl, sty, P):
    """The style's sound strength over the genre's levels: 'strong' lifts the drop / accent hits to strong, 'light'
    keeps everything at normal or below (the main hit normal, the rest light)."""
    lv = sty['preset'].get('sfx_level')
    t_drop = P.parts['drop']['t0'] if P.parts['drop']['beat1'] > P.parts['drop']['beat0'] else None
    for x in edl['audio'].get('sfx', []):
        main = t_drop is not None and abs(ev_at(x, -99.0) - t_drop) < 0.08 and x.get('kind') in ('impact', 'sub_drop')
        if lv == 'strong' and x.get('kind') in ('impact', 'sub_drop') and x.get('level') != 'light':
            x['level'] = 'strong'
        elif lv == 'light':
            x['level'] = 'normal' if main else 'light'


def _scale_closing_fade(P):
    """The last part of a composite closes the whole video, but the card's fade (epic: 1.25 s + 0.5 s of black) is
    sized for a full-length edit: the closing fade to black scales with the part, 5 % of its length, 0.25-0.5 s for
    parts up to 12 s and at most the card's own length (75 % ramp, 25 % black hold when the card holds black)."""
    e, fps = P.e, P.fps
    n = e['n_frames']
    T = n / fps
    tail = [o for o in e['ops'] if o.get('op') == 'black' and o.get('move', 'trans.fade') == 'trans.fade' and _op_f0(o) >= n - int(3.0 * fps)]
    if not tail:
        return
    f_first = min(_op_f0(o) for o in tail)
    span = n - f_first
    want_s = min(span / fps, max(0.25, 0.05 * T))
    if T <= 12.0:
        want_s = min(want_s, 0.5)
    want = int(round(want_s * fps))
    if want >= span:
        return
    hold = any(_op_f0(o) < n and float(o.get('a', 1.0)) >= 0.999 and isinstance(o.get('f'), str) for o in tail)
    n_hold = int(round(0.25 * want)) if hold else 0
    n_ramp = max(2, want - n_hold)
    e['ops'] = [o for o in e['ops'] if o not in tail]
    f0 = n - n_hold - n_ramp
    for k in range(n_ramp):
        a = _ease((k + 1) / n_ramp, 'inOutCubic')
        e['ops'].append(dict(f=[f0 + k], op='black', a=round(min(1.0, a), 3), stage='post', move='trans.fade'))
    if n_hold:
        e['ops'].append(dict(f=f'{n - n_hold}:{n - 1}', op='black', a=1.0, stage='post', move='trans.fade'))
    P.planned_black = [f for f in P.planned_black if f < f_first] + list(range(n - n_hold, n)) + \
        [f0 + k for k in range(n_ramp) if _ease((k + 1) / n_ramp, 'inOutCubic') >= 0.85]
    mu = e['audio'].get('music')
    if mu and mu.get('fade_out'):
        mu['fade_out'] = round(min(float(mu['fade_out']), want / fps + 0.1), 3)
    P.notes.append(f'closing fade scaled to the part: {span / fps:.2f} s -> {want / fps:.2f} s ({T:.1f} s part)')


def ev_at(x, default=None):
    """Where an audio.sfx event lands (output seconds): ed_sfx.event_anchor (an "at" event, or a "t": [t0, t1] range
    landing on t1 when peak / end aligned, else on t0); a local copy of that rule without ed_sfx."""
    fn = getattr(_sfx_mod(), 'event_anchor', None)
    if callable(fn):
        try:
            v = fn(x)
            return default if v is None else float(v)
        except Exception:
            pass
    if x.get('at') is not None:
        return float(x['at']) + float(x.get('offset_ms', 0.0) or 0.0) / 1000.0
    t = x.get('t')
    if isinstance(t, (list, tuple)) and len(t) == 2:
        peak = x.get('align') in ('peak', 'end') or x.get('kind') in ('whoosh', 'riser', 'reverse_whoosh', 'swell')
        return float(t[1] if peak else t[0])
    return default


def _sfx_mod():
    try:
        import ed_sfx as _S
        return _S
    except Exception:
        return None


def _sfx_pass(P, level):
    """Sound density and strength per genre and the user's sfx_level (aliases: normal = genre, strong = heavy).
      none   no synthesized sound
      light  the section switch only (the hits / riser on the drop)
      genre  the genre program + a low thump on every speed-ramp brake and a whoosh into the switch (the drop);
             hype genres (phonk, epic, sport, viral, motivation, teaser, fanedit): the drop / accent hits 'strong',
             whooshes under fast transitions
      heavy  genre + a whoosh on every ramp speed-up (peak on the next cut), a riser into every section (build, drop),
             a hit on every downbeat cut of the drop (1 per beat in its first 2 bars, then 1 per bar), a sub drop
             under the drop hit.
    Event times are read with ev_at (an "at" event or a "t" range)."""
    e, fps, segs = P.e, P.fps, P.segs
    slug = P.g['slug']
    hype, quiet = slug in HYPE_GENRES, slug in QUIET_GENRES
    sfx = e['audio']['sfx']
    if level == 'none':
        e['audio']['sfx'] = []
        P.skipped.append(dict(move='sfx', part=None, reason='sfx_level none: no synthesized sound'))
        return
    has_drop = P.parts['drop']['beat1'] > P.parts['drop']['beat0']
    t_drop = P.parts['drop']['t0'] if has_drop else None
    near = lambda t, kinds, tol=0.06: any(abs(ev_at(x, -99.0) - t) <= tol and x['kind'] in kinds for x in e['audio']['sfx'])   # noqa: E731
    sfx_ok = lambda part, mid: level == 'heavy' or P.ok(mid, part)   # noqa: E731
    cut_t = [s['f0'] / fps for s in segs[1:]]
    if level == 'light':
        keep = []
        for x in sfx:
            if t_drop is not None and abs(ev_at(x, -99.0) - t_drop) < 0.08 and x['kind'] in ('impact', 'sub_drop', 'riser'):
                x['level'] = 'normal'
                keep.append(x)
        e['audio']['sfx'] = keep
        return
    strong_lv = 'strong' if level == 'heavy' else 'normal'
    # every speed ramp: a low thump where it brakes (genre and up), a whoosh on its speed-up (heavy)
    for si, s in enumerate(segs):
        sl = P.slots_by_seg.get(si) or {}
        sp = sl.get('speed') or {}
        if sp.get('mode') != 'ramp':
            continue
        if sp.get('at') is not None:
            tb = s['f0'] / fps + float(sp['at'])
            if not near(tb, ('impact', 'sub_drop'), 0.12) and sfx_ok(sl.get('part'), 'sfx.impact'):
                P.sfx('sfx.impact', 'impact', round(tb, 4), 'low thump on the speed-ramp brake', variant='soft', align='attack',
                      level=strong_lv)
        if level == 'heavy' and sp.get('exit') and si + 1 < len(segs):
            t = segs[si + 1]['f0'] / fps
            if not near(t, ('whoosh',), 0.2) and sfx_ok(sl.get('part'), 'sfx.whoosh'):
                P.sfx('sfx.whoosh', 'whoosh', t, 'speed-ramp speed-up: the whoosh rushes into the cut', variant='air', align='peak',
                      dur=0.45, level='strong')
    # a whoosh into the switch (the drop); a card without whooshes gets its short riser; a part of a sequence whose
    # drop is its first frame leaves the boundary to the sequence's own package (riser / impact / sub drop)
    seq_edge = bool((getattr(P, 'opts', None) or {}).get('in_sequence')) and t_drop is not None and t_drop < 0.05
    if t_drop is not None and t_drop >= 0.2 and not seq_edge:
        before = 'build' if P.parts['build']['beat1'] > P.parts['build']['beat0'] else 'drop'
        pick = None
        if level == 'heavy' or P.ok('sfx.whoosh', before) or P.ok('sfx.whoosh', 'drop'):
            pick = ('sfx.whoosh', 'whoosh', 'heavy' if level == 'heavy' else 'air', 0.6 if level == 'heavy' else 0.45)
        elif P.ok('sfx.riser', before) or P.ok('sfx.riser', 'drop'):
            pick = ('sfx.riser', 'riser', 'short', 0.5)
        if pick and not near(t_drop, (pick[1],), 0.2):
            P.sfx(pick[0], pick[1], t_drop, f'{pick[1]} into the switch (the drop)', variant=pick[2], align='peak', dur=pick[3],
                  level=strong_lv)
    if hype or level == 'heavy':
        for si, s in enumerate(segs):                 # whooshes under fast transitions without one
            sl = P.slots_by_seg.get(si) or {}
            tr = s.get('transition_in') or {}
            if tr.get('kind') in ('whip', 'zoom', 'spin', 'push', 'slide') and not near(s['f0'] / fps, ('whoosh',), 0.2) \
                    and sfx_ok(sl.get('part'), 'sfx.whoosh'):
                P.sfx('sfx.whoosh', 'whoosh', s['f0'] / fps, f'whoosh under the {tr["kind"]} transition', variant='air', align='peak',
                      dur=0.5, level=strong_lv)
        # the drop hit
        if has_drop and t_drop is not None and not near(t_drop, ('impact', 'sub_drop'), 0.08) and sfx_ok('drop', 'sfx.impact'):
            P.sfx('sfx.impact', 'impact', t_drop, 'the hit on the first beat of the drop', variant='punch', align='attack',
                  level='strong' if hype else 'normal')
    if level == 'heavy':
        bar = 4 * P.period
        for name in ('build', 'drop'):                # a riser into every section that lifts the energy
            ts = P.parts[name]['t0']
            if P.parts[name]['beat1'] > P.parts[name]['beat0'] and ts >= P.period and not near(ts, ('riser',), 0.3):
                P.sfx('sfx.riser', 'riser', ts, f'riser into the {name} (heavy)', variant='noise', align='peak',
                      dur=round(min(2 * bar, max(P.period, ts - 0.1)), 3), level='normal')
    if level == 'heavy' and has_drop:
        d0, d1 = P.parts['drop']['t0'], P.parts['drop']['t1']
        bar = 4 * P.period
        last = -1e9
        for t in cut_t:
            if not (d0 + 0.05 < t < d1 - 0.05):
                continue
            b = next((x for x in P.beats if abs(x['t'] - t) < 1.5 / fps), None)
            if b is None or b['pos'] != 0:
                continue
            gap = P.period * 0.95 if t < d0 + 2 * bar else bar * 0.95
            if t - last >= gap and not near(t, ('impact',), 0.1):
                P.sfx('sfx.impact', 'impact', t, 'hit on a downbeat cut of the drop (heavy)', variant='punch', align='attack',
                      level='strong' if not quiet else 'normal')
                last = t
        if not near(t_drop, ('sub_drop',), 0.08) and slug != 'phonk':
            P.sfx('sfx.sub_drop', 'sub_drop', t_drop, 'sub drop under the drop hit (heavy)', variant='short', align='attack', level='strong')
    # one sound of a kind per moment (programs and this pass may both place the drop hit)
    out = []
    for x in sorted(e['audio']['sfx'], key=lambda x: (ev_at(x, 0.0), 0 if 'drop' in (x.get('why') or '') else 1)):
        if any(y['kind'] == x['kind'] and abs(ev_at(y, 0.0) - ev_at(x, 0.0)) < 0.08 for y in out):
            P.count[x.get('move', x['kind'])] = max(0, P.count.get(x.get('move', x['kind']), 1) - 1)
            continue
        out.append(x)
    e['audio']['sfx'] = out
    # levels: hype genres hit hard on the drop and the accents, quiet genres stay under the picture
    for x in e['audio']['sfx']:
        main = t_drop is not None and abs(ev_at(x, -99.0) - t_drop) < 0.08 and x['kind'] in ('impact', 'sub_drop')
        if 'level' in x:
            continue
        if x.get('rel_lu') is not None and float(x['rel_lu']) <= -9 and not main:
            x['level'] = 'light'                       # quiet by the card (-9 LU and below): the light preset
        elif quiet:
            x['level'] = 'normal' if main else 'light'
        elif hype:                                     # hits on the drop and the accents read clearly; whooshes stay under them
            x['level'] = 'strong' if (main or x['kind'] in ('impact', 'sub_drop') or (level == 'heavy' and x['kind'] == 'whoosh')) \
                else 'normal'
        else:
            x['level'] = 'strong' if main and level == 'heavy' else 'normal'


def sfx_level_support():
    """The level presets of ed_sfx ({name: ...}) when the mixer has them, else None (levels become rel_lu)."""
    try:
        import ed_sfx as _S
    except Exception:
        return None
    for name in ('LEVELS', 'LEVEL_PRESETS', 'SFX_LEVELS'):
        v = getattr(_S, name, None)
        if isinstance(v, dict) and v:
            return v
    return {} if re.search(r'"level"\s*:\s*"(light|normal|strong)"', _S.__doc__ or '') else None


def _finish_sfx(edl):
    """Every sound carries `level` and nothing else sets its loudness: with ed_sfx level presets (the mixer's targets
    and the QA's audibility floor, ed_sfx.QA_MIN_LU, come from one table) the cards' rel_lu numbers are dropped;
    without presets (an older mixer) the level becomes a rel_lu offset from the card value."""
    sup = sfx_level_support()
    try:
        import ed_sfx as _S
        kinds = _S.KINDS
    except Exception:
        kinds = {}
    for x in edl['audio'].get('sfx', []):
        lvl = x.setdefault('level', 'normal')
        if sup is not None:
            x.pop('rel_lu', None)
            continue
        off = SFX_LEVEL_LU.get(lvl, 0.0)
        if off:
            k = kinds.get(x.get('kind')) or {}
            v = (k.get('variants') or {}).get(x.get('variant') or k.get('default')) or {}
            base = x.get('rel_lu', v.get('rel_lu', -6))
            x['rel_lu'] = round(float(base) + off, 1)


# ============================================================================ styles (plain words -> a full recipe)
# Our own house styles. Each one names a genre card (the rules: rhythm, structure, limits) and adds a look on top:
# look = an ed_fx.LOOK_PRESETS picture treatment by name (+ intensity) with alternates (`alt`): versions walk the
# rotation [name, *alt] (look_pick), so two versions in a row never share a look; name None = the natural picture
# (speech styles: version 0 natural, later versions a subtle look at <= 0.4). Its grade is the shots' grade, its fx
# join every shot; looks = constant texture / light moves when ed_fx has no look presets
# (and any the look does not already carry), transitions = the palette decorative cuts are drawn from
# ('cut' = a straight cut), moves.prefer / avoid, a grade over the genre grade (the card's colour targets still hold,
# _fit_grades), the caption preset (ed_text), the sound style / level (ed_sfx) and pacing (cut_rate = x the card's
# cutting rate, transitions = share of cuts that carry a transition).
STYLE_PRESETS = {
    'clean_luxe': dict(
        look=dict(name='clean_luxe', intensity=1.0, alt=[dict(name='film_print', intensity=0.6), dict(name='teal_orange', intensity=0.5)]),
        description='Clean and expensive: unhurried cuts on strong beats, soft dissolves and slow push-ins, a gentle '
                    'highlight glow, neutral-warm colour with matte shadows; no glitches, shakes or whips.',
        genre='fashion', looks=['fx.glow'], transitions=['cut', 'trans.dissolve', 'trans.fade'],
        moves=dict(prefer=['zoom.slow', 'time.slow_motion', 'cut.match'],
                   avoid=['fx.glitch', 'fx.rgb_split', 'shake.beat', 'zoom.crash', 'glitch.vhs', 'glitch.datamosh', 'trans.whip',
                          'trans.spin', 'fx.film_overlay']),
        grade=dict(preset='color', contrast=1.08, sat=0.92, temp=0.03, fade=0.015, gain=0.97),
        caption_style='clean', sfx_style='clean', sfx_level='light', pacing=dict(cut_rate=0.85, transitions=0.3),
        keywords=['clean', 'expensive', 'luxury', 'luxe', 'premium', 'elegant', 'minimal', 'minimalist', 'sleek', 'high end',
                  'polished', 'classy', 'refined', 'chic', 'rich', 'quiet luxury', 'sophisticated', 'smooth', 'tasteful']),
    'editorial_mono': dict(
        look=dict(name='mono_noir', intensity=0.8, alt=[dict(name='silver_bleach', intensity=0.9)]),
        description='Black-and-white editorial: hard graphic contrast, film grain, quick runway cuts, white flashes and '
                    'wipes on downbeats.',
        genre='fashion', looks=['fx.film_overlay', 'lens.vignette'], transitions=['cut', 'trans.flash', 'trans.wipe'],
        moves=dict(prefer=['zoom.punch', 'cut.quick'], avoid=['fx.rgb_split', 'fx.glitch', 'fx.light_leak', 'fx.glow']),
        grade=dict(preset='bw_hi'), caption_style='boxed', sfx_style='clean', sfx_level='normal',
        pacing=dict(cut_rate=1.1, transitions=0.3),
        keywords=['black and white', 'b&w', 'bw', 'monochrome', 'mono', 'editorial', 'magazine', 'runway', 'catwalk',
                  'stark', 'graphic', 'noir fashion', 'high contrast']),
    'street_grit': dict(
        look=dict(name='gritty_contrast', intensity=1.0, alt=[dict(name='silver_bleach', intensity=1.0)]),
        description='Gritty street: dark crushed contrast, cold desaturated colour, coarse grain, heavy shakes and '
                    'punches on the kick, whips and flashes, velocity on the drop.',
        genre='phonk', looks=['fx.film_overlay', 'lens.vignette'], transitions=['cut', 'trans.whip', 'trans.flash', 'trans.zoom'],
        moves=dict(prefer=['shake.beat', 'zoom.punch', 'time.velocity', 'fx.rgb_split'],
                   avoid=['trans.dissolve', 'fx.light_leak', 'fx.glow', 'light.halation']),
        grade=dict(contrast=1.38, sat=0.66, temp=-0.1, black=0.05),
        caption_style='podcast_caps', sfx_style='trap', sfx_level='strong', pacing=dict(cut_rate=1.15, transitions=0.3),
        keywords=['gritty', 'grit', 'street', 'urban', 'raw', 'underground', 'rough', 'dirty', 'grime', 'concrete', 'hard',
                  'aggressive', 'skate', 'skateboard', 'graffiti', 'hood', 'trap', 'dark']),
    'neon_drift': dict(
        look=dict(name='neon_night', intensity=1.0, alt=[dict(name='teal_orange', intensity=0.9), dict(name='gritty_contrast', intensity=0.7)]),
        description='Neon night drive: cold shadows with hot highlights, glow on the lights, velocity and flashes on the '
                    'beat, zoom transitions through the cuts.',
        genre='phonk', looks=['fx.glow', 'lens.vignette'], transitions=['cut', 'trans.flash', 'trans.zoom', 'trans.whip'],
        moves=dict(prefer=['time.velocity', 'shake.beat', 'fx.rgb_split'], avoid=['trans.dissolve', 'fx.film_overlay']),
        grade=dict(temp=-0.14, tint=-0.04, sat=0.8, contrast=1.32),
        caption_style='podcast_caps', sfx_style='trap', sfx_level='strong', pacing=dict(cut_rate=1.1, transitions=0.35),
        keywords=['neon', 'night', 'nightlife', 'cyberpunk', 'synth', 'synthwave', 'city lights', 'drift', 'car', 'cars',
                  'racing', 'midnight', 'glow', 'electric', 'night drive', 'tunnel']),
    'blockbuster': dict(
        look=dict(name='teal_orange', intensity=1.0, alt=[dict(name='silver_bleach', intensity=0.8)]),
        description='Big-screen cinematic: wide establishing shots, slow motion on the drop, teal shadows and warm '
                    'highlights, letterbox, dips to black between phrases.',
        genre='epic', looks=['lens.vignette'], transitions=['cut', 'trans.fade', 'trans.flash', 'trans.dissolve'],
        moves=dict(prefer=['time.slow_motion', 'zoom.slow', 'time.speed_ramp'],
                   avoid=['fx.rgb_split', 'fx.glitch', 'trans.whip', 'trans.spin', 'fx.film_overlay']),
        grade=dict(preset='teal', contrast=1.22),
        caption_style='podcast_bold', sfx_style='cinematic', sfx_level='strong', pacing=dict(cut_rate=1.0, transitions=0.2),
        keywords=['epic', 'cinematic', 'blockbuster', 'trailer', 'movie', 'film look', 'grand', 'heroic', 'big',
                  'orchestral', 'larger than life', 'teal orange', 'widescreen', 'majestic', 'powerful']),
    'dreamy_retro': dict(
        look=dict(name='dreamy_bloom', intensity=1.0, alt=[dict(name='film_print', intensity=1.0)]),
        description='Dreamy retro: warm faded film colour, halation and light leaks, soft long dissolves, slow motion '
                    'and slow push-ins; nothing hard or digital.',
        genre='calm', looks=['light.halation', 'fx.film_overlay', 'fx.light_leak'], transitions=['trans.dissolve', 'cut', 'trans.fade'],
        moves=dict(prefer=['time.slow_motion', 'zoom.slow'],
                   avoid=['zoom.punch', 'shake.beat', 'zoom.crash', 'fx.rgb_split', 'fx.glitch', 'trans.whip', 'trans.flash']),
        grade=dict(preset='warm', temp=0.16, sat=0.85, contrast=0.92, lift=0.07, fade=0.03, gain=0.95),
        caption_style='clean', sfx_style='clean', sfx_level='light', pacing=dict(cut_rate=0.85, transitions=0.7),
        keywords=['dreamy', 'dream', 'retro', 'vintage', 'nostalgic', 'nostalgia', 'analog', 'analogue', '70s', '80s', '90s',
                  'super 8', '8mm', 'hazy', 'faded', 'old school', 'memory', 'memories', 'film grain', 'polaroid', 'warm']),
    'soft_morning': dict(
        look=dict(name='pastel_fade', intensity=0.8, alt=[dict(name='golden_hour', intensity=0.6), dict(name='dreamy_bloom', intensity=0.6)]),
        description='Soft and airy: bright gentle colour, long dissolves, slow zooms, a light glow; quiet sound.',
        genre='calm', looks=['fx.glow'], transitions=['trans.dissolve', 'cut'],
        moves=dict(prefer=['zoom.slow', 'time.slow_motion'],
                   avoid=['zoom.punch', 'shake.beat', 'zoom.crash', 'fx.rgb_split', 'fx.glitch', 'trans.whip', 'trans.flash',
                          'fx.film_overlay']),
        grade=dict(preset='warm', temp=0.08, sat=0.9, contrast=0.95, lift=0.06),
        caption_style='clean', sfx_style='clean', sfx_level='light', pacing=dict(cut_rate=0.8, transitions=0.6),
        keywords=['calm', 'peaceful', 'serene', 'airy', 'light', 'pastel', 'gentle', 'slow', 'cozy', 'morning', 'quiet',
                  'relaxing', 'chill', 'mellow', 'lofi', 'soft', 'tender', 'minimal calm']),
    'moody_noir': dict(
        look=dict(name='mono_noir', intensity=1.0, alt=[dict(name='cold_concrete', intensity=1.0)]),
        description='Moody and dark: desaturated cold colour, deep shadows, vignette and grain, slow cuts, dips to '
                    'black; no punches or flashes.',
        genre='drama', looks=['lens.vignette', 'fx.film_overlay'], transitions=['cut', 'trans.fade', 'trans.dissolve'],
        moves=dict(prefer=['time.slow_motion', 'zoom.slow'],
                   avoid=['zoom.punch', 'shake.beat', 'fx.rgb_split', 'fx.glitch', 'trans.whip', 'trans.flash', 'fx.light_leak']),
        grade=dict(preset='desat', contrast=1.25, sat=0.55, temp=-0.05),
        caption_style='clean', sfx_style='cinematic', sfx_level='normal', pacing=dict(cut_rate=0.9, transitions=0.3),
        keywords=['moody', 'noir', 'sad', 'melancholic', 'melancholy', 'emotional', 'dramatic', 'serious', 'intense',
                  'brooding', 'somber', 'heartbreak', 'tense', 'rain', 'lonely', 'grief', 'tragic']),
    'punchy_pop': dict(
        look=dict(name='vivid_pop', intensity=1.0, alt=[dict(name='neon_night', intensity=0.8), dict(name='golden_hour', intensity=0.8)]),
        description='Bright and punchy: saturated colour, quick cuts on every beat, punch-ins and whips, zoom '
                    'transitions, bold word-by-word captions.',
        genre='viral', looks=[], transitions=['cut', 'trans.whip', 'trans.zoom', 'trans.flash'],
        moves=dict(prefer=['zoom.punch', 'shake.beat', 'cut.quick'], avoid=['trans.dissolve', 'fx.film_overlay', 'trans.fade']),
        grade=dict(preset='color', contrast=1.14, sat=1.2, temp=0.04),
        caption_style='karaoke_highlight', sfx_style='trap', sfx_level='normal', pacing=dict(cut_rate=1.15, transitions=0.3),
        keywords=['fun', 'playful', 'pop', 'bright', 'colorful', 'colourful', 'punchy', 'energetic', 'viral', 'trendy',
                  'catchy', 'bold', 'upbeat', 'happy', 'loud', 'fresh', 'vibrant', 'snappy']),
    'hype_energy': dict(
        look=dict(name='vivid_pop', intensity=0.7, alt=[dict(name='teal_orange', intensity=0.8), dict(name='gritty_contrast', intensity=0.6)]),
        description='Full-throttle hype: hard contrast, speed ramps into freeze frames, crash zooms, white flashes on '
                    'downbeats, heavy hits.',
        genre='sport', looks=['lens.vignette'], transitions=['cut', 'trans.flash', 'trans.zoom', 'trans.whip'],
        moves=dict(prefer=['time.speed_ramp', 'shake.beat', 'zoom.crash', 'time.freeze'],
                   avoid=['trans.dissolve', 'fx.light_leak', 'fx.film_overlay']),
        grade=dict(preset='color', contrast=1.2, sat=1.08, temp=-0.02),
        caption_style='podcast_caps', sfx_style='trap', sfx_level='strong', pacing=dict(cut_rate=1.1, transitions=0.3),
        keywords=['hype', 'sport', 'sports', 'athletic', 'power', 'fast', 'energy', 'adrenaline', 'game day', 'workout',
                  'gym', 'hard hitting', 'beast', 'match', 'highlights', 'training', 'fitness', 'extreme']),
    'golden_wander': dict(
        look=dict(name='golden_hour', intensity=1.0, alt=[dict(name='film_print', intensity=0.9), dict(name='dreamy_bloom', intensity=0.6)]),
        description='Golden-hour wanderlust: warm saturated colour, light leaks and glow, motion-matched cuts, whip and '
                    'zoom transitions between places, the odd dissolve.',
        genre='travel', looks=['fx.light_leak', 'fx.glow'], transitions=['cut', 'trans.whip', 'trans.zoom', 'trans.dissolve'],
        moves=dict(prefer=['cut.match', 'zoom.slow', 'time.speed_ramp', 'time.hyperlapse'],
                   avoid=['fx.rgb_split', 'fx.glitch', 'shake.beat', 'fx.film_overlay']),
        grade=dict(preset='warm', sat=1.12, contrast=1.08, temp=0.1),
        caption_style='boxed', sfx_style='cinematic', sfx_level='normal', pacing=dict(cut_rate=1.0, transitions=0.35),
        keywords=['travel', 'adventure', 'wanderlust', 'journey', 'trip', 'vacation', 'holiday', 'explore', 'golden hour',
                  'sunset', 'summer', 'beach', 'mountains', 'road trip', 'nature', 'outdoors', 'sunny', 'getaway']),
    'fan_glow': dict(
        look=dict(name='teal_orange', intensity=0.8, alt=[dict(name='neon_night', intensity=0.8), dict(name='dreamy_bloom', intensity=0.7)]),
        description='Fan edit with a shine: teal grade, glow and film texture, velocity on the drop, punches and RGB '
                    'splits on accents, flashes and zoom cuts.',
        genre='fanedit', looks=['fx.glow', 'fx.film_overlay'], transitions=['cut', 'trans.flash', 'trans.zoom', 'trans.dissolve'],
        moves=dict(prefer=['time.velocity', 'zoom.punch', 'fx.rgb_split', 'shake.beat'], avoid=['fx.light_leak']),
        grade=dict(preset='teal', contrast=1.22, sat=0.95),
        caption_style='podcast_caps', sfx_style='trap', sfx_level='strong', pacing=dict(cut_rate=1.1, transitions=0.35),
        keywords=['fan edit', 'fanedit', 'character', 'anime', 'scene pack', 'aesthetic', 'badass', 'villain', 'hero',
                  'tribute', 'iconic', 'edit of', 'coloring', 'velocity edit', 'amv']),
    'mystery_tease': dict(
        look=dict(name='cold_concrete', intensity=1.0, alt=[dict(name='mono_noir', intensity=0.8)]),
        description='Mysterious teaser: cold contrasty colour, vignette and grain, slow reveals, dips to black and a single '
                    'flash per phrase, title cards between beats.',
        genre='teaser', looks=['lens.vignette', 'fx.film_overlay'], transitions=['cut', 'trans.fade', 'trans.flash'],
        moves=dict(prefer=['time.slow_motion', 'zoom.slow'], avoid=['trans.whip', 'trans.spin', 'fx.light_leak', 'zoom.punch']),
        grade=dict(preset='cool', contrast=1.28, sat=0.75, gamma=1.12),
        caption_style='clean', sfx_style='cinematic', sfx_level='normal', pacing=dict(cut_rate=0.95, transitions=0.25),
        keywords=['mystery', 'mysterious', 'suspense', 'teaser', 'coming soon', 'reveal', 'tension', 'thriller', 'secret',
                  'cryptic', 'launch', 'announcement', 'tease', 'enigmatic', 'ominous']),
    'studio_crisp': dict(
        look=dict(name='clean_luxe', intensity=0.5, alt=[dict(name='vivid_pop', intensity=0.5), dict(name='pastel_fade', intensity=0.5)]),
        description='Crisp studio product: neutral clean colour, punch-ins on features, quick bursts, flashes and wipes '
                    'on the beat, slow motion for the hero shot.',
        genre='product', looks=[], transitions=['cut', 'trans.flash', 'trans.wipe', 'trans.zoom'],
        moves=dict(prefer=['zoom.punch', 'cut.quick', 'zoom.slow', 'time.slow_motion'],
                   avoid=['fx.film_overlay', 'fx.glitch', 'fx.light_leak', 'shake.beat']),
        grade=dict(preset='natural', contrast=1.06, sat=1.04),
        caption_style='boxed', sfx_style='clean', sfx_level='normal', pacing=dict(cut_rate=1.0, transitions=0.25),
        keywords=['product', 'crisp', 'studio', 'commercial', 'ad', 'advert', 'advertisement', 'unboxing', 'gadget', 'tech',
                  'packshot', 'e-commerce', 'ecommerce', 'showcase', 'shop', 'store', 'launch video']),
    'rise_grind': dict(
        look=dict(name='silver_bleach', intensity=1.0, alt=[dict(name='gritty_contrast', intensity=0.8), dict(name='mono_noir', intensity=0.8)]),
        description='Motivational grind: contrasty muted colour, vignette and grain, slow motion and speed ramps on the '
                    'key line, dips to black, big cinematic hits.',
        genre='motivation', looks=['lens.vignette', 'fx.film_overlay'], transitions=['cut', 'trans.fade', 'trans.flash'],
        moves=dict(prefer=['time.slow_motion', 'zoom.slow', 'time.speed_ramp'], avoid=['fx.rgb_split', 'fx.glitch', 'trans.spin']),
        grade=dict(preset='teal', contrast=1.2, sat=0.85),
        caption_style='podcast_caps', sfx_style='cinematic', sfx_level='strong', pacing=dict(cut_rate=0.95, transitions=0.2),
        keywords=['motivation', 'motivational', 'inspiring', 'inspirational', 'grind', 'discipline', 'hustle', 'success',
                  'never give up', 'mindset', 'comeback', 'rise', 'determination', 'work hard', 'speech', 'ambition']),
    'podcast_punch': dict(
        look=dict(name=None, alt=[dict(name='clean_luxe', intensity=0.35), dict(name='teal_orange', intensity=0.3)]),
        description='Punchy talk clip: tight speaker crops, jump cuts on pauses, punch-ins on phrase starts, bold '
                    'captions with keywords in colour.',
        genre='clips', looks=[], transitions=['cut'], moves=dict(prefer=['zoom.punch', 'cut.jump'], avoid=['fx.film_overlay', 'fx.glitch']),
        grade=dict(preset='natural', contrast=1.06, sat=1.04),
        caption_style='podcast_bold', sfx_style='clean', sfx_level='light', pacing=dict(cut_rate=1.0, transitions=0.0),
        keywords=['podcast', 'clip', 'clips', 'interview', 'talk', 'talking head', 'conversation', 'quote', 'moment',
                  'show', 'episode', 'guest', 'host']),
    'calm_explain': dict(
        look=dict(name=None, alt=[dict(name='clean_luxe', intensity=0.3), dict(name='pastel_fade', intensity=0.3)]),
        description='Clear explainer: steady framing, plain cuts and the odd dissolve, slow zooms, easy-to-read boxed '
                    'captions, quiet sound.',
        genre='explainer', looks=[], transitions=['cut', 'trans.dissolve'],
        moves=dict(prefer=['zoom.slow'], avoid=['shake.beat', 'fx.rgb_split', 'fx.glitch', 'zoom.crash']),
        grade=dict(preset='natural', contrast=1.04, sat=1.02),
        caption_style='boxed', sfx_style='clean', sfx_level='light', pacing=dict(cut_rate=1.0, transitions=0.1),
        keywords=['explain', 'explainer', 'tutorial', 'how to', 'educational', 'lesson', 'guide', 'breakdown',
                  'informative', 'clear', 'simple', 'teach', 'learn', 'walkthrough', 'course']),
    'native_ugc': dict(
        look=dict(name=None, alt=[dict(name='golden_hour', intensity=0.35), dict(name='vivid_pop', intensity=0.3)]),
        description='Phone-native creator look: natural colour, quick jump cuts, punch-ins, a whip between ideas, '
                    'word-by-word boxed captions.',
        genre='ugc', looks=[], transitions=['cut', 'trans.whip'],
        moves=dict(prefer=['zoom.punch', 'cut.jump'], avoid=['fx.film_overlay', 'fx.letterbox', 'trans.dissolve']),
        grade=dict(preset='color', sat=1.06), caption_style='karaoke_box', sfx_style='clean', sfx_level='normal',
        pacing=dict(cut_rate=1.1, transitions=0.1),
        keywords=['ugc', 'authentic', 'real', 'phone', 'selfie', 'testimonial', 'review', 'creator', 'native', 'casual',
                  'honest', 'haul', 'day in my life', 'vlog', 'relatable']),
}
GENRE_DEFAULT_STYLE = {'phonk': 'street_grit', 'epic': 'blockbuster', 'calm': 'soft_morning', 'drama': 'moody_noir',
                       'viral': 'punchy_pop', 'sport': 'hype_energy', 'travel': 'golden_wander', 'fashion': 'clean_luxe',
                       'fanedit': 'fan_glow', 'teaser': 'mystery_tease', 'product': 'studio_crisp', 'motivation': 'rise_grind',
                       'clips': 'podcast_punch', 'explainer': 'calm_explain', 'ugc': 'native_ugc'}
CAPTION_SIBLING = {'podcast_bold': 'podcast_caps', 'podcast_caps': 'podcast_bold', 'karaoke_highlight': 'karaoke_box',
                   'karaoke_box': 'karaoke_highlight', 'clean': 'boxed', 'boxed': 'clean'}
_STOP = {'and', 'the', 'a', 'an', 'with', 'of', 'for', 'to', 'in', 'on', 'my', 'me', 'it', 'like', 'make', 'style', 'look',
         'vibe', 'vibes', 'feel', 'edit', 'video', 'please', 'some', 'more', 'very', 'really', 'kind', 'sort', 'but', 'not'}


def _words(text):
    return re.sub(r'[^a-z0-9&+]+', ' ', str(text or '').lower().replace('-', ' ')).split()


def resolve_style(text, genre=None):
    """Plain words -> a house style: {"name", "score" 0..1, "genre", "matched", "why"}. A preset name matches
    outright; else keywords (phrases count more), the genre's name and words of the description score each preset.
    Nothing matches (words in another language: style words are English) -> matched False, the default style of the
    named genre (or of `genre`), score 0, and a why that says so (the CLI and the plan log print it)."""
    if isinstance(text, dict):
        text = text.get('name') or text.get('style') or ''
    raw = str(text or '').strip()
    key = raw.lower().replace(' ', '_').replace('-', '_')
    if key in STYLE_PRESETS:
        st = STYLE_PRESETS[key]
        return dict(name=key, score=1.0, genre=st['genre'], matched=True, why=f'preset name "{key}"')
    ws = _words(raw)
    joined = ' ' + ' '.join(ws) + ' '
    named_genre = None
    for w in ws + [' '.join(ws[i:i + 2]) for i in range(len(ws) - 1)]:
        try:
            named_genre = resolve_genre(w)
            break
        except KeyError:
            continue
    best = None
    for name, st in STYLE_PRESETS.items():
        sc, hits = 0.0, []
        for kw in st['keywords']:
            k = ' '.join(_words(kw))
            if not k:
                continue
            if f' {k} ' in joined:
                sc += 3.0 if ' ' in k else 2.0
                hits.append(kw)
            elif ' ' not in k and len(k) >= 5 and any(w.startswith(k[:max(5, len(k) - 2)]) for w in ws):
                sc += 1.0
                hits.append(kw + '~')
        if named_genre and named_genre == st['genre']:
            sc += 1.5
            hits.append(f'genre {named_genre}')
        if genre and resolve_genre(genre) == st['genre']:
            sc += 0.75
        desc = set(_words(st['description'])) - _STOP
        sc += 0.25 * len([w for w in set(ws) - _STOP if len(w) >= 4 and w in desc])
        if best is None or sc > best[0] + 1e-9:
            best = (sc, name, hits)
    sc, name, hits = best
    if sc <= 0.0:
        g = named_genre or (resolve_genre(genre) if genre else None)
        name = GENRE_DEFAULT_STYLE.get(g or 'viral', 'punchy_pop')
        return dict(name=name, score=0.0, genre=STYLE_PRESETS[name]['genre'], matched=False,
                    why=f"no style matched '{raw}' — style words are matched in English; using {name}")
    return dict(name=name, score=round(sc / (sc + 3.0), 3), genre=STYLE_PRESETS[name]['genre'], matched=True,
                why='matched ' + ', '.join(hits[:6]))


def _avoid_choices(avoid):
    """meta.choices of earlier versions (EDL dicts or paths); an EDL without choices is read from its content."""
    out = []
    for a in avoid or []:
        try:
            e = _load_json(a) if isinstance(a, str) else a
        except Exception:
            continue
        if not isinstance(e, dict):
            continue
        stored = dict((e.get('meta') or {}).get('choices') or {})
        segs = e.get('segments') or []                  # read from the content, what is stored overrides it
        ch = dict(transitions=sorted({(s.get('transition_in') or {}).get('move', (s.get('transition_in') or {}).get('kind'))
                                      for s in segs if s.get('transition_in')} - {None}),
                  looks=sorted({fx.get('move', fx.get('type')) for s in segs for fx in s.get('fx', [])
                                if fx.get('type') in ('film_overlay', 'glow', 'vignette', 'light_leak')}),
                  shots=[[i, sl.get('shot'), (sl.get('src_t') or [None])[0]] for i, sl in enumerate((e.get('meta') or {}).get('slots') or [])],
                  variant=(e.get('meta') or {}).get('variant'))
        ch.update(stored)
        out.append(ch)
    return out


def style_context(style, genre=None, variant=None, avoid=None):
    """Resolve the style words / name, pick the variant (the next unused one when `avoid` lists earlier versions) and
    gather what earlier versions used. -> dict(name, preset, match, variant, avoid, rng) | None."""
    av = _avoid_choices(avoid)
    if not style and not av and not variant:
        return None
    if not style:
        for c in av:                                    # another version of a styled edit keeps its style
            if c.get('style') in STYLE_PRESETS:
                style = c['style']
                break
    if not style:                                       # a version of the plain genre plan: no look on top
        slug = resolve_genre(genre) if genre else 'viral'
        m = dict(name=None, score=0.0, genre=slug, why='no style: the genre card as written')
        preset = dict(description='the genre card as written', genre=slug, looks=[], transitions=[], moves=dict(prefer=[], avoid=[]),
                      grade={}, caption_style=None, sfx_style=None, sfx_level=None, pacing={}, keywords=[])
    else:
        m = resolve_style(style, genre)
        preset = STYLE_PRESETS[m['name']]
    used = {int(c['variant']) for c in av if isinstance(c.get('variant'), int)}
    if variant is None:
        variant = 0 if not av else max(used | {0}) + 1
        while variant in used:
            variant += 1
    variant = int(variant)
    if variant < 0:
        raise ValueError('variant must be >= 0')
    seed = int(hashlib.md5(f'{m["name"] or m["genre"]}|{variant}'.encode()).hexdigest()[:8], 16)
    dark = bool(DARK_WORDS.search(str(style or '').lower())) or any(c.get('dark') for c in av)
    return dict(name=m['name'], preset=preset, match=m, variant=variant, avoid=av, rng=np.random.default_rng(seed), seed=seed,
                dark=dark)


def _style_nuance(sty):
    """Small, repeatable grade differences between versions of one style (variant 0 = the preset as written)."""
    if not sty or not sty['variant']:
        return {}
    r = np.random.default_rng(sty['seed'] + 17)
    return dict(temp=round(float(r.uniform(-0.05, 0.05)), 3), sat=round(float(r.uniform(0.93, 1.07)), 3),
                contrast=round(float(r.uniform(-0.04, 0.04)), 3))


def look_rotation(preset):
    """A style's looks in version order: [(look name | None = the natural picture, intensity), ...] - the main look,
    then its alternates (preset look.alt: a name, or a list of names / {name, intensity})."""
    lk = (preset or {}).get('look') or {}
    if not lk:
        return []
    out = [(lk.get('name'), float(lk.get('intensity', 1.0)) if lk.get('name') else 0.0)]
    alt = lk.get('alt')
    for a in ([alt] if isinstance(alt, (str, dict)) else list(alt or [])):
        if isinstance(a, str):
            out.append((a, float(lk.get('intensity', 1.0))))
        elif isinstance(a, dict) and a.get('name'):
            out.append((a['name'], float(a.get('intensity', lk.get('intensity', 1.0)))))
    return out


def look_pick(sty):
    """(index, look name | None, intensity) of a style version in its look rotation: version v takes look v mod n, so
    two versions in a row never share a look; None when the style has no looks."""
    rot = look_rotation(sty['preset']) if sty else []
    if not rot:
        return None
    i = int(sty['variant']) % len(rot)
    return (i,) + tuple(rot[i])


def style_look(sty):
    """The ed_fx look of a style version: {'name', 'grade', 'fx', 'intensity', 'pick', 'rotation'} (ed_fx.look at the
    picked intensity; versions walk the style's look rotation, look_pick), None for a natural version or without
    ed_fx looks. A subtle look (intensity <= 0.4, the speech styles' later versions) scales its auto levels too."""
    pk = look_pick(sty)
    if pk is None or not pk[1]:
        return None
    if '_look' in sty:
        return sty['_look']
    i, name, inten = pk
    try:
        import ed_fx as FX
        fn = getattr(FX, 'look', None)
        out = fn(name, inten) if callable(fn) else None
    except Exception:
        out = None
    if out is not None:
        out = dict(out, intensity=inten, pick=i, rotation=[n for n, _ in look_rotation(sty['preset'])])
        if inten <= 0.4 and out['grade'].get('auto'):
            out['grade'] = dict(out['grade'], auto=round(float(out['grade']['auto']) * inten, 3))
    sty['_look'] = out
    return out


def style_grade(slug, sty):
    """The shots' grade: the style's ed_fx look grade (the genre grade when the style has no look, with the
    style's own grade numbers on top when ed_fx has no looks), plus the version's nuance (temp / contrast offsets,
    sat factor). The card's colour targets still apply (_fit_grades)."""
    g = dict(GRADES.get(slug, dict(preset='color')))
    if not sty:
        return g
    lk = style_look(sty)
    if lk is not None:
        g = dict(lk['grade'])
    else:
        sg = dict(sty['preset'].get('grade') or {})
        if sg.get('preset') and sg['preset'] != g.get('preset'):
            g = {}                                 # another base look: the style's grade replaces the genre's
        g.update(sg)
    nu = _style_nuance(sty)
    if nu:
        g['temp'] = round(float(g.get('temp', 0.0)) + nu['temp'], 3)
        g['contrast'] = round(float(g.get('contrast', 1.0)) + nu['contrast'], 3)
        if not g.get('mono'):
            g['sat'] = round(float(g.get('sat', 1.0)) * nu['sat'], 3)
    return g


class _ScaledRng:
    """The cut-grid DP's tie-break jitter, wider for versions > 0 (other equally good grids within the card's rhythm)."""

    def __init__(self, rng, k):
        self.rng, self.k = rng, float(k)

    def uniform(self, a=0.0, b=1.0, size=None):
        return self.rng.uniform(a, a + (b - a) * self.k, size)

    def __getattr__(self, name):
        return getattr(self.rng, name)


def _style_noise(sty):
    """Score noise of a version (variant >= 1): close candidate windows swap places; repeatable per window."""
    if not sty or not sty['variant']:
        return None
    base = sty['seed']

    def noise(s, sh, w0):
        h = hashlib.md5(f'{base}|{s["i"]}|{sh["id"]}|{round(float(w0), 2)}'.encode()).hexdigest()
        return (int(h[:8], 16) / 0xFFFFFFFF - 0.5) * 0.9
    return noise


def _avoid_windows(sty):
    out = []
    for c in (sty or {}).get('avoid') or []:
        for row in c.get('shots') or []:
            if isinstance(row, (list, tuple)) and len(row) >= 3 and row[1]:
                out.append((int(row[0]), str(row[1]), float(row[2]) if row[2] is not None else None))
    return out


TRANSITION_FRAMES = {'trans.dissolve': 0.6, 'trans.fade': 0.4, 'trans.whip': 0.2, 'trans.zoom': 0.4, 'trans.spin': 0.34,
                     'trans.wipe': 0.34, 'trans.lens_distort': 0.34, 'trans.flash': 0.0}


def _style_transition_plan(slots, sty, g, fps, period):
    """Which cuts carry a style transition and which one: the preset's palette (rotated by the variant, ids used by
    earlier versions last), on downbeat cuts first, up to pacing.transitions of the cuts; slots get the handles the
    centred transitions need (before assignment, so the source windows have them). -> {slot index: move id}"""
    if not sty:
        return {}
    st = sty['preset']
    share = float((st.get('pacing') or {}).get('transitions', 0.0))
    pal = [t for t in st['transitions'] if t == 'cut' or (move_card(t) is not None and move_allowed(g, t)[1] not in
                                                          ('forbidden by the user', 'forbidden by the genre card',
                                                           'the move card forbids this genre'))]
    trs = [t for t in pal if t != 'cut']
    if share <= 0 or not trs:
        return {}
    used = {t for c in sty['avoid'] for t in (c.get('transitions') or [])}
    trs = sorted(trs, key=lambda t: (t in used, trs.index(t)))
    v = sty['variant']
    trs = trs[v % len(trs):] + trs[:v % len(trs)]
    vis = [s for s in slots if s['kind'] != 'black']
    cand = []
    for i, s in enumerate(slots):
        if i == 0 or s['kind'] == 'black' or slots[i - 1]['kind'] == 'black':
            continue
        if s['kind'] == 'burst' or slots[i - 1]['kind'] == 'burst':
            continue
        if (s['t1'] - s['t0']) < 0.45 or (slots[i - 1]['t1'] - slots[i - 1]['t0']) < 0.45:
            continue
        down = abs(s['b0'] - round(s['b0'])) < 1e-6 and int(round(s['b0'])) % 4 == 0
        cand.append((0 if down else 1, s['b0'], i))
    n_want = int(round(share * max(0, len(vis) - 1)))
    r = np.random.default_rng(sty['seed'] + 3)
    cand.sort(key=lambda x: (x[0], r.uniform()))
    pick = sorted(i for _, _, i in cand[:n_want])
    plan = {}
    for k, i in enumerate(pick):
        mid = trs[k % len(trs)]
        sec = TRANSITION_FRAMES.get(mid, 0.3)
        if mid == 'trans.dissolve':
            sec = min(sec, 0.4 * min(slots[i]['t1'] - slots[i]['t0'], slots[i - 1]['t1'] - slots[i - 1]['t0']))
        plan[i] = (mid, max(2, int(round(sec * fps))))
        h = plan[i][1] / 2 / fps + 0.05
        slots[i]['handle_in'] = max(slots[i].get('handle_in', 0.0), h)
        slots[i - 1]['handle_out'] = max(slots[i - 1].get('handle_out', 0.0), h)
    return plan


def _look_fx(mid, r, P, si):
    """Constant look of a style on one shot (ed_fx params, variant nuance from r)."""
    s = P.segs[si]
    if mid == 'fx.film_overlay':
        return dict(type='film_overlay', level=int(r.choice([1, 2])), delivery='social')
    if mid == 'light.halation':
        return dict(type='glow', threshold=0.85, knee=0.1, strength=round(float(r.uniform(0.22, 0.34)), 2),
                    radii=[0.006, 0.015, 0.03, 0.06], tint='#ff5a1a', tint_mix=0.45, blend='screen')
    if mid == 'fx.glow':
        return dict(type='glow', threshold=0.72, strength=round(float(r.uniform(0.16, 0.28)), 2))
    if mid == 'lens.vignette':
        return dict(type='vignette', amount=round(float(r.uniform(0.18, 0.3)), 2))
    if mid == 'fx.light_leak':
        t0, t1 = s['f0'] / P.fps, (s['f1'] + 1) / P.fps
        return dict(type='light_leak', mode='ambient', t=[round(t0, 4), round(t1, 4)], shape=str(r.choice(['edge', 'corner', 'blob'])),
                    palette=str(r.choice(['amber', 'peach', 'gold'])), anchor=str(r.choice(['left', 'right', 'tl', 'tr'])),
                    peak=round(float(r.uniform(0.35, 0.6)), 2), seed=int(r.integers(1, 9999)))
    return None


HARD_TRANSITIONS = ('flash', 'whip', 'zoom', 'spin', 'lens', 'glitch', 'pixel_sort', 'light_leak', 'datamosh')
EDGE_ACCENTS = {'zoom.punch': 10, 'shake.beat': 6, 'zoom.in_out': 8}      # frames of visible camera motion after a hit
                                                                           # (bounce punch: its release; held: the jump)


def _calm_transition_edges(P):
    """A hard transition is the hit. A camera accent whose motion runs into the two frames just outside the
    transition window (where the eye - and the QA - compares the outgoing and the incoming picture) blurs the switch:
    that hit is taken out (logged in meta.skipped). Required moves stay."""
    fps, segs = P.fps, P.segs
    req = set(P.g.get('required') or [])
    out = []
    for si, sg in enumerate(segs):
        tr = sg.get('transition_in') or {}
        F = int(tr.get('frames', 6) or 0)
        if tr.get('kind') not in HARD_TRANSITIONS or F <= 0:
            continue
        a = int(sg['f0']) - F // 2 if tr.get('align', 'center') == 'center' else int(sg['f0'])
        z = a + F - 1
        for sj in (si - 1, si):
            if sj < 0:
                continue
            s2, keep = segs[sj], []
            for fx in s2.get('fx', []):
                L = EDGE_ACCENTS.get(fx.get('type'))
                if L and fx.get('type') == 'zoom.punch' and fx.get('mode') in ('hold', 'speech'):
                    L = 1 + int(fx.get('attack', 0) or 0)   # a held punch moves only on its jump
                mid = fx.get('move') or fx.get('type')
                ts = fx.get('times')
                if L is None or mid in req or not isinstance(ts, list) or not all(isinstance(t, (int, float)) for t in ts):
                    keep.append(fx)
                    continue
                left = []
                for t in ts:
                    h = int(math.floor(float(t) * fps + 0.4))
                    hit = (h <= a - 1 and h + L >= a - 2) if sj < si else (h <= z + 2 and h + L >= z + 1)
                    if hit:
                        out.append((sj, mid, h))
                    else:
                        left.append(t)
                if left:
                    fx['times'] = left
                    keep.append(fx)
            s2['fx'] = keep
    for sj, mid, h in out:
        sl = P.slots_by_seg.get(sj) or {}
        if sl.get('moves'):
            sl['moves'] = [m for m in sl['moves'] if not (m.get('id') == mid and m.get('f') == h)]
        P.skip(mid, f'hit at frame {h} would move the picture next to a hard transition (the transition is the hit)')
    return out


def _style_pass(P, sty, plan):
    """Apply a style after the genre program: its looks on every shot (light leaks on about a third of them), the
    planned style transitions (an added transition only on a plain cut; a genre transition is re-skinned only by one
    no longer than itself), whooshes under fast style transitions, the sound style. Records meta.choices."""
    if not sty:
        return {}
    st, fps, segs = sty['preset'], P.fps, P.segs
    r = np.random.default_rng(sty['seed'] + 11)
    lk = style_look(sty)
    lk_types = {f.get('type') for f in (lk or {}).get('fx', [])}
    LOOK_TYPE = {'fx.film_overlay': 'film_overlay', 'light.halation': 'glow', 'fx.glow': 'glow', 'lens.vignette': 'vignette',
                 'fx.light_leak': 'light_leak'}
    looks = []
    for mid in st.get('looks') or []:
        if LOOK_TYPE.get(mid) in lk_types:
            continue                                     # the ed_fx look already carries it
        ok, why = move_allowed(P.g, mid)
        if not ok and why in ('forbidden by the user', 'forbidden by the genre card', 'the move card forbids this genre', 'no move card'):
            P.skip(mid, f'style look: {why}')
            continue
        looks.append(mid)
    if lk is not None:                                   # the look's fx on every shot (tagged with the look)
        TEXTURE = {'film_overlay': 'texture', 'grain': 'texture'}
        own = {TEXTURE.get(f_.get('type'), f_.get('type')) for f_ in lk['fx']}
        replaced = set()
        for si, s in enumerate(segs):
            sl = P.slots_by_seg.get(si) or {}
            if sl.get('kind') == 'black' or s.get('speed') == 0.0:
                continue
            # the look is the finished treatment: a constant vignette / texture / glow / clarity the genre program
            # already put on the shot gives way to the look's own (two vignettes stacked crush the picture)
            keep = []
            for fx in s.get('fx', []):
                fam = TEXTURE.get(fx.get('type'), fx.get('type'))
                if (fam in own and fam in ('vignette', 'texture', 'glow', 'clarity') and not fx.get('look')
                        and not fx.get('times') and not fx.get('frames') and not fx.get('t')):
                    replaced.add((fx.get('move') or fx.get('type'), fx.get('type')))
                    if sl.get('moves'):
                        sl['moves'] = [m for m in sl['moves'] if m.get('id') != fx.get('move')]
                    continue
                keep.append(fx)
            s['fx'] = keep
            have = {(fx.get('type'), fx.get('look')) for fx in s.get('fx', [])}
            for f_ in lk['fx']:
                if (f_.get('type'), f_.get('look')) in have:
                    continue
                d = dict(f_)
                d.setdefault('look', lk['name'])
                d['move'] = 'look'
                s.setdefault('fx', []).append(d)
        for mid, typ in sorted(replaced):
            P.skip(mid, f"the {lk['name']} look carries its own {typ}")
    leak_every = 3
    for si, s in enumerate(segs):
        sl = P.slots_by_seg.get(si) or {}
        if sl.get('kind') == 'black' or s.get('speed') == 0.0:
            continue
        have = {fx.get('type') for fx in s.get('fx', [])}
        for mid in looks:
            if mid == 'fx.light_leak' and (si + sty['variant']) % leak_every:
                continue
            d = _look_fx(mid, r, P, si)
            if d is None or (d['type'] in have and d['type'] != 'light_leak'):
                continue
            d['move'] = mid
            s.setdefault('fx', []).append(d)
            have.add(d['type'])
            P._log(si, mid, None, f'style {sty["name"]}: look')
    swaps = 0
    if sty['variant']:                       # move picks: some beat accents change family or character, same beats
        rs = np.random.default_rng(sty['seed'] + 29)
        ACC = ('zoom.punch', 'shake.beat', 'zoom.in_out')
        for si, s in enumerate(segs):
            sl = P.slots_by_seg.get(si) or {}
            part = sl.get('part')
            for j, fx in enumerate(list(s.get('fx', []))):
                mid0 = fx.get('move')
                if mid0 not in ACC or not fx.get('times') or rs.uniform() >= 0.45:
                    continue
                alts = [m for m in ACC if m != mid0 and move_allowed(P.g, m, part)[0]]
                other = alts[int(rs.integers(len(alts)))] if alts else mid0
                t = float(fx['times'][0])
                if other == 'shake.beat':        # another family, or the same move with another character
                    prof = [k_ for k_ in ('impact', 'heavy', 'soft') if k_ != fx.get('profile')] if other == mid0 else ['impact', 'heavy']
                    d = dict(type='shake.beat', **P_SHAKE[prof[int(rs.integers(len(prof)))]], seed=int(round(t * 100)) + sty['variant'],
                             times=list(fx['times']), move=other)
                elif other == 'zoom.punch':
                    kinds = [k_ for k_ in ('bounce', 'strong', 'hold') if not (other == mid0 and P_PUNCH[k_]['scale'] == fx.get('scale'))]
                    d = dict(type='zoom.punch', **P_PUNCH[kinds[int(rs.integers(len(kinds)))]], center=_center(s), times=list(fx['times']),
                             move=other)
                else:
                    d = dict(type='zoom.in_out', scale=round(float(rs.choice([1.2, 1.3, 1.4])), 2), stroke=round(P.period / 2, 3), hold=0,
                             center=_center(s), times=list(fx['times']), move=other)
                s['fx'][j] = d
                swaps += 1
                k = frame_at(t, fps) - s['f0']
                for m in sl.get('moves', []):
                    if m['id'] == mid0 and m.get('k') == k:
                        m.update(id=other, why=f'{m.get("why", "")} (version {sty["variant"]}: {other}'
                                               + (f' {d.get("profile") or d.get("mode") or ""}' if other == mid0 else f' instead of {mid0}') + ')')
                        break
                if other != mid0:
                    P.count[mid0] = max(0, P.count.get(mid0, 1) - 1)
                    P.count[other] = P.count.get(other, 0) + 1
    placed = {}
    for i, (mid, nfr) in sorted(plan.items()):
        si = next((k for k, sl in P.slots_by_seg.items() if sl.get('i') == i), None)
        if si is None or si == 0:
            continue
        s = segs[si]
        cur = s.get('transition_in')
        kind, d = _move_fx(mid, fps, s.get('crop', {}).get('center'), P.period, 0, dict(frames=nfr))
        if kind != 'transition':
            continue
        if cur:
            if cur.get('move') == mid:
                continue
            if cur.get('kind') == 'flash' and P.slots_by_seg[si].get('role') == 'drop_first':
                continue                                   # the hit into the drop stays the genre's
        if d['kind'] == 'flash':
            if not P.flash_ok(s['f0']):
                continue
            P.flash_frames.append(s['f0'])
        d['move'] = mid
        s['transition_in'] = d
        P._log(si, mid, 0, f'style {sty["name"]}: transition')
        placed[s['f0']] = mid
        part = P.slots_by_seg[si].get('part')
        if d['kind'] in ('whip', 'zoom', 'spin') and P.ok('sfx.whoosh', part):
            P.sfx('sfx.whoosh', 'whoosh', s['f0'] / fps, f'whoosh under the {d["kind"]} (style)', variant='air', align='peak', dur=0.5)
    if st.get('sfx_style'):
        P.e['audio']['sfx_style'] = st['sfx_style']
    return dict(looks=looks, look=(dict(name=lk['name'], intensity=lk.get('intensity')) if lk else None),
                transitions_placed=placed, accent_swaps=swaps)


def _style_choices(edl, sty, slots, looks_info):
    """meta.choices: what this version picked, so the next version can avoid it."""
    segs = edl['segments']
    trs = {}
    for s in segs[1:]:
        tr = s.get('transition_in')
        if tr:
            trs[str(s['f0'])] = tr.get('move', tr.get('kind'))
    g0 = next((s.get('grade') for s in segs if s.get('grade')), {}) or {}
    return dict(style=sty['name'], variant=sty['variant'], seed=sty['seed'], match=sty['match'], dark=bool(sty.get('dark')),
                transitions=sorted(set(trs.values())), transitions_at=trs, looks=(looks_info or {}).get('looks', []),
                look=(looks_info or {}).get('look') or ((dict(name=style_look(sty)['name'], intensity=style_look(sty).get('intensity'))
                                                        if style_look(sty) else None)),
                look_pick=(dict(i=look_pick(sty)[0], name=look_pick(sty)[1], intensity=look_pick(sty)[2],
                                rotation=[n for n, _ in look_rotation(sty['preset'])]) if look_pick(sty) else None),
                grade={k: g0.get(k) for k in ('preset', 'temp', 'tint', 'sat', 'contrast', 'gamma', 'black', 'lift', 'fade', 'gain')
                       if g0.get(k) is not None},
                nuance=_style_nuance(sty), caption_style=_caption_style(sty), sfx_style=sty['preset'].get('sfx_style'),
                accent_swaps=(looks_info or {}).get('accent_swaps', 0),
                sfx_level=sty['preset'].get('sfx_level'),
                shots=[[sl['i'], (sl.get('pick') or {}).get('shot'), (sl.get('pick') or {}).get('w0')] for sl in slots
                       if sl.get('pick')],
                ramps=[[sl['i'], sl['speed'].get('pattern'), sl['speed'].get('at_beat'), sl['speed'].get('fast'), sl['speed'].get('slow'),
                        sl['speed'].get('dec_frames'), sl['speed'].get('acc_frames'), sl['speed'].get('exit_beat'), sl['speed'].get('fast_out')]
                       for sl in slots if (sl.get('speed') or {}).get('mode') == 'ramp'])


def _caption_style(sty):
    if not sty:
        return None
    cs = sty['preset'].get('caption_style')
    return CAPTION_SIBLING.get(cs, cs) if (cs and sty['variant'] % 2 == 1) else cs


# ============================================================================ plan_genre
def _slot_times(s, fps, grid, parts):
    """Per-frame source offsets (s['_times']), source length needed and the accent offsets of one slot."""
    rel_beats = s['beat_rel']
    mode = s['speed']['mode']
    if mode == 'stutter':
        s['speed']['frag_s'] = grid.period / 4
    if mode == 'ramp':
        inner = [b for b in rel_beats if b > 1e-3]
        ia = int(round(s['speed'].get('at_beat', 1.0))) - 1
        s['speed']['at'] = inner[ia] if 0 <= ia < len(inner) else (inner[0] if inner else None)
        ie = s['speed'].get('exit_beat')
        te = inner[int(round(ie)) - 1] if (ie is not None and 0 <= int(round(ie)) - 1 < len(inner)) else None
        if te is not None and s['speed']['at'] is not None and te - s['speed']['at'] >= 0.3:
            s['speed']['exit'] = te
        else:
            s['speed'].pop('exit', None)
        s['_times'] = speed_times(s, fps, inner)
    else:
        s['_times'] = speed_times(s, fps, rel_beats)
    s['src_need'] = float(s['_times'].max() + 1.0 / fps) if s['kind'] != 'black' else 0.0
    # accent offsets (source seconds from window start) where an action peak should land
    if mode == 'velocity':
        s['accent_offsets'] = sorted({round(float(s['_times'][min(len(s['_times']) - 1, int(round(b * fps)))]), 3) for b in rel_beats})
    elif mode == 'slow' and s['role'] == 'drop_first':
        s['accent_offsets'] = [0.05, 0.15]
    elif mode == 'slow':
        s['accent_offsets'] = [round(0.55 * s['src_need'], 3)]
    elif mode == 'ramp':
        k = int(round((s['speed'].get('at') or 0) * fps))
        s['accent_offsets'] = [round(float(s['_times'][min(k, len(s['_times']) - 1)]), 3)]
    elif mode == 'ramp_freeze':
        kf = frame_at(parts['outro']['t0'], fps) - s['f0']
        s['accent_offsets'] = [round(float(s['_times'][min(max(kf, 0), len(s['_times']) - 1)]), 3)]
    else:
        s['accent_offsets'] = sorted({round(b, 3) for b in rel_beats if b > 0.05})[:3] or [round(0.3 * s['src_need'], 3)]


def _set_speed(s, speed, fps, grid, parts, note=None):
    s['speed'] = dict(speed)
    _slot_times(s, fps, grid, parts)
    if note:
        s['note_speed'] = note


def _fill_gaps(slots, F, g, ctx, fps, grid, parts):
    """Slots the footage cannot serve: no source window of the needed length (or the given clip is too short) ->
    the longest suitable shot, slowed down to fit when needed; a reused range or an unreadable hero shot is also
    reported. Returns meta.gaps entries (each one is a brief for a generated shot, edit-gen)."""
    gaps = []
    given = ctx.get('given') or {}
    by_i = {s['i']: s for s in slots}
    want = {'drop_first': 'the best action shot of the video: a readable subject, a motion peak on the first beat',
            'hook': 'a strong opening image: a face to camera, a silhouette or a scale shot',
            'outro': 'a calm wide shot', 'freeze': 'a sharp peak moment for the freeze', 'crash': 'a face or a detail to zoom into'}
    for s in slots:
        if s['kind'] == 'black':
            continue
        out_dur = (s['f1'] - s['f0'] + 1) / fps
        kind = reason = fill = None
        if not s.get('pick'):
            pin = given.get(s['i'])
            pool = [sh for sh in F.shots if pin is None or sh['ci'] == pin] or F.shots
            sh = max(pool, key=lambda x: (x['dur'], -x['i']))
            avail = max(0.05, sh['t1'] - sh['t0'] - 0.08)
            if s['src_need'] > avail:
                rate = max(0.25, min(1.0, avail / out_dur))
                if s['speed']['mode'] != 'normal' and avail >= out_dur:
                    _set_speed(s, dict(mode='normal'), fps, grid, parts, f"{s['speed']['mode']}: the clip is too short for it")
                else:
                    _set_speed(s, dict(mode='slow', rate=round(rate, 3)), fps, grid, parts, f'stretched to {rate:.2f}x to fill the slot')
                kind = 'stretched'
            else:
                kind = 'reused'
            w0 = sh['t0'] + 0.04
            w1 = min(sh['t1'], w0 + s['src_need'])
            W = F.win(sh, w0, w1)
            s['pick'] = dict(shot=sh['id'], ci=sh['ci'], src=sh['src'], w0=round(w0, 3), w1=round(w1, 3), score=-9.0, W=W,
                             tags=['gap fill'], n_cands=0, alts=[])
            reason = ('the given clip is shorter than this slot needs' if pin is not None
                      else f'no shot is {s["src_need"]:.2f} s long')
            fill = f'{sh["id"]}' + (f' at {s["speed"].get("rate", 1):.2f}x' if s['speed']['mode'] == 'slow' else '')
        else:
            pk = s['pick']
            if 'reused range' in pk.get('tags', []):
                kind, reason, fill = 'reused', 'too little footage: a source range is shown twice', pk['shot']
            elif s['role'] in ('drop_first', 'hook', 'freeze') and pk['W'].get('readable', 1) < 0.3 and not ctx.get('given'):
                kind, reason, fill = 'weak', f'no readable {s["role"]} shot in the footage ({pk["W"].get("subject")})', pk['shot']
        if kind:
            nb = [by_i.get(s['i'] - 1), by_i.get(s['i'] + 1)]
            s['gap'] = kind
            gaps.append(dict(slot=s['i'], part=s['part'], role=s['role'], kind=kind, reason=reason, fill=fill,
                             t=[s['t0'], s['t1']], f=[s['f0'], s['f1']], dur=round(out_dur, 3), need_s=round(s['src_need'], 3),
                             brief=dict(want=want.get(s['role'], f'a {s["part"]} shot'), speed=s['speed']['mode'],
                                        neighbours=[(x.get('pick') or {}).get('W', {}).get('size') if x else None for x in nb])))
    return gaps


def plan_genre(track, footage, genre_slug, canvas=(1080, 1920), fps=30, dur=None, **opts):
    """Track + footage + genre -> EDL dict (TIMELINE.md). Speech genres (card kind 'speech': clips, ugc, explainer)
    go to plan_speech (cut by words); motivation is a music edit with the voice-over laid on top.
    opts: cache_dir, seed, reframe (True), sample_fps (6), title, word, outro_text, log (callable or None),
      music (precomputed analysis), footage_obj (Footage);
      n_shots (exact shot count), order 'auto'|'given' (shot i = footage item i), require_moves / forbid_moves (ids or
      families; required moves are placed even where the card does not list them), music_in (alias start: track second
      at output 0), drop_at (output second where the drop lands; with music_in it names the drop beat), drop_t (track
      second of the drop, overrides the detector), bpm (tempo hint), bars (length in bars), cut_rate (x the card's
      cutting rate), sfx_level none|light|genre|heavy, in_sequence first|middle|last (a part of an ed_sequence composite:
      opening / closing structure only on the first / last part, no letterbox changes);
      speech: words (list | transcript | JSON path), lang, asr_model, voice (voice-over file), src_in / src_out or
      from / to phrases, subtitles karaoke|subtitle|none, music_db.
    footage: paths or dicts {path, name, role ('aroll' | 'broll' | 'voice'), weight, t0, t1}."""
    log = opts.get('log', print) or (lambda *a, **k: None)
    t_start = time.time()
    sty = style_context(opts.get('style'), genre_slug or None, opts.get('variant'), opts.get('avoid'))
    if sty and (sty.get('match') or {}).get('matched') is False:
        log(f"[plan] {sty['match']['why']}")                   # e.g. words in another language: translate them first
    if not genre_slug:
        if sty is None or not sty['name']:
            raise ValueError('plan_genre needs a genre or a style')
        genre_slug = sty['preset']['genre']
    g0 = load_genre(genre_slug)
    o = norm_opts(opts, g0)
    if sty:
        st_ = sty['preset']
        o['forbid'] = sorted(set(o['forbid']) | {m for m in st_['moves'].get('avoid', []) if m not in o['require']})
        if opts.get('cut_rate') in (None, ''):
            o['cut_rate'] = min(4.0, max(0.25, float((st_.get('pacing') or {}).get('cut_rate', 1.0))))
        if opts.get('sfx_level') in (None, '') and st_.get('sfx_level'):
            o['sfx_level'] = 'light' if st_['sfx_level'] == 'light' else 'genre'
        o['seed'] = int(o.get('seed', 1)) + 1009 * sty['variant']
        log(f'[style] {sty["name"] or "(genre card)"} (variant {sty["variant"]}): {sty["match"]["why"]}')
    g = genre_view(g0, o['require'], o['forbid'])
    if sty:                                              # the style's preferred moves join the genre's part lists
        for mid in sty['preset']['moves'].get('prefer', []):
            ok_, why_ = move_allowed(g, mid)
            if move_card(mid) is None or why_ in ('forbidden by the user', 'forbidden by the genre card', 'the move card forbids this genre'):
                continue
            for p_ in PARTS:
                if mid not in g['part_moves'][p_]:
                    g['part_moves'][p_] = list(g['part_moves'][p_]) + [mid]
            if mid not in g['allowed']:
                g['allowed'] = sorted(set(g['allowed']) | {mid})
    speech_note = None
    o['_style'] = sty
    if g['kind'] == 'speech' and g['slug'] != 'motivation':
        if o.get('words') is not None or _has_voice(footage):
            try:
                return plan_speech(track, footage, g, canvas, fps, dur, o, log)
            except NoSpeech as ex:
                if not track:
                    raise
                speech_note = f'{ex}: cut to the track beats instead (no word grid)'
        elif not track:
            raise ValueError(f'{g["slug"]} cuts by words: the footage has no audio and no words= were given')
        else:
            speech_note = 'speech genre without speech in the footage: cut to the track beats (no word grid)'
        log(f'[plan] {speech_note}')
    seed = int(o.get('seed', 1))
    rng = np.random.default_rng(seed) if not (sty and sty['variant']) else _ScaledRng(np.random.default_rng(seed), 6.0)
    cache = o.get('cache_dir')
    W_, H_ = canvas
    voice_item = None
    if g['slug'] == 'motivation':                       # the voice-over is laid on the music edit afterwards
        footage, voice_item = _split_voice(footage, o)
    # ---- 1. music
    mus = o.get('music') or analyze_music(track, cache, o.get('bpm'))
    grid = Grid(mus)
    if o['drop_t'] is not None and o['music_in'] is None and o['drop_at'] is None:
        a_, _ = drop_anchor(mus, grid, o['drop_t'])
        mus = dict(mus, drops=[dict(t=a_, bar=None, jump_db=None, user=True)])
    if o['bars'] and not dur and o['music_in'] is None and o['drop_at'] is None:
        dur = o['bars'] * 4 * grid.period
    fixed = o['music_in'] is not None or o['drop_at'] is not None
    if fixed:
        win = fixed_window(mus, grid, g, dur, o['music_in'], o['drop_at'], o['drop_t'], o['bars'])
        parts = map_parts_fixed(win, grid, g)
    else:
        win = choose_window(mus, grid, g, dur)
        parts = map_parts(win, grid, g)
    T = win['t_out'] - win['t_in']
    n_frames = int(round(T * fps))
    log(f'[music] {mus["bpm"]} BPM, window {win["t_in"]:.2f}–{win["t_out"]:.2f} s ({win["n_bars"]:.2f} bars): {win["why"]}')
    beats = []
    for j in range(win['j0'], win['j1']):
        t = grid.time(j) - win['t_in']
        if t >= T - 1e-3:
            break
        rel = j - win['j0']
        part = next((p for p in PARTS if parts[p]['beat0'] <= rel < parts[p]['beat1']), 'outro')
        beats.append(dict(j=rel, t=round(t, 4), f=frame_at(t, fps), bar=rel // 4, pos=(j - grid.phase) % 4, down=grid.is_down(j),
                          kick=round(float(grid.kick[j]), 3), snare=round(float(grid.snare[j]), 3), onset=round(float(grid.onset[j]), 3),
                          fill=round(float(grid.fill[j]), 3), part=part))
    # ---- 2. footage
    F = o.get('footage_obj') or Footage(footage if isinstance(footage, (list, tuple)) else [footage], cache, o.get('sample_fps', 6.0), log)
    # ---- 3. slots
    nb_total = float(win.get('n_beats') or (win['j1'] - win['j0']))
    if o['n_shots']:
        slots = slots_n(o['n_shots'], parts, grid, win, g)
    else:
        slots = build_slots(g, parts, grid, win, rng, o)
        slots = apply_cut_rate(slots, o['cut_rate'], grid, win['j0'], g)
    slots = [s for s in slots if s['b0'] < nb_total - 1e-6]
    btime = lambda b: min(T, grid.time(win['j0'] + b) - win['t_in'])   # noqa: E731
    for s in slots:
        s['t0'], s['t1'] = round(btime(s['b0']), 4), round(btime(s['b1']), 4)
        s['f0'], s['f1'] = frame_at(s['t0'], fps), frame_at(s['t1'], fps) - 1
    slots = [s for s in slots if s['f1'] >= s['f0']]
    slots[-1]['f1'] = n_frames - 1
    for i, s in enumerate(slots):
        s['i'] = i
        if i:
            s['f0'] = slots[i - 1]['f1'] + 1
    _required_speeds(slots, g, o, grid.period)
    floor = slow_floor(min((float(c['info'].get('fps') or 25.0) for c in F.clips), default=25.0), bool(o.get('interp')))
    ramp_choices = _ramp_patterns(slots, sty, o, floor)
    for s in slots:
        s['beat_rel'] = [b['t'] - s['t0'] for b in beats if s['t0'] - 1e-4 <= b['t'] < s['t1'] - 1e-4]
        _slot_times(s, fps, grid, parts)
    longest = max((sh['dur'] for sh in F.shots), default=0.0) - 0.4
    for s in slots:                                  # a ramp never asks for more source than the footage has
        sp = s.get('speed') or {}
        if sp.get('mode') == 'ramp' and longest > 0.5 and s['src_need'] > longest:
            k = max(0.6, longest / s['src_need'])
            sp['fast'] = round(max(1.6, float(sp['fast']) * k), 2)
            if sp.get('fast_out'):
                sp['fast_out'] = round(max(1.6, float(sp['fast_out']) * k), 2)
            _slot_times(s, fps, grid, parts)
            for row in ramp_choices:
                if row[0] == s['i']:
                    row[3], row[8] = sp['fast'], sp.get('fast_out')
    # velocity budget (time.velocity: ≤ 50 % of the video)
    vel = [s for s in slots if s['speed']['mode'] == 'velocity']
    if vel:
        budget = 0.5 * T
        acc = 0.0
        for s in vel:
            d = s['t1'] - s['t0']
            if acc + d > budget + 1e-6 and not s['speed'].get('required'):
                _set_speed(s, dict(mode='normal'), fps, grid, parts, 'velocity budget 50 % — normal speed')
            else:
                acc += d
    # handles for centred transitions (calm dissolves, epic dips)
    for i, s in enumerate(slots):
        if g['slug'] == 'calm' and i > 0:
            sec = 2.0 if s['role'] == 'drop_first' else (1.75 if s['part'] in ('drop', 'outro') else 1.25)
            h = sec / 2 + 0.05
            s['handle_in'] = h * (s['speed'].get('rate', 1.0) if s['speed']['mode'] == 'slow' else 1.0)
            slots[i - 1]['handle_out'] = h * (slots[i - 1]['speed'].get('rate', 1.0) if slots[i - 1]['speed']['mode'] == 'slow' else 1.0)
        if s.get('dip'):
            s['handle_in'] = 6 / fps
            if i:
                slots[i - 1]['handle_out'] = max(slots[i - 1].get('handle_out', 0), 6 / fps)
    style_plan = _style_transition_plan(slots, sty, g, fps, grid.period)
    # ---- 4. assignment
    def beat_db_of(s):
        return grid.energy_db(win['t_in'] + s['t0'], win['t_in'] + s['t1'])
    style_note = sty['match']['why'] if (sty and (sty.get('match') or {}).get('matched') is False) else None
    ctx = dict(fps=fps, T=T, parts=parts, notes=list(win.get('notes') or []) + ([speech_note] if speech_note else [])
               + ([style_note] if style_note else []), beat_db_of=beat_db_of,
               noise=_style_noise(sty), avoid_win=_avoid_windows(sty))
    if o['order'] == 'given':
        vis = [s for s in slots if s['kind'] != 'black']
        ctx['given'] = {s['i']: k % len(F.clips) for k, s in enumerate(vis)}
        if len(F.clips) != len(vis):
            ctx['notes'].append(f'order=given: {len(F.clips)} clips for {len(vis)} shots — the clips repeat in order'
                                if len(F.clips) < len(vis) else f'order=given: only the first {len(vis)} of {len(F.clips)} clips are used')
    assign(slots, F, g, ctx, log)
    # a ramp that found no source long enough, or only static footage, plays at normal speed (unless required)
    retry = []
    for s in slots:
        if s['kind'] == 'black' or s['speed']['mode'] in ('normal', 'freeze'):
            continue
        pk = s.get('pick')
        static_ramp = pk is not None and s['speed']['mode'] == 'ramp' and pk['W']['motion_r'] < 0.3 and not s['speed'].get('required')
        if pk is None or static_ramp:
            note = (f"{s['speed']['mode']}: no source window of the needed length — normal speed" if pk is None
                    else 'ramp: the chosen shot has no real motion — normal speed')
            s['pick'] = None
            _set_speed(s, dict(mode='normal'), fps, grid, parts, note)
            retry.append(s)
    if retry:
        assign(slots, F, g, ctx, log)
    for _ in range(3 if o.get('check_dark', True) else 0):
        if not _dark_check(slots, F, g, ctx, fps, log):
            break
        assign(slots, F, g, ctx, log)
    for _ in range(3 if o.get('check_flash', True) else 0):
        cl = _flash_check(slots, F, g, ctx, fps, sty, qa_flash_hz(g['slug']))
        if not cl:
            break
        for s in cl:
            if s.pop('_speed_reset', False):
                _set_speed(s, dict(mode='normal'), fps, grid, parts, 'velocity flickers on this footage - normal speed')
        assign(slots, F, g, ctx, log)
    for _ in range(3 if o.get('check_cuts', True) else 0):
        if not _cut_check(slots, F, ctx, log):
            break
        assign(slots, F, g, ctx, log)
    _loop_end(g, slots, F, ctx)
    gaps = _fill_gaps(slots, F, g, ctx, fps, grid, parts)
    if gaps:
        ctx['notes'] += [f"gap at {x['t'][0]:.2f}–{x['t'][1]:.2f} s ({x['role']}): {x['reason']}" for x in gaps]
    # black slots continue the previous source (frozen)
    # ---- build segments
    sources, src_names = {}, {}
    segs, by_seg = [], {}
    for s in slots:
        if s['kind'] == 'black':
            prev = segs[-1] if segs else None
            if prev is None:
                continue
            sg = dict(id=f'C{len(segs) + 1:02d}', f0=s['f0'], f1=s['f1'], src=prev['src'], t=round(prev.get('t', 0), 4), speed=0.0,
                      crop=copy.deepcopy({k: v for k, v in prev['crop'].items() if k != 'path'}), border='black',
                      grade=dict(prev.get('grade', {})), fx=[], note=f'{s["part"]} · black pause')
            if prev['crop'].get('path'):
                sg['crop'].update(cx=prev['crop']['path'][-1][1], cy=prev['crop']['path'][-1][2], z=prev['crop']['path'][-1][3])
            by_seg[len(segs)] = s
            segs.append(sg)
            continue
        pk = s.get('pick')
        if pk is None:
            raise RuntimeError(f'slot {s["i"]} ({s["role"]}, {s["t0"]:.2f}s) has no footage — add more clips')
        clip = F.clips[pk['ci']]
        bx = clip.get('box')
        full = [0, 0, clip['info'].get('w'), clip['info'].get('h')]
        sources.setdefault(clip['name'], dict(path=clip['path'], **({'box': bx} if bx and bx != full else {})))
        times = pk['w0'] + s['_times']
        sg = dict(id=f'C{len(segs) + 1:02d}', f0=s['f0'], f1=s['f1'], src=clip['name'], t=round(float(times[0]), 4))
        mode = s['speed']['mode']
        if mode == 'normal':
            sg['speed'] = 1.0
        elif mode == 'slow':
            sg['speed'] = s['speed']['rate']
            sg['interp'] = 'flow'
        else:
            sg['times'] = [round(float(x), 4) for x in times]
            if mode in ('velocity', 'ramp', 'ramp_freeze'):
                rates = np.diff(times) * fps
                rates = np.append(rates, rates[-1] if len(rates) else 1.0)
                sg['speed_curve'] = [[int(k), round(float(r), 3)] for k, r in enumerate(rates)]
                sg['interp'] = 'flow'
            if mode == 'stutter':
                sg['stutter'] = dict(frag_frames=int(max(2, round(s['speed']['frag_s'] * fps))), repeats=int(math.ceil(len(times) / max(2, round(s['speed']['frag_s'] * fps)))))
        sg['_mode'] = mode
        bx = clip.get('box') or [0, 0, clip['info'].get('w') or 16, clip['info'].get('h') or 9]
        sg['_src_aspect'] = (bx[2] - bx[0]) / max(1, bx[3] - bx[1])
        sg['_src_h'] = bx[3] - bx[1]
        sg['_out_h'] = H_
        sg['crop'] = _crop_for(clip, pk, s, times, fps, W_ / H_, opts.get('reframe', True))
        sg['_center'] = sg['crop']['center'] = sg['crop'].pop('_center', [0.5, 0.45])   # subject in output fractions (punch/crash centre)
        sg['_win_w'] = sg['crop'].pop('_win_w', None)
        sg['border'] = 'reflect'
        sg['grade'] = style_grade(g['slug'], sty)
        cxs = [p_[1] for p_ in sg['crop']['path']] if sg['crop'].get('path') else [sg['crop'].get('cx', 0.5)]
        cl = F.crop_luma(pk['ci'], float(times.min()), float(times.max()) + 1.0 / fps, float(np.median(cxs)), sg['_win_w'] or 0.32)
        Wp = pk['W']
        ev = exposure_ev(g['slug'], cl, Wp.get('p99'), Wp.get('face_luma') if (Wp.get('face_share') or 0) >= 0.3 else None)
        sg['_crop_luma'] = round(cl, 1)
        if ev:
            sg['grade']['exposure'] = ev
        sg['fx'] = []
        W = pk['W']
        sg['note'] = f'{s["part"]} · {s["role"]} · {W["size"]}' + (f' · {mode}' if mode != 'normal' else '') + \
            (f' · gap ({s["gap"]})' if s.get('gap') else '')
        by_seg[len(segs)] = s
        segs.append(sg)
    _match_burst_exposure(segs, by_seg)
    edl = dict(canvas=dict(w=W_, h=H_, fps=fps), n_frames=n_frames, frame_interp='flow', sources=sources,
               audio=dict(copy=False, music=dict(path=os.path.abspath(track), **{'in': round(win['t_in'], 4)}, gain_db=0.0, fade_in=0.0,
                                                 fade_out=0.0), voice=[], sfx=[], duck=[], loudness=dict(lufs=-14, tp=-1)),
               segments=segs, ops=[], texts=[], layers=[], qa={}, meta={})
    edl['audio']['grid'] = dict(bpm=mus['bpm'], beats=[b['t'] for b in beats],
                                downbeats=[b['t'] for b in beats if b['pos'] == 0])
    # ---- 5. moves
    Pl = Placer(g, edl, slots, beats, parts, fps, T, win['t_in'])
    Pl.slots_by_seg = by_seg
    Pl.period = grid.period
    Pl.heterogeneous = F.heterogeneous
    Pl.title, Pl.word, Pl.outro_text = o.get('title'), o.get('word'), o.get('outro_text')
    Pl.planned_black, Pl.planned_freeze, Pl.n_build_impacts = [], [], 0
    Pl.beat_time = lambda b: btime(b)
    t_drop_abs = win['t_in'] + parts['drop']['t0']
    bar_s = 4 * grid.period                       # sfx.riser anti_double: does the track rise by itself over 2 bars?
    Pl.rise_db = grid.energy_db(t_drop_abs - 0.5 * bar_s - 2 * grid.period, t_drop_abs - 0.05) - \
        grid.energy_db(t_drop_abs - 2 * bar_s, t_drop_abs - 1.5 * bar_s)
    Pl.notes = ctx['notes']
    Pl.opts = o
    Pl.fixed = fixed
    PROGRAMS.get(g['slug'], program_generic)(Pl)
    style_info = _style_pass(Pl, sty, style_plan)
    _text_layers(Pl)
    _sequence_context(Pl, o['in_sequence'])
    _require_moves(Pl)
    _calm_transition_edges(Pl)
    _cap_fx(Pl)
    _sfx_pass(Pl, o['sfx_level'])
    if sty:
        _style_levels(edl, sty, Pl)
    _gen_hints(g, slots, Pl)
    if voice_item is not None:
        _lay_voiceover(edl, Pl, voice_item, o, log)
    faces = {}
    for si_, sg_ in enumerate(segs):
        W_f = ((by_seg.get(si_) or {}).get('pick') or {}).get('W') or {}
        if W_f.get('face_cx') is not None and (W_f.get('face_share') or 0) >= 0.3 and W_f.get('face_h'):
            faces[sg_['id']] = (W_f['face_cx'], W_f.get('face_cy') or 0.4, W_f['face_h'])
    dark = bool(o.get('dark')) or bool(sty and sty.get('dark'))
    pairs = _plain_cut_pairs(edl, by_seg) if g['slug'] in LUMA_MATCH_GENRES else None
    fit = _fit_grades(edl, g['slug'], faces=faces, limits=PICTURE_LIMITS_DARK if dark else PICTURE_LIMITS,
                      cut_pairs=pairs) if o.get('fit_grades', True) else {}
    # ---- 6. qa, 7. meta
    edl['qa'] = _qa_block(g, edl, slots, Pl, beats, fps)
    _relax_p99_for_capped(edl, fit)
    edl['meta'] = _meta(g, edl, slots, by_seg, Pl, mus, win, parts, beats, F, o, seed, cache, track, time.time() - t_start)
    if fit:
        edl['meta']['grade_fit'] = {sid: dict(after={k: (round(v, 3) if k == 'sat_mean' else round(100 * v, 2) if k.startswith('clip')
                                                         else round(v, 1)) for k, v in r['after'].items()},
                                              changed=r['changed'], **{k: r[k] for k in ('look', 'ev_cap', 'matched') if r.get(k) is not None})
                                    for sid, r in fit.items() if r['changed']}
    edl['meta']['style'] = sty['name'] if sty else None
    edl['meta']['variant'] = sty['variant'] if sty else 0
    if sty:
        edl['meta']['choices'] = _style_choices(edl, sty, slots, style_info)
    still = {s['i'] for s in slots if (s.get('speed') or {}).get('mode') == 'ramp'}
    ramp_choices = [r for r in ramp_choices if r[0] in still]
    if ramp_choices:                                     # the ramp curves of this version (no two in a row alike)
        edl['meta'].setdefault('choices', {})['ramps'] = ramp_choices
    edl['meta']['gaps'] = gaps
    edl['meta']['window_mode'] = 'fixed' if fixed else 'chosen'
    if voice_item is not None and getattr(Pl, 'voice_words', None):
        edl['qa'].update(words=Pl.voice_words, kind='speech_over_music')
    _finish_sfx(edl)
    for sg in segs:
        for k in [k for k in sg if k.startswith('_')]:
            sg.pop(k)
    log(f'[plan] {g["slug"]}: {len(segs)} segments, {n_frames} frames, moves {edl["meta"]["moves"]} ({time.time() - t_start:.0f}s)'
        + (f', {len(gaps)} gaps' if gaps else ''))
    return edl


def _face_safe(clip, times, cx, win_w, margin=0.012):
    """Never cut a face with the crop edge: a face partly inside the 9:16 window (12-88 % of its width) moves fully
    in when that keeps the main face inside, else fully out; one constant shift per segment (no jitter).
    Faces come from the clip analysis (box fractions). Returns (cx, note | None)."""
    if win_w >= 0.999 or not clip.get('rows'):
        return cx, None
    S = clip.get('_np') or _series(clip)
    ts = S['t']
    bx = clip.get('box') or [0, 0, clip['info'].get('w') or 16, clip['info'].get('h') or 9]
    ar = (bx[3] - bx[1]) / max(1.0, bx[2] - bx[0])
    lo_c, hi_c = win_w / 2, 1 - win_w / 2
    shifts, n_s = [], 0
    for k in range(0, len(times), 5):
        r = clip['rows'][int(np.clip(np.searchsorted(ts, times[k]), 0, len(ts) - 1))]
        fs = [f for f in (r.get('faces') or []) if f[2] >= 0.05 and f[3] >= 0.6]
        if len(fs) < 1:
            continue
        n_s += 1
        main = max(fs, key=lambda f: f[2])
        mw = 0.85 * main[2] * ar
        c = float(cx[k])
        need = 0.0
        for f in fs:
            fw = 0.85 * f[2] * ar
            a, b = f[0] - fw / 2, f[0] + fw / 2
            lo, hi = c - win_w / 2, c + win_w / 2
            inside = (min(b, hi) - max(a, lo)) / max(fw, 1e-6)
            if not (0.12 < inside < 0.88):
                continue
            opts = [(b - hi + margin) if b > hi else -(lo - a + margin)]          # bring it fully in
            if f is not main:
                opts.append(-(hi - a + margin) if b > hi else (b - lo + margin))  # push it fully out
            ok = []
            for d in opts:
                c2 = min(max(c + d, lo_c), hi_c)
                l2, h2 = c2 - win_w / 2, c2 + win_w / 2
                if main is f or (main[0] - mw / 2 >= l2 - 1e-6 and main[0] + mw / 2 <= h2 + 1e-6):
                    ok.append(c2 - c)
            if ok:
                need = min(ok, key=abs)
                break
        if need:
            shifts.append(need)
    if not shifts or len(shifts) < 0.3 * max(1, n_s):
        return cx, None
    d = float(np.median(shifts))
    return np.clip(cx + d, lo_c, hi_c), f'shifted {d:+.3f} so no face is cut by the frame edge'


def _crop_for(clip, pk, s, times, fps, out_aspect, reframe):
    """9:16 crop path from ed_reframe (face -> person -> motion saliency), sampled per output frame through the slot's
    source-time mapping; static centre on the shot's face when reframe is off."""
    info = clip['info']
    W0, H0 = info.get('w') or 16, info.get('h') or 9
    bx = clip.get('box') or [0, 0, W0, H0]
    bw, bh = bx[2] - bx[0], bx[3] - bx[1]
    src_aspect = bw / max(1, bh)
    win_w = min(1.0, out_aspect / src_aspect)
    to_box = lambda cx, cy: (np.clip((np.asarray(cx) * W0 - bx[0]) / bw, 0, 1), np.clip((np.asarray(cy) * H0 - bx[1]) / bh, 0, 1))
    W = pk['W']
    cx0 = W['face_cx'] if W.get('face_cx') is not None else 0.5
    cy0 = W['face_cy'] if W.get('face_cy') is not None else 0.5
    n = len(times)
    if reframe and win_w < 0.999:
        t0, t1 = float(times.min()), float(times.max())
        try:
            rf = RF.crop_path(clip['path'], t0, max(t1 - t0, 0.2), out_aspect=out_aspect)
        except Exception as ex:          # decoding hiccup: keep a static crop
            rf = dict(keys=[[0.0, cx0, cy0, None]], subject='center', win_w=win_w, error=str(ex))
        kt = [k[0] for k in rf['keys']]
        cx = np.interp(times - t0, kt, [k[1] for k in rf['keys']])
        cy = np.interp(times - t0, kt, [k[2] for k in rf['keys']])
        if rf.get('error') is None:
            cx, cy = to_box(cx, cy)                     # ed_reframe works on the full frame; the EDL crop on the box
        subject = rf['subject']
    else:
        cx, cy = np.full(n, cx0), np.full(n, cy0)
        subject = 'face' if W.get('face_cx') is not None else 'center'
    cx, moved = _face_safe(clip, times, np.asarray(cx, float), win_w)
    if moved:
        subject = f'{subject}; {moved}'
    ks = sorted(set(list(range(0, n, 3)) + [n - 1]))
    path = [[int(k), round(float(cx[k]), 4), round(float(cy[k]), 4), 1.0] for k in ks]
    # where the subject sits in the output frame (for punch / crash centres)
    if W.get('face_cx') is not None:
        wc = min(max(float(np.median(cx)), win_w / 2), 1 - win_w / 2)
        ox = 0.5 + (W['face_cx'] - wc) / win_w
        center = [round(min(0.85, max(0.15, ox)), 3), round(min(0.8, max(0.2, W['face_cy'])), 3)]
    else:
        center = [0.5, 0.45]
    return dict(cx=path[0][1], cy=path[0][2], z=1.0, path=path, subject=subject, _center=center, _win_w=win_w)


def _gen_hints(g, slots, P):
    """Holes in the plan that a generated shot would fill (scenario 4, edit-gen; paid — only with the user's yes)."""
    hints = []
    W = lambda role: next(((s.get('pick') or {}).get('W', {}) for s in slots if s['role'] == role and s.get('pick')), {})
    if g['slug'] == 'epic' and not W('hook').get('ews'):
        hints.append(dict(slot='hook', move='shot.extreme_wide', reason='the source footage has no extreme wide shot for the hook',
                          options=['zoom.out from a 4K wide shot (start ×2)', 'outpaint a simple background ×1.5–2',
                                   'generation: a small figure in a huge landscape (edit-gen, after the price is confirmed)']))
    if g['slug'] == 'calm' and (W('drop_first').get('p99') or 0) < 225:
        hints.append(dict(slot='drop_first', move='light.halation', reason='the best shot has no highlights — the "climax of light" is weak',
                          options=['the warmest wide shot + a little more zoom-in', 'generation: golden hour, highlights on water (edit-gen)']))
    if g['slug'] == 'phonk' and not (W('hook').get('low_angle') or (W('hook').get('face_luma') or 0) >= 40):
        hints.append(dict(slot='hook', move='angle.low', reason='no low angle / silhouette for the hook — the digital dutch tilt does the job',
                          options=['angle.dutch in code (already placed)', 'generation: a low-angle silhouette against the sky (edit-gen)']))
    P.notes.extend(f"gen-hint {h['slot']}: {h['reason']}" for h in hints)
    P.gen_hints = hints


def _text_layers(P):
    """type.beat_text (one word slapped on the drop's first beat) and type.kinetic (name on the final freeze) —
    only with user text; fonts are the engine's OFL files."""
    fps = P.fps
    if P.word:
        if P.ok('type.beat_text', 'drop'):
            f0 = frame_at(P.parts['drop']['t0'], fps)
            P.layer('type.beat_text', dict(kind='beat_text', f0=f0, f1=min(P.e['n_frames'] - 1, f0 + int(round(4 * P.period * fps)) - 1),
                                           slots=[dict(w=P.word.upper(), t=round(P.parts['drop']['t0'], 4), accent='downbeat')],
                                           layout='single', type_class='grotesk_condensed_black', font='grotesk_condensed_black', caps=True,
                                           size={'fit_width': 0.5, 'max': 0.13}, color='#FFFFFF', pos=[0.47, 0.45],   # ×1.6 slam peak stays in the safe zone
                                           anim_in=dict(kind='slam', scale=[1.6, 0.97, 1.0], frames=6 if fps >= 30 else 5),
                                           anim_out=dict(kind='cut'), invert_frames=2, shake=dict(amp=0.012, frames=7), safe_zone='tiktok'),
                    'slam word on the first beat of the drop (×1.6 → 0.97 → 1.0), holds 1 bar')
    if P.outro_text and P.g['slug'] == 'phonk':
        fr = [si for si, s in enumerate(P.segs) if P.slots_by_seg[si]['kind'] == 'freeze']
        if fr and P.ok('type.kinetic', 'outro'):
            s = P.segs[fr[0]]
            f0 = frame_at(P.parts['outro']['t0'], fps) + 4
            f1 = max(f0, (P.planned_black[0] - 1) if P.planned_black else s['f1'])
            P.layer('type.kinetic', dict(kind='kinetic', f0=f0, f1=f1, mode='word',
                                         words=[dict(w=P.outro_text.upper(), t0=round(f0 / fps, 4), t1=round((f1 + 1) / fps, 4))],
                                         text=P.outro_text.upper(), type_class='grotesk_condensed_caps', font='grotesk_condensed_caps',
                                         caps=True, size=0.09, color='#FFFFFF', pos=[0.47, 0.5],
                                         anim_in=dict(kind='pop', frames=7), anim_out=dict(kind='cut'), safe_zone='tiktok'),
                    'name on the final freeze frame, 8–10 % H')


def _qa_block(g, edl, slots, P, beats, fps):
    rh = g['rhythm']
    cuts = [s['f0'] for s in edl['segments'][1:]]
    bf = {b['f']: b for b in beats}
    half = {frame_at(b['t'] + P.period / 2, fps) for b in beats}
    grid_of = []
    for f in cuts:
        near = [x for x in (f - 1, f, f + 1) if x in bf]
        if near:
            grid_of.append(dict(f=f, grid='downbeat' if bf[near[0]]['pos'] == 0 else 'beat'))
        elif any(x in half for x in (f - 1, f, f + 1)):
            grid_of.append(dict(f=f, grid='half'))
        else:
            grid_of.append(dict(f=f, grid='off'))
    tr0 = edl['segments'][0].get('transition_in') or {} if edl['segments'] else {}
    if tr0.get('kind') == 'fade':                           # opening from black: its first frames are black by design
        P.planned_black += [0, 1]
    white = []
    for si, s in enumerate(edl['segments']):
        tr = s.get('transition_in') or {}
        if tr.get('kind') == 'flash':
            white += [s['f0'] + k for k in range(tr.get('params', {}).get('peak_frames', 1))]
    for op in edl['ops']:
        if op['op'] == 'flash':
            white.append(op['f'] if isinstance(op['f'], int) else int(str(op['f']).split(':')[0]))
    # kind 'music': a beat-cut plan, even for a card whose kind is speech (motivation: the voice-over rides on top;
    # ed_qa would otherwise read the whole edit as a talk part and judge the B-roll as a speaker)
    qa = dict(genre=g['slug'], kind='music', on_beat_share=rh.get('on_beat_share'), on_word_share=None,
              planned_black=sorted(set(int(x) for x in P.planned_black)), planned_white=sorted(set(white)),
              planned_freeze=P.planned_freeze, flash_limit_hz=qa_flash_hz(g['slug']),   # ed_qa: per 1 s window
              flash_min_gap_frames=10 if fps >= 30 else 9, safe_zone='tiktok', lufs=-14, lufs_tol=1, tp_max=-1,
              max_shot_s=rh.get('max_shot_s'), shot_len_s=rh.get('shot_len_s'), cuts=grid_of,
              planned_on_beat_share=round(sum(1 for x in grid_of if x['grid'] != 'off') / max(1, len(grid_of)), 3))
    color = copy.deepcopy(COLOR_TARGETS.get(g['slug']))
    if color:
        if any(fx.get('type') == 'letterbox' for sg in edl['segments'] for fx in sg.get('fx', [])) and 'p1' in color:
            color['p1'][0] = 0                            # letterbox bars are #000: they set p1 of those frames
        qa['color'] = color                               # ed_qa image check ranges ("Color" / "Quality checks")
    if g['slug'] == 'phonk':
        qa['red_flash_limit_hz'] = 1.0
    extra = {}
    if g['slug'] == 'phonk':
        extra.update(velocity_max_share=0.5, luma_mean=[40, 90], accents_per_beat_max=2, rgb_per_10s_max=12, crop_max=2.2)
    elif g['slug'] == 'epic':
        extra.update(slowmo_max_share=0.5, first_drop_cut_frame=frame_at(P.parts['drop']['t0'], fps), flash_per_10s_max=3,
                     letterbox_changes_max=3, p1=[4, 10], p99=[235, 248], no_black_inside_drop=True)
    elif g['slug'] == 'calm':
        extra.update(min_shot_s=2.0, median_shot_s_min=3.0, dissolve_share_min=0.7, dissolve_s=[0.8, 2.5], flashes=0,
                     p1=[14, 26], p99=[228, 242], slowmo_max_share=0.4, zoom_rate_max_pct_per_frame=0.2)
    qa['genre_checks'] = extra
    return qa


def _meta(g, edl, slots, by_seg, P, mus, win, parts, beats, F, opts, seed, cache, track, took):
    fps = P.fps
    seg_slots = []
    for si, sg in enumerate(edl['segments']):
        s = by_seg.get(si, {})
        pk = s.get('pick') or {}
        W = pk.get('W') or {}
        why = []
        if pk:
            why.append(f'{s["role"]}: score {pk["score"]:.2f} of {pk.get("n_cands", 0)} windows')
            why.append(f'motion P{int(100 * W.get("motion_r", 0))}, peak P{int(100 * W.get("peak_r", 0))}, '
                       f'sharpness P{int(100 * W.get("sharp_r", 0))}, luma {W.get("luma", 0):.0f}, {W.get("size")}')
            if pk.get('tags'):
                why.append(', '.join(pk['tags']))
        if s.get('note_speed'):
            why.append(s['note_speed'])
        cut_b = next((b for b in beats if b['f'] == sg['f0']), None)
        seg_slots.append(dict(id=sg['id'], part=s.get('part'), role=s.get('role'), kind=s.get('kind'),
                              t=[round(sg['f0'] / fps, 3), round((sg['f1'] + 1) / fps, 3)], tc=tcode(sg['f0'] / fps), f=[sg['f0'], sg['f1']],
                              beats=round(s.get('b1', 0) - s.get('b0', 0), 2),
                              cut='downbeat' if (cut_b and cut_b['pos'] == 0) else ('beat' if cut_b else 'half/off'),
                              speed=s.get('speed', {}).get('mode'), shot=pk.get('shot'), src=sg['src'], crop_luma=sg.get('_crop_luma'),
                              exposure=sg.get('grade', {}).get('exposure', 0.0),
                              src_t=[pk.get('w0'), pk.get('w1')], why='; '.join(why), alts=pk.get('alts', []),
                              moves=s.get('moves', []),
                              W={k: (round(v, 3) if isinstance(v, float) else v) for k, v in W.items()
                                 if k in ('motion_r', 'peak_r', 'sharp_r', 'luma', 'contrast', 'size', 'face_h', 'jitter', 'pan', 'ews', 'static')}))
    footage_index = None
    if cache:
        footage_index = os.path.join(cache, 'footage_index.json')
        os.makedirs(cache, exist_ok=True)
        _dump_atomic(dict(paths=[c['path'] for c in F.clips], sample_fps=F.clips[0]['fps_sample'] if F.clips else 6.0,
                          shots=[{k: s[k] for k in ('id', 'src', 'ci', 't0', 't1', 'scale', 'motion', 'sharp', 'luma', 'dup', 'peaks')}
                                 for s in F.shots]), footage_index)
    return dict(genre=g['slug'], genre_name=g['genre_name'], scenario='genre', version=1, planner=PLANNER,
                created=time.strftime('%Y-%m-%dT%H:%M:%S'), seed=seed, took_s=round(took, 1),
                track=dict(path=os.path.abspath(track), bpm=mus['bpm'], duration=mus['duration'], window=[win['t_in'], win['t_out']],
                           bars=win['n_bars'], anchor=win.get('anchor'), anchor_kind=win.get('anchor_kind'), reason=win['why'],
                           alternatives=win.get('top', [])),
                parts={k: dict(t=[v['t0'], v['t1']], f=[frame_at(v['t0'], fps), frame_at(v['t1'], fps) - 1], bars=[v['bar0'], v['bar1']])
                       for k, v in parts.items()},
                grid=dict(beats=[b['t'] for b in beats], frames=[b['f'] for b in beats], pos=[b['pos'] for b in beats],
                          kick=[b['kick'] for b in beats], snare=[b['snare'] for b in beats], period=round(P.period, 5)),
                footage=dict(clips=[dict(name=c['name'], path=c['path'], duration=c['info']['duration'], fps=c['info'].get('fps'),
                                         w=c['info'].get('w'), h=c['info'].get('h'), box=c.get('box'), shots=len(c['shots']))
                                    for c in F.clips],
                             shots=len(F.shots), dup_groups=[v for v in F.dup_groups.values() if len(v) > 1], index=footage_index,
                             sample_fps=F.clips[0]['fps_sample'] if F.clips else None),
                slots=seg_slots, moves={k: v for k, v in sorted(P.count.items()) if v > 0}, skipped=P.skipped, notes=list(P.__dict__.get('notes', [])),
                gen_hints=P.__dict__.get('gen_hints', []),
                options=_meta_options(opts), history=[])


OPTION_KEYS = ('title', 'word', 'outro_text', 'reframe', 'sample_fps', 'n_shots', 'order', 'require', 'forbid', 'music_in',
               'drop_at', 'drop_t', 'bpm', 'bars', 'cut_rate', 'sfx_level', 'lang', 'asr_model', 'voice', 'src_in', 'src_out',
               'from', 'to', 'subtitles', 'music_db', 'fillers', 'in_sequence', 'style', 'variant', 'avoid', 'dark', 'interp')


def _meta_options(opts):
    """The options that shaped the plan (re-plans and point edits read them back)."""
    out = {}
    for k in OPTION_KEYS:
        v = opts.get(k)
        if v is None or v == [] or (k == 'cut_rate' and v == 1.0) or (k == 'order' and v == 'auto') or (k == 'sfx_level' and v == 'genre'):
            continue
        if k == 'avoid':                       # earlier versions: their paths (dicts are not repeated)
            v = [x for x in v if isinstance(x, str)]
            if not v:
                continue
        out[k] = v
    return out


# ============================================================================ speech genres (cut by words)
SPEECH_CFG = {
    # cards' cut_grid / Text / SFX: removed pauses, the pause left at a cut, caption kind, bed level and ducking
    'clips': dict(min_pause=0.25, keep_pause=0.12, sub='karaoke', bed_db=-12.0, duck_db=6.0, punch_every=3.0, insert_every=4.0,
                  payoff_pause=0.4, z_alt=1.15),
    'ugc': dict(min_pause=0.20, keep_pause=0.10, sub='karaoke', bed_db=-14.0, duck_db=6.0, punch_every=2.5, insert_every=3.5,
                payoff_pause=0.3, z_alt=1.15),
    'explainer': dict(min_pause=0.30, keep_pause=0.20, sub='subtitle', bed_db=-16.0, duck_db=6.0, punch_every=5.0, insert_every=4.0,
                      payoff_pause=0.4, z_alt=1.12),
}
SPEECH_CAPTION = {('clips', 'karaoke'): 'karaoke_highlight', ('clips', 'subtitle'): 'podcast_bold',
                  ('ugc', 'karaoke'): 'karaoke_box', ('ugc', 'subtitle'): 'boxed',
                  ('explainer', 'subtitle'): 'boxed', ('explainer', 'karaoke'): 'karaoke_box'}   # default ed_text presets
SENT_END = '.!?…'
# words that continue an earlier thought: an excerpt that starts with one makes a weak hook (language data, en / ru)
CONTINUATIONS = {'and', 'but', 'so', 'because', 'which', 'or', 'then', 'also', 'that', 'cause', 'plus', 'anyway',
                 'и', 'а', 'но', 'так', 'потому', 'поэтому', 'который', 'которая', 'или', 'тоже', 'также', 'то'}


class NoSpeech(ValueError):
    """The voice has no recognisable words (music video, silent footage): a speech genre cannot cut by words."""


def _has_voice(footage):
    """True when some footage item can carry a voice: an audio stream (or the role aroll / talk / voice)."""
    items = [p if isinstance(p, dict) else dict(path=p) for p in (footage if isinstance(footage, (list, tuple)) else [footage])]
    for it in items:
        if str(it.get('role') or '').lower() in ('aroll', 'talk', 'voice'):
            return True
        try:
            if V.probe(it['path']).get('has_audio'):
                return True
        except Exception:            # unreadable file: the planner reports it later
            continue
    return False


def _voice_mod():
    try:
        import ed_voice as VO
        return VO
    except Exception:            # optional module: speech planning needs it (or words + no captions)
        return None


def _norm_tok(w):
    return re.sub(r"[^\w']+", '', str(w).lower())


def glue_tokens(words):
    """ASR tokens that are one word on screen and in the cut: number groups ('$10' ',000' -> '$10,000', '4' '.5'),
    bare punctuation, a dangling apostrophe suffix ("'s"). A cut can never fall between them."""
    out = []
    for w in words:
        t = str(w['w']).strip()
        if out:
            prev = out[-1]
            num_cont = re.match(r'^[.,]\d', t) and re.search(r'\d$', str(prev['w']))
            punct = re.fullmatch(r'[^\w$€£₽%]+', t) is not None
            suffix = re.match(r"^'\w{1,2}$", t) is not None
            if num_cont or punct or suffix:
                prev['w'] = str(prev['w']) + t
                prev['t1'] = max(prev['t1'], w['t1'])
                continue
        out.append(dict(w))
    return out


def asr_model_for(lang, model=None):
    """Whisper for its 99 languages, the omnilingual CTC model ('omni') for any other language code."""
    if model:
        return model
    if not lang:
        return 'auto'
    code = str(lang).strip().lower().replace('_', '-')
    return 'auto' if (code in WHISPER_LANGS or code.split('-')[0] in WHISPER_LANGS) else 'omni'


def get_words(path, o, log=print):
    """Transcript of the voice: opts words (list | transcript dict | JSON path) or ed_voice.transcribe (cached by file
    hash); a language Whisper does not know - or a transcript the aligner contradicts in most chunks - goes to the
    omnilingual model. Returns a transcript-like dict {words, speech, lang, model, warnings}."""
    w = o.get('words')
    if w is not None:
        if isinstance(w, str):
            with open(w) as fh:
                w = json.load(fh)
        if isinstance(w, list):
            return dict(words=w, speech=None, lang=o.get('lang'), model='given', warnings=[])
        return w
    VO = _voice_mod()
    if VO is None or not callable(getattr(VO, 'transcribe', None)):
        raise RuntimeError('ed_voice.transcribe is not available: pass words= (word timestamps of the voice)')
    model = asr_model_for(o.get('lang'), o.get('asr_model'))
    log(f'[speech] transcribing {os.path.basename(path)} (model {model}, lang {o.get("lang") or "auto"})')
    res = VO.transcribe(path, lang=o.get('lang'), model=model)
    ch = res.get('chunks') or []
    sus = sum(1 for c in ch if c.get('suspect'))
    if model != 'omni' and ch and sus / len(ch) > 0.5:
        log('[speech] the aligner contradicts Whisper in most chunks: retrying with the omnilingual model')
        res2 = VO.transcribe(path, lang=o.get('lang'), model='omni')
        res2.setdefault('warnings', []).append(f'{sus}/{len(ch)} Whisper chunks were not confirmed: omnilingual recognition used')
        res = res2
    return res


def find_phrase(words, text, after=None, before=None):
    """Fuzzy phrase search in word timestamps: ed_voice.find_phrase when available (number formats, punctuation),
    else a token match here. -> {t0, t1, i0, i1, score} | None"""
    VO = _voice_mod()
    fn = getattr(VO, 'find_phrase', None) if VO else None
    if callable(fn):
        try:
            return fn(words, text, after=after, before=before)
        except Exception:        # an incompatible version: fall back to the local matcher
            pass
    import difflib
    toks = [_norm_tok(x) for x in str(text).split() if _norm_tok(x)]
    if not toks:
        return None
    norm = [_norm_tok(w['w']) for w in words]
    target = ' '.join(toks)
    best = None
    for i in range(len(words)):
        if after is not None and words[i]['t0'] < after - 1e-3:
            continue
        for n in (len(toks) - 1, len(toks), len(toks) + 1):
            j = i + n
            if n < 1 or j > len(words) or (before is not None and words[j - 1]['t1'] > before + 1e-3):
                continue
            sc = difflib.SequenceMatcher(None, ' '.join(x for x in norm[i:j] if x), target).ratio()
            if best is None or sc > best['score'] + 1e-9:
                best = dict(t0=words[i]['t0'], t1=words[j - 1]['t1'], i0=i, i1=j - 1, score=round(sc, 3))
    return best if best and best['score'] >= 0.7 else None


def _sentences(words, pause=0.7):
    """[(i0, i1)] word index ranges split at sentence punctuation or pauses >= pause."""
    out, a = [], 0
    for i, w in enumerate(words):
        end = str(w['w']).rstrip('"»”)').endswith(tuple(SENT_END))
        gap = (words[i + 1]['t0'] - w['t1']) if i + 1 < len(words) else 99
        if end or gap >= pause or i == len(words) - 1:
            out.append((a, i))
            a = i + 1
    return out


def speech_range(words, o, target, tail=0.0):
    """Source range [s0, s1] of the excerpt: src_in / src_out (snapped to words), from / to phrases, else the
    sentence-aligned window nearest the target length with the densest speech, a short first sentence (hook) and
    a strong last one (question, exclamation, number)."""
    if not words:
        raise ValueError('no words in the transcript: nothing to cut by')
    if o.get('src_in') is not None or o.get('src_out') is not None:
        a = parse_time(o.get('src_in')) if o.get('src_in') is not None else words[0]['t0']
        b = parse_time(o.get('src_out')) if o.get('src_out') is not None else words[-1]['t1']
        i0 = next((i for i, w in enumerate(words) if w['t0'] >= a - 0.15), 0)
        i1 = max((i for i, w in enumerate(words) if w['t1'] <= b + 0.15), default=len(words) - 1)
        return i0, max(i0, i1), f'source range {a:.2f}–{b:.2f} s (given)'
    if o.get('from') or o.get('to'):
        i0, i1 = 0, len(words) - 1
        why = []
        if o.get('from'):
            hit = find_phrase(words, o['from'])
            if not hit:
                raise ValueError(f'phrase not found in the transcript: {o["from"]!r}')
            i0 = hit['i0']
            why.append(f'from "{o["from"]}" ({hit["score"]:.2f})')
        if o.get('to'):
            hit = find_phrase(words, o['to'], after=words[i0]['t0'])
            if not hit:
                raise ValueError(f'phrase not found in the transcript after the start: {o["to"]!r}')
            i1 = hit['i1']
            why.append(f'to "{o["to"]}" ({hit["score"]:.2f})')
        return i0, i1, '; '.join(why)
    sents = _sentences(words)
    total = words[-1]['t1'] - words[0]['t0']
    if total <= target * 1.15:
        return 0, len(words) - 1, f'the whole speech ({total:.1f} s)'
    best = None
    for a in range(len(sents)):
        for b in range(a, len(sents)):
            t0, t1 = words[sents[a][0]]['t0'], words[sents[b][1]]['t1']
            span = (t1 - t0) * 0.88                      # ~12 % goes with the jump cuts
            if span > target * 1.4:
                break
            if span < target * 0.6:
                continue
            nw = sents[b][1] - sents[a][0] + 1
            dens = nw / max(t1 - t0, 1e-6)
            first = words[sents[a][1]]['t1'] - words[sents[a][0]]['t0']
            last_w = ' '.join(str(w['w']) for w in words[sents[b][0]:sents[b][1] + 1])
            strong = 1.0 if re.search(r'[!?]|\d', last_w) else 0.0
            # a hook never starts mid-thought ("but ...", "and so ...") and the clip ends on a finished sentence
            lead = _norm_tok(words[sents[a][0]]['w'])
            first_w = str(words[sents[a][0]]['w']).lstrip('"«“(¿¡')
            cont = 1.0 if (lead in CONTINUATIONS or first_w[:1].islower()) else 0.0   # lowercase = mid-sentence (cut-off recording)
            done = 1.0 if str(words[sents[b][1]]['w']).rstrip('"»”)').endswith(tuple(SENT_END)) else 0.0
            sc = 0.5 * dens - 2.0 * abs(span - target) / target + 0.4 * (first <= 3.5) + 0.4 * strong - 0.8 * cont + 0.3 * done
            if best is None or sc > best[0]:
                best = (sc, sents[a][0], sents[b][1])
    if best is None:
        return 0, len(words) - 1, 'no sentence-aligned window of the target length: the whole speech'
    return best[1], best[2], f'auto: sentences {words[best[1]]["t0"]:.2f}–{words[best[2]]["t1"]:.2f} s (densest speech near {target:.0f} s)'


def _split_long(keep, words, max_s, fps):
    """Keep ranges -> shots: a range longer than max_s splits at word boundaries (the largest gap nearest the
    middle) - no time is removed there, the framing changes (medium <-> close)."""
    out = []
    for a, b in keep:
        stack = [(a, b)]
        while stack:
            x, y = stack.pop(0)
            if y - x <= max_s + 1e-6:
                out.append((x, y))
                continue
            inner = [w for w in words if x + 0.6 < w['t1'] < y - 0.6]
            cands = []
            for i, w in enumerate(inner):
                nxt = next((v for v in words if v['t0'] >= w['t1'] - 1e-6), None)
                if nxt is None or nxt['t0'] >= y:
                    continue
                gap = nxt['t0'] - w['t1']
                t = (w['t1'] + nxt['t0']) / 2
                end = str(w['w']).rstrip('"»”)').endswith(tuple(SENT_END + ',;:'))
                cands.append((gap + 0.15 * end - 0.5 * abs(t - (x + y) / 2) / max(y - x, 1e-6), t))
            if not cands:
                out.append((x, y))
                continue
            t = max(cands)[1]
            t = round(t * fps) / fps
            stack[:0] = [(x, t), (t, y)]
    return out


def _source_camera_cuts(path, s0, s1, box=None, log=print):
    """Camera cuts of the source inside [s0, s1] (multi-cam recordings): ed_video.shot_cuts when available, else
    ed_video.detect_cuts on a light decode."""
    try:
        sc = getattr(V, 'shot_cuts', None)
        if callable(sc):
            return [float(c) for c in sc(path, s0, s1, box=box)]
        feats, times = [], []
        for t, fr in V.frames(path, t0=s0, t1=s1, fps=10, width=160):
            feats.append(V.frame_feats(fr))
            times.append(t)
        if len(feats) < 3:
            return []
        res = V.detect_cuts(feats, 10.0)
        cuts = res.get('cuts', []) if isinstance(res, dict) else res
        return [round(times[c], 3) for c in cuts if 0 < int(c) < len(times)]
    except Exception as ex:           # no cut list: the speaker crop still follows the face
        log(f'[speech] camera-cut detection skipped: {ex}')
        return []


def _aroll_analysis(path, info, s0, s1, fps, out_aspect, o, words, log=print):
    """Content box (screen recordings / letterbox), persistent overlays (logo, lower third), camera cuts and the
    speaker crop items of the excerpt: ed_video.content_box / static_overlays / shot_cuts and
    ed_reframe.speaker_crop when available (the face of the active speaker, cut-aware, overlays kept out), else the
    letterbox box and plain crop paths per shot. -> (items | None, cuts, box | None, overlays)"""
    W0, H0 = info.get('w') or 16, info.get('h') or 9
    box = None
    cb = getattr(V, 'content_box', None)
    if callable(cb):
        try:
            box = [int(x) for x in cb(path, s0, s1)]
        except Exception as ex:
            log(f'[speech] content_box failed: {ex}')
    if box is None:
        try:
            box = detect_box(path, info)
        except Exception:
            box = None
    if box == [0, 0, W0, H0]:
        box = None
    overlays = []
    so = getattr(V, 'static_overlays', None)
    if callable(so):
        try:
            overlays = [x for x in so(path, box or [0, 0, W0, H0], s0, s1) if x.get('kind') in ('logo', 'text', 'ui')]
        except Exception as ex:
            log(f'[speech] static_overlays failed: {ex}')
    items, cuts = None, None
    sc = getattr(RF, 'speaker_crop', None)
    if callable(sc) and o.get('reframe', True):
        canvas = (int(round(out_aspect * 1920)), 1920)
        try:
            try:
                items, det = sc(path, s0, s1, box=box, avoid=overlays or None, canvas=canvas, fps=fps, words=words, detail=True)
                cuts = [float(c) for c in (det or {}).get('cuts', [])]
            except TypeError:
                items = sc(path, s0, s1, box=box, avoid=overlays or None, canvas=canvas, fps=fps, words=words)
        except Exception as ex:
            log(f'[speech] speaker_crop failed ({ex}): plain crop paths')
            items = None
    if cuts is None:
        cuts = _source_camera_cuts(path, s0, s1, box, log)
    return items, sorted(c for c in cuts if s0 < c < s1), box, overlays


def _aroll_crops(path, info, pieces, fps, out_aspect, o, items, box, log=print):
    """Crop per A-roll piece: the speaker_crop item that holds the piece (re-based with ed_reframe.sub_crop), else
    ed_reframe.crop_path on the content box. Returns [(crop dict, box | None)], window width (box fraction)."""
    W0, H0 = info.get('w') or 16, info.get('h') or 9
    bx = box or [0, 0, W0, H0]
    win_w = min(1.0, out_aspect / ((bx[2] - bx[0]) / max(1, bx[3] - bx[1])))
    sub = getattr(RF, 'sub_crop', None)
    out = []
    for a, b in pieces:
        n = max(1, int(round((b - a) * fps)))
        crop = None
        ii = 0
        if items:
            ii = max(range(len(items)), key=lambda j: min(b, items[j]['t1']) - max(a, items[j]['t0']))
            it = items[ii]
            if callable(sub):
                c = sub(it, max(a, it['t0']), min(b, it['t1']), fps)
            else:
                c = dict(it.get('crop') or {})
                c.pop('path', None)
            crop = dict(cx=float(c.get('cx', 0.5)), cy=float(c.get('cy', 0.5)), z=float(c.get('z', 1.0)),
                        subject=it.get('subject', 'speaker'))
            if c.get('path'):
                crop['path'] = [[min(int(p[0]), n - 1), float(p[1]), float(p[2]), float(p[3])] for p in c['path'] if int(p[0]) <= n - 1]
                if crop['path'] and crop['path'][-1][0] < n - 1:
                    crop['path'].append([n - 1] + crop['path'][-1][1:])
                if len(crop['path']) < 2:
                    crop.pop('path')
        elif o.get('reframe', True) and win_w < 0.999:
            try:
                rf = RF.crop_path(path, a, max(b - a, 0.2), out_aspect=out_aspect)
                kt = [k[0] for k in rf['keys']]
                ts = np.arange(n) / fps
                cx = np.clip((np.interp(ts, kt, [k[1] for k in rf['keys']]) * W0 - bx[0]) / (bx[2] - bx[0]), 0, 1)
                cy = np.clip((np.interp(ts, kt, [k[2] for k in rf['keys']]) * H0 - bx[1]) / (bx[3] - bx[1]), 0, 1)
                ks = sorted(set(list(range(0, n, 3)) + [n - 1]))
                crop = dict(cx=round(float(cx[0]), 4), cy=round(float(cy[0]), 4), z=1.0, subject=rf['subject'],
                            path=[[int(k), round(float(cx[k]), 4), round(float(cy[k]), 4), 1.0] for k in ks])
            except Exception as ex:
                log(f'[speech] crop path failed ({ex}): centre crop')
        out.append((crop or dict(cx=0.5, cy=0.5, z=1.0, subject='center'), ii))
    return out, win_w


def _split_voice(footage, o):
    """motivation: (picture footage, voice item or None). The voice is opts voice, or the footage item with role
    voice / aroll / talk; without one the edit is a plain music edit."""
    items = [p if isinstance(p, dict) else dict(path=p) for p in (footage if isinstance(footage, (list, tuple)) else [footage])]
    if o.get('voice'):
        return items, dict(path=o['voice'])
    vi = next((it for it in items if str(it.get('role') or '').lower() in ('voice', 'aroll', 'talk')), None)
    if vi is None:
        return items, None
    rest = [it for it in items if it is not vi] or items
    return rest, vi


def _lay_voiceover(edl, P, vi, o, log=print):
    """motivation: the voice-over on the music edit - long pauses tightened, the drop lands in a voice pause and the
    key phrase follows it, the music ducked under the voice (8 dB, attack 80 ms, release 400 ms), karaoke captions
    and the key phrase as kinetic type."""
    VO = _voice_mod()
    try:
        tr = get_words(vi['path'], o, log)
    except Exception as ex:
        P.notes.append(f'voice-over skipped: {ex}')
        return
    words = [w for w in tr['words'] if w.get('t0') is not None and w.get('t1') is not None]
    if not words:
        P.notes.append('voice-over: no words recognised')
        return
    fps, T = P.fps, P.T
    if VO is not None and callable(getattr(VO, 'speech_segments', None)):
        keep = VO.speech_segments(dict(words=words, speech=tr.get('speech'), lang=tr.get('lang')), min_pause=0.6, keep_pause=0.3,
                                  fillers='sure')['keep']
    else:
        keep = [[max(0.0, words[0]['t0'] - 0.05), words[-1]['t1'] + 0.1]]
    # phrases: the kept speech split at sentence ends and breaths (>= 0.25 s), laid with a 0.2 s breath between them
    phrases = []
    for a, b in keep:
        ws = [w for w in words if w['t0'] >= a - 1e-3 and w['t1'] <= b + 1e-3]
        start = None
        for i, w in enumerate(ws):
            start = max(a, w['t0'] - 0.05) if start is None else start
            nxt = ws[i + 1] if i + 1 < len(ws) else None
            if nxt is None or str(w['w']).rstrip('"»”)').endswith(tuple(SENT_END)) or nxt['t0'] - w['t1'] >= 0.25:
                phrases.append([round(start, 3), round(min(b, w['t1'] + 0.08), 3)])
                start = None
    has_drop = P.parts['drop']['beat1'] > P.parts['drop']['beat0'] and P.parts['drop']['t0'] > 1.0
    t_drop = P.parts['drop']['t0'] if has_drop else None
    gap = 0.2
    dur = lambda rs: sum(b - a for a, b in rs) + gap * max(0, len(rs) - 1)   # noqa: E731
    placed = []
    if t_drop is not None:
        # split point k: the phrases before it end just before the drop, the first one after it (the key phrase)
        # must fit between the drop and the end; more voice before the drop is better
        room_b = T - 0.4 - (t_drop + 0.3)
        ks = [k for k in range(len(phrases) + 1) if dur(phrases[:k]) <= t_drop - 0.45]
        fit = [k for k in ks if k < len(phrases) and phrases[k][1] - phrases[k][0] <= room_b]
        k = max(fit) if fit else (max(ks) if ks else 0)
        A, B = phrases[:k], phrases[k:]
        at = max(0.25, t_drop - 0.15 - dur(A))
        for a, b in A:
            placed.append([at, a, b])
            at += b - a + gap
        at = t_drop + 0.3
        rest = B
    else:
        at, rest = 0.25, phrases
    for a, b in rest:
        if at + (b - a) > T - 0.4:
            break
        placed.append([at, a, b])
        at += b - a + gap
    if not placed:
        P.notes.append('voice-over: no phrase fits the edit')
        return
    path = os.path.abspath(vi['path'])
    edl['audio']['voice'] = [dict(path=path, at=round(x, 4), **{'in': round(a, 4)}, dur=round(b - a, 4), gain_db=0.0) for x, a, b in placed]
    edl['audio']['duck'] = [d for d in edl['audio'].get('duck', []) if d.get('under') != 'voice'] + \
        [dict(under='voice', depth_db=8, attack_ms=80, release_ms=400)]
    out = []
    for x, a, b in placed:
        for w in words:
            if w['t0'] >= a - 1e-3 and w['t1'] <= b + 1e-3:
                out.append(dict(w=w['w'], t0=round(x + w['t0'] - a, 3), t1=round(x + w['t1'] - a, 3)))
    P.voice_words = out
    sub_fn = getattr(VO, 'subtitle_chunks', None) if VO else None
    if out and callable(sub_fn) and P.ok('type.karaoke', 'build'):
        for L in sub_fn(out, kind='karaoke', fps=fps):
            if L['f1'] <= P.e['n_frames'] - 1:
                P.layer('type.karaoke', L, 'karaoke captions of the voice-over (words in output time)')
    if t_drop is not None and P.ok('type.kinetic', 'drop'):
        key = [w for w in out if w['t0'] >= t_drop][:3]
        if key:
            f0 = frame_at(key[0]['t0'], fps)
            f1 = min(P.e['n_frames'] - 1, frame_at(key[-1]['t1'] + 0.6, fps))
            P.layer('type.kinetic', dict(kind='kinetic', f0=f0, f1=f1, mode='word', words=key, text=' '.join(w['w'] for w in key).upper(),
                                         type_class='grotesk_condensed_caps', font='grotesk_condensed_caps', caps=True, size=0.085,
                                         color='#FFFFFF', pos=[0.47, 0.42], anim_in=dict(kind='pop', frames=6), anim_out=dict(kind='cut'),
                                         safe_zone='tiktok'), 'the key phrase after the drop, big')
    P.notes.append(f'voice-over: {len(placed)} phrases, {sum(b - a for _, a, b in placed):.1f} s'
                   + (f'; the drop at {t_drop:.2f} s lands in a voice pause' if t_drop is not None else ''))


def plan_speech(track, footage, g, canvas, fps, dur, o, log=print):
    """Speech genres (clips, ugc, explainer): the A-roll is cut by its words. Transcript (ed_voice) -> excerpt
    (given range, phrases, or the best sentence-aligned window) -> jump cuts at pauses / fillers / repeats on word
    boundaries (ed_voice.speech_segments; a cut never falls inside a word) -> shots split at phrase boundaries with
    alternating framing -> B-roll inserts (cut.insert) over the running voice -> punches on phrase starts, a crash on
    the payoff -> karaoke / subtitle layers from the remapped words -> music bed ducked under the voice -> qa for the
    speech checks (words, on_word_share, first word, pauses, reading speed)."""
    t_start = time.time()
    slug = g['slug']
    cfg = SPEECH_CFG.get(slug, SPEECH_CFG['clips'])
    VO = _voice_mod()
    W_, H_ = canvas
    items = [p if isinstance(p, dict) else dict(path=p) for p in (footage if isinstance(footage, (list, tuple)) else [footage])]
    if not items:
        raise ValueError('speech genre: no footage (the talking video is the first item)')
    role = lambda it: str(it.get('role') or '').lower()   # noqa: E731
    a_it = next((it for it in items if role(it) in ('aroll', 'talk', 'voice', 'main')), None)
    if a_it is None:
        a_it = next((it for it in items if V.probe(it['path']).get('has_audio')), items[0])
    b_items = [it for it in items if it is not a_it and role(it) not in ('voice',)]
    info = V.probe(a_it['path'])
    a_name = _clean_name(a_it.get('name') or a_it['path'], set())
    tr = get_words(a_it['path'], o, log)
    words = glue_tokens(sorted([dict(w) for w in tr['words'] if w.get('t0') is not None and w.get('t1') is not None
                                and str(w.get('w', '')).strip()], key=lambda w: w['t0']))
    if len(words) < 3:
        raise NoSpeech(f'no speech recognised in {os.path.basename(a_it["path"])} ({len(words)} words)')
    target = float(dur) if dur else float(g['format']['typical_s'])
    i0, i1, why = speech_range(words, o, target)
    rng_words = words[i0:i1 + 1]
    s0, s1 = rng_words[0]['t0'], rng_words[-1]['t1']
    notes = []
    max_shot = float(g['rhythm'].get('max_shot_s') or 4)
    if VO is not None and callable(getattr(VO, 'speech_segments', None)):
        jc = VO.speech_segments(dict(words=rng_words, speech=tr.get('speech'), lang=tr.get('lang')), min_pause=cfg['min_pause'],
                                keep_pause=cfg['keep_pause'], fillers=o.get('fillers') or 'sure', fps=fps, src=a_name)
        keep = [list(k) for k in jc['keep']]
        jstats = jc.get('stats', {})
    else:
        keep = [[math.floor(max(0.0, s0 - 0.06) * fps) / fps, math.ceil((s1 + 0.1) * fps) / fps]]
        jstats, jc = {}, dict(cuts=[])
        notes.append('ed_voice.speech_segments not available: no jump cuts')
    # the payoff keeps its breath: the pause before the drop part's sentence stays ~0.3-0.6 s (cards)
    out_len = sum(b - a for a, b in keep)
    fr_parts = {x['part']: x for x in g['parts']}
    allowed_pauses = []
    if len(keep) > 1 and cfg.get('payoff_pause'):
        acc, bounds = 0.0, []
        for i in range(len(keep) - 1):
            acc += keep[i][1] - keep[i][0]
            bounds.append((acc, i))
        d_out = fr_parts['drop']['f0'] * out_len
        acc_t, i = min(bounds, key=lambda x: abs(x[0] - d_out))
        a, b = keep[i][1], keep[i + 1][0]
        # only a removed pause (no removed words) gets its breath back, and only from inside that pause
        cut = next((c for c in jc.get('cuts', []) if c.get('kind') == 'pause' and c['t0'] >= a - 0.05 and c['t1'] <= b + 0.05), None)
        w1 = max((w for w in rng_words if w['t1'] <= a + 1e-3), key=lambda w: w['t1'], default=None)
        w2 = min((w for w in rng_words if w['t0'] >= b - 1e-3), key=lambda w: w['t0'], default=None)
        if cut is not None and w1 is not None and w2 is not None:
            orig = w2['t0'] - w1['t1']
            now = (a - w1['t1']) + (w2['t0'] - b)
            extra = min(cfg['payoff_pause'], orig) - now
            if extra > 1.0 / fps:
                na = round(math.floor((a + extra / 2) * fps) / fps, 4)
                nb = round(math.ceil((b - extra / 2) * fps) / fps, 4)
                if na < nb - 1e-6:
                    keep[i][1], keep[i + 1][0] = na, nb
                    allowed_pauses.append(i)
    # source camera cuts and speaker turns: a shot that spans one splits there (the source's own cut / the crop
    # moves to the other speaker in the pause before the turn)
    items, cam_cuts, src_box, overlays = _aroll_analysis(a_it['path'], info, keep[0][0], keep[-1][1], fps, W_ / H_, o, rng_words, log)
    turns = sorted({round(float(it['t0']), 3) for it in (items or [])} | set(cam_cuts))
    splits = [c for c in cam_cuts if any(a + 0.05 < c < b - 0.05 for a, b in keep)]
    edges = [x for k in keep for x in k] + splits
    for c in turns:
        if c in cam_cuts or not any(a + 0.05 < c < b - 0.05 for a, b in keep):
            continue
        # a speaker turn: move it into the nearest word gap (a reframe cut never lands inside a word), never
        # closer than 0.6 s to another cut (no flash shots)
        gaps = [(w1['t1'] + w2['t0']) / 2 for w1, w2 in zip(rng_words, rng_words[1:]) if abs((w1['t1'] + w2['t0']) / 2 - c) < 0.6]
        if gaps:
            x = min(gaps, key=lambda x: abs(x - c))
            if all(abs(x - e) >= 0.6 for e in edges):
                splits.append(x)
                edges.append(x)
    pieces = []
    src_fps = float(info.get('fps') or 30.0)
    for a, b in keep:
        x = a
        for c in sorted(c for c in splits if a + 0.3 < c < b - 0.3):
            if c in cam_cuts:
                # the source's own cut (time of the new shot's first frame): the reframe lands on the first output
                # frame that already shows the new shot, never one frame early (a frame of the old shot in the new crop)
                c = a + math.ceil((c - a) * fps - 0.4 * fps / src_fps) / fps
            else:
                c = a + round((c - a) * fps) / fps
            if c - x >= 0.3:
                pieces.append((x, c))
                x = c
        pieces.append((x, b))
    pieces = _split_long(pieces, rng_words, max_shot, fps)
    # ---- segments (A-roll) in output frames
    vsegs, vrng = [], []
    f = 0
    for k, (a, b) in enumerate(keep):
        n = int(round((b - a) * fps))
        if n > 0:
            vsegs.append(dict(id=f'V{k + 1:02d}', f0=f, f1=f + n - 1, src=a_name, t=round(a, 4), speed=1.0))
            vrng.append((a, b))
            f += n
    n_frames = f
    T = n_frames / fps
    crops, win_w = _aroll_crops(a_it['path'], info, pieces, fps, W_ / H_, o, items, src_box, log)
    segs, meta_slots = [], []
    sources = {a_name: dict(path=os.path.abspath(a_it['path']), **({'box': src_box} if src_box else {}))}
    if overlays:
        notes.append('overlays kept out of the crop: ' + ', '.join(f'{x.get("kind")} {[int(v) for v in x["box"]]}' for x in overlays))

    def out_f(t_src):                       # source time -> output frame through the keep ranges
        for vs, (a, b) in zip(vsegs, vrng):
            if a - 1e-6 <= t_src <= b + 1e-6:
                return vs['f0'] + int(round((t_src - a) * fps))
        return None
    prev_end, z_alt, prev_item = None, False, None
    for (a, b), (crop, item_i) in zip(pieces, crops):
        f0, f1 = out_f(a), out_f(b)
        if f0 is None or f1 is None:
            continue
        f1 = min(f1 - 1, n_frames - 1)
        if f1 < f0:
            continue
        jump = prev_end is not None and a - prev_end > 1e-3      # time removed at this cut
        # the framing alternates (medium <-> close) only between pieces of one camera shot and speaker
        z_alt = (not z_alt) if (prev_end is not None and item_i == prev_item) else False
        prev_item = item_i
        cr = dict(crop)
        zm = cfg['z_alt'] if z_alt else 1.0
        cr['z'] = round(float(cr.get('z', 1.0)) * zm, 4)
        if cr.get('path'):
            cr['path'] = [[p[0], p[1], p[2], round(p[3] * zm, 4)] for p in cr['path']]
        segs.append(dict(id=f'S{len(segs) + 1:02d}', f0=f0, f1=f1, src=a_name, t=round(a, 4), speed=1.0, crop=cr, border='reflect',
                         grade=dict(preset='natural', contrast=1.05, sat=1.03), fx=[], _item=item_i,
                         note=f'A-roll · {"jump cut" if jump else "framing change"}' if prev_end is not None else 'A-roll'))
        meta_slots.append(dict(kind='aroll', src_t=[round(a, 3), round(b, 3)], jump=jump,
                               text=' '.join(w['w'] for w in rng_words if a - 1e-3 <= w['t0'] < b)))
        prev_end = b
    for i in range(len(segs) - 1):                 # contiguous frames
        segs[i]['f1'] = segs[i + 1]['f0'] - 1
    if segs:
        segs[-1]['f1'] = n_frames - 1
    for s in segs:
        _trim_path(s['crop'], s['f1'] - s['f0'] + 1)
        if overlays:
            moved = _clear_overlays(s['crop'], src_box or [0, 0, info.get('w') or 16, info.get('h') or 9], overlays, W_ / H_)
            if moved:
                notes.append(f'frames {s["f0"]}-{s["f1"]}: crop moved off a static overlay ({moved})')
        it_ = s.pop('_item', None)
        it_ = items[it_] if (items and isinstance(it_, int) and 0 <= it_ < len(items)) else None
        if it_ and it_.get('face'):                # the caption band stays below the chin (headroom framing)
            dy = _caption_headroom(s['crop'], src_box or [0, 0, info.get('w') or 16, info.get('h') or 9], it_['face'],
                                   overlays, W_ / H_)
            if dy:
                notes.append(f'frames {s["f0"]}-{s["f1"]}: crop lowered {dy:.0f} px so the captions sit below the face')
    # ---- words in output time, parts snapped to sentence boundaries
    words_out, issues = (VO.remap_words(rng_words, vsegs, fps, src=a_name) if VO is not None else ([], []))
    bounds = [w['t0'] for w in words_out]

    def snap_t(x):
        return min(bounds, key=lambda b: abs(b - x)) if bounds else x
    parts = {}
    for p in PARTS:
        x = fr_parts[p]
        parts[p] = dict(t0=round(0.0 if p == 'hook' else snap_t(x['f0'] * T), 3), t1=round(T if p == 'outro' else snap_t(x['f1'] * T), 3))
    for p in PARTS:
        parts[p]['f'] = [frame_at(parts[p]['t0'], fps), max(frame_at(parts[p]['t0'], fps), frame_at(parts[p]['t1'], fps) - 1)]
    part_of = lambda f: next((p for p in PARTS if parts[p]['f'][0] <= f <= parts[p]['f'][1]), 'outro')   # noqa: E731
    edl = dict(canvas=dict(w=W_, h=H_, fps=fps), n_frames=n_frames, frame_interp='flow', sources=sources,
               audio=dict(copy=False, voice=[dict(path=os.path.abspath(a_it['path']), at=round(vs['f0'] / fps, 4), **{'in': vs['t']},
                                                  dur=round((vs['f1'] - vs['f0'] + 1) / fps, 4), gain_db=0.0) for vs in vsegs],
                          sfx=[], duck=[], loudness=dict(lufs=-14, tp=-1)),
               segments=segs, ops=[], texts=[], layers=[], qa={}, meta={})
    if track:
        mus = analyze_music(track, o.get('cache_dir'), o.get('bpm'))
        m_in = o['music_in'] if o.get('music_in') is not None else 0.0
        bed = float(o.get('music_db') if o.get('music_db') is not None else cfg['bed_db'])
        edl['audio']['music'] = dict(path=os.path.abspath(track), **{'in': round(m_in, 3)}, gain_db=round(bed + cfg['duck_db'], 1), fade_in=0.3,
                                     fade_out=1.0)
        edl['audio']['duck'] = [dict(under='voice', depth_db=cfg['duck_db'], attack_ms=80, release_ms=400)]
        edl['audio']['grid'] = dict(bpm=mus['bpm'], beats=[round(b - m_in, 4) for b in mus['beats'] if m_in <= b < m_in + T],
                                    downbeats=[round(b - m_in, 4) for b in mus.get('downbeats', []) if m_in <= b < m_in + T])
    # ---- moves (Placer on a slot table built from the pieces)
    slots = []
    for si, s in enumerate(segs):
        part = part_of(s['f0'])
        slots.append(dict(i=si, part=part, role='aroll', kind='shot', speed=dict(mode='normal'), b0=0.0, b1=0.0, t0=s['f0'] / fps,
                          t1=(s['f1'] + 1) / fps, f0=s['f0'], f1=s['f1'], moves=[]))
    pbeats = [dict(j=i, t=w['t0'], f=frame_at(w['t0'], fps), bar=i // 4, pos=0, down=True, kick=0, snare=0, onset=0, fill=0,
                   part=part_of(frame_at(w['t0'], fps))) for i, w in enumerate(words_out)]
    pparts = {p: dict(parts[p], beat0=0, beat1=1 if parts[p]['t1'] > parts[p]['t0'] else 0) for p in PARTS}
    P = Placer(g, edl, slots, pbeats, pparts, fps, T, 0.0)
    P.slots_by_seg = {i: s for i, s in enumerate(slots)}
    P.period = 0.5
    P.planned_black, P.planned_freeze, P.notes, P.opts = [], [], notes, o
    for si, s in enumerate(segs):
        if si and P.ok('cut.jump', slots[si]['part']) and meta_slots[si]['jump']:
            P._log(si, 'cut.jump', 0, 'jump cut at a removed pause / filler, framing alternates medium <-> close')
    _speech_inserts(P, b_items, words_out, cfg, o, log, meta_slots)
    _speech_moves(P, words_out, cfg)
    # ---- captions
    sub = (o.get('subtitles') or cfg['sub']).lower()
    if sub in ('karaoke', 'subtitle') and words_out and VO is not None:
        mid = 'type.karaoke' if sub == 'karaoke' else 'type.subtitles'
        if not P.ok(mid, 'build') and sub == 'karaoke':
            sub, mid = 'subtitle', 'type.subtitles'
        # chunks stay on screen >= 0.7 s and <= 25 cps (karaoke) / 20 cps (subtitles): the QA reading checks; fast
        # speakers (> 3 words/s) get 4-word karaoke chunks so a chunk is not gone before it is read
        wps = len(words_out) / max(1e-6, words_out[-1]['t1'] - words_out[0]['t0'])
        extra = dict(max_words=4) if (sub == 'karaoke' and wps > 3.0) else {}
        cap = _caption_style(o.get('_style')) or SPEECH_CAPTION.get((slug, sub))
        try:
            sig = inspect.signature(VO.subtitle_chunks).parameters
        except (TypeError, ValueError):
            sig = {}
        if 'style' in sig and cap:
            extra['style'] = cap                           # the preset's line lengths / kinds drive the chunking
        if 'breaks' in sig:                                # no chunk across a jump cut (the audio jumps there)
            extra['breaks'] = [round(segs[i]['f0'] / fps, 4) for i in range(1, len(segs))
                               if i < len(meta_slots) and meta_slots[i].get('jump')]
        if 'canvas' in sig:
            extra['canvas'] = (W_, H_)
        faces = _speech_face_track(edl, segs, items, a_name) if items else None
        for L in VO.subtitle_chunks(words_out, kind=sub, fps=fps, lang=tr.get('lang'), min_dur=0.7,
                                    max_cps=25.0 if sub == 'karaoke' else 20.0, **extra):
            L['f1'] = min(L['f1'], n_frames - 1)
            if cap and not L.get('style'):
                L['style'] = cap                           # the ed_text caption preset
            if faces and 'faces' not in L:
                L['faces'] = faces                         # ed_text moves a chunk off the speaker's face (avoid 'face')
            if L['f0'] <= L['f1']:
                P.layer(mid, L, f'{sub} captions from the word timestamps (cards: mandatory, people watch without sound)')
    _require_moves(P)
    _cap_fx(P)
    _sfx_pass(P, o['sfx_level'])
    _finish_sfx(edl)
    # ---- qa (speech checks) + meta
    cuts = [s['f0'] for s in segs[1:]]
    rh = g['rhythm']
    sq = None
    max_pause = round(max(0.35, cfg['keep_pause'] + 0.2), 3)
    max_cps = 25.0 if sub == 'karaoke' else 20.0             # karaoke follows the voice word by word
    pause_ok = [(vsegs[i + 1]['f0'] / fps - 0.8, vsegs[i + 1]['f0'] / fps + 0.8) for i in allowed_pauses if i + 1 < len(vsegs)]
    if VO is not None and callable(getattr(VO, 'speech_qa', None)):
        try:
            sq = VO.speech_qa(words_out, edl['layers'], cuts, fps, max_pause=max_pause, allowed_pauses=pause_ok, max_cps=max_cps,
                              remap_issues=issues)
        except Exception as ex:
            notes.append(f'speech_qa failed: {ex}')
    edl['qa'] = dict(genre=slug, kind='speech', on_beat_share=None, on_word_share=rh.get('on_word_share', 0.95), words=words_out,
                     planned_black=sorted(set(P.planned_black)), planned_white=[], planned_freeze=P.planned_freeze,
                     flash_limit_hz=qa_flash_hz(slug), flash_min_gap_frames=10 if fps >= 30 else 9,
                     safe_zone='tiktok', lufs=-14, lufs_tol=1, tp_max=-1, max_shot_s=rh.get('max_shot_s'), first_word_max=0.3,
                     max_pause=max_pause, allowed_pauses=[[round(a, 3), round(b, 3)] for a, b in pause_ok], max_cps=max_cps,
                     source_cuts=[s['f0'] for s in segs[1:] if s['src'] == a_name and any(abs(s['t'] - c) <= 1.5 / fps for c in cam_cuts)],
                     cuts=[dict(f=f, grid='word') for f in cuts],
                     speech=({k: sq[k] for k in ('first_word', 'first_word_ok', 'ok')} | dict(pauses=len(sq['pauses']), word_cuts=len(sq['word_cuts']),
                                                                                           reading_speed=len(sq['reading_speed'])))
                     if sq else None)
    seg_slots = []
    for si, s in enumerate(segs):
        ms = meta_slots[si] if si < len(meta_slots) else {}
        seg_slots.append(dict(id=s['id'], part=slots[si]['part'], role=ms.get('kind', 'aroll'), kind=ms.get('kind', 'aroll'),
                              t=[round(s['f0'] / fps, 3), round((s['f1'] + 1) / fps, 3)], tc=tcode(s['f0'] / fps), f=[s['f0'], s['f1']],
                              cut='word' if si else 'start', speed='normal', shot=ms.get('shot'), src=s['src'],
                              src_t=ms.get('src_t'), why=ms.get('why') or (f'"{ms.get("text", "")[:60]}"' if ms.get('text') else ''),
                              alts=[], moves=slots[si].get('moves', []), W={}))
    edl['meta'] = dict(genre=slug, genre_name=g['genre_name'], scenario='genre', kind='speech', version=1, planner=PLANNER,
                       created=time.strftime('%Y-%m-%dT%H:%M:%S'), took_s=round(time.time() - t_start, 1),
                       source=dict(path=os.path.abspath(a_it['path']), name=a_name, range=[round(s0, 3), round(s1, 3)], why=why,
                                   keep=keep, removed=jstats, camera_cuts=cam_cuts, words=len(rng_words),
                                   transcript=dict(model=tr.get('model'), lang=tr.get('lang'), warnings=tr.get('warnings', []))),
                       track=dict(path=os.path.abspath(track)) if track else None,
                       parts={p: dict(t=[parts[p]['t0'], parts[p]['t1']], f=parts[p]['f']) for p in PARTS},
                       grid=dict(beats=[w['t0'] for w in words_out], frames=[frame_at(w['t0'], fps) for w in words_out], period=0.5),
                       slots=seg_slots, moves={k: v for k, v in sorted(P.count.items()) if v > 0}, skipped=P.skipped, notes=notes, gaps=[],
                       options=_meta_options(o), history=[])
    sty = o.get('_style')
    edl['meta']['style'] = sty['name'] if sty else None
    edl['meta']['variant'] = sty['variant'] if sty else 0
    if sty:
        lk = style_look(sty)                               # natural on version 0, a subtle look (<= 0.4) later
        for s_ in segs:
            if s_['src'] == a_name or (lk is not None and s_['src'] in edl['sources']):
                # the A-roll takes the style's grade (+ the version nuance); with a look every shot takes it
                s_['grade'] = dict(style_grade(slug, sty), **{k: v for k, v in s_['grade'].items() if k == 'exposure'})
            if lk is not None and s_['src'] in edl['sources']:
                s_.setdefault('fx', []).extend(dict(f_, move='look') for f_ in lk['fx'])
        edl['audio']['sfx_style'] = sty['preset'].get('sfx_style')
        edl['meta']['choices'] = _style_choices(edl, sty, [], None)
    log(f'[plan] {slug} (speech): {len(segs)} shots, {n_frames} frames ({T:.1f} s from {s1 - s0:.1f} s of source), '
        f'{len(edl["layers"])} caption layers ({time.time() - t_start:.0f}s)')
    return edl


def _caption_headroom(crop, box, face, overlays, out_aspect, chin_max=0.58, margin=0.012):
    """Vertical talk framing that leaves the caption band free: when the speaker's chin (face box, source px) sits
    below chin_max of the output height, the window moves down (the face moves up) as far as the picture box and the
    static overlays below allow (they stay out of the window) and the face stays inside. Edits crop cy (and its path
    keys) in place; returns the largest shift in box px (0 = unchanged)."""
    bw, bh = float(box[2] - box[0]), float(box[3] - box[1])
    ba = bw / max(1.0, bh)
    fy0, fy1 = float(face[1]) - box[1], float(face[3]) - box[1]
    fx0, fx1 = float(face[0]) - box[0], float(face[2]) - box[0]
    keys = crop.get('path') or [[0, crop.get('cx', 0.5), crop.get('cy', 0.5), crop.get('z', 1.0)]]
    worst = 0.0
    for key in keys:
        cx, cy, z = float(key[1]), float(key[2]), float(key[3])
        wh = bh / z
        ww = wh * out_aspect if out_aspect <= ba else bw / z
        cyc = min(max(cy * bh, wh / 2), bh - wh / 2)           # the renderer keeps the window inside the box
        cxc = min(max(cx * bw, ww / 2), bw - ww / 2)
        w0 = cyc - wh / 2
        need = (fy1 - w0) / wh - chin_max
        if need <= 0:
            continue
        room = bh - (w0 + wh)                                   # the box bottom
        room = min(room, fy0 - w0 - 0.03 * wh)                  # the forehead stays inside
        for o in overlays or []:
            ob = o.get('box') if isinstance(o, dict) else o
            ox0, oy0, ox1 = ob[0] - box[0], ob[1] - box[1], ob[2] - box[0]
            if ox1 > cxc - ww / 2 and ox0 < cxc + ww / 2 and oy0 >= w0 + wh - 1:   # an overlay below the window
                room = min(room, oy0 - margin * bh - (w0 + wh))
        dy = max(0.0, min(need * wh, room))
        if dy > 0.5:
            key[2] = round((cyc + dy) / bh, 4)
            worst = max(worst, dy)
    if crop.get('path'):
        crop['cy'] = crop['path'][0][2]
    else:
        crop['cy'] = keys[0][2]
    return worst


def _speech_face_track(edl, segs, items, a_name, pad=0.0, chin=-0.15):
    """Where the speaker's face sits in the output, for the captions to keep off it (ed_text layer `faces`):
    [[f, x0, y0, x1, y1], ...] (fractions of the output frame, step keys at each A-roll shot and its crop-path keys;
    [f, 0, 0, 0, 0] on B-roll). The speaker_crop face box (source px) goes through each shot's crop window, its
    bottom trimmed to about the mouth line (chin=-0.15): the framing (_caption_headroom) keeps the chin above the
    caption band, the track only moves a chunk that would cover the mouth - a chunk pushed far down leaves the safe
    zone when it pops in."""
    track = []
    for sg in segs:
        it = None
        if sg['src'] == a_name:
            t = float(sg.get('t', 0.0))
            it = next((x for x in items or [] if x.get('face') and x['t0'] - 1e-3 <= t < x['t1']), None)
        if it is None:
            track.append([int(sg['f0']), 0.0, 0.0, 0.0, 0.0])
            continue
        fx0, fy0, fx1, fy1 = [float(v) for v in it['face']]
        n = int(sg['f1']) - int(sg['f0']) + 1
        ks = sorted({0} | {int(p_[0]) for p_ in (sg.get('crop') or {}).get('path') or [] if 0 <= int(p_[0]) < n})
        for k in ks:
            try:
                r = _crop_window(edl, sg, k)
            except Exception:
                continue
            rw, rh = max(1.0, r[2] - r[0]), max(1.0, r[3] - r[1])
            fw, fh = fx1 - fx0, fy1 - fy0
            box = [(fx0 - pad * fw - r[0]) / rw, (fy0 - pad * fh - r[1]) / rh, (fx1 + pad * fw - r[0]) / rw,
                   (fy1 + (pad + chin) * fh - r[1]) / rh]
            box = [round(min(1.0, max(0.0, v)), 4) for v in box]
            track.append([int(sg['f0']) + k] + box)
    return track


def _clear_overlays(crop, box, overlays, out_aspect, margin=0.012, z_max=1.9):
    """Safety net after the speaker crop: a window that still covers a static overlay (a lower-third band, a corner
    logo) is moved off it - a band by zooming in just enough and shifting the window away from it, a small box by a
    sideways shift of at most 15 % of the box. Edits crop (cx / cy / z and path keys) in place; returns what moved."""
    bw, bh = float(box[2] - box[0]), float(box[3] - box[1])
    ba = bw / max(1.0, bh)
    mg = margin * bh
    obs = []
    for o in overlays or []:
        ob = o.get('box') if isinstance(o, dict) else o
        x0, y0, x1, y1 = max(ob[0], box[0]) - box[0], max(ob[1], box[1]) - box[1], min(ob[2], box[2]) - box[0], min(ob[3], box[3]) - box[1]
        if x1 > x0 and y1 > y0:
            obs.append((x0, y0, x1, y1))
    keys = crop.get('path') or [[0, crop.get('cx', 0.5), crop.get('cy', 0.5), crop.get('z', 1.0)]]
    out = set()
    for key in keys:
        cx, cy, z = float(key[1]) * bw, float(key[2]) * bh, float(key[3])
        for (x0, y0, x1, y1) in obs:
            wh = bh / z
            ww = wh * out_aspect if out_aspect <= ba else bw / z
            w0, w1, h0, h1 = cx - ww / 2, cx + ww / 2, cy - wh / 2, cy + wh / 2
            ix, iy = max(0.0, min(w1, x1) - max(w0, x0)), max(0.0, min(h1, y1) - max(h0, y0))
            if ix * iy < 0.01 * ww * wh:
                continue
            if (x1 - x0) >= 0.4 * bw and (y0 >= 0.5 * bh or y1 <= 0.5 * bh):        # a band across the picture
                room = (y0 - mg) if y0 >= 0.5 * bh else (bh - y1 - mg)
                if room <= 0:
                    continue
                z = min(z_max, max(z, bh / room))
                wh = bh / z
                cy = min(cy, y0 - mg - wh / 2) if y0 >= 0.5 * bh else max(cy, y1 + mg + wh / 2)
                cy = min(max(cy, wh / 2), bh - wh / 2)
                out.add('band')
            else:                                                                 # a box: step aside
                left = (x0 - mg) - w1                     # move left so the window ends before the box
                right = (x1 + mg) - w0
                step = left if abs(left) <= abs(right) else right
                if abs(step) <= 0.15 * bw:
                    cx = min(max(cx + step, ww / 2), bw - ww / 2)
                    out.add('box')
        key[1], key[2], key[3] = round(cx / bw, 4), round(cy / bh, 4), round(z, 4)
    if crop.get('path'):
        crop.update(cx=crop['path'][0][1], cy=crop['path'][0][2], z=crop['path'][0][3])
    else:
        crop.update(cx=keys[0][1], cy=keys[0][2], z=keys[0][3])
    return ', '.join(sorted(out))


def _trim_path(crop, n):
    """Cut a crop path to a segment that got shorter (n frames): keys past the end go, the last key is interpolated."""
    path = crop.get('path')
    if not path:
        return
    ks = [p[0] for p in path]
    end = [n - 1] + [round(float(np.interp(n - 1, ks, [p[j] for p in path])), 4) for j in (1, 2, 3)]
    keep = [p for p in path if p[0] < n - 1] + [end]
    if len(keep) < 2:
        crop.pop('path', None)
        crop.update(cx=end[1], cy=end[2], z=end[3])
    else:
        crop['path'] = keep


def _speech_inserts(P, b_items, words_out, cfg, o, log, meta_slots):
    """cut.insert: B-roll over the running voice, from a word boundary inside an A-roll shot to its end, at most one
    per insert_every seconds, never in the first 1.5 s, on the payoff or in the last 1.5 s."""
    if not b_items or not words_out:
        return
    parts_ok = [p for p in PARTS if P.ok('cut.insert', p)]
    if not parts_ok:
        return
    try:
        F = Footage(b_items, o.get('cache_dir'), o.get('sample_fps', 6.0), log)
    except Exception as ex:
        P.notes.append(f'B-roll skipped: {ex}')
        return
    fps, segs = P.fps, P.segs
    d0 = P.parts['drop']['t0']
    last_t = -1e9
    used = []
    new = []
    for si, s in enumerate(list(segs)):
        sl = P.slots_by_seg[si]
        t0, t1 = s['f0'] / fps, (s['f1'] + 1) / fps
        if sl['part'] not in parts_ok or t0 < 1.5 or t1 > P.T - 1.5 or (d0 - 0.3 <= t0 <= d0 + 1.5) or t0 - last_t < cfg['insert_every']:
            continue
        cand = [w['t0'] for w in words_out if t0 + 0.6 <= w['t0'] <= t1 - 1.0]
        if not cand:
            continue
        ta = min(cand, key=lambda x: abs((t1 - x) - 1.5))
        need = t1 - ta
        best = None
        for sh, w0, _ in F.candidates(need):
            if any(u[0] == sh['ci'] and w0 < u[2] + 0.3 and w0 + need > u[1] - 0.3 for u in used):
                continue
            W = F.win(sh, w0, w0 + need)
            sc = 1.0 * W['readable'] + 0.4 * W['sharp_r'] + 0.3 * _band(W['motion_r'], 0.2, 0.7, 0.3) - 0.3 * (W['jitter'] > 2)
            if best is None or sc > best[0]:
                best = (sc, sh, w0, W)
        if best is None:
            continue
        sc, sh, w0, W = best
        fa = frame_at(ta, fps)
        if fa <= s['f0'] + 2 or fa >= s['f1'] - 2:
            continue
        new.append((si, fa, sh, w0, W, need))
        used.append((sh['ci'], w0, w0 + need))
        last_t = ta
    for si, fa, sh, w0, W, need in reversed(new):
        s = segs[si]
        clip = F.clips[sh['ci']]
        name = 'B_' + clip['name']
        bx = clip.get('box')
        full = [0, 0, clip['info'].get('w'), clip['info'].get('h')]
        P.e['sources'].setdefault(name, dict(path=clip['path'], **({'box': bx} if bx and bx != full else {})))
        n = s['f1'] - fa + 1
        times = w0 + np.arange(n) / fps
        pk = dict(W=W, ci=sh['ci'])
        cr = _crop_for(clip, pk, dict(f0=fa, f1=s['f1']), times, fps, P.e['canvas']['w'] / P.e['canvas']['h'], o.get('reframe', True))
        center = cr.pop('_center', [0.5, 0.45])
        cr.pop('_win_w', None)
        cr['center'] = center
        ins = dict(id=s['id'] + 'b', f0=fa, f1=s['f1'], src=name, t=round(w0, 4), speed=1.0, crop=cr, border='reflect',
                   grade=dict(preset='natural', contrast=1.05, sat=1.03), fx=[], note='B-roll insert over the voice')
        s['f1'] = fa - 1
        _trim_path(s['crop'], s['f1'] - s['f0'] + 1)
        segs.insert(si + 1, ins)
        sl = dict(P.slots_by_seg[si], moves=[], role='insert', kind='shot', f0=fa, f1=ins['f1'])
        meta_slots.insert(si + 1, dict(kind='insert', src_t=[round(w0, 3), round(w0 + need, 3)], shot=sh['id'],
                                       why=f'B-roll {sh["id"]} (readable {W["readable"]:.2f}, {W["size"]})', jump=False))
        P.slots.insert(si + 1, sl)
    for i, s in enumerate(segs):
        s['id'] = f'S{i + 1:02d}'
    P.slots_by_seg = {i: s for i, s in enumerate(P.slots)}
    for i, s in enumerate(P.slots):
        s['i'] = i
    for si, s in enumerate(segs):
        if P.slots_by_seg[si].get('role') == 'insert':
            P._log(si, 'cut.insert', 0, 'B-roll insert from a word boundary; the voice runs on')
            if P.ok('sfx.whoosh', P.slots_by_seg[si]['part']):
                P.sfx('sfx.whoosh', 'whoosh', s['f0'] / fps, 'short swish on the cutaway (under the voice)', variant='swish', align='peak',
                      level='light')


def _speech_moves(P, words_out, cfg):
    """Moves on phrase boundaries: a punch-in on the first stressed word of a phrase (the phrase start itself when it
    is not on the cut frame, else its first content word inside the shot) at most every punch_every seconds; a crash
    zoom landing on the payoff's first word (clips)."""
    fps, segs = P.fps, P.segs
    starts = []
    for i, w in enumerate(words_out):
        prev = words_out[i - 1] if i else None
        if prev is None or w['t0'] - prev['t1'] >= 0.2 or str(prev['w']).rstrip('"»”)').endswith(tuple(SENT_END + ',;:')):
            f = frame_at(w['t0'], fps)
            si = P.seg_at(f)
            if si is not None and f - segs[si]['f0'] < 4:
                # the phrase starts on a cut: the accent goes to its first content word inside the same shot
                nxt = next((x for x in words_out[i + 1:i + 5] if len(_norm_tok(x['w'])) >= 4 or re.search(r'\d', str(x['w']))), None)
                if nxt is not None and P.seg_at(frame_at(nxt['t0'], fps)) == si and frame_at(nxt['t0'], fps) - segs[si]['f0'] >= 4:
                    w = nxt
            starts.append(w)
    last = -1e9
    d0 = P.parts['drop']['t0']
    crash_done = False
    part_at = lambda f: next((p for p in PARTS if P.parts[p]['f'][0] <= f <= P.parts[p]['f'][1]), 'outro')   # noqa: E731
    for w in starts:
        f = frame_at(w['t0'], fps)
        si = P.seg_at(f)
        if si is None or P.slots_by_seg[si].get('role') == 'insert':
            continue
        s = segs[si]
        k = f - s['f0']
        part = part_at(f)
        if part == 'drop' and not crash_done and abs(w['t0'] - d0) < 1.0 and k >= int(0.4 * fps) and P.ok('zoom.crash', 'drop'):
            P.fx(si, 'zoom.crash', dict(type='zoom.crash', frames=[k - int(round(0.4 * fps))], scale=1.6, dur=0.4, ease='inOutCubic',
                                        blur_shutter=0.3, center=_center(s)), k, 'crash zoom x1.6 landing on the payoff', 'crash')
            if P.ok('sfx.impact', 'drop'):
                P.sfx('sfx.impact', 'impact', w['t0'], 'soft hit on the payoff landing (under the voice)', variant='soft', align='attack', level='light')
            crash_done = True
            last = w['t0']
            continue
        if k < 4 or w['t0'] - last < cfg['punch_every'] or not P.ok('zoom.punch', part):
            continue
        P.fx(si, 'zoom.punch', dict(type='zoom.punch', frames=[k], scale=1.1, mode='bounce', attack=0, release=0.33, blur_shutter=0.3,
                                    center=_center(s)), k, f'punch x1.1 on the phrase start "{w["w"]}"', 'punch')
        last = w['t0']


# ============================================================================ validation (TIMELINE.md contract)
IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff')


def validate_edl(edl):
    """Returns (errors, warnings) — structural contract of TIMELINE.md (§1–6) plus renderer sanity."""
    E, Wn = [], []
    for k in ('canvas', 'n_frames', 'sources', 'audio', 'segments', 'qa', 'meta'):
        if k not in edl:
            E.append(f'missing top-level key {k}')
    if E:
        return E, Wn
    cv = edl['canvas']
    if not all(isinstance(cv.get(k), int) and not isinstance(cv.get(k), bool) and cv[k] > 0 for k in ('w', 'h')):
        E.append('canvas w/h must be positive ints')
    fr_ = cv.get('fps')
    if not (isinstance(fr_, (int, float)) and not isinstance(fr_, bool) and 1 <= fr_ <= 240):
        E.append('canvas fps must be a positive number (30, 29.97, 23.976 ...)')
    n = edl['n_frames']
    fps = cv.get('fps', 30)
    if edl.get('frame_interp', 'flow') not in ('nearest', 'blend', 'flow'):
        E.append('frame_interp must be nearest|blend|flow')
    durs = {}
    for name, src in edl['sources'].items():
        if not os.path.exists(src.get('path', '')):
            E.append(f'source {name}: file not found {src.get("path")}')
        elif str(src['path']).lower().endswith(IMAGE_EXT):
            continue                                    # a still (storyboard slate, photo): any source time shows it
        else:
            try:
                durs[name] = V.probe(src['path'])['duration']
            except Exception as ex:
                E.append(f'source {name}: probe failed {ex}')
    segs = edl['segments']
    if not segs:
        E.append('no segments')
    exp = 0
    ids = set()
    for s in segs:
        sid = s.get('id')
        if not sid or sid in ids:
            E.append(f'segment id missing or duplicated: {sid}')
        ids.add(sid)
        if s['f0'] != exp:
            E.append(f'{sid}: f0 {s["f0"]} != expected {exp} (gap/overlap)')
        if s['f1'] < s['f0']:
            E.append(f'{sid}: f1 < f0')
        exp = s['f1'] + 1
        if s.get('src') not in edl['sources']:
            E.append(f'{sid}: unknown src {s.get("src")}')
        m = s['f1'] - s['f0'] + 1
        if 'times' in s:
            if len(s['times']) != m:
                E.append(f'{sid}: times has {len(s["times"])} values for {m} frames')
            t_hi = max(s['times'])
        else:
            sp = s.get('speed', 1.0)
            t_hi = s.get('t', 0) + (m - 1) / fps * sp
        if 'speed_curve' in s:
            ks = [p[0] for p in s['speed_curve']]
            if ks != sorted(ks) or ks[0] != 0 or ks[-1] > m - 1:
                E.append(f'{sid}: speed_curve keys must be sorted segment-relative frames 0..{m - 1}')
        if s.get('t', 0) < 0:
            E.append(f'{sid}: negative source time')
        if s.get('src') in durs and t_hi > durs[s['src']] + 0.05:
            E.append(f'{sid}: source time {t_hi:.2f} beyond {s["src"]} duration {durs[s["src"]]:.2f}')
        cr = s.get('crop') or {}
        for k in ('cx', 'cy'):
            if k in cr and not (0 <= cr[k] <= 1):
                E.append(f'{sid}: crop.{k} out of 0..1')
        if cr.get('path'):
            for p in cr['path']:
                if len(p) != 4 or not (0 <= p[0] <= m - 1) or not (0 <= p[1] <= 1 and 0 <= p[2] <= 1) or p[3] <= 0:
                    E.append(f'{sid}: bad crop.path key {p}')
                    break
            if [p[0] for p in cr['path']] != sorted(p[0] for p in cr['path']):
                E.append(f'{sid}: crop.path keys not sorted')
            zmax = max(p[3] for p in cr['path'])
            if zmax > 2.2:
                Wn.append(f'{sid}: crop z {zmax:.2f} > 2.2 (soft)')
        if s.get('border', 'reflect') not in ('reflect', 'black'):
            E.append(f'{sid}: border must be reflect|black')
        for fx in s.get('fx', []):
            if 'type' not in fx:
                E.append(f'{sid}: fx without type')
            for k in fx.get('frames', []) if isinstance(fx.get('frames'), list) else []:
                if not (0 <= int(k) <= m - 1):
                    E.append(f'{sid}: fx {fx.get("type")} frame {k} outside segment 0..{m - 1}')
                    break
            if 't' in fx and (not isinstance(fx['t'], list) or len(fx['t']) != 2 or fx['t'][0] > fx['t'][1]):
                E.append(f'{sid}: fx {fx.get("type")} t must be [t0, t1]')
        tr = s.get('transition_in')
        if tr:
            if tr.get('kind') not in TRANSITION_KINDS:
                E.append(f'{sid}: transition kind {tr.get("kind")} not in TIMELINE kinds')
            if not isinstance(tr.get('frames'), int) or tr['frames'] <= 0:
                E.append(f'{sid}: transition frames must be a positive int')
            if tr.get('align', 'center') not in ('center', 'end'):
                E.append(f'{sid}: transition align must be center|end')
            if s is segs[0] and tr.get('kind') not in ('fade', 'flash'):
                E.append(f'{sid}: first segment can only fade/flash in')
    if exp != n:
        E.append(f'segments end at {exp - 1}, n_frames {n}')
    for op in edl.get('ops', []):
        if op.get('op') not in OP_KINDS:
            E.append(f'op {op.get("op")} unknown')
        fs = op.get('f')
        try:
            lst = [fs] if isinstance(fs, int) else ([int(x) for x in fs.split(':')] if isinstance(fs, str) else [int(x) if not isinstance(x, str) else int(x.split(':')[0]) for x in fs])
            if min(lst) < 0 or max(lst) > n - 1:
                E.append(f'op {op.get("op")} frames {fs} outside 0..{n - 1}')
        except Exception:
            E.append(f'op {op.get("op")}: bad f {fs}')
        if op.get('stage', 'pre') not in ('pre', 'post'):
            E.append('op stage must be pre|post')
    au = edl['audio']
    if not au.get('copy'):
        mu = au.get('music') or {}
        if mu and not os.path.exists(mu.get('path', '')):
            E.append('audio.music.path not found')
        if mu.get('in', 0) < 0:
            E.append('audio.music.in < 0')
        if not mu and not au.get('voice'):
            Wn.append('no music and no voice: the edit is silent apart from sound effects')
        for v in au.get('voice') or []:
            if not os.path.exists(v.get('path', '')):
                E.append(f'audio.voice path not found: {v.get("path")}')
            if v.get('at', 0) < 0 or v.get('in', 0) < 0:
                E.append('audio.voice at / in < 0')
    try:
        import ed_sfx as _S
    except Exception:
        _S = None
    va = getattr(_S, 'validate_audio', None) if _S is not None else None
    if callable(va):                                     # the mixer's own schema: sfx, music_fx, duck (one source of truth)
        try:
            ea, wa = va(au, total_s=n / fps, base_dir=au.get('base_dir'))
            E += [f'audio: {x}' for x in ea]
            Wn += [f'audio: {x}' for x in wa if 'unknown keys' not in x]
        except Exception as ex:
            Wn.append(f'audio check skipped ({ex})')
    else:
        kinds = (set(_S.KINDS) | set(getattr(_S, 'ALIASES', {}))) if _S is not None else SFX_KINDS
        lv_name = getattr(_S, 'level_name', None) if _S is not None else None
        base = au.get('base_dir')
        for x in au.get('sfx', []):
            label = x.get('kind') or os.path.basename(str(x.get('file') or ''))
            if x.get('file'):                       # a user sample: any kind label (or none)
                fp = os.path.expanduser(str(x['file']))
                if not os.path.exists(fp if (os.path.isabs(fp) or not base) else os.path.join(str(base), fp)):
                    E.append(f'sfx file not found: {x["file"]}')
            elif x.get('kind') not in kinds:
                E.append(f'sfx kind {x.get("kind")} unknown')
            if x.get('level') is not None:
                try:
                    if lv_name is not None:
                        lv_name(x['level'])
                    elif x['level'] not in ('light', 'normal', 'strong') and not isinstance(x['level'], (int, float)):
                        raise KeyError(x['level'])
                except KeyError:
                    Wn.append(f'sfx {label}: level {x["level"]!r} unknown - normal used')
            at = x.get('at', (x.get('t') or [None])[0] if isinstance(x.get('t'), (list, tuple)) else None)
            if not isinstance(at, (int, float)) or not (0 <= at <= n / fps + 0.01):
                E.append(f'sfx {label} at {at} outside the edit (needs "at" or "t": [t0, t1])')
            if x.get('align', 'attack') not in ('attack', 'peak', 'start', 'end'):
                E.append('sfx align must be attack|peak|start|end')
    lk, kind_of = layer_kinds()
    for L in edl.get('layers', []):
        if kind_of(L) not in lk:
            E.append(f'layer kind {L.get("kind")} unknown')
        if not (0 <= L.get('f0', -1) <= L.get('f1', -2) <= n - 1):
            E.append(f'layer {L.get("kind")} f0/f1 outside the edit')
    qa = edl['qa']
    for k in ('genre', 'on_beat_share', 'planned_black', 'planned_white', 'planned_freeze', 'flash_limit_hz', 'safe_zone', 'lufs', 'lufs_tol', 'tp_max'):
        if k not in qa:
            E.append(f'qa.{k} missing')
    for k in ('genre', 'scenario', 'version'):
        if k not in edl['meta']:
            E.append(f'meta.{k} missing')
    return E, Wn


# ============================================================================ storyboard (generate the whole video)
SB_SIZE = {'hook2': 'wide', 'drop_wide': 'wide', 'outro': 'wide', 'outro2': 'wide', 'drop_first': 'close-up',
           'burst': 'detail', 'crash': 'close-up (a face or a detail to crash into)', 'freeze': 'medium close-up at the peak'}
SB_SIZE_CYCLE = {'drop': ['medium', 'close-up', 'wide', 'detail'], 'build': ['medium', 'detail', 'medium close-up'],
                 'hook': ['medium close-up'], 'outro': ['wide']}
SB_HOOK_SIZE = {'epic': 'extreme wide (a small figure in a huge landscape)', 'calm': 'wide establishing',
                'travel': 'wide establishing (aerial if possible)', 'phonk': 'low-angle medium, silhouette against the light',
                'product': 'macro detail of the product (reveal)', 'fashion': 'full length, walking toward the camera',
                'drama': 'close-up, a still face', 'teaser': 'detail in darkness (partial reveal)'}
SB_CAMERA = {'epic': 'slow dolly-in or a crane move', 'calm': 'slow gimbal drift', 'phonk': 'handheld low angle, quick pans',
             'travel': 'gimbal or drone moving along the action', 'fashion': 'smooth gimbal orbit around the subject',
             'product': 'slow orbit / turntable, controlled light', 'sport': 'tracking with the action', 'viral': 'handheld push-in',
             'fanedit': 'dynamic push-in', 'teaser': 'slow creeping push-in', 'drama': 'locked-off or a slow push-in',
             'motivation': 'slow push-in, low angle'}
SB_ACTION = {'hook': 'a striking first image: the subject is revealed or looks into the lens',
             'build': 'preparation and rising tension: hands, details, walking in, getting ready',
             'drop': 'the peak action on the beat: movement, impact, energy', 'outro': 'release: the subject settles or walks away, a calm end frame'}


def _neutral_clip(path, k, w, h, fps, dur=30.0, fps_s=2.0):
    """Analysis-shaped stand-in for a shot that does not exist yet (storyboard): a readable subject, real motion with a
    peak every 1.5 s, neutral exposure; distinct thumbnails so no two stand-ins count as duplicates."""
    n = int(dur * fps_s)
    t = np.arange(n) / fps_s
    rows = []
    for i in range(n):
        resid = 8.0 + 16.0 * math.exp(-0.5 * (((t[i] % 1.5) - 0.75) / 0.2) ** 2)
        rows.append(dict(t=round(float(t[i]), 3), luma=110.0, p1=5.0, p5=12.0, p50=110.0, p95=200.0, p99=225.0, sat=0.3, warm=0.02,
                         sharp=300.0, clip=0.0, sky=0.2, sky_tex=10.0, strips=[110.0] * 8, pdiff=resid, hd=0.01, resid=resid,
                         sc=1.0, rot=0.0, tx=0.001, ty=0.0, cam_ok=1, faces=[[0.5, 0.4, 0.25, 0.9, 120.0]], person=[0.35, 0.5, 0.15, 0.95]))
    info = dict(path=path, duration=dur, has_audio=False, w=w, h=h, fps=float(fps))
    clip = dict(path=path, info=info, box=[0, 0, w, h], fps_sample=fps_s, width=320, version=FOOTAGE_VERSION, rows=rows, cuts=[],
                name=f'slot{k:02d}')
    grays = np.random.default_rng(1000 + k).integers(0, 255, (n, 18, 32)).astype(np.uint8)
    clip['_gray'] = grays
    clip['shots'] = _shots(clip, grays)
    return clip


def _look_words(grade, sty):
    g = dict(grade or {})
    words = []
    if g.get('mono') or str(g.get('preset', '')).startswith('bw'):
        words.append('black and white')
    t = float(g.get('temp', 0.0))
    words += ['warm'] if t > 0.05 else (['cool'] if t < -0.05 else [])
    s = float(g.get('sat', 1.0))
    words += ['muted colour'] if s < 0.85 else (['rich saturated colour'] if s > 1.1 else [])
    c = float(g.get('contrast', 1.0))
    words += ['high contrast'] if c >= 1.2 else (['soft contrast'] if c < 0.97 else [])
    if g.get('fade') or g.get('lift'):
        words.append('lifted matte blacks')
    lead = sty['preset']['description'].split(':')[0] if sty else None
    return ', '.join(([lead.lower()] if lead else []) + words) or 'natural light, true colour'


def _shot_brief(e, i, sl, sg, sty, brief, character, fps, slug, prev_size=None):
    """edit-gen brief of one storyboard slot: shot size, subject, action, camera move, duration with handles, continuity,
    look, speed, aspect, fps and a prompt-ready sentence."""
    part, role = sl.get('part'), sl.get('role')
    if role == 'hook':
        size = SB_HOOK_SIZE.get(slug, 'medium close-up, face to camera')
    elif role in SB_SIZE:
        size = SB_SIZE[role]
    else:
        cyc = SB_SIZE_CYCLE.get(part, ['medium'])
        size = cyc[i % len(cyc)]
        if size == prev_size and len(cyc) > 1:
            size = cyc[(i + 1) % len(cyc)]
    speed = sl.get('speed') or 'normal'
    action = SB_ACTION.get(part, 'a clear readable action')
    if role == 'drop_first':
        action = 'the strongest action of the video, peaking right at the start (it lands on the first beat of the drop)'
    if speed == 'ramp':
        action += '; fast continuous motion through the frame (a turn, a step, a throw) - it plays fast, slow, fast'
    elif speed == 'slow':
        action += '; fluid motion that reads in slow motion (hair, fabric, water, a turn)'
    elif speed == 'velocity':
        action += '; fast directional motion across the frame'
    elif speed in ('freeze', 'ramp_freeze'):
        action += '; one sharp peak moment for a freeze frame'
    camera = SB_CAMERA.get(slug, 'steady gimbal move')
    if sty and 'zoom.slow' in sty['preset']['moves'].get('prefer', []) and speed == 'normal':
        camera = 'slow push-in'
    n = sg['f1'] - sg['f0'] + 1
    out_s = n / fps
    need = float(sl.get('need_s') or out_s)
    handles = 0.5
    gen = need + 2 * handles
    gen_s = 5 if gen <= 5 else (10 if gen <= 10 else int(math.ceil(gen)))
    char = character if isinstance(character, str) else ((character or {}).get('description') or (character or {}).get('name'))
    subject = char or brief or 'the main subject'
    cont = []
    if char:
        cont.append(f'the same character in every shot: {char} (one reference / element for all slots)')
    if prev_size:
        cont.append(f'matches the previous shot ({prev_size}): same light, wardrobe and time of day')
    cont.append('screen direction left to right' if i % 2 == 0 else 'screen direction right to left (answers the previous shot)')
    look = _look_words(sg.get('grade'), sty)
    W_, H_ = e['canvas']['w'], e['canvas']['h']
    aspect = '9:16' if H_ > W_ else ('1:1' if H_ == W_ else '16:9')
    prompt = (f'{size} of {subject}, {action}. Camera: {camera}. Look: {look}. {aspect}, {gen_s} s, 24 fps, '
              f'no text, no logos, no watermarks.')
    return dict(slot=i, id=sg['id'], part=part, role=role, shot_size=size, subject=subject, action=action, camera=camera,
                duration=dict(slot_s=round(out_s, 3), source_s=round(need, 3), handles_s=handles, generate_s=gen_s),
                speed=speed, continuity=cont, look=look, aspect=aspect, fps=24, prompt=prompt)


def _draw_slate(path, b, w, h, t0, t1):
    """Storyboard slate image (the animatic shows it in the slot): number, time, size, action, camera."""
    grad = np.linspace(46, 22, h, dtype=np.float32)[:, None]
    img = np.ascontiguousarray(np.repeat(np.repeat(grad, w, axis=1)[..., None], 3, axis=2).astype(np.uint8))
    s = w / 1080.0
    cv2.rectangle(img, (int(40 * s), int(40 * s)), (w - int(40 * s), h - int(40 * s)), (90, 90, 90), max(1, int(2 * s)))
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, f'#{b["slot"] + 1:02d}', (int(80 * s), int(230 * s)), font, 5.0 * s, (235, 235, 235), max(2, int(9 * s)), cv2.LINE_AA)
    cv2.putText(img, f'{t0:.2f}-{t1:.2f} s  {b["part"]} / {b["role"] or ""}', (int(85 * s), int(320 * s)), font, 1.25 * s,
                (170, 200, 255), max(1, int(3 * s)), cv2.LINE_AA)

    def wrap(text, n=34):
        out, line = [], ''
        for wd in str(text).split():
            if len(line) + len(wd) + 1 > n:
                out.append(line)
                line = wd
            else:
                line = (line + ' ' + wd).strip()
        return out + ([line] if line else [])
    y = int(440 * s)
    for label, text in (('SIZE', b['shot_size']), ('ACTION', b['action']), ('CAMERA', b['camera']), ('SPEED', b['speed'])):
        cv2.putText(img, label, (int(85 * s), y), font, 0.95 * s, (120, 220, 160), max(1, int(2 * s)), cv2.LINE_AA)
        y += int(52 * s)
        for ln in wrap(text)[:6]:
            cv2.putText(img, ln, (int(85 * s), y), font, 1.15 * s, (230, 230, 230), max(1, int(2 * s)), cv2.LINE_AA)
            y += int(54 * s)
        y += int(30 * s)
    cv2.imwrite(path, img)
    return path


def plan_storyboard(track, genre=None, style=None, dur=None, brief=None, canvas=(1080, 1920), fps=30, n_shots=None,
                    character=None, **opts):
    """A whole video to generate, cut to the user's track: the genre plan (music window, parts, cut grid, speeds,
    moves, sound, grade) over stand-in shots, then every slot becomes a gap placeholder - a slate image in the
    animatic and an edit-gen brief in meta.gaps (shot size, subject, action, camera move, duration with handles,
    continuity, look, speed, prompt). meta.storyboard keeps each slot's timing, speed mapping, crop zooms and grade
    for fill_gaps(). genre / style: either (words work: resolve_style); brief: what the video is about; character: a
    description (str) or {"name", "description", ...} kept identical across all briefs. Slates go to out_dir
    (default cache_dir, else ~/.cache/edit-studio)/storyboard."""
    W_, H_ = canvas
    root = opts.pop('out_dir', None) or opts.get('cache_dir') or os.path.join(os.environ.get('ED_ROOT', 'C:/Claude Code/cinema-studio/edit'), 'cache')
    key = hashlib.md5(f'{track}|{genre}|{style}|{brief}|{dur}|{n_shots}|{opts.get("variant")}'.encode()).hexdigest()[:10]
    sb_dir = os.path.join(root, 'storyboard', key)
    os.makedirs(sb_dir, exist_ok=True)
    if not genre and not style:
        style = brief or ''
    blank = os.path.join(sb_dir, f'blank_{W_}x{H_}.png')
    if not os.path.exists(blank):
        cv2.imwrite(blank, np.full((H_, W_, 3), 40, np.uint8))
    n_clips = max(24, int(n_shots or 0) + 4)
    F = Footage.from_clips([_neutral_clip(blank, k, W_, H_, fps) for k in range(n_clips)], log=None)
    opts = dict(opts)
    opts.update(footage_obj=F, reframe=False, fit_grades=False, check_dark=False, check_cuts=False)
    e = plan_genre(track, None, genre, canvas, fps, dur, style=style, n_shots=n_shots, **opts)
    slug = e['meta']['genre']
    sty = style_context(style, slug, opts.get('variant'), opts.get('avoid')) if (style or opts.get('variant') or opts.get('avoid')) else None
    slots_meta = e['meta']['slots']
    plans, gaps, prev_size, prev_src = [], [], None, None
    new_sources = {}
    for i, sg in enumerate(e['segments']):
        sl = slots_meta[i] if i < len(slots_meta) else {}
        n = sg['f1'] - sg['f0'] + 1
        if sg.get('speed') == 0.0 and 'black pause' in str(sg.get('note', '')):
            sg['src'] = prev_src or sg['src']
            sg['t'] = 0.0
            plans.append(dict(slot=i, id=sg['id'], kind='black', f=[sg['f0'], sg['f1']]))
            continue
        if sg.get('times'):
            tt = np.asarray(sg['times'], float)
            rel = (tt - tt.min()).round(6).tolist()
        else:
            rel = (np.arange(n) / fps * float(sg.get('speed', 1.0))).round(6).tolist()
        need = float(max(rel) + 1.0 / fps)
        sl = dict(sl, need_s=need)
        b = _shot_brief(e, i, sl, sg, sty, brief, character, fps, slug, prev_size)
        prev_size = b['shot_size']
        name = f'slot{i + 1:02d}'
        slate = _draw_slate(os.path.join(sb_dir, f'{name}.png'), b, W_, H_, sg['f0'] / fps, (sg['f1'] + 1) / fps)
        cr = sg.get('crop') or {}
        zp = [[p_[0], p_[3]] for p_ in cr.get('path', [])] or [[0, cr.get('z', 1.0)], [n - 1, cr.get('z', 1.0)]]
        plans.append(dict(slot=i, id=sg['id'], part=sl.get('part'), role=sl.get('role'), kind=sl.get('kind', 'shot'), f=[sg['f0'], sg['f1']],
                          speed=sl.get('speed') or 'normal', rel_times=rel, need_s=round(need, 4), z=zp, rot=cr.get('rot'),
                          grade=dict(sg.get('grade') or {}), interp=sg.get('interp'), brief=b))
        new_sources[name] = dict(path=slate)
        sg.update(src=name, t=0.0, speed=1.0, grade=dict(preset='natural'),
                  crop=dict(cx=0.5, cy=0.5, z=1.0, path=[[p_[0], 0.5, 0.5, p_[1]] for p_ in zp], center=[0.5, 0.45]))
        for k_ in ('times', 'speed_curve', 'interp', 'stutter'):
            sg.pop(k_, None)
        prev_src = name
        gaps.append(dict(slot=i, id=sg['id'], part=sl.get('part'), role=sl.get('role'), kind='storyboard',
                         reason='storyboard: this shot is to be generated', fill=None, t=[round(sg['f0'] / fps, 3), round((sg['f1'] + 1) / fps, 3)],
                         f=[sg['f0'], sg['f1']], dur=round(n / fps, 3), need_s=round(need, 3), brief=b))
    e['sources'] = new_sources
    # slates are stills: their holds are the design of an animatic, not a frozen render (ed_qa planned_freeze)
    e['qa']['planned_freeze'] = sorted([list(x) for x in (e['qa'].get('planned_freeze') or [])] +
                                       [[sg['f0'], sg['f1']] for sg in e['segments'] if sg['src'] in new_sources])
    e['meta'].update(scenario='storyboard', gaps=gaps,
                     storyboard=dict(slots=plans, brief=brief, character=character, dir=sb_dir, filled={},
                                     cache_dir=opts.get('cache_dir')))
    e['meta']['notes'] = list(e['meta'].get('notes') or []) + [f'storyboard: {len(gaps)} shots to generate (edit-gen briefs in meta.gaps)']
    return e


def _slot_key(e, key):
    segs = e['segments']
    if isinstance(key, int) or (isinstance(key, str) and key.lstrip('#').isdigit()):
        k = int(str(key).lstrip('#'))
        return k - 1 if str(key).startswith('#') or not isinstance(key, int) else k
    for i, s in enumerate(segs):
        if s['id'] == key or s.get('src') == key:
            return i
    raise KeyError(f'unknown slot {key!r}')


def fill_gaps(edl, clips, cache_dir=None, log=None):
    """Plug generated (or the user's) clips into storyboard / gap slots -> new EDL (version + 1). clips:
    {slot: path | {"path", "t"}} where slot is a segment id ('C03'), a slot source ('slot03'), a 1-based '#3' or a
    0-based int. Per slot: the clip is analysed, the best window for the slot's role and speed mapping is chosen (or
    "t"), a clip shorter than the slot needs is slowed down to fit (reported in meta.gaps as 'stretched'), the crop
    follows the subject (ed_reframe) with the planned zooms / tilt kept, the planned grade gets the clip's exposure
    and the genre's colour fit, and punch / crash centres move to the subject."""
    e = copy.deepcopy(edl)
    fps = e['canvas']['fps']
    W_, H_ = e['canvas']['w'], e['canvas']['h']
    sb = e['meta'].get('storyboard') or {}
    plans = {p['id']: p for p in sb.get('slots', [])}
    slug = e['meta'].get('genre') or 'viral'
    cache = cache_dir or sb.get('cache_dir')
    done, notes, faces = [], [], {}
    taken = set(e['sources'])
    for key, v in clips.items():
        si = _slot_key(e, key)
        sg = e['segments'][si]
        path, t_given = (v, None) if isinstance(v, str) else (v['path'], v.get('t'))
        c = analyze_clip(path, cache, 6.0)
        name = _clean_name(os.path.splitext(os.path.basename(path))[0], taken)
        taken.add(name)
        c = dict(c, name=name)
        F = Footage.from_clips([c])
        n = sg['f1'] - sg['f0'] + 1
        p = plans.get(sg['id']) or dict(rel_times=(np.arange(n) / fps).tolist(), need_s=n / fps, z=[[0, 1.0], [n - 1, 1.0]], grade=sg.get('grade') or {},
                                        role=None, part=None, speed='normal')
        rel = np.asarray(p['rel_times'], float)
        need = float(rel.max() + 1.0 / fps)
        avail = max(sh['t1'] - sh['t0'] for sh in F.shots)
        stretched = None
        if t_given is None and need > avail - 0.1:
            rate = max(0.25, (avail - 0.1) / need)
            rel = rel * rate
            need = float(rel.max() + 1.0 / fps)
            stretched = round(rate, 3)
        if t_given is not None:
            sh = next((x for x in F.shots if x['t0'] - 1e-6 <= float(t_given) < x['t1']), F.shots[0])
            w0 = float(t_given)
        else:
            best = None
            slot_like = dict(i=si, part=p.get('part') or 'drop', role=p.get('role') or 'drop', kind=p.get('kind') or 'shot',
                             speed=dict(mode=p.get('speed') or 'normal'))
            for sh_, w0_, _al in F.candidates(need, 0.0, 0.0, (), margin=0.05):
                W = F.win(sh_, w0_, w0_ + need)
                sc, _ = score_window(slug, slot_like['role'], W, slot_like, 0.5)
                if p.get('speed') in ('ramp', 'velocity'):
                    sc += 0.8 * W['peak_r'] + 0.5 * W['motion_r']
                if best is None or sc > best[0]:
                    best = (sc, sh_, w0_)
            if best is None:
                sh, w0 = max(F.shots, key=lambda x: x['dur']), F.shots[0]['t0'] + 0.02
            else:
                _, sh, w0 = best
        times = w0 + rel
        W = F.win(sh, w0, min(sh['t1'], w0 + need))
        pk = dict(shot=sh['id'], ci=0, src=name, w0=w0, w1=w0 + need, W=W)
        crop = _crop_for(F.clips[0], pk, dict(role=p.get('role'), part=p.get('part'), speed=dict(mode=p.get('speed') or 'normal')),
                         times, fps, W_ / H_, True)
        zk = [z[0] for z in p['z']]
        zv = [z[1] for z in p['z']]
        crop['path'] = [[k, x, y, round(float(np.interp(k, zk, zv)), 4)] for k, x, y, _ in crop['path']]
        crop['z'] = crop['path'][0][3]
        if p.get('rot'):
            crop['rot'] = p['rot']
        center = crop.pop('_center', [0.5, 0.45])
        crop.pop('_win_w', None)
        crop['center'] = center
        bx = F.clips[0].get('box')
        full = [0, 0, F.clips[0]['info'].get('w'), F.clips[0]['info'].get('h')]
        e['sources'][name] = dict(path=os.path.abspath(path), **({'box': bx} if bx and bx != full else {}))
        sg['src'], sg['t'] = name, round(float(times[0]), 4)
        steps = np.diff(times)
        for k_ in ('times', 'speed_curve', 'interp', 'stutter'):
            sg.pop(k_, None)
        if len(steps) == 0 or np.allclose(steps, steps[0], atol=2e-4):
            sp_ = float(np.mean(steps) * fps) if len(steps) else 1.0
            sg['speed'] = 1.0 if abs(sp_ - 1.0) < 0.005 else round(sp_, 3)
            if sg['speed'] < 0.995:
                sg['interp'] = 'flow'
        else:
            sg.pop('speed', None)
            sg['times'] = [round(float(x), 4) for x in times]
            rates = np.append(steps * fps, steps[-1] * fps)
            sg['speed_curve'] = [[int(k), round(float(r), 3)] for k, r in enumerate(rates)]
            sg['interp'] = 'flow'
        sg['crop'] = crop
        grade = dict(p.get('grade') or {})
        cl = F.crop_luma(0, float(times.min()), float(times.max()) + 1.0 / fps, float(np.median([q[1] for q in crop['path']])),
                         min(1.0, (W_ / H_) / max(1e-6, (F.clips[0]['info'].get('w') or 16) / (F.clips[0]['info'].get('h') or 9))))
        ev = exposure_ev(slug, cl, W.get('p99'), W.get('face_luma') if (W.get('face_share') or 0) >= 0.3 else None)
        if ev:
            grade['exposure'] = ev
        sg['grade'] = grade
        if W.get('face_cx') is not None and (W.get('face_share') or 0) >= 0.3 and W.get('face_h'):
            faces[sg['id']] = (W['face_cx'], W.get('face_cy') or 0.4, W['face_h'])
        for fx in sg.get('fx', []):
            if fx.get('type') in ('zoom.punch', 'zoom.crash', 'zoom.in_out') and 'center' in fx:
                fx['center'] = center
        e['meta']['gaps'] = [g_ for g_ in e['meta'].get('gaps', []) if g_.get('id', None) != sg['id'] and g_.get('slot') != si]
        if stretched:
            e['meta']['gaps'].append(dict(slot=si, id=sg['id'], part=p.get('part'), role=p.get('role'), kind='stretched',
                                          reason=f'the clip is {avail:.2f} s, the slot needs {need / stretched:.2f} s', fill=name,
                                          brief=p.get('brief')))
            notes.append(f'{sg["id"]}: {name} slowed to {stretched}x to fill the slot')
        sb.setdefault('filled', {})[sg['id']] = os.path.abspath(path)
        done.append(sg)
    used = {s['src'] for s in e['segments']}
    e['sources'] = {k: v for k, v in e['sources'].items() if k in used}
    filled = {(s['f0'], s['f1']) for s in done}
    e['qa']['planned_freeze'] = [x for x in (e['qa'].get('planned_freeze') or []) if tuple(x) not in filled]
    if done:
        dark = bool((e['meta'].get('options') or {}).get('dark') or (e['meta'].get('choices') or {}).get('dark'))
        _fit_grades(dict(e, segments=done), slug, faces=faces, limits=PICTURE_LIMITS_DARK if dark else PICTURE_LIMITS)
    if sb:
        e['meta']['storyboard'] = sb
        if not [g_ for g_ in e['meta'].get('gaps', []) if g_.get('kind') == 'storyboard']:
            e['meta']['scenario'] = 'genre'
    e['meta']['notes'] = list(e['meta'].get('notes') or []) + notes
    return _finish(e, dict(cmd=dict(op='fill_gaps', slots=sorted(str(k) for k in clips)),
                           changed=[f'{s["id"]}: {s["src"]} @ {s.get("t", 0):.2f}s' for s in done]))


# ============================================================================ point edits
def _seg_at_time(edl, t):
    f = int(round(t * edl['canvas']['fps']))
    for i, s in enumerate(edl['segments']):
        if s['f0'] <= f <= s['f1']:
            return i
    return len(edl['segments']) - 1


def _seg_index(edl, ref):
    if ref is None:
        return None
    if isinstance(ref, int) or (isinstance(ref, str) and ref.lstrip('#').isdigit()):
        k = int(str(ref).lstrip('#')) - 1
        return k if 0 <= k < len(edl['segments']) else None
    for i, s in enumerate(edl['segments']):
        if s['id'] == ref:
            return i
    return None


def _beat_frames(edl):
    """Beat frames of the edit: meta.grid.frames (genre EDLs) or audio.grid.beats (composites, other planners)."""
    fr = (edl['meta'].get('grid') or {}).get('frames')
    if fr:
        return list(fr)
    beats = ((edl.get('audio') or {}).get('grid') or {}).get('beats') or []
    fps = edl['canvas']['fps']
    return sorted({frame_at(float(t), fps) for t in beats if 0 <= float(t) * fps < edl['n_frames']})


def _period(edl):
    gr = edl['meta'].get('grid') or {}
    if gr.get('period'):
        return float(gr['period'])
    bpm = ((edl.get('audio') or {}).get('grid') or {}).get('bpm')
    return 60.0 / float(bpm) if bpm else 0.5


def _as_range(v):
    if isinstance(v, dict):
        if 'f' in v:
            v = v['f']
        elif 'f0' in v and 'f1' in v:
            v = [v['f0'], v['f1']]
        else:
            return None
    if isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
        return [int(v[0]), int(v[1])]
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return [int(v), int(v)]
    return None


def _comp_parts(edl):
    """Parts of a composite timeline (ed_sequence: meta.parts is a list of {id, type, f0, f1, genre, ...}), else None."""
    ps = edl['meta'].get('parts')
    return ps if isinstance(ps, list) else None


def _comp_part_at(edl, f):
    for pm in _comp_parts(edl) or []:
        if pm.get('f0', 0) <= f <= pm.get('f1', -1):
            return pm
    return None


def _section_range(pm, name):
    """[f0, f1] of a section (hook / build / drop / outro) of one edit part of a composite, from what ed_sequence
    exposes: pm['parts' | 'sections'][name] ({'f': [a, b]} | [a, b] | {'f0', 'f1'}), pm[name], pm[name + '_f'] /
    pm[name + '_frames'], or for the drop pm['drop_frame'] up to the part's end."""
    for holder in (pm.get('parts'), pm.get('sections'), pm):
        if isinstance(holder, dict) and name in holder:
            fr = _as_range(holder[name])
            if fr:
                return fr
    for key in (name + '_f', name + '_frames'):
        fr = _as_range(pm.get(key))
        if fr:
            return fr
    if name == 'drop' and pm.get('drop_frame') is not None:
        return [int(pm['drop_frame']), int(pm['f1'])]
    return None


def part_range(edl, part, near=None):
    """[f0, f1] of a named part. Genre EDL: meta.parts[part]['f']. Composite (meta.parts is a list): a part id
    ('talk', 'hype'), 'id.section' / 'id:section' ('hype.drop'), or a section name (hook / build / drop / outro) of
    the edit part that contains frame `near` (else the first edit part that exposes it; the drop falls back to the
    part with drop_frame). Raises ValueError naming what exists."""
    ps = edl['meta'].get('parts')
    if isinstance(ps, dict):
        if part in ps and _as_range(ps[part]):
            return _as_range(ps[part])
        raise ValueError(f'unknown part {part!r}; this edit has {sorted(ps)}')
    comp = _comp_parts(edl) or []
    pid, _, sec = str(part).replace(':', '.').partition('.')
    by_id = {pm.get('id'): pm for pm in comp}
    if pid in by_id and not sec:
        return [int(by_id[pid]['f0']), int(by_id[pid]['f1'])]
    if pid in by_id and sec:
        fr = _section_range(by_id[pid], sec)
        if fr:
            return fr
        raise ValueError(f'part {pid!r} exposes no {sec!r} frames')
    name = str(part)
    edits = [pm for pm in comp if pm.get('type') == 'edit']
    if near is not None:
        edits.sort(key=lambda pm: 0 if pm.get('f0', 0) <= near <= pm.get('f1', -1) else 1)
    for pm in edits:
        fr = _section_range(pm, name)
        if fr:
            return fr
    if name == 'drop':
        pm = next((pm for pm in edits if pm.get('drop_frame') is not None), edits[0] if edits else None)
        if pm is not None:
            return [int(pm.get('drop_frame', pm['f0'])), int(pm['f1'])]
    raise ValueError(f'unknown part {part!r}; this timeline has parts {[pm.get("id") for pm in comp]}'
                     + (' (edit parts expose hook / build / drop / outro)' if edits else ''))


def _section_of(edl, f):
    """Section name (hook / build / drop / outro) at frame f, for the move rules; None when unknown."""
    ps = edl['meta'].get('parts')
    if isinstance(ps, dict):
        for k, v in ps.items():
            fr = _as_range(v)
            if fr and fr[0] <= f <= fr[1]:
                return k
        return None
    pm = _comp_part_at(edl, f)
    if pm is None or pm.get('type') != 'edit':
        return None
    for name in PARTS:
        fr = _section_range(pm, name)
        if fr and fr[0] <= f <= fr[1]:
            return name
    return None


def _genre_for(edl, f=None):
    """Genre card governing a point edit at frame f: the edit part's genre in a composite, else meta.genre; None
    when it is missing or unknown (the command then runs without the card's move rules)."""
    name = None
    if f is not None and _comp_parts(edl):
        pm = _comp_part_at(edl, f)
        if pm is not None and pm.get('type') != 'edit':
            return None                     # a talk / clip part: cut by words, no music-genre card rules
        name = (pm or {}).get('genre')
    name = name or edl['meta'].get('genre')
    if not name:
        return None
    try:
        return load_genre(name)
    except (KeyError, OSError, ValueError):
        return None


def _nearest_beat(edl, f, lo=None, hi=None):
    fr = [x for x in _beat_frames(edl) if (lo is None or x >= lo) and (hi is None or x <= hi)]
    return min(fr, key=lambda x: abs(x - f)) if fr else f


# moves a point edit can place without a re-plan (_move_fx); the pool of op 'family' when the timeline has no genre
PLACEABLE = ('zoom.punch', 'zoom.crash', 'zoom.in_out', 'shake.beat', 'fx.rgb_split', 'fx.glitch', 'glitch.vhs', 'glitch.datamosh',
             'glitch.pixel_sort', 'glitch.tv_noise', 'glitch.film_damage', 'fx.glow', 'fx.light_leak', 'light.halation',
             'lens.vignette', 'fx.film_overlay', 'light.flash', 'trans.flash', 'trans.dissolve', 'trans.fade', 'trans.whip',
             'trans.zoom', 'trans.spin', 'trans.lens_distort', 'trans.wipe', 'glitch.transition', 'zoom.slow', 'zoom.out',
             'zoom.in', 'angle.dutch', 'type.title_card', 'type.beat_text', 'type.kinetic', 'type.lower_third')


def _move_fx(mid, fps, center, period, k, params=None):
    """EDL entry for a move placed by a point edit: ('fx', dict) | ('transition', dict) | ('crop', fn) | (None, reason)."""
    p = dict(params or {})
    c = center or [0.5, 0.45]
    if mid == 'zoom.punch':
        d = dict(type='zoom.punch', frames=[k], **dict(P_PUNCH['strong'], **p), center=c)
    elif mid == 'zoom.crash':
        k0 = max(0, k - int(round(0.4 * fps)))
        d = dict(type='zoom.crash', frames=[k0], scale=p.get('scale', 3.5), dur=p.get('dur', 0.4), ease='inOutCubic', blur='zoom',
                 hold_after='cut', center=c)
    elif mid == 'zoom.in_out':
        d = dict(type='zoom.in_out', frames=[k], scale=p.get('scale', 1.3), stroke=round(period / 2, 3), ease=['outCubic', 'inCubic'], hold=0, center=c)
    elif mid == 'shake.beat':
        prof = p.pop('profile', 'impact')
        d = dict(type='shake.beat', frames=[k], **dict(P_SHAKE.get(prof, P_SHAKE['impact']), **p), seed=k)
    elif mid == 'fx.rgb_split':
        lvl = p.pop('level', 'normal')
        d = dict(type='rgb_split', frames=[k], **dict(P_RGB.get(lvl, P_RGB['normal']), **p))
    elif mid in ('fx.glitch', 'glitch.datamosh', 'glitch.vhs', 'glitch.pixel_sort', 'glitch.tv_noise', 'glitch.film_damage'):
        typ = {'fx.glitch': 'glitch_blocks', 'glitch.pixel_sort': 'pixel_sort', 'glitch.vhs': 'vhs', 'glitch.datamosh': 'datamosh',
               'glitch.tv_noise': 'tv_noise', 'glitch.film_damage': 'film_damage'}[mid]
        d = dict(type=typ, frames=list(range(k, k + int(p.pop('frames', 3)))), intensity=p.get('intensity', 0.6))
    elif mid == 'fx.glow':
        d = dict(type='glow', threshold=0.72, strength=p.get('strength', 0.3), radii=[0.004, 0.015, 0.04, 0.1])
    elif mid == 'fx.light_leak':
        d = dict(type='light_leak', mode='accent', frames=[k], shape=p.get('shape', 'edge'), palette=p.get('palette', 'amber'),
                 anchor=p.get('anchor', 'left'))
    elif mid == 'light.halation':
        d = dict(type='glow', threshold=0.85, knee=0.1, strength=p.get('strength', 0.3), radii=[0.006, 0.015, 0.03, 0.06],
                 tint='#ff5a1a', tint_mix=0.45, blend='screen')
    elif mid.startswith('type.'):
        return 'layer', dict(kind={'type.title_card': 'title_card', 'type.beat_text': 'beat_text', 'type.kinetic': 'kinetic',
                                   'type.intertitle': 'intertitle', 'type.lower_third': 'lower_third', 'type.subtitles': 'subtitle',
                                   'type.karaoke': 'karaoke'}.get(mid, 'static'))
    elif mid == 'lens.vignette':
        d = dict(type='vignette', amount=p.get('amount', 0.3))
    elif mid == 'fx.film_overlay':
        d = dict(type='film_overlay', level=p.get('level', 2), delivery='social')
    elif mid == 'light.flash':
        return 'op', dict(op='flash', color=p.get('color', '#ffffff'), curve=_exp_curve(0.04, fps), blend='screen')
    elif mid == 'trans.flash':
        return 'transition', dict(kind='flash', frames=len(_exp_curve(0.06, fps)), align='end',
                                  params=dict(color=p.get('color', '#ffffff'), mode='solid', peak_frames=1, tau=0.06, curve=_exp_curve(0.06, fps)))
    elif mid == 'trans.dissolve':
        fr = int(p.get('frames', round(p.get('dur', 1.0) * fps)))
        return 'transition', dict(kind='dissolve', frames=fr - fr % 2 or 2, align='center', params=dict(curve=p.get('curve', 'linear')))
    elif mid == 'trans.fade':
        return 'transition', dict(kind='dip', frames=int(p.get('frames', 10)), align='center', params=dict(color='#000000', out=3, hold=2, **{'in': 5}))
    elif mid == 'trans.whip':
        return 'transition', dict(kind='whip', frames=int(p.get('frames', 6)), align='center',
                                  params=dict(dir=p.get('dir', p.get('direction', 'left')), shutter=p.get('shutter', 0.7)))
    elif mid == 'trans.zoom':
        return 'transition', dict(kind='zoom', frames=int(p.get('frames', 12)), align='center',
                                  params=dict(out_scale=3, in_scale=1.5, mode='through', ease=['inExpo', 'outExpo'], blur='zoom'))
    elif mid == 'trans.spin':
        return 'transition', dict(kind='spin', frames=int(p.get('frames', 10)), align='center', params=dict(angle=p.get('angle', 180), blur=0.5))
    elif mid == 'trans.lens_distort':
        return 'transition', dict(kind='lens', frames=int(p.get('frames', 10)), align='center', params=dict(mode=p.get('mode', 'bulge')))
    elif mid == 'trans.wipe':
        return 'transition', dict(kind='wipe', frames=int(p.get('frames', 10)), align='center', params=dict(shape='linear', angle=0, softness=0.05))
    elif mid == 'trans.liquid':
        return 'transition', dict(kind='liquid', frames=int(p.get('frames', 14)), align='center', params={})
    elif mid == 'glitch.transition':
        return 'transition', dict(kind='glitch', frames=11, align='center', params=dict(streaks='vertical'))
    elif mid in ('zoom.slow', 'zoom.out', 'zoom.in'):
        return 'crop', dict(z0=1.0 if mid != 'zoom.out' else p.get('scale', 1.3), z1=p.get('scale', 1.1) if mid != 'zoom.out' else 1.0,
                            ease='linear' if mid != 'zoom.out' else 'outCubic')
    elif mid == 'angle.dutch':
        return 'crop', dict(rot=p.get('angle', 15.0))
    else:
        return None, f'{mid}: a point edit cannot place this move yet (needs a re-plan or a special shot)'
    d['move'] = mid
    return 'fx', d


def apply_command(edl, cmd):
    """Structured point edit -> new EDL (deep copy; meta.version + 1, meta.history appended). Claude turns the user's
    words into the dict; times are output time ('0:07' or 7.0), clips are ids ('C05') or 1-based numbers (5 / '#5').
      {"op": "add", "move": "zoom.crash", "at": "0:07"}                     # lands on the beat nearest to 0:07
      {"op": "add", "move": "zoom.punch", "clip": "C05", "params": {"scale": 1.25}}
      {"op": "replace", "move": "trans.whip", "replace": "trans.flash", "clip": 5}   # no "replace": same family as move
      {"op": "remove", "move": "shake.beat", "part": "drop"}               # scope: at / clip / part / everything; move may be a family
      {"op": "transition", "between": ["C04", "C05"], "move": "trans.whip"} # or "at": the cut nearest to that time
      {"op": "family", "family": "glitch", "part": "drop"}                  # any allowed move of the family, first beat of the part
      {"op": "swap", "clip": "C05", "with": "next" | {"src": "clipname", "t": 12.3} | {"shot": "clip#3"}}
    A move the genre card forbids is refused with the reason (add "force": true to override).
    Composite timelines (ed_sequence, meta.parts is a list): "part" is a part id ("hype"), "hype.drop", or a section
    (hook / build / drop / outro) of the edit part at "at" / "clip" (else the first edit part that has it); the rules
    of the edit part's genre apply. No genre (or an unknown one): the command runs without card rules."""
    e = copy.deepcopy(edl)
    fps = e['canvas']['fps']
    period = _period(e)
    op = cmd.get('op', 'add')
    res = dict(cmd=cmd, changed=[])
    segs = e['segments']
    t_at = parse_time(cmd.get('at'))
    part = cmd.get('part')
    si = _seg_index(e, cmd.get('clip'))
    if cmd.get('between'):
        a_, b_ = (_seg_index(e, x) for x in cmd['between'])
        if a_ is None or b_ is None or b_ != a_ + 1:
            raise ValueError(f'between {cmd["between"]}: clips must be neighbours')
        si = b_
    if si is None and t_at is not None:
        si = _seg_at_time(e, t_at)
    near = segs[si]['f0'] if si is not None else None
    prange = part_range(e, part, near) if part else None
    g = _genre_for(e, near if near is not None else (prange[0] if prange else None))
    sec = str(part).replace(':', '.').split('.')[-1] if part else None
    sec = sec if sec in PARTS else (_section_of(e, prange[0]) if prange else None)

    def slot_part(i):
        if i is None:
            return None
        sl = e['meta'].get('slots') or []
        if i < len(sl) and isinstance(sl[i], dict) and sl[i].get('part'):
            return sl[i]['part']
        return _section_of(e, segs[i]['f0'])
    if op == 'family':
        fam = cmd['family']
        pool = moves_of_family(g, fam, sec) if g is not None else []
        if g is None or (not pool and cmd.get('force')):
            pool = [m for m in PLACEABLE if m.split('.')[0] == fam]
        cand = [m for m in pool if _move_fx(m, fps, None, period, 0)[0] is not None]
        if not cand:
            raise ValueError((f'genre {g["slug"]} has no allowed move of family {fam!r}' if g is not None else
                              f'no placeable move of family {fam!r}') + (f' in part {part}' if part else ''))
        at = cmd.get('at')
        if at is None and part:
            fb = prange[0]
            inner = [x for x in _beat_frames(e) if fb < x <= prange[1]]
            at = (inner[0] if (inner and _move_fx(cand[0], fps, None, period, 0)[0] == 'fx') else fb) / fps
        out = apply_command(edl, dict(op='add', move=cand[0], at=at, clip=cmd.get('clip'), params=cmd.get('params'), force=cmd.get('force')))
        out['meta']['history'][-1]['cmd'] = cmd
        out['meta']['history'][-1]['picked'] = cand[0]
        return out
    mid = cmd.get('move')
    if op in ('add', 'replace', 'transition'):
        if not mid:
            raise ValueError(f'{op} needs "move"')
        ok, reason = move_allowed(g, mid, sec or slot_part(si)) if g is not None else (True, 'no genre card')
        if not ok and not reason.startswith(NOT_IN_PART) and not cmd.get('force'):
            raise ValueError(f'{mid}: {reason} — the move is not placed in genre {g["slug"]} (force: true to place it anyway)')
    # ---------------------------------------------------------------- remove / replace (removal half)
    removed_at = None
    if op in ('remove', 'replace'):
        target = cmd.get('replace') if op == 'replace' else mid
        if op == 'replace' and not target:
            target = mid.split('.')[0]                 # same family as the new move
        fam = bool(target) and '.' not in target
        hit = lambda m: (target is None) or (m == target) or (fam and str(m).split('.')[0] == target)
        if si is not None:
            scope = [si]
        elif part:
            pf = prange
            scope = [i for i, x in enumerate(segs) if pf[0] <= x['f0'] <= pf[1] or x['f0'] <= pf[0] <= x['f1']]
        else:
            scope = list(range(len(segs)))
        for i in scope:
            x = segs[i]
            keep = []
            for fx in x.get('fx', []):
                mm = fx.get('move', fx['type'])
                if hit(mm) and mm != 'grade':
                    res['changed'].append(f'{x["id"]}: removed {mm}')
                    if removed_at is None and isinstance(fx.get('frames'), list) and fx['frames']:
                        removed_at = x['f0'] + int(fx['frames'][0])
                else:
                    keep.append(fx)
            x['fx'] = keep
            tr = x.get('transition_in')
            if tr and hit(tr.get('move', tr.get('kind'))):
                x.pop('transition_in')
                res['changed'].append(f'{x["id"]}: removed transition {tr.get("move")}')
                removed_at = x['f0'] if removed_at is None else removed_at
        lo = min(segs[i]['f0'] for i in scope)
        hi = max(segs[i]['f1'] for i in scope)
        n_ops, n_sfx = len(e['ops']), len(e['audio']['sfx'])
        e['ops'] = [o for o in e['ops'] if not (target and hit(o.get('move')) and lo <= _op_f0(o) <= hi)]
        e['audio']['sfx'] = [x for x in e['audio']['sfx'] if not (target and hit(x.get('move')) and lo <= ev_at(x, -99.0) * fps <= hi + 1)]
        if len(e['ops']) < n_ops:
            res['changed'].append(f'frame ops removed: {n_ops - len(e["ops"])}')
        if len(e['audio']['sfx']) < n_sfx:
            res['changed'].append(f'sounds removed: {n_sfx - len(e["audio"]["sfx"])}')
        if op == 'remove':
            return _finish(e, res)
    if op == 'swap':
        return _finish(e, _swap(e, si, cmd, res))
    # ---------------------------------------------------------------- add (also the second half of replace)
    if si is None:
        if part:
            si = _seg_at_time(e, prange[0] / fps)
        else:
            raise ValueError('the command needs "at", "clip", "between" or "part"')
    kind, d = _move_fx(mid, fps, None, period, 0, cmd.get('params'))
    if kind is None:
        raise ValueError(d)
    if kind == 'transition' or op == 'transition':
        if kind != 'transition':
            raise ValueError(f'{mid} is not a transition')
        if t_at is not None and cmd.get('clip') is None and not cmd.get('between'):
            fc = min((x['f0'] for x in segs[1:]), key=lambda f: abs(f - t_at * fps))     # the cut nearest to that time
            si = next(i for i, x in enumerate(segs) if x['f0'] == fc)
        if si == 0:
            raise ValueError('there is no cut before the first clip')
        x = segs[si]
        d['move'] = mid
        x['transition_in'] = d
        res['changed'].append(f'{x["id"]}: transition {mid} ({d["kind"]}, {d["frames"]} frames) on the cut at {tcode(x["f0"] / fps)}')
        return _finish(e, res)
    x = segs[si]
    f_target = removed_at if (op == 'replace' and removed_at is not None and t_at is None) else (
        int(round(t_at * fps)) if t_at is not None else None)
    if f_target is None:
        lo_t = max(x['f0'] + 1, prange[0]) if prange else x['f0'] + 1       # inside the named part
        inner = [f for f in _beat_frames(e) if lo_t <= f <= x['f1']]
        f_target = inner[0] if inner else (min(max(prange[0], x['f0']), x['f1']) if prange else x['f0'] + (x['f1'] - x['f0']) // 2)
    lo = x['f0'] + (0 if kind in ('op', 'crop') else 1)            # a camera accent never sits on the cut frame
    fb = f_target if cmd.get('exact') else _nearest_beat(e, f_target, lo, x['f1'])
    if mid == 'zoom.crash':
        cut_beat = _nearest_beat(e, f_target)
        prev_i = next((i for i, y in enumerate(segs) if y['f0'] == cut_beat), None)
        if prev_i and abs(cut_beat - f_target) <= abs(fb - f_target) and segs[prev_i - 1]['f1'] - segs[prev_i - 1]['f0'] + 1 >= int(0.4 * fps):
            si, x = prev_i - 1, segs[prev_i - 1]                          # "cut on the landing": lands on the cut
            fb = x['f1']
        elif fb - x['f0'] < int(0.4 * fps):                               # needs a 0.4 s run-up inside the clip
            later = [f for f in _beat_frames(e) if x['f0'] + int(0.4 * fps) <= f <= x['f1']]
            fb = later[0] if later else x['f1']
    fb = min(max(fb, x['f0']), x['f1'])
    k = fb - x['f0']
    center = (x.get('crop') or {}).get('center') or [0.5, 0.45]
    kind, d = _move_fx(mid, fps, center, period, k, cmd.get('params'))
    if kind == 'layer':
        text = cmd.get('text')
        if not text:
            raise ValueError(f'{mid}: needs "text"')
        dur = float(cmd.get('dur', 1.9))
        L = dict(kind=d['kind'], f0=fb, f1=min(e['n_frames'] - 1, fb + int(round(dur * fps)) - 1), text=text,
                 lines=[dict(role='title', text=text)], words=[dict(w=text, t0=round(fb / fps, 4), t1=round(fb / fps + dur, 4))],
                 pos=cmd.get('pos', [0.47, 0.45]), size=cmd.get('size', 0.05), color=cmd.get('color', '#FFFFFF'),
                 anim_in=dict(kind='fade', dur=0.3), anim_out=dict(kind='fade', dur=0.3), safe_zone='tiktok', move=mid,
                 why='point edit')
        e.setdefault('layers', []).append(L)
        res['changed'].append(f'layer {mid} "{text}" {tcode(fb / fps)}–{tcode((L["f1"] + 1) / fps)}')
        return _finish(e, res)
    if kind == 'crop':
        if 'rot' in d:
            th = float(d['rot'])
            S = math.cos(math.radians(abs(th))) + 0.5625 * math.sin(math.radians(abs(th)))
            x['crop']['rot'] = th
            _crop_cover(x, S)
        else:
            _crop_zoom(x, d['z0'], d['z1'], d['ease'])
        res['changed'].append(f'{x["id"]}: {mid} (crop)')
    elif kind == 'op':
        curve = d.pop('curve')
        d.update(f=f'{fb}:{min(e["n_frames"] - 1, fb + len(curve) - 1)}', curve=curve, move=mid, stage='pre')
        e['ops'].append(d)
        res['changed'].append(f'{mid} at frame {fb} ({tcode(fb / fps)})')
    else:
        d = _to_events(d, x['f0'], fps)
        if mid == 'zoom.crash':      # the crash owns its landing beat: no punch / shake on the same frame
            tl = round(fb / fps, 4)
            x['fx'] = [y for y in x.get('fx', []) if not (y['type'] in ('zoom.punch', 'shake.beat') and
                                                           any(abs(t - tl) < 0.5 / fps for t in y.get('times', [])))]
        x.setdefault('fx', []).append(d)
        res['changed'].append(f'{x["id"]}: {mid} at k={k} (frame {fb}, {tcode(fb / fps)})')
        if mid == 'zoom.crash':
            e['audio']['sfx'].append(dict(kind='whoosh', variant='air', at=round(fb / fps, 4), align='peak', dur=0.7, level='normal',
                                          seed=900 + fb, move='sfx.whoosh', why='whoosh under the crash zoom (point edit)'))
    return _finish(e, res)


def _op_f0(o):
    f = o.get('f')
    if isinstance(f, int):
        return f
    if isinstance(f, str):
        return int(f.split(':')[0])
    return int(f[0]) if f else 0


def _swap(e, si, cmd, res):
    if si is None:
        raise ValueError('swap needs "clip" or "at"')
    s = e['segments'][si]
    fps = e['canvas']['fps']
    w = cmd.get('with', 'next')
    meta_slot = e['meta']['slots'][si] if si < len(e['meta'].get('slots', [])) else {}
    if w == 'next':
        alts = meta_slot.get('alts') or []
        if not alts:
            raise ValueError(f'{s["id"]}: no alternatives stored; pass {{"src", "t"}}')
        a = alts.pop(0)
        idx = json.load(open(e['meta']['footage']['index'])) if e['meta']['footage'].get('index') else None
        shot = next((x for x in (idx or {}).get('shots', []) if x['id'] == a['shot']), None)
        src_name = a['shot'].split('#')[0]
        path = next(c['path'] for c in e['meta']['footage']['clips'] if c['name'] == src_name)
        w = dict(src=src_name, t=a['w0'], path=path)
    elif isinstance(w, dict) and 'shot' in w:
        src_name = w['shot'].split('#')[0]
        idx = json.load(open(e['meta']['footage']['index']))
        shot = next(x for x in idx['shots'] if x['id'] == w['shot'])
        path = next(c['path'] for c in e['meta']['footage']['clips'] if c['name'] == src_name)
        w = dict(src=src_name, t=shot['t0'] + 0.15, path=path)
    src = w['src']
    if src not in e['sources']:
        clip = next((c for c in (e['meta'].get('footage') or {}).get('clips', []) if c['name'] == src), {})
        path = w.get('path') or clip.get('path')
        if not path:
            raise ValueError(f'unknown source {src}')
        e['sources'][src] = dict(path=path)
        bx = clip.get('box')
        if bx and bx != [0, 0, clip.get('w'), clip.get('h')]:
            e['sources'][src]['box'] = bx
    dt = float(w['t']) - s['t']
    s['src'] = src
    s['t'] = round(float(w['t']), 4)
    if 'times' in s:
        s['times'] = [round(x + dt, 4) for x in s['times']]
    cr = s.get('crop') or {}
    if cr.get('path'):
        # new subject path for the new footage (ed_reframe works on the full frame; the crop is box-relative)
        n = s['f1'] - s['f0'] + 1
        times = np.asarray(s['times'], float) if s.get('times') else s['t'] + np.arange(n) / fps * float(s.get('speed', 1.0))
        try:
            info = V.probe(e['sources'][src]['path'])
            W0, H0 = info['w'], info['h']
            bx = e['sources'][src].get('box') or [0, 0, W0, H0]
            t0, t1 = float(times.min()), float(times.max())
            rf = RF.crop_path(e['sources'][src]['path'], t0, max(t1 - t0, 0.2),
                              out_aspect=e['canvas']['w'] / e['canvas']['h'])
            kt = [k[0] for k in rf['keys']]
            cx = np.clip((np.interp(times - t0, kt, [k[1] for k in rf['keys']]) * W0 - bx[0]) / (bx[2] - bx[0]), 0, 1)
            cy = np.clip((np.interp(times - t0, kt, [k[2] for k in rf['keys']]) * H0 - bx[1]) / (bx[3] - bx[1]), 0, 1)
            zk = [p[0] for p in cr['path']]
            zv = [p[3] for p in cr['path']]
            cr['path'] = [[int(k), round(float(cx[k]), 4), round(float(cy[k]), 4), round(float(np.interp(k, zk, zv)), 4)]
                          for k in sorted(set(list(range(0, n, 3)) + [n - 1]))]
            cr['cx'], cr['cy'], cr['subject'] = cr['path'][0][1], cr['path'][0][2], rf['subject']
        except Exception as ex:                   # keep a centred crop if the new source cannot be analysed
            cr['path'] = [[p[0], 0.5, 0.5, p[3]] for p in cr['path']]
            cr['cx'], cr['cy'], cr['subject'] = 0.5, 0.5, f'center ({ex})'
    if si < len(e['meta'].get('slots', [])):
        e['meta']['slots'][si].update(src=src, src_t=[s['t'], None], shot=w.get('shot', src), why=f'replaced by command: {cmd}')
    res['changed'].append(f'{s["id"]}: footage -> {src} @ {s["t"]:.2f}s')
    return res


def _finish(e, res):
    m = e['meta']
    m['version'] = int(m.get('version', 1)) + 1
    m.setdefault('history', []).append(dict(at=time.strftime('%Y-%m-%dT%H:%M:%S'), cmd=res['cmd'], changed=res['changed']))
    cnt = {}
    for s in e['segments']:
        for fx in s.get('fx', []):
            mm = fx.get('move', fx['type'])
            cnt[mm] = cnt.get(mm, 0) + 1
        if s.get('transition_in'):
            mm = s['transition_in'].get('move', s['transition_in']['kind'])
            cnt[mm] = cnt.get(mm, 0) + 1
    m['moves_now'] = dict(sorted(cnt.items()))
    return e


# ============================================================================ CLI
def _explain_composite(edl):
    """The composite's per-part shot table: # / time / length / part / shot (source @ in-point) / moves / why."""
    fps = edl['canvas']['fps']
    m = edl['meta']
    seq_parts = (m.get('sequence') or {}).get('parts') or {}
    out = [f"composite ({m.get('scenario')}) · {edl['n_frames']} frames · {len(edl['segments'])} segments"]
    part_of = {}
    for pm in _comp_parts(edl):
        for sid in pm.get('segments') or []:
            part_of[sid] = pm.get('id')
    tc = lambda f: f'{int(f / fps // 60)}:{f / fps % 60:05.2f}'      # noqa: E731
    for pm in _comp_parts(edl):
        pid = pm.get('id')
        secs = ', '.join(f'{n} {_section_range(pm, n)}' for n in PARTS if _section_range(pm, n)) if pm.get('type') == 'edit' else ''
        sp = seq_parts.get(pid) or {}
        extra = []
        if pm.get('type') == 'edit':
            extra.append(' '.join(str(x) for x in (pm.get('genre'), pm.get('style'), f"v{pm.get('variant') or 0}") if x))
        elif sp.get('keep'):
            extra.append('source ' + ', '.join(f'{a:.2f}–{b:.2f} s' for a, b in sp['keep']))
        out.append(f"\n{pid} ({pm.get('type')}) frames {pm.get('f0')}–{pm.get('f1')} · {tc(pm.get('f0', 0))}–{tc(pm.get('f1', 0) + 1)}"
                   + (f" · {secs}" if secs else '') + (f" · {'; '.join(extra)}" if extra else ''))
        out.append(f"{'#':>3} {'time':8s} {'len':>6s}  {'shot':34s} {'moves':38s} why")
        ramps = {r[0]: r[1] for r in ((sp.get('choices') or {}).get('ramps') or []) if isinstance(r, list) and len(r) > 1
                 and isinstance(r[1], str)}
        k = 0
        for n_, sg in enumerate(edl['segments']):
            if part_of.get(sg['id'], (_comp_part_at(edl, sg['f0']) or {}).get('id')) != pid:
                continue
            mv = []
            tr = sg.get('transition_in') or {}
            if tr:
                mv.append(tr.get('move') or f"trans.{tr.get('kind')}")
            if sg.get('times') or sg.get('speed_curve'):
                mv.append('ramp: ' + ramps[k] if k in ramps else 'speed curve')
            elif sg.get('speed') not in (None, 1.0, 1):
                mv.append(f"x{sg['speed']}")
            looks = sorted({fx.get('look') for fx in sg.get('fx', []) if fx.get('look')})
            mv += sorted({fx.get('move') or fx.get('type') for fx in sg.get('fx', []) if not fx.get('look')})
            mv += [f'look {x}' for x in looks]
            shot = f"{sg.get('src')} @{float(sg.get('t', 0.0)):.2f}"
            out.append(f"{n_ + 1:>3} {tc(sg['f0']):8s} {(sg['f1'] - sg['f0'] + 1) / fps:5.2f}s  {shot[:34]:34s} "
                       f"{', '.join(mv) or '—':38s} {sg.get('note') or ''}")
            k += 1
    if m.get('notes'):
        out.append('\nnotes: ' + ' · '.join(str(x) for x in m['notes'][:12]))
    return '\n'.join(out)


def explain(edl):
    fps = edl['canvas']['fps']
    m = edl['meta']
    if _comp_parts(edl) is not None:                    # composite (ed_sequence): parts, then the shot table
        return _explain_composite(edl)
    if m.get('kind') == 'speech':
        src = m.get('source') or {}
        rm = src.get('removed') or {}
        out = [f"{m['genre']} ({m['genre_name']}, cut by words) · source {src.get('name')} {src.get('range', [0, 0])[0]:.2f}–"
               f"{src.get('range', [0, 0])[1]:.2f} s ({src.get('why')}) · {edl['n_frames']} frames · removed {rm.get('removed_s', 0)} s of "
               f"pauses / fillers · {src.get('words')} words"]
    else:
        out = [f"{m['genre']} ({m['genre_name']}) · {m['track']['bpm']} BPM · window {m['track']['window'][0]:.2f}–{m['track']['window'][1]:.2f} s · "
               f"{edl['n_frames']} frames · {m['track']['reason']}"]
    out.append('parts: ' + ', '.join(f"{k} {v['t'][0]:.1f}–{v['t'][1]:.1f}" for k, v in m['parts'].items()))
    for s in m['slots']:
        mv = ', '.join(sorted({x['id'] for x in s.get('moves', [])}))
        out.append(f"{s['id']} {s['tc']} {s['t'][1] - s['t'][0]:4.2f}s {s['part']:5s} {s['role'] or '':10s} cut={s['cut']:8s} "
                   f"{s['speed'] or '':11s} {s['shot'] or s['src']:22s} | {mv} | {s['why']}")
    if m.get('skipped'):
        out.append('not placed: ' + '; '.join(f"{x['move']} ({x.get('part') or '—'}): {x['reason']}" for x in m['skipped'][:30]))
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='command')         # not 'cmd': the apply subcommand has a positional 'cmd'
    p = sub.add_parser('plan')
    p.add_argument('--track', help='music (speech genres: optional bed)')
    p.add_argument('--footage', nargs='+', required=True)
    p.add_argument('--genre', help='genre card (optional with --style: the style names its genre)')
    p.add_argument('--style', help='house style: a preset name or plain words ("clean and expensive")')
    p.add_argument('--variant', type=int, help='version of the style (0 = as written; another number = another version)')
    p.add_argument('--avoid', nargs='+', help='earlier versions (EDL files) whose choices this one steers away from')
    p.add_argument('--out', required=True)
    p.add_argument('--dur', type=float)
    p.add_argument('--fps', type=int, default=30)
    p.add_argument('--canvas', default='1080x1920')
    p.add_argument('--cache')
    p.add_argument('--seed', type=int, default=1)
    p.add_argument('--title')
    p.add_argument('--word')
    p.add_argument('--outro-text')
    p.add_argument('--no-reframe', action='store_true')
    p.add_argument('--sample-fps', type=float, default=6.0)
    p.add_argument('--n-shots', type=int, help='exact number of shots')
    p.add_argument('--order', choices=ORDERS, default='auto', help='given: shot i = footage file i')
    p.add_argument('--require', help='moves that must appear, comma-separated (ids or families)')
    p.add_argument('--forbid', help='moves that must not appear, comma-separated (ids or families)')
    p.add_argument('--music-in', help='track second shown at output 0 (start offset)')
    p.add_argument('--drop-at', help='output second where the drop lands')
    p.add_argument('--drop-t', help='track second of the drop (overrides the detector)')
    p.add_argument('--bpm', type=float, help='tempo hint')
    p.add_argument('--bars', type=int, help='length in whole bars')
    p.add_argument('--cut-rate', type=float, help='x the genre card cutting rate (default 1, or the style pacing)')
    p.add_argument('--sfx-level', choices=SFX_LEVELS, help='default genre (or the style level)')
    p.add_argument('--words', help='speech genres: transcript JSON (ed_voice format) instead of recognising the voice')
    p.add_argument('--lang')
    p.add_argument('--voice', help='motivation: voice-over file')
    p.add_argument('--src-in')
    p.add_argument('--src-out')
    p.add_argument('--from', dest='from_phrase')
    p.add_argument('--to', dest='to_phrase')
    p.add_argument('--subtitles', choices=['karaoke', 'subtitle', 'none'])
    sb = sub.add_parser('storyboard', help='a whole video to generate: every slot a gap with an edit-gen brief')
    sb.add_argument('--track', required=True)
    sb.add_argument('--genre')
    sb.add_argument('--style')
    sb.add_argument('--variant', type=int)
    sb.add_argument('--brief', help='what the video is about (the subject of every shot)')
    sb.add_argument('--character', help='one character kept identical in every shot')
    sb.add_argument('--dur', type=float)
    sb.add_argument('--n-shots', type=int)
    sb.add_argument('--fps', type=int, default=30)
    sb.add_argument('--canvas', default='1080x1920')
    sb.add_argument('--cache')
    sb.add_argument('--out', required=True)
    fl = sub.add_parser('fill', help='plug clips into storyboard / gap slots')
    fl.add_argument('edl')
    fl.add_argument('map', help='JSON file or inline JSON {slot id: path | {"path", "t"}}')
    fl.add_argument('--cache')
    fl.add_argument('--out')
    st_ = sub.add_parser('styles', help='list the house styles, or resolve plain words to one')
    st_.add_argument('words', nargs='*')
    q = sub.add_parser('apply')
    q.add_argument('edl')
    q.add_argument('cmd', help='JSON file or inline JSON')
    q.add_argument('--out')
    v = sub.add_parser('validate')
    v.add_argument('edl')
    x = sub.add_parser('explain')
    x.add_argument('edl')
    r = sub.add_parser('remake')
    r.add_argument('--ref', required=True)
    r.add_argument('--src', required=True)
    r.add_argument('--track')
    r.add_argument('--out', required=True)
    r.add_argument('--canvas', default='1080x1920')
    r.add_argument('--fps', type=int, default=30)
    r.add_argument('--max-zoom', type=float, default=2.6)
    a = ap.parse_args()
    if a.command == 'plan':
        w, h = map(int, a.canvas.lower().split('x'))
        cache = a.cache or os.path.join(os.path.dirname(os.path.abspath(a.out)), '.ed_cache')
        extra = {k: v for k, v in dict(n_shots=a.n_shots, order=a.order, require_moves=a.require, forbid_moves=a.forbid,
                                       music_in=a.music_in, drop_at=a.drop_at, drop_t=a.drop_t, bpm=a.bpm, bars=a.bars,
                                       cut_rate=a.cut_rate, sfx_level=a.sfx_level, words=a.words, lang=a.lang, voice=a.voice,
                                       src_in=a.src_in, src_out=a.src_out, subtitles=a.subtitles, style=a.style,
                                       variant=a.variant, avoid=a.avoid,
                                       **{'from': a.from_phrase, 'to': a.to_phrase}).items() if v is not None}
        if not a.genre and not a.style:
            raise SystemExit('--genre or --style is required')
        gname = a.genre or resolve_style(a.style)['genre']
        if not a.track and genre_kind(load_genre(gname).get('kind')) != 'speech':
            raise SystemExit('--track is required for music genres')
        edl = plan_genre(a.track, a.footage, a.genre, (w, h), a.fps, a.dur, cache_dir=cache, seed=a.seed, title=a.title, word=a.word,
                         outro_text=a.outro_text, reframe=not a.no_reframe, sample_fps=a.sample_fps, **extra)
        _dump_atomic(edl, a.out, indent=1)
        errs, warns = validate_edl(edl)
        print(explain(edl))
        print('validate:', 'OK' if not errs else errs, ('warnings: ' + '; '.join(warns)) if warns else '')
    elif a.command == 'storyboard':
        w, h = map(int, a.canvas.lower().split('x'))
        cache = a.cache or os.path.join(os.path.dirname(os.path.abspath(a.out)), '.ed_cache')
        edl = plan_storyboard(a.track, genre=a.genre, style=a.style, dur=a.dur, brief=a.brief, canvas=(w, h), fps=a.fps,
                              n_shots=a.n_shots, character=a.character, cache_dir=cache,
                              **({'variant': a.variant} if a.variant is not None else {}))
        _dump_atomic(edl, a.out, indent=1)
        for gp in edl['meta']['gaps']:
            print(f"{gp['id']} {gp['t'][0]:6.2f}-{gp['t'][1]:6.2f}s {gp['brief']['shot_size']}: {gp['brief']['prompt']}")
        errs, _ = validate_edl(edl)
        print('validate:', 'OK' if not errs else errs)
    elif a.command == 'fill':
        edl = _load_json(a.edl)
        mp = json.loads(a.map) if a.map.strip().startswith('{') else _load_json(a.map)
        out = fill_gaps(edl, mp, cache_dir=a.cache)
        _dump_atomic(out, a.out or a.edl, indent=1)
        print(json.dumps(out['meta']['history'][-1], ensure_ascii=False))
        errs, _ = validate_edl(out)
        print('validate:', 'OK' if not errs else errs)
    elif a.command == 'styles':
        if a.words:
            res = resolve_style(' '.join(a.words))
            if not res.get('matched', True):
                print(res['why'], file=sys.stderr)
            print(json.dumps(res, ensure_ascii=False))
        else:
            for name, st in STYLE_PRESETS.items():
                rot = ' | '.join(f"{n or 'natural'}{'' if not n or i == 1.0 else f' {i:g}'}" for n, i in look_rotation(st))
                print(f"{name:15s} {st['genre']:10s} looks: {rot}\n{'':26s} {st['description']}")
    elif a.command == 'apply':
        edl = json.load(open(a.edl))
        cmd = json.loads(a.cmd) if a.cmd.strip().startswith('{') else json.load(open(a.cmd))
        out = apply_command(edl, cmd)
        _dump_atomic(out, a.out or a.edl, indent=1)
        print(json.dumps(out['meta']['history'][-1], ensure_ascii=False))
    elif a.command == 'validate':
        errs, warns = validate_edl(json.load(open(a.edl)))
        print('OK' if not errs else '\n'.join(errs))
        for w_ in warns:
            print('warning:', w_)
        sys.exit(1 if errs else 0)
    elif a.command == 'explain':
        print(explain(json.load(open(a.edl))))
    elif a.command == 'remake':
        ref = json.load(open(a.ref))
        src = json.load(open(a.src))
        w, h = map(int, a.canvas.split('x'))
        tl = plan_remake(ref, src, a.track, (w, h), a.fps, a.max_zoom)
        _dump_atomic(tl, a.out, indent=1)
        print('clips', len(tl['clips']), 'mapping', tl['mapping']['mode'])
    else:
        ap.print_help()


if __name__ == '__main__':
    main()
