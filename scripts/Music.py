import sys
import requests
import os
import subprocess
from pathlib import Path
import re
from pytube import YouTube
from pydub import AudioSegment
import traceback
import urllib.parse

# Set paths to ffmpeg and ffprobe
ffmpeg_path = 'ffmpeg'
ffprobe_path = 'ffprobe'

# Configure pydub to use the ffmpeg installed on the system
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

def sanitize_filename(filename):
    """Sanitize filename by removing or replacing invalid characters and retaining Unicode."""
    filename = re.sub(r'[<>:"/\\|?*]+', '_', filename)
    filename = re.sub(r'\s+', '_', filename)  # Replace spaces with underscores
    return filename

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
            print("FFmpeg stderr:", result.stderr.decode())
    except subprocess.CalledProcessError as e:
        print("FFmpeg command failed with error:", e.stderr.decode())
        raise e

    os.replace(output_path, audio_path)

def download_video_as_mp3(youtube_url, output_folder):
    output_folder = os.path.join(os.path.dirname(__file__), 'public')  # Define output folder relative to script location
    try:
        yt = YouTube(youtube_url)
        title = sanitize_filename(yt.title)
        folder_path = Path(output_folder)
        folder_path.mkdir(parents=True, exist_ok=True)
        video = yt.streams.get_audio_only()
        temp_file = video.download(output_path=folder_path)
        output_path = folder_path / f"{title}.mp3"
        audio_segment = AudioSegment.from_file(temp_file)
        audio_segment.export(output_path, format='mp3', bitrate="320k", tags={"title": yt.title})

        # Clean up and log success
        os.remove(temp_file)
        print(urllib.parse.quote(output_path.name))  # Print the URL-safe filename to stdout for Node.js to capture

        return 0  # Exit successfully
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return 1  # Exit with error

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <youtube_url>", file=sys.stderr)
        sys.exit(1)
    youtube_url = sys.argv[1]
    output_folder = '/tmp'
    result = download_video_as_mp3(youtube_url, output_folder)
    sys.exit(result)
