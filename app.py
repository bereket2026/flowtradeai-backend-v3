from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "FlowTradeAI Signal API is running 🚀"

@app.route("/price/<symbol>")
def price(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
    data = requests.get(url).json()
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
