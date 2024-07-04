const express = require("express");
const path = require('path');
const { spawn } = require('child_process');
const router = express.Router();
const rateLimit = require('express-rate-limit');
const app = express();


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


app.use(express.json());
app.use('/downloads', express.static(path.join(__dirname, 'public', 'downloads')));

app.post('/playlist', (req, res) => {
  const { youtube_url } = req.body;

  if (!youtube_url) {
      return res.status(400).json({ success: false, message: 'Please insert a valid YouTube URL' });
  }

  const pythonScriptPath = path.join(__dirname, 'scripts', 'playlist.py');
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
              res.status(200).json({ success: true, message: 'Playlist downloaded successfully', downloadUrl });
          } else {
              console.error('Python script failed with code:', code, 'and error:', scriptError);
              res.status(500).json({
                  success: false,
                  message: 'Failed to download playlist',
                  error: scriptError || 'Unknown error detected, please check logs'
              });
          }
      });
  } catch (error) {
      console.error('Error spawning Python script:', error);
      res.status(500).json({ success: false, message: 'Failed to download playlist', error: error.message });
  }
});
app.get('/downloads/:filename', (req, res) => {
  const filename = req.params.filename;
  const filepath = path.join(__dirname, 'public', 'downloads', filename);
  res.download(filepath);
});



//rate limiter 

  

const musicRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 20, // Limit each IP to 7 requests per windowMs
  message: 'Slow down brotha ,Too many requests from this IP, please try again after 15 minutes :)'
});

 

//health
//,musicRateLimiter
router.get('/check', (req, res) => {
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

 
//music
//, musicRateLimiter
router.post('/music', async (req, res) => {
  const { youtube_url } = req.body;

  if (!youtube_url || !isValidYouTubeUrl(youtube_url)) {
      return res.status(400).json({ success: false, message: 'Please insert a valid YouTube URL' });
  }

  const pythonScriptPath = path.join(__dirname, '..', 'scripts', 'Music.py');
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
              res.status(200).json({ success: true, message: 'Song downloaded successfully', downloadUrl });
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

//video
//, musicRateLimiter
router.post('/video', async (req, res) => {
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
