import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import AsyncOpenAI

# === КЛЮЧИ (Render возьмёт из переменных окружения или из кода) ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8686785559:AAF0XL23x1MoS7fKKWZYj_IpJ1Xhes2MPAQ")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-8dc1daec370247958b1dc2e34671fb33ы")

SYSTEM_PROMPT = (
    "Ты — дружелюбный AI-репетитор английского языка. "
    "Отвечай на английском, но если нужно объяснить правило, переходи на русский. "
    "Аккуратно исправляй ошибки пользователя, давай краткие пояснения."
)

client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1",
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
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Ошибка: {e}"
    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запускаем встроенный веб-сервер для вебхуков
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=None,  # мы уже установили вебхук вручную
        url_path="webhook",
    )

if __name__ == "__main__":
    main()
