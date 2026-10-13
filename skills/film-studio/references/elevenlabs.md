# ElevenLabs reference (voice, audio, subtitles)

Status: ElevenLabs MCP connected (2026-10-13). Tool names below are exact.
Scope: this file covers voice and audio only. Visuals stay on Higgsfield (higgsfield-master).

## What we use it for
- Voiceover and narration: ads, explainers, documentary-style narration.
- Character dialogue: one locked voice per film or series character.
- Dubbing: audio-only dubbing of finished cuts into other languages. No lipsync; lipsync is a separate job.
- Voice design: build a new synthetic voice from a text description.
- Sound effects and music: SFX and score beds, checked against the audio QC list in sound-music-voice.md.
- Speech-to-text: transcripts and timing for subtitles.
- Voice agents: conversational voice bots for client products. Later phase only; not part of current film or ad work.

## Tools (exact names)
- creative_list_voices: filter by language, gender, age, use_cases, descriptives, voice_category.
- creative_generate_speech: text to speech. Spends credits.
- creative_design_voice, creative_get_voice_design_previews, creative_save_designed_voice: design, pick a preview, save.
- creative_transcribe_audio: speech to text for subtitles.
- creative_generate_image, creative_generate_video: visual generation. Use only when the user asks for ElevenLabs visuals; Higgsfield is primary.
- Flow tools: creative_create_flow, creative_add_flow_node, creative_connect_flow_nodes, creative_run_flow_nodes, creative_get_flow_run_status. Running a flow spends credits.
- Brand kit tools: creative_create_brand_kit, creative_list_brand_kits, creative_get_brand_kit, creative_update_brand_kit, creative_add_brand_kit_item, creative_delete_brand_kit_item.
- agents_* family (voice bots): for example agents_create, agents_get, agents_list, agents_update, agents_create_test, agents_create_deployment.
- Higgsfield voice tools (comparison only): generate_audio, dubbing, list_voices, create_voice, voice_change.

## Casting by role (no voice IDs; pick from creative_list_voices)
Verified fact (owner-checked, dated 2026-10-13): the library has 20+ professional Tamil voices, covering ad narrators, storytellers, documentary narrators, Tanglish, and emotional character voices (angry, sad, anxious), plus Chennai and Coimbatore accents.
- Energetic ad narrator: short product spots, hooks, offers.
- Calm documentary narrator: explainers, process and ingredient stories.
- Dramatic angry character: conflict scenes. Keep emotion in the script, not only in the voice.
- Warm storyteller: origin stories, brand films, bedtime-style narration.

## Rules
1. Credits: every generation, voice design, dub and flow run uses credits. Quote the cost, then wait for the user's yes before running it.
2. Real people: never clone a real person's voice without written consent on file. No celebrity voices.
3. No fake testimonials: never give a synthetic voice to a customer, reviewer, doctor or expert quote.
4. Disclosure: label AI-generated voices where the platform, broadcast, OTT or local rules require it. Note the label in the delivery note.
5. Language fit: pick a native-accent voice for each language. Test Telugu and Malayalam samples before committing; neither is confirmed in our sources yet, so mark them "unverified" until tested.
6. Head-to-head: run the same script through ElevenLabs and the Higgsfield voice tools. Score naturalness, pronunciation of brand and product names, emotion, accent and cost. Keep whichever wins for each language.
7. Pronunciation: check brand, product and ingredient names in every language before final.
8. Audio QC: apply the checklist in sound-music-voice.md (levels, clipping, sync, loudness, stems).
9. Voice bots (agents_*): build only for an approved client product brief. No live calls, outbound messages or deployments without the user's yes.
10. Data: do not upload customer data, unreleased formulations or confidential scripts to a voice service unless the user approves it for that job.

## Routing
- Making voice sound human (Tamil and Indian languages, v3 and v4 settings, speech-to-speech, artists, post, consent): `voice-studio` (`${CLAUDE_PLUGIN_ROOT}/skills/voice-studio/SKILL.md`). This file keeps only tool names and rules.
- Voice choice and comparison: this file, then the language notes in languages-and-localization.md.
- Mixing and delivery: sound-music-voice.md and delivery-and-legal.md.
- Visuals for the same scene: higgsfield-master.
