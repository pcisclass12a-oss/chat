import subprocess
import threading
import time
import re
import sys
from pathlib import Path

def run_server():
    print("[SERVER] Starting FastAPI server...")
    subprocess.run([sys.executable, "run_server.py"])

def run_tunnel():
    print("[CLOUDFLARE] Starting tunnel...")
    cloudflared_path = Path(__file__).with_name("cloudflared.exe")
    binary = str(cloudflared_path) if cloudflared_path.exists() else "cloudflared"
    # Cloudflared logs to standard error
    process = subprocess.Popen(
        [binary, "tunnel", "--url", "http://127.0.0.1:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    url_found = False
    
    # Read stderr line by line
    while True:
        line = process.stderr.readline()
        if not line:
            break
            
        # Parse for the Cloudflare URL
        if "trycloudflare.com" in line and "https://" in line and not url_found:
            match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
            if match:
                url = match.group(0)
                print("\n" + "="*60)
                print(f"SERVER IS LIVE GLOBALLY!")
                print(f"Public Link: {url}")
                print("="*60 + "\n")
                url_found = True

if __name__ == "__main__":
    try:
        # Start server in a background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Give server a second to bind
        time.sleep(2)
        
        # Run tunnel in main thread (blocks and keeps script alive)
        run_tunnel()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
