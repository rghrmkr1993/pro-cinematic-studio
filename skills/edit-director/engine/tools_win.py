#!/usr/bin/env python3
"""Show source frames with the 9:16 crop window drawn: tools_win.py SRC OUT.jpg 't@cx,cy,z' ... [--box 0:90:1280:630]"""
import sys, argparse, subprocess, numpy as np, cv2


def tsec(s):
    if ':' in s:
        m, x = s.split(':')
        return int(m) * 60 + float(x)
    return float(s)


ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('specs', nargs='+')
ap.add_argument('--box', default='0:90:1280:630'); ap.add_argument('--w', type=int, default=640)
ap.add_argument('--cols', type=int, default=3); ap.add_argument('--gamma', type=float, default=0.75)
a = ap.parse_args()
x0, y0, x1, y1 = map(int, a.box.split(':'))
W, H = x1 - x0, y1 - y0
lut = (np.clip((np.arange(256) / 255.0) ** a.gamma, 0, 1) * 255).astype(np.uint8)
tiles = []
for sp in a.specs:
    t, _, c = sp.partition('@')
    cx, cy, z = (list(map(float, c.split(','))) + [0.5, 0.5, 1.0])[:3] if c else (0.5, 0.5, 1.0)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{tsec(t):.3f}', '-i', a.src, '-vframes', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(720, 1280, 3)[y0:y1, x0:x1]
    fr = lut[fr]
    hw = H / z; ww = hw * 9 / 16
    px = min(max(cx * W, ww / 2), W - ww / 2); py = min(max(cy * H, hw / 2), H - hw / 2)
    s = a.w / W
    im = cv2.resize(fr, (a.w, int(H * s)), interpolation=cv2.INTER_AREA).copy()
    dim = (im * 0.45).astype(np.uint8)
    X0, Y0, X1, Y1 = int((px - ww / 2) * s), int((py - hw / 2) * s), int((px + ww / 2) * s), int((py + hw / 2) * s)
    dim[Y0:Y1, X0:X1] = im[Y0:Y1, X0:X1]
    cv2.rectangle(dim, (X0, Y0), (X1 - 1, Y1 - 1), (255, 255, 0), 1)
    for k in range(1, 10):
        cv2.line(dim, (int(a.w * k / 10), 0), (int(a.w * k / 10), 5), (255, 255, 0), 1)
    lab = np.zeros((16, a.w, 3), np.uint8)
    cv2.putText(lab, sp, (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 1, cv2.LINE_AA)
    tiles.append(np.vstack([lab, dim]))
rows = []
for i in range(0, len(tiles), a.cols):
    r = tiles[i:i + a.cols]; r += [np.zeros_like(tiles[0])] * (a.cols - len(r))
    rows.append(np.hstack([np.pad(t, ((0, 0), (0, 4), (0, 0))) for t in r]))
cv2.imwrite(a.out, cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
