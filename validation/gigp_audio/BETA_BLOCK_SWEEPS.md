# Beta block sweeps — audio companion to the numerical validation

This folder contains three audio sweeps, one per GIGP configuration block. Each
sweep renders the same 21-point beta grid used in the numerical validation
(`validation/gigp/`), but instead of measuring a statistical distance it
produces an actual `.wav` + frequency-glissando `.png` per beta value, so the
effect of beta can be heard and seen directly.

## Why three separate sweeps of 21, and not one sweep of 168

The numerical validation (`run_validation.py`, Phase 2) crosses 21 beta values
with 8 base kernel/energy combinations (Strauss, Hawkes, DPP, Poisson,
Permanental, ...) to get 168 configurations, because it needs that full grid
to compute an MMD distance between distributions.

That structure does not carry over to audio, for two reasons:

1. **No statistical target.** The audio sweeps are for listening, not for a
   distance metric — there is nothing that "needs" a 168-point grid the way
   an MMD computation does.
2. **A hard technical constraint.** `gigp.py`'s `gigp()` convenience wrapper
   forces `beta=0` whenever `kernel` is `'strauss'` or `'hawkes'` (see the
   docstring in `hutchinson_pure/gigp.py`): the interaction is handled by the
   Gibbs energy term instead, and beta and Strauss/Hawkes energy are mutually
   exclusive through that wrapper. A literal 21x8 audio mirror is therefore
   not directly reachable without bypassing `gigp()` in a more invasive way,
   which we deliberately did not do here.

Instead, each of the three GIGP configuration blocks gets its own clean,
one-factor-at-a-time sweep: vary that block's beta across the full grid,
kernel Matern, no Strauss/Hawkes energy, and hold the other two blocks at
their baseline value from the reference config
(`examples/01_matern_3niches_sparse/config.py`). 3 blocks x 21 values = 63
files total. This keeps each sweep interpretable on its own ("this is what
beta does when it moves niche boundaries" vs "... when it moves relative
event counts per niche" vs "... when it moves placement inside a niche"),
which is more useful for a listening demonstration than a much larger but
harder-to-interpret combinatorial set.

## The three GIGP blocks

These match the "GIGP Distribution Configuration" section of the paper
(`camera-ready-eng/hutchinson_synthesis.tex`): "The three levels operate in
cascade but are mathematically separable."

| Block | Config variable | Paper name | What it controls |
|---|---|---|---|
| 1 | `CONFIGS_GIGP` | Cell geometry | Position of the Voronoi centroids (the niche boundaries themselves) |
| 2 | `CONFIGS_GIGP_NICHES` | Population density | Which cell/niche is chosen for each event — i.e. the relative event count per niche |
| 3 | `CONFIGS_GIGP_INTERNAL` | Intra-cell distribution | Where a value lands *inside* the niche once that niche has been chosen |

## The three sweep folders

| Folder | Block swept | Held at baseline (unchanged) | Kernel used for the swept block |
|---|---|---|---|
| `08_population_density_sweep/` | 2 — Population density | Block 1 (beta=-1, matern), Block 3 (beta=0, kernel=None) | matern |
| `09_cell_geometry_sweep/` | 1 — Cell geometry | Block 2 (beta=-1, matern), Block 3 (beta=0, kernel=None) | matern |
| `10_intracell_distribution_sweep/` | 3 — Intra-cell distribution | Block 1 (beta=-1, matern), Block 2 (beta=-1, matern) | matern |

Note on block 3: the reference config's documented default for
`CONFIGS_GIGP_INTERNAL` is `kernel=None` (which resolves internally to a
gaussiano kernel). For the `10_intracell_distribution_sweep/` sweep only, we
use `kernel='matern'` instead, so that all three sweeps share the same
interaction geometry and differ *only* in which block's beta is being moved.
When block 3 is held at baseline (in the `08` and `09` folders) it keeps the
original `kernel=None` default — it is not touched at all there.

In every variant, beta grid is `-1.00, -0.90, ..., 0.00, ..., 0.90, 1.00`
(21 values, step 0.10), matching the numerical grid.

## Spatial constraints: REN and ring, disabled everywhere

All 63 configs (across all three folders) have the REN / ring spatial
constraints fully disabled:

- `REN_2D_FORCE = 0.0` (was 1.0 in the base template)
- `FREEDOM_REN_RADIUS = 1.0` (was 0.0)
- `FREEDOM_REN_RELAXATION = 1.0` (was 0.0)

This lets the niches move freely in space instead of being pulled toward a
deterministic flower-shaped mask, so the audible effect of beta is not
dominated or masked by that separate spatial constraint. Everything else in
the base template (`NUM_NICHES=3`, `N_EVENTS_PER_NICHE=100`, `SEED=41`,
`TOTAL_DURATION=30.0`, ...) is left untouched.

## Rendering

Each folder has its own `render_all.sh`. All three point at the same shared
scratch copy of the synthesis engine,
`_render_scratch_population_sweep/` (at the repository root, sibling of
`examples/` and `validation/` -- historical name from when only the
population-density sweep existed and lived under `examples/`; it is a
generic copy of `hutchinson_pure/` and works for all three sweeps, now that
this whole folder lives under `validation/gigp_audio/`). The real
`hutchinson_pure/` is never touched.

```
bash validation/gigp_audio/08_population_density_sweep/render_all.sh
bash validation/gigp_audio/09_cell_geometry_sweep/render_all.sh
bash validation/gigp_audio/10_intracell_distribution_sweep/render_all.sh
```

For each of the 21 variants in a folder, the script copies that variant's
`config.py` into the scratch engine, runs `main_v1_independent.py`
(interactive visualization disabled, so it doesn't block the batch loop),
then copies the two outputs back next to the config:

- `beta_X.XX.wav` — the rendered audio
- `beta_X.XX.png` — the frequency glissando plot (circle = freq_start,
  square = freq_end, curve = the glissando between them), same style as the
  existing `examples/*/freq.png` files

You can delete `_render_scratch_population_sweep/` once you're happy with
all three batches (`rm -rf`) — none of the scripts need it afterward.

## Relationship to the numerical validation

This audio sweep is a qualitative, listening-level companion to the
statistical validation in `validation/gigp/` — see
`validation/gigp/BETA_ENSEMBLE_VALIDATION.md` for the full methodology (21
beta values x 12 seeds, testing whether intermediate beta-ensembles are
measurably distinct from the 8 base distributions) and
`validation/gigp/test_results.md` for the complete fix/verification history
that the numerical grid itself is built on. The camera-ready paper's added
paragraph on intermediate beta-ensembles (after the Table II / Test 4
discussion) references the validation repository generally; this file and
the three sweep folders are the audio-side extension of that same
investigation, not something separately claimed in the paper text.
