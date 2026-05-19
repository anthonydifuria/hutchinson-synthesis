# GIGP Explorer

Interactive tool for sampling and validating GIGP configurations via Maximum Mean Discrepancy (MMD).

## Usage

```bash
cd gigp_explorer
python gigp_explorer.py
```

## What it does

Samples a given GIGP configuration and computes MMD against all 8 reference distributions. The distribution with minimum MMD is classified as the closest structural match.

Useful for verifying emergent behavior when combining blocks — see Test 4 in the paper for an example of an intermediate regime classified as Strauss rather than Hawkes.
