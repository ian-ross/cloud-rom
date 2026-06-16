# TASK-015 log-mass reformulation for full Berton AUTO seed continuation

## Commands

Notebook entry point:

```bash
# Open/run cells in:
episodes/06-full-model-auto-seed-continuation/notebooks/task015_logm_reformulation.ipynb
```

Equivalent non-interactive reproduction from the repository root:

```bash
bash episodes/06-full-model-auto-seed-continuation/auto/berton_full_task015/run_auto.sh
uv run python episodes/06-full-model-auto-seed-continuation/scripts/berton_full_task015_logm_continuation.py
```

## Reformulated coordinate

TASK-012 stored the fourth AUTO coordinate as a scaled mass, `U(4)=m/1e-9 kg`. TASK-015 replaces this with

```text
U(4) = log_m_kg = log(m / 1 kg)
m = exp(U(4)) kg
dU(4)/dt = m_dot / m
```

For the TASK-011 equilibrium seed this gives:

| quantity | value |
| --- | ---: |
| `z` | `9618.027532260936 m` |
| `u` | `1.9098623386953226 m/s` |
| `w` | `-2.9084536311763646e-21 m/s` |
| `m` | `1.0802293920592054e-9 kg` |
| `log(m/kg)` | `-20.646092418309163` |

The inverse conversion is documented in the AUTO source comments and in `outputs/task015/seed_logm_crosscheck.csv`.

## Derivatives and finite-difference justification

The new Fortran source is `auto/berton_full_task015/bertonfull_logm.f90`.

- `DFDU(1,3)=1` is supplied analytically for the kinematic equation `dz/dt=w`.
- The mass row uses the exact coordinate transform `d log(m)/dt = m_dot/m` in the RHS.
- Remaining `DFDU` entries are centered finite differences in the transformed variables with a fixed `1e-4` log-mass step. These pieces pass through profile interpolation, geometry root solves, drag correlations, saturation-vapor expressions, and radiation/growth diagnostics, so closed-form derivatives would be lengthy and fragile for this exploratory continuation task.
- `DFDP` is populated by centered differences for the active AUTO control/diagnostic parameters rather than left entirely absent. This is still finite-difference-based, but it makes the derivative policy explicit and tied to the reformulated RHS.

AUTO constants set `JAC=1`, `ITMX=20`, `ITNW=12`, `NWTN=6`, `DS=±0.001`, `DSMIN=1e-7`, and `DSMAX=0.02` for the `W_a0` first-step sanity check.

## Seed cross-check

Generated cross-checks:

- `outputs/task015/seed_logm_crosscheck.csv`
- `outputs/task015/seed_logm_python_eigenvalues.csv`

The transformed seed has small residuals and agrees with the physical-coordinate diagnostics:

| diagnostic | value |
| --- | ---: |
| physical RHS norm | `2.1506e-13` |
| transformed RHS norm | `2.0263e-13` |
| Fortran/Python transformed RHS max abs diff | `2.52e-16` |
| physical/transformed eigenvalues match | `True` |

The AUTO seed eigenvalues in `outputs/task015/auto_eigenvalue_diagnostics.csv` preserve the TASK-011/TASK-012 stable complex pair near `-7.0603e-6 ± 1.7121e-4 i s^-1`.

## First-step retry and TASK-012 comparison

TASK-015 retried `W_a0` in both directions:

- `task015-logm-wA0-plus`
- `task015-logm-wA0-minus`

Raw AUTO files are under `auto/berton_full_task015/`; parsed tables are under `outputs/task015/`.

| run | control | accepted non-MX points | accepted range | comparison |
| --- | --- | ---: | --- | --- |
| `logm-wA0-plus` | `W_a0` | 1 | `0.6` only | TASK-012 also accepted only the seed for `W_a0` |
| `logm-wA0-minus` | `W_a0` | 1 | `0.6` only | TASK-012 also accepted only the seed for `W_a0` |

The failure mode changed from the TASK-012 minimum-step-only diagnostic to a more severe Newton divergence: the first continuation correction produces large excursions, `NaN` iterates, pivot warnings, and an AUTO `DGEBAL` illegal-value message before any nontrivial point is accepted. The explicit comparison is saved in `outputs/task015/continuation_summary.csv`, including TASK-012 `W_a0` accepted-point counts and failure-reference text.

## Interpretation and residual risks

The log-mass coordinate satisfies the reformulation and seed-validation part of TASK-015, and it removes positivity/raw-mass scaling from the AUTO state. It does **not** by itself solve the first-step continuation problem. The residual numerical risk is now sharper: the limiting issue appears to involve the coupled Newton/pseudo-arclength system and derivative/scaling quality for the full microphysics, not merely the tiny physical mass coordinate.

Recommended follow-up before treating `H_a3` Hopf searches as AUTO-validated:

1. add a stronger state scaling for `z` and velocity equations, not only mass/log-mass;
2. consider radius as an alternative cloud-size coordinate with a smoother geometry derivative;
3. derive analytic derivatives for the local force/growth balance or build a reduced equilibrium system in `(z,u,log_m)` with `w=0` rather than continuing the full four-state ODE equilibrium directly;
4. retry `W_a0` as a conditioning sanity check before spending runs on `H_a3`.
