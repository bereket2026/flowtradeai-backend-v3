import os
import ccxt
import time
import datetime
import threading
import jwt

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flowtradeai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'flowtradeai-secret-key'

db = SQLAlchemy(app)

# ================= MODELS =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

class AutoBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    symbol = db.Column(db.String(20), default="BTC/USDT")
    amount = db.Column(db.Float, default=0.001)
    active = db.Column(db.Boolean, default=False)

# ================= AUTH =================
def create_token(user_id):
    return jwt.encode(
        {"user_id": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)},
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )

def get_user(req):
    auth = req.headers.get("Authorization")
    if not auth:
        return None

    try:
        token = auth.split(" ")[1]
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return User.query.get(data["user_id"])
    except Exception:
        return None

# ================= BINANCE TESTNET =================
def connect_binance():
    return ccxt.binance({
        "apiKey": os.getenv("BINANCE_API_KEY"),
        "secret": os.getenv("BINANCE_SECRET"),
        "enableRateLimit": True,
        "options": {"defaultType": "spot"},
        "urls": {
            "api": {
                "public": "https://testnet.binance.vision/api",
                "private": "https://testnet.binance.vision/api"
            }
        }
    })

# ================= SIMPLE AI SIGNAL =================
def ai_signal():
    import random
    return random.choice(["buy", "sell", None])

# ================= TRADING LOOP =================
def trading_loop():
    while True:
        with app.app_context():
            bots = AutoBot.query.filter_by(active=True).all()

            if bots:
                exchange = connect_binance()

                for bot in bots:
                    try:
                        signal = ai_signal()

                        if signal == "buy":
                            exchange.create_market_buy_order(bot.symbol, bot.amount)

                        elif signal == "sell":
                            exchange.create_market_sell_order(bot.symbol, bot.amount)

                    except Exception as e:
                        print("Trade error:", e)

        time.sleep(20)

threading.Thread(target=trading_loop, daemon=True).start()

# ================= ROUTES =================
@app.route("/")
def home():
    return "FlowTradeAI backend is running"

@app.route("/register", methods=["POST"])
def register():
    data = request.json

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing email or password"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "User exists"}), 400

    user = User(email=data["email"], password=data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registered"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(email=data.get("email"), password=data.get("password")).first()

    if not user:
        return jsonify({"error": "Invalid login"}), 401

    return jsonify({"token": create_token(user.id)})

@app.route("/start-bot", methods=["POST"])
def start_bot():
    user = get_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    bot = AutoBot.query.filter_by(user_id=user.id).first()

    if not bot:
        bot = AutoBot(user_id=user.id, active=True)
        db.session.add(bot)
    else:
        bot.active = True

    db.session.commit()
    return jsonify({"message": "Bot started (TESTNET)"})

@app.route("/stop-bot", methods=["POST"])
def stop_bot():
    user = get_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    bot = AutoBot.query.filter_by(user_id=user.id).first()
    if bot:
        bot.active = False
        db.session.commit()

    return jsonify({"message": "Bot stopped"})

@app.route("/balance", methods=["GET"])
def balance():
    try:
        exchange = connect_binance()
        bal = exchange.fetch_balance()

        return jsonify({
            "BTC": bal["total"].get("BTC", 0),
            "USDT": bal["total"].get("USDT", 0)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= MAIN =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=10000)
