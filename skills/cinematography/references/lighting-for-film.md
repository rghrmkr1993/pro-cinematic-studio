---
name: cinematography
description: "Film lighting translated to AI prompts: three-point, high key, low key, Rembrandt, butterfly, split, loop, motivated light, practicals, golden and blue hour, night exterior, neon, chiaroscuro, volumetric haze, color temperature in Kelvin, contrast ratios, and lighting different skin tones with exposure and reflectance care. Part of the cinematography skill."
---

# Lighting for film
Labels: (K) craft, (3P) third-party or interview, (H) house rule. For 3D and real-time rig math (azimuth, stops, HDRI) use `graphics-rendering/references/lighting-setups.md`; this file covers the cinematic intent and AI wording. Do not repeat the shared formulas there.

## Principles
- Light has source, direction, quality (hard or soft), color, and contrast. Name all five. (K)
- Motivated light: every light looks like it comes from something in the world (window, lamp, sun, screen). Roger Deakins is known for lighting from sources in or implied by the frame, often a single bulb or a very large soft source (3P, interview summaries). Prompt: "lit only by the desk lamp in frame".
- Soft = large source relative to subject (overcast, bounce, softbox); hard = small source (sun, bare bulb), crisp shadows. (K)
- Shape comes from shadows, not brightness. (K)
- If something stands out and does not serve the story, remove it (Deakins paraphrase, 3P).

## Named setups
| Setup | Light | Mood | Prompt |
|---|---|---|---|
| Three-point | Key, fill, backlight | Clean, commercial | "classic three-point lighting, soft key from camera left, gentle fill, rim light on hair" |
| High key | Bright, low ratio, few shadows | Cheerful, clean, beauty, comedy | "high-key lighting, bright, soft, minimal shadows, white background" |
| Low key | Single source, deep shadows | Drama, noir, menace | "low-key lighting, single hard source from the side, deep black shadows" |
| Rembrandt | Key 45 degrees, high; triangle on shadow cheek | Moody portrait | "Rembrandt lighting, triangle of light under the eye on the shadow side" |
| Butterfly / Paramount | Key high, frontal; shadow under nose | Glamour, beauty | "butterfly lighting from above front, soft shadow under the nose and chin" |
| Clamshell | Large key above plus fill below | Beauty, skincare close-up | "clamshell lighting, soft top key and bounce from below, smooth even skin" |
| Loop | Key 30 to 45 degrees, small nose-shadow loop | Flattering default | "loop lighting, soft key from 45 degrees" |
| Split | Key at 90 degrees, half face dark | Duality, menace | "split lighting, half the face in shadow" |
| Short vs broad | Light the far side (short) or near side (broad) of face | Short slims and deepens | "short lighting" |
| Backlight / rim / contre-jour | Source behind subject toward camera | Separation, halo, silhouette | "backlit, rim light, contre-jour, camera on the shadow side" |
| Kicker / hair light | Small rim from behind-side | Edge glow | "kicker light on cheekbone" |
| Chiaroscuro | Strong light and dark contrast, painterly | Renaissance drama | "chiaroscuro, single candle-like source, deep shadow" |
| Silhouette | Subject unlit against bright background | Iconic, mystery | "pure silhouette against a bright window" |
| Cove / ambient wash | Very large soft source | Even coverage for freedom of movement (Deakins' cove light, 3P) | "large soft ambient light wrapping the room" |
Higgsfield Cinema Studio 4.0 lighting presets: Auto, Silhouette, Practicals, Window, Overhead Fall, Contre-jour, Soft Cross (V).

## Practicals and sources
| Source | Look | Prompt |
|---|---|---|
| Window | Soft directional, gradient across room | "soft north window light from camera left, falloff across the room" |
| Practical lamp | Warm pool, visible bulb | "warm tungsten table lamp in frame, 3000K pool of light" |
| Candle / fire | Flicker, orange, falloff | "candlelight only, flickering warm glow, deep shadows" |
| Screen / monitor | Cool, flickering | "lit by a laptop screen, cool blue glow on the face" |
| Streetlight / car lights | Sodium or LED | "sodium streetlight 2200K, orange cast" |
| Fluorescent | Greenish, flat | "overhead fluorescent, slight green cast, flat" |
| Neon | Saturated color, spill | "neon signs magenta and cyan spill on wet pavement" |
| Sun | Hard, directional | "hard late-afternoon sun from camera right" |
| Overcast | Giant softbox | "overcast soft shadowless daylight" |

## Time of day and exteriors
| Time | Kelvin and feel | Prompt |
|---|---|---|
| Golden hour | Low sun, long shadows, warm 3500 to 4500K | "golden-hour sun at 10 degrees, long warm shadows, rim on hair" |
| Magic / blue hour | 9000K+, even blue, practicals pop | "blue hour, deep indigo sky, warm windows glowing" |
| Midday sun | Hard overhead, harsh shadows | "harsh midday sun, short sharp shadows, squinting" |
| Overcast | 6500 to 7000K, soft | "flat overcast, soft, muted color" |
| Night exterior | Motivated pools plus a blue ambient base ("movie moonlight") | "night exterior, blue moonlight ambient, warm streetlamp pools, wet ground reflections" |
| Day-for-night | Underexposed day with blue grade | "day-for-night, cool low exposure" Real technique: about 1.5 to 3 stops under with a subtle blue, hide the sky and sun disc, add practicals (3P Meliès, Videomaker, toolsforfilm). Generators do not follow stop counts, so write "dark sky, low backlight, desaturated, subtle cool tint, streetlamps" and grade in post [verified melies.co and toolsforfilm.com, 2026-10-14; single source for the AI wording] |
| Rain | Backlit rain shows best against dark | "rain backlit by a lamp, wet reflections, mist" |
Rain and backlight are visible features of Indian cinema from Mani Ratnam collaborators; see `director-styles.md`.

## Volumetric haze and atmosphere
Haze or smoke makes light beams visible and adds depth. Prompt: "light shafts through haze, volumetric beams, dust motes". Keep density low or it flattens contrast. (K)

## Color temperature (Kelvin) cheat sheet
| Source | Approx K |
|---|---|
| Candle | 1800 to 1900 |
| Sodium streetlight | 2000 to 2200 |
| Tungsten household | 2700 to 3200 |
| Golden hour | 3500 to 4500 |
| Daylight, flash | 5200 to 5600 |
| Overcast | 6500 to 7000 |
| Open shade, blue hour | 8000 to 10000 |
Mixed temperature (warm key, cool fill or window) gives depth and a built-in color story; use one warm and one cool family, not rainbow. (K, also in `graphics-rendering`)

## Contrast ratio
| Ratio (key to fill) | Stops | Look |
|---|---|---|
| 1:1 to 2:1 | 0 to 1 | High key, flat, comedy, beauty |
| 3:1 | 1.6 | Natural portrait |
| 4:1 to 6:1 | 2 to 2.6 | Dramatic |
| 8:1+ | 3+ | Noir, low key |
Prompt with words: "soft contrast, lifted shadows" (low ratio) or "deep crushed blacks, strong key to fill ratio 8:1" (high). Models respond to the words, not the numbers; numbers add little. Ratio maths: each stop of difference doubles it (1 stop 2:1, 2 stops 4:1, 3 stops 8:1); high key is about 1:1 to 2:1 and low key 8:1 or more (3P StudioBinder); the ASC formula is (key+fill):fill so 200 fc key and 100 fc fill reads 3:1; working DPs rarely think in ratios now (David Mullen ASC, cinematography.com). For the AI claim itself [no public source as of 2026-10-14; checked: Runway, Google and Higgsfield guides, StudioBinder, cinematography.com; no vendor documents numeric ratios as a parsed control] [verified studiobinder.com/blog/lighting-ratios, 2026-10-14]

## Lighting different skin tones
- There is no formula by color of skin. A working DP lighting dark skin on HBO's Insecure (Ava Berkofsky, ASC) said everybody's skin is different, rejected the "70 IRE on skin" convention, and rated the camera higher to underexpose then lift, while keeping the image from looking over-bright (3P interviews, Mic and British Cinematographer).
- Reflectance matters more than quantity: give skin a surface to reflect (sheen, makeup base, soft large source) and control specular highlights; polarizer helps shape. (3P, same interviews)
- Film stocks and white-balance defaults historically optimized for light skin (Shirley cards); digital and AI can inherit that bias. (3P)
- Prompt practice (H): name the skin tone in plain words ("deep brown skin"), light with a large soft source from the side, add a gentle rim for separation, and say "rich skin tone with natural highlights, no gray cast, no washed-out lifting". Avoid "pale", "ashen" or fixed gels. Raise exposure only to the point where texture holds; do not flatten the face.
- Light faces separately from the background: a mixed-skin-tone scene needs a different level on each, or the grade pushes one face to gray. (3P)
- Check results for: ashy highlights, blown specular spots, muddy shadow detail, eye catchlight present.
- For Indian and other Asian subjects use `asian-human-reference` for tone range and `photoreal-humans` for texture.

## Beauty and skincare notes
Clamshell or a large soft source gives even skin for macro beauty; keep real skin texture, pores and imperfections visible. Do not smooth to the point of a claim about results. (H)

## Prompt recipes
- Interior drama: "A man at a kitchen table at night, lit only by a single hanging bulb overhead, low key, warm 2900K, deep shadows, faint haze."
- Warm romance: "Golden-hour backlight, warm rim glow on hair, soft fill from a reflector, haze."
- Cold thriller: "Cool 5600K overhead fluorescent flicker, green cast, hard shadows, wet floor reflections."
- Product hero: "Large softbox top light, strip lights left and right drawing clean edge highlights, dark gradient background."
- Neon-noir: "Magenta and cyan neon spill on wet asphalt, deep black shadows, volumetric haze."
