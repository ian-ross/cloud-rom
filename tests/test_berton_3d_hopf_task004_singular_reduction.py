from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import sympy as sp


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
SCRIPT_PATH = SCRIPTS_DIR / "berton_3d_hopf_task004_singular_reduction.py"


def load_task004_module():
    sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location("berton_3d_hopf_task004_singular_reduction", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_route_a_extracts_k_independent_slow_quadratic():
    module = load_task004_module()
    result = module.route_a_cubic_expansion()
    s = module.symbols()
    lam, w, B, c, d, eps = (s[name] for name in ("lambda", "w", "B", "c", "d", "eps"))

    expected_q0 = lam**2 + (w + c) * lam + (w * c - B * d)
    expected_q1 = lam**3 + c * lam**2

    assert sp.simplify(result["q0"] - expected_q0) == 0
    assert sp.simplify(result["q1"] - expected_q1) == 0
    assert eps not in result["q0"].free_symbols
    assert result["det0"] == w * c - B * d


def test_route_b_includes_inertial_correction_matrix():
    module = load_task004_module()
    result = module.route_b_slow_fast_reduction()
    s = module.symbols()
    w, B, c, d = (s[name] for name in ("w", "B", "c", "d"))

    expected_M1 = sp.Matrix([[-(w**2 + B * d), -B * (w + c)], [0, 0]])
    assert sp.simplify(result["M1"] - expected_M1) == sp.zeros(2, 2)
    assert sp.simplify(result["h1"] - (-(w**2 + B * d) * sp.symbols("zeta") - B * (w + c) * sp.symbols("r"))) == 0


def test_route_a_and_route_b_reconcile_through_order_eps():
    module = load_task004_module()
    route_a = module.route_a_cubic_expansion()
    route_b = module.route_b_slow_fast_reduction()

    reconciliation = module.reconcile_routes(route_a, route_b)

    assert reconciliation["q0_difference"] == 0
    assert reconciliation["q1_remainder"] == 0
    assert reconciliation["mu1_diff_remainder"] == 0


def test_frequency_structure_is_k_free_and_has_expected_dominant_product():
    module = load_task004_module()
    route_a = module.route_a_cubic_expansion()
    frequency = module.berton_eq119_frequency_check(route_a)

    assert not any(str(sym) in {"k", "eps"} for sym in frequency["omega_primitive"].free_symbols)
    assert str(frequency["dominant_eq119_like"]) == "-2*G*beta*(R_zeta + sigma_S)"
