import sys
from pytube import YouTube
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

def download_video_as_mp4(youtube_url, output_folder):
    try:
        yt = YouTube(youtube_url)
        title = sanitize_filename(yt.title)
        
        # Create the 'Videos' folder if it doesn't exist
        folder_path = output_folder / 'Videos'
        folder_path.mkdir(parents=True, exist_ok=True)

        # Select the highest quality video stream with audio
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not video:
            print(f"No suitable video stream found for {youtube_url}")
            return

        # Set the file name of the downloaded video
        file_name = f"{title}.mp4"
        output_path = folder_path / file_name

        # Download the video
        video.download(filename=output_path) # Ensure this points to a file path with a filename and extension

        print(f"Downloaded: {output_path}")

    except Exception as e:
        print(f"Error processing {youtube_url}: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <youtube_url>")
        sys.exit(1)

    youtube_url = sys.argv[1]
    # Define the path for the 'Downloads' folder
    output_folder = Path.home() / 'Downloads'
    download_video_as_mp4(youtube_url, output_folder)
