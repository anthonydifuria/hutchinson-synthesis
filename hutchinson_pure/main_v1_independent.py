"""
main_v1_independent.py — Hutchinson Synthesis
Architettura 1D indipendente: ogni dimensione ha la sua distribuzione GIGP.
Le dimensioni sono completamente ortogonali — nessun accoppiamento.
"""
import os
import numpy as np
from gigp            import (genera_eventi_gigp, ConfigDimensione,
config_dpp_puro, config_da_separazione,
config_preset, campiona_gigp_esatto,
_genera_candidati_lambda,
genera_centroidi_gigp_1d)
from score_generator import genera_csd
from renderer        import renderizza, riproduci
from visualizer      import mostra_tutto
from config import *

DIR_OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
CSD_PATH   = os.path.join(DIR_OUTPUT, 'hutchinson_v1.csd')
WAV_PATH   = os.path.join(DIR_OUTPUT, 'hutchinson_v1.wav')
MOSTRA_VISUALIZZAZIONI = True
RIPRODUCI_AUDIO        = False

# ═══════════════════════════════════════════════════════════════
# 1D DIMENSION DEFINITIONS
# ═══════════════════════════════════════════════════════════════
# Each dimension has:
# ev_key     = key in the generated event
# range_key  = key in gs OR direct (min,max) tuple
# log        = True if dimension is in log space (type_*)
# In log case: mins/maxs are in log10, value
# is converted with 10^x after sampling
# dim 1 (density) is global — does not enter 1D pipeline
# dim 0 (duration) is sampled, but onset is separate
DIM_DEFS = {
    0:  ('durata',          'durata_range',            False),
    2:  ('amp',             'amp_range',               False),
    3:  ('perc',            'perc_range',              False),
    4:  ('n_sinusoidi',     'n_sin',                   False),
    5:  ('freq_start',      'freq_range',              False),
    6:  ('az',              'az_range',                False),
    7:  ('el',              'el_range',                False),
    8:  ('type_gliss',      'type_gliss_range',        True),
    9:  ('type_env',        'type_env_range',          True),
    10: ('type_mov_amb',    'type_mov_amb_range',      True),
    11: ('type_prox_amb',   'type_prox_amb_range',     True),
    12: ('freq_mod',        'freq_mod_range',          False),
    13: ('freq_amp',        'freq_amp_range',          False),
    14: ('prox_amp',        'prox_amp_range',          False),
    15: ('_prob_gliss',     'prob_range',              False),
    16: ('_prob_mov',       'prob_range',              False),
    # ── Anelli azimuth ────────────────────────────────────────
    17: ('az_band_center',  'az_range',                False),
    # ── Anelli elevazione ─────────────────────────────────────
    18: ('el_band_center',  'el_range',                False),
    # ── REN 2D ────────────────────────────────────────────────
    19: ('ren_az_center',   'az_range',                False),
    # REMOVED 22 & 23 to avoid Voronoi 1D conflicts, handled by _sample_ren_2d
    # ── Onset niche ─────────────────────────────────────────
    20: ('niche_onset',   'niche_onset_range',     False),
    21: ('niche_fade_in', 'niche_fade_in_range',   False),
    # ── NUOVE: dimensioni end e FM (Round 2) ──────────────────
    1:  ('onset',           'onset_range',             False),
    22: ('freq_end',        'freq_range',              False),
    23: ('az_end',          'az_range',                False),
    24: ('el_end',          'el_range',                False),
    25: ('freq_mod1',       'freq_mod_range',          False),
    26: ('freq_mod2',       'freq_mod_range',          False),
    27: ('freq_amp1',       'freq_amp_range',          False),
    28: ('freq_amp2',       'freq_amp_range',          False),
}

# Reverse: event key → dim_idx (for bias and visualizer)
KEY_TO_DIM = {v[0]: k for k, v in DIM_DEFS.items()}

# ═══════════════════════════════════════════════════════════════
# STATE
# ═══════════════════════════════════════════════════════════════
def genera_stato():
    return {
        'n': NUM_NICHES, 'seed': SEED, 'n_candidati': N_CANDIDATES,
        'master_gain': MASTER_GAIN, 'comp_iso': ISOPHONIC_COMPENSATION,
        'min_iso': ISOPHONIC_MINIMUM,
        'amp_range': AMP_RANGE_GLOBAL,
        'freq_range': FREQ_RANGE_GLOBAL,
        'scala_freq': FREQ_SCALE,
        'larghezza': NICHE_WIDTH,
        'durata_range': EVENT_DURATION_RANGE,
        'variabilita': DURATION_VARIABILITY,
        'struttura': RHYTHMIC_STRUCTURE,
        'durata_cellula': BEAT_DURATION,
        'perc_range': PERC_RANGE,
        'n_sin': (float(N_SIN_MIN), float(N_SIN_MAX)),
        'az_range': (-np.pi, np.pi),
        'el_range': (-np.pi/2, np.pi/2),
        'prob_range': (0.0, 1.0),
        # REN 2D and Rings
        'forza_ren_2d': REN_2D_FORCE,
        'visualizza_ren_2d': VISUALIZE_REN_2D,
        'anelli_az_attivi': RINGS_AZ_ATTIVI,
        'anelli_el_attivi': RINGS_EL_ATTIVI,
        # Rings
        # REN 2D
        'ren_raggio_range':    REN_RAGGIO_RANGE,
        'liberta_ren_raggio':  FREEDOM_REN_RADIUS,
        'liberta_rilassamento_ren': FREEDOM_REN_RELAXATION,
        # Niche onset
        'niche_onset_range':   (0.0, TOTAL_DURATION * 0.8),
        'niche_fade_in_range': (0.0, TOTAL_DURATION * 0.3),
        # REN shape parameters
        'ren_k': REN_K,
        'ren_lambda': REN_LAMBDA,
        'ren_q': REN_Q,
        # REN 2D center bias
        'ren_az_bias': (WEIGHT_REN_AZ_CENTER, FORCE_WEIGHT_REN_AZ_CENTER, CURVE_WEIGHT_REN_AZ_CENTER),
        'ren_el_bias': (WEIGHT_REN_EL_CENTER, FORCE_WEIGHT_REN_EL_CENTER, CURVE_WEIGHT_REN_EL_CENTER),
        # Active rings
        'niche_onset_attivo':   NICHE_ONSET_ACTIVE,
        'niche_fade_in_attivo': NICHE_FADE_IN_ACTIVE,
        'anelli_az_attivi': RINGS_AZ_ATTIVI,
        'anelli_el_attivi': RINGS_EL_ATTIVI,
        'type_gliss_range':    TYPE_GLISS_RANGE,
        'type_env_range':      TYPE_ENV_RANGE,
        'type_mov_amb_range':  TYPE_MOV_AMB_RANGE,
        'type_prox_amb_range': TYPE_PROX_AMB_RANGE,
        'prox_amp_range': PROX_AMP_RANGE,
        'freq_mod_range': FREQ_MOD_RANGE,
        'freq_amp_range': FREQ_AMP_RANGE,
        'liberta_freq_end': FREEDOM_FREQ_END,
        'liberta_az_end':   FREEDOM_AZ_END,
        'liberta_el_end':   FREEDOM_EL_END,
        'liberta_fm':       FREEDOM_FM,
        'freq_mod_range':   FREQ_MOD_RANGE,
        'freq_amp_range':   FREQ_AMP_RANGE,
        'forza_fm': FORCE_FM,
        'type_freq_mod': 1.0, 'forza_type_freq_mod': FORZA_TYPE_FREQ_MOD,
        'type_freq_amp': 1.0, 'forza_type_freq_amp': FORZA_TYPE_FREQ_AMP,
        # Onset range (dim 1)
        'onset_range': (0.0, TOTAL_DURATION * 0.92),
        # Freedom per dimension — expands sampling beyond the cell
        'liberta': {
            0:  FREEDOM_DURATION,
            1:  FREEDOM_ONSET,
            2:  FREEDOM_AMP,
            3:  FREEDOM_PERC,
            4:  FREEDOM_N_SIN,
            5:  FREEDOM_FREQ_START,
            6:  FREEDOM_AZ,
            7:  FREEDOM_EL,
            8:  FREEDOM_TYPE_GLISS,
            9:  FREEDOM_TYPE_ENV,
            10: FREEDOM_TYPE_MOV_AMB,
            11: FREEDOM_TYPE_PROX_AMB,
            12: FREEDOM_FREQ_MOD,
            13: FREEDOM_FREQ_AMP,
            14: FREEDOM_PROX_AMP,
            22: FREEDOM_FREQ_END,
            23: FREEDOM_AZ_END,
            24: FREEDOM_EL_END,
            25: FREEDOM_FREQ_MOD1,
            26: FREEDOM_FREQ_MOD2,
            27: FREEDOM_FREQ_AMP1,
            28: FREEDOM_FREQ_AMP2,
        },
        # Internal cell distribution configs
        'configs_interna': CONFIGS_GIGP_INTERNAL,
        # Width per dimension (overrides NICHE_WIDTH if defined)
        'larghezza_per_dim': globals().get('WIDTH_PER_DIM', {}),
    }

# ═══════════════════════════════════════════════════════════════
# ISOPHONIC COMPENSATION
# ═══════════════════════════════════════════════════════════════
def compensazione_isofonica(freq_hz, min_iso):
    f = float(np.clip(freq_hz, 20.0, 20000.0))
    f_log = (np.log10(f) - np.log10(20.0)) / (np.log10(20000.0) - np.log10(20.0))
    curva = 1.0 - 4.0 * (f_log - 0.5) ** 2
    curva = float(np.clip(curva, 0.0, 1.0))
    return float(np.clip(min_iso + (1.0 - min_iso) * curva, min_iso, 1.0))

# ═══════════════════════════════════════════════════════════════
# INDEPENDENT 1D VORONOI COMPUTATION
# ═══════════════════════════════════════════════════════════════
def _get_range(dim_idx, gs):
    """Restituisce (vmin, vmax) in spazio fisico per la dimensione dim_idx."""
    ev_key, range_key, is_log = DIM_DEFS[dim_idx]
    if isinstance(range_key, tuple):
        lo, hi = range_key
    else:
        val = gs[range_key]
        if isinstance(val, tuple):
            lo, hi = val
        else:
            lo, hi = float(val[0]), float(val[1])
    if is_log:
        # Convert to log10 space — GIGP operates on these values
        lo = np.log10(max(lo, 0.01))
        hi = np.log10(max(hi, 0.01))
    return float(lo), float(hi)

def voronoi_1d(c_norm, vmin, vmax):
    """
    Tassellazione di Voronoi 1D reale.
    I confini sono calcolati come punti medi tra centroidi adiacenti nello spazio normalizzato.
    Preserva la metrica di repulsione/attrazione del processo GIGP scelto.
    """
    n = len(c_norm)
    mins = np.zeros(n)
    maxs = np.zeros(n)
    order = np.argsort(c_norm)
    sorted_c = c_norm[order]

    # Normalized bounds [0, 1]
    boundaries = np.zeros(n + 1)
    boundaries[0]  = 0.0
    boundaries[-1] = 1.0
    for i in range(n - 1):
        boundaries[i + 1] = (sorted_c[i] + sorted_c[i + 1]) / 2.0

    # Linear mapping to physical space [vmin, vmax]
    span = vmax - vmin
    for rank, orig_idx in enumerate(order):
        mins[orig_idx] = vmin + boundaries[rank] * span
        maxs[orig_idx] = vmin + boundaries[rank + 1] * span

    return mins, maxs

def calc_voronoi_1d(gs, configs_voronoi, n, rng, configs_nicchie=None):
    """
    Esegue GIGP indipendente per ogni dimensione.
    configs_voronoi : CONFIGS_GIGP — geometria delle celle (posizione centroidi)
    configs_nicchie : CONFIGS_GIGP_NICHES — densita' di popolazione delle celle
                      I pesi vengono calcolati in base alla vicinanza dei centroidi
                      del secondo set a quelli del primo (zero costo extra).
    """
    dim_1d = {}
    for d, (ev_key, range_key, is_log) in DIM_DEFS.items():
        vmin, vmax = _get_range(d, gs)

        # 1. CONFIGS_GIGP — genera celle Voronoi
        config_v = configs_voronoi[d]
        c_1d     = genera_centroidi_gigp_1d(n, config_v, rng)
        mins, maxs = voronoi_1d(c_1d, vmin, vmax)

        # 2. CONFIGS_GIGP_NICHES — calcola pesi delle celle
        #    Genera n centroidi con la distribuzione nicchie e assegna
        #    ogni centroide alla cella piu' vicina del Voronoi.
        #    Le celle che attraggono piu' centroidi ricevono peso maggiore.
        if configs_nicchie is not None:
            config_n  = configs_nicchie[d]
            n_pts     = max(n * 10, 30)
            c_n       = genera_centroidi_gigp_1d(n_pts, config_n, rng)
            pts       = vmin + c_n * (vmax - vmin)
            # Sort cells by position for correct searchsorted
            sort_idx  = np.argsort(mins)
            mins_s    = mins[sort_idx]
            # Assign each point to nearest sorted cell
            cell_idx  = np.searchsorted(mins_s, pts, side='right') - 1
            cell_idx  = np.clip(cell_idx, 0, n - 1)
            # Convert sorted indices back to original cell indices
            counts_s  = np.bincount(cell_idx, minlength=n).astype(float)
            counts    = counts_s[np.argsort(sort_idx)]  # remap to original order
            counts    = np.maximum(counts, 0.1)
            weights   = counts / counts.sum()
        else:
            weights = np.ones(n) / n

        dim_1d[d] = {
            'mins': mins, 'maxs': maxs,
            'weights': weights,
            'log': is_log,
        }
    return dim_1d

def _risolvi_configs(preset=None):
    """
    Restituisce un dict {dim_idx: ConfigDimensione} allineato esattamente
    alle chiavi di DIM_DEFS.
    preset: lista o oggetto ConfigDimensione (default: CONFIGS_GIGP_NICHES)
    """
    dim_keys = sorted(DIM_DEFS.keys())
    n_dims   = len(dim_keys)
    base     = preset if preset is not None else CONFIGS_GIGP_NICHES
    if base is None:
        base = config_preset('matern', n_dims=n_dims)
    if not isinstance(base, list):
        base = [base] * n_dims
    if len(base) == 0:
        base = config_preset('matern', n_dims=n_dims)
    if len(base) < n_dims:
        base = list(base) + [base[-1]] * (n_dims - len(base))
    return {d: base[i] for i, d in enumerate(dim_keys)}

# ═══════════════════════════════════════════════════════════════
# BIAS — modifies 1D weights per dimension (completely independent)
# ═══════════════════════════════════════════════════════════════
def build_pesi_dimensioni():
    return _build_pesi([
        (0,  WEIGHT_DURATION,              FORCE_WEIGHT_DURATION,              CURVE_WEIGHT_DURATION),
        (2,  WEIGHT_AMPLITUDE,            FORCE_WEIGHT_AMPLITUDE,            CURVE_WEIGHT_AMPLITUDE),
        (3,  WEIGHT_PERC,                FORCE_WEIGHT_PERC,                CURVE_WEIGHT_PERC),
        (4,  WEIGHT_N_SIN,               FORCE_WEIGHT_N_SIN,               CURVE_WEIGHT_N_SIN),
        (5,  WEIGHT_FREQUENCY,           FORCE_WEIGHT_FREQUENCY,           CURVE_WEIGHT_FREQUENCY),
        (6,  WEIGHT_AZIMUTH,             FORCE_WEIGHT_AZIMUTH,             CURVE_WEIGHT_AZIMUTH),
        (7,  WEIGHT_ELEVATION,          FORCE_WEIGHT_ELEVATION,          CURVE_WEIGHT_ELEVATION),
        (8,  WEIGHT_TYPE_GLISS,          FORCE_WEIGHT_TYPE_GLISS,          CURVE_WEIGHT_TYPE_GLISS),
        (9,  WEIGHT_TYPE_ENV,            FORCE_WEIGHT_TYPE_ENV,            CURVE_WEIGHT_TYPE_ENV),
        (10, WEIGHT_TYPE_MOV_AMB,        FORCE_WEIGHT_TYPE_MOV_AMB,        CURVE_WEIGHT_TYPE_MOV_AMB),
        (11, WEIGHT_TYPE_PROX_AMB,       FORCE_WEIGHT_TYPE_PROX_AMB,       CURVE_WEIGHT_TYPE_PROX_AMB),
        (12, WEIGHT_FREQ_MOD,            FORCE_WEIGHT_FREQ_MOD,            CURVE_WEIGHT_FREQ_MOD),
        (13, WEIGHT_FREQ_AMP,            FORCE_WEIGHT_FREQ_AMP,            CURVE_WEIGHT_FREQ_AMP),
        (14, WEIGHT_PROX_AMP,            FORCE_WEIGHT_PROX_AMP,            CURVE_WEIGHT_PROX_AMP),
        (15, WEIGHT_PROB_GLISSANDO,       FORCE_WEIGHT_PROB_GLISSANDO,       CURVE_WEIGHT_PROB_GLISSANDO),
        (16, WEIGHT_PROB_SPATIAL_MOVE,   FORCE_WEIGHT_PROB_SPATIAL_MOVE,   CURVE_WEIGHT_PROB_SPATIAL_MOVE),
        # Rings
        (17, PESO_RINGS_AZ,           FORZA_PESO_RINGS_AZ,           CURVATURA_PESO_RINGS_AZ),
        (18, PESO_RINGS_EL,           FORZA_PESO_RINGS_EL,           CURVATURA_PESO_RINGS_EL),
        # REN 2D
        # Niche onset
        (20, WEIGHT_NICHE_ONSET,       FORCE_WEIGHT_NICHE_ONSET,       CURVE_WEIGHT_NICHE_ONSET),
        (21, WEIGHT_NICHE_FADE_IN,     FORCE_WEIGHT_NICHE_FADE_IN,     CURVE_WEIGHT_NICHE_FADE_IN),
        # Round 2 — new dimensions
        (1,  WEIGHT_ONSET,               FORCE_WEIGHT_ONSET,               CURVE_WEIGHT_ONSET),
        (22, WEIGHT_FREQ_END,            FORCE_WEIGHT_FREQ_END,            CURVE_WEIGHT_FREQ_END),
        (23, WEIGHT_AZ_END,              FORCE_WEIGHT_AZ_END,              CURVE_WEIGHT_AZ_END),
        (24, WEIGHT_EL_END,              FORCE_WEIGHT_EL_END,              CURVE_WEIGHT_EL_END),
        (25, WEIGHT_FREQ_MOD1,           FORCE_WEIGHT_FREQ_MOD1,           CURVE_WEIGHT_FREQ_MOD1),
        (26, WEIGHT_FREQ_MOD2,           FORCE_WEIGHT_FREQ_MOD2,           CURVE_WEIGHT_FREQ_MOD2),
        (27, WEIGHT_FREQ_AMP1,           FORCE_WEIGHT_FREQ_AMP1,           CURVE_WEIGHT_FREQ_AMP1),
        (28, WEIGHT_FREQ_AMP2,           FORCE_WEIGHT_FREQ_AMP2,           CURVE_WEIGHT_FREQ_AMP2),
    ])

def _build_pesi(lista):
    """
    Costruisce il dizionario dei pesi per dimensione.
    Accetta peso = 0.0 (centro). Attiva solo se forza > eps.
    """
    return {d: (float(p), float(f), float(c)) 
            for d, p, f, c in lista if f > 1e-6}

def applica_pesi_1d(dim_1d, pesi_dims):
    """
    Modifica i pesi di ogni dimensione indipendentemente.
    Introduce hard-clamp deterministico per forza >= 0.99.
    """
    result = {d: dict(dim) for d, dim in dim_1d.items()}
    for d, dim in result.items():
        result[d]['weights'] = dim['weights'].copy()

    for dim_idx, (peso, forza, curv) in pesi_dims.items():
        if dim_idx not in result:
            continue
        dim = result[dim_idx]
        n = len(dim['weights'])
        centers = (dim['mins'] + dim['maxs']) / 2.0
        c_min, c_max = centers.min(), centers.max()
        span = c_max - c_min

        # Hard clamp legacy per probabilità
        if dim_idx in (15, 16) and forza >= 1.0:
            w = np.zeros(n)
            if peso <= -1.0: w[np.argmin(centers)] = 1.0
            else:            w[np.argmax(centers)] = 1.0
            result[dim_idx]['weights'] = w
            continue

        if span < 1e-10:
            continue

        fn_norm = (centers - c_min) / span
        target  = (peso + 1.0) / 2.0
        dist    = np.abs(fn_norm - target)

        # ✅ PATCH: Selezione deterministica a cella singola per forza >= 0.99
        if forza >= 0.99:
            idx_sel = int(np.argmin(dist))  # Risolve le parità prendendo l'indice minore
            new_w = np.zeros(n)
            new_w[idx_sel] = 1.0
            result[dim_idx]['weights'] = new_w
            continue

        # Comportamento graduale per forza < 0.99
        fn_c = np.clip(1.0 - dist, 0.0, 1.0) ** curv
        mx = fn_c.max()
        if mx > 1e-10:
            fn_c /= mx
        else:
            fn_c = np.zeros(n)
            fn_c[np.argmin(dist)] = 1.0

        new_w = dim['weights'] * (fn_c * forza + (1.0 - forza))
        if new_w.sum() < 1e-10:
            new_w = np.ones(n) / n
        else:
            new_w /= new_w.sum()
            
        result[dim_idx]['weights'] = new_w

    return result

# ═══════════════════════════════════════════════════════════════
# CAMPIONAMENTO EVENTO
# ═══════════════════════════════════════════════════════════════
def _stringe(lo, hi, larghezza):
    """Applica larghezza a un range [lo,hi] stringendo verso il centro."""
    if larghezza >= 1.0:
        return lo, hi
    center = (lo + hi) / 2.0
    half   = (hi - lo) / 2.0 * larghezza
    return center - half, center + half

def _campiona_dim(dim, rng, larghezza=1.0, beta_interna=0.0, liberta=0.0):
    """Campiona un valore da una distribuzione 1D pesata.
    larghezza    [0,1]  : stringe il range verso il centro della cella
    beta_interna [-1,1] : forma distribuzione intra-cella
    liberta      [0,1]  : espande il range oltre la cella verso il range globale
    """
    w = dim['weights']
    s = w.sum()
    if s < 1e-10:
        r = rng.integers(len(w))
    else:
        r = rng.choice(len(w), p=w / s)
    lo, hi = float(dim['mins'][r]), float(dim['maxs'][r])
    # Applica larghezza: stringe il range verso il centro della cella
    if larghezza < 1.0:
        center = (lo + hi) / 2.0
        half   = (hi - lo) / 2.0 * larghezza
        lo, hi = center - half, center + half
    # Applica liberta': espande il range verso il range globale
    if liberta > 0.0:
        lo_g = float(dim['mins'].min())
        hi_g = float(dim['maxs'].max())
        lo = lo * (1.0 - liberta) + lo_g * liberta
        hi = hi * (1.0 - liberta) + hi_g * liberta
    # Campionamento intra-cella con distribuzione configurabile
    if abs(beta_interna) < 1e-6:
        val = float(rng.uniform(lo, hi))
    else:
        # Beta(alpha, alpha): >1=campana (centro), <1=U (bordi)
        alpha = float(np.clip(1.0 + beta_interna, 0.05, 10.0))
        u = float(rng.beta(alpha, alpha))
        val = lo + u * (hi - lo)
    if dim['log']:
        val = 10.0 ** val
    return val, r  # valore fisico + indice regione

def ren_2d(az, el, az_c, el_c, raggio, k, m, lam1, lam2, q, p):
    """Formula REN 2D sulla sfera. Restituisce valore in [0,1]."""
    daz = az - az_c
    del_ = el - el_c
    # Normalizza rispetto al raggio
    tnorm_az = daz / max(raggio, 1e-6)
    tnorm_el = del_ / max(raggio, 1e-6)
    r = np.exp(-lam1 * abs(np.sin(k * tnorm_az)) ** q
               -lam2 * abs(np.cos(m * tnorm_el)) ** p)
    return float(r)

def _campiona_ren_2d(n_nicchie, rng, gs):
    """Genera N centri REN accoppiati (az, el) con repulsione sferica.

    FREEDOM_REN_RELAXATION [0,1]:
      0.0 = rilassamento pieno (centri equidistanti sulla sfera)
      1.0 = nessun rilassamento (centri casuali puri)

    FREEDOM_REN_RADIUS [0,1]:
      0.0 = raggio scalato automaticamente per evitare sovrapposizioni
      1.0 = use REN_RAGGIO_RANGE without correction
    """
    # Campionamento iniziale uniforme su S2
    pts = []
    for _ in range(n_nicchie):
        u  = rng.uniform(-1, 1)
        el = float(np.arcsin(u))
        az = float(rng.uniform(-np.pi, np.pi))
        pts.append([el, az])   # [el, az] in coordinate sferiche

    # Rilassamento repulsivo su S2 vera con proiezione tangente e passo adattivo
    # Il rilassamento opera su vettori 3D sulla sfera, non su coordinate piatte
    lib_ril = float(gs.get('liberta_rilassamento_ren', 0.0))
    n_iter  = int(round(200 * (1.0 - lib_ril)))  # 0=200 iter, 1.0=0 iter
    step    = 0.3
    for _ in range(n_iter):
        # Converti in 3D
        xyz = []
        for el, az in pts:
            x = np.cos(el)*np.cos(az)
            y = np.cos(el)*np.sin(az)
            z = np.sin(el)
            xyz.append([x, y, z])
        new_pts = []
        for i in range(n_nicchie):
            xi, yi, zi = xyz[i]
            fx, fy, fz = 0.0, 0.0, 0.0
            for j in range(n_nicchie):
                if i == j: continue
                dx = xi-xyz[j][0]; dy = yi-xyz[j][1]; dz = zi-xyz[j][2]
                dist2 = dx**2 + dy**2 + dz**2 + 1e-8
                fx += dx/dist2; fy += dy/dist2; fz += dz/dist2
            # Project onto tangent plane (remove radial component)
            dot = fx*xi + fy*yi + fz*zi
            fx -= dot*xi; fy -= dot*yi; fz -= dot*zi
            # Move and renormalize on S2
            nx = xi + step*fx; ny = yi + step*fy; nz = zi + step*fz
            norm = np.sqrt(nx**2 + ny**2 + nz**2)
            if norm < 1e-10: norm = 1.0
            nx /= norm; ny /= norm; nz /= norm
            new_el = float(np.arcsin(np.clip(nz, -1.0, 1.0)))
            new_az = float(np.arctan2(ny, nx))
            new_pts.append([new_el, new_az])
        pts  = new_pts
        step *= 0.98  # decreasing step

    centers = [[float(np.clip(az, -np.pi, np.pi)), float(np.clip(el, -np.pi/2, np.pi/2))]
               for el, az in pts]  # convert back to [az, el]

    # REN az/el center bias
    def _applica_bias_ren(vals, v_min, v_max, bias_params):
        peso, forza, curv = bias_params
        if forza <= 0.0 or peso == 0.0:
            return vals
        span = v_max - v_min
        if span < 1e-10:
            return vals
        target = v_max if peso > 0 else v_min
        result = []
        for v in vals:
            fn = ((v - v_min) / span) if peso > 0 else (1.0 - (v - v_min) / span)
            fn_c = float(np.clip(fn, 0.0, 1.0)) ** curv
            result.append(float(v + (target - v) * forza * fn_c))
        return result

    azs = _applica_bias_ren([c[0] for c in centers], -np.pi,   np.pi,   gs.get('ren_az_bias', (0,0,1)))
    els = _applica_bias_ren([c[1] for c in centers], -np.pi/2, np.pi/2, gs.get('ren_el_bias', (0,0,1)))
    centers = [[float(np.clip(a, -np.pi, np.pi)), float(np.clip(e, -np.pi/2, np.pi/2))]
               for a, e in zip(azs, els)]

    # Radius: auto-scaled with FREEDOM_REN_RADIUS
    # r_auto ~ pi/sqrt(N) = guaranteed average distance between N points on S2
    r_min_user, r_max_user = gs.get('ren_raggio_range', (0.1, np.pi/2))
    lib_r   = float(gs.get('liberta_ren_raggio', 0.0))
    r_auto  = float(np.pi / max(np.sqrt(n_nicchie), 1.0))
    r_max_eff = r_auto       * (1.0 - lib_r) + r_max_user * lib_r
    r_min_eff = r_auto * 0.3 * (1.0 - lib_r) + r_min_user * lib_r
    radii = [float(rng.uniform(r_min_eff, r_max_eff)) for _ in range(n_nicchie)]
    
    # Returns the unified structure
    # Adds empty keys for compatibility with _sample_dim if called by mistake
    # Computes r_circle = half minimum distance between centers (spherical distance)
    # Saved in structure so magnet and visualizer use the same value
    def _dsf(a1,e1,a2,e2):
        x1=np.cos(e1)*np.cos(a1); y1=np.cos(e1)*np.sin(a1); z1=np.sin(e1)
        x2=np.cos(e2)*np.cos(a2); y2=np.cos(e2)*np.sin(a2); z2=np.sin(e2)
        return float(np.arccos(np.clip(x1*x2+y1*y2+z1*z2,-1.0,1.0)))
    if n_nicchie > 1:
        min_d = min(_dsf(centers[i][0],centers[i][1],centers[j][0],centers[j][1])
                    for i in range(n_nicchie) for j in range(i+1,n_nicchie))
    else:
        min_d = np.pi / 2.0
    r_cerchio = min_d * 0.45
    # Radii are capped in _add_derived accounting for FREEDOM_REN_RADIUS

    return {
        'centers':  centers,
        'radii':    radii,
        'r_cerchio': r_cerchio,
        'weights':  np.ones(n_nicchie) / n_nicchie,
        'mins':     np.zeros(n_nicchie),
        'maxs':     np.zeros(n_nicchie),
        'log':      False
    }

def _aggiunge_derived(ev, dim_1d, gs, rng, rng_per_dim=None):
    # Use per-dimension RNG where available, fall back to global rng
    def _rng(d): return rng_per_dim[d] if rng_per_dim and d in rng_per_dim else rng
    # 1. freq_end — respects FREEDOM_FREQ_END and prob_gliss
    freq_c  = ev['freq_start']
    prob_g  = float(ev.get('_prob_gliss', 0.0))
    if rng.random() >= prob_g:
        ev['freq_end'] = freq_c  # No glissando: end = start
    else:
        # Glissando: sample freq_end within freq_start cell
        # expanding toward global range based on FREEDOM_FREQ_END
        L       = float(gs.get('liberta_freq_end', 0.0))
        f_lo    = float(ev.get('freq_min', freq_c))
        f_hi    = float(ev.get('freq_max', freq_c))
        if L > 0.0:
            g_lo, g_hi = gs['freq_range']
            f_lo = f_lo * (1.0 - L) + g_lo * L
            f_hi = f_hi * (1.0 - L) + g_hi * L
        f_lo, f_hi = _stringe(f_lo, f_hi, float(gs.get('larghezza', 1.0)))
        ev['freq_end'] = float(_rng(22).uniform(f_lo, f_hi))

    # 2. az_end / el_end — respects FREEDOM_AZ/EL_END and prob_mov
    az0    = ev['az']
    el0    = ev['el']
    prob_m = float(ev.get('_prob_mov', 0.0))
    if rng.random() >= prob_m:
        az_end = az0
        el_end = el0
    else:
        La = float(gs.get('liberta_az_end', 0.0))
        Le = float(gs.get('liberta_el_end', 0.0))
        az_lo = float(ev.get('az_min', -np.pi));  az_hi = float(ev.get('az_max', np.pi))
        el_lo = float(ev.get('el_min', -np.pi/2)); el_hi = float(ev.get('el_max', np.pi/2))
        if La > 0.0:
            az_lo = az_lo * (1.0 - La) + (-np.pi)   * La
            az_hi = az_hi * (1.0 - La) + ( np.pi)   * La
        if Le > 0.0:
            el_lo = el_lo * (1.0 - Le) + (-np.pi/2) * Le
            el_hi = el_hi * (1.0 - Le) + ( np.pi/2) * Le
        lw = float(gs.get('larghezza', 1.0))
        az_lo, az_hi = _stringe(az_lo, az_hi, lw)
        el_lo, el_hi = _stringe(el_lo, el_hi, lw)
        az_end = float(_rng(23).uniform(az_lo, az_hi))
        el_end = float(_rng(24).uniform(el_lo, el_hi))

    # 3. Rings — uses region already sampled by GIGP (with bias applied)
    #    _r19 / _r17 are cell indices chosen during sampling
    #    and already reflect weights/bias — we do NOT search where current event falls
    if gs.get('anelli_el_attivi', False) and 18 in dim_1d:
        r_el = int(ev.get('_r18', 0))
        em, eM = dim_1d[18]['mins'], dim_1d[18]['maxs']
        _el_lo, _el_hi = _stringe(em[r_el], eM[r_el], float(gs.get('larghezza', 1.0)))
        el0    = float(_rng(7).uniform(_el_lo, _el_hi))
        el_end = float(_rng(24).uniform(_el_lo, _el_hi))
        ev['el_band_idx'] = r_el

    if gs.get('anelli_az_attivi', False) and 17 in dim_1d:
        r_az = int(ev.get('_r17', 0))
        am, aM = dim_1d[17]['mins'], dim_1d[17]['maxs']
        _az_lo, _az_hi = _stringe(am[r_az], aM[r_az], float(gs.get('larghezza', 1.0)))
        az0    = float(rng.uniform(_az_lo, _az_hi))
        az_end = float(rng.uniform(_az_lo, _az_hi))
        ev['az_band_idx'] = r_az

    # 4. REN 2D — Circle assignment + Magnet + Guaranteed clamp
    #    1. Each event belongs to nearest circle (spherical distance)
    #    2. The magnet attracts toward the REN flower lobes of the niche
    #    3. With force=1.0 the final clamp guarantees the event stays inside
    forza = float(gs.get('forza_ren_2d', 0.0))
    if forza > 0.0 and 19 in dim_1d and 'centers' in dim_1d[19]:
        rd      = dim_1d[19]
        centers = rd['centers']
        radii   = rd['radii']
        k       = int(gs.get('ren_k', 5))
        lam     = float(gs.get('ren_lambda', 2.0))
        q_val   = float(gs.get('ren_q', 2.0))

        # ── Base functions ────────────────────────────────────────────────────
        def _dist_sferica_3d(az1, el1, az2, el2):
            x1=np.cos(el1)*np.cos(az1); y1=np.cos(el1)*np.sin(az1); z1=np.sin(el1)
            x2=np.cos(el2)*np.cos(az2); y2=np.cos(el2)*np.sin(az2); z2=np.sin(el2)
            return float(np.arccos(np.clip(x1*x2+y1*y2+z1*z2, -1.0, 1.0)))

        def _base_gnomonica(c_az, c_el):
            cos_el_c, sin_el_c = np.cos(c_el), np.sin(c_el)
            cos_az_c, sin_az_c = np.cos(c_az), np.sin(c_az)
            C    = np.array([cos_el_c*cos_az_c, cos_el_c*sin_az_c, sin_el_c])
            e_az = np.array([-sin_az_c, cos_az_c, 0.0])
            e_el = np.array([-sin_el_c*cos_az_c, -sin_el_c*sin_az_c, cos_el_c])
            return C, e_az, e_el

        def _proietta(az_p, el_p, C, e_az, e_el):
            P   = np.array([np.cos(el_p)*np.cos(az_p),
                            np.cos(el_p)*np.sin(az_p), np.sin(el_p)])
            vec = P - C
            dx  = float(np.dot(vec, e_az))
            dy  = float(np.dot(vec, e_el))
            r   = np.sqrt(dx*dx + dy*dy)
            phi = float(np.arctan2(dy, dx)) if r > 1e-8 else 0.0
            return dx, dy, r, phi

        def _ren_val(phi):
            return float(np.exp(-lam * abs(np.sin(k * phi / 2.0)) ** q_val))

        def _riproietta(r_fin, phi, C, e_az, e_el, az_orig, el_orig):
            offset = r_fin * np.cos(phi) * e_az + r_fin * np.sin(phi) * e_el
            P_new  = C + offset
            n      = np.linalg.norm(P_new)
            if n < 1e-10: return az_orig, el_orig
            P_new /= n
            return (float(np.arctan2(P_new[1], P_new[0])),
                    float(np.arcsin(np.clip(P_new[2], -1.0, 1.0))))

        # ── Assignment: nearest circle ───────────────────────────────────────
        # r_circle already computed in _sample_ren_2d and saved in structure
        r_cerchio = float(rd.get('r_cerchio', np.pi / 2.0))
        dists = [_dist_sferica_3d(az0, el0, c[0], c[1]) for c in centers]
        idx   = int(np.argmin(dists))

        c_az, c_el = centers[idx]
        lib_r  = float(gs.get('liberta_ren_raggio', 0.0))
        r_raw  = float(radii[idx])
        r_cap  = r_cerchio * (1.0 - lib_r) + r_raw * lib_r
        r_mask = min(r_raw, r_cap)
        C, e_az, e_el = _base_gnomonica(c_az, c_el)

        def _applica_magnete(az_curr, el_curr):
            _, _, r_curr, phi = _proietta(az_curr, el_curr, C, e_az, e_el)
            if r_curr < 1e-8:
                return az_curr, el_curr
            # REN boundary at this angle
            r_ren    = r_mask * _ren_val(phi)
            r_target = min(r_curr, r_ren)
            r_final  = r_curr * (1.0 - forza) + r_target * forza
            return _riproietta(r_final, phi, C, e_az, e_el, az_curr, el_curr)

        def _clamp_dentro_fiore(az_v, el_v):
            """Guarantees the event stays INSIDE the flower.
            If outside, projects it onto the nearest lobe border."""
            _, _, r_v, phi_v = _proietta(az_v, el_v, C, e_az, e_el)
            r_ren = r_mask * _ren_val(phi_v)
            if r_v <= r_ren + 1e-6:
                return az_v, el_v  # already inside
            # Find nearest lobe (phi where sin(k*phi/2)=0)
            phi_lobi = [2.0 * np.pi * n / k for n in range(k)]
            phi_near = min(phi_lobi, key=lambda p: abs(
                np.arctan2(np.sin(phi_v - p), np.cos(phi_v - p))))
            r_lobo  = r_mask * _ren_val(phi_near)
            r_final = min(r_v, r_lobo * 0.99)
            return _riproietta(r_final, phi_near, C, e_az, e_el, az_v, el_v)

        # Apply magnet
        az0,    el0    = _applica_magnete(az0,    el0)
        az_end, el_end = _applica_magnete(az_end, el_end)

        # Guaranteed final clamp — with force=1.0 no event exits the flower
        if forza > 0.99:
            az0,    el0    = _clamp_dentro_fiore(az0,    el0)
            az_end, el_end = _clamp_dentro_fiore(az_end, el_end)

        ev['ren_region'] = idx

    # 5. Serialization
    ev['az']     = az0
    ev['el']     = el0
    ev['az_end'] = az_end
    ev['el_end'] = el_end


    # 6. FM, Gain
    ev['ren3d_scale'] = 1.0

    # FM: freq_mod1/2 and freq_amp1/2 — respects freedom and parent cell
    liberta_dict = gs.get('liberta', {})

    def _campiona_end_dim(base_val, min_key, max_key, global_range, liberta, dim_idx):
        lo = float(ev.get(min_key, base_val))
        hi = float(ev.get(max_key, base_val))
        if liberta > 0.0:
            g_lo, g_hi = global_range
            lo = lo * (1.0 - liberta) + g_lo * liberta
            hi = hi * (1.0 - liberta) + g_hi * liberta
        lo, hi = _stringe(lo, hi, float(gs.get('larghezza', 1.0)))
        return float(np.clip(_rng(dim_idx).uniform(lo, hi), global_range[0], global_range[1]))

    fm_range  = gs.get('freq_mod_range', (0.01, 1000.0))
    fam_range = gs.get('freq_amp_range', (0.0, 10000.0))

    ev['freq_mod1'] = _campiona_end_dim(
        ev.get('freq_mod', 1.0), 'freq_mod_min', 'freq_mod_max',
        fm_range, float(liberta_dict.get(25, 0.0)), 25)
    ev['freq_mod2'] = _campiona_end_dim(
        ev.get('freq_mod', 1.0), 'freq_mod_min', 'freq_mod_max',
        fm_range, float(liberta_dict.get(26, 0.0)), 26)
    ev['freq_amp1'] = _campiona_end_dim(
        ev.get('freq_amp', 0.0), 'freq_amp_min', 'freq_amp_max',
        fam_range, float(liberta_dict.get(27, 0.0)), 27)
    ev['freq_amp2'] = _campiona_end_dim(
        ev.get('freq_amp', 0.0), 'freq_amp_min', 'freq_amp_max',
        fam_range, float(liberta_dict.get(28, 0.0)), 28)

    ev['type_freq_mod'] = float(np.clip(gs['type_freq_mod'] * (1 - gs['forza_type_freq_mod'])
                                        + (0.1 + _rng(14).random() * 9.9) * gs['forza_type_freq_mod'], 0.1, 10.0))
    ev['type_freq_amp'] = float(np.clip(gs['type_freq_amp'] * (1 - gs['forza_type_freq_amp'])
                                        + (0.1 + rng.random() * 9.9) * gs['forza_type_freq_amp'], 0.1, 10.0))

    comp = compensazione_isofonica(ev['freq_start'], gs['min_iso'])
    ev['amp_gain'] = float(gs['master_gain']) * (comp + (1.0 - comp) * gs['comp_iso']) * ev['ren3d_scale']

def genera_tutti_eventi_1d(dim_1d, n_eventi, gs, rng):
    """
    Genera n_eventi campionando ogni dimensione indipendentemente.
    Non esistono più nicchie multi-D: ogni dimensione ha la sua distribuzione.
    """
    eventi = []
    larghezza_global = float(gs.get('larghezza', 1.0))
    larghezza_per_dim = gs.get('larghezza_per_dim', {})
    liberta_dict = gs.get('liberta', {})
    # Internal beta per dimension from CONFIGS_GIGP_INTERNAL
    configs_interna = gs.get('configs_interna', None)
    def _get_beta_interna(d_idx):
        if configs_interna is None:
            return 0.0
        if isinstance(configs_interna, list):
            if len(configs_interna) == 0:
                return 0.0
            # If list is shorter than number of dimensions,
            # use beta from first element as global default
            if d_idx < len(configs_interna):
                return float(getattr(configs_interna[d_idx], 'beta', 0.0))
            return float(getattr(configs_interna[0], 'beta', 0.0))
        return float(getattr(configs_interna, 'beta', 0.0))

    # Per-dimension RNG — guarantees each dimension is independent
    # Removing/adding active dimensions does not affect others.
    seed_base = gs.get('seed', 42)
    rng_per_dim = {d: np.random.default_rng(seed_base * 1000 + d)
                   for d in DIM_DEFS.keys()}

    for ev_idx in range(n_eventi):
        ev = {}

        for d, (ev_key, _, is_log) in DIM_DEFS.items():
            rng_d = rng_per_dim[d]  # RNG dedicated to this dimension

            # Dim 19 (REN 2D): handle specially because unified
            if d == 19:
                rd = dim_1d[d]
                if 'centers' in rd:
                    r_idx = rng_d.integers(len(rd['centers']))
                    ev[ev_key] = rd['centers'][r_idx][0]
                    ev[f'_r{d}'] = r_idx
                continue

            # Dims 22-28 are end/FM — handled entirely in _add_derived
            if d in (22, 23, 24, 25, 26, 27, 28):
                continue

            larghezza = larghezza_per_dim.get(d, larghezza_global)
            beta_int  = _get_beta_interna(d)
            liberta   = float(liberta_dict.get(d, 0.0))
            val, r_idx = _campiona_dim(dim_1d[d], rng_d, larghezza=larghezza,
                                       beta_interna=beta_int, liberta=liberta)
            ev[ev_key] = val
            ev[f'_r{d}'] = r_idx  # region index for each dimension

            # Save region bounds (useful for FM clamping and visualizer)
            if d == 5:  # frequency
                ev['freq_min'] = float(dim_1d[d]['mins'][r_idx])
                ev['freq_max'] = float(dim_1d[d]['maxs'][r_idx])
                ev['freq_region'] = r_idx
            elif d == 2:  # amplitude
                ev['amp_min'] = float(dim_1d[d]['mins'][r_idx])
                ev['amp_max'] = float(dim_1d[d]['maxs'][r_idx])
                ev['amp_region'] = r_idx
            elif d == 4:  # n_sinusoids
                ev['n_sin_min'] = float(dim_1d[d]['mins'][r_idx])
                ev['n_sin_max'] = float(dim_1d[d]['maxs'][r_idx])
            elif d == 6:  # azimuth
                ev['az_min'] = float(dim_1d[d]['mins'][r_idx])
                ev['az_max'] = float(dim_1d[d]['maxs'][r_idx])
            elif d == 7:  # elevation
                ev['el_min'] = float(dim_1d[d]['mins'][r_idx])
                ev['el_max'] = float(dim_1d[d]['maxs'][r_idx])
            elif d == 12:  # freq_mod
                ev['freq_mod_min'] = float(dim_1d[d]['mins'][r_idx])
                ev['freq_mod_max'] = float(dim_1d[d]['maxs'][r_idx])
            elif d == 13:  # freq_amp
                ev['freq_amp_min'] = float(dim_1d[d]['mins'][r_idx])
                ev['freq_amp_max'] = float(dim_1d[d]['maxs'][r_idx])
            elif d == 1:  # onset — clamp to valid range
                ev['onset'] = float(np.clip(val, 0.0, TOTAL_DURATION * 0.95))

        # Rhythmic structure on onset (jitter su griglia se RHYTHMIC_STRUCTURE > 0)
        sr = gs.get('struttura', 0.0)
        if sr > 0.01:
            # Snap to nearest grid point and apply reduced jitter
            # cell_w = BEAT_DURATION — grid repeats every BEAT_DURATION seconds
            o_raw   = float(ev.get('onset', 0.0))
            span    = TOTAL_DURATION * 0.92
            cell_w  = float(gs.get('durata_cellula', 2.0))
            grid_pt = round(o_raw / cell_w) * cell_w
            jitter  = cell_w * (1.0 - sr) * 0.5
            ev['onset'] = float(np.clip(grid_pt + rng.uniform(-jitter, jitter), 0.0, span))

        # n_sinusoids must be integer — ricalcola _r4 sul valore intero finale
        n_sin_int = int(np.clip(round(ev['n_sinusoidi']), N_SIN_MIN, N_SIN_MAX))
        ev['n_sinusoidi'] = n_sin_int
        # Update _r4: find the cell containing the integer value
        if 4 in dim_1d:
            d4 = dim_1d[4]
            for ri in range(len(d4['mins'])):
                if d4['mins'][ri] <= n_sin_int <= d4['maxs'][ri]:
                    ev['_r4'] = ri
                    ev['n_sin_min'] = float(d4['mins'][ri])
                    ev['n_sin_max'] = float(d4['maxs'][ri])
                    break

        # Duration variability
        vr = gs.get('variabilita', 0.0)
        if vr > 0.0:
            dmn, dmx = gs['durata_range']
            ev['durata'] = float(np.clip(
                ev['durata'] + (rng.random() * 2 - 1) * vr * ev['durata'], dmn, dmx))

        # Derived parameters (freq_end, az_end, FM, etc.)
        _aggiunge_derived(ev, dim_1d, gs, rng, rng_per_dim=rng_per_dim)

        # FM clamp
        if ev.get('freq_amp', 0) > 0:
            freq_c   = ev['freq_start']
            f_min_n  = ev.get('freq_min', freq_c)
            f_max_n  = ev.get('freq_max', freq_c)
            max_dev  = max(0.0, min(freq_c - f_min_n, f_max_n - freq_c))
            Lfm      = float(gs.get('liberta_fm', 0.0))
            max_dev_g = float(gs['freq_amp_range'][1])
            max_dev_f = max_dev * (1.0 - Lfm) + max_dev_g * Lfm
            ev['freq_amp'] = min(ev['freq_amp'], max_dev_f)

        # Niche onset — only if active
        if gs.get('niche_onset_attivo', False):
            n_onset = ev.get('niche_onset', 0.0)
            if ev['onset'] < n_onset:
                continue
            if gs.get('niche_fade_in_attivo', False):
                n_fade = ev.get('niche_fade_in', 0.0)
                if n_fade > 0.0 and ev['onset'] < n_onset + n_fade:
                    if rng.random() > (ev['onset'] - n_onset) / n_fade:
                        continue

        eventi.append(ev)

    # Sort by onset (GIGP samples in random order)
    eventi.sort(key=lambda e: e.get('onset', 0.0))
    return eventi

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    os.makedirs(DIR_OUTPUT, exist_ok=True)
    gs  = genera_stato()
    rng = np.random.default_rng(gs['seed'])
    n   = gs['n']
    n_dims = len(DIM_DEFS)
    print("=" * 60)
    print("  Hutchinson Synthesis — 1D Indipendente ")
    print(f"  Regioni/dim: {n} | Durata: {TOTAL_DURATION}s ")
    print("=" * 60)

    # Config per dimension (one per dim)
    configs_voronoi  = _risolvi_configs(CONFIGS_GIGP)         # cell centroids
    configs_nicchie  = _risolvi_configs(CONFIGS_GIGP_NICHES)  # cell selection per event
    configs          = configs_voronoi  # used by calc_voronoi_1d

    # ✅ Diagnostica di verifica kernel/beta per dimensione
    print("\n[Config] Distribution check per dimension: ")
    for d in sorted(configs.keys()):
        cfg = configs[d]
        print(f"  dim {d:2d} ({DIM_DEFS[d][0]:12s}): kernel={cfg.kernel_tipo:<10s} beta={cfg.beta} ")

    # 1. Standard 1D Voronoi (genera 21 come struttura temporanea)
    dim_1d = calc_voronoi_1d(gs, configs_voronoi, n, rng, configs_nicchie=configs_nicchie)

    # 2. Biases/Weights (lavora SOLO su strutture 1D standard, evita KeyError)
    pesi = build_pesi_dimensioni()
    dim_1d = applica_pesi_1d(dim_1d, pesi)

    # 3. Inietta REN 2D unificata (sovrascrive 21 DOPO i pesi)
    dim_1d[19] = _campiona_ren_2d(n, rng, gs)

    # Print main dimension distribution
    print(f"\n[Distribuzioni 1D] {n} regioni per dimensione: ")
    for d in [5, 2, 6, 7]:
        dname = DIM_DEFS[d][0]
        dim   = dim_1d[d]
        w     = dim['weights']
        print(f"  dim {d:2d} ({dname:12s}):  "
              f"[{dim['mins'][0]:.2f} … {dim['maxs'][-1]:.2f}]   "
              f"pesi=[{', '.join(f'{x:.2f}' for x in w)}] ")

    # Total event count calculation
    scala = TOTAL_DURATION / max(REFERENCE_DURATION, 0.001)
    n_eventi = max(1, round(N_EVENTS_PER_NICHE * scala))

    print(f"\n[Main] Generazione {n_eventi} eventi (tutte le dimensioni indipendenti)... ")
    tutti_eventi = genera_tutti_eventi_1d(dim_1d, n_eventi, gs, rng)
    print(f"  → {len(tutti_eventi)} eventi generati ")

    # Minimum duration guarantee
    fine_max = max((e['onset'] + e['durata'] for e in tutti_eventi), default=0.0)
    if fine_max < TOTAL_DURATION:
        e0 = tutti_eventi[0].copy() if tutti_eventi else {}
        e0.update({'onset': TOTAL_DURATION - 0.01, 'durata': 0.01, 'amp': 0.0,
                   'freq_start': 440.0, 'freq_end': 440.0,
                   'az': 0.0, 'el': 0.0, 'az_end': 0.0, 'el_end': 0.0,
                   'perc': 0.5, 'n_sinusoidi': 1})
        tutti_eventi.append(e0)

    print(f"\n[Main] Totale eventi: {len(tutti_eventi)} ")

    genera_csd(tutti_eventi, TOTAL_DURATION, WAV_PATH, CSD_PATH,
               hoa_order=HOA_ORDER, udos_path=os.path.join(os.path.dirname(__file__), 'hoa_udos.udo'))
    if renderizza(CSD_PATH, WAV_PATH):
        if RIPRODUCI_AUDIO:
            riproduci(WAV_PATH)

    if MOSTRA_VISUALIZZAZIONI:
        # For visualizer: group events by freq region (dim 5)
        lista_per_regione = [[] for _ in range(n)]
        for ev in tutti_eventi:
            r = ev.get('freq_region', 0)
            if 0 <= r < n:
                lista_per_regione[r].append(ev)
        
        mostra_tutto(
            lista_per_regione,
            nicchie_info=dim_1d,
            forza_ren_2d=gs['forza_ren_2d'],
            anelli_az_attivi=gs['anelli_az_attivi'],
            anelli_el_attivi=gs['anelli_el_attivi'],
            visualizza_ren_2d=gs['visualizza_ren_2d'],
            # Shape parameters
            ren_k=gs['ren_k'], ren_l=gs['ren_lambda'], ren_q=gs['ren_q'],
            liberta_ren_raggio=gs.get('liberta_ren_raggio', 0.0)
        )

if __name__ == '__main__':
    main()