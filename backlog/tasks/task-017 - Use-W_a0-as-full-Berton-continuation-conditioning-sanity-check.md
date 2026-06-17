---
id: TASK-017
title: Use W_a0 as full Berton continuation conditioning sanity check
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-15 19:47'
updated_date: '2026-06-17 11:06'
labels:
  - berton
  - auto
  - continuation
  - W_a0
dependencies:
  - TASK-013
  - TASK-015
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use W_a0 continuation in the improved full Berton AUTO formulation as a sanity check for branch conditioning and local-equilibrium movement. This task is not primarily Hopf-seeking; it verifies that the reformulated problem can continue a branch for a control known from the Python probe to move the equilibrium smoothly while remaining stable.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Continuation starts from the TASK-011/TASK-012 equilibrium seed in the reformulated AUTO variables.
- [x] #2 W_a0 continuation covers a documented range comparable to the TASK-012 Python probe where feasible, or explains any reduced range.
- [ ] #3 AUTO outputs show whether the branch moves the equilibrium altitude smoothly beyond the seed and no longer immediately fails at the first step.
- [x] #4 Stability/eigenvalue diagnostics are reported and compared with the TASK-012 Python W_a0 probe expectation of stable equilibria.
- [x] #5 The result is used to assess whether remaining H_a3 failures are control-specific or indicate broader formulation/conditioning problems.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Treat TASK-017 as the historical W_a0 conditioning record for the failed full-4D/TASK-017 restricted `M=log(m/m_seed)` attempts, not as the final working W_a0 gate.
2. Read TASK-019 outputs and docs to confirm that AC #3 is now satisfied by the successor `P=M/10` restricted W_a0 gate, while preserving TASK-017/TASK-021 as negative evidence for the un-fixed arclength coordinate.
3. Update the TASK-017 companion note or add a short addendum pointing to TASK-019 as the corrected W_a0 continuation, explaining that the original TASK-017 seed-only failure was due to mass-coordinate arclength scaling rather than a physical W_a0 branch issue.
4. Ensure TASK-017 outputs remain unchanged as a reproducible failure artifact; do not overwrite raw TASK-017 AUTO files.
5. Run the relevant episode-07 tests, then check remaining AC #3 only with explicit wording that the branch movement is demonstrated by TASK-019 successor artifacts.
6. Add a final summary that distinguishes: TASK-017 negative result, TASK-022 diagnosis, TASK-019 fix, and implication for TASK-020/TASK-023.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
TASK-015 already attempted W_a0 on the log-mass full-4D formulation and still accepted only the seed. Follow-up W_a0 conditioning work should move to the restricted/scaled 3D formulation in TASK-018/TASK-019 rather than simply rerunning the TASK-015 setup.

Started TASK-017: set task In Progress and reassessed the existing plan against completed TASK-015/TASK-018. TASK-015 full-4D log-mass W_a0 remained seed-only, so the useful continuation check should now be based on the restricted/scaled 3D route from TASK-018/TASK-019.

- Added restricted/scaled TASK-017 AUTO variant under episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task017 using TASK-018 coordinates Z, U, M=log(m/m_seed), w=0, and row-scaled residuals.
- Ran bidirectional W_a0 AUTO attempts and parsed them with episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task017_wa0_sanity.py.
- Curated outputs under episodes/07-restricted-equilibrium-auto/outputs/task017 and wrote docs/task017_wa0_conditioning_sanity_check.md.
- Result is negative: Python W_a0 probe remains smooth/stable over 0.1-1.2 m/s, but restricted/scaled AUTO still accepts only the seed at W_a0=0.6 and hits DGEBAL/NaN first-step failures. This means H_a3 failures remain broader formulation/conditioning concerns, not control-specific Hopf evidence.
- Validation: uv run pytest tests/test_episode07_restricted_task017.py tests/test_episode07_restricted_task018.py

- Full validation passed: uv run pytest (66 passed).
- TASK-017 remains blocked on AC #3 as written because the new restricted/scaled AUTO attempt still immediately fails after the seed instead of demonstrating nontrivial branch movement. The negative result is documented and should feed TASK-019 refinement.

Post TASK-022 follow-up found a likely fix for AC #3: the restricted AUTO arclength geometry is dominated by `M=log(m/m_seed)`. A scratch variant using `P=M/10` and inverse map `log(m)=log(m_seed)+10P` accepted nontrivial W_a0 points up to the 1.2 target. TASK-019 has been updated to implement this as the curated W_a0 gate rather than treating the TASK-017/TASK-021 seed-only result as final.
<!-- SECTION:NOTES:END -->
