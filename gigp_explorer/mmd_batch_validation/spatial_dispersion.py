"""
spatial_dispersion.py -- Objective spatial dispersion statistic on the
sphere, for Reviewer 2's Main comment 4(b) ("source distribution
statistics on the sphere").

It does not modify gigp.py; it only imports gigp() and
genera_centroidi_gigp_1d from gigp.py (same folder's parent), the same
functions already used by run_validation.py and by the
validation/gigp_audio/09_cell_geometry_sweep audio sweep for the "Cell
geometry" GIGP block (CONFIGS_GIGP).

Method
------
For each of the same 21 beta values used throughout the rest of the
paper's numerical validation (-1.00 .. +1.00, step 0.10), draw N=100
independent azimuth and independent elevation niche centroids with
kernel='matern' (matching validation/gigp_audio/09_cell_geometry_sweep),
map them from [0,1] to az_range=(-pi,pi) and el_range=(-pi/2,pi/2) -- the
exact ranges used in hutchinson_pure/main_v1_independent.py's
DIM_RANGE_MAP, not invented here -- convert each (az, el) pair to a unit
vector on S^2, and compute the mean resultant vector length

  R = | sum_i u_i | / N

the standard Fisher (1953) spherical concentration statistic: R -> 0 for
points spread uniformly over the sphere (no preferred direction), R -> 1
for points collapsed onto a single direction (total clustering).

N=100 matches N_EVENTS_PER_NICHE=100 in the reference config
(examples/01_matern_3niches_sparse/config.py). SEED=41 matches the SEED
used throughout that reference config and the beta-block audio sweeps.
sigma_base=0.3 is the ConfigDimensione / genera_centroidi_gigp_1d default
used throughout the rest of the codebase.

This is a single deterministic run per beta (one fixed seed, no averaging
over replicates): a descriptive, reproducible spatial statistic, offered
as evidence of the qualitative repulsion-to-attraction trend, not as a
significance-tested claim about any single beta value. See
SPATIAL_DISPERSION_VALIDATION.md (validation/gigp/) for the full
discussion, including what this result does and does not support.

Usage: python3 spatial_dispersion.py
Output: spatial_dispersion_cell_geometry_block.csv (in the current
directory), plus a console table.
"""
import os
import sys
import csv

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gigp import gigp, genera_centroidi_gigp_1d

AZ_RANGE = (-np.pi, np.pi)
EL_RANGE = (-np.pi / 2, np.pi / 2)
SIGMA_BASE = 0.3
N = 100
SEED = 41

BETAS = [round(-1.0 + 0.1 * i, 2) for i in range(21)]


def sample_direction_set(beta):
    cfg = gigp('uniforme', beta=beta, kernel='matern')
    rng_az = np.random.default_rng(SEED)
    rng_el = np.random.default_rng(SEED + 100000)
    az01 = np.asarray(genera_centroidi_gigp_1d(N, cfg, rng_az, sigma_base=SIGMA_BASE)).reshape(-1)
    el01 = np.asarray(genera_centroidi_gigp_1d(N, cfg, rng_el, sigma_base=SIGMA_BASE)).reshape(-1)
    az = AZ_RANGE[0] + az01 * (AZ_RANGE[1] - AZ_RANGE[0])
    el = EL_RANGE[0] + el01 * (EL_RANGE[1] - EL_RANGE[0])
    x = np.cos(el) * np.cos(az)
    y = np.cos(el) * np.sin(az)
    z = np.sin(el)
    return np.stack([x, y, z], axis=1)


def resultant_length(u):
    s = u.sum(axis=0)
    return float(np.linalg.norm(s) / u.shape[0])


def main():
    rows = []
    for beta in BETAS:
        u = sample_direction_set(beta)
        R = resultant_length(u)
        rows.append({"beta": beta, "R": R})

    print(f"{'beta':>6} | {'R':>8}")
    for r in rows:
        print(f"{r['beta']:6.2f} | {r['R']:8.4f}")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "spatial_dispersion_cell_geometry_block.csv")
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["beta", "R"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print()
    print(f"R(beta=-1.00) = {rows[0]['R']:.4f}")
    print(f"R(beta= 0.00) = {rows[10]['R']:.4f}")
    print(f"R(beta=+1.00) = {rows[20]['R']:.4f}")


if __name__ == "__main__":
    main()
