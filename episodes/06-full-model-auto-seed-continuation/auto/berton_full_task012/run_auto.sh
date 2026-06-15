#!/usr/bin/env bash
# Run TASK-012 full Berton equilibrium continuations from TASK-011 seed.
set -euo pipefail
cd "$(dirname "$0")"
auto <<'AUTOEOF'
clean()
ld('bertonfull')
r=run(c='bertonfull-wA0-plus')
sv(r,'task012-wA0-plus')
r=run(c='bertonfull-wA0-minus')
sv(r,'task012-wA0-minus')
r=run(c='bertonfull-Ha3-plus')
sv(r,'task012-Ha3-plus')
r=run(c='bertonfull-Ha3-minus')
sv(r,'task012-Ha3-minus')
AUTOEOF
echo "saved AUTO outputs for TASK-012 W_a0 and H_a3 continuations"
