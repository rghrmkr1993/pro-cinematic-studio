#!/usr/bin/env python3
"""Validate genre cards (genres/<slug>.md): YAML front matter + required body sections.

Usage: python3 -I scripts/check_genre.py genres/epic.md [...]   (or the genres/ directory)
Checks: front matter keys; genre key is one of the 15; every move id exists in moves/index.json (moves or planned);
signature ⊆ union(hook, build, drop, outro); no id both allowed/used and forbidden; sfx ids exist; body has all sections.
Library root: the skill folder (parent of scripts/); if it has no moves/index.json — $EDIT_STUDIO_ROOT, then the folder
that holds the checked genres/.
"""
import sys, os, re, glob, json
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
GENRES = {s: s for s in ('viral', 'epic', 'drama', 'calm', 'product', 'phonk', 'sport', 'travel', 'fashion', 'fanedit',
                          'teaser', 'clips', 'explainer', 'ugc', 'motivation')}
SECTIONS = ['Goal and platform', 'Structure by seconds', 'Rhythm', 'Shot selection', 'Moves by part', 'SFX', 'Color',
            'Text', 'Quality checks']
KINDS = {'music', 'speech'}
CYR = re.compile('[\u0400-\u04ff]')     # Cyrillic block: cards are English, none may be left in a card
PARTS = ['hook', 'build', 'drop', 'outro']


def library_root(paths=()):
    for c in [ROOT, os.environ.get('EDIT_STUDIO_ROOT')] + [os.path.dirname(os.path.dirname(os.path.abspath(p)))
                                                            for p in paths]:
        if c and os.path.exists(os.path.join(c, 'moves', 'index.json')):
            return c
    sys.exit('moves/index.json not found next to scripts/, in $EDIT_STUDIO_ROOT or next to the genres/ folder')


def known_ids(root=None):
    idx = json.load(open(os.path.join(root or ROOT, 'moves', 'index.json'), encoding='utf-8'))
    return {m['id'] for m in idx['moves']} | {m['id'] for m in idx.get('planned', [])}


def check(path, ids):
    errs = []
    txt = open(path, encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', txt, re.S)
    if not m:
        return ['no YAML front matter']
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return [f'YAML error: {e}']
    body = m.group(2)
    for k in ('genre', 'slug', 'kind', 'platforms', 'format', 'structure', 'rhythm', 'moves', 'sfx'):
        if k not in fm:
            errs.append(f'missing {k}')
    g = fm.get('genre')
    if g not in GENRES:
        errs.append(f'unknown genre {g!r}')
    elif fm.get('slug') != GENRES[g] or os.path.basename(path) != GENRES[g] + '.md':
        errs.append(f'slug/file must be {GENRES[g]}')
    mv = fm.get('moves') or {}
    used = set()
    for p in PARTS:
        lst = mv.get(p) or []
        if not lst:
            errs.append(f'moves.{p} empty')
        used |= set(lst)
    for k in PARTS + ['signature', 'allowed', 'forbidden']:
        for i in mv.get(k) or []:
            if i not in ids:
                errs.append(f'moves.{k}: unknown id {i}')
    sig = set(mv.get('signature') or [])
    if not sig:
        errs.append('moves.signature empty')
    if sig - used:
        errs.append(f'signature not used in any part: {sorted(sig - used)}')
    forb = set(mv.get('forbidden') or [])
    clash = forb & (used | set(mv.get('allowed') or []))
    if clash:
        errs.append(f'ids both used/allowed and forbidden: {sorted(clash)}')
    sfx = fm.get('sfx') or {}
    for p, lst in sfx.items():
        for i in lst or []:
            if i not in ids:
                errs.append(f'sfx.{p}: unknown id {i}')
            if i in forb:
                errs.append(f'sfx.{p}: {i} is forbidden')
    for s in SECTIONS:
        if not re.search(r'^##\s+' + re.escape(s) + r'\s*$', body, re.M):
            errs.append(f'body section missing: {s}')
    if fm.get('kind') not in KINDS:
        errs.append(f"kind must be music|speech, got {fm.get('kind')!r}")
    for ln, line in enumerate(txt.splitlines(), 1):
        if CYR.search(line):
            errs.append(f'Cyrillic left on line {ln}: {line.strip()[:60]}')
            break
    if re.search(r'https?://|www\.', txt, re.I):
        errs.append('contains URL / source reference')
    return errs


def main():
    if not sys.argv[1:] or any(a in ('-h', '--help') for a in sys.argv[1:]):
        print(__doc__.strip())
        sys.exit(0 if sys.argv[1:] else 2)
    paths = []
    for a in sys.argv[1:]:
        paths += sorted(p for p in glob.glob(os.path.join(a, '*.md')) if not os.path.basename(p).startswith('_')) \
            if os.path.isdir(a) else [a]
    ids = known_ids(library_root(paths))
    bad = 0
    for p in paths:
        e = check(p, ids)
        print(('OK ' if not e else 'FAIL ') + p)
        for x in e:
            print('   E', x)
        bad += bool(e)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
