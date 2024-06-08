import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MusicDownloader from './Music/DownloadForm.jsx';
import PlaylistDownloader from './Music/Playlist.jsx';
import PlaylistDownloaderVideo from './Music/Playlistvideo.jsx';
import VideoDownloader from './Music/DownloadFormvideo.jsx';
import NotFound from './Music/NotFound.jsx';
import ShareButton from './Music/Share.jsx';
import AboutMePopup from './Music/AboutMePopup.jsx';
import { ToastContainer } from 'react-toastify';
import './App.css';

function App() {
  const [showPopup, setShowPopup] = useState(false);
  const [isFlipped, setIsFlipped] = useState(false);

  const togglePopup = () => setShowPopup(!showPopup);
  const toggleComponentView = () => setIsFlipped(!isFlipped);

  return (
    <>
      <div style={{ textAlign: 'center' }}>
      <div className="logo-container"> {/* Container for centering the logo */}
      <img src="/Melody.png" alt="MelodyAddict Logo" className="melody-logo" />
    </div>
        <h3 style={{ marginTop: '-80px', color: 'white' }}>Fastest High-Quality Music Downloader (320kbps)</h3>
      </div>
      <div style={{ marginBottom: '30px', textAlign: 'center' }}>
        <button onClick={toggleComponentView} style={{
          backgroundColor: '#081d48', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '20px', cursor: 'pointer', fontSize: '16px'
        }}>MP4/MP3</button>
      </div>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            <div style={{ position: 'relative', height: '400px', width: '91%' }}>
              <div className={`cube ${isFlipped ? 'is-flipped' : ''}`}>
                <div className="cube__face cube__face--front">
                  <PlaylistDownloader />
                  <MusicDownloader />
                </div>
                <div className="cube__face cube__face--back">
                  <PlaylistDownloaderVideo />
                  <VideoDownloader />
                </div>
              </div>
            </div>
          } />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
      <div style={{ marginTop: '35px', textAlign: 'center' }}>
        <button onClick={togglePopup} style={{
          backgroundColor: '#081d48', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '20px', cursor: 'pointer', fontSize: '16px'
        }}>About Me</button>
        {showPopup && <AboutMePopup />}
      </div>
      <p className="text-emboss">If you like Music, please share it! <ShareButton /></p>
      <ToastContainer />
    </>
  );
}

export default App;
