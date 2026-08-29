# Hutchinson Synthesis

Parametric additive synthesis system based on Hutchinson's N-dimensional hypervolume concept with 7th-order Higher Order Ambisonics spatialization.

## Overview

Hutchinson Synthesis organizes sound events across four parametric dimensions — time, frequency, amplitude, and spatial position — using the GIGP (Generalized Immanantal Gibbs Process) framework. The system supports 8 stochastic distributions unified under a single formulation with continuous interpolation between repulsion, independence, and attraction regimes via the β parameter.

## Dependencies

- Python 3.10+
- numpy
- scipy
- matplotlib / vispy
- CSound 6.x or later

Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

```bash
cd hutchinson_pure
python main.py
```

Edit `config.py` to configure niches, distributions, and spatial parameters.

## Structure

- `hutchinson_pure/` — Hutchinson Pure: additive synthesis with time, frequency, amplitude, and spatial dimensions
- `hutchinson_generalized/` — Hutchinson Generalized: extension to any synthesis type (work in progress)
- `gigp_explorer/` — interactive GIGP validation tool
- `examples/` — curated audio and visual examples
- `validation/` — numerical (MMD, β-ensemble, spatial dispersion) and audio validation of the GIGP framework; see `validation/README.md`
- `docs/` — technical documentation

## Audio Examples

See `examples/` for curated configurations with binaural audio and spectrograms.

## Validation Data

Numerical validation CSVs and the audio-sweep configurations/images are
kept in this repository under `validation/`. The larger audio-sweep
`.wav` files are archived separately in the project's Zenodo data
deposit:
[10.5281/zenodo.22163384](https://doi.org/10.5281/zenodo.22163384)
(CC-BY 4.0). See `validation/README.md` for details on what is where.

## License

GNU General Public License v3.0 — see `LICENSE`. Validation data on
Zenodo is separately licensed CC-BY 4.0 (see the deposit for details).
