from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import ccxt, random, time

app = Flask(__name__)
CORS(app)

# ===== DATABASE =====
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flowtradeai.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ===== MODELS =====
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    token = db.Column(db.String(120), unique=True)

class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    api_key = db.Column(db.String(200))
    secret = db.Column(db.String(200))

class Strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    stop_loss = db.Column(db.Float, default=1.0)
    take_profit = db.Column(db.Float, default=2.0)
    risk = db.Column(db.Float, default=1.0)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    pair = db.Column(db.String(20))
    price = db.Column(db.Float)
    amount = db.Column(db.Float)
    pnl = db.Column(db.Float)
    time = db.Column(db.Integer)

PAIRS = ["BTC/USDT", "ETH/USDT"]
POSITIONS = {}
AUTO_TRADE = True

# ===== HELPERS =====
def get_user(token):
    return User.query.filter_by(token=token).first()

def get_exchange(user):
    keys = ApiKey.query.filter_by(user_id=user.id).first()
    if not keys:
        return None
    ex = ccxt.binance({
        "apiKey": keys.api_key,
        "secret": keys.secret,
        "enableRateLimit": True,
        "options": {"defaultType": "spot"}
    })
    ex.set_sandbox_mode(True)
    return ex

def get_strategy(user):
    strat = Strategy.query.filter_by(user_id=user.id).first()
    if not strat:
        strat = Strategy(user_id=user.id)
        db.session.add(strat)
        db.session.commit()
    return strat

# ===== ROUTES =====
@app.route("/")
def home():
    return "FlowTradeAI backend running (Strategy Controls)"

@app.route("/login", methods=["POST"])
def login():
    d = request.json
    user = User.query.filter_by(email=d["email"], password=d["password"]).first()
    if not user:
        return jsonify(success=False), 401
    return jsonify(success=True, token=user.token)

@app.route("/strategy", methods=["GET", "POST"])
def strategy():
    token = request.headers.get("Authorization")
    user = get_user(token)
    if not user:
        return jsonify(error="Unauthorized"), 401

    strat = get_strategy(user)

    if request.method == "POST":
        strat.stop_loss = float(request.json["stop_loss"])
        strat.take_profit = float(request.json["take_profit"])
        strat.risk = float(request.json["risk"])
        db.session.commit()

    return jsonify(
        stop_loss=strat.stop_loss,
        take_profit=strat.take_profit,
        risk=strat.risk
    )

@app.route("/account")
def account():
    token = request.headers.get("Authorization")
    user = get_user(token)
    if not user:
        return jsonify(error="Unauthorized"), 401

    trades = Trade.query.filter_by(user_id=user.id).all()
    pnl = round(sum(t.pnl for t in trades), 2)
    return jsonify(balance=10000 + pnl, total_pnl=pnl)

@app.route("/ai-signal")
def ai_signal():
    token = request.headers.get("Authorization")
    user = get_user(token)
    if not user:
        return jsonify(error="Unauthorized"), 401

    exchange = get_exchange(user)
    strat = get_strategy(user)
    results = []

    for pair in PAIRS:
        signal = random.choice(["BUY", "HOLD"])
        confidence = random.randint(60, 95)

        try:
            price = round(exchange.fetch_ticker(pair)["last"], 2)
        except:
            price = round(random.uniform(100, 70000), 2)

        risk_amount = strat.risk / 100
        amount = round(0.01 * risk_amount, 4)

        if AUTO_TRADE and signal == "BUY" and pair not in POSITIONS and exchange:
            POSITIONS[pair] = {
                "entry": price,
                "amount": amount,
                "sl": price * (1 - strat.stop_loss / 100),
                "tp": price * (1 + strat.take_profit / 100)
            }
            try:
                exchange.create_market_buy_order(pair, amount)
            except:
                pass

        if pair in POSITIONS:
            pos = POSITIONS[pair]
            if price <= pos["sl"] or price >= pos["tp"]:
                pnl = round((price - pos["entry"]) * pos["amount"], 2)
                db.session.add(Trade(
                    user_id=user.id,
                    pair=pair,
                    price=price,
                    amount=pos["amount"],
                    pnl=pnl,
                    time=int(time.time())
                ))
                db.session.commit()
                del POSITIONS[pair]

        results.append({
            "pair": pair,
            "signal": signal,
            "confidence": confidence,
            "price": price,
            "position": POSITIONS.get(pair)
        })

    return jsonify(results)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.first():
            db.session.add(User(
                email="admin@flowtradeai.com",
                password="123456",
                token="demo-token"
            ))
            db.session.commit()

    app.run(host="0.0.0.0", port=10000)
