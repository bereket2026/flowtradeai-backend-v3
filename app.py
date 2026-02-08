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

        # Get 7-day price history
        url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days=7"
        data = requests.get(url).json()

        prices = [p[1] for p in data["prices"]]

        first_price = prices[0]
        last_price = prices[-1]

        # Simple trend logic
        if last_price > first_price * 1.02:
            trade_signal = "BUY"
        elif last_price < first_price * 0.98:
            trade_signal = "SELL"
        else:
            trade_signal = "HOLD"

        return jsonify({
            "symbol": symbol.upper() + "USDT",
            "price": round(last_price, 2),
            "signal": trade_signal
        })

    except Exception as e:
        return jsonify({"error": str(e)})
