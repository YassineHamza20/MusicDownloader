const express = require("express");
const path = require('path');
const { spawn } = require('child_process');
const router = express.Router();
const rateLimit = require('express-rate-limit');
const fs = require('fs').promises;

// Rate limiter - REMOVE OR INCREASE THIS
const musicRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Increased from 20 to 100
  message: {
    success: false,
    message: 'Slow down brotha, please try again after 15 minutes :)'
  }
});

// Health check
router.get('/check', (req, res) => {
  res.json({
    success: true,
    message: 'Server is running',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// YouTube URL validation
function isValidYouTubeUrl(url) {
  if (!url) return false;
  const regex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
  return regex.test(url);
}

function isValidPlaylistUrl(url) {
  const pattern = /^(https?:\/\/)?(www\.)?youtube\.com\/playlist\?list=[\w-]+(&[^\s]*)?$/;
  return pattern.test(url);
}

// Create downloads directory
const PUBLIC_DIR = path.join(__dirname, '..', 'public');
(async () => {
  try {
    await fs.mkdir(PUBLIC_DIR, { recursive: true });
    console.log(`Public directory ready: ${PUBLIC_DIR}`);
  } catch (error) {
    console.error('Error creating public directory:', error);
  }
})();

// Single MP3 download - FIXED
router.post('/music', async (req, res) => {
  const { youtube_url } = req.body;

  if (!youtube_url || !isValidYouTubeUrl(youtube_url)) {
    return res.status(400).json({ 
      success: false, 
      message: 'Please insert a valid YouTube URL' 
    });
  }

  const pythonScriptPath = path.join(__dirname, '..', 'scripts', 'Music.py');
  
  // Check if script exists
  try {
    await fs.access(pythonScriptPath);
  } catch {
    return res.status(500).json({
      success: false,
      message: 'Server configuration error',
      error: 'Python script not found'
    });
  }

  console.log(`Starting MP3 download for: ${youtube_url}`);
  
  try {
    const process = spawn('python3', [pythonScriptPath, youtube_url]);
    let output = '';
    let scriptError = '';

    process.stdout.on('data', (data) => {
      output += data.toString();
      console.log(`Python stdout: ${data.toString()}`);
    });

    process.stderr.on('data', (data) => {
      scriptError += data.toString();
      console.error(`Python stderr: ${data.toString()}`);
    });

    process.on('close', (code) => {
      console.log(`Python process exited with code ${code}`);
      
      if (code === 0 && output) {
        // Parse output to find filename
        const lines = output.split('\n');
        let filename = null;
        
        // Look for filename in output
        for (const line of lines.reverse()) {
          if (line.includes('.mp3') && line.includes('[SUCCESS]')) {
            // Extract filename from line like: "[SUCCESS] Download completed: song.mp3"
            const match = line.match(/Download completed:\s*(.+\.mp3)/);
            if (match) {
              filename = match[1].trim();
              break;
            }
          }
        }
        
        if (filename) {
          const encodedFilename = encodeURIComponent(filename);
          const downloadUrl = `/downloads/${encodedFilename}`;
          
          res.status(200).json({ 
            success: true, 
            message: 'Song downloaded successfully', 
            downloadUrl,
            filename: filename
          });
        } else {
          // Fallback: use last non-empty line
          const lastLine = lines.filter(line => line.trim()).pop();
          if (lastLine && lastLine.includes('.mp3')) {
            const encodedFilename = encodeURIComponent(lastLine.trim());
            const downloadUrl = `/downloads/${encodedFilename}`;
            
            res.status(200).json({ 
              success: true, 
              message: 'Song downloaded successfully', 
              downloadUrl,
              filename: lastLine.trim()
            });
          } else {
            res.status(200).json({ 
              success: true, 
              message: 'Download completed, check /downloads directory',
              output: output
            });
          }
        }
      } else {
        console.error('Python script failed:', scriptError);
        res.status(500).json({
          success: false,
          message: 'Download failed',
          error: scriptError || 'Unknown error',
          code: code
        });
      }
    });
    
  } catch (error) {
    console.error('Error spawning Python script:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Server error', 
      error: error.message 
    });
  }
});

// Video download - FIXED
router.post('/video', async (req, res) => {
  const { youtube_url } = req.body;

  if (!youtube_url || !isValidYouTubeUrl(youtube_url)) {
    return res.status(400).json({ 
      success: false, 
      message: 'Please insert a valid YouTube URL' 
    });
  }

  console.log(`Starting video download for: ${youtube_url}`);
  
  // For now, return a message since video.py might not exist
  res.status(501).json({
    success: false,
    message: 'Video download is temporarily disabled',
    note: 'MP3 download is available at /api/music'
  });
});

// Playlist MP3 download - FIXED
router.post('/playlist', async (req, res) => {
  const { youtube_url } = req.body;

  console.log("Received playlist URL:", youtube_url);
  
  if (!youtube_url || !isValidPlaylistUrl(youtube_url)) {
    return res.status(400).json({ 
      success: false, 
      message: 'Please insert a valid YouTube playlist URL' 
    });
  }

  const pythonScriptPath = path.join(__dirname, '..', 'scripts', 'playlist.py');
  
  // Check if script exists
  try {
    await fs.access(pythonScriptPath);
  } catch {
    return res.status(500).json({
      success: false,
      message: 'Playlist download is not configured',
      error: 'Python script not found'
    });
  }

  console.log(`Starting playlist download for: ${youtube_url}`);
  
  try {
    const process = spawn('python3', [pythonScriptPath, youtube_url]);
    let output = '';
    let scriptError = '';

    process.stdout.on('data', (data) => {
      output += data.toString();
      console.log(`Playlist stdout: ${data.toString()}`);
    });

    process.stderr.on('data', (data) => {
      scriptError += data.toString();
      console.error(`Playlist stderr: ${data.toString()}`);
    });

    process.on('close', (code) => {
      console.log(`Playlist process exited with code ${code}`);
      
      if (code === 0) {
        // Playlist download creates a folder, not a single file
        const lines = output.split('\n');
        let folderName = null;
        
        // Look for folder name in output
        for (const line of lines.reverse()) {
          if (line.includes('Output folder:') || line.includes('Playlist:')) {
            const match = line.match(/Output folder:\s*(.+)/) || 
                         line.match(/Playlist:\s*(.+)/);
            if (match) {
              folderName = match[1].trim();
              break;
            }
          }
        }
        
        if (folderName) {
          res.status(200).json({ 
            success: true, 
            message: 'Playlist downloaded successfully', 
            folder: folderName,
            note: 'Files are available in the downloads directory'
          });
        } else {
          res.status(200).json({ 
            success: true, 
            message: 'Playlist download completed',
            output: output
          });
        }
      } else {
        console.error('Playlist script failed:', scriptError);
        res.status(500).json({
          success: false,
          message: 'Playlist download failed',
          error: scriptError || 'Unknown error'
        });
      }
    });
    
  } catch (error) {
    console.error('Error spawning playlist script:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Server error', 
      error: error.message 
    });
  }
});

// Video playlist - DISABLED for now
router.post('/videoplaylist', async (req, res) => {
  res.status(501).json({
    success: false,
    message: 'Video playlist download is temporarily unavailable',
    note: 'Audio playlist download is available at /api/playlist'
  });
});

// New endpoints for modern API
router.post('/info', async (req, res) => {
  const { url } = req.body;
  
  if (!url || !isValidYouTubeUrl(url)) {
    return res.status(400).json({ 
      success: false, 
      message: 'Please insert a valid YouTube URL' 
    });
  }
  
  // Create a simple Python script to get video info
  const pythonScript = `
import sys
import json
import yt_dlp

url = sys.argv[1]

ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        result = {
            'title': info.get('title', 'Unknown'),
            'duration': info.get('duration', 0),
            'uploader': info.get('uploader', 'Unknown'),
            'thumbnail': info.get('thumbnail', ''),
            'is_live': info.get('is_live', False)
        }
        print(json.dumps(result))
except Exception as e:
    print(json.dumps({'error': str(e)}))
    sys.exit(1)
`;
  
  try {
    // Write temporary Python script
    const tempScriptPath = path.join(__dirname, '..', 'temp_info.py');
    await fs.writeFile(tempScriptPath, pythonScript);
    
    const process = spawn('python3', [tempScriptPath, url]);
    let output = '';
    let scriptError = '';
    
    process.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    process.stderr.on('data', (data) => {
      scriptError += data.toString();
    });
    
    process.on('close', async (code) => {
      // Clean up temp file
      try {
        await fs.unlink(tempScriptPath);
      } catch (e) {
        // Ignore cleanup errors
      }
      
      if (code === 0) {
        try {
          const info = JSON.parse(output);
          res.json({
            success: true,
            ...info
          });
        } catch (e) {
          res.status(500).json({
            success: false,
            error: 'Failed to parse video info',
            raw: output
          });
        }
      } else {
        res.status(500).json({
          success: false,
          error: scriptError || 'Failed to get video info'
        });
      }
    });
    
  } catch (error) {
    console.error('Error getting video info:', error);
    res.status(500).json({
      success: false,
      error: 'Server error',
      message: error.message
    });
  }
});

module.exports = router;