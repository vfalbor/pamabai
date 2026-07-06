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
