---
id: TASK-035
title: Fix Berton report plot scales
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-18 12:42'
updated_date: '2026-06-18 12:42'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Correct plotting issues identified in the new Berton website reports: the AUTO damped-envelope plot renders no visible data, and the Python continuation z_W0 width-map plot uses an overly broad x-axis.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AUTO article damped-envelope plot displays the BDF/LSODA amplitude data clearly.
- [ ] #2 Python continuation z_W0 width-map plot x-axis focuses on the 9000-10000 m region of interest.
- [ ] #3 Website build passes after the plot fixes.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the Vega-Lite specs and generated JSON data for the affected plots.
2. Replace the AUTO damped-envelope log-scale bar mark with a log-compatible visible mark.
3. Constrain the Python z_W0 width-map x scale to the region of interest.
4. Run the website build and mark the task done.
<!-- SECTION:PLAN:END -->
