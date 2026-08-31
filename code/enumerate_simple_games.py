"""Enumerate all simple games (monotone Boolean functions, f(empty)=0, f(full)=1)
for small n by antichains of minimal winning coalitions; find games whose Banzhaf
swing vector is proportional to (2,2,...,2,1) (Conjecture 16 target psi^n).
"""
from itertools import combinations
import sys, time

def antichains(n):
    """Yield all antichains (as tuples of masks) of subsets of {0..n-1}."""
    masks = list(range(1 << n))
    results = []
    def rec(chosen, start):
        results.append(tuple(chosen))
        for idx in range(start, len(masks)):
            m = masks[idx]
            if any((m & c) == c for c in chosen):  # m is a superset of a chosen element
                continue
            # if m contains any chosen as subset -> m can be added? Actually chosen must be
            # pairwise incomparable: no chosen element is subset of m.
            if any((c & m) == c for c in chosen):  # some chosen c is subset of m
                continue
            chosen.append(m)
            rec(chosen, idx + 1)
            chosen.pop()
    rec([], 0)
    return results

def swing_vector(antichain, n):
    """Swing count eta_i for each player i. f(coalition)=1 iff coalition contains some antichain element."""
    # build winning set
    full = (1 << n) - 1
    eta = [0]*n
    # For each coalition mask, determine winning; count swings.
    for m in range(1 << n):
        # f(m)
        win = any((m & c) == c for c in antichain)
        if win:
            # swings: removing a player makes it losing
            for i in range(n):
                mm = m & ~(1 << i)
                if not any((mm & c) == c for c in antichain):
                    eta[i] += 1
        else:
            for i in range(n):
                mm = m | (1 << i)
                if any((mm & c) == c for c in antichain):
                    eta[i] += 1
    return eta

def find_solutions(n, target_multiset):
    t0 = time.time()
    sols = []
    for ac in antichains(n):
        # require f(empty)=0, f(full)=1 i.e. antichain nonempty and covers full
        if not ac: continue
        if not any((c & ((1<<n)-1)) == c and c != 0 for c in ac):
            continue
        # full must be winning: some antichain element = 0? no, need some c (c is subset of full) -> always
        # f(full)=1 iff antichain nonempty. f(empty)=0 iff no antichain element is empty set.
        if 0 in ac: continue
        eta = swing_vector(ac, n)
        if sorted(eta) == sorted(target_multiset):
            sols.append((ac, eta))
    return sols, time.time()-t0

if __name__ == "__main__":
    n = int(sys.argv[1])
    target = tuple(sorted([1] + [2]*(n-1)))
    sols, dt = find_solutions(n, target)
    print(f"n={n}: found {len(sols)} solutions in {dt:.1f}s")
    for ac, eta in sols[:10]:
        print("  antichain:", ac, " swings:", eta)
