# Web animation stack choice

Support facts dated 2026-10-13 from MDN, web-platform-dx features explorer and secondary write-ups; verify on caniuse/MDN before relying on them.

## Choice table
| Need | Pick | Why |
|---|---|---|
| Hover, focus, state change | CSS transitions | zero JS, compositor friendly |
| Looping/ambient or simple sequences | CSS `@keyframes` | declarative, pausable via `animation-play-state` |
| Scroll-linked reveal, progress bar, parallax | CSS scroll-driven animations | runs off main thread, no scroll listeners |
| Page/route/element-to-element continuity | View Transitions | browser snapshots and animates between states |
| Programmatic control of a single element, with promises | WAAPI (`element.animate`) | same engine as CSS, JS control, `finished`, `reverse`, `commitStyles` |
| Complex timelines, scrubbing, SVG, text splits, ScrollTrigger pinning | GSAP | best sequencing and cross-browser scroll tools; all plugins free since 2025 per vendor announcement (verify licence terms) |
| React/Vue/JS springs, layout animation, gestures, shared layout | Motion (formerly Framer Motion; `motion` package) | `layout`, `AnimatePresence`, springs, hybrid WAAPI engine; patterns in `framer-motion-skill` |
| Designer-authored vector animation (After Effects export) | Lottie (`lottie-web`, `dotLottie` player) | tiny JSON/zip, wide support; limited expressions and effects |
| Interactive vector with state machine, inputs, events | Rive | runtime in WASM/Canvas; designer-owned logic; good for onboarding, mascots, interactive UI |
| Many objects, particles | Canvas/WebGL/WebGPU | see `webgpu-wgsl` |

## CSS scroll-driven animations
```css
@keyframes reveal { from { opacity: 0; translate: 0 24px } to { opacity: 1; translate: 0 0 } }
.card { animation: reveal linear both; animation-timeline: view(); animation-range: entry 0% entry 60%; }
.bar  { animation: grow linear; animation-timeline: scroll(root block); transform-origin: left; }
@keyframes grow { from { scale: 0 1 } to { scale: 1 1 } }
@media (prefers-reduced-motion: reduce) { .card, .bar { animation: none; opacity: 1 } }
```
Use `@supports (animation-timeline: view())` so unsupported browsers see final state. Support (2026-10): Chrome/Edge 115+ (2023-07); Safari 26 (2025-09-15); Firefox behind a flag in stable (still flagged in 152, reported 2026-06), on in Nightly; Baseline not reached. Option: polyfill (`scroll-timeline` by Flackr) or GSAP ScrollTrigger as fallback for Firefox.
Gotchas: `animation` shorthand resets `animation-timeline`, declare timeline after; use `animation-fill-mode: both`; sticky and overflow ancestors define the scroll container; named timelines `scroll-timeline-name`, `view-timeline-name`.

## View Transitions
```js
if (!document.startViewTransition) update(); else document.startViewTransition(() => update());
```
```css
.hero-img { view-transition-name: hero; }                  /* unique per page at a time */
::view-transition-old(hero), ::view-transition-new(hero) { animation-duration: .35s; }
@view-transition { navigation: auto; }                      /* cross-document (MPA), progressive enhancement */
@media (prefers-reduced-motion: reduce) { ::view-transition-group(*) { animation: none } }
```
Support: same-document API Chrome/Edge 111+, Safari 18+, Firefox 133+ (sources report Baseline newly available around 2025-10); cross-document (`@view-transition`) conflicting reports for Firefox, treat as Chromium/Safari enhancement. Name collisions break the transition; `view-transition-class` groups styles; `types` option for direction-aware transitions. Snapshots are images: text during transition is not selectable, huge elements are costly.

## WAAPI
```js
const a = el.animate([{ transform: "translateY(16px)", opacity: 0 }, { transform: "none", opacity: 1 }],
  { duration: 300, easing: "cubic-bezier(0.16,1,0.3,1)", fill: "both" });
await a.finished; a.commitStyles(); a.cancel();            // persist end state then release
```
Baseline for years across browsers (core features). Control: `playbackRate`, `reverse()`, `pause()`, `currentTime` scrubbing, `ScrollTimeline` where supported. Composite modes `composite: "add"` for layering.

## GSAP
`gsap.timeline({ defaults: { ease: "power3.out", duration: .6 } })`; ScrollTrigger for pin/scrub; `gsap.matchMedia()` to branch by reduced-motion and breakpoints; `gsap.context()` (or `useGSAP` hook) for cleanup in React; SplitText, Flip (layout transitions), MorphSVG, DrawSVG plugins. Clean up on unmount to avoid leaks; kill ScrollTriggers on route change; set `autoAlpha` instead of toggling visibility manually. Check current licence and plugin availability on gsap.com before shipping.
```js
const mm = gsap.matchMedia();
mm.add("(prefers-reduced-motion: no-preference)", () => { gsap.from(".hero > *", { y: 24, autoAlpha: 0, stagger: .06 }); });
```

## Motion (motion.dev)
Vanilla `animate(el, { x: 100 }, { type: "spring", bounce: .2 })`, `scroll()`, `inView()`, `stagger()`; React `motion.div` with `layout`, `AnimatePresence`, `useReducedMotion`, `MotionConfig reducedMotion="user"`. Bundle: hybrid mini `animate` about 2 to 3 KB (vendor claim, verify). Prefer for React UI; vanilla for small sites. Deep patterns: `framer-motion-skill`.

## Lottie
Export from After Effects (Bodymovin/LottieFiles), use `.lottie` (dotLottie, zip, smaller) with `@lottiefiles/dotlottie-web`. Constraints: keep layers and shapes low (under about 100 animated layers), avoid expressions and unsupported effects, no raster images if possible (file bloat), test on Safari and low-end Android. Respect reduced motion: show a static frame (`goToAndStop`). Render with canvas renderer for many instances, SVG for crispness.

## Rive
Author in Rive editor; runtime `@rive-app/canvas` (or `-webgl2`, or React `@rive-app/react-canvas`); state machine inputs (triggers, booleans, numbers) driven from app events; data binding (view models) in newer runtimes. Smaller than video for interactive scenes, handles pointer and listeners natively. Pause when offscreen; `.riv` binary is cacheable; provide reduced-motion state by setting a static artboard or input state.

## Combine sensibly
CSS for micro-interactions + View Transitions for navigation + GSAP or scroll-driven CSS for the one storytelling section + Lottie/Rive for illustrative moments. One library per concern; do not stack GSAP and Motion on the same element.
