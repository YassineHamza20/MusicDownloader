const express = require('express');
const cors = require('cors');
const path = require('path');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const app = express();

app.use(helmet());
app.set('trust proxy', 1);

// Remove or adjust rate limit - THIS IS CAUSING YOUR ERROR
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Increased from 20 to 100
    message: {
        success: false,
        message: 'Slow down brotha, Too many requests from this IP, please try again after 15 minutes :)'
    }
});

app.use(express.json());

// CORS options
const corsOptions = {
    origin: ['https://melodyaddicts.netlify.app', 'https://songs-kd5e.onrender.com', 'http://localhost:3000'],
    optionsSuccessStatus: 200
};

app.use(cors(corsOptions));

// Static files - FIXED
app.use('/downloads', express.static(path.join(__dirname, 'public'), {
    setHeaders: (res, filePath) => {
        const fileName = path.basename(filePath);
        res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
    }
}));

// Health check endpoint - ADD THIS
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        service: 'YouTube MP3 Downloader'
    });
});

// Root endpoint
app.get('/', (req, res) => {
    res.json({
        message: 'YouTube MP3 Downloader API',
        endpoints: {
            health: 'GET /health',
            info: 'POST /api/info',
            download: 'POST /api/download',
            status: 'GET /api/status/:taskId'
        }
    });
});

// Apply routes with NO LIMITER on health check
app.use("/api", limiter, require("./routes/music"));

const PORT = process.env.PORT || 10000; // Changed to 10000 for Render
app.listen(PORT, () => console.log(`Server started on port ${PORT}`));