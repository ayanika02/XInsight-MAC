import os
from subprocess import Popen, PIPE, STDOUT
import sys
import time
import webbrowser
import tempfile
import shutil


def main():
    print("Starting IDEAS XInsight...")
    
    # Getting path to python executable
    executable = sys.executable
    path_to_main = os.path.join(os.path.dirname(__file__), "home_grid.py")
    
    print(f"Python executable: {executable}")
    print(f"Main app path: {path_to_main}")
    
    # Start streamlit server FIRST (in background)
    print("Starting Streamlit server...")
    proc = Popen(
        [
            executable,
            "-m",
            "streamlit",
            "run",
            path_to_main,
            "--server.headless=true",
            "--server.maxMessageSize=30000",
            "--server.maxUploadSize=2000",
            "--global.developmentMode=false",
            "--server.port=8502"
        ],
        stdin=PIPE,
        stdout=PIPE,
        stderr=STDOUT,
        text=True,
    )
    proc.stdin.close()
    
    # Wait a moment for server to start initializing
    print("Waiting for Streamlit to initialize...")
    time.sleep(2)
    
    # Now open splash screen
    splash_path = os.path.join(os.path.dirname(__file__), "splash_screen.html")
    
    if os.path.exists(splash_path):
        print(f"Opening splash screen: {splash_path}")
        # Copy splash screen to temp directory and open it
        temp_dir = tempfile.mkdtemp()
        temp_splash = os.path.join(temp_dir, "splash_screen.html")
        shutil.copy(splash_path, temp_splash)
        
        # Copy assets to temp directory
        for asset in ["IDEAS-TIH.ico", "xinsight_small.gif"]:
            asset_path = os.path.join(os.path.dirname(__file__), asset)
            if os.path.exists(asset_path):
                shutil.copy(asset_path, os.path.join(temp_dir, asset))
                print(f"Copied asset: {asset}")
        
        # Open splash screen
        webbrowser.open(f"file://{temp_splash}")
    else:
        print(f"Splash screen not found at {splash_path}")
        # Fallback: just open the app directly
        time.sleep(5)
        webbrowser.open("http://localhost:8502")
    
    print("Streamlit server running. Waiting for process...")
    
    # Read output (this will block until streamlit exits)
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        print(line, end="")
    
    proc.wait()
    #print("Application closed.")


if __name__ == "__main__":
    main()