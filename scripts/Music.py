import os
from flask import Flask, request, send_file, after_this_request
from pathlib import Path
import re
from pytube import YouTube
from pydub import AudioSegment
import tempfile
import socket

app = Flask(__name__)

def sanitize_filename(filename):
    """Sanitize filename by removing or replacing invalid characters and retaining Unicode."""
    return re.sub(r'[<>:"/\\|?*]+', '_', filename)

def is_valid_youtube_url(url):
    """Validate YouTube URL."""
    return bool(re.match(r'(https?://)?(www\.)?(youtube.com|youtu.be)/', url))

@app.route('/music', methods=['POST'])
def download_video():
    youtube_url = request.json.get('youtube_url')
    if not youtube_url or not is_valid_youtube_url(youtube_url):
        return {"message": "Invalid URL"}, 400

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        try:
            yt = YouTube(youtube_url)
            title = sanitize_filename(yt.title)
            output_path = temp_dir_path / f"{title}.mp3"

            video = yt.streams.get_audio_only()
            temp_file_path = Path(video.download(output_path=temp_dir_path))

            audio_segment = AudioSegment.from_file(temp_file_path)
            audio_segment.export(output_path, format='mp3', bitrate="320k")

            os.remove(temp_file_path)

            @after_this_request
            def remove_file(response):
                os.remove(output_path)
                return response

            return send_half_file(str(output_path), as_attachment=True, download_name=f"{title}.mp3")

        except Exception as e:
            return {"message": f"Failed to process the video due to error: {e}"}, 500

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

port = 5001  # Example port number
if check_port(port):
    print(f"Port {port} is already in use")
else:
    print(f"Port {port} is available")
    # Start Flask app here if port is available

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', port, app)  # Specify the port explicitly here
