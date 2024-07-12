import sys
import requests
import os
from pathlib import Path
import re
from pydub import AudioSegment
import traceback
from youtubesearchpython import VideosSearch

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

def download_audio(url, output_folder):
    try:
        title = "audio"
        folder_path = Path(output_folder)
        folder_path.mkdir(parents=True, exist_ok=True)
        output_path = folder_path / f"{title}.mp3"
        temp_path = folder_path / f"{title}.wav"

        # Download audio content
        audio_response = requests.get(url, stream=True)
        with open(temp_path, 'wb') as audio_file:
            for chunk in audio_response.iter_content(chunk_size=1024):
                if chunk:
                    audio_file.write(chunk)

        # Convert to MP3 using pydub
        audio_segment = AudioSegment.from_file(temp_path)
        audio_segment.export(output_path, format='mp3', bitrate="320k")

        # Clean up temporary file
        os.remove(temp_path)
        
        return output_path.name  # Return the filename for Node.js to capture

    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return None  # Return None in case of error

def search_and_download_video(youtube_url, output_folder):
    try:
        search = VideosSearch(youtube_url, limit=1)
        result = search.result()
        video_info = result['result'][0]
        video_id = video_info['id']
        title = sanitize_filename(video_info['title'])
        stream_url = f"https://www.youtubeinmp3.com/fetch/?video=https://www.youtube.com/watch?v={video_id}"

        # Download and convert the video to mp3
        return download_audio(stream_url, output_folder)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <youtube_url>", file=sys.stderr)
        sys.exit(1)
    youtube_url = sys.argv[1]
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
    result = search_and_download_video(youtube_url, output_folder)
    if result:
        print(result)
        sys.exit(0)
    else:
        sys.exit(1)
