# Characters, AI influencers and consistency (researched 2026-10-13)
Labels: (V) vendor-official, (3P) third-party, (U) unverified.

## Tool map
| Need | Use | Notes |
|---|---|---|
| Real person (consented) in images and video | Soul ID | train once, reuse across Soul models; Elements reference it in Seedance (real people require Soul ID first, V) |
| Invented persona | AI Influencer builder, then Soul ID on its portraits | 1.12 credits per character; save as Element; Recreate |
| Film actor | Soul Cast (Cinema Studio) | parameters: genre, era, archetype, physique, outfit, imperfections |
| Environment | Soul Location, locked location Element | build before characters |
| Props and products | Elements, reference images, Brand Kit | product packshot front angle |
| Series of frames | Popcorn (8 frames, 4 refs) | one coherent unit |

## Soul ID (V help center and blog)
- Train from 20+ photos (up to 80) [official, 2026-10-13]: at least one full-height photo, no sunglasses, hats, scarves, group shots or cropped faces; a smaller clean varied set beats a large inconsistent one; do not repeat one pose; 960px+ best (3P), same person, recent (last 4-5 months), varied angle, expression, light; include full-body shots; avoid sunglasses, heavy shadow, cropped faces, busy backgrounds. 3-5 min training, about 25 credits (3P). Name it clearly.
- Strong on close and mid shots, weaker on wide shots where face is tiny. Does NOT lock wardrobe, body, product, location or cinematography: lock those separately.
- Consent: only yourself, signed models, or ambassadors with written release covering AI generation, scope, term, territory, voice.

## Consistency stack (V blog, how-to guides)
1. Identity: Soul ID or Element, plus 2+ reference angles (front and three-quarter). Prefer anchors over text.
2. Location: one establishing reference (geography, light direction, landmarks) reused every shot. Plant fixed anchors (door, lamp, window) and stage movement against them.
3. Look: same lens character, light direction, grade, aspect ratio for every shot in a sequence.
4. Wardrobe and product: reference images in every shot, describe wardrobe verbatim each time.
5. Chain clips: last frame becomes next first frame; keep clips under about 30s.
6. Change one variable per shot (setting OR angle OR light).
7. Cross-session: save the strongest frame of a finished sequence as an extra anchor.
8. Seedance @ roles: @character (identity), @style (look), @motion (camera and movement), @audio (sync). Up to 9 images, 3 video, 3 audio on 2.0; 30 + 10 + 10 on 2.5.
9. Test the hardest shot first.
10. Keep identity separate from motion in prompts: identity in the Element, action in the prompt (3P rule, consistent with V).

## Why faces drift (V blog)
Text descriptions ("brown hair, strong jaw") are reinterpreted each generation; single-angle references under-anchor identity; stacked changes (angle plus light plus action) compound drift; long clips accumulate error.

## Anti-AI-look person recipe (company house rule, from prior research)
Order: composition, "identical original subject", background, identity (age, skin), face, eyes with "naturally muted catchlights, no oversized specular glare", brows, hair with finish, realism module, body, wardrobe top to shoes, lighting, quality tail, negatives.
Realism module: visible fine skin texture with natural pores, fine lines, subtle asymmetries, natural makeup with slightly uneven blending, faint blush, slight natural sheen not glossy, no digital smoothing, no beauty filter, no airbrushed look. Imperfection anchors (faint freckles, small mole). Adults: mature bone structure, no babyface. Negatives: no text, no watermark, no plastic skin.
De-slop pass: Seedream i2i with "keep composition, poses, product exactly; change only micro-realism: pore-level skin, real material detail, even natural light, faint sensor noise; avoid waxy skin, HDR glow, oversharpening, teal-orange grade".

## Realistic hands and skin in video
Hand-count law (two hands, name each hand's job, one action per beat), selfie shots allow one free hand, product held or resting never floating, multi-step actions across cuts, avoid fast hand motion, prefer medium shots for hands. Skin: neutral daylight, deep focus for UGC, avoid "glowing" or "dewy" words that push plastic look.

## AI influencer program (business use)
Define persona bible (name, age range, voice, values, wardrobe palette, locations), label as virtual per ASCI and platform rules, never fabricate lived experience or sensory claims ("it feels silky on my skin") for a synthetic persona (3P reading of ASCI, U), get brand-owned rights, keep a consent and disclosure log. Prefer a real, consenting spokesperson plus Soul ID for scalable variants, disclosed as AI-assisted.

## Voice
Voice cloning only for voices owned or permitted. Lock a voice prompt or cloned voice per character; Seedance and Kling speak natively. Lipsync models need front-facing, uncovered mouth.

## Official additions [official, 2026-10-13]
- Results are "clearly the same person", not pixel-identical. One Soul ID holds one person; use Elements for multi-character scenes. A trained character cannot be exported as a file. Weak sets, extreme style shifts and odd angles cause drift; retrain on a stronger set (varied poses, less shadow, full-height shot). Invented character: generate portraits first, then train.
- Academy rules: character sheet on plain grey, close-up plus full body; erase the face from the full-body panel so only ONE face is locked; separate sheets for each wardrobe or state (dry, sweaty, aged); cast side characters with AI Cast; build a layout map for geometry; run hero through each location before locking; after every edit pass re-check skin detail. See academy-lessons.md.
- Talking characters (blog 2026-10-08): front-facing image, mouth uncovered, 1 to 2 sentences (about 35 words fits 15 s), check eyes, jaw, hair, signature details while speaking; Lipsync Studio offers 8 models, 18+ languages.
- Series drift (blog 2026-10-05): decide the style once and point every generation at the style reference; keep a growing reference library; compare against the season-one reference before each batch.
