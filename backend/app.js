const express = require('express');
const cors = require('cors');
const app = express();
app.use(express.json())
app.use(cors({
  origin: 'https://melodyaddict.onrender.com' // Allow requests from localhost:3000
}));

app.use("/", require("./routes/music"));


// app.use(express.static(path.join(__dirname, '../frontend/dist')));

// Handles any requests that don't match the ones above
// app.get('*', (req, res) =>{
//     res.sendFile(path.join(__dirname+'../frontend/dist/index.html'));
// });

const PORT = process.env.PORT || 5000;
const server = app.listen(PORT, console.log(`Server started on port ${PORT}`));
  
module.exports = app;
