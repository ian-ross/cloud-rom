---
id: TASK-020
title: Retry H_a3 Hopf-control continuation on scaled restricted 3D system
status: Done
assignee:
  - '@pi'
created_date: '2026-06-15 20:17'
updated_date: '2026-06-17 11:23'
labels:
  - berton
  - auto
  - hopf
  - continuation
dependencies:
  - TASK-019
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In episodes/07-restricted-equilibrium-auto/, after the restricted 3D W_a0 sanity check demonstrates acceptable conditioning, retry H_a3 as the Hopf-relevant control on the scaled restricted equilibrium formulation. Treat this as the successor to the direct full-4D H_a3 retry, which should not be trusted until the restricted formulation passes the W_a0 gate.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 H_a3 continuation uses the scaled restricted 3D AUTO formulation validated by the W_a0 sanity check, or explicitly documents why the gate was not met.
- [x] #2 AUTO branch results are parsed for accepted points, LP/HB/BP labels, eigenvalue diagnostics, and user-defined control anchors over a documented H_a3 range.
- [x] #3 Python diagnostics independently evaluate residuals and critical eigenvalues along representative accepted points or explain why this is impossible.
- [x] #4 Results are compared against the TASK-012 Python H_a3 probe and the failed full-4D AUTO attempts.
- [x] #5 A companion note states whether there is AUTO-supported evidence for a Hopf candidate, no crossing, or continued numerical inconclusiveness.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Start from the TASK-019 validated restricted formulation: `Z=(z-z_seed)/100`, `U=(u-u_seed)/(1 m/s)`, `P=M/10`, row-scaled residuals, physical inverse `m=m_seed*exp(10P)`, and parsers/tests that reconstruct physical `M` and `m`.
2. Before running production AUTO, compute the local H_a3 implicit tangent from TASK-022-style Python finite differences in the TASK-019 coordinates; use it to choose H_a3-specific arclength scaling rather than raw `H_a3`.
3. Introduce a scaled active H_a3 control if needed, e.g. `q_H=(H_a3-0.61)/h_scale`, with `h_scale` chosen so one unit of q_H gives order-one state motion; document the mapping and report physical H_a3 in all outputs.
4. If raw H_a3 still causes huge Z/U excursions, add a second controlled variant with adjusted state scales for the H_a3 branch, but keep the physical residual and `P=M/10` mass scaling unchanged.
5. Run bidirectional H_a3 continuation over the TASK-012 probe range that brackets the predicted stability crossing near H_a3≈0.62, preserving raw `b/s/d` outputs under distinct TASK-020 names.
6. Parse accepted branch points, user anchors, LP/HB/BP labels, stability index/eigenvalues where available, physical z/u/m, `P` and reconstructed `M`, and convergence notes into `outputs/task020/`.
7. Independently evaluate Python restricted residuals and full physical finite-difference eigenvalues at representative accepted points and around any suspected stability crossing.
8. Compare results against the TASK-012 H_a3 Python probe, the failed full-4D TASK-012/TASK-015 attempts, and the successful TASK-019 W_a0 gate.
9. Write a companion verdict note: AUTO-supported Hopf candidate, no crossing, numerical hint only, or still inconclusive; explicitly state whether H_a3 scaling is now good enough to inform TASK-016.
10. Add tests for H_a3 artifacts, scaled-control mapping, `P<->M` conversion, range/anchor coverage or documented failure, independent eigenvalue checks, and conservative verdict language.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
TASK-022 follow-up found a concrete arclength scaling fix for the restricted W_a0 gate: continue the mass coordinate as `P=M/10` with `M=log(m/m_seed)`, mapping back via `log(m)=log(m_seed)+10P`. TASK-020 should not clone the older TASK-017/TASK-021 `M` coordinate; it should wait for TASK-019 to validate and curate the `P=M/10` W_a0 branch, then reuse that exact coordinate for H_a3.

TASK-019 has now validated the `P=M/10` restricted W_a0 gate: upward continuation reaches all W_a0 anchors through 1.2 and matches the TASK-012 Python probe closely. TASK-020 can proceed using the exact TASK-019 formulation and should treat the W_a0 conditioning gate as passed.

- Started TASK-020 after TASK-019 cleared the W_a0 gate. A direct H_a3 continuation using the validated `P=M/10` mass coordinate is not sufficient by itself: the local TASK-022 tangent has very large altitude sensitivity (`dZ/dH_a3≈-279`, `dU/dH_a3≈139`, `dP/dH_a3≈0.110`), so AUTO makes large state excursions while H_a3 advances only ~1e-3 before MX/failure.
- Removed the scratch direct-H_a3 AUTO artifacts rather than curating them as final results. Next TASK-020 step should add H_a3-specific arclength scaling, likely an active scaled control `q_H=(H_a3-0.61)/0.001` plus reconsidered state scaling for altitude/horizontal velocity, before making any Hopf verdict.

- Implemented TASK-020 scaled H_a3 AUTO variants under episodes/07-restricted-equilibrium-auto/auto/: the trusted TASK-019-state-scale q_H continuation and an exploratory larger-state-scale retry.
- Ran both AUTO scripts and curated outputs with berton_restricted_task020_ha3_scaled.py into outputs/task020/.
- Downward q_H run accepted a nontrivial restricted branch and detected an LP near H_a3=0.5971; upward run stopped near H_a3=0.611 with DGEBAL/floating-point diagnostics; no HB label was accepted.
- Added independent Python residual/eigenvalue diagnostics, TASK-012/TASK-015 comparisons, conservative verdict note, and regression tests.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the TASK-020 scaled restricted H_a3 continuation attempt after the TASK-019 W_a0 gate.

Changes:
- Added AUTO sources/configs for q_H=(H_a3-0.61)/0.001 using the validated TASK-019 P=M/10 restricted formulation.
- Added an exploratory H-specific state-scale retry, preserving the same physical residual and mass coordinate.
- Added a synthesis script that parses AUTO branches/diagnostics, reconstructs physical H_a3/z/u/m, evaluates Python residuals and full finite-difference eigenvalues, compares against TASK-012/TASK-015, and writes a conservative verdict note.
- Added TASK-020 regression tests for scaling, branch parsing, diagnostics, comparisons, and no-Hopf verdict language.

Result:
- AUTO accepts a nontrivial downward restricted H_a3 branch and detects an LP near H_a3≈0.5971.
- The upward Hopf-relevant direction remains numerically inconclusive, stopping near H_a3≈0.611 with DGEBAL/floating-point diagnostics.
- No AUTO-supported HB/Hopf candidate is present; the TASK-012 crossing near 0.62 remains a Python hint only.

Tests:
- uv run pytest tests/test_episode07_restricted_task019.py tests/test_episode07_restricted_task020.py
<!-- SECTION:FINAL_SUMMARY:END -->
