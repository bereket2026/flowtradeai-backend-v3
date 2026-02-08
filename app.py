import requests
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return "FlowTradeAI Signal API is running 🚀"


@app.route("/signal/<symbol>")
def signal(symbol):
    try:
        # convert BTCUSDT → btc
        symbol_clean = symbol.lower().replace("usdt", "")

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol_clean}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        data = response.json()

        # check if symbol exists
        if symbol_clean not in data:
            return jsonify({"error": "Invalid symbol"}), 400

        price = data[symbol_clean]["usd"]

        return jsonify({
            "symbol": symbol.upper(),
            "price": price,
            "signal": "BUY"
        })

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
