# Sound, music and voice (Phase 4, planned in Phase 2)

Sound is half the film. Generators give clip-level audio; a feature needs a designed track: dialogue, Foley, ambience, effects, score, mixed to a standard. Owner: creative-director (sound intent), fullstack-engineer (stems, mix, ffmpeg), qa-tester (loudness, sync), tech-writer (licence log).

## 1. Sound plan per sequence
Dialogue (clean, intelligible), ambience bed (room tone, location), Foley (footsteps, cloth, props, hands), effects (hard FX, design), score and songs, silence (scripted). Make a spotting list per scene: where music enters and leaves, what is loud, what is silent. Keep stems separate until the final mix: DLG, FOLEY, AMB, FX, MUS, plus M and E (music and effects without dialogue) for dubbing.

## 2. Dialogue and voice casting
- Voice bible per character (bibles-and-continuity.md section 2): language, accent, age, pitch, pace, emotional range, sample file.
- Casting sources (choose per film, record the choice and licence): (a) native audio of the video model (Veo 3.1, Kling 3.0, Seedance voice profiles keep a voice across scenes, 3P), (b) TTS or voice-design tools (ElevenLabs type) with commercial licence, (c) hired voice actors, recorded and consented, then optional voice-to-voice conversion, (d) clone of a real voice only with written consent.
- Never clone or imitate a real or celebrity voice without documented consent; no soundalike of a known person.
- Generate dialogue per line, not per scene: gives timing control and retake control. Name files `AUD-S03-SC07-SH020-DLG-T02.wav`. Keep takes under 8 to 12 s.
- Direct performance with emotion words plus pace plus intent; record 3 takes for hero lines and pick; keep breath and room tone.
- Record or generate at 48 kHz, 24-bit; keep lines dry (no reverb) so the mix can place them in space.
- Native-speaker review of every language and accent: pronunciation, stress, regional phrase, and register (languages-and-localization.md).

## 3. Lipsync
- Easiest: the video model generates lips and voice together (Kling 3.0 native lipsync in a handful of languages, Veo 3.1, 3P); verify per language.
- Pre-recorded line to picture: use a lipsync tool (Higgsfield Lipsync Studio, 18 plus languages, 3P; Sync or similar) on the approved shot; check teeth, lip shape and head motion; reject sync drift.
- Cheaper: shoot dialogue shots so lips are hidden or distant (over the shoulder, back of head, silhouette, wide, reaction), and cut to a face only on key lines.
- Test sync on a sample of 3 shots before committing a language.
- Frame accuracy: sync check at 0, 50, 100 percent of the film.

## 4. Foley and ambience
- Build ambience beds per location (10 to 60 s loops, crossfaded), recorded or generated or licensed; room tone under every scene.
- Foley: footsteps per surface and shoe, cloth movement, prop handling (the compass, the door); sync to picture on key actions only, subtle elsewhere.
- Sources: licensed libraries, original recordings, AI sound effect generation (verify licence for commercial use), model-generated clip audio as a reference only unless its licence is clear.
- Use the model's native clip audio as a guide track, then replace it with the designed track; native audio rarely matches across a sequence.

## 5. Score and songs
- Score plan: leitmotifs per character or idea, instrumentation palette per world, tempo map per sequence; temp music in the animatic marked TEMP and replaced.
- Sources: commissioned composer (clean rights), licensed library (sync licence), AI music generation (Suno, Udio type, Stable Audio and others), cleared existing songs (sync plus master licence).
- Music film: lyrics and melody before picture; beat map for the edit (BPM, bars, section timestamps); lip-sync singing is hard, hide mouths or use stylised visuals.
- Indian film music: raga or regional folk palette per setting, playback singer voice (consented), song picturisation as set pieces (E).
- Export music as stems, 48 kHz 24-bit, with cue sheet.

## 6. AI music licensing (3P, changing quickly, 2026-10-13; read each tool's live terms; not legal advice)
- Settlements and deals: UMG and Warner settled with Udio and Warner settled with Suno in late 2025, with licensed models promised for 2026; UMG and Sony litigation against Suno was still active in spring 2026, sources conflict on Sony versus Udio; a musicians' union sued UMG and Warner in June 2026 over compensation.
- Suno: paid tiers grant commercial licence to outputs (language moved from "ownership" to a licence), export caps apply; free-tier output is non-commercial. Udio: export is gated and the platform behaves as a walled garden, so it is a poor choice for soundtrack files unless the live terms allow download and commercial sync.
- Rules: (1) use only paid tiers with a written commercial licence, keep the terms page snapshot and invoice in `ledgers/music_licences/`; (2) no prompts naming artists or songs; (3) run a similarity check and listen for lyric or melody resemblance; (4) in the US, AI output with no human authorship is not copyrightable, so human-composed or human-edited parts protect the score (Copyright Office report Part 2, 2025, F); (5) a distributor or content ID may flag AI tracks, so prefer commissioned or library music for the main theme and release; (6) keep a cue sheet with source, licence, tool, date.
- Library and commissioned music remain the lower risk path for features going to festivals or OTT; AI music is strong for temp, shorts and YouTube-first films.
- Existing songs: need sync licence (publisher) and master licence (label), territory and term; none from memory.

## 7. Mix
- Premix by stem, then final mix with dialogue first (dialogue sits at the loudest stable level), music ducked under speech (sidechain compression, 3 to 6 dB), ambience steady, effects accents, music up in silence.
- Stereo 2.0 for web, 5.1 for cinema or OTT if required (stems to six mono WAVs L, R, C, LFE, Ls, Rs for DCP).
- Check on laptop speakers, phone, headphones and a reference monitor.
- Mastering: loudnorm two-pass (editing-and-assembly.md section 4) after the creative mix, then measure again.

## 8. Loudness targets (F, from standards; confirm the delivery spec of the actual platform)
| Destination | Integrated | True peak |
|---|---|---|
| US broadcast (ATSC A/85) | -24 LKFS +/- 2 | -2 dBTP |
| EU broadcast (EBU R128) | -23 LUFS +/- 0.5 | -1 dBTP |
| Netflix, dialogue-gated | -27 LKFS +/- 2 | -2 dBTP |
| YouTube and streaming music platforms | about -14 LUFS (consensus, not a YouTube spec) | about -1 dBTP |
| Cinema | calibrated room mix, dialogue anchored near 85 dB SPL reference (E); no LUFS target, follow the festival or DCP lab | n/a |
LUFS and LKFS are the same unit. Netflix lists a different target for programmes with under 15 percent dialogue (3P, check). Dialogue-gated measure means only speech is measured. Re-measure after final encode because lossy codecs raise true peak. Features for the web: master at -24 to -23 integrated for a natural dynamic range; a -14 version only for short clips and trailers (E).

## 9. Dubbing workflow (per language; tools 3P)
1. Prepare M and E stems and a clean transcript with timecodes (the dialogue list).
2. Translate and adapt (not literal): lip length, culture, register, honorifics (languages-and-localization.md). A human adapter or native reviewer signs off.
3. Voices: cast one consistent voice per character per language; use consented actors or licensed synthetic voices; do not clone the original actor's voice into another language without that actor's consent.
4. Generate or record each line to the original timing (time-stretch within about 10 percent; rewrite lines that need more).
5. Lipsync the picture where faces are visible (section 3), or choose cutaways.
6. Mix with the M and E stem at the same levels; loudness per language.
7. QC with a native speaker: meaning, tone, taboo words, sync, names.
8. Deliver as separate audio tracks (MP4 audio streams tagged by language, or MKV) and as stems for OTT.
Tool language support changes: ElevenLabs reports 90 plus languages in dubbing but audio-only, no lipsync; HeyGen claims 175 plus with lipsync (vendor-stated, older sources say 40 plus); Tamil and Telugu support is not confirmed in the sources read, so test each language and check Indian-language specialists such as Dubverse (3P). Mark any language not tested as "unverified" in the delivery note.

ElevenLabs tools, casting by role and voice rules: see elevenlabs.md in this folder.

## 10. Audio QC list
No clipping; dialogue intelligible at -30 dB below the music; no hallucinated music or lyrics from the generator; no leftover temp music; consistent room tone; matched ambience across cuts; sync verified; loudness measured; peak and true peak logged; silence gaps on cuts under 300 ms removed unless scripted.

Music briefs, AI music prompting, scoring, SFX and mixing craft: see the `music-and-sound` skill (`${CLAUDE_PLUGIN_ROOT}/skills/music-and-sound/SKILL.md`).
