import random
import time
from flask import Flask, jsonify

app = Flask(__name__)

# ------------------------------
# Simple in-memory paper account
# ------------------------------
account = {
    "balance_usdt": 1000.0,
    "position": None,
    "entry_price": 0.0,
    "trade_history": []
}

# ------------------------------
# Fake market price generator
# (later we connect real API)
# ------------------------------
current_price = 30000.0

def get_market_price():
    global current_price
    change = random.uniform(-50, 50)
    current_price += change
    return round(current_price, 2)

# ------------------------------
# Simple trading strategy
# ------------------------------

def trading_decision(price):
    """Very simple demo strategy"""

    # Buy if price randomly chosen low signal
    if account["position"] is None and random.random() < 0.3:
        return "BUY"

    # Sell if we are in position and small profit
    if account["position"] == "LONG" and price > account["entry_price"] * 1.002:
        return "SELL"

    return "HOLD"

# ------------------------------
# Execute paper trade
# ------------------------------

def execute_trade(action, price):
    if action == "BUY" and account["position"] is None:
        account["position"] = "LONG"
        account["entry_price"] = price
        account["trade_history"].append({
            "type": "BUY",
            "price": price
        })

    elif action == "SELL" and account["position"] == "LONG":
        profit = price - account["entry_price"]
        account["balance_usdt"] += profit
        account["position"] = None
        account["entry_price"] = 0.0
        account["trade_history"].append({
            "type": "SELL",
            "price": price,
            "profit": round(profit, 2)
        })

# ------------------------------
# Bot loop (runs in background)
# ------------------------------

def bot_step():
    price = get_market_price()
    decision = trading_decision(price)
    execute_trade(decision, price)

    return {
        "price": price,
        "decision": decision,
        "account": account
    }

# ------------------------------
# API Routes for dashboard
# ------------------------------

@app.route("/")
def home():
    return "FlowTradeAI Paper Bot Running"

@app.route("/status")
def status():
    return jsonify(bot_step())

@app.route("/history")
def history():
    return jsonify(account["trade_history"])


# ------------------------------
# Local run (Render uses gunicorn)
# ------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
