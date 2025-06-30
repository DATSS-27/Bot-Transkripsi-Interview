import os
import logging
import tempfile
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from transcriber_vosk import transcribe_audio, transcribe_pdf

# Setup logging
def setup_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

# Token dan folder download
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or "YOUR_BOT_TOKEN"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Text saat /start
def start_text():
    return (
        "Halo Sayang❣️ Kirim file audio (voice/mp3/ogg) atau PDF transkrip wawancara.\n"
        "Aku akan ubah jadi teks yang rapi buat kamu ✨"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(start_text())

# Simpan file ke direktori sementara
async def save_file_to_temp(file_obj, ext):
    file = await file_obj.get_file()
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}", dir=DOWNLOAD_DIR)
    await file.download_to_drive(custom_path=tmp_file.name)
    return tmp_file.name

# Handle file kiriman user
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    file_obj, ext, method = None, None, None

    if msg.voice:
        file_obj, ext, method = msg.voice, 'ogg', 'audio'
    elif msg.audio:
        file_obj, ext, method = msg.audio, 'mp3', 'audio'
    elif msg.document:
        mime = msg.document.mime_type
        if mime == 'application/pdf':
            file_obj, ext, method = msg.document, 'pdf', 'pdf'
        elif mime in ['text/plain']:
            file_obj, ext, method = msg.document, 'txt', 'pdf'

    if not file_obj:
        await msg.reply_text("Sayang, file kamu nggak bisa aku baca 😢. Kirim audio (mp3/ogg/voice) atau PDF/text yaa.")
        return

    if file_obj.file_size > 10 * 1024 * 1024:
        await msg.reply_text("File-nya kegedean, Sayang 😵. Maksimal 10MB ya.")
        return

    await msg.reply_text("Tunggu bentar yaaa, aku kerjain dulu... 💪")

    try:
        file_path = await save_file_to_temp(file_obj, ext)

        if method == 'audio':
            transcript = transcribe_audio(file_path)
        else:
            transcript = transcribe_pdf(file_path)

        transcript_path = file_path.replace(f".{ext}", "_transcript.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

        await msg.reply_document(document=InputFile(transcript_path), caption="Transkripsi udah jadi Sayang ❣️")

    except Exception as e:
        logging.exception("Error saat transkripsi")
        await msg.reply_text("Maaf Sayang, gagal transkripsi 😭. Coba lagi nanti yaa.")
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            if 'transcript_path' in locals() and os.path.exists(transcript_path):
                os.remove(transcript_path)
        except Exception:
            pass

# Entry utama
if __name__ == '__main__':
    setup_logging()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO | filters.Document.ALL, handle_file))

    logging.info("Transcription bot is running...")
    app.run_polling()
