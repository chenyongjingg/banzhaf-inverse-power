#!/usr/bin/env python3
"""Graphical abstract for the Brief Report (separate composition from Fig. 1).

Schematic, not to scale.  Two lanes share one ratio axis:

  weighted majority games -- for every n the attainable ratios are 0 (dummy
      outsider), 1, and a discrete set inside [n/(n-2), 2^(n-1)-1]; the open
      interval (0,1) is empty, so the target ratio 1/2 of psi^n is out of reach;
  simple games -- the target IS attained (n = 6 witness), hence every such
      witness is necessarily non-weighted.

Output is 2026 x 1133 px (MDPI asks for at least 1100 x 560 px).

Usage:  python plot_graphical_abstract.py <outdir>
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "pdf.fonttype": 42,
})

RED, BLUE, GREEN, GREY = "#b03a2e", "#1f4e79", "#1e7a3c", "#808080"

# symbolic x positions (not to scale)
X0, BAND_L, XHALF, BAND_R = 0.80, 1.55, 2.30, 3.00
BAR_L, BAR_R = 4.00, 9.55

YW, YS = 3.30, 1.50          # lane heights
Y_TOKEN = 0.42               # the small "n/(n-2) ... 2^(n-1)-1" tokens

fig, ax = plt.subplots(figsize=(11.0, 5.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis("off")


def dot(x, y, s=170, color=BLUE, z=6):
    ax.scatter([x], [y], s=s, color=color, zorder=z,
               edgecolors="white", linewidths=1.2)


# ------------------------------------------------------------------ headline
ax.text(0.04, 5.45,
        "A two-level Banzhaf profile is unreachable by weighted majority games",
        fontsize=16.5, color="#1a1a1a", ha="left", va="center")
ax.text(0.04, 4.98, "target", fontsize=12, color=GREY, ha="left", va="center")
ax.text(0.78, 4.97, r"$\psi^{n}=(2,\ldots,2,1)/(2n-1)$", fontsize=15,
        color="#1a1a1a", ha="left", va="center")
ax.text(3.60, 4.99, "one voter is half as powerful as each of $n-1$ equal others",
        fontsize=12, color=GREY, ha="left", va="center")
ax.plot([0.04, 9.9], [4.52, 4.52], color="#d8d8d8", lw=1.0)

# ------------------------------------------------------------------ weighted lane
ax.text(0.04, 4.06, "Weighted majority games", fontsize=13.5, color=BLUE,
        ha="left", va="center")
ax.text(2.62, 4.06, "— for every $n$", fontsize=13.5, color=BLUE,
        ha="left", va="center")

ax.add_patch(Rectangle((BAND_L, YW - 0.33), BAND_R - BAND_L, 0.66,
                       facecolor="#f0f0f0", edgecolor="#c8c8c8",
                       hatch="////", lw=1.0, zorder=2))
ax.text(XHALF, YW, "×", fontsize=21, color=RED, ha="center", va="center",
        zorder=7, fontweight="bold")

dot(X0, YW)
ax.text(X0, YW - 0.30, "0", fontsize=12.5, color=BLUE, ha="center", va="top")
ax.text(X0, YW + 0.34, "dummy", fontsize=10.5, color=GREY, ha="center",
        va="bottom")

dot(BAND_R + 0.30, YW)                      # the value 1, clear of the band
ax.text(BAND_R + 0.46, YW, "1", fontsize=12.5, color=BLUE, ha="left",
        va="center")

ax.add_patch(Rectangle((BAR_L, YW - 0.09), BAR_R - BAR_L, 0.18,
                       facecolor=BLUE, edgecolor="none", zorder=3))
rng = np.random.default_rng(7)                         # a rug of discrete values
for t in rng.uniform(BAR_L + 0.20, BAR_R - 0.20, 17):
    ax.plot([t, t], [YW + 0.12, YW + 0.22], color=BLUE, lw=1.4, zorder=4)
ax.text((BAR_L + BAR_R) / 2, YW + 0.30,
        r"attainable:  $n/(n-2)\ \leq\ \eta/c\ \leq\ 2^{\,n-1}-1$",
        fontsize=13, color=BLUE, ha="center", va="bottom")

ax.text(XHALF, YW + 0.40, r"target $1/2$", fontsize=11.5, color=RED,
        ha="center", va="bottom")
ax.text(XHALF, YW - 0.46, "nothing attainable here", fontsize=11,
        color=GREY, ha="center", va="top", style="italic")

# ------------------------------------------------------------------ simple lane
ax.plot([0.04, 9.9], [2.58, 2.58], color="#d8d8d8", lw=1.0)
ax.text(0.04, 2.20, "Simple games", fontsize=13.5, color=GREEN,
        ha="left", va="center")
ax.text(1.62, 2.20, "— the same target is attained", fontsize=13.5,
        color=GREEN, ha="left", va="center")

ax.scatter([XHALF], [YS], s=560, color=GREEN, zorder=6,
           edgecolors="white", linewidths=1.6)
ax.plot([XHALF - 0.100, XHALF - 0.022, XHALF + 0.108],
        [YS + 0.008, YS - 0.092, YS + 0.112],
        color="white", lw=3.2, solid_capstyle="round",
        solid_joinstyle="round", zorder=7)
ax.text(XHALF + 0.40, YS + 0.02,
        r"$n=6$: swing vector $(8,8,8,8,8,4)$",
        fontsize=12.5, color="#1a1a1a", ha="left", va="center")

# ------------------------------------------------------------------ conclusion
ax.plot([0.04, 9.9], [1.05, 1.05], color="#d8d8d8", lw=1.0)
ax.text(0.04, 0.55,
        "So every simple game that realizes the target is necessarily non-weighted: "
        "the obstruction lies in the weighted class, not in the games.",
        fontsize=12, color="#1a1a1a", ha="left", va="center")
ax.text(9.9, 0.16, "schematic, not to scale", fontsize=9.5, color="#a0a0a0",
        ha="right", va="center")

fig.tight_layout(pad=0.12)
outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "graphical_abstract.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(outdir, "graphical_abstract.png"), dpi=200,
            bbox_inches="tight")
print("wrote graphical_abstract.pdf/.png in", outdir)
