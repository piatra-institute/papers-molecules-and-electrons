"""Figures for *Molecules and Electrons*. Each reads the results dict and writes
one PNG. No new computation; every plotted value is a results key.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_price_lever(results: dict, path: str) -> None:
    pl = results["price_lever"]
    ps = [s["p_P"] for s in pl["sweep"]]
    xd = [min(max(s["x_dagger"], -0.05), 1.05) for s in pl["sweep"]]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(ps, xd, color="#2166ac")
    ax.axhline(pl["x0"], ls=":", color="#888", label=f"importer share $x_0$ = {pl['x0']}")
    ax.axhspan(0, 1, color="#f0f0f0", zorder=0)
    ax.axvline(pl["p_trap"], ls="--", color="#b2182b",
               label=f"trap price = {pl['p_trap']:.2f}")
    ax.axvline(pl["p_lockout"], ls="--", color="#444",
               label=f"lockout price = {pl['p_lockout']:.2f}")
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel("exporter price $p_P$ (USD/mcf)")
    ax.set_ylabel("takeoff threshold $x^\\dagger$")
    ax.set_title("Importer takeoff threshold against exporter price")
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def plot_harvest_extend(results: dict, path: str) -> None:
    hv = results["harvest_vs_extend"]
    ps = [r["p_P"] for r in hv["pv_curve"]]
    pv = [r["pv"] for r in hv["pv_curve"]]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.8))
    ax1.plot(ps, pv, color="#444")
    ax1.axvline(hv["p_trap"], ls="--", color="#b2182b",
                label=f"trap price = {hv['p_trap']:.2f}")
    pv_star = max(r["pv"] for r in hv["pv_curve"])
    ax1.scatter([hv["p_star_default"]], [pv_star], color="#1a9850", zorder=5,
                label=f"rent-max price = {hv['p_star_default']:.2f}")
    ax1.set_xlabel("constant price $p_P$ (USD/mcf)")
    ax1.set_ylabel("present value of rents (USD bn)")
    ax1.set_title(f"PV of rents against price ($\\eta$ = {results['params']['eta']}, $r$ = {results['params']['r']})", fontsize=9)
    ax1.legend(fontsize=8)

    rs = [d["r"] for d in hv["by_discount_rate"]]
    popt = [d["p_opt"] for d in hv["by_discount_rate"]]
    ax2.plot(rs, popt, color="#2166ac")
    ax2.axhline(hv["p_trap"], ls="--", color="#b2182b")
    ax2.axvline(hv["discount_rate_crossover_exact"], ls=":", color="#888",
                label=f"crossover $r$ = {hv['discount_rate_crossover_exact']:.3f}")
    ax2.legend(fontsize=8)
    ax2.set_xlabel("discount rate $r$")
    ax2.set_ylabel("rent-maximizing price $p_P^*$")
    ax2.set_title(f"Rent-maximizing price against discount rate ($\\eta$ = {hv['eta_fast']})", fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def plot_magnitude(results: dict, path: str) -> None:
    mr = results["magnitude_repair"]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    labels = ["original claim\n(current account)", "corrected\n(current account)",
              "capitalized European\nrent (60 years)"]
    # express all as $bn for visual comparison
    orig = mr["original_claim_pct"][1] / 100 * results["params"]["us_ca_deficit"]
    corr = mr["lost_export_value_bn"][1]
    cap = mr["capitalized_rent_bn"]
    vals = [orig, corr, cap]
    colors = ["#bbbbbb", "#2166ac", "#b2182b"]
    ax.bar(labels, vals, color=colors)
    ax.set_yscale("log")
    ax.set_ylabel("USD bn (log scale)")
    ax.set_ylim(1, 1000)
    ax.set_title("Annual displacement against capitalized rent")
    for i, v in enumerate(vals):
        ax.text(i, v * 1.1, f"{v:.1f} bn", ha="center", fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)
