# Re-run logs — pre-submission re-verification

These are the raw logs of an independent re-run of the numerical claims on a
second machine, retained so that the numbers in `../README.md` are backed by a
log rather than by a summary. They are reproduced **verbatim**, including the
runs that went wrong.

Read the "Verdict" column before reading any single log. Two logs contain
alarming-looking lines (`mismatch 27443/27443`, `0 hits`) that do **not**
contradict the manuscript; the reason is recorded below and the superseding run
is in the same directory. Publishing the broken runs alongside the fixed ones is
deliberate: the instrument error they expose was found by their own positive
controls, and hiding it would make the evidence look cleaner than it is.

## Verdict table

| log | what it re-checked | verdict |
|---|---|---|
| `rerun_weighted_n6.log` | `weighted_enum.py 6 40`, then `probe3_weighted_n6.py` | **backs** the weighted n = 6 claims |
| `rerun_feas_n6_n8.log` | `conj15_feas.py` at n = 6, n = 8 | **backs** the infeasibility certificates |
| `recheck_n6_simple_games.log` | exhaustive enumeration of simple games at n = 6 | **superseded** (wrong target multiset) |
| `recheck_360.log` | same enumeration, corrected target | **backs** 360 solutions / 2 classes |
| `recheck_math_t1_u.log` | Theorem 1 and (U), first run | **superseded** (pre-correction `v_G`) |
| `recheck_t1_u.log` | Theorem 1 (n = 6 full, n = 7 sampled) + (U) | **(U) backs**; Theorem 1 **superseded** |
| `recheck_t1_fixed.log` | Theorem 1, corrected `v_G` | **backs** Theorem 1 |
| `recheck_t1_n7full.aborted.log` | n = 7 full, first attempt | provenance only (aborted) |
| `recheck_t1_n7full.log` | n = 7 full exhaustive, corrected `v_G` | **backs** Theorem 1 at n = 7 |

## What is backed

**Weighted n = 6 (`rerun_weighted_n6.log`).** Enumerating weight vectors with
cap 40 yields 7,947,963 vectors, which merge to 2,607 distinct labelled weighted
games, 2,606 of them valid (empty coalition losing), falling into **1,111**
isomorphism classes — the known value #W(6) (Kurz & Napel 2014, Table 1). The
best L₁ distance to ψⁿ is 0.1136363636 at swings [6, 6, 6, 6, 4, 4], total 32.
`probe3_weighted_n6.py` reproduces the same 1,111 classes and the same optimum
from an independent path.

**Infeasibility (`rerun_feas_n6_n8.log`).** n = 6 at W = 32: INFEASIBLE in
2.7 s. n = 8 at W = 128: INFEASIBLE in 1,781.4 s. Eight workers, no seed.

**(U) — Proposition 2 (`recheck_t1_u.log`).** The positive control fires
(corrupting the constant in (U) by +1 produces 1,024 mismatches in the n = 5
graph set), so the instrument has discriminating power; then the exhaustive
n = 5 sweep over all 1,024 × 1,024 = 1,048,576 pairs gives **0 mismatches**, and
random re-checks at n = 6..10 give **0 mismatches** each.

**Theorem 1, corrected (`recheck_t1_fixed.log`, `recheck_t1_n7full.log`).** With
the manuscript's `v_G` (see below): self-check on games with known answers
passes; two independent construction paths for the paper's n = 6 example
converge on the printed value [8, 8, 8, 8, 8, 4]; the positive control confirms
the check has discriminating power; then **n = 6 full (27,443 graphs) 0
mismatches**, **n = 7 full (1,887,277 graphs) 0 mismatches**, and a
closure-vs-lookup collision test over 20,000 graphs shows 0 disagreements.

## What is superseded, and why

Two independent instrument errors, both caught by the runs' own controls.

### 1. Theorem 1: the test used the pre-correction `v_G`

The manuscript defines `v_G` by (Section 5):

> a coalition is winning iff the voters outside it are contained in some edge of G

The first re-run instrument instead encoded the *dual* condition — a coalition
wins iff it meets every edge of G (a vertex cover). These are different games,
and Theorem 1 is stated for the former. Under the wrong one, the formula
β_i = |E| + (n−1) − 2·deg_G(i) fails on **every** graph:

- `recheck_math_t1_u.log`: n = 6, 27,443 / 27,443 mismatches; n = 7 full,
  1,887,277 / 1,887,277 mismatches.
- `recheck_t1_u.log`: n = 6 full and n = 7 sampled, likewise 100%.

A 100% mismatch rate is the signature of a misaligned instrument, not of a false
theorem: a genuine counterexample would be occasional, not universal. The clean
control is that the **same n = 7 domain of 1,887,277 graphs** gives 100%
mismatches under the old semantics and **0** under the corrected one.

`recheck_t1_dualsem.py` (here, self-contained) settles it independently: it
implements the closure semantics, re-derives the formula analytically, and
re-runs the whole n = 6 enumeration to **0 mismatches**, with a control that
fires on all 27,443 graphs when the formula's sign is corrupted. Run it with
`python recheck_t1_dualsem.py`.

### 2. The n = 6 simple-game target was the literal multiset

`recheck_n6_simple_games.log` searched for coalitions whose swing vector equals
{2, 2, 2, 2, 2, 1} literally and found **0**. The reachable swing vectors are
proportional to that multiset, not equal to it (the paper's example has
[8, 8, 8, 8, 8, 4]), so 0 is the correct answer to the wrong question.
`recheck_360.log` re-runs the enumeration on the proportional target and
reproduces the manuscript: Dedekind number M(6) = 7,828,354, simple games
7,828,352, **360** solutions, **2** isomorphism classes of sizes [180, 180].

That same log also carries an invalid helper: a bitwise `swings()` that
double-counts (it returns [2, 2, 10, 6] where the naive count gives
[1, 1, 5, 3]). Its own two positive controls reject it, which is why the log
prints `swings() invalid`, and two of that log's verdict lines are artefacts of
the helper. The enumeration in the same log is not invalidated by this: its
target is the multiset *up to a factor*, so the factor-2 scale does not change
which games are counted, and its own n = 3 control (20 antichains → 18 simple
games) passes independently of swing scaling. The printed sample vectors
([16, 16, 16, 16, 16, 8], i.e. the same 2× scale) are consistent with the
enumeration sharing that helper, which is why this point is recorded rather than
smoothed over.

## Runtimes

Retained here because the runtimes are part of the record: 2.7 s (n = 6,
weighted certification), 1,781.4 s (n = 8), 670.1 s and 807.1 s (n = 6 simple-game
enumeration), 4.1 s (n = 6 full, corrected Theorem 1), 329.3 s (n = 7 full,
corrected), 1,584.2 s (n = 7 full, first run), 430.8 s + 161.0 s (n = 5
exhaustive (U) + n = 7 sampling).

## Provenance

The audit instruments that produced these logs live in the manuscript's audit
tree, not in this repository; `recheck_t1_dualsem.py` is the one exception and is
self-contained. Logs were captured on 2026-09-21 and are unedited except for
this README.
