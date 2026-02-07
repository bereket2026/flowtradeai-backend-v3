from flask import Flask, jsonify, render_template
from bot import bot

app = Flask(__name__)


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/status")
def status():
    return jsonify(bot.get_status())


@app.route("/api/start")
def start():
    bot.start()
    return jsonify({"message": "Bot started"})


@app.route("/api/stop")
def stop():
    bot.stop()
    return jsonify({"message": "Bot stopped"})


if __name__ == "__main__":
    app.run(debug=True)
