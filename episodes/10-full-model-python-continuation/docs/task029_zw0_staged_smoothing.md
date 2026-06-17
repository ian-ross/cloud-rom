# TASK-029 — staged full-model Python z_W0 continuation

This episode-10 workflow follows the full Berton equilibrium branch in `z_W0` using Python pseudo-arclength continuation and the TASK-023/TASK-024 softplus-smoothed updraft.

## Reproducibility

```bash
uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task029_zw0_staged_smoothing.py
```

## Smoothing and physical mapping

The active coordinate is `q_z=(z_W0-9000 m)/1000 m`, with inverse `z_W0=9000 m + 1000 m q_z`. The updraft is `W_a0 * eps * (softplus(x/eps)-softplus((x-1)/eps))`, where `x=(z-(z_W0-Delta_z_W))/Delta_z_W`, `eps=width/Delta_z_W`, and `Delta_z_W=300 m`. The staged widths are `[300.0, 150.0, 100.0, 50.0]` m; the final width is the TASK-023/TASK-024 `50 m` setting.

## Coverage

The sharp 50 m stage covers `z_W0=[6999.500, 9929.955] m` with `48` unique accepted points. Full 7--10 km coverage: `False`. Transition-region accepted points in 9.6--10 km: `28`.

## Verdict

Classification: `smoothing_or_nonsmoothness_sensitive`. Easier smoothing widths reach farther than the 50 m width, so transition fragility remains smoothing-width/nonsmoothness sensitive.

The verdict is limited to accepted equilibrium branch points saved in `full_zw0_staged_branch_points.csv`; rejected corrector steps and conditioning diagnostics are saved separately.
