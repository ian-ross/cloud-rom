import math

import pytest
import pint

from cloud_rom import berton2023 as b


def assert_close(q, expected, unit, rel=1e-6, abs_=0.0):
    assert q.to(unit).magnitude == pytest.approx(expected, rel=rel, abs=abs_)


def test_atmospheric_profile_smoke_values():
    atm = b.Atmosphere()
    assert_close(atm.temperature(b.Q_(0, "km")), 293.15, "K")
    assert_close(atm.temperature(b.Q_(8, "km")), 223.15, "K")
    assert_close(atm.temperature(b.Q_(20, "km")), 213.15, "K")
    assert_close(b.dry_air_pressure(b.Q_(0, "km")), 101493.0, "Pa")
    assert_close(b.dry_air_pressure(b.Q_(7.5, "km")), 101493.0 / math.e, "Pa")
    assert atm.atmospheric_eta(b.Q_(9, "km")) == pytest.approx(0.9)
    assert atm.atmospheric_eta(b.Q_(9.5, "km")) == pytest.approx(1.0)
    assert atm.atmospheric_eta(b.Q_(10, "km")) == pytest.approx(1.1)


def test_horizontal_wind_corrected_constants():
    atm = b.Atmosphere()
    assert_close(atm.horizontal_wind(b.Q_(0, "km")), 0.0, "m/s")
    assert_close(atm.horizontal_wind(b.Q_(5, "km")), 5.0, "m/s")
    assert_close(atm.horizontal_wind(b.Q_(8, "km")), 10.0, "m/s")
    assert_close(atm.horizontal_wind(b.Q_(10, "km")), 0.0, "m/s")
    assert_close(atm.horizontal_wind(b.Q_(16, "km")), -30.0, "m/s")


def test_case0_geometry_reproduces_table2_values():
    state = b.initial_state_for_case(0)
    V, a, c, c_B, A = b.dimensions_from_mass_constant_phi(state.crystal)
    assert_close(state.crystal.m, 0.935, "microgram", rel=1e-3)
    assert_close(a, 51.1, "micrometer", rel=1e-6)
    assert_close(c, 102.2, "micrometer", rel=1e-6)
    assert_close(c_B, 20.44, "micrometer", rel=1e-6)
    assert_close(b.capacitance_hollow_column(a, c), 88.6, "micrometer", rel=1e-3)
    assert_close(b.equivalent_diameter(V), 125.0, "micrometer", rel=3e-3)
    assert_close(b.effective_density_column(V, a, c), 675.0, "kg/m^3", rel=1e-3)


def test_units_and_mass_growth_smoke():
    state = b.initial_state_for_case(0)
    diag = b.LocalDiagnostics.from_state(state, b.atmosphere_for_case(0))
    k = diag.k
    m_dot = diag.m_dot
    D_i = diag.D_i
    f_v = diag.f_v
    assert isinstance(k, pint.Quantity)
    assert isinstance(m_dot, pint.Quantity)
    assert isinstance(D_i, pint.Quantity)
    assert isinstance(f_v, float)
    assert k.check("[time]^-1")
    assert m_dot.check("[mass] / [time]")
    ax, az = b.accelerations(state, diag)
    assert ax.check("[length] / [time]^2")
    assert az.check("[length] / [time]^2")
    assert D_i.to("micrometer").magnitude > 0
    assert f_v > 1


def test_incompatible_units_rejected():
    with pytest.raises(pint.DimensionalityError):
        b.dynamic_viscosity_air(b.Q_(10, "m"))


def test_short_simulation_returns_pint_quantities_and_positive_mass():
    cfg = b.SimulationConfig(duration=b.Q_(1, "s"), dt=b.Q_(0.1, "s"))
    df = b.simulate(b.initial_state_for_case(0), b.atmosphere_for_case(0), config=cfg, progress=False)
    assert len(df) == 11
    assert isinstance(df.loc[0, "z"], pint.Quantity)
    assert df.iloc[-1]["m"].to("kg").magnitude > 0
    assert df.iloc[-1]["z"].check("[length]")


def test_steady_case0_begins_with_hook_like_lift_and_leftward_motion():
    cfg = b.SimulationConfig(duration=b.Q_(10, "minute"), dt=b.Q_(0.04, "s"), include_coriolis=False)
    df = b.simulate(
        b.initial_state_for_case(0),
        b.atmosphere_for_case(0, oscillatory=False),
        config=cfg,
        sample_every=15000,
        progress=False,
    )
    start = df.iloc[0]
    end = df.iloc[-1]
    assert end["m"].to("microgram").magnitude > start["m"].to("microgram").magnitude
    assert end["z"].to("km").magnitude > start["z"].to("km").magnitude
    assert end["x"].to("km").magnitude < start["x"].to("km").magnitude
