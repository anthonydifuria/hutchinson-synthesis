"""
gigp_distribution.py — GIGP 1D Interactive Explorer
with MMD (Maximum Mean Discrepancy) for validation
numpy + matplotlib only
"""
import sys
sys.path.insert(0, '/tmp/hutch_clean')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider, RadioButtons
from gigp import ConfigDimensione, genera_centroidi_gigp_1d

BG      = '#11111b'
SURFACE = '#1e1e2e'
BORDER  = '#313244'
FG      = '#cdd6f4'
ACCENT  = '#89b4fa'
GREEN   = '#a6e3a1'
YELLOW  = '#f9e2af'
MAUVE   = '#cba6f7'
RED     = '#f38ba8'
TEAL    = '#94e2d5'
GRAY    = '#6c7086'
ORANGE  = '#fab387'
PINK    = '#eba0ac'

plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor':   SURFACE,
    'axes.edgecolor':   BORDER,
    'text.color':       FG,
    'xtick.color':      GRAY,
    'ytick.color':      GRAY,
    'grid.color':       BORDER,
    'grid.alpha':       0.5,
    'font.family':      'monospace',
    'font.size':        9,
})

N_POINTS = 50
N_RUNS   = 8    # aggregated runs for MMD reference
SIGMA    = 0.15
SEED     = 42

# ── Biased MMD ────────────────────────────────────────────────────────────────
def mmd_biased(X, Y, sigma=SIGMA):
    """Biased MMD² — always >= 0, stable with few points.
    MMD²(X,Y) = E[k(x,x')] - 2E[k(x,y)] + E[k(y,y')]"""
    def k(a, b):
        return np.exp(-(a[:, None] - b[None, :]) ** 2 / (2 * sigma ** 2))
    return float(k(X, X).mean() - 2 * k(X, Y).mean() + k(Y, Y).mean())

def reference(cfg, seed=SEED):
    """Aggregates N_RUNS samples to reduce estimator variance."""
    rng = np.random.default_rng(seed)
    return np.concatenate([
        genera_centroidi_gigp_1d(N_POINTS, cfg, rng) for _ in range(N_RUNS)
    ])

# ── Reference distributions ───────────────────────────────────────────────────
DIST_VALID = [
    ('Poisson',   ConfigDimensione(beta=0.0,  kernel_tipo='gaussiano'), YELLOW),
    ('DPP',       ConfigDimensione(beta=-1.0, kernel_tipo='gaussiano'), ACCENT),
    ('Matern',    ConfigDimensione(beta=-1.0, kernel_tipo='matern'),    TEAL),
    ('Permanent', ConfigDimensione(beta=+1.0, kernel_tipo='gaussiano'), RED),
    ('Strauss',   ConfigDimensione(beta=0.0,  w_strauss=3.0, R_strauss=0.08), MAUVE),
    ('Hawkes',    ConfigDimensione(beta=0.0,  w_hawkes=2.0,  decay_hawkes=5.0), GREEN),
    ('LGCP',      ConfigDimensione(beta=0.0,  lambda_tipo='lgcp'),      ORANGE),
    ('Alpha-S.',  ConfigDimensione(beta=0.0,  lambda_tipo='alpha_stable'), PINK),
]
DIST_NAMES  = [d[0] for d in DIST_VALID]
DIST_COLORS = [d[2] for d in DIST_VALID]
N_DIST      = len(DIST_VALID)

# ── State ─────────────────────────────────────────────────────────────────────
state = {
    'lambda_type': 'uniform',
    'beta':         0.0,
    'kernel_type':  'gaussian',
    'energy':       'none',
    'seed':         SEED,
}

def config_from_state(s):
    kw = dict(
        beta        = float(s['beta']),
        sigma       = 0.3,
        kernel_tipo = 'gaussiano' if s['kernel_type'] == 'gaussian' else s['kernel_type'],
        lambda_tipo = 'uniforme'  if s['lambda_type'] == 'uniform'  else s['lambda_type'],
        w_strauss   = 0.0,
        w_hawkes    = 0.0,
    )
    if s['energy'] == 'strauss':
        kw['w_strauss'] = 3.0; kw['R_strauss'] = 0.08
    elif s['energy'] == 'hawkes':
        kw['w_hawkes'] = 2.0;  kw['decay_hawkes'] = 5.0
    return ConfigDimensione(**kw)

def sample(s):
    rng = np.random.default_rng(s['seed'])
    cfg = config_from_state(s)
    return np.sort(genera_centroidi_gigp_1d(N_POINTS, cfg, rng))

def dist_name(s):
    b=s['beta']; k=s['kernel_type']; l=s['lambda_type']; e=s['energy']
    if l == 'lgcp':           return 'LGCP'
    if l == 'alpha_stable':   return 'Alpha-S.'
    if e == 'strauss':        return 'Strauss'
    if e == 'hawkes':         return 'Hawkes'
    if abs(b) < 0.02:         return 'Poisson'
    if b <= -0.95 and k == 'matern': return 'Matern'
    if b <= -0.95:            return 'DPP'
    if b >= +0.95:            return 'Permanent'
    return f'beta={b:+.2f}'

def dist_color(s):
    n = dist_name(s)
    if 'DPP'      in n: return ACCENT
    if 'Matern'   in n: return TEAL
    if 'Poisson'  in n: return YELLOW
    if 'Permanent'in n: return RED
    if 'Strauss'  in n: return MAUVE
    if 'Hawkes'   in n: return GREEN
    if 'LGCP'     in n: return ORANGE
    if 'Alpha'    in n: return PINK
    return GRAY

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(15, 9), facecolor=BG)
fig.text(0.5, 0.97, 'GIGP EXPLORER — 1D  |  MMD Validation',
         ha='center', va='top', fontsize=13, color=FG, fontweight='bold')

ax_strip = fig.add_axes([0.04, 0.65, 0.60, 0.27])
ax_hist  = fig.add_axes([0.04, 0.35, 0.60, 0.24])
ax_mmd   = fig.add_axes([0.04, 0.06, 0.60, 0.24])

fig.text(0.70, 0.93, 'LAMBDA',  fontsize=8, color=GRAY, fontweight='bold')
fig.text(0.70, 0.70, 'BETA',    fontsize=8, color=GRAY, fontweight='bold')
fig.text(0.70, 0.58, 'KERNEL',  fontsize=8, color=GRAY, fontweight='bold')
fig.text(0.70, 0.42, 'ENERGY',  fontsize=8, color=GRAY, fontweight='bold')
fig.text(0.70, 0.22, 'SEED',    fontsize=8, color=GRAY, fontweight='bold')

ax_lambda = fig.add_axes([0.70, 0.74, 0.28, 0.18], facecolor=SURFACE)
for sp in ax_lambda.spines.values(): sp.set_edgecolor(BORDER)
radio_lambda = RadioButtons(ax_lambda, ['uniform', 'lgcp', 'alpha_stable'], activecolor=ACCENT)
for lbl in radio_lambda.labels: lbl.set_color(FG); lbl.set_fontsize(9)

ax_beta = fig.add_axes([0.70, 0.63, 0.28, 0.04], facecolor=SURFACE)
slider_beta = Slider(ax_beta, 'b', -1.0, 1.0, valinit=0.0, color=ACCENT)
slider_beta.label.set_color(ACCENT); slider_beta.valtext.set_color(ACCENT)

ax_kernel = fig.add_axes([0.70, 0.45, 0.28, 0.12], facecolor=SURFACE)
for sp in ax_kernel.spines.values(): sp.set_edgecolor(BORDER)
radio_kernel = RadioButtons(ax_kernel, ['gaussian', 'matern'], activecolor=TEAL)
for lbl in radio_kernel.labels: lbl.set_color(FG); lbl.set_fontsize(9)

ax_energy = fig.add_axes([0.70, 0.26, 0.28, 0.14], facecolor=SURFACE)
for sp in ax_energy.spines.values(): sp.set_edgecolor(BORDER)
radio_energy = RadioButtons(ax_energy, ['none', 'strauss', 'hawkes'], activecolor=MAUVE)
for lbl in radio_energy.labels: lbl.set_color(FG); lbl.set_fontsize(9)

ax_seed_r = fig.add_axes([0.70, 0.14, 0.09, 0.06], facecolor=SURFACE)
ax_seed_n = fig.add_axes([0.81, 0.14, 0.09, 0.06], facecolor=SURFACE)
ax_valid  = fig.add_axes([0.70, 0.06, 0.28, 0.06], facecolor=SURFACE)
btn_reseed  = Button(ax_seed_r, 'RESET',    color=SURFACE, hovercolor=BORDER)
btn_newdraw = Button(ax_seed_n, 'NEW DRAW', color=SURFACE, hovercolor=BORDER)
btn_valid   = Button(ax_valid,  f'VALIDATE MMD  ({N_RUNS} runs x {N_POINTS} pts)',
                     color='#1a2a1a', hovercolor='#2a3a2a')
btn_reseed.label.set_color(YELLOW)
btn_newdraw.label.set_color(GREEN)
btn_valid.label.set_color(GREEN); btn_valid.label.set_fontweight('bold')

txt_name = fig.text(0.70, 0.01, '', fontsize=10, color=ACCENT, fontweight='bold')

# ── Draw ──────────────────────────────────────────────────────────────────────
def draw():
    pts = sample(state)
    c   = dist_color(state)
    n   = dist_name(state)

    ax_strip.cla()
    ax_strip.set_facecolor(SURFACE)
    for sp in ax_strip.spines.values(): sp.set_edgecolor(BORDER)
    ax_strip.set_xlim(-0.02, 1.02); ax_strip.set_ylim(-0.5, 1.5)
    ax_strip.set_yticks([]); ax_strip.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_strip.grid(axis='x', alpha=0.3)
    ax_strip.set_title('Point distribution', color=GRAY, fontsize=9, pad=4)
    ax_strip.axhline(0.5, color=BORDER, lw=1.0)
    rng_j  = np.random.default_rng(state['seed'] + 999)
    jitter = rng_j.uniform(-0.28, 0.28, len(pts))
    ax_strip.scatter(pts, 0.5+jitter, color=c, s=40, alpha=0.85, zorder=3, linewidths=0)
    for p in pts: ax_strip.axvline(p, ymin=0, ymax=0.08, color=c, lw=0.7, alpha=0.4)
    if len(pts) > 1:
        gaps = np.diff(pts)
        ax_strip.text(0.01, 0.06,
            f'n={len(pts)}  gap min={gaps.min():.3f}  max={gaps.max():.3f}  std={gaps.std():.3f}',
            transform=ax_strip.transAxes, color=GRAY, fontsize=8)

    ax_hist.cla()
    ax_hist.set_facecolor(SURFACE)
    for sp in ax_hist.spines.values(): sp.set_edgecolor(BORDER)
    ax_hist.set_xlim(-0.02, 1.02); ax_hist.grid(axis='y', alpha=0.3)
    ax_hist.set_title('Density', color=GRAY, fontsize=9, pad=4)
    ax_hist.hist(pts, bins=20, range=(0,1), color=c, alpha=0.75, edgecolor=BG, linewidth=0.5)
    ax_hist.axhline(N_POINTS/20, color=GRAY, lw=1.0, ls='--', alpha=0.6, label='expected Poisson')
    ax_hist.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=GRAY, fontsize=8)

    ax_mmd.cla()
    ax_mmd.set_facecolor(SURFACE)
    for sp in ax_mmd.spines.values(): sp.set_edgecolor(BORDER)
    ax_mmd.set_title('MMD — press VALIDATE', color=GRAY, fontsize=9, pad=4)
    ax_mmd.text(0.5, 0.5, 'press  VALIDATE  to compute the MMD matrix',
                ha='center', va='center', transform=ax_mmd.transAxes, color=GRAY, fontsize=10)
    ax_mmd.set_xticks([]); ax_mmd.set_yticks([])

    txt_name.set_text(n); txt_name.set_color(c)
    fig.canvas.draw_idle()

# ── MMD Validation ────────────────────────────────────────────────────────────
def validate():
    n_current  = dist_name(state)
    cfg_current = config_from_state(state)
    print(f'\n{"="*60}')
    print(f'  MMD VALIDATION — generator: {n_current}')
    print(f'  sigma={SIGMA}, {N_RUNS} runs x {N_POINTS} points')
    print(f'{"="*60}')

    # Build references for all distributions
    refs = {}
    for name_d, cfg_d, _ in DIST_VALID:
        refs[name_d] = reference(cfg_d)

    ref_current = reference(cfg_current, seed=state['seed'])

    mmd_vals = []
    for name_d, _, _ in DIST_VALID:
        v = mmd_biased(ref_current, refs[name_d])
        mmd_vals.append(v)
        marker = ' <-- MIN (most similar)' if v == min(mmd_vals) else ''
        print(f'  MMD({n_current:10s}, {name_d:10s}) = {v:.6f}{marker}')

    idx_min = int(np.argmin(mmd_vals))
    print(f'{"="*60}')
    print(f'  Most similar distribution: {DIST_NAMES[idx_min]}')
    ok = DIST_NAMES[idx_min].lower()[:4] in n_current.lower() or \
         n_current.lower()[:4] in DIST_NAMES[idx_min].lower()
    print(f'  Result: {"OK" if ok else "WARNING"}')
    print(f'{"="*60}\n')

    ax_mmd.cla()
    ax_mmd.set_facecolor(SURFACE)
    for sp in ax_mmd.spines.values(): sp.set_edgecolor(BORDER)
    ax_mmd.grid(axis='x', alpha=0.3)
    ax_mmd.set_title(
        f'MMD — generator: {n_current}  (low = similar)',
        color=GRAY, fontsize=9, pad=4)

    y_pos = np.arange(N_DIST)
    bars = ax_mmd.barh(y_pos, mmd_vals, color=DIST_COLORS, alpha=0.75,
                       edgecolor=BG, height=0.6)
    bars[idx_min].set_edgecolor(FG); bars[idx_min].set_linewidth(2.0)
    bars[idx_min].set_alpha(1.0)

    ax_mmd.set_yticks(y_pos)
    ax_mmd.set_yticklabels(DIST_NAMES, fontsize=8)
    ax_mmd.set_xlabel('MMD²  (0 = identical, high = different)', color=GRAY, fontsize=8)

    for i, (bar, val) in enumerate(zip(bars, mmd_vals)):
        ax_mmd.text(val + 0.0001, i, f'{val:.4f}',
                    va='center', ha='left', color=FG, fontsize=7)

    msg = f'OK — {DIST_NAMES[idx_min]} is the most similar' if ok \
          else f'WARNING — {DIST_NAMES[idx_min]} is the most similar'
    ax_mmd.text(0.99, 0.02, msg, transform=ax_mmd.transAxes,
                ha='right', va='bottom',
                color=GREEN if ok else YELLOW, fontsize=8, fontweight='bold')

    fig.canvas.draw_idle()

# ── Callbacks ─────────────────────────────────────────────────────────────────
def on_lambda(val):
    state['lambda_type'] = val
    if val != 'uniform':
        state['beta'] = 0.0; slider_beta.set_val(0.0)
    draw()

def on_beta(val):
    state['beta'] = val; draw()

def on_kernel(val):
    state['kernel_type'] = val; draw()

def on_energy(val):
    state['energy'] = val
    if val != 'none':
        state['beta'] = 0.0; slider_beta.set_val(0.0)
    draw()

def on_reseed(event):
    state['seed'] = SEED; draw()

def on_newdraw(event):
    state['seed'] = int(np.random.randint(0, 9999)); draw()

def on_validate(event):
    validate()

radio_lambda.on_clicked(on_lambda)
slider_beta.on_changed(on_beta)
radio_kernel.on_clicked(on_kernel)
radio_energy.on_clicked(on_energy)
btn_reseed.on_clicked(on_reseed)
btn_newdraw.on_clicked(on_newdraw)
btn_valid.on_clicked(on_validate)

draw()
plt.show()