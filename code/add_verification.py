p = r'manuscript.md'
t = open(p, encoding='utf-8').read()
marker = '### Current coverage table'
sec = '''### Verification of the core theorems (independent re-check)

The three central claims were re-verified independently of their original derivations:

**(a) The W-family swing formula (U), Proposition 8.** The identity
  β_i(v(G,F)) = |G| + (n−1) + |F| − 2·deg_G(i) − 2·r_i + e_i
was checked against direct swing enumeration on 440 randomly generated monotone instances
(Pairs(F) ⊆ G, n = 4..14): **0 mismatches**. The two special cases were checked separately —
Theorem 1 (F = ∅, 199 random instances) and Theorem 2 (G = complement(E), 29 instances) —
also with **0 mismatches**.

**(b) The closed-form constructions of Proposition 11.** The triangle-with-special-triples
construction was generated and its swing counts verified via (U) for every n ∈ [6, 50] with
n ≡ 1, 4, 5 (mod 7) and n ≥ 18, and for the complement-of-edges constructions for the other
residue classes: **all verified** (the five values 8, 10, 11, 12, 15 are covered by the
deg_G + r_i = D constructions of Corollary 14, also verified).

**(c) The necessary property of Proposition 6.** Exhaustive enumeration for n = 6 (all 360
solutions) and infeasibility of the MILP with a "losing (n−1)-set" constraint for n = 7, 8
confirm that all (n−1)-sets are winning in any game with Bz(v) = ψⁿ.

All verification scripts are included in the reproducible code package.

'''
if marker in t:
    t = t.replace(marker, sec + marker)
    open(p, 'w', encoding='utf-8').write(t)
    print('verification subsection added')
else:
    print('marker not found')
