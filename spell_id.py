from spellchecker import SpellChecker

# Inisialisasi spell checker tanpa bahasa bawaan
spell = SpellChecker(language=None)

# Muat daftar kata Bahasa Indonesia dari file
DICT_PATH = "id_words.txt"

if not spell.word_frequency.load_text_file(DICT_PATH):
    print("⚠️ Kamus Bahasa Indonesia tidak ditemukan:", DICT_PATH)

def correct_indonesian(text: str) -> str:
    words = text.split()
    corrected_words = []
    for word in words:
        corrected = spell.correction(word)
        corrected_words.append(corrected if corrected else word)
    return " ".join(corrected_words)