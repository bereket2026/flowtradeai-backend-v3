const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());

app.get("/", (req, res) => {
  res.send("Backend is WORKING");
});

app.get("/ai", (req, res) => {
  res.json({
    status: "ok",
    message: "AI endpoint working"
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log("Server running on port", PORT);
});
