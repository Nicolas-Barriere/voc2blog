from telegram.ext import ApplicationBuilder, MessageHandler, filters  # type: ignore
from telegram import Update  # type: ignore
from telegram.ext import ContextTypes  # type: ignore
import os
from dotenv import load_dotenv  # type: ignore
import logging
import subprocess
from generate_post import generate_post


load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

# Cas où seule la deuxième moitié du token est lue
if TOKEN and not TOKEN.startswith("8111143826:"):
    TOKEN = "8111143826:" + TOKEN

logging.basicConfig(level=logging.INFO)

DOWNLOAD_DIR = "downloads"
CONVERTED_DIR = "converted"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(CONVERTED_DIR, exist_ok=True)


def transcrire_wav(wav_path, model_path="./whisper.cpp/models/ggml-base.bin"):
    command = [
        "./whisper.cpp/build/bin/whisper-cli",
        "-m",
        model_path,
        "-f",
        wav_path,
        "--language",
        "fr",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    # 🔍 Affiche le stderr si stdout est vide
    return result.stdout


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    logging.info(f"🎙️ Nouveau vocal de {user}")

    file = await context.bot.get_file(update.message.voice.file_id)
    ogg_path = os.path.join(DOWNLOAD_DIR, f"{update.message.message_id}.ogg")
    await file.download_to_drive(ogg_path)

    wav_path = os.path.join(CONVERTED_DIR, f"{update.message.message_id}.wav")
    command = [
        "ffmpeg",
        "-i",
        ogg_path,
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        wav_path,
    ]

    subprocess.run(command, check=True)
    logging.info(f"✅ Converti en {wav_path}")

    await update.message.reply_text("🧠 Audio reçu et prêt pour transcription !")

    transcription = transcrire_wav(wav_path)
    markdown = generate_post(transcription)
    print("📝 Article généré :")
    print(markdown)

    # Optionnel : sauvegarde dans un fichier .md
    with open("articles/generated.md", "w") as f:
        f.write(markdown)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    logging.info("🤖 Bot prêt, en attente de vocaux...")
    app.run_polling()
