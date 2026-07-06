"""Shared figure style for The PaMaBAI Journal, Vol. 1.

Same palette as the hibrid evaluation paper so the issue reads as one system.
Print context: direct labels over legends where possible, recessive axes,
tight bounding boxes, 150 dpi.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# categorical order (fixed, never cycled): green, slate, rust, blue, lite
C = {"green": "#176043", "slate": "#5b6470", "rust": "#c2691c",
     "blue": "#3b5b8c", "lite": "#9ec6b4", "ink": "#22201b"}
ORDER = [C["green"], C["slate"], C["rust"], C["blue"], C["lite"]]

plt.rcParams.update({
    "font.size": 10.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#8a857a", "axes.linewidth": 0.8,
    "grid.color": "#e3ded2", "grid.linewidth": 0.6,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
})


def save(fig, path):
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    print("fig ->", path)
