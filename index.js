const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();
app.use(cors());
app.use(express.json());

let history = [];
let position = "NONE";
let entryPrice = null;

// ---------- INDICATORS ----------

function rsi(prices, period = 14) {
  if (prices.length < period + 1) return null;
  let gains = 0, losses = 0;

  for (let i = prices.length - period; i < prices.length; i++) {
    const diff = prices[i] - prices[i - 1];
    if (diff > 0) gains += diff;
    else losses -= diff;
  }

  if (losses === 0) return 100;
  const rs = gains / losses;
  return Math.round(100 - 100 / (1 + rs));
}

function macd(prices) {
  if (prices.length < 26) return null;
  const ema12 = prices.slice(-12).reduce((a, b) => a + b) / 12;
  const ema26 = prices.slice(-26).reduce((a, b) => a + b) / 26;
  return Math.round((ema12 - ema26) * 100) / 100;
}

// ---------- AI DECISION ----------

function decide(price, rsiVal, macdVal, strategy) {
  let signal = "HOLD";
  let confidence = 60;

  if (strategy === "scalp") confidence += 10;
  if (strategy === "long") confidence -= 10;

  if (rsiVal !== null) {
    if (rsiVal < 30) signal = "BUY";
    if (rsiVal > 70) signal = "SELL";
  }

  if (macdVal !== null) {
    if (macdVal > 0 && signal === "BUY") confidence += 5;
    if (macdVal < 0 && signal === "SELL") confidence += 5;
  }

  confidence = Math.min(confidence, 95);
  return { signal, confidence };
}

// ---------- API ----------

app.post("/ai", async (req, res) => {
  try {
    const strategy = req.body.strategy || "swing";

    const kline = await axios.get(
      "https://api.binance.com/api/v3/klines",
      { params: { symbol: "BTCUSDT", interval: "1m", limit: 100 } }
    );

    const prices = kline.data.map(c => parseFloat(c[4]));
    const price = prices[prices.length - 1];

    const rsiVal = rsi(prices);
    const macdVal = macd(prices);

    const { signal, confidence } =
      decide(price, rsiVal, macdVal, strategy);

    let explanation = "No trade";

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
      const pnl = Math.round(((price - entryPrice) / entryPrice) * 10000) / 100;
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
      rsi: rsiVal,
      macd: macdVal,
      position,
      history,
      explanation
    });

  } catch (e) {
    res.status(500).json({ error: "Backend error" });
  }
});

// ---------- START ----------

const PORT = process.env.PORT || 3000;
app.listen(PORT, () =>
  console.log("FlowTradeAI backend running on port", PORT)
);
