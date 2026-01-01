#!/usr/bin/env python3
import sys
import os
import re
import json
import yt_dlp
from pathlib import Path
import zipfile
import time
import traceback  # ADD THIS FOR DEBUGGING

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
            print(f"Found cookies file: {cookie_file}", file=sys.stderr)  # DEBUG
            return cookie_file
    print("No cookies file found", file=sys.stderr)  # DEBUG
    return None

def get_video_info(url):
    """Get video information."""
    print(f"Getting video info for: {url}", file=sys.stderr)  # DEBUG
    
    ydl_opts = {
        'quiet': False,  # CHANGED TO FALSE FOR DEBUG
        'no_warnings': False,  # CHANGED TO FALSE FOR DEBUG
        'extract_flat': True,
        'socket_timeout': 30,  # INCREASED
    }
    
    cookies_file = get_cookies_file()
    if cookies_file:
        ydl_opts['cookiefile'] = cookies_file
        print(f"Using cookies from: {cookies_file}", file=sys.stderr)  # DEBUG
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"Successfully got video info", file=sys.stderr)  # DEBUG
            
            # Check limits (safe for Render)
            duration = info.get('duration', 0)
            if duration > 900:  # 15 minutes
                raise Exception(f"Video too long ({duration//60} min). Max 15 minutes.")
            
            filesize = info.get('filesize_approx', 0)
            if filesize > 50 * 1024 * 1024:  # 50MB
                raise Exception(f"Video too large ({filesize//1024//1024}MB). Max 50MB.")
            
            return {
                'title': info.get('title', 'Unknown'),
                'duration': duration,
                'uploader': info.get('uploader', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'is_live': info.get('is_live', False)
            }
    except Exception as e:
        print(f"Error in get_video_info: {str(e)}", file=sys.stderr)  # DEBUG
        traceback.print_exc(file=sys.stderr)  # DEBUG
        raise Exception(f"Error getting video info: {str(e)}")

def download_video(url, task_id, download_dir, temp_dir, quality='192'):
    """Download video as MP3."""
    print(f"Starting download for task {task_id}: {url}", file=sys.stderr)  # DEBUG
    
    # Create directories
    task_folder = os.path.join(download_dir, task_id)
    os.makedirs(task_folder, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Task folder: {task_folder}", file=sys.stderr)  # DEBUG
    print(f"Temp dir: {temp_dir}", file=sys.stderr)  # DEBUG
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip('%')
            try:
                progress = float(percent) if percent != 'NA' else 0
            except:
                progress = 0
            
            speed = d.get('_speed_str', 'N/A')
            print(f"PROGRESS:{progress}")
            if speed and speed != 'N/A':
                print(f"SPEED:{speed}")
            
        elif d['status'] == 'finished':
            print(f"PROGRESS:100")
    
    try:
        # Get video info first
        info = get_video_info(url)
        title = sanitize_filename(info['title'])
        
        print(f"Video title: {title}", file=sys.stderr)  # DEBUG
        
        # yt-dlp options for Render
        ydl_opts = {
            'format': 'bestaudio/best',  # SIMPLIFIED FOR RENDER
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'outtmpl': os.path.join(task_folder, f'{title}.%(ext)s'),
            'quiet': False,  # CHANGED FOR DEBUG
            'no_warnings': False,  # CHANGED FOR DEBUG
            'progress_hooks': [progress_hook],
            'max_filesize': 50 * 1024 * 1024,
            'socket_timeout': 60,  # INCREASED FOR RENDER
            'retries': 5,  # INCREASED
            'fragment_retries': 5,
            'ignoreerrors': True,  # IMPORTANT FOR RENDER
            'no_overwrites': True,
        }
        
        cookies_file = get_cookies_file()
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
            print(f"Using cookies for download", file=sys.stderr)  # DEBUG
        
        # Download
        print(f"Starting yt-dlp download...", file=sys.stderr)  # DEBUG
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print(f"Download completed, looking for MP3 files...", file=sys.stderr)  # DEBUG
        
        # Check result
        mp3_files = list(Path(task_folder).glob('*.mp3'))
        print(f"Found {len(mp3_files)} MP3 files", file=sys.stderr)  # DEBUG
        
        if not mp3_files:
            # Check for any audio files
            audio_files = list(Path(task_folder).glob('*.*'))
            print(f"All files in task folder: {audio_files}", file=sys.stderr)  # DEBUG
            raise Exception("No MP3 file created")
        
        # Create ZIP
        zip_filename = f"{task_id}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        print(f"Creating ZIP: {zip_path}", file=sys.stderr)  # DEBUG
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for mp3_file in mp3_files:
                zipf.write(mp3_file, mp3_file.name)
                print(f"Added to ZIP: {mp3_file.name}", file=sys.stderr)  # DEBUG
        
        file_size = os.path.getsize(mp3_files[0])
        print(f"File size: {file_size} bytes", file=sys.stderr)  # DEBUG
        
        # Send completion message
        print(f"COMPLETED:{mp3_files[0].name}:{file_size}:{zip_path}")
        
    except Exception as e:
        print(f"ERROR in download_video: {str(e)}", file=sys.stderr)  # DEBUG
        traceback.print_exc(file=sys.stderr)  # DEBUG
        print(f"ERROR:{str(e)}")
        raise

def main():
    """Main entry point."""
    print(f"Python script started with args: {sys.argv}", file=sys.stderr)  # DEBUG
    
    if len(sys.argv) < 2:
        print("ERROR: No arguments provided", file=sys.stderr)  # DEBUG
        print("Usage:")
        print("  python main.py --info <youtube_url>")
        print("  python main.py --download <youtube_url> --quality <192> --task-id <id> --download-dir <dir> --temp-dir <dir>")
        sys.exit(1)
    
    command = sys.argv[1]
    print(f"Command: {command}", file=sys.stderr)  # DEBUG
    
    if command == '--info' and len(sys.argv) >= 3:
        # Get video info
        url = sys.argv[2]
        print(f"Getting info for: {url}", file=sys.stderr)  # DEBUG
        try:
            info = get_video_info(url)
            print(json.dumps(info, ensure_ascii=False))
            sys.exit(0)
        except Exception as e:
            error_msg = json.dumps({'error': str(e)})
            print(f"ERROR returning: {error_msg}", file=sys.stderr)  # DEBUG
            print(error_msg)
            sys.exit(1)
    
    elif command == '--download' and len(sys.argv) >= 9:
        # Parse arguments
        args = {}
        for i in range(2, len(sys.argv), 2):
            if i + 1 < len(sys.argv):
                key = sys.argv[i]
                value = sys.argv[i + 1]
                args[key] = value
                print(f"Arg: {key} = {value}", file=sys.stderr)  # DEBUG
        
        url = args.get('--download')
        quality = args.get('--quality', '192')
        task_id = args.get('--task-id')
        download_dir = args.get('--download-dir', 'downloads')
        temp_dir = args.get('--temp-dir', 'temp')
        
        print(f"Parsed args - URL: {url}, Task ID: {task_id}", file=sys.stderr)  # DEBUG
        
        if not url or not task_id:
            print("ERROR: Missing required arguments", file=sys.stderr)
            print(f"URL: {url}, Task ID: {task_id}", file=sys.stderr)
            sys.exit(1)
        
        try:
            download_video(url, task_id, download_dir, temp_dir, quality)
            sys.exit(0)
        except Exception as e:
            print(f"ERROR in main download: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            print(f"ERROR:{str(e)}")
            sys.exit(1)
    
    else:
        print(f"ERROR: Invalid command or arguments. Args: {sys.argv}", file=sys.stderr)
        print("ERROR:Invalid command or arguments")
        sys.exit(1)

if __name__ == '__main__':
    main()