const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.json({ status: "ok", message: "FlowTradeAI backend is running" });
});

app.post("/ai", (req, res) => {
  const answers = [
    "Market shows mixed momentum.",
    "Bullish trend detected.",
    "High volatility today
