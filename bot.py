import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "PASTE_NEW_TOKEN_HERE"
API_URL = "https://flowtradeai-backend-v3.onrender.com/signal/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 FlowTradeAI Bot Ready\n\n"
        "Type:\n"
        "/btc\n/eth\n/sol"
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.replace("/", "").lower()

    try:
        res = requests.get(API_URL + symbol).json()

        if "error" in res:
            await update.message.reply_text("❌ " + res["error"])
            return

        msg = (
            f"📊 {res['symbol']}\n"
            f"💰 Price: {res['price']}$\n"
            f"📈 RSI: {res['rsi']}\n"
            f"🚦 Signal: {res['signal']}"
        )

        await update.message.reply_text(msg)

    except:
        await update.message.reply_text("⚠️ Server error")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("btc", signal))
app.add_handler(CommandHandler("eth", signal))
app.add_handler(CommandHandler("sol", signal))

app.run_polling()
