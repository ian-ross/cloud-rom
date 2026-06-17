# cloud-rom

This repository contains a reusable Python implementation of the Berton (2023) cirrus parcel model plus episodic research workflows that analyze that model.

## Repository map

- `src/cloud_rom/` — reusable package code.
- `tests/` — repository-level pytest suite.
- `episodes/` — research artifacts organized by project episode rather than by file type.
- `references/` — source/reference material used across episodes.
- `backlog/` — Backlog.md task tracking metadata.

## Episodes

See `episodes/README.md` for the detailed index.

1. `episodes/01-berton2023-integration/` — numerical integrator, extraction notes, and replication notebooks for the Berton (2023) model.
2. `episodes/02-reduced-model-cas/` — symbolic/CAS and reduced-model Hopf mechanism analysis.
3. `episodes/03-reduced-model-auto/` — AUTO-07p validation on the reduced 3D model.
4. `episodes/04-full-model-auto-equilibria/` — full-model AUTO equilibrium continuation and failed Hopf search.
5. `episodes/05-full-model-oscillatory-orbit/` — long-integration classification of the canonical full-model apparent oscillation.
6. `episodes/06-full-model-auto-seed-continuation/` — full-model AUTO seed continuation attempts in `W_a0` and `H_a3`.
7. `episodes/07-restricted-equilibrium-auto/` — restricted/local equilibrium AUTO continuation and conditioning work.
8. `episodes/08-full-model-auto-ha3/` — scaled full-model AUTO `H_a3` retry.
9. `episodes/09-full-model-auto-zw0/` — smoothed full-model AUTO `z_W0` retry.
10. `episodes/10-full-model-python-continuation/` — Python-continuation-first full-model investigation, with AUTO reserved for final validation.

## Validation

Run the full test suite with:

```bash
uv run pytest
```

AUTO-dependent workflows use the installed AUTO-07p environment described in `AGENTS.md`.
