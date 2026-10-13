# Sound design and Foley

Labels: F standard practice or sourced, E craft estimate, 3P third-party tool facts (verify live). Phase plan, stems and QC list: `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/sound-music-voice.md` sections 1, 4 and 10.

## 1. Layers of a sound track
Dialogue, ambience bed, room tone, Foley, hard effects (SFX), designed effects, music, silence. Keep stems apart: DLG, AMB, FOLEY, FX, MUS (plus M and E for dubbing).

## 2. Ambience and room tone
- Ambience = the sound of a place (street, forest, office). Room tone = the "silence" of a room, recorded 30 to 60 s empty, used to fill gaps and match edits.
- Build beds 10 to 60 s long, loop with a 1 to 2 s crossfade (equal power). Layer: bed (steady wash) + mid details (distant voices, birds) + spot events (a horn, a door).
- Match ambience across cuts in a scene; change it on a scene change to signal place. Keep ambience level low (about 20 to 30 dB under dialogue, E).
- Perspective: close = detail and dry; far = low-passed and washed. Interior vs exterior: change the EQ and reverb.
- Never leave dead silence between sounds; the ear hears the gap as an edit.

## 3. Foley
Foley is performed sound synced to picture: footsteps (by surface and shoe), cloth (movement, rustle), props (a cup, a jar, a door handle, a soap bar), hands and body (touch, breath).
- Sync key actions precisely; add subtle sound for others.
- Record close (cardioid mic about 30 cm), dry, 48 kHz 24-bit.
- Cloth and footsteps are what makes a shot feel real; synthetic video clip audio rarely has them.
- AI route: generate single short sounds (0.5 to 3 s), pick the best, place by hand.

## 4. SFX layering
Build a big sound from 3 layers: low (impact or sub, 40 to 120 Hz), mid (body, character, 200 to 2 kHz), top (air, snap, sizzle, 4 kHz plus). Example door slam: wood thud + metal latch click + room reverb tail. Vary pitch (plus or minus 10 percent) so repeated sounds do not sound looped. Keep SFX loudness below dialogue peaks. Remove clashing frequency overlap with music (carve 2 to 4 kHz).

## 5. Whooshes, risers, transitions
- Whoosh: a swept noise (band-pass or filtered pink noise) timed to a fast move or a cut; length 0.3 to 1 s; start just before the cut.
- Riser: pitch or filter sweep up over 1 to 8 s into an impact; reverse cymbal; ends at the hit. Pair with a hit and a gap of silence 100 to 300 ms before the hit for punch.
- Downlifter or sweep down: after impacts, to release.
- Impact: low boom + hit + reverb tail. Use for logo reveals and titles.
- Transitions: sound bridges (J-cut: the next scene audio starts before the picture; L-cut: the previous audio continues). Use ambience crossfades of 0.5 to 2 s for scene changes.
- UI and app sounds: short (80 to 300 ms), soft attack, single tonal centre; one sonic family per product; test on phone speaker.

## 6. Noise types (F)
- White noise: equal energy per Hz; bright hiss; good for air, wind sweeps, snare layers.
- Pink noise: equal energy per octave (−3 dB per octave); sounds balanced, like rain or waterfall; use for speaker and room testing and for natural ambience beds.
- Brown (red) noise: −6 dB per octave; deep rumble like thunder, distant engines; good for tension low bed.
- Blue and violet exist (rising high end). Use for hiss layers.

## 7. Prompting ElevenLabs text-to-sound (3P summary of docs; verify)
- Model default `eleven_text_to_sound_v2`; duration 0.5 to 30 s (auto or set); loop option for seamless beds; `prompt_influence` 0 to 1, default 0.3 (higher is more literal, lower is more creative). Prompt limit reported as 450 characters. Output can be quiet (a test peaked near -21 dBFS): normalise or gain it up in the mix.
- Formula: [Sound source] + [material and action] + [distance and space] + [intensity] + [duration or sequence] + [style: realistic, cinematic, designed].
  - "Heavy wooden temple door creaking open slowly, large stone hall echo, close, then a soft thud, realistic, 4 seconds."
  - "Steady heavy monsoon rain on tin roof, distant thunder rolls twice, no voices, loopable, realistic."
- For a sequence, write events in order with "then" and set a duration long enough; auto length may cut it short.
- Generate separate sounds and combine them; do not ask for one complex scene.
- Ask for no music and no voices to avoid hallucinated vocals.
- Generate 3 or more variants only after the first passes review (credit discipline: `ai-music-prompting.md` section 7; spend gate: elevenlabs.md rule 1).
- Licence: confirm commercial terms of the plan in use; keep the terms snapshot in the licence ledger.

## 8. Indian ambiences (prompt recipes, E)
| Scene | Layers | Prompt seed |
|---|---|---|
| Temple bells | large bronze bell strikes with long resonant tail, small hand bells, murmur of chanting, conch blast distant, footsteps on stone | "temple courtyard morning, bronze bell ringing with long decay, distant chanting murmur, soft footsteps on stone, no music" |
| Market | vendors calling (non-intelligible), scooters and horns, metal scales, bargaining murmur, plastic bags, cooking sizzle | "busy Indian street market, overlapping unintelligible vendor calls, auto-rickshaw horns, clatter, sizzling pan, steady crowd" |
| Monsoon rain | heavy rain on leaves and roof, gutter runoff, distant thunder, frogs at night, wind in coconut palms | "heavy monsoon rain on tiled roof, water running through gutters, distant rolling thunder, frogs, loopable" |
| Train | rhythmic wheel clatter on rails, chai vendor calls, whistle, platform announcements (unintelligible), doors | "Indian train interior, steady rhythmic wheels on tracks, rattling window, distant whistle, quiet murmur" |
| Village dawn | cock crow, temple bell far, birds (koel, crows), cow bells, water drawn from a well, broom sweeping, distant radio | "village at dawn, rooster, koel call, cow bells, distant temple bell, soft breeze, sweeping broom" |
| Kitchen | pressure cooker whistle, mustard seeds popping, steel vessels, grinder | "south Indian kitchen morning, pressure cooker whistle, tempering sizzle, steel vessels" |
| Festival | dhol and parai, firecrackers distant, crowd, loudspeaker music far | "festival night street, parai drums approaching, crowd, distant firecrackers" |
| Beach and backwater | waves, boat engine putter, gulls, wind | "calm backwater, wooden boat paddling, birds, gentle ripples" |
Avoid intelligible foreground speech in ambience beds; use "murmur", "walla".

## 9. Cleaning and fixing
- Remove noise with spectral denoise (conservative), de-click, de-hum 50 Hz (India mains is 50 Hz, so hum at 50 and 100 Hz, F), de-ess, de-reverb.
- Check phase when layering stereo ambience; check mono compatibility.
- Generated SFX often has a fixed tone; add 2 to 3 dB of randomness (small EQ and pitch changes) across repeats.

## 10. Delivery
WAV 48 kHz 24-bit per stem; loops marked; names `SFX-<scene>-<n>`; licence log with source tool, model, prompt, date. QC with the list in sound-music-voice.md section 10 and loudness steps in `mixing-and-mastering.md`.
