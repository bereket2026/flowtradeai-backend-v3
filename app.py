from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="static")
CORS(app)

# Root → status message
@app.route("/")
def home():
    return jsonify({"status": "FlowTradeAI backend running"})

# Dashboard → open HTML page
@app.route("/dashboard")
def dashboard():
    return send_from_directory("static", "index.html")

# Example API endpoint
@app.route("/account")
def account():
    return jsonify({
        "balance": 1000,
        "total_pnl": 25,
        "status": "connected"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
