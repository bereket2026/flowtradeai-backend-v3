import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔒 PUT YOUR NEW TELEGRAM TOKEN HERE (keep it secret)
TOKEN = "PASTE_NEW_TOKEN_HERE"

# Your FlowTradeAI API URL
API_URL = "https://flowtradeai-backend-v3.onrender.com/signal/{}"


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 FlowTradeAI Bot is LIVE!\n\n"
        "Commands:\n"
        "/btc → Bitcoin signal\n"
        "/eth → Ethereum signal"
    )


# Function to get signal from API
async def get_signal(update: Update, symbol: str):
    try:
        response = requests.get(API_URL.format(symbol))
        data = response.json()

        if "error" in data:
            await update.message.reply_text(f"❌ {data['error']}")
            return

        message = (
            f"📊 {data['symbol']}\n"
            f"💰 Price: {data['price']}\n"
            f"🚦 Signal: {data['signal']}"
        )

        await update.message.reply_text(message)

    except Exception:
        await update.message.reply_text("⚠️ Failed to fetch signal.")


# BTC command
async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_signal(update, "bitcoin")


# ETH command
async def eth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_signal(update, "ethereum")


# Create and run bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("btc", btc))
app.add_handler(CommandHandler("eth", eth))

app.run_polling()
