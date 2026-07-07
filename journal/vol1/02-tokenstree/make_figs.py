"""Figures for the TokensTree paper, from bench/*.json."""
import json
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "style"))
from figstyle import C, plt, save

lat = json.load(open(os.path.join(HERE, "bench", "latency_raw.json")))
db = json.load(open(os.path.join(HERE, "bench", "db_stats.json")))


def fig_latency():
    """Point-range: p50 dot, p90-p99 whisker per endpoint."""
    names = {"health": "/health", "root": "/", "api_posts": "/api/v1/posts",
             "api_agents_rankings": "/api/v1/agents/rankings"}
    stats = []
    for key, label in names.items():
        tot = sorted(s["time_total"] * 1000 for s in lat[key]["samples"])
        n = len(tot)
        stats.append((label, tot[n // 2], tot[int(n * 0.9)], tot[min(n - 1, int(n * 0.99))]))
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    ys = range(len(stats))
    for y, (label, p50, p90, p99) in zip(ys, stats):
        ax.plot([p50, p99], [y, y], color=C["lite"], linewidth=3, zorder=2, solid_capstyle="round")
        ax.scatter([p50], [y], s=60, color=C["green"], zorder=3)
        ax.scatter([p90], [y], s=34, color=C["slate"], zorder=3)
        ax.scatter([p99], [y], s=34, color=C["rust"], zorder=3)
        ax.text(p99 + 1.5, y, f"p99 {p99:.0f}", va="center", fontsize=8.5, color=C["rust"])
    ax.set_yticks(list(ys))
    ax.set_yticklabels([s[0] for s in stats], fontfamily="monospace", fontsize=9)
    ax.set_xlabel("client latency (ms) — p50 (green) / p90 (slate) / p99 (rust)")
    ax.set_title("Public API latency, 30 samples/endpoint (all HTTP 200)")
    ax.grid(True, axis="x")
    ax.invert_yaxis()
    save(fig, os.path.join(HERE, "fig_latency.png"))


def fig_scale():
    """Log-scale horizontal bars of table row counts (the platform's shape)."""
    rows = [("messages", 671494), ("votes", 288485), ("follows", 112504),
            ("chat members", 93138), ("chats", 27498), ("posts", 20004),
            ("agents", 11529), ("reputation events", 10517), ("users (humans)", 8012)]
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ys = range(len(rows))
    ax.barh(list(ys), [r[1] for r in rows], color=C["green"], height=0.62)
    for y, (_, v) in zip(ys, rows):
        ax.text(v * 1.06, y, f"{v:,}", va="center", fontsize=8.5)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([r[0] for r in rows], fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(right=4e6)
    ax.set_xlabel("rows (log scale) — 31 GB PostgreSQL, 49 tables")
    ax.set_title("What 11,529 agents produce: platform data shape (July 2026)")
    ax.invert_yaxis()
    ax.grid(True, axis="x")
    save(fig, os.path.join(HERE, "fig_scale.png"))


fig_latency()
fig_scale()


def _social(name):
    import json as j
    return j.load(open(os.path.join(HERE, "bench", "social", name)))


def fig_diurnal():
    t = _social("04_temporal_signature.json")["messages_per_hour_of_day_utc"]
    hours = sorted(int(h) for h in t if h.isdigit())
    vals = [t[str(h)] / 1000 for h in hours]
    fig, ax = plt.subplots(figsize=(6.0, 2.9))
    ax.plot(hours, vals, color=C["green"], linewidth=1.8)
    ax.fill_between(hours, vals, color=C["green"], alpha=0.12)
    ax.set_xticks(range(0, 24, 3))
    ax.set_xlabel("hour of day (UTC)")
    ax.set_ylabel("messages (thousands)")
    ax.set_title("The circadian fingerprint: agent messages follow a 12× human daily\nrhythm — machines that never sleep, run by owners who do")
    ax.grid(True)
    save(fig, os.path.join(HERE, "fig_diurnal.png"))


def fig_weekly_growth():
    raw = _social("04_temporal_signature.json")["messages_per_week"]["series"]
    items = sorted(raw.items())[:-1]  # drop the final partial week
    dates = [d for d, _ in items]
    xs = range(len(items))
    vals = [max(1, n) for _, n in items]
    fig, ax = plt.subplots(figsize=(6.1, 3.0))
    ax.plot(list(xs), vals, color=C["green"], linewidth=1.6)
    ax.set_yscale("log")
    peak_i = max(xs, key=lambda i: vals[i])
    ax.scatter([peak_i], [vals[peak_i]], color=C["rust"], zorder=3, s=40)
    ax.annotate(f"peak {vals[peak_i]:,}/wk\nthen collapse ×30", (peak_i, vals[peak_i]),
                textcoords="offset points", xytext=(-95, -22), fontsize=8.5, color=C["rust"])
    step = max(1, len(items)//7)
    labels = [dates[i] for i in range(0, len(items), step)]
    ax.set_xticks(list(range(0, len(items), step)))
    ax.set_xticklabels(labels, fontsize=7.5, rotation=30)
    ax.set_ylabel("messages/week (log)")
    ax.set_title("Fourteen months of growth, one unexplained cliff (reported as found)")
    ax.grid(True)
    save(fig, os.path.join(HERE, "fig_weekly.png"))


def fig_degrees():
    g = _social("03_graph_shape.json")["follows"]
    fig, ax = plt.subplots(figsize=(5.7, 2.9))
    stats = [("in-degree", g["in_degree"], C["green"]), ("out-degree", g["out_degree"], C["rust"])]
    for i, (label, dd, color) in enumerate(stats):
        pts = [("p50", dd.get("p50")), ("p90", dd.get("p90")), ("p99", dd.get("p99")), ("max", dd.get("max"))]
        xs = [x for x, v in pts if v]
        vals = [v for _, v in pts if v]
        ax.plot(range(len(vals)), vals, marker="o", color=color, label=label, linewidth=1.6)
    ax.set_yscale("log")
    ax.set_xticks(range(4)); ax.set_xticklabels(["p50", "p90", "p99", "max"])
    ax.set_ylabel("degree (log)")
    ax.set_title("Broadcast without reciprocity: in-degree tails to 3,424 while\nout-degree is capped near 39 (mutual edges: 2.1%)")
    ax.legend(frameon=False)
    ax.grid(True)
    save(fig, os.path.join(HERE, "fig_degrees.png"))


fig_diurnal()
fig_weekly_growth()
fig_degrees()
