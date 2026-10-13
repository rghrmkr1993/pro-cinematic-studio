---
name: motion-animation
description: "Motion design for web UI and 3D in code: the 12 animation principles applied to interfaces, easing and spring math, timing scales, keyframe vs procedural vs physics animation, skeletal animation, IK, blend shapes and morph targets, camera motion grammar, and the web stack choice (CSS scroll-driven animations, View Transitions, WAAPI, GSAP, Motion, Lottie, Rive), compositor-only performance for 60/120 fps, and reduced-motion accessibility. Includes a router to existing framer-motion, motion-reel and hyperframes skills. Use when deciding how something should move and with which tool."
---
Part of the cinematic pipeline: entry point creative-studio

# Motion and animation

Decide how things move, how long, with what curve, using which technology, and how to stay fast and accessible.

## Router (link, do not repeat; load one)
| Job | Skill |
|---|---|
| React/Next UI animation patterns (stagger, parallax, 3D, gestures, charts) | `framer-motion-skill` |
| Perf triage of janky animation | `fixing-motion-performance` |
| Design baseline (motion values, when heavy tech is justified) | `modern-web-design-standards` |
| Video from code with seek(t), Playwright, ffmpeg, critique loop | `motion-reel` |
| HTML-to-video compositions, GSAP timelines, keyframes, studio | `hyperframes` (`hyperframes-core`, `-animation`, `-keyframes`, `-motion-graphics`, `-slideshow`, `-cli`) |
| React-based programmatic video | `remotion-create`, `remotion-render`, `remotion-docs` |
| GPU shaders, particles, compute motion | `webgpu-wgsl` |
| Lighting, materials, engine choice | `graphics-rendering` |
| Generative 2D motion art | `anthropic-skills:algorithmic-art` |
| Game feel / Godot / Unreal animation | `godot`, `unreal-skill` |
| Cinematic AI video prompts | `01-cinematic` and the Higgsfield pack (`higgsfield-master`) |

## Decision gate
1. Purpose first: feedback, orientation, continuity, or delight? If it does none, remove it.
2. Can CSS alone do it (transition, `@keyframes`, scroll-driven, view transition)? Use CSS.
3. Needs sequencing, scrubbing, SVG morph, complex scroll choreography: GSAP (or Motion for React).
4. Designer-authored illustration/icon: Lottie. Interactive states and logic in the animation: Rive.
5. 3D scene motion: three.js/engine animation system plus camera grammar (`references/mechanics-animation.md`).
6. Video deliverable: `motion-reel`, `hyperframes`, or Remotion.
Tool table with support dates: `references/web-stack.md`.

## Workflow
1. Write the motion brief: purpose, trigger, duration, easing, reduced-motion variant, fallback.
2. Pick tokens (durations, easings, distances) once; reuse everywhere (`references/principles-easing-timing.md`).
3. Prototype with CSS or the simplest tool; only escalate when a requirement forces it.
4. Animate compositor-only properties (`transform`, `opacity`, some `filter`); avoid layout properties (`references/performance-a11y.md`).
5. Add reduced-motion handling before polish; test with the OS setting on.
6. Verify in real Chrome plus one other engine; check frame time in the Performance panel. Timeline screenshots and computed styles can lie about running motion (known lesson: verify motion visually in a real browser).

## Defaults (use unless the brief says otherwise)
- Durations: micro feedback 100 to 150 ms; small UI (toggle, tooltip) 150 to 250 ms; medium (menu, card, modal enter) 250 to 400 ms; large/page 400 to 700 ms; ambient loops 3 to 20 s. Exit 60 to 70% of enter duration.
- Easing: enter `ease-out` (decelerate), exit `ease-in` (accelerate), move-on-screen `ease-in-out`; custom `cubic-bezier(0.2, 0, 0, 1)` (emphasized decelerate) or `(0.16, 1, 0.3, 1)` (out-expo feel). Linear only for progress, opacity cross-fades in loops, scroll-linked.
- Stagger 30 to 60 ms per item, cap total at 400 to 500 ms.
- Distances: 8 to 24 px for UI entrances; bigger travel needs longer duration (about 1 ms per 1 px beyond 100 px as a rule of thumb).
- Spring defaults: stiffness 170 to 260, damping 20 to 30, mass 1 for UI; bouncy only for playful brands.
- Animate in and out symmetrical where the user can reverse (interrupt-safe: retarget from current value).

## Pitfalls
- Animating `width/height/top/left/margin/box-shadow` at scale: layout or paint per frame.
- `will-change` everywhere: memory bloat; set on active elements only, remove after.
- Scroll-jacking and parallax that fights native scroll; hijacked wheel breaks accessibility.
- No reduced-motion path; auto-playing loops without pause (WCAG 2.2.2); flashing (WCAG 2.3.1).
- Entrance animations that delay content (LCP) or hide content when JS fails: default to visible, enhance.
- Timelines scrubbing with non-deterministic sources (`Date.now`, random) in video renders: seed and drive by time.
- Easing mismatch between elements moving together; unify tokens.
- 3D camera moves with constant speed look robotic; ease and add micro handheld noise (small amplitude).

## Reference map
| Topic | File |
|---|---|
| 12 principles for UI/3D, easing and spring math, timing scales | `references/principles-easing-timing.md` |
| Keyframe/procedural/physics, skeletal, IK, blend shapes, morph, camera grammar | `references/mechanics-animation.md` |
| CSS scroll-driven, View Transitions, WAAPI, GSAP, Motion, Lottie, Rive | `references/web-stack.md` |
| Compositor, budgets, reduced motion, testing | `references/performance-a11y.md` |

## Sources consulted (paraphrased)
Disney's 12 principles (Johnston and Thomas, "The Illusion of Life"); Material Design motion and Apple HIG motion guidance; MDN (CSS animations, scroll-driven animations, WAAPI, View Transitions); web.dev and Chrome DevRel articles on animation and compositing; GSAP, Motion, Lottie (airbnb/lottie-web, dotLottie), Rive docs; glTF animation spec; Robert Penner easing equations; The Book of Shaders for procedural motion.

## Output contract
Motion spec (tokens table), implementation in the chosen stack, reduced-motion variant, support note with date, measured or reasoned frame cost, and what remains unverified.
