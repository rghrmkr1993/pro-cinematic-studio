# Storing projects between sessions

Sandbox files are wiped between sessions: footage, renders and analysis are gone. The project is saved "as code": a
small archive from which everything can be rebuilt.

## Project layout

```
$PROJ/                       # /home/claude/projects/<name> — the same name in every session
  project.json               # passport: scenario, brief, style, mode, canvas, fps, overrides, sources, track
  notes.md                   # the user's requests and what was done (read it first in a new session)
  media/                     # links to the sources: media/clip1.mp4 -> /mnt/user-data/uploads/clip1.mp4
  spec_vN.json               # composite specs (edit.py sequence)
  edl_v1.json … edl_vN.json  # every version (older projects: timeline_vN.json)
  plan_vN.jpg  preview_vN.mp4  final_vN.mp4  qa_vN/
  track.json  track.png      # music analysis
  voice/words.json           # transcripts (edit-voice)
  gen/map.json  gen/provenance.json   # generated shots: slot map for edit.py fill; model, prompt, price, job_id
  refs/                      # reference clips for named effects and their sheets — never shared, never packed
  remake/                    # remake analysis (slots / survey sheets show reference frames — never shared)
  <cmd>_<stamp>.log/.job.json  # background jobs (--background): log + state for edit.py status; not packed
  .ed_cache/                 # analysis cache (rebuilt when missing)
```
Point timeline sources at `$PROJ/media/…`: in a new session only the links need recreating.

## Pack and unpack

```bash
python3 -I $ED/engine/edit.py pack $PROJ --out /mnt/user-data/outputs/<name>.edit.zip     # --media auto|all|none, --max-mb 256
python3 -I $ED/engine/edit.py unpack <name>.edit.zip --project /home/claude/projects/<name> --search /mnt/user-data/uploads
```
`pack` stores the project data (json, md, srt, py) and a manifest of every file the timelines and specs use (sha256,
size, duration); files up to `--max-mb` are stored inside (`media/<name>`), bigger ones are relinked on `unpack` by
hash (fallback: size + duration) from `--search` and the usual upload folders. A remake's reference video is listed
but **never stored**; renders, sheets (they can show reference frames), QA folders and caches are left out. `unpack`
rewrites the timelines to the new paths and exits with code 3 while a source is still missing — ask the user to
upload it, then run `unpack` again.

The user's shared data — `/home/claude/projects/_user/`: the style DNA database `dna/`, their own genre and move
cards, the brand kit (their fonts with licences, colours, logo) — is a separate folder: pack it as its own project.

## Where to keep the archive

| option | how |
|---|---|
| a file kept by the user (default, always works) | the archive in `/mnt/user-data/outputs/`; next session the user attaches it |
| Higgsfield storage | `media_upload(filename="<name>.edit.zip")` → PUT with the returned command → `media_confirm(type="file")` → a link; next session `curl -sSfL "<link>" -o p.edit.zip` |
A Higgsfield link opens for anyone who has it, and the archive holds file names, transcripts and (by default) the
smaller source files: pack with `--media none` for that, and tell the user before uploading. Write the link and the
archive name into `notes.md`.

## Continuing in a new session

1. Get the archive (an attachment or a link) and `edit.py unpack` it into `/home/claude/projects/<name>`.
2. Read `notes.md` and `project.json`: what the project is, which version, what the user asked last.
3. Sources not stored: ask the user to upload them again, then `unpack` again with `--search`.
4. `edit.py doctor`, render a draft of the latest version, continue from there.
