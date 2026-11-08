#!/usr/bin/env python3
"""
run.py — lancia Hutchinson Synthesis con il file di config che scegli.

COME SI USA
  1. Nella lista SCEGLI qui sotto togli il '#' davanti a UNA sola riga.
  2. Lancia:   python run.py

COSA FA
  Carica il file scelto (cartella configs/) al posto di config.py e poi avvia
  main_v1_independent.py, come se lo avessi lanciato tu.
  Non modifica nessun altro file. L'output resta dove è sempre stato
  (output/hutchinson_v1.wav, output/hutchinson_v1.csd, ...) e ogni lancio
  sovrascrive il precedente.

  config.py resta quello usato se lanci direttamente main_v1_independent.py.
  I file in configs/ sono copie: se cambi config.py, 00_config_prova.py non cambia.
"""
import importlib.util
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
CARTELLA_CONFIG = os.path.join(QUI, "configs")

# ----------------------------------------------------------------------
#  SCEGLI IL CONFIG: togli il '#' davanti a UNA sola riga.
# ----------------------------------------------------------------------
SCEGLI = [
    # "00_config_prova",
    # "01_matern_3niches_sparse",
    # "02_matern_10niches_rings_low",
    # "03_matern_10niches_rings_dense",
    # "04_matern_10niches_ren_medium",
    # "05_matern_10niches_ren_fullrange",
    # "06_matern_2niches_longdur_bass",
    # "07_dpp_3niches",
]
# ----------------------------------------------------------------------


def prepara():
    """Controlla la scelta e carica il config al posto di 'config'.
    Restituisce (nome, percorso). Non avvia il programma."""
    if not SCEGLI:
        sys.exit("Nessun config scelto: in run.py togli il '#' davanti a UNA riga della lista SCEGLI.")
    if len(SCEGLI) > 1:
        sys.exit("Hai scelto %d config (%s): ne serve UNO solo. In run.py rimetti il '#' alle altre."
                 % (len(SCEGLI), ", ".join(SCEGLI)))
    nome = SCEGLI[0]
    if nome.endswith(".py"):
        nome = nome[:-3]
    percorso = os.path.join(CARTELLA_CONFIG, nome + ".py")
    if not os.path.isfile(percorso):
        sys.exit("File di config non trovato: " + percorso)

    # il programma importa gigp, renderer, visualizer... da questa cartella
    if QUI not in sys.path:
        sys.path.insert(0, QUI)

    # il file scelto prende il posto di config.py:
    # main_v1_independent.py fa 'from config import *' e trova questo.
    spec = importlib.util.spec_from_file_location("config", percorso)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules["config"] = modulo
    spec.loader.exec_module(modulo)
    return nome, percorso


def lancia():
    nome, percorso = prepara()
    print("=" * 60)
    print("  Config scelto: %s" % nome)
    print("  File:          %s" % percorso)
    print("=" * 60)
    import main_v1_independent
    main_v1_independent.main()


if __name__ == "__main__":
    lancia()
