import os
import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from transcriber_vosk import transcribe_audio, transcribe_pdf  # Menggunakan Vosk (gratis) untuk transkripsi

# Setup logging
def setup_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

# Bot token and directories
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or "YOUR_BOT_TOKEN"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# /start command text
def start_text():
    return (
        "Halo Sayang❣️❣️❣️, Kirim file audio atau PDF transkrip wawancara. "
        "Saya akan mengubahnya menjadi teks transkripsi yang akurat dan jelas untuk analisis lanjutan."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(start_text())

# Save incoming file
def save_file(file_obj, ext):
    filepath = os.path.join(DOWNLOAD_DIR, f"{file_obj.file_id}.{ext}")
    return file_obj.get_file().download_to_drive(filepath)

# Handle file messages
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    # Identify file type
    if msg.voice:
        file_obj, ext, method = msg.voice, 'ogg', 'audio'
    elif msg.audio:
        file_obj, ext, method = msg.audio, 'mp3', 'audio'
    elif msg.document and msg.document.mime_type in ['application/pdf', 'text/plain']:
        file_obj = msg.document
        ext = 'pdf' if msg.document.mime_type == 'application/pdf' else 'txt'
        method = 'pdf'
    else:
        await msg.reply_text("Format tidak didukung. Mohon kirim audio (voice/mp3/ogg) atau PDF/text.")
        return

    # Batasi ukuran file (mis. 10MB)
    if file_obj.file_size > 10 * 1024 * 1024:
        await msg.reply_text("Ukuran file terlalu besar. Maksimum 10MB.")
        return

    await msg.reply_text("Tunggu neh Yaaa...")
    filepath = await save_file(file_obj, ext)

    try:
        if method == 'audio':
            transcript = transcribe_audio(filepath)
        else:
            transcript = transcribe_pdf(filepath)
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        await msg.reply_text("Gagal transkripsi. Coba lagi nanti.")
        os.remove(filepath)
        return

    # Kirim hasil transkripsi
    text_path = os.path.join(DOWNLOAD_DIR, f"transcript_{file_obj.file_id}.txt")
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(transcript)

    await msg.reply_text("Ini Sayanggg")
    await msg.reply_document(document=InputFile(text_path), caption="Transkripsi wawancara.")

    # Hapus file sementara agar tidak penuhi storage
    os.remove(filepath)
    os.remove(text_path)

# Main entry
if __name__ == '__main__':
    setup_logging()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    file_filter = filters.VOICE | filters.AUDIO | filters.Document.FILE
    app.add_handler(MessageHandler(file_filter, handle_file))

    logging.info("Transcription bot running...")
    app.run_polling()
