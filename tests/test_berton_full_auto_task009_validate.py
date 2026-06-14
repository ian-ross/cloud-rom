from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.append(str(SCRIPTS))

from berton_full_auto_task009_validate import S_FILE, validate


def test_task009_saved_auto_output_exists() -> None:
    assert S_FILE.exists()


def test_task009_fortran_rhs_and_auto_fixed_point_validate() -> None:
    validate(run_auto=False)
