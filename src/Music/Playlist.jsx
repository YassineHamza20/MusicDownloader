import React, { useState } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './PlaylistDownloader.css';  // Import CSS file for styles

function PlaylistDownloader() {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(true);  // New state to track response status

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await fetch('https://musicdownloader1.onrender.com/playlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ youtube_url: youtubeUrl })
      });

      const data = await response.json();
      if (response.ok) {
        setMessage(data.message);
        setIsSuccess(true);  // Update success status
        toast.success('Playlist downloaded successfully');
      } else {
        setMessage(`Error: ${data.message}`);
        setIsSuccess(false);  // Update success status on error
      }
    } catch (error) {
      console.error('Error:', error);
      setMessage('Internal server error');
      setIsSuccess(false);  // Update success status on exception
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
    <div className="music-downloader-container">
      <h1>Download A Playlist as Mp3 </h1>
      <form onSubmit={handleSubmit} className="downloader-form">
        <label>
          <span>Enter YouTube Playlist URL:</span>
          <input 
            type="text" 
            value={youtubeUrl} 
            onChange={(event) => setYoutubeUrl(event.target.value)}
            placeholder="Paste YouTube playlist link here"
          />
        </label>
        <button type="submit"   className="download-button"disabled={loading}>Download Playlist</button>
      </form>
      {loading && <p className="loading">Downloading...</p>}
   
      {message && !loading && <p className={`message ${isSuccess ? 'success' : 'error'}`}>{message}</p>}
    </div>
  
  
    </>);
}

export default PlaylistDownloader;
