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

 
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server started on port ${PORT}`));
