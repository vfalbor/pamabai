# bench-trading findings (from calibration_results.json, 2026-07-06)
- n=645,620 evaluated ensemble predictions (707,579 total, 8.8% unevaluated), 1,662 symbols. Base rate direction-correct 0.5042.
- Reliability (true deciles, 64,562 each): observed freq 0.497–0.510 in EVERY decile while predicted prob spans 0.0→0.6+ — flat; confidence carries no information.
- Brier: constant base rate 0.250 | raw confidence 0.345 | isotonic-calibrated 0.494 (shipped calibrator makes it worse).
- Shipped calibrator forensics: trained on legacy `predictions` table, 673 rows (0.1% of available); label = accuracy>50 (NOT direction hit for NEUTRAL); confidence scale 29–70 vs 0–23 in modern table; isotonic map degenerate (93 knots, ~all y=1.0).
- Per-model hit rates (n≈600k each): ml 0.510, gbm 0.508, ensemble 0.504, merton 0.504, kalman 0.490, hmm_signal 0.485, kalman_signal 0.472.
- Ridge stacker: n=566k, holdout R²=0.0007 (selection note recorded holdout sharpe 1.58/hr 55.8% — not reproduced by full-store audit).
- Ops: 84 daily reports / 89 days (94%). Backtest table hit_rate field (~0.06–0.08) uses inconsistent definition — flagged, excluded.
