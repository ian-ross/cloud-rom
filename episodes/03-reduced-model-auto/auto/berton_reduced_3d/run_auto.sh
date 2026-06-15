#!/usr/bin/env bash
# Run AUTO-07p continuations for the reduced Berton 3D validation problem.
# Usage from repository root: bash episodes/03-reduced-model-auto/auto/berton_reduced_3d/run_auto.sh
set -euo pipefail
cd "$(dirname "$0")"

run_case() {
  local constants_file="$1"
  local output_name="$2"
  cp "$constants_file" c.berton3d
  auto <<EOF
clean()
ld('berton3d')
r=run()
sv(r,'$output_name')
EOF
  echo "saved AUTO output b/s/d.$output_name"
}

run_case c.berton3d.k bert3d-k
run_case c.berton3d.alpha bert3d-alpha
