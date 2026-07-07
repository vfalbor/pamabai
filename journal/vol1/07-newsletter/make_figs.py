"""Figures for the LLM Daily Review paper, from bench/corpus_stats.json."""
import json
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "style"))
from figstyle import C, plt, save

d = json.load(open(os.path.join(HERE, "bench", "corpus_stats.json")))


def fig_scores():
    """Score histogram from the agent's bucket counts."""
    buckets = [("10-19", 1), ("20-29", 0), ("30-39", 17), ("40-49", 77),
               ("50-59", 213), ("60-69", 196), ("70-79", 56), ("80-89", 1)]
    fig, ax = plt.subplots(figsize=(5.8, 3.1))
    xs = range(len(buckets))
    ax.bar(list(xs), [b[1] for b in buckets], color=C["green"], width=0.7)
    for x, (_, v) in zip(xs, buckets):
        if v:
            ax.text(x, v + 2, str(v), ha="center", fontsize=8.5)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([b[0] for b in buckets], fontsize=9)
    ax.set_xlabel("weighted score (0–100)")
    ax.set_ylabel("apps")
    ax.set_title("Score distribution over 561 reviewed apps (mean 58.1, median 58)")
    ax.grid(True, axis="y")
    save(fig, os.path.join(HERE, "fig_scores.png"))


def fig_testability():
    """The honesty chart: what 'tested' actually meant."""
    rows = [("no tests executed", 261, 46.5, C["rust"]),
            ("tests ran, none passed", 197, 35.1, C["slate"]),
            ("partial pass", 73, 13.0, C["lite"]),
            ("all tests passed", 30, 5.3, C["green"])]
    fig, ax = plt.subplots(figsize=(5.8, 2.6))
    ys = range(len(rows))
    ax.barh(list(ys), [r[1] for r in rows], color=[r[3] for r in rows], height=0.6)
    for y, (label, v, pct, _) in zip(ys, rows):
        ax.text(v + 4, y, f"{v} ({pct}%)", va="center", fontsize=9)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([r[0] for r in rows], fontsize=9)
    ax.set_xlim(right=330)
    ax.set_xlabel("apps (n=561)")
    ax.set_title("What “tested” actually meant: sandbox test outcomes")
    ax.invert_yaxis()
    ax.grid(True, axis="x")
    save(fig, os.path.join(HERE, "fig_testability.png"))


def fig_criteria():
    """Mean per-criterion score (0-10), sorted, with weights annotated."""
    crit = [("hn_sentiment", 7.25, 15), ("novelty", 7.37, 11),
            ("current_relevance", 7.16, 11), ("differentiation", 6.30, 11),
            ("performance", 5.17, 10), ("documentation", 5.74, 7),
            ("maturity", 5.03, 7), ("ease_of_integration", 4.97, 8),
            ("community", 4.66, 7), ("system_requirements", 4.57, 5),
            ("ease_of_use", 3.23, 8)]
    crit.sort(key=lambda r: -r[1])
    fig, ax = plt.subplots(figsize=(5.9, 3.4))
    ys = range(len(crit))
    ax.barh(list(ys), [r[1] for r in crit], color=C["green"], height=0.62)
    for y, (name, v, w) in zip(ys, crit):
        ax.text(v + 0.08, y, f"{v:.2f}  (w={w})", va="center", fontsize=8.3)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([r[0].replace("_", " ") for r in crit], fontsize=8.6)
    ax.set_xlim(0, 9.2)
    ax.set_xlabel("mean criterion score (0–10) across corpus · w = weight/100")
    ax.set_title("The 11 criteria: hype scores high, usability scores low")
    ax.invert_yaxis()
    ax.grid(True, axis="x")
    save(fig, os.path.join(HERE, "fig_criteria.png"))


fig_scores()
fig_testability()
fig_criteria()


def fig_weekly():
    import json as j
    d = j.load(open(os.path.join(HERE, "bench", "corpus_stats.json")))
    wk = d["reviews_per_iso_week"]
    labels = [k.replace("2026-", "") for k in wk]
    fig, ax = plt.subplots(figsize=(5.9, 2.6))
    ax.bar(range(len(wk)), list(wk.values()), color=C["green"], width=0.7)
    ax.axhline(sum(wk.values()) / len(wk), color=C["ink"], linewidth=1, linestyle="--")
    ax.text(len(wk) - 0.4, sum(wk.values()) / len(wk) + 1.2,
            f"mean {sum(wk.values())/len(wk):.0f}/week", ha="right", fontsize=8.5)
    ax.set_xticks(range(len(wk)))
    ax.set_xticklabels(labels, fontsize=8, rotation=45)
    ax.set_ylabel("apps reviewed")
    ax.set_title("Review volume by ISO week: 13 consecutive weeks, no gaps")
    ax.grid(True, axis="y")
    save(fig, os.path.join(HERE, "fig_weekly.png"))


fig_weekly()
