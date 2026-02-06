from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "FlowTradeAI backend running"

@app.route("/account")
def account():
    return jsonify({
        "balance": 1000,
        "pnl": 25,
        "status": "demo mode"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
