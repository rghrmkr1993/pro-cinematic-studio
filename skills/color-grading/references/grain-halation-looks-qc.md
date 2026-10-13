# Looks by genre, grain, halation, final QC
Labels: (V) vendor-official, (3P) third-party, (H) house rule, (E) estimate. ffmpeg lines verified on 9.0.1, 2026-10-14. Look intent words and the full stock list live in `cinematography` references/color-and-look.md; this file adds the grading moves.

## 1. Looks by genre: grading moves (H unless noted)
Colourist craft is a convention, not a rule. Pick one look per film and write the recipe down.
| Genre | Moves | Skin safety |
|---|---|---|
| Thriller | Pull saturation 10 to 20 percent, cool shadows slightly, deepen blacks, keep highlights neutral | Hold skin hue on the line; do not green the face |
| Romance | Warm highlights, lift shadows a little, soft contrast, gentle bloom | Warm light, not warm skin; protect skin saturation |
| Horror | Underexposed mids, green or blue shadow cast, tight contrast, restrained saturation | Face may go cool; keep it plausible, not grey |
| Period | Muted earths, lower saturation, warm mids, film grain, slight vignette | Keep tone from the lock, no sepia on skin unless flashback |
| Sci-fi | Cool shadows, cyan accents, clean whites, controlled neon pops | Isolate neon with qualifiers so skin stays natural |
| Indian commercial cinema | Richer saturation, strong separation, gold and red pops, glossy contrast | Rich but not orange; keep each face on the line |
| Indian realist | Natural contrast, lived-in muted colour, little stylisation | Closest to the lock |
| Korean-drama style | Soft contrast, pastel, gentle warm and cool split, lifted blacks (3P tendencies) | Never imply product-made glow; skin clean from light, not retouch |
| Documentary | True colour, minimal look, light contrast curve | Reference patch only |
| Luxury and beauty commercial | Controlled neutrals, gold or warm accent, clean skin, deep blacks | Truthful colour; no result implied |
| Teal and orange | Cool shadows, warm highlights, restraint; avoid for skincare and for brown skin close-ups | Use only if skin is windowed out of the push |
Look strength: build at 100 percent, ship at 60 to 80 percent unless the brief wants a bold look (H).
Consistent look rule: same node order and settings across the film; vary only exposure and a scene tint within tolerance.

## 2. Grain
Why: it unifies clips from different models, hides AI plastic smoothness, and avoids banding (H, 3P).
- Fine (35mm daylight stock), medium (500T-style), heavy (16mm, 8mm, push-processed). One grain size for the film.
- Apply last, after the look, before final encode; on the full frame, not per element.
- ffmpeg (verified): `noise=alls=6:allf=t+u` (temporal and uniform) for strength 4 to 8; higher looks digital. Luma-biased: `noise=c0s=7:c1s=2:c2s=2:allf=t`. For softer grain, add `gblur=sigma=0.6` to a noise layer and blend with `blend=all_mode=overlay` (H).
- Do not add grain on top of a clip that already carries heavy model noise; degrain lightly first (`hqdn3d=2:1:3:3`, verified) and re-grain.
- Check grain at 100 percent and at phone size: visible but not crawling, not stronger in shadows than in mids unless that is the look.
- Resolve film grain tools are listed as Studio features by some third parties (3P, U); free edition can use ffmpeg grain.

## 3. Halation and bloom
- Halation: red-orange glow around bright highlights, from light scattering back in film; stock backing normally limits it (3P, color-and-look.md).
- ffmpeg recipe (verified): isolate highlights, tint red, blur, screen back at low opacity:
```
split[a][b];[b]lutrgb=r='if(gt(val,200),val,0)':g=0:b=0,gblur=sigma=12[h];[a][h]blend=all_mode=screen:all_opacity=0.4
```
Tune threshold 190 to 230, sigma 8 to 24, opacity 0.2 to 0.5. Use sparingly on skin highlights: it can look like a reddish rash on brown skin; check faces (H).
- Bloom: similar without red tint, a wider blur on luma highlights, opacity 0.15 to 0.3.
- Pick one signature: grain, or halation, or bloom as the lead. Do not stack all at strength.
- Gate weave, scratches, dust: period and archive looks only.
- Vignette: `vignette=PI/6` at most, subtle (verified).

## 4. Deliver
- SDR master: Rec.709, tagged, 10-bit intermediate if available, plus the flat QC copy (no look) and the graded copy.
- Web or social: 8-bit H.264, tagged bt709, check in Chrome and phone.
- Safe: no fully crushed black (below 5 percent) on skin scenes for phone viewing; no white above 100 percent on SDR.

## 5. Final colour QC checklist (tick each; log in grade-notes.md)
Technical
- [ ] Every clip tagged and treated per its real source space; one conversion per step.
- [ ] Master tagged bt709 (or the delivery tag), range as intended.
- [ ] Waveform: no clipped whites or crushed blacks beyond intent; legal range for broadcast targets.
- [ ] No banding in skies, walls and skin gradients at full size.
- [ ] No flicker in graded clips; secondaries do not shimmer.
Matching
- [ ] Hero frame matched per scene; model-to-model cuts checked on neutrals and skin.
- [ ] Look LUT id and version recorded; no stacked creative LUT.
- [ ] One grain and halation recipe across the film.
Skin and brand
- [ ] Every face patch inside tolerance against the lock (luma, hue, saturation); before and after stills saved.
- [ ] No lightening, no desaturated grey cast, no orange mask, no green or magenta cast.
- [ ] Mixed groups: each face checked.
- [ ] Product and packaging colour true to the supplied pack; label legible; no grade implies a result.
Playback
- [ ] Reviewed on a calibrated monitor and on a phone and a laptop browser; differences noted.
- [ ] Flat QC copy delivered with the graded copy.
Critical fails (return to the colorist): skin tone lightened or shifted outside tolerance, tone mismatch with the lock, unlabelled HDR from SDR, a LUT applied twice, product colour wrong on a hero shot.
