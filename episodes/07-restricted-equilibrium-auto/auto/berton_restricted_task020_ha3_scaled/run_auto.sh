#!/usr/bin/env bash
# Run TASK-020 P-scaled restricted/scaled H_a3 continuations with q_H control.
set -euo pipefail
cd "$(dirname "$0")"
auto <<'AUTOEOF'
clean()
ld('bertonrestricted_task020_ha3_scaled')
r=run(c='bertonrestricted-task020-ha3-q-plus')
sv(r,'task020-ha3-q-plus')
r=run(c='bertonrestricted-task020-ha3-q-minus')
sv(r,'task020-ha3-q-minus')
AUTOEOF
echo "saved AUTO outputs for TASK-020 scaled restricted H_a3 continuations"
