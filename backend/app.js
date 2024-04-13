const express = require('express');
const cors = require('cors');
const app = express();
app.use(express.json())
app.use(cors({
  origin: 'http://localhost:5173' // Allow requests from localhost:3000
}));
app.use("/", require("./routes/music"));
const PORT = process.env.PORT || 5000;
const server = app.listen(PORT, console.log(`Server started on port ${PORT} server is running`));
  
module.exports = app;
