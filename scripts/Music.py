import sys
import requests
import os
import subprocess
from pathlib import Path
import unicodedata
import re
from pytube import YouTube
from pydub import AudioSegment

# Set paths to ffmpeg and ffprobe for cross-platform compatibility
ffmpeg_path = 'ffmpeg'  # Assumes ffmpeg is in the system PATH
ffprobe_path = 'ffprobe'  # Assumes ffprobe is in the system PATH

# Set pydub to use the ffmpeg installed on the system
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

def sanitize_filename(filename):
    """Sanitize filename by removing or replacing invalid characters and retaining Unicode."""
    filename = re.sub(r'[<>:"/\\|?*]+', '_', filename)
    return filename

def embed_album_art_ffmpeg(audio_path, image_path):
    """Embeds album art into an MP3 file using FFmpeg."""
    output_path = audio_path.with_suffix('.temp.mp3')
    cmd = [
        ffmpeg_path,
        '-i', str(audio_path),
        '-i', str(image_queue_path),
        '-map', '0:0',
        '-map', '1:0',
        '-c', 'copy',
        '-id3v2_version', '3',
        '-metadata:s:v', 'title="Album cover"',
        '-metadata:s:v', 'comment="Cover (front)"',
        str(output_path)
    ]
    subprocess.run(cmd, check=True)
    os.replace(output_path, audio_path)  # Replace original file with the new one

def download_video_as_mp3(youtube_url, output_folder):
    try:
        yt = YouTube(youtube_url)
        title = sanitize_filename(yt.title)
        folder_path = Path(output_folder)
        folder_path.mkdir(parents=True, exist_ok=True)

        # Select the highest quality audio stream
        video = yt.streams.get_audio_only()
        temp_file = video.download(output_path=folder_path)

        # Output filename incorporates the title
        output_path = folder_path / f"{title}.mp3"
        
        # Convert to MP3 using explicit encoding
        audio_segment = AudioSegment.from_file(temp_file)
        audio_segment.export(output_path, format='mp3', bitrate="320k", tags={"title": yt.title})

        # Download the thumbnail
        thumb_url = yt.thumbnail_url
        response = requests.get(thumb_url)
        thumb_path = folder_path / "thumbnail.jpg"
        with open(thumb_path, 'wb') as thumb_file:
            thumb_file.write(response.content)

        # Embed the thumbnail as album art
        embed_album_art_ffmpeg(output_path, thumb_path)

        print(f"Downloaded and converted to MP3: {output_path}")

        # Cleanup temporary files
        os.remove(temp_file)
        os.remove(thumb_path)  # Remove thumbnail after embedding
    except Exception as e:
        print(f"Error processing {youtube_url}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <youtube_url>")
        sys.exit(1)

    youtube_url = sys.argv[1]
    # Determine the downloads folder based on the platform
    if sys.platform == "win32":
        output_folder = Path(os.getenv('USERPROFILE', ''), 'Downloads')
    else:
        output_folder = Path(os.getenv('HOME', ''), 'Downloads')
    download_video_as_mp3(youtube_url, output_folder)
