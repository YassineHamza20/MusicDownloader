const express = require('express');
const cors = require('cors');
const path = require('path');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const { spawn } = require('child_process');
const app = express();

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

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 20, // Limit each IP to 20 requests per `window` (here, per 15 minutes)
    message: 'Slow down, too many requests from this IP, please try again after 15 minutes.'
});
app.use(limiter);
app.use(express.json());
// Utility function to sanitize filename
function sanitizeFilename(filename) {
  return filename.replace(/[<>:"/\\|?*]+/g, '_');
}

// Validate YouTube URL function
function isValidYouTubeUrl(url) {
  const regex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
  return regex.test(url);
}

const corsOptions = {
    origin: ['https://melodyaddicts.netlify.app', 'https://songs-kd5e.onrender.com'],
    optionsSuccessStatus: 200 // For legacy browser support
};

app.use(cors(corsOptions));

app.post('/music', async (req, res) => {
    const { youtube_url } = req.body;

    if (!youtube_url || !isValidYouTubeUrl(youtube_url)) {
        return res.status(400).json({ success: false, message: 'Please insert a valid YouTube URL' });
    }

    const pythonScriptPath = path.join(__dirname, 'scripts', 'Music.py');
    const args = [youtube_url];

    try {
        const process = spawn('python', [pythonScriptPath, ...args], { stdio: ['pipe', 'pipe', 'pipe'] });
        let output = Buffer.from('');
        let scriptError = '';

        process.stdout.on('data', (data) => {
            output = Buffer.concat([output, data]);
        });

        process.stderr.on('data', (data) => {
            scriptError += data.toString();
        });

        process.on('close', (code) => {
            if (code === 0 && output.length > 0) {
                res.setHeader('Content-Type', 'audio/mpeg');
                res.setHeader('Content-Disposition', `attachment; filename="${sanitizeFilename(youtube_url)}.mp3"`);
                res.send(output);
            } else {
                console.error('Python script failed with code:', code, 'and error:', scriptError);
                res.status(500).json({
                    success: false,
                    message: 'Too many requests sorry',
                    error: scriptError || 'Unknown error detected, please check logs'
                });
            }
        });
    } catch (error) {
        console.error('Error spawning Python script:', error);
        res.status(500).json({ success: false, message: 'Too many requests sorry', error: error.message });
    }
});

app.get('/', (req, res) => {
    res.send('Backend is running');
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server started on port ${PORT}`));

