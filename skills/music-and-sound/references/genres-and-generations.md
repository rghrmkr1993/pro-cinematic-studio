# Genres and generations

Labels: F widely documented, E craft estimate. Use for era wording in prompts ("1980s gated-reverb pop feel"). Never name a song or artist; era and genre words only.

## 1. Decade signatures (global pop and film music)
| Decade | Sound and gear | Production signature |
|---|---|---|
| 1950s | upright bass, brushed drums, electric guitar arrives, sax, big band, early rock and roll, crooners, mono | slapback echo, close mic, warm tape, little compression |
| 1960s | Beatles-era band format, Motown rhythm section, tambourine, fuzz guitar, sitar crossover, string sections, stereo emerges | tape saturation, spring reverb, tracked live, hard-panned stereo |
| 1970s | Rhodes, clavinet, wah guitar, disco strings and four-on-floor, funk bass, early Moog and ARP, prog and arena rock, reggae and dub | long tape delay, big live drums, analog warmth, orchestral disco, dub echo |
| 1980s | DX7 FM keys, Linn and 808 drum machines, gated reverb snare, chorus guitar, synth bass, new wave, hair metal, early hip-hop | digital reverb, glossy polish, big drums, MIDI sequencing |
| 1990s | sampling, breakbeats, house and techno, grunge guitars, R&B with swing beats, boy-band pop, Eurodance, Britpop, early trance | hard compression, loud masters begin, sampler grit, CD clarity |
| 2000s | Pro Tools, Auto-Tune as effect, crunk and dirty south, nu metal, emo, electro-house, mp3 era, reggaeton | loudness war brickwall, tuned vocals, bright and compressed |
| 2010s | EDM festival drops, trap hats and 808 subs, streaming pop, indie folk (stomp, clap), future bass, melodic rap, K-pop global, Afrobeats rise | sidechain pumping, wide stereo synths, sub bass, vocal chops |
| 2020s | bedroom pop, lofi beats, hyperpop, drill, amapiano, Afrobeats global, phonk, cinematic hybrid trailers, AI-assisted production, short-form hooks | loudness normalised for streaming, dynamics returned, intimate close vocals, TikTok-length hook in first 5 s |

## 2. Genres (global)
Each entry: tempo (E), instruments, production, prompt wording.

- **Lofi hip-hop** 60-90 BPM. Dusty Rhodes or piano with jazzy 7th and 9th chords, vinyl crackle, soft boom-bap drums with lazy swing, mellow bass. Low-pass filtered, tape wobble, side-chained gently. Prompt: "lofi chillhop, warm Rhodes, vinyl crackle, laid-back swing drums, 78 BPM, no vocals".
- **EDM** 120-140. Supersaws, risers, snare rolls, kick and sub, vocal chops, build then drop. Heavy sidechain, bright master. Subgenres: house (120-128, groove), techno (125-140, hypnotic), trance (128-140, arpeggios), dubstep (140 half-time wobble bass), drum and bass (170-176, rolling breaks). Prompt: "melodic house, 124 BPM, plucky arpeggio, warm sub, 16-bar build, drop at 0:30".
- **Hip-hop** boom bap 80-100: sampled soul loops, punchy kick and snare, scratches. Trap 130-170 (half-time): 808 sub slides, rolling hats, dark pads. Drill: sliding 808, sparse tense melodies. Prompt: "dark trap, 140 BPM half-time, sliding 808, triplet hats, sparse bell melody".
- **Cinematic and orchestral hybrid** 60-140. Strings ostinato, brass swells, taiko hits, braams, synth pulses, choir pads, risers. Wide reverb, big dynamics. Prompt: "epic hybrid orchestral, low string ostinato, taiko, rising brass, 120 BPM, builds to a full hit at 0:20".
- **Ambient** 40-70 or rubato. Pads, drones, granular textures, field recordings, long reverb. Prompt: "ambient, evolving warm pads, slow filter motion, no drums, no melody hook".
- **Jazz** swing 100-200. Upright bass, ride cymbal, piano comping, sax or trumpet. Chords ii-V-I, extensions. Subgenres: bebop (fast), cool, bossa nova (Brazilian 4/4 with guitar syncopation, 110-130), smooth jazz. Prompt: "jazz trio, brushed drums, walking upright bass, piano, medium swing 120 BPM".
- **Rock** 100-180. Distorted guitars, bass, live drums. Subgenres: classic (blues-based), punk (fast, three chords), indie (jangly), metal (down-tuned, double kick), shoegaze (wall of reverb). Prompt: "indie rock, jangly clean guitar, tight live drums, 128 BPM, raw room sound".
- **Pop** 95-130. Hook-first, verse-prechorus-chorus, vocal-forward, tight drums, synth bass, bright top. Prompt: "modern pop, 112 BPM, punchy kick, finger snaps, bright synth hook, catchy chorus".
- **K-pop** 100-140. Genre-switching within one song (verse in trap, chorus in EDM, bridge in ballad), multiple vocalists with rap parts, big dance breaks, English and Korean mix, tight choir stacks, polished production. Prompt: "K-pop dance track, 118 BPM, tight vocal stacks, trap verse, big EDM chorus, dance break at the bridge".
- **Afrobeats** 98-115. Interlocking percussion, log drum and shakers, syncopated kick, melodic guitar, warm smooth vocals, call-and-response. Amapiano (South Africa): 110-115, log-drum bass, jazzy piano, shaker. Prompt: "Afrobeats, 102 BPM, syncopated drums, shakers, clean guitar riff, warm bass, laid-back groove".
- **Reggae and dub** 60-90 one-drop, skank guitar on offbeats, bass-led.
- **Country and folk** acoustic guitar, banjo, fiddle, storytelling, 90-130.
- **R&B and soul** 60-100, smooth chords, layered vocal harmonies, finger-snap or live groove.
- **Latin and reggaeton** 90-100 dembow rhythm. **Salsa** 160-220 clave-based.
- **Classical** forms: symphony, concerto, chamber; use "chamber strings" for intimacy.
- **Electronic experimental** IDM, synthwave (80s retro, 100-120, arpeggio and gated snare), vaporwave (slowed, pitched down).
- **Gospel and choir** call and response, organ, handclaps, 70-120.

## 3. Genre mixing rules (E)
One primary genre, one flavour: "Afrobeats with a Carnatic flute melody", "lofi with tabla loop". Give the primary a clear tempo and the flavour a clear instrument. More than two genres confuses models and results in muddy output. The ElevenLabs genre-switch behaviour is reported conservative for hard style breaks (3P); build separate sections or tracks instead.

## 4. Era wording that is safe
Good: "1970s soul-funk groove with clavinet and horn stabs". "Late-1980s synth-pop feel, gated reverb snare". "Mid-1990s dance with piano house stabs".
Bad: naming a song, an album, an artist, "like [artist]", "cover of", "sounds like the hit from [film]".

## 5. Production signature checklist per brief
Space (dry room, plate, hall, gated), tape or digital, drum character (live, programmed, sampled), bass character (upright, synth, 808), vocal character (dry, doubled, tuned), loudness era (dynamic 70s, loud 2000s, streaming 2020s), stereo width, noise (vinyl, tape hiss). Put 3 of these into the prompt.

## 6. Genre by use case (ads and film)
Beauty and wellness: soft acoustic pop, ambient, gentle lofi. Tech: minimal electronic, pulse synths. Food: playful, acoustic and percussion. Sports: trap or rock energy. Luxury: slow piano, strings, sparse. Youth social: hyperpop, trap, short punchy hook. Festival and devotion (India): folk percussion plus nadaswaram, or raga-based ambient (see Indian reference). Corporate explainer: light electronic with steady pulse and no lead melody under speech.

## 7. Cultural care
Do not use a genre as costume. Fusion needs a native-musician check (instrument tuning, rhythm cycle, vocal style). Ask a reviewer for K-pop Korean lines, Afrobeats Yoruba or Pidgin lines, Tamil lines.
