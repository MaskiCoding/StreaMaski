"""
StreaMaski - Ultra-Lightweight Twitch Stream Viewer
A minimal desktop GUI for watching ad-free Twitch streams using Streamlink

Version: 3.2.0
Author: MaskiCoding
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import time
import re
import os
import json
from typing import List, Tuple, Optional, Callable, Dict, Any, Union
from enum import Enum

# Lazy imports for heavy modules - only import when needed
def _lazy_import_requests():
    """Lazy import requests module"""
    global requests
    if 'requests' not in globals():
        import requests
    return requests

def _lazy_import_customtkinter():
    """Lazy import customtkinter module"""
    global ctk
    if 'ctk' not in globals():
        import customtkinter as ctk
    return ctk

# Windows-specific imports - lazy loaded
def _lazy_import_windows():
    """Lazy import Windows-specific modules"""
    global ctypes, win32gui, win32con, WINDOWS_AVAILABLE
    if 'ctypes' not in globals():
        try:
            import ctypes
            import win32gui
            import win32con
            WINDOWS_AVAILABLE = True
        except ImportError:
            ctypes = None
            win32gui = None
            win32con = None
            WINDOWS_AVAILABLE = False
    return ctypes, win32gui, win32con, WINDOWS_AVAILABLE

# Initialize Windows availability check
ctypes, win32gui, win32con, WINDOWS_AVAILABLE = _lazy_import_windows()

# Application Constants - Aggressively optimized for minimal memory usage
APP_NAME = "StreaMaski"
APP_VERSION = "3.3.0"
WINDOW_SIZE = "480x420"
PROXY_URL = "https://eu.luminous.dev"
MAX_SWAP_STREAMS = 4
QUALITY_OPTIONS = ("best", "1080p60", "1080p", "720p60", "720p", "480p", "360p", "worst")
BUTTON_HEIGHT = 45
MAIN_PADDING = 15

# Ultra-aggressive optimization for minimal resource usage
CACHE_SIZE_URL = 8         # Further reduced
CACHE_SIZE_STREAMER = 4    # Further reduced  
CACHE_DURATION = 60        # Increased from 15 to 60 seconds to reduce web scraping
TIMEOUT_SECONDS = 5        # Further reduced
MAX_CONCURRENT_THREADS = 1

# Streamlink paths - immutable tuple
STREAMLINK_PATHS = (
    "streamlink",
    r"C:\Program Files\Streamlink\bin\streamlink.exe",
    r"C:\Program Files (x86)\Streamlink\bin\streamlink.exe",
    "streamlink.exe",
    r"~\AppData\Local\Programs\Streamlink\bin\streamlink.exe",
    r"~\AppData\Roaming\Python\Scripts\streamlink.exe"
)

# Pre-computed time format for logging efficiency
TIME_FORMAT = '%H:%M:%S'

# Singleton pattern for shared resources
_shared_session = None
_shared_pattern = None


def get_shared_session():
    """Get or create shared requests session - singleton pattern with lazy import"""
    global _shared_session
    if _shared_session is None:
        # Lazy import requests
        requests = _lazy_import_requests()
        
        _shared_session = requests.Session()
        _shared_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    return _shared_session

def get_shared_pattern():
    """Get or create shared regex pattern - singleton pattern"""
    global _shared_pattern
    if _shared_pattern is None:
        _shared_pattern = re.compile(r'"isLive(?:Broadcast)?":true', re.IGNORECASE)
    return _shared_pattern

def get_app_data_dir() -> str:
    """Get the appropriate application data directory for the current OS"""
    if os.name == 'nt':
        app_data = os.environ.get('APPDATA')
        if app_data:
            return os.path.join(app_data, APP_NAME)
    return os.path.join(os.path.expanduser('~'), '.config', APP_NAME.lower())

def ensure_app_data_dir() -> str:
    """Ensure the application data directory exists and return its path"""
    app_dir = get_app_data_dir()
    try:
        os.makedirs(app_dir, exist_ok=True)
        return app_dir
    except OSError:
        return os.path.dirname(os.path.abspath(__file__))

def log_message(message: str, error: Exception = None) -> None:
    """Ultra-optimized logging"""
    timestamp = time.strftime(TIME_FORMAT)
    if error:
        print(f"[{timestamp}] {message}: {error}")
    else:
        print(f"[{timestamp}] {message}")

def safe_execute(func: Callable, *args, **kwargs) -> Any:
    """Safe execution wrapper with minimal overhead"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log_message("Operation failed", e)
        return None

def thread_safe_gui_update(root, func, *args):
    """Unified thread-safe GUI update helper"""
    try:
        root.after(0, func, *args)
    except RuntimeError:
        # GUI main loop not running, update directly
        func(*args)

# Initialize settings file path
SETTINGS_FILE = os.path.join(ensure_app_data_dir(), "settings.json")

class AppState(Enum):
    """Consolidated state enumeration with string values for efficiency"""
    # Stream states
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    # Stream status
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    CHECKING = "checking"

# Aliases for backward compatibility
StreamState = AppState
StreamStatus = AppState


class StreamStatusChecker:
    """Ultra-lightweight stream status checker with shared resources"""
    __slots__ = ('cache',)
    
    def __init__(self):
        self.cache = {}  # Minimal cache
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return ValidationManager.extract_streamer_name(url).lower()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self.cache:
            return False
        timestamp, _ = self.cache[cache_key]
        return time.time() - timestamp < CACHE_DURATION
    
    def _cache_result(self, cache_key: str, status: 'StreamStatus') -> None:
        """Cache result with aggressive cleanup"""
        if len(self.cache) >= CACHE_SIZE_STREAMER:
            self.cache.clear()
        self.cache[cache_key] = (time.time(), status)
    
    def check_stream_status(self, url: str) -> 'StreamStatus':
        """Check if a single stream is online"""
        if not url:
            return StreamStatus.UNKNOWN
        
        cache_key = self._get_cache_key(url)
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]
        
        streamer_name = ValidationManager.extract_streamer_name(url)
        if not streamer_name:
            return StreamStatus.UNKNOWN
        
        status = self._check_via_web_scraping(streamer_name)
        self._cache_result(cache_key, status)
        return status
    
    def _check_via_web_scraping(self, streamer_name: str) -> 'StreamStatus':
        """Ultra-optimized web scraping with shared resources and lazy imports"""
        try:
            # Lazy import requests
            requests = _lazy_import_requests()
            
            url = f"https://www.twitch.tv/{streamer_name.lower()}"
            response = get_shared_session().get(url, timeout=TIMEOUT_SECONDS, stream=True)
            
            if response.status_code != 200:
                return StreamStatus.UNKNOWN
            
            # Read minimal content for pattern matching
            content = response.raw.read(20000).decode('utf-8', errors='ignore')
            return StreamStatus.ONLINE if get_shared_pattern().search(content) else StreamStatus.OFFLINE
            
        except Exception:
            return StreamStatus.UNKNOWN
    
    def check_multiple_streams(self, urls: List[str], callback: Callable[[str, 'StreamStatus'], None] = None) -> Dict[str, 'StreamStatus']:
        """Sequential checking for minimal CPU usage"""
        results = {}
        for url in urls:
            try:
                status = self.check_stream_status(url)
                results[url] = status
                if callback:
                    callback(url, status)
            except Exception:
                results[url] = StreamStatus.UNKNOWN
                if callback:
                    callback(url, StreamStatus.UNKNOWN)
        return results
    
    def clear_cache(self) -> None:
        """Clear the status cache"""
        self.cache.clear()


class Theme:
    """Simplified Rose Pine theme with minimal memory footprint"""
    __slots__ = ()  # No instance variables
    
    # Core colors - constants for immutability
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
    
    # Simplified status colors
    STATUS_ONLINE = "#9ccfd8"    # FOAM - bright cyan for online streams
    STATUS_OFFLINE = "#eb6f92"   # LOVE - soft pink for offline
    STATUS_CHECKING = "#f6c177"  # GOLD - warm yellow for checking
    STATUS_UNKNOWN = "#000000"   # BLACK - black for unknown
    STATUS_ERROR = "#eb6f92"     # LOVE - soft pink for errors
    
    # Simplified color lookup - no dictionary overhead
    @classmethod
    def get_status_color(cls, state: AppState) -> str:
        """Get status color for state - direct lookup only"""
        if state == AppState.ONLINE or state == AppState.RUNNING:
            return cls.STATUS_ONLINE
        elif state == AppState.OFFLINE or state == AppState.STOPPED:
            return cls.STATUS_OFFLINE
        elif state == AppState.CHECKING or state == AppState.STARTING or state == AppState.STOPPING:
            return cls.STATUS_CHECKING
        elif state == AppState.ERROR:
            return cls.STATUS_ERROR
        else:
            return cls.STATUS_UNKNOWN
    
    # Simplified theme presets - no complex caching
    @classmethod
    def get_button_colors(cls, style: str) -> dict:
        """Get button colors for style - simplified"""
        if style == "primary":
            return {"fg_color": cls.PINE, "hover_color": cls.FOAM, "text_color": cls.BASE}
        elif style == "destructive":
            return {"fg_color": cls.LOVE, "hover_color": cls.ROSE, "text_color": cls.BASE}
        elif style == "warning":
            return {"fg_color": cls.GOLD, "hover_color": cls.ROSE, "text_color": cls.BASE}
        elif style == "disabled":
            return {"fg_color": cls.MUTED, "hover_color": cls.SUBTLE, "text_color": cls.TEXT}
        else:
            return {"fg_color": cls.PINE, "hover_color": cls.FOAM, "text_color": cls.BASE}


class ProcessUtils:
    """Streamlined process utility with minimal overhead"""
    __slots__ = ()
    
    @staticmethod
    def get_subprocess_config():
        """Get subprocess configuration for Windows"""
        if os.name != 'nt':
            return {}, 0
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return {'startupinfo': startupinfo}, subprocess.CREATE_NO_WINDOW
    
    @staticmethod
    def run_hidden_command(cmd: List[str], **kwargs):
        """Run command with hidden window"""
        config, flags = ProcessUtils.get_subprocess_config()
        return subprocess.run(cmd, creationflags=flags, **config, **kwargs)
    
    @staticmethod
    def create_hidden_process(cmd: List[str], **kwargs):
        """Create process with hidden window"""
        config, flags = ProcessUtils.get_subprocess_config()
        return subprocess.Popen(cmd, creationflags=flags, **config, **kwargs)


class StreamlinkService:
    """Service for managing Streamlink operations with path discovery and caching"""
    
    def __init__(self):
        self.path = "streamlink"
        self.proxy_url = PROXY_URL
        self._is_available = None  # Cache availability check
        self._discover_path()
    
    def _discover_path(self) -> None:
        """Discover Streamlink installation path with better error handling"""
        # Check all paths including user-specific ones
        all_paths = STREAMLINK_PATHS + tuple(
            os.path.expanduser(path) for path in STREAMLINK_PATHS[4:]  # Last 2 are user paths
        )
        
        for path in all_paths:
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
    """Manages stream processes and state with error handling"""
    
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
        """Emit event to callback"""
        if event in self._callbacks:
            self._callbacks[event](*args)
    
    def is_running(self) -> bool:
        """Check if stream is currently running"""
        return self.state == StreamState.RUNNING
    
    def get_state(self) -> StreamState:
        """Get current stream state"""
        return self.state
    
    def _set_state(self, state: StreamState) -> None:
        """Set stream state and emit event"""
        self.state = state
        # Only emit if callback exists
        if 'state_changed' in self._callbacks:
            self._callbacks['state_changed'](state)
    
    def switch_stream(self, url: str, quality: str) -> bool:
        """Switch to a different stream"""
        if self.is_running():
            self.stop_stream()
            # Wait a moment for cleanup to complete
            time.sleep(0.5)
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
        if not self.is_running():
            return
        
        self._set_state(StreamState.STOPPING)
        self.manually_stopped = True
        
        if self.current_process:
            try:
                # First try gentle termination
                self.current_process.terminate()
                try:
                    self.current_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # Force kill if gentle termination fails
                    self.current_process.kill()
                    self.current_process.wait(timeout=2)
                
                # Close media players on Windows
                if os.name == 'nt':
                    self._close_media_players()
                    
            except Exception as e:
                log_message("Error stopping stream", e)
                # Try to force kill if everything else fails
                try:
                    if self.current_process:
                        self.current_process.kill()
                        self.current_process.wait(timeout=2)
                except Exception:
                    pass
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
            
            # Wait for process to complete
            stdout, stderr = self.current_process.communicate()
            
            # Only emit error if we didn't manually stop and there was an actual error
            if self.current_process.returncode != 0 and not self.manually_stopped:
                error_msg = self._parse_error_message(stderr, stdout)
                self._emit('error', f"Stream failed: {error_msg}")
                
        except Exception as e:
            if not self.manually_stopped:
                self._emit('error', f"Failed to start stream: {str(e)}")
        finally:
            # Always cleanup, regardless of how we got here
            if not self.manually_stopped:
                self._cleanup()
    
    def _extract_stream_info(self, cmd: List[str]) -> Tuple[str, str]:
        """Extract URL and quality from command with better parsing"""
        # Find URL and quality in command, accounting for optional proxy parameter
        url_found = False
        for i, arg in enumerate(cmd):
            if arg.startswith('https://') or arg.startswith('http://'):
                url = arg
                quality = cmd[i + 1] if i + 1 < len(cmd) else "best"
                return url, quality
        return "", "best"
    
    def _get_error_mappings(self) -> Dict[str, str]:
        """Get error pattern to user-friendly message mappings"""
        return {
            "No playable streams found": "Stream not found or offline",
            "Unable to open URL": "Unable to connect to stream",
            "Authentication failed": "Stream requires authentication",
            "Network is unreachable": "Network connection error",
            "Connection timed out": "Connection timeout - try again",
            "404 Client Error": "Stream not found or offline",
            "403 Client Error": "Stream is subscriber-only or restricted",
            "500 Server Error": "Twitch server error - try again later"
        }
    
    def _parse_error_message(self, stderr: bytes, stdout: bytes = b"") -> str:
        """Parse and clean error messages for better user experience"""
        if not stderr and not stdout:
            return "Unknown error occurred"
        
        # Combine stderr and stdout for comprehensive error checking
        error_msg = ""
        if stderr:
            error_msg += stderr.decode('utf-8', errors='ignore').strip()
        if stdout:
            stdout_str = stdout.decode('utf-8', errors='ignore').strip()
            if stdout_str:
                error_msg += "\n" + stdout_str
        
        # Check for known error patterns
        for pattern, friendly_msg in self._get_error_mappings().items():
            if pattern in error_msg:
                return friendly_msg
        
        return error_msg if error_msg else "Unknown error occurred"
    
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
            except Exception as e:
                log_message(f"Failed to close {player}", e)
    
    def _cleanup(self) -> None:
        """Clean up stream state"""
        self._set_state(StreamState.STOPPED)
        self.current_process = None
        self.manually_stopped = False
        if 'stopped' in self._callbacks:
            self._callbacks['stopped']()


class ValidationManager:
    """Ultra-lightweight validation manager with optimized caching"""
    __slots__ = ()
    
    # Single compiled pattern for efficiency
    TWITCH_URL_PATTERN = re.compile(r'^https?://(?:www\.)?twitch\.tv/([a-zA-Z0-9_]{3,25})/?$', re.IGNORECASE)
    
    # Ultra-minimal class-level cache with LRU-like behavior
    _cache = {}
    _cache_order = []
    
    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, str]:
        """Validate Twitch URL with optimized caching"""
        if not url:
            return False, "Please enter a Twitch stream URL"
        
        url = url.strip()
        
        # Cache check
        if url in cls._cache:
            return cls._cache[url]
        
        # Validate URL format
        if cls.TWITCH_URL_PATTERN.match(url):
            result = True, ""
        elif 'twitch.tv' not in url.lower():
            result = False, "URL must be from Twitch (twitch.tv)"
        elif not url.startswith(('http://', 'https://')):
            result = False, "URL must start with http:// or https://"
        else:
            result = False, "Invalid Twitch URL format.\nExample: https://www.twitch.tv/streamer_name"
        
        # Ultra-aggressive cache management with LRU
        if len(cls._cache) >= CACHE_SIZE_URL:
            # Remove oldest entry
            oldest = cls._cache_order.pop(0)
            del cls._cache[oldest]
        
        cls._cache[url] = result
        cls._cache_order.append(url)
        return result
    
    @classmethod
    def extract_streamer_name(cls, url: str) -> str:
        """Extract streamer name - optimized"""
        if not url:
            return ""
        match = cls.TWITCH_URL_PATTERN.match(url.strip())
        return match.group(1).capitalize() if match else ""
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """Normalize URL to standard format - optimized"""
        if not url:
            return ""
        match = cls.TWITCH_URL_PATTERN.match(url.strip())
        return f"https://www.twitch.tv/{match.group(1).lower()}" if match else url
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear cache"""
        cls._cache.clear()
        cls._cache_order.clear()

# Backward compatibility alias
URLValidator = ValidationManager


class SettingsManager:
    """Ultra-lightweight settings manager with minimal memory footprint"""
    __slots__ = ('settings_file', 'settings', '_defaults')
    
    def __init__(self, settings_file: str = SETTINGS_FILE):
        self.settings_file = settings_file
        self._defaults = {
            "last_url": "",
            "last_quality": "best",
            "last_streamer_name": "",
            "quick_swap_streams": [],
            "app_version": APP_VERSION
        }
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file with error recovery"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    settings = self._defaults.copy()
                    for key, value in loaded.items():
                        if key in settings:
                            # Simple validation
                            if key == "quick_swap_streams" and isinstance(value, list):
                                settings[key] = value
                            elif key == "last_quality" and value in QUALITY_OPTIONS:
                                settings[key] = value
                            elif key in ("last_url", "last_streamer_name", "app_version") and isinstance(value, str):
                                settings[key] = value
                    return settings
        except (json.JSONDecodeError, IOError, OSError) as e:
            log_message("Error loading settings", e)
            if os.path.exists(self.settings_file):
                safe_execute(os.rename, self.settings_file, f"{self.settings_file}.backup")
        return self._defaults.copy()
    
    def save(self) -> bool:
        """Save settings to file"""
        self.settings["app_version"] = APP_VERSION
        try:
            with open(self.settings_file, "w", encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, OSError) as e:
            log_message("Error saving settings", e)
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
        self.settings = self._defaults.copy()
        return self.save()


class QuickSwapManager:
    """Ultra-optimized quick swap manager with minimal overhead"""
    __slots__ = ('settings', 'streams', 'stream_statuses', 'status_checker')
    
    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        self.streams = []
        self.stream_statuses = {}
        self.status_checker = StreamStatusChecker()
        
        # Initialize streams efficiently
        raw_streams = self.settings.get("quick_swap_streams", [])
        for url in raw_streams[:MAX_SWAP_STREAMS]:
            if ValidationManager.validate_url(url)[0]:
                normalized = ValidationManager.normalize_url(url)
                if normalized not in self.streams:
                    self.streams.append(normalized)
                    self.stream_statuses[normalized] = StreamStatus.UNKNOWN
    
    def add_stream(self, url: str) -> bool:
        """Add stream to quick swap - optimized"""
        if not url or len(self.streams) >= MAX_SWAP_STREAMS:
            return False
        
        normalized_url = ValidationManager.normalize_url(url)
        if normalized_url in self.streams:
            return False
        
        self.streams.append(normalized_url)
        self.stream_statuses[normalized_url] = StreamStatus.UNKNOWN
        return self.settings.set("quick_swap_streams", self.streams)
    
    def remove_by_index(self, index: int) -> bool:
        """Remove stream by index - optimized"""
        if not (0 <= index < len(self.streams)):
            return False
        
        url = self.streams.pop(index)
        self.stream_statuses.pop(url, None)
        return self.settings.set("quick_swap_streams", self.streams)
    
    def get_stream(self, index: int) -> Optional[str]:
        """Get stream by index"""
        return self.streams[index] if 0 <= index < len(self.streams) else None
    
    def get_streams(self) -> List[str]:
        """Get all streams"""
        return self.streams
    
    def get_stream_status(self, url: str) -> StreamStatus:
        """Get stream status - optimized"""
        normalized_url = ValidationManager.normalize_url(url)
        return self.stream_statuses.get(normalized_url, StreamStatus.UNKNOWN)
    
    def set_stream_status(self, url: str, status: StreamStatus) -> None:
        """Set stream status - optimized"""
        normalized_url = ValidationManager.normalize_url(url)
        self.stream_statuses[normalized_url] = status
    
    def check_all_streams_status(self, callback: Optional[Callable[[str, StreamStatus], None]] = None) -> None:
        """Check status of all streams - optimized"""
        if not self.streams:
            return
        
        # Set all to checking first
        for url in self.streams:
            self.set_stream_status(url, StreamStatus.CHECKING)
            if callback:
                callback(url, StreamStatus.CHECKING)
        
        # Check in background
        def check_statuses():
            try:
                self.status_checker.check_multiple_streams(self.streams, 
                    lambda url, status: self._on_status_checked(url, status, callback))
            except Exception as e:
                log_message("Error checking stream statuses", e)
        
        threading.Thread(target=check_statuses, daemon=True).start()
    
    def _on_status_checked(self, url: str, status: StreamStatus, 
                          callback: Optional[Callable[[str, StreamStatus], None]] = None) -> None:
        """Handle status check result"""
        self.set_stream_status(url, status)
        if callback:
            callback(url, status)
    
    # Optimized utility methods
    def is_full(self) -> bool:
        return len(self.streams) >= MAX_SWAP_STREAMS
    
    def is_valid_index(self, index: int) -> bool:
        return 0 <= index < len(self.streams)
    
    def has_stream(self, url: str) -> bool:
        return ValidationManager.normalize_url(url) in self.streams
    
    def clear_cache(self) -> None:
        """Clear cache - optimized"""
        self.status_checker.clear_cache()


class StreaMaski:
    """Ultra-lightweight main application class with minimal memory footprint"""
    __slots__ = ('streamlink_service', 'settings_manager', 'quick_swap_manager', 'stream_manager',
                 'root', 'main_frame', 'url_entry', 'quality_var', 'quality_combo', 'button_frame',
                 'watch_button', 'control_row', 'stop_button', 'switch_button', 'swap_buttons',
                 'remove_buttons', 'status_dots')
    
    def __init__(self):
        # Initialize services
        self.streamlink_service = StreamlinkService()
        self.settings_manager = SettingsManager()
        self.quick_swap_manager = QuickSwapManager(self.settings_manager)
        self.stream_manager = StreamManager(self.streamlink_service)
        
        # Setup callbacks
        self.stream_manager.set_callback('started', self._on_stream_started)
        self.stream_manager.set_callback('stopped', self._on_stream_stopped)
        self.stream_manager.set_callback('error', self._on_stream_error)
        
        # Initialize UI with lazy CustomTkinter import
        ctk = _lazy_import_customtkinter()
        self.root = ctk.CTk()
        self._setup_theme()
        self._setup_window()
        self._setup_ui()
        self._load_initial_settings()
    
    def _setup_theme(self) -> None:
        """Setup Rose Pine theme with lazy import"""
        ctk = _lazy_import_customtkinter()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    def _setup_window(self) -> None:
        """Setup main window with proper icon support"""
        self.root.title(APP_NAME)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(fg_color=Theme.BASE)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Enable high DPI awareness BEFORE setting icons
        if os.name == 'nt' and hasattr(ctypes, 'windll'):
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            except:
                try:
                    ctypes.windll.user32.SetProcessDPIAware()  # Fallback for older Windows
                except:
                    pass
        
        # Setup icon for window and taskbar with high resolution support
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "StreaMaski_icon.ico")
        if os.path.exists(icon_path):
            try:
                # Method 1: Set ICO file directly for window icon (standard method)
                self.root.iconbitmap(icon_path)
                
                # Method 2: Simplified icon handling - only load essential sizes
                try:
                    # Lazy import PIL only when needed
                    from PIL import Image, ImageTk
                    
                    # Load and process the original icon
                    img = Image.open(icon_path)
                    
                    # Only use essential sizes: 32px for standard display, 256px for high-DPI
                    essential_sizes = [32, 256]
                    
                    # Generate only essential icons
                    icon_photos = []
                    for size in essential_sizes:
                        # Use LANCZOS resampling for best quality
                        resized = img.resize((size, size), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(resized)
                        icon_photos.append(photo)
                    
                    # Set the icons (largest first for best quality)
                    self.root.iconphoto(True, *reversed(icon_photos))
                    
                    # Store references to prevent garbage collection
                    self.root._icon_photos = icon_photos
                    
                    log_message("Essential StreaMaski icons loaded successfully")
                    
                except ImportError:
                    log_message("PIL not available - using standard icon")
                except Exception as e:
                    log_message("PIL icon loading failed, using standard method", e)
                
                # Method 3: Windows-specific taskbar icon enhancement
                if os.name == 'nt':
                    try:
                        # Use 200ms delay for proper icon loading
                        self.root.after(200, self._set_windows_taskbar_icon, icon_path)
                    except Exception as e:
                        log_message("Windows-specific icon setting failed", e)
                
                # Ensure proper window attributes for taskbar display
                self.root.wm_attributes('-toolwindow', False)
                self.root.wm_attributes('-topmost', False)
                
                # Force window focus and visibility
                self.root.lift()
                self.root.focus_force()
                self.root.deiconify()  # Ensure window is not minimized
                
                log_message(f"Successfully loaded StreaMaski icon: {icon_path}")
                
            except Exception as e:
                log_message("Failed to set StreaMaski icon", e)
        else:
            log_message(f"StreaMaski icon file not found: {icon_path}")
    
    def _set_windows_taskbar_icon(self, icon_path: str) -> None:
        """Set Windows taskbar icon with high-resolution support and lazy imports"""
        # Lazy import Windows modules
        ctypes, win32gui, win32con, windows_available = _lazy_import_windows()
        
        if not windows_available:
            return
            
        try:
            # Set explicit app user model ID
            myappid = f'{APP_NAME}.{APP_VERSION}'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
            # Get window handle
            hwnd = int(self.root.wm_frame(), 16)
            
            # Load and set only essential taskbar icons
            essential_configs = [
                (32, 1),   # Standard icon
                (256, 1),  # High-DPI icon
            ]
            
            for size, icon_type in essential_configs:
                try:
                    icon = ctypes.windll.user32.LoadImageW(
                        0,                    # hInst
                        icon_path,           # name (file path)
                        1,                   # type (IMAGE_ICON)
                        size,                # desired width
                        size,                # desired height
                        0x00000010 | 0x00008000  # LR_LOADFROMFILE | LR_SHARED
                    )
                    if icon:
                        # Send WM_SETICON message
                        ctypes.windll.user32.SendMessageW(hwnd, 0x0080, icon_type, icon)
                        log_message(f"Set StreaMaski taskbar icon at size {size}x{size}")
                except Exception as e:
                    log_message(f"Failed to set StreaMaski icon at size {size}x{size}: {e}")
                    continue
            
            log_message("Successfully applied StreaMaski taskbar icon with high resolution")
            
        except Exception as e:
            log_message(f"Failed to set Windows taskbar icon: {e}")
    
    def _create_widget(self, widget_type: str, parent, **kwargs):
        """Optimized widget creation with lazy imports"""
        # Lazy import CustomTkinter
        ctk = _lazy_import_customtkinter()
        
        if widget_type == "frame":
            fg_color = kwargs.pop("fg_color", "transparent")
            if fg_color == "surface":
                fg_color = Theme.SURFACE
            elif fg_color == "overlay":
                fg_color = Theme.OVERLAY
            border_color = kwargs.pop("border_color", Theme.HIGHLIGHT_MED)
            return ctk.CTkFrame(parent, fg_color=fg_color, border_color=border_color, **kwargs)
        
        elif widget_type == "button":
            style = kwargs.pop("style", "primary")
            colors = Theme.get_button_colors(style)
            return ctk.CTkButton(parent, 
                               height=kwargs.pop("height", BUTTON_HEIGHT),
                               font=ctk.CTkFont(size=kwargs.pop("font_size", 12), weight="bold"),
                               border_color=kwargs.pop("border_color", Theme.HIGHLIGHT_MED),
                               **colors, **kwargs)
        
        elif widget_type == "label":
            return ctk.CTkLabel(parent, 
                              font=ctk.CTkFont(size=kwargs.pop("size", 12), weight="bold"),
                              text_color=kwargs.pop("text_color", Theme.TEXT),
                              **kwargs)
        
        elif widget_type == "entry":
            return ctk.CTkEntry(parent, 
                              font=ctk.CTkFont(size=11),
                              fg_color=Theme.OVERLAY, 
                              border_color=Theme.HIGHLIGHT_MED,
                              text_color=Theme.TEXT, 
                              placeholder_text_color=Theme.MUTED,
                              height=kwargs.pop("height", 32),
                              **kwargs)
        
        elif widget_type == "combobox":
            return ctk.CTkComboBox(parent,
                                 font=ctk.CTkFont(size=10), 
                                 fg_color=Theme.OVERLAY,
                                 border_color=Theme.HIGHLIGHT_MED, 
                                 button_color=Theme.PINE,
                                 button_hover_color=Theme.FOAM, 
                                 text_color=Theme.TEXT,
                                 dropdown_fg_color=Theme.SURFACE, 
                                 dropdown_text_color=Theme.TEXT,
                                 dropdown_hover_color=Theme.HIGHLIGHT_MED,
                                 height=kwargs.pop("height", 32),
                                 width=kwargs.pop("width", 120),
                                 state="readonly",
                                 **kwargs)
        
        raise ValueError(f"Unknown widget type: {widget_type}")
    
    def _setup_ui(self) -> None:
        """Setup UI with minimal allocations and lazy imports"""
        # Main frame
        self.main_frame = self._create_widget("frame", self.root, fg_color="surface", border_width=2)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = self._create_widget("label", self.main_frame, text="StreaMaski Client", size=22, text_color=Theme.ROSE)
        title_label.grid(row=0, column=0, pady=(15, 20))
        
        # URL Section
        url_frame = self._create_widget("frame", self.main_frame)
        url_frame.grid(row=1, column=0, sticky="ew", padx=MAIN_PADDING, pady=(0, 15))
        url_frame.grid_columnconfigure(0, weight=1)
        
        self._create_widget("label", url_frame, text="Twitch Stream URL:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        input_row = self._create_widget("frame", url_frame)
        input_row.grid(row=1, column=0, sticky="ew")
        input_row.grid_columnconfigure(0, weight=1)
        
        self.url_entry = self._create_widget("entry", input_row, placeholder_text="https://www.twitch.tv/streamer_name")
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.quality_var = tk.StringVar(value="best")
        self.quality_combo = self._create_widget("combobox", input_row, values=QUALITY_OPTIONS, variable=self.quality_var)
        self.quality_combo.grid(row=0, column=1)
        
        # Control Buttons
        self.button_frame = self._create_widget("frame", self.main_frame)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=MAIN_PADDING, pady=(0, 15))
        self.button_frame.grid_columnconfigure(0, weight=1)
        
        self.watch_button = self._create_widget("button", self.button_frame, text="🎬 Watch Stream", command=self._toggle_stream)
        self.watch_button.grid(row=0, column=0, sticky="ew")
        
        self.control_row = self._create_widget("frame", self.button_frame)
        self.control_row.grid(row=1, column=0, sticky="ew")
        self.control_row.grid_columnconfigure(0, weight=1)
        self.control_row.grid_columnconfigure(1, weight=1)
        
        self.stop_button = self._create_widget("button", self.control_row, text="⏹ Stop Stream", command=self._stop_stream, style="destructive")
        self.stop_button.grid(row=0, column=0, sticky="ew", padx=(0, MAIN_PADDING // 2))
        
        self.switch_button = self._create_widget("button", self.control_row, text="🔄 Switch Stream", command=self._switch_stream, style="warning")
        self.switch_button.grid(row=0, column=1, sticky="ew", padx=(MAIN_PADDING // 2, 0))
        
        self.control_row.grid_remove()
        
        # Management Buttons
        manage_frame = self._create_widget("frame", self.main_frame)
        manage_frame.grid(row=3, column=0, sticky="ew", padx=MAIN_PADDING, pady=(0, 15))
        manage_frame.grid_columnconfigure(0, weight=1)
        manage_frame.grid_columnconfigure(1, weight=1)
        
        self._create_widget("button", manage_frame, text="➕ Add to Quick Swap", command=self._add_stream, height=BUTTON_HEIGHT, width=180).grid(row=0, column=0, sticky="ew", padx=(0, MAIN_PADDING // 2))
        
        self._create_widget("button", manage_frame, text="🔍 Check Status", command=self._check_streams_status, height=BUTTON_HEIGHT, width=180, style="warning").grid(row=0, column=1, sticky="ew", padx=(MAIN_PADDING // 2, 0))
        
        # Swap Section
        swap_frame = self._create_widget("frame", self.main_frame)
        swap_frame.grid(row=4, column=0, sticky="ew", padx=MAIN_PADDING, pady=(0, 15))
        swap_frame.grid_columnconfigure(0, weight=1, uniform="swap_cols")
        swap_frame.grid_columnconfigure(1, weight=1, uniform="swap_cols")
        
        self.swap_buttons = []
        self.remove_buttons = []
        self.status_dots = []
        
        for i in range(MAX_SWAP_STREAMS):
            self._create_swap_button_pair(swap_frame, i)
    
    def _create_swap_button_pair(self, parent_frame, index: int) -> None:
        """Create swap button pair with status indicator"""
        row = index // 2
        col = index % 2
        
        button_container = self._create_widget("frame", parent_frame)
        button_container.grid(row=row, column=col, sticky="ew", 
                            padx=(0, 8) if col == 0 else (8, 0), 
                            pady=(0, 8) if row == 0 else (8, 0))
        button_container.grid_columnconfigure(0, weight=1)
        button_container.grid_columnconfigure(1, weight=0, minsize=25)
        
        # Create a frame to hold the button and status dot
        button_wrapper = self._create_widget("frame", button_container)
        button_wrapper.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        button_wrapper.grid_columnconfigure(0, weight=1)
        button_wrapper.grid_rowconfigure(0, weight=1)
        
        # Main swap button
        swap_button = self._create_widget("button", button_wrapper, text="Empty Slot", 
                                        command=lambda idx=index: self._load_swap_stream(idx),
                                        font_size=10, height=45, style="disabled")
        swap_button.grid(row=0, column=0, sticky="ew")
        swap_button.configure(state="disabled")
        self.swap_buttons.append(swap_button)
        
        # Status dot (positioned absolutely in top-left corner) - Canvas with button color matching
        # Create minimal canvas for dot - background matches button color
        status_canvas = tk.Canvas(button_wrapper, width=10, height=10, 
                                 highlightthickness=0, bd=0, relief='flat',
                                 bg=Theme.MUTED)  # Default to disabled button color
        status_canvas.place(x=3, y=3)
        
        # Create dot on canvas - perfect circle
        dot_id = status_canvas.create_oval(2, 2, 8, 8, fill="#000000", outline="")
        
        # Store reference to canvas and dot for updates
        self.status_dots.append((status_canvas, dot_id))
        
        # Add hover events to update canvas background
        def on_button_enter(event):
            if swap_button.cget("state") != "disabled":
                status_canvas.configure(bg=Theme.FOAM)  # Hover color
        
        def on_button_leave(event):
            if swap_button.cget("state") != "disabled":
                status_canvas.configure(bg=Theme.PINE)  # Normal color
        
        # Bind hover events
        swap_button.bind("<Enter>", on_button_enter)
        swap_button.bind("<Leave>", on_button_leave)
        
        # Remove button
        remove_button = self._create_widget("button", button_container, text="✕", 
                                          command=lambda idx=index: self._remove_swap_stream(idx),
                                          style="destructive", height=45, width=25)
        remove_button.grid(row=0, column=1, sticky="ew")
        remove_button.grid_remove()
        self.remove_buttons.append(remove_button)
    
    def _load_initial_settings(self) -> None:
        """Load initial settings"""
        last_url = self.settings_manager.get("last_url", "")
        if last_url and ValidationManager.validate_url(last_url)[0]:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, last_url)
        
        quality = self.settings_manager.get("last_quality", "best")
        if quality in QUALITY_OPTIONS:
            self.quality_var.set(quality)
        
        self._update_swap_buttons()
    
    def _update_swap_buttons(self) -> None:
        """Update swap buttons display - optimized with status dots"""
        streams = self.quick_swap_manager.get_streams()
        
        for i, button in enumerate(self.swap_buttons):
            if i < len(streams):
                url = streams[i]
                streamer_name = ValidationManager.extract_streamer_name(url)
                status = self.quick_swap_manager.get_stream_status(url)
                
                # Update button text and state (no color change)
                button.configure(text=streamer_name, state="normal", 
                               fg_color=Theme.PINE, hover_color=Theme.FOAM, 
                               text_color=Theme.BASE)
                
                # Update status dot color and canvas background
                if hasattr(self, 'status_dots') and i < len(self.status_dots):
                    dot_color = self._get_status_dot_color(status)
                    self._update_status_dot(i, dot_color)
                
                self.remove_buttons[i].grid()
            else:
                # Empty slot
                button.configure(text="Empty Slot", state="disabled", **Theme.get_button_colors("disabled"))
                
                # Hide status dot for empty slots
                if hasattr(self, 'status_dots') and i < len(self.status_dots):
                    self._update_status_dot(i, "transparent")
                
                self.remove_buttons[i].grid_remove()
    
    def _get_status_dot_color(self, status: StreamStatus) -> str:
        """Get color for status dot - optimized direct lookup"""
        # Direct mapping for performance
        if status == AppState.ONLINE:
            return "#00FF00"  # Green
        elif status == AppState.OFFLINE:
            return "#FF0000"  # Red
        elif status == AppState.CHECKING:
            return "#FFFF00"  # Yellow
        else:  # UNKNOWN
            return "#000000"  # Black
    
    def _update_status_dot(self, index: int, color: str) -> None:
        """Update status dot color - Canvas with button color matching"""
        if not hasattr(self, 'status_dots') or index >= len(self.status_dots):
            return
            
        try:
            canvas, dot_id = self.status_dots[index]
            
            # Handle transparency by hiding the canvas
            if color == "transparent":
                canvas.place_forget()
            else:
                canvas.place(x=3, y=3)  # Show the canvas
                canvas.itemconfig(dot_id, fill=color)
                
                # Update canvas background to match button color
                if index < len(self.swap_buttons):
                    button = self.swap_buttons[index]
                    # Get current button color (non-hover state)
                    if button.cget("state") == "disabled":
                        canvas.configure(bg=Theme.MUTED)  # Disabled button color
                    else:
                        canvas.configure(bg=Theme.PINE)   # Active button color
        except (IndexError, tk.TclError):
            # Handle cases where canvas might be destroyed
            pass
    
    def _toggle_stream(self) -> None:
        """Toggle stream state"""
        if self.stream_manager.is_running():
            self._stop_stream()
        else:
            self._watch_stream()
    
    def _watch_stream(self) -> None:
        """Watch stream"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a stream URL")
            return
        
        is_valid, error_msg = ValidationManager.validate_url(url)
        if not is_valid:
            messagebox.showerror("Invalid URL", error_msg)
            return
        
        quality = self.quality_var.get()
        self.settings_manager.set("last_url", url)
        self.settings_manager.set("last_quality", quality)
        
        self.stream_manager.start_stream(url, quality)
    
    def _stop_stream(self) -> None:
        """Stop stream"""
        self.stream_manager.stop_stream()
    
    def _switch_stream(self) -> None:
        """Switch stream"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a stream URL")
            return
        
        is_valid, error_msg = ValidationManager.validate_url(url)
        if not is_valid:
            messagebox.showerror("Invalid URL", error_msg)
            return
        
        quality = self.quality_var.get()
        self.settings_manager.set("last_url", url)
        self.settings_manager.set("last_quality", quality)
        
        self.stream_manager.switch_stream(url, quality)
    
    def _add_stream(self) -> None:
        """Add stream to quick swap"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a stream URL")
            return
        
        is_valid, error_msg = ValidationManager.validate_url(url)
        if not is_valid:
            messagebox.showerror("Invalid URL", error_msg)
            return
        
        if self.quick_swap_manager.has_stream(url):
            return
        
        if self.quick_swap_manager.is_full():
            messagebox.showwarning("Warning", f"All {MAX_SWAP_STREAMS} quick swap slots are occupied.")
            return
        
        if self.quick_swap_manager.add_stream(url):
            self._update_swap_buttons()
    
    def _load_swap_stream(self, index: int) -> None:
        """Load swap stream"""
        if not self.quick_swap_manager.is_valid_index(index):
            return
        
        url = self.quick_swap_manager.get_stream(index)
        if not url:
            return
        
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        self.settings_manager.set("last_url", url)
        
        quality = self.quality_var.get()
        if self.stream_manager.is_running():
            self.stream_manager.switch_stream(url, quality)
        else:
            self.stream_manager.start_stream(url, quality)
    
    def _remove_swap_stream(self, index: int) -> None:
        """Remove swap stream"""
        if self.quick_swap_manager.is_valid_index(index):
            if self.quick_swap_manager.remove_by_index(index):
                self._update_swap_buttons()
    
    def _check_streams_status(self) -> None:
        """Check streams status"""
        if not self.quick_swap_manager.get_streams():
            messagebox.showwarning("Warning", "No streams in quick swap to check.")
            return
        
        self.quick_swap_manager.check_all_streams_status(self._on_stream_status_update)
    
    def _on_stream_status_update(self, url: str, status: StreamStatus) -> None:
        """Handle status update - optimized"""
        try:
            streams = self.quick_swap_manager.get_streams()
            index = streams.index(url)
            thread_safe_gui_update(self.root, self._update_button_text_color, index, status)
        except (ValueError, IndexError):
            # Stream not found in current list or index out of range
            pass
    
    def _update_button_text_color(self, index: int, status: StreamStatus) -> None:
        """Update button status dot based on status - simplified"""
        if 0 <= index < len(self.status_dots):
            self._update_status_dot(index, self._get_status_dot_color(status))
    
    def _on_stream_started(self, url: str, quality: str) -> None:
        """Handle stream started"""
        streamer_name = ValidationManager.extract_streamer_name(url)
        thread_safe_gui_update(self.root, self._update_gui_stream_started, streamer_name)
    
    def _update_gui_stream_started(self, streamer_name: str) -> None:
        """Update GUI for stream started (main thread)"""
        self.watch_button.grid_remove()
        self.control_row.grid()
        self.root.title(f"{APP_NAME} - Watching {streamer_name}")
    
    def _on_stream_stopped(self) -> None:
        """Handle stream stopped"""
        thread_safe_gui_update(self.root, self._update_gui_stream_stopped)
    
    def _update_gui_stream_stopped(self) -> None:
        """Update GUI for stream stopped (main thread)"""
        self.watch_button.grid()
        self.control_row.grid_remove()
        self.root.title(APP_NAME)
    
    def _on_stream_error(self, error: str) -> None:
        """Handle stream error"""
        thread_safe_gui_update(self.root, self._update_gui_stream_error, error)
    
    def _update_gui_stream_error(self, error: str) -> None:
        """Update GUI for stream error (main thread)"""
        self.watch_button.grid()
        self.control_row.grid_remove()
        self.root.title(APP_NAME)
        messagebox.showerror("Stream Error", f"Failed to start stream:\n{error}")
    
    def _on_closing(self) -> None:
        """Handle window closing with proper cleanup"""
        try:
            # Stop any running streams
            if self.stream_manager.is_running():
                self.stream_manager.stop_stream()
            
            # Clean up status dots to prevent memory leaks
            if hasattr(self, 'status_dots'):
                for canvas, dot_id in self.status_dots:
                    try:
                        canvas.destroy()
                    except:
                        pass
                self.status_dots.clear()
            
            # Clear caches
            self.quick_swap_manager.clear_cache()
            ValidationManager.clear_cache()
            
            # Save settings
            self.settings_manager.save()
            
            # Destroy root window
            self.root.destroy()
        except Exception as e:
            log_message("Error during cleanup", e)
            # Force destroy if cleanup fails
            try:
                self.root.destroy()
            except:
                pass
    
    def run(self) -> None:
        """Run application"""
        try:
            self.root.mainloop()
        except Exception as e:
            log_message("Critical error", e)
            messagebox.showerror("Critical Error", f"Application encountered a critical error:\n{e}")


def main():
    """Main application entry point with error handling"""
    try:
        app = StreaMaski()
        app.run()
    except Exception as e:
        log_message("Failed to start application", e)
        messagebox.showerror("Startup Error", f"Failed to start {APP_NAME}:\n{e}")


if __name__ == "__main__":
    main()
