import sys
import os
import re
import json
import yt_dlp
from pathlib import Path
import zipfile
import time

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
            return cookie_file
    return None

def get_video_info(url):
    """Get video information."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'socket_timeout': 10,
    }
    
    cookies_file = get_cookies_file()
    if cookies_file:
        ydl_opts['cookiefile'] = cookies_file
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
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
        raise Exception(f"Error getting video info: {str(e)}")

def download_video(url, task_id, download_dir, temp_dir, quality='192'):
    """Download video as MP3."""
    task_folder = os.path.join(download_dir, task_id)
    os.makedirs(task_folder, exist_ok=True)
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip('%')
            try:
                progress = float(percent) if percent != 'NA' else 0
            except:
                progress = 0
            
            speed = d.get('_speed_str', 'N/A')
            print(f"PROGRESS:{progress}")
            print(f"SPEED:{speed}")
            
        elif d['status'] == 'finished':
            print(f"PROGRESS:100")
    
    try:
        # Get video info first
        info = get_video_info(url)
        title = sanitize_filename(info['title'])
        
        # yt-dlp options
        ydl_opts = {
            'format': 'bestaudio[filesize<25M]/bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'outtmpl': os.path.join(task_folder, f'{title}.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
            'max_filesize': 50 * 1024 * 1024,
            'socket_timeout': 30,
            'retries': 3,
        }
        
        cookies_file = get_cookies_file()
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
        
        # Download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Check result
        mp3_files = list(Path(task_folder).glob('*.mp3'))
        if not mp3_files:
            raise Exception("No MP3 file created")
        
        # Create ZIP
        zip_filename = f"{task_id}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for mp3_file in mp3_files:
                zipf.write(mp3_file, mp3_file.name)
        
        file_size = os.path.getsize(mp3_files[0])
        
        # Send completion message
        print(f"COMPLETED:{mp3_files[0].name}:{file_size}:{zip_path}")
        
    except Exception as e:
        print(f"ERROR:{str(e)}")
        raise

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py --info <youtube_url>")
        print("  python main.py --download <youtube_url> --quality <192> --task-id <id> --download-dir <dir> --temp-dir <dir>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == '--info' and len(sys.argv) >= 3:
        # Get video info
        url = sys.argv[2]
        try:
            info = get_video_info(url)
            print(json.dumps(info, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({'error': str(e)}))
    
    elif command == '--download' and len(sys.argv) >= 9:
        # Parse arguments
        args = {}
        for i in range(2, len(sys.argv), 2):
            if i + 1 < len(sys.argv):
                args[sys.argv[i]] = sys.argv[i + 1]
        
        url = args.get('--download')
        quality = args.get('--quality', '192')
        task_id = args.get('--task-id')
        download_dir = args.get('--download-dir', 'downloads')
        temp_dir = args.get('--temp-dir', 'temp')
        
        if not url or not task_id:
            print("ERROR:Missing required arguments")
            sys.exit(1)
        
        try:
            download_video(url, task_id, download_dir, temp_dir, quality)
        except Exception as e:
            print(f"ERROR:{str(e)}")
            sys.exit(1)
    
    else:
        print("ERROR:Invalid command or arguments")
        sys.exit(1)

if __name__ == '__main__':
    main()