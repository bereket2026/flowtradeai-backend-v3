from flask import Flask, jsonify
import random

app = Flask(__name__)

# --- Fake price generator (for now) ---
def get_price():
    return round(random.uniform(60000, 70000), 2)


# --- Simple RSI/EMA-like logic ---
def generate_signal(price):
    if price > 65000:
        return "SELL"
    elif price < 63000:
        return "BUY"
    else:
        return "HOLD"


@app.route("/")
def home():
    return "FlowTradeAI Signal API is running 🚀"


@app.route("/price")
def price():
    return jsonify({"price": get_price()})


@app.route("/signal")
def signal():
    price = get_price()
    return jsonify({
        "price": price,
        "signal": generate_signal(price)
    })


@app.route("/status")
def status():
    return jsonify({"status": "online"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
