# Third-party components

The owner states they hold the licence for this package as a whole. All third-party licence, notice and credit files below are preserved exactly as shipped (not edited). Where a component shipped without a licence file, that is stated; the owner should confirm terms.

## Licence files shipped and preserved

| Path | Component | Licence |
|---|---|---|
| skills/seedance-20/LICENSE | seedance-20 (Iamemily2050, @iamemily2050), v6.7.0 | MIT |
| skills/seedance-20/assets/fonts/OFL.txt | fonts in seedance-20 | SIL OFL 1.1 |
| skills/edit-director/NOTICE.md | edit-director (edit-studio, by Arseniy per owner): openai-whisper re-implementation notice | MIT (OpenAI, 2022) |
| skills/edit-director/engine/models/LICENSES.md | edit-director models and downloads inventory | see file |
| skills/edit-director/engine/assets/fonts/*_OFL.txt (17 files) | bundled fonts: Anton, Bebas Neue, Caveat, Cormorant Garamond, Dela Gothic One, Fira Sans Extra Condensed, Great Vibes, Inter, JetBrains Mono, Montserrat, Noto Sans, Nunito, Oswald, Playfair Display, Press Start 2P, Rubik, Unbounded | SIL OFL 1.1 |
| skills/hyperframes-creative/frame-presets/code-editorial/fonts/OFL-*.txt (3 files) | EB Garamond, Inter, JetBrains Mono | SIL OFL 1.1 |

## Shipped models (edit-director)

- skills/edit-director/engine/models/face_detection_yunet_2023mar.onnx: OpenCV Zoo YuNet, MIT, Shiqi Yu and contributors.
- skills/edit-director/engine/models/human_segmentation_pphumanseg_2023mar.onnx: PP-HumanSeg via OpenCV Zoo, Apache-2.0, PaddlePaddle Authors.
- Not shipped (downloaded on demand into the cache): U2-Net human segmentation, Noto Sans CJK, Whisper ONNX models. See LICENSES.md.

## Components by origin

| Component | Source | Licence status |
|---|---|---|
| edit-director, edit-gen, edit-voice (edit-studio) | Arseniy (per owner); engine ships NOTICE.md and LICENSES.md | Third-party notices preserved. No top-level LICENSE file for the edit-studio code itself found in the folder; owner to confirm terms. |
| higgsfield-timed-prompts | Adil (per owner). Source URL not recorded in the files. | No licence file shipped; owner to confirm. |
| faceless-script-writer, faceless-video-prompts | Adil (per owner). Source URL not recorded in the files. | No licence file shipped; owner to confirm. |
| creator-playbook-adil.md (in higgsfield-master/references) | Adil's creator techniques, summarised | No licence file; owner to confirm. |
| hyperframes and 13 hyperframes-* skills (hyperframes-animation, -cli, -core, -creative, -faceless-explainer, -general-video, -keyframes, -motion-graphics, -pr-to-video, -product-launch-video, -registry, -slideshow, -studio) | github.com/heygen-com/hyperframes (as named in higgsfield-master references/sources.md) | Apache-2.0 per the owner's Remotion note in the skills. FLAG: no Apache LICENSE or NOTICE file ships in these folders; Apache-2.0 requires the licence text to accompany redistribution. Add the upstream LICENSE before any wider distribution. |
| remotion-captions, -create, -docs, -interactivity, -maps, -markup, -multimedia, -render, -saas, -studio (v4.0.534) | github.com/remotion-dev/skills (named in sources.md) | Remotion licence, not an open-source licence. FLAG, COMPANY SIZE: free only for individuals and for-profit companies with 3 or fewer employees; larger companies need a paid Company License. Every remotion-* SKILL.md keeps its licence note intact. Upstream public docs-search key replaced with a placeholder in this package. No LICENSE file ships in these folders. The owner has said they will not buy a Company License; use only for the owner's own work or clients with 3 or fewer employees, otherwise use motion-reel or hyperframes. |
| seedance-20 (with its 20+ sub-skills) | Iamemily2050 | MIT, LICENSE preserved |
| seedance-auto-generate | github.com/beshuaxian/higgsfield-seedance2-jineng (source line in its SKILL.md) | No licence file shipped; owner to confirm. |
| 01-cinematic to 15-real-estate (seedance style packs) | Seedance 2.0 style packs, upstream not recorded in the files | No licence file shipped; owner to confirm. |
| higgsfield-image-auto, ugc-video-auto | Playwright automation skills, upstream not recorded | No licence file shipped; owner to confirm. |
| higgsfield-master references | cite OSideMedia/higgsfield-ai-prompt-skill and Higgsfield documentation as research sources (sources.md); text is a summary, not a copy | Reference only |
| create-ads-with-agents (v2.1.2) | upstream not recorded | `license: MIT` in its frontmatter |
| motion-reel, minimax-h3-motion-design, webgpu-wgsl, graphics-rendering | upstream not recorded | No licence file shipped; owner to confirm. |

## Owner-authored skills with `license: MIT` frontmatter

cast-real-people, color-grading, creative-studio, film-legal-distribution, film-studio, higgsfield-master, indic-languages, music-and-sound, performance-direction, photoreal-humans, production-tracking, title-and-key-art, vfx-compositing, voice-studio declare `license: MIT` in SKILL.md. This differs from the plugin's proprietary licence. Left unchanged.

## Flag summary

1. Remotion: company-size condition (3 or fewer employees), no paid licence held.
2. hyperframes: Apache-2.0 text missing from the folders.
3. Several third-party skills (Adil's, edit-studio code, seedance packs, automation skills) ship no licence file; ownership of redistribution rights rests on the owner's statement.
