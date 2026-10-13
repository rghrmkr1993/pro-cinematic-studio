#!/usr/bin/env python3
"""ed_sequence - composite edits: several PARTS in a row on one canvas with one soundtrack, planned from a small
JSON spec into a normal EDL (engine/TIMELINE.md) that ed_edl renders and ed_qa checks like any other project.

Typical request: "a clip of the interview from where she names the number up to his reaction, then a short edit of
my five shots with speed ramps on the drop of the track; vertical; only the people (it's a screen recording)" ->
one talk part (exact in / out by spoken words, vertical speaker crops that keep the player UI, logos and captions
out, subtitles, a music bed under it) + one edit part (one shot per bar from the drop, speed ramps, SFX), joined by a
flash on the strongest downbeat of the track.

CLI
  python3 -I ed_sequence.py plan SPEC.json --out edl_v1.json [--cache DIR] [--quiet]
  python3 -I ed_sequence.py resolve SPEC.json [--cache DIR]     # where the phrases land + the drop, no video work
  python3 -I ed_sequence.py variant edl_v1.json --out edl_v2.json [--variant N] [--style WORDS]   # another version
  python3 -I ed_sequence.py example                             # prints the commented example spec below
  (exit code 3 when the planned EDL fails ed_edl.validate / ed_plan.validate_edl - errors listed)
Then:  python3 -I ed_edl.py edl_v1.json preview_v1.mp4 --preview --labels ;  python3 -I ed_qa.py edl_v1.json
       preview_v1.mp4 qa_v1/   (or edit.py: edl_vN.json / preview_vN.mp4 / qa_vN/ in the project folder)

API
  plan_sequence(spec, cache_dir=None, log=print) -> EDL dict (+ meta.parts, meta.sequence, meta.validation)
  variant(edl | path, variant=None, style=None, cache_dir=None, log=print) -> EDL   another version: re-plans the
        stored spec (meta.sequence.spec) with the next unused variant, avoiding the given version(s)
  style_info(style, variant=None) -> {"name", "genre", "caption_style", "transitions", "why"} | None
  load_spec(path) -> dict          JSON or JSON with // and # comments (the `example` output loads as is)
  resolve(spec, cache_dir=None, log=print) -> {"parts": [...], "music": {...}}   talk/clip ranges + drop, cheap
  find_phrase(words, text, after=None, before=None) -> {"t0","t1","i0","i1","score","text"} | None
        (ed_voice.find_phrase when available, else the local fuzzy matcher: case / punctuation / number format
        insensitive, "3 million" = "3,000,000" = "three million", "Korvanta" = "Kor vanta")
  reaction_end(media, t, words, max_s=4.0) -> float   (ed_voice.reaction_end when available, else local)
  ramp_curve(n, fps, beats_k, profile, fast, slow, src_fps, brake_beat) -> speed-ramped shot (ed_fx.speed_ramp)
  pace_chunks(layers, fps, hard=(), f_end=None) -> [notes]   reading time for subtitle chunks of fast speech
  estimate_av_offset(video, t0, t1, cache_dir=None) -> {"offset", "measured", "lag", "r", "confident", "why"}
        lip sync of any file (a source or a render): how much the audio lags the picture (mouth motion vs the
        speech envelope); offset = lag - the natural 0.08 s lead when confident and >= 2 frames, else 0
  clean_starts(words) -> [word index]   starts of clean sentences (a fragment cut off by the recording is skipped)

SPEC (JSON; seconds are source seconds unless a key says otherwise; paths relative to the spec file)
  canvas      {"w": 1080, "h": 1920, "fps": 30}
  parts       ordered list; every part has "type" (talk | edit | clip) and "id" (default type + index)
  music       {"path", "drop_at": {"part": ID, "at": "start" | "end" | seconds into the part} (or just the part ID),
               "drop": track seconds (default: the strongest downbeat - start of the most energetic section, a
               detected drop, the loudness / low-end jump - that leaves enough track for the parts after it; a
               track with no detected drop: the biggest bass / loudness rise on a downbeat into music as energetic
               as the edit needs, with a note for the user that names it and suggests another section or track),
               "in": track seconds at output 0 (overrides the alignment), "gain_db": 0, "fade_in": 0.6, "fade_out"}.
               Without drop_at the drop lands on the first frame of the first edit part (exactly: music.in =
               drop - that frame's time; when the parts before it are longer than the track before its drop, the
               music starts later, music.at > 0).
  transitions [{"from": ID, "to": ID, "kind": "cut" | "flash" | <ed_edl transition kind: dissolve dip fade whip zoom
               spin wipe luma lens glitch pixel_sort light_leak liquid push slide>, "frames": 4,
               "sfx": "auto" | "none" | kind | [kinds]}]   default between a talk/clip part and an edit part:
               flash + auto sfx (riser into the cut, impact + sub drop on it); otherwise a plain cut. A part that
               starts on the music drop always gets its level's drop package (genre / heavy: riser ending a 1/16 note
               before the drop in epic, impact + sub drop on it) - minus every kind the part already places on its
               own first frame (a planner part opens with its drop hit: no second impact); duplicates merge. The
               riser / impact / sub flavour rotates with the next part's variant.
  sfx         default SFX level for every part: none | light | genre | heavy (default genre; the planner's words
              normal / strong are the same as genre / heavy)
  sfx_dir     a folder of the user's sound effects (relative to the spec) -> audio.sfx_dir: every SFX event takes the
              best-named file there for its kind / flavour (ed_sfx.pick_sample), else it is synthesized
  loudness    {"lufs": -14, "tp": -1}        subtitles: default subtitle settings for talk parts (see below)
  end         {"fade": s}  fade to black at the very end. Default 0.27 s when the last part is an edit; a genre outro
               fade of the planner is kept on long parts and shortened to <= 0.5 s on parts <= 12 s; the music fades
               with the picture.
  qa          extra keys for the EDL's qa block (override the computed ones)
  style       house style for every part (ed_plan.STYLE_PRESETS name or plain words: "clean and expensive"): the edit
              parts' planner style (genre defaults to the style's), the talk parts' caption preset, the default
              talk -> edit transition from the style's palette
  variant     version number (int, default 0): re-seeds the choices inside the rules - planner moves / transitions /
              shot windows / grade nuance, recipe brake pattern / action peak / whoosh / punch size, talk punch-in
              placement, caption sibling preset - so "another version" never repeats; the cut points and the drop stay
  avoid       earlier versions (EDL paths or dicts) whose recorded choices (meta.choices) the new one steers away
              from; style / variant / avoid may also sit on a single part (the part's key wins) - except that a
              talk / clip part's own "avoid" stays its overlay boxes (earlier versions there: "avoid_versions")

  talk part   {"type": "talk", "id", "source": video, "transcript": words.json (optional; else a transcript of this
               file in ed_voice's cache, else ed_voice.transcribe with lang + vocab as the prompt), "lang": "en",
               "vocab": ["Korvanta"] (names the recogniser splits; joined for matching and subtitles),
               "from": seconds | "0:24.05" | {"phrase": "...", "occurrence": 1, "snap": "pause" | "word" | "sentence",
                                              "pad": 0.0} | {"auto": true, "max_s": 25} | missing (the first clean
               sentence - not a fragment cut off by the recording, not one whose picture is hidden by a pop-up or
               shows no face; a source over 90 s or "auto": the best setup sentence at most max_s before the end,
               ed_voice.setup_starts when it exists),
               "to": seconds | {"phrase": "...", "end": "phrase" | "after_reaction" | "sentence", "max_s": 4, "pad"},
               "remove": [{"phrase": "..."} | "phrase" | {"from": .., "to": ..} | [t0, t1], ...],
               "tighten_pauses": null | seconds (longer pauses are shortened to this; the reaction is kept; recorded
               in meta.parts so the QA judges the pauses left inside shots),
               "crop": "speaker" | "center" | {"cx", "cy", "z"}, "box": [x0, y0, x1, y1] (live picture inside a
               screen recording; default detected), "avoid": [[x0, y0, x1, y1], ...] (default: detected logos,
               lower thirds, watermarks, UI; a transient pop-up only while it is on screen), "max_zoom": 1.45,
               "push": true (slow push-in on the punchline and the reaction), "punch_ins": true | seconds (motivated
               zoom cuts inside camera shots longer than 4 s: numbers, sentence starts, the punchline - the
               punchline, else a number, always on the tight framing;
               x <= 1.12 about the face, the tighter window stays inside the overlay-free one), "av_offset": seconds
               the source's audio lags its picture - the picture is taken that much earlier (default: measured -
               estimate_av_offset - and corrected when confident and >= 2 output frames; 0 = keep as recorded;
               recorded in meta.parts[i].av_offset / lip_sync; scans do not depend on it, no re-analysis),
               "subtitles": "subtitle" | "karaoke" | <ed_text caption preset, e.g. "podcast_caps"> | null |
                            {"kind", "style", "pos", "max_chars", "max_lines", "max_words", "pace": true}
                            (default: the house style's caption preset, else "podcast_bold"; ed_voice.subtitle_chunks
                            gets the preset as `style` (it sets kind and line limits for the canvas) and every jump
                            - removed text, camera cut, the part's ends - as `breaks`, so chunks are planned
                            around them and keep their reading time; pace_chunks only re-times what would still
                            fail the QA (> 20 chars/s or < 0.7 s on screen)),
               "audio": "voice" | "mute", "music_db": -18 (bed level under this part; ducked under the voice),
               "swell": {"s": 0.6, "to_db": music_db / 2} | false (the bed rises into a following edit part and is
               back to full level exactly on its first frame), "grade": {...}}
               Cut points sit in the quiet part of the pause next to the word, never past the energy onset of the
               next word (ASR times can be 0.1-0.3 s off); a phrase that starts / ends inside connected speech moves
               the point to the previous / next pause (<= 1.5 s); removals cut on the word boundary when there is no
               pause and keep the joined pause short (<= ~0.35 s). "after_reaction" keeps the non-verbal or one-word
               reaction after the phrase (sigh, face-palm, "Wow.") and ends just before the next sentence.
               Camera cuts inside the kept ranges become segment boundaries on the exact source frame; every camera
               shot gets its own vertical crop: ed_reframe.speaker_crop when it exists (its boundaries are snapped
               to the frame-exact cuts of the local scan, and any window over a logo / caption / small overlay is
               replaced by the local solver's), else the local solver - active speaker by mouth-motion / speech-
               envelope correlation at the source's audio lag, face box from the track's median, the smallest
               zoom that frames the face whole with head room and keeps every avoid box out (relaxing margins
               before overlays). No piece under 0.5 s at the edge of a kept range (the offset moves the picture
               against the source's cuts): the in / out point moves onto the camera cut when no word is spoken
               there, else that sliver holds the neighbouring shot's frame (qa.planned_freeze). The source's own
               camera cuts go to qa.source_cuts (not judged against the words). Captions: jump cuts and the part's
               ends are hard breaks, camera cuts soft ones (subtitle_chunks(soft_breaks=..) when it has them, else
               a camera-cut break that would squeeze a chunk under 0.7 s or over 20 chars/s is dropped).
  edit part   {"type": "edit", "id", "footage": [videos or globs], "order": "given" | "auto", "genre": "epic",
               "bars": 5, "shots": 5, "moves": ["time.speed_ramp"], "forbid": [...], "sfx": level,
               "engine": "auto" | "planner" | "recipe", "ramp": {"fast": 2.5, "slow": 0.4}, "grade": {...},
               "seed": 1}
               engine auto: ed_plan.plan_genre(n_shots, order, require_moves, forbid_moves, music_in, drop_at,
               drop_t, bars, sfx_level, in_sequence, style, variant, avoid) - used only when its result has the
               requested frames, shot count, shot order, music in-point and visible required moves - else the
               local recipe: one shot per bar (or shots spread over the beats) on the downbeats in the given order,
               speed ramps from ed_fx.speed_ramp anchored on each clip's action peak (move card time.speed_ramp:
               first shot slow out of the drop -> fast exit, middle shots fast -> brake on a beat -> slow -> fast
               into the cut, the last shot ends slow; slow 0.4 from < 45 fps sources), a hold punch-in x1.08-1.1
               at every brake (on the face; into the middle of a detail / body shot), subject-following 9:16 crop,
               the genre grade + per-shot exposure match,
               motion blur on fast frames, heavy shake on the drop, whooshes on the cuts, soft hits on the brakes
               (heavy). Its sections (drop = up to the last shot, outro = the last shot) go to meta.parts.
  clip part   {"type": "clip", "id", "source", "from", "to" (seconds or phrases, as talk), "crop": "auto" (as
               "speaker") | "center" | {...}, "audio": "voice" | "mute", "speed": 1.0, "subtitles": null,
               "music_db", "punch_ins": false}

OUTPUT: a normal EDL; segment ids T01.. (talk), E01.. (edit), K01.. (clip), every segment carries "part" and a
  "note" with the reason (speaker pick, punch-in word, push-in); sources named after the part ("talk", "hype_...");
  talk segments interp "nearest" (exact source frames); audio.voice = one entry per kept range (ed_sfx gives clips
  of one file one common gain and click-free fades at the joins; with an older mixer that normalises clips alone,
  gain_db carries the clip's loudness minus the group's); audio.music_fx = the bed level under talk parts + swell;
  audio.sfx from transitions and edit parts (with "level"), audio.sfx_dir from the spec; audio.grid = beats /
  downbeats in output time;
  layers = subtitles; qa = speech mode (qa.words, on_word_share, source_cuts) when there is a talk part,
  planned_freeze = held slivers, on_beat_share = 0.9 x
  the share of cuts that sit in edit parts, qa.safe_zone = the vertical-video text-safe box (title_safe on a
  landscape canvas), qa.parts = per-part checks, planned_white / planned_black from the
  flash and the fades; meta.parts = [{"id", "type", "f0", "f1", "t0", "t1", "segments", (talk/clip: "source",
  "keep"), (edit: "genre", "bars", "shots", "engine", "sfx", "drop_frame", "sections": {"hook" | "build" | "drop" |
  "outro": [f0, f1]} (absolute frames: point edits "on the drop" resolve with ed_plan.part_range), "style",
  "variant"), (talk/clip with tighten_pauses: "tighten_pauses")}]; meta.style / meta.variant / meta.choices (the
  edit part's picks + the sequence's transitions and talk punch-ins, for the next version's avoid);
  meta.sequence = music (drop, in, why, candidates), transitions and per-part decisions (ranges, removals,
  reaction, box, overlays, crops, choices) + "spec" (the input spec, for variant()); meta.validation = {"errors",
  "warnings"} of ed_edl.validate + ed_plan.validate_edl; meta.notes.
  Caches (scans, music, clip profiles): cache_dir, default ~/.cache/edit-studio/sequence.

EXAMPLE (a typical composite request; `python3 -I ed_sequence.py example` prints it with comments)
  {"canvas": {"w": 1080, "h": 1920, "fps": 30},
   "parts": [
     {"type": "talk", "id": "talk", "source": "interview.mp4", "lang": "en", "vocab": ["Korvanta"],
      "from": {"phrase": "the real question is"},
      "to": {"phrase": "three million a year", "end": "after_reaction"},
      "remove": [{"phrase": "Let me check my notes."}],
      "tighten_pauses": null, "crop": "speaker", "subtitles": "subtitle", "music_db": -18},
     {"type": "edit", "id": "hype", "footage": ["g1.mp4", "g2.mp4", "g3.mp4", "g4.mp4", "g5.mp4"],
      "order": "given", "genre": "epic", "bars": 5, "shots": 5, "moves": ["time.speed_ramp"], "sfx": "heavy"}],
   "music": {"path": "track.wav", "drop_at": {"part": "hype", "at": "start"}},
   "transitions": [{"from": "talk", "to": "hype", "kind": "flash", "sfx": "impact"}]}
"""
import os
import re
import sys
import json
import math
import copy
import glob
import time
import difflib
import hashlib
import argparse
import importlib
import subprocess
import unicodedata

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PLANNER = 'ed_sequence/1'
SCAN_VERSION = 4
PART_TYPES = ('talk', 'edit', 'clip')
SFX_LEVELS = ('none', 'light', 'genre', 'heavy')
SFX_LEVEL_ALIAS = {'normal': 'genre', 'medium': 'genre', 'default': 'genre', 'strong': 'heavy', 'max': 'heavy',
                   'off': 'none'}                          # the planner's level words (ed_plan.SFX_LEVEL_ALIAS)


def _sfx_level(v, what):
    lv = str(v).strip().lower()
    lv = SFX_LEVEL_ALIAS.get(lv, lv)
    if lv not in SFX_LEVELS:
        raise SpecError(f'{what} must be one of {SFX_LEVELS} (or {", ".join(sorted(SFX_LEVEL_ALIAS))}); got {v!r}')
    return lv
TRANSITION_KINDS = {'dissolve', 'dip', 'flash', 'fade', 'whip', 'zoom', 'spin', 'wipe', 'luma', 'lens', 'glitch',
                    'pixel_sort', 'light_leak', 'liquid', 'push', 'slide'}
DEFAULT_CACHE = os.path.join(os.environ.get('EDIT_STUDIO_CACHE') or os.path.join(os.environ.get('ED_ROOT', 'C:/Claude Code/cinema-studio/edit'), 'cache'), 'sequence')
# subtitles for talk parts: the clips/ugc cards (bold sans 4.4-4.6 % H, white, black outline ~10 % of the size,
# block centre x 0.47, y 0.62-0.78, <= 2 lines of ~18 characters)
SUB_STYLE = {'font': 'inter:800', 'size': 0.044, 'color': '#FFFFFF',
             'stroke': {'w': 0.11, 'color': '#000000'},
             'shadow': {'dx': 0.0, 'dy': 0.045, 'blur': 0.12, 'alpha': 0.55, 'color': '#000000'},
             'line_height': 1.12}
SUB_POS = {'x': 0.47, 'block': [0.63, 0.75]}
KARAOKE_HL = {'mode': 'color', 'active': '#FFE14A', 'keyword': {'pick': 'numbers', 'color': '#45F06B'}}
TALK_GRADE = {'preset': 'natural', 'contrast': 1.06, 'sat': 1.04}
EPIC_GRADE = dict(preset='teal', auto=0.7, contrast=1.2, sat=1.0, temp=0.0, tint=0.0,
                  split=[[0.05, 0.40, 0.45], [1.0, 0.82, 0.62], 0.12], black=0.02)


class SpecError(ValueError):
    """The spec cannot be planned (missing file, unknown part type, phrase not found ...)."""


# ============================================================================ small helpers
_MODS, _MOD_ERR = {}, {}


def _mod(name):
    """Engine module or None (owned by other agents; may be missing or half-written right now)."""
    if name not in _MODS:
        try:
            _MODS[name] = importlib.import_module(name)
        except Exception as e:  # noqa: BLE001 - any import problem means "use the fallback"
            _MODS[name] = None
            _MOD_ERR[name] = f'{type(e).__name__}: {e}'
    return _MODS[name]


def _fn(mod, name):
    m = _mod(mod)
    f = getattr(m, name, None) if m is not None else None
    return f if callable(f) else None


def _r(x, n=4):
    return None if x is None else round(float(x), n)


def _file_key(path, extra=''):
    st = os.stat(path)
    return hashlib.md5(f'{os.path.abspath(path)}|{st.st_size}|{int(st.st_mtime)}|{extra}'.encode()).hexdigest()[:16]


def _load_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _dump_json(obj, path):
    tmp = f'{path}.tmp{os.getpid()}'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, path)


def frame_at(t, fps):
    """Frame that shows a musical event at output time t (the cards' rule: floor(t*fps + 0.4))."""
    return int(math.floor(t * fps + 0.4))


def _ease(u, kind='linear'):
    u = min(1.0, max(0.0, float(u)))
    if kind == 'inCubic':
        return u ** 3
    if kind == 'outCubic':
        return 1 - (1 - u) ** 3
    if kind == 'inOutCubic':
        return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2
    if kind == 'inOutSine':
        return -(math.cos(math.pi * u) - 1) / 2
    return u


def _probe(path):
    V = _mod('ed_video')
    if V is not None:
        return V.probe(path)
    out = subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', path],
                         capture_output=True, check=True).stdout
    j = json.loads(out)
    v = next((s for s in j['streams'] if s['codec_type'] == 'video'), None)
    info = dict(path=path, duration=float(j['format'].get('duration', 0)),
                has_audio=any(s['codec_type'] == 'audio' for s in j['streams']))
    if v:
        num, den = (v.get('avg_frame_rate') or '0/1').split('/')
        info.update(w=int(v['width']), h=int(v['height']), fps=float(num) / float(den) if float(den) else 0.0)
    return info


# ============================================================================ spec
def _strip_comments(text):
    """JSON with // and # line comments (outside strings) and trailing commas -> JSON text."""
    out, i, n, in_str, esc = [], 0, len(text), False, False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == '#' or (c == '/' and i + 1 < n and text[i + 1] == '/'):
            while i < n and text[i] != '\n':
                i += 1
            continue
        out.append(c)
        i += 1
    return re.sub(r',(\s*[}\]])', r'\1', ''.join(out))


def load_spec(path):
    """Spec file (JSON, or JSON with // / # comments) -> dict with base_dir = the file's folder."""
    with open(path, encoding='utf-8') as f:
        text = f.read()
    try:
        spec = json.loads(text)
    except ValueError:
        spec = json.loads(_strip_comments(text))
    spec.setdefault('base_dir', os.path.dirname(os.path.abspath(path)))
    return spec


def _abspath(p, base):
    if p is None:
        return None
    p = os.path.expanduser(str(p))
    return p if os.path.isabs(p) else os.path.abspath(os.path.join(base or os.getcwd(), p))


def _expand_footage(items, base):
    out = []
    for it in items if isinstance(items, (list, tuple)) else [items]:
        p = _abspath(it, base)
        if any(ch in p for ch in '*?['):
            hits = sorted(glob.glob(p))
            if not hits:
                raise SpecError(f'footage pattern matches nothing: {it}')
            out += hits
        else:
            out.append(p)
    for p in out:
        if not os.path.exists(p):
            raise SpecError(f'file not found: {p}')
    return out


def _point(v, what):
    """A time point: seconds | "0:24.05" | {"t": s} | {"phrase": ...} | {"auto": true, "max_s": 25} (a start)."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return {'t': float(v)}
    if isinstance(v, str):
        s = v.strip()
        if re.fullmatch(r'\d+(?:[.,]\d+)?s?|\d+:\d+(?::\d+)?(?:[.,]\d+)?', s):
            t = 0.0
            for part in s.rstrip('s').replace(',', '.').split(':'):
                t = t * 60 + float(part)
            return {'t': t}
        return {'phrase': s}
    if isinstance(v, dict):
        d = dict(v)
        if d.get('t') is not None:
            d['t'] = float(d['t'])
        elif d.get('auto') and what.endswith('.from') and '.remove[' not in what:
            d['max_s'] = float(d.get('max_s', AUTO_MAX_S))
        elif not d.get('phrase'):
            raise SpecError(f'{what}: needs seconds, {{"t": s}} or {{"phrase": "..."}} (got {v!r})')
        return d
    raise SpecError(f'{what}: cannot read {v!r}')


def _style_genre(style):
    """Genre of a house style (ed_plan.resolve_style: plain words or a preset name), None when unknown."""
    if not style:
        return None
    f = _fn('ed_plan', 'resolve_style')
    if f is None:
        return None
    try:
        m = f(str(style))
        return m.get('genre') if m and m.get('name') else None
    except Exception:  # noqa: BLE001
        return None


def style_info(style, variant=None):
    """The house style a spec names -> {"name", "genre", "caption_style", "transitions", "why"} | None
    (caption style: the preset's, its sibling on odd variants like the planner does)."""
    Pl = _mod('ed_plan')
    if not style or Pl is None or not hasattr(Pl, 'resolve_style'):
        return None
    try:
        m = Pl.resolve_style(str(style))
    except Exception:  # noqa: BLE001
        return None
    pre = (getattr(Pl, 'STYLE_PRESETS', {}) or {}).get(m.get('name')) if m else None
    if not pre:
        return None
    cs = pre.get('caption_style')
    sib = getattr(Pl, 'CAPTION_SIBLING', {}) or {}
    if cs and variant and int(variant) % 2 == 1:
        cs = sib.get(cs, cs)
    return dict(name=m['name'], genre=pre.get('genre'), caption_style=cs, transitions=list(pre.get('transitions') or []),
                why=m.get('why'))


def normalize_spec(spec, base_dir=None):
    """Validate + fill defaults; paths absolute. Raises SpecError with a readable message."""
    if not isinstance(spec, dict):
        raise SpecError('spec must be a JSON object')
    s = copy.deepcopy(spec)
    base = base_dir or s.get('base_dir') or os.getcwd()
    cv = s.get('canvas') or {}
    fps = float(cv.get('fps', 30))
    canvas = dict(w=int(cv.get('w', 1080)), h=int(cv.get('h', 1920)), fps=int(round(fps)))
    if abs(fps - round(fps)) > 1e-6:
        raise SpecError('canvas.fps must be a whole number (24, 25, 30, 60)')
    level = _sfx_level(s.get('sfx') or 'genre', 'sfx')
    parts, ids = [], set()
    if not s.get('parts'):
        raise SpecError('spec.parts is empty')
    counters = {}
    for i, p in enumerate(s['parts']):
        if not isinstance(p, dict):
            raise SpecError(f'part #{i + 1}: must be an object')
        t = p.get('type')
        if t not in PART_TYPES:
            raise SpecError(f'part #{i + 1}: type must be one of {PART_TYPES} (got {t!r})')
        counters[t] = counters.get(t, 0) + 1
        q = dict(p)
        q['id'] = str(p.get('id') or (t if counters[t] == 1 else f'{t}{counters[t]}'))
        if q['id'] in ids:
            raise SpecError(f'duplicate part id {q["id"]!r}')
        ids.add(q['id'])
        q['index'] = i
        q['sfx'] = _sfx_level(p.get('sfx') or level, f'part {q["id"]}: sfx')
        if t in ('talk', 'clip'):
            if not p.get('source'):
                raise SpecError(f'part {q["id"]}: "source" is required')
            q['source'] = _abspath(p['source'], base)
            if not os.path.exists(q['source']):
                raise SpecError(f'part {q["id"]}: file not found {q["source"]}')
            if p.get('transcript'):
                q['transcript'] = _abspath(p['transcript'], base)
            q['from'] = _point(p.get('from'), f'{q["id"]}.from')
            q['to'] = _point(p.get('to'), f'{q["id"]}.to')
            rem = []
            for j, r in enumerate(p.get('remove') or []):
                if isinstance(r, (list, tuple)) and len(r) == 2:
                    rem.append({'from': {'t': float(r[0])}, 'to': {'t': float(r[1])}})
                elif isinstance(r, str):
                    rem.append({'phrase': r})
                elif isinstance(r, dict) and r.get('phrase'):
                    rem.append(dict(r))
                elif isinstance(r, dict) and ('from' in r or 'to' in r):
                    rem.append({'from': _point(r.get('from'), f'{q["id"]}.remove[{j}].from'),
                                'to': _point(r.get('to'), f'{q["id"]}.remove[{j}].to')})
                else:
                    raise SpecError(f'part {q["id"]}: remove[{j}] must be a phrase, {{"from","to"}} or [t0, t1]')
            q['remove'] = rem
        for key in ('style', 'variant'):                           # per part, else the spec's top level
            if q.get(key) is None and s.get(key) is not None:
                q[key] = copy.deepcopy(s[key])
        if q.get('variant') is not None:
            q['variant'] = int(q['variant'])
            if q['variant'] < 0:
                raise SpecError(f'part {q["id"]}: variant must be >= 0')
        # earlier versions to steer away from: an edit part's "avoid" (a talk / clip part's "avoid" is its overlay
        # boxes), else the part's "avoid_versions", else the spec's top-level "avoid" / "avoid_versions"
        av = q.get('avoid_versions')
        if av is None and t == 'edit':
            av = q.get('avoid')
        if av is None:
            av = s.get('avoid_versions', s.get('avoid'))
        if av is not None:
            av = [_abspath(a, base) if isinstance(a, str) else a for a in (av if isinstance(av, list) else [av])]
        q['avoid_versions'] = av
        if t == 'edit':
            q['avoid'] = av
        if t == 'edit':
            if not p.get('footage'):
                raise SpecError(f'part {q["id"]}: "footage" is required')
            q['footage'] = _expand_footage(p['footage'], base)
            q['order'] = str(p.get('order') or 'given')
            q['genre'] = str(p.get('genre') or _style_genre(q.get('style')) or 'epic')
            q['bars'] = None if p.get('bars') is None else int(p['bars'])
            q['shots'] = None if p.get('shots') is None else int(p['shots'])
            if q['bars'] is None and q['shots'] is None:
                q['shots'] = len(q['footage'])
            if q['bars'] is None:
                q['bars'] = q['shots']
            if q['shots'] is None:
                q['shots'] = min(q['bars'] * 2, max(q['bars'], len(q['footage'])))
            if q['bars'] <= 0 or q['shots'] <= 0:
                raise SpecError(f'part {q["id"]}: bars and shots must be positive')
            mv = p.get('moves') or []
            q['moves'] = [mv] if isinstance(mv, str) else list(mv)
            fb = p.get('forbid') or []
            q['forbid'] = [fb] if isinstance(fb, str) else list(fb)
            q['engine'] = str(p.get('engine') or 'auto')
        parts.append(q)
    music = None
    if s.get('music'):
        m = dict(s['music']) if isinstance(s['music'], dict) else {'path': s['music']}
        m['path'] = _abspath(m.get('path'), base)
        if not m['path'] or not os.path.exists(m['path']):
            raise SpecError(f'music file not found: {m.get("path")}')
        da = m.get('drop_at')
        if isinstance(da, str):
            da = {'part': da, 'at': 'start'}
        if da is not None:
            if da.get('part') not in ids:
                raise SpecError(f'music.drop_at.part {da.get("part")!r} is not a part id')
            da = dict(part=da['part'], at=da.get('at', 'start'))
        m['drop_at'] = da
        music = m
    trans = []
    for j, tr in enumerate(s.get('transitions') or []):
        if tr.get('from') not in ids or tr.get('to') not in ids:
            raise SpecError(f'transitions[{j}]: from/to must be part ids')
        kind = str(tr.get('kind') or 'cut')
        if kind != 'cut' and kind not in TRANSITION_KINDS:
            raise SpecError(f'transitions[{j}]: unknown kind {kind!r}')
        trans.append(dict(tr, kind=kind))
    lo = s.get('loudness') or {}
    sfx_dir = None
    if s.get('sfx_dir'):                                       # the user's sound folder (relative to the spec)
        sfx_dir = _abspath(str(s['sfx_dir']), base)
        if not os.path.isdir(sfx_dir):
            raise SpecError(f'sfx_dir is not a folder: {s["sfx_dir"]}')
    return dict(canvas=canvas, parts=parts, music=music, transitions=trans, sfx=level, sfx_dir=sfx_dir,
                style=s.get('style'), variant=None if s.get('variant') is None else int(s['variant']),
                loudness=dict(lufs=float(lo.get('lufs', -14.0)), tp=float(lo.get('tp', -1.0))),
                subtitles=s.get('subtitles'), end=dict(s.get('end') or {}), base_dir=base,
                qa=dict(s.get('qa') or {}), title=s.get('title'))


# ============================================================================ words and phrases
_ONES = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
         'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
         'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
         'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90}
_SCALES = {'hundred': 100, 'thousand': 1000, 'million': 10 ** 6, 'billion': 10 ** 9, 'trillion': 10 ** 12}
_SUFFIX = {'k': 'thousand', 'm': 'million', 'mm': 'million', 'mn': 'million', 'b': 'billion', 'bn': 'billion'}
SENT_END = '.!?\u2026'
CLOSERS = '"\'\u00bb\u201d)'                  # quotes / brackets that may follow a sentence end


def clean_words(words, vocab=None):
    """ASR word list -> display-ready words: digit groups split by the recogniser are joined ("$20" ",000" ->
    "$20,000"), vocabulary terms split into pieces are joined ("Kor" "vanta," -> "Korvanta,"). Keeps t0/t1/p."""
    out = []
    for w in words or []:
        if w.get('t0') is None or not str(w.get('w', '')).strip():
            continue
        x = dict(w)
        x['w'] = str(x['w']).strip()
        if out and re.fullmatch(r'[,.]\d{3}\S*', x['w']) and re.search(r'\d$', out[-1]['w']):
            out[-1] = dict(out[-1], w=out[-1]['w'] + x['w'], t1=x['t1'])
            continue
        out.append(x)
    terms = []
    for v in vocab or []:
        key = re.sub(r'[\W_]+', '', unicodedata.normalize('NFKC', str(v)).lower())
        if key:
            terms.append((key, str(v)))
    if not terms:
        return out
    res, i = [], 0
    while i < len(out):
        hit = None
        for key, term in terms:
            acc = ''
            for j in range(i, min(i + 4, len(out))):
                acc += re.sub(r'[\W_]+', '', unicodedata.normalize('NFKC', out[j]['w']).lower())
                if acc == key and j > i:
                    hit = (j, term)
                    break
                if not key.startswith(acc):
                    break
            if hit:
                break
        if hit:
            j, term = hit
            tail = re.search(r'[^\w]*$', out[j]['w']).group(0)
            lead = re.match(r'^[^\w]*', out[i]['w']).group(0)
            res.append(dict(out[i], w=lead + term + tail, t1=out[j]['t1']))
            i = j + 1
        else:
            res.append(out[i])
            i += 1
    return res


def _tokens(text):
    s = re.sub('(?<=\\d)[,\u202f\u00a0](?=\\d{3}(?!\\d))', '', str(text))     # 4,000,000 -> 4000000 (before NFKC)
    s = unicodedata.normalize('NFKC', s).lower().replace('\u0451', '\u0435').replace('\u2019', "'")
    s = re.sub(r'(?<=\d)\s?(mm|mn|bn|k|m|b)\b', lambda m: ' ' + _SUFFIX[m.group(1)], s)
    s = s.replace('%', ' percent ').replace("'", '')
    return re.findall(r'\d+(?:\.\d+)?|[^\W\d_]+', s)


def _is_num(t):
    return t[:1].isdigit() or t in _ONES or t in _SCALES


def _atoms(words):
    """Canonical atoms [(text, w0, w1)] of a word list: lowercase letters/digits only, number phrases folded into
    one value ("3" "million" -> "3000000", "three million" -> "3000000", "$20,000" -> "20000")."""
    toks = []
    for i, w in enumerate(words):
        for t in _tokens(w['w'] if isinstance(w, dict) else w):
            toks.append((t, i))
    out, k = [], 0
    while k < len(toks):
        t, wi = toks[k]
        starts = _is_num(t) or (t == 'a' and k + 1 < len(toks) and toks[k + 1][0] in _SCALES)
        if not starts:
            out.append((t, wi, wi))
            k += 1
            continue
        total, cur, j, w0, w1, used = 0.0, 0.0, k, wi, wi, False
        while j < len(toks):
            tj = toks[j][0]
            if tj[:1].isdigit():
                if used and cur and not total and cur >= 10 and float(tj) < 1000:
                    break                                         # "2024 5" are two numbers
                cur += float(tj)
            elif tj in _ONES:
                cur += _ONES[tj]
            elif tj == 'hundred':
                cur = (cur or 1) * 100
            elif tj in _SCALES:
                total += (cur or 1) * _SCALES[tj]
                cur = 0.0
            elif tj == 'a' and j + 1 < len(toks) and toks[j + 1][0] in _SCALES and not used:
                pass
            elif tj == 'and' and used and j + 1 < len(toks) and (toks[j + 1][0] in _ONES or toks[j + 1][0][:1].isdigit()):
                pass
            else:
                break
            used = True
            w1 = toks[j][1]
            j += 1
        v = total + cur
        out.append(((str(int(v)) if float(v).is_integer() else f'{v:g}'), w0, w1))
        k = max(j, k + 1)
    return out


def _numbers(atoms):
    return {a for a, _, _ in atoms if a[:1].isdigit()}


def numbers_match(words, i0, i1, text):
    """Every number of the query appears, as the same value, in words[i0..i1] ("3 million" never matches
    "5 billion", whatever the fuzzy score)."""
    need = _numbers(_atoms([{'w': x} for x in str(text).split()]))
    return need <= _numbers(_atoms(words[i0:i1 + 1])) if need else True


def find_phrase_local(words, text, after=None, before=None, min_score=0.72, numbers=True):
    """Fuzzy phrase search on the canonical character string (spaces, case, punctuation and number format do not
    matter; numbers must match exactly). Earliest of the best-scoring windows that start at/after `after` and end
    by `before`. -> {"t0", "t1", "i0", "i1", "score", "text"} | None"""
    A = _atoms(words)
    qa = _atoms([{'w': x} for x in str(text).split()])
    q = ''.join(a for a, _, _ in qa)
    need = _numbers(qa) if numbers else set()
    if not q or not A:
        return None
    sm = difflib.SequenceMatcher(autojunk=False)
    sm.set_seq2(q)
    nq = len(q)
    cands = []
    for a in range(len(A)):
        w0 = A[a][1]
        if after is not None and words[w0]['t0'] < after - 0.05:
            continue
        if before is not None and words[w0]['t0'] >= before:
            break
        s = ''
        for b in range(a, len(A)):
            s += A[b][0]
            if len(s) > 1.5 * nq + 3:
                break
            if before is not None and words[A[b][2]]['t1'] > before + 0.05:
                break
            if len(s) < 0.6 * nq - 2:
                continue
            sm.set_seq1(s)
            if sm.real_quick_ratio() < min_score or sm.quick_ratio() < min_score:
                continue
            r = sm.ratio()
            if r >= min_score and (not need or need <= {x for x, _, _ in A[a:b + 1] if x[:1].isdigit()}):
                cands.append((r, a, b))
    if not cands:
        return None
    best = max(c[0] for c in cands)
    top = [c for c in cands if c[0] >= best - 0.02]
    r, a, b = min(top, key=lambda c: (A[c[1]][1], -c[0], c[2]))
    for c in cands:                         # the best window starting at the same atom (tight end)
        if c[1] == a and c[0] > r:
            r, b = c[0], c[2]
    i0, i1 = A[a][1], A[b][2]
    return dict(t0=float(words[i0]['t0']), t1=float(words[i1]['t1']), i0=int(i0), i1=int(i1), score=round(r, 3),
                text=' '.join(w['w'] for w in words[i0:i1 + 1]))


def find_phrase(words, text, after=None, before=None):
    """ed_voice.find_phrase when available (talk agent), else the local matcher; results are sanity-checked."""
    f = _fn('ed_voice', 'find_phrase')
    if f is not None:
        try:
            r = f(words, text, after=after, before=before)
            if r and 0 <= int(r['i0']) <= int(r['i1']) < len(words) and r['t1'] >= r['t0'] and \
                    numbers_match(words, int(r['i0']), int(r['i1']), text):
                r = dict(r)
                r.setdefault('text', ' '.join(w['w'] for w in words[int(r['i0']):int(r['i1']) + 1]))
                r['by'] = 'ed_voice'
                return r
        except Exception:  # noqa: BLE001 - fall back to the local matcher
            pass
    r = find_phrase_local(words, text, after=after, before=before)
    if r:
        r['by'] = 'local'
    return r


def _sentences(words):
    """Word index groups split at sentence ends and pauses >= 0.5 s."""
    out, cur = [], []
    for i, w in enumerate(words):
        if cur and w['t0'] - words[i - 1]['t1'] >= 0.5:
            out.append(cur)
            cur = []
        cur.append(i)
        if w['w'].rstrip(CLOSERS)[-1:] in SENT_END:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


# ============================================================================ audio envelope (cut points)
class Envelope:
    """10 ms RMS (dB) of a source's audio between t0 and t1 (16 kHz mono, decoded once)."""

    HOP = 0.01

    def __init__(self, path, t0, t1):
        self.t0 = max(0.0, float(t0))
        dur = max(0.2, float(t1) - self.t0)
        cmd = ['ffmpeg', '-v', 'error', '-nostdin', '-ss', f'{self.t0:.3f}', '-i', path, '-t', f'{dur:.3f}', '-vn',
               '-ac', '1', '-ar', '16000', '-f', 'f32le', '-']
        y = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)
        hop = 160
        n = len(y) // hop
        if n < 3:
            self.db = np.full(3, -90.0)
        else:
            fr = y[:n * hop].reshape(n, hop).astype(np.float64)
            self.db = 10 * np.log10(np.mean(fr * fr, axis=1) + 1e-10)
        sm = np.convolve(self.db, np.ones(3) / 3, mode='same')
        self.sm = sm
        self.floor = float(np.percentile(sm, 8)) if len(sm) else -90.0
        self.peak = float(np.percentile(sm, 97)) if len(sm) else -20.0

    def _i(self, t):
        return int(round((t - self.t0) / self.HOP))

    def level(self, a, b):
        i0, i1 = max(0, self._i(a)), min(len(self.sm), max(self._i(b), self._i(a) + 1))
        return float(np.mean(self.sm[i0:i1])) if i1 > i0 else -90.0

    def quietest(self, a, b, prefer=None, tol_db=3.0):
        """A quiet 10 ms point in [a, b]: among the points within tol_db of the window's minimum (smoothed), the one
        nearest to `prefer` (default: the minimum itself). Keeps cuts off word onsets and breath noise."""
        if b <= a:
            return (a + b) / 2
        i0, i1 = max(0, self._i(a)), min(len(self.sm) - 1, self._i(b))
        if i1 < i0:
            return (a + b) / 2
        ts = self.t0 + np.arange(i0, i1 + 1) * self.HOP
        v = self.sm[i0:i1 + 1]
        if prefer is None:
            return float(ts[int(np.argmin(v))])
        ok = v <= float(v.min()) + tol_db
        return float(ts[ok][int(np.argmin(np.abs(ts[ok] - prefer)))])

    def onset_after(self, a, b, rise_db=12.0):
        """First time in [a, b] where the level jumps >= rise_db within 30 ms (a word onset), or None."""
        i0, i1 = max(0, self._i(a)), min(len(self.sm) - 4, self._i(b))
        for i in range(i0, i1):
            if self.db[i + 3] - self.db[i] >= rise_db and self.db[i + 3] > self.floor + 15:
                return self.t0 + (i + 1) * self.HOP
        return None

    def quiet_runs(self, a, b, margin_db=7.0, min_s=0.06):
        """[(t0, t1)] stretches in [a, b] that stay within margin_db of the noise floor for >= min_s."""
        i0, i1 = max(0, self._i(a)), min(len(self.sm), self._i(b) + 1)
        q = self.sm[i0:i1] <= self.floor + margin_db
        out, s = [], None
        for k, v in enumerate(list(q) + [False]):
            if v and s is None:
                s = k
            elif not v and s is not None:
                if (k - s) * self.HOP >= min_s:
                    out.append((self.t0 + (i0 + s) * self.HOP, self.t0 + (i0 + k) * self.HOP))
                s = None
        return out


def _cut_before(words, i, env, lead=0.08, max_back=1.5, min_gap=0.12, walk=True, max_lead=0.30):
    """In-point for a range that starts with word i: the quietest point of the pause before it. Inside connected
    speech (no pause) the in-point moves back to the previous pause (<= max_back) so no syllable is clipped -
    unless walk=False (the words before are removed on purpose): then the cut sits on the word boundary.
    -> (t, first word index kept)"""
    j = i
    while walk and j > 0 and words[j]['t0'] - words[j - 1]['t1'] < min_gap and \
            words[i]['t0'] - words[j - 1]['t0'] <= max_back:
        j -= 1
    if j > 0 and words[j]['t0'] - words[j - 1]['t1'] < min_gap:
        j = i                                   # no pause within reach: cut at the word itself
        if env is not None:
            return float(env.quietest(words[j]['t0'] - 0.07, words[j]['t0'] + 0.02, prefer=words[j]['t0'] - 0.01)), j
        return float(words[j]['t0'] - 0.01), j
    w = words[j]
    prev_t1 = words[j - 1]['t1'] if j > 0 else w['t0'] - 0.6
    lo, hi = max(prev_t1 + 0.03, w['t0'] - max_lead), w['t0'] - 0.02
    if env is not None and hi > lo:
        on = env.onset_after(lo, w['t0'] + 0.12)          # the word may start before its ASR time
        if on is not None and lo < on - 0.02 < hi:
            hi = on - 0.02
            lo = max(lo, on - max_lead)
    if hi <= lo:
        return max(prev_t1, w['t0'] - 0.02 if hi < lo else (lo + hi) / 2), j
    t = env.quietest(lo, hi, prefer=hi - lead + 0.02) if env is not None else max(lo, w['t0'] - lead)
    return t, j


def _cut_after(words, i, env, tail=0.14, max_fwd=1.5, min_gap=0.12, walk=True, max_tail=0.40):
    """Out-point for a range that ends with word i: the quietest point of the pause after it (moves forward to the
    next pause inside connected speech, <= max_fwd; walk=False: the next words are removed on purpose, cut on the
    word boundary). -> (t, last word index kept)"""
    j = i
    n = len(words)
    while walk and j < n - 1 and words[j + 1]['t0'] - words[j]['t1'] < min_gap and \
            words[j + 1]['t1'] - words[i]['t1'] <= max_fwd:
        j += 1
    if j < n - 1 and words[j + 1]['t0'] - words[j]['t1'] < min_gap:
        j = i
        if env is not None:
            return float(env.quietest(words[j]['t1'] - 0.02, words[j + 1]['t0'] + 0.05,
                                      prefer=words[j]['t1'] + 0.01)), j
        return float(words[j]['t1'] + 0.01), j
    w = words[j]
    nxt_t0 = words[j + 1]['t0'] if j < n - 1 else w['t1'] + 0.6
    lo, hi = w['t1'] + 0.03, min(w['t1'] + max_tail, nxt_t0 - 0.04)
    if env is not None and hi > lo:
        on = env.onset_after(lo + 0.05, nxt_t0 + 0.12)     # the next word may start before its ASR time
        if on is not None and lo < on - 0.04 < hi:
            hi = on - 0.04
    if hi <= lo:
        return min(nxt_t0, w['t1'] + 0.02 if hi < lo else (lo + hi) / 2), j
    t = env.quietest(lo, hi, prefer=w['t1'] + tail) if env is not None else min(hi, w['t1'] + tail)
    return t, j


def reaction_end_local(media, t, words, max_s=4.0, env=None):
    """End of the reaction after time t: one/two-word exclamations ("Wow.", "Oh my") and non-verbal sound (sigh,
    laugh) are kept; the result is the quiet point before the next real sentence (or the end of the sound)."""
    env = env or Envelope(media, t - 0.5, t + max_s + 1.5)
    after = [i for i, w in enumerate(words) if w['t0'] >= t - 0.02]
    sents = _sentences([words[i] for i in after])
    last, nxt = t, None
    for s in sents:
        ws = [words[after[k]] for k in s]
        if ws[0]['t0'] > t + max_s:
            nxt = ws[0]['t0']
            break
        if len(ws) <= 2 and ws[-1]['t1'] - ws[0]['t0'] <= 1.5:
            last = ws[-1]['t1']                 # a reaction word
            continue
        nxt = ws[0]['t0']
        break
    hi = min(t + max_s, (nxt - 0.04) if nxt is not None else t + max_s)
    lo = min(last + 0.04, hi)
    # non-verbal sound right after the last reaction word: wait for it to fade
    runs = [r for r in env.quiet_runs(lo, hi + 0.05) if r[1] - r[0] >= 0.06]
    if runs:
        a, b = runs[0]
        if nxt is not None and b >= nxt - 0.06:
            return float(min(hi, max(lo, env.quietest(a, min(b, hi), prefer=a + 0.10))))
        return float(min(hi, a + min(0.15, (b - a) / 2)))
    return float(env.quietest(lo, hi, prefer=lo + 0.1)) if hi > lo else float(hi)


def refine_end(env, t, words, lo=None):
    """Make an out-point safe: never past the energy onset of the next word (ASR word times can be 0.1-0.3 s off);
    inside connected speech take the quietest point just before that onset."""
    if env is None:
        return t
    nxt = next((w for w in words if w['t0'] > t - 0.25), None)
    a = max(lo if lo is not None else t - 0.25, t - 0.25)
    on = env.onset_after(a, t + 0.12)
    if on is not None and on < t + 0.02:
        return float(env.quietest(max(a, on - 0.18), on - 0.02, prefer=on - 0.05))
    if nxt is not None and nxt['t0'] < t + 0.1:
        return float(env.quietest(a, min(t + 0.03, nxt['t0'] - 0.01), prefer=t - 0.03))
    return t


def reaction_end(media, t, words, max_s=4.0, env=None):
    """-> (out-point, 'ed_voice'|'local'); the result is refined against the energy envelope (refine_end)."""
    f = _fn('ed_voice', 'reaction_end')
    v, by = None, 'local'
    if f is not None:
        try:
            v = float(f(media, t, words=words, max_s=max_s))
            by = 'ed_voice'
            if not t - 0.05 <= v <= t + max_s + 0.6:
                v, by = None, 'local'
        except Exception:  # noqa: BLE001
            v = None
    if v is None:
        v = reaction_end_local(media, t, words, max_s=max_s, env=env)
    return refine_end(env, v, words, lo=t + 0.05), by


# ============================================================================ transcripts
def _cached_transcript(path):
    """A transcript of this exact file already in ed_voice's cache (any language option) - saves an ASR run."""
    Vo = _mod('ed_voice')
    if Vo is None or not hasattr(Vo, 'CACHE'):
        return None
    try:
        h = Vo.file_hash(path)
    except Exception:  # noqa: BLE001
        return None
    best = None
    for p in glob.glob(os.path.join(str(Vo.CACHE), 'transcripts', f'{h}-*.json')):
        d = _load_json(p)
        if d and d.get('version') == getattr(Vo, 'VERSION', d.get('version')) and d.get('source') == 'asr' \
                and d.get('words') and (best is None or os.path.getmtime(p) > best[0]):
            best = (os.path.getmtime(p), d)
    return best[1] if best else None


def get_words(part, log):
    """Words of a talk/clip source: the part's transcript file, ed_voice's cache, or a fresh ed_voice.transcribe."""
    if part.get('transcript'):
        d = _load_json(part['transcript'])
        if d is None:
            raise SpecError(f'part {part["id"]}: cannot read transcript {part["transcript"]}')
        words = d.get('words') if isinstance(d, dict) else d
        return words, dict(source='file', path=part['transcript'], lang=(d.get('lang') if isinstance(d, dict) else None))
    hit = _cached_transcript(part['source'])
    if hit and part.get('lang') and str(hit.get('lang') or '')[:2] != str(part['lang'])[:2]:
        hit = None                                      # cached in another language: transcribe again
    if hit:
        log(f'[sequence] {part["id"]}: transcript from the ed_voice cache ({len(hit["words"])} words, {hit.get("model")})')
        return hit['words'], dict(source='cache', lang=hit.get('lang'), model=hit.get('model'))
    tr = _fn('ed_voice', 'transcribe')
    if tr is None:
        raise SpecError(f'part {part["id"]}: phrases need word timestamps - ed_voice.transcribe is not available; '
                        f'give "transcript": words.json or times in seconds')
    log(f'[sequence] {part["id"]}: transcribing {os.path.basename(part["source"])} (ed_voice, cached by file hash) ...')
    t0 = time.time()
    res = tr(part['source'], lang=part.get('lang'), prompt=', '.join(part.get('vocab') or []) or None)
    log(f'[sequence] {part["id"]}: {len(res["words"])} words, lang {res.get("lang")} ({time.time() - t0:.0f} s)')
    return res['words'], dict(source='asr', lang=res.get('lang'), model=res.get('model'))


# ============================================================================ talk / clip ranges
def _locate(pt, words, what, after=None, before=None):
    if pt is None:
        return None
    if pt.get('t') is not None:
        return dict(t0=pt['t'], t1=pt['t'], by='time')
    occ = int(pt.get('occurrence') or 1)
    lo = after
    hit = None
    for _ in range(max(1, occ)):
        hit = find_phrase(words, pt['phrase'], after=lo, before=before)
        if hit is None:
            break
        lo = hit['t1'] + 0.01
    if hit is None:
        near = find_phrase_local(words, pt['phrase'], after=after, before=before, min_score=0.45, numbers=False)
        msg = f'{what}: phrase not found: {pt["phrase"]!r}'
        if near:
            msg += f' (closest: {near["text"]!r} at {near["t0"]:.2f} s, score {near["score"]})'
        raise SpecError(msg)
    return hit


LONG_SOURCE_S = 90.0       # a talk source longer than this with no "from": the start is a setup sentence ...
AUTO_MAX_S = 25.0          # ... at most this many seconds before the end (or "from": {"auto": true, "max_s": ..})


def clean_starts(words, t_min=0.0, t_max=None):
    """Indices of words that start a clean sentence: capitalised (or a number) after a sentence end or a pause of
    >= 0.6 s; the very first word only when the recording does not start inside it (>= 0.25 s before it) - a
    fragment cut off by the start of the recording is skipped."""
    out = []
    for i, w in enumerate(words):
        if w['t0'] < t_min - 1e-6 or (t_max is not None and w['t0'] > t_max + 1e-6):
            continue
        c = str(w['w']).strip().lstrip('"\'(\u201c\u00ab')[:1]
        cap = c.isupper() or c.isdigit() or c == '$'
        if i == 0:
            ok = cap and w['t0'] >= 0.25
        else:
            prev = words[i - 1]
            ok = cap and (prev['w'].rstrip(CLOSERS)[-1:] in SENT_END or w['t0'] - prev['t1'] >= 0.6)
        if ok:
            out.append(i)
    return out


def _setup_start(words, t_end, max_s, skip, log, env=None):
    """talk's ed_voice.setup_starts(words, end_t, max_s=, env={"cuts", "turns", "avoid"}) - the best setup sentence
    before the end, when it exists - minus the starts in `skip` -> (word index, why) | None."""
    f = _fn('ed_voice', 'setup_starts')
    if f is None:
        return None
    env = dict(env or {})
    env['avoid'] = [list(x) for x in env.get('avoid') or []] + [[s - 0.3, s + 0.3] for s in skip]
    try:
        try:
            res = f(words, t_end, max_s=max_s, env=env)
        except TypeError:
            res = f(words, t_end)
    except Exception as e:  # noqa: BLE001
        log(f'[sequence] ed_voice.setup_starts failed ({type(e).__name__}: {e}); first clean sentence instead')
        return None
    cands = (res.get('candidates') or ([res['best']] if res.get('best') else [])) if isinstance(res, dict) else (res or [])
    for c in [c for c in cands if isinstance(c, dict)]:          # best first
        i = c.get('i0', c.get('i'))
        t = c.get('t0', c.get('t'))
        if not isinstance(i, int) or not 0 <= i < len(words):
            if t is None:
                continue
            i = next((k for k, w in enumerate(words) if w['t0'] >= float(t) - 0.05), None)
            if i is None:
                continue
        if any(abs(words[i]['t0'] - s) < 0.05 for s in skip) or words[i]['t0'] >= t_end:
            continue
        return i, str(c.get('why') or c.get('text') or 'setup sentence')[:120]
    return None


def _auto_start(part, words, t_end, log):
    """Start of a talk part whose "from" is missing / {"auto": true}: the first clean sentence (a long source: the
    best setup sentence at most max_s before the end, from ed_voice.setup_starts when it exists); starts listed in
    part["_skip_starts"] (picture hidden by a popup / no face) are passed over. -> (word index, why)"""
    fp = part.get('from') if isinstance(part.get('from'), dict) else {}
    dur = float(part.get('_dur') or 0.0)
    skip = list(part.get('_skip_starts') or [])
    explicit = bool(fp.get('auto'))
    long_src = dur > LONG_SOURCE_S
    max_s = float(fp.get('max_s', AUTO_MAX_S)) if (explicit or long_src) else None
    if max_s is not None:
        hit = _setup_start(words, t_end, max_s, skip, log,
                           env=dict(avoid=part.get('_avoid_spans') or [], cuts=part.get('_cuts') or []))
        if hit is not None and t_end - words[hit[0]]['t0'] <= max_s + 1e-6:
            return hit[0], f'setup sentence ({hit[1]})'
    lo = (t_end - max_s) if max_s is not None else 0.0
    cands = [i for i in clean_starts(words, lo, t_end - 0.5) if not any(abs(words[i]['t0'] - s) < 0.05 for s in skip)]
    if cands:
        why = 'first clean sentence' + (f' within {max_s:g} s of the end' if max_s is not None else '')
        if skip:
            why += f' ({len(skip)} earlier start(s) skipped: picture hidden)'
        return cands[0], why
    i = next((k for k, w in enumerate(words) if w['t0'] >= lo), 0)
    return i, 'first word' + (f' within {max_s:g} s of the end' if max_s is not None else '')


def resolve_ranges(part, words, env, log=print):
    """Phrases / times of a talk or clip part -> kept source ranges. No "from" (or {"auto": true}): the first clean
    sentence, see _auto_start.
    -> {"keep": [[t0, t1], ...], "from": hit, "to": hit, "removed": [...], "reaction": [t0, t1] | None, "notes"}"""
    notes = []
    fp, tp = part.get('from'), part.get('to')
    auto = bool(words) and (isinstance(fp, dict) and bool(fp.get('auto')) or
                            (fp is None and part.get('type', 'talk') == 'talk'))
    h_from = _locate(fp, words, f'{part["id"]}.from') if fp and not auto else None
    h_to = _locate(tp, words, f'{part["id"]}.to', after=(h_from['t0'] if h_from and h_from.get('by') != 'time' else
                                                          (h_from['t0'] if h_from else None))) if tp else None
    # ---- in-point
    if auto:
        t_end = h_to['t0'] if h_to else words[-1]['t1']
        i, why = _auto_start(part, words, t_end, log)
        t_in, i_first = _cut_before(words, i, env)
        h_from = dict(t0=words[i]['t0'], t1=words[i]['t1'], i0=i, i1=i, by='auto', text=words[i]['w'], score=1.0)
        notes.append(f'start: {why} - "{" ".join(w["w"] for w in words[i:i + 6])}..." at {words[i]["t0"]:.2f} s')
    elif h_from is None:
        t_in, i_first = (words[0]['t0'] - 0.1, 0) if words else (0.0, 0)
    elif h_from.get('by') == 'time':
        t_in = h_from['t0']
        i_first = next((i for i, w in enumerate(words) if w['t1'] > t_in + 0.02), len(words))
    else:
        snap = (fp or {}).get('snap', 'pause')
        i = h_from['i0']
        if snap == 'sentence':
            while i > 0 and words[i - 1]['w'].rstrip(CLOSERS)[-1:] not in SENT_END and h_from['t0'] - words[i - 1]['t0'] < 6:
                i -= 1
        if snap == 'word':
            t_in, i_first = max(words[i]['t0'] - 0.06, words[i - 1]['t1'] if i else 0.0), i
        else:
            t_in, i_first = _cut_before(words, i, env)
        if i_first < h_from['i0']:
            notes.append(f'in-point moved back to the pause before "{words[i_first]["w"]}" '
                         f'(the phrase starts inside connected speech)')
    t_in = max(0.0, t_in - float((fp or {}).get('pad', 0.0) or 0.0))      # pad: extra seconds before
    # ---- out-point
    reaction = None
    if h_to is None:
        t_out = (words[-1]['t1'] + 0.3) if words else None
        i_last = len(words) - 1
    elif h_to.get('by') == 'time':
        t_out, i_last = h_to['t1'], max([i for i, w in enumerate(words) if w['t0'] < h_to['t1']] or [0])
    else:
        mode = (tp or {}).get('end', 'phrase')
        i = h_to['i1']
        if mode == 'sentence':
            while i < len(words) - 1 and words[i]['w'].rstrip(CLOSERS)[-1:] not in SENT_END:
                i += 1
        if mode == 'after_reaction':
            t_out, by = reaction_end(part['source'], words[i]['t1'], words, max_s=float(tp.get('max_s', 4.0)), env=env)
            reaction = [float(words[i]['t1']), float(t_out)]
            i_last = max([k for k, w in enumerate(words) if w['t1'] <= t_out + 0.02] or [i])
            notes.append(f'reaction kept: {reaction[0]:.2f}-{reaction[1]:.2f} s ({by})')
        else:
            t_out, i_last = _cut_after(words, i, env)
            if i_last > i:
                notes.append(f'out-point moved on to the pause after "{words[i_last]["w"]}" '
                             f'(the phrase ends inside connected speech)')
    if t_out is None:
        raise SpecError(f'part {part["id"]}: no out-point (no words after the in-point); give "to" in seconds')
    t_out = t_out + float((tp or {}).get('pad', 0.0) or 0.0)
    if t_out <= t_in + 0.2:
        raise SpecError(f'part {part["id"]}: empty range ({t_in:.2f}-{t_out}); check from/to')
    keep = [[float(t_in), float(t_out)]]
    removed = []
    # ---- removals
    for j, rm in enumerate(part.get('remove') or []):
        if rm.get('phrase'):
            h = find_phrase(words, rm['phrase'], after=t_in - 0.05, before=t_out + 0.05)
            if h is None:
                near = find_phrase_local(words, rm['phrase'], after=t_in - 0.05, before=t_out + 0.05, min_score=0.45, numbers=False)
                raise SpecError(f'{part["id"]}.remove[{j}]: phrase not found inside the part: {rm["phrase"]!r}'
                                + (f' (closest: {near["text"]!r}, score {near["score"]})' if near else ''))
            # jump cut: keep the joined pause short (clips card: <= 0.35 s) - a short tail and a short lead
            a = _cut_after(words, h['i0'] - 1, env, tail=0.10, walk=False, max_tail=0.20)[0] if h['i0'] > 0 \
                else h['t0'] - 0.05
            b = _cut_before(words, h['i1'] + 1, env, lead=0.03, walk=False, max_lead=0.14)[0] \
                if h['i1'] + 1 < len(words) else h['t1'] + 0.1
            if h['i0']:
                a = max(a, words[h['i0'] - 1]['t1'] + 0.02)
            removed.append(dict(t0=_r(a), t1=_r(b), text=h['text'], score=h['score']))
        else:
            a = _locate(rm.get('from'), words, f'{part["id"]}.remove[{j}].from')
            b = _locate(rm.get('to'), words, f'{part["id"]}.remove[{j}].to')
            a = a['t0'] if a else t_in
            b = b['t1'] if b else t_out
            removed.append(dict(t0=_r(a), t1=_r(b), text=None))
        keep = _subtract(keep, removed[-1]['t0'], removed[-1]['t1'])
    # ---- tighten long pauses (never inside the reaction)
    tp_s = part.get('tighten_pauses')
    if tp_s:
        mx = 0.35 if tp_s is True else float(tp_s)
        ws = [w for w in words if any(a <= w['t0'] and w['t1'] <= b + 0.02 for a, b in keep)]
        for w, w2 in zip(ws, ws[1:]):
            gap = w2['t0'] - w['t1']
            if gap <= mx + 0.05:
                continue
            if reaction and w['t1'] >= reaction[0] - 0.02:
                continue
            if not any(a <= w['t1'] and w2['t0'] <= b for a, b in keep):
                continue                                    # the pause spans a removal: already cut
            a = env.quietest(w['t1'] + 0.6 * mx - 0.05, w['t1'] + 0.6 * mx + 0.05) if env else w['t1'] + 0.6 * mx
            b = env.quietest(w2['t0'] - 0.4 * mx - 0.05, w2['t0'] - 0.4 * mx + 0.05) if env else w2['t0'] - 0.4 * mx
            if b - a >= 0.08:
                keep = _subtract(keep, a, b)
                removed.append(dict(t0=_r(a), t1=_r(b), text=None, pause=_r(gap, 2)))
    keep = [[_r(a), _r(b)] for a, b in keep if b - a >= 0.1]
    return dict(keep=keep, removed=removed, reaction=reaction, notes=notes,
                **{'from': h_from, 'to': h_to, 'first_word': i_first, 'last_word': i_last})


def _subtract(keep, a, b):
    out = []
    for x, y in keep:
        if b <= x or a >= y:
            out.append([x, y])
            continue
        if a > x:
            out.append([x, a])
        if b < y:
            out.append([b, y])
    return out


# ============================================================================ talk video analysis (local fallback)
def _yunet(rgb):
    """YuNet faces with landmarks: [{"box": [x0, y0, x1, y1], "score", "lm": [10 floats]}] in frame px."""
    import cv2
    V = _mod('ed_video')
    h, w = rgb.shape[:2]
    det = V.face_detector(w, h)
    _, f = det.detect(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    out = []
    if f is not None:
        for row in f:
            x, y, fw, fh = [float(v) for v in row[:4]]
            out.append(dict(box=[x, y, x + fw, y + fh], score=float(row[-1]), lm=[float(v) for v in row[4:14]]))
    return out


def _rois(face):
    """Mouth and eye-band rectangles (frame px) from YuNet landmarks."""
    x0, y0, x1, y1 = face['box']
    fw, fh = x1 - x0, y1 - y0
    lm = face['lm']
    mx, my = (lm[6] + lm[8]) / 2, (lm[7] + lm[9]) / 2
    mw = max(abs(lm[8] - lm[6]) * 1.7, 0.38 * fw)
    ex, ey = (lm[0] + lm[2]) / 2, (lm[1] + lm[3]) / 2
    ew = max(abs(lm[2] - lm[0]) * 1.9, 0.6 * fw)
    mouth = [mx - mw / 2, my - 0.12 * fh, mx + mw / 2, my + 0.20 * fh]
    eyes = [ex - ew / 2, ey - 0.12 * fh, ex + ew / 2, ey + 0.10 * fh]
    return mouth, eyes


def _crop_gray(g, r, size):
    import cv2
    h, w = g.shape
    x0, y0 = int(max(0, math.floor(r[0]))), int(max(0, math.floor(r[1])))
    x1, y1 = int(min(w, math.ceil(r[2]))), int(min(h, math.ceil(r[3])))
    if x1 - x0 < 3 or y1 - y0 < 3:
        return None
    return cv2.resize(g[y0:y1, x0:x1], size, interpolation=cv2.INTER_AREA).astype(np.float32)


def _bhatt(h1, h2):
    return float(np.sqrt(max(0.0, 1.0 - np.sum(np.sqrt(h1 * h2)))))


def scan_range(path, a, b, width=1920, face_hz=6.0, keep_hz=10.0, log=None):
    """One decode pass over source [a, b] at the source frame rate: frame-exact camera cuts, faces (YuNet +
    landmarks) at ~face_hz with mouth / eye-band motion over 1/30 s, and small colour frames at ~keep_hz for the
    content box and static overlays. Times are source seconds (frame i = first + i / fps)."""
    import cv2
    info = _probe(path)
    W0, H0, fps = info['w'], info['h'], float(info['fps'] or 30.0)
    dw = int(min(width, W0) // 2 * 2)
    dh = int(round(H0 * dw / W0 / 2) * 2)
    sc = W0 / dw
    cmd = ['ffmpeg', '-v', 'error', '-nostdin', '-ss', f'{max(0.0, a):.4f}', '-i', path, '-t', f'{b - a:.4f}', '-an',
           '-vf', f'scale={dw}:{dh}:flags=area', '-fps_mode', 'passthrough', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-']
    first = math.ceil(max(0.0, a) * fps - 1e-4) / fps
    size = dw * dh * 3
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=size * 2)
    face_every = max(1, int(round(fps / face_hz)))
    keep_every = max(1, int(round(fps / keep_hz)))
    lag = max(1, int(round(fps / 30.0)))            # mouth motion over 1/30 s, sampled at ~30 Hz
    th, hists, samples, keep_t, keep_fr, motion = [], [], [], [], [], []
    grays = {}
    cur, next_tid, last_cut_k = [], 0, -10 ** 9
    k = 0
    try:
        while True:
            buf = p.stdout.read(size)
            if len(buf) < size:
                break
            fr = np.frombuffer(buf, np.uint8).reshape(dh, dw, 3)
            t = first + k / fps
            small = cv2.resize(fr, (160, 90), interpolation=cv2.INTER_AREA)
            g_small = cv2.cvtColor(small, cv2.COLOR_RGB2GRAY)
            th.append(cv2.resize(g_small, (64, 36), interpolation=cv2.INTER_AREA).astype(np.int16))
            hsv = cv2.cvtColor(small, cv2.COLOR_RGB2HSV)
            hh = cv2.calcHist([hsv], [0, 1, 2], None, [16, 4, 4], [0, 180, 0, 256, 0, 256]).flatten()
            hists.append(hh / (hh.sum() + 1e-9))
            if k and float(np.mean(np.abs(th[-1] - th[-2]))) > 18.0:
                cur, last_cut_k = [], k                     # likely a camera cut: forget the held face boxes
            if k % keep_every == 0:
                keep_t.append(t)
                keep_fr.append(cv2.resize(fr, (320, int(round(320 * dh / dw))), interpolation=cv2.INTER_AREA))
            g = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY) if (k % lag == 0 or k % face_every == 0) else None
            if k % face_every == 0:
                fs = _yunet(fr)
                s = dict(t=round(t, 4), k=k, faces=[])
                prev = cur
                cur = []
                for f in fs:
                    c = ((f['box'][0] + f['box'][2]) / 2, (f['box'][1] + f['box'][3]) / 2)
                    m = min(prev, key=lambda q: math.hypot(q['c'][0] - c[0], q['c'][1] - c[1]), default=None)
                    if m is not None and math.hypot(m['c'][0] - c[0], m['c'][1] - c[1]) < 0.08 * dw:
                        tid = m['tid']
                    else:
                        tid, next_tid = next_tid, next_tid + 1
                    mr, er = _rois(f)
                    cur.append(dict(c=c, tid=tid, mr=mr, er=er))
                    s['faces'].append(dict(box=[round(v * sc, 1) for v in f['box']], score=round(f['score'], 3),
                                           lm=[round(v * sc, 1) for v in f['lm']], tid=tid))
                samples.append(s)
            if g is not None and k % lag == 0:
                g0 = grays.pop(k - lag, None)
                if g0 is not None and cur and k - lag >= last_cut_k:
                    for q in cur:
                        m0, m1 = _crop_gray(g0, q['mr'], (32, 16)), _crop_gray(g, q['mr'], (32, 16))
                        e0, e1 = _crop_gray(g0, q['er'], (32, 12)), _crop_gray(g, q['er'], (32, 12))
                        if m0 is None or m1 is None:
                            continue
                        mm = float(np.mean(np.abs(m1 - m0)) / (np.mean(m0) + 12.0) * 100)
                        em = float(np.mean(np.abs(e1 - e0)) / (np.mean(e0) + 12.0) * 100) if e0 is not None and e1 is not None else 0.0
                        motion.append((round(t, 4), q['tid'], round(mm, 3), round(em, 3)))
                grays[k] = g
                for old in [x for x in grays if x < k - lag]:
                    grays.pop(old)
            k += 1
    finally:
        p.stdout.close()
        p.kill()
        p.wait()
    n = len(th)
    # ---- camera cuts: grey-thumbnail change AND colour-histogram change well above the local level
    pd = np.zeros(n)
    hd = np.zeros(n)
    for i in range(1, n):
        pd[i] = float(np.mean(np.abs(th[i] - th[i - 1])))
        hd[i] = _bhatt(hists[i - 1], hists[i])
    cuts = []
    if n > 3:
        med_p, mad_p = np.median(pd[1:]), np.median(np.abs(pd[1:] - np.median(pd[1:]))) + 1e-6
        med_h, mad_h = np.median(hd[1:]), np.median(np.abs(hd[1:] - np.median(hd[1:]))) + 1e-6
        cand = [i for i in range(1, n) if pd[i] > max(9.0, med_p + 8 * mad_p) and hd[i] > max(0.18, med_h + 8 * mad_h)]
        gap = max(2, int(round(0.25 * fps)))
        for i in sorted(cand, key=lambda j: -(pd[j] / (med_p + 1) + hd[j] / (med_h + 0.01))):
            if all(abs(i - c) >= gap for c in cuts):
                cuts.append(i)
        cuts.sort()
    return dict(path=path, a=round(a, 4), b=round(b, 4), first=round(first, 6), fps=fps, n=n, w=W0, h=H0,
                cuts=[round(first + i / fps, 6) for i in cuts], cut_frames=cuts, samples=samples, motion=motion,
                keep_t=[round(x, 4) for x in keep_t]), np.stack(keep_fr) if keep_fr else np.zeros((0, 1, 1, 3), np.uint8)


def _scan_cached(path, a, b, cache_dir, log):
    key = _file_key(path, f'scan{SCAN_VERSION}|{a:.3f}|{b:.3f}')
    jp = os.path.join(cache_dir, f'scan_{key}.json') if cache_dir else None
    npz = os.path.join(cache_dir, f'scan_{key}.npz') if cache_dir else None
    if jp and os.path.exists(jp) and os.path.exists(npz):
        d = _load_json(jp)
        if d:
            with np.load(npz) as z:
                return d, z['frames']
    t = time.time()
    d, frames = scan_range(path, a, b, log=log)
    log(f'[sequence] scanned {os.path.basename(path)} {a:.2f}-{b:.2f} s: {d["n"]} frames, {len(d["cuts"])} camera cuts, '
        f'{sum(len(s["faces"]) for s in d["samples"])} faces ({time.time() - t:.0f} s)')
    if jp:
        os.makedirs(cache_dir, exist_ok=True)
        np.savez_compressed(npz, frames=frames)
        _dump_json(d, jp)
    return d, frames


def content_box_local(frames, groups, W0, H0, min_area=0.12):
    """Live picture inside a screen recording: the largest region that changes over time or between shots
    (browser / player UI and letterbox bars stay constant). frames: small RGB (N, h, w, 3); groups: shot id per
    frame. -> [x0, y0, x1, y1] source px or None."""
    import cv2
    if len(frames) < 3:
        return None
    X = frames.astype(np.float32)
    h, w = X.shape[1:3]
    gray = X.mean(-1)
    # changing DETAIL, not changing light: a player's ambient glow and UI hover fades are smooth, video is not
    hp = np.stack([g - cv2.GaussianBlur(g, (0, 0), 1.5) for g in gray])
    live = hp.std(0) > 0.9
    ids = sorted(set(groups))
    if len(ids) >= 2:
        G = np.asarray(groups)
        mh = np.stack([hp[G == g].mean(0) for g in ids])
        live |= np.abs(mh - mh.mean(0)).max(0) > 0.9
    m = cv2.morphologyEx(live.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    if n <= 1:
        return None
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, bw, bh = st[i, 0], st[i, 1], st[i, 2], st[i, 3]
    if bw * bh < min_area * w * h:
        return None
    # tighten each edge to rows / columns that are mostly live (drops thin UI strips glued to the picture)
    sub = (lab[y:y + bh, x:x + bw] == i)
    rows = np.nonzero(sub.mean(1) > 0.25)[0]
    cols = np.nonzero(sub.mean(0) > 0.25)[0]
    if len(rows) and len(cols):
        y, bh = y + rows[0], rows[-1] - rows[0] + 1
        x, bw = x + cols[0], cols[-1] - cols[0] + 1
    sx, sy = W0 / w, H0 / h
    if bw >= w - 2 and bh >= h - 2:
        return [0, 0, W0, H0]
    # one analysis pixel inwards on every edge that is not the frame border (edge pixels are mixed)
    x0 = (x + 1) if x > 0 else 0
    y0 = (y + 1) if y > 0 else 0
    x1 = (x + bw - 1) if x + bw < w else w
    y1 = (y + bh - 1) if y + bh < h else h
    box = [int(round(x0 * sx)), int(round(y0 * sy)), int(round(x1 * sx)), int(round(y1 * sy))]
    return [box[0] // 2 * 2, box[1] // 2 * 2, box[2] // 2 * 2, box[3] // 2 * 2]


def static_overlays_local(frames, groups, box, W0, H0):
    """Persistent graphics inside the live picture (logo, lower third, watermark): pixels identical in every shot
    with strong edges. Needs >= 2 different shots. -> [{"box": source px, "kind": "logo"|"text"|"ui", "coverage"}]"""
    import cv2
    ids = sorted(set(groups))
    if len(frames) < 3 or len(ids) < 2 or box is None:
        return []
    X = frames.astype(np.float32)
    h, w = X.shape[1:3]
    sx, sy = W0 / w, H0 / h
    G = np.asarray(groups)
    means = np.stack([X[G == g].mean(0) for g in ids])
    shot_std = np.stack([X[G == g].std(0).max(-1) for g in ids]).max(0)
    if np.abs(means[1:] - means[:1]).max() < 8:
        return []                                              # all "shots" look alike: no evidence
    agree = (np.abs(means - means.mean(0)).max(0).max(-1) < 7.0) & (shot_std < 10.0)
    mg = means.mean(0).mean(-1).astype(np.float32)
    gx, gy = cv2.Sobel(mg, cv2.CV_32F, 1, 0), cv2.Sobel(mg, cv2.CV_32F, 0, 1)
    edges = np.hypot(gx, gy) > 60.0
    bx = [int(box[0] / sx), int(box[1] / sy), int(math.ceil(box[2] / sx)), int(math.ceil(box[3] / sy))]
    inside = np.zeros((h, w), bool)
    inside[bx[1] + 1:bx[3] - 1, bx[0] + 1:bx[2] - 1] = True
    m = (agree & edges & inside).astype(np.uint8)
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 11), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    bw_, bh_ = bx[2] - bx[0], bx[3] - bx[1]
    out = []
    for i in range(1, n):
        x, y, cw, ch, area = st[i]
        if area < 0.0006 * bw_ * bh_ or ch > 0.35 * bh_ or cw > 0.8 * bw_:
            continue
        sel = lab[y:y + ch, x:x + cw] == i
        if (edges[y:y + ch, x:x + cw] & sel).sum() < 12:
            continue
        cxr, cyr = (x + cw / 2 - bx[0]) / bw_, (y + ch / 2 - bx[1]) / bh_
        if cyr < 0.25 and (cxr < 0.25 or cxr > 0.75) and cw < 0.3 * bw_:
            kind = 'logo'
        elif cyr > 0.6 and cw > 1.5 * ch:
            kind = 'text'
        else:
            kind = 'ui'
        out.append(dict(box=[int(x * sx), int(y * sy), int(math.ceil((x + cw) * sx)), int(math.ceil((y + ch) * sy))],
                        kind=kind, coverage=1.0))
    # merge boxes of one graphic (words of a lower third, logo parts)
    out.sort(key=lambda o: (o['box'][1], o['box'][0]))
    merged = []
    for o in out:
        for m_ in merged:
            a, b = m_['box'], o['box']
            if o['kind'] == m_['kind'] and not (b[0] > a[2] + 0.05 * W0 or b[2] < a[0] - 0.05 * W0 or
                                                b[1] > a[3] + 0.02 * H0 or b[3] < a[1] - 0.02 * H0):
                m_['box'] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                break
        else:
            merged.append(o)
    return merged


def _tracks(samples, t0, t1):
    """Faces of one piece grouped by the scan's track id -> [{"tid", "cx", "h", "presence", "boxes"}]."""
    ss = [s for s in samples if t0 - 1e-6 <= s['t'] < t1]
    n = max(1, len(ss))
    by = {}
    for s in ss:
        for f in s['faces']:
            by.setdefault(f.get('tid', 0), []).append((s['t'], f))
    # one person can get several ids (occlusion by a hand, a fast turn): merge groups that sit at the same place
    groups = []
    for tid, fs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        bx = np.array([f['box'] for _, f in fs], float)
        c = np.median((bx[:, :2] + bx[:, 2:]) / 2, axis=0)
        wd = float(np.median(bx[:, 2] - bx[:, 0]))
        for g in groups:
            if math.hypot(*(g['c'] - c)) < 0.6 * max(wd, g['w']):
                g['fs'] += fs
                g['tids'].append(tid)
                break
        else:
            groups.append(dict(c=c, w=wd, fs=list(fs), tids=[tid]))
    out = []
    need = max(2, 0.25 * n) if any(len(g['fs']) >= max(2, 0.25 * n) for g in groups) else 1
    for g in groups:
        fs = sorted(g['fs'], key=lambda x: x[0])
        if len(fs) < need:
            continue
        boxes = np.array([f['box'] for _, f in fs], float)
        out.append(dict(tid=g['tids'][0], tids=g['tids'], cx=float(np.median((boxes[:, 0] + boxes[:, 2]) / 2)),
                        presence=min(1.0, len(fs) / n), h=float(np.median(boxes[:, 3] - boxes[:, 1])), boxes=boxes,
                        times=[t for t, _ in fs]))
    return out


def face_box(boxes):
    """Representative face box of a track for a static crop: median size around the 10-90 % range of centres
    (a few wild detections - a hand over the face - do not inflate it)."""
    b = np.asarray(boxes, float)
    cx, cy = (b[:, 0] + b[:, 2]) / 2, (b[:, 1] + b[:, 3]) / 2
    w, h = float(np.median(b[:, 2] - b[:, 0])), float(np.median(b[:, 3] - b[:, 1]))
    return [float(np.percentile(cx, 10)) - w / 2, float(np.percentile(cy, 10)) - h / 2,
            float(np.percentile(cx, 90)) + w / 2, float(np.percentile(cy, 90)) + h / 2]


def _av_curve(ser, env, lags):
    """Correlation of a mouth-motion series [(t, v)] with the speech envelope at each audio lag."""
    ts = np.array([t for t, _ in ser])
    x = np.convolve(np.array([v for _, v in ser]), np.ones(3) / 3, mode='same')
    if x.std() < 1e-6:
        return None
    out = []
    for lag in lags:
        a = np.array([max(0.0, env.level(t + lag - 0.02, t + lag + 0.02) - env.floor) for t in ts])
        out.append(float(np.corrcoef(x, a)[0, 1]) if a.std() > 1e-6 else 0.0)
    return np.array(out)


AV_LAGS = np.round(np.arange(0.0, 0.42, 0.02), 3)


def _lag_estimate(pieces_tracks, motion_of, env):
    """Summed mouth-motion / speech-envelope correlation over the pieces with a single face -> {"lag" (s, peak with
    parabolic refinement), "r" (peak), "r0" (at the natural lead), "n" (motion samples), "pieces"} | None"""
    acc, n, used = np.zeros(len(AV_LAGS)), 0, 0
    for (t0, t1, trs), mot in zip(pieces_tracks, motion_of):
        if len(trs) != 1:
            continue
        ser = [(t, mm - 0.5 * em) for t, tid, mm, em in mot if tid in trs[0]['tids'] and t0 <= t < t1]
        if len(ser) < 30:
            continue
        cv = _av_curve(ser, env, AV_LAGS)
        if cv is None or cv.max() < 0.3:
            continue
        acc += cv * len(ser)
        n += len(ser)
        used += 1
    if not n:
        return None
    c = acc / n
    i = int(np.argmax(c))
    lag = float(AV_LAGS[i])
    if 0 < i < len(c) - 1:                                   # sub-step peak
        den = c[i - 1] - 2 * c[i] + c[i + 1]
        if den < -1e-9:
            lag += float(np.clip(0.5 * (c[i - 1] - c[i + 1]) / den, -0.5, 0.5)) * float(AV_LAGS[1] - AV_LAGS[0])
    j = int(np.argmin(np.abs(AV_LAGS - NATURAL_LEAD)))
    return dict(lag=round(lag, 3), r=round(float(c[i]), 3), r0=round(float(c[j]), 3), n=int(n), pieces=used)


def av_lag(pieces_tracks, motion_of, env):
    """Audio-vs-picture lag of a source (mouth motion leads its sound by ~0.05-0.1 s; screen recordings add their
    own delay) from pieces with a single speaking face: argmax of the summed correlation curves. -> (lag, r) | None"""
    e = _lag_estimate(pieces_tracks, motion_of, env)
    return None if e is None else (e['lag'], e['r'])


NATURAL_LEAD = 0.08        # s: in any recording the sound of a word follows the mouth opening by ~0.05-0.1 s
AV_MIN_R = 0.35            # peak correlation needed to trust a measured lag ...
AV_MIN_N = 120             # ... over this many mouth-motion samples (~4 s of one speaking face) ...
AV_MIN_GAIN = 0.05         # ... with the peak clearly above the correlation at the natural lead


def _av_decision(est, fps_out=30):
    """Measured lag -> {"offset" (s the picture is taken earlier; 0 = keep), "lag", "r", "confident", "why"}: the
    offset is the lag minus the natural lead, applied only when the estimate is confident and the result is at least
    2 output frames."""
    if est is None:
        return dict(offset=0.0, lag=None, r=None, n=0, confident=False, why='no single speaking face long enough')
    off = round(max(0.0, est['lag'] - NATURAL_LEAD), 3)
    conf = est['r'] >= AV_MIN_R and est['n'] >= AV_MIN_N and est['r'] - est['r0'] >= AV_MIN_GAIN
    why = (f'mouth/speech sync r={est["r"]:.2f} at {est["lag"]:.2f} s (r={est["r0"]:.2f} at the natural '
           f'{NATURAL_LEAD:.2f} s lead, {est["n"]} samples)')
    if not conf:
        return dict(est, offset=0.0, measured=off, confident=False, why='not confident: ' + why)
    if off < 2.0 / fps_out - 1e-9:
        return dict(est, offset=0.0, measured=off, confident=True, why='in sync (under 2 frames): ' + why)
    return dict(est, offset=off, measured=off, confident=True, why=why)


def estimate_av_offset(video, t0, t1, cache_dir=None, fps_out=30, log=None):
    """Lip sync of any file - a source or a render - over [t0, t1] s: how much its audio lags the picture, from the
    mouth motion of single speaking faces against the speech envelope (one cached decode pass).
    -> {"offset" (s to take the picture earlier; 0 when in sync, not confident or under 2 output frames),
        "measured" (lag - natural lead), "lag" (raw mouth -> sound lag), "r", "r0", "n", "confident", "why"}"""
    log = log or (lambda *a, **k: None)
    info = _probe(video)
    dur = float(info.get('duration') or t1)
    t0, t1 = max(0.0, float(t0)), min(float(t1), dur)
    d, _ = _scan_cached(video, t0, t1, cache_dir, log)
    env = Envelope(video, max(0.0, t0 - 0.5), t1 + 0.5) if info.get('has_audio', True) else None
    if env is None:
        return _av_decision(None, fps_out)
    bounds = [t0] + [c for c in d['cuts'] if t0 + 0.04 < c < t1 - 0.04] + [t1]
    pt = [(a, b, _tracks(d['samples'], a, b)) for a, b in zip(bounds, bounds[1:])]
    return _av_decision(_lag_estimate(pt, [d.get('motion') or []] * len(pt), env), fps_out)


def pick_speaker(tracks, motion, env, t0, t1, lag=None):
    """Active speaker among the faces of a piece: correlation of mouth motion (minus head motion, ~30 Hz) with the
    speech envelope, read at the source's audio lag (+-0.06 s; any lag 0-0.4 s when unknown). A single face, or
    no clear evidence, -> the most present / largest face. -> (track, why)"""
    if not tracks:
        return None, 'no face'
    if len(tracks) == 1:
        return tracks[0], 'single face'
    win = (AV_LAGS >= lag - 0.061) & (AV_LAGS <= lag + 0.061) if lag is not None else np.ones(len(AV_LAGS), bool)
    scores = []
    for tr in tracks:
        ser = [(t, mm - 0.5 * em) for t, tid, mm, em in motion if tid in tr.get('tids', [tr['tid']]) and t0 <= t < t1]
        cv = _av_curve(ser, env, AV_LAGS) if len(ser) >= 20 and env is not None else None
        scores.append((None if cv is None else float(cv[win].max()), tr))
    ok = sorted([s for s in scores if s[0] is not None], key=lambda s: -s[0])
    if len(ok) >= 2 and ok[0][0] >= 0.15 and ok[0][0] - ok[1][0] >= 0.08:
        return ok[0][1], f'mouth-speech sync r={ok[0][0]:.2f} vs {ok[1][0]:.2f}'
    best = max(tracks, key=lambda tr: tr['presence'] * tr['h'])
    return best, 'largest face (no clear speaker' + (f', r={ok[0][0]:.2f}/{ok[1][0]:.2f})' if len(ok) >= 2 else ')')


def solve_crop(Bw, Bh, face, avoid, aspect, z_lo=1.0, z_hi=1.45, fy_t=0.37, face_frac=0.17, margins=None):
    """Static 9:16 (any aspect) window inside a Bw x Bh picture: the face box (picture px; None = centre) whole,
    with head room and side margins, its centre near (0.5, fy_t) of the frame; no avoid box (picture px) inside the
    window; zoom z (window height = Bh / z) close to the one that makes the face ~face_frac of the frame height.
    -> {"cx", "cy", "z"} fractions of the picture, or None when nothing fits."""
    mg = dict(side=0.06, top=0.04, bottom=0.40)
    mg.update(margins or {})
    best = None
    if face is not None:
        fh = max(1.0, face[3] - face[1])
        hx0, hx1 = face[0] - 0.12 * (face[2] - face[0]), face[2] + 0.12 * (face[2] - face[0])
        hy0, hy1 = max(0.0, face[1] - 0.32 * fh), face[3] + 0.08 * fh
        fcx, fcy = (face[0] + face[2]) / 2, (face[1] + face[3]) / 2
        z_pref = min(z_hi, max(z_lo, face_frac * Bh / fh))
    else:
        fcx, fcy, z_pref = Bw / 2, Bh / 2, z_lo
    for z in np.arange(z_lo, z_hi + 1e-9, 0.02):
        hw = Bh / z
        ww = hw * aspect
        if ww > Bw:
            continue
        step = max(4.0, ww / 150)
        cxs = np.arange(ww / 2, Bw - ww / 2 + 1e-6, step) if Bw - ww > 1 else np.array([Bw / 2])
        cys = np.arange(hw / 2, Bh - hw / 2 + 1e-6, step) if Bh - hw > 1 else np.array([Bh / 2])
        CX, CY = np.meshgrid(cxs, cys)
        L, R, T, B = CX - ww / 2, CX + ww / 2, CY - hw / 2, CY + hw / 2
        ok = np.ones(CX.shape, bool)
        if face is not None:
            ok &= (hx0 >= L + mg['side'] * ww) & (hx1 <= R - mg['side'] * ww)
            ok &= ((hy0 >= T + mg['top'] * hw) | (T <= 1.0)) & (hy1 <= B - mg['bottom'] * hw)   # head at the top edge
        for a in avoid:
            ok &= (R <= a[0]) | (L >= a[2]) | (B <= a[1]) | (T >= a[3])
        if not ok.any():
            continue
        if face is not None:
            fx, fy = (fcx - L) / ww, (fcy - T) / hw
            cost = ((fx - 0.5) / 0.10) ** 2 + ((fy - fy_t) / 0.08) ** 2 + ((z - z_pref) / 0.25) ** 2
        else:
            cost = ((CX - fcx) / Bw / 0.1) ** 2 + ((CY - fcy) / Bh / 0.1) ** 2 + ((z - z_pref) / 0.25) ** 2
        cost = np.where(ok, cost, np.inf)
        j = np.unravel_index(int(np.argmin(cost)), cost.shape)
        if best is None or cost[j] < best[0]:
            best = (float(cost[j]), float(CX[j]), float(CY[j]), float(z))
    if best is None:
        return None
    return dict(cx=round(best[1] / Bw, 4), cy=round(best[2] / Bh, 4), z=round(best[3], 3))


def _crop_with_relax(Bw, Bh, face, avoid, aspect, z_hi):
    """solve_crop with progressively relaxed constraints -> (crop, how)."""
    hard = [a for a in avoid if a[4] in ('logo', 'text', 'spec')]
    steps = [(avoid, None, 'ok'), (avoid, dict(side=0.02, top=0.02, bottom=0.28), 'tight margins'),
             (hard, dict(side=0.02, top=0.02, bottom=0.28), 'ui overlap allowed'),
             (hard, dict(side=0.0, top=0.0, bottom=0.12), 'minimal margins'),
             (hard, dict(side=-0.15, top=-0.25, bottom=0.0), 'face slightly cut, overlays kept out')]
    for av, mg, how in steps:
        c = solve_crop(Bw, Bh, face, [a[:4] for a in av], aspect, z_hi=z_hi, margins=mg)
        if c is not None:
            return c, how
    if face is not None:                                 # keep the overlays out, aim at the face only
        c = solve_crop(Bw, Bh, None, [a[:4] for a in hard], aspect, z_hi=z_hi)
        if c is not None:
            return c, 'overlays kept out, face not framed'
    c = solve_crop(Bw, Bh, face, [], aspect, z_hi=z_hi, margins=dict(side=0.0, top=0.0, bottom=0.1))
    return (c or dict(cx=0.5, cy=0.5, z=1.0)), 'overlays could not be avoided'


def _window_px(c, Bw, Bh, aspect):
    hw = Bh / c['z']
    ww = hw * aspect
    cx = min(max(c['cx'] * Bw, ww / 2), Bw - ww / 2)
    cy = min(max(c['cy'] * Bh, hw / 2), Bh - hw / 2)
    return [cx - ww / 2, cy - hw / 2, cx + ww / 2, cy + hw / 2]


def _push(c, face, Bw, Bh, aspect, amount=1.07):
    """Zoom a crop by `amount` about the face (the eye line when known): the face keeps its place on screen and the
    tighter window stays inside the old one, so it still misses every avoided overlay. No face: about the centre."""
    x0, y0, x1, y1 = _window_px(c, Bw, Bh, aspect)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if face is not None:
        fx = min(max((face[0] + face[2]) / 2, x0), x1)
        fy = min(max(face[1] + 0.40 * (face[3] - face[1]), y0), y1)        # roughly the eye line
        cx, cy = fx + (cx - fx) / amount, fy + (cy - fy) / amount
    return dict(cx=round(cx / Bw, 4), cy=round(cy / Bh, 4), z=round(c['z'] * amount, 3))


def _fit_path(crop, m):
    """A crop path inside a segment of m frames: piece lengths come from times, the frame-exact segment can be a
    frame shorter, so keys past its last frame are dropped and the state on that frame is interpolated."""
    path = crop.get('path')
    if not path or m < 1:
        return crop
    last = m - 1
    keep = [list(k) for k in path if int(k[0]) <= last]
    nxt = next((k for k in path if int(k[0]) > last), None)
    if nxt is not None:
        if keep and keep[-1][0] < last:
            prv = keep[-1]
            u = (last - prv[0]) / max(1e-9, nxt[0] - prv[0])
            keep.append([last] + [round(prv[i] + (nxt[i] - prv[i]) * u, 4) for i in (1, 2, 3)])
        elif not keep:
            keep = [[0] + list(nxt[1:4])]
    out = dict(crop, path=keep)
    out['cx'], out['cy'], out['z'] = keep[0][1], keep[0][2], keep[0][3]
    return out


def _rebase_path(path, off, n):
    """Crop path keys [[k, cx, cy, z], ...] of a piece -> the same motion for a sub-range starting off frames later
    and n frames long (keys at its first / last frame plus the original keys inside)."""
    ks = np.array([p[0] for p in path], float)
    cols = [np.array([p[j] for p in path], float) for j in (1, 2, 3)]
    pts = sorted({0, n - 1} | {int(k - off) for k in ks if 0 < k - off < n - 1})
    return [[int(k)] + [round(float(np.interp(k + off, ks, c)), 4) for c in cols] for k in pts]


def scale_crop(crop, amount, face, Bw, Bh, aspect, n=None, ease=None):
    """A tighter version of a crop that stays inside the original window (so it still misses every overlay):
    static crops move towards the face (_push); path crops are zoomed about every key. With ease and n the zoom
    grows from 1 to `amount` over the n frames of the segment (a slow push-in on a moving crop)."""
    if not crop.get('path'):
        return _push(crop, face, Bw, Bh, aspect, amount)
    out = dict(crop)
    keys = []
    for k, cx, cy, z in crop['path']:
        u = _ease(k / max(1, (n or 1) - 1), ease) if ease else 1.0
        keys.append([int(k), cx, cy, round(z * (1 + (amount - 1) * u), 4)])
    out['path'] = keys
    out['z'] = keys[0][3]
    out.pop('to', None)
    return out


def _shot_ids(pieces, frames_of):
    """Pieces that show the same camera set-up (a removal inside one shot) share a shot id."""
    reps, ids = [], []
    for pc in pieces:
        fr = frames_of(pc)
        m = fr.astype(np.float32).mean(0).mean(-1) if len(fr) else None
        sid = None
        if m is not None:
            for j, r in enumerate(reps):
                if r is not None and float(np.mean(np.abs(m - r))) < 12.0:
                    sid = j
                    break
        if sid is None:
            sid = len(reps)
            reps.append(m)
        ids.append(sid)
    return ids


def talk_layout(part, keep, words, env, canvas, cache_dir, log=print, scans=None, lag=None, windows=None):
    """Vertical layout of a talk / clip part: pieces = kept ranges split at camera cuts, each with a crop that
    frames the active speaker and keeps static overlays (logo, lower third, player UI) out. keep = PICTURE time
    ranges; scans / windows = the cached scans around them (wider source windows that do not depend on an A/V
    offset), lag = the source's measured mouth -> sound lag (s) for the speaker pick.
    -> {"box", "avoid", "pieces": [{"t0", "t1", "shot", "crop", "face", "speaker", "why"}], "by", "notes"}"""
    path = part['source']
    info = _probe(path)
    W0, H0 = info['w'], info['h']
    aspect = canvas['w'] / canvas['h']
    mode = part.get('crop', 'speaker')
    notes = []
    if isinstance(mode, dict) or mode in ('center', 'centre', 'none'):     # fixed crop: no video analysis
        crop = dict(mode) if isinstance(mode, dict) else dict(cx=0.5, cy=0.5, z=1.0)
        box = part.get('box') or [0, 0, W0, H0]
        return dict(box=box, avoid=[], by='spec' if isinstance(mode, dict) else 'centre', notes=notes,
                    by_box='spec' if part.get('box') else 'full frame', by_avoid='none',
                    Bw=box[2] - box[0], Bh=box[3] - box[1], aspect=aspect,
                    pieces=[dict(t0=a, t1=b, shot=0, crop=dict(crop), face=None, speaker=None, why='fixed crop')
                            for a, b in keep])
    windows = windows or [list(r) for r in keep]
    scans = scans or [_scan_cached(path, a, b, cache_dir, log) for a, b in windows]
    pieces = []
    for si, ((d, fr), (a, b)) in enumerate(zip(scans, keep)):
        cuts = [c for c in d['cuts'] if a + 0.04 < c < b - 0.04]
        bounds = [a] + cuts + [b]
        for x, y in zip(bounds, bounds[1:]):
            pieces.append(dict(t0=float(x), t1=float(y), scan=si, cut_in=(x in cuts)))

    def frames_of(pc):
        d, fr = scans[pc['scan']]
        sel = [i for i, t in enumerate(d['keep_t']) if pc['t0'] + 0.03 <= t < pc['t1'] - 0.03]
        return fr[sel] if sel else fr[:0]
    sids = _shot_ids(pieces, frames_of)
    for pc, sid in zip(pieces, sids):
        pc['shot'] = sid
    frames = [frames_of(pc) for pc in pieces]
    groups = [pc['shot'] for pc, f in zip(pieces, frames) for _ in range(len(f))]
    allf = np.concatenate([f for f in frames if len(f)]) if any(len(f) for f in frames) else np.zeros((0, 1, 1, 3))
    # ---- live picture box and static overlays (talk agent's ed_video first, then the local detectors)
    box, by_box = part.get('box'), 'spec'
    t_lo, t_hi = windows[0][0], windows[-1][1]                    # the scan windows: no re-analysis per offset
    if box is None:
        f = _fn('ed_video', 'content_box')
        if f is not None:
            try:
                box, by_box = [int(v) for v in f(path, t_lo, t_hi)], 'ed_video'
            except Exception as e:  # noqa: BLE001
                notes.append(f'ed_video.content_box failed: {e}')
                box = None
        if box is None:
            box, by_box = content_box_local(allf, groups, W0, H0), 'local'
        if box is None:
            box, by_box = [0, 0, W0, H0], 'full frame'
    if box[2] - box[0] > 0.985 * W0 and box[3] - box[1] > 0.985 * H0:
        box = [0, 0, W0, H0]
    avoid, by_avoid = None, 'spec'
    if part.get('avoid') is not None:
        avoid = [dict(box=list(a), kind='spec') if not isinstance(a, dict) else a for a in part['avoid']]
    else:
        f = _fn('ed_video', 'static_overlays')
        if f is not None:
            try:
                avoid, by_avoid = list(f(path, box, t_lo, t_hi)), 'ed_video'
            except Exception as e:  # noqa: BLE001
                notes.append(f'ed_video.static_overlays failed: {e}')
        if avoid is None:
            avoid, by_avoid = static_overlays_local(allf, groups, box, W0, H0), 'local'
    Bw, Bh = box[2] - box[0], box[3] - box[1]
    mgn = 0.012 * Bh
    av_box = [[a['box'][0] - box[0] - mgn, a['box'][1] - box[1] - mgn, a['box'][2] - box[0] + mgn,
               a['box'][3] - box[1] + mgn, a.get('kind', 'ui')] for a in avoid]
    pop_spans = [[(float(x), float(y)) for x, y in (a.get('spans') or [])] if a.get('kind') == 'popup' else None
                 for a in avoid]

    def active(t0, t1):
        """Indices of the avoid boxes on screen during [t0, t1]: a popup only inside its spans."""
        return tuple(i for i, sp_ in enumerate(pop_spans) if sp_ is None or any(x < t1 and y > t0 for x, y in sp_))
    z_hi = float(part.get('max_zoom', 1.45))
    sc_ = {}
    # ---- local speaker crops for every piece (also the yardstick for ed_reframe.speaker_crop's result)
    ptracks = [(pc['t0'], pc['t1'], _tracks(scans[pc['scan']][0]['samples'], pc['t0'], pc['t1'])) for pc in pieces]
    if lag is None and env is not None:
        lag = av_lag(ptracks, [scans[pc['scan']][0].get('motion') or [] for pc in pieces], env)
    elif isinstance(lag, (int, float)):
        lag = (float(lag), None)

    def local(pc, trs):
        d, _ = scans[pc['scan']]
        tr, why = pick_speaker(trs, d.get('motion') or [], env, pc['t0'], pc['t1'],
                               lag=None if lag is None else lag[0]) if trs else (None, 'no face')
        face = None
        if tr is not None:
            fb = face_box(tr['boxes'])
            face = [fb[0] - box[0], fb[1] - box[1], fb[2] - box[0], fb[3] - box[1]]
        on = active(pc['t0'], pc['t1'])
        key = (pc['shot'], None if tr is None else round(tr['cx'] / (0.05 * W0)), on)
        if key in sc_:                                   # same shot + same person (+ same popups): same framing
            crop, how = sc_[key]
        else:
            crop, how = _crop_with_relax(Bw, Bh, face, [av_box[i] for i in on], aspect, z_hi)
            sc_[key] = (crop, how)
        return dict(crop=dict(crop), face=face, speaker=None if tr is None else dict(tid=tr['tid'], cx=round(tr['cx'], 1)),
                    why=f'{why}; {how}')
    for pc, (_, _, trs) in zip(pieces, ptracks):
        pc.update(local(pc, trs))
    by = 'local'
    # ---- ed_reframe.speaker_crop (talk agent) when available: its framing is used where it passes two checks -
    # piece boundaries on the frame-exact camera cuts of the scan, and no window over a logo / caption / overlay
    sp = _fn('ed_reframe', 'speaker_crop') if mode == 'speaker' else None
    if sp is not None:
        try:
            hard = [(i, [a[0] + mgn, a[1] + mgn, a[2] - mgn, a[3] - mgn, a[4]]) for i, a in enumerate(av_box)
                    if a[4] in ('logo', 'text', 'spec', 'popup') or (a[2] - a[0]) * (a[3] - a[1]) < 0.15 * Bw * Bh]
            cuts = sorted(c for d, _ in scans for c in d['cuts'])
            out, fixed, snapped = [], 0, 0
            for (a, b), (wa, wb) in zip(keep, windows):
                its = [dict(it) for it in sp(path, wa, wb, box=box,       # popups: checked below, inside their spans
                                             avoid=[a_['box'] for a_ in avoid if a_.get('kind') != 'popup'],
                                             canvas=(canvas['w'], canvas['h']), fps=canvas['fps'], words=words)]
                for it in its:                               # the window's items clipped to this picture range
                    it['t0'], it['t1'] = max(float(it['t0']), a), min(float(it['t1']), b)
                its = [it for it in its if float(it['t1']) > float(it['t0']) + 1e-3 and 'crop' in it]
                if not its:
                    raise ValueError('no items')
                its[0]['t0'], its[-1]['t1'] = a, b
                for x, y in zip(its, its[1:]):
                    t = float(y['t0'])
                    c = min(cuts, key=lambda c_: abs(c_ - t), default=None)
                    if c is not None and abs(c - t) <= 0.25 and a < c < b and abs(c - t) > 1e-3:
                        x['t1'] = y['t0'] = c
                        snapped += 1
                for it in its:
                    c = dict(it['crop'])
                    wins = [_window_px(c, Bw, Bh, aspect)]
                    if isinstance(c.get('to'), dict):
                        wins.append(_window_px(dict(c, **c['to']), Bw, Bh, aspect))
                    for key_ in c.get('path') or []:
                        wins.append(_window_px(dict(cx=key_[1], cy=key_[2], z=key_[3]), Bw, Bh, aspect))
                    on = set(active(float(it['t0']), float(it['t1'])))
                    bad = [h for i_, h in hard if i_ in on for w in wins
                           if not (w[2] <= h[0] or w[0] >= h[2] or w[3] <= h[1] or w[1] >= h[3])]
                    mid = (float(it['t0']) + float(it['t1'])) / 2
                    mine = next((pc for pc in pieces if pc['t0'] <= mid < pc['t1']), None)
                    pc_out = dict(t0=float(it['t0']), t1=float(it['t1']), shot=it.get('shot', (mine or {}).get('shot')),
                                  crop=c, face=(mine or {}).get('face'), speaker=it.get('speaker'),
                                  why=str(it.get('why') or 'speaker_crop'))
                    if bad and mine is not None:
                        pc_out.update(crop=dict(mine['crop']), speaker=mine.get('speaker'),
                                      why=f'local ({mine["why"]}): speaker_crop window covered a {bad[0][4]} overlay')
                        fixed += 1
                    out.append(pc_out)
            by = 'ed_reframe.speaker_crop'
            if snapped or fixed:
                notes.append(f'speaker_crop: {snapped} boundary(ies) moved onto the frame-exact camera cut, '
                             f'{fixed} crop(s) replaced (window over an overlay)')
            return dict(box=box, avoid=avoid, pieces=out, by=by, by_box=by_box, by_avoid=by_avoid, notes=notes,
                        Bw=Bw, Bh=Bh, aspect=aspect, local=[{k: v for k, v in pc.items() if k != 'scan'} for pc in pieces])
        except Exception as e:  # noqa: BLE001
            notes.append(f'ed_reframe.speaker_crop failed ({type(e).__name__}: {e}); local speaker crop')
    return dict(box=box, avoid=avoid, pieces=[{k: v for k, v in pc.items() if k != 'scan'} for pc in pieces],
                by=by, by_box=by_box, by_avoid=by_avoid, notes=notes, Bw=Bw, Bh=Bh, aspect=aspect)


# ============================================================================ music
def _plain(x):
    """numpy scalars / arrays inside dicts and lists -> plain Python (JSON-safe)."""
    def d(o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o).__name__)
    return json.loads(json.dumps(x, default=d))


def analyze_music(path, cache_dir=None, log=print):
    """Track analysis (ed_plan.analyze_music: beats, downbeats, bars with loudness, sections, drops, per-beat kick
    strength; cached) or ed_audio.analyze as the fallback."""
    f = _fn('ed_plan', 'analyze_music')
    if f is not None:
        try:
            return _plain(f(path, cache_dir))
        except Exception as e:  # noqa: BLE001
            log(f'[sequence] ed_plan.analyze_music failed ({type(e).__name__}: {e}); using ed_audio.analyze')
    A = _mod('ed_audio')
    if A is None:
        raise SpecError('music analysis needs engine/ed_audio.py')
    cp = os.path.join(cache_dir, f'music_{_file_key(path, "seq1")}.json') if cache_dir else None
    if cp and os.path.exists(cp):
        d = _load_json(cp)
        if d:
            return d
    d = _plain(A.analyze(path))
    if cp:
        os.makedirs(cache_dir, exist_ok=True)
        _dump_json(d, cp)
    return d


class Beats:
    """Beat grid of the whole track, extended by the median period before the first and after the last tracked
    beat; j indexes beats, downbeats are every 4th beat from the analysed phase."""

    def __init__(self, mus):
        b = np.asarray(mus['beats'], float)
        p = float(np.median(np.diff(b))) if len(b) > 2 else 60.0 / float(mus['bpm'])
        pre, t = [], b[0] - p
        while t > -8 * p:
            pre.insert(0, t)
            t -= p
        post, t = [], b[-1] + p
        while t < float(mus['duration']) + 32 * p:
            post.append(t)
            t += p
        self.t = np.concatenate([pre, b, post])
        self.period = p
        self.duration = float(mus['duration'])
        d0 = (mus.get('downbeats') or [b[0]])[0]
        self.phase = int(np.argmin(np.abs(self.t - d0))) % 4

    def index(self, t):
        return int(np.argmin(np.abs(self.t - t)))

    def is_down(self, j):
        return (j - self.phase) % 4 == 0

    def next_down(self, t, tol=0.04):
        j = int(np.searchsorted(self.t, t - tol))
        while not self.is_down(j):
            j += 1
        return j

    def time(self, j):
        j = int(j)
        if j < len(self.t):
            return float(self.t[j])
        return float(self.t[-1] + (j - len(self.t) + 1) * self.period)


def pick_drop(mus, need_after=0.0, given=None):
    """Track second of the strongest drop / downbeat: start of the most energetic section, a detected drop, the
    loudness and low-end jump over the two bars before, the kick on it; it must leave `need_after` seconds of track.
    -> (t, why, top candidates)"""
    if given is not None:
        return float(given), 'given in the spec', []
    bars = mus.get('bars') or []
    dur = float(mus['duration'])
    secs = mus.get('sections') or []
    top = max((float(s.get('energy', 0)) for s in secs), default=None)
    drops = [float(d['t'] if isinstance(d, dict) else d) for d in mus.get('drops') or []]
    beats = np.asarray(mus.get('beats') or [], float)
    kick = mus.get('beat_kick') or []
    bar_s = 4 * 60.0 / float(mus['bpm'])
    cands = []
    for i, bar in enumerate(bars):
        t = float(bar['t0'])
        if i < 1 or t + need_after > dur + 0.05:
            continue
        prev = bars[max(0, i - 2):i]
        jump = float(bar.get('rms_db', 0)) - float(np.mean([float(x.get('rms_db', 0)) for x in prev]))
        low = float(bar.get('low_db', 0)) - float(np.mean([float(x.get('low_db', 0)) for x in prev]))
        sec = next((s for s in secs if abs(float(s['t0']) - t) < 0.12), None)
        why = []
        s_b = 0.0
        if sec is not None:
            e = float(sec.get('energy', 0))
            s_b = 3.0 if top is not None and e >= top - 1e-6 else 1.0 + e
            why.append(f'start of the {"most energetic" if s_b == 3.0 else sec.get("label", "")} section')
        d_b = 3.0 if any(abs(x - t) < 0.15 for x in drops) else 0.0
        if d_b:
            why.append('detected drop')
        k_b = 0.5 * float(kick[int(np.argmin(np.abs(beats - t)))]) if len(kick) == len(beats) and len(beats) else 0.0
        score = s_b + d_b + 0.35 * jump + 0.12 * low + k_b - (1.0 if t < 2 * bar_s else 0.0)
        why.append(f'{jump:+.1f} dB loudness, {low:+.1f} dB low end vs the 2 bars before')
        cands.append((round(score, 3), round(t, 4), '; '.join(why)))
    if not cands:
        t = float((mus.get('downbeats') or mus.get('beats') or [0.0])[0])
        return t, 'no bar fits: first downbeat', []
    cands.sort(key=lambda c: -c[0])
    if any(x + need_after <= dur + 0.05 for x in drops):
        return cands[0][1], cands[0][2], cands[:5]
    # no clear drop: the strongest energy jump - a bass or loudness rise on a downbeat - into music as energetic as
    # the edit needs (energy = loudness + a quarter of the low end, over the bars the edit uses: within 1.5 dB of
    # the most energetic stretch of that length - an intro's bass entry does not carry a hype edit)
    rows = []
    for i, bar in enumerate(bars):
        t = float(bar['t0'])
        if i < 1 or t + need_after > dur + 0.05:
            continue
        prev = bars[max(0, i - 2):i]
        jump = float(bar.get('rms_db', 0)) - float(np.mean([float(x.get('rms_db', 0)) for x in prev]))
        low = float(bar.get('low_db', 0)) - float(np.mean([float(x.get('low_db', 0)) for x in prev]))
        win = [float(x.get('rms_db', 0)) + 0.25 * float(x.get('low_db', 0)) for x in bars
               if t - 1e-3 <= float(x['t0']) < t + max(need_after, bar_s)]
        rows.append((t, max(jump, 0.8 * low), jump, low, float(np.mean(win)) if win else -99.0))
    if not rows:
        return cands[0][1], cands[0][2], cands[:5]
    top = max(r[4] for r in rows)
    fit = sorted([r for r in rows if r[4] >= top - 1.5], key=lambda r: (-r[1], -r[4]))
    t, rise, jump, low, _ = fit[0]
    what = f'+{low:.1f} dB in the low end' if 0.8 * low >= jump else f'+{jump:.1f} dB louder'
    why = (f'{NO_DROP}; the switch lands on the biggest energy jump at {_mmss(t)} ({what}). '
           f'For a harder hit, pick another section or track.')
    return round(t, 4), why, [(round(r[1], 2), round(r[0], 4), f'{r[2]:+.1f} dB loudness, {r[3]:+.1f} dB low end')
                              for r in fit[:5]]


NO_DROP = 'no clear drop in this track'


def _mmss(t):
    return f'{int(t // 60)}:{t % 60:04.1f}'


# ============================================================================ building blocks
class _Ctx:
    def __init__(self, S, cache_dir, log):
        self.S, self.cache_dir, self.log = S, cache_dir, log
        self.canvas = S['canvas']
        self.fps = S['canvas']['fps']
        self.W, self.H = S['canvas']['w'], S['canvas']['h']
        self.sources = {}
        self.counters = {}
        self.notes = []

    def seg_id(self, prefix):
        self.counters[prefix] = self.counters.get(prefix, 0) + 1
        return f'{prefix}{self.counters[prefix]:02d}'

    def source(self, name, cfg):
        base, k = re.sub(r'[^A-Za-z0-9_]+', '_', name).strip('_') or 'src', 1
        nm = base
        while nm in self.sources and self.sources[nm]['path'] != cfg['path']:
            k += 1
            nm = f'{base}_{k}'
        if nm not in self.sources:
            self.sources[nm] = dict(cfg)
        return nm


def _part_out(**kw):
    out = dict(segments=[], voice=[], layers=[], sfx=[], ops=[], music_fx=[], duck=[], words=[], meta={},
               planned_white=[], planned_black=[], has_voice=False)
    out.update(kw)
    return out


# ============================================================================ talk / clip parts
SCAN_PAD = (0.5, 0.1)      # s scanned before / after a kept range: the picture of any A/V offset up to 0.45 s
                           # lies inside, so a changed (or measured) offset never re-scans the source
EDGE_MIN_S = 0.5           # no piece shorter than this at the edge of a kept range (a sliver of the other camera)


def _scan_windows(keep, off, dur=None):
    """Source windows scanned around kept (audio-time) ranges - the same for every A/V offset up to 0.45 s."""
    pre, post = max(SCAN_PAD[0], off + 0.05), max(SCAN_PAD[1], 0.05 - off)
    out = []
    for a, b in keep:
        wa, wb = max(0.0, round(a - pre, 2)), round(b + post, 2)
        out.append([wa, min(wb, float(dur)) if dur else wb])
    return out


def _lag_from_scans(scans, windows, env):
    """Mouth -> sound lag of a source from its scans (each window split at its camera cuts)."""
    pt, mo = [], []
    for (d, _), (wa, wb) in zip(scans, windows):
        bounds = [wa] + [c for c in d['cuts'] if wa + 0.04 < c < wb - 0.04] + [wb]
        for a, b in zip(bounds, bounds[1:]):
            pt.append((a, b, _tracks(d['samples'], a, b)))
            mo.append(d.get('motion') or [])
    return _lag_estimate(pt, mo, env)


def _start_hidden(scans, windows, t_pic, avoid, H0, dur=0.5):
    """Why the picture at the start of a talk part (picture time t_pic .. + dur) is no clean start - a transient
    overlay ("popup" spans from ed_video.static_overlays) over a face, or no speaking-size face on screen (a face
    hidden under a pop-up window leaves at most icon-size detections) - else None."""
    ss = []
    for (d, _), (wa, wb) in zip(scans, windows):
        if wa - 1e-6 <= t_pic < wb:
            ss = [x for x in d['samples'] if t_pic - 1e-6 <= x['t'] < t_pic + dur]
            break
    if len(ss) < 2:
        return None
    for o in avoid or []:
        if o.get('kind') != 'popup' or not any(a < t_pic + dur and b > t_pic for a, b in o.get('spans') or []):
            continue
        ob = o.get('box') or [0, 0, 0, 0]
        if any(not (f['box'][2] <= ob[0] or f['box'][0] >= ob[2] or f['box'][3] <= ob[1] or f['box'][1] >= ob[3])
               for x in ss for f in x['faces']) or not any(x['faces'] for x in ss):
            return 'a pop-up covers the face'
    big = sum(1 for x in ss if any(f['box'][3] - f['box'][1] >= 0.05 * H0 for f in x['faces']))
    if big < 0.6 * len(ss):
        return 'no face on screen (covered or turned away)'
    return None


def _scans_for(keep, off, windows, scans, path, dur, cache_dir, log):
    """The scan (and its window) holding each picture range of keep (audio time - off); a range outside every
    window gets its own scan."""
    out_s, out_w = [], []
    for a, b in keep:
        pa, pb = a - off, b - off
        j = next((j for j, (wa, wb) in enumerate(windows) if wa - 1e-6 <= pa and pb <= wb + 1e-6), None)
        if j is None:
            windows.append(_scan_windows([[a, b]], off, dur)[0])
            scans.append(_scan_cached(path, windows[-1][0], windows[-1][1], cache_dir, log))
            j = len(windows) - 1
        out_s.append(scans[j])
        out_w.append(windows[j])
    return out_s, out_w


def _fix_edges(rr, pieces, words, off, sfps):
    """A camera cut just inside a kept range would leave a sliver (< EDGE_MIN_S) of the other camera at its edge
    (an A/V offset moves the picture range against the source's own cuts): the in / out point moves onto the cut
    when no word is spoken in the sliver, else the sliver holds the neighbouring piece's picture ("hold": "next" /
    "prev"). -> notes"""
    notes = []

    def spoken(t0, t1):
        return any(w['t1'] > t0 + 0.02 and w['t0'] < t1 - 0.02 for w in words)

    for rng in rr['keep']:
        a, b = rng
        pcs = sorted([pc for pc in pieces if pc['t0'] >= a - 0.02 and pc['t1'] <= b + 0.02], key=lambda pc: pc['t0'])
        if len(pcs) >= 2 and pcs[0]['t1'] - pcs[0]['t0'] < EDGE_MIN_S:
            first, c = pcs[0], pcs[0]['t1']
            if not spoken(first['t0'], c):
                new_a = c                                      # first output frame = the cut frame of the new shot
                for _ in range(3):
                    if round((round(new_a * sfps) / sfps - off) * sfps) >= round((c - off) * sfps):
                        break
                    new_a += 1.0 / sfps
                notes.append(f'in-point moved onto the camera cut at {c:.2f} s (no word before it; a '
                             f'{c - first["t0"]:.2f} s sliver of the other camera dropped)')
                rng[0] = round(new_a, 6)
                pieces.remove(first)
                pcs = pcs[1:]
                pcs[0]['t0'] = rng[0]
            else:
                first['hold'] = 'next'
                notes.append(f'the {c - first["t0"]:.2f} s before the camera cut at {c:.2f} s show the next shot\'s '
                             f'first frame (held; words are spoken there)')
        if len(pcs) >= 2 and pcs[-1]['t1'] - pcs[-1]['t0'] < EDGE_MIN_S:
            last, c = pcs[-1], pcs[-1]['t0']
            if not spoken(c, last['t1']):
                notes.append(f'out-point moved onto the camera cut at {c:.2f} s (no word after it; a '
                             f'{last["t1"] - c:.2f} s sliver of the other camera dropped)')
                rng[1] = round(c, 6)
                pieces.remove(last)
                pcs[-2]['t1'] = rng[1]
            else:
                last['hold'] = 'prev'
                notes.append(f'the {last["t1"] - c:.2f} s after the camera cut at {c:.2f} s show the previous shot\'s '
                             f'last frame (held; words are spoken there)')
    return notes


def _is_auto_start(part):
    fp = part.get('from')
    return (isinstance(fp, dict) and bool(fp.get('auto'))) or (fp is None and part.get('type', 'talk') == 'talk')


def prepare_source_part(p, ctx):
    """Words, cut points, layout (crops) and lip sync of a talk or clip part - everything except the frame placement.
    A/V: with no "av_offset" in the spec the source's measured audio lag (minus the natural lead) is corrected when
    the estimate is confident and >= 2 output frames; "av_offset": 0 keeps the recording as it is."""
    log = ctx.log
    info = _probe(p['source'])
    dur = float(info.get('duration') or 0.0)
    need_words = p['type'] == 'talk' or any(isinstance(x, dict) and x.get('phrase') for x in (p.get('from'), p.get('to'))) \
        or any(r.get('phrase') for r in p.get('remove') or []) or p.get('subtitles')
    words, winfo = ([], dict(source='none')) if not need_words else get_words(p, log)
    words = clean_words(words, p.get('vocab'))
    rp = dict(p, _dur=dur)                                         # resolve_ranges' view (auto start state)
    lo = 0.0
    hi = dur or (words[-1]['t1'] + 1 if words else 1.0)
    pts = [x.get('t') for x in (p.get('from'), p.get('to')) if isinstance(x, dict) and x.get('t') is not None]
    if not words and len(pts) < 2:
        raise SpecError(f'part {p["id"]}: give "from" and "to" in seconds (no words to search)')
    if words:   # envelope only around the region the phrases point to
        dry = resolve_ranges(rp, words, None, log=lambda *a, **k: None)
        lo = max(0.0, dry['keep'][0][0] - 3.0)
        hi = min(hi, dry['keep'][-1][1] + 6.0)
    elif pts:
        lo, hi = max(0.0, min(pts) - 1.0), min(hi, max(pts) + 1.0)
    env = Envelope(p['source'], lo, hi) if info.get('has_audio', True) else None
    rr = resolve_ranges(rp, words, env, log) if words else dict(
        keep=[[float(p['from']['t']), float(p['to']['t'])]], removed=[], reaction=None, notes=[], first_word=0,
        last_word=-1, **{'from': None, 'to': None})
    mode = p.get('crop', 'speaker' if p['type'] == 'talk' else 'auto')
    lp = dict(p, crop='speaker' if mode == 'auto' else mode)
    fixed = isinstance(lp['crop'], dict) or lp['crop'] in ('center', 'centre', 'none')
    spec_off = p.get('av_offset')
    off = float(spec_off or 0.0)
    sync, scans, windows, est = None, [], [], None
    notes = []
    if not fixed:
        windows = _scan_windows(rr['keep'], off, dur)
        scans = [_scan_cached(p['source'], a, b, ctx.cache_dir, log) for a, b in windows]
        if env is not None:
            est = _lag_from_scans(scans, windows, env)
            sync = _av_decision(est, ctx.fps)
            if spec_off is None:
                off = sync['offset']
    layout = None
    for attempt in range(4):
        vkeep = [[a - off, b - off] for a, b in rr['keep']]       # picture ranges (audio time - offset)
        sc, wn = _scans_for(rr['keep'], off, windows, scans, p['source'], dur, ctx.cache_dir, log) if not fixed \
            else (None, None)
        layout = talk_layout(lp, vkeep, words, env, ctx.canvas, ctx.cache_dir, log, scans=sc,
                             lag=None if est is None else est['lag'], windows=wn)
        if fixed or not words or not _is_auto_start(rp) or attempt == 3:
            break
        rp['_avoid_spans'] = [[x + off, y + off] for o in layout.get('avoid') or [] if o.get('kind') == 'popup'
                              for x, y in o.get('spans') or []]          # audio time, for ed_voice.setup_starts
        rp['_cuts'] = sorted(c + off for d, _ in sc for c in d['cuts'])
        fp_ = rp.get('from') if isinstance(rp.get('from'), dict) else {}
        if attempt == 0 and (fp_.get('auto') or dur > LONG_SOURCE_S) and _fn('ed_voice', 'setup_starts') is not None:
            rr2 = resolve_ranges(rp, words, env, log=lambda *a, **k: None)   # setup_starts, now with the cuts
            if [list(x) for x in rr2['keep']] != [list(x) for x in rr['keep']]:
                rr = rr2
                continue
        why = _start_hidden(sc, wn, vkeep[0][0], layout.get('avoid'), info.get('h') or 1080)
        if why is None:
            break
        t_bad = (rr.get('from') or {}).get('t0', rr['keep'][0][0])
        notes.append(f'start at {t_bad:.2f} s skipped: {why}')
        rp['_skip_starts'] = list(rp.get('_skip_starts') or []) + [t_bad]
        rr = resolve_ranges(rp, words, env, log=lambda *a, **k: None)
    for pc in layout['pieces']:                                    # back to audio time
        pc['t0'] += off
        pc['t1'] += off
    if not fixed:
        notes += _fix_edges(rr, layout['pieces'], words, off, float(info.get('fps') or ctx.fps))
    # lip sync: what was measured and what was done, in plain words
    lip = dict(offset=round(off, 3), by='spec' if spec_off is not None else ('measured' if off else 'none'))
    if sync is not None:
        lip.update({k: sync.get(k) for k in ('measured', 'lag', 'r', 'confident', 'why') if sync.get(k) is not None})
        meas = sync.get('measured')
        if spec_off is None and off:
            notes.append(f'lip sync: the source audio lags the picture by {off:.2f} s - corrected')
        elif spec_off is not None and off:
            notes.append(f'lip sync: picture taken {off:.2f} s earlier (spec "av_offset"'
                         + (f'; measured {meas:.2f} s)' if sync.get('confident') and meas is not None else ')'))
        elif spec_off is not None and sync.get('confident') and meas is not None and meas >= 2.0 / ctx.fps:
            notes.append(f'lip sync: the source audio lags the picture by ~{meas:.2f} s; kept as recorded '
                         f'("av_offset": 0)')
    layout['notes'] = notes + layout.get('notes', [])
    for k, (a, b) in enumerate(rr['keep']):
        txt = ' '.join(w['w'] for w in words if a - 0.02 <= w['t0'] and w['t1'] <= b + 0.05)
        log(f'[sequence] {p["id"]}: keep {a:.2f}-{b:.2f} s  "{txt[:90]}{"..." if len(txt) > 90 else ""}"')
    for r in rr['removed']:
        log(f'[sequence] {p["id"]}: cut {r["t0"]:.2f}-{r["t1"]:.2f} s' + (f'  "{r["text"]}"' if r.get('text') else ''))
    for n in rr['notes'] + layout.get('notes', []):
        log(f'[sequence] {p["id"]}: {n}')
    return dict(words=words, winfo=winfo, env=env, rr=rr, layout=layout, info=info, off=off, lip_sync=lip)


def _sub_cfg(p, S, W=1080, H=1920):
    """Subtitle settings of a part: kind, caption preset (ed_text.CAPTION_STYLES: the spec's style name, else the
    house style's caption style, else "podcast_bold" / "karaoke_highlight") and chunking hints for that preset at
    this canvas (ed_text.caption_hints)."""
    v = p.get('subtitles', S.get('subtitles') if p['type'] == 'talk' else None)
    if p['type'] == 'talk' and 'subtitles' not in p and S.get('subtitles') is None:
        v = 'subtitle'
    if v in (None, False, 'none', 'off', ''):
        return None
    cfg = dict(v) if isinstance(v, dict) else {'kind': 'karaoke' if v == 'karaoke' else 'subtitle'}
    if isinstance(v, str) and v not in ('subtitle', 'karaoke', 'subtitles', 'captions'):
        cfg['style'] = v                                   # a caption preset name: "podcast_caps", "boxed" ...
    cfg.setdefault('kind', 'subtitle')
    Tx = _mod('ed_text')
    name = cfg.get('style') if isinstance(cfg.get('style'), str) else None
    if name is None and p.get('style'):
        name = (style_info(p.get('style'), p.get('variant')) or {}).get('caption_style')
    if Tx is not None and hasattr(Tx, 'caption_style_name'):
        pre = Tx.caption_style_name(name or ('karaoke_highlight' if cfg['kind'] == 'karaoke' else 'podcast_bold')) \
            or Tx.caption_style_name('podcast_bold')
        if pre:
            cfg['preset'] = pre
            hints = {}
            try:
                if hasattr(Tx, 'caption_hints'):
                    hints = dict(Tx.caption_hints(pre, W, H) or {})
                else:
                    hints = dict(Tx.caption_styles()[pre].get('voice') or {})
            except Exception:  # noqa: BLE001
                hints = {}
            cfg['hints'] = hints
    return cfg


VERTICAL_UI_ZONE = dict(x0=0.06, x1=0.88, y0=0.12, y1=0.80)   # text-safe area of vertical-video apps
PACE_STEPS = ((17.0, 0.25), (18.0, 0.3), (19.0, 0.35), (19.5, 0.45))   # (chars / s, max lag s) tried in order


def pace_chunks(layers, fps, hard=(), f_end=None, steps=PACE_STEPS, min_s=0.7, qa_cps=19.5):
    """Reading speed of subtitle chunks in connected speech. Chunks follow the words, so a fast speaker gets chunks
    on screen for 0.5 s at 30+ chars/s; a run of touching chunks that holds such a chunk (> qa_cps or < min_s) is
    re-timed: each chunk stays on for len / cps (>= min_s) and the next ones follow later, each at most `lag` behind
    its first word, until the run reaches a pause. Per run the first (cps, lag) step that fits wins (a slower read
    only for a small lag; the QA limits are 20 chars/s and 0.7 s); nothing fits ->
    the last step with the lag capped (the chunk before is shortened). Frames in `hard` (jump cuts) and f_end are
    never crossed by a chunk whose words end before them. Updates f0/f1/lead/tail/t0/t1/cps in place -> [notes]."""
    n = len(layers)
    if not n:
        return []
    w0f, w1f, lim = [], [], []
    for L in layers:
        ws = L.get('words') or []
        a = int(round(float(ws[0]['t0']) * fps)) if ws else int(L['f0'])
        b = int(round(float(ws[-1]['t1']) * fps)) if ws else int(L['f1'])
        w0f.append(a)
        w1f.append(b)
        cap = [int(J) - 1 for J in hard if int(J) > b] + ([int(f_end)] if f_end is not None else [])
        lim.append(max(int(L['f1']), min(cap)) if cap else 10 ** 9)

    def need(j, cps):
        return int(math.ceil(max(min_s, len(str(layers[j].get('text', ''))) / cps) * fps - 1e-6))

    def bad(j):
        d = (int(layers[j]['f1']) - int(layers[j]['f0']) + 1) / fps
        return d < min_s - 1e-6 or len(str(layers[j].get('text', ''))) / d > qa_cps + 1e-6

    def sim(k0, cps, lag, prev_end, capped=False):
        out, ok, j = [], True, k0
        while j < n:
            L = layers[j]
            f0 = max(int(L['f0']), prev_end + 1)
            if capped and f0 > int(L['f0']) and f0 - w0f[j] > lag * fps:
                f0 = max(int(L['f0']), w0f[j] + int(lag * fps))
                if out and out[-1][1] >= f0:                      # the chunk before gives way
                    out[-1] = (out[-1][0], max(out[-1][0], f0 - 1))
            f1 = min(max(int(L['f1']), f0 + need(j, cps) - 1), lim[j])
            if f1 - f0 + 1 < need(j, cps) or (f0 > int(L['f0']) and f0 - w0f[j] > lag * fps + 1e-6):
                ok = False
            out.append((f0, max(f0, f1)))
            prev_end = max(f0, f1)
            j += 1
            if j < n and int(layers[j]['f0']) > prev_end:       # the next chunk is not pushed: the run ends here
                break
        return out, ok, j

    notes, k, prev_end = [], 0, -1
    while k < n:
        out, ok, j = sim(k, *steps[0], prev_end)
        if any(bad(i) for i in range(k, j)):
            for cps, lag in steps:
                out, ok, j = sim(k, cps, lag, prev_end)
                if ok:
                    break
            if not ok:
                cps, lag = steps[-1]
                out, ok, j = sim(k, cps, lag, prev_end, capped=True)
            for i, (f0, f1) in zip(range(k, j), out):
                L = layers[i]
                if (f0, f1) != (int(L['f0']), int(L['f1'])):
                    L['f0'], L['f1'] = f0, f1
                    L['lead'], L['tail'] = f0 - w0f[i], f1 - w1f[i]
                    L['t0'], L['t1'] = round(f0 / fps, 3), round((f1 + 1) / fps, 3)
                    L['cps'] = round(len(str(L.get('text', ''))) / ((f1 - f0 + 1) / fps), 1)
                    if 'reading speed' in str(L.get('warn', '')) and L['cps'] <= qa_cps:
                        L.pop('warn', None)
            notes.append(f'chunks {k + 1}-{j}: paced to <= {cps:g} chars/s'
                         + ('' if ok else ' (best effort: no room before the next pause)'))
            prev_end = out[-1][1]
        else:
            prev_end = int(layers[j - 1]['f1'])
        k = j
    return notes


def zoom_splits(t0, t1, words, max_hold=4.0, min_len=1.2, must=None):
    """Punch-in points inside one long camera shot (clips card: <= 4 s without a visual change): word onsets that cut
    [t0, t1] into stretches <= max_hold; numbers / key words, sentence starts and words after a pause are preferred,
    `must` (the punchline's first word) is used whenever it leaves >= min_len on both sides. -> sorted times"""
    if t1 - t0 <= max_hold + 1e-6:
        return []
    idx = {id(w): i for i, w in enumerate(words)}

    def score(w):
        i = idx[id(w)]
        s = 0.0
        if re.search(r'\d', w['w']) or norm_tok(w['w']) in _ONES or norm_tok(w['w']) in _SCALES:
            s += 3.0
        if i > 0 and words[i - 1]['w'].rstrip(CLOSERS)[-1:] in SENT_END:
            s += 2.0
        if i > 0 and w['t0'] - words[i - 1]['t1'] >= 0.15:
            s += 1.0
        return s
    splits = []
    if must is not None and t0 + min_len <= must <= t1 - min_len:
        # the punch-in may start up to 0.6 s (a word or two) earlier when that spares a cut before it
        early = [w['t0'] for w in words if must - 0.6 <= w['t0'] <= must and w['t0'] - t0 >= min_len]
        fit = [x for x in early if x - t0 <= max_hold + 1e-6]
        splits.append(float(max(fit) if fit and must - t0 > max_hold else must))
    def lead_in(w):                                            # a number may come sooner after a cut (>= 1 s)
        return min(min_len, 1.0) if score(w) >= 3.0 else min_len
    for _ in range(12):
        bounds = [t0] + sorted(splits) + [t1]
        L, a, b = max((y - x, x, y) for x, y in zip(bounds, bounds[1:]))
        if L <= max_hold + 1e-6:
            break
        cands = [w for w in words if a + lead_in(w) <= w['t0'] <= b - min_len]
        if not cands:
            break
        mid = (a + b) / 2
        best = max(cands, key=lambda w: score(w) - 4.0 * abs(w['t0'] - mid) / (b - a))
        splits.append(float(best['t0']))
    return sorted(splits)


def norm_tok(w):
    return re.sub(r'[\W_]+', '', unicodedata.normalize('NFKC', str(w)).lower())


def _with_zoom_cuts(pcs, p, words, to_hit, react, Bw, Bh, aspect, H, on, fps=30, variant=0):
    """Split long single-camera pieces of a talk part at motivated words, alternating the speaker's framing with a
    tighter one (the sub-piece with the punchline is always the tight one). Skipped when the source resolution
    does not allow a sharp tighter crop."""
    if not on or not Bw:
        return pcs
    max_hold = float(p.get('max_hold', 4.0)) if not isinstance(on, (int, float)) or isinstance(on, bool) else float(on)
    if variant % 2 == 1:
        max_hold = min(max_hold, 3.5)                          # another version: other cut points, same rules
    out = []
    for pc in pcs:
        c = pc.get('crop') or {}
        if pc['t1'] - pc['t0'] <= max_hold:
            out.append(pc)
            continue
        z = max([float(c.get('z', 1.0))] + [float(k[3]) for k in c.get('path') or []])
        amount = min(1.12, (Bh / (0.62 * H)) / z)              # <= 1.12, and >= 62 % of the output height sharp
        if amount < 1.06:
            out.append(pc)
            continue
        must = to_hit['t0'] if to_hit is not None and pc['t0'] < to_hit['t0'] < pc['t1'] else None
        ws = [w for w in words if pc['t0'] <= w['t0'] < pc['t1'] and (react is None or w['t0'] < react[0])]
        sp = zoom_splits(pc['t0'], pc['t1'], ws, max_hold, must=must)
        if not sp:
            out.append(pc)
            continue
        fps_ = float(fps)

        def at_word(s):                                        # one frame before the word, never inside the last one
            i = next((i for i, w in enumerate(ws) if abs(w['t0'] - s) < 1e-6), None)
            prev_t1 = ws[i - 1]['t1'] if i else s - 1.0
            return max(prev_t1 + 0.005, s - 1.0 / fps_)
        bounds = [pc['t0']] + [at_word(s) for s in sp] + [pc['t1']]
        n = len(bounds) - 1
        jp = next((j for j in range(n) if must is not None and bounds[j] <= at_word(must) + 1e-6 < bounds[j + 1]), None)
        if jp is None:                                         # no punchline here: a number gets the tight framing
            jp = next((j + 1 for j, s in enumerate(sp) for w in ws if w['t0'] == s and
                       (re.search(r'\d', w['w']) or norm_tok(w['w']) in _ONES or norm_tok(w['w']) in _SCALES)), None)
        tight_parity = (jp % 2) if jp is not None else (1 + variant) % 2
        for j in range(n):
            q = dict(pc, t0=bounds[j], t1=bounds[j + 1], zoom=j > 0)
            cj = dict(c)
            if c.get('path'):
                off = int(round((bounds[j] - pc['t0']) * fps_))
                cj['path'] = _rebase_path(c['path'], off, max(2, int(round((bounds[j + 1] - bounds[j]) * fps_))))
                cj['cx'], cj['cy'], cj['z'] = cj['path'][0][1:4]
            is_tight = j % 2 == tight_parity
            q['crop'] = scale_crop(cj, amount, pc.get('face'), Bw, Bh, aspect) if is_tight else cj
            if j > 0:
                s = sp[j - 1]
                w = next((w for w in ws if w['t0'] == s), None)
                q['tags'] = [f'punch-{"in" if is_tight else "out"}' + (f' on "{w["w"]}"' if w else '')]
            out.append(q)
    return out


def _crop_state(c, end=False):
    """A static crop from a crop with a push ("to") or a path: its first state, or its last (end=True)."""
    c = dict(c or {})
    if c.get('path'):
        k = c['path'][-1] if end else c['path'][0]
        return dict(cx=k[1], cy=k[2], z=k[3])
    if end and isinstance(c.get('to'), dict):
        return dict(cx=c['to'].get('cx', c.get('cx', 0.5)), cy=c['to'].get('cy', c.get('cy', 0.5)),
                    z=c['to'].get('z', c.get('z', 1.0)))
    return dict(cx=c.get('cx', 0.5), cy=c.get('cy', 0.5), z=c.get('z', 1.0))


def _merge_continuous(aud_segs, fps):
    """Audio segments with continuous source time merged (a camera cut or a zoom cut over continuous speech is no
    audio cut: word remapping reports cuts inside words only where the audio really jumps)."""
    out = []
    for sg in aud_segs:
        if out:
            pv = out[-1]
            n = pv['f1'] - pv['f0'] + 1
            if sg['f0'] == pv['f1'] + 1 and abs(pv['t'] + n * float(pv.get('speed', 1.0)) / fps - sg['t']) < 0.6 / fps \
                    and pv.get('src') == sg.get('src') and pv.get('speed') == sg.get('speed'):
                pv['f1'] = sg['f1']
                continue
        out.append(dict(sg))
    return out


def _chunks_with_soft_breaks(sc, words, kw, soft, fps, min_s=0.7, max_cps=20.0):
    """ed_voice.subtitle_chunks with camera cuts as soft breaks: its own soft_breaks when it has them; else each
    camera cut is a hard break unless it squeezes a neighbouring chunk under min_s or over max_cps, then it is
    dropped (one at a time). -> (layers, soft breaks kept)"""
    import inspect
    try:
        params = inspect.signature(sc).parameters
    except (TypeError, ValueError):
        params = {}
    if 'soft_breaks' in params:
        return sc(words, **dict(kw, soft_breaks=list(soft))), list(soft)
    use = list(soft)
    hard = list(kw.get('breaks') or [])
    for _ in range(len(soft) + 1):
        layers = sc(words, **dict(kw, breaks=sorted(set(hard) | set(use))))
        bad = []
        for b in use:
            B = int(round(b * fps))
            for L in layers:
                d = (int(L['f1']) - int(L['f0']) + 1) / fps
                near = B - 2 <= int(L['f1']) + 1 <= B + 1 or B - 1 <= int(L['f0']) <= B + 1
                if near and (d < min_s - 1e-6 or len(str(L.get('text', ''))) / max(d, 1e-6) > max_cps + 1e-6):
                    bad.append(b)
                    break
        if not bad:
            return layers, use
        use.remove(bad[0])
    return layers, use


def build_source_part(p, f0, prep, ctx):
    """Frames, segments, voice, subtitles of a talk / clip part starting at output frame f0."""
    fps = ctx.fps
    rr, L, words, off = prep['rr'], prep['layout'], prep['words'], prep['off']
    info = prep['info']
    sfps = float(info.get('fps') or fps)
    box = L['box']
    full = [0, 0, info['w'], info['h']]
    name = ctx.source(p['id'], dict(path=p['source'], **({'box': [int(v) for v in box]} if box and list(box) != full else {})))
    logo = next((a['box'] for a in L.get('avoid') or [] if a.get('kind') == 'logo'), None)
    if logo and box:
        ctx.sources[name]['logo'] = [int(v) for v in logo]       # safety net: inpainted if a window ever touches it
    speed = float(p.get('speed', 1.0) or 1.0)
    prefix = 'T' if p['type'] == 'talk' else 'K'
    grade = dict(p.get('grade') or TALK_GRADE)
    segs, aud_segs, voice, f = [], [], [], f0
    jumps, cams = [], []                                           # first frames after a removal / a camera cut
    src_cuts = []                                                  # the source's own camera cuts (qa.source_cuts)
    freeze = []                                                    # held frames ([a, b]: qa.planned_freeze)
    punch_log = []                                                 # zoom cuts placed (meta.choices)
    to_hit = rr.get('to')
    react = rr.get('reaction')
    push_on = p.get('push', p['type'] == 'talk')
    punch_on = p.get('punch_ins', p['type'] == 'talk')
    Bw, Bh, aspect = L.get('Bw'), L.get('Bh'), L.get('aspect', ctx.W / ctx.H)
    prev_piece = None
    for (a, b) in rr['keep']:
        a2 = round(a * sfps) / sfps                                # on the source frame grid
        n = int(round((b - a2) * fps / speed))
        if n <= 0:
            continue
        pcs = sorted([pc for pc in L['pieces'] if pc['t0'] >= a - 0.02 and pc['t1'] <= b + 0.02],
                     key=lambda pc: pc['t0']) or [dict(t0=a, t1=b, crop=dict(cx=0.5, cy=0.5, z=1.0), shot=0, why='')]
        pcs = _with_zoom_cuts(pcs, p, words, to_hit, react, Bw, Bh, aspect, ctx.H, punch_on, fps,
                              variant=int(p.get('variant') or 0))
        ks = [0]
        r_src = sfps * speed / fps                                 # source frames per output frame
        for pc in pcs[1:]:
            # output frame k shows source frame round(n_a + k * r_src) (renderer: nearest frame); the new camera
            # shot owns every frame from its first source frame n_c on
            n_c = round((pc['t0'] - off) * sfps)
            k_c = int(math.ceil((n_c - round((a2 - off) * sfps) - 0.5) / r_src - 1e-9))
            ks.append(min(n - 1, max(ks[-1] + 1, k_c)))
        ks.append(n)
        for j_pc, (pc, k0, k1) in enumerate(zip(pcs, ks, ks[1:])):
            if k1 <= k0:
                continue
            hold = pc.get('hold') if pc.get('hold') in ('next', 'prev') else None
            nb = (pcs[j_pc + 1] if hold == 'next' and j_pc + 1 < len(pcs) else
                  pcs[j_pc - 1] if hold == 'prev' and j_pc > 0 else None)
            if hold and nb is not None:                            # a sliver at the range edge: the neighbour's frame
                t_hold = (nb['t0'] - off) if hold == 'next' else (nb['t1'] - off - 1.0 / sfps)
                sg = dict(id=ctx.seg_id(prefix), f0=f + k0, f1=f + k1 - 1, src=name, t=round(t_hold, 6),
                          times=[round(t_hold, 6)] * (k1 - k0), speed=speed, interp='nearest',
                          crop=_crop_state(segs[-1]['crop'] if hold == 'prev' and segs else nb['crop'], end=hold == 'prev'),
                          border='reflect', grade=dict(grade), fx=[],
                          part=p['id'], note=f'{p["id"]} | held {"first" if hold == "next" else "last"} frame of the '
                                             f'{"next" if hold == "next" else "previous"} shot (sliver at the range edge)')
                segs.append(sg)
                aud_segs.append(dict(id=sg['id'], f0=sg['f0'], f1=sg['f1'], src=name, t=round(a2 + k0 * speed / fps, 6),
                                     speed=speed))
                freeze.append([sg['f0'], sg['f1']])
                if hold == 'prev' and k0 > 0:
                    src_cuts.append(f + k0)                        # the source's cut, held across: not an edit
                continue
            crop = _fit_path(dict(pc['crop']), k1 - k0)
            tags = list(pc.get('tags') or [])
            if push_on and Bw:
                is_punch = to_hit is not None and pc['t0'] - 0.65 <= to_hit['t0'] < pc['t1'] - 0.05
                is_react = react is not None and pc['t0'] >= react[0] - 0.05
                same = prev_piece is not None and not pc.get('zoom') and prev_piece.get('shot') == pc.get('shot') \
                    and prev_piece.get('speaker') == pc.get('speaker') and pc.get('shot') is not None
                if same:                                           # jump cut inside one shot: punch in
                    crop = scale_crop(crop, 1.12, pc.get('face'), Bw, Bh, aspect)
                    tags.append('punch-in (jump cut)')
                if is_punch or is_react:
                    amt = 1.05 if is_react else 1.06
                    if crop.get('path'):
                        crop = scale_crop(crop, amt, pc.get('face'), Bw, Bh, aspect, n=k1 - k0, ease='inOutSine')
                    else:
                        crop['to'] = dict(_push(crop, pc.get('face'), Bw, Bh, aspect, amt))
                        crop['ease'] = 'inout'
                    tags.append('slow push-in on the ' + ('reaction' if is_react and not is_punch else 'punchline'))
            held_before = j_pc > 0 and pcs[j_pc - 1].get('hold') == 'next'
            if k0 > 0 and not pc.get('zoom'):
                src_cuts.append(f + k0)                            # where the source cuts, not an edit decision
                if not held_before:
                    cams.append(f + k0)                            # camera cut: a soft caption break
            if pc.get('zoom'):
                punch_log.append([round(pc['t0'], 3), (pc.get('tags') or [''])[0]])
            sg = dict(id=ctx.seg_id(prefix), f0=f + k0, f1=f + k1 - 1, src=name,
                      t=round(a2 - off + k0 * speed / fps, 6), speed=speed, interp='nearest' if speed == 1.0 else 'flow',
                      crop=crop, border='reflect', grade=dict(grade), fx=[], part=p['id'],
                      note=f'{p["id"]} | {pc.get("why", "")}' + (f' | {", ".join(tags)}' if tags else ''))
            segs.append(sg)
            aud_segs.append(dict(id=sg['id'], f0=sg['f0'], f1=sg['f1'], src=name, t=round(a2 + k0 * speed / fps, 6),
                                 speed=speed))
            prev_piece = pc
        if p.get('audio', 'voice') != 'mute' and speed == 1.0 and info.get('has_audio', True):
            voice.append(dict(path=p['source'], at=round(f / fps, 4), **{'in': round(a2, 4)}, dur=round(n / fps, 4),
                              gain_db=0.0, part=p['id']))
        if f > f0:
            jumps.append(f)
        f += n
    if not segs:
        raise SpecError(f'part {p["id"]}: nothing left after the cuts')
    # levels and click-free joins are the mixer's job (ed_sfx: clips of one file share one gain, raised-cosine
    # fades at clip edges); with an older mixer that normalises every clip alone, carry the group gain here
    if voice and not _mixer_groups_sources():
        _group_gain(voice)
    f1 = f - 1
    # subtitles (output time)
    out_words, layers = [], []
    sub = _sub_cfg(p, ctx.S, ctx.W, ctx.H) if words else None
    rw = _fn('ed_voice', 'remap_words')
    if words and rw is not None:
        out_words, issues = rw(words, _merge_continuous(aud_segs, fps), fps, src=name)
        out_words = [w for w in out_words if w['t0'] < (f1 + 1) / fps]
        uniq = {x['f']: x for x in issues}
        if uniq:
            ctx.notes.append(f'{p["id"]}: {len(uniq)} cut(s) inside a word: ' +
                             ', '.join(f'"{x["word"]}" f{x["f"]}' for x in list(uniq.values())[:4]))
    if sub and out_words:
        sc = _fn('ed_voice', 'subtitle_chunks')
        # the chunker plans around the jumps (removed text) and the part's ends - hard breaks: no chunk holds words
        # from both sides or stays on across one; camera cuts are soft breaks (kept where the chunks keep their
        # reading time); the preset sets kind and line limits
        hard = sorted({round(J / fps, 6) for J in jumps} | {round((f1 + 1) / fps, 6)} | ({round(f0 / fps, 6)} if f0 else set()))
        soft = sorted({round(J / fps, 6) for J in cams} - set(hard))
        kw = dict(fps=fps, lang=prep['winfo'].get('lang'), canvas=(ctx.W, ctx.H), breaks=hard)
        if sub.get('preset'):
            kw['style'] = sub['preset']
        else:
            kw['kind'] = sub['kind']
        for key in ('max_chars', 'max_lines', 'max_words'):         # only what the spec says explicitly
            if sub.get(key):
                kw[key] = sub[key]
        if sc is not None:
            try:
                layers, used_soft = _chunks_with_soft_breaks(sc, out_words, kw, soft, fps)
                if soft and len(used_soft) < len(soft):
                    ctx.notes.append(f'{p["id"]}: subtitles run across {len(soft) - len(used_soft)} camera cut(s) '
                                     f'(a break there would squeeze a chunk under 0.7 s or over 20 chars/s)')
            except TypeError:                                      # an older ed_voice: no canvas / breaks / presets
                hints = sub.get('hints') or {}
                kw = dict(kind=sub['kind'], fps=fps, lang=prep['winfo'].get('lang'),
                          max_chars=sub.get('max_chars') or hints.get('max_chars') or 18,
                          max_lines=sub.get('max_lines') or hints.get('max_lines') or 2)
                if sub.get('max_words') or hints.get('max_words'):
                    kw['max_words'] = sub.get('max_words') or hints.get('max_words')
                layers = sc(out_words, **kw)
        for Ly in layers:
            kind = Ly.get('kind') or sub['kind']
            if sub.get('preset'):
                Ly['style'] = sub['preset'] if not isinstance(sub.get('style'), dict) else dict(sub['style'], preset=sub['preset'])
            else:
                Ly['style'] = dict(SUB_STYLE, **(sub.get('style') or {}))
                Ly['pos'] = dict(sub.get('pos') or SUB_POS)
                if kind == 'karaoke':
                    Ly['highlight'] = dict(KARAOKE_HL)
            if sub.get('pos') and sub.get('preset'):
                Ly['pos'] = dict(sub['pos'])
            Ly['part'] = p['id']
            Ly['move'] = 'type.karaoke' if kind == 'karaoke' else 'type.subtitles'
            # safety net (an older chunker without breaks): a chunk's lead / tail never crosses a jump or the part end
            w0 = int(round(Ly['words'][0]['t0'] * fps)) if Ly.get('words') else int(Ly['f0'])
            w1 = int(round(Ly['words'][-1]['t1'] * fps)) if Ly.get('words') else int(Ly['f1'])
            a, b = int(Ly['f0']), min(int(Ly['f1']), f1)
            for J in jumps:
                if w1 < J <= b:
                    b = J - 1
                if a < J <= w0:
                    a = J
            if (a, b) != (int(Ly['f0']), int(Ly['f1'])):
                Ly['f0'], Ly['f1'] = a, b
                if Ly.get('words'):
                    Ly['lead'], Ly['tail'] = a - w0, b - w1               # ed_text redraws exactly these frames
        layers = [Ly for Ly in layers if Ly['f0'] <= Ly['f1']]
        if sub.get('pace', True):                                     # safety net: only chunks the QA would flag
            plain = [Ly for Ly in layers if Ly.get('kind') != 'karaoke']
            ctx.notes += [f'{p["id"]}: subtitles {x}' for x in pace_chunks(plain, fps, hard=jumps, f_end=f1, qa_cps=20.0)]
    # output time of the reaction (riser start for the next transition)
    react_out = None
    if react is not None:
        for sg in aud_segs:
            a_t = sg['t']
            b_t = a_t + (sg['f1'] - sg['f0'] + 1) / fps
            if a_t - 1e-3 <= react[0] < b_t:
                react_out = (sg['f0'] + (react[0] - a_t) * fps) / fps
                break
    meta = dict(source=p['source'], words=prep['winfo'], keep=rr['keep'], removed=rr['removed'],
                reaction=react, **{'from': _brief_hit(rr.get('from')), 'to': _brief_hit(rr.get('to'))},
                box=box, box_by=L.get('by_box'), avoid=L.get('avoid'), avoid_by=L.get('by_avoid'), crops_by=L.get('by'),
                pieces=[dict(t0=_r(pc['t0']), t1=_r(pc['t1']), shot=pc.get('shot'), crop=pc['crop'], why=pc.get('why'))
                        for pc in L['pieces']],
                notes=rr['notes'] + L.get('notes', []), subtitles=(sub or {}).get('preset') or (sub or {}).get('kind'),
                lip_sync=prep.get('lip_sync'),
                choices=dict(variant=int(p.get('variant') or 0), punch_ins=punch_log,
                             caption_style=(sub or {}).get('preset')))
    return _part_out(segments=segs, voice=voice, layers=layers, words=out_words, f1=f1, meta=meta,
                     has_voice=bool(voice), react_out=react_out, src_name=name, planned_freeze=freeze,
                     source_cuts=src_cuts)


def _brief_hit(h):
    if not h:
        return None
    return {k: (_r(v) if isinstance(v, float) else v) for k, v in h.items() if k in ('t0', 't1', 'text', 'score', 'by')}


def _mixer_groups_sources():
    """True when ed_sfx normalises the voice clips of one file together (round r4 mixer: "norm": "source")."""
    sfx = _mod('ed_sfx')
    f = getattr(sfx, '_voices', None) if sfx is not None else None
    return bool(f is not None and 'norm' in (f.__doc__ or '') and 'share one gain' in (f.__doc__ or ''))


def _group_gain(voice):
    """The mixer normalises every voice entry to the target on its own; pieces of one recording should keep their
    relative level, so each entry gets gain_db = its loudness - the loudness of all entries together."""
    sfx = _mod('ed_sfx')
    if sfx is None or not hasattr(sfx, '_load') or not hasattr(sfx, 'lufs_integrated'):
        return
    try:
        ys, Is = [], []
        for v in voice:
            y = sfx._load(v['path'], 48000, start=float(v['in']), dur=float(v['dur']))
            ys.append(y)
            Is.append(float(sfx.lufs_integrated(y, 48000)))
        I_all = float(sfx.lufs_integrated(np.concatenate(ys), 48000))
        if not np.isfinite(I_all):
            return
        for v, I in zip(voice, Is):
            if np.isfinite(I):
                v['gain_db'] = round(I - I_all, 2)
    except Exception:  # noqa: BLE001 - levels stay per-entry
        return


# ============================================================================ edit parts
def clip_profile(path, cache_dir=None):
    """Motion over time (mean frame change of 192 px greys at 12 fps), action peaks (ed_fx.action_peaks: where the
    motion stops after a maximum), mean luma; cached."""
    key = _file_key(path, 'clip3')
    cp = os.path.join(cache_dir, f'clip_{key}.json') if cache_dir else None
    if cp and os.path.exists(cp):
        d = _load_json(cp)
        if d:
            return d
    info = _probe(path)
    fa = 12.0
    cmd = ['ffmpeg', '-v', 'error', '-nostdin', '-i', path, '-an', '-vf', f'fps={fa},scale=192:-2:flags=area',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    h = int(round(info['h'] * 192 / info['w'] / 2) * 2)
    n = len(raw) // (192 * h * 3)
    frames = np.frombuffer(raw[:n * 192 * h * 3], np.uint8).reshape(n, h, 192, 3)
    g = frames.astype(np.float32).mean(-1)
    mot = [0.0] + [float(np.mean(np.abs(g[i] - g[i - 1]))) for i in range(1, n)]
    luma = [float(x.mean()) for x in g]
    peaks = []
    ap = _fn('ed_fx', 'action_peaks')
    if ap is not None and n >= 4:
        try:
            peaks = [float(x) for x in ap(list(frames), fa)]
        except Exception:  # noqa: BLE001
            peaks = []
    d = dict(path=path, dur=float(info['duration']), fps=float(info['fps'] or 24), w=info['w'], h=info['h'],
             t=[round(i / fa, 4) for i in range(n)], motion=[round(v, 3) for v in mot], luma=[round(v, 2) for v in luma],
             peaks=peaks)
    if cp:
        os.makedirs(cache_dir, exist_ok=True)
        _dump_json(d, cp)
    return d


def ramp_rates(n, beats_k, profile, fast=2.5, slow=0.4, dec=6, acc=5, end_slow=None):
    """Per-frame playback rate (source s per output s) of a speed-ramped shot of n frames; beats_k = beat frames
    inside the shot (k > 0). Profiles (move card time.speed_ramp: braking on a hit, speed-up on the next beat):
      'drop'  slow from the cut (the drop is the hit) -> speed-up on the last beat -> fast into the next cut
      'ramp'  fast -> brake (dec frames, inOutCubic) landing on the first beat after the cut -> slow -> speed-up
              (acc frames, inCubic) on the last beat -> fast into the cut
      'end'   fast -> brake on the first beat -> slow to the end (easing to end_slow)
      'hold'  slow throughout.        -> (rates, braking frame, speed-up frame)"""
    b = sorted(int(k) for k in beats_k if 0 < k < n)
    kb = b[0] if b else max(dec + 1, int(round(0.28 * n)))
    ku = b[-1] if len(b) >= 2 else int(round(0.75 * n))
    if ku - kb < 6:
        ku = min(n - acc - 1, kb + max(6, int(0.4 * n)))
    r = np.full(n, float(slow))

    def fill(k0, k1, r0, r1, kind):
        for k in range(max(0, k0), min(n, k1)):
            r[k] = r0 + (r1 - r0) * _ease((k - k0 + 1) / max(1, k1 - k0), kind)
    if profile == 'ramp':
        r[:max(0, kb - dec)] = fast
        fill(kb - dec, kb, fast, slow, 'inOutCubic')
        r[kb:ku] = slow
        fill(ku, ku + acc, slow, fast, 'inCubic')
        r[ku + acc:] = fast
    elif profile == 'drop':
        r[:ku] = slow
        fill(ku, ku + acc, slow, fast, 'inCubic')
        r[ku + acc:] = fast
    elif profile == 'end':
        r[:max(0, kb - dec)] = fast
        fill(kb - dec, kb, fast, slow, 'inOutCubic')
        fill(kb, n, slow, slow if end_slow is None else end_slow, 'outCubic')
    return r, kb, ku


def ramp_times(n, fps, beats_k, profile, fast=2.5, slow=0.4, **kw):
    """Source offsets (s from the shot's in-point) of every output frame of a speed-ramped shot (+ rates, kb, ku)."""
    r, kb, ku = ramp_rates(n, beats_k, profile, fast, slow, **kw)
    S = np.concatenate([[0.0], np.cumsum(r) / fps])
    return S, r, kb, ku


def _place_window(prof, S, anchor_k, anchor_off, rank=0, avoid_t=()):
    """In-point so the clip's action peak lands just after the braking frame (anchor_k) and the shot fits. rank picks
    the rank-th best peak (another version shows another moment); peaks within 0.3 s of avoid_t (earlier versions'
    picks) go to the back of the list."""
    span = float(S[-1]) + 1.0 / prof['fps']
    lo, hi = 0.04, prof['dur'] - 0.06 - span
    if hi < lo:
        return max(0.0, (prof['dur'] - span) / 2), 'clip shorter than the ramp needs', None
    t = np.asarray(prof['t'], float)
    m = np.asarray(prof['motion'], float)
    ms = np.convolve(m, np.ones(5) / 5, mode='same') if len(m) >= 5 else m
    cands = []
    for pk in sorted(set(list(prof.get('peaks') or []) + ([float(t[int(np.argmax(ms))])] if len(ms) else []))):
        t_in = pk - anchor_off - float(S[anchor_k])
        if lo <= t_in <= hi:
            strength = float(np.interp(pk - 0.15, t, ms)) if len(ms) else 0.0
            used = any(abs(pk - a) < 0.3 for a in avoid_t)
            cands.append((used, -(strength - 0.05 * abs(t_in + span / 2 - prof['dur'] / 2)), t_in, pk))
    if cands:
        cands.sort()
        _, _, t_in, pk = cands[rank % len(cands)]
        return float(t_in), f'action peak at {pk:.2f} s on the braking', float(pk)
    mid = float(t[int(np.argmax(ms))]) if len(ms) else prof['dur'] / 2
    return float(min(max(mid - anchor_off - float(S[anchor_k]), lo), hi)), 'no peak fits: nearest feasible window', None


def _integral(rates, fps):
    """Source offsets of frames 0..n of a per-frame rate curve, integrated exactly like the renderer
    (ed_edl.rate_integral: linear between the per-frame keys, flat after the last)."""
    r = np.asarray(rates, float)
    S = np.zeros(len(r) + 1)
    if len(r) > 1:
        S[1:len(r)] = np.cumsum((r[:-1] + r[1:]) / 2.0) / fps
    S[len(r)] = S[len(r) - 1] + r[-1] / fps
    return S


def ramp_curve(n, fps, beats_k, profile, fast=2.5, slow=0.4, src_fps=None, brake_beat=1):
    """A speed-ramped shot: ed_fx.speed_ramp (move card time.speed_ramp) when it exists, else ramp_rates.
    brake_beat = which beat inside the shot the braking lands on (1 = the first after the cut).
    -> dict(S: source offsets of frames 0..n, rates, kb (slow-motion start), ku (speed-up start), fx, notes)"""
    b = sorted(int(k) for k in beats_k if 0 < k < n)
    kb = b[min(max(brake_beat, 1), len(b)) - 1] if b else max(7, int(round(0.28 * n)))
    if profile in ('drop', 'hold'):
        kb = 0
    ku = b[-1] if len(b) >= 2 and b[-1] > kb + 6 else min(n - 6, max(kb + 7, int(round(0.75 * n))))
    sr = _fn('ed_fx', 'speed_ramp')
    if sr is not None and profile in ('drop', 'ramp', 'end', 'hold'):
        try:
            kw = dict(fast=fast, slow=slow, brake_at=kb, src_fps=src_fps)
            if profile in ('drop', 'ramp'):
                kw.update(exit_at=ku, exit_frames=5)
            res = sr(n, fps, **kw)
            rates = [float(v) for _, v in sorted(res['speed_curve'])]
            if len(rates) == n:
                fx = [dict(f, move=f.get('move', 'time.motion_blur')) for f in res.get('fx') or []]
                return dict(S=_integral(rates, fps), rates=rates, kb=kb, ku=ku, fx=fx, notes=list(res.get('notes') or []),
                            by='ed_fx.speed_ramp')
        except Exception:  # noqa: BLE001 - the local ramp below
            pass
    r, kb2, ku2 = ramp_rates(n, beats_k, 'ramp' if profile == 'ramp' else profile, fast, slow, end_slow=0.8 * slow)
    r = list(map(float, r))
    return dict(S=_integral(r, fps), rates=r, kb=0 if profile in ('drop', 'hold') else kb2, ku=ku2, notes=[], by='local',
                fx=[dict(type='motion_blur', mode='frames', shutter=0.5, min_rate=1.4, move='time.motion_blur')])


def _subject_path(path, t_in, times, out_aspect):
    RF = _mod('ed_reframe')
    if RF is None or not hasattr(RF, 'crop_path'):
        return None, None, 'centre'
    try:
        rf = RF.crop_path(path, t_in, max(float(times[-1]) - t_in, 0.3), out_aspect=out_aspect)
    except Exception:  # noqa: BLE001
        return None, None, 'centre'
    kt = [k[0] for k in rf['keys']]
    rel = np.asarray(times, float) - t_in
    return (np.interp(rel, kt, [k[1] for k in rf['keys']]), np.interp(rel, kt, [k[2] for k in rf['keys']]),
            rf.get('subject', 'face'))


def edit_grid(p, beats, track_t0):
    """Cut grid of an edit part in track time: bars from the downbeat at (or after) track_t0; shots spread over the
    beats. -> (cut track times [shots + 1], beat track times inside the part)"""
    j0 = beats.next_down(track_t0)
    if abs(beats.time(j0) - track_t0) > 0.06:
        j0 = beats.index(track_t0)
    nb = 4 * p['bars']
    if p['shots'] > nb:
        raise SpecError(f'part {p["id"]}: {p["shots"]} shots do not fit {p["bars"]} bars (max one shot per beat)')
    js = [j0 + int(round(i * nb / p['shots'])) for i in range(p['shots'] + 1)]
    cuts = [beats.time(j) for j in js]
    bt = [beats.time(j) for j in range(j0, j0 + nb + 1)]
    return cuts, bt


def _face_out(cx, cy, z, src_w, src_h, W, H):
    """Where a subject at source fractions (cx, cy) lands in the output frame of a crop centred on it (window
    clamped inside the picture like the renderer does) -> [x, y] output fractions."""
    hw = 1.0 / max(z, 1e-3)                                   # window height as a fraction of the picture
    ww = hw * (W / H) * (src_h / src_w)                       # ... and its width
    wc = min(max(cx, ww / 2), 1 - ww / 2) if ww < 1 else 0.5
    hc = min(max(cy, hw / 2), 1 - hw / 2) if hw < 1 else 0.5
    return [round(min(0.85, max(0.15, 0.5 + (cx - wc) / ww)), 3), round(min(0.8, max(0.2, 0.5 + (cy - hc) / hw)), 3)]


def _recipe_avoid(avoid, pid):
    """Choices of earlier versions of this part (their meta.sequence.parts[pid].choices / meta.choices)."""
    out = []
    for a in avoid or []:
        e = _load_json(a) if isinstance(a, str) else a
        if not isinstance(e, dict):
            continue
        m = e.get('meta') or {}
        ch = (((m.get('sequence') or {}).get('parts') or {}).get(pid) or {}).get('choices') or m.get('choices')
        if isinstance(ch, dict):
            out.append(ch)
    return out


def build_edit_recipe(p, f0, m, beats, ctx):
    """Local edit recipe: one shot per bar (or the grid's share) in the given order on the downbeats, speed ramps
    (ed_fx.speed_ramp) anchored on action peaks, a face-centred hold punch-in (<= 1.12) on every brake, subject crop,
    the genre grade + exposure match, motion blur on fast frames, heavy shake on the drop, whooshes on the cuts and
    soft hits on the braking points (heavy). `variant` re-seeds the choices inside these rules (brake beat pattern,
    which action peak, whoosh flavour, punch size, grade nuance); `avoid` (earlier versions) steers away from their
    picks. Records meta.choices."""
    fps = ctx.fps
    out_t = lambda tt: m['at'] + (tt - m['in'])                     # noqa: E731
    track_t0 = m['in'] + (f0 / fps - m['at'])
    cuts, bt = edit_grid(p, beats, track_t0)
    F = [f0] + [frame_at(out_t(c), fps) for c in cuts[1:]]
    footage = list(p['footage'])
    profs = [clip_profile(x, ctx.cache_dir) for x in footage]
    order = list(range(len(footage)))
    if p['order'] == 'auto':                                       # the most dynamic clip lands on the drop
        score = [float(np.percentile(pf['motion'], 90)) if pf['motion'] else 0.0 for pf in profs]
        order.sort(key=lambda i: -score[i])
    variant = int(p.get('variant') or 0)
    prev = _recipe_avoid(p.get('avoid'), p['id'])
    if p.get('variant') is None and prev:                          # "another version": the next unused variant
        used = {int(c.get('variant', 0)) for c in prev}
        variant = 0
        while variant in used:
            variant += 1
    avoid_peaks = {}
    for c in prev:
        for row in c.get('peaks') or []:
            if isinstance(row, (list, tuple)) and len(row) == 2 and row[1] is not None:
                avoid_peaks.setdefault(str(row[0]), []).append(float(row[1]))
    Pl = _mod('ed_plan')
    genre = p['genre']
    base_grade = dict((getattr(Pl, 'GRADES', {}) or {}).get(genre) or (EPIC_GRADE if genre == 'epic' else
                                                                        dict(preset='color', contrast=1.1, sat=1.0)))
    base_grade.update(p.get('grade') or {})
    if variant:                                                    # a small, repeatable grade nuance per version
        rg = np.random.default_rng(7919 * variant + 13)
        base_grade['temp'] = round(float(base_grade.get('temp', 0.0)) + float(rg.uniform(-0.05, 0.05)), 3)
        base_grade['contrast'] = round(float(base_grade.get('contrast', 1.0)) + float(rg.uniform(-0.04, 0.04)), 3)
    ramp = dict(fast=2.5, slow=0.4)
    ramp.update(p.get('ramp') or {})
    level = p['sfx']
    whoosh_v = ['air', 'swish', 'heavy'][variant % 3] if level != 'heavy' or variant else 'heavy'
    punch = 1.1 if variant % 2 == 0 else 1.08
    want_ramp = (not p['moves']) or any(str(x).startswith('time.speed_ramp') or x == 'time' for x in p['moves'])
    segs, sfx, shots_meta, notes, peaks = [], [], [], [], []
    is_drop = bool(m.get('drop_here'))
    n_sh = p['shots']
    for i in range(n_sh):
        ci = order[i % len(order)]
        prof, path = profs[ci], footage[ci]
        n = F[i + 1] - F[i]
        if n <= 0:
            continue
        beats_k = sorted({frame_at(out_t(b), fps) - F[i] for b in bt if cuts[i] < b < cuts[i + 1] - 1e-6})
        if not want_ramp:
            profile = 'hold' if (i == 0 and is_drop) else 'normal'
        elif n_sh == 1:
            profile = 'end'
        elif i == 0 and is_drop:
            profile = 'drop'
        elif i == n_sh - 1:
            profile = 'end'
        else:
            profile = 'ramp'
        slow = ramp['slow'] if prof['fps'] < 45 else min(ramp['slow'], 0.3)
        fast = ramp['fast']
        brake_beat = 1 + ((i % 2) if variant % 2 == 1 and profile == 'ramp' else 0)   # odd versions alternate 3 / 2
        if profile == 'normal':
            R = dict(S=np.arange(n + 1) / fps, rates=[1.0] * n, kb=0, ku=n, fx=[], notes=[], by='none')
        else:
            while True:
                R = ramp_curve(n, fps, beats_k, profile, fast, slow, src_fps=prof['fps'], brake_beat=brake_beat)
                if float(R['S'][-1]) + 1 / prof['fps'] <= prof['dur'] - 0.12 or fast <= 1.25:
                    break
                fast = round(fast - 0.1, 2)
        S, kb = R['S'], R['kb']
        notes += [n_ for n_ in R['notes'] if n_ not in notes]
        anchor_k = 0 if profile in ('drop', 'hold') else kb
        t_in, why, pk = _place_window(prof, S, anchor_k, 0.15 if anchor_k == 0 else 0.10, rank=variant,
                                      avoid_t=avoid_peaks.get(os.path.basename(path), ()))
        peaks.append([os.path.basename(path), None if pk is None else round(pk, 3)])
        times = t_in + S[:n]
        cx, cy, subj = _subject_path(path, t_in, times, ctx.W / ctx.H)
        punch_here = profile in ('ramp', 'end') and 0 < kb < n - 3
        z0, z1 = 1.0, (1.0 if punch_here else 1.05)                 # the brake punch replaces the slow push
        ks = sorted(set(list(range(0, n, 2)) + [n - 1]))
        if cx is not None:
            path_k = [[int(k), round(float(cx[k]), 4), round(float(cy[k]), 4),
                       round(z0 + (z1 - z0) * _ease(k / max(1, n - 1), 'outCubic'), 4)] for k in ks]
            crop = dict(cx=path_k[0][1], cy=path_k[0][2], z=z0, path=path_k, subject=subj)
        else:
            crop = dict(cx=0.5, cy=0.5, z=z0, to=dict(z=z1), ease='out')
        g = dict(base_grade)
        lum = float(np.interp((times[0] + times[-1]) / 2, prof['t'], prof['luma'])) if prof['luma'] else 100.0
        ev_fn = getattr(Pl, 'exposure_ev', None) if Pl is not None else None
        if ev_fn is not None:
            ev = ev_fn(genre, lum)
            if ev:
                g['exposure'] = ev
        fx = [dict(type='vignette', amount=0.22, move='fx.vignette')] + [dict(f_) for f_ in R['fx']]
        if i == 0 and is_drop:
            fx.append(dict(type='shake.beat', times=[round(F[0] / fps, 4)], profile='heavy', move='shake.beat'))
        center = None
        if punch_here:                                              # punch in on the face as it brakes, hold to the cut
            if cx is not None and subj == 'face':
                center = _face_out(float(cx[kb]), float(cy[kb]), 1.0, prof['w'], prof['h'], ctx.W, ctx.H)
            else:                                                   # a detail / body shot: into the middle, not
                center = [0.5, 0.5]                                 # towards a head cut by the frame edge
            fx.append(dict(type='zoom.punch', times=[round((F[i] + kb) / fps, 4)], scale=punch, mode='hold',
                           hold_until='cut', attack=1, center=center, blur_shutter=0.5, move='zoom.punch'))
        src = ctx.source(f'{p["id"]}_{ci + 1}', dict(path=path))
        sg = dict(id=ctx.seg_id('E'), f0=F[i], f1=F[i + 1] - 1, src=src, t=round(float(times[0]), 4),
                  times=[round(float(x), 4) for x in times],
                  speed_curve=[[int(k), round(float(v), 4)] for k, v in enumerate(R['rates'])],
                  interp='flow', crop=crop, border='reflect', grade=g, fx=fx, part=p['id'],
                  note=f'{p["id"]} | shot {i + 1}/{n_sh} | {os.path.basename(path)} | {profile} ramp | {why}'
                       + (f' | punch x{punch} on the brake' if punch_here else ''))
        if profile == 'normal':
            sg.pop('times')
            sg.pop('speed_curve')
            sg['speed'] = 1.0
        segs.append(sg)
        # sound: whoosh peaking on every cut into this shot, soft hits where it brakes (heavy)
        if i > 0 and level != 'none':
            sfx.append(dict(kind='whoosh', variant=whoosh_v, at=round(F[i] / fps, 4), align='peak',
                            level='strong' if level == 'heavy' else ('light' if level == 'light' else 'normal'),
                            move='sfx.whoosh', why='speed-up into the cut'))
        if level == 'heavy' and punch_here:
            sfx.append(dict(kind='impact', variant='soft', at=round((F[i] + kb) / fps, 4), align='attack',
                            level='light', move='sfx.impact', why='braking into slow motion'))
        shots_meta.append(dict(id=sg['id'], clip=os.path.basename(path), f0=sg['f0'], f1=sg['f1'], profile=profile,
                               t_in=round(t_in, 3), span=round(float(times[-1] - times[0]), 3), brake_k=int(kb),
                               fast=round(fast, 2), slow=slow, ramp_by=R['by'], punch_center=center, why=why))
    f1 = segs[-1]['f1'] if segs else f0 - 1
    sections = {}
    if segs:
        if is_drop and len(segs) >= 3:                             # the drop runs to the last shot, which closes
            sections = dict(drop=[f0, segs[-1]['f0'] - 1], outro=[segs[-1]['f0'], f1])
        elif is_drop:
            sections = dict(drop=[f0, f1])
        elif len(segs) >= 3:
            sections = dict(hook=[f0, segs[0]['f1']], build=[segs[1]['f0'], segs[-1]['f0'] - 1],
                            outro=[segs[-1]['f0'], f1])
        else:
            sections = dict(build=[f0, f1])
    choices = dict(variant=variant, brake_pattern='alternate' if variant % 2 else 'beat 2', peaks=peaks,
                   whoosh=whoosh_v, punch=punch, grade={k: base_grade.get(k) for k in ('temp', 'contrast')})
    return _part_out(segments=segs, sfx=sfx, f1=f1,
                     meta=dict(engine='recipe', genre=genre, cuts_track=[round(c, 4) for c in cuts], cut_frames=F,
                               shots=shots_meta, grade=base_grade, sections=sections, choices=choices, notes=notes))


def _shift_frames(spec, df):
    if isinstance(spec, int):
        return spec + df
    if isinstance(spec, str) and ':' in spec:
        a, b = spec.split(':')[:2]
        return f'{int(a) + df}:{int(b) + df}'
    if isinstance(spec, str):
        return str(int(spec) + df)
    if isinstance(spec, (list, tuple)):
        return [_shift_frames(x, df) for x in spec]
    return spec


def _shift_times(d, dt, keys=('at', 't', 't0', 't1', 'until', 'reset_at', 'end_at', 'resume_at', 'times')):
    for k in keys:
        v = d.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            d[k] = round(v + dt, 4)
        elif isinstance(v, list) and v and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v):
            d[k] = [round(x + dt, 4) for x in v]


def _part_avoid(avoid, pid):
    """Earlier versions for the planner's `avoid`: a composite contributes this part's recorded choices (wrapped as
    {"meta": {"choices"}}), a plain planner EDL goes as it is."""
    out = []
    for a in avoid or []:
        try:
            e = _load_json(a) if isinstance(a, str) else a
        except (OSError, ValueError):
            continue
        if not isinstance(e, dict):
            continue
        m = e.get('meta') or {}
        if not isinstance(m.get('sequence'), dict):
            out.append(e)
            continue
        ch = (((m['sequence'].get('parts') or {}).get(pid)) or {}).get('choices')
        if isinstance(ch, dict) and ch:
            out.append({'meta': {'choices': ch}})
    return out


def _planner_choices(e):
    """meta.choices of a planner EDL; a plan made without style / variant records none, so they are read from its
    content in the planner's own format (transitions, looks, shots [[slot, shot id, window start]], variant)."""
    em = e.get('meta') or {}
    if isinstance(em.get('choices'), dict) and em['choices']:
        return em['choices']
    segs = e.get('segments') or []
    trs = {str(s['f0']): (s.get('transition_in') or {}).get('move', (s.get('transition_in') or {}).get('kind'))
           for s in segs[1:] if s.get('transition_in')}
    looks = sorted({fx.get('move', fx.get('type')) for s in segs for fx in s.get('fx') or []
                    if fx.get('type') in ('film_overlay', 'glow', 'vignette', 'light_leak')} - {None})
    shots = [[i, sl.get('shot'), (sl.get('src_t') or [None])[0]] for i, sl in enumerate(em.get('slots') or [])
             if isinstance(sl, dict)]
    return dict(style=em.get('style'), variant=int(em.get('variant') or 0), transitions=sorted(set(trs.values()) - {None}),
                transitions_at=trs, looks=looks, shots=shots, by='content')


def _sharpen_times(sg, fps):
    """A planner segment's per-frame source "times" rounded to 0.1 ms read as 0.399x where its speed curve says 0.4x
    (the QA's slow floor): when the times are exactly the curve's forward sum (times[k] = t + sum rate[j < k] / fps,
    the planner's mapping), they are re-derived at 1 us - the same frames, no rounding steps."""
    ts, sc = sg.get('times'), sg.get('speed_curve')
    if not ts or not sc or len(ts) < 2:
        return
    n = len(ts)
    try:
        rates = np.interp(np.arange(n), [float(k) for k, _ in sc], [float(r) for _, r in sc])
    except (TypeError, ValueError):
        return
    exact = float(ts[0]) + np.concatenate([[0.0], np.cumsum(rates[:-1])]) / fps
    if float(np.max(np.abs(exact - np.asarray(ts, float)))) <= 2.5e-4:
        sg['times'] = [round(float(x), 6) for x in exact]


def build_edit_planner(p, f0, m, beats, ctx, expect_frames):
    """ed_plan.plan_genre for one part of the sequence (n_shots, order, require_moves, music_in, drop_at, bars,
    sfx_level, in_sequence, style, variant, avoid); its EDL is checked against the request and shifted into place.
    None = not usable."""
    plan_genre = _fn('ed_plan', 'plan_genre')
    if plan_genre is None:
        return None, 'ed_plan.plan_genre not available'
    fps = ctx.fps
    track_t0 = m['in'] + (f0 / fps - m['at'])
    pos = 'only' if len(ctx.S['parts']) == 1 else ('first' if p['index'] == 0 else
                                                     ('last' if p['index'] == len(ctx.S['parts']) - 1 else 'middle'))
    opts = dict(n_shots=p['shots'], order=p['order'], require_moves=p['moves'], forbid_moves=p['forbid'],
                music_in=round(track_t0, 4), bars=p['bars'], sfx_level=p['sfx'], in_sequence=pos,
                cache_dir=ctx.cache_dir, seed=int(p.get('seed', 1)), log=ctx.log)
    if m.get('drop_here'):
        opts.update(drop_at=0.0, drop_t=round(m['drop'], 4))
    for key in ('style', 'variant'):                               # house style / another version (r5 planner)
        if p.get(key) is not None:
            opts[key] = p[key]
    if p.get('avoid'):
        opts['avoid'] = _part_avoid(p['avoid'], p['id'])
    try:
        e = plan_genre(m['path'], p['footage'], p['genre'], (ctx.W, ctx.H), fps, None, **opts)
    except Exception as ex:  # noqa: BLE001
        return None, f'plan_genre failed: {type(ex).__name__}: {ex}'
    segs = e.get('segments') or []
    problems = []
    if abs(int(e.get('n_frames', 0)) - expect_frames) > 2:
        problems.append(f'{e.get("n_frames")} frames instead of {expect_frames}')
    if len(segs) != p['shots']:
        problems.append(f'{len(segs)} shots instead of {p["shots"]}')
    srcs = e.get('sources') or {}
    if p['order'] == 'given' and len(segs) == p['shots']:
        got = [os.path.abspath(srcs.get(s.get('src'), {}).get('path', '')) for s in segs]
        want = [os.path.abspath(p['footage'][i % len(p['footage'])]) for i in range(p['shots'])]
        if got != want:
            problems.append('shot order differs from the given footage order')
    mi = ((e.get('audio') or {}).get('music') or {}).get('in')
    if mi is None or abs(float(mi) - track_t0) > 1.5 / fps:
        problems.append(f'music in {mi} instead of {track_t0:.3f}')
    if p['moves']:
        used = set()
        for s in segs:
            used |= {fx.get('move') for fx in s.get('fx') or []}
            if s.get('speed_curve') or s.get('times'):
                used.add('time.speed_ramp' if any(r < 0.6 for _, r in (s.get('speed_curve') or [[0, 1]])) else 'time.velocity')
        missing = [mv for mv in p['moves'] if mv not in used and not any(str(u).startswith(mv) for u in used if u)]
        if missing:
            problems.append(f'required moves not visible: {missing}')
    if problems:
        return None, 'planner result rejected: ' + '; '.join(problems)
    T0 = f0 / fps
    em = e.get('meta') or {}
    sections = {}
    for name, v in (em.get('parts') or {}).items() if isinstance(em.get('parts'), dict) else []:
        fr = v.get('f') if isinstance(v, dict) else v
        if isinstance(fr, (list, tuple)) and len(fr) == 2 and int(fr[1]) >= int(fr[0]):
            sections[name] = [int(fr[0]) + f0, int(fr[1]) + f0]
    out = _part_out(meta=dict(engine='ed_plan.plan_genre', genre=p['genre'], sections=sections,
                              style=em.get('style'), variant=em.get('variant'), choices=_planner_choices(e),
                              planner_meta={k: v for k, v in em.items()
                                            if k in ('window', 'parts', 'notes', 'reasons', 'genre')}))
    rename = {}
    for name, cfg in srcs.items():
        rename[name] = ctx.source(f'{p["id"]}_{name}', cfg)
    for s in segs:
        s = copy.deepcopy(s)
        _sharpen_times(s, fps)
        s['f0'] += f0
        s['f1'] += f0
        s['id'] = ctx.seg_id('E')
        s['src'] = rename.get(s.get('src'), s.get('src'))
        for gh in s.get('ghosts') or []:
            if gh.get('src') in rename:
                gh['src'] = rename[gh['src']]
        for fx in s.get('fx') or []:
            _shift_times(fx, T0, keys=('at', 't', 'times'))
        s['part'] = p['id']
        out['segments'].append(s)
    for o in e.get('ops') or []:
        o = copy.deepcopy(o)
        o['f'] = _shift_frames(o.get('f'), f0)
        out['ops'].append(o)
    for Ly in e.get('layers') or []:
        Ly = copy.deepcopy(Ly)
        for k in ('f0', 'f1'):
            if isinstance(Ly.get(k), int):
                Ly[k] += f0
        _shift_times(Ly, T0, keys=('t0', 't1'))
        for key in ('words', 'slots', 'chunks'):
            for it in Ly.get(key) or []:
                if isinstance(it, dict):
                    _shift_times(it, T0, keys=('t', 't0', 't1'))
                    for k in ('f', 'f0', 'f1'):
                        if isinstance(it.get(k), int):
                            it[k] += f0
        out['layers'].append(Ly)
    au = e.get('audio') or {}
    for ev in au.get('sfx') or []:
        ev = copy.deepcopy(ev)
        _shift_times(ev, T0, keys=('at', 't'))
        out['sfx'].append(ev)
    for op in au.get('music_fx') or []:
        op = copy.deepcopy(op)
        _shift_times(op, T0)
        out['music_fx'].append(op)
    for rule in au.get('duck') or []:
        rule = copy.deepcopy(rule)
        if rule.get('t') is not None:
            _shift_times(rule, T0, keys=('t',))
        out['duck'].append(rule)
    q = e.get('qa') or {}
    out['planned_white'] = [x + f0 for x in _frames_of(q.get('planned_white'))]
    out['planned_black'] = [x + f0 for x in _frames_of(q.get('planned_black'))]
    out['planned_freeze'] = [[a + f0, b + f0] for a, b in (q.get('planned_freeze') or []) if isinstance(a, int)]
    out['f1'] = out['segments'][-1]['f1']
    return out, 'ok'


def _op_frames(o):
    """Frames of an op's "f": int | "a:b" | [frames or "a:b" strings]."""
    f = o.get('f')
    if isinstance(f, (int, str)):
        f = [f]
    out = []
    for v in f or []:
        if isinstance(v, str) and ':' in v:
            a, b = v.split(':')[:2]
            out += list(range(int(a), int(b) + 1))
        elif isinstance(v, (int, float)) or (isinstance(v, str) and v.strip().isdigit()):
            out.append(int(v))
    return out


def _frames_of(spec):
    out = []
    for v in spec or []:
        if isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(x, int) for x in v):
            out += list(range(v[0], v[1] + 1))
        elif isinstance(v, str) and ':' in v:
            a, b = v.split(':')[:2]
            out += list(range(int(a), int(b) + 1))
        elif isinstance(v, (int, float)):
            out.append(int(v))
    return out


def build_edit(p, f0, m, beats, ctx):
    fps = ctx.fps
    track_t0 = m['in'] + (f0 / fps - m['at'])
    cuts, _ = edit_grid(p, beats, track_t0)
    expect = frame_at(m['at'] + (cuts[-1] - m['in']), fps) - f0
    engine = p.get('engine', 'auto')
    why = 'recipe requested'
    if engine in ('auto', 'planner'):
        res, why = build_edit_planner(p, f0, m, beats, ctx, expect)
        if res is not None:
            ctx.log(f'[sequence] {p["id"]}: ed_plan.plan_genre ({p["genre"]}, {p["shots"]} shots, {p["bars"]} bars)')
            return res
        if engine == 'planner':
            raise SpecError(f'part {p["id"]}: {why}')
        ctx.log(f'[sequence] {p["id"]}: {why} -> local recipe')
    res = build_edit_recipe(p, f0, m, beats, ctx)
    res['meta']['planner_note'] = why
    return res


# ============================================================================ assembly
def music_level_ops(t0, t1, db, swell=None, steps=8):
    """audio.music_fx gain automation: the bed at `db` over [t0, t1]; swell = (seconds, to_db) lifts it in smoothed
    steps over the last seconds and returns to full level exactly at t1 (the next part's first frame)."""
    if db is None or db >= -0.05 or t1 <= t0:
        return []
    if not swell or swell[0] <= 0:
        return [dict(op='gain', t=[round(t0, 4), round(t1, 4)], db=round(db, 2), attack_ms=40, release_ms=8,
                     curve='hold', move='mix.bed')]
    s = min(float(swell[0]), t1 - t0)
    to_db = min(float(swell[1]), -0.5)
    ops, step = [], s / steps
    for i in range(steps):
        e = t1 - s + (i + 1) * step
        lvl = db + (to_db - db) * i / max(1, steps - 1)
        ops.append(dict(op='gain', t=[round(t0, 4), round(e, 4)], db=round(lvl, 2), attack_ms=40,
                        release_ms=round(6 if i == steps - 1 else 0.35 * step * 1000, 1), curve='hold',
                        move='mix.swell' if i else 'mix.bed'))
    return ops


RISER_BY_VERSION = ('noise', 'tonal', 'reverse_cymbal')      # ed_sfx riser flavours, one per version (mod 3)
IMPACT_BY_VERSION = ('boom', 'stretched', 'chord')
SUB_BY_VERSION = ('classic', 'long', 'classic')


def _boundary_sfx(kinds, T, level, pre_s, bar_s, gap, version=0):
    """SFX events on a part boundary at output time T. kinds from the transition ('auto' = by level); `version`
    (the next part's variant) picks the riser / impact / sub flavour, so another version also sounds different."""
    out = []
    lv = 'strong' if level == 'heavy' else ('light' if level == 'light' else 'normal')
    v = int(version or 0) % 3
    for k in kinds:
        if k == 'riser':
            dur = min(bar_s, max(0.8, pre_s - gap))
            fl = RISER_BY_VERSION[v] if not (RISER_BY_VERSION[v] == 'reverse_cymbal' and dur < 1.0) else 'noise'
            if pre_s - gap >= 0.6:
                out.append(dict(kind='riser', variant=fl, at=round(T - gap, 4), align='peak', dur=round(dur, 3),
                                level=lv, move='sfx.riser', why='build into the drop'))
        elif k == 'impact':
            out.append(dict(kind='impact', variant=IMPACT_BY_VERSION[v], at=round(T, 4), align='attack', level=lv,
                            move='sfx.impact', why='hit on the drop'))
        elif k == 'sub_drop':
            out.append(dict(kind='sub_drop', variant=SUB_BY_VERSION[v], at=round(T, 4), align='attack', level=lv,
                            move='sfx.sub_drop', why='low end under the drop'))
        elif k in ('whoosh', 'reverse_whoosh', 'swell', 'glitch', 'click'):
            out.append(dict(kind=k, at=round(T, 4), align='peak' if k in ('whoosh', 'reverse_whoosh', 'swell') else 'attack',
                            level=lv, move=f'sfx.{k}', why='transition'))
    return out


def _auto_kinds(level, kind):
    if level == 'none':
        return []
    if kind in ('whip', 'zoom', 'spin', 'push', 'slide'):
        return ['whoosh'] + (['impact'] if level == 'heavy' else [])
    if kind == 'glitch':
        return ['glitch']
    if kind in ('dissolve', 'fade', 'luma', 'light_leak'):
        return ['swell'] if level != 'light' else []
    if level == 'light':
        return ['impact']
    return ['riser', 'impact', 'sub_drop']


def _styled_kind(pb):
    """Default talk -> edit transition under a house style: a punchy kind from the style's palette (flash, cut,
    zoom, whip, glitch, light leak), rotated by the version number; no style -> flash."""
    info = style_info(pb.get('style'), pb.get('variant')) if pb.get('style') else None
    pal = [t.split('.', 1)[-1] for t in (info or {}).get('transitions') or []]
    punchy = [k for k in ('flash', 'cut', 'zoom', 'whip', 'glitch', 'light_leak') if k in pal] or ['flash', 'cut']
    if info is None:
        punchy = ['flash', 'zoom', 'cut']
    return punchy[int(pb.get('variant') or 0) % len(punchy)]


def _ev_at(ev, default=0.0):
    """Output second where an audio.sfx event lands - ed_sfx.event_anchor ("at"; a range "t": [t0, t1] lands on t1
    for builds - risers, whooshes, swells - and on t0 for hits); default when it has no time."""
    f = _fn('ed_sfx', 'event_anchor')
    if f is not None:
        try:
            v = f(ev)
            return default if v is None else float(v)
        except Exception:  # noqa: BLE001
            pass
    if ev.get('at') is not None:
        return float(ev['at'])
    t = ev.get('t')
    if isinstance(t, (list, tuple)) and len(t) == 2:
        return float(t[1]) if ev.get('kind') in ('riser', 'whoosh', 'reverse_whoosh', 'swell') else float(t[0])
    return default


def _dedupe_sfx(events, tol=0.06):
    out = []
    for ev in sorted(events, key=lambda e: (_ev_at(e), e.get('kind', ''))):
        dup = next((o for o in out if o.get('kind') == ev.get('kind') and abs(_ev_at(o) - _ev_at(ev)) <= tol), None)
        if dup is None:
            out.append(ev)
    return out


def plan_sequence(spec, cache_dir=None, log=print):
    """Spec (dict or path; see the module docstring) -> EDL dict with meta.parts. Raises SpecError on a spec that
    cannot be planned (missing file, phrase not found, ...) with a message meant for the user."""
    t_start = time.time()
    log = log or (lambda *a, **k: None)
    if isinstance(spec, str):
        spec = load_spec(spec)
    spec_in = copy.deepcopy(spec)
    S = normalize_spec(spec)
    cache_dir = cache_dir or DEFAULT_CACHE
    os.makedirs(cache_dir, exist_ok=True)
    ctx = _Ctx(S, cache_dir, log)
    fps = ctx.fps
    parts = S['parts']
    edits = [p for p in parts if p['type'] == 'edit']
    if edits and not S['music']:
        raise SpecError('edit parts need "music": {"path": ...}')
    # 1. music
    mus = beats = None
    if S['music']:
        t = time.time()
        mus = analyze_music(S['music']['path'], cache_dir, log)
        beats = Beats(mus)
        log(f'[sequence] music: {mus["bpm"]:.1f} BPM, {mus["duration"]:.1f} s ({time.time() - t:.0f} s)')
    # 2. talk / clip parts: words, cut points, crops (needed for the frame layout)
    prep = {}
    for p in parts:
        if p['type'] in ('talk', 'clip'):
            t = time.time()
            prep[p['id']] = prepare_source_part(p, ctx)
            log(f'[sequence] {p["id"]}: ready ({time.time() - t:.0f} s)')
    # 3. where the drop lands: frames of the parts before the anchor
    est = {}
    for p in parts:
        if p['type'] == 'edit':
            est[p['id']] = int(round(4 * p['bars'] * beats.period * fps))
        else:
            sfps = float(prep[p['id']]['info'].get('fps') or fps)
            sp = float(p.get('speed', 1.0) or 1.0)
            est[p['id']] = sum(int(round((b - round(a * sfps) / sfps) * fps / sp)) for a, b in prep[p['id']]['rr']['keep'])
    m = None
    anchor = None
    if S['music']:
        mu = S['music']
        da = mu.get('drop_at') or ({'part': edits[0]['id'], 'at': 'start'} if edits else None)
        T_anchor, after = None, 0.0
        if da is not None:
            fa = 0
            for p in parts:
                if p['id'] == da['part']:
                    break
                fa += est[p['id']]
            at = da.get('at', 'start')
            fa += est[da['part']] if at == 'end' else (0 if at == 'start' else int(round(float(at) * fps)))
            T_anchor = fa / fps
            after = (sum(est.values()) - fa) / fps
            anchor = dict(part=da['part'], at=at, frame=fa)
        if mu.get('in') is not None:
            m_in, why, cands, t_drop = float(mu['in']), 'music.in given', [], None
        elif T_anchor is not None:
            t_drop, why, cands = pick_drop(mus, need_after=after, given=mu.get('drop'))
            j = beats.index(t_drop)
            if abs(beats.time(j) - t_drop) <= 0.05 and mu.get('drop') is None:
                t_drop = beats.time(j)
            m_in = t_drop - T_anchor
        else:
            j = beats.next_down(0.0)
            t_drop, why, cands, m_in = None, 'no edit part: the bed starts on the first downbeat', [], beats.time(j)
        m = dict(path=mu['path'], at=round(max(0.0, -m_in), 6), **{'in': round(max(0.0, m_in), 6)}, drop=t_drop,
                 why=why, cands=cands, anchor=anchor, m_in=m_in)
        if m_in < 0:
            log(f'[sequence] music starts at {-m_in:.2f} s of the output (the part before the drop is longer than the '
                f'track before its drop)')
        if t_drop is not None:
            log(f'[sequence] drop: track {t_drop:.3f} s -> output frame {anchor["frame"]} ({why})')
            if str(why).startswith(NO_DROP):
                ctx.notes.append(f'music: {why}')
    # 4. parts in order
    outs, f = [], 0
    for p in parts:
        t = time.time()
        if p['type'] == 'edit':
            mm = dict(m, drop_here=bool(anchor and anchor['part'] == p['id'] and anchor['at'] == 'start'))
            res = build_edit(p, f, mm, beats, ctx)
        else:
            res = build_source_part(p, f, prep[p['id']], ctx)
        res['f0'] = f
        res['part'] = p
        outs.append(res)
        log(f'[sequence] {p["id"]} ({p["type"]}): frames {f}-{res["f1"]} ({(res["f1"] - f + 1) / fps:.2f} s, '
            f'{len(res["segments"])} segments, {time.time() - t:.0f} s)')
        f = res['f1'] + 1
    n_frames = f
    T_total = n_frames / fps
    if anchor is not None and anchor['part'] in [o['part']['id'] for o in outs] and anchor['at'] == 'start':
        real = next(o['f0'] for o in outs if o['part']['id'] == anchor['part'])
        if real != anchor['frame']:
            ctx.notes.append(f'drop planned on frame {anchor["frame"]}, part starts on {real} (edit part before the anchor)')
    # 5. transitions between consecutive parts
    ops, sfx, planned_white, planned_black = [], [], [], []
    trans_meta = []
    bar_s = 4 * beats.period if beats is not None else 2.0
    for A, B in zip(outs, outs[1:]):
        pa, pb = A['part'], B['part']
        tr = next((x for x in S['transitions'] if x['from'] == pa['id'] and x['to'] == pb['id']), None)
        default_flash = pa['type'] in ('talk', 'clip') and pb['type'] == 'edit'
        kind = tr['kind'] if tr else ('flash' if default_flash else 'cut')
        if tr is None and default_flash and (pb.get('style') or pb.get('variant')):
            kind = _styled_kind(pb)                                   # the style's palette, rotated per version
        fb = B['f0']
        T = fb / fps
        lvl = max(pa['sfx'], pb['sfx'], key=SFX_LEVELS.index)
        sfx_spec = (tr or {}).get('sfx', 'auto' if (default_flash or kind != 'cut') else 'none')
        kinds = _auto_kinds(lvl, kind) if sfx_spec == 'auto' else \
            ([] if sfx_spec in (None, 'none', False) else ([sfx_spec] if isinstance(sfx_spec, str) else list(sfx_spec)))
        drop_on_b = bool(anchor and anchor['part'] == pb['id'] and anchor['at'] == 'start')
        if drop_on_b and lvl in ('genre', 'heavy'):
            for k in ('riser', 'impact', 'sub_drop'):                # the drop package of the edit part's level
                if k not in kinds:
                    kinds.append(k)
        # the next part may already open with its own hit (a planner part in a sequence puts the drop's impact /
        # sub drop on its frame 0): never a second one of a kind on the boundary
        own = {x.get('kind') for x in B['sfx'] if abs(_ev_at(x, -9.0) - T) <= 0.1}
        skipped = [k for k in kinds if k in own]
        kinds = [k for k in kinds if k not in own]
        pre_s = (T - A['react_out']) if A.get('react_out') is not None else (T - A['f0'] / fps)
        gap = beats.period / 4 if (beats is not None and pb['type'] == 'edit' and pb.get('genre') == 'epic') else 0.0
        b_sfx = _boundary_sfx(kinds, T, lvl, pre_s, bar_s, gap, version=pb.get('variant') or 0)
        sfx += b_sfx
        if kind == 'flash':
            if not any(o.get('op') in ('flash', 'white') and fb in _op_frames(o) for o in B['ops']):
                n_fl = int((tr or {}).get('frames', 4))
                curve = [0.95, 0.62, 0.32, 0.14, 0.06][:max(2, n_fl)]
                ops.append(dict(f=f'{fb}:{fb + len(curve) - 1}', op='flash', color=[1, 1, 1], curve=curve,
                                blend='screen', move='trans.flash'))
                planned_white.append(fb)
        elif kind != 'cut':
            n_tr = int((tr or {}).get('frames', 6))
            B['segments'][0]['transition_in'] = dict(kind=kind, frames=n_tr, align='center',
                                                     params=dict((tr or {}).get('params') or {}))
        trans_meta.append(dict(**{'from': pa['id'], 'to': pb['id']}, kind=kind, frame=fb, sfx=kinds,
                               flavours={x['kind']: x.get('variant') for x in b_sfx},
                               **({'sfx_from_part': skipped} if skipped else {})))
    # 6. audio
    segments = [s for o in outs for s in o['segments']]
    voice = [v for o in outs for v in o['voice']]
    for v in voice:
        v.pop('part', None)
    music_fx, duck = [], []
    for o in outs:
        music_fx += o['music_fx']
        duck += o['duck']
        sfx += o['sfx']
        ops += o['ops']
        planned_white += o.get('planned_white', [])
        planned_black += o.get('planned_black', [])
    if m is not None:
        for i, o in enumerate(outs):
            p = o['part']
            if p['type'] not in ('talk', 'clip') or not o['has_voice']:
                continue
            db = float(p.get('music_db', -18.0))
            t0, t1 = o['f0'] / fps, (o['f1'] + 1) / fps
            nxt = outs[i + 1]['part'] if i + 1 < len(outs) else None
            sw = p.get('swell', {})
            swell = None
            if nxt is not None and nxt['type'] == 'edit' and sw is not False:
                sw = sw if isinstance(sw, dict) else {}
                s_len = float(sw.get('s', min(0.6, beats.period * 1.3)))
                swell = (s_len, float(sw.get('to_db', db / 2)))
            music_fx += music_level_ops(t0, t1, db, swell)
        if voice:
            duck.append(dict(under='voice', depth_db=6.0, attack_ms=40, release_ms=300))
    sfx = [e for e in _dedupe_sfx(sfx) if 0.0 <= _ev_at(e) <= T_total + 0.5]
    audio = dict(copy=False, voice=voice, sfx=sfx, music_fx=music_fx, duck=duck,
                 loudness=dict(lufs=S['loudness']['lufs'], tp=S['loudness']['tp']))
    if S.get('sfx_dir'):
        audio['sfx_dir'] = S['sfx_dir']                        # events without a file take the best-named sound
    if m is not None:
        mu = S['music']
        fade_in = float(mu.get('fade_in', 0.6 if outs[0]['part']['type'] != 'edit' else 0.0))
        audio['music'] = dict(path=m['path'], at=m['at'], **{'in': m['in']}, gain_db=float(mu.get('gain_db', 0.0)),
                              fade_in=fade_in, fade_out=float(mu.get('fade_out', 0.4)))
        off = m['at'] - m['in']
        bt = [round(float(x) + off, 4) for x in beats.t if 0.0 <= float(x) + off <= T_total and float(x) >= 0.0]
        dn = [round(beats.time(j) + off, 4) for j in range(len(beats.t)) if beats.is_down(j)
              and 0.0 <= beats.time(j) + off <= T_total and beats.time(j) >= 0.0]
        audio['grid'] = dict(bpm=float(mus['bpm']), beats=bt, downbeats=dn)
    else:
        audio['music'] = None
    # 7. the end: fade to black when the sequence ends on an edit part. A genre outro fade (epic: 1-1.5 s + 0.5 s
    # of black) is kept on long parts but shortened on short ones (a 5-bar hype edit must not lose its last shot);
    # the music fades with the picture.
    last = outs[-1]
    tail = sorted((x for o in ops if o.get('op') == 'black' for x in _op_frames(o)
                   if x >= last['f0']), reverse=True)
    span = 0
    if tail and tail[0] >= n_frames - 3:
        span = 1
        while span < len(tail) and tail[span] == tail[span - 1] - 1:
            span += 1
    short = last['part']['type'] == 'edit' and (last['f1'] - last['f0'] + 1) / fps <= 12.0
    if 'fade' in S['end']:
        target = float(S['end']['fade'])
    elif span:
        target = min(span / fps, 0.5) if short else span / fps
    else:
        target = 0.27 if last['part']['type'] == 'edit' else 0.0
    nf = int(round(target * fps))
    if span and nf != span:                               # replace the existing tail fade
        drop = set(range(n_frames - span, n_frames))
        ops = [o for o in ops if not (o.get('op') == 'black' and set(_op_frames(o)) & drop)]
        planned_black = [x for x in planned_black if x not in drop]
        notes_end = f'end fade {span / fps:.2f} s -> {nf / fps:.2f} s (short final part keeps its last shot)'
        ctx.notes.append(notes_end)
        span = 0
    if nf >= 2 and not span:
        for k in range(nf):
            a = (k + 1) / nf
            ff = n_frames - nf + k
            ops.append(dict(f=[ff], op='black', a=round(_ease(a, 'inOutSine'), 3), stage='post', move='trans.fade'))
            if _ease(a, 'inOutSine') >= 0.85:
                planned_black.append(ff)
    pic_fade = (span or nf) / fps
    if audio.get('music') and 'fade_out' not in (S['music'] or {}):
        audio['music']['fade_out'] = round(max(0.4, pic_fade + 0.1), 3)
    # 8. QA + meta
    words = [w for o in outs for w in o['words']]
    genre = edits[0]['genre'] if edits else 'clips'
    parts_meta = []
    for o in outs:
        p = o['part']
        pm = dict(id=p['id'], type=p['type'], f0=o['f0'], f1=o['f1'], t0=_r(o['f0'] / fps), t1=_r((o['f1'] + 1) / fps),
                  segments=[s['id'] for s in o['segments']])
        if p['type'] == 'edit':
            pm.update(genre=p['genre'], bars=p['bars'], shots=p['shots'], engine=o['meta'].get('engine'),
                      sfx=p['sfx'], drop_frame=o['f0'] if anchor and anchor['part'] == p['id'] else None,
                      sections=dict(o['meta'].get('sections') or {}),          # hook / build / drop / outro frames
                      style=o['meta'].get('style') or (style_info(p.get('style')) or {}).get('name'),
                      variant=o['meta'].get('variant', p.get('variant')))
        else:
            pm.update(source=p['source'], keep=o['meta']['keep'])
            if o['meta'].get('lip_sync'):                               # what was measured / corrected (lip sync)
                pm.update(av_offset=o['meta']['lip_sync'].get('offset', 0.0), lip_sync=o['meta']['lip_sync'])
            if p.get('tighten_pauses'):                                 # QA judges pauses inside shots then
                pm['tighten_pauses'] = 0.35 if p['tighten_pauses'] is True else float(p['tighten_pauses'])
        parts_meta.append(pm)
    q = dict(genre=genre, safe_zone=dict(VERTICAL_UI_ZONE) if ctx.H >= ctx.W else 'title_safe', flash_limit_hz=3, lufs=S['loudness']['lufs'], lufs_tol=1.0,
             tp_max=S['loudness']['tp'], planned_white=sorted(set(planned_white)), planned_black=sorted(set(planned_black)),
             planned_freeze=[x for o in outs for x in o.get('planned_freeze', [])],
             source_cuts=sorted({x for o in outs for x in o.get('source_cuts', [])}),
             parts=[dict(id=pm['id'], type=pm['type'], f0=pm['f0'], f1=pm['f1'],
                         mode='speech' if pm['type'] in ('talk', 'clip') else 'music',
                         **({'on_word_share': 1.0} if pm['type'] in ('talk', 'clip') else {'on_beat_share': 0.9}))
                    for pm in parts_meta])
    # cuts that are meant to sit on the beat grid: inside edit parts and on the start of an edit part
    cut_f = [s['f0'] for s in segments[1:]]
    on_grid = [f_ for f_ in cut_f if any(o['part']['type'] == 'edit' and o['f0'] <= f_ <= o['f1'] for o in outs)]
    q['on_beat_share'] = round(0.9 * len(on_grid) / max(1, len(cut_f)), 3) if cut_f else 0.9
    if words:
        q.update(words=[dict(w=w['w'], t0=w['t0'], t1=w['t1']) for w in words], on_word_share=1.0)
    q.update(S.get('qa') or {})
    notes = list(ctx.notes)
    for o in outs:
        notes += [f'{o["part"]["id"]}: {n}' for n in (o['meta'].get('notes') or [])]
        if o['meta'].get('planner_note') and o['meta']['planner_note'] != 'recipe requested':
            notes.append(f'{o["part"]["id"]}: {o["meta"]["planner_note"]}')
    first_edit = next((o for o in outs if o['part']['type'] == 'edit'), None)
    choices = dict((first_edit or {}).get('meta', {}).get('choices') or {})
    choices.setdefault('variant', (first_edit or {}).get('meta', {}).get('variant') or
                       (first_edit['part'].get('variant') if first_edit else S.get('variant')) or 0)
    choices['sequence'] = dict(transitions={t['to']: t['kind'] for t in trans_meta},
                               boundary_sfx={t['to']: t.get('flavours') or {} for t in trans_meta},
                               talk={o['part']['id']: (o['meta'].get('choices') or {}) for o in outs
                                     if o['part']['type'] != 'edit'})
    edl = dict(canvas=dict(w=ctx.W, h=ctx.H, fps=fps), n_frames=n_frames, frame_interp='flow', sources=ctx.sources,
               audio=audio, segments=segments, ops=ops, texts=[], layers=[Ly for o in outs for Ly in o['layers']], qa=q,
               meta=dict(scenario='sequence', planner=PLANNER, genre=genre, version=1, parts=parts_meta,
                         style=(first_edit or {}).get('meta', {}).get('style') or (style_info(S.get('style')) or {}).get('name'),
                         variant=int(choices.get('variant') or 0), choices=choices,
                         sequence=dict(music=None if m is None else dict(
                             path=m['path'], drop_track=None if m['drop'] is None else round(m['drop'], 4),
                             drop_frame=None if anchor is None else anchor['frame'], **{'in': m['in']}, at=m['at'],
                             why=m['why'], candidates=m['cands']),
                             transitions=trans_meta, parts={o['part']['id']: o['meta'] for o in outs},
                             spec=_plain(dict(spec_in, base_dir=S['base_dir']))),
                         notes=notes, took_s=round(time.time() - t_start, 1)))
    edl = _plain(edl)
    # both validators on our own output (renderer side + planner contract)
    val = dict(errors=[], warnings=[])
    vf = _fn('ed_edl', 'validate')
    if vf is not None:
        try:
            for x in vf(edl) or []:
                (val['errors'] if x.get('level') == 'error' else val['warnings']).append(
                    f"ed_edl: {x.get('where', '')} {x.get('msg', '')}".strip())
        except Exception as ex:  # noqa: BLE001
            val['warnings'].append(f'ed_edl.validate failed: {type(ex).__name__}: {ex}')
    pf = _fn('ed_plan', 'validate_edl')
    if pf is not None:
        try:
            errs, warns = pf(edl)
            val['errors'] += [f'ed_plan: {x}' for x in errs]
            val['warnings'] += [f'ed_plan: {x}' for x in warns]
        except Exception as ex:  # noqa: BLE001
            val['warnings'].append(f'ed_plan.validate_edl failed: {type(ex).__name__}: {ex}')
    edl['meta']['validation'] = val
    for x in val['errors']:
        log(f'[sequence] VALIDATION ERROR {x}')
    log(f'[sequence] {len(segments)} segments, {n_frames} frames ({T_total:.2f} s), {len(sfx)} SFX, '
        f'{len(edl["layers"])} subtitle chunks, validation {len(val["errors"])} errors / {len(val["warnings"])} '
        f'warnings ({time.time() - t_start:.0f} s)')
    return edl


def variant(edl, variant=None, style=None, cache_dir=None, log=print):
    """Another version of a sequence: re-plans the spec stored in the EDL (meta.sequence.spec) with the next unused
    variant (or `variant`) and optionally another house style, steering away from the given version's choices (and
    the versions it already avoided). The cut points by words and the drop stay; looks, moves, shot windows, punch-ins
    and transitions change inside the same rules. edl: dict or path. -> EDL"""
    log = log or (lambda *a, **k: None)
    path = os.path.abspath(edl) if isinstance(edl, str) else None
    e = _load_json(path) if path else edl
    if not isinstance(e, dict):
        raise SpecError(f'cannot read {edl!r}')
    spec = copy.deepcopy(((e.get('meta') or {}).get('sequence') or {}).get('spec'))
    if not spec:
        raise SpecError('this EDL has no stored sequence spec (meta.sequence.spec): plan it with ed_sequence first')
    prev = spec.pop('avoid_versions', None) or spec.get('avoid') or []
    prev = list(prev) if isinstance(prev, list) else [prev]
    prev.append(path or e)
    used = set()
    for a in prev:
        try:
            ea = _load_json(a) if isinstance(a, str) else a
        except (OSError, ValueError):
            continue
        if isinstance(ea, dict):
            used.add(int((ea.get('meta') or {}).get('variant') or 0))
    if variant is None:
        variant = 0
        while variant in used:
            variant += 1
    spec['avoid'] = prev
    spec['variant'] = int(variant)
    if style:
        spec['style'] = style
    for q in spec.get('parts') or []:                    # the new version / style applies to every part
        for key in ('variant', 'avoid_versions') + (('style',) if style else ()):
            q.pop(key, None)
        if q.get('type') == 'edit':                      # (a talk / clip part's "avoid" = its overlay boxes)
            q.pop('avoid', None)
    log(f'[sequence] version {variant}' + (f', style {style!r}' if style else '') + f' (avoiding {len(prev)} earlier)')
    return plan_sequence(spec, cache_dir=cache_dir, log=log)


def resolve(spec, cache_dir=None, log=print):
    """Cheap check of a spec: where the phrases of talk / clip parts land (kept ranges with their text, removals,
    the reaction) and which drop the music alignment would use. No video analysis."""
    if isinstance(spec, str):
        spec = load_spec(spec)
    S = normalize_spec(spec)
    out = dict(parts=[], music=None)
    for p in S['parts']:
        if p['type'] == 'edit':
            out['parts'].append(dict(id=p['id'], type='edit', footage=[os.path.basename(x) for x in p['footage']],
                                     bars=p['bars'], shots=p['shots'], genre=p['genre']))
            continue
        words, winfo = get_words(p, log) if (p['type'] == 'talk' or p.get('subtitles') or any(
            isinstance(x, dict) and x.get('phrase') for x in (p.get('from'), p.get('to')))) else ([], {})
        words = clean_words(words, p.get('vocab'))
        if words:
            p = dict(p, _dur=float(_probe(p['source']).get('duration') or 0.0))     # long source: setup start
            dry = resolve_ranges(p, words, None, log=lambda *a, **k: None)
            env = Envelope(p['source'], max(0.0, dry['keep'][0][0] - 3), dry['keep'][-1][1] + 6)
            rr = resolve_ranges(p, words, env, log)
        else:
            rr = dict(keep=[[p['from']['t'], p['to']['t']]], removed=[], reaction=None, notes=[])
        keep = [dict(t0=a, t1=b, text=' '.join(w['w'] for w in words if a - 0.02 <= w['t0'] and w['t1'] <= b + 0.05))
                for a, b in rr['keep']]
        out['parts'].append(dict(id=p['id'], type=p['type'], keep=keep, removed=rr['removed'], reaction=rr['reaction'],
                                 notes=rr['notes'], seconds=round(sum(b - a for a, b in rr['keep']), 3)))
    if S['music']:
        mus = analyze_music(S['music']['path'], cache_dir or DEFAULT_CACHE, log)
        t, why, cands = pick_drop(mus, given=S['music'].get('drop'))
        out['music'] = dict(bpm=mus['bpm'], drop=t, why=why, candidates=cands)
    return out


EXAMPLE = r'''// Edit Studio sequence spec: parts in a row on one canvas and one soundtrack.
// Plan:   python3 -I ed_sequence.py plan this.json --out edl_v1.json
// Check:  python3 -I ed_sequence.py resolve this.json    (where the phrases land, which drop is used)
{
  "canvas": {"w": 1080, "h": 1920, "fps": 30},          // vertical 9:16
  "parts": [
    {"type": "talk", "id": "talk",
     "source": "interview.mp4",                         // a screen recording is fine: the player UI, logos and
                                                        // lower thirds are detected and kept out of the frame
     "lang": "en", "vocab": ["Korvanta"],               // ASR language + names the recogniser splits
     "from": {"phrase": "the real question is"},        // or seconds: "from": 24.05
     "to": {"phrase": "three million a year", "end": "after_reaction"},   // keep the laugh / "Wow" after it
     "remove": [{"phrase": "Let me check my notes."}],
     "tighten_pauses": null,                            // seconds: shorten longer pauses (never the reaction)
     "crop": "speaker",                                 // follow the active speaker, one framing per camera shot
     "subtitles": "subtitle",                           // or "karaoke", a caption preset name, or null
     "music_db": -18},                                  // music bed under the talk (swells into the next part)
    {"type": "edit", "id": "hype",
     "footage": ["shots/g1.mp4", "shots/g2.mp4", "shots/g3.mp4", "shots/g4.mp4", "shots/g5.mp4"],
     "order": "given",                                  // shot i = footage i ("auto": the planner chooses)
     "genre": "epic", "bars": 5, "shots": 5,            // one shot per bar from the drop
     "moves": ["time.speed_ramp"],                      // required moves
     "sfx": "heavy"}                                    // none | light | genre | heavy
  ],
  "music": {"path": "track.wav",
            "drop_at": {"part": "hype", "at": "start"}},   // the strongest drop lands on the first frame of "hype"
  "transitions": [{"from": "talk", "to": "hype", "kind": "flash", "sfx": "impact"}]
  // , "sfx_dir": "sounds"                            // your own sound effects folder (else they are synthesized)
}
'''


def main(argv=None):
    ap = argparse.ArgumentParser(prog='ed_sequence.py', description='Composite edits (talk + edit + clip parts) -> EDL')
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('plan', help='plan a spec into an EDL')
    a.add_argument('spec')
    a.add_argument('--out', required=True)
    a.add_argument('--cache', default=None, help='cache folder (default ~/.cache/edit-studio/sequence)')
    a.add_argument('--quiet', action='store_true')
    b = sub.add_parser('resolve', help='where the phrases land + the drop (no video work)')
    b.add_argument('spec')
    b.add_argument('--cache', default=None)
    sub.add_parser('example', help='print a commented example spec')
    c = sub.add_parser('variant', help='another version of a planned sequence EDL (next unused variant)')
    c.add_argument('edl')
    c.add_argument('--out', required=True)
    c.add_argument('--variant', type=int, default=None)
    c.add_argument('--style', default=None, help='house style: a preset name or plain words')
    c.add_argument('--cache', default=None)
    c.add_argument('--quiet', action='store_true')
    args = ap.parse_args(argv)
    if args.cmd == 'example':
        print(EXAMPLE)
        return 0
    log = (lambda *x, **k: None) if getattr(args, 'quiet', False) else (lambda *x, **k: print(*x, flush=True))
    try:
        if args.cmd == 'resolve':
            print(json.dumps(resolve(args.spec, args.cache, log), indent=1, ensure_ascii=False))
            return 0
        if args.cmd == 'variant':
            edl = variant(args.edl, args.variant, args.style, cache_dir=args.cache, log=log)
        else:
            edl = plan_sequence(args.spec, cache_dir=args.cache, log=log)
    except SpecError as e:
        print(f'[sequence] spec problem: {e}', file=sys.stderr)
        return 2
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(edl, f, indent=1, ensure_ascii=False)
    for pm in edl['meta']['parts']:
        print(f'  {pm["id"]:<10} {pm["type"]:<5} frames {pm["f0"]:>5}-{pm["f1"]:<5} {pm["t0"]:7.2f}-{pm["t1"]:.2f} s')
    for n in edl['meta']['notes']:
        print(f'  note: {n}')
    for x in (edl['meta'].get('validation') or {}).get('errors') or []:
        print(f'  VALIDATION ERROR: {x}')
    print(out)
    mv = re.match(r'edl_v(\d+)\.json$', os.path.basename(out))
    prev = os.path.join(os.path.dirname(out), f'preview_v{mv.group(1)}.mp4' if mv else
                        os.path.splitext(os.path.basename(out))[0] + '.preview.mp4')
    print(f'next: python3 -I {os.path.join(HERE, "ed_edl.py")} {out} {prev} --preview --labels')
    return 3 if (edl['meta'].get('validation') or {}).get('errors') else 0


if __name__ == '__main__':
    sys.exit(main())
