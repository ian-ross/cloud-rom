# TASK-007 AUTO-07p validation for the reduced Berton 3D model

## Scope

This note validates AUTO-07p on the already-audited reduced Berton 3D fixed-point model before porting the full Berton system.  The AUTO problem is in:

- `auto/berton_reduced_3d/berton3d.f90`
- `auto/berton_reduced_3d/c.berton3d.k`
- `auto/berton_reduced_3d/c.berton3d.alpha`
- `auto/berton_reduced_3d/run_auto.sh`

The validation/cross-check script and reproducibility notebook are:

- `scripts/berton_3d_auto_task007_validate.py`
- `notebooks/berton_3d_auto_task007_validation.ipynb`

## State and parameter definitions

AUTO state variables are the reduced fixed-point variables:

```text
U(1) = zeta [m]
U(2) = v    [m/s]
U(3) = r    [m]
```

The Fortran problem uses these continuation parameters:

```text
PAR(1) = k              drag relaxation rate [s^-1]
PAR(2) = alpha_grad     multiplier on sigma_S + R_zeta [-]
PAR(3) = zeta_star      9618.062976835217 m
PAR(4) = r_star         6.55e-5 m
PAR(5) = beta           1.398519899773e8 m^-1 s^-1
PAR(6) = G              3.568753045458e-12 m^2 s^-1
PAR(7) = w_prime        0 s^-1 for this baseline
PAR(8) = R_r            33.69976459537 m^-1
PAR(9) = sigma_plus_Rz  -5.640219674712e-5 m^-1
```

`PVLS` records diagnostic output parameters:

```text
PAR(10) = c = (G/r_star) R_r
PAR(11) = d = (G/r_star) alpha_grad (sigma_S + R_zeta)
PAR(12) = a0
PAR(13) = a2*a1 - a0, the Routh-Hurwitz Hopf residual
PAR(14) = analytic alpha_grad at the Hopf residual zero
```

The RHS is the same local reduced model used for TASK-003 finite-difference checks:

```text
zeta_dot = v
v_dot    = -k * (v - (W_a(zeta) - V_f(r)))
r_dot    = (G/r) * (s(zeta) - R(zeta,r))
```

with first-order local ingredients

```text
W_a - V_f ~= -w_prime*(zeta-zeta*) - 2*beta*r_star*(r-r*)
s - R     ~= -alpha_grad*(sigma_S+R_zeta)*(zeta-zeta*) - R_r*(r-r*)
```

## Commands run

AUTO is available as `/usr/local/bin/auto`; the Python interface requires adding `/usr/local/lib64/auto-07p/python` to `sys.path` if used from scripts/notebooks.

From the repository root:

```bash
bash auto/berton_reduced_3d/run_auto.sh
uv run python scripts/berton_3d_auto_task007_validate.py
uv run pytest tests/test_berton_3d_auto_task007_validate.py
# Optional notebook-driven reproduction/plotting:
# jupyter notebook notebooks/berton_3d_auto_task007_validation.ipynb
```

The run script saves these AUTO files, which were inspected by the validation script:

```text
auto/berton_reduced_3d/b.bert3d-k
auto/berton_reduced_3d/s.bert3d-k
auto/berton_reduced_3d/d.bert3d-k
auto/berton_reduced_3d/b.bert3d-alpha
auto/berton_reduced_3d/s.bert3d-alpha
auto/berton_reduced_3d/d.bert3d-alpha
```

## Results

### Drag-rate continuation

`c.berton3d.k` continues the baseline equilibrium in `k` with `alpha_grad=1`.  AUTO keeps the same fixed point and records positive `a0` and positive Routh-Hurwitz residual at matched branch points.  The Python validation script recomputes the corrected cubic roots at the AUTO branch points; all parsed drag-rate points are stable.  Representative matched points:

| k [s^-1] | AUTO a0 | Python a0 | AUTO RH residual | Python max Re(lambda) |
|---:|---:|---:|---:|---:|
| 21.6488 | 1.218837e-06 | 1.218837e-06 | 8.593216e-04 | -9.167618e-07 |
| 100 | 5.630036e-06 | 5.630036e-06 | 1.835561e-02 | -9.177806e-07 |
| 1000 | 5.630036e-05 | 5.630036e-05 | 1.836068e+00 | -9.180340e-07 |
| 10000 | 5.630036e-04 | 5.630036e-04 | 1.836119e+02 | -9.180593e-07 |

This agrees with the TASK-003/TASK-005 conclusion that the baseline fixed slow parameters are a stable Hopf-capable spiral, not a saddle.

### Mechanism-parameter continuation and Hopf diagnostic

`c.berton3d.alpha` continues `alpha_grad`, a multiplier on the destabilizing negative `sigma_S + R_zeta` feedback, at the model drag rate.  AUTO detects a Hopf point (`TY=HB`, numeric type `3`) where the recorded Routh-Hurwitz residual crosses zero.

Matched validation output:

```text
AUTO Hopf alpha       = 7.060338617400e+02
Python RH Hopf alpha  = 7.060338636100e+02
AUTO diagnostic PAR14 = 7.060338636100e+02
```

Below this value (`alpha_grad=1, 100, 500`), Python roots have negative maximum real part.  Above it (`alpha_grad=800, 900`), the complex pair has positive real part.  The AUTO Hopf label, AUTO `PAR(13)` residual, and Python corrected cubic roots therefore identify the same stability change.

## Discrepancies and limitations

- No numerical discrepancies were found at the tolerances in `scripts/berton_3d_auto_task007_validate.py`; AUTO `a0` and `a2*a1-a0` match the Python corrected cubic at parsed branch points.
- The reduced model is intentionally local and first-order.  The equilibrium remains fixed while `k` or `alpha_grad` changes, so this validates AUTO setup, Jacobian signs, stability diagnostics, and Hopf detection, not the full Berton trajectory physics.
- The `alpha_grad` continuation is a mechanism probe, not a directly measured Berton control parameter.  It is useful because the analytic Hopf residual predicts a precise crossing for AUTO to detect.
