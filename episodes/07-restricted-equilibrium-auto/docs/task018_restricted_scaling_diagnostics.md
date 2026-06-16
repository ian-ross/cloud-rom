# TASK-018 restricted 3D equilibrium scaling diagnostics

The restricted residual uses unknowns `(z, u, log_m)` with `w=0` and maps back to the full state as `(z, u, w, m) = (z, u, 0, exp(log_m))`. The three equations are `(du/dt, dw/dt, dlog(m)/dt)`.

## Seed cross-check

The TASK-011 seed residual norm in the full physical RHS is `2.151e-13`. The restricted residual norm is `2.026e-13`. The full-system eigenvalues remain stable and match the saved TASK-011 diagnostics within the CSV tolerances checked by the script.

## Conditioning verdict

The unscaled `(z,u,log_m)` restricted Jacobian condition estimate is `1.802e+08`. Using centered variables `Z=(z-z_seed)/100 m`, `U=(u-u_seed)/1 m s^-1`, and `M=log(m/m_seed)`, with residual scales from seed row norms, gives condition estimate `7.428e+00`.

## Recommendation for TASK-019

Proceed with the restricted system only in scaled coordinates and scaled residuals:

- AUTO states: `U(1)=Z=(z-z_seed)/100 m`, `U(2)=U=(u-u_seed)/(1 m/s)`, `U(3)=M=log(m/m_seed)`.
- Physical map: `z=z_seed+100*U(1)`, `u=u_seed+U(2)`, `w=0`, `m=m_seed*exp(U(3))`.
- Residuals: divide `(du/dt, dw/dt, dlogm/dt)` by the seed row-norm scales written in `scaling_recommendation.json`.
- Parameters: continue `W_a0` and `H_a3` in physical units but set AUTO step limits conservatively enough to avoid crossing the nearby 10 km humidity/eta kinks in one step.

This is not a claim that Hopf continuation is ready: the TASK-019 gate should first demonstrate a meaningful `W_a0` branch from the same scaled restricted residual.
