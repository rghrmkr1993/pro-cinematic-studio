---
name: story-and-screenplay
description: "Turns an owner's casual scene description, in any language including Tamil and Tanglish, into a story beat, a Fountain-format screenplay scene, a shot list, performance beats and model-ready video prompts, with a credit estimate before any spend. Use whenever the owner says things like 'scene where...', 'oru scene...', 'write a script', 'story idea', 'make a short film or ad scene', 'village love scene', 'fight entry', or pastes a rough scene. Covers logline, beats, scene craft, dialogue in spoken register, screenplay format, Indian cinema storytelling techniques, 6/15/30 second ad arcs and prompt writing for Higgsfield Seedance and Cinema Studio."
---

Part of the cinematic pipeline: entry point creative-studio

# Story and screenplay (casual scene to prompt)

Owner: screenwriter, with the cinematographer, performance-director and prompt-engineer for steps 5 to 7. This skill is the fast, default path for any scene the owner describes. It does not repeat the long-form method; it links to it.

## Link, do not duplicate
| Need | Open |
|---|---|
| Long-form workflow, Save the Cat table, AI-readiness pass | `../film-studio/references/story-and-script.md` |
| Faceless channel scripts | `../faceless-script-writer/SKILL.md` |
| Camera, lens, light, colour per shot; 512 check | `../cinematography/references/scene-to-shot-reasoning.md`, `../cinematography/references/prompt-compression.md` |
| Multi-shot timecoded Seedance prompts | `../higgsfield-timed-prompts/SKILL.md` |
| Acting, subtext, eyelines | `../performance-direction/SKILL.md` |
| Tamil, Telugu, Malayalam, Hindi, Kannada, Indian English | `../indic-languages/SKILL.md` (then its one language file) |
| Indian and Asian faces, attire, gestures | `../asian-human-reference/SKILL.md` |
| Credits and model choice | `../higgsfield-master/SKILL.md` (credits-and-budget.md) |

This skill's own references (open one per need, never all):
- `references/story-structure.md`: logline, premise, character, three-act, beats, sequences, payoffs, theme, short-film and ad structures.
- `references/scene-craft.md`: scene goal, conflict, turn, subtext, scene types, pacing, show-don't-tell checklist.
- `references/screenplay-format.md`: Fountain syntax, page = minute, dual-language and Tamil transliteration format.
- `references/dialogue-craft.md`: voice, subtext, spoken register, Indian patterns, Tamil, Telugu, Hindi naturalness.
- `references/indian-cinema-storytelling.md`: genre conventions as techniques: hero intro, interval, songs, climax, family themes.
- `references/casual-to-prompt-examples.md`: 6 worked examples from raw owner line to final prompts.

## Casual scene to prompt (mandatory 8-step protocol)
Run every step in order. Show each step's output in one compact block. Never skip step 8.

### 1. Listen and extract
Read the owner's words as they are, in any language or mix. Pull out: who, where, when, what happens, the feeling, and what was left unsaid (time of day, weather, clothing, relationship, ending, runtime, platform, language of dialogue).
- Fill every gap with the most cinematic sensible default and list the defaults in one line ("Assumed: dusk, rural Tamil Nadu, 20 s, 9:16, Tamil dialogue").
- Never interrogate. Ask at most one clarifying question, and only when the scene is truly ambiguous (two incompatible readings, or a missing fact that changes the story). Otherwise proceed.
- Keep the owner's own images and phrases; they are the seed. Do not replace their idea with a generic one.
- Originals only: no protected characters, worlds, lines, lyrics. If the owner references a famous scene, take the emotion and rebuild it with new people, place and words.
- Defaults when unsaid: platform Reels 9:16 for ads, 2.39:1 or 16:9 for film; India setting; no TikTok for Indian clients; runtime 5 to 15 s for a single beat, 30 to 60 s for a sequence.

### 2. Story beat
Write four lines: Goal (what the character wants in this scene), Obstacle (who or what blocks it), Turn (the moment the situation flips), Value shift (one value from plus to minus or reverse: hope to doubt, shame to pride, strangers to close). If nothing changes, the scene is not a scene; find the change or merge it into a neighbour. Detail in `references/scene-craft.md`.

### 3. Screenplay scene (Fountain)
Write the scene in Fountain: slugline, action in present tense with only what the camera can see, dialogue in natural spoken language (Tamil spoken, not written; see `references/dialogue-craft.md`). Enter late, leave early. Page count matches runtime (about 1 page per minute). For non-English dialogue use the dual-language convention in `references/screenplay-format.md` (native script, transliteration, English gloss). Dialogue is spoken-register and short; a shot rarely holds more than one line.

### 4. Shot breakdown
Cut the scene into shots, one action and one story change each. IDs follow `S<scene>-SH<nnn>` (for example S01-SH003). Row: ID, size and angle, duration (4 to 8 s per generated clip), subject action, story purpose. Wide to establish, medium to relate, close to feel, insert to prove. A shot that carries no change is cut.

### 5. Camera, lens, light, colour
Hand every shot to `cinematography/references/scene-to-shot-reasoning.md` (steps 3 to 11 and the emotion table). Return lens mm and aperture, one move with speed, key light with source and Kelvin, a two or three colour palette, realism cue. Hardware that lives in the Cinema Studio panel stays out of the prompt text.

### 6. Performance beats
For each shot with a face, add one line: the start emotion, the turn, the end emotion, the physical tell (eyes, breath, hands), and the eyeline. Use `performance-direction` for subtext and `asian-human-reference` for Indian expressions and gestures. Lines of dialogue are fixed text; the performer does not improvise them.

### 7. Model-native prompt per shot
Write each prompt in the target model's dialect (higgsfield-master references/model-dialects.md):
- Seedance multi-shot in one generation: use `higgsfield-timed-prompts` (timecoded shot headings, contiguous times, handles, fixed dialogue, SOUND list).
- Single Cinema Studio shot: subject and action first, camera in the first half, one move, one action, positive phrasing, then light, look, realism cue, audio.
- Pass the 512 check: save the prompt to a file and count it with Python (command in `prompt-compression.md`). 512 characters or fewer, minus about 90 per @ chip in Cinema Studio 2.5. Over budget: compress with the slot method or split into timed beats. Log the count on the shot row.
- State skin tone and region in every prompt with people; never lighten. Faces, wardrobe and product go to references, not words.
- Dialogue text stays in the owner's language inside the prompt where the model speaks it; everything else in English.

### 8. Show the owner, then wait
Present in chat, in this order: (a) defaults assumed, (b) the beat, (c) the Fountain scene, (d) the shot list with camera and performance lines, (e) the prompts with character counts, (f) the credit estimate, (g) the question "go?".
- Credit estimate: number of shots x expected draft runs (cap 3 per shot) x live per-run cost on the chosen model and tier, plus one final render per shot. Take the per-run cost from the live Higgsfield quote or credits-and-budget.md; never invent a price. Show balance if known. Label proofs versus finals.
- Do not generate, post or spend until the owner says yes. A changed quote needs a new yes.
- On yes, hand the locked pack to the prompt-engineer (generation) and log in the project `log.md`.

## Quality rules
- Spoken, not literary: read each line aloud; if a real person would not say it, rewrite it.
- Every scene: goal, obstacle, turn, value shift. Every shot: one action, one change.
- Show, do not tell: emotion lives in image, prop and behaviour first, words second.
- Cultural truth: names, kinship terms, festivals, food, clothing and speech match the region and class; use `asian-human-reference` and `indic-languages`. Do not caricature.
- Cosmetic and skincare scenes: no result claims, no before-and-after shown as real, no medical claims; the qualified team reviews claims before anything is published.
- Confidential: never paste unreleased formulations, customer data or one client's brand into another client's story.
- Safety: no real person's face or voice without written consent; no minors in romantic or violent scenes; no gore beyond what the platform allows.

## Output files (long-form or when asked to save)
`C:/Claude Code/company/creative/<client>/<project>/`: logline.md, treatment.md, beats.md, script.md, script-tamil-spoken.md when Tamil is needed, shot list, prompt pack. For a single casual scene, chat output is enough unless the owner asks for files.

## Gate before handing on
Scene has a visible turn; dialogue passes the read-aloud test; every shot has an ID and a prompt count at or under its limit; defaults stated; credit estimate shown; owner yes received.
