from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.append(str(SCRIPTS))

from berton_3d_auto_task007_validate import AUTO_DIR, parse_auto_branch, validate


def test_task007_saved_auto_outputs_parse_expected_special_points() -> None:
    k_rows = parse_auto_branch(AUTO_DIR / "b.bert3d-k", "k")
    alpha_rows = parse_auto_branch(AUTO_DIR / "b.bert3d-alpha", "alpha_grad")

    assert any(abs(row.active_value - 100.0) < 1.0e-4 for row in k_rows)
    assert any(abs(row.active_value - 1000.0) < 1.0e-3 for row in k_rows)
    assert any(abs(row.active_value - 10000.0) < 1.0e-2 for row in k_rows)
    assert any(abs(row.ty) == 3 for row in alpha_rows)  # AUTO HB label


def test_task007_auto_outputs_match_corrected_python_cubic() -> None:
    validate(run_auto_first=False)
