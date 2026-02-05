import threading
import time
from binance.client import Client
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)
client.API_URL = "https://testnet.binance.vision/api"

bot_running = False

def trade_loop():
    global bot_running
    while bot_running:
        try:
            price = float(client.get_symbol_ticker(symbol="BTCUSDT")["price"])
            print(f"Price: {price}")

            balance = float(client.get_asset_balance(asset="USDT")["free"])
            print(f"USDT balance: {balance}")

            if balance > 10:
                qty = round(10 / price, 6)
                order = client.create_order(
                    symbol="BTCUSDT",
                    side="BUY",
                    type="MARKET",
                    quantity=qty
                )
                print("BOUGHT:", order)

            time.sleep(15)

        except Exception as e:
            print("Trade error:", e)
            time.sleep(10)

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

@app.route("/balance")
def balance():
    return jsonify(client.get_account())

@app.route("/")
def home():
    return "FlowTradeAI backend running"

if __name__ == "__main__":
    app.run()
