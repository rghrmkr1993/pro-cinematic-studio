#!/usr/bin/env python3
"""Edit Studio - one command line for the whole engine.     python3 -I edit.py <command> -h   for details

Make an edit (each writes the next version edl_vN.json, a plan sheet, a fast labelled preview and a QA report)
  plan        footage + genre or style words (+ track)   edit.py plan --track T.wav --footage a.mp4 b.mp4 --style "dreamy retro" --project P
  variant     another version of a planned edit          edit.py variant P/edl_v2.json --variant 2      (avoids v2's choices)
  sequence    composite edit from a spec                 edit.py sequence spec.json --project P   (talk part + music edit ...)
  remake      redo a reference edit with your footage    edit.py remake --ref REF.mp4 --footage a.mp4 b.mp4 --project P
  storyboard  a video to generate, cut to the track      edit.py storyboard --track T.wav --style "gritty street" --project P
  fill        plug generated / own clips into gaps       edit.py fill P/edl_v1.json clips.json      ({"C03": "shot.mp4"})
Look and check
  plan-sheet  the plan as an image (#N, time, part, moves, gaps)   edit.py plan-sheet P/edl_v2.json
  render      preview (fast draft; --full = high quality) or --final, progress + ETA   edit.py render --project P --final --background
  frame       one frame at full output resolution (1:1 checks)   edit.py frame P/edl_v2.json 0:07.5 --out f.png
  status      progress of background jobs and renders            edit.py status P
  qa          measure a render against its timeline               edit.py qa P/edl_v2.json P/preview_v2.mp4
  measure-ref measure a clip of a named effect -> moves + params  edit.py measure-ref whip.gif --sheet whip.jpg
Change
  cmd         point edit -> next version     edit.py cmd P/edl_v2.json '{"op":"add","move":"zoom.crash","at":"0:07"}'
  validate    planner contract + renderer check of a timeline     edit.py validate P/edl_v3.json
Sound and speech
  track       music analysis (tempo, beats, drops)   edit.py track T.wav P/track.json --plot P/track.png
  voice       speech tools (transcribe, subs, jumpcuts, align, plan, models)   edit.py voice transcribe talk.mp4 --out w.json
Project
  pack        project -> one zip (timelines, notes, sources by relative path)  edit.py pack P --out P.edit.zip
  unpack      zip -> project; sources relinked by sha256 (else size+duration)  edit.py unpack P.edit.zip --project P
  fonts       which bundled fonts can set a text      edit.py fonts --text "Hello, world" --font anton
  doctor      environment check (exit 1 on a hard failure)   edit.py doctor

Common flags: --no-render, --no-qa, --full (high-quality preview), --background (long jobs: detached, poll status).
Errors are one line (ED_DEBUG=1: traceback). Versions are never overwritten: edl_v3 -> preview_v3.mp4, plan_v3.jpg.
"""
import os, sys, re, json, glob, copy, argparse, time, subprocess, importlib, inspect, hashlib, shutil, zipfile
import traceback
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
if sys.pycache_prefix is None:      # bytecode caches go to the user cache, never into the engine folder
    sys.pycache_prefix = os.path.join(os.environ.get('ED_ROOT', 'C:/Claude Code/cinema-studio/edit'), 'cache',
                                      'pycache')
os.environ.setdefault('OPENCV_LOG_LEVEL', 'ERROR')      # OpenCV's dnn backend notices are noise for users
E = None            # ed_edl, imported lazily (doctor / fonts / pack work without the renderer stack)


def _E():
    global E
    if E is None:
        import ed_edl
        E = ed_edl
    return E


def say(*a):
    print(*a, flush=True)


def warn(*a):
    print(*a, file=sys.stderr, flush=True)


class UserError(Exception):
    """A problem with the input (missing file, bad argument): reported in one line, exit code 2."""


def need(mod, fn=None):
    """Optional module (or function) or None, with the reason printed once."""
    try:
        m = _E().EXT.module(mod)
    except Exception:  # renderer stack unavailable: plain import
        try:
            m = importlib.import_module(mod)
        except Exception as e:
            warn(f'[edit] {mod} not available ({type(e).__name__}: {e})')
            return None
    if m is None:
        return None
    if fn is None:
        return m
    f = getattr(m, fn, None)
    if not callable(f):
        warn(f'[edit] {mod}.{fn}() not available')
        return None
    return f


def _exists(path, what='file'):
    if not path or not os.path.exists(path):
        raise UserError(f'{what} not found: {path}')
    return path


# ----------------------------------------------------------------------------- versions / paths
_VER = re.compile(r'^(?:edl|timeline)_v(\d+)\.json$')


def versions(project):
    out = []
    for p in glob.glob(os.path.join(project, 'edl_v*.json')) + glob.glob(os.path.join(project, 'timeline_v*.json')):
        m = _VER.match(os.path.basename(p))
        if m:
            out.append(int(m.group(1)))
    return sorted(set(out))


def latest_version(project):
    v = versions(project)
    return v[-1] if v else 0


def project_edl(project, version=None):
    if not os.path.isdir(project or ''):
        raise UserError(f'project folder not found: {project}')
    v = version or latest_version(project)
    for name in (f'edl_v{v}.json', f'timeline_v{v}.json'):
        p = os.path.join(project, name)
        if os.path.exists(p):
            return p
    raise UserError(f'no edl_v{v}.json in {project}' if v else f'no timeline (edl_vN.json) in {project} yet')


def version_of(path):
    m = _VER.match(os.path.basename(path))
    return int(m.group(1)) if m else None


def next_edl_path(edl_path):
    d = os.path.dirname(os.path.abspath(edl_path))
    if version_of(edl_path) is not None:
        return os.path.join(d, f'edl_v{latest_version(d) + 1}.json')
    stem = os.path.splitext(os.path.basename(edl_path))[0]
    m = re.match(r'^(.*)_v(\d+)$', stem)
    base, n = (m.group(1), int(m.group(2))) if m else (stem, 1)
    while os.path.exists(os.path.join(d, f'{base}_v{n + 1}.json')):
        n += 1
    return os.path.join(d, f'{base}_v{n + 1}.json')


def render_path(edl_path, final=False, frames=None):
    d = os.path.dirname(os.path.abspath(edl_path))
    v = version_of(edl_path)
    kind = 'final' if final else 'preview'
    part = f"_f{frames.replace(':', '-')}" if frames else ''
    if v is not None:
        return os.path.join(d, f'{kind}_v{v}{part}.mp4')
    return os.path.join(d, f'{os.path.splitext(os.path.basename(edl_path))[0]}.{kind}{part}.mp4')


def sheet_path(edl_path):
    d = os.path.dirname(os.path.abspath(edl_path))
    v = version_of(edl_path)
    return os.path.join(d, f'plan_v{v}.jpg' if v is not None else f'{os.path.splitext(os.path.basename(edl_path))[0]}.plan.jpg')


def qa_dir(video):
    d = os.path.dirname(os.path.abspath(video))
    stem = os.path.splitext(os.path.basename(video))[0]
    m = re.match(r'^(preview|final)_v(\d+)$', stem)
    if m:
        return os.path.join(d, f"qa_v{m.group(2)}{'_final' if m.group(1) == 'final' else ''}")
    return os.path.join(d, f'qa_{stem}')


def load_json(path):
    _exists(path)
    with open(path, encoding='utf-8') as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as e:
            raise UserError(f'{path} is not valid JSON ({e})')


def save_json(obj, path):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    return path


def parse_canvas(s):
    try:
        w, h = map(int, s.lower().split('x'))
    except ValueError:
        raise UserError(f'--canvas must look like 1080x1920, got {s!r}')
    return w, h


def fmt_s(s):
    if s is None:
        return '?'
    s = int(round(s))
    return f'{s // 60}:{s % 60:02d}'


# ----------------------------------------------------------------------------- progress
class Progress:
    """Frame progress of a render: a line on stderr every ~10 s or 10 % (first frame and the end always) and
    <out>.progress.json for `edit.py status`. Accepts (done, total), a dict {done|frames, total, stage} or kw."""

    def __init__(self, total, label='render', path=None, min_gap=3.0, every=10.0, quiet=False):
        self.total, self.label, self.path, self.quiet = max(1, int(total or 1)), label, path, quiet
        self.min_gap, self.every = min_gap, every
        self.t0 = time.time()
        self.last_t, self.last_dec, self.done, self.stage = 0.0, -1, 0, 'rendering'
        self._write(force=True)

    def __call__(self, *a, **kw):
        done, total, stage = None, None, kw.get('stage')
        if a and isinstance(a[0], dict):
            d = a[0]
            done, total, stage = d.get('done', d.get('frames')), d.get('total'), d.get('stage', stage)
        else:
            if a:
                done = a[0]
            if len(a) > 1:
                total = a[1]
            done, total = kw.get('done', done), kw.get('total', total)
        if total:
            self.total = max(1, int(total))
        if stage:
            self.stage = stage
        if done is not None:
            self.update(int(done))

    def eta(self):
        el = time.time() - self.t0
        if self.done <= 0 or el <= 0:
            return None, 0.0
        fps = self.done / el
        return (self.total - self.done) / fps, fps

    def update(self, done):
        self.done = done
        now = time.time()
        dec = int(10 * done / self.total)
        end = done >= self.total
        if end or done == 1 or (now - self.last_t >= self.min_gap and (dec > self.last_dec or now - self.last_t >= self.every)):
            self.last_t, self.last_dec = now, dec
            eta, fps = self.eta()
            if not self.quiet:
                warn(f'[{self.label}] {done}/{self.total} frames {100 * done / self.total:3.0f}%  {fps:.1f} fps  '
                     f'elapsed {fmt_s(now - self.t0)}  ETA {fmt_s(0 if end else eta)}')
            self._write()

    def finish(self, stage='done', **extra):
        self.stage = stage
        self._write(force=True, **extra)

    def _write(self, force=False, **extra):
        if not self.path:
            return
        eta, fps = self.eta()
        rec = dict(pid=os.getpid(), label=self.label, done=self.done, total=self.total, stage=self.stage,
                   fps=round(fps, 2), elapsed_s=round(time.time() - self.t0, 1),
                   eta_s=None if eta is None else round(eta, 1), updated=time.strftime('%Y-%m-%dT%H:%M:%S'), **extra)
        try:
            with open(self.path + '.tmp', 'w') as fh:
                json.dump(rec, fh)
            os.replace(self.path + '.tmp', self.path)
        except OSError:
            pass


def progress_path(out):
    return out + '.progress.json'


def _attach_progress(r, prog):
    """kwargs that hand a Progress to Renderer.render(progress=callable(done, total)) - empty for a renderer
    without that parameter (its own progress lines still show)."""
    try:
        params = inspect.signature(r.render).parameters
    except (TypeError, ValueError):
        params = {}
    return {'progress': prog} if 'progress' in params else {}


# ----------------------------------------------------------------------------- render / QA
def render(edl_path, out=None, final=False, labels=None, frames=None, interp=None, workers=None, stills=None, at=None,
           fast=False, draft=False):
    """Render an EDL (or a legacy timeline with 'clips') -> output path (stills: the contact sheet path).
    draft (previews): 540x960, optical flow only where the crop samples (fast) and blend interpolation.
    A full preview (draft=False) and the final use the EDL's frame_interp, else optical flow."""
    E_ = _E()
    edl = load_json(edl_path)
    own = edl.get('frame_interp')
    if draft and not final:
        fast, interp = True, interp or ('nearest' if own == 'nearest' else 'blend')
    else:
        interp = interp or own or 'flow'
    labels = (not final) if labels is None else labels
    if 'clips' in edl and 'segments' not in edl:
        import ed_render as RD   # first engine's timeline format
        out = out or render_path(edl_path, final)
        RD.render(edl, out, preview=not final, labels=labels)
        say('[render]', out, '(legacy timeline)')
        return out
    for name, src in (edl.get('sources') or {}).items():
        if not os.path.exists(src.get('path') or ''):
            raise UserError(f"source '{name}' not found: {src.get('path')} (unpack the project or fix sources.{name}.path)")
    r = E_.Renderer(edl, preview=not final, labels=labels, frame_interp=interp, workers=workers, fast=fast and not final)
    if stills:
        st = r.render(None, stills=E_.parse_at(at, edl))
        E_.contact(st, stills, edl=edl)
        say('[stills]', len(st), '->', stills)
        return stills
    rng = None
    if frames:
        try:
            rng = tuple(map(int, frames.split(':')))
        except ValueError:
            raise UserError(f'--frames must look like 120:240, got {frames!r}')
    out = out or render_path(edl_path, final, frames)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    n = (min(rng[1], edl['n_frames'] - 1) - max(0, rng[0]) + 1) if rng else edl['n_frames']
    kind = 'final' if final else 'preview'
    warn(f"[render] {kind} {r.ow}x{r.oh} {n} frames ({n / edl['canvas']['fps']:.1f} s) -> {out}")
    own = hasattr(E_, '_Progress')       # the renderer prints its own progress lines: pass them through, count quietly
    prog = Progress(n, 'render', progress_path(out), quiet=own)
    kw = _attach_progress(r, prog)
    try:
        r.render(out, frame_range=rng, **kw)
    except BaseException as e:
        prog.finish('failed', error=f'{type(e).__name__}: {e}'[:300])
        raise
    t = r.report['timing']
    prog.done = r.report['rendered']['frames']
    prog.finish('done', out=out)
    mods = {k: v for k, v in r.report['modules'].items() if k != 'calls'}
    say('[render]', out, f"{r.report['rendered']['frames']} frames, {t['wall_s']} s ({t['fps']} fps, {t['workers']} workers)",
        f"audio={(r.report.get('audio') or {}).get('method')}", json.dumps(mods))
    return out


def qa(edl_path, video, out_dir=None, as_json=False):
    out_dir = out_dir or qa_dir(video)
    _exists(edl_path, 'timeline')
    _exists(video, 'video')
    run = need('ed_qa', 'run')
    res = None
    if run is not None:
        try:
            res = run(edl_path, video, out_dir)
        except Exception as e:  # keep the render; fall back to the minimal checks
            warn(f'[qa] ed_qa.run failed ({type(e).__name__}: {e}); minimal checks only')
    if res is None:
        res = qa_minimal(edl_path, video, out_dir)
    if as_json:
        say(json.dumps(res, ensure_ascii=False, indent=1, default=str))
        return res
    lines = res.get('verdict_lines') or res.get('verdict') or []
    if isinstance(lines, str):
        lines = [lines]
    md = (res.get('files') or {}).get('md') or os.path.join(out_dir, 'qa.json')
    say(f"[qa] {str(res.get('status', '?')).upper()} -> {md}")
    for ln in lines:                     # every check (storyboards have 13), never truncated
        say('  ' + str(ln))
    return res


def qa_minimal(edl_path, video, out_dir):
    """Built-in QA when ed_qa is unavailable: frame count / duration, loudness, render report problems."""
    E_ = _E()
    os.makedirs(out_dir, exist_ok=True)
    edl = load_json(edl_path)
    info = E_.V.probe(video)
    fps = edl['canvas']['fps']
    res = dict(duration=info.get('duration'), expected=round(edl['n_frames'] / fps, 3), frames=info.get('nb_frames'))
    verdict = []
    if info.get('nb_frames') and int(info['nb_frames']) != int(edl['n_frames']):
        verdict.append(f"{info['nb_frames']} frames, EDL {edl['n_frames']}")
    if info.get('has_audio'):
        res['lufs'], res['true_peak'] = E_._ebur128(video)
        lo = (edl.get('audio') or {}).get('loudness') or {}
        if res['lufs'] is not None and lo.get('lufs') is not None and abs(res['lufs'] - lo['lufs']) > 1.0:
            verdict.append(f"loudness {res['lufs']} LUFS (target {lo['lufs']})")
    side = E_.sidecar_path(video)
    if os.path.exists(side):
        rep = load_json(side)
        res['modules'] = rep.get('modules')
        W, H = rep['canvas']['w'], rep['canvas']['h']
        off = sorted({r['f'] for r in rep['frames'] for b in (r.get('texts') or []) + [x['bbox'] for x in r.get('layers', [])]
                      if b and (b[0] < 0 or b[1] < 0 or b[2] > W or b[3] > H)})
        if off:
            verdict.append(f'text outside the frame on {len(off)} frames (first {off[0]})')
    res['verdict'] = verdict or ['ok']
    res['status'] = 'ok' if not verdict else 'warn'
    save_json(res, os.path.join(out_dir, 'qa.json'))
    return res


def after_edit(edl_path, a, final=False, sheet=True):
    """Plan sheet + render + QA of a freshly written EDL version (unless --no-sheet / --no-render / --no-qa)."""
    if sheet and not getattr(a, 'no_sheet', False):
        try:
            plan_sheet(edl_path, sheet_path(edl_path))
        except Exception as e:  # the sheet is a convenience: never block the render
            warn(f'[plan-sheet] failed ({type(e).__name__}: {e})')
    if getattr(a, 'no_render', False):
        return None
    full = getattr(a, 'full', False)
    out = render(edl_path, final=final, workers=getattr(a, 'workers', None), fast=getattr(a, 'fast', False) and not full,
                 draft=not full)
    if not getattr(a, 'no_qa', False):
        qa(edl_path, out)
    return out


def _n(k, word):
    return f"{k} {word}{'' if k == 1 else 's'}"


def check_edl(edl):
    """Both validators on an EDL dict, quietly -> (errors, warnings, validators that ran)."""
    errs, warns, ran = [], [], []
    v = need('ed_plan', 'validate_edl')
    if v is not None:
        try:
            e_, w_ = v(edl)
            errs += [f'plan: {x}' for x in e_]
            warns += [f'plan: {x}' for x in w_]
            ran.append('plan')
        except Exception as e:  # validator problems never block rendering
            warn(f'[validate] ed_plan.validate_edl failed: {e!r}')
    rv = getattr(_E(), 'validate', None)
    if callable(rv):
        try:
            for p in rv(edl):
                (errs if p.get('level') == 'error' else warns).append(f"render: {p.get('where')}: {p.get('msg')}")
            ran.append('render')
        except Exception as e:  # noqa: BLE001
            warn(f'[validate] ed_edl.validate failed: {e!r}')
    return errs, warns, ran


def validate(edl_path, verbose=False):
    """Planner contract (ed_plan.validate_edl) + renderer check (ed_edl.validate: files, ranges, overlaps, unknown fx /
    transition / layer kinds) -> (errors, warnings) or None when neither validator is available."""
    errs, warns, ran = check_edl(load_json(edl_path))
    if not ran:
        return None
    lim = 50 if verbose else 6
    wtxt = ('| warnings: ' + '; '.join(map(str, warns[:lim]))) if warns else ''
    if not errs:
        say(f"[validate] ({' + '.join(ran)}) OK", wtxt)
        return errs, warns
    say(f"[validate] ({' + '.join(ran)}) {_n(len(errs), 'error')}")
    for who in ran:                              # each validator gets its own line, so one cannot hide the other
        mine = [x[len(who) + 2:] for x in errs if x.startswith(who + ': ')]
        if mine:
            more = f' (+{len(mine) - lim} more, --verbose)' if len(mine) > lim else ''
            say(f"  {who}: {_n(len(mine), 'error')}: " + '; '.join(mine[:lim]) + more)
    if wtxt:
        say(' ', wtxt)
    return errs, warns


def new_version_path(project):
    return os.path.join(project, f'edl_v{latest_version(project) + 1}.json')


# ----------------------------------------------------------------------------- plan / sequence / remake
PLAN_OPTS = (('n_shots', 'n_shots'), ('order', 'order'), ('require_moves', 'require'), ('forbid_moves', 'forbid'),
             ('music_in', 'music_in'), ('drop_at', 'drop_at'), ('drop_t', 'drop_t'), ('bpm', 'bpm'), ('bars', 'bars'),
             ('cut_rate', 'cut_rate'), ('sfx_level', 'sfx_level'), ('words', 'words'), ('lang', 'lang'),
             ('voice', 'voice'), ('src_in', 'src_in'), ('src_out', 'src_out'), ('from', 'from_phrase'),
             ('to', 'to_phrase'), ('subtitles', 'subtitles'), ('style', 'style'), ('variant', 'variant'),
             ('avoid', 'avoid'))


def plan_opts(a):
    """argparse namespace -> ed_plan.plan_genre options (only the ones given)."""
    opts = {}
    for key, attr in PLAN_OPTS:
        v = getattr(a, attr, None)
        if v is None:
            continue
        if key in ('require_moves', 'forbid_moves'):
            v = [m.strip() for x in v for m in str(x).split(',') if m.strip()]
        if key == 'avoid':
            for x in v:
                _exists(x, 'earlier version (--avoid)')
            v = [os.path.abspath(x) for x in v]
        if key in ('words', 'voice'):
            _exists(v, key)
            v = os.path.abspath(v)
        opts[key] = v
    return opts


def _speech_genre(genre, style):
    """True when the genre (or the style's genre) cuts by words, so the track is optional."""
    P_ = need('ed_plan')
    if P_ is None:
        return False
    try:
        g = genre or (P_.resolve_style(style)['genre'] if style and callable(getattr(P_, 'resolve_style', None)) else None)
        if not g:
            return False
        card = P_.load_genre(g)
        kind = card.get('kind')
        gk = getattr(P_, 'genre_kind', None)
        return (gk(kind) if callable(gk) else kind) == 'speech' and P_.resolve_genre(g) != 'motivation'
    except Exception:  # unknown genre: the planner reports it
        return False


def cmd_plan(a):
    plan_genre = need('ed_plan', 'plan_genre')
    if plan_genre is None:
        raise UserError('ed_plan.plan_genre is not available: genre planning needs engine/ed_plan.py')
    if not a.genre and not a.style:
        raise UserError('plan needs --genre or --style (a preset name or plain words, e.g. "clean and expensive")')
    if a.track:
        _exists(a.track, 'track')
    elif not _speech_genre(a.genre, a.style):
        raise UserError('--track is required for music genres (speech genres - clips, ugc, explainer - can do without)')
    for f in a.footage:
        _exists(f, 'footage')
    bg = _bg(a, a.project)
    if bg:
        return bg
    os.makedirs(a.project, exist_ok=True)
    t = time.time()
    opts = dict(cache_dir=os.path.join(a.project, '.ed_cache'), seed=a.seed, reframe=not a.no_reframe,
                sample_fps=a.sample_fps)
    for k in ('title', 'word', 'outro_text'):
        if getattr(a, k, None):
            opts[k] = getattr(a, k)
    opts.update(plan_opts(a))
    edl = plan_genre(a.track, a.footage, a.genre, parse_canvas(a.canvas), a.fps, a.dur, **opts)
    if a.sfx_dir:
        _exists(a.sfx_dir, 'sound effects folder')
        edl.setdefault('audio', {})['sfx_dir'] = os.path.abspath(a.sfx_dir)
    path = save_json(edl, new_version_path(a.project))
    sty = (edl.get('meta') or {}).get('style')
    say('[plan]', path, f"{len(edl['segments'])} segments, {edl['n_frames']} frames, {time.time() - t:.0f} s"
        + (f"; style {sty.get('name') if isinstance(sty, dict) else sty}" if sty else ''))
    validate(path)
    explain = need('ed_plan', 'explain')
    if explain is not None:
        try:
            say(explain(edl))
        except Exception as e:  # explanation is informational only
            warn(f'[plan] explain failed: {e!r}')
    after_edit(path, a)
    return path


def _strip_style_options(P_, opts, old_style):
    """Options a style put into meta.options (its avoided moves, SFX level, cutting rate) - removed when a variant
    switches to another style, so the old style does not leak into the new one."""
    pre = (getattr(P_, 'STYLE_PRESETS', {}) or {}).get(str(old_style or '').strip().lower().replace(' ', '_'))
    if not pre and old_style and callable(getattr(P_, 'resolve_style', None)):
        try:
            pre = P_.STYLE_PRESETS.get(P_.resolve_style(old_style).get('name'))
        except Exception:  # unknown words: nothing to strip
            pre = None
    if not pre:
        return opts
    o = dict(opts)
    avoid = set((pre.get('moves') or {}).get('avoid') or [])
    if o.get('forbid'):
        o['forbid'] = [m for m in o['forbid'] if m not in avoid]
    if o.get('sfx_level') == ('light' if pre.get('sfx_level') == 'light' else 'genre'):
        o.pop('sfx_level')
    if o.get('cut_rate') is not None and abs(float(o['cut_rate']) - float((pre.get('pacing') or {}).get('cut_rate', 1.0))) < 1e-6:
        o.pop('cut_rate')
    return o


def replan_variant(edl_path, variant, style=None, avoid=(), log=say):
    """Another version of a timeline from its own inputs: ed_sequence.variant for composites, plan_storyboard for
    storyboards, else plan_genre with the recorded track, footage, genre, options and length, variant N, the given
    (or recorded) style and avoid = this version + the ones it already avoided + `avoid`."""
    edl = load_json(edl_path)
    meta = edl.get('meta') or {}
    project = os.path.dirname(os.path.abspath(edl_path))
    cache = os.path.join(project, '.ed_cache')
    if meta.get('scenario') == 'sequence' or (isinstance(meta.get('sequence'), dict) and meta['sequence'].get('spec')):
        S = need('ed_sequence')                          # a composite: re-planned from its stored spec
        fn = getattr(S, 'variant', None) if S is not None else None
        if not callable(fn):
            raise UserError('ed_sequence.variant is not available')
        err = getattr(S, 'SpecError', ValueError)
        if avoid:
            log('[variant] note: --avoid is not used for composites (ed_sequence.variant avoids the versions in the spec)')
        try:
            return fn(os.path.abspath(edl_path), variant, style, cache_dir=cache, log=lambda *x, **k: log(*x))
        except err as e:
            raise UserError(f'spec problem: {e}')
    if meta.get('scenario') == 'remake':
        raise UserError('a remake has no variants (its timing is the reference): swap shots with edit.py remake --pick')
    P_ = need('ed_plan')
    if P_ is None:
        raise UserError('ed_plan is not available')
    opts = dict(meta.get('options') or {})
    old_style = meta.get('style') or opts.get('style')
    if style and old_style:
        opts = _strip_style_options(P_, opts, old_style)
    prev = [x for x in (opts.get('avoid') or []) if isinstance(x, str) and os.path.exists(x)]
    for k in ('style', 'variant', 'avoid'):
        opts.pop(k, None)
    av = list(dict.fromkeys([os.path.abspath(edl_path)] + prev + [os.path.abspath(x) for x in (avoid or [])]))
    track = (meta.get('track') or {}).get('path') if isinstance(meta.get('track'), dict) else meta.get('track')
    fp = meta.get('footage')
    clips = fp.get('clips') if isinstance(fp, dict) else (fp if isinstance(fp, list) else None)
    footage = [c['path'] if isinstance(c, dict) else c for c in (clips or [])] or \
        list(dict.fromkeys(sc['path'] for sc in (edl.get('sources') or {}).values()))
    canvas = (int(edl['canvas']['w']), int(edl['canvas']['h']))
    fps = edl['canvas']['fps']
    genre = None if style else meta.get('genre')
    st = style or (old_style if isinstance(old_style, str) else None)
    speech = _speech_genre(meta.get('genre'), None)
    dur = None if speech else round(edl['n_frames'] / float(fps), 3)
    for p in [track] + footage:
        if p and not os.path.exists(p):
            raise UserError(f'input of the original plan not found: {p} (unpack the project or upload it again)')
    if meta.get('scenario') == 'storyboard':
        sb = meta.get('storyboard') or {}
        new = P_.plan_storyboard(track, genre=genre, style=st, dur=dur, brief=sb.get('brief'), canvas=canvas, fps=fps,
                                 n_shots=opts.get('n_shots'), character=sb.get('character'), cache_dir=cache,
                                 variant=variant, avoid=av)
    else:
        new = P_.plan_genre(track, footage, genre, canvas, fps, dur, cache_dir=cache, style=st, variant=variant, avoid=av,
                            **{k: v for k, v in opts.items() if k not in ('cache_dir', 'log', 'footage_obj', 'music')})
    if (edl.get('audio') or {}).get('sfx_dir'):
        new.setdefault('audio', {})['sfx_dir'] = edl['audio']['sfx_dir']
    return new


def _choice_summary(old, new):
    """What changed between two versions (style, transitions, looks, grade) - one line."""
    mo, mn = old.get('meta') or {}, new.get('meta') or {}
    co, cn = mo.get('choices') or {}, mn.get('choices') or {}
    parts = [f"style {cn.get('style') or mn.get('style') or 'none'}, variant {cn.get('variant', mn.get('variant'))}"]
    for k in ('transitions', 'looks'):
        a_, b_ = co.get(k) or [], cn.get(k) or []
        if a_ != b_:
            parts.append(f"{k} {', '.join(map(str, a_)) or '-'} -> {', '.join(map(str, b_)) or '-'}")
    ga, gb = (co.get('grade') or {}).get('preset'), (cn.get('grade') or {}).get('preset')
    if ga != gb:
        parts.append(f"grade {ga or '-'} -> {gb or '-'}")
    ta, tb = ((co.get('sequence') or {}).get('transitions') or {}), ((cn.get('sequence') or {}).get('transitions') or {})
    if ta != tb and isinstance(ta, dict) and isinstance(tb, dict):      # composites: transitions into each part
        parts.append('part transitions ' + ', '.join(f'{k} {ta.get(k) or "-"} -> {tb.get(k) or "-"}'
                                                     for k in sorted(set(ta) | set(tb)) if ta.get(k) != tb.get(k)))

    def shots(m, c):
        if m.get('slots'):
            return [str(sl.get('shot') or sl.get('src')) for sl in m['slots']]
        return [f'{x[1]}@{round(float(x[2]), 1)}' for x in c.get('shots') or [] if isinstance(x, list) and len(x) >= 3]
    so, sn = shots(mo, co), shots(mn, cn)
    if so and sn:
        diff = sum(1 for i, x in enumerate(sn) if i >= len(so) or so[i] != x)
        parts.append(f'shots: {diff} of {len(sn)} changed')
    return '; '.join(parts)


def cmd_variant(a):
    _exists(a.edl, 'timeline')
    bg = _bg(a, os.path.dirname(os.path.abspath(a.edl)))
    if bg:
        return bg
    t = time.time()
    new = replan_variant(a.edl, a.variant, style=a.style, avoid=a.avoid)
    project = os.path.dirname(os.path.abspath(a.edl))
    path = save_json(new, os.path.join(project, f'edl_v{latest_version(project) + 1}.json'))
    say('[variant]', path, f"{len(new['segments'])} segments, {new['n_frames']} frames, {time.time() - t:.0f} s")
    say('  ' + _choice_summary(load_json(a.edl), new))
    _gate(new, path)
    after_edit(path, a)
    return path


def cmd_storyboard(a):
    P_ = need('ed_plan')
    fn = getattr(P_, 'plan_storyboard', None) if P_ is not None else None
    if not callable(fn):
        raise UserError('ed_plan.plan_storyboard is not available')
    _exists(a.track, 'track')
    if not a.genre and not a.style and not a.brief:
        raise UserError('storyboard needs --genre, --style or --brief')
    bg = _bg(a, a.project)
    if bg:
        return bg
    os.makedirs(a.project, exist_ok=True)
    t = time.time()
    kw = dict(genre=a.genre, style=a.style, dur=a.dur, brief=a.brief, canvas=parse_canvas(a.canvas), fps=a.fps,
              n_shots=a.n_shots, character=a.character, cache_dir=os.path.join(a.project, '.ed_cache'))
    if a.variant is not None:
        kw['variant'] = a.variant
    edl = fn(a.track, **kw)
    path = save_json(edl, new_version_path(a.project))
    gaps = (edl.get('meta') or {}).get('gaps') or []
    say('[storyboard]', path, f"{len(edl['segments'])} slots, {edl['n_frames']} frames "
                              f"({edl['n_frames'] / edl['canvas']['fps']:.1f} s), {len(gaps)} shots to generate, {time.time() - t:.0f} s")
    for gp in gaps[:40]:
        b = gp.get('brief') or {}
        tt = gp.get('t') or [0, 0]
        say(f"  {gp.get('id')} {tt[0]:6.2f}-{tt[1]:6.2f}s {b.get('shot_size', '')}: {str(b.get('prompt', ''))[:110]}")
    say('  next: generate the shots with edit-gen (cost first, only after a yes), then: '
        f'edit.py fill {path} clips.json')
    validate(path)
    after_edit(path, a)
    return path


def _parse_map(s):
    s = s.strip()
    if s.startswith('{'):
        try:
            return json.loads(s)
        except json.JSONDecodeError as e:
            raise UserError(f'MAP is not valid JSON ({e})')
    return load_json(s)


def cmd_fill(a):
    P_ = need('ed_plan')
    fn = getattr(P_, 'fill_gaps', None) if P_ is not None else None
    if not callable(fn):
        raise UserError('ed_plan.fill_gaps is not available')
    edl = load_json(a.edl)
    mp = _parse_map(a.map)
    if not isinstance(mp, dict) or not mp:
        raise UserError('MAP must be {slot: path | {"path": ..., "t": ...}}')
    fixed = {}
    for k, v in mp.items():
        p = v if isinstance(v, str) else (v or {}).get('path')
        _exists(p, f'clip for slot {k}')
        fixed[k] = os.path.abspath(p) if isinstance(v, str) else dict(v, path=os.path.abspath(p))
    project = os.path.dirname(os.path.abspath(a.edl))
    try:
        new = fn(edl, fixed, cache_dir=os.path.join(project, '.ed_cache'), log=lambda *x, **k: say(*x))
    except (KeyError, ValueError, IndexError) as e:
        raise UserError(f'fill refused: {e}')
    out = a.out or next_edl_path(a.edl)
    save_json(new, out)
    hist = ((new.get('meta') or {}).get('history') or [None])[-1]
    left = [g.get('id') for g in (new.get('meta') or {}).get('gaps') or [] if not g.get('filled')]
    say('[fill]', out, json.dumps(hist, ensure_ascii=False)[:300] if hist else '',
        f'| gaps left: {", ".join(map(str, left))}' if left else '')
    validate(out)
    after_edit(out, a)
    return out


def cmd_measure_ref(a):
    if re.match(r'^[a-z][a-z0-9+.-]*://', a.clip, re.I):
        raise UserError('measure-ref needs a local file; links are not downloaded (for a video on a social platform: '
                        'the original file or a screen recording you have the rights to)')
    _exists(a.clip, 'clip')
    R = need('ed_remake')
    fn = getattr(R, 'measure_effect', None) if R is not None else None
    if not callable(fn):
        raise UserError('ed_remake.measure_effect is not available')
    win = {}
    try:
        if a.t_from:
            win['start'] = _secs(a.t_from)
        if a.t_to:
            win['end'] = _secs(a.t_to)
    except ValueError:
        raise UserError(f'--from / --to must be times like 0:12.5 or 12.5, got {a.t_from!r} / {a.t_to!r}')
    if win.get('end') is not None and win['end'] <= win.get('start', 0.0):
        raise UserError('--to must be after --from')
    try:
        res = fn(a.clip, fps=a.fps, sheet=a.sheet, **win)
    except TypeError:                     # an older ed_remake without windows
        if win:
            raise UserError('this ed_remake cannot measure a window (--from / --to)')
        res = fn(a.clip, fps=a.fps, sheet=a.sheet)
    if a.json:
        say(json.dumps(res, ensure_ascii=False, indent=1))
        return res
    ev = [e for e in res['events'] if e['type'] != 'cut']
    cuts = [e['t0'] for e in res['events'] if e['type'] == 'cut']
    w = res.get('window') or [0.0, res['duration']]
    span = f" (window {w[0]:.2f}-{w[1]:.2f} s)" if w[0] > 0 else ''
    say(f"[measure-ref] {os.path.basename(a.clip)}{span}: {res['duration']} s @ {res['fps']:g} fps, {len(cuts)} cut(s)"
        + (f" at {', '.join(f'{c:.2f}' for c in cuts[:8])} s" if cuts else '') + f", {len(ev)} event(s)")
    for e in ev[:12]:
        keys = [k for k in ('kind', 'scale', 'dur', 'dir', 'axis', 'frames', 'amp', 'rot', 'tau', 'ratio', 'angle', 'color')
                if e.get(k) is not None]
        say(f"  {e['t0']:.2f}-{e['t1']:.2f}s {e['type']}: " + ', '.join(f'{k} {e[k]}' for k in keys))
    if not res['candidates']:
        say('  no move recognised (try a shorter clip around the effect, or --sheet to look at the curves)')
    for c in res['candidates'][:a.top]:
        say(f"  {c['score']:.2f} {c['move']:16s} {json.dumps(c['params'], ensure_ascii=False)[:120]}  - {c['why']}")
        if c.get('apply'):
            say(f"       apply: {json.dumps(c['apply'], ensure_ascii=False)[:160]}")
    if res.get('sheet'):
        say(f"  sheet: {res['sheet']}")
    return res


SPEC_PATH_KEYS = {'source', 'footage', 'path', 'file', 'track', 'music', 'words', 'transcript', 'image', 'logo', 'font',
                  'sources', 'media', 'video', 'audio_path'}


def resolve_spec_paths(obj, base):
    """Relative file paths in a spec -> absolute, relative to the spec's folder (when the file exists there)."""
    def fix(v):
        if isinstance(v, str) and v and not os.path.isabs(v) and not v.startswith(('http:', 'https:')):
            p = os.path.normpath(os.path.join(base, v))
            if os.path.exists(p):
                return p
        return v
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in SPEC_PATH_KEYS:
                v = [fix(x) for x in v] if isinstance(v, list) else fix(v) if isinstance(v, str) else resolve_spec_paths(v, base)
            else:
                v = resolve_spec_paths(v, base)
            out[k] = v
        return out
    if isinstance(obj, list):
        return [resolve_spec_paths(x, base) for x in obj]
    return obj


EXAMPLE_SPEC = {
    "canvas": {"w": 1080, "h": 1920, "fps": 30},
    "parts": [
        {"type": "talk", "id": "talk", "source": "podcast.mp4",
         "from": {"phrase": "first words of the clip"}, "to": {"phrase": "last words", "end": "after_reaction"},
         "remove": [{"phrase": "a sentence to drop"}], "crop": "speaker", "subtitles": "subtitle", "music_db": -18},
        {"type": "edit", "id": "hype", "footage": ["shot1.mp4", "shot2.mp4"], "order": "given", "genre": "epic",
         "bars": 5, "shots": 5, "moves": ["time.speed_ramp"], "sfx": "heavy"}],
    "music": {"path": "track.wav", "drop_at": {"part": "hype", "at": "start"}},
    "transitions": [{"from": "talk", "to": "hype", "kind": "flash", "sfx": "impact"}]}


def cmd_sequence(a):
    S = need('ed_sequence')
    if not a.spec and not a.example:
        raise UserError('give SPEC.json (edit.py sequence --example prints a spec to start from)')
    if a.example:
        ex = getattr(S, 'EXAMPLE', None) if S is not None else None
        if callable(getattr(S, 'example_spec', None)):
            ex = S.example_spec()
        if isinstance(ex, str):
            say(ex.rstrip())
        elif isinstance(ex, dict):
            say(json.dumps(ex, ensure_ascii=False, indent=1))
        elif S is not None and callable(getattr(S, 'main', None)):
            S.main(['example'])
        else:
            say(json.dumps(EXAMPLE_SPEC, ensure_ascii=False, indent=1))
        return None
    plan = getattr(S, 'plan_sequence', None) if S is not None else None
    if not callable(plan):
        raise UserError('ed_sequence.plan_sequence is not available (engine/ed_sequence.py)')
    if not a.project:
        raise UserError('sequence needs --project DIR')
    _exists(a.spec, 'spec')
    bg = _bg(a, a.project)
    if bg:
        return bg
    # ed_sequence reads the file itself (comments allowed, paths relative to the spec); an older one gets a dict
    spec = os.path.abspath(a.spec) if callable(getattr(S, 'load_spec', None)) else \
        resolve_spec_paths(load_json(a.spec), os.path.dirname(os.path.abspath(a.spec)))
    os.makedirs(a.project, exist_ok=True)
    t = time.time()
    cache = a.cache or os.path.join(a.project, '.ed_cache')
    spec_err = getattr(S, 'SpecError', None)
    try:
        edl = plan(spec, cache_dir=cache, log=lambda *x, **k: say(*x))       # its lines carry their own tags
    except Exception as e:
        if spec_err is not None and isinstance(e, spec_err):
            raise UserError(f'spec problem: {e}')
        raise
    path = save_json(edl, new_version_path(a.project))
    parts = (edl.get('meta') or {}).get('parts') or []
    say('[sequence]', path, f"{len(edl['segments'])} segments, {edl['n_frames']} frames "
                            f"({edl['n_frames'] / edl['canvas']['fps']:.1f} s), {time.time() - t:.0f} s")
    for p in parts if isinstance(parts, list) else []:
        say(f"  part {p.get('id')} ({p.get('type')}): frames {p.get('f0')}-{p.get('f1')}"
            + (f" = {p['t0']:.2f}-{p['t1']:.2f} s" if p.get('t0') is not None and p.get('t1') is not None else ''))
    for n in ((edl.get('meta') or {}).get('notes') or [])[:8] if isinstance((edl.get('meta') or {}).get('notes'), list) else []:
        say(f'  note: {n}')
    _gate(edl, path)
    after_edit(path, a)
    return path


def _gate(edl, path):
    """Validation before a render: the planner's own meta.validation errors and both validators. Errors -> the
    timeline is kept (versions are never lost) but not rendered, and the command exits non-zero with the reason."""
    problems = _validation_errors(edl)
    res = validate(path)
    if problems or (res and res[0]):
        why = problems or [str(x) for x in res[0]]
        raise UserError(f'{len(why)} validation error(s) in {os.path.basename(path)}: ' + '; '.join(why[:5])
                        + (' ...' if len(why) > 5 else '') + f' (kept, not rendered; edit.py render {path} renders it anyway)')


def _validation_errors(edl):
    """meta.validation errors a planner recorded ({"errors": [str | {where, msg}], ...} or a list) -> strings."""
    v = (edl.get('meta') or {}).get('validation')
    errs = v.get('errors') if isinstance(v, dict) else (v if isinstance(v, list) else [])
    out = []
    for x in errs or []:
        if isinstance(x, dict):
            out.append(': '.join(str(x[k]) for k in ('where', 'msg', 'message') if x.get(k) is not None) or json.dumps(x)[:200])
        else:
            out.append(str(x))
    return out


def _remake_dir(project):
    return os.path.join(project, 'remake')


def cmd_remake(a):
    bg = _bg(a, a.project) if (a.pick or (a.ref and a.footage and all(os.path.exists(x) for x in [a.ref] + a.footage))) else None
    if bg:
        return bg
    if a.pick:
        return remake_pick(a)
    if not a.ref or not a.footage:
        raise UserError('remake needs --ref REF and --footage F [F ...] (or --pick SLOT=TIME on an existing project)')
    _exists(a.ref, 'reference')
    for f in a.footage:
        _exists(f, 'footage')
    if a.music:
        _exists(a.music, 'music track')
    R = need('ed_remake')
    draft = getattr(R, 'draft', None) if R is not None else None
    os.makedirs(a.project, exist_ok=True)
    t = time.time()
    if draft is None:
        warn('[remake] ed_remake.draft not available: first-engine pipeline (timeline + ed_render)')
        return remake_legacy(a)
    work = _remake_dir(a.project)
    kw = dict(sample_fps=a.sample_fps or 3.0)
    try:
        sig = inspect.signature(draft).parameters
    except (TypeError, ValueError):
        sig = {}
    if a.music and 'music' in sig:
        kw.update(music=a.music, music_in=a.music_in)
    footage = a.footage if (len(a.footage) > 1 and 'names' in sig) else a.footage[0]
    if len(a.footage) > 1 and footage == a.footage[0]:
        warn('[remake] this ed_remake takes one footage file: using', a.footage[0])
    edl = draft(a.ref, footage, work, parse_canvas(a.canvas), a.fps, **kw)
    if a.music and 'music' not in sig:
        edl['audio'] = dict(copy=False, music={'path': os.path.abspath(a.music), 'in': float(a.music_in or 0.0)},
                            loudness=dict(lufs=-14, tp=-1))
    path = save_json(edl, new_version_path(a.project))
    say('[remake]', path, f"{len(edl['segments'])} slots, {edl['n_frames']} frames, {time.time() - t:.0f} s")
    say(f"  review: {os.path.join(work, 'slots.jpg')} (reference | top-5 candidates per slot), "
        f"{os.path.join(work, 'survey.jpg')} (every shot of the footage), {os.path.join(work, 'candidates.json')}")
    say(f'  swap a shot: edit.py remake --project {a.project} --pick S05=12:34.5 [S07=<source>@1:02]')
    validate(path)
    out = after_edit(path, a, sheet=False)
    if out:
        remake_compare(a.ref, out, path)
    return path


def remake_compare(ref, video, edl_path):
    R = need('ed_remake', 'compare_sheet')
    if R is None or not ref or not os.path.exists(ref):
        return None
    v = version_of(edl_path)
    out = os.path.join(os.path.dirname(os.path.abspath(edl_path)), f'compare_v{v}.jpg' if v else 'compare.jpg')
    try:
        rows = R(ref, video, out, edl=edl_path)
    except Exception as e:  # review aid only
        warn(f'[remake] compare sheet failed ({type(e).__name__}: {e})')
        return None
    flagged = [f"#{r['n']}" for r in rows if r.get('flag')]
    say(f'[remake] {out}: reference | remake per slot' + (f'; look differs on {", ".join(flagged[:12])}' if flagged else ''))
    return out


def remake_pick(a):
    if not a.project:
        raise UserError('--pick needs --project DIR (the remake project)')
    src = a.edl or project_edl(a.project, a.version)
    edl = load_json(src)
    work = (edl.get('meta') or {}).get('remake_dir') or _remake_dir(a.project)
    if not os.path.exists(os.path.join(work, 'candidates.json')):
        raise UserError(f'no remake analysis in {work} (candidates.json): run edit.py remake --ref ... first')
    R = need('ed_remake')
    if R is None or not callable(getattr(R, 'repick', None)):
        raise UserError('ed_remake.repick is not available')
    try:
        new = R.repick(edl, work, R.parse_picks(a.pick), log_fn=lambda m: say('[pick]', m))
    except ValueError as e:
        raise UserError(str(e))
    path = save_json(new, os.path.join(os.path.dirname(os.path.abspath(src)), f'edl_v{latest_version(a.project) + 1}.json'))
    say('[remake]', path)
    out = after_edit(path, a, sheet=False)
    ref = (new.get('meta') or {}).get('reference')
    if out and ref:
        remake_compare(ref, out, path)
    return path


def remake_legacy(a):
    import ed_analyze as AN
    import ed_render as RD
    plan_remake = need('ed_plan', 'plan_remake') or need('legacy_plan', 'plan_remake')
    if plan_remake is None:
        raise UserError('no remake planner available')
    ref_dir, src_dir = os.path.join(a.project, 'ref'), os.path.join(a.project, 'src')
    rj, sj = os.path.join(ref_dir, 'reference.json'), os.path.join(src_dir, 'source.json')
    ref = load_json(rj) if os.path.exists(rj) else AN.analyze_reference(a.ref, ref_dir)
    src = load_json(sj) if os.path.exists(sj) else AN.analyze_source(a.footage[0], src_dir, fps=8.0)
    tl = plan_remake(ref, src, a.music, parse_canvas(a.canvas), a.fps or 30)
    path = save_json(tl, os.path.join(a.project, f'timeline_v{latest_version(a.project) + 1}.json'))
    say('[remake]', path, len(tl['clips']), 'clips')
    if not a.no_render:
        out = render_path(path)
        RD.render(tl, out, preview=True, labels=True)
        say('[render]', out)
        if not a.no_qa:
            qa(path, out)
    return path


# ----------------------------------------------------------------------------- background jobs
BG_COMMANDS = ('plan', 'variant', 'sequence', 'remake', 'storyboard')      # + voice transcribe (cmd_voice)
_RAW_ARGV = []          # this process's command line (after a --job prefix)
_JOB = None             # the job record this process updates when it runs as a background job


def _py_cmd():
    """How to call this edit.py again, exactly (python3 when that is this interpreter)."""
    w = shutil.which('python3')
    py = 'python3' if w and os.path.realpath(w) == os.path.realpath(sys.executable) else sys.executable
    return f'{py} -I {os.path.abspath(__file__)}'


def _job_write(path, **kw):
    rec = {}
    try:
        with open(path) as fh:
            rec = json.load(fh)
    except (OSError, ValueError):
        pass
    rec.update(kw)
    tmp = path + '.tmp'
    with open(tmp, 'w') as fh:
        json.dump(rec, fh, indent=1, default=str)
    os.replace(tmp, path)


def spawn_job(name, argv, folder, result=None):
    """Run `edit.py ARGV` detached in its own session (it survives the caller's shell, tool timeouts included), with
    its output in FOLDER/NAME_STAMP.log and its state in FOLDER/NAME_STAMP.job.json for `edit.py status FOLDER`."""
    folder = os.path.abspath(folder or '.')
    os.makedirs(folder, exist_ok=True)
    stem = os.path.join(folder, f"{name.replace(' ', '_')}_{time.strftime('%Y%m%d-%H%M%S')}")
    base, k = stem, 2
    while os.path.exists(base + '.job.json'):
        base, k = f'{stem}_{k}', k + 1
    log, job = base + '.log', base + '.job.json'
    rest = [x for x in argv if x != '--background']
    child = [sys.executable, '-I', '-u', os.path.abspath(__file__), '--job', job] + rest
    _job_write(job, kind='job', cmd=name, args=rest, cwd=os.getcwd(), stage='starting', started=time.time(), log=log,
               pid=None, **({'result': os.path.abspath(result)} if result else {}))
    with open(log, 'w') as fh:
        p = subprocess.Popen(child, stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                             start_new_session=True, cwd=os.getcwd())
    poll = f'{_py_cmd()} status {folder}'
    say(f'[{name}] started in the background (pid {p.pid}); log: {log}')
    say(f'  poll: {poll}')
    return dict(job=job, log=log, pid=p.pid, poll=poll)


def _bg(a, folder, name=None):
    """--background on a long command: detach it (see spawn_job) -> the job dict, else None (run here)."""
    if not getattr(a, 'background', False) or _JOB:
        return None
    return spawn_job(name or a.cmd, _RAW_ARGV, folder)


def _log_tail(log, n=1):
    try:
        with open(log, 'rb') as fh:
            fh.seek(0, 2)
            fh.seek(max(0, fh.tell() - 4000))
            lines = [ln.strip() for ln in fh.read().decode('utf-8', 'replace').splitlines() if ln.strip()]
    except OSError:
        return []
    return [ln for ln in lines if not ln.startswith('[ WARN:')][-n:]


# ----------------------------------------------------------------------------- render command / status
def cmd_render(a):
    edl_path = a.edl or project_edl(a.project, a.version)
    _exists(edl_path, 'timeline')
    labels = True if a.labels else (False if a.no_labels else None)
    if a.background and not a.stills:
        out = a.out or render_path(edl_path, a.final, a.frames)
        argv = [sys.executable, '-I', os.path.abspath(__file__), 'render', os.path.abspath(edl_path), '--out', out]
        for flag in ('final', 'fast', 'full', 'labels', 'no_labels', 'no_qa'):
            if getattr(a, flag):
                argv.append('--' + flag.replace('_', '-'))
        for opt in ('frames', 'interp', 'workers'):
            if getattr(a, opt) is not None:
                argv += ['--' + opt, str(getattr(a, opt))]
        log = out + '.log'
        with open(log, 'w') as fh:
            p = subprocess.Popen(argv, stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True,
                                 cwd=os.getcwd())
        say(f'[render] started in the background (pid {p.pid}) -> {out}')
        say(f'  progress: edit.py status {out}    log: {log}')
        return out
    out = render(edl_path, a.out, a.final, labels, a.frames, a.interp, a.workers, a.stills, a.at, a.fast,
                 draft=not (a.full or a.final))
    if not a.stills and not a.no_qa and not a.frames:
        qa(edl_path, out)
    return out


def cmd_frame(a):
    """One frame of a timeline at full output resolution, rendered like the final (no labels) -> PNG / JPG."""
    import cv2
    _exists(a.edl, 'timeline')
    edl = load_json(a.edl)
    if 'segments' not in edl:
        raise UserError('frame needs an EDL (engine/TIMELINE.md), not a legacy timeline')
    fps = float(edl['canvas']['fps'])
    t = str(a.at).strip()
    try:
        f = int(t[1:]) if t[:1] in ('f', 'F') else int(round(_secs(t) * fps))
    except ValueError:
        raise UserError(f'T must be a time (7.5 or 0:07.5) or a frame (f225), got {a.at!r}')
    if not 0 <= f < int(edl['n_frames']):
        raise UserError(f"frame {f} is outside the edit (0-{int(edl['n_frames']) - 1}, {edl['n_frames'] / fps:.2f} s)")
    for name, src in (edl.get('sources') or {}).items():
        if not os.path.exists(src.get('path') or ''):
            raise UserError(f"source '{name}' not found: {src.get('path')}")
    E_ = _E()
    own = edl.get('frame_interp')
    r = E_.Renderer(edl, preview=bool(a.preview), labels=False, frame_interp=own or 'flow')
    st = r.render(None, stills=[f])
    im = st[f]
    m_ = re.search(r'_v(\d+)\.json$', a.edl)
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.edl)), f"frame_v{m_.group(1) if m_ else 'x'}_f{f}.png")
    os.makedirs(os.path.dirname(os.path.abspath(out)) or '.', exist_ok=True)
    ok = cv2.imwrite(out, cv2.cvtColor(im, cv2.COLOR_RGB2BGR),
                     [cv2.IMWRITE_JPEG_QUALITY, 95] if out.lower().endswith(('.jpg', '.jpeg')) else [])
    if not ok:
        raise UserError(f'could not write {out} (use .png or .jpg)')
    seg = next((sg for sg in edl['segments'] if sg['f0'] <= f <= sg['f1']), None)
    say(f"[frame] {out}: frame {f} ({f / fps:.3f} s) {im.shape[1]}x{im.shape[0]}"
        + (f", clip {seg.get('id')} #{edl['segments'].index(seg) + 1}" if seg else ''))
    return out


def _pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError, TypeError):
        return False


def _job_rows(folder, as_json=False):
    """Background jobs of a folder (the last 3): state, time, last log line, result."""
    rows = []
    for f in sorted(glob.glob(os.path.join(folder, '*.job.json')), key=os.path.getmtime)[-3:]:
        try:
            with open(f) as fh:
                rec = json.load(fh)
        except (OSError, ValueError):
            continue
        st = rec.get('stage')
        if st in ('starting', 'running') and not _pid_alive(rec.get('pid')) and time.time() - float(rec.get('started') or 0) > 20:
            st = 'stopped'
        el = (rec.get('ended') or time.time()) - float(rec.get('started') or time.time())
        rec.update(job=f, state=st, elapsed_s=round(el, 1))
        rows.append(rec)
        if as_json:
            continue
        name = os.path.basename(f)[:-len('.job.json')]
        if st == 'done' and rec.get('result') and not os.path.exists(rec['result']):
            st = rec['state'] = 'failed'
            rec['error'] = rec.get('error') or f"finished without writing {rec['result']}"
        say(f"{name}: {st}, {fmt_s(el)}" + (f" -> {rec['result']}" if rec.get('result') else '')
            + (f" - {rec['error']}" if rec.get('error') else ''))
        if st in ('starting', 'running'):
            for ln in _log_tail(rec.get('log'), 1):
                say(f'  now: {ln[:200]}')
        elif st == 'done':
            for ln in [x for x in _log_tail(rec.get('log'), 40) if x.startswith(('[qa]', '[validate]'))][-2:]:
                say(f'  {ln[:200]}')
        elif st in ('failed', 'stopped'):
            say('  log tail: ' + '\n  '.join(_log_tail(rec.get('log'), 6)))
    return rows


def cmd_status(a):
    target = a.target or '.'
    files, jobs = [], []
    if os.path.isdir(target):
        jobs = _job_rows(target, a.json)
        files = sorted(glob.glob(os.path.join(target, '*.progress.json')), key=os.path.getmtime)
    elif target.endswith('.job.json'):
        jobs = _job_rows(os.path.dirname(os.path.abspath(target)) or '.', a.json)
    elif target.endswith('.progress.json'):
        files = [target]
    elif os.path.exists(progress_path(target)):
        files = [progress_path(target)]
    if not files and not jobs:
        raise UserError(f'no background job or render progress found for {target}')
    rows = list(jobs)
    for f in files[-5:]:
        try:
            with open(f) as fh:
                rec = json.load(fh)
        except (OSError, ValueError):
            continue
        out = f[:-len('.progress.json')]
        alive = _pid_alive(rec.get('pid'))
        st = rec.get('stage')
        if st not in ('done', 'failed') and not alive:
            st = 'stopped'
        rec.update(out=out, state=st)
        rows.append(rec)
        if not a.json:
            pct = 100 * rec.get('done', 0) / max(1, rec.get('total', 1))
            say(f"{os.path.basename(out)}: {st} {rec.get('done')}/{rec.get('total')} frames ({pct:.0f}%), "
                f"{rec.get('fps')} fps, elapsed {fmt_s(rec.get('elapsed_s'))}"
                + (f", ETA {fmt_s(rec.get('eta_s'))}" if st not in ('done', 'failed', 'stopped') else '')
                + (f" - {rec.get('error')}" if rec.get('error') else ''))
            log = out + '.log'
            if st in ('failed', 'stopped') and os.path.exists(log):
                with open(log, errors='replace') as fh:
                    tail = fh.read()[-800:]
                say('  log tail: ' + tail.strip().replace('\n', '\n  '))
    if a.json:
        say(json.dumps(rows, indent=1))
    return rows


# ----------------------------------------------------------------------------- point edits
LOW_LEVEL = ('set', 'append', 'delete')


def _walk(obj, path, create=False):
    """Resolve 'segments.C03.crop' (list items by index or by their 'id') -> (parent, key)."""
    toks = [t for t in re.split(r'\.(?![^\[]*\])', path) if t]
    cur = obj
    for i, t in enumerate(toks):
        last = i == len(toks) - 1
        if isinstance(cur, list):
            if re.fullmatch(r'-?\d+', t):
                key = int(t)
            else:
                key = next((j for j, it in enumerate(cur) if isinstance(it, dict) and str(it.get('id')) == t), None)
                if key is None:
                    raise KeyError(f'{path}: no item with id {t!r}')
        elif isinstance(cur, dict):
            key = t
            if not last and key not in cur:
                if not create:
                    raise KeyError(f'{path}: {t!r} not found')
                cur[key] = {}
        else:
            raise KeyError(f'{path}: cannot descend into {type(cur).__name__} at {t!r}')
        if last:
            return cur, key
        cur = cur[key]
    raise KeyError(f'empty path {path!r}')


def apply_low_level(edl, cmd):
    """{"op": "set" | "append" | "delete", "path": "segments.C03.fx", "value": ...} -> new EDL (deep copy)."""
    e = copy.deepcopy(edl)
    op = cmd['op']
    parent, key = _walk(e, cmd['path'], create=op != 'delete')
    if op == 'set':
        if isinstance(parent, list) and key == len(parent):
            parent.append(cmd['value'])
        else:
            parent[key] = cmd['value']
    elif op == 'append':
        if isinstance(parent, dict) and key not in parent:
            parent[key] = []
        tgt = parent[key]
        if not isinstance(tgt, list):
            raise ValueError(f"{cmd['path']} is not a list")
        tgt.append(cmd['value'])
    elif op == 'delete':
        del parent[key]
    meta = e.setdefault('meta', {}) if 'meta' in e else None
    if meta is not None:
        meta['version'] = int(meta.get('version', 1)) + 1
        meta.setdefault('history', []).append(dict(cmd=cmd, at=time.strftime('%Y-%m-%dT%H:%M:%S')))
    return e


def parse_cmd(s):
    s = s.strip()
    if s.startswith('@'):
        return load_json(s[1:])
    if s.startswith('{') or s.startswith('['):
        try:
            return json.loads(s)
        except json.JSONDecodeError as e:
            raise UserError(f'command is not valid JSON ({e})')
    if os.path.exists(s):
        return load_json(s)
    raise UserError('command must be inline JSON, @file.json or a JSON file path (Claude turns words into the dict)')


SHIFT_OPS = ('insert', 'delete_clip', 'delete_range')


def _secs(v):
    """7 | 7.5 | '7.5' | '0:07.5' -> seconds."""
    if isinstance(v, (int, float)):
        return float(v)
    t = 0.0
    for part in str(v).strip().split(':'):
        t = t * 60 + float(part)
    return t


def _frame_arg(edl, cmd, t_key, f_key):
    if cmd.get(f_key) is not None:
        return int(cmd[f_key])
    if cmd.get(t_key) is not None:
        return int(round(_secs(cmd[t_key]) * float(edl['canvas']['fps'])))
    raise ValueError(f'{cmd.get("op")}: give "{t_key}" (time) or "{f_key}" (frame)')


def _clip_index(edl, clip):
    segs = edl['segments']
    c = str(clip).strip()
    if c.lstrip('#').isdigit() and not any(str(s.get('id')) == c for s in segs):
        j = int(c.lstrip('#')) - 1
        if 0 <= j < len(segs):
            return j
        raise ValueError(f'clip {clip}: the edit has {len(segs)} clips')
    for j, s in enumerate(segs):
        if str(s.get('id')) == c:
            return j
    raise ValueError(f'clip {clip!r} not found')


def _split_motion(E_, old, head, tail, k, n_old, f, fps):
    """A clip cut in two at segment frame k: the crop animation continues across the cut (path keys and 'to' end
    states split at the crop state of frame k), segment-relative fx frames go to their half (rebased in the tail),
    absolute-time fx to the half that shows them."""
    import copy as _c
    cr = old.get('crop') or {}
    if cr.get('path'):
        pth = [list(p) for p in cr['path']]
        mid = E_.crop_state(old, k, n_old)
        pk = [k, mid['cx'], mid['cy'], mid['z']]
        head['crop'] = dict(cr, path=[p for p in pth if p[0] < k] + [[k - 1] + pk[1:]])
        tail['crop'] = dict(cr, path=[[0] + pk[1:]] + [[p[0] - k] + p[1:] for p in pth if p[0] > k])
    elif isinstance(cr.get('to'), dict) and n_old > 1:
        mid = E_.crop_state(old, k, n_old)
        tail['crop'] = dict(_c.deepcopy(cr), **{x: mid[x] for x in ('cx', 'cy', 'z', 'rot') if x in mid})
        head['crop'] = dict(_c.deepcopy(cr), to={x: round(mid[x], 4) for x in cr['to'] if x in mid})
    t_cut = f / fps
    for key in ('fx', 'post_text_fx'):
        if not isinstance(old.get(key), list):
            continue
        hf, tf = [], []
        for fx in head.get(key) or []:
            if isinstance(fx.get('frames'), list) and all(isinstance(v, int) for v in fx['frames']):
                a_ = [v for v in fx['frames'] if v < k]
                b_ = [v - k for v in fx['frames'] if v >= k]
                if a_:
                    hf.append(dict(fx, frames=a_))
                if b_:
                    tf.append(dict(fx, frames=b_))
            elif isinstance(fx.get('times'), list):
                a_ = [v for v in fx['times'] if v < t_cut]
                b_ = [v for v in fx['times'] if v >= t_cut]
                if a_:
                    hf.append(dict(fx, times=a_))
                if b_:
                    tf.append(dict(fx, times=b_))
            elif fx.get('at') is not None:
                (hf if float(fx['at']) < t_cut else tf).append(fx)
            else:
                hf.append(fx)
                tf.append(_c.deepcopy(fx))
        head[key], tail[key] = hf, tf


def _split_at(E_, edl, f):
    """Cut the clip that plays frame f in two at f (in place): the tail keeps its source timing ('t' / 'times' /
    speed_curve), crop animation and fx continue across the cut. No-op at a cut or outside the edit -> tail or None."""
    import numpy as np
    fps = float(edl['canvas']['fps'])
    host = next((s for s in edl['segments'] if s['f0'] < f <= s['f1']), None)
    if host is None:
        return None
    old = copy.deepcopy(host)
    n_old = old['f1'] - old['f0'] + 1
    k = f - old['f0']
    tail = copy.deepcopy(host)
    host['f1'] = f - 1
    ids = {str(s.get('id')) for s in edl['segments']}
    m_ = re.match(r'^(.*\d)[b-z]$', str(old.get('id')))           # C05 -> C05b, C05b -> C05c ...
    base = m_.group(1) if m_ else str(old.get('id'))
    tid = next(c for c in [base + ch for ch in 'bcdefghijklmnopqrstuvwxyz'] + [f'{base}_{i}' for i in range(2, 999)]
               if c not in ids)
    tail['f0'], tail['id'] = f, tid
    tail.pop('transition_in', None)
    tail['t'] = round(E_.seg_time(old, k, fps), 4)
    if isinstance(old.get('times'), list):
        host['times'], tail['times'] = old['times'][:k], old['times'][k:n_old]
    if old.get('speed_curve'):
        cv = [[float(p[0]) - k, float(p[1])] for p in old['speed_curve']]
        r0 = float(np.interp(0.0, [p[0] for p in cv], [p[1] for p in cv])) if len(cv) > 1 else cv[0][1]
        tail['speed_curve'] = [[0.0, r0]] + [p for p in cv if p[0] > 0]
        head = [p for p in old['speed_curve'] if float(p[0]) < k]
        r1 = float(np.interp(k - 1.0, [float(p[0]) for p in old['speed_curve']], [float(p[1]) for p in old['speed_curve']]))
        host['speed_curve'] = head + ([[float(k - 1), r1]] if not head or float(head[-1][0]) < k - 1 else [])
    _split_motion(E_, old, host, tail, k, n_old, f, fps)
    edl['segments'].append(tail)
    edl['segments'].sort(key=lambda s: s['f0'])
    return tail


def apply_shift(edl, cmd):
    """Ripple edits through ed_edl.shift (everything after the point moves: fx times, ops, texts, layers, voice,
    SFX, qa marks; the music and its beat grid stay):
      {"op": "insert", "at": "0:07" | "f": 210, "frames": 15 | "dur": 0.5,
       "segment": {"src": "a" | "path": "/clip.mp4", "t": 12.0, ...}}
          without "segment" the clip at that point plays on longer; with it, a new clip fills the inserted frames
          (a clip that was cut in two keeps its source timing on both sides; a new clip gets the look of the clip
          it joins unless "grade" is given)
      {"op": "delete_clip", "clip": "C05" | "#5"}                    the clip and its frames are removed
      {"op": "delete_range", "from": "0:07" | "f0": 210, "to": "0:08" | "f1": 239}   frames from..to (inclusive);
          clips cut by the range keep their source timing and motion on both sides (a jump cut)"""
    E_ = _E()
    shift = getattr(E_, 'shift', None)
    if not callable(shift):
        raise ValueError('ripple edits need ed_edl.shift')
    op = cmd['op']
    fps = float(edl['canvas']['fps'])
    if op == 'insert':
        f = _frame_arg(edl, cmd, 'at', 'f')
        n = int(cmd['frames']) if cmd.get('frames') is not None else int(round(_secs(cmd.get('dur', 0)) * fps))
        if n <= 0 or not 0 <= f <= edl['n_frames']:
            raise ValueError('insert: needs "frames" or "dur" > 0 and a point inside the edit')
        seg = cmd.get('segment')
        if not seg:
            new = shift(edl, f, n)
        else:
            work = copy.deepcopy(edl)
            _split_at(E_, work, f)
            joins = next((s for s in reversed(work['segments']) if s['f1'] < f), None) or \
                next((s for s in work['segments'] if s['f0'] <= f <= s['f1']), None)
            look = copy.deepcopy(joins.get('grade')) if joins and joins.get('grade') else None
            new = shift(work, f, n)
            grown = next((s for s in new['segments'] if s['f0'] == f), None)
            if grown is not None:                                 # the clip after the point moves behind the insert
                grown['f0'] = f + n
                if isinstance(grown.get('times'), list):
                    grown['times'] = grown['times'][:grown['f1'] - grown['f0'] + 1]
            item = {k: v for k, v in seg.items() if k not in ('f0', 'f1', 'path')}
            srcs = new.setdefault('sources', {})
            if seg.get('path'):                                   # a new file: becomes a source of its own
                pth = os.path.abspath(os.path.expanduser(str(seg['path'])))
                if not os.path.exists(pth):
                    raise ValueError(f'insert: file not found: {pth}')
                name = next((k_ for k_, v_ in srcs.items() if os.path.abspath(v_.get('path') or '') == pth), None)
                if name is None:
                    base = re.sub(r'[^a-z0-9]+', '_', os.path.splitext(os.path.basename(pth))[0].lower()).strip('_')[:24] or 'clip'
                    name = base if base not in srcs else next(f'{base}_{i}' for i in range(2, 999) if f'{base}_{i}' not in srcs)
                    srcs[name] = dict(path=pth)
                item['src'] = name
            if item.get('src') not in srcs:
                raise ValueError(f"insert: unknown source {item.get('src')!r} (sources: {', '.join(srcs) or 'none'}; "
                                 f'or give "path" to a file)')
            item.setdefault('t', 0.0)
            item.setdefault('crop', dict(cx=0.5, cy=0.5, z=1.0))
            if look is not None and 'grade' not in item:
                item['grade'] = look                              # the look of the clip it joins
            ids = {str(s.get('id')) for s in new['segments']}
            item['id'] = str(seg.get('id') or next(c for c in [f'I{f:04d}'] + [f'I{f:04d}_{i}' for i in range(2, 999)]
                                                    if c not in ids))
            item.update(f0=f, f1=f + n - 1)
            new['segments'].append(item)
            new['segments'].sort(key=lambda s: s['f0'])
    elif op == 'delete_clip':
        sg = edl['segments'][_clip_index(edl, cmd.get('clip'))]
        new = shift(edl, sg['f0'], -(sg['f1'] - sg['f0'] + 1))
    else:
        a = _frame_arg(edl, cmd, 'from', 'f0')
        b = _frame_arg(edl, cmd, 'to', 'f1')
        b = min(b, edl['n_frames'] - 1)
        if b < a or a < 0:
            raise ValueError('delete_range: "to" is before "from" (or outside the edit)')
        work = copy.deepcopy(edl)
        _split_at(E_, work, a)                                    # the range removes whole pieces: what stays
        _split_at(E_, work, b + 1)                                # keeps its timing and motion
        new = shift(work, a, -(b - a + 1))
    meta = new.setdefault('meta', {})
    meta['version'] = int(meta.get('version', 1)) + 1
    meta.setdefault('history', []).append(dict(cmd=cmd, at=time.strftime('%Y-%m-%dT%H:%M:%S')))
    return new


def apply_cmd(edl, cmd):
    """One point edit -> new EDL. Low-level ops (set/append/delete) and ripple edits (insert / delete_clip /
    delete_range, via ed_edl.shift) are applied here; everything else goes to ed_plan.apply_command (genre-aware:
    refuses moves the genre card forbids, with the reason)."""
    if isinstance(cmd, list):                      # several ops = one edit: the version goes up once
        v0 = int((edl.get('meta') or {}).get('version') or 1)
        for c in cmd:
            edl = apply_cmd(edl, c)
        edl.setdefault('meta', {})['version'] = v0 + 1
        return edl
    if cmd.get('op') in SHIFT_OPS:
        return apply_shift(edl, cmd)
    if cmd.get('op') in LOW_LEVEL and 'path' in cmd:
        return apply_low_level(edl, cmd)
    fn = need('ed_plan', 'apply_command')
    if fn is None:
        raise UserError(f"op {cmd.get('op')!r} needs ed_plan.apply_command; available here: "
                        f"{', '.join(LOW_LEVEL + SHIFT_OPS)}")
    return fn(edl, cmd)


def cmd_cmd(a):
    edl = load_json(a.edl)
    cmd = parse_cmd(a.command)
    try:
        new = apply_cmd(edl, cmd)
    except (ValueError, KeyError) as e:
        raise UserError(f'refused: {e}')
    had = set(check_edl(edl)[0])
    broke = [x for x in check_edl(new)[0] if x not in had]
    if broke and not any(isinstance(c, dict) and c.get('force') for c in (cmd if isinstance(cmd, list) else [cmd])):
        raise UserError('refused: the edit would break the timeline: ' + '; '.join(broke[:4])
                        + ' ("force": true writes it anyway)')
    out = a.out or next_edl_path(a.edl)
    save_json(new, out)
    hist = ((new.get('meta') or {}).get('history') or [None])[-1]
    say('[cmd]', out, json.dumps(hist, ensure_ascii=False)[:600] if hist else '')
    if a.render:
        after_edit(out, a, sheet=False)
    return out


# ----------------------------------------------------------------------------- plan sheet
def _parts(edl):
    """meta.parts as [(id, type, f0, f1)]: the planner's {name: {"f": [f0, f1]}} or ed_sequence's [{id, type, f0, f1}]."""
    m = (edl.get('meta') or {}).get('parts')
    fps = edl['canvas']['fps']
    out = []
    if isinstance(m, dict):
        for k, v in m.items():
            f = v.get('f') or ([int(round(v['t'][0] * fps)), int(round(v['t'][1] * fps)) - 1] if v.get('t') else None)
            if f:
                out.append((str(k), str(v.get('type', k)), int(f[0]), int(f[1])))
    elif isinstance(m, list):
        for v in m:
            if isinstance(v, dict) and v.get('f0') is not None:
                out.append((str(v.get('id', v.get('type', '?'))), str(v.get('type', '')), int(v['f0']), int(v.get('f1', v['f0']))))
    return out


def _seg_moves(edl, seg, slot_meta):
    """Short move list of a segment: transition, fx, speed, camera move, ops and SFX inside it."""
    fps = edl['canvas']['fps']
    f0, f1 = int(seg['f0']), int(seg['f1'])
    mv = []
    tr = seg.get('transition_in') or {}
    if tr.get('kind'):
        mv.append(f"in:{tr['kind']}")
    ids = [m.get('id') for m in (slot_meta or {}).get('moves', []) if isinstance(m, dict) and m.get('id')]
    for f in seg.get('fx') or []:
        ids.append(f.get('move') or f.get('type'))
    curve = seg.get('speed_curve')
    if curve:
        rates = [float(p[1]) for p in curve]
        mv.append(f'ramp {max(rates):.2g}-{min(rates):.2g}x')
    elif seg.get('times'):
        mv.append('time remap')
    elif abs(float(seg.get('speed', 1.0)) - 1.0) > 1e-3:
        mv.append(f"speed {float(seg['speed']):.2g}x")
    crop = seg.get('crop') or {}
    if crop.get('path'):
        mv.append('tracked crop')
    elif isinstance(crop.get('to'), dict) and 'z' in crop['to']:
        mv.append(f"push z{float(crop.get('z', 1)):.2f}-{float(crop['to']['z']):.2f}")
    E_ = _E()
    for op in edl.get('ops') or []:
        try:
            fr = E_.frange(op.get('f'))
        except (TypeError, ValueError):
            fr = []
        if any(f0 <= x <= f1 for x in fr):
            ids.append(op.get('move') or op.get('op'))
    au = edl.get('audio') or {}
    sfx = sorted({s.get('kind') or 'file' for s in au.get('sfx') or [] if f0 <= int(float(s.get('at', -1)) * fps + 0.4) <= f1})
    seen = []
    for x in ids:
        x = str(x)
        x = x[3:] if x.startswith('fx.') else x
        if x and x not in seen:
            seen.append(x)
    mv += seen
    if sfx:
        mv.append('sfx:' + '+'.join(sfx))
    return mv


def _sheet_font(size):
    from PIL import ImageFont
    for p in (os.path.join(HERE, 'assets', 'fonts', 'inter_Inter-VF.ttf'),
              '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'):
        if os.path.exists(p):
            try:
                f = ImageFont.truetype(p, size)
                try:
                    names = [a['name'].decode('latin-1') if isinstance(a['name'], bytes) else str(a['name'])
                             for a in f.get_variation_axes()]
                    f.set_variation_by_axes([700 if n == 'Weight' else 24 for n in names])
                except Exception:  # static font: nothing to set
                    pass
                return f
            except OSError:
                continue
    return ImageFont.load_default()


def _grab(path, t, width):
    """One frame of `path` at source time t (accurate seek), scaled to `width` px wide -> RGB uint8 or None."""
    import numpy as np
    info = _E().V.probe(path)
    W, H = info['w'], info['h']
    w = min(width, W) // 2 * 2
    h = max(2, int(round(H * w / W / 2)) * 2)
    still = os.path.splitext(path)[1].lower() in ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff')
    seek = [] if still else ['-ss', f'{max(0.0, t):.4f}']             # a still image has no time to seek to
    p = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin'] + seek + ['-i', path, '-frames:v', '1',
                        '-vf', f'scale={w}:{h}:flags=area', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
    if len(p.stdout) < w * h * 3:
        return None, (W, H)
    return np.frombuffer(p.stdout[:w * h * 3], np.uint8).reshape(h, w, 3), (W, H)


def _wrap(draw, text, font, width, max_lines=2):
    """Greedy word wrap by rendered width -> list of lines (the last one cut with '...' when it does not fit)."""
    words, lines, cur = text.split(), [], ''
    for w in words:
        cand = (cur + ' ' + w).strip()
        if draw.textlength(cand, font=font) <= width or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and draw.textlength(last + ' ...', font=font) > width:
            last = last[:-1]
        lines[-1] = last + ' ...'
    return lines


def plan_sheet(edl_or_path, out, cols=6, width=270, at='mid', log=warn):
    """The plan as an image: one tile per segment (#N = position in `segments`) with the frame that will be used
    (crop + grade of that frame; camera fx and effects are listed, not drawn), output time, part, source moment and
    moves (moves every segment has are listed once in the header); frames no segment covers and segments without a
    usable source are NO SHOT tiles. Writes `out` and returns the tile list (dicts, also printed by --json)."""
    import numpy as np
    import cv2
    from PIL import Image, ImageDraw
    E_ = _E()
    edl = load_json(edl_or_path) if isinstance(edl_or_path, str) else edl_or_path
    if not edl.get('segments'):
        raise UserError('the timeline has no segments')
    fps = float(edl['canvas']['fps'])
    CW, CH = int(edl['canvas']['w']), int(edl['canvas']['h'])
    tw = int(width)
    th = int(round(tw * CH / CW))
    parts = _parts(edl)
    slots = {str(s.get('id')): s for s in (edl.get('meta') or {}).get('slots') or [] if isinstance(s, dict)}
    gap_meta = {str(g.get('id')): g for g in (edl.get('meta') or {}).get('gaps') or []
                if isinstance(g, dict) and not g.get('filled')}          # storyboard / planner gaps still to fill
    srcs = edl.get('sources') or {}
    t_start = time.time()
    segs = list(enumerate(edl['segments'], 1))
    covered = np.zeros(int(edl['n_frames']), bool)
    for _, s in segs:
        covered[max(0, int(s['f0'])):int(s['f1']) + 1] = True
    items = [('seg', s['f0'], n, s) for n, s in segs]
    f = 0
    while f < len(covered):                                   # frames without a segment
        if not covered[f]:
            g = f
            while g + 1 < len(covered) and not covered[g + 1]:
                g += 1
            items.append(('hole', f, None, dict(f0=f, f1=g)))
            f = g + 1
        else:
            f += 1
    items.sort(key=lambda x: (x[1], 0 if x[0] == 'seg' else 1))
    rows, imgs = [], []
    for kind, _, n, s in items:                               # pass 1: frames and facts
        f0, f1 = int(s['f0']), int(s['f1'])
        part = next((p[0] for p in parts if p[2] <= f0 <= p[3]), s.get('part') or '')
        row = dict(n=n, id=s.get('id'), f0=f0, f1=f1, t0=round(f0 / fps, 3), t1=round((f1 + 1) / fps, 3), part=part)
        img, why = None, None
        if kind == 'hole':
            why = 'no segment covers these frames'
        else:
            src = srcs.get(s.get('src')) if s.get('src') else None
            gm = gap_meta.get(str(s.get('id')))
            if gm is not None:
                b = gm.get('brief') or {}
                why = (f"{b.get('shot_size')}: {b.get('prompt') or b.get('subject') or ''}" if b.get('shot_size')
                       else (gm.get('reason') or 'shot to generate'))
            elif s.get('gap') or s.get('src') in (None, '', 'gap'):
                why = s.get('need') or (s.get('gap') if isinstance(s.get('gap'), str) else None) or s.get('note') or 'gap'
            elif src is None:
                why = f"unknown source '{s.get('src')}'"
            elif not os.path.exists(src.get('path') or ''):
                why = f"missing file of '{s.get('src')}'"
            else:
                nf = f1 - f0 + 1
                k = 0 if at == 'first' else (nf - 1) // 2
                try:
                    t = E_.seg_time(s, k, fps)
                except (KeyError, TypeError, ValueError):
                    t = float(s.get('t', 0.0))
                row.update(src=s.get('src'), src_t=round(t, 3))
                try:
                    fr, (W, H) = _grab(src['path'], t, 1280)
                    if fr is not None:
                        sx = fr.shape[1] / W
                        bx = src.get('box') or [0, 0, W, H]
                        x0, y0 = int(round(bx[0] * sx)), int(round(bx[1] * sx))
                        x1, y1 = int(round(bx[2] * sx)), int(round(bx[3] * sx))
                        fr = np.ascontiguousarray(fr[y0:y1, x0:x1])
                        c = E_.crop_state(s, k, nf)
                        box_wh = SimpleNamespace(w=fr.shape[1], h=fr.shape[0])     # window() needs the box size
                        cx, cy, ww, hw = E_.window(box_wh, c, tw, th)
                        img = E_.warp(fr, cx, cy, ww, hw, tw, th, c.get('rot', 0.0), interp=cv2.INTER_AREA,
                                      border=s.get('border', 'reflect'))
                        if s.get('grade'):
                            try:
                                x = img.astype(np.float32) / 255.0
                                img = (np.clip(E_.apply_grade(x, s['grade'], E_.grade_stats([x])), 0, 1) * 255 + 0.5).astype(np.uint8)
                            except Exception:  # grade preview is best effort
                                pass
                    else:
                        why = 'source frame could not be decoded'
                except Exception as e:  # one bad tile must not kill the sheet
                    why = f'{type(e).__name__}: {e}'[:60]
            row['moves'] = [m for m in _seg_moves(edl, s, slots.get(str(s.get('id')))) if m != 'grade']
        if img is None:
            row['gap'] = why
        rows.append(row)
        imgs.append(img)
    seg_rows = [r for r in rows if r.get('n')]
    common = [m for m in (seg_rows[0].get('moves') or []) if len(seg_rows) > 2 and all(m in (r.get('moves') or []) for r in seg_rows)]
    big = _sheet_font(max(24, tw // 6))
    mid = _sheet_font(max(14, tw // 18))
    small = _sheet_font(max(13, tw // 20))
    msz, ssz = getattr(mid, 'size', 14), getattr(small, 'size', 13)
    cap = msz + 2 * (ssz + 3) + ssz + 14
    tiles = []
    for row, img in zip(rows, imgs):                           # pass 2: draw
        tile = Image.new('RGB', (tw, th + cap), (18, 18, 18))
        if img is not None:
            tile.paste(Image.fromarray(img), (0, 0))
        else:
            d0 = ImageDraw.Draw(tile)
            for x in range(-th, tw, 18):
                d0.line([(x, th), (x + th, 0)], fill=(48, 30, 30), width=6)
        d = ImageDraw.Draw(tile)
        d.text((8, 4), f"#{row['n']}" if row['n'] else 'GAP', font=big, fill=(255, 235, 60), stroke_width=3,
               stroke_fill=(0, 0, 0))
        if img is None:
            d.text((8, th // 2 - 14), 'NO SHOT', font=big, fill=(255, 90, 90), stroke_width=3, stroke_fill=(0, 0, 0))
            for i, ln in enumerate(_wrap(d, str(row['gap']), small, tw - 16, 3)):
                d.text((8, th // 2 + 26 + i * (ssz + 3)), ln, font=small, fill=(255, 210, 210), stroke_width=2,
                       stroke_fill=(0, 0, 0))
        y = th + 4
        tc = f"{tc_str(row['t0'])}-{tc_str(row['t1'])} {row['t1'] - row['t0']:.2f}s" + (f"  {row['id']}" if row.get('id') else '')
        d.text((6, y), tc, font=mid, fill=(240, 240, 240))
        y += msz + 3
        sname = str(row.get('src') or '')
        sname = sname if len(sname) <= 16 else sname[:14] + '..'
        line2 = ' '.join(x for x in (row.get('part') or '', f"{sname}@{tc_str(row['src_t'])}" if row.get('src_t') is not None
                                     else '') if x)
        if line2:
            d.text((6, y), _wrap(d, line2, small, tw - 10, 1)[0], font=small, fill=(150, 200, 255))
        y += ssz + 3
        mv = [m for m in (row.get('moves') or []) if m not in common]
        for ln in _wrap(d, ' '.join(mv), small, tw - 10, 2):
            d.text((6, y), ln, font=small, fill=(255, 190, 110))
            y += ssz + 3
        tiles.append(np.asarray(tile))
    gap, head_h = 6, 2 * msz + 22
    ncol = max(1, min(int(cols), len(tiles)))
    nrow = (len(tiles) + ncol - 1) // ncol
    sheet = np.full((nrow * (th + cap + gap) + head_h, ncol * (tw + gap) + gap, 3), 8, np.uint8)
    for i, t_ in enumerate(tiles):
        r_, c_ = divmod(i, ncol)
        y, x = head_h + r_ * (th + cap + gap), gap + c_ * (tw + gap)
        sheet[y:y + th + cap, x:x + tw] = t_
    head = Image.fromarray(sheet)
    meta = edl.get('meta') or {}
    n_gap = sum(1 for r in rows if r.get('gap'))
    title = (f"{meta.get('genre') or meta.get('scenario') or 'edit'}  {CW}x{CH} {fps:g} fps  {edl['n_frames']} frames "
             f"({edl['n_frames'] / fps:.1f} s)  {len(seg_rows)} segments" + (f'  {n_gap} without a shot' if n_gap else '')
             + ('  |  parts: ' + ', '.join(f'{p[0]} {p[2] / fps:.1f}-{(p[3] + 1) / fps:.1f}s' for p in parts) if parts else ''))
    dh = ImageDraw.Draw(head)
    dh.text((gap, 6), title, font=mid, fill=(235, 235, 235))
    if common:
        dh.text((gap, 10 + msz), 'on every segment: ' + ' '.join(common), font=small, fill=(255, 190, 110))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    head.save(out, quality=88)
    for r in rows:
        if r.get('moves') is not None:
            r['moves_common'] = common
    log(f'[plan-sheet] {out}: {len(rows)} tiles, {n_gap} without a shot ({time.time() - t_start:.1f} s)')
    return rows


def tc_str(t):
    m, s = divmod(max(0.0, float(t)), 60)
    return f'{int(m)}:{s:05.2f}'


def cmd_plan_sheet(a):
    edl_path = a.edl or project_edl(a.project, a.version)
    out = a.out or sheet_path(edl_path)
    rows = plan_sheet(edl_path, out, cols=a.cols, width=a.width, at=a.at)
    if a.json:
        say(json.dumps(dict(out=out, tiles=rows), ensure_ascii=False, indent=1))
    else:
        say('[plan-sheet]', out)
        for r in rows:
            say(f"  #{r['n'] or '-'} {tc_str(r['t0'])}-{tc_str(r['t1'])} {r.get('part') or ''} "
                + (f"NO SHOT ({r['gap']})" if r.get('gap') else f"{r.get('src')}@{tc_str(r.get('src_t') or 0)}")
                + (f" | {' '.join(r.get('moves') or [])}" if r.get('moves') else ''))
    return out


# ----------------------------------------------------------------------------- pack / unpack
PACK_FORMAT = 'edit-studio-pack'
PACK_MANIFEST = 'edit_studio_pack.json'
MEDIA_EXT = {'.mp4', '.mov', '.mkv', '.webm', '.m4v', '.avi', '.mts', '.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg',
             '.opus', '.aif', '.aiff', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.tif', '.tiff', '.ttf', '.otf', '.svg',
             '.lut', '.cube'}
KEEP_EXT = {'.json', '.md', '.txt', '.srt', '.ass', '.vtt', '.py', '.yaml', '.yml', '.csv'}
SKIP_DIRS = {'.ed_cache', '__pycache__', '.git', 'media'}
SKIP_SUFFIX = ('.render.json', '.boxes.json', '.progress.json', '.job.json', '.tmp')


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for b in iter(lambda: fh.read(chunk), b''):
            h.update(b)
    return h.hexdigest()


def _media_info(path):
    info = dict(size=os.path.getsize(path))
    if os.path.splitext(path)[1].lower() in ('.ttf', '.otf', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.cube', '.lut',
                                             '.tif', '.tiff'):
        return info
    try:
        p = _E().V.probe(path)
        info.update(duration=round(float(p.get('duration') or 0), 3), w=p.get('w'), h=p.get('h'), fps=p.get('fps'))
    except Exception:  # not a media file ffprobe understands
        pass
    return info


def _json_strings(obj, fn, path=''):
    """Apply fn(value, path) to every string in a JSON tree (in place for dicts/lists); returns the new tree."""
    if isinstance(obj, dict):
        return {k: _json_strings(v, fn, f'{path}.{k}' if path else str(k)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_strings(v, fn, f'{path}.{i}') for i, v in enumerate(obj)]
    if isinstance(obj, str):
        return fn(obj, path)
    return obj


def _ref_file(s, base):
    """A JSON string that names an existing media file (absolute, or relative to base) -> its absolute path."""
    if len(s) > 1024 or '\n' in s or not os.path.splitext(s)[1].lower() in MEDIA_EXT:
        return None
    p = s if os.path.isabs(s) else os.path.join(base, s)
    return os.path.abspath(p) if os.path.isfile(p) else None


def pack(project, out=None, media='auto', max_mb=256.0, log=say):
    """Project folder -> zip: timelines and project data (json/md/srt/py ...) + edit_studio_pack.json; every file the
    JSON files reference (sources, music, voice, user SFX samples, fonts, images) is listed with sha256, size,
    duration and stored under media/<name> when media='all' or ('auto' and <= max_mb); a remake's reference video
    (keys named 'reference') is listed but never stored. Inside the zip, references point to media/<name>
    (relative); renders, sheets (they can show reference frames), QA folders and caches are left out."""
    project = os.path.abspath(project)
    if not os.path.isdir(project):
        raise UserError(f'project folder not found: {project}')
    name = os.path.basename(project.rstrip(os.sep))
    out = os.path.abspath(out or os.path.join(os.path.dirname(project), f'{name}.edit.zip'))
    files = []
    for root, dirs, fnames in os.walk(project):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith('qa_') and not d.startswith('.'))
        for fn in sorted(fnames):
            p = os.path.join(root, fn)
            if fn.endswith(SKIP_SUFFIX) or os.path.splitext(fn)[1].lower() not in KEEP_EXT or os.path.abspath(p) == out:
                continue
            files.append(p)
    media_map = {}                                   # abs path -> manifest entry
    refs = set()                                     # someone else's video (meta.reference): never stored inside
    texts = {}
    render_re = re.compile(r'^(preview|final)_v\d+.*\.(mp4|mov|mkv|wav)$')
    for p in files:
        if not p.endswith('.json'):
            continue
        try:
            with open(p, encoding='utf-8') as fh:
                obj = json.load(fh)
        except (OSError, ValueError):
            continue
        base = os.path.dirname(p)
        texts[p] = obj
        meta = obj.get('meta') if isinstance(obj, dict) else None
        if not (isinstance(obj, dict) and (any(k in obj for k in ('segments', 'sources', 'parts', 'clips')) or
                                           (isinstance(meta, dict) and ('footage' in meta or 'reference' in meta)))):
            continue                                 # only timelines, specs and analysis files name sources

        def collect(s, _path, base=base):
            f = _ref_file(s, base)
            if f and f.startswith(project + os.sep) and render_re.match(os.path.basename(f)):
                return s                             # a render of this project is never a source
            if f and f not in media_map:
                media_map[f] = None
            if f and _path.split('.')[-1] == 'reference':
                refs.add(f)
            return s
        _json_strings(obj, collect)
    used_names = set()
    entries = []
    for f in sorted(media_map):
        real = os.path.realpath(f)
        nm = os.path.basename(f)
        stem, ext = os.path.splitext(nm)
        k = 2
        while nm.lower() in used_names:
            nm, k = f'{stem}_{k}{ext}', k + 1
        used_names.add(nm.lower())
        info = _media_info(real)
        log(f'[pack] hashing {os.path.basename(f)} ({info["size"] / 1e6:.1f} MB)')
        e = dict(name=f'media/{nm}', orig=f, real=real if real != f else None, sha256=sha256_file(real), **info)
        if f in refs:
            e.update(role='reference', embedded=False)
        else:
            e['embedded'] = media == 'all' or (media == 'auto' and info['size'] <= max_mb * 1e6)
        media_map[f] = e
        entries.append(e)
    rel = {f: e['name'] for f, e in media_map.items()}
    manifest = dict(format=PACK_FORMAT, version=1, created=time.strftime('%Y-%m-%dT%H:%M:%S'), project=name, root=project,
                    files=[], media=entries)
    tmp = out + '.part'
    with zipfile.ZipFile(tmp, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in files:
            arc = os.path.relpath(p, project).replace(os.sep, '/')
            if p in texts:
                base = os.path.dirname(p)
                new = _json_strings(texts[p], lambda s, _path, base=base: rel.get(_ref_file(s, base) or '', s))
                z.writestr(arc, json.dumps(new, ensure_ascii=False, indent=1))
            else:
                z.write(p, arc)
            manifest['files'].append(arc)
        for e in entries:
            if e['embedded']:
                z.write(e['real'] or e['orig'], e['name'], compress_type=zipfile.ZIP_STORED)
        z.writestr(PACK_MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=1))
    os.replace(tmp, out)
    emb = [e for e in entries if e['embedded']]
    rep = dict(out=out, size_mb=round(os.path.getsize(out) / 1e6, 2), files=len(files), media=len(entries),
               embedded=[e['name'] for e in emb],
               not_embedded=[dict(name=e['name'], orig=e['orig'], size_mb=round(e['size'] / 1e6, 1), role=e.get('role'))
                             for e in entries if not e['embedded']])
    return rep


def _safe_member(name, dest):
    """Zip member name -> destination path inside dest, or None for unsafe names (absolute, '..', drive letters)."""
    n = name.replace('\\', '/')
    if not n or n.startswith('/') or re.match(r'^[A-Za-z]:', n) or any(part == '..' for part in n.split('/')):
        return None
    p = os.path.abspath(os.path.join(dest, *n.split('/')))
    return p if p.startswith(os.path.abspath(dest) + os.sep) else None


def default_search_dirs(zip_path=None):
    home = os.path.expanduser('~')
    out = [os.path.join(os.environ.get('ED_ROOT', 'C:/Claude Code/cinema-studio/edit'), 'input'), os.path.join(os.environ.get('ED_ROOT', 'C:/Claude Code/cinema-studio/edit'), 'output'), '/mnt/user-data/uploads', '/mnt/user-data/outputs', os.path.join(home, '.claude', 'uploads'),
           os.path.join(home, 'projects'), '/home/claude/projects', os.getcwd()]
    if zip_path:
        out.insert(0, os.path.dirname(os.path.abspath(zip_path)))
    return [d for d in dict.fromkeys(out) if os.path.isdir(d)]


def _scan(dirs, max_depth=4, limit=20000):
    """size -> [paths] for regular media files under dirs."""
    by_size, n = {}, 0
    for d in dirs:
        d = os.path.abspath(d)
        depth0 = d.rstrip(os.sep).count(os.sep)
        for root, sub, fnames in os.walk(d):
            if root.count(os.sep) - depth0 >= max_depth:
                sub[:] = []
            sub[:] = [s for s in sub if not s.startswith('.') or s in ('.claude',)]
            for fn in fnames:
                if os.path.splitext(fn)[1].lower() not in MEDIA_EXT:
                    continue
                p = os.path.join(root, fn)
                try:
                    if not os.path.isfile(p):
                        continue
                    by_size.setdefault(os.path.getsize(p), []).append(p)
                except OSError:
                    continue
                n += 1
                if n >= limit:
                    return by_size
    return by_size


def relink(entry, by_size, dur_tol=0.1):
    """Find a manifest media entry among scanned files: sha256 (exact) -> size + duration (fallback).
    -> (path, how) or (None, None)."""
    cands = by_size.get(entry.get('size'), [])
    if entry.get('sha256'):
        for p in cands:
            try:
                if sha256_file(p) == entry['sha256']:
                    return p, 'sha256'
            except OSError:
                continue
    if entry.get('duration') is not None:
        for p in cands:
            info = _media_info(p)
            if info.get('duration') is not None and abs(info['duration'] - entry['duration']) <= dur_tol:
                return p, 'size+duration'
    return None, None


def unpack(zip_path, project, search=None, log=say):
    """Zip from pack() -> project folder: files extracted (unsafe member names refused), embedded media extracted to
    media/, other media relinked by sha256 (fallback: same size and duration) from the search folders (default: the
    zip's folder, /mnt/user-data/uploads, ~/.claude/uploads, ~/projects, cwd) as symlinks media/<name> -> file;
    JSON references media/<name> and the old project root are rewritten to absolute paths in the new folder."""
    _exists(zip_path, 'archive')
    project = os.path.abspath(project)
    os.makedirs(project, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        try:
            manifest = json.loads(z.read(PACK_MANIFEST).decode('utf-8'))
        except KeyError:
            raise UserError(f'{zip_path} is not an Edit Studio pack (no {PACK_MANIFEST})')
        if manifest.get('format') != PACK_FORMAT:
            raise UserError(f'{zip_path}: unknown pack format {manifest.get("format")!r}')
        extracted = []
        for info in z.infolist():
            if info.is_dir() or info.filename == PACK_MANIFEST:
                continue
            if (info.external_attr >> 16) & 0o170000 == 0o120000:     # symlink member: never extracted
                log(f'[unpack] skipped symlink member {info.filename}')
                continue
            dst = _safe_member(info.filename, project)
            if dst is None:
                log(f'[unpack] refused unsafe member name {info.filename!r}')
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with z.open(info) as src, open(dst + '.part', 'wb') as fh:
                shutil.copyfileobj(src, fh, 1 << 20)
            os.replace(dst + '.part', dst)
            extracted.append(dst)
    report = dict(project=project, files=len(extracted), media=[])
    by_size = None
    media_abs = {}
    for e in manifest.get('media', []):
        dst = _safe_member(e['name'], project)
        if dst is None:
            continue
        row = dict(name=e['name'], orig=e.get('orig'))
        if e.get('embedded') and os.path.exists(dst):
            row['status'] = 'embedded'
        else:
            found, how = None, None
            orig = e.get('orig')
            if orig and os.path.isfile(orig) and os.path.getsize(orig) == e.get('size'):
                if e.get('sha256') and sha256_file(orig) == e['sha256']:
                    found, how = orig, 'sha256 (original path)'
            if found is None:
                if by_size is None:
                    dirs = list(search or []) + default_search_dirs(zip_path)
                    log(f'[unpack] looking for sources in: {", ".join(dirs)}')
                    by_size = _scan(dirs)
                found, how = relink(e, by_size)
            if found:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if os.path.lexists(dst):
                    os.remove(dst)
                try:
                    os.symlink(found, dst)
                except OSError:
                    shutil.copy2(found, dst)
                row.update(status='relinked', how=how, path=found)
            else:
                row.update(status='missing', size=e.get('size'), duration=e.get('duration'),
                           hint='upload this file again (same bytes), then run unpack again or pass --search DIR')
        report['media'].append(row)
        media_abs[e['name']] = dst
    old_root = manifest.get('root')
    for p in extracted:
        if not p.endswith('.json'):
            continue
        try:
            with open(p, encoding='utf-8') as fh:
                obj = json.load(fh)
        except (OSError, ValueError):
            continue

        def fix(s, _path):
            if s in media_abs:
                return media_abs[s]
            if old_root and (s == old_root or s.startswith(old_root.rstrip(os.sep) + os.sep)):
                return project + s[len(old_root.rstrip(os.sep)):]
            return s
        new = _json_strings(obj, fix)
        if new != obj:
            save_json(new, p)
    missing = [m for m in report['media'] if m['status'] == 'missing']
    report['ok'] = not missing
    return report


def cmd_pack(a):
    rep = pack(a.project, a.out, media=a.media, max_mb=a.max_mb, log=warn)
    if a.json:
        say(json.dumps(rep, ensure_ascii=False, indent=1))
    else:
        say(f"[pack] {rep['out']} ({rep['size_mb']} MB): {rep['files']} project files, {rep['media']} sources "
            f"({len(rep['embedded'])} inside)")
        for m in rep['not_embedded']:
            why = 'the reference video is never packed' if m.get('role') == 'reference' else 'relinked on unpack by hash'
            say(f"  not inside ({why}): {m['name']} <- {m['orig']} ({m['size_mb']} MB)")
    return rep


def cmd_unpack(a):
    rep = unpack(a.archive, a.project, search=a.search, log=warn)
    if a.json:
        say(json.dumps(rep, ensure_ascii=False, indent=1))
    else:
        say(f"[unpack] {rep['project']}: {rep['files']} files")
        for m in rep['media']:
            say(f"  {m['status']:9s} {m['name']}" + (f" <- {m.get('path')} ({m.get('how')})" if m['status'] == 'relinked' else '')
                + (f" - {m['hint']}" if m.get('hint') else ''))
    if not rep['ok']:
        sys.exit(3)
    return rep


# ----------------------------------------------------------------------------- fonts
def fonts_report(text, font='inter', lang=None, download=True):
    """Bundled fonts for a text: ed_text.fonts_for_text (the faces that will actually render it with `font`, as
    runs, missing characters and shaping warnings) + a cmap coverage table (fonts that contain every character)."""
    T = need('ed_text')
    if T is None:
        raise UserError('ed_text is not available')
    rep = dict(text=text, font=font)
    fn = getattr(T, 'fonts_for_text', None)
    if callable(fn):
        kw = dict(font=font, lang=lang, download=download)
        try:
            params = inspect.signature(fn).parameters
            kw = {k: v for k, v in kw.items() if k in params}
        except (TypeError, ValueError):
            pass
        try:
            rep['render'] = fn(text, **kw)
        except Exception as e:  # report, keep the coverage table
            rep['render_error'] = f'{type(e).__name__}: {e}'
    files = getattr(T, 'FONT_FILES', {})
    ref, covers = getattr(T, 'font_ref', None), getattr(T, 'font_covers', None)
    chars = sorted({c for c in text if not c.isspace()})
    rows = []
    if callable(ref) and callable(covers):
        for key in files:
            try:
                r = ref(key)
                miss = [c for c in chars if not covers(r, c)]
            except Exception as e:  # unreadable font file
                rows.append(dict(font=key, error=str(e)))
                continue
            rows.append(dict(font=key, covers=not miss, missing=''.join(miss[:40])))
    rep.update(chars=len(chars), full=[r['font'] for r in rows if r.get('covers')],
               partial=[dict(font=r['font'], missing=r['missing']) for r in rows if not r.get('covers') and 'missing' in r])
    return rep


def cmd_fonts(a):
    rep = fonts_report(a.text, font=a.font, lang=a.lang, download=not a.no_download)
    if a.json:
        say(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
        return rep
    r = rep.get('render')
    if isinstance(r, dict):
        runs = ' + '.join(f'{k}: {t!r}' for t, k in (r.get('runs') or [])[:8])
        say(f"[fonts] with '{a.font}': {', '.join(r.get('fonts') or []) or '-'}" + (f'  ({runs})' if len(r.get('runs') or []) > 1 else ''))
        if r.get('missing'):
            say(f"  no bundled font has: {r['missing']!r}")
        for w in r.get('warnings') or []:
            say(f'  warning: {w}')
    elif rep.get('render_error'):
        say(f"[fonts] ed_text.fonts_for_text failed: {rep['render_error']}")
    say(f"[fonts] {rep['chars']} distinct characters; fonts that set all of them: {', '.join(rep['full']) or 'none'}")
    for p in rep['partial'][:12]:
        say(f"  {p['font']}: missing {p['missing']!r}")
    return rep


# ----------------------------------------------------------------------------- doctor
def _run(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except (OSError, subprocess.TimeoutExpired) as e:
        return -1, str(e)


def doctor_checks(net=True):
    """-> list of dict(status OK|WARN|FAIL, check, detail, fix). FAIL = the engine cannot work."""
    res = []

    def add(status, check, detail, fix=''):
        res.append(dict(status=status, check=check, detail=detail, fix=fix))
    v = sys.version_info
    add('OK' if v >= (3, 9) else 'FAIL', 'python', sys.version.split()[0], '' if v >= (3, 9) else 'Python 3.9+ is needed')
    for tool in ('ffmpeg', 'ffprobe'):
        path = shutil.which(tool)
        if not path:
            add('FAIL', tool, 'not found', f'install {tool} (apt install ffmpeg)')
            continue
        rc, out = _run([tool, '-hide_banner', '-version'])
        first = out.split('\n')[0].split()
        add('OK' if rc == 0 else 'FAIL', tool, (first[2] if len(first) > 2 and first[1] == 'version' else ' '.join(first[:3]))
            + f' ({path})')
    if shutil.which('ffmpeg'):
        _, flt = _run(['ffmpeg', '-hide_banner', '-filters'])
        _, enc = _run(['ffmpeg', '-hide_banner', '-encoders'])
        have = lambda name, text: re.search(rf'\s{re.escape(name)}\s', text) is not None
        miss_hard = [n for n in ('libx264', 'aac') if not have(n, enc)]
        add('FAIL' if miss_hard else 'OK', 'ffmpeg encoders', 'libx264, aac' if not miss_hard else f'missing {", ".join(miss_hard)}',
            'an ffmpeg build with libx264' if miss_hard else '')
        for name, why in (('ass', 'libass (burned-in ASS subtitles)'), ('zscale', 'zscale/zimg (HDR and colour-space conversion)'),
                          ('loudnorm', 'loudnorm'), ('ebur128', 'ebur128 (loudness QA)')):
            ok = have(name, flt)
            add('OK' if ok else 'WARN', f'ffmpeg {name}', why if ok else f'missing: {why}',
                '' if ok else 'a full ffmpeg build (e.g. the distribution package)')
    for mod, hard, why in (('numpy', True, 'arrays'), ('cv2', True, 'OpenCV: decoding helpers, faces, warps'),
                           ('scipy', True, 'signal processing (music, planner, SFX)'), ('yaml', True, 'genre / move cards'),
                           ('PIL', True, 'text rendering'), ('onnxruntime', False, 'speech recognition, fine person masks'),
                           ('fontTools', False, 'font coverage checks (fonts --text)')):
        try:
            m = importlib.import_module(mod)
            ver = getattr(m, '__version__', None) or getattr(m, 'version', None)
            ver = ver if isinstance(ver, str) else ''
            detail = f'{ver} - {why}'.strip(' -')
            if mod == 'cv2' and not hasattr(m, 'dnn'):
                add('FAIL', 'opencv', f'{ver} without the dnn module', 'opencv-python with dnn (faces, objects)')
                continue
            add('OK', {'cv2': 'opencv', 'PIL': 'pillow', 'yaml': 'pyyaml'}.get(mod, mod), detail)
        except Exception as e:
            add('FAIL' if hard else 'WARN', mod, f'not importable ({type(e).__name__})', f'install {mod} ({why})')
    try:
        from PIL import features
        raqm = features.check('raqm')
        add('OK' if raqm else 'WARN', 'pillow raqm', f"raqm {features.version('raqm')} (complex scripts, right-to-left)" if raqm
            else 'no raqm: Arabic/Hebrew/Indic text is set without shaping', '' if raqm else 'Pillow built with libraqm')
    except Exception:
        pass
    try:
        sh = importlib.import_module('sherpa_onnx')
        add('OK', 'sherpa-onnx', f"python package {getattr(sh, '__version__', '')} (optional)")
    except Exception:
        add('OK', 'sherpa-onnx', 'python package not installed - not needed: ed_voice runs the sherpa-onnx model exports '
                                 'with onnxruntime')
    voice = None
    try:
        voice = importlib.import_module('ed_voice')
    except Exception as e:
        add('WARN', 'speech models', f'ed_voice not importable ({type(e).__name__})')
    if voice is not None:
        try:
            inst = voice.installed_models()
            ctc = (voice.CACHE / voice.CTC['dir'] / 'model.int8.onnx').exists()
            vad = (voice.CACHE / voice.VAD_FILE).exists()
            ok = bool(inst) and ctc and vad
            add('OK' if ok else 'WARN', 'speech models',
                f"whisper {'/'.join(inst) or 'none'}, aligner {'yes' if ctc else 'no'}, VAD {'yes' if vad else 'no'} in {voice.CACHE}",
                '' if ok else 'downloaded on first use, or now: edit.py voice models --get turbo ctc vad')
        except Exception as e:
            add('WARN', 'speech models', f'unknown ({type(e).__name__}: {e})')
    fdir = os.path.join(HERE, 'assets', 'fonts')
    ttf = sorted(glob.glob(os.path.join(fdir, '*.ttf')) + glob.glob(os.path.join(fdir, '*.otf')))
    lic = glob.glob(os.path.join(fdir, '*_OFL.txt'))
    want = ['inter_Inter-VF.ttf', 'oswald_Oswald-VF.ttf', 'notosans_NotoSans-VF.ttf', 'jetbrainsmono_JetBrainsMono-VF.ttf']
    lost = [w for w in want if not os.path.exists(os.path.join(fdir, w))]
    add('FAIL' if (lost or not ttf) else 'OK', 'bundled fonts', f'{len(ttf)} font files, {len(lic)} OFL licences'
        + (f'; missing {", ".join(lost)}' if lost else ''), 'reinstall the skill (engine/assets/fonts)' if lost else '')
    mdir = os.path.join(HERE, 'models')
    for fn, hard, why in (('face_detection_yunet_2023mar.onnx', True, 'faces (framing, reframe, QA)'),
                          ('human_segmentation_pphumanseg_2023mar.onnx', True, 'person masks'),
                          ('object_detection_nanodet_2022nov.onnx', False, 'object types in remakes (optional)')):
        p = os.path.join(mdir, fn)
        ok = os.path.exists(p) and os.path.getsize(p) > 100_000
        if ok and hard:
            try:
                import cv2
                if fn.startswith('face'):
                    cv2.FaceDetectorYN.create(p, '', (320, 320))
                else:
                    cv2.dnn.readNet(p)
            except Exception as e:
                ok, why = False, f'unreadable ({type(e).__name__})'
        add('OK' if ok else ('FAIL' if hard else 'WARN'), f'model {fn.split("_")[0]}_{fn.split("_")[1]}',
            why if ok else f'{fn} missing - {why}', '' if ok else ('reinstall the skill (engine/models)' if hard else 'not included; remakes work without it'))
    cache = os.environ.get('EDIT_STUDIO_CACHE') or os.path.join(os.environ.get('ED_ROOT', 'C:/Claude Code/cinema-studio/edit'), 'cache')
    try:
        os.makedirs(cache, exist_ok=True)
        probe = os.path.join(cache, f'.doctor_{os.getpid()}')
        with open(probe, 'w') as fh:
            fh.write('ok')
        os.remove(probe)
        free = shutil.disk_usage(cache).free / 1e9
        add('OK' if free >= 2 else 'WARN', 'cache', f'{cache} writable, {free:.1f} GB free',
            '' if free >= 2 else 'free some disk space (models and renders need a few GB)')
    except OSError as e:
        add('FAIL', 'cache', f'{cache} not writable ({e})', 'set EDIT_STUDIO_CACHE to a writable folder')
    try:
        cpus = len(os.sched_getaffinity(0))
    except AttributeError:
        cpus = os.cpu_count() or 1
    mem = None
    try:
        with open('/proc/meminfo') as fh:
            mm = {ln.split(':')[0]: int(ln.split()[1]) for ln in fh if ':' in ln}
        mem = mm.get('MemAvailable', 0) / 1e6
    except (OSError, ValueError, IndexError):
        pass
    add('OK' if (mem is None or mem >= 2) else 'WARN', 'machine', f'{cpus} CPU cores' + (f', {mem:.1f} GB RAM available' if mem else ''),
        '' if (mem is None or mem >= 2) else 'close other jobs: renders and speech models need 2+ GB')
    if net:
        import urllib.request
        url = 'https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx'
        try:
            req = urllib.request.Request(url, method='GET', headers={'Range': 'bytes=0-15', 'User-Agent': 'edit-studio-doctor'})
            with urllib.request.urlopen(req, timeout=8) as r:
                r.read(16)
                code = r.status
            add('OK' if code in (200, 206) else 'WARN', 'github', f'release downloads reachable (HTTP {code})')
        except Exception as e:
            add('WARN', 'github', f'release downloads unreachable ({type(e).__name__}: {str(e)[:60]})',
                'models are downloaded on first use; without network speech recognition needs pre-installed models')
    return res


def cmd_doctor(a):
    rows = doctor_checks(net=not a.offline)
    fails = [r for r in rows if r['status'] == 'FAIL']
    if a.json:
        say(json.dumps(dict(ok=not fails, checks=rows), indent=1))
    else:
        for r in rows:
            say(f"{r['status']:4s}  {r['check']:24s} {r['detail']}" + (f"  -> {r['fix']}" if r['fix'] and r['status'] != 'OK' else ''))
        say(f"doctor: {len(fails)} hard failure(s), {sum(r['status'] == 'WARN' for r in rows)} warning(s)")
    if fails:
        sys.exit(1)
    return rows


# ----------------------------------------------------------------------------- misc
def cmd_track(a):
    import ed_audio as AU
    _exists(a.audio, 'audio')
    res = AU.analyze(a.audio)
    save_json(res, a.out)
    if a.plot:
        AU.plot(res, a.plot)
    say(f"[track] {a.out}: {res['bpm']} BPM, {len(res['beats'])} beats, drops at {[d['t'] for d in res['drops']]}")


SUBS_FLAGS = ('--style', '--canvas', '--breaks')


def voice_subs(V_, argv):
    """edit.py voice subs with the caption preset, canvas and break points passed to ed_voice.subtitle_chunks
    (the other flags are ed_voice's own: same defaults, same outputs)."""
    p = argparse.ArgumentParser(prog='edit.py voice subs', formatter_class=_Fmt,
                                description='words.json -> subtitle / karaoke layers (ed_voice.subtitle_chunks), SRT, ASS.',
                                epilog='examples:\n  edit.py voice subs w.json --style podcast_bold --canvas 1080x1920 '
                                       '--breaks 4.2,9.75 --out subs.json --ass subs.ass')
    p.add_argument('words')
    p.add_argument('--kind', choices=['subtitle', 'karaoke'], help='default: subtitle, or what the --style preset makes')
    p.add_argument('--fps', type=float, default=30)
    p.add_argument('--max-chars', type=int)
    p.add_argument('--max-lines', type=int)
    p.add_argument('--horizontal', action='store_true', help='16:9 (default canvas 1920x1080)')
    p.add_argument('--style', metavar='PRESET', help='ed_text caption preset (name or alias): line length, line count '
                                                       'and kind follow it')
    p.add_argument('--canvas', metavar='WxH', help='output size (default 1080x1920; --horizontal 1920x1080)')
    p.add_argument('--breaks', metavar='T1,T2,...', help='output seconds where the picture / audio jumps (jump cuts, '
                                                         'part joins): no caption spans one')
    p.add_argument('--out')
    p.add_argument('--srt')
    p.add_argument('--ass')
    a = p.parse_args(argv)
    _exists(a.words, 'words')
    kw = dict(kind=a.kind or (None if a.style else 'subtitle'), fps=a.fps, max_chars=a.max_chars,
              max_lines=a.max_lines, vertical=not a.horizontal)
    if a.style:
        try:
            import ed_text as Tx
            canon = Tx.caption_style_name(a.style)
        except Exception:                                   # no ed_text: ed_voice falls back to plain defaults
            canon = a.style
        if not canon:
            raise UserError(f'unknown caption style {a.style!r}; known: {", ".join(sorted(getattr(Tx, "CAPTION_STYLES", {})))}')
        kw['style'] = canon
    if a.canvas:
        kw['canvas'] = parse_canvas(a.canvas)
    if a.breaks:
        try:
            kw['breaks'] = sorted(_secs(x) for x in a.breaks.split(',') if x.strip())
        except ValueError:
            raise UserError(f'--breaks must be seconds like 4.2,9.75 (or 0:04.2), got {a.breaks!r}')
    L = V_.subtitle_chunks(load_json(a.words), **kw)
    if a.srt:
        V_.to_srt(L, a.srt)
    if a.ass:
        V_.to_ass(L, a.ass, canvas=kw.get('canvas') or ((1920, 1080) if a.horizontal else (1080, 1920)))
    txt = json.dumps(L, ensure_ascii=False, indent=1)
    if a.out:
        with open(a.out, 'w', encoding='utf-8') as f:
            f.write(txt)
        say(f'-> {a.out}')
    else:
        say(txt)
    return L


def cmd_voice(argv):
    """Pass everything after 'voice' to ed_voice's own command line ('subs' with --style / --canvas / --breaks, or
    its help, is handled here: voice_subs)."""
    V_ = need('ed_voice')
    if V_ is None or not callable(getattr(V_, 'main', None)):
        raise UserError('ed_voice is not available')
    if argv and argv[0] == 'subs' and any(x.split('=')[0] in SUBS_FLAGS + ('-h', '--help') for x in argv[1:]):
        return voice_subs(V_, argv[1:])
    if argv and argv[0] == 'transcribe' and '--background' in argv and not _JOB:
        if '-h' in argv or '--help' in argv:
            say('edit.py voice transcribe ... --background: run detached (log + status in the --out folder, else here)')
        else:
            out = next((argv[i + 1] for i, x in enumerate(argv[:-1]) if x == '--out'), None)
            out = out or next((x.split('=', 1)[1] for x in argv if x.startswith('--out=')), None)
            folder = os.path.dirname(os.path.abspath(out)) if out else os.getcwd()
            return spawn_job('voice transcribe', ['voice'] + argv, folder, result=out)
    old = sys.argv[0]
    sys.argv[0] = 'edit.py voice'
    try:
        return V_.main(argv)
    finally:
        sys.argv[0] = old


def cmd_transcribe(a):
    fn = need('ed_voice', 'transcribe')
    if fn is None:
        raise UserError('ed_voice.transcribe is not available')
    _exists(a.audio, 'media')
    res = fn(a.audio, lang=a.lang)
    save_json(res, a.out)
    say('[transcribe]', a.out, len(res.get('words', [])), 'words', res.get('lang'))


# ----------------------------------------------------------------------------- argument parsing
class _Fmt(argparse.RawDescriptionHelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=30, width=118)


def build_parser():
    ap = argparse.ArgumentParser(prog='edit.py', description=__doc__, formatter_class=_Fmt, add_help=False)
    ap.add_argument('-h', '--help', action='store_true')
    sub = ap.add_subparsers(dest='cmd', metavar='<command>')

    def P(name, help_, desc, epilog=''):
        return sub.add_parser(name, help=help_, description=desc, epilog=epilog, formatter_class=_Fmt)

    def common(p, sheet=True):
        g = p.add_argument_group('after the timeline is written')
        g.add_argument('--no-render', action='store_true', help='write the timeline only')
        g.add_argument('--no-qa', action='store_true', help='skip QA after the preview')
        if sheet:
            g.add_argument('--no-sheet', action='store_true', help='skip the plan sheet plan_vN.jpg')
        g.add_argument('--full', action='store_true', help='high-quality preview (optical flow) instead of the fast draft')
        g.add_argument('--fast', action='store_true', help=argparse.SUPPRESS)          # r4 name: the draft is fast already
        g.add_argument('--workers', type=int, metavar='N', help='render threads (default: up to 4)')

    def background(p):
        p.add_argument('--background', action='store_true',
                       help='run detached (log + job file in the project folder); poll with edit.py status PROJECT')

    def wishes(p):
        g = p.add_argument_group('planner wishes (ed_plan.plan_genre options)')
        g.add_argument('--style', help='house style: a preset name or plain words ("clean and expensive", "gritty street")')
        g.add_argument('--variant', type=int, metavar='N', help='another version of the style (0 = as written)')
        g.add_argument('--avoid', nargs='+', metavar='EDL', help="earlier versions whose choices this one steers away from")
        g.add_argument('--n-shots', '--shots', dest='n_shots', type=int, metavar='N', help='exact number of shots')
        g.add_argument('--order', choices=['given', 'auto'], help='given: shot i = footage file i')
        g.add_argument('--require', '--moves', dest='require', nargs='+', metavar='ID',
                       help='moves (ids or families) that must appear')
        g.add_argument('--forbid', '--no-moves', dest='forbid', nargs='+', metavar='ID', help='moves that must not appear')
        g.add_argument('--music-in', metavar='S', help='track second at output 0 (seconds or m:ss)')
        g.add_argument('--drop-at', metavar='S', help='output second where the strongest drop lands')
        g.add_argument('--drop-t', metavar='S', help='track second of the drop (overrides the detector)')
        g.add_argument('--bpm', type=float, help='tempo hint')
        g.add_argument('--bars', type=int, help='length in whole bars')
        g.add_argument('--cut-rate', type=float, metavar='X', help='x the card cutting rate (2 = twice as many cuts)')
        g.add_argument('--sfx-level', '--sfx', dest='sfx_level', choices=['none', 'light', 'genre', 'heavy'],
                       help='sound effects level (default: the genre / style)')
        g.add_argument('--sfx-dir', metavar='DIR', help="a folder of the user's own sound effects (used instead of synthesis)")
        sp = p.add_argument_group('speech genres (clips, ugc, explainer) and voice-overs')
        sp.add_argument('--words', metavar='JSON', help='transcript (ed_voice format) instead of recognising the voice')
        sp.add_argument('--lang', help='speech language')
        sp.add_argument('--voice', metavar='FILE', help='voice-over file (motivation)')
        sp.add_argument('--src-in', metavar='S', help='source second where the excerpt starts')
        sp.add_argument('--src-out', metavar='S', help='source second where it ends')
        sp.add_argument('--from', dest='from_phrase', metavar='PHRASE', help='the excerpt starts at this phrase')
        sp.add_argument('--to', dest='to_phrase', metavar='PHRASE', help='the excerpt ends with this phrase')
        sp.add_argument('--subtitles', choices=['karaoke', 'subtitle', 'none'])

    p = P('plan', 'footage + genre or style (+ track) -> edit',
          'Scenario "genre edit": footage, a genre card or a style in plain words, and a track (speech genres: optional)\n'
          '-> timeline (ed_plan.plan_genre) -> plan sheet -> fast labelled preview -> QA. Every run writes the next\n'
          'version edl_vN.json in --project. "Another version": edit.py variant EDL --variant N.',
          'examples:\n  edit.py plan --track song.wav --footage a.mp4 b.mp4 --genre phonk --project ~/projects/x --dur 20\n'
          '  edit.py plan --track song.wav --footage *.mp4 --style "clean and expensive" --project ~/projects/x\n'
          '  edit.py plan ... --n-shots 5 --order given --require time.speed_ramp --drop-at 8.0 --sfx-level heavy\n'
          '  edit.py plan --footage talk.mp4 broll.mp4 --genre clips --from "the first words" --to "the last" --project P')
    p.add_argument('--track', help='music file (optional for speech genres: clips, ugc, explainer)')
    p.add_argument('--footage', nargs='+', required=True, help='video files')
    p.add_argument('--genre', help='genre slug (genres/<slug>.md): viral, epic, phonk, ... (optional with --style)')
    p.add_argument('--project', required=True, help='project folder (created if missing)')
    p.add_argument('--dur', type=float, help='target length in seconds')
    p.add_argument('--canvas', default='1080x1920', help='WxH (default 1080x1920)')
    p.add_argument('--fps', type=int, default=30)
    p.add_argument('--seed', type=int, default=1)
    p.add_argument('--title')
    p.add_argument('--word')
    p.add_argument('--outro-text')
    p.add_argument('--no-reframe', action='store_true')
    p.add_argument('--sample-fps', type=float, default=6.0)
    wishes(p)
    common(p)
    background(p)

    v_ = P('variant', 'another version of a planned edit',
           'Re-plan a timeline made by "plan" (or "storyboard") from the same inputs - track, footage, genre, options,\n'
           'length - as another version: --variant N re-seeds the choices inside the genre / style rules, --style\n'
           'switches the style, and the given version (plus --avoid ones) is avoided: its transitions, signature moves\n'
           'and shot order are steered away from. Composites made by "sequence" are re-planned from their stored spec\n'
           '(ed_sequence.variant): the cut points by words and the drop stay, looks, moves, shot windows, punch-ins and\n'
           'transitions change. Writes the next version next to it, sheet, preview, QA.',
           'examples:\n  edit.py variant ~/projects/x/edl_v2.json --variant 2\n'
           '  edit.py variant ~/projects/x/edl_v2.json --variant 1 --style "dreamy retro"')
    v_.add_argument('edl')
    v_.add_argument('--variant', type=int, required=True, metavar='N')
    v_.add_argument('--style', help='another house style (preset name or words); default: the one of EDL')
    v_.add_argument('--avoid', nargs='+', metavar='EDL', help='more earlier versions to steer away from')
    common(v_)
    background(v_)

    sb = P('storyboard', 'a video to generate, cut to the track',
           'A whole video to generate with edit-gen (Higgsfield, paid, only after an explicit yes): the music is planned\n'
           'like a genre edit and every slot becomes a gap with a brief (shot size, subject, action, camera move, duration\n'
           'with handles, continuity, look, prompt) in meta.gaps (ed_plan.plan_storyboard). The animatic (slates) is\n'
           'rendered as the preview. Fill the slots later: edit.py fill EDL MAP.json.',
           'example:\n  edit.py storyboard --track song.wav --style "gritty street" --brief "a boxer before a fight" '
           '--character "a tall boxer in a red hoodie" --project ~/projects/gen --n-shots 8')
    sb.add_argument('--track', required=True)
    sb.add_argument('--project', required=True)
    sb.add_argument('--genre')
    sb.add_argument('--style')
    sb.add_argument('--variant', type=int)
    sb.add_argument('--brief', help='what the video is about (the subject of every shot)')
    sb.add_argument('--character', help='one character kept identical in every shot')
    sb.add_argument('--dur', type=float)
    sb.add_argument('--n-shots', type=int)
    sb.add_argument('--canvas', default='1080x1920')
    sb.add_argument('--fps', type=int, default=30)
    common(sb)
    background(sb)

    fl = P('fill', 'plug clips into gap / storyboard slots',
           'Plug generated (or your own) clips into the gap slots of a timeline (ed_plan.fill_gaps): per slot the best\n'
           'window of the clip, a slow-down when it is too short, a subject crop with the planned zooms, the planned\n'
           'grade fitted to the clip. MAP = a JSON file or inline JSON {slot: path | {"path", "t"}}; slot = segment id\n'
           '(C03), #N, or the slot source (slot03). Writes the next version, sheet, preview, QA.',
           'example:\n  edit.py fill ~/projects/gen/edl_v1.json \'{"C01": "/mnt/user-data/uploads/shot1.mp4", "#2": "shot2.mp4"}\'')
    fl.add_argument('edl')
    fl.add_argument('map', help='JSON file or inline JSON')
    fl.add_argument('--out', help='default: the next version next to EDL')
    common(fl)

    mr = P('measure-ref', 'measure a clip of a named effect -> moves + params',
           'Measure a short reference clip or GIF of a named effect or transition (ed_remake.measure_effect): cuts,\n'
           'flashes and dips (opacity curve, decay), whips (streak axis, camera direction), zooms (scale, duration,\n'
           'easing), rolls, shakes (amplitude, rotation, decay), speed ramps and freezes, RGB splits. Prints the move\n'
           'cards that reproduce it, best first, with params; each "apply" line is an edit.py cmd command once its\n'
           '"at" (time), "between" (two clips) or segment id is filled in. Works on MP4 / MOV / WebM and dithered GIFs\n'
           '(tested at 15-30 fps). CLIP is a local file: links are not downloaded - for a video on a social platform\n'
           'use the original file or a screen recording you have the rights to. Reference clips stay in the project:\n'
           'they are never part of an output or of the package.',
           'examples:\n  edit.py measure-ref ~/projects/x/refs/whip.gif --sheet ~/projects/x/refs/whip_sheet.jpg\n'
           '  edit.py measure-ref clip.mp4 --json > measured.json\n'
           '  edit.py cmd P/edl_v2.json \'{"op":"transition","move":"trans.whip","between":["#3","#4"],"params":{"dir":"right"}}\'')
    mr.add_argument('clip')
    mr.add_argument('--from', dest='t_from', metavar='TIME', help='measure from here (a longer clip: 0:12.5 or 12.5)')
    mr.add_argument('--to', dest='t_to', metavar='TIME', help='... to here (default: 30 s after --from, or the end)')
    mr.add_argument('--fps', type=float, help='analysis rate (default: the clip fps; GIFs: their average)')
    mr.add_argument('--sheet', metavar='OUT.jpg', help='frames with the events marked + the measured curves')
    mr.add_argument('--top', type=int, default=5, help='candidates to print (default 5)')
    mr.add_argument('--json', action='store_true', help='print the whole measurement')

    s = P('sequence', 'composite edit from a spec (talk part + music edit ...)',
          'A composite edit described by a spec: talk parts cut by spoken phrases, music edits, transitions, one music\n'
          'track (ed_sequence.plan_sequence) -> edl_vN.json -> plan sheet -> preview -> QA.\n'
          'Relative paths in the spec are resolved against the spec\'s folder.',
          'examples:\n  edit.py sequence --example > spec.json      (a commented example to start from)\n'
          '  edit.py sequence spec.json --project ~/projects/aura')
    s.add_argument('spec', nargs='?', help='SPEC.json')
    s.add_argument('--project', help='project folder')
    s.add_argument('--cache', help='analysis cache folder (default PROJECT/.ed_cache)')
    s.add_argument('--example', action='store_true', help='print an example spec and exit')
    common(s)
    background(s)

    r = P('remake', 'redo a reference edit with your footage',
          'Scenario "remake": the reference edit\'s exact timing, text and effects with your footage (ed_remake.draft).\n'
          'Writes edl_vN.json + PROJECT/remake/ (slots.jpg = reference | top-5 candidates per slot, survey.jpg = every\n'
          'shot of your footage, candidates.json), renders a preview, runs QA and writes compare_vN.jpg (reference |\n'
          'remake per slot). Re-pick slots by eye: --pick SLOT=TIME (SLOT = S05 | #5, TIME = 12:34.5 or SOURCE@1:02).',
          'examples:\n  edit.py remake --ref ref.mp4 --footage film.mp4 --project ~/projects/r\n'
          '  edit.py remake --ref ref.mp4 --footage a.mp4 b.mp4 --music clean_track.wav --project ~/projects/r\n'
          '  edit.py remake --project ~/projects/r --pick S05=12:34.5 "#7=b@0:41.2"')
    r.add_argument('--ref', help='reference edit (video)')
    r.add_argument('--footage', '--src', dest='footage', nargs='+', help='your footage (one or more files)')
    r.add_argument('--music', '--track', dest='music', help='separate music track: replaces the reference audio '
                                                            '(aligned to it automatically)')
    r.add_argument('--music-in', type=float, metavar='S', help='music second at output 0 (skips the alignment)')
    r.add_argument('--project', required=True)
    r.add_argument('--canvas', default='1080x1920')
    r.add_argument('--fps', type=int, help='default: the reference fps')
    r.add_argument('--sample-fps', type=float, help='footage analysis rate (default 3)')
    r.add_argument('--pick', nargs='+', metavar='SLOT=TIME', help='swap the moment of slots in the latest version')
    r.add_argument('--edl', help='--pick: timeline to start from (default: the latest version)')
    r.add_argument('--version', type=int, help='--pick: version to start from')
    common(r, sheet=False)
    background(r)

    d = P('render', 'preview or final render (progress + ETA)',
          'Render a timeline. Preview = 540x960 with labels (#N, timecode); --final = full size, no labels. Progress\n'
          'lines go to stderr with fps and ETA; <out>.progress.json is kept for `edit.py status`. QA runs after full\n'
          'renders. --background detaches the render (log next to the output) so long finals do not block.',
          'examples:\n  edit.py render --project P                      (latest version, preview)\n'
          '  edit.py render P/edl_v4.json --frames 180:260    (partial check, no sound)\n'
          '  edit.py render --project P --final --background  then: edit.py status P\n'
          '  edit.py render P/edl_v4.json --stills P/stills.jpg --at first')
    d.add_argument('edl', nargs='?', help='EDL.json (or --project)')
    d.add_argument('--project')
    d.add_argument('--version', type=int)
    d.add_argument('--final', action='store_true', help='full size, no labels, best interpolation')
    d.add_argument('--out', help='output file (default preview_vN.mp4 / final_vN.mp4 next to the EDL)')
    d.add_argument('--labels', action='store_true')
    d.add_argument('--no-labels', action='store_true')
    d.add_argument('--frames', metavar='A:B', help='render only frames A..B (no audio)')
    d.add_argument('--interp', choices=['nearest', 'blend', 'flow'])
    d.add_argument('--workers', type=int)
    d.add_argument('--full', action='store_true', help='high-quality preview (optical flow) instead of the fast draft')
    d.add_argument('--draft', action='store_true', help='fast preview: 540x960, blend interpolation (the default)')
    d.add_argument('--fast', action='store_true', help='optical flow only where the crop samples')
    d.add_argument('--stills', metavar='SHEET.jpg', help='contact sheet of frames instead of a video')
    d.add_argument('--at', help='stills: frames "first" | "0:120:6" | "5,40,100"')
    d.add_argument('--no-qa', action='store_true')
    d.add_argument('--background', action='store_true', help='run detached; poll with edit.py status')

    fr = P('frame', 'one frame at full output resolution',
           'One frame of the timeline rendered like the final (full canvas size, optical flow unless the EDL sets\n'
           'its own frame_interp, no labels) -> PNG (or .jpg): for sharpness, colour and caption checks at 1:1.\n'
           '(render --stills makes a small contact sheet of many frames.)',
           'examples:\n  edit.py frame P/edl_v3.json 0:07.5 --out P/check_7s.png\n  edit.py frame P/edl_v3.json f225')
    fr.add_argument('edl')
    fr.add_argument('at', metavar='T', help='time (7.5 or 0:07.5) or frame number (f225)')
    fr.add_argument('--out', help='PNG or JPG path (default: next to the EDL, frame_vN_fF.png)')
    fr.add_argument('--preview', action='store_true', help='at the preview size (540x960 for a 1080x1920 canvas)')

    st = P('status', 'progress of background jobs and renders',
           'Background jobs (plan, variant, sequence, remake, storyboard, voice transcribe with --background: state,\n'
           'time, what it is doing now, the result or the error) and renders (frames, fps, ETA) of a folder; or one\n'
           'render: OUT.mp4 / its .progress.json.', 'example:\n  edit.py status ~/projects/x')
    st.add_argument('target', nargs='?', help='output video, progress file or project folder (default .)')
    st.add_argument('--json', action='store_true')

    q = P('qa', 'measure a render against its timeline',
          'QA of a rendered file (ed_qa.run): frame count, cut accuracy, rhythm, loudness, black/white/frozen frames,\n'
          'flashes, safe zone, faces, image stats. Writes OUT/qa.json, qa.md and contact sheets.')
    q.add_argument('edl')
    q.add_argument('video')
    q.add_argument('--out', help='QA folder (default qa_vN next to the video)')
    q.add_argument('--json', action='store_true', help='print the full report')

    c = P('cmd', 'point edit -> next version',
          'Point edit: a structured command (ed_plan.apply_command, genre-aware), a ripple edit (insert / delete_clip /\n'
          'delete_range: everything after the point moves, the music stays) or a low-level set/append/delete on any\n'
          'path; writes the next version (edl_vN+1.json). A JSON list applies several commands in order. An edit that\n'
          'would break the timeline (both validators) is refused with the reason; "force": true writes it anyway.\n'
          'Ripple edits keep source timing and camera motion of clips they cut (jump cut); an inserted clip names a\n'
          'source ("src") or a file ("path", added as a source) and takes the look of the clip before it.',
          'examples:\n  edit.py cmd P/edl_v4.json \'{"op": "add", "move": "zoom.crash", "at": "0:07"}\' --render\n'
          '  edit.py cmd P/edl_v4.json \'{"op": "insert", "at": "0:07", "dur": 0.5, "segment": {"src": "a", "t": 12.0}}\'\n'
          '  edit.py cmd P/edl_v4.json \'{"op": "insert", "at": "0:07", "frames": 12, "segment": {"path": "b-roll.mp4"}}\'\n'
          '  edit.py cmd P/edl_v4.json \'{"op": "delete_clip", "clip": "#5"}\'\n'
          '  edit.py cmd P/edl_v4.json \'{"op": "delete_range", "from": "0:07", "to": "0:07.5"}\'\n'
          '  edit.py cmd P/edl_v4.json \'{"op": "set", "path": "segments.C03.crop.z", "value": 1.3}\'')
    c.add_argument('edl')
    c.add_argument('command', help='inline JSON, @file.json or a JSON file')
    c.add_argument('--out')
    c.add_argument('--render', action='store_true', help='render a preview + QA of the new version')
    common(c, sheet=False)

    v = P('validate', 'contract check of a timeline',
          'Two checks: the planner contract (ed_plan.validate_edl, engine/TIMELINE.md) and the renderer\'s own check\n'
          '(ed_edl.validate: files, frame ranges, overlaps, unknown fx / transition / layer kinds). Exit code 1 on errors.')
    v.add_argument('edl')
    v.add_argument('--verbose', '-v', action='store_true', help='list every problem (default: the first 6 per check)')

    ps = P('plan-sheet', 'the plan as an image',
           'One tile per segment: the frame that will be used (with its crop and grade), a big #N, output time, part,\n'
           'source moment and moves; frames without a segment and segments without a usable source are NO SHOT tiles.\n'
           'Fast: one decoded frame per segment, no render.',
           'example:\n  edit.py plan-sheet P/edl_v2.json --out P/plan_v2.jpg')
    ps.add_argument('edl', nargs='?')
    ps.add_argument('--project')
    ps.add_argument('--version', type=int)
    ps.add_argument('--out', help='default plan_vN.jpg next to the EDL')
    ps.add_argument('--cols', type=int, default=6)
    ps.add_argument('--width', type=int, default=270, help='tile width in px')
    ps.add_argument('--at', choices=['mid', 'first'], default='mid', help='which frame of each segment')
    ps.add_argument('--json', action='store_true')

    t = P('track', 'music analysis', 'Tempo, beats, bars, sections and drops of a music file (ed_audio.analyze).')
    t.add_argument('audio')
    t.add_argument('out')
    t.add_argument('--plot')

    P('voice', 'speech tools (ed_voice)', 'Everything after "voice" goes to ed_voice: transcribe, subs, jumpcuts, align, plan,\n'
                                          'models. edit.py voice -h for its options.')
    tr = P('transcribe', 'words with timestamps (= voice transcribe)', 'Shortcut for `edit.py voice transcribe`.')
    tr.add_argument('audio')
    tr.add_argument('out')
    tr.add_argument('--lang')

    pk = P('pack', 'project -> zip',
           'Pack a project: timelines and project data (json, md, srt, py), plus a manifest of every source the\n'
           'timelines use (sha256, size, duration). Sources up to --max-mb are stored inside (media/<name>); bigger\n'
           'ones are relinked on unpack by hash. Renders, sheets, QA folders and caches are left out.',
           'example:\n  edit.py pack ~/projects/aura --out /mnt/user-data/outputs/aura.edit.zip')
    pk.add_argument('project')
    pk.add_argument('--out', help='default <project>.edit.zip next to the project folder')
    pk.add_argument('--media', choices=['auto', 'all', 'none'], default='auto',
                    help='store sources inside: auto = files up to --max-mb (default), all, none')
    pk.add_argument('--max-mb', type=float, default=256.0)
    pk.add_argument('--json', action='store_true')

    up = P('unpack', 'zip -> project (relinks sources)',
           'Unpack a pack into a project folder. Sources stored inside go to media/; the others are found again by\n'
           'sha256 (fallback: same size and duration) in --search folders and the usual upload folders, and linked\n'
           'as media/<name>. Timelines are rewritten to the new paths. Exit code 3 when a source is still missing.',
           'example:\n  edit.py unpack aura.edit.zip --project ~/projects/aura --search /mnt/user-data/uploads')
    up.add_argument('archive')
    up.add_argument('--project', required=True)
    up.add_argument('--search', nargs='+', metavar='DIR', help='extra folders to look for the sources')
    up.add_argument('--json', action='store_true')

    fo = P('fonts', 'fonts that can set a text',
           'Which bundled OFL fonts set --text: the faces ed_text will use with --font (per-character fallback runs,\n'
           'missing characters, shaping warnings; CJK faces are fetched on demand unless --no-download) and the\n'
           'fonts that contain every character on their own.',
           'example:\n  edit.py fonts --text "Hello, world" --font anton')
    fo.add_argument('--text', required=True)
    fo.add_argument('--font', default='inter', help='font key, type class or ed_edl font name (default inter)')
    fo.add_argument('--lang', help='language hint (CJK region, shaping)')
    fo.add_argument('--no-download', action='store_true', help='never fetch CJK faces')
    fo.add_argument('--json', action='store_true')

    dr = P('doctor', 'environment check',
           'One line per check: ffmpeg/ffprobe (+ libx264, libass, zscale, loudness filters), Python libraries,\n'
           'Pillow raqm, speech models, bundled fonts and models, cache folder, CPU/RAM, GitHub reachability.\n'
           'Exit code 1 when something the engine cannot work without is missing.')
    dr.add_argument('--json', action='store_true')
    dr.add_argument('--offline', action='store_true', help='skip the network check')
    return ap


def overview():
    say(__doc__.rstrip())


def dispatch(a, ap):
    if a.cmd == 'plan':
        return cmd_plan(a)
    if a.cmd == 'sequence':
        return cmd_sequence(a)
    if a.cmd == 'remake':
        return cmd_remake(a)
    if a.cmd == 'render':
        if not a.edl and not a.project:
            raise UserError('render: give EDL.json or --project DIR')
        return cmd_render(a)
    if a.cmd == 'status':
        return cmd_status(a)
    if a.cmd == 'frame':
        return cmd_frame(a)
    if a.cmd == 'qa':
        return qa(a.edl, a.video, a.out, as_json=a.json)
    if a.cmd == 'cmd':
        return cmd_cmd(a)
    if a.cmd == 'validate':
        _exists(a.edl, 'timeline')
        res = validate(a.edl, verbose=a.verbose)
        sys.exit(1 if res and res[0] else 0)
    if a.cmd == 'plan-sheet':
        if not a.edl and not a.project:
            raise UserError('plan-sheet: give EDL.json or --project DIR')
        return cmd_plan_sheet(a)
    if a.cmd == 'variant':
        return cmd_variant(a)
    if a.cmd == 'storyboard':
        return cmd_storyboard(a)
    if a.cmd == 'fill':
        return cmd_fill(a)
    if a.cmd == 'measure-ref':
        return cmd_measure_ref(a)
    if a.cmd == 'track':
        return cmd_track(a)
    if a.cmd == 'transcribe':
        return cmd_transcribe(a)
    if a.cmd == 'pack':
        return cmd_pack(a)
    if a.cmd == 'unpack':
        return cmd_unpack(a)
    if a.cmd == 'fonts':
        return cmd_fonts(a)
    if a.cmd == 'doctor':
        return cmd_doctor(a)
    overview()
    return None


def main(argv=None):
    global _JOB, _RAW_ARGV
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ['--job'] and len(argv) > 1:          # a background job started by spawn_job
        _JOB, argv = argv[1], argv[2:]
        _job_write(_JOB, stage='running', pid=os.getpid())
        code, res = 1, None
        try:
            res = _main(argv)
            code = 0
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
            raise
        finally:
            _job_write(_JOB, stage='done' if code == 0 else 'failed', exit=code, ended=time.time(),
                       **({'result': res} if isinstance(res, str) else {}))
        return res
    return _main(argv)


def _main(argv):
    global _RAW_ARGV
    _RAW_ARGV = list(argv)
    if not argv or argv[0] in ('-h', '--help', 'help'):
        if len(argv) > 1 and argv[0] == 'help':
            argv = [argv[1], '-h']
        else:
            overview()
            return None
    try:
        if argv[0] == 'voice':
            return cmd_voice(argv[1:])
        ap = build_parser()
        a = ap.parse_args(argv)
        if getattr(a, 'help', False) and not a.cmd:
            overview()
            return None
        return dispatch(a, ap)
    except UserError as e:
        warn(f'edit.py: error: {e}')
        if _JOB:
            _job_write(_JOB, error=str(e)[:400])
        sys.exit(2)
    except KeyboardInterrupt:
        warn('edit.py: interrupted')
        sys.exit(130)
    except Exception as e:
        if os.environ.get('ED_DEBUG'):
            raise
        tb = traceback.extract_tb(e.__traceback__)[-3:]
        where = ' <- '.join(f'{os.path.basename(f.filename)}:{f.lineno} {f.name}' for f in reversed(tb))
        warn(f'edit.py: {type(e).__name__}: {e}\n  at {where}\n  (ED_DEBUG=1 for the full traceback)')
        if _JOB:
            _job_write(_JOB, error=f'{type(e).__name__}: {e}'[:400])
        sys.exit(1)


if __name__ == '__main__':
    main()
