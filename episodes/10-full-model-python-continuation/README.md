# Episode 10 — Full-model Python continuation

This episode is the reproducible home for the Python-continuation-first investigation of the full Berton cirrus parcel model.

## Purpose

Episodes 06–09 showed that the full-model AUTO equilibrium formulations are fragile near the paper-relevant controls. Episode 10 therefore moves the primary branch exploration into Python, where continuation steps, residual scaling, state transformations, smoothing choices, diagnostics, and fallback solvers can be inspected directly before any final AUTO handoff.

The episode should answer whether a well-conditioned full-model equilibrium branch can be followed through the scientifically relevant control ranges, and whether any candidate local bifurcation or stability change is robust enough to justify a later AUTO validation run.

## Scope

In scope:

- Python-first pseudo-arclength or predictor-corrector continuation experiments for the full 4D Berton equilibrium problem.
- Reuse of the scaled variables, log-mass coordinate, and softplus updraft-transition lessons from earlier episodes.
- Notebook records that show exact solver settings, continuation parameters, branch diagnostics, eigenvalue checks, labels inspected, and generated output paths.
- Curated outputs that support documented findings.
- AUTO files only when the Python investigation has produced a final validation target.

Out of scope for this episode:

- Treating AUTO first-step failures as the primary exploration mechanism.
- Periodic-orbit continuation without an independently validated equilibrium branch or periodic seed.
- New research artifacts in old top-level `scripts/`, `notebooks/`, `docs/`, `auto/`, or `outputs/` directories.

## Relationship to episodes 06–09

- `episodes/06-full-model-auto-seed-continuation/` established the TASK-011 late-time full-model equilibrium seed and showed that direct full-system AUTO continuation in `W_a0` and `H_a3` remained numerically fragile even after log-mass reformulation.
- `episodes/07-restricted-equilibrium-auto/` demonstrated that restricted/local 3D formulations can become useful after centering, scaling, row-scaled residuals, and a softplus-smoothed updraft transition; it also identified the 9.6--10 km updraft-transition region as a major numerical risk.
- `episodes/08-full-model-auto-ha3/` retried the full-system `H_a3` branch with scaled variables but accepted no useful nontrivial AUTO branch and found no AUTO-supported Hopf label.
- `episodes/09-full-model-auto-zw0/` ported the smoothed updraft transition into a full 4D AUTO `z_W0` continuation but again accepted only the seed before numerical failure.

Episode 10 keeps these lessons but changes the order of operations: explore and condition the full-model branch in Python first, then use AUTO only to validate a mature, reproducible candidate.

## Strategy

1. Start from the validated late-time equilibrium seed used by episodes 06–09.
2. Implement Python continuation experiments with explicit control over residual scaling, state scaling, tangent prediction, correction, step rejection, and branch diagnostics.
3. Track stability with independent Jacobian/eigenvalue checks at accepted branch points.
4. Save notebooks, scripts, and curated outputs inside this episode so every figure or verdict can be regenerated.
5. Prepare an AUTO validation case only after Python continuation identifies a branch segment or bifurcation candidate worth validating.

In short: **Python continuation first; AUTO only for final validation.**

## Current artifacts

- `scripts/berton_full_task026_continuation.py` — full 4D scaled/log-mass Python pseudo-arclength core with a local `W_a0` seed step and transparent diagnostics.
- `scripts/berton_full_task027_wa0_gate.py` — full-model `W_a0` gate following the branch through the prior probe range, adding exact anchor refinements, eigenvalue/conditioning diagnostics, and a pass/fail verdict.
- `docs/task026_python_continuation_core.md` — reproducibility note for the TASK-026 core, coordinate definitions, output files, and residual risks.
- `docs/task027_wa0_full_model_gate.md` — TASK-027 gate note comparing the full-model Python branch against the previous TASK-012 probe and restricted TASK-019 behavior.
- `outputs/task026/` — curated seed/corrected point, eigenvalue, tangent, Newton iteration, and condition-diagnostic outputs.
- `outputs/task027/` — curated full-model `W_a0` branch points, exact anchor reachability, eigenvalues, corrector iterations, comparison tables, and verdict JSON.

## Organization

- `notebooks/` — notebook-first reproducibility records for continuation runs, plots, and branch/stability diagnostics.
- `scripts/` — standalone Python helpers for continuation, parsing, validation, and reproducible output generation.
- `outputs/` — curated tables, plots, JSON summaries, and branch diagnostics supporting documented findings.
- `docs/` — companion notes, strategy records, scaling decisions, and verdicts.
- `auto/` — reserved for final AUTO validation inputs/outputs after Python has produced a validation target.
