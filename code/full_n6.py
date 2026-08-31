"""Full enumeration of simple games on n=6 via antichains; find swing vectors
proportional to (2,2,...,2,1). Bit-trick swing computation."""
import time
from math import gcd
from functools import reduce

n = 6
NB = 1 << n
FULLMASK = (1 << NB) - 1  # 64 bits
MASKS = list(range(NB))

# precompute superset mask for each coalition
SUP = [0] * NB
for c in range(NB):
    rem = (~c) & (NB - 1)
    sub = rem
    s = 0
    while True:
        s |= 1 << (c | sub)
        if sub == 0:
            break
        sub = (sub - 1) & rem
    SUP[c] = s

# precompute per-player masks
MaskZ = [0] * n
MaskO = [0] * n
twoi = [1 << i for i in range(n)]
for i in range(n):
    z = 0; o = 0
    for m in range(NB):
        if (m >> i) & 1:
            o |= 1 << m
        else:
            z |= 1 << m
    MaskZ[i] = z
    MaskO[i] = o

def swings_fast(ac):
    WIN = 0
    for c in ac:
        WIN |= SUP[c]
    NOTWIN = (~WIN) & FULLMASK
    eta = [0] * n
    for i in range(n):
        eta[i] = bin(MaskZ[i] & NOTWIN & ((MaskO[i] & WIN) >> twoi[i])).count("1")
    return eta

def antichains(n):
    masks = MASKS
    results = []
    def rec(chosen, start):
        results.append(tuple(chosen))
        for idx in range(start, len(masks)):
            m = masks[idx]
            ok = True
            for c in chosen:
                if (c & m) == c:
                    ok = False; break
            if ok:
                chosen.append(m); rec(chosen, idx + 1); chosen.pop()
    rec([], 0)
    return results

t0 = time.time()
sols = []
target = tuple([1] + [2] * (n - 1))
for ac in antichains(n):
    if not ac or 0 in ac:
        continue
    eta = swings_fast(ac)
    if any(e == 0 for e in eta):
        continue
    g = reduce(gcd, eta)
    if tuple(sorted(e // g for e in eta)) == target:
        sols.append((ac, eta))
print(f"n={n}: {len(sols)} solutions in {time.time()-t0:.1f}s")
for ac, eta in sols[:12]:
    fmt = sorted([sorted(j + 1 for j in range(n) if (c >> j) & 1) for c in ac])
    print("  antichain:", fmt, " swings:", eta, " gcd:", reduce(gcd, eta))
