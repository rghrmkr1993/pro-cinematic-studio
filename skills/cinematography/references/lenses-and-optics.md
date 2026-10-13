---
name: cinematography
description: "Lenses and optics for AI prompting: focal lengths and feel, spherical vs anamorphic (flares, oval bokeh, 2.39:1), depth of field and T-stop, macro, tilt-shift, fisheye, probe, split diopter, vintage glass, sensor size, frame rates and the 180-degree shutter rule. Part of the cinematography skill."
---

# Lenses and optics
Labels: (K) established craft, (V) vendor-official, (3P) third-party. Lens maker notes (Cooke, ARRI/Zeiss via rental houses) describe real glass; AI models imitate the look statistically, so the words steer, they do not simulate optics. (H)

## Focal length and feel (full-frame equivalent)
| Focal length | Perspective | Feel | Use | Prompt |
|---|---|---|---|---|
| 8 to 14mm | Extreme wide, strong distortion | Scale, disorientation, fisheye at 8 | Environments, POV thrills; avoid faces | "14mm ultra-wide, converging lines" |
| 16 to 24mm | Wide, expansive | Tension, space, grandeur | Rooms, landscapes, walk-and-talk | "24mm wide-angle" |
| 28 to 35mm | Natural wide | Documentary, human, street | Handheld, dialogue in context | "35mm natural perspective" |
| 40 to 50mm | Close to eye | Neutral, honest | General coverage, portraits | "50mm, natural proportions" |
| 65 to 85mm | Mild compression | Flattering, intimate | Portraits, close-ups | "85mm portrait, shallow depth" |
| 100 to 135mm | Compressed, isolating | Voyeuristic, tight | Beauty, reaction, macro-ish | "100mm compressed background" |
| 200mm+ | Heavy compression, flat | Surveillance, epic crowds, sun disk | Long-lens chase, distant action | "200mm telephoto, stacked layers" |
Short lens exaggerates depth and distance between planes; long lens flattens planes and makes backgrounds loom. (K)
Higgsfield Cinema Studio: focal choices 8, 14, 35, 50 (and 75 in 3.5), aperture f/1.4, f/4, f/11 (3P and V; see `higgsfield-master/references/cinema-studio.md`).

## Spherical vs anamorphic
| Trait | Spherical | Anamorphic |
|---|---|---|
| Bokeh | Round | Oval, vertical stretch (Cooke, 3P) |
| Flares | Starbursts, veiling | Long horizontal streaks, often blue or amber by maker (Panavision warm amber, ARRI Signature cooler, Hawk blue, 3P) |
| Field of view | As labeled | Squeeze (1.3x, 1.8x, 2x) widens horizontal view; a 50mm anamorphic gives the vertical view of a 50mm and the horizontal view of about 25mm (Cooke, 3P) |
| Aspect ratio | 16:9, 1.85:1 | 2.39:1 typical cinema scope |
| Edge behavior | Clean | Softer edges, distortion, focus stretch (Cooke, 3P) |
| Depth of field | Same as a spherical lens of equal focal length and stop (Art Adams, 3P); anamorphic bokeh simply looks different |
| Prompt | "spherical prime, clean, round bokeh" | "anamorphic 2x, 2.39:1, horizontal blue flare, oval bokeh, edge falloff" |
Modern low-distortion anamorphics (ARRI/Zeiss Master Anamorphic, 3P) give oval bokeh with fewer flaws; ask for "clean anamorphic" to keep elegance without heavy flare.
Tip: ask for the aspect in the tool UI, not only in text. A prompt "2.39:1" in a 16:9 render may add black bars instead of true scope; crop in post [no vendor doc, see `exposure-and-settings.md`, 2026-10-14].

## Depth of field and aperture
DOF grows with smaller aperture (higher f-number), shorter focal length, longer subject distance, smaller sensor. (K)
| Aperture | Look | Use |
|---|---|---|
| f/1.2 to f/2 | Razor-thin, creamy | Portrait isolation, night, dreamy |
| f/2.8 to f/4 | Balanced, subject sharp, background soft | Dialogue, product |
| f/5.6 to f/8 | Environment readable | Walk-and-talk, action |
| f/11 to f/16 | Deep focus | Landscapes, UGC clarity, clinical product (V Higgsfield uses f/1.4, f/4, f/11) |
T-stop vs f-stop: T-stop measures actual light transmission and is what lens makers rate cinema glass in; f-stop is the geometric ratio. Equal T-stops give equal exposure across lenses. (K)
Phrasing: "shallow depth of field, f/1.8, background melts into soft bokeh" or "deep focus, f/11, everything sharp from foreground to horizon".
Focus breathing: cheap zooms change framing when focus is pulled; Zeiss Master Primes are designed with essentially no breathing (3P). AI footage can show breathing-like zoom on a rack; avoid by locking focus.

## Special lenses and tools
| Tool | Optics | Look | Prompt |
|---|---|---|---|
| Macro | 1:1 close focus, 60 to 105mm | Texture, droplets, eyes | "100mm macro, extreme close-up, shallow focus" |
| Tilt-shift | Rotates focal plane | Slanted focus, miniature effect | "tilt-shift look, band of focus across the frame, miniature" |
| Fisheye | 8 to 16mm, barrel distortion | Raw, skate, music video | "fisheye 8mm, barrel distortion, subject close to lens" |
| Probe / periscope | Long narrow barrel into tight spaces | Bug's-eye, deep focus, impossible path | "probe lens glides through the shelf, deep focus" |
| Split diopter | Half-moon close-up filter | Near and far both sharp with a soft line between; fake deep focus (ASC article, 3P) | "split-diopter shot, foreground object and background face both sharp" |
| Swirly or petzval | Vintage design | Spinning bokeh at edges | "swirly bokeh, vintage petzval lens" |
| Softening filters | Black Pro-Mist, diffusion | Glow in highlights, lowers contrast, flatters skin | "black diffusion filter, soft halation around lights" |
| Lens whacking / free-lensing | Lens detached slightly | Light leaks, soft smears | "free-lensed, warm light leaks, soft edges" |
| Vintage glass | Old coatings, low contrast | Flares, halation, dreamy | "vintage 1970s prime, lifted blacks, warm bloom" |

## Vintage and character glass looks
| Look | Traits | Prompt |
|---|---|---|
| 1960s to 70s spherical | Low contrast, soft corners, warm flare | "1970s vintage lens, soft contrast, flare" |
| Cooke look (3P) | Warm, gentle, rounded skin | "warm gentle lens, creamy skin, soft roll-off" |
| Clean modern (Master Prime style) | Sharp, neutral, no breathing | "clean sharp modern prime" |
| Anamorphic vintage | Strong flare, blur, warp | "vintage anamorphic, swirl, flare" |
| 16mm or 8mm | Grain, instability | "Super 16 grain, gate weave, soft" |
Cinema Studio lens characters: Clean Sharp, Anamorphic, Vintage Anamorphic, Warm Vintage, Halation Vintage (V).

## Sensor size
Larger sensor with the same field of view means shallower depth of field at equal f-stop. Super 35 is cinema standard; full-frame and large-format (ARRI Alexa LF, used on RRR with Signature Primes per an ASC interview summarized in 3P) give a softer fall-off and wider view; smaller sensors (phones, 1/2.3") give deep focus. (K)
Phrasing: "large-format sensor look, shallow, smooth falloff" or "phone footage, deep focus, small sensor" for UGC authenticity.

## Frame rate and shutter
| Frame rate | Use | Feel |
|---|---|---|
| 24 fps | Cinema standard | Filmic motion blur |
| 25, 30 fps | Broadcast, web | Neutral, video-like |
| 48 fps | Mild slow-down | Smooth, hyper-real |
| 60 fps | Sport, light slow-mo | Crisp |
| 120 fps | 5x slow motion at 24 playback | Pour, impact, fabric, hair |
| 240 fps+ | Extreme slow motion | Droplets, debris |
180-degree shutter rule: shutter speed is about 1 over twice the frame rate (1/48 at 24 fps, 1/240 at 120 fps), the half-open disc that gives natural motion blur (3P). Narrower angles (for example 45 degrees at 24 fps) look crisp and staccato (Saving Private Ryan style battle crispness, K); wider angles smear. Shutter angle changes texture, not speed; frame rate changes speed. (3P)
AI note: models do not take fps or shutter as parameters reliably. Write "slow motion, 120fps look, high-speed camera, each droplet sharp" for slow-mo and "natural 180-degree shutter motion blur" for normal. For a crisp action look: "sharp, short shutter, little blur". Higgsfield 3.0 adds speed ramps (Linear, Slow-mo, Bullet Time, Impact, Ramp Up, etc., V). Speed ramps are a clean way to get slow-mo without a model asking for fps.

## Prompt recipes
- Portrait: "85mm, f/1.8, shallow depth of field, skin sharp, background bokeh".
- Epic wide: "anamorphic 35mm, 2.39:1, deep focus, horizontal flare, large-format".
- Product macro: "100mm macro, f/4, extreme close-up, softbox gradient, droplet sharp".
- Documentary: "35mm, handheld, natural light, slight grain, 24fps".
- Dreamy memory: "vintage lens, black diffusion, halation, lifted blacks".

## Cautions
- Do not use 8 to 14mm on faces unless distortion is the point. (K)
- Fisheye and tilt-shift are inconsistent in models; check distortion near hands and labels. (H)
- Oval bokeh needs an actual bright point source in the frame to show; add "street lights" or "fairy lights" in the background. (K)
