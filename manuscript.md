<!--
Title (kept as readable text here; compiled via the raw-LaTeX title block below):
Prescribed Banzhaf Power by Exact Computation: Closed-Form Realizations and
Certified Weighted Obstructions
-->
\title{Prescribed Banzhaf Power by Exact Computation: Closed-Form Realizations and Certified Weighted Obstructions}
\author{Yongjin Chen\textsuperscript{a}, Shi Jin\textsuperscript{a}, Songze Zhu\textsuperscript{a,*}\\[4pt]
{\footnotesize \textsuperscript{a} School of Public Security Management, People's Public Security}\\[1pt]
{\footnotesize University of China, Beijing 100038, China}\\[2pt]
{\footnotesize \textsuperscript{*} Corresponding author. E-mail: 20196846@ppsuc.edu.cn}}
\date{}
\maketitle

## Abstract

Designing a voting rule that realizes a prescribed distribution of voting power — the inverse power
index problem — is a fundamental computational task for parliaments, councils, and other weighted
voting bodies. This paper develops an exact, fully reproducible computational methodology for the
inverse Banzhaf problem and applies it to the egalitarian benchmark target of Kurz (2015), in which a
single player holds half the voting power of each of the remaining players.

On the constructive side, a single parametric family of simple games (the W-family) with an exact
closed-form swing formula yields explicit realizing games for every number of voters from six upward,
resolving Kurz's Conjecture 16 and correcting the sole erroneous published example; a compact
formulation with a cubic number of variables solves every instance up to eighty voters in seconds to
minutes. On the obstruction side, a sharpened swap/block rigidity condition drives a deterministic
constraint-programming satisfiability (CP-SAT) certification that no weighted majority game on six to
ten voters realizes the target, at a conclusive weight bound, and the certified optimal weighted
approximation is computed exactly for up to eight voters.

As a computational case study, the methodology is applied to the historical weighted Council of the
European Union: its exact Banzhaf power distributions are reproduced and shown to be far from the
target, with the certified optimal redesign for six voters improving the distance about threefold.
Every numerical claim is reproducible from the companion code package.

**Keywords:** voting games; Banzhaf power index; inverse power index problem; integer programming; constraint programming

## 1. Introduction: the inverse Banzhaf problem

Designing a voting rule for a committee of *dissimilar* members — a weighted parliament, the Council
of the European Union, or a federal upper chamber — is a decision problem: the designer must decide
how voting *power* is to be distributed among members. The Banzhaf index (and the related
Shapley–Shubik index) quantify power as the normalized number of *swings*, i.e., coalitions in which
a member is decisive (Penrose 1946; Felsenthal & Machover 1998); for a weighted majority game,
computing these indices is NP-hard (Matsui & Matsui 2001). The **inverse power index problem**
is the formal dual of this computation: given a desired power distribution, decide whether a voting
rule realizes it, construct one if so, and certify impossibility otherwise (Nurmi 1982; Kurz & Napel
2014; de Keijzer et al. 2014). From an operations-research standpoint this is an
*inverse-optimization* problem: the power index is the forward map from rules to power distributions,
and the designer must invert it subject to the structural constraints of a chosen rule class —
general simple games, or the weighted majority games used by most real voting bodies (Muroga 1971).

This paper contributes an exact, fully reproducible computational methodology for both halves of this
design decision problem, and applies it to a benchmark target that has resisted a unified treatment
since 2014: the vector
  ψⁿ = (2, …, 2, 1) / (2n−1),          (1)
which assigns to n−1 members twice the power of the remaining member. Kurz (2015) conjectured the
existence of a realizing simple game for every n ≥ 6:

> **Conjecture 16 (Kurz 2015).** For every n ≥ 6 there exists a simple game v on n voters such
> that Bz(v) = ψⁿ, where Bz is the (normalized) Penrose–Banzhaf index.

and the natural dual — that no *weighted majority* game can do so (Kurz's Conjecture 15). Kurz and
Napel (2014) verified Conjecture 16 computationally for 6 ≤ n ≤ 18, but gave no construction valid
for all n; we provide one (Corollaries 14–17, Section 11), and settle the weighted obstruction
computationally for n ≤ 10 (Section 9).

The paper is organized as an exact computational study, centered on two engines. On the constructive
side, Sections 3–7 give closed-form families, exact swing formulas, and explicit games realizing ψⁿ
for every n ≥ 6; Section 8 summarizes the constructive half. On the obstruction side, Section 9
derives a sharp structural rigidity property (M′) and certifies by the constraint-programming
satisfiability (CP-SAT) solver that no weighted majority game realizes ψⁿ for n ≤ 10; Section 10
collects the two engines as a reusable methodology, with complexity statements and instance tables;
Section 11 develops the unified W-family framework, the exact closed-form constructions, and the open
problems. Section 12 applies the methodology as an exact computational case study to the historical
weighted Council of the European Union, whose actual Banzhaf power distributions fall exactly in the
certified range. Section 13 concludes.

## 2. Preliminaries

Let N = {1,…,n} be a set of voters. A **simple game** (Taylor & Zwicker 1999) is a monotone Boolean function
v : 2^N → {0,1} with v(∅) = 0 and v(N) = 1. A coalition S ⊆ N is **winning** if v(S) = 1 and
**losing** otherwise. A winning coalition is **minimal winning** if all its proper subsets are
losing; a simple game is uniquely determined by its family of minimal winning coalitions.

For i ∈ N, let
  β_i(v) = |{S ⊆ N\{i} : v(S) = 0, v(S ∪ {i}) = 1}|
be the number of **swings** of player i (the Banzhaf measure). The (normalized) **Penrose–Banzhaf
index** is
  Bz_i(v) = β_i(v) / Σ_j β_j(v).
Thus Bz(v) = ψⁿ iff β(v) is proportional to (2,…,2,1), i.e., iff n−1 players have an equal number
2c of swings and one player has c swings, for some integer c ≥ 1.

## 3. The complement-of-edges family

For a graph G on vertex set N with edge set E, consider the simple game v_G whose minimal winning
coalitions are exactly the complements of the edges of G:
  v_G(S) = 1  ⟺  S ⊇ N\{a,b} for some edge {a,b} ∈ E.
Equivalently, a coalition is winning iff it misses no edge of G. We prove:

**Theorem 1.** Let G be a graph on n vertices with edge set E. Suppose (i) G has no isolated
vertices, and (ii) G is not a star (no vertex is incident with every edge). Then the Banzhaf swing
counts of v_G are
  β_i(v_G) = |E| + (n−1) − 2·deg_G(i)     (i ∈ N).          (2)

*Proof.* Player i has a swing on a losing coalition S with i ∉ S and S ∪ {i} winning. The latter
means S ∪ {i} ⊇ N\{a,b} for some edge {a,b}.
- If |S| = n−3, then S ∪ {i} = N\{a,b} is an (n−2)-set, so S = N\({a,b} ∪ {i}) with i ∉ {a,b};
  such S is losing since it has size n−3. Each edge not containing i contributes exactly one such
  swing, giving |E| − deg_G(i) swings.
- If |S| = n−2, then S ∪ {i} = N\{x} for some x ≠ i. This is winning iff deg_G(x) ≥ 1, which
  holds by (i). The set S = N\{x,i} is losing iff {x,i} ∉ E (otherwise S contains the winning
  (n−2)-set N\{x,i}). Hence exactly (n−1) − deg_G(i) swings of this type.
- If |S| = n−1, then S = N\{i} and S ∪ {i} = N is winning. But N\{i} is losing iff every edge
  contains i, i.e., G is a star centered at i, excluded by (ii). Hence no swings of this type.
- No other cardinality yields a swing.

Summing gives β_i(v_G) = |E| + (n−1) − 2·deg_G(i). ∎

**Corollary 2.** If G has all vertices but one of common degree d and the exceptional vertex of
degree d + c/2, and if |E| + (n−1) − 2d = 2c, then Bz(v_G) = ψⁿ. Since 2|E| = nd + c/2, the
existence of such a graph is equivalent to the solvability of
  7c = d(2n−8) + 4(n−1)              (3)
in positive integers d, c with 0 ≤ d ≤ n−2 and d + c/2 ≤ n−1, together with the graphicality of
the degree sequence (d,…,d, d+c/2).

For 6 ≤ n ≤ 18, equation (3) admits such a solution exactly for n ∈ {6, 7, 9, 13, 14, 16, 17}.
For n ≡ 4 (mod 7) there is no solution at all; for n ∈ {8, 10, 12, 15} the required exceptional
degree exceeds n−1. Hence the complement-of-edges family alone does **not** cover all n — which is
consistent with the conjecture requiring a genuinely different construction for the remaining
values.

The condition (3) is solvable for *infinitely many* n: for n ≤ 30 the solvable values are
  6, 7, 9, 13, 14, 16, 17, 20, 21, 23, 24, 27, 28, 30, …
Indeed, the residue classes n ≡ 6, 0, 2, 3 (mod 7) are solvable for every admissible n with
the *constant* common degree d = 2, 3, 1, 4 respectively, since then deg_G(n) = (4n+4)/7,
(5n+7)/7, (3n+1)/7, (6n+10)/7 ≤ n−1. Thus Conjecture 16 holds, by Theorem 1, for **four of the
seven residue classes** (i.e. for infinitely many n); the values n ≡ 1, 4, 5 (mod 7) require a
genuinely different construction (given in Sections 4 and 9).

## 4. The threshold-with-exceptions family

The complement-of-edges family does not cover every n. For the remaining small values a second,
equally explicit family is useful. Let E be a set of pairs and F a set of triples of [n]. Define
the game v(E,F) by
  v(S) = 1  ⟺  |S| ≥ n−1,  or  (|S| = n−2 and N\S ∉ E),  or  (|S| = n−3 and N\S ∈ F).   (4)
That is, the game is "almost" a majority-style threshold at size n−2, with a set of *holes*
(N\S ∈ E) removed at level n−2 and a set of *exceptions* (N\S ∈ F) added at level n−3.

**Lemma (monotonicity).** v(E,F) is monotone (hence a simple game) iff no edge of E is contained
in a triple of F, i.e. E ∩ Pairs(F) = ∅, where Pairs(F) is the set of all two-element subsets of
triples in F. Indeed, a winning (n−3)-set $N\setminus X$ (X ∈ F) has a losing (n−2)-superset N\{a,b} exactly
when {a,b} ∈ E with {a,b} ⊆ X.

**Theorem 2.** For any E, F with E ∩ Pairs(F) = ∅, the swing counts of v(E,F) are
  β_i(v(E,F)) = C(n−1,2) + |F| − |E| + 2·deg_E(i) − 2·r_i + e_i,        (5)
where deg_E(i) is the degree of i in the graph E, r_i = |{X ∈ F : i ∈ X}|, and
e_i = |{X ∈ F : i ∈ X, X\{i} ∈ E}|.

*Proof sketch.* Player i swings on a losing S with S∪{i} winning. Enumerate by |S|:
- |S| = n−2 (S losing means N\S ∈ E): the unique losing (n−2)-set with i ∉ S and N\S ∈ E
  requires N\S ∋ i, giving deg_E(i) swings;
- |S| = n−3: S = N\{i,a,b} with {i,a,b} ∉ F and {a,b} ∉ E, giving
  C(n−1,2) − |E| + deg_E(i) − r_i + e_i swings;
- |S| = n−4: S = N\(X∪{i}) for X ∈ F with i ∉ X, giving |F| − r_i swings.
Summing yields (5). ∎ (The identity is verified exhaustively against direct computation on
random instances for n = 8, 10, 12.)

**Corollary 3.** If deg_E(i) − r_i is constant, say D, for all i ≠ n and deg_E(n) − r_n = D − c/2,
then Bz(v(E,F)) = ψⁿ with scale c = (n·C(n−1,2) + (n−6)|F| − (n−4)|E|)/(2n−1) (when this is a
positive integer). In particular, such games realize ψⁿ for every n ∈ {8, 10, 11, 12, 15} not
covered by Corollary 2 (found by solving (5) via mixed-integer programming; see Section 7), while
for n = 18 a solution was obtained by Kurz and Napel.

## 5. Explicit games realizing ψⁿ

For each n ∈ {6,7,9,13,14,16,17} we give the graph G_n (edges written as pairs) such that
Bz(v_{G_n}) = ψⁿ; the minimal winning coalitions of v_{G_n} are the complements of these edges.
The resulting swing vector is β = c·(2,…,2,1), displayed as a multiple of c.

| n | graph G_n | c | β(v_{G_n}) |
|--|-----------|--|----|
| 6 | C₄(1-2-6-3-1) ∪ K₃(4,5,6) | 4 | (8,8,8,8,8,4) |
| 7 | C₆ on {1,…,6} ∪ star centered at 7 | 6 | (12,…,12,6) |
| 9 | star at 9 on {1,2,3,4} ∪ matching {5,6},{7,8} | 6 | (12,…,12,6) |
| 13 | star at 13 on {1,…,8} ∪ matching on {1,…,8} ∪ C₄ on {9,…,12} | 12 | (24,…,24,12) |
| 14 | C₁₃ on {1,…,13} + chord {6,10} ∪ star at 14 except {6,10} | 16 | (32,…,32,16) |
| 16 | star at 16 on {1,…,7} ∪ matching on {8,…,15} | 12 | (24,…,24,12) |
| 17 | star at 17 (to all) ∪ C₁₆ on {1,…,16} ∪ matching {i,i+8} (1≤i≤8) | 24 | (48,…,48,24) |

Each entry is verified directly by computing the swing counts. For instance, the n = 6 entry is the
game whose minimal winning coalitions are
  {1,2,3,4}, {1,2,3,5}, {1,2,3,6}, {1,2,4,5}, {1,3,4,5}, {2,4,5,6}, {3,4,5,6}
(the complements of the seven edges of C₄ ∪ K₃), whose swing counts are (8,8,8,8,8,4).

## 6. A correction to the published example

Kurz and Napel (2014, footnote 19) state that the game on six voters whose minimal winning
coalitions are
  {2,4,5,6}, {2,3,4,5}, {1,3,5,6}, {1,3,4,5}, {1,2,4,6}, {1,2,3,5}
attains the PBI vector (8,8,8,8,8,4)/44 = ψ⁶. This is **incorrect**: a direct computation (or a
routine check by hand for, e.g., player 6, who has five swings) shows the swing counts are
  β = (7,7,7,7,9,5),   Σβ = 42,
so that Bz(v) = (7,7,7,7,9,5)/42 ≠ ψ⁶. The claim that an exact solution exists for n = 6 is
nevertheless true: the game in Section 5 (seven four-sets) attains ψ⁶. (An exhaustive enumeration
of all 7,828,354 simple games on six voters yields 360 games, in two symmetry classes, whose
Banzhaf index equals ψ⁶.)

## 7. Computational verification for 6 ≤ n ≤ 17

For the values n ∈ {8, 10, 11, 12, 15} not covered by Corollary 2 we verified existence by
formulating the problem as a mixed-integer program: variables x(S) ∈ {0,1} for the winning status
of each coalition S, the monotonicity constraints x(S) ≤ x(T) for S ⊆ T, the normalization
x(∅) = 0, x(N) = 1, and the swing equations
  Σ_{S ∌ i} (x(S∪{i}) − x(S)) = 2c (i ≠ n),   Σ_{S ∌ n} (x(S∪{n}) − x(S)) = c,
with c ≥ 1 integer. Using HiGHS, all these instances are feasible. Table 2 summarizes the scale c
found (n = 6, 7 by exhaustive enumeration; n = 13, 14, 16, 17 by the closed-form construction of
Section 4; the five remaining values by mixed-integer linear programming (MILP) — since reproduced at the same scales by the closed-form
deg_G + r_i = D constructions of Corollary 16).

| n | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
|---|----|----|----|----|----|----|----|----|----|----|----|----|
| c | 4 | 6 | 8 | 6 | 10 | 14 | 16 | 12 | 16 | 20 | 12 | 24 |

*Note.* The scale c = 20 for n = 15 was found by the CP-SAT model — an
improvement over the previously reported c = 22; minimality at n = 15 is open (a downward sweep at
c = 18 did not terminate within a 600 s solver budget). Minimality is certified for n = 8
(c = 8, with c ∈ {2, 4, 6} proven infeasible), n = 9 (c = 6, c ∈ {2, 4} infeasible) and n = 10
(c = 10, c ∈ {2, 4, 6, 8} infeasible); see Open problem 3 in Section 11.

For n = 6 the existence is established by exhaustive enumeration over all 7,828,354 simple games
(360 solutions in two symmetry classes). For n = 7, exhaustive enumeration of all games is
infeasible; we instead enumerated the 5-uniform family (winning coalitions of size 5) exhaustively
and found 490 solutions, all of the complement-of-edges type C₆ ∪ star₇. Thus Conjecture 16 holds
for every 6 ≤ n ≤ 17 by the constructions of Sections 3–5; the value n = 18 and all larger values
are covered by the closed-form constructions of Section 11 (Corollaries 14–17).

## 8. Summary of the constructive half

For the inverse voting-design problem, we have delivered the *construction half* in full: an
explicit, closed-form simple game whose Penrose–Banzhaf index equals ψⁿ = (2,…,2,1)/(2n−1) for every
n ≥ 6 — constructively resolving Kurz's Conjecture 16, whose benchmark status motivated the design
study. The main ingredients are:

1. **Two closed-form families** with exact swing formulas (Theorems 1 and 2) — the
   *complement-of-edges* family (covering n ≡ 0, 2, 3, 6 (mod 7)) and the *triangle-with-special-
   triples* family (covering n ≡ 1, 4, 5 (mod 7)) — unified in a single parametric framework, the
   W-family (Proposition 11), whose swing formula (U) is exact;
2. **A correction of the only published example** (Kurz and Napel 2014, footnote 19);
3. **A complete closed-form construction for every n ≥ 6** (Corollaries 14, 16, 17), where the
   five smallest values 8, 10, 11, 12, 15 are handled by the deg_G + r_i = D structure.

The arithmetic characterization (3) shows that no single complement-of-edges construction can cover
all n, and the residue classes differ genuinely; nevertheless, a single parametric framework — the
W-family with base degree and a suitable number of (special) triangles — realizes ψⁿ for every n.

## 9. The weighted case: ψⁿ is not realizable by any weighted majority game

We now turn to the *obstruction half* of the design decision problem: is the target ψⁿ realizable
within the weighted majority class — the rule class used by most real voting bodies (parliaments,
the EU Council, the IMF, corporate voting)? This is the question a designer must answer before
deciding whether to stay in the weighted class. It is precisely Kurz's **Conjecture 15**, the natural
"dual" of Conjecture 16. As stated by Kurz (2015, Conjecture 15) it is quantitative: there exists a
universal c > 0 with
‖Bz(v) − ψⁿ‖₁ ≥ c/n for every n ≥ 2 and every weighted majority game v. In particular no weighted
majority game reproduces ψⁿ exactly (distance zero is excluded). We certify the exact case for
n ≤ 10, and the quantitative form for n ≤ 8. Recall that a **weighted majority game** is a simple game [q; w₁,…,wₙ] with
integer weights 1 ≤ w₁ ≤ … ≤ wₙ and quota q ≥ 1, where S is winning iff W(S) = Σ_{i∈S} wᵢ ≥ q.
Let ηᵢ = βᵢ([q;w]) be the swing count. The following identity is a classical structural fact for
weighted majority games — a swap/block argument of the type long used in the Banzhaf literature (cf.
Felsenthal & Machover 1998). We do not claim it as new; what is new is that it rigidly dissects
Kurz's specific target ψⁿ, pinning the obstruction on a subset-sum problem.

**Proposition 4 (structural decomposition; swap/block argument).** Let v = [q; w] be a weighted
majority game with wᵢ ≥ wⱼ. Then
  ηᵢ − ηⱼ = 2 · |{ T ⊆ N\{i,j} : q − wᵢ ≤ W(T) < q − wⱼ }|.       (K)

*Proof.* Enumerate the swings of i and j by the subset T ⊆ N\{i,j} that excludes both, and by
whether the swing coalition S does or does not contain the other player:
- i swings on S = T iff W(T) ∈ [q−wᵢ, q);
- i swings on S = T ∪ {j} iff W(T) ∈ [q−wᵢ−wⱼ, q−wⱼ);
- j swings on S = T iff W(T) ∈ [q−wⱼ, q);
- j swings on S = T ∪ {i} iff W(T) ∈ [q−wᵢ−wⱼ, q−wᵢ).

Because wᵢ ≥ wⱼ, we have q−wᵢ ≤ q−wⱼ and q−wᵢ−wⱼ ≤ q−wᵢ, so [q−wⱼ, q) ⊆ [q−wᵢ, q) and
[q−wᵢ−wⱼ, q−wᵢ) ⊆ [q−wᵢ−wⱼ, q−wⱼ), and in both inclusions the *removed* interval is the same one,
[q−wᵢ, q−wⱼ). Summing the four counts over all T and subtracting ηⱼ from ηᵢ cancels the two common
pieces and leaves exactly twice the count of T with W(T) ∈ [q−wᵢ, q−wⱼ). ∎

The identity was verified on 12,000 random weighted games (n = 3…12, weights ≤ 30) with 0 failures
(`probe6_identity.py`).

**Corollary 5 (parity; resolves Observation 7 in the Appendix).** If Bz(v) = ψⁿ, then the
scale factor c is even. Two independent proofs:
- *(any simple game, Dubey–Shapley 1979)*: in every simple game all swing counts have a common
  parity. Here β = (2c,…,2c,c); since 2c is even, the common parity is even, so c is even.
- *(weighted, from (K))*: if w_s is the special player (ηₛ = c), then for any i ≠ s,
  c = ηᵢ − ηₛ = 2·|{T : q−wᵢ ≤ W(T) < q−wₛ}|, so c is even.

**Corollary 6 (the special player has strictly minimal weight).** Suppose ηₛ is the unique minimum
swing count and ηᵢ > ηₛ for every i ≠ s. Then wₛ < wᵢ for all i ≠ s. Indeed ηᵢ − ηₛ > 0 forces the
interval [q−wᵢ, q−wₛ) to contain some subset sum, so it is nonempty and wᵢ > wₛ. Thus, in any
weighted game whose Banzhaf index is proportional to ψⁿ, the singled-out voter must be the *unique
lightest* voter — an a-priori monotonicity constraint on the weights.

**Corollary 7 (interval decomposition and the mirror obstruction).** With s the special player and
η = (2c,…,2c,c), identity (K) applied to the pair (i, s) yields, for every i ≠ s,
  |{ T ⊆ N\{i,s} : q − wᵢ ≤ W(T) < q − wₛ }| = c/2,        (L)
so the excess c/2 of each non-special voter over the special voter is realized by subset sums of
N\{i,s} inside the weight gap [q−wᵢ, q−wₛ). Now fix two non-special voters i, j with wᵢ ≥ wⱼ (WLOG)
and split the window count in (L) at (i, s) according to whether j lies in T, and likewise the count
at (j, s) according to whether i lies in T:
  |{T ⊆ N\{i,s} : q−wᵢ ≤ W(T) < q−wₛ}|
    = |{T ⊆ N\{i,j,s} : q−wᵢ ≤ W(T) < q−wₛ}|
      + |{T ⊆ N\{i,j,s} : q−wᵢ−wⱼ ≤ W(T) < q−wₛ−wⱼ}|,
  |{T ⊆ N\{j,s} : q−wⱼ ≤ W(T) < q−wₛ}|
    = |{T ⊆ N\{i,j,s} : q−wⱼ ≤ W(T) < q−wₛ}|
      + |{T ⊆ N\{i,j,s} : q−wᵢ−wⱼ ≤ W(T) < q−wₛ−wᵢ}|,
both equal to c/2. Since wᵢ ≥ wⱼ > wₛ (Corollary 6), the relevant weight windows nest as disjoint
unions
  [q−wᵢ, q−wₛ) = [q−wᵢ, q−wⱼ) ⊔ [q−wⱼ, q−wₛ),
  [q−wᵢ−wⱼ, q−wₛ−wⱼ) = [q−wᵢ−wⱼ, q−wₛ−wᵢ) ⊔ [q−wₛ−wᵢ, q−wₛ−wⱼ),
so subtracting the two equalities leaves the **mirror identity**
  |{ T ⊆ N\{i,j,s} : q−wᵢ ≤ W(T) < q−wⱼ }|
    + |{ T ⊆ N\{i,j,s} : q−wₛ−wᵢ ≤ W(T) < q−wₛ−wⱼ }| = 0.   (M)
Both summands are nonnegative, hence they vanish individually:
  |{ T ⊆ N\{i,j,s} : q−wᵢ ≤ W(T) < q−wⱼ }| = 0  and
  |{ T ⊆ N\{i,j,s} : q−wₛ−wᵢ ≤ W(T) < q−wₛ−wⱼ }| = 0.         (M′)
In words: for every pair of non-special voters i, j with wᵢ ≥ wⱼ, the weight-gap window
[q−wᵢ, q−wⱼ) — and its translate by wₛ — is *sum-free* for the profile of the remaining n−3 voters.
Together with (L) this is a sharp rigidity statement: the c/2 sums realizing voter i's excess over s
must come exclusively from the part [q−wᵢ−wⱼ, q−wₛ−wⱼ) of the gap window, never from the sub-window
[q−wᵢ, q−wⱼ) itself; and the reflected sub-window [q−wₛ−wᵢ, q−wₛ−wⱼ) is likewise empty. (Verified
numerically: across 2.28×10⁵ random weighted games with ηᵢ = ηⱼ, both windows in (M′) were empty in
every case.)

**The Banzhaf–weighted obstruction property (M′).** We record the rigidity statement just derived as
the paper's central structural obstruction. Under the exact hypothesis η = (2c,…,2c,c), *any*
realizing game must satisfy (L) and (M′) — they are necessary conditions. They are also so tight
that the full constraint system — (L), (M′), together with the exact swing profile — is *provably
infeasible*, as certified by CP-SAT at the classical weight bound wᵢ ≤ 2^(n−1) for n = 6, …, 10
(Section 9, below). In this sense (M′) is the structural certificate of the obstruction: the
subset-sum windows it forces to be empty are precisely the degrees of freedom whose infeasibility
the deterministic solver establishes. The property is not merely cosmetic: the mirror constraints of
(M′) are the pruning constraints of the enhanced feasibility model (`conj15_feas2.py`), which decides
n = 6 in 2.5 s (vs 2.9 s) and n = 7 in 19 s — about six times faster than the unpruned model at n = 7 (117 s) — and are thus
what makes the n ≥ 9 frontier approachable at all. We are not aware of this reflected sum-freeness
rigidity in the threshold-logic or voting-power literature; the closest structural studies — Chow's
(1961) theorem on Chow parameters (a recovery problem) and the inverse-power-index certification results of
Alon & Edelman (2010) and Kurz (2016) — address reconstruction and worst-case approximation, not the
exact-hypothesis rigidity used here.

**Two-tier generalization ψⁿ(a,b) and a family-level no-go.** For a = b the target
ψⁿ(a,b) = (a,…,a,b)/((n−1)a+b) equals ψⁿ with c scaled. For a > b the W-family triangle
construction of Proposition 11 realizes ψⁿ(a,b) with special degree
  s = [ (a−b)(5n−5−p) − 4aq + 12b ] / (3a+b),               (N)
where p pure and q special triangles are used. Systematic search (probe4/probe5) gives:
- **(3,1) is uniform**: for all n ∈ [6, 80], s = n−1 with p = 0, q = 1 realizes ψⁿ(3,1) — the
  construction G = star(n) ∪ C_{n−1} ∪ {1,2}, F = {triangle on the special player} works for every
  n, no case distinction.
- **(k,1), k ≥ 4 is obstructed within this family**: for k ≥ 4 the required degree
  s ≈ 5(k−1)n/(3k+1) exceeds n−1 for large n, so no triangle construction of this shape exists.
  Coverage rates over n ∈ [6,80]: k=2: 73/75 (gaps 8, 11); k=3: 75/75; k=4: 40/75; k=5: 28/75;
  k=6: 9/75; k=7: 8/75. Combined with Corollaries 6–7, this is strong evidence that ψⁿ(k,1) for
  k ≥ 4 is not weighted-realizable at all; a complete proof is the subject of ongoing work
  (Corollary 6 pins w_s minimal; (L) and (M) then over-constrain the subset-sum profile).

**Computational obstruction (exact).** For ψⁿ itself, exact feasibility of a weighted realization
with swing vector (2c,…,2c,c) was settled by CP-SAT (`conj15_feas.py`). Infeasibility is certified at
the classical weight bound W = 2^(n−1): every weighted majority game on n voters has an integer
representation with all weights in [1, 2^(n−1)] (a standard bound, implied for n ≥ 3 already by
Muroga's sharper minimal-weight bound 3^(n/3)), so infeasibility at W = 2^(n−1) is conclusive:

| n | W = 2^(n−1) | model | verdict | runtime |
|---|----|-----|----------|---------|
| 6 | 32 | standard | INFEASIBLE | 2.9 s |
| 7 | 64 | standard | INFEASIBLE | 117 s |
| 8 | 128 | +symmetry breaking | INFEASIBLE | 316 s |
| 9 | 256 | enhanced (`feas2`) | INFEASIBLE | 1562.9 s |
| 10 | 512 | enhanced (`feas2`) | INFEASIBLE | 9527.4 s |

The pipeline is three-tiered, and we are explicit about which tier backs each claim. **Tier 1
(exhaustive)**: n = 6 is settled by enumerating all 1,111 weighted games, guaranteed. **Tier 2
(deterministic)**: n = 7, 8, 9 and 10 are settled by CP-SAT at the conclusive weight bound W = 2^(n−1)
(standard model for n = 7, 8; the enhanced model below for n = 9, 10), guaranteed. **Tier 3 (budgeted)**:
n ≥ 11 runs the same solver under a time budget, so a negative outcome there is heuristic evidence
for a trend, not a proof, and is labeled accordingly.

n = 6 agrees with the exhaustive enumeration of all 1,111 weighted games on 6 voters
(`weighted_enum.py`), whose best L₁-distance to ψ⁶ is 5/44 ≈ 0.1136; hence no weighted game attains
distance 0. The n = 8 run required the symmetry-breaking constraint that non-special voters can be
relabeled in nondecreasing weight order (all have equal target swing 2c); with it the infeasibility
certificate is found in 316 s, whereas the unconstrained model is inconclusive after 20 min. n = 9
is substantially harder: the standard model exhausts a full 2 h budget without a certificate
(UNKNOWN), a dramatic jump consistent with the exponential growth of the subset-sum constraint
structure. The enhanced model (`conj15_feas2.py`), which additionally enforces the sharp mirror
constraints (M′) — valid since they are consequences of the exact hypothesis — then decides n = 9
in 1562.9 s (3584 mirror constraints): **INFEASIBLE**. At n = 10 the same enhanced model decides
**INFEASIBLE** in 9527.4 s (9216 mirror constraints), while the standard model again exhausts a 2 h
budget without a
certificate (UNKNOWN). This closes the exact obstruction for all n ≤ 10, the strongest conclusive
statement currently available; the enhanced model already gives a 6× speedup on the smaller scales
(n = 6: 2.5 s, n = 7: 19 s), and its growing mirror-constraint set is what makes the n ≥ 9 frontier
approachable at all. This is exactly Kurz's Conjecture 15, which asserts the quantitative statement that for some universal
c > 0, ‖Bz(v) − ψⁿ‖₁ ≥ c/n for *every* weighted majority game v and every n ≥ 2. The exact
obstruction for n = 6, …, 10 is the first step; the constant c is extracted from the optimal L₁
errors computed just below.

**Optimal L₁-distance (exact computation, `conj15_l1.py`).** For each n we compute the exact minimal
value of ‖Bz(v) − ψⁿ‖₁ over all weighted majority games, by fixing the total number of swings
T = Σηᵢ and minimizing the integer objective Σ_{i≠s} |(2n−1)ηᵢ − 2T| + |(2n−1)ηₛ − T| in CP-SAT,
enumerating T over its full range and using the same weight bound W = 2^(n−1); the special player is
fixed at position n without loss (relabeling). The method reproduces the exhaustive n = 6 optimum
exactly (`conj15_l1.py` n=6 T≤45): **L₁ = 5/44 ≈ 0.113636 at T = 32, with weights w = (3,1,3,3,3,1),
quota q = 11**, matching the brute-force enumeration of all 1,111 weighted games — a strong check of
both methods.

| n | optimal L₁ | T | n·L₁ | 1/n |
|---|-----------|----|------|-----|
| 6 | 5/44 ≈ 0.113636 | 32 | ≈ 0.682 | 0.167 |
| 7 | ≈ 0.085470 | 45 | ≈ 0.598 | 0.143 |
| 8 | ≈ 0.066667 | 60 | ≈ 0.533 | 0.125 |

(The n = 8 value is certified as the global optimum: T = 60 is OPTIMAL by CP-SAT, and the total
swing count was swept over its full range to the theoretical maximum 8·2⁷ = 1024 —
`conj15_l1_range.py` — whose best value outside T = 60 is L₁ = 0.116667 at T = 280, well above the
incumbent.) For n = 7 the optimal profile is (5,7,7,7,7,7,5) with weights
(2,64,64,64,64,64,1) and quota 65; the value is certified OPTIMAL by CP-SAT (re-verified with a
600 s budget), and the full sweep over T ≤ 448 — the theoretical maximum 7·2⁶ of the total swing
count — confirms that no other total swing count improves on it: the best value in the complementary
range T ≥ 121 is L₁ = 0.119535 at T = 139 (`conj15_l1_range.py`), well above the incumbent. For n = 8
the optimum is attained at profile (6,8,8,8,8,8,8,6) with weights (2,3,3,3,3,3,3,1) and quota 4.
The column
n·L₁ is the empirical anchor for the universal constant in Conjecture 15: since ‖·‖₁ ≥ c/n, any
admissible c is at most infₙ n·L₁(n); the values above give
c ≤ min(30/44, 7·0.08547, 8·0.066667) ≈ 0.533. We stress the distinction between proof and
certification, which is central to how the computational results below are to be read: the value
5/44 for n = 6 is an exhaustive optimum, and 0.085470 for n = 7 is a *certified* optimum (over the
full range T ≤ 448 of the total swing count); the value 0.066667 for n = 8 is likewise a
*certified* optimum, the total swing count having been swept over its full range to the theoretical
maximum T = 8·2⁷ = 1024. The
exact target (2c,…,2c,c) is infeasible for 6 ≤ n ≤ 10 by the computation above, so the L₁-optimum
is strictly positive. It is the monotone decrease n·L₁ = 0.682 → 0.598 → 0.533 that supports the
*conjectured* Θ(1/n) asymptotics for all n; deriving an analytic lower bound ‖Bz(v) − ψⁿ‖₁ ≥ c/n
with an effective constant — not merely certification on the first three scales — remains open. The optimal profiles are asymmetric: the two lightest voters — the special voter and one
further voter — carry the reduced swing count, and they do not sit at the ideal scale T = (2n−1)c
(n = 6: profile (6,4,6,6,6,4) at weights (3,1,3,3,3,1), quota 11; n = 7: profile (5,7,7,7,7,7,5) at
weights (2,64,64,64,64,64,1), quota 65; n = 8: profile (6,8,8,8,8,8,8,6) at weights (2,3,3,3,3,3,3,1),
quota 4). This is consistent with Corollary 6: in the exact case the special voter alone would be
uniquely lightest, whereas near-optimal games distribute the reduction between the two lightest
voters.

## 10. Computational methodology: exact construction and certified obstruction

This section collects the two computational engines behind the paper as a reusable methodology —
with the complexity statements and instance tables expected of an operations-research study. Every
claim below is backed by a named script and a full log in the companion code package (Section 11).

### 10.1 Constructive engine: closed forms and the W-family MILP

*Task.* Given n, produce an explicit simple game with Bz(v) = ψⁿ, or show that the family under
consideration cannot cover n.

1. **Residue arithmetic.** For the complement-of-edges family, realization reduces (Theorem 1) to
   the diophantine equation 7c = d(2n−8) + 4(n−1) in positive integers d, c with 1 ≤ d ≤ n−2,
   d + c/2 ≤ n−1, together with Erdős–Gallai graphicality of the degree sequence (d,…,d, d+c/2).
   This is an O(1) decision per n, and the family covers exactly the four residue classes
   n ≡ 0, 2, 3, 6 (mod 7) (Proposition 8).
2. **W-family MILP/CP-SAT.** For the remaining residue classes, realization over the W-family of
   Proposition 11 is formulated as a MILP with edge variables x_e (e ∈ G) and triple variables
   y_T (T ∈ F), the bilinear products z = y·x linearized in the standard way, and the exact swing
   formula (U) together with the monotonicity constraint Pairs(F) ⊆ G as linear constraints.
   **Model size: O(n³) variables and constraints** (C(n,2) + C(n,3) variables) — versus 2ⁿ for
   the general monotone Boolean MILP of Section 7, which becomes intractable near n = 18. The
   compressed model solves every instance up to n = 64 in seconds to minutes (instance data below);
   its practical limiting factor is memory, reached around n ≈ 80.
3. **Closed forms.** Proposition 13 gives explicit triangle constructions for the three hard
   residue classes n ≡ 1, 4, 5 (mod 7), valid for all n ≥ 22, 18, 19 respectively; the small values
   8, 10, 11, 12, 15 are handled by the deg_G + r_i = D structure (Corollary 16). Combined with
   Step 1 and Corollary 14, **every n ≥ 6 admits an explicit closed form** (Corollary 17).

Representative W-family instances (hard residue classes; c = scale factor). All are explicit closed
forms, re-verified by direct swing enumeration against ψⁿ (full data in appendix-data-n80.json):

| n | n mod 7 | c | edges | triples | construction |
|---|---------|----|----|----|-------------|
| 18 | 4 | 24 | 33 | 6 | deg+r = D = 4 |
| 22 | 1 | 26 | 32 | 5 | tri(D3,f5,q3) |
| 25 | 4 | 30 | 36 | 6 | tri(D3,f6,q3) |
| 39 | 4 | 50 | 62 | 6 | tri(D3,f6,q2) |
| 67 | 4 | 90 | 114 | 6 | tri(D3,f6,q0) |
| 71 | 1 | 96 | 123 | 5 | tri(D3,f5,q0) |
| 74 | 4 | 100 | 127 | 6 | tri(D3,f6,q0) |
| 78 | 1 | 106 | 136 | 5 | tri(D3,f5,q0) |

Here `tri(D,f,q)` denotes the triangle construction of Proposition 13 with base degree D, f disjoint
triangles and q special triples (containing the special player), and `deg+r = D` the small-value
structure of Corollary 16. The structural insight for the hard residues is that the solutions use
few exceptional triples — f ∈ {4, 5, 6} — and that for n ≥ 67 the special player need not
participate in any special triple (q = 0; Corollary 15).

### 10.2 Verification engine: certification of weighted obstructions

*Task.* Given n, decide whether any weighted majority game [q; w] on n voters realizes the exact
target swing vector (2c,…,2c,c); if none exists, produce a certificate.

1. **Constraint system and conclusive weight bound.** The model (`conj15_feas.py`) has variables
   w₁ ≤ … ≤ wₙ ≤ W, q, and the swing counts ηᵢ, together with the exact profile equations
   (ηᵢ = 2c for i ≠ s, ηₛ = c) and the structural consequences (L), (M′) of Section 9. Infeasibility
   at W = 2^(n−1) is conclusive, because every weighted majority game on n voters admits an integer
   representation with all weights in [1, 2^(n−1)] (Muroga's sharper bound 3^(n/3) applies for
   n ≥ 3). A solver certificate of infeasibility at this bound is therefore a proof for that n, not
   a heuristic.
2. **Symmetry breaking.** Non-special voters may be relabeled in nondecreasing weight order (they
   carry equal target swing 2c). Without this constraint n = 8 remains inconclusive after 20 min;
   with it the certificate is found in 316 s.
3. **Mirror pruning.** The sharp constraints (M′) of Corollary 7 are consequences of the exact
   hypothesis, hence valid; enforcing them (`conj15_feas2.py`) yields a roughly six-fold speedup
   (n = 6: 2.5 s vs 2.9 s; n = 7: 19 s vs 117 s, a six-fold speedup) and — decisively — makes the n ≥ 9 frontier decidable at all.

Certified obstructions (deterministic, at W = 2^(n−1)):

| n | W = 2^(n−1) | model | verdict | runtime |
|---|----|-----|----------|---------|
| 6 | 32 | standard | INFEASIBLE | 2.9 s |
| 7 | 64 | standard | INFEASIBLE | 117 s |
| 8 | 128 | +symmetry breaking | INFEASIBLE | 316 s |
| 9 | 256 | +mirror | INFEASIBLE | 1562.9 s |
| 10 | 512 | +mirror | INFEASIBLE | 9527.4 s |

The n = 6 verdict agrees with exhaustive enumeration of all 1,111 weighted games (Tier 1); n = 7–10
are Tier-2 deterministic certificates. Under a two-hour budget the standard (unpruned) model remains
UNKNOWN at n = 9 and n = 10 — the mirror constraints are what closes these cases. For n ≥ 11 the
same solver is run budgeted, so a negative outcome there is heuristic (Tier 3) and is labelled as
such. The mirror constraints — 3584 at n = 9 and 9216 at n = 10, i.e. C(n−1,2)·2^(n−2) window
conditions, one per subset of the n−3 remaining voters and for both windows — are themselves a
measure of the rigidity that (M′) forces on any realizing game.

### 10.3 Exact optimization over total swing count

For the quantitative form of Conjecture 15 we compute the minimal L₁-distance
‖Bz(v) − ψⁿ‖₁ exactly. Fixing the total number of swings T = Σηᵢ, the integer objective
Σ_{i≠s} |(2n−1)ηᵢ − 2T| + |(2n−1)ηₛ − T| is minimized in CP-SAT; T is enumerated over its full
range up to the theoretical maximum n·2^(n−1), at the same conclusive weight bound (`conj15_l1.py`,
`conj15_l1_range.py`). The method reproduces the exhaustive n = 6 optimum 5/44 (weights (3,1,3,3,3,1),
quota 11) exactly — a strong cross-check of both methods. Certified optima over the full swing
range: n = 7, L₁ ≈ 0.085470 at T = 45; n = 8, L₁ ≈ 0.066667 at T = 60 (over T ≤ 1024). These give
c ≤ min(30/44, 7·0.08547, 8·0.066667) ≈ 0.533. At n = 9 the problem hits the CP-SAT complexity
cliff: with 120 s per T-value, 23 of the 112 values in [9,120] are decided, 0 are certified
infeasible, and the best found L₁ ≈ 0.1042 (at T = 70) is not certified. We report this honestly as
the current frontier: **c ≤ 0.533 is certified for n ≤ 8; no certified value exists at n = 9.**

### 10.4 Reproducibility

Every claim above is tied to a named script — `conj15_feas.py`, `conj15_feas2.py`, `conj15_l1.py`,
`conj15_l1_range.py`, `weighted_enum.py`, `probe6_identity.py`, and the W-family MILP/CP-SAT solver of
Proposition 12 — with full logs in the companion package; solver versions, hardware, and per-run
parameters are recorded in the package README.

## 11. The W-family: unified constructions, structural properties, and open problems

This section develops the W-family into its full scope: it proves the unified swing formula that
the construction half (Section 8) relies on, establishes the structural properties that govern which
residue classes admit closed-form realizations, and collects the open problems that remain. All
results are labelled with their derivation or verification method; unproven numerical observations
are explicitly marked as such. Reproducible code is given in the appendix.

### Proposition 8 (Exact description of complement-of-edges coverage; Erdős–Gallai computation)

For each n ≥ 6, the complement-of-edges family (Theorem 1) is solvable at n if and only if there are
positive integers d, c with
  7c = d(2n−8) + 4(n−1),  1 ≤ d ≤ n−2,  c even,  d + c/2 ≤ n−1,  (n·d + c/2) even,
and the degree sequence (d,…,d, d+c/2) passes the Erdős–Gallai test and is constructible by
Havel–Hakimi.

**Lemma A (two-value Erdős–Gallai reduction).** Let 1 ≤ d < D ≤ n−1. The degree sequence
(d, …, d, D) with n−1 copies of d is graphical if and only if (n−1)d + D is even, D ≤ n−1,
and D ≤ d(n−d).

*Proof.* Sorting descending as (D, d, …, d), the Erdős–Gallai inequalities are, for every k,
Σ_{i≤k} aᵢ ≤ k(k−1) + Σ_{i>k} min(aᵢ, k). For k = 1 this reads D ≤ n−1. For 2 ≤ k ≤ d every
aᵢ = d ≥ k, so the RHS is k(k−1) + (n−k)k = k(n−1); the strongest such inequality is at k = 2,
i.e. D ≤ 2(n−1) − d, which is implied by D ≤ n−1. For k > d the RHS is k(k−1) + (n−k)d, and the
strongest case is k = d+1, reading D ≤ d(d+1) + (n−d−1)d = d(n−d). Hence, besides parity and
D ≤ n−1, the only content is D ≤ d(n−d). (Sufficiency is the Erdős–Gallai theorem.) ∎

*Analytic conclusion.* Applying Lemma A to the four residue classes with the constant d above
(n ≡ 6, 0, 2, 3 (mod 7); D = d + c/2 = (4n+4)/7, (5n+7)/7, (3n+1)/7, (6n+10)/7), the conditions
hold for every admissible n: for n ≡ 6 (d = 2) both D ≤ n−1 and D ≤ 2(n−2) hold for all n ≥ 6;
for n ≡ 0 (d = 3) D ≤ 3(n−3) always and D ≤ n−1 for n ≥ 7; for n ≡ 2 (d = 1) both hold for all
n ≥ 9; for n ≡ 3 (d = 4) D ≤ 4(n−4) always and D ≤ n−1 for n ≥ 17. Parity: (n−1)d + D equals
(18m+14), (26m−2), (10m+2), (34m+12) respectively for n = 7m+r, all even. Hence the
complement-of-edges family covers n ≡ 6 (mod 7) from n ≥ 6, n ≡ 0 from n ≥ 7, n ≡ 2 from n ≥ 9,
and n ≡ 3 from n ≥ 17 — with no computational verification. (The value n = 10, the only n ≡ 3
with 6 ≤ n < 17, is covered by Corollary 16.)

**Corollary 9 (new infinite families).** All admissible n in the following four residue classes are
realized by complement-of-edges constructions:
  n ≡ 6 (mod 7), d = 2; n ≡ 0 (mod 7), d = 3; n ≡ 2 (mod 7), d = 1; n ≡ 3 (mod 7), d = 4.
Each construction is a complement-of-edges game whose graph is "a star centered at the special player
plus a structured graph"; explicit graphs for n = 20, 21, 23, 24 etc. were built and independently
re-checked by both the swing formula and (for small n) exhaustive enumeration. The
complement-of-edges family therefore covers **4/7 of all integers**, far beyond the two residue
classes of the main text.

Uncovered residue classes: n ≡ 1, 4, 5 (mod 7) (n = 18, 19, 22, 25, 26, … in the main text).

### Necessary property: all (n−1)-sets are winning

**Proposition 10 (necessary; computational verification + proof sketch).** If the Banzhaf index of a
simple game v equals ψⁿ, then every (n−1)-element coalition is winning.

*Verification*: exhaustive enumeration of all 7,828,354 simple games on 6 voters (all 360 solutions
satisfy it); for n = 7, 8 the MILP becomes infeasible when the constraint "some (n−1)-set is losing"
is added.

*Proof sketch*: if N\{x} is losing, player x swings on S = N\{x}; moreover, on each (n−2)-set
S = N\{x,j}, player x may swing (because N\{j} is winning) while player j never does (because N\{x}
is losing), so x accumulates extra swings at the top levels, contradicting β ∝ (2,…,2,1). A complete
proof needs a level-by-level count; left as an unfinished proof in the work record.

*Use*: it shrinks the search space to games in which all (n−1)-sets win (adopted in Task F).

### A unified framework: the W-family

**Proposition 11 (unifying theorem).** For a graph G and a family F of triples with
Pairs(F) ⊆ G (monotonicity), define
  v(G,F)(S) = 1  ⟺  |S| ≥ n−1,  or  (|S| = n−2 and N\S ∈ G),  or  (|S| = n−3 and N\S ∈ F).
Then v(G,F) is a simple game and
  β_i(v(G,F)) = |G| + (n−1) + |F| − 2·deg_G(i) − 2·r_i + e_i,      (U)
where r_i = |{X ∈ F : i ∈ X}| and e_i = |{X ∈ F : i ∈ X, X\{i} ∉ G}|.

- With G = E and F = ∅, (U) reduces to Theorem 1 (complement-of-edges);
- With G = complement(E) and arbitrary F, (U) reduces to Theorem 2 (threshold-with-exceptions).

*Verification*: for n = 6..10, (U) agrees with direct swing counts on random monotone (G,F)
instances. This unification shows that the two construction families belong to one parametric
framework, and provides a single equation for finding new constructions.

### Proposition 12 (Task F: an O(n³)-variable MILP over the W-family; verification extended to n ≥ 18)

The general MILP of Section 7 has 2ⁿ variables and becomes infeasible around n = 18. Using
Proposition 11's W-family, we compress the search to variables x_e (edge e ∈ G, C(n,2) of them) and
y_T (triple T ∈ F, C(n,3) of them), with the bilinear terms z = y·x linearized in the standard way,
yielding a MILP with **O(n³) variables** (formula (U) and monotonicity Pairs(F) ⊆ G as linear
constraints). This MILP solves all instances up to n ≤ 64 in seconds to minutes; every resulting
construction is an explicit closed form (Corollaries 14–17, Proposition 13), re-verified by formula
(U). The scales c are:

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}llll@{}}
\toprule\noalign{}
n & n mod 7 & c & construction \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
18 & 4 & 24 & deg+r=D \\
19 & 5 & 22 & tri(D3,f4,q2) \\
20 & 6 & 20 & comp-edge \\
21 & 0 & 26 & comp-edge \\
22 & 1 & 26 & tri(D3,f5,q3) \\
23 & 2 & 18 & comp-edge \\
24 & 3 & 36 & comp-edge \\
\end{longtable}}

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}llll@{}}
\toprule\noalign{}
n & n mod 7 & c & construction \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
25 & 4 & 30 & tri(D3,f6,q3) \\
26 & 5 & 32 & tri(D3,f4,q2) \\
27 & 6 & 28 & comp-edge \\
28 & 0 & 36 & comp-edge \\
29 & 1 & 36 & tri(D3,f5,q2) \\
30 & 2 & 24 & comp-edge \\
31 & 3 & 48 & comp-edge \\
\end{longtable}}

Here `tri(D,f,q)` and `comp-edge` are as in Proposition 13 / Section 10.1.

Then n = 32 (≡4) c=40, n=33 (≡5) c=42, n=34 (≡6) c=36, n=35 (≡0) c=46, n=36 (≡1) c=46; n=37 (≡2)
c=30 and n=38 (≡3) c=60 by complement-of-edges; n=39 (≡4) c=50. Further: 40(≡5) c=52,
43(≡1) c=56, 46(≡4) c=60, 47(≡5) c=62, 50(≡1) c=66, 53(≡4) c=70, 54(≡5) c=72, 57(≡1) c=76,
60(≡4) c=80, 61(≡5) c=82, 64(≡1) c=86, all rechecked by (U).

**Closed forms cover every n ≥ 67 (supplement to Proposition 12).** Corollary 15 shows that for
n ≥ 67 the special player need not participate in any F-triple (q = 0). Applying the triangle
construction directly yields the remaining values: n = 67 (≡4) c = 90, n = 68 (≡5) c = 92,
n = 71 (≡1) c = 96, n = 74 (≡4) c = 100, n = 75 (≡5) c = 102, n = 78 (≡1) c = 106, with
|G| = 123, |F| = 5 at n = 71 and |G| = 136, |F| = 5 at n = 78. **Hence every n with 6 ≤ n ≤ 80 is
covered without gaps, for all residue classes mod 7** (verified: 75/75 values in [6,80]). The
structural insight for the hard residues is that their solutions use few exceptional triples: the
triangle construction needs at most six (|F| ∈ {4, 5, 6}), and for n ≥ 67 none of them involves the
special player. For n ≥ 81 the O(n³) model exhausts memory around n ≈ 80, recorded as the second
computational lower bound of this method.

*Methodological remark*: the speed of the W-family MILP/CP-SAT (n = 18 in about 5 s) shows that the
unified framework of Proposition 11 not only unifies the constructions but also gives a scalable
computational route; this is a direct payoff of Tasks C/E.

### Closed-form constructions for the hard residue classes; full resolution

**Proposition 13 (found by exploration, verified via the proven formula (U)).** For each of the
three residue classes n ≡ 1, 4, 5 (mod 7), there is an explicit closed-form construction realizing
ψⁿ, valid for all n from a small threshold:

| residue | f | c | special degree s | valid for |
|--------|----|------------|-----------------|--------------------|
| n ≡ 1 | 5 | (10(n−1)−28)/7 | (c+6)/2 − q | n ≥ 22 |
| n ≡ 4 | 6 | (10(n−1)−30)/7 for n ≥ 25 (D = 3); c = 24 at n = 18 (D = 4) | D + c/2 − q | n ≥ 18 (D = 4 at n = 18, else D = 3) |
| n ≡ 5 | 4 | (10(n−1)−26)/7 | (c+6)/2 − q | n ≥ 19 |

Here q ∈ {0,…,f} is the number of *special triples* — F-triples containing the special player
(equal to the number of triples in which the special player participates). The construction takes
f disjoint triangles: q of them of the form {n, a, b} (special triple) and p = f − q of them
involving only non-special players; every player in a triangle has degree 2 in G (base degree D = 3,
so each triangle player has degree D−1 = 2) and lies in exactly one F-triple (r_i = 1, e_i = 0). The
remaining n−1−3f+q non-special players have degree D = 3 and r_i = 0; the special player has degree
s = D + c/2 − q (for D = 3 this is (c+6)/2 − q). By formula (U) the swing counts are
  β_i = |G| + (n−1) + f − 6 = 2c (non-special),   β_n = |G| + (n−1) + f − 2s − 2q = c.
The smallest feasible q admits the closed form
  q = max(0, ⌈(K − n)/14⌉),   K = 57 (n ≡ 1), 67 (n ≡ 4), 47 (n ≡ 5).      (6)
Indeed, writing δ = 2, 1, 3 for n ≡ 1, 4, 5 respectively, direct substitution (D = 3,
c = (10(n−1)−A)/7 with A = 28, 30, 26) gives the special degree s = (5n+δ)/7 − q and the
residual degree sequence (3^a, 2^x) on the m = n−1−3f+q non-triangle players, where x = s − 2q
and a = m − x = (2(n−K) + 28q)/7. Since n ≡ K (mod 7), a is **always even**. The feasibility
conditions x ≥ 0, a ≥ 0, a ≤ (m+1)/2, q ≤ f, m ≥ 4, s ≤ n−1 all hold at (6): x ≥ 0 ⟺
q ≤ (5n+δ)/21 and a ≤ (m+1)/2 ⟺ 49q ≤ 3n + 4K − 21f are the binding ones, each holding for
every n ≥ n₀ once the elementary inequalities are checked (e.g. n ≥ (3K+42−2δ)/13 < n₀ for
x ≥ 0; n ≥ (3.5K+49−(4K−21f))/6.5 < n₀ for the chord condition); a ≥ 0 is built into (6),
q ≤ f and s ≤ n−1 are automatic. The residual graph (3^a, 2^x) is then constructed
explicitly: place the a degree-3 vertices at the even positions 0, 2, …, 2a−2, add the cycle
(0 1 … m−1 0), and add the matching chords (2j, 2j+2) for j = 0, 2, …, a−2. Each even-position
vertex is the endpoint of exactly one chord, so it has degree 3; all other vertices have
degree 2. (a ≤ (m+1)/2 ⟺ 2a−2 ≤ m−1 makes the positions exist; a even closes the chord set.)
Thus (6) realizes ψⁿ for every n ≡ 1, 4, 5 (mod 7) with n ≥ 22, 25, 19 respectively, with no
search and no reliance on numerical verification.


**Corollary 14 (every n ≥ 18 has a closed form).** Since n ≡ 0, 2, 3, 6 (mod 7) are covered by
the complement-of-edges construction of Proposition 8 (by Lemma A, analytically for every
admissible n) and n ≡ 1, 4, 5 by the general triangle construction of Proposition 13 (by the
closed form (6), analytically for n ≥ 22, 25, 19 respectively), **every n ≥ 18 admits an
explicit closed-form simple game with Bz(v) = ψⁿ**. For n = 18 this uses base degree D = 4 with
six disjoint triangles, three of which contain the special player: c = 24, |G| = 33, |F| = 6.

**Corollary 15 (unified parametric family).** With base degree d = 3 for all non-special players and
f = the smallest non-negative integer with f ≡ 5(n mod 7) (mod 7), the same construction realizes ψⁿ
for every residue class; for n ≥ 67 the special player need not participate in any F-triple, and for
smaller n a suitable number q of special triples is used. Thus a single parametric family (the
W-family of Proposition 11 with the degree/f-triple data above) covers all n.

**Corollary 16 (closed forms for the five remaining small values).** For n = 8, 10, 11, 12, 15
explicit closed-form constructions are also found (via the same deg_G + r_i = D structure, with the
data below; verified by formula (U)):

| n | n mod 7 | c | \|G\| | \|F\| | D = deg+r (non-special) |
|---|---------|----|----|----|---------------------------|
| 8 | 1 | 8 | 15 | 2 | 4 |
| 10 | 3 | 10 | 16 | 1 | 3 |
| 11 | 4 | 14 | 22 | 6 | 5 |
| 12 | 5 | 16 | 25 | 6 | 5 |
| 15 | 1 | 20 | 32 | 2 | 4 |

Each is a W-family game v(G,F) with all swing counts ∝ (2,…,2,1) and Pairs(F) ⊆ G (monotone),
so Bz(v) = ψⁿ.

**Corollary 17 (full resolution — analytic).** Combining Corollary 14 (analytic, via Lemma A
and (6)) with Corollary 16, **every n ≥ 6 admits an explicit closed-form simple game with
Bz(v) = ψⁿ.** The proof is fully analytic: for n ≡ 0, 2, 3, 6 (mod 7) the complement-of-edges
construction of Proposition 8 realizes ψⁿ for every admissible n (Lemma A: the two-value
Erdős–Gallai conditions hold for all n in the residue class), and for n ≡ 1, 4, 5 (mod 7) the
triangle construction of Proposition 13 with the closed form (6) realizes ψⁿ for every
n ≥ 22, 25, 19 respectively; the finitely many remaining values 6 ≤ n ≤ 21 are the explicit
games of Corollary 16 (n = 8, 10, 11, 12, 15) and of Proposition 8 (n = 6, 7, 9, 13, 14, 16, 17),
with n = 18 the D = 4 variant of Corollary 14. Kurz's Conjecture 16 is therefore fully resolved
with explicit constructions for all n, with no reliance on computer search for existence.


### Verification of the core theorems (independent re-check)

The three central claims were re-verified independently of their original derivations:

**(a) The W-family swing formula (U), Proposition 11.** The identity
  β_i(v(G,F)) = |G| + (n−1) + |F| − 2·deg_G(i) − 2·r_i + e_i
was checked against direct swing enumeration on 440 randomly generated monotone instances
(Pairs(F) ⊆ G, n = 4..14): **0 mismatches**. The two special cases were checked separately —
Theorem 1 (F = ∅, 199 random instances) and Theorem 2 (G = complement(E), 29 instances) —
also with **0 mismatches**.

**(b) The closed-form constructions of Proposition 13 (analytic by Lemma A and (6)).** As an
independent confirmation of the analytic proof, the triangle-with-special-triples construction
was generated and its swing counts verified via (U) for every n ∈ [6, 50] with n ≡ 1, 4, 5
(mod 7) and n ≥ 18, and for the complement-of-edges constructions for the other residue classes:
**all verified** (the five values 8, 10, 11, 12, 15 are covered by the deg_G + r_i = D
constructions of Corollary 16, also verified). The Erdős–Gallai conditions of Lemma A and the
feasibility inequalities of (6) were additionally checked by direct computation for all n up to
10⁶ — agreeing with the analytic conclusion.

**(c) The necessary property of Proposition 10.** Exhaustive enumeration for n = 6 (all 360
solutions) and infeasibility of the MILP with a "losing (n−1)-set" constraint for n = 7, 8
confirm that all (n−1)-sets are winning in any game with Bz(v) = ψⁿ.

All verification scripts are included in the reproducible code package.

### Current coverage table

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}lll@{}}
\toprule\noalign{}
n & method & c \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
6 & compl & 4 \\
7 & compl & 6 \\
8 & deg+r & 8 \\
9 & compl & 6 \\
10 & deg+r & 10 \\
11 & deg+r & 14 \\
12 & deg+r & 16 \\
13 & compl & 12 \\
14 & compl & 16 \\
15 & deg+r & 20 \\
16 & compl & 12 \\
17 & compl & 24 \\
\end{longtable}}

(18–75 see the tables in Proposition 12.) n ≡ 0, 2, 3, 6 (mod 7) are covered for infinitely many n
by Proposition 8; n ≡ 1, 4, 5 (mod 7) are covered by the triangle construction of Proposition 13
and by Corollary 16 for the smallest values. **Every n ≥ 6 has a closed-form construction.**
Full explicit (G, F) data for 6 ≤ n ≤ 80 are provided in machine-readable form in
appendix-data-`n80.json`; entries for 41 ≤ n ≤ 80 are produced by the closed-form constructions of
Proposition 8 (n ≡ 0, 2, 3, 6 (mod 7)) and Proposition 13 (n ≡ 1, 4, 5 (mod 7)), and every entry
(6 ≤ n ≤ 80) is re-verified by direct enumeration of the swing counts — equal to ψⁿ, i.e.
(2c,…,2c,c) — and of the monotonicity condition Pairs(F) ⊆ G.

### Open problems

1. Can Proposition 10 (all (n−1)-sets winning) be proved rigorously?
2. Is c necessarily even?
3. What is the minimal c for each n? (Certified by the CP-SAT model of Section 7:
   n=6: 4, n=7: 6, n=8: 8, n=9: 6, n=10: 10.) For n = 8 the previously open "7 or 8" gap is
   closed: the infeasibility of every smaller even scale c ∈ {2, 4, 6} is certified, and c = 8 is
   realized (Table 2); likewise n = 9 (c ∈ {2, 4} infeasible, c = 6 realized) and n = 10
   (c ∈ {2, 4, 6, 8} infeasible, c = 10 realized). Note that c is even (Corollary 5), so the odd
   candidate c = 7 is already excluded; the certified values are conclusive because CP-SAT proves
   infeasibility exactly.
4. Is there a single uniform construction that realizes ψⁿ for all n with no case distinction?
   The current resolution uses residue-specific parameters within one framework (Corollary 15).
5. *(Weighted case, Conjecture 15.)* Can the certified infeasibility of the exact target
   (2c,…,2c,c) for 6 ≤ n ≤ 10 (Section 9) be turned into an analytic proof for all n? In particular,
   the quantitative form asks for a universal c > 0 with ‖Bz(v) − ψⁿ‖₁ ≥ c/n for every weighted
   majority game v. The certified optimal distances 5/44, 0.085470, 0.066667 (n = 6, 7, 8) give the
   empirical constant c ≤ 0.533; an analytic argument with c = Θ(1) would settle the conjecture.

## 12. Application: an exact computational case study

We close with a concrete case study applying the two engines of Sections 10.1–10.3 to a real voting
body: the weighted voting rules of the Council of the European Union (EU) and its predecessors.
Every claim below is tagged with its epistemic status — **certified** (deterministic computation at a
conclusive weight bound), **exact** (closed form / subset enumeration), or **contextual** (institutional
background, not a theorem of this paper).

### 12.1 Actual Banzhaf power of historical EU Council bodies

The original European Economic Community (EEC) Council (Treaty of Rome, 1958) and its first enlargements
were weighted majority games on n = 6, 9, 10 voters — exactly the certified range of Section 9.
Their official qualified-majority weights and quotas (Felsenthal & Machover 1998, who tabulate the EU
Council history; the accession treaties) and the exact Banzhaf power distributions are:

| body | n | weights w | quota q | L₁ to ψⁿ |
|---|---|---|---|---|
| EEC-6 (1958–1973) | 6 | (4×3, 2×2, 1) | 12 | 26/77 ≈ 0.338 |
| EEC-9 (1973–1981) | 9 | (10×4, 5×2, 3×2, 2) | 41 | 2136/5389 ≈ 0.396 |
| EEC-10 (1981–1986) | 10 | (10×4, 5×3, 3×2, 2) | 45 | 2528/6023 ≈ 0.420 |
| EEC-12 (1986–1995) † | 12 | (10×4, 8, 5×4, 3×2, 2) | 54 | 878/2323 ≈ 0.378 |
| EU-15 (1995–2004) † | 15 | (10×4, 8, 5×4, 4×3, 3×2, 2) | 62 | 98402/255867 ≈ 0.385 |

*Weights are in compact multiplicity form: e.g. 10×4 means four members of weight 10, a bare value means multiplicity one. The exact Banzhaf swing-count vectors β and the derived power distributions (percentages of total swings), in the same notation, are: EEC-6 β = (10×3, 6×2, 0), power = (23.8×3, 14.3×2, 0)%; EEC-9 β = (53×4, 29×2, 21×2, 5), power = (16.7×4, 9.2×2, 6.6×2, 1.6)%; EEC-10 β = (100×4, 52×3, 26×3), power = (15.8×4, 8.2×3, 4.1×3)%; EEC-12 β = (286×4, 242, 148×4, 102×2, 40), power = (12.9×4, 10.9, 6.7×4, 4.6×2, 1.8)%; EU-15 β = (1968×4, 1606, 1028×4, 806×3, 616×2, 406), power = (11.2×4, 9.1, 5.8×4, 4.6×3, 3.5×2, 2.3)%.*

† *Beyond the certified range* (n ≥ 11): exact infeasibility is not certified for these bodies (Tier-3
runs are heuristic, Section 9); the power distributions and L₁ values are exact computations reported
as scaling context only, carrying no certificate.

Here L₁ is the distance to ψⁿ minimized over which member occupies the half-power position of the
egalitarian-with-one-exception target. Three observations:

- **EEC-6 has a null player.** Luxembourg (weight 1, quota 12 of total 17) has zero swings: no
  coalition of the remaining five members sums to weight 11, so Luxembourg's vote is never decisive.
  Its power is 0, while the three large members (Germany, France, Italy) jointly hold 71.4% of all
  power. This is a known pathology of the original weighted Council, reproduced here exactly.
- **Real power is far from egalitarian.** The three bodies sit at L₁-distance 0.338–0.420 from ψⁿ,
  and the power spread (largest/smallest positive power) ranges from 3.85× (EEC-10) to 10.6× (EEC-9).
- **All three lie in the certified range** (n = 6, 9, 10), so the obstruction of Section 9 applies to
  them directly (exact infeasibility; the distance values above are exact subset-enumeration
  computations, reproduced by `case_study_eu.py` in the companion package).

### 12.2 What the certified machinery tells a designer

For each body with n ≤ 10, Section 9 certifies — deterministically, at the conclusive weight bound
wᵢ ≤ 2^(n−1) — that **no weighted majority game on n voters realizes ψⁿ exactly**. The decision-support
consequences for an institutional designer are:

1. **Certified infeasibility of the target.** No re-weighting of these councils — indeed no weighted
   rule on ≤ 10 voters at all — can attain the egalitarian target ψⁿ. A designer who insists on a
   weighted rule must accept a strictly positive distance to ψⁿ.
2. **Certified best achievable (n ≤ 8).** Section 10.3 computes the exact minimal L₁-distance over
   all weighted games: 5/44 ≈ 0.114 for n = 6 (attained at weights (3,1,3,3,3,1), quota 11, and
   verified against exhaustive enumeration of all 1,111 weighted games), 0.0855 for n = 7, and
   0.0667 for n = 8, each certified as a global optimum over the full total-swing range. The actual
   EEC-6 rule sits at L₁ = 26/77 ≈ 0.338 — so even within the weighted class, a redesign could
   improve the distance to ψ⁶ by a factor of about three.
3. **Boundary of certification.** For n ≥ 11 the exact infeasibility is not certified (Tier 3 runs
   are heuristic; Section 9). The later EEC-12 (n = 12) and EU-15 (n = 15) bodies lie beyond the
   certified range; their exact power distributions in Section 12.1 are reported as scaling context
   only, and their distance values carry no certificate.

### 12.3 The design decision and institutional context

The obstruction of Section 9 is a structural statement about the weighted class: egalitarian power is
unattainable for n ≤ 10, and the real EU bodies are far from it. This is consistent with the actual
trajectory of the institution — **contextual** — the Council moved away from a single weighted quota
in the Lisbon Treaty, adopting a double-majority rule (at least 55% of member states representing at
least 65% of the population) that cannot be represented as one weighted majority game. The certified
obstruction supplies the formal decision-support complement to that historical choice: it quantifies
how far weighted rules can be from an egalitarian target, certifies that they cannot reach it for
small bodies, and — via Section 10.3 — returns the exact best weighted approximation when the designer
insists on staying in the weighted class.

### 12.4 A prescriptive design-analysis procedure

For a designer facing a target ψ on an n-voter body, the two engines of Section 10 compose into a
decision-support procedure:

- if n ≤ 10 and ψ = ψⁿ, the Section 9 obstruction certifies the decision (infeasible in the weighted
  class; feasible by explicit construction in the general class, Section 5);
- if n ≤ 8 and ψ = ψⁿ, the Section 10.3 optimizer returns the certified best weighted approximation
  and its distance;
- otherwise the same solvers run under a time budget, and the outcome is labelled heuristic
  (Tier 3), not a certificate.

All numbers in this section are exact computations reproduced by `case_study_eu.py` in the companion
code package.

## 13. Conclusion

We complement the construction half with a negative result in the *weighted* universe (Section 9):
the egalitarian target ψⁿ cannot be reproduced by any weighted majority game. The obstruction is
anchored in a classical swap/block identity (Proposition 4) for swing-count differences in weighted
majority games, which forces the distinguished player to carry minimal weight and concentrates every
other player's deviation into a rigid subset-sum window; the sharp mirror form (M′) of those windows
— a new rigidity consequence of the classical swap/block identity — is our central structural
contribution. Deterministic CP-SAT, at the conclusive weight bound wᵢ ≤ 2^(n−1), certifies
infeasibility for n = 6, 7, 8, 9 and 10 (n = 6 consistent with the exhaustive enumeration of all
1,111 weighted games, whose optimal L₁-distance to ψ⁶ is 5/44). We stress the distinction between
proof and certification: the infeasibility of the exact target is a certified computation for
6 ≤ n ≤ 10, not an analytic proof for all n, and likewise the quantitative form of Conjecture 15 —
the universal bound ‖Bz(v) − ψⁿ‖₁ ≥ c/n — is certified for n = 6, 7, 8 (optimal L₁ distances 5/44,
0.085470, 0.066667, giving c ≤ 0.533), while the Θ(1/n) asymptotics for all n remains a conjecture
supported by these certified values. The two-tier generalization ψⁿ(3,1) is shown to be realizable by
a *uniform* construction for all n ≥ 6, while ψⁿ(k,1) is obstructed for k ≥ 4. This gives a complete
picture of the two Kurz conjectures: Conjecture 16 holds by explicit construction, and Conjecture 15
holds *computationally* for n ≤ 10, with the structural mechanism (M′) explaining why — an analytic
proof for all n remains open.

As an operations-research contribution, the paper offers a reusable, two-sided methodology rather
than a one-off verification: a construction engine (Section 10.1) that is closed-form for every
n ≥ 6 and computationally verified for every 6 ≤ n ≤ 80, and an exact verification engine
(Section 10.2) that certifies non-existence at a conclusive weight bound, with the structural
property (M′) as its pruning engine. Both halves are fully reproducible from the companion code
package, and both are explicit about their limits: the constructions cover every n ≥ 6, while the
weighted obstruction is certified for n ≤ 10 and the quantitative constant c ≤ 0.533 is certified
for n ≤ 8 only. The Section 12 case study grounds this methodology in a concrete institution — the
weighted Council of the European Union — turning the abstract inverse-optimization problem into
prescriptive decision support for the design of voting rules.

## Appendix. Additional explorations and negative results

The material in this appendix is kept for reproducibility and completeness; none of it is needed
for the main results. It documents numerical observations and constructions that were explored and
either remain open or did not realize the target.

**Observation 7 (numerical).** In all known solutions the scaling factor c is even
(c ∈ {4, 6, 8, 10, 12, 14, 16, 22, 24, …}). Whether this is forced is open. (In the weighted case
Corollary 5 resolves it: c must be even in any weighted realization.)

**Observation 9 (hidden structure of MILP solutions).** The MILP solutions for n = 8, 10, 11, 12, 15
(Section 7) all belong to the W-family (all (n−1)-sets win). Their threshold parameters (G, F)
share: the special player has low degree in G (1–3) and appears in most F-triples; the graph G is
connected. These reflect the solver's specific choices and show no complete symmetry/cyclic
structure, indicating that these n are "essentially mixed" and indeed cannot be covered by the
complement-of-edges family (Proposition 8) or any single uniform family — consistent with the
arithmetic description of Proposition 8. (Superseded for n ≡ 1, 4, 5 (mod 7) — including n = 8,
11, 12, 15 above — by the parametric triangle family of Corollary 15, which covers those residue
classes at every n by varying q; n = 10 (n ≡ 3 (mod 7)) remains outside that family.)

**Unsuccessful constructions and negative results.**

1. **"Core-set" construction**: v(S)=1 ⟺ |S|≥n−1 or (|S|≥n−3 and C⊆S) for a fixed core C.
   For n = 6..10 no |C| yields ∝(2,…,2,1). Reason: the core makes swings too symmetric.
2. **Random sampling of the threshold (E,F) family**: for n = 8 (known solvable), 4×10⁶ monotone
   random (E,F) samples gave zero hits — the density of threshold-family solutions is essentially
   zero, so random search is hopeless and MILP is necessary. Recorded as a search lower bound.
3. **F = all triples containing the special player**: makes the special player a null player
   (β_n = 0), so it does not realize ψⁿ.
4. **E = K_{n−1} minus a regular graph**: makes β_n ≡ 0, so it does not realize ψⁿ.
5. **Complement-of-edges at n = 18**: n ≡ 4 (mod 7), no integer (d,c) by Proposition 8. Confirmed.
6. **Closed-form parametric family for n ≡ 1, 4, 5 (mod 7)**: CP-SAT was used to extract the full
   (G, F) solutions for n = 22, 25, 26, 43. These solutions are highly ad-hoc: the special player's
   E-degree ranges from low (small n) to almost n−2 (n = 43: degree 42), |F| ranges from 4 to 299,
   and the c values are not unique across solvers (n = 43: HiGHS finds c = 56, CP-SAT c = 362, since
   c may be any multiple). **No clean parametric family could be extracted from these solutions**;
   this explains why these residue classes resist closed-form treatment (negative result, recorded).
   (Superseded: for n ≡ 1, 4, 5 (mod 7), Proposition 13 and Corollary 15 now derive the exact
   closed-form family from the deterministic certificates, so this negative conclusion no longer
   holds; the solver-dependence of the extracted c values observed here (n = 43: c = 56 vs 362) is
   explained there by the fact that c may be any multiple of the minimal feasible value.)

## Declarations

**Declaration of competing interest.** The authors declare that they have no known competing financial
interests or personal relationships that could have appeared to influence the work reported in this
paper.

**Funding.** This work was supported by the National Social Science Fund of China under Grant No.
25CSH113.

**Data availability.** All results reported in this paper are reproducible from the companion code
package (CP-SAT/HiGHS models, instance tables, and recorded runtimes), publicly available at

https://github.com/chenyongjingg/banzhaf-inverse-power

**CRediT authorship contribution statement.** Yongjin
Chen: Conceptualization, Methodology, Investigation, Writing — original draft. Shi Jin: Formal
analysis, Software, Data curation, Writing — review & editing. Songze Zhu: Conceptualization,
Supervision, Writing — review & editing, Funding acquisition.

**Declaration of generative AI and AI-assisted technologies in the writing process.** During the
preparation of this work the authors used Claude (Anthropic) as an AI writing assistant to assist
with language editing, typesetting, and formatting of the manuscript. After using this tool, the
authors reviewed and edited the content as needed and take full responsibility for the content of
the publication.

## References

- Alon, N., & Edelman, P. H. (2010). The inverse Banzhaf problem. *Social Choice and Welfare*,
  34(3), 371–377.
- Chow, C. K. (1961). On the characterization of threshold functions. In *Proceedings of the 2nd
  Annual Symposium on Switching Circuit Theory and Logical Design (SWCT 1961)* (pp. 34–38). IEEE.
  <https://doi.org/10.1109/FOCS.1961.24>
- de Keijzer, B., Klos, T., & Zhang, Y. (2014). Finding optimal solutions for voting game design
  problems. *Journal of Artificial Intelligence Research*, 50, 105–140. <https://doi.org/10.1613/jair.4109>
- Dubey, P., & Shapley, L. S. (1979). Mathematical properties of the Banzhaf power index.
  *Mathematics of Operations Research*, 4(2), 99–131.
- Felsenthal, D. S., & Machover, M. (1998). *The measurement of voting power: Theory and practice,
  problems and paradoxes*. Edward Elgar.
- Kurz, S. (2015). Ready for the design of voting rules? *Homo Oeconomicus*, 32(1), 117–129.
  (Preprint: arXiv:1405.0823).
- Kurz, S. (2016). The inverse problem for power distributions in committees. *Social Choice and
  Welfare*, 47(1), 65–88. <https://doi.org/10.1007/s00355-015-0946-8>
- Kurz, S., & Napel, S. (2014). Heuristic and exact solutions to the inverse power index problem
  for small voting bodies. *Annals of Operations Research*, 215(1), 137–163.
- Matsui, Y., & Matsui, T. (2001). NP-completeness for calculating power indices of weighted
  majority games. *Theoretical Computer Science*, 263(1–2), 305–310. <https://doi.org/10.1016/S0304-3975(00)00251-6>
- Muroga, S. (1971). *Threshold logic and its applications*. Wiley.
- Nurmi, H. (1982). The problem of the right distribution of voting power. In M. J. Holler (Ed.),
  *Power, Voting, and Voting Power* (pp. 203–212). Physica-Verlag (Springer).
- Penrose, L. S. (1946). The elementary statistics of majority voting. *Journal of the Royal
  Statistical Society*, 109(1), 53–57.
- Taylor, A. D., & Zwicker, W. S. (1999). *Simple games: Desirability relations, trading,
  pseudoweightings*. Princeton University Press.
