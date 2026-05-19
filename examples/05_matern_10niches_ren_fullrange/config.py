"""
config.py — Hutchinson Synthesis

Hutchinson space dimensions:
  ── TEMPO ──────────────────────────────
  0  durata
  1  onset
  20 niche_onset
  21 niche_fade_in
  ── AMPIEZZA ───────────────────────────
  2  amp
  3  perc
  9  type_env
  ── FREQUENZA ──────────────────────────
  4  n_sinusoidi
  5  freq_start         / 22 freq_end
  8  type_gliss
  15 prob_glissato
  ── FREQUENZA MODULATA (VIBRATO/FM) ────
  12 freq_mod            / 25 freq_mod1 / 26 freq_mod2
  13 freq_amp            / 27 freq_amp1 / 28 freq_amp2
  ── SPAZIO ─────────────────────────────
  6  az                 / 23 az_end
  7  el                 / 24 el_end
  14 prox_amp
  10 type_mov_amb
  16 prob_mov_spaziale
  11 type_prox_amb
  17 az_band_center
  18 el_band_center
  19 ren_az_center

How biases work:
  peso      [-1,+1]  direction: -1=low values, +1=high values, 0=free
  forza     [0,1]    intensity: 0=free, 1=hard clamp at extreme
  curvatura [>0]     shape: 1000=binary threshold, 2=gradual

How freedom works:
  0.0 = sampling inside the assigned Voronoi cell
  1.0 = free sampling over the full global range
  0.5 = halfway
"""
from gigp import ConfigDimensione, config_preset, gigp

# TODO: GLOBAL PARAMS
# ================================================================
# HOA — ORDINE AMBISONICS
# ================================================================
# HOA order for spatial rendering.
# Output channels = (HOA_ORDER + 1)^2
#   order 1 ->  4 channels (first order B-format)
#   order 2 ->  9 channels
#   order 3 -> 16 channels
#   order 4 -> 25 channels
#   order 5 -> 36 channels
#   order 6 -> 49 channels
#   order 7 -> 64 channels (maximum resolution)
HOA_ORDER = 1

# ================================================================
# PARAMETRI GLOBALI
# ================================================================
NUM_NICHES       = 10
TOTAL_DURATION        = 30.0
REFERENCE_DURATION   = 30.0
N_EVENTS_PER_NICHE = 1000
N_CANDIDATES          = 200
SEED                 = 41


# TODO: DISTRIBUTIONS
# ================================================================
# DISTRIBUZIONI GIGP
# ================================================================
# Three distribution levels:
#   CONFIGS_GIGP         -> position of Voronoi centroids
#   CONFIGS_GIGP_NICHES -> which cell is chosen for each event
#   CONFIGS_GIGP_INTERNAL -> distribution of values INSIDE the cell
#
# Syntax: gigp(lambda_type, beta, kernel)
#
#   lambda_tipo : 'uniforme'     flat density (default)
#                 'lgcp'         dense and sparse zones
#                 'alpha_stable' heavy tails, extreme events
#
#   beta        : -1.0  pure DPP (maximum repulsion)
#                 -0.5  moderate repulsion (beta-ensemble)
#                  0.0  Poisson (no interaction)
#                 +0.5  moderate attraction (beta-ensemble)
#                 +1.0  Permanental (maximum attraction)
#
#   kernel      : None        gaussian kernel (default)
#                 'gaussiano' smooth interaction
#                 'matern'    more regular than gaussian
#                 'strauss'   hard exclusion zone
#                 'hawkes'    self-exciting temporal clustering
#
# Pure distribution examples:
#   gigp('uniforme', beta=0.0,  kernel=None)        # Poisson
#   gigp('uniforme', beta=-1.0, kernel='gaussiano') # DPP
#   gigp('uniforme', beta=-1.0, kernel='matern')    # Matern
#   gigp('uniforme', beta=+1.0, kernel='gaussiano') # Permanental
#   gigp('uniforme', beta=0.0,  kernel='strauss')   # Strauss
#   gigp('uniforme', beta=0.0,  kernel='hawkes')    # Hawkes
#   gigp('lgcp',     beta=0.0,  kernel=None)        # LGCP
#   gigp('alpha_stable', beta=0.0, kernel=None)     # Alpha-Stable

# -- Voronoi cell structure ------------------------------------
CONFIGS_GIGP = gigp('uniforme', beta=-1.0, kernel='matern')
# For specific dimension:
# CONFIGS_GIGP = [
#   gigp('uniforme', beta=-1.0, kernel='matern'),   # 0  durata
#   gigp('uniforme', beta=0.0,  kernel=None),        # 1  onset
#   gigp('uniforme', beta=-1.0, kernel='matern'),   # 2  amp
#   gigp('uniforme', beta=-1.0, kernel='matern'),   # 3  perc
#   gigp('uniforme', beta=-1.0, kernel='matern'),   # 4  n_sinusoidi
#   gigp('uniforme', beta=-1.0, kernel='matern'),   # 5  freq_start
#   gigp('uniforme', beta=-1.0, kernel='matern'),   # 6  az
#   gigp('uniforme', beta=-1.0, kernel='matern'),   # 7  el
#   gigp('uniforme', beta=0.0,  kernel=None),        # 8  type_gliss
#   gigp('uniforme', beta=0.0,  kernel=None),        # 9  type_env
#   gigp('uniforme', beta=0.0,  kernel=None),        # 10 type_mov_amb
#   gigp('uniforme', beta=0.0,  kernel=None),        # 11 type_prox_amb
#   gigp('uniforme', beta=0.0,  kernel=None),        # 12 freq_mod
#   gigp('uniforme', beta=0.0,  kernel=None),        # 13 freq_amp
#   gigp('uniforme', beta=0.0,  kernel=None),        # 14 prox_amp
#   gigp('uniforme', beta=0.0,  kernel=None),        # 15 prob_glissato
#   gigp('uniforme', beta=0.0,  kernel=None),        # 16 prob_mov
#   gigp('uniforme', beta=0.0,  kernel=None),        # 17 az_band_center
#   gigp('uniforme', beta=0.0,  kernel=None),        # 18 el_band_center
#   gigp('uniforme', beta=0.0,  kernel=None),        # 19 ren_az_center
#   gigp('uniforme', beta=0.0,  kernel=None),        # 20 niche_onset
#   gigp('uniforme', beta=0.0,  kernel=None),        # 21 niche_fade_in
#   gigp('uniforme', beta=-1.0, kernel='matern'),   # 22 freq_end
#   gigp('uniforme', beta=-1.0, kernel='matern'),   # 23 az_end
#   gigp('uniforme', beta=-1.0, kernel='matern'),   # 24 el_end
#   gigp('uniforme', beta=0.0,  kernel=None),        # 25 freq_mod1
#   gigp('uniforme', beta=0.0,  kernel=None),        # 26 freq_mod2
#   gigp('uniforme', beta=0.0,  kernel=None),        # 27 freq_amp1
#   gigp('uniforme', beta=0.0,  kernel=None),        # 28 freq_amp2
# ]

# -- Cell selection per event (29 total dimensions) --------
CONFIGS_GIGP_NICHES = gigp('uniforme', beta=-1.0, kernel='matern', n_dims=29)
# Per dimension: same structure as CONFIGS_GIGP above

# -- INTERNAL cell distribution ---------------------------
# beta=-1 = values at cell borders (intra-cell repulsion)
# beta=0  = uniform inside the cell
# beta=+1 = values at cell center (intra-cell clustering)
CONFIGS_GIGP_INTERNAL = gigp('uniforme', beta=0.0, kernel=None)
# Per dimension: same structure as CONFIGS_GIGP above


# TODO: NICHE WIDTH
# ================================================================
# NICHE WIDTH
# ================================================================
# Narrows the sampling range toward the cell center.
# 1.0 = full cell, 0.5 = half, 0.1 = very concentrated
# Global — applies to all dimensions
NICHE_WIDTH = 1.0
# For specific dimension:
WIDTH_PER_DIM = {
  0:  1.0,   # durata
  2:  1.0,   # amp
  5:  0.3,   # freq_start — piu' concentrata
  6:  1.0,   # az
  7:  1.0,   # el
  22: 1.0,   # freq_end
  23: 1.0,   # az_end
  24: 1.0,   # el_end 
}
# (if defined, overrides NICHE_WIDTH for that dimension)

# TODO: TIME
# ================================================================
# DIM 0 — DURATA
# ================================================================
# Event duration range in seconds
EVENT_DURATION_RANGE  = (0.01, 0.3)
# Random jitter applied after sampling [0,1]
# 0.0 = exact duration from cell, 1.0 = +-100% (clamped to range)
DURATION_VARIABILITY   = 1.0
# Sampling freedom relative to Voronoi cell
FREEDOM_DURATION       = 0.0
# Bias on duration distribution
# -1 = short events, +1 = long events
WEIGHT_DURATION            = 0.0
FORCE_WEIGHT_DURATION      = 0.0
CURVE_WEIGHT_DURATION  = 1000.0

# ================================================================
# DIM 1 — ONSET
# ================================================================
# Onsets are sampled by GIGP over (0, TOTAL_DURATION * 0.92)
# Rhythmic structure: quantizes onsets on a grid [0,1]
# 0.0 = free (sound cloud), 1.0 = periodic grid
RHYTHMIC_STRUCTURE    = 0.0
# Rhythmic cell duration in seconds (used if STRUCTURE > 0)
BEAT_DURATION       = 2.0
# Sampling freedom relative to Voronoi cell
FREEDOM_ONSET        = 0.0
# Bias on onset distribution over time
# -1 = events concentrated at start, +1 = at end, 0 = distributed
WEIGHT_ONSET               = 0.0
FORCE_WEIGHT_ONSET         = 0.0
CURVE_WEIGHT_ONSET     = 100.0

# ================================================================
# DIM 20-21 — NICHE ONSET / FADE-IN NICCHIA
# ================================================================
# If False: all events generated normally without temporal filter
NICHE_ONSET_ACTIVE   = False
NICHE_FADE_IN_ACTIVE = False
# Bias niche_onset (dim 20)
WEIGHT_NICHE_ONSET           = 0.0
FORCE_WEIGHT_NICHE_ONSET     = 0.0
CURVE_WEIGHT_NICHE_ONSET  = 100.0
# Bias niche_fade_in (dim 21)
WEIGHT_NICHE_FADE_IN         = 0.0
FORCE_WEIGHT_NICHE_FADE_IN   = 0.0
CURVE_WEIGHT_NICHE_FADE_IN = 100.0

# TODO: AMPLITUDE
# ================================================================
# DIM 2 — AMPLITUDE
# ================================================================
# Master gain applied to all events
MASTER_GAIN             = 0.1
# Isophonic compensation [0,1]: 0=none, 1=full
ISOPHONIC_COMPENSATION = 0.0
ISOPHONIC_MINIMUM        = 0.05
# Global normalized amplitude range
AMP_RANGE_GLOBAL       = (0.02, 0.4)
# Sampling freedom relative to Voronoi cell
FREEDOM_AMP            = 0.0
# Bias
# -1 = quieter niches, +1 = louder niches
WEIGHT_AMPLITUDE          = 0.0
FORCE_WEIGHT_AMPLITUDE    = 0.0
CURVE_WEIGHT_AMPLITUDE= 100.0

# ================================================================
# DIM 3 — PERC (posizione picco inviluppo)
# ================================================================
# Range [0,1]: 0=percussive, 0.5=symmetric, 1=swelling
PERC_RANGE = (0.01, 0.9)
PERC_BIAS  = 0.5   # fallback without Voronoi
# Sampling freedom
FREEDOM_PERC           = 0.0
# Bias
# -1 = more percussive, +1 = more sustained
WEIGHT_PERC              = 0.0
FORCE_WEIGHT_PERC        = 0.0
CURVE_WEIGHT_PERC    = 1000.0

# ================================================================
# DIM 9 — TYPE INVILUPPO
# ================================================================
TYPE_ENV_RANGE       = (0.1, 10.0)
FORCE_TYPE_ENV       = 0.0   # fallback
# Sampling freedom
FREEDOM_TYPE_ENV     = 0.0
# Bias
# -1 = log (fast attacks), +1 = exponential (slow attacks)
WEIGHT_TYPE_ENV          = 0.0
FORCE_WEIGHT_TYPE_ENV    = 0.0
CURVE_WEIGHT_TYPE_ENV = 100.0

# TODO: FREQUENCY
# ================================================================
# DIM 5 — FREQUENZA START  |  DIM 22 — FREQ END
# ================================================================
FREQ_RANGE_GLOBAL  = (100.0, 10000.0)
FREQ_SCALE     = 0.0   # slope (non-Matern branch only)
# freq_start freedom relative to cell
FREEDOM_FREQ_START   = 0.0
# freq_end freedom relative to freq_start cell
# 0.0 = glissando within niche, 1.0 = free over full range
FREEDOM_FREQ_END     = 0.1
# Bias freq_start
# -1 = niches in low frequencies, +1 = high
WEIGHT_FREQUENCY         = -1.0
FORCE_WEIGHT_FREQUENCY   = 1.0
CURVE_WEIGHT_FREQUENCY = 100.0
# Bias freq_end (dim 22)
# -1 = glissando toward low, +1 = toward high
WEIGHT_FREQ_END            = 0.0
FORCE_WEIGHT_FREQ_END      = 0.0
CURVE_WEIGHT_FREQ_END  = 100.0

# ================================================================
# DIM 8 — TYPE GLISSANDO
# ================================================================
# Curvature range: 0.1=log, 1.0=linear, 10.0=exponential
TYPE_GLISS_RANGE     = (0.1, 10.0)
# Sampling freedom
FREEDOM_TYPE_GLISS   = 0.0
# Bias
# -1 = log (starts fast, slows), +1 = exponential (starts slow, accelerates)
WEIGHT_TYPE_GLISS        = 0.0
FORCE_WEIGHT_TYPE_GLISS  = 0.0
CURVE_WEIGHT_TYPE_GLISS = 1000.0

# ================================================================
# DIM 15 — PROBABILITY GLISSATO
# ================================================================
# Bias
# -1 = no glissando, +1 = all always glissando
# FORCE=1.0 = guaranteed hard clamp
WEIGHT_PROB_GLISSANDO          = 0.0
FORCE_WEIGHT_PROB_GLISSANDO    = 0.0
CURVE_WEIGHT_PROB_GLISSANDO = 100.0

# ================================================================
# DIM 4 — N. SINUSOIDI
# ================================================================
N_SIN_MIN   = 1
N_SIN_MAX   = 6
# Sampling freedom
FREEDOM_N_SIN          = 0.0
# Bias
# -1 = simple sound, +1 = rich sound
WEIGHT_N_SIN             = 0.0
FORCE_WEIGHT_N_SIN       = 0.0
CURVE_WEIGHT_N_SIN   = 100.0


# TODO: FREQUENCY VIBRATO
# ================================================================
# DIM 12 — FREQ MOD  |  DIM 25 — FREQ MOD1  |  DIM 26 — FREQ MOD2
# ================================================================
# Global FM scale [0,1]. 0.0 = no FM.
FORCE_FM               = 0.0
# Modulator frequency range in Hz
# Low (1-5 Hz) = vibrato, High (20-50 Hz) = FM timbre
# Modulating frequency transeg curvature range over time
TYPE_FREQ_MOD_RANGE     = (0.1, 10.0)
FORZA_TYPE_FREQ_MOD     = 0.0   # fallback
# Modulation amplitude transeg curvature range over time
TYPE_FREQ_AMP_RANGE     = (0.1, 10.0)
FORZA_TYPE_FREQ_AMP     = 0.0   # fallback
# Modulator frequency range in Hz
FREQ_MOD_RANGE         = (5.0, 10.0)
# freq_mod sampling freedom
FREEDOM_FREQ_MOD       = 0.0
# freq_mod1/2 sampling freedom
FREEDOM_FREQ_MOD1      = 0.0
FREEDOM_FREQ_MOD2      = 0.0
# Bias freq_mod
# -1 = slow FM, +1 = fast FM
WEIGHT_FREQ_MOD          = 0.0
FORCE_WEIGHT_FREQ_MOD    = 0.0
CURVE_WEIGHT_FREQ_MOD = 100.0
# Bias freq_mod1 (dim 25)
WEIGHT_FREQ_MOD1           = 0.0
FORCE_WEIGHT_FREQ_MOD1     = 0.0
CURVE_WEIGHT_FREQ_MOD1 = 100.0
# Bias freq_mod2 (dim 26)
WEIGHT_FREQ_MOD2           = 0.0
FORCE_WEIGHT_FREQ_MOD2     = 0.0
CURVE_WEIGHT_FREQ_MOD2 = 100.0

# ================================================================
# DIM 13 — FREQ AMP  |  DIM 27 — FREQ AMP1  |  DIM 28 — FREQ AMP2
# ================================================================
# FM deviation range in Hz (clamped to niche bounds)
FREQ_AMP_RANGE         = (1.0, 3.0)
# FM freedom relative to niche bounds
# 0.0 = FM within niche, 1.0 = FM free over FREQ_AMP_RANGE
FREEDOM_FM             = 0.0
# freq_amp sampling freedom
FREEDOM_FREQ_AMP       = 0.0
FREEDOM_FREQ_AMP1      = 0.0
FREEDOM_FREQ_AMP2      = 0.0
# Bias freq_amp
# -1 = subtle FM, +1 = intense FM
WEIGHT_FREQ_AMP          = 0.0
FORCE_WEIGHT_FREQ_AMP    = 0.0
CURVE_WEIGHT_FREQ_AMP = 1000.0
# Bias freq_amp1 (dim 27)
WEIGHT_FREQ_AMP1           = 0.0
FORCE_WEIGHT_FREQ_AMP1     = 0.0
CURVE_WEIGHT_FREQ_AMP1 = 100.0
# Bias freq_amp2 (dim 28)
WEIGHT_FREQ_AMP2           = 0.0
FORCE_WEIGHT_FREQ_AMP2     = 0.0
CURVE_WEIGHT_FREQ_AMP2 = 100.0


# TODO: SPATIAL
# ================================================================
# DIM 6 — AZIMUTH START  |  DIM 23 — AZ END
# ================================================================
# az freedom relative to cell
FREEDOM_AZ             = 0.0
# az_end freedom relative to az cell
# 0.0 = movement within niche, 1.0 = free over full sphere
FREEDOM_AZ_END         = 0.0
# Bias az_start
# -1 = left hemisphere, +1 = right hemisphere
WEIGHT_AZIMUTH           = 0.0
FORCE_WEIGHT_AZIMUTH     = 0.0
CURVE_WEIGHT_AZIMUTH = 100.0
# Bias az_end (dim 23)
# -1 = movements toward left, +1 = toward right
WEIGHT_AZ_END              = 0.0
FORCE_WEIGHT_AZ_END        = 0.0
CURVE_WEIGHT_AZ_END    = 100.0

# ================================================================
# DIM 7 — ELEVAZIONE START  |  DIM 24 — EL END
# ================================================================
# el freedom relative to cell
FREEDOM_EL             = 0.0
# el_end freedom relative to el cell
FREEDOM_EL_END         = 0.0
# Bias el_start
# -1 = downward, +1 = upward
WEIGHT_ELEVATION        = 0.0
FORCE_WEIGHT_ELEVATION  = 0.0
CURVE_WEIGHT_ELEVATION = 100.0
# Bias el_end (dim 24)
# -1 = movements downward, +1 = upward
WEIGHT_EL_END              = 0.0
FORCE_WEIGHT_EL_END        = 0.0
CURVE_WEIGHT_EL_END    = 100.0

# ================================================================
# DIM 14 — PROX AMP (profondita' prossimita' spaziale)
# ================================================================
# Range [0,1]: 0=on HOA surface, 1=toward center
PROX_AMP_RANGE         = (1.0, 1.0)
# Sampling freedom
FREEDOM_PROX_AMP       = 0.0
# Bias
# -1 = sounds on HOA surface, +1 = sounds toward center
WEIGHT_PROX_AMP          = 0.0
FORCE_WEIGHT_PROX_AMP    = 0.0
CURVE_WEIGHT_PROX_AMP = 100.0

# ================================================================
# DIM 10 — TYPE MOVIMENTO SPAZIALE
# ================================================================
TYPE_MOV_AMB_RANGE     = (0.1, 10.0)
FORCE_MOV_AMB          = 1.0   # fallback
# Sampling freedom
FREEDOM_TYPE_MOV_AMB = 0.0
# Bias
# -1 = log (moves fast then slows), +1 = exponential (accelerates)
WEIGHT_TYPE_MOV_AMB      = 0.0
FORCE_WEIGHT_TYPE_MOV_AMB = 0.0
CURVE_WEIGHT_TYPE_MOV_AMB = 100.0

# ================================================================
# DIM 16 — PROBABILITY MOVIMENTO SPAZIALE
# ================================================================
# Bias
# -1 = static sounds, +1 = sounds always moving
WEIGHT_PROB_SPATIAL_MOVE          = 0.0
FORCE_WEIGHT_PROB_SPATIAL_MOVE    = 0.0
CURVE_WEIGHT_PROB_SPATIAL_MOVE = 100.0

# ================================================================
# DIM 11 — TYPE PROSSIMITA' SPAZIALE
# ================================================================
TYPE_PROX_AMB_RANGE    = (0.1, 10.0)
# Sampling freedom
FREEDOM_TYPE_PROX_AMB = 0.0
# Bias
# -1 = log, +1 = exponential
WEIGHT_TYPE_PROX_AMB     = 0.0
FORCE_WEIGHT_TYPE_PROX_AMB = 0.0
CURVE_WEIGHT_TYPE_PROX_AMB = 100.0

# ================================================================
# DIM 17-18 — RINGS SPAZIALI
# ================================================================
# If True, activates the band constraint
RINGS_AZ_ATTIVI = False
RINGS_EL_ATTIVI = True
# Bias az_band_center (dim 17)
# -1 = left hemisphere rings, +1 = right hemisphere
PESO_RINGS_AZ          = 0.0
FORZA_PESO_RINGS_AZ    = 0.0
CURVATURA_PESO_RINGS_AZ = 100.0
# Bias el_band_center (dim 18)
# -1 = rings downward, +1 = upward
PESO_RINGS_EL          = 0.0
FORZA_PESO_RINGS_EL    = 0.0
CURVATURA_PESO_RINGS_EL = 100.0

# ================================================================
# DIM 19 — REN 2D (maschera di tendenza sulla sfera)
# ================================================================
# Number of lobes (1=blob, 3=trefoil, 5=five-petal flower)
REN_K      = 3
# Valley depth (low=wide lobes, high=narrow lobes)
REN_LAMBDA = 1.0
# Edge shape (1.0=soft, 4.0+=sharp)
REN_Q      = 1.0
# Constraint force [0,1]: 0=free, 1=strongly confined
REN_2D_FORCE = 0.0
# If True, draws masks in the visualizer
VISUALIZE_REN_2D = False
# REN flower radius range — user reference point
# With FREEDOM_REN_RADIUS=0 it is auto-scaled for N niches
# With FREEDOM_REN_RADIUS=1 it is used exactly as written
REN_RAGGIO_RANGE = (0.2, 0.8)
# Liberta' sul raggio [0,1]:
# 0.0 = automatic radius (no overlap guaranteed)
# 1.0 = use REN_RAGGIO_RANGE without correction
FREEDOM_REN_RADIUS = 0.0
# Liberta' sul rilassamento dei centri [0,1]:
# 0.0 = perfectly equidistant centers on sphere (20 iterations)
# 1.0 = purely random centers (0 iterations)
FREEDOM_REN_RELAXATION = 0.0
# REN flower center bias
# -1 = centers left/down, +1 = centers right/up
WEIGHT_REN_AZ_CENTER           = 0.0
FORCE_WEIGHT_REN_AZ_CENTER     = 0.0
CURVE_WEIGHT_REN_AZ_CENTER  = 100.0
WEIGHT_REN_EL_CENTER           = 0.0
FORCE_WEIGHT_REN_EL_CENTER     = 0.0
CURVE_WEIGHT_REN_EL_CENTER  = 100.0

