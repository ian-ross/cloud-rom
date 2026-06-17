# TASK-016 full-system scaled H_a3 continuation verdict

TASK-016 retried the full 4D Berton equilibrium continuation after the restricted TASK-019/TASK-020 scaling work. The AUTO state starts exactly at the TASK-011/TASK-012 equilibrium seed and uses `Z=(z-z_seed)/1000`, `U=(u-u_seed)/5`, `W=w`, and `P=log(m/m_seed)/10`; the active control is `q_H=(H_a3-0.61)/0.001`. The physical inverse conversions are recorded in `outputs/task016/config_summary.csv` and in the AUTO source comments.

## Commands

```bash
bash episodes/08-full-model-auto-ha3/auto/berton_full_task016_ha3_scaled/run_auto.sh
uv run python episodes/08-full-model-auto-ha3/scripts/berton_full_task016_ha3_scaled.py
uv run pytest tests/test_episode08_full_task016.py
```

## AUTO result

Accepted H_a3 range: `0.610000` to `0.610000`. This range includes only the canonical seed value `0.61`; both requested directions were attempted, but AUTO did not accept a nontrivial full-system H_a3 branch. AUTO Hopf/HB label present: `False`. The upward direction retries through small q_H steps before NaN/DGEBAL/floating-point failure; the downward direction records only the seed plus MX/no movement.

Parsed convergence diagnostics include:

- `q-plus` line 2: Stable eigenvalues: 4
- `q-plus` line 29: 1     1 NOTE:Retrying step
- `q-plus` line 49: 1     1 NOTE:Retrying step
- `q-plus` line 69: 1     1 NOTE:Retrying step
- `q-plus` line 78: NOTE:Pivot   3 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 1.0566E-301 in GE
- `q-plus` line 79: NOTE:Pivot   4 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 1.0566E-301 in GE
- `q-plus` line 80: 1     2   5                NaN           NaN
- `q-plus` line 81: NOTE:Pivot   1 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 0.0000E+000 in GE
- `q-plus` line 82: NOTE:Pivot   2 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 0.0000E+000 in GE
- `q-plus` line 83: NOTE:Pivot   3 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 0.0000E+000 in GE
- `q-plus` line 84: NOTE:Pivot   4 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 0.0000E+000 in GE
- `q-plus` line 85: 1     2   6                NaN           NaN

## Independent Python cross-check

The representative accepted point(s) have Python full-RHS norm up to `2.132e-13` and stable eigenvalue count `4`. The critical real eigenvalue at the accepted seed is `-7.060e-06` s^-1, so the accepted point is locally stable in the independent Python finite-difference Jacobian. A separate finite-difference Python check at TASK-012 suspected crossing anchors (`outputs/task016/python_suspected_crossing_crosscheck.csv`) gives critical real parts from `-1.409e-05` to `2.104e-05` s^-1 over H_a3=0.600--0.650; this confirms the Python stability-sign hint but not an accepted AUTO crossing.

## Verdict

`H_a3` does **not** provide an AUTO-validated full-system Hopf candidate in this TASK-016 retry. The result is negative/inconclusive rather than a Hopf validation: the canonical seed is stable, the branch fails before reaching the Python-predicted `H_a3≈0.62` crossing region, and no HB label or independently cross-checked stability crossing is available from accepted full-system AUTO points. The restricted TASK-020 upward hint therefore remains a Python/restricted numerical hint only, not full-system AUTO evidence.
