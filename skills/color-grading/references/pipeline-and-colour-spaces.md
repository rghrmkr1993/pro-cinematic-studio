# Pipeline and colour spaces
Labels: (V) vendor-official, (3P) third-party, (H) house rule, (E) estimate, (U) unverified. Researched 2026-10-14. Sources: ACES Central docs (docs.acescentral.com), Blackmagic Resolve materials, colourist blogs; ffmpeg recipes run on ffmpeg 9.0.1.

## 1. The chain in plain words
Scene light, camera encoding (log or display-referred), working space, creative grade, display transform (output), display. Each arrow is a defined conversion. Most grading mistakes are a missing or doubled conversion (a clip treated as log when it is already Rec.709, or a LUT applied twice).
- Scene-referred: pixel values proportional to real light, wide range (camera log, EXR, ACES). Needs a view transform to look right.
- Display-referred: values already shaped for a screen (Rec.709, sRGB). AI clips are this. No view transform needed, only correct tagging.
- Log (a camera encoding like S-Log3, LogC, V-Log) compresses wide range into a flat image; a LUT or transform brings it to display. Real log appears only with real camera plates in hybrid work (vfx-compositing).

## 2. Display standards in one table
| Standard | Primaries and white | Transfer | Peak (nominal) | Use |
|---|---|---|---|---|
| Rec.709 | BT.709, D65 | gamma about 2.4 (BT.1886) for grading rooms; web reality closer to sRGB 2.2 | 100 nits | Default for web, social, OTT SDR (V ITU) |
| sRGB | BT.709 primaries | piecewise, about gamma 2.2 | 80 to 100 nits | Browsers, phones, images |
| DCI-P3 (D65 or theatrical white) | wider red and green | gamma 2.6 for cinema | 48 nits cinema | Cinema projection, DCP, Apple displays use Display P3 |
| Rec.2020 PQ or HLG | very wide | ST 2084 PQ or HLG | 1000 to 4000 nits mastering | HDR delivery |
Notes: (1) Display P3 is P3 primaries with D65 white and sRGB-like transfer, used by Apple devices; DCI-P3 cinema has a different white point and 2.6 gamma (3P, H: verify the exact variant a client asks for). (2) The 2.4 versus 2.2 mismatch makes a Rec.709 grade look lifted or crushed on the web; decide one target per deliverable and test on a phone (3P, H).

## 3. Which target to deliver (decision)
- Default: Rec.709 SDR, tagged bt709. AI sources are SDR, so this loses nothing.
- Cinema or festival DCP: grade in Rec.709 then convert, or grade P3 only if a colourist can monitor it; the source gamut is sRGB so P3 does not add real colour (H, E).
- HDR: AI clips are SDR. Inverse tone-mapping to HDR creates fake highlights; deliver SDR unless a platform requires HDR, then do it on a Studio-grade tool with an HDR monitor (H). Resolve HDR grading tools are reported as Studio-only; sources conflict, check Blackmagic's comparison page (3P, U).
- Cross-delivery: SDR master first, derive others; never grade HDR first and tone-map down for an AI film.

## 4. ACES (when it earns its place)
- ACES is a colour management system: input transform (IDT) to ACES2065-1 or a working space, grade in ACEScct or ACEScg, then an output transform to the display (V acescentral docs).
- ACES 2.0 changed the output transform: it works in a perceptual JMh space, tone-maps lightness only, keeps hue, has gentler highlight roll-off and lower mid contrast than ACES 1, and adds gamut mapping (V docs.acescentral.com about-rendering, read 2026-10-14). Community threads discuss Resolve behaviour; the exact Resolve version that ships 2.0 is not confirmed here (U).
- Use ACES when: mixing real camera log plates with CG or AI plates; multiple deliverables (SDR, P3, HDR) from one grade; EXR VFX handoff.
- Skip ACES when: an all-AI 8-bit Rec.709 film. It adds a conversion that cannot recover anything and risks a wrong IDT. A simple Rec.709 timeline is safer (H).
- If used: set each AI clip's IDT to sRGB or Rec.709 (match the real tag), work in ACEScct, output Rec.709 (ACES 2.0 or 1.x per project, note which in grade-notes.md). Never mix ACES 1 and 2 transforms in one project.
- Resolve setup keywords: Color Science set to ACEScct, ACES version, input transform per clip, output transform for the monitor (3P tutorials; confirm menu names on the installed build).

## 5. AgX (when it earns its place)
- AgX is a view transform (default in Blender since 4.x; Blender 5.0 also offers an ACES 2.0 view) giving a filmic highlight handling without hue skews (3P, 80.lv and famousandfaded).
- Relevance: CG renders from Blender in a CG plus AI composite. Render with the project view transform noted, export EXR linear or a display-referred PNG in Rec.709, and tell the colorist which (H).
- Resolve does not list AgX as a native option in the sources found (3P, U); treat AgX plates as pre-viewed display images, not scene-referred.
- Do not apply AgX look to AI clips; it is a transform, not a style.

## 6. DaVinci Resolve colour management (free edition)
- Colour managed mode ("DaVinci YRGB Color Managed", RCM) or ACES, or a plain unmanaged Rec.709 project (3P, V docs, U on menu wording; confirm in your build).
- Simple, reliable AI-film setup: unmanaged project, timeline Rec.709 (gamma 2.4 or sRGB per target), grade by eye and scopes, tag on export. Fewer moving parts.
- Free versus Studio (3P: simonsaysai, miracamp, digitalfilmmaker): grading engine, nodes, curves, scopes, Fusion page and LUT generation are in free; HDR tools, temporal and AI noise reduction, Magic Mask, some OpenFX and grain tools are Studio-listed; free exports up to UHD at 60 fps. Sources disagree on Color Warper and HDR; check the official comparison (U).
- Generate a LUT from a grade: Color page, right-click the clip thumbnail, Generate 3D LUT (CUBE), choose 33 points. Free version supports it per a third-party guide; Blackmagic does not list it as paid (3P, U on edition limits).

## 7. ffmpeg colour handling (verified on 9.0.1, 2026-10-14)
Tag SDR export: `-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv` (a tag only labels; it does not convert).
Convert between matrices (filter `colorspace`): `-vf "colorspace=all=bt709:iall=bt601-6-625:fast=1"`.
HDR PQ to SDR (untagged input needs setparams or the zscale step fails with "no path between colorspaces"):
```
ffmpeg -i hdr.mp4 -vf "setparams=color_primaries=bt2020:color_trc=smpte2084:colorspace=bt2020nc:range=tv,zscale=t=linear:npl=1000,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" -c:v libx264 -crf 14 sdr.mp4
```
The setparams line is only for untagged files; for a correctly tagged HDR source drop it. Check the result on scopes; tone mapping is a rough preview, not a colourist HDR to SDR trim (H).
View scopes in the render: `vectorscope=mode=color3:colorspace=709`, `waveform=mode=column:scale=ire`, `histogram` (all present and run on 9.0.1).

## 8. Tagging and playback traps (3P, H)
- Untagged files are guessed by players; tag every export and every intermediate.
- QuickTime-based players and browsers apply different gamma assumptions to Rec.709 tags (3P). Compare the master in the target player and on a phone.
- Limited range (tv, 16 to 235) is the video default; full range (pc) for stills or when a tool says so. A range mismatch looks like crushed blacks or milky blacks.
- 8-bit banding in skies and skin gradients after a strong grade: work in 10-bit intermediates (ProRes 422 HQ or DNxHR HQX) and add grain before the final 8-bit encode (H).
- Convert once. Keep a log of every conversion in grade-notes.md.
