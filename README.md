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

## Validation

Run the full test suite with:

```bash
uv run pytest
```

AUTO-dependent workflows use the installed AUTO-07p environment described in `AGENTS.md`.
