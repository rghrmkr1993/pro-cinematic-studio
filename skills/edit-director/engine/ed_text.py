#!/usr/bin/env python3
"""Animated text and graphics layers (TIMELINE.md §5) — code only: Pillow (FreeType + raqm shaping) draws the glyphs,
numpy / OpenCV animate and composite them. Every shipped font is an OFL file in engine/assets/fonts (licence next to
it); Chinese / Japanese / Korean faces (Noto Sans CJK, OFL) are downloaded on first use into FONT_CACHE (below).

API (ed_edl.py calls it — keep these signatures)
  render_layer(layer, f, fps, ow, oh, scale, ctx=None) -> (rgba, blend) | None
      rgba: float32 premultiplied (oh, ow, 4), a LayerRGBA (ndarray subclass): .bbox = (x0, y0, x1, y1) non-empty
      region, .opaque = full-frame card. Derived arrays drop the hints (composite() then scans alpha). None when the
      layer shows nothing on frame f; blend = layer['blend'] (default 'normal'). A fresh array per call; set
      ed_text.BUFFER_RING = n to reuse n buffers per size (~3 ms/frame less; a result is then valid until n more calls).
  composite(x, rgba, blend='normal', opacity=1.0) -> x
      x float32 (oh, ow, 3) 0..1, modified IN PLACE inside the bbox and returned. Blends (premultiplied maths):
      normal x(1−a)+c · difference x(1−a)+|x·a−c| · multiply x(1−a)+x·c · screen x+c(1−x) · add x+c.
  render_layers(x, layers, f, fps, scale, ctx=None) -> x   render + composite every layer in order (reuses one buffer)
  layer_span(layer, fps, ctx=None) -> (f0, f1)             inclusive output frames (a superset for word-driven kinds)
  layers_at(layers, f, fps, ctx=None) -> [i]               layers whose span contains f
  layout_words(words, font, size, max_width, max_lines, line_height, align, tracking, caps, min_size, max_height,
               balance, glue) -> Block                    wrap ('\\n' tokens force breaks), balance, auto-shrink (canvas px)
  helpers: text_length, char_offsets, font_ref, pil_font, raster, split_runs, chunk_words, format_number, ease,
           parse_anim, safe_rect, check_safe_zone, flash_guard, count_flashes, subject_mask, clear_caches,
           to_rgba / to_rgba_list (any colour format), keyword_indices, orient
  split_caption_layer(layer, ow, oh, fps=30, ctx=None) -> [layers]   a caption layer as the layers it is shown as
           at full size (see "Captions never shrink"); fit_caption_layers(layers, ow, oh, fps) maps a list
  text_fits(text, style, canvas=(1080, 1920), max_lines=None) -> {fits, lines, width_px, max_px, size_px, n_lines}
           a caption line / chunk measured with the real font exactly as the renderer wraps it (producers check
           their lines with it); caption_hints(name, ow, oh, text=None) -> {max_chars, max_lines, max_px, ...}
  registries: LAYER_KINDS {kind: class} — a KindRegistry: .spec(kind) -> {name, desc, params {name: default},
           landscape, choices, aliases, doc}, .describe(), .names(), .canonical(name); LAYER_SPECS,
           COMMON_LAYER_PARAMS; describe() -> JSON-ready {layers, common, caption_styles, anims, fonts, type_classes};
           FONT_FILES, TYPE_CLASSES, FONT_ALIASES, EASE, SAFE_ZONES, ANIM_LIB, CAPTION_STYLES, CJK_FONTS
  CLI: python3 -I ed_text.py registry [layers|caption_styles|all] [--md]   ·   python3 -I ed_text.py fonts "TEXT"
       [--font inter:800] [--lang ja] [--no-download]   (which fonts a text needs; fetches CJK faces)

Caption presets (talk clips: podcast / interview moments, 9:16 first) — a subtitle or karaoke layer takes
"style": "<name>" | {"preset": "<name>", ...style overrides} (or a top-level "preset"); preset fields fill what the
layer leaves unset (style, highlight, anim_in / anim_out, pos, max_width, avoid, chunk); a karaoke-only preset turns a
subtitle layer with words into karaoke. caption_style(name, **overrides) -> layer fields; caption_styles() ->
{name: {desc, kinds, voice}} where voice = chunking hints for producers (ed_voice.subtitle_chunks max_chars /
max_lines / max_words; max_chars from measured glyph widths, of the transcript when caption_hints gets text=, and
max_px the room for a line); text_fits(text, style, canvas) checks a line exactly; resolve_preset(layer) expands one. Aliases: aura/podcast/bold/clip -> podcast_bold,
caps -> podcast_caps, interview/minimal -> clean, box/plate -> boxed, karaoke/highlight/word -> karaoke_highlight,
karaoke_plate -> karaoke_box.
  podcast_bold       heavy white sans, mixed case, thin outline + soft shadow, numbers/keywords yellow, pop-in
  podcast_caps       condensed black caps, outline + shadow, keywords yellow, pop-in
  clean              semibold white, micro outline + wide soft dark halo, fade-in, lower
  boxed              bold white on a rounded dark plate per line, keywords yellow, soft pop-in
  karaoke_highlight  2-3 heavy caps words, sounding word yellow, numbers green, pop-in (karaoke)
  karaoke_box        yellow plate slides under the sounding word, black text on it (karaoke)
Keyword highlight (subtitle and karaoke): highlight.keyword {pick: 'numbers' | 'none', color, max_per_chunk (runs),
words: [...]} or layer "keywords": ["4 million", ...] or words flagged {"kw": true}; numbers keep their unit
("4 million", "$10,000", "15 %"). Orientation-dependent values {"vertical": a, "landscape": b} work for style.size and
the subtitle pos / max_width (pos.x "auto" = 0.47 on 9:16, 0.5 on 16:9).
Captions never shrink (subtitle / karaoke, fit 'reflow' = default): every chunk keeps the style's size. A chunk that
needs more than chunk.max_lines lines (2) wraps to more lines up to the layer's max_lines (presets: 3, karaoke
presets 2; kinds' default 3 / 2); still too long, its time span splits in two at a word boundary (balanced, ranked
by ed_voice._phrase_costs when ed_voice is importable - pauses, sentence ends, phrases; English word lists when the
layer's lang is en or unset and the text is not Cyrillic - else the built-in rule: after a sentence end or comma,
before a conjunction; never inside "4 million dollars" / "at home"; both parts >= chunk.min_show 0.7 s, and where no
split allows that the chunk takes one more line instead): the second part starts at its first word (+ lead),
text-only chunks split in proportion to the characters; repeated until every part fits; parts stay inside the
layer's f0..f1. Only a single word wider than the line shrinks. A producer's lines are kept when they fit at full size. fit 'shrink' = the
old fit (smaller text on chunk.max_lines lines). split_caption_layer() returns the same split as separate layers
(own f0 / f1 / t0 / t1, text, lines, words) for producers that emit one layer per chunk.

Fonts and scripts. Characters a font lacks fall back per character (FONT_FALLBACK, GLOBAL_FALLBACK: Inter, Noto Sans
for Greek / Cyrillic extended, Rubik for Hebrew / Arabic). CJK: the first Han / kana / Hangul character no shipped font
covers fetches the matching Noto Sans CJK subset (sc | tc | hk | jp | kr: Hangul -> kr, kana -> jp, else the layer's
"lang" (zh-Hant -> tc, zh-HK -> hk, ja, ko) or ED_CJK_REGION, default sc) from the GitHub release, verifies the archive
and each face against the pinned sha256 (CJK_FONTS), keeps Regular / Bold / Black + the OFL text in FONT_CACHE
(~/.cache/edit-studio/fonts; ED_FONT_CACHE overrides; ED_NO_DOWNLOAD=1 disables downloads -> boxes + one warning).
layer_span() prefetches a layer's fonts (renders never wait on a download mid-frame). fonts_for_text(text, font, lang,
download) -> {fonts, runs, missing, cjk, warnings}; ensure_cjk_font(region); cjk_region_for(text, lang). CJK lines
break between characters with kinsoku rules (no line starts with 、。」 or small kana) when a token is too wide.
Shaping: shaping_info() (raqm / fribidi / harfbuzz) and shaping_warnings(text) — Arabic, Hebrew, Indic, Thai and other
complex scripts without libraqm render unshaped; that is reported once, clearly, instead of silently.

Units. Frames are output frames (inclusive f0..f1); word times are seconds of output time. Lengths: a number with
|v| <= 1 is a fraction (of H for sizes and vertical values, of W for horizontal ones), a bigger number is canvas px
(full canvas, e.g. 1080×1920) multiplied by `scale`. Layout runs in canvas px, so a preview (scale 0.5) breaks lines
exactly like the full render. Animation: a name, a call string "fade(0.6)" / "zoom_through(dur=0.2, scale=6)" /
"pop(dur=7fr@25)", or a dict {type|kind, dur (s) | frames, ease, …}. Card frame counts are @25 fps; the defaults
here are the same timings in seconds. Easing names: ed_edl (linear in out inout expo_out), ed_render (inQuad …
inOutExpo, hold) + outBack inBack inOutBack elastic/outElastic inElastic outBounce, sine/quart.
  entrances: cut fade pop hit bump slam slam_in scale slide slide_up drop blur_in typewriter write_on cascade decode
             stretch reveal_center_out wipe color_reveal burst strobe words_build (title_card)
  exits:     cut fade dissolve zoom_through scatter tracking pop_out shrink blur_out slide_out reverse strobe

Common layer fields: kind, f0, f1 (or t0/t1 s, or dur s), blend, opacity, safe_zone ('auto' | 'tiktok' | 'reels' |
'shorts' | '16:9' | 'title_safe' | 'action_safe' | 'none' | [x0, y0, x1, y1] fractions; default ctx['safe_zone'] or
'auto' = tiktok x 0.06–0.88 y 0.12–0.80 on 9:16, 5 % margins otherwise), style {font, weight, axes, size, color,
gradient, stroke, shadow, box, glow, caps, tracking (em), line_height, align, features} (style keys and type_class
may also sit at the top level), anim_in, anim_out, pos [x, y], seed, enabled, render_scale (<1: draw at lower
resolution and upscale), occlude (true: hide the layer behind the person mask — any kind), mask_levels, feather.
  size: 0.046 (of H) | 88 (canvas px) | {"fit_width": 0.8, "max": 0.14, "min": 0.03}
  stroke: 0.08 (of size) | {"w": 0.1 (of size) | "w_h": 0.003 (of H) | "px": 6, "color": "#000", "grow": 3 (frames)}
  shadow: true | {"dx": 0, "dy": 0.04, "blur": 0.08 (of size), "alpha": 0.7, "color": "#000"};  glow: {blur, alpha}
  box: {"color": "#000", "alpha": 0.5, "pad": [0.28, 0.12] (of size), "radius": 0.22, "mode": "block|line|word"}
Text is kept inside the safe zone: wrap widths lose the stroke / box / shadow reach and the entrance overshoot,
long lines shrink (captions re-flow and split instead; an unbreakable word shrinks until it fits), elements are
shifted into the zone (a caption moved off a face keeps its ink and the pop-in peak inside), scale peaks (slam,
burst) are capped per side. Sprites are placed without their transparent margins (alpha <= 1/255), so a layer's
bbox - the renderer's boxes sidecar that QA checks - is where it really draws. Full-frame by design: cards with bg, repeat patterns, spotlight, zoom_through.

Kinds (move cards -> layer kind; card ids like "type.kinetic" / "gfx.counter" work too)
  static         text + pos/anchor/max_width/max_lines | items: ed_edl `texts` items {text, x, y, size, font, color,
                 anchor 'lt'|'rt'|'mm'…, tracking (px), opacity} at fixed canvas px
  subtitle       words [{w, t0, t1}] (or ctx words) | chunks [{text, t0|f0, t1|f1}] (translations) ; lines [..]
                 (forced breaks, one-chunk layers from ed_voice) ; mode dialog|lyric ; chunk {max_chars 26|42,
                 max_lines 2, min_dur 0.8, max_dur 6, cps_max 17, max_words, break_on_pause 0.6, split_on_cut 0.3,
                 ellipsis, punct_break, gap_min, join_gap} ; lead −2 / tail +6 (frames) ; pos {x, block:[y0,y1]} |
                 {x, baseline} | {x, center_y} ; avoid 'face' (ctx face track: the chunk moves off the face) ;
                 style "<caption preset>" ; highlight.keyword / keywords (words in a highlight colour) ; fit
                 reflow|shrink, max_lines 3 (most lines at full size before the chunk splits in time) ; when the
                 producer's lines do not fit at full size, the chunk is re-wrapped (one size for the series)
  karaoke        subtitle + highlight {mode color|box|bounce|fill|ghost, active, progressive, upcoming_alpha,
                 box{fill,text,pad,radius}, bounce{scale,grow,back}, keyword{indices|pick:'numbers'|words, color,
                 max_per_chunk}} ;
                 switch_lead −1, min_on 3fr@25, join_gap 0.6 s ; chunks of 2–3 words (9:16) / 3–6 (16:9) ; max_lines
                 2 ; box mode widens word gaps / line pitch so the sliding plate never covers a neighbour
  kinetic        words (or text + per s) ; mode word (pop, one size per series, 1–3 words stacked) | phrase (words
                 slide into a laid-out phrase) | cascade | decode | strobe {per, bands, max_flash_hz, smear} |
                 countdown {digits, per, sizes, slant, stripes} ; group, lead −1fr, min_hold 0.3, max_gap, tail
  beat_text      slots [{w, t|f, accent: downbeat|slam|drop|snare, dur}] | words + beats (ctx beats) + every/start ;
                 layout single|line_build|stack_build|jump|cards ; hit in, slam on accents (anim_in may be the slam),
                 kicks (pulse), outline_cycle, scrim, invert_frames (black on white for n frames), shake {amp,frames}
  title_card     lines [{text, role kicker|title|credit, delay, style}] | text ; layout center_block|poster|fill|
                 frame_top_bottom|lower_block|sky_top ; type_class ; pos ; sizes ; bg color | {gradient, breathe} ;
                 underline {dur, delay, w, color} ; pulse {scale, period} ; in fade|blur_in|slam_in|reveal_center_out|
                 words_build|strobe (flash-limited, 180° flip)|color_reveal ; out dissolve|cut|zoom_through (2.8 s)
  lower_third    name, role ; variant plate|block|minimal|location|topic|handle ; side left|right ; y | above (top of
                 the subtitles) ; accent, plate_color/alpha ; 13-frame build @25, out reverse (8 fr) | fade
  intertitle     text | lines ; variant caption|chapter|card|reply (typed, cps)|trailer (slam)|prologue (line_times)
  margin_note    items [{op write|correct|strike|arrow|punch, text, t|f, i, from_i, to_i, cps, pos}] ; side auto
                 (opposite the face)|left|right ; handwriting font, typed in time, hand-drawn strike and arrow
  repeat         text | [texts] ; layout echo_stack|rows|wave|radial|tunnel|recursive ; copies, pitch, drift, loop,
                 bg, color2, gradient (tunnel renders at half resolution and is cached once settled)
  behind_subject text | lines ; layout giant|sides|wall|ring ; in burst (from the face)|fade|cut ; needs a person mask
  callout        target [x,y] | [x0,y0,x1,y1] | {track: name} | {keys: [[f, x, y(, x1, y1)]]} ; variant pin_label|
                 arrow|ring|brackets|spotlight|tag ; text ; side ; lag (frames) ; exits early near the edge / lost track
  counter        from, to, dur, end_at (s) | end_f, ease ; format {locale ru|en, decimals, prefix, suffix, sign,
                 abbreviate auto|k|False} ; mode number|roll|clock|bars|line|ring|progress ; data, label, land, plate
  route_map      points [[x,y]] (fractions of box) | geo [[lat, lon]] ; labels ; box ; curve smooth|straight|arc ;
                 draw {delay, dur, ease} ; line {color, w, dash, casing} ; bg 'panel' | color ; grid ; km
ctx (all optional): safe_zone; flash_limit_hz (default 3: strobes keep ≤ 3 luminance flashes per second, evenly
spaced); face/faces (callable f -> boxes | {f: box} | [[f, x0, y0, x1, y1], …]; boxes as fractions [x0, y0, x1, y1]
or dicts x, y, w, h; > 1 = canvas px); person_mask (callable f -> HxW 0..1 at any resolution) | mask | frame (HxWx3,
ed_video.person_mask is used); tracks {name: callable f -> point/box | keyframes}; words; beats; downbeats; kicks;
cuts (frames where a new shot starts: subtitles split there with ellipses).
"""
import os, re, math, json, hashlib, unicodedata, weakref
from collections import OrderedDict, namedtuple
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, features as _pil_features

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, 'assets', 'fonts')
HAVE_RAQM = bool(_pil_features.check('raqm'))
_LAYOUT_ENGINE = ImageFont.Layout.RAQM if HAVE_RAQM else ImageFont.Layout.BASIC


# ============================================================================ caches
class LRU:
    """Least-recently-used cache with an item and a byte budget."""

    def __init__(self, max_bytes=256 << 20, max_items=4096):
        self.d = OrderedDict()
        self.nbytes = 0
        self.max_bytes, self.max_items = max_bytes, max_items

    def get(self, k, default=None):
        it = self.d.get(k)
        if it is None:
            return default
        self.d.move_to_end(k)
        return it[0]

    def put(self, k, v, nbytes=0):
        old = self.d.pop(k, None)
        if old is not None:
            self.nbytes -= old[1]
        self.d[k] = (v, nbytes)
        self.nbytes += nbytes
        while len(self.d) > 1 and (self.nbytes > self.max_bytes or len(self.d) > self.max_items):
            _, (_, nb) = self.d.popitem(last=False)
            self.nbytes -= nb
        return v

    def clear(self):
        self.d.clear()
        self.nbytes = 0


_FONT_OBJ = LRU(max_items=384)
_GLYPHS = LRU(max_bytes=160 << 20, max_items=6000)      # word / char coverage masks (uint8)
_SPRITES = LRU(max_bytes=320 << 20, max_items=1500)     # composed premultiplied sprites (float32)
_PLANS = LRU(max_items=256)                             # per-layer plans (chunking, layout, schedules)
_MEASURE = LRU(max_items=60000)


def clear_caches():
    for c in (_FONT_OBJ, _GLYPHS, _SPRITES, _PLANS, _MEASURE):
        c.clear()


def _clamp(v, a, b):
    return a if v < a else b if v > b else v


def _f(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


# ============================================================================ easing
def _back_out(u, s=1.70158):
    u -= 1.0
    return u * u * ((s + 1) * u + s) + 1.0


def _back_in(u, s=1.70158):
    return u * u * ((s + 1) * u - s)


def _back_inout(u, s=1.70158 * 1.525):
    if u < 0.5:
        return (2 * u) ** 2 * ((s + 1) * 2 * u - s) / 2
    return ((2 * u - 2) ** 2 * ((s + 1) * (u * 2 - 2) + s) + 2) / 2


def _elastic_out(u):
    if u <= 0 or u >= 1:
        return float(u >= 1)
    return 2 ** (-10 * u) * math.sin((u * 10 - 0.75) * (2 * math.pi / 3)) + 1


def _elastic_in(u):
    if u <= 0 or u >= 1:
        return float(u >= 1)
    return -(2 ** (10 * u - 10)) * math.sin((u * 10 - 10.75) * (2 * math.pi / 3))


def _bounce_out(u):
    n, d = 7.5625, 2.75
    if u < 1 / d:
        return n * u * u
    if u < 2 / d:
        u -= 1.5 / d
        return n * u * u + 0.75
    if u < 2.5 / d:
        u -= 2.25 / d
        return n * u * u + 0.9375
    u -= 2.625 / d
    return n * u * u + 0.984375


EASE = {
    'linear': lambda u: u,
    'hold': lambda u: 0.0 if u < 1 else 1.0,
    # ed_edl names
    'in': lambda u: u * u, 'out': lambda u: 1 - (1 - u) ** 2, 'inout': lambda u: u * u * (3 - 2 * u),
    'expo_out': lambda u: 1 - 2 ** (-10 * u) if u < 1 else 1.0, 'smooth': lambda u: u * u * (3 - 2 * u),
    # ed_render names
    'inQuad': lambda u: u * u, 'outQuad': lambda u: 1 - (1 - u) ** 2,
    'inOutQuad': lambda u: 2 * u * u if u < 0.5 else 1 - (-2 * u + 2) ** 2 / 2,
    'inCubic': lambda u: u ** 3, 'outCubic': lambda u: 1 - (1 - u) ** 3,
    'inOutCubic': lambda u: 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2,
    'inQuart': lambda u: u ** 4, 'outQuart': lambda u: 1 - (1 - u) ** 4,
    'inOutQuart': lambda u: 8 * u ** 4 if u < 0.5 else 1 - (-2 * u + 2) ** 4 / 2,
    'inExpo': lambda u: 0.0 if u <= 0 else 2 ** (10 * u - 10),
    'outExpo': lambda u: 1.0 if u >= 1 else 1 - 2 ** (-10 * u),
    'inOutExpo': lambda u: 0.0 if u <= 0 else (1.0 if u >= 1 else (2 ** (20 * u - 10) / 2 if u < 0.5 else (2 - 2 ** (-20 * u + 10)) / 2)),
    'inSine': lambda u: 1 - math.cos(u * math.pi / 2), 'outSine': lambda u: math.sin(u * math.pi / 2),
    'inOutSine': lambda u: -(math.cos(math.pi * u) - 1) / 2,
    # added here
    'outBack': _back_out, 'inBack': _back_in, 'inOutBack': _back_inout,
    'elastic': _elastic_out, 'outElastic': _elastic_out, 'inElastic': _elastic_in, 'outBounce': _bounce_out,
}
_EASE_N = {k.lower().replace('_', ''): v for k, v in EASE.items()}
_EASE_N.update({'expoout': EASE['outExpo'], 'backout': _back_out, 'backin': _back_in, 'ease': EASE['inOutCubic']})


def ease(p, name='linear'):
    """Easing by name (ed_edl: linear|in|out|inout|expo_out; ed_render: inQuad … inOutExpo, hold; plus outBack,
    inBack, inOutBack, elastic/outElastic, inElastic, outBounce, sine/quart). Unknown names fall back to linear."""
    p = 0.0 if p <= 0 else 1.0 if p >= 1 else float(p)
    fn = EASE.get(name) or _EASE_N.get(str(name).lower().replace('_', ''), EASE['linear'])
    return fn(p)


# ============================================================================ colours
NAMED_COLORS = {
    'white': '#ffffff', 'black': '#000000', 'yellow': '#ffe14a', 'red': '#ff1e3c', 'green': '#45f06b',
    'blue': '#3fe0ff', 'cyan': '#3fe0ff', 'gold': '#eebb14', 'cream': '#f2ede4', 'gray': '#8a8f98', 'grey': '#8a8f98',
    'orange': '#ff7d00', 'accent': '#ffc400', 'lemon': '#dbdb40', 'purple': '#7a3cff', 'pink': '#ff1f4b',
}


_NAMES_EXTRA = {'warm': '#fff1dc', 'magenta': '#ff2bd6', 'acid': '#b6ff2b', 'amber': '#ffb02e', 'navy': '#0b1020',
                'teal': '#14b8a6', 'transparent': '#00000000'}


def _hex_rgba(s):
    s = s.strip().lower()
    s = s[2:] if s.startswith('0x') else s.lstrip('#')
    if len(s) in (3, 4):
        s = ''.join(ch * 2 for ch in s)
    if len(s) not in (6, 8) or any(ch not in '0123456789abcdef' for ch in s):
        return None
    return [int(s[i:i + 2], 16) / 255.0 for i in range(0, len(s), 2)]


def to_rgba(c, alpha=None, default=(1.0, 1.0, 1.0, 1.0)):
    """Any colour spec -> (r, g, b, a) floats 0..1: '#rgb' | '#rgba' | '#rrggbb' | '#rrggbbaa' (with or without '#',
    or '0x…') | 'rgb(r, g, b)' / 'rgba(r, g, b, a)' | a name (NAMED_COLORS + warm magenta acid amber navy teal
    transparent) | [r, g, b(, a)] list / tuple / ndarray (0..1, or 0..255 when any channel > 1) | int 0xRRGGBB |
    {'r', 'g', 'b'(, 'a')} | None (default). Unreadable specs give `default`. alpha multiplies the alpha."""
    v = None
    if c is None or isinstance(c, bool):
        v = list(default)
    elif isinstance(c, str):
        s = c.strip()
        key = s.lower()
        s = NAMED_COLORS.get(key) or _NAMES_EXTRA.get(key) or s
        if s.lower().startswith(('rgb(', 'rgba(')) and s.endswith(')'):
            try:
                nums = [float(x) for x in s[s.index('(') + 1:-1].split(',')]
                if len(nums) >= 3:
                    rgb = [x / 255.0 for x in nums[:3]] if any(x > 1.0 for x in nums[:3]) else nums[:3]
                    v = rgb + ([nums[3] / 255.0 if nums[3] > 1.0 else nums[3]] if len(nums) > 3 else [])
            except ValueError:
                v = None
        else:
            v = _hex_rgba(s)
        if v is None:
            v = list(default)
    elif isinstance(c, (int, np.integer)):
        n = int(c) & 0xFFFFFF
        v = [((n >> 16) & 255) / 255.0, ((n >> 8) & 255) / 255.0, (n & 255) / 255.0]
    elif isinstance(c, dict):
        v = [_f(c.get('r', 0)), _f(c.get('g', 0)), _f(c.get('b', 0))] + ([_f(c['a'], 1.0)] if 'a' in c else [])
        if any(x > 1.0 for x in v[:3]):
            v = [x / 255.0 for x in v[:3]] + v[3:]
    else:
        try:
            v = [float(x) for x in np.asarray(c, np.float64).reshape(-1)]
        except (TypeError, ValueError):
            v = list(default)
        if len(v) == 1:
            v = v * 3
        if len(v) < 3:
            v = list(default)
        elif any(x > 1.0 for x in v[:3]):
            v = [x / 255.0 for x in v[:3]] + ([v[3] / 255.0 if v[3] > 1.0 else v[3]] if len(v) > 3 else [])
    if len(v) == 3:
        v.append(1.0)
    v = [_clamp(x, 0.0, 1.0) if x == x else 0.0 for x in v[:4]]
    if alpha is not None:
        v[3] *= float(alpha)
    return tuple(v)


def _is_one_color(c):
    if isinstance(c, (str, dict)) or (isinstance(c, (int, np.integer)) and not isinstance(c, bool)):
        return True
    if isinstance(c, np.ndarray):
        return c.ndim == 1 and c.size in (3, 4)
    return (isinstance(c, (list, tuple)) and len(c) in (3, 4)
            and all(isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool) for v in c))


def to_rgba_list(spec, default=None):
    """Colour list (gradient stops, palettes): [colour, ...] or one colour -> [rgba, ...] (to_rgba per item)."""
    if spec is None or (isinstance(spec, (list, tuple)) and not len(spec)):
        spec = default
    if spec is None:
        return []
    if _is_one_color(spec):
        return [to_rgba(spec)]
    return [to_rgba(c) for c in spec]


def _premul(c, k=1.0):
    r, g, b, a = c
    a = a * k
    return (r * a, g * a, b * a, a)


def _mix(c0, c1, u):
    return tuple(c0[i] + (c1[i] - c0[i]) * u for i in range(4))


# ============================================================================ safe zones
SAFE_ZONES = {
    # 9:16 platform UI: top 12 %, bottom 20 %, right 12 % (+ 6 % left margin) — the move cards' x 0.06–0.88, y 0.12–0.80
    'tiktok': (0.06, 0.12, 0.88, 0.80), 'reels': (0.06, 0.12, 0.88, 0.80), 'shorts': (0.06, 0.12, 0.88, 0.80),
    'vertical': (0.06, 0.12, 0.88, 0.80),
    '16:9': (0.05, 0.05, 0.95, 0.95), 'landscape': (0.05, 0.05, 0.95, 0.95), 'square': (0.05, 0.05, 0.95, 0.95),
    'title_safe': (0.05, 0.05, 0.95, 0.95), 'action_safe': (0.035, 0.035, 0.965, 0.965), 'none': (0.0, 0.0, 1.0, 1.0),
}
_VERTICAL_ZONES = ('tiktok', 'reels', 'shorts', 'vertical')


def safe_zone_frac(zone, ow, oh):
    vertical = oh > ow * 1.15
    if isinstance(zone, (list, tuple)) and len(zone) == 4:
        return tuple(float(v) for v in zone)
    z = str(zone or 'auto').lower()
    if z == 'auto' or z not in SAFE_ZONES:
        z = 'tiktok' if vertical else '16:9'
    if z in _VERTICAL_ZONES and not vertical:
        z = '16:9'                       # vertical UI zones make no sense on a landscape canvas
    return SAFE_ZONES[z]


def safe_rect(zone, ow, oh):
    """Safe rectangle (x0, y0, x1, y1) in output px."""
    a, b, c, d = safe_zone_frac(zone, ow, oh)
    return (a * ow, b * oh, c * ow, d * oh)


# ============================================================================ fonts (OFL only)
FONT_FILES = {
    # key: (file in engine/assets/fonts, default variation axes) — every family is SIL OFL 1.1, licence in <family>_OFL.txt
    'inter': ('inter_Inter-VF.ttf', {'wght': 700, 'opsz': 32}),
    'inter_italic': ('inter_Inter-Italic-VF.ttf', {'wght': 700, 'opsz': 32}),
    'noto': ('notosans_NotoSans-VF.ttf', {'wght': 700}),
    'rubik': ('rubik_Rubik-VF.ttf', {'wght': 700}),                 # + Hebrew and Arabic: RTL fallback
    'montserrat': ('montserrat_Montserrat-VF.ttf', {'wght': 800}),
    'oswald': ('oswald_Oswald-VF.ttf', {'wght': 700}),
    'firacond': ('firasansextracondensed_FiraSansExtraCondensed-Black.ttf', {}),
    'firacond_xb': ('firasansextracondensed_FiraSansExtraCondensed-ExtraBold.ttf', {}),
    'firacond_b': ('firasansextracondensed_FiraSansExtraCondensed-Bold.ttf', {}),
    'nunito': ('nunito_Nunito-VF.ttf', {'wght': 900}),
    'unbounded': ('unbounded_Unbounded-VF.ttf', {'wght': 800}),
    'playfair': ('playfairdisplay_PlayfairDisplay-VF.ttf', {'wght': 700}),
    'playfair_italic': ('playfairdisplay_PlayfairDisplay-Italic-VF.ttf', {'wght': 600}),
    'cormorant': ('cormorantgaramond_CormorantGaramond-VF.ttf', {'wght': 600}),
    'greatvibes': ('greatvibes_GreatVibes-Regular.ttf', {}),
    'caveat': ('caveat_Caveat-VF.ttf', {'wght': 700}),
    'jetbrains': ('jetbrainsmono_JetBrainsMono-VF.ttf', {'wght': 700}),
    'pixel': ('pressstart2p_PressStart2P-Regular.ttf', {}),
    'dela': ('delagothicone_DelaGothicOne-Regular.ttf', {}),
    'anton': ('anton_Anton-Regular.ttf', {}),             # Latin only — Cyrillic falls back to firacond
    'bebas': ('bebasneue_BebasNeue-Regular.ttf', {}),     # Latin only — Cyrillic falls back to oswald
}
_STATIC_WEIGHTS = {'firacond': ((700, 'firacond_b'), (800, 'firacond_xb'), (900, 'firacond'))}
FONT_FALLBACK = {'anton': ['firacond'], 'bebas': ['oswald'], 'pixel': ['jetbrains'], 'greatvibes': ['playfair_italic'],
                 'caveat': ['nunito'], 'firacond': ['oswald'], 'firacond_xb': ['oswald'], 'firacond_b': ['oswald'],
                 'cormorant': ['playfair'], 'dela': ['unbounded']}
GLOBAL_FALLBACK = ['inter', 'noto', 'rubik']
# type classes used by the move cards -> registry key[:weight]
TYPE_CLASSES = {
    'grotesk': 'inter:700', 'grotesk_regular': 'inter:400', 'grotesk_medium': 'inter:500', 'grotesk_semibold': 'inter:600',
    'grotesk_bold': 'inter:700', 'grotesk_heavy': 'inter:800', 'grotesk_black': 'inter:900',
    'grotesk_bold_italic': 'inter_italic:700', 'grotesk_italic': 'inter_italic:600',
    'grotesk_condensed': 'oswald:600', 'grotesk_condensed_black': 'firacond:900', 'grotesk_condensed_caps': 'firacond:900',
    'grotesk_condensed_lower': 'firacond:800', 'condensed_bold_caps': 'firacond:900',
    'grotesk_rounded': 'nunito:800', 'grotesk_rounded_bold': 'nunito:800', 'grotesk_bold_rounded': 'nunito:900',
    'grotesk_rounded_black': 'nunito:1000', 'rounded': 'nunito:900',
    'grotesk_light_geo': 'montserrat:300', 'geometric': 'montserrat:700', 'geometric_bold': 'montserrat:800',
    'grotesk_extended': 'unbounded:700', 'grotesk_extended_bold': 'unbounded:800', 'caps_bold_wide': 'unbounded:700',
    'caps_bold': 'montserrat:800', 'wide': 'unbounded:800',
    'serif': 'playfair:600', 'serif_caps': 'cormorant:600', 'serif_book': 'cormorant:500', 'didone': 'playfair:800',
    'serif_italic': 'playfair_italic:500', 'script': 'greatvibes', 'calligraphy': 'greatvibes',
    'mono': 'jetbrains:700', 'mono_caps': 'jetbrains:800', 'mono_typewriter': 'jetbrains:400', 'typewriter': 'jetbrains:400',
    'mono_white': 'jetbrains:600', 'pixel': 'pixel',
    'hand': 'caveat:600', 'handwriting': 'caveat:600', 'hand_marker': 'caveat:700', 'handwriting_marker': 'caveat:700',
    'hand_pen': 'caveat:500', 'hand_brush': 'caveat:700',
    'display': 'dela', 'display_mix': 'dela', 'chunky': 'dela', 'chunky_multicolor': 'dela', 'comic_bold': 'rubik:900',
}
# names of ed_edl.FONTS kept working (mapped to OFL faces)
FONT_ALIASES = {'sans': 'inter:700', 'sans_wide': 'inter:800', 'mono': 'jetbrains:700', 'oswald_semi': 'oswald:600',
                'montserrat': 'montserrat:800', 'oswald': 'oswald:700', 'anton': 'anton', 'bebas': 'bebas'}
_AXIS_TAG = {'Weight': 'wght', 'Width': 'wdth', 'Optical size': 'opsz', 'Optical Size': 'opsz', 'Italic': 'ital',
             'Slant': 'slnt'}

FontRef = namedtuple('FontRef', 'key path axes')


def font_ref(spec=None, weight=None, axes=None):
    """'inter:800' | registry key | type class ('grotesk_black') | ed_edl name ('sans') | path -> FontRef."""
    ax = tuple(sorted((str(k), float(v)) for k, v in (axes or {}).items()))
    return _resolve_font(str(spec or 'inter'), None if weight is None else float(weight), ax)


_RESOLVED = {}


def _resolve_font(spec, weight, axes_items):
    k = (spec, weight, axes_items)
    r = _RESOLVED.get(k)
    if r is not None:
        return r
    s = spec.strip()
    for _ in range(4):
        if s in TYPE_CLASSES and s not in FONT_FILES:
            s = TYPE_CLASSES[s]
        elif s in FONT_ALIASES and s not in FONT_FILES:
            s = FONT_ALIASES[s]
        else:
            break
    if s.lower().endswith(('.ttf', '.otf')) or os.sep in s:
        path = s if os.path.isabs(s) else os.path.join(FONT_DIR, s)
        key, ax = os.path.basename(path), {}
        if not os.path.exists(path):
            key, path, ax = 'inter', os.path.join(FONT_DIR, FONT_FILES['inter'][0]), dict(FONT_FILES['inter'][1])
    else:
        key, _, w = s.partition(':')
        if _font_entry(key) is None:
            key = TYPE_CLASSES.get(key, 'inter').partition(':')[0] if key in TYPE_CLASSES else 'inter'
        ax = dict(_font_entry(key)[1])
        if w:
            ax['wght'] = float(w)
        path = None
    if weight is not None:
        ax['wght'] = weight
    ax.update(dict(axes_items))
    if key in _STATIC_WEIGHTS and 'wght' in ax:
        wt = ax.pop('wght')
        key = min(_STATIC_WEIGHTS[key], key=lambda p: abs(p[0] - wt))[1]
    if path is None:
        path = os.path.join(FONT_DIR, _font_entry(key)[0])        # cache fonts carry an absolute path
    r = FontRef(key, path, tuple(sorted(ax.items())))
    _RESOLVED[k] = r
    return r


def _font_entry(key):
    """(file, default axes) of a shipped font (FONT_FILES) or of a downloaded cache font (CACHE_FONT_FILES)."""
    return FONT_FILES.get(key) or CACHE_FONT_FILES.get(key)


def pil_font(ref, size):
    """Cached Pillow font at `size` px with the variation axes of `ref` applied."""
    size = max(1.0, round(float(size) * 4) / 4)
    k = (ref, size)
    f = _FONT_OBJ.get(k)
    if f is None:
        f = ImageFont.truetype(ref.path, size, layout_engine=_LAYOUT_ENGINE)
        if ref.axes:
            try:
                axes = f.get_variation_axes()
            except Exception:
                axes = None
            if axes:
                want = dict(ref.axes)
                vals = []
                for a in axes:
                    nm = a.get('name')
                    nm = nm.decode('latin-1') if isinstance(nm, bytes) else str(nm)
                    tag = _AXIS_TAG.get(nm, nm[:4].lower())
                    vals.append(_clamp(float(want.get(tag, a.get('default', a['minimum']))), a['minimum'], a['maximum']))
                try:
                    f.set_variation_by_axes(vals)
                except Exception:
                    pass
        _FONT_OBJ.put(k, f)
    return f


_CMAPS = {}


def _cmap(path):
    cm = _CMAPS.get(path, False)
    if cm is False:
        try:
            from fontTools.ttLib import TTFont
            cm = frozenset((TTFont(path, lazy=True).getBestCmap() or {}).keys())
        except Exception:
            cm = None                    # unknown coverage: trust the font
        _CMAPS[path] = cm
    return cm


_NOTDEF = {}


def font_covers(ref, ch):
    """True when the font has a glyph for ch (cmap via fontTools; without fontTools the glyph raster is compared with
    the font's .notdef box)."""
    cm = _cmap(ref.path)
    if cm is not None:
        return ord(ch) in cm
    if ch.isspace() or ord(ch) < 0x80:
        return True
    k = (ref.path, ch)
    v = _NOTDEF.get(k)
    if v is None:
        try:
            f = ImageFont.truetype(ref.path, 24)
            nd = f.getmask('\U000E0042').tobytes()
            v = f.getmask(ch).tobytes() != nd
        except Exception:
            v = True
        _NOTDEF[k] = v
    return v


_FALLBACKS = {}


def _fallback_chain(ref):
    ch = _FALLBACKS.get(ref)
    if ch is None:
        w = dict(ref.axes).get('wght')
        ch = [ref]
        for k in FONT_FALLBACK.get(ref.key, []) + GLOBAL_FALLBACK:
            e = _font_entry(k)
            r = font_ref(k, weight=w if (w is not None and ('wght' in e[1] or k in _STATIC_WEIGHTS)) else None)
            if r not in ch:
                ch.append(r)
        _FALLBACKS[ref] = ch
    return ch


# ============================================================================ on-demand CJK fonts (OFL, cached)
# Chinese / Japanese / Korean glyphs are not shipped (tens of MB). The first text that needs them downloads the
# matching Noto Sans CJK subset (SIL OFL 1.1) from the GitHub release, verifies the archive and every extracted face
# against the sha256 pinned here, and keeps Regular / Bold / Black (+ LICENSE) in FONT_CACHE. Per-character fallback
# then picks them up. ED_FONT_CACHE overrides the folder; ED_NO_DOWNLOAD=1 (or download=False) never downloads;
# ED_CJK_REGION sets the default region for Han-only text (sc).
FONT_CACHE = os.environ.get('ED_FONT_CACHE') or os.path.join(os.environ.get('ED_ROOT', 'C:/Claude Code/cinema-studio/edit'), 'cache', 'fonts')
CJK_RELEASE = 'https://github.com/notofonts/noto-cjk/releases/download/Sans2.004/'
CJK_SUBDIR = 'noto-cjk-sans-2.004'
CJK_FONTS = {   # region: release asset (zip) + sha256 / size, faces {weight: (file, sha256, size)}
    'sc': {'asset': '18_NotoSansSC.zip', 'size': 50077940, 'lang': ['zh', 'zh-cn', 'zh-hans', 'zh-sg', 'cmn'],
           'sha256': '4d107c09ada479d3e48b6e78c83835773cbd9214bf6e12cdb7b60f8e068292ec',
           'faces': {400: ('NotoSansSC-Regular.otf', 'faa6c9df652116dde789d351359f3d7e5d2285a2b2a1f04a2d7244df706d5ea9', 8331336),
                     700: ('NotoSansSC-Bold.otf', 'c6cb5a93abaa9edc8ee7463b7ebb7f42d618d40e6ed2f7a5371c97b0b64767c0', 8543168),
                     900: ('NotoSansSC-Black.otf', 'ccb496022356b7dd14d117538a472ae40feff8f6e8f3fe8bffc5616785d2f3f9', 8855916)}},
    'tc': {'asset': '19_NotoSansTC.zip', 'size': 34139452, 'lang': ['zh-tw', 'zh-hant', 'zh-mo'],
           'sha256': 'fbbcb216be8056a436c7ec142847f302bb1932d07bdad8b322f4953a389d7cbc',
           'faces': {400: ('NotoSansTC-Regular.otf', '5bab0cb3c1cf89dde07c4a95a4054b195afbcfe784d69d75c340780712237537', 5683368),
                     700: ('NotoSansTC-Bold.otf', '55420b259eb119bf5f2a0aadba10cf9d736c12d64ab93e78546d69ef5f43558b', 5839972),
                     900: ('NotoSansTC-Black.otf', '3280b221ab7b011c6ae48d38388a0e8c72ddf479992bce62ff589ae932819ce4', 6068384)}},
    'hk': {'asset': '20_NotoSansHK.zip', 'size': 34195355, 'lang': ['zh-hk', 'yue'],
           'sha256': 'c2d8a17fc668116920b75a3bc6f63606faefe43722efec7bb03c66164b3ec52f',
           'faces': {400: ('NotoSansHK-Regular.otf', '8a43afea92bb58dfd9027bd7ac6f5b0b2662e2ffb3e7c1edc02c62b2b21924f1', 5688384),
                     700: ('NotoSansHK-Bold.otf', '4bce16fbed09278cbdfb4d57749500038cdda70737925a846e3f6c59327ab46e', 5840928),
                     900: ('NotoSansHK-Black.otf', 'aa7e48349d2c606f0194fd73c3e5fad03d88d851b8a440bd189377dbeaf44f89', 6072180)}},
    'jp': {'asset': '16_NotoSansJP.zip', 'size': 27139567, 'lang': ['ja', 'jp', 'ja-jp'],
           'sha256': '2bbdd2c20f30670b39ca735c96d75f1fdabdb348103e43b820cf17701fd22b18',
           'faces': {400: ('NotoSansJP-Regular.otf', 'dff723ba59d57d136764a04b9b2d03205544f7cd785a711442d6d2d085ac5073', 4533028),
                     700: ('NotoSansJP-Bold.otf', '1b0edfb500b73a4fa8a4fcaae1bbbd403994e08e73e3e0da37e70d3853f42c5f', 4656448),
                     900: ('NotoSansJP-Black.otf', '3aa30b0956510f4205f759ab3079a5b658310ebcda2577f290466ea51c948819', 4855212)}},
    'kr': {'asset': '17_NotoSansKR.zip', 'size': 26036461, 'lang': ['ko', 'kr', 'ko-kr'],
           'sha256': 'ac7eeb4e2b0d41de8ff31b2d6e1e2a41caf253fd5cefb380bfa1f40f1747b612',
           'faces': {400: ('NotoSansKR-Regular.otf', '69975a0ac8472717870aefeab0a4d52739308d90856b9955313b2ad5e0148d68', 4644748),
                     700: ('NotoSansKR-Bold.otf', '5a6ceb287ed2fc6cfc6213144ebea68cbd94b20fc9eb873d8486493bf02d9bda', 4816044),
                     900: ('NotoSansKR-Black.otf', 'a9977a588488d2a7f544bb2b589b01bed071dca64a4655d438696301b527884b', 5033248)}},
}
CACHE_FONT_FILES = {}           # key -> (absolute path, default axes): downloaded faces registered at runtime
CJK_REGIONS = []                # regions registered (available) in preference order of registration
_CJK_LOCK = __import__('threading').Lock()
_CJK_TRIED = {}                 # region -> (ok, reason) of the download attempt in this process
_TLS = __import__('threading').local()     # per-thread language hint (render_layer sets it from layer['lang'])
_CJK_SCANNED = []


def _cjk_key(region, weight=700):
    return f'cjk_{region}' + {400: '_r', 700: '', 900: '_k'}[weight]


def cjk_font_path(region, weight=700):
    return os.path.join(FONT_CACHE, CJK_SUBDIR, CJK_FONTS[region]['faces'][weight][0])


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for blk in iter(lambda: fh.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


def cjk_available(region, verify=False):
    """True when the region's faces are in FONT_CACHE (sizes match; verify=True also re-checks the sha256)."""
    spec = CJK_FONTS.get(region)
    if not spec:
        return False
    for wt, (fn, sha, size) in spec['faces'].items():
        p = cjk_font_path(region, wt)
        try:
            if os.path.getsize(p) != size:
                return False
        except OSError:
            return False
        if verify and _sha256_file(p) != sha:
            return False
    return True


def _register_cjk(region):
    if region in CJK_REGIONS:
        return
    for wt in (400, 700, 900):
        CACHE_FONT_FILES[_cjk_key(region, wt)] = (cjk_font_path(region, wt), {})
    base = _cjk_key(region)
    _STATIC_WEIGHTS[base] = tuple((wt, _cjk_key(region, wt)) for wt in (400, 700, 900))
    CJK_REGIONS.append(region)
    clear_font_caches()


def clear_font_caches():
    """Forget resolved fonts, fallback chains, runs, measurements, rasters and plans (after fonts were added)."""
    for c in (_RESOLVED, _FALLBACKS, _RUNS, _CMAPS, _NOTDEF):
        c.clear()
    for c in (_MEASURE, _GLYPHS, _SPRITES, _PLANS, _FONT_OBJ):
        c.clear()


def _no_download():
    return os.environ.get('ED_NO_DOWNLOAD', '').strip().lower() in ('1', 'true', 'yes', 'on')


def ensure_cjk_font(region='sc', download=None, log=None):
    """Make the region's Noto Sans CJK faces available (sc | tc | hk | jp | kr): from FONT_CACHE, else downloaded once
    from the GitHub release (sha256-verified archive and faces, OFL licence kept next to them). -> True when usable.
    Never raises: a failure (offline, ED_NO_DOWNLOAD=1, checksum mismatch) warns once and returns False."""
    region = (region or 'sc').lower()
    if region not in CJK_FONTS:
        return False
    if region in CJK_REGIONS:
        return True
    with _CJK_LOCK:
        if region in CJK_REGIONS:
            return True
        if cjk_available(region):
            _register_cjk(region)
            return True
        if region in _CJK_TRIED:
            return _CJK_TRIED[region][0]
        allow = (not _no_download()) if download is None else bool(download)
        if not allow:
            if download is None:                       # environment switch: remember for this process
                _CJK_TRIED[region] = (False, 'downloads disabled (ED_NO_DOWNLOAD)')
            _warn_once(('cjk', region), f'CJK text needs the {region} font (Noto Sans CJK, OFL) but downloads are '
                                        f'disabled; characters without a font render as boxes. Allow the download '
                                        f'or put the faces in {os.path.join(FONT_CACHE, CJK_SUBDIR)}')
            return False
        ok, why = _download_cjk(region, log)
        _CJK_TRIED[region] = (ok, why)
        if ok:
            _register_cjk(region)
        else:
            _warn_once(('cjk', region), f'CJK font {region} unavailable ({why}); CJK characters render as boxes')
        return ok


def _download_cjk(region, log=None):
    """Download + verify + extract one region (cross-process lock file; atomic renames). -> (ok, reason)."""
    import tempfile, zipfile, urllib.request
    spec = CJK_FONTS[region]
    d = os.path.join(FONT_CACHE, CJK_SUBDIR)
    try:
        os.makedirs(d, exist_ok=True)
    except OSError as e:
        return False, f'cache folder: {e}'
    lockf = open(os.path.join(d, f'.{region}.lock'), 'w')
    try:
        try:
            import fcntl
            fcntl.flock(lockf, fcntl.LOCK_EX)
        except Exception:
            pass
        if cjk_available(region):                      # another process finished it meanwhile
            return True, 'cached'
        url = CJK_RELEASE + spec['asset']
        msg = (f'[ed_text] downloading CJK font {spec["asset"]} ({spec["size"] / 1e6:.0f} MB, SIL OFL 1.1) -> {d} '
               f'(once)')
        (log or (lambda m: print(m, file=__import__('sys').stderr)))(msg)
        fd, tmp = tempfile.mkstemp(prefix=f'.{region}-', suffix='.zip', dir=d)
        h = hashlib.sha256()
        try:
            with os.fdopen(fd, 'wb') as out, urllib.request.urlopen(url, timeout=60) as resp:
                while True:
                    blk = resp.read(1 << 20)
                    if not blk:
                        break
                    h.update(blk)
                    out.write(blk)
            if h.hexdigest() != spec['sha256']:
                return False, f'sha256 mismatch for {spec["asset"]}'
            with zipfile.ZipFile(tmp) as zf:
                names = set(zf.namelist())
                for wt, (fn, sha, size) in spec['faces'].items():
                    if fn not in names:
                        return False, f'{fn} missing in {spec["asset"]}'
                    data = zf.read(fn)
                    if len(data) != size or hashlib.sha256(data).hexdigest() != sha:
                        return False, f'sha256 mismatch for {fn}'
                    part = os.path.join(d, fn + '.part')
                    with open(part, 'wb') as fh:
                        fh.write(data)
                    os.replace(part, os.path.join(d, fn))
                if 'LICENSE' in names:
                    lic = zf.read('LICENSE')
                    if b'SIL OPEN FONT LICENSE' in lic.upper():
                        with open(os.path.join(d, 'NotoSansCJK_OFL.txt'), 'wb') as fh:
                            fh.write(lic)
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass
        return (True, 'downloaded') if cjk_available(region) else (False, 'extract failed')
    except Exception as e:                              # offline, proxy, disk full ...
        return False, f'{type(e).__name__}: {e}'
    finally:
        lockf.close()


# script detection (per character)
def char_script(c):
    """Coarse script of one character: han | kana | hangul | cjk (CJK punctuation, fullwidth forms) | arabic |
    hebrew | indic | thai | lao | khmer | myanmar | tibetan | other."""
    o = ord(c)
    if 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF or 0x20000 <= o <= 0x2FA1F or 0xF900 <= o <= 0xFAFF:
        return 'han'
    if 0x3040 <= o <= 0x30FF or 0x31F0 <= o <= 0x31FF or 0xFF66 <= o <= 0xFF9F:
        return 'kana'
    if 0xAC00 <= o <= 0xD7AF or 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F or 0xA960 <= o <= 0xA97F:
        return 'hangul'
    if 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF or 0x3200 <= o <= 0x33FF or 0xFE30 <= o <= 0xFE4F:
        return 'cjk'
    if 0x0600 <= o <= 0x08FF or 0xFB50 <= o <= 0xFDFF or 0xFE70 <= o <= 0xFEFF:
        return 'arabic'
    if 0x0590 <= o <= 0x05FF or 0xFB1D <= o <= 0xFB4F:
        return 'hebrew'
    if 0x0900 <= o <= 0x0DFF:
        return 'indic'
    if 0x0E00 <= o <= 0x0E7F:
        return 'thai'
    if 0x0E80 <= o <= 0x0EFF:
        return 'lao'
    if 0x1780 <= o <= 0x17FF:
        return 'khmer'
    if 0x1000 <= o <= 0x109F:
        return 'myanmar'
    if 0x0F00 <= o <= 0x0FFF:
        return 'tibetan'
    return 'other'


_CJK_SCRIPTS = ('han', 'kana', 'hangul', 'cjk')
_COMPLEX_SCRIPTS = ('arabic', 'hebrew', 'indic', 'thai', 'lao', 'khmer', 'myanmar', 'tibetan')


def is_cjk(text):
    return any(char_script(c) in _CJK_SCRIPTS for c in str(text))


def cjk_region_for(text, lang=None):
    """Noto CJK region for a text: Hangul -> kr, kana -> jp, else the language hint (zh-Hant -> tc, zh-HK -> hk,
    ja -> jp, ko -> kr, zh -> sc), else ED_CJK_REGION or sc."""
    sc = {char_script(c) for c in str(text)}
    if 'hangul' in sc:
        return 'kr'
    if 'kana' in sc:
        return 'jp'
    lg = str(lang or getattr(_TLS, 'lang', None) or '').strip().lower().replace('_', '-')
    if lg:
        for reg, spec in CJK_FONTS.items():
            if lg in spec['lang']:
                return reg
        base = lg.split('-')[0]
        for reg, spec in CJK_FONTS.items():
            if base in spec['lang']:
                return reg
    env = os.environ.get('ED_CJK_REGION', '').strip().lower()
    return env if env in CJK_FONTS else 'sc'


def _scan_cjk_cache():
    """Register every region already in FONT_CACHE (stat only; a face is sha256-checked when downloaded)."""
    for reg in CJK_FONTS:
        try:
            if reg not in CJK_REGIONS and cjk_available(reg):
                _register_cjk(reg)
        except Exception:
            pass


def _cjk_chain(ref, region):
    """CJK faces to try for a reference font: the region's face first, then the other registered regions (weight
    matched to the reference)."""
    if not _CJK_SCANNED:
        _CJK_SCANNED.append(True)
        _scan_cjk_cache()
    w = dict(ref.axes).get('wght')
    if w is None:
        w = 900 if ref.key in ('firacond', 'anton', 'dela') else 700
    out = []
    for reg in [region] + [r for r in CJK_REGIONS if r != region]:
        if reg in CJK_REGIONS:
            out.append(font_ref(_cjk_key(reg), weight=w))
    return out


# shaping checks (raqm = harfbuzz + fribidi via Pillow)
def shaping_info():
    """Text shaping capabilities of this Pillow: {'raqm', 'fribidi', 'harfbuzz', 'versions', 'layout'}."""
    info = {'raqm': HAVE_RAQM, 'layout': 'raqm' if HAVE_RAQM else 'basic'}
    for f in ('fribidi', 'harfbuzz'):
        try:
            info[f] = bool(_pil_features.check_feature(f))
        except Exception:
            info[f] = None
    vers = {}
    for f in ('raqm', 'fribidi', 'harfbuzz', 'freetype2'):
        try:
            vers[f] = _pil_features.version(f) if f in ('freetype2', 'raqm') else _pil_features.version_feature(f)
        except Exception:
            vers[f] = None
    info['versions'] = vers
    return info


def shaping_warnings(text):
    """Warnings for text this Pillow cannot shape correctly: complex scripts (Arabic, Hebrew, Indic, Thai, ...) without
    libraqm render unjoined / in the wrong order; RTL without fribidi is not reordered. [] when fine."""
    scripts = sorted({char_script(c) for c in str(text)} & set(_COMPLEX_SCRIPTS))
    if not scripts:
        return []
    out = []
    if not HAVE_RAQM:
        out.append(f'{"/".join(scripts)} text needs libraqm for shaping (joined letters, RTL order, marks), but '
                   f'Pillow has no raqm support: it will render unshaped. Install libraqm (+ libfribidi, libharfbuzz) '
                   f'and a Pillow built with it (python3 -c "from PIL import features; print(features.check(\'raqm\'))")')
    else:
        info = shaping_info()
        if info.get('fribidi') is False and ({'arabic', 'hebrew'} & set(scripts)):
            out.append('RTL text: Pillow raqm runs without fribidi, bidirectional reordering may be wrong '
                       '(install libfribidi)')
    return out


def fonts_for_text(text, font='inter', lang=None, download=True, weight=None):
    """Fonts that render `text` with `font` (per-character fallback, CJK faces fetched on demand):
    {'fonts': [font keys in run order], 'runs': [[substring, key], ...], 'missing': chars no font covers,
    'cjk': region | None, 'warnings': [...] (missing glyphs, failed downloads, shaping without raqm)}."""
    ref = font if isinstance(font, FontRef) else font_ref(font, weight)
    text = str(text)
    warns = list(shaping_warnings(text))
    region = cjk_region_for(text, lang) if is_cjk(text) else None
    prev = getattr(_TLS, 'lang', None)
    _TLS.lang = lang if lang else prev
    try:
        if region and download is not None:
            ok = ensure_cjk_font(region, download=download)
            if not ok:
                why = _CJK_TRIED.get(region, (False, 'downloads disabled'))[1]
                warns.append(f'CJK font {region} unavailable ({why})' + (
                    '; other CJK faces cover what they can' if CJK_REGIONS else ''))
        runs = split_runs(text, ref, auto_download=download is not False)
    finally:
        _TLS.lang = prev
    missing = ''.join(sorted({c for t, r in runs for c in t if not c.isspace() and c not in _ZW
                              and unicodedata.category(c)[0] not in ('M', 'C') and not font_covers(r, c)}))
    if missing:
        warns.append(f'no font covers {missing!r}: those characters render as boxes')
    keys = []
    for t, r in runs:
        if r.key not in keys:
            keys.append(r.key)
    return {'fonts': keys, 'runs': [[t, r.key] for t, r in runs], 'missing': missing, 'cjk': region,
            'warnings': warns}


_ZW = set('​‌‍‎‏⁠﻿')
_RUNS = {}


def split_runs(text, ref, auto_download=True):
    """Split text into (substring, FontRef) runs: each char takes the first font of the fallback chain that has it;
    characters no shipped font covers go to the Noto CJK faces (downloaded on first use, see ensure_cjk_font).
    Combining marks and zero-width joiners stay with the previous character."""
    lang = getattr(_TLS, 'lang', None)
    k = (text, ref, lang, len(CJK_REGIONS))
    r = _RUNS.get(k)
    if r is not None:
        return r
    cm0 = _cmap(ref.path)
    if cm0 is not None and all((ord(c) in cm0) or c in _ZW for c in text):
        r = [(text, ref)]
    else:
        chain = _fallback_chain(ref)
        cjk = None
        runs = []
        for c in text:
            if runs and (c in _ZW or unicodedata.category(c)[0] == 'M'):
                runs[-1][0] += c
                continue
            pick = None
            for fr in chain:
                if font_covers(fr, c):
                    pick = fr
                    break
            if pick is None and char_script(c) in _CJK_SCRIPTS:
                if cjk is None:
                    region = cjk_region_for(text, lang)
                    if region not in CJK_REGIONS and auto_download:
                        ensure_cjk_font(region)
                    cjk = _cjk_chain(ref, region)
                for fr in cjk:
                    if font_covers(fr, c):
                        pick = fr
                        break
            if pick is None:
                pick = ref
            if runs and runs[-1][1] == pick:
                runs[-1][0] += c
            else:
                runs.append([c, pick])
        r = [(t, fr) for t, fr in runs]
        if not HAVE_RAQM:
            for w in shaping_warnings(text):
                _warn_once(('shape', w[:40]), w)
    if len(_RUNS) > 20000:
        _RUNS.clear()
    _RUNS[(text, ref, lang, len(CJK_REGIONS))] = r
    return r


def text_direction(text):
    """'rtl' when the first strong character is right-to-left (Hebrew, Arabic, …), else 'ltr'."""
    for c in text:
        b = unicodedata.bidirectional(c)
        if b in ('R', 'AL'):
            return 'rtl'
        if b == 'L':
            return 'ltr'
    return 'ltr'


def _kw(direction, features):
    kw = {}
    if HAVE_RAQM:
        if direction:
            kw['direction'] = direction
        if features:
            kw['features'] = list(features)
    return kw


def text_length(text, font='inter', size=100.0, tracking=0.0, features=None):
    """Advance width of `text` (px at `size`), fallback fonts and tracking (em) included."""
    ref = font if isinstance(font, FontRef) else font_ref(font)
    feats = tuple(features) if features else None
    k = (text, ref, round(float(size), 3), round(float(tracking), 4), feats)
    v = _MEASURE.get(k)
    if v is None:
        v = 0.0
        for run, r in split_runs(text, ref):
            d = 'rtl' if text_direction(run) == 'rtl' else None
            v += pil_font(r, size).getlength(run, **_kw(d, feats))
        if tracking and len(text) > 1 and text_direction(text) != 'rtl':
            v += float(tracking) * float(size) * (len(text) - 1)
        _MEASURE.put(k, v)
    return v


_METRICS = {}


def font_metrics(ref):
    """Ink metrics as fractions of the font size: cap height, x-height, descender depth, space."""
    m = _METRICS.get(ref)
    if m is None:
        f = pil_font(ref, 200)
        def top(s):
            try:
                return -f.getbbox(s, anchor='ls')[1] / 200.0
            except Exception:
                return 0.7
        cap = top('HE')
        if not (0.3 < cap < 1.2):
            cap = 0.7
        try:
            desc = max(0.12, f.getbbox('gpy', anchor='ls')[3] / 200.0)
        except Exception:
            desc = 0.22
        m = dict(cap=cap, x=top('xo') or 0.5, desc=min(desc, 0.45), space=max(0.18, f.getlength(' ') / 200.0))
        _METRICS[ref] = m
    return m


# ============================================================================ glyph rasters
class Glyph:
    """Coverage of one word/run at an output size: fill `a` and fill+stroke `s` (uint8, same box, s None without
    stroke); (x0, y0) = top-left relative to the pen origin on the baseline; adv = advance width (px)."""
    __slots__ = ('a', 's', 'x0', 'y0', 'adv')

    def __init__(self, a, s, x0, y0, adv):
        self.a, self.s, self.x0, self.y0, self.adv = a, s, x0, y0, adv

    @property
    def w(self):
        return self.a.shape[1]

    @property
    def h(self):
        return self.a.shape[0]


def _draw_piece(text, font, stroke, direction, features):
    kw = _kw(direction, features)
    try:
        bb = font.getbbox(text, anchor='ls', stroke_width=stroke, **kw)
    except Exception:
        kw = {}
        bb = font.getbbox(text, anchor='ls', stroke_width=stroke)
    x0, y0 = int(math.floor(bb[0])) - 1, int(math.floor(bb[1])) - 1
    x1, y1 = int(math.ceil(bb[2])) + 2, int(math.ceil(bb[3])) + 2
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).text((-x0, -y0), text, font=font, fill=255, anchor='ls', **kw)
    a = np.asarray(im)
    s = None
    if stroke > 0:
        im2 = Image.new('L', (w, h), 0)
        ImageDraw.Draw(im2).text((-x0, -y0), text, font=font, fill=255, anchor='ls', stroke_width=stroke,
                                 stroke_fill=255, **kw)
        s = np.maximum(np.asarray(im2), a)
    adv = font.getlength(text, **kw)
    return a, s, x0, y0, adv


def raster(text, ref, size, stroke=0.0, tracking=0.0, features=None):
    """Cached Glyph of a word at `size` output px. stroke = outline width px (outside+inside, FreeType stroker);
    tracking in em. Fallback fonts per character; RTL runs are shaped right-to-left by raqm."""
    feats = tuple(features) if features else None
    size = max(1.0, round(float(size) * 4) / 4)
    stroke = round(max(0.0, float(stroke)) * 4) / 4
    key = (text, ref, size, stroke, round(float(tracking), 4), feats)
    g = _GLYPHS.get(key)
    if g is not None:
        return g
    rtl = text_direction(text) == 'rtl'
    runs = split_runs(text, ref)
    if rtl:
        runs = runs[::-1]
    pieces, pen = [], 0.0
    trk = float(tracking) * size
    for run, r in runs:
        f = pil_font(r, size)
        rdir = 'rtl' if text_direction(run) == 'rtl' else None
        if trk and not rdir and len(run) > 1:
            for c in run:
                a, s, x0, y0, adv = _draw_piece(c, f, stroke, None, feats)
                pieces.append((a, s, x0 + pen, y0))
                pen += adv + trk
            pen -= trk
        else:
            a, s, x0, y0, adv = _draw_piece(run, f, stroke, rdir, feats)
            pieces.append((a, s, x0 + pen, y0))
            pen += adv
    if len(pieces) == 1 and pieces[0][2] == int(pieces[0][2]):
        a, s, x0, y0 = pieces[0]
        g = Glyph(a, s, int(x0), y0, pen)
    else:
        X0 = int(math.floor(min(p[2] for p in pieces)))
        Y0 = min(p[3] for p in pieces)
        X1 = int(math.ceil(max(p[2] + p[0].shape[1] for p in pieces)))
        Y1 = max(p[3] + p[0].shape[0] for p in pieces)
        A = np.zeros((Y1 - Y0, X1 - X0), np.uint8)
        S = np.zeros_like(A) if stroke > 0 else None
        for a, s, x0, y0 in pieces:
            xi, yi = int(round(x0)) - X0, y0 - Y0
            sl = (slice(yi, yi + a.shape[0]), slice(xi, xi + a.shape[1]))
            np.maximum(A[sl], a[:A[sl].shape[0], :A[sl].shape[1]], out=A[sl])
            if S is not None:
                np.maximum(S[sl], s[:S[sl].shape[0], :S[sl].shape[1]], out=S[sl])
        g = Glyph(A, S, X0, Y0, pen)
    nb = g.a.nbytes * (2 if g.s is not None else 1)
    _GLYPHS.put(key, g, nb)
    return g


# ============================================================================ layout
# language data: Russian + English — short function words that never end a line, and units glued to a number
_ORPHANS = set('в во на с со к ко по за из от до у о об и а но не ни же ли бы да или то что как the a an of to in on at '
               'by for and or but with from as than into onto via about over under per this these those that my your '
               'his her our their its some any every each no very if because'.split())
_UNITS = set('% ‰ ₽ $ € £ ¥ руб руб. р. тыс тыс. млн млрд км кг м см мм г л мин сек с ч дн шт km kg m cm mm g l min '
             'sec s h k m b x × pcs тысяч тысячи тысяча миллионов миллиона миллион миллиардов миллиарда рублей рубля '
             'рубль долларов доллара доллар евро процентов процента процент thousand million billion dollars percent'
             .split())
_NUM_RE = re.compile(r'^[+\-−]?[$€£₽]?\d[\d  .,]*$')
_DIGIT_GROUP_RE = re.compile(r'^\d{3}(?:[.,]\d+)?[%₽$€]?[.,;:!?»)]*$')     # the "000" of an ASR-split "12 000"


def glue_flags(tokens):
    """glue[i] True = no line/chunk break between token i and i+1 (Russian/English short function words stay with the
    next word, numbers stay with their unit, a dash never starts a line)."""
    n = len(tokens)
    g = [False] * n
    for i in range(n - 1):
        t = tokens[i]
        core = t.strip('«»"\'()[]').lower()
        nxt = tokens[i + 1]
        if core in _ORPHANS:
            g[i] = True
        if _NUM_RE.match(t) and (nxt.strip('.,;:!?»)').lower() in _UNITS or nxt[:1] in '%₽$€‰'
                                 or (_DIGIT_GROUP_RE.match(nxt) and not re.search(r'[.,;:!?]$', t))):
            g[i] = True
        if nxt in ('—', '–', '-'):
            g[i] = True
    return g


def _units(n, glue):
    out, j = [], 0
    while j < n:
        k = j
        while k < n - 1 and glue[k]:
            k += 1
        out.append((j, k))
        j = k + 1
    return out


def _wrap(widths, space, limit, glue, hard=None, gaps=None):
    """Greedy wrap of token widths into lines no wider than `limit` (glued tokens never split; hard[i] = a forced
    break after token i; gaps[i] = the gap after token i instead of `space`, 0 inside a split CJK run). -> [(i0, i1)]"""
    lines, cur, cur_w = [], None, 0.0

    def gap(i):
        return space if gaps is None else gaps[i]
    for a, b in _units(len(widths), glue):
        w = sum(widths[a:b + 1]) + (space * (b - a) if gaps is None else sum(gaps[a:b]))
        if cur is None:
            cur, cur_w = [a, b], w
        elif cur_w + gap(cur[1]) + w <= limit + 1e-6 and not (hard and hard[cur[1]]):
            cur[1], cur_w = b, cur_w + gap(cur[1]) + w
        else:
            lines.append(tuple(cur))
            cur, cur_w = [a, b], w
    if cur is not None:
        lines.append(tuple(cur))
    return lines


# CJK line breaking: any character boundary, except before closing punctuation / small kana / prolonged sound mark
# (they stay with the previous character) and after opening brackets (they stay with the next one)
_NO_START = set('、。，．,.！？!?：；:;）〕］｝〉》」』】〙〗〟’”｠»・ーぁぃぅぇぉっゃゅょゎゕゖァィゥェォッャュョヮヵヶㇰㇱㇲㇳㇴㇵㇶㇷㇸㇹㇺㇻㇼㇽㇾㇿ々〻‐゠–〜～…‥')
_NO_END = set('（〔［｛〈《「『【〘〖〝‘“｟«')


def cjk_pieces(token):
    """Break a CJK token into line-breakable pieces (one ideograph / kana each, Latin runs and Hangul words kept
    whole, kinsoku rules applied)."""
    pieces = []
    for c in token:
        sc = char_script(c)
        breakable = sc in ('han', 'kana') or (sc == 'cjk' and c not in _NO_START)
        if not pieces:
            pieces.append(c)
        elif c in _NO_START or pieces[-1][-1] in _NO_END:
            pieces[-1] += c
        elif breakable or char_script(pieces[-1][-1]) in ('han', 'kana', 'cjk'):
            pieces.append(c)
        else:
            pieces[-1] += c
    return pieces


def _cjk_split(toks, hard, ref, size, tracking, feats, max_width):
    """Split CJK tokens wider than max_width into pieces joined without spaces -> (toks, hard, join)."""
    out, hd, jn = [], [], []
    for t, h in zip(toks, hard):
        if is_cjk(t) and len(t) > 1 and text_length(t, ref, size, tracking, feats) > max_width:
            ps = cjk_pieces(t)
            for j, pc in enumerate(ps):
                out.append(pc)
                hd.append(h if j == len(ps) - 1 else False)
                jn.append(j < len(ps) - 1)
        else:
            out.append(t)
            hd.append(h)
            jn.append(False)
    return out, hd, jn


class WordPos:
    __slots__ = ('text', 'x', 'base', 'w', 'line', 'i', 'rtl')

    def __init__(self, text, x, base, w, line, i, rtl=False):
        self.text, self.x, self.base, self.w, self.line, self.i, self.rtl = text, x, base, w, line, i, rtl

    def __repr__(self):
        return f'WordPos({self.text!r}, x={self.x:.1f}, base={self.base:.1f}, w={self.w:.1f}, line={self.line})'


class Block:
    """Laid-out text in canvas px: words (WordPos), lines [(x0, width, base, i0, i1)], width/height of the layout box
    (top = cap line of the first line, bottom = descender of the last), size used after fitting."""
    __slots__ = ('words', 'lines', 'size', 'ref', 'width', 'height', 'cap', 'desc', 'line_h', 'tracking', 'features',
                 'overflow', 'align', 'key')

    def __repr__(self):
        return f'Block({len(self.words)} words, {len(self.lines)} lines, size={self.size:.1f}, {self.width:.0f}x{self.height:.0f})'


def tokenize(text):
    """Split on ordinary whitespace only (NBSP and narrow NBSP stay inside tokens)."""
    return [t for t in re.split(r'[ \t\r\n]+', str(text)) if t]


def layout_words(words, font='inter', size=64.0, max_width=None, max_lines=None, line_height=1.15, align='center',
                 tracking=0.0, caps=False, weight=None, axes=None, min_size=None, max_height=None, balance=None,
                 features=None, word_spacing=0.0, glue=True):
    """Lay out tokens (list or string) into lines, all in canvas px.

    Fits automatically: shrinks the size when a token (or glued group) is wider than max_width, when more than
    max_lines lines are needed, or when the block is taller than max_height (never below min_size, default 0.35×size).
    balance (default for centred text): lines of similar length instead of a greedy long first line.
    Returns a Block; block.overflow is True if it still does not fit at min_size."""
    if isinstance(words, str):
        raw = [t for t in re.split(r'[ \t\r]+|(\n)', words) if t]
    else:
        raw = [str(w) for w in words if str(w)]
    toks, hard = [], []
    for t in raw:                       # '\n' tokens force a line break after the previous word
        if t == '\n':
            if hard:
                hard[-1] = True
            continue
        toks.append(t)
        hard.append(False)
    if caps:
        toks = [t.upper() for t in toks]
    ref = font if isinstance(font, FontRef) else font_ref(font, weight, axes)
    S = float(size)
    feats = tuple(features) if features else None
    join = [False] * len(toks)
    cjk = any(is_cjk(t) for t in toks)
    if cjk and max_width and max_width > 0:
        toks, hard, join = _cjk_split(toks, hard, ref, S, tracking, feats, max_width)
    kins = [False] * len(toks)
    if cjk:
        # Chinese / Japanese words (e.g. ASR tokens) sit together without spaces; kinsoku glue at the joins
        for i in range(len(toks) - 1):
            a_, b_ = toks[i][-1:], toks[i + 1][:1]
            if (char_script(a_) in ('han', 'kana', 'cjk') and char_script(b_) in ('han', 'kana', 'cjk')
                    and 'hangul' not in (char_script(a_), char_script(b_))):
                join[i] = True
                kins[i] = b_ in _NO_START or a_ in _NO_END
    widths = [text_length(t, ref, S, tracking, feats) for t in toks]
    m = font_metrics(ref)
    space = m['space'] * S + tracking * S + word_spacing * S
    gaps = [0.0 if join[i] else space for i in range(max(0, len(toks) - 1))]
    gl = glue_flags(toks) if glue else [False] * len(toks)
    gl = [(g or k) and not h for g, k, h in zip(gl, kins, hard)]
    hard = hard if any(hard) else None
    smin = float(min_size) if min_size else 0.35 * S
    kmin = min(1.0, smin / S) if S > 0 else 1.0
    units = _units(len(toks), gl)
    unit_w = [sum(widths[a:b + 1]) + sum(gaps[a:b]) for a, b in units] or [0.0]
    k = 1.0
    overflow = False
    if max_width and max_width > 0:
        if max(unit_w) > max_width:
            k = max_width / max(unit_w) * 0.999
        if max_lines and len(_wrap(widths, space, max_width / k, gl, hard, gaps)) > max_lines:
            lo, hi = kmin, k
            if len(_wrap(widths, space, max_width / lo, gl, hard, gaps)) > max_lines:
                k = lo
                overflow = True
            else:
                for _ in range(22):
                    mid = (lo + hi) / 2
                    if len(_wrap(widths, space, max_width / mid, gl, hard, gaps)) <= max_lines:
                        lo = mid
                    else:
                        hi = mid
                k = lo
    for _ in range(3):
        if not max_height:
            break
        limit = max_width / k if max_width else float('inf')
        nl = len(_wrap(widths, space, limit, gl, hard, gaps)) if max_width else 1
        hgt = (m['cap'] + m['desc'] + (nl - 1) * line_height) * S * k
        if hgt <= max_height:
            break
        k *= max_height / hgt * 0.999
    if k < kmin:
        k, overflow = kmin, True
    if overflow and max_width:
        # still too big at the soft floor: first allow more lines, then shrink an unbreakable unit until it fits
        if max_lines and len(_wrap(widths, space, max_width / k, gl, hard, gaps)) > max_lines:
            max_lines = len(_wrap(widths, space, max_width / k, gl, hard, gaps))
        if max(unit_w) * k > max_width:
            k = max_width / max(unit_w) * 0.999
        overflow = False
    limit = max_width / k if max_width else float('inf')
    lines = _wrap(widths, space, limit, gl, hard, gaps) if (max_width or hard) else [(0, len(toks) - 1)] if toks else []
    if balance is None:
        balance = align == 'center'
    if balance and max_width and len(lines) > 1:
        lo, hi, n = max(unit_w), limit, len(lines)
        for _ in range(20):
            mid = (lo + hi) / 2
            if len(_wrap(widths, space, mid, gl, hard, gaps)) <= n:
                hi = mid
            else:
                lo = mid
        lines = _wrap(widths, space, hi, gl, hard, gaps)
    s = S * k
    b = Block()
    b.ref, b.size, b.tracking, b.features, b.align = ref, s, float(tracking), feats, align
    b.cap, b.desc, b.line_h = m['cap'] * s, m['desc'] * s, line_height * s
    sp = space * k
    lw = [sum(widths[a:c + 1]) * k + sum(gaps[a:c]) * k for a, c in lines]
    b.width = max(lw) if lw else 0.0
    b.words, b.lines = [], []
    for li, ((a, c), w) in enumerate(zip(lines, lw)):
        x0 = 0.0 if align == 'left' else (b.width - w) if align == 'right' else (b.width - w) / 2
        base = b.cap + li * b.line_h
        rtl = text_direction(' '.join(toks[a:c + 1])) == 'rtl'
        order = list(range(a, c + 1))
        x = x0
        if rtl:
            x = x0 + w
            for i in order:
                ww = widths[i] * k
                x -= ww
                b.words.append(WordPos(toks[i], x, base, ww, li, i, True))
                x -= gaps[i] * k if i < len(gaps) else sp
        else:
            for i in order:
                ww = widths[i] * k
                b.words.append(WordPos(toks[i], x, base, ww, li, i, False))
                x += ww + (gaps[i] * k if i < len(gaps) else sp)
        b.lines.append((x0, w, base, a, c))
    b.words.sort(key=lambda wp: wp.i)
    b.height = b.cap + b.desc + max(0, len(lines) - 1) * b.line_h
    b.overflow = overflow
    b.key = (tuple(toks), ref, round(s, 3), round(b.width, 2), align, round(line_height, 3), b.tracking, feats,
             tuple(lines))
    return b


def char_offsets(text, ref, size, tracking=0.0, features=None):
    """x offset (px at `size`) of every character of a word from the word's pen origin (kerning included)."""
    return [text_length(text[:j], ref, size, tracking, features) + (tracking * size if (j and tracking) else 0.0)
            for j in range(len(text))]


# ============================================================================ premultiplied pixel ops
def _over(dst, src):
    """dst = src + dst·(1 − src_a), in place; both (h, w, 4) premultiplied, same shape."""
    inv = 1.0 - src[..., 3]
    for c in range(4):
        d = dst[..., c]
        d *= inv
        d += src[..., c]


def _over_mask(dst, m, col):
    """Colour `col` (straight rgba) with coverage m (h, w float 0..1) over dst (h, w, 4), in place."""
    r, g, b, a = col
    am = m * a if a != 1.0 else m
    inv = 1.0 - am
    for c, v in enumerate((r, g, b)):
        d = dst[..., c]
        d *= inv
        if v:
            d += am * v
    d = dst[..., 3]
    d *= inv
    d += am


def fast_blur(img, sigma):
    """Gaussian-ish blur that stays cheap for big radii (downscale → blur → upscale)."""
    if sigma < 0.35:
        return img
    if sigma <= 3.0:
        return cv2.GaussianBlur(img, (0, 0), sigma)
    h, w = img.shape[:2]
    k = max(2, int(sigma / 1.6))
    sw, sh = max(1, w // k), max(1, h // k)
    small = cv2.resize(img, (sw, sh), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), sigma / k)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)


def _pad(rgba, p):
    p = int(math.ceil(p))
    if p <= 0:
        return rgba, 0
    return cv2.copyMakeBorder(rgba, p, p, p, p, cv2.BORDER_CONSTANT, value=0), p


def round_rect_mask(w, h, r, ss=1.0):
    """Anti-aliased rounded rectangle coverage (h, w) float32 with corner radius r (px)."""
    w, h = max(1, int(round(w))), max(1, int(round(h)))
    r = _clamp(float(r), 0.0, min(w, h) / 2.0)
    if r < 0.5:
        return np.ones((h, w), np.float32)
    ys = np.arange(h, dtype=np.float32) + 0.5
    xs = np.arange(w, dtype=np.float32) + 0.5
    dx = np.maximum(np.maximum(r - xs, xs - (w - r)), 0)[None, :]
    dy = np.maximum(np.maximum(r - ys, ys - (h - r)), 0)[:, None]
    d = np.sqrt(dx * dx + dy * dy) - r
    return np.clip(0.5 - d, 0.0, 1.0).astype(np.float32)


class Sprite:
    """Premultiplied RGBA patch (float32 (h, w, 4)); (x, y) = its top-left relative to the element origin (output px)."""
    __slots__ = ('rgba', 'x', 'y')

    def __init__(self, rgba, x=0.0, y=0.0):
        self.rgba, self.x, self.y = rgba, x, y

    @property
    def w(self):
        return self.rgba.shape[1]

    @property
    def h(self):
        return self.rgba.shape[0]

    def tight(self, thr=0.01):
        """Bounding box (x0, y0, x1, y1) of visible pixels relative to the element origin, or None."""
        a = self.rgba[..., 3]
        rows = np.flatnonzero(a.max(axis=1) > thr)
        if not len(rows):
            return None
        cols = np.flatnonzero(a.max(axis=0) > thr)
        return (self.x + cols[0], self.y + rows[0], self.x + cols[-1] + 1, self.y + rows[-1] + 1)


def colored_sprite(mask, col, x=0.0, y=0.0):
    """Coverage mask (h, w float 0..1) + straight colour -> Sprite."""
    r, g, b, a = col
    m = mask.astype(np.float32) * a
    out = np.empty(mask.shape + (4,), np.float32)
    out[..., 0] = m * r
    out[..., 1] = m * g
    out[..., 2] = m * b
    out[..., 3] = m
    return Sprite(out, x, y)


# ============================================================================ layer output and canvas
class LayerRGBA(np.ndarray):
    """(oh, ow, 4) float32 premultiplied layer; .bbox = non-empty region (x0, y0, x1, y1); .opaque = alpha is 1
    everywhere (full-frame card). Derived arrays drop both hints."""

    def __array_finalize__(self, obj):
        self.bbox = None
        self.opaque = False


class St:
    """Animation state of one element."""
    __slots__ = ('alpha', 'sx', 'sy', 'rot', 'dx', 'dy', 'blur', 'zblur', 'decor', 'reveal', 'wipe', 'smear',
                 'tint', 'shear', 'chars')

    def __init__(self):
        self.alpha, self.sx, self.sy, self.rot, self.dx, self.dy = 1.0, 1.0, 1.0, 0.0, 0.0, 0.0
        self.blur, self.zblur, self.decor, self.reveal, self.wipe, self.smear = 0.0, 0.0, 1.0, None, None, 0.0
        self.tint, self.shear, self.chars = None, 0.0, None

    def compose(self, o):
        if o is None:
            return self
        self.alpha *= o.alpha
        self.sx *= o.sx
        self.sy *= o.sy
        self.rot += o.rot
        self.dx += o.dx
        self.dy += o.dy
        self.blur = max(self.blur, o.blur)
        self.zblur = max(self.zblur, o.zblur)
        self.decor *= o.decor
        if o.reveal is not None:
            self.reveal = o.reveal if self.reveal is None else min(self.reveal, o.reveal)
        self.wipe = o.wipe if o.wipe is not None else self.wipe
        self.smear = max(self.smear, o.smear)
        self.tint = o.tint if o.tint is not None else self.tint
        self.shear += o.shear
        if o.chars is not None:
            self.chars = o.chars
        return self

    def is_identity(self):
        return (abs(self.sx - 1) < 1e-4 and abs(self.sy - 1) < 1e-4 and abs(self.rot) < 1e-3 and abs(self.shear) < 1e-4
                and self.zblur < 1e-3)

    def __repr__(self):
        return (f'St(a={self.alpha:.2f}, s={self.sx:.3f}/{self.sy:.3f}, d=({self.dx:.1f},{self.dy:.1f}), '
                f'blur={self.blur:.1f}, z={self.zblur:.2f}, rot={self.rot:.1f})')


BUFFER_RING = 0          # > 0: render_layer reuses that many full-frame buffers per size (see _alloc)
_RING = {}


def _alloc(ow, oh, reuse=None):
    """Zeroed (oh, ow, 4) float32 buffer. A fresh array by default (safe to keep). With BUFFER_RING = n (or `reuse`)
    buffers rotate and only their last dirty bbox is cleared: a returned layer then stays valid until n more
    render_layer calls of the same size — composite (or copy) it before that."""
    n = BUFFER_RING if reuse is None else reuse
    if n <= 0:
        return np.zeros((oh, ow, 4), np.float32), None
    ring = _RING.setdefault((ow, oh, n), {'i': 0, 'bufs': [None] * n, 'dirty': [None] * n})
    i = ring['i'] = (ring['i'] + 1) % n
    b = ring['bufs'][i]
    if b is None:
        b = ring['bufs'][i] = np.zeros((oh, ow, 4), np.float32)
    else:
        d = ring['dirty'][i]
        if d is not None:
            b[d[1]:d[3], d[0]:d[2]] = 0.0
    return b, (ring, i)


class Canvas:
    """Full-frame premultiplied RGBA target, allocated lazily; tracks the touched bbox and whether it is opaque."""

    def __init__(self, ow, oh, reuse=None):
        self.ow, self.oh = int(ow), int(oh)
        self.buf = None
        self.bbox = None
        self.opaque = False
        self.reuse = reuse
        self._slot = None

    def _ensure(self):
        if self.buf is None:
            self.buf, self._slot = _alloc(self.ow, self.oh, self.reuse)
        return self.buf

    def _grow(self, X0, Y0, X1, Y1):
        b = self.bbox
        self.bbox = (X0, Y0, X1, Y1) if b is None else (min(b[0], X0), min(b[1], Y0), max(b[2], X1), max(b[3], Y1))

    def blit(self, rgba, x, y, alpha=1.0):
        """Premultiplied over at integer top-left (x, y). Margins with alpha <= 1/255 (blur / shadow padding) are
        skipped, so the layer's bbox is where it really draws (the renderer's boxes sidecar, the QA safe zone)."""
        if alpha <= 1e-5:
            return
        x, y = int(x), int(y)
        ir = _ink_rect(rgba)
        if ir is None:
            return
        X0, Y0, X1, Y1 = max(x + ir[0], 0), max(y + ir[1], 0), min(x + ir[2], self.ow), min(y + ir[3], self.oh)
        if X1 <= X0 or Y1 <= Y0:
            return
        src = rgba[Y0 - y:Y1 - y, X0 - x:X1 - x]
        if alpha != 1.0:
            src = src * np.float32(alpha)
        buf = self._ensure()
        dst = buf[Y0:Y1, X0:X1]
        b = self.bbox
        if b is None or X0 >= b[2] or X1 <= b[0] or Y0 >= b[3] or Y1 <= b[1]:
            dst[...] = src
        else:
            _over(dst, src)
        self._grow(X0, Y0, X1, Y1)

    def fill(self, col, alpha=1.0, rect=None, mask=None):
        """Fill rect (output px, default whole frame) with a straight colour (optionally times a mask)."""
        x0, y0, x1, y1 = rect or (0, 0, self.ow, self.oh)
        x0, y0 = max(0, int(math.floor(x0))), max(0, int(math.floor(y0)))
        x1, y1 = min(self.ow, int(math.ceil(x1))), min(self.oh, int(math.ceil(y1)))
        if x1 <= x0 or y1 <= y0:
            return
        c = col if isinstance(col, tuple) else to_rgba(col)
        a = c[3] * float(alpha)
        if a <= 1e-5:
            return
        if mask is not None:
            spr = colored_sprite(mask, (c[0], c[1], c[2], a))
            self.blit(spr.rgba, x0, y0)
            return
        pm = (c[0] * a, c[1] * a, c[2] * a, a)
        buf = self._ensure()
        b = self.bbox
        full = (x0, y0, x1, y1) == (0, 0, self.ow, self.oh)
        if b is None or x0 >= b[2] or x1 <= b[0] or y0 >= b[3] or y1 <= b[1]:
            cv2.rectangle(buf, (x0, y0), (x1 - 1, y1 - 1), pm, -1)            # empty region: plain fill
        else:
            reg = buf[y0:y1, x0:x1]
            reg[...] = cv2.add(cv2.multiply(reg, (1.0 - a,) * 4), pm)
        if full and a >= 0.999:
            self.opaque = True
        self._grow(x0, y0, x1, y1)

    def place(self, spr, ox, oy, st=None, pivot=None):
        """Draw sprite `spr` whose untransformed top-left is (ox + spr.x, oy + spr.y) (output px), with the animation
        state `st` applied about `pivot` (default: sprite centre): blur, smear, scale/rotation/shear, zoom blur, alpha."""
        if spr is None:
            return
        st = st or _ID
        if st.alpha <= 1e-4:
            return
        if isinstance(spr, MaskSprite):
            if st.is_identity() and st.blur <= 0.4 and st.smear <= 0.8:
                c = spr.col
                self.blit_mask(spr.m, int(round(ox + spr.x + st.dx)), int(round(oy + spr.y + st.dy)),
                               (c[0], c[1], c[2], c[3] * st.alpha))
                return
            spr = spr.to_sprite()
        rgba, X, Y = spr.rgba, ox + spr.x, oy + spr.y
        if pivot is None:
            pivot = (X + rgba.shape[1] / 2.0, Y + rgba.shape[0] / 2.0)
        pivot = (pivot[0] + st.dx, pivot[1] + st.dy)          # the pivot travels with the element
        if st.blur > 0.4:
            rgba, p = _pad(rgba, st.blur * 2.5)
            rgba = fast_blur(rgba, st.blur)
            X, Y = X - p, Y - p
        if st.smear > 0.8:
            L = int(round(st.smear))
            rgba, _ = _pad(rgba, 0)
            rgba = cv2.copyMakeBorder(rgba, 0, 0, L, L, cv2.BORDER_CONSTANT, value=0)
            rgba = cv2.blur(rgba, (2 * L + 1, 1))
            X -= L
        X += st.dx
        Y += st.dy
        if st.is_identity():
            self.blit(rgba, int(round(X)), int(round(Y)), st.alpha)
            return
        px, py = pivot
        c, s = math.cos(math.radians(st.rot)), math.sin(math.radians(st.rot))
        A = np.array([[c, -s], [s, c]], np.float64) @ np.array([[st.sx, st.shear], [0.0, st.sy]], np.float64)
        h, w = rgba.shape[:2]
        n = 1
        if st.zblur > 1e-3:
            n = 4 if h * w * max(st.sx, st.sy) ** 2 > 1.5e6 else 7
        scales = [1.0 + st.zblur * i / max(n - 1, 1) for i in range(n)]
        corners = np.array([[0, 0], [w, 0], [0, h], [w, h]], np.float64) + (X, Y)
        pts = []
        for k in (scales[0], scales[-1]):
            pts.append((corners - (px, py)) @ (A * k).T + (px, py))
        pts = np.vstack(pts)
        bx0, by0 = max(0, int(math.floor(pts[:, 0].min()))), max(0, int(math.floor(pts[:, 1].min())))
        bx1, by1 = min(self.ow, int(math.ceil(pts[:, 0].max()))), min(self.oh, int(math.ceil(pts[:, 1].max())))
        if bx1 <= bx0 or by1 <= by0:
            return
        bw, bh = bx1 - bx0, by1 - by0
        q = 0.5 if (n > 1 and bw * bh > 1.2e6) else 1.0      # big motion-blurred frames: warp at half resolution
        dw, dh = max(1, int(math.ceil(bw * q))), max(1, int(math.ceil(bh * q)))
        acc = None
        for k in scales:
            Ak = A * k
            t = np.array([px, py]) + Ak @ (np.array([X, Y]) - np.array([px, py])) - (bx0, by0)
            M = (np.hstack([Ak, t[:, None]]) * q).astype(np.float64)
            out = cv2.warpAffine(rgba, M, (dw, dh), flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
            acc = out if acc is None else cv2.add(acc, out)
        if n > 1:
            acc *= np.float32(1.0 / n)
        if q != 1.0:
            acc = cv2.resize(acc, (bw, bh), interpolation=cv2.INTER_LINEAR)
        self.blit(acc, bx0, by0, st.alpha)

    def blit_mask(self, m, x, y, col):
        """Coverage mask (uint8 0..255 or float 0..1) at integer (x, y) in a straight colour, over the canvas."""
        x, y = int(x), int(y)
        h, w = m.shape[:2]
        X0, Y0, X1, Y1 = max(x, 0), max(y, 0), min(x + w, self.ow), min(y + h, self.oh)
        if X1 <= X0 or Y1 <= Y0:
            return
        mm = m[Y0 - y:Y1 - y, X0 - x:X1 - x]
        mm = mm.astype(np.float32) * (1.0 / 255.0) if mm.dtype == np.uint8 else mm
        _over_mask(self._ensure()[Y0:Y1, X0:X1], mm, col)
        self._grow(X0, Y0, X1, Y1)

    def fill_mask_full(self, m, col):
        """Full-frame coverage m (oh, ow) float32 in a straight colour — fast path for spotlights / scrims."""
        r, g, b, a = col
        am = (m * np.float32(a)).astype(np.float32) if a != 1.0 else m.astype(np.float32)
        z = np.zeros_like(am) if (r, g, b) == (0, 0, 0) else None
        planes = [z, z, z, am] if z is not None else [am * np.float32(r), am * np.float32(g), am * np.float32(b), am]
        rg = cv2.merge(planes)
        if self.buf is None and self.reuse in (None, 0) and BUFFER_RING <= 0:
            self.buf, self._slot = rg, None
            self._grow(0, 0, self.ow, self.oh)
        else:
            self.blit(rg, 0, 0)

    def apply_mask(self, keep, ox=0, oy=0):
        """Multiply the layer by keep (0..1, e.g. 1 − person mask) inside the bbox; keep's top-left sits at (ox, oy)
        (a full-frame array by default)."""
        if self.buf is None or self.bbox is None:
            return
        x0, y0, x1, y1 = self.bbox
        X0, Y0 = max(x0, ox), max(y0, oy)
        X1, Y1 = min(x1, ox + keep.shape[1]), min(y1, oy + keep.shape[0])
        if X1 > X0 and Y1 > Y0:
            k = keep[Y0 - oy:Y1 - oy, X0 - ox:X1 - ox]
            reg = self.buf[Y0:Y1, X0:X1]
            for c in range(4):
                reg[..., c] *= k
        self.opaque = False

    def result(self):
        if self.buf is None or self.bbox is None:
            return None
        if self._slot is not None:
            ring, i = self._slot
            ring['dirty'][i] = self.bbox
        out = self.buf.view(LayerRGBA)
        out.bbox = self.bbox
        out.opaque = self.opaque
        return out


_ID = St()


# ============================================================================ compositing (public)
def _alpha_bbox(a, thr=0.0):
    rows = np.flatnonzero(a.max(axis=1) > thr)
    if not len(rows):
        return None
    cols = np.flatnonzero(a.max(axis=0) > thr)
    return (int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1)


BLENDS = ('normal', 'difference', 'multiply', 'screen', 'add')


def composite(x, rgba, blend='normal', opacity=1.0):
    """Composite a premultiplied layer onto x (float32 (oh, ow, 3) 0..1) in place inside its bbox; returns x.
    normal: x(1−a)+c · difference: x(1−a)+|x·a−c| · multiply: x(1−a)+x·c · screen: x+c(1−x) · add: x+c."""
    if rgba is None:
        return x
    if x.dtype != np.float32 or not x.flags.writeable:
        x = np.array(x, np.float32)
    b = (blend or 'normal').lower()
    if (getattr(rgba, 'opaque', False) and b == 'normal' and opacity >= 0.999 and rgba.shape[:2] == x.shape[:2]
            and x.flags.c_contiguous):
        cv2.cvtColor(np.asarray(rgba), cv2.COLOR_RGBA2RGB, dst=x)           # opaque card: the layer replaces x
        return x
    bb = getattr(rgba, 'bbox', None)
    if bb is None or rgba.shape[:2] != x.shape[:2]:
        if rgba.shape[:2] != x.shape[:2]:
            rgba = cv2.resize(np.asarray(rgba, np.float32), (x.shape[1], x.shape[0]), interpolation=cv2.INTER_LINEAR)
        bb = _alpha_bbox(rgba[..., 3])
        if bb is None:
            return x
    x0, y0, x1, y1 = bb
    r = np.asarray(rgba[y0:y1, x0:x1], np.float32)
    if r.size == 0:
        return x
    xs = x[y0:y1, x0:x1]
    h, w = r.shape[:2]
    sc3, sc1, sa3 = _scratch(h, w)
    c = cv2.cvtColor(r, cv2.COLOR_RGBA2RGB, dst=sc3)
    a = cv2.extractChannel(r, 3, dst=sc1)
    if opacity != 1.0:
        c = cv2.multiply(c, (float(opacity),) * 3, dst=c)
        a = cv2.multiply(a, float(opacity), dst=a)
    if b == 'normal':
        inv = cv2.subtract(1.0, a, dst=a)
        inv3 = cv2.cvtColor(inv, cv2.COLOR_GRAY2RGB, dst=sa3)
        out = cv2.multiply(xs, inv3)
        out = cv2.add(out, c, dst=out)
    else:
        a3 = cv2.cvtColor(a, cv2.COLOR_GRAY2RGB, dst=sa3)
        if b == 'add':
            out = xs + c
        elif b == 'screen':
            out = xs + c * (1.0 - xs)
        elif b == 'multiply':
            out = xs * (1.0 - a3 + c)
        elif b == 'difference':
            out = xs * (1.0 - a3) + np.abs(xs * a3 - c)
        else:
            out = xs * (1.0 - a3) + c
        np.clip(out, 0.0, 1.0, out=out)
    xs[...] = out
    return x


_SCR = {}


def _scratch(h, w):
    """Reusable float32 scratch planes (no fresh page faults per frame): (h, w, 3), (h, w), (h, w, 3) views."""
    H, W = _SCR.get('shape', (0, 0))
    if h > H or w > W:
        H, W = max(h, H), max(w, W)
        _SCR['shape'] = (H, W)
        _SCR['c3'] = np.empty((H, W, 3), np.float32)
        _SCR['c1'] = np.empty((H, W), np.float32)
        _SCR['a3'] = np.empty((H, W, 3), np.float32)
    return _SCR['c3'][:h, :w], _SCR['c1'][:h, :w], _SCR['a3'][:h, :w]


def check_safe_zone(rgba, zone='auto', thr=0.02, tol=1.0):
    """Numeric safe-zone check of a rendered layer: ok, bbox and zone (fractions), overflow per side (px), share of
    alpha mass outside the zone."""
    oh, ow = rgba.shape[:2]
    a = np.asarray(rgba[..., 3])
    zx0, zy0, zx1, zy1 = safe_rect(zone, ow, oh)
    bb = _alpha_bbox(a, thr)
    res = dict(zone=[round(zx0 / ow, 4), round(zy0 / oh, 4), round(zx1 / ow, 4), round(zy1 / oh, 4)])
    if bb is None:
        res.update(ok=True, bbox=None, overflow=None, outside_share=0.0)
        return res
    x0, y0, x1, y1 = bb
    ov = dict(left=max(0.0, zx0 - x0), top=max(0.0, zy0 - y0), right=max(0.0, x1 - zx1), bottom=max(0.0, y1 - zy1))
    tot = float(a.sum()) + 1e-9
    inside = float(a[int(math.ceil(zy0)):int(zy1), int(math.ceil(zx0)):int(zx1)].sum())
    res.update(ok=all(v <= tol for v in ov.values()), bbox=[round(x0 / ow, 4), round(y0 / oh, 4), round(x1 / ow, 4),
               round(y1 / oh, 4)], overflow={k: round(v, 1) for k, v in ov.items()},
               outside_share=round(max(0.0, 1.0 - inside / tot), 5))
    return res


# ============================================================================ render environment
class Env:
    """One layer on one frame. Output px = canvas px × s."""

    def __init__(self, layer, f, fps, ow, oh, scale, ctx):
        self.layer = layer
        self.f = int(f)
        self.fps = float(fps) if fps else 30.0
        self.ow, self.oh = int(ow), int(oh)
        self.s = float(scale) if scale else 1.0
        self.W, self.H = self.ow / self.s, self.oh / self.s
        self.ctx = ctx or {}
        self.vertical = self.oh > self.ow * 1.15
        self.zone = layer.get('safe_zone', self.ctx.get('safe_zone', 'auto'))
        self.safe = safe_rect(self.zone, self.ow, self.oh)               # output px
        self.safe_c = tuple(v / self.s for v in self.safe)              # canvas px
        self.t = self.f / self.fps
        self.seed = int(layer.get('seed', 7))

    # canvas-px conversions (|v| <= 1: fraction)
    def cH(self, v):
        v = float(v)
        return v * self.H if abs(v) <= 1.0 else v

    def cW(self, v):
        v = float(v)
        return v * self.W if abs(v) <= 1.0 else v

    def o(self, v_canvas):
        return v_canvas * self.s

    def frames(self, sec):
        return float(sec) * self.fps

    def fr25(self, n):
        """Frame count given @25 fps (move cards) -> frames at this fps (rounded, ≥ 1)."""
        return max(1, int(round(float(n) * self.fps / 25.0)))

    def tf(self, t):
        return int(round(float(t) * self.fps))

    def safe_w_center(self, cx):
        """Widest symmetric width (canvas px) around x = cx inside the safe zone."""
        x0, _, x1, _ = self.safe_c
        return max(0.0, 2.0 * min(cx - x0, x1 - cx))


# ============================================================================ animation
ANIM_LIB = {
    # entrances (dur in seconds)
    'cut': {}, 'none': {},
    'fade': {'dur': 0.2, 'ease': 'linear'},
    'pop': {'dur': 0.27, 'scale': [0.9, 1.07, 1.0], 'peak': 0.45, 'ease': 'outQuad', 'grow': 0.1},
    'hit': {'dur': 0.16, 'scale': [1.2, 1.0], 'ease': 'outExpo'},
    'bump': {'dur': 0.2, 'scale': [1.0, 1.05, 1.0], 'peak': 0.2, 'ease': 'outQuad'},
    'slam': {'dur': 0.2, 'scale': [1.55, 0.97, 1.0], 'peak': 0.6, 'ease': 'outExpo', 'zoom_blur': True},
    'slam_in': {'dur': 0.3, 'scale': [6.0, 0.95, 1.0], 'peak': 0.62, 'ease': 'outExpo', 'zoom_blur': True, 'fade': 0.08},
    'scale': {'dur': 0.3, 'scale': [0.0, 1.0], 'ease': 'outBack'},
    'slide': {'dur': 0.12, 'dx': 0.11, 'dy': 0.0, 'ease': 'outCubic', 'fade': 0.6},
    'slide_up': {'dur': 0.25, 'dx': 0.0, 'dy': 0.04, 'ease': 'outCubic', 'fade': 0.6},
    'drop': {'dur': 0.13, 'dx': 0.0, 'dy': -0.07, 'ease': 'outCubic', 'fade': 0.0},
    'blur_in': {'dur': 1.5, 'r': 0.03, 'ease': 'inCubic', 'fade': 0.4},
    'typewriter': {'cps': 14.0, 'cursor': False, 'fade_frames': 0},
    'write_on': {'cps': 18.0, 'cursor': False, 'fade_frames': 2},
    'cascade': {'per_letter': 0.06, 'jitter': 0.3, 'settle': 0.16, 'tracking': 0.2, 'tracking_dur': 0.25},
    'decode': {'dur': 0.6, 'plate': True},
    'stretch': {'dur': 0.45, 'from': 0.1, 'ease': 'outCubic', 'smear': 0.03},
    'reveal_center_out': {'dur': 0.6, 'ease': 'outCubic', 'soft': 0.04},
    'wipe': {'dur': 0.3, 'ease': 'outCubic', 'soft': 0.05, 'dir': 'ltr'},
    'color_reveal': {'dur': 0.8, 'from': '#6a090e', 'ease': 'outQuad'},
    'burst': {'dur': 0.2, 'from': 0.18, 'settle': 0.3, 'ease': 'outExpo', 'zoom_blur': True},
    'strobe': {'dur': 0.5, 'per': 1, 'flip': 0.2},
    'words_build': {'step': 0.3},
    # exits
    'dissolve': {'dur': 0.9, 'ease': 'linear'},
    'zoom_through': {'dur': 0.2, 'scale': 6.0, 'ease': 'inExpo', 'zoom_blur': True},
    'scatter': {'dur': 0.16, 'dist': 0.25},
    'tracking': {'dur': 0.25, 'to': 0.6},
    'pop_out': {'dur': 0.08, 'scale': 1.3},
    'shrink': {'dur': 0.15, 'ease': 'inBack'},
    'blur_out': {'dur': 0.4, 'r': 0.03, 'ease': 'inCubic'},
    'slide_out': {'dur': 0.2, 'dx': 0.0, 'dy': 0.05, 'ease': 'inCubic'},
    'reverse': {'dur': 0.27},
}
_ANIM_ALIAS = {'cut_in': 'cut', 'appear': 'cut', 'fade_in': 'fade', 'fade_out': 'fade', 'scale_in': 'scale',
               'slam_out': 'pop_out', 'zoomthrough': 'zoom_through', 'write': 'write_on', 'type': 'typewriter',
               'bounce': 'pop', 'blur': 'blur_in', 'dissolve_out': 'dissolve', 'explode': 'pop_out'}


def _parse_value(s):
    s = s.strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    try:
        return json.loads(s.replace("'", '"'))
    except Exception:
        pass
    m = re.match(r'^(-?[\d.]+)\s*fr(?:@(\d+))?$', s)
    if m:
        return {'_frames': float(m.group(1)), '_at': float(m.group(2) or 0)}
    return s.strip('\'"')


def _split_args(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '([{':
            depth += 1
        elif ch in ')]}':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return out


def parse_anim(spec, default='cut', fps=30.0):
    """Animation spec -> dict with 'type' and parameters (library defaults filled in). Accepts a name, a call string
    "fade(0.6, ease=outCubic)" or "pop(dur=7fr)", or a dict {"type": ..., "dur": s | "frames": n, ...}."""
    if spec is None or spec is False or spec == '':
        spec = default
    if isinstance(spec, str):
        m = re.match(r'^\s*([A-Za-z_]+)\s*(?:\((.*)\))?\s*$', spec)
        d = {'type': (m.group(1) if m else spec).strip()}
        if m and m.group(2):
            pos = 0
            for part in _split_args(m.group(2)):
                if '=' in part and not part.strip().startswith(('[', '{')):
                    k, v = part.split('=', 1)
                    d[k.strip()] = _parse_value(v)
                else:
                    if pos == 0:
                        d['dur'] = _parse_value(part)
                    pos += 1
    elif isinstance(spec, dict):
        d = dict(spec)
        d['type'] = d.get('type') or d.get('kind') or d.get('name') or default
    else:
        d = {'type': default}
    t = str(d['type']).lower()
    t = _ANIM_ALIAS.get(t, t)
    base = dict(ANIM_LIB.get(t, {}))
    base.update(d)
    base['type'] = t if t in ANIM_LIB else ('cut' if t not in ANIM_LIB else t)
    for key in list(base.keys()):
        v = base[key]
        if isinstance(v, dict) and '_frames' in v:
            base[key] = v['_frames'] * (fps / v['_at'] if v['_at'] else 1.0) / fps
    if 'frames' in base:
        base['dur'] = float(base['frames']) / fps
    if 'frames25' in base:
        base['dur'] = float(base['frames25']) / 25.0
    if 'dur' in base:
        base['dur'] = max(0.0, _f(base['dur'], 0.0))
    return base


def anim_frames(a, fps):
    """Duration of an animation in frames (0 for cut)."""
    if not a or a.get('type') in ('cut', 'none'):
        return 0
    return max(1, int(round(a.get('dur', 0.0) * fps)))


def _keys_scale(scale, v, a):
    sc = list(scale)
    if len(sc) == 1:
        return float(sc[0])
    if len(sc) == 2:
        return sc[0] + (sc[1] - sc[0]) * ease(v, a.get('ease', 'outCubic'))
    pk = _clamp(float(a.get('peak', 0.5)), 0.05, 0.95)
    if v <= pk:
        return sc[0] + (sc[1] - sc[0]) * ease(v / pk, a.get('ease', 'outQuad'))
    return sc[1] + (sc[2] - sc[1]) * ease((v - pk) / (1 - pk), a.get('ease2', 'inOutQuad'))


def in_state(a, k, env, size_out=None):
    """State of an entrance animation k frames after the element appeared (k = 0 is the first visible frame)."""
    st = St()
    if not a:
        return st
    typ = a.get('type', 'cut')
    if typ in ('cut', 'none'):
        return st
    fps = env.fps
    D = max(a.get('dur', 0.0), 1e-6)
    nfr = max(1.0, D * fps)
    u = min(1.0, (k + 1) / nfr)            # appear-type progress (first frame already > 0)
    v = min(1.0, k / max(1.0, nfr - 1))    # transform progress (first frame = start value)
    if typ == 'fade':
        st.alpha = ease(u, a.get('ease', 'linear'))
    elif typ in ('pop', 'hit', 'bump', 'slam', 'slam_in', 'scale'):
        s = _keys_scale(a['scale'], v, a)
        st.sx = st.sy = max(1e-3, s)
        if typ == 'pop' and a.get('grow'):
            st.decor = min(1.0, (k + 1) / max(1.0, a['grow'] * fps))
        if a.get('fade'):
            st.alpha = min(1.0, (k + 1) / max(1.0, a['fade'] * fps))
        if typ == 'scale' and a['scale'][0] < 0.05:
            st.alpha = min(1.0, (k + 1) / max(1.0, 0.3 * nfr))
        if a.get('zoom_blur') and k > 0 and v < 1:
            sp = _keys_scale(a['scale'], max(0.0, (k - 1) / max(1.0, nfr - 1)), a)
            if sp > s:
                st.zblur = min(1.5, (sp / s - 1.0) * 0.6)
    elif typ in ('slide', 'slide_up', 'drop'):
        e = ease(v, a.get('ease', 'outCubic'))
        st.dx = env.o(env.cW(a.get('dx', 0.0))) * (1 - e)
        st.dy = env.o(env.cH(a.get('dy', 0.0))) * (1 - e)
        if a.get('fade'):
            st.alpha = min(1.0, (k + 1) / max(1.0, a['fade'] * nfr))
    elif typ == 'blur_in':
        r = env.o(env.cH(a.get('r', 0.03)))
        st.blur = r * (1.0 - ease(u, a.get('ease', 'inCubic')))
        st.alpha = min(1.0, (k + 1) / max(1.0, a.get('fade', 0.4) * nfr))
    elif typ in ('typewriter', 'write_on'):
        st.reveal = (k + 1) * a.get('cps', 14.0) / fps
    elif typ == 'stretch':
        e = ease(v, a.get('ease', 'outCubic'))
        st.sy = a.get('from', 0.1) + (1 - a.get('from', 0.1)) * e
        st.smear = env.o(env.cW(a.get('smear', 0.03))) * (1 - e)
    elif typ in ('reveal_center_out', 'wipe'):
        st.wipe = (typ, ease(u, a.get('ease', 'outCubic')), a.get('soft', 0.04), a.get('dir', 'ltr'))
    elif typ == 'color_reveal':
        st.tint = (to_rgba(a.get('from', '#6a090e')), 1.0 - ease(u, a.get('ease', 'outQuad')))
        st.alpha = min(1.0, (k + 1) / max(1.0, 0.25 * nfr))
    elif typ == 'burst':
        e = ease(v, a.get('ease', 'outExpo'))
        s0 = a.get('from', 0.18)
        settle = a.get('settle', 0.3) * fps
        if k < nfr:
            s = s0 + (1.06 - s0) * e
        else:
            s = 1.06 - 0.06 * ease(min(1.0, (k - nfr) / max(1.0, settle)), 'outCubic')
        st.sx = st.sy = s
        if 0 < k < nfr:
            sp = s0 + (1.06 - s0) * ease(max(0.0, (k - 1) / max(1.0, nfr - 1)), a.get('ease', 'outExpo'))
            st.zblur = min(1.2, abs(s / max(sp, 1e-3) - 1.0) * 0.5)
    elif typ == 'cascade':
        st.chars = ('cascade', k, a)
    elif typ == 'decode':
        st.chars = ('decode', k, a)
    elif typ == 'strobe':
        per = max(1, int(a.get('per', 1)))
        st.alpha = 1.0 if (k // per) % 2 == 0 else 0.0
        if k / fps < a.get('flip', 0.0):
            st.rot = 180.0
    return st


def out_state(a, j, n, env):
    """State of an exit animation on its j-th frame of n (the element disappears after j = n−1)."""
    st = St()
    if not a:
        return st
    typ = a.get('type', 'cut')
    u = (j + 1) / (n + 1.0)
    if typ in ('fade', 'dissolve'):
        st.alpha = 1.0 - ease(u, a.get('ease', 'linear'))
    elif typ == 'zoom_through':
        S = float(a.get('scale', 6.0))
        e = ease(u, a.get('ease', 'inExpo'))
        s = 1.0 + (S - 1.0) * e
        st.sx = st.sy = s
        st.alpha = 1.0 - _clamp((u - 0.55) / 0.45, 0.0, 1.0)
        if a.get('zoom_blur', True) and j > 0:
            sp = 1.0 + (S - 1.0) * ease(j / (n + 1.0), a.get('ease', 'inExpo'))
            st.zblur = min(1.0, (s / sp - 1.0) * 0.7)
    elif typ == 'pop_out':
        s = 1.0 + (a.get('scale', 1.3) - 1.0) * ease(u, 'outQuad')
        st.sx = st.sy = s
        st.alpha = 1.0 - u
    elif typ == 'shrink':
        st.sx = st.sy = max(0.02, 1.0 - ease(u, a.get('ease', 'inBack')))
    elif typ == 'blur_out':
        st.blur = env.o(env.cH(a.get('r', 0.03))) * ease(u, a.get('ease', 'inCubic'))
        st.alpha = 1.0 - ease(u, 'inQuad')
    elif typ == 'slide_out':
        e = ease(u, a.get('ease', 'inCubic'))
        st.dx = env.o(env.cW(a.get('dx', 0.0))) * e
        st.dy = env.o(env.cH(a.get('dy', 0.05))) * e
        st.alpha = 1.0 - e
    elif typ in ('scatter', 'tracking'):
        st.chars = (typ, u, a)
    elif typ == 'strobe':
        st.alpha = 1.0 if j % 2 == 0 else 0.0
    return st


def element_state(a_in, a_out, f, fa, fb, env, size_out=None):
    """Combined state of an element visible on frames fa..fb (inclusive) with entrance a_in and exit a_out."""
    if f < fa or f > fb:
        return None
    k = f - fa
    if a_in and a_in.get('type') == 'reverse':
        a_in = None
    st = in_state(a_in, k, env, size_out) if a_in else St()
    if a_out and a_out.get('type') not in ('cut', 'none'):
        n = anim_frames(a_out, env.fps)
        n = min(n, fb - fa + 1)
        j = f - (fb - n + 1)
        if j >= 0:
            if a_out.get('type') == 'reverse' and a_in:
                # play the entrance backwards over the last n frames
                st = in_state(a_in, max(0, n - 1 - j), env, size_out)
                if a_in.get('type') in ('cut', 'none'):
                    st.alpha = 1.0 - (j + 1) / (n + 1.0)
            else:
                st.compose(out_state(a_out, j, n, env))
    return st


# ============================================================================ flash-rate guard
def flash_guard(states, lum_of, fps, max_hz=3.0, area=0.05, dl=0.1):
    """Limit luminance flashes of a scheduled sequence (one state key per frame, None = empty).
    A transition is a flash transition when more than `area` of the frame changes luminance by > dl (lum_of(state)
    gives a low-res luminance map, None -> zeros). At most 2·max_hz flash transitions (max_hz flashes) in any 1 s
    window, spaced at least fps / (2·max_hz) frames apart (an even rhythm instead of a burst and a freeze): a change
    that would break either rule is held back (the previous state stays). Returns the shown states."""
    min_gap = max(1, int(math.ceil(fps / (2.0 * max(max_hz, 0.1)))))
    shown, recent, prev, prev_map = [], [], None, None
    cache = {}

    def lum(s):
        if s not in cache:
            cache[s] = lum_of(s)
        return cache[s]

    win = max(1, int(round(fps)))
    for i, s in enumerate(states):
        if s == prev:
            shown.append(s)
            continue
        m1 = lum(s)
        m0 = prev_map if prev_map is not None else (np.zeros_like(m1) if m1 is not None else None)
        flash = False
        if m1 is not None and m0 is not None:
            flash = float((np.abs(m1 - m0) > dl).mean()) > area
        elif m1 is None and m0 is not None:
            flash = float((m0 > dl).mean()) > area
        if flash:
            recent = [t for t in recent if t > i - win]
            if len(recent) >= int(2 * max_hz) or (recent and i - recent[-1] < min_gap):
                shown.append(prev)
                continue
            recent.append(i)
        shown.append(s)
        prev, prev_map = s, m1 if m1 is not None else (np.zeros_like(m0) if m0 is not None else None)
    return shown


def count_flashes(lum_maps, fps, area=0.05, dl=0.1):
    """Max number of flash transitions in any 1 s window of a sequence of luminance maps (QA helper)."""
    marks = []
    for i in range(1, len(lum_maps)):
        if float((np.abs(lum_maps[i] - lum_maps[i - 1]) > dl).mean()) > area:
            marks.append(i)
    win = max(1, int(round(fps)))
    best = 0
    for i, t in enumerate(marks):
        best = max(best, sum(1 for u in marks[i:] if u < t + win))
    return best


# ============================================================================ text toolkit used by the kinds
STYLE_KEYS = ('font', 'weight', 'axes', 'size', 'color', 'gradient', 'stroke', 'shadow', 'box', 'glow', 'caps',
              'tracking', 'line_height', 'align', 'features')


def style_of(L, defaults):
    """defaults <- layer['style'] <- style keys at the top level of the layer (type_class works as a font name)."""
    st = dict(defaults)
    lst = L.get('style')
    if isinstance(lst, str) or (isinstance(lst, dict) and lst.get('preset')):     # caption preset name
        lst = resolve_preset(L).get('style')
    lst = lst if isinstance(lst, dict) else {}
    if L.get('type_class') and not (L.get('font') or lst.get('font')):
        st['font'] = L['type_class']
    st.update({k: v for k, v in lst.items() if k != 'preset'})
    for k in STYLE_KEYS:
        if k in L:
            st[k] = L[k]
    return st


def font_of(st):
    return font_ref(st.get('font', 'inter'), st.get('weight'), st.get('axes'))


class TS:
    """Text style resolved to output px."""
    __slots__ = ('fill', 'grad', 'stroke', 'stroke_col', 'grow', 'shadow', 'box', 'glow', 'key')


def resolve_style(st, env, size_c):
    s = env.s
    size_o = size_c * s
    ts = TS()
    ts.fill = to_rgba(st.get('color', '#ffffff'))
    ts.grad = tuple(to_rgba_list(st['gradient'])) if st.get('gradient') else None
    ts.stroke, ts.stroke_col, ts.grow = 0.0, (0.0, 0.0, 0.0, 1.0), 0
    sk = st.get('stroke')
    if sk:
        if isinstance(sk, (int, float)) and not isinstance(sk, bool):
            w = float(sk) * size_c if sk <= 1 else float(sk)
            col, al, grow = '#000000', 1.0, 0
        else:
            d = {} if sk is True else dict(sk)
            if 'w_h' in d:
                w = float(d['w_h']) * env.H
            elif 'px' in d:
                w = float(d['px'])
            else:
                w = float(d.get('w', 0.08))
                w = w * size_c if w <= 1 else w
            col, al, grow = d.get('color', '#000000'), d.get('alpha', 1.0), d.get('grow', 0)
        ts.stroke = max(0.0, w * s)
        ts.stroke_col = to_rgba(col, al)
        ts.grow = int(grow or 0)
    ts.shadow = None
    sh = st.get('shadow')
    if sh:
        d = {} if sh is True else dict(sh)
        ts.shadow = (float(d.get('dx', 0.0)) * size_o, float(d.get('dy', 0.04)) * size_o,
                     max(0.0, float(d.get('blur', 0.08))) * size_o, to_rgba(d.get('color', '#000000'), d.get('alpha', 0.7)))
    ts.box = None
    bx = st.get('box')
    if bx:
        d = {} if bx is True else dict(bx)
        pad = d.get('pad', [0.28, 0.12])
        if isinstance(pad, (int, float)):
            pad = [pad, pad]
        ts.box = (to_rgba(d.get('color', '#000000'), d.get('alpha', 0.5)), float(pad[0]) * size_o, float(pad[1]) * size_o,
                  float(d.get('radius', 0.22)) * size_o, str(d.get('mode', 'block')))
    ts.glow = None
    gl = st.get('glow')
    if gl:
        d = {} if gl is True else dict(gl)
        ts.glow = (to_rgba(d.get('color', st.get('color', '#ffffff')), d.get('alpha', 0.85)),
                   float(d.get('blur', 0.12)) * size_o, float(d.get('strength', 1.4)))
    ts.key = (ts.fill, ts.grad, round(ts.stroke, 2), ts.stroke_col, ts.shadow, ts.box, ts.glow)
    return ts


def _shift(m, dx, dy):
    if abs(dx) < 0.05 and abs(dy) < 0.05:
        return m
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(m, M, (m.shape[1], m.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                          borderValue=0)


def _over_mask_rows(dst, m, cr):
    """Like _over_mask with one straight colour per row: cr (h, 4)."""
    am = m * cr[:, 3:4]
    inv = 1.0 - am
    for c in range(3):
        d = dst[..., c]
        d *= inv
        d += am * cr[:, c:c + 1]
    d = dst[..., 3]
    d *= inv
    d += am


def _grad_rows(grad, y_abs, top, bottom):
    t = np.clip((y_abs - top) / max(1e-3, bottom - top), 0.0, 1.0)
    stops = np.linspace(0.0, 1.0, len(grad))
    g = np.array(grad, np.float32)
    return np.stack([np.interp(t, stops, g[:, c]) for c in range(4)], axis=1).astype(np.float32)


def _clip_paste(dst, m, ix, iy):
    """Region of dst (h, w, …) under a mask placed at integer (ix, iy) -> (dst_view, mask_view) or (None, None)."""
    H, W = dst.shape[:2]
    h, w = m.shape[:2]
    x0, y0, x1, y1 = max(ix, 0), max(iy, 0), min(ix + w, W), min(iy + h, H)
    if x1 <= x0 or y1 <= y0:
        return None, None
    return dst[y0:y1, x0:x1], m[y0 - iy:y1 - iy, x0 - ix:x1 - ix]


def text_sprite(block, ts, env, cols=None, alphas=None, reveal=None, decor=1.0, outline=False, only=None, fills=None,
                cache=True):
    """Render a laid-out block into a premultiplied Sprite (origin = block top-left, output px).
    cols {word i: rgba}, alphas {word i: opacity}, reveal = visible characters (spaces count), decor = stroke/shadow
    opacity, outline = stroke ring only, only = set of word indices, fills {word i: (progress, rgba2, soft_px)}."""
    key = None
    if cache:
        key = ('t', block.key, ts.key, env.s, None if cols is None else tuple(sorted(cols.items())),
               None if alphas is None else tuple(sorted(alphas.items())), reveal, round(decor, 2), outline,
               None if only is None else tuple(sorted(only)),
               None if fills is None else tuple(sorted((k, (round(v[0], 3),) + tuple(v[1:])) for k, v in fills.items())))
        spr = _SPRITES.get(key)
        if spr is not None:
            return spr
    s = env.s
    size_o = block.size * s
    items = []
    left = None if reveal is None else int(reveal)
    for wp in block.words:
        txt = wp.text
        if left is not None:
            if left <= 0:
                break
            if len(txt) > left:
                txt = txt[:left]
            left -= len(wp.text) + 1
        if only is not None and wp.i not in only:
            continue
        if not txt:
            continue
        g = raster(txt, block.ref, size_o, ts.stroke, block.tracking, block.features)
        X = wp.x * s + g.x0
        if wp.rtl and len(txt) < len(wp.text):
            X += wp.w * s - g.adv
        items.append((g, X, wp.base * s + g.y0, wp))
    rects = []
    if ts.box and items:
        col, px, py, rr, mode = ts.box
        vis = [it[3] for it in items]
        if mode == 'word':
            for wp in vis:
                rects.append((wp.x * s - px, (wp.base - block.cap) * s - py, (wp.x + wp.w) * s + px,
                              (wp.base + block.desc) * s + py))
        elif mode == 'line':
            for li in sorted(set(wp.line for wp in vis)):
                ws = [wp for wp in vis if wp.line == li]
                base = ws[0].base
                rects.append((min(wp.x for wp in ws) * s - px, (base - block.cap) * s - py,
                              max(wp.x + wp.w for wp in ws) * s + px, (base + block.desc) * s + py))
        else:
            rects.append((min(wp.x for wp in vis) * s - px, (min(wp.base for wp in vis) - block.cap) * s - py,
                          max(wp.x + wp.w for wp in vis) * s + px, (max(wp.base for wp in vis) + block.desc) * s + py))
    if not items:
        return None
    mx = 2.0
    if ts.shadow:
        mx = max(mx, abs(ts.shadow[0]) + abs(ts.shadow[1]) + 2.6 * ts.shadow[2] + 2)
    if ts.glow:
        mx = max(mx, 2.6 * ts.glow[1] + 2)
    X0 = int(math.floor(min([X for _, X, _, _ in items] + [r[0] for r in rects]) - mx))
    Y0 = int(math.floor(min([Y for _, _, Y, _ in items] + [r[1] for r in rects]) - mx))
    X1 = int(math.ceil(max([X + g.w for g, X, _, _ in items] + [r[2] for r in rects]) + mx))
    Y1 = int(math.ceil(max([Y + g.h for g, _, Y, _ in items] + [r[3] for r in rects]) + mx))
    buf = np.zeros((Y1 - Y0, X1 - X0, 4), np.float32)
    if rects:
        col, px, py, rr, mode = ts.box
        for a, b, c, d in rects:
            m = round_rect_mask(c - a, d - b, rr)
            reg, mm = _clip_paste(buf, m, int(round(a)) - X0, int(round(b)) - Y0)
            if reg is not None:
                _over_mask(reg, mm, (col[0], col[1], col[2], col[3]))
    if ts.shadow or ts.glow:
        cov = np.zeros(buf.shape[:2], np.float32)
        for g, X, Y, wp in items:
            al = 1.0 if alphas is None else alphas.get(wp.i, 1.0)
            m = (g.s if g.s is not None else g.a).astype(np.float32) * (al / 255.0)
            reg, mm = _clip_paste(cov, m, int(round(X)) - X0, int(round(Y)) - Y0)
            if reg is not None:
                np.maximum(reg, mm, out=reg)
        if ts.glow:
            gcol, gbl, gk = ts.glow
            gm = np.clip(fast_blur(cov, gbl) * gk, 0.0, 1.0)
            _over_mask(buf, gm, (gcol[0], gcol[1], gcol[2], gcol[3] * decor))
        if ts.shadow:
            dx, dy, bl, scol = ts.shadow
            shm = fast_blur(cov, bl) if bl > 0.3 else cov
            _over_mask(buf, _shift(shm, dx, dy), (scol[0], scol[1], scol[2], scol[3] * decor))
    for g, X, Y, wp in items:
        al = 1.0 if alphas is None else alphas.get(wp.i, 1.0)
        if al <= 0:
            continue
        ix, iy = int(round(X)) - X0, int(round(Y)) - Y0
        reg = buf[iy:iy + g.h, ix:ix + g.w]
        if ts.stroke > 0 and g.s is not None and not outline:
            sc = ts.stroke_col
            _over_mask(reg, g.s.astype(np.float32) * (1.0 / 255.0), (sc[0], sc[1], sc[2], sc[3] * al * decor))
        col = cols.get(wp.i, ts.fill) if cols else ts.fill
        m = g.a.astype(np.float32) * (1.0 / 255.0)
        if outline:
            m = np.clip(g.s.astype(np.float32) * (1.0 / 255.0) - m, 0.0, 1.0) if g.s is not None else m
        fl = fills.get(wp.i) if fills else None
        if fl is not None:
            prog, col2, soft = fl
            rel = np.arange(g.w, dtype=np.float32) + (X - wp.x * s)
            ramp = np.clip((prog * wp.w * s - rel) / max(1.0, soft) + 0.5, 0.0, 1.0)[None, :]
            if wp.rtl:
                ramp = ramp[:, ::-1]
            _over_mask(reg, m * (1.0 - ramp), (col[0], col[1], col[2], col[3] * al))
            _over_mask(reg, m * ramp, (col2[0], col2[1], col2[2], col2[3] * al))
        elif ts.grad and not (cols and wp.i in cols):
            ya = Y + np.arange(g.h, dtype=np.float32)
            cr = _grad_rows(ts.grad, ya, (wp.base - block.cap) * s, (wp.base + block.desc * 0.6) * s)
            cr[:, 3] *= al
            _over_mask_rows(reg, m, cr)
        else:
            _over_mask(reg, m, (col[0], col[1], col[2], col[3] * al))
    spr = Sprite(buf, X0, Y0)
    if cache:
        _SPRITES.put(key, spr, buf.nbytes)
    return spr


# language data: Latin + Russian capitals the decode animation cycles through
_DECODE_CHARS = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789#$%&*+=<>?/АБВГДЖЗИКЛМНПРСТФЦЧШЭЮЯ'


def _rnd(seed, i, j=0):
    """Deterministic pseudo-random in [0, 1) for (seed, i, j)."""
    h = hashlib.blake2b(f'{seed}:{i}:{j}'.encode(), digest_size=8).digest()
    return int.from_bytes(h, 'little') / 2.0 ** 64


def char_sprite(block, ts, env, chars, seed=7):
    """Per-character animation (cascade / decode in; scatter / tracking out) of a block -> Sprite."""
    mode, kv, a = chars
    s = env.s
    size_o = block.size * s
    total = sum(len(wp.text) + 1 for wp in block.words)
    items, plate = [], []
    ci = 0
    fps = env.fps
    for wp in block.words:
        if wp.rtl:
            parts = [(wp.text, 0.0)]
        else:
            offs = char_offsets(wp.text, block.ref, block.size, block.tracking, block.features)
            parts = list(zip(wp.text, offs))
        n = len(parts)
        for j, (ch, off) in enumerate(parts):
            if ch.isspace():
                ci += 1
                continue
            dx = dy = 0.0
            al = 1.0
            sub = ch
            if mode == 'cascade':
                per = a.get('per_letter', 0.06) * fps
                kj = ci * per
                if kv < kj:
                    ci += 1
                    continue
                kk = kv - kj
                e = ease(min(1.0, kk / max(1.0, a.get('settle', 0.16) * fps)), 'outCubic')
                r = _rnd(seed, ci) * 2 - 1
                dy = r * a.get('jitter', 0.3) * block.line_h * s * (1 - e)
                al = min(1.0, (kk + 1) / 2.0)
                te = ease(min(1.0, kv / max(1.0, a.get('tracking_dur', 0.25) * fps)), 'outCubic')
                dx = a.get('tracking', 0.2) * size_o * (j - (n - 1) / 2.0) * (1 - te)
            elif mode == 'scatter':
                e = ease(kv, 'inQuad')
                dist = env.o(env.cH(a.get('dist', 0.25)))
                vx, vy = _rnd(seed, ci, 1) * 2 - 1, (_rnd(seed, ci, 2) * 1.6 - 0.5)
                dx, dy = vx * dist * 0.45 * e, vy * dist * e
                al = 1.0 - kv
            elif mode == 'tracking':
                e = ease(kv, 'outCubic')
                dx = a.get('to', 0.6) * size_o * (j - (n - 1) / 2.0) * e
                al = 1.0 - ease(kv, 'inQuad')
            elif mode == 'decode':
                nfr = max(1.0, a.get('dur', 0.6) * fps)
                resolved = int(total * min(1.0, (kv + 1) / nfr))
                if ci >= resolved:
                    sub = _DECODE_CHARS[int(_rnd(seed, ci, int(kv)) * len(_DECODE_CHARS))]
                    plate.append((wp, off, ch))
            if al <= 0.003:
                ci += 1
                continue
            g = raster(sub, block.ref, size_o, ts.stroke, 0.0, block.features)
            X = (wp.x + off) * s + g.x0 + dx
            if sub != ch:
                X += (text_length(ch, block.ref, size_o) - g.adv) / 2.0
            items.append((g, X, wp.base * s + g.y0 + dy, al, sub != ch))
            ci += 1
        ci += 1
    if not items:
        return None
    X0 = int(math.floor(min(X for _, X, _, _, _ in items))) - 3
    Y0 = int(math.floor(min(Y for _, _, Y, _, _ in items))) - 3
    X1 = int(math.ceil(max(X + g.w for g, X, _, _, _ in items))) + 3
    Y1 = int(math.ceil(max(Y + g.h for g, _, Y, _, _ in items))) + 3
    if plate:
        xs = [(wp.x + off) * s for wp, off, ch in plate]
        X0 = min(X0, int(min(xs)) - 3)
    buf = np.zeros((Y1 - Y0, X1 - X0, 4), np.float32)
    if plate and a.get('plate', True):
        # running white plates under the unresolved characters
        for wp, off, ch in plate:
            cw = text_length(ch, block.ref, size_o)
            x0 = (wp.x + off) * s - 0.04 * size_o
            y0 = (wp.base - block.cap) * s - 0.1 * size_o
            m = np.ones((max(1, int(block.cap * s + block.desc * s + 0.2 * size_o)), max(1, int(cw + 0.08 * size_o))),
                        np.float32)
            reg, mm = _clip_paste(buf, m, int(round(x0)) - X0, int(round(y0)) - Y0)
            if reg is not None:
                _over_mask(reg, mm, (1.0, 1.0, 1.0, 0.92))
    for g, X, Y, al, scrambled in items:
        ix, iy = int(round(X)) - X0, int(round(Y)) - Y0
        if ts.stroke > 0 and g.s is not None:
            reg, mm = _clip_paste(buf, g.s, ix, iy)
            if reg is not None:
                sc = ts.stroke_col
                _over_mask(reg, mm.astype(np.float32) / 255.0, (sc[0], sc[1], sc[2], sc[3] * al))
        reg, mm = _clip_paste(buf, g.a, ix, iy)
        if reg is not None:
            col = (0.05, 0.05, 0.05, 1.0) if (scrambled and plate and a.get('plate', True)) else ts.fill
            _over_mask(reg, mm.astype(np.float32) / 255.0, (col[0], col[1], col[2], col[3] * al))
    return Sprite(buf, X0, Y0)


def apply_wipe(spr, wipe, block, env):
    typ, p, soft, d = wipe
    rgba = spr.rgba.copy()
    w = rgba.shape[1]
    xs = np.arange(w, dtype=np.float32) + spr.x
    bw = max(1.0, block.width * env.s)
    sp = max(1.0, soft * bw)
    if typ == 'reveal_center_out':
        m = np.clip((p * (bw / 2.0 + sp) - np.abs(xs - bw / 2.0)) / sp + 0.5, 0.0, 1.0)
    else:
        edge = p * (bw + 2 * sp) - sp
        m = np.clip((edge - xs) / sp + 0.5, 0.0, 1.0) if d != 'rtl' else np.clip((xs - (bw - edge)) / sp + 0.5, 0.0, 1.0)
    for c in range(4):
        rgba[..., c] *= m[None, :]
    return Sprite(rgba, spr.x, spr.y)


def apply_tint(spr, tint):
    col, t = tint
    if t <= 0.002:
        return spr
    rgba = spr.rgba.copy()
    a = rgba[..., 3]
    for c in range(3):
        rgba[..., c] = rgba[..., c] * (1 - t) + a * col[c] * t
    return Sprite(rgba, spr.x, spr.y)


def orient(v, env):
    """Orientation-dependent value: {'vertical': a, 'landscape': b} -> a on a vertical canvas, b otherwise (any other
    value passes unchanged)."""
    if isinstance(v, dict) and ('vertical' in v or 'landscape' in v):
        return v.get('vertical' if env.vertical else 'landscape', v.get('landscape' if env.vertical else 'vertical'))
    return v


def size_of(st, env, default=0.05):
    """Font size spec -> (size canvas px, fit_width canvas px or None, min canvas px). The spec may be
    orientation-dependent ({'vertical': 0.05, 'landscape': 0.06})."""
    sz = orient(st.get('size', default), env)
    if isinstance(sz, dict):
        fw = sz.get('fit_width')
        return env.cH(sz.get('max', 0.5)), (env.cW(fw) if fw else None), env.cH(sz.get('min', 0.02))
    if isinstance(sz, str) and sz.startswith('fit'):
        m = re.findall(r'[\d.]+', sz)
        fw = float(m[0]) if m else 0.8
        mx = float(m[1]) if len(m) > 1 else 0.5
        return env.cH(mx), env.cW(fw), env.cH(0.02)
    v = env.cH(_f(sz, default))
    return v, None, v * 0.35


def deco_margin(st, env, size_c):
    """Ink that sticks out of the advance box on each side (canvas px): stroke + max(box padding, shadow / glow
    reach ≈ |dx| + 2.5σ). Subtracted from wrap widths so decorated text still fits the safe zone."""
    w = 0.0
    sk = st.get('stroke')
    if sk:
        if isinstance(sk, (int, float)) and not isinstance(sk, bool):
            w = float(sk) * size_c if sk <= 1 else float(sk)
        else:
            d = {} if sk is True else dict(sk)
            if 'w_h' in d:
                w = float(d['w_h']) * env.H
            elif 'px' in d:
                w = float(d['px'])
            else:
                w = float(d.get('w', 0.08))
                w = w * size_c if w <= 1 else w
    extra = 0.0
    bx = st.get('box')
    if bx:
        d = {} if bx is True else dict(bx)
        pad = d.get('pad', [0.28, 0.12])
        pad = pad if isinstance(pad, (list, tuple)) else [pad, pad]
        extra = float(pad[0]) * size_c
    sh = st.get('shadow')
    if sh:
        d = {} if sh is True else dict(sh)
        extra = max(extra, (abs(float(d.get('dx', 0.0))) + 2.5 * float(d.get('blur', 0.08))) * size_c)
    gl = st.get('glow')
    if gl:
        d = {} if gl is True else dict(gl)
        extra = max(extra, 2.5 * float(d.get('blur', 0.12)) * size_c)
    # glyph overhang beyond the advance box (swashes of script and italic faces reach much further)
    key = font_of(st).key
    over = 0.16 if key in ('greatvibes', 'playfair_italic', 'inter_italic', 'caveat') else 0.06
    return w + extra + over * size_c


def make_block(tokens, st, env, max_width=None, max_lines=None, max_height=None, size=None, min_size=None,
               word_spacing=0.0, glue=True):
    """Layout with the style's font / size (fit_width honoured) — sizes in canvas px. Stroke, box and shadow reach are
    taken off the available width first."""
    S, fit, smin = size_of(st, env)
    if size is not None:
        S, fit = float(size), None
        smin = min_size if min_size is not None else S * 0.35
    dm = 2.0 * deco_margin(st, env, S)
    mw = max(max_width * 0.3, max_width - dm) if max_width else max_width
    if fit:
        fit = max(fit * 0.3, fit - dm)
        mw = min(fit, mw) if mw else fit
        if max_lines is None:
            max_lines = 1
    if min_size is not None:
        smin = min_size
    return layout_words(tokens, font_of(st), S, max_width=mw, max_lines=max_lines,
                        line_height=float(st.get('line_height', 1.12)), align=st.get('align', 'center'),
                        tracking=float(st.get('tracking', 0.0)), caps=bool(st.get('caps', False)), min_size=smin,
                        max_height=max_height, features=st.get('features'), word_spacing=word_spacing, glue=glue)


def block_origin(block, x_c, y_c, ax='center', ay='center'):
    """Canvas-px top-left of a block anchored at (x_c, y_c). ay: top|center|bottom|baseline (first line)|
    last_baseline."""
    ox = x_c if ax == 'left' else x_c - block.width if ax == 'right' else x_c - block.width / 2.0
    if ay == 'top':
        oy = y_c
    elif ay == 'bottom':
        oy = y_c - block.height
    elif ay == 'baseline':
        oy = y_c - block.cap
    elif ay == 'last_baseline':
        oy = y_c - block.cap - (len(block.lines) - 1) * block.line_h
    else:
        oy = y_c - block.height / 2.0
    return ox, oy


def clamp_origin(ox, oy, spr, env, grow=1.0, rect=None):
    """Shift an element origin (output px) so the sprite's visible pixels (scaled by `grow` about their centre, for
    animation overshoot) stay inside the safe rectangle; larger-than-zone content is centred in it."""
    tb = _tight(spr)
    if tb is None:
        return ox, oy
    x0, y0, x1, y1 = ox + tb[0], oy + tb[1], ox + tb[2], oy + tb[3]
    if grow != 1.0:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        x0, x1 = cx + (x0 - cx) * grow, cx + (x1 - cx) * grow
        y0, y1 = cy + (y0 - cy) * grow, cy + (y1 - cy) * grow
    sx0, sy0, sx1, sy1 = rect or env.safe
    dx = dy = 0.0
    if x1 - x0 > sx1 - sx0:
        dx = (sx0 + sx1) / 2 - (x0 + x1) / 2
    elif x0 < sx0:
        dx = sx0 - x0
    elif x1 > sx1:
        dx = sx1 - x1
    if y1 - y0 > sy1 - sy0:
        dy = (sy0 + sy1) / 2 - (y0 + y1) / 2
    elif y0 < sy0:
        dy = sy0 - y0
    elif y1 > sy1:
        dy = sy1 - y1
    return ox + dx, oy + dy


_TIGHT = LRU(max_items=4000)
_INKR = LRU(max_items=4000)
_INK_THR = 1.0 / 255.0          # alpha above this is "drawn" (clamps, the blit bbox and the safe-zone sidecar agree)


def _tight(spr):
    k = id(spr.rgba)
    v = _TIGHT.get(k)
    if v is None or v[0] is not spr.rgba:
        v = (spr.rgba, spr.tight(_INK_THR))
        _TIGHT.put(k, v)
    return v[1]


def _ink_rect(rgba):
    """(x0, y0, x1, y1) of the pixels of a premultiplied patch with alpha > 1/255, relative to its top-left; None
    when nothing shows (cached per array)."""
    k = id(rgba)
    v = _INKR.get(k)
    if v is not None and v[0]() is rgba:          # weak reference: per-frame warped patches are not kept alive
        return v[1]
    a = rgba[..., 3]
    rows = np.flatnonzero(a.max(axis=1) > _INK_THR)
    if not len(rows):
        r = None
    else:
        cols = np.flatnonzero(a[rows[0]:rows[-1] + 1].max(axis=0) > _INK_THR)
        r = (int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1)
    try:
        _INKR.put(k, (weakref.ref(rgba), r))
    except TypeError:
        pass
    return r


def cap_scale(st, spr, ox, oy, pivot, env, rect=None):
    """Limit st's scale (and zoom-blur reach) so the sprite, scaled about `pivot`, stays inside the safe rectangle."""
    if st is None or (st.sx <= 1.0 and st.zblur <= 0):
        return st
    tb = _tight(spr)
    if tb is None:
        return st
    px, py = pivot
    sx0, sy0, sx1, sy1 = rect or env.safe
    cap = 9.0
    for d_zone, d_ink in ((px - sx0, px - (ox + tb[0])), (sx1 - px, ox + tb[2] - px),
                          (py - sy0, py - (oy + tb[1])), (sy1 - py, oy + tb[3] - py)):
        if d_ink > 1.0 and d_zone > 0:
            cap = min(cap, d_zone / d_ink)
    peak = st.sx * (1.0 + st.zblur)
    if peak > cap:
        st.sx = st.sy = max(min(1.0, st.sx), min(st.sx, cap))
        st.zblur = max(0.0, cap / max(st.sx, 1e-3) - 1.0)
    return st


def draw_text_el(cv, env, block, ts, ox, oy, st, cols=None, alphas=None, outline=False, only=None, fills=None,
                 pivot=None, seed=7):
    """Draw a block with an animation state; (ox, oy) = block origin in output px. Returns the sprite drawn."""
    if st is None or st.alpha <= 1e-4:
        return None
    if st.chars is not None:
        spr = char_sprite(block, ts, env, st.chars, seed)
    else:
        decor = round(st.decor, 1)
        spr = text_sprite(block, ts, env, cols, alphas, None if st.reveal is None else int(st.reveal), decor, outline,
                          only, fills)
    if spr is None:
        return None
    if st.wipe:
        spr = apply_wipe(spr, st.wipe, block, env)
    if st.tint:
        spr = apply_tint(spr, st.tint)
    if pivot is None:
        # scale / flip about the ink centre of the whole block (caps have no descenders: the layout box centre
        # would sit too low), horizontally about the layout centre
        base = text_sprite(block, ts, env) if (st.chars is not None or st.reveal is not None or only is not None) else spr
        tb = _tight(base) if base is not None else None
        cy = oy + ((tb[1] + tb[3]) / 2.0 if tb else block.height * env.s / 2.0)
        pivot = (ox + block.width * env.s / 2.0, cy)
    cv.place(spr, ox, oy, st, pivot)
    return spr


def norm_words(src):
    """[{w|word|text, t0|start, t1|end}] -> sorted [{'w', 't0', 't1', 'kw'}] (seconds)."""
    out = []
    for w in src or []:
        if not isinstance(w, dict):
            continue
        text = str(w.get('w', w.get('word', w.get('text', '')))).strip()
        t0 = w.get('t0', w.get('start'))
        if not text or t0 is None:
            continue
        t0 = float(t0)
        t1 = w.get('t1', w.get('end'))
        t1 = max(float(t1) if t1 is not None else t0 + 0.3, t0 + 0.02)
        out.append({'w': text, 't0': t0, 't1': t1, 'kw': bool(w.get('kw') or w.get('keyword'))})
    out.sort(key=lambda d: d['t0'])
    return out


def chunk_words(words, fps, max_chars=42, max_lines=2, min_dur=0.8, max_dur=6.0, cps_max=17.0, max_words=None,
                min_words=1, break_on_pause=0.6, lead=-2, tail=6, gap_min=2, join_gap=None, cuts=None,
                split_on_cut=0.3, ellipsis=True, punct_break=True, **_):
    """Subtitle chunks from word timestamps (type.subtitles / type.karaoke).
    A chunk ends at a pause ≥ break_on_pause, a sentence end, a comma once the chunk is half full, when it would need
    more than max_lines lines of max_chars, last longer than max_dur or hold more than max_words; a short function
    word never ends a chunk and a number keeps its digit groups and unit ("12 000 dollars", "15 %"). Frames: f0 = first word start + lead, f1 = last word end + tail, ≥ min_dur, no overlap
    (gaps < gap_min frames or speech gaps ≤ join_gap s are closed: the chunk stays until the next one), extended into
    the following gap when faster than cps_max; chunks crossing a cut by more than split_on_cut s on both sides are
    split at the word nearest the cut, with ellipses. Returns [{i0, i1, f0, f1, text, warn?}]."""
    words = norm_words(words)
    n = len(words)
    if not n:
        return []
    toks = [w['w'] for w in words]
    glue = glue_flags(toks)

    def fits(i0, i1):
        return len(_wrap([len(t) for t in toks[i0:i1 + 1]], 1, max_chars, glue[i0:i1 + 1])) <= max_lines

    groups, start, i = [], 0, 1
    while start < n:
        if i >= n:
            groups.append((start, n - 1))
            break
        prev, w = words[i - 1], words[i]
        pause = w['t0'] - prev['t1'] >= break_on_pause
        brk, hard = pause, False
        if not brk:
            if not fits(start, i):
                brk = hard = True
            elif w['t1'] - words[start]['t0'] > max_dur or (max_words and i - start >= max_words):
                brk = True
            elif punct_break and re.search(r'[.!?…]["»”)]*$', prev['w']) and i - start >= min_words:
                brk = True
            elif (punct_break and re.search(r'[,;:—–]["»”)]*$', prev['w']) and
                  sum(len(t) + 1 for t in toks[start:i]) >= 0.5 * max_chars * max_lines):
                brk = True
        if not brk:
            i += 1
            continue
        j = i
        if not pause and glue[i - 1]:
            # never break inside a glued run ("for 12 000 ₽", "15 %"): move the break back to its start, or — when the
            # whole chunk is that run and the limit was a soft one — just past its end
            while j - 1 > start and glue[j - 1]:
                j -= 1
            if glue[j - 1]:
                k = i
                while k < n and glue[k - 1] and words[k]['t0'] - words[k - 1]['t1'] < break_on_pause:
                    k += 1
                j = k if (not hard and k - i <= 2 and fits(start, k - 1)) else i
        groups.append((start, j - 1))
        start, i = j, j + 1
    out = []
    for a, b in groups:
        f0 = int(round(words[a]['t0'] * fps)) + int(lead)
        f1 = int(round(words[b]['t1'] * fps)) + int(tail)
        f1 = max(f1, f0 + int(math.ceil(min_dur * fps)) - 1)
        out.append({'i0': a, 'i1': b, 'f0': f0, 'f1': f1})
    for k in range(len(out) - 1):
        c, d = out[k], out[k + 1]
        if d['f0'] <= c['f0']:
            d['f0'] = c['f0'] + 1
        gap_s = words[d['i0']]['t0'] - words[c['i1']]['t1']
        if c['f1'] >= d['f0'] - gap_min or (join_gap is not None and gap_s <= join_gap):
            c['f1'] = d['f0'] - 1
        c['f1'] = max(c['f1'], c['f0'])
    for k, c in enumerate(out):
        chars = len(' '.join(toks[c['i0']:c['i1'] + 1]))
        dur = (c['f1'] - c['f0'] + 1) / fps
        if cps_max and chars / dur > cps_max:
            limit = out[k + 1]['f0'] - 1 if k + 1 < len(out) else c['f1'] + int(fps)
            need = c['f0'] + int(math.ceil(chars / cps_max * fps)) - 1
            c['f1'] = max(c['f1'], min(limit, need))
            if chars / ((c['f1'] - c['f0'] + 1) / fps) > cps_max + 1e-6:
                c['warn'] = 'reading speed %.1f cps' % (chars / ((c['f1'] - c['f0'] + 1) / fps))
    if cuts and split_on_cut:
        thr = float(split_on_cut) * fps
        res = []
        for c in out:
            parts = [c]
            for cut in sorted(int(x) for x in cuts):
                last = parts[-1]
                if last['f0'] < cut <= last['f1'] and last['i1'] > last['i0']:
                    before, after = cut - last['f0'], last['f1'] - cut + 1
                    if before > thr and after > thr:
                        best, bd = None, None
                        for j in range(last['i0'] + 1, last['i1'] + 1):
                            dj = abs(int(round(words[j]['t0'] * fps)) + int(lead) - cut)
                            if bd is None or dj < bd:
                                best, bd = j, dj
                        p1 = dict(last, i1=best - 1, f1=cut - 1, ell_end=bool(ellipsis))
                        p2 = dict(last, i0=best, f0=cut, ell_start=bool(ellipsis))
                        p2.pop('ell_end', None)
                        parts[-1:] = [p1, p2]
            res.extend(parts)
        out = res
    for c in out:
        t = toks[c['i0']:c['i1'] + 1]
        if c.get('ell_end'):
            t = t[:-1] + [t[-1].rstrip('.,;:') + '…']
        if c.get('ell_start'):
            t = ['…' + t[0]] + t[1:]
        c['tokens'] = t
        c['text'] = ' '.join(t)
    return out


def _fp(v):
    if callable(v) or isinstance(v, np.ndarray):
        return ('id', id(v))
    try:
        r = repr(v)
        return ('r', hashlib.md5(r.encode('utf-8', 'surrogatepass')).hexdigest()) if len(r) < 2_000_000 else ('id', id(v))
    except Exception:
        return ('id', id(v))


_PLAN_CTX = ('face', 'faces', 'cuts', 'beats', 'downbeats', 'kicks', 'snares', 'words', 'tracks', 'flash_limit_hz',
             'subtitle_band', 'safe_zone')


def faces_at(env, f):
    """Face boxes at frame f in canvas px [(x0, y0, x1, y1)] from layer['faces'] or ctx face/faces."""
    src = env.layer.get('faces', env.ctx.get('face', env.ctx.get('faces')))
    if src is None:
        return []
    try:
        if callable(src):
            r = src(f)
        elif isinstance(src, dict):
            r = src.get(f, src.get(str(f)))
        elif isinstance(src, (list, tuple)) and src and isinstance(src[0], (list, tuple)) and len(src[0]) == 5:
            ks = [k for k in src if k[0] <= f]
            r = (ks[-1] if ks else src[0])[1:]
        else:
            r = src
    except Exception:
        return []
    if r is None:
        return []
    if isinstance(r, dict) or (isinstance(r, (list, tuple)) and len(r) == 4 and all(isinstance(v, (int, float)) for v in r)):
        r = [r]
    out = []
    for b in r:
        if isinstance(b, dict):
            x, y, w, h = float(b.get('x', 0)), float(b.get('y', 0)), float(b.get('w', 0)), float(b.get('h', 0))
            box = [x, y, x + w, y + h]
        else:
            box = [float(v) for v in b[:4]]
        if max(abs(v) for v in box) <= 1.0:           # fractions of the frame; otherwise canvas px already
            box = [box[0] * env.W, box[1] * env.H, box[2] * env.W, box[3] * env.H]
        out.append(tuple(box))
    return out


def _hit(r, boxes, m):
    return any(not (r[2] <= b[0] - m or r[0] >= b[2] + m or r[3] <= b[1] - m or r[1] >= b[3] + m) for b in boxes)


def avoid_dy(rect, boxes, env, step, margin, prefer=1, keep=None, grow=1.0):
    """Vertical shift (canvas px) that moves rect off every box while staying in the safe zone (0 if not needed or
    impossible). keep = (y0, y1) the extent that must stay inside the zone (default rect's: pass the drawn ink with
    outline / shadow), grown by `grow` about its centre (the entrance overshoot, e.g. a pop-in's 1.06)."""
    if not boxes or not _hit(rect, boxes, margin):
        return 0.0
    sy0, sy1 = env.safe_c[1], env.safe_c[3]
    k0, k1 = keep if keep is not None else (rect[1], rect[3])
    half = (k1 - k0) / 2.0 * max(1.0, float(grow))
    kc = (k0 + k1) / 2.0
    for k in range(1, 120):
        for sgn in (prefer, -prefer):
            dy = sgn * k * step
            r = (rect[0], rect[1] + dy, rect[2], rect[3] + dy)
            if kc + dy - half >= sy0 and kc + dy + half <= sy1 and not _hit(r, boxes, margin):
                return dy
    return 0.0


def _words_minmax(src):
    """(first start, last end) seconds of a word list without normalising it (cheap per-frame span checks)."""
    t0, t1 = 1e18, -1e18
    for w in src or ():
        if not isinstance(w, dict):
            continue
        a = w.get('t0', w.get('start'))
        if a is None:
            continue
        a = float(a)
        b = w.get('t1', w.get('end'))
        b = float(b) if b is not None else a + 0.3
        t0 = min(t0, a)
        t1 = max(t1, b)
    return t0, t1


def _span(L, fps, default_dur=2.0):
    f0, f1 = L.get('f0'), L.get('f1')
    if f0 is None:
        f0 = int(round(_f(L.get('t0', 0.0)) * fps))
    if f1 is None:
        if L.get('t1') is not None:
            f1 = int(round(_f(L['t1']) * fps)) - 1
        else:
            f1 = int(f0) + max(1, int(round(_f(L.get('dur', default_dur), default_dur) * fps))) - 1
    return int(f0), int(f1)


# ============================================================================ caption style presets
# Named looks for talk clips (podcast / interview moments, vertical 9:16 first). A subtitle or karaoke layer uses
# one with "style": "<name>" or "style": {"preset": "<name>", ...overrides} (or a top-level "preset"). Layer
# fields win over the preset; nested dicts (highlight, highlight.keyword) are merged. "voice" holds chunking hints
# for producers (ed_voice.subtitle_chunks max_chars / max_lines / max_words).
_POP_CLEAN = {'type': 'pop', 'dur': 0.2, 'scale': [0.8, 1.06, 1.0], 'peak': 0.5, 'ease': 'outQuad',
              'ease2': 'inOutQuad', 'fade': 0.07, 'grow': 0.1}
_POP_SOFT = {'type': 'pop', 'dur': 0.17, 'scale': [0.9, 1.03, 1.0], 'peak': 0.5, 'ease': 'outQuad',
             'ease2': 'inOutQuad', 'fade': 0.08, 'grow': 0.08}
_KW_YELLOW = '#ffd21f'
CAPTION_STYLES = {
    'podcast_bold': {
        'desc': 'Talk-clip captions: heavy white sans, mixed case, thin outline + soft drop shadow, numbers and '
                'keywords in yellow, 1-2 lines in the lower middle, clean pop-in per chunk.',
        'kinds': ['subtitle', 'karaoke'],
        'layer': {
            'style': {'font': 'montserrat:800', 'size': {'vertical': 0.05, 'landscape': 0.062}, 'color': '#ffffff',
                      'stroke': {'w': 0.075, 'color': '#000000'},
                      'shadow': {'dx': 0.0, 'dy': 0.06, 'blur': 0.14, 'alpha': 0.8, 'color': '#000000'},
                      'line_height': 1.06, 'tracking': -0.005},
            'highlight': {'keyword': {'pick': 'numbers', 'color': _KW_YELLOW, 'max_per_chunk': 2}},
            'anim_in': _POP_CLEAN, 'anim_out': 'cut',
            'pos': {'x': 'auto', 'center_y': {'vertical': 0.7, 'landscape': 0.84}},
            'max_width': {'vertical': 0.78, 'landscape': 0.7}, 'avoid': 'face', 'max_lines': 3},
        'voice': {'max_lines': 2, 'max_words': 6}},
    'podcast_caps': {
        'desc': 'Punchy talk-clip captions: condensed black caps, outline + shadow, keywords in yellow, 1-2 short '
                'lines, pop-in per chunk.',
        'kinds': ['subtitle', 'karaoke'],
        'layer': {
            'style': {'font': 'firacond:900', 'size': {'vertical': 0.062, 'landscape': 0.075}, 'color': '#ffffff', 'caps': True,
                      'stroke': {'w': 0.07, 'color': '#000000'},
                      'shadow': {'dx': 0.0, 'dy': 0.05, 'blur': 0.12, 'alpha': 0.8, 'color': '#000000'},
                      'line_height': 0.98, 'tracking': 0.01},
            'highlight': {'keyword': {'pick': 'numbers', 'color': _KW_YELLOW, 'max_per_chunk': 2}},
            'anim_in': _POP_CLEAN, 'anim_out': 'cut',
            'pos': {'x': 'auto', 'center_y': {'vertical': 0.69, 'landscape': 0.83}},
            'max_width': {'vertical': 0.76, 'landscape': 0.66}, 'avoid': 'face', 'max_lines': 3},
        'voice': {'max_lines': 2, 'max_words': 5}},
    'clean': {
        'desc': 'Minimal interview captions: semibold white sans, hairline outline and a wide soft dark halo, '
                'lower placement, short fade in.',
        'kinds': ['subtitle', 'karaoke'],
        'layer': {
            'style': {'font': 'inter:600', 'size': {'vertical': 0.037, 'landscape': 0.048}, 'color': '#ffffff',
                      'stroke': {'w': 0.028, 'color': '#000000', 'alpha': 0.6},
                      'shadow': {'dx': 0.0, 'dy': 0.035, 'blur': 0.1, 'alpha': 0.85, 'color': '#000000'},
                      'glow': {'color': '#000000', 'alpha': 0.62, 'blur': 0.3, 'strength': 1.6},
                      'line_height': 1.16},
            'highlight': {'keyword': {'pick': 'none', 'color': '#ffe58a'}},
            'anim_in': {'type': 'fade', 'dur': 0.12}, 'anim_out': 'cut',
            'pos': {'x': 'auto', 'center_y': {'vertical': 0.735, 'landscape': 0.87}},
            'max_width': {'vertical': 0.8, 'landscape': 0.72}, 'avoid': 'face', 'max_lines': 3},
        'voice': {'max_lines': 2}},
    'boxed': {
        'desc': 'High-contrast captions on busy or bright footage: bold white text on a rounded dark plate per '
                'line, keywords in yellow, soft pop-in.',
        'kinds': ['subtitle', 'karaoke'],
        'layer': {
            'style': {'font': 'inter:700', 'size': {'vertical': 0.04, 'landscape': 0.05}, 'color': '#ffffff', 'stroke': None, 'shadow': None,
                      'box': {'color': '#0a0a0c', 'alpha': 0.72, 'pad': [0.34, 0.17], 'radius': 0.26,
                              'mode': 'line'},
                      'line_height': 1.4},
            'highlight': {'keyword': {'pick': 'numbers', 'color': _KW_YELLOW, 'max_per_chunk': 2}},
            'anim_in': _POP_SOFT, 'anim_out': 'cut',
            'pos': {'x': 'auto', 'center_y': {'vertical': 0.72, 'landscape': 0.86}},
            'max_width': {'vertical': 0.8, 'landscape': 0.72}, 'avoid': 'face', 'max_lines': 3},
        'voice': {'max_lines': 2}},
    'karaoke_highlight': {
        'desc': 'Word-by-word captions: 2-3 heavy caps words, the sounding word turns yellow, numbers in green, '
                'outline + shadow, pop-in per chunk.',
        'kinds': ['karaoke'], 'kind': 'karaoke',
        'layer': {
            'style': {'font': 'montserrat:900', 'size': {'vertical': 0.052, 'landscape': 0.066}, 'color': '#ffffff', 'caps': True,
                      'stroke': {'w': 0.08, 'color': '#000000'},
                      'shadow': {'dx': 0.0, 'dy': 0.06, 'blur': 0.12, 'alpha': 0.8, 'color': '#000000'},
                      'line_height': 1.04},
            'highlight': {'mode': 'color', 'active': _KW_YELLOW,
                          'keyword': {'pick': 'numbers', 'color': '#4dff7c', 'max_per_chunk': 1}},
            'anim_in': _POP_CLEAN, 'anim_out': 'cut',
            'pos': {'x': 'auto', 'center_y': {'vertical': 0.68, 'landscape': 0.84}}, 'avoid': 'face',
            'max_lines': 2},
        'voice': {'max_lines': 2, 'max_words': 3}},
    'karaoke_box': {
        'desc': 'Word-by-word captions with a yellow plate sliding under the sounding word (black text on it), '
                'bold mixed case, soft pop-in.',
        'kinds': ['karaoke'], 'kind': 'karaoke',
        'layer': {
            'style': {'font': 'inter:800', 'size': {'vertical': 0.05, 'landscape': 0.062}, 'color': '#ffffff',
                      'stroke': {'w': 0.045, 'color': '#000000', 'alpha': 0.9},
                      'shadow': {'dx': 0.0, 'dy': 0.05, 'blur': 0.16, 'alpha': 0.85, 'color': '#000000'}},
            'highlight': {'mode': 'box', 'box': {'fill': _KW_YELLOW, 'text': '#000000', 'pad': [0.2, 0.1],
                                                 'radius': 0.24}},
            'anim_in': _POP_SOFT, 'anim_out': 'cut',
            'pos': {'x': 'auto', 'center_y': {'vertical': 0.68, 'landscape': 0.84}}, 'avoid': 'face',
            'max_lines': 2},
        'voice': {'max_lines': 2, 'max_words': 3}},
}
CAPTION_ALIASES = {'aura': 'podcast_bold', 'podcast': 'podcast_bold', 'bold': 'podcast_bold', 'clip': 'podcast_bold',
                   'caps': 'podcast_caps', 'interview': 'clean', 'minimal': 'clean', 'box': 'boxed',
                   'plate': 'boxed', 'karaoke': 'karaoke_highlight', 'highlight': 'karaoke_highlight',
                   'word': 'karaoke_highlight', 'karaoke_plate': 'karaoke_box'}
_CAPTION_KINDS = ('subtitle', 'karaoke')


def caption_style_name(name):
    """Preset name or alias -> canonical CAPTION_STYLES name (None when unknown)."""
    if not isinstance(name, str):
        return None
    n = name.strip().lower().replace('-', '_').replace(' ', '_')
    n = CAPTION_ALIASES.get(n, n)
    return n if n in CAPTION_STYLES else None


def caption_style(name, **overrides):
    """Layer fields of a caption preset (deep copy) merged with overrides: {'style', 'highlight', 'anim_in',
    'anim_out', 'pos', 'max_width', 'avoid', 'max_lines' (most lines at full size before a chunk splits in time),
    'chunk'(, 'kind')}. Unknown name -> ValueError listing the presets."""
    n = caption_style_name(name)
    if n is None:
        raise ValueError(f'unknown caption style {name!r}; known: {sorted(CAPTION_STYLES)} '
                         f'(aliases {sorted(CAPTION_ALIASES)})')
    P = CAPTION_STYLES[n]
    out = json.loads(json.dumps(P['layer']))
    if P.get('kind'):
        out['kind'] = P['kind']
    if 'chunk' not in out and P.get('voice'):         # ed_text's own chunking of raw words follows the same hints
        hv, hl = caption_hints(n, 1080, 1920), caption_hints(n, 1920, 1080)
        out['chunk'] = {k: ({'vertical': hv[k], 'landscape': hl[k]} if hv[k] != hl[k] else hv[k])
                        for k in ('max_chars', 'max_lines', 'max_words') if k in hv}
    for k, v in overrides.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def caption_styles(ow=1080, oh=1920):
    """{name: {desc, kinds, voice}} of every caption preset (for planners and docs); voice = chunking hints for that
    canvas (max_chars measured from the preset's font, size and decoration, see caption_hints)."""
    return {n: {'desc': p['desc'], 'kinds': list(p['kinds']), 'voice': caption_hints(n, ow, oh)}
            for n, p in CAPTION_STYLES.items()}


_HINT_SAMPLE = ('so the crew rides over 12,000 miles a season and that adds up to 3 million steps '
                'это значит что каждую неделю мы бегаем дальше')
_HINTS = {}


def _caption_geom(n, ow, oh):
    """(layer, env, geometry, size px, room px) of caption preset n on a canvas, built from the preset's raw layer
    (caption_style() calls caption_hints, so no resolve_preset here). room = the width a line of text may take
    after outline / shadow / plate reach and the entrance overshoot (exactly what the renderer wraps to)."""
    P = CAPTION_STYLES[n]
    L = json.loads(json.dumps(P['layer']))
    cls = LAYER_KINDS[P.get('kind') or 'subtitle']
    env = Env(L, 0, 30.0, ow, oh, 1.0, None)
    geom = cls.layout_geom(L, env)
    S = size_of(geom['st'], env)[0]
    room = max(geom['maxw'] * 0.3, geom['maxw'] - 2.0 * deco_margin(geom['st'], env, S))
    return L, env, geom, S, room


def caption_hints(name, ow=1080, oh=1920, text=None):
    """Chunking hints of a caption preset for a canvas: {'max_chars', 'max_lines', 'max_px', 'max_words'?}. max_px =
    the room for a line's glyphs (the wrap width minus outline / shadow / plate reach, after the pop-in overshoot -
    exactly what the renderer wraps to). max_chars, measured with the preset's font, size, tracking and caps: with
    `text` (the transcript) the largest N for which every run of its consecutive words of <= N characters fits
    max_px ("And remember," at podcast_bold 1080x1920 -> 12); without, max_px over the average character width of a
    built-in sample (an estimate: text_fits() measures a line exactly)."""
    n = caption_style_name(name)
    if n is None:
        raise ValueError(f'unknown caption style {name!r}')
    key = (n, int(ow), int(oh), hashlib.md5(str(text).encode('utf-8', 'surrogatepass')).hexdigest() if text else None)
    if key in _HINTS:
        return dict(_HINTS[key])
    L, env, geom, S, room = _caption_geom(n, ow, oh)
    st = geom['st']
    ref, tr, caps = font_of(st), float(st.get('tracking', 0.0)), bool(st.get('caps', False))
    space = font_metrics(ref)['space'] * S + tr * S + geom['wsp'] * S
    txt = _HINT_SAMPLE.upper() if caps else _HINT_SAMPLE
    max_chars = int(room / max(text_length(txt, ref, S, tr) / len(txt), 1e-3) * 0.97)
    words = tokenize(text) if text else []
    if words:
        # the text is known: the largest N such that every run of its consecutive words of <= N characters fits
        # the room by measured width (one word wider than the room alone does not count: it cannot wrap)
        wl = [text_length(w.upper() if caps else w, ref, S, tr) for w in words]

        def runs_fit(N):
            for i in range(len(words)):
                chars, width = len(words[i]), wl[i]
                for j in range(i + 1, len(words)):
                    chars += 1 + len(words[j])
                    if chars > N:
                        break
                    width += space + wl[j]
                    if width > room:
                        return False
            return True
        lo, hi = 1, max(max_chars, 8) * 2
        while lo < hi:
            mid = (lo + hi + 1) // 2
            lo, hi = (mid, hi) if runs_fit(mid) else (lo, mid - 1)
        max_chars = lo
    out = dict(CAPTION_STYLES[n].get('voice') or {})
    out['max_chars'] = max(6, max_chars)
    out['max_px'] = int(room)
    out.setdefault('max_lines', 2)
    _HINTS[key] = out
    return dict(out)


def text_fits(text, style, canvas=(1080, 1920), max_lines=None):
    """Does caption text fit at the full preset size? Laid out exactly as the renderer does (same wrap width and
    line breaking, the real font): glyph widths, tracking, the uppercase transform, outline / shadow / plate reach,
    the entrance overshoot and the safe zone - not an average glyph width. style: a caption preset name,
    {'preset': name, ...overrides}, a style dict, or a whole subtitle / karaoke layer. '\\n' in text = the
    producer's line breaks (kept only if each line fits). max_lines: default the layer's chunk.max_lines (presets:
    2). -> {'fits', 'lines' [str, as rendered], 'width_px' (widest line's glyph advance at full size, canvas px),
    'max_px' (the room for a line: wrap width minus outline / shadow / plate reach after the overshoot - also
    caption_hints' max_px), 'size_px', 'n_lines'}. fits is False when more lines are needed, a given line does not
    fit as it is, or one word alone is wider than the room (it would shrink)."""
    ow, oh = (int(canvas['w']), int(canvas['h'])) if isinstance(canvas, dict) else (int(canvas[0]), int(canvas[1]))
    if isinstance(style, dict) and any(k in style for k in ('kind', 'words', 'chunks', 'text')):
        L = dict(style)
    else:
        n = caption_style_name(style if isinstance(style, str) else (style or {}).get('preset'))
        L = {'kind': (CAPTION_STYLES[n].get('kind') if n else None) or 'subtitle', 'style': style}
    L = resolve_preset(L)
    cls = LAYER_KINDS.get(kind_of(L))
    if cls is None or not issubclass(cls, Subtitle):
        cls = Subtitle
    env = Env(L, 0, 30.0, ow, oh, 1.0, None)
    geom = cls.layout_geom(L, env)
    st = geom['st']
    S = size_of(st, env)[0]
    if max_lines is None:
        max_lines = orient((L.get('chunk') or {}).get('max_lines'), env) or 2
    max_lines = int(max_lines)
    raw = [t for t in re.split(r'[ \t\r]+|(\n)', str(text)) if t]
    plain = [t for t in raw if t != '\n']
    given = [ln for ln in (' '.join(x.split()) for x in str(text).split('\n')) if ln] if '\n' in raw else None
    block, ok = _fit_caption(raw, st, env, geom['maxw'], max_lines, max_lines, geom['wsp'], len(given or []), True)
    if len(block.words) == len(plain):
        lines = [' '.join(plain[a:b + 1]) for (_x, _w, _y, a, b) in block.lines]
    else:                                           # CJK runs split into characters
        lines = [''.join(w.text for w in block.words if w.line == i) for i in range(len(block.lines))]
    room = max(geom['maxw'] * 0.3, geom['maxw'] - 2.0 * deco_margin(st, env, S))    # as make_block wraps
    k = S / max(block.size, 1e-6)
    width = max((w for (_x, w, _y, _a, _b) in block.lines), default=0.0) * k
    fits = bool(plain) and ok and len(lines) <= max_lines and block.size >= 0.995 * S and width <= room + 0.5 and \
        (given is None or lines == given)
    return {'fits': bool(fits), 'lines': lines, 'width_px': round(width, 1), 'max_px': round(room, 1),
            'size_px': round(S, 1), 'n_lines': len(lines)}


def _merge(base, over):
    out = dict(base)
    for k, v in (over or {}).items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def _preset_of(L):
    st = L.get('style')
    name = L.get('preset')
    if name is None and isinstance(st, str):
        name = st
    if name is None and isinstance(st, dict):
        name = st.get('preset')
    return name


def resolve_preset(L):
    """Expand a caption preset on a layer ("style": "podcast_bold" | {"preset": ..., overrides} | "preset": ...):
    preset fields fill what the layer does not set; the layer's style dict and highlight dict are merged over the
    preset's; a karaoke-only preset turns a subtitle layer with words into karaoke. Non-caption kinds take only the
    preset's style (font, size, colours, outline, shadow). Layers without a preset pass unchanged."""
    name = _preset_of(L)
    if name is None:
        return L
    n = caption_style_name(name)
    if n is None:
        if isinstance(L.get('style'), str):           # an unknown name must not crash the frame
            _warn_once(('preset', name), f'unknown caption style {name!r}; known: {sorted(CAPTION_STYLES)}')
            out = dict(L)
            out['style'] = {}
            return out
        return L
    P = caption_style(n)
    out = dict(L)
    st = P.pop('style')
    if isinstance(L.get('style'), dict):
        st = _merge(st, {k: v for k, v in L['style'].items() if k != 'preset'})
    out['style'] = st
    if kind_of(L) not in _CAPTION_KINDS:                # other kinds borrow the look (style) only
        out.pop('preset', None)
        out['_preset'] = n
        return out
    kind = P.pop('kind', None)
    if kind and kind_of(L) in _CAPTION_KINDS and (L.get('words') or kind_of(L) == kind):
        out['kind'] = kind
    for k, v in P.items():
        if k not in L:
            out[k] = v
        elif isinstance(v, dict) and isinstance(L[k], dict):
            out[k] = _merge(v, L[k])
    out.pop('preset', None)
    out['_preset'] = n
    return out


_WARNED = set()


def _warn_once(key, msg):
    if key not in _WARNED:
        _WARNED.add(key)
        import sys
        print(f'[ed_text] {msg}', file=sys.stderr)


# keyword highlight: numbers keep their unit ("4 million", "$10,000", "15 %")
_KW_DIGIT = re.compile(r'\d')
_KW_NUMTOK = re.compile(r'^[+\-−~≈]?[$€£₽¥]?\d[\d\u00a0\u202f.,:]*(?:%|‰|[kmbx×]|bn|st|nd|rd|th|s)?$', re.I)


def _kw_norm(t):
    return re.sub(r'[^\w%$€£₽‰]+', '', str(t).lower())


def keyword_indices(tokens, flags=None, keywords=None, pick='numbers', max_runs=None):
    """Token indices to highlight in one caption chunk: words flagged kw (flags[i]), matches of `keywords` (words or
    phrases, case and punctuation insensitive, phrases match consecutive tokens) and, with pick='numbers', every
    number with the unit glued to it ('4 million', '$10,000', '15 %'). Adjacent highlighted tokens form one run;
    max_runs keeps the first N runs. -> sorted list of indices."""
    n = len(tokens)
    hit = [bool(flags[i]) if flags is not None and i < len(flags) else False for i in range(n)]
    norm = [_kw_norm(t) for t in tokens]
    for kwd in (keywords or []):
        parts = [p for p in (_kw_norm(q) for q in tokenize(kwd)) if p]
        m = len(parts)
        if not m:
            continue
        for i in range(n - m + 1):
            if norm[i:i + m] == parts:
                for j in range(i, i + m):
                    hit[j] = True
    if pick in ('numbers', 'auto'):
        for i, t in enumerate(tokens):
            if _KW_DIGIT.search(t) and _KW_NUMTOK.match(t.strip('.,;:!?»)«("\'')):
                hit[i] = True
                j = i
                while j + 1 < n and (tokens[j + 1].strip('.,;:!?»)').lower() in _UNITS or tokens[j + 1][:1] in '%₽$€‰'
                                     or _DIGIT_GROUP_RE.match(tokens[j + 1])):
                    hit[j + 1] = True
                    j += 1
    idx = [i for i in range(n) if hit[i]]
    if max_runs is not None and idx:
        runs, out = 0, []
        for i in idx:
            if not out or i != out[-1] + 1:
                runs += 1
                if runs > int(max_runs):
                    break
            out.append(i)
        idx = out
    return idx


def _kw_cfg(L):
    hl = L.get('highlight') or {}
    kw = hl.get('keyword') or {}
    words = L.get('keywords') or kw.get('words')
    if isinstance(words, str):
        words = [words]
    return kw, words


# ============================================================================ kinds
LAYER_KINDS = {}
KIND_ALIASES = {'subtitles': 'subtitle', 'captions': 'subtitle', 'margin_notes': 'margin_note', 'notes': 'margin_note',
                'text': 'static', 'texts': 'static', 'route': 'route_map', 'map': 'route_map', 'beat': 'beat_text',
                'title': 'title_card', 'lower': 'lower_third', 'lowerthird': 'lower_third', 'chart': 'counter',
                'infographic': 'counter', 'kinetic_text': 'kinetic', 'text_repeater': 'repeat', 'behind': 'behind_subject'}


def kind_of(L):
    k = str(L.get('kind') or L.get('type') or 'static').strip()
    if k.startswith(('type.', 'gfx.')):
        k = k.split('.', 1)[1]
    return KIND_ALIASES.get(k, k)


def register(cls):
    LAYER_KINDS[cls.name] = cls
    return cls


class Kind:
    name = 'base'
    default_dur = 2.0

    @classmethod
    def span(cls, L, fps, ctx=None):
        return _span(L, fps, cls.default_dur)

    @classmethod
    def plan(cls, L, env):
        return {}

    @classmethod
    def draw(cls, L, env, plan, cv):
        return None

    @classmethod
    def render_scale_for(cls, L):
        return 1.0


def _anims(L, fps, din='cut', dout='cut'):
    return parse_anim(L.get('anim_in', din), din, fps), parse_anim(L.get('anim_out', dout), dout, fps)


def _overshoot(a):
    if not a:
        return 1.0
    t = a.get('type')
    if t in ('pop', 'hit', 'bump', 'slam') and a.get('scale'):
        return min(1.25, max(1.0, max(float(v) for v in a['scale'])))
    if t == 'burst':
        return 1.06
    return 1.0


def _el_origin(el, env, spr, grow=1.0):
    """Clamped output-px origin of an element (cached on the element per sprite)."""
    k = ('o', id(spr.rgba), round(grow, 3))
    if el.get('_ok') != k:
        ox, oy = el['ox'] * env.s, el['oy'] * env.s
        if el.get('clamp', True):
            ox, oy = clamp_origin(ox, oy, spr, env, grow)
        el['_o'], el['_ok'] = (ox, oy), k
    return el['_o']


def _draw_el(cv, env, el, st, **kw):
    """Draw a planned text element {block, ts, ox, oy (canvas)} with state st, clamped into the safe zone."""
    if st is None or st.alpha <= 1e-4:
        return
    base = text_sprite(el['block'], el['ts'], env)          # full block: the clamp must not depend on visible words
    if base is None:
        return
    ox, oy = _el_origin(el, env, base, el.get('grow', 1.0))
    only = kw.get('only')
    if only is not None and len(only) == 1 and kw.get('pivot') is None:
        b = el['block']
        wp = b.words[next(iter(only))]
        kw['pivot'] = (ox + (wp.x + wp.w / 2.0) * env.s, oy + (wp.base - b.cap / 2.0) * env.s)
    draw_text_el(cv, env, el['block'], el['ts'], ox, oy, st, seed=el.get('seed', 7), **kw)


# ---------------------------------------------------------------------------- static
@register
class Static(Kind):
    """Plain text (also the ed_edl `texts` item format). anim_in / anim_out optional (fade, pop, slide…)."""
    name = 'static'

    @classmethod
    def plan(cls, L, env):
        els = []
        if L.get('items'):
            for it in L['items']:
                size_c = env.cH(it.get('size', 64))
                st = {'font': it.get('font', 'sans'), 'color': it.get('color', [235, 235, 235]),
                      'stroke': it.get('stroke'), 'shadow': it.get('shadow'), 'box': it.get('box'),
                      'tracking': _f(it.get('tracking', 0.0)) / max(size_c, 1.0), 'caps': it.get('caps', False)}
                block = layout_words(tokenize(it.get('text', '')), font_of(st), size_c, tracking=st['tracking'],
                                     caps=st['caps'], align='left')
                anchor = str(it.get('anchor', 'lt'))
                ax = {'l': 'left', 'm': 'center', 'r': 'right'}.get(anchor[:1], 'left')
                ay = {'t': 'top', 'a': 'top', 'm': 'center', 's': 'baseline', 'b': 'bottom', 'd': 'bottom'}.get(
                    anchor[1:2], 'top')
                ox, oy = block_origin(block, env.cW(it.get('x', 0)), env.cH(it.get('y', 0)), ax, ay)
                els.append(dict(block=block, ts=resolve_style(st, env, block.size), ox=ox, oy=oy, clamp=False,
                                alpha=float(it.get('opacity', 1.0))))
        else:
            st = style_of(L, {'font': 'inter:700', 'size': 0.05, 'color': '#ffffff', 'line_height': 1.12})
            pos = L.get('pos', [0.47 if env.vertical else 0.5, 0.5])
            x_c, y_c = env.cW(pos[0]), env.cH(pos[1])
            mw = env.cW(L['max_width']) if L.get('max_width') else env.safe_w_center(x_c)
            if st.get('align', 'center') != 'center':
                mw = env.cW(L.get('max_width', 0.8))
            block = make_block(tokenize(L.get('text', '')), st, env, max_width=mw, max_lines=L.get('max_lines'))
            anchor = L.get('anchor', ['center', 'center'])
            ox, oy = block_origin(block, x_c, y_c, anchor[0], anchor[1])
            els.append(dict(block=block, ts=resolve_style(st, env, block.size), ox=ox, oy=oy,
                            clamp=L.get('clamp', True)))
        return {'els': els}

    @classmethod
    def draw(cls, L, env, plan, cv):
        f0, f1 = cls.span(L, env.fps)
        a_in, a_out = _anims(L, env.fps)
        for el in plan['els']:
            el['grow'] = _overshoot(a_in)
            st = element_state(a_in, a_out, env.f, f0, f1, env)
            if st is not None:
                st.alpha *= el.get('alpha', 1.0)
                _draw_el(cv, env, el, st)


# ---------------------------------------------------------------------------- subtitles / karaoke
def _sub_params(L, env, karaoke):
    v = env.vertical
    if karaoke:
        p = dict(max_chars=20 if v else 36, max_lines=2, min_dur=0.0, max_dur=2.5 if v else 4.0, cps_max=20.0,
                 max_words=3 if v else 6, break_on_pause=0.25, lead=-2, tail=env.fr25(5), gap_min=0, join_gap=0.6,
                 split_on_cut=None, ellipsis=False)
    elif L.get('mode') == 'lyric':
        p = dict(max_chars=26 if v else 42, max_lines=2, min_dur=0.36, max_dur=1.7, cps_max=25.0, max_words=4,
                 min_words=2, break_on_pause=0.35, lead=-2, tail=6, gap_min=2, split_on_cut=0.3, ellipsis=True)
    else:
        p = dict(max_chars=26 if v else 42, max_lines=2, min_dur=0.8, max_dur=6.0, cps_max=17.0, max_words=None,
                 break_on_pause=0.6, lead=-2, tail=6, gap_min=2, split_on_cut=0.3, ellipsis=True)
    p.update({k: orient(v, env) for k, v in (L.get('chunk') or {}).items()})
    for k in ('lead', 'tail', 'join_gap', 'gap_min'):
        if k in L:
            p[k] = L[k]
    return p


def _given_breaks(toks):
    """Token positions (into the tokens without '\\n') after which a producer's line break sits."""
    brk, j = [], -1
    for t in toks:
        if t == '\n':
            brk.append(j)
        else:
            j += 1
    return brk


def _fit_caption(toks, st, env, maxw, soft, hard, wsp, n_given, reflow):
    """Lay out one caption chunk -> (block, fits). reflow: at the style's full size (never smaller) on up to `soft`
    lines, else up to `hard` lines (fits False beyond: the caller splits the chunk in time); a glued pair wider than
    the line ("4 million") breaks inside rather than shrink; only one word wider than the line shrinks.
    Without reflow: the old fit (shrink to soft lines). '\\n' tokens are the producer's lines, kept when they fit."""
    plain = [t for t in toks if t != '\n']
    gl = glue_flags(plain)
    split_pair = any(0 <= i < len(gl) and gl[i] for i in _given_breaks(toks))
    want = max(soft, n_given)
    S = size_of(st, env)[0]
    if not reflow:
        block = make_block(toks, st, env, max_width=maxw, max_lines=want, word_spacing=wsp)
        if '\n' in toks and (block.size < 0.97 * S or split_pair):
            # the producer's breaks force a smaller size, or split a glued pair ("at | home", "4 | million"): a
            # balanced free wrap keeps the series' size and the pairs together
            free = make_block(plain, st, env, max_width=maxw, max_lines=want, word_spacing=wsp)
            if free.size > block.size * 1.01 or (split_pair and free.size >= block.size * 0.97
                                                 and len(free.lines) <= want):
                block = free
        return block, True

    def lay(tk, glue=True):
        return make_block(tk, st, env, max_width=maxw, max_lines=want, word_spacing=wsp, min_size=S, glue=glue)

    block = lay(toks)
    if '\n' in toks and (len(block.lines) > n_given or split_pair or block.size < 0.995 * S):
        free = lay(plain)
        if (len(free.lines), -round(free.size, 2)) < (len(block.lines), -round(block.size, 2)) or \
                (split_pair and len(free.lines) <= len(block.lines) and free.size >= block.size * 0.995):
            block = free
    if block.size < 0.995 * S and len(plain) > 1:
        loose = lay(plain, glue=False)
        if loose.size > block.size * 1.005:
            block = loose
    return block, len(block.lines) <= max(hard, n_given)


_SPLIT_END = re.compile(r'[.!?…]["»”)]*$')
_SPLIT_PAUSE = re.compile(r'[,;:—–]["»”)]*$')
_SPLIT_BEFORE = set('and but so or because that which who when where while if then until although though '
                    'и а но или что чтобы потому когда если который которая которые которое где пока хотя'.split())


_PHRASE_COSTS = []          # [ed_voice._phrase_costs or None], looked up once (getattr; ed_text works without it)
_SCALE_WORDS = set('thousand thousands million millions billion billions trillion k m mln bn тыс тысяч тысячи тысяча '
                   'млн миллион миллиона миллионов млрд миллиард миллиарда миллиардов'.split())


def _scale_unit(a, b):
    """'million' + 'dollars': a scale word before its unit (one amount, like a number before its unit)."""
    return (a.strip('.,;:!?»)«("\'').lower() in _SCALE_WORDS and b.strip('.,;:!?»)«("\'').lower() in _UNITS)


def _phrase_cost_fn():
    if not _PHRASE_COSTS:
        fn = None
        try:
            import importlib
            fn = getattr(importlib.import_module('ed_voice'), '_phrase_costs', None)
        except Exception:
            fn = None
        _PHRASE_COSTS.append(fn if callable(fn) else None)
    return _PHRASE_COSTS[0]


def _split_costs(toks, gaps=None, lang=None):
    """[(cost, j)] for every split of a caption chunk into toks[:j] | toks[j:], best first. Cost = character
    imbalance (0..1) + ed_voice._phrase_costs / 1000 for a break after toks[j-1] (sentence end -0.4, clause -0.2, a
    pause up to -0.36 (gaps[k] = s after token k), before a phrase-introducing word -0.1; inside a phrase +0.9..3: an
    article / preposition from its word, a number from its unit, a modifier from its noun) + 1 between a scale word
    and its unit ("4 million | dollars"). Without ed_voice: after a sentence end -0.25 or comma -0.15, before a
    conjunction -0.12 or preposition -0.06, inside a glued run or an amount +1."""
    n = len(toks)
    total = sum(len(t) for t in toks) + n - 1
    bal, left = [], -1
    for j in range(1, n):
        left += len(toks[j - 1]) + 1
        bal.append(abs(left - (total - left - 1)) / max(total, 1))
    fn = _phrase_cost_fn() if n > 1 else None
    if fn is not None:
        try:
            if lang:
                en = str(lang)[:2].lower() == 'en'
            else:                                          # like ed_voice: mostly Cyrillic -> not English
                text = ' '.join(toks)
                en = sum(1 for ch in text if '\u0400' <= ch <= '\u04ff') <= 0.3 * len(text)
            pc = fn(list(toks), list(gaps) if gaps is not None else None, en=en)
            if len(pc) >= n - 1:
                return sorted((bal[j - 1] + float(pc[j - 1]) / 1000.0 + (1.0 if _scale_unit(toks[j - 1], toks[j]) else 0.0),
                               j) for j in range(1, n))
        except Exception as e:                             # an incompatible ed_voice: the built-in rule
            _warn_once(('phrase_costs', type(e).__name__), f'ed_voice._phrase_costs failed ({e}); built-in split rule')
    gl = glue_flags(toks)
    out = []
    for j in range(1, n):
        cost = bal[j - 1]
        if _SPLIT_END.search(toks[j - 1]):
            cost -= 0.25
        elif _SPLIT_PAUSE.search(toks[j - 1]):
            cost -= 0.15
        elif toks[j].strip('«»"\'(').lower() in _SPLIT_BEFORE:
            cost -= 0.12
        elif toks[j].strip('«»"\'(').lower() in _ORPHANS:            # before a preposition / article
            cost -= 0.06
        if gl[j - 1] or _scale_unit(toks[j - 1], toks[j]):
            cost += 1.0
        out.append((cost, j))
    return sorted(out)


def _split_point(toks, gaps=None, lang=None):
    """Best token index j (1..n-1) to split a caption chunk (see _split_costs); None for a single token."""
    c = _split_costs(toks, gaps, lang)
    return c[0][1] if c else None


def _split_frame(c, j, words, fps, lead):
    """Frame where the second part of chunk c split before token j starts: its first word's start + lead, or
    (no word timing) the share of the characters before the split."""
    toks = [t for t in c['tokens'] if t != '\n']
    f0, f1 = int(c['f0']), int(c['f1'])
    i0, i1 = c.get('i0', 0), c.get('i1', -1)
    if i1 >= i0 and words and i1 < len(words) and i1 - i0 + 1 == len(toks):
        return int(round(words[i0 + j]['t0'] * fps)) + int(lead), True
    a, b = len(' '.join(toks[:j])), len(' '.join(toks[j:]))
    return f0 + int(round((f1 - f0 + 1) * a / max(a + b, 1))), False


def _split_chunk(c, words, fps, lead, min_part, min_show=0, lang=None):
    """Chunk c split in two -> ([first, second], readable) with its time span divided at the second part's first
    word (or by characters); the split point is the best-ranked one (_split_costs) whose parts both last min_show
    frames (readable True), else the best one; each part keeps at least min_part frames. (None, False) when it cannot
    be split."""
    toks = [t for t in c['tokens'] if t != '\n']
    f0, f1 = int(c['f0']), int(c['f1'])
    if len(toks) < 2 or f1 - f0 + 1 < 2:
        return None, False
    m = max(1, min(int(min_part), (f1 - f0 + 1) // 2))
    best, readable = None, False
    i0, i1 = c.get('i0', 0), c.get('i1', -1)
    gaps = None
    if i1 >= i0 and words and i1 < len(words) and i1 - i0 + 1 == len(toks):      # pauses between the words (s)
        gaps = [words[i0 + q + 1]['t0'] - words[i0 + q]['t1'] for q in range(len(toks) - 1)] + [None]
    for _cost, j in _split_costs(toks, gaps, lang):
        fs, timed = _split_frame(c, j, words, fps, lead)
        fs = min(max(fs, f0 + m), f1 - m + 1)
        if best is None:
            best = (j, fs, timed)
        if _cost < 0.9 and fs - f0 >= min_show and f1 - fs + 1 >= min_show:
            best, readable = (j, fs, timed), True
            break
    j, fs, timed = best
    c1 = dict(c, f1=fs - 1, tokens=toks[:j], text=' '.join(toks[:j]), part=True)
    c2 = dict(c, f0=fs, tokens=toks[j:], text=' '.join(toks[j:]), part=True)
    if timed:
        c1['i1'], c2['i0'] = i0 + j - 1, i0 + j
    for d in (c1, c2):
        d.pop('warn', None)
    return [c1, c2], readable


_ONE_CHUNK = dict(max_chars=999, max_dur=1e9, max_words=None, break_on_pause=1e9, min_dur=0, cps_max=0, gap_min=0,
                  join_gap=None, split_on_cut=None, punct_break=False)


def split_caption_layer(L, ow=1080, oh=1920, fps=30.0, ctx=None):
    """A subtitle / karaoke layer -> the layers it is shown as at the full preset size: [L] unchanged when every
    chunk fits (chunk.max_lines lines, or re-flowed up to the layer's max_lines), else one layer per displayed chunk,
    the long chunk split in time at a word boundary (the second part starts at its first word), each with its own
    f0 / f1 / t0 / t1, text, lines and words (single-chunk params) - for producers that emit one layer per chunk
    (ed_voice.subtitle_chunks) and want the split explicit. Parts tile the layer's own [f0, f1] (a stale lead / tail
    never moves a part outside it). The renderer splits the same way on its own; text never shrinks below the preset
    size. Other kinds and fit='shrink' layers pass unchanged."""
    if not isinstance(L, dict):
        return [L]
    R = resolve_preset(L)
    kind = kind_of(R)
    if kind not in _CAPTION_KINDS or str(R.get('fit', 'reflow')).lower() == 'shrink':
        return [L]
    fps = float(fps or 30.0)
    env = Env(R, 0, fps, ow, oh, 1.0, ctx or {})
    plan = LAYER_KINDS[kind].plan(R, env)
    if not plan.get('split'):
        return [L]
    lo, hi = LAYER_KINDS[kind].span(R, fps, ctx)          # every part stays inside the layer's own frames
    words = plan['words']
    out = []
    for el in plan['chunks']:
        c = el['chunk']
        toks = [t for t in c['tokens'] if t != '\n']
        f0, f1 = max(int(el['f0']), int(lo)), min(int(el['f1']), int(hi))
        if f1 < f0:
            continue
        P = {k: v for k, v in L.items() if k not in ('chunks', 'warn', 'lines', 'cps')}
        P.update(f0=f0, f1=f1, t0=round(f0 / fps, 3), t1=round((f1 + 1) / fps, 3), text=' '.join(toks))
        blk = el['block']
        if len(blk.words) == len(toks):
            P['lines'] = [' '.join(toks[a:b + 1]) for (_x, _w, _y, a, b) in blk.lines]
        i0, i1 = c.get('i0', 0), c.get('i1', -1)
        if i1 >= i0 and words:
            ws = words[i0:i1 + 1]
            P['words'] = [dict(w=w['w'], t0=round(w['t0'], 3), t1=round(w['t1'], 3), **({'kw': True} if w['kw'] else {}))
                          for w in ws]
            P['lead'] = f0 - int(round(ws[0]['t0'] * fps))
            P['tail'] = f1 - int(round(ws[-1]['t1'] * fps))
            P['chunk'] = dict(R.get('chunk') or {}, **_ONE_CHUNK)
        else:
            P.pop('words', None)
            P['chunks'] = [dict(text=' '.join(toks), f0=f0, f1=f1)]
        if 'cps' in L:
            P['cps'] = round(len(P['text']) / max((f1 - f0 + 1) / fps, 1e-6), 1)
        out.append(P)
    return out


def fit_caption_layers(layers, ow=1080, oh=1920, fps=30.0, ctx=None):
    """split_caption_layer over a list of layers (flat list, order kept)."""
    out = []
    for L in layers or []:
        out.extend(split_caption_layer(L, ow, oh, fps, ctx))
    return out


@register
class Subtitle(Kind):
    """type.subtitles — chunks from word timestamps, 1–2 lines, cut in/out (or fade), face avoidance."""
    name = 'subtitle'
    karaoke = False

    @classmethod
    def span(cls, L, fps, ctx=None):
        if L.get('f0') is not None and L.get('f1') is not None:
            return int(L['f0']), int(L['f1'])
        t0, t1 = _words_minmax(L.get('words') or (ctx or {}).get('words'))
        for c in L.get('chunks') or []:
            if c.get('t0') is not None:
                t0 = min(t0, float(c['t0']))
                t1 = max(t1, float(c.get('t1', c['t0'])))
            elif c.get('f0') is not None:
                t0 = min(t0, float(c['f0']) / fps)
                t1 = max(t1, float(c.get('f1', c['f0'])) / fps)
        if t0 > t1:
            return _span(L, fps, 2.0)
        return (int(L.get('f0', math.floor(t0 * fps) - 4)), int(L.get('f1', math.ceil(t1 * fps + 7.0 * fps))))

    @classmethod
    def defaults(cls, L, env):
        v = env.vertical
        if L.get('mode') == 'lyric':
            return {'font': 'grotesk_semibold', 'size': 0.03 if v else 0.032, 'color': '#e0d79c', 'stroke': None,
                    'shadow': {'dy': 0.04, 'blur': 0.1, 'alpha': 0.55}, 'line_height': 1.18}
        return {'font': 'inter:700', 'size': 0.04 if v else 0.05, 'color': '#ffffff',
                'stroke': {'w_h': 0.0032, 'color': '#000000'}, 'line_height': 1.16}

    @classmethod
    def layout_geom(cls, L, env, st=None):
        """Placement and wrap width of the chunks (canvas px): {st, pos, x_c, maxw (the width the decorated text may
        take: max_width, the safe zone divided by the entrance overshoot, a plate's padding), wsp, mode, grow}."""
        st = style_of(L, cls.defaults(L, env)) if st is None else st
        v = env.vertical
        lyric = L.get('mode') == 'lyric'
        pos = L.get('pos')
        if pos is None:
            if cls.karaoke:
                pos = {'x': 0.47, 'center_y': 0.67} if v else {'x': 0.5, 'center_y': 0.86}
            elif lyric:
                pos = {'x': 0.47 if v else 0.5, 'center_y': 0.52}
            else:
                pos = {'x': 0.47, 'block': [0.62, 0.78]} if v else {'x': 0.5, 'baseline': 0.93}
        if isinstance(pos, (list, tuple)):
            pos = {'x': pos[0], 'center_y': pos[1]}
        pos = {k: orient(q, env) for k, q in pos.items()}
        if pos.get('x') == 'auto':
            pos['x'] = 0.47 if v else 0.5
        x_c = env.cW(pos.get('x', 0.5))
        mw_l = orient(L.get('max_width'), env)
        maxw = env.cW(mw_l) if mw_l else env.W * (0.76 if (cls.karaoke and v) else 0.86)
        zone_w = max(env.safe_w_center(x_c), 0.25 * env.W)
        hl = L.get('highlight') or {}
        mode = hl.get('mode', 'color') if cls.karaoke else None
        wsp = 0.1 if mode == 'bounce' else 0.0
        if mode == 'box':
            # the settled plate never touches a neighbour: word gap >= side pad + 0.08 em, line pitch clears the
            # plate by 0.1 em, and the plate of an edge word stays inside the zone
            pad = (hl.get('box') or {}).get('pad', [0.28, 0.12])
            m = font_metrics(font_of(st))
            wsp = max(0.0, float(pad[0]) + 0.08 - m['space'])
            if 'line_height' not in L and 'line_height' not in (L.get('style') or {}):
                st['line_height'] = max(float(st.get('line_height', 1.1)), m['cap'] + m['desc'] + float(pad[1]) + 0.1)
            zone_w = max(zone_w * 0.5, zone_w - 2.0 * float(pad[0]) * size_of(st, env)[0])
        grow = _overshoot(_anims(L, env.fps)[0])          # the pop-in peak scale must fit the zone too
        maxw = min(maxw, zone_w / grow)
        if mode == 'bounce':
            maxw /= float((hl.get('bounce') or {}).get('scale', 1.12))
        return dict(st=st, pos=pos, x_c=x_c, maxw=maxw, wsp=wsp, mode=mode, grow=grow)

    @classmethod
    def plan(cls, L, env):
        p = _sub_params(L, env, cls.karaoke)
        words = norm_words(L.get('words') or env.ctx.get('words'))
        if L.get('f0') is not None and L.get('f1') is not None and not L.get('words'):
            words = [w for w in words if L['f0'] <= w['t0'] * env.fps <= L['f1']]
        if L.get('chunks'):
            chunks = []
            for c in L['chunks']:
                f0 = c.get('f0', int(round(_f(c.get('t0')) * env.fps)) + int(p.get('lead', -2)))
                f1 = c.get('f1', int(round(_f(c.get('t1')) * env.fps)) + int(p.get('tail', 6)))
                toks = tokenize(c.get('text', ''))
                chunks.append({'f0': int(f0), 'f1': int(f1), 'tokens': toks, 'text': ' '.join(toks), 'i0': 0,
                               'i1': -1, 'words': c.get('words')})
            chunks.sort(key=lambda c: c['f0'])
            for a, b in zip(chunks, chunks[1:]):
                a['f1'] = min(a['f1'], b['f0'] - 1)
        else:
            chunks = chunk_words(words, env.fps, cuts=env.ctx.get('cuts'), **p)
        if L.get('f0') is not None and L.get('f1') is not None:
            # the layer's own frames bound every chunk (a stale tail / lead after pacing or a jump cut must not move
            # a chunk - or a part split from it - outside them)
            lo, hi = int(L['f0']), int(L['f1'])
            chunks = [dict(c, f0=max(int(c['f0']), lo), f1=min(int(c['f1']), hi)) for c in chunks]
            chunks = [c for c in chunks if c['f1'] >= c['f0']]
        geom = cls.layout_geom(L, env)
        st, pos, x_c, maxw, wsp = geom['st'], geom['pos'], geom['x_c'], geom['maxw'], geom['wsp']
        avoid = L.get('avoid', 'face')
        step = 0.02 * env.H
        out = []
        given = L.get('lines') if (isinstance(L.get('lines'), list) and len(chunks) == 1) else None
        kwc, kw_words = _kw_cfg(L)
        use_kw = bool(kwc or kw_words)
        kw_glob = set(int(i) for i in kwc.get('indices', []))
        # fit: 'reflow' (default) keeps the style's size - a chunk that does not fit chunk.max_lines lines wraps to
        # more lines (up to the layer's max_lines), then splits its time span in two at a word boundary; only a
        # single word wider than the line shrinks. 'shrink' = the old behaviour (smaller text, chunk.max_lines).
        reflow = str(L.get('fit', 'reflow')).lower() != 'shrink' and size_of(st, env)[1] is None
        soft = int(p.get('max_lines', 2) or 2)
        hard = orient(L.get('max_lines'), env)
        hard = max(soft, int(hard) if hard else (2 if cls.karaoke else 3))
        min_part = max(1, int(round(0.25 * env.fps)))
        ms = p.get('min_show')
        min_show = max(1, int(round((0.7 if ms is None else float(ms)) * env.fps)))
        queue, fitted, n_split = [dict(c) for c in chunks], [], 0
        while queue:
            c = queue.pop(0)
            toks = c['tokens']
            gv = None
            if given and not n_split and ' '.join(tokenize(' '.join(given))) == ' '.join(toks):
                gv = given
                toks = []
                for li, ln in enumerate(given):
                    toks += tokenize(ln) + (['\n'] if li < len(given) - 1 else [])
            block, ok = _fit_caption(toks, st, env, maxw, soft, hard, wsp, len(gv or []), reflow)
            if not ok and n_split < 64:
                parts, readable = _split_chunk(c, words, env.fps, int(p.get('lead', -2)), min_part, min_show,
                                               L.get('lang'))
                if not readable and len(block.lines) <= hard + 1:
                    parts = None        # no split leaves two parts of >= min_show s: one more line instead
                if parts:
                    queue[0:0] = parts
                    n_split += 1
                    continue
            fitted.append((c, toks, block))
        for c, toks, block in fitted:
            kw = []
            if use_kw:
                flags = None
                if c.get('i1', -1) >= c.get('i0', 0) and words:
                    flags = [bool(words[i]['kw']) or i in kw_glob for i in range(c['i0'], c['i1'] + 1)
                             if i < len(words)]
                kw = keyword_indices([t for t in toks if t != '\n'], flags, kw_words, kwc.get('pick', 'none'),
                                     kwc.get('max_per_chunk', 1 if cls.karaoke else None))
            if 'block' in pos:
                y_c, ay = env.cH((pos['block'][0] + pos['block'][1]) / 2.0), 'center'
            elif 'baseline' in pos:
                y_c, ay = env.cH(pos['baseline']), 'last_baseline'
            else:
                y_c, ay = env.cH(pos.get('center_y', pos.get('y', 0.5))), 'center'
            ox, oy = block_origin(block, x_c, y_c, 'center', ay)
            if avoid and avoid != 'none':
                boxes = []
                for ff in sorted({c['f0'], (c['f0'] + c['f1']) // 2, c['f1']}):
                    boxes += faces_at(env, ff)
                rect = (ox, oy - 0.1 * block.size, ox + block.width, oy + block.height + 0.1 * block.size)
                keep = None
                if boxes and _hit(rect, boxes, 0.01 * env.H):
                    # the drawn ink (outline, shadow) at the entrance's peak scale must stay in the zone
                    tb = _tight(text_sprite(block, resolve_style(st, env, block.size), env) or Sprite(
                        np.zeros((1, 1, 4), np.float32)))
                    keep = (oy + tb[1] / env.s, oy + tb[3] / env.s) if tb else None
                oy += avoid_dy(rect, boxes, env, step, 0.01 * env.H, prefer=1, keep=keep, grow=geom['grow'])
            el = dict(block=block, ts=resolve_style(st, env, block.size), ox=ox, oy=oy, f0=c['f0'], f1=c['f1'],
                      i0=c.get('i0', 0), i1=c.get('i1', -1), chunk=c, kw=[j for j in kw if j < len(block.words)])
            out.append(el)
        return {'chunks': out, 'f0s': [c['f0'] for c in out], 'words': words, 'p': p, 'st': st,
                'kw_col': to_rgba(kwc.get('color', '#ffd21f')), 'split': n_split}

    @classmethod
    def _active(cls, plan, f):
        import bisect
        i = bisect.bisect_right(plan['f0s'], f) - 1
        if i < 0:
            return None
        c = plan['chunks'][i]
        return c if c['f0'] <= f <= c['f1'] else None

    @classmethod
    def draw(cls, L, env, plan, cv):
        c = cls._active(plan, env.f)
        if c is None:
            return
        a_in, a_out = _anims(L, env.fps)
        st = element_state(a_in, a_out, env.f, c['f0'], c['f1'], env)
        c['grow'] = _overshoot(a_in)
        cols = {j: plan['kw_col'] for j in c.get('kw') or ()} or None
        _draw_el(cv, env, c, st, cols=cols)


def _plate_text(block, ts, env, cols, alphas, tcol, R, r, decor):
    """Karaoke box text: tcol where the plate covers it, its own colour elsewhere (a premultiplied blend by the plate
    coverage), so the sliding plate never leaves a dark word on the background. R = plate rect, block-local px."""
    key = ('kbox', block.key, ts.key, env.s, tuple(sorted(cols.items())) if cols else None,
           None if alphas is None else tuple(sorted(alphas.items())), tuple(int(round(v)) for v in R), round(r, 1),
           tuple(tcol), decor)
    spr = _SPRITES.get(key)
    if spr is not None:
        return spr
    W = text_sprite(block, ts, env, cols or None, alphas, None, decor)
    # on the plate: plain text colour, no stroke / shadow / glow (decor 0 keeps the sprite geometry identical)
    B = text_sprite(block, ts, env, {j: tcol for j in range(len(block.words))}, alphas, None, 0.0)
    if W is None or B is None or W.rgba.shape != B.rgba.shape or (W.x, W.y) != (B.x, B.y):
        return W
    M = np.zeros(W.rgba.shape[:2], np.float32)
    reg, mm = _clip_paste(M, round_rect_mask(R[2] - R[0], R[3] - R[1], r), int(round(R[0] - W.x)),
                          int(round(R[1] - W.y)))
    if reg is None:
        return W
    reg[...] = mm
    out = W.rgba + (B.rgba - W.rgba) * M[..., None]
    spr = Sprite(out, W.x, W.y)
    _SPRITES.put(key, spr, out.nbytes)
    return spr


@register
class Karaoke(Subtitle):
    """type.karaoke — the chunk stands still, the sounding word is highlighted (colour, sliding box, bounce,
    left-to-right fill for songs, or ghost)."""
    name = 'karaoke'
    karaoke = True

    @classmethod
    def defaults(cls, L, env):
        hl = (L.get('highlight') or {}).get('mode', 'color')
        st = {'font': 'inter:800', 'size': 0.046 if env.vertical else 0.06, 'color': '#ffffff',
              'stroke': {'w': 0.1, 'color': '#000000'}, 'line_height': 1.1}
        if hl == 'box':
            st['stroke'] = None
        return st

    @classmethod
    def plan(cls, L, env):
        plan = super().plan(L, env)
        hl = dict(L.get('highlight') or {})
        words = plan['words']
        fps = env.fps
        lead = int(L.get('switch_lead', -1))
        min_on = int(L.get('min_on', env.fr25(3)))
        kw, kw_words = _kw_cfg(L)
        kw_idx = set(int(i) for i in kw.get('indices', []))
        for c in plan['chunks']:
            if c['i1'] < c['i0']:
                c['sw'] = []
                continue
            sw = [int(round(words[i]['t0'] * fps)) + lead for i in range(c['i0'], c['i1'] + 1)]
            for j in range(1, len(sw)):
                if sw[j] - sw[j - 1] < min_on:
                    sw[j] = max(sw[j], min(sw[j - 1] + min_on, sw[j] + 2))
            c['sw'] = sw
            toks = [t for t in (c['chunk'].get('tokens') or [w.text for w in c['block'].words]) if t != '\n']
            flags = [bool(words[i]['kw']) or i in kw_idx for i in range(c['i0'], c['i1'] + 1)]
            c['kw'] = keyword_indices(toks, flags, kw_words, kw.get('pick', 'none'), kw.get('max_per_chunk', 1))
        plan['hl'] = hl
        return plan

    @classmethod
    def draw(cls, L, env, plan, cv):
        c = cls._active(plan, env.f)
        if c is None:
            return
        f = env.f
        hl = plan['hl']
        mode = hl.get('mode', 'color')
        a_in, a_out = _anims(L, env.fps)
        st = element_state(a_in, a_out, f, c['f0'], c['f1'], env)
        if st is None:
            return
        c['grow'] = max(_overshoot(a_in), float((hl.get('bounce') or {}).get('scale', 1.12)) if mode == 'bounce' else 1.0)
        sw = c.get('sw') or []
        act = -1
        for j, s0 in enumerate(sw):
            if s0 <= f:
                act = j
        nw = len(c['block'].words)
        active_col = to_rgba(hl.get('active', '#ffe14a'))
        kw_col = to_rgba((hl.get('keyword') or {}).get('color', '#45f06b'))
        progressive = bool(hl.get('progressive', False))
        cols, alphas, fills = {}, None, None
        for j in range(nw):
            if j in c.get('kw', []) and j <= act:
                cols[j] = kw_col
            elif j == act or (progressive and j < act):
                cols[j] = active_col
        if mode == 'ghost':
            alphas = {j: (1.0 if j <= act else float(hl.get('upcoming_alpha', 0.45))) for j in range(nw)}
            if not hl.get('active'):
                cols = {j: v for j, v in cols.items() if j in c.get('kw', [])}
        base = text_sprite(c['block'], c['ts'], env)
        if base is None:
            return
        ox, oy = _el_origin(c, env, base, c['grow'])
        block, s = c['block'], env.s
        if mode == 'box' and act >= 0:
            bx = dict(hl.get('box') or {})
            pad = bx.get('pad', [0.28, 0.12])
            r = float(bx.get('radius', 0.22)) * block.size * s

            def rect(j):
                wp = block.words[j]
                return np.array([wp.x * s - pad[0] * block.size * s, (wp.base - block.cap) * s - pad[1] * block.size * s,
                                 (wp.x + wp.w) * s + pad[0] * block.size * s,
                                 (wp.base + block.desc) * s + pad[1] * block.size * s])
            R = rect(act)
            nsl = env.fr25(3)
            if act > 0 and f - sw[act] < nsl:
                u = ease((f - sw[act] + 1) / float(nsl), bx.get('ease', 'outCubic'))
                R = rect(act - 1) + (R - rect(act - 1)) * u
            m = round_rect_mask(R[2] - R[0], R[3] - R[1], r)
            plate = colored_sprite(m, to_rgba(bx.get('fill', hl.get('active', '#ffe14a'))), R[0], R[1])
            tb = _tight(base)                 # plate and text turn about the same pivot as draw_text_el uses
            piv = (ox + block.width * s / 2.0, oy + ((tb[1] + tb[3]) / 2.0 if tb else block.height * s / 2.0))
            cv.place(plate, ox, oy, st, piv)
            cols = {j: v for j, v in cols.items() if j != act and j in c.get('kw', [])}
            tcol = to_rgba(bx.get('text', '#000000'))
            if st.chars is None and st.reveal is None and not st.wipe and not st.tint:
                cv.place(_plate_text(block, c['ts'], env, cols, alphas, tcol, R, r, round(st.decor, 1)), ox, oy, st, piv)
                return
            cols[act] = tcol
        if mode == 'fill':
            fills = {}
            words = plan['words']
            for j in range(nw):
                wi = c['i0'] + j
                if wi >= len(words):
                    break
                w = words[wi]
                prog = _clamp((env.t - w['t0']) / max(0.05, w['t1'] - w['t0']), 0.0, 1.0)
                prog = round(prog * 48) / 48.0
                if prog > 0:
                    fills[j] = (prog, active_col, 0.08 * block.size * s)
            cols = {j: v for j, v in cols.items() if j in c.get('kw', [])}
        if mode == 'bounce' and act >= 0:
            bo = dict(hl.get('bounce') or {})
            grow_f, back_f = env.fr25(bo.get('grow', 3)), env.fr25(bo.get('back', 4))
            k = f - sw[act]
            S = float(bo.get('scale', 1.12))
            if k < grow_f:
                sc = 1 + (S - 1) * ease((k + 1) / grow_f, 'outQuad')
            else:
                sc = S + (1 - S) * ease(min(1.0, (k - grow_f + 1) / back_f), 'outBack')
            others = set(range(nw)) - {act}
            draw_text_el(cv, env, block, c['ts'], ox, oy, st, cols=cols, alphas=alphas, only=others)
            wp = block.words[act]
            st2 = St().compose(st)
            st2.sx *= sc
            st2.sy *= sc
            piv = (ox + (wp.x + wp.w / 2) * s, oy + (wp.base - block.cap / 2) * s)
            if abs(sc - 1) < 1e-3 and abs(st.sx - 1) < 1e-3:
                piv = None
            draw_text_el(cv, env, block, c['ts'], ox, oy, st2, cols=cols, alphas=alphas, only={act}, pivot=piv)
            return
        draw_text_el(cv, env, block, c['ts'], ox, oy, st, cols=cols or None, alphas=alphas, fills=fills)


# ---------------------------------------------------------------------------- kinetic typography
def _text_words(L, env, per=0.4):
    """Timed words from layer words / ctx words, or from layer text spread from t0/f0 every `per` seconds."""
    ws = norm_words(L.get('words'))
    if not ws and L.get('text'):
        toks = tokenize(L['text'])
        t0 = _f(L.get('t0'), (L.get('f0') or 0) / env.fps)
        per = float(L.get('per', per))
        ws = [{'w': t, 't0': t0 + i * per, 't1': t0 + (i + 1) * per - 0.02, 'kw': False} for i, t in enumerate(toks)]
    if not ws:
        ws = norm_words(env.ctx.get('words'))
        if L.get('f0') is not None and L.get('f1') is not None:
            ws = [w for w in ws if L['f0'] <= w['t0'] * env.fps <= L['f1']]
    return ws


@register
class Kinetic(Kind):
    """type.kinetic — words on their timestamps, 1–3 per screen (word | phrase | cascade | decode | strobe | countdown)."""
    name = 'kinetic'

    @classmethod
    def span(cls, L, fps, ctx=None):
        if L.get('f0') is not None and L.get('f1') is not None:
            return int(L['f0']), int(L['f1'])
        mode = L.get('mode', 'word')
        if mode == 'countdown':
            cd = L.get('countdown') or {}
            f0 = _span(L, fps)[0]
            return f0, f0 + int(round(len(cd.get('digits', [3, 2, 1])) * float(cd.get('per', 0.35)) * fps)) - 1
        t0, t1 = _words_minmax(L.get('words'))
        if t0 > t1 and L.get('text'):
            t0 = _f(L.get('t0'), (L.get('f0') or 0) / fps)
            t1 = t0 + len(tokenize(L['text'])) * float(L.get('per', 0.4))
        if t0 > t1:
            t0, t1 = _words_minmax((ctx or {}).get('words'))
        if t0 > t1:
            return _span(L, fps)
        return (int(L.get('f0', math.floor(t0 * fps) - 3)), int(L.get('f1', math.ceil(t1 * fps + 1.2 * fps))))

    @classmethod
    def defaults(cls, L, env):
        mode = L.get('mode', 'word')
        v = env.vertical
        if mode == 'phrase':
            return {'font': 'inter:800', 'size': 0.06 if v else 0.11, 'color': '#ffffff', 'line_height': 1.1}
        if mode == 'decode':
            return {'font': 'mono_caps', 'caps': True, 'size': {'fit_width': 0.8, 'max': 0.07 if v else 0.1},
                    'color': '#ffffff'}
        if mode == 'strobe':
            return {'font': 'grotesk_condensed_black', 'caps': True, 'size': {'fit_width': 0.74, 'max': 0.3 if v else 0.34},
                    'gradient': ['#ffe600', '#ff7d00', '#ff1e3c'], 'tracking': -0.01}
        if mode == 'countdown':
            return {'font': 'grotesk_condensed_black', 'color': '#ffffff'}
        return {'font': 'grotesk_bold_rounded', 'size': {'fit_width': 0.8, 'max': 0.14 if v else 0.35,
                                                         'min': 0.035 if v else 0.06},
                'color': '#ffffff', 'stroke': {'w': 0.05, 'color': '#000000', 'grow': 3}, 'line_height': 1.0}

    @classmethod
    def plan(cls, L, env):
        mode = L.get('mode', 'word')
        st = style_of(L, cls.defaults(L, env))
        v = env.vertical
        pos = L.get('pos', [0.47 if v else 0.5, 0.48])
        x_c, y_c = env.cW(pos[0]), env.cH(pos[1])
        fps = env.fps
        din0 = {'cascade': 'cascade', 'decode': 'decode', 'phrase': 'slide'}.get(mode, 'pop')
        maxw = min(env.safe_w_center(x_c), env.W * 0.92) / _overshoot(parse_anim(L.get('anim_in', din0), din0, fps))
        f0L, f1L = cls.span(L, fps, env.ctx)
        if mode == 'countdown':
            return cls._plan_countdown(L, env, st, x_c, y_c, f0L)
        ws = _text_words(L, env)
        lead = int(L.get('lead', -1))
        if mode == 'strobe':
            return cls._plan_strobe(L, env, st, ws, x_c, y_c, f0L, f1L, maxw)
        if mode == 'phrase':
            return cls._plan_phrase(L, env, st, ws, x_c, y_c, f0L, f1L, maxw, lead)
        group = max(1, int(L.get('group', 1)))
        min_hold = float(L.get('min_hold', 0.3))
        max_gap = float(L.get('max_gap', 0.7))
        tail = float(L.get('tail', 0.25))
        groups, i = [], 0
        while i < len(ws):
            g = [i]
            while len(g) < group and g[-1] + 1 < len(ws):
                g.append(g[-1] + 1)
            # too short to read: take the next word along (max 3 words)
            while (len(g) < 3 and g[-1] + 1 < len(ws) and ws[g[-1] + 1]['t0'] - ws[g[0]]['t0'] < min_hold
                   and L.get('auto_group', True)):
                g.append(g[-1] + 1)
            groups.append(g)
            i = g[-1] + 1
        # one size for the series (move card): the longest single word fits the width; groups of 2–3 words stack
        s0 = None
        if groups and isinstance(st.get('size'), dict) and L.get('same_size', True):
            uniq = sorted({ws[k]['w'] for g in groups for k in g})
            s0 = min(make_block([w], st, env, max_width=maxw, max_lines=1, glue=False).size for w in uniq)
        blocks = [make_block([ws[k]['w'] for k in g], st, env, max_width=maxw, max_lines=len(g), size=s0, glue=False)
                  for g in groups]
        els = []
        for gi, (g, b) in enumerate(zip(groups, blocks)):
            fa = int(round(ws[g[0]]['t0'] * fps)) + lead
            end = int(round(ws[g[-1]]['t1'] * fps + tail * fps))
            nxt = int(round(ws[groups[gi + 1][0]]['t0'] * fps)) + lead if gi + 1 < len(groups) else None
            if nxt is not None and (ws[groups[gi + 1][0]]['t0'] - ws[g[-1]]['t1']) <= max_gap:
                fb = nxt - 1
            else:
                fb = end if nxt is None else min(end, nxt - 1)
            fb = max(fb, fa + int(math.ceil(min_hold * fps)) - 1)
            if nxt is not None:
                fb = min(fb, nxt - 1)
            fb = min(fb, f1L)
            ox, oy = block_origin(b, x_c, y_c)
            els.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=ox, oy=oy, fa=max(fa, f0L), fb=fb,
                            seed=env.seed + gi))
        din = {'cascade': 'cascade', 'decode': 'decode'}.get(mode, 'pop')
        a_in, a_out = _anims(L, fps, din, 'cut')
        for el in els:
            el['grow'] = _overshoot(a_in)
            if a_in.get('type') == 'cascade':
                # the whole word must land within ~45 % of its time on screen (12–60 letters/s in the card)
                hold = (el['fb'] - el['fa'] + 1) / fps
                n_ch = max(1, sum(len(w.text) for w in el['block'].words))
                el['in'] = dict(a_in, per_letter=min(a_in.get('per_letter', 0.06), 0.45 * hold / n_ch),
                                settle=min(a_in.get('settle', 0.16), 0.3 * hold))
        return {'els': els, 'in': a_in, 'out': a_out}

    @classmethod
    def _plan_phrase(cls, L, env, st, ws, x_c, y_c, f0L, f1L, maxw, lead):
        fps = env.fps
        max_words = int(L.get('max_words', 6))
        phrases, cur = [], []
        for i, w in enumerate(ws):
            if cur and (len(cur) >= max_words or w['t0'] - ws[cur[-1]]['t1'] > float(L.get('max_gap', 0.6)) or
                        re.search(r'[.!?…]$', ws[cur[-1]]['w'])):
                phrases.append(cur)
                cur = []
            cur.append(i)
        if cur:
            phrases.append(cur)
        els = []
        for pi, ph in enumerate(phrases):
            b = make_block([ws[k]['w'] for k in ph], st, env, max_width=maxw, max_lines=int(L.get('max_lines', 3)))
            fa = int(round(ws[ph[0]]['t0'] * fps)) + lead
            nxt = int(round(ws[phrases[pi + 1][0]]['t0'] * fps)) + lead if pi + 1 < len(phrases) else None
            fb = int(round(ws[ph[-1]]['t1'] * fps + float(L.get('tail', 0.5)) * fps))
            if nxt is not None:
                fb = min(fb, nxt - 1) if ws[phrases[pi + 1][0]]['t0'] - ws[ph[-1]]['t1'] > 0.6 else nxt - 1
            ox, oy = block_origin(b, x_c, y_c)
            wf = [int(round(ws[k]['t0'] * fps)) + lead for k in ph]
            els.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=ox, oy=oy, fa=max(fa, f0L),
                            fb=min(fb, f1L), wf=wf))
        a_in = parse_anim(L.get('anim_in', 'slide'), 'slide', fps)
        a_out = parse_anim(L.get('anim_out', 'cut'), 'cut', fps)
        return {'els': els, 'in': a_in, 'out': a_out, 'phrase': True}

    @classmethod
    def _plan_strobe(cls, L, env, st, ws, x_c, y_c, f0L, f1L, maxw):
        sp = dict(L.get('strobe') or {})
        per = max(1, int(sp.get('per', 1)))
        bands = sp.get('bands', ['top', 'mid', 'bottom'])
        sx0, sy0, sx1, sy1 = env.safe_c
        ys = {'top': sy0 + (sy1 - sy0) * 0.2, 'mid': (sy0 + sy1) / 2, 'bottom': sy0 + (sy1 - sy0) * 0.8}
        toks = [w['w'] for w in ws] or tokenize(L.get('text', 'STROBE'))
        blocks = [make_block([t], st, env, max_width=maxw, max_lines=1) for t in toks]
        n = f1L - f0L + 1
        want = []
        for k in range(n):
            j = k // per
            want.append((j % len(blocks), j % len(bands)))
        smear = env.o(env.cW(sp.get('smear', 0.02)))
        ts_list = [resolve_style(st, env, b.size) for b in blocks]
        els = {}
        for bi, b in enumerate(blocks):
            for band_i, band in enumerate(bands):
                ox, oy = block_origin(b, x_c, ys.get(band, (sy0 + sy1) / 2))
                els[(bi, band_i)] = dict(block=b, ts=ts_list[bi], ox=ox, oy=oy)
        limit = float(sp.get('max_flash_hz', env.ctx.get('flash_limit_hz', 3.0)))
        q = 8

        def lum(key):
            if key is None:
                return None
            el = els[key]
            spr = text_sprite(el['block'], el['ts'], env)
            m = np.zeros((env.oh // q + 1, env.ow // q + 1), np.float32)
            if spr is None:
                return m
            ox, oy = _el_origin(el, env, spr)
            a = spr.rgba
            L_ = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
            small = cv2.resize(L_, (max(1, a.shape[1] // q), max(1, a.shape[0] // q)), interpolation=cv2.INTER_AREA)
            X, Y = int((ox + spr.x) // q), int((oy + spr.y) // q)
            reg, mm = _clip_paste(m, small, X, Y)
            if reg is not None:
                np.maximum(reg, mm, out=reg)
            return m
        shown = flash_guard(want, lum, env.fps, max_hz=limit)
        return {'strobe': shown, 'els': els, 'f0': f0L, 'smear': smear}

    @classmethod
    def _plan_countdown(cls, L, env, st, x_c, y_c, f0L):
        cd = dict(L.get('countdown') or {})
        digits = [str(d) for d in cd.get('digits', [3, 2, 1])]
        per = float(cd.get('per', 0.35))
        sizes = cd.get('sizes', [[0.96, 0.47], [0.45, 0.35], [0.33, 0.23]])
        els = []
        for i, d in enumerate(digits):
            s0, s1 = sizes[min(i, len(sizes) - 1)]
            S0 = env.cH(s0) if s0 <= 1 else float(s0)
            b = make_block([d], st, env, size=S0)
            k = min(1.0, 0.9 * env.safe_w_center(x_c) / max(1.0, b.width),
                    0.9 * (env.safe_c[3] - env.safe_c[1]) / max(1.0, b.cap * 1.1))
            if k < 1.0:
                b = make_block([d], st, env, size=S0 * k)
            fa = f0L + int(round(i * per * env.fps))
            fb = f0L + int(round((i + 1) * per * env.fps)) - 1
            ox, oy = block_origin(b, x_c, y_c)
            els.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=ox, oy=oy, fa=fa, fb=fb,
                            s0=1.0, s1=(s1 / s0), clamp=True))
        return {'countdown': els, 'slant': float(cd.get('slant', 10.0)), 'stripes': cd.get('stripes', 7)}

    @classmethod
    def draw(cls, L, env, plan, cv):
        f = env.f
        if 'strobe' in plan:
            k = f - plan['f0']
            if 0 <= k < len(plan['strobe']) and plan['strobe'][k] is not None:
                el = plan['els'][plan['strobe'][k]]
                st = St()
                st.smear = plan['smear']
                _draw_el(cv, env, el, st)
            return
        if 'countdown' in plan:
            for el in plan['countdown']:
                if el['fa'] <= f <= el['fb']:
                    u = (f - el['fa']) / max(1.0, el['fb'] - el['fa'])
                    st = St()
                    st.sx = st.sy = el['s0'] + (el['s1'] - el['s0']) * ease(u, 'outExpo')
                    st.shear = -math.tan(math.radians(plan['slant']))
                    spr = text_sprite(el['block'], el['ts'], env)
                    if spr is None:
                        return
                    if plan['stripes']:
                        rg = spr.rgba.copy()
                        h = rg.shape[0]
                        per_px = max(4.0, el['block'].size * env.s / float(plan['stripes']))
                        yy = (np.arange(h, dtype=np.float32) + spr.y) % per_px
                        m = np.clip((per_px * 0.74 - yy) / 1.5, 0.0, 1.0)
                        for c in range(4):
                            rg[..., c] *= m[:, None]
                        spr = Sprite(rg, spr.x, spr.y)
                    ox, oy = _el_origin(el, env, text_sprite(el['block'], el['ts'], env), 1.0 + math.tan(math.radians(plan['slant'])) * 0.3)
                    cv.place(spr, ox, oy, st, (ox + el['block'].width * env.s / 2, oy + el['block'].height * env.s / 2))
            return
        a_in, a_out = plan['in'], plan['out']
        for el in plan['els']:
            if not (el['fa'] <= f <= el['fb']):
                continue
            if plan.get('phrase'):
                st_out = element_state(None, a_out, f, el['fa'], el['fb'], env)
                if st_out is None:
                    continue
                for j, wf in enumerate(el['wf']):
                    if f < wf:
                        continue
                    st = in_state(a_in, f - wf, env).compose(st_out)
                    _draw_el(cv, env, el, st, only={j})
                continue
            st = element_state(el.get('in', a_in), a_out, f, el['fa'], el['fb'], env)
            if st is not None and el['ts'].grow and a_in.get('type') == 'pop':
                st.decor = min(st.decor, (f - el['fa'] + 1) / float(el['ts'].grow))
            _draw_el(cv, env, el, st)


# ---------------------------------------------------------------------------- beat text
@register
class BeatText(Kind):
    """type.beat_text — words on the beat grid: hit on each slot, slam on downbeats/drop, kick pulse, builds."""
    name = 'beat_text'

    @classmethod
    def _slots(cls, L, fps, ctx=None):
        ctx = ctx or {}
        if L.get('slots'):
            out = []
            for s in L['slots']:
                fr = s.get('f')
                if fr is None:
                    fr = int(round(_f(s.get('t', 0.0)) * fps))
                out.append(dict(w=str(s.get('w', s.get('text', ''))), f=int(fr), accent=s.get('accent'),
                                dur=s.get('dur')))
            return sorted(out, key=lambda d: d['f'])
        toks = L.get('words') or tokenize(L.get('text', ''))
        toks = [t if isinstance(t, str) else str(t.get('w', '')) for t in toks]
        beats = [float(b) for b in (L.get('beats') or ctx.get('beats') or [])]
        if not beats:
            bpm = float(L.get('bpm', 120.0))
            t0 = _f(L.get('t0'), (L.get('f0') or 0) / fps)
            beats = [t0 + i * 60.0 / bpm for i in range(len(toks) * int(L.get('every', 1)) + 8)]
        t_start = _f(L.get('start', L.get('t0')), beats[0] if beats else 0.0)
        bi = int(np.searchsorted(np.array(beats), t_start - 1e-3))
        every = max(1, int(L.get('every', 1)))
        down = set(round(float(d), 3) for d in (L.get('downbeats') or ctx.get('downbeats') or []))
        out = []
        min_on = float(L.get('min_on', 0.27))
        for t in toks:
            if bi >= len(beats):
                break
            nb = bi + every
            dur_t = (beats[nb] - beats[bi]) if nb < len(beats) else 60.0 / float(L.get('bpm', 120.0)) * every
            need = min_on + max(0, len(t) - 5) * 0.04
            if dur_t < need and nb + every < len(beats):
                nb += every
            acc = 'downbeat' if round(beats[bi], 3) in down else None
            out.append(dict(w=t, f=int(round(beats[bi] * fps)), accent=acc, dur=None))
            bi = nb
        return out

    @classmethod
    def span(cls, L, fps, ctx=None):
        if L.get('f0') is not None and L.get('f1') is not None:
            return int(L['f0']), int(L['f1'])
        sl = cls._slots(L, fps, ctx)
        if not sl:
            return _span(L, fps)
        hold = int(round(float(L.get('hold', 0.6)) * fps))
        return int(L.get('f0', sl[0]['f'] - 2)), int(L.get('f1', sl[-1]['f'] + hold))

    @classmethod
    def plan(cls, L, env):
        v = env.vertical
        st = style_of(L, {'font': 'grotesk_condensed_black', 'caps': True, 'tracking': -0.02, 'color': '#ffffff',
                          'size': {'fit_width': 0.76, 'max': 0.16, 'min': 0.05} if v else 0.22,
                          'stroke': None, 'line_height': 0.95})
        fps = env.fps
        f0L, f1L = cls.span(L, fps, env.ctx)
        slots = cls._slots(L, fps, env.ctx)
        lead = int(L.get('lead', -1))
        layout = L.get('layout', 'single')
        reset = int(L.get('reset_every', 4))
        pos = L.get('pos', [0.47 if v else 0.5, 0.48])
        x_c, y_c = env.cW(pos[0]), env.cH(pos[1])
        maxw = min(env.safe_w_center(x_c), env.W * (0.76 if v else 0.9)) / _overshoot(
            parse_anim(L.get('anim_in', 'hit'), 'hit', fps))
        anchors = L.get('anchors', [[0.47, 0.24], [0.47, 0.46], [0.47, 0.68]] if v else [[0.3, 0.3], [0.5, 0.5], [0.7, 0.7]])
        accent = to_rgba(st.get('accent', L.get('accent', '#ffe600')))
        kicks = [float(k) for k in (L.get('kicks') or env.ctx.get('kicks') or [])]
        els = []
        for i, sl in enumerate(slots):
            a = sl['accent']
            fa = sl['f'] + (0 if a in ('slam', 'drop', 'downbeat') else lead)
            nxt = slots[i + 1]['f'] + lead if i + 1 < len(slots) else None
            if sl.get('dur'):
                fb = fa + int(round(float(sl['dur']) * fps)) - 1
            elif layout in ('line_build', 'stack_build'):
                g0 = (i // reset) * reset
                g1 = min(len(slots) - 1, g0 + reset - 1)
                fb = slots[g1 + 1]['f'] + lead - 1 if g1 + 1 < len(slots) else f1L
            else:
                fb = (nxt - 1) if nxt is not None else f1L
            fb = min(fb, f1L)
            els.append(dict(i=i, w=sl['w'], fa=max(fa, f0L), fb=fb, accent=a))
        # layouts (canvas px)
        if layout in ('line_build', 'stack_build'):
            for g0 in range(0, len(els), reset):
                grp = els[g0:g0 + reset]
                toks = [e['w'] for e in grp]
                if layout == 'line_build':
                    b = make_block(toks, st, env, max_width=maxw, max_lines=2)
                    ox, oy = block_origin(b, x_c, y_c)
                    for j, e in enumerate(grp):
                        e.update(block=b, only={j}, ox=ox, oy=oy)
                else:
                    sub = [make_block([t], st, env, max_width=maxw, max_lines=1) for t in toks]
                    S = min(b.size for b in sub)
                    sub = [make_block([t], st, env, max_width=maxw, max_lines=1, size=S) for t in toks]
                    pitch = S * float(L.get('pitch', 0.95))
                    tot = (len(sub) - 1) * pitch
                    for j, (e, b) in enumerate(zip(grp, sub)):
                        ox, oy = block_origin(b, x_c, y_c - tot / 2 + j * pitch)
                        e.update(block=b, only=None, ox=ox, oy=oy)
        else:
            blocks = [make_block([e['w']], st, env, max_width=maxw, max_lines=1) for e in els]
            if blocks and isinstance(st.get('size'), dict) and L.get('same_size', False):
                S = min(b.size for b in blocks)
                blocks = [make_block([e['w']], st, env, max_width=maxw, max_lines=1, size=S) for e in els]
            for j, (e, b) in enumerate(zip(els, blocks)):
                if layout == 'jump':
                    ax, ay = anchors[j % len(anchors)]
                    ox, oy = block_origin(b, env.cW(ax), env.cH(ay))
                else:
                    ox, oy = block_origin(b, x_c, y_c)
                e.update(block=b, only=None, ox=ox, oy=oy)
        for e in els:
            e['ts'] = resolve_style(st, env, e['block'].size)
            e['grow'] = 1.2 if e['accent'] not in ('slam', 'drop', 'downbeat') else 1.0
            e['clamp'] = layout != 'cards'
        a_hit = parse_anim(L.get('anim_in', 'hit'), 'hit', fps)
        acc_spec = (L.get('accents') or {}).get('downbeat')
        if acc_spec is None:
            acc_spec = L['anim_in'] if a_hit.get('type') in ('slam', 'slam_in') else 'slam'
        a_slam = parse_anim(acc_spec, 'slam', fps)
        a_out = parse_anim(L.get('anim_out', 'cut'), 'cut', fps)
        return dict(els=els, hit=a_hit, slam=a_slam, out=a_out, kicks=kicks, accent=accent, layout=layout,
                    outline=L.get('outline_cycle'), scrim=float(L.get('scrim', 0.0)), f0=f0L, f1=f1L)

    @classmethod
    def draw(cls, L, env, plan, cv):
        f = env.f
        fps = env.fps
        if plan['scrim'] > 0 and plan['f0'] <= f <= plan['f1']:
            cv.fill('#000000', plan['scrim'])
        for e in plan['els']:
            if not (e['fa'] <= f <= e['fb']):
                continue
            slam = e['accent'] in ('slam', 'drop', 'downbeat')
            st = element_state(plan['slam'] if slam else plan['hit'], plan['out'], f, e['fa'], e['fb'], env)
            if st is None:
                continue
            k = f - e['fa']
            if slam and st.sx > 1.0:
                # the slam peak (×1.4–1.6) is capped so the word never leaves the safe zone (per side, about its centre)
                b = e['block']
                spr0 = text_sprite(b, e['ts'], env)
                if spr0 is not None:
                    ox, oy = _el_origin(e, env, spr0, e.get('grow', 1.0))
                    tb = _tight(spr0)
                    cap_scale(st, spr0, ox, oy, (ox + b.width * env.s / 2.0, oy + (tb[1] + tb[3]) / 2.0), env)
            if slam and L.get('shake'):
                sh = L['shake'] if isinstance(L['shake'], dict) else {}
                n_sh = int(sh.get('frames', env.fr25(6)))
                if k < n_sh:
                    amp = env.o(env.cH(sh.get('amp', 0.012))) * math.exp(-3.0 * k / n_sh)
                    st.dx += amp * (2 * _rnd(env.seed, f, 1) - 1)
                    st.dy += amp * (2 * _rnd(env.seed, f, 2) - 1)
            inv = slam and k < int(L.get('invert_frames', 0) or 0)
            if inv:                                  # drop slam: black word on a white field for 1–2 frames
                cv.fill('#ffffff', 1.0)
            cols = None
            if e['accent'] in ('snare', 'accent') or (slam and plan['layout'] != 'cards'):
                cols = {k: plan['accent'] for k in range(len(e['block'].words))}
            # kick pulse on a standing word
            for kt in plan['kicks']:
                kf = int(round(kt * fps))
                if e['fa'] + 3 <= kf <= f and f - kf < env.fr25(6):
                    j = f - kf
                    back = env.fr25(5)
                    st.sx *= 1 + 0.06 * (1 - ease(min(1.0, j / back), 'outQuad'))
                    st.sy = st.sx
            outline = False
            if plan['outline']:
                every = int(plan['outline'].get('every', 1)) if isinstance(plan['outline'], dict) else 1
                outline = (e['i'] // every) % 2 == 1
            if plan['layout'] == 'cards' and not inv:
                cv.fill('#000000', 1.0)
            if inv:
                cols = {kk: (0.0, 0.0, 0.0, 1.0) for kk in range(len(e['block'].words))}
            if outline and not e['ts'].stroke:
                ts = resolve_style(dict(style_of(L, {}), stroke={'w': 0.05, 'color': L.get('color', '#ffffff')}), env,
                                   e['block'].size)
                e2 = dict(e, ts=ts)
                _draw_el(cv, env, e2, st, outline=True, only=e.get('only'), cols=cols)
            else:
                _draw_el(cv, env, e, st, only=e.get('only'), cols=cols)


# ---------------------------------------------------------------------------- shape helpers (anti-aliased, local)
class MaskSprite:
    """uint8 coverage + straight colour at (x, y): drawn straight into the canvas when untransformed (no RGBA)."""
    __slots__ = ('m', 'x', 'y', 'col')

    def __init__(self, m, col, x, y):
        self.m, self.col, self.x, self.y = m, col, x, y

    def to_sprite(self):
        return colored_sprite(self.m.astype(np.float32) * (1.0 / 255.0), self.col, self.x, self.y)

    @property
    def rgba(self):
        return self.to_sprite().rgba


def stroke_sprite(points, width, col, closed=False, progress=1.0, cap=True):
    """Polyline (output px points) drawn up to `progress` of its length -> MaskSprite (or None)."""
    pts = np.asarray(points, np.float64).reshape(-1, 2)
    if len(pts) < 2 or progress <= 0:
        return None
    if closed:
        pts = np.vstack([pts, pts[:1]])
    if progress < 1.0:
        seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1))
        cum = np.concatenate([[0], np.cumsum(seg)])
        target = cum[-1] * progress
        k = int(np.searchsorted(cum, target))
        k = max(1, min(k, len(pts) - 1))
        t = (target - cum[k - 1]) / max(seg[k - 1], 1e-9)
        pts = np.vstack([pts[:k], pts[k - 1] + (pts[k] - pts[k - 1]) * t])
    w = max(1.0, float(width))
    pad = int(math.ceil(w)) + 3
    x0, y0 = int(math.floor(pts[:, 0].min())) - pad, int(math.floor(pts[:, 1].min())) - pad
    x1, y1 = int(math.ceil(pts[:, 0].max())) + pad, int(math.ceil(pts[:, 1].max())) + pad
    img = np.zeros((y1 - y0, x1 - x0), np.uint8)
    p = np.round((pts - (x0, y0)) * 8).astype(np.int32)
    cv2.polylines(img, [p], False, 255, thickness=max(1, int(round(w))), lineType=cv2.LINE_AA, shift=3)
    return MaskSprite(img, col, x0, y0)


def poly_sprite(points, col):
    pts = np.asarray(points, np.float64).reshape(-1, 2)
    x0, y0 = int(math.floor(pts[:, 0].min())) - 2, int(math.floor(pts[:, 1].min())) - 2
    x1, y1 = int(math.ceil(pts[:, 0].max())) + 2, int(math.ceil(pts[:, 1].max())) + 2
    img = np.zeros((max(1, y1 - y0), max(1, x1 - x0)), np.uint8)
    cv2.fillPoly(img, [np.round((pts - (x0, y0)) * 8).astype(np.int32)], 255, lineType=cv2.LINE_AA, shift=3)
    return MaskSprite(img, col, x0, y0)


def disc_sprite(cx, cy, r, col, ring=None):
    """Filled disc (ring=None) or ring of width `ring`, anti-aliased, centred at (cx, cy) output px."""
    r = max(0.5, float(r))
    R = int(math.ceil(r + (ring or 0) + 2))
    ys, xs = np.mgrid[-R:R + 1, -R:R + 1].astype(np.float32)
    fx, fy = cx - math.floor(cx), cy - math.floor(cy)
    d = np.sqrt((xs - fx + 0.5) ** 2 + (ys - fy + 0.5) ** 2)
    if ring:
        m = np.clip(0.5 - (np.abs(d - r) - ring / 2.0), 0.0, 1.0)
    else:
        m = np.clip(r - d + 0.5, 0.0, 1.0)
    return colored_sprite(m, col, math.floor(cx) - R, math.floor(cy) - R)


def rect_sprite(x0, y0, x1, y1, col, radius=0.0):
    if x1 - x0 < 0.5 or y1 - y0 < 0.5:
        return None
    m = round_rect_mask(x1 - x0, y1 - y0, radius)
    return colored_sprite(m, col, x0, y0)


def clip_x(spr, ox, x_min=None, x_max=None):
    """Zero the sprite columns left of x_min / right of x_max (output px, sprite drawn at origin ox)."""
    rg = spr.rgba
    w = rg.shape[1]
    xs = np.arange(w, dtype=np.float32) + ox + spr.x
    m = np.ones(w, np.float32)
    if x_min is not None:
        m *= np.clip(xs - x_min + 0.5, 0.0, 1.0)
    if x_max is not None:
        m *= np.clip(x_max - xs + 0.5, 0.0, 1.0)
    if m.min() >= 1.0:
        return spr
    rg = rg * m[None, :, None]
    return Sprite(np.ascontiguousarray(rg, np.float32), spr.x, spr.y)


def bezier(p0, p1, p2, n=40):
    t = np.linspace(0.0, 1.0, n)[:, None]
    p0, p1, p2 = (np.asarray(p, np.float64) for p in (p0, p1, p2))
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


# ---------------------------------------------------------------------------- title card
@register
class TitleCard(Kind):
    """type.title_card — title block (kicker / title / credit) in 6 layouts, fade / blur_in / slam_in / reveal /
    words_build / strobe(-limited) / colour reveal in; dissolve / cut / zoom_through out; optional card background,
    underline draw-on and beat pulse."""
    name = 'title_card'
    default_dur = 5.0

    @classmethod
    def plan(cls, L, env):
        v = env.vertical
        layout = L.get('layout', 'center_block')
        tc = L.get('type_class', 'script' if layout == 'sky_top' else 'serif_caps')
        caps = tc in ('serif_caps', 'grotesk_condensed_black', 'grotesk_extended', 'grotesk_extended_bold', 'caps_bold_wide',
                      'condensed_bold_caps')
        base = style_of(L, {'font': tc, 'color': '#f2ede4', 'caps': caps, 'tracking': 0.05 if tc == 'serif_caps' else 0.0,
                            'line_height': 1.02})
        raw = L.get('lines') or [{'text': L.get('text', ''), 'role': 'title'}]
        lines = [dict(l) if isinstance(l, dict) else {'text': str(l), 'role': 'title' if i == 0 else 'credit'}
                 for i, l in enumerate(raw)]
        pos = L.get('pos')
        x_c = env.cW(pos[0] if pos else L.get('x', 0.47 if v else 0.5))
        maxw = min(env.safe_w_center(x_c), env.W * 0.92)
        small_font = L.get('small_font', 'serif_book' if tc in ('serif_caps', 'didone', 'serif', 'script') else 'grotesk_medium')

        def mk(text, role, size, extra=None, max_lines=2, width=None):
            st = dict(base)
            if role != 'title':
                st.update({'font': small_font, 'caps': True, 'tracking': 0.16, 'size': size})
            st['size'] = size
            st.update(extra or {})
            st.update(L.get(role + '_style') or {})
            for ln in lines:
                if ln.get('text') == text and ln.get('style'):
                    st.update(ln['style'])
            b = make_block(tokenize(text), st, env, max_width=width or maxw, max_lines=max_lines)
            return b, st

        title_size = {'center_block': 0.10, 'poster': 0.33, 'fill': 0.8, 'frame_top_bottom': 0.12, 'lower_block': 0.077,
                      'sky_top': 0.16}.get(layout, 0.10)
        if v:
            title_size = {'fit_width': 0.8 if layout != 'poster' else 0.86,
                          'max': {'center_block': 0.11, 'poster': 0.2, 'fill': 0.3, 'frame_top_bottom': 0.075,
                                  'lower_block': 0.065, 'sky_top': 0.1}.get(layout, 0.11)}
        if L.get('size') is not None and not isinstance(L.get('size'), dict):
            title_size = L['size']
        elif isinstance(L.get('size'), dict) and 'title' not in L['size']:
            title_size = L['size']
        sizes = {'kicker': 0.022 if not v else 0.017, 'credit': 0.022 if not v else 0.017}
        if isinstance(L.get('sizes'), dict):
            sizes.update(L['sizes'])
            title_size = L['sizes'].get('title', title_size)
        els = []
        titles = [l for l in lines if l.get('role', 'title') == 'title']
        kick = [l for l in lines if l.get('role') == 'kicker']
        creds = [l for l in lines if l.get('role') == 'credit']
        sx0, sy0, sx1, sy1 = env.safe_c

        def add(b, st, x, y, role, ax='center', ay='center', delay=0.0):
            ox, oy = block_origin(b, x, y, ax, ay)
            els.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=ox, oy=oy, role=role, delay=float(delay)))

        if layout == 'fill':
            toks = [t for l in titles for t in tokenize(l['text'])]
            if v:
                st = dict(base, size={'fit_width': 0.84, 'max': 0.3})
                bl = [make_block([t], st, env, max_width=maxw, max_lines=1) for t in toks]
                S = min(b.size for b in bl) if bl else 10
                bl = [make_block([t], st, env, max_width=maxw, max_lines=1, size=S) for t in toks]
                pitch = S * 0.98
                y_c = env.cH(pos[1] if pos else L.get('y', 0.46))
                for j, b in enumerate(bl):
                    add(b, dict(base, size=S), x_c, y_c - (len(bl) - 1) * pitch / 2 + j * pitch, 'title')
            else:
                st = dict(base, size={'fit_width': 0.92, 'max': 0.8})
                b = make_block(toks, st, env, max_width=env.W * 0.92, max_lines=1, max_height=(sy1 - sy0))
                add(b, st, x_c, env.cH(pos[1] if pos else L.get('y', 0.5)), 'title')
        elif layout == 'frame_top_bottom':
            ex = {'tracking': 0.35}
            top = titles[0]['text'] if titles else ''
            bot = (titles[1]['text'] if len(titles) > 1 else (creds[0]['text'] if creds else ''))
            bt, st = mk(top, 'title', title_size, ex, 1)
            add(bt, st, x_c, env.cH(L.get('y_top', 0.2 if v else 0.22)), 'title')
            if bot:
                bb, st2 = mk(bot, 'title', title_size, ex, 1)
                add(bb, st2, x_c, env.cH(L.get('y_bottom', 0.72 if v else 0.82)), 'title', delay=0.0)
        else:
            stack = []
            for l in kick:
                stack.append(mk(l['text'], 'kicker', sizes['kicker'], None, 2) + ('kicker', l.get('delay', 0.0)))
            for l in titles:
                stack.append(mk(l['text'], 'title', title_size, None, int(L.get('max_lines', 2))) + ('title', l.get('delay', 0.0)))
            billing = []
            for l in creds:
                item = mk(l['text'], 'credit', sizes['credit'] if layout != 'poster' else (0.012 if v else 0.014), None, 2) + (
                    'credit', l.get('delay', 0.0))
                (billing if layout == 'poster' else stack).append(item)
            gap = lambda a, b: 0.45 * max(a.size, b.size) if 'title' not in (None,) else 0
            y_c = env.cH(pos[1] if pos else L.get('y', {'center_block': 0.44 if v else 0.45, 'poster': 0.42,
                                                         'lower_block': 0.66 if v else 0.7, 'sky_top': 0.25}.get(layout, 0.45)))
            heights = [b.height for b, _, _, _ in stack]
            gaps = [0.55 * min(stack[i][0].size, stack[i + 1][0].size) + 0.25 * max(stack[i][0].size, stack[i + 1][0].size) * 0.3
                    for i in range(len(stack) - 1)]
            if L.get('underline'):
                ti = next((i for i, it in enumerate(stack) if it[2] == 'title'), None)
                if ti is not None and ti < len(gaps):
                    gaps[ti] += 0.35 * stack[ti][0].size
            tot = sum(heights) + sum(gaps)
            y = y_c - tot / 2
            for i, (b, st, role, dl) in enumerate(stack):
                add(b, st, x_c, y, role, 'center', 'top', dl)
                y += b.height + (gaps[i] if i < len(gaps) else 0)
            if billing:
                yb = env.cH(L.get('y_billing', 0.76 if v else 0.9))
                for b, st, role, dl in billing[::-1]:
                    add(b, st, x_c, yb, role, 'center', 'bottom', dl)
                    yb -= b.height + 0.5 * b.size
        a_in = parse_anim(L.get('anim_in', 'fade(0.6)'), 'fade', env.fps)
        out_spec = L.get('anim_out', 'dissolve')
        if isinstance(out_spec, str) and out_spec.strip() == 'zoom_through':
            out_spec = {'type': 'zoom_through', 'dur': 2.8, 'scale': 12.0, 'ease': 'inExpo'}
        a_out = parse_anim(out_spec, 'dissolve', env.fps)
        f0, f1 = cls.span(L, env.fps)
        strobe = None
        if a_in.get('type') == 'strobe':
            n = int(round(a_in.get('dur', 0.5) * env.fps))
            per = max(1, int(a_in.get('per', 1)))
            want = [('on' if (k // per) % 2 == 0 else None) for k in range(n)]
            limit = float(a_in.get('max_flash_hz', env.ctx.get('flash_limit_hz', 3.0)))
            area = sum(el['block'].width * el['block'].height for el in els) / (env.W * env.H) * 0.45

            def lum(sname):
                return None if sname is None else np.full((4, 4), 1.0 if area > 0.05 else 0.0, np.float32)
            strobe = flash_guard(want, lum, env.fps, max_hz=limit)
        for el in els:
            el['grow'] = _overshoot(a_in)
        return dict(els=els, a_in=a_in, a_out=a_out, f0=f0, f1=f1, strobe=strobe)

    @classmethod
    def draw(cls, L, env, plan, cv):
        f, fps = env.f, env.fps
        f0, f1 = plan['f0'], plan['f1']
        a_in, a_out = plan['a_in'], plan['a_out']
        bg = L.get('bg')
        if bg:
            st_bg = element_state(None, a_out if L.get('bg_out', 'cut') != 'cut' else None, f, f0, f1, env)
            a = st_bg.alpha if st_bg else 0.0
            if isinstance(bg, dict) and bg.get('gradient'):
                g = to_rgba_list(bg['gradient'])
                yy = np.linspace(0, 1, env.oh, dtype=np.float32)
                ph = 0.08 * math.sin(2 * math.pi * env.t / float(bg.get('period', 6.0))) if bg.get('breathe', True) else 0
                t = np.clip(yy + ph, 0, 1)
                cr = np.stack([np.interp(t, np.linspace(0, 1, len(g)), [c[i] for c in g]) for i in range(4)], 1)
                rg = np.empty((env.oh, env.ow, 4), np.float32)
                for i in range(3):
                    rg[..., i] = (cr[:, i] * cr[:, 3] * a)[:, None]
                rg[..., 3] = (cr[:, 3] * a)[:, None]
                cv.blit(rg, 0, 0)
            else:
                cv.fill(bg if isinstance(bg, str) else tuple(bg), a)
        for i, el in enumerate(plan['els']):
            fa = f0 + int(round(el['delay'] * fps))
            if f < fa:
                continue
            alphas = None
            if a_in.get('type') == 'words_build':
                step = float(a_in.get('step', 0.3)) * fps
                alphas = {j: (1.0 if f >= fa + j * step else 0.0) for j in range(len(el['block'].words))}
                st = element_state(None, a_out, f, fa, f1, env)
            elif a_in.get('type') == 'strobe':
                k = f - fa
                st = element_state(None, a_out, f, fa, f1, env)
                if st is not None and k < len(plan['strobe']):
                    if plan['strobe'][k] is None:
                        st.alpha = 0.0
                    if k / fps < a_in.get('flip', 0.2):
                        st.rot = 180.0
            else:
                st = element_state(a_in, a_out, f, fa, f1, env)
            if st is None:
                continue
            if L.get('pulse'):
                pu = L['pulse'] if isinstance(L['pulse'], dict) else {}
                lo, hi = pu.get('scale', [0.96, 1.06])
                ph = (f - fa) / fps / float(pu.get('period', 0.36))
                k = lo + (hi - lo) * (0.5 + 0.5 * math.cos(2 * math.pi * ph))
                st.sx *= k
                st.sy *= k
            _draw_el(cv, env, el, st, alphas=alphas)
            if L.get('underline') and el['role'] == 'title' and i == next(
                    (j for j, e in enumerate(plan['els']) if e['role'] == 'title'), -1):
                ul = L['underline'] if isinstance(L['underline'], dict) else {}
                d0 = fa + int(round(float(ul.get('delay', a_in.get('dur', 0.6))) * fps))
                if f >= d0:
                    p = ease(min(1.0, (f - d0 + 1) / max(1.0, float(ul.get('dur', 0.32)) * fps)), 'outCubic')
                    b = el['block']
                    spr0 = text_sprite(b, el['ts'], env)
                    ox, oy = _el_origin(el, env, spr0, el.get('grow', 1.0))
                    y = oy + (b.height + 0.16 * b.size) * env.s
                    th = max(1.5, env.o(env.cH(ul.get('w', 0.006))))
                    x0 = ox
                    spr = rect_sprite(x0, y, x0 + b.width * env.s * p, y + th,
                                      to_rgba(ul.get('color', L.get('color', '#f2ede4'))), th / 2)
                    if spr is not None:
                        st2 = St()
                        st2.alpha = st.alpha
                        cv.place(spr, 0, 0, st2)


# ---------------------------------------------------------------------------- lower third
@register
class LowerThird(Kind):
    """type.lower_third — name/role plate: accent bar grows, plate wipes open, name and role slide out from under
    the mask (13 frames @25, ×fps/25), hold, reverse exit (8 frames) or fade; variants plate | minimal | block |
    location | topic | handle."""
    name = 'lower_third'
    default_dur = 4.0

    @classmethod
    def plan(cls, L, env):
        v = env.vertical
        variant = L.get('variant', 'plate')
        name = str(L.get('name', L.get('text', '')))
        role = L.get('role')
        if variant == 'handle' and not name.startswith('@'):
            name = '@' + name
        nh = float(L.get('name_size', (0.026 if v else 0.03) if variant == 'location' else (0.032 if v else 0.045)))
        st_n = style_of(L, {'font': 'inter:700', 'color': '#ffffff', 'size': nh})
        st_r = {'font': 'inter:500', 'color': '#c9cdd2', 'size': nh * float(L.get('role_ratio', 0.66))}
        st_r.update(L.get('role_style') or {})
        accent = to_rgba(L.get('accent', '#ffc400'))
        plate_col = to_rgba(L.get('plate_color', '#000000'), L.get('plate_alpha', 0.65))
        if variant == 'block':
            plate_col = accent
            st_n['color'] = st_n.get('text_color', '#111111')
            st_r.update({'color': '#ffffff'})
        if variant in ('minimal', 'location', 'handle'):
            st_n.setdefault('shadow', {'dy': 0.05, 'blur': 0.12, 'alpha': 0.6})
            st_r.setdefault('shadow', {'dy': 0.05, 'blur': 0.12, 'alpha': 0.6})
        if variant == 'location':
            st_n.update({'caps': True, 'tracking': 0.08, 'font': 'inter:600'})
        nh_c = env.cH(nh)
        side = L.get('side', 'left')
        max_w = (0.70 if v else 0.45) * env.W
        pad_x, pad_y = 0.6 * nh_c, 0.35 * nh_c
        if variant in ('minimal', 'location', 'handle'):
            pad_x, pad_y = 0.0, 0.0
        bar_w = (0.006 if v else 0.005) * env.W if variant == 'plate' else 0.0
        icon_w = 0.9 * nh_c if variant == 'location' else 0.0
        nb = make_block(tokenize(name), st_n, env, max_width=max_w - 2 * pad_x - icon_w, max_lines=1)
        rb = make_block(tokenize(role), st_r, env, max_width=max_w - 2 * pad_x, max_lines=1) if role else None
        gap = 0.3 * nb.size
        inner_w = max(nb.width + icon_w, rb.width if rb else 0.0)
        inner_h = nb.height + ((gap + rb.height) if (rb and variant != 'block') else 0.0)
        plate_w, plate_h = inner_w + 2 * pad_x, inner_h + 2 * pad_y
        if 'y' in L:
            bottom = env.cH(L['y'])
        elif L.get('above') is not None:
            bottom = env.cH(L['above']) - 0.02 * env.H
        else:
            bottom = env.cH(0.78 if v else 0.86)
        role_pill_h = (rb.height + 2 * 0.3 * rb.size) if (rb and variant == 'block') else 0.0
        top = bottom - plate_h - (role_pill_h + 0.01 * env.H if role_pill_h else 0.0)
        if side == 'right':
            x_right = env.cW(L.get('x', 0.88 if v else 0.93))
            x0 = x_right - plate_w - bar_w
        else:
            x0 = env.cW(L.get('x', 0.07))
        # keep the whole group (plus shadow reach) in the safe zone
        sm = deco_margin(st_n, env, nh_c) if variant in ('minimal', 'location', 'handle') else 0.0
        sx0, sy0, sx1, sy1 = env.safe_c
        sx0, sy0, sx1, sy1 = sx0 + sm, sy0 + sm, sx1 - sm, sy1 - sm
        gw = plate_w + bar_w
        dx = (sx0 - x0) if x0 < sx0 else (sx1 - (x0 + gw)) if x0 + gw > sx1 else 0.0
        dy = (sy0 - top) if top < sy0 else (sy1 - bottom) if bottom > sy1 else 0.0
        x0 += dx
        top += dy
        bottom += dy
        if side == 'right':
            plate = (x0, top, x0 + plate_w, top + plate_h)
            bar = (x0 + plate_w, top, x0 + plate_w + bar_w, top + plate_h)
        else:
            bar = (x0, top, x0 + bar_w, top + plate_h)
            plate = (x0 + bar_w, top, x0 + bar_w + plate_w, top + plate_h)
        if side == 'right':
            name_o = (plate[2] - pad_x - nb.width, plate[1] + pad_y)
            role_o = (plate[2] - pad_x - rb.width, name_o[1] + nb.height + gap) if rb else None
        else:
            name_o = (plate[0] + pad_x + icon_w, plate[1] + pad_y)
            role_o = (plate[0] + pad_x, name_o[1] + nb.height + gap) if rb else None
        pill = None
        if rb and variant == 'block':
            px = 0.3 * rb.size
            pill = (plate[0] + 0.015 * env.W, plate[3] + 0.01 * env.H, plate[0] + 0.015 * env.W + rb.width + 2 * px,
                    plate[3] + 0.01 * env.H + rb.height + 2 * px)
            role_o = (pill[0] + px, pill[1] + px)
        return dict(variant=variant, bar=bar, plate=plate, pill=pill, accent=accent, plate_col=plate_col,
                    name=dict(block=nb, ts=resolve_style(st_n, env, nb.size), ox=name_o[0], oy=name_o[1], clamp=False),
                    role=(dict(block=rb, ts=resolve_style(st_r, env, rb.size), ox=role_o[0], oy=role_o[1], clamp=False)
                          if rb else None), side=side, icon=icon_w, radius=float(L.get('radius', 0.0)) * nh_c)

    @classmethod
    def draw(cls, L, env, plan, cv):
        f0, f1 = cls.span(L, env.fps)
        f = env.f
        k = f - f0
        F = env.fr25
        s = env.s
        out = parse_anim(L.get('anim_out', 'reverse'), 'reverse', env.fps)
        n_out = F(8) if out.get('type') == 'reverse' else max(1, anim_frames(out, env.fps) or F(6))
        j = f - (f1 - n_out + 1)
        u = (j + 1) / (n_out + 1.0) if j >= 0 else 0.0
        lin = lambda a, b: _clamp((k - F(a) + 1) / max(1.0, F(b) - F(a)), 0.0, 1.0)
        variant = plan['variant']
        if variant in ('minimal', 'location', 'handle'):
            bar_p, plate_p = 0.0, 0.0
            name_p = ease(min(1.0, (k + 1) / F(8)), 'outCubic')
            role_p = ease(_clamp((k - F(3) + 1) / F(8), 0.0, 1.0), 'outCubic')
        else:
            bar_p = ease(min(1.0, (k + 1) / F(3)), 'outCubic')
            plate_p = ease(lin(2, 10), 'outExpo')
            name_p = ease(lin(4, 10), 'outCubic')
            role_p = ease(lin(7, 13), 'outCubic')
        g_alpha = 1.0
        if j >= 0:
            if out.get('type') == 'reverse':
                role_p *= 1 - _clamp(u / 0.4, 0, 1)
                name_p *= 1 - _clamp((u - 0.15) / 0.4, 0, 1)
                plate_p *= 1 - ease(_clamp((u - 0.3) / 0.5, 0, 1), 'inCubic')
                bar_p *= 1 - _clamp((u - 0.6) / 0.4, 0, 1)
                if variant in ('minimal', 'location', 'handle'):
                    g_alpha = 1 - u
            else:
                g_alpha = 1 - u
        stA = St()
        stA.alpha = g_alpha
        bx0, by0, bx1, by1 = [v * s for v in plan['bar']]
        px0, py0, px1, py1 = [v * s for v in plan['plate']]
        right = plan['side'] == 'right'
        if bar_p > 0 and bx1 > bx0:
            hh = (by1 - by0) * bar_p
            cy = (by0 + by1) / 2
            spr = rect_sprite(bx0, cy - hh / 2, bx1, cy + hh / 2, plan['accent'])
            cv.place(spr, 0, 0, stA)
        if plate_p > 0:
            w = (px1 - px0) * plate_p
            spr = (rect_sprite(px1 - w, py0, px1, py1, plan['plate_col'], plan['radius'] * s) if right else
                   rect_sprite(px0, py0, px0 + w, py1, plan['plate_col'], plan['radius'] * s))
            cv.place(spr, 0, 0, stA)
        clip_l = px0 if not right else None
        for el, p in ((plan['name'], name_p), (plan['role'], role_p)):
            if el is None or p <= 0:
                continue
            spr = text_sprite(el['block'], el['ts'], env)
            if spr is None:
                continue
            ox, oy = el['ox'] * s, el['oy'] * s
            if variant in ('plate', 'block'):          # out from under the plate mask, away from the bar
                dx = -0.025 * env.ow * (1 - p) * (-1 if right else 1)
            else:                                       # no mask: drift outwards from the inner side
                dx = 0.02 * env.ow * (1 - p) * (-1 if right else 1)
            if variant in ('plate', 'block'):
                spr = clip_x(spr, ox + dx, x_min=clip_l, x_max=px1 if right else None)
            st = St()
            st.dx = dx
            st.alpha = p * g_alpha
            cv.place(spr, ox, oy, st)
        if plan['pill'] is not None and role_p > 0:
            qx0, qy0, qx1, qy1 = [v * s for v in plan['pill']]
            spr = rect_sprite(qx0, qy0, qx0 + (qx1 - qx0) * role_p, qy1, to_rgba('#111111', 0.88), (qy1 - qy0) * 0.25)
            cv.place(spr, 0, 0, stA)
            el = plan['role']
            sp2 = text_sprite(el['block'], el['ts'], env)
            st = St()
            st.alpha = role_p * g_alpha
            cv.place(sp2, el['ox'] * s, el['oy'] * s, st)
        if plan['icon'] and name_p > 0:
            nb = plan['name']['block']
            r = 0.2 * nb.size * s
            cx = plan['name']['ox'] * s - plan['icon'] * s * 0.55
            cy = plan['name']['oy'] * s + nb.cap * s * 0.42
            col = plan['name']['ts'].fill
            st = St()
            st.alpha = name_p * g_alpha
            cv.place(disc_sprite(cx, cy, r, col, ring=0.42 * r), 0, 0, st)
            cv.place(poly_sprite([(cx - 0.62 * r, cy + 0.55 * r), (cx + 0.62 * r, cy + 0.55 * r), (cx, cy + 1.9 * r)], col),
                     0, 0, st)


# ---------------------------------------------------------------------------- intertitle
@register
class Intertitle(Kind):
    """type.intertitle — caption over the shot (time/place), chapter (big + small, second line later), text card,
    reply typed on black, trailer phrases slamming in, prologue lines revealed one by one."""
    name = 'intertitle'
    default_dur = 2.0

    @classmethod
    def plan(cls, L, env):
        v = env.vertical
        var = L.get('variant', 'caption')
        fps = env.fps
        f0, f1 = cls.span(L, fps)
        x_c = env.cW(L.get('x', 0.47 if v else 0.5))
        maxw = min(env.safe_w_center(x_c), env.W * 0.86)
        lines = L.get('lines') or [L.get('text', '')]
        els, bg = [], None
        if var == 'chapter':
            st1 = style_of(L, {'font': 'caps_bold_wide', 'caps': True, 'color': '#eebb14',
                               'size': {'fit_width': 0.8, 'max': 0.075} if v else 0.12})
            st2 = dict(st1, size={'fit_width': 0.7, 'max': 0.035} if v else 0.06, font='inter:600', tracking=0.08)
            b1 = make_block(tokenize(lines[0]), st1, env, max_width=maxw, max_lines=2)
            y = env.cH(L.get('y', 0.2 if v else 0.15))
            ox, oy = block_origin(b1, x_c, y, 'center', 'top')
            els.append(dict(block=b1, ts=resolve_style(st1, env, b1.size), ox=ox, oy=oy, fa=f0, a_in='cut'))
            if len(lines) > 1:
                b2 = make_block(tokenize(lines[1]), st2, env, max_width=maxw, max_lines=2)
                ox2, oy2 = block_origin(b2, x_c, y + b1.height + 0.45 * b1.size, 'center', 'top')
                els.append(dict(block=b2, ts=resolve_style(st2, env, b2.size), ox=ox2, oy=oy2,
                                fa=f0 + int(round(float(L.get('second_delay', 0.5)) * fps)), a_in='fade(0.3)'))
        elif var == 'reply':
            bg = L.get('bg', '#000000')
            st = style_of(L, {'font': 'mono', 'color': '#5aa0c8', 'size': 0.03 if v else 0.04, 'align': 'left'})
            b = make_block(tokenize(lines[0]), st, env, max_width=env.W * (0.78 if v else 0.7), max_lines=4)
            ox, oy = block_origin(b, env.cW(L.get('x', 0.1 if v else 0.15)), env.cH(L.get('y', 0.4 if v else 0.34)), 'left', 'top')
            els.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=ox, oy=oy, fa=f0,
                            a_in={'type': 'typewriter', 'cps': float(L.get('cps', 22))}))
        elif var == 'trailer':
            if L.get('card', True):
                bg = L.get('bg', '#000000')
            st = style_of(L, {'font': 'grotesk_condensed_black', 'caps': True, 'color': '#ffffff',
                              'size': {'fit_width': 0.8, 'max': 0.1} if v else 0.2})
            b = make_block(tokenize(lines[0]), st, env, max_width=maxw, max_lines=2)
            ox, oy = block_origin(b, x_c, env.cH(L.get('y', 0.46 if v else 0.5)))
            els.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=ox, oy=oy, fa=f0,
                            a_in={'type': 'slam_in', 'scale': [4.0, 0.97, 1.0], 'dur': 0.4}))
        elif var == 'prologue':
            bg = L.get('bg')
            st = style_of(L, {'font': 'inter:800', 'caps': True, 'color': '#f2ede4', 'size': 0.03 if v else 0.048})
            times = L.get('line_times') or [i * 1.5 for i in range(len(lines))]
            pitch = env.cH(st['size'] if not isinstance(st['size'], dict) else 0.05) * 1.35
            y0 = env.cH(L.get('y', 0.25))
            for i, (ln, t) in enumerate(zip(lines, times)):
                b = make_block(tokenize(ln), st, env, max_width=maxw, max_lines=1)
                ox, oy = block_origin(b, x_c, y0 + i * pitch, 'center', 'top')
                fa = f0 + int(round(float(t) * fps)) if float(t) < 1000 else int(t)
                els.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=ox, oy=oy, fa=fa, a_in='fade(0.5)'))
        elif var == 'card':
            bg = L.get('bg', '#000000')
            st = style_of(L, {'font': 'serif', 'color': '#f2ede4', 'size': {'fit_width': 0.8, 'max': 0.055} if v else 0.08,
                              'line_height': 1.15})
            b = make_block(tokenize(' '.join(lines)), st, env, max_width=maxw, max_lines=4)
            ox, oy = block_origin(b, x_c, env.cH(L.get('y', 0.46 if v else 0.5)))
            els.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=ox, oy=oy, fa=f0, a_in=L.get('anim_in', 'cut')))
        else:   # caption over the shot
            st = style_of(L, {'font': 'caps_bold_wide', 'caps': True, 'color': '#eebb14',
                              'size': {'fit_width': 0.76, 'max': 0.035} if v else 0.045, 'tracking': 0.02})
            b = make_block(tokenize(lines[0]), st, env, max_width=min(maxw, env.W * 0.8), max_lines=2)
            pos = L.get('pos', 'top')
            y = env.cH(0.5) if pos == 'center' else env.cH(L.get('y', 0.2 if v else 0.17)) if not isinstance(pos, (list, tuple)) else env.cH(pos[1])
            ox, oy = block_origin(b, x_c, y)
            els.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=ox, oy=oy, fa=f0, a_in=L.get('anim_in', 'cut')))
        for el in els:
            el['a_in'] = parse_anim(el['a_in'], 'cut', fps)
            el['grow'] = _overshoot(el['a_in'])
        return dict(els=els, bg=bg, f0=f0, f1=f1, a_out=parse_anim(L.get('anim_out', 'cut'), 'cut', fps))

    @classmethod
    def draw(cls, L, env, plan, cv):
        f = env.f
        if plan['bg']:
            cv.fill(plan['bg'], 1.0)
        for el in plan['els']:
            st = element_state(el['a_in'], plan['a_out'], f, el['fa'], plan['f1'], env)
            _draw_el(cv, env, el, st)


# ---------------------------------------------------------------------------- margin notes
@register
class MarginNote(Kind):
    """type.margin_notes — handwritten notes typed beside the speaker in time with the words: write, strike,
    correct (indented, next row), arrow to a total, punch word; side opposite to the face."""
    name = 'margin_note'
    default_dur = 6.0

    @classmethod
    def span(cls, L, fps, ctx=None):
        if L.get('f0') is not None and L.get('f1') is not None:
            return int(L['f0']), int(L['f1'])
        ts = [_f(it.get('t'), None) for it in L.get('items', []) if it.get('t') is not None]
        if not ts:
            return _span(L, fps, cls.default_dur)
        f0 = L.get('f0', int(math.floor(min(ts) * fps)) - 1)
        f1 = L.get('f1', int(math.ceil(max(ts) * fps + 3.0 * fps)))
        return int(f0), int(f1)

    @classmethod
    def plan(cls, L, env):
        v = env.vertical
        fps = env.fps
        f0, f1 = cls.span(L, fps)
        st = style_of(L, {'font': 'hand_marker', 'color': '#dbdb40', 'size': 0.04 if v else 0.05, 'line_height': 1.0,
                          'align': 'left'})
        size_c = env.cH(st['size'] if not isinstance(st['size'], dict) else 0.05)
        pitch = float(L.get('pitch', 1.35)) * size_c
        side = L.get('side', 'auto')
        if side == 'auto':
            fb = faces_at(env, f0)
            side = 'left' if (fb and (fb[0][0] + fb[0][2]) / 2 > env.W / 2) else 'right'
        x0 = env.cW(L.get('x', (0.5 if v else 0.55) if side == 'right' else (0.08 if v else 0.09)))
        y0 = env.cH(L.get('y', 0.2 if v else 0.15))
        x_max = env.safe_c[2] - 0.01 * env.W
        width = max(env.W * 0.2, min(env.W * (0.38 if v else 0.36), x_max - x0))
        cps_default = float(L.get('cps', 18))
        indent = env.cW(L.get('correct_indent', 0.03))
        lines, marks = [], []
        cursor = f0
        row = 0
        for it in L.get('items', []):
            op = it.get('op', 'write')
            start = it.get('f')
            if start is None and it.get('t') is not None:
                start = int(round(float(it['t']) * fps))
            if op in ('write', 'correct'):
                text = str(it.get('text', ''))
                if start is None:
                    start = cursor + (int(round(0.6 * fps)) if op == 'correct' else int(round(0.7 * fps)) if lines else 0)
                cps = float(it.get('cps', 26.0 if re.fullmatch(r'[\d\s.,+\-−=%₽$€×x:/]+', text) else cps_default))
                ind = indent if op == 'correct' else env.cW(it.get('indent', 0.0)) if it.get('indent') else 0.0
                b = layout_words(tokenize(text), font_of(st), size_c, max_width=width - ind, max_lines=1, align='left',
                                 line_height=1.0, min_size=size_c * 0.5)
                n = len(text)
                end = start + int(math.ceil(n / cps * fps))
                lines.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=x0 + ind, oy=y0 + row * pitch,
                                  f=start, end=end, cps=cps, clamp=False))
                row += 1
                cursor = end
            elif op == 'strike':
                i = int(it.get('i', len(lines) - 1))
                if not lines:
                    continue
                i = max(-len(lines), min(i, len(lines) - 1))
                if start is None:
                    start = lines[i]['end'] + int(round(0.3 * fps))
                n = max(1, int(round(float(it.get('dur', L.get('strike_dur', 0.3))) * fps)))
                marks.append(dict(op='strike', i=i % len(lines), f=start, n=n))
                cursor = start + n
            elif op == 'arrow':
                if len(lines) < 2:
                    continue
                a = int(it.get('from_i', len(lines) - 2)) % len(lines)
                b = int(it.get('to_i', len(lines) - 1)) % len(lines)
                if start is None:
                    start = cursor + int(round(0.15 * fps))
                n = max(1, int(round(float(it.get('dur', L.get('arrow_dur', 0.5))) * fps)))
                marks.append(dict(op='arrow', a=a, b=b, f=start, n=n))
                cursor = start + n
            elif op == 'punch':
                text = str(it.get('text', ''))
                if start is None:
                    start = cursor + int(round(0.4 * fps))
                sc = float(it.get('scale', 2.5))
                b = layout_words(tokenize(text), font_of(st), size_c * sc, max_width=env.safe_c[2] - env.safe_c[0],
                                 max_lines=1, align='left')
                if it.get('pos'):
                    ox, oy = block_origin(b, env.cW(it['pos'][0]), env.cH(it['pos'][1]))
                else:
                    ox, oy = x0, y0 + (row + 0.4) * pitch
                n_chars = max(1, len(text))
                cps = n_chars / max(0.05, float(it.get('dur', 0.27)))
                lines.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=ox, oy=oy, f=start,
                                  end=start + int(math.ceil(n_chars / cps * fps)), cps=cps, clamp=True, punch=True))
                cursor = lines[-1]['end']
        return dict(lines=lines, marks=marks, f0=f0, f1=f1, col=to_rgba(st.get('color', '#dbdb40')), size=size_c,
                    seed=env.seed)

    @classmethod
    def draw(cls, L, env, plan, cv):
        f, s = env.f, env.s
        out = parse_anim(L.get('anim_out', 'cut'), 'cut', env.fps)
        stx = element_state(None, out, f, plan['f0'], plan['f1'], env)
        if stx is None:
            return
        for ln in plan['lines']:
            if f < ln['f']:
                continue
            st = St().compose(stx)
            st.reveal = max(1.0, (f - ln['f'] + 1) * ln['cps'] / env.fps)
            if st.reveal >= len(' '.join(w.text for w in ln['block'].words)):
                st.reveal = None
            _draw_el(cv, env, ln, st)
        col = plan['col']
        for mk in plan['marks']:
            if f < mk['f']:
                continue
            p = min(1.0, (f - mk['f'] + 1) / float(mk['n']))
            if mk['op'] == 'strike':
                ln = plan['lines'][mk['i']]
                b = ln['block']
                y = (ln['oy'] + b.cap * 0.55) * s
                xa, xb = (ln['ox'] - 0.05 * b.size) * s, (ln['ox'] + b.width + 0.05 * b.size) * s
                n = 12
                xs = np.linspace(xa, xb, n)
                ys = y + np.array([math.sin(i * 1.7 + plan['seed']) for i in range(n)]) * 0.025 * b.size * s
                spr = stroke_sprite(np.stack([xs, ys], 1), max(2.0, 0.1 * b.size * s), col, progress=p)
                cv.place(spr, 0, 0, stx)
            elif mk['op'] == 'arrow':
                la, lb = plan['lines'][mk['a']], plan['lines'][mk['b']]
                pa = ((la['ox'] + la['block'].width + 0.25 * la['block'].size) * s, (la['oy'] + la['block'].cap * 0.5) * s)
                pb = ((lb['ox'] + lb['block'].width + 0.25 * lb['block'].size) * s, (lb['oy'] + lb['block'].cap * 0.5) * s)
                w0 = max(2.0, 0.09 * plan['size'] * s)
                bulge = min(max(pa[0], pb[0]) + 0.9 * plan['size'] * s, env.safe[2] - 2 * w0 - 2)
                bulge = max(bulge, max(pa[0], pb[0]) + 0.15 * plan['size'] * s)
                ctrl = (2 * bulge - (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2)
                pts = bezier(pa, ctrl, pb, 32)
                pts[:, 0] = np.minimum(pts[:, 0], env.safe[2] - w0 - 1)
                w = w0
                cv.place(stroke_sprite(pts, w, col, progress=p), 0, 0, stx)
                if p >= 0.9:
                    d = pts[-1] - pts[-4]
                    d = d / (np.linalg.norm(d) + 1e-9)
                    nrm = np.array([-d[1], d[0]])
                    L_ = 0.32 * plan['size'] * s
                    tip = pts[-1]
                    for sg in (1, -1):
                        cv.place(stroke_sprite([tip - d * L_ + sg * nrm * L_ * 0.6, tip], w, col), 0, 0, stx)


# ---------------------------------------------------------------------------- repeat (typographic loops)
@register
class Repeat(Kind):
    """type.repeat — one word multiplied into a pattern living in a seamless loop: echo_stack | rows | wave |
    radial | tunnel | recursive."""
    name = 'repeat'
    default_dur = 3.0

    @classmethod
    def render_scale_for(cls, L):
        return 0.5 if L.get('layout') == 'tunnel' else 1.0

    @classmethod
    def plan(cls, L, env):
        v = env.vertical
        layout = L.get('layout', 'echo_stack')
        texts = L.get('text', 'REPEAT')
        texts = texts if isinstance(texts, list) else [texts]
        size_default = {'echo_stack': {'fit_width': 0.8, 'max': 0.1} if v else 0.1,
                        'rows': 0.075 if v else 0.09, 'wave': 0.045 if v else 0.047,
                        'radial': {'fit_width': 0.36, 'max': 0.06} if v else 0.09,
                        'tunnel': {'fit_width': 0.6, 'max': 0.09} if v else 0.16, 'recursive': 0.59}.get(layout, 0.1)
        st = style_of(L, {'font': 'grotesk_condensed_black', 'caps': True, 'color': '#ffffff', 'size': size_default,
                          'line_height': 1.0})
        x_c = env.cW(L.get('x', 0.47 if v else 0.5))
        y_c = env.cH(L.get('y', 0.48 if v else 0.49))
        maxw = env.safe_w_center(x_c)
        blocks = [make_block(tokenize(t), st, env, max_width=maxw if layout in ('echo_stack', 'tunnel') else None, max_lines=1)
                  for t in texts]
        ts = [resolve_style(st, env, b.size) for b in blocks]
        loop = float(L.get('loop', {'echo_stack': 2.8, 'rows': 2.0, 'wave': 2.0, 'radial': 3.0, 'tunnel': 2.0,
                                    'recursive': 2.0}.get(layout, 2.0)))
        return dict(layout=layout, blocks=blocks, ts=ts, st=st, x=x_c, y=y_c, loop=loop,
                    col2=to_rgba(L.get('color2', '#3fe0ff')), bg=L.get('bg'))

    @classmethod
    def draw(cls, L, env, plan, cv):
        f0, f1 = cls.span(L, env.fps)
        t = (env.f - f0) / env.fps
        s = env.s
        if plan['bg']:
            cv.fill(plan['bg'], 1.0)
        lay = plan['layout']
        b, ts = plan['blocks'][0], plan['ts'][0]
        spr = text_sprite(b, ts, env)
        if spr is None:
            return
        x_c, y_c = plan['x'] * s, plan['y'] * s
        loop = plan['loop'] if L.get('loop_mode', 'loop') == 'loop' else 1e9
        tl = t % loop
        if lay == 'echo_stack':
            copies = int(L.get('copies', 6))
            pitch = float(L.get('pitch', 0.85)) * (b.cap + b.desc) * s
            g, hold, r = float(L.get('grow', 0.9)), float(L.get('hold', 1.1)), float(L.get('retract', 0.8))
            if tl < g:
                p = ease(tl / g, 'outCubic')
            elif tl < g + hold:
                p = 1.0
            else:
                p = 1.0 - ease(min(1.0, (tl - g - hold) / r), 'inCubic')
            key = ('echo', b.key, ts.key, s)
            cp = _SPRITES.get(key)
            if cp is None:
                rg = spr.rgba.copy()
                h = rg.shape[0]
                lo, hi = L.get('inner_gradient', [0.2, 1.0])
                gm = np.linspace(lo, hi, h, dtype=np.float32) * float(L.get('opacity', 0.6))
                for c in range(4):
                    rg[..., c] *= gm[:, None]
                cp = Sprite(rg, spr.x, spr.y)
                _SPRITES.put(key, cp, rg.nbytes)
            shift = copies * pitch * p / 2.0
            ox, oy = x_c - b.width * s / 2, y_c - b.height * s / 2 - shift
            for i in range(copies, 0, -1):
                cv.place(cp, ox, oy + i * pitch * p, None)
            cv.place(spr, ox, oy, None)
        elif lay in ('rows', 'recursive'):
            texts = L.get('text') if isinstance(L.get('text'), list) else [L.get('text', 'REPEAT')]
            if lay == 'recursive':
                steps = L.get('steps', [1, 3, 8, 20, 40])
                k = min(len(steps) - 1, int(tl / float(L.get('step', 0.25))))
                n_rows = int(steps[k])
                zone_h = env.oh * 0.9
                size_c = min(zone_h / n_rows / 1.02, env.oh * 0.59) / s
                pitch = zone_h / n_rows
                y_top = env.oh * 0.05 + (pitch - size_c * s * 1.02) / 2
                drift = 0.0
                sizes = [size_c] * len(texts)
            else:
                pitch = env.o(env.cH(L.get('pitch', 0.1)))
                n_rows = int(math.ceil(env.oh / pitch)) + 1
                y_top = -pitch * 0.3
                drift = env.o(env.cW(L.get('drift', 0.04)))
                sizes = [b.size for b in plan['blocks']]
            gap = float(L.get('gap', 0.5))
            strips = []
            for ti, (txt, sz) in enumerate(zip(texts, sizes)):
                key = ('strip', txt, plan['st'].get('font'), round(sz, 2), env.s, env.ow, gap)
                strip = _SPRITES.get(key)
                if strip is None:
                    tk = tokenize(txt)
                    ref = font_of(plan['st'])
                    caps = bool(plan['st'].get('caps'))
                    unit = text_length(' '.join(t.upper() if caps else t for t in tk), ref, sz) + gap * sz
                    reps = int(math.ceil((env.W * 2 + unit) / max(unit, 1.0))) + 1
                    words = tk * reps
                    if unit > env.W * 2:                       # gigantic: only the characters that can be seen
                        full = ' '.join(tk)
                        offs = char_offsets(full.upper() if caps else full, ref, sz)
                        cut = next((j for j, o in enumerate(offs) if o > env.W * 2.2), len(full))
                        words = tokenize(full[:cut])
                    bb = layout_words(words, ref, sz, align='left', caps=caps, word_spacing=gap - font_metrics(ref)['space'] + 0.25)
                    sp = text_sprite(bb, resolve_style(plan['st'], env, sz), env, cache=False)
                    strip = (sp, unit * s)
                    _SPRITES.put(key, strip, sp.rgba.nbytes if sp is not None else 0)
                strips.append(strip)
            for r in range(n_rows):
                sp, period = strips[r % len(strips)]
                if sp is None:
                    continue
                half = period / 2 if period < env.ow else 0.3 * env.ow       # giant rows: shift by part of the frame
                off = (r % 2) * half + (drift * t * (1 if r % 2 == 0 else -1) if L.get('alternate', True) else drift * t)
                jitter = 0.0
                if L.get('boil', lay == 'rows'):
                    jitter = (_rnd(env.seed, r, int(env.f // 2)) - 0.5) * 0.04 * sizes[r % len(sizes)] * s
                y = y_top + r * pitch + jitter
                x = -(off % period) - (period if period < env.ow else 0)
                cv.blit(sp.rgba, int(round(x + sp.x)), int(round(y + sp.y)))
        elif lay == 'wave':
            rows = int(L.get('rows', 7))
            pitch = env.o(env.cH(L.get('pitch', 0.078)))
            amp = float(L.get('amp', 0.4)) * b.size * s
            per = float(L.get('period', 1.5))
            wl = float(L.get('wavelength', 6))
            tot = (rows - 1) * pitch
            text = b.words[0].text if b.words else ''
            offs = char_offsets(' '.join(w.text for w in b.words), b.ref, b.size, b.tracking)
            full = ' '.join(w.text for w in b.words)
            cw = (b.width / max(1, len(full)))
            cols = [plan['ts'][0].fill, plan['col2']]
            for r in range(rows):
                y = y_c - tot / 2 + r * pitch
                n_rep = int(math.ceil(env.ow / ((b.width + 0.5 * b.size) * s))) + 1
                x_start = (env.ow - n_rep * (b.width + 0.5 * b.size) * s) / 2
                for rep in range(n_rep):
                    xb = x_start + rep * (b.width + 0.5 * b.size) * s
                    for j, ch in enumerate(full):
                        if ch.isspace():
                            continue
                        gi = rep * len(full) + j
                        ph = 2 * math.pi * (gi / wl - tl / per) + r * 0.6
                        dy = amp * math.sin(ph)
                        cmix = 0.5 + 0.5 * math.sin(ph * 0.5)
                        col = _mix(cols[0], cols[1], cmix)
                        g = raster(ch, b.ref, b.size * s, 0.0, 0.0)
                        cv.blit_mask(g.a, int(round(xb + offs[j] * s + g.x0)), int(round(y + dy + g.y0 + b.cap * s / 2)), col)
        elif lay == 'radial':
            n = int(L.get('copies', 5))
            spin = float(L.get('spin', 90.0))
            fan = 0.55 + 0.45 * math.cos(2 * math.pi * tl / loop)
            cx, cy = env.ow / 2, env.oh / 2
            r0 = env.o(env.cH(L.get('r0', 0.04)))
            for i in range(n):
                ang = spin * t + 360.0 / n * i * fan
                st = St()
                st.rot = ang
                ox = cx + r0 - spr.x
                oy = cy - (b.cap / 2) * s - b.cap * s / 2
                cv.place(spr, ox, oy, st, pivot=(cx, cy))
        elif lay == 'tunnel':
            n = int(L.get('copies', 12))
            g = min(1.0, tl / float(L.get('grow', 0.75)))
            e = ease(g, 'outCubic')
            ckey = ('tunnel', b.key, ts.key, env.s, env.ow, env.oh, n, repr(L.get('gradient')), x_c, y_c)
            if g >= 1.0:
                done = _SPRITES.get(ckey)
                if done is not None:
                    cv.blit(done[0], done[1], done[2])
                    return
                sub = Canvas(env.ow, env.oh)
            else:
                sub = cv
            stops = to_rgba_list(L.get('gradient'), ['#ffe14a', '#3fe0ff'])
            ts_o = resolve_style(dict(plan['st'], stroke={'w': 0.04}), env, b.size)
            for i in range(n, 0, -1):
                k = 1.0 + i * 0.32 * e
                col = _mix(stops[0], stops[-1], i / float(n))
                ts_i = resolve_style(dict(plan['st'], color=col, stroke={'w': 0.035, 'color': col}), env, b.size)
                sp = text_sprite(b, ts_i, env, outline=True)
                st = St()
                st.sx = st.sy = k
                st.alpha = (1 - i / (n + 1.0)) * e
                ox, oy = x_c - b.width * s / 2, y_c - b.height * s / 2
                sub.place(sp, ox, oy, st, (x_c, y_c))
            sub.place(spr, x_c - b.width * s / 2, y_c - b.height * s / 2, None)
            if sub is not cv and sub.bbox is not None:
                x0, y0, x1, y1 = sub.bbox
                rg = sub.buf[y0:y1, x0:x1].copy()
                _SPRITES.put(ckey, (rg, x0, y0), rg.nbytes)
                cv.blit(rg, x0, y0)


# ---------------------------------------------------------------------------- text behind the subject
def subject_mask(env, bbox=None, region=False):
    """Person/subject mask (oh, ow) 0..1 for frame env.f: ctx person_mask(f) | mask | ed_video.person_mask(frame).
    Probability maps are turned into a crisp matte (mask_levels, smoothstep) and feathered; with bbox only that region
    (plus the feather margin) is processed."""
    ctx = env.ctx
    m = None
    try:
        cb = ctx.get('person_mask') or ctx.get('mask_fn')
        if callable(cb):
            m = cb(env.f)
        elif ctx.get('mask') is not None:
            m = ctx['mask']
        elif ctx.get('frame') is not None:
            import sys
            if HERE not in sys.path:
                sys.path.insert(0, HERE)
            import ed_video as V
            fr = ctx['frame']
            u8 = (np.clip(fr, 0, 1) * 255).astype(np.uint8) if fr.dtype != np.uint8 else fr
            m = V.person_mask(u8)
    except Exception:
        m = None
    if m is None:
        return None
    m = np.asarray(m, np.float32)
    if m.ndim == 3:
        m = m[..., 0]
    if m.size and m.max() > 1.5:
        m = m / 255.0
    fe = float(env.layer.get('feather', 1.5)) * env.s
    mg = int(3 * fe) + 2
    if bbox is not None:
        x0, y0 = max(0, int(bbox[0]) - mg), max(0, int(bbox[1]) - mg)
        x1, y1 = min(env.ow, int(bbox[2]) + mg), min(env.oh, int(bbox[3]) + mg)
    else:
        x0, y0, x1, y1 = 0, 0, env.ow, env.oh
    if m.shape != (env.oh, env.ow):
        # sample only the needed region straight from the (usually low-res) probability map
        sx, sy = m.shape[1] / float(env.ow), m.shape[0] / float(env.oh)
        M = np.float64([[sx, 0, x0 * sx + 0.5 * sx - 0.5], [0, sy, y0 * sy + 0.5 * sy - 0.5]])
        sub = cv2.warpAffine(m, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                             borderMode=cv2.BORDER_REPLICATE)
    else:
        sub = m[y0:y1, x0:x1]
    lo, hi = env.layer.get('mask_levels', [0.3, 0.7])          # probability map -> crisp matte (smoothstep)
    if hi > lo:
        sub = np.clip((sub - lo) / (hi - lo), 0.0, 1.0)
        sub = sub * sub * (3.0 - 2.0 * sub)
    if fe > 0.3:
        sub = cv2.GaussianBlur(sub, (0, 0), fe)
    sub = np.clip(sub, 0.0, 1.0).astype(np.float32)
    if region:
        return sub, x0, y0
    if (x0, y0, x1, y1) == (0, 0, env.ow, env.oh):
        return sub
    full = np.zeros((env.oh, env.ow), np.float32)
    full[y0:y1, x0:x1] = sub
    return full


@register
class BehindSubject(Kind):
    """type.behind_subject — the text sits between the background and the person (mask from ctx): giant word behind
    the head, side blocks (above/below the head in 9:16), a wall of rows or a ring of the word; burst entrance."""
    name = 'behind_subject'
    default_dur = 2.5

    @classmethod
    def plan(cls, L, env):
        v = env.vertical
        layout = L.get('layout', 'giant')
        lines = L.get('lines') or tokenize(L.get('text', 'TEXT'))
        if isinstance(lines, str):
            lines = [lines]
        x_c = env.cW(L.get('x', 0.47 if v else 0.5))
        els = []
        palette = to_rgba_list(L.get('palette'), ['#2f6bff', '#ff3b30', '#34c759', '#f2ede4'])
        if layout == 'giant':
            st = style_of(L, {'font': 'grotesk_condensed_black', 'caps': True, 'color': '#ffffff',
                              'size': {'fit_width': 0.88 if v else 0.92, 'max': 0.32 if v else 0.6}, 'line_height': 0.9})
            text = ' '.join(lines) if isinstance(lines, list) else str(lines)
            b = make_block(tokenize(text), st, env, max_width=env.safe_w_center(x_c) / 1.1,
                           max_lines=int(L.get('max_lines', 2 if v else 1)))
            ox, oy = block_origin(b, x_c, env.cH(L.get('y', 0.33 if v else 0.4)))
            els.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=ox, oy=oy))
        elif layout == 'sides':
            st = style_of(L, {'font': 'display', 'caps': True, 'size': 0.06 if v else 0.13, 'line_height': 1.0})
            half = (len(lines) + 1) // 2
            groups = [lines[:half], lines[half:]]
            for gi, grp in enumerate(groups):
                if not grp:
                    continue
                if v:
                    b = make_block(grp, st, env, max_width=env.safe_w_center(x_c) / 1.1, max_lines=3)
                    y = env.cH(0.21 if gi == 0 else 0.71)
                    ox, oy = block_origin(b, x_c, y)
                else:
                    st2 = dict(st, align='right' if gi == 0 else 'left')
                    b = make_block(grp, st2, env, max_width=env.W * 0.33, max_lines=3)
                    ox, oy = block_origin(b, env.W * (0.35 if gi == 0 else 0.62), env.cH(0.45), 'right' if gi == 0 else 'left')
                cols = {j: palette[(j + gi * 2) % len(palette)] for j in range(len(b.words))}
                els.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=ox, oy=oy, cols=cols))
        elif layout == 'wall':
            st = style_of(L, {'font': 'grotesk_condensed_black', 'caps': True, 'size': 0.075 if v else 0.13, 'color': '#ffffff'})
            text = ' '.join(lines)
            b1 = make_block(tokenize(text), st, env)
            reps = int(env.W / max(1.0, b1.width + 0.6 * b1.size)) + 3
            toks = (tokenize(text) * reps)
            pitch = b1.size * 1.02
            n_rows = int(math.ceil(env.H / pitch)) + 1
            for r in range(n_rows):
                inv = r % 2 == 1
                st_r = dict(st, color='#111111' if inv else '#ffffff', align='left', word_spacing=0.3,
                            box={'color': '#ffffff' if inv else '#111111', 'alpha': 1.0, 'pad': [0.15, 0.06], 'radius': 0.0,
                                 'mode': 'word'})
                b = layout_words(toks, font_of(st_r), b1.size, align='left', caps=True, word_spacing=0.3)
                period = (b.width + b1.size * 0.3 + b1.size * 0.25) / reps
                els.append(dict(block=b, ts=resolve_style(st_r, env, b.size), ox=-period * (0.3 + 0.5 * (r % 2)),
                                oy=r * pitch - 0.2 * pitch, clamp=False))
        elif layout == 'ring':
            st = style_of(L, {'font': 'grotesk_condensed_black', 'caps': True, 'size': 0.035 if v else 0.05, 'color': '#ffffff'})
            b = make_block(tokenize(lines[0] if lines else 'RING'), st, env)
            els.append(dict(block=b, ts=resolve_style(st, env, b.size), ox=0, oy=0, ring=True, clamp=False))
        a_in = parse_anim(L.get('anim_in', 'burst' if layout in ('giant', 'sides') else 'fade'), 'burst', env.fps)
        a_out = parse_anim(L.get('anim_out', 'cut'), 'cut', env.fps)
        for el in els:
            el['grow'] = 1.1 if a_in.get('type') == 'burst' else 1.0
        return dict(els=els, a_in=a_in, a_out=a_out, layout=layout)

    @classmethod
    def draw(cls, L, env, plan, cv):
        f0, f1 = cls.span(L, env.fps)
        f = env.f
        a_in, a_out = plan['a_in'], plan['a_out']
        st0 = element_state(a_in, a_out, f, f0, f1, env)
        if st0 is None:
            return
        fb = faces_at(env, f)
        if plan['layout'] == 'ring':
            if fb:
                bx = fb[0]
                cx, cy = (bx[0] + bx[2]) / 2 * env.s, (bx[1] + bx[3]) / 2 * env.s
                rad = 0.75 * max(bx[2] - bx[0], bx[3] - bx[1]) * env.s
            else:
                m = subject_mask(env)
                ys, xs = (np.nonzero(m[::4, ::4] > 0.5) if m is not None else ([], []))
                if len(xs) == 0:
                    cy, cx, rad = env.oh * 0.45, env.ow * 0.5, env.oh * 0.14
                else:
                    cx, cy = float(np.mean(xs)) * 4, float(np.mean(ys)) * 4
                    rad = math.sqrt(len(xs) * 16 / math.pi) * 0.85
            rad += env.o(env.cH(L.get('gap', 0.02)))
            el = plan['els'][0]
            spr = text_sprite(el['block'], el['ts'], env)
            n = int(L.get('copies', max(8, min(40, int(2 * math.pi * rad / max(1.0, el['block'].cap * env.s * 1.6))))))
            spin = float(L.get('spin', 20.0))
            for i in range(n):
                st = St().compose(st0)
                st.rot = spin * env.t + 360.0 / n * i
                st.sx = st.sy = 1.0
                ox = cx + rad - spr.x
                oy = cy - el['block'].cap * env.s / 2
                cv.place(spr, ox, oy, st, pivot=(cx, cy))
            return
        for el in plan['els']:
            st = St().compose(st0)
            piv = None
            if a_in.get('type') == 'burst' and fb:
                bx = fb[0]
                piv = ((bx[0] + bx[2]) / 2 * env.s, (bx[1] + bx[3]) / 2 * env.s)
            spr = text_sprite(el['block'], el['ts'], env, cols=el.get('cols'))
            if spr is None:
                continue
            ox, oy = (_el_origin(el, env, spr, el.get('grow', 1.0)) if el.get('clamp', True) else
                      (el['ox'] * env.s, el['oy'] * env.s))
            if el.get('clamp', True):
                tb = _tight(spr)
                cap_scale(st, spr, ox, oy, piv or (ox + el['block'].width * env.s / 2.0, oy + (tb[1] + tb[3]) / 2.0), env)
            draw_text_el(cv, env, el['block'], el['ts'], ox, oy, st, cols=el.get('cols'), pivot=piv)


# ---------------------------------------------------------------------------- tracks for callouts
def _pt(v, env):
    """Point/box value -> (cx, cy, x0, y0, x1, y1) in output px. Fractions (≤ 1) or canvas px; dict x,y(,w,h)."""
    if v is None:
        return None
    if isinstance(v, dict):
        if 'x0' in v:
            nums = [float(v['x0']), float(v['y0']), float(v['x1']), float(v['y1'])]
        elif 'w' in v:
            nums = [float(v['x']), float(v['y']), float(v['x']) + float(v['w']), float(v['y']) + float(v['h'])]
        else:
            nums = [float(v.get('x', 0.5)), float(v.get('y', 0.5))]
    else:
        nums = [float(a) for a in v]
    frac = max(abs(a) for a in nums) <= 1.0
    sx, sy = (env.ow, env.oh) if frac else (env.s, env.s)
    if len(nums) >= 4:
        x0, y0, x1, y1 = nums[0] * sx, nums[1] * sy, nums[2] * sx, nums[3] * sy
        return ((x0 + x1) / 2, (y0 + y1) / 2, x0, y0, x1, y1)
    x, y = nums[0] * sx, nums[1] * sy
    return (x, y, x, y, x, y)


def track_fn(spec, env):
    """Target spec -> f -> (cx, cy, x0, y0, x1, y1) output px or None. spec: [x, y] | [x0,y0,x1,y1] |
    {"track": name} (ctx['tracks'][name] callable or keyframes; "face" uses ctx face) | {"keys": [[f, x, y(, x1, y1)]]}."""
    ctx = env.ctx
    src = spec
    if isinstance(spec, dict) and 'track' in spec:
        name = spec['track']
        src = (ctx.get('tracks') or {}).get(name)
        if src is None and name in ('face', 'person'):
            src = ctx.get('face', ctx.get('faces'))
        if src is None:
            return lambda f: None
    if isinstance(src, dict) and 'keys' in src:
        src = src['keys']
    if callable(src):
        def fn(f):
            try:
                r = src(f)
            except Exception:
                return None
            if isinstance(r, (list, tuple)) and r and isinstance(r[0], (list, tuple, dict)):
                r = r[0]
            return _pt(r, env) if r is not None else None
        return fn
    if isinstance(src, dict):
        keys = sorted((int(k), v) for k, v in src.items())
        src = [[k] + (list(v) if not isinstance(v, dict) else [v['x'], v['y']]) for k, v in keys]
    if isinstance(src, (list, tuple)) and src and isinstance(src[0], (list, tuple)):
        ks = np.array([[float(a) for a in k] for k in src], np.float64)
        frames = ks[:, 0]

        def fn(f):
            if len(ks) == 1:
                row = ks[0, 1:]
            else:
                row = np.array([np.interp(f, frames, ks[:, c]) for c in range(1, ks.shape[1])])
            return _pt(list(row), env)
        return fn
    p = _pt(src, env)
    return lambda f: p


# ---------------------------------------------------------------------------- callout
@register
class Callout(Kind):
    """gfx.callout — pin + elbow leader + plate label stuck to a tracked target (dot rigid, label lagging like a
    spring), or arrow / ring / brackets / spotlight / tag."""
    name = 'callout'
    default_dur = 2.5

    @classmethod
    def plan(cls, L, env):
        v = env.vertical
        fps = env.fps
        f0, f1 = cls.span(L, fps)
        fn = track_fn(L.get('target', [0.5, 0.5]), env)
        raw, last, lost, lost_at = {}, None, 0, None
        for f in range(f0 - 3, f1 + 4):
            r = fn(f)
            if r is None:
                lost += 1
                if lost > 6 and lost_at is None and f >= f0:
                    lost_at = f
                r = last
            else:
                lost = 0
            raw[f] = r
            last = r if r is not None else last
        first = next((raw[f] for f in range(f0, f1 + 1) if raw.get(f) is not None), None)
        if first is None:
            return dict(ok=False)
        for f in list(raw):
            if raw[f] is None:
                raw[f] = first
        dot, lag = {}, {}
        lag_n = max(1.0, float(env.fr25(L.get('lag', 3))))
        al = 1.0 - math.exp(-1.0 / lag_n)
        prev = None
        for f in range(f0 - 3, f1 + 4):
            nb = [raw[g] for g in (f - 1, f, f + 1) if g in raw]
            dot[f] = tuple(float(np.mean([p[c] for p in nb])) for c in range(6))
            if prev is None:
                prev = dot[f]
            else:
                prev = tuple(prev[c] + (dot[f][c] - prev[c]) * al for c in range(6))
            lag[f] = prev
        # early exit near the frame edge or after a lost track
        fb = f1
        for f in range(f0, f1 + 1):
            cx0, cy0, x0, y0, x1, y1 = dot[f]
            if x0 < 0.05 * env.ow or x1 > 0.95 * env.ow or y0 < 0.05 * env.oh or y1 > 0.95 * env.oh:
                if f > f0 + env.fr25(18):
                    fb = min(fb, f + env.fr25(7))
                    break
        if lost_at is not None:
            fb = min(fb, lost_at)
        kind = L.get('variant', 'pin_label')
        sx0, sy0, sx1, sy1 = env.safe
        cx, cy = first[0], first[1]
        side = L.get('side', 'auto')
        sxn = (1 if (sx1 - cx) >= (cx - sx0) else -1) if side == 'auto' else (1 if side == 'right' else -1)
        syn = -1 if cy > (sy0 + sy1) / 2 else 1
        if isinstance(L.get('up'), bool):
            syn = -1 if L['up'] else 1
        st = style_of(L, {'font': 'inter:600', 'size': 0.025 if v else 0.032, 'color': '#111111', 'line_height': 1.12,
                          'align': 'left'})
        text = str(L.get('text', ''))
        plate = to_rgba(L.get('plate', '#ffffff'), L.get('plate_alpha', 0.92))
        accent = to_rgba(L.get('accent', L.get('dot_color', '#ffc400')))
        diag = env.o(env.cH(L.get('diag', 0.05)))
        shelf = env.o(env.cW(L.get('shelf', 0.08 if v else 0.11)))
        lab = None
        if text:
            size_c = env.cH(st['size'] if not isinstance(st['size'], dict) else 0.03)
            s_ = env.s
            d_c = diag / s_ / math.sqrt(2)
            sh_min = 0.03 * env.W
            cx_c = cx / s_
            room = {1: env.safe_c[2] - (cx_c + d_c), -1: (cx_c - d_c) - env.safe_c[0]}
            if side == 'auto':
                sxn = 1 if room[1] >= room[-1] else -1
            pad = 0.5 * size_c
            max_chars = 18 if v else 24
            # the label takes the room on its side: wrap to 2 lines, then shorten the shelf, then shrink a little
            avail = room[sxn] - shelf / s_ - 2 * pad
            want = min(size_c * 0.56 * max_chars, max(avail, 0))
            b = layout_words(tokenize(text), font_of(st), size_c, max_width=max(want, size_c * 2.5), max_lines=2,
                             align='left', line_height=1.12, min_size=size_c * 0.75)
            need = b.width + 2 * pad
            if need > room[sxn] - shelf / s_:
                shelf = max(sh_min, (room[sxn] - need)) * s_
                if need > room[sxn] - shelf / s_:
                    b = layout_words(tokenize(text), font_of(st), size_c,
                                     max_width=max(size_c * 2.0, room[sxn] - shelf / s_ - 2 * pad), max_lines=3,
                                     align='left', line_height=1.12, min_size=size_c * 0.6)
            lab = dict(block=b, ts=resolve_style(st, env, b.size))
        return dict(ok=True, dot=dot, lag=lag, fb=fb, kind=kind, sx=sxn, sy=syn, lab=lab, plate=plate, accent=accent,
                    diag=diag, shelf=shelf, f0=f0, f1=f1)

    @classmethod
    def draw(cls, L, env, plan, cv):
        if not plan.get('ok'):
            return
        f = env.f
        f0, fb = plan['f0'], plan['fb']
        if f > fb or f < f0:
            return
        F = env.fr25
        s = env.s
        v = env.vertical
        k = f - f0
        out = parse_anim(L.get('anim_out', 'reverse'), 'reverse', env.fps)
        n_out = F(7) if out.get('type') == 'reverse' else max(1, anim_frames(out, env.fps) or F(4))
        j = f - (fb - n_out + 1)
        u = (j + 1) / (n_out + 1.0) if j >= 0 else 0.0
        gal = 1.0 - u if (j >= 0 and out.get('type') != 'reverse') else 1.0
        rev = j >= 0 and out.get('type') == 'reverse'
        cx, cy, x0, y0, x1, y1 = plan['dot'][f]
        lx, ly = plan['lag'][f][0], plan['lag'][f][1]
        kind = plan['kind']
        acc = plan['accent']
        stA = St()
        stA.alpha = gal
        line_w = max(1.5, env.o(env.cH(0.003)))
        if kind == 'pin_label':
            n_dot, n_line, n_wipe, n_text = F(4), F(7), F(7), F(4)
            a_line = n_dot - 1
            a_wipe = a_line + n_line
            a_text = a_wipe + n_wipe - 2
            pd = min(1.0, (k + 1) / n_dot)
            p_line = ease(_clamp((k - a_line + 1) / n_line, 0, 1), 'inOutCubic')
            p_wipe = ease(_clamp((k - a_wipe + 1) / n_wipe, 0, 1), 'outCubic')
            p_text = _clamp((k - a_text + 1) / n_text, 0, 1)
            dot_a = 1.0
            if rev:
                p_text *= 1 - _clamp(u / 0.3, 0, 1)
                p_wipe *= 1 - ease(_clamp((u - 0.15) / 0.4, 0, 1), 'inCubic')
                p_line *= 1 - ease(_clamp((u - 0.4) / 0.4, 0, 1), 'inCubic')
                dot_a = 1 - _clamp((u - 0.7) / 0.3, 0, 1)
            sc = _keys_scale([0.0, 1.2, 1.0], min(1.0, k / max(1.0, n_dot - 1)), {'peak': 0.6, 'ease': 'outQuad', 'ease2': 'outBack'})
            r = env.o(env.cH(0.0105 if v else 0.014)) / 2 * max(sc, 0.0)
            st_d = St()
            st_d.alpha = gal * dot_a
            if k < F(10) and not rev:
                e = ease((k + 1) / F(10), 'outCubic')
                ring_r = env.o(env.cH(0.0105 if v else 0.014)) / 2 * (1 + 1.5 * e)
                st_r = St()
                st_r.alpha = 0.6 * (1 - e) * gal
                cv.place(disc_sprite(cx, cy, ring_r, acc, ring=line_w), 0, 0, st_r)
            if r > 0.3:
                cv.place(disc_sprite(cx, cy, r + 0.12 * line_w * 2, (0, 0, 0, 0.3)), 0, 0, st_d)
                cv.place(disc_sprite(cx, cy, r, acc), 0, 0, st_d)
            sxn, syn = plan['sx'], plan['sy']
            d = plan['diag'] / math.sqrt(2)
            P1 = (lx + sxn * d, ly + syn * d)
            P2 = (P1[0] + sxn * plan['shelf'], P1[1])
            if p_line > 0:
                spr = stroke_sprite([(cx, cy), P1, P2], line_w, acc, progress=p_line)
                cv.place(spr, 0, 0, stA)
            lab = plan['lab']
            if lab is not None and p_wipe > 0:
                b = lab['block']
                padx, pady = 0.5 * b.size * s, 0.3 * b.size * s
                pw, ph = b.width * s + 2 * padx, b.height * s + 2 * pady
                if sxn > 0:
                    rx0 = P2[0]
                else:
                    rx0 = P2[0] - pw
                ry0 = P2[1] - ph / 2
                ry0 = _clamp(ry0, env.safe[1], env.safe[3] - ph)
                rx0 = _clamp(rx0, env.safe[0], env.safe[2] - pw)
                ww = pw * p_wipe
                spr = rect_sprite(rx0 if sxn > 0 else rx0 + pw - ww, ry0, (rx0 + ww) if sxn > 0 else rx0 + pw, ry0 + ph,
                                  plan['plate'], 0.2 * b.size * s)
                cv.place(spr, 0, 0, stA)
                if p_text > 0:
                    st_t = St()
                    st_t.alpha = p_text * gal
                    tsp = text_sprite(b, lab['ts'], env)
                    cv.place(tsp, rx0 + padx, ry0 + pady, st_t)
        elif kind == 'ring':
            n = F(10)
            p = ease(min(1.0, (k + 1) / n), 'inOutCubic')
            if rev:
                p *= 1 - ease(u, 'inCubic')
            rx = (x1 - x0) / 2 * 1.25 + env.o(env.cH(0.015))
            ry = (y1 - y0) / 2 * 1.25 + env.o(env.cH(0.015))
            if rx < 2 or ry < 2:
                rx = ry = env.o(env.cH(0.06))
            th0 = math.radians(300)
            ext = math.radians(372 if L.get('style', 'vector') == 'marker' else 360)
            ths = th0 + np.linspace(0, ext, 90)
            pts = np.stack([cx + rx * np.sin(ths), cy - ry * np.cos(ths)], 1)
            col = to_rgba(L.get('color', '#e8323c' if L.get('style') == 'marker' else '#ffffff'))
            cv.place(stroke_sprite(pts, max(2.0, env.o(env.cH(0.006))), col, progress=p), 0, 0, stA)
        elif kind == 'brackets':
            n = F(6)
            e = ease(min(1.0, (k + 1) / n), 'outCubic')
            sc = 1.15 + (1.0 - 1.15) * e
            if rev:
                sc = 1.0 + 0.15 * ease(u, 'inCubic')
            pad = 0.03 * env.oh
            bx0, by0, bx1, by1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
            mx, my = (bx0 + bx1) / 2, (by0 + by1) / 2
            hw, hh = (bx1 - bx0) / 2 * sc, (by1 - by0) / 2 * sc
            arm = 0.18 * max(hw, hh) * 2
            w = max(2.0, env.o(env.cH(0.004)))
            col = to_rgba(L.get('color', '#ffffff'))
            st_b = St()
            st_b.alpha = min(1.0, (k + 1) / 2.0) * (1 - u if rev else 1.0) * gal
            for sxx in (-1, 1):
                for syy in (-1, 1):
                    c0 = (mx + sxx * hw, my + syy * hh)
                    pts = [(c0[0], c0[1] - syy * arm), c0, (c0[0] - sxx * arm, c0[1])]
                    cv.place(stroke_sprite(pts, w, col), 0, 0, st_b)
        elif kind == 'spotlight':
            n = F(8)
            p = ease(min(1.0, (k + 1) / n), 'outCubic') * (1 - u if j >= 0 else 1.0)
            rx = max(8.0, (x1 - x0) / 2 * 1.25)
            ry = max(8.0, (y1 - y0) / 2 * 1.25)
            if x1 - x0 < 2:
                rx = ry = env.o(env.cH(0.12))
            fe = env.o(env.cH(L.get('feather', 0.04)))
            q = 4
            hs, ws = env.oh // q + 1, env.ow // q + 1
            yy, xx = np.mgrid[0:hs, 0:ws].astype(np.float32) * q
            dd = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
            m = np.clip((dd - 1.0) * min(rx, ry) / max(1.0, fe) + 0.5, 0.0, 1.0)
            m = cv2.resize(m, (env.ow, env.oh), interpolation=cv2.INTER_LINEAR)
            cv.fill_mask_full(m, to_rgba(L.get('color', '#000000'), float(L.get('dim', 0.5)) * p))
        elif kind == 'arrow':
            n = F(10)
            p = ease(min(1.0, (k + 1) / n), 'inOutCubic')
            if rev:
                p *= 1 - ease(u, 'inCubic')
            sxn, syn = plan['sx'], plan['sy']
            length = env.o(env.cH(L.get('length', 0.16)))
            start = (cx + sxn * length * 0.8, cy + syn * length * 0.6)
            gap = env.o(env.cH(0.03))
            dv = np.array([cx - start[0], cy - start[1]])
            dist = np.linalg.norm(dv) + 1e-9
            end = (cx - dv[0] / dist * gap, cy - dv[1] / dist * gap)
            nrm = np.array([-dv[1], dv[0]]) / dist
            ctrl = ((start[0] + end[0]) / 2 + nrm[0] * dist * 0.25, (start[1] + end[1]) / 2 + nrm[1] * dist * 0.25)
            pts = bezier(start, ctrl, end, 40)
            w = max(2.0, env.o(env.cH(0.008)))
            col = to_rgba(L.get('color', '#ffffff'))
            cv.place(stroke_sprite(pts, w, col, progress=p), 0, 0, stA)
            if p > 0.97:
                dd = pts[-1] - pts[-3]
                dd = dd / (np.linalg.norm(dd) + 1e-9)
                nn = np.array([-dd[1], dd[0]])
                hs = 3.5 * w * min(1.0, (k - n + 3) / 2.0)
                tip = pts[-1] + dd * w * 0.5
                cv.place(poly_sprite([tip, tip - dd * hs + nn * hs * 0.6, tip - dd * hs - nn * hs * 0.6], col), 0, 0, stA)
            lab = plan['lab']
            if lab is not None and p > 0.3:
                b = lab['block']
                ts2 = resolve_style(dict(style_of(L, {}), color=L.get('label_color', '#ffffff'), shadow=True,
                                         font=L.get('font', 'inter:600'), size=b.size), env, b.size)
                tsp = text_sprite(b, ts2, env)
                st_t = St()
                st_t.alpha = min(1.0, (p - 0.3) / 0.4) * gal
                tx = start[0] - (b.width * s if sxn < 0 else 0) + sxn * 0.4 * b.size * s
                ty = start[1] - b.height * s / 2 + syn * 0.6 * b.size * s
                mg = 0.35 * b.size * s
                tx = _clamp(tx, env.safe[0] + mg, env.safe[2] - b.width * s - mg)
                ty = _clamp(ty, env.safe[1] + mg, env.safe[3] - b.height * s - mg)
                cv.place(tsp, tx, ty, st_t)
        elif kind == 'tag':
            lab = plan['lab']
            if lab is None:
                return
            b = lab['block']
            n = F(5)
            sc = _keys_scale([0.0, 1.15, 1.0], min(1.0, k / max(1.0, n - 1)), {'peak': 0.6, 'ease': 'outQuad', 'ease2': 'outBack'})
            if rev:
                sc *= 1 - ease(u, 'inBack') * 0.98
            padx, pady = 0.45 * b.size * s, 0.25 * b.size * s
            pw, ph = b.width * s + 2 * padx, b.height * s + 2 * pady
            tx = cx + plan['sx'] * env.ow * 0.04 - (pw if plan['sx'] < 0 else 0)
            ty = cy - ph - env.oh * 0.02
            tx = _clamp(tx, env.safe[0], env.safe[2] - pw)
            ty = _clamp(ty, env.safe[1], env.safe[3] - ph)
            col = to_rgba(L.get('plate', '#ffc400'))
            st_g = St()
            st_g.sx = st_g.sy = max(0.01, sc)
            st_g.rot = float(L.get('angle', -6.0))
            st_g.alpha = gal
            piv = (tx + pw / 2, ty + ph / 2)
            cv.place(rect_sprite(tx, ty, tx + pw, ty + ph, col, 0.2 * b.size * s), 0, 0, st_g, piv)
            cv.place(text_sprite(b, lab['ts'], env), tx + padx, ty + pady, st_g, piv)


# ---------------------------------------------------------------------------- counter / infographic
def format_number(v, locale='en', decimals=0, group=None, group_from=None, decimal=None, prefix='', suffix='',
                  sign='auto', minus='−', unit='', rounding='round'):
    """Number -> display string. ru: groups with U+202F from 5 digits ('12 500', '2500'), decimal comma, minus U+2212;
    en: '12,500', '3.5'. sign 'auto' (minus only) | 'always' (+/−). rounding round | floor | ceil."""
    ru = str(locale).lower().startswith('ru')
    group = (' ' if ru else ',') if group is None else group
    decimal = (',' if ru else '.') if decimal is None else decimal
    group_from = (5 if ru else 4) if group_from is None else int(group_from)
    d = max(0, int(decimals or 0))
    q = 10 ** d
    x = abs(float(v)) * q
    x = math.floor(x + 1e-9) if rounding == 'floor' else math.ceil(x - 1e-9) if rounding == 'ceil' else math.floor(x + 0.5)
    ip, fp = divmod(int(x), q)
    s = str(ip)
    if len(s) >= group_from:
        parts = []
        while len(s) > 3:
            parts.insert(0, s[-3:])
            s = s[:-3]
        parts.insert(0, s)
        s = group.join(parts)
    if d:
        s += decimal + str(fp).zfill(d)
    neg = float(v) < 0 and x > 0
    sg = minus if neg else ('+' if (sign in ('always', '+', True) and float(v) > 0) else '')
    return sg + str(prefix) + s + str(unit) + str(suffix)


def _abbrev(v, locale, mode):
    """-> (divisor, unit) for abbreviate='auto' (≥ 1e6) | 'k' (≥ 1e3) | False."""
    if not mode:
        return 1.0, ''
    av = abs(float(v))
    ru = str(locale).lower().startswith('ru')
    # language data: Russian number abbreviations (billion / million / thousand)
    if av >= 1e9:
        return 1e9, ' млрд' if ru else 'B'
    if av >= 1e6:
        return 1e6, ' млн' if ru else 'M'
    if mode == 'k' and av >= 1e3:
        return 1e3, ' тыс.' if ru else 'K'
    return 1.0, ''


def _decimals_of(v):
    s = repr(float(v))
    if 'e' in s:
        return 0
    frac = s.split('.')[1].rstrip('0') if '.' in s else ''
    return min(3, len(frac))


@register
class Counter(Kind):
    """gfx.counter — number counting to the exact final value (tabular digits, reserved width, landing pulse and
    accent colour, label fade), odometer roll, clock, and simple charts: bars, line, ring, progress."""
    name = 'counter'
    default_dur = 3.0

    @classmethod
    def plan(cls, L, env):
        v = env.vertical
        fps = env.fps
        f0, f1 = cls.span(L, fps)
        mode = L.get('mode', 'number')
        fmt = dict(L.get('format') or {})
        loc = fmt.get('locale', L.get('locale', 'en'))
        v0, v1 = float(L.get('from', 0.0)), float(L.get('to', 100.0))
        div, unit = _abbrev(max(abs(v0), abs(v1)), loc, fmt.get('abbreviate', 'auto'))
        dec = fmt.get('decimals', 'auto')
        if dec == 'auto':
            dec = 2 if div > 1 and _decimals_of(v1 / div) > 0 else _decimals_of(v1 / div)
            if div > 1:
                dec = min(2, max(1, _decimals_of(round(v1 / div, 2))))
        dur = float(L.get('dur', 1.2))
        n_in = env.fr25(5)
        if L.get('end_at') is not None:
            end_f = int(round(float(L['end_at']) * fps))
        elif L.get('end_f') is not None:
            end_f = int(L['end_f'])
        else:
            end_f = f0 + n_in + env.fr25(3) + int(round(dur * fps))
        start_f = end_f - int(round(dur * fps))
        st = style_of(L, {'font': 'inter:800', 'color': '#ffffff', 'size': {'fit_width': 0.72, 'max': 0.13} if v else 0.24,
                          'line_height': 1.0, 'shadow': {'dy': 0.025, 'blur': 0.05, 'alpha': 0.45}})
        ref = font_of(st)
        fkw = dict(locale=loc, decimals=dec, prefix=fmt.get('prefix', ''), suffix=fmt.get('suffix', ''),
                   sign=fmt.get('sign', 'auto'), unit=unit, group=fmt.get('group'), group_from=fmt.get('group_from'))
        s_end = format_number(v1 / div, **fkw)
        s_start = format_number(v0 / div, **fkw)
        if mode == 'clock':
            s_end = s_start = '00:00:00' if max(abs(v0), abs(v1)) >= 3600 else '00:00'
        pos = L.get('pos', [0.47 if v else 0.5, 0.42 if v else 0.46])
        x_c, y_c = env.cW(pos[0]), env.cH(pos[1])
        S, fit, smin = size_of(st, env, 0.2)

        def width_of(sz, s_):
            cell = max(text_length(dg, ref, sz) for dg in '0123456789')
            return sum(cell if ch.isdigit() else text_length(ch, ref, sz) for ch in s_)
        wmax = max(width_of(100.0, s_end), width_of(100.0, s_start)) / 100.0
        avail = min(fit or 1e9, env.safe_w_center(x_c) * 0.98)
        if mode in ('number', 'roll', 'clock'):
            S = min(S, avail / max(wmax, 1e-6))
        cell = max(text_length(dg, ref, S) for dg in '0123456789')
        reserve = max(width_of(S, s_end), width_of(S, s_start))
        m = font_metrics(ref)
        label = None
        if L.get('label'):
            lst = dict(st, font=L.get('label_font', 'inter:600'), size=L.get('label_size', 0.026 if v else 0.035),
                       color=L.get('label_color', '#ffffff'), shadow={'dy': 0.05, 'blur': 0.1, 'alpha': 0.6})
            lst.update(L.get('label_style') or {})
            lb = make_block(tokenize(L['label']), lst, env, max_width=env.safe_w_center(x_c), max_lines=2)
            label = dict(block=lb, ts=resolve_style(lst, env, lb.size))
        land = dict(L.get('land') or {})
        plan = dict(mode=mode, v0=v0, v1=v1, div=div, fkw=fkw, start_f=start_f, end_f=end_f, ease=L.get('ease', 'outCubic'),
                    st=st, ref=ref, size=S, cell=cell, reserve=reserve, cap=m['cap'] * S, desc=m['desc'] * S, x=x_c, y=y_c,
                    label=label, land_col=to_rgba(land.get('color', '#ffc400')), pulse=float(land.get('pulse', 1.1)),
                    f0=f0, f1=f1, ts=resolve_style(st, env, S), plate=L.get('plate'), n_in=n_in)
        if mode in ('bars', 'line', 'ring', 'progress'):
            plan.update(cls._chart_plan(L, env, plan))
        return plan

    @classmethod
    def _chart_plan(cls, L, env, plan):
        v = env.vertical
        data = L.get('data') or [{'label': '', 'value': plan['v1']}]
        rows = []
        for i, d in enumerate(data):
            if isinstance(d, dict):
                rows.append(dict(label=str(d.get('label', '')), value=float(d.get('value', 0)), hl=bool(d.get('highlight'))))
            else:
                rows.append(dict(label='', value=float(d), hl=False))
        if rows and not any(r['hl'] for r in rows) and L.get('highlight') is not None:
            rows[int(L['highlight'])]['hl'] = True
        sh = {'dy': 0.05, 'blur': 0.1, 'alpha': 0.6}
        lst = dict(plan['st'], font='inter:600', size=0.022 if v else 0.025, color='#ffffff', shadow=sh)
        vst = dict(plan['st'], font='inter:800', size=0.028 if v else 0.032, color='#ffffff', shadow=sh)
        return dict(rows=rows, lst=lst, vst=vst, main=to_rgba(L.get('main_color', '#ffc400')),
                    rest=to_rgba(L.get('rest_color', '#8a8f98'), 0.6 if L.get('rest_alpha') is None else L['rest_alpha']),
                    grow=float(L.get('grow', 0.6)), stagger=env.fr25(L.get('stagger', 4)))

    @classmethod
    def _value(cls, plan, f):
        v0, v1 = plan['v0'], plan['v1']
        if f >= plan['end_f']:
            return v1, True
        if f <= plan['start_f']:
            return v0, False
        p = (f - plan['start_f']) / float(plan['end_f'] - plan['start_f'])
        return v0 + (v1 - v0) * ease(p, plan['ease']), False

    @classmethod
    def _num_sprite(cls, plan, env, text, col, hide=None):
        s = env.s
        ref, S = plan['ref'], plan['size']
        cell = plan['cell']
        stroke = plan['ts'].stroke
        items, x = [], 0.0
        for ci, ch in enumerate(text):
            adv = cell if ch.isdigit() else text_length(ch, ref, S)
            if not ch.isspace() and not (hide and ci in hide):
                g = raster(ch, ref, S * s, stroke, 0.0)
                items.append((g, x * s + (adv * s - g.adv) / 2 + g.x0, g.y0 + plan['cap'] * s))
            x += adv
        width = x
        if not items:
            return None, width
        sh = plan['ts'].shadow
        mg = 2 + (int(abs(sh[0]) + abs(sh[1]) + 2.6 * sh[2]) if sh else 0)
        X0 = int(math.floor(min(i[1] for i in items))) - mg
        Y0 = int(math.floor(min(i[2] for i in items))) - mg
        X1 = int(math.ceil(max(i[1] + i[0].w for i in items))) + mg
        Y1 = int(math.ceil(max(i[2] + i[0].h for i in items))) + mg
        buf = np.zeros((Y1 - Y0, X1 - X0, 4), np.float32)
        for g, X, Y in items:
            ix, iy = int(round(X)) - X0, int(round(Y)) - Y0
            reg = buf[iy:iy + g.h, ix:ix + g.w]
            if stroke > 0 and g.s is not None:
                _over_mask(reg, g.s.astype(np.float32) / 255.0, plan['ts'].stroke_col)
            _over_mask(reg, g.a.astype(np.float32) / 255.0, col)
        if sh:
            out = np.zeros_like(buf)
            m = _shift(fast_blur(np.ascontiguousarray(buf[..., 3]), sh[2]), sh[0], sh[1])
            _over_mask(out, m, sh[3])
            _over(out, buf)
            buf = out
        return Sprite(buf, X0, Y0), width

    @classmethod
    def draw(cls, L, env, plan, cv):
        f = env.f
        s = env.s
        fps = env.fps
        mode = plan['mode']
        a_out = parse_anim(L.get('anim_out', 'fade(0.2)'), 'fade', fps)
        st = element_state(parse_anim(L.get('anim_in', {'type': 'pop', 'scale': [0.9, 1.0], 'dur': 0.2,
                                                          'ease': 'outCubic'}), 'pop', fps), a_out, f, plan['f0'], plan['f1'], env)
        if st is None:
            return
        if plan.get('plate'):
            pl = plan['plate'] if isinstance(plan['plate'], dict) else {}
            w = plan['reserve'] + plan['size'] * 0.8
            h = plan['cap'] + plan['desc'] + plan['size'] * 0.6 + (plan['label']['block'].height + plan['size'] * 0.3
                                                                   if plan['label'] else 0)
            spr = rect_sprite((plan['x'] - w / 2) * s, (plan['y'] - (plan['cap'] + plan['desc']) / 2 - plan['size'] * 0.3) * s,
                              (plan['x'] + w / 2) * s, (plan['y'] - (plan['cap'] + plan['desc']) / 2 - plan['size'] * 0.3 + h) * s,
                              to_rgba(pl.get('color', '#000000'), pl.get('alpha', 0.55)), plan['size'] * 0.15 * s)
            st_p = St()
            st_p.alpha = st.alpha
            cv.place(spr, 0, 0, st_p)
        if mode in ('bars', 'line', 'ring', 'progress'):
            cls._draw_chart(L, env, plan, cv, st)
            return
        val, landed = cls._value(plan, f)
        rising = plan['v1'] >= plan['v0']
        fkw = dict(plan['fkw'])
        hide = None
        if mode == 'clock':
            secs = max(0.0, val)
            text = '%02d:%02d' % (int(secs) // 60, int(secs) % 60)
            if L.get('blink', True) and (f / fps) % 1.0 >= 0.5 and not landed:
                hide = {2}                      # colon blinks at 1 Hz, its advance stays (digits do not move)
        else:
            fkw['rounding'] = 'floor' if rising else 'ceil'
            text = format_number(val / plan['div'], **fkw) if not landed else format_number(plan['v1'] / plan['div'], **plan['fkw'])
        col = plan['ts'].fill
        k_land = f - plan['end_f']
        sc = 1.0
        if landed:
            col = plan['land_col'] if L.get('land_color', True) else col
            g_, b_ = env.fr25(3), env.fr25(5)
            if k_land < g_:
                sc = 1 + (plan['pulse'] - 1) * ease((k_land + 1) / g_, 'outQuad')
            elif k_land < g_ + b_:
                sc = plan['pulse'] + (1 - plan['pulse']) * ease((k_land - g_ + 1) / b_, 'outBack')
        if mode == 'roll' and not landed:
            spr, width = cls._roll_sprite(plan, env, val, col)
        else:
            spr, width = cls._num_sprite(plan, env, text, col, hide=hide)
        if spr is None:
            return
        ox = (plan['x'] - plan['reserve'] / 2 + (plan['reserve'] - width)) * s
        oy = (plan['y'] - (plan['cap'] + plan['desc']) / 2) * s
        st2 = St().compose(st)
        st2.sx *= sc
        st2.sy *= sc
        piv = (plan['x'] * s, plan['y'] * s)
        cv.place(spr, ox, oy, st2, piv)
        if plan['label'] is not None:
            lb = plan['label']
            n = env.fr25(4)
            a = _clamp((k_land + 1) / n, 0.0, 1.0) if L.get('label_after_landing', True) else 1.0
            if a > 0:
                st3 = St().compose(st)
                st3.alpha *= a
                b = lb['block']
                lo = (plan['x'] - b.width / 2) * s, (plan['y'] + (plan['cap'] + plan['desc']) / 2 + plan['size'] * 0.18) * s
                cv.place(text_sprite(b, lb['ts'], env), lo[0], lo[1], st3)

    @classmethod
    def _roll_sprite(cls, plan, env, val, col):
        """Odometer: every digit column scrolls (fraction of its place value), with vertical blur by speed."""
        s = env.s
        final = format_number(plan['v1'] / plan['div'], **plan['fkw'])
        ref, S, cell = plan['ref'], plan['size'], plan['cell']
        dec = int(plan['fkw'].get('decimals') or 0)
        digits_pos = [i for i, ch in enumerate(final) if ch.isdigit()]
        nd = len(digits_pos)
        x, items = 0.0, []
        vv = abs(val) / plan['div'] * 10 ** dec
        h_cell = (plan['cap'] + plan['desc']) * s * 1.15
        for i, ch in enumerate(final):
            adv = cell if ch.isdigit() else text_length(ch, ref, S)
            if ch.isdigit():
                place = nd - 1 - digits_pos.index(i)
                pv = vv / (10 ** place)
                d0 = int(math.floor(pv)) % 10
                fr = pv - math.floor(pv)
                if place > 0:
                    fr = _clamp((fr - 0.9) / 0.1, 0.0, 1.0) if (vv % (10 ** place)) / (10 ** place) > 0.9 else 0.0
                for dd, off in ((d0, -fr), ((d0 + 1) % 10, 1 - fr)):
                    if abs(off) >= 1.0:
                        continue
                    g = raster(str(dd), ref, S * s, 0.0, 0.0)
                    items.append((g, x * s + (adv * s - g.adv) / 2 + g.x0, g.y0 + plan['cap'] * s + off * h_cell, i))
            elif not ch.isspace():
                g = raster(ch, ref, S * s, 0.0, 0.0)
                items.append((g, x * s + g.x0, g.y0 + plan['cap'] * s, i))
            x += adv
        y_top, y_bot = -0.05 * S * s, (plan['cap'] + plan['desc']) * s + 0.05 * S * s
        X1 = int(math.ceil(x * s)) + 4
        buf = np.zeros((int(math.ceil(y_bot - y_top)) + 4, X1, 4), np.float32)
        for g, X, Y, _ in items:
            ix, iy = int(round(X)), int(round(Y - y_top))
            reg, mm = _clip_paste(buf, g.a, ix, iy)
            if reg is not None:
                _over_mask(reg, mm.astype(np.float32) / 255.0, col)
        return Sprite(buf, 0, y_top), x

    @classmethod
    def _draw_chart(cls, L, env, plan, cv, st):
        f, s, fps = env.f, env.s, env.fps
        v = env.vertical
        mode = plan['mode']
        rows = plan['rows']
        t0 = plan['start_f']
        grow = max(1, int(round(plan['grow'] * fps)))
        if mode == 'bars':
            n = len(rows)
            bw = env.W * (0.11 if v else 0.08)
            gap = bw * 0.5
            tot = n * bw + (n - 1) * gap
            if tot > env.W * 0.8:
                k = env.W * 0.8 / tot
                bw, gap, tot = bw * k, gap * k, tot * k
            x0 = plan['x'] - tot / 2
            base = env.cH(L.get('base', 0.66 if v else 0.75))
            hmax = env.cH(L.get('max_h', 0.3 if v else 0.45))
            vmax = max(r['value'] for r in rows) or 1.0
            for i, r in enumerate(rows):
                fa = t0 + i * plan['stagger']
                p = ease(_clamp((f - fa + 1) / grow, 0.0, 1.0), 'outCubic')
                h = hmax * r['value'] / vmax * p
                col = plan['main'] if r['hl'] or (not any(q['hl'] for q in rows) and r['value'] == vmax) else plan['rest']
                bx = x0 + i * (bw + gap)
                if h > 0.5:
                    cv.place(rect_sprite(bx * s, (base - h) * s, (bx + bw) * s, base * s, col, 0.06 * bw * s), 0, 0, st)
                if p > 0:
                    vs = format_number(r['value'] * p if p < 1 else r['value'], **dict(plan['fkw'], unit='', rounding='floor'))
                    vb = make_block([vs], plan['vst'], env)
                    cv.place(text_sprite(vb, resolve_style(plan['vst'], env, vb.size), env),
                             (bx + bw / 2 - vb.width / 2) * s, (base - h - vb.height - 0.01 * env.H) * s, st)
                if r['label']:
                    lb = make_block(tokenize(r['label']), plan['lst'], env, max_width=bw + gap * 0.9, max_lines=2)
                    cv.place(text_sprite(lb, resolve_style(plan['lst'], env, lb.size), env),
                             (bx + bw / 2 - lb.width / 2) * s, (base + 0.012 * env.H) * s, st)
            cv.place(rect_sprite((x0 - gap * 0.3) * s, base * s, (x0 + tot + gap * 0.3) * s, base * s + max(1.0, 0.002 * env.oh),
                                 to_rgba('#ffffff', 0.5)), 0, 0, st)
        elif mode == 'line':
            vals = [r['value'] for r in rows]
            n = len(vals)
            wbox = env.W * (0.74 if v else 0.6)
            hbox = env.H * (0.22 if v else 0.4)
            bx0, by1 = plan['x'] - wbox / 2, env.cH(L.get('base', 0.62 if v else 0.75))
            lo, hi = min(vals + [0.0]), max(vals) or 1.0
            pts = [((bx0 + wbox * i / max(1, n - 1)) * s, (by1 - hbox * (q - lo) / (hi - lo + 1e-9)) * s) for i, q in enumerate(vals)]
            dur = max(1, int(round(float(L.get('draw', 1.2)) * fps)))
            p = ease(_clamp((f - t0 + 1) / dur, 0.0, 1.0), 'inOutCubic')
            if p > 0:
                w = max(2.0, env.o(env.cH(0.005)))
                af = _clamp((f - t0 - dur + 1) / env.fr25(8), 0.0, 1.0)
                if af > 0:
                    poly = pts + [(pts[-1][0], by1 * s), (pts[0][0], by1 * s)]
                    sp = poly_sprite(poly, (plan['main'][0], plan['main'][1], plan['main'][2], 0.2 * af))
                    cv.place(sp, 0, 0, st)
                cv.place(stroke_sprite(pts, w, plan['main'], progress=p), 0, 0, st)
                if p >= 1.0:
                    k = f - t0 - dur
                    r = env.o(env.cH(0.006)) * (1 + 0.25 * math.sin(k / fps * 2 * math.pi))
                    cv.place(disc_sprite(pts[-1][0], pts[-1][1], r, plan['main']), 0, 0, st)
                    vs = format_number(vals[-1], **dict(plan['fkw'], unit=''))
                    vb = make_block([vs], plan['vst'], env)
                    cv.place(text_sprite(vb, resolve_style(plan['vst'], env, vb.size), env),
                             pts[-1][0] - vb.width * s / 2, pts[-1][1] - (vb.height + 0.02 * env.H) * s, st)
        elif mode == 'ring':
            val = rows[0]['value'] if L.get('data') else plan['v1']
            ratio = _clamp(val / float(L.get('max', 100.0)), 0.0, 1.0)
            dur = max(1, int(round(float(L.get('dur', 1.0)) * fps)))
            p = ease(_clamp((f - t0 + 1) / dur, 0.0, 1.0), 'outCubic')
            R = env.o(env.cH(L.get('radius', 0.1 if v else 0.13)))
            w = env.o(env.cH(L.get('thickness', 0.03 if v else 0.04)))
            cx, cy = plan['x'] * s, plan['y'] * s
            bg = np.linspace(0, 2 * math.pi, 120)
            cv.place(stroke_sprite(np.stack([cx + R * np.sin(bg), cy - R * np.cos(bg)], 1), w,
                                   (plan['main'][0], plan['main'][1], plan['main'][2], 0.2)), 0, 0, st)
            if p * ratio > 0.002:
                th = np.linspace(0, 2 * math.pi * ratio * p, max(3, int(120 * ratio * p)))
                cv.place(stroke_sprite(np.stack([cx + R * np.sin(th), cy - R * np.cos(th)], 1), w, plan['main']), 0, 0, st)
            vs = format_number(val * p, **dict(plan['fkw'], unit='', rounding='floor')) if p < 1 else format_number(val, **dict(plan['fkw'], unit=''))
            vb = make_block([vs], dict(plan['st'], size=(R / s) * 0.55), env)
            cv.place(text_sprite(vb, resolve_style(plan['st'], env, vb.size), env), cx - vb.width * s / 2,
                     cy - vb.height * s / 2, st)
        elif mode == 'progress':
            val = rows[0]['value'] if L.get('data') else plan['v1']
            ratio = _clamp(val / float(L.get('max', 100.0)), 0.0, 1.0)
            dur = max(1, int(round(float(L.get('dur', 1.0)) * fps)))
            p = ease(_clamp((f - t0 + 1) / dur, 0.0, 1.0), 'outCubic')
            wbar = env.W * (0.68 if v else 0.6)
            th = env.H * (0.018 if v else 0.022)
            x0, y0 = (plan['x'] - wbar / 2) * s, plan['y'] * s
            cv.place(rect_sprite(x0, y0, x0 + wbar * s, y0 + th * s, to_rgba('#ffffff', 0.18), th * s / 2), 0, 0, st)
            fw = wbar * ratio * p
            if fw > th:
                cv.place(rect_sprite(x0, y0, x0 + fw * s, y0 + th * s, plan['main'], th * s / 2), 0, 0, st)
            vs = format_number(val * p, **dict(plan['fkw'], unit='', rounding='floor'))
            vb = make_block([vs], plan['vst'], env)
            tx = _clamp(x0 + fw * s - vb.width * s / 2, env.safe[0], env.safe[2] - vb.width * s)
            cv.place(text_sprite(vb, resolve_style(plan['vst'], env, vb.size), env), tx, y0 - (vb.height + 0.012 * env.H) * s, st)


# ---------------------------------------------------------------------------- route map
def _catmull(pts, n=16):
    pts = np.asarray(pts, np.float64)
    if len(pts) < 3:
        return pts
    P = np.vstack([pts[:1], pts, pts[-1:]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2])
    return np.array(out)


@register
class RouteMap(Kind):
    """gfx.route_map (basic, own drawing — no third-party map tiles): route polyline drawn over time along its arc
    length (casing + line, smooth / straight / arc segments), pins popping as the head passes them with labels, a
    pulsing head dot, optional distance counter, optional panel / card background and faint graticule."""
    name = 'route_map'
    default_dur = 4.0

    @classmethod
    def plan(cls, L, env):
        v = env.vertical
        box = L.get('box', [0.12, 0.24, 0.82, 0.66] if v else [0.14, 0.14, 0.86, 0.84])
        bx0, by0, bx1, by1 = env.cW(box[0]), env.cH(box[1]), env.cW(box[2]), env.cH(box[3])
        if L.get('geo'):
            g = np.array([[float(a), float(b)] for a, b in L['geo']], np.float64)
            lat0 = math.radians(float(np.mean(g[:, 0])))
            xy = np.stack([g[:, 1] * math.cos(lat0), -g[:, 0]], 1)
            lo, hi = xy.min(0), xy.max(0)
            span = np.maximum(hi - lo, 1e-9)
            k = min((bx1 - bx0) * 0.8 / span[0], (by1 - by0) * 0.8 / span[1])
            c = (lo + hi) / 2
            pts = np.stack([(bx0 + bx1) / 2 + (xy[:, 0] - c[0]) * k, (by0 + by1) / 2 + (xy[:, 1] - c[1]) * k], 1)
        else:
            raw = np.array([[float(a), float(b)] for a, b in (L.get('points') or [[0.1, 0.8], [0.5, 0.4], [0.9, 0.2]])])
            pts = np.stack([bx0 + raw[:, 0] * (bx1 - bx0), by0 + raw[:, 1] * (by1 - by0)], 1)
        curve = L.get('curve', 'smooth')
        stops = [0]
        if curve == 'arc':
            seg_pts = [pts[:1]]
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                d = b - a
                nrm = np.array([d[1], -d[0]]) * float(L.get('bulge', 0.18))
                ctrl = (a + b) / 2 + nrm
                seg_pts.append(bezier(a, ctrl, b, 24)[1:])
                stops.append(sum(len(sp) for sp in seg_pts) - 1)
            path = np.vstack(seg_pts)
        elif curve == 'smooth' and len(pts) >= 3:
            path = _catmull(pts, 16)
            stops = [i * 16 for i in range(len(pts))]
        else:
            path = pts
            stops = list(range(len(pts)))
        seg = np.sqrt(((path[1:] - path[:-1]) ** 2).sum(1))
        cum = np.concatenate([[0], np.cumsum(seg)])
        stop_frac = [float(cum[min(i, len(cum) - 1)] / max(cum[-1], 1e-9)) for i in stops]
        labels = L.get('labels') or []
        st = style_of(L, {'font': 'inter:700', 'size': 0.022 if v else 0.028, 'color': '#ffffff',
                          'shadow': {'dy': 0.06, 'blur': 0.15, 'alpha': 0.8}})
        lab = []
        for i, t in enumerate(labels[:len(pts)]):
            if not t:
                lab.append(None)
                continue
            b = make_block(tokenize(t), st, env, max_width=env.W * 0.3, max_lines=2)
            lab.append(dict(block=b, ts=resolve_style(st, env, b.size)))
        draw = dict(L.get('draw') or {})
        km = None
        if L.get('km') is not None or L.get('total') is not None:
            # language data: Russian kilometre suffix for locale 'ru'
            km = dict(total=float(L.get('km', L.get('total'))), suffix=L.get('suffix', ' км' if str(L.get('locale', 'en')).startswith('ru') else ' km'),
                      locale=L.get('locale', 'en'))
            kst = dict(st, size=0.03 if v else 0.04, font='inter:800')
            km['st'] = kst
        return dict(path=path, cum=cum, pts=pts, stop_frac=stop_frac, lab=lab, box=(bx0, by0, bx1, by1),
                    delay=float(draw.get('delay', 0.3)), dur=float(draw.get('dur', 1.8)), ease=draw.get('ease', 'outCubic'),
                    line=dict(L.get('line') or {}), km=km, st=st)

    @classmethod
    def draw(cls, L, env, plan, cv):
        f0, f1 = cls.span(L, env.fps)
        f, s, fps = env.f, env.s, env.fps
        v = env.vertical
        a_out = parse_anim(L.get('anim_out', 'fade(0.3)'), 'fade', fps)
        st = element_state(parse_anim(L.get('anim_in', 'fade(0.25)'), 'fade', fps), a_out, f, f0, f1, env)
        if st is None:
            return
        bx0, by0, bx1, by1 = plan['box']
        bg = L.get('bg')
        if bg and not (bg == 'panel' or isinstance(bg, dict)):
            cv.fill(bg, st.alpha)
        if (bg == 'panel' or isinstance(bg, dict) or L.get('grid', bool(bg))) and plan.get('bg_spr') is None:
            pad = 0.03 * env.H if (bg == 'panel' or isinstance(bg, dict)) else 0.0
            X0, Y0 = int((bx0 - pad) * s), int((by0 - pad) * s)
            buf = np.zeros((int((by1 + pad) * s) - Y0 + 2, int((bx1 + pad) * s) - X0 + 2, 4), np.float32)
            if pad:
                pd = bg if isinstance(bg, dict) else {}
                m = round_rect_mask(buf.shape[1] - 2, buf.shape[0] - 2, 0.025 * env.H * s)
                _over_mask(buf[:m.shape[0], :m.shape[1]], m, to_rgba(pd.get('color', '#0d1620'), pd.get('alpha', 0.72)))
            if L.get('grid', bool(bg)):
                gc = to_rgba('#ffffff', 0.07)
                lw = max(1, int(round(s)))
                step = 0.06 * env.H * s
                x = bx0 * s - X0
                while x <= (bx1 * s - X0) + 1:
                    _over_mask(buf[int(by0 * s - Y0):int(by1 * s - Y0), int(x):int(x) + lw],
                               np.ones((int(by1 * s - Y0) - int(by0 * s - Y0), lw), np.float32), gc)
                    x += step
                y = by0 * s - Y0
                while y <= (by1 * s - Y0) + 1:
                    _over_mask(buf[int(y):int(y) + lw, int(bx0 * s - X0):int(bx1 * s - X0)],
                               np.ones((lw, int(bx1 * s - X0) - int(bx0 * s - X0)), np.float32), gc)
                    y += step
            plan['bg_spr'] = Sprite(buf, X0, Y0)
        if plan.get('bg_spr') is not None:
            cv.place(plan['bg_spr'], 0, 0, st)
        t = (f - f0) / fps - plan['delay']
        p = ease(_clamp(t / max(plan['dur'], 1e-3), 0.0, 1.0), plan['ease'])
        path = plan['path'] * s
        ln = plan['line']
        col = to_rgba(ln.get('color', '#ffc400'))
        w = max(2.0, env.o(env.cH(ln.get('w', 0.006))))
        if p > 0:
            if ln.get('casing', True):
                cw = w + max(2.0, env.o(env.cH(0.004)))
                cv.place(stroke_sprite(path, cw, to_rgba('#000000', 0.45), progress=p), 0, 0, st)
            if ln.get('dash'):
                L_tot = plan['cum'][-1] * s
                dl = env.o(env.cH(0.02))
                nd = int(L_tot * p / (2 * dl)) + 1
                for i in range(nd):
                    a0, a1 = i * 2 * dl / L_tot, min(p, (i * 2 + 1) * dl / L_tot)
                    if a1 <= a0:
                        break
                    seg = cls._sub(path, plan['cum'] * s, a0, a1)
                    cv.place(stroke_sprite(seg, w, col), 0, 0, st)
            else:
                cv.place(stroke_sprite(path, w, col, progress=p), 0, 0, st)
        # pins and labels
        r_pin = env.o(env.cH(0.009 if v else 0.011))
        for i, (pt, fr) in enumerate(zip(plan['pts'], plan['stop_frac'])):
            if p + 1e-6 < fr and not (i == 0 and t >= 0):
                continue
            t_hit = plan['delay'] + cls._inv_ease(fr, plan['ease']) * plan['dur'] if fr > 0 else plan['delay']
            k = (f - f0) - t_hit * fps
            sc = _keys_scale([0.0, 1.25, 1.0], _clamp(k / max(1.0, env.fr25(5)), 0, 1), {'peak': 0.55, 'ease': 'outQuad',
                                                                                         'ease2': 'outBack'})
            if sc <= 0.01:
                continue
            big = 1.25 if i in (0, len(plan['pts']) - 1) else 1.0
            cx, cy = pt[0] * s, pt[1] * s
            stp = St().compose(st)
            cv.place(disc_sprite(cx, cy, r_pin * big * sc * 1.45, to_rgba('#000000', 0.35)), 0, 0, stp)
            cv.place(disc_sprite(cx, cy, r_pin * big * sc, to_rgba('#ffffff')), 0, 0, stp)
            cv.place(disc_sprite(cx, cy, r_pin * big * sc * 0.55, col), 0, 0, stp)
            lb = plan['lab'][i] if i < len(plan['lab']) else None
            if lb is not None:
                b = lb['block']
                a = _clamp(k / max(1.0, env.fr25(6)), 0.0, 1.0)
                if a > 0:
                    up = cy > (by0 + by1) / 2 * s if i not in (0,) else cy > (by0 + by1) / 2 * s
                    mg = 0.4 * b.size * s
                    lx = _clamp(cx - b.width * s / 2, env.safe[0] + mg, env.safe[2] - b.width * s - mg)
                    ly = cy - r_pin * 2 - b.height * s if up else cy + r_pin * 2
                    ly = _clamp(ly, env.safe[1] + mg, env.safe[3] - b.height * s - mg)
                    st_l = St().compose(st)
                    st_l.alpha *= a
                    cv.place(text_sprite(b, lb['ts'], env), lx, ly, st_l)
        # moving head
        if 0 < p < 1 and len(path) > 1:
            hx, hy = cls._at(path, plan['cum'] * s, p)
            ph = (f % int(max(2, round(fps * 0.5)))) / max(1.0, fps * 0.5)
            st_h = St().compose(st)
            st_h.alpha *= 0.5 * (1 - ph)
            cv.place(disc_sprite(hx, hy, r_pin * (1.2 + 1.6 * ph), col, ring=max(1.5, w * 0.5)), 0, 0, st_h)
            cv.place(disc_sprite(hx, hy, r_pin * 0.95, to_rgba('#ffffff')), 0, 0, st)
        if plan['km'] is not None and p > 0:
            km = plan['km']
            val = km['total'] * p
            txt = format_number(val, locale=km['locale'], decimals=0, rounding='floor') + km['suffix']
            b = make_block([txt.replace(' ', ' ')], km['st'], env)
            cv.place(text_sprite(b, resolve_style(km['st'], env, b.size), env), (bx1 * s - b.width * s), by1 * s + 0.01 * env.oh,
                     st)

    @staticmethod
    def _inv_ease(y, name):
        lo, hi = 0.0, 1.0
        for _ in range(30):
            mid = (lo + hi) / 2
            if ease(mid, name) < y:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    @staticmethod
    def _at(path, cum, p):
        if len(path) < 2:
            return tuple(path[0])
        target = cum[-1] * p
        k = int(np.searchsorted(cum, target))
        k = max(1, min(k, len(path) - 1))
        t = (target - cum[k - 1]) / max(cum[k] - cum[k - 1], 1e-9)
        return tuple(path[k - 1] + (path[k] - path[k - 1]) * t)

    @classmethod
    def _sub(cls, path, cum, a0, a1):
        pa = cls._at(path, cum, a0)
        pb = cls._at(path, cum, a1)
        ia = int(np.searchsorted(cum, cum[-1] * a0))
        ib = int(np.searchsorted(cum, cum[-1] * a1))
        mid = [tuple(q) for q in path[ia:ib]]
        return [pa] + mid + [pb]


# ============================================================================ machine-readable layer registry
# params: {name: default} on a 9:16 canvas (None = optional / derived; the class docstring explains), landscape:
# defaults that differ on 16:9, choices: enumerated values. Style keys (STYLE_KEYS) and COMMON_LAYER_PARAMS apply to
# every kind; caption kinds also take a CAPTION_STYLES preset. Checked by tests/test_text.py (every key a kind reads
# is listed).
COMMON_LAYER_PARAMS = {
    'kind': 'static', 'f0': None, 'f1': None, 't0': None, 't1': None, 'dur': None, 'blend': 'normal', 'opacity': 1.0,
    'safe_zone': 'auto', 'style': None, 'anim_in': None, 'anim_out': None, 'pos': None, 'seed': 7, 'enabled': True,
    'render_scale': 1.0, 'occlude': False, 'mask_levels': None, 'feather': None, 'type_class': None,
}
COMMON_LAYER_DOC = ('frames f0..f1 (or t0/t1 s, or dur s); blend normal|screen|add|multiply|difference; style {font, '
                    'weight, axes, size, color, gradient, stroke, shadow, box, glow, caps, tracking, line_height, '
                    'align, features} (style keys may also sit at the top level); anim_in / anim_out: name, '
                    '"name(dur, k=v)" or {type, dur, ...} (ANIM_LIB); safe_zone auto|tiktok|reels|shorts|16:9|'
                    'title_safe|action_safe|none|[x0, y0, x1, y1]; occlude hides the layer behind the person mask')
_SUB_PARAMS = {
    'words': None, 'chunks': None, 'lines': None, 'mode': 'dialog', 'max_width': None, 'avoid': 'face',
    'fit': 'reflow', 'max_lines': 3, 'lang': None,
    'chunk': {'max_chars': 26, 'max_lines': 2, 'min_dur': 0.8, 'max_dur': 6.0, 'cps_max': 17.0, 'max_words': None,
              'break_on_pause': 0.6, 'split_on_cut': 0.3, 'ellipsis': True, 'min_show': 0.7},
    'lead': -2, 'tail': 6, 'gap_min': 2, 'join_gap': None, 'highlight': None, 'keywords': None, 'preset': None,
}
LAYER_SPECS = {
    'static': dict(desc='Plain text block (or ed_edl `texts` items at fixed canvas px), optional entrance / exit.',
                   params={'text': '', 'items': None, 'pos': [0.47, 0.5], 'max_width': None, 'max_lines': None,
                           'anchor': ['center', 'center'], 'clamp': True},
                   landscape={'pos': [0.5, 0.5]}),
    'subtitle': dict(desc='Dialogue subtitles chunked from word timestamps (or given chunks), 1-2 lines, face '
                          'avoidance, keyword highlight, caption presets.',
                     params=dict(_SUB_PARAMS), landscape={'chunk': {'max_chars': 42}},
                     choices={'mode': ['dialog', 'lyric'], 'avoid': ['face', 'none'], 'fit': ['reflow', 'shrink'],
                              'preset': sorted(CAPTION_STYLES)}),
    'karaoke': dict(desc='Word-by-word captions: the chunk stands still and the sounding word is highlighted '
                         '(colour, sliding box, bounce, fill, ghost).',
                    params=dict(_SUB_PARAMS, highlight={
                        'mode': 'color', 'active': '#ffe14a', 'progressive': False, 'upcoming_alpha': 0.45,
                        'box': {'fill': '#ffe14a', 'text': '#000000', 'pad': [0.28, 0.12], 'radius': 0.22},
                        'bounce': {'scale': 1.12, 'grow': 3, 'back': 4},
                        'keyword': {'pick': 'none', 'color': '#45f06b', 'max_per_chunk': 1}},
                        switch_lead=-1, min_on=None, max_lines=2,
                        chunk={'max_chars': 20, 'max_lines': 2, 'max_dur': 2.5, 'cps_max': 20.0, 'max_words': 3,
                               'break_on_pause': 0.25, 'join_gap': 0.6}),
                    landscape={'chunk': {'max_chars': 36, 'max_dur': 4.0, 'max_words': 6}},
                    choices={'highlight.mode': ['color', 'box', 'bounce', 'fill', 'ghost'], 'fit': ['reflow', 'shrink'],
                             'highlight.keyword.pick': ['none', 'numbers'], 'preset': sorted(CAPTION_STYLES)}),
    'kinetic': dict(desc='Kinetic typography: words on their timestamps, 1-3 per screen (word, phrase, cascade, '
                         'decode, strobe, countdown).',
                    params={'mode': 'word', 'words': None, 'text': None, 'per': 0.4, 'pos': [0.47, 0.48],
                            'lead': -1, 'group': 1, 'min_hold': 0.3, 'max_gap': 0.7, 'tail': 0.25,
                            'auto_group': True, 'same_size': True, 'max_words': 6, 'max_lines': 3, 'strobe': None,
                            'countdown': None},
                    landscape={'pos': [0.5, 0.48]},
                    choices={'mode': ['word', 'phrase', 'cascade', 'decode', 'strobe', 'countdown']}),
    'beat_text': dict(desc='Words on the beat grid: hit on each slot, slam on downbeats / the drop, kick pulse, '
                           'line and stack builds.',
                      params={'slots': None, 'words': None, 'text': '', 'beats': None, 'downbeats': None,
                              'bpm': 120.0, 'every': 1, 'start': None, 'min_on': 0.27, 'hold': 0.6, 'lead': -1,
                              'layout': 'single', 'reset_every': 4, 'pos': [0.47, 0.48],
                              'anchors': [[0.47, 0.24], [0.47, 0.46], [0.47, 0.68]], 'accent': '#ffe600',
                              'kicks': None, 'pitch': 0.95, 'same_size': False, 'accents': None,
                              'outline_cycle': None, 'scrim': 0.0, 'shake': None, 'invert_frames': 0,
                              'color': '#ffffff'},
                      landscape={'pos': [0.5, 0.48], 'anchors': [[0.3, 0.3], [0.5, 0.5], [0.7, 0.7]]},
                      choices={'layout': ['single', 'line_build', 'stack_build', 'jump', 'cards']}),
    'title_card': dict(desc='Title block (kicker / title / credit) in six layouts with fades, slams, reveals, '
                            'underline draw-on and optional card background.',
                       params={'layout': 'center_block', 'lines': None, 'text': '', 'type_class': 'serif_caps',
                               'small_font': None, 'x': 0.47, 'y': None, 'y_top': 0.2, 'y_bottom': 0.72,
                               'y_billing': 0.76, 'size': None, 'sizes': None, 'max_lines': 2, 'underline': None,
                               'bg': None, 'bg_out': 'cut', 'pulse': None, 'color': '#f2ede4'},
                       landscape={'x': 0.5, 'y_top': 0.22, 'y_bottom': 0.82, 'y_billing': 0.9},
                       choices={'layout': ['center_block', 'poster', 'fill', 'frame_top_bottom', 'lower_block',
                                           'sky_top']}),
    'lower_third': dict(desc='Name / role plate: accent bar grows, plate wipes open, text slides out from under '
                             'the mask; reverse exit.',
                        params={'variant': 'plate', 'name': None, 'text': None, 'role': None, 'name_size': 0.026,
                                'role_ratio': 0.66, 'role_style': None, 'accent': '#ffc400',
                                'plate_color': '#000000', 'plate_alpha': 0.65, 'side': 'left', 'x': None,
                                'y': None, 'above': None, 'radius': 0.0},
                        landscape={'name_size': 0.03},
                        choices={'variant': ['plate', 'block', 'minimal', 'location', 'topic', 'handle'],
                                 'side': ['left', 'right']}),
    'intertitle': dict(desc='Intertitles: caption over the shot, chapter, text card, typed reply, trailer slams, '
                            'prologue lines.',
                       params={'variant': 'caption', 'text': '', 'lines': None, 'x': None, 'y': None,
                               'second_delay': 0.5, 'bg': '#000000', 'cps': 22, 'card': True, 'line_times': None},
                       choices={'variant': ['caption', 'chapter', 'card', 'reply', 'trailer', 'prologue'],
                                'pos': ['top', 'bottom', 'center']}),
    'margin_note': dict(desc='Handwritten notes typed beside the speaker in time with the words: write, strike, '
                             'correct, arrow, punch.',
                        params={'items': [], 'side': 'auto', 'x': None, 'y': 0.2, 'pitch': 1.35, 'cps': 18,
                                'correct_indent': 0.03, 'strike_dur': 0.3, 'arrow_dur': 0.5},
                        landscape={'y': 0.15},
                        choices={'side': ['auto', 'left', 'right'],
                                 'items.op': ['write', 'correct', 'strike', 'arrow', 'punch']}),
    'repeat': dict(desc='One word multiplied into a looping pattern: echo stack, rows, wave, radial, tunnel, '
                        'recursive.',
                   params={'layout': 'echo_stack', 'text': 'REPEAT', 'x': 0.47, 'y': 0.48, 'color2': '#3fe0ff',
                           'gradient': ['#ffe14a', '#3fe0ff'], 'bg': None, 'loop_mode': 'loop', 'copies': None,
                           'pitch': None, 'grow': None, 'loop': None, 'hold': 1.1, 'retract': 0.8,
                           'inner_gradient': [0.2, 1.0],
                           'steps': [1, 3, 8, 20, 40], 'step': 0.25, 'drift': 0.04, 'gap': 0.5, 'alternate': True,
                           'boil': None, 'rows': 7, 'amp': 0.4, 'period': 1.5, 'wavelength': 6, 'spin': 90.0,
                           'r0': 0.04},
                   landscape={'x': 0.5, 'y': 0.49},
                   choices={'layout': ['echo_stack', 'rows', 'wave', 'radial', 'tunnel', 'recursive']}),
    'behind_subject': dict(desc='Text between the background and the person (needs a person mask): giant word, '
                                'side blocks, wall, ring.',
                           params={'layout': 'giant', 'text': 'TEXT', 'lines': None, 'x': 0.47, 'y': 0.33,
                                   'palette': ['#2f6bff', '#ff3b30', '#34c759', '#f2ede4'], 'max_lines': 2,
                                   'gap': 0.02, 'copies': None, 'spin': 20.0},
                           landscape={'x': 0.5, 'y': 0.4, 'max_lines': 1},
                           choices={'layout': ['giant', 'sides', 'wall', 'ring']}),
    'callout': dict(desc='Pin + leader + label stuck to a tracked target, or arrow / ring / brackets / spotlight '
                         '/ tag.',
                    params={'target': [0.5, 0.5], 'variant': 'pin_label', 'text': '', 'side': 'auto', 'up': None,
                            'lag': 3, 'plate': None, 'plate_alpha': 0.92, 'accent': None, 'dot_color': '#ffc400',
                            'diag': 0.05, 'shelf': 0.08, 'style': 'vector', 'color': None, 'feather': 0.04,
                            'dim': 0.5, 'length': 0.16, 'label_color': '#ffffff', 'font': 'inter:600',
                            'angle': -6.0},
                    landscape={'shelf': 0.11},
                    choices={'variant': ['pin_label', 'arrow', 'ring', 'brackets', 'spotlight', 'tag'],
                             'target': ['[x, y]', '[x0, y0, x1, y1]', '{track: name}', '{keys: [[f, x, y]]}']}),
    'counter': dict(desc='Number counting to an exact final value (odometer roll, clock) and simple charts: bars, '
                         'line, ring, progress.',
                    params={'mode': 'number', 'from': 0.0, 'to': 100.0, 'dur': 1.0, 'end_at': None, 'end_f': None,
                            'ease': 'outCubic', 'format': None, 'locale': 'en', 'pos': [0.47, 0.42], 'label': None,
                            'label_font': 'inter:600', 'label_size': 0.026, 'label_color': '#ffffff',
                            'label_style': None, 'label_after_landing': True, 'land': None, 'land_color': True,
                            'blink': True, 'plate': None, 'data': None, 'highlight': None, 'main_color': '#ffc400',
                            'rest_color': '#8a8f98', 'rest_alpha': None, 'grow': 0.6, 'stagger': 4, 'base': 0.62,
                            'max_h': 0.3, 'draw': 1.2, 'max': 100.0, 'radius': 0.1, 'thickness': 0.03},
                    landscape={'pos': [0.5, 0.46], 'label_size': 0.035, 'base': 0.75, 'max_h': 0.45,
                               'radius': 0.13, 'thickness': 0.04},
                    choices={'mode': ['number', 'roll', 'clock', 'bars', 'line', 'ring', 'progress'],
                             'locale': ['en', 'ru']}),
    'route_map': dict(desc='Route polyline drawn over time along its length with pins, labels, head dot and an '
                           'optional distance counter (own drawing, no map tiles).',
                      params={'points': None, 'geo': None, 'box': [0.12, 0.24, 0.82, 0.66], 'curve': 'smooth',
                              'bulge': 0.18, 'labels': None, 'draw': None, 'line': None, 'km': None, 'total': None,
                              'suffix': None, 'locale': 'en', 'bg': None, 'grid': None},
                      landscape={'box': [0.14, 0.14, 0.86, 0.84]},
                      choices={'curve': ['smooth', 'straight', 'arc']}),
}


class KindRegistry(dict):
    """{kind: class} (exactly as before) + machine-readable specs: spec(kind) -> {name, kind: 'layer', desc, params,
    landscape, choices, aliases, doc}; describe() -> JSON-ready {kind: spec}; canonical(name) resolves aliases and
    card ids ('type.kinetic'); common -> COMMON_LAYER_PARAMS."""

    common = COMMON_LAYER_PARAMS

    def canonical(self, name):
        k = kind_of({'kind': name}) if name else None
        return k if k in self else None

    def names(self):
        return sorted(self)

    def spec(self, name):
        k = self.canonical(name)
        if k is None:
            return None
        s = LAYER_SPECS.get(k) or {}
        cls = dict.get(self, k)
        return dict(name=k, kind='layer', desc=s.get('desc') or ' '.join((cls.__doc__ or '').split())[:120],
                    params=json.loads(json.dumps(s.get('params') or {})),
                    landscape=json.loads(json.dumps(s.get('landscape') or {})), choices=dict(s.get('choices') or {}),
                    aliases=sorted(a for a, t in KIND_ALIASES.items() if t == k),
                    doc=' '.join((cls.__doc__ or '').split()))

    def describe(self):
        return {k: self.spec(k) for k in self.names()}


LAYER_KINDS = KindRegistry(LAYER_KINDS)
for _k, _cls in LAYER_KINDS.items():
    _cls.desc = (LAYER_SPECS.get(_k) or {}).get('desc', '')
    _cls.params = (LAYER_SPECS.get(_k) or {}).get('params', {})


def describe(what='all'):
    """JSON-ready registry for planners and docs: {'layers': {kind: spec}, 'common': {...}, 'caption_styles':
    {name: {desc, kinds, voice}}, 'anims': ANIM_LIB, 'fonts': {key: file}, 'type_classes': TYPE_CLASSES}."""
    out = {}
    if what in ('layers', 'all'):
        out['layers'] = LAYER_KINDS.describe()
        out['common'] = {'params': COMMON_LAYER_PARAMS, 'doc': COMMON_LAYER_DOC, 'style_keys': list(STYLE_KEYS)}
    if what in ('caption_styles', 'all'):
        out['caption_styles'] = caption_styles()
        out['caption_aliases'] = dict(CAPTION_ALIASES)
    if what == 'all':
        out['anims'] = json.loads(json.dumps(ANIM_LIB))
        out['fonts'] = {k: v[0] for k, v in FONT_FILES.items()}
        out['type_classes'] = dict(TYPE_CLASSES)
    return out


# ============================================================================ public API
_PREFETCHED = {}


def _layer_texts(L, out=None, depth=0):
    """Every string a layer may draw (text, words, chunks, lines, items, slots, names...) -> list of strings."""
    out = [] if out is None else out
    if depth > 4:
        return out
    if isinstance(L, str):
        out.append(L)
    elif isinstance(L, dict):
        for k, v in L.items():
            if k in ('text', 'w', 'word', 'lines', 'words', 'chunks', 'items', 'slots', 'name', 'role', 'label',
                     'labels', 'prefix', 'suffix', 'title', 'kicker', 'credit'):
                _layer_texts(v, out, depth + 1)
    elif isinstance(L, (list, tuple)):
        for v in L[:5000]:
            _layer_texts(v, out, depth + 1)
    return out


def prefetch_fonts(layer):
    """Fetch the CJK faces a layer will need before rendering starts (render threads then never wait on a
    download); returns the CJK region or None. Called by layer_span."""
    k = id(layer)
    if k in _PREFETCHED and _PREFETCHED[k][0] is layer:
        return _PREFETCHED[k][1]
    txt = ''.join(_layer_texts(layer))
    region = None
    if is_cjk(txt):
        region = cjk_region_for(txt, layer.get('lang'))
        ensure_cjk_font(region)
    for w in shaping_warnings(txt):
        _warn_once(('shape', w[:40]), w)
    if len(_PREFETCHED) > 4096:
        _PREFETCHED.clear()
    _PREFETCHED[k] = (layer, region)
    return region


def layer_span(layer, fps, ctx=None):
    """(f0, f1) inclusive output frames in which the layer may be visible (a superset for word-driven kinds).
    Also fetches on-demand fonts (CJK) the layer needs, so renders never stall on a download mid-frame."""
    try:
        prefetch_fonts(layer)
    except Exception:
        pass
    layer = resolve_preset(layer)
    cls = LAYER_KINDS.get(kind_of(layer))
    if cls is None:
        raise ValueError(f"unknown layer kind {layer.get('kind')!r}; known: {sorted(LAYER_KINDS)}")
    return cls.span(layer, float(fps), ctx)


def _plan_for(cls, L, env):
    key = (cls.name, _fp(L), round(env.fps, 4), env.ow, env.oh, round(env.s, 5), repr(env.zone),
           tuple((k, _fp(env.ctx.get(k))) for k in _PLAN_CTX if env.ctx.get(k) is not None))
    p = _PLANS.get(key)
    if p is None:
        p = cls.plan(L, env)
        _PLANS.put(key, p)
    return p


def render_layer(layer, f, fps, ow, oh, scale, ctx=None):
    """Render one layer on output frame f -> (rgba float32 premultiplied (oh, ow, 4) LayerRGBA, blend) or None.
    The array is fresh (safe to keep) unless the module-level BUFFER_RING is set (see _alloc)."""
    return _render(layer, f, fps, ow, oh, scale, ctx, None)


def _render(layer, f, fps, ow, oh, scale, ctx, reuse):
    if not layer or layer.get('enabled', True) is False:
        return None
    prev = getattr(_TLS, 'lang', None)
    _TLS.lang = layer.get('lang') or (ctx or {}).get('lang')
    try:
        return _render_layer(resolve_preset(layer), f, fps, ow, oh, scale, ctx, reuse)
    finally:
        _TLS.lang = prev


def _render_layer(layer, f, fps, ow, oh, scale, ctx, reuse):
    cls = LAYER_KINDS.get(kind_of(layer))
    if cls is None:
        raise ValueError(f"unknown layer kind {layer.get('kind')!r}; known: {sorted(LAYER_KINDS)}")
    f0, f1 = cls.span(layer, float(fps), ctx)
    if f < f0 or f > f1:
        return None
    k = float(layer.get('render_scale', cls.render_scale_for(layer)))
    low = k < 0.999
    if low:                                      # heavy pattern layers: draw at k× resolution, upscale once
        ow2, oh2 = max(2, int(round(ow * k))), max(2, int(round(oh * k)))
        env = Env(layer, f, fps, ow2, oh2, scale * (ow2 / float(ow)), ctx)
        cv = Canvas(ow2, oh2, reuse=0)
    else:
        env = Env(layer, f, fps, ow, oh, scale, ctx)
        cv = Canvas(ow, oh, reuse=reuse)
    plan = _plan_for(cls, layer, env)
    cls.draw(layer, env, plan, cv)
    if cv.bbox is None:
        return None
    if layer.get('occlude', cls.name == 'behind_subject'):
        r = subject_mask(env, cv.bbox, region=True)
        if r is not None:
            sub, rx, ry = r
            cv.apply_mask(1.0 - sub, rx, ry)
    op = float(layer.get('opacity', 1.0))
    if op < 0.999:
        x0, y0, x1, y1 = cv.bbox
        cv.buf[y0:y1, x0:x1] *= np.float32(max(0.0, op))
        cv.opaque = False
    out = cv.result()
    if out is None:
        return None
    if low:
        big = cv2.resize(np.asarray(out), (int(ow), int(oh)), interpolation=cv2.INTER_LINEAR)
        x0, y0, x1, y1 = out.bbox
        sx, sy = ow / float(env.ow), oh / float(env.oh)
        res = big.view(LayerRGBA)
        res.bbox = (max(0, int(x0 * sx) - 1), max(0, int(y0 * sy) - 1), min(int(ow), int(math.ceil(x1 * sx)) + 1),
                    min(int(oh), int(math.ceil(y1 * sy)) + 1))
        res.opaque = out.opaque
        out = res
    return out, str(layer.get('blend', 'normal')).lower()


def render_layers(x, layers, f, fps, scale, ctx=None):
    """Render and composite every layer (in order) onto x (float32 (oh, ow, 3)); returns x. Reuses one scratch
    buffer (each layer is composited before the next is drawn)."""
    oh, ow = x.shape[:2]
    for L in layers or []:
        r = _render(L, f, fps, ow, oh, scale, ctx, 1)
        if r is not None:
            x = composite(x, r[0], r[1])
    return x


def layers_at(layers, f, fps, ctx=None):
    """Indices of layers whose span contains frame f."""
    out = []
    for i, L in enumerate(layers or []):
        try:
            a, b = layer_span(L, fps, ctx)
        except ValueError:
            continue
        if a <= f <= b:
            out.append(i)
    return out


def _md_layers(d):
    rows = ['| kind | description | params (defaults on 9:16) |', '|---|---|---|']
    for k, s in d.items():
        ps = ', '.join(f'{p}={json.dumps(v, ensure_ascii=False)}' for p, v in s['params'].items() if v is not None)
        al = f" (aliases: {', '.join(s['aliases'])})" if s['aliases'] else ''
        rows.append(f"| `{k}`{al} | {s['desc']} | {ps} |")
    return '\n'.join(rows)


def _main(argv=None):
    """CLI: registry [layers|caption_styles|all] [--md]  |  fonts TEXT [--font F] [--lang L] [--no-download]."""
    import argparse
    import sys
    ap = argparse.ArgumentParser(prog='ed_text.py', description='Edit Studio text layers')
    sub = ap.add_subparsers(dest='cmd')
    r = sub.add_parser('registry', help='print LAYER_KINDS / caption preset specs')
    r.add_argument('what', nargs='?', default='all', choices=['layers', 'caption_styles', 'all'])
    r.add_argument('--md', action='store_true')
    f = sub.add_parser('fonts', help='fonts a text needs (fetches CJK faces on demand)')
    f.add_argument('text')
    f.add_argument('--font', default='inter:700')
    f.add_argument('--lang')
    f.add_argument('--no-download', action='store_true')
    a = ap.parse_args(argv)
    if a.cmd == 'registry':
        d = describe(a.what)
        if a.md:
            if 'layers' in d:
                print('### layer kinds\n\nCommon: ' + COMMON_LAYER_DOC + '\n\n' + _md_layers(d['layers']) + '\n')
            if 'caption_styles' in d:
                print('### caption presets ("style": "<name>")\n\n| name | kinds | look | chunk hints |\n|---|---|---|---|')
                for n, c in d['caption_styles'].items():
                    print(f"| `{n}` | {', '.join(c['kinds'])} | {c['desc']} | {json.dumps(c['voice'])} |")
        else:
            print(json.dumps(d, indent=1, ensure_ascii=False))
        return 0
    if a.cmd == 'fonts':
        res = fonts_for_text(a.text, a.font, lang=a.lang, download=not a.no_download)
        res['shaping'] = shaping_info()
        print(json.dumps(res, indent=1, ensure_ascii=False))
        return 0 if not res['missing'] else 1
    ap.print_help(sys.stderr)
    return 2


if __name__ == '__main__':
    import sys as _sys
    _sys.exit(_main())
