# Third-party notices

## openai-whisper (MIT)

`engine/ed_voice.py` re-implements in numpy parts of openai-whisper: log-mel features (mel filter bank),
temperature-fallback decoding rules, word timestamps (alignment heads, median filter, DTW) and token splitting.

Copyright (c) 2022 OpenAI

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.

## Models, fonts and downloaded assets

Shipped models (YuNet face detection — MIT; PP-HumanSeg person segmentation — Apache-2.0) and the assets downloaded
on demand into `~/.cache/edit-studio/` (U²-Net human segmentation — Apache-2.0; Noto Sans CJK — SIL OFL 1.1; speech
models — MIT / Apache-2.0) are listed with sources and licences in `engine/models/LICENSES.md`. Bundled fonts: SIL
Open Font License 1.1, the licence text of each family in `engine/assets/fonts/<family>_OFL.txt`.
