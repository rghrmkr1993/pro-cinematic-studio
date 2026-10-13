# Film scoring and ad music

Labels: F from film-scoring curricula (Berklee, see sources.md), E craft estimate. Phase 4 sound plan and stems: `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/sound-music-voice.md`.

## 1. Underscore vs source
- Underscore (score): music the audience hears and the characters do not; emotion, pace, subtext.
- Source (diegetic) music: music that the characters in the scene can hear (radio, band, a temple procession, a song in a market) (F).
- Hybrid: source music that slides into score (a radio tune becomes an orchestral cue). Plan the crossfade.
- Songs in film: picturisation (a set-piece). Hook early; hide mouths or plan lipsync.

## 2. Spotting session (F)
Producer, director, music editor, composer (or the studio's music lead) watch the picture and decide where music starts (in), where it ends (out), what it does, and the hit points. The music editor writes timestamped spotting notes.
Per scene: dramatic question, whose perspective, emotional turning point, in-point, out-point, function, tempo, instrumentation, silence zones, hit points (to the frame), cut dependencies.
Spotting table:
`Cue | TC in | TC out | Dur | Function | Emotion | Themes | Hit points | Instrumentation | Notes`
Name cues `1M1`, `1M2` (reel then number) or `MUS-<film>-<scene>-<n>`.

## 3. Cue functions (E)
Establish place and era; set mood; reveal inner feeling; foreshadow; link scenes; build pace; cover cuts; comment (irony); release tension; announce a character. Cut cues that have no function.

## 4. Themes and leitmotifs
- Give each major character or idea a motif of 3 to 8 notes with a clear rhythm.
- Develop by: change mode (major to minor), tempo, instrument, harmony, rhythm, register, fragmentation, augmentation.
- Example arc: hero theme on solo flute (alone) > cello (loss) > full strings plus drums (triumph).
- Keep a "theme map" table: motif, notes or contour, instrument, where it appears.
- Avoid overuse; reintroduce with change.

## 5. Tension and release
Build: pedal tone, slow rising pitch, tremolo strings, shrinking intervals, rising pulse rate, filtered noise, rising risers, fewer instruments (hold) then many. Release: resolve to tonic, drop out, a single warm note, silence. Use a false release then a hit for scare. Dynamic contrast matters more than loudness.

## 6. Stingers and hits
A stinger is a short sharp music hit (0.5 to 3 s) for a reveal, a button, a logo, a scare. Types: orchestral hit, braam, reverse cymbal into hit, string slam, piano low cluster, bell and boom, synth impact. Pair with a quiet gap before. Sync to the exact frame; place the hit 2 to 3 frames early because the ear lags picture slightly (E).

## 7. Silence
Silence is the strongest cue. Use it before a hit, after a death, in awe, when the line is the point. Plan as "music out at X, room tone only until Y". Never replace with dead digital silence; keep room tone (see sound-design-and-foley.md).

## 8. Scoring per genre (E)
- Romance: slow to medium, 60-95 BPM, strings, piano, solo flute or sax, warm major or Mixolydian; gentle suspensions; in Indian setting raga (Kalyani, Hindolam, Sivaranjani for longing).
- Thriller: sparse, low drones, ticking pulse, dissonance (minor second, tritone), muted brass, processed sounds, silence gaps; 60-100 BPM pulse.
- Action: 120-160 BPM, driving ostinato, staccato strings, brass hits, taiko and kicks, risers into impacts, motifs in brass; keep lead room for SFX.
- Horror: unstable pitch, glissandi, clusters, bowed metal, whisper-like voices, a lullaby twisted, long silences, sudden hits; reversed sounds.
- Comedy: light, pizzicato, woodwinds (bassoon), quirky percussion, mickey-mousing used sparingly; timing is the joke; do not play the joke, support it.
- Devotional: raga plus drone, bells, flute, veena, choir; slow, warm reverb; avoid slick EDM unless modern.
- Drama and family: simple tune, solo piano or guitar, strings under; restraint.
- Epic and period: hybrid orchestra, choir, large percussion; regional instruments for place (nadaswaram, thavil for a temple town).
- Documentary: ambient, minimal pulse, texture beds, space for voiceover.
- Sports and mass hero: stomps, claps, chants, bass drops, hero motif on brass or nadaswaram plus drums.

## 9. Briefing a composer (human)
Send: the spotting notes, the temp track described in words (not a song name), tempo map, reference of mood words, theme map, instrument palette and budget, deliverables (stems, 48 kHz 24-bit WAV, MIDI, cue sheet), number of revisions, deadline, rights (work for hire or licence, territory, term, media, AI use), credit line. Ask for a sketch (mock-up) before full production.

## 10. Ad music structures
Rule: the first beat must carry the hook; end on a clear button; leave dialogue space; use cutdown stems.
- **6 s bumper**: 0.0 to 1.0 s sonic hook (the brand sound); 1.0 to 4.5 s lift; 4.5 to 6.0 s product beat and button. Often one motif only. 100 to 125 BPM, align the hit to a bar line (2 bars at 120 BPM = 4 s; 3 bars = 6 s at 120).
- **15 s**: 0 to 2 s intro hook; 2 to 7 s build (single idea); 7 to 12 s lift or product moment; 12 to 15 s resolve and logo sting. At 120 BPM that is 7.5 bars: choose 8 bars at 128 BPM (about 15 s) or accept a short ending tail.
- **30 s**: 0 to 4 s hook; 4 to 14 s story; 14 to 24 s lift and product beat; 24 to 30 s payoff and sting. Add one variation or key change at about 20 s.
- Maths: seconds = bars x 4 x 60 / BPM. For 15 s at 128 BPM = 8 bars. For 30 s at 120 = 15 bars (pick 16 bars at 128 = 30 s).
- Cutdowns: write the 30 s first, then plan edit points on phrase ends for 15 and 6 s; ask for matching stems so the cuts are clean.
- Jingle: 1 to 3 syllable hook phrase, repeated; melody within a 5th; mnemonic, rhythmic. Do not borrow a known tune. Original words only; native check for Tamil.
- Voice and music: leave 1.5 to 4 kHz free for the voice (mixing-and-mastering.md); duck music 3 to 6 dB under speech.
- Platforms: social hook in the first 1 to 3 s; sound-off safe (captions), but design the first sound.
- Loudness: sound-music-voice.md section 8; web and social about -14 LUFS for short clips (E, platform dependent), true peak under -1 dBTP.

## 11. Music for generated video
Video generators give clip-level audio only as a guide (sound-music-voice.md section 4). Build the track from stems against the final picture. Beat map the edit: BPM, bar grid, cut points on beats; cut on strong beats for energy and on the "and" for lilt. Mark sync points to the frame before generating.

## 12. Delivery per cue
WAV 48 kHz 24-bit stems (lead, rhythm, bass, pads, FX, full mix), a 30 s, 15 s and 6 s cutdown, loop version, MIDI if human, a cue sheet (title, composer or tool, publisher, duration, usage, licence, tool and plan, date), a prompt log for AI cues.
