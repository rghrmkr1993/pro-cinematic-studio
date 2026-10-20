# Screenplay format (Fountain)

Fountain is a plain-text screenplay markup (fountain.io/syntax) that Final Draft and other editors read. Rules below are paraphrased from the public syntax spec. Output in chat as a code block so formatting survives.

## 1. Elements and syntax
| Element | Rule | Example |
|---|---|---|
| Title page | Optional, first, `key: value` lines | `Title: Dusk at the Well` |
| Scene heading (slugline) | Line starts with INT., EXT., INT./EXT. or I/E, blank line before | `EXT. VILLAGE WELL - DAWN` |
| Forced heading | Start with a single period | `.THE OLD HOUSE` |
| Scene number | Between hash marks at line end | `EXT. TEMPLE STREET - DUSK #12#` |
| Action | Any ordinary paragraph; present tense; only what is seen and heard | `Mist lifts off the water.` |
| Character | All caps line, blank line before, none after | `MEENA` |
| Extension | In parentheses after the name | `MEENA (V.O.)`, `MEENA (O.S.)` |
| Dialogue | Lines directly under the character or parenthetical | `Neenga yaaru?` |
| Parenthetical | In parentheses under the character, sparingly | `(quietly)` |
| Transition | Upper case ending in `TO:`, or forced with `>` | `CUT TO:` |
| Dual dialogue | Add `^` after the second character name | `RAJA ^` |
| Note | Double brackets | `[[Check costume continuity]]` |
| Centered text | Wrap in `>` and `<` | `>THE END<` |
| Section, synopsis | `#` section lines, `=` synopsis lines (not printed) | `= She meets him.` |
| Boneyard | `/* ... */` hidden text | |
Slugline form: LOCATION type, place, time of day (DAY, NIGHT, DAWN, DUSK, CONTINUOUS). Time words must match the lighting you will prompt.

## 2. Style rules
- Action lines: short paragraphs, 1 to 4 lines. Present tense. No camera directions in the screenplay unless a shot is the story (then write "CLOSE ON" sparingly). Camera lives in the shot list.
- Introduce a character in caps on first appearance with age, one visual trait, one behaviour: `MEENA (22), cotton saree, ink on her fingers, counts coins twice.`
- Parentheticals: only for tone that is not obvious or for an action beat between lines. Never for stage-managing every line.
- Transitions: use `CUT TO:` rarely; cuts are implied. Use `SMASH CUT TO:` or `MATCH CUT TO:` when the edit is the idea.
- Sound: write `SFX:` lines in action only when a sound carries story (temple bell, a bus horn). The composer-sound-designer owns the rest.
- Montage and song: `MONTAGE - VILLAGE MORNING` with lettered items (A, B, C), each one image.
- Flashback and V.O.: label in the slugline or extension; keep rare.

## 3. Page = minute
One formatted page is about one minute of screen time. Ads and shorts: 6 s is a few lines, 15 s is about a quarter page, 30 s about half a page, 60 s one page. Dialogue-heavy pages play faster than action pages, so check by reading aloud with a timer. Locked script page count must match the runtime (film-studio gate G1). In AI video, assume 4 to 8 s per generated shot and a maximum of one line of dialogue (6 to 12 words) per shot.

## 4. Dual-language dialogue convention
Show three layers so every crew member can work: native script (for the voice and lipsync), transliteration (for reading and pronunciation checks), English gloss (for approval). Block form:

```
MEENA
(Tamil)
நீங்க யாரு?
Neenga yaaru?
[EN: Who are you?]
```

Rules:
1. Line 1 native script, line 2 Roman transliteration in spoken form, line 3 gloss in `[EN: ...]`. The gloss is a note and is not spoken.
2. Tag the language in a parenthetical on the first line: `(Tamil)`, `(Telugu)`, `(Hindi)`, `(Tanglish)`. Tanglish is written in Roman only; keep one line plus the gloss.
3. Transliteration follows how it is said, not how it is written: `Enna da, saapteengala?` not the formal written form. Keep colloquial endings (da, di, pa, ma, nga, la) and clipped forms. No scheme with diacritics unless the voice-director asks; see `../../indic-languages/references/subtitles-and-transliteration.md` and `tamil.md`.
4. One `script-tamil-spoken.md` carries the full spoken version for the voice-director; `script.md` carries the working version with English gloss.
5. Dialogue that overlaps uses dual dialogue (`^`), but a generator cannot do true overlap; plan it as two cut shots or add it in the sound edit.
6. Mixed lines (Tamil with English words) keep the English word in Roman inside the native line only when real speakers do that (school, office, tech words).
7. Never put the gloss into the prompt; send only the line the model should speak.

## 5. Worked mini example (Fountain)
```
Title: Tea Before the Rain
Draft date: 2026-10-14

EXT. BUS STOP, RAJAJI SALAI - EVENING #1#

Rain starts. A tin shelter, four strangers, one dry bench.

KAVYA (24), yellow kurta, laptop bag held like a shield, steps in last.

ARUN (26), grey shirt, a torn umbrella still open, grins at his own bad luck.

                                                  ARUN
(Tamil)
குடை இருந்தும் நனைஞ்சுட்டேன்.
Kudai irundhum nanainjuten.
[EN: I got wet even with an umbrella.]

Kavya looks at the umbrella, then at him. She almost smiles. She hides it in her scarf.

CUT TO:
```
(Fountain does not require the indent; centre it in the editor if wanted.)

## 6. Export and files
- Chat: Fountain in a fenced block. Files: `script.md` (Fountain text), `script-tamil-spoken.md`.
- Scene numbers: `#n#`, matched by shot IDs `S<scene>-SH<nnn>` so the cinematographer, prompt-engineer and continuity-supervisor stay aligned.
- Keep a short "continuity header" under each slugline in a note: `[[Costume: ... Prop in hand: ... Light: ...]]`.
