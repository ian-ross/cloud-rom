# TASK-024 full-system smoothed `z_W0` continuation verdict

## Setup

- AUTO formulation: full 4D Berton equilibrium with `Z=(z-z_seed)/1000`, `U=(u-u_seed)/5`, `W=w`, `P=log(m/m_seed)/10`.
- Control: `q_z=(z_W0-9000 m)/1000 m`.
- Updraft smoothing follows TASK-023: `W_a=W_a0*eps*(softplus(x/eps)-softplus((x-1)/eps))`, `x=(z-(z_W0-Delta_z_W))/Delta_z_W`, `eps=50/Delta_z_W=50/300`.
- Seed: TASK-011/TASK-012 canonical seed at `z≈9618.03 m`, `u≈1.90986 m/s`, `w=0`, `m≈1.08023e-9 kg`.

## Result

AUTO starts at the seed but does not accept a useful nontrivial full-system `z_W0` branch across the paper-relevant 7--10 km interval. The preserved diagnostics show early numerical failure rather than an HB/LP/BP-supported transition.

## Cross-checks

`python_full_eigenvalue_crosscheck.csv` evaluates independent finite-difference full-Jacobian eigenvalues at representative `z_W0` anchors, including 7 km and the 9.6--10 km transition region. These checks are diagnostics only because the corresponding points were not accepted AUTO branch points.

## Verdict

**Continued numerical inconclusiveness.** This is not AUTO-supported evidence for a full-system Hopf/oscillatory transition in `z_W0`, and it is also not a mathematically clean negative result over the desired range. Periodic-orbit continuation should not be attempted from TASK-024 without a better-conditioned full-system equilibrium parameterization or a staged seed near the smoothed ramp region.
