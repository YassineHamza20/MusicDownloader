import sys
from pytube import YouTube, Playlist
from pydub import AudioSegment
import requests
import os
from pathlib import Path
import subprocess
from urllib.parse import parse_qs, urlparse

# Set paths to ffmpeg and ffprobe
ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"
ffprobe_path = r"C:\ffmpeg\bin\ffprobe.exe"
os.environ["PATH"] += os.pathsep + r'C:\ffmpeg\bin'

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

def sanitize_filename(filename):
    """Sanitize filename by removing or replacing invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

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
    subprocess.run(cmd, check=True)
    os.replace(output_path, audio_path)  # Replace original file with the new one

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
        audio_segment.export(output_path, format='mp3', bitrate="320k")

        thumb_url = yt.thumbnail_url
        response = requests.get(thumb_url)
        thumb_path = folder_path / "thumbnail.jpg"
        with open(thumb_path, 'wb') as thumb_file:
            thumb_file.write(response.content)

        embed_album_art_ffmpeg(output_path, thumb_path)

        print(f"Downloaded and converted to MP3: {output_path}")

        os.remove(temp_file)
        os.remove(thumb_path)
    except Exception as e:
        print(f"Error processing {youtube_url}: {e}")

def download_playlist(playlist_url, output_folder):
    try:
        playlist_id = validate_playlist_url(playlist_url)
        playlist = Playlist(f"https://www.youtube.com/playlist?list={playlist_id}")
        print(f"Starting download of playlist: {playlist.title}")
        for video_url in playlist.video_urls:
            print(f"Downloading {video_url}")
            download_video_as_mp3(video_url, output_folder)
    except Exception as e:
        print(f"Error processing playlist {playlist_url}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <playlist_url>")
        sys.exit(1)
    playlist_url = sys.argv[1]
    output_folder = Path.home() / 'Downloads' / 'PlaylistMp3'
    download_playlist(playlist_url, output_folder)
    
