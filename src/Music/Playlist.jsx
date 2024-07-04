import React, { useState } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './PlaylistDownloader.css';  // Import CSS file for styles

function PlaylistDownloader() {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(true);  // New state to track response status

  


//   const handleSubmit = async (event) => {
//     event.preventDefault();
//     setLoading(true);

//     try {
//         const response = await fetch('https://musicdownloader1.onrender.com/playlist', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ youtube_url: youtubeUrl })
//         });

//         if (response.ok) {
//             const data = await response.json();
//             if (data.success) {
//                 const downloadUrl = data.downloadUrl;
//                 const link = document.createElement('a');
//                 link.href = downloadUrl;
//                 link.setAttribute('download', ''); // Let the browser use the filename from the URL
//                 document.body.appendChild(link);
//                 link.click();
//                 document.body.removeChild(link);

//                 setMessage('Playlist downloaded successfully');
//                 setIsSuccess(true);
//                 toast.success('Playlist downloaded successfully');
//             } else {
//                 setMessage(`Error: ${data.message}`);
//                 setIsSuccess(false);
//                 toast.error(`Error: ${data.message}`);
//             }
//         } else {
//             const errorData = await response.json();
//             setMessage(`Error: ${errorData.message}`);
//             setIsSuccess(false);
//             toast.error(`Error: ${errorData.message}`);
//         }
//     } catch (error) {
//         console.error('Error:', error);
//         setMessage('Internal server error');
//         setIsSuccess(false);
//         toast.error('Internal server error');
//     } finally {
//         setLoading(false);
//     }
// }; 

const handleSubmit = async (event) => {
  event.preventDefault();
  setLoading(true);

  try {
      const response = await fetch('https://musicdownloader1.onrender.com/playlist', {
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
              link.setAttribute('download', 'playlist.zip'); // Set the filename for the download
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);

              setMessage('Playlist downloaded successfully');
              setIsSuccess(true);
              toast.success('Playlist downloaded successfully');
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
