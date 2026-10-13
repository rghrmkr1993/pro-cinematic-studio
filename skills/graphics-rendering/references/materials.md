# Materials: skin, hair, cloth, glass, liquids

Numbers are typical starting values (estimates from public docs such as Filament, Unreal/Blender manuals, GPU Gems 3 skin chapter, Disney/pixar papers); calibrate visually and with reference photography. For photoreal people (AI or 3D) also load `photoreal-humans`.

## Skin (subsurface scattering, SSS)
Physics: light enters, scatters beneath the surface, exits nearby, softening shading and tinting shadow terminators red. Layers: oily thin specular layer, epidermis (melanin), dermis (haemoglobin).
- Specular: dielectric F0 about 0.028 (IOR 1.4), roughness 0.35 to 0.55 base, two-lobe (0.3 and 0.6 mixed) reads better; plus tight sheen/oil on nose and forehead; Fresnel rim stays low.
- Diffuse/albedo: do not use pure sRGB mid-tones; light skin albedo luminance about 0.35 to 0.6 linear, dark skin about 0.1 to 0.3 (measured ranges vary; check against a reference chart). Keep saturation moderate; add per-region variation (cheeks, nose, ears redder; forehead yellower).
- SSS: red scatters farthest (mean free path roughly R 3.7 mm, G 1.4 mm, B 0.9 mm for light skin in Jimenez-style profile values, estimate), so blur diffuse lighting per channel. Real-time methods: pre-integrated skin (lookup by curvature and n.l) for mobile/web; screen-space SSS (separable Gaussian sum, Jimenez 2015) for desktop; Burley normalized diffusion in Unreal/Blender "Random Walk"; texture-space blur (GPU Gems 3 ch.14).
- Thin areas (ears, nostrils) need transmission/backlight term; use thickness map.
- Detail: pore-scale normal (micro), roughness map variance, peach-fuzz (vellus hair) shell or sheen, eyes: cornea clearcoat IOR 1.376, wet meniscus, sclera SSS, parallax iris. Eyes and teeth fail realism first.
- Web budget: pre-integrated SSS or simply wrapped diffuse `(n.l + w)/(1+w)` with `w ~0.3` tinted red, plus baked AO.

## Hair
Models: Kajiya-Kay (two shifted specular highlights along the tangent: primary white, secondary tinted, shift about 0.1 to 0.2 in opposite directions), Marschner (R, TT, TRT lobes, true to physics), Disney/Chiang (Blender Principled Hair, Unreal hair BSDF).
- Cards (textured alpha strips) for real-time, strands for hero close-ups (Unreal Groom, Blender curves). Alpha-to-coverage or dithered alpha plus TAA to avoid sorting.
- Parameters: roughness 0.3 to 0.5, melanin by shade (blonde low, black high), anisotropy strong, shadow self-occlusion needs deep opacity maps or just baked AO per card.
- Frizz, flyaways: separate thin cards; subtle sheen colour shift under rim light. Stay with Kajiya-Kay on web.

## Cloth
Fabrics scatter differently from hard surfaces: soft rim, fuzzy retroreflection, anisotropic highlights for satin.
- Cotton/wool/velvet: use sheen lobe (glTF `KHR_materials_sheen`; Charlie/Ashikhmin NDF, inverted Gaussian-like distribution), sheenColor around base or lighter, sheenRoughness 0.3 to 0.8; base roughness 0.8 to 1.0, F0 low (0.04).
- Satin/silk: anisotropic specular (anisotropy 0.6 to 0.9, along thread direction); polyester shine roughness 0.2 to 0.4.
- Denim/weave: tileable normal + height with micro-fibre detail; fuzz via sheen; use thread-direction map.
- Simulation: position-based dynamics (mass-spring with constraints) for web; Verlet integration, 4 to 10 iterations; GPU compute cloth feasible at 10k to 100k vertices (`webgpu-wgsl` compute patterns). Native: Chaos cloth, Blender cloth baked to morph targets or VAT for web.

## Glass
- Dielectric transmission: IOR 1.5 (window/bottle glass 1.45 to 1.55), F0 = ((ior-1)/(ior+1))^2 = 0.04, crown glass about 1.52, acrylic 1.49, diamond 2.42, water 1.33, ice 1.31.
- glTF: `KHR_materials_transmission` (factor 1), `KHR_materials_ior`, `KHR_materials_volume` (thickness, attenuationColor, attenuationDistance for tinted glass: Beer-Lambert `T = exp(-sigma * d)`), roughness 0 to 0.15 (frosted 0.3 to 0.6).
- Real-time techniques: refract the opaque-scene background copy (render scene to texture, then sample offset by `refract(v, n, 1/ior)` times thickness), chromatic dispersion by three IOR samples (separate R,G,B offsets 1.0 / 1.02 / 1.04 style), planar or probe reflection plus Fresnel mix, back-face render for thickness, ray-traced refraction offline.
- Sorting: render glass after opaque; double-sided glass render back faces first; keep layers to 2 or 3 on mobile.

## Liquids (water, milk, oil, gels, serum)
- Water: IOR 1.333, absorption stronger in red (clear shallow tint toward blue-green), attenuation distance 2 to 10 m for pool-like volume; surface = animated normal maps (two scrolled layers, different scales) or FFT/Gerstner waves; foam from curvature/Jacobian; caustics baked or projected texture; SSR plus sky probe reflection, Fresnel strong at grazing.
- Milk/lotion/creams: strong subsurface (high scattering, low absorption), albedo near white (0.8 to 0.95), low roughness 0.2 to 0.4, thin specular; use volume scattering or SSS-like wrapped diffuse.
- Oils/serums in bottles: transmission 1, IOR 1.46, amber attenuation colour, slight roughness 0.05, add meniscus and bubbles for believability.
- Simulation: SPH or position-based fluids on GPU (compute, 10k to 100k particles on web) with screen-space fluid rendering (depth smoothing, normals from depth, thickness for absorption); heightfield shallow-water for pools; for product hero shots bake a Blender/Houdini simulation to an alembic/VAT or video.
- Drops/droplets: instanced spheres with refraction and a tiny environment fresnel; contact shadow soft.

## Quick sanity checks
Material looks plastic: roughness too uniform or no variation maps. Looks CG-clean: add micro roughness noise, dust, edge wear. Too glossy under studio light: reduce roughness contrast, or soften with larger softboxes. Product colour shifted: switch tonemap to Neutral and check sRGB decode on the albedo.
