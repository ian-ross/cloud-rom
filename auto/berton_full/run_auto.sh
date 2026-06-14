#!/usr/bin/env bash
# Run the full Berton four-state equilibrium continuation.
# Usage from repository root: bash auto/berton_full/run_auto.sh
set -euo pipefail
cd "$(dirname "$0")"
cp c.bertonfull c.bertonfull.active
auto <<'EOF'
clean()
ld('bertonfull')
r=run(c='bertonfull')
sv(r,'bertfull-zW0')
EOF
echo "saved AUTO output b/s/d.bertfull-zW0"
