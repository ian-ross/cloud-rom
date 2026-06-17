#!/usr/bin/env bash
# Run TASK-023 P-scaled restricted/scaled z_W0 continuations with smoothed updraft and q_z control.
set -euo pipefail
cd "$(dirname "$0")"
auto <<'AUTOEOF'
clean()
ld('bertonrestricted_task023_zw0_smooth')
r=run(c='bertonrestricted-task023-zw0-smooth-plus')
sv(r,'task023-zw0-smooth-plus')
r=run(c='bertonrestricted-task023-zw0-smooth-minus')
sv(r,'task023-zw0-smooth-minus')
AUTOEOF
echo "saved AUTO outputs for TASK-023 smoothed z_W0 continuations"
