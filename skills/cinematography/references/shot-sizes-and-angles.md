---
name: cinematography
description: "Shot sizes (extreme wide to extreme close-up), inserts, over-the-shoulder, POV, two-shot, cowboy and camera angles (eye level, high, low, dutch, bird's eye, worm's eye) with emotional effect and AI prompt phrasing. Part of the cinematography skill for AI video and image prompting."
---

# Shot sizes and angles
Labels: (K) established film craft, (3P) third-party guide, (H) house rule. Size answers "how close must the viewer be to feel this". Angle answers "who has power here and how does the viewer relate to it". StudioBinder and film-school glossaries agree on the size ladder (3P).

## Shot size ladder (frame cut-off point on a standing person)
| Size | Abbrev | Frames | Effect | Use | Prompt phrasing |
|---|---|---|---|---|---|
| Extreme wide / establishing | EWS, ELS | Person tiny or absent, landscape or city dominates | Scale, isolation, place, awe | Open a scene, show journey, loneliness | "Extreme wide shot, tiny figure crossing a salt flat, vast empty sky" |
| Wide / long | WS, LS | Full body with room to spare | Context, body language, geography | Entrances, group staging | "Wide shot, full body, centered in a lit corridor" |
| Full | FS | Head to toe, little extra | Posture, costume, gesture | Fashion, walks, dance | "Full shot, head to toe, subject mid-stride" |
| Medium wide / cowboy | MWS, CS | Knees or mid-thigh up | Posture plus hands near a holster or tool | Westerns, confrontations, product handling | "Cowboy shot, mid-thigh up, hand near the tool" |
| Medium | MS | Waist up | Conversation, natural, neutral | Dialogue workhorse | "Medium shot, waist up, relaxed, eye level" |
| Medium close-up | MCU | Chest up | Intimacy with context | Interviews, key lines | "Medium close-up, chest up, 50mm" |
| Close-up | CU | Face, shoulders cut | Emotion, thought, truth | Reaction, reveal | "Close-up on the face, shallow depth of field" |
| Big close-up | BCU | Forehead to chin | Intensity, discomfort | Climax, fear | "Tight close-up, face fills the frame" |
| Extreme close-up | ECU | Eye, lips, a detail | Obsession, tension, texture | Macro, sensory beats | "Extreme close-up of the eye, iris fills frame, 100mm macro" |

Rules of thumb: (K) wide for where and who, medium for what they do, close for what they feel. Do not jump more than two steps in size across a cut without reason; vary size at least one step to avoid a jump-cut look. (H) For AI, ask for the size by body landmark ("chest up"), because models read landmarks more reliably than abbreviations. (3P)

## Inserts and special frames
| Shot | What | Effect | Phrasing |
|---|---|---|---|
| Insert | Close detail of an object or action (hand, dial, letter) | Directs attention, adds information | "Insert shot of fingers pressing a dropper, macro, shallow focus" |
| Cutaway | Related image away from main action | Hides a cut, adds context | "Cutaway to rain on the window" |
| Over-the-shoulder (OTS) | Foreground shoulder and head, face of the other person | Connection, relationship, dialogue geometry | "Over-the-shoulder, soft out-of-focus shoulder in foreground left, listener's face sharp" |
| Two-shot | Two subjects in one frame | Relationship, balance, tension of distance | "Two-shot, medium, both in profile, space between them" |
| Three-shot / group | Three or more | Hierarchy, alliances | "Group shot, hero center, others angled in" |
| POV | Camera is a character's eyes | Identification, voyeurism, threat | "POV shot, hands visible at bottom of frame, walking toward a door" |
| Reaction | Face response to off-screen event | Emotional payload | "Reaction close-up, eyes widen, mouth slightly open" |
| Profile | Side view of face | Reflective, formal, mysterious | "Profile close-up, soft rim light" |
| Master | Wide shot covering a whole scene | Geography and fallback | See `coverage-and-sequences.md` |

OTS and POV in AI: models often draw the shoulder person's face wrong; name "back of head and shoulder only" and keep it out of focus. Fixes: lock a start and end frame, keep the foreground person facing away, use a wider frame, and name which shoulder and whose back is in front (3P invideo, DEV Community, unifab; OTS is a documented weak point of image and video models) [verified 2026-10-14, 3P blogs only; no vendor test]

## Camera angles
| Angle | Camera position | Effect | Phrasing |
|---|---|---|---|
| Eye level | At subject eye line | Neutral, honest, equal | "Eye-level, neutral" |
| Shoulder / hip / knee level | Lower than eye | Intimate, kinetic, child-height | "Hip-level camera looking slightly up" |
| Ground level | Lens on the floor | Texture, scale, menace | "Ground-level camera, wheels and boots pass" |
| Low angle | Below, looking up | Power, heroism, threat; ceilings add confinement | "Low angle, looking up at the subject, sky behind" |
| High angle | Above, looking down | Vulnerability, smallness, surveillance | "High angle, looking down at the subject, tiled floor" |
| Overhead / top shot | Straight down | Pattern, god view, fate; food and flat-lays | "Overhead top-down shot, 90 degrees, symmetrical table" |
| Bird's eye / aerial | Far above, may be drone | Geography, insignificance | "Bird's-eye aerial, rising, city grid below" |
| Worm's eye | Very low and steep up | Towering, extreme power, comic distortion | "Worm's-eye view, looming figure, 16mm lens" |
| Dutch / canted | Horizon tilted | Unease, instability, madness | "Dutch angle, horizon tilted 15 degrees" |
| Over-the-hip, profile, 3/4 | Rotated around the subject | Flattering (3/4), formal (profile) | "Three-quarter angle, soft rim on cheek" |

Notes
- Dutch: state degrees; 10 to 20 reads as unease, 30+ reads stylized or comic. (3P Higgsfield Academy pairing, K)
- Low angle on a person pairs with wide lens for exaggeration (see `lenses-and-optics.md`), with a longer lens for dignified power. (K)
- Do not use extreme angles on every shot: the effect only reads against neutral coverage. (K)
- Height is relative to subject: for a child or pet, "eye level" means low to the floor. State it. (H)

## Pairing size, angle and emotion (quick picks)
| Intent | Size | Angle | Lens |
|---|---|---|---|
| Trust, warmth | MCU | Eye level or slightly high | 50 to 85mm |
| Power | MS or CS | Low | 35 to 50mm |
| Fear or entrapment | CU or BCU | High or dutch | 24 to 35mm |
| Awe | EWS | Low or aerial | 14 to 24mm |
| Desire, intimacy | CU or ECU | Eye level, 3/4 | 85mm+ shallow |
| Loneliness | EWS or WS | Eye level or high | 24 to 35mm, negative space |
| Product hero | CU or macro | Slight low or 3/4 | 50 to 100mm |

## AI prompt tips
- Put size and angle first: models front-weight the opening words. (3P, several guides)
- Pair size with a lens word to lock perspective: "close-up, 85mm, f/1.8".
- When a model ignores a size, add a landmark rule: "shoulders cut off by the frame" for CU, "feet visible" for full.
- Aspect ratio changes read of size: 9:16 favors CU and MCU, 2.39:1 favors wide and two-shots. (K)
- For stills, vary size across a set to build a sequence; see `shot-list-templates.md`.
