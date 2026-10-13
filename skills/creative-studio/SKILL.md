---
name: creative-studio
description: "Single entry point for ALL visual, creative and graphics work: any image, photo, video, reel, ad creative, banner, brand film, avatar, AI influencer, UGC, talking head, animation, motion graphic, explainer, 3D, WebGPU or shader scene, photoreal or human depiction (including Indian and Asian people), storyboard or campaign. Routes to the right sub-skills (Higgsfield, Seedance, photoreal humans, code-rendered video, WebGPU, UI motion, ad strategy, brand), enforces a 6-question intake, a 3-skill load budget, an 8-step studio pipeline with named owner agents, a 100-point QA scorecard (pass 85 drafts / 90 finals), credit quotes before spend, and compliance gates. Load this first for any creative request, then follow its routing."
license: MIT
user-invocable: true
---

Part of the cinematic pipeline: entry point creative-studio

# Creative Studio (router and operating system)

This skill holds no craft content. It decides which skills to load, in what order, with which gates. Craft lives in the skills named below.

## 1. What this covers (map)
| Need | Load | Reference to open (one only) |
|---|---|---|
| Long-form film, series, short film (story to delivery, any genre or language) | `film-studio` | the one references/ file for the phase |
| Voice, dubbing, music, sound, Indian languages, editing (see One cinematic pipeline) | `voice-studio`, `music-and-sound`, `indic-languages`, `edit-director` | the one references/ file for the task |
| Camera, shots, lenses, lighting, shot lists (AI video and image) | `cinematography` | references/shot-sizes-and-angles.md |
| Any AI image or video, tool and model choice, credits | `higgsfield-master` | mcp-operations.md, production-pipeline.md, credits-and-budget.md or signature-shots.md |
| Realistic people, skin, hands, AI-look removal, likeness rules | `photoreal-humans` | realism-qa-checklist.md |
| Indian, South Asian, East Asian, SE Asian people | `asian-human-reference` | regions-and-appearance.md or prompt-library.md |
| Seedance 2.0 prompting on any surface | `seedance-20` | its SKILL.md body only |
| Named looks (cinematic, 3D, cartoon, ecommerce, social hook, brand story, fashion, food, product 360, music, anime, comic, fight, real estate, motion ad) | folders `01-cinematic` to `15-real-estate` | the one pack that matches |
| Browser-driven generation helpers | `higgsfield-image-auto`, `ugc-video-auto`, `seedance-auto-generate` | none |
| Code-rendered video (default) | `motion-reel` | reference/engine.md |
| HTML-composition video | `hyperframes` | the matching hyperframes-* sub-skill |
| React-programmatic video (licence permitting) | `remotion-create` | remotion-render |
| Real-time web graphics, shaders, compute | `webgpu-wgsl` | references/recipes-basic.md |
| Rendering theory, PBR, lighting, glTF, engine choice | `graphics-rendering` | references/engine-choice.md |
| UI and 3D motion principles, easing, performance | `motion-animation` | references/web-stack.md |
| Animation pattern library on React or Next | `framer-motion-skill` | none |
| Ad copy and creative variations | `ad-creative` | references on request |
| Paid media strategy, geo and vertical playbooks | `ads-agency-pro` | references/geo-playbooks.md |
| Brand voice, identity, consistency; banners, hero and social sizes | `brand`, `banner-design` | references on request |
| Colour grading and LUTs; VFX, compositing and AI cleanup; acting direction and motion transfer (see One cinematic pipeline) | `color-grading`, `vfx-compositing`, `performance-direction` | the one references/ file for the task |
| Film titles, credits, posters, trailers; film legal and delivery; production tracking | `title-and-key-art`, `film-legal-distribution`, `production-tracking` | the one references/ file for the task |

## 2. Intake (never interrogate)
Fill this brief from the request. Ask only what blocks the work; default the rest and state the defaults in one line.
1. Goal: what must the asset do (sell, announce, educate, build trust, test a hook)? Default: drive one measurable action.
2. Audience and region: who sees it, where. Default: India, urban 22 to 40, English plus the local language if relevant.
3. Format and channel: aspect, length, placement. Default: 9:16, 15 s, Instagram Reels, plus 1:1 and 16:9 crops.
4. Assets: product photos, logo, brand text bible, references, voice. Default: none supplied, original characters, generic product.
5. Budget in credits: hard cap for the job. Default: proofs only (about 20 percent of a typical job), finals after a yes.
6. Deadline. Default: draft in 1 day, final in 3.
Output the brief as a 6-line block; get one confirmation only if credits or publishing are involved.

## Fast path: scene + images to finished video
Use when the user gives a scene plus images. Run these steps in order.
1. Asset lock: read every image given. For each, write a lock: subject identity (face, skin depth and undertone, hair, attire); product (exact shape, colour, label text, material); location and light. Never invent details that contradict the images.
2. Beats: split the scene into beats. Pick duration (default 5 to 10 s per clip), aspect (9:16 for Reels/Shorts, 16:9 for film, 1:1 or 4:5 for feed) and model with the higgsfield-master decision tree: Seedance for multi-shot or character work, Kling or Veo for realism or audio, Cinema Studio for camera control.
3. Prompt: write in the chosen model's dialect (higgsfield-master references/model-dialects.md), in this order: subject, action, setting, camera (shot, lens, move; signature-shots.md if it fits), light, mood and colour, realism cues (photoreal-humans), cultural accuracy (asian-human-reference if Indian or Asian people appear), audio or dialogue if needed. Close every open choice. Keep one subject and one action per beat. Image references stay authoritative.
4. Prompt pack in chat: prompt, model, settings, reference images used, credit estimate and current balance. Wait for the user's explicit yes.
5. On yes: media_upload the images, draft on the fast or cheap tier, QA with the master scorecard (section 6). Below the pass mark (85 drafts, 90 finals): fix one variable and retry. After 4 failed retries: rewrite the prompt. Then render the final, upscale if needed, show the result and log it (section 8).
6. Deliver the final video, the final prompt and the seed/settings so the result can be reproduced.

## 3. Router decision tree
1. AI generated image or video
   - Always `higgsfield-master`.
   - People on screen: add `photoreal-humans`.
   - Indian or Asian people: add `asian-human-reference` (all three load for that case).
   - Creative camera or transition work: open signature-shots.md from higgsfield-master.
   - Named visual style: open the single matching 01 to 15 pack instead of a general reference.
2. Code-rendered video
   - `motion-reel` by default (in-house, no licence concerns).
   - `hyperframes` for HTML compositions, captions, slideshows, PR-to-video.
   - `remotion-*` only if the Remotion licence fits the use (owner's own or permitted freelance work; otherwise do not use).
3. Real-time web graphics or 3D
   - `webgpu-wgsl` for the code, `graphics-rendering` for lighting, materials, engine choice.
   - Engineers build; the studio supplies concept and asset specs.
4. UI motion
   - `motion-animation` for principles and timing, `framer-motion-skill` when the app is React or Next.
5. Ad strategy and copy
   - `ad-creative` for variations and specs, `ads-agency-pro` for plan, geo and channel rules.
6. Brand
   - `brand` for voice and identity, `banner-design` for banners and hero art.
7. Film, voice, music, edit: follow the One cinematic pipeline section below (film-studio, voice-studio incl. film-studio/references/elevenlabs.md, music-and-sound).
Mixed jobs: pick the lane that produces the asset and treat the others as inputs (brand first, then generation, then ad specs).

## One cinematic pipeline
One chain; each stage has one owner, so there is never a doubt. Default named first, alternative only where stated.
1. Brief and intake: creative-studio (section 2); owner creative-director.
2. Story and script: film-studio (story-and-script.md), plus indic-languages for Indian-language scripts; owner screenwriter.
3. Shot design (camera, lens, light, colour): cinematography, following cinematography/references/scene-to-shot-reasoning.md and the fps rules in cinematography/references/frame-rates-deep.md; owner cinematographer.; works with performance-director on blocking and eyelines
4. People realism and bibles: photoreal-humans + asian-human-reference; owner production-designer.
5. Performance direction: performance-direction (beats, subtext, eyelines, Kling motion control or Runway Act-Two transfer, performer consent, lipsync acting; asian-human-reference expressions, indic-languages for lipsync); owner performance-director, with the cinematographer, before generation.
6. Prompt writing: higgsfield-master dialects; higgsfield-timed-prompts for multi-shot timecoded Seedance (style packs 01 to 15 and seedance-20 as needed); run the 512 check from cinematography/references/prompt-compression.md before any generation; owner prompt-engineer.
7. Generation: higgsfield-master, via edit-gen (Elements consistency) or direct; owner prompt-engineer (user's yes first).
8. VFX and cleanup: vfx-compositing (AI cleanup of hands and text, keys, sky, set extension, CG plus AI, hybrid comps; repair before regenerate); owner vfx-artist, after generation and before the edit.
9. Voice: voice-studio + indic-languages (ElevenLabs; Indian scripts, lipsync, subtitles); owner voice-director.
10. Music, score and SFX: music-and-sound; owner composer-sound-designer.
11. Edit and assembly: edit-director (beat-sync, styles, captions via edit-voice); film-studio editing-and-assembly for long form; owner editor.
12. Colour grade: color-grading (pipeline, shot matching across models, skin check with no lightening, LUTs, grain and halation, colour QC); owner colorist, after the editor's picture lock and before QA.
13. Titles, credits, posters, thumbnails, teasers, trailers: title-and-key-art (motion via motion-reel / hyperframes); owner title-designer, after the colorist and in parallel with the editor's final conform; fullstack-engineer for code-rendered builds.
14. 3D and web: webgpu-wgsl + graphics-rendering (UI motion: motion-animation); owner fullstack-engineer.
15. QA: the master scorecard (section 6), 85 drafts / 90 finals; owner continuity-supervisor (qa-tester for code builds), then creative-director sign-off.
16. Delivery and legal: film-legal-distribution (releases, music, E&O, CBFC, platform specs; not legal advice, a lawyer reviews) plus film-studio delivery-and-legal; owner producer, creative-director signs off (publish only on the user's yes).
Across all stages: production-tracking (shot tracker, credit budget, burn chart, daily and weekly reports, 3-2-1 backup); owner producer (replaces product-analyst for film).
Handoff contract, artifacts passed stage to stage, all in `C:/Claude Code/company/creative/<client>/<project>/` (Windows edit workdir `C:/Claude Code/cinema-studio/edit` via ED_ROOT):
brief.md -> script -> shot list with shot IDs -> performance briefs -> prompt pack -> asset locks -> takes -> vfx plates -> edit timeline (lock) -> graded master -> mix -> final.
- Special lanes: ad research plus multi-agent ad production: create-ads-with-agents; faceless YouTube script: faceless-script-writer; faceless video prompts: faceless-video-prompts; MiniMax H3 launch or motion-design prompts: minimax-h3-motion-design; clipping business: higgsfield-master references/clipping-business.md
Overlaps resolved:
- Editing: edit-director is the default for short-form and beat-cut; film-studio ffmpeg recipes for long-form. Colour: color-grading owns the grade; cinematography color-and-look is look intent only. Code-rendered video: motion-reel is the default, hyperframes the alternative. Timed prompts: higgsfield-timed-prompts whenever one Seedance generation holds more than 1 shot.

## 4. Load budget (token discipline)
- Load at most 3 skills per step, and open at most one reference file from each. Never read whole folders.
- Order: the lane skill, then the people or culture skill, then one support skill.
- Summarise references into the brief; never paste them into prompts.
- Later steps may load a different set of 3 (for example copy and ad specs at step 7).
- If a 4th skill seems needed, finish the current step, record the output, then load it fresh.

## 5. Pipeline (studio SOP, 8 steps)
Every step ends with a gate. Do not advance on a failed gate.
| # | Step | Owner agent | Gate |
|---|---|---|---|
| 1 | Brief (section 2, plus references and constraints) | product-analyst or growth-marketer | Brief block complete; defaults stated; cap set |
| 2 | Concept and moodboard (2 to 3 routes) | creative-director | One route picked; claims list drafted |
| 3 | Brand and look check | ui-designer | Palette, type, logo rules and text bible match the brand; no other client's assets |
| 4 | Prompt pack and shot list | creative-director | Prompts per model dialect; people spec (tone, region) written; credit quote computed |
| 5 | Draft production (proofs, low cost) | creative-director, or fullstack-engineer for code-rendered and WebGPU | Balance checked, quote given, user's explicit yes received before any spend |
| 6 | QA (section 6) | qa-tester | Score 85 or higher for drafts, 90 for finals, no critical fail; max 2 repair rounds, then redo |
| 7 | Copy and ad specs (captions, CTAs, placements, disclosures) | growth-marketer | Claims substantiated; disclosure and platform rules applied; no TikTok for India |
| 8 | Finals and delivery note | creative-director then tech-writer | Finals re-checked after edits; log complete; note lists files, specs, credits, risks; publish only on the user's yes |

## 6. Master QA scorecard (0 to 100, pass 85 drafts / 90 finals)
Merges higgsfield-master (frozen-frame QA), photoreal-humans (realism-qa-checklist.md, 28 tells) and asian-human-reference (prompt-library.md QA list). Score each block; open the named reference only for detail.
| Block | Pts | Short criteria | Detail in |
|---|---|---|---|
| Skin and face | 20 | Tone matches brief in every frame, no lightening or grey cast; pores and fine lines; faces differ in a group; no plastic smoothing | realism-qa-checklist.md |
| Eyes, mouth, hands | 15 | Eye type as specified; teeth natural; finger count and grip logic; no melted contact | realism-qa-checklist.md |
| Light, optics, scene | 10 | One consistent light source; believable lens depth; wardrobe and background continuity | realism-qa-checklist.md |
| Motion and video | 15 | No morphing at 5 to 8 s; no extra limbs; physics plausible; lip sync; no hallucinated music or lyrics; first frame is a hook | higgsfield-master SKILL.md section 4 |
| Product and brand | 15 | One product, correct shape, legible label, cap logic; no text baked into generation; brand lock held | higgsfield-master, realism-qa-checklist.md |
| Cultural accuracy | 10 | Region, attire, hair, grooming, gestures correct; no generic pan-Asian look; no caricature | asian-human-reference prompt-library.md |
| Compliance | 10 | Claims substantiated; AI label decided; consent on file; no fake testimonial | higgsfield-master compliance.md |
| Platform fit | 5 | Safe zones (9:16: 14 percent top, 35 percent bottom, 6 percent sides); legible at phone size; length and size correct | higgsfield-master SKILL.md section 4 |
Critical fails (asset fails regardless of total): skin tone lightened; real person without consent; fabricated testimonial or before-after shown as real; unsupported cosmetic claim; wrong product shape or gibberish label on a hero shot.
Repair rounds fix the two worst tells by edit or reference, not by blind reroll; rescore after each.

## Quality bar and credit discipline (standing)
Owner rule: award-level, ultra-realistic output AND no wasted credits. Both are enforced on every job.
**Quality bar.** Benchmark is award-level cinema and top global ad work. Scorecard pass mark: 85 for drafts (drafts are not scored for delivery), 90 for any client or final deliverable. Craft pillars, all required: intentional cinematography per beat, motivated lighting, skin and material realism, continuity, sound design, edit rhythm. No visible AI tell ever ships (realism-qa-checklist.md).
**Think before you render.** Most quality comes from pre-production, not rerolls. Ladder:
1. Write the full prompt pack, shot list and asset locks offline (0 credits).
2. Self-review the prompt against the cinematography, realism and cultural checklists BEFORE any generation; fix ambiguities.
3. Stills first: lock the look on cheap image models (keyframe or first frame) before any video.
4. Video drafts at low resolution or short duration on fast or turbo tiers; prove only the hardest shot first.
5. Change one variable per retry. Cap drafts at 3 per shot. After 4 fails, rewrite the prompt, do not reroll.
6. Render the final once, at full quality, from the locked prompt, seed and references. Upscale approved finals only.
7. Reuse everything: Soul ID, Elements, last-frame chaining, and the saved prompt library of shots that worked.
8. Prefer web unlimited modes where allowed (personal use only); MCP and API usage always costs credits.
9. Before every run show balance, estimate and expected number of draft runs; get the user's yes; report actual versus estimate after.
**Waste log.** Record every failed generation and its cause in the project log.md (section 8). Weekly review checks the waste rate; target under 25 percent of credits on rejected outputs (an estimate, not a guarantee).
**Learning loop.** After each project add winning prompts to `C:/Claude Code/company/creative/prompt-library.md` with model, settings and score. Check that library before writing new prompts.

## 7. Money and safety gates (non-negotiable)
- Spend: check balance, give a credit quote (per asset and total, proof versus final split), then wait for the user's explicit yes. A changed quote needs a new yes. Never use unlimited or auto-refill options unprompted.
- Never publish, post, deploy or send an asset without the user's explicit yes.
- Real-person likeness (face, voice, Soul ID, clone) needs documented consent; never a celebrity. Prefer original characters.
- No fake testimonials, doctors, reviews or AI before-and-after presented as real results.
- Disclosure: apply ASCI (India), FTC (US) and Meta rules; label realistic AI people, virtual influencers and AI demos; use platform AI-content toggles.
- TikTok is banned in India: never plan, build or schedule it for Indian audiences.
- Skin-tone fidelity: state the tone in every prompt; never lighten, even for "glow" or beauty looks.
- Cosmetic claims need substantiation and regulatory review by the qualified team; AI visuals must not exaggerate results.
- Confidentiality: never upload unreleased formulations, confidential packaging or customer data to a generation platform; keep one client's brand out of another's prompts and demos.

## 8. Asset logging
Append every generation and decision to `C:/Claude Code/company/creative/<client>/<project>/log.md` (create folders on first use; use "internal" as client when there is none). Columns: date, step, tool and model, prompt ref, job id, credits, result, QA score, notes. Start the file with a header block: the brief, cap, quote and the date of each approval.

## 9. Quick recipes (one line each)
1. Skincare product ad: higgsfield-master + `07-ecommerce-ad` or `09-product-360`, real pack as reference, texture macro plus hand-in-frame, no results claims, ad-creative for specs.
2. Indian UGC testimonial-style, compliant: higgsfield-master + photoreal-humans + asian-human-reference, original character, scripted "my routine" (not a fake review), AI label on, ugc-video-auto optional.
3. AI influencer series: Higgsfield character lock, text bible plus reference set reused verbatim, 6 episodes planned before any spend, label every post.
4. Brand film: `12-brand-story` + `01-cinematic`, 6 to 8 shots from a shot list, signature-shots for transitions, brand skill for tone.
5. 3D product web hero (WebGPU): webgpu-wgsl + graphics-rendering, glTF asset, IBL lighting, WebGL2 and static-poster fallback, fullstack-engineer builds.
6. Animated explainer: motion-reel by default (hyperframes-faceless-explainer if HTML-based), script first, captions on, beat-synced sound.
7. Reels hook pack: `11-social-hook`, 10 hooks of 3 s each in 9:16, mid-motion first frame, proof at 720p, ad-creative for variants.
8. Festive campaign: brand + ad-creative + higgsfield-master, one master concept resized for feed, story and banner, regional attire via asian-human-reference, ads-agency-pro geo-playbooks for timing.
9. User gives scene + images -> Fast path (see the Fast path section).
