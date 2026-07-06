"""Figures for the TokenTranslation paper, from bench/raw_measurements.json."""
import json
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "style"))
from figstyle import C, plt, save

d = json.load(open(os.path.join(HERE, "bench", "raw_measurements.json")))
rows = d["arbitrage_rows"]
tok = d["tokinensis_rows"]


def fig_arbitrage():
    cats = {"instruction": C["green"], "qa": C["slate"], "technical": C["rust"]}
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    xs, ys, colors = [], [], []
    for i, r in enumerate(rows):
        xs.append(i)
        ys.append(r["saving_pct_es_to_en"])
        cat = r["category"] if r["category"] in cats else ("qa" if r["category"].lower().startswith("q") else r["category"])
        colors.append(cats.get(cat, C["blue"]))
    ax.bar(xs, ys, color=colors, width=0.7)
    mean = d["arbitrage_summary"]["mean_saving_pct"]
    ax.axhline(mean, color=C["ink"], linewidth=1.2, linestyle="--")
    ax.text(len(xs) - 0.4, mean + 0.7, f"mean {mean}%", ha="right", fontsize=9)
    ax.set_xticks(xs)
    ax.set_xticklabels([r["id"] for r in rows], rotation=55, ha="right", fontsize=7.2)
    ax.set_ylabel("token saving es→en (%)")
    ax.set_title("Token arbitrage: Spanish→English saving per prompt (cl100k_base), n=15")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in cats.values()]
    ax.legend(handles, list(cats.keys()), frameon=False, fontsize=8.5, ncol=3)
    ax.grid(True, axis="y")
    save(fig, os.path.join(HERE, "fig_arbitrage.png"))


def fig_methods():
    """Savings comparison + the reversibility verdict."""
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    labels = ["translation es→en\n(google backend)", "tokinensis encoding\n(es+en, n=30)"]
    vals = [d["arbitrage_summary"]["mean_saving_pct"], d["tokinensis_summary"]["mean_saving_pct"]]
    bars = ax.bar(labels, vals, color=[C["green"], C["rust"]], width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.5, f"{v}%", ha="center", fontsize=10)
    ax.text(1, vals[1] + 6.5, "reversibility: 0/30\n(claimed lossless — measured lossy)",
            ha="center", fontsize=8.6, color=C["rust"])
    ax.set_ylabel("mean token saving (%)")
    ax.set_ylim(0, 42)
    ax.set_title("Mean savings by method — and the property that failed")
    ax.grid(True, axis="y")
    save(fig, os.path.join(HERE, "fig_methods.png"))


fig_arbitrage()
fig_methods()
