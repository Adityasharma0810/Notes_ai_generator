import os
import requests
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
TRANSLATE_URL = "https://api.sarvam.ai/translate"

# Sarvam supported language codes
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "od": "Odia",
    "pa": "Punjabi",
    "ta": "Tamil",
    "te": "Telugu",
}


def translate_text(text: str, target_lang: str) -> str:
    """Translate text to target language using Sarvam API.
    If target is English or translation fails, return original text."""
    if target_lang == "en" or not text.strip():
        return text

    # Sarvam translate has a ~1000 char limit per request — chunk it
    MAX_CHARS = 900
    chunks = []
    current = ""
    for sentence in text.replace("\n", " \n ").split("\n"):
        if len(current) + len(sentence) < MAX_CHARS:
            current += sentence + "\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence + "\n"
    if current.strip():
        chunks.append(current.strip())

    translated_chunks = []
    for chunk in chunks:
        try:
            payload = {
                "input": chunk,
                "source_language_code": "en-IN",
                "target_language_code": f"{target_lang}-IN",
                "speaker_gender": "Male",
                "mode": "formal",
                "model": "mayura:v1",
                "enable_preprocessing": False
            }
            headers = {
                "api-subscription-key": SARVAM_API_KEY,
                "Content-Type": "application/json"
            }
            response = requests.post(TRANSLATE_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            translated_chunks.append(response.json().get("translated_text", chunk))
        except Exception:
            # On failure, keep original chunk
            translated_chunks.append(chunk)

    return "\n".join(translated_chunks)
