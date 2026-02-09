import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 Telegram token from environment variable
TOKEN = os.getenv("TELEGRAM_TOKEN")

# BTC signal API
API_URL = "https://flowtradeai-backend-v3.onrender.com"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot is running!\n\n"
        "Type /btc to get BTC signal."
    )


async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(API_URL, timeout=10)
        data = response.json()

        if "error" in data:
            await update.message.reply_text(f"❌ API Error: {data['error']}")
            return

        message = (
            f"📊 {data.get('symbol','BTCUSDT')} Signal\n"
            f"💰 Price: {data.get('price')}\n"
            f"📈 RSI: {data.get('rsi')}\n"
            f"🚦 Signal: {data.get('signal')}"
        )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


def main():
    if not TOKEN:
        print("❌ TELEGRAM_TOKEN not set")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("btc", btc))

    print("✅ Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
