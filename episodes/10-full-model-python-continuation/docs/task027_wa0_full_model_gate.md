# TASK-027 — full-model Python W_a0 continuation gate

TASK-027 applies the TASK-026 scaled Python pseudo-arclength continuation core to the full four-dimensional Berton equilibrium branch in `W_a0`. This is the conditioning/control sanity gate before attempting `H_a3` or `z_W0` Hopf-focused studies.

## Reproducibility command

```bash
uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task027_wa0_gate.py
```

Curated outputs are written to `episodes/10-full-model-python-continuation/outputs/task027/`.

## Gate result

The full-model continuation reached `W_a0=[0.099, 1.201]` m/s with `52` unique accepted control points. The maximum scaled residual norm is `2.508e-07` and the maximum physical RHS residual norm is `7.770e-10`. The largest branch Jacobian condition estimate is `1.484e+04`.

Accepted branch diagnostics include full-RHS residual norms, transformed/scaled residual norms, eigenvalues, tangent components, branch singular values, and Newton corrector histories.

## Comparison to previous probes

Against the previous TASK-012 Python `W_a0` probe, the maximum matched-anchor altitude discrepancy is `1.518e-08` m and the maximum relative mass discrepancy is `1.339e-12` over reachable comparison anchors.

Against the restricted TASK-019 behavior, the full-model branch agrees at the same anchors to maximum altitude discrepancy `3.213e-05` m and maximum relative mass discrepancy `2.722e-06`. The full model retains the explicit vertical-velocity coordinate, but the accepted gate stays on the same `w≈0` equilibrium geometry.

## Verdict

The W_a0 gate **passes**: full-model pseudo-arclength continuation reaches the required W_a0 anchors through 1.2 m/s with small residuals and reproduces prior W_a0 geometry
