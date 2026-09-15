# Prescribed Banzhaf power: closed-form games, congruence conditions, and certified weighted obstructions

Companion repository for the paper of the same name.

**Authors.** Yongjin Chen <sup>a</sup> · Ziying Xue <sup>b</sup> · Songze Zhu <sup>a,\*</sup>

<sup>a</sup> School of Public Security Management, People's Public Security University of China, Beijing 100038, China
<sup>b</sup> School of Investigation, People's Public Security University of China, Beijing 100038, China
<sup>\*</sup> Corresponding author: 20196846@ppsuc.edu.cn

This repository holds the manuscript, the machine-readable datasets, and every script that
reproduces a numerical claim in the paper. It is self-contained and deterministic: no step
requires network access.

## Layout

| Path | Contents |
|---|---|
| `manuscript.pdf` / `.md` / `.tex` | The manuscript (PDF, Markdown source, LaTeX) |
| `mathfix.lua` | Pandoc Lua filter that typesets the mathematics |
| `graphical_abstract.pdf` / `.png` / `.py` | Graphical abstract and the script that draws it |
| `source_manifest.json` | The 18 references (E001–E018), each with a verification record |
| `code/` | 93 Python scripts — constructions, MILP/CP-SAT models, verification, the formulation benchmark |
| `q3/` | Weighted-infeasibility experiments (§9) and their server run logs |
| `data/` | Result datasets (see below) |
| `scripts/` | The checkers that verify the paper's numbers and reproduce the case study |

## Reproducing the claims

Every numerical claim in the manuscript is checked against `data/appendix-data-n80.json`, the
authoritative dataset covering n = 6..80 whose swing vectors were re-verified by direct
enumeration.

- **Closed-form constructions (W-family).** `python code/reproduce_all.py` prints the swing
  vectors β(v_{G_n}) ∝ (2,…,2,1); every c-value in the §10.1 / Proposition 10 / §7 tables is
  stored in and cross-checked against `data/appendix-data-n80.json`.
- **Theorem 2 (the target family ψⁿ(a,b)).** `python code/general_target_family.py --nmax 18
  --amax 4` builds each realizing graph by Havel–Hakimi and confirms the swing vector by
  enumerating all 2ⁿ coalitions. The script asserts the exhaustive-search bound before
  searching, so negative entries in its coverage table are complete for n ≤ 120 rather than
  artifacts of a truncated loop.
- **§9 weighted infeasibility (ψⁿ is not realizable by a weighted majority game, n = 6..10).**
  `python q3/conj15_feas.py` (n ≤ 8) and `python q3/conj15_feas2.py` (n = 9, 10; the enhanced
  model with (M′) mirror constraints). The weight bound W = 2^(n−1) makes INFEASIBLE
  conclusive. Run scripts and server logs are in `q3/`.
- **§10.4 formulation benchmark.** `python code/benchmark_formulations.py` runs the three
  formulations (direct weight-space, general monotone, compressed W-family) on n = 6..20 under
  one 300 s solver limit and writes `data/benchmark_formulations.json`. The witness check is
  independent of the formulations: each solution is rebuilt and its swings recounted by
  enumerating all 2ⁿ coalitions.
- **§12 EU Council case study (EEC-6/9/10/12, EU-15).** `python scripts/case_study_eu.py`
  reproduces every §12 number; captured output in `scripts/case_study_eu_output.txt`.

## Verification scripts

| Script | Purpose |
|---|---|
| `scripts/verify_appendix_manuscript.py` | every c-value claimed in the manuscript (tables and narrative) vs `data/appendix-data-n80.json` |
| `scripts/verify_benchmark_manuscript.py` | every number in the §10.4 tables, and the rerun times quoted in its prose, vs `data/benchmark_formulations.json` |
| `scripts/case_study_eu.py` | reproduces every §12 number |

All three are offline and exit non-zero on any mismatch.

## Data files

| File | Role |
|---|---|
| `data/appendix-data-n80.json` | **Authoritative**: an explicit realizing graph and a scale c for every n = 6..80, each re-verified against ψⁿ and the monotonicity condition Pairs(F) ⊆ G (`code/reproduce_all.py`). Minimality of c is certified for n = 6..10 only; for larger n it is an upper bound, and minimality is an open problem (§11, Open problem 2) |
| `data/appendix-data.json` | Earlier-generation dataset, superseded by the n80 file |
| `data/appendix-solutions.md` | Human-readable appendix of realizing constructions |
| `data/benchmark_formulations.json` | §10.4: every field of the three-formulation benchmark |

## Rebuilding the manuscript

`manuscript.tex` is included, so the PDF can be rebuilt without pandoc:

```
xelatex manuscript.tex
xelatex manuscript.tex
```

To regenerate `manuscript.tex` from `manuscript.md` the way it was produced:

```
pandoc manuscript.md --lua-filter mathfix.lua -s \
  --pdf-engine=xelatex -V mainfont="Latin Modern Roman" -o manuscript.tex
```

The title and author block live in `manuscript.md` as raw LaTeX, so no `-M title` is needed.

Two typesetting hazards are worth knowing if you edit the source, because both produce a
completely clean LaTeX log while printing the wrong mathematics. A backslash in the prose can
be silently eaten by pandoc (`N\({a,b} ∪ {i})` prints as `N ({a,b} ∪ {i})`, losing the
set-difference operator), and a hand-written `N\S` prints a section sign. `mathfix.lua`
refuses stray raw TeX at build time, which catches the second.

## Dependencies

Python 3 (the standard library is enough for `reproduce_all.py` and
`verify_appendix_manuscript.py`), `ortools` for the CP-SAT obstruction and W-family models,
`scipy`/HiGHS for some MILP scripts, and pandoc + xelatex for a LaTeX rebuild.

## What is not here

The pre-submission QA harness — the gate suite and the guards that check the rendered PDF —
is not distributed, because it rules on files that are internal by nature. It is available
from the corresponding author on request.
