import os
from spellchecker import SpellChecker

# Path file kamus relatif terhadap file ini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_PATH = os.path.join(BASE_DIR, "id_words.txt")

# Inisialisasi spell checker
spell = SpellChecker(language=None)

# Load kamus jika tersedia
if not os.path.exists(DICT_PATH):
    raise FileNotFoundError(f"❌ Kamus Bahasa Indonesia tidak ditemukan: {DICT_PATH}")
spell.word_frequency.load_text_file(DICT_PATH)

def correct_indonesian(text: str) -> str:
    """
    Koreksi ejaan Bahasa Indonesia menggunakan kamus lokal.
    Hanya mengoreksi kata yang tidak dikenal oleh kamus.
    """
    corrected_words = []
    for word in text.split():
        if word in spell:
            corrected_words.append(word)
        else:
            suggestion = spell.correction(word)
            # Jika tidak ada saran atau saran sama dengan kata awal, gunakan kata asli
            corrected_words.append(suggestion if suggestion else word)
    return " ".join(corrected_words)
