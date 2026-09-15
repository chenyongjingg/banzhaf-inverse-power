#!/bin/bash
# n=10 re-certification in a box that the HADAMARD FORM of Muroga's bound certifies,
# so that the n=10 cell of the Section 9 table no longer depends on the tabulated
# value alpha_10 = 320 (OEIS A003432).
#
# alpha_n <= (n+1)^((n+1)/2) / 2^n   (Hadamard, applied to order-n 0-1 determinants)
#   n=9  -> 10^5/2^9   = 195.31 <= 2^8  = 256   (the published W = 2^(n-1) is already
#                                                covered by the inequality, no re-run needed)
#   n=10 -> 11^5.5/2^10 = 521.61 >  2^9  = 512   (NOT covered: the published run needs
#                                                the table value 320, hence this job)
# An integer weight below 521.61 is at most 521, so W = 522 is the smallest box the
# inequality certifies.  Same enhanced model (feas2) as the published n=10 verdict;
# 16 workers (the box is free now) rather than the published 8, and every run prints
# its own configuration, so the log states its provenance.
#
# Expected verdict: INFEASIBLE, as at W = 512.  Anything else -- in particular a
# FEASIBLE -- would mean the target IS realizable at n = 10 with a weight in (512,522]
# and the Section 9 table is wrong; the log would have to be treated as a headline.
cd "$(dirname "$0")" || exit 1

echo "n=10, W=522 (Hadamard-certified box), enhanced model, 16 workers, 8h solver budget"
timeout 30000 python conj15_feas2.py 10 522 28800 16 > conj15_feas2_n10_W522.log 2>&1
echo "exit=$?" >> conj15_feas2_n10_W522.log
