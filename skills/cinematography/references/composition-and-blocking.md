---
name: cinematography
description: "Composition and blocking for AI frames: rule of thirds, center framing, leading lines, frames within frames, negative space, headroom, lead room, 180-degree rule, 30-degree rule, eyeline match, screen direction, blocking actors and camera, depth staging. Part of the cinematography skill."
---

# Composition and blocking
Labels: (K) established craft, (3P) third-party, (H) house rule. Film-school glossaries (MasterClass, Filmmakers Academy, Frame.io) agree on continuity rules (3P). Evidence that viewers consciously notice a broken 180 line is limited; the rules are working conventions, not laws. (3P)

## Frame composition tools
| Tool | What | Emotional use | Prompt |
|---|---|---|---|
| Rule of thirds | Subject on a thirds line or intersection | Natural, balanced, relaxed | "subject on the left third, eyes on the upper third line" |
| Center framing | Subject dead center | Authority, confrontation, deadpan | "centered symmetrical composition" |
| Symmetry / planimetric | Camera square to a flat back wall, mirrored halves | Formal, stylized, storybook (Wes Anderson technique per a Cooke interview with Robert Yeoman, 3P) | "planimetric frame, camera perpendicular to the back wall, perfect symmetry" |
| Leading lines | Roads, rails, architecture pull the eye to the subject | Direction, destiny, depth | "converging lines of the corridor lead to the figure" |
| Frame within a frame | Door, window, arch, mirror around subject | Confinement, voyeurism, focus | "subject framed through a doorway, dark foreground frame" |
| Negative space | Large empty area around subject | Loneliness, calm, space for copy | "small figure bottom-right, vast empty sky" |
| Foreground element | Out-of-focus object in front | Depth, voyeurism, layers | "blurred foliage in foreground edge" |
| Layers / depth stacking | Foreground, mid, background all readable | Dimension | "three depth layers: leaves, subject, skyline" |
| Golden ratio / spiral | Subject on a spiral focus | Organic flow | Use sparingly; models mostly read it as "not centred". Write the placement in words ("subject in the left third") [no vendor documents grid rules as a parsed control as of 2026-10-14; checked: Google and OpenAI guides, prompt-architects.com, Atlabs, Lovart; models default to centred subjects per 3P guides] |
| Diagonals | Tilted lines or poses | Energy, tension | "strong diagonal composition" |
| Silhouette | Subject as dark shape | Mystery, iconic | "backlit silhouette against orange sky" |
| Shape and color blocking | 60:30:10 color areas (Academy guidance per V Higgsfield visual language) | Hierarchy | "60 percent cream, 30 percent sage, 10 percent amber" |

## Headroom, lead room, look room
- Headroom: gap above head. Tight for intensity, generous for isolation. Too much headroom on a CU reads as an error. (K)
- Lead room (nose room): space in the direction the subject faces or moves. Without it the subject feels trapped or about to exit. (K)
- Walking room: space ahead of a moving subject. Chase scenes often remove it for tension. (K)
- Prompt: "subject faces right with open space to the right, small headroom".
- Safe areas for social: leave the bottom 15 percent and right edge clear in 9:16 for captions and UI. (H)

## Continuity rules
| Rule | Meaning | Why | Prompt effect |
|---|---|---|---|
| 180-degree rule | Keep the camera on one side of the line between two subjects | Keeps who is left and who is right consistent (MasterClass, 3P) | Every shot: "A frame left looking right, B frame right looking left" |
| Crossing the line | Deliberately flip sides | Disorientation or a change in power (Requiem for a Dream example, 3P) | Use a neutral shot or on-screen move across the line first |
| 30-degree rule | Move the camera at least 30 degrees between shots of the same subject | Avoids jump-cut feel (3P) | Change angle or size by a clear step |
| Eyeline match | Shot A look off-screen, shot B shows what they see; angle and direction agree | Connects space (3P) | "She looks off-screen right", then "object, seen from her position" |
| Screen direction | Moving subject keeps the same left-to-right direction across cuts | Prevents reversal confusion | State "moving left to right" in every shot of the move |
| Axis of action | The line along a movement | Same as 180 for travel | Keep camera on one side of the road |
| Matching eye line height | Eyes at the same frame height in cuts | Smooth cut | "eyes on the upper third line" across shots |
| Shot-reverse-shot | Alternate singles of two speakers | Dialogue rhythm | See `coverage-and-sequences.md` |
When AI shots will be edited together, put the 180 line and screen direction in the shot list before prompting and repeat it in each prompt. Models do not remember across clips. (H)

## Blocking: staging actors and camera
- Blocking is where people stand and move; the camera follows or counters it. Plan both as one choreography. (K)
- Triangle: for three or more people, arrange in triangles to give readable depth. (K)
- Hierarchy: higher, closer, center or lit = more power. (K)
- Distance = relationship: close together intimacy, wide apart conflict or fear. (K)
- Moving to the camera = approaching threat or confession; away = withdrawal. (K)
- Pass in front of the lens as a wipe or transition. (K)
- Walk-and-talk: camera backs ahead or tracks beside; give a clear start and end mark. (K)
- Roger Deakins: build lighting into the set and let the director change blocking without re-lighting, a big soft source such as a cove light (3P). For AI: describe light as ambient from the environment so actors can move without breaking the shot.
- AI limits: complex multi-person blocking drifts. One or two subjects, one action each, clear start and end positions. (H)

## Depth staging
| Layer | Role |
|---|---|
| Foreground | Out-of-focus frame, texture, parallax in a move |
| Midground | Subject and action |
| Background | Context, light source, color anchor |
Staging in depth lets a camera move reveal parallax; in a flat symmetrical frame, planes stack without depth (K). In prompts: "foreground leaves soft, subject sharp at midground, city lights bokeh far background".
Deep staging in a single frame (Citizen Kane-style deep focus) uses a small aperture or split diopter, see `lenses-and-optics.md`. (K)

## Composition by emotion
| Emotion | Composition |
|---|---|
| Calm | Thirds, generous space, horizontal lines |
| Tension | Tight, diagonal, off-center, half-hidden subject |
| Loneliness | Small subject, large negative space |
| Power | Low angle, center, symmetrical |
| Chaos | Dutch, crowded, handheld, off-balance |
| Intimacy | Close, shallow, subject filling frame, soft edge light |
| Order, whimsy | Symmetry, flat planes, pastel blocks |

## Prompt patterns
- "Wide shot, rule of thirds, a woman on the right third looking left into negative space, mist."
- "Centered symmetrical frame, camera perpendicular to the pink hotel facade, character at the doorway, deadpan."
- "Over-the-shoulder, A in foreground left out of focus, B sharp on right third, B looks off-axis left."
- "Doorway frame within frame, subject in the next room, dark foreground, light from the far window."

## Common AI composition failures
- Models center everything by default; specify the third explicitly. (3P)
- Symmetry gets bent; say "perfectly mirrored, level horizon, camera at exact center". (3P)
- Leading lines drift; use real architecture words (corridor, railway, row of columns). (H)
- Left and right swap between generations; repeat "frame left" and "frame right" and verify each output. (H)
