---
id: TASK-014
title: Reorganize research artifacts into episodic structure
status: To Do
assignee: []
created_date: '2026-06-15 12:03'
labels: []
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move research docs, scripts, notebooks, AUTO problems, examples, and curated outputs from functional top-level directories into episode directories that reflect the project research phases. Keep reusable source code and tests top-level, update imports/references, document the new structure, and add AGENTS.md guidance for future work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 episodes/ contains README-indexed episode directories for integration, reduced CAS, reduced AUTO, and full AUTO equilibria.
- [ ] #2 Existing research artifacts are moved into appropriate episode subdirectories with no compatibility copies left in old top-level functional dirs.
- [ ] #3 Tests and scripts use updated paths and the full test suite passes.
- [ ] #4 Top-level README and AGENTS.md document the episodic structure and future-agent guidance.
- [ ] #5 Backlog task notes for moved completed work include migration references to new episode paths.
- [ ] #6 Transient generated files are cleaned/ignored while curated outputs remain tracked.
<!-- AC:END -->
