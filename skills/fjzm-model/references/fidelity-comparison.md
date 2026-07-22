# Fidelity comparison

## Evidence set

Reopen the saved output in actual Blockbench and capture one summary board plus eight separate high-resolution views: front, back, left, right, top, bottom, three-quarter, and gameplay-distance.

For each comparable view, provide the approved reference beside the actual Blockbench render and a 50% transparent overlay. Bind the report to the exact model SHA-256 and reference SHA-256. Record camera type, orientation, scale, and whether the comparison is numeric or visual.

Orthographic front/back/left/right/top/bottom views use numeric measurements. Three-quarter and gameplay-distance views use visual comparison unless the reference camera is calibrated.

## Balanced fidelity gate

- blocking anchors: 100%
- missing approved parts: zero
- unapproved parts: zero
- main proportion error: at most 5%
- key-part position error: at most 0.5 Blockbench units
- symmetric-part error: at most 0.25 Blockbench units
- rotation error: at most 3 degrees
- declared moving clearance: pass
- zero unintended intersections, floating parts, wrong groups, and identity mismatch

Any failed blocking anchor fails the report. Cosmetic micro-detail may be deferred only when the approved blueprint explicitly assigns it to texture; it may not hide a geometry miss.
