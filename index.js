const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.send("FlowTradeAI backend is running");
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log("FlowTradeAI backend running on port", PORT);
});
