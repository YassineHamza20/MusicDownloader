const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();
app.use(express.json());

// CORS options to allow specific origins
const corsOptions = {
    origin: ['https://melodyaddicts.netlify.app', 'https://musicdownloader1.onrender.com'],
    optionsSuccessStatus: 200 // For legacy browser support
};

// Apply CORS with the options
app.use(cors(corsOptions));

// Serve static files from the 'public' directory
app.use('/downloads', express.static(path.join(__dirname, 'public')));

// Apply the router
app.use("/", require("./routes/music"));

// Route for the homepage
app.get('/', (req, res) => {
    res.send('Backend is running');
});

// Optional: Fallback route for handling SPA routing (if your Express serves your frontend directly)
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/dist/index.html'));
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server started on port ${PORT}`));
