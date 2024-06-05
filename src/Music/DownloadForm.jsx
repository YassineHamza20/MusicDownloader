import React, { useState } from 'react';
import './Songs.css'; // Import updated CSS file for styling
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';


function MusicDownloader() {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(true);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('https://musicdownloader1.onrender.com/music', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ youtube_url: youtubeUrl })
      });

      const data = await response.json();
      if (response.ok) {
        setMessage(data.message);
        setIsSuccess(true);
        toast.success('Song downloaded successfully');
      } else {
        setMessage(`Error: ${data.message}`);
        setIsSuccess(false);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessage('Internal server error');
      setIsSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
    <div className="app-container"> {/* New container for flex display */}
      <div className="music-downloader-container">
       
        <h1>Download One Song As Mp3</h1>
        <form onSubmit={handleSubmit} className="downloader-form">
          <label className="input-label">
            <span>Enter YouTube video URL:</span>
            <input 
              type="text" 
              value={youtubeUrl} 
              placeholder="Paste YouTube video link here"
              onChange={(event) => setYoutubeUrl(event.target.value)}
              className="text-input"
            />
          </label>
          <button type="submit" className="download-button" disabled={loading}>Download Song</button>
        </form>
        {loading && <p className="loading">Downloading...</p>}
       

        {message && !loading && <p className={`message ${isSuccess ? 'success' : 'error'}`}>{message}</p>}
      </div>
 
    
       
    </div>

    
    </>
  );
}

export default MusicDownloader;
