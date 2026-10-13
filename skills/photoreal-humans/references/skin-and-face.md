# Skin and face: what real people look like (researched 2026-10-13)
Labels: (V) vendor, (3P) third-party or beauty-brand source, (E) estimate or rule of thumb, (U) unverified. Use as vocabulary and a checklist; name features in prompts, do not rely on adjectives like "realistic".

## 1. Why AI skin goes plastic
Generators learn from heavily retouched photography, so they average away micro-texture, subsurface colour variation and directional falloff (3P, many guides agree). Beauty-tuned LoRAs, "cinematic" presets and words like flawless or glowing amplify it. Fix: ask for the specific features below, set the light, and check at 100% zoom.

## 2. Real skin anatomy as visual cues
| Feature | What it looks like | Prompt wording (positive) |
|---|---|---|
| Pores | Visible mostly on nose, nose wings, cheeks, forehead; larger on oily skin; absent on lips and eyelids | "visible pores across nose and cheeks, fine skin grain" |
| Vellus hair | Pale fuzz on cheeks, jaw, upper lip, forearms; catches rim light as a soft halo | "fine peach fuzz catching backlight along the cheek" |
| Specular breakup | Highlights are patchy and follow pore and fine-line structure, not a smooth gloss | "slight natural sheen on forehead and nose bridge, broken highlights" |
| Oil zones | T-zone, nose tip, chin shinier; cheeks and temples matter-er; dry skin has flaking and a flatter highlight | "slightly oily T-zone, matte cheeks" |
| Micro-imperfections | Tiny marks, uneven tone, faint scars, dry patches, small blemishes, fine lines at forehead, nasolabial fold, neck | "a few small blemishes, faint expression lines, uneven tone" |
| Under-eye | Thin skin, bluish or brown tint, fine crepey lines, tear trough shadow, puffiness varies by hour | "subtle under-eye texture and tint, faint tear-trough shadow" |
| Asymmetry | Eyes, brows, nostrils, mouth corners and smile differ left to right by small amounts | "natural left-right asymmetry, one brow slightly higher" |
| Freckles, moles | Irregular clusters, varied size, denser on nose bridge, cheeks, shoulders; moles are raised or flat, single | name one or two only, with placement |
| Redness | Cheeks, nose tip, around nostrils, chin, ears flush; capillary hints; post-blemish marks | "faint redness at nose wings and cheeks" |
| Translucency | Ear rims, nostrils, fingertips and lips glow warmer when backlit (subsurface light) | "ears glowing warm red from the backlight" |
| Neck and chest | Texture and tone differ from the face; neck creases, collarbone shadows | keep tone consistent but not identical to face |
| Body skin | Knuckle creases, elbow darkening, knees, visible veins on hands, tan lines | name 1 or 2 |
Rule: 3 to 5 imperfection cues per image is enough; stacking 10 produces dirty or diseased skin (E).

## 3. Makeup and grooming realism
Natural makeup is slightly uneven: blended edges that stop at the jaw, faint blush, a lip tint that fades at the edges, real brow hairs with gaps (E). Foundation settles into pores and fine lines at the end of a day. Bare-faced shots still show brow shape and lash clumps. Avoid perfect symmetric winged liner, porcelain base and mirror-matched lips.

## 4. Skin tone and undertone vocabulary
- Depth (how light or dark) and undertone (the hue underneath: warm golden or yellow, olive green-grey gold, neutral, cool pink or red) are independent; any depth can carry any undertone (3P, several beauty guides). State both.
- Fitzpatrick I to VI: built to predict UV burn and tan response in lighter skin, four of six types are light, and it is a weak descriptor of appearance (3P, dermatology literature). Use it only for sun-sensitivity context, never as the imaging brief.
- Monk Skin Tone scale: 10 open-source swatches with six for medium to dark skin, made for apparent tone in imaging; clinical validation is limited (3P). Use it to specify depth (for example "Monk 5 to 6") and to audit batches.
- Best practice: give depth word + MST range + undertone + light, then verify with a colour picker on the cheek in neutral light against a swatch or reference photo. Do not trust the model to hit the number.
| Depth word | Approx. MST (E) | Approx. Fitzpatrick (E) |
|---|---|---|
| fair or light | 1 to 3 | I to II |
| light-medium, light wheatish | 3 to 5 | III |
| medium, wheatish, golden tan | 5 to 6 | III to IV |
| medium-deep, dusky | 6 to 8 | IV to V |
| deep, dark brown | 8 to 10 | V to VI |
Mappings are estimates; the scales measure different things and do not align one to one.

## 5. Indian and South Asian skin (3P beauty-industry and bias-study sources; regional claims are tendencies, not rules)
For region-by-region ranges, attire, gestures and cultural QA load the `asian-human-reference` skill; this section only covers skin realism.
- Range is wide: from fair and light-wheatish to medium wheatish, dusky and deep brown. Tones tend to deepen toward the south and east, but every region holds the full range; never infer tone from a state or surname.
- Undertones: warm (golden, yellow, olive) is the most common in medium and deep tones; neutral is frequent in wheatish; olive is a muted green or grey-gold cast; cool or rosy undertones are real and often mislabelled. Test, do not assume warm.
- Descriptors to prompt: "medium wheatish skin with warm golden undertone", "deep brown skin with neutral-warm undertone and visible blue-red depth in the lips", "olive-tinted medium skin". Avoid vague "tan" or "ethnic".
- Typical real features: slight uneven pigmentation, darker periorbital and perioral areas, post-blemish marks, melasma-type patches, a gloss that shows clearly on the T-zone; natural vellus hair on upper lip, jaw and forearms; naturally pigmented lips, darker than the face on many people. Keep them; do not lighten or smooth them.
- Eyes: dark brown to near black irises with visible fibre texture and a limbal ring; do not default to light brown, green or blue.
- Hair: black to dark brown, often with a warm brown glint in sun, straight, wavy or curly, oil-sheen, scalp parting visible, grey strands for age; coils and curls need distinct strand clumping, not a smooth helmet.
- Cultural props (bindi, sindoor, mehndi, jewellery, saree, kurta) only when the brief asks and with correct placement; not every Indian subject needs them, and not as a shorthand for "Indian".

## 6. Avoiding whitewashing and plastic smoothing
- Evidence: a 2023 analysis of one generator found "woman" results for India and other countries at least two tone levels lighter than "person" results; another analysis found tone lightening as the prompt's education level rose (3P, a news analysis and a blog, small samples, model-specific). One SDXL study found a "person" prompt over-produced white faces (3P, peer-reviewed, older model). Treat as a reason to verify, not as a law.
- Prompt: state depth, MST range, undertone and ethnicity every time; add "natural skin tone preserved, no lightening, no skin whitening" in the constraints; keep tone words identical across a series.
- Avoid in prompts: fair and glowing, glass skin, porcelain, radiant fair, flawless, luminous fair, pale-washed (they push lightening or smoothing). "Luminous" is acceptable only with "natural oil sheen".
- Exposure: on deeper skin, expose for the face and keep a real key light; under-lit deep skin loses highlights and goes flat grey, and high-key or lifted-black grades can make brown skin ashy (E, photographic practice). Add a soft rim or kicker to show contour; keep saturation and warmth in the grade. Check white balance against a neutral grey in the scene.
- Edits and upscales: use reference-preserving editing; generative upscalers at high creativity can change skin tone, ethnicity or bone structure (3P). Compare tone patches before and after.
- Batch audit: for a set of N people, list the depth of each; if the set is uniformly light despite the brief, regenerate with explicit tone words.
- Retouching rule: skin tone and texture shown in a skincare context must not be altered to imply results; see ethics-and-consent.md.

## 7. Face structure
Adults show mature bone structure: defined jaw, nasolabial fold, subtle neck lines, brow ridge. Avoid the default AI face: huge symmetrical eyes, tiny nose, same lip shape, no ear detail. Vary lip volume and philtrum, nose width and bridge, ear shape (ears are rarely identical), hairline irregularity, brow thickness. Age cues: crow's feet, forehead lines, under-eye hollows, neck bands, hand veins, age spots; younger skin has fewer but not zero. Keep identity anchors (age range, 2 to 3 distinguishing features) front-loaded in the prompt.

## 8. Eyes
- Catchlights: shape and position come from the light source (window gives a soft rectangle, ring light a ring, softbox a square); two eyes show the same source in matching positions, slightly shifted by eye curvature. A beauty-dish clamshell is commonly lit for catchlights near 10 and 2 o'clock (3P). Prefer "muted, natural catchlights, no oversized glare" (house rule).
- Wet line: a thin bright meniscus along the lower lid and a shiny tear line at the inner corner; slight red at the caruncle.
- Sclera: off-white, not paper white; faint warm shadow under the upper lid; a few thin red vessels near the corners; tint varies with age and tiredness. Avoid glowing white sclera.
- Iris: radial fibre texture, a darker limbal ring, pupil round and centred, same size in both eyes. Dark brown irises still show texture when lit.
- Lashes and lids: uneven lash lengths, a few crossed or clumped, upper lid crease asymmetry, eyelid fold covering part of the iris top.
- Gaze: both eyes converge on the same target; a small off-camera gaze reads more candid than a dead-stare to lens.
- Glasses: frames cast a shadow and refract the eye edge; reflections match the scene.

## 9. Teeth, lips, mouth
- Teeth: slightly uneven edges, subtle colour gradient (warmer at gum line, a little translucent at the tips), visible gaps or a rotated incisor, a small shadow behind. AI tells: a continuous white band, too many teeth, identical rectangles. Fix: closed or slight smile, or inpaint the mouth.
- Lips: vertical creases, a darker line where they meet, a moist highlight on the lower lip, slightly different upper and lower lip colour; cupid's bow not symmetric. Do not smooth lip texture.
- Tongue and gums only when needed; gum tone varies with ethnicity and is often pigmented, which is normal.
- Facial hair: stubble has direction and density changes; beard edges are irregular.

## 10. Hair
Strands taper and cross; flyaways float off the crown and temples, with a few baby hairs at the hairline; roots are slightly darker; parting shows scalp; the hair edge against the background is soft with individual hairs, not a hard cut-out. Backlit hair gets a rim; oiled hair shows clumped glossy ribbons. Avoid a single glossy "helmet", hair that merges with a collar or ear, and symmetrical strand patterns. Facial and body hair follow the same rules.

## 11. Hands
- Count: five fingers per hand, thumb on the correct side, two hands unless one is out of frame. Joints: knuckle creases, bent fingers fold at joints, not like rubber.
- Skin: more veins, creases and tendons than face; nails with cuticles, slight ridges, uneven free edge, natural pink or polish with chips.
- Grip logic: fingers wrap an object with contact shadows and pressure whitening; no floating products; a hand never merges with a sleeve or cup.
- Prompt: "natural relaxed hands, five fingers each, visible knuckle creases, short natural nails", name each hand's job and contact point (consistent with the hand law in higgsfield-master). Prefer medium shots, hands partly out of frame, or simple poses (holding a jar by the lid) if hands keep failing; inpaint a bad hand instead of rerolling the face.

## 12. Posture and body
Weight shifts to one leg, shoulders unequal, head tilts, clothes wrinkle at joints and gather at the waist, jewellery sits on skin with a small shadow. Avoid stiff symmetrical poses, perfectly pressed fabric and identical left and right earrings unless the brief says so.

## 13. Imperfection budget (quick recipe)
Pick: 1 tone variation (redness or sun patch), 1 texture feature (pores or fine lines), 1 hair feature (flyaways or baby hairs), 1 asymmetry (brow or smile), 1 mark (freckle, mole or faint scar). Re-check after any edit pass.
