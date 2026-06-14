---
id: TASK-007
title: Validate AUTO-07p on reduced Berton 3D model
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-14 12:39'
updated_date: '2026-06-14 15:23'
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
- [ ] #1 AUTO problem files for the reduced 3D model are added with clear parameter/state definitions.
- [ ] #2 Equilibrium continuation runs over a drag-rate or mechanism-relevant parameter and detects/records stability consistently with the Python root-tracking scripts.
- [ ] #3 AUTO eigenvalue/Hopf diagnostics are cross-checked against the existing Python corrected cubic at matched parameter values.
- [ ] #4 A short validation note documents commands run, AUTO output files inspected, and any discrepancies.
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
