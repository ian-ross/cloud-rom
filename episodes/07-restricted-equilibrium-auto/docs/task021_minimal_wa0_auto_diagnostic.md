# TASK-021 minimal W_a0 AUTO diagnostic

This diagnostic strips the TASK-017 restricted/scaled equilibrium continuation to the smallest AUTO setup that still asks for continuation in `W_a0`. The task021 AUTO directory is separate from TASK-017 artifacts.  The AUTO state remains `Z_scaled`, `U_scaled`, `M_log_ratio` with `w=0`, but the active continuation list is only `ICP=['W_a0']`.

## Commands and raw artifacts

```bash
bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task021_minimal/run_auto.sh
uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task021_minimal_auto.py
```

Raw AUTO files are in `episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task021_minimal/` as `b./s./d.task021-minimal-wA0-{plus,minus}`. Curated CSV/JSON outputs are in `episodes/07-restricted-equilibrium-auto/outputs/task021/`.

## Minimal AUTO constants

- `ICP`: `['W_a0']` only; no TASK-017 diagnostic or PVLS parameters are active.
- `ISP=0`, `ILP=0`, `JAC=0`, `NPAR=53`.
- The Fortran `PVLS` callback is deliberately empty and `FUNC` supplies no analytic/user Jacobian, so the first run uses AUTO finite-difference Jacobians.

## Result

The two minimal directions printed `2` total branch rows and `0` non-seed rows. The accepted AUTO `W_a0` range remained `0.600`-`0.600` m/s; therefore no nontrivial point beyond `W_a0=0.6` was accepted.

First raw diagnostic lines:

- `minimal-wA0-plus` line 24: NOTE:Pivot   2 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 9.8051E-300 in GE
- `minimal-wA0-plus` line 25: NOTE:Pivot   3 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 9.8051E-300 in GE
- `minimal-wA0-plus` line 26: 1     2   5                NaN           NaN
- `minimal-wA0-plus` line 27: NOTE:Pivot   1 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 0.0000E+000 in GE
- `minimal-wA0-plus` line 28: NOTE:Pivot   2 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 0.0000E+000 in GE
- `minimal-wA0-plus` line 29: NOTE:Pivot   3 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 0.0000E+000 in GE
- `minimal-wA0-plus` line 30: 1     2   6                NaN           NaN
- `minimal-wA0-plus` line 31: NOTE:Pivot   1 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 0.0000E+000 in GE
- `minimal-wA0-plus` line 32: NOTE:Pivot   2 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 0.0000E+000 in GE
- `minimal-wA0-plus` line 33: NOTE:Pivot   3 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 0.0000E+000 in GE

## Comparison

TASK-017 also accepted only the seed (`W_a0=0.600`-`0.600`, nontrivial points `0`). In contrast, the TASK-012 Python W_a0 probe successfully follows stable equilibria from `0.1` to `1.2` m/s with altitude span `55.473` m.

## Interpretation

**Verdict:** failure persists in stripped configuration; not solely diagnostic/PVLS/supplied-Jacobian bookkeeping

Because the failure persists after removing diagnostic ICP entries, PVLS bookkeeping, and supplied Jacobians, the observed first-step divergence is unlikely to be caused solely by TASK-017 diagnostic metadata/PVLS/Jacobian bookkeeping. The remaining culprit is more likely the AUTO algebraic continuation formulation/scaling/initial tangent setup for this restricted problem, despite the underlying Python equilibrium branch being smooth and stable.
