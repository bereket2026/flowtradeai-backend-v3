import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Map common symbols to CoinGecko IDs
SYMBOL_MAP = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "bnb": "binancecoin",
    "sol": "solana",
    "xrp": "ripple",
    "ada": "cardano",
    "doge": "dogecoin"
}

def get_price_and_rsi(coin_id):
    # Get market data (includes price change %)
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_id}"
    data = requests.get(url).json()

    if not data:
        return None, None

    price = data[0]["current_price"]
    change_24h = data[0]["price_change_percentage_24h"]

    # Simple RSI-like logic using 24h change
    if change_24h is None:
        rsi = 50
    else:
        rsi = 50 + change_24h

    return price, rsi


@app.route("/")
def home():
    return "FlowTradeAI Signal API with RSI is LIVE 🚀"


@app.route("/signal/<symbol>")
def signal(symbol):
    symbol = symbol.lower().replace("usdt", "")

    if symbol not in SYMBOL_MAP:
        return jsonify({"error": "Unsupported symbol"})

    coin_id = SYMBOL_MAP[symbol]
    price, rsi = get_price_and_rsi(coin_id)

    if price is None:
        return jsonify({"error": "Data not found"})

    # Trading decision
    if rsi < 30:
        decision = "BUY"
    elif rsi > 70:
        decision = "SELL"
    else:
        decision = "HOLD"

    return jsonify({
        "symbol": symbol.upper() + "USDT",
        "price": price,
        "rsi": round(rsi, 2),
        "signal": decision
    })
