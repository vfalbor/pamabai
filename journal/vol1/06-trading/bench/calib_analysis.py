#!/usr/bin/env python3
"""
Calibration measurement for the trading-prediction pipeline.
Reads from a COPY of trading.db (read-only intent). stdlib only.
"""
import sqlite3, json, math, sys
from bisect import bisect_right

DB = "/tmp/claude-1000/-home-vfalbor/bcd99207-91f8-4708-83fa-b124b3cc457d/scratchpad/trading_copy.db"
CALIB_JSON = "/tmp/claude-1000/-home-vfalbor/bcd99207-91f8-4708-83fa-b124b3cc457d/scratchpad/calibrator.json"
WEIGHTS_JSON = "/tmp/claude-1000/-home-vfalbor/bcd99207-91f8-4708-83fa-b124b3cc457d/scratchpad/ensemble_weights.json"
OUT_JSON = "/home/vfalbor/pamabai/journal/vol1/06-trading/bench/calibration_results.json"

conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

results = {}

# ── 1. Schema / row counts / date ranges ────────────────────────────────────
tables = ["predictions", "quant_predictions", "quant_errors", "backtest_runs",
          "top_picks", "daily_reports", "investments", "symbol_universe",
          "news", "news_sentiment", "sentiment_daily", "macro_context",
          "macro_series", "corporate_events", "asset_to_ticker"]
schema_info = {}
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    n = cur.fetchone()[0]
    schema_info[t] = {"row_count": n}
schema_info["predictions"]["date_range"] = list(cur.execute("SELECT MIN(date),MAX(date) FROM predictions").fetchone())
schema_info["quant_predictions"]["date_range"] = list(cur.execute("SELECT MIN(datetime),MAX(datetime) FROM quant_predictions").fetchone())
schema_info["quant_errors"]["date_range"] = list(cur.execute("SELECT MIN(prediction_dt),MAX(prediction_dt) FROM quant_errors").fetchone())
schema_info["backtest_runs"]["date_range"] = list(cur.execute("SELECT MIN(run_at),MAX(run_at) FROM backtest_runs").fetchone())
schema_info["daily_reports"]["date_range"] = list(cur.execute("SELECT MIN(report_date),MAX(report_date) FROM daily_reports").fetchone())
schema_info["top_picks"]["date_range"] = list(cur.execute("SELECT MIN(picked_at),MAX(picked_at) FROM top_picks").fetchone())
results["schema"] = schema_info

# ── 2. Core calibration dataset: ensemble predictions with realized outcome ─
# quant_predictions.confidence is the value ACTUALLY LOGGED at prediction time
# (already passed through get_calibrated_confidence at write time per app code
# path; see quant_engine.py L838-866). Ground truth = quant_errors.direction_correct
# for model='ensemble', joined on prediction_id == quant_predictions.id.
cur.execute("""
    SELECT qp.confidence AS conf, qe.direction_correct AS hit, qp.symbol AS symbol
    FROM quant_errors qe
    JOIN quant_predictions qp ON qp.id = qe.prediction_id
    WHERE qe.model = 'ensemble'
      AND qe.direction_correct IS NOT NULL
      AND qp.confidence IS NOT NULL
""")
rows = cur.fetchall()
n_scored = len(rows)
confs = [r["conf"] for r in rows]
hits = [r["hit"] for r in rows]

def brier(probs, outcomes):
    return sum((p - o) ** 2 for p, o in zip(probs, outcomes)) / len(outcomes)

raw_probs = [c / 100.0 for c in confs]
brier_raw = brier(raw_probs, hits)
base_rate = sum(hits) / len(hits)
brier_base_rate = brier([base_rate] * len(hits), hits)  # naive baseline: predict constant base rate

# ── Apply the production isotonic calibrator to these same raw confidences ──
with open(CALIB_JSON) as f:
    calib = json.load(f)
kx, ky = calib["knots_x"], calib["knots_y"]

def isotonic_calibrate(r):
    if not kx:
        return r / 100.0
    if r <= kx[0]:
        p = ky[0]
    elif r >= kx[-1]:
        p = ky[-1]
    else:
        idx = bisect_right(kx, r) - 1
        x0, x1 = kx[idx], kx[idx + 1]
        y0, y1 = ky[idx], ky[idx + 1]
        p = y0 if x1 == x0 else y0 + (r - x0) / (x1 - x0) * (y1 - y0)
    return max(0.0, min(1.0, p))

calibrated_probs = [isotonic_calibrate(c) for c in confs]
brier_calibrated = brier(calibrated_probs, hits)

results["calibration_core"] = {
    "n_scored_ensemble_predictions": n_scored,
    "base_rate_direction_correct": base_rate,
    "brier_raw_confidence": brier_raw,
    "brier_isotonic_calibrated_confidence": brier_calibrated,
    "brier_naive_constant_base_rate": brier_base_rate,
    "calibrator_metadata": {
        "n_samples_used_to_train_calibrator": calib.get("n_samples"),
        "trained_at": calib.get("trained_at"),
        "source_query_claimed_in_json": calib.get("source_query"),
        "actual_training_source": "predictions table (evaluated=1, confidence & accuracy>0.5 as hit) because it had >=200 rows (MIN_SAMPLES); the quant_errors/quant_predictions fallback in source_query was NEVER reached",
        "knots_y_unique_values": sorted(set(round(y, 4) for y in ky)),
        "knots_x_range": [min(kx), max(kx)],
    },
    "note": "brier_isotonic_calibrated_confidence uses the calibrator ACTUALLY SHIPPED IN PRODUCTION (calibrator.json), applied out-of-sample to the large quant_errors/quant_predictions dataset it was never trained on.",
}

# ── 3. Reliability diagram: deciles of raw confidence -> observed freq ──────
# Confidence values in this table are highly discrete/clustered near 0-30, so
# use rank-based deciles on the pooled data.
paired = sorted(zip(confs, hits), key=lambda x: x[0])
n = len(paired)
decile_size = n // 10
reliability = []
for i in range(10):
    start = i * decile_size
    end = (i + 1) * decile_size if i < 9 else n
    chunk = paired[start:end]
    if not chunk:
        continue
    cs = [c for c, h in chunk]
    hs = [h for c, h in chunk]
    reliability.append({
        "decile": i + 1,
        "n": len(chunk),
        "conf_min": min(cs), "conf_max": max(cs),
        "mean_predicted_prob": sum(cs) / len(cs) / 100.0,
        "observed_freq": sum(hs) / len(hs),
    })
results["reliability_diagram_raw_confidence_deciles"] = reliability

# Fixed-width bin reliability (0-10,...,90-100) as a cross-check / for plotting
fixed_bins = []
for lo in range(0, 100, 10):
    hi = lo + 10
    chunk = [(c, h) for c, h in paired if (c >= lo and (c < hi or (hi == 100 and c <= 100)))]
    if chunk:
        cs = [c for c, h in chunk]
        hs = [h for c, h in chunk]
        fixed_bins.append({
            "bin": f"{lo}-{hi}", "n": len(chunk),
            "mean_predicted_prob": sum(cs) / len(cs) / 100.0,
            "observed_freq": sum(hs) / len(hs),
        })
results["reliability_diagram_fixed_bins"] = fixed_bins

# ── 4. Brier by asset (top 15 by volume) ────────────────────────────────────
by_symbol = {}
for r in rows:
    by_symbol.setdefault(r["symbol"], {"probs": [], "hits": []})
    by_symbol[r["symbol"]]["probs"].append(r["conf"] / 100.0)
    by_symbol[r["symbol"]]["hits"].append(r["hit"])
symbol_stats = []
for sym, d in by_symbol.items():
    symbol_stats.append({
        "symbol": sym, "n": len(d["hits"]),
        "brier_raw": brier(d["probs"], d["hits"]),
        "hit_rate": sum(d["hits"]) / len(d["hits"]),
    })
symbol_stats.sort(key=lambda x: -x["n"])
results["brier_by_asset_top20_by_volume"] = symbol_stats[:20]

# ── 5. Small `predictions` table (what the calibrator was actually trained on) ─
cur.execute("""
    SELECT confidence, accuracy FROM predictions
    WHERE evaluated=1 AND confidence IS NOT NULL AND accuracy IS NOT NULL
""")
small_rows = cur.fetchall()
small_pairs = [(r["confidence"], 1.0 if r["accuracy"] > 50 else 0.0) for r in small_rows]
small_by_conf = {}
for c, h in small_pairs:
    small_by_conf.setdefault(c, []).append(h)
small_table = [{"confidence": c, "n": len(hs), "hit_rate_proxy_accuracy_gt_50": sum(hs) / len(hs)}
               for c, hs in sorted(small_by_conf.items())]
results["training_source_of_shipped_calibrator"] = {
    "table": "predictions",
    "n_evaluated_rows": len(small_rows),
    "ground_truth_used": "accuracy column > 50 (accuracy is NOT a strict binary direction hit -- see app.py _auto_evaluate: for NEUTRAL predictions accuracy is a magnitude-proximity score, not direction correctness)",
    "by_confidence_bucket": small_table,
}

# ── 6. Hit rate / accuracy overall (direction accuracy, not calibration) ────
results["direction_accuracy_overall"] = {
    "ensemble_model_hit_rate_large_dataset": base_rate,
    "per_model_hit_rate": {},
}
cur.execute("""
    SELECT model, AVG(direction_correct) hr, COUNT(*) n
    FROM quant_errors WHERE direction_correct IS NOT NULL GROUP BY model
""")
for r in cur.fetchall():
    results["direction_accuracy_overall"]["per_model_hit_rate"][r["model"]] = {"hit_rate": r["hr"], "n": r["n"]}

# ── 7. Ensemble weights + calibrator shape summary ──────────────────────────
with open(WEIGHTS_JSON) as f:
    weights = json.load(f)
results["ensemble_weights"] = weights
results["calibrator_shape"] = {
    "n_knots": len(kx),
    "knots_x_unique": sorted(set(kx)),
    "knots_y_at_unique_x": [{"x": x, "y": ky[kx.index(x)]} for x in sorted(set(kx))],
}

# ── 8. Walk-forward backtest_runs summary ───────────────────────────────────
cur.execute("SELECT symbol, model, metrics_json, start_date, end_date FROM backtest_runs")
bt_rows = cur.fetchall()
bt_summary = []
parse_fail = 0
for r in bt_rows:
    try:
        m = json.loads(r["metrics_json"]) if r["metrics_json"] else {}
    except Exception:
        parse_fail += 1
        m = {}
    bt_summary.append({
        "symbol": r["symbol"], "model": r["model"],
        "n_trades": m.get("n_trades"), "hit_rate": m.get("hit_rate"),
        "sharpe": m.get("sharpe"), "windows": m.get("windows"),
        "start_date": r["start_date"], "end_date": r["end_date"],
    })
# aggregate by model
by_model = {}
for b in bt_summary:
    by_model.setdefault(b["model"], []).append(b)
model_agg = []
for model, items in by_model.items():
    hrs = [i["hit_rate"] for i in items if i["hit_rate"] is not None]
    trades = [i["n_trades"] for i in items if i["n_trades"] is not None]
    model_agg.append({
        "model": model, "n_runs": len(items),
        "avg_hit_rate": sum(hrs)/len(hrs) if hrs else None,
        "total_trades": sum(trades) if trades else None,
    })
results["backtest_runs_summary"] = {
    "n_runs_total": len(bt_rows), "json_parse_failures": parse_fail,
    "by_model": model_agg,
}

# ── 9. Data quality checks ──────────────────────────────────────────────────
cur.execute("SELECT COUNT(*) FROM quant_predictions WHERE confidence IS NULL")
null_conf = cur.fetchone()[0]
cur.execute("SELECT COUNT(DISTINCT symbol) FROM quant_predictions")
n_symbols = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM quant_predictions qp LEFT JOIN quant_errors qe ON qp.id=qe.prediction_id AND qe.model='ensemble' WHERE qe.id IS NULL")
unevaluated = cur.fetchone()[0]
results["data_quality"] = {
    "quant_predictions_null_confidence": null_conf,
    "distinct_symbols_in_quant_predictions": n_symbols,
    "quant_predictions_never_evaluated_as_ensemble": unevaluated,
    "quant_predictions_total": schema_info["quant_predictions"]["row_count"],
    "pct_unevaluated": unevaluated / schema_info["quant_predictions"]["row_count"],
}

with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=2, default=str)

print("WROTE", OUT_JSON)
print(json.dumps({
    "n_scored": n_scored,
    "base_rate": base_rate,
    "brier_raw": brier_raw,
    "brier_calibrated": brier_calibrated,
    "brier_naive": brier_base_rate,
}, indent=2))
