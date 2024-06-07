import sys
import requests
import os
import subprocess
from pathlib import Path
import re
from pytube import Playlist, YouTube
from pydub import AudioSegment
import traceback
import zipfile

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

        # Clean up and log success
        os.remove(temp_file)
        return output_path.name  # Return the filename for Node.js to capture
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return None  # Return None in case of error

def download_playlist(playlist_url, output_folder):
    try:
        pl = Playlist(playlist_url)
        folder_path = Path(output_folder) / sanitize_filename(pl.title)
        folder_path.mkdir(parents=True, exist_ok=True)
        downloaded_files = []
        for video_url in pl.video_urls:
            result = download_video_as_mp3(video_url, folder_path)
            if result:
                downloaded_files.append(result)
        
        # Zip the folder
        zip_filename = folder_path.with_suffix('.zip')
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file in downloaded_files:
                zipf.write(folder_path / file, arcname=file)

        return zip_filename.name  # Return the zip filename
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <playlist_url>", file=sys.stderr)
        sys.exit(1)
    playlist_url = sys.argv[1]
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
    result = download_playlist(playlist_url, output_folder)
    if result:
        print(result)
        sys.exit(0)
    else:
        sys.exit(1)
