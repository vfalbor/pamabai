"""Figures for the trading-pipeline audit paper, from bench/calibration_results.json."""
import json
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "style"))
from figstyle import C, plt, save

d = json.load(open(os.path.join(HERE, "bench", "calibration_results.json")))
rel = d["reliability_diagram_raw_confidence_deciles"]
core = d["calibration_core"]


def fig_reliability():
    fig, ax = plt.subplots(figsize=(4.9, 4.4))
    ax.plot([0, 1], [0, 1], color=C["slate"], linewidth=1, linestyle="--", zorder=1)
    ax.text(0.86, 0.9, "perfect\ncalibration", fontsize=8, color=C["slate"], ha="center")
    xs = [r["mean_predicted_prob"] for r in rel]
    ys = [r["observed_freq"] for r in rel]
    ax.plot(xs, ys, color=C["green"], linewidth=1.6, zorder=2)
    ax.scatter(xs, ys, s=42, color=C["green"], zorder=3)
    base = core["base_rate_direction_correct"]
    ax.axhline(base, color=C["rust"], linewidth=1, linestyle=":")
    ax.text(0.985, base + 0.015, f"base rate {base:.3f}", fontsize=8, color=C["rust"], ha="right")
    ax.set_xlabel("mean predicted probability (per decile of raw confidence)")
    ax.set_ylabel("observed frequency (direction correct)")
    ax.set_xlim(-0.02, 1.0)
    ax.set_ylim(-0.02, 1.0)
    ax.set_title(f"Reliability diagram, n={core['n_scored_ensemble_predictions']:,}\n"
                 "(64,562 per decile): confidence carries no information")
    ax.grid(True)
    save(fig, os.path.join(HERE, "fig_reliability.png"))


def fig_brier():
    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    labels = ["constant\nbase rate", "raw\nconfidence", "isotonic-\n\"calibrated\""]
    vals = [core["brier_naive_constant_base_rate"], core["brier_raw_confidence"],
            core["brier_isotonic_calibrated_confidence"]]
    cols = [C["slate"], C["rust"], C["rust"]]
    bars = ax.bar(labels, vals, color=cols, width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.006, f"{v:.3f}", ha="center", fontsize=10)
    ax.set_ylabel("Brier score (lower is better)")
    ax.set_title("Both confidence signals lose to the do-nothing baseline;\nthe shipped calibrator makes it worse")
    ax.grid(True, axis="y")
    save(fig, os.path.join(HERE, "fig_brier.png"))


def fig_hitrates():
    per = d["direction_accuracy_overall"]["per_model_hit_rate"]
    items = sorted(per.items(), key=lambda kv: -kv[1]["hit_rate"])
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    ys = range(len(items))
    ax.barh(list(ys), [v["hit_rate"] for _, v in items], color=C["green"], height=0.6)
    for y, (name, v) in zip(ys, items):
        ax.text(v["hit_rate"] + 0.002, y, f'{v["hit_rate"]:.3f}  (n={v["n"]:,})',
                va="center", fontsize=8.2)
    ax.axvline(0.5, color=C["ink"], linewidth=1.1, linestyle="--")
    ax.text(0.5005, len(items) - 0.4, "coin flip", fontsize=8.5, rotation=90, va="top")
    ax.set_yticks(list(ys))
    ax.set_yticklabels([k for k, _ in items], fontsize=9, fontfamily="monospace")
    ax.set_xlim(0.45, 0.56)
    ax.set_xlabel("direction hit rate")
    ax.set_title("Per-model direction accuracy: statistically flat around 0.5")
    ax.invert_yaxis()
    ax.grid(True, axis="x")
    save(fig, os.path.join(HERE, "fig_hitrates.png"))


fig_reliability()
fig_brier()
fig_hitrates()
