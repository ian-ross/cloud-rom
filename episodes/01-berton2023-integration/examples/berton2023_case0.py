"""Minimal paper-inspired Berton (2023) Case 0 run.

This short run demonstrates the API and units.  It is not a full reproduction
of the 40-hour oscillatory case in Table 2.
"""

from cloud_rom import berton2023 as b


def main() -> None:
    state = b.initial_state_for_case(0)
    atmosphere = b.atmosphere_for_case(0, oscillatory=True)
    config = b.SimulationConfig(duration=b.Q_(10, "minute"), dt=b.Q_(0.04, "s"), include_coriolis=True)
    df = b.simulate(state, atmosphere, config=config, sample_every=500)

    last = df.iloc[-1]
    print("Berton (2023) Case 0 short run")
    print(f"samples: {len(df)}")
    print(f"t = {last['t'].to('minute'):.3f}")
    print(f"x = {last['x'].to('km'):.6f}")
    print(f"z = {last['z'].to('km'):.6f}")
    print(f"m = {last['m'].to('microgram'):.6f}")
    print(f"D_i = {last['D_i'].to('micrometer'):.3f}")


if __name__ == "__main__":
    main()
