---
name: cinematography
description: "Still photography craft for keyframes and product shots: genres, lighting modifiers and setups, cosmetics and product techniques (backlit liquids, glass edges, cream texture, soap lather), retouching realism rules, and composition. Part of the cinematography skill."
---

# Photography craft for keyframes and product shots
Labels: (K) established craft, (3P) practitioner, (H) house rule. A strong keyframe decides the look of the video made from it, so treat stills as lighting and composition exercises. Image models respond to light, lens and framing words; motion words do nothing. (K, see `ai-camera-prompting.md`)

## Genres and their defaults
| Genre | Lens and aperture | Light | Composition | Prompt seed |
|---|---|---|---|---|
| Portrait | 85mm, f/1.8 to f/2.8 | Loop or Rembrandt, soft key, rim | Eye on upper third, catchlights | "85mm portrait, soft window key, catchlights, skin texture" |
| Product | 50 to 100mm, f/5.6 to f/11 | Softbox plus strips, flags | Clean negative space, hero angle slightly above eye of product | "studio product, strip highlights, gradient backdrop" |
| Food | 50 to 100mm, f/2.8 to f/5.6 | Side or backlight, soft | 45-degree or overhead, steam, droplets | "side backlit, steam, glistening, shallow focus" |
| Fashion | 70 to 135mm | Hard or beauty dish, flash | Dynamic pose, negative space | "editorial fashion, beauty dish, crisp shadows" |
| Beauty | 85 to 105mm | Clamshell, ring, beauty dish | Tight crop, skin and lip detail | "beauty close-up, clamshell light, visible skin texture" |
| Street | 28 to 35mm, f/5.6 to f/8 | Available, shadows | Layers, decisive moment | "35mm street photograph, hard light, layered" |
| Landscape | 16 to 35mm, f/8 to f/11 | Golden hour, graduated ND | Foreground anchor, leading lines | "wide landscape, golden hour, deep focus, foreground rocks" |
| Architecture | 17 to 24mm tilt-shift | Overcast or blue hour | Verticals straight, symmetry | "tilt-shift architecture, straight verticals, blue hour" |
| Macro | 90 to 105mm, f/5.6 to f/11 | Soft ring or small softbox | Focus plane on detail, stacked | "100mm macro, extreme close-up, shallow focus" |
| Astro | 14 to 24mm, f/1.4 to f/2.8 | Starlight, long exposure, tracked | Foreground silhouette, Milky Way | "wide astro, Milky Way arc, silhouetted foreground" |

## Modifiers and what they do
| Modifier | Quality | Use |
|---|---|---|
| Softbox | Soft, directional, rectangular catchlight | Product, portrait key |
| Beauty dish | Crisp but soft-edged, contrasty | Fashion, beauty, cheekbone definition |
| Octabox | Soft, round catchlight | Portrait, headshot |
| Strip box | Narrow, edge highlight | Bottles, jewellery, rim |
| Grid | Narrows spread, controls spill | Background gradient, hair light |
| Scrim | Diffuses sun or light | Outdoor soft shade |
| Bounce card (white, silver, gold) | Fill, silver is hotter, gold warms | Fill under chin or into shadow |
| Flag and negative fill (black) | Deepens shadow, adds shape | Contrast, glass edges |
| Reflector | Fill without power | Reflector under face for beauty |
| Ring light | Flat frontal, ring catchlight | Beauty vlog, makeup |

## Lighting setups (stills)
| Setup | Layout | Best for |
|---|---|---|
| Clamshell | Large key above axis, bounce or fill below | Beauty, skincare close-up |
| Rembrandt | Key 45 degrees high, triangle on cheek | Moody portrait |
| Butterfly | Key high front | Glamour |
| Short light | Key on the far side of face | Slimming, drama |
| Rim and kicker | Back-side strip or small source | Separation from dark background |
| Window light | Large soft side source | Natural lifestyle, food |
| Overhead with flag | Soft top, flags for edges | Flat lay |
| Low key | One source, black cards | Luxury product |
Skin tones: no formula by tone; light with large soft sources, control speculars, avoid ashy cast (see `lighting-for-film.md`; `asian-human-reference`). (3P)

## Product and cosmetics techniques
| Subject | Technique | Prompt |
|---|---|---|
| Backlit liquid (serum, oil, toner) | Light behind the bottle through a diffuser; liquid glows; add a white card behind for brightness or a black card for dark edges | "backlit amber serum glowing through glass, soft gradient, specular edges" |
| Glass edge lighting | Strip boxes at each side give white edge lines; black flags in front remove reflections | "glass bottle with crisp strip-light edge highlights on dark background" |
| Black-on-black luxury | Edge strips only, dark gradient, small rim | "dark premium, gold rim, deep shadow, slow glide" |
| Cream and texture | Raking side light at a low angle reveals ridges and peaks; macro lens, thick props like a swatch or spatula | "raking light across cream swirl, macro, peaks and ridges sharp" |
| Soap lather | Bright soft light, backlight to light bubbles; wet surfaces; fast shutter for bubble pop; real water spray | "creamy lather, backlit bubbles, warm soft light, macro" |
| Droplets and splash | High-speed flash or 120 fps, backlight, dark or coloured gradient | "water droplet splash frozen mid-air, backlit, sharp" |
| Powder and dust | Rim light and short shutter | "powder burst frozen, rim light, dark background" |
| Hands and application | Large soft key, matched skin tone, honest texture | "hand applying cream, soft side light, natural skin" |
| Props and surface | Marble, wood, stone, leaf; keep palette to three colours | "cream, sage and amber palette on stone slab" |
Natural-ingredient story shots (coconut, turmeric, neem, rose) work best with window light and natural surfaces; keep ingredients real to the formula, route claims to compliance. (H)
Cosmetic imagery must not imply results the product cannot support; no beauty filters on before and after, and no smoothing that changes texture. Claims belong to the compliance owner. (H)

## Retouching realism rules
1. Keep skin texture: pores, fine lines, peach fuzz. Reduce blemishes, do not wipe pores. (H)
2. Do not reshape faces or bodies; do not whiten teeth and eyes beyond natural.
3. Keep colour true: product, skin and packaging colours match the real item; neutral white balance. (H)
4. Keep edge falloff and contact shadows on products; floating products read fake.
5. Match the highlight shape to the stated light source; one catchlight shape per eye matches the key.
6. Remove only distractions (dust, stray hair); keep label sharp and legible; never alter label text.
7. Add a touch of grain to unify a composite or AI image; avoid "8k ultra detailed" (see failures in `SKILL.md`).
8. Check hands, fingers, text, reflections and shadows in AI stills before use. (H)
9. Frequency separation or dodge and burn is acceptable for smoothing tone, not texture.
10. If AI-generated, label per platform rules and client policy; no real person without consent. (H)

## Composition
| Principle | Use |
|---|---|
| Rule of thirds | Subject on a third, eye on the upper line |
| Leading lines | Roads, shelves, light beams lead to subject |
| Frame within frame | Doors, windows, arches |
| Negative space | Room for copy; luxury feel |
| Symmetry | Order, formality, product hero |
| Diagonals | Energy |
| Golden ratio | Gentle spiral weighting |
| Layers | Foreground, middle, background for depth |
| Colour block | 60:30:10 (see `color-and-look.md`) |
| Visual weight | Balance heavy and light, warm and cool |
| Crop | Cut at mid-limb is awkward; cut above or below joints |
| Headroom and lead room | Space where the subject looks or moves (see `composition-and-blocking.md`) |
Product hero angles: straight-on for authority, 15 to 30 degrees above for friendliness, low for power, top-down flat lay for arrangement. Leave 20 to 30 percent empty space on one side for copy.

## Keyframe workflow for video (H)
1. Compose the hero still: light, lens, grade. 2. Check it at full size for defects. 3. Use as the first frame in image-to-video and write motion only. 4. Re-grade the video to match the still. 5. Keep a lighting diagram note in `look.md`.

## Gaps
- Product lighting recipes now cross-checked against several guides: two softboxes at about 45 degrees for even light, one brighter for depth; silver reflector on a cream jar; black card beside a dropper bottle for a clean dark glass edge; jar shot at 30 to 45 degrees downward plus an open-lid texture shot; zoom to 200 percent to check label text (3P Clipping Path Studio, Welpix, Graphic-Aid, Caspa, Monoshoot) [verified 2026-10-14, 3P blogs only]. They are blog-level craft, not standards: test with the real product and a cosmetic scientist or product photographer, and keep colour and texture true to the product (compliance).
