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
        const response = await fetch('https://songs-kd5e.onrender.com/music', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ youtube_url: youtubeUrl })
        });

        if (response.ok) {
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.setAttribute('download', 'song.mp3'); // You can set the default filename here
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(downloadUrl);

            setMessage('Click The 3 Dots On the Next Page To Download');
            setIsSuccess(true);
        } else {
            const errorData = await response.json();
            setMessage(`Error: ${errorData.message}`);
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
              placeholder="Paste link here"
              onChange={(event) => setYoutubeUrl(event.target.value)}
              className="text-input"
            />
          </label>
          <button type="submit" className="download-button" disabled={loading}>Download Song</button>
        </form>
        {loading && <p className="loading">Getting File Ready...</p>}
       

        {message && !loading && <p className={`message ${isSuccess ? 'success' : 'error'}`}>{message}</p>}
      </div>
 
    
       
    </div>

    
    </>
  );
}

export default MusicDownloader;
