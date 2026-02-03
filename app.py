from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
