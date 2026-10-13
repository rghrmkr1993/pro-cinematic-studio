# Correction, shot matching, skin tone
Labels: (V) vendor-official, (3P) third-party or colourist commentary, (H) house rule, (E) estimate, (U) unverified. Researched 2026-10-14 (Aaron Williams, Larry Jordan, Daniel Grindrod and similar colourist teaching; Mixing Light and Lowepost style workflow). Numbers marked (H) are starting points, not standards.

## 1. Primary correction order (per shot)
1. Look at the scopes before the picture: waveform (levels), vectorscope (hue and saturation), histogram, parade (RGB balance).
2. Exposure and contrast: set black and white points so shadows sit near the black floor without clipping and highlights have headroom; mid-gray (face or neutral wall) where the brief wants it. Do not crush; 8-bit AI clips band fast.
3. White balance: neutral objects (white wall, grey card, product white) on the parade should be level; skin is not a neutral reference.
4. Saturation: global saturation last; use a hue-vs-sat curve for individual colour rather than a global push.
5. Only then creative balance (warm highlights, cool shadows) via lift, gamma, gain or a curve, mild.
Tools in any grader: lift (shadows), gamma (mids), gain (highlights), offset, curves, hue vs hue, hue vs sat, lum vs sat.

## 2. Secondary correction (isolate and refine)
- Qualifier (select by hue, saturation, luma) or a power window or mask, feathered; track if there is motion (Resolve free has window tracking; Magic Mask is Studio, 3P).
- Typical jobs: sky colour, skin evenness (not smoothing), product colour accuracy, brightening a face a half stop with a soft window (never to change tone, only to separate), background desaturation, vignette.
- Keep every secondary invisible at 100 percent zoom and in motion. A flicker on an AI clip usually means the qualifier is picking up model noise; widen the softness or switch to a window.
- Do not use secondaries to hide an AI defect (melting hand, bad text): send it to vfx-compositing.

## 3. Matching clips from different AI models
Why they differ: each model bakes its own contrast curve, saturation, white balance bias, grain character and sharpening (3P observation, H). Seedance, Kling, Veo and Cinema Studio outputs rarely match raw.
Method:
1. Pick the hero frame (the best frame of the key scene) and save it as a still with scopes.
2. Per model, build one corrective LUT or node group aimed at the hero frame: levels, white balance, saturation, then export as a LUT (luts-and-ffmpeg.md). Document it by model name.
3. Within a scene, A/B shots against the previous shot with split-screen or a still reference; match skin first, then neutrals, then shadows, then highlights.
4. Match sequence to sequence only after each scene is internally consistent.
5. Add the unifying look LUT on top of all of them, then the same grain recipe on every clip.
6. Re-check cuts where the model changes: skin patch values (section 4) must agree within tolerance across the cut.
Other drift: flicker (temporal drift in exposure) can be reduced with a slow timeline-level fix or a small deflicker; if heavy, regenerate (vfx-compositing). Sharpening halos from a model: reduce with a soft blur on edges before grain, or a gentle degrain-regrain pass.

## 4. Skin tone line and vectorscope
What the scopes show (3P: Aaron Williams, Larry Jordan, Pixel Valley Studio, Daniel Grindrod):
- On the vectorscope, skin of every complexion clusters along one line between red and yellow, near the 10 to 11 o'clock direction. Hue is similar across people; what changes is luminance and saturation (3P). The explanation that blood sets the hue is a teaching simplification; melanin and other pigments also matter, and small hue spread is normal (3P).
- The line is a guide: skin should sit on or close to it, not exactly on it. Skin that falls clearly to the green side looks sick; clearly to the red side looks sunburned or magenta (3P).
- The vectorscope shows hue and chroma only. Use the waveform for brightness.
- Darker skin: same hue region, typically more saturation farther along the line, lower luma. Do not pull saturation toward the centre or raise luma to compensate for a dark scene (H).
Measuring in ffmpeg (verified 9.0.1): crop a skin patch and compare before and after:
```
ffmpeg -i in.mp4 -vf "crop=100:100:X:Y,signalstats,metadata=print:file=-" -frames:v 1 -f null - | grep -E "YAVG|SATAVG|HUEMED"
```
Fields: YAVG luma 0 to 255 (limited range 16 to 235), SATAVG, HUEMED hue in degrees. Draw the vectorscope into the render for review: `split[a][b];[b]vectorscope=mode=color3:colorspace=709,scale=256:256[v];[a][v]overlay=W-w:H-h`.

## 5. Correct Indian and South Asian skin tones, no lightening
Hard rule: the grade never lightens or evens out skin tone, never "fairness-corrects", never shifts toward a lighter or redder palette to look premium. The tone comes from the asset lock and the brief (asian-human-reference regions-and-appearance.md gives tone ranges and undertones per region).
Practice:
1. Take the skin patch from the approved reference still (cheek, forehead, neck, in the same light) and record YAVG, SATAVG, HUEMED. This is the target.
2. Grade shots so the same face patch stays within tolerance of the target (H starting point: luma within about 5 percent of the target, hue within about 3 degrees, saturation within about 10 percent). Larger shifts need a documented reason in grade-notes.md (a night scene, a sunset), and the shift must be light-driven, not a tone change.
3. Typical face-highlight waveform zones (H starting points; (3P) Larry Jordan gives roughly 15 to 35 percent for darker complexions and a higher zone for lighter ones): deep brown skin about 25 to 45 percent IRE on the main face plane, medium brown about 35 to 55, light brown or wheatish about 45 to 65. Use these only to spot a face sitting far outside its zone; the reference patch decides.
4. Undertones: South Asian skin ranges across warm golden, olive, neutral and cool brown undertones. Keep the undertone of the reference. Avoid a global teal and orange look; it pushes brown skin to orange or muddy. If a look needs warmth, warm the highlights lightly and keep skin hue on the line.
5. Mixed groups: check each face; a global correction tuned to the lightest face crushes the deepest, and vice versa. Use a soft window per face when needed, with the same moves.
6. Sheen and highlights: let natural specular stay (it carries texture); do not smooth with qualifiers; no beauty blur (photoreal-humans).
7. Skin and brand clients (skincare, cosmetics): never grade to imply results (a glow, evened tone). Show true colour.
8. After every grade, save before and after stills with the skin patch numbers in the QC table. A face that moved outside tolerance is a critical fail until fixed.

## 6. Common defects and fixes (grade side)
| Defect | Likely cause | Fix |
|---|---|---|
| Magenta or green skin | White balance push | Parade-level neutrals, then tint a few points; re-check hue vs line |
| Orange mask on brown skin | Teal and orange look too strong | Reduce look strength, protect skin with a skin qualifier |
| Grey, muddy face | Contrast crushed, saturation pulled | Restore saturation along the line, lift mids gently |
| Plastic sheen | Model smoothing | Add grain, reduce sharpening, no extra softening |
| Banding | 8-bit, strong curves | 10-bit intermediate, grain before encode |
| Flicker | Exposure drift in clip | Slow gain keyframes or deflicker, else regenerate |
| Cut pops between models | Model bias differs | Per-model corrective LUT, re-match skin patch |
