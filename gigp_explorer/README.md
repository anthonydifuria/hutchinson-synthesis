# GIGP Explorer

Interactive tool for sampling and validating GIGP configurations via Maximum Mean Discrepancy (MMD).

## Usage

```bash
cd gigp_explorer
python gigp_explorer.py
```

## What it does

Samples a given GIGP configuration and computes MMD against all 8 reference distributions. The distribution with minimum MMD is classified as the closest structural match. Results are saved to `validation/gigp_explorer_results/`.

Useful for checking how the combined blocks behave — see Test 4 in the paper (Table II, a Hawkes term with β = 0.4), where the nearest reference distribution is Hawkes.
