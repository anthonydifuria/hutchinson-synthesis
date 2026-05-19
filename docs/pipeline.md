# Pipeline: Python → CSound

1. Configure niches and GIGP parameters in `config.py`
2. `main.py` calls `gigp.py` (from `core/`) to sample events per niche
3. `score_generator.py` serializes events into a `.csd` file (orchestra + score)
4. The score specifies per-event: onset, duration, frequency with glissando morphology, amplitude envelope, FM modulation parameters, spherical coordinates with spatial movement
5. The orchestra instrument delegates HOA encoding to a dedicated UDO based on SN3D real spherical harmonics up to 7th order
6. `renderer.py` calls CSound to render the `.csd` into a multichannel WAV in AmbiX SN3D/ACN format
