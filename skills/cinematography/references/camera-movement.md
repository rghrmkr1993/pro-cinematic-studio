---
name: cinematography
description: "Camera movement for AI video: pan, tilt, dolly, truck, pedestal, crane, jib, Steadicam, gimbal, handheld, drone, whip pan, crash zoom, dolly zoom, orbit, push-in, pull-out, rack focus, tracking, long take and snorricam, with when to use each, speed, prompt wording and which models cope. Part of the cinematography skill."
---

# Camera movement
Labels: (K) film craft, (V) vendor-official, (3P) third-party guide. Model strength ratings are 3P and community-reported; test on your plan before relying on them.

## Core principles
- A move needs a motive: reveal, follow, emphasize, or change emotional distance. (K)
- A move = start framing + path + speed curve (ease in or out) + end framing. Higgsfield's camera blog says text-only prompts vary run to run because speed, path and end position are unspecified. Name all four. (V)
- Physical moves (dolly, truck, pedestal, crane) change parallax; rotations (pan, tilt) do not; zoom changes only focal length. Prompt the right one or the model blends them. (K)
- One primary move per shot. Runway and several Kling and Veo guides say stacking moves yields chaos; Seedance guides allow 2 to 3 joined by "while" (3P, sources disagree; test).
- Speed words: "very slow, about 1 metre over 5 seconds", "walking pace", "quick snap". Kling's guide pairs speed descriptors with durations (V).
- Hold a still beat of about 1 to 2 seconds at start or end to give the edit a clean cut point. (H)

## Move reference
| Move | What it is | Use when | Speed | Prompt wording | Model fit (3P) |
|---|---|---|---|---|---|
| Static / locked-off | Camera does not move | Dialogue, dread, tableau, product | n/a | "Locked-off tripod shot, no camera movement" (Runway: "camera remains completely still") | All strong |
| Pan | Rotate left or right on a fixed point | Reveal, follow, survey | Slow for survey, fast for whip | "Slow pan left to right, camera stays in place" | All good |
| Tilt | Rotate up or down | Reveal scale (feet to head, ground to sky) | Slow | "Tilt up from boots to face, slow, camera stays in place" | All good |
| Push-in / dolly in | Camera physically moves toward subject | Focus, tension, emotional realization | Slow = intimate, fast = urgent | "Slow dolly push-in from medium to close-up over 5 seconds, then hold" | Best-supported move on Seedance, Kling, Veo, Runway |
| Pull-out / dolly out | Away from subject | Isolation, reveal context, ending | Slow | "Pull back from the eyes to a wide shot revealing the room" | Good; geometry may invent background |
| Truck / track | Sideways move parallel to the subject | Follow walk, reveal along a wall, lateral parallax | Match subject pace | "Camera trucks left alongside the subject at walking pace" | Good |
| Pedestal | Camera rises or lowers vertically, no tilt | Reveal over an object, shift level | Slow | "Pedestal up, camera rises straight up, level horizon" | Moderate; models substitute tilt |
| Crane / jib | Arm move combining lift, arc | Opening and closing, scale reveal | Slow, sweeping | "Crane shot starts low on a hiker and rises above to reveal the canyon" (Google's own Veo example) | Good on Veo, Kling, Seedance |
| Steadicam / gimbal | Smooth handheld follow | Following through spaces, ghost-like float | Walking pace | "Smooth steadicam follow behind the subject through the corridor" | Good |
| Handheld | Human-held, micro shake | Realism, urgency, documentary | Light tremor | "Handheld, subtle sway, documentary" (keep intensity low; heavy shake jitters detail, 3P) | Good; avoid on wide frames |
| Tracking / follow | Camera moves with a moving subject | Chase, walk-and-talk | Match subject | "Tracking shot at the subject's side, keeping pace" | Strong on Kling, Seedance |
| Orbit / arc | Circle around subject | Hero reveal, product, romantic beat | Slow; keep partial (30 to 180 degrees) | "Slow 90-degree orbit around the subject, subject stays centered" | Product orbits good; full 360 drifts (3P) |
| Drone / aerial | Flying camera | Geography, chase over land | Medium | "Drone ascends and pulls back over the coastline" | Good in Kling, Veo, Seedance |
| FPV | Fast drone through spaces | Thrill, impossible paths | Fast | "FPV drone dives through the gap and skims the street" | Hit-and-miss; rubber-sheet warping on fast low passes; end with "stabilized, no deformation", give a tight space to thread, or use first and last frame (3P Atlabs, Seedance guides) [no independent artefact comparison as of 2026-10-14; checked: Atlabs, metricsmule, screenweaver, renoise, edimakor] |
| Whip pan | Very fast pan, blur between two points | Transition, surprise, comic timing | Under a second | "Whip pan right to the second character, motion blur" | Works as a transition via two clips better than inside one |
| Crash zoom | Rapid zoom in | Shock, comedy, 70s crime homage | Very fast | "Crash zoom into the face, fast, then hold" | Fair; may blend into dolly |
| Zoom (slow) | Focal length change, no move | Observational, retro, documentary | Very slow | "Slow optical zoom in, no camera translation" | Fair; distinguish from dolly |
| Dolly zoom (vertigo) | Dolly one way, zoom opposite; subject size constant, background stretches | Dread, realization, vertigo | Medium | "Dolly zoom: camera dollies back while zooming in, subject size stays constant, background stretches" | Only some models; name the effect and both motions, centre a still subject, one action, under 10 s (V Runway guide, 3P); one creator reported Seedance 2.5 best [no rigorous head-to-head as of 2026-10-14; checked: Runway guide, screenweaver, imaginode, X post by Travis Davids]; test 3 variants |
| Rack focus | Focus shifts between planes | Shift attention, reveal, connect objects | Smooth, about 1 s | "Rack focus from the glass in foreground to the face behind, shallow depth" | Moderate; often only partly resolves |
| Roll / spin | Rotation around lens axis | Disorientation, dream | Slow | "Slow barrel roll, horizon rotates" | Variable |
| Long take / oner | Continuous shot, no cut | Immersion, tension, showpiece | Continuous | "One continuous unbroken shot, no cuts, camera follows..." | Up to clip length only (4 to 30 s by model); chain clips with last frame |
| Snorricam | Camera fixed to actor's body | Panic, disorientation | Matches actor | "Camera mounted on the actor's chest, face fixed in frame while the background sways" | Hard; prompt "Snorricam locked to the torso, face fixed and sharp, background sways"; try image-to-video from a frame (3P Seedance guides) [no independent test as of 2026-10-14; checked: klingaio, screenweaver, Atlabs] |
| Pull focus / follow focus | Keeps moving subject sharp | Following action | n/a | "Focus follows the runner" | Mixed |

## Speed and easing vocabulary
| Word | Roughly | Feel |
|---|---|---|
| Ultra slow, glacial | 0.5 m or less over 5 s | Dread, reverence |
| Slow, deliberate | 1 m over 5 s | Premium, intimate |
| Moderate | Walking pace | Natural |
| Quick snap | Under 1 s | Impact, transition |
Easing: "constant speed then decelerate into a hold" or "ease in, ease out". Higgsfield's Prompt Bank phrases it this way (V).

## Wording template
"The camera [move] at [speed], starting on [framing A] and ending on [framing B]. One continuous shot. Subject [action]. [Camera not doing: no zoom, no tilt]."
For models that dislike negation (Runway, Veo), rephrase "no zoom" as "locked focal length, steady".

## Motivation cheat sheet
| Intent | Move |
|---|---|
| Draw viewer into a thought | Slow push-in |
| Make character smaller, withdraw | Pull-out, crane up |
| Show who is where | Slow pan or truck |
| Create fear of what is behind | Slow track behind, handheld |
| Reveal on release of tension | Pedestal up, tilt up |
| Give a hero entrance | Low-angle orbit, crane |
| Make viewer dizzy | Dolly zoom, roll, snorricam |
| Show luxury | Slow glide, gimbal, slider |

## Failure modes
- Mixed signals ("zoom and dolly and pan"): reduce to one (3P).
- Orbit drift above low speed or beyond 180 degrees: keep partial; run image-to-video to hold identity (3P).
- Wide handheld looks like earthquake: lock off or switch to gimbal (3P).
- Move reverses or does not end where stated: give an end frame where the model supports it (Kling start and end frames, Veo first and last frame) (V).
- Fast subject motion plus fast camera: speed in the edit instead.
- Duration: Veo clips 4, 6 or 8 s (V); Cinema Studio 4.0 up to 30 s (V); plan the move to fit.
