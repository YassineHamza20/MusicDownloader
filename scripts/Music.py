import sys
import requests
import os
import subprocess
from pathlib import Path
import re
from pytube import YouTube
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
        folder_path.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
        video = yt.streams.get_audio_only()
        temp_file = video.download(output_path=folder_path)  # Download the audio stream
        output_path = folder_path / f"{title}.mp3"  # Path where the MP3 will be saved
        audio_segment = AudioSegment.from_file(temp_file)
        audio_segment.export(output_path, format='mp3', bitrate="320k", tags={"title": yt.title})  # Export as MP3

        # Download and embed thumbnail as album art
        thumb_url = yt.thumbnail_url
        response = requests.get(thumb_url)
        thumb_path = folder_path / "thumbnail.jpg"
        with open(thumb_path, 'wb') as thumb_file:
            thumb_file.write(response.content)
        embed_album_art_ffmpeg(output_path, thumb_path)  # Embed album art using FFmpeg

        print(f"Downloaded and converted to MP3: {output_path}")
        os.remove(temp_file)  # Clean up temporary video file
        os.remove(thumb_path)  # Clean up downloaded thumbnail

        return str(output_path.name)  # Return the filename for use in the Node.js response
    except Exception as e:
        traceback.print_exc()  # This will print the stack trace to stderr
        return str(e)  # Return the exception message instead of None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <youtube_url>")
        sys.exit(1)
    youtube_url = sys.argv[1]
    output_folder = '/tmp'
    sys.exit(download_video_as_mp3(youtube_url, output_folder))
    
