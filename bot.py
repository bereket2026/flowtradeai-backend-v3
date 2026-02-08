import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔑 PUT YOUR TELEGRAM BOT TOKEN HERE
TOKEN = "PASTE_NEW_TOKEN_HERE"

# Your working signal API
API_URL = "https://flowtradeai-backend-v3.onrender.com/signal/bitcoin"


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 FlowTradeAI Bot Ready!\n\n"
        "Type /signal to get Bitcoin signal."
    )


# /signal command
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        res = requests.get(API_URL, timeout=10)
        data = res.json()

        message = (
            f"📊 *BTC Signal*\n\n"
            f"💰 Price: {data.get('price')}$\n"
            f"📈 RSI: {data.get('rsi')}\n"
            f"🧠 Signal: *{data.get('signal')}*"
        )

        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception:
        await update.message.reply_text("❌ Error getting signal. Try later.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
