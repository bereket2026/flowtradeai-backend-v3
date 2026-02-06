from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="static")
CORS(app)

# Root
@app.route("/")
def home():
    return jsonify({"status": "FlowTradeAI backend running"})

# Dashboard page
@app.route("/dashboard")
def dashboard():
    return send_from_directory("static", "index.html")

# Account info
@app.route("/account")
def account():
    return jsonify({
        "balance": 1000,
        "total_pnl": 25,
        "status": "connected"
    })

# Register
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    return jsonify({
        "message": "User registered successfully",
        "user": data
    })

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    return jsonify({
        "message": "Login successful",
        "token": "demo-token-123"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
