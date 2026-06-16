#!/usr/bin/env bash
# Run TASK-015 log-mass full Berton equilibrium continuations from TASK-011 seed.
set -euo pipefail
cd "$(dirname "$0")"
auto <<'AUTOEOF'
clean()
ld('bertonfull_logm')
r=run(c='bertonfull-logm-wA0-plus')
sv(r,'task015-logm-wA0-plus')
r=run(c='bertonfull-logm-wA0-minus')
sv(r,'task015-logm-wA0-minus')
AUTOEOF
echo "saved AUTO outputs for TASK-015 log-mass W_a0 continuations"
