import requests
from flask import Flask, jsonify

app = Flask(__name__)

# CoinGecko symbol map
COINS = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana"
}

@app.route("/")
def home():
    return "FlowTradeAI Signal API is running 🚀"

@app.route("/signal/<symbol>")
def signal(symbol):
    try:
        symbol = symbol.lower().replace("usdt", "")

        if symbol not in COINS:
            return jsonify({"error": "Unsupported symbol"}), 400

        coin_id = COINS[symbol]

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        data = requests.get(url).json()

        price = data[coin_id]["usd"]

        return jsonify({
            "symbol": symbol.upper() + "USDT",
            "price": price,
            "signal": "BUY"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
