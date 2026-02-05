import os
import time
import threading
import datetime
import random

import ccxt
import jwt

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# ================= APP SETUP =================
app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = "flowtradeai-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flowtradeai.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================= MODELS =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=False)
    last_buy_price = db.Column(db.Float, default=0.0)

# ================= AUTH HELPERS =================
def create_token(user_id):
    return jwt.encode(
        {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
        },
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )

def get_user(req):
    auth = req.headers.get("Authorization")
    if not auth:
        return None
    try:
        token = auth.split(" ")[1]
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return User.query.get(data["user_id"])
    except:
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

# ================= SIMPLE STRATEGY =================
SYMBOL = "BTC/USDT"
TRADE_USDT = 10
BUY_DROP = 0.003   # 0.3%
SELL_PROFIT = 0.004  # 0.4%

# ================= TRADING LOOP =================
def trading_loop():
    while True:
        try:
            with app.app_context():
                bot = Bot.query.filter_by(active=True).first()
                if not bot:
                    time.sleep(10)
                    continue

                exchange = connect_binance()
                ticker = exchange.fetch_ticker(SYMBOL)
                price = ticker["last"]

                # BUY
                if bot.last_buy_price == 0:
                    usdt_balance = exchange.fetch_balance()["free"]["USDT"]
                    if usdt_balance >= TRADE_USDT:
                        amount = TRADE_USDT / price
                        exchange.create_market_buy_order(SYMBOL, amount)
                        bot.last_buy_price = price
                        db.session.commit()
                        print("BOUGHT at", price)

                # SELL
                else:
                    if price >= bot.last_buy_price * (1 + SELL_PROFIT):
                        btc_balance = exchange.fetch_balance()["free"]["BTC"]
                        if btc_balance > 0:
                            exchange.create_market_sell_order(SYMBOL, btc_balance)
                            bot.last_buy_price = 0
                            db.session.commit()
                            print("SOLD at", price)

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
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "User exists"}), 400
    user = User(email=data["email"], password=data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Registered"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(
        email=data["email"], password=data["password"]
    ).first()
    if not user:
        return jsonify({"error": "Invalid login"}), 401
    return jsonify({"token": create_token(user.id)})

@app.route("/start-bot", methods=["POST"])
def start_bot():
    user = get_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    bot = Bot.query.filter_by(user_id=user.id).first()
    if not bot:
        bot = Bot(user_id=user.id, active=True)
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

    bot = Bot.query.filter_by(user_id=user.id).first()
    if bot:
        bot.active = False
        db.session.commit()

    return jsonify({"message": "Bot stopped"})

@app.route("/balance")
def balance():
    exchange = connect_binance()
    bal = exchange.fetch_balance()
    return jsonify({
        "BTC": bal["total"].get("BTC", 0),
        "USDT": bal["total"].get("USDT", 0)
    })

# ================= MAIN =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=10000)
