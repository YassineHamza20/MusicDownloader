const express = require('express');
const cors = require('cors');
const path = require('path');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const app = express();
app.use(helmet());
app.use((req, res, next) => {
    res.setHeader('X-Frame-Options', 'DENY');
    next();
  });
  
  // Set Content Security Policy header to prevent framing
  app.use((req, res, next) => {
    res.setHeader('Content-Security-Policy', "frame-ancestors 'none'");
    next();
  });

app.set('trust proxy', 1);

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // Limit each IP to 100 requests per `window` (here, per 15 minutes)
    message: 'Slow down brotha ,Too many requests from this IP, please try again after 15 minutes :) '
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
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server started on port ${PORT}`));
