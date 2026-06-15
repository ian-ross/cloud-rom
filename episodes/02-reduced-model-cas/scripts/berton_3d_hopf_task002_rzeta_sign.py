"""TASK-002: derive and evaluate the sign of R_zeta for Berton (2023).

This script audits the pivotal derivative in the reduced 3D Hopf-or-saddle
analysis:

    R(z, r) = Phi(T(z)) * (eta_a(z) - 1) * r

with Berton's piecewise-linear temperature, humidity, and infrared-ratio
profiles.  It prints the symbolic derivative and then evaluates R_zeta and
sigma_S + R_zeta at the Case-0 oscillatory operating point used in the paper
(z_infty ~= 9.63 km, D_i,infty ~= 131 um).

The numerical evaluation deliberately reuses constants and profile formulas from
src/cloud_rom/berton2023.py, while keeping the reduced radiative term linear in
r as required by the briefing.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Any

import sympy as sp

from cloud_rom import berton2023 as b


def banner(title: str) -> None:
    print("\n" + "=" * 88)
    print(title)
    print("=" * 88)


def show(label: str, expr: Any) -> None:
    print(f"\n{label}:")
    sp.pprint(expr, use_unicode=True)


def sign_word(x: float, *, tol: float = 1e-14) -> str:
    if x > tol:
        return "POSITIVE"
    if x < -tol:
        return "NEGATIVE"
    return "ZERO/AMBIGUOUS"


@dataclass(frozen=True)
class Task002Result:
    z_star_m: float
    r_star_m: float
    eta_star: float
    R_zeta_per_m: float
    sigma_S_per_m: float
    sigma_plus_R_zeta_per_m: float
    finite_difference_R_zeta_per_m: float
    finite_difference_sigma_S_per_m: float


def temperature_branch_expr(z_m: sp.Symbol, atm: b.Atmosphere) -> sp.Expr:
    """T(z) for the 8--14 km branch of Eqs. (75)--(76), in kelvin."""

    z_T2 = atm.z_T2.to("m").magnitude
    z_T3 = atm.z_T3.to("m").magnitude
    T2 = atm.T_a2.to("K").magnitude
    T3 = atm.T_a3.to("K").magnitude
    return sp.Float(T2) + sp.Float((T3 - T2) / (z_T3 - z_T2)) * (z_m - sp.Float(z_T2))


def eta_transition_expr(z_m: sp.Symbol, atm: b.Atmosphere) -> sp.Expr:
    """eta_a(z) for the 9--10 km transition branch of Eqs. (80)--(81)."""

    z0 = atm.z_η0.to("m").magnitude
    z1 = atm.z_η1.to("m").magnitude
    eta0 = atm.η_a0
    eta1 = atm.η_a1
    return sp.Float(eta0) + sp.Float((eta1 - eta0) / (z1 - z0)) * (z_m - sp.Float(z0))


def humidity_branch_expr(z_m: sp.Symbol, atm: b.Atmosphere) -> sp.Expr:
    """H_l(z) for the 4--10 km branch of Eqs. (78)--(79)."""

    z2 = atm.z_H2.to("m").magnitude
    z3 = atm.z_H3.to("m").magnitude
    H2 = atm.H_a2
    H3 = atm.H_a3
    return sp.Float(H2) + sp.Float((H3 - H2) / (z3 - z2)) * (z_m - sp.Float(z2))


def validate_baseline_branches(z_m_value: float, atm: b.Atmosphere) -> None:
    """Assert and print the branch assumptions used for the baseline point."""

    z_km = z_m_value / 1000.0
    print(f"Baseline z*: {z_m_value:.3f} m = {z_km:.5f} km")
    print("Branch assumptions:")
    print("- T(z): 8--14 km linear layer (Eqs. 75--76)")
    print("- eta_a(z): 9--10 km linear transition layer (Eqs. 80--81)")
    print("- H_l(z): 4--10 km linear layer (Eqs. 78--79), Case 0 H_a3=0.61")
    assert atm.z_T2.to("m").magnitude <= z_m_value <= atm.z_T3.to("m").magnitude
    assert atm.z_η0.to("m").magnitude <= z_m_value <= atm.z_η1.to("m").magnitude
    assert atm.z_H2.to("m").magnitude <= z_m_value <= atm.z_H3.to("m").magnitude


def crystal_for_equivalent_diameter(D_i_um: float) -> b.Crystal:
    """Create a fixed-shape Case-0 crystal with the requested equivalent diameter."""

    constants = b.CONSTANTS
    D = b.Q_(D_i_um, "micrometer").to("m")
    volume = (pi / 6.0 * D**3).to("m^3")
    mass = (constants.ρ_i * volume).to("kg")
    return b.Crystal(m=mass, φ=2.0, c_B=b.Q_(20.44, "micrometer"))


def state_at(z_m: float, crystal: b.Crystal) -> b.State:
    return b.State(
        t=b.Q_(0.0, "s"),
        x=b.Q_(0.0, "m"),
        z=b.Q_(z_m, "m"),
        u=b.Q_(0.0, "m/s"),
        w=b.Q_(0.0, "m/s"),
        crystal=crystal,
    )


def supersaturation_minus_one(z_m: float, atm: b.Atmosphere) -> float:
    """Return s(z)=S_i(z)-1 using the existing Berton thermodynamics."""

    z = b.Q_(z_m, "m")
    T = atm.temperature(z)
    p_a = b.dry_air_pressure(z)
    H_l = atm.relative_humidity_profile(z)
    p_vsl = b.saturation_pressure_liquid(T)
    p_vsi = b.saturation_pressure_ice(T)
    p_v = b.water_vapor_pressure_from_Hl(H_l, p_a, p_vsl)
    _, S_i = b.saturation_ratios(p_v, p_vsl, p_vsi)
    return float(S_i - 1.0)


def central_difference(f, x: float, h: float) -> float:
    return (f(x + h) - f(x - h)) / (2.0 * h)


def derive_task002() -> Task002Result:
    banner("Symbolic closed-form derivative of R(z, r)")

    z, r = sp.symbols("z r", real=True)
    T = sp.Function("T")
    eta_a = sp.Function("eta_a")
    Phi = sp.Function("Phi")

    R = Phi(T(z)) * (eta_a(z) - 1) * r
    R_zeta = sp.diff(R, z)
    show("Closed-form reduced radiative term R(z, r)", R)
    show("General derivative R_zeta = dR/dz", R_zeta)

    banner("Substitute Berton profile branches symbolically")
    atm = b.atmosphere_for_case(0, oscillatory=True)
    z_m = sp.symbols("z_m", real=True)
    T_branch = temperature_branch_expr(z_m, atm)
    eta_branch = eta_transition_expr(z_m, atm)
    H_branch = humidity_branch_expr(z_m, atm)
    show("T(z) branch, 8--14 km [K]", T_branch)
    show("dT/dz on branch [K/m]", sp.diff(T_branch, z_m))
    show("eta_a(z) branch, 9--10 km", eta_branch)
    show("d eta_a/dz on branch [1/m]", sp.diff(eta_branch, z_m))
    show("H_l(z) branch, 4--10 km", H_branch)
    show("dH_l/dz on branch [1/m]", sp.diff(H_branch, z_m))

    # Thermal part of Phi.  The positive geometry factor A/(4*pi*C*r) is
    # evaluated from the baseline crystal below.  K_a(T) follows Eq. (15), as in
    # berton2023.heat_conductivity_air.
    gamma, sigma_SB, L_s, R_v = sp.symbols("gamma sigma_SB L_s R_v", positive=True)
    T_sym = sp.symbols("T", positive=True)
    K_a = sp.Float(2.42e-2) * (sp.Float(293.0) / (T_sym + sp.Float(120.0))) * (T_sym / sp.Float(273.0)) ** sp.Rational(3, 2)
    Phi_T = gamma * sigma_SB * T_sym**3 / K_a * (L_s / (R_v * T_sym) - 1)
    dPhi_dT = sp.diff(Phi_T, T_sym)
    R_zeta_branch = r * (
        dPhi_dT.subs(T_sym, T_branch) * sp.diff(T_branch, z_m) * (eta_branch - 1)
        + Phi_T.subs(T_sym, T_branch) * sp.diff(eta_branch, z_m)
    )
    show("Phi(T) thermal expression up to positive geometry factor gamma", Phi_T)
    show("dPhi/dT", dPhi_dT)
    show("R_zeta on selected branches", sp.factor(R_zeta_branch))

    banner("Baseline operating point and parameter provenance")
    # Paper Sect. 3.2.3 reports z_infty ~= 9.63 km and D_i,infty ~= 131 um for
    # Case 0 oscillatory mode.  The repository's notebook CSV shows the same
    # trajectory approaching this layer; TASK-002 only needs the local sign.
    z_star_m = 9630.0
    D_i_star_um = 131.0
    crystal = crystal_for_equivalent_diameter(D_i_star_um)
    st = state_at(z_star_m, crystal)
    diag = b.LocalDiagnostics.from_state(st, atm, config=b.SimulationConfig(include_coriolis=False))
    r_star_m = diag.r_i.to("m").magnitude
    validate_baseline_branches(z_star_m, atm)
    print("Provenance:")
    print("- Atmosphere: atmosphere_for_case(0, oscillatory=True): H_a3=0.61, z_W0=9 km, eta from eta_a(z).")
    print("- z*: 9.63 km from Berton Sect. 3.2.3 fixed/limit height quoted in references/berton-2023-pdftotext.txt.")
    print("- D_i*: 131 um from Berton Sect. 3.2.3 limiting mass-equivalent diameter; r*=D_i/2.")
    print("- Geometry factor gamma=A/(4*pi*C*r*) from LocalDiagnostics at (z*, D_i*).")
    print("- sigma_S=-d(S_i-1)/dz from existing pressure/humidity/saturation formulas.")
    print(f"T(z*) = {diag.T_a.to('K').magnitude:.8g} K")
    print(f"eta_a(z*) = {diag.η_a:.8g}")
    print(f"r* = {r_star_m:.8e} m")
    print(f"A = {diag.A.to('m^2').magnitude:.8e} m^2")
    print(f"C = {diag.C.to('m').magnitude:.8e} m")
    print(f"R from full radiative_correction = {diag.R:.8e} (dimensionless)")

    gamma_value = diag.A.to("m^2").magnitude / (4.0 * pi * diag.C.to("m").magnitude * r_star_m)
    substitutions = {
        z_m: z_star_m,
        r: r_star_m,
        gamma: gamma_value,
        sigma_SB: b.CONSTANTS.σ.to("W/m^2/K^4").magnitude,
        L_s: b.CONSTANTS.L_s.to("J/kg").magnitude,
        R_v: b.CONSTANTS.R_v.to("J/kg/K").magnitude,
    }
    R_zeta_value = float(sp.N(R_zeta_branch.subs(substitutions)))

    # Cross-check the reduced closed form against direct finite differencing of
    # R(z, r*) with r fixed and the same gamma.  This isolates altitude effects.
    Phi_T_num = sp.lambdify((T_sym, gamma, sigma_SB, L_s, R_v), Phi_T, "math")

    def reduced_R_at_z(z_eval_m: float) -> float:
        T_eval = atm.temperature(b.Q_(z_eval_m, "m")).to("K").magnitude
        eta_eval = atm.atmospheric_eta(b.Q_(z_eval_m, "m"))
        return r_star_m * Phi_T_num(
            T_eval,
            gamma_value,
            b.CONSTANTS.σ.to("W/m^2/K^4").magnitude,
            b.CONSTANTS.L_s.to("J/kg").magnitude,
            b.CONSTANTS.R_v.to("J/kg/K").magnitude,
        ) * (eta_eval - 1.0)

    fd_R_zeta = central_difference(reduced_R_at_z, z_star_m, 1.0)
    ds_dz = central_difference(lambda zz: supersaturation_minus_one(zz, atm), z_star_m, 1.0)
    sigma_S = -ds_dz
    fd_sigma_S = sigma_S
    sigma_plus = sigma_S + R_zeta_value

    banner("Numerical sign result")
    print(f"R_zeta analytic branch value       = {R_zeta_value:.12e} per m")
    print(f"R_zeta finite-difference check     = {fd_R_zeta:.12e} per m")
    print(f"sigma_S = -d(S_i - 1)/dz          = {sigma_S:.12e} per m")
    print(f"sigma_S + R_zeta                  = {sigma_plus:.12e} per m")
    print("\nPROMINENT SIGN REPORT")
    print(f"- sign(R_zeta)             : {sign_word(R_zeta_value)}")
    print(f"- sign(sigma_S + R_zeta)   : {sign_word(sigma_plus)}")
    print("No Hopf/saddle verdict is made here; downstream tasks use this sign.")

    return Task002Result(
        z_star_m=z_star_m,
        r_star_m=r_star_m,
        eta_star=diag.η_a,
        R_zeta_per_m=R_zeta_value,
        sigma_S_per_m=sigma_S,
        sigma_plus_R_zeta_per_m=sigma_plus,
        finite_difference_R_zeta_per_m=fd_R_zeta,
        finite_difference_sigma_S_per_m=fd_sigma_S,
    )


if __name__ == "__main__":
    derive_task002()
