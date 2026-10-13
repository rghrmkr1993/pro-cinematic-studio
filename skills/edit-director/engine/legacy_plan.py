#!/usr/bin/env python3
"""Legacy remake planner (scenario 1, timeline v1 format with `clips`), moved out of ed_plan.py when ed_plan became
the genre planner. Still used by edit.py through ed_plan.plan_remake (re-exported).

python3 -I legacy_plan.py remake --ref <reference.json> --src <source.json> [--track <track.mp3>] --out <timeline.json>
                             [--canvas 1080x1920] [--fps 30] [--max-zoom 2.6]
"""
import os, sys, json, math, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ed_audio as A      # noqa: E402
import ed_reframe as R    # noqa: E402

SCALE_RANK = {'extreme-close': 4, 'close': 3, 'medium': 2, 'wide': 1, 'wide/no-face': 0}


def _rank(v):
    v = np.asarray(v, float)
    if len(v) <= 1:
        return np.full(len(v), 0.5)
    order = v.argsort().argsort()
    return order / (len(v) - 1)


def map_timeline(ref, track_path=None):
    """Output slot times (seconds) and the audio segment. Same music -> exact; different music -> beat-relative."""
    shots = ref['shots']
    ref_dur = shots[-1]['t1']
    aud = ref.get('audio')
    if not track_path:
        return [(s['t0'], s['t1']) for s in shots], dict(src=ref['path'], start=0.0, dur=ref_dur), dict(mode='reference-audio')
    al = A.align(ref['path'], track_path)
    if al['same_music'] and abs(al['stretch'] - 1.0) < 0.01:
        off = al['offset_s']
        return [(s['t0'], s['t1']) for s in shots], dict(src=track_path, start=max(0.0, off), dur=ref_dur), dict(mode='same-music', **al)
    # different (or re-timed) music: keep the reference's rhythm in beats, place it on the track's grid
    tr = A.analyze(track_path)
    tb = np.array(tr['beats'])
    period_ref = 60.0 / aud['bpm'] if aud else 0.5
    period_tr = 60.0 / tr['bpm']
    if al['same_music']:
        start = al['offset_s']                            # same song, other speed: start where it matches
    else:
        # align the reference's first drop (or its energy peak) with the track's first drop, else first strong downbeat
        ref_drop = aud['drops'][0]['t'] if aud and aud.get('drops') else None
        if ref_drop is not None and tr['drops']:
            start = tr['drops'][0]['t'] - ref_drop / period_ref * period_tr
        else:
            hi = [s for s in tr['sections'] if s.get('label') in ('high', 'mid')]
            start = hi[0]['t0'] if hi else (tr['downbeats'][0] if tr['downbeats'] else 0.0)
        start = max(0.0, start)
    # snap start to the nearest downbeat of the track
    if tr['downbeats']:
        db = np.array(tr['downbeats'])
        start = float(db[np.argmin(np.abs(db - start))])
    times = []
    for s in shots:
        b0 = s['t0'] / period_ref
        b1 = s['t1'] / period_ref
        times.append((b0 * period_tr, b1 * period_tr))
    # snap internal boundaries to the track's beats (exact grid)
    snapped = []
    for t0, t1 in times:
        snapped.append([_snap(start + t0, tb) - start, _snap(start + t1, tb) - start])
    dur = snapped[-1][1]
    return [tuple(x) for x in snapped], dict(src=track_path, start=start, dur=dur), dict(mode='beat-mapped', **al, track_bpm=tr['bpm'])


def _snap(t, beats, tol=0.09):
    if len(beats) == 0:
        return t
    # allow half-beat positions
    period = np.median(np.diff(beats)) if len(beats) > 1 else 0.5
    grid = np.sort(np.concatenate([beats, beats[:-1] + period / 2]))
    j = int(np.argmin(np.abs(grid - t)))
    return float(grid[j]) if abs(grid[j] - t) < tol else t


def candidate_windows(src, dur, step=0.25, margin=0.15):
    ser = src['series']
    t = np.array(ser['t'])
    mot = np.array(ser['motion'])
    shp = np.array(ser['sharp'])
    lum = np.array(ser['luma'])
    faces = ser['faces']
    out = []
    for sh in src['shots']:
        if sh['dur'] < dur + 2 * margin:
            continue
        w0 = sh['t0'] + margin
        while w0 + dur <= sh['t1'] - margin + 1e-6:
            sel = (t >= w0) & (t < w0 + dur)
            if sel.sum() == 0:
                w0 += step
                continue
            idx = np.nonzero(sel)[0]
            fh = [faces[i][0][2] for i in idx if faces[i]]
            out.append(dict(shot=sh['i'], t0=round(w0, 3), dur=dur, motion=float(mot[idx].mean()),
                            motion_peak_t=float(t[idx[np.argmax(mot[idx])]] - w0), sharp=float(np.median(shp[idx])),
                            luma=float(lum[idx].mean()), face_share=float(np.mean([bool(faces[i]) for i in idx])),
                            face_h=float(np.median(fh)) if fh else 0.0))
            w0 += step
    return out


def plan_remake(ref, src, track=None, canvas=(1080, 1920), fps=30, max_zoom=2.6):
    times, audio, mapping = map_timeline(ref, track)
    shots = ref['shots']
    n = len(shots)
    # slot features
    ref_mot = _rank([s['motion'].get('motion_energy', 0) for s in shots])
    slot_energy = np.zeros(n)
    if mapping['mode'] != 'reference-audio' and track:
        tr = A.analyze(track)
    else:
        tr = ref.get('audio')
    if tr and tr.get('bars'):
        for k, (t0, t1) in enumerate(times):
            ta = audio['start'] + (t0 + t1) / 2
            b = [x for x in tr['bars'] if x['t0'] <= ta < x['t1']]
            slot_energy[k] = b[0]['rms_db'] if b else -30
        slot_energy = _rank(slot_energy)
    importance = 0.6 * slot_energy + 0.4 * ref_mot
    order = sorted(range(n), key=lambda k: -importance[k])
    used_shots = {}
    chosen = [None] * n
    all_windows = {}
    for k in order:
        t0, t1 = times[k]
        dur = round(t1 - t0, 3)
        s = shots[k]
        cut = s.get('cut_in', {}).get('type', 'cut')
        if cut in ('punch_in', 'punch_out') and k > 0:
            continue                      # filled after its predecessor (continuation of the same footage)
        key = round(dur, 2)
        if key not in all_windows:
            all_windows[key] = candidate_windows(src, dur)
        cands = all_windows[key]
        if not cands:
            continue
        wm = _rank([c['motion'] for c in cands])
        ws = _rank([c['sharp'] for c in cands])
        best, best_sc = None, -1e9
        want_scale = SCALE_RANK.get(s['scale'], 1)
        for c, rm, rs in zip(cands, wm, ws):
            sc = 0.0
            sc -= 1.2 * abs(rm - ref_mot[k])                 # motion character like the reference shot
            sc += 0.6 * rs                                    # sharpness
            sc += 0.5 * importance[k] * (rm + rs) / 2          # best footage to the most important slots
            if c['luma'] < 35 or c['luma'] > 225:
                sc -= 0.6
            have_scale = 3 if c['face_h'] > 0.18 else (2 if c['face_h'] > 0.08 else (1 if c['face_share'] > 0 else 0))
            sc -= 0.25 * abs(have_scale - want_scale)
            # never put the same source shot next to itself (except punch continuations handled later)
            for nb in (k - 1, k + 1):
                if 0 <= nb < n and chosen[nb] is not None and chosen[nb]['shot'] == c['shot']:
                    sc -= 3.0
            if c['shot'] in used_shots:
                sc -= 1.5 * used_shots[c['shot']]
                # never overlap a range already used
                for (u0, u1) in [(x['src_in'], x['src_in'] + x['dur']) for x in chosen if x and x['shot'] == c['shot']]:
                    if c['t0'] < u1 + 0.5 and c['t0'] + c['dur'] > u0 - 0.5:
                        sc -= 100
            if sc > best_sc:
                best, best_sc = c, sc
        chosen[k] = dict(shot=best['shot'], src_in=best['t0'], dur=dur, score=round(best_sc, 3), motion=round(best['motion'], 2))
        used_shots[best['shot']] = used_shots.get(best['shot'], 0) + 1
    # punch-in continuations and neighbours from the same shot
    for k in range(n):
        if chosen[k] is None and k > 0 and chosen[k - 1] is not None:
            p = chosen[k - 1]
            dur = round(times[k][1] - times[k][0], 3)
            chosen[k] = dict(shot=p['shot'], src_in=round(p['src_in'] + p['dur'], 3), dur=dur, score=0.0, motion=p['motion'],
                             continuation=True)
    # build clips
    clips = []
    for k in range(n):
        s = shots[k]
        c = chosen[k]
        if c is None:
            continue
        t0, t1 = times[k]
        rf = R.crop_path(src['path'], c['src_in'], c['dur'])
        rf['zoom'] = 1.0
        cut = s.get('cut_in', {}).get('type', 'cut')
        cut_in = {'id': 'cut'}
        if cut == 'flash':
            cut_in = {'id': 'trans.flash', 'frames': 3}
        elif cut == 'dip_black':
            cut_in = {'id': 'trans.fade', 'frames': 6}
        elif cut in ('punch_in', 'punch_out') and clips:
            prev = clips[-1]
            scale = s['cut_in'].get('scale', 1.3 if cut == 'punch_in' else 1 / 1.3)
            rf['zoom'] = float(np.clip(prev['reframe']['zoom'] * scale, 1.0, max_zoom))
            rf['keys'] = prev['reframe']['keys'][-1:]
            cut_in = {'id': 'zoom.punch', 'scale': round(scale, 3)}
        moves = []
        for e in s['motion'].get('events', []):
            if not e['type'].startswith('ZOOM') or e.get('conf', 'ok') != 'ok':
                continue
            fa, fb = e['frames']
            mt0 = (fa / ref['fps'])
            mt1 = (fb / ref['fps'])
            fac = e['factor']
            if fac > 1:
                fac = min(fac, max_zoom / rf['zoom'])
            ease = 'inOutCubic' if 'S-curve' in e['ease'] else ('outCubic' if 'ease-out' in e['ease'] else ('inCubic' if 'ease-in' in e['ease'] else 'linear'))
            kind = 'zoom.crash' if (fac > 1.8 and (mt1 - mt0) < 0.8) else ('zoom.in' if fac > 1 else 'zoom.out')
            if fac < 1:
                rf['zoom'] = max(rf['zoom'], min(max_zoom, 1 / fac))      # start tight so we can pull out
                moves.append(dict(id='zoom.out', t0=round(mt0, 3), t1=round(mt1, 3), scale=[1.0, fac], ease=ease))
            else:
                moves.append(dict(id=kind, t0=round(mt0, 3), t1=round(mt1, 3), scale=[1.0, round(fac, 3)], ease=ease, blur=kind == 'zoom.crash'))
        sh = s['motion'].get('shake', {})
        if sh.get('jitter_pct', 0) > 1.2:
            moves.append(dict(id='shake.beat', times=[0.0], amp=min(0.03, sh['jitter_pct'] / 100), decay=8, freq=8.0, rot=0.6))
        clips.append(dict(n=len(clips) + 1, src=src['path'], src_in=c['src_in'], t0=round(t0, 4), t1=round(t1, 4), speed=1.0,
                          reframe=rf, moves=moves, cut_in=cut_in,
                          slot=dict(ref_shot=s['i'], ref_scale=s['scale'], beat=s.get('beat'), importance=round(float(importance[k]), 2)),
                          pick=dict(shot=c['shot'], score=c['score'], motion=c['motion'], continuation=c.get('continuation', False))))
    tl = dict(version=1, kind='remake', canvas=dict(w=canvas[0], h=canvas[1], fps=fps), audio=dict(audio, fade_out=0.25, loudnorm=-14),
              clips=clips, mapping=mapping, reference=ref['path'], source=src['path'])
    return tl


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    r = sub.add_parser('remake')
    r.add_argument('--ref', required=True)
    r.add_argument('--src', required=True)
    r.add_argument('--track')
    r.add_argument('--out', required=True)
    r.add_argument('--canvas', default='1080x1920')
    r.add_argument('--fps', type=int, default=30)
    r.add_argument('--max-zoom', type=float, default=2.6)
    a = ap.parse_args()
    ref = json.load(open(a.ref))
    src = json.load(open(a.src))
    w, h = map(int, a.canvas.split('x'))
    tl = plan_remake(ref, src, a.track, (w, h), a.fps, a.max_zoom)
    json.dump(tl, open(a.out, 'w'), indent=1)
    print('clips', len(tl['clips']), 'mapping', tl['mapping']['mode'], 'audio', tl['audio'])
    for c in tl['clips']:
        print(f"#{c['n']:2d} {c['t0']:6.2f}-{c['t1']:6.2f} src {c['src_in']:7.2f} shot {c['pick']['shot']:3d} cut {c['cut_in']['id']:12s} moves {[m['id'] for m in c['moves']]} subj {c['reframe']['subject']}")


if __name__ == '__main__':
    main()
