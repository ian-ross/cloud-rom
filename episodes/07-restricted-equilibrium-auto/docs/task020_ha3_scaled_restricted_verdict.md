# TASK-020 scaled restricted H_a3 verdict

TASK-020 reused the TASK-019 restricted 3D AUTO formulation after the W_a0 gate passed: `Z=(z-z_seed)/100`, `U=(u-u_seed)/(1 m/s)`, `P=M/10`, row-scaled residuals, and `m=m_seed*exp(10P)`. The active humidity control was scaled as `q_H=(H_a3-0.61)/0.001`. An exploratory larger-state-scale variant used `ZH=(z-z_seed)/1000` and `UH=(u-u_seed)/5` while preserving the same residual and `P` mass coordinate.

## Commands

```bash
bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task020_ha3_scaled/run_auto.sh
bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task020_ha3_hscaled/run_auto.sh
uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task020_ha3_scaled.py
```

## AUTO result

The trusted TASK-019-scale upward run accepted `10` rows and reached only `H_a3=0.610989` before DGEBAL/floating-point failure. The downward run accepted `34` rows and detected an LP at `H_a3=0.597113` before MX. No HB label was accepted in these AUTO files. The larger-state-scale retry failed at the seed in both directions, so it does not improve the verdict.

## Independent Python diagnostics

Representative accepted AUTO points have max scaled restricted residual `1.652e-09` under the Python residual. The full 4D finite-difference eigenvalue diagnostics over those points have critical real parts from `-8.473e-06` to `1.188e-04` s^-1. A separate Python restricted root continuation solves locally from `H_a3=0.600` through `0.625`, but fails below about `0.595` from this branch, consistent with the AUTO LP/fold indication rather than a clean Hopf crossing.

## Comparison to TASK-012/TASK-015

TASK-012's Python H_a3 probe reported a critical-pair sign change near `H_a3≈0.62`, but its saved equilibrium coordinates remain essentially at the seed for all H_a3 samples. The TASK-020 restricted branch instead moves altitude and horizontal velocity by hundreds of metres / metres per second over the same interval, so the TASK-012 probe is useful as a stability hint but not as branch geometry evidence. The direct full-4D TASK-012 AUTO H_a3 runs accepted only the seed; TASK-015 improved the mass coordinate for W_a0 but still documented first-step/full-formulation numerical fragility. TASK-020 improves on that by accepting a nontrivial restricted H_a3 branch in the downward direction, but not enough for an AUTO-supported Hopf claim.

## Diagnostics notes

- `q-plus` line 38: 1     1         Iterations   :   2
- `q-plus` line 57: 1     2         Iterations   :   2
- `q-plus` line 76: 1     3         Iterations   :   2
- `q-plus` line 95: 1     4         Iterations   :   2
- `q-plus` line 114: 1     5         Iterations   :   2
- `q-plus` line 133: 1     6         Iterations   :   2
- `q-plus` line 153: 1     7         Iterations   :   3
- `q-plus` line 173: 1     8         Iterations   :   3
- `q-plus` line 193: 1     9         Iterations   :   3
- `q-plus` line 205: NOTE:Pivot   2 = 0.0000E+000 <= ||A||_max/1.7977E+308 = 8.8293E-303 in GE

## Verdict

There is **no AUTO-supported Hopf candidate** from TASK-020. The restricted branch gives AUTO-supported evidence for a nearby H_a3 fold/turning limitation around `H_a3≈0.597`, while the upward Hopf-relevant side remains numerically inconclusive because AUTO stops near `H_a3≈0.611`. Treat any crossing near `0.62` as a Python hint only, not an AUTO-validated HB.
