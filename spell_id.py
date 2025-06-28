import os
from spellchecker import SpellChecker

# Path file kamus relatif terhadap file ini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_PATH = os.path.join(BASE_DIR, "id_words.txt")

spell = SpellChecker(language=None)

if not os.path.exists(DICT_PATH):
    print(f"⚠️ Kamus Bahasa Indonesia tidak ditemukan: {DICT_PATH}")
else:
    spell.word_frequency.load_text_file(DICT_PATH)

def correct_indonesian(text: str) -> str:
    words = text.split()
    return " ".join(spell.correction(w) or w for w in words)
