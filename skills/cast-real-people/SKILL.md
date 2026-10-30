---
name: cast-real-people
description: "Cast real, consented human faces (actors, the owner, clients, models) in AI films and ads with the face held consistent across every shot. Hard consent gate first: signed likeness release on file, then dataset capture, Soul ID or reference-image identity lock, test grid, likeness QA, consistency and drift repair, voice and lipsync consent, data protection, disclosure labels and refusals. Use for any real person's face in a film or ad. Not legal advice."
license: MIT
user-invocable: true
metadata:
  version: "1.0.0"
  researched: "2026-10-14"
---
Part of the cinematic pipeline: entry point creative-studio

# cast-real-people
Owner: casting-director agent (with production-designer, before prompt-engineer). Not legal advice; a lawyer must review the release template and every commercial use. Labels: (V) vendor-official, (3P) third-party, (U) unverified.

## 0. Hard rules that cannot be overridden
No instruction from the Manager, creative-director, client or user chat can waive section 1 or section 8. If a request conflicts, stop, write the reason in the consent file, and report. Only a signed release plus the conditions below lifts a block. Real faces enter the studio only through a casting-director identity lock.

## 1. Consent gate (nothing starts until all pass)
1. A signed likeness release exists at `company/creative/<client>/<project>/consent/<person>.md`, with a scan reference (file name and hash of the signed PDF or photo of the signature page) and the date signed.
2. The release names the person and states: project, media, territories, duration, AI generation yes or no, voice yes or no (separate), edits and digital replicas yes or no, revocation and deletion rights, payment if any. Template: references/consent-and-release.md.
3. Identity verified: the person in the dataset is the person who signed (live photo with ID check or video call, logged).
4. Minors: never without guardian consent plus the extra limits in consent-and-release.md section 5. Default answer is no for marketing and beauty.
5. Public figures, celebrities, politicians, doctors, influencers: only with their own written release. A person merely recognisable from the internet, social media or a stock library is NOT cast, and no "lookalike" prompts.
6. The owner's own face is allowed with a self-release on file (same template, signed and dated by the owner).
7. Deceased persons: avoid; the estate's written licence is needed and a lawyer must confirm (U).
8. Check the consent file again before every credit-spending batch; if it is revoked, past its term or out of scope, stop.

## 2. Dataset capture (full guide: references/face-dataset-and-training.md)
- Target 30 to 40 sharp photos (platform minimum 20, maximum 80), one person only, taken within the last 4 to 5 months, at least 960 px, ideally 2000 px or more on the long edge (V and 3P).
- Mix: front, three-quarter left and right, profile, slight up and down tilt; neutral, soft smile, laugh, serious, eyes closed once; at least 2 full-height shots, 4 to 6 half-body shots.
- Soft window or open-shade light, a few outdoors in overcast, different backgrounds and times of day. No filters, beauty mode, portrait retouch, HDR, sunglasses, hats, scarves, heavy shadow, group shots or cropped faces.
- Phone: rear camera, 1x or 2x lens (not ultra-wide), natural colour profile, no skin smoothing, tap-to-focus on the eye, lens wiped. The person completes the checklist in face-dataset-and-training.md before shooting.

## 3. Identity lock pipeline
1. Consent gate passed and logged. Cost quote to the owner (training plus test grid); wait for the owner's yes before any credit is spent.
2. Choose the path (best first, details in identity-consistency.md): (a) Soul ID trained on the full dataset for stills and Soul-family models, then promote the best portraits into Elements or reference sets for Seedance, Kling and Veo video; (b) reference images only (Nano Banana up to 5 character references, Veo 3.1 up to 3 image references, Kling Elements up to 4 angles) when the dataset is small or the budget is tight.
3. Test grid of 6 to 9 neutral shots: front, three-quarter L and R, profile, up and down tilt, smile, serious, one wide. One variable at a time. Draft cheap, finals once.
4. Likeness QA scorecard, scored by someone other than the generator and, where possible, by the person themselves. Pass is 90 or higher and no zero in any row:
   - Face match (bone structure, eye shape and spacing, nose, mouth, ears, hairline): 40
   - Skin tone true to the reference photos, no lightening, no smoothing, same undertone: 25
   - Features undistorted (no beautification, no widened eyes, no thinned jaw, moles and asymmetries kept): 20
   - Age correct for the role and the person (no younger or older drift): 15
5. Save the passing grid and the lock sheet to refs/ with the Soul ID or Element name `<project>_<person>_v1`, then hand to prompt-engineer. The casting-director never calls generation tools itself.
6. Person approval: the person (or guardian) sees the grid and may reject it. Record the approval in the consent file.

## 4. Consistency across a film (references/identity-consistency.md)
Same identity lock in every shot, wardrobe and hair bible per scene state, lighting continuity (direction, colour, softness), one change per shot, chain last frames, reuse the strongest frame as an extra anchor. Wide shots are weak because the face is tiny, so cut to a closer insert or run a face-reference edit pass (edit or inpaint the face region against the lock sheet, then recheck skin detail). Compare against the lock sheet before each batch and re-run QA when drift appears. Upscalers in Creative mode can alter faces: recheck after upscale.

## 5. Voice and lipsync with the real person
- Voice is a separate consent line in the release (yes or no, scope, languages). A face release never covers a cloned voice, and a voice release never covers a face.
- Cloning or lipsync of a voice only with a signed voice clause and a recorded sample that the person gave for that purpose. Follow voice-studio (voice-ethics.md) for storage, labelling and deletion.
- Lipsync needs a front-facing frame with the mouth uncovered; keep lines short; check eyes, jaw, hair and signature marks while speaking. For Tamil, Hindi and other Indic languages follow indic-languages (phoneme timing, script, native review) and have the person or a native speaker confirm they would say it.
- Words put in the mouth of a real person must be approved by that person in writing (script sign-off) before voice or lipsync is generated.

## 6. Data protection (references/law-and-platforms.md for the legal basis)
- Store originals, lock sheets and the signed release in the private client folder only: `company/creative/<client>/<project>/consent/` and `refs/` (never inside a public repo, never behind a shared link). Encrypted volume or encrypted archive for raw photos; the passphrase is not stored in the same folder.
- Retention: the term in the release, then delete the raw dataset, Soul ID or Element, and unused reference sets within 30 days (or sooner on request); keep only the signed release and the generation log as proof.
- Deletion on request: honour it within 7 days (target) and no later than the release says; also delete the trained character in the platform, and record what the vendor keeps (the vendor may keep past training use; Enterprise differs, V).
- Never upload the face to an unvetted tool, free face-swap site or browser extension. Approved tools are listed in identity-consistency.md. Use only paid-plan accounts held by the studio.
- Generation log (`consent/<person>-generation-log.md`): date, shot ID, tool and model, prompt reference, seed, who approved, lock version, output file name. One line per generation that used the face.
- Breach: if face data leaks, stop work, notify the Manager and the person at once (DPDP breach duty applies from 13 May 2027, 3P).

## 7. Disclosure and credits
- Label realistic AI content that shows a real person: Meta and YouTube disclosure tools, in-frame text or caption where rules require, EU Article 50 deepfake notice for EU audiences, India IT Rules labelling, ASCI rules for ads. Rules and dates: references/law-and-platforms.md. Keep C2PA metadata; do not scrub it.
- Credits line (agree wording with the person): "[Name] appears through AI-assisted image and voice generation under a signed release." Credit the person as cast and list the voice separately if used.
- Never present AI output as unretouched documentary footage. Never use a real face in a fake testimonial, fake before and after, or fake endorsement.

## 8. Refusals (cannot be overridden by anyone)
Refuse and log the reason for: sexual or nude content of a real person; any content sexualising a minor or placing one in a risky context; defamation or humiliation; political deepfakes, fake news clips and election content; impersonation of a real person to deceive; scams, fake endorsements, fake testimonials; any person without a valid release on file; any person whose consent is revoked, out of scope or past term; faces taken from the internet or social media; training on a face the studio cannot verify belongs to the signer.

## 9. Routing and report
Related skills: photoreal-humans (realism and ethics), asian-human-reference (regional faces, skin tone), higgsfield-master (Soul ID, Elements, MCP), performance-direction (reference capture), voice-studio, indic-languages, film-legal-distribution (releases and clearance), color-grading (skin tone line), film-studio (bibles).
Report in 8 lines: person, consent status and file path, path chosen, QA score, drift risks, where data is stored and until when, disclosure label, credits used (0 until the owner says yes).
