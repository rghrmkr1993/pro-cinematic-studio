# Music: sourcing, track analysis and the grid

Music leads a music edit: tempo, beats and downbeats, accents, structure (intro / build / drop), the energy curve.

## Where the music comes from

- **The user's file** (wav, mp3, m4a, or a video with the music): the normal case. The user chooses the music and is
  responsible for the rights.
- **No links to platforms**: YouTube / TikTok / streaming downloads are not supported — ask for the file.
- **Generated music** (Higgsfield audio) is a paid option: describe it, give the price, wait for an explicit "yes"
  (the consent rules of edit-voice / edit-gen). Never on autopilot.
- **TikTok**: platform music can be picked in the publishing form (`references/publish.md`), but the edit will not
  adapt to it automatically.

## Analysis

```bash
python3 -I $ED/engine/edit.py track TRACK $PROJ/track.json --plot $PROJ/track.png
python3 -I $ED/engine/ed_audio.py analyze TRACK $PROJ/track.json --plot $PROJ/track.png --bpm-hint 140   # tempo known
```
The JSON is large — read only the fields you need:
`python3 -I -c "import json; d=json.load(open('$PROJ/track.json')); print({k: d[k] for k in ('bpm','tempo_conf','steady','downbeat_conf','drops','sections')})"`.

| field | what it is |
|---|---|
| `bpm`, `tempo_conf` | the tempo and the confidence in it |
| `steady`, `grid_resid_ms` | a steady tempo (electronic music) or a drifting one (live) |
| `beats`, `beat_strength` | beats (s) and their attack strength; "hits" = strong beats |
| `downbeats`, `downbeat_conf` | bar starts and the confidence |
| `bars`, `sections` | bars and sections with `energy` and a `label` (high / mid / low) |
| `drops` | drops with the loudness and low-end jumps |

`track.png`: onsets with beats (blue) and downbeats (red) on top, loudness with sections (orange, darker = more
energy) and drops (thick red) below.

## When not to trust it

- Low `tempo_conf` or a tempo outside 70–180 → a ×2 / ÷2 error is possible; check against the genre and the plot, ask
  the user or pass `--bpm`.
- Low `downbeat_conf` → the "one" may be off by a beat; rely on the drop and the section starts.
- `steady: false` → cut on the detected beats, not on an even grid.
- No clear drop (`jump_db` < 3): a genre plan takes the start of the most energetic section; a composite lands the
  switch on the biggest bass / loudness rise on a downbeat into music energetic enough for the edit and prints a note
  (`no clear drop in this track; the switch lands on the biggest energy jump at 0:42.0 (+3.1 dB in the low end).
  For a harder hit, pick another section or track.`). Tell the user and offer another section (`"in"` / `"drop"`,
  `--music-in` / `--drop-t`) or another track.

## The user's word wins

"The drop is at 1:05", "start from the second verse", "it's 140 BPM" beat the analysis. Record it in `project.json`
(`music.overrides`) and pass it on:

| wish | `edit.py plan` | sequence spec `music` |
|---|---|---|
| the track second at output 0 | `--music-in 42` | `"in": 42` |
| where the drop lands in the output | `--drop-at 8` (output second) | `"drop_at": {"part": "hype", "at": "start"}` (or seconds into the part) |
| where the drop is in the track | `--drop-t 65` | `"drop": 65` |
| the tempo | `--bpm 140` | — |
| length in bars | `--bars 8` | edit part `"bars": 8` |
In a composite the parts before the drop play the track's build under them (`music_db`, a swell into the edit part);
the drop and its sound package land on the edit part's first frame.

## Track window

- Track longer than the video: cut on bars — the drop where the genre (or the user) wants it, the start on a
  downbeat, the end at a phrase end or on a hit (else a 0.3–0.5 s fade-out).
- Track shorter: shorten the video, or repeat bars within a section (the seam on a downbeat; ask the user to listen).
- Several lengths (15 / 30 / 60 s) from one track: windows with the same drop, different lead-ins.

## The same track as in a reference

`edit.py remake … --music TRACK` aligns a clean track to the reference audio automatically (spectral-flux onset
envelopes, cross-correlation); no match → it starts at 0 with a warning, `--music-in S` sets it by hand. The
reference's rhythm then sits on the track; its sound accents fall into place when it is the same recording.
