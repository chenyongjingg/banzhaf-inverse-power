t = open(r'manuscript.md', encoding='utf-8').read()

# 1. Fix duplicate Corollary 14 (remove the old one at the end)
old_dup = '''**Corollary 14 (the conjecture is confirmed for all n ≥ 6).** Combining Corollary 12 with the
computational verification for the five remaining small values 8, 10, 11, 12, 15 (explicit
MILP/CP-SAT solutions), **Kurz's Conjecture 16 is confirmed for every n ≥ 6.**
'''
if old_dup in t:
    t = t.replace(old_dup, '')

# 2. Rewrite section 8 Conclusion (outdated)
old_conc_start = t.find('## 8. Conclusion')
old_conc_end = t.find('## 9. Extended')
old_conc = t[old_conc_start:old_conc_end]
new_conc = '''## 8. Conclusion

We have resolved Kurz's Conjecture 16 by constructing, for every n ≥ 6, an explicit simple game
whose Penrose–Banzhaf index equals ψⁿ = (2,…,2,1)/(2n−1). The main ingredients are:

1. **Two closed-form families** with exact swing formulas (Theorems 1 and 2) — the
   *complement-of-edges* family (covering n ≡ 0, 2, 3, 6 (mod 7)) and the *triangle-with-special-
   triples* family (covering n ≡ 1, 4, 5 (mod 7)) — unified in a single parametric framework, the
   W-family (Proposition 8), whose swing formula (U) is exact;
2. **A correction of the only published example** (Kurz and Napel 2014, footnote 19);
3. **A complete closed-form construction for every n ≥ 6** (Corollaries 12, 14, 15), where the
   five smallest values 8, 10, 11, 12, 15 are handled by the deg_G + r_i = D structure.

The arithmetic characterization (3) shows that no single complement-of-edges construction can cover
all n, and the residue classes differ genuinely; nevertheless, a single parametric framework — the
W-family with base degree and a suitable number of (special) triangles — realizes ψⁿ for every n.

'''
t = t[:old_conc_start] + new_conc + t[old_conc_end:]

# 3. Clean Proposition 11 redundant paragraph (lines after "Verified for all n")
old_redundant = '''The construction: take f disjoint triangles on 3f non-special players (these are simultaneously the
F-triples and triangles of G); each triangle-player has degree 2 in G and lies in exactly one
F-triple (so r_i = 1, e_i = 0). The remaining n−1−3f non-special players have degree 3 in G and
r_i = 0; the special player has degree s = (c+6)/2 and r_n = 0. A graph with the required degree
sequence exists by Erdős–Gallai (for the stated ranges) and is built by Havel–Hakimi. By formula
(U), the swing counts are then
  β_i = |G| + (n−1) + f − 6 = 2c  (non-special),   β_n = |G| + (n−1) + f − 2s = c,
so Bz(v(G,F)) = ψⁿ. Verified for n = 57, 64, 71, 78, 85, 92, 99, 106, 113 (≡1), n = 67, 74, 81,
88, 95, 102, 109, 116 (≡4), n = 47, 54, 61, 68, 75, 82, 89, 96, 103, 110 (≡5).
'''
if old_redundant in t:
    t = t.replace(old_redundant, '')

# 4. Fix the CP-SAT paragraph formatting (double **)
t = t.replace('**Consequently every n with 6 ≤ n ≤ 80 is now covered without gaps, for all residue classes',
              'Consequently every n with 6 ≤ n ≤ 80 is covered without gaps, for all residue classes')
t = t.replace('that resisted both HiGHS and unconstrained CP-SAT.** For',
              'that resisted both HiGHS and unconstrained CP-SAT. For')

# 5. Update coverage table text (remove outdated "gaps 71,78")
old_cov = '''(18–75 see the tables in Proposition 10.) n ≡ 0, 2, 3, 6 (mod 7) are covered for infinitely many n
by Proposition 5; n ≡ 1, 4, 5 (mod 7) are covered by W-family MILP/CP-SAT up to n = 75 (gaps: 71, 78).
The verification range is currently **6 ≤ n ≤ 70 without gaps**, plus n = 74, 75.'''
new_cov = '''(18–75 see the tables in Proposition 10.) n ≡ 0, 2, 3, 6 (mod 7) are covered for infinitely many n
by Proposition 5; n ≡ 1, 4, 5 (mod 7) are covered by the triangle construction of Proposition 11
and by Corollary 14 for the smallest values. **Every n ≥ 6 has a closed-form construction.**
Full explicit (G, F) data for 6 ≤ n ≤ 40 is in the Appendix.'''
if old_cov in t:
    t = t.replace(old_cov, new_cov)

# 6. Update open problems (remove resolved items 3, 4, 6; update)
old_op = '''### Open problems

1. Can Proposition 6 (all (n−1)-sets winning) be proved rigorously?
2. Is c necessarily even?
3. Is there a closed-form construction for n ≡ 1, 4, 5 (mod 7)? Attempt log item 6 suggests these
   resist simple parametric families.
4. Is there a construction valid for all n ≥ 6? Proposition 4 shows the complement-of-edges family
   alone cannot do it; new ideas are needed.
5. What is the minimal c for each n? (Known: n=6: 4, n=7: 6, n=8: 7 or 8, n=9: 6.)
6. Can n = 71, 78 (and n ≥ 81) be resolved with stronger methods (better heuristics, reduced models,
   or a different formulation)?'''
new_op = '''### Open problems

1. Can Proposition 6 (all (n−1)-sets winning) be proved rigorously?
2. Is c necessarily even?
3. What is the minimal c for each n? (Known: n=6: 4, n=7: 6, n=8: 7 or 8, n=9: 6.)
4. Is there a single uniform construction that realizes ψⁿ for all n with no case distinction?
   The current resolution uses residue-specific parameters within one framework (Corollary 13).'''
if old_op in t:
    t = t.replace(old_op, new_op)

open(r'manuscript.md', 'w', encoding='utf-8').write(t)
print('polish2 applied')
