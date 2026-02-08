from flask import Flask, jsonify
from binance.client import Client

app = Flask(__name__)
client = Client()

@app.route("/")
def home():
    return "FlowTradeAI Signal API is running 🚀"

@app.route("/signal/<symbol>")
def signal(symbol):
    try:
        symbol = symbol.upper()   # IMPORTANT FIX

        price = client.get_symbol_ticker(symbol=symbol)["price"]

        return jsonify({
            "symbol": symbol,
            "price": price,
            "signal": "BUY"  # simple test signal
        })

    except Exception as e:
        return jsonify({"error": str(e)})
