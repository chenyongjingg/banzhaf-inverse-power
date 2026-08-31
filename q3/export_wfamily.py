# -*- coding: utf-8 -*-
"""Export full W-family data for 6 <= n <= 80: for each n produce (c, G, F, method)
with brute-force swing verification, merging the 6 non-closed-form values
(n = 8,10,11,12,15,18, the deg+r=D class) from appendix-data.json.

Writes ../data/appendix-data-n80.json (extended machine-readable data) and prints
the coverage table.  Usage: python export_wfamily.py
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wfamily_gen as W

APPDATA = r"../data/appendix-data.json"
OUT = r"../data/appendix-data-n80.json"

with open(APPDATA, encoding="utf-8") as f:
    app = json.load(f)

rows = []
out = {}
for n in range(6, 81):
    r = n % 7
    res = None
    if r in (0, 2, 3, 6):
        res = W.complement_edge(n)
    if res is None and r in (1, 4, 5):
        res = W.triangle(n)
    if res is not None:
        G, F, c, method = res
        ok, msg = W.verify(n, G, F, c)
        if not ok:
            print(f"n={n}: VERIFY FAIL {msg}")
            continue
        G = sorted(tuple(sorted(e)) for e in G)
        F = sorted(tuple(sorted(t)) for t in F)
        out[str(n)] = {"c": c, "G": G, "F": F, "method": method}
        rows.append((n, c, len(G), len(F), method, "closed+verify"))
    elif str(n) in app:
        d = app[str(n)]
        out[str(n)] = d
        rows.append((n, d["c"], len(d["G"]), len(d["F"]), d.get("method", "appendix"), "appendix-data"))
    else:
        print(f"n={n}: NO DATA")
        rows.append((n, None, None, None, None, "MISSING"))

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
print(f"wrote {OUT}  ({len(out)} entries)")

# coverage table
hdr = f"{'n':>4} {'mod7':>4} {'c':>5} {'|G|':>4} {'|F|':>4}  {'method':<20} {'source'}"
print(hdr)
print("-" * len(hdr))
for n, c, ng, nf, method, src in rows:
    print(f"{n:>4} {n%7:>4} {c:>5} {ng:>4} {nf:>4}  {method:<20} {src}")
