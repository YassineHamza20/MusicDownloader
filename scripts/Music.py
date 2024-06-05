import os
from flask import Flask, request, send_file, after_this_request
from pathlib import Path
import re
from pytube import YouTube
from pydub import AudioSegment
import tempfile

app = Flask(__name__)

def sanitize_filename(filename):
    """Sanitize filename by removing or replacing invalid characters and retaining Unicode."""
    return re.sub(r'[<>:"/\\|?*]+', '_', filename)

@app.route('/download', methods=['POST'])
def download_video():
    youtube_url = request.json.get('youtube_url')
    if not youtube_url:
        return {"message": "Invalid URL"}, 400

    # Create a temporary directory to hold the files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        try:
            yt = YouTube(youtube_url)
            title = sanitize_filename(yt.title)
            output_path = temp_dir_path / f"{title}.mp3"

            # Download and convert the video
            video = yt.streams.get_audio_only()
            temp_file_path = Path(video.download(output_path=temp_dir_path))

            # Convert to MP3
            audio_segment = AudioSegment.from_file(temp_file_path)
            audio_segment.export(output_path, format='mp3', bitrate="320k")

            # Cleanup the temporary video file
            os.remove(temp_file_path)

            @after_this_request
            def remove_file(response):
                os.remove(output_path)
                return response

            return send_file(str(output_path), as_attachment=True, download_name=f"{title}.mp3")

        except Exception as e:
            print(f"Error processing {youtube_url}: {e}")
            return {"message": "Failed to process the video"}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))  # Use the port provided by Render
    app.run(host="0.0.0.0", port=port, debug=True)
