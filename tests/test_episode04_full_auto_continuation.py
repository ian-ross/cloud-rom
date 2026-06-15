from pathlib import Path
import sys

import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1] / "episodes" / "04-full-model-auto-equilibria" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.append(str(SCRIPTS))

import berton_full_auto_task010_analyze as task010


def test_task010_parses_branch_and_special_catalogue():
    bdf = task010.parse_b_file()
    assert {"z_W0", "sigma_plus_Rzeta", "driving_factor", "k"}.issubset(bdf.columns)
    assert bdf["z_W0"].max() >= 9999.0
    assert (bdf["z_W0"] <= 9000.1).any()

    specials = task010.catalogue_special_points(bdf, task010.branch_rows_with_cross_checks()[1])
    by_kind = specials.set_index("kind")
    assert by_kind.loc["LP", "status"] == "not detected"
    assert by_kind.loc["HB", "status"] == "not detected"
    assert by_kind.loc["BP", "status"] == "not detected"


def test_task010_labeled_solution_cross_checks_cover_berton_interval():
    _, sdf = task010.branch_rows_with_cross_checks()
    required = sdf[sdf["z_W0"].between(8499.0, 10001.0)]
    assert {10000.0, 9500.000003, 9000.0, 8500.0}.issubset(set(np.round(required["z_W0"], 6)))
    assert np.all(required["stable_count_auto"] == 3)
    assert np.all(required["critical_real_python"] > 0.0)
    assert np.allclose(required["critical_imag_python"], 0.0)
    assert np.nanmax(required["residual_norm_python"]) < 1e-7


def test_task010_outputs_exist_after_analysis():
    task010.write_outputs(run=False)
    out = Path("episodes/04-full-model-auto-equilibria/outputs/task010")
    for name in ["branch_points.csv", "labeled_solution_cross_checks.csv", "special_points.md", "summary_table.md", "branch_summary.png"]:
        assert (out / name).exists()
