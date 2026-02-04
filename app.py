from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)

# ===== DEMO USER =====
USER = {
    "email": "admin@flowtradeai.com",
    "password": "123456"
}

AUTO_TRADE = False
BALANCE = 10000.0
TRADES = []

@app.route("/")
def home():
    return "FlowTradeAI backend is running"

@app.route("/health")
def health():
    return jsonify(status="ok")

# ===== AUTH =====
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data:
        return jsonify(error="No data"), 400

    if (
        data.get("email") == USER["email"]
        and data.get("password") == USER["password"]
    ):
        return jsonify(success=True, token="demo-token-123")
    return jsonify(success=False), 401

# ===== ACCOUNT =====
@app.route("/account")
def account():
    total_pnl = round(sum(t["pnl"] for t in TRADES), 2)
    return jsonify(balance=round(BALANCE, 2), total_pnl=total_pnl)

# ===== AI SIGNAL =====
@app.route("/ai-signal")
def ai_signal():
    global BALANCE

    signal = random.choice(["BUY", "SELL", "HOLD"])
    confidence = random.randint(60, 95)
    price = round(random.uniform(62000, 68000), 2)

    if AUTO_TRADE and signal != "HOLD":
        amount = round(random.uniform(0.01, 0.03), 4)
        pnl = 0

        if signal == "SELL":
            pnl = round(random.uniform(-80, 150), 2)
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
        if len(TRADES) > 30:
            TRADES.pop()

    return jsonify(signal=signal, confidence=confidence)

@app.route("/trades")
def trades():
    return jsonify(TRADES)

# ===== AUTO TRADE =====
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
