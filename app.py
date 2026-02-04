from flask import Flask, jsonify, request
from flask_cors import CORS
import ccxt
import random
import time
import os

app = Flask(__name__)
CORS(app)

# ===== DEMO LOGIN =====
USER = {
    "email": "admin@flowtradeai.com",
    "password": "123456"
}

# ===== BINANCE TESTNET KEYS =====
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_SECRET = os.getenv("BINANCE_SECRET", "")

exchange = ccxt.binance({
    "apiKey": BINANCE_API_KEY,
    "secret": BINANCE_SECRET,
    "enableRateLimit": True,
    "options": {
        "defaultType": "spot"
    }
})

exchange.set_sandbox_mode(True)

AUTO_TRADE = False
BALANCE = 10000.0
TRADES = []

@app.route("/")
def home():
    return "FlowTradeAI backend is running (Binance Testnet)"

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if data and data.get("email") == USER["email"] and data.get("password") == USER["password"]:
        return jsonify(success=True, token="demo-token")
    return jsonify(success=False), 401

@app.route("/account")
def account():
    total_pnl = round(sum(t["pnl"] for t in TRADES), 2)
    return jsonify(balance=round(BALANCE, 2), total_pnl=total_pnl)

@app.route("/ai-signal")
def ai_signal():
    global BALANCE

    signal = random.choice(["BUY", "SELL", "HOLD"])
    confidence = random.randint(60, 95)

    try:
        ticker = exchange.fetch_ticker("BTC/USDT")
        price = round(ticker["last"], 2)
    except:
        price = round(random.uniform(62000, 68000), 2)

    if AUTO_TRADE and signal != "HOLD":
        amount = 0.001
        pnl = 0

        try:
            if signal == "BUY":
                exchange.create_market_buy_order("BTC/USDT", amount)
            elif signal == "SELL":
                exchange.create_market_sell_order("BTC/USDT", amount)
                pnl = round(random.uniform(-20, 40), 2)
                BALANCE += pnl
        except Exception as e:
            print("Trade error:", e)

        TRADES.insert(0, {
            "time": int(time.time()),
            "pair": "BTC/USDT",
            "side": signal,
            "price": price,
            "amount": amount,
            "pnl": pnl
        })

        if len(TRADES) > 25:
            TRADES.pop()

    return jsonify(signal=signal, confidence=confidence)

@app.route("/trades")
def trades():
    return jsonify(TRADES)

@app.route("/auto-trade/status")
def auto_trade_status():
    return jsonify(enabled=AUTO_TRADE)

@app.route("/auto-trade/toggle", methods=["POST"])
def toggle_auto_trade():
    global AUTO_TRADE
    AUTO_TRADE = not AUTO_TRADE
    return jsonify(enabled=AUTO_TRADE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
