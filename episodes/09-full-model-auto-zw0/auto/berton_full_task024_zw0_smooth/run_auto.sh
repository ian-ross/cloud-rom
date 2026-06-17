#!/usr/bin/env bash
# Run TASK-024 full scaled z_W0 continuations with smoothed updraft and q_z control.
set -euo pipefail
cd "$(dirname "$0")"
auto <<'AUTOEOF'
clean()
ld('bertonfull_task024_zw0_smooth')
r=run(c='bertonfull-task024-zw0-smooth-plus')
sv(r,'task024-full-zw0-smooth-plus')
r=run(c='bertonfull-task024-zw0-smooth-minus')
sv(r,'task024-full-zw0-smooth-minus')
AUTOEOF
echo "saved AUTO outputs for TASK-024 full smoothed z_W0 continuations"
