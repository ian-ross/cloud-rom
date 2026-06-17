#!/usr/bin/env bash
# Run TASK-020 H-scaled restricted/scaled H_a3 continuations with q_H control.
set -euo pipefail
cd "$(dirname "$0")"
auto <<'AUTOEOF'
clean()
ld('bertonrestricted_task020_ha3_hscaled')
r=run(c='bertonrestricted-task020-ha3-hscaled-plus')
sv(r,'task020-ha3-hscaled-plus')
r=run(c='bertonrestricted-task020-ha3-hscaled-minus')
sv(r,'task020-ha3-hscaled-minus')
AUTOEOF
echo "saved AUTO outputs for TASK-020 H-scaled restricted H_a3 continuations"
