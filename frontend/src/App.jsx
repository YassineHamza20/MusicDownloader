import { useState } from 'react'
import MusicDownloader from  './Music/DownloadForm.jsx'
import PlaylistDownloader from  './Music/Playlist.jsx'
import {   BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css'
import { ToastContainer } from 'react-toastify';
import NotFound from './Music/NotFound.jsx';
import ShareButton from './Music/Share.jsx';

function App() {
  
  const CombinedComponent = () => (
    <div style={{ display: 'flex' }}>
      <div style={{ flex: 1, margin: '0 10px' }}>
        <PlaylistDownloader />
      </div>
      <div style={{ flex: 1, margin: '0 10px' }}>
        <MusicDownloader />
      </div>
    </div>
  );
  const headerStyle = {
    display: 'flex',
    alignItems: 'center', // This ensures vertical alignment if your logo and text are of different heights
    marginBottom: '-40px' // Adds some space below the header
  };

  const logoStyle = {
    marginRight: '260px', // Adds some space between the logo and the title
    width: '140px' // Set the width of your logo
  };
  return (
    <>

<div style={headerStyle}>
        <img src="/music.webp" alt="Logo" style={logoStyle} />
        <h3 style={{ fontFamily: 'Roboto, sans-serif' }}>Fastest Highest Quality Music Downloader (320kbps)</h3>

      </div>
    <BrowserRouter>
    <Routes>
    
    <Route path="/" element={<CombinedComponent />} />
    <Route path="*" element={<NotFound />} />
    </Routes>
    </BrowserRouter>
   
        <ToastContainer />
    
    <h3>About me </h3> 
    <p>Hey, my name is Yassine, and I'm a computer science student
     with a passion for programming, development, and music. Combining my interests, I've created this high-quality
     music website for people like you who love to enjoy good,
     free music while studying or working
     this website aims to be a go-to destination for anyone seeking to enhance their productivity or simply unwind with some great tunes. Join me in exploring 
     the world of music and productivity on this platform, where programming meets melody in perfect harmony.
     </p>
     <p>If you like Music, please share it! <ShareButton/></p>  
     
    </>
    
  )
}

export default App
