#!/usr/bin/env python3
"""Graphical abstract.

"Prescribed Banzhaf power: closed-form games, congruence conditions, and
certified weighted obstructions"

Elsevier spec for graphical abstracts: minimum 531 x 1328 px (h x w), i.e. a
wide banner with aspect w/h = 2.5. This script renders a vector PDF plus a
300-dpi PNG. Reproducible: python graphical_abstract.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# --- validated palette (dataviz reference, light mode) -----------------------
INK      = "#0b0b0b"   # text primary
INK_SUB  = "#52514e"   # text secondary
SURFACE  = "#fcfcfb"
PANEL    = "#f4f3f0"   # card fill
EDGE     = "#d8d6d2"   # card border
BLUE     = "#2a78d6"   # categorical 1  (target / actual)
ORANGE   = "#eb6834"   # categorical 2  (special player)
GREEN    = "#008300"   # status good    (realized)
RED      = "#e34948"   # status critical(infeasible)

W, H = 100.0, 40.0  # abstract coordinate space (aspect 2.5)

fig = plt.figure(figsize=(13.28, 5.31), dpi=100)
fig.patch.set_facecolor(SURFACE)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H)
ax.axis("off")

def card(x0, y0, x1, y1, facecolor=PANEL, edgecolor=EDGE, lw=1.4, r=1.6):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                 boxstyle=f"round,pad=0,rounding_size={r}",
                 facecolor=facecolor, edgecolor=edgecolor, lw=lw, zorder=1))

def text(x, y, s, size=7.2, color=INK, weight="normal", ha="left", va="center",
         zorder=3, family="DejaVu Sans"):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
            ha=ha, va=va, zorder=zorder, family=family)

def arrow(x0, y0, x1, y1, color=INK_SUB, lw=1.6, style="-|>", zorder=2):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style,
                 mutation_scale=11, color=color, lw=lw, zorder=zorder))

def lane(x0, y0, x1, y1, fill, edge, title, body, mark, mark_color):
    """A rounded 'lane' box with a status mark and two lines of text."""
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                 boxstyle="round,pad=0,rounding_size=1.3",
                 facecolor=fill, edgecolor=edge, lw=1.3, zorder=2))
    # status mark on the left
    ax.add_patch(plt.Circle((x0 + 1.6, (y0 + y1) / 2), 1.1,
                 facecolor=mark_color, edgecolor="none", zorder=3))
    ax.text(x0 + 1.6, (y0 + y1) / 2, mark, fontsize=8, color="white",
            ha="center", va="center", weight="bold", zorder=4)
    text(x0 + 3.4, y1 - 2.6, title, size=6.8, weight="bold")
    text(x0 + 3.4, y0 + 2.2, body, size=5.9, color=INK_SUB)

# ============================== Panel 1: problem =============================
card(3.2, 5.0, 30.0, 37.2)
text(5.2, 34.6, "Inverse Banzhaf voting-design", size=8.2, weight="bold")
text(5.2, 31.6, "given a target power distribution, construct a", size=5.9, color=INK_SUB)
text(5.2, 29.9, "realizing rule, or certify that none exists", size=5.9, color=INK_SUB)

# mini bar chart of the egalitarian benchmark psi^n = (2,...,2,1)/(2n-1)
bx0, bbase, bh = 5.4, 8.0, 16.0
n = 8                                  # illustrative: 7 players at 2, 1 at 1
bw = 1.55
for k in range(n):
    special = (k == n - 1)
    h = bh / 2 if special else bh
    c = ORANGE if special else BLUE
    x = bx0 + k * (bw + 1.05)
    ax.add_patch(plt.Rectangle((x, bbase), bw, h, facecolor=c,
                 edgecolor="none", zorder=2))
    ax.text(x + bw / 2, bbase + h + 1.1, "1" if special else "2",
            fontsize=6.4, ha="center", va="bottom", color=c, weight="bold", zorder=3)
ax.plot([bx0 - 0.8, bx0 + (n - 1) * (bw + 1.05) + bw + 0.8],
        [bbase, bbase], color=INK_SUB, lw=1.1, zorder=2)
text(bx0 + 0.3, bbase - 1.7, "target ψⁿ :  n−1 players 2×,  one player 1×",
     size=5.9, color=INK_SUB)

# ============================ Panel 2: method ================================
card(34.2, 5.0, 64.0, 37.2)
text(36.2, 34.6, "Two rule classes, opposite verdicts", size=8.2, weight="bold")

# green lane: simple games / W-family
lane(36.2, 22.2, 62.0, 31.4, "#e7f3e7", GREEN,
     "Simple games  (W-family)",
     "explicit game for all n ≥ 6 and for (a,…,a,b)",
     "✓", GREEN)

# red lane: weighted majority games
lane(36.2, 10.2, 62.0, 19.4, "#fbeaea", RED,
     "Weighted majority games",
     "CP-SAT certifies: none realizes the target, 6 ≤ n ≤ 10",
     "✗", RED)

# arrows: problem feeds both lanes
arrow(27.6, 22.0, 35.6, 26.8, color=GREEN, lw=1.7)
arrow(27.6, 20.0, 35.6, 14.8, color=RED,  lw=1.7)

# ========================= Panel 3: application ==============================
card(68.2, 5.0, 96.8, 37.2)
text(70.2, 34.6, "Exact case study", size=8.2, weight="bold")
text(70.2, 31.9, "weighted EU Council (EEC-6/9/10, EU-15)", size=5.9, color=INK_SUB)

# actual vs redesign L1 distance to target (schematic horizontal bars)
lab_y = 27.4
text(70.2, lab_y, "actual power", size=5.9, color=INK_SUB)
ax.add_patch(plt.Rectangle((74.8, lab_y - 0.75), 15.5, 1.5,
             facecolor=BLUE, edgecolor="none", zorder=2))
text(91.6, lab_y, "L₁ ≈ 0.34–0.42", size=5.6, color=INK_SUB)

lab_y = 22.6
text(70.2, lab_y, "best redesign", size=5.9, color=INK_SUB)
ax.add_patch(plt.Rectangle((74.8, lab_y - 0.75), 4.6, 1.5,
             facecolor=GREEN, edgecolor="none", zorder=2))
text(80.7, lab_y, "L₁ ≈ 0.11  (3× closer)", size=5.6, color=INK_SUB)

# takeaway lines
text(70.2, 17.4, "real councils are far from egalitarian", size=5.9, color=INK_SUB)
text(70.2, 15.6, "no weighted redesign reaches the target", size=5.9, color=INK_SUB)
text(70.2, 13.8, "certified optimal redesign improves ~3x", size=5.9, color=INK_SUB)

# footer
text(3.2, 2.2, "Every claim is reproducible from the companion code package.",
     size=5.6, color=INK_SUB)

fig.savefig("graphical_abstract.pdf", format="pdf", facecolor=SURFACE)
fig.savefig("graphical_abstract.png", format="png", dpi=300, facecolor=SURFACE)
print("wrote graphical_abstract.pdf and graphical_abstract.png")
print("PNG size (px):", matplotlib.image.imread("graphical_abstract.png").shape[1],
      "x", matplotlib.image.imread("graphical_abstract.png").shape[0])
