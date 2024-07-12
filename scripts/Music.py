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

def embed_album_art_ffmpeg(audio_data, image_data):
    output = BytesIO()
    cmd = [
        ffmpeg_path, '-i', 'pipe:0', '-i', 'pipe:1',
        '-map', '0:0', '-map', '1:0', '-c', 'copy', '-id3v2_version', '3',
        '-metadata:s:v', 'title=Album cover', '-metadata:s:v', 'comment=Cover (front)',
        'pipe:2'
    ]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(input=audio_data.read() + image_data.read())
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd, output=stdout, stderr=stderr)
    output.write(stdout)
    return output

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
            thumbnail_url = info_dict.get('thumbnail', '')

        audio_data = BytesIO()
        with open(f"{title}.mp3", "rb") as f:
            audio_data.write(f.read())

        if thumbnail_url:
            response = requests.get(thumbnail_url)
            image_data = BytesIO(response.content)

            audio_with_art = embed_album_art_ffmpeg(audio_data, image_data)
            return audio_with_art, title
        else:
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
