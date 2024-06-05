import React from 'react';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const ShareButton = () => {
  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href)
      .then(() => {
        toast.success('URL copied to clipboard!', {
          position: "bottom-center",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        });
      })
      .catch(err => {
        toast.error('Failed to copy: ' + err.message, {
          position: "bottom-center",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        });
        console.error('Failed to copy: ', err);
      });
  };

  return (
    <>
      <button onClick={handleShare} style={{
    margin: '10px',
    backgroundColor: '#081d48',  // Green background
    color: 'white',               // White text
    padding: '5px 10px',         // Padding around the text
    border: 'none',               // No border
    borderRadius: '20px',          // Rounded corners
    cursor: 'pointer',            // Pointer cursor on hover
    fontSize: '14px',             // Font size
                
  }}>
  Share
</button>
      <ToastContainer />
    </>
  );
};

export default ShareButton;
