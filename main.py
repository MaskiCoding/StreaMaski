"""
Streamlink Maski - Lightweight Twitch Stream Viewer
A minimal desktop GUI for watching ad-free Twitch streams using Streamlink

Version: 2.0.0
Author: MaskiCoding
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import subprocess
import threading
import time
import re
import os
import json
from typing import List, Tuple, Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum


# Application Constants
APP_NAME = "Streamlink Maski"
APP_VERSION = "2.0.0"
WINDOW_SIZE = "480x440"
SETTINGS_FILE = "settings.json"
PROXY_URL = "https://eu.luminous.dev"
MAX_SWAP_STREAMS = 4
QUALITY_OPTIONS = ["best", "1080p60", "1080p", "720p60", "720p", "480p", "360p", "worst"]

# UI Constants
BUTTON_HEIGHT = 45
SMALL_BUTTON_HEIGHT = 36
BUTTON_PADDING = 8
SECTION_PADDING = 15
MAIN_PADDING = 20

# Common Streamlink installation paths
STREAMLINK_PATHS = [
    "streamlink",
    r"C:\Program Files\Streamlink\bin\streamlink.exe",
    r"C:\Program Files (x86)\Streamlink\bin\streamlink.exe",
    "streamlink.exe"
]

# User-specific paths (expanded at runtime)
USER_STREAMLINK_PATHS = [
    "~\\AppData\\Local\\Programs\\Streamlink\\bin\\streamlink.exe",
    "~\\AppData\\Roaming\\Python\\Scripts\\streamlink.exe"
]


class StreamState(Enum):
    """Stream state enumeration"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class UIConfig:
    """UI configuration dataclass"""
    window_size: str = WINDOW_SIZE
    button_height: int = BUTTON_HEIGHT
    small_button_height: int = SMALL_BUTTON_HEIGHT
    padding: int = SECTION_PADDING
    main_padding: int = MAIN_PADDING


class Theme:
    """Rose Pine Color Theme - Centralized color management"""
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
    HIGHLIGHT_MED = "#403d52"


class ProcessUtils:
    """Utility class for subprocess management with invisible windows"""
    
    @staticmethod
    def get_subprocess_config():
        """Get subprocess configuration for invisible windows on Windows"""
        if os.name != 'nt':
            return None, 0
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return startupinfo, subprocess.CREATE_NO_WINDOW
    
    @staticmethod
    def run_hidden_command(cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Run a command with hidden window"""
        startupinfo, creationflags = ProcessUtils.get_subprocess_config()
        return subprocess.run(
            cmd,
            startupinfo=startupinfo,
            creationflags=creationflags,
            **kwargs
        )
    
    @staticmethod
    def create_hidden_process(cmd: List[str], **kwargs) -> subprocess.Popen:
        """Create a process with hidden window"""
        startupinfo, creationflags = ProcessUtils.get_subprocess_config()
        return subprocess.Popen(
            cmd,
            startupinfo=startupinfo,
            creationflags=creationflags,
            **kwargs
        )


class StreamlinkService:
    """Service for managing Streamlink operations with improved path discovery and caching"""
    
    def __init__(self):
        self.path = "streamlink"
        self.proxy_url = PROXY_URL
        self._is_available = None  # Cache availability check
        self._discover_path()
    
    def _discover_path(self) -> None:
        """Discover Streamlink installation path with better error handling"""
        # Check common paths first
        paths_to_check = STREAMLINK_PATHS + [
            os.path.expanduser(path) for path in USER_STREAMLINK_PATHS
        ]
        
        for path in paths_to_check:
            if self._test_path(path):
                self.path = path
                self._is_available = True
                return
        
        self._is_available = False
    
    def _test_path(self, path: str) -> bool:
        """Test if Streamlink path is valid with improved error handling"""
        try:
            result = ProcessUtils.run_hidden_command(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def is_available(self) -> bool:
        """Check if Streamlink is available (cached result)"""
        if self._is_available is None:
            self._is_available = self._test_path(self.path)
        return self._is_available
    
    def create_command(self, url: str, quality: str) -> List[str]:
        """Create Streamlink command with proxy configuration"""
        return [
            self.path,
            f"--twitch-proxy-playlist={self.proxy_url}",
            url,
            quality
        ]


class StreamManager:
    """Manages stream processes and state with improved error handling"""
    
    def __init__(self, streamlink_service: StreamlinkService):
        self.streamlink = streamlink_service
        self.current_process: Optional[subprocess.Popen] = None
        self.state = StreamState.STOPPED
        self.manually_stopped = False
        self._callbacks: Dict[str, Callable] = {}
    
    def set_callback(self, event: str, callback: Callable) -> None:
        """Set event callback with type safety"""
        self._callbacks[event] = callback
    
    def _emit(self, event: str, *args) -> None:
        """Emit event to callback with error handling"""
        if event in self._callbacks:
            try:
                self._callbacks[event](*args)
            except Exception as e:
                print(f"Error in callback for {event}: {e}")
    
    def is_running(self) -> bool:
        """Check if stream is currently running"""
        return self.state == StreamState.RUNNING
    
    def get_state(self) -> StreamState:
        """Get current stream state"""
        return self.state
    
    def _set_state(self, state: StreamState) -> None:
        """Set stream state and emit event"""
        self.state = state
        self._emit(f'state_changed', state)
    
    def switch_stream(self, url: str, quality: str) -> bool:
        """Switch to a different stream"""
        if self.is_running():
            self.stop_stream()
            time.sleep(0.5)  # Allow cleanup time
        
        return self.start_stream(url, quality)
    
    def start_stream(self, url: str, quality: str) -> bool:
        """Start streaming with improved validation"""
        if self.is_running():
            return False
        
        if not self.streamlink.is_available():
            self._emit('error', 'Streamlink not found. Please install Streamlink.')
            return False
        
        self._set_state(StreamState.STARTING)
        self.manually_stopped = False
        cmd = self.streamlink.create_command(url, quality)
        
        thread = threading.Thread(
            target=self._run_stream, 
            args=(cmd,),
            daemon=True
        )
        thread.start()
        
        return True
    
    def stop_stream(self) -> None:
        """Stop current stream with improved cleanup"""
        if not self.is_running() or not self.current_process:
            return
        
        self._set_state(StreamState.STOPPING)
        self.manually_stopped = True
        
        try:
            self.current_process.terminate()
            try:
                self.current_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
                self.current_process.wait()
            
            # Close media players on Windows
            if os.name == 'nt':
                self._close_media_players()
                
        except Exception as e:
            print(f"Error stopping stream: {e}")
        finally:
            self._cleanup()
    
    def _run_stream(self, cmd: List[str]) -> None:
        """Run stream in background thread with better error handling"""
        try:
            self.current_process = ProcessUtils.create_hidden_process(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self._set_state(StreamState.RUNNING)
            url, quality = self._extract_stream_info(cmd)
            self._emit('started', url, quality)
            
            stdout, stderr = self.current_process.communicate()
            
            if self.current_process.returncode != 0 and not self.manually_stopped:
                error_msg = self._parse_error_message(stderr)
                self._emit('error', f"Stream failed: {error_msg}")
                
        except Exception as e:
            if not self.manually_stopped:
                self._emit('error', f"Failed to start stream: {str(e)}")
        finally:
            self._cleanup()
    
    def _extract_stream_info(self, cmd: List[str]) -> Tuple[str, str]:
        """Extract URL and quality from command with better parsing"""
        url = cmd[2] if len(cmd) > 2 else ""  # URL is after proxy parameter
        quality = cmd[3] if len(cmd) > 3 else "best"  # Quality is last parameter
        return url, quality
    
    def _parse_error_message(self, stderr: bytes) -> str:
        """Parse and clean error messages for better user experience"""
        if not stderr:
            return "Unknown error occurred"
        
        error_msg = stderr.decode('utf-8', errors='ignore').strip()
        
        # Map of error patterns to user-friendly messages
        error_mappings = {
            "No playable streams found": "Stream not found or offline",
            "Unable to open URL": "Unable to connect to stream",
            "Authentication failed": "Stream requires authentication",
            "Network is unreachable": "Network connection error",
            "Connection timed out": "Connection timeout - try again"
        }
        
        # Check for known error patterns
        for pattern, friendly_msg in error_mappings.items():
            if pattern in error_msg:
                return friendly_msg
        
        return error_msg
    
    def _close_media_players(self) -> None:
        """Close media player windows with improved error handling"""
        if os.name != 'nt':
            return  # Only applies to Windows
        
        players = ['vlc.exe', 'wmplayer.exe', 'mpv.exe']
        for player in players:
            try:
                ProcessUtils.run_hidden_command(
                    ['taskkill', '/F', '/IM', player],
                    capture_output=True,
                    timeout=5
                )
            except Exception:
                continue  # Ignore individual player close failures
    
    def _cleanup(self) -> None:
        """Clean up stream state"""
        self._set_state(StreamState.STOPPED)
        self.current_process = None
        self.manually_stopped = False
        self._emit('stopped')


class URLValidator:
    """Validates Twitch URLs with enhanced validation and caching"""
    
    # Compiled regex pattern for better performance
    TWITCH_URL_PATTERN = re.compile(
        r'^https?://(?:www\.)?twitch\.tv/([a-zA-Z0-9_]{4,25})/?$',
        re.IGNORECASE
    )
    
    # Cache for validation results to improve performance
    _validation_cache: Dict[str, Tuple[bool, str]] = {}
    _cache_size_limit = 100
    
    @classmethod
    def validate(cls, url: str) -> Tuple[bool, str]:
        """Validate Twitch URL format with caching for performance"""
        if not url:
            return False, "Please enter a Twitch stream URL"
        
        url = url.strip()
        
        # Check cache first
        if url in cls._validation_cache:
            return cls._validation_cache[url]
        
        # Validate URL
        result = cls._validate_url(url)
        
        # Cache result (with size limit)
        if len(cls._validation_cache) >= cls._cache_size_limit:
            # Remove oldest entry
            cls._validation_cache.pop(next(iter(cls._validation_cache)))
        cls._validation_cache[url] = result
        
        return result
    
    @classmethod
    def _validate_url(cls, url: str) -> Tuple[bool, str]:
        """Internal URL validation logic"""
        if not cls.TWITCH_URL_PATTERN.match(url):
            if 'twitch.tv' not in url.lower():
                return False, "URL must be from Twitch (twitch.tv)"
            elif not url.startswith(('http://', 'https://')):
                return False, "URL must start with http:// or https://"
            else:
                return False, "Invalid Twitch URL format.\nExample: https://www.twitch.tv/streamer_name"
        
        return True, ""
    
    @classmethod
    def extract_streamer_name(cls, url: str) -> str:
        """Extract streamer name from Twitch URL with validation"""
        if not url:
            return ""
        
        match = cls.TWITCH_URL_PATTERN.match(url.strip())
        return match.group(1).capitalize() if match else ""
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """Normalize Twitch URL to standard format"""
        if not url:
            return ""
        
        url = url.strip()
        match = cls.TWITCH_URL_PATTERN.match(url)
        if match:
            streamer_name = match.group(1).lower()  # Store in lowercase for consistency
            return f"https://www.twitch.tv/{streamer_name}"
        
        return url
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the validation cache"""
        cls._validation_cache.clear()


class SettingsManager:
    """Manages application settings with improved error handling and validation"""
    
    def __init__(self, settings_file: str = SETTINGS_FILE):
        self.settings_file = settings_file
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file with error recovery"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Validate loaded settings
                    return self._validate_settings(loaded_settings)
        except (json.JSONDecodeError, IOError, OSError) as e:
            print(f"Error loading settings: {e}")
            # Backup corrupted settings
            self._backup_corrupted_settings()
        
        return self._get_default_settings()
    
    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate loaded settings and merge with defaults"""
        defaults = self._get_default_settings()
        
        # Ensure all required keys exist
        for key, default_value in defaults.items():
            if key not in settings:
                settings[key] = default_value
        
        # Validate specific settings
        if not isinstance(settings.get("quick_swap_streams"), list):
            settings["quick_swap_streams"] = []
        
        if settings.get("last_quality") not in QUALITY_OPTIONS:
            settings["last_quality"] = "best"
        
        return settings
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings with type annotations"""
        return {
            "last_url": "",
            "last_quality": "best",
            "last_streamer_name": "",
            "quick_swap_streams": [],
            "app_version": APP_VERSION
        }
    
    def _backup_corrupted_settings(self) -> None:
        """Backup corrupted settings file"""
        if os.path.exists(self.settings_file):
            backup_file = f"{self.settings_file}.backup"
            try:
                os.rename(self.settings_file, backup_file)
                print(f"Corrupted settings backed up to {backup_file}")
            except OSError:
                pass
    
    def save(self) -> bool:
        """Save settings to file with error handling"""
        try:
            # Update app version
            self.settings["app_version"] = APP_VERSION
            
            with open(self.settings_file, "w", encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, OSError) as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default=None) -> Any:
        """Get setting value with default fallback"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set setting value with automatic save"""
        self.settings[key] = value
        return self.save()
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        self.settings = self._get_default_settings()
        return self.save()


class QuickSwapManager:
    """Manages quick swap streams with improved validation and limits"""
    
    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        self.max_streams = MAX_SWAP_STREAMS
        self._normalized_cache: Dict[str, str] = {}  # Cache for normalized URLs
        self.streams = self._validate_streams(
            self.settings.get("quick_swap_streams", [])
        )
    
    def _validate_streams(self, streams: List[str]) -> List[str]:
        """Validate and clean stream URLs"""
        validated_streams = []
        seen_urls = set()
        
        for url in streams:
            if URLValidator.validate(url)[0]:
                normalized_url = self._get_normalized_url(url)
                if normalized_url not in seen_urls:
                    validated_streams.append(normalized_url)
                    seen_urls.add(normalized_url)
        
        return validated_streams[:self.max_streams]
    
    def _get_normalized_url(self, url: str) -> str:
        """Get normalized URL with caching"""
        if url not in self._normalized_cache:
            self._normalized_cache[url] = URLValidator.normalize_url(url)
        return self._normalized_cache[url]
    
    def _save_streams(self) -> bool:
        """Save streams to settings"""
        return self.settings.set("quick_swap_streams", self.streams)
    
    def add_stream(self, url: str) -> bool:
        """Add stream to quick swap with validation"""
        if not url or len(self.streams) >= self.max_streams:
            return False
        
        normalized_url = self._get_normalized_url(url)
        
        if normalized_url in self.streams:
            return False
        
        self.streams.append(normalized_url)
        return self._save_streams()
    
    def remove_stream(self, url: str) -> bool:
        """Remove stream from quick swap"""
        normalized_url = self._get_normalized_url(url)
        
        if normalized_url not in self.streams:
            return False
        
        self.streams.remove(normalized_url)
        return self._save_streams()
    
    def remove_by_index(self, index: int) -> bool:
        """Remove stream by index with bounds checking"""
        if not self.is_valid_index(index):
            return False
        
        self.streams.pop(index)
        return self._save_streams()
    
    def get_stream(self, index: int) -> Optional[str]:
        """Get stream by index with bounds checking"""
        return self.streams[index] if self.is_valid_index(index) else None
    
    def get_streams(self) -> List[str]:
        """Get all streams as a copy"""
        return self.streams.copy()
    
    def is_full(self) -> bool:
        """Check if swap manager is at capacity"""
        return len(self.streams) >= self.max_streams
    
    def get_available_slots(self) -> int:
        """Get number of available slots"""
        return self.max_streams - len(self.streams)
    
    def is_valid_index(self, index: int) -> bool:
        """Check if index is valid for current streams"""
        return 0 <= index < len(self.streams)
    
    def has_stream(self, url: str) -> bool:
        """Check if stream URL already exists in quick swap"""
        normalized_url = self._get_normalized_url(url)
        return normalized_url in self.streams


class StreamlinkMaski:
    """Main application class with improved organization and error handling"""
    
    def __init__(self):
        # Initialize configuration
        self.ui_config = UIConfig()
        
        # Initialize services with dependency injection
        self.streamlink_service = StreamlinkService()
        self.settings_manager = SettingsManager()
        self.quick_swap_manager = QuickSwapManager(self.settings_manager)
        self.stream_manager = StreamManager(self.streamlink_service)
        
        # Setup callbacks
        self._setup_callbacks()
        
        # Initialize UI
        self.root = ctk.CTk()
        self._setup_theme()
        self._setup_window()
        self._setup_ui()
        self._load_initial_settings()
    
    def _setup_callbacks(self) -> None:
        """Setup all event callbacks"""
        self.stream_manager.set_callback('started', self._on_stream_started)
        self.stream_manager.set_callback('stopped', self._on_stream_stopped)
        self.stream_manager.set_callback('error', self._on_stream_error)
    
    def _setup_theme(self) -> None:
        """Setup application theme"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    def _setup_window(self) -> None:
        """Setup main window properties"""
        self.root.title(APP_NAME)
        self.root.geometry(self.ui_config.window_size)
        self.root.configure(fg_color=Theme.BASE)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configure main grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def _create_frame(self, parent, fg_color="transparent", **kwargs) -> ctk.CTkFrame:
        """Utility method to create frames with consistent styling"""
        return ctk.CTkFrame(parent, fg_color=fg_color, **kwargs)
    
    def _create_button(self, parent, text: str, command: Callable, 
                      height: int = None, **kwargs) -> ctk.CTkButton:
        """Utility method to create buttons with consistent styling"""
        height = height or self.ui_config.button_height
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=height,
            font=ctk.CTkFont(size=12, weight="bold"),
            **kwargs
        )
    
    def _create_label(self, parent, text: str, size: int = 12, **kwargs) -> ctk.CTkLabel:
        """Utility method to create labels with consistent styling"""
        # Remove text_color from kwargs if present to avoid conflicts
        kwargs.pop('text_color', None)
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=size, weight="bold"),
            text_color=Theme.TEXT,
            **kwargs
        )
    
    def _create_ui_elements(self) -> None:
        """Create all UI elements in order"""
        self._create_title()
        self._create_url_section()
        self._create_control_buttons()
        self._create_management_buttons()
        self._create_swap_section()
    
    def _setup_ui(self) -> None:
        """Setup the main user interface"""
        # Main frame
        self.main_frame = self._create_frame(
            self.root,
            fg_color=Theme.SURFACE,
            border_color=Theme.HIGHLIGHT_MED,
            border_width=1
        )
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Create UI elements
        self._create_ui_elements()
    
    def _create_standard_button(self, parent, text: str, command: Callable, 
                              height: int = None, colors: Dict[str, str] = None, **kwargs) -> ctk.CTkButton:
        """Create button with standard styling and custom colors"""
        height = height or self.ui_config.button_height
        colors = colors or {"fg_color": Theme.PINE, "hover_color": Theme.FOAM, "text_color": Theme.BASE}
        
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=height,
            font=ctk.CTkFont(size=12, weight="bold"),
            **colors,
            **kwargs
        )
    
    def _create_title(self) -> None:
        """Create title label with version info"""
        title_label = self._create_label(
            self.main_frame,
            text=f"🎭 {APP_NAME}",
            size=22,
            text_color=Theme.ROSE
        )
        title_label.grid(row=0, column=0, pady=(15, 20))
    
    def _create_url_section(self) -> None:
        """Create URL input section with improved layout"""
        url_frame = self._create_frame(self.main_frame)
        url_frame.grid(row=1, column=0, sticky="ew", padx=self.ui_config.main_padding, pady=(0, 15))
        url_frame.grid_columnconfigure(0, weight=1)
        
        # URL label
        url_label = self._create_label(url_frame, "Twitch Stream URL:")
        url_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Input row
        input_row = self._create_frame(url_frame)
        input_row.grid(row=1, column=0, sticky="ew")
        input_row.grid_columnconfigure(0, weight=1)
        
        # URL entry with improved placeholder
        self.url_entry = ctk.CTkEntry(
            input_row,
            placeholder_text="https://www.twitch.tv/streamer_name",
            font=ctk.CTkFont(size=11),
            fg_color=Theme.OVERLAY,
            border_color=Theme.HIGHLIGHT_MED,
            text_color=Theme.TEXT,
            height=32
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Quality selection with all options
        self.quality_var = tk.StringVar(value="best")
        self.quality_combo = ctk.CTkComboBox(
            input_row,
            values=QUALITY_OPTIONS,
            variable=self.quality_var,
            font=ctk.CTkFont(size=10),
            fg_color=Theme.OVERLAY,
            border_color=Theme.HIGHLIGHT_MED,
            button_color=Theme.PINE,
            button_hover_color=Theme.FOAM,
            text_color=Theme.TEXT,
            height=32,
            width=120,
            state="readonly"
        )
        self.quality_combo.grid(row=0, column=1)
    
    def _create_control_buttons(self) -> None:
        """Create control buttons with improved organization"""
        self.button_frame = self._create_frame(self.main_frame)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=self.ui_config.main_padding, pady=(0, 15))
        self.button_frame.grid_columnconfigure(0, weight=1)
        
        # Watch button
        self.watch_button = self._create_standard_button(
            self.button_frame,
            text="🎬 Watch Stream",
            command=self._toggle_stream
        )
        self.watch_button.grid(row=0, column=0, sticky="ew", pady=(0, self.ui_config.padding // 2))
        
        # Stop/Switch buttons row
        self.control_row = self._create_frame(self.button_frame)
        self.control_row.grid(row=1, column=0, sticky="ew")
        self.control_row.grid_columnconfigure(0, weight=1)
        self.control_row.grid_columnconfigure(1, weight=1)
        
        # Color schemes for different button types
        stop_colors = {"fg_color": Theme.LOVE, "hover_color": Theme.ROSE, "text_color": Theme.BASE}
        switch_colors = {"fg_color": Theme.GOLD, "hover_color": Theme.ROSE, "text_color": Theme.BASE}
        
        self.stop_button = self._create_standard_button(
            self.control_row,
            text="⏹ Stop Stream",
            command=self._stop_stream,
            colors=stop_colors
        )
        self.stop_button.grid(row=0, column=0, sticky="ew", padx=(0, self.ui_config.padding // 2))
        
        self.switch_button = self._create_standard_button(
            self.control_row,
            text="🔄 Switch Stream",
            command=self._switch_stream,
            colors=switch_colors
        )
        self.switch_button.grid(row=0, column=1, sticky="ew", padx=(self.ui_config.padding // 2, 0))
        
        # Initially hide stop/switch buttons
        self.control_row.grid_remove()
    
    def _create_management_buttons(self) -> None:
        """Create stream management buttons"""
        manage_frame = self._create_frame(self.main_frame)
        manage_frame.grid(row=3, column=0, sticky="ew", padx=self.ui_config.main_padding, pady=(0, 15))
        manage_frame.grid_columnconfigure(0, weight=1)
        
        # Add button with improved text
        self.add_button = self._create_standard_button(
            manage_frame,
            text="➕ Add to Quick Swap",
            command=self._add_stream,
            height=self.ui_config.small_button_height
        )
        self.add_button.grid(row=0, column=0, sticky="ew")
    
    def _create_swap_section(self) -> None:
        """Create swap streams section with improved layout"""
        # Swap frame (removed header label)
        swap_frame = self._create_frame(self.main_frame)
        swap_frame.grid(row=4, column=0, sticky="ew", padx=self.ui_config.main_padding, pady=(0, 15))
        swap_frame.grid_columnconfigure(0, weight=1)
        swap_frame.grid_columnconfigure(1, weight=1)
        
        # Create swap buttons
        self.swap_buttons = []
        self.remove_buttons = []
        
        for i in range(MAX_SWAP_STREAMS):
            self._create_swap_button_pair(swap_frame, i)
    
    def _create_swap_button_pair(self, parent_frame: ctk.CTkFrame, index: int) -> None:
        """Create a swap button with its remove button"""
        row = index // 2
        col = index % 2
        
        # Container for each swap button
        button_container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        button_container.grid(
            row=row, 
            column=col, 
            sticky="ew", 
            padx=(0, 8) if col == 0 else (8, 0), 
            pady=(0, 8) if row == 0 else (8, 0)
        )
        button_container.grid_columnconfigure(0, weight=1)
        button_container.grid_columnconfigure(1, weight=0)
        
        # Main swap button
        swap_button = ctk.CTkButton(
            button_container,
            text="Empty Slot",
            command=lambda idx=index: self._load_swap_stream(idx),
            font=ctk.CTkFont(size=10),
            fg_color=Theme.MUTED,
            hover_color=Theme.SUBTLE,
            text_color=Theme.TEXT,
            height=45,
            state="disabled"
        )
        swap_button.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        self.swap_buttons.append(swap_button)
        
        # Remove button with predefined colors
        remove_colors = {"fg_color": Theme.LOVE, "hover_color": Theme.ROSE, "text_color": Theme.BASE}
        remove_button = ctk.CTkButton(
            button_container,
            text="✕",
            command=lambda idx=index: self._remove_swap_stream(idx),
            font=ctk.CTkFont(size=10),
            height=45,
            width=25,
            **remove_colors
        )
        remove_button.grid(row=0, column=1, sticky="ew")
        remove_button.grid_remove()
        self.remove_buttons.append(remove_button)
    
    def _load_initial_settings(self) -> None:
        """Load initial settings with validation"""
        # Load URL
        last_url = self.settings_manager.get("last_url", "")
        if last_url:
            is_valid, _ = URLValidator.validate(last_url)
            if is_valid:
                self.url_entry.insert(0, last_url)
        
        # Load quality
        quality = self.settings_manager.get("last_quality", "best")
        if quality in QUALITY_OPTIONS:
            self.quality_var.set(quality)
        
        # Update swap buttons
        self._update_swap_buttons()
    
    def _update_swap_buttons(self) -> None:
        """Update swap buttons display with better organization"""
        streams = self.quick_swap_manager.get_streams()
        
        # Define button states for better performance
        active_state = {
            "state": "normal",
            "fg_color": Theme.PINE,
            "hover_color": Theme.FOAM,
            "text_color": Theme.BASE
        }
        
        inactive_state = {
            "state": "disabled",
            "fg_color": Theme.MUTED,
            "hover_color": Theme.SUBTLE,
            "text_color": Theme.TEXT
        }
        
        for i, button in enumerate(self.swap_buttons):
            if i < len(streams):
                url = streams[i]
                streamer_name = URLValidator.extract_streamer_name(url)
                button.configure(text=streamer_name, **active_state)
                self.remove_buttons[i].grid()
            else:
                button.configure(text="Empty Slot", **inactive_state)
                self.remove_buttons[i].grid_remove()
    
    def _toggle_stream(self) -> None:
        """Toggle between watching and stopping stream with improved validation"""
        if self.stream_manager.is_running():
            self._stop_stream()
        else:
            self._watch_stream()
    
    def _get_validated_url_and_quality(self) -> Tuple[Optional[str], Optional[str]]:
        """Get and validate URL and quality from UI inputs"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Warning", "Please enter a stream URL")
            return None, None
        
        # Validate URL format
        is_valid, error_msg = URLValidator.validate(url)
        if not is_valid:
            messagebox.showerror("Invalid URL", error_msg)
            return None, None
        
        quality = self.quality_var.get()
        return url, quality
    
    def _validate_and_save_stream_settings(self, url: str, quality: str) -> bool:
        """Validate URL and save settings - common functionality"""
        # Validate URL format
        is_valid, error_msg = URLValidator.validate(url)
        if not is_valid:
            messagebox.showerror("Invalid URL", error_msg)
            return False
        
        # Save current settings
        self.settings_manager.set("last_url", url)
        self.settings_manager.set("last_quality", quality)
        return True
    def _validate_and_execute_stream_action(self, action_name: str, action_func: Callable[[str, str], bool]) -> bool:
        """Common validation and execution pattern for stream actions"""
        url, quality = self._get_validated_url_and_quality()
        if not url or not quality:
            return False
        
        # Validate and save settings
        if not self._validate_and_save_stream_settings(url, quality):
            return False
        
        # Execute the action
        return action_func(url, quality)
    
    def _watch_stream(self) -> None:
        """Watch stream with comprehensive validation and error handling"""
        self._validate_and_execute_stream_action("watch", self.stream_manager.start_stream)
    
    def _stop_stream(self) -> None:
        """Stop stream with proper cleanup"""
        self.stream_manager.stop_stream()
    
    def _switch_stream(self) -> None:
        """Switch to new stream with validation"""
        self._validate_and_execute_stream_action("switch", self.stream_manager.switch_stream)
    
    def _show_validation_error(self, message: str) -> None:
        """Show validation error message consistently"""
        messagebox.showerror("Invalid URL", message)
    
    def _show_warning(self, message: str) -> None:
        """Show warning message consistently"""
        messagebox.showwarning("Warning", message)
    
    def _add_stream(self) -> None:
        """Add current stream to quick swap with improved validation"""
        url, _ = self._get_validated_url_and_quality()
        if not url:
            return
        
        normalized_url = URLValidator.normalize_url(url)
        
        # Check constraints
        if self.quick_swap_manager.has_stream(normalized_url):
            return  # Silently ignore if already exists
        
        if self.quick_swap_manager.is_full():
            self._show_warning(f"All {MAX_SWAP_STREAMS} quick swap slots are occupied. Remove a stream to add a new one.")
            return
        
        # Add stream and update UI
        if self.quick_swap_manager.add_stream(normalized_url):
            self._update_swap_buttons()
    
    def _load_swap_stream(self, index: int) -> None:
        """Load a stream from quick swap with automatic playback"""
        if not self.quick_swap_manager.is_valid_index(index):
            return
        
        url = self.quick_swap_manager.get_stream(index)
        if not url:
            return
        
        # Update UI with selected stream
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        self.settings_manager.set("last_url", url)
        
        # Auto-start or switch stream
        quality = self.quality_var.get()
        if self.stream_manager.is_running():
            self.stream_manager.switch_stream(url, quality)
        else:
            self.stream_manager.start_stream(url, quality)
    
    def _remove_swap_stream(self, index: int) -> None:
        """Remove a stream from quick swap without confirmation"""
        if self.quick_swap_manager.is_valid_index(index):
            if self.quick_swap_manager.remove_by_index(index):
                self._update_swap_buttons()
    
    def _update_ui_state(self, is_streaming: bool, streamer_name: str = "") -> None:
        """Update UI state based on streaming status"""
        if is_streaming:
            self.watch_button.configure(text="🎬 Watching...")
            self.watch_button.grid_remove()
            self.control_row.grid()
            self.root.title(f"{APP_NAME} - Watching {streamer_name}")
        else:
            self.watch_button.configure(text="🎬 Watch Stream")
            self.watch_button.grid()
            self.control_row.grid_remove()
            self.root.title(APP_NAME)
    
    def _on_stream_started(self, url: str, quality: str) -> None:
        """Handle stream started event with UI updates"""
        streamer_name = URLValidator.extract_streamer_name(url)
        self._update_ui_state(True, streamer_name)
    
    def _on_stream_stopped(self) -> None:
        """Handle stream stopped event with UI cleanup"""
        self._update_ui_state(False)
    
    def _on_stream_error(self, error: str) -> None:
        """Handle stream error event with user-friendly messages"""
        self._update_ui_state(False)
        messagebox.showerror("Stream Error", f"Failed to start stream:\n{error}")
    
    def _safe_cleanup_and_exit(self) -> None:
        """Safely cleanup resources and exit application"""
        try:
            if self.stream_manager.is_running():
                self.stream_manager.stop_stream()
            self.settings_manager.save()
            self.root.destroy()
        except Exception as e:
            print(f"Error during cleanup: {e}")
            self.root.destroy()
    
    def _on_closing(self) -> None:
        """Handle application closing with proper cleanup"""
        self._safe_cleanup_and_exit()
    
    def run(self) -> None:
        """Start the application main loop"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Critical error: {e}")
            messagebox.showerror("Critical Error", f"Application encountered a critical error:\n{e}")


def main():
    """Main application entry point with error handling"""
    try:
        app = StreamlinkMaski()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start {APP_NAME}:\n{e}")


if __name__ == "__main__":
    main()
