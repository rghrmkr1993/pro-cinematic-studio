# Help center facts, official [official, 2026-10-13]
Source: higgsfield.ai/creator-hub/help-center (71 articles; about 30 read in full, listed in sources.md). These override earlier third-party claims. Not legal advice; Terms of Use are binding.

## Credits (V)
- Types: Subscription (resets each cycle, no rollover; annual plans reset every 30 days), Credit Pack (90 days), Auto-Refill (90 days), Boost (90 days), Promo (date shown). Spend order: subscription first, then soonest expiry. Cancel: purchased credits stay usable on the free plan until expiry.
- Credits are charged for images, video, re-rolls, upscale on web, MCP, CLI, Canvas, Supercomputer. Batch size 2 to 4 charges each output. Exact total shown on the Generate button. Edit button also shows its cost.
- Value: Auto-Refill rate is $1 = 18 credits; vendor blog uses a reference rate of 20 credits per $1 for plan math. Per-model credit costs are NOT published in help articles.
- Failed generations refund automatically in minutes (check Manage Account, Usage). Exception: Grok is charged at start (V). IP and NSFW blocks refund in most cases. Queued jobs can be cancelled for instant refund; Processing and Generating cannot.
- Auto-Refill: off by default, $20/40/90/150/300, triggers below the plan threshold, not on entry plans, failed charge adds nothing.
- Concurrency Boost: one-time pack adds +4/+8/+12/+16 parallel generations (max +16) with separate Boost Credits (90 days), per-pack toggle.

## Plans (V)
- Individual: entry plan (core models, monthly credits); mid and top plans give all models (new ones may roll out gradually) plus Unlimited on selected models. Monthly or annual. One active subscription per account. Prices not in help text; blog (2026-09-21) shows Starter $15, Plus $49, Ultra $129 per month.
- Upgrade: immediate, prorated, billing date resets, unused credit value counts toward price. Downgrade: next cycle, from the detailed comparison section. Promo and pack credits unaffected.
- Team 2 to 9 seats, 16 image + 16 video parallel, standard queue, pooled credits. Scale 5 to 15 seats, 32 + 32 parallel, priority queue, SSO, pause member spend. Enterprise: custom, SOC 2, legal indemnification, no training on customer data, per-user caps, dedicated manager. Free: small model set, no credits, visible watermark, no paid trial.
- Exclusive Offers: personalised, one-time, may add credits, temporary Unlimited, priority or an upgrade (an upgrade renews at the higher standard price next cycle).

## Unlimited (V)
Mid and top plans; most models 365 days, newest flagships about 7 days, some a pool of free generations. Toggle in the generation panel; off means Credit Mode, priority queue. Standard queue otherwise, speed varies at peak. WEB ONLY: MCP, CLI, Canvas, Supercomputer, other automation always deduct credits. Starts at activation, no restart at renewal, stops if the subscription ends. Marketplace bundles: video 1 at a time up to 15 s, image 2 at a time. Personal human use only: no scripting, credential sharing or resale; abuse can pause access. Coverage table at Manage Account, Subscription.
Blog (2026-09-21): 365-day set includes original Nano Banana, Seedream 5.0 Lite, Seedream 4.5, Flux.2 Pro, Kling O1 Image, GPT Image; 7-day 2K windows for Nano Banana 2 (Plus, Ultra) and Pro (Ultra). Windows cap at 2K.

## Watermark, ownership, commercial use (V)
- Free accounts: visible watermark on every output. Paid plans: none, including free and Unlimited generations; embedded at generation, so old files do not change. Invisible AI-provenance metadata may be embedded and is not removed by upgrading.
- Terms s4.4: Higgsfield claims no ownership of inputs or outputs; outputs are not exclusive (others may get similar). Commercial use is not tied to a plan (ads, client work, products, monetised video); rights survive cancellation. Higgsfield licenses content to train its models; deletion stops future use, not past; Enterprise is excluded. You may not use outputs to train or distill other AI models. You carry third-party copyright, trademark and likeness risk; no uploading another person's image without permission (s5.3). Only Enterprise has IP indemnification.

## Refunds and billing (V)
Initial purchase refundable within 7 days only if no credits used (free and Unlimited generations do not count); renewals never. Packs, Auto-Refill and credit-adding offers: 7 days, unused. Access-type offers: no. Fee up to 6%, processing up to 3 business days, refund cancels the plan at once. EU/UK 14-day withdrawal ends once content is used. Upgrade refund within 7 days if new-plan credits unused. Cancel stops charges but returns nothing. Refund if a paid feature is shut down or the account is terminated without fault.

## Models and tools (V, see models-catalog.md and tools-a-z.md for detail)
Seedance 2.5 up to 1080p, 4 to 30 s, 30 img + 10 video + 10 audio refs, Pro/Plus or above. 2.0 up to 4K, 4 to 15 s, 9 + 3 + 3. Kling table (3.0 up to 4K, Turbo 1080p, Motion Control 3 to 30 s). Nano Banana family above. Cinema Studio 4.0: up to 30 s, 50 refs, Seedance 2.5 base, resolution not stated in help. Soul ID: 20 to 80 photos, one person per ID, cost not stated, shared across Soul family. Soul HEX in Soul 2.0 and Cinema; Moodboards Soul 2.0 only (20+ images, no faces). DoP: Higgsfield Standard in picker, 3 or 5 s, preset based. Popcorn: 8 frames, 4 refs. Lipsync: 8 models, 18 languages, covered mouths hurt sync. Canvas: free to build, always credits; Kling connected image is a start frame, not a character ref; Seedance needs roles written in the prompt. Marketing Studio: web only, 15 s cap, edit only in Posters.

## Integrations (V)
MCP https://mcp.higgsfield.ai/mcp, OAuth, no API key, subscription needed, Developer Terms apply (you answer for agent output). CLI route for coding agents: `npx skills add higgsfield-ai/skills` (help text names 3 skills: generate, soul, product-photoshoot), `higgsfield auth login`. API is a separate product: USD prepaid balance (min $5), 50+ models, key from open.higgsfield.ai, 20 concurrent, no plan or Unlimited. Apps built in Supercomputer bill end users on their own credits.

## Safety blocks (V)
IP blocks: named franchise characters, sports leagues, logos, living artists. Rephrase descriptively; Seedance runs its own IP check Higgsfield cannot override; "I own the rights" button may unblock owned inputs. NSFW false positives: swimwear, fitness, medical imagery; add text to an image-only input, swap model. Stuck over 10 h for Kling: contact support.
