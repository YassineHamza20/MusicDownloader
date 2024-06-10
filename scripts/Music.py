import sys
import requests
import os
import subprocess
from pathlib import Path
import re
from pytube import YouTube
import traceback
import time

# Set paths to ffmpeg and ffprobe
ffmpeg_path = 'ffmpeg'
ffprobe_path = 'ffprobe'

def sanitize_filename(filename):
    """Sanitize filename by removing or replacing invalid characters and retaining Unicode."""
    return re.sub(r'[<>:"/\\|?*]+', '_', filename)

def embed_album_art_ffmpeg(audio_path, image_path):
    """Embeds album art into an MP3 file using FFmpeg."""
    output_path = audio_path.with_suffix('.temp.mp3')
    cmd = [
        ffmpeg_path, '-i', str(audio_path), '-i', str(image_path),
        '-map', '0', '-map', '1', '-c', 'copy', '-id3v2_version', '3',
        '-metadata:s:v', 'title="Album cover"', '-metadata:s:v', 'comment="Cover (front)"',
        str(output_path)
    ]
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stderr:
            print("FFmpeg stderr:", result.stderr.decode())
    except subprocess.CalledProcessError as e:
        print("FFmpeg command failed with error:", e.stderr.decode())
        raise e

    os.replace(output_path, audio_path)

def download_video_as_mp3(youtube_url, output_folder):
    try:
        yt = retry_request(YouTube, youtube_url)
        title = sanitize_filename(yt.title)
        folder_path = Path(output_folder)
        folder_path.mkdir(parents=True, exist_ok=True)
        audio_stream = retry_request(yt.streams.get_audio_only)
        output_path = folder_path / f"{title}.mp3"
        audio_stream.download(output_path=folder_path, filename=f"{title}.mp3")

        # Download thumbnail
        thumb_url = yt.thumbnail_url
        response = requests.get(thumb_url)
        thumb_path = folder_path / "thumbnail.jpg"
        with open(thumb_path, 'wb') as thumb_file:
            thumb_file.write(response.content)

        # Embed album art
        embed_album_art_ffmpeg(output_path, thumb_path)

        # Clean up and log success
        os.remove(thumb_path)

        return output_path.name  # Return the filename for Node.js to capture
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return None  # Return None in case of error

def retry_request(func, *args, max_retries=5, initial_delay=1, backoff_factor=2, **kwargs):
    """Retries a request with exponential backoff."""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, urllib.error.HTTPError) and e.code == 429:
                print(f"HTTP 429 Error: Too many requests. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= backoff_factor
            else:
                raise e
    raise Exception(f"Failed to complete request after {max_retries} attempts.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <youtube_url>", file=sys.stderr)
        sys.exit(1)
    youtube_url = sys.argv[1]
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
    result = download_video_as_mp3(youtube_url, output_folder)
    if result:
        print(result)
        sys.exit(0)
    else:
        sys.exit(1)
