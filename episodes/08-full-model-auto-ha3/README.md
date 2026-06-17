# Episode 08 — Full-model AUTO H_a3 retry

This episode contains TASK-016: a full 4D Berton equilibrium continuation retry for the humidity control `H_a3` after the restricted AUTO scaling work in episode 07.

Key artifacts:

- `auto/berton_full_task016_ha3_scaled/` — full-system AUTO formulation with scaled states `Z`, `U`, `W`, `P=log(m/m_seed)/10` and active `q_H=(H_a3-0.61)/0.001`.
- `scripts/berton_full_task016_ha3_scaled.py` — parser/synthesis script for AUTO outputs, independent Python eigenvalue checks, verdict JSON/CSV, and notebook record generation.
- `outputs/task016/` — curated branch summaries, convergence diagnostics, Python cross-checks, and verdict metadata.
- `docs/task016_full_ha3_scaled_verdict.md` — companion verdict note.
- `notebooks/task016_full_ha3_auto_record.ipynb` — notebook-style reproducibility record with AUTO path, constants, and commands.

Verdict: the full-system scaled `H_a3` retry starts at the TASK-011/TASK-012 seed but does not accept a nontrivial AUTO branch in either direction. No HB/Hopf label is present; `H_a3≈0.62` remains a Python/restricted hint only, not full-system AUTO evidence.
