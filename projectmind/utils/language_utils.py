# projectmind/utils/language_utils.py

from langdetect import detect
from deep_translator import GoogleTranslator

def translate_to_english(text: str) -> tuple[str, bool]:
    try:
        lang = detect(text)
    except Exception as e:
        return text, False  # fallback en caso de fallo de detección

    if lang == "en":
        return text, False  # No necesita traducción

    translated = GoogleTranslator(source='auto', target='en').translate(text)
    return translated, True
