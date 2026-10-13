# Models and downloaded assets: sources and licences

All models and fonts the engine uses are permissively licensed. Two small models ship with the skill; everything
else is downloaded on first use into `~/.cache/edit-studio/` (verified, never written into the skill folder) or is
optional.

## Shipped in `engine/models/`

| file | used by | source | licence | copyright |
|---|---|---|---|---|
| `face_detection_yunet_2023mar.onnx` (0.2 MB) | `ed_video.faces`: faces + 5 landmarks for framing, speaker crops, QA | OpenCV Zoo, `models/face_detection_yunet` (github.com/opencv/opencv_zoo) | MIT | Shiqi Yu and contributors |
| `human_segmentation_pphumanseg_2023mar.onnx` (6.2 MB) | `ed_video.person_mask`: person masks (subject regions, text behind the subject, the default matte) | OpenCV Zoo, `models/human_segmentation_pphumanseg` (PP-HumanSeg from PaddleSeg) | Apache-2.0 | PaddlePaddle Authors |

## Downloaded on demand (into `~/.cache/edit-studio/`)

| asset | used by | source | licence |
|---|---|---|---|
| U²-Net human segmentation, `u2net_human_seg.onnx` (176 MB, sha256 `01eb6a29a5c4d8edb30b56adad9bb3a2a0535338e480724a213e0acfd2d1c73c`) → `models/` | `ed_video.person_mask_hq` (fine mattes, op `mask_flash`); without it PP-HumanSeg is used | the rembg project's release: github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx | Apache-2.0 (U²-Net weights, as recorded in `ed_video`) |
| Noto Sans CJK (Simplified / Traditional Chinese, Hong Kong, Japanese, Korean subsets; Regular / Bold / Black) → `fonts/` | `ed_text`: the first CJK character in a text layer; archives and faces checked against pinned sha256 (`ed_text.CJK_FONTS`); the OFL text is kept next to the faces | github.com/notofonts/noto-cjk/releases (Sans2.004) | SIL Open Font License 1.1 |
| Whisper large-v3-turbo / small / base / tiny, int8 ONNX → `asr/` | `ed_voice.transcribe` | github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/ (sherpa-onnx-whisper-*) | weights: MIT (OpenAI); ONNX export: Apache-2.0 (k2-fsa/sherpa-onnx) |
| Omnilingual ASR CTC 300M, int8 ONNX → `asr/` | `ed_voice` word alignment and `model='omni'` | same release: sherpa-onnx-omnilingual-asr-1600-languages-300M-ctc-int8-2025-11-12 | Apache-2.0 (Meta Platforms, Inc. and affiliates) |
| Silero VAD, `silero_vad.onnx` (0.6 MB) → `asr/` | `ed_voice` speech regions | same release: silero_vad.onnx | MIT (Silero Team) |

`ED_NO_DOWNLOAD=1` disables the font downloads; `edit.py doctor` reports what is installed.

## Optional, not shipped

| model | used by | without it |
|---|---|---|
| NanoDet-Plus object detection, `object_detection_nanodet_2022nov.onnx` (OpenCV Zoo, Apache-2.0) | `ed_remake`: object types in slot descriptors, when the file is present in `engine/models/` or the user cache | remakes fall back to faces, person masks and image features |

## Fonts and sounds

Bundled fonts: `engine/assets/fonts/*` — SIL Open Font License 1.1, each family's licence text next to it
(`<family>_OFL.txt`). Sound effects are synthesized by code (`ed_sfx`) or taken from the user's own files; no sound
files are included.
