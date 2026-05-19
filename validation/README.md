# Validation

This folder contains validation results produced by the GIGP Explorer tool.

## Contents

### `gigp_explorer_results/`

MMD (Maximum Mean Discrepancy) results from GIGP Explorer sampling sessions.
Each test samples a given GIGP configuration and computes MMD against all 8
reference distributions. The distribution with minimum MMD is classified as
the closest structural match.

To reproduce these results, run GIGP Explorer:
```bash
cd ../gigp_explorer
python gigp_explorer.py
```

Note: audio and visual validation examples (spectrograms, binaural renders)
are in `examples/` — those demonstrate the sonic output of specific
configurations rather than the statistical properties of the distributions.
