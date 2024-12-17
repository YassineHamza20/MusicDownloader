import sys
import requests
import os
import subprocess
from pathlib import Path
import re
from pytube import YouTube
from pydub import AudioSegment
import pytube
import traceback

# Monkey patch for pytube's title error
def patched_get_yt_initial_data(self):
    from pytube.extract import get_ytplayer_config
    self._yt_initial_data = get_ytplayer_config(self.watch_html)["ytInitialData"]

pytube.__main__.YouTube._get_yt_initial_data = patched_get_yt_initial_data

# Set paths to ffmpeg
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
        yt = YouTube(youtube_url)
        title = sanitize_filename(yt.title)

        folder_path = Path(output_folder)
        folder_path.mkdir(parents=True, exist_ok=True)

        video = yt.streams.get_audio_only()
        temp_file = video.download(output_path=folder_path)
        output_path = folder_path / f"{title}.mp3"
        audio_segment = AudioSegment.from_file(temp_file)
        audio_segment.export(output_path, format='mp3', bitrate="320k", tags={"title": yt.title})

        # Download thumbnail
        thumb_url = yt.thumbnail_url
        response = requests.get(thumb_url)
        thumb_path = folder_path / "thumbnail.jpg"
        with open(thumb_path, 'wb') as thumb_file:
            thumb_file.write(response.content)

        # Embed album art
        embed_album_art_ffmpeg(output_path, thumb_path)

        os.remove(temp_file)
        os.remove(thumb_path)

        return output_path.name
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <youtube_url>")
        sys.exit(1)
    youtube_url = sys.argv[1]
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
    result = download_video_as_mp3(youtube_url, output_folder)

    if result:
        print(result)
        sys.exit(0)
    else:
        sys.exit(1)
