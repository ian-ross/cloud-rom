from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import sympy as sp


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "episodes" / "02-reduced-model-cas" / "scripts"
SCRIPT_PATH = SCRIPTS_DIR / "berton_3d_hopf_task005_classification.py"


def load_task005_module():
    sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location("berton_3d_hopf_task005_classification", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_symbolic_relations_state_corrected_hopf_locus_and_determinant():
    module = load_task005_module()
    relations = module.symbolic_relations()

    k, B, c, d, w = sp.symbols("k B c d w")
    expected_hopf_residual = k * (B * d + c**2 + c * k + k * w)

    assert str(relations["hopf_locus_residual"]) == str(expected_hopf_residual)
    assert str(relations["det_2d"]) == "-B*d + c*w"
    assert relations["briefing_det_residual"] != 0
    assert "r_star**2" in str(relations["briefing_det_candidate"])
    assert "r_star**2" not in str(relations["corrected_det_primitive"])


def test_baseline_classification_is_hopf_capable_stable_spiral():
    module = load_task005_module()

    params = module.derive_slow_parameters()
    rows = module.track_roots(params)
    classification = module.classify(params, rows)

    assert classification.sigma_plus_Rzeta < 0.0
    assert classification.d < 0.0
    assert classification.determinant_2d > 0.0
    assert classification.a0_at_model_k > 0.0
    assert classification.rh_residual_at_model_k > 0.0
    assert classification.all_swept_roots_stable is True
    assert classification.verdict.startswith("HOPF-CAPABLE STABLE SPIRAL")


def test_root_evidence_has_no_positive_real_part_for_swept_k():
    module = load_task005_module()

    params = module.derive_slow_parameters()
    rows = module.track_roots(params)
    classification = module.classify(params, rows)

    assert [k for k, _ in classification.max_root_real_by_k] == list(module.K_SWEEP)
    for _k, max_real in classification.max_root_real_by_k:
        assert max_real < 0.0
    for row in rows:
        assert row.a0 > 0.0
        assert "Hopf-capable" in row.diagnosis


def test_frequency_structure_reports_k_free_eq119_like_term():
    module = load_task005_module()

    classification = module.classify()

    assert not any(str(sym) in {"k", "eps"} for sym in classification.omega0_squared_expr.free_symbols)
    assert str(classification.eq119_like_expr) == "-2*G*beta*(R_zeta + sigma_S)"
