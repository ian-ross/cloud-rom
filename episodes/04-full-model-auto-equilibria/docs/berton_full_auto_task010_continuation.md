# TASK-010 full Berton equilibrium continuation and Hopf screen

This note records the reproducible AUTO-07p equilibrium continuation for the full four-state Berton model and the independent Python eigenvalue cross-checks.

## Reproducible workflow

The notebook-driven workflow is in:

- `episodes/04-full-model-auto-equilibria/notebooks/berton_full_auto_task010_continuation.ipynb`

It calls the same checked-in AUTO configuration used by the script:

```bash
bash episodes/04-full-model-auto-equilibria/auto/berton_full/run_auto.sh
uv run python episodes/04-full-model-auto-equilibria/scripts/berton_full_auto_task010_analyze.py
```

The AUTO constants/configuration are checked in at `episodes/04-full-model-auto-equilibria/auto/berton_full/c.bertonfull`. The primary continuation parameter is `PAR(1)=z_W0`, with the Berton-relevant anchors `10000`, `9500`, `9000`, and `8500` m in `UZR`. The run uses the TASK-009 full-model Fortran problem `episodes/04-full-model-auto-equilibria/auto/berton_full/bertonfull.f90` with `include_coriolis=0`, `W_a0=0.6 m/s`, `rad_mult=1`, and Case-0 humidity/eta settings.

Generated analysis artifacts are in `episodes/04-full-model-auto-equilibria/outputs/task010/`:

- `branch_points.csv`: parsed AUTO branch rows.
- `labeled_solution_cross_checks.csv`: labeled AUTO solutions with independent Python finite-difference eigenvalues.
- `special_points.csv` / `special_points.md`: LP/HB/BP catalogue.
- `summary_table.csv` / `summary_table.md`: compact table for the 10 km to 8.5 km control range and endpoints.
- `branch_summary.png`: summary plot.

## Continuation interval and branch structure

The branch was continued from `z_W0=10000 m` through the selected Berton transition interval down to `9000 m`, with an additional anchor at `8500 m`. The saved AUTO branch also continued past the requested lower anchor because the current AUTO run did not terminate at the `UZSTOP` lower bound; the analysis table therefore highlights the required 10--9 km interval plus the 8.5 km robustness anchor and treats the lower extra continuation only as an endpoint diagnostic.

Across the 10 km to 9 km interval, the solved equilibrium remains on the same saturated-updraft branch:

- `z* = 10178.50407189 m`
- `u* = -0.8925203595 m/s`
- `w* = 0 m/s`
- `m* = 1.0570071795e-9 kg`

This invariance is expected for this first control: the equilibrium altitude lies above all tested `z_W0` values, so `W_a(z*) = W_a0 = 0.6 m/s` remains unchanged as the updraft base/top parameter is lowered.

## AUTO special-point catalogue

No AUTO limit points, Hopf points, or branch points were detected on the labeled equilibrium continuation branch. The `d.bertfull-zW0` file reports the BP test function value, but no branch-point label (`TY=1`) is present in the parsed branch file.

See `episodes/04-full-model-auto-equilibria/outputs/task010/special_points.md` for the machine-generated catalogue.

## Stability and Hopf cross-check

At all labeled anchors from 10 km through 8.5 km, AUTO reports three stable eigenvalues and one positive real eigenvalue. The leading eigenvalue remains approximately

```text
lambda_crit = +2.38933e-4 s^-1 + 0 i
```

The independent Python finite-difference Jacobian gives the same leading real eigenvalue to the precision available in AUTO's diagnostic file. No complex-conjugate pair approaches the imaginary axis, so there is no Hopf candidate along this `z_W0` branch.

Mechanism diagnostics are also effectively constant across the target range:

```text
sigma_S + R_zeta ~= -1.2268e-4 m^-1
R ~= 9.2227e-3
growth balance residual ~= 0
k ~= 16.3426 s^-1
```

The branch is therefore a one-dimensional continuation of a state that is insensitive to the chosen control over this interval, not a Hopf-generating transition.

## Summary table

The generated summary table is checked in as `episodes/04-full-model-auto-equilibria/outputs/task010/summary_table.md`. It includes parameter value, equilibrium state, AUTO stability index, AUTO and Python critical eigenvalues, and PVLS mechanism diagnostics.

## Implication for follow-up tasks

For the first physical `z_W0` continuation, the full AUTO problem does not detect an LP/HB/BP in the Berton 10 km to 9 km interval. Follow-up searches should probe controls that change the local equilibrium conditions at `z*`, for example `W_a0`, humidity/radiation controls, eta blending, drag multiplier, or a reformulated updraft-control parameter that moves the updraft transition through the equilibrium altitude.
