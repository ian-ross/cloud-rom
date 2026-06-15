---
id: TASK-007
title: Validate AUTO-07p on reduced Berton 3D model
status: Done
assignee:
  - '@pi'
created_date: '2026-06-14 12:39'
updated_date: '2026-06-15 12:12'
labels:
  - berton
  - auto
  - continuation
dependencies: []
references:
  - scripts/berton_3d_hopf_task005_classification.py
  - docs/berton_3d_hopf_analysis_summary.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create an AUTO-07p continuation problem for the already-audited reduced Berton 3D fixed-point model and verify AUTO reproduces the Python symbolic/root-tracking stability results before porting the full Berton model.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 AUTO problem files for the reduced 3D model are added with clear parameter/state definitions.
- [x] #2 Equilibrium continuation runs over a drag-rate or mechanism-relevant parameter and detects/records stability consistently with the Python root-tracking scripts.
- [x] #3 AUTO eigenvalue/Hopf diagnostics are cross-checked against the existing Python corrected cubic at matched parameter values.
- [x] #4 A short validation note documents commands run, AUTO output files inspected, and any discrepancies.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Check that AUTO-07p is available in the environment and document the exact invocation expected for this repo.
2. Create a minimal AUTO example directory for the reduced 3D Berton model with state U=(zeta, v, r) and parameters matching the audited corrected local model.
3. Encode the reduced RHS and starting equilibrium using the TASK-003/TASK-005 baseline slow parameters, keeping parameter names and units documented.
4. Configure equilibrium continuation over k and, if useful, one mechanism parameter such as a sigma_S+R_zeta or radiation-gradient multiplier.
5. Run AUTO continuation and save/parse the branch output needed to compare stability and special-point diagnostics.
6. Add a Python validation script/test that evaluates the corrected cubic at the AUTO branch points and checks eigenvalue/stability agreement.
7. Write a short validation note with commands, files inspected, agreement/discrepancies, and remaining limitations.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Implemented AUTO reduced 3D problem in auto/berton_reduced_3d with documented U=(zeta,v,r), continuation parameters, and PVLS diagnostics for c, d, a0, RH residual, and analytic Hopf alpha.
- Ran bash auto/berton_reduced_3d/run_auto.sh; inspected saved b/s/d.bert3d-k and b/s/d.bert3d-alpha outputs. AUTO labels HB on the alpha_grad mechanism branch near 7.0603386e2.
- Added scripts/berton_3d_auto_task007_validate.py plus pytest coverage to parse AUTO branch output and compare a0/RH/eigenvalue stability against the corrected Python cubic.
- Added docs/berton_3d_auto_task007_validation.md and notebooks/berton_3d_auto_task007_validation.ipynb documenting commands, outputs, plots, agreement, and limitations.
- Verification run: uv run python scripts/berton_3d_auto_task007_validate.py; uv run pytest; 40 passed.

Repository reorganization note: TASK-007 AUTO validation artifacts moved to episodes/03-reduced-model-auto/ (auto/, docs/, notebooks/, scripts/ subdirectories).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added an AUTO-07p validation problem for the audited reduced Berton 3D fixed-point model.

Changes:
- Added auto/berton_reduced_3d with Fortran RHS, k and alpha_grad continuation constants, saved AUTO branch/solution/diagnostic outputs, and a run script.
- Added a validation script and pytest coverage that parse AUTO b.* files and cross-check a0, Routh-Hurwitz residuals, roots, and the AUTO HB label against the corrected Python cubic.
- Added a validation note and notebook documenting state/parameter definitions, exact commands, inspected AUTO outputs, matched diagnostics, and limitations.

Validation:
- bash auto/berton_reduced_3d/run_auto.sh
- uv run python scripts/berton_3d_auto_task007_validate.py
- uv run pytest (40 passed)

Result: AUTO agrees with the Python corrected cubic on the stable drag-rate continuation and detects the expected Hopf crossing on the alpha_grad mechanism branch near 7.0603386e2.
<!-- SECTION:FINAL_SUMMARY:END -->
