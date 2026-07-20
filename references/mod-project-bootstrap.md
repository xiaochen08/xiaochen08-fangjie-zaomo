# Java Mod project bootstrap gate

## Opening route

Ask whether the user has an authorized Mod project and its path before asking the model category.

- Existing project: do not create another one; use `scripts/inspect_runtime_project.py` and preserve its hashes.
- Missing or unknown project: offer a minimal Mod shell through the first route, present exactly these two routes, and wait for the user's explicit choice:
  1. `create_mod_first` — prepare a minimal Mod shell before model production; collect the locked creation brief only after this route is selected.
  2. model-first (`model_first`) — record `project_status: runtime_deferred`; run the runtime risk classification in `model-first-runtime-gate.md`; validate `runtime-contract.json`; proceed only to its production ceiling. A validated `runtime-neutral source` may include editable geometry, textures, adapter-safe groups/origins, and provisional animation/effect/audio contracts. Platform exports stay blocked, runtime integration remains deferred, and no runtime integration claim is allowed.

Do not continue to the model category until the project route is explicitly selected. Do not auto-resolve, recommend as if selected, or treat silence, urgency, model approval, or “decide for me” as the route choice. Record the user's verbatim choice as `route_choice_evidence`.

Never create a project from silence, urgency, delegated choice, or model approval. Project creation requires separate explicit project-creation approval and an absolute destination path that does not already exist.

Do not force Mod creation for every asset. For medium/high-risk runtime-dependent assets, present `create_mod_first` as the default recommendation. If the user declines, require separate verbatim decline evidence, explicit risk acceptance, and a validated production ceiling. Unknown critical role/render/animation decisions restrict work to concepts or graybox; they never authorize a speculative final rig.

## When the version is unknown

If the user does not know the Minecraft version, ask whether the target must match an existing server or modpack, other players, or an older world; otherwise offer a latest stable profile suitable for the requested feature set.

Check official primary sources at execution time for Minecraft, loader, mappings, animation library, Java, Gradle/plugin, and generator/template compatibility. Record direct source URLs and the check timestamp. Community tutorials may explain usage but cannot be the compatibility authority. State uncertainty and do not guess compatibility.

Present at most three evidence-backed profiles with tradeoffs. Do not describe “latest” as a version number until verified. Wait for the user to select or approve one profile.

## Locked creation brief

Create `mod-project-brief.json` with:

- explicit route choice and verbatim route-choice evidence;
- Minecraft version;
- loader and loader version;
- mappings;
- animation runtime and version;
- namespace and mod_id plus display name;
- Java and Gradle versions;
- unused absolute destination path;
- official compatibility evidence;
- verbatim creation approval;
- Windows toolchain policy.

Run `scripts/validate_mod_project_brief.py` and fix every error before creating files.

For `runtime_deferred`, the brief must instead reference a validated `runtime-contract.json`, record `runtime_risk`, `production_ceiling`, Mod-first recommendation/decline evidence, risk acceptance, and the `no runtime integration claim` restriction.

## Windows creation rules

Use PowerShell 7 and literal absolute paths. Prefer the selected loader's official generator or official template for the exact approved version profile. Review the generated file list before writing.

Use a project-local wrapper and `gradlew.bat`; no global install, global PATH change, JDK replacement, or package-manager switch without separate user approval. Never merge into or overwrite an existing directory during bootstrap.

## Minimal Mod shell

Create only what is required to compile and launch:

- version-pinned build files and wrapper;
- minimal entrypoint and mod metadata;
- `src/main/resources/assets/<namespace>` with model, texture, animation, sound, language, and particle-ready directories;
- required data/server directories for the chosen loader;
- selected animation dependency only when its exact compatibility is verified;
- identity-scoped placeholders/contracts, not speculative gameplay code.

Do not implement the boss, targeting, damage, projectile, particles, or audio behavior merely because the shell exists. Those remain later approved production tasks.

## Smoke evidence

On Windows, run the project-local wrapper diagnostics, then `gradlew.bat build`. If authorized and supported, run `gradlew.bat runClient`, launch the development client, and confirm the empty Mod loads without errors. Record command arguments, exit codes, logs, build artifact hash, Java/Gradle versions, project inspection report, and failures.

A successful shell proves only that the selected toolchain launches. It does not verify the future model or gameplay implementation.
