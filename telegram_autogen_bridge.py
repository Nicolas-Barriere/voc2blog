from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram import Update, Bot
from dotenv import load_dotenv
import logging, os
from agents_session import BotSession
from openai import OpenAI


client = OpenAI()

# 🔧 Chargement de l'API Telegram et configuration
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
if TOKEN and not TOKEN.startswith("8111143826:"):
    TOKEN = "8111143826:" + TOKEN

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 📦 Config pour LLM local via Ollama
LLM_CONFIG = {
    "config_list": [
        {
            "model": "gpt-4.1-nano-2025-04-14",
            "api_key": OPENAI_API_KEY,
        }
    ],
}

# 🧠 Création de la session avec agents
session = BotSession(config=LLM_CONFIG)
session.register_reply_handler()


# 🤖 Handler principal pour les messages Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    logging.info(f"[Telegram] Message reçu : {user_msg}")

    # Stocke le contexte Telegram dans la session
    session.set_telegram_context(bot=context.bot, chat_id=update.effective_chat.id)

    # Lance la conversation avec le message de l'utilisateur
    session.handle_user_message(user_msg)


# 🚀 Lancement du bot Telegram
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("🤖 Prêt à discuter sur Telegram...")
    app.run_polling()
