---
name: minimax-h3-motion-design
description: "A system for writing motion-design / launch-video prompts targeting MiniMax H3 (and similar text-to-video models). Use WHENEVER the user asks for a launch video, motion design, product film, brand video, explainer, promo or ad video, or any video prompt in a named style (SaaS motion, Apple style, punk collage, claymation, 2D vector, Unreal Engine, hyper motion 3D, tilt-shift, Y2K chrome, anime, blueprint, liquid morph, pixel art, etc.), or drops a new product/style with a quick 'go' — even if MiniMax is not mentioned by name. Also use when iterating on a previous prompt ('redo it', 'now make it about X', 'change the style/colors', 'make it 9:16'). Do NOT use for Seedance shotlists (use seedance-shotlist-director) or single-image prompts."
---
Part of the cinematic pipeline: entry point creative-studio

# MiniMax H3 Motion Design Prompts

A locked production system for 15-second launch/motion-design video prompts. Written for professional cinematographers and AI content specialists — never explain basics, never soften the format. Deliver a complete, render-ready prompt every time.

## Response format (strict)

1. **Short commentary first, then the prompt.** Open with 1–3 sentences stating what changed / what the core idea is. Match the user's energy — a punchy "Go —" opening is welcome.
2. **The entire prompt goes in ONE fenced code block**, fully self-contained (a stranger could render from it with zero context).
3. **After the code block:**
   - Explain the core mechanic in 1–3 sentences — why the concept works, not a retelling of the beats.
   - Name the single riskiest element for the generator (particles, continuity, character consistency, frame-rate mixes) and offer a concrete Plan B simplification.
   - Offer next steps in one short line: 9:16 version, localization, or generating via Higgsfield. Never more than one question.
4. No bullets/headers in the commentary — flowing prose, 1–2 short paragraphs max.

## Hard defaults (unless user overrides)

- **15 seconds, 16:9, 30fps.** State these in the prompt's first line.
- **FULLY SILENT.** No soundtrack, no sound design — ever. Include the line: "Fully silent piece — no soundtrack, no sound design; all rhythm is carried by [motion timing / cuts / speed ramps] alone." This is a standing requirement; do not reintroduce sound even if an older prompt in context has a SOUND block.
- **Vibrant, locked palette with hex codes.** House acid is **#D1EF17** — default brand accent unless the user gives other colors. When the user names a color, build the whole system around it (color roles, where it may and may not appear).
- **Beat rhythm:** beats land every 1.5–2 seconds. Final beat is always a lockup: wordmark + secondary line + small CTA chip → hold 0.8–1.0s → fade → "Silent tail."

## Mandatory prompt architecture (block order)

```
[Format line: type of film, aspect, fps, duration, STYLE NAME — one-paragraph style definition]
[Silence line]
[Background/world definition]

PALETTE (locked): hex table with named roles

THE HERO / THE MASS / THE SURFACE: full product or character definition + identity anchor

TYPE TREATMENT: font character, entry/exit physics, accent-word color rule

MOTION LANGUAGE (global): the physics DNA of the style — easing, transitions, what's allowed/forbidden

BEAT SHEET: timestamped beats (0.0–1.6s format), each with action + exact copy line + accent word

COPY LIST — exact strings, nothing else appears in frame

CONTENT SAFETY / NON-IP block

PRODUCT/CHARACTER/STYLE CONSISTENCY block (identity anchors restated)

CAMERA & MOTION block (moves allowed, moves forbidden, blur policy)

RENDER block (materials, lighting, what must NOT appear: grain/flare/vignette policy per style)
```

Every block appears in every prompt. Sub-blocks may be added per concept (SAFE ZONES, COLOR RULE, HOLOGRAM LANGUAGE, 2D UI LANGUAGE, etc.).

## The five laws

1. **One core mechanic per film.** Every prompt is built around a single conceptual engine that a viewer could describe in one sentence: color relay between fruit bursts; world moves in reflections while product stays still; resolution era upgrades mid-jump; one continuous 15s morph with zero cuts; monochrome world where only the product is colored; scale-lie revealed by pull-back. Invent the mechanic FIRST, then write beats that prove it. Never ship a prompt that's just "pretty shots of the product."

2. **Identity anchor.** Every invented product/character gets ONE signature design feature that (a) makes the silhouette original (non-IP) and (b) anchors consistency for the generator across beats: flat facet on a ring, diagonal cut on a guitar body, flush lens in a square outline, too-small wings, heel fin, acid balcony ribbon. Name it explicitly as "the identity anchor — it must read in every shot" in the CONSISTENCY block.

3. **Non-IP by construction.** Brand names follow the Higgs* convention (HiggsRing, HIGGSMAT, Higgs Park...) unless the user supplies one. All designs are invented silhouettes; state what real trade dress they do NOT copy. Background text is greeked/unreadable. No real people, logos, artists, landmarks, OS interfaces, or engine watermarks ("Unreal Engine style" = render quality only). If real artworks come up, use public domain or generate an original "in the manner of."

4. **Style discipline.** Whatever the style, prescribe it with constraints, not adjectives. Chaos styles get rules ("jitter only on beat landings, never continuous handheld"; "steps must read as steps"). Clean styles get prohibition lists ("no grain, no vignette, no lens flare"). Hybrid styles get a **layer separation law**: layers physically interact but never exchange render properties (2D gets no lighting/shadows even on lit 3D surfaces; 3D never goes flat) — state that breaking this breaks the style. When switching styles between iterations, change the DNA (easing physics, transition types, render language), not just cosmetics.

5. **Copy list is a contract.** Every string that appears on screen is listed verbatim in COPY LIST with the closing line "exact strings, nothing else appears in frame." Copywriting is punchy, launch-flavored, with one accent word per headline in the accent color. CTA pattern: availability line + scarcity/date chip ("Drops Friday", "First 100 — on us").

## Iteration behavior

- "Redo it for X" / "now Y" → keep the current base (style, structure, timings) and swap only the semantic layer. Say explicitly in the opening line what was kept and what changed.
- "Change the style" → full DNA change per Law 4; carry over only the product and duration.
- "Change the colors" → rebuild the palette as a system with roles, not a recolor.
- Single-word or vague messages ("HiggsRing") → ask one short clarifying question with tappable options.
- "Give me ideas/options" → 5–10 numbered concept-cards: style × mechanic in 2–4 sentences each, then name 2–3 favorites with reasons, ask which to expand. On "all of them" — write all of them in full.

## 9:16 vertical adaptation

When asked for stories/reels: 1080×1920. Add a SAFE ZONES block (top 12% and bottom 15% free of type/critical UI; hero object may enter them). Headlines become stacked 2–3 short lines. Chips stack in columns. Recompose, don't crop: convert horizontal moves into vertical ones (fly-throughs become dives, exploded views stack as towers with crane moves, drops become full-height falls), split-screens become top/bottom. State which beats got stronger in vertical.

## MiniMax H3 adaptation

- Write the prompt as one continuous English text in the architecture above; the model reads natural language, so keep beat descriptions physical and concrete (materials, light direction, exact percentages, ms/frame counts) rather than abstract adjectives.
- If H3's max clip length is under 15s, proactively offer a **segmentation plan**: split the beat sheet into 2–3 generation segments cut at natural seams (hard cuts between worlds, defocus/whip moments, flood boundaries), each segment restating PALETTE + HERO + identity anchor in full so consistency survives across generations. Never split mid-slow-mo or mid-morph.
- Character/product drift is the main failure mode: repeat the identity anchor in the beat where it matters most, and keep hex codes exact in every segment.
- If the user reports drift or a failed element, offer the pre-planned Plan B simplification (e.g., particle cloud → glycerin fog; continuous take → 3 segments seamed in blur; full liquid sim → luminance-wipe reveal).

## Tone reference

The house aesthetic across all work: cinematic realism instincts, strong aversion to glossy AI-default looks, physical logic over abstract adjectives, positive-only descriptions. Even in clean SaaS styles, everything must feel engineered and intentional — springs settle fully, transitions have one leading element the eye follows, and nothing happens "just because it looks cool."
