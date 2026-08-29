# Validation

This folder contains the validation work for the GIGP (Generalized
Immanantal Gibbs Process) framework, split into three companions.

## `gigp/` — numerical validation

Statistical validation of the GIGP sampler via Maximum Mean Discrepancy
(MMD) against the 8 reference distributions, plus the beta-ensemble sweep
(21 beta values x 12 seeds) that tests whether intermediate beta regimes
are measurably distinct from the base distributions, and a directional
statistic (mean resultant vector length on the sphere) that measures how
the Cell geometry block's beta changes the spatial concentration of
sampled source directions. See `gigp/BETA_ENSEMBLE_VALIDATION.md` and
`gigp/SPATIAL_DISPERSION_VALIDATION.md` for the full methodology, and
`gigp/test_results.md` for the complete fix/verification history. Raw and
per-seed CSVs, plots (`plots/`), niche-occupancy counts
(`region_counts_sweep.csv`), and the spatial-dispersion CSV
(`spatial_dispersion_cell_geometry_block.csv`) are also here.

## `gigp_audio/` — audio validation

Listening-level companion sweeps: three 21-point beta sweeps, one per GIGP
configuration block (population density, cell geometry, intra-cell
distribution), each producing a rendered `.wav` and a set of
visualizations (frequency glissando, 3D sphere, 2D flat azimuth/elevation
map, per-axis azimuth/elevation movement) per beta value. See
`gigp_audio/BETA_BLOCK_SWEEPS.md` for the full rationale and rendering
instructions.

The `.wav` files themselves are not kept in this git repository (63 files,
~1.1 GB) — they are archived, together with the numerical validation data
above, in the project's Zenodo data deposit:
[10.5281/zenodo.22163384](https://doi.org/10.5281/zenodo.22163384)
(CC-BY 4.0). The `config.py` and image files for every beta value stay
here, so each sweep's configuration and visual output remain directly
browsable in the repository even without the audio.

Note: curated audio/visual examples with fixed, hand-picked configurations
(spectrograms, binaural renders, reverb added in post-production) live
separately in `examples/` — those demonstrate the sonic output of
specific configurations rather than the statistical or listening-level
properties of the beta parameter, and are not part of the Zenodo deposit
above (pending a re-render).

## Citing this data

If you use the validation data (numerical or audio) from this project,
please cite the Zenodo deposit:
[10.5281/zenodo.22163384](https://doi.org/10.5281/zenodo.22163384).
