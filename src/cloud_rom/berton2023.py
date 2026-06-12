"""Reference implementation of Berton (2023) cirrus-uncinus parcel model.

Equations and section references follow:

    Roland P. H. Berton (2023), "Two-Dimensional Dynamics of Ice Crystal
    Parcels in a Cirrus Uncinus", Tellus A, DOI: 10.16993/tellusa.3227.

The implementation is intentionally literal and equation-by-equation.  It is
not optimized: the aim is traceability and unit visibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from math import cos, exp, log, pi, sqrt
from typing import Any, Iterable, TypeAlias, cast

import numpy as np
import pandas as pd
import pint
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from tqdm.auto import tqdm

ureg = pint.UnitRegistry()


def Q_(value: Any, units: str | None = None) -> Any:
    """Create a Pint quantity from this module's unit registry."""

    return ureg.Quantity(value, units)


# Pint 0.25.x returns `PlainQuantity[...]` from a UnitRegistry, while the
# exported `pint.Quantity` type alias is not currently Pyright-friendly on
# Python 3.12.  For this reference implementation we keep runtime Pint checks
# (`isinstance(x, pint.Quantity)`) and use `Quantity = Any` for annotations to
# avoid false PlainQuantity-vs-Quantity errors.
Quantity: TypeAlias = Any


# -----------------------------------------------------------------------------
# Helpers


def _q(value: float | Quantity, unit: str) -> Quantity:
    """Return *value* as a Pint quantity in *unit*."""

    if isinstance(value, pint.Quantity):
        return value.to(unit)
    return Q_(value, unit)


def _mag(value: float | Quantity, unit: str) -> float:
    """Magnitude of *value* in *unit*."""

    return _q(value, unit).magnitude


def _piecewise_linear(z: Quantity, points: Iterable[tuple[Quantity, Quantity]]) -> Quantity:
    """Piecewise-linear profile, constant outside supplied endpoints."""

    z_m = _mag(z, "m")
    pts = [(p[0].to("m").magnitude, p[1]) for p in points]
    if z_m <= pts[0][0]:
        return pts[0][1]
    for (z0, y0), (z1, y1) in zip(pts[:-1], pts[1:]):
        if z_m <= z1:
            f = (z_m - z0) / (z1 - z0)
            return y0 + f * (y1 - y0)
    return pts[-1][1]


# -----------------------------------------------------------------------------
# Constants and configuration


@dataclass(frozen=True)
class Constants:
    """Physical constants from Table 1 and Sect. 2.2.3."""

    g: Quantity = Q_(9.81, "m/s^2")
    Ω0: Quantity = Q_(7.27e-5, "rad/s")
    R_a: Quantity = Q_(287.05, "J/kg/K")
    R_v: Quantity = Q_(461.00, "J/kg/K")
    ε: float = 0.622
    L_s: Quantity = Q_(2.837e6, "J/kg")
    L_v: Quantity = Q_(2.525e6, "J/kg")
    σ: Quantity = Q_(5.67e-8, "W/m^2/K^4")
    T_r: Quantity = Q_(273.15, "K")
    p_r: Quantity = Q_(1.0e5, "Pa")
    ρ_i: Quantity = Q_(920.0, "kg/m^3")
    Q_abs: float = 1.0
    emissivity: float = 1.0


CONSTANTS = Constants()


@dataclass(frozen=True)
class Atmosphere:
    """Atmospheric profile parameters from Appendix A.

    `η_override` may be supplied for Cases 1--3, where the numerical
    experiments prescribe crystal-related η directly rather than inferring it
    from atmospheric η_a.
    """

    H_a3: float = 0.61
    W_a0: Quantity = Q_(0.6, "m/s")
    z_W0: Quantity = Q_(9.0, "km")
    Δz_W: Quantity = Q_(0.3, "km")
    η_override: float | None = None

    # Eq. (69), corrected by user from the paper PDF.
    z_U1: Quantity = Q_(5.0, "km")
    U_a1: Quantity = Q_(5.0, "m/s")
    z_U0: Quantity = Q_(8.0, "km")
    U_a0: Quantity = Q_(10.0, "m/s")
    z_U2: Quantity = Q_(16.0, "km")
    U_a2: Quantity = Q_(-30.0, "m/s")

    # Appendix A.2, Eqs. (75)--(76).
    z_T0: Quantity = Q_(0.0, "km")
    T_a0: Quantity = Q_(293.15, "K")
    z_T1: Quantity = Q_(2.0, "km")
    T_a1: Quantity = Q_(273.15, "K")
    z_T2: Quantity = Q_(8.0, "km")
    T_a2: Quantity = Q_(223.15, "K")
    z_T3: Quantity = Q_(14.0, "km")
    T_a3: Quantity = Q_(213.15, "K")
    z_T4: Quantity = Q_(20.0, "km")
    T_a4: Quantity = Q_(213.15, "K")

    # Appendix A.3, Eqs. (78)--(79).
    z_H0: Quantity = Q_(0.0, "km")
    H_a0: float = 0.20
    z_H1: Quantity = Q_(2.0, "km")
    H_a1: float = 0.30
    z_H2: Quantity = Q_(4.0, "km")
    H_a2: float = 0.40
    z_H3: Quantity = Q_(10.0, "km")
    z_H4: Quantity = Q_(15.0, "km")
    H_a4: float = 0.20
    z_H5: Quantity = Q_(20.0, "km")
    H_a5: float = 0.0

    # Appendix A.4, Eqs. (80)--(81).
    z_η0: Quantity = Q_(9.0, "km")
    η_a0: float = 0.9
    z_η1: Quantity = Q_(10.0, "km")
    η_a1: float = 1.1

    def horizontal_wind(self, z: Quantity) -> Quantity:
        """Horizontal wind U_a(z), Appendix A.1, Eq. (68)."""

        z_m = _mag(z, "m")
        z_U1 = self.z_U1.to("m").magnitude
        z_U0 = self.z_U0.to("m").magnitude
        z_U2 = self.z_U2.to("m").magnitude
        U_a1 = self.U_a1.to("m/s").magnitude
        U_a0 = self.U_a0.to("m/s").magnitude
        U_a2 = self.U_a2.to("m/s").magnitude

        if z_m <= z_U1:
            U = U_a1 / z_U1 * z_m
        elif z_m <= z_U0:
            U = U_a1 + (U_a0 - U_a1) / (z_U0 - z_U1) * (z_m - z_U1)
        elif z_m <= z_U2:
            U = U_a2 + (U_a0 - U_a2) / (z_U0 - z_U2) * (z_m - z_U2)
        else:
            U = U_a2
        return Q_(U, "m/s")

    def updraft(self, z: Quantity) -> Quantity:
        """Vertical wind W_a(z), Appendix A.1, Eq. (70)."""

        z_m = _mag(z, "m")
        z_W0 = self.z_W0.to("m").magnitude
        z_W1 = (self.z_W0 - self.Δz_W).to("m").magnitude
        W_a0 = self.W_a0.to("m/s").magnitude
        if z_m <= z_W1:
            return Q_(0.0, "m/s")
        if z_m <= z_W0:
            return Q_(W_a0 * (z_m - z_W1) / (z_W0 - z_W1), "m/s")
        return Q_(W_a0, "m/s")

    def temperature(self, z: Quantity) -> Quantity:
        """Ambient temperature T_a(z), Appendix A.2, Eqs. (75)--(76)."""

        return _piecewise_linear(
            z,
            [
                (self.z_T0, self.T_a0),
                (self.z_T1, self.T_a1),
                (self.z_T2, self.T_a2),
                (self.z_T3, self.T_a3),
                (self.z_T4, self.T_a4),
            ],
        ).to("K")

    def relative_humidity_profile(self, z: Quantity) -> float:
        """Ambient relative humidity wrt liquid water H_a(z), App. A.3, Eqs. (78)--(79)."""

        return float(
            _piecewise_linear(
                z,
                [
                    (self.z_H0, Q_(self.H_a0, "")),
                    (self.z_H1, Q_(self.H_a1, "")),
                    (self.z_H2, Q_(self.H_a2, "")),
                    (self.z_H3, Q_(self.H_a3, "")),
                    (self.z_H4, Q_(self.H_a4, "")),
                    (self.z_H5, Q_(self.H_a5, "")),
                ],
            ).magnitude
        )

    def atmospheric_eta(self, z: Quantity) -> float:
        """Atmospheric infrared ratio η_a(z), Appendix A.4, Eqs. (80)--(81)."""

        return float(
            _piecewise_linear(
                z,
                [
                    (self.z_η0, Q_(self.η_a0, "")),
                    (self.z_η1, Q_(self.η_a1, "")),
                ],
            ).magnitude
        )

    def eta(self, z: Quantity) -> float:
        """Crystal-related infrared ratio η used in Eq. (24).

        Cases 1--3 set η directly.  Case 0 uses the altitude-dependent profile
        as the paper does in practice; Eq. (27)'s α relation is diagnostic.
        """

        if self.η_override is not None:
            return self.η_override
        return self.atmospheric_eta(z)


@dataclass(frozen=True)
class Crystal:
    """Hollow-column crystal state and fixed shape parameters."""

    m: Quantity
    φ: float = 2.0
    c_B: Quantity = Q_(20.44, "micrometer")


@dataclass(frozen=True)
class State:
    """Parcel dynamical state."""

    t: Quantity
    x: Quantity
    z: Quantity
    u: Quantity
    w: Quantity
    crystal: Crystal


@dataclass(frozen=True)
class SimulationConfig:
    """Time stepping and Coriolis settings."""

    dt: Quantity = Q_(0.04, "s")
    duration: Quantity = Q_(1.0, "hour")
    θ: Quantity = Q_(45.0, "degree")
    include_coriolis: bool = True
    stop_on_nonpositive_mass: bool = True
    reynolds_length: str = "diameter"  # The text before Sect. 3 sets r_i = D_i in Eq. (4); use "radius" for the printed-symbol variant.

    # Integration controls.
    integration_method: str = "euler"  # Set to "euler" for the paper-matching explicit method.
    output_dt: Quantity | None = None  # Optional fixed-output cadence (seconds); default is adaptive for SciPy methods.
    scipy_options: dict[str, Any] = field(default_factory=dict)


# -----------------------------------------------------------------------------
# Atmospheric profiles, Appendix A


def dry_air_pressure(z: Quantity) -> Quantity:
    """Dry-air partial pressure p_a(z), Appendix A.2, Eq. (77)."""

    p0 = Q_(101493.0, "Pa")
    h = Q_(7.5, "km")
    return p0 * exp(-(z / h).to_base_units().magnitude)


# -----------------------------------------------------------------------------
# Thermodynamics and humidity


def saturation_pressure_liquid(T: Quantity) -> Quantity:
    """Saturation vapor pressure over liquid water, Appendix C, Eq. (86)."""

    T_K = _mag(T, "K")
    Cw_m1 = 6096.9385
    Cw0 = 21.2409642
    Cw1 = -2.711193e-2
    Cw2 = 1.673952e-5
    Cw3 = 2.433502
    return Q_(exp(-Cw_m1 / T_K + Cw0 + Cw1 * T_K + Cw2 * T_K**2 + Cw3 * log(T_K)), "Pa")


def saturation_pressure_ice(T: Quantity) -> Quantity:
    """Saturation vapor pressure over ice, Appendix C, Eq. (86)."""

    T_K = _mag(T, "K")
    Ci_m1 = 6024.5282
    Ci0 = 29.32707
    Ci1 = 1.0613868e-2
    Ci2 = -1.3198825e-5
    Ci3 = -0.49382577
    return Q_(exp(-Ci_m1 / T_K + Ci0 + Ci1 * T_K + Ci2 * T_K**2 + Ci3 * log(T_K)), "Pa")


def water_vapor_pressure_from_Hl(H_l: float, p_a: Quantity, p_vsl: Quantity) -> Quantity:
    """Invert relative humidity wrt liquid water, Appendix B, Eqs. (84)--(85)."""

    pa = _mag(p_a, "Pa")
    pvsl = _mag(p_vsl, "Pa")
    δ = sqrt((pa - pvsl) ** 2 + 4 * H_l * pa * pvsl)
    return Q_((-pa + pvsl + δ) / 2, "Pa")


def saturation_ratios(p_v: Quantity, p_vsl: Quantity, p_vsi: Quantity) -> tuple[float, float]:
    """Saturation ratios S_l and S_i, Eq. (12)."""

    return (p_v / p_vsl).to_base_units().magnitude, (p_v / p_vsi).to_base_units().magnitude


def relative_humidities(p_v: Quantity, p: Quantity, p_vsl: Quantity, p_vsi: Quantity) -> tuple[float, float]:
    """Relative humidities H_l and H_i, Eq. (13)."""

    H_l = (p_v / p_vsl * (p - p_vsl) / (p - p_v)).to_base_units().magnitude
    H_i = (p_v / p_vsi * (p - p_vsi) / (p - p_v)).to_base_units().magnitude
    return H_l, H_i


def saturation_mixing_ratio(p: Quantity, p_vsl: Quantity, constants: Constants = CONSTANTS) -> float:
    """Saturation mixing ratio q_s, Eq. (14), returned as kg/kg."""

    return (constants.ε * p_vsl / (p - p_vsl)).to_base_units().magnitude


def dynamic_viscosity_air(T: Quantity, constants: Constants = CONSTANTS) -> Quantity:
    """Dynamic viscosity μ_a of air, Eq. (6)."""

    ΔT = (T - constants.T_r).to("K").magnitude
    return Q_(1e-5 * (1.718 + 0.0049 * ΔT - 1.2e-5 * ΔT**2), "Pa*s")


def dry_air_density(p_a: Quantity, T_a: Quantity, constants: Constants = CONSTANTS) -> Quantity:
    """Dry-air density ρ_a = p_a/(R_a T_a), used by Eqs. (1), (4), and (18)."""

    return (p_a / (constants.R_a * T_a)).to("kg/m^3")


def moist_air_density(p_a: Quantity, p: Quantity, p_vsl: Quantity, T_a: Quantity, constants: Constants = CONSTANTS) -> Quantity:
    """Moist-air density as printed in Eq. (7).

    The paper does not appear to use this quantity in the coupled model.
    """

    return (p_a / (constants.R_a * T_a) * (1 - 0.378 * p_vsl / p)).to("kg/m^3")


def diffusivity_water_vapor(T: Quantity, p: Quantity) -> Quantity:
    """Diffusivity D_v of water vapor in air, Eq. (15)."""

    T_K = _mag(T, "K")
    p_Pa = _mag(p, "Pa")
    # Eq. (15) is dimensionally interpreted with p in Pa, yielding m^2/s.
    return Q_(8.28e-3 * (T_K / p_Pa) * (293.0 / (T_K + 120.0)) * (T_K / 273.0) ** 1.5, "m^2/s")


def heat_conductivity_air(T: Quantity) -> Quantity:
    """Heat conductivity K_a of air, Eq. (15)."""

    T_K = _mag(T, "K")
    return Q_(2.42e-2 * (293.0 / (T_K + 120.0)) * (T_K / 273.0) ** 1.5, "W/m/K")


# -----------------------------------------------------------------------------
# Crystal geometry and microphysics


def hollow_column_volume_area(a: Quantity, c: Quantity, c_B: Quantity) -> tuple[Quantity, Quantity]:
    """Volume and surface area of hollow hexagonal column, Eq. (31a,b)."""

    # PDF text extraction drops the radical in Eq. (31a).  The √3 factor is
    # required by the hexagonal cross section and reproduces Table 2 masses.
    V = (sqrt(3) * (2 * c + c_B) * a**2).to("m^3")
    # Eq. (31b): six rectangular side faces plus six pyramidal hollow faces.
    A = (6 * a * (2 * c + ((c - c_B) ** 2 + 3 * a**2 / 4) ** 0.5)).to("m^2")
    return V, A


def hollowness(c: Quantity, c_B: Quantity) -> float:
    """Hollowness factor ψ = 1 - c_B/c, Eq. (33)."""

    return (1 - c_B / c).to_base_units().magnitude


def aspect_ratio(a: Quantity, c: Quantity) -> float:
    """Aspect ratio φ = c/a, Eq. (34)."""

    return (c / a).to_base_units().magnitude


def volume_from_mass(m: Quantity, constants: Constants = CONSTANTS) -> Quantity:
    """Crystal volume V=m/ρ_i, Eq. (36)."""

    return (m / constants.ρ_i).to("m^3")


def radius_from_volume_constant_phi(V: Quantity, φ: float, c_B: Quantity) -> Quantity:
    """Solve Eq. (35)/(47), `2 φ a^3 + c_B a^2 - V/3 = 0`, for positive `a`."""

    V_m3 = _mag(V, "m^3")
    cB_m = _mag(c_B, "m")

    def f(a_m: float) -> float:
        return sqrt(3) * (2 * φ * a_m + cB_m) * a_m**2 - V_m3

    upper = max((V_m3 / max(φ, 1e-30)) ** (1 / 3) * 10, cB_m * 10, 1e-12)
    while f(upper) <= 0:
        upper *= 2
    return Q_(brentq(f, 0.0, upper), "m")


def dimensions_from_mass_constant_phi(crystal: Crystal, constants: Constants = CONSTANTS) -> tuple[Quantity, Quantity, Quantity, Quantity, Quantity]:
    """Return `(V, a, c, c_B, A)` for a crystal with fixed φ and c_B."""

    V = volume_from_mass(crystal.m, constants)
    a = radius_from_volume_constant_phi(V, crystal.φ, crystal.c_B)
    c = crystal.φ * a
    _, A = hollow_column_volume_area(a, c, crystal.c_B)
    return V, a.to("m"), c.to("m"), crystal.c_B.to("m"), A


def equivalent_diameter(V: Quantity) -> Quantity:
    """Mass-equivalent diameter D_i, Eq. (37)."""

    return Q_((6 * _mag(V, "m^3") / pi) ** (1 / 3), "m")


def equivalent_radius(V: Quantity) -> Quantity:
    """Mass-equivalent radius r_i = D_i/2."""

    return (equivalent_diameter(V) / 2).to("m")


def effective_density_max_dimension(V: Quantity, a: Quantity, c: Quantity, constants: Constants = CONSTANTS) -> Quantity:
    """Effective density using maximum dimension, Eq. (39)."""

    D_m = max((2 * a).to("m").magnitude, (2 * c).to("m").magnitude) * ureg.m
    return (6 * V / (pi * D_m**3) * constants.ρ_i).to("kg/m^3")


def effective_density_column(V: Quantity, a: Quantity, c: Quantity, constants: Constants = CONSTANTS) -> Quantity:
    """Effective density for solid hexagonal column envelope, Eq. (40)."""

    return (V / (3 * sqrt(3) * a**2 * c) * constants.ρ_i).to("kg/m^3")


def capacitance_hollow_column(a: Quantity, c: Quantity) -> Quantity:
    """Capacitance C of hollow column, Eq. (41)."""

    return (0.751 * a + 0.491 * c).to("m")


def terminal_reynolds_number(
    ρ_a: Quantity,
    r_i: Quantity,
    μ_a: Quantity,
    m: Quantity,
    constants: Constants = CONSTANTS,
    *,
    length: str = "diameter",
) -> float:
    """Self-consistent terminal Reynolds number for the zero-slip initial state.

    The Table 2 initial condition has `w0 == W_a(z0)`, so Eq. (4)'s relative
    speed is exactly zero and Eq. (5)'s drag coefficient is singular.  The paper
    figures instead start on the physically relevant low-Re branch (Re≈2,
    C_D≈11 for Case 0).  Use Eq. (9) with Eqs. (3)--(5) to obtain that branch
    when the instantaneous slip speed is zero.
    """

    ℓ = r_i if length == "radius" else 2 * r_i
    ρ = _mag(ρ_a, "kg/m^3")
    length_m = _mag(ℓ, "m")
    μ = _mag(μ_a, "Pa*s")
    mass = _mag(m, "kg")
    g_eff = _mag(constants.g * (1 - ρ_a / constants.ρ_i), "m/s^2")

    def k_for_re(Re: float) -> float:
        return _mag(damping_coefficient(drag_coefficient(Re), Re, μ_a, r_i, m), "1/s")

    def f(Re: float) -> float:
        terminal_speed = g_eff / k_for_re(Re)
        return Re - ρ * length_m * terminal_speed / μ

    upper = 100.0
    while f(upper) < 0:
        upper *= 2
    return float(cast(float, brentq(f, 1e-12, upper)))


def reynolds_number(
    ρ_a: Quantity,
    r_i: Quantity,
    u: Quantity,
    w: Quantity,
    U_a: Quantity,
    W_a: Quantity,
    μ_a: Quantity,
    *,
    length: str = "diameter",
    m: Quantity | None = None,
    constants: Constants = CONSTANTS,
) -> float:
    """Reynolds number, Eq. (4).

    Eq. (4) prints `r_i`, but the text before Sect. 3 states that `r_i` is
    set equal to `D_i` in Eq. (4) as the convention retained for the numerical
    calculations.  Set `length='radius'` to use the printed-symbol variant.
    """

    ℓ = r_i if length == "radius" else 2 * r_i
    speed = ((u - U_a) ** 2 + (w - W_a) ** 2) ** 0.5
    Re = (ρ_a * ℓ * speed / μ_a).to_base_units().magnitude
    if Re <= 1e-12 and m is not None:
        return terminal_reynolds_number(ρ_a, r_i, μ_a, m, constants, length=length)
    return max(float(Re), 1e-12)


def drag_coefficient(Re: float) -> float:
    """Drag coefficient C_D, Eq. (5)."""

    return 64.0 / (pi * Re) * (1 + 0.078 * Re**0.945)


def damping_coefficient(C_D: float, Re: float, μ_a: Quantity, r_i: Quantity, m: Quantity) -> Quantity:
    """Damping coefficient k, Eq. (3)."""

    return (6 * pi * C_D * Re * μ_a * r_i / (24 * m)).to("1/s")


def schmidt_number(μ_a: Quantity, ρ_a: Quantity, D_v: Quantity) -> float:
    """Schmidt number Sc, Eq. (18)."""

    return (μ_a / (ρ_a * D_v)).to_base_units().magnitude


def ventilation_coefficient(Sc: float, Re: float) -> float:
    """Ventilation coefficient f_v, Eqs. (16)--(17).

    Corrected Eq. (17): `X = Sc^(1/3) Re^(1/2)`.
    """

    X = Sc ** (1 / 3) * Re ** 0.5
    return 1 + 0.039 * X + 0.1447 * X**2


def blackbody_flux(T_s: Quantity, constants: Constants = CONSTANTS) -> Quantity:
    """Black-body flux B_i = ε σ T_s^4, Eq. (21)."""

    return (constants.emissivity * constants.σ * T_s**4).to("W/m^2")


def radiative_source(A: Quantity, η_value: float, T_s: Quantity, constants: Constants = CONSTANTS) -> Quantity:
    """Radiative source ℛ = A(η - 1)B_i, Eq. (24)."""

    return (A * (η_value - 1.0) * blackbody_flux(T_s, constants)).to("W")


def radiative_correction(
    C: Quantity,
    K_a: Quantity,
    T: Quantity,
    A: Quantity,
    η_value: float,
    constants: Constants = CONSTANTS,
) -> float:
    """Radiative correction R to supersaturation, Eq. (19) using Eq. (24)."""

    ℛ = radiative_source(A, η_value, T, constants)
    R = ℛ / (4 * pi * C * K_a * T) * (constants.L_s / (constants.R_v * T) - 1)
    return R.to_base_units().magnitude


def driving_factor(S_i: float, R: float) -> float:
    """Growth driving factor S_i - 1 - R, Eq. (10) and Sect. 2.2.1."""

    return S_i - 1.0 - R


def mass_growth_rate(
    C: Quantity,
    f_v: float,
    S_i: float,
    R: float,
    T: Quantity,
    p_vsi: Quantity,
    D_v: Quantity,
    K_a: Quantity,
    constants: Constants = CONSTANTS,
) -> Quantity:
    """Crystal mass growth rate dm/dt, Eq. (10)."""

    denominator = constants.R_v * T / (p_vsi * D_v) + constants.L_s / (K_a * T) * (
        constants.L_s / (constants.R_v * T) - 1
    )
    return (4 * pi * C * f_v * driving_factor(S_i, R) / denominator).to("kg/s")


def surface_temperature_difference(m_dot: Quantity, C: Quantity, K_a: Quantity, constants: Constants = CONSTANTS) -> Quantity:
    """Crystal surface-air temperature difference, Eq. (22)."""

    return (constants.L_s * m_dot / (4 * pi * C * K_a)).to("K")


def alpha_from_eta(η: float, η_a: float) -> float:
    """Diagnostic α inferred from Eq. (27), `η - 1 = α(η_a - 1)`."""

    return (η - 1.0) / (η_a - 1.0)


def eta_from_alpha(α: float, η_a: float) -> float:
    """Diagnostic η from Eq. (27)."""

    return 1.0 + α * (η_a - 1.0)


# -----------------------------------------------------------------------------
# Coupled dynamics


@dataclass(frozen=True)
class LocalDiagnostics:
    """Local quantities needed by Eqs. (42)--(47) at one model state."""

    T_a: Quantity
    p_a: Quantity
    p_v: Quantity
    p: Quantity
    p_vsl: Quantity
    p_vsi: Quantity
    H_l: float
    S_l: float
    S_i: float
    ρ_a: Quantity
    ρ_m: Quantity
    μ_a: Quantity
    D_v: Quantity
    K_a: Quantity
    U_a: Quantity
    W_a: Quantity
    V: Quantity
    a: Quantity
    c: Quantity
    c_B: Quantity
    A: Quantity
    D_i: Quantity
    r_i: Quantity
    C: Quantity
    Re: float
    C_D: float
    k: Quantity
    Sc: float
    f_v: float
    η: float
    η_a: float
    R: float
    driving_factor: float
    m_dot: Quantity
    T_s_minus_T_a: Quantity
    ψ: float
    ρ_ie: Quantity

    @classmethod
    def from_state(
        cls,
        state: State,
        atmosphere: Atmosphere = Atmosphere(),
        constants: Constants = CONSTANTS,
        config: SimulationConfig = SimulationConfig(),
    ) -> "LocalDiagnostics":
        """Evaluate all local quantities needed by Eqs. (42)--(47)."""

        T_a = atmosphere.temperature(state.z)
        p_a = dry_air_pressure(state.z)
        H_l = atmosphere.relative_humidity_profile(state.z)
        p_vsl = saturation_pressure_liquid(T_a)
        p_vsi = saturation_pressure_ice(T_a)
        p_v = water_vapor_pressure_from_Hl(H_l, p_a, p_vsl)
        p = p_a + p_v
        S_l, S_i = saturation_ratios(p_v, p_vsl, p_vsi)
        ρ_a = dry_air_density(p_a, T_a, constants)
        μ_a = dynamic_viscosity_air(T_a, constants)
        D_v = diffusivity_water_vapor(T_a, p)
        K_a = heat_conductivity_air(T_a)
        U_a = atmosphere.horizontal_wind(state.z)
        W_a = atmosphere.updraft(state.z)
        V, a, c, c_B, A = dimensions_from_mass_constant_phi(state.crystal, constants)
        D_i = equivalent_diameter(V)
        r_i = D_i / 2
        C = capacitance_hollow_column(a, c)
        Re = reynolds_number(
            ρ_a,
            r_i,
            state.u,
            state.w,
            U_a,
            W_a,
            μ_a,
            length=config.reynolds_length,
            m=state.crystal.m,
            constants=constants,
        )
        C_D = drag_coefficient(Re)
        Sc = schmidt_number(μ_a, ρ_a, D_v)
        f_v = ventilation_coefficient(Sc, Re)
        η_value = atmosphere.eta(state.z)
        R = radiative_correction(C, K_a, T_a, A, η_value, constants)
        m_dot = mass_growth_rate(C, f_v, S_i, R, T_a, p_vsi, D_v, K_a, constants)

        return cls(
            T_a=T_a,
            p_a=p_a,
            p_v=p_v,
            p=p,
            p_vsl=p_vsl,
            p_vsi=p_vsi,
            H_l=H_l,
            S_l=S_l,
            S_i=S_i,
            ρ_a=ρ_a,
            ρ_m=moist_air_density(p_a, p, p_vsl, T_a, constants),
            μ_a=μ_a,
            D_v=D_v,
            K_a=K_a,
            U_a=U_a,
            W_a=W_a,
            V=V,
            a=a,
            c=c,
            c_B=c_B,
            A=A,
            D_i=D_i,
            r_i=r_i,
            C=C,
            Re=Re,
            C_D=C_D,
            k=damping_coefficient(C_D, Re, μ_a, r_i, state.crystal.m),
            Sc=Sc,
            f_v=f_v,
            η=η_value,
            η_a=atmosphere.atmospheric_eta(state.z),
            R=R,
            driving_factor=driving_factor(S_i, R),
            m_dot=m_dot,
            T_s_minus_T_a=surface_temperature_difference(m_dot, C, K_a, constants),
            ψ=hollowness(c, c_B),
            ρ_ie=effective_density_column(V, a, c, constants),
        )

    def to_dict(self) -> dict[str, object]:
        """Return diagnostics as a dictionary for tabular output."""

        return dict(
            T_a=self.T_a,
            p_a=self.p_a,
            p_v=self.p_v,
            p=self.p,
            p_vsl=self.p_vsl,
            p_vsi=self.p_vsi,
            H_l=self.H_l,
            S_l=self.S_l,
            S_i=self.S_i,
            ρ_a=self.ρ_a,
            ρ_m=self.ρ_m,
            μ_a=self.μ_a,
            D_v=self.D_v,
            K_a=self.K_a,
            U_a=self.U_a,
            W_a=self.W_a,
            V=self.V,
            a=self.a,
            c=self.c,
            c_B=self.c_B,
            A=self.A,
            D_i=self.D_i,
            r_i=self.r_i,
            C=self.C,
            Re=self.Re,
            C_D=self.C_D,
            k=self.k,
            Sc=self.Sc,
            f_v=self.f_v,
            η=self.η,
            η_a=self.η_a,
            R=self.R,
            driving_factor=self.driving_factor,
            m_dot=self.m_dot,
            T_s_minus_T_a=self.T_s_minus_T_a,
            ψ=self.ψ,
            ρ_ie=self.ρ_ie,
        )


def accelerations(
    state: State,
    diag: LocalDiagnostics,
    constants: Constants = CONSTANTS,
    config: SimulationConfig = SimulationConfig(),
) -> tuple[Quantity, Quantity]:
    """Accelerations from Eq. (1a,b), optionally including Coriolis terms."""

    coriolis = constants.Ω0 * cos(config.θ.to("rad").magnitude) if config.include_coriolis else Q_(0.0, "1/s")
    ax = (-diag.k * (state.u - diag.U_a) - 2 * coriolis * state.w).to("m/s^2")
    az = (-diag.k * (state.w - diag.W_a) - constants.g * (1 - diag.ρ_a / constants.ρ_i) + 2 * coriolis * state.u).to(
        "m/s^2"
    )
    return ax, az


def euler_step(
    state: State,
    atmosphere: Atmosphere = Atmosphere(),
    constants: Constants = CONSTANTS,
    config: SimulationConfig = SimulationConfig(),
) -> tuple[State, LocalDiagnostics]:
    """One explicit-Euler update, Sect. 3.1, Eqs. (42)--(47)."""

    diag = LocalDiagnostics.from_state(state, atmosphere, constants, config)
    ax, az = accelerations(state, diag, constants, config)
    dt = config.dt.to("s")

    u_next = (state.u + ax * dt).to("m/s")
    w_next = (state.w + az * dt).to("m/s")
    # Eq. (43) uses current velocity in the explicit position update.
    x_next = (state.x + state.u * dt).to("m")
    z_next = (state.z + state.w * dt).to("m")
    m_next = (state.crystal.m + diag.m_dot * dt).to("kg")
    next_state = State(
        t=(state.t + dt).to("s"),
        x=x_next,
        z=z_next,
        u=u_next,
        w=w_next,
        crystal=replace(state.crystal, m=m_next),
    )
    return next_state, diag


def _state_from_vector(t: float, y: np.ndarray, crystal: Crystal) -> State:
    """Convert a solver state vector into a model state."""

    return State(
        t=Q_(t, "s"),
        x=Q_(float(y[0]), "m"),
        z=Q_(float(y[1]), "m"),
        u=Q_(float(y[2]), "m/s"),
        w=Q_(float(y[3]), "m/s"),
        crystal=replace(crystal, m=Q_(float(y[4]), "kg")),
    )


def _ode_rhs(
    t: float,
    y: np.ndarray,
    atmosphere: Atmosphere,
    constants: Constants,
    config: SimulationConfig,
    crystal: Crystal,
) -> np.ndarray:
    """Derivative function for SciPy ODE integrators."""

    state = _state_from_vector(t, y, crystal)
    diag = LocalDiagnostics.from_state(state, atmosphere, constants, config)
    ax, az = accelerations(state, diag, constants, config)
    return np.array(
        [
            state.u.to("m/s").magnitude,
            state.w.to("m/s").magnitude,
            ax.to("m/s^2").magnitude,
            az.to("m/s^2").magnitude,
            diag.m_dot.to("kg/s").magnitude,
        ],
        dtype=float,
    )


def _nonpositive_mass_event(
    t: float,
    y: np.ndarray,
    atmosphere: Atmosphere,
    constants: Constants,
    config: SimulationConfig,
    crystal: Crystal,
) -> float:
    """Event used to stop integration when mass reaches zero or below."""

    del t, atmosphere, constants, config, crystal
    return float(y[4])


def _fixed_output_times(duration_s: float, output_dt: Quantity | None) -> np.ndarray | None:
    if output_dt is None:
        return None
    if output_dt.to("s").magnitude <= 0:
        raise ValueError("output_dt must be positive")

    step_count = int(duration_s / output_dt.to("s").magnitude)
    if step_count <= 0:
        return np.array([0.0])
    return np.arange(step_count + 1) * float(output_dt.to("s").magnitude)


def _euler_output_indices(steps: int, config: SimulationConfig, sample_every: int) -> set[int]:
    if config.output_dt is not None:
        dt_s = config.dt.to("s").magnitude
        out_s = config.output_dt.to("s").magnitude
        if out_s <= 0:
            raise ValueError("output_dt must be positive")
        ratio = out_s / dt_s
        if not np.isclose(ratio, round(ratio)):
            raise ValueError("output_dt must be an integer multiple of dt when integration_method='euler'")
        output_every = int(round(ratio))
        if output_every <= 0:
            raise ValueError("output_dt must be at least dt")
        return set(range(0, steps + 1, output_every))

    if sample_every <= 0:
        raise ValueError("sample_every must be positive")
    return {n for n in range(0, steps + 1) if n % sample_every == 0}


def initial_crystal_from_dimensions(
    a0: Quantity,
    c0: Quantity,
    ψ0: float = 0.8,
    constants: Constants = CONSTANTS,
) -> Crystal:
    """Create initial hollow-column crystal from Table 2 dimensions."""

    c_B0 = (1 - ψ0) * c0
    V0, _ = hollow_column_volume_area(a0, c0, c_B0)
    m0 = (constants.ρ_i * V0).to("kg")
    return Crystal(m=m0, φ=aspect_ratio(a0, c0), c_B=c_B0)


def case0_initial_state() -> State:
    """Table 2 Case 0 initial state."""

    return State(
        t=Q_(0, "s"),
        x=Q_(2, "km").to("m"),
        z=Q_(10, "km").to("m"),
        u=Q_(0, "m/s"),
        w=Q_(0.6, "m/s"),
        crystal=initial_crystal_from_dimensions(Q_(51.1, "micrometer"), Q_(102.2, "micrometer"), 0.8),
    )


def atmosphere_for_case(case: int, *, oscillatory: bool = True) -> Atmosphere:
    """Atmospheric/profile settings for Table 2 cases 0--3."""

    if case == 0:
        return Atmosphere(H_a3=0.61, W_a0=Q_(0.6, "m/s"), z_W0=Q_(9 if oscillatory else 10, "km"), η_override=None)
    if case == 1:
        return Atmosphere(H_a3=0.61, W_a0=Q_(0.6, "m/s"), z_W0=Q_(9 if oscillatory else 10, "km"), η_override=1.0)
    if case == 2:
        return Atmosphere(H_a3=0.68, W_a0=Q_(0.8, "m/s"), z_W0=Q_(7 if oscillatory else 10, "km"), η_override=1.1)
    if case == 3:
        return Atmosphere(H_a3=0.68, W_a0=Q_(0.8, "m/s"), z_W0=Q_(7 if oscillatory else 10, "km"), η_override=0.9)
    raise ValueError("case must be one of 0, 1, 2, 3")


def initial_state_for_case(case: int) -> State:
    """Initial state for Table 2 cases 0--3."""

    data = {
        0: (51.1, 102.2, 0.6),
        1: (50.17, 100.34, 0.6),
        2: (52.0, 104.0, 0.8),
        3: (50.2, 100.4, 0.8),
    }
    if case not in data:
        raise ValueError("case must be one of 0, 1, 2, 3")
    a_um, c_um, w0 = data[case]
    return State(
        t=Q_(0, "s"),
        x=Q_(2, "km").to("m"),
        z=Q_(10, "km").to("m"),
        u=Q_(0, "m/s"),
        w=Q_(w0, "m/s"),
        crystal=initial_crystal_from_dimensions(Q_(a_um, "micrometer"), Q_(c_um, "micrometer"), 0.8),
    )


def _row(state: State, diag: LocalDiagnostics) -> dict[str, object]:
    row: dict[str, object] = {
        "t": state.t,
        "x": state.x,
        "z": state.z,
        "u": state.u,
        "w": state.w,
        "m": state.crystal.m,
    }
    row.update(diag.to_dict())
    return row


def simulate(
    initial_state: State | None = None,
    atmosphere: Atmosphere = Atmosphere(),
    constants: Constants = CONSTANTS,
    config: SimulationConfig = SimulationConfig(),
    *,
    sample_every: int = 1,
    progress: bool = True,
    progress_desc: str = "simulate",
) -> pd.DataFrame:
    """Integrate the coupled parcel model and return Pint-valued diagnostics.

    The returned `pandas.DataFrame` stores Pint quantities directly in object
    columns, as requested for traceable unit-bearing output.  Use
    `quantity_column_to(...)` to convert a column to magnitudes for plotting.

    `config.integration_method="euler"` preserves the original explicit-Euler
    stepping behavior.  Other methods use `scipy.integrate.solve_ivp` with
    `config.integration_method` as the SciPy `method` and `config.scipy_options`
    passed through.

    For SciPy integrators, set `config.output_dt` to request fixed output times
    (for direct comparison against Euler).  If `config.output_dt` is `None`, the
    solver chooses output times adaptively.

    `sample_every` is an Euler-only convenience and is ignored for SciPy
    integrators.

    Set `progress=False` to disable the tqdm progress bar.
    """

    if initial_state is None:
        initial_state = case0_initial_state()
    state = initial_state

    duration_s = config.duration.to("s").magnitude
    start_t_s = state.t.to("s").magnitude
    stop_t_s = start_t_s + duration_s

    method = config.integration_method
    if method.lower() == "euler":
        dt_s = config.dt.to("s").magnitude
        steps = int(duration_s / dt_s)
        output_indices = _euler_output_indices(steps, config, sample_every)
        rows: list[dict[str, object]] = []
        iterator = tqdm(range(steps + 1), desc=progress_desc, unit="step", disable=not progress)
        for n in iterator:
            diag = LocalDiagnostics.from_state(state, atmosphere, constants, config)
            if n in output_indices:
                rows.append(_row(state, diag))
            if n == steps:
                break
            state, _ = euler_step(state, atmosphere, constants, config)
            if config.stop_on_nonpositive_mass and state.crystal.m.to("kg").magnitude <= 0:
                break
        return pd.DataFrame(rows)

    y0 = np.array(
        [
            _mag(state.x, "m"),
            _mag(state.z, "m"),
            _mag(state.u, "m/s"),
            _mag(state.w, "m/s"),
            _mag(state.crystal.m, "kg"),
        ],
        dtype=float,
    )

    t_eval = _fixed_output_times(duration_s, config.output_dt)
    if t_eval is not None:
        t_eval = t_eval + start_t_s

    events: tuple[Any, ...] | None = None
    if config.stop_on_nonpositive_mass:

        def _event(t: float, y: np.ndarray) -> float:
            return _nonpositive_mass_event(t, y, atmosphere, constants, config, state.crystal)

        event_fn: Any = _event
        event_fn.terminal = True
        event_fn.direction = -1
        events = (event_fn,)

    progress_bar = tqdm(total=duration_s, desc=progress_desc, unit="s", disable=not progress)
    furthest_t_s = start_t_s

    def _rhs_with_progress(t: float, y: np.ndarray) -> np.ndarray:
        nonlocal furthest_t_s
        if t > furthest_t_s:
            progress_bar.update(t - furthest_t_s)
            furthest_t_s = t
        return _ode_rhs(t, y, atmosphere, constants, config, state.crystal)

    try:
        solution = solve_ivp(
            _rhs_with_progress,
            (start_t_s, stop_t_s),
            y0,
            method=method,
            t_eval=t_eval,
            events=events,
            **config.scipy_options,
        )
    finally:
        progress_bar.close()
    if not solution.success:
        raise RuntimeError(f"solve_ivp failed: {solution.message}")

    rows = []
    for t, y in zip(solution.t, solution.y.T):
        current_state = _state_from_vector(float(t), y, state.crystal)
        rows.append(_row(current_state, LocalDiagnostics.from_state(current_state, atmosphere, constants, config)))
    return pd.DataFrame(rows)


def simulate_with_method(
    method: str,
    initial_state: State | None = None,
    atmosphere: Atmosphere = Atmosphere(),
    constants: Constants = CONSTANTS,
    config: SimulationConfig = SimulationConfig(),
    *,
    output_dt: Quantity | None = None,
    scipy_options: dict[str, Any] | None = None,
    sample_every: int = 1,
    progress: bool = True,
    progress_desc: str | None = None,
) -> pd.DataFrame:
    """Convenience wrapper around `simulate(...)` for one-off method selection.

    This avoids constructing a new `SimulationConfig` just to compare SciPy ODE
    methods.  `method="euler"` selects the preserved explicit-Euler integrator;
    any other value is passed to `scipy.integrate.solve_ivp` as its `method`.
    """

    method_config = replace(
        config,
        integration_method=method,
        output_dt=output_dt,
        scipy_options={} if scipy_options is None else scipy_options,
    )
    return simulate(
        initial_state,
        atmosphere,
        constants,
        method_config,
        sample_every=sample_every,
        progress=progress,
        progress_desc=progress_desc if progress_desc is not None else f"simulate {method}",
    )


def quantity_column_to(df: pd.DataFrame, column: str, unit: str) -> list[float]:
    """Convert a Pint-valued DataFrame column to magnitudes in `unit`."""

    return [value.to(unit).magnitude if isinstance(value, pint.Quantity) else float(value) for value in df[column]]


