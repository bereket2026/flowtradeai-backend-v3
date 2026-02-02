const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

// ================= STATE =================
let prices = [];
let position = null;
let entryPrice = null;
let tradeHistory = [];

// ================= RSI =================
function calculateRSI(values, period = 14) {
  if (values.length < period + 1) return null;

  let gains = 0;
  let losses = 0;

  for (let i = values.length - period; i < values.length; i++) {
    const diff = values[i] - values[i - 1];
    if (diff >= 0) gains += diff;
    else losses -= diff;
  }

  if (losses === 0) return 100;

  const rs = gains / losses;
  return Math.round(100 - 100 / (1 + rs));
}

// ================= EMA =================
function calculateEMA(values, period) {
  const k = 2 / (period + 1);
  let ema = values[0];
  for (let i = 1; i < values.length; i++) {
    ema = values[i] * k + ema * (1 - k);
  }
  return ema;
}

// ================= MACD =================
function calculateMACD(values) {
  if (values.length < 26) return null;

  const ema12 = calculateEMA(values.slice(-12), 12);
  const ema26 = calculateEMA(values.slice(-26), 26);
  return (ema12 - ema26).toFixed(2);
}

// ================= HOME =================
app.get("/", (req, res) => {
  res.json({
    status: "ok",
    message: "FlowTradeAI backend (RSI + MACD) running"
  });
});

// ================= AI ENDPOINT =================
app.post("/ai", async (req, res) => {
  try {
    const response = await fetch(
      "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    );
    const data = await response.json();
    const price = data.bitcoin.usd;

    prices.push(price);
    if (prices.length > 200) prices.shift();

    const rsi = calculateRSI(prices);
    const macd = calculateMACD(prices);

    let signal = "HOLD";
    let confidence = 50;
    let explanation = "Market neutral.";

    if (rsi !== null && macd !== null) {
      if (rsi < 30 && macd > 0) {
        signal = "BUY";
        confidence = 82;
        explanation = `RSI ${rsi} oversold + MACD bullish (${macd}).`;
      } else if (rsi > 70 && macd < 0) {
        signal = "SELL";
        confidence = 84;
        explanation = `RSI ${rsi} overbought + MACD bearish (${macd}).`;
      } else {
        explanation = `RSI ${rsi}, MACD ${macd} → mixed signals.`;
      }
    }

    // ============ PAPER TRADING ============
    if (signal === "BUY" && position !== "LONG") {
      position = "LONG";
      entryPrice = price;
      tradeHistory.push({
        time: new Date().toLocaleString(),
        action: "BUY",
        price
      });
    }

    if (signal === "SELL" && position === "LONG") {
      const pnl = (((price - entryPrice) / entryPrice) * 100).toFixed(2);
      tradeHistory.push({
        time: new Date().toLocaleString(),
        action: "SELL",
        price,
        pnl
      });
      position = null;
      entryPrice = null;
    }

    let pnl = null;
    if (position === "LONG" && entryPrice) {
      pnl = (((price - entryPrice) / entryPrice) * 100).toFixed(2);
    }

    res.json({
      price,
      rsi,
      macd,
      signal,
      confidence,
      position: position || "NONE",
      entryPrice,
      pnl,
      explanation,
      history: tradeHistory.slice(-10)
    });

  } catch (err) {
    res.json({
      signal: "HOLD",
      confidence: 40,
      explanation: "Market data unavailable."
    });
  }
});

// ================= START =================
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log("FlowTradeAI running on port " + PORT);
});
