const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();
app.use(cors());
app.use(express.json());

// ===== UTIL FUNCTIONS =====
function calculateRSI(closes, period = 14) {
  let gains = 0;
  let losses = 0;

  for (let i = 1; i <= period; i++) {
    const diff = closes[i] - closes[i - 1];
    if (diff >= 0) gains += diff;
    else losses -= diff;
  }

  const avgGain = gains / period;
  const avgLoss = losses / period || 1;

  const rs = avgGain / avgLoss;
  return 100 - 100 / (1 + rs);
}

function calculateEMA(values, period) {
  const k = 2 / (period + 1);
  let ema = values[0];

  for (let i = 1; i < values.length; i++) {
    ema = values[i] * k + ema * (1 - k);
  }
  return ema;
}

function calculateMACD(closes) {
  const ema12 = calculateEMA(closes.slice(-26), 12);
  const ema26 = calculateEMA(closes.slice(-26), 26);
  const macd = ema12 - ema26;
  return macd;
}

// ===== ROUTES =====
app.get("/", (req, res) => {
  res.send("FlowTradeAI backend running with RSI + MACD");
});

app.post("/ai", async (req, res) => {
  try {
    const candles = await axios.get(
      "https://api.binance.com/api/v3/klines",
      { params: { symbol: "BTCUSDT", interval: "1m", limit: 100 } }
    );

    const closes = candles.data.map(c => parseFloat(c[4]));
    const price = closes[closes.length - 1];

    const rsi = calculateRSI(closes.slice(-15));
    const macd = calculateMACD(closes);

    let signal = "HOLD";
    let confidence = 60;

    if (rsi < 30 && macd > 0) {
      signal = "BUY";
      confidence = 85;
    } else if (rsi > 70 && macd < 0) {
      signal = "SELL";
      confidence = 85;
    }

    res.json({
      price,
      rsi: rsi.toFixed(2),
      macd: macd.toFixed(4),
      signal,
      confidence,
      message: "AI analysis based on RSI & MACD"
    });

  } catch (err) {
    res.status(500).json({ error: "AI calculation failed" });
  }
});

// ===== START SERVER =====
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log("Server running on port", PORT);
});
