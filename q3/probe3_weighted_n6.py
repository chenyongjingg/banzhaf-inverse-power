# -*- coding: utf-8 -*-
"""Probe 3: exact min-L1 over WEIGHTED majority games for n=6 (Conjecture 15 anchor).
Enumerates weight vectors w_1>=...>=w_6>=1 (gcd=1, increasing cap), all quotas q,
dedups by winning-coalition bitmask, then canonicalizes under S_6. Verifies
completeness against the unlabeled weighted-game count 1111 (Kurz & Napel 2014
Table 1 #W(6); note #C(6)=1171 is the COMPLETE-game count, not weighted)."""
import sys, math
from itertools import combinations_with_replacement, permutations
from fractions import Fraction

def subset_sums(w, n):
    sums = [0]*(1 << n)
    for m in range(1, 1 << n):
        lb = m & (-m)
        i = lb.bit_length() - 1
        sums[m] = sums[m ^ lb] + w[i]
    return sums

def winning_mask_for_threshold(sums, q):
    mask = 0
    for m in range(len(sums)):
        if sums[m] >= q:
            mask |= (1 << m)
    return mask

def banzhaf_swings(winmask, n):
    """winmask: bit m set iff coalition m is winning. Returns swings list."""
    eta = [0]*n
    N = 1 << n
    for i in range(n):
        bit = 1 << i
        cnt = 0
        for m in range(N):
            if m & bit: continue
            if (winmask >> m) & 1 == 0 and (winmask >> (m | bit)) & 1:
                cnt += 1
        eta[i] = cnt
    return eta

def l1_to_psi(eta, n):
    tot = sum(eta)
    if tot == 0: return 1e9
    target = [2.0/(2*n-1)]*(n-1) + [1.0/(2*n-1)]
    return sum(abs(e/tot - t) for e, t in zip(eta, target))

def canonical(mask, n):
    """Minimum winning-mask under all relabelings of the n players (S_n action);
    equal for isomorphic games, so the number of distinct canonical masks over an
    exhaustive enumeration is the count of unlabeled games (Kurz-Napel #W(n))."""
    best = mask
    for p in permutations(range(n)):
        m = 0
        msk = mask
        while msk:
            lsb = msk & -msk
            S = lsb.bit_length() - 1
            T = 0
            for i in range(n):
                if (S >> i) & 1:
                    T |= 1 << p[i]
            m |= 1 << T
            msk ^= lsb
        if m < best:
            best = m
    return best

def main(cap):
    n = 6
    games = {}   # winmask -> swings
    count = 0
    for w in combinations_with_replacement(range(1, cap+1), n):
        w = list(reversed(w))  # nondecreasing -> we don't even need nonincreasing; all orders enumerated by combinations covers each multiset once
        if math.gcd(*w) != 1:
            continue
        sums = subset_sums(w, n)
        seen_q = set()
        for q in range(1, sum(w)+1):
            m = winning_mask_for_threshold(sums, q)
            if m in seen_q: continue
            seen_q.add(m)
            if m not in games:
                count += 1
                eta = banzhaf_swings(m, n)
                games[m] = eta
    uniq = len({canonical(m, n) for m in games})           # unlabeled (S_6 iso classes)
    best = min((l1_to_psi(eta, n), wmask) for wmask, eta in games.items())
    # also best excluding the trivial "dictator/const" cases is fine; report top few
    top = sorted(((l1_to_psi(e, n), m) for m, e in games.items()))[:5]
    print(f"cap={cap}: labeled weighted games={count}, unlabeled (S6)={uniq}"
          f"  (known n=6 unlabeled=1111, Kurz-Napel 2014 Table 1 #W(6))")
    for d, m in top:
        eta = games[m]
        print(f"  L1={d:.8f}  swings={eta}  total={sum(eta)}")
    return count, games

if __name__ == "__main__":
    cap = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    main(cap)
