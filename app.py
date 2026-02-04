from flask import Flask, jsonify
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)

AUTO_TRADE = False
BALANCE = 10000.0  # starting USDT balance
TRADES = []

@app.route("/")
def home():
    return "FlowTradeAI backend is running"

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/account")
def account():
    total_pnl = round(sum(t["pnl"] for t in TRADES), 2)
    return jsonify(
        balance=round(BALANCE, 2),
        total_pnl=total_pnl
    )

@app.route("/ai-signal")
def ai_signal():
    global BALANCE

    signal = random.choice(["BUY", "SELL", "HOLD"])
    confidence = random.randint(60, 95)
    price = round(random.uniform(62000, 68000), 2)

    if AUTO_TRADE and signal != "HOLD":
        amount = round(random.uniform(0.01, 0.03), 4)
        cost = price * amount

        pnl = 0
        if signal == "SELL":
            pnl = round(random.uniform(-50, 120), 2)
            BALANCE += pnl

        trade = {
            "time": int(time.time()),
            "pair": "BTC/USDT",
            "side": signal,
            "price": price,
            "amount": amount,
            "pnl": pnl
        }

        TRADES.insert(0, trade)
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
