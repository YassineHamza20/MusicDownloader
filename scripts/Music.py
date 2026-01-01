#!/usr/bin/env python3
import sys
import os
import re
import yt_dlp
from pathlib import Path
import traceback

def sanitize_filename(filename):
    """Sanitize filename."""
    if not filename:
        return "audio"
    filename = re.sub(r'[<>:"/\\|?*]+', '_', filename)
    filename = re.sub(r'[^\x00-\x7F]+', '', filename)
    return filename.strip()[:100]

def get_cookies_file():
    """Find cookies file."""
    cookie_files = [
        'www.youtube.com_cookies',
        'www.youtube.com_cookies.txt',
        'cookies.txt'
    ]
    for cookie_file in cookie_files:
        if os.path.exists(cookie_file):
            print(f"[INFO] Found cookies file: {cookie_file}", file=sys.stderr)
            return cookie_file
    print("[INFO] No cookies file found", file=sys.stderr)
    return None

def download_single_mp3(youtube_url, quality='192'):
    """Download single video as MP3 - simple version for /music endpoint."""
    try:
        print(f"[INFO] Starting download for: {youtube_url}", file=sys.stderr)
        
        # Determine output directory (Render vs local)
        if 'RENDER' in os.environ:
            # On Render, save to public directory for serving
            output_folder = '/opt/render/project/src/public'
        else:
            # Local development
            output_folder = os.path.join(os.path.dirname(__file__), '..', 'public')
        
        # Create directory if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        print(f"[INFO] Output folder: {output_folder}", file=sys.stderr)
        
        # Simple yt-dlp options for single download
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'quiet': False,  # Show output for debugging
            'no_warnings': False,
            'socket_timeout': 60,
            'retries': 5,
            'fragment_retries': 5,
            'ignoreerrors': True,  # Continue on errors
            'no_overwrites': True,
            'max_filesize': 50 * 1024 * 1024,  # 50MB limit for Render
        }
        
        # Add cookies if available
        cookies_file = get_cookies_file()
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
        
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"[INFO] Extracting video info...", file=sys.stderr)
            info = ydl.extract_info(youtube_url, download=True)
            
            # Get the filename that was created
            title = sanitize_filename(info.get('title', 'audio'))
            filename = f"{title}.mp3"
            filepath = os.path.join(output_folder, filename)
            
            # Check if file was created
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"[SUCCESS] Download completed: {filename}", file=sys.stderr)
                print(f"[SUCCESS] File size: {file_size} bytes", file=sys.stderr)
                print(f"[SUCCESS] Saved to: {output_folder}", file=sys.stderr)
                
                # OUTPUT THE FILENAME - This is what Node.js reads
                print(filename)
                return True
            else:
                # Check for any MP3 file in the directory
                mp3_files = list(Path(output_folder).glob('*.mp3'))
                if mp3_files:
                    # Use the most recent MP3 file
                    latest_file = max(mp3_files, key=os.path.getctime)
                    filename = latest_file.name
                    print(f"[SUCCESS] Found MP3 file: {filename}", file=sys.stderr)
                    print(filename)
                    return True
                else:
                    raise Exception("No MP3 file was created")
                
    except Exception as e:
        print(f"[ERROR] Download failed: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False

def main():
    """Main function - expects just a YouTube URL as argument."""
    if len(sys.argv) != 2:
        print("Usage: python Music.py <youtube_url>", file=sys.stderr)
        print("Example: python Music.py https://www.youtube.com/watch?v=dQw4w9WgXcQ", file=sys.stderr)
        sys.exit(1)
    
    youtube_url = sys.argv[1].strip()
    
    print(f"[INFO] Starting Music.py with URL: {youtube_url}", file=sys.stderr)
    
    # Validate URL format
    if 'youtube.com' not in youtube_url and 'youtu.be' not in youtube_url:
        print(f"[ERROR] Invalid YouTube URL: {youtube_url}", file=sys.stderr)
        sys.exit(1)
    
    try:
        success = download_single_mp3(youtube_url, quality='192')
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"[FATAL] Unexpected error: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()