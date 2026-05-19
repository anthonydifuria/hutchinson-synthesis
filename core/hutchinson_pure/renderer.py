"""
renderer.py — Hutchinson Synthesis
Chiama CSound per renderizzare il .csd e riproduce l'audio.
"""

import subprocess
import sys
import os


def renderizza(csd_path, output_wav):
    """
    Chiama CSound per renderizzare il file .csd.
    Restituisce True se successo.
    """
    print(f"\n[Renderer] Avvio CSound...")
    print(f"[Renderer] Input : {csd_path}")
    print(f"[Renderer] Output: {output_wav}")

    # Cerca csound nel sistema
    csound_cmd = _trova_csound()
    if csound_cmd is None:
        print("[Renderer] ERRORE: CSound non trovato nel sistema.")
        print("[Renderer] Installa CSound: https://csound.com/download.html")
        return False

    cmd = [csound_cmd, csd_path]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print(f"[Renderer] Renderizzazione completata.")
            if os.path.exists(output_wav):
                size_mb = os.path.getsize(output_wav) / (1024 * 1024)
                print(f"[Renderer] File audio: {output_wav} ({size_mb:.2f} MB)")
            return True
        else:
            print(f"[Renderer] ERRORE CSound (returncode={result.returncode})")
            print(result.stderr[-2000:] if result.stderr else "")
            return False
    except subprocess.TimeoutExpired:
        print("[Renderer] TIMEOUT — CSound ha impiegato troppo tempo.")
        return False
    except Exception as e:
        print(f"[Renderer] Errore: {e}")
        return False


def riproduci(output_wav):
    """
    Riproduce il file WAV con il player di sistema.
    """
    if not os.path.exists(output_wav):
        print(f"[Renderer] File not found: {output_wav}")
        return

    print(f"\n[Renderer] Riproduzione: {output_wav}")

    if sys.platform == 'darwin':
        subprocess.Popen(['afplay', output_wav])
    elif sys.platform.startswith('linux'):
        # Prova aplay, poi paplay, poi ffplay
        for player in ['aplay', 'paplay', 'ffplay', 'mpv']:
            if subprocess.run(['which', player],
                              capture_output=True).returncode == 0:
                subprocess.Popen([player, output_wav])
                break
        else:
            print("[Renderer] Nessun player trovato. "
                  f"Riproduci manualmente: {output_wav}")
    elif sys.platform == 'win32':
        os.startfile(output_wav)
    else:
        print(f"[Renderer] Piattaforma non supportata. "
              f"Riproduci manualmente: {output_wav}")


def _trova_csound():
    """Cerca l'eseguibile csound nel sistema."""
    candidati = ['csound', 'csound6', 'csound64']
    for c in candidati:
        r = subprocess.run(['which', c], capture_output=True, text=True)
        if r.returncode == 0:
            return c
    return None
