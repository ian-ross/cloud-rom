# TASK-028 — full-model Python H_a3 continuation branch

TASK-028 follows the full four-dimensional Berton equilibrium branch in `H_a3` from the TASK-011/TASK-012 seed after the TASK-027 `W_a0` gate passed.

## Reproducibility command

```bash
uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task028_ha3_branch.py
```

Curated outputs are written to `episodes/10-full-model-python-continuation/outputs/task028/`.

## Branch coverage and diagnostics

The accepted branch covers `H_a3=[0.599999, 0.650020]` with `53` unique accepted control points. The maximum scaled residual norm is `9.590e-08` and the maximum physical RHS residual norm is `8.929e-10`. The largest branch Jacobian condition estimate is `7.808e+03`.

Each accepted point records full residuals, transformed/scaled residuals, all eigenvalues, stable-eigenvalue counts, and a tracked complex-pair real/imaginary component. The independent eigenvalue check recomputes the full finite-difference Jacobian from saved physical states and confirms the tracked pair signs.

## Verdict

No Hopf-style complex-pair sign crossing was found on the accepted segment. A non-Hopf stability-count transition is bracketed between `H_a3=0.633731` and `H_a3=0.635165`: the stable count changes from `4` to `2`, while the right-side critical eigenvalues are real.

## Physical interpretation

The bracketed stable-count transition is most plausibly an **updraft-profile kink effect**, not two clean nearby smooth bifurcations and not robust Hopf evidence. The accepted branch crosses the prescribed updraft cap altitude `z_W0=9000 m` inside the same narrow interval:

- at `H_a3=0.633731`, the accepted equilibrium is at `z≈9023 m`, just above `z_W0`, where the updraft profile is on the constant `W_a0` plateau;
- at `H_a3=0.635165`, the accepted equilibrium is at `z≈8995 m`, just below `z_W0`, where the updraft profile is on the linear ramp.

The model uses a piecewise-linear ambient updraft `W_a(z)`: zero below `z_W0-Δz_W`, a linear ramp over `Δz_W=300 m`, and a constant value above `z_W0`. Therefore `dW_a/dz` jumps at `z_W0` from approximately `W_a0/Δz_W = 0.6/300 ≈ 0.002 s^-1` below the cap to `0` above it. The post-transition positive real eigenvalue is `≈1.96e-3 s^-1`, close to this imposed updraft-ramp slope, which supports the interpretation that the stability change is tied to the derivative discontinuity in the prescribed atmospheric profile.

The affected eigenvectors are physically realizable perturbations, dominated by altitude/vertical-velocity components with weaker mass participation. However, because the stability change is tied to an idealized piecewise-profile derivative jump and occurs over a very narrow `H_a3` interval, it should be treated as an artifact-sensitive local stability feature rather than a likely robust mode during ordinary model evolution. A smoothed-updraft or analytic/autodiff-Jacobian follow-up would be needed before attaching stronger physical significance.

## Numerical limitations

Rejected corrector steps: `0`. The verdict is limited to the reached interval and finite-difference eigenvalue/Jacobian settings recorded in `task028_ha3_branch_verdict.json`.

## Finite-difference Jacobian robustness check

A follow-up finite-difference robustness check recomputed the full-model Jacobian eigenvalues near `H_a3=0.632–0.636` using perturbation scales `[100.0, 30.0, 10.0, 3.0, 1.0, 0.3, 0.1, 0.03, 0.01]` relative to the TASK-009 baseline finite-difference steps. It checked `3` accepted branch states and wrote `27` spectra to `outputs/task028/fd_jacobian_robustness.csv`.

Result for perturbation scales up to 10× the TASK-009 baseline: all trusted scales show a stable-count transition: `True`; trusted scales supporting a Hopf-style complex-pair sign crossing: `False`. Very broad perturbations above 10× baseline are not classification-stable: the 30× case gives an artificial-looking Hopf-like complex sign crossing, while 100× loses the transition entirely. Thus the useful finite-difference sweep supports the conservative classification above: the accepted branch shows a narrow stability-count transition, but not resolved Hopf evidence under baseline-to-10× finite-difference settings. An analytic/autodiff Jacobian would still be a stronger follow-up.
