import sys
import requests
import os
import subprocess
from pathlib import Path
import re
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pydub import AudioSegment
import traceback

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

def download_video_as_mp3(youtube_url, output_folder):
    try:
        print(f"Starting download for URL: {youtube_url}")
        yt = YouTube(youtube_url, on_progress_callback=on_progress)
        title = sanitize_filename(yt.title)
        print(f"Video title: {title}")
        
        folder_path = Path(output_folder)
        folder_path.mkdir(parents=True, exist_ok=True)
        video = yt.streams.get_audio_only()
        
        if not video:
            print("No audio-only stream available.")
            return None
        
        output_path = folder_path / f"{title}.mp3"
        video.download(output_path=folder_path, mp3=True)
        
        # Move and rename the downloaded file
        temp_file = folder_path / f"{title}.mp4"
        if temp_file.exists():
            temp_file.rename(output_path)

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

        print(f"Download and conversion successful: {output_path}")
        return output_path.name  # Return the filename for Node.js to capture
    except Exception as e:
        print("An error occurred:", e, file=sys.stderr)
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
