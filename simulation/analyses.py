"""Deterministic model for *Molecules and Electrons*.

Every number cited in the paper's modelled sections is a key in the dict this
module returns. The dynamics are integrated on a fixed grid with a fixed step,
so the run is reproducible to the last digit; there is no Monte-Carlo layer.

The model. An importing region R supplies a share x in [0,1] of its useful
energy services electrically; 1-x is the molecular (fossil) system. Substitution
follows a replicator equation with a generalized advantage of electrification
that is linear in x once local learning and integration costs are folded in:

    x_dot = eta * x * (1 - x) * Delta(x),    Delta(x) = A + (l - k) x,

so the cubic has equilibria x=0, x=1, and an interior threshold
x_dagger = -A / (l - k). When A < 0 < A + (l - k) the system is bistable and
x_dagger is the unstable takeoff threshold: below it the region falls back to
fossil lock-in, above it learning and coalition feedback carry it to x=1. This
is the standard carbon-lock-in / electro-industrial-takeoff geometry.

A is moved by the petrostate's export price p_P (a higher fossil price raises
the advantage of electrifying):

    A(p_P) = A_base + alpha * (p_P - p_ref).

The petrostate earns a rent margin (p_P - c_P) on the European volume it still
sells, which shrinks as x rises. Its choice of price therefore sets both its
per-unit rent and, through x_dagger, whether the importer ever takes off. That
coupling is the harvest-versus-extend dilemma the paper prices.

Magnitudes are illustrative and anchored to public 2025 figures (EIA export
prices, EU gas demand, BEA current-account, IEA electrification shares, the
Neptun Deep volume); they are not estimates of any actor's true cost or
strategy. The geometry, not the calibration, is the contribution.
"""
from __future__ import annotations

import numpy as np

# --- transition dynamics ---------------------------------------------------
ETA = 0.40            # speed of capital replacement / adoption (per year)
L = 1.0               # local learning slope (electric cost falls with x)
K = 0.2               # integration slope (grid/storage cost rises with x)
L_MINUS_K = L - K     # net destabilizing slope; bistable when 0 < -A < L-K

# advantage of electrification as a function of the petrostate price p_P ($/mcf)
A_BASE = -0.30        # advantage at the reference price
ALPHA = 0.15          # sensitivity of the advantage to the fossil price
P_REF = 7.0           # reference fossil price ($/mcf)

X0 = 0.21             # importer's current electric share (EU, IEA 2025)

# --- rent / volume accounting ($bn, bcm, $/mcf) ----------------------------
C_P = 3.0             # petrostate marginal cost incl. liquefaction+shipping ($/mcf)
BCM_TO_BN_PER_MCF = 0.03531   # $bn of revenue per bcm per $/mcf of price
V_EU_NOW = 86.0       # US LNG volume to the EU at the current fossil share (bcm)
EU_GAS = 335.0        # average EU gas demand 2021-2025 (bcm/yr)
US_CA_DEFICIT = 1120.0  # US current-account deficit 2025 ($bn, BEA)
NEPTUN_DEEP = 8.0     # Neptun Deep projected output from 2027 (bcm/yr)

R_DEFAULT = 0.05      # discount rate
HORIZON = 60.0        # integration horizon (years)
DT = 0.02             # integration step (years)


def advantage(p_P: float) -> float:
    return A_BASE + ALPHA * (p_P - P_REF)


def x_dagger(p_P: float) -> float:
    """Interior takeoff threshold; outside (0,1) it is not an active barrier."""
    A = advantage(p_P)
    return -A / L_MINUS_K


def volume(x: float) -> float:
    """Petrostate's European volume (bcm), proportional to the fossil share."""
    return V_EU_NOW * (1.0 - x) / (1.0 - X0)


def margin_per_bcm(p_P: float) -> float:
    """Rent margin in $bn per bcm at price p_P."""
    return (p_P - C_P) * BCM_TO_BN_PER_MCF


def _integrate_x(p_P: float, x_init: float = X0, eta: float = ETA,
                 horizon: float = HORIZON, dt: float = DT) -> np.ndarray:
    """Integrate the replicator dynamics at a fixed price (RK4)."""
    A = advantage(p_P)

    def f(x):
        return eta * x * (1.0 - x) * (A + L_MINUS_K * x)

    n = int(horizon / dt) + 1
    xs = np.empty(n)
    xs[0] = x_init
    x = x_init
    for i in range(1, n):
        k1 = f(x)
        k2 = f(x + 0.5 * dt * k1)
        k3 = f(x + 0.5 * dt * k2)
        k4 = f(x + dt * k3)
        x = x + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        x = min(max(x, 0.0), 1.0)
        xs[i] = x
    return xs


def _pv_rent(p_P: float, r: float = R_DEFAULT, eta: float = ETA,
             horizon: float = HORIZON, dt: float = DT) -> dict:
    """Present value of petrostate rents on its European volume at price p_P."""
    xs = _integrate_x(p_P, eta=eta, horizon=horizon, dt=dt)
    t = np.arange(len(xs)) * dt
    vol = volume(xs)
    rent_flow = margin_per_bcm(p_P) * vol            # $bn/yr
    disc = np.exp(-r * t)
    pv = float(np.trapezoid(rent_flow * disc, t))
    return {"pv": pv, "x_final": float(xs[-1]),
            "rent_now": float(rent_flow[0]), "took_off": bool(xs[-1] > 0.9)}


# ---------------------------------------------------------------------------
# Study 1: the price lever and the takeoff threshold. The petrostate's export
# price moves the importer's threshold x_dagger; there is a critical price at
# which the importer's current share x0 sits exactly on the threshold, and a
# lockout price below which takeoff is impossible.
# ---------------------------------------------------------------------------
def price_lever() -> dict:
    # price at which A = 0 (above it, takeoff is automatic: x_dagger <= 0)
    p_takeoff = P_REF - A_BASE / ALPHA
    # price at which A + (L-K) = 0 (below it, x=1 unreachable: locked out)
    p_lockout = P_REF - (A_BASE + L_MINUS_K) / ALPHA
    # price at which x_dagger = x0 (the importer's current share sits on the
    # threshold); above it the importer is past the barrier and takes off
    A_at_x0 = -X0 * L_MINUS_K
    p_trap = P_REF + (A_at_x0 - A_BASE) / ALPHA
    grid = np.linspace(2.0, 10.0, 161)
    sweep = []
    for p in grid:
        A = advantage(p)
        xd = x_dagger(p)
        if A >= 0:
            regime = "automatic_takeoff"
        elif A + L_MINUS_K <= 0:
            regime = "locked_out"
        else:
            regime = "bistable_trap"
        sweep.append({"p_P": float(p), "A": float(A),
                      "x_dagger": float(xd), "regime": regime,
                      "traps_importer": bool(0.0 < xd and xd > X0)})
    return {
        "p_takeoff": float(p_takeoff),
        "p_lockout": float(p_lockout),
        "p_trap": float(p_trap),
        "x0": X0,
        "limit_pricing_window": [float(p_lockout), float(p_trap)],
        "window_width": float(p_trap - p_lockout),
        "sweep": sweep,
    }


# ---------------------------------------------------------------------------
# Study 2: harvest versus extend. Over a grid of constant prices, the petrostate
# trades per-unit margin against the survival of its rent stream. A high price
# harvests large margins now but pushes the importer past x_dagger so the stream
# ends; a low (limit) price keeps the importer trapped and the stream alive. The
# rent-maximizing price, and the discount rate at which extend overtakes
# harvest, are the result.
# ---------------------------------------------------------------------------
def _optimal_price(eta: float, r: float, grid: np.ndarray) -> float:
    pv = np.array([_pv_rent(float(p), r=r, eta=eta)["pv"] for p in grid])
    return float(grid[int(np.argmax(pv))])


def harvest_vs_extend() -> dict:
    """The petrostate's choice of constant price, and when limit-pricing wins.

    Harvesting (a high price above the trap price) collects a large margin now
    but pushes the importer past its threshold, so the rent stream ends as the
    importer takes off. Extending (a price below the trap price) keeps the
    importer trapped below threshold and the stream alive at a thin margin.
    Which wins depends on how fast substitution would otherwise be (eta) and on
    the petrostate's patience (r): limit-pricing pays only in the fast-and-
    patient corner, so a petrostate that chooses it reveals it believes the
    importer is near takeoff.
    """
    grid = np.linspace(C_P + 0.2, 10.0, 197)
    p_trap = price_lever()["p_trap"]

    # rent curve at the default eta, r
    rows = []
    for p in grid:
        res = _pv_rent(p)
        rows.append({"p_P": float(p), "pv": res["pv"],
                     "x_final": res["x_final"], "took_off": res["took_off"],
                     "rent_now": res["rent_now"]})
    pvs = np.array([row["pv"] for row in rows])
    p_star = float(grid[int(np.argmax(pvs))])

    # representative harvest and extend prices for the headline comparison,
    # under a patient petrostate facing fast substitution
    p_harvest, p_extend = 9.5, 5.5
    eta_fast, r_patient = 0.6, 0.03
    harvest = _pv_rent(p_harvest, r=r_patient, eta=eta_fast)
    extend = _pv_rent(p_extend, r=r_patient, eta=eta_fast)

    # critical discount rate: at the fast eta, scan r and find where the optimum
    # flips from limit-pricing (below trap) to harvesting (above trap)
    r_grid = np.linspace(0.01, 0.20, 39)
    r_cross = None
    by_r = []
    prev = None
    for r in r_grid:
        p_opt = _optimal_price(eta_fast, float(r), grid)
        side = "extend" if p_opt < p_trap else "harvest"
        by_r.append({"r": float(r), "p_opt": p_opt, "side": side})
        if prev == "extend" and side == "harvest" and r_cross is None:
            r_cross = float(r)
        prev = side

    # critical substitution speed: at the patient r, scan eta and find where the
    # optimum flips from harvesting (slow) to limit-pricing (fast)
    eta_grid = np.linspace(0.1, 1.0, 37)
    eta_cross = None
    by_eta = []
    prev = None
    for e in eta_grid:
        p_opt = _optimal_price(float(e), r_patient, grid)
        side = "extend" if p_opt < p_trap else "harvest"
        by_eta.append({"eta": float(e), "p_opt": p_opt, "side": side})
        if prev == "harvest" and side == "extend" and eta_cross is None:
            eta_cross = float(e)
        prev = side

    # Refined crossovers. The scans above report the first grid point (step
    # 0.005 in r, 0.025 in eta) at which the argmax over a 197-point price grid
    # lies at or above the trap price. Near the crossover the rent-maximizing
    # price moves continuously through p_trap, so the crossover is the root of
    # p_trap - p_opt, with p_opt refined by golden-section search around the
    # grid argmax and the root located by bisection on a verified bracket.
    step = grid[1] - grid[0]

    def _p_opt_refined(eta, r):
        pv = np.array([_pv_rent(float(q), r=r, eta=eta)["pv"] for q in grid])
        i = int(np.argmax(pv))
        lo, hi = float(grid[max(i - 1, 0)]), float(grid[min(i + 1, len(grid) - 1)])
        g = (np.sqrt(5.0) - 1.0) / 2.0
        f = lambda q: _pv_rent(q, r=r, eta=eta)["pv"]
        c, d = hi - g * (hi - lo), lo + g * (hi - lo)
        fc, fd = f(c), f(d)
        for _ in range(50):
            if fc > fd:
                hi, d, fd = d, c, fc
                c = hi - g * (hi - lo)
                fc = f(c)
            else:
                lo, c, fc = c, d, fd
                d = lo + g * (hi - lo)
                fd = f(d)
        return 0.5 * (lo + hi)

    def _root(fun, lo, hi, it=30):
        flo, fhi = fun(lo), fun(hi)
        while (flo > 0) == (fhi > 0):          # widen until the sign changes
            lo, hi = lo - (hi - lo), hi + (hi - lo)
            flo, fhi = fun(lo), fun(hi)
        for _ in range(it):
            mid = 0.5 * (lo + hi)
            fm = fun(mid)
            if (fm > 0) == (flo > 0):
                lo, flo = mid, fm
            else:
                hi, fhi = mid, fm
        return 0.5 * (lo + hi)

    r_step = r_grid[1] - r_grid[0]
    eta_step = eta_grid[1] - eta_grid[0]
    r_cross_exact = _root(lambda rr: p_trap - _p_opt_refined(eta_fast, rr),
                          r_cross - r_step, r_cross)
    eta_cross_exact = _root(lambda ee: p_trap - _p_opt_refined(ee, r_patient),
                            eta_cross - eta_step, eta_cross)

    # bracket confirmation: the refined optimum lies on opposite sides of the
    # trap price just below and just above each refined crossover
    r_bracket = [_p_opt_refined(eta_fast, r_cross_exact - 0.002) - p_trap,
                 _p_opt_refined(eta_fast, r_cross_exact + 0.002) - p_trap]
    eta_bracket = [_p_opt_refined(eta_cross_exact - 0.01, r_patient) - p_trap,
                   _p_opt_refined(eta_cross_exact + 0.01, r_patient) - p_trap]

    # time for an importer facing the harvest price to reach 90% electric
    xs_h = _integrate_x(p_harvest, eta=eta_fast)
    t90_harvest = float(np.argmax(xs_h > 0.9) * DT)

    return {
        "discount_rate_crossover_exact": float(r_cross_exact),
        "p_opt_minus_trap_around_r_crossover": [float(v) for v in r_bracket],
        "p_opt_minus_trap_around_eta_crossover": [float(v) for v in eta_bracket],
        "substitution_speed_crossover_exact": float(eta_cross_exact),
        "discount_rate_grid_step": float(r_step),
        "substitution_speed_grid_step": float(eta_step),
        "harvest_years_to_90pct_electric": t90_harvest,
        "p_star_default": p_star,
        "p_trap": float(p_trap),
        "p_harvest": p_harvest, "p_extend": p_extend,
        "eta_fast": eta_fast, "r_patient": r_patient,
        "pv_harvest": harvest["pv"], "pv_extend": extend["pv"],
        "harvest_takes_off": harvest["took_off"],
        "extend_takes_off": extend["took_off"],
        "extend_over_harvest_ratio": float(extend["pv"] / harvest["pv"]),
        "extend_wins_when_patient_and_fast": bool(extend["pv"] > harvest["pv"]),
        "discount_rate_crossover": r_cross,
        "substitution_speed_crossover": eta_cross,
        "by_discount_rate": by_r,
        "by_substitution_speed": by_eta,
        "pv_curve": rows,
    }


# ---------------------------------------------------------------------------
# Study 3: the magnitude repair. The original hypothesis attached a 5-9 bcm
# displacement to the US current-account deficit and read off 1.7-3.6%. The
# current-account channel is real but an order of magnitude smaller; the stake
# the petrostate actually defends is the capitalized rent the displacement
# threatens, which lives in a different account and is far larger.
# ---------------------------------------------------------------------------
def magnitude_repair() -> dict:
    displ_lo, displ_hi = 5.0, 9.0           # bcm displaced (the original figure)
    price = 8.0
    # current-account channel: lost export value over the deficit
    val_lo = displ_lo * price * BCM_TO_BN_PER_MCF
    val_hi = displ_hi * price * BCM_TO_BN_PER_MCF
    ca_share_lo = val_lo / US_CA_DEFICIT
    ca_share_hi = val_hi / US_CA_DEFICIT

    # capitalized-rent channel: the full European rent stream a successful
    # takeoff terminates, capitalized over the horizon at the discount rate
    annual_rent = margin_per_bcm(price) * V_EU_NOW          # $bn/yr now
    r = R_DEFAULT
    # finite-horizon capitalization with a slow volume decline once locked out
    t = np.arange(0.0, HORIZON + DT, DT)
    pv_perpetuity = float(np.trapezoid(annual_rent * np.exp(-r * t), t))
    pv_pure_perp = annual_rent / r

    return {
        "displacement_bcm": [displ_lo, displ_hi],
        "lost_export_value_bn": [float(val_lo), float(val_hi)],
        "current_account_share": [float(ca_share_lo), float(ca_share_hi)],
        "current_account_share_pct": [float(ca_share_lo * 100),
                                      float(ca_share_hi * 100)],
        "original_claim_pct": [1.7, 3.6],
        "annual_rent_at_stake_bn": float(annual_rent),
        "capitalized_rent_bn": float(pv_perpetuity),
        "capitalized_rent_pure_perpetuity_bn": float(pv_pure_perp),
        "stake_to_annual_ca_ratio": float(pv_perpetuity / val_hi),
        "neptun_deep_bcm": NEPTUN_DEEP,
    }


# ---------------------------------------------------------------------------
# Study 4: the delay is bounded. Global learning lowers the electric cost
# wherever the rival electrostate keeps deploying, so the advantage A floats up
# over time independent of the petrostate's price in region R. Limit-pricing
# subtracts a fixed amount from A but cannot stop the floor from rising, so it
# buys a finite delay set by the rival's deployment rate, which the petrostate
# cannot price.
# ---------------------------------------------------------------------------
def bounded_delay() -> dict:
    # the petrostate holds A down by a fixed limit-pricing depression
    suppression = 0.12          # how far below zero limit-pricing pins A locally
    A_limit = -suppression
    # global learning lifts the advantage floor at a rate proportional to the
    # rival's deployment rate g (per year of effective A-units)
    g_values = [0.005, 0.01, 0.02, 0.04]
    rows = []
    for g in g_values:
        # takeoff when A_limit + g*t >= 0
        tau = -A_limit / g
        rows.append({"rival_deploy_rate": g, "delay_years": float(tau)})
    return {
        "limit_pricing_suppression": suppression,
        "by_rival_rate": rows,
        "note": "delay is finite for every positive rival rate; the petrostate "
                "cannot drive the global learning rate to zero",
    }


# ---------------------------------------------------------------------------
def run() -> dict:
    return {
        "params": {
            "eta": ETA, "l": L, "k": K, "l_minus_k": L_MINUS_K,
            "A_base": A_BASE, "alpha": ALPHA, "p_ref": P_REF, "x0": X0,
            "c_P": C_P, "v_eu_now": V_EU_NOW, "eu_gas": EU_GAS,
            "us_ca_deficit": US_CA_DEFICIT, "r": R_DEFAULT,
            "horizon": HORIZON, "dt": DT,
        },
        "price_lever": price_lever(),
        "harvest_vs_extend": harvest_vs_extend(),
        "magnitude_repair": magnitude_repair(),
        "bounded_delay": bounded_delay(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2)[:3000])
