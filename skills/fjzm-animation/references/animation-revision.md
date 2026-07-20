# Animation revision diagnosis

Diagnose before moving keys. Separate an animation defect from a model-geometry issue and a runtime-controller issue.

## Review order

1. Confirm the user-observed clip, playback state, runtime, camera, speed, and intended feeling.
2. Compare default, entry, key pose, exit, and interrupted poses.
3. Check timing and phase lengths: anticipation, action, follow-through, recovery, cooldown, return.
4. Check interpolation, overshoot, velocity continuity, and the loop seam.
5. Check bone ownership, pivot position, orbit center, motion plane, direction, phase separation, and hierarchy.
6. Check contact, swept volume, minimum clearance, clipping, ground penetration, held-item alignment, and camera obstruction.
7. Classify the cause as keyframe/timing/interpolation, pivot/rig contract, model-geometry issue, or runtime/controller issue.

## Revision proposal

Before approval, report:

- affected animation IDs and visible defect;
- intended motion and key pose changes;
- exact timing/interpolation changes;
- pivot, orbit, contact, and clearance changes;
- protected geometry/UV/texture/rig content;
- whether events need retiming and whether dependent rebinding is required;
- new versioned output name and rollback source;
- actual Blockbench and interpolated-frame evidence to capture.

If the safest fix needs geometry, UV, texture, bone topology, bone name, hierarchy, or locator edits, do not improvise. Escalate through the handoff contract.
