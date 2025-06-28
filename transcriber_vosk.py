import os
import json
import wave
import fitz
import tempfile
import subprocess
from vosk import Model, KaldiRecognizer
from spell_id import correct_indonesian

model = Model(lang="id")  # Pastikan model Bahasa Indonesia sudah diekstrak

def convert_to_wav(input_path):
    output_path = tempfile.mktemp(suffix=".wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1", "-f", "wav", output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def transcribe_audio(path: str) -> str:
    wav_path = convert_to_wav(path)
    wf = wave.open(wav_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            part = json.loads(rec.Result())
            if part.get("text"):
                results.append(part["text"])

    final = json.loads(rec.FinalResult()).get("text", "")
    results.append(final)

    raw_text = " ".join(results)
    corrected = correct_indonesian(raw_text)
    return corrected.strip()

def transcribe_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()
