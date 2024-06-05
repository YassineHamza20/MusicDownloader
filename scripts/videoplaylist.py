import sys
from pytube import YouTube, Playlist
import os
from pathlib import Path

# Set paths to ffmpeg and ffprobe
ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"
ffprobe_path = r"C:\ffmpeg\bin\ffprobe.exe"
os.environ["PATH"] += os.pathsep + r'C:\ffmpeg\bin'

def sanitize_filename(filename):
    """Sanitize filename by removing or replacing invalid characters."""
    invalid_chars = '<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def download_video_as_mp4(video, output_folder):
    try:
        title = sanitize_filename(video.title)
        # Ensure we use the correct file name
        output_path = output_folder / f"{title}.mp4"

        # Select the highest quality video stream with audio and download it
        stream = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if stream:
            stream.download(filename=output_path)
            print(f"Downloaded: {output_path}")
        else:
            print(f"No suitable stream found for {title}")
    except Exception as e:
        print(f"Error downloading {video.title}: {e}")

def download_playlist(playlist_url, output_folder):
    playlist = Playlist(playlist_url)
    print(f"Downloading playlist: {playlist.title}")
    for video in playlist.videos:
        download_video_as_mp4(video, output_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <youtube_url_or_playlist_url>")
        sys.exit(1)

    url = sys.argv[1]
    output_folder = Path.home() / 'Downloads' / 'PlaylistMp4'
    output_folder.mkdir(parents=True, exist_ok=True)  # Make sure the target directory exists
    if 'playlist?list=' in url:
        download_playlist(url, output_folder)
    else:
        yt = YouTube(url)
        download_video_as_mp4(yt, output_folder)
