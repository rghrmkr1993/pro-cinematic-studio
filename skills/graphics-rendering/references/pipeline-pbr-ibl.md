# Pipeline, PBR, IBL

## Real-time pipeline (Real-Time Rendering, Learn OpenGL, paraphrased)
1. Application: scene update, culling (frustum, occlusion), LOD, batching, animation, physics.
2. Geometry/vertex: model-view-projection transform, skinning, morphing, normal/tangent transform.
3. Rasterisation: triangle setup, coverage, interpolation of attributes (perspective-correct), early depth/stencil test.
4. Fragment/pixel: texture sampling, lighting, alpha test, writes colour (+ depth, MRT).
5. Output merge: depth test, blending, MSAA resolve. Then post-process (bloom, tonemap, AA, DoF, motion blur).
Forward: shade during geometry pass; cheap with few lights, MSAA friendly, default on the web. Forward+ (tiled/clustered light lists): many lights. Deferred: G-buffer (albedo, normal, roughness/metal, depth) then lighting pass; many lights and screen-space effects, heavy bandwidth, no MSAA, awkward transparency. Visibility buffer: modern variant storing triangle ids.
Transparency: sort back-to-front, or weighted blended OIT, or alpha-to-coverage for foliage; premultiplied alpha avoids fringes.
Coordinate spaces: object -> world -> view -> clip -> NDC -> screen. Normals use the inverse transpose of the model matrix; non-uniform scale breaks plain matrices.

## PBR metal/roughness (Filament design doc, Disney principled BRDF lineage)
Inputs per pixel: baseColor (sRGB), metallic (0 or 1, intermediate only for blends and dirt), roughness (perceptual, use `alpha = roughness^2`), normal, occlusion, emissive.
Derived: `diffuseColor = baseColor * (1 - metallic)`; `F0 = mix(0.04, baseColor, metallic)` (dielectrics around 0.02 to 0.05; gemstones/diamond up to 0.17).
Specular BRDF `f_s = D * V * F`:
- D (normal distribution): GGX/Trowbridge-Reitz, `D = a^2 / (pi * ((n.h)^2 * (a^2 - 1) + 1)^2)`.
- V (visibility, geometry over denominator): Smith height-correlated GGX (cheaper approximation exists).
- F (Fresnel): Schlick, `F = F0 + (1 - F0) * (1 - v.h)^5`.
Diffuse: Lambert `baseColor / pi` (Burley/Disney adds retroreflection at grazing, costs more).
Clamp roughness to 0.045 or so for punctual lights to avoid vanishing highlights (Filament rule of thumb).
Energy conservation: the light reflected (specular + diffuse) must not exceed incoming. Metal/rough ensures this by scaling diffuse by `(1 - F)` (or `1 - metallic` approximation) and normalising D. Multiple-scattering compensation (Kulla-Conty) restores energy lost on rough metals; cheap fit from the split-sum LUT.
Units: point light intensity in candela, exposure via EV; physical camera (aperture, shutter, ISO) simplifies consistent lighting across scenes. Sun about 100,000 lux, overcast sky 1,000 to 20,000 lux, indoor 100 to 500 lux (typical reference values).
Parameters cheat sheet (typical values, estimates): plastic F0 0.04 rough 0.3 to 0.6; brushed aluminium base (0.91,0.92,0.92) metal 1 rough 0.35; gold (1.0,0.78,0.34) metal 1 rough 0.2; rubber rough 0.8; polished wood rough 0.4 plus clearcoat; skin see `materials.md`.

## Extensions (glTF KHR_materials_*)
clearcoat (car paint, lacquer), sheen (cloth), transmission + volume + ior (glass, liquids), iridescence, anisotropy (brushed metal, hair-like highlight), specular, emissive_strength, dispersion. Prefer these over custom shaders so the asset travels across engines. Matrix: `assets-gltf.md`.

## Image-based lighting (IBL)
Environment map = light from all directions. Split-sum approximation (Epic, Karis 2013):
- Diffuse irradiance: low-order spherical harmonics (L2, 9 coefficients) or a small convolved cubemap (32x32).
- Specular: prefiltered radiance cubemap, one mip per roughness level (GGX importance sampled), sampled with the reflection vector and `lod = roughness * maxMip`.
- BRDF integration LUT (2D, n.v by roughness, RG16F), generated once or downloaded; gives the scale and bias on F0.
Workflow: HDRI (equirectangular .hdr/.exr, 1k to 2k for web) -> PMREM/prefilter at load (three.js `PMREMGenerator`, Babylon `HDRCubeTexture`, Filament `cmgen`) -> ship KTX2 cubemap (ASTC/BC6H) for speed.
Rules: match exposure between HDRI and punctual lights; use the HDRI also as the visible background only if it fits the art direction (blur or replace otherwise); parallax-corrected or box-projected probes for interiors; reflection probes capture static scene, update lazily; screen-space reflections (SSR) fill dynamic detail with fallback to probes.
Studio-look product shots: neutral grey HDRI plus softbox lights as emissive quads (area lights, LTC technique) to get shaped specular highlights.

## Texture and mip rules
Mipmaps always for minification; anisotropic filtering 4x to 8x for floors; atlas or array textures to cut bind changes; normal map blue-dominant, DirectX versus OpenGL green channel; AO baked into R of ORM pack (R occlusion, G roughness, B metal) per glTF convention.
