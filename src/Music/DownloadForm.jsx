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

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                const downloadUrl = data.downloadUrl;
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.setAttribute('download', ''); // Let the browser use the filename from the URL
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                setMessage('Song downloaded successfully');
                setIsSuccess(true);
                toast.success('Song downloaded successfully');
            } else {
                setMessage(`Error: ${data.message}`);
                setIsSuccess(false);
                toast.error(`Error: ${data.message}`);
            }
        } else {
            const errorData = await response.json();
            setMessage(`Error: ${errorData.message}`);
            setIsSuccess(false);
            toast.error(`Error: ${errorData.message}`);
        }
    } catch (error) {
        console.error('Error:', error);
        setMessage('Internal server error');
        setIsSuccess(false);
        toast.error('Internal server error');
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
