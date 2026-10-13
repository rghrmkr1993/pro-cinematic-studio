---
name: asian-human-reference
description: "Use for ANY AI image or video that shows Indian, South Asian, East Asian or Southeast Asian people, on Higgsfield with Seedance, Kling, Veo, Nano Banana and similar models. Gives region-by-region ranges for skin tone, face, eyes, hair, grooming and attire, FACS-based expressions, culture-specific gestures, body motion, accents and dialogue, plus 25+ prompts and a cultural QA checklist. Prevents colourism, caricature, exoticism and pan-Asian generic faces. Use alongside higgsfield-master and photoreal-humans."
---
Part of the cinematic pipeline: entry point creative-studio

# Asian Human Reference

Companion skill for depicting Indian and other Asian people accurately, respectfully and believably in AI visuals. It adds cultural and anatomical specifics; it does not replace the production workflow (`higgsfield-master`) or the realism craft (`photoreal-humans`). Load all three for any such job.

## Core principle (read first)

1. **Diversity within every region.** There is no single "Indian look" or "Asian look". India alone spans 28 states, 200+ languages (OED/CIIL sources, see sources.md) and skin tones from fair to very deep. A cast of 4 people from one country should not look like siblings.
2. **Every trait is a RANGE, not a RULE.** Region tells you what is common, never what is required. Individual people break every pattern. Never infer religion, caste, class, or nationality from a face. Specify the person, not the stereotype.
3. **No colourism.** Do not lighten, brighten or "glow" skin by default. Keep the skin tone you specified through the whole clip (video models drift lighter between frames; check).
4. **No caricature or exoticism.** No mystical, servile, comic, hyper-sexualised or "ancient wisdom" framing. People are doing ordinary things for ordinary reasons.
5. **No stereotyped behaviour.** Not every Indian is a call-centre agent, taxi driver or yogi; not every East Asian is a martial artist, geisha or maths prodigy; not every Southeast Asian is a vendor or tourist guide.
6. **Mark what is unverified.** Statements here are labelled (verified, estimate, unverified) in the reference files. Prompting behaviour differs by model and version; test before scaling.

## Workflow

1. **Specify the person** with the 8-slot sheet below (never skip skin, age, setting).
2. **Pick region ranges** from `references/regions-and-appearance.md` and choose ONE concrete point in each range.
3. **Add grooming and attire** from `references/hair-grooming-attire.md`; keep attire from one coherent tradition per outfit.
4. **Add expression** (`expressions-and-emotions.md`) at intensity 1 to 3, and motion (`body-language-and-motion.md`) for video.
5. **Dialogue/voice** (`speech-and-voice.md`) when lipsync is used.
6. **Start from a prompt** in `prompt-library.md`, then run its QA checklist before delivery.

## 8-slot character sheet

| Slot | Example (illustrative only) |
|---|---|
| Age and build | late 30s, lean, 5 ft 6 in |
| Region/background (specific) | Tamil Nadu urban, Chennai |
| Skin tone and undertone | deep warm brown, golden undertone, natural sheen, visible pores |
| Face | oval face, strong brow, broad nose bridge, full lips |
| Eyes | almond, deep-set, double lid, dark brown |
| Hair | black, wavy, shoulder-length, slightly oiled, centre parting |
| Attire and markers | cotton kurta, small stud, no bindi (state absence when relevant) |
| Setting, light, camera | window light, 85 mm, f/2.0, 4500 K |

Say what is ABSENT when a model tends to add it (bindi, tilak, turban, bangles, extra jewellery).

## Skin tone rules

- Describe with plain colour words plus undertone plus light behaviour (see regions file). Avoid scale numbers alone: Monk and Fitzpatrick scales are measurement aids, not prompt vocabulary, and Fitzpatrick is criticised as a poor skin-tone measure for non-white groups (Monk, 2023 sources). Use the Monk scale only for QA swatch checks.
- Expose for the skin, not the background. Deep skin needs soft, large, close light sources and a real highlight; flat dim light reads as muddy (cinematographer practice, Berkofsky 2017). Do not "fix" it by brightening.
- Same character across shots: repeat the identical skin phrase every time and use the same reference image.

## Hard avoid list

- Skin-lightening words as quality words: "fair", "glowing fair", "porcelain", "radiant white", "flawless" (unless the person is specified as light-skinned).
- "Exotic", "mysterious", "oriental", "slanted eyes", "almond-eyed beauty", "Asian features", "ethnic look".
- Costume mixing: sari with sherwani, kimono with hanbok, bindi on a non-Hindu or on a man by default.
- Sacred items as decoration (turban, patka, bindi, sindoor, tilak, wai, kimono) without a reason from the scene.
- Real identifiable people, real politicians, and minors in suggestive or beauty-retouch framing.

## Skincare and beauty ads (company context)

- Show a range of tones and ages. Show real texture (pores, fine lines, uneven tone); do not use before/after lightening visuals or imply a result.
- Claims, "brightening", "even tone" and efficacy visuals go to regulatory and cosmetic-science review, not to this skill. Flag any ad that implies lightening.
- Hair, scalp, lip and body-care ads should use varied hair textures and grooming, not one model type.

## When not to use markers

Skip bindi, sindoor, turban, kesh, tilak, hijab, wai, namaste, bow unless the story needs it and you can state context (who, why, occasion). Never use religious markers as a shorthand for "Indian" or "authentic". Details in `hair-grooming-attire.md`.

## References (open only when needed)

- `references/regions-and-appearance.md` skin, face, eyes, hair ranges by region; do-not list
- `references/hair-grooming-attire.md` hair, beards, bindi, jewellery, attire, religious markers
- `references/expressions-and-emotions.md` FACS action units, 1 to 3 intensity prompts, cultural cues
- `references/body-language-and-motion.md` gait, sitting, eating, space, micro-motion for video
- `references/speech-and-voice.md` accents, code-switching, honorifics, lipsync guidance
- `references/prompt-library.md` 25+ prompts and the QA checklist
- `references/sources.md` citations with dates and verification labels

## Sibling skills

`higgsfield-master` (platform, models, workflow), `photoreal-humans` (anatomy, skin texture, anti-AI-look). Linked by name only; this skill does not duplicate them.
