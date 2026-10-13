# Higgsfield agents and assistants (researched 2026-10-13)
Labels: (V) vendor-official, (3P) third-party, (U) unverified.

## Supercomputer (V, help center)
Web agent workspace (paid plan). Give a plain-language goal; it plans, routes models per sub-task, generates image, video, audio, assembles in one chat, re-runs only changed steps.
- Chat LLM: auto-routed (cheaper, faster) or chosen (Anthropic, OpenAI, Google, xAI, DeepSeek and others; Claude Sonnet 5.5 added 2026-09-27, GPT-6.1 Sol 09-29, V changelog).
- Sections: New chat, Search, Apps, Games, Skills, Connectors, Memory, Faceless channel.
- Official skills: Product UGC, Faceless Video, Shorts Maker, YouTube Covers, Personal Clipper, TV Commercials, Animated Infographics, Localization, Ad Multiplier. Community skills and My skills (build from chats or Create new). Skills also run through MCP and the ChatGPT plugin.
- Connectors: Telegram, Slack, TikTok, Gmail, Google Drive, Notion. Outward posting or email needs explicit user approval; never auto-publish.
- Credits: each step at standard rates, running cost shown; no web Unlimited inside it. Storage is metered (Manage Storage).
- Drive it well: state outcome, audience, platform, duration, brand kit, must-nots; ask for the plan first and cost per step; approve proof shots before full runs; give references; specify "do not publish". Marketing Studio is not reachable from it yet (V).
- Official help (2026-10-13) says Supercomputer can schedule recurring tasks and connect Slack, Drive, Notion; Faceless channel up to 15 minutes; auto-routed LLM is cheaper and faster than one flagship; reply to refine one step so only changed steps re-run; Memory keeps context between chats; extra storage via Manage Storage. Gaps (U): numeric task caps, scheduling limits, Games details.

## Marketing Studio as agent-like one-click (V)
Template plus product URL builds the ad. Hook and setting picklists exist on UGC, Tutorial, Unboxing, Product Review, UGC Virtual Try On (3P skill, snapshot 2026-05-18; lists drift). See ads-studio.md.

## Cinema Studio Personal Assistant / AI Director (V)
4.0 Personal Assistant adjusts genre, style, camera by conversation and splits a script into shots with parameters pre-filled. 3.5 had a Claude Chat AI Director: it writes prompts and settings but never generates; the human reviews and clicks Generate. Prompt tip: give the script, runtime, genre, era, then review each pre-filled shot.

## Ads Studio chat (V)
After a run, ask in chat to add variations or "Mention a product" to extend; up to 20 ads per product per run.

## Higgsfield MCP (V)
Server https://mcp.higgsfield.ai/mcp, OAuth to the Higgsfield account, no API key. Claude web or desktop: Settings, Connectors, Add custom connector. Requires an active subscription. Covers generation (images, video, characters), Soul ID creation, Marketing Studio presets, upscale, background removal, outpaint, reframe, Kling Motion Control, audio and dubbing (Claude only, not ChatGPT). Always deducts credits (no Unlimited). Verify tool names by asking the agent to list tools (names drift, U). Keep confidential material out of uploads.

## Higgsfield CLI and Skills for coding agents (V)
Claude Code route is the CLI, not MCP (V help center): `npm i -g @higgsfield/cli`, `higgsfield auth login`, `npx skills add higgsfield-ai/skills` (help article names 3 skills: generate, soul, product-photoshoot [official, 2026-10-13]; the 8-skill list with brandkit, youtube-thumbnail, websites was 3P and may reflect a newer repo, verify with the skills list). CLI vs MCP: CLI has minimal token overhead and structured skill output for coding agents (Claude Code, Cursor, Codex); MCP exposes all tools with free parameters for chat agents. Both fall under Developer Terms: you are responsible for what an agent generates [official, 2026-10-13]. Separate API product: USD balance, key from open.higgsfield.ai, no plan credits. Check with `higgsfield --version`, `higgsfield account status` (3P). Review skill contents and install only per company tool-quarantine rules before use. Safe first prompt: inspect the CLI, list models, do not generate.

## ChatGPT extension and Dots (V, 2026-09-29/30)
Slash-command generation in ChatGPT; Dots roles: Character Creator, Cinematic Director, Content Lead, Motion Designer. Not used by this company unless the user asks.

## Katana skill (V) and Production Skills Bundle (V)
Katana recreates reference edits from up to 5 photos. Bundle: 11 workflows in Blender, Adobe, TouchDesigner, DaVinci.

## Community prompt skill (3P)
OSideMedia/higgsfield-ai-prompt-skill v3.40 (2026-09-26): MCSLA (Model, Camera, Subject, Look, Action), DISCIPLINE patterns, generation ledger, seedance lint, acting system. Ideas worth borrowing, content unverified by Higgsfield. Do not install without quarantine.

## Agent operating rules
1. Ask the agent for a plan and credit estimate before generating. 2. Approve one proof shot. 3. Keep references and brand kit explicit. 4. Never let an agent publish, email or spend without a user yes. 5. Record every attempt (prompt, model, seed if any, result) in the job notes to learn hit rates.

## Claude plus Higgsfield production chain [official, 2026-10-13, blog 2026-09-21]
Claude alone writes scripts and analyses exports; with Higgsfield MCP it generates finished ads (30+ video models, images to 4K, voice, Soul characters); TikTok posting and Meta MCP campaign building exist but are outward actions that need the user's yes (house rule: no TikTok for India work; Meta campaigns stay paused). Finished video is uploaded to Ads Manager by hand. Three autonomy levels: assistant, operator, agent, with review gates before publish, activation and budget. Katana (Claude skill) rebuilds a reference edit from up to 5 photos; uploads open a Higgsfield upload window because Claude cannot read chat attachments; corrections regenerate only affected shots.
