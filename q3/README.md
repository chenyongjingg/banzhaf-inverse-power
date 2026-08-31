# Companion code — Section 9 (The weighted case)

This directory contains the scripts that reproduce every numerical claim of
Section 9 of the manuscript ("The weighted case": exact infeasibility of the
egalitarian target over weighted majority games, and certified optimal
weighted approximations). Each result below is produced by the script named in
parentheses and re-checked independently where noted.

## Verified results

### Exact infeasibility of the target ψⁿ over weighted majority games

The target ψⁿ = (2,…,2,1)/(2n−1) is not realizable by any weighted majority
game on n voters for every 6 ≤ n ≤ 10. The certificate is conclusive because
the search is run up to the classical weight bound W = 2^(n−1)
(`conj15_feas.py` standard model; `conj15_feas2.py` enhanced model that adds
the (M′) mirror constraints — the enhanced model is required for n = 9, 10):

| n | W      | model       | verdict      | runtime   |
|---|--------|-------------|--------------|-----------|
| 6 | 32     | standard    | infeasible   | 2.9 s     |
| 7 | 64     | standard    | infeasible   | 117 s     |
| 8 | 128    | standard    | infeasible   | 316 s     |
| 9 | 256    | enhanced    | infeasible   | 1562.9 s  |
| 10| 512    | enhanced    | infeasible   | 9527.4 s  |

For n = 6 the verdict is additionally confirmed by exhaustive enumeration of
all 1,111 inequivalent weighted majority games (`weighted_enum.py`; the count
agrees with Kurz & Napel 2014, Table 1).

### Certified optimal L1-approximation

For n = 6, 7, 8 the best weighted-majority approximation to ψⁿ is certified
globally (`conj15_l1.py`; n = 6 double-confirmed by exhaustive enumeration):

| n | optimal L1     | T  | n·L1   | witness profile        |
|---|----------------|----|--------|------------------------|
| 6 | 5/44 ≈ 0.113636| 32 | ≈ 0.682| (6,4,6,6,6,4), w=(3,1,3,3,3,1) |
| 7 | ≈ 0.085470     | 45 | ≈ 0.598| (5,7,7,7,7,7,5), w=(2,64,64,64,64,64,1) |
| 8 | ≈ 0.066667     | 60 | ≈ 0.533| (6,8,8,8,8,8,8,6), w=(2,3,3,3,3,3,3,1) |

The L1-optimal n = 6 profile realizes L1 = 5/44; the certified n = 7, 8 values
are the global optima over all weighted games at the conclusive weight bound.

## Script inventory

### Cited in Section 9

- `probe6_identity.py` — swing-count identity (keystone lemma): verifies
  η_i − η_j = 2·#{T ⊆ N∖{i,j} : q−w_i ≤ W(T) < q−w_j} over 12,000 random
  weighted games (n = 3…12, weights ≤ 30), 0 failures.
- `brute_mirror3.py` — sharp mirror statement (M′): 246,000 random power
  profiles, 0 violations.
- `brute_mirror4.py` — sharp mirror statement (M′) on real games: 228,000
  random weighted games with η_i = η_j, 0 violations.
- `conj15_feas.py` — CP-SAT infeasibility of ψⁿ over weighted majority games
  at W = 2^(n−1) (standard model).
- `conj15_feas2.py` — enhanced CP-SAT model with the (M′) mirror constraints;
  certifies n = 6,…,10.
- `conj15_l1.py` — exact optimal L1-approximation to ψⁿ (n = 6, 7, 8).
- `weighted_enum.py` — exhaustive enumeration of the 1,111 inequivalent
  weighted games on 6 voters.
- `probe4_twotier.py` — two-tier target ψⁿ(a,b): uniform (3,1) construction
  over n = 6,…,80.
- `probe5_k1_coverage.py` — coverage rates of the (k,1) families over
  n = 6,…,80.

### Supporting probes and checks

- `check_parity.py` — parity (evenness) of swing counts.
- `lp_check.py` — LP feasibility of scale-candidate instances.
- `min_c_sweep.py` — sweep for the minimal scale c of explicit constructions.
- `probe1_parity_ssi.py` — parity and structural checks on swing profiles.
- `probe2_weighted_gap.py` — gap-window structure of weighted games.
- `probe3_weighted_n6.py` — weighted-game probes on 6 voters.
- `verify_indicator.py` — independent verification of the feasibility check.
- `verify_n8_upper.py` — swing counts and L1 distance for the n = 8 witness.
- `conj15_l1_range.py` — L1-optimal computation over a range of total swing T.
- `l1_n9_status.py` — status probe for the n = 9 L1 computation.
- `export_wfamily.py` — export of the W-family constructions to the appendix
  data files.
- `wfamily_gen.py` — generator of W-family simple games (Erdős–Gallai /
  Havel–Hakimi degree constructions).

### Driver scripts

`run_*.sh` and `runner_*.sh` are command-line drivers for the individual
experiments above.

## Dependencies

Python 3, OR-Tools CP-SAT, HiGHS. All scripts are deterministic; run times are
as reported in the tables above.
