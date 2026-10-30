---
name: film-studio
description: "Full-length AI film production OS: features, shorts, series, animated (3D, anime, 2D, stop-motion look), photoreal drama, sci-fi and fantasy epics, documentary-style films, music films, period pieces, any era and any language. Covers development (logline to screenplay), pre-production (bibles, shot IDs, storyboard, animatic), chunked shot production with locked references and last-frame chaining, edit, colour, sound, music, dubbing, subtitles, delivery and legal (copyright, consent, disclosure, CBFC). Phases with owner agents, artifacts, gates, credit and time model. Load after creative-studio for any film, movie, series or short film."
license: MIT
user-invocable: true
metadata:
  version: "1.0.0"
  researched: "2026-10-14"
---
Part of the cinematic pipeline: entry point creative-studio
It routes film work here. This skill adds the long-form layer; it does not repeat single-clip craft.

# film-studio

A film is thousands of clips that must feel like one. The job is not generation, it is control: story locked first, references locked second, shots third, edit last. Craft for single shots stays in `cinematography` (camera, light), `higgsfield-master` (prompts, models, credits), `photoreal-humans`, `asian-human-reference`, `seedance-20`, style packs `01-cinematic`, `02-3d-cgi`, `03-cartoon`, `08-anime-action`, `10-music-video`. Read those, do not copy them.

## 1. Intake (ask only what blocks; default the rest, state defaults in one line)
1. Format: feature (80 to 120 min), medium (40 to 79), short (under 40), series (episodes x minutes). Default: 90 min feature.
2. Genre and look: one style family for the whole film (genres-and-styles.md). Switching style mid-film means regenerating.
3. Language(s) of dialogue, subtitle and dub targets (languages-and-localization.md). Default: original in one language plus English subtitles.
4. Era and place (period research, genres-and-styles.md section 6).
5. Story source: client script, treatment, idea, or none (then run Development).
6. Budget cap in credits and money, deadline, distribution target (YouTube, OTT, festival, theatrical, CBFC needed or not).
7. IP check: original characters and worlds only. A film may be inspired by a genre; never copy protected characters, worlds, names, designs or plots (delivery-and-legal.md section 3).

## 2. Pipeline (5 phases, each ends with a gate; do not advance on a failed gate)
Roles (Cinema Studio crew): creative-director = director and sign-off; screenwriter; production-designer; cinematographer; performance-director = acting, eyelines, motion transfer and performer consent; prompt-engineer; vfx-artist = cleanup and comps after generation; voice-director; composer-sound-designer; editor; colorist = grade after picture lock; continuity-supervisor = continuity and QA; producer = tracking, credit budget, schedule and legal checklists (replaces producer for film); title-designer = titles, credits, poster, thumbnails; tech-writer = docs; fullstack-engineer = tooling; growth-marketer = trailer and marketing.

### Phase 1 Development
- Owners: screenwriter (story, script), creative-director (approval), producer (scope, budget), tech-writer (documents).
- Artifacts: logline, one-page synopsis, treatment, beat sheet, sequence plan, screenplay v1, budget model, IP and legal checklist.
- Method: story-and-script.md (logline to treatment to beat sheet to sequences to screenplay); for a scene the owner describes casually, use story-and-screenplay (Casual scene to prompt). Pipeline owner: film-studio (indic-languages for Indian-language scripts).
- Gate G1: screenplay locked (page count matches runtime, about 1 page per minute), runtime and shot budget agreed, IP check clean, cap approved by the user.

### Phase 2 Pre-production
- Owners: production-designer (bibles, references), cinematographer (shot list, boards), performance-director (performance bible and per-shot briefs, performer consent), creative-director (look), producer (schedule), continuity-supervisor (bible audit, ledger).
- Artifacts: character, world, style, wardrobe, prop and location bibles with reference sheets; shot list with IDs; storyboard; animatic with temp voice and temp music; voice cast list; production folder; schedule by sequence.
- Pipeline owners: cinematography (shot design), photoreal-humans + asian-human-reference (people), performance-direction (acting, motion transfer), cast-real-people (real consented faces: signed release and identity lock before any generation; owner casting-director).
- Method: bibles-and-continuity.md, previs-storyboard.md; period research per genres-and-styles.md.
- Gate G2: every recurring character, location and prop has an approved reference set; animatic runtime within 5 percent of target; consents on file; the user's yes on the credit quote.

### Phase 3 Production (chunked, by sequence)
- Owners: prompt-engineer (prompts, generation), vfx-artist (cleanup, comps, plate fixes before the edit), voice-director and composer-sound-designer (audio), fullstack-engineer (batch tooling), continuity-supervisor (per-sequence QA), producer (burn-down).
- Artifacts: approved takes per shot ID, take ledger, continuity ledger, per-sequence lock files, sequence rough cuts.
- Pipeline owners: vfx-compositing (fixes before the edit), higgsfield-master prompts, higgsfield-timed-prompts for any multi-shot Seedance generation, edit-gen (Elements consistency) or direct generation; run the 512 check (cinematography/references/prompt-compression.md) before any generation.
- Method: shot-production-at-scale.md. Proof at low cost first, finals once, one sequence at a time. 90 minutes is about 40 to 60 scenes, roughly 600 to 1200 shots (estimate, 4.5 to 9 s average cut length), made in 8 to 12 sequences of 8 to 12 minutes.
- Gate G3 (per sequence): all shots approved, continuity ledger clean, sequence lock committed, QA scorecard 85 or higher. Failed gate: repair by edit or reference, not blind reroll.

### Phase 4 Post-production
- Owners: editor (conform, ffmpeg, assembly, picture lock), colorist (grade after lock, before QA), composer-sound-designer (mix), voice-director (dubs), creative-director (picture lock), continuity-supervisor (QA), growth-marketer (trailer cut), tech-writer (credits), title-designer (titles and credits, after the colorist, parallel to the final conform).
- Artifacts: assembly cut, picture lock, colour-matched master, dialogue, Foley, ambience, score, mix, subtitle files, dubbed stems.
- Pipeline owners: edit-director (short-form, beat-cut) + edit-voice (captions); color-grading (colour pipeline, matching, LUTs, grain, colour QC); ffmpeg recipes here for long form; music-and-sound; voice-studio + indic-languages (Indian-language dubs, captions, lipsync QA).
- Method: editing-and-assembly.md, sound-music-voice.md.
- Gate G4: picture lock, loudness within target, subtitles pass CPS and line checks, A/V sync verified at start, middle and end, music licences logged.

### Phase 5 Delivery
- Owners: editor (exports, packages), tech-writer (delivery note, credits, AI disclosure), title-designer (titles, credits, poster, thumbnails), growth-marketer (trailer cut, press kit), producer (rights file, CBFC and platform checklists), continuity-supervisor (final QC), creative-director (sign-off).
- Artifacts: master (ProRes or high-bitrate H.264), platform deliverables, DCP if needed, subtitle and audio sidecars, trailer, poster, disclosure text, rights file, CBFC dossier if India theatrical.
- Pipeline owners: QA via the creative-studio master scorecard (85 drafts / 90 finals); delivery here.
- Method: delivery-and-legal.md; deeper skills: film-legal-distribution (rights, CBFC, platform specs, festivals; not legal advice), title-and-key-art, production-tracking.
- Gate G5: QC pass on the real exports, rights file complete, disclosure decided per platform, the user's explicit yes before any publish, submission or send.

## 3. Chunked production model (the core idea)
- Scene = one location and continuous time. Sequence = 3 to 6 scenes forming one dramatic movement (8 to 15 min in a feature).
- Never start a sequence until its locks exist: character sheets, location plates, prop sheets, style header, lens and grade settings, voice profiles.
- Shot IDs are permanent (S03-SC07-SH012). Every file, prompt, take and edit decision carries the ID.
- Chain, do not extend: last frame of shot N is first frame of shot N+1 inside a scene; clips under 30 s (identity and light drift past that, 3P).
- After each sequence: freeze its lock file (prompt headers, seeds, settings, reference hashes) so a re-render months later matches.

## 4. Credit and time model (ESTIMATE, recompute on the live Generate button before any quote)
Basis: Higgsfield vendor figures for Cinema Studio, about 75 credits for an 8 s 720p shot and about 150 for a 15 s 1080p shot (vendor-stated 2026-10-13), 20 credits per USD, keep rate 15 to 33 percent from the published Hell Grind account (3P) and vendor example near 1:1 for simple shots.
| Per runtime minute | Optimistic | Planning | Pessimistic (action, VFX, non-human leads) |
|---|---|---|---|
| Takes generated per kept shot | 1.5 | 4 | 10 |
| Generated seconds per runtime minute | 90 | 240 | 600 |
| Credits per runtime minute (720p proof pricing) | about 850 | about 2,300 | about 5,700 |
| Plus finals re-render at 1080p (kept shots only) | +600 | +600 | +600 |
| Money per runtime minute at 20 credits per USD | about 70 | about 145 | about 315 |
| Human hours per runtime minute (review, prompts, edit, QA) | 3 | 6 | 12 |
A 90-minute film at planning rate is about 260,000 credits (about 13,000 USD) and 540 human-hours spread across agents. Add 8 to 12 percent for audio, music and dubbing tools, and a 15 percent contingency. Assumption: costs fall as references lock; treat the first sequence as the calibration run and re-quote the rest from its actual burn.
Cheaper routes: shorts and episodes first; animatic-first approval; 720p proofs; reuse establishing shots; held shots and cutaways; fewer speaking close-ups per scene.

## 5. Gates and rules that never bend
- Spend: balance check, quote per sequence and total, then the user's explicit yes (creative-studio section 7). A changed quote needs a new yes.
- Publish, submit to a festival, send or upload anywhere: only on the user's explicit yes.
- Real-person likeness or voice: documented consent only; no celebrities; no living persons depicted as real.
- Confidentiality: unreleased scripts and client assets go to a generation platform only if the client approves and the platform terms allow it (training and licence clauses, higgsfield-master compliance.md).
- Client neutrality: one client's brand, characters or data never appear in another film.
- Legal and censorship sign-off is not ours: return to the Manager for qualified counsel review.
- Research and drafting are AI work, not certification: festival rules, platform specs and CBFC rules change, so re-check the live source before delivery.

## 6. QA (qa-tester)
Per shot: creative-studio scorecard blocks (skin, eyes, hands, light, motion, culture). Per sequence add: continuity ledger diff (wardrobe, props, injuries, time of day, weather, screen direction), 180-degree and eyeline check, voice match, no hallucinated music or text. Per film: runtime, loudness, subtitle audit, black frames, A/V drift, credits spelling, disclosure present. Critical fails: unconsented likeness, copied protected IP, wrong-era anachronism in a hero shot, culturally wrong attire or speech, loudness out of range.

## 7. Folder structure
`C:/Claude Code/company/creative/<client>/<film>/` with `00_dev`, `01_bibles`, `02_previs`, `03_shots/S##/SC##/`, `04_audio`, `05_edit`, `06_delivery`, `ledgers/`, `log.md`. Detail and naming: shot-production-at-scale.md section 6. Log every generation and decision in log.md (creative-studio section 8).

## 8. Router: which reference to open
| Need | Open |
|---|---|
| Idea to screenplay, structure, dialogue | references/story-and-script.md |
| Bibles, shot IDs, continuity ledger | references/bibles-and-continuity.md |
| Shot list, boards, animatic | references/previs-storyboard.md |
| Batching, chaining, locks, retakes, folders | references/shot-production-at-scale.md |
| Cuts, pacing, ffmpeg, colour, LUTs | references/editing-and-assembly.md |
| Voice, dubbing, lipsync, Foley, score, loudness | references/sound-music-voice.md |
| ElevenLabs tools, voice casting, consent and disclosure rules | references/elevenlabs.md |
| Animation or live-action style, prompt vocabulary, models, period | references/genres-and-styles.md |
| Tamil, Hindi, Telugu, Malayalam, Kannada, Bengali, others, subtitles | references/languages-and-localization.md |
| Export specs, platforms, DCP, legal, CBFC | references/delivery-and-legal.md |
| Source list and confidence | references/sources.md |
| Titles, credits, poster, trailer; legal, CBFC, platform delivery; shot tracker and budget | skills title-and-key-art, film-legal-distribution, production-tracking |
Load at most this file plus two references per step. Model choice and prompts: higgsfield-master references/model-dialects.md and cinema-studio.md.

## 9. Model roles (3P, 2026-10-13, confirm on the Generate button)
Seedance 2.5 or 2.0: long multi-reference narrative shots, main backbone. Kling 3.0: multi-shot clips, cheap iteration, native lipsync in several languages. Veo 3.1: hero shots and native audio. Cinema Studio: camera and lens control, storyboard-fed shots. Popcorn: board frames. Soul ID or Soul Cast: persistent faces. Seedream, Flux Kontext, Nano Banana: reference sheets and repairs. Genjutsu and video-to-video: fix a nearly right shot. Mixed-model films need one shared style header and a grade pass to unify.

## 10. Report format to the Manager (10 lines max)
Phase and gate status, sequences locked of total, credits spent versus quote, runtime assembled, open risks (legal, consent, licence), next gate and what the user must approve.
