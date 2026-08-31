# -*- coding: utf-8 -*-
"""Probe 5: for psi^n(k,1)=(k,...,k,1)/(k(n-1)+1), find the coverage of the W-family
triangle construction over n (with p pure + q special triangles). Determines which n are
realizable and the coverage threshold N(k) if any. Uses the swing formula (U) directly
(no explicit graph needed) with Havel-Hakimi graphicality."""
import math, sys
from itertools import combinations

def havel_hakimi_ok(degseq, G_edges_fixed):
    """Check if remaining degrees can be realized as a simple graph NOT using fixed edges.
    Simplified: build a graph greedily (Erdos-Gallai style) ignoring fixed-edge conflicts,
    but for the two-tier probe we only need a correct existence check for our structured
    degree sequences. We implement full graphicality via Havel-Hakimi on all nodes with
    the constraint that triangle players can't get extra edges."""
    return True  # placeholder, refined below

def graphical(seq):
    """Standard Erdős–Gallai test. seq: multiset of degrees."""
    seq = sorted(seq, reverse=True)
    total = sum(seq)
    if total % 2: return False
    n = len(seq)
    prefix = [0]
    for d in seq: prefix.append(prefix[-1] + d)
    for k in range(1, n+1):
        lhs = prefix[k]
        rhs = k*(k-1) + sum(min(d, k) for d in seq[k:])
        if lhs > rhs: return False
    return True

def swings_formula(n, p, q, s):
    """Compute swings via formula (U) for the triangle construction.
    Non-special: triangle players deg2 r1, base deg3 r0 -> all = A-6.
    Special: A - 2s - 2q."""
    m = n-1-3*p-2*q
    if m < 0: return None
    A = (5*n - 5 - p + s)/2
    beta_ns = A - 6
    beta_s = A - 2*s - 2*q
    return beta_ns, beta_s, m, A

def check(a, b, n, p, q, s):
    m = n-1-3*p-2*q
    if m < 0: return False
    if s < 0 or s > n-1: return False
    if s - 2*q < 0: return False
    r = swings_formula(n, p, q, s)
    if r is None: return False
    beta_ns, beta_s, _, A = r
    if beta_ns <= 0 or beta_s <= 0: return False
    if abs(beta_ns/beta_s - a/b) > 1e-9: return False
    # scale integer check: beta_ns must be a*c with c integer (and beta_s = b*c)
    c = beta_ns / a
    if abs(c - round(c)) > 1e-9: return False
    if c < 1: return False
    # graphicality of full degree sequence: [3]*(m) + [2]*(3p+2q) + [s]
    seq = [3]*m + [2]*(3*p+2*q) + [s]
    if not graphical(seq): return False
    return True

def cover(k, nmax, pmax=8, qmax=8):
    hits = {}
    for n in range(6, nmax+1):
        found = None
        for p in range(0, pmax+1):
            for q in range(0, qmax+1):
                num = (k-1)*(5*n-5-p) - 4*k*q + 12
                den = 3*k + 1
                if num % den != 0: continue
                s = num // den
                if check(k, 1, n, p, q, s):
                    found = (p, q, s)
                    break
            if found: break
        hits[n] = found
    return hits

def gaps(hits):
    return [n for n, h in hits.items() if h is None]

for k in [2, 3, 4, 5, 6, 7]:
    h = cover(k, 80)
    gap = gaps(h)
    # coverage threshold: largest n with a gap, beyond which all covered
    threshold = max(gap) + 1 if gap else 6
    first_cover = min(n for n in h if h[n] is not None)
    print(f"k={k}: covered n in [6,80]: {sum(1 for v in h.values() if v)}/75"
          f"  first={first_cover}  gaps={gap[:15]}{'...' if len(gap)>15 else ''}  "
          f"threshold(N)>={threshold if threshold<=80 else '>80'}")
