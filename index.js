const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

let lastBTCPrice = null;
let position = null;
let entryPrice = null;

app.get("/", (req, res) => {
  res.json({
    status: "ok",
    message: "FlowTradeAI backend with paper trading is running"
  });
});

app.post("/ai", async (req, res) => {
  try {
    const response = await fetch(
      "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    );
    const data = await response.json();
    const price = data.bitcoin.usd;

    let signal = "HOLD";
    let confidence = 50;
    let explanation = "Market is stable.";

    if (lastBTCPrice !== null) {
      if (price > lastBTCPrice) {
        signal = "BUY";
        confidence = 70;
        explanation = "BTC price increased since last check.";
      } else if (price < lastBTCPrice) {
        signal = "SELL";
        confidence = 70;
        explanation = "BTC price decreased since last check.";
      }
    }

    // Paper trading logic
    if (signal === "BUY" && position !== "LONG") {
      position = "LONG";
      entryPrice = price;
    } else if (signal === "SELL" && position === "LONG") {
      position = null;
      entryPrice = null;
    }

    let pnl = null;
    if (position === "LONG" && entryPrice) {
      pnl = (((price - entryPrice) / entryPrice) * 100).toFixed(2);
    }

    lastBTCPrice = price;

    res.json({
      signal,
      confidence,
      price,
      position: position ? position : "NONE",
      entryPrice,
      pnl,
      explanation
    });
  } catch {
    res.json({
      signal: "HOLD",
      confidence: 40,
      explanation: "Market data unavailable."
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log("FlowTradeAI paper trading backend running on port " + PORT);
});
