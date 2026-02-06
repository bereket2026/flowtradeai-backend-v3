from flask import Flask, jsonify
from binance.client import Client
import os

app = Flask(__name__)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)
client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"

@app.route("/")
def home():
    return "FlowTradeAI backend running with Binance Testnet"

@app.route("/account")
def account():
    try:
        balance_info = client.futures_account_balance()

        usdt = next((b for b in balance_info if b["asset"] == "USDT"), None)

        return jsonify({
            "balance": float(usdt["balance"]) if usdt else 0,
            "pnl": float(usdt["crossUnPnl"]) if usdt else 0,
            "status": "connected to Binance TESTNET"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
