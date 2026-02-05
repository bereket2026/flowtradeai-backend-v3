import ccxt
import time
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import jwt
import datetime

app = Flask(__name__)

# 🔓 Allow frontend to connect
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

# ================= AUTH HELPERS =================
def create_token(user_id):
    return jwt.encode(
        {"user_id": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)},
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )

def get_user_from_token(req):
    auth = req.headers.get("Authorization")
    if not auth:
        return None
    token = auth.split(" ")[1]
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return User.query.get(data["user_id"])
    except:
        return None

# ================= AUTH ROUTES =================
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data.get("email"), password=data.get("password")).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_token(user.id)
    return jsonify({"token": token})

# ================= AUTO TRADE ROUTES =================
@app.route("/start-bot", methods=["POST"])
def start_bot():
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    bot = AutoBot.query.filter_by(user_id=user.id).first()
    if not bot:
        bot = AutoBot(user_id=user.id, symbol="BTC/USDT", amount=0.001, active=True)
        db.session.add(bot)
    else:
        bot.active = True

    db.session.commit()
    return jsonify({"message": "Bot started"})

@app.route("/stop-bot", methods=["POST"])
def stop_bot():
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    bot = AutoBot.query.filter_by(user_id=user.id).first()
    if bot:
        bot.active = False
        db.session.commit()

    return jsonify({"message": "Bot stopped"})

# ================= MAIN =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=10000)

