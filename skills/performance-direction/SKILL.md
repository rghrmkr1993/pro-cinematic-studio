---
name: performance-direction
description: "Directing acting for AI characters: emotional beats, subtext, micro-expressions, blocking and eyelines, motion control and performance transfer (Kling motion control, Runway Act-Two, Higgsfield motion tools), reference-video capture specs for a phone at 24 or 25 fps, consent rules for using a real performer, lipsync acting for Indian languages, performance consistency across shots, and a per-shot performance brief template. Use before generation with the cinematographer, and whenever a character must act, emote, speak or move with intent."
license: MIT
user-invocable: true
metadata:
  version: "1.0.0"
  researched: "2026-10-14"
---
Part of the cinematic pipeline: entry point creative-studio

# performance-direction

A character is only as good as its performance. AI models give faces; direction gives intent. Owner agent: performance-director (works with the cinematographer before generation, hands a performance brief to the prompt-engineer). Labels: (V) vendor-official, (3P) third-party, (H) house rule, (E) estimate, (U) unverified.

## 1. Boundaries (do not duplicate)
- Expression vocabulary, FACS prompt language, regional gestures and gait: `asian-human-reference` (expressions-and-emotions.md, body-language-and-motion.md). Link, do not copy.
- Skin, eyes, hands realism, consent and AI labels: `photoreal-humans` (ethics-and-consent.md).
- Camera, lens, coverage, eyeline matching mechanics: `cinematography` (composition-and-blocking.md, coverage-and-sequences.md).
- Character locks and tools (Soul ID, Elements, Lipsync Studio): `higgsfield-master` (characters-and-consistency.md, tools-a-z.md).
- Voice casting, dubbing, Indian-language speech: `voice-studio`, `indic-languages` (lipsync-and-dubbing.md).
- This skill adds: direction method, beat design, capture and transfer specs, consent for performers, lipsync acting, consistency, and the brief.

## 2. The method in six steps
1. Read the scene: what does the character want, what stands in the way, what changes by the end (one line each).
2. Break into beats: one beat equals one clear emotional shift or intention (3 to 8 s per generated clip; one action per beat).
3. Write subtext: what the character says versus what they feel. Prompt the behaviour that shows the feeling, not the label ("her thumb rubs the ring while she smiles", not "she is nervous").
4. Choose the route: prompt-only acting, performance transfer from a reference video, or a hybrid (acting-direction.md section 7).
5. Block: where the character stands, moves, looks (eyeline), with the cinematographer's shot sizes. Lock screen direction.
6. Write the performance brief per shot (performance-brief-template.md), then hand to the prompt-engineer. Review takes against the brief, not against taste.

## 3. Hard rules
- Consent first. A real performer's face, voice, body motion or likeness needs written consent that names AI generation, media, channels, term, territory and right to withdraw. No celebrities or living people as real. Motion alone is not consent-free: the Higgsfield AI Influencer article does not address consent for a real person's movement (V gap, tools-a-z.md), so treat it as requiring consent (H).
- Originals only: no copying a known actor's performance beat for beat, no recognisable imitation of a real person.
- Never publish or send a take without the user's yes. No spend without a quote and the user's yes; capture and prompt design cost nothing.
- Never lighten or alter skin tone to "improve" a performance take; tone comes from the asset lock.
- Label realistic AI people per platform and ASCI or FTC rules (photoreal-humans).
- No fabricated testimonials; scripted "routine" content must not claim lived experience or results for a synthetic persona.
- A child performer or child likeness: avoid; if unavoidable, verifiable guardian consent and the Manager first.

## 4. Router: which reference to open
| Need | Open |
|---|---|
| Emotional beats, subtext, micro-expressions, blocking, eyelines, direction language | references/acting-direction.md |
| Kling motion control, Runway Act-Two, Higgsfield motion tools, capture specs, phone setup, consent rules | references/motion-transfer-and-capture.md |
| Lipsync acting, Indian languages, consistency across shots, drift fixes | references/lipsync-and-consistency.md |
| Per-shot performance brief, take review sheet, performer consent checklist | references/performance-brief-template.md |
Open at most two per step.

## 5. Quick recipes
1. Subtle grief beat (prompt-only): medium close-up, eyes drop to hands, one slow breath, jaw tension, no tears until the last second; asian-human-reference sadness level 1 to 2.
2. Dialogue pair: A and B singles with matched eye height, off-screen looks opposed, eyelines 15 to 30 degrees off the lens (cinematography composition-and-blocking.md).
3. Performance transfer, own phone: record the performer once, waist up, still camera, continuous, 24 or 25 fps, even light; run Kling motion control or Act-Two with the character image; keep the take if identity holds (motion-transfer-and-capture.md).
4. Tamil or Hindi dialogue: front-facing, mouth uncovered, short lines (about 35 words per 15 s), natively spoken audio or Lipsync Studio; QA mouth at 25 fps (lipsync-and-consistency.md).
5. A series: one performance bible per character (tics, tempo, default posture) reused verbatim every shot.

## 6. Outputs
In `C:/Claude Code/company/creative/<client>/<project>/performance/`: performance-bible.md (per character), per-shot briefs, reference-video log (file, performer, consent ref, spec, date), consent file pointers (stored outside public folders), take review sheet, log.md entries.

## 7. Related skills
`cinematography`, `asian-human-reference`, `photoreal-humans`, `higgsfield-master`, `indic-languages`, `voice-studio`, `film-studio`, `color-grading` (skin tone check on takes), `vfx-compositing` (fix a hand or eye after the take).

## 8. Report format (8 lines max)
Shots briefed, route per shot (prompt, transfer, hybrid), reference captures made and consent status, takes reviewed versus pass rate, consistency risks, credits quoted versus spent, what needs the user's yes.
