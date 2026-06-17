#!/usr/bin/env bash
# Run TASK-019 P-scaled restricted/scaled W_a0 continuation gate.
set -euo pipefail
cd "$(dirname "$0")"
auto <<'AUTOEOF'
clean()
ld('bertonrestricted_task019_pmass')
r=run(c='bertonrestricted-task019-pmass-wA0-plus')
sv(r,'task019-pmass-wA0-plus')
r=run(c='bertonrestricted-task019-pmass-wA0-minus')
sv(r,'task019-pmass-wA0-minus')
AUTOEOF
echo "saved AUTO outputs for TASK-019 P-scaled restricted/scaled W_a0 continuations"
