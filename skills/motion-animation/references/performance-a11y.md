# Performance and accessibility for motion

For jank triage on an existing page use `fixing-motion-performance`; design baselines in `modern-web-design-standards`. GPU canvas specifics: `webgpu-wgsl/references/perf-debug-a11y-support.md`.

## Rendering pipeline for CSS/DOM motion
Style -> Layout -> Paint -> Composite. Cheapest animations only trigger Composite.
- Compositor-only (GPU, usually off the main thread): `transform` (translate, scale, rotate), `opacity`; in Chromium also `filter` and `backdrop-filter` (often GPU but can be costly), and CSS individual transform props `translate`, `scale`, `rotate`.
- Paint-triggering: `color`, `background`, `box-shadow`, `border-radius`, `clip-path` (partly), gradients; ok for small areas, expensive when large or many.
- Layout-triggering (avoid): `width`, `height`, `top/left/right/bottom`, `margin`, `padding`, `font-size`, `display`, grid/flex size changes. Emulate with transforms (FLIP technique: measure First/Last, Invert with transform, Play).
- Properties are only composited when the element gets its own layer; the browser promotes during an active animation. `will-change: transform` hints it; apply right before an animation and remove after; never on dozens of static elements (memory per layer, texture size x DPR^2).
- `contain: layout paint` and `content-visibility: auto` limit invalidation scope for large lists; `position: fixed/sticky` elements animate cheaper than scroll-handler repositioning.

## Frame budgets
60 Hz = 16.7 ms per frame, of which the browser needs about 4 to 6 ms; keep your JS plus style/layout under about 8 to 10 ms. 120 Hz = 8.3 ms (ProMotion phones, high-refresh monitors); main-thread animations drop frames first, so keep hero motion compositor-only. Long animation frames (LoAF API) and INP (target 200 ms or less at p75) show main-thread blocking. A 100 to 200 ms entrance tween that stalls on JS is worse than none.
Rules: batch reads then writes (no layout thrashing); use `requestAnimationFrame` only for JS-driven values and derive from `t`, not frame count; read time delta clamped; pause when `document.hidden` or offscreen (IntersectionObserver); avoid animating more than about 10 to 20 large blurred/shadowed layers; image animations decode ahead (`img.decode()`); prefer `translate3d` hacks only on legacy engines (not needed today); keep animated element count modest (hundreds OK as DOM, thousands go to canvas/WebGL).
JS animation libs (GSAP, Motion) run on main thread except WAAPI hybrid paths; heavy ScrollTrigger scrubbing needs `will-change` on pinned layers and `fastScrollEnd`.

## Measuring
- Chrome DevTools Performance panel: frames lane, "Rendering" tab (Paint flashing, Layer borders, Frame rendering stats), Layers panel, Animations panel for timing curves.
- Lighthouse and `web-vitals` (CLS from layout shifts due to animations; use transforms not layout changes), `PerformanceObserver` for `long-animation-frame`.
- Test on a mid-range Android with 4x CPU throttle plus a 120 Hz device if available; screenshot/timeline tools can misreport running motion: confirm visually in real Chrome.
- Budget in review: no new long task over 50 ms during animation; zero layout recalcs per frame from the animation.

## Accessibility
- Honor reduced motion: `@media (prefers-reduced-motion: reduce)`. Meaning is "reduce", not necessarily "remove": replace large parallax, zoom, slides, auto-play loops and spinning with fades or instant changes; keep small helpful feedback (colour, 100 ms opacity). Pattern: write motion in `no-preference` blocks (opt-in) or neutralise in `reduce`.
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; scroll-behavior: auto !important; }
}
```
(Blunt global rule: acceptable safety net, but prefer targeted per-component handling; it can break things that wait for `animationend`.)
- JS: `const reduce = matchMedia("(prefers-reduced-motion: reduce)")`; read `.matches`, subscribe to `change`; in Motion use `MotionConfig reducedMotion="user"`; in GSAP use `gsap.matchMedia`; Lottie/Rive show a static state; video backgrounds: do not autoplay, show a poster.
- WCAG 2.2: 2.2.2 Pause, Stop, Hide (moving content over 5 s that starts automatically needs a control); 2.3.1 Three Flashes or Below Threshold; 2.3.3 Animation from Interactions (AAA: allow disabling non-essential motion); 1.4.3/1.4.11 contrast must hold through the animation; 2.1.1 keyboard, 2.4.7 focus visible during transitions; 4.1.3 announce status changes (live regions) not only visually.
- Vestibular triggers: large-area parallax, full-screen zooms/spins, scroll-jacking, fast background motion, 3D camera fly-throughs. Cap motion distance and speed; avoid combining multiple directions.
- Focus management with View Transitions and route animations: move focus to the new content heading after the transition; do not trap focus in animating elements; `inert` the outgoing view if it remains in DOM.
- Do not hide content until JS animates it in: default visible, enhance progressively (also helps SEO and LCP). Text must remain selectable and readable; avoid animated text that is not readable at any frame.
- Test: enable OS reduce-motion (Windows: Show animations off; macOS: Reduce motion; Android: Remove animations; iOS: Reduce Motion), then walk the key flows; screen-reader pass for dynamic changes; flashing analysis tool (PEAT or Harding) for video.

## Checklist before shipping
Compositor-only properties; tokens used; interruptible; reduced-motion path; pause/stop for long loops; no layout shift; performance trace on a throttled profile; fallback state for unsupported features (`@supports`); real-browser visual check recorded.
