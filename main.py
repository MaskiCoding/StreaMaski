"""
Streamlink Maski - Lightweight Twitch Stream Viewer
A minimal desktop GUI for watching ad-free Twitch streams using Streamlink
"""

import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import subprocess
import threading
import re
import os
import sys
import json
import webbrowser
from urllib.parse import urlparse, parse_qs
import requests
import time
from datetime import datetime

# Rose Pine Color Theme
class RosePineTheme:
    # Rose Pine colors
    BASE = "#191724"
    SURFACE = "#1f1d2e"
    OVERLAY = "#26233a"
    MUTED = "#6e6a86"
    SUBTLE = "#908caa"
    TEXT = "#e0def4"
    LOVE = "#eb6f92"
    GOLD = "#f6c177"
    ROSE = "#ebbcba"
    PINE = "#31748f"
    FOAM = "#9ccfd8"
    IRIS = "#c4a7e7"
    HIGHLIGHT_LOW = "#21202e"
    HIGHLIGHT_MED = "#403d52"
    HIGHLIGHT_HIGH = "#524f67"

class StreamlinkMaski:
    def __init__(self):
        self.root = ctk.CTk()
        self.current_process = None
        self.is_streaming = False
        self.twitch_token = None
        self.followed_channels = []
        
        # Configure CustomTkinter theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup the main user interface"""
        self.root.title("Streamlink Maski")
        self.root.geometry("600x500")
        self.root.configure(fg_color=RosePineTheme.BASE)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main frame
        main_frame = ctk.CTkFrame(
            self.root, 
            fg_color=RosePineTheme.SURFACE,
            border_color=RosePineTheme.HIGHLIGHT_MED,
            border_width=1
        )
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🎭 Streamlink Maski",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=RosePineTheme.ROSE
        )
        title_label.grid(row=0, column=0, pady=(20, 30))
        
        # URL Input Section
        url_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        url_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        url_frame.grid_columnconfigure(0, weight=1)
        
        url_label = ctk.CTkLabel(
            url_frame,
            text="Twitch Stream URL:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=RosePineTheme.TEXT
        )
        url_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="https://www.twitch.tv/streamer_name",
            font=ctk.CTkFont(size=12),
            fg_color=RosePineTheme.OVERLAY,
            border_color=RosePineTheme.HIGHLIGHT_MED,
            text_color=RosePineTheme.TEXT,
            height=40
        )
        self.url_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Quality Selection
        quality_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        quality_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        quality_frame.grid_columnconfigure(0, weight=1)
        
        quality_label = ctk.CTkLabel(
            quality_frame,
            text="Stream Quality:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=RosePineTheme.TEXT
        )
        quality_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.quality_var = tk.StringVar(value="best")
        self.quality_combo = ctk.CTkComboBox(
            quality_frame,
            values=["best", "1080p60", "1080p", "720p60", "720p", "480p", "360p", "worst"],
            variable=self.quality_var,
            font=ctk.CTkFont(size=12),
            fg_color=RosePineTheme.OVERLAY,
            border_color=RosePineTheme.HIGHLIGHT_MED,
            button_color=RosePineTheme.PINE,
            button_hover_color=RosePineTheme.FOAM,
            text_color=RosePineTheme.TEXT,
            height=40
        )
        self.quality_combo.grid(row=1, column=0, sticky="ew")
        
        # Control Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.watch_button = ctk.CTkButton(
            button_frame,
            text="🎬 Watch Stream",
            command=self.start_stream,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=RosePineTheme.PINE,
            hover_color=RosePineTheme.FOAM,
            text_color=RosePineTheme.BASE,
            height=45
        )
        self.watch_button.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.switch_button = ctk.CTkButton(
            button_frame,
            text="🔄 Switch Stream",
            command=self.switch_stream,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=RosePineTheme.LOVE,
            hover_color=RosePineTheme.ROSE,
            text_color=RosePineTheme.BASE,
            height=45
        )
        self.switch_button.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # Status Section
        status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        status_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Status: Ready",
            font=ctk.CTkFont(size=12),
            text_color=RosePineTheme.SUBTLE
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        # Twitch Integration Section
        twitch_frame = ctk.CTkFrame(
            main_frame,
            fg_color=RosePineTheme.OVERLAY,
            border_color=RosePineTheme.HIGHLIGHT_MED,
            border_width=1
        )
        twitch_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
        twitch_frame.grid_columnconfigure(0, weight=1)
        
        twitch_label = ctk.CTkLabel(
            twitch_frame,
            text="🎮 Twitch Integration",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=RosePineTheme.IRIS
        )
        twitch_label.grid(row=0, column=0, pady=(15, 10))
        
        twitch_button_frame = ctk.CTkFrame(twitch_frame, fg_color="transparent")
        twitch_button_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        twitch_button_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.login_button = ctk.CTkButton(
            twitch_button_frame,
            text="🔑 Login to Twitch",
            command=self.twitch_login,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=RosePineTheme.IRIS,
            hover_color=RosePineTheme.LOVE,
            text_color=RosePineTheme.BASE,
            height=35
        )
        self.login_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.channels_button = ctk.CTkButton(
            twitch_button_frame,
            text="📺 View Followed",
            command=self.show_followed_channels,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=RosePineTheme.GOLD,
            hover_color=RosePineTheme.ROSE,
            text_color=RosePineTheme.BASE,
            height=35,
            state="disabled"
        )
        self.channels_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
    def validate_url(self, url):
        """Validate Twitch URL format"""
        if not url:
            return False, "Please enter a Twitch stream URL"
        
        # Basic URL validation
        twitch_pattern = r'^https?://(?:www\.)?twitch\.tv/[a-zA-Z0-9_]+/?$'
        if not re.match(twitch_pattern, url):
            return False, "Invalid Twitch URL format. Use: https://www.twitch.tv/streamer_name"
        
        return True, ""
    
    def start_stream(self):
        """Start streaming with Streamlink"""
        if self.is_streaming:
            messagebox.showwarning("Already Streaming", "A stream is already running. Use 'Switch Stream' to change streams.")
            return
        
        url = self.url_entry.get().strip()
        quality = self.quality_var.get()
        
        # Validate URL
        is_valid, error_msg = self.validate_url(url)
        if not is_valid:
            messagebox.showerror("Invalid URL", error_msg)
            return
        
        # Check if Streamlink is available
        if not self.check_streamlink():
            messagebox.showerror("Streamlink Not Found", 
                               "Streamlink is not installed or not in PATH. Please install Streamlink first.")
            return
        
        # Start streaming in a separate thread
        self.update_status("Starting stream...")
        self.watch_button.configure(state="disabled")
        
        thread = threading.Thread(target=self._run_streamlink, args=(url, quality))
        thread.daemon = True
        thread.start()
    
    def _run_streamlink(self, url, quality):
        """Run Streamlink in a separate thread"""
        try:
            cmd = [
                "streamlink",
                "--twitch-proxy-playlist=https://eu.luminous.dev",
                url,
                quality
            ]
            
            # Run without showing console window
            startupinfo = None
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo
            )
            
            self.is_streaming = True
            self.root.after(0, lambda: self.update_status(f"Streaming: {url} ({quality})"))
            self.root.after(0, lambda: self.watch_button.configure(state="normal"))
            
            # Wait for process to complete
            stdout, stderr = self.current_process.communicate()
            
            if self.current_process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error occurred"
                self.root.after(0, lambda: messagebox.showerror("Stream Error", f"Stream failed to start:\n{error_msg}"))
                self.root.after(0, lambda: self.update_status("Stream failed"))
            else:
                self.root.after(0, lambda: self.update_status("Stream ended"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start stream:\n{str(e)}"))
            self.root.after(0, lambda: self.update_status("Error occurred"))
        finally:
            self.is_streaming = False
            self.current_process = None
            self.root.after(0, lambda: self.watch_button.configure(state="normal"))
    
    def switch_stream(self):
        """Switch to a different stream"""
        if self.is_streaming and self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
            except Exception as e:
                print(f"Error terminating process: {e}")
            finally:
                self.is_streaming = False
                self.current_process = None
                self.update_status("Stream stopped")
        
        # Clear the URL field for new input
        self.url_entry.delete(0, tk.END)
        self.url_entry.focus()
        
        messagebox.showinfo("Stream Switched", "Previous stream stopped. Enter a new URL and click 'Watch Stream'.")
    
    def check_streamlink(self):
        """Check if Streamlink is installed and accessible"""
        try:
            result = subprocess.run(
                ["streamlink", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def update_status(self, message):
        """Update the status label"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_label.configure(text=f"Status: {message} ({timestamp})")
    
    def twitch_login(self):
        """Handle Twitch OAuth login"""
        # For now, show a placeholder message
        messagebox.showinfo("Coming Soon", 
                          "Twitch OAuth integration will be implemented in the next version.\n"
                          "This feature will allow you to:\n"
                          "• Login with your Twitch account\n"
                          "• View your followed channels\n"
                          "• Quick access to live streams")
    
    def show_followed_channels(self):
        """Show followed channels (placeholder)"""
        messagebox.showinfo("Coming Soon", "This feature will display your followed channels that are currently live.")
    
    def load_settings(self):
        """Load user settings from file"""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    self.url_entry.insert(0, settings.get("last_url", ""))
                    self.quality_var.set(settings.get("last_quality", "best"))
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save user settings to file"""
        try:
            settings = {
                "last_url": self.url_entry.get(),
                "last_quality": self.quality_var.get()
            }
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        self.save_settings()
        
        # Terminate any running stream
        if self.is_streaming and self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
            except Exception as e:
                print(f"Error terminating process: {e}")
        
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Main entry point"""
    app = StreamlinkMaski()
    app.run()

if __name__ == "__main__":
    main()
