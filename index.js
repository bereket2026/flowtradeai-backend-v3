const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

let balance = 10000;
let position = null;
let tradeHistory = [];

function fakePrice() {
  return 30000 + Math.random() * 2000;
}

function aiSignal() {
  const r = Math.random();
  if (r < 0.4) return "BUY";
  if (r < 0.7) return "SELL";
  return "HOLD";
}

app.post("/login", (req, res) => {
  const { email, password } = req.body;
  if (email === "admin@flowtradeai.com" && password === "123456") {
    res.json({ success: true });
  } else {
    res.status(401).json({ error: "Invalid login" });
  }
});

app.post("/ai", (req, res) => {
  const price = fakePrice();
  const signal = aiSignal();
  const confidence = Math.floor(60 + Math.random() * 30);
  const rsi = Math.floor(30 + Math.random() * 40);
  const macd = (Math.random() * 2 - 1).toFixed(2);

  if (signal === "BUY" && !position) {
    position = price;
    balance -= 1000;
    tradeHistory.push({
      time: new Date().toLocaleTimeString(),
      action: "BUY",
      price: price.toFixed(2)
    });
  }

  if (signal === "SELL" && position) {
    const profit = price - position;
    balance += 1000 + profit;
    tradeHistory.push({
      time: new Date().toLocaleTimeString(),
      action: "SELL",
      price: price.toFixed(2)
    });
    position = null;
  }

  res.json({
    price,
    signal,
    confidence,
    rsi,
    macd,
    balance: balance.toFixed(2),
    history: tradeHistory.slice(-5),
    message: "AI analyzed market and executed simulated trades."
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log("FlowTradeAI backend running on port", PORT);
});
