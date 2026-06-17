#!/usr/bin/env bash
# Run TASK-016 full scaled H_a3 continuations from TASK-011/TASK-012 seed.
set -euo pipefail
cd "$(dirname "$0")"
auto <<'AUTOEOF'
clean()
ld('bertonfull_task016_ha3_scaled')
r=run(c='bertonfull-task016-ha3-q-plus')
sv(r,'task016-full-ha3-q-plus')
r=run(c='bertonfull-task016-ha3-q-minus')
sv(r,'task016-full-ha3-q-minus')
AUTOEOF
echo "saved AUTO outputs for TASK-016 full scaled H_a3 continuations"
