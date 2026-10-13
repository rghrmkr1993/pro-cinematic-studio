# Image direction: realistic advertising assets

Adapted from the user's CINEIMAGE v2.7 production principles. This reference controls image content, physical logic, composition, references, lighting and edits. The campaign brief controls the message and intended audience. Good photography must make the product, evidence and next action easier to understand.

## Routing and dependencies

All generated visual assets go through the connected Higgsfield integration. Generate characters with **Seedream 5** and product/prop sheets with **Nano Banana Pro**. Resolve location generation through the model policy in the main skill and Higgsfield reference; this file does not assign a different location model. All generated video uses **Seedance 2.5**. Verify actual provider model identifiers and capabilities before submission; a display name is not an API identifier.

The default dependency order is needed location plates, character references, product/prop sheets, then final stills or video. Approve each asset that later assets depend on. Skip an unnecessary asset rather than adding scenery or characters to justify the workflow. A simple approved text-to-video route may omit reference generation as described in the video workflow.

Do not silently switch models, ignore a requested model or send a job outside Higgsfield. An unavailable locked model blocks only the affected generation stage; retain usable preparation and report the exact missing capability.

## Start with the commercial job

Before writing the prompt, record only what changes the result:

- Asset purpose: location plate, character reference, product sheet, final static, video start frame or repair.
- One primary message, the visible evidence supporting it and the required product identity.
- Requested placement and aspect ratio; select dimensions supported by the actual provider. No universal cinematic crop.
- Hard constraints from the brief; flexible visual choices; unsupported product details that must stay absent.
- Supplied reference IDs and the role each is allowed to provide.
- Text content and whether it belongs on a physical carrier or a separate graphic layer.
- Scene occupancy, planned action and the space the action needs.

Choose Generate, Reference Match, Edit, Cleanup or Diagnose. Make conservative layout choices without a long intake. Ask only when an unknown would materially change the product, claim, identity or production route.

## Hierarchy and spatial map

For a subject-led scene, state the subject's form, position, apparent scale, orientation, visibility and relationship to its setting. A small accessory must not displace the product as the visual subject. For a location plate, the setting itself is the subject; do not invent a hero product.

For environments and multi-object scenes, prepare a compact left/center/right map with relevant foreground, midground and background positions. For every important object, give one location, approximate scale, orientation, what supports it, what it may overlap and what must remain visible. Mark intentional empty areas as action space, circulation, a sightline or copy space; do not fill them with decorative objects.

Example planning map:

| Zone | Foreground | Midground | Background |
| --- | --- | --- | --- |
| Left | Clear edge of a counter | Small work surface | Window supplying daylight |
| Center | Unobstructed action area | Product at readable scale | Quiet wall |
| Right | No foreground obstruction | One supporting prop | Door with a usable access route |

This is a layout technique, not a reusable set. Describe the final scene in the same spatial order. A close isolated product, a plain-background portrait or a repair preserving an existing layout does not need a full environment map.

Check gravity, contact shadows, scale, support, coherent boundaries, plausible reflections and access to doors, drawers and work areas. Exact counts are useful when they prevent duplication or preserve a demonstration; do not count every incidental object.

## Occupancy and character realism

Location reference plates are empty by default. Include “No people” and extend it to windows, mirrors, screens or printed portraits when those surfaces could introduce accidental occupants. Do not infer an employee, driver or passerby merely from the type of location.

This empty-plate rule does not prohibit people in final ads. A storyboard may deliberately add an approved character. Generate that character in Seedream 5 and bind the approved identity reference to each dependent shot. Describe observable appearance, wardrobe, pose, framing and expression without naming a real person as a likeness shortcut. Use properly authorized real-person references only within their permitted scope.

Aim for varied natural skin texture, coherent facial features, plausible hair boundaries, believable clothing folds and anatomically correct visible hands. Do not force airbrushed skin, hyper-defined pores, symmetrical smiles, beauty lighting or a fashion pose onto an ordinary use case. Match gaze and body position to the actual task. Do not mistake a realistic fictional presenter for evidence of a real customer's experience.

## Product and prop identity

Use Nano Banana Pro for the product/prop sheet. Extract invariants from the approved source: silhouette, dimensions where verified, seams, closures, handle or attachment count, hardware geometry, color and visible authorized marks. Show only views needed for the planned shots. Do not generate unseen internals or the reverse side as though they had been verified from one front photograph.

A generated sheet is a consistency aid, not factual product evidence. Generated macro texture cannot establish material grade; a generated loadout cannot establish capacity; a generated demonstration cannot establish performance. Preserve uncertainty in the asset notes and obtain actual product evidence when the ad depends on that claim.

For each important prop, specify category, construction, visible material, condition, placement and function. Use a clean new condition for a new product unless the brief calls for a used example. Restrained natural variation belongs in the environment; random scratches and stains are not a universal realism recipe. Reject geometry changes, invented pockets, added labels, floating straps and inconsistent product color.

## Camera and readable composition

State viewpoint, shot scale, viewing direction and useful camera height. Choose perspective to reveal the relevant action or feature. Use focal length only when it improves control; use “full-frame equivalent” when that is what is intended. Never attach a universal horizontal field of view to a focal length without specifying sensor width and the actual orientation/crop. Portrait outputs and crops change horizontal coverage. If the geometry is unspecified, omit numerical FOV rather than invent precision.

Prefer naturally proportioned objects and readable verticals when distortion would misrepresent the product. Avoid automatic ultra-wide rooms, extreme shallow focus, anamorphic flare or artificial blur. A photographed note must be readable; a proof detail must remain in focus. Cropping, visual hierarchy and safe areas follow [typography and UI/UX](typography-uiux.md).

Use the minimum prompt length that controls the frame. Do not enforce a word-count quota. Replace “premium,” “stunning,” “8K” or “cinematic” filler with visible decisions: the light source, the product's size in frame, separated outlines, a quiet text area or a material's real surface.

## Motivated light, clean middle tones and local color

Specify source position and type, broad quality, where it directs attention and how it falls off. For example: window light from frame left crosses the work surface, while recesses beneath the counter remain darker. Do not replace a plausible lighting decision with exposure-stop lists, render jargon or fabricated optical precision.

Preserve a broad readable middle register. Gray stone stays gray; off-white paint stays off-white; brown material retains its actual color. Adjacent surfaces must separate through luminance, depth and reflectance. Allow real shadows and selective highlights without crushing the evidence or bleaching the product.

Keep source color spatially plausible. A warm task lamp affects its nearby surface and reflections. Cool daylight is associated with the window and its spill. Do not wash the whole image orange, teal, cyan or magenta as a default mood treatment. A deliberately expressive palette may be used when the brief requires it, while maintaining material and product identity.

Choose a coherent visual treatment that serves the ad: an observed everyday photograph, a clean product study or a naturally photographed note. No mandatory prestige-drama look, film grain, haze, luxury interior or desaturated palette. Describe stylistic properties directly rather than citing artists, directors, studios, brands or franchises.

## Exact copy and physical text

Keep a copy manifest containing exact wording, language, capitalization, line breaks, price, CTA, destination and any necessary qualifier. Separate three layers:

1. Photography: product, people, location, light and surfaces.
2. Physical text: labels, packaging or a note belonging in the scene.
3. Graphic overlays: callouts, captions, headline, price and CTA.

When physical text is required, identify its carrier and specify exact copy; do not ask for decorative pseudo-writing. Keep incidental surfaces unbranded where appropriate without an indiscriminate “erase all text” instruction that removes authorized product details.

For a CTA or translation revision, change the text layer and only its necessary layout dependencies. Preserve approved photography, product geometry, identity, crop, pose, light and reference associations. Use the authorized exact text-edit/compositing path in the Higgsfield workflow; do not regenerate the entire photograph solely to fix a misspelled CTA. Never silently substitute a generative image tool. If precise text editing is unavailable, deliver the approved plate plus a clearly identified copy/layout specification and report the unfinished assembly.

Generated physical writing still needs exact spelling and legibility checks. A handwritten note is an ad format, not permission to invent a customer quotation, owner statement or third-party endorsement. Abstract useful format principles without copying a competitor's words, logo, phone number, distinctive design or interface identity. See [typography and UI/UX](typography-uiux.md) for type selection and final-size checks.

## Reference roles and protected edits

For each reference use a concrete instruction: “Reference A supplies product identity only; Reference B supplies room layout only. Preserve A's geometry and color. Do not transfer B's objects, writing or people.” Authorized references define specific roles; they do not grant permission to reproduce unrelated protected material.

Priority is explicit user constraints, base-image identity and protected structure, assigned product or character identity, composition, location, then lighting/palette/mood. A mood reference cannot redesign the product.

For edits list the requested delta and locks. Preserve everything not directly or necessarily changed: subject count, identity, geometry, placement, crop, perspective, pose, protected text and regions. Shadows and reflections may change only when required by the edit's physical consequences. Cleanup repairs a local defect; it is not permission to restage the scene. Record whether the actual repair used generation or deterministic editing rather than calling every cleanup “non-generative.”

## Prompt compilation and acceptance

Compile plain English production prose in this order when relevant: asset purpose and subject; immutable identity; mapped scene; camera; specific objects/materials; action or pose; motivated light; local color; occupancy; exact text; a short list of likely failure constraints. Keep workflow notes separate from the actual generation prompt. Read [the worked examples](clean-midtones-examples.md) when applying mixed light, environment maps or physical notes.

Before submission, verify the required model, references, output size, exact copy and dependencies. After generation, the independent slop-control reviewer inspects the actual asset at both full resolution and intended display size:

- Product and character match the approved references; no invented feature or unsupported proof.
- Scene position, contact, reflection, anatomy and object count are coherent.
- Product/evidence is visibly primary; the frame communicates the concept without explanation.
- Materials have plausible texture, reflectance and local color; no waxy faces, liquid-looking hard edges or arbitrary color wash.
- Every letter, number and CTA is correct, readable and connected to the real destination.
- Composition survives the intended crop and overlay treatment.
- Styling is specific to the buyer situation, with no unrelated generic “luxury” filler or borrowed identity.

Return pass, revise or unverified with the visible defect, its location and the smallest repair. Mark execution blocked separately when a required capability or asset is absent. Passing aesthetics does not prove conversion. Preserve good assets and use the workflow's bounded repair budget.
