# Acting direction for AI characters
Labels: (K) craft knowledge, (3P) third-party, (H) house rule, (E) estimate, (U) unverified. Expression and gesture vocabulary lives in `asian-human-reference` (expressions-and-emotions.md, body-language-and-motion.md); this file shows how to direct with it. Eyeline mechanics: `cinematography` composition-and-blocking.md.

## 1. What AI performance can and cannot do (E, H, from studio testing)
- Strong: a held expression, a single clear emotion, a slow look, a small gesture, a walk, a head turn.
- Weak: fast shifts between emotions inside one clip, long dialogue with complex expression, two characters reacting to each other at once, subtle eye movement while talking, crying realism, laughter.
- Rule: one emotion arc per clip, one change at most. Cut between shots to show a shift, rather than ask the model to play a transition in one take.
- Models read nouns of emotion poorly and physical behaviour well. Prompt behaviour.

## 2. Emotional beats
A beat is a unit of intention. Structure per scene:
| Element | Question | Prompt output |
|---|---|---|
| Want | What does the character want right now? | Direction of gaze, posture lean toward or away |
| Obstacle | What stops them? | Tension in jaw, hands, breath |
| Tactic | How do they try to get it? | Smile, plea, avoidance, silence |
| Shift | What changes at the end of the beat? | The last second: eyes down, smile fades, small nod |
Beat sizes: setup (1 clip), pressure (1 to 2 clips), turn (1 clip), landing (1 clip held). Hold on the landing after the line (film-studio editing-and-assembly.md: hold on faces).
Beat map table (put in the brief): beat number, clip length, emotion (with intensity 1 to 3, per asian-human-reference), physical action, line (if any), what the viewer should feel.

## 3. Subtext
Subtext is the gap between what is said and what is meant. Show it with behaviour that contradicts or colours the line.
| Said | Meant | Behaviour to prompt |
|---|---|---|
| "I'm fine." | Hurt | Smile that does not reach the eyes, thumb rubbing a ring, a half-second pause before the line |
| "Go ahead." | Reluctant | Slight head tilt back, lips press, eyes flick to the door |
| "Congratulations." | Envy | Social smile (mouth only), brief jaw tension, hands tighten on a cup |
| Silence | Decision | Still face, a slow blink, shoulders settle |
Rules: one subtext per beat; do not stack two contradictory emotions in one prompt; the contradicting detail is small and physical (H). Cultural note: restraint and indirectness are common in many South and East Asian settings, so understatement often reads truer than big gestures (asian-human-reference expressions-and-emotions.md culture section, E); check region and age.

## 4. Micro-expressions and small tells
Real micro-expressions (very brief, around 0.5 second or less, K) flash across the face and are hard for models. Do not promise them. Use slow "micro-motion" instead: a short list of tells that videos can hold:
- Eyes: gaze shift, slow blink, a glance away on a hard word, softened gaze on affection; eyelid tension.
- Brows: inner raise for sadness or worry, slight furrow for thought, one-brow lift for scepticism (FACS quick map in asian-human-reference).
- Mouth: lip press, corner pull (contempt), lip bite, swallow, breath through nose.
- Jaw and neck: clench, tilt, swallow.
- Hands: ring turn, cup grip, finger tap; obey the hand-count law (higgsfield-master characters-and-consistency.md).
- Breath: chest rise, shoulder drop on release.
Prompt shape: "Medium close-up. She listens, eyes steady, then a slow blink; her lips press once; inner brows lift slightly; a small exhale." Names of tells plus timing words (slowly, once, after a beat).
Intensity ladder: level 1 (barely there, default for drama), 2 (clear), 3 (heightened, for comedy or melodrama). Default to 1 or 2 (H).

## 5. Blocking
- Blocking is where bodies go. With the cinematographer: shot size, stage (floor plan), positions A and B, entries and exits, props that carry business (cup, phone, saree end).
- Write blocking as positions plus one move per beat ("crosses from the window to the table on 'later'"), not choreography.
- Lock screen direction: character A faces screen right, B screen left; do not cross the line without a reason (cinematography coverage, 180-degree rule).
- Environmental anchors: the door, the lamp, the window; characters move relative to them across shots (higgsfield-master consistency stack).
- Hands and props: one prop per hand, each with a verb; no mid-air hand-offs (photoreal-humans hand law).
- Distance and touch: culturally set (asian-human-reference body-language-and-motion.md personal space and touch; U on many points, check with the region lead).

## 6. Eyelines
- Eyeline: where the character looks. Wrong eyelines break cuts and cause "dead eyes".
- Looking at the lens (direct address) only for ads, testimony styles or intentional breaks (disclose AI per rules); otherwise the gaze is just off the lens.
- Two-person conversation: A looks screen right, B screen left; eye heights match across singles; off-screen gaze 15 to 30 degrees from the lens axis (H, E).
- Looking at an object or off-screen action: the next shot shows it from a matching direction and the same height (cinematography composition-and-blocking.md).
- Looking up or down: match the height of the other character or object; do not let a model "float" the gaze.
- Prompt: "gaze fixed on the person off-screen right, eyes at lens height" and keep the same words for every shot of the scene.
- Reaction shots: allow time for the face to take the line in before it changes (hold 1 to 2 s).

## 7. Choosing the route
| Route | Use when | Strength | Weakness |
|---|---|---|---|
| Prompt-only (text and image to video) | Simple beats, no dialogue, cheap drafts | Fast, no performer | Little control of timing |
| Performance transfer (Kling motion control, Act-Two, Genjutsu Motion Transfer) | Specific timing, a gesture, a walk, a reaction, a speaking performance | Real timing and expression | Needs a performer, consent, clean capture |
| Native audio and dialogue (Seedance, Kling 3.0, Veo, Wan 2.5) | Short lines, fresh clip | Simple | Limited acting control |
| Lipsync pass (Lipsync Studio) | Replace or sync speech to a finished clip | Controls the audio | Mouth only; face acting stays as it was |
| Hybrid | Transfer for the body, prompt for the world, comp in VFX | Best results | More steps and credits |
Test the hardest beat first on the cheapest route, then escalate.

## 8. Direction language (give the model physical instructions)
Do: "slowly", "once", "after a beat", "without moving the head", "eyes only", "small", "barely".
Avoid: "emotional", "dramatic", "very sad", "intense acting" (vague, produces overacting), long adjectives, contradictions in one clause.
One subject, one action per beat. Keep dialogue short (about 35 words per 15 s clip, characters-and-consistency.md).
Reference vocabulary: use real actor-training concepts as shorthand in the brief (want, obstacle, tactic) but never name a living actor to imitate (H, consent and originality).

## 9. Review of a take (6 questions)
1. Does the behaviour match the beat and subtext?
2. Is the intensity at the planned level (not overacted)?
3. Do the eyelines and screen direction match the shot list?
4. Do hands, eyes, teeth, skin pass the realism checklist (photoreal-humans)?
5. Is identity and tone the same as the lock?
6. Does the last second land (a clean hold)?
Pass needs a yes on all six. Any no means refine one variable; do not reroll blindly.
