from flask import Flask, jsonify, request
from flask_cors import CORS
import ccxt, random, time

app = Flask(__name__)
CORS(app)

# ===== DEMO USER =====
USER = {
    "email": "admin@flowtradeai.com",
    "password": "123456",
    "token": "demo-token"
}

# ===== USER STORAGE (DEMO / IN-MEMORY) =====
USER_KEYS = {}       # token -> {apiKey, secret}
AUTO_TRADE = False
BALANCE = 10000.0
TRADES = []
POSITIONS = {}

PAIRS = ["BTC/USDT", "ETH/USDT"]
STOP_LOSS_PCT = 1.0
TAKE_PROFIT_PCT = 2.0

def get_exchange(token):
    keys = USER_KEYS.get(token)
    if not keys:
        return None
    ex = ccxt.binance({
        "apiKey": keys["apiKey"],
        "secret": keys["secret"],
        "enableRateLimit": True,
        "options": {"defaultType": "spot"}
    })
    ex.set_sandbox_mode(True)
    return ex

@app.route("/")
def home():
    return "FlowTradeAI backend running (User API Keys)"

# ===== AUTH =====
@app.route("/login", methods=["POST"])
def login():
    d = request.json
    if d and d["email"] == USER["email"] and d["password"] == USER["password"]:
        return jsonify(success=True, token=USER["token"])
    return jsonify(success=False), 401

# ===== SAVE API KEYS =====
@app.route("/api-keys", methods=["POST"])
def save_keys():
    token = request.headers.get("Authorization")
    d = request.json
    if token != USER["token"]:
        return jsonify(error="Unauthorized"), 401

    USER_KEYS[token] = {
        "apiKey": d.get("apiKey"),
        "secret": d.get("secret")
    }
    return jsonify(success=True)

@app.route("/api-keys/status")
def key_status():
    token = request.headers.get("Authorization")
    return jsonify(connected=token in USER_KEYS)

# ===== ACCOUNT =====
@app.route("/account")
def account():
    pnl = round(sum(t["pnl"] for t in TRADES), 2)
    return jsonify(balance=round(BALANCE, 2), total_pnl=pnl)

# ===== AI ENGINE =====
@app.route("/ai-signal")
def ai_signal():
    global BALANCE
    token = request.headers.get("Authorization")
    exchange = get_exchange(token)

    results = []

    for pair in PAIRS:
        signal = random.choice(["BUY", "HOLD"])
        confidence = random.randint(60, 95)

        try:
            price = round(exchange.fetch_ticker(pair)["last"], 2) if exchange else 0
        except:
            price = round(random.uniform(100, 70000), 2)

        # OPEN
        if AUTO_TRADE and signal == "BUY" and pair not in POSITIONS and exchange:
            amount = 0.001
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

        # CLOSE
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

        results.append({
            "pair": pair,
            "signal": signal,
            "confidence": confidence,
            "price": price,
            "position": POSITIONS.get(pair)
        })

    return jsonify(results)

@app.route("/auto-trade/toggle", methods=["POST"])
def toggle():
    global AUTO_TRADE
    AUTO_TRADE = not AUTO_TRADE
    return jsonify(enabled=AUTO_TRADE)

@app.route("/auto-trade/status")
def status():
    return jsonify(enabled=AUTO_TRADE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
