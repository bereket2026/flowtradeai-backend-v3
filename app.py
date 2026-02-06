from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

bot_running = False
profit = 0.0
balance = 10000


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>FlowTradeAI Dashboard</title>
    <style>
        body {
            font-family: Arial;
            background: #0f172a;
            color: white;
            text-align: center;
            padding-top: 40px;
        }
        .card {
            background: #1e293b;
            padding: 20px;
            margin: 15px auto;
            width: 300px;
            border-radius: 12px;
        }
        button {
            padding: 10px 20px;
            margin: 10px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }
        .start { background: #22c55e; color: white; }
        .stop { background: #ef4444; color: white; }
    </style>
</head>
<body>

<h1>🚀 FlowTradeAI Dashboard</h1>

<div class="card">
    <h2>Balance</h2>
    <p id="balance">$0</p>
</div>

<div class="card">
    <h2>Profit</h2>
    <p id="profit">$0</p>
</div>

<div class="card">
    <h2>Bot Status</h2>
    <p id="status">Stopped</p>
</div>

<button class="start" onclick="startBot()">Start Bot</button>
<button class="stop" onclick="stopBot()">Stop Bot</button>

<script>
async function refresh() {
    const res = await fetch("/data");
    const d = await res.json();

    document.getElementById("balance").innerText = "$" + d.balance;
    document.getElementById("profit").innerText = "$" + d.profit;
    document.getElementById("status").innerText = d.running ? "Running" : "Stopped";
}

async function startBot() {
    await fetch("/start");
    refresh();
}

async function stopBot() {
    await fetch("/stop");
    refresh();
}

setInterval(refresh, 2000);
refresh();
</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/data")
def data():
    return jsonify({
        "balance": balance,
        "profit": profit,
        "running": bot_running
    })


@app.route("/start")
def start():
    global bot_running
    bot_running = True
    return jsonify({"status": "bot started"})


@app.route("/stop")
def stop():
    global bot_running
    bot_running = False
    return jsonify({"status": "bot stopped"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
