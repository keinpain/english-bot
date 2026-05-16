import os
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === КЛЮЧИ ===
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
YANDEX_API_KEY = os.environ["YANDEX_API_KEY"]
YANDEX_FOLDER_ID = os.environ["YANDEX_FOLDER_ID"]

SYSTEM_PROMPT = (
    "Ты — дружелюбный AI-репетитор английского языка. "
    "Отвечай на английском, но если нужно объяснить правило, переходи на русский. "
    "Аккуратно исправляй ошибки пользователя, давай краткие пояснения."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я твой репетитор английского. Пиши мне на английском — "
        "я исправлю ошибки и объясню."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        async with httpx.AsyncClient() as client:
            folder_id = os.environ.get("YANDEX_FOLDER_ID", "")
            # Отладочная информация: покажем, что лежит в переменной
            if not folder_id:
                reply = "Ошибка: переменная YANDEX_FOLDER_ID пуста"
                await update.message.reply_text(reply)
                return
            # Сформируем modelUri и тоже покажем
            model_uri = f"gpt://{folder_id}/yandexgpt/lite"
            debug_info = f"folder_id={folder_id}, model_uri={model_uri}"

            response = await client.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                headers={
                    "Authorization": f"Api-Key {YANDEX_API_KEY}",
                    "x-folder-id": folder_id,
                    "Content-Type": "application/json"
                },
                json={
                    "modelUri": model_uri,
                    "completionOptions": {
                        "stream": False,
                        "temperature": 0.7,
                        "maxTokens": 500
                    },
                    "messages": [
                        {"role": "system", "text": SYSTEM_PROMPT},
                        {"role": "user", "text": user_message}
                    ]
                }
            )
            result = response.json()
            if "result" not in result:
                reply = f"{debug_info}\nОтвет Яндекса: {result}"
            else:
                reply = result["result"]["alternatives"][0]["message"]["text"]
    except Exception as e:
        reply = f"Ошибка: {e}"

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
