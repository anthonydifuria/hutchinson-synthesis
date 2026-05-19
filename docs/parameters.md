# Parameters Reference

Full parameter documentation for `config.py`.

## Global Parameters
- `HOA_ORDER` — ambisonics order (1–7)
- `NUM_NICHES` — number of active niches
- `TOTAL_DURATION` — composition duration in seconds
- `N_EVENTS_PER_NICHE` — events per niche
- `N_CANDIDATI` — candidate points for GIGP sampling
- `SEED` — random seed for reproducibility

## GIGP Configuration
- `CONFIGS_GIGP` — Voronoi cell geometry
- `CONFIGS_GIGP_NICHES` — population density per cell
- `CONFIGS_GIGP_INTERNAL` — intra-cell distribution

## Per-Dimension Control
Each effective dimension exposes: range [min, max], sampling freedom [0,1], directional bias (weight, strength, curvature).
