const express = require("express");
const path = require('path');
const { spawn } = require('child_process');
const router = express.Router();
const rateLimit = require('express-rate-limit');
//rate limiter 
const musicRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 20, // Limit each IP to 7 requests per windowMs
  message: 'Slow down brotha ,Too many requests from this IP, please try again after 15 minutes :)'
});

//health
 
router.get('/check',musicRateLimiter, (req, res) => {
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
      res.status(500).json({ success: false, message: 'Too many requests sorry', error: error.message });
  }
});

///validation
function isValidYouTubeUrl(url) {
  const regex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
  return regex.test(url);
}

// const isValidYouTubeUrl = (url) => {
//   const pattern = /^(https?:\/\/)?((www\.youtube\.com\/(watch\?v=|shorts\/))|(youtu\.be\/))[a-zA-Z0-9_-]{11}(\?.*)?$/;
//   return pattern.test(url);
// };
  const isValidPlaylistUrl = (url) => {
    const pattern = /^(https?:\/\/)?(www\.)?youtube\.com\/playlist\?list=[\w-]+(&[^\s]*)?$/;
    return pattern.test(url);
  };


 

// musicRateLimiter 
// In your music.js - /music route
router.post('/music', async (req, res) => {
  const { youtube_url } = req.body;

  if (!youtube_url || !isValidYouTubeUrl(youtube_url)) {
    return res.status(400).json({ 
      success: false, 
      message: 'Please insert a valid YouTube URL' 
    });
  }

  const pythonScriptPath = path.join(__dirname, '..', 'scripts', 'Music.py');
  
  // Log for debugging
  console.log(`Starting Python script: ${pythonScriptPath}`);
  console.log(`URL: ${youtube_url}`);
  
  try {
    // Use python3 on Render, python locally
    const pythonCommand = process.env.RENDER ? 'python3' : 'python';
    const process = spawn(pythonCommand, [pythonScriptPath, youtube_url]);
    
    let output = '';
    let scriptError = '';

    process.stdout.on('data', (data) => {
      output += data.toString().trim();
      console.log(`Python stdout: ${data.toString()}`);
    });

    process.stderr.on('data', (data) => {
      scriptError += data.toString();
      console.error(`Python stderr: ${data.toString()}`);
    });

    process.on('close', (code) => {
      console.log(`Python process exited with code ${code}`);
      console.log(`Output: ${output}`);
      console.log(`Error: ${scriptError}`);
      
      if (code === 0 && output) {
        // The Python script outputs just the filename
        const filename = output.trim();
        
        if (filename.endsWith('.mp3')) {
          const encodedFilename = encodeURIComponent(filename);
          const downloadUrl = `/downloads/${encodedFilename}`;
          
          res.status(200).json({ 
            success: true, 
            message: 'Song downloaded successfully', 
            downloadUrl,
            filename: filename
          });
        } else {
          // Python script returned something unexpected
          res.status(200).json({ 
            success: true, 
            message: 'Download completed', 
            note: 'Check the downloads directory',
            output: output
          });
        }
      } else {
        // Parse error message
        let errorMessage = 'Download failed';
        if (scriptError.includes('Video unavailable')) {
          errorMessage = 'Video is unavailable or restricted';
        } else if (scriptError.includes('too long')) {
          errorMessage = 'Video is too long (max 15 minutes)';
        } else if (scriptError.includes('too large')) {
          errorMessage = 'Video is too large (max 50MB)';
        } else if (scriptError) {
          errorMessage = scriptError.split('\n')[0] || 'Unknown error';
        }
        
        res.status(500).json({
          success: false,
          message: errorMessage,
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

//video
//, musicRateLimiter
router.post('/video', musicRateLimiter,async (req, res) => {
  const { youtube_url } = req.body;

  if (!youtube_url || !isValidYouTubeUrl(youtube_url)) {
      return res.status(400).json({ success: false, message: 'Please insert a valid YouTube URL' });
  }

  const pythonScriptPath = path.join(__dirname, '..', 'scripts', 'video.py');
  const args = [youtube_url];

  try {
      const process = spawn('python', [pythonScriptPath, ...args]);
      let output = '';
      let scriptError = '';

      process.stdout.on('data', (data) => {
          output += data.toString().trim();  // Capture the filename from Python script output
      });

      process.stderr.on('data', (data) => {
          scriptError += data.toString();
      });

      process.on('close', (code) => {
          if (code === 0 && output) {
              const lines = output.split('\n');
              const filename = lines[lines.length - 1].trim();
              const encodedFilename = encodeURIComponent(filename); // URL encode the output filename
              const downloadUrl = `${req.protocol}://${req.get('host')}/downloads/${encodedFilename}`;
              res.status(200).json({ success: true, message: 'Video downloaded successfully', downloadUrl });
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


router.post('/playlist', async (req, res) => {
  const { youtube_url } = req.body;

  console.log("Received URL for validation:", youtube_url);
  if (!youtube_url || !isValidPlaylistUrl(youtube_url)) {
      console.log("Validation failed for URL:", youtube_url);
      return res.status(400).json({ success: false, message: 'Please insert a valid Playlist YouTube URL' });
  }

  const pythonScriptPath = path.join(__dirname, '..', 'scripts', 'playlist.py');
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
          console.log(`Process exited with code ${code}`);
          if (code === 0) {
              const lines = output.split('\n');
              const lastLine = lines[lines.length - 1].trim();
              const downloadUrl = `${req.protocol}://${req.get('host')}/downloads/${encodeURIComponent(lastLine)}`;
              res.status(200).json({ success: true, message: 'Playlist downloaded successfully', downloadUrl });
          } else {
              console.error('Python script error:', scriptError);
              res.status(500).json({
                  success: false,
                  message: 'Failed to download playlist.',
                  error: scriptError
              });
          }
      });
  } catch (error) {
      console.error('Server Error:', error);
      res.status(500).json({ success: false, message: 'Too many requests sorry', error: error.message });
  }
});
  router.post('/videoplaylist', async (req, res) => {
    const { youtube_url } = req.body;
  
    console.log("Received URL for validation:", youtube_url);
    if (!youtube_url || !isValidPlaylistUrl(youtube_url)) {
      console.log("Validation failed for URL:", youtube_url);
      return res.status(400).json({ success: false, message: 'Please insert a valid Playlist YouTube URL' });
    }
  
    const pythonScriptPath = path.join(__dirname, '..', '../scripts/videoplaylist.py');
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
        console.log(`Process exited with code ${code}`);
        if (code === 0) {
          res.status(200).json({ success: true, message: 'Playlist downloaded successfully', output });
        } else {
          console.error('Python script error:', scriptError);
          res.status(500).json({
            success: false,
            message: 'Failed to download playlist.  ',
            error: scriptError
          });
        }
      });
    } catch (error) {
      console.error('Server Error:', error);
      res.status(500).json({ success: false, message: 'Too many requests sorry', error: error.message });
    }
  });


module.exports = router;
