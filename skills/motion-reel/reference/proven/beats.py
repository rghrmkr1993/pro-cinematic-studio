"""python beats.py out/music.wav > beats.json
Measures bpm, beats, downbeats and onset hits. Uses librosa when importable, else a pure-numpy fallback."""
import sys, os, json
import numpy as np
try:
    import soundfile as sf
except Exception:
    sf = None
try:
    import librosa
except Exception:
    librosa = None


def load(path):
    if sf is not None:
        y, sr = sf.read(path, dtype="float32")
        return (y.mean(axis=1) if y.ndim > 1 else y), sr
    import wave
    w = wave.open(path)
    sr = w.getframerate()
    y = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return y, sr


def numpy_beats(y, sr, hop=512):
    n = len(y) // hop
    env = np.sqrt((y[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    flux = np.maximum(np.diff(env, prepend=env[0]), 0)
    thr = flux.mean() + flux.std()
    peaks = [i for i in range(1, n - 1) if flux[i] > thr and flux[i] >= flux[i - 1] and flux[i] > flux[i + 1]]
    hits = [round(i * hop / sr, 3) for i in peaks]
    ac = np.correlate(flux - flux.mean(), flux - flux.mean(), "full")[n - 1:]
    lo, hi = int(60 / 180 * sr / hop), int(60 / 70 * sr / hop)
    lag = lo + int(np.argmax(ac[lo:hi]))
    bpm = 60 * sr / hop / lag
    return bpm, hits


if os.environ.get('NO_LIBROSA'):
    librosa = None   # force the pure-numpy path
y, sr = load(sys.argv[1])
if librosa is not None:
    tempo, frames = librosa.beat.beat_track(y=y, sr=sr, units="frames")
    beats = librosa.frames_to_time(frames, sr=sr).round(3).tolist()
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    peaks = librosa.util.peak_pick(onset, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=10)
    hits = librosa.frames_to_time(peaks, sr=sr).round(3).tolist()
    bpm, engine = float(np.atleast_1d(tempo)[0]), "librosa " + librosa.__version__
else:
    bpm, hits = numpy_beats(y, sr)
    step = 60 / bpm
    beats = [round(i * step, 3) for i in range(int(len(y) / sr / step))]
    engine = "numpy-fallback"
json.dump({"engine": engine, "bpm": bpm, "beats": beats, "downbeats": beats[::4], "hits": hits}, sys.stdout, indent=1)
