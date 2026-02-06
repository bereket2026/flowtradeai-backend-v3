from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="static")
CORS(app)

# MAIN PAGE → open dashboard directly
@app.route("/")
def home():
    return send_from_directory("static", "index.html")

# API → account info
@app.route("/account")
def account():
    return jsonify({
        "balance": 1000,
        "total_pnl": 25,
        "status": "connected"
    })

# OPTIONAL → health check
@app.route("/status")
def status():
    return jsonify({"status": "FlowTradeAI backend running"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
