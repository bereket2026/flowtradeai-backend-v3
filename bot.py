import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Get token from Render environment variable
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Your BTC signal API
API_URL = "https://flowtradeai-backend-v3.onrender.com"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot is running!\n\n"
        "Type /btc to get the latest BTC signal."
    )


async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(API_URL, timeout=10)
        data = response.json()

        price = data.get("price", "N/A")
        rsi = data.get("rsi", "N/A")
        signal = data.get("signal", "N/A")
        symbol = data.get("symbol", "BTCUSDT")

        message = (
            f"📊 {symbol} Signal\n"
            f"💰 Price: {price}\n"
            f"📈 RSI: {rsi}\n"
            f"🚦 Signal: {signal}"
        )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")


def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN not set in environment variables")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("btc", btc))

    print("✅ Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
