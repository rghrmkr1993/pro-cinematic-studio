# AI cleanup and fixes
Labels: (V) vendor-official, (3P) third-party, (H) house rule, (E) estimate, (U) unverified. Researched 2026-10-14: Higgsfield tools list (higgsfield-master references/tools-a-z.md, official blog and changelog 2026-09 and 10), Runway help centre and third-party summaries (Aleph 2.0, Edit Studio), colourist and VFX blog advice. Costs are indicative; read the Generate button before any quote.

## 1. Triage table: symptom to fix
| Symptom | First try (free) | Then (credits, quote first) | Last resort |
|---|---|---|---|
| Bad hand, extra finger, melted grip | Cut away, insert, reframe to hide, crop | Draw to Edit or Inpaint on the hand region with a hand-law prompt (two hands, one task each) | Regenerate the beat with a simpler hand action |
| Gibberish text or label | Replace in comp with a real overlay (design the label in a vector tool, track it on) | Inpaint blank, then comp true text | Regenerate with no text, add text in post |
| Face drift, wrong eyes or teeth | Cutaway; mask a few frames | Edit Video or Genjutsu Object Swap with the Soul ID or Element reference; keyframe repair via image edit | Regenerate with stronger anchors (characters-and-consistency.md) |
| Flicker (light, texture) | Deflicker in grade, slow gain keys, temporal blur | Edit Video pass with "keep lighting stable" | Shorter clip, last-frame chaining |
| Warping background, morphing | Mask and replace with a locked plate | Draw to Edit on the region | Regenerate with a static background plate |
| Extra limb, phantom third hand | Mask out in comp using a clean frame (from the same clip) | Inpaint region | Regenerate |
| Unwanted object or person | Clone from a clean frame, cutaway | Object removal in Edit Video or Runway (mask-free in Aleph 2.0, 3P) | Reframe, crop |
| Wrong wardrobe or product colour | Secondary colour in grade (small shifts only) | Genjutsu Object Swap or Edit Video with the product reference | Regenerate |
| Low resolution or soft | Upscale last on the approved final | Upscale (Topaz or Higgsfield upscalers; Precise preserves detail, Creative can alter faces and labels, V) | Re-render at higher resolution |
| Plastic skin | Add grain, reduce sharpening; do not blur | Seedream or similar i2i de-slop pass on a keyframe (characters-and-consistency.md house recipe) | Regenerate with a realism module |
Rule: edit the smallest region, with the smallest instruction, with the best reference; one fix per pass (H).

## 2. Higgsfield tools (V, tools-a-z.md, read 2026-10-14)
- Draw to Edit inside Seedance 2.5 Edit: mark the region on the frame, describe what happens inside it; up to 50 references, video up to 30 s, up to 1080p. Also in the Adobe and DaVinci plugins.
- Edit Video: Kling 3.0 Omni Edit, FLUX 3 Video Edit, Seedance 2.5 Edit (audio change, 480 to 720p).
- Genjutsu: Motion Transfer (move a clip's motion to new cast or world) and Object Swap (replace one object, rest unchanged); one video 4 to 30 s, up to 30 images; Restyle 20+ styles.
- Edit Image and Inpaint (stills), Expand or Outpaint (extend frame), Reframe (aspect with subject tracking), Relight (listed in changelog, details U), Upscale (Topaz, ByteDance, FLUX 3 Video Upscaler).
- Plugins: Premiere Pro, After Effects, DaVinci Resolve (V). The Production Skills Bundle lists MCP workflows for Blender, Adobe, TouchDesigner and DaVinci (V, 2026-09-23).
Workflow: select the nearest-right take, export the frame range, edit, bring back, composite into the plate if only a region changed (mask the edit result over the original to protect the unchanged parts and keep the original grain, H).

## 3. Image-model edits (keyframe repair)
- Nano Banana (Gemini image edit family) and Seedream or Flux Kontext style edits: change one thing in a still while keeping composition and identity (higgsfield-master models; names and credits as listed in its catalogue; edit capabilities from vendor pages and community use, 3P).
- Use for: fix a keyframe (hand, label, wardrobe), then use the repaired still as the first frame for an image-to-video redo or as a reference for Edit Video.
- Prompt shape: "Keep everything identical. Change only [region]: [exact result]. Same lighting and skin tone. No text unless [text]." Add the reference image and name its role.
- Check skin tone against the lock after every image edit; image models sometimes brighten faces (H, photoreal-humans).
- Real-person faces: only with documented consent, and some platforms block them (protected content).

## 4. Runway options (3P summary, check help.runwayml.com before use)
- Aleph 2.0 and Edit Studio: prompt-based edits of real or generated footage: product swap, background replacement, object removal, element insertion; single shots or sequences up to 30 seconds (3P summary).
- The older mask-based Inpainting tool was retired on 2026-07-30 (3P); object removal is now prompt-driven and mask-free (3P). Older tutorials may describe the retired flow.
- Green Screen: AI matte tracking from a few clicks (3P).
- Output: native 720p, upscale for more (3P). Credits apply; quote and ask first.
Use Runway only when the Higgsfield tools do not fit; one platform per shot where possible (consistency, H).

## 5. Text and logos
- Never trust model-rendered text (higgsfield-master: no text baked into generation). Generate the plate without text, then add real type in post.
- Logos and packaging: use the supplied vector or packshot, track and comp; match perspective, light and grain. Do not generate a brand's real logo (use the real file with permission).
- Indic scripts: render with a font that shapes the script correctly (libass or a design tool); see indic-languages subtitles reference.

## 6. Hands, faces, bodies: comp-level fixes
- Hand fix by patch: take a clean frame of the same hand from another moment, stabilise and warp onto the bad frame, soft matte edge, match grain. Works when motion is small.
- Eye or mouth fix: avoid. Face repair belongs at keyframe level with identity references, not paint-overs; if a face needs repair on more than 12 frames, regenerate (E).
- Never smooth skin to hide a defect. Smoothing is itself an AI tell.

## 7. Credit discipline for fixes
- Fix cost is usually a fraction of a regen, but not always: a 15 s Genjutsu job is 40 to 144 credits by resolution (V, tools-a-z.md), close to a fresh shot. Compare before choosing.
- Cap fix attempts at 2 per shot, then switch method (H). Log each attempt in log.md with cost.
- Prefer a cutaway or a different edit solution over repeated fixing (editor decides).
- Show balance, estimate and number of passes, wait for the user's yes.
