# Western instruments deep dive

Extends `instruments.md` section 2 (one-line table) and `film-scoring.md`; do not repeat them. Labels: E craft knowledge and standard orchestration texts, U unverified. Ranges are sounding pitch, practical (not extreme), scientific notation (middle C = C4). Never name a player or composer in prompts.

## 1. Orchestra sections, ranges, timbre
| Instrument | Practical range | Timbre by register |
|---|---|---|
| Violin | G3 to E7 (soloists higher) | low G string dark and rich; E string bright, sweet, edgy at the top |
| Viola | C3 to E6 | dark, nasal-warm, veiled; tender |
| Cello | C2 to A5 | low rich and heavy, middle singing, top intense and vocal |
| Double bass | E1 to G4 (C1 with extension) | foundation, thick, woody; pizzicato for jazz and walking |
| Piccolo | D5 to C8 | piercing, bright, playful or martial |
| Flute | C4 to C7 | low breathy and veiled, middle sweet, top brilliant |
| Oboe | Bb3 to A6 | plaintive, reedy, pastoral, sad |
| Clarinet (Bb) | D3 to Bb6 | woody low (chalumeau), clear middle, bright top; jazz to comic |
| Bassoon | Bb1 to Eb5 | dark, comic, buzzy, humorous or sombre |
| French horn | B1 to F5 | noble, warm, wide, heroic or distant |
| Trumpet | F#3 to D6 | bright, brassy, heroic, fanfare |
| Trombone | E2 to Bb4 | solemn, strong, menacing |
| Tuba | D1 to F4 | huge, foundation, comic or ominous |
| Harp | Cb1 to G#7 | shimmering, glissando, magic and ceremony |
| Timpani | D2 to A3 (set of 4 reaches higher) | pitched thunder, rolls, drama |
| Piano | A0 to C8 | any role: lead, harmony, percussion |
Choir ranges: soprano C4 to A5 (up to C6), alto G3 to D5, tenor C3 to G4, bass E2 to D4 (E).

## 2. Articulations and wording
- Legato: smooth long bows; "long legato strings". Spiccato and staccato: short, bouncing; "tight staccato strings, rhythmic ostinato".
- Pizzicato: plucked; "playful pizzicato strings", light and comic. Tremolo: rapid bow shake; "tremolo strings suspense".
- Col legno: bowing with the wood; dry and skeletal, spooky; "col legno strings, ghostly rattle". Sul ponticello: near the bridge, glassy, tense; sul tasto: soft, airy.
- Flutter-tongue (winds and brass), muted brass ("trumpet with mute, distant"), harmonics (strings, flute-like), glissando (harp, trombone, strings), swell (crescendo-decrescendo "hairpin"), sforzando, marcato, portamento (slide, vocal in strings).
- Prompt rule: one articulation per line; AI usually blends them. Say "sustained" or "short" explicitly.

## 3. Orchestration combos (E)
- Strings in unison with melody: classic film-song texture; octave doubling for warmth (violins plus cellos).
- Flute plus clarinet: airy but warm; oboe plus bassoon: dry, pastoral, ironic.
- Horns plus low strings: noble, grand; brass choir plus timpani: epic fanfare.
- Harp plus celesta plus high strings: wonder, magic, childhood.
- Pizzicato strings plus woodwind staccato: lightness, comedy.
- Low strings tremolo plus low brass swells plus bass drum: dread, suspense.
- Solo cello plus soft piano: tender intimacy; solo oboe over strings: aching melancholy.
- Doubling rule: double the melody one octave apart for power; avoid more than two doublings or the sound smears.
- Counter-melody (answer phrase) in another register keeps the lead clean.

## 4. Piano, guitars, bass, drums
- Piano: felted or close-miked piano for intimacy; bright concert grand for clarity; upright for lo-fi; sustain pedal for wash. Prompts: "felted piano, close mic, sparse", "bright grand piano, arpeggiated". Mix: low-mid 150-300 Hz, presence 3-5 kHz, panned wide for stereo piano or centre-left for a lead.
- Nylon guitar: warm, soft, folk and flamenco; steel acoustic: bright, strummed, pop; electric clean: chime and chorus; overdrive: grit; distortion: rock. Prompts: "fingerpicked nylon guitar", "strummed steel-string", "clean chorus electric". Mix: acoustics 100-250 Hz body, 3-5 kHz air, centre or doubled wide; electrics HPF 80 Hz.
- Bass: upright (round, woody, jazz); electric finger (round), pick (aggressive), slap (funk), synth sub (808, weight). Mix: below 100 Hz one source only, mono, sidechain to the kick (see `mixing-and-mastering.md`).
- Drum kit: kick (50-100 Hz thump, 3-5 kHz click), snare (200 Hz body, 5 kHz crack), hi-hat (8 kHz+), toms, cymbals; brushes soft, sticks hard; rim-shot, side-stick. Feels: straight, swing, shuffle, half-time, four-on-the-floor.
- Percussion: shaker, tambourine, congas, bongos, cajon, claps; taiko and large drums for epic impact; cymbal swell for risers.

## 5. Synths
- Pad (warm analog, glassy, choir pad), pluck, lead, arp, bass, FX. Wording: "warm analog pad, slow attack", "plucky arpeggio, 16th notes", "detuned supersaw lead", "sub bass 808, long glide".
- Role: pads fill space; arps add pulse; leads carry hooks; sub bass adds weight. Keep to 2 to 3 synth layers in a short cue (E).

## 6. Brass and woodwind solos
- Solo trumpet: heroic or lonely (muted); solo horn: noble, distance; trombone: slide glissandi and weight; sax (smoky ballad), flute (tender), clarinet (playful or jazz), oboe (plaintive), bassoon (humour or sorrow).
- Treat solos as human-sounding lines: allow breaths, phrase gaps and vibrato drift; ask "slight vibrato, breathy, close mic, imperfect timing". AI renders of brass and winds can sound flat; add a humanising layer or commission a player for hero cues (E, U).

## 7. How Indian film music fuses Western and Carnatic (E, era sound, no names)
- Unison string melody beside a vocal in a raga: the classic mid-century film-song texture (see `indian-and-tamil-music.md` section 7).
- String section answering a nadaswaram: nadaswaram states a raga phrase with gamaka; strings reply in a lush legato line, giving a wedding or celebration scene both tradition and cinema scale.
- Flute countermelody (Western flute or venu) over strings; mandolin or clarinet obbligato (an echo line) in 1960s-style songs.
- Raga over Western harmony: a Mohanam or Kalyani tune harmonised with chord pads; Hindolam or Natabhairavi works over minor chords; Kharaharapriya fits Dorian and blues-adjacent grooves (E).
- Rhythm hybrid: mridangam or thavil patterns doubled by drum kit; a kuthu or gaana beat on electronic drums with parai samples; tabla and congas for romance numbers.
- Interludes: violin runs (Western) then a Carnatic-style korvai-like rhythmic punctuation before the next verse.
- Synth era: layered pads under tambura-like drones; digital reverb on voice.
- Orchestral hero cue: brass fanfare plus nadaswaram motif plus taiko and thavil hits; avoid doubling the nadaswaram with brass in the same register (they clash in pitch and intonation).
- Pitch caution: nadaswaram and Carnatic violin use gamaka and just-leaning intonation while piano and fixed instruments are equal-tempered; keep fixed-pitch instruments to rhythm and chord pads, or let them drop out during gamaka-heavy passages.
- Prompt wording (no names): "Tamil film orchestral fusion, lush string section answers a nadaswaram phrase, thavil and drum kit, wedding celebration", "1980s orchestral folk-fusion, flute counter-melody over string runs, folk drum groove".

## 8. Mixing quick map (E)
- Strings: HPF 40 Hz (cello and bass 30), warmth 200 Hz, air 10 kHz; panned left to right in section order (violins left, cellos right).
- Brass: 700 Hz to 2 kHz body, tame 3-5 kHz; woodwinds: 300 Hz to 3 kHz; harps and bells: 2-8 kHz.
- Keep room reverb consistent across instruments; mix depth: strings close, brass back, percussion rear.
