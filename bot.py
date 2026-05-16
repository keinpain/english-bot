import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY", "не задан")
YANDEX_FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID", "не задан")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я тестовый эхо-бот.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    debug = f"folder_id={YANDEX_FOLDER_ID}\napi_key={YANDEX_API_KEY[:10]}..."
    reply = f"Эхо: {user_text}\n\n{debug}"
    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=os.environ.get("RENDER_EXTERNAL_URL", "") + "/webhook",
        url_path="webhook",
    )

if __name__ == "__main__":
    main()
