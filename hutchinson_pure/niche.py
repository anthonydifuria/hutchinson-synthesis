"""
niche.py — Hutchinson Synthesis
Definisce NicchiaParametro e Nicchia come ipervolume N-dimensionale.
"""
import numpy as np

class NicchiaParametro:
    """
    Un singolo parametro della niche con curva temporale definita da breakpoint.
    valore_iniziale e valore_finale sono obbligatori.
    I breakpoint intermedi sono opzionali — lista di tuple (t_norm, valore)
    dove t_norm è in [0, 1] rispetto alla durata totale.
    """
    def __init__(self, valore_iniziale, valore_finale,
                 breakpoints=None, max_breakpoints=10,
                 interpolazione='lineare'):
        self.valore_iniziale   = float(valore_iniziale)
        self.valore_finale     = float(valore_finale)
        self.max_breakpoints   = max_breakpoints
        self.interpolazione    = interpolazione  # 'lineare' | 'esponenziale'
        self._breakpoints      = []
        for bp in (breakpoints or []):
            self.aggiungi_breakpoint(*bp)

    def aggiungi_breakpoint(self, t_norm, valore):
        if len(self._breakpoints) >= self.max_breakpoints:
            raise ValueError(f"Raggiunto max_breakpoints={self.max_breakpoints}")
        t_norm = float(np.clip(t_norm, 0.0, 1.0))
        self._breakpoints.append((t_norm, float(valore)))
        self._breakpoints.sort(key=lambda x: x[0])

    def valore_a(self, t, durata_totale):
        """Restituisce il valore del parametro al tempo t (secondi)."""
        t_norm = float(np.clip(t / durata_totale, 0.0, 1.0))
        punti  = ([(0.0, self.valore_iniziale)]
                  + self._breakpoints
                  + [(1.0, self.valore_finale)])
        for i in range(len(punti) - 1):
            t0, v0 = punti[i]
            t1, v1 = punti[i + 1]
            if t0 <= t_norm <= t1:
                if t1 == t0:
                    return v0
                alpha = (t_norm - t0) / (t1 - t0)
                if self.interpolazione == 'esponenziale' and v0 > 0 and v1 > 0:
                    return v0 * (v1 / v0) ** alpha
                return v0 + alpha * (v1 - v0)
        return self.valore_finale

    def range_a(self, t, durata_totale):
        """Restituisce (min, max) — alias comodo per parametri che sono range."""
        return self.valore_a(t, durata_totale)

class Nicchia:
    """
    Ipervolume N-dimensionale di Hutchinson per la sintesi sonora.
    Ogni dimensione è un NicchiaParametro (curva temporale con breakpoint).
    Dimensioni primarie (start + end indipendenti):
      Frequenziale : freq_min, freq_max        (start)
                     freq_end_min, freq_end_max (end — libertà controllata)
      Ampiezza     : amp_min, amp_max           (start)
                     amp_end_min, amp_end_max   (end — libertà controllata)
      Spaziale     : az_min, az_max, el_min, el_max          (start)
                     az_end_min, az_end_max, el_end_min, el_end_max (end)

    Dimensioni temporali:
      onset_min, onset_max, durata_min, durata_max, densita

    Dimensioni strutturali:
      n_sinusoidi, inviluppo micro (attack/decay/sustain/release)
    """

    MODALITA_SPAZIALI = ('S1', 'S2', 'S3', 'S4', 'S5', 'S6')

    def __init__(self,
                 # --- Temporale ---
                 onset_min        : NicchiaParametro = None,
                 onset_max        : NicchiaParametro = None,
                 durata_min       : NicchiaParametro = None,
                 durata_max       : NicchiaParametro = None,
                 densita          : NicchiaParametro = None,
                 # --- Frequenziale start ---
                 freq_min         : NicchiaParametro = None,
                 freq_max         : NicchiaParametro = None,
                 # --- Frequenziale end (indipendente, libertà) ---
                 freq_end_min     : NicchiaParametro = None,
                 freq_end_max     : NicchiaParametro = None,
                 # --- N. sinusoidi ---
                 n_sinusoidi      : NicchiaParametro = None,
                 # --- Ampiezza start ---
                 amp_min          : NicchiaParametro = None,
                 amp_max          : NicchiaParametro = None,
                 # --- Ampiezza end (indipendente, libertà) ---
                 amp_end_min      : NicchiaParametro = None,
                 amp_end_max      : NicchiaParametro = None,
                 # --- Inviluppo micro ---
                 attack_min       : NicchiaParametro = None,
                 attack_max       : NicchiaParametro = None,
                 decay_min        : NicchiaParametro = None,
                 decay_max        : NicchiaParametro = None,
                 sustain_min      : NicchiaParametro = None,
                 sustain_max      : NicchiaParametro = None,
                 release_min      : NicchiaParametro = None,
                 release_max      : NicchiaParametro = None,
                 # --- Spaziale start ---
                 modalita_spaziale: str              = 'S1',
                 az_min           : NicchiaParametro = None,
                 az_max           : NicchiaParametro = None,
                 el_min           : NicchiaParametro = None,
                 el_max           : NicchiaParametro = None,
                 # --- Spaziale end (indipendente, libertà) ---
                 az_end_min       : NicchiaParametro = None,
                 az_end_max       : NicchiaParametro = None,
                 el_end_min       : NicchiaParametro = None,
                 el_end_max       : NicchiaParametro = None,
                 # --- Separazione per dimensione ---
                 separazione_tempo    : float         = 0.8,
                 separazione_freq    : float         = 0.8,
                 separazione_amp     : float         = 0.5,
                 separazione_spazio  : float         = 0.5,
                 ):

        def _p(v0, v1):
            return NicchiaParametro(v0, v1)

        # Temporale
        self.onset_min   = onset_min   or _p(0.0,  0.0)
        self.onset_max   = onset_max   or _p(5.0,  5.0)
        self.durata_min  = durata_min  or _p(0.5,  0.5)
        self.durata_max  = durata_max  or _p(2.0,  2.0)
        self.densita     = densita     or _p(1.0,   1.0)

        # Frequenziale start
        self.freq_min    = freq_min    or _p(200.0, 200.0)
        self.freq_max    = freq_max    or _p(800.0, 800.0)

        # Frequenziale end — default = stessa cella dello start (libertà=0)
        self.freq_end_min = freq_end_min or self.freq_min
        self.freq_end_max = freq_end_max or self.freq_max

        # N. sinusoidi
        self.n_sinusoidi = n_sinusoidi or _p(3.0, 3.0)

        # Ampiezza start
        self.amp_min = amp_min or _p(0.1, 0.1)
        self.amp_max = amp_max or _p(0.5, 0.5)

        # Ampiezza end — default = stessa cella dello start
        self.amp_end_min = amp_end_min or self.amp_min
        self.amp_end_max = amp_end_max or self.amp_max

        # Inviluppo micro
        self.attack_min  = attack_min  or _p(0.01, 0.01)
        self.attack_max  = attack_max  or _p(0.1,  0.1)
        self.decay_min   = decay_min   or _p(0.05, 0.05)
        self.decay_max   = decay_max   or _p(0.2,  0.2)
        self.sustain_min = sustain_min or _p(0.5,  0.5)
        self.sustain_max = sustain_max or _p(0.8,  0.8)
        self.release_min = release_min or _p(0.1,  0.1)
        self.release_max = release_max or _p(0.5,  0.5)

        # Spaziale start
        assert modalita_spaziale in self.MODALITA_SPAZIALI
        self.modalita_spaziale = modalita_spaziale
        self.az_min = az_min or _p(0.0,        0.0)
        self.az_max = az_max or _p(2*np.pi,   2*np.pi)
        self.el_min = el_min or _p(-np.pi/4,  -np.pi/4)
        self.el_max = el_max or _p(np.pi/4,   np.pi/4)

        # Spaziale end — default = stessa cella dello start
        self.az_end_min = az_end_min or self.az_min
        self.az_end_max = az_end_max or self.az_max
        self.el_end_min = el_end_min or self.el_min
        self.el_end_max = el_end_max or self.el_max

        # Separazione per dimensione
        self.separazione_tempo  = float(np.clip(separazione_tempo,  0.0, 1.0))
        self.separazione_freq   = float(np.clip(separazione_freq,   0.0, 1.0))
        self.separazione_amp    = float(np.clip(separazione_amp,    0.0, 1.0))
        self.separazione_spazio = float(np.clip(separazione_spazio, 0.0, 1.0))

    def bounds_a(self, t, durata_totale):
        """
        Restituisce un dizionario con tutti i bounds al tempo t.
        """
        def v(p): return p.valore_a(t, durata_totale)
        return {
            'onset'        : (v(self.onset_min),      v(self.onset_max)),
            'durata'       : (v(self.durata_min),      v(self.durata_max)),
            'densita'      : v(self.densita),
            # Frequenza start
            'freq'         : (v(self.freq_min),       v(self.freq_max)),
            # Frequenza end — range indipendente, libertà controllata
            'freq_end'     : (v(self.freq_end_min),   v(self.freq_end_max)),
            'n_sin'        : max(1, round(v(self.n_sinusoidi))),
            # Ampiezza start
            'amp'          : (v(self.amp_min),        v(self.amp_max)),
            # Ampiezza end — range indipendente
            'amp_end'      : (v(self.amp_end_min),    v(self.amp_end_max)),
            'attack'       : (v(self.attack_min),     v(self.attack_max)),
            'decay'        : (v(self.decay_min),      v(self.decay_max)),
            'sustain'      : (v(self.sustain_min),    v(self.sustain_max)),
            'release'      : (v(self.release_min),    v(self.release_max)),
            # Spaziale start
            'az'           : (v(self.az_min),         v(self.az_max)),
            'el'           : (v(self.el_min),         v(self.el_max)),
            # Spaziale end — range indipendente
            'az_end'       : (v(self.az_end_min),     v(self.az_end_max)),
            'el_end'       : (v(self.el_end_min),     v(self.el_end_max)),
        }