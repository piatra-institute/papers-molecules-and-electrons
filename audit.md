# Audit

Dated log of editorial passes and verification runs. Newest first.

## 2026-09-23 — prose revision

Prose rewritten against the house standards. Headings: 1. Introduction; 2. Molecule power and electron power; 3. Model; 4. Results (4.1 The price as a lever on the takeoff threshold; 4.2 Harvesting and extending the fossil age; 4.3 Current-account displacement and capitalized rent; 4.4 Bounded delay under global learning); 5. The Romanian case; 6. Limitations (new); 7. Conclusion (new); Reproducibility (new). Tics: "rather than" 4 -> 0, inline ", not X" 6 -> 0, negate-pivots 2 -> 0, "not X but Y" 8 -> 0, "this paper" 4 -> 0.

Corrections found during the pass:
  - Discount-rate crossover "about 0.165" was the first point of a 0.005 r grid at which the argmax over a 197-point price grid (step 0.035) landed above the trap price. Near the crossover the optimal price moves continuously through the trap price, so the crossover is the root of p_trap - p_opt(r) with p_opt refined by golden-section search; bisection gives r = 0.171 (the price-grid coarseness had pulled the grid crossover more than one r step early). New fields harvest_vs_extend.discount_rate_crossover_exact and p_opt_minus_trap_around_r_crossover (bracket -0.0034 / +0.0032); invariants r_crossover_brackets_trap_price, r_crossover_within_two_grid_steps.
  - Substitution-speed crossover "about 0.20" (0.025 eta grid) -> 0.188 by the same refinement. New fields substitution_speed_crossover_exact, p_opt_minus_trap_around_eta_crossover; invariant eta_crossover_brackets_trap_price.
  - Lost export value "1.4 to 2.6 billion dollars" -> 1.4 to 2.5 (5-9 bcm at 8 USD/mcf = 1.41-2.54).
  - Bounded delay: "a rate four times faster buys about 3 [years]" -> four times faster buys 6, eight times faster buys 3 (rates 0.005/0.02/0.04 give 24/6/3 years).
  - "an unobstructed importer would electrify within roughly a decade" -> reaches 90 percent electric after about 12 years at the harvest price (new field harvest_years_to_90pct_electric = 12.2).
  - The harvest-extend figure caption described the left panel as "a patient exporter facing fast substitution"; it is drawn at the default eta = 0.4, r = 0.05. Caption and title corrected; the text now states that the rent-maximizing price (7.71) sits just below the trap price.
Grid audit: outcome above. Takeoff (9.00), trap (7.88) and lockout (3.67) prices are closed forms; the capitalized rent (289) and ratio (113) are direct integrals.
Figure titles replaced with descriptive ones.

## 2026-06-19 — Initial implementation from seed chat
Scope: full paper built from `chats/chat.md` (two deep-research passes on the Romanian-energy / petrostate-vs-electrostate hypothesis) through the PIATRA pipeline.
Decision: ships a deterministic dynamical-systems + valuation simulation (no Monte-Carlo, no headline threshold near 0.4), chosen to keep the corpus from sounding like one instrument while honoring a hypothesis that is full of real numbers begging to be modelled correctly.
Changes:
  - Extracted the crown contribution from the seed's §6: the petrostate's harvest-vs-extend dilemma, made computable. A bistable replicator-with-learning model of an importer's electric share, with the exporter's price moving the takeoff threshold x_dagger.
  - Three results: (1) harvest vs extend — limit-pricing (PV ~$259bn) beats harvesting (~$135bn) by ~1.9x only when patient (r<0.165) and fast (eta>0.20), so suppressing one's own price is a tell that the actor believes takeoff is near; (2) magnitude repair — the current-account channel is 0.13-0.23% (order of magnitude below the hypothesis's 1.7-3.6%, confirming the deflation) but the real stake is the capitalized European rent, ~$289bn, ~113x the annual figure, in a different ledger; (3) bounded delay — the global learning curve drags the threshold down regardless of price, so limit-pricing buys a finite 24/12/6/3 years set by the rival's deployment rate.
  - Repaired the user's hypothesis honestly: vindicates the "stakes are large" intuition by relocating it (capitalized rent, not current account) while confirming the arithmetic error.
  - The negative result is framed as OVERDETERMINATION (the Romanian outcome arises from four independent optima, so coordination is unnecessary, not merely unproven) rather than the corpus's identification framing, to avoid the fingerprint. Closes on the bounded-delay insight, not a "prices X not Y" formula.
  - Built simulation/ (numpy + matplotlib, uv): analyses.py (model + 4 studies), figures.py (3 figures), run_all.py. Deterministic RK4 integration on a fixed grid; reproducible to the last digit. Note: numpy 2.x — used np.trapezoid (np.trapz removed).
  - Recalibrated once: initial parameters made substitution too slow, so harvest always dominated and the crown result didn't emerge; raised eta and the advantage scale so a fast takeoff genuinely kills the rent stream, and reframed Study 2 as the (eta, r) crossover surface.
  - Wrote PAPER.md (7 sections, distinctive titles, claim-strength discipline: prices the incentive, does not establish coordination), metadata.yaml, brief/research/sources, README.
  - 15-source bibliography, all engaged in-text, verified against the real literature (energy geopolitics, lock-in, directed technical change, learning curves, replicator dynamics); 0 confabulated (refs MISSING = 0). Tooze's Chartbook cited as the framing's origin.
Verification:
  - voice: 0 errors, 12 review-candidate warns. Converted spelled quantities to numerals (15->25, 5->9, 8 bcm) per house rule; added short sentences to break an over-smooth 48-sentence run (down to 27, 10% short).
  - refs: 0 missing, 0 unused (15 in-text keys, 15 bib entries; aligned the IEA in-text key to the bib author).
  - claims: 17 prose decimals, 0 without a matching results.json value.
  - build: 10 pages, 0 missing-character warnings.
  - check => PASS

---

## 2026-07-02 — reform pass (false-precision fix)

Corpus reform. The paper has no templated closer (ends on the substantive §7 "The Delay Is Bounded") and its molecule/electron distinction and conspiracy-not-needed argument are strong. The one genuine defect was the audit's charge: §5 presented the $289B capitalized stake and the 113x ratio as precise while stating none of the assumptions behind them.

- paper/PAPER.md §5: the sim capitalizes a $15.18B/yr rent at 5% over a 60-year horizon (near the $304B pure perpetuity) to get $288.5B, and 113x is that over the high current-account displacement; none of this was in the prose. Rewrote to state the ~60-year horizon and perpetuity comparison, and added that "the three-figure precision is spurious, and the order of magnitude is the whole of the claim: the exact stake moves with the assumed margin, discount rate, and horizon, none of them measured here." The sound conceptual point (a flow's value is a capital sum, not one coupon) is kept; the false precision is disowned.
- Verify: voice 0 errors; refs 15/15, 0 missing/0 unused; claims 17/0 unmatched (dollar figures are integers, not gate-checked); check => PASS; synced.
