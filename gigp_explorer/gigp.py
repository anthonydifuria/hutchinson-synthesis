"""
gigp.py — Hutchinson Synthesis
Generalized Immanantal Gibbs Process (GIGP)

Formula:  P(X) ∝  Λ(X)  ·  Imm_β(K)  ·  exp(-H(X))

Pezzo 1 — Λ: come vengono generati i candidati
    'uniforme'     → U[0,1]
    'lgcp'         → dense and sparse zones random
    'alpha_stable' → heavy tails, extreme events rari

Pezzo 2 — Imm_β(K): kernel + campionamento
    beta=-1  → DPP    → repulsione, nicchie separate
    beta=0   → Poisson → casuale
    beta=+1  → Permanental → attrazione, clustering

    kernel_tipo='gaussiano' → exp(-r²/2σ²)
    kernel_tipo='matern'    → (1+√3·r/σ)·exp(-√3·r/σ)  [Matérn ν=3/2]
    Matérn è DPP con kernel diverso: separa i punti rispettando
    la geometria dello spazio in modo più regolare del gaussiano.

Pezzo 3 — exp(-H): energia di Gibbs
    strauss → distanza minima tra punti
    hawkes  → auto-eccitazione temporale

Solo numpy. Zero librerie esterne.
"""

import numpy as np


# ============================================================
# CONFIGURAZIONE PER DIMENSIONE
# ============================================================

class ConfigDimensione:
    """
    beta : float in [-1,+1]
        -1   → DPP (repulsione massima)
        -0.5 → β-ensemble (repulsione moderata)
         0   → Poisson (no interaction)
        +1   → Permanental (attrazione massima)

    sigma : float > 0
        Kernel length scale.

    kernel_tipo : str
        'gaussiano' → kernel RBF. Default per DPP, β-ensemble, Permanental.
        'matern'    → kernel Matérn ν=3/2. Usa con beta=-1.
                      Separates points respecting space geometry.

    lambda_tipo : str
        'uniforme'     → U[0,1]. Default.
        'lgcp'         → Log-Gaussian Cox: dense and sparse zones.
        'alpha_stable' → heavy tails, rare extreme events.

    w_strauss, R_strauss : Strauss energy (exclusion zone).
    w_hawkes, decay_hawkes : Hawkes energy (temporal clustering).
    """

    def __init__(self,
                 beta=         -1.0,
                 sigma=         0.3,
                 kernel_tipo=  'gaussiano',
                 lambda_tipo=  'uniforme',
                 lgcp_sigma=    0.5,
                 alpha_index=   1.5,
                 w_strauss=     0.0,
                 R_strauss=     0.1,
                 w_hawkes=      0.0,
                 decay_hawkes=  5.0):

        self.beta         = float(np.clip(beta, -1.0, 1.0))
        self.sigma        = float(max(sigma, 1e-6))
        self.kernel_tipo  = kernel_tipo
        self.lambda_tipo  = lambda_tipo
        self.lgcp_sigma   = float(max(lgcp_sigma, 0.01))
        self.alpha_index  = float(np.clip(alpha_index, 0.1, 2.0))
        self.w_strauss    = float(max(w_strauss, 0.0))
        self.R_strauss    = float(np.clip(R_strauss, 0.0, 1.0))
        self.w_hawkes     = float(max(w_hawkes, 0.0))
        self.decay_hawkes = float(max(decay_hawkes, 0.01))


# ============================================================
# SHORTCUTS
# ============================================================


# ============================================================
# INTERFACCIA GIGP() — sintassi unificata a 3 argomenti
# ============================================================

def gigp(lambda_tipo='uniforme', beta=0.0, kernel=None,
         sigma=0.3, n_dims=None,
         w_strauss=0.0, R_strauss=0.1,
         w_hawkes=0.0,  decay_hawkes=5.0,
         lgcp_sigma=0.5, alpha_index=1.5):
    """
    Interfaccia unificata GIGP a 3 argomenti principali.

    gigp(lambda_tipo, beta, kernel)

    Argomento 1 — lambda_tipo: distribuzione di base (Pezzo 1)
        'uniforme'     -> densita' piatta, nessuna preferenza
        'lgcp'         -> dense and sparse zones (Log-Gaussian Cox)
        'alpha_stable' -> heavy tails, extreme events

    Argomento 2 — beta: continuo repulsione/attrazione (Pezzo 2)
        -1.0  -> pure DPP (maximum repulsion)
        -0.5  -> moderate repulsion (beta-ensemble)
         0.0  -> Poisson (no interaction)
        +0.5  -> moderate attraction (beta-ensemble)
        +1.0  -> Permanental (maximum attraction)

    Argomento 3 — kernel: forma dell'interazione (Pezzo 2 + Pezzo 3)
        None        -> gaussian kernel (default)
        'gaussiano' -> kernel RBF, smooth interaction
        'matern'    -> kernel Matern nu=3/2, more regular than gaussian
        'strauss'   -> hard exclusion zone (Pezzo 3)
        'hawkes'    -> self-exciting temporal clustering (Pezzo 3)

    Nota: con kernel='matern' il beta e' attivo e controlla
    repulsione/attrazione con geometria Matern.
    Con kernel='strauss' o 'hawkes' il beta viene forzato a 0
    perche' l'interazione e' gestita dal termine energetico.

    Esempi:
        gigp('uniforme', beta=-1.0, kernel='matern')   # Matern puro
        gigp('uniforme', beta=0.0,  kernel=None)       # Poisson
        gigp('uniforme', beta=-1.0, kernel='gaussiano')# DPP
        gigp('uniforme', beta=+1.0, kernel='gaussiano')# Permanental
        gigp('uniforme', beta=0.0,  kernel='strauss')  # Strauss
        gigp('uniforme', beta=0.0,  kernel='hawkes')   # Hawkes
        gigp('lgcp',     beta=0.0,  kernel=None)       # LGCP
        gigp('alpha_stable', beta=0.0, kernel=None)    # Alpha-Stable

    n_dims: se specificato restituisce una lista di n_dims ConfigDimensione
            identiche (per uso con CONFIGS_GIGP_NICHES)
    """
    # Kernel speciali -> energia Gibbs (beta=0, kernel gaussiano di base)
    if kernel in ('strauss', 'hawkes'):
        cfg = ConfigDimensione(
            beta         = 0.0,
            sigma        = sigma,
            kernel_tipo  = 'gaussiano',
            lambda_tipo  = lambda_tipo,
            w_strauss    = w_strauss if kernel == 'strauss' else 0.0,
            R_strauss    = R_strauss if kernel == 'strauss' else 0.1,
            w_hawkes     = w_hawkes  if kernel == 'hawkes'  else 0.0,
            decay_hawkes = decay_hawkes,
            lgcp_sigma   = lgcp_sigma,
            alpha_index  = alpha_index,
        )
        if kernel == 'strauss' and w_strauss == 0.0:
            cfg.w_strauss = 3.0
        if kernel == 'hawkes' and w_hawkes == 0.0:
            cfg.w_hawkes = 2.0

    else:
        kernel_tipo = kernel if kernel in ('gaussiano', 'matern') else 'gaussiano'
        cfg = ConfigDimensione(
            beta         = float(np.clip(beta, -1.0, 1.0)),
            sigma        = sigma,
            kernel_tipo  = kernel_tipo,
            lambda_tipo  = lambda_tipo,
            lgcp_sigma   = lgcp_sigma,
            alpha_index  = alpha_index,
        )

    if n_dims is not None:
        return [cfg] * int(n_dims)
    return cfg

def config_dpp_puro(sigma=0.3):
    """DPP puro per tutte le 6 dimensioni. Backward-compatible con dpp.py."""
    return [ConfigDimensione(beta=-1.0, sigma=sigma) for _ in range(6)]


def config_preset(distribuzione, sigma=0.3, n_dims=6, **kwargs):
    """
    Applica una distribuzione a tutte e 6 le dimensioni.
    Ogni preset usa solo il meccanismo della sua distribuzione.

    Pezzo 2 (kernel+beta):
        'dpp'         → beta=-1, kernel gaussiano
        'matern'      → beta=-1, kernel Matérn ν=3/2
        'beta_soft'   → beta=-0.5, kernel gaussiano
        'poisson'     → beta=0
        'permanental' → beta=+1, kernel gaussiano

    Pezzo 3 (energia Gibbs):
        'strauss'     → beta=0, w_strauss=3.0, R_strauss=0.1
        'hawkes'      → beta=0, w_hawkes=2.0, decay_hawkes=5.0

    Pezzo 1 (intensità):
        'lgcp'         → beta=0, lambda_tipo='lgcp'
        'alpha_stable' → beta=0, lambda_tipo='alpha_stable'
    """
    preset = {
        'dpp':          dict(beta=-1.0, sigma=sigma, kernel_tipo='gaussiano'),
        'matern':       dict(beta=-1.0, sigma=sigma, kernel_tipo='matern'),
        'beta_soft':    dict(beta=-0.5, sigma=sigma, kernel_tipo='gaussiano'),
        'poisson':      dict(beta= 0.0, sigma=sigma),
        'permanental':  dict(beta=+1.0, sigma=sigma, kernel_tipo='gaussiano'),
        'strauss':      dict(beta= 0.0, sigma=sigma, w_strauss=3.0, R_strauss=0.1),
        'hawkes':       dict(beta= 0.0, sigma=sigma, w_hawkes=2.0,  decay_hawkes=5.0),
        'lgcp':         dict(beta= 0.0, sigma=sigma, lambda_tipo='lgcp'),
        'alpha_stable': dict(beta= 0.0, sigma=sigma, lambda_tipo='alpha_stable'),
    }
    if distribuzione not in preset:
        nomi = ', '.join(f"'{k}'" for k in preset)
        raise ValueError(f"'{distribuzione}' non trovata. Disponibili: {nomi}")
    params = {**preset[distribuzione], **kwargs}
    return [ConfigDimensione(**params) for _ in range(n_dims)]


def config_da_separazione(sep_tempo, sep_freq, sep_amp, sep_spazio, sigma=0.3):
    """Backward-compatible con dpp.py: separazione in [0,1] → beta in [-1,0]."""
    def s2b(s): return -float(np.clip(s, 0.0, 1.0))
    return [
        ConfigDimensione(beta=s2b(sep_tempo),  sigma=sigma),
        ConfigDimensione(beta=s2b(sep_tempo),  sigma=sigma),
        ConfigDimensione(beta=s2b(sep_freq),   sigma=sigma),
        ConfigDimensione(beta=s2b(sep_amp),    sigma=sigma),
        ConfigDimensione(beta=s2b(sep_spazio), sigma=sigma),
        ConfigDimensione(beta=s2b(sep_spazio), sigma=sigma),
    ]


# ============================================================
# PEZZO 1 — LAMBDA: GENERAZIONE CANDIDATI
# ============================================================

def _genera_candidati_lambda(n_candidati, configs, rng):
    D = len(configs)
    C = np.zeros((n_candidati, D))

    for d, cfg in enumerate(configs):

        if cfg.lambda_tipo == 'lgcp':
            n_centri = max(3, n_candidati // 15)
            centri   = rng.random(n_centri)
            ampiezze = rng.exponential(scale=1.0, size=n_centri)
            x_grid   = np.linspace(0.0, 1.0, 500)
            campo    = np.zeros(500)
            for c_pos, c_amp in zip(centri, ampiezze):
                campo += c_amp * np.exp(-(x_grid - c_pos)**2 / (2.0 * cfg.lgcp_sigma**2))
            campo   = campo / campo.sum()
            C[:, d] = rng.choice(x_grid, size=n_candidati, p=campo)

        elif cfg.lambda_tipo == 'alpha_stable':
            alpha = cfg.alpha_index
            if alpha <= 1.0:
                raw = rng.standard_cauchy(n_candidati)
            else:
                raw = rng.standard_normal(n_candidati) * (2.0 / alpha)
            C[:, d] = np.clip(1.0 / (1.0 + np.exp(-raw)), 0.0, 1.0)

        else:
            C[:, d] = rng.random(n_candidati)

    return C


# ============================================================
# PEZZO 2 — KERNEL
# ============================================================

def _costruisci_kernel(C, configs, sigma_base):
    """
    Kernel globale calcolato sulla distanza pesata combinata.

    r_totale = sqrt( sum_d (gamma_d * diff_d)² )

    gaussiano: K = exp( -r_totale² / (2σ²) )
    matern:    K = (1 + √3·r_totale/σ) · exp(-√3·r_totale/σ)  [ν=3/2]

    La distanza combinata evita il collasso del prodotto multi-dimensionale.
    gamma_d = 0.5 + |beta_d| * 9.5  (range [0.5, 10])

    Matérn vs Gaussiano: a parità di distanza, Matérn decade più lentamente
    (coda più pesante). I punti si respingono su un raggio più ampio, la
    distribuzione risultante è geometricamente più uniforme e regolare.
    """
    diff     = C[:, None, :] - C[None, :, :]   # (N, N, D)
    D        = len(configs)
    gammas   = np.array([(0.1 + abs(cfg.beta) * 0.9) / np.sqrt(D) for cfg in configs])  # scala con 1/sqrt(D) — significativo in qualsiasi dimensione

    # Distanza euclidea pesata per dimensione (scalare per ogni coppia)
    sq       = np.sum((diff * gammas[None, None, :]) ** 2, axis=-1)   # (N, N)
    r_totale = np.sqrt(sq)                                             # (N, N)

    # Kernel: usa il tipo della prima dimensione con kernel != 'gaussiano',
    # oppure 'gaussiano' se tutte le dimensioni usano il default.
    # (Il kernel_tipo è una proprietà del processo, non della singola dimensione.)
    usa_matern = any(cfg.kernel_tipo == 'matern' for cfg in configs)
       

    if usa_matern:
        # Matérn ν=3/2: K(r) = (1 + √3·r/σ) · exp(-√3·r/σ)
        arg = np.sqrt(3.0) * r_totale / sigma_base
        K   = (1.0 + arg) * np.exp(-arg)
    else:
        # Gaussiano: K(r) = exp(-r²/2σ²)
        K   = np.exp(-sq / (2.0 * sigma_base ** 2))

    return K


def _campiona_dpp_spettrale(K, rng):
    N                         = K.shape[0]
    eigenvalues, eigenvectors = np.linalg.eigh(K)
    eigenvalues               = np.real(eigenvalues)
    eigenvectors              = np.real(eigenvectors)

    probs = eigenvalues / (1.0 + eigenvalues)
    mask  = rng.random(N) < probs
    idx_v = np.where(mask)[0]

    if len(idx_v) == 0:
        return [int(np.argmax(eigenvalues))]

    V = eigenvectors[:, idx_v].copy()
    k = V.shape[1]
    punti = []

    for i in range(k):
        p = np.clip(np.sum(V**2, axis=1), 0.0, None)
        s = p.sum()
        if s < 1e-12:
            break
        idx = int(rng.choice(N, p=p / s))
        punti.append(idx)
        if i < k - 1 and V.shape[1] > 1:
            e = V[idx].copy()
            n = np.linalg.norm(e)
            if n > 1e-10:
                e = e / n
                V = V - np.outer(V @ e, e)
            Q, _ = np.linalg.qr(V)
            V    = Q[:, :k - i - 1]

    return punti


def _campiona_permanental(K, n_target, rng):
    N     = K.shape[0]
    n_sel = max(1, min(n_target, N // 2))
    q     = np.diag(K)
    q     = q / (q.sum() + 1e-12)
    primo = int(rng.choice(N, p=q))
    sel   = [primo]
    mask  = np.ones(N, dtype=bool)
    mask[primo] = False

    for _ in range(n_sel - 1):
        disp = np.where(mask)[0]
        if len(disp) == 0:
            break
        sim = K[disp[:, None], sel].mean(axis=1)
        sim = np.clip(sim, 0.0, None)
        s   = sim.sum()
        if s < 1e-12:
            break
        c = int(disp[rng.choice(len(disp), p=sim / s)])
        sel.append(c)
        mask[c] = False

    return sel


def _campiona_immanante(K, configs, rng):
    betas = np.array([cfg.beta for cfg in configs])
    pesi  = np.array([abs(cfg.beta) for cfg in configs])
    N     = K.shape[0]

    if pesi.sum() < 1e-12:
        return list(rng.choice(N, size=max(1, N // 5), replace=False))

    beta_m = float(np.average(betas, weights=pesi + 1e-12))

    if abs(beta_m) < 0.02:
        return list(rng.choice(N, size=max(1, N // 5), replace=False))
    elif beta_m < 0:
        forza = abs(beta_m)
        return _campiona_dpp_spettrale(forza * K + (1 - forza) * np.eye(N), rng)
    else:
        ev     = np.clip(np.real(np.linalg.eigvalsh(K)), 0.0, None)
        n_t    = max(1, int(round(np.sum(ev / (1.0 + ev)))))
        K_eff  = beta_m * K + (1 - beta_m) * np.eye(N)
        return _campiona_permanental(K_eff, n_t, rng)


# ============================================================
# PEZZO 3 — ENERGIA DI GIBBS
# ============================================================

def _calcola_energia_gibbs(C_subset, configs):
    """
    Strauss: penalizza coppie con distanza < R su dimensione d.
    Hawkes:  premia clustering su dimensione d (energia negativa).
             Agisce su qualsiasi dimensione con w_hawkes > 0.
             Nessun vincolo hardcoded su nessuna dimensione.
    """
    k = len(C_subset)
    if k < 2:
        return 0.0
    C_s    = np.array(C_subset)
    H      = 0.0
    diff_d = np.abs(C_s[:, None, :] - C_s[None, :, :])

    for d, cfg in enumerate(configs):
        if cfg.w_strauss > 0.0:
            tc = diff_d[:, :, d] < cfg.R_strauss
            np.fill_diagonal(tc, False)
            H += cfg.w_strauss * float(np.sum(tc)) / 2.0

        if cfg.w_hawkes > 0.0:
            x  = C_s[:, d]
            ha = 0.0
            for i in range(k):
                for j in range(k):
                    dx = x[j] - x[i]
                    if dx > 1e-10:
                        ha += np.exp(-cfg.decay_hawkes * dx)
            H -= cfg.w_hawkes * ha

    return H


def _metropolis_gibbs(C_sel, configs, rng, n_passi=5):
    H = _calcola_energia_gibbs(C_sel, configs)
    if abs(H) < 1e-10:
        return C_sel
    C = C_sel.copy()
    D = C.shape[1]
    for _ in range(n_passi):
        Cp      = C.copy()
        idx     = int(rng.integers(len(C)))
        Cp[idx] = np.clip(Cp[idx] + rng.normal(0.0, 0.05, D), 0.0, 1.0)
        Hp      = _calcola_energia_gibbs(Cp, configs)
        dH      = Hp - H
        if dH < 0.0 or rng.random() < np.exp(-dH):
            C = Cp; H = Hp
    return C



# ============================================================
# CAMPIONAMENTO ESATTO — N PUNTI PRECISI
# ============================================================

def _dpp_greedy_esatto(K, n_target):
    """
    MAP inference per DPP: seleziona esattamente n_target punti
    massimizzando det(K_S) con selezione greedy.
    Usato per generare esattamente N centroidi di nicchie.
    """
    N = K.shape[0]
    n = min(n_target, N)
    sel  = []
    disp = list(range(N))

    for _ in range(n):
        migliore    = None
        det_migliore = -np.inf
        for idx in disp:
            cand    = sel + [idx]
            K_sub   = K[np.ix_(cand, cand)]
            det_val = float(K_sub[0, 0]) if len(cand) == 1 else float(np.linalg.det(K_sub))
            if det_val > det_migliore:
                det_migliore = det_val
                migliore     = idx
        if migliore is None:
            break
        sel.append(migliore)
        disp.remove(migliore)

    return sel


def _lhs_esatto(n, D, rng):
    """
    Latin Hypercube Sampling: genera n punti in [0,1]^D con copertura
    uniforme garantita su ogni asse.
    Per ogni asse, divide [0,1] in n segmenti e assegna uno a ogni punto.
    Questo è il comportamento corretto di Matérn su pochi punti:
    distribuzione geometricamente regolare indipendentemente da n e D.
    """
    seg  = 1.0 / n
    C    = np.zeros((n, D))
    for d in range(D):
        perm   = rng.permutation(n)
        C[:, d] = perm * seg + seg / 2.0  # centro fisso dello strato
    return C


def campiona_gigp_esatto(C_candidati, configs, sigma_base, n_target, rng):
    """
    Come campiona_gigp() ma restituisce esattamente n_target punti.
    Usato per generare i centroidi delle nicchie.

    P(X) ∝ Λ(X) · Imm_β(K) · exp(-H(X))

    Matérn usa Latin Hypercube Sampling — distribuzione geometricamente
    regolare garantita anche con pochi punti in molte dimensioni.
    DPP usa greedy MAP — massima diversità tra i candidati.
    """
    N      = len(C_candidati)
    n      = min(n_target, N)
    D      = C_candidati.shape[1]

    # Matérn: LHS garantisce copertura uniforme su ogni asse
    usa_matern = any(cfg.kernel_tipo == 'matern' for cfg in configs)
    if usa_matern:
        return _lhs_esatto(n, D, rng)

    K      = _costruisci_kernel(C_candidati, configs, sigma_base)
    betas  = np.array([cfg.beta for cfg in configs])
    pesi   = np.array([abs(cfg.beta) for cfg in configs])

    if pesi.sum() < 1e-12:
        # Poisson: selezione random
        indici = list(rng.choice(N, size=n, replace=False))

    else:
        beta_m = float(np.average(betas, weights=pesi + 1e-12))

        if beta_m <= 0:
            # DPP: greedy MAP — massima diversità
            forza  = abs(beta_m)
            L_eff  = forza * K + (1 - forza) * np.eye(N)
            indici = _dpp_greedy_esatto(L_eff, n)
        else:
            # Permanental: greedy similarity — massima coesione
            forza  = beta_m
            K_eff  = forza * K + (1 - forza) * np.eye(N)
            indici = _campiona_permanental(K_eff, n, rng)

        # Aggiusta se necessario
        if len(indici) < n:
            mancanti = [i for i in range(N) if i not in indici]
            indici  += list(rng.choice(mancanti, size=n - len(indici), replace=False))

    C_sel = C_candidati[indici].copy()

    # Correzione Gibbs se ci sono termini energetici
    if any(cfg.w_strauss > 0.0 or cfg.w_hawkes > 0.0 for cfg in configs):
        C_sel = _metropolis_gibbs(C_sel, configs, rng)

    return C_sel


# ============================================================
# FORMULA GIGP COMPLETA
# ============================================================

def campiona_gigp(C_candidati, configs, sigma_base, rng):
    """P(X) ∝ Λ(X) · Imm_β(K) · exp(-H(X))"""
    K      = _costruisci_kernel(C_candidati, configs, sigma_base)
    indici = _campiona_immanante(K, configs, rng)
    if len(indici) == 0:
        indici = [int(rng.integers(len(C_candidati)))]
    C_sel  = C_candidati[indici].copy()
    if any(cfg.w_strauss > 0.0 or cfg.w_hawkes > 0.0 for cfg in configs):
        C_sel = _metropolis_gibbs(C_sel, configs, rng)
    return C_sel


# ============================================================
# INTERFACCIA PRINCIPALE
# ============================================================

def genera_eventi_gigp(niche, t_campionamento, durata_totale,
                       n_candidati=200, sigma_base=0.3,
                       configs=None, rng=None):
    """
    Drop-in replacement di genera_eventi_dpp().
    configs=None → DPP automatico da separazione_* della Nicchia.
    """
    if rng is None:
        rng = np.random.default_rng()
    if configs is None:
        configs = config_da_separazione(
            niche.separazione_tempo, niche.separazione_freq,
            niche.separazione_amp,   niche.separazione_spazio,
            sigma=sigma_base)

    bounds     = niche.bounds_a(t_campionamento, durata_totale)
    onset_min,  onset_max  = bounds['onset']
    durata_min, durata_max = bounds['durata']
    freq_min,   freq_max   = bounds['freq']
    fend_min,   fend_max   = bounds['freq_end']   # range indipendente per freq_end
    amp_min,    amp_max    = bounds['amp']
    aend_min,   aend_max   = bounds['amp_end']    # range indipendente per amp_end
    az_min,     az_max     = bounds['az']
    el_min,     el_max     = bounds['el']

    C     = _genera_candidati_lambda(n_candidati, configs, rng)
    C_sel = campiona_gigp(C, configs, sigma_base, rng)

    eventi = []
    for c in C_sel:
        onset     = onset_min  + c[0] * (onset_max  - onset_min)
        durata    = durata_min + c[1] * (durata_max - durata_min)
        freq      = freq_min   + c[2] * (freq_max   - freq_min)
        amp       = amp_min    + c[3] * (amp_max    - amp_min)
        az        = az_min     + c[4] * (az_max     - az_min)
        el        = el_min     + c[5] * (el_max     - el_min)

        # freq_end: dimensione indipendente — campionata dai suoi bounds.
        # LIBERTA=0 → bounds = cella start → glissa dentro la niche
        # LIBERTA>0 → bounds espansi → glissa verso altri range
        # prob_glissato (in _aggiunge_nuovi_params) decide SE l'evento glissa.
        freq_end = float(np.clip(
            fend_min + rng.random() * (fend_max - fend_min),
            min(freq_min, fend_min), max(freq_max, fend_max)))

        # amp_end: stesso meccanismo
        amp_end = float(np.clip(
            aend_min + rng.random() * (aend_max - aend_min),
            min(amp_min, aend_min), max(amp_max, aend_max)))

        perc      = float(np.clip(
            bounds['attack'][0] + rng.random() * (bounds['attack'][1] - bounds['attack'][0]),
            0.01, 0.99))

        eventi.append({
            'onset': float(onset), 'durata': float(durata),
            'freq_start': float(freq), 'freq_end': float(freq_end),
            'freq_min': float(freq_min), 'freq_max': float(freq_max),
            'amp': float(amp), 'amp_end': float(amp_end),
            'az': float(az), 'el': float(el),
            'perc': perc, 'n_sinusoidi': bounds['n_sin'],
        })

    return eventi

# ============================================================
# GIGP 1D — Per singola dimensione indipendente
# ============================================================

def genera_centroidi_gigp_1d(n, config, rng, sigma_base=0.3):
    """
    Genera n centroidi in 1D per una singola dimensione.
    Ogni dimensione ha la sua distribuzione GIGP indipendente.
    Restituisce array di n valori in [0,1].
    """
    n_candidati = max(n * 10, 100)
    C = _genera_candidati_lambda(n_candidati, [config], rng)   # (n_cand, 1)
    result = campiona_gigp_esatto(C, [config], sigma_base, n, rng)  # (n, 1)
    return result[:, 0]  # (n,)