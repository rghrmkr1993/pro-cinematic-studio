# Lighting setups (photography and film grammar applied to 3D and AI renders)

Positions are given as azimuth from camera axis (0 = behind camera, 90 = side) and elevation above subject eye line. Ratios are key:fill. Starting points; adjust by eye. Intensity in stops (each stop = 2x).

## Three-point lighting
| Light | Position | Quality | Role |
|---|---|---|---|
| Key | 30 to 45 deg to one side, 30 to 45 deg up | medium-soft, largest source | main shape and shadow direction, sets exposure |
| Fill | opposite side, near camera height, 0 to 20 deg up | large, very soft | lifts shadows; ratio sets mood |
| Back/rim | behind subject, 120 to 160 deg, 45 to 60 deg up | small, harder | separates subject from background, hair/edge glint |
Ratios (key:fill): 2:1 (1 stop) bright commercial, 3:1 (1.6 stops) natural portrait, 4:1 (2 stops) dramatic, 8:1 and above low-key/noir. Rim about equal to key or 1 stop above for strong separation. Optional fourth: background light to pull the backdrop from black; kicker; hair light.
In real-time: key = shadow-casting directional/spot (or area light), fill = hemisphere/IBL (no shadows), rim = cheap spot without shadows. Add a bounce card via emissive plane for cheap fill on web.

## Named looks
- Rembrandt: key 45 deg side, 45 deg up, a triangle of light on the shadow cheek; fill low (4:1 to 6:1). Moody portraits.
- Butterfly/Paramount: key frontal and high, shadow under nose and chin; add reflector below (clamshell) for beauty and skincare close-ups.
- Loop: key 30 to 45 deg, small nose shadow loop toward cheek; flattering default.
- Split: key at 90 deg, half face dark; dramatic only.
- Broad vs short: broad lights the side of face toward camera (wider look), short lights the far side (slimmer, more depth). Short is default.
- Clamshell: large soft key above plus reflector/fill below, minimal shadows; beauty and cosmetics.
- Flat/high-key: huge frontal soft light plus lit white background, ratios 2:1, upbeat and clean. Background overexposed 1 to 2 stops above subject.
- Low-key: single small source, black surroundings, deep shadows; drama.

## Studio product setup (hero shot)
1. Seamless sweep (cyc) or white infinity backdrop; invisible floor reflection (planar or SSR fade) optional.
2. Large overhead softbox (top light) for gradient on lid/top; two strip softboxes left and right (80 to 100 deg) to draw clean edge highlights on bottles and metal; a fill card in front; one small rim spot for glass/liquid separation.
3. Glass and shiny items: light the background and use "negative fill" black flags to define edges; for liquids, backlight through a diffusion panel.
4. Matte packaging: broad soft light from 45 deg, texture raking light at 75 deg to reveal paper/emboss.
5. In 3D: use area lights (rect, LTC), or emissive planes in an HDRI studio; keep exposure fixed, neutral tonemap (Khronos PBR Neutral) so brand colours stay true; add contact shadow and subtle AO.
6. Check specular highlight shape: rectangular softbox shapes read "studio", round blobs read "game".

## Colour and mood
Colour temperature: tungsten about 3200 K, daylight 5600 K, overcast 6500 to 7000 K, golden hour 3500 to 4500 K, blue hour 9000 K+. Mixed temperature (warm key, cool fill/rim) gives depth (complementary orange/teal grammar, use with restraint). Lighting contrast and saturation should follow brand and story; skin colour must stay believable.
Practical lights and volumetrics: light shafts (volumetric fog) and soft haze add depth; keep density low. Gobo/cookie textures for window light or foliage shadow.

## Outdoor/daylight
Sun plus sky: sun elevation 25 to 45 deg for pleasing portrait; overcast sky = giant softbox; golden hour low sun 5 to 15 deg for rim and long shadows; sky as IBL provides fill automatically. Use a procedural sky (Preetham, Hosek-Wilkie, Bruneton) tied to sun direction.

## Web-friendly rig (default)
IBL studio HDRI 0.8x + 1 key directional (shadow 1024 to 2048, PCF soft) + 1 rim spot without shadow + contact shadow plane. Total shadow casters: 1 on mobile. Bake the rest. Evaluate on a grey ball, a chrome ball and the real subject.
