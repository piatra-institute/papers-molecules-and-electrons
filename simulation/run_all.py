"""Orchestrator: reproduces every modelled number in the paper.

    cd simulation
    uv run run_all.py

Writes output/results.json and output/figures/. The dynamics are integrated on
a fixed grid with a fixed step (analyses.DT), so the run is reproducible to the
last digit.
"""
from __future__ import annotations

import json
from pathlib import Path

from analyses import run
from figures import plot_price_lever, plot_harvest_extend, plot_magnitude

OUT = Path(__file__).parent / "output"


def main() -> None:
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    results = run()
    (OUT / "results.json").write_text(json.dumps(results, indent=2))
    plot_price_lever(results, str(OUT / "figures" / "price_lever.png"))
    plot_harvest_extend(results, str(OUT / "figures" / "harvest_extend.png"))
    plot_magnitude(results, str(OUT / "figures" / "magnitude.png"))

    pl, hv = results["price_lever"], results["harvest_vs_extend"]
    mr, bd = results["magnitude_repair"], results["bounded_delay"]
    print("PRICE LEVER")
    print(f"  takeoff price (A=0)          : {pl['p_takeoff']:.2f}")
    print(f"  trap price (x_dagger=x0)      : {pl['p_trap']:.2f}")
    print(f"  lockout price                 : {pl['p_lockout']:.2f}")
    print("HARVEST VS EXTEND")
    print(f"  rent-maximizing price (default): {hv['p_star_default']:.2f} "
          f"(trap price {hv['p_trap']:.2f})")
    print(f"  PV harvest (p={hv['p_harvest']})           : {hv['pv_harvest']:.1f} bn")
    print(f"  PV extend  (p={hv['p_extend']})           : {hv['pv_extend']:.1f} bn")
    print(f"  extend/harvest PV ratio       : {hv['extend_over_harvest_ratio']:.2f} "
          f"(extend wins: {hv['extend_wins_when_patient_and_fast']})")
    print(f"  discount-rate crossover       : {hv['discount_rate_crossover']}")
    print(f"  substitution-speed crossover  : {hv['substitution_speed_crossover']}")
    print("MAGNITUDE REPAIR")
    print(f"  current-account share (orig)  : {mr['original_claim_pct']} %")
    print(f"  current-account share (corr)  : "
          f"[{mr['current_account_share_pct'][0]:.2f}, {mr['current_account_share_pct'][1]:.2f}] %")
    print(f"  capitalized rent at stake     : {mr['capitalized_rent_bn']:.0f} bn")
    print(f"  stake / annual CA hit ratio   : {mr['stake_to_annual_ca_ratio']:.0f}x")
    print("BOUNDED DELAY")
    for row in bd["by_rival_rate"]:
        print(f"  rival rate {row['rival_deploy_rate']:.3f} -> delay {row['delay_years']:.1f} yr")


if __name__ == "__main__":
    main()
