import warnings
import os
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Suprime warnings do HuggingFace Hub e symlinks no Windows
os.environ.setdefault('HF_HUB_DISABLE_IMPLICIT_TOKEN', '1')
os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING', '1')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')

from main import app
from flask import request, send_file, jsonify
from kokoro import KPipeline
import soundfile as sf
import numpy as np
import io

VOICES = {
    'a': {
        'af_heart': 'Heart (F)', 'af_bella': 'Bella (F)', 'af_nicole': 'Nicole (F)',
        'af_aoede': 'Aoede (F)', 'af_kore': 'Kore (F)', 'af_sarah': 'Sarah (F)',
        'af_sky': 'Sky (F)', 'am_adam': 'Adam (M)', 'am_echo': 'Echo (M)',
        'am_eric': 'Eric (M)', 'am_fenrir': 'Fenrir (M)', 'am_liam': 'Liam (M)',
        'am_michael': 'Michael (M)', 'am_onyx': 'Onyx (M)', 'am_puck': 'Puck (M)',
    },
    'b': {
        'bf_emma': 'Emma (F)', 'bf_isabella': 'Isabella (F)',
        'bm_george': 'George (M)', 'bm_lewis': 'Lewis (M)',
    },
    'p': {
        'pf_dora': 'Dora (F)', 'pm_alex': 'Alex (M)', 'pm_santa': 'Santa (M)',
    },
    'e': {
        'ef_dora': 'Dora (F)', 'em_alex': 'Alex (M)', 'em_santa': 'Santa (M)',
    },
    'f': {
        'ff_siwis': 'Siwis (F)',
    },
    'i': {
        'if_sara': 'Sara (F)', 'im_nicola': 'Nicola (M)',
    },
    'h': {
        'hf_alpha': 'Alpha (F)', 'hf_beta': 'Beta (F)',
        'hm_omega': 'Omega (M)', 'hm_psi': 'Psi (M)',
    },
}

LANG_NAMES = {
    'a': 'American English',
    'b': 'British English',
    'p': 'Brazilian Portuguese',
    'e': 'Spanish',
    'f': 'French',
    'i': 'Italian',
    'h': 'Hindi',
}

_pipelines: dict[str, KPipeline] = {}

def get_pipeline(lang_code: str) -> KPipeline:
    if lang_code not in _pipelines:
        try:
            _pipelines[lang_code] = KPipeline(lang_code=lang_code, repo_id='hexgrad/Kokoro-82M')
        except Exception as e:
            raise RuntimeError(
                f'Falha ao carregar pipeline para lang="{lang_code}": {e}. '
                'Tente: uv add misaki'
            ) from e
    return _pipelines[lang_code]


@app.route('/')
def index():
    html_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()


@app.route('/api/voices', methods=['GET'])
def get_voices():
    return jsonify({
        'voices': VOICES,
        'languages': LANG_NAMES,
    })


@app.route('/api/tts', methods=['POST'])
def tts():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body is required'}), 400

    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'text is required and cannot be empty'}), 400

    lang = data.get('lang', 'a')
    if lang not in VOICES:
        return jsonify({'error': f'unsupported lang "{lang}". Available: {list(VOICES.keys())}'}), 400

    default_voice = next(iter(VOICES[lang]))
    voice = data.get('voice', default_voice)
    if voice not in VOICES[lang]:
        return jsonify({'error': f'voice "{voice}" not available for lang "{lang}"'}), 400

    try:
        speed = float(data.get('speed', 1.0))
        speed = max(0.5, min(2.0, speed))
    except (TypeError, ValueError):
        return jsonify({'error': 'speed must be a number between 0.5 and 2.0'}), 400

    try:
        pipeline = get_pipeline(lang)
        chunks = []
        for _, _, audio in pipeline(text, voice=voice, speed=speed):
            chunks.append(audio)

        if not chunks:
            return jsonify({'error': 'no audio generated'}), 500

        full_audio = np.concatenate(chunks)
        buffer = io.BytesIO()
        sf.write(buffer, full_audio, 24000, format='WAV')
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='audio/wav',
            as_attachment=False,
            download_name='speech.wav',
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
