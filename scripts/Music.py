import os
import requests
import subprocess
from flask import Flask, request, send_file, jsonify
from pathlib import Path
from yt_dlp import YoutubeDL
import re
import traceback

# Create a Flask app
app = Flask(__name__)

# Directory for downloads
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Path to FFmpeg
ffmpeg_path = 'ffmpeg'

# Sanitize filename
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]+', '_', filename)

# Download YouTube video as MP3
def download_video_as_mp3(youtube_url):
    try:
        # Set yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(Path(OUTPUT_FOLDER) / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        }

        # Download video
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = sanitize_filename(info['title'])
            mp3_path = os.path.join(OUTPUT_FOLDER, f"{title}.mp3")
            return mp3_path
    except Exception as e:
        print(traceback.format_exc())
        return None

# Flask route to handle POST requests
@app.route('/download', methods=['POST'])
def download():
    try:
        # Parse JSON input
        data = request.get_json()
        youtube_url = data.get('youtube_url')

        if not youtube_url:
            return jsonify({"success": False, "message": "No YouTube URL provided"}), 400

        # Download and convert video to MP3
        mp3_path = download_video_as_mp3(youtube_url)
        if not mp3_path or not os.path.isfile(mp3_path):
            return jsonify({"success": False, "message": "Failed to download video"}), 500

        # Return the MP3 file as a download
        return send_file(mp3_path, as_attachment=True)

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"success": False, "message": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
