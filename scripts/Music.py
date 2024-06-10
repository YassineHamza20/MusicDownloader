from __future__ import print_function
import sys
import time
import requests
import os
import subprocess
from pathlib import Path
import re
from pytube import YouTube
from pydub import AudioSegment
import traceback
from urllib.error import HTTPError

# Set paths to ffmpeg and ffprobe
ffmpeg_path = 'ffmpeg'
ffprobe_path = 'ffprobe'

# Configure pydub to use the ffmpeg installed on the system
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

def sanitize_filename(filename):
    """Sanitize filename by removing or replacing invalid characters and retaining Unicode."""
    return re.sub(r'[<>:"/\\|?*]+', '_', filename)

def embed_album_art_ffmpeg(audio_path, image_path):
    """Embeds album art into an MP3 file using FFmpeg."""
    output_path = audio_path.with_suffix('.temp.mp3')
    cmd = [
        ffmpeg_path, '-i', str(audio_path), '-i', str(image_path),
        '-map', '0:0', '-map', '1:0', '-c', 'copy', '-id3v2_version', '3',
        '-metadata:s:v', 'title="Album cover"', '-metadata:s:v', 'comment="Cover (front)"',
        str(output_path)
    ]
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stderr:
            print("FFmpeg stderr:", result.stderr.decode(), file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print("FFmpeg command failed with error:", e.stderr.decode(), file=sys.stderr)
        raise e

    os.replace(output_path, audio_path)

def download_video_as_mp3(youtube_url, output_folder, retries=5):
    user_agent = {'User-Agent': 'your bot 0.1'}
    for attempt in range(retries):
        try:
            print("Downloading video from URL:", youtube_url, file=sys.stderr)
            yt = YouTube(youtube_url)
            title = sanitize_filename(yt.title)
            print("Video title:", title, file=sys.stderr)
            folder_path = Path(output_folder)
            folder_path.mkdir(parents=True, exist_ok=True)
            video = yt.streams.get_audio_only()
            print("Downloading audio stream...", file=sys.stderr)
            temp_file = video.download(output_path=folder_path)
            print("Downloaded to temporary file:", temp_file, file=sys.stderr)
            output_path = folder_path / "{}.mp3".format(title)
            audio_segment = AudioSegment.from_file(temp_file)
            audio_segment.export(output_path, format='mp3', bitrate="320k", tags={"title": yt.title})

            # Download thumbnail
            thumb_url = yt.thumbnail_url
            print("Downloading thumbnail from URL:", thumb_url, file=sys.stderr)
            response = requests.get(thumb_url, headers=user_agent)
            thumb_path = folder_path / "thumbnail.jpg"
            with open(thumb_path, 'wb') as thumb_file:
                thumb_file.write(response.content)
            print("Thumbnail downloaded to:", thumb_path, file=sys.stderr)

            # Embed album art
            embed_album_art_ffmpeg(output_path, thumb_path)
            print("Album art embedded into:", output_path, file=sys.stderr)

            # Clean up and log success
            os.remove(temp_file)
            os.remove(thumb_path)

            return output_path.name  # Return the filename for Node.js to capture
        except HTTPError as e:
            if e.code == 429:
                wait_time = (2 ** attempt) * 10  # Exponential backoff
                print(f"HTTP 429 encountered. Retrying in {wait_time} seconds...", file=sys.stderr)
                time.sleep(wait_time)
            else:
                print("HTTP Error occurred:", e, file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return None
        except Exception as e:
            print("Error occurred:", e, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <youtube_url>", file=sys.stderr)
        sys.exit(1)
    youtube_url = sys.argv[1]
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
    print("Output folder set to:", output_folder, file=sys.stderr)
    result = download_video_as_mp3(youtube_url, output_folder)
    if result:
        print(result)
        sys.exit(0)
    else:
        sys.exit(1)
