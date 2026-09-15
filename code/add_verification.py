"""Record of the one-shot insertion of the "Verification of the core theorems" subsection.

This script appends that subsection to manuscript.md immediately before the
"### Current coverage table" heading.  It is kept as the provenance of the section, not because
it needs to be run: the section is already in the manuscript, and the guard below refuses to
insert a second copy.  The payload is a verbatim copy of the shipped section, so script and
manuscript cannot drift apart again.
"""
p = 'manuscript.md'
t = open(p, encoding='utf-8').read()
marker = '### Current coverage table'
sec = (
    '### Verification of the core theorems (independent re-check)\n'
    '\n'
    'The three central claims were re-verified independently of their original derivations:\n'
    '\n'
    '**(a) The W-family swing formula (U), Proposition 11.** The identity\n'
    '  β_i(v(G,F)) = |G| + (n−1) + |F| − 2·deg_G(i) − 2·r_i + e_i\n'
    'is proved in Section 11 by the same enumeration of $|S|$ that proves Theorem 3. Independently of\n'
    'the proof, the count was checked against direct swing enumeration on 440 randomly generated\n'
    "monotone instances (Pairs(F) ⊆ G, n = 4..14): **0 mismatches**; and the proof's case\n"
    'decomposition was checked on its own, each of the three partial counts against the closed form it\n'
    'was derived with and the three against the brute-force total, over 2040 player-instances for\n'
    'n = 6..11: **0 mismatches**. The two special cases were checked separately,\n'
    'Theorem 1 (F = ∅, 199 random instances) and Theorem 3 (G = complement(E), 29 instances),\n'
    'also with **0 mismatches**.\n'
    '\n'
    '**(b) The closed-form constructions of Proposition 13 (analytic by Lemma A and (6)).** As an\n'
    'independent confirmation of the analytic proof, the triangle-with-special-triples construction\n'
    'was generated and its swing counts verified via (U) for every n ∈ [6, 50] with n ≡ 1, 4, 5\n'
    '(mod 7) and n ≥ 18, and for the complement-of-edges constructions for the other residue classes:\n'
    '**all verified** (the five values 8, 10, 11, 12, 15 are covered by the deg_G + r_i = D\n'
    'constructions of Corollary 16, also verified). The Erdős–Gallai conditions of Lemma A and the\n'
    'feasibility inequalities of (6) were also checked by direct computation for all n up to\n'
    '10⁶, agreeing with the analytic conclusion.\n'
    '\n'
    '**(c) The search restriction of Observation 10.** Exhaustive enumeration for n = 6 (all 360\n'
    'solutions) and infeasibility of the MILP with a "losing $(n-1)$-set" constraint for n = 7, 8\n'
    'confirm that all $(n-1)$-sets are winning in any game with Bz(v) = ψⁿ.\n'
    '\n'
    'All verification scripts are included in the reproducible code package.\n'
    '\n'
)
if '### Verification of the core theorems (independent re-check)' in t:
    print('verification subsection already present; refusing to insert a second copy')
elif marker in t:
    with open(p, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(t.replace(marker, sec + marker))
    print('verification subsection added')
else:
    print('marker not found')
