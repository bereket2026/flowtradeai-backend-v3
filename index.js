const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();
app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.send("FlowTradeAI backend running");
});

app.post("/ai", async (req, res) => {
  try {
    const response = await axios.get(
      "https://api.binance.com/api/v3/ticker/price",
      { params: { symbol: "BTCUSDT" } }
    );

    const price = parseFloat(response.data.price);

    res.json({
      price,
      signal: "HOLD",
      confidence: 75,
      message: "Backend + AI endpoint working"
    });

  } catch (err) {
    res.status(500).json({
      error: "Failed to fetch price"
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log("Server running on", PORT);
});
