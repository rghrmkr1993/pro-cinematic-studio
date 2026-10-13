# Delivery and legal (Phase 5)

Not legal advice. Legal, regulatory and certification sign-off belongs to qualified counsel and the Manager. Specs change: re-check the live source (festival tech page, platform help, CBFC portal) before delivery. Labels: (F) from a source, (3P) secondary, (E) estimate, (A) assumption.

## 1. Master and mezzanine
- Master (archive): ProRes 422 HQ or 4444 in a MOV at 24 fps, 1920x1080 or 3840x2160, Rec.709 SDR, 48 kHz 24-bit PCM stereo plus 5.1 if mixed, plus the M and E stem and a text-free version. ProRes via ffmpeg: `-c:v prores_ks -profile:v 3 -vendor apl0 -pix_fmt yuv422p10le -c:a pcm_s24le` (profile 3 = HQ, test run 2026-10-14 on ffmpeg 9.0.1).
- Frame rate: 24 fps for features (23.976 only if the platform asks). Keep generation, edit and export at one rate.
- Resolution reality: most generators output 720p to 1080p (some 4K); upscale last, and describe the source resolution honestly in the delivery note. Do not claim native 4K for upscaled material.
- Archive: lock files, prompts, seeds, references, EDL, stems, project files, licences.

## 2. Platform specs (re-check before delivery)
| Destination | Spec (3P unless stated) | Notes |
|---|---|---|
| YouTube | MP4, H.264 High, closed GOP, 2 B-frames, 4:2:0, moov at front, AAC-LC 48 kHz; 4K SDR 24 to 30 fps about 35 to 45 Mbps; HDR needs BT.2020 and is not supported below 720p | Upload at or above recommended bitrate; thumbnails 1280x720; chapters in description; altered content setting in Studio |
| OTT (Netflix style) | ProRes or IMF (SMPTE), 24 fps native, 5.1 and stereo mix, loudness -27 LKFS dialogue-gated, true peak -2 dBTP, timed text TTML or per guide, QC report | Netflix requires an approved path; aggregators exist for smaller films; check minimum resolution (4K native for originals, F per vendor) |
| Festival online screener | H.264 MP4 1080p, 8 to 20 Mbps, stereo, burned or sidecar English subtitles | Platform may be Film Freeway or festival portals; check watermark rules |
| Festival projection | DCP (below) or ProRes file as the festival states | Test the file on the venue spec |
| Theatre (India and global) | DCP, 2K or 4K, Flat 1998x1080 or Scope 2048x858, 24 fps, 5.1 or stereo | Needs a DCP lab or a tool and a test screening |
| Social | 9:16, 1:1, 16:9 trailers, text-safe areas | Trailer cut, 30 to 90 s, subtitles burned in |

## 3. DCP basics (3P, vendor guides, read 2026-10-13)
- A DCP is a folder of assets, not one file: JPEG 2000 picture in MXF, uncompressed 24-bit WAV audio (up to 16 channels), CPL and PKL and other XML. Cinema servers do not decode H.264.
- Picture: 2K (2048x1080) or 4K (4096x2160) container; Flat 1998x1080 (1.85:1) or Scope 2048x858 (2.39:1) in 2K; DCI-P3 colour with gamma 2.6, XYZ, JPEG 2000 up to 250 Mbit/s.
- Audio: 5.1 as six mono WAVs at 48 kHz 24 bit (L, R, C, LFE, Ls, Rs); stereo acceptable.
- Interop (legacy, widest compatibility) versus SMPTE (modern; needed for Atmos, HDR, encryption); festivals vary, so ask. Naming: ISDCF convention. Subtitles go in a separate version file (VF) beside the original version (OV).
- Size: about 100 to 200 GB per hour in 2K (3P); budget a lab fee, typical professional creation 500 to 2000 USD (3P).
- Workflow (A): grade in Rec.709 SDR, convert to DCI-P3 XYZ with a DCP tool (such as open-source DCP-o-matic, check licence) rather than ffmpeg alone; test on a cinema server.
- Always get a test screening or lab QC before the festival date.

## 4. Metadata and credits
Title, logline, synopsis, cast and crew (AI roles named as such: "AI-generated performances", "AI video generation direction"), runtime, language, subtitle languages, country, year, genre, rating. Credits include tools and music sources as required by licences, and a clear note of what was AI-generated. Poster, stills, trailer, press kit by growth-marketer.

## 5. Disclosure (F unless noted)
- YouTube: the altered or synthetic content setting is required when content looks realistic and could be mistaken for a real person, place or event (synthetic voice clones, fabricated real events). Stylised animation and colour correction do not need it. Non-disclosure risks a label added by YouTube, removal or partner suspension.
- Meta and others: use the platform's AI label tools.
- India: the IT (Intermediary Guidelines and Digital Media Ethics Code) Amendment Rules 2026 (notified 10 Feb 2026, in force 20 Feb 2026) require platforms to have users declare synthetically generated information, with visual or audio labels and metadata where feasible; duty falls on platforms, high-risk deepfakes are removed within 2 hours of a valid notice (3P, law-firm summaries; read the gazette text). We label every realistic AI person or event.
- Festivals: disclose AI use in the submission, per stage (pre-production, generation, post); Sundance wording is broad (any use, including denoise and upscale), TIFF and Berlinale expect disclosure, SXSW has an AI category, some AI-specific festivals require generative tools; Tribeca sources conflict, read the form. A director's statement on how AI was used is expected (3P, Aug 2026).
- Oscars (99th, rules published May 2026, 3P): AI use is neither a help nor a hindrance; human authorship is weighed; acting performances must be demonstrably performed by humans with consent to be eligible, so a fully synthetic film is unlikely to be eligible for acting categories.
- Documentary style and news-like pieces: label fictional recreations; never fabricate real persons or events.

## 6. Copyright and IP (the rules we apply)
1. Inspired by a genre is allowed; copying is not. Free: genres, tropes, structures, general ideas, public-domain works (check country and edition), historical facts, styles described by qualities.
2. Never use protected characters, worlds, names, designs, plots or distinctive visual elements: for example do not make a clownfish dad searching for his son named Nemo, a blue tall alien race called Na'vi, a boy wizard at a school of magic, a masked billionaire vigilante, or any named franchise hero, even with changed names. Test: could a viewer name the source from characters and setting? If yes, redesign: change species, silhouette, colour script, role, name, world rules and plot.
3. No prompts naming studios, living artists, franchises, films or actors as the target look; describe qualities. No uploading frames of protected films as references.
4. Real people: no depiction of a real person's face, voice or name without written consent (likeness, publicity and personality rights, plus laws on deepfakes); no celebrities; no living public figures in fictional or defamatory scenes; deceased persons and estates: counsel.
5. Original characters: keep a creation record (character bibles with dates, prompts, versions) as evidence of authorship.
6. Music, sound and fonts: licences logged (sound-music-voice.md section 6); fonts with film licences.
7. Third-party assets in references (photos, architecture, artworks, logos, trademarks): use only own, licensed or public-domain material; avoid real brand logos and trademarks in shots; fictional brands only (no client brand in another client's film).
8. Mythology, epics, religious figures: public-domain texts, but depictions carry regulation and sensitivity risk (see section 8); retellings with copyrighted modern designs are protected.
9. Copyrightability of the film itself (F, US Copyright Office Part 2, Jan 2025): prompts alone are not enough for authorship; human selection, arrangement, editing, writing, and modifications are protectable; document human contribution (script, boards, edit, music, VO) and register accordingly; India and other regimes differ, counsel.
10. Platform terms: generator terms may grant the vendor a licence to content and training use; enterprise plans carry IP indemnity only for some (higgsfield-master help-center-facts.md). Do not upload confidential scripts or client assets without client approval.
11. Contracts: crew and voice actors (consent for AI use, voice rights), composer, editor, adviser; chain of title file.
12. Errors and omissions insurance and clearance report for distribution (3P norm for features).

## 7. Consent and ethics file (`ledgers/consents/`)
Per person or voice: name, role, what is used (face, voice, likeness, performance), scope, term, territory, fee, signature, date; a withdrawal clause; no minors without guardian consent and counsel. Digital replicas follow union and local rules (E).

## 8. India: CBFC certification basics (F from PIB, CBFC and MIB pages read 2026-10-13; confirm on the portal)
- All films for public exhibition in India need CBFC certification, applied for on the e-Cinepramaan portal after CBFC registration and ID allotment.
- Categories: U (unrestricted), UA with age markers 7+, 13+ and 16+ (Cinematograph (Certification) Rules 2024, recommendatory), A (adult), S (specialised audience). Certificates are valid in perpetuity under the 2023 Amendment Act (earlier 10 years). A or S films need a fresh certificate for TV or other media.
- Application items listed in the 2024 Rules: prescribed fee, synopsis with full credit titles, complete script including full lyrics, and a declaration; secondary sources also list cast and credits, lab or format certificate and authorisations (3P). Prepare: DCP or file per the portal, subtitles (English), music licences, consent and rights file.
- Time: Rule 37 sets 48 working days; CBFC reported averages of about 18 working days for features and 3 for shorts (PIB Feb 2026). Allow buffer for cuts and re-examination. Appeals go to the High Court.
- Feature films must carry accessibility features for persons with disabilities to be certified (F per summaries); plan captions or audio description.
- The sources read did not mention an AI declaration on the CBFC form: check the live form and notices (A: ask the regional office).
- Online release (OTT, YouTube) does not need CBFC certificates in the same way, but intermediary rules, platform policies and general law apply; counsel to confirm for each platform.
- Content flags for CBFC and platforms: violence, sexual content, religion, community, nudity, drugs and smoking warnings, language; add the statutory health warnings where tobacco is shown (F, rules; E, scope).
- For other countries: MPA (US), BBFC (UK), classification boards; same principle.

## 9. Delivery gate G5 checklist
Master archived with checksum; exports passed QC on the real file; loudness reported; subtitles QC; DCP tested if used; rights file complete; credits approved; AI disclosure text per platform; consent files; CBFC dossier if needed; marketing assets; the user's explicit yes to publish or submit; nothing sent or uploaded by agents.
