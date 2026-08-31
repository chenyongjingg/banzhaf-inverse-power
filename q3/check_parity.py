# -*- coding: utf-8 -*-
"""Check: do ALL swing counts share a common parity in (a) ALL simple games, (b) weighted games?
Enumerate all monotone simple games on n=4,5 voters; also random weighted games on larger n."""
from itertools import combinations
def swings(winning_mask, n):
    eta = [0]*n
    for S in range(1 << n):
        vS = (winning_mask >> S) & 1
        for i in range(n):
            if S & (1 << i): continue
            vSp = (winning_mask >> (S | (1 << i))) & 1
            if vSp != vS:
                eta[i] += 1
    return eta

def enumerate_monotone(n):
    all_S = list(range(1 << n))
    # generate all monotone games via winning-coalition sets containing all supersets
    from itertools import product
    masks = []
    # build all winning sets: assign each minimal set... simpler: enumerate via antichains is complex.
    # Instead sample: for each mask, check monotonicity (if winning, all supersets winning)
    cnt = same = diff = 0
    for mask in range(1 << (1 << n)):
        # monotone check
        ok = True
        for S in range(1 << n):
            if (mask >> S) & 1:
                for i in range(n):
                    if not (S & (1 << i)):
                        if not ((mask >> (S | (1 << i))) & 1):
                            ok = False; break
                if not ok: break
        if not ok: continue
        cnt += 1
        eta = swings(mask, n)
        p = [e % 2 for e in eta]
        if len(set(p)) == 1:
            same += 1
        else:
            diff += 1
            if diff <= 3:
                print(f"  mixed-parity game n={n}: eta={eta}")
    print(f"n={n}: monotone games={cnt}, all-same-parity: {same}, mixed: {diff}")

for n in (3, 4):
    enumerate_monotone(n)
