# #!/bin/bash
# # Stop the script if any command fails
# set -e

# # Install Node packages
# echo "Installing Node.js dependencies..."
# npm install

# # Install Python packages
# echo "Installing Python dependencies..."
# pip install -r requirements.txt

# echo "Installing FFmpeg..."
# apt-get update && apt-get install -y ffmpeg
# echo "Verifying cookies file..."
# if [ ! -f "www.youtube.com_cookies" ]; then
#     echo "Error: Cookies file 'www.youtube.com_cookies' not found!"
#     exit 1
# fi
#!/bin/bash
set -e

echo "========================================"
echo "YouTube MP3 Downloader - Node.js Backend"
echo "========================================"

# Check if we're on Render
if [ -n "$RENDER" ]; then
    echo "Running on Render.com"
    # Install FFmpeg if not already installed
    if ! command -v ffmpeg &> /dev/null; then
        echo "Installing FFmpeg..."
        apt-get update && apt-get install -y ffmpeg
    fi
fi

# Install dependencies
echo "Installing Node.js dependencies..."
npm install --production

echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check for cookies file
echo "Checking for cookies file..."
if [ -f "www.youtube.com_cookies" ]; then
    echo "Found cookies file: www.youtube.com_cookies"
elif [ -f "www.youtube.com_cookies.txt" ]; then
    echo "Found cookies file: www.youtube.com_cookies.txt"
else
    echo "Warning: No cookies file found. Downloads may fail for age-restricted content."
fi

# Create necessary directories
mkdir -p downloads temp

# Start Node.js server
echo "Starting Node.js server on port $PORT..."
exec node server.js