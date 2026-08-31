# -*- coding: utf-8 -*-
"""Probe 1: parity theorem (c even), decisive/divisibility-by-4, and Shapley-Shubik resonance
for the closed-form constructions realizing Bz = psi^n = (2,...,2,1)/(2n-1)."""
import itertools, math
from math import factorial as fact

def swings_from_winmask(winfunc, n):
    eta = [0]*n
    for i in range(n):
        bit = 1 << i
        for m in range(1 << n):
            if m & bit: continue
            if (not winfunc(m)) and winfunc(m | bit):
                eta[i] += 1
    return eta

def build_complement_edges(n, edges):
    win = [sum(1 << (x-1) for x in sorted(set(range(1, n+1)) - set(e))) for e in edges]
    return lambda m: any((m & c) == c for c in win)

def shubik(winfunc, n):
    """Shapley-Shubik index (efficient via per-coalition swing)."""
    ssi = [0.0]*n
    for i in range(n):
        bit = 1 << i
        for m in range(1 << n):
            if m & bit: continue
            if (not winfunc(m)) and winfunc(m | bit):
                sz = bin(m).count("1")
                ssi[i] += fact(sz)*fact(n-1-sz)
    tot = sum(ssi)
    return [s/tot for s in ssi] if tot else ssi

def is_decisive(winfunc, n):
    for m in range(1 << n):
        if winfunc(m) == winfunc((1 << n)-1 ^ m):
            return False
    return True

# ---------------- constructions from reproduce_all ----------------
CONST = [
    (6, [(1,2),(1,3),(2,6),(3,6),(4,5),(4,6),(5,6)]),
    (7, [(i,i+1) for i in range(1,6)]+[(6,1)]+[(i,7) for i in range(1,7)]),
    (9, [(i,9) for i in range(1,5)]+[(5,6),(7,8)]),
    (13, [(i,13) for i in range(1,9)]+[(1,2),(3,4),(5,6),(7,8)]+[(9,10),(10,11),(11,12),(12,9)]),
    (14, [(i,i+1) for i in range(1,13)]+[(13,1)]+[(6,10)]+[(i,14) for i in [1,2,3,4,5,7,8,9,11,12,13]]),
    (16, [(i,16) for i in range(1,8)]+[(8,9),(10,11),(12,13),(14,15)]),
    (17, [(i,17) for i in range(1,17)]+[(i,i+1) for i in range(1,16)]+[(16,1)]+[(i,i+8) for i in range(1,9)]),
]

print(f"{'n':>3} {'c':>3} {'parity-ok':>10} {'decisive':>9} {'SSI of special':>15} {'max|SSI-psi|':>13} {'SSI mult-c?':>12}")
for n, edges in CONST:
    wf = build_complement_edges(n, edges)
    eta = swings_from_winmask(wf, n)
    c = math.gcd(*eta)
    c_even = (c % 2 == 0)
    dec = is_decisive(wf, n)
    # div by 4 if decisive
    div4 = (c % 4 == 0) if dec else None
    ssi = shubik(wf, n)
    psi = [2/(2*n-1)]*(n-1) + [1/(2*n-1)]
    maxdev = max(abs(a-b) for a, b in zip(ssi, psi))
    # check if SSI ≈ multiple of psi (i.e. SSI exactly proportional to psi)
    special = ssi[-1]
    ratios = [x/special if special else float('inf') for x in ssi]
    ismult = all(abs(r-2.0) < 1e-9 for r in ratios[:-1]) and abs(ratios[-1]-1.0) < 1e-9
    print(f"{n:>3} {c:>3} {str(c_even):>10} {str(dec):>9} {special:>15.6f} {maxdev:>13.6f} {str(ismult):>12}")

print()
print("Note: SSI is efficient, so SSI=psi^n would require special player to hold 1/(2n-1) of power.")
print("SSI of special player in these constructions (psi target = 1/(2n-1)):")
for n, edges in CONST:
    wf = build_complement_edges(n, edges)
    ssi = shubik(wf, n)
    target = 1/(2*n-1)
    print(f"  n={n}: SSI_special={ssi[-1]:.6f}  target={target:.6f}  ratio={ssi[-1]/target:.3f}")
