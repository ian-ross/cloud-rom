---
id: TASK-035
title: Fix Berton report plot scales
status: To Do
assignee: []
created_date: '2026-06-18 12:42'
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
