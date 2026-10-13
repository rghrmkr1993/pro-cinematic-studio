# Principles, easing, springs, timing

## The 12 principles (Disney, Johnston and Thomas) applied
| Principle | UI application | 3D/character application |
|---|---|---|
| Squash and stretch | subtle scale (0.95 to 1.05) on press/release, elastic buttons; keep volume feel | deform on impact, stretch in fast motion; preserve volume |
| Anticipation | tiny pull-back before a swipe-away, button depress before action | wind-up before jump or punch, look before move |
| Staging | one focal motion at a time, dim background (scrim), direction toward target | camera framing, silhouette readability, lighting to guide |
| Straight ahead vs pose to pose | procedural/physics (straight ahead) vs authored keyframes (pose to pose) | blocking poses first, then breakdowns, then polish |
| Follow-through and overlapping action | settle (small overshoot), staggered children lag the parent | hair, cloth, tail drag; limbs end at different times |
| Slow in, slow out | easing curves, never linear for position | ease curves on keys, arcs with spacing |
| Arcs | curved paths for shared-element moves, FAB expands on arc | joints swing in arcs, camera orbit arcs |
| Secondary action | icon wiggle or badge pulse supports main action | breathing, blinking, cloth while walking |
| Timing | duration conveys weight and importance (below) | frames per action; heavier = slower acceleration |
| Exaggeration | amplify feedback modestly (error shake 4 to 8 px) | push poses 10 to 20% beyond real |
| Solid drawing | consistent depth, shadows, perspective, scale | volume, weight, balance, correct perspective |
| Appeal | personality matches brand (calm, playful, precise) | readable character, clear silhouette |
Use few principles per interaction: timing, easing and staging do 80% of UI; add anticipation or follow-through for personality.

## Functional UI goals
Feedback (response to input within 100 ms), orientation (where did it come from/go), continuity (shared elements, View Transitions), focus (draw attention once), delight (rare). Material 3 and Apple HIG agree: motion is purposeful, quick, interruptible.

## Easing math
Normalised time `t in [0,1]`, output `e(t)`.
- Linear `t`. Quad `t^2` in, `1-(1-t)^2` out. Cubic `t^3`, out `1-(1-t)^3`. Sine `1-cos(t*pi/2)`. Expo out `1 - 2^(-10t)`. Back (overshoot) `c3*t^3 - c1*t^2` with `c1 = 1.70158`, `c3 = c1+1`. Elastic out `2^(-10t) * sin((10t - 0.75) * (2pi/3)) + 1`. Bounce (piecewise parabolas, Penner).
- Cubic Bezier `cubic-bezier(x1,y1,x2,y2)` with P0=(0,0), P3=(1,1): solve `x(s)=t` numerically (Newton, 4 to 8 iterations) then `y(s)`. y outside [0,1] gives overshoot.
- CSS `linear()` function (multi-point piecewise linear easing) can encode springs and bounces natively (Chrome 113+, Firefox 112+, Safari 17.2+ per MDN, check dates): generate points from a spring function, sample 30 to 60 points.
- Token set (use as CSS vars): `--ease-out: cubic-bezier(0.16,1,0.3,1)`, `--ease-in: cubic-bezier(0.7,0,0.84,0)`, `--ease-in-out: cubic-bezier(0.65,0,0.35,1)`, `--ease-standard: cubic-bezier(0.2,0,0,1)`.
Perception: ease-out feels responsive for entrances, ease-in feels sluggish for entrances; never use ease-in for feedback.

## Spring math
Damped harmonic oscillator for displacement `x` from target: `m x'' + c x' + k x = 0`.
- Natural frequency `w0 = sqrt(k/m)`; damping ratio `zeta = c / (2 sqrt(k m))`.
- zeta < 1 underdamped (overshoot and oscillate), = 1 critically damped (fastest no overshoot), > 1 overdamped (slow).
- Underdamped closed form: `x(t) = e^(-zeta w0 t) (A cos(wd t) + B sin(wd t))`, `wd = w0 sqrt(1 - zeta^2)`, with `A = x0`, `B = (v0 + zeta w0 x0)/wd`.
- Settling time (2%) about `4 / (zeta w0)`. Overshoot percent `exp(-pi zeta / sqrt(1 - zeta^2)) * 100` (zeta 0.5 gives about 16%, zeta 0.7 about 4.6%).
- Duration-based APIs (Apple, Motion `duration` + `bounce`): `bounce` 0 = critical, 0.2 to 0.3 subtle, above 0.5 playful.
- Numerical: semi-implicit Euler `v += ((-k*(x - target)) - c*v)/m * dt; x += v*dt` with fixed dt (1/120 s) accumulator for stability; or analytic form for exactness and scrubbing.
- Springs are interruptible and preserve velocity on retarget, which is why gestures should use springs, while choreographed sequences use durations and curves.
- Smoothing alternatives: exponential damping `x += (target - x) * (1 - exp(-lambda * dt))` (frame-rate independent lerp, lambda 8 to 20); critically damped SmoothDamp for cameras.

## Timing scales
Perception thresholds: under 100 ms feels instant; 100 to 300 ms is "a reaction"; above 1 s needs progress indication.
| Scale | ms | Use |
|---|---|---|
| Instant | 0 to 80 | hover colour, focus ring |
| Micro | 100 to 150 | press, ripple, checkbox |
| Small | 150 to 250 | tooltip, dropdown, toggle |
| Medium | 250 to 400 | modal, drawer, card expand, tab change |
| Large | 400 to 700 | page transition, hero reveal, shared element across screens |
| Cinematic | 700 to 1500 | onboarding, story sequences (use sparingly) |
| Ambient | 3000 to 20000 | background loops (slow, low amplitude) |
Rules: duration grows with distance and size; exits faster than enters; mobile slightly shorter than desktop (about 70%); large surfaces slower than small; a sequence's total under 1 s for task flows. Scale tokens in a 4-step modular scale (100, 160, 250, 400, 640 ms).
Frame views: at 60 fps 1 frame = 16.7 ms; film cuts at 24 fps = 41.7 ms; 12 fps "on twos" gives stylised look; 120 fps = 8.3 ms.

## Motion choreography
Order by importance; lead with the element that explains the change; shared-element transitions beat cross-fades for continuity; parent first, children cascade with 30 to 60 ms offsets; keep direction consistent with spatial model (forward = left/up, back = right/down depending on locale; mirror for RTL).
