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

- `core/` — shared modules (GIGP engine)
- `hutchinson_pure/` — core synthesis system (Hutchinson Pure)
- `hutchinson_generalized/` — generalized framework (work in progress)
- `gigp_explorer/` — interactive GIGP validation tool
- `examples/` — curated audio and visual examples
- `validation/` — MMD validation results from GIGP Explorer
- `docs/` — technical documentation
- `tests/` — basic tests

## Audio Examples

See `examples/` for curated configurations with binaural audio and spectrograms.

## Paper

Preprint and full documentation available after publication.

## License

GNU General Public License v3.0 — see `LICENSE`.
