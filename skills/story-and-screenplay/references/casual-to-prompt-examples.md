# Casual to prompt: 6 worked examples

Each: raw owner line, defaults assumed, beat (steps 1 and 2), Fountain scene (3), shot list with camera and performance (4 to 6), prompts with Python character counts (7). Step 8 (show the owner, estimate credits, wait for yes) follows each; estimates use the live quote, so none is invented here. All characters, places and lines are original; no brand names. Counts measured with `len(open(f,encoding='utf8').read().strip())`; every prompt is at or under 512 characters. Prompts with @ chips in Cinema Studio 2.5 lose about 90 per chip, so these use none.

## 1. Village love scene
Raw: "village la oru girl well kitta thanni edukka varaa, hero paakuran, avaluku theriyum aana paakala maari irukka. oru soft feel venum, 15 sec"
Defaults: dawn, rural Tamil Nadu, 9:16, spoken Tamil, no song, 2 characters.
Beat: Goal she wants water and to hide she noticed him. Obstacle her shyness, his boldness. Turn his hand catches the rope above hers. Shift strangers to spark.
```
EXT. VILLAGE WELL - DAWN #1#

MEENA (22), cotton saree, brass pot on hip, draws the rope. ARUN (25), checked lungi, towel on shoulder, leans at the tea stall.

                    ARUN
(Tamil)
நான் இழுக்கவா?
Naan izhukkava?
[EN: Shall I pull?]

She will not look up. The rope slips; his hand catches it above hers. Both freeze. She hides a smile in her pallu.
```
| ID | Frame, lens | s | Action and performance |
|---|---|---|---|
| S01-SH001 | Wide, 28mm, locked | 5 | Well, mist, her pot; calm, eyes down |
| S01-SH002 | CU, 85mm f/1.4, slow push-in | 5 | Her glance to him then away; start guarded, turn a flicker, end hidden smile |
| S01-SH003 | Insert, 100mm macro, locked | 4 | Two hands on one rope; his steady, hers trembling |

Prompt S01-SH002 385 chars:
```
Close-up, 85mm f/1.4, slow push-in over 4s. A young Tamil woman, deep brown skin, in a cotton saree, glances right at a man off-screen, then lowers her eyes and hides a smile in her pallu. Village well, brass pot, rising mist. Low golden sun behind her, 3800K rim on her hair, soft warm bounce. Warm film grain, natural skin texture, soft breath. Distant rooster, rope creak, no music.
```
Prompt S01-SH003 338 chars:
```
Macro insert, 100mm, locked. Two hands on a wet coir rope at a village well: a man's steady hand catches the rope just above a young woman's trembling hand, both freeze. Brown skin, brass bangle, rope fibres, water drops. Soft golden dawn side light, 3800K, shallow focus. Warm grain, natural skin pores. Water drip, rope creak, no music.
```

## 2. Father and son argument
Raw: "appa um son um fight, son city job ku pogaporaan, appa kovam but sollave mattaar. dinner time. sad ah mudiyanum"
Defaults: night, middle-class Tamil home, 16:9, 30 s, spoken Tamil, warm tungsten.
Beat: Goal son wants his father's blessing; father wants him to stay but hides fear as anger. Turn father serves him another dosa and his voice breaks. Shift defiance to guilt and love.
```
INT. KITCHEN, SMALL HOUSE - NIGHT #2#

RAVI (26), office shirt, bag by the door, stands. SELVAM (55), faded vest, spectacles on his nose, tears a dosa without looking up.

                    SELVAM
(Tamil)
போறேன்னு சொல்லாத டா. போயிட்டு வரேன்னு சொல்லு.
Poren-nu sollaadha da. Poittu varen-nu sollu.
[EN: Don't say "I'm going". Say "I'll go and come back".]

Ravi's jaw loosens. Selvam puts one more dosa on his plate.
```
| ID | Frame, lens | s | Action and performance |
|---|---|---|---|
| S02-SH001 | Medium two-shot, 35mm, locked | 6 | Table between them; father eats, son stands; stiff |
| S02-SH002 | CU father, 85mm f/2, slow push-in | 6 | Eyes on the dosa; anger, then voice cracks; never meets son's eyes |
| S02-SH003 | Insert plate, 50mm | 4 | Extra dosa lands on the plate; the unspoken yes |

Prompt S02-SH002 434 chars:
```
Close-up, eye level, 85mm f/2, slow push-in over 6s. A 55-year-old Tamil man, dark brown weathered skin, grey stubble, spectacles, faded vest, tears a dosa and speaks low without looking up; his jaw tightens and his voice cracks. Small kitchen, steel plates, steam. Warm 3200K tungsten overhead, cool blue window fill. Muted amber grade, fine grain, natural pores. He says in Tamil: "Poittu varen-nu sollu." Quiet room tone, no music.
```
Prompt S02-SH003 291 chars:
```
Insert, high angle, 50mm, locked. A weathered hand places a fresh dosa on a steel plate beside a half-eaten one, steam rising. Steel plate, chutney bowl, wooden table. Warm 3200K tungsten from above, soft shadows. Amber tones, fine grain, visible knuckle creases. Soft plate clink, no music.
```

## 3. Skincare ad (generic product, no claims)
Raw: "skincare ad, girl morning routine, calm, product soft touch. results pathi onnum sollathe. 15 sec reels"
Defaults: 9:16, 15 s, urban India, one woman, no brand name, product from the client's reference image, no result claims, English voiceover.
Beat: Goal one calm minute before the day. Obstacle phone buzzing, rush. Turn she turns the phone face down. Shift rushed to calm.
```
INT. BATHROOM, SMALL FLAT - MORNING #3#

PRIYA (28), hair in a clip, phone buzzing on the shelf. She turns it face down. Smooths a cream onto her cheek and breathes out.

                    PRIYA (V.O.)
One minute that is only yours.
```
| ID | Frame, lens | s | Action and performance |
|---|---|---|---|
| S03-SH001 | MCU, 50mm, locked | 4 | Phone buzzes; her shoulders tense |
| S03-SH002 | Macro, 100mm, slow dolly in | 5 | Fingertip lifts cream from the jar; texture only |
| S03-SH003 | CU, 85mm, static | 6 | Cream on cheek, long exhale, eyes close; calm |

Prompt S03-SH002 344 chars:
```
Macro, 100mm f/4, slow dolly in over 4s. A woman's fingertip lifts a soft cream from a small white jar, the surface folds and holds peaks. Pale stone shelf, blurred green plant. Soft window light from left, 5000K, gentle highlight on the cream. Cream and sage palette, fine grain, natural skin pores on the finger. Soft jar-lid click, no music.
```
Prompt S03-SH003 327 chars:
```
Close-up, 85mm f/1.8, static. A South Asian woman, medium brown skin, hair in a clip, smooths cream onto her cheek and exhales slowly, eyes closing. Bright airy bathroom, soft tile blur. Soft window key from left, 5000K, warm bounce. Cream and sage palette, fine grain, unretouched skin, light sheen. Quiet room tone, no music.
```

## 4. Fight entry
Raw: "mass fight entry, hero mazhai la nadandhu varaan, 5 rowdies wait panraanga, avan umbrella close pannitu adikkanum. slow motion, goosebumps"
Defaults: night, wet street, Chennai, 2.39:1, 12 s, one line in Tanglish-style spoken Tamil, teal and amber.
Beat: Goal reach the shop and protect the owner. Obstacle five men. Turn he folds the umbrella (the hit comes next). Shift threat to control.
```
EXT. MARKET STREET - NIGHT, RAIN #4#

Five men block the road. KARTHIK (30), black shirt, one black umbrella, walks through the rain without hurrying.

                    KARTHIK
(Tamil)
மழை நிக்கட்டும். அப்புறம் பேசலாம்.
Mazhai nikkattum. Appuram pesalaam.
[EN: Let the rain stop. We can talk after.]

He folds the umbrella. Water falls off it like a signal.
```
| ID | Frame, lens | s | Action and performance |
|---|---|---|---|
| S04-SH001 | Wide low, 24mm, locked | 4 | Five men on the road; he enters frame calm |
| S04-SH002 | Medium low, 35mm, slow push-in | 5 | Walk, stop, line; cold eyes, no blink |
| S04-SH003 | Insert, 50mm, 120fps look | 3 | Umbrella closes; water sheets off |

Prompt S04-SH002 424 chars:
```
Medium shot, low angle, 35mm, slow push-in over 5s. A broad Tamil man, dark brown skin, black shirt, black umbrella, walks down a rain-soaked Chennai street, stops, and says in Tamil: "Mazhai nikkattum. Appuram pesalaam." Cold unblinking stare. Sodium streetlights, shuttered shops, wet asphalt. Backlit rain, 2200K sodium glow, cyan sign spill. Teal and amber, fine grain, wet shirt weight. Rain, distant thunder, no music.
```
Prompt S04-SH003 285 chars:
```
Insert, 50mm, locked, 120fps slow motion. A black umbrella folds shut and a sheet of water falls from its ribs in slow motion. Rain-lit street blurred behind, neon smear. Backlit sodium glow 2200K, cyan edge on the droplets. Teal and amber, fine grain. Deep thump, rain hiss, no music.
```

## 5. Rainy bus-stop meet (Tanglish input)
Raw: "bus stop la mazhai, oru ponnu oru paiyan, umbrella onnu dhaan irukku, share panraanga, cute ah irukkanum, 10 sec"
Defaults: evening, Chennai bus shelter, 9:16, 10 s, Tanglish, strangers, yellow kurta and grey shirt.
Beat: Goal both want to get home dry. Obstacle one umbrella, strangers. Turn she steps under it. Shift strangers to shy ease.
```
EXT. BUS STOP, RAJAJI SALAI - EVENING #5#

Rain on a tin shelter. KAVYA (24), yellow kurta, laptop bag. ARUN (26), grey shirt, a torn umbrella.

                    ARUN
(Tanglish)
Umbrella-la jaaga irukku. Vaanga.
[EN: There's room under the umbrella. Come.]

She hesitates, then steps in. Her bag brushes his arm. Both stare at the road.
```
| ID | Frame, lens | s | Action and performance |
|---|---|---|---|
| S05-SH001 | Wide, 28mm, locked | 3 | Shelter, rain, two strangers apart |
| S05-SH002 | MCU two-shot, 50mm, slow push-in | 7 | He offers; she steps in; awkward, hidden smiles |

Prompt S05-SH002 415 chars:
```
Medium close-up two-shot, 50mm f/2, slow push-in over 6s. A young Indian man in a grey shirt tilts a torn umbrella toward a young woman in a yellow kurta with a laptop bag; she steps under it and both stare ahead, hiding smiles. Rainy Chennai bus shelter, wet road, blurred headlights. Soft blue dusk, warm shop-light bounce 3200K. Teal and amber, fine grain, natural skin. Rain on tin roof, one bus horn, no music.
```

## 6. Fantasy kingdom opening
Raw: "fantasy kingdom opening, floating islands, small princess running on a bridge, sunrise, wonder feel. original da, no copy"
Defaults: sunrise, painterly 3D animation, 16:9, 12 s, no dialogue, wonder.
Beat: Goal reach the highest tower to see sunrise. Obstacle the guard bell. Turn she reaches the edge as the sun lifts the kingdom. Shift confined to awe.
```
EXT. SKY BRIDGE, FLOATING KINGDOM - SUNRISE #6#

ILA (10), cream cloak, bare feet, runs along a rope bridge between floating islands. A bell tolls below. She does not stop.

                    ILA
(whispers)
Almost there.

She reaches the edge. The sun clears the clouds and the whole kingdom lifts into gold.
```
| ID | Frame, lens | s | Action and performance |
|---|---|---|---|
| S06-SH001 | Extreme wide, 18mm virtual, crane up | 6 | Islands, bridge, tiny runner; curiosity |
| S06-SH002 | Side track, 35mm virtual | 4 | Running, cloak flying; joy, urgency |
| S06-SH003 | CU, 50mm virtual | 3 | Face in sun; awe, mouth open |

Prompt S06-SH001 379 chars:
```
Extreme wide, 18mm virtual lens, slow crane up over 6s. A tiny girl in a cream cloak runs across a rope bridge between floating stone islands with waterfalls and cloud seas below. Pastel towers, hanging gardens, drifting petals. Warm sunrise rim light, rose and gold sky, soft volumetric shafts. Painterly 3D animation, jewel palette, deep focus. Wind and distant bell, no music.
```
Prompt S06-SH003 348 chars:
```
Close-up, 50mm virtual lens, locked. A ten-year-old girl with warm brown skin and a cream cloak stands at a cliff edge, sunlight washing her face, mouth opening in wonder, eyes wide. Golden clouds behind, drifting petals. Warm sunrise key from front-left, rose rim light. Painterly 3D, jewel palette, soft depth of field. Soft wind swell, no music.
```

## Notes
- Defaults are stated once; change them on the owner's reply, then recount prompts.
- Any prompt over 512 characters is compressed with `prompt-compression.md` or split into timed beats via `higgsfield-timed-prompts`.
- Dialogue stays in the model's prompt only where the clip speaks it; glosses never go into a prompt.
- Claims: example 3 shows texture and ritual only; any benefit claim goes to the qualified team first.
