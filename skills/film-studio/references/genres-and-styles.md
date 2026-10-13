# Genres and styles (prompt vocabulary and models)

Rule: choose ONE style family per film and write it into the style bible (bibles-and-continuity.md). Style words are inspiration, not imitation: describe qualities (line weight, light, texture), never name a living studio, artist, film, franchise or character as the target (delivery-and-legal.md section 3). Models: 3P, 2026-10-13, confirm on the Generate button; model dialects in higgsfield-master model-dialects.md. Style packs to open once: `02-3d-cgi`, `03-cartoon`, `08-anime-action`, `01-cinematic`, `10-music-video`, `04-comic-to-video`. Camera words: `cinematography` skill, signature-shots.md.

## 1. 3D feature animation (original characters, family tone)
- Vocabulary: stylised proportions, large expressive eyes, soft subsurface scattering, rounded forms, physically based materials, volumetric light, warm bounce light, shallow depth of field, clean render, appeal-driven design, squash and stretch on faces, rich environment set dressing, painterly textures on backgrounds, colour script per act.
- Negatives: photoreal skin pores, uncanny realism, text, extra fingers, plastic toy look when not wanted.
- Model: Seedance 2.x or 2.5 for multi-reference shots; Kling 3.0 for iteration; Cinema Studio for lens control. Character model sheet, turnaround and expression sheet are mandatory. Check hand and mouth shape fidelity.
- Pitfalls: faces drift into other animation looks; keep one render look; avoid existing studios' character archetypes and signature designs (a clownfish hero, a blue tall alien race with tails and neural braids, a sheriff toy: do not echo protected designs).
- Pacing: ASL 4 to 7 s, songs or montage at the midpoint, held emotional close-ups.

## 2. Anime (original design)
- Vocabulary: cel-shaded, flat colour with painted backgrounds, bold line art with variable line weight, limited animation held frames, impact frames, speed lines, sakuga bursts for action, large eyes with highlights, wind in hair and cloth, dramatic low-angle, sunset gradient skies, bokeh lights, 2D compositing look, film grain light.
- Subgenres: shonen action, seinen drama, slice of life, mecha, isekai, magical girl, sci-fi noir.
- Model: Seedance 2.x anime packs (`08-anime-action`), Kling 3.0 for dynamic action; character sheet with fixed hair shape, eye design and palette. Keep series continuity with a consistent colour script.
- Writing: kishotenketsu or episodic arcs, silent beats; do not use any existing series' names, techniques names or costumes.

## 3. 2D cel and hand-drawn
- Vocabulary: hand-drawn, traditional cel animation, ink and paint, visible line boil, watercolour backgrounds, 12 fps on twos, gouache or painted multiplane depth, limited palette, storybook illustration, rotoscope look as a variant.
- Model: Seedance 2.x (cartoon pack `03-cartoon`), Kling 3.0; for painterly styles use style frames as references and reuse the same brushwork and palette. Risk: line weight and colour inconsistency; fix the model sheet.
- Variants: flat vector motion graphics, paper cut-out, shadow puppet (traditional leather puppet looks for Indian epics, original designs).

## 4. Stop-motion and clay looks
- Vocabulary: stop-motion animation, claymation, plasticine, visible fingerprints, handmade miniature sets, practical lighting, 12 fps stepped motion, felt and wool textures, macro tabletop depth, slight inconsistency in motion, armature posing.
- Model: Seedance 2.x or Kling 3.0 with style frames; add stepped frame rate in post (`fps=12` then up to 24 with frame duplication) for authenticity: `ffmpeg -i in.mp4 -vf "fps=12,fps=24" out.mp4`. Do not copy any known clay or puppet character.

## 5. Photoreal drama (live-action look)
- Vocabulary: shot on 35 mm, anamorphic or spherical lenses, natural light, practical lights, motivated lighting, handheld or locked tripod, shallow depth of field, film grain, skin texture with pores, muted palette, subtle halation, realistic wardrobe wear, ambient sound.
- Realism tells: load `photoreal-humans` (28 tells) and `asian-human-reference` for Indian and Asian casts.
- Model: Veo 3.1 for hero close-ups, Seedance 2.x for scene work, Kling 3.0 for iteration; Soul ID or Soul Cast for faces; Cinema Studio camera and lens controls. Keep close-ups of speaking faces under 8 s.
- Pacing: ASL 6 to 9 s; masters, singles, insert; quiet performance beats.

## 6. Period pieces (any era): research pipeline
1. Define era and place to the decade and region (not just "ancient India"): social class, occupation, season.
2. Research sheet per category with at least two sources (museum collections, archives, scholarly books, official heritage bodies, period photographs, paintings): costume (fabric, cut, colour, drape style, jewellery, hair, footwear), architecture (materials, roof forms, doorways, columns, scale), interiors (furniture, lighting source: oil lamp, candle, gas, electric), props (tools, weapons, writing, vessels), transport, street life, signage and script, food service, weather.
3. Anachronism list: what must NOT appear (plastic, zippers, modern bulbs, wires, concrete in ancient scenes, modern fonts, English where the era used another language). Add to the negative list.
4. Colour and material: natural dyes, hand-loom textures; pre-synthetic palettes; metals and patina.
5. Language register: archaic versus modern speech; script of the era; names of the period.
6. Visual references: 6 to 12 licensed or original period-accurate reference images, saved in the bibles; do not use a copyrighted film still as a reference input.
7. Cultural and religious sensitivity review (qa-tester plus a subject adviser for sacred or contested material); epics and mythology: do not caricature deities, respect depiction norms (E), involve a cultural adviser; flag for legal.
8. Verify the output: check costume, architecture and props against the research sheet per shot, not once per film.
Era presets: ancient (stone, mud brick, lamp light), classical or medieval (temple, fort, palace, handloom, bronze), colonial (railways, steam, gas lamps, uniforms), early 20th century (black and white to early colour, gramophone, tram), mid-century (1950 to 1970: film stock, Ambassador-like cars as generic vintage, radio), 1980s to 1990s (CRT TVs, landline, film grain, Kodak-like warmth), contemporary, near future, far future. Era control in Cinema Studio (grain, grade, lens, 3P).

## 7. Epic sci-fi and fantasy
- Vocabulary: epic scale, wide establishing shots, volumetric god rays, atmospheric haze, practical plus CG plates, matte painting, hard-surface design, creature design with weight, magic with a physical rule and a colour, banners and heraldry, armour wear, cinematic score cue sheet.
- World bible first: rules, cost of magic or technology, three visual motifs, design language per culture.
- Model: Seedance 2.x or 2.5 for large multi-reference scenes, Veo 3.1 for hero landscapes, Kling 3.0 for creature action; build environment plates first; non-human leads need a turnaround sheet and a motion rule.
- Avoid: protected creature or species designs, named races, ship designs, or magic systems from existing franchises.
- Pitfalls: crowd and armies morph; stage in wide silhouette and use cutaways.

## 8. Documentary-style film
- Vocabulary: handheld verite, natural light, interview framing (MCU, off-axis, shallow background with practical lights), archival look (grain, scratches, 4:3), b-roll cutaways, location establishing, graphics inserts, voice-over narration, ambient sound.
- Ethics: a documentary look with invented people or events must be labelled as a dramatisation or fictional; no fake interviews of real persons; YouTube altered or synthetic content label applies to realistic fabrication (delivery-and-legal.md section 5). Recreations clearly marked.
- Model: Veo 3.1 or Seedance for realism, voice for narration with consent, text overlays added in the edit.

## 9. Music film and music video features
- Vocabulary: performance coverage, rhythm-driven cuts, choreography with named steps and counts, lighting cues synced to beat, wardrobe changes per song, set pieces, lip-sync alternatives, lyric visualisation.
- Model: Seedance (`10-music-video` pack), Kling for dance with Motion Control; audio first, beat map, then shots.

## 10. Style selection quick table
| Film type | Family | First model to test | Reference sheets needed |
|---|---|---|---|
| Family animated feature | 3D feature animation | Seedance 2.x | model sheet, expressions, hands, environments |
| Anime series or film | Anime | Seedance 2.x anime | face angles, hair, costume, palette |
| Storybook or hand-drawn | 2D cel or painterly | Seedance 2.x | style frames, line weight sheet |
| Craft look | Stop-motion, clay | Seedance 2.x or Kling | set plates, material macros |
| Human drama | Photoreal | Veo 3.1 plus Seedance | Soul ID, wardrobe plates, location plates |
| Epic | Sci-fi or fantasy | Seedance 2.5 | world bible, creature sheets, plates |
| Period | Photoreal or painterly | Seedance plus Veo | research sheets, era plates |
| Documentary style | Verite | Veo 3.1 | interview subjects (consented or fictional), plates |
| Music film | Performance | Seedance, Kling | performers, beat map, set pieces |
Always run a calibration scene (3 to 5 shots including the hardest) in the chosen style before committing the film.
