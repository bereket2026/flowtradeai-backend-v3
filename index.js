const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();
app.use(cors());
app.use(express.json());

let position = "NONE";
let entryPrice = null;
let pnl = null;
let history = [];

// ---------------- INDICATORS ----------------

function calculateRSI(prices, period = 14) {
  if (prices.length < period + 1) return null;

  let gains = 0;
  let losses = 0;

  for (let i = prices.length - period; i < prices.length; i++) {
    const diff = prices[i] - prices[i - 1];
    if (diff >= 0) gains += diff;
    else losses -= diff;
  }

  if (losses === 0) return 100;

  const rs = gains / losses;
  return Math.round(100 - 100 / (1 + rs));
}

function calculateMACD(prices) {
  if (prices.length < 26) return null;
  const short = prices.slice(-12).reduce((a, b) => a + b) / 12;
  const long = prices.slice(-26).reduce((a, b) => a + b) / 26;
  return Math.round((short - long) * 100) / 100;
}

// ---------------- AI LOGIC ----------------

function aiDecision(price, rsi, macd, strategy) {
  let confidence = 60;
  let signal = "HOLD";

  if (strategy === "scalp") confidence += 10;
  if (strategy === "long") confidence -= 10;

  if (rsi !== null) {
    if (rsi < 30) {
      signal = "BUY";
      confidence += 10;
    }
    if (rsi > 70) {
      signal = "SELL";
      confidence += 10;
    }
  }

  if (macd !== null) {
    if (macd > 0 && signal === "BUY") confidence += 5;
    if (macd < 0 && signal === "SELL") confidence += 5;
  }

  confidence = Math.min(confidence, 95);

  return { signal, confidence };
}

// ---------------- API ----------------

app.post("/ai", async (req, res) => {
  try {
    const strategy = req.body.strategy || "swing";

    const market = await axios.get(
      "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100"
    );

    const prices = market.data.map(c => parseFloat(c[4]));
    const price = prices[prices.length - 1];

    const rsi = calculateRSI(prices);
    const macd = calculateMACD(prices);

    const { signal, confidence } =
      aiDecision(price, rsi, macd, strategy);

    // ----- Paper trading -----
    let explanation = "No action taken";

    if (signal === "BUY" && position === "NONE") {
      position = "LONG";
      entryPrice = price;
      explanation = "AI opened LONG position";
      history.unshift({
        time: new Date().toLocaleTimeString(),
        action: "BUY",
        price
      });
    }

    if (signal === "SELL" && position === "LONG") {
      pnl = Math.round(((price - entryPrice) / entryPrice) * 10000) / 100;
      position = "NONE";
      entryPrice = null;
      explanation = "AI closed position";
      history.unshift({
        time: new Date().toLocaleTimeString(),
        action: "SELL",
        price,
        pnl: pnl + "%"
      });
    }

    history = history.slice(0, 20);

    res.json({
      price,
      signal,
      confidence,
      rsi,
      macd,
      position,
      pnl,
      history,
      explanation
    });

  } catch (err) {
    res.status(500).json({ error: "AI backend error" });
  }
});

// ---------------- SERVER ----------------

const PORT = process.env.PORT || 3000;
app.listen(PORT, () =>
  console.log("FlowTradeAI backend running on port " + PORT)
);
