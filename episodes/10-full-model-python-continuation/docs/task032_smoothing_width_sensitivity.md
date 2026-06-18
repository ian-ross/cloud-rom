# TASK-032 — smoothing-width sensitivity map

TASK-032 treats updraft smoothing width as a scientific parameter rather than only a numerical staging aid.

## Reproducibility

```bash
uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task032_smoothing_width_map.py
```

## Coordinates

The fixed-z_W0 smoothing continuation uses `mu=log(width_m/50 m)`, with inverse `width_m=50*exp(mu)`. The z_W0 coordinate remains `q_z=(z_W0-9000 m)/1000 m`.

## Coverage

Fixed-z_W0 anchors: `[9600.0, 9700.0, 9800.0, 9900.0, 9930.0]` m. Width anchors: `[300.0, 200.0, 150.0, 100.0, 75.0, 50.0, 35.0, 25.0, 10.0]` m. Accepted fixed-z path points: `45`; accepted two-parameter map points: `61`.

## Geometry diagnostics

Minimum accepted fixed-control state-Jacobian singular value: `2.454e-03`. Maximum state-Jacobian condition: `1.216e+09`. Maximum width-branch condition: `1.616e+08`.

## Verdict

Classification: `near_singular_sharp_limit_not_50m_nonexistence`. Fixed-z_W0 solves reach the previously obstructed 50 m and sub-50 m region, so the TASK-029 z-continuation stop is not evidence of equilibrium nonexistence at 50 m; however conditioning grows sharply as the profile is further sharpened, supporting a near-singular smoothing-limit interpretation.

This verdict is limited to Newton-refined equilibrium points and pseudo-arclength-style width branch diagnostics; it does not by itself prove a global two-parameter bifurcation diagram.
