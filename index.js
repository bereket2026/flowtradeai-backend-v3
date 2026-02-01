const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

app.get("/", function (req, res) {
  res.json({
    status: "ok",
    message: "FlowTradeAI backend is running"
  });
});

app.post("/ai", function (req, res) {
  const answers = [
    "Market shows mixed momentum.",
    "Bullish trend detected.",
    "High volatility today.",
    "Sideways market conditions.",
    "Possible trend reversal."
  ];

  const reply = answers[Math.floor(Math.random() * answers.length)];
  res.json({ ai: reply });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, function () {
  console.log("FlowTradeAI backend running on port " + PORT);
});
