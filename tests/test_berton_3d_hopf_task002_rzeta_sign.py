from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import sympy as sp

from cloud_rom import berton2023 as b


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "berton_3d_hopf_task002_rzeta_sign.py"


def load_task002_module():
    spec = importlib.util.spec_from_file_location("berton_3d_hopf_task002_rzeta_sign", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("z_m", [8500.0, 9630.0, 9990.0])
def test_temperature_branch_matches_existing_atmosphere(z_m: float):
    module = load_task002_module()
    atm = b.atmosphere_for_case(0, oscillatory=True)
    z = sp.symbols("z")

    branch_value = float(module.temperature_branch_expr(z, atm).subs({z: z_m}))
    model_value = atm.temperature(b.Q_(z_m, "m")).to("K").magnitude

    assert branch_value == pytest.approx(model_value)


@pytest.mark.parametrize("z_m", [9000.0, 9630.0, 10000.0])
def test_eta_transition_branch_matches_existing_atmosphere(z_m: float):
    module = load_task002_module()
    atm = b.atmosphere_for_case(0, oscillatory=True)
    z = sp.symbols("z")

    branch_value = float(module.eta_transition_expr(z, atm).subs({z: z_m}))
    model_value = atm.atmospheric_eta(b.Q_(z_m, "m"))

    assert branch_value == pytest.approx(model_value)


@pytest.mark.parametrize("z_m", [5000.0, 9630.0, 10000.0])
def test_humidity_branch_matches_existing_atmosphere(z_m: float):
    module = load_task002_module()
    atm = b.atmosphere_for_case(0, oscillatory=True)
    z = sp.symbols("z")

    branch_value = float(module.humidity_branch_expr(z, atm).subs({z: z_m}))
    model_value = atm.relative_humidity_profile(b.Q_(z_m, "m"))

    assert branch_value == pytest.approx(model_value)


def test_task002_baseline_signs_are_finite_and_cross_checked():
    module = load_task002_module()

    result = module.derive_task002()

    assert result.R_zeta_per_m > 0.0
    assert result.sigma_plus_R_zeta_per_m < 0.0
    assert result.R_zeta_per_m == pytest.approx(result.finite_difference_R_zeta_per_m, rel=1e-9)
