# Compositing basics and tools
Labels: (V) vendor-official, (3P) third-party, (H) house rule, (E) estimate, (U) unverified. Researched 2026-10-14 (Blackmagic Fusion and Resolve materials via third-party comparisons, Natron GitHub and Wikipedia, ffmpeg filter lists run locally on 9.0.1, Runway help centre articles via search).

## 1. Core ideas
- Alpha: a fourth channel for opacity (0 transparent, 1 opaque). Matte: the alpha as a greyscale image. Mask or roto shape: a drawn matte.
- Premultiplied versus straight: premultiplied colour is already multiplied by alpha (edges look dark when composited wrongly); straight keeps colour separate. A dark fringe means a premult mismatch; a bright fringe often means colour spill or a missing unpremult (3P, H). ffmpeg: `premultiply` and `unpremultiply` filters exist (U, run `-h filter=...`); ProRes 4444 and PNG carry straight alpha by convention.
- Over: foreground over background: result = FG alpha x FG + (1 - alpha) x BG. Every comp is a stack of overs plus colour work.
- Layers, nodes: layers (After Effects style) or node graphs (Fusion, Nuke, Natron). Node graphs are easier to audit and version.
- Resolution and bit depth: comp in 10-bit or float where possible; AI sources are 8-bit, so avoid heavy grading inside the comp (colour-grading skill).
- Plate: the shot you comp onto. Clean plate: the shot without the unwanted element. Element: the thing you add.
- Garbage matte: a loose mask that removes unwanted areas before a key.

## 2. Keying (green or blue screen, or luma and colour keys)
AI clips rarely give a clean physical key; models paint soft edges, motion blur and baked light. Use keys on purpose-made plates (green screen from a model prompt with an evenly lit flat green, or real footage).
Method:
1. Pull a core matte by colour (chroma key) with tolerance and softness; keep the inside solid.
2. Clean the edge: erode or dilate by a pixel or two, blur 0.5 to 1 pixel, feather.
3. Despill: remove green light on the subject (ffmpeg `despill=type=green:mix=0.5`, verified), then relight with the BG's colour.
4. Edge treatment: light wrap (bleed BG light into the edge), match edge softness to the plate's blur.
5. Check on a flat mid-grey and on the real BG, in motion.
ffmpeg: `chromakey=0x00ff00:similarity:blend` works in YUV, `colorkey` in RGB; both verified. Prompting a model for a green screen: flat even green, no green on the subject, no shadows on the backdrop, no motion blur on hair (H); expect imperfect edges.
Hair, smoke and glass need a proper matte tool (Fusion Delta Keyer, Nuke Keylight or IBK, or an AI matting tool such as Runway Green Screen, 3P). Runway's tool tracks a mask through the frames from a few clicks (3P, vendor-like source).

## 3. Roto and AI matting
- Roto: hand-drawn shape per frame with interpolation. Time-consuming; use AI roto first and fix by hand (E).
- AI matting options (3P): Resolve Magic Mask (Studio), Runway Green Screen, Higgsfield mask tools in Draw to Edit, SAM-style tools in ComfyUI (U). Test on your own shot; edge hair and fast motion fail first.
- Always keep the raw matte and a feathered matte as separate files; the editor may need to adjust.
- Motion blur on the matte edge: AI mattes are often sharp; blur the edge by the plate's blur amount (section 5 of shot-types).

## 4. Tracking
- 2D point tracking: attach an element to a moving surface (screens, signs, sky patches). Planar tracking for flat surfaces. 3D camera solve for set extension and CG (Fusion, Nuke, Blender; heavy).
- AI clips have no real camera, so a solve can fail; if a solve fails, use a 2D track plus manual keyframes, or lock the camera (cinematography: static or simple moves help later comps).
- Stabilise a hybrid plate with ffmpeg `vidstabdetect` then `vidstabtransform` (both present in the build checked).

## 5. Tool matrix
| Tool | Cost | Strength | Limit | Use here |
|---|---|---|---|---|
| ffmpeg (overlay, chromakey, colorkey, despill, alphamerge, maskedmerge, tmix, minterpolate, blend) | Free | Batch, scripting, simple key, overlays | No GUI, poor edge control, no tracking GUI | Default for simple overlays, sky or logo placement, shutter and grain |
| DaVinci Resolve free (Fusion page) | Free | Node compositor, planar and point tracking, keyers, masks; same Resolve file as the grade | Some tools Studio-only (3P: Magic Mask, noise reduction, parts of Fusion effects); verify per tool | Main free comp tool |
| DaVinci Resolve Studio | One-time licence (3P price not verified, U) | More OpenFX, Magic Mask, AI tools | Paid | Only if free hits a wall; needs the user's yes |
| Natron | Free, open source GPL | Node compositor in the Nuke style, OpenColorIO, OpenFX | Official stable release is 2.5.0 (2022); a community 2.6 fork exists with builds this month and is not an official release (3P, 2026-10-14). Verify provenance and checksums before running | Backup if Fusion is not suitable; quarantine steps first (operating-model section 6) |
| Blender (compositor, motion tracking, CG render) | Free | 3D render, camera tracking, node compositor | Learning curve | CG elements and camera solve |
| After Effects | Paid subscription (U price) | Layer comp, huge plugin set, tracking, roto brush | Paid, desktop | Only on a request; Higgsfield has an After Effects plugin (V tools-a-z.md) |
| Nuke (Foundry) | Paid (U price) | Industry-standard node comp, deep tools | Cost, learning | Studio-scale only |
| Runway (Aleph, Edit Studio, Green Screen) | Credits | Prompt-based video edits, object removal, matting (3P) | Paid credits, 720p native, check length limits | Quote first; see ai-cleanup-and-fixes.md |
| Higgsfield edit tools | Credits | Draw to Edit, Edit Video, Inpaint, Relight, Reframe, Upscale (V) | Paid credits, claims limited | First choice for in-platform fixes |
| ComfyUI graphs | Free software, own GPU | Open models for plates, inpaint, matting | Setup and model licences, security review | Quarantine steps before install |
Nothing new is installed or run without the quarantine steps in `C:/Claude Code/company/operating-model.md` section 6.

## 6. ffmpeg compositing recipes (all run on 9.0.1 on 2026-10-14)
```
# Chroma key plus despill over a background
ffmpeg -i bg.mp4 -i fg.mp4 -filter_complex "[1:v]chromakey=0x00ff00:0.15:0.05,despill=type=green:mix=0.5:expand=0[k];[0:v][k]overlay=x=100:y=60,format=yuv420p" out.mp4
# Alpha from a colour clip plus a grey matte clip (to ProRes 4444 or FFV1)
ffmpeg -i color.mp4 -i matte.mp4 -filter_complex "[0:v]format=rgba[c];[1:v]format=gray[m];[c][m]alphamerge,format=yuva444p10le[o]" -map "[o]" -c:v prores_ks -profile:v 4 out.mov
# Masked merge (take B where the mask is white)
ffmpeg -i a.mp4 -i b.mp4 -i mask.mp4 -filter_complex "[0:v][1:v][2:v]maskedmerge" out.mp4
# VP9 with alpha for a web overlay
ffmpeg -i in.mp4 -vf "colorkey=0x00ff00:0.3:0.1,format=yuva420p" -c:v libvpx-vp9 out.webm
# Place an image sequence or PNG with transparency
ffmpeg -i bg.mp4 -i logo.png -filter_complex "[0:v][1:v]overlay=W-w-40:H-h-40" out.mp4
# Intermediate for compositing (10-bit)
ffmpeg -i in.mp4 -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le out.mov
```
Alpha-capable outputs: ProRes 4444 (profile 4, yuva444p10le), FFV1, PNG sequences, VP9 in WebM, not plain H.264. The 3 outputs checked: FFV1 MKV alphamerge, ProRes 422 HQ intermediate, VP9 WebM with colorkey alpha, all ran (alphamerge ran with a test grey gradient; ProRes 4444 command shape not run, U).
