#!/bin/bash
# Stop the script if any command fails
set -e

# Install Node packages
echo "Installing Node.js dependencies..."
npm install

# Install Python packages
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing FFmpeg..."
apt-get update && apt-get install -y ffmpeg
echo "Verifying cookies file..."
if [ ! -f "www.youtube.com_cookies" ]; then
    echo "Error: Cookies file 'www.youtube.com_cookies' not found!"
    exit 1
fi