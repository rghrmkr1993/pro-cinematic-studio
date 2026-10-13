# Realism QA checklist: 28 tells, scored (researched 2026-10-13)
Labels: (3P) from detection and fix guides, (E) rule of thumb. Detection guides note that obvious tells like six fingers and garbled text are now rarer in current models, so clean hands or eyes prove little: inspect at 100% zoom and stress areas (background text, ears, hands in motion, reflections). No single tell proves anything; score the set.

## How to score
Score each tell 0 (clean), 1 (minor, visible only when zoomed), 2 (obvious at normal size). Stills: items 1 to 22. Video adds items 23 to 28. Items marked * are critical.
- PASS: total 6 or less on stills, and no critical item scored 2.
- REPAIR: 7 to 14, or any critical item at 2: fix the worst two tells by edit, then rescore (max 2 repair rounds).
- REDO: above 14, or 3 or more tells at 2: rewrite the prompt, change model or restart from references.
Video: PASS 10 or less across 1 to 28 with no critical at 2, scored on a frozen frame at the start, the 5 to 8 s mark and the end, plus one real-speed viewing.
Record: score, worst tell, fix, version, in the asset log.

## Skin and face
| # | Tell | Check | Fix |
|---|---|---|---|
| 1* | Plastic or waxy skin | Pores on nose and forehead visible at 100%? highlights patchy? | Add pore, fine-line, sheen cues; drop beauty words; inpaint face; lower upscale creativity; add grain; try Seedream 4.5 or Soul |
| 2 | Over-smooth gradient, airbrushed cheeks | Tone changes smoothly with no redness, freckles, under-eye tint | Add 3 to 5 imperfection cues; redness and texture masks; local texture blend from original |
| 3* | Perfect symmetry | Mirror the face: do halves match? | Add "natural left-right asymmetry"; vary brow, smile, nostril; change seed or angle to three-quarter |
| 4 | Generic AI face, same beauty template | Large eyes, tiny nose, identical lips across a batch | Specify age, bone structure, nose and lip shape, distinguishing marks; use a reference |
| 5* | Wrong or lightened skin tone | Cheek colour vs brief swatch; does batch drift lighter? | State depth, undertone, MST range; "no lightening"; edit tone locally; avoid fair and glowing words |
| 6 | Grey or ashy cast on deeper skin | Highlights flat, shadow chalky | Re-light with a key and warm rim; remove lifted blacks; expose for face |
| 7 | Flat uniform skin tone across face, neck and hands | Neck or hands a different material | Match undertone, add neck creases, vary redness by zone |
| 8 | Missing vellus hair and sheen | No halo in backlight, no oil zone | Add "peach fuzz in backlight", T-zone sheen |
| 9 | Hair helmet, merged hair edge | Hair edge cut out, no flyaways, merges into collar or ear | Add flyaways, baby hairs, partings; inpaint edge; soften background separation |

## Eyes, mouth, hands
| # | Tell | Check | Fix |
|---|---|---|---|
| 10* | Dead eyes or glassy stare | No wet line, iris texture flat, catchlight absent or huge | Name the light source for the catchlight; wet meniscus; small gaze offset; muted catchlights; inpaint eyes |
| 11 | Catchlights mismatch between eyes or the scene | Two different shapes or sources | One named source; fix by inpainting both eyes in one pass |
| 12 | Pupils unequal, eyes diverge, wrong iris colour | Zoom to the irises | Inpaint eyes; keep brief colour (dark brown default for Indian subjects, avoid light eyes) |
| 13 | Sclera too white, no veins | Glowing paper-white | "off-white sclera, faint vessels" |
| 14* | Teeth wrong: too many, a single white band, melted | Count visible teeth | Closed or slight smile; inpaint mouth; mention slight unevenness |
| 15 | Lips smooth and painted | No creases, same colour top and bottom | Add vertical creases, tint gradient, moist highlight |
| 16* | Hands wrong: extra or fused fingers, rubbery joints, wrong thumb | Count, check knuckles and nails | Hands out of frame or simple pose; inpaint hand only; name contact points; medium shot |
| 17 | Floating grip, product not held, hand merges with object or sleeve | Contact shadows, pressure | Define each hand's job; "fingers wrap the jar"; add contact shadow; reference |

## Light, optics, scene
| # | Tell | Check | Fix |
|---|---|---|---|
| 18* | Impossible or mixed light | Shadows disagree, face lit but scene dark, no shadow under chin | Name one source and direction; relight or composite; match WB |
| 19 | Fake depth of field: blur ignores depth, hair or glasses halo | Edge blur around hair, mismatched focus plane | Specify aperture and lens; deep focus for UGC; inpaint edges |
| 20 | HDR glow, oversharpen, halo, oily gloss | Crunchy edges, bright rim around subject | Remove "enhance" passes; reduce sharpening; neutral grade; grain |
| 21* | Text gibberish or warped label | Zoom into signs, packs, tattoos, clothing prints | Keep scene text-free and overlay; use a text-capable model for in-frame copy; reference the real pack |
| 22 | Background logic: repeated patterns, melted objects, impossible architecture | Scan edges and background props | Simplify the set with 3 anchors; inpaint; blur honestly; use a location reference |

## Video-only
| # | Tell | Check | Fix |
|---|---|---|---|
| 23* | Uncanny motion: statue head, floating face, rubbery morph | Watch at speed; face versus neck motion | Small staged micro-actions; shorter clip; start from a stronger still; change motion model (Kling or Veo for faces) |
| 24 | Blink wrong: none, constant, regular or asymmetric | Count blinks over 10 s (rest about 15 per min; talking 25 to 30+) | "blinks naturally at pauses"; reroll; reduce motion energy |
| 25 | Lip sync off, jaw mismatch, no plosive closure | Mute and watch mouth on p, b, m | Native-audio model or Lipsync tool; front-facing mouth uncovered; short line (about 35 words per 15 s) |
| 26 | Identity or skin tone drift between cuts, or mid clip at 5 to 8 s | Compare first, mid, last frame | Element or Soul ID; last-frame chaining; shorter clips; lock tone words |
| 27 | Motion blur, shutter and camera feel wrong (smooth gimbal for a "handheld" claim, no blur on fast moves, rubbery rolling shutter) | Fast move frames | Specify 180 degree shutter, handheld micro-sway, rolling-shutter skew only on fast pans |
| 28 | Cloth and hair physics wrong, clipping, no breathing | Chest and shoulders still, hair rigid | Add breath and weight shift; reduce speed; mention hair lag |

## Product, cosmetic and compliance tells (score as part of the set)
Count these as extra points on the same 0 to 2 scale; any critical (marked *) at 2 blocks release.
| # | Tell | Fix |
|---|---|---|
| P1* | Product shape, cap or label wrong, duplicated product | Packshot reference; one hero product; frozen-frame check; composite label |
| P2 | Texture not honest to the real product (cream, oil, lather, colour) | Match to a lab or photo reference; reshoot or restyle; ask the formulation owner |
| P3* | Skin result implied: smoother, brighter, fairer after use | Remove; real consented footage or none; qualified review |
| P4* | Synthetic person shown as a real customer, doctor or reviewer | Remove; use a labelled brand character; see ethics-and-consent.md |
| P5* | Missing AI label or provenance where required | Apply platform and ASCI or EU labels; keep C2PA metadata |

## Quick triage order
1. Skin tone and plastic skin. 2. Eyes. 3. Hands. 4. Teeth. 5. Light. 6. Text and product. 7. Motion and blink. 8. Continuity. 9. Compliance. Fix in that order because early-stage fixes change later ones; re-check skin after every edit.

## Provenance and false confidence
Passing this checklist means "looks real", not "is real" and not "is allowed". Realistic synthetic people still need consent, labels and honest claims. Detection heuristics are weak evidence either way; do not use them to assert a competitor or person is fake.
