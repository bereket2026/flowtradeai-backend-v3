import os
import threading
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from binance.client import Client

# ================= APP SETUP =================
app = Flask(__name__)
CORS(app)

# ================= BINANCE TESTNET =================
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)
client.API_URL = "https://testnet.binance.vision/api"

# ================= BOT STATE =================
bot_running = False
last_buy_price = None
profit_total = 0.0

# ================= TRADING LOGIC =================
def trade_loop():
    global bot_running, last_buy_price, profit_total

    print("🚀 Trade loop started")

    while bot_running:
        try:
            price = float(client.get_symbol_ticker(symbol="BTCUSDT")["price"])
            print(f"📈 BTC Price: {price}")

            usdt_balance = float(client.get_asset_balance(asset="USDT")["free"])
            print(f"💰 USDT Balance: {usdt_balance}")

            # BUY
            if last_buy_price is None and usdt_balance > 12:
                qty = round(10 / price, 6)

                client.create_order(
                    symbol="BTCUSDT",
                    side="BUY",
                    type="MARKET",
                    quantity=qty
                )

                last_buy_price = price
                print(f"🟢 BOUGHT BTC at {price}")

            # SELL
            elif last_buy_price is not None:
                target = last_buy_price * 1.003  # 0.3% profit

                if price >= target:
                    btc_balance = float(client.get_asset_balance(asset="BTC")["free"])

                    if btc_balance > 0:
                        qty = round(btc_balance, 6)

                        client.create_order(
                            symbol="BTCUSDT",
                            side="SELL",
                            type="MARKET",
                            quantity=qty
                        )

                        trade_profit = (price - last_buy_price) * qty
                        profit_total += trade_profit

                        print(f"🔴 SOLD BTC | Profit: {trade_profit:.4f} USDT")

                        last_buy_price = None

            time.sleep(15)

        except Exception as e:
            print("❌ Trade error:", e)
            time.sleep(10)

# ================= ROUTES =================
@app.route("/")
def home():
    return "FlowTradeAI backend running"


@app.route("/start-bot", methods=["POST"])
def start_bot():
    global bot_running

    if not bot_running:
        bot_running = True
        threading.Thread(target=trade_loop, daemon=True).start()

    return jsonify({"status": "Bot started"})


@app.route("/stop-bot", methods=["POST"])
def stop_bot():
    global bot_running
    bot_running = False
    return jsonify({"status": "Bot stopped"})


@app.route("/status")
def status():
    return jsonify({
        "bot_running": bot_running,
        "last_buy_price": last_buy_price,
        "profit_total": round(profit_total, 4)
    })


@app.route("/balance")
def balance():
    try:
        return jsonify(client.get_account())
    except Exception as e:
        return jsonify({"error": str(e)})


# ================= MAIN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
