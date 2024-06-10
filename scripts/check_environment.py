# check_environment.py
import sys
import subprocess

def check_installations():
    print("Python version:", sys.version)
    print("Python executable:", sys.executable)
    print("Sys path:", sys.path)
    try:
        import requests
        import pytube
        import pydub
        print("All modules are installed.")
    except ImportError as e:
        print("ImportError:", e)

    ffmpeg_check = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ffmpeg_check.returncode == 0:
        print("ffmpeg is installed.")
    else:
        print("ffmpeg is not installed.")

if __name__ == "__main__":
    check_installations()
