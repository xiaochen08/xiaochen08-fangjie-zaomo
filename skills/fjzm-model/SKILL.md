---
name: fjzm-model
description: "Use when creating, rebuilding, comparing, diagnosing, or repairing Minecraft Blockbench geometry for 方界造模/FJZM assets, including silhouette, proportions, groups, base bones, origins, locators, clearances, placeholder UVs, and concept-to-model fidelity."
---

# 方界造模·模型工坊

`$fjzm-model` is the geometry specialist in the FJZM suite. It accepts work only from `$fjzm` through ContractFlow v1. `$fjzm` remains the sole approval, identity, pipeline-state, integration, and release owner. This skill never sends work directly to `$fjzm-texture` or `$fjzm-animation`.

## Hard gate

Read [model-handoff.md](references/model-handoff.md), [geometry-blueprint.md](references/geometry-blueprint.md), [fidelity-comparison.md](references/fidelity-comparison.md), and [auto-repair.md](references/auto-repair.md) before production.

Require `model-handoff.json`, then run:

```powershell
python -X utf8 scripts/validate_model_handoff.py model-handoff.json --workspace <approved-asset-folder>
```

Stop on any error. Lock `project_id`, `asset_id`, `asset_version`, approval hash, reference hashes, blueprint hash, output version, and the declared single-writer surface. Never infer the target from the active Blockbench tab, newest file, filename similarity, or visual similarity.

## Owned surface

This skill may create or revise only approved geometry, clean groups, the base bone hierarchy, stable bone names, origins, locators/interfaces, clearance envelopes, and placeholder UV layout. Placeholder UV exists only to keep geometry faces addressable; it is not final texture work.

Do not paint a final texture, author animation keyframes, bind particles/audio/gameplay logic, change approved identity, or claim runtime compatibility. Keep source artifacts read-only and write every attempt to a new versioned path.

## Production workflow

1. Validate the ContractFlow handoff and open only its hashed inputs.
2. Convert the approved concept into a measurable geometry blueprint: dimensions, silhouettes, named anchors, part count, symmetry, rotations, pivots, locators, moving clearances, groups, and explicit exclusions.
3. Build the smallest complete graybox that contains every approved part and no invented part. Match silhouette and proportions before adding micro-detail.
4. Create the base rig interface without animation keyframes. Keep moving assemblies in independent groups and put origins at the declared mechanical or anatomical centers.
5. Reopen the saved `.bbmodel` in actual Blockbench. Capture one summary board plus eight separate high-resolution views and a side-by-side/overlay comparison according to [fidelity-comparison.md](references/fidelity-comparison.md).
6. If a technical, reversible defect fails the gate, use the bounded repair policy. Never repair design ambiguity, approval ambiguity, identity/hash mismatch, or the wrong asset automatically.
7. Freeze `geometry_signature` and `rig_signature`, write `reference-fidelity-report.json`, then write `model-result.json`.
8. Run:

```powershell
python -X utf8 scripts/validate_model_result.py model-result.json --workspace <approved-asset-folder>
```

9. On pass, return `model-result.json` to `$fjzm`. Do not start texture or animation work here.

## Required outputs

- Versioned `.bbmodel`; source and earlier attempts remain untouched
- `geometry-blueprint.json`
- `reference-fidelity-report.json`
- `model-result.json`
- Actual Blockbench screenshots and the 50% overlay bound to model/reference hashes

Passing the geometry checkpoint means the approved shape is reproducible in Blockbench. It does not prove texture quality, animation quality, shader behavior, collision, gameplay logic, or Minecraft runtime compatibility.
