"""
score_generator.py — Hutchinson Synthesis
Genera l'orchestra CSound (.orc) e lo score (.sco) e li combina in un .csd.
HOA SN3D/ACN — ordini 1-7 selezionabili via HOA_ORDER nel config.

Mappa p-field (24 parametri):
  p1  = numero strumento
  p2  = onset
  p3  = durata
  p4  = freq_start        p5  = freq_end        p6  = iTypeGliss
  p7  = ampiezza          p8  = iPerc           p9  = iTypeEnv
  p10 = ifreqMOD          p11 = ifreqAMP
  p12 = ifreqMOD1         p13 = ifreqMOD2       p14 = iTypeFreqMOD
  p15 = ifreqAMP1         p16 = ifreqAMP2       p17 = iTypeFreqAMP
  p18 = azimuth start     p19 = elevation start
  p20 = azimuth end       p21 = elevation end
  p22 = iTypeMoveAmb      p23 = iTypeProxAmb    p24 = iAmpProx
"""

import os
import math
import numpy as np

def get_n_channels(order):
    return (order + 1) ** 2

def build_orchestra(order=1, udos_path="hoa_udos.udo"):
    """Costruisce l'orchestra CSound per l'ordine HOA specificato."""
    n_ch = get_n_channels(order)
    # Lista uscite UDO: aACN00, aACN01, ..., aACN{n_ch-1}
    out_vars = ", ".join(f"aACN{i:02d}" for i in range(n_ch))
    outc_vars = ", ".join(f"aACN{i:02d}" for i in range(n_ch))

    orchestra = f"""; ============================================================
; Hutchinson Synthesis — CSound Orchestra
; HOA order {order} — AmbiX SN3D/ACN — {n_ch} canali
; ============================================================

sr     = 48000
ksmps  = 64
nchnls = {n_ch}
0dbfs  = 1.0
seed 0

#include "hoa_udos.udo"

; p4  = freq_start         p5  = freq_end          p6  = iTypeGliss
; p7  = ampiezza           p8  = iPerc             p9  = iTypeEnv
; p10 = ifreqMOD           p11 = ifreqAMP
; p12 = ifreqMOD1          p13 = ifreqMOD2         p14 = iTypeFreqMOD
; p15 = ifreqAMP1          p16 = ifreqAMP2         p17 = iTypeFreqAMP
; p18 = azimuth start      p19 = elevation start
; p20 = azimuth end        p21 = elevation end
; p22 = iTypeMoveAmb       p23 = iTypeProxAmb      p24 = iAmpProx

instr 1
  ifreq1       = p4
  ifreq2       = p5
  iTypeGliss   = p6
  iamp         = p7
  iPerc        = p8
  iTypeEnv     = p9
  ifreqMOD     = p10
  ifreqAMP     = p11
  ifreqMOD1    = p12
  ifreqMOD2    = p13
  iTypeFreqMOD = p14
  ifreqAMP1    = p15
  ifreqAMP2    = p16
  iTypeFreqAMP = p17
  iazIN        = p18
  ielIN        = p19
  iazOUT       = p20
  ielOUT       = p21
  iTypeMoveAmb = p22
  iTypeProxAmb = p23
  iAmpProx     = p24

  iDurAtt = (p3 * iPerc < 0.0005 ? 0.0005 : p3 * iPerc)
  iDurRel = (p3 * (1 - iPerc) < 0.0005 ? 0.0005 : p3 * (1 - iPerc))

  aenv    transeg  0, iDurAtt, iTypeEnv, iamp, iDurRel, -iTypeEnv, 0
  afreq   transeg  ifreq1, p3, iTypeGliss, ifreq2

  krandMOD_freq randomh -ifreqMOD1, ifreqMOD2, 5
  krandAMP_freq randomh -ifreqMOD1, ifreqMOD2, 5
  krandMOD_amp  randomh -ifreqAMP1, ifreqAMP2, 5
  krandAMP_amp  randomh -ifreqAMP1, ifreqAMP2, 5
  arandMOD oscili krandMOD_amp, krandMOD_freq
  arandAMP oscili krandAMP_amp, krandAMP_freq

  aMod    oscili  ifreqAMP + arandAMP, ifreqMOD + arandMOD
  asig    oscili  aenv, afreq + aMod

  aAzi  transeg  iazIN,  p3, iTypeMoveAmb, iazOUT
  aEle  transeg  ielIN,  p3, iTypeMoveAmb, ielOUT
  aProx transeg  1, p3/2, iTypeProxAmb, iAmpProx, p3/2, -iTypeProxAmb, 1

  ; HOA encoding ordine {order} — {n_ch} canali SN3D/ACN
  {out_vars} hoa_encode_{order} asig*aProx, aAzi, aEle

  outc   {outc_vars}
endin

"""
    return orchestra

def genera_score(lista_eventi, durata_totale):
    righe = ["; Hutchinson Synthesis — Score CSound", ""]
    eventi = sorted(lista_eventi, key=lambda e: e['onset'])

    for ev in eventi:
        onset         = ev['onset']
        durata        = ev['durata']
        freq_start    = ev['freq_start']
        freq_end      = ev['freq_end']
        freq_min_nich = ev.get('freq_min', min(freq_start, freq_end))
        freq_max_nich = ev.get('freq_max', max(freq_start, freq_end))
        amp           = ev['amp'] * float(ev.get('amp_gain', 1.0))
        az            = ev['az']
        el            = ev['el']
        perc          = max(0.01, min(0.99, ev.get('perc', 0.5)))
        n_sin         = ev.get('n_sinusoidi', 1)

        type_gliss    = float(np.clip(ev.get('type_gliss',    1.0), 0.1, 10.0))
        az_end        = float(ev.get('az_end', az))
        el_end        = float(ev.get('el_end', el))
        type_mov_amb  = float(np.clip(ev.get('type_mov_amb',  1.0), 0.1, 10.0))
        type_prox_amb = float(np.clip(ev.get('type_prox_amb', 1.0), 0.1, 10.0))
        prox_amp      = float(np.clip(ev.get('prox_amp', 1.0), 0.0, 1.0))
        type_env      = float(np.clip(ev.get('type_env',      1.0), 0.1, 10.0))
        freq_mod      = float(ev.get('freq_mod',  1.0))
        freq_amp      = float(ev.get('freq_amp',  0.0))
        freq_mod1     = float(np.clip(ev.get('freq_mod1', 1.0), 0.01, 100.0))
        freq_mod2     = float(np.clip(ev.get('freq_mod2', 1.0), 0.01, 100.0))
        type_freq_mod = float(np.clip(ev.get('type_freq_mod', 1.0), 0.1, 10.0))
        freq_amp1     = float(np.clip(ev.get('freq_amp1', 1.0), 0.01, 100.0))
        freq_amp2     = float(np.clip(ev.get('freq_amp2', 1.0), 0.01, 100.0))
        type_freq_amp = float(np.clip(ev.get('type_freq_amp', 1.0), 0.1, 10.0))

        for k in range(n_sin):
            if n_sin == 1:
                f_s = freq_start
                f_e = freq_end
            else:
                ratio = k / max(n_sin - 1, 1)
                f_s = freq_start + ratio * (freq_end - freq_start) * 0.5
                gliss = freq_end - freq_start
                # ✅ Rimuovo il clamp alle bound di nicchia che distruggeva il glissando cross-niche
                f_s = float(f_s)
                f_e = float(f_s + gliss)

            amp_k = amp / math.sqrt(n_sin)
            riga = (
                f"i 1  {onset:.4f}  {durata:.4f}  "
                f"{f_s:.4f}  {f_e:.4f}  {type_gliss:.4f}  "
                f"{amp_k:.6f}  {perc:.4f}  {type_env:.4f}  "
                f"{freq_mod:.4f}  {freq_amp:.4f}  "
                f"{freq_mod1:.4f}  {freq_mod2:.4f}  {type_freq_mod:.4f}  "
                f"{freq_amp1:.4f}  {freq_amp2:.4f}  {type_freq_amp:.4f}  "
                f"{az:.4f}  {el:.4f}  "
                f"{az_end:.4f}  {el_end:.4f}  "
                f"{type_mov_amb:.4f}  {type_prox_amb:.4f}  {prox_amp:.4f}"
            )
            righe.append(riga)

    righe.append("")
    righe.append(f"i 99  0  {durata_totale:.2f}")
    righe.append(f"f 0 {durata_totale:.2f}")
    righe.append(f"e {durata_totale:.2f}")
    return "\n".join(righe)

def genera_csd(lista_eventi, durata_totale, output_wav, csd_path,
               hoa_order=1, udos_path="hoa_udos.udo"):
    orchestra = build_orchestra(order=hoa_order, udos_path=udos_path)
    score = genera_score(lista_eventi, durata_totale)
    csd = f"""<CsoundSynthesizer>
<CsOptions>
-o "{output_wav}" --format=wav -3 -d
</CsOptions>
<CsInstruments>
{orchestra}
</CsInstruments>
<CsScore>
{score}
</CsScore>
</CsoundSynthesizer>
"""
    with open(csd_path, 'w') as f:
        f.write(csd)

    n_ch = get_n_channels(hoa_order)
    print(f"[ScoreGenerator] CSD scritto: {csd_path}")
    print(f"[ScoreGenerator] HOA order {hoa_order} — {n_ch} canali SN3D/ACN")
    print(f"[ScoreGenerator] Output WAV : {output_wav}")
    print(f"[ScoreGenerator] Eventi totali: {len(lista_eventi)}")