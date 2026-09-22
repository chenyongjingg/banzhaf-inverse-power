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

## Re-runs, 2026-09-22 — the counts and certificates the papers quote

The logs above were captured on 2026-09-21 and cover the mathematics. The set below was added
on 2026-09-22 to close a specific gap: the two manuscript files quote a number of *counts* and
*minimality certificates* for which no run output had been archived. Every one of them is
produced by a script that ships in this repository, so they were reproducible on demand; these
are the runs.

| log | what it re-runs | result |
|---|---|---|
| `rerun_uproof_n6_11.log` | formula (U) proof cases, n = 6…11, both with and without Pairs(F) ⊆ G imposed | **PASS, 2,040 player-instances**, each case matching its closed form |
| `rerun_uproof_n12_18.log` | the same, n = 12…18 | the 630 that complete the 2,670 total |
| `rerun_minc_8_{2,4,6}.log` | minimality sweep at n = 8 | **INFEASIBLE** 0.4 / 0.3 / 2.4 s |
| `rerun_minc_9_{2,4}.log` | minimality sweep at n = 9 | **INFEASIBLE** 0.5 / 0.6 s |
| `rerun_minc_10_{2,4,6,8}.log` | minimality sweep at n = 10 | **INFEASIBLE** 3.7 / 5.8 / 11.2 / 287.8 s |
| `rerun_minc_15_18.log` | the downward sweep the paper reports as unresolved under a 600 s budget | **UNKNOWN (timeout 600 s, 635.1 s)** — as printed |
| `rerun_minc_driver.log` | driver summary for the sweep above | one row per per-case log, regenerated from them (see below) |
| `rerun_runtimes_n6_n7.log` | the four standard/enhanced solver runtimes quoted in the MILP discussion | see the runtime note below |
| `rerun_feas_n6_n8.log` | (2026-09-21) standard n = 6 and n = 8 weighted certification | 2.7 s / 1,781.4 s |

`rerun_minc_*.log` and `rerun_runtimes_n6_n7.log` were produced by
`rerun_minc_20260922.sh` and by the command sequence recorded in the log headers. Nothing was
deleted or overwritten; the 2026-09-21 logs are still in place next to them.

One artefact to record rather than smooth over. The first `rerun_minc_driver.log` was written by
redirecting the script's stdout into the same directory the summary loop globs, so the loop
reached its own output file and read it half-written; its last line was `tail -1` of that partial
file, which happened to be the previous row's text prefixed with the driver's own name. The
per-case logs were never affected. The script now skips its own output by name and takes a
`--summary-only` flag, and the driver log in this directory was regenerated with

```
bash rerun_minc_20260922.sh --summary-only > recheck/rerun_minc_driver.log
```

from the ten per-case logs, unchanged and un-re-solved. So the driver log is a pure function of
the per-case logs: a reader can recompute it byte for byte with the command above, and if it ever
stops matching, the per-case logs are the authority. Checked: md5
`e96c04fa95085f2a1648d53befa1bc8c`, reproduced twice.

### The four runtimes, and why they disagree with the manuscript

These four cells are the one place a re-run does not return the printed value, and the reason is
the solver, not the record. `conj15_feas.py` / `conj15_feas2.py` run CP-SAT with 8 workers and
`seed None`, so wall-clock time is genuinely non-deterministic. The same command, same machine,
two days apart:

| row | printed in the paper | 2026-09-22 | 2026-09-21 |
|---|---|---|---|
| standard, n = 6, W = 32 | 2.9 s | 12.0 s | **2.7 s** |
| standard, n = 7, W = 128 | 117 s | 211.2 s | — |
| enhanced, n = 6, W = 32 | 2.5 s | 3.5 s | — |
| enhanced, n = 7, W = 128 | 19 s | 30.5 s | — |

What reproduces is the *comparison the paper draws*, not the individual seconds. The paper says
the enhanced model "gives a six-fold speedup at n = 7 (19 s vs 117 s) and a much smaller one at
n = 6 (2.5 s vs 2.9 s)":

| | printed ratio | re-run ratio |
|---|---|---|
| n = 7, standard ÷ enhanced | 117 / 19 = 6.2× | 211.2 / 30.5 = **6.9×** |
| n = 6, standard ÷ enhanced | 2.9 / 2.5 = 1.16× | 12.0 / 3.5 = **3.4×** |

The n = 7 six-fold is stable across two machines and two days, which is a stronger result than a
single timing would have been. At n = 6 the enhanced model is faster in every run on record
(2.5 < 2.9 printed; 2.5 < 2.7 on 2026-09-21; 3.5 < 12.0 here), so the direction is not in doubt;
what varies is the margin, from 1.16× to 3.4×. Both margins are, as the paper says, much smaller
than the six-fold at n = 7. The paper's own sentence therefore holds on the re-run.

The manuscript already says the frontier "is measured, not proved" and that the numbers come
from one machine; this table is the evidence for that sentence. A reader who wants the ranking
should read the ratios above; a reader who wants the seconds should read the spread, not a row.
