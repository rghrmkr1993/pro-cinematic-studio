# Rhythm and cultural soundscapes (Tamil occasions, ambience layers, solkattu)

Extends `indian-and-tamil-music.md` sections 5 and 6, `heritage-instruments.md` and `sound-design-and-foley.md` (Indian ambiences); do not repeat them. Labels: F sourced in session research 2026-10-14 (`sources.md` section "2026-10-14 additions"), E craft knowledge, U unverified. BPM values are working ranges (E). Describe the occasion and instruments; never reproduce a specific tune.

## 1. Tamil rhythm by occasion
| Occasion | Instruments and pattern | Feel and tempo (E) | Notes |
|---|---|---|---|
| Wedding (periya melam) | nadaswaram pair, ottu drone, thavil pair, talam cymbals; mangala vadyam is auspicious music (F) | rolling, festive, 100 to 140 BPM, tisra and chatusra nadai | key moments: muhurtham (the thali-tying instant) gets loud drum rolls ("kettimelam", E, U on regional use) |
| Temple festival | nadaswaram, thavil, kombu, urumi, pambai, thappu, bells and conch | processional, building, 90 to 130 BPM | chariot festival and utsavam; add crowd, bells (F, E) |
| Pongal and harvest | parai, thappu, kolattam sticks, kummi claps, folk songs, harvest calls | joyful, communal, bouncy, 100 to 130 BPM | cattle bells, pot-boiling shouts, crowd; kolam and sugarcane imagery (E) |
| Kuthu | parai, thappu and electronic drums, nadaswaram sample, chorus chants | fast dance, 100 to 140 BPM (existing base file), heavy accent on 1 and 3 | crowd shouts, whistles |
| Gaana | thappu, parai, kanjira, tin or box percussion, harmonium or guitar, gaana vocal | street, humorous and tragic, 85 to 120 BPM (E, U) | call-and-response, Chennai urban voice; social commentary (F, E) |
| Villupattu | large bow (vil) struck with sticks, udukku, ghatam, kudam, chorus echo (F) | narrative, steady, 80 to 110 BPM | story-telling voice leads; mythic and local legends (F) |
| Karakattam, kavadi | nadaswaram and thavil, or pambai and urumi, with bells | spirited, sway and spin, 100 to 120 BPM | kavadi devotees chant; murugan context (F) |
| Therukoothu | harmonium, mridangam, dholak, mugavina, loud declamation | theatrical, call and response | shows epic stories; costume, make-up |
| Silambam and martial | thappu, parai, stick clashes and shouts | sharp, aggressive | stick clacks as rhythm |
| Death rites | parai, thappu or urumi melam, nadaswaram (inauspicious), oppari laments sung by women (F) | slow, heavy, irregular, sparse | see cultural care below |
- Pairings are in `heritage-instruments.md` section D.
- Cultural care: oppari and funeral drumming are mourning practice shaped by caste history (F); do not use them as colour, do not mix them with product celebration scenes, hire native consultants, and credit real musicians. Parai and thappu are also dance and revival instruments (F), so choose the context deliberately.
- Auspicious versus inauspicious: nadaswaram plus thavil is auspicious; an urumi melam (nadaswaram, pambai, urumi) is tied to funerals and inauspicious events (F). Do not swap them casually.

## 2. Regional soundscapes (E, build as layers)
- Chennai city: Marina beach waves, auto horns, vendors, local train, Carnatic or film songs from a tea shop radio, temple bells at Mylapore, street gaana.
- Madurai and temple towns: gopuram bell echo, nadaswaram from a distance, jasmine sellers, temple tank splashes, crow calls, bus horns.
- Thanjavur and Kaveri delta: paddy field wind, frogs at night, water channels, cattle bells, village temple bells, harvest songs.
- Coastal villages (Rameswaram, Nagapattinam): sea breeze, boat motors, gulls, fish market calls.
- Hill stations (Ooty, Kodaikanal): wind in pines, mist quiet, birds, a distant bus; tea-estate bells.
- Rural festival night: generator hum, loudspeaker announcements, firecrackers, drum groups, crowd murmur.
- Home interiors: pressure cooker whistle, kolam water splash, mixer-grinder, temple bell in the pooja room, mid-morning radio, ceiling fan, coconut grater (E).
- Other Indian regions have their own sets; do not substitute.

## 3. Layered ambience recipe (authentic bed)
1. Room tone (constant, low): fan, distant traffic, wind or sea; 1 to 2 layers, -35 to -28 dB (E).
2. Mid-distance texture: crowds, vendors, birds, animals, water; loop 30 to 60 s with crossfades; vary pitch and offset to avoid repetition.
3. Close-up accents (sparse): bell strike, cooker whistle, door, footsteps, cloth; hand-placed.
4. Music from afar: radio or temple loudspeaker played through a band-pass (300 Hz to 3 kHz) with room reverb to read as "in the world".
5. Culture markers: one or two per scene (temple bell, nadaswaram snippet, call to prayer, church bell) to place location; avoid stereotypes and religious mixing unless the script has it.
6. Pan and depth: close sounds dry and wide-centre, far sounds filtered and quieter; use a low-pass at 4 to 8 kHz for distance; keep dialogue clear (music and ambience 12 to 20 dB below dialogue peaks, E).
7. Check loudness and mono; never clip.
Tool path: ElevenLabs sound effects and field recordings (3P) for textures; real recordings are better for hero cues (see `sound-design-and-foley.md`). Prompt phrases: "temple town morning ambience, distant nadaswaram, bell, crows, bicycle bells", "village harvest night ambience, frogs, distant parai, cattle bells", "Chennai street evening, auto horns, vendors, local train, distant radio" (E, U on tool quality).

## 4. Rhythm syllables (solkattu and konnakol)
- Solkattu is the spoken syllable system for Carnatic rhythm; konnakol is the vocal performance of it (F, E). Syllables map to the nadai (subdivision).
- Basic groups: 2 = ta ka; 3 = ta ki ta (also ta di mi in some schools); 4 = ta ka di mi (also ta ka ta ka); 5 = ta ka ta ki ta (2+3) or ta ki ta ta ka (3+2); 7 = ta ki ta ta ka di mi (3+4) or ta ka di mi ta ki ta (4+3); 9 = ta ka di mi ta ka ta ki ta (E, U across schools).
- Common phrase: "ta ka di mi, ta ka ju na" (chatusra, 8 syllables), "ta di gi na tom" (E).
- Mridangam syllables: tha, thi, thom, nam (open and bass tones), dhin, ta, ki, gu (E). Thavil and parai have their own vocal rhythms; they are taught orally.
- Structure of a korvai: a phrase repeated three times with a pause (gap, "karvai") and ending on the sama (F).
- Use: a 'rhythm script' for a human drummer: write the tala, nadai, syllables, and the tempo; for AI prompts: "tisra nadai pattern, spoken solkattu feel, ta ki ta ta ki ta" (U on AI reading syllables).
- Hearing it: practise counting hand-cycles: adi tala = clap, finger count 2, 3, 4 (four-beat laghu), then wave, clap, wave (two drutas) (F, E).
- Konnakol in film: used for rhythm interludes and openers; a human voice reciting syllables over mridangam adds an authentic texture.

## 5. Building a rhythm cue for a brief (checklist)
Occasion; tala and nadai (or meter); BPM; instruments; leader (who carries the tune); crowd layer (yes or no); mood (auspicious or sombre); cultural reviewer; sample source (own recording, licensed, or AI draft); loop length (bars); stem plan (percussion, melody, ambience).
