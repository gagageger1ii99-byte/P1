import os
import time
import subprocess
from curl_cffi import requests

CHANNEL_NAME = "ib6h"
RTMP_TARGET = "rtmp://live.restream.io/live/re_11725544_event57b4ae7f7bef4493a9528d5432741a03"

def get_kick_stream_url(channel_name):
    api_url = f"https://kick.com/api/v2/channels/{channel_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://kick.com/",
        "Origin": "https://kick.com/"
    }
    try:
        response = requests.get(api_url, headers=headers, impersonate="chrome120", timeout=15)
        if response.status_code == 200:
            data = response.json()
            playback_url = data.get("playback_url")
            if playback_url:
                return playback_url
    except Exception:
        pass
    return None

def start_stream():
    print(f"[*] Starting Restream Bridge for: {CHANNEL_NAME}...")
    
    while True:
        live_url = get_kick_stream_url(CHANNEL_NAME)
        
        if not live_url:
            print("[!] Stream is offline. Retrying in 30 seconds...")
            time.sleep(30)
            continue

        print(f"[+] Active stream found! Launching FFmpeg push to Restream...")
        
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-fflags', '+nobuffer+discardcorrupt',
            '-i', live_url,
            '-map', '0:v:0',
            '-map', '0:a:0?',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'flv',
            RTMP_TARGET
        ]
        
        subprocess.run(ffmpeg_cmd)
        print("[!] FFmpeg connection dropped. Re-checking in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    start_stream()

