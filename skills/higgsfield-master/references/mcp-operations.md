# MCP operations playbook (2026-10-13)
Executable sequences for the connected Higgsfield MCP. Tools appear as `mcp__<id>__<tool>`; this file uses bare tool names only. Tool names and parameters drift: if a call is rejected, run `get_workflow_instructions` or re-read the tool schema, do not guess. MCP always deducts credits (no Unlimited).

## 0. Gates (apply to every workflow)
1. `balance` first. Report credits left. `show_plans_and_credits` and `transactions` are read-only history.
2. QUOTE: `ads_studio_quote` where available (Ads Studio), otherwise estimate from credits-and-budget.md (stills + proofs + finals + 10 percent repurpose + 20 percent contingency). Tell the user: tool, model, count, resolution, total credits, balance after.
3. STOP. Wait for the user's explicit yes in chat. A yes covers only the quoted job; a new quote needs a new yes.
4. Draft cheap first: 720p, 4-5s, Fast/Turbo/Lite/Mini model, hardest shot first. Finals once, after QA (production-pipeline.md).
5. Never call without an explicit yes: any publish_*, deploy_*, `create_website`, `tiktok_prepare_publish`, `tiktok_connect`, `participate_in_contest`. Never call `cancel_trial_auto_renewal` or change billing or plans. Never pass an unlimited flag.
6. Real-person likeness (Soul ID, voice clone, reference ad faces) only with documented written consent (compliance.md). No celebrities, no minors.
7. TikTok is banned in India: never plan or call tiktok_* for Indian clients. Meta campaigns stay paused and are built by hand.
8. Never upload unreleased formulations, confidential packaging art, customer data or personal data. Keep client brands apart.
9. Log every job in the asset log (production-pipeline.md section 9).

## 1. Setup (read-only, free)
`list_workspaces` then `select_workspace` (confirm with the user if more than one). `get_preferences` to read defaults; `update_preferences` only if the user asks. `create_project` (name = client-project slug) and `create_folder` per deliverable type; `list_projects`, `list_folders`, `list_project_assets` to avoid duplicates.
Discovery before choosing: `models_explore` (live models, limits, cost hints), `get_presets` then `get_preset_instructions` for a preset, `apps_search` then `apps_describe` before `apps_invoke`.
Inputs: `media_upload` (or `media_import_url` for a public approved URL), then `media_confirm` to get the usable media id. `show_reference_elements` / `manage_reference_elements` for Elements; `show_characters` for Soul IDs.

## 2. Product ad (one hero video from a product photo)
1. Setup (section 1). Upload packshot front, 3/4, back via `media_upload`, `media_confirm`.
2. Stills proof: `generate_image` (Soul 2.0 or Nano Banana; params: model, prompt, aspect_ratio, reference media ids, count 1). Cost check first. User approves the hero frame.
3. Motion proof: `generate_video` (Seedance 2.0 Fast or Kling Turbo; start_image = hero frame, prompt in model dialect, duration 4-5, resolution 720p, audio per brief). Wait with `jobs_wait` on the job id; view with `job_display` or `show_result`.
4. QA (qa-tester). Fix with an edit or `generate_image` i2i, one variable per pass.
5. Final: same prompt and refs on the premium model at target resolution, once. `upscale_video` last, only the chosen take.
6. Formats: `reframe` (9:16, 4:5, 1:1, 16:9), `outpaint_image` for stills. Overlay text and price in editing, never in the generation.

## 3. Ads Studio batch (static ads from a site URL)
1. `ads_studio_create_brand` (name, URL, palette, tone). Reuse via `ads_studio_list_brands` or `ads_studio_get_brand`.
2. `ads_studio_add_product` (URL or photos, claims list approved by the regulatory reviewer); fix with `ads_studio_update_product`. Check `ads_studio_list_products`.
3. `ads_studio_quote` (product, ad count up to 20 per product per run, formats). About 4 credits per ad. STOP for yes.
4. `ads_studio_generate` with the quoted parameters only. Poll `ads_studio_get_run`; `ads_studio_list_runs` for history; `show_marketing_studio_v2` to display.
5. `ads_studio_cancel_run` only if the user asks or QA shows the run is wrong. Reject any invented claim, rating or testimonial.

## 4. AI influencer series (recurring original persona)
1. Consent check: original character only, or a documented consenting real person. State the AI label plan.
2. `ai_influencer_get_options` and `ai_influencer_get_settings` (free). `ai_influencer_list_presets` for looks.
3. `ai_influencer_prepare` (persona spec, reference stills, preset) to preview. Quote about 1.12 credits per character plus any Soul ID training; STOP for yes.
4. `ai_influencer_generate` for the character, then Soul stills via `generate_image_batch` (batch of 2-4 charges each output) using the Soul ID.
5. Animate chosen stills with `generate_video` (image-to-video, Kling 3.0 or Seedance). Locks: characters-and-consistency.md.
6. Series ledger: persona bible reused verbatim; one variable per episode.

## 5. Short-form video (9:16 shorts)
1. Script and hook (0.1s law) by growth-marketer; shot list by creative-director.
2. `shorts_studio_list_presets` (or `shorts_studio_create_preset` for a house style), then `shorts_studio_create` (script, preset, voice, 9:16). Quote and STOP before create.
3. `shorts_studio_status` to poll; `show_generations` to review. Manual route: `generate_video_batch` for shots, `generate_audio` for VO or music, assemble outside.
4. `virality_predictor` on the finished cut. `video_analysis_jobs` then `video_analysis_status` to study a reference the user supplied.
5. Publishing is outside this skill: hand over files. TikTok never for India.

## 6. Cinematic scene (multi-shot, up to 30s)
1. Locations first: `generate_image` per location (3/4 angle, no people). Character sheet on grey with ONE face. Store as Elements via `manage_reference_elements`.
2. Proof the hardest shot: `generate_video` (Cinema/Seedance/Veo 3.1; start and end frame; one camera move; 720p).
3. On approval, `generate_video_batch` for the rest with the same style header. Chain last frame to next first frame.
4. Optional: `motion_control` (real performance onto a character; consent from the performer), `animation_actions`, `scene_builder_3d_create_project` then `scene_builder_3d_import_asset`, `scene_builder_3d_generate_angles`, `scene_builder_3d_generate_video` for layout-locked shots, `generate_3d` for a prop.
5. Finals once, `upscale_video`, then QA.

## 7. Talking avatar or dub
1. Voice: `list_voices` first. `create_voice` only from a consenting speaker's confirmed audio (written consent on file).
2. Avatar clip: `generate_video` with native audio, or `generate_audio` (VO) then lipsync via `apps_invoke` (Lipsync Studio, found with `apps_search`).
3. Dub: `dubbing` (source video, target language; check Hindi, Tamil, English support in `models_explore`), then native-speaker review. `voice_change` only with consent.
4. Label realistic AI presenters ("Video created using AI").

## 8. Upscale and finish
`upscale_image`, `upscale_video` (selected take only, 1080p or 4K), `remove_background` for cut-outs, `outpaint_image` or `reframe` for formats, `generate_image` i2i (Seedream) for the de-slop pass. Re-check skin after each pass. Deliver text-free masters plus overlay copy.

## 9. Read-only calls (no yes needed)
balance, show_plans_and_credits, transactions, models_explore, get_presets, get_preset_instructions, apps_search, apps_describe, list_*, show_*, job_display, jobs_wait (job already paid), ads_studio_quote, get_workflow_instructions, get_workflow_bundle_file. Everything else can spend credits: quote and ask first.

## 10. Failure handling
Failed jobs auto-refund (not Grok). 4 of 4 bad takes: rewrite the prompt. One defect: edit or reroll once. Job stuck: `jobs_wait` again, then report. If the MCP is down, fall back to the Playwright skills (seedance-auto-generate, higgsfield-image-auto) only with the user's yes.
