#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
auto <<'AUTOEOF'
clean()
ld('bertonrestricted_task022_linear')
r=run(c='bertonrestricted-task022-linear-wA0-plus')
sv(r,'task022-linear-wA0-plus')
AUTOEOF
