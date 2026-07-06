# comp-trading findings (verbatim summary, 2026-07-06)
Data: 648,118 ensemble pairs (grew since audit's 645,620; window 2026-04-07..07-05, 1658 symbols, 24h horizon, ~30min issue cadence). 80/20 temporal split: 518,494/129,624; holdout base rate 0.512.
SHOOT-OUT (holdout Brier | ECE | fit s): project PAV 0.249983|0.0107|13.62 · sklearn Isotonic 0.249947|0.0095|0.05 · Platt 0.249972|0.0092|0.36 · constant 0.249951|0.0094|0.0003 · raw confidence 0.353|0.295 (reference).
=> All four calibrators statistically identical to constant (~theoretical floor at p≈0.5). Calibration layer works; the signal has nothing to give. sklearn 270x faster than pure-PAV for identical output (engineering note).
BASELINES: always-up 0.5331 (window drift, not skill: up/down 345,539/302,579); always-down 0.4669; persistence 0.9024 INVALID (overlapping 24h windows at 30min cadence = autocorrelation, not forecasting — flag or drop). System models 0.4726-0.5100.
LITERATURE: M6 (arXiv:2310.13357): 38/163 (23.3%) beat naive accuracy; 11 (6.7%) both accuracy+return; 3 all 12 months. GPT-as-analyst (arXiv:2412.01069): 49.3% direction accuracy vs human 71.1%. Retail win-rate stats excluded (SEO junk only).
Caveats: persistence contaminated; always-up regime-dependent; literature numbers qualitative context only.
