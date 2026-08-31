# -*- coding: utf-8 -*-
"""Probe 4: two-tier generalization. For psi^n(a,b) = (a,...,a,b)/((n-1)a+b), use the
W-family triangle construction: f=p+q disjoint triangles (q special containing player n),
non-special players base degree 3, special degree s = [(a-b)(5n-5-p) - 4aq + 12b]/(3a+b).
Verifies integerity + Havel-Hakimi graphicality + exact swing ratio (a,...,a,b)."""
import math, sys
from itertools import combinations
from collections import defaultdict

def havel_hakimi(seq):
    """seq: list of (node, deg) with deg>0 required. Returns edge list or None."""
    seq = [(node, d) for node, d in seq if d > 0]
    edges = []
    while seq:
        seq.sort(key=lambda x: -x[1])
        node, d = seq[0]
        if d > len(seq)-1:
            return None
        seq = seq[1:]
        for i in range(d):
            seq[i] = (seq[i][0], seq[i][1]-1)
            edges.append(tuple(sorted((node, seq[i][0]))))
        seq = [(nd, dd) for nd, dd in seq if dd > 0]
        # recheck negative
        if any(dd < 0 for _, dd in seq):
            return None
    return edges

def build_game(n, p, q, s):
    """Build v(G,F) W-family game. Returns winfunc."""
    m = n-1-3*p-2*q          # non-triangle non-special players
    if m < 0: return None
    # node ids: 0..n-1 internal; non-triangle = last m of 0..n-2, special = n-1
    non_tri = list(range(m))          # first m non-special players (0..m-1)
    tri_players = list(range(m, n-1)) # m..n-2 in triangles
    special = n-1
    # F triples: q special {special, a, b}, p pure
    F = []
    idx = m
    for _ in range(q):
        if idx+1 >= n-1: return None
        F.append((special, idx, idx+1)); idx += 2
    for _ in range(p):
        if idx+2 >= n-1: return None
        F.append((idx, idx+1, idx+2)); idx += 3
    # triangle edges
    G = set()
    for X in F:
        for e in combinations(X, 2):
            G.add(tuple(sorted(e)))
    # remaining degrees: non_tri need 3, special needs s - 2q
    rem = [(nd, 3) for nd in non_tri] + [(special, s - 2*q)]
    if any(d < 0 for _, d in rem): return None
    extra = havel_hakimi(rem)
    if extra is None: return None
    G |= set(extra)
    # build winfunc for v(G,F): |S|>=n-1 win; |S|=n-2 win iff N\S in G; |S|=n-3 win iff N\S in F
    full = (1 << n) - 1
    Gpairs = [sum(1 << x for x in e) for e in G]
    Ftrip = [sum(1 << x for x in X) for X in F]
    def win(mask):
        sz = bin(mask).count("1")
        if sz >= n-1: return True
        if sz == n-2:
            cmpl = full ^ mask
            return (cmpl in Gpairs)
        if sz == n-3:
            cmpl = full ^ mask
            return (cmpl in Ftrip)
        return False
    return win

def swings(win, n):
    eta = [0]*n
    for i in range(n):
        bit = 1 << i
        for m in range(1 << n):
            if m & bit: continue
            if (not win(m)) and win(m | bit):
                eta[i] += 1
    return eta

def main():
    results = {}
    for (a, b) in [(2,1),(3,1),(4,1),(5,1),(3,2),(4,3),(7,2)]:
        hits = {}
        for n in range(6, 13):
            found = None
            for p in range(0, 5):
                for q in range(0, 5):
                    num = (a-b)*(5*n-5-p) - 4*a*q + 12*b
                    den = 3*a + b
                    if num % den != 0: continue
                    s = num // den
                    if s < 0 or s > n-1: continue
                    if 3*p + 2*q > n-1: continue
                    if s - 2*q < 0: continue
                    win = build_game(n, p, q, s)
                    if win is None: continue
                    eta = swings(win, n)
                    g = math.gcd(*eta)
                    red = tuple(sorted(e//g for e in eta))
                    target = tuple(sorted([a]*(n-1) + [b]))
                    if red == target:
                        found = (n, p, q, s, eta, g)
                        break
                if found: break
            if found: hits[n] = found
        realizable = sorted(hits.keys())
        results[(a,b)] = (realizable, hits)
        print(f"(a,b)=({a},{b}): verified realizable n in [6,12] = {realizable}")
    # details for a couple of cases
    for (a,b) in [(3,1),(3,2)]:
        realizable, hits = results[(a,b)]
        print(f"\n--- (a,b)=({a},{b}) detail ---")
        for n in realizable:
            np_, q_, s_, eta, g = hits[n][1:]
            print(f"  n={n}: p={np_}, q={q_}, s={s_}, scale={g}, swings={eta}")

if __name__ == "__main__":
    main()
