#!/usr/bin/env bash
# Run TASK-017 restricted/scaled W_a0 continuation sanity check.
set -euo pipefail
cd "$(dirname "$0")"
auto <<'AUTOEOF'
clean()
ld('bertonrestricted_task017')
r=run(c='bertonrestricted-task017-wA0-plus')
sv(r,'task017-restricted-wA0-plus')
r=run(c='bertonrestricted-task017-wA0-minus')
sv(r,'task017-restricted-wA0-minus')
AUTOEOF
echo "saved AUTO outputs for TASK-017 restricted/scaled W_a0 continuations"
