# Validation

This folder contains the validation work for the GIGP (Generalized
Immanantal Gibbs Process) framework, split into two companions.

## `gigp/` — numerical validation

Statistical validation of the GIGP sampler via Maximum Mean Discrepancy
(MMD) against the 8 reference distributions, plus the beta-ensemble sweep
(21 beta values x 12 seeds) that tests whether intermediate beta regimes
are measurably distinct from the base distributions. See
`gigp/BETA_ENSEMBLE_VALIDATION.md` for the full methodology and
`gigp/test_results.md` for the complete fix/verification history. Raw and
per-seed CSVs, plots (`plots/`), and niche-occupancy counts
(`region_counts_sweep.csv`) are also here.

## `gigp_audio/` — audio validation

Listening-level companion sweeps: three 21-point beta sweeps, one per GIGP
configuration block (population density, cell geometry, intra-cell
distribution), each producing a rendered `.wav` and a set of
visualizations (frequency glissando, 3D sphere, 2D flat azimuth/elevation
map, per-axis azimuth/elevation movement) per beta value. See
`gigp_audio/BETA_BLOCK_SWEEPS.md` for the full rationale and rendering
instructions.

Note: curated audio/visual examples with fixed, hand-picked configurations
(spectrograms, binaural renders) live separately in `examples/` — those
demonstrate the sonic output of specific configurations rather than the
statistical or listening-level properties of the beta parameter.
