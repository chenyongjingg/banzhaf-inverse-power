"""Verify a simple game on 6 voters given by its minimal winning coalitions.

Default witness: realizes psi^6 = (2,...,2,1)/11.
Checks: every listed coalition is minimal winning; the swing vector is
(8,8,8,8,8,4); the desirability (Isbell) relation is not total, so the game
is not complete and admits no weight representation.
"""
from itertools import combinations

WITNESS = [(1, 2, 3, 4), (1, 2, 4, 5), (1, 3, 4, 5),
           (2, 3, 4, 5), (1, 3, 4, 6), (1, 2, 5, 6), (2, 3, 5, 6)]


def check(MW, verbose=True):
    """Return (swing_vector, is_complete) for the game with MW coalitions."""
    N = sorted({i for m in MW for i in m})

    def win(S):
        T = set(S)
        return any(set(m) <= T for m in MW)

    eta = [0] * len(N)
    for r in range(len(N) + 1):
        for S in combinations(N, r):
            if win(S):
                continue
            for i in N:
                if i not in S and win(set(S) | {i}):
                    eta[i - 1] += 1

    def desirable(i, j):
        rest = [k for k in N if k not in (i, j)]
        for r in range(len(rest) + 1):
            for T in combinations(rest, r):
                T = set(T)
                if win(T | {i}) < win(T | {j}):
                    return False
        return True

    M = [[desirable(i, j) for j in N] for i in N]
    complete = all(M[i][j] or M[j][i] for i in range(len(N)) for j in range(len(N)))
    if verbose:
        total = sum(eta)
        print("swing vector  :", eta, " total:", total)
        print("Banzhaf vector:", [round(e / total, 6) for e in eta])
        print("all listed coalitions minimal:",
              all(all(not win(set(m) - {i}) for i in m) for m in MW))
        print("desirability relation total (game complete):", complete)
        print("incomparable pairs:", [(i + 1, j + 1) for i in range(len(N))
                                      for j in range(i + 1, len(N))
                                      if not M[i][j] and not M[j][i]])
    return eta, complete


if __name__ == "__main__":
    eta, complete = check(WITNESS)
    assert eta == [8, 8, 8, 8, 8, 4], eta
    assert not complete
    print("OK: Bz = (2,2,2,2,2,1)/11 and the game is not weighted.")
