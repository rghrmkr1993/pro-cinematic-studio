# LUTs and ffmpeg grading
Labels: (V) vendor-official, (3P) third-party, (H) house rule, (U) unverified. Every ffmpeg line below was run on ffmpeg 9.0.1 (Windows build) on 2026-10-14 with synthetic clips unless marked (U). Re-run on your build before delivery.

## 1. What a LUT is and is not
- A LUT maps input colours to output colours. 1D LUT: per-channel curve. 3D LUT: full colour cube (sizes 17, 33, 65 points; 33 is the usual balance, 3P).
- It bakes colour and contrast only. It cannot hold windows, tracking, blur, grain or temporal effects (3P).
- A LUT assumes an input space. A Rec.709 creative LUT on a different input gives wrong colour. Record the expected input in the LUT name: `look-warm-film_r709in_r709out_v01.cube`.
- Never stack two creative LUTs. A corrective (technical) LUT first, then one creative LUT, is allowed (H).
- Apply LUTs at the end of the colour chain, before grain.

## 2. Apply in ffmpeg
```
ffmpeg -i in.mp4 -vf "lut3d=file=look.cube:interp=tetrahedral" -c:v libx264 -crf 14 -pix_fmt yuv420p -c:a copy out.mp4
```
- `interp` choices: nearest, trilinear, tetrahedral (default), pyramid, prism. Use tetrahedral.
- Strength control (blend 60 percent): `split[a][b];[b]lut3d=file=look.cube[c];[a][c]blend=all_expr='A*(1-0.6)+B*0.6'`.
- Hald CLUT (a PNG): `ffmpeg -i in.mp4 -i look_hald.png -filter_complex "[0][1]haldclut=interp=tetrahedral" out.mp4`.
- Tag the export after the LUT (pipeline-and-colour-spaces.md section 7).
- Batch a folder: loop over files with the same command; keep names equal to shot IDs.
- 1D or per-channel quick curves: `curves=preset=increase_contrast`, `eq=contrast=1.1:saturation=0.95:gamma=1.0`, `colorbalance=rs=.02:bs=-.02` (shadows red and blue offsets), `colorchannelmixer`, `lutrgb`. For shot-level correction, these are enough.

## 3. Create a LUT, route A: DaVinci Resolve free
1. Grade a frame on the Color page, using the primary palettes and curves (qualifiers, windows and blurs are ignored in a LUT, 3P).
2. Right-click the clip thumbnail, Generate 3D LUT (CUBE) (some builds say Generate LUT), choose 33 points, save the .cube (3P guide, Unity docs; the menu wording varies by version, U).
3. The LUT must be generated from the grade nodes only, with colour management consistent between generation and use.
4. Test the LUT back on the reference frame and on two other shots; compare to the original grade on the scopes.
Resolve free: grading engine, LUT generation and import are present; some Studio-only items are listed in pipeline-and-colour-spaces.md section 6.

## 4. Create a LUT, route B: ffmpeg only (no GUI)
Hald CLUT method:
```
ffmpeg -f lavfi -i haldclutsrc=level=8 -frames:v 1 hald_id.png
ffmpeg -i hald_id.png -vf "eq=contrast=1.1:saturation=0.9,colorbalance=rs=0.03:bs=-0.03" hald_look.png
ffmpeg -i in.mp4 -i hald_look.png -filter_complex "[0][1]haldclut=interp=tetrahedral" out.mp4
```
Run any colour-only filter chain on the identity image: the result image is the LUT. Level 8 gives a 512 x 512 PNG (verified). Keep the chain colour-only (no blur, noise, scale, crop, vignette).
Write a .cube from a function (identity template, verified to load in lut3d), then edit the transform inside the loop:
```
python -I - <<'E'
n=33
with open('look.cube','w') as f:
    f.write('TITLE "look"\nLUT_3D_SIZE %d\n'%n)
    for b in range(n):
        for g in range(n):
            for r in range(n):
                R,G,B=r/(n-1),g/(n-1),b/(n-1)
                # put the transform here, clamp to 0..1
                f.write('%.6f %.6f %.6f\n'%(R,G,B))
E
```
In a .cube the red index changes fastest. Keep a reference still graded in a GUI to compare against.

## 5. Match clips with numbers (ffmpeg)
Neutral patch or skin patch crop, before and after:
```
ffmpeg -i clip.mp4 -vf "crop=100:100:X:Y,signalstats,metadata=print:file=-" -frames:v 1 -f null - | grep -E "YAVG|UAVG|VAVG|SATAVG|HUEMED"
```
Adjust gain with `eq=brightness=...` or `colorlevels`, white balance with `colorbalance` or `colortemperature` (present in ffmpeg 9, check `-h filter=colortemperature`, U), until the hero and the clip agree. Then bake the correction into a corrective LUT (route B) named per model. Wide agreement on numbers does not guarantee the look; confirm on scopes and by eye in a split screen: `hstack` the two crops.

## 6. Scopes and monitoring in ffmpeg
- Vectorscope: `vectorscope=mode=color3:colorspace=709` (overlay it as in correction-matching-skin.md).
- Waveform: `waveform=mode=column:filter=lowpass:scale=ire` (ran OK).
- Review proxy with scope: `split[a][b];[b]waveform,scale=...[w];[a][w]overlay`. Scopes are for review copies only, never in the master.

## 7. LUT library and hygiene
- Folder: `C:/Claude Code/company/creative/<client>/<project>/luts/` with a luts.md table: id, input space, output space, purpose, author, date, test frames.
- Never download unknown LUT packs into a client project (licence unknown, may include hidden gamut clips); build or buy with a licence note (H).
- Test every LUT on skin, a white, a black and a saturated product shot. Reject LUTs that crush deep skin, clip highlights or tint neutrals.
- Version, do not overwrite: v01, v02. The version in use is in grade-notes.md.

## 8. Plugin and paid options (mention, do not buy)
Free: ffmpeg, Resolve free, Natron (OpenColorIO support, see vfx-compositing tool matrix). Paid (3P, price not verified here, U): Resolve Studio, film emulation plugins (Dehancer, FilmConvert, Dehancer-style tools), Baselight. Any purchase goes to the Manager and the user's yes.
