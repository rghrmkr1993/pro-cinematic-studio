#!/usr/bin/env python3
"""Search the move library without loading every card (reads moves/index.json and the genre card headers).

  find_move.py QUERY...                          moves by id / alias / description
  find_move.py --family glitch                   a family (id prefix) + related moves by name and aliases
  find_move.py QUERY --genre epic [--part drop]  + the move's position in the genre; --part ranks for that part of the video
  find_move.py --genre phonk                     the genre's move plan: parts, signature, allowed, forbidden, SFX, looks
  find_move.py --show zoom.crash trans.whip [--fields params,engine,when]   selected fields of the cards

Filters: --status code,hybrid  --group transition  --level B  --limit 20  --with-forbidden
Library root: the skill folder (parent of scripts/), or --root DIR, or $EDIT_STUDIO_ROOT.
Run: python3 -I find_move.py ...
"""
import argparse
import json
import os
import re
import sys

import yaml

PARTS = ['hook', 'build', 'drop', 'outro']
DEFAULT_FIELDS = ['what', 'status', 'fallback', 'params', 'when', 'avoid', 'sfx', 'engine', 'commands', 'related']
# query words that name a move group: optional in a query, they only lift the moves of their group (singular forms;
# a trailing "s" is dropped before the lookup)
GROUP_WORDS = {'camera': 'camera', 'angle': 'angle', 'editing': 'editing', 'cut': 'editing', 'transition': 'transition',
               'time': 'time', 'speed': 'time', 'effect': 'effect', 'fx': 'effect', 'optic': 'optics', 'optics': 'optics',
               'aesthetic': 'aesthetics', 'aesthetics': 'aesthetics', 'look': 'aesthetics', 'graphic': 'graphics',
               'graphics': 'graphics', 'text': 'graphics', 'title': 'graphics', 'sound': 'sound', 'sfx': 'sound',
               'audio': 'sound'}
# genre synonyms (prefix of the query -> genre slug)
GENRE_SYNONYMS = {'epic': 'epic', 'cinematic': 'epic', 'drama': 'drama', 'chill': 'calm', 'calm': 'calm',
                  'relax': 'calm', 'product': 'product', 'travel': 'travel', 'trip': 'travel', 'lifestyle': 'travel',
                  'beauty': 'fashion', 'fashion': 'fashion', 'fan': 'fanedit', 'anime': 'fanedit', 'teaser': 'teaser',
                  'trailer': 'teaser', 'announce': 'teaser', 'clip': 'clips', 'cut-down': 'clips', 'cutdown': 'clips',
                  'podcast': 'clips', 'interview': 'clips', 'highlight': 'sport', 'sport': 'sport',
                  'tutorial': 'explainer', 'educational': 'explainer', 'explain': 'explainer', 'ugc': 'ugc',
                  'motivat': 'motivation', 'viral': 'viral', 'trend': 'viral', 'velocity': 'phonk', 'phonk': 'phonk'}
def norm(s):
    s = str(s).lower()
    return re.sub(r'[^\w.\- ]+', ' ', s).strip()


def gkey(name):
    """Genre key: the slug."""
    return norm(name)


def group_of(name):
    """Move group (English group name)."""
    return norm(name)


def stem(t):
    """Rough stem so that word forms match: "dissolves" / "dissolving" -> "dissolv"."""
    for suf in ('ing', 'es', 'ed', 's'):
        if t.endswith(suf) and len(t) - len(suf) >= 4 and not t.endswith('ss'):
            return t[:len(t) - len(suf)]
    return t


def find_root(arg):
    cands = [arg, os.environ.get('EDIT_STUDIO_ROOT'),
             os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]
    for c in cands:
        if c and os.path.exists(os.path.join(c, 'moves', 'index.json')):
            return c
    sys.exit('moves/index.json not found — pass --root (the folder that holds moves/ and genres/)')


def load_genres(root):
    out = {}
    gdir = os.path.join(root, 'genres')
    if not os.path.isdir(gdir):
        return out
    for fn in sorted(os.listdir(gdir)):
        if not fn.endswith('.md') or fn.startswith('_'):
            continue
        txt = open(os.path.join(gdir, fn), encoding='utf-8').read()
        m = re.match(r'^---\n(.*?)\n---\n', txt, re.S)
        if not m:
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        if fm.get('genre'):
            fm['_file'] = os.path.join('genres', fn)
            out[gkey(fm.get('slug') or fm['genre'])] = fm
    return out


def resolve_genre(name, genres):
    n = gkey(name)                          # slug
    for key, fm in genres.items():
        if n in (key, norm(fm.get('slug', '')), gkey(fm.get('genre', ''))):
            return key
    for syn, key in GENRE_SYNONYMS.items():  # "cinematic" -> epic, "podcast" -> clips
        if n.startswith(syn) and key in genres:
            return key
    for key, fm in genres.items():          # prefix: "dram" -> drama
        if key.startswith(n) or norm(fm.get('slug', '')).startswith(n):
            return key
    sys.exit(f'genre {name!r} not found; available: ' + ', '.join(sorted(genres)))


def genre_position(mid, fm):
    """Position of the move by the genre card (the source of truth for the genre)."""
    mv = fm.get('moves') or {}
    pos = [p for p in PARTS if mid in (mv.get(p) or [])]
    if mid in (mv.get('signature') or []):
        pos.append('signature')
    if mid in (mv.get('allowed') or []):
        pos.append('allowed')
    sfx = fm.get('sfx') or {}
    for p in PARTS:
        if mid in (sfx.get(p) or []):
            pos.append(f'sfx:{p}')
    if mid in (fm.get('looks') or []):
        pos.append('look')
    if mid in (mv.get('forbidden') or []):
        pos = ['FORBIDDEN'] + pos
    return pos


def card_position(m, key):
    if key in [gkey(x) for x in m.get('banned', [])]:
        return 'forbidden by the move card'
    if key in [gkey(x) for x in m.get('signature', [])]:
        return 'signature by the move card'
    if key in [gkey(x) for x in m.get('allowed', [])]:
        return 'allowed by the move card'
    return ''


def group_word(t):
    for w in (t, t[:-1] if t.endswith('s') else None):
        if w and w in GROUP_WORDS:
            return GROUP_WORDS[w]
    return None


def score(m, tokens, phrase, require_all=True):
    """Match weight. Group words ("transition", "effect") are not required, they only lift the moves of their group."""
    mid = norm(m['id'])
    name = mid.split('.', 1)[-1]
    aliases = [norm(a) for a in m.get('aliases', [])]
    what = norm(m.get('what', ''))
    total, hits = 0, 0
    if phrase and (phrase in aliases or phrase.replace(' ', '_') in (mid, name)):
        total += 150
    content = [t for t in tokens if not group_word(t)] or tokens
    for t in tokens:
        g = group_word(t)
        if g and t not in content:
            total += 20 if group_of(m['group']) == g else 0
            continue
        st = stem(t)
        s = 0
        if t in (mid, name):
            s = 100
        elif any(a == t for a in aliases):
            s = 80
        elif t in mid:
            s = 40
        elif any(a.startswith(st) for a in aliases):
            s = 50
        elif any(st in a for a in aliases):
            s = 30
        elif st in what:
            s = 10
        if s:
            hits += 1
        elif require_all:
            return 0
        total += s
    return total if hits else 0


def line(m, extra=''):
    what = m.get('what', '')
    what = what if len(what) <= 120 else what[:117] + '…'
    al = ', '.join(str(a) for a in m.get('aliases', [])[:3])
    tag = f"{m['status']}·{m['level']}"
    return f"{m['id']:<26} {tag:<13} {extra:<28} {what} | {al}"


def show_cards(root, ids, fields):
    for mid in ids:
        p = os.path.join(root, 'moves', f'{mid}.yaml')
        c = None
        if os.path.exists(p):
            c = yaml.safe_load(open(p, encoding='utf-8'))
        else:                                   # packaged skill: one multi-document file per family
            p = os.path.join(root, 'moves', mid.split('.')[0] + '.yaml')
            if os.path.exists(p):
                c = next((d for d in yaml.safe_load_all(open(p, encoding='utf-8'))
                          if isinstance(d, dict) and d.get('id') == mid), None)
        if c is None:
            print(f'# {mid}: no card')
            continue
        sel = {k: c[k] for k in fields if k in c}
        print(f'# {mid}  ({p})')
        print(yaml.safe_dump(sel, allow_unicode=True, sort_keys=False, width=110).rstrip())
        print()


def genre_plan(key, fm):
    kind = fm.get('kind')
    name = '' if gkey(fm.get('genre', key)) == key else f" ({fm.get('genre')})"
    print(f"# {key}{name} — {kind}, format {fm.get('format')}  [{fm['_file']}]")
    for s in fm.get('structure') or []:
        print(f"  {s.get('part'):<6} {s.get('t'):<22} {s.get('goal')}")
    r = fm.get('rhythm') or {}
    print(f"  rhythm: shot lengths {r.get('shot_len_s')}; on the beat ≥ {r.get('on_beat_share')}; "
          f"on words ≥ {r.get('on_word_share')}; shot ≤ {r.get('max_shot_s')} s")
    mv = fm.get('moves') or {}
    for k in PARTS + ['signature', 'allowed', 'forbidden']:
        print(f"  {k:<9}: {', '.join(mv.get(k) or [])}")
    print(f"  sfx      : {fm.get('sfx')}")
    print(f"  looks    : {', '.join(fm.get('looks') or [])}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('query', nargs='*')
    ap.add_argument('--root')
    ap.add_argument('--family')
    ap.add_argument('--genre')
    ap.add_argument('--part', choices=PARTS)
    ap.add_argument('--status')
    ap.add_argument('--group')
    ap.add_argument('--level')
    ap.add_argument('--limit', type=int, default=20)
    ap.add_argument('--with-forbidden', action='store_true')
    ap.add_argument('--show', nargs='+', metavar='ID')
    ap.add_argument('--fields', default=','.join(DEFAULT_FIELDS))
    a = ap.parse_args()

    root = find_root(a.root)
    if a.show:
        show_cards(root, a.show, [f.strip() for f in a.fields.split(',') if f.strip()])
        return
    moves = json.load(open(os.path.join(root, 'moves', 'index.json'), encoding='utf-8'))['moves']
    genres = load_genres(root)
    key = resolve_genre(a.genre, genres) if a.genre else None
    gfm = genres.get(key) if key else None
    if key and not a.query and not a.family and not a.part and not (a.status or a.group or a.level):
        genre_plan(key, gfm)
        return

    tokens = [t for t in norm(' '.join(a.query)).split() if t]
    rows, hidden = collect(moves, tokens, a, key, gfm, require_all=True)
    if not rows and not hidden and len(tokens) > 1:
        rows, hidden = collect(moves, tokens, a, key, gfm, require_all=False)
        if rows:
            print('# no move matches all the words — showing matches for single words')
    rows.sort(key=lambda r: (-r[0], r[1]['id']))
    if hidden:
        hidden.sort(key=lambda h: -h[0])
        print(f'# hidden as forbidden in genre "{key}": ' + ', '.join(h[1] for h in hidden[:6]) +
              ' — show them: --with-forbidden; place one only if the user insists')
    if not rows:
        if not hidden:
            print('nothing found; try a synonym, --family, or drop the filters')
        return
    if gfm and a.part and not any(set(r[3]) & {a.part, 'allowed', 'signature'} for r in rows):
        print(f'# genre "{key}" plans none of the matches for {a.part} — the closest are below; '
              'ask the user or suggest a move from that part of the genre')
    for s, m, extra, _pos in rows[:a.limit]:
        print(line(m, extra))
    if len(rows) > a.limit:
        print(f'… {len(rows) - a.limit} more; narrow the query or raise --limit')


def collect(moves, tokens, a, key, gfm, require_all):
    phrase = ' '.join(tokens)
    fam = norm(a.family) if a.family else None
    rows, hidden = [], []
    for m in moves:
        if a.status and m['status'] not in a.status.split(','):
            continue
        if a.group and group_of(m['group']) != group_of(a.group):
            continue
        if a.level and m['level'] != a.level.upper():
            continue
        s = 0
        if fam:
            if norm(m['family']) == fam or norm(m['id']).startswith(fam + '.'):
                s += 200
            elif fam in norm(m['id']) or any(fam in norm(x) for x in m.get('aliases', [])):
                s += 60                                   # related: the name or an alias contains the word
            else:
                continue
        if tokens:
            q = score(m, tokens, phrase, require_all)
            if q == 0:
                continue
            s += q
        if not fam and not tokens:
            s = 1
        extra, pos = '', []
        if gfm:
            pos = genre_position(m['id'], gfm)
            by_card = card_position(m, key)
            if ('FORBIDDEN' in pos or (not pos and by_card.startswith('forbidden'))) and not a.with_forbidden:
                hidden.append((s, m['id']))
                continue
            if a.part:
                if a.part in pos:
                    s += 300
                elif 'allowed' in pos or 'signature' in pos:
                    s += 150
            extra = ','.join(pos) if pos else (by_card or 'not mentioned in the genre')
        rows.append((s, m, extra, pos))
    return rows, hidden


if __name__ == '__main__':
    main()
