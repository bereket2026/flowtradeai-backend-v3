import requests
from flask import Flask, jsonify

app = Flask(__name__)

# CoinGecko ID mapping
SYMBOL_MAP = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
    "bnb": "binancecoin",
    "xrp": "ripple",
    "ada": "cardano",
}

@app.route("/")
def home():
    return "FlowTradeAI Signal API is running 🚀"


@app.route("/signal/<symbol>")
def signal(symbol):
    try:
        symbol = symbol.lower().replace("usdt", "")

        # convert to CoinGecko id
        if symbol not in SYMBOL_MAP:
            return jsonify({"error": "Unsupported symbol"})

        coin_id = SYMBOL_MAP[symbol]

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        data = requests.get(url).json()

        price = data[coin_id]["usd"]

        # simple RSI placeholder logic
        rsi = 50

        if rsi < 30:
            sig = "BUY"
        elif rsi > 70:
            sig = "SELL"
        else:
            sig = "HOLD"

        return jsonify({
            "symbol": symbol.upper() + "USDT",
            "price": price,
            "rsi": rsi,
            "signal": sig
        })

    except Exception as e:
        return jsonify({"error": str(e)})
