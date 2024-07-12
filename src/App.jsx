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
  const [viewMP4, setViewMP4] = useState(false);

  // Function to toggle between MP3 and MP4
  const toggleMediaView = () => {
    setViewMP4(!viewMP4);
  };
  const togglePopup = () => setShowPopup(!showPopup);
  const toggleComponentView = () => setIsFlipped(!isFlipped);

  return (
    <>
      <div style={{ textAlign: 'center' }}>
      <div className="logo-container"> {/* Container for centering the logo */}
      <img src="/Melody.png" alt="MelodyAddict Logo" className="melody-logo" />
    </div>
        <h3 style={{ marginTop: '-50px', color: 'white' }}>High Quality Music Downloader  </h3>
        <h3 style={{ marginTop: '-10px', color: 'white' }}>Server down dua to pytube library error - coming back soon sorry  </h3> 
      </div>
    
      <div style={{ marginBottom: '-10px', textAlign: 'center' }}>
        <button onClick={toggleMediaView} style={{
          backgroundColor: '#081d48', color: 'white', padding: '10px 40px', border: 'none', borderRadius: '20px', cursor: 'pointer', fontSize: '17px'
        }}>
          
          {viewMP4 ? "Change To Mp3" : "Change To Mp4"}   
        </button>
      </div>
      <h2>{viewMP4 ? "Mp4" : "Mp3"} </h2> 
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            
            <div style={{ position: 'relative', height: '340px', width: '100%' }}>
              <div className={`cube ${viewMP4 ? 'is-flipped' : ''}`}>
                
                <div className="cube__face cube__face--front">
                  <MusicDownloader />   
                </div>
               
                <div className="cube__face cube__face--back">
                  <VideoDownloader />  
                </div>
                
              </div>
            </div>
          } />
          <Route path="*" element={<NotFound />} />
        </Routes>
      
      </BrowserRouter>
     
       <p className="text-emboss">If you like Music, please share it! <ShareButton /></p>
      <div style={{ marginTop: '-10px', textAlign: 'center' }}>
        <button onClick={togglePopup} style={{
          backgroundColor: '#081d48', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '20px', cursor: 'pointer', fontSize: '16px'
        }}>About Me</button>
        {showPopup && <AboutMePopup />}
      </div>
     
      <ToastContainer />
    </>
  );
}

export default App;
