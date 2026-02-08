import requests
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "FlowTradeAI Signal API is running 🚀"

@app.route("/signal/<symbol>")
def signal(symbol):
    try:
        symbol = symbol.lower().replace("usdt", "")

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()

        # check if symbol exists
        if symbol not in data:
            return jsonify({"error": "Symbol not found on CoinGecko"})

        price = data[symbol]["usd"]

        return jsonify({
            "symbol": symbol.upper() + "USDT",
            "price": price,
            "signal": "BUY"
        })

    except Exception as e:
        return jsonify({"error": str(e)})
