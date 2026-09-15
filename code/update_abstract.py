t = open(r'manuscript.md', encoding='utf-8').read()
old = '''(iv) find explicit closed-form constructions for the remaining three residue classes
(n ≡ 1, 4, 5 (mod 7)) using a triangle-based construction, so that **every n ≥ 67 admits an
explicit closed-form game realizing ψⁿ**; and (v) verify the conjecture computationally for all
6 ≤ n ≤ 66 (exhaustive enumeration, O(n³)-variable MILP, and OR-Tools CP-SAT with a small-|F|
constraint). **Consequently Kurz's Conjecture 16 is confirmed for every n ≥ 6.**'''
new = '''(iv) find explicit closed-form constructions for the remaining three residue classes
(n ≡ 1, 4, 5 (mod 7)) using a triangle-based construction (with a small number of "special
triples" containing the distinguished player), so that **every n ≥ 19 admits an explicit
closed-form game realizing ψⁿ**, unified in a single parametric family with base degree 3; and
(v) verify the six small remaining values 8, 10, 11, 12, 15, 18 computationally (O(n³)-variable
MILP and OR-Tools CP-SAT). **Consequently Kurz's Conjecture 16 is confirmed for every n ≥ 6.**'''
assert old in t, "abstract pattern not found"
t = t.replace(old, new)
open(r'manuscript.md', 'w', encoding='utf-8').write(t)
print('abstract updated')
