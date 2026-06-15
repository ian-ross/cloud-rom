# Episode 06 — Full-model AUTO seed continuation

This episode continues from the TASK-011 long-integration seed for canonical Berton Case 0.

TASK-011 classified the apparent oscillation as **damped/equilibrium-like**, so TASK-012 initializes equilibrium continuation from the exported late-time equilibrium rather than attempting periodic-orbit continuation.

Key files:

- `notebooks/task012_seed_continuation.ipynb` — notebook-first reproducibility entry point.
- `auto/berton_full_task012/` — AUTO-07p Fortran model, constants, and run script for `W_a0` and `H_a3` continuations from the TASK-011 seed.
- `scripts/berton_full_task012_seed_continuation.py` — parser/diagnostic script for saved AUTO outputs plus Python root-continuation sensitivity probe.
- `outputs/task012/` — curated seed review, AUTO summaries, eigenvalue diagnostics, convergence notes, and control-probe plot/table.
- `docs/task012_seed_continuation.md` — companion note with commands, diagnostics, and residual risks.
