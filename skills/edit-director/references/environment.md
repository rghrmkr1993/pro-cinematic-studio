# Environment: sandbox, check, downloads, speed

## The claude.ai sandbox

- **ffmpeg 6** with libx264, aac, libass, zscale, loudnorm, ebur128. **Python**: numpy, scipy, opencv, onnxruntime,
  Pillow (with raqm), PyYAML, fontTools. No torch, librosa or whisper packages: music and speech analysis are the
  engine's own, models are ONNX.
- **Hardware**: 1–2 CPU cores, ~4–7 GB RAM, ~10 GB disk. **Files are wiped between sessions** →
  `references/storage.md`.
- **Network**: package installs are blocked. Model and font downloads come from GitHub releases (allowed in most
  setups). Video platforms and social networks are blocked — and their downloading is not supported anyway: the
  user sends files.

## Check at session start

```bash
python3 -I $ED/engine/edit.py doctor            # --offline skips the network check, --json for machines
```
One line per check: ffmpeg / ffprobe and their filters (x264, AAC, libass, zscale, loudness), Python libraries,
Pillow raqm (complex scripts), speech models, bundled fonts and models, the cache folder, CPU / RAM, GitHub
reachability. Exit code 1 = something the engine cannot work without is missing: say what does not work and offer a
workaround; never try to install packages.

## Downloads on demand (into `~/.cache/edit-studio/`, never into the skill folder)

| what | when | where |
|---|---|---|
| speech models (Whisper turbo ~560 MB, aligner ~290 MB, VAD) | the first transcription of a session | `asr/` (`$ED_VOICE_CACHE` overrides) |
| U²-Net person matte (176 MB) | the first fine person mask (`mask_flash`); without it the shipped PP-HumanSeg is used | `models/` |
| CJK font faces (OFL) | the first Chinese / Japanese / Korean character in a text layer (`edit.py fonts --text … --no-download` to avoid it) | `fonts/` (`$ED_FONT_CACHE`; `ED_NO_DOWNLOAD=1` disables all) |
| analysis caches (screen-recording boxes, overlays, reframe scans, sequence music and clip profiles, storyboard slates) | as you work | `video/`, `reframe/`, `sequence/`, `storyboard/` |
Projects keep their own analysis cache in `$PROJ/.ed_cache` (footage analysis of the planner, talk-part scans keyed
by the source window — a new `av_offset` or a moved cut point re-plans in seconds). The object detector used by
remakes is optional and not shipped; remakes work without it.

## Speed

Measured on 2 cores on a 4K-screen-recording + generated-shots composite (1 core: about twice as long). Use these
to tell the user how long a step takes.

| step | time |
|---|---|
| `edit.py track`, 1 min of music | a few seconds |
| transcription (turbo + word alignment) | ~0.5–0.7 × the speech length; first use + model download ~1–3 min; cached per file |
| planning on cached analysis (`plan`, `sequence`, `variant`, `fill`) | seconds to a minute; the first run analyses each clip once |
| draft preview 540×960 (the default) | ~9–13 frames/s → a 30 s edit in ~1.5 min; ~0.65 GB of memory |
| QA of a preview | ~30–45 s |
| a whole composite build (plan + draft + QA) | 2–5 min → always `--background` + `edit.py status` |
| `--full` preview (optical flow) | ~5–9 frames/s; the low end over speed ramps and other retimed shots (24 → 30 fps) |
| final 1080×1920 | ~2.5 frames/s → a 30 s edit in ~6 min, ~1.4 GB; always `--background` + `edit.py status` |

What makes renders slow: optical-flow interpolation (sources whose fps differs from the output, slow motion, ramps),
many segments over long sources. The engine already decodes each segment only at the size its crop needs (a 4K
source in a draft is read at roughly preview size) and tone-maps HDR on the way; you do not need proxies.
**Long jobs**: a foreground command that outlives the tool's time limit is killed (a ~200 s build is enough), so
anything that may take over ~1.5 minutes runs with `--background` (`plan`, `variant`, `sequence`, `remake`,
`storyboard`, `voice transcribe`, `render`) and is polled with `edit.py status $PROJ`. Check edits with `--frames
a:b`, still sheets and `edit.py frame`, not with full previews; keep the latest 1–2 previews and delete partial
renders.

## Input files

`ffprobe` every source before the plan lines: rotation, variable fps, HDR (handled by the engine), no audio track,
very long files (analyse only the named window), screen recordings (the content box and overlays are detected —
`references/scenario-composite.md`).

## Outside claude.ai (Claude Code, Cowork on your own computer)

Install by your organisation's rules: ffmpeg ≥ 6 with libx264, libass, freetype, zimg (zscale); Python ≥ 3.11 with
numpy, scipy, opencv-python, onnxruntime, Pillow (raqm for complex scripts), PyYAML, matplotlib, fontTools. No GPU
needed. `edit.py doctor` lists what is missing. Replace `/mnt/user-data/uploads` and `/mnt/user-data/outputs` with
your own folders.
