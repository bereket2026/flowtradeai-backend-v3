const express = require("express");
const cors = require("cors");

const app = express();

// middleware
app.use(cors());
app.use(express.json());

// ===== BASIC ROUTES (KEEP SERVER ALIVE) =====
app.get("/", (req, res) => {
  res.status(200).send("✅ FlowTradeAI backend is running");
});

app.get("/health", (req, res) => {
  res.json({ status: "ok", time: new Date().toISOString() });
});

// ===== DEMO AI ENDPOINT =====
app.post("/ai", (req, res) => {
  const signals = ["BUY", "SELL", "HOLD"];
  const signal = signals[Math.floor(Math.random() * signals.length)];

  res.json({
    price: (30000 + Math.random() * 2000).toFixed(2),
    signal,
    confidence: Math.floor(60 + Math.random() * 30),
    message: "AI analysis completed successfully"
  });
});

// ===== START SERVER =====
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log("🚀 FlowTradeAI backend running on port", PORT);
});

// ===== PREVENT EARLY EXIT (IMPORTANT FOR RENDER) =====
setInterval(() => {
  // keeps the process alive
}, 1000 * 60);
