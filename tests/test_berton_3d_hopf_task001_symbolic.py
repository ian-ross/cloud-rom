from __future__ import annotations

import importlib.util
from pathlib import Path

import sympy as sp


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "berton_3d_hopf_task001_symbolic.py"


def load_task001_module():
    spec = importlib.util.spec_from_file_location("berton_3d_hopf_task001_symbolic", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_task001_symbolic_derivation_assertions_pass():
    module = load_task001_module()

    result = module.derive_task001()

    assert sp.simplify(result["J_derived"] - result["J_reference"]) == sp.zeros(3, 3)
    assert sp.simplify(result["a0"] - result["a"] * result["c"] + result["b"] * result["d"]) == 0
