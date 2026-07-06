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
    """Savings comparison by method/language + the reversibility verdict."""
    import statistics as st
    es = [r["saving_pct"] for r in tok if r["lang"] == "es"]
    en = [r["saving_pct"] for r in tok if r["lang"] == "en"]
    fig, ax = plt.subplots(figsize=(5.8, 3.1))
    labels = ["translation es→en\n(google backend)", "tokinensis on es\n(n=15)", "tokinensis on en\n(n=15)"]
    vals = [d["arbitrage_summary"]["mean_saving_pct"], round(st.mean(es), 1), round(st.mean(en), 1)]
    bars = ax.bar(labels, vals, color=[C["green"], C["rust"], C["rust"]], width=0.55)
    for b, v in zip(bars, vals):
        off = 0.6 if v >= 0 else -2.4
        ax.text(b.get_x() + b.get_width() / 2, v + off, f"{v}%", ha="center", fontsize=10)
    ax.axhline(0, color=C["ink"], linewidth=0.9)
    ax.text(1.5, 26, "reversibility: 0/30\n(claimed lossless — measured lossy)",
            ha="center", fontsize=8.6, color=C["rust"])
    ax.set_ylabel("mean token saving (%)")
    ax.set_ylim(-6, 40)
    ax.set_title("Mean savings by method — tokinensis is a net cost on English 47% of the time")
    ax.grid(True, axis="y")
    save(fig, os.path.join(HERE, "fig_methods.png"))


fig_arbitrage()
fig_methods()


def fig_tokenizers():
    """E1: the arbitrage across tokenizer generations."""
    import json as j
    comp = j.load(open(os.path.join(HERE, "bench", "competitors",
                                    "tokenizer_comparison_results.json")))
    import statistics as st
    rows = comp["es_en_full15"]
    tks = [("cl100k_base\n(GPT-4, 2023)", "cl100k_base", C["green"]),
           ("qwen2.5\n(2024)", "qwen2.5", C["slate"]),
           ("o200k_base\n(GPT-4o, 2024)", "o200k_base", C["rust"]),
           ("xlm-roberta\n(multiling., 2020)", "xlm-roberta-base", C["blue"])]
    fig, ax = plt.subplots(figsize=(5.9, 3.2))
    xs = range(len(tks))
    vals = [st.mean([r[f"{key}_saving_pct"] for r in rows]) for _, key, _ in tks]
    bars = ax.bar(list(xs), vals, color=[c for _, _, c in tks], width=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.5, f"{v:.1f}%", ha="center", fontsize=10)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([t for t, _, _ in tks], fontsize=8.6)
    ax.set_ylabel("mean es→en token saving (%)")
    ax.set_ylim(0, 36)
    ax.set_title("The arbitrage depends on the tokenizer's generation (same 15 prompts)")
    ax.grid(True, axis="y")
    save(fig, os.path.join(HERE, "fig_tokenizers.png"))


fig_tokenizers()
