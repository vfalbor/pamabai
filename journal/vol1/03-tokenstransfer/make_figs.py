"""Figures for the TokensTransfer paper, from bench/compress_benchmark_raw.json."""
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "style"))
from figstyle import C, plt, save

d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "bench", "compress_benchmark_raw.json")))
samples = d["raw_samples"]
sizes = sorted({s["size_chars"] for s in samples})


def fig_latency():
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    for i, size in enumerate(sizes):
        lats = sorted(s["client_latency_ms"] for s in samples if s["size_chars"] == size)
        # drop the single cold-start outlier from the jitter cloud but note max separately
        ax.scatter([i] * len(lats), lats, s=26, color=C["green"], alpha=0.55, zorder=3)
        p50 = lats[len(lats) // 2]
        ax.hlines(p50, i - 0.22, i + 0.22, color=C["ink"], linewidth=2, zorder=4)
    ax.set_xticks(range(len(sizes)))
    ax.set_xticklabels([f"{s:,}" for s in sizes])
    ax.set_xlabel("payload size (characters)")
    ax.set_ylabel("client latency (ms)")
    ax.set_yscale("log")
    ax.set_title("Fallback-mode /compress latency is flat in payload size (n=10/size; bar = median)")
    ax.grid(True, axis="y")
    save(fig, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig_latency.png"))


def fig_tokens():
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    w = 0.38
    xs = range(len(sizes))
    to = [next(s["tokens_original"] for s in samples if s["size_chars"] == z) for z in sizes]
    tc = [next(s["tokens_compressed"] for s in samples if s["size_chars"] == z) for z in sizes]
    ax.bar([x - w / 2 for x in xs], to, w, label="tokens in", color=C["slate"])
    ax.bar([x + w / 2 for x in xs], tc, w, label="tokens returned", color=C["green"])
    for x, (a, b) in zip(xs, zip(to, tc)):
        ax.text(x - w / 2, a, f"{a:,}", ha="center", va="bottom", fontsize=8.5)
        ax.text(x + w / 2, b, f"{b:,}", ha="center", va="bottom", fontsize=8.5)
    ax.axhline(300, color=C["rust"], linewidth=1.2, linestyle="--")
    ax.text(len(sizes) - 0.55, 315, "target_token = 300", color=C["rust"], fontsize=9)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([f"{s:,}" for s in sizes])
    ax.set_xlabel("payload size (characters)")
    ax.set_ylabel("tokens (cl100k_base)")
    ax.set_title("Fallback truncation discards content above the token budget (n=10/size)")
    ax.legend(frameon=False)
    save(fig, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig_tokens.png"))


fig_latency()
fig_tokens()
