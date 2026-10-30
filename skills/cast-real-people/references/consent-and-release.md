# Consent and release (cast-real-people)
Not legal advice. HAVE A LAWYER REVIEW this template before first use and before any commercial release. Indian law (Contract Act, DPDP Act, personality rights) and the person's home law may both apply. Labels: fact, estimate, assumption.

## 1. Where it lives
`company/creative/<client>/<project>/consent/<person>.md` (summary record) plus the signed PDF or scan stored beside it. The .md holds: person, role, date signed, scan file name and SHA-256 hash, witness, ID check method (not the ID number), scope flags, expiry date, revocation status, link to the generation log.

## 2. Release outline (one document per person per project)
1. Parties: the person (and guardian if a minor), the producer or client, the studio. Contact details, held privately.
2. Project: title, client, version, purpose (film, ad, trailer, social cut).
3. Grant, itemised as separate yes or no boxes initialled by the person:
   - Photographs taken for the dataset (fact: capture is a separate act from generation)
   - Training a Soul ID or reference set from those photos
   - AI-generated images of the person
   - AI-generated video of the person
   - Voice recording, voice cloning and lipsync (separate clause, see voice-studio)
   - Digital replica in scenes the person did not perform (stunts, other locations, other ages)
   - Edits that change wardrobe, hair, age or setting
   - Use in trailers, posters, thumbnails, behind-the-scenes, festival and promo
4. Scope: media (web, social, OTT, cinema, TV, print), territories (India, named countries or world), start date and duration (term), exclusivity if any, sub-licensing to the client and platforms.
5. Content limits (fixed, cannot be waived): no nudity or sexual content, no political or religious messaging, no fake testimonials or endorsements, no content the person finds defamatory, no use for any other project. The person approves the script lines and key stills before release.
6. Approval rights: right to see the test grid and final cut before publication; objections handled within an agreed number of days (suggest 5 working days).
7. Payment: fee, schedule, kill fee, credit line, expenses. If unpaid, say so and why. Payment never changes the content limits.
8. Revocation and deletion (see section 3).
9. Data protection: what is stored, where, who can access, retention period, vendors involved (Higgsfield or other named tool), vendor terms summary, the person's right to ask for a copy and for deletion.
10. Disclosure: the person agrees the work is labelled as AI-assisted where rules require, and agrees the credits line.
11. Warranties: person confirms they are over 18 (or guardian signs), own the photos supplied, and no conflicting exclusive contract (for example with an agency or another brand).
12. Governing law, jurisdiction, dispute process, language of the signed version (offer a Tamil, Hindi or other local-language version for the person to read; a plain-language summary page on top).
13. Signatures, date, place, witness; plain-language summary signed too.

## 3. Revocation and deletion process
1. Request: any written message (email or chat) from the person counts as notice; log date and time.
2. Within 24 hours: freeze the identity lock (rename folder `_REVOKED`), stop any queued generations, tell prompt-engineer and creative-director.
3. Within 7 days (target): delete the Soul ID or Elements, raw dataset, lock sheets and unused generations from the studio and platform accounts; ask the vendor to delete if a support route exists; record confirmations.
4. Published work: assess with the lawyer. Fact: DPDP withdrawal of consent does not by itself undo lawful processing already done (3P reading). The release should state what happens to finished films already delivered (typical options: stays in the cut for the paid term, or is pulled at the producer's cost). Pick one before signing.
5. Keep: the signed release, the revocation notice and the generation log. Do not keep the face data.
6. Close out: update the consent .md with status REVOKED, date, who actioned, what was deleted.

## 4. Self-release for the owner
Same template with the owner as grantor and the studio as producer. Signed and dated before the dataset is shot. The owner may revoke by the same process.

## 5. Minors (under 18)
Default: do not cast. Marketing, beauty, cosmetic, anti-ageing, skin-result and body-image content with a minor is out of scope.
If a minor is essential to the story, all of the following are required, and a lawyer must approve first:
- Written consent of a parent or legal guardian, verified by ID and relationship check; the child gives age-appropriate assent, and either may stop at any time. DPDP treats under-18 as a child and expects verifiable parental consent (3P; applies from 13 May 2027). Treat it as binding now.
- Child-labour and child-performer permits where the local law requires them (assumption: rules differ by state; check).
- No tracking, profiling or targeted advertising built from the child's data. No voice cloning of a child. No Soul ID of a child for any use beyond the single named film.
- Wardrobe fully covered, no suggestive context, no swimwear or glamour, no romantic or violent content with the child's face. Any request that sexualises a minor is refused and escalated to the Manager (see SKILL.md section 8).
- Shorter retention (delete 14 days after final delivery), guardian present at capture, guardian can revoke at any time and is a named recipient of the generation log.
- When the child turns 18 during the term, ask for a fresh adult consent or end use.

## 6. Public figures and celebrities
Own written release from the person (or their registered representative with a power of attorney). A release from an agency, a brand contract or a past photoshoot release is not enough for AI use. Courts in India grant injunctions in favour of well-known people against unauthorised AI use of face and voice (see law-and-platforms.md), so the risk is real. Parody and news exceptions are a lawyer's call; the studio does not rely on them.

## 7. Refusal wording to use
"We cannot start casting this person without a signed release that covers AI generation. Here is the template. Until it is signed and filed, no photos are uploaded and no credits are spent."
