# Two-level Banzhaf profiles (Brief Report)

Scripts supporting the note *Two-Level Banzhaf Profiles Are Unattainable by
Weighted Majority Games: An Exact Classification for Every Number of Voters*.

| Script | What it reproduces |
|---|---|
| `check_swing_identity.py` | Lemma 1 (swing-difference identity, 42,836 pairs) and Lemma 2 (equal swing counts force interchangeability, 133,178 pairs) over seeded random weighted games |
| `check_counting_lemma.py` | Lemma 3, exhaustively for every simple game symmetric in n-1 voters, 2 <= n <= 9 |
| `two_level_image.py` | The exact set of attainable ratios `eta/c` for n = 3..12 (Table 1 of the note), and a brute-force cross-check against every weighted game with weights in {0..6} (n <= 5) or {0..5} (n = 6) and every quota: 983,844 (w, q) pairs, none outside the list and none with `eta/c` in (0, 1) |
| `find_simple_n6.py` | CP-SAT search for a simple game with `eta ∝ (2,...,2,1)`; finds the n = 6 witness |
| `verify_witness_n6.py` | Independent check of that witness: swing vector `(8,8,8,8,8,4)`, minimality, and non-completeness of the desirability relation |

Requirements: Python 3.9+, `ortools` (only for `find_simple_n6.py`).
The randomized checks use fixed seeds; the two exhaustive checks are
deterministic. The CP-SAT search uses 8 workers, so the solver trace is not
deterministic, but any returned game is a certificate that is checked
separately by `verify_witness_n6.py`.

The constraint-programming certificates of infeasibility at the weight bound
`w_i <= 2^(n-1)` for 6 <= n <= 10 are in `../../q3/` (`conj15_feas2.py`) with
their run logs in `../../q3/server_q3work/`.
