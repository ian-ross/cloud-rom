---
id: TASK-028
title: Continue full-model H_a3 branch with Python continuation
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-17 16:39'
updated_date: '2026-06-17 17:13'
labels:
  - berton
  - continuation
  - python
  - hopf
  - episode-10
dependencies:
  - TASK-027
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After the W_a0 gate passes, use Python pseudo-arclength continuation to follow the actual full Berton equilibrium branch in H_a3 through the previously suspected stability-crossing region, rather than evaluating fixed-seed probes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 H_a3 continuation starts from the TASK-011/TASK-012 equilibrium seed and attempts to cover the suspected H_a3≈0.61–0.65 crossing region
- [x] #2 Accepted branch points include full residuals, scaled residuals, eigenvalue spectra, stable-eigenvalue counts, and complex-pair tracking
- [x] #3 Any candidate Hopf crossing is supported by accepted equilibrium branch points on both sides and an independently checked eigenvalue sign change
- [x] #4 If no crossing is found or continuation fails, the report distinguishes numerical limitation from negative dynamical evidence
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review TASK-027 output and existing episode-10 continuation/gate scripts to identify the validated W_a0 seed, TASK-011/TASK-012 equilibrium seed, parameter conventions, and output locations.
2. Inspect the current Python continuation utilities/tests for full-model equilibria and eigenvalue diagnostics.
3. Implement or adapt a reproducible notebook/script under the current episode to run pseudo-arclength continuation in H_a3 across H_a3≈0.61–0.65 from the validated seed.
4. Ensure saved branch outputs include residuals, scaled residuals, eigenvalue spectra, stable counts, and complex-pair tracking; add lightweight validation/helpers/tests if useful.
5. Run the continuation/validation, inspect any candidate Hopf crossing with independent eigenvalue sign checks, and write a concise report distinguishing negative evidence from numerical limitations.
6. Update TASK-028 notes, acceptance criteria, and final summary via backlog CLI after verification.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented episode-10 TASK-028 H_a3 pseudo-arclength script and curated outputs. The branch covers H_a3≈0.6000–0.6500 from the TASK-011/TASK-012 seed, with residual/eigenvalue/complex-pair diagnostics and independent eigenvalue recomputation. Result: no Hopf-style complex-pair sign crossing; accepted points bracket a non-Hopf stable-count transition from 4 to 2 near H_a3≈0.6337–0.6352. Added regression tests and updated episode README.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented TASK-028 full-model Python H_a3 continuation in episode 10.

Changes:
- Added `episodes/10-full-model-python-continuation/scripts/berton_full_task028_ha3_branch.py` to continue the full Berton equilibrium branch in H_a3 from the TASK-011/TASK-012 seed.
- Wrote curated TASK-028 outputs with accepted branch points, residuals, scaled residuals, eigenvalue spectra, stable counts, complex-pair tracking, rejected-step/corrector histories, and independent eigenvalue checks.
- Added `docs/task028_ha3_full_model_branch.md` and updated the episode README.
- Added regression tests in `tests/test_episode10_task028_ha3_branch.py`.

Result:
- The branch covers H_a3≈0.6000–0.6500 with max scaled residual ≈9.59e-08.
- No Hopf-style complex-pair sign crossing is supported on the accepted branch segment.
- Accepted branch points bracket a non-Hopf stability-count transition from 4 to 2 between H_a3≈0.633731 and 0.635165; the right-side critical eigenvalues are real, so this is not treated as Hopf evidence.

Tests:
- `uv run pytest tests/test_episode10_task028_ha3_branch.py`
- `uv run pytest tests/test_episode10_task028_ha3_branch.py tests/test_episode10_task027_wa0_gate.py`
<!-- SECTION:FINAL_SUMMARY:END -->
