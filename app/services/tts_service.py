import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
TTS_URL = "https://api.sarvam.ai/text-to-speech"
AUDIO_DIR = "outputs/audio"

os.makedirs(AUDIO_DIR, exist_ok=True)

# Language code to Sarvam TTS speaker mapping
LANG_SPEAKER = {
    "hi": "meera",
    "bn": "amartya",
    "gu": "meera",
    "kn": "meera",
    "ml": "meera",
    "mr": "meera",
    "od": "meera",
    "pa": "meera",
    "ta": "meera",
    "te": "meera",
    "en": "meera",
}


def generate_audio(text: str, lang: str, filename_base: str) -> str | None:
    """Generate TTS audio for the given text and language.
    Returns the audio file path or None on failure."""
    # Sarvam TTS supports up to 500 chars per request — use first 500 chars as preview
    preview_text = text[:500].strip()
    if not preview_text:
        return None

    speaker = LANG_SPEAKER.get(lang, "meera")
    lang_code = f"{lang}-IN" if lang != "en" else "en-IN"

    try:
        payload = {
            "inputs": [preview_text],
            "target_language_code": lang_code,
            "speaker": speaker,
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.5,
            "speech_sample_rate": 8000,
            "enable_preprocessing": True,
            "model": "bulbul:v1"
        }
        headers = {
            "api-subscription-key": SARVAM_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(TTS_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        audio_b64 = data.get("audios", [None])[0]
        if not audio_b64:
            return None

        audio_bytes = base64.b64decode(audio_b64)
        audio_filename = f"{filename_base}_{lang}.wav"
        audio_path = os.path.join(AUDIO_DIR, audio_filename)
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)

        return audio_path

    except Exception:
        return None
