#!/bin/bash
# Stop the script if any command fails
set -e

# Install Node packages
echo "Installing Node.js dependencies..."
npm install

# Install Python packages
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Any other build steps can be added here
 