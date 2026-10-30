# Face dataset and training (cast-real-people)
Labels: (V) vendor-official, (3P) third-party, (U) unverified. Researched 2026-10-14. Consent gate in SKILL.md section 1 must pass before any photo is shot or uploaded.

## 1. What the platform asks for (Higgsfield Soul ID)
- (V help center) Train once on 20 or more photos of one person, up to 80. Include at least one full-height photo. Avoid sunglasses, hats, scarves, heavy shadows, cropped or head-only shots and group photos. A smaller clean varied set beats a large inconsistent one. Prefer recent photos. Training takes a few minutes.
- (V) Consent: only photos of yourself or of someone who gave permission to use their likeness. A trained Soul ID cannot be exported as a file, represents one person, and gives "recognisably the same person", not pixel-identical results. Multi-person scenes use Elements.
- (3P) 960 px or more per photo; recency of 4 to 5 months; about 3 to 5 minutes training; roughly 25 credits (U, cost is not stated in the help text, quote from the Generate button first).
- (U) Some third-party pages describe a CLI or API route taking 5 to 20 face photos; treat it as a different workflow and verify before use.
- Studio rule: use 30 to 40 photos so that about 25 percent can be dropped after review.

## 2. Shot list for the person (target 36)
| Group | Count | Notes |
|---|---|---|
| Front, neutral, eyes to lens | 5 | even light, mouth closed, shoulders square |
| Three-quarter left and right | 6 | chin level, eyes to lens or just past it |
| Profile left and right | 2 | ear visible, hair tucked or natural per bible |
| Tilt up and down (10 to 15 degrees) | 4 | do not exaggerate |
| Expressions | 8 | soft smile, wide smile with teeth, laugh, serious, concern, surprise, thoughtful, eyes closed once |
| Half body | 5 | arms natural, wardrobe variety |
| Full height | 3 | head to shoes, plain wall, neutral pose |
| Wardrobe and hair variants | 3 | hair down, hair tied, with glasses if the role needs them (clear lenses, no glare) |
Total 36. Add a few shots of the exact period look (beard stage, hairstyle) if the film needs it.

## 3. Lighting
- Soft window light at 45 degrees to the face, or open shade outdoors; neutral white balance. Mix 2 or 3 lighting set-ups so that the model learns the face rather than the light.
- No on-camera flash, no ring-light glare in the eyes, no coloured LEDs, no heavy backlight, no harsh noon sun.
- Keep a grey card or a white sheet in the first frame of each set-up so that skin tone can be checked later against a neutral reference (colourist).
- Brown and deep skin: shoot at a little higher exposure so the face is not crushed, never lighten in post; check the skin line with color-grading.

## 4. Phone settings
- Rear camera, main lens (1x) or 2x portrait lens; not ultra-wide (distorts nose and jaw) and not the selfie camera unless it is the only option (softer, mirrored).
- Resolution: full resolution JPG or HEIC (12 MP or more), not screenshots, not messaging-app copies (compressed). Turn off HDR auto, beauty, portrait retouch, skin smoothing, filters, Live Photo, night-mode over-sharpening. Apps: native camera in standard or "natural" profile.
- Tap to focus on the nearer eye. Hold the phone at eye level, 1 to 1.5 m away, tripod or a helper. Wipe the lens. Burst only for expressions, then pick the sharpest.
- Remove metadata that shows location before sharing (EXIF GPS), but keep the original dated file in the private folder to prove recency.

## 5. Checklist for the person being photographed
- [ ] I have read and signed the release; I understand what AI generation of my face means.
- [ ] I can ask to stop or delete at any time, and I know who to message.
- [ ] No makeup change from my normal look unless the role needs it; no heavy contouring, no filters, no lens-style tinted glasses.
- [ ] Hair, beard and glasses are as they are today (or as the film needs, noted).
- [ ] Clean front-facing face, ears and hairline visible in most photos; no hats, scarves or hands over the face.
- [ ] Only me in the frame. No friends, no children in the background.
- [ ] I will send the original files (not WhatsApp-compressed) through the private upload link only.
- [ ] I will review the first test grid and say yes or no.
- [ ] I know the voice is covered separately and only if I ticked it.

## 6. Dataset QA before upload (casting-director)
1. Remove blur, closed-eye accidents (except the one intended), heavy shadow, duplicates and near-duplicates, group shots, filtered photos, photos older than 6 months, and any photo that is not clearly the signer.
2. Check there is variety in angle, expression, light and background; reject sets where more than 30 percent share one pose.
3. Check skin colour is consistent across the set; if phones differ, fix white balance only, never lighten.
4. Name files `<person>_NN_<angle>_<expr>.jpg`, stored in `refs/<person>/dataset/` (private). Record the count and date in the consent .md.
5. Weak set? Retake. Do not pad with AI-generated photos of the person for the first training (circular drift). A second training round may add chosen test-grid winners only after QA.

## 7. Training steps (Higgsfield web or MCP; MCP is `show_characters` and reference-element tools, see higgsfield-master mcp-operations.md)
1. Owner approves the cost quote (training plus test grid).
2. Name the Soul ID `<project>_<person>_v1`; upload the clean set; train; wait.
3. Run the 6 to 9 shot test grid (identity-consistency.md), score with the scorecard.
4. If face match is under 90: retrain with a better set, not more prompts.
5. Promote the best 4 to 6 test outputs (front, 3/4 L, 3/4 R, profile, smile, serious) into an Element or reference set for video models.

## 8. Other tools and their face rules
| Tool | Face-reference mechanism | Limits and notes |
|---|---|---|
| Higgsfield Soul ID (V) | trained identity, Soul family models, Elements in Seedance (real people need Soul ID first, V per characters-and-consistency.md) | 20 to 80 photos, one person per ID |
| Nano Banana Pro / Gemini image (3P, Google docs summary) | reference images in the request | up to 14 images per request: up to 6 object refs plus up to 5 character refs; best fidelity with 6 or fewer; master reference front-facing, even light, neutral expression; say what must not change |
| Kling O1 / 3.0 Elements (3P) | Element built from multi-angle images, called with @Element tags | about 4 images per Element, up to 7 simultaneous references via one API host; verify current limits on the Higgsfield page |
| Veo 3.1 Ingredients (V Google docs summary) | up to 3 reference images of a person, character or product | person-generation setting allows adults only; fewer slots than Kling |
| Seedance 2.0 / 2.5 (V help) | @character image refs (9 images on 2.0; 30 on 2.5) | face lock weakens in wide shots and fast motion |
| Higgsfield Face Swap (V page) | swaps a face into photo or video | page says it is for creative and professional use with strict policies against non-consensual content; (U) a consent tick-box may appear on upload. A tick-box is not a release. Use only with a signed release and only to repair or place a consented face; never to put a face on another real person's body without that person's release too |

Policy facts (V): the Higgsfield terms prohibit outputs that harm minors, including real or synthetic depictions of minors in inappropriate ways, and prohibit inferring sensitive attributes of an identifiable person. The excerpt read did not show a dedicated real-person likeness clause (U); read the live terms before a commercial job. Paid plans carry commercial rights; Higgsfield claims no ownership of outputs but licenses content to improve its models (deletion stops future use, not past; Enterprise is excluded) per help-center-facts.md.

## 9. Age and expression range
- Fact-based rule: age shifts (younger or older) and extreme expressions are where identity drifts most. Build them as separate locks, not prompt adjustments.
- Age: shoot or generate a separate reference sheet per age state ("present", "+15 years") with the person's written approval, since ageing a face is an edit of their likeness. Keep scars, moles and bone structure; change skin texture, hair colour and lines.
- Expression: test 6 expressions (neutral, smile, laugh, anger, grief, surprise) at intensity 1 to 3 (asian-human-reference expressions-and-emotions.md; performance-direction for beats). Check that the eyes, nasolabial folds and teeth still read as the person.
- Regional realism: use asian-human-reference for skin undertone, hair and grooming ranges; never lighten, narrow or "idealise" the face.
