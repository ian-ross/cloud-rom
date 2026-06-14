"""TASK-003: track corrected Berton 3D Jacobian roots across drag rate.

This script is the cheap numerical cross-check requested by the Hopf-vs-saddle
briefing.  It holds the slow physical derivatives fixed at a Berton Case-0
oscillatory operating point, sweeps the drag relaxation rate k, and computes the
roots of the corrected characteristic polynomial

    lambda^3 + a2 lambda^2 + a1 lambda + a0

with

    a2 = k + c
    a1 = k*c + a
    a0 = a*c - b*d

where the corrected Jacobian is

    J = [[ 0,  1,  0],
         [-a, -k, -b],
         [-d,  0, -c]].

The baseline point is not obtained by integrating the full Berton ODE.  We use
the paper's limiting mass-equivalent diameter D_i ~= 131 um, then solve the
local reduced growth balance s(z*) = R(z*, r*) with the existing atmospheric,
thermodynamic, and radiative formulas.  The force balance then defines the
Stokes beta through W_a(z*) = beta*r*^2.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Callable

import numpy as np
from scipy.optimize import brentq

from cloud_rom import berton2023 as b

# Reuse the audited TASK-002 helper functions.  When this file is executed as a
# script, Python puts scripts/ on sys.path, so this sibling import works.
from berton_3d_hopf_task002_rzeta_sign import (  # noqa: E402
    central_difference,
    crystal_for_equivalent_diameter,
    sign_word,
    state_at,
    supersaturation_minus_one,
)


K_SWEEP: tuple[float, ...] = (1.0, 10.0, 100.0, 1000.0, 1.0e4)


def banner(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


@dataclass(frozen=True)
class SlowParameters:
    z_star_m: float
    r_star_m: float
    beta_per_m_s: float
    G_m2_per_s: float
    w_prime_per_s: float
    sigma_S_per_m: float
    R_r_per_m: float
    R_zeta_per_m: float
    c_per_s: float
    d_per_s_per_m: float
    eta_star: float
    R_star: float
    S_i_minus_one_star: float
    model_k_per_s: float


@dataclass(frozen=True)
class RootRow:
    k_per_s: float
    a2: float
    a1: float
    a0: float
    roots: tuple[complex, complex, complex]
    diagnosis: str


def growth_diffusivity_G(diag: b.LocalDiagnostics) -> float:
    """Return G in dr/dt = (G/r) * (S_i - 1 - R) at the local state.

    Existing Berton Eq. (10) gives dm/dt = 4*pi*C*f_v*drive/denominator.
    With m = 4/3*pi*r^3*rho_i, dr/dt = dm/dt/(4*pi*rho_i*r^2), hence
    G = C*f_v/(rho_i*r*denominator).
    """

    denominator = b.CONSTANTS.R_v * diag.T_a / (diag.p_vsi * diag.D_v) + b.CONSTANTS.L_s / (
        diag.K_a * diag.T_a
    ) * (b.CONSTANTS.L_s / (b.CONSTANTS.R_v * diag.T_a) - 1)
    G = diag.C * diag.f_v / (b.CONSTANTS.ρ_i * diag.r_i * denominator)
    return G.to("m^2/s").magnitude


def updraft_derivative(atm: b.Atmosphere, z_m: float) -> float:
    """Return dW_a/dz by a centered difference inside the local branch."""

    return central_difference(lambda zz: atm.updraft(b.Q_(zz, "m")).to("m/s").magnitude, z_m, 1.0)


def solve_growth_balance_z(atm: b.Atmosphere, crystal: b.Crystal, bracket_m: tuple[float, float]) -> float:
    """Solve s(z)-R(z,r*)=0 using existing LocalDiagnostics."""

    config = b.SimulationConfig(include_coriolis=False)

    def drive(z_m: float) -> float:
        diag = b.LocalDiagnostics.from_state(state_at(z_m, crystal), atm, config=config)
        return diag.S_i - 1.0 - diag.R

    return float(brentq(drive, bracket_m[0], bracket_m[1]))


def derive_slow_parameters() -> SlowParameters:
    """Derive and print all slow parameters used in the root sweep."""

    banner("Derive baseline fixed-point derivatives from the existing Berton model")
    atm = b.atmosphere_for_case(0, oscillatory=True)
    crystal = crystal_for_equivalent_diameter(131.0)
    z_star_m = solve_growth_balance_z(atm, crystal, (9500.0, 9700.0))
    config = b.SimulationConfig(include_coriolis=False)
    diag = b.LocalDiagnostics.from_state(state_at(z_star_m, crystal), atm, config=config)

    r_star_m = diag.r_i.to("m").magnitude
    W_star_mps = diag.W_a.to("m/s").magnitude
    beta = W_star_mps / r_star_m**2
    G = growth_diffusivity_G(diag)
    dW_dz = updraft_derivative(atm, z_star_m)
    w_prime = -dW_dz
    sigma_S = -central_difference(lambda zz: supersaturation_minus_one(zz, atm), z_star_m, 1.0)

    # Reduced radiative derivative: fixed crystal habit/geometry, r fixed for
    # zeta derivative.  Around z* this is equivalent to differentiating the
    # existing radiative_correction for the same crystal at nearby altitudes.
    def R_at_z(zz: float) -> float:
        return b.LocalDiagnostics.from_state(state_at(zz, crystal), atm, config=config).R

    R_zeta = central_difference(R_at_z, z_star_m, 1.0)
    R_r = diag.R / r_star_m
    c = (G / r_star_m) * R_r
    d = (G / r_star_m) * (sigma_S + R_zeta)

    params = SlowParameters(
        z_star_m=z_star_m,
        r_star_m=r_star_m,
        beta_per_m_s=beta,
        G_m2_per_s=G,
        w_prime_per_s=w_prime,
        sigma_S_per_m=sigma_S,
        R_r_per_m=R_r,
        R_zeta_per_m=R_zeta,
        c_per_s=c,
        d_per_s_per_m=d,
        eta_star=diag.η_a,
        R_star=diag.R,
        S_i_minus_one_star=diag.S_i - 1.0,
        model_k_per_s=diag.k.to("1/s").magnitude,
    )

    print("Provenance and values:")
    print("- Atmosphere: atmosphere_for_case(0, oscillatory=True); Case 0 eta_a(z), H_a3=0.61, W_a0=0.6 m/s.")
    print("- r*: D_i/2 with D_i=131 um, the paper's limiting mass-equivalent diameter.")
    print("- z*: solved local reduced growth balance s(z*) = R(z*, r*) using existing LocalDiagnostics.")
    print("- beta: force balance W_a(z*) = beta*r*^2, not an independent fit.")
    print("- G: converted from existing mass-growth law to dr/dt = (G/r)*(S_i-1-R).")
    print("- w_prime: -dW_a/dz from existing updraft profile; it is zero because z* is above the updraft ramp.")
    print("- sigma_S: -d(S_i-1)/dz from existing saturation thermodynamics.")
    print("- R_r: R/r from the reduced linear-in-r radiative form.")
    print("- R_zeta: finite difference of existing radiative_correction at fixed crystal geometry.")
    print(f"z*                         = {params.z_star_m:.12f} m")
    print(f"r*                         = {params.r_star_m:.12e} m")
    print(f"eta_a(z*)                  = {params.eta_star:.12e}")
    print(f"S_i(z*) - 1                = {params.S_i_minus_one_star:.12e}")
    print(f"R(z*, r*)                  = {params.R_star:.12e}")
    print(f"model instantaneous k      = {params.model_k_per_s:.12e} s^-1")
    print(f"beta                       = {params.beta_per_m_s:.12e} m^-1 s^-1")
    print(f"G                          = {params.G_m2_per_s:.12e} m^2 s^-1")
    print(f"w_prime = -dW_a/dz         = {params.w_prime_per_s:.12e} s^-1")
    print(f"sigma_S                    = {params.sigma_S_per_m:.12e} m^-1")
    print(f"R_r                        = {params.R_r_per_m:.12e} m^-1")
    print(f"R_zeta                     = {params.R_zeta_per_m:.12e} m^-1")
    print(f"sigma_S + R_zeta           = {params.sigma_S_per_m + params.R_zeta_per_m:.12e} m^-1")
    print(f"c = (G/r*) R_r             = {params.c_per_s:.12e} s^-1")
    print(f"d = (G/r*)(sigma+R_zeta)   = {params.d_per_s_per_m:.12e} s^-1 m^-1")
    print("Signs:")
    print(f"- R_r                      : {sign_word(params.R_r_per_m)}")
    print(f"- R_zeta                   : {sign_word(params.R_zeta_per_m)}")
    print(f"- sigma_S + R_zeta         : {sign_word(params.sigma_S_per_m + params.R_zeta_per_m)}")
    print(f"- d                        : {sign_word(params.d_per_s_per_m)}")

    assert abs(params.S_i_minus_one_star - params.R_star) < 1e-12
    assert params.r_star_m > 0.0
    assert params.beta_per_m_s > 0.0
    assert params.G_m2_per_s > 0.0
    return params


def corrected_coefficients(k_per_s: float, params: SlowParameters) -> tuple[float, float, float]:
    """Return corrected (a2, a1, a0) for the selected drag rate."""

    a = k_per_s * params.w_prime_per_s
    bcoef = 2.0 * k_per_s * params.beta_per_m_s * params.r_star_m
    c = params.c_per_s
    d = params.d_per_s_per_m
    a2 = k_per_s + c
    a1 = k_per_s * c + a
    a0 = a * c - bcoef * d
    return a2, a1, a0


def symbolic_jacobian(k_per_s: float, params: SlowParameters) -> np.ndarray:
    a = k_per_s * params.w_prime_per_s
    bcoef = 2.0 * k_per_s * params.beta_per_m_s * params.r_star_m
    c = params.c_per_s
    d = params.d_per_s_per_m
    return np.array([[0.0, 1.0, 0.0], [-a, -k_per_s, -bcoef], [-d, 0.0, -c]], dtype=float)


def classify_roots(a0: float, roots: np.ndarray) -> str:
    max_real = float(np.max(np.real(roots)))
    positive_roots = [root for root in roots if root.real > 1e-10]
    if a0 < 0.0 and positive_roots:
        return "SADDLE: a0<0 and at least one positive-real root"
    if max_real < 0.0 and a0 > 0.0:
        return "stable for this k; Hopf-capable sign structure (a0>0, no positive root)"
    if positive_roots:
        return "UNSTABLE: positive-real root despite a0>=0"
    return "marginal/ambiguous at printed precision"


def track_roots(params: SlowParameters, k_values: tuple[float, ...] = K_SWEEP) -> list[RootRow]:
    banner("Corrected coefficient and numpy.roots sweep")
    print(
        f"{'k [s^-1]':>10}  {'a2':>15}  {'a1':>15}  {'a0':>15}  "
        f"{'root 1':>28}  {'root 2':>28}  {'root 3':>28}  diagnosis"
    )
    rows: list[RootRow] = []
    for k_per_s in k_values:
        a2, a1, a0 = corrected_coefficients(k_per_s, params)
        roots = np.roots([1.0, a2, a1, a0])
        roots_sorted = tuple(sorted((complex(root) for root in roots), key=lambda z: (z.real, z.imag)))
        diagnosis = classify_roots(a0, roots)
        rows.append(RootRow(k_per_s, a2, a1, a0, roots_sorted, diagnosis))
        root_text = [f"{root.real:+.6e}{root.imag:+.6e}j" for root in roots_sorted]
        print(
            f"{k_per_s:10.3g}  {a2:15.8e}  {a1:15.8e}  {a0:15.8e}  "
            f"{root_text[0]:>28}  {root_text[1]:>28}  {root_text[2]:>28}  {diagnosis}"
        )

    banner("Plain-language root-tracking diagnosis")
    if all(row.a0 > 0 and max(root.real for root in row.roots) < 0.0 for row in rows):
        print("For the fixed slow parameters used here, every swept k has a0>0 and all root real parts are negative.")
        print("The cheap root check therefore does NOT show the corrected-Jacobian saddle outcome for this baseline.")
        print("Instead, the roots consist of one fast real root near -k and a slow stable complex pair.")
        print("This is Hopf-capable sign structure, but this sweep alone is not a Hopf bifurcation proof because no parameter is tuned through a crossing.")
    else:
        print("At least one swept k shows a positive-real root or non-positive a0; inspect the table above for saddle behavior.")

    return rows


def reduced_rhs(x: np.ndarray, k_per_s: float, params: SlowParameters) -> np.ndarray:
    """Reduced RHS linearized ingredients, but not using the Jacobian matrix directly.

    The local nonlinear functions are represented by their first-order fixed-point
    forms so the finite-difference Jacobian checks the corrected signs and
    coefficient placement independently of numpy.roots.
    """

    zeta, v, r = map(float, x)
    dz = zeta - params.z_star_m
    dr = r - params.r_star_m
    W_minus_V = -params.w_prime_per_s * dz - 2.0 * params.beta_per_m_s * params.r_star_m * dr
    drive = -(params.sigma_S_per_m + params.R_zeta_per_m) * dz - params.R_r_per_m * dr
    return np.array(
        [
            v,
            -k_per_s * (v - W_minus_V),
            (params.G_m2_per_s / r) * drive,
        ],
        dtype=float,
    )


def finite_difference_jacobian(
    f: Callable[[np.ndarray], np.ndarray], x0: np.ndarray, steps: np.ndarray
) -> np.ndarray:
    cols = []
    for i, h in enumerate(steps):
        xp = x0.copy()
        xm = x0.copy()
        xp[i] += h
        xm[i] -= h
        cols.append((f(xp) - f(xm)) / (2.0 * h))
    return np.column_stack(cols)


def compare_symbolic_and_fd_jacobian(params: SlowParameters, k_per_s: float | None = None) -> np.ndarray:
    banner("Finite-difference check of corrected symbolic Jacobian")
    if k_per_s is None:
        k_per_s = params.model_k_per_s
    x0 = np.array([params.z_star_m, 0.0, params.r_star_m], dtype=float)
    steps = np.array([1.0e-2, 1.0e-6, 1.0e-10], dtype=float)
    J_fd = finite_difference_jacobian(lambda xx: reduced_rhs(xx, k_per_s, params), x0, steps)
    J_sym = symbolic_jacobian(k_per_s, params)
    residual = J_fd - J_sym
    print(f"Using k = {k_per_s:.12e} s^-1 for Jacobian comparison")
    print("Symbolic corrected Jacobian:")
    print(J_sym)
    print("Finite-difference Jacobian from reduced RHS:")
    print(J_fd)
    print("FD - symbolic residual:")
    print(residual)
    max_abs = float(np.max(np.abs(residual)))
    print(f"max |residual| = {max_abs:.12e}")
    assert np.allclose(J_fd, J_sym, rtol=2e-8, atol=2e-8)
    return residual


def run_task003() -> tuple[SlowParameters, list[RootRow], np.ndarray]:
    params = derive_slow_parameters()
    rows = track_roots(params)
    residual = compare_symbolic_and_fd_jacobian(params)
    return params, rows, residual


if __name__ == "__main__":
    run_task003()
