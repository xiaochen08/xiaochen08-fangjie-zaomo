# Blockbench-faithful concept prompt

Use this only after the consultation brief is complete. Its purpose is design approval with high model fidelity, not cinematic concept art.

## Compile before prompting

Create a `concept-to-build manifest` for each variant containing:

- target edition, Blockbench format, runtime, overall size in blocks, and cube budget;
- silhouette proportions and a named inventory of every visible cuboid group;
- permitted cube rotations, moving groups, joints, pivots, and clearance envelopes;
- material palette, atlas dimensions, texels per Blockbench unit, neutral albedo/base-texture rules, emissive regions, transparency/render layer, and texture tier;
- shader compatibility tier, no-shader fallback, named runtime targets, PBR standard/version when approved, and the applicable runtime test rows;
- runtime-only effects such as particles, bloom, projectiles, trails, shaders, and sounds.

Every visible feature in the image must map one-to-one to this manifest. Use geometry supported by the selected target format. If the target is unknown, restrict the design to cuboids/boxes and ordinary cube rotations.

Do not include an unapproved related asset in a manifest or image. For an approved asset set, name the primary asset and every approved companion in the manifest, preserve their relative scale, and keep separate asset identities. If staged damage or full destruction is approved, also compile a damage-state manifest and request a separate aligned sheet showing the approved intact, damaged, critical, and destroyed silhouettes without cinematic debris or runtime effects.

Every A/B/C package must visibly demonstrate all approved requirements. Each package contains a primary model sheet, a related-asset sheet when companions are approved, and a damage/destruction keyframe sheet when staged damage or full destruction is approved. Generate required sheets separately when a combined sheet would reduce readable detail. Do not replace a required visual sheet with text. An explicitly approved single, non-destructible asset needs only the primary sheet.

## Master image prompt

Replace every brace field; never send unresolved placeholders to imagegen.

```text
Create one Blockbench viewport-style model sheet for Minecraft model variant {VARIANT}. This is a production-feasibility preview of the exact model to be built, not an illustration.

SUBJECT AND USE
{SUBJECT}; target: {EDITION_RUNTIME_FORMAT}; overall size: {WIDTH} x {HEIGHT} x {DEPTH} blocks; intended gameplay viewing distance: {DISTANCE}.

APPROVED SCOPE
Approved related assets: {APPROVED_RELATED_ASSETS}.
Damage/destruction requirements: {DAMAGE_DESTRUCTION_REQUIREMENTS}.
Required preview sheets: {REQUIRED_PREVIEW_SHEETS}.
Depict every approved modeled requirement and no declined, deferred, suggested, or unspecified companion.

LOCKED DESIGN
Silhouette and proportions: {PROPORTIONS}.
Visible build manifest: {NAMED_CUBOID_GROUPS_WITH_COUNTS_AND_RELATIVE_PLACEMENT}.
Moving assemblies and resting positions: {MOVING_GROUPS_PIVOTS_AND_CLEARANCES}.
Materials and palette: {MATERIALS_PALETTE}.
Texture: {ATLAS} atlas dimensions, {DENSITY} texels per Blockbench unit, nearest-neighbor pixel texture, {TEXTURE_TIER}; use deliberate pixel clusters, readable material separation, neutral albedo, restrained non-directional edge accents, recess value separation, and controlled wear at that native density. Use no painted-in directional highlights, cast shadows, bloom halos, or environment tint. Shader contract: {SHADER_COMPATIBILITY_TIER_AND_NAMED_TARGETS}; no-shader fallback: {NO_SHADER_FALLBACK}; emissive/PBR/transparency policy: {MATERIAL_MAP_AND_RENDER_LAYER_POLICY}.

STRICT BLOCKBENCH GEOMETRY
Construct the visible design only from buildable cuboids/boxes and the rotations supported by {FORMAT}. Preserve hard square edges and Minecraft form language. Use no smooth sculpting, organic curves, subdivision surfaces, rounded bevels, cloth simulation, hair strands, or details that would require a high-poly mesh; do not depict any visible feature that is absent from the build manifest. Do not hide impossible geometry behind effects or darkness.

MODEL-SHEET VIEWS
Show front, left side, back, and three-quarter views of the exact same model in one clean sheet. Use orthographic projection for front/side/back and a restrained fixed camera for the three-quarter view. Align every view to the same floor line and scale. Maintain the same proportions and part count across every view; matching armor plates, eyes, joints, weapons, cores, and appendages must occupy consistent positions.

BLOCKBENCH-LIKE PRESENTATION
Use neutral studio lighting, restrained ambient occlusion, crisp hard-surface shading, a plain dark checker or neutral viewport background, and unobstructed full-body framing. Render pixel textures sharply without antialiasing blur. Use no cinematic perspective, no depth of field, no bloom, no particles, no motion blur, no fog, no dramatic rim light, no photorealistic PBR reflections, and no environment scenery. Emissive areas may be flat bright pixel regions without glow spill. All runtime-only effects are excluded from the model sheet and described separately in text; runtime lighting is not proof of compatibility until the exact model is tested in-game.

OUTPUT DISCIPLINE
Generate each variant as a separate image package; generate each required sheet as a separate image using identical design, scale, and lighting. Keep the primary sheet in neutral idle; use aligned readable keyframes on the damage/destruction sheet. Do not embed A/B/C labels or any text, dimensions, arrows, UI, watermark, or logo inside images.
```

## Negative prompt

```text
cinematic concept art, realistic creature, smooth sculpture, rounded organic anatomy, high-poly mesh, bevelled surfaces, curved pipes, cloth, hair, fur strands, painterly texture, PBR metal, ray tracing, glossy reflections, depth of field, bloom, glow halo, particles, smoke, fog, motion blur, dramatic shadows, extreme perspective, cropped parts, hidden rear geometry, inconsistent multi-view design, extra limbs, missing parts, floating details, text, labels, watermark
```

## Audit before showing the user

Inspect each generated image against its manifest. Reject it if views disagree, a visible part has no cuboid mapping, the texture looks smoother than the chosen density, painted-in directional highlights or shadows would create double lighting, effects conceal geometry, or the silhouette cannot be built at the declared scale. Fix the prompt and regenerate the preview before showing it. Present A/B/C as conversation labels outside the images, plus each variant's manifest and known limitations.

Present the generated packages to the user in A, then B, then C order. Under each package, show every required image followed by a requirements-to-image checklist mapping the primary asset, each approved related asset, and each damage/destruction stage to a visible sheet. State excluded runtime-only effects separately; ask the user to select or revise only after all required images are visible.

After selection, freeze the chosen image and manifest together. The build may simplify nothing visible without renewed approval. Generative previews cannot guarantee pixel-identical output; this contract minimizes drift, while actual Blockbench screenshots remain the final visual evidence.
