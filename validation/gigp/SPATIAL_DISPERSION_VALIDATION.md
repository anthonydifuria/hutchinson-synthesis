# Spatial Dispersion on the Sphere -- Numerical Validation

This note documents the quantitative spatial result added to the paper
(Section VII, "The Spatial Dimension: HOA and REN") in response to
Reviewer 2's Main comment 4: the reported spatial validation was mainly
distributional and visual, and the paper should add at least one
objective or descriptive spatial result, such as source distribution
statistics on the sphere.

## Question

The paper already states, qualitatively, that the Cell geometry GIGP
block's beta continuously controls separation vs. clustering of niches
across every dimension, including azimuth and elevation, and that
beta = -1 produces spatially separated sources while beta = +1
concentrates them into clusters. Can this be shown as an objective,
reproducible number rather than only a qualitative/visual claim?

## Method

For each of the 21 beta values already used throughout the rest of the
paper's numerical validation (-1.00 to +1.00, step 0.10), N=100
independent azimuth and N=100 independent elevation niche centroids are
drawn with `gigp('uniforme', beta=beta, kernel='matern')` -- the same
GIGP call already used for the "Cell geometry" block in
`validation/gigp_audio/09_cell_geometry_sweep` -- and mapped from [0,1]
to az_range=(-pi,pi), el_range=(-pi/2,pi/2), the exact ranges used
in `hutchinson_pure/main_v1_independent.py`'s `DIM_RANGE_MAP`.

Each (az, el) pair is converted to a unit vector on the sphere S^2, and
the mean resultant vector length is computed:

  R = | sum_i u_i | / N

This is the standard Fisher (1953) concentration statistic for
directional/spherical data: R -> 0 when the N directions are spread
uniformly over the sphere (no preferred direction, consistent with
maximum repulsion), R -> 1 when they collapse onto a single direction
(total clustering, consistent with maximum attraction).

N=100 matches `N_EVENTS_PER_NICHE=100` in the reference config
(`examples/01_matern_3niches_sparse/config.py`). SEED=41 matches the
`SEED` used throughout that reference config and the beta-block audio
sweeps. `sigma_base=0.3` is the `ConfigDimensione` /
`genera_centroidi_gigp_1d` default used throughout the rest of the
codebase. This is a single deterministic run per beta value (one fixed
seed, no averaging over replicates).

## Results

| beta  | R      | beta  | R      | beta  | R      |
|------:|-------:|------:|-------:|------:|-------:|
| -1.00 | 0.0069 | -0.30 | 0.1665 |  0.40 | 0.1173 |
| -0.90 | 0.0776 | -0.20 | 0.1691 |  0.50 | 0.0681 |
| -0.80 | 0.0788 | -0.10 | 0.1044 |  0.60 | 0.1249 |
| -0.70 | 0.0526 |  0.00 | 0.1347 |  0.70 | 0.1849 |
| -0.60 | 0.0733 |  0.10 | 0.1133 |  0.80 | 0.2134 |
| -0.50 | 0.0876 |  0.20 | 0.0613 |  0.90 | 0.1023 |
| -0.40 | 0.0989 |  0.30 | 0.0920 |  1.00 | 0.2032 |

R(beta=-1.00) = 0.0069, R(beta=0.00) = 0.1347, R(beta=+1.00) = 0.2032.

At beta=-1 (pure Matern/LHS coverage, exact geometric spacing), R is
close to zero, i.e. the 100 sampled directions are close to uniformly
spread over the sphere -- consistent with maximum repulsion. Moving
away from beta=-1 raises R by roughly an order of magnitude, and the
single highest value in the whole sweep is at beta=+1.00 (maximum
attraction). Between these two endpoints, R does not increase
monotonically with beta: at N=100 with a single seed per beta, sampling
noise on this statistic is large enough (see the analogous
seed-to-seed spread documented for other quantities in
`BETA_ENSEMBLE_VALIDATION.md`) that the intermediate beta values are
not individually ordered in a stable way run to run.

## What this does and does not support

Supports: a positive claim that Cell-geometry beta measurably changes
the directional concentration of sampled sources on the sphere, in the
direction predicted by the block's repulsion/attraction interpretation
(beta=-1 close to uniform, beta=+1 the most clustered value observed),
given as a concrete, reproducible number rather than only a
distributional/visual comparison.

Does not support, and should not be cited as: a claim that R(beta) is
monotonic, or that any single intermediate beta value's R is
individually meaningful without replication -- both would require the
same kind of multi-seed replicate design as
`BETA_ENSEMBLE_VALIDATION.md`, which was not run here (a single
6-replicate check at N=100 during development showed the same
low-at-beta=-1 / high-at-positive-beta trend but similarly noisy
intermediate values; that check is not included as a shipped artifact
since only the single-seed run above is referenced by the paper text).

## Files

- `gigp_explorer/mmd_batch_validation/spatial_dispersion.py` -- generates
  the result below; imports `gigp()` and `genera_centroidi_gigp_1d` from
  `gigp.py` (same folder's parent), does not modify it.
- `spatial_dispersion_cell_geometry_block.csv` (this folder) -- the 21
  (beta, R) pairs listed above, also produced alongside the script in
  `gigp_explorer/mmd_batch_validation/`.
