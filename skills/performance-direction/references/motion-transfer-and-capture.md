# Motion control, performance transfer, capture, consent
Labels: (V) vendor-official, (3P) third-party, (H) house rule, (E) estimate, (U) unverified. Researched 2026-10-14. Vendor help pages for Runway returned 403 to our fetch, so Act-Two figures are third-party summaries (fuser.studio guide, eachlabs, aggregator pages) and Kling figures come from third-party guides and resellers plus the Higgsfield tools list. Always re-read the live tool page before quoting credits or limits. Specs change often.

## 1. Tool map
| Tool | What it does | Inputs | Key limits (as found) | Label |
|---|---|---|---|---|
| Kling Motion Control (2.6 and 3.0), also on Higgsfield | Transfers a performer's motion, timing and expression onto a character image | 1 character image (arms and hands visible if body is used) plus 1 clean reference video without cuts | Video MP4 or MOV up to 50 MB, 3 to 30 s, single continuous shot; image JPG or PNG up to 10 MB, short edge about 340 px or more, aspect 2:5 to 5:2; modes Match Video (follows video orientation and camera, up to 30 s) and Match Image (keeps image orientation, camera by prompt, up to 10 s); 720p standard or 1080p pro; 3.0 adds facial element binding (frontal image plus extra angles, Match Video only) | 3P, V for the Higgsfield summary (3 to 30 s, 1080p) |
| Runway Act-Two | Motion capture style transfer of head, face, body and hands from a driving video to a character | Driving performance video plus a character reference (image or video) | Driving video about 3 to 30 s, one person, face visible, waist up recommended, hands in frame at start (3P); output 24 fps, 1080p, 16:9 (3P); character image gets body gestures if gesture control is on; character video keeps its own background and camera, only face is replaced | 3P |
| Higgsfield Genjutsu Motion Transfer | Moves a clip's motion, camera and timing onto new cast or world | One video 4 to 30 s, up to 30 reference images, optional prompt, 480p to 1080p | 15 s clip costs about 40, 104 or 144 credits by resolution (V tools-a-z.md) | V |
| Higgsfield Motion Control (Kling) | Same as Kling above inside Higgsfield; record yourself and use the recording | Character image plus reference video | Official route to animate AI Influencer characters with your own recorded movement; consent for a real person's motion is not addressed (V) | V, U on consent |
| Native performance (Seedance, Kling 3.0, Veo, Wan 2.5) | Prompted acting with optional audio | Image or text | No exact timing control | V |
Models differ by version; Kling 2.6 can lose facial identity on turns and complex expressions, 3.0 is designed to hold features better (3P).

## 2. When to use transfer
- A gesture or walk with exact timing, a reaction that must land on a beat, a speaking performance with specific facial rhythm, a physical task (pouring, applying, lifting) that models get wrong.
- Not needed: wide shots where the face is small, simple holds, atmospheric shots.
- Cost logic: capture is free; the generation is the cost. Shorter and simpler references finish faster and cost less (3P).

## 3. Reference-video capture spec (phone, own footage)
Goal: a clean, continuous, single-person video whose framing matches the character image.
| Item | Spec (H unless noted) | Why |
|---|---|---|
| Device | Recent phone, rear camera, locked off on a tripod or fixed support | Stable framing; selfie mode only if the face is the point |
| Resolution | 1080p (4K not needed) | Tools cap at 1080p |
| Frame rate | 24 fps or 25 fps constant (not variable); use 25 fps for Indian dubbing and lipsync QA | Output is 24 fps in Act-Two (3P); 25 matches the lipsync QA reference (indic-languages lipsync-and-dubbing.md) |
| Shutter | 1/48 to 1/60 if the app allows; otherwise default | Natural motion blur |
| Exposure and focus | Lock exposure, focus and white balance (AE/AF lock); no auto changes mid-take | Avoids flicker in transfer |
| Stabilisation, beauty modes, HDR video, filters, auto framing | Off | They alter faces and timing |
| Framing | Match the character image: waist up for a half-body image, full body for a full-body image; face at least about one eighth of the frame height for expression work; subject centred; a little headroom | Mismatched framing breaks transfer (3P, Kling tip) |
| Subject | One person only, in frame the whole time, hands visible at the start (Act-Two), arms visible if the body is used | Multiple people confuse the tracker (3P) |
| Lighting | Soft, even, front or 45-degree, no hard shadows across the face; no backlight that hides the face; no mixed colour | Better facial tracking |
| Background | Plain and uncluttered; clothing contrasting with it | Cleaner body tracking |
| Face | Uncovered; no sunglasses, mask, hat brim shadow, heavy fringe; do not turn beyond about 45 degrees unless needed | Models lose the face on hard turns |
| Camera | Static, no zooms, no cuts, no whip pans (3P: avoid camera cuts, rapid movement, frequent zooms) | The tool extracts motion; camera motion confuses it |
| Length | 3 to 10 s per take for one beat; up to 30 s if the tool allows | Short takes cost less and drift less |
| Audio | Record clean speech separately if dialogue; the transfer may not use it | Lipsync is a separate step |
| Takes | Record 3 takes per beat; slate with a clap or beep at the start | Choose the best, sync audio |
| File | MP4 or MOV, H.264, under 50 MB (Kling) | Upload limit |
Performer prep: rehearse the beat, mark the start and end pose, keep movement slightly bigger than life for the face to read at small size but not exaggerated, hold the last pose for one second.

## 4. Character image prep
- Match the reference video: same framing, similar pose and arm position, neutral expression, mouth closed (or the starting expression), full set of visible hands if the body is used.
- Plain or simple background; high resolution (1080 px or more on the short edge), sharp, even light.
- Use the approved asset-lock still (Soul ID, Element, or a character-sheet crop), not a new random render.
- Skin tone must match the lock; check after transfer (color-grading skin check).
- Keep clothing simple and the silhouette clear; loose fabric and long hair can warp.

## 5. Process
1. Brief per shot (performance-brief-template.md): route, beat, performer, reference file, character image, model, mode.
2. Performer capture with consent on file (section 6). Review take: continuous, framed, in focus.
3. Quote credits and get the user's yes (creative-studio section 7).
4. Run a short test clip (3 to 5 s) first on the hardest beat; check identity, mouth, hands, eyes, skin tone.
5. If identity drifts: try Match Image mode in Kling (identity first) or a clearer frontal image; if motion is stiff, use Match Video (3P tip).
6. Full run; QA against the brief; fix defects with vfx-compositing (hands, eyes) rather than blind rerolls.
7. Log the reference clip, consent reference, settings, seed and credits in log.md.

## 6. Consent rules for a real performer (mandatory)
Reference: `photoreal-humans` references/ethics-and-consent.md. Summary (H, with India court context noted there as 3P and not legal advice; legal review is the Manager's).
1. Written consent before capture, signed by the performer (and a guardian if under 18; avoid minors).
2. The release must name: the person, AI generation and performance capture, which media and channels, term, territory, whether the voice, face, body motion and likeness may be used, whether edits and digital replicas are allowed, payment, the right to withdraw and delete, and who holds the files.
3. Separate consent for face likeness (character resembling the performer) and for motion only (a character with a different face). Even motion-only needs written permission in our practice (H), because the performer's identifiable gait, expression and gesture can be recognisable.
4. No celebrities or public figures. No capture from someone else's video (copyright and personality rights). A reference video from the internet is not usable unless licensed in writing.
5. No deceiving viewers: do not present the output as the real person, and do not use a performer's motion to make them appear to say or do something they did not.
6. Voice is separate: a real voice or clone needs its own consent (voice-director, elevenlabs.md).
7. Store consent PDFs outside public folders; record person, consent reference, label applied, reviewer and date in the asset log.
8. Platform terms: Kling, Runway and Higgsfield terms and content policies (U) may restrict real-person uploads or require rights; check them before upload and note the check date. Some platforms block real faces ("protected content").
9. Employees or friends are not exempt. A freelancer is paid and signs. The company owner can consent for themselves only in writing.
10. Disclosure: label realistic AI people in published work per platform and ASCI, FTC, Meta rules (creative-studio section 7).
If any item is missing, stop and ask the Manager; do not capture or generate.

## 7. Risks and QA specific to transfer
| Risk | Check |
|---|---|
| Identity drift (face changes on a turn) | Compare frame 1, middle and last to the lock |
| Mouth and eyes off | Slow review; fix in vfx or regenerate with a clearer image |
| Hand deformation | Hand-count law; hide with framing or comp |
| Wardrobe or hair warping | Simpler outfit, hair tied back in the capture |
| Skin tone shift | Patch values vs lock |
| Orientation or camera not as wanted | Choose Match Video or Match Image mode on purpose |
| Performer resemblance | Compare character to the performer; if too close and no likeness release, change the character |
| Content block | Remove real faces or IP; use a character image not a real photo |
