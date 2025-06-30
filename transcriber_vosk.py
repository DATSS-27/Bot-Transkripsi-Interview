import os
import json
import wave
import fitz  # PyMuPDF
import tempfile
import subprocess
from vosk import Model, KaldiRecognizer
from spell_id import correct_indonesian


# Load Vosk model untuk Bahasa Indonesia
model = Model(lang="id")


def convert_to_wav(input_path: str) -> str:
    """
    Konversi file audio apa pun ke WAV mono 16kHz.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File tidak ditemukan: {input_path}")

    output_path = tempfile.mktemp(suffix=".wav")
    result = subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1", "-f", "wav", output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if result.returncode != 0 or not os.path.exists(output_path):
        raise RuntimeError("Gagal mengonversi audio ke WAV.")

    return output_path


def transcribe_audio(path: str) -> str:
    """
    Transkripsi audio Bahasa Indonesia menjadi teks, lalu koreksi ejaannya.
    """
    wav_path = convert_to_wav(path)

    try:
        with wave.open(wav_path, "rb") as wf:
            if wf.getnchannels() != 1 or wf.getframerate() != 16000:
                raise ValueError("Audio harus mono 16kHz.")

            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)

            results = []
            while True:
                data = wf.readframes(4000)
                if not data:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if result.get("text"):
                        results.append(result["text"])

            final_result = json.loads(rec.FinalResult()).get("text", "")
            if final_result:
                results.append(final_result)

        raw_text = " ".join(results)
        corrected_text = correct_indonesian(raw_text)
        return corrected_text.strip()

    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


def transcribe_pdf(pdf_path: str) -> str:
    """
    Ekstraksi teks dari PDF menggunakan PyMuPDF (fitz).
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF tidak ditemukan: {pdf_path}")

    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    return text.strip()
