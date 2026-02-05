import ccxt
import time
import threading
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flowtradeai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= MODELS =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))


class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    exchange = db.Column(db.String(20))
    api_key = db.Column(db.String(200))
    api_secret = db.Column(db.String(200))


class AutoBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    symbol = db.Column(db.String(20))
    amount = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True)


# ================= EXCHANGE =================
def connect_exchange(api_key, api_secret):
    return ccxt.binance({
        'apiKey': api_key.strip(),
        'secret': api_secret.strip(),
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })


# ================= AI SIGNAL (SIMPLE STRATEGY) =================
def ai_signal(symbol):
    import random
    return random.choice(['buy', 'sell', None])


# ================= LOGIN SYSTEM =================
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "User exists"}), 400

    user = User(username=data["username"], password=data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify({"status": "registered"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(
        username=data["username"],
        password=data["password"]
    ).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"status": "success", "user_id": user.id})


# ================= AUTO TRADE CONTROL =================
auto_trade_enabled = False


@app.route("/auto-trade/start", methods=["POST"])
def start_auto_trade():
    global auto_trade_enabled
    auto_trade_enabled = True
    return jsonify({"status": "started"})


@app.route("/auto-trade/stop", methods=["POST"])
def stop_auto_trade():
    global auto_trade_enabled
    auto_trade_enabled = False
    return jsonify({"status": "stopped"})


@app.route("/auto-trade/status")
def auto_trade_status():
    return jsonify({"running": auto_trade_enabled})


# ================= ACCOUNT DATA =================
@app.route("/account")
def account():
    return jsonify({"balance": "REAL BALANCE FROM BINANCE"})


# ================= AUTO TRADING LOOP =================
def run_autobots():
    global auto_trade_enabled

    with app.app_context():
        while True:
            if not auto_trade_enabled:
                time.sleep(5)
                continue

            bots = AutoBot.query.filter_by(active=True).all()

            for bot in bots:
                key = APIKey.query.filter_by(user_id=bot.user_id).first()
                if not key:
                    continue

                exchange = connect_exchange(key.api_key, key.api_secret)
                signal = ai_signal(bot.symbol)

                try:
                    if signal == 'buy':
                        exchange.create_market_buy_order(bot.symbol, bot.amount)
                    elif signal == 'sell':
                        exchange.create_market_sell_order(bot.symbol, bot.amount)
                except Exception as e:
                    print('Trade error:', e)

            time.sleep(60)


# ================= START BACKGROUND BOT =================
def start_bot_thread():
    thread = threading.Thread(target=run_autobots, daemon=True)
    thread.start()


# ================= MAIN =================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # create default admin if not exists
        if not User.query.filter_by(username="admin").first():
            db.session.add(User(username="admin", password="1234"))
            db.session.commit()

    start_bot_thread()
    app.run(host='0.0.0.0', port=5000)
