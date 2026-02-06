from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# Root → open dashboard
@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

# Account API
@app.route("/account")
def account():
    return jsonify({
        "status": "connected",
        "balance": 1000,
        "total_pnl": 25
    })

# Health check
@app.route("/health")
def health():
    return jsonify({"status": "FlowTradeAI backend running"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
