"""
Baixa todos os arquivos de voz do Kokoro para o cache local.
Execute uma vez: uv run python download_voices.py
"""
import os
import sys

# Força UTF-8 no terminal Windows e suprime warning de symlinks
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from huggingface_hub import hf_hub_download

REPO_ID = 'hexgrad/Kokoro-82M'

ALL_VOICES = [
    # American English
    'af_heart', 'af_bella', 'af_nicole', 'af_aoede', 'af_kore',
    'af_sarah', 'af_sky', 'am_adam', 'am_echo', 'am_eric',
    'am_fenrir', 'am_liam', 'am_michael', 'am_onyx', 'am_puck',
    # British English
    'bf_emma', 'bf_isabella', 'bm_george', 'bm_lewis',
    # Brazilian Portuguese
    'pf_dora', 'pm_alex', 'pm_santa',
    # Spanish
    'ef_dora', 'em_alex', 'em_santa',
    # French
    'ff_siwis',
    # Italian
    'if_sara', 'im_nicola',
    # Hindi
    'hf_alpha', 'hf_beta', 'hm_omega', 'hm_psi',
]

def download_all():
    total = len(ALL_VOICES)
    ok = 0
    fail = 0

    print(f"Baixando {total} vozes de {REPO_ID}...\n")

    for voice in ALL_VOICES:
        filename = f'voices/{voice}.pt'
        try:
            path = hf_hub_download(repo_id=REPO_ID, filename=filename)
            print(f"  [OK]   {voice}")
            ok += 1
        except Exception as e:
            print(f"  [ERRO] {voice}: {e}")
            fail += 1

    print(f"\nConcluido: {ok} vozes baixadas, {fail} falhas.")
    if ok > 0:
        print("As vozes estao salvas no cache local e serao usadas offline.")

if __name__ == '__main__':
    download_all()
