from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>FlowTradeAI Backend Running</h1>
    <p>Use /status or /account endpoint.</p>
    """

@app.route("/status")
def status():
    return jsonify({"status": "FlowTradeAI backend running"})

@app.route("/account")
def account():
    return jsonify({"balance": 1000, "status": "connected", "total_pnl": 25})
