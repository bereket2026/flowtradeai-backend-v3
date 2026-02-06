from flask import Flask, render_template_string

app = Flask(__name__)

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
            padding-top: 50px;
        }
        .card {
            background: #1e293b;
            padding: 20px;
            margin: 20px auto;
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
        .start { background: #22c55e; }
        .stop { background: #ef4444; }
    </style>
</head>
<body>

<h1>🚀 FlowTradeAI Dashboard</h1>

<div class="card">
    <h2>Balance</h2>
    <p>$10,000 (Paper)</p>
</div>

<div class="card">
    <h2>Profit</h2>
    <p>$0.00</p>
</div>

<div class="card">
    <h2>Bot Status</h2>
    <p>Stopped</p>
</div>

<button class="start">Start Bot</button>
<button class="stop">Stop Bot</button>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
