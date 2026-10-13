#!/usr/bin/env python3
"""Peek at source moments: labelled sheet of frames (picture area only) with a 10 % grid.

python3 -I tools_peek.py SRC OUT.jpg t1 t2 ... [--w 640] [--cols 3] [--box y0:y1]
Times as seconds or m:ss.s. Each tile shows the letterboxed picture area (auto-detected or --box)
with x-grid lines at every 10 % so a vertical crop centre can be picked.
"""
import sys, subprocess, argparse, numpy as np, cv2


def tsec(s):
    if ':' in s:
        m, x = s.split(':')
        return int(m) * 60 + float(x)
    return float(s)


def grab(src, t, w=1280, h=720):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', src, '-vframes', '1',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('times', nargs='+')
    ap.add_argument('--w', type=int, default=640); ap.add_argument('--cols', type=int, default=3)
    ap.add_argument('--box', default='90:630'); ap.add_argument('--gamma', type=float, default=0.7)
    a = ap.parse_args()
    y0, y1 = map(int, a.box.split(':'))
    lut = (np.clip((np.arange(256) / 255.0) ** a.gamma, 0, 1) * 255).astype(np.uint8)
    tiles = []
    for ts in a.times:
        t = tsec(ts)
        fr = lut[grab(a.src, t)[y0:y1]]
        h = int(round(a.w * fr.shape[0] / fr.shape[1]))
        im = cv2.resize(fr, (a.w, h), interpolation=cv2.INTER_AREA).copy()
        for k in range(1, 10):
            x = int(a.w * k / 10)
            cv2.line(im, (x, 0), (x, 6), (255, 255, 0), 1)
            cv2.line(im, (x, h - 7), (x, h - 1), (255, 255, 0), 1)
            cv2.putText(im, str(k), (x + 2, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 0), 1, cv2.LINE_AA)
        lab = np.zeros((16, a.w, 3), np.uint8)
        cv2.putText(lab, f'{ts}  ({t:.2f}s)', (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 1, cv2.LINE_AA)
        tiles.append(np.vstack([lab, im]))
    th = max(t.shape[0] for t in tiles)
    rows = []
    for i in range(0, len(tiles), a.cols):
        row = tiles[i:i + a.cols]
        row += [np.zeros_like(tiles[0])] * (a.cols - len(row))
        rows.append(np.hstack([np.pad(t, ((0, th - t.shape[0]), (0, 4), (0, 0))) for t in row]))
    cv2.imwrite(a.out, cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
