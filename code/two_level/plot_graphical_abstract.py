#!/usr/bin/env python3
"""Graphical abstract for the Brief Report (separate composition from Fig. 1).

Schematic, not to scale.  Two rows on a common (symbolic) ratio axis:

  weighted majority games -- for every n the attainable ratios are 0, 1 and a
      discrete set inside [n/(n-2), 2^(n-1)-1]; the open interval (0,1) is
      empty, so the target ratio 1/2 of psi^n is unattainable;
  simple games -- the target IS attained (n = 6 witness), hence every such
      witness is necessarily non-weighted.

Usage:  python plot_graphical_abstract.py <outdir>
Writes <outdir>/graphical_abstract.png (2200 px wide) and .pdf.
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

RED, BLUE, GREEN, GREY = "#c0392b", "#1f4e79", "#1e7a3c", "#777777"

# symbolic x positions (not to scale)
X0, BAND_L, XHALF, BAND_R = 0.70, 1.45, 2.25, 3.05
BAR_L, BAR_R = 3.75, 9.15

fig, ax = plt.subplots(figsize=(11.0, 5.5))
ax.set_xlim(0, 10)
ax.set_ylim(0.15, 6)
ax.axis("off")


def dot(x, y, s=150, color=BLUE, z=6):
    ax.scatter([x], [y], s=s, color=color, zorder=z,
               edgecolors="white", linewidths=1.0)


# ------------------------------------------------------------------ headline
ax.text(0.04, 5.62, "Two-level Banzhaf target", fontsize=15, color="#222222",
        ha="left", va="center")
ax.text(0.04, 5.10, r"$\psi^{n}=(2,\ldots,2,1)/(2n-1)$", fontsize=21,
        color="#222222", ha="left", va="center")
ax.text(4.85, 5.13, "one voter is half as powerful as each of $n-1$ equal others",
        fontsize=12.5, color=GREY, ha="left", va="center")

ax.plot([0.04, 9.9], [4.62, 4.62], color="#dddddd", lw=1.0)

# ------------------------------------------------------------------ weighted row
YW = 3.55
ax.text(0.04, 4.24, "Weighted majority games", fontsize=15, color=BLUE,
        ha="left", va="center")
ax.text(3.02, 4.25, "no $n$ attains the target", fontsize=13,
        color=RED, ha="left", va="center", style="italic")

# empty interval
ax.add_patch(Rectangle((BAND_L, YW - 0.34), BAND_R - BAND_L, 0.68,
                       facecolor="#efefef", edgecolor="#c4c4c4",
                       hatch="////", lw=1.0, zorder=2))
ax.text(XHALF, YW - 0.52, "no attainable ratio in $(0,1)$", fontsize=11.5,
        color=GREY, ha="center", va="top")
ax.text(XHALF, YW, "×", fontsize=22, color=RED, ha="center", va="center",
        zorder=7, fontweight="bold")

# the two isolated attainable values
dot(X0, YW)
ax.text(X0, YW - 0.30, "0", fontsize=13, color=BLUE, ha="center", va="top")
ax.text(X0, YW + 0.34, "dummy voter", fontsize=10.5, color=GREY,
        ha="center", va="bottom")
dot(BAND_R, YW)
ax.text(BAND_R + 0.16, YW, "1", fontsize=13, color=BLUE, ha="left", va="center")

# the attainable range
ax.plot([BAR_L, BAR_R], [YW, YW], color=BLUE, lw=5.0,
        solid_capstyle="butt", zorder=3)
import numpy as np
rng = np.random.default_rng(7)
ax.scatter(rng.uniform(BAR_L + 0.15, BAR_R - 0.15, 46),
           YW + np.full(46, 0.075), s=11, color=BLUE, alpha=0.55, zorder=4,
           linewidths=0)
ax.text((BAR_L + BAR_R) / 2, YW + 0.34,
        r"attainable:  $n/(n-2)\ \leq\ \eta/c\ \leq\ 2^{\,n-1}-1$",
        fontsize=13.5, color=BLUE, ha="center", va="bottom")

# target ratio marker, weighted row
ax.text(XHALF, YW + 0.40, r"target ratio $1/2$", fontsize=12.5, color=RED,
        ha="center", va="bottom")

# ------------------------------------------------------------------ simple row
YS = 1.45
ax.plot([0.04, 9.9], [2.62, 2.62], color="#dddddd", lw=1.0)
ax.text(0.04, 2.24, "Simple games", fontsize=15, color=GREEN,
        ha="left", va="center")
ax.text(1.72, 2.25, "the target is attained  (6 ≤ n ≤ 18)", fontsize=13,
        color=GREEN, ha="left", va="center", style="italic")

ax.scatter([XHALF], [YS], s=520, color=GREEN, zorder=6,
           edgecolors="white", linewidths=1.5)
ax.plot([XHALF - 0.095, XHALF - 0.02, XHALF + 0.105],
        [YS + 0.005, YS - 0.085, YS + 0.105],
        color="white", lw=3.2, solid_capstyle="round",
        solid_joinstyle="round", zorder=7)
ax.text(XHALF + 0.42, YS + 0.06,
        r"$n=6$ witness with swing vector $(8,8,8,8,8,4)$",
        fontsize=13, color="#222222", ha="left", va="center")

# the 1/2 column, tying the two rows together
ax.plot([XHALF, XHALF], [YS + 0.19, YW - 0.92], color="#cccccc", lw=1.0,
        ls=(0, (2, 3)), zorder=0)

# ------------------------------------------------------------------ conclusion
ax.text(0.04, 0.62,
        "Every simple game realizing the target is therefore necessarily "
        "non-weighted: the obstruction lives in the weighted class, not in "
        "simple games.",
        fontsize=12.5, color="#222222", ha="left", va="center")

ax.text(9.9, 0.22, "schematic, not to scale", fontsize=10, color="#999999",
        ha="right", va="center")
fig.tight_layout(pad=0.15)
outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "graphical_abstract.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(outdir, "graphical_abstract.png"), dpi=200,
            bbox_inches="tight")
print("wrote graphical_abstract.pdf/.png in", outdir)
