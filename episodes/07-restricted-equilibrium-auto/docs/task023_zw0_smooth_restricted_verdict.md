# TASK-023 smoothed restricted z_W0 continuation verdict

TASK-023 reuses the TASK-019 restricted 3D AUTO formulation: `Z=(z-z_seed)/100`, `U=(u-u_seed)/(1 m/s)`, `P=M/10`, row-scaled residuals, and `m=m_seed*exp(10P)`. The active control is `q_z=(z_W0-9000 m)/1000 m`, so physical `z_W0=9000+1000 q_z` metres.

## Smoothed updraft profile

The original Berton profile is `W_a(z)=W_a0*clip((z-(z_W0-Delta_z_W))/Delta_z_W,0,1)`. The smoothed profile used here is `W_a0*eps*[softplus(x/eps)-softplus((x-1)/eps)]`, where `x=(z-(z_W0-Delta_z_W))/Delta_z_W`, `softplus(y)=log(1+exp(y))`, and `eps=50 m / Delta_z_W = 0.166667`. This is the original ramp/plateau in the zero-width limit but removes the derivative jump at the ramp base and plateau transition.

## Commands

```bash
bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task023_zw0_smooth/run_auto.sh
uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task023_zw0_smooth.py
```

## AUTO result

The upward run accepted `22` rows and reached `z_W0=9710.2 m`, approaching the smoothed plateau transition at the seed before DGEBAL/floating-point failure. The downward run accepted `900` rows and reached at least the paper oscillatory `z_W0=7000 m` setting; the saved run continues farther to `z_W0=-35700.0 m` before MX. There is no HB label in the accepted branch output. The asymmetric result is physically interpretable: lowering z_W0 leaves the seed on a saturated plateau and barely perturbs the restricted equilibrium, while raising z_W0 moves the seed into the smoothed ramp/transition region.

## Python checks

At the TASK-011 seed the smoothing perturbation in W_a is `-4.274e-07 m/s` and the scaled residual norm is `1.320e-06`. Representative AUTO points have max Python smoothed scaled residual `1.320e-06`. Critical full finite-difference eigenvalue real parts span `-7.060e-06` to `1.704e-03` s^-1.

## Comparison and verdict

Compared with TASK-019 W_a0, the same `P=M/10` formulation again gives a meaningful branch in the easy direction. Compared with TASK-020 H_a3, the z_W0 upward direction still shows numerical fragility near a physically important profile transition, but smoothing makes that failure a branch/ramp-region limitation rather than an artificial derivative kink. The restricted experiment supports a full-system z_W0 attempt only in a staged way: first use the smoothed profile and scaled z_W0 control, and treat the 9.6--10 km transition region as the main risk rather than claiming an AUTO-supported Hopf.

## Diagnostics notes

- `z-plus` line 38: 1     1         Iterations   :   2
- `z-plus` line 56: 1     2         Iterations   :   1
- `z-plus` line 74: 1     3         Iterations   :   1
- `z-plus` line 93: 1     4         Iterations   :   2
- `z-plus` line 112: 1     5         Iterations   :   2
- `z-plus` line 131: 1     6         Iterations   :   2
- `z-plus` line 150: 1     7         Iterations   :   2
- `z-plus` line 169: 1     8         Iterations   :   2
- `z-plus` line 188: 1     9         Iterations   :   2
- `z-plus` line 237: 1    11         Iterations   :   2
