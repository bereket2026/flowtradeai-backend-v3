from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

AUTO_TRADE = False

@app.route("/")
def home():
    return "FlowTradeAI backend is running"

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/ai-signal")
def ai_signal():
    return jsonify(
        signal=random.choice(["BUY", "SELL", "HOLD"]),
        confidence=random.randint(60, 95)
    )

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
