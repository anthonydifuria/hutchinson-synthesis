# Beta-Ensemble Numerical Validation

This note documents the quantitative validation behind the statement, in
the paper (Section IV, "The Three Blocks of the GIGP Formula"), that the
parameter $\beta \in [-1,+1]$ navigates continuously between DPP
($\beta=-1$), Poisson ($\beta=0$), and Permanental ($\beta=+1$), and that
intermediate values produce a continuum of structure between the two
extremes (Section V, Table II discussion).

## Question

Does the sampler, for an intermediate $\beta$ (i.e. not one of the eight
base presets), produce a configuration that is genuinely distinct from
each of the eight reference distributions -- or could it, in practice,
coincide with one of them within sampling noise?

## Method

The full Phase 2 sweep from `run_validation.py` -- 168 configurations
(21 $\beta$ values from $-1.0$ to $+1.0$ in steps of 0.1, 4 Gibbs-energy
presets, 2 kernels) -- was run independently for 12 different random seeds
(`--seed` argument of `run_validation.py`). For every configuration and
every one of the 8 reference distributions, MMD$^2$ was computed for each
of the 12 seeds, giving a mean and a standard error of the mean (SEM)
per cell instead of a single point estimate.

## Two separability tests

**Test 1 -- distance from the nearest of the eight.** For each
intermediate $\beta$, is the MMD$^2$ to the closest of the 8 reference
distributions significantly different from zero, relative to its SEM
across the 12 seeds?

**Test 2 -- identity of the nearest neighbour.** Is the gap between the
first- and second-closest reference distribution significant relative to
their combined SEM -- i.e. can we confidently say *which* of the 8 the
intermediate configuration resembles most?

## Results

| Test | Median signal/SEM ratio | Configurations with ratio > 3 |
|------|--------------------------|-------------------------------|
| 1 -- distance from nearest | 4-6 (per \|β\| bucket) | 14-16 / 16 |
| 2 -- gap to 2nd-nearest | 1.3-2.9 (per \|β\| bucket) | 3-7 / 16 |

(A ratio > 3 is used as a conventional threshold for "clearly resolved
relative to sampling noise"; buckets are the 10 |β| values from 0.1 to
1.0, aggregated across the 4 energy presets x 2 kernels.)

At the anchor points ($\beta=-1$, $\beta=0$, $\beta=+1$, already validated
in Table I of the paper) both tests are unambiguous, with signal/SEM
ratios above 4.

## Interpretation

Test 1 is solid across almost the entire swept range: intermediate
$\beta$-ensembles are never statistically compatible with being a
disguised copy of one of the eight base distributions. Test 2 is
markedly weaker: for many intermediate $\beta$, two structurally related
neighbours (e.g. DPP/Strauss on the repulsive side, or
Matérn/LGCP/Permanental on the attractive side) remain nearly tied, and
which one is nominally "closest" is not statistically resolved even with
12 independent seeds.

Read together, this is exactly the numerical signature of a genuine
continuum between neighbouring regimes -- not a hidden ninth category
(which would show up as a stable, well-separated identity in Test 2) and
not sampling noise around one of the eight (which would fail Test 1). By
contrast, the paper's Table II ($\beta=0.4$ with an active Hawkes term) is
a case in which the nearest reference is unambiguous: Hawkes in all 12
seeds.

This is consistent with the paper's own caveat that a formally
consolidated denomination for the continuum of intermediate values has
not been identified in the consulted literature: the data support the
*existence* of a continuum (Test 1), not a finer categorical label for
each point along it (Test 2), which the paper does not claim either.

## What this validates, and what it does not

- Validates: intermediate $\beta$-ensembles are measurably distinct from
  each of the eight base distributions (Test 1), consistent with the
  continuity claim already published in Section IV.
- Does not validate, and should not be cited as: a specific "closest
  match" label for a given intermediate $\beta$ as a precise, reproducible
  result (Test 2) -- that identification is often within noise at the
  current sample size (N_POINTS=50, N_RUNS=8 per single measurement).

## Files

- `gigp_explorer/mmd_batch_validation/run_validation.py` -- generates all
  data below; `--seed <N>` produces an independent replicate run without
  overwriting the canonical (`--seed 42`, default) files.
- `phase2_beta_sweep_raw.csv`, `phase2_beta_sweep_raw_seed<N>.csv` --
  per-configuration, per-reference MMD$^2$ values (13 files: canonical +
  seeds 7, 100-109).
- `phase2_beta_sweep_closest.csv`, `phase2_beta_sweep_closest_seed<N>.csv`
  -- per-configuration nearest-reference summary.
- `test_results.md` -- full working log of the validation process,
  including the bugs found and fixed along the way (Gibbs-energy
  correction strength, Hawkes-energy point collapse, DPP-greedy plateau
  at $\beta \to 0$) that this study's fixes depend on.
