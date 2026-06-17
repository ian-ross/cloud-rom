#!/usr/bin/env bash
# Run TASK-021 minimal restricted/scaled W_a0 continuation diagnostic.
set -euo pipefail
cd "$(dirname "$0")"
auto <<'AUTOEOF'
clean()
ld('bertonrestricted_task021_minimal')
r=run(c='bertonrestricted-task021-minimal-wA0-plus')
sv(r,'task021-minimal-wA0-plus')
r=run(c='bertonrestricted-task021-minimal-wA0-minus')
sv(r,'task021-minimal-wA0-minus')
AUTOEOF
echo "saved AUTO outputs for TASK-021 minimal restricted/scaled W_a0 continuations"
