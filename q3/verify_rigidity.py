# -*- coding: utf-8 -*-
"""Pointwise checks for the four structural statements of the rigidity section:

  (P) parity      : all swing counts of a weighted game are congruent mod 2;
  (O) weight order: eta_i > eta_j  =>  w_i > w_j;
  (D) decomposition: for w_i > w_s, |{T subset N\\{i,s}: q-w_i <= W(T) < q-w_s}|
                    equals (eta_i - eta_s)/2;
  (M) mirror      : for w_i >= w_j > w_s and eta_i == eta_j, both
                    |{T subset N\\{i,j,s}: q-w_i <= W(T) < q-w_j}| and its
                    translate by -w_s are empty.

Every statement is checked on random weighted majority games, not on the
two-level profile: that profile is not realizable by any weighted game (the
result the obstructions paper certifies), so there is nothing to sample
directly. What is sampled is the hypothesis each statement actually needs,
and which real games do satisfy.

Run:  python verify_rigidity.py [trials] [seed]
"""
import random
import sys

TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
# 7 is the seed that produced rigidity_200k.log, so that running this script
# with no arguments reproduces the log exactly rather than approximately.
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 7


def swing_counts(w, q):
    """eta_i by subset-sum DP over bitmasks; O(n 2^n)."""
    n = len(w)
    size = 1 << n
    tot = [0] * size
    for mask in range(1, size):
        low = mask & (-mask)
        tot[mask] = tot[mask ^ low] + w[low.bit_length() - 1]
    eta = [0] * n
    for i in range(n):
        bit = 1 << i
        wi = w[i]
        for mask in range(size):
            if mask & bit:
                continue
            if q - wi <= tot[mask] < q:
                eta[i] += 1
    return eta


def subset_sums(vals):
    out = [0]
    for v in vals:
        out = out + [x + v for x in out]
    return out


def count_in(sums, a, b):
    return sum(1 for x in sums if a <= x < b)


def main():
    rng = random.Random(SEED)
    p_bad = o_bad = d_bad = m_bad = 0
    o_met = d_met = m_met = 0
    for _ in range(TRIALS):
        n = rng.randint(2, 7)
        w = [rng.randint(1, 12) for _ in range(n)]
        q = rng.randint(1, sum(w) + 1)
        eta = swing_counts(w, q)

        # (P) parity
        if len({e % 2 for e in eta}) > 1:
            p_bad += 1

        # (O) strict order of counts implies strict order of weights
        for i in range(n):
            for j in range(n):
                if eta[i] > eta[j]:
                    o_met += 1
                    if not w[i] > w[j]:
                        o_bad += 1

        # (D) and (M) need a triple s, i, j
        if n < 3:
            continue
        for s in range(n):
            rest = [x for x in range(n) if x != s]
            for i in rest:
                if w[i] <= w[s]:
                    continue
                d_met += 1
                others = [w[x] for x in range(n) if x not in (i, s)]
                got = count_in(subset_sums(others), q - w[i], q - w[s])
                if 2 * got != eta[i] - eta[s]:
                    d_bad += 1
            for t in range(len(rest)):
                for u in range(t + 1, len(rest)):
                    i, j = rest[t], rest[u]
                    if not w[i] >= w[j] > w[s]:
                        continue
                    if eta[i] != eta[j]:
                        continue
                    m_met += 1
                    sums = subset_sums(
                        [w[x] for x in range(n) if x not in (i, j, s)])
                    if count_in(sums, q - w[i], q - w[j]):
                        m_bad += 1
                    if count_in(sums, q - w[s] - w[i], q - w[s] - w[j]):
                        m_bad += 1

    # the parameters travel with the counts: a log that does not say which
    # invocation produced it cannot be re-run, and cannot be cited either.
    print("trials                         :", TRIALS)
    print("seed                           :", SEED)
    print("games sampled                  :", TRIALS)
    print("(P) parity violations          :", p_bad)
    print("(O) order tests / violations   :", o_met, "/", o_bad)
    print("(D) decomposition tests / bad  :", d_met, "/", d_bad)
    print("(M) mirror tests / violations  :", m_met, "/", m_bad)


if __name__ == "__main__":
    main()
