from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import ccxt, random, time, os

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

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    pair = db.Column(db.String(20))
    price = db.Column(db.Float)
    amount = db.Column(db.Float)
    pnl = db.Column(db.Float)
    time = db.Column(db.Integer)

# ===== CONSTANTS =====
PAIRS = ["BTC/USDT", "ETH/USDT"]
STOP_LOSS_PCT = 1.0
TAKE_PROFIT_PCT = 2.0
AUTO_TRADE = True
POSITIONS = {}

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

# ===== ROUTES =====
@app.route("/")
def home():
    return "FlowTradeAI backend running (Database enabled)"

@app.route("/login", methods=["POST"])
def login():
    d = request.json
    user = User.query.filter_by(email=d.get("email"), password=d.get("password")).first()
    if not user:
        return jsonify(success=False), 401
    return jsonify(success=True, token=user.token)

@app.route("/api-keys", methods=["POST"])
def save_keys():
    token = request.headers.get("Authorization")
    user = get_user(token)
    if not user:
        return jsonify(error="Unauthorized"), 401

    ApiKey.query.filter_by(user_id=user.id).delete()
    db.session.add(ApiKey(
        user_id=user.id,
        api_key=request.json.get("apiKey"),
        secret=request.json.get("secret")
    ))
    db.session.commit()
    return jsonify(success=True)

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
    results = []

    for pair in PAIRS:
        signal = random.choice(["BUY", "HOLD"])
        confidence = random.randint(60, 95)

        try:
            price = round(exchange.fetch_ticker(pair)["last"], 2)
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

        # CREATE DEFAULT USER (ONLY FIRST TIME)
        if not User.query.first():
            db.session.add(User(
                email="admin@flowtradeai.com",
                password="123456",
                token="demo-token"
            ))
            db.session.commit()

    app.run(host="0.0.0.0", port=10000)
