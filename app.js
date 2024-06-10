const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();
app.use(express.json());

// CORS options to allow specific origins
const corsOptions = {
    origin: ['https://melodyaddicts.netlify.app', 'https://songsdownloader.onrender.com'],
    optionsSuccessStatus: 200 // For legacy browser support
};

// Apply CORS with the options
app.use(cors(corsOptions));

// Serve static files from the 'public' directory
// app.use('/downloads', express.static(path.join(__dirname, 'public'), {
//     setHeaders: (res, path) => {
//         res.setHeader('Content-Disposition', `attachment; filename="${path.split('/').pop()}"`);
//     }
// }));
// app.use('/downloads', express.static(path.join(__dirname, 'public'), {
//   setHeaders: (res, path) => {
//       res.setHeader('Content-Disposition', 'attachment');
//   }
// }));
// app.use('/downloads', express.static(path.join(__dirname, 'public')));

app.use('/downloads', express.static(path.join(__dirname, 'public'), {
  setHeaders: (res, path) => {
      res.setHeader('Content-Disposition', 'inline');
  }
}));
// Apply the router
app.use("/", require("./routes/music"));

// Route for the homepage
app.get('/', (req, res) => {
    res.send('Backend is running');
});

// app.get('/heartbeat', (req, res) => {
//   res.status(200).send('Server is awake!');
// });
// function keepServerAwake() {
//   const url = "https://musicdownloader1.onrender.com/heartbeat"; // Change to your actual server URL
//   fetch(url).then(response => response.text()).then(console.log).catch(console.error);

//   // Set timeout for next ping
//   setTimeout(keepServerAwake, 14 * 60 * 1000 + 50 * 1000); // 14 minutes and 50 seconds
// }
app.get('/check', (req, res) => {
    const pythonScriptPath = path.join(__dirname, '..', 'scripts', 'check_environment.py');
    try {
        const process = spawn('python', [pythonScriptPath]);
        let output = '';
        let scriptError = '';

        process.stdout.on('data', (data) => {
            output += data.toString().trim();
        });

        process.stderr.on('data', (data) => {
            scriptError += data.toString();
        });

        process.on('close', (code) => {
            if (code === 0) {
                res.status(200).json({ success: true, message: 'Environment check complete', output });
            } else {
                console.error('Python script failed with code:', code, 'and error:', scriptError);
                res.status(500).json({
                    success: false,
                    message: 'Failed to check environment.',
                    error: scriptError || 'Unknown error detected, please check logs'
                });
            }
        });
    } catch (error) {
        console.error('Error spawning Python script:', error);
        res.status(500).json({ success: false, message: 'Internal server error', error: error.message });
    }
});
// // Start the pinging process
// keepServerAwake();
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server started on port ${PORT}`));
