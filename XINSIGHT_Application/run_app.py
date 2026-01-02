# import os
# from subprocess import Popen, PIPE, STDOUT
# import sys
# import time
# import webbrowser

# #running it as streamlit run run_app.py was opening infinite tabs, so we run python run_app.py instead
# def main():

#     # Getting path to python executable (full path of deployed python on Windows)
#     executable = sys.executable

#     path_to_main = os.path.join(os.path.dirname(__file__), "home_grid.py")
#     print(path_to_main)

#     # Running streamlit server in a subprocess and writing to log file
#     proc = Popen(
#         [
#             executable,
#             "-m",
#             "streamlit",
#             "run",
#             path_to_main,
#             # The following option appears to be necessary to correctly start the streamlit server,
#             # but it should start without it. More investigations should be carried out.
#             "--server.headless=true",
#             "--global.developmentMode=false",
#             "--server.maxMessageSize=1000"
#         ],
#         stdin=PIPE,
#         stdout=PIPE,
#         stderr=STDOUT,
#         text=True,
#     )
#     proc.stdin.close()

#     # Force the opening (does not open automatically) of the browser tab after a brief delay to let
#     # the streamlit server start.
#     time.sleep(3)
#     #webbrowser.open("http://localhost:8502/?embed=true&embed_options=hide_loading_screen")
#     webbrowser.open("http://localhost:8502")

#     while True:
#         s = proc.stdout.read()
#         if not s:
#             break
#         print(s, end="")

#     proc.wait()


# if __name__ == "__main__":
#     main()

# # # import os
# # # import sys
# # # import subprocess
# # # import time
# # # import webbrowser
# # # import socket
# # # import signal
# # # import atexit

# # # def kill_port(port):
# # #     try:
# # #         # MacOS specific port killing
# # #         result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
# # #         if result.stdout:
# # #             for pid in result.stdout.strip().split('\n'):
# # #                 os.kill(int(pid), signal.SIGTERM)
# # #     except: pass

# # # def main():
# # #     PORT = 8502
# # #     kill_port(PORT)
    
# # #     # Identify if we are running inside the .app bundle
# # #     is_frozen = getattr(sys, 'frozen', False)
    
# # #     if is_frozen:
# # #         # Path: XInsight.app/Contents/Resources/
# # #         res_dir = os.path.join(os.path.dirname(sys.executable), '..', 'Resources')
# # #         main_script = os.path.abspath(os.path.join(res_dir, 'XINSIGHT_Application', 'home_grid.py'))
# # #         # Crucial: Add the bundled site-packages to the path
# # #         lib_dir = os.path.join(res_dir, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}')
# # #         env = os.environ.copy()
# # #         env['PYTHONPATH'] = lib_dir + ":" + env.get('PYTHONPATH', '')
# # #     else:
# # #         main_script = os.path.join(os.path.dirname(__file__), "XINSIGHT_Application", "home_grid.py")
# # #         env = os.environ.copy()

# # #     cmd = [
# # #         sys.executable,
# # #         "-m", "streamlit", "run",
# # #         main_script,
# # #         f"--server.port={PORT}",
# # #         "--server.headless=true",
# # #         "--global.developmentMode=false",
# # #     ]

# # #     # Start the process
# # #     proc = subprocess.Popen(cmd, env=env)
    
# # #     # Wait for the server to actually be alive before opening browser
# # #     for _ in range(20):
# # #         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
# # #             if s.connect_ex(('localhost', PORT)) == 0:
# # #                 break
# # #         time.sleep(0.5)

# # #     webbrowser.open(f"http://localhost:{PORT}")
    
# # #     # Keep the wrapper script alive while streamlit is running
# # #     atexit.register(lambda: proc.terminate())
# # #     proc.wait()

# # # if __name__ == "__main__":
# # #     main()

# # # import os
# # # import sys
# # # import subprocess
# # # import time

# # # def main():
# # #     is_frozen = getattr(sys, 'frozen', False)
    
# # #     if is_frozen:
# # #         # Standard py2app bundle structure
# # #         res_path = os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..', 'Resources'))
# # #         app_path = os.path.join(res_path, 'XINSIGHT_Application')
# # #         script_path = os.path.join(app_path, 'home_grid.py')
        
# # #         env = os.environ.copy()
# # #         env["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
# # #         env["STREAMLIT_RUNTIME_ENV"] = "production"

# # #         # Ensure the bundled Python can find its own site-packages
# # #         env['PYTHONPATH'] = os.path.join(res_path, 'lib', 'python3.11')
# # #     else:
# # #         # Development mode
# # #         app_path = os.path.dirname(__file__)
# # #         script_path = os.path.join(app_path, 'home_grid.py')
# # #         env = os.environ.copy()
# # #     # Commands to make it look like a native app (Hides Deploy, Running, and Menu)
# # #     cmd = [
# # #         sys.executable, "-m", "streamlit", "run", script_path,
# # #         "--server.headless", "true",
# # #         "--client.toolbarMode", "minimal",
# # #         "--browser.gatherUsageStats", "false"  # Privacy
# # #     ]

# # #     # Start the Streamlit server
# # #     # 'cwd=app_path' is critical so it finds ingestion_gui.py and db.py
# # #     process = subprocess.Popen(cmd, env=env, cwd=app_path)
    
# # #     try:
# # #         process.wait()
# # #     except KeyboardInterrupt:
# # #         process.terminate()

# # # if __name__ == "__main__":
# # #     main()

# # import os
# # import sys
# # import subprocess
# # import time
# # import socket
# # import signal

# # def kill_port(port):
# #     try:
# #         result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
# #         if result.returncode == 0 and result.stdout.strip():
# #             for pid in result.stdout.strip().split('\n'):
# #                 try:
# #                     os.kill(int(pid), signal.SIGTERM)
# #                 except (ProcessLookupError, ValueError):
# #                     pass
# #     except Exception:
# #         pass

# # def is_port_open(port, host='127.0.0.1'):
# #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
# #         return s.connect_ex((host, port)) == 0

# # def main():
# #     PORT = 8502
# #     kill_port(PORT)

# #     is_frozen = getattr(sys, 'frozen', False)
    
# #     if is_frozen:
# #         res_path = os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..', 'Resources'))
# #         app_path = os.path.join(res_path, 'XINSIGHT_Application')
# #         script_path = os.path.join(app_path, 'home_grid.py')
        
# #         # Point to bundled site-packages
# #         site_packages = os.path.join(res_path, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
# #         env = os.environ.copy()
# #         env['PYTHONPATH'] = site_packages + ':' + env.get('PYTHONPATH', '')
# #         env["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
# #         env["STREAMLIT_RUNTIME_ENV"] = "production"
# #         env["BROWSER"] = ""  # Prevent Streamlit from auto-opening browser (you can do it manually if needed)
# #     else:
# #         app_path = os.path.dirname(os.path.abspath(__file__))
# #         script_path = os.path.join(app_path, 'home_grid.py')
# #         env = os.environ.copy()

# #     cmd = [
# #         sys.executable, "-m", "streamlit", "run", script_path,
# #         f"--server.port={PORT}",
# #         "--server.headless=true",
# #         "--client.toolbarMode=minimal",
# #         "--browser.gatherUsageStats=false"
# #     ]

# #     # Log to file for debugging (critical for .app bundles)
# #     log_path = os.path.expanduser("~/Library/Logs/XInsight_streamlit.log")
# #     os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
# #     with open(log_path, "w") as log_file:
# #         process = subprocess.Popen(
# #             cmd,
# #             env=env,
# #             cwd=app_path,
# #             stdout=log_file,
# #             stderr=subprocess.STDOUT
# #         )

# #     # Optional: wait for server to start
# #     for _ in range(20):
# #         if is_port_open(PORT):
# #             break
# #         time.sleep(0.5)

# #     try:
# #         process.wait()
# #     except KeyboardInterrupt:
# #         process.terminate()

# # if __name__ == "__main__":
# #     main()

import os
from subprocess import Popen, PIPE, STDOUT
import sys
import time
import webbrowser

def main():
    # Getting path to python executable
    executable = sys.executable
    
    # Determine the correct path to home_grid.py
    if getattr(sys, 'frozen', False):
        # Running as frozen app (py2app)
        # py2app structure: XInsight.app/Contents/MacOS/XInsight
        #                   XInsight.app/Contents/Resources/XINSIGHT_Application/home_grid.py
        bundle_dir = os.path.dirname(sys.executable)  # MacOS folder
        contents_dir = os.path.dirname(bundle_dir)     # Contents folder
        resources_dir = os.path.join(contents_dir, 'Resources')
        
        # Try multiple possible locations
        possible_paths = [
            os.path.join(resources_dir, 'XINSIGHT_Application', 'home_grid.py'),
            os.path.join(resources_dir, 'home_grid.py'),
        ]
        
        path_to_main = None
        for path in possible_paths:
            if os.path.exists(path):
                path_to_main = path
                print(f"Found home_grid.py at: {path}")
                break
        
        if not path_to_main:
            print("ERROR: Could not find home_grid.py")
            print(f"Searched in:")
            for path in possible_paths:
                print(f"  - {path}")
            print(f"\nResources directory contents:")
            if os.path.exists(resources_dir):
                for item in os.listdir(resources_dir)[:20]:
                    print(f"  - {item}")
            input("Press Enter to exit...")
            return
    else:
        # Running normally (not frozen)
        path_to_main = os.path.join(os.path.dirname(__file__), "home_grid.py")
    
    print(f"Starting Streamlit with: {path_to_main}")
    print(f"File exists: {os.path.exists(path_to_main)}")
    
    # Running streamlit server in a subprocess
    proc = Popen(
        [
            executable,
            "-m",
            "streamlit",
            "run",
            path_to_main,
            "--server.headless=true",
            "--global.developmentMode=false",
            "--server.maxMessageSize=1000",
            "--server.port=8502",
            "--client.toolbarMode=minimal",
        ],
        stdin=PIPE,
        stdout=PIPE,
        stderr=STDOUT,
        text=True,
    )
    proc.stdin.close()
    
    # Wait for server to start and monitor output
    print("Starting Streamlit server...")
    time.sleep(3)
    
    # Open browser
    webbrowser.open("http://localhost:8502")
    
    # Keep showing output
    while True:
        s = proc.stdout.read()
        if not s:
            break
        print(s, end="")
    
    proc.wait()

if __name__ == "__main__":
    main()