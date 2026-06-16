---
id: TASK-021
title: Run minimal AUTO W_a0 diagnostic for restricted Berton branch
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-16 13:23'
updated_date: '2026-06-16 13:44'
labels:
  - berton
  - auto
  - continuation
  - diagnostics
dependencies:
  - TASK-017
  - TASK-018
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the fastest diagnostic for the restricted/scaled Berton W_a0 continuation failure: strip the AUTO setup to the smallest possible equilibrium continuation problem and test whether AUTO can follow the known-smooth W_a0 branch when diagnostic parameters, user functions, and supplied Jacobians are removed. This should distinguish a physical/model branch issue from AUTO metadata/Jacobian/PVLS bookkeeping problems.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A minimal restricted/scaled AUTO config is added without overwriting TASK-017 artifacts, using only W_a0 as ICP and no diagnostic/PVLS parameters in the continuation parameter list.
- [ ] #2 The minimal run disables special-point/eigenvalue detection where practical and runs with AUTO finite-difference Jacobians first, e.g. ISP=0 and JAC=0 or documented equivalents.
- [ ] #3 The run is executed in at least one W_a0 direction from the TASK-011/TASK-012 seed and records whether any nontrivial branch points are accepted beyond W_a0=0.6.
- [ ] #4 Results are compared against TASK-017 restricted/scaled failure and the TASK-012 Python W_a0 probe expectation of smooth stable movement.
- [ ] #5 A short note states whether the failure is likely due to AUTO metadata/Jacobian/PVLS bookkeeping or persists even in the stripped configuration, with raw AUTO diagnostics and commands recorded.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a separate minimal AUTO variant/config under episodes/07-restricted-equilibrium-auto/auto/ without modifying TASK-017 artifacts; reuse the same restricted/scaled residual and seed constants from TASK-017/TASK-018.
2. Strip the AUTO constants to the minimum: NDIM=3, ICP only W_a0, no PVLS diagnostic parameters in ICP, no UZR/PVLS-derived output columns unless proven harmless, ISP=0 where accepted, and JAC=0 for the first run so AUTO finite-differences the residual.
3. Run the minimal W_a0 continuation from the TASK-011/TASK-012 seed in the easiest direction first, using conservative DS/DSMIN/DSMAX and raw AUTO diagnostics saved under a distinct TASK-021 name.
4. If the first minimal run still fails, try only tightly scoped variants that isolate setup factors, such as smaller DS, opposite direction, JAC=1 with the existing finite-difference DFDU/DFDP, or removing remaining ancillary callbacks; keep each variant separately named.
5. Parse branch and diagnostic files into outputs/task021, recording accepted W_a0 range, number of nontrivial points, Newton/failure notes, and any differences from TASK-017.
6. Compare the minimal AUTO outcome against the TASK-012 Python W_a0 probe and the TASK-017 restricted/scaled failure to decide whether metadata/PVLS/Jacobian bookkeeping is implicated.
7. Write a concise companion note with commands, constants changed from TASK-017, raw artifact paths, result table, interpretation, and recommended next step for TASK-022/TASK-017.
8. Add regression tests for the minimal config properties, curated outputs, and conclusion language, then run the relevant pytest selection.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Added separate TASK-021 minimal AUTO directory with stripped W_a0 configs (ICP only W_a0, ISP=0/ILP=0/JAC=0, empty PVLS, no supplied Jacobian).
- Ran plus/minus minimal AUTO continuations from the TASK-011/TASK-012 seed; both accepted only the seed at W_a0=0.6 and failed first correction with pivot/NaN diagnostics.
- Added parser/synthesis script, curated task021 outputs, companion note, reproducibility notebook, and pytest coverage.
- Verification: uv run pytest tests/test_episode07_restricted_task017.py tests/test_episode07_restricted_task018.py tests/test_episode07_restricted_task021.py (12 passed).
<!-- SECTION:NOTES:END -->
