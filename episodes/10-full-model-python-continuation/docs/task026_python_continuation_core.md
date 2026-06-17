# TASK-026 — Python pseudo-arclength continuation core

This note records the first Episode 10 continuation core implementation for the full Berton equilibrium problem.

## Reproducibility command

```bash
uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task026_continuation.py
```

The script reads the TASK-011/TASK-012 late-time equilibrium seed from:

- `episodes/05-full-model-oscillatory-orbit/outputs/task011/continuation_equilibrium_seed.csv`

and writes curated TASK-026 diagnostics to:

- `episodes/10-full-model-python-continuation/outputs/task026/continuation_diagnostics.json`
- `episodes/10-full-model-python-continuation/outputs/task026/seed_and_corrected_points.csv`
- `episodes/10-full-model-python-continuation/outputs/task026/seed_corrected_eigenvalues.csv`
- `episodes/10-full-model-python-continuation/outputs/task026/corrector_iterations.csv`
- `episodes/10-full-model-python-continuation/outputs/task026/tangent_estimates.csv`

## Coordinate system

The continuation state is the full four-dimensional Berton equilibrium state in scaled variables:

- `x0 = (z_m - z_ref_m) / z_scale_m` for altitude,
- `x1 = (u_m_s - u_ref_m_s) / u_scale_m_s` for horizontal velocity,
- `x2 = (w_m_s - w_ref_m_s) / w_scale_m_s` for vertical velocity,
- `x3 = (log(m_kg) - log_m_ref) / log_m_scale` for log mass.

The current local branch control is:

- `lambda = (W_a0_m_s - W_a0_ref_m_s) / W_a0_scale_m_s`.

The residual is the full transformed RHS `[z_dot, u_dot, w_dot, d(log m)/dt]`, row-scaled before Newton solves.  This keeps the tiny raw mass tendency visible without returning to the ill-scaled raw mass coordinate.

## Predictor/corrector diagnostics

For the seed and one local pseudo-arclength step, the script records:

- scaled and physical residual norms,
- pseudo-arclength step size and accepted control step,
- SVD tangent estimates at the seed and corrected point,
- branch and augmented Jacobian singular values and condition estimates,
- Newton iteration residual norms, correction norms, linear solver mode, and convergence reason.

The initial run accepted one local step with convergence reason `converged`.  This is intentionally a core validation step, not yet a long branch-following verdict.

## Seed residual/eigenvalue cross-check

`seed_and_corrected_points.csv` reproduces the TASK-011/TASK-012 equilibrium residual check in both physical and transformed/scaled coordinates.  `seed_corrected_eigenvalues.csv` records finite-difference eigenvalues of the physical full-model RHS at the seed and corrected point; the seed retains the stable complex pair previously used to explain the damped oscillatory trajectory.

## Residual risks

- Only one local `W_a0` step is exercised here; adaptive continuation, step rejection policy, branch-length diagnostics, and other controls remain follow-up work.
- Finite-difference Jacobians are adequate for transparent debugging but may need analytic or mixed analytic/finite-difference derivatives for larger branch segments.
- Updraft transition nonsmoothness is not stressed by this local step and remains a known risk from episodes 07–09.
