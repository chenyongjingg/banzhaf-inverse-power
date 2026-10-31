# -*- coding: utf-8 -*-
"""The image of the two-level map, and a brute-force cross-check.

A weighted majority game v = [q; w] on n voters is two-level when n-1 voters
have one swing count c and the remaining voter ('special') has swing count eta.
Notation follows the counting lemma proved in the note:

  m = n - 1
  f(k) = v(T) for T a set of k bloc voters, special voter absent
  g(k) = v(T) for T a set of k bloc voters, special voter present
  t = min{k : f(k) = 1}      ("without"),  m+1 if no such k
  u = min{k : g(k) = 1}      ("with"),     m+1 if no such k
  u <= t because f <= g

and for u < t

  eta(u, t) = sum_{k=u}^{t-1} C(m, k)
  c(u, t)   = C(m-1, t-1) + C(m-1, u-1)          (0 outside range)

The game [t; t-u, 1, ..., 1] realizes exactly (c(u,t)^{n-1}, eta(u,t)).

Output:
  1. the set of attainable ratios eta/c for n = 3..12, its two ends, and the
     four numbers quoted in Table 1 of the note;
  2. the whole set for n = 6;
  3. a brute-force enumeration of every weighted game with integer weights in
     {0..6} (n <= 5) or {0..5} (n = 6) and every quota, checking that each
     two-level swing vector observed belongs to the list above and that no
     game produces a ratio in (0, 1).

Run:  python two_level_image.py          (about a minute on one core)
"""
from fractions import Fraction
from itertools import product
from math import comb


def C(a, b):
    return comb(a, b) if 0 <= b <= a else 0


def eta_c(m, u, t):
    """swing counts (eta of the special voter, c of each bloc voter)"""
    return (sum(C(m, k) for k in range(u, t)),
            C(m - 1, t - 1) + C(m - 1, u - 1))


def ratio_set(n):
    """all eta/c attained by a two-level weighted game on n voters, c > 0"""
    m, out = n - 1, set()
    for u in range(0, m + 2):
        for t in range(u, m + 2):
            eta, c = eta_c(m, u, t)
            if c > 0:
                out.add(Fraction(eta, c))
    return out


def table_row(n):
    """(pairs contributing a ratio, #positive ratios, min ratio > 1, max ratio)"""
    m = n - 1
    pairs = 0
    for u in range(0, m + 2):
        for t in range(u + 1, m + 2):
            if eta_c(m, u, t)[1] > 0:
                pairs += 1
    R = ratio_set(n)
    pos = sorted(r for r in R if r > 0)
    return pairs, len(pos), min(r for r in pos if r > 1), max(pos)


# ---------------------------------------------------------------- brute force
def swings_by_quota(w):
    """eta_i(q) for every i and every quota 1 <= q <= sum(w), in one pass.

    A coalition S (i not in S) is a swing for i at quota q iff
    sum(S) < q <= sum(S) + w_i, so each such S contributes to an interval of q.
    """
    n = len(w)
    W = sum(w)
    acc = []
    full = 1 << n
    sums = [0] * full
    for S in range(1, full):
        low = S & -S
        sums[S] = sums[S ^ low] + w[low.bit_length() - 1]
    for i in range(n):
        diff = [0] * (W + 2)
        bit = 1 << i
        for S in range(full):
            if S & bit:
                continue
            lo, hi = sums[S], sums[S] + w[i]
            if hi >= 1:
                diff[lo + 1] += 1
                diff[min(hi, W) + 1] -= 1
        eta = [0] * (W + 2)
        run = 0
        for q in range(0, W + 2):
            run += diff[q]
            eta[q] = run
        acc.append(eta)
    return acc, W


def brute(n, Wmax):
    """enumerate every (w, q); return (pairs, two-level ratios seen, violations)"""
    pairs, seen, bad = 0, set(), []
    for w in product(range(Wmax + 1), repeat=n):
        if sum(w) == 0:
            continue
        eta_q, W = swings_by_quota(list(w))
        for q in range(1, W + 1):
            pairs += 1
            eta = [e[q] for e in eta_q]
            if sum(eta) == 0:
                continue
            vals = set(eta)
            if len(vals) != 2:
                continue
            hi, lo = max(vals), min(vals)
            if eta.count(lo) != 1 and eta.count(hi) != 1:
                continue                      # not a (n-1, 1) shape
            if lo == 0:
                seen.add(Fraction(0))         # dummy outsider
                continue
            # r = (count of the singleton) / (count of a bloc voter)
            if eta.count(hi) == 1:
                r = Fraction(hi, lo)          # singleton carries the high count
            else:
                r = Fraction(lo, hi)          # singleton carries the low count
            seen.add(r)
            if r <= 1:
                bad.append((w, q, tuple(eta), r))       # must never happen
    return pairs, seen, bad


def main():
    print('1. attainable ratios eta/c, n = 3..12 (columns as in Table 1)')
    for n in range(3, 13):
        pairs, npos, lo, hi = table_row(n)
        print('   n=%2d  pairs=%2d  |R_n|=%2d  min{r>1}=%-5s  max R_n=%d'
              % (n, pairs, npos, lo, hi))
        assert lo == Fraction(n, n - 2)
        assert hi == 2 ** (n - 1) - 1

    print()
    print('2. the whole set for n = 6')
    R6 = sorted(ratio_set(6))
    print('   ', ', '.join(str(r) for r in R6))
    assert R6 == [Fraction(0), Fraction(1), Fraction(3, 2), Fraction(15, 7),
                  Fraction(5, 2), Fraction(8, 3), Fraction(5), Fraction(13, 2),
                  Fraction(15), Fraction(31)]

    print()
    print('3. brute force over all weighted games, every quota')
    total = 0
    for n, Wmax in ((3, 6), (4, 6), (5, 6), (6, 5)):
        pairs, seen, bad = brute(n, Wmax)
        total += pairs
        R = ratio_set(n)
        outside = sorted(r for r in seen if r not in R)
        print('   n=%d weights in {0..%d}: %d (w,q) pairs, %d two-level ratios, '
              'outside the list: %d, violations: %d'
              % (n, Wmax, pairs, len(seen), len(outside), len(bad)))
        assert not outside and not bad
        assert all(r >= 0 for r in seen) and Fraction(1, 2) not in seen
    print('   total (w,q) pairs enumerated:', total)
    assert total == 983844

    print()
    print('all checks passed')


if __name__ == '__main__':
    main()
