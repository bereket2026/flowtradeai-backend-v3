import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 Read Telegram token from environment variable (SAFE)
TOKEN = os.getenv("TELEGRAM_TOKEN")

# 📊 BTC signal API endpoint
API_URL = "https://flowtradeai-backend-v3.onrender.com/signal/btc"


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 FlowTradeAI Bot is running!\n\n"
        "Type /btc to get the latest BTC signal."
    )


# /btc command
async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(API_URL, timeout=10)
        data = response.json()

        # If API returns error
        if "error" in data:
            await update.message.reply_text(f"❌ API Error: {data['error']}")
            return

        # Extract values
        price = data.get("price", "N/A")
        rsi = data.get("rsi", "N/A")
        signal = data.get("signal", "N/A")
        symbol = data.get("symbol", "BTCUSDT")

        # Message to user
        message = (
            f"📊 {symbol} Signal\n"
            f"💰 Price: {price}\n"
            f"📈 RSI: {rsi}\n"
            f"🚦 Signal: {signal}"
        )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error getting signal: {e}")


def main():
    # Check token exists
    if not TOKEN:
        print("❌ TELEGRAM_TOKEN not set in environment variables")
        return

    # Create bot
    app = ApplicationBuilder().token(TOKEN).build()

    # Add commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("btc", btc))

    print("✅ Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
