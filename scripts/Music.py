import os
import sys
import requests
import subprocess
from flask import Flask, request, send_file, jsonify
from pathlib import Path
from yt_dlp import YoutubeDL
import re
import traceback
import socket

app = Flask(__name__)

# Directory for downloads
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Path to FFmpeg
ffmpeg_path = 'ffmpeg'
COOKIES_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")
if os.path.isfile(COOKIES_FILE):
    print(f"Cookies file found: {COOKIES_FILE}")
else:
    print("Error: 'cookies.txt' not found. Ensure the file exists in the script directory.")
    raise FileNotFoundError("Error: 'cookies.txt' not found. Ensure the file exists in the script directory.")
# Sanitize filename
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]+', '_', filename)
if not os.path.isfile(COOKIES_FILE):
    raise FileNotFoundError("Error: 'cookies.txt' not found. Ensure the file exists in the script directory.")
# Download YouTube video as MP3
def download_video_as_mp3(youtube_url, output_folder):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(Path(output_folder) / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = sanitize_filename(info['title'])
            mp3_path = os.path.join(output_folder, f"{title}.mp3")
            return mp3_path
    except Exception as e:
        print(traceback.format_exc())
        return None

# Flask route
@app.route('/music', methods=['POST'])
def download():
    try:
        data = request.get_json()
        youtube_url = data.get('youtube_url')
        if not youtube_url:
            return jsonify({"success": False, "message": "YouTube URL not provided"}), 400

        mp3_path = download_video_as_mp3(youtube_url, OUTPUT_FOLDER)
        if not mp3_path or not os.path.isfile(mp3_path):
            return jsonify({"success": False, "message": "Failed to process video"}), 500

        return send_file(mp3_path, as_attachment=True)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"success": False, "message": "Server error occurred"}), 500

# Function to get a dynamic free port
def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Bind to port 0 to get a free port
        return s.getsockname()[1]  # Return the assigned port

if __name__ == "__main__":
    if len(sys.argv) == 2:
        youtube_url = sys.argv[1]
        output_folder = Path.home() / 'Downloads'
        download_video_as_mp3(youtube_url, output_folder)
    else:
        # Run Flask with dynamic port
        port = get_free_port()
        print(f"Running Flask server on dynamic port {port}")
        app.run(debug=True, host='0.0.0.0', port=port)
