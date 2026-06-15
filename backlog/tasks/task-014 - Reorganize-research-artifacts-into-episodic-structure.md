---
id: TASK-014
title: Reorganize research artifacts into episodic structure
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-15 12:03'
updated_date: '2026-06-15 12:03'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create episodes/ and references/ skeletons with README files reflecting agreed episode boundaries.
2. Move research artifacts from top-level docs/scripts/notebooks/auto/examples/outputs into the appropriate episode or references directories, removing empty functional directories and transient junk.
3. Update script imports, test path insertions, notebook references, docs, README, AGENTS.md, and .gitignore for the new layout.
4. Run repository-wide searches for stale old paths and repair intentional references.
5. Run the full test suite and relevant AUTO analysis command if path updates affect it.
6. Append migration notes to completed backlog tasks via CLI and mark TASK-014 acceptance criteria complete.
<!-- SECTION:PLAN:END -->
