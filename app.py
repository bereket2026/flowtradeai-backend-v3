from flask import Flask, jsonify
from binance.client import Client
import os

app = Flask(__name__)

# Binance client (no keys needed for public price)
client = Client()

@app.route("/")
def home():
    return "FlowTradeAI Signal API is running 🚀"

@app.route("/price/<symbol>")
def price(symbol):
    ticker = client.get_symbol_ticker(symbol=symbol.upper())
    return jsonify(ticker)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
