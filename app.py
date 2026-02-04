from flask import Flask, jsonify, request
from flask_cors import CORS
import ccxt, os, random, time

app = Flask(__name__)
CORS(app)

# ===== DEMO LOGIN =====
USER = {"email": "admin@flowtradeai.com", "password": "123456"}

# ===== BINANCE TESTNET =====
exchange = ccxt.binance({
    "apiKey": os.getenv("BINANCE_API_KEY"),
    "secret": os.getenv("BINANCE_SECRET"),
    "enableRateLimit": True,
    "options": {"defaultType": "spot"}
})
exchange.set_sandbox_mode(True)

AUTO_TRADE = False
BALANCE = 10000.0

PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
POSITIONS = {}   # pair -> position
TRADES = []

STOP_LOSS_PCT = 1.0
TAKE_PROFIT_PCT = 2.0

@app.route("/")
def home():
    return "FlowTradeAI backend running (Multi-Pair)"

@app.route("/login", methods=["POST"])
def login():
    d = request.json
    if d and d["email"] == USER["email"] and d["password"] == USER["password"]:
        return jsonify(success=True, token="demo-token")
    return jsonify(success=False), 401

@app.route("/account")
def account():
    pnl = round(sum(t["pnl"] for t in TRADES), 2)
    return jsonify(balance=round(BALANCE, 2), total_pnl=pnl)

@app.route("/ai-signal")
def ai_signal():
    global BALANCE

    results = []

    for pair in PAIRS:
        signal = random.choice(["BUY", "HOLD"])
        confidence = random.randint(60, 95)

        try:
            price = round(exchange.fetch_ticker(pair)["last"], 2)
        except:
            price = round(random.uniform(50, 70000), 2)

        # ===== OPEN =====
        if AUTO_TRADE and signal == "BUY" and pair not in POSITIONS:
            amount = 0.001 if "BTC" in pair else 0.01
            try:
                exchange.create_market_buy_order(pair, amount)
            except:
                pass

            POSITIONS[pair] = {
                "entry": price,
                "amount": amount,
                "sl": price * (1 - STOP_LOSS_PCT / 100),
                "tp": price * (1 + TAKE_PROFIT_PCT / 100)
            }

        # ===== CHECK SL / TP =====
        if pair in POSITIONS:
            pos = POSITIONS[pair]
            if price <= pos["sl"] or price >= pos["tp"]:
                try:
                    exchange.create_market_sell_order(pair, pos["amount"])
                except:
                    pass

                pnl = round((price - pos["entry"]) * pos["amount"], 2)
                BALANCE += pnl

                TRADES.insert(0, {
                    "time": int(time.time()),
                    "pair": pair,
                    "side": "CLOSE",
                    "price": price,
                    "amount": pos["amount"],
                    "pnl": pnl
                })

                del POSITIONS[pair]
                if len(TRADES) > 40:
                    TRADES.pop()

        results.append({
            "pair": pair,
            "signal": signal,
            "confidence": confidence,
            "price": price,
            "position": POSITIONS.get(pair)
        })

    return jsonify(results)

@app.route("/trades")
def trades():
    return jsonify(TRADES)

@app.route("/auto-trade/status")
def auto_trade_status():
    return jsonify(enabled=AUTO_TRADE)

@app.route("/auto-trade/toggle", methods=["POST"])
def toggle_auto_trade():
    global AUTO_TRADE
    AUTO_TRADE = not AUTO_TRADE
    return jsonify(enabled=AUTO_TRADE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
