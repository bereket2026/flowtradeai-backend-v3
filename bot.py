import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 Put your NEW Telegram token here or use environment variable
TOKEN = os.getenv("TELEGRAM_TOKEN", "PASTE_NEW_TOKEN_HERE")

# Your BTC signal API endpoint (replace with your real URL if different)
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

        # If API returns error
        if "error" in data:
            await update.message.reply_text(f"❌ API Error: {data['error']}")
            return

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
        await update.message.reply_text(f"⚠️ Error fetching data: {str(e)}")


def main():
    if TOKEN == AAF05oQ9mRlh-PRkbVU3KbXoPeF6yJ_VtwM

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("btc", btc))

    print("✅ Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
