import React from 'react';

const NotFound = () => {
  return (
    <div style={styles.container}>
      <h1 style={styles.header}>404</h1>
      <p style={styles.text}>Page Not Found</p>
      <p style={styles.text}>The page you are looking for does not exist. You may have mistyped the address or the page may have moved.</p>
    </div>
  );
};

// Styling for the component
const styles = {
  container: {
    textAlign: 'center',
    marginTop: '50px',
  },
  header: {
    fontSize: '72px',
    fontWeight: 'bold',
  },
  text: {
    fontSize: '24px'
  }
};

export default NotFound;
