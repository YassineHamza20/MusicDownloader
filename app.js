const express = require('express');
const cors = require('cors');
const path = require('path');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const fs = require('fs');
const app = express();

// Security headers
app.use(helmet());
app.use((req, res, next) => {
    res.setHeader('X-Frame-Options', 'DENY');
    next();
});

app.use((req, res, next) => {
    res.setHeader('Content-Security-Policy', "frame-ancestors 'none'");
    next();
});

app.set('trust proxy', 1);

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 20, // Limit each IP to 20 requests per `window` (here, per 15 minutes)
    message: 'Slow down brotha, Too many requests from this IP, please try again after 15 minutes :)'
});
app.use(limiter);
app.use(express.json());

// CORS options to allow specific origins
const corsOptions = {
    origin: ['https://melodyaddicts.netlify.app', 'https://songsdownloader.onrender.com'],
    optionsSuccessStatus: 200 // For legacy browser support
};

// Apply CORS with the options
app.use(cors(corsOptions));

// Serve static files from the "public" directory
app.use('/downloads', express.static(path.join(__dirname, 'public'), {
    setHeaders: (res, path) => {
        res.setHeader('Content-Disposition', 'inline');
    }
}));

// Apply the music router
app.use("/music", require("./routes/music"));

// Route for the homepage
app.get('/', (req, res) => {
    res.send('Backend is running');
});

// Endpoint to serve the downloaded files
app.get('/downloads/:filename', (req, res) => {
    const filename = req.params.filename;
    const filepath = path.join(__dirname, 'public', filename);

    console.log(`Serving file from path: ${filepath}`);  // Debugging statement

    fs.access(filepath, fs.constants.F_OK, (err) => {
        if (err) {
            res.status(404).send('File not found');
        } else {
            res.download(filepath);
        }
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server started on port ${PORT}`);
});


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


// app.get('/heartbeat', (req, res) => {
//   res.status(200).send('Server is awake!');
// });
// function keepServerAwake() {
//   const url = "https://musicdownloader1.onrender.com/heartbeat"; // Change to your actual server URL
//   fetch(url).then(response => response.text()).then(console.log).catch(console.error);

//   // Set timeout for next ping
//   setTimeout(keepServerAwake, 14 * 60 * 1000 + 50 * 1000); // 14 minutes and 50 seconds
// }

// // Start the pinging process
// keepServerAwake();
