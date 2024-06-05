const express = require('express');
const cors = require('cors');
const app = express();
app.use(express.json());

// CORS options to allow specific origins
const corsOptions = {
    origin: ['https://melodyaddicts.netlify.app', 'https://musicdownloader1.onrender.com'], // Allow requests from both front-end and another specified domain
    optionsSuccessStatus: 200 // For legacy browser support
};

// Apply CORS with the options
app.use(cors(corsOptions));

// Route for the homepage
app.get('/', (req, res) => {
    res.send('Backend is running');
});

// Apply CORS specifically to the "/music" routes if needed separately
app.use("/", cors(corsOptions), require("./routes/music"));

// Optional: Serve static files if your backend serves the frontend directly
// app.use(express.static(path.join(__dirname, '../frontend/dist')));

// Optional: Fallback route for handling SPA routing (if your Express serves your frontend directly)
// app.get('*', (req, res) => {
//     res.sendFile(path.join(__dirname, '../frontend/dist/index.html'));
// });
// Place this after all your API routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/build/index.html'));
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server started on port ${PORT}`));
