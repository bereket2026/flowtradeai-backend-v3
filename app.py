# FlowTradeAI – Professional AI Trading Backend (Flask)

import ccxt
import time
import threading
import os
import random
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# ================= APP SETUP =================
app = Flask(__name__, static_folder="static", static_url_path="/")
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flowtradeai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= DATABASE MODELS =================
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
        'options': {'defaultType': 'spot'},
        'urls': {
            'api': {
                'public': 'https://testnet.binance.vision/api',
                'private': 'https://testnet.binance.vision/api'
            }
        }
    })


# ================= SIMPLE AI SIGNAL =================
def ai_signal(symbol):
    return random.choice(['buy', 'sell', None])


# ================= GLOBAL BOT STATE =================
auto_trade_enabled = False


# ================= PRICE ENDPOINT =================
@app.route("/price/<symbol>")
def get_price(symbol):
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker(symbol.upper())
        return jsonify({"price": ticker['last']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= AUTO TRADE CONTROL =================
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


# ================= DEMO ACCOUNT =================
@app.route("/account")
def account():
    return jsonify({"balance": 1000, "pnl": 0})


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

                try:
                    exchange = connect_exchange(key.api_key.strip(), key.api_secret.strip())
                    signal = ai_signal(bot.symbol)

                    if signal == 'buy':
                        exchange.create_market_buy_order(bot.symbol, bot.amount)
                        print("BUY order executed")

                    elif signal == 'sell':
                        exchange.create_market_sell_order(bot.symbol, bot.amount)
                        print("SELL order executed")

                except Exception as e:
                    print("Trade error:", e)

            time.sleep(60)


# ================= START BOT THREAD =================
def start_bot_thread():
    thread = threading.Thread(target=run_autobots, daemon=True)
    thread.start()


# ================= SERVE DASHBOARD =================
@app.route("/")
def serve_dashboard():
    return send_from_directory("static", "index.html")


# ================= MAIN =================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    start_bot_thread()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
