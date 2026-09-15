t = open(r'manuscript.md', encoding='utf-8').read()
old = '''Indeed, the residue classes n ≡ 6 (mod 7) and n ≡ 0 (mod 7) are solvable for every admissible n
with the *constant* common degree d = 2 (respectively d = 3), since then deg_G(n) = (4n+4)/7
(resp. (5n+7)/7) ≤ n−1. Thus Conjecture 16 holds, by Theorem 1, for an infinite set of n; the
values n ∈ {8, 10, 11, 12, 15, 18, 19, 22, 25, 26, 29, …} require a genuinely different
construction.'''
new = '''Indeed, the residue classes n ≡ 6, 0, 2, 3 (mod 7) are solvable for every admissible n with
the *constant* common degree d = 2, 3, 1, 4 respectively, since then deg_G(n) = (4n+4)/7,
(5n+7)/7, (3n+1)/7, (6n−18)/7 ≤ n−1. Thus Conjecture 16 holds, by Theorem 1, for **four of the
seven residue classes** (i.e. for infinitely many n); the values n ≡ 1, 4, 5 (mod 7) require a
genuinely different construction (given in Sections 4 and 9).'''
assert old in t
t = t.replace(old, new)
old2 = '''(iv) find explicit closed-form constructions for the remaining three residue classes
(n ≡ 1, 4, 5 (mod 7)) using a triangle-based construction (with a small number of "special
triples" containing the distinguished player), so that **every n ≥ 19 admits an explicit
closed-form game realizing ψⁿ**, unified in a single parametric family with base degree 3; and
(v) close the five smallest remaining values 8, 10, 11, 12, 15 with explicit constructions.
**Consequently Kurz's Conjecture 16 is fully resolved: for every n ≥ 6 there is an explicit
closed-form simple game with Bz(v) = ψⁿ.**'''
new2 = '''(iv) find explicit closed-form constructions for the remaining three residue classes
(n ≡ 1, 4, 5 (mod 7)) using a triangle-based construction (with a small number of "special
triples" containing the distinguished player), and (v) close the small values 8, 10, 11, 12, 15, 18
with explicit constructions. **Consequently Kurz's Conjecture 16 is fully resolved: for every
n ≥ 6 there is an explicit closed-form simple game with Bz(v) = ψⁿ.**'''
assert old2 in t
t = t.replace(old2, new2)
open(r'manuscript.md', 'w', encoding='utf-8').write(t)
print('polished')
