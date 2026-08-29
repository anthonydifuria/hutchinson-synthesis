"""
run_validation.py -- Batch / headless MMD validation for the GIGP framework.

This script automates what gigp_distribution.py does interactively (drag a
slider, press VALIDATE, read the plot): it runs a fixed list of GIGP
configurations, computes MMD^2 against the same 8 reference distributions
used by gigp_explorer, and saves the results as CSV + a plot instead of
console-only output.

It does not modify gigp.py or gigp_distribution.py; it only imports
ConfigDimensione and genera_centroidi_gigp_1d from gigp.py (same folder's
parent) and reimplements the same MMD / reference logic used by
gigp_distribution.py (mmd_biased, reference, DIST_VALID), so results are
directly comparable with the ones already in validation/gigp/test_results.md.

Two phases:

  Phase 1 -- all eight base distributions as generators.
    Each of the 8 reference presets (Poisson, DPP, Matern, Permanental,
    Strauss, Hawkes, LGCP, Alpha-Stable) is also run *as a generator* and
    compared against all 8 references, producing a full 8x8 MMD matrix.

  Phase 2 -- beta sweep across all kernel/energy combinations.
    For kernel in {gaussian, matern} and energy in {none, strauss, hawkes,
    both}, beta is swept over 21 values from -1.0 to +1.0 (step 0.1), each
    point compared against all 8 references. 2 kernels x 4 energy presets x
    21 beta values = 168 configurations. This traces the full transition
    curve behind the claim in Section IV of the paper ("intermediate
    values generate all degrees of structure"), instead of a single point,
    and -- now that gigp.py routes Matern through the same Block 2/3
    pipeline as the Gaussian kernel for any beta != -1 or active energy --
    the Matern combinations are meaningful too, not flat.

Output (written to ../../validation/gigp/):
  phase1_eight_distributions.csv
  phase2_beta_sweep_raw.csv
  phase2_beta_sweep_closest.csv
  plots/beta_sweep_overview.png

Expected runtime: a few minutes (beta < 0 configurations are the slow ones,
roughly 3s each; beta >= 0 configurations are fast). Progress is printed
per configuration so it's clear the script is still working.
"""

import os
import sys
import csv
import time
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gigp import ConfigDimensione, genera_centroidi_gigp_1d

# ---------------------------------------------------------------------------
# Constants -- match gigp_distribution.py exactly, for comparable results
# ---------------------------------------------------------------------------
N_POINTS = 50
N_RUNS = 8
SIGMA = 0.15
SEED = 42

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, '..', '..', 'validation', 'gigp')
PLOTS_DIR = os.path.join(OUT_DIR, 'plots')


def mmd_biased(X, Y, sigma=SIGMA):
    """Biased MMD^2 -- same formula as gigp_distribution.py's mmd_biased."""
    def k(a, b):
        return np.exp(-(a[:, None] - b[None, :]) ** 2 / (2 * sigma ** 2))
    return float(k(X, X).mean() - 2 * k(X, Y).mean() + k(Y, Y).mean())


def reference(cfg, seed=None):
    """Aggregates N_RUNS samples of N_POINTS points -- same as
    gigp_distribution.py's reference(). seed=None reads the *current*
    module-level SEED at call time (not the value bound at import time),
    so --seed can override it for a full independent replicate sweep."""
    if seed is None:
        seed = SEED
    rng = np.random.default_rng(seed)
    return np.concatenate([
        genera_centroidi_gigp_1d(N_POINTS, cfg, rng) for _ in range(N_RUNS)
    ])


# The 8 reference distributions -- identical presets to gigp_distribution.py
DIST_VALID = [
    ('Poisson',   ConfigDimensione(beta=0.0,  kernel_tipo='gaussiano')),
    ('DPP',       ConfigDimensione(beta=-1.0, kernel_tipo='gaussiano')),
    ('Matern',    ConfigDimensione(beta=-1.0, kernel_tipo='matern')),
    ('Permanent', ConfigDimensione(beta=+1.0, kernel_tipo='gaussiano')),
    ('Strauss',   ConfigDimensione(beta=0.0,  w_strauss=3.0, R_strauss=0.08)),
    ('Hawkes',    ConfigDimensione(beta=0.0,  w_hawkes=2.0,  decay_hawkes=5.0)),
    ('LGCP',      ConfigDimensione(beta=0.0,  lambda_tipo='lgcp')),
    ('Alpha-S.',  ConfigDimensione(beta=0.0,  lambda_tipo='alpha_stable')),
]
DIST_NAMES = [d[0] for d in DIST_VALID]


def build_reference_samples():
    print(f"Building the 8 reference distributions "
          f"({N_RUNS} runs x {N_POINTS} points each, seed={SEED})...")
    refs = {}
    for name, cfg in DIST_VALID:
        refs[name] = reference(cfg)
    return refs


def mmd_row(candidate_samples, refs):
    """MMD of candidate_samples against each of the 8 references."""
    return {name: mmd_biased(candidate_samples, refs[name]) for name in DIST_NAMES}


# ---------------------------------------------------------------------------
# Phase 1 -- eight base distributions as generators
# ---------------------------------------------------------------------------

def run_phase1(refs, suffix=''):
    print("\n=== Phase 1: eight base distributions as generators ===")
    rows = []
    for gen_name, gen_cfg in DIST_VALID:
        gen_samples = reference(gen_cfg)
        row = mmd_row(gen_samples, refs)
        closest = min(row, key=row.get)
        ok = closest == gen_name
        print(f"  generator={gen_name:10s} closest={closest:10s} "
              f"{'OK' if ok else 'MISMATCH'}")
        rows.append({'generator': gen_name, **row,
                      'closest': closest, 'self_identified': ok})

    path = os.path.join(OUT_DIR, f'phase1_eight_distributions{suffix}.csv')
    with open(path, 'w', newline='') as f:
        fieldnames = ['generator'] + DIST_NAMES + ['closest', 'self_identified']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  written: {path}")
    return rows


# ---------------------------------------------------------------------------
# Phase 2 -- beta sweep across kernel/energy combinations
# ---------------------------------------------------------------------------

ENERGY_PRESETS = {
    'none':    dict(w_strauss=0.0, w_hawkes=0.0),
    'strauss': dict(w_strauss=3.0, R_strauss=0.08, w_hawkes=0.0),
    'hawkes':  dict(w_strauss=0.0, w_hawkes=2.0, decay_hawkes=5.0),
    'both':    dict(w_strauss=3.0, R_strauss=0.08, w_hawkes=2.0, decay_hawkes=5.0),
}
KERNELS = ['gaussiano', 'matern']
BETA_VALUES = np.round(np.linspace(-1.0, 1.0, 21), 2)


def run_phase2(refs, suffix=''):
    total = len(BETA_VALUES) * len(ENERGY_PRESETS) * len(KERNELS)
    print(f"\n=== Phase 2: beta sweep "
          f"({len(BETA_VALUES)} beta points x {len(ENERGY_PRESETS)} energy x "
          f"{len(KERNELS)} kernel = {total} configs) ===")

    raw_rows = []
    closest_rows = []
    curves = {}  # (energy, kernel) -> {ref_name: [mmd per beta]}
    t_start = time.time()
    done = 0

    for energy_name, energy_kw in ENERGY_PRESETS.items():
        for kernel in KERNELS:
            curve = {name: [] for name in DIST_NAMES}
            for beta in BETA_VALUES:
                t0 = time.time()
                cfg = ConfigDimensione(beta=float(beta), kernel_tipo=kernel, **energy_kw)
                samples = reference(cfg)
                row = mmd_row(samples, refs)
                closest = min(row, key=row.get)
                dt = time.time() - t0
                done += 1

                for name in DIST_NAMES:
                    curve[name].append(row[name])
                    raw_rows.append({'energy': energy_name, 'kernel': kernel,
                                      'beta': beta, 'ref_distribution': name,
                                      'mmd': row[name]})
                closest_rows.append({'energy': energy_name, 'kernel': kernel,
                                      'beta': beta, 'closest': closest,
                                      'min_mmd': row[closest]})
                elapsed = time.time() - t_start
                print(f"  [{done:3d}/{total}] energy={energy_name:8s} "
                      f"kernel={kernel:9s} beta={beta:+.2f}  "
                      f"closest={closest:10s}  ({dt:.2f}s, {elapsed:.0f}s elapsed)")
            curves[(energy_name, kernel)] = curve

    raw_path = os.path.join(OUT_DIR, f'phase2_beta_sweep_raw{suffix}.csv')
    with open(raw_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['energy', 'kernel', 'beta',
                                                'ref_distribution', 'mmd'])
        writer.writeheader()
        writer.writerows(raw_rows)
    print(f"  written: {raw_path}")

    closest_path = os.path.join(OUT_DIR, f'phase2_beta_sweep_closest{suffix}.csv')
    with open(closest_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['energy', 'kernel', 'beta',
                                                'closest', 'min_mmd'])
        writer.writeheader()
        writer.writerows(closest_rows)
    print(f"  written: {closest_path}")

    return curves


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

def plot_overview(curves, suffix=''):
    """Single combined figure (one file, one continuous beta axis -1..1),
    y-axis in symlog scale.

    History: v1 used one linear shared y-axis (0-0.5) across both beta
    regimes -- the attractive side (beta>=0, MMD^2 up to ~0.03) looked
    visually flat/zero next to the repulsive side (up to ~0.5), even
    though the difference is real (see validation/gigp/test_results.md).
    v2 split into two separate images with two different linear scales --
    Anthony pointed out this has the opposite honesty problem: two panels
    with silently different y-axis scales can visually mislead a reader
    into thinking both regimes have comparable magnitude. Correct here:
    a single plot, single y-axis, in symlog scale, since the data spans
    several orders of magnitude (0.0003 to ~0.5) and includes exact zeros
    (self-identification points) that a plain log scale can't show. This
    is standard practice for this kind of data and keeps everything
    honestly on one declared, nonlinear-but-labelled axis.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    os.makedirs(PLOTS_DIR, exist_ok=True)
    energies = list(ENERGY_PRESETS.keys())
    kernels = KERNELS
    LINTHRESH = 1e-3

    fig, axes = plt.subplots(len(kernels), len(energies),
                              figsize=(19, 8), sharex=True, sharey=True)
    colors = plt.cm.tab10(np.linspace(0, 1, len(DIST_NAMES)))

    for i, kernel in enumerate(kernels):
        for j, energy in enumerate(energies):
            ax = axes[i, j]
            curve = curves[(energy, kernel)]
            for name, color in zip(DIST_NAMES, colors):
                ax.plot(BETA_VALUES, curve[name], label=name, color=color,
                        linewidth=1.5)
            ax.set_yscale('symlog', linthresh=LINTHRESH)
            ax.set_title(f"energy={energy}, kernel={kernel}", fontsize=10)
            ax.axvline(0.0, color='gray', linewidth=0.5, linestyle=':')
            if i == len(kernels) - 1:
                ax.set_xlabel('beta')
            if j == 0:
                ax.set_ylabel(f'MMD^2 (symlog, linthresh={LINTHRESH})')

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=8, fontsize=9,
               bbox_to_anchor=(0.5, 1.04))
    fig.suptitle('GIGP: MMD to each of the 8 reference distributions, '
                 'as a function of beta (symlog y-axis)', y=1.09, fontsize=12)
    fig.tight_layout()

    out_path = os.path.join(PLOTS_DIR, f'beta_sweep_overview{suffix}.png')
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  written: {out_path}")
    return out_path


# ---------------------------------------------------------------------------

def main():
    global SEED
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=SEED,
                         help=f'RNG seed for the whole run (default {SEED}). '
                              'A non-default seed writes to *_seed<N> files '
                              'instead of the canonical ones, so it never '
                              'overwrites the already-validated seed=42 '
                              'results -- use this to generate an '
                              'independent replicate sweep (see '
                              'validation/gigp/test_results.md, sezione '
                              '"novita\' dei beta-ensemble").')
    args = parser.parse_args()
    SEED = args.seed
    suffix = '' if SEED == 42 else f'_seed{SEED}'

    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    print(f"Using seed={SEED}"
          + (f" (independent replicate run, output suffix '{suffix}')"
             if suffix else " (canonical run)"))
    refs = build_reference_samples()
    run_phase1(refs, suffix=suffix)
    curves = run_phase2(refs, suffix=suffix)
    plot_overview(curves, suffix=suffix)
    print(f"\nDone in {time.time() - t0:.0f}s.")


if __name__ == '__main__':
    main()
