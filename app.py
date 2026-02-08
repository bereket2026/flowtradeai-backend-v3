import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)


# Home route
@app.route("/")
def home():
    return "FlowTradeAI Signal API is running 🚀"


# Dashboard route (needs templates/index.html)
@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


# Signal API
@app.route("/signal/<symbol>")
def signal(symbol):
    try:
        # convert BTCUSDT → btc
        symbol = symbol.lower().replace("usdt", "")

        # CoinGecko price API
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()

        # check if symbol exists
        if symbol not in data:
            return jsonify({"error": "Symbol not found on CoinGecko"})

        price = data[symbol]["usd"]

        # simple demo signal logic
        signal_type = "BUY" if price % 2 == 0 else "HOLD"

        return jsonify({
            "symbol": symbol.upper() + "USDT",
            "price": price,
            "signal": signal_type
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# Run locally (Render uses gunicorn instead)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
