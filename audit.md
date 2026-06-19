# Audit

Dated log of editorial passes and verification runs. Newest first.

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
