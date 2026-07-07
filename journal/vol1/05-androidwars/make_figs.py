"""Figures for the AndroidWars paper, from bench/live_match_result.json."""
import json
import os
import statistics as st
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "style"))
from figstyle import C, plt, save

d = json.load(open(os.path.join(HERE, "bench", "live_match_result.json")))


def fig_latency():
    groups = [("register", d["register"], C["rust"]),
              ("orders (POST)", d["orders"], C["green"]),
              ("state, agent A", d["state_a"], C["slate"]),
              ("state, agent B", d["state_b"], C["slate"])]
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    for y, (label, rows, color) in enumerate(groups):
        lats = sorted(r["latency_ms"] for r in rows if r.get("status") == 200)
        ax.scatter(lats, [y + (i % 7 - 3) * 0.035 for i in range(len(lats))],
                   s=14, color=color, alpha=0.35, zorder=2)
        p50 = st.median(lats)
        ax.vlines(p50, y - 0.28, y + 0.28, color=C["ink"], linewidth=2, zorder=3)
        ax.text(p50, y + 0.33, f"p50 {p50:.0f}ms", fontsize=8, ha="center")
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([g[0] for g in groups], fontsize=9)
    ax.set_xlabel("client latency (ms), via nginx + TLS on the host")
    ax.set_title("REST latency during a live 3-minute match (all HTTP 200)")
    ax.invert_yaxis()
    ax.grid(True, axis="x")
    save(fig, os.path.join(HERE, "fig_latency.png"))


def fig_ticks():
    sa = [s for s in d["state_a"] if s.get("status") == 200 and isinstance(s.get("body"), dict)]
    t0 = sa[0]["ts"]
    xs = [s["ts"] - t0 for s in sa]
    ys = [s["body"]["tick"] - sa[0]["body"]["tick"] for s in sa]
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    ax.plot(xs, ys, color=C["green"], linewidth=1.6)
    rate = ys[-1] / xs[-1]
    ax.plot([0, xs[-1]], [0, xs[-1] * rate], color=C["slate"], linewidth=1, linestyle="--")
    ax.text(xs[-1] * 0.55, ys[-1] * 0.4, f"{rate:.2f} ticks/s\n(tick period 2.0 s)",
            fontsize=9.5, color=C["ink"])
    ax.set_xlabel("wall-clock time (s)")
    ax.set_ylabel("simulation ticks elapsed")
    ax.set_title("The world advances in fixed 2-second ticks, independent of agent activity")
    ax.grid(True)
    save(fig, os.path.join(HERE, "fig_ticks.png"))


fig_latency()
fig_ticks()


def fig_economy():
    import json as j
    d = j.load(open(os.path.join(HERE, "bench", "gameplay", "timeseries.json")))
    a = d["alpha"]
    t0 = a[0]["tick"]
    xs = [s["tick"] - t0 for s in a]
    fig, ax = plt.subplots(figsize=(6.0, 3.1))
    ax.plot(xs, [s["fuel"] for s in a], color=C["green"], linewidth=1.8, label="fuel")
    ax.plot(xs, [s["ammo"] for s in a], color=C["rust"], linewidth=1.4, label="ammo")
    houses = [h["tick"] for h in d["house_build_ticks"]["alpha"] if h["n_structures"] > 0]
    for ht in houses:
        ax.axvline(ht - t0, color=C["slate"], linewidth=0.8, linestyle=":", alpha=0.7)
    ax.text(houses[-1] - t0 + 1, 88, "house built (x5)", fontsize=8, color=C["slate"], rotation=90, va="top")
    ax.set_xlabel("simulation ticks since match start")
    ax.set_ylabel("resource units (agent alpha)")
    ax.set_title("The bootstrapping economy: fuel funds expansion (+78), ammo runs a\nsawtooth deficit (−22); five houses on a fixed 16–20-tick cadence")
    ax.legend(frameon=False, loc="upper left")
    ax.grid(True)
    save(fig, os.path.join(HERE, "fig_economy.png"))


def fig_leaderboard():
    import json as j
    d = j.load(open(os.path.join(HERE, "bench", "gameplay", "leaderboard.json")))
    entries = d["full_leaderboard"]
    scores = sorted((e.get("highscore", 0) for e in entries), reverse=True)
    fig, ax = plt.subplots(figsize=(5.9, 3.0))
    colors = [C["green"] if s == 14 else C["slate"] for s in scores]
    ax.bar(range(len(scores)), scores, color=colors, width=0.85)
    ax.axhline(10, color=C["ink"], linewidth=1, linestyle="--")
    ax.text(len(scores) - 1, 10.6, "median 10", ha="right", fontsize=8.5)
    ax.set_xlabel("rank (top 100 agents, round 1)")
    ax.set_ylabel("score")
    ax.set_title("The population: 100-agent leaderboard; our 3-minute agents (green, 14)\nland just above the median")
    ax.grid(True, axis="y")
    save(fig, os.path.join(HERE, "fig_leaderboard.png"))


fig_economy()
fig_leaderboard()
