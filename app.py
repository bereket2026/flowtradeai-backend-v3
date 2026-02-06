from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)


# ---------- HOME PAGE ----------
@app.route("/")
def home():
    return send_from_directory("static", "index.html")


# ---------- ACCOUNT DATA ----------
@app.route("/account")
def account():
    return jsonify({
        "balance": 1000,
        "total_pnl": 25
    })


# ---------- HEALTH CHECK ----------
@app.route("/health")
def health():
    return "OK"


# ---------- RUN SERVER ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
