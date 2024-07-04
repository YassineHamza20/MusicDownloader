import React, { useState } from 'react';
import './Songs.css'; 
 
import 'react-toastify/dist/ReactToastify.css';


function AboutMePopup() {
  return (
    <div className="popup">
      <p>
        Hello, my name is Yassine, and I'm a computer science student
        with a passion for programming, development, and music. Combining my interests, I've created this high-quality
        music website for people like you who love to enjoy good 
        music while studying or working.
        <br></br> <div>
      Feel free to reach out via 
      <a href="https://www.linkedin.com/in/yassine-hamza17/" target="_blank" rel="noopener noreferrer">
        : LinkedIn
      </a>
    </div>
       
      
      </p>  
    </div>
  );
}

export default AboutMePopup;
