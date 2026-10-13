# Animation mechanics

## Keyframe vs procedural vs physics
| Type | Source of motion | Strengths | Weaknesses | Use |
|---|---|---|---|---|
| Keyframe | authored values at times, interpolated | exact art direction, deterministic, tiny data | rigid, repeats, labour intensive | UI transitions, logo reveals, cinematics |
| Procedural | math/noise/state evaluated per frame | infinite variation, tiny assets, parametric, GPU-friendly | hard to art-direct, may look mechanical | ambient motion, particles, grass, camera shake, shaders |
| Physics | simulation (springs, rigid, cloth, fluid) | believable response to input, interactive | tuning stability, nondeterminism, cost | drag/throw, cloth, ragdoll, liquids |
| Hybrid | physics-driven layered on keyframe | reactive polish | complexity | spring-follow on authored pose, secondary motion |
| Motion capture / retargeted clips | recorded data | realism | cleanup, licence, size | humanoid characters |
Interpolation: linear (value), cubic Hermite/spline (smooth, tangents), step (discrete states), slerp for quaternions (never lerp Euler angles: gimbal lock). glTF animation supports LINEAR, STEP, CUBICSPLINE for translation, rotation (quaternion), scale, weights.
Procedural primitives: sine layers with phase offsets, noise (Perlin/simplex, 1 to 3 octaves) for organic drift, hashes for per-instance variation, easing of time (`smoothstep`), spring followers, wave functions with `time * speed - distance * frequency` for ripples.
Determinism for video/testing: drive everything from `t` (seek), seeded PRNG, fixed step simulation (see `motion-reel`).

## Skeletal animation
Mesh vertices bound to bone (joint) hierarchy; linear blend skinning: `v' = sum_i w_i * (M_i * B_i^-1) * v` with up to 4 joints per vertex (glTF JOINTS_0/WEIGHTS_0), where `B_i^-1` is inverse bind matrix. Artifacts: candy-wrapper twist and volume loss at joints; fix with dual quaternion skinning, corrective blend shapes, twist/helper bones.
- Data flow: clip (tracks of TRS per joint) sampled at time t, blended, converted to world matrices down the hierarchy, uploaded as bone matrices (uniform/storage/texture); GPU skinning in the vertex stage. See GPU-driven animation in `webgpu-wgsl/references/recipes-basic.md`.
- Blending: crossfade between clips (0.1 to 0.3 s) with slerp per joint; blend trees by parameters (speed, direction); additive layers (breathing, lean) subtract reference pose; masks per body part (upper body aiming while legs run); state machines for transitions (idle, walk, run, jump) with exit times.
- Root motion: extract translation from root bone to drive character movement and avoid foot sliding; otherwise match speed to stride length.
- Retargeting: map bone names/humanoid rig (Mixamo-like, Unity Humanoid, UE Mannequin), compensate proportions and rest pose differences.
- Web: three.js `AnimationMixer`/`AnimationAction` (`crossFadeTo`, `setEffectiveWeight`), Babylon animation groups, glTF clips; optimise by baking, limiting influences to 4, removing static tracks, quantising keys (`gltf-transform` animation compression).

## Inverse kinematics (IK)
Forward kinematics: rotations down the chain give end position. IK solves joint rotations from a target end position.
- Two-bone analytic (law of cosines): arms and legs; `cos(theta) = (a^2 + b^2 - d^2)/(2ab)`; add pole vector to control elbow/knee direction. Cheap and stable.
- CCD (Cyclic Coordinate Descent): iterate from tip to root rotating each joint toward the target; simple, arbitrary chain length, can look twitchy; 10 to 20 iterations.
- FABRIK (Forward And Backward Reaching): move joints along lines; fast converging, natural-looking for tentacles, spines, ropes; add angle limits as constraints.
- Jacobian/damped least squares: general but costlier.
- Uses: foot placement on terrain (raycast, adjust pelvis height), hand on object (grab), look-at (head/eyes with clamp and speed limit), aim. Blend IK weight with animation (0 to 1) to avoid pops. Apply after FK animation and before skinning.
- Libraries: three.js `CCDIKSolver`, Babylon `BoneIKController`, FABRIK libs, Godot `SkeletonIK3D`/Skeleton modifiers, Unreal Control Rig and Full Body IK.

## Blend shapes and morph targets
Per-vertex delta sets: `v' = v + sum_k w_k * delta_k` (weights 0 to 1, can exceed for exaggeration). Best for facial expression, corrective shapes, product transformations.
- Faces: ARKit 52 blendshapes (jawOpen, eyeBlinkLeft, mouthSmile...) / FACS action units; visemes for lip-sync (about 15 viseme set, driven by phoneme timing or audio analysis); combine with eye saccades and blink every 3 to 6 s for life.
- glTF: `primitive.targets` + `mesh.weights` + `weights` animation channel; names in `extras.targetNames`. GPU limit: three.js packs morph targets into a texture, so hundreds are possible, but memory grows with vertices x targets (52 targets x 20k verts x 12 B = 12 MB per attribute, estimate). Normals and tangents deltas double that.
- Sparse targets (store only changed verts) and `KHR_mesh_quantization` reduce size.
- Use morph targets to avoid skeletons for simple deformations (product open/close, logo morph, waves).

## Camera motion grammar (film language for 3D, product, and UI cameras)
| Move | Effect | Notes |
|---|---|---|
| Static | calm, authority | start and end holds (0.3 to 0.5 s) |
| Pan/tilt | reveals, follows | pivot at camera; ease in/out |
| Dolly in/out | emotional push-in (intimacy, focus) or pull-out (reveal context) | changes perspective, unlike zoom |
| Truck/pedestal | parallax, lateral reveals | strong depth cue |
| Orbit/arc | hero product showcase | 360 in 6 to 10 s, ease, keep subject centred, slight elevation variation |
| Crane/jib | grand reveal, establishing | combined vertical and arc |
| Zoom (FOV change) | flattening, surveillance feel | use rarely; dolly-zoom for unease |
| Handheld | realism, urgency | add noise 0.2 to 1 Hz low amplitude plus 4 to 8 Hz tiny jitter |
| Whip/rack focus | transitions, attention shift | pair with motion blur or DoF |
Rules: 180-degree rule for dialogue; match movement direction across cuts; slow moves feel premium (product hero 4 to 8 s per move); one move per shot; ease start and stop; avoid motion during key text reading; keep horizon level unless intentional; lens: 35 to 50 mm equivalent natural, 85 to 135 mm portrait/product compression, 14 to 24 mm wide distortion (use sparingly).
Implementation: camera rig as parent pivot (orbit) + child offset; spline path (Catmull-Rom/centripetal) with arc-length parametrisation for constant speed; damped follow (SmoothDamp) for gameplay; scroll-driven camera path (progress 0 to 1 maps to spline position), clamp progress, smooth with inertia; respect reduced motion by cutting between fixed viewpoints instead of flying.
Depth of field, bloom, vignette and subtle film grain add cinematic feel; keep intensity low and consistent.
