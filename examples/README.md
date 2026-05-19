# Examples

Curated configurations demonstrating specific GIGP regimes and spatial
behaviors. Each example folder contains:

- `config.py` — full parameter configuration to reproduce the result
- `spectrogram.png` — frequency distribution over time
- `audio_binaural.wav` — binaural render for headphone listening

| # | Folder | Niches | Events/niche | Freq range | Spatial | Key feature |
|---|--------|--------|-------------|------------|---------|-------------|
| 01 | matern_3niches_sparse | 3 | 100 | 100–10000 Hz | free | baseline Matérn separation, 3 niches |
| 02 | matern_10niches_rings_low | 10 | 100 | 100–2000 Hz | rings EL | elevation rings, low register |
| 03 | matern_10niches_rings_dense | 10 | 1000 | 100–2100 Hz | rings EL | high density, elevation rings |
| 04 | matern_10niches_ren_medium | 10 | 200 | 100–6000 Hz | REN 0.8 | partial REN constraint |
| 05 | matern_10niches_ren_fullrange | 10 | 1000 | 100–10000 Hz | REN soft | full range, soft REN |
| 06 | matern_2niches_longdur_bass | 2 | 50 | 100–500 Hz | rings EL | long events, bass register |