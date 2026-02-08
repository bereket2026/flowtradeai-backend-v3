from flask import Flask, jsonify
import requests

app = Flask(__name__)

last_price = {}

@app.route("/")
def home():
    return "FlowTradeAI Signal API is running 🚀"

@app.route("/signal/<symbol>")
def signal(symbol):
    global last_price

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
    data = requests.get(url).json()

    if symbol.lower() not in data:
        return jsonify({"error": "Invalid symbol"})

    price = data[symbol.lower()]["usd"]

    # first time → no signal
    if symbol not in last_price:
        last_price[symbol] = price
        return jsonify({
            "symbol": symbol,
            "price": price,
            "signal": "WAIT"
        })

    # compare prices
    if price > last_price[symbol]:
        sig = "BUY"
    elif price < last_price[symbol]:
        sig = "SELL"
    else:
        sig = "HOLD"

    last_price[symbol] = price

    return jsonify({
        "symbol": symbol,
        "price": price,
        "signal": sig
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
