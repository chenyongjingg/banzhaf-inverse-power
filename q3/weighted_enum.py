# -*- coding: utf-8 -*-
"""Server: enumerate ALL weighted majority games for n=6,7 via weight-vector + quota
dedup. Verified counts are UNLABELED (isomorphism classes), per Kurz & Napel 2014
Table 1: #W(6)=1111, #W(7)=29373 (NOT the labeled count, and NOT #C=complete games,
which is 1171 / 44313). We therefore canonicalize under the S_n action so the printed
count matches the literature. Outputs best L1 to psi^n and explicit optimal game.
Usage: python weighted_enum.py [n] [cap]"""
import sys, math, multiprocessing as mp
import numpy as np
from itertools import combinations_with_replacement, permutations

def subset_sums(w):
    sums = np.array([0], dtype=np.int64)
    for wi in w:
        sums = np.concatenate([sums, sums + wi])
    return sums

def games_from_weights(w):
    """Set of winning-mask ints realized by this weight vector across all quotas.
    Winning set for quota q = {coalitions with sum >= q}; distinct such sets are the
    nested prefixes when coalitions are added in descending sum order."""
    sums = subset_sums(w)
    order = np.argsort(-sums)
    out = set()
    mask = 0
    prev = -1
    for idx in order:
        mask |= (1 << int(idx))
        if sums[idx] != prev:
            out.add(mask)
            prev = sums[idx]
    return out

_PERMS = {}

def canonical(mask, n):
    """Minimum winning-mask under all relabelings of the n players (S_n action).
    Two simple games are isomorphic iff they share the same canonical mask, so the
    number of distinct canonical masks over an exhaustive enumeration is the count
    of unlabeled (isomorphism classes of) games -- the count tabulated by Kurz-Napel."""
    global _PERMS
    if n not in _PERMS:
        tbls = []
        for p in permutations(range(n)):
            tbl = [0] * (1 << n)
            for S in range(1 << n):
                T = 0
                for i in range(n):
                    if (S >> i) & 1:
                        T |= 1 << p[i]
                tbl[S] = T
            tbls.append(tbl)
        _PERMS[n] = tbls
    best = mask
    for tbl in _PERMS[n]:
        m = 0
        msk = mask
        while msk:
            lsb = msk & -msk
            S = lsb.bit_length() - 1
            m |= 1 << tbl[S]
            msk ^= lsb
        if m < best:
            best = m
    return best

def process_chunk(vecs):
    games = set()
    for w in vecs:
        games |= games_from_weights(w)
    return games

def banzhaf_swings(winmask, n):
    eta = []
    N = 1 << n
    for i in range(n):
        bit = 1 << i
        cnt = 0
        for m in range(N):
            if m & bit: continue
            if ((winmask >> m) & 1) == 0 and ((winmask >> (m | bit)) & 1):
                cnt += 1
        eta.append(cnt)
    return eta

def l1_to_psi(eta, n):
    tot = sum(eta)
    if tot == 0: return 1e9
    target = [2.0/(2*n-1)]*(n-1) + [1.0/(2*n-1)]
    return sum(abs(e/tot - t) for e, t in zip(eta, target))

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    # nonincreasing weight vectors w_1>=...>=w_n>=1 with gcd 1, w_1<=cap
    allw = []
    for w in combinations_with_replacement(range(1, cap+1), n):
        if math.gcd(*w) != 1: continue
        allw.append(list(w))
    print(f"n={n} cap={cap}: {len(allw)} weight vectors", flush=True)
    pool = mp.Pool(mp.cpu_count())
    chunks = [allw[i::mp.cpu_count()*4] for i in range(mp.cpu_count()*4)]
    games = set()
    for i, res in enumerate(pool.imap_unordered(process_chunk, chunks)):
        games |= res
        if i % 2 == 1:
            print(f"  merged {len(games)} distinct so far", flush=True)
    pool.close(); pool.join()
    known = {6: 1111, 7: 29373}   # Kurz & Napel 2014 Table 1, unlabeled weighted games
    valid = sorted(g for g in games if not (g & 1))        # exclude trivial all-winning game
    uniq = {canonical(g, n) for g in valid}                # unlabeled (S_n iso classes)
    print(f"TOTAL distinct labeled weighted games = {len(games)}", flush=True)
    print(f"  valid (empty coalition losing)       = {len(valid)}", flush=True)
    print(f"  unlabeled (S{n} iso classes)          = {len(uniq)}"
          f"  (known n={n}: {known.get(n, '?')})", flush=True)
    # compute best L1
    best = None
    for g in valid:
        eta = banzhaf_swings(g, n)
        d = l1_to_psi(eta, n)
        if best is None or d < best[0]:
            best = (d, eta, g)
    print(f"BEST L1 to psi^n = {best[0]:.10f}")
    print(f"  swings = {best[1]}")
    print(f"  total swings = {sum(best[1])}")
    print(f"  winning-mask = {best[2]}")

if __name__ == "__main__":
    main()
