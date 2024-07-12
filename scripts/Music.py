import sys
import os
import re
from io import BytesIO
import yt_dlp
import traceback

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
            audio_file_path = f"{title}.mp3"

        # Read the audio file into memory
        with open(audio_file_path, "rb") as f:
            audio_data = f.read()
        
        # Clean up the downloaded file
        os.remove(audio_file_path)
        
        return audio_data, title

    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return None, None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python Music.py <youtube_url>", file=sys.stderr)
        sys.exit(1)
    youtube_url = sys.argv[1]
    audio_data, title = download_video_as_mp3(youtube_url)
    if audio_data:
        sys.stdout.buffer.write(audio_data)
        sys.exit(0)
    else:
        sys.exit(1)
