"""
visualizer.py — Hutchinson Synthesis
Layout: plot grande a sinistra, pulsanti a destra in elenco verticale.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mp
from matplotlib.widgets import Button
from mpl_toolkits.mplot3d import Axes3D  # noqa

_PALETTE = ['#2196F3','#F44336','#4CAF50','#FF9800','#9C27B0','#00BCD4',
            '#FFEB3B','#795548','#E91E63','#009688','#FF5722','#607D8B',
            '#3F51B5','#8BC34A','#FFC107','#673AB7','#00E5FF','#FF6F00']
def _col(i): return _PALETTE[i % len(_PALETTE)]
_BG='#ffffff'; _PLOT_BG='#f5f5f8'; _FG='#22223a'; _GRID='#ccccdd'

# ── Definizione pulsanti ─────────────────────────────────────────────────────
_BUTTONS = [
    (None,          '── DURATA / ONSET ─','#45475a', False),
    ('durata',      'Durata',            '#f9e2af', False),
    ('onset',       'Onset',             '#f9e2af', False),
    (None,          '── FREQUENZA ──',   '#45475a', False),
    ('freq_start',  'Freq Start',        '#89b4fa', False),
    ('freq_end',    'Freq End',          '#74c7ec', False),
    ('gliss',       'Glissato (curva)',  '#89b4fa', False),
    ('n_sinusoidi', 'N Sinusoidi',       '#89dceb', False),
    ('type_gliss',  'Type Gliss',        '#89dceb', False),
    (None,          '── FM ──',          '#45475a', False),
    ('freq_mod',    'Freq MOD',          '#a6e3a1', False),
    ('freq_mod1',   'Freq MOD start',    '#94e2d5', False),
    ('freq_mod2',   'Freq MOD end',      '#94e2d5', False),
    ('freq_amp',    'Freq AMP',          '#a6e3a1', False),
    ('freq_amp1',   'Freq AMP start',    '#94e2d5', False),
    ('freq_amp2',   'Freq AMP end',      '#94e2d5', False),
    ('type_freq_mod','Type Freq MOD',    '#94e2d5', False),
    ('type_freq_amp','Type Freq AMP',    '#94e2d5', False),
    (None,          '── AMPIEZZA ──',    '#45475a', False),
    ('amp',         'Ampiezza',          '#a6e3a1', False),
    ('perc',        'Perc Env',          '#a6e3a1', False),
    ('type_env',    'Type Env',          '#94e2d5', False),
    (None,          '── SPAZIO ──',      '#45475a', False),
    ('az',          'Azimuth',           '#cba6f7', False),
    ('el',          'Elevation',         '#cba6f7', False),
    ('az_end',      'Az End',            '#b4befe', False),
    ('el_end',      'El End',            '#b4befe', False),
    ('type_mov_amb','Type Mov',          '#f38ba8', False),
    ('type_prox_amb','Type Prox',        '#f38ba8', False),
    ('prox_amp',    'Prox Amp',          '#eba0ac', False),
    # ── TEMPO ────────────────────────────────────────────────────
    (None,          '── TEMPO ──',       '#45475a', False),
    ('onset',       'Onset',             '#f9e2af', False),
    # ── Anelli ───────────────────────────────────────────────────
    (None,          '── RINGS ──',      '#45475a', False),
    ('_anelli',     '  RINGS 2D',       '#74c7ec', False),
    # ── REN 2D ───────────────────────────────────────────────────
    (None,          '── REN 2D ──',      '#45475a', False),
    ('_ren2d',      '  REN 2D MAPPA',    '#a6e3a1', False),
    # ── Onset niche ────────────────────────────────────────────
    (None,          '── ONSET ─',       '#45475a', False),
    ('niche_onset',  'Onset Nicchia',  '#f38ba8', False),
    ('niche_fade_in','Fade In',        '#eba0ac', False),
    (None,          '── PROBABILITÀ ──', '#45475a', False),
    ('_prob_gliss', 'P Glissato',        '#f9e2af', False),
    ('_prob_mov',   'P Movimento',       '#f9e2af', False),
    (None,          '── ─',             '#45475a', False),
    ('_sfera',      '  SFERA 3D',       '#cba6f7', False),
    ('_dur',        '● Dur ON',          '#f9e2af', False),
]

_KEY_LABEL  = {b[0]:b[1] for b in _BUTTONS if b[0] and not b[0].startswith('')}
_KEY_LABEL.update({'_prob_gliss':'P Glissato','_prob_mov':'P Movimento'})
_KEY_COLOR  = {b[0]:b[2] for b in _BUTTONS if b[0]}
_GRADI_KEYS = {'az','el','az_end','el_end'}
_LOG10_KEYS = {'type_gliss','type_env','type_mov_amb','type_prox_amb',
               'type_freq_mod','type_freq_amp'}

KEY_BOUNDS = {
    'durata':        ('durata_min',            'durata_max',            False),
    'onset':         ('onset_min',             'onset_max',             False),
    'onset':         ('onset_min',             'onset_max',             False),
    'freq_start':    ('freq_min',              'freq_max',              False),
    'freq_end':      ('freq_min',              'freq_max',              False),
    'freq_mod':      ('freq_mod_min',          'freq_mod_max',          False),
    'freq_mod1':     ('freq_mod_min',          'freq_mod_max',          False),
    'freq_mod2':     ('freq_mod_min',          'freq_mod_max',          False),
    'freq_amp':      ('freq_amp_min',          'freq_amp_max',          False),
    'freq_amp1':     ('freq_amp_min',          'freq_amp_max',          False),
    'freq_amp2':     ('freq_amp_min',          'freq_amp_max',          False),
    'amp':           ('amp_min',               'amp_max',               False),
    'perc':          ('perc_min',              'perc_max',              False),
    'n_sinusoidi':   ('n_sin_min',             'n_sin_max',             False),
    'az':            ('az_min',                'az_max',                True),
    'el':            ('el_min',                'el_max',                True),
    'az_end':        ('az_end_min',            'az_end_max',            True),
    'el_end':        ('el_end_min',            'el_end_max',            True),
    'prox_amp':      ('prox_amp_min',          'prox_amp_max',          False),
    'type_gliss':    ('type_gliss_min',        'type_gliss_max',        False),
    'type_env':      ('type_env_min',          'type_env_max',          False),
    'type_mov_amb':  ('type_mov_amb_min',      'type_mov_amb_max',      False),
    'type_prox_amb': ('type_prox_amb_min',     'type_prox_amb_max',     False),
    'type_freq_mod': ('type_freq_mod_min',     'type_freq_mod_max',     False),
    'type_freq_amp': ('type_freq_amp_min',     'type_freq_amp_max',     False),
    '_prob_gliss':   ('prob_glissato_min',     'prob_glissato_max',     False),
    '_prob_mov':     ('prob_mov_spaziale_min', 'prob_mov_spaziale_max', False),
}

_KEY_TO_DIM = {
    # Dimensioni primarie
    'durata':        0,
    'onset':         1,
    'amp':           2,   'perc':          3,
    'n_sinusoidi':   4,
    'freq_start':    5,   'freq_end':      5,   # freq_end usa cella parent freq_start
    'az':            6,   'az_end':        6,   # az_end usa cella parent az
    'el':            7,   'el_end':        7,   # el_end usa cella parent el
    # Dimensioni secondarie
    'type_gliss':    8,   'type_env':      9,
    'type_mov_amb':  10,  'type_prox_amb': 11,
    'freq_mod':      12,  'freq_mod1':     12,  'freq_mod2': 12,  # usano cella parent freq_mod
    'freq_amp':      13,  'freq_amp1':     13,  'freq_amp2': 13,  # usano cella parent freq_amp
    'prox_amp':      14,
    '_prob_gliss':   15,  '_prob_mov':     16,
    # Anelli e REN
    'az_band_center':17,  'el_band_center':18,
    'niche_onset': 20,  'niche_fade_in':21,
}

_COPPIE = {
    frozenset(['freq_start','freq_end','type_gliss']),
    frozenset(['az','az_end','type_mov_amb']),
    frozenset(['el','el_end','type_mov_amb']),
    frozenset(['freq_mod1','freq_mod2','type_freq_mod']),
    frozenset(['freq_amp1','freq_amp2','type_freq_amp']),
}

# ── Stato ────────────────────────────────────────────────────────────────────
class _S:
    selezionate=[]; bottoni={}; ax_plot=None; fig=None
    eventi=None; nicchie_info=None; durata_on=True; modo='normal'
    forza_ren_2d=0.0; liberta_ren_raggio=0.0
    anelli_az_attivi=False; anelli_el_attivi=False
    visualizza_ren_2d=True
    # Parametri forma REN 2D
    ren_k=5; ren_l=2.0; ren_q=2.0
_stato = _S()

# ── Utility ──────────────────────────────────────────────────────────────────
def _transeg(t, tv):
    tv=float(np.clip(tv,-15,15))
    if abs(tv)<0.05: return t.copy()
    return (np.exp(tv*t)-1)/(np.exp(tv)-1)

def _get(ev, key):
    v=float(ev.get(key,0) or 0)
    if key in _GRADI_KEYS: v=np.degrees(v)
    if key in _LOG10_KEYS and v>0: v=np.log10(v)
    return v

def _trange(lista):
    t=0.0
    for evs in lista:
        for e in evs: t=max(t,float(e.get('onset',0))+float(e.get('durata',0)))
    return 0.0, max(t,0.1)

def _bounds(region_idx, key):
    ni = _stato.nicchie_info
    if ni is None: return None
    if isinstance(ni, dict) and key in KEY_BOUNDS:
        km, kx, gr = KEY_BOUNDS[key]
        dim_idx = _KEY_TO_DIM.get(key)
        if dim_idx is None or dim_idx not in ni: return None
        dim = ni[dim_idx]
        if region_idx >= len(dim['mins']): return None
        lo = float(dim['mins'][region_idx])
        hi = float(dim['maxs'][region_idx])
        if gr: lo = np.degrees(lo); hi = np.degrees(hi)
        return lo, hi
    if isinstance(ni, list):
        if region_idx >= len(ni) or key not in KEY_BOUNDS: return None
        km, kx, gr = KEY_BOUNDS[key]; nb = ni[region_idx]
        if km not in nb or kx not in nb: return None
        lo, hi = float(nb[km]), float(nb[kx])
        if gr: lo, hi = np.degrees(lo), np.degrees(hi)
        return lo, hi
    return None

def _style(ax):
    ax.set_facecolor(_PLOT_BG); ax.tick_params(colors=_FG,labelsize=9)
    for sp in ax.spines.values(): sp.set_edgecolor(_GRID)
    ax.grid(True,color=_GRID,lw=0.5,alpha=0.6)

def _legend(evs, ax):
    p=[mp.Patch(color=_col(i),label=f'R{i+1}') for i in range(len(evs)) if evs[i]]
    ax.legend(handles=p,facecolor='#f0f0f5',edgecolor='#aaaacc',
              labelcolor=_FG,fontsize=7,loc='upper right')

# ── Plot generici ─────────────────────────────────────────────────────────────
def _draw_2d(ax, evs, dims):
    if isinstance(dims,str): dims=[dims]
    _style(ax)
    lbl=' + '.join(_KEY_LABEL.get(d,d) for d in dims)
    ax.set_xlabel('Tempo (s)',color=_FG,fontsize=10)
    ax.set_ylabel(lbl,color=_FG,fontsize=10)
    nota=''
    if any(d in ('type_freq_mod','type_freq_amp') for d in dims): nota=' [random per-evento]'
    if any(d in ('_prob_gliss','_prob_mov') for d in dims): nota=' [prob dim 15/16]'
    ax.set_title(lbl+nota,color=_FG,fontsize=10 if nota else 12,pad=8)
    t0,t1=_trange(evs)
    dim_vis=dims[0]
    ni=_stato.nicchie_info
    dim_idx=_KEY_TO_DIM.get(dim_vis)
    if ni is not None and isinstance(ni,dict) and dim_idx in ni:
        dim_data=ni[dim_idx]
        for r_idx in range(len(dim_data['mins'])):
            b=_bounds(r_idx,dim_vis)
            if b:
                ax.axhspan(b[0],b[1],color=_col(r_idx),alpha=0.08,zorder=0)
                ax.axhline(b[0],color=_col(r_idx),lw=0.5,alpha=0.3,ls='--')
                ax.axhline(b[1],color=_col(r_idx),lw=0.5,alpha=0.3,ls='--')
    else:
        for i in range(len(evs)):
            b=_bounds(i,dim_vis)
            if b:
                ax.axhspan(b[0],b[1],color=_col(i),alpha=0.08,zorder=0)

    mks=['o','s','^','D']; lss=['-','--','-.',':']
    for di,dim in enumerate(dims):
        all_xs=[]; all_ys=[]; all_cs=[]; all_x0=[]; all_x1=[]; all_yh=[]
        for evs_lista in evs:
            for ev in evs_lista:
                c=_col(ev.get(f'_r{dim_idx}',0)) if dim_idx is not None else _col(0)
                xs=_get(ev,'onset'); dr=_get(ev,'durata'); ys=_get(ev,dim)
                all_xs.append(xs); all_ys.append(ys); all_cs.append(c)
                if _stato.durata_on: all_x0.append(xs); all_x1.append(xs+dr); all_yh.append(ys)
        if _stato.durata_on:
            for x0,x1,y,c in zip(all_x0,all_x1,all_yh,all_cs):
                ax.plot([x0,x1],[y,y],color=c,lw=1.4,alpha=0.5,ls=lss[di%4])
        if all_xs: ax.scatter(all_xs,all_ys,c=all_cs,s=25,marker=mks[di%4],zorder=5,alpha=0.85)

    ax.set_xlim(t0, t1)
    all_y = [_get(e, d) for evs_l in evs for e in evs_l for d in dims]

    # Recupero bound globali dalla tassellazione Voronoi
    ni = _stato.nicchie_info
    dim_idx = _KEY_TO_DIM.get(dims[0])
    ylo_glob, yhi_glob = None, None
    if ni is not None and isinstance(ni, dict) and dim_idx in ni:
        dim_data = ni[dim_idx]
        ylo_glob = float(dim_data['mins'].min())
        yhi_glob = float(dim_data['maxs'].max())

    if all_y:
        ylo_dat, yhi_dat = min(all_y), max(all_y)
        # Clamp ai bound globali della dimensione
        ylo = min(ylo_dat, ylo_glob) if ylo_glob is not None else ylo_dat
        yhi = max(yhi_dat, yhi_glob) if yhi_glob is not None else yhi_dat
    else:
        ylo, yhi = ylo_glob, yhi_glob

    if ylo is not None and yhi is not None:
        span = yhi - ylo
        pad = span * 0.05 if span > 1e-6 else 1.0
        ax.set_ylim(ylo - pad, yhi + pad)

def _draw_gliss(ax, evs):
    _style(ax)
    ax.set_xlabel('Time (s)',color=_FG,fontsize=10)
    ax.set_ylabel('Frequency (Hz)',color=_FG,fontsize=10)
    ax.set_title('Glissato — freq_start → freq_end',color=_FG,fontsize=12,pad=8)
    t0,t1=_trange(evs); tn=np.linspace(0,1,60)
    for i in range(len(evs)):
        b=_bounds(i,'freq_start')
        if b:
            ax.axhspan(b[0],b[1],color=_col(i),alpha=0.07,zorder=0)
            ax.axhline(b[0],color=_col(i),lw=0.5,alpha=0.3,ls='--')
            ax.axhline(b[1],color=_col(i),lw=0.5,alpha=0.3,ls='--')
    for i,eventi in enumerate(evs):
        if not eventi: continue
        c=_col(i)
        for ev in eventi:
            o=float(ev.get('onset',0)); d=max(0.001,float(ev.get('durata',0.1)))
            f0=float(ev.get('freq_start',440)); f1=float(ev.get('freq_end',f0))
            tg=float(ev.get('type_gliss',1.0))
            fc=f0+(f1-f0)*_transeg(tn,tg)
            ax.plot(o+tn*d,fc,color=c,lw=1.3,alpha=0.55)
            ax.scatter([o],[f0],c=c,s=22,zorder=5,alpha=0.85)
            if _stato.durata_on:
                ax.scatter([o+d],[f1],c=c,s=14,marker='s',zorder=5,alpha=0.65)
    ax.set_xlim(t0,t1); _legend(evs,ax)

def _draw_mov(ax, evs, ds, de):
    _style(ax); lbl=_KEY_LABEL.get(ds,ds)
    ax.set_xlabel('Tempo (s)',color=_FG,fontsize=10)
    ax.set_ylabel(f'{lbl} (°)',color=_FG,fontsize=10)
    ax.set_title(f'Movimento — {lbl}',color=_FG,fontsize=12,pad=8)
    for dim_key in (ds, de):
        for i in range(len(evs)):
            b = _bounds(i, dim_key)
            if b:
                ax.axhspan(b[0],b[1],color=_col(i),alpha=0.07,zorder=0)
                ax.axhline(b[0],color=_col(i),lw=0.5,alpha=0.3,ls='--')
                ax.axhline(b[1],color=_col(i),lw=0.5,alpha=0.3,ls='--')
    t0,t1=_trange(evs); tn=np.linspace(0,1,60)
    for i,eventi in enumerate(evs):
        if not eventi: continue
        c=_col(i)
        for ev in eventi:
            o=float(ev.get('onset',0)); d=max(0.001,float(ev.get('durata',0.1)))
            v0=_get(ev,ds); v1=_get(ev,de)
            tm=float(ev.get('type_mov_amb',1.0))
            vc=v0+(v1-v0)*_transeg(tn,10**tm)
            ax.plot(o+tn*d,vc,color=c,lw=1.3,alpha=0.55)
            ax.scatter([o],[v0],c=c,s=22,zorder=5,alpha=0.85)
            if _stato.durata_on:
                ax.scatter([o+d],[v1],c=c,s=14,marker='s',zorder=5,alpha=0.65)
    ax.set_xlim(t0,t1); _legend(evs,ax)

def _draw_fm_curva(ax, evs, key_amp, key1, key2):
    _style(ax); lbl=_KEY_LABEL.get(key_amp,key_amp)
    ax.set_xlabel('Tempo (s)',color=_FG,fontsize=10)
    ax.set_ylabel(lbl,color=_FG,fontsize=10)
    ax.set_title(f'{lbl} — {_KEY_LABEL.get(key1,key1)} → {_KEY_LABEL.get(key2,key2)}',
                 color=_FG,fontsize=12,pad=8)
    t0,t1=_trange(evs); tn=np.linspace(0,1,60)
    for i in range(len(evs)):
        b=_bounds(i,key_amp)
        if b:
            ax.axhspan(b[0],b[1],color=_col(i),alpha=0.07,zorder=0)
            ax.axhline(b[0],color=_col(i),lw=0.5,alpha=0.3,ls='--')
            ax.axhline(b[1],color=_col(i),lw=0.5,alpha=0.3,ls='--')
    type_key='type_freq_mod' if 'mod' in key1 else 'type_freq_amp'
    for i,eventi in enumerate(evs):
        if not eventi: continue
        c=_col(i)
        for ev in eventi:
            v0=float(ev.get(key1,0)); v1=float(ev.get(key2,v0))
            if v0==0 and v1==0: continue
            o=float(ev.get('onset',0)); d=max(0.001,float(ev.get('durata',0.1)))
            tv=float(ev.get(type_key,1.0))
            vc=v0+(v1-v0)*_transeg(tn,tv)
            ax.plot(o+tn*d,vc,color=c,lw=1.2,alpha=0.5)
            ax.scatter([o],[v0],c=c,s=18,zorder=5,alpha=0.8)
            if _stato.durata_on:
                ax.scatter([o+d],[v1],c=c,s=12,marker='s',zorder=5,alpha=0.6)
    ax.set_xlim(t0,t1); _legend(evs,ax)

# ── SFERA 3D ──────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# DRAW IN-PLACE (tutte usano ax passato, nessuna finestra separata)
# ─────────────────────────────────────────────────────────────────────────────

def _draw_anelli_in(ax, evs):
    """Mappa 2D az/el con fasce anelli. Disegna nell'ax passato."""
    ax.set_facecolor(_BG)
    ax.tick_params(colors=_FG, labelsize=8)
    for sp in ax.spines.values(): sp.set_edgecolor(_GRID)
    ax.grid(True, color=_GRID, lw=0.4, alpha=0.5)
    ax.set_xlabel('Azimuth (deg)', color=_FG, fontsize=10)
    ax.set_ylabel('Elevation (deg)', color=_FG, fontsize=10)
    ax.set_xlim(-180, 180); ax.set_ylim(-90, 90)
    ni = _stato.nicchie_info; titolo = []
    if _stato.anelli_el_attivi and ni and 18 in ni:
        titolo.append('El')
        em, eM = ni[18]['mins'], ni[18]['maxs']
        for r in range(len(em)):
            lo = float(np.degrees(np.clip(em[r], -np.pi/2, np.pi/2)))
            hi = float(np.degrees(np.clip(eM[r], -np.pi/2, np.pi/2)))
            c  = _col(r)
            ax.axhspan(lo, hi, color=c, alpha=0.18, zorder=1)
            ax.axhline(lo, color=c, lw=1.2, alpha=0.7, ls='--', zorder=2)
            ax.axhline(hi, color=c, lw=1.2, alpha=0.7, ls='--', zorder=2)
            ax.text(175, (lo+hi)/2, f'EL{r+1}', color=c, fontsize=8,
                    va='center', ha='right', zorder=3)
    if _stato.anelli_az_attivi and ni and 17 in ni:
        titolo.append('Az')
        am, aM = ni[17]['mins'], ni[17]['maxs']
        for r in range(len(am)):
            lo = float(np.degrees(np.clip(am[r], -np.pi, np.pi)))
            hi = float(np.degrees(np.clip(aM[r], -np.pi, np.pi)))
            c  = _col(r)
            ax.axvspan(lo, hi, color=c, alpha=0.18, zorder=1)
            ax.axvline(lo, color=c, lw=1.2, alpha=0.7, ls='--', zorder=2)
            ax.axvline(hi, color=c, lw=1.2, alpha=0.7, ls='--', zorder=2)
            ax.text((lo+hi)/2, 88, f'AZ{r+1}', color=c, fontsize=8,
                    va='top', ha='center', zorder=3)
    if not (_stato.anelli_el_attivi or _stato.anelli_az_attivi):
        ax.set_title('Rings 2D — inactive', color=_FG, fontsize=12, pad=8)
        ax.text(0.5, 0.5, 'Rings inactive\n(RINGS_AZ_ATTIVI / RINGS_EL_ATTIVI = False)',
                color='#888899', ha='center', va='center', fontsize=12,
                transform=ax.transAxes)
        return
    for i, eventi in enumerate(evs):
        for ev in eventi:
            if _stato.anelli_el_attivi:   c_idx = int(ev.get('el_band_idx', i))
            elif _stato.anelli_az_attivi: c_idx = int(ev.get('az_band_idx', i))
            else:                         c_idx = i
            c   = _col(c_idx)
            az  = float(np.degrees(ev.get('az', 0)))
            el  = float(np.degrees(ev.get('el', 0)))
            az1 = float(np.degrees(ev.get('az_end', ev.get('az', 0))))
            el1 = float(np.degrees(ev.get('el_end', ev.get('el', 0))))
            if abs(az1-az) > 0.5 or abs(el1-el) > 0.5:
                ax.annotate('', xy=(az1,el1), xytext=(az,el),
                            arrowprops=dict(arrowstyle='->', color=c, lw=0.8, alpha=0.45))
            ax.scatter([az], [el], c=c, s=20, alpha=0.75, zorder=5)
    lbl = ' + '.join(titolo) if titolo else 'nessuna attiva'
    ax.set_title(f'Rings 2D — {lbl}', color=_FG, fontsize=12, pad=8)


def _draw_ren2d_in(ax, evs):
    """Mappa 2D az/el con fiori REN + wrapping ai bordi. Disegna nell'ax passato."""
    ax.set_facecolor(_BG)
    ax.tick_params(colors=_FG, labelsize=8)
    for sp in ax.spines.values(): sp.set_edgecolor(_GRID)
    ax.grid(True, color=_GRID, lw=0.4, alpha=0.5)
    ax.set_xlabel('Azimuth (deg)', color=_FG, fontsize=10)
    ax.set_ylabel('Elevation (deg)', color=_FG, fontsize=10)
    ax.set_xlim(-180, 180); ax.set_ylim(-90, 90)
    ax.set_title('REN 2D — Flat map', color=_FG, fontsize=12, pad=8)
    ni = _stato.nicchie_info
    if not (ni and 19 in ni and 'centers' in ni[19]):
        ax.text(0.5, 0.5, 'REN 2D inactive\n(REN_2D_FORCE = 0)',
                color='#888899', ha='center', va='center', fontsize=12,
                transform=ax.transAxes)
        return
    rd=ni[19]; centers=rd['centers']; radii=rd['radii']
    r_cerchio = float(rd.get('r_cerchio', np.pi/2.0))
    k=int(_stato.ren_k); lam=float(_stato.ren_l); q=float(_stato.ren_q)
    phi = np.linspace(0, 2*np.pi, 800)

    def _disegna_fiore(az_pts, el_pts, c, alpha_line, alpha_fill, zorder=3):
        """Disegna il fiore solo se almeno un punto è nel range visibile."""
        az_d = np.array(az_pts); el_d = np.array(el_pts)
        mask = (az_d >= -180) & (az_d <= 180) & (el_d >= -90) & (el_d <= 90)
        if not mask.any(): return
        ax.plot(az_d, el_d, color=c, lw=1.8, alpha=alpha_line, zorder=zorder)
        ax.fill(az_d, el_d, color=c, alpha=alpha_fill, zorder=zorder-1)

    for i, (c_az, c_el) in enumerate(centers):
        c      = _col(i)
        lib_r  = float(_stato.liberta_ren_raggio)
        r_raw  = float(radii[i])
        r_cap  = r_cerchio * (1.0 - lib_r) + r_raw * lib_r
        r_mask = min(r_raw, r_cap)
        r_val  = np.exp(-lam * np.abs(np.sin(k * phi / 2)) ** q)
        dist   = r_val * r_mask

        # Coordinate in radianti (non clampate)
        az_r = c_az + dist * np.cos(phi)
        el_r = c_el + dist * np.sin(phi)

        # Converti in gradi
        az_d = np.degrees(az_r)
        el_d = np.degrees(el_r)

        # ── Fiore principale ─────────────────────────────────────────
        _disegna_fiore(az_d, el_d, c, 0.7, 0.10, zorder=4)
        ax.scatter([np.degrees(c_az)], [np.degrees(c_el)],
                   c=c, s=80, marker='*', zorder=6)
        ax.text(np.degrees(c_az)+2, np.degrees(c_el)+2, f'REN{i+1}',
                color=c, fontsize=8, zorder=7)

        # ── Ghost wrapping azimuth (+360 e -360) ─────────────────────
        _disegna_fiore(az_d + 360, el_d, c, 0.25, 0.04, zorder=2)
        _disegna_fiore(az_d - 360, el_d, c, 0.25, 0.04, zorder=2)

        # ── Ghost wrapping elevazione (polo nord: el>90) ─────────────
        # Al polo la sfera si ripiega: el_new = 180-el, az_new = az+180
        el_nord = 180.0 - el_d
        az_nord = az_d + 180.0
        _disegna_fiore(az_nord,       el_nord, c, 0.20, 0.03, zorder=2)
        _disegna_fiore(az_nord + 360, el_nord, c, 0.15, 0.02, zorder=2)
        _disegna_fiore(az_nord - 360, el_nord, c, 0.15, 0.02, zorder=2)

        # ── Ghost wrapping elevazione (polo sud: el<-90) ─────────────
        # Al polo sud: el_new = -180-el, az_new = az+180
        el_sud = -180.0 - el_d
        az_sud = az_d + 180.0
        _disegna_fiore(az_sud,       el_sud, c, 0.20, 0.03, zorder=2)
        _disegna_fiore(az_sud + 360, el_sud, c, 0.15, 0.02, zorder=2)
        _disegna_fiore(az_sud - 360, el_sud, c, 0.15, 0.02, zorder=2)

    # ── Linee bordo per indicare il wrapping ─────────────────────────
    ax.axvline(-180, color=_GRID, lw=1.0, ls=':', alpha=0.6)
    ax.axvline( 180, color=_GRID, lw=1.0, ls=':', alpha=0.6)
    ax.axhline(-90,  color=_GRID, lw=1.0, ls=':', alpha=0.6)
    ax.axhline( 90,  color=_GRID, lw=1.0, ls=':', alpha=0.6)

    # ── Eventi ───────────────────────────────────────────────────────
    for i, eventi in enumerate(evs):
        for ev in eventi:
            c_idx = int(ev.get('ren_region', i))
            c   = _col(c_idx)
            az  = float(np.degrees(ev.get('az', 0)))
            el  = float(np.degrees(ev.get('el', 0)))
            az1 = float(np.degrees(ev.get('az_end', ev.get('az', 0))))
            el1 = float(np.degrees(ev.get('el_end', ev.get('el', 0))))
            if abs(az1-az) > 0.5 or abs(el1-el) > 0.5:
                ax.annotate('', xy=(az1,el1), xytext=(az,el),
                            arrowprops=dict(arrowstyle='->', color=c, lw=0.8, alpha=0.45))
            ax.scatter([az], [el], c=c, s=18, alpha=0.8, zorder=5)

    patches = [mp.Patch(color=_col(r), label=f'REN{r+1}') for r in range(len(centers))]
    ax.legend(handles=patches, facecolor='#f0f0f5', edgecolor='#aaaacc',
              labelcolor=_FG, fontsize=7, loc='upper right')


def _draw_sfera_in(ax, evs):
    """HOA Sphere 3D. Disegna nell'ax 3D passato."""
    u=np.linspace(0,2*np.pi,40); v=np.linspace(0,np.pi,20)
    U,V=np.meshgrid(u,v)
    ax.plot_wireframe(np.cos(U)*np.sin(V),np.sin(U)*np.sin(V),np.cos(V),
                      color=_GRID,alpha=0.15,rstride=4,cstride=4,lw=0.5)
    t=np.linspace(0,2*np.pi,100)
    for a,b,c in [(np.cos(t),np.sin(t),t*0),(np.cos(t),t*0,np.sin(t)),(t*0,np.cos(t),np.sin(t))]:
        ax.plot(a,b,c,color=_GRID,lw=0.5,alpha=0.4)
    ni=_stato.nicchie_info
    usa_ren=_stato.forza_ren_2d>1e-6 and _stato.visualizza_ren_2d
    if usa_ren and ni and 19 in ni and 'centers' in ni[19]:
        rd=ni[19]; centers=rd['centers']; radii=rd['radii']
        k=int(_stato.ren_k); lam=float(_stato.ren_l); q=float(_stato.ren_q)
        phi=np.linspace(0,2*np.pi,1000)
        for i,(c_az,c_el) in enumerate(centers):
            r_mask=float(radii[i]); c=_col(i)
            r_val=np.exp(-lam*np.abs(np.sin(k*phi/2))**q); dist=r_val*r_mask
            cos_el_c=np.cos(c_el); sin_el_c=np.sin(c_el)
            cos_az_c=np.cos(c_az); sin_az_c=np.sin(c_az)
            cx=cos_el_c*cos_az_c; cy=cos_el_c*sin_az_c; cz=sin_el_c
            eaz_x=-sin_az_c; eaz_y=cos_az_c; eaz_z=0.0
            eel_x=-sin_el_c*cos_az_c; eel_y=-sin_el_c*sin_az_c; eel_z=cos_el_c
            dx=dist*np.cos(phi); dy=dist*np.sin(phi)
            px=cx+dx*eaz_x+dy*eel_x; py=cy+dx*eaz_y+dy*eel_y; pz=cz+dx*eaz_z+dy*eel_z
            norm=np.sqrt(px**2+py**2+pz**2); norm=np.where(norm<1e-10,1.0,norm)
            X=px/norm; Y=py/norm; Z=pz/norm
            ax.plot(X,Y,Z,color=c,lw=2.0,alpha=0.45,zorder=4)
            xc=np.cos(c_el)*np.cos(c_az); yc=np.cos(c_el)*np.sin(c_az); zc=np.sin(c_el)
            step=4
            for j in range(0,len(phi)-step,step):
                verts=[(xc,yc,zc),(X[j],Y[j],Z[j]),(X[j+step],Y[j+step],Z[j+step])]
                from mpl_toolkits.mplot3d.art3d import Poly3DCollection
                tri=Poly3DCollection([verts],alpha=0.05,zorder=2)
                tri.set_facecolor(c); tri.set_edgecolor('none')
                ax.add_collection3d(tri)
            ax.scatter([xc],[yc],[zc],c=c,s=80,marker='*',zorder=10)
    alpha_an=0.15 if (usa_ren and (_stato.anelli_az_attivi or _stato.anelli_el_attivi)) else 0.85
    lw_an=1.0 if usa_ren else 2.0
    if _stato.anelli_el_attivi and ni and 18 in ni:
        em,eM=ni[18]['mins'],ni[18]['maxs']
        az_r=np.linspace(-np.pi,np.pi,120)
        for r in range(len(em)):
            el_lo=np.clip(em[r],-np.pi/2,np.pi/2); el_hi=np.clip(eM[r],-np.pi/2,np.pi/2); c=_col(r)
            ax.plot(np.cos(el_lo)*np.cos(az_r),np.cos(el_lo)*np.sin(az_r),np.full_like(az_r,np.sin(el_lo)),color=c,lw=lw_an,alpha=alpha_an,zorder=1)
            ax.plot(np.cos(el_hi)*np.cos(az_r),np.cos(el_hi)*np.sin(az_r),np.full_like(az_r,np.sin(el_hi)),color=c,lw=lw_an,alpha=alpha_an,zorder=1)
    if _stato.anelli_az_attivi and ni and 17 in ni:
        am,aM=ni[17]['mins'],ni[17]['maxs']
        el_l=np.linspace(-np.pi/2,np.pi/2,80)
        for r in range(len(am)):
            az_lo=np.clip(am[r],-np.pi,np.pi); az_hi=np.clip(aM[r],-np.pi,np.pi); c=_col(r)
            ax.plot(np.cos(el_l)*np.cos(az_lo),np.cos(el_l)*np.sin(az_lo),np.sin(el_l),color=c,lw=lw_an,alpha=alpha_an,zorder=1)
            ax.plot(np.cos(el_l)*np.cos(az_hi),np.cos(el_l)*np.sin(az_hi),np.sin(el_l),color=c,lw=lw_an,alpha=alpha_an,zorder=1)
    tn=np.linspace(0,1,50)
    for i,eventi in enumerate(evs):
        if not eventi: continue
        for ev in eventi:
            if usa_ren: c_idx=int(ev.get('ren_region',i))
            elif _stato.anelli_el_attivi: c_idx=int(ev.get('el_band_idx',i))
            elif _stato.anelli_az_attivi: c_idx=int(ev.get('az_band_idx',i))
            else: c_idx=i
            c=_col(c_idx)
            az0=float(ev.get('az',0)); az1=float(ev.get('az_end',az0))
            el0=float(ev.get('el',0)); el1=float(ev.get('el_end',el0))
            tm=float(ev.get('type_mov_amb',1)); pa=float(ev.get('prox_amp',1)); amp=float(ev.get('amp',0.3))
            sh=_transeg(tn,tm)
            az_p=az0+(az1-az0)*sh; el_p=el0+(el1-el0)*sh
            th=np.linspace(0,1,25)
            pr=np.concatenate([1+(pa-1)*_transeg(th,float(ev.get('type_prox_amb',1))),
                                pa+(1-pa)*_transeg(th,-float(ev.get('type_prox_amb',1)))])
            xp=pr*np.cos(el_p)*np.cos(az_p); yp=pr*np.cos(el_p)*np.sin(az_p); zp=pr*np.sin(el_p)
            ax.plot(xp,yp,zp,color=c,lw=1.1,alpha=np.clip(0.2+amp*0.6,0.1,0.9),zorder=5)
            ax.scatter([xp[0]],[yp[0]],[zp[0]],c=c,s=18,alpha=0.85,zorder=6)
    ax.set_xlim(-1.1,1.1); ax.set_ylim(-1.1,1.1); ax.set_zlim(-1.1,1.1)
    ax.set_box_aspect([1,1,1])
    n_lbl=len(ni[19]['centers']) if (usa_ren and ni and 19 in ni) else len(evs)
    pref='REN' if usa_ren else ('EL' if _stato.anelli_el_attivi else ('AZ' if _stato.anelli_az_attivi else 'R'))
    ax.legend(handles=[mp.Patch(color=_col(r),label=f'{pref}{r+1}') for r in range(n_lbl)],
              facecolor='#f0f0f5',edgecolor='#aaaacc',labelcolor=_FG,fontsize=7,loc='upper left')

def _refresh():
    fig=_stato.fig; sel=_stato.selezionate; evs=_stato.eventi
    if _stato.ax_plot is not None:
        _stato.ax_plot.remove(); _stato.ax_plot=None

    modo = _stato.modo

    # ── SFERA 3D ─────────────────────────────────────────────────────
    if modo == 'sfera':
        ax = fig.add_subplot(fig._gs_plot[0,0], projection='3d')
        ax.set_position([0.03, 0.04, 0.74, 0.93])
        ax.set_facecolor(_BG)
        for p in [ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane]:
            p.fill = False; p.set_edgecolor(_GRID)
        ax.tick_params(colors=_FG, labelsize=7)
        ax.set_title('HOA Sphere', color=_FG, fontsize=12)
        _draw_sfera_in(ax, evs)
        _stato.ax_plot=ax; fig.canvas.draw_idle(); return

    # ── RINGS 2D ────────────────────────────────────────────────────
    if modo == 'anelli':
        ax = fig.add_subplot(fig._gs_plot[0,0])
        ax.set_position([0.03, 0.04, 0.74, 0.93])
        _draw_anelli_in(ax, evs)
        _stato.ax_plot=ax; fig.canvas.draw_idle(); return

    # ── REN 2D MAPPA ─────────────────────────────────────────────────
    if modo == 'ren2d':
        ax = fig.add_subplot(fig._gs_plot[0,0])
        ax.set_position([0.03, 0.04, 0.74, 0.93])
        _draw_ren2d_in(ax, evs)
        _stato.ax_plot=ax; fig.canvas.draw_idle(); return

    # ── NORMAL ───────────────────────────────────────────────────────
    ax=fig.add_subplot(fig._gs_plot[0,0])
    ax.set_position([0.03, 0.04, 0.74, 0.93])
    if not sel:
        ax.set_facecolor(_PLOT_BG); ax.tick_params(colors=_FG)
        for sp in ax.spines.values(): sp.set_edgecolor(_GRID)
        ax.text(0.5,0.5,'Select a dimension',ha='center',va='center',
                transform=ax.transAxes,color='#888899',fontsize=13)
        ax.set_xticks([]); ax.set_yticks([])
    else:
        ss=frozenset(sel)
        if ss>=frozenset(['freq_start','freq_end','type_gliss']): _draw_gliss(ax,evs)
        elif 'gliss' in sel: _draw_gliss(ax,evs)
        elif ss>=frozenset(['az','az_end','type_mov_amb']): _draw_mov(ax,evs,'az','az_end')
        elif ss>=frozenset(['el','el_end','type_mov_amb']): _draw_mov(ax,evs,'el','el_end')
        elif ss>=frozenset(['freq_mod1','freq_mod2','type_freq_mod']): _draw_fm_curva(ax,evs,'freq_mod','freq_mod1','freq_mod2')
        elif ss>=frozenset(['freq_amp1','freq_amp2','type_freq_amp']): _draw_fm_curva(ax,evs,'freq_amp','freq_amp1','freq_amp2')
        else: _draw_2d(ax,evs,sel)
    _stato.ax_plot=ax; fig.canvas.draw_idle()

# ── Stile btn ─────────────────────────────────────────────────────────────────
def _bstyle(key, on):
    btn=_stato.bottoni.get(key)
    if btn is None: return
    c_on=_KEY_COLOR.get(key,'#cdd6f4')
    face=c_on if on else '#f0f0f5'
    lbl=f'● {_KEY_LABEL.get(key,key)}' if on else f'○ {_KEY_LABEL.get(key,key)}'
    btn.label.set_text(lbl); btn.label.set_color('#111' if on else _FG)
    btn.color=face; btn.hovercolor=c_on
    btn.ax.set_facecolor(face)
    for sp in btn.ax.spines.values():
        sp.set_edgecolor(c_on if on else '#aaaacc')
        sp.set_linewidth(1.4 if on else 0.6)

def _make_cb(key):
    def cb(event):
        sel=_stato.selezionate
        _stato.modo='normal'
        if key in sel: sel.remove(key); _bstyle(key,False)
        else:
            new=frozenset(sel+[key])
            ok=any(new<=g for g in _COPPIE) or any(new>=g for g in _COPPIE) or not sel
            if not ok:
                for k in list(sel): _bstyle(k,False)
                sel.clear()
            sel.append(key); _bstyle(key,True)
        _refresh()
    return cb

def cb_dur(event):
    _stato.durata_on=not _stato.durata_on
    btn=_stato.bottoni.get('_dur')
    if btn is None: return
    on=_stato.durata_on
    face='#f9e2af' if on else '#f5e8c0'
    btn.label.set_text('● Dur ON' if on else '○ Dur OFF')
    btn.label.set_color('#111' if on else _FG)
    btn.color=face; btn.hovercolor=face; btn.ax.set_facecolor(face)
    for sp in btn.ax.spines.values():
        sp.set_edgecolor('#89dceb' if on else '#aaaacc')
        sp.set_linewidth(1.4 if on else 0.6)
    _refresh()

# ── Build figura ──────────────────────────────────────────────────────────────
_BW  = 0.21; _BX  = 0.785; _BH  = 0.014; _HH  = 0.012; _G   = 0.001
_N_ROWS = len(_BUTTONS); _PANEL_H = _N_ROWS * (_BH + _G) + _G
_scroll = {'offset': 0.0, 'axes': [], 'step': _BH + _G}

def _applica_scroll():
    for ax, y_orig in _scroll['axes']:
        pos = ax.get_position()
        ax.set_position([pos.x0, y_orig + _scroll['offset'], pos.width, pos.height])
    _stato.fig.canvas.draw_idle()

def _on_scroll(event):
    if event.x < _stato.fig.get_size_inches()[0] * _stato.fig.dpi * _BX:
        return
    step = _scroll['step']
    if event.button == 'up':
        max_scroll = -(_N_ROWS * (_BH + _G) - 0.95)
        _scroll['offset'] = max(_scroll['offset'] - step * 2, max_scroll)
    elif event.button == 'down':
        _scroll['offset'] = min(_scroll['offset'] + step * 2, 0.0)
    _applica_scroll()

def _build_fig():
    fig=plt.figure(figsize=(19,11),facecolor=_BG)
    try: fig.canvas.manager.set_window_title('Hutchinson Synthesis — Visualizzatore')
    except: pass
    gs=gridspec.GridSpec(1,1,figure=fig,bottom=0.04,top=0.97,left=0.03,right=0.76)
    fig._gs_plot=gs
    _stato.bottoni.clear(); _stato.selezionate.clear()
    _scroll['axes'].clear(); _scroll['offset'] = 0.0
    y = 0.975
    for key, label, color, _ in _BUTTONS:
        y -= (_HH if key is None else _BH) + _G
        y_orig = y
        if key is None:
            ax=fig.add_axes([_BX, y, _BW, _HH])
            ax.set_facecolor('#f0f0f5'); ax.axis('off')
            for sp in ax.spines.values(): sp.set_edgecolor(color); sp.set_linewidth(0.6)
            ax.text(0.5,0.5,label,ha='center',va='center',color=color,
                    fontsize=6,fontweight='bold',transform=ax.transAxes)
            _scroll['axes'].append((ax, y_orig))
            continue
        if key == '_anelli':
            ax=fig.add_axes([_BX, y, _BW, _BH])
            ax.set_facecolor('#daeaf8')
            for sp in ax.spines.values(): sp.set_edgecolor('#74c7ec'); sp.set_linewidth(1.2)
            btn=Button(ax,label,color='#daeaf8',hovercolor='#b8d8f0')
            btn.label.set_color('#1a7ab0'); btn.label.set_fontsize(6.5)
            btn.label.set_fontweight('bold')
            btn.on_clicked(lambda e: [setattr(_stato,'modo','anelli'), _refresh()])
            _stato.bottoni[key]=btn
            _scroll['axes'].append((ax, y_orig))
            continue
        if key == '_ren2d':
            ax=fig.add_axes([_BX, y, _BW, _BH])
            ax.set_facecolor('#d0f0e0')
            for sp in ax.spines.values(): sp.set_edgecolor('#a6e3a1'); sp.set_linewidth(1.2)
            btn=Button(ax,label,color='#d0f0e0',hovercolor='#a0dfc0')
            btn.label.set_color('#2a8050'); btn.label.set_fontsize(6.5)
            btn.label.set_fontweight('bold')
            btn.on_clicked(lambda e: [setattr(_stato,'modo','ren2d'), _refresh()])
            _stato.bottoni[key]=btn
            _scroll['axes'].append((ax, y_orig))
            continue
        if key == '_sfera':
            ax=fig.add_axes([_BX, y, _BW, _BH])
            ax.set_facecolor('#ead8f8')
            for sp in ax.spines.values(): sp.set_edgecolor(color); sp.set_linewidth(1.2)
            btn=Button(ax,label,color='#ead8f8',hovercolor='#d0b0f0')
            btn.label.set_color('#7733bb'); btn.label.set_fontsize(6.5)
            btn.label.set_fontweight('bold')
            btn.on_clicked(lambda e: [setattr(_stato,'modo','sfera'), _refresh()])
            _stato.bottoni[key]=btn
            _scroll['axes'].append((ax, y_orig))
            continue
        if key == '_dur':
            ax=fig.add_axes([_BX, y, _BW, _BH])
            ax.set_facecolor('#f9e2af')
            for sp in ax.spines.values(): sp.set_edgecolor('#89dceb'); sp.set_linewidth(1.3)
            btn=Button(ax,'● Dur ON',color='#f9e2af',hovercolor='#f9e2af')
            btn.label.set_color('#111'); btn.label.set_fontsize(6.5)
            btn.on_clicked(cb_dur)
            _stato.bottoni[key]=btn
            _scroll['axes'].append((ax, y_orig))
            continue
        ax=fig.add_axes([_BX, y, _BW, _BH])
        ax.set_facecolor('#f0f0f5')
        for sp in ax.spines.values(): sp.set_edgecolor('#aaaacc'); sp.set_linewidth(0.6)
        btn=Button(ax,f'○ {label}',color='#f0f0f5',hovercolor='#e0e0ee')
        btn.label.set_color(_FG); btn.label.set_fontsize(6)
        btn.label.set_ha('left'); btn.label.set_x(0.05)
        btn.on_clicked(_make_cb(key))
        _stato.bottoni[key]=btn
        _scroll['axes'].append((ax, y_orig))
    fig.canvas.mpl_connect('scroll_event', _on_scroll)
    return fig

# ── Entry point ───────────────────────────────────────────────────────────────
def mostra_tutto(lista_eventi_per_niche, nicchie_info=None,
                 forza_ren_2d=0.0,
                 liberta_ren_raggio=0.0,
                 anelli_az_attivi=False, anelli_el_attivi=False,
                 visualizza_ren_2d=True,
                 ren_k=5, ren_l=2.0, ren_q=2.0):
    _stato.eventi = lista_eventi_per_niche
    _stato.nicchie_info = nicchie_info
    _stato.forza_ren_2d = float(forza_ren_2d)
    _stato.liberta_ren_raggio = float(liberta_ren_raggio)
    _stato.anelli_az_attivi = bool(anelli_az_attivi)
    _stato.anelli_el_attivi = bool(anelli_el_attivi)
    _stato.visualizza_ren_2d = bool(visualizza_ren_2d)
    _stato.ren_k = int(ren_k)
    _stato.ren_l = float(ren_l)
    _stato.ren_q = float(ren_q)
    _stato.durata_on = True
    fig = _build_fig(); _stato.fig = fig
    _stato.selezionate.append('freq_start')
    _bstyle('freq_start', True); _refresh()
    plt.show()