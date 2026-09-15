"""Reproduce all closed-form constructions for the paper. Outputs a results table."""
from math import gcd
from functools import reduce

def swings(ac_sets, n):
    ac=[sum(1<<(x-1) for x in c) for c in ac_sets]
    def win(m): return any((m&c)==c for c in ac)
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        for m in range(1<<n):
            if m&bit: continue
            if (not win(m)) and win(m|bit): eta[i]+=1
    return eta

def build(n, edges):
    win=[sorted(set(range(1,n+1))-set(e)) for e in edges]
    return swings(win, n)

results = []
# n=6: C4(1-2-6-3-1) U K3(4,5,6)
results.append((6, [(1,2),(1,3),(2,6),(3,6),(4,5),(4,6),(5,6)], "C4 U K3"))
# n=7: C6 on 1..6 + star7
results.append((7, [(i,i+1) for i in range(1,6)]+[(6,1)]+[(i,7) for i in range(1,7)], "C6 + star7"))
# n=9: star9(1-4) + matching{5,6},{7,8}
results.append((9, [(i,9) for i in range(1,5)]+[(5,6),(7,8)], "star9 + matching"))
# n=13: star13(1-8) + matching + C4(9-12)
results.append((13, [(i,13) for i in range(1,9)]+[(1,2),(3,4),(5,6),(7,8)]+[(9,10),(10,11),(11,12),(12,9)], "star13+matching+C4"))
# n=14: C13 + chord{6,10} + star14(excl 6,10)
results.append((14, [(i,i+1) for i in range(1,13)]+[(13,1)]+[(6,10)]+[(i,14) for i in [1,2,3,4,5,7,8,9,11,12,13]], "C13+chord+star14"))
# n=16: star16(1-7) + matching
results.append((16, [(i,16) for i in range(1,8)]+[(8,9),(10,11),(12,13),(14,15)], "star16+matching"))
# n=17: star17(all) + C16 + matching(i,i+8)
results.append((17, [(i,17) for i in range(1,17)]+[(i,i+1) for i in range(1,16)]+[(16,1)]+[(i,i+8) for i in range(1,9)], "star17+C16+matching"))

print(f"{'n':>3} {'c':>3} {'swings':<55} OK")
print("-"*90)
for n, edges, name in results:
    eta = build(n, edges)
    g = reduce(gcd, eta)
    c = g
    ok = sorted(e//g for e in eta) == sorted([1]+[2]*(n-1))
    assert ok, f"FAIL n={n}"
    print(f"{n:>3} {c:>3} {str(eta):<55} OK ({name})")
# ---------------------------------------------------------------------------------------
# The appendix constructions, checked as a chain rather than through a single formula.
#
# For large n the 2^n coalitions cannot be enumerated, which is why the paper quotes the
# constructions of the appendix dataset "by formula (U)".  (U) is proved (Proposition 11) and its
# four cases use nothing but the definition of v(G,F), so for these instances the claim
# Bz(v) = psi^n is a theorem once two finite hypotheses are checked on the shipped data:
#   (i)  Pairs(F) is contained in G   -- so that v(G,F) is a simple game;
#   (ii) deg_G(i) + r_i is constant, with the special player c/2 above the rest -- the structure
#        the constructions were found with.
# Both are checked for every n = 6..80 below.  For n up to BRUTE_MAX the swing counts are
# additionally enumerated directly, so for those the conclusion never passes through (U) at all.
import itertools, json, os


def swings_wfamily(G, F, n):
    """Swing counts of v(G,F) by direct enumeration, straight from its definition."""
    W = [False] * (1 << n)
    for m in range(1 << n):
        k = bin(m).count("1")
        if k >= n - 1:
            W[m] = True
        elif k == n - 2:
            W[m] = tuple(sorted(i for i in range(n) if not (m >> i) & 1)) in G
        elif k == n - 3:
            W[m] = tuple(sorted(i for i in range(n) if not (m >> i) & 1)) in F
    eta = [0] * n
    for i in range(n):
        bit = 1 << i
        for m in range(1 << n):
            if m & bit:
                continue
            if (not W[m]) and W[m | bit]:
                eta[i] += 1
    return eta


DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                    "appendix-data-n80.json")
with open(DATA, encoding="utf-8") as fh:
    dataset = json.load(fh)

BRUTE_MAX = 24
bad = []
for n in range(6, 81):
    rec = dataset[str(n)]
    G = {tuple(e) for e in rec["G"]}
    F = {tuple(t) for t in rec["F"]}
    c = rec["c"]
    deg = [sum(1 for e in G if i in e) for i in range(n)]
    r = [sum(1 for t in F if i in t) for i in range(n)]
    e = [sum(1 for t in F if i in t and tuple(sorted(set(t) - {i})) not in G) for i in range(n)]
    if not all(tuple(sorted(p)) in G for t in F for p in itertools.combinations(t, 2)):
        bad.append((n, "Pairs(F) not contained in G"))
    Dvals = {deg[i] + r[i] for i in range(n - 1)}
    if len(Dvals) != 1:
        bad.append((n, "deg_G + r_i not constant off the special player"))
    elif deg[n - 1] + r[n - 1] != Dvals.pop() + c // 2:
        bad.append((n, "special player not c/2 above the constant"))
    beta = [len(G) + (n - 1) + len(F) - 2 * deg[i] - 2 * r[i] + e[i] for i in range(n)]
    if beta[:n - 1] != [2 * c] * (n - 1) or beta[n - 1] != c:
        bad.append((n, "formula (U) does not return psi^n (got %s)" % beta[:3]))
    if n <= BRUTE_MAX:
        eta = swings_wfamily(G, F, n)
        g = reduce(gcd, eta)
        if g != c or sorted(x // g for x in eta) != sorted([1] + [2] * (n - 1)):
            bad.append((n, "direct enumeration does not return psi^n"))
assert not bad, "DATASET CHAIN FAIL: %s" % bad
print("DATASET CHAIN: n = 6..80 PASS -- Pairs(F) in G, deg_G + r_i = D with the special player "
      "c/2 above it, (U) = c*(2,...,2,1), and direct swing enumeration for n <= %d" % BRUTE_MAX)
# ---------------------------------------------------------------------------------------
# Observation 10, exercised here on a range the gate can afford.
#
# The manuscript states Observation 10 as certified for n <= 19 (q3/certify_obs10.py decides both
# inequivalent cases exactly).  The full range costs about fifteen minutes, which a gate should not,
# so the encoding is exercised here for n <= OBS10_MAX (about half a minute); the recorded result
# for n <= 18 stands on the run documented in q3/README.md.  The control matters as much as the
# verdict: the same model must be FEASIBLE when the losing-set constraint is dropped, or the
# "certification" would only show that the model admits nothing at all.
import importlib.util

OBS10_MAX = 12
_spec = importlib.util.spec_from_file_location(
    "certify_obs10", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "q3",
                                  "certify_obs10.py"))
obs10 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(obs10)

bad_obs = []
for n in range(6, OBS10_MAX + 1):
    for case in ("A", "B"):
        verdict, _, _ = obs10.decide(n, case, 900, 8)
        if verdict != "INFEASIBLE":
            bad_obs.append((n, case, verdict))
verdict, _, _ = obs10.decide(6, "none", 900, 8)
if verdict != "FEASIBLE":
    bad_obs.append((6, "control", verdict))
assert not bad_obs, "OBS10 FAIL: %s" % bad_obs
print("OBS10: n = 6..%d PASS -- no simple game on n <= %d voters has Bz = psi^n with a losing "
      "(n-1)-set, in either of the two inequivalent cases (and n = 6 is feasible without that "
      "constraint, the control)" % (OBS10_MAX, OBS10_MAX))
print("ALL CLOSED-FORM CONSTRUCTIONS VERIFIED.")
