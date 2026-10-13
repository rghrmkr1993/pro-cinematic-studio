---
name: cinematography
description: "Shot list and storyboard templates for AI video with columns for shot ID, size, angle, lens, move, light, duration, dialogue, prompt and model, plus three worked example scenes: a dialogue drama, an action chase and a product hero. Part of the cinematography skill."
---

# Shot list and storyboard templates
Labels: (H) house format, (K) craft. All example content is client-neutral and invented. Replace names, products and places per project. Times are planning values; actual clip length depends on model limits (Veo 4, 6 or 8 s; Cinema Studio 4.0 up to 30 s, V).

## Template A: shot list (markdown table)
| ID | Beat | Size | Angle | Lens | Move | Light | Dur | Dialogue / sound | Prompt | Model |
|---|---|---|---|---|---|---|---|---|---|---|
Fill order: Beat (story change), Size, Angle, Lens and aperture, Move with speed and endpoints, Light (source, direction, K), Duration, Dialogue and SFX, final prompt, model plus settings.
Extra optional columns: Start frame ref, End frame ref, Element tags, Screen direction, Status (draft, locked, final), Notes.

## Template B: storyboard card
```
SHOT 03  |  Scene 1 INT KITCHEN NIGHT
Image slot: [frame ref or sketch]
Beat: She decides to leave.
Frame: MCU, eye level, 50mm f/2, thirds, looking frame right (lead room)
Move: slow push-in 4 s, hold 1 s
Light: single hanging bulb 2900K, low key, haze
Audio: fridge hum, "I'm done." (line)
Continuity: A frame left, B frame right (180 line at table); same wardrobe
Prompt: ...
Model: Veo 3.1, 8 s
Checks: hands, eyeline, left-right
```

## Template C: sequence overview
| Scene | Place and time | Beats | Shot count | Palette | Light key | Look |
|---|---|---|---|---|---|---|

## Template D: continuity pack (build before shooting)
- Subject references (front, 3/4, profile), wardrobe locked.
- Location reference frames (wide, two angles) and light direction.
- Palette (3 colors), stock and grain choice, lens family, aspect ratio.
- Negative or constraint tail: "no text, no watermark, no extra fingers, no morphing, no duplicate product." (V Higgsfield visual language note)

## Worked scene 1: dialogue drama (INT. KITCHEN, NIGHT)
Premise: two siblings, MARA and DEV, argue over selling the family home. One location, one lamp, 7 shots. Palette: warm amber lamp against deep blue window. Look: Vision3 500T style, fine grain. 180 line along the table: Mara frame left, Dev frame right. 24 fps look.
| ID | Beat | Size | Angle | Lens | Move | Light | Dur | Sound | Model |
|---|---|---|---|---|---|---|---|---|---|
| 01 | Establish room | WS | Eye | 28mm f/4 | Locked-off | Hanging bulb 2900K, blue window ambient | 5 s | Fridge hum | Veo 3.1 |
| 02 | Tension at table | Two-shot MS | Eye | 40mm f/2.8 | Very slow push-in | Same | 6 s | Chair creak | Cinema Studio |
| 03 | Mara states plan | MCU Mara | Eye, slightly high | 85mm f/2 | Locked | Key from lamp camera left, soft | 6 s | "We have to sell it." | Veo 3.1 |
| 04 | Dev reacts | MCU Dev | Eye, slightly low | 85mm f/2 | Locked | Lamp rim, face half shadow | 5 s | silence | Veo 3.1 |
| 05 | Insert: keys on table | ECU | High | 100mm macro f/2.8 | Locked | Pool of lamp | 3 s | Metal clink | Image to video |
| 06 | Dev answers | CU Dev | Slightly low | 85mm f/1.8 | Slow push-in 2 s | Low key | 6 s | "Dad built this." | Veo 3.1 |
| 07 | Mara leaves, empty chair | WS | Eye | 28mm | Slow pull-out | Window blue dominant | 6 s | Door click | Cinema Studio |
Prompt example (shot 03): "Medium close-up, eye level, 85mm, f/2. A woman in a gray cardigan sits at a wooden kitchen table and says, 'We have to sell it.' Her eyes drop to the table, then lift to the person off-screen frame right. Warm tungsten lamp 2900K from camera left, soft, deep blue window glow behind, faint haze. Locked camera, subtle breathing only. Fine 35mm grain, warm amber and deep blue palette. Ambient: low fridge hum."
Notes: use identical environment anchors and light in every prompt; generate 03 and 04 from the same Element and lens; the eye line is frame right for Mara and frame left for Dev.

## Worked scene 2: action chase (EXT. HARBOR MARKET, DAY)
Premise: a courier with a satchel is chased by two pursuers through a market and across a bridge, ending at a ferry. Palette: sun-faded canvas colors, teal water. 9 shots; vector: chase runs left to right throughout, turns on the bridge. Look: crisp short shutter, slight grain. Avoid contact fighting; the beats are speed, obstacles, near misses.
| ID | Beat | Size | Angle | Lens | Move | Light | Dur | Model |
|---|---|---|---|---|---|---|---|---|
| 01 | Establish market | EWS aerial | High | 24mm | Drone descends | Midday sun | 5 s | Kling 3.0 |
| 02 | Courier bursts out | MS | Eye | 35mm | Tracking alongside, left to right | Hard sun | 4 s | Seedance |
| 03 | Pursuers enter frame | WS | Low | 24mm | Static | Sun | 3 s | Seedance |
| 04 | Feet through puddle | CU | Ground | 24mm | Tracking | Sun glints | 3 s | Seedance |
| 05 | Stall tips over, near miss | MS | Eye | 35mm | Handheld follow | Sun | 4 s | Kling |
| 06 | POV vault over crates | POV | Eye | 16mm | Handheld | Sun | 3 s | Veo |
| 07 | Bridge crossing, direction holds | WS | High | 35mm | Crane tracking | Backlit sun | 5 s | Kling |
| 08 | Courier glances back | MCU | Low | 85mm | Tracking | Rim light | 3 s | Seedance |
| 09 | Ferry leaves, pursuers stranded | EWS | High | 24mm | Slow pull-out | Sun | 6 s | Veo |
Prompt example (shot 05): "Medium shot, eye level, 35mm. A courier sprints left to right between fruit stalls, a stall of oranges tips and oranges roll across the stones as she leaps past. Handheld follow at running pace, subtle shake, camera parallel to her path. Harsh midday sun from camera right, dust in the air. Crisp short-shutter motion, sun-faded colors, light grain."
Rules applied: one move per shot; alternate sizes; change angle by 30+ degrees between neighbors; cut away at impact to a reaction or aftermath (V Higgsfield: unreliable precise contact).

## Worked scene 3: product hero (30-second skincare-style ad, client-neutral)
Premise: a plain glass dropper bottle of facial oil in a calm bathroom, 7 shots, 9:16 for short-form with safe areas. Palette: ivory, sage and a single amber accent (60:30:10). Light: soft north window, neutral 5600K. Look: clean natural, fine grain, neutral white balance, honest texture. No result claims; copy added in edit; product label added in edit to avoid garbled text.
| ID | Beat | Size | Angle | Lens | Move | Light | Dur | Model |
|---|---|---|---|---|---|---|---|---|
| 01 | Hook: droplet falls | ECU macro | Eye | 100mm f/4 | Locked | Side window, backlit droplet | 2 s | Seedance |
| 02 | Hand lifts bottle | CU | Slightly high | 85mm f/2.8 | Slow push-in | Soft window | 3 s | Seedance |
| 03 | Oil on fingertip | ECU | Eye | 100mm macro | Locked | Soft window, spec highlight | 3 s | Seedance |
| 04 | Applying (hand, no result claim) | MCU | Eye | 50mm f/2.8 | Slow handheld | Window | 4 s | Veo 3.1 |
| 05 | Hero bottle on shelf | MS | Slightly low | 50mm f/4 | Slow 60-degree orbit | Window plus rim | 5 s | Seedance or Kling |
| 06 | Texture macro pull-out to bathroom | ECU to WS | Eye | 24mm probe look | Pull-out 6 s | Window | 6 s | Cinema Studio |
| 07 | End card hold | MS | Eye | 50mm | Locked | Window | 3 s | Image to video |
Prompt example (shot 05): "Medium shot, slightly low angle, 50mm, f/4. A glass dropper bottle with a plain label stands on an oak shelf beside a folded linen towel and a sprig of eucalyptus, camera performs a slow 60-degree orbit left, keeping the bottle centered, soft north window light from camera left at 5600K with a faint rim from behind, ivory and sage palette, a single amber accent from the oil, fine grain, natural white balance. One continuous shot, steady, no zoom."
Checks: label shape consistent across shots, no extra bottles, droplet physics plausible, skin texture honest. Compliance and claims review belongs to the claims owner.

## Review checklist per shot
Size and angle correct; one move; light source named; screen direction; palette; subject identity; hands, text, reflections, eyelines; duration within model limit; model and settings recorded.

## File naming (H)
`PROJECT_S01_SH03_v02_veo31.mp4` plus the prompt in a sidecar text or sheet row.
