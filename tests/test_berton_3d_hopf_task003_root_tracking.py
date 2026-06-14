from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
SCRIPT_PATH = SCRIPTS_DIR / "berton_3d_hopf_task003_root_tracking.py"


def load_task003_module():
    sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location("berton_3d_hopf_task003_root_tracking", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_slow_parameters_are_fixed_point_consistent():
    module = load_task003_module()

    params = module.derive_slow_parameters()

    assert params.z_star_m == pytest.approx(9618.062976835217)
    assert params.r_star_m == pytest.approx(6.55e-5)
    assert params.S_i_minus_one_star == pytest.approx(params.R_star, abs=1e-12)
    assert params.beta_per_m_s > 0.0
    assert params.G_m2_per_s > 0.0
    assert params.R_r_per_m > 0.0
    assert params.R_zeta_per_m > 0.0
    assert params.sigma_S_per_m + params.R_zeta_per_m < 0.0


def test_corrected_coefficients_match_jacobian_characteristic_polynomial():
    module = load_task003_module()
    params = module.derive_slow_parameters()
    k = 10.0

    a2, a1, a0 = module.corrected_coefficients(k, params)
    char = np.poly(module.symbolic_jacobian(k, params))

    assert char[0] == pytest.approx(1.0)
    assert char[1] == pytest.approx(a2)
    assert char[2] == pytest.approx(a1)
    assert char[3] == pytest.approx(a0)
    assert a0 > 0.0


def test_root_sweep_has_fast_root_and_stable_slow_pair():
    module = load_task003_module()
    params = module.derive_slow_parameters()

    rows = module.track_roots(params)

    assert [row.k_per_s for row in rows] == list(module.K_SWEEP)
    for row in rows:
        roots = np.array(row.roots)
        assert row.a0 > 0.0
        assert np.max(np.real(roots)) < 0.0
        assert np.min(np.real(roots)) == pytest.approx(-row.k_per_s, rel=1e-5, abs=1e-5)
        assert "Hopf-capable" in row.diagnosis


def test_finite_difference_jacobian_matches_symbolic_jacobian():
    module = load_task003_module()
    params = module.derive_slow_parameters()

    residual = module.compare_symbolic_and_fd_jacobian(params)

    assert np.max(np.abs(residual)) < 1e-4
