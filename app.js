const express = require('express');
const cors = require('cors');
const app = express();
app.use(express.json());

// CORS options to allow specific origins
const corsOptions = {
    origin: ['https://melodyaddicts.netlify.app', 'https://musicdownloader1.onrender.com'],
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
app.post('/music', async (req, res) => {
  const { youtube_url } = req.body;

  // Validate the YouTube URL
  if (!youtube_url || !isValidYouTubeUrl(youtube_url)) {
    return res.status(400).json({ success: false, message: 'Please insert a valid YouTube URL' });
  }

  // Use the correct path to your script
  const pythonScriptPath = path.join(__dirname, 'scripts', 'Music.py');
  const args = [youtube_url];

  try {
    const process = spawn('python', [pythonScriptPath, ...args]);
    let output = '';
    let scriptError = '';

    process.stdout.on('data', (data) => {
      output += data.toString();
    });

    process.stderr.on('data', (data) => {
      scriptError += data.toString();
    });

    process.on('close', (code) => {
      if (code === 0) {
        res.status(200).json({ success: true, message: 'Song downloaded successfully', output });
      } else {
        console.error('Python script failed:', scriptError);
        res.status(500).json({
          success: false,
          message: 'Failed to download song.',
          error: scriptError || 'Unknown error'
        });
      }
    });
  } catch (error) {
    console.error('Server Error:', error);
    res.status(500).json({ success: false, message: 'Internal server error', error: error.message });
  }
});

// Optional: Serve static files if your backend serves the frontend directly
// app.use(express.static(path.join(__dirname, '../frontend/dist')));

// Optional: Fallback route for handling SPA routing (if your Express serves your frontend directly)
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/dist/index.html'));
});

// const PORT = process.env.PORT || 5000;
// app.listen(PORT, () => console.log(`Server started on port ${PORT}`));
