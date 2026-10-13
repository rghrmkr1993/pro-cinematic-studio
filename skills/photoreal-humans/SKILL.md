---
name: photoreal-humans
description: "Playbook for realistic images and video of people, with skin as the main focus, covering both AI generation (Nano Banana, Flux, Midjourney, Seedream, Soul, Veo, Kling, Seedance) and 3D rendering (Blender Cycles, Unreal MetaHuman, three.js). Use for any photoreal portrait, model, UGC, avatar, influencer, beauty or skincare visual, any request to remove the AI look, plastic skin or uncanny faces, skin tone and undertone accuracy including South Asian and Indian skin, eyes, hands, hair, subsurface scattering setups, realism QA scoring, and consent, deepfake and AI-disclosure rules. Research-based, dated 2026-10-13."
license: MIT
user-invocable: true
metadata:
  version: "1.0.0"
  researched: "2026-10-13"
---
Part of the cinematic pipeline: entry point creative-studio

# photoreal-humans

Realism companion for any image or video that shows a human. It does not replace the router: pick tool, model and credits with `higgsfield-master` (Higgsfield jobs) or `seedance-20` (Seedance dialect) first, then use this skill for the realism layer. For code or engine rendering, also load the graphics-rendering skill (see section 8).
Labels used in references: (V) vendor-official, (3P) third-party or community guide, (E) estimate or rule of thumb, (U) unverified or sources conflict. Dated 2026-10-13; models change weekly, so re-test any prompt or setting before relying on it. All guidance here is visual craft, not evidence of product performance and not legal advice.

## 1. Route the job (open ONE reference, two at most)
| Job | Open |
|---|---|
| What real skin, eyes, teeth, hair, hands look like; skin tones, Indian skin, avoiding whitewash | references/skin-and-face.md |
| Write or fix a prompt for a photoreal person, per-model realism tricks, upscale, video motion, product and cosmetic texture | references/ai-prompting-realism.md |
| Digital human, SSS, skin shader, Blender, Unreal, three.js | references/3d-skin-rendering.md |
| Score a result, decide ship or redo, find the fix for a tell | references/realism-qa-checklist.md |
| Real faces, deepfakes, AI labels, minors, testimonials, claims | references/ethics-and-consent.md |
Compliance (the last row) is a gate on EVERY job that shows a realistic person, not an optional read.

## 2. The six realism laws
1. Real skin is uneven. Pores, vellus hair, oil zones, redness, asymmetry and small marks are the signal; smooth, even skin is the AI tell. Ask for them in positive words, and avoid "flawless", "perfect", "airbrushed", "glowing", "dewy" in the prompt (they push smoothing).
2. Light does most of the work. Name one motivated source, its direction, size and colour temperature. Impossible or mismatched light betrays a render faster than any skin flaw.
3. Describe a photograph, not a quality. "Photorealistic, 8K, hyperdetailed" is weak (3P). Camera body class, lens, aperture, film or sensor behaviour, and an honest-photo register ("unretouched candid frame") are strong.
4. Name tone, undertone and ethnicity explicitly. Defaults skew lighter and Western in several generators (3P studies); never rely on them. See skin-and-face.md.
5. Fix by edit, not by blind reroll. Inpaint or edit the defective region (face, hand, teeth, text), re-check skin after every pass, because each edit and upscale softens detail.
6. Realism is not deception. Consent, disclosure and claim honesty are part of quality. AI people never "demonstrate" results.

## 3. Workflow (stills)
1. Brief: person (age, build, ethnicity, depth and undertone, distinguishing marks), setting, light, camera, purpose, claim risk, consent status.
2. Choose model by the realism need (ai-prompting-realism.md section 5). Draft cheap, finals once.
3. Prompt in this order: framing and camera, subject identity, skin and imperfection cues, eyes, hair, wardrobe, environment, one light source, grade and grain, constraints.
4. Generate 4 proofs at low cost. Inspect at 100% zoom on forehead, nose, under-eye, lips, hands. Score with realism-qa-checklist.md.
5. Repair the worst tell (inpaint or a Seedream/Kontext-style edit that keeps composition and changes micro-realism only).
6. Optional detail pass, conservative: 2x face-aware upscale, low creativity, high resemblance, grain last.
7. Compliance gate, then deliver with provenance metadata kept (C2PA or platform labels) and a text-free master.

## 4. Workflow (video)
1. Start from a sharp, neutral-lit, front-facing still that already passes the still QA; image-to-video beats text-to-video for faces.
2. Motion is small and specific: breath, blink, gaze shift, head tilt, one gesture. One camera move per shot, handheld only as gentle sway.
3. Keep clips short (4 to 8 s), chain by last frame, and re-check identity drift at the 5 to 8 s mark.
4. Frozen-frame review plus real-speed review: blink timing, lip sync, jaw and neck motion, hair and cloth physics, hands.
5. Same compliance gate; synthetic realistic people in ads need a label.

## 5. Workflow (3D)
1. Decide the target: offline hero render (Cycles, Unreal path tracer), real-time (Unreal Lumen, three.js) or a facial-scan-based digital human (MetaHuman).
2. Build the skin as layers: albedo with melanin and redness variation, multi-scale normal detail, roughness variation by zone, dedicated SSS profile or radius, thin oil coat, peach-fuzz sheen.
3. Light with large soft area sources plus a rim, then check ears, nostrils and lips for translucency.
4. Grade, add lens effects and film grain; compare side by side with a real photo under the same light.

## 6. Hard rules
- Never use a real person's face or voice without documented written consent; never a celebrity.
- No minors in sexualised content, ever; no minors in beauty, anti-ageing or cosmetic-claim content.
- No fabricated customers, doctors, reviews or before/after results; no AI skin shown as a product result.
- Do not lighten, narrow or "correct" a subject's skin tone, hair texture or features unless the brief is an explicit, consented retouch.
- Keep any client's brand, face or product out of another client's prompts, demos and examples.
- Skincare claims, shade names and texture shown need substantiation and review by the qualified team; do not let AI visuals imply an effect.

## 7. Defaults when the brief is thin
Adult, natural window light from camera left, 85mm equivalent at f/2 to f/2.8 for portraits (35mm for UGC context), neutral white balance, soft shadow roll-off, fine grain, visible pores, faint asymmetry, no beauty filter, no text in frame, closed or relaxed mouth if teeth keep failing, hands out of frame or simple.

## 8. Related skills
`higgsfield-master` (router, credits, studios), `seedance-20` (Seedance dialect), `ugc-hot-girl` and `ugc-video-auto` (UGC fallbacks), `07-ecommerce-ad`, `13-fashion-lookbook`, `02-3d-cgi` (style packs, only when named), `motion-reel` (code video), `unreal-mcp` (Unreal driving), `webgpu-wgsl` (browser GPU shaders). Graphics-rendering skill (`graphics-rendering`): generic real-time rendering theory, PBR, lighting, tonemapping; load it with 3d-skin-rendering.md for engine work and do not duplicate it here. `asian-human-reference`: region-by-region Indian and Asian faces, attire and gestures; load it for any Indian or South Asian subject, alongside skin-and-face.md.
Owners: creative-director (prompting and generation), qa-tester (scoring), growth-marketer (claims), Manager (consent and disclosure sign-off).

## 9. Report format (8 lines max)
Tool and model chosen and why; realism checklist score and worst tell; fix applied; skin tone and undertone specified; consent status; AI label decision; credits used; open risks.
