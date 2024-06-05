import React, { useState } from 'react';
import './combinedComponentStyles.css';

// Import external components
import MusicDownloaderForm from './Music/DownloadForm.jsx';
import PlaylistDownloaderList from './Music/Playlist.jsx';
import PlaylistDownloaderVideoComponent from './Music/Playlistvideo.jsx';
import VideoDownloaderForm from './Music/DownloadFormvideo.jsx';

const CombinedComponent = () => {
  const [isFlipped, setIsFlipped] = useState(false);

  const toggleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  return (
    <div className="cube-container">
      <div className={`cube ${isFlipped ? 'show-back' : ''}`}>
        <div className="cube-face front">
          <PlaylistDownloaderList />
          <MusicDownloaderForm />
        </div>
        <div className="cube-face back">
          <PlaylistDownloaderVideoComponent />
          <VideoDownloaderForm />
        </div>
      </div>
      <button className="cube-button" onClick={toggleFlip}>
        Toggle Components
      </button>
    </div>
  );
};

export default CombinedComponent;
