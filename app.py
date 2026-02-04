from flask import Flask, jsonify
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)

AUTO_TRADE = False
TRADES = []

@app.route("/")
def home():
    return "FlowTradeAI backend is running"

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/ai-signal")
def ai_signal():
    signal = random.choice(["BUY", "SELL", "HOLD"])
    confidence = random.randint(60, 95)

    if AUTO_TRADE and signal != "HOLD":
        trade = {
            "time": int(time.time()),
            "pair": "BTC/USDT",
            "side": signal,
            "price": round(random.uniform(62000, 68000), 2),
            "amount": round(random.uniform(0.01, 0.05), 4)
        }
        TRADES.insert(0, trade)
        if len(TRADES) > 20:
            TRADES.pop()

    return jsonify(signal=signal, confidence=confidence)

@app.route("/trades")
def get_trades():
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
