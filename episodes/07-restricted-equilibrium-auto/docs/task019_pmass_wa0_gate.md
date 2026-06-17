# TASK-019 P-scaled restricted W_a0 gate

TASK-019 implements the TASK-022 arclength fix for the restricted Berton equilibrium gate. The AUTO state is `Z=(z-z_seed)/100`, `U=(u-u_seed)/(1 m/s)`, and `P=M/10`, where `M=log(m/m_seed)`. Physical mass is reconstructed as `m=m_seed*exp(10P)`.

## Commands

```bash
bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task019_pmass/run_auto.sh
uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task019_pmass_wa0.py
```

Raw AUTO files are in `episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task019_pmass/`; curated outputs are in `episodes/07-restricted-equilibrium-auto/outputs/task019/`.

## Scaling and gate result

The older TASK-017/TASK-021 coordinate used `M=log(m/m_seed)` directly and failed at the first correction.  TASK-022 showed the local tangent was dominated by the mass direction, so this run uses `P=M/10` for AUTO arclength while preserving the same physical residual.

The upward W_a0 run accepted `257` branch rows, reached `W_a0=2.407`, and hit all user anchors through `W_a0=1.2`. The downward run accepted `21` branch rows and reached `W_a0=0.419` before its MX stop. The accepted altitude span over the upward gate was `382.273` m.

## Python comparison

The TASK-012 Python W_a0 probe is smooth and stable over `0.1`-`1.2` m/s. At matched user anchors, max absolute altitude error is `3.212e-05` m and max relative mass error is `2.722e-06`.

## Diagnostics

- `pmass-wA0-plus` line 37: 1     1         Iterations   :   2
- `pmass-wA0-plus` line 55: 1     2         Iterations   :   2
- `pmass-wA0-plus` line 73: 1     3         Iterations   :   2
- `pmass-wA0-plus` line 91: 1     4         Iterations   :   2
- `pmass-wA0-plus` line 109: 1     5         Iterations   :   2
- `pmass-wA0-plus` line 127: 1     6         Iterations   :   2
- `pmass-wA0-plus` line 146: 1     7         Iterations   :   3
- `pmass-wA0-plus` line 165: 1     8         Iterations   :   3

## Verdict

The restricted W_a0 gate **passes** with the `P=M/10` arclength coordinate.  This clears the way for TASK-020 to retry `H_a3` on the same fixed restricted formulation.  Do not reuse the older unscaled `M` coordinate for Hopf-control verdicts.
