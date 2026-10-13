# Prompt templates

## Showreel one-liners (engine test only)
- `make a dynamic 15-second motion graphics video that shows what an incredible motion designer you are, like it's your showreel for a resume. go all out.`
- Long with sound: `make a dynamic 16:9, 60-second motion graphics showreel that shows your real creative limits. S-tier sound design, no generic synth pads. Compose an original piano score and sync every cut to it. Export 1080p MP4.`
- Anti-slop: add `Avoid frames and text in the corners, the usual giveaways of AI-made video.`
- Story: `use your showreel energy, but tell a story: the history of [TOPIC] from [START] to today. 45 seconds, vertical 9:16.`
- Agency persona: `make a 30-second showreel as if you were a niche branding studio for [AUDIENCE]. Create every graphic from scratch. One accent color. Every shot is a different technique.`

## Brand film
```
Make a dynamic 20-second motion graphics video for [PRODUCT] ([URL]), with the energy of a motion designer's showreel. Go all out.

Assets
- Visit the site. Use real screenshots (Playwright), the real logo, real colors and fonts.
  Save everything to ./assets and list what you found before you animate.
- Never redraw the product UI from imagination. Crop and animate the real thing.

Story (one beat each, 2 to 4 seconds)
1. Hook: the problem in 5 words of huge kinetic type.
2. The product appears, the UI assembles itself piece by piece.
3. Three features, each as a UI moment with a cursor doing a real action.
4. One number that proves it works: [METRIC].
5. Logo lockup + [CTA].

Sound: original music, 120 BPM, synthesized in code. UI clicks and whooshes on the beat.
Format: 1080x1920 (9:16) first, then 1:1 and 16:9 from the same timeline.
Before the full render, show a contact sheet of one frame per beat.
```

## Reference intake
```
Reference: ./refs/launch.mp4 (and ./refs/frames/*.png)
1. Extract one frame every 0.5s with ffmpeg. Study them.
2. Write ./docs/style_guide.md: palette (hex), type (family, weight, tracking), shot lengths,
   transition types, camera moves, texture/grain, how text enters and exits.
3. Write ./docs/shotlist.md for a [DURATION]s video about [SUBJECT] in THAT style.
   Take the grammar of the reference, never its content, logos or characters.
4. Show me both files. Wait for my OK before any code.
```

## UI morph spec (one shape, never cut)
```
<inputs>Ask me for: product + URL, 8 to 12 UI states that tell its story, the real data shown in each state,
brand colors + fonts + one accent, a royalty-free track near 120 BPM, formats.</inputs>
<direction>Product-film UI motion. One container never cuts: every state is the same element changing size,
radius and fill while its content swaps behind a short blur. A cursor drives every change. Warm neutral canvas,
one accent. Springs with at most a tiny overshoot. Banned: bouncy easing, glows, gradients on UI chrome,
particle bursts, dead time.</direction>
<structure>120 BPM, 8 bars, something happens on every beat.
logo > CTA button > email field (typed) > loader > success check > dashboard card > chart draws itself
> tooltip on hover > cmd-K palette > toast > logo.</structure>
<build>
1. One HTML file, one canvas, window.seek(t). No CSS transitions, no timers, no carried state.
2. Closed-form springs. A value with many targets = sum of one spring per change.
3. Text inside a morphing container enters after the morph starts, leaves before the next one.
4. Tab indicators: leading and trailing edges on different springs so they stretch.
5. Beat grid from the track (numpy/librosa). Start on a downbeat. UI sounds on measured peaks.
6. Render in headless Chrome at 60 fps, 4 subframes per frame, blended for motion blur.
</build>
<gotchas>Never use will-change on anything the camera scales (blurry text). The last frame must equal the
first, cursor position and velocity included.</gotchas>
<start>Ask for the inputs, then show the state list on the beat grid before writing code.</start>
```

## Overnight director's brief
```
You are the director, animator, sound designer and render engineer for a [DURATION] film made in code.
Treat this as a multi-session production. Don't rush to a final render.
## The film in one line   [LOGLINE]
## References and inputs  ./refs/ (take the grammar, never the content); ./audio/track.wav (measure beats first);
   skills available; APIs in .env (names only); budget [$X], be economical.
## Look   palette, type, texture, camera language, banned looks.
## Beat sheet   0:00-0:02 hook; acts with timestamps; a new visual payoff every 3-5s; last frame sets up the first (loop).
## Workflow, with gates
1. docs/style_guide.md + docs/shotlist.md. Show the shot list; continue if no answer in 10 minutes.
2. Stills for every shot, contact sheet, critique.
3. Animatic at 960x540 with placeholder audio. Fix pacing before polish.
4. Full animation, polish pass, sound pass, final render.
5. Split work across subagents per chapter; write docs/ANIMATION_GUIDE.md first so all code in one style.
## Critique loop (every shot, at least 3 rounds)
Render 3-5 stills, score 1-10 on hook, readability at 360px, motion, composition, depth, sound sync, polish.
Log scores + 3 biggest problems in docs/review_log.md. Fix. Repeat until all 8+.
## Deliverables   out/final.mp4, out/loop_check.mp4, out/poster.png, out/contact.png, README.md
```

## Critique pass
```
Open out/contact.png, out/strip.png and out/phone.png and look at them properly. Be a harsh motion director.
Score 1-10: hook in first 2s, readability at phone size, motion quality (springs, no dead frames), variety
(new thing every 2-4s), composition, brand accuracy, sound sync.
List the 3 biggest problems with timestamps. Hunt for: text overlapping during swaps, anything sliding instead
of easing, corner labels and frame borders, centered-on-gradient shots, blurry scaled text, a dead beat,
a stutter at the loop seam.
Fix them, re-render only the affected seconds, show the new contact sheet and new scores.
```
