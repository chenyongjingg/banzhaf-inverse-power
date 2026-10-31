#!/usr/bin/env python3
"""Figure for the Brief Report: the exact image R_n of the two-level ratio.

For a weighted majority game v on n voters whose Banzhaf vector is two-level,
the attainable values of the ratio eta/c (outsider's swing count over a bloc
member's) are exactly the elements of R_n computed by two_level_image.py.

The plot draws R_n for n = 6..12 on a logarithmic axis, shades the empty
interval (0, 1), and marks the target ratio 1/2 of psi^n = (2,...,2,1)/(2n-1).

Usage:
    python plot_ratio_image.py <outdir>

Produces <outdir>/figure.pdf and <outdir>/figure.png.
"""
import os
import sys
from fractions import Fraction

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import two_level_image as tl  # noqa: E402

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8.0,
    "axes.linewidth": 0.7,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "pdf.fonttype": 42,
})

NS = list(range(6, 13))
DATA = {n: sorted(tl.ratio_set(n)) for n in NS}

# sanity checks against Table 1 of the manuscript
for n in NS:
    vals = DATA[n]
    assert vals[0] == 0 and vals[1] == 1, (n, vals[:2])
    assert vals[2] == Fraction(n, n - 2), (n, vals[2])
    assert vals[-1] == 2 ** (n - 1) - 1, (n, vals[-1])
    assert Fraction(1, 2) not in vals

X0 = 0.205          # synthetic position of the value 0 (a separate column)
EDGE = 0.235        # right edge of that column / left edge of the shaded band
RED = "#c0392b"
BLUE = "#1f4e79"

fig, ax = plt.subplots(figsize=(6.1, 2.55))
ax.set_xscale("log")
ax.set_xlim(0.15, 12000)
ax.set_ylim(len(NS) - 0.6, -0.8)

# the empty interval (0, 1): no weighted game realizes a ratio inside it
ax.axvspan(EDGE, 1.0, color="#ececec", zorder=0, lw=0)

# reference lines
ax.axvline(1.0, color="#999999", lw=0.8, zorder=1)
ax.axvline(0.5, color=RED, lw=1.0, ls=(0, (4, 2)), zorder=1)

for i, n in enumerate(NS):
    xs = [X0 if v == 0 else float(v) for v in DATA[n]]
    ax.scatter(xs, [i] * len(xs), s=14, color=BLUE, zorder=3,
               edgecolors="white", linewidths=0.3)
    # number of attainable ratios for this n (Table 1 counts positives only)
    ax.text(12500, i, str(len(DATA[n])), ha="left", va="center",
            fontsize=7.2, color="#555555", clip_on=False)

ax.set_yticks(range(len(NS)))
ax.set_yticklabels([f"n = {n}" for n in NS])
ax.set_yticks([], minor=True)

ticks = [X0, 0.5, 1, 2, 5, 10, 50, 100, 500, 2047]
labels = ["0", "1/2", "1", "2", "5", "10", "50", "100", "500", "2047"]
ax.set_xticks(ticks)
ax.set_xticklabels(labels)
ax.minorticks_off()
for lab in ax.get_xticklabels():
    if lab.get_text() == "1/2":
        lab.set_color(RED)

ax.text(0.545, -0.5, r"target $\psi^{n}$", color=RED, fontsize=6.2,
        ha="center", va="center")
ax.set_xlabel(r"attainable ratio $\eta/c$ of a two-level Banzhaf profile"
              "  (the value 0 in a separate column at left)", fontsize=7.6)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0, pad=2)
ax.tick_params(axis="x", pad=2)

fig.tight_layout(pad=0.2)
outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "figure.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(outdir, "figure.png"), dpi=600, bbox_inches="tight")
print("wrote", os.path.join(outdir, "figure.pdf"), "and figure.png")
