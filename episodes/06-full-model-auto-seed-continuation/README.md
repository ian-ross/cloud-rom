# Episode 06 — Full-model AUTO seed continuation

This episode continues from the TASK-011 long-integration seed for canonical Berton Case 0.

TASK-011 classified the apparent oscillation as **damped/equilibrium-like**, so TASK-012 initializes equilibrium continuation from the exported late-time equilibrium rather than attempting periodic-orbit continuation.

Key files:

- `notebooks/task012_seed_continuation.ipynb` — TASK-012 notebook-first reproducibility entry point.
- `auto/berton_full_task012/` — TASK-012 AUTO-07p Fortran model, constants, and run script for `W_a0` and `H_a3` continuations from the TASK-011 seed.
- `scripts/berton_full_task012_seed_continuation.py` — TASK-012 parser/diagnostic script for saved AUTO outputs plus Python root-continuation sensitivity probe.
- `outputs/task012/` — TASK-012 curated seed review, AUTO summaries, eigenvalue diagnostics, convergence notes, and control-probe plot/table.
- `docs/task012_seed_continuation.md` — TASK-012 companion note with commands, diagnostics, and residual risks.
- `notebooks/task015_logm_reformulation.ipynb` — TASK-015 notebook record for the log-mass AUTO reformulation and retry.
- `auto/berton_full_task015/` — TASK-015 AUTO variant using `U(4)=log(m/kg)` and explicit derivative policy.
- `scripts/berton_full_task015_logm_continuation.py` — TASK-015 seed translation, transformed RHS/eigenvalue cross-check, AUTO parser, and TASK-012 comparison.
- `outputs/task015/` — TASK-015 seed cross-checks, AUTO summaries, convergence notes, and verdict JSON.
- `docs/task015_logm_reformulation.md` — TASK-015 companion note documenting scaling choices, commands, retry diagnostics, and residual risks.
- `docs/full_berton_dynamics_continuation_report.md` — TASK-013 synthesis report combining the negative `z_W0` Hopf screen, long-integration classification, continuation-from-seed results, reduced-model comparison, verdict, risks, and suggested next steps.
