import sys
import requests
import subprocess
from io import BytesIO
import re
from pydub import AudioSegment
import traceback
import yt_dlp

ffmpeg_path = 'ffmpeg'
ffprobe_path = 'ffprobe'

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]+', '_', filename)

def download_video_as_mp3(youtube_url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            title = sanitize_filename(info_dict.get('title', ''))

        audio_data = BytesIO()
        with open(f"{title}.mp3", "rb") as f:
            audio_data.write(f.read())

        return audio_data, title

    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return None, None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <youtube_url>", file=sys.stderr)
        sys.exit(1)
    youtube_url = sys.argv[1]
    audio_data, title = download_video_as_mp3(youtube_url)
    if audio_data:
        sys.stdout.buffer.write(audio_data.getvalue())
        sys.exit(0)
    else:
        sys.exit(1)
