# Mixing and mastering

Labels: F sourced or standard, E starting point to be adjusted by ear. Loudness table by platform lives in `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/sound-music-voice.md` section 8; the full ffmpeg two-pass loudnorm is in `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/editing-and-assembly.md` section 4. This file adds only what those do not hold.

## 1. Gain staging
- Work at 48 kHz and 24-bit (or 32-bit float). Never print loud into a clip; peaks on tracks around -12 to -6 dBFS leaves headroom (E).
- Set every source to a sensible level before using effects; keep the master bus peaks under -6 dBFS until mastering.
- Order: clean (edit, de-noise) > level > EQ (subtractive) > compress > tone EQ > space (reverb, delay) > bus > master.
- Trust meters but verify with ears at a steady monitor level.

## 2. EQ ranges by instrument (E, starting points; iZotope and Sonicbids charts, see sources)
| Element | Cut or fix | Boost or character |
|---|---|---|
| All tracks | high-pass to remove rumble below 30 to 80 Hz as fits | none |
| Kick | 200-500 Hz boxiness | 60-80 Hz punch; 100-200 knock; 1-5 kHz click |
| Bass | 300-500 Hz mud | 40-120 Hz low end; 120-250 body; 800 Hz-1 kHz presence |
| Snare | 300-500 Hz box | 150-250 body; 2-3.5 kHz crack; 8 kHz+ air |
| Hi-hats and cymbals | below 200-300 Hz | 8-12 kHz sheen |
| Acoustic guitar | 100-200 Hz boom; 200-300 Hz mud | 2-5 kHz attack; 10 kHz air |
| Piano | 200-500 Hz mud; 2-4 kHz harsh | 5 kHz definition |
| Strings | 200-300 Hz mud | 2-4 kHz bow; 8-10 kHz air |
| Flute, bansuri | below 200 Hz | 3-5 kHz breath; 8-10 kHz air |
| Tabla, mridangam | 250-400 Hz ring (check) | 80-150 Hz depth; 3-6 kHz slap |
| Voice (speech) | 80 Hz high-pass; 200-400 Hz boxy; 3-5 kHz harsh if hard | 100-250 body; 1-4 kHz intelligibility; 5-8 kHz presence; 10 kHz air; de-ess 5-9 kHz |
| Vocals (sung) | 200-400 mud | 3-5 kHz presence; 10 kHz+ air |
| Synth pad | clear 200-400 Hz | 5-10 kHz glow |
iZotope warns vocals cannot be set by chart; mix to the voice, genre and context. Frequency conflicts: use small cuts (1 to 3 dB) in the competing track at the voice's main band (500 Hz to 4 kHz), E.
Band words: sub 20-60, bass 60-250, low mids 250-500 (mud), mids 500-2 k (honk, vocal clarity), upper mids 2-6 k (ear peak, harsh), presence 4-6 k, brilliance and air 6-20 k.

## 3. Compression
- Ratio 2:1 to 4:1 for gentle control; 4:1 to 10:1 for drums and vocals; limiting above 10:1.
- Threshold so gain reduction is 2 to 6 dB on peaks (voice), 3 to 8 dB (drums). Attack: slower (20 to 40 ms) keeps punch; faster smooths. Release: 50 to 200 ms or tempo-timed.
- Parallel compression for drums; compress after EQ cleanup. Over-compression kills dynamics; keep film and ad dynamics natural.
- Multiband for the master only if needed; use a soft limiter (not a brickwall) for final ceiling.

## 4. Reverb and delay
- Reverb: short room 0.2-0.6 s (intimacy), plate 1-2 s (vocals), hall 2-4 s (cinematic). Pre-delay 10-40 ms keeps the voice clear. High-pass the reverb return (about 200 Hz) and low-pass (about 8 kHz) to avoid mud and hiss.
- Delay: tempo sync (1/4, dotted 1/8 for movement); feedback 20-40 percent; filter the repeats. Slapback 80-120 ms for 1950s feel.
- Dialogue stays nearly dry; place it in the room with a short early reflection and match the picture.
- Use one reverb per space to glue; do not wash every track.

## 5. Panning and width
- Centre: kick, bass, lead vocal, dialogue. Hard sides: guitars, pads (doubles), percussion. 60 to 80 percent for supports.
- Mono compatibility: check mono sum (phone speakers are often mono). Keep sub bass below 100-150 Hz centred.
- Width tools (stereo wideners) sparingly; widen pads, not bass.
- Haas delay (under 30 ms) widens but can phase; check in mono.

## 6. Dialogue and music ducking
- Sidechain compress the music bus from the dialogue bus: 3 to 6 dB reduction, attack 10 to 30 ms, release 200 to 600 ms (E; sound-music-voice.md says 3 to 6 dB).
- Better than ducking all frequencies: use dynamic EQ on music, triggered by the voice, cut 2 to 4 dB in 500 Hz to 4 kHz (iZotope technique, extrapolated to dialogue, E).
- Music should rise in pauses and between phrases ("breathing"); write the automation in the DAW or use ffmpeg `sidechaincompress`.
- Check speech intelligibility with a low-quality speaker; the voice must be clear without the music.
- Music below dialogue by about 12 to 20 dB during speech at the low end of reading, E.

ffmpeg ducking (E; test and listen):
```
ffmpeg -i music.wav -i voice.wav -filter_complex "[0:a][1:a]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400[duck];[duck][1:a]amix=inputs=2:normalize=0[a]" -map "[a]" mix.wav
```

## 7. Stems and buses
Stems: DLG, MUS, FX, AMB, FOLEY; music stems: drums, bass, harmony, lead, pad, FX. M and E (music and effects) for dubbing. Print at the same start time, same length, 48 kHz 24-bit WAV, no master processing on stems unless asked, with a printed mix and a no-limiter mix. ElevenLabs Music can split stems (reported 225 credits for vocals plus instrumental, 450 for a full split on 30 s, 3P); confirm the price shown and download test.

## 8. Loudness (F)
- Units: LUFS (also LKFS) integrated over the whole programme; true peak in dBTP; loudness range LRA in LU.
- EBU R128 (EU broadcast): -23 LUFS integrated, +/- 0.5 LU, true peak -1 dBTP max (F). ATSC A/85 (US): -24 LKFS +/- 2, -2 dBTP (F, from sound-music-voice.md).
- AES TD1004 (streaming, 2015): recommends stream targets between -16 and -20 LUFS to avoid excessive limiting and still be audible on mobiles (F). Many platforms play near -14 LUFS (consensus).
- Streaming music: about -14 LUFS, -1 dBTP. YouTube: about -14 LUFS (not an official spec). Podcast: about -16 LUFS stereo, -19 mono (E, common convention). Broadcast TV Europe: -23. Netflix: -27 dialogue-gated (3P).
- Lossy codecs raise true peak; leave -2 to -3 dBTP headroom before MP3 or AAC (E).
- Do not master a film to -14 unless it is a short clip; keep dynamic range for the web feature (sound-music-voice.md).

## 9. ffmpeg loudnorm (summary; full recipe in editing-and-assembly.md)
Measure: `ffmpeg -hide_banner -i in.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -` Then apply the measured values in a second pass with `linear=true` and `-ar 48000`. Re-measure the final file. To only measure LUFS without changing, use `-af ebur128=peak=true`.
Targets used: streaming -14 TP -1; broadcast EU -23 TP -1; US -24 TP -2; podcast -16 TP -1.

## 10. Mastering a music track
Reference against a similar track described by genre (not copied); EQ for balance; gentle bus compression 1-2 dB; limiter for ceiling; stay at target LUFS; check true peak; dither if reducing bit depth; export WAV master and a delivery encode; compare to the mix by ear at matched loudness (loudness-matched A/B).

## 11. Final check on four systems
Phone speaker (mono), laptop, headphones, a reference or car. Listen for harshness at 3 to 5 kHz, mud at 200 to 400 Hz, vocal lost, bass vanishing, clipped transients, codec artefacts after encoding.
