import { useState } from 'react'
import MusicDownloader from  './Music/DownloadForm.jsx'
import PlaylistDownloader from  './Music/Playlist.jsx'
import {   BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css'
import { ToastContainer } from 'react-toastify';
import NotFound from './Music/NotFound.jsx';
import ShareButton from './Music/Share.jsx';
 

function AboutMePopup() {
  return (
    <div className="popup">
      
      <p >
        Hello, my name is Yassine, and I'm a computer science student
        with a passion for programming, development, and music. Combining my interests, I've created this high-quality
        music website for people like you who love to enjoy good,
        free music while studying or working. 
        
        <br></br>Feel free to reach out via  
               
        <a href="https://www.linkedin.com/in/yassine-hamza-222605215">Linkdin</a> 
        </p>  
    </div>
  );
}

function App() {
  const [showPopup, setShowPopup] = useState(false);

  const togglePopup = () => {
    setShowPopup(!showPopup);
  };
  const CombinedComponent = () => (
    <div style={{ display: 'flex' }}>
      <div style={{ flex: 1, margin: '0 5px' }}>
        <PlaylistDownloader />
      </div>
      <div style={{ flex: 1, margin: '0 5px' }}>
        <MusicDownloader />
      </div>
    </div>
  );
  const headerStyle = {
    display: 'flex',
    alignItems: 'center', // This ensures vertical alignment if your logo and text are of different heights
    marginBottom: '0px' // Adds some space below the header
  };

  const logoStyle = {
    marginRight: '260px', // Adds some space between the logo and the title
    width: '120px' // Set the width of your logo
  };
  return (
    <>

<div style={headerStyle}>
  
        <img src="/Melody.png" alt="MelodyAddictLogo" style={logoStyle} />
        <h3 style={{color:'white', fontFamily: 'Roboto, sans-serif' }}>Fastest Highest Quality Music Downloader (320kbps)</h3>

      </div>
    <BrowserRouter>
    <Routes>
    
    <Route path="/" element={<CombinedComponent />} />
    <Route path="*" element={<NotFound />} />
    </Routes>
    </BrowserRouter>
    <div>

    <p>If you like Music, please share it! <ShareButton/></p>  
      <button onClick={togglePopup} style={{
  margin: '10px',
  backgroundColor: '#081d48',  // Green background
  color: 'white',               // White text
  padding: '5px 10px',         // Padding around the text
  border: 'none',               // No border
  borderRadius: '5px',          // Rounded corners
  cursor: 'pointer',            // Pointer cursor on hover
  fontSize: '14px',             // Font size
              
      }}>About me</button>
      


      
      {showPopup && <AboutMePopup />}
    </div>
        <ToastContainer />
     
   
    
     
    </>
    
  )
}

export default App
