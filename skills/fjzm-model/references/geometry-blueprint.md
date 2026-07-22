# Geometry blueprint

The blueprint converts an approved image into quantities Blockbench can reproduce. Record:

- global width, height, depth, ground line, center, and intended Minecraft scale;
- front/back/left/right/top/bottom silhouettes and the three-quarter identity read;
- every blocking anchor with part name, parent group, dimensions, position, rotation, material role, and reference coordinates;
- symmetry pairs and approved asymmetry;
- base bone hierarchy, stable names, origins, and locators;
- moving-part orbit center, swept envelope, and minimum clearance;
- explicit included parts, excluded parts, and details delegated to texture;
- placeholder UV intent without final painting.

Geometry owns visible volume. Texture owns surface appearance. Do not imitate a missing muzzle, nose, ear, strap, armor plate, crystal, or silhouette break with painted pixels. Conversely, do not create tiny cubes for detail approved as a texture mark.

Use Blockbench units consistently. Orthographic reference views drive numeric measurement; perspective three-quarter views are a visual identity check unless camera calibration is known.
