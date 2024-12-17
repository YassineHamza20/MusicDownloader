import os
import requests
import subprocess
from pathlib import Path
import re
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import traceback

# Define the path to cookies.txt in the scripts folder
script_dir = os.path.dirname(__file__)
cookies_path = os.path.join(script_dir, 'cookies.txt')

# Check if cookies.txt exists in the scripts folder
if not os.path.isfile(cookies_path):
    raise FileNotFoundError(f"cookies.txt not found in the script directory: {cookies_path}")

# Set FFmpeg path
ffmpeg_path = 'ffmpeg'
AudioSegment.converter = ffmpeg_path

def sanitize_filename(filename):
    """Sanitize filename by removing or replacing invalid characters."""
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
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.replace(output_path, audio_path)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        raise

def download_video_as_mp3(youtube_url, output_folder):
    try:
        folder_path = Path(output_folder)
        folder_path.mkdir(parents=True, exist_ok=True)

        # Use cookies file with yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(folder_path / '%(title)s.%(ext)s'),
            'cookiefile': cookies_path,  # Explicit path to cookies.txt
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        }

        # Run yt-dlp and download audio
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = sanitize_filename(info['title'])
            mp3_path = folder_path / f"{title}.mp3"

        # Download and embed album art
        thumb_url = info.get('thumbnail')
        if thumb_url:
            response = requests.get(thumb_url)
            thumb_path = folder_path / "thumbnail.jpg"
            with open(thumb_path, 'wb') as thumb_file:
                thumb_file.write(response.content)
            embed_album_art_ffmpeg(mp3_path, thumb_path)
            os.remove(thumb_path)

        return mp3_path.name
    except Exception as e:
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python Music.py <youtube_url>")
        sys.exit(1)

    youtube_url = sys.argv[1]
    output_folder = os.path.join(os.path.dirname(__file__), '..', 'public')
    print(f"Using cookies file: {cookies_path}")
    result = download_video_as_mp3(youtube_url, output_folder)

    if result:
        print(f"Downloaded: {result}")
        sys.exit(0)
    else:
        print("Download failed.")
        sys.exit(1)
