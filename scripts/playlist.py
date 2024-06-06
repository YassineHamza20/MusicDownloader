import sys
from pytube import YouTube, Playlist
from pydub import AudioSegment
import requests
import os
from pathlib import Path
import subprocess
import re
from urllib.parse import parse_qs, urlparse
import traceback

# Set paths to ffmpeg and ffprobe
ffmpeg_path = 'ffmpeg'
ffprobe_path = 'ffprobe'

# Configure pydub to use the ffmpeg installed on the system
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

def sanitize_filename(filename):
    """Sanitize filename by removing or replacing invalid characters."""
    return re.sub(r'[<>:"/\\|?*]+', '_', filename)

def validate_playlist_url(url):
    """Validates the playlist URL and extracts the playlist ID."""
    query = urlparse(url).query
    params = parse_qs(query)
    playlist_id = params.get('list')
    if not playlist_id:
        raise ValueError("Invalid playlist URL: No playlist ID found")
    return playlist_id[0]

def embed_album_art_ffmpeg(audio_path, image_path):
    """Embeds album art into an MP3 file using FFmpeg."""
    output_path = audio_path.with_suffix('.temp.mp3')
    cmd = [
        'ffmpeg',
        '-i', str(audio_path),
        '-i', str(image_path),
        '-map', '0:0',
        '-map', '1:0',
        '-c', 'copy',
        '-id3v2_version', '3',
        '-metadata:s:v', 'title="Album cover"',
        '-metadata:s:v', 'comment="Cover (front)"',
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
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
    try:
        yt = YouTube(youtube_url)
        title = sanitize_filename(yt.title)
        folder_path = Path(output_folder)
        folder_path.mkdir(parents=True, exist_ok=True)

        video = yt.streams.get_audio_only()
        temp_file = video.download(output_path=folder_path)

        output_path = folder_path / f"{title}.mp3"
        
        audio_segment = AudioSegment.from_file(temp_file)
        audio_segment.export(output_path, format='mp3', bitrate="320k")

        thumb_url = yt.thumbnail_url
        response = requests.get(thumb_url)
        thumb_path = folder_path / "thumbnail.jpg"
        with open(thumb_path, 'wb') as thumb_file:
            thumb_file.write(response.content)

        embed_album_art_ffmpeg(output_path, thumb_path)

        print(output_path.name)  # Print the filename to stdout for Node.js to capture

        os.remove(temp_file)
        os.remove(thumb_path)

        return output_path.name  # Return the filename for Node.js to capture
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return None  # Return None in case of error

def download_playlist(playlist_url):
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
    try:
        playlist_id = validate_playlist_url(playlist_url)
        playlist = Playlist(f"https://www.youtube.com/playlist?list={playlist_id}")
        print(f"Starting download of playlist: {playlist.title}")
        for video_url in playlist.video_urls:
            print(f"Downloading {video_url}")
            download_video_as_mp3(video_url, output_folder)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <playlist_url>", file=sys.stderr)
        sys.exit(1)
    playlist_url = sys.argv[1]
    result = download_playlist(playlist_url)
    if result:
        print(result)
        sys.exit(0)
    else:
        sys.exit(1)
