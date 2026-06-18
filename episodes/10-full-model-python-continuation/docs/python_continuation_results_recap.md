# Python continuation results recap

This note summarizes the Episode 10 Python-continuation results through TASK-029.

## Continuation setup

The Episode 10 Python continuation workflow now has a validated full-model equilibrium continuation core:

- State variables: scaled `z`, `u`, `w`, and `log(m/kg)`.
- Residual row scaling: `[10, 100, 100, 1e8]`.
- Pseudo-arclength predictor/corrector with explicit residual, tangent, Newton, conditioning, and rejected-step diagnostics.
- Full-model diagnostics at accepted points: physical RHS residuals, transformed/scaled residuals, eigenvalue spectra, stable-eigenvalue counts, and branch-Jacobian conditioning.
- Seed: the TASK-011/TASK-012 late-time full Berton equilibrium.

The local TASK-026 validation step converged with scaled residual about `5.1e-08`, confirming that the core algebra and scaling are usable.

## TASK-027 — `W_a0` gate

TASK-027 used `W_a0` as the first full-model conditioning/control sanity gate.

Results:

- Branch covered `W_a0≈0.0995–1.2006 m/s`.
- Reached all requested anchors through `W_a0=1.2 m/s`.
- Accepted `52` unique points.
- Rejected steps: `0`.
- Max scaled residual: `2.5e-07`.
- Branch geometry matches the previous Python probe and restricted TASK-019 behavior closely.

Conclusion:

> The full-model Python continuation core is reliable enough for harder controls. `W_a0` is not the source of the previous AUTO fragility.

## TASK-028 — `H_a3` branch

TASK-028 followed the actual full-model equilibrium branch in `H_a3` across the suspected `0.61–0.65` crossing region.

Results:

- Covered `H_a3≈0.6000–0.6500`.
- Accepted `53` unique points.
- Rejected steps: `0`.
- Max scaled residual: `9.6e-08`.
- Independent eigenvalue recomputation agreed exactly for tracked-pair real parts.

Key finding:

- No Hopf-style complex-pair sign crossing was found.
- A stability-count transition was bracketed:
  - Left: `H_a3≈0.633731`, stable count `4`, critical eigenvalue complex with small negative real part.
  - Right: `H_a3≈0.635165`, stable count `2`, critical eigenvalues real with positive real part.

Conclusion:

> There is accepted-branch evidence for a stability-count change, but not for a Hopf crossing. The transition is likely artifact-sensitive near the updraft-profile kink/transition rather than robust oscillatory evidence.

## TASK-029 — staged `z_W0` smoothing

TASK-029 moved to the paper-relevant `z_W0` control using the TASK-023/TASK-024 smoothed updraft formulation.

Setup:

- Control scaling: `q_z=(z_W0 - 9000 m)/1000 m`.
- Physical inverse: `z_W0 = 9000 m + 1000 m q_z`.
- Smoothed updraft: `W_a0 * eps * (softplus(x/eps)-softplus((x-1)/eps))`.
- Staged smoothing widths: `300`, `150`, `100`, and `50 m`.
- Final `50 m` width matches TASK-023/TASK-024.

Results for the sharp `50 m` width:

- Reached `z_W0≈6999.5–9929.96 m`.
- Accepted anchors through `9900 m`.
- Accepted `48` unique sharp-width points.
- Accepted `28` points in the `9.6–10 km` transition region.
- Did not cleanly reach `10 km`.
- Max scaled residual: `2.2e-07`.
- Rejected steps accumulated near `z_W0≈9930 m`.

Easier smoothing widths:

- `100–300 m` smoothing reached approximately `10 km`.

Conclusion:

> Transition-region fragility is smoothing/nonsmoothness-sensitive. It is not primarily explained by bad `q_z` scaling. The sharp 50 m profile gets deep into the transition region but still fails before a fully clean 7–10 km result.

## Overall interpretation

The Python continuation setup has clarified the full-model continuation picture:

1. The full-model continuation core works.
2. Basic branch following is well conditioned for `W_a0`.
3. The suspected `H_a3` Hopf is not supported by accepted branch/eigenvalue evidence.
4. `z_W0` is the genuinely fragile control, especially near the updraft transition.
5. Smoothing width matters: easier smoothing reaches farther, while the TASK-023/TASK-024 50 m width stalls near the upper transition region.
6. The earlier AUTO failures were not just AUTO quirks; the Python workflow indicates that they are tied to transition-region smoothness/geometry rather than a global inability to continue the full model.

Short version:

> Python continuation is now a reliable diagnostic tool for the full model. It gives negative evidence for a clean `H_a3` Hopf and identifies `z_W0` transition-region smoothness as the remaining hard numerical/dynamical bottleneck.
