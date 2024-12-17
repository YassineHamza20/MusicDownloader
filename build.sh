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