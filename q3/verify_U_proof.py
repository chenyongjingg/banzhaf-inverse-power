# -*- coding: utf-8 -*-
"""Case-by-case verification of the proof of Proposition 11's formula (U).

Proposition 11 states the swing identity (U) for the family v(G,F) and carried only
a random-instance verification.  The identity is provable by the same enumeration of
|S| that proves Theorem 3, and the proof decomposes the swings into four cases.  This
script checks the *decomposition*, not merely the total: for each random instance and
each player it counts the swings contributed by each case separately and compares each
partial count with the closed form the proof gives for it.  A proof whose cases are
individually checked is a different claim from a formula that happens to match in sum.

Cases for a player i, over losing S with S u {i} winning (i not in S):
  |S| = n-2 : S = N \\ {i,j}, losing iff {i,j} not in G.
              count = (n-1) - deg_G(i)
  |S| = n-3 : S u {i} = N \\ {a,b}, winning iff {a,b} in G; S losing iff {i,a,b} not in F.
              count = |G| - deg_G(i) - e_i,  e_i = |{X in F : i in X, X\\{i} in G}|
  |S| = n-4 : S u {i} = N \\ X with X in F and i not in X.
              count = |F| - r_i
  |S| <= n-5: S u {i} has size <= n-4, hence losing; count = 0.
The four sum to |G| + (n-1) + |F| - 2 deg_G(i) - r_i - e_i, which equals (U) because
the proposition's e_i corresponds to the complement count r_i - e_i.

Two passes are run.  The first imposes the proposition's hypothesis Pairs(F) subset of G; the
second drops it.  None of the four cases uses that hypothesis -- only the claim that v(G,F) is
monotone does -- so (U) is an identity for arbitrary (G,F), and the second pass is what makes the
proposition's applicability exceed its own hypothesis.

Usage: python verify_U_proof.py [trials] [nmin] [nmax]
"""
import itertools
import random
import sys


def game_winning(S, n, G, F):
    """v(G,F) as defined in Proposition 11; S is a frozenset of voters."""
    k = len(S)
    if k >= n - 1:
        return True
    comp = frozenset(range(n)) - S
    if k == n - 2:
        return tuple(sorted(comp)) in G
    if k == n - 3:
        return tuple(sorted(comp)) in F
    return False


def brute_swings(n, G, F):
    """Direct Banzhaf swing counts from the game definition."""
    full = frozenset(range(n))
    players = list(range(n))
    out = []
    for i in players:
        c = 0
        rest = [j for j in players if j != i]
        for k in range(0, n - 1):          # |S| = k, i not in S
            for S in itertools.combinations(rest, k):
                S = frozenset(S)
                if not game_winning(S, n, G, F) and game_winning(S | {i}, n, G, F):
                    c += 1
        out.append(c)
    return out


def case_counts(n, G, F, i):
    """Swings contributed by each of the four cases, counted directly."""
    players = list(range(n))
    rest = [j for j in players if j != i]
    c2 = c3 = c4 = 0
    for k in range(0, n - 1):
        for S in itertools.combinations(rest, k):
            S = frozenset(S)
            if game_winning(S, n, G, F) or not game_winning(S | {i}, n, G, F):
                continue
            if k == n - 2:
                c2 += 1
            elif k == n - 3:
                c3 += 1
            elif k == n - 4:
                c4 += 1
            else:
                raise AssertionError("a swing at |S| = %d (n = %d)" % (k, n))
    return c2, c3, c4


def random_instance(n, rng, monotone=True):
    pairs = list(itertools.combinations(range(n), 2))
    triples = list(itertools.combinations(range(n), 3))
    G = {p for p in pairs if rng.random() < rng.choice([0.3, 0.5, 0.8])}
    # Pairs(F) subset of G is the monotonicity hypothesis of Proposition 11
    F = set()
    for t in triples:
        if rng.random() < 0.25 and (not monotone or all(
                tuple(sorted(p)) in G for p in itertools.combinations(t, 2))):
            F.add(t)
    return G, F


def run(trials, nmin, nmax, seed, monotone):
    """Verify the four cases and (U) on random instances; return the instance count.

    monotone=False drops the hypothesis Pairs(F) subset of G.  The four cases of the proof never
    use it -- only the monotonicity claim does -- so the same assertions must hold there too.
    """
    rng = random.Random(seed)
    checked = 0
    for n in range(nmin, nmax + 1):
        for t in range(trials):
            G, F = random_instance(n, rng, monotone=monotone)
            brute = brute_swings(n, G, F)
            for i in range(n):
                deg = sum(1 for e in G if i in e)
                r_i = sum(1 for X in F if i in X)
                e_i = sum(1 for X in F if i in X and tuple(sorted(set(X) - {i})) in G)
                # (U) as printed in the manuscript
                U = len(G) + (n - 1) + len(F) - 2 * deg - 2 * r_i + (r_i - e_i)
                assert brute[i] == U, ("(U) mismatch", n, i, brute[i], U)
                c2, c3, c4 = case_counts(n, G, F, i)
                assert c2 == (n - 1) - deg, ("case n-2", n, i, c2, (n - 1) - deg)
                assert c3 == len(G) - deg - e_i, ("case n-3", n, i, c3, len(G) - deg - e_i)
                assert c4 == len(F) - r_i, ("case n-4", n, i, c4, len(F) - r_i)
                assert c2 + c3 + c4 == brute[i], ("cases miss swings", n, i)
                checked += 1
    return checked


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    nmin = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    nmax = int(sys.argv[3]) if len(sys.argv) > 3 else 9
    for monotone in (True, False):
        checked = run(trials, nmin, nmax, 20260914, monotone)
        print("U PROOF CASES: PASS - %d player-instances over n = %d..%d%s, "
              "each case matched its closed form and the three summed to the brute-force count"
              % (checked, nmin, nmax,
                 "" if monotone else " with Pairs(F) subset of G NOT imposed"))


if __name__ == "__main__":
    main()
