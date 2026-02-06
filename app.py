# FlowTradeAI – Professional AI Trading Backend (Flask)

import ccxt
import time
import threading
import random
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# ================= APP SETUP =================
app = Flask(__name__, static_folder="static", static_url_path="/")
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flowtradeai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ================= DATABASE =================
db = SQLAlchemy(app)


# ================= MODELS =================
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


# ================= EXCHANGE CONNECTION =================
def connect_exchange(api_key, api_secret):
    return ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })


# ================= AI SIGNAL (DEMO) =================
def ai_signal(symbol):
    return random.choice(['buy', 'sell', None])


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


# ================= DEMO ACCOUNT DATA =================
@app.route("/account")
def account():
    return jsonify({"balance": 1000, "total_pnl": 25})


@app.route("/ai-signal")
def signals():
    return jsonify([
        {"pair": "BTC/USDT", "signal": "BUY", "confidence": 72, "price": 43000},
        {"pair": "ETH/USDT", "signal": "SELL", "confidence": 64, "price": 2300},
    ])


# ================= HOME PAGE (SERVE DASHBOARD) =================
@app.route("/")
def home():
    return app.send_static_file("index.html")


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

    start_bot_thread()
    app.run(host='0.0.0.0', port=5000)
