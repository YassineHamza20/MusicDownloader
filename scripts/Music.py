import sys
import requests
import os
import subprocess
from pathlib import Path
import re
from pydub import AudioSegment
import traceback
import yt_dlp
import time

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
            print("FFmpeg stderr:", result.stderr.decode())
    except subprocess.CalledProcessError as e:
        print("FFmpeg command failed with error:", e.stderr.decode())
        raise e

    os.replace(output_path, audio_path)

def download_video_as_mp3(youtube_url, output_folder, retries=5, delay=60):
    def retry_yt_dlp_download(url, retries, delay):
        for attempt in range(retries):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=True)
            except yt_dlp.utils.DownloadError as e:
                if '429' in str(e):
                    print(f"HTTP 429: Too Many Requests. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                    time.sleep(delay)
                else:
                    raise e
        raise Exception("Maximum retries exceeded")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(Path(output_folder) / '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }

    try:
        info_dict = retry_yt_dlp_download(youtube_url, retries, delay)
        title = sanitize_filename(info_dict.get('title', 'audio'))
        output_path = Path(output_folder) / f"{title}.mp3"

        # Download thumbnail
        thumb_url = info_dict.get('thumbnail')
        response = requests.get(thumb_url)
        thumb_path = Path(output_folder) / "thumbnail.jpg"
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
