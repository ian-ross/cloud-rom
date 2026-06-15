"""TASK-007: validate AUTO-07p on the reduced Berton 3D model.

This script cross-checks AUTO branch output from episodes/03-reduced-model-auto/auto/berton_reduced_3d
against the corrected cubic used in TASK-003/TASK-005.

It intentionally parses the saved AUTO ``b.*`` files, rather than relying on
screen output, so the validation note can cite stable artifacts.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

EPISODE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
CAS_SCRIPTS = REPO_ROOT / "episodes" / "02-reduced-model-cas" / "scripts"
if str(CAS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(CAS_SCRIPTS))

from berton_3d_hopf_task003_root_tracking import derive_slow_parameters

AUTO_DIR = EPISODE_ROOT / "auto" / "berton_reduced_3d"


@dataclass(frozen=True)
class AutoRow:
    branch: int
    point: int
    ty: int
    label: int
    active_value: float
    l2_norm: float
    zeta: float
    v: float
    r: float
    a0: float
    rh_residual: float
    hopf_alpha: float


def parse_auto_branch(path: Path, active_name: str) -> list[AutoRow]:
    """Parse numeric rows from an AUTO b.* output file for this problem."""

    rows: list[AutoRow] = []
    in_table = False
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "PT" in line and "TY" in line and "LAB" in line and active_name in line:
            in_table = True
            continue
        if not in_table:
            continue
        parts = line.split()
        if len(parts) != 12:
            continue
        try:
            rows.append(
                AutoRow(
                    branch=int(parts[0]),
                    point=int(parts[1]),
                    ty=int(parts[2]),
                    label=int(parts[3]),
                    active_value=float(parts[4]),
                    l2_norm=float(parts[5]),
                    zeta=float(parts[6]),
                    v=float(parts[7]),
                    r=float(parts[8]),
                    a0=float(parts[9]),
                    rh_residual=float(parts[10]),
                    hopf_alpha=float(parts[11]),
                )
            )
        except ValueError:
            continue
    if not rows:
        raise ValueError(f"No AUTO rows parsed from {path}")
    return rows


def corrected_quantities(k: float, alpha_grad: float, params) -> tuple[float, float, np.ndarray]:
    """Return a0, RH residual, and corrected cubic roots for possibly scaled d."""

    a = k * params.w_prime_per_s
    bcoef = 2.0 * k * params.beta_per_m_s * params.r_star_m
    c = params.c_per_s
    d = alpha_grad * params.d_per_s_per_m
    a2 = k + c
    a1 = k * c + a
    a0 = a * c - bcoef * d
    rh_residual = a2 * a1 - a0
    roots = np.roots([1.0, a2, a1, a0])
    return float(a0), float(rh_residual), roots


def stability_word(roots: np.ndarray, tol: float = 1.0e-8) -> str:
    max_real = float(np.max(np.real(roots)))
    if max_real < -tol:
        return "stable"
    if max_real > tol:
        return "unstable"
    return "hopf/marginal"


def run_auto() -> None:
    subprocess.run(["bash", str(AUTO_DIR / "run_auto.sh")], cwd=REPO_ROOT, check=True)


def validate(run_auto_first: bool = False) -> None:
    if run_auto_first:
        run_auto()

    params = derive_slow_parameters()
    k_rows = parse_auto_branch(AUTO_DIR / "b.bert3d-k", "k")
    alpha_rows = parse_auto_branch(AUTO_DIR / "b.bert3d-alpha", "alpha_grad")

    print("\nAUTO drag-rate continuation validation")
    print("k [s^-1]       AUTO a0        Python a0       AUTO RH        Python RH       max Re(lambda)  stability")
    for row in k_rows:
        k = row.active_value
        a0, rh, roots = corrected_quantities(k, 1.0, params)
        assert np.isclose(row.a0, a0, rtol=2.0e-6, atol=1.0e-12)
        assert np.isclose(row.rh_residual, rh, rtol=2.0e-6, atol=1.0e-10)
        max_real = float(np.max(np.real(roots)))
        if row.label != 0 or abs(k - params.model_k_per_s) < 1.0e-6:
            print(f"{k:11.6g}  {row.a0:13.6e}  {a0:13.6e}  {row.rh_residual:13.6e}  {rh:13.6e}  {max_real:+13.6e}  {stability_word(roots)}")
        assert stability_word(roots) == "stable"

    print("\nAUTO alpha_grad continuation validation")
    print("alpha          AUTO a0        Python a0       AUTO RH        Python RH       max Re(lambda)  stability  TY")
    hb_rows = [row for row in alpha_rows if abs(row.ty) == 3]
    assert hb_rows, "AUTO did not label a Hopf point (TY=HB/3) on alpha continuation"
    for row in alpha_rows:
        alpha = row.active_value
        a0, rh, roots = corrected_quantities(params.model_k_per_s, alpha, params)
        assert np.isclose(row.a0, a0, rtol=2.0e-6, atol=1.0e-12)
        assert np.isclose(row.rh_residual, rh, rtol=2.0e-6, atol=1.0e-10)
        max_real = float(np.max(np.real(roots)))
        if row.label != 0 or abs(row.ty) == 3:
            print(f"{alpha:11.6g}  {row.a0:13.6e}  {a0:13.6e}  {row.rh_residual:13.6e}  {rh:13.6e}  {max_real:+13.6e}  {stability_word(roots):>13}  {row.ty:3d}")

    expected_hopf_alpha = -params.model_k_per_s * (
        params.model_k_per_s * params.c_per_s
        + params.model_k_per_s * params.w_prime_per_s
        + params.c_per_s**2
    ) / ((2.0 * params.model_k_per_s * params.beta_per_m_s * params.r_star_m) * params.d_per_s_per_m)
    hb = hb_rows[0]
    print(f"\nAUTO Hopf alpha = {hb.active_value:.12e}")
    print(f"Python RH Hopf alpha = {expected_hopf_alpha:.12e}")
    print(f"AUTO diagnostic PAR(14) = {hb.hopf_alpha:.12e}")
    assert np.isclose(hb.active_value, expected_hopf_alpha, rtol=5.0e-8, atol=1.0e-6)
    assert abs(hb.rh_residual) < 1.0e-10
    assert any(row.rh_residual > 0.0 for row in alpha_rows if row.active_value < hb.active_value)
    assert any(row.rh_residual < 0.0 for row in alpha_rows if row.active_value > hb.active_value)

    print("\nValidation passed: AUTO diagnostics agree with the corrected Python cubic at matched branch points.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-auto", action="store_true", help="run AUTO before parsing saved b.* files")
    args = parser.parse_args()
    validate(run_auto_first=args.run_auto)


if __name__ == "__main__":
    main()
