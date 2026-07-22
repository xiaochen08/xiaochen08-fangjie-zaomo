# Bounded auto repair

Use an initial attempt plus at most two internal retries (`attempt` 0, 1, and 2); preserve every attempt, report, screenshot, prompt/operation log, and hash under a versioned name. Never overwrite or silently replace prior evidence.

Retry only deterministic, reversible technical defects such as a missing declared group, a measurable position/rotation threshold miss, unintended intersection, wrong origin, invalid locator, broken face/UV placeholder, or evidence capture failure.

Stop immediately for identity mismatch, hash mismatch, approval ambiguity, design ambiguity, wrong asset, changed scope, missing reference, incompatible protocol/capability, or user-choice decisions. These are hard-stop conditions, not retries.

Never lower the approved quality target, delete an approved part, simplify the silhouette, loosen a threshold, or relabel a failed gate to make a retry pass. After attempt 2 fails, return a blocked result to `$fjzm` with exact evidence and no further mutation.
