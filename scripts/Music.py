import sys
import requests
import os
import subprocess
from pathlib import Path
import re
import yt_dlp
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
    return re.sub(r'[<>:"/\\|?*]+', '_', filename).replace(' ', '_')

def embed_album_art_ffmpeg(audio_path, image_path):
    """Embeds album art into an MP3 file using FFmpeg."""
    output_path = audio_path.with_suffix('.temp.mp3')
    cmd = [
        ffmpeg_path, '-i', str(audio_path), '-i', str(image_path),
        '-map', '0:0', '-map', '1:0', '-c', 'copy', '-id3v2_version', '3',
        '-metadata:s:v', 'title=Album_cover', '-metadata:s:v', 'comment=Cover_(front)',
        str(output_path)
    ]
    
    try:
        if not audio_path.exists():
            print(f"Error: Audio file {audio_path} does not exist.", file=sys.stderr)
            return
        
        if not image_path.exists():
            print(f"Error: Image file {image_path} does not exist.", file=sys.stderr)
            return

        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stderr:
            print("FFmpeg stderr:", result.stderr.decode(), file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print("FFmpeg command failed with error:", e.stderr.decode(), file=sys.stderr)
        raise e

    os.replace(output_path, audio_path)

def download_video_as_mp3(youtube_url, output_folder):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(Path(output_folder) / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            title = sanitize_filename(info_dict.get('title', ''))
            output_path = Path(output_folder) / f"{title}.mp3"

        # Download thumbnail
        thumb_url = info_dict.get('thumbnail')
        response = requests.get(thumb_url)
        response.raise_for_status()  # Ensure the request was successful
        thumb_path = Path(output_folder) / "thumbnail.jpg"
        with open(thumb_path, 'wb') as thumb_file:
            thumb_file.write(response.content)

        print(f"Downloaded thumbnail to {thumb_path}")
        print(f"Checking if audio file exists at {output_path}")

        # Embed album art
        embed_album_art_ffmpeg(output_path, thumb_path)

        # Clean up and log success
        os.remove(thumb_path)

        return output_path.name  # Return the filename for Node.js to capture
    except yt_dlp.utils.DownloadError as e:
        print(f"DownloadError: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return None
    except requests.RequestException as e:
        print(f"RequestException: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return None
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return None
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return None  # Return None in case of error

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <youtube_url>", file=sys.stderr)
        sys.exit(1)
    youtube_url = sys.argv[1]
    output_folder = Path(__file__).resolve().parent.parent / 'public'
    result = download_video_as_mp3(youtube_url, output_folder)
    if result:
        print(result)
        sys.exit(0)
    else:
        sys.exit(1)
