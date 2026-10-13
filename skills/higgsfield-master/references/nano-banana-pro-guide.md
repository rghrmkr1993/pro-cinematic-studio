# Nano Banana Pro guide [official, 2026-10-13]
Sources: higgsfield.ai/nano-banana-pro-prompt-guide (thin, marketing-style, 7 gallery prompts), help center "How do I use Nano Banana?", academy lessons (brand visuals, 3-step ad), blog on unlimited Nano Banana 2. Labels: (V) official statement, (H) house practice inferred from official lessons, not stated by the guide. Nano Banana is Google's model family, not built by Higgsfield (V).

## Family facts (V help center)
| Model | Refs | Resolution | Notes |
|---|---|---|---|
| Nano Banana Pro | 14 | 1K to native 4K | reasons about the prompt before rendering; accurate typography |
| Nano Banana 2 | 14 | 1K to 4K | up to 5 consistent characters and 14 stable objects in one scene |
| Nano Banana 2 Lite | 14 | 1K fixed, about 4 s per image | Thinking setting High or Minimal, no resolution picker |
| Nano Banana (original) | 8 | n/a | short-instruction edits, adds or edits text |
Draft at 1K or on Lite, iterate, then final at 2K or 4K. Blurry at 2K/4K: retry, or generate lower and upscale. Refs must be JPG, PNG or WebP, no heavy compression or watermarks (size limit not stated).

## The five-part prompt (V guide)
1. SUBJECT: specific, no ambiguity ("a Shiba Inu with metallic plating", not "dog").
2. COMPOSITION: direct the virtual camera: macro for texture, isometric from above, fisheye, shot scale, numeric aspect ratio (16:9, 2:3).
3. ACTION: motion and energy ("leaping across a rooftop gap"); static images are weak.
4. LOCATION: setting and atmosphere ("neon-lit back alley").
5. STYLE: medium and aesthetic ("vintage 1980s polaroid").
Add: lens focal length, aperture, shutter speed for real depth; gear tag ("shot on a full-frame cinema camera") for grain and photoreal; negative constraints to block distortion or biological errors.

## Reusable templates (rewritten from the gallery, H)
- Cinematic scene: `[subject + 2 anchors], [action], [location + one light source], [lens mm, aperture], [film look], [ratio], [resolution]`.
- Product hero: `Exactly one [product], front label facing camera, on [surface], [one soft key light], [lens 85mm f/4], clean background, no extra text, 4:5`.
- Layout or ad mock: `[era] [medium] ad layout, [grain], [hero object floating], bold title "EXACT TITLE" in [font family], bottom lineup, fictional branding only`.
- Macro or POV: `Ultra-detailed POV from inside [container], looking up at [person doing action], [light on face], slight lens distortion, [droplets], hyperrealistic textures, [mood]`.
- Architecture or editorial: `[geometry], [material], [plants], [black-and-white architectural photograph], [time of day], [ratio]`.
- Surreal scale: `Tiny [workers] working on a giant [material] as if it were [landscape]`.

## Precision features (V)
- COMMAND style: drop filler like "please"; short instruction syntax holds focus better.
- Relative positioning: place objects by position ("exactly 3 bottles on the left of the frame"); help center asks for explicit quantities, layout and lighting.
- NEGATIVES: list what to exclude, but keep it short (the academy warns against long exclusion lists).
- Reference weights: when image inputs are used the guide says each can carry a weight for influence (UI availability not verified).
- Seed: guide says lock the seed once a result works and reuse it for a series. Cinema Studio has no seed control (3P), so on Higgsfield rely on references, not seeds (U for Nano Banana UI).

## Text rendering (V)
Put the exact string in double quotes, name font family (or style, size, placement), keep the copy short, one text block per area. Pro and 2 render typography accurately; use for in-frame text only, otherwise overlay type in editing (company rule). Verify spelling on every output.

## Multi-image reference rules (V help center plus H)
- Describe each reference's ROLE in the prompt (character, outfit, location, product). Connecting alone is not enough.
- Change the prompt OR the references between iterations, never both.
- Character consistency: attach the same portraits in Multi-reference mode on every generation and state the character's role.
- Sheet-building (academy): product from one photo to front/3-4/back sheet; character sheet two or three panels on plain grey; location 3/4 angle; schematic map for geometry; stills at 3:4 for social, same ambassador across the batch (H from lessons, GPT Image 2.0 is the course's pick for sheet edits).

## Editing tricks (H, from lessons)
- Edit prompts name what stays and what changes: "keep face, pose, background exactly; change only [wardrobe]".
- Every edit pass softens skin; check detail after edits; for faces prefer one clean generation over chained edits.
- The separate Edit tool deducts credits (about 1.5 observed by a vendor blog) even while an Unlimited window runs; generation with references inside the Unlimited toggle does not (V blog, 2026-09-21).

## Access and cost (V blog 2026-09-21, verify)
Plus and Ultra plans include one 7-day Unlimited window on Nano Banana 2 at 2K; Ultra adds Pro at 2K; 4K needs credits. Starter pays about 2 credits per image. Original Nano Banana is in the 365-day Unlimited set. Window runs on the standard queue and never inside MCP, CLI, Canvas or Supercomputer.

## Pitfalls
Typo "Nano Banano" and mixed nano_banana_2 links on the guide page (cosmetic). Marketing claims on the page (ratings, user counts) are unverified. Guide gives no weights range, no size limits, no editing section.
