---
id: TASK-034
title: Publish Berton symbolic and continuation reports to website
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-18 12:20'
updated_date: '2026-06-18 12:20'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create final public-facing website content for the Berton 2023 symbolic and continuation phases. Add project/result articles, companion research-log process articles, transcript-only session imports, reusable collapsible details styling, and reproducible plot/data assets based on episodes 2-10 documentation and Pi session logs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Transcript-only import support exists for Pi sessions and relevant cloud-rom sessions are imported with descriptive transcript slugs.
- [ ] #2 A reusable MDX details component supports collapsible technical/process sections with variants.
- [ ] #3 Project pages cover the reduced-model symbolic treatment, AUTO continuation stress-test, and Python continuation final synthesis in chronological order for a non-specialist audience.
- [ ] #4 Research-log process coverage includes the revised symbolic log article and new AUTO/Python process articles with curated links to relevant transcript spans.
- [ ] #5 Project article plots/visualizations use reproducible website data assets, preferring Vega-Lite for normal plots and SVG for complex figures.
- [ ] #6 All authored pages are non-draft and the website build passes.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect website content schemas, existing project/log pages, session transcript routes, and episode 2-10 docs/outputs to inventory source material and plotting inputs.
2. Update the website add-log script/API to support a transcript-only mode that writes normalized session JSON without creating draft log MDX, then bulk-import relevant cloud-rom Pi sessions using descriptive slugs.
3. Add a reusable Details/AsideDetails MDX component with variants for math, reproducibility, process, and caution sections, using native details/summary semantics and site-consistent styling.
4. Create reproducible website data-generation assets for the three project pages from episode CSV/JSON outputs, preferring Vega-Lite JSON data for ordinary plots and SVG only if a complex figure needs it.
5. Write three non-draft project/result MDX pages in chronological order: reduced-model symbolic analysis, AUTO continuation stress-test, and Python continuation final synthesis/closure, with light transcript/process links.
6. Revise the existing symbolic research-log article and add AUTO/Python research-log articles, focusing on agent-process narrative and curated links to multiple transcript spans.
7. Run website tests/build, fix validation issues, then update TASK-034 acceptance criteria/final summary through Backlog CLI.
<!-- SECTION:PLAN:END -->
