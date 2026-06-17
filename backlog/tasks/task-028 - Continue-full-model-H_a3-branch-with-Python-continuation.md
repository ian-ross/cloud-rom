---
id: TASK-028
title: Continue full-model H_a3 branch with Python continuation
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-17 16:39'
updated_date: '2026-06-17 17:05'
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
- [ ] #1 H_a3 continuation starts from the TASK-011/TASK-012 equilibrium seed and attempts to cover the suspected H_a3≈0.61–0.65 crossing region
- [ ] #2 Accepted branch points include full residuals, scaled residuals, eigenvalue spectra, stable-eigenvalue counts, and complex-pair tracking
- [ ] #3 Any candidate Hopf crossing is supported by accepted equilibrium branch points on both sides and an independently checked eigenvalue sign change
- [ ] #4 If no crossing is found or continuation fails, the report distinguishes numerical limitation from negative dynamical evidence
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
