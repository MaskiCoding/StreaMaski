"""
StreaMaski - Lightweight Twitch Stream Viewer
A minimal desktop GUI for watching ad-free Twitch streams using Streamlink

Version: 3.0.0
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
import requests
from typing import List, Tuple, Optional, Callable, Dict, Any, Union
from enum import Enum
import contextlib
import weakref

# Windows-specific imports
try:
    import ctypes
    from ctypes import wintypes
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

# Application Constants
APP_NAME = "StreaMaski"
APP_VERSION = "3.0.0"
WINDOW_SIZE = "480x420"
PROXY_URL = "https://eu.luminous.dev"
MAX_SWAP_STREAMS = 4
QUALITY_OPTIONS = ["best", "1080p60", "1080p", "720p60", "720p", "480p", "360p", "worst"]
BUTTON_HEIGHT = 45
MAIN_PADDING = 15
PADDING = MAIN_PADDING
CACHE_SIZE_URL = 100
CACHE_SIZE_STREAMER = 50
CACHE_DURATION = 60
TIMEOUT_SECONDS = 10
MAX_CONCURRENT_THREADS = 5

# Streamlink paths (optimized for Windows)
STREAMLINK_PATHS = [
    "streamlink",
    r"C:\Program Files\Streamlink\bin\streamlink.exe",
    r"C:\Program Files (x86)\Streamlink\bin\streamlink.exe",
    "streamlink.exe",
    r"~\AppData\Local\Programs\Streamlink\bin\streamlink.exe",
    r"~\AppData\Roaming\Python\Scripts\streamlink.exe"
]


def get_app_data_dir() -> str:
    """Get the appropriate application data directory for the current OS"""
    if os.name == 'nt':  # Windows
        app_data = os.environ.get('APPDATA')
        if app_data:
            return os.path.join(app_data, APP_NAME)
    
    # macOS
    if os.name == 'posix' and os.path.exists(os.path.expanduser('~/Library')):
        return os.path.join(os.path.expanduser('~/Library'), 'Application Support', APP_NAME)
    
    # Linux/Unix
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config_home:
        return os.path.join(xdg_config_home, APP_NAME.lower())
    
    return os.path.join(os.path.expanduser('~'), '.config', APP_NAME.lower())


def ensure_app_data_dir() -> str:
    """Ensure the application data directory exists and return its path"""
    app_dir = get_app_data_dir()
    try:
        os.makedirs(app_dir, exist_ok=True)
        return app_dir
    except OSError as e:
        _log_error(f"Could not create app data directory {app_dir}", e)
        return os.path.dirname(os.path.abspath(__file__))

def _log_error(message: str, error: Exception = None, level: str = "Warning") -> None:
    """Centralized error logging with improved formatting"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if error:
        print(f"[{timestamp}] {level}: {message}: {error}")
    else:
        print(f"[{timestamp}] {level}: {message}")

def _safe_execute(func: Callable, *args, error_msg: str = "Operation failed", **kwargs) -> Any:
    """Safe execution wrapper with error handling and return value"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        _log_error(error_msg, e)
        return None

@contextlib.contextmanager
def _suppress_exceptions(default_return: Any = None, error_msg: str = "Operation failed"):
    """Context manager to suppress exceptions and return default value"""
    try:
        yield
    except Exception as e:
        _log_error(error_msg, e)
        return default_return


# Initialize settings file path
SETTINGS_FILE = os.path.join(ensure_app_data_dir(), "settings.json")


class AppState(Enum):
    """Consolidated state enumeration"""
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
    """Checks if Twitch streams are online or offline with optimized performance"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.timeout = TIMEOUT_SECONDS
        self.cache = {}
        self.cache_duration = CACHE_DURATION
        # Pre-compile regex patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Pre-compile all regex patterns for better performance"""
        self._streamer_pattern = re.compile(r'"login":"([^"]+)"', re.IGNORECASE)
        self._live_patterns = [
            re.compile(r'"isLiveBroadcast":true', re.IGNORECASE),
            re.compile(r'"broadcastType":"live"', re.IGNORECASE),
            re.compile(r'"isLive":true', re.IGNORECASE),
            re.compile(r'"viewerCount":\s*[1-9]\d*', re.IGNORECASE)
        ]
        self._offline_patterns = [
            re.compile(r'"isLiveBroadcast":false', re.IGNORECASE),
            re.compile(r'"broadcastType":"upload"', re.IGNORECASE),
            re.compile(r'OfflineScreen', re.IGNORECASE)
        ]
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return ValidationManager.extract_streamer_name(url).lower()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        return (cache_key in self.cache and 
                time.time() - self.cache[cache_key][0] < self.cache_duration)
    
    def _cache_result(self, cache_key: str, status: StreamStatus) -> None:
        """Cache the status result with size limit"""
        if len(self.cache) >= CACHE_SIZE_STREAMER:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][0])
            del self.cache[oldest_key]
        self.cache[cache_key] = (time.time(), status)
    
    def check_stream_status(self, url: str) -> StreamStatus:
        """Check if a single stream is online or offline"""
        if not url:
            return StreamStatus.UNKNOWN
        
        cache_key = self._get_cache_key(url)
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]
        
        streamer_name = ValidationManager.extract_streamer_name(url)
        if not streamer_name:
            return StreamStatus.UNKNOWN
        
        status = self._check_via_web_scraping(url, streamer_name)
        self._cache_result(cache_key, status)
        return status
    
    def _check_via_web_scraping(self, url: str, streamer_name: str) -> StreamStatus:
        """Check stream status using web scraping with improved error handling"""
        try:
            twitch_url = f"https://www.twitch.tv/{streamer_name.lower()}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            response = self.session.get(twitch_url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for live indicators first (most common case)
                if any(pattern.search(content) for pattern in self._live_patterns):
                    return StreamStatus.ONLINE
                
                # Check offline patterns
                if any(pattern.search(content) for pattern in self._offline_patterns):
                    return StreamStatus.OFFLINE
                
                # Default to offline if status is unclear
                return StreamStatus.OFFLINE
            else:
                return StreamStatus.UNKNOWN
                
        except requests.RequestException as e:
            _log_error(f"Network error checking stream {streamer_name}", e)
            return StreamStatus.UNKNOWN
        except Exception as e:
            _log_error(f"Unexpected error checking stream {streamer_name}", e)
            return StreamStatus.UNKNOWN
    
    def check_multiple_streams(self, urls: List[str], callback: Callable[[str, StreamStatus], None] = None) -> Dict[str, StreamStatus]:
        """Check multiple streams concurrently with improved thread management"""
        if not urls:
            return {}
        
        results = {}
        
        def check_single(url: str):
            try:
                status = self.check_stream_status(url)
                results[url] = status
                if callback:
                    callback(url, status)
            except Exception as e:
                _log_error(f"Error checking stream {url}", e)
                results[url] = StreamStatus.UNKNOWN
                if callback:
                    callback(url, StreamStatus.UNKNOWN)
        
        # Use threading with reasonable limits
        max_threads = min(len(urls), MAX_CONCURRENT_THREADS)
        
        # Process URLs in batches
        for i in range(0, len(urls), max_threads):
            batch = urls[i:i + max_threads]
            threads = []
            
            for url in batch:
                thread = threading.Thread(target=check_single, args=(url,), daemon=True)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads in this batch
            for thread in threads:
                thread.join(timeout=self.timeout + 2)
        
        return results
    
    def clear_cache(self) -> None:
        """Clear the status cache"""
        self.cache.clear()
    
    def __del__(self):
        """Cleanup session on deletion"""
        if hasattr(self, 'session'):
            self.session.close()


class Theme:
    """Rose Pine theme with optimized colors and styles"""
    
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
    
    # Color mapping for UI elements (frozen for performance)
    COLOR_MAP = {
        "surface": SURFACE,
        "overlay": OVERLAY,
        "base": BASE,
        "transparent": "transparent"
    }
    
    # Pre-computed button styles (frozen for performance)
    BUTTON_STYLES = {
        "primary": {"fg_color": PINE, "hover_color": FOAM, "text_color": BASE},
        "destructive": {"fg_color": LOVE, "hover_color": ROSE, "text_color": BASE},
        "warning": {"fg_color": GOLD, "hover_color": ROSE, "text_color": BASE},
        "disabled": {"fg_color": MUTED, "hover_color": SUBTLE, "text_color": TEXT}
    }
    
    # Individual button style aliases for backward compatibility
    BUTTON_PRIMARY = BUTTON_STYLES["primary"]
    BUTTON_DISABLED = BUTTON_STYLES["disabled"]
    
    # Consolidated status colors (frozen for performance)
    STATUS_COLORS = {
        AppState.ONLINE: "#00FF00", 
        AppState.OFFLINE: "#FF0000", 
        AppState.CHECKING: "#FFD700", 
        AppState.UNKNOWN: "#FFFF00",
        AppState.RUNNING: "#00FF00", 
        AppState.STOPPED: "#FF0000",
        AppState.STARTING: "#FFD700", 
        AppState.STOPPING: "#FFD700",
        AppState.ERROR: "#FF0000"
    }
    
    # Status color constants
    STATUS_UNKNOWN = "#FFFF00"
    
    # Pre-cached color lookups for performance
    _STATUS_COLOR_CACHE = {}
    
    @classmethod
    def get_status_color(cls, state: AppState) -> str:
        """Get status color for state with caching"""
        if state not in cls._STATUS_COLOR_CACHE:
            cls._STATUS_COLOR_CACHE[state] = cls.STATUS_COLORS.get(state, cls.GOLD)
        return cls._STATUS_COLOR_CACHE[state]
    
    @classmethod
    def get_status_colors(cls) -> Dict[AppState, str]:
        """Get all status colors"""
        return cls.STATUS_COLORS.copy()
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear color cache (for testing purposes)"""
        cls._STATUS_COLOR_CACHE.clear()


class ProcessUtils:
    """Utility for subprocess management with invisible windows"""
    
    _startup_info = None
    _creation_flags = 0
    
    @classmethod
    def _init_windows_config(cls):
        """Initialize Windows-specific configuration once"""
        if cls._startup_info is None and os.name == 'nt':
            cls._startup_info = subprocess.STARTUPINFO()
            cls._startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            cls._startup_info.wShowWindow = subprocess.SW_HIDE
            cls._creation_flags = subprocess.CREATE_NO_WINDOW
    
    @classmethod
    def get_subprocess_config(cls) -> Tuple[Optional[subprocess.STARTUPINFO], int]:
        """Get subprocess configuration for invisible windows on Windows"""
        cls._init_windows_config()
        return cls._startup_info, cls._creation_flags
    
    @classmethod
    def run_hidden_command(cls, cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Run a command with hidden window"""
        startupinfo, creationflags = cls.get_subprocess_config()
        return subprocess.run(
            cmd,
            startupinfo=startupinfo,
            creationflags=creationflags,
            **kwargs
        )
    
    @classmethod
    def create_hidden_process(cls, cmd: List[str], **kwargs) -> subprocess.Popen:
        """Create a process with hidden window"""
        startupinfo, creationflags = cls.get_subprocess_config()
        return subprocess.Popen(
            cmd,
            startupinfo=startupinfo,
            creationflags=creationflags,
            **kwargs
        )
    
    @staticmethod
    def safe_execute(func: Callable, *args, default_return: Any = None, 
                    error_msg: str = "Operation failed", **kwargs) -> Any:
        """Helper to reduce try-catch duplication (DRY)"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            _log_error(error_msg, e)
            return default_return


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
        all_paths = STREAMLINK_PATHS + [
            os.path.expanduser(path) for path in STREAMLINK_PATHS[4:]  # Last 2 are user paths
        ]
        
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
            # No need for sleep, cleanup is handled
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
            _log_error("Error stopping stream", e)
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
                error_msg = self._parse_error_message(stderr, stdout)
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
            ProcessUtils.safe_execute(
                ProcessUtils.run_hidden_command,
                ['taskkill', '/F', '/IM', player],
                capture_output=True,
                timeout=5,
                error_msg=f"Failed to close {player}"
            )
    
    def _cleanup(self) -> None:
        """Clean up stream state"""
        self._set_state(StreamState.STOPPED)
        self.current_process = None
        self.manually_stopped = False
        if 'stopped' in self._callbacks:
            self._callbacks['stopped']()


class ValidationManager:
    """Consolidated validation and settings management with optimized caching"""
    
    # Pre-compiled URL validation pattern
    TWITCH_URL_PATTERN = re.compile(r'^https?://(?:www\.)?twitch\.tv/([a-zA-Z0-9_]{3,25})/?$', re.IGNORECASE)
    
    # Class-level caches with size limits
    _url_cache: Dict[str, Tuple[bool, str]] = {}
    _streamer_cache: Dict[str, str] = {}
    
    # Error messages for better UX
    _ERROR_MESSAGES = {
        'not_twitch': "URL must be from Twitch (twitch.tv)",
        'no_protocol': "URL must start with http:// or https://",
        'invalid_format': "Invalid Twitch URL format.\nExample: https://www.twitch.tv/streamer_name"
    }
    
    @classmethod
    def _maintain_cache_size(cls, cache: Dict, max_size: int) -> None:
        """Maintain cache size by removing oldest entries"""
        while len(cache) >= max_size:
            # Remove oldest entry (first in insertion order)
            cache.pop(next(iter(cache)))
    
    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, str]:
        """Validate Twitch URL with caching and size limits"""
        if not url:
            return False, "Please enter a Twitch stream URL"
        
        url = url.strip()
        if url in cls._url_cache:
            return cls._url_cache[url]
        
        # Validate URL format
        if not cls.TWITCH_URL_PATTERN.match(url):
            if 'twitch.tv' not in url.lower():
                result = False, cls._ERROR_MESSAGES['not_twitch']
            elif not url.startswith(('http://', 'https://')):
                result = False, cls._ERROR_MESSAGES['no_protocol']
            else:
                result = False, cls._ERROR_MESSAGES['invalid_format']
        else:
            result = True, ""
        
        # Cache with size limit
        cls._maintain_cache_size(cls._url_cache, CACHE_SIZE_URL)
        cls._url_cache[url] = result
        return result
    
    @classmethod
    def extract_streamer_name(cls, url: str) -> str:
        """Extract streamer name with caching and size limits"""
        if not url:
            return ""
        
        if url in cls._streamer_cache:
            return cls._streamer_cache[url]
        
        match = cls.TWITCH_URL_PATTERN.match(url.strip())
        result = match.group(1).capitalize() if match else ""
        
        # Cache with size limit
        cls._maintain_cache_size(cls._streamer_cache, CACHE_SIZE_STREAMER)
        cls._streamer_cache[url] = result
        return result
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """Normalize URL to standard format"""
        if not url:
            return ""
        match = cls.TWITCH_URL_PATTERN.match(url.strip())
        return f"https://www.twitch.tv/{match.group(1).lower()}" if match else url
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all validation caches (for testing purposes)"""
        cls._url_cache.clear()
        cls._streamer_cache.clear()

# Backward compatibility alias
URLValidator = ValidationManager


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
                    return self._validate_settings(json.load(f))
        except (json.JSONDecodeError, IOError, OSError) as e:
            _log_error("Error loading settings", e)
            self._backup_corrupted_settings()
        return self._get_default_settings()
    
    _VALIDATION_RULES = {
        "quick_swap_streams": lambda x: x if isinstance(x, list) else [],
        "last_quality": lambda x: x if x in QUALITY_OPTIONS else "best",
        "last_url": lambda x: x if isinstance(x, str) else "",
        "last_streamer_name": lambda x: x if isinstance(x, str) else "",
        "app_version": lambda x: x if isinstance(x, str) else APP_VERSION
    }
    
    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate loaded settings and merge with defaults"""
        defaults = self._get_default_settings()
        for key, default_value in defaults.items():
            if key not in settings:
                settings[key] = default_value
            else:
                validator = self._VALIDATION_RULES.get(key)
                settings[key] = validator(settings[key]) if validator else settings[key]
        return settings
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings"""
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
            _safe_execute(os.rename, self.settings_file, f"{self.settings_file}.backup", 
                         error_msg="Could not backup corrupted settings")
    
    def save(self) -> bool:
        """Save settings to file"""
        self.settings["app_version"] = APP_VERSION
        try:
            with open(self.settings_file, "w", encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, OSError) as e:
            _log_error("Error saving settings", e)
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
    """Manages quick swap streams with validation and limits"""
    
    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        self.max_streams = MAX_SWAP_STREAMS
        self._normalized_cache: Dict[str, str] = {}
        self.streams = self._validate_streams(
            self.settings.get("quick_swap_streams", [])
        )
        self.stream_statuses: Dict[str, StreamStatus] = {}
        self.status_checker = StreamStatusChecker()
        # Pre-initialize status for all streams
        self._initialize_stream_statuses()
        # Use weakref to avoid circular references
        self._status_callbacks: List[weakref.ref] = []
    
    def _initialize_stream_statuses(self) -> None:
        """Initialize status for all streams"""
        for stream in self.streams:
            self.stream_statuses[stream] = StreamStatus.UNKNOWN
    
    def _validate_streams(self, streams: List[str]) -> List[str]:
        """Validate and clean stream URLs with duplicate removal"""
        if not streams:
            return []
        
        validated_streams = []
        seen_urls = set()
        
        for url in streams:
            if len(validated_streams) >= self.max_streams:
                break
                
            if ValidationManager.validate_url(url)[0]:
                normalized_url = self._get_normalized_url(url)
                if normalized_url not in seen_urls:
                    validated_streams.append(normalized_url)
                    seen_urls.add(normalized_url)
        
        return validated_streams
    
    def _get_normalized_url(self, url: str) -> str:
        """Get normalized URL with caching"""
        if url not in self._normalized_cache:
            # Maintain cache size
            if len(self._normalized_cache) >= CACHE_SIZE_URL:
                self._normalized_cache.pop(next(iter(self._normalized_cache)))
            self._normalized_cache[url] = ValidationManager.normalize_url(url)
        return self._normalized_cache[url]
    
    def _save_streams(self) -> bool:
        """Save streams to settings"""
        return self.settings.set("quick_swap_streams", self.streams)
    
    def add_stream(self, url: str) -> bool:
        """Add stream to quick swap with validation"""
        if not url or self.is_full():
            return False
        
        normalized_url = self._get_normalized_url(url)
        
        if normalized_url in self.streams:
            return False
        
        self.streams.append(normalized_url)
        self.stream_statuses[normalized_url] = StreamStatus.UNKNOWN
        return self._save_streams()
    
    def remove_stream(self, url: str) -> bool:
        """Remove stream from quick swap"""
        normalized_url = self._get_normalized_url(url)
        
        if normalized_url not in self.streams:
            return False
        
        self.streams.remove(normalized_url)
        self.stream_statuses.pop(normalized_url, None)
        return self._save_streams()
    
    def remove_by_index(self, index: int) -> bool:
        """Remove stream by index with bounds checking"""
        if not self.is_valid_index(index):
            return False
        
        url = self.streams[index]
        self.streams.pop(index)
        self.stream_statuses.pop(url, None)
        return self._save_streams()
    
    def get_stream(self, index: int) -> Optional[str]:
        """Get stream by index with bounds checking"""
        return self.streams[index] if self.is_valid_index(index) else None
    
    def get_streams(self) -> List[str]:
        """Get all streams as a copy"""
        return self.streams.copy()
    
    def get_stream_status(self, url: str) -> StreamStatus:
        """Get the status of a specific stream"""
        normalized_url = self._get_normalized_url(url)
        return self.stream_statuses.get(normalized_url, StreamStatus.UNKNOWN)
    
    def set_stream_status(self, url: str, status: StreamStatus) -> None:
        """Set the status of a specific stream"""
        normalized_url = self._get_normalized_url(url)
        self.stream_statuses[normalized_url] = status
    
    def check_all_streams_status(self, callback: Optional[Callable[[str, StreamStatus], None]] = None) -> None:
        """Check status of all streams asynchronously"""
        if not self.streams:
            return
        
        # Set all streams to checking status first
        for url in self.streams:
            self.set_stream_status(url, StreamStatus.CHECKING)
            if callback:
                callback(url, StreamStatus.CHECKING)
        
        # Check statuses in background thread
        def check_statuses():
            try:
                self.status_checker.check_multiple_streams(
                    self.streams, 
                    lambda url, status: self._on_status_checked(url, status, callback)
                )
            except Exception as e:
                _log_error("Error checking stream statuses", e)
        
        thread = threading.Thread(target=check_statuses, daemon=True)
        thread.start()
    
    def _on_status_checked(self, url: str, status: StreamStatus, 
                          callback: Optional[Callable[[str, StreamStatus], None]] = None) -> None:
        """Handle status check result"""
        self.set_stream_status(url, status)
        if callback:
            callback(url, status)
    
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
    
    def clear_cache(self) -> None:
        """Clear internal caches"""
        self._normalized_cache.clear()
        self.status_checker.clear_cache()
    
    def __del__(self):
        """Cleanup on deletion"""
        self.clear_cache()


class StreaMaski:
    """Main application class with improved organization and error handling"""
    
    def __init__(self):
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
        """Setup Rose Pine theme for the entire application"""
        ctk.set_appearance_mode("dark")
        # Set custom Rose Pine color theme
        ctk.set_default_color_theme("blue")  # Base theme, will be overridden
    
    def _configure_grid_weights(self, widget, **configs) -> None:
        """Helper to configure grid weights in one call - Optimized"""
        for config_type, config_data in configs.items():
            if config_type == "columns":
                for col, weight in config_data.items():
                    widget.grid_columnconfigure(col, weight=weight)
            elif config_type == "rows":
                for row, weight in config_data.items():
                    widget.grid_rowconfigure(row, weight=weight)
            elif config_type == "uniform_columns":
                for col, (weight, uniform) in config_data.items():
                    widget.grid_columnconfigure(col, weight=weight, uniform=uniform)
    
    def _setup_grid_section(self, frame: ctk.CTkFrame, row: int, column: int = 0, sticky: str = "ew", padx: int = None, pady: tuple = None) -> None:
        """Helper to reduce grid setup duplication (DRY) - Optimized"""
        if padx is None:
            padx = MAIN_PADDING
        if pady is None:
            pady = (0, 15)
        
        frame.grid(row=row, column=column, sticky=sticky, padx=padx, pady=pady)
        # Most common case - single column with weight 1
        frame.grid_columnconfigure(0, weight=1)
    
    def _configure_container_grid(self, container) -> None:
        """Configure button container grid with fixed remove button column - Optimized"""
        # Batch configure both columns at once
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=0, minsize=25)  # Fixed size for remove button
    
    def _setup_window(self) -> None:
        """Setup main window properties"""
        self.root.title(APP_NAME)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(fg_color=Theme.BASE)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._setup_icon()
        self._configure_grid_weights(self.root, columns={0: 1}, rows={0: 1})
    
    def _setup_icon(self) -> None:
        """Setup application icon"""
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Icon.ico")
        if not os.path.exists(icon_path):
            _log_error("Icon file not found", icon_path)
            return
        
        try:
            self.root.iconbitmap(icon_path)
            if os.name == 'nt' and WINDOWS_AVAILABLE:
                self.root.after(200, lambda: self._set_taskbar_icon_delayed(icon_path))
        except Exception as e:
            _log_error("Could not load icon", e)
            try:
                self.root.iconbitmap(default=icon_path)
            except Exception as e2:
                _log_error("Alternative icon method also failed", e2)
    
    def _set_taskbar_icon_delayed(self, icon_path: str) -> None:
        """Set taskbar icon with delay"""
        if not WINDOWS_AVAILABLE:
            return
        try:
            myappid = f'{APP_NAME}.{APP_VERSION}'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            hwnd = int(self.root.wm_frame(), 16)
            
            # Load and set icons
            for size in [(16, 0), (32, 1), (48, 1)]:
                icon = ctypes.windll.user32.LoadImageW(0, icon_path, 1, size[0], size[0], 0x00000010 | 0x00008000)
                if icon:
                    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, size[1], icon)
        except Exception as e:
            _log_error("Could not set delayed taskbar icon", e)
    
    def _setup_ui(self) -> None:
        """Setup the main user interface with Rose Pine theme"""
        # Main frame with Rose Pine colors
        self.main_frame = self._create_frame(
            self.root,
            fg_color="surface",
            border_width=2
        )
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self._configure_grid_weights(self.main_frame, columns={0: 1})
        
        # Create UI elements
        self._create_ui_elements()
    
    def _create_ui_elements(self) -> None:
        """Create all UI elements in order using extracted helpers"""
        self._create_section(self._create_title)
        self._create_section(self._create_url_section)
        self._create_section(self._create_control_buttons)
        self._create_section(self._create_management_buttons)
        self._create_section(self._create_swap_section)

    def _create_section(self, section_func: Callable) -> None:
        """Helper to create a UI section and allow for future extension"""
        section_func()

    @staticmethod
    def _create_widget(widget_type: str, parent, **kwargs):
        """Unified widget creation method with Rose Pine styling"""
        if widget_type == "frame":
            fg_color = Theme.COLOR_MAP.get(kwargs.pop("fg_color", "transparent"), kwargs.pop("fg_color", "transparent"))
            border_color = kwargs.pop("border_color", Theme.HIGHLIGHT_MED)
            return ctk.CTkFrame(parent, fg_color=fg_color, border_color=border_color, **kwargs)
        
        elif widget_type == "button":
            text = kwargs.pop("text", "")
            command = kwargs.pop("command", None)
            height = kwargs.pop("height", BUTTON_HEIGHT)
            style = kwargs.pop("style", "primary")
            font_size = kwargs.pop("font_size", 12)
            border_color = kwargs.pop("border_color", Theme.HIGHLIGHT_MED)
            colors = Theme.BUTTON_STYLES.get(style, Theme.BUTTON_STYLES["primary"])
            
            return ctk.CTkButton(parent, text=text, command=command, height=height,
                               font=ctk.CTkFont(size=font_size, weight="bold"),
                               border_color=border_color, **colors, **kwargs)
        
        elif widget_type == "label":
            text = kwargs.pop("text", "")
            size = kwargs.pop("size", 12)
            text_color = kwargs.pop("text_color", Theme.TEXT)
            return ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=size, weight="bold"),
                              text_color=text_color, **kwargs)
        
        elif widget_type == "entry":
            placeholder_text = kwargs.pop("placeholder_text", "")
            height = kwargs.pop("height", 32)
            return ctk.CTkEntry(parent, placeholder_text=placeholder_text, font=ctk.CTkFont(size=11),
                              fg_color=Theme.OVERLAY, border_color=Theme.HIGHLIGHT_MED,
                              text_color=Theme.TEXT, placeholder_text_color=Theme.MUTED,
                              height=height, **kwargs)
        
        elif widget_type == "combobox":
            values = kwargs.pop("values", [])
            variable = kwargs.pop("variable", None)
            width = kwargs.pop("width", 120)
            height = kwargs.pop("height", 32)
            return ctk.CTkComboBox(parent, values=values, variable=variable,
                                 font=ctk.CTkFont(size=10), fg_color=Theme.OVERLAY,
                                 border_color=Theme.HIGHLIGHT_MED, button_color=Theme.PINE,
                                 button_hover_color=Theme.FOAM, text_color=Theme.TEXT,
                                 dropdown_fg_color=Theme.SURFACE, dropdown_text_color=Theme.TEXT,
                                 dropdown_hover_color=Theme.HIGHLIGHT_MED, height=height,
                                 width=width, state="readonly", **kwargs)
        
        raise ValueError(f"Unknown widget type: {widget_type}")

    # Backward compatibility aliases
    def _create_frame(self, parent, **kwargs): return self._create_widget("frame", parent, **kwargs)
    def _create_button(self, parent, **kwargs): return self._create_widget("button", parent, **kwargs)
    def _create_label(self, parent, **kwargs): return self._create_widget("label", parent, **kwargs)
    def _create_entry(self, parent, **kwargs): return self._create_widget("entry", parent, **kwargs)
    def _create_combobox(self, parent, **kwargs): return self._create_widget("combobox", parent, **kwargs)
    
    def _create_ui_row(self, parent, widgets: List[dict], grid_config: dict = None) -> ctk.CTkFrame:
        """Create a row of UI elements with automatic grid configuration"""
        row_frame = self._create_frame(parent)
        
        # Configure grid weights
        if grid_config:
            self._configure_grid_weights(row_frame, **grid_config)
        else:
            # Default: equal columns
            self._configure_grid_weights(row_frame, columns={i: 1 for i in range(len(widgets))})
        
        for i, widget_config in enumerate(widgets):
            widget_type = widget_config.pop('type', 'button')
            grid_opts = widget_config.pop('grid', {})
            
            if widget_type == 'label':
                widget = self._create_label(row_frame, **widget_config)
            elif widget_type == 'entry':
                widget = self._create_entry(row_frame, **widget_config)
            elif widget_type == 'combobox':
                widget = self._create_combobox(row_frame, **widget_config)
            else:  # default to button
                widget = self._create_button(row_frame, **widget_config)
            
            # Apply grid configuration
            default_grid = {'row': 0, 'column': i, 'sticky': 'ew'}
            default_grid.update(grid_opts)
            widget.grid(**default_grid)
        
        return row_frame
    
    def _create_title(self) -> None:
        """Create title label"""
        title_label = self._create_label(self.main_frame, text=f"🎭 {APP_NAME}", size=22, text_color=Theme.ROSE)
        title_label.grid(row=0, column=0, pady=(15, 20))
    
    def _create_url_section(self) -> None:
        """Create URL input section"""
        url_frame = self._create_frame(self.main_frame)
        self._setup_grid_section(url_frame, row=1)
        
        self._create_label(url_frame, text="Twitch Stream URL:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        input_row = self._create_frame(url_frame)
        input_row.grid(row=1, column=0, sticky="ew")
        self._configure_grid_weights(input_row, columns={0: 1})
        
        self.url_entry = self._create_entry(input_row, placeholder_text="https://www.twitch.tv/streamer_name")
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.quality_var = tk.StringVar(value="best")
        self.quality_combo = self._create_combobox(input_row, values=QUALITY_OPTIONS, variable=self.quality_var)
        self.quality_combo.grid(row=0, column=1)
    
    def _create_control_buttons(self) -> None:
        """Create control buttons"""
        self.button_frame = self._create_frame(self.main_frame)
        self._setup_grid_section(self.button_frame, row=2)
        
        self.watch_button = self._create_button(self.button_frame, text="🎬 Watch Stream", command=self._toggle_stream)
        self.watch_button.grid(row=0, column=0, sticky="ew")
        
        # Stop/Switch buttons row
        self.control_row = self._create_frame(self.button_frame)
        self.control_row.grid(row=1, column=0, sticky="ew")
        self._configure_grid_weights(self.control_row, columns={0: 1, 1: 1})
        
        self.stop_button = self._create_button(
            self.control_row,
            text="⏹ Stop Stream",
            command=self._stop_stream,
            style="destructive"
        )
        self.stop_button.grid(row=0, column=0, sticky="ew", padx=(0, PADDING // 2))
        
        self.switch_button = self._create_button(
            self.control_row,
            text="🔄 Switch Stream",
            command=self._switch_stream,
            style="warning"
        )
        self.switch_button.grid(row=0, column=1, sticky="ew", padx=(PADDING // 2, 0))
        
        # Initially hide stop/switch buttons
        self.control_row.grid_remove()
    
    def _create_management_buttons(self) -> None:
        """Create stream management buttons"""
        manage_frame = self._create_frame(self.main_frame)
        self._setup_grid_section(manage_frame, row=3)
        
        button_row_frame = self._create_frame(manage_frame)
        button_row_frame.grid(row=0, column=0, sticky="ew")
        self._configure_grid_weights(button_row_frame, columns={0: 1, 1: 1})
        
        self._create_button(button_row_frame, text="➕ Add to Quick Swap", command=self._add_stream, 
                          height=BUTTON_HEIGHT, width=180).grid(row=0, column=0, sticky="ew", padx=(0, PADDING // 2))
        
        self._create_button(button_row_frame, text="🔍 Check Status", command=self._check_streams_status,
                          height=BUTTON_HEIGHT, width=180, style="warning").grid(row=0, column=1, sticky="ew", padx=(PADDING // 2, 0))
    
    def _create_swap_section(self) -> None:
        """Create swap streams section"""
        swap_frame = self._create_frame(self.main_frame)
        self._setup_grid_section(swap_frame, row=4)
        self._configure_grid_weights(swap_frame, uniform_columns={0: (1, "swap_cols"), 1: (1, "swap_cols")})
        
        # Create swap buttons
        self.swap_buttons = []
        self.remove_buttons = []
        
        for i in range(MAX_SWAP_STREAMS):
            self._create_swap_button_pair(swap_frame, i)
    
    def _create_swap_button_pair(self, parent_frame: ctk.CTkFrame, index: int) -> None:
        """Create a swap button with its remove button using Rose Pine theme"""
        row = index // 2
        col = index % 2
        
        # Container for each swap button with consistent sizing
        button_container = self._create_frame(parent_frame)
        button_container.grid(
            row=row, 
            column=col, 
            sticky="ew", 
            padx=(0, 8) if col == 0 else (8, 0), 
            pady=(0, 8) if row == 0 else (8, 0)
        )
        # Ensure consistent column configuration for all containers
        self._configure_container_grid(button_container)
        
        # Main swap button with Rose Pine theme
        swap_button = self._create_button(
            button_container,
            text="Empty Slot",
            command=lambda idx=index: self._load_swap_stream(idx),
            font_size=10,
            height=45,
            style="disabled"
        )
        swap_button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0)  # Span both columns when empty
        swap_button.configure(state="disabled")
        self.swap_buttons.append(swap_button)
        
        # Status indicator as a transparent overlay on the button
        status_label = tk.Label(
            swap_button,  # Place directly on the button
            text="●",
            font=("Arial", 12, "bold"),  # Increased font size for bigger dot
            fg=Theme.STATUS_UNKNOWN,
            bg=swap_button.cget("fg_color"),  # Match button background
            highlightthickness=0,
            bd=0,
            padx=0,
            pady=0
        )
        # Position it over the button's top-left corner with better alignment
        status_label.place(x=3, y=3)
        
        # Make the status indicator pass through clicks to the button below
        def on_status_click(event):
            # Get the button coordinates and trigger its command
            swap_button.invoke()
        
        status_label.bind("<Button-1>", on_status_click)
        
        # Add hover event handlers to sync background with button hover state
        def on_button_enter(event):
            if swap_button.cget("state") == "normal":
                # When button is hovered, update indicator background to match hover color
                hover_color = swap_button.cget("hover_color")
                status_label.configure(bg=hover_color)
        
        def on_button_leave(event):
            if swap_button.cget("state") == "normal":
                # When hover ends, restore original button background
                normal_color = swap_button.cget("fg_color")
                status_label.configure(bg=normal_color)
        
        # Bind hover events to button
        swap_button.bind("<Enter>", on_button_enter)
        swap_button.bind("<Leave>", on_button_leave)
        
        # Store references
        if not hasattr(self, 'status_labels'):
            self.status_labels = []
        
        self.status_labels.append(status_label)
        
        # Remove button with Rose Pine theme
        remove_button = self._create_button(
            button_container,
            text="✕",
            command=lambda idx=index: self._remove_swap_stream(idx),
            style="destructive",
            height=45,
            width=25
        )
        remove_button.grid(row=0, column=1, sticky="ew")
        remove_button.grid_remove()
        self.remove_buttons.append(remove_button)
    
    def _get_setting_with_validation(self, key: str, default: Any, validator: Callable[[Any], bool] = None) -> Any:
        """Get setting with optional validation - Optimized"""
        value = self.settings_manager.get(key, default)
        if validator and not validator(value):
            return default
        return value
    
    def _load_initial_settings(self) -> None:
        """Load initial settings with validation - Optimized"""
        # Batch load common settings
        last_url = self._get_setting_with_validation(
            "last_url", "", 
            lambda url: ValidationManager.validate_url(url)[0] if url else True
        )
        quality = self._get_setting_with_validation(
            "last_quality", "best", 
            lambda q: q in QUALITY_OPTIONS
        )
        
        # Apply settings to UI
        if last_url:
            self.url_entry.insert(0, last_url)
        self.quality_var.set(quality)
        
        # Update swap buttons
        self._update_swap_buttons()
    
    def _update_swap_button_state(self, index: int, url: str = None) -> None:
        """Update a single swap button state - Optimized"""
        button = self.swap_buttons[index]
        
        if url:
            # Filled state - use cached theme values
            streamer_name = ValidationManager.extract_streamer_name(url)
            button.configure(
                text=streamer_name,
                state="normal",
                **Theme.BUTTON_PRIMARY,
                border_color=Theme.PINE
            )
            button.grid(row=0, column=0, columnspan=1, sticky="ew", padx=(0, 2))
            self.remove_buttons[index].grid()
            
            # Show and update status indicator
            if hasattr(self, 'status_labels') and index < len(self.status_labels):
                self._show_status_indicator(index, url)
        else:
            # Empty state - use cached theme values
            button.configure(
                text="Empty Slot",
                state="disabled",
                **Theme.BUTTON_DISABLED,
                border_color=Theme.HIGHLIGHT_MED
            )
            button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0)
            self.remove_buttons[index].grid_remove()
            
            # Hide status indicator
            if hasattr(self, 'status_labels') and index < len(self.status_labels):
                self.status_labels[index].place_forget()
    
    def _show_status_indicator(self, index: int, url: str) -> None:
        """Show and configure status indicator for a button"""
        if not hasattr(self, 'status_labels') or index >= len(self.status_labels):
            return
            
        label = self.status_labels[index]
        button = self.swap_buttons[index]
        
        # Match button background color and show indicator
        button_bg = button.cget("fg_color")
        label.configure(bg=button_bg)
        label.place(x=3, y=3)
        
        # Update color based on current status
        status = self.quick_swap_manager.get_stream_status(url)
        self._update_status_indicator(index, status)
    
    def _update_swap_buttons(self) -> None:
        """Update swap buttons display with Rose Pine theme and status indicators - Optimized"""
        streams = self.quick_swap_manager.get_streams()
        streams_count = len(streams)
        
        # Batch update all buttons to minimize UI operations
        for i, button in enumerate(self.swap_buttons):
            url = streams[i] if i < streams_count else None
            self._update_swap_button_state(i, url)
    
    def _batch_update_status_indicators(self, status_updates: Dict[str, StreamStatus]) -> None:
        """Batch update multiple status indicators - Optimized"""
        streams = self.quick_swap_manager.get_streams()
        
        # Find indices and update in batch
        updates = []
        for url, status in status_updates.items():
            try:
                index = streams.index(url)
                updates.append((index, status))
            except ValueError:
                continue
        
        # Apply all updates at once
        for index, status in updates:
            self._update_status_indicator(index, status)
    
    def _update_status_indicator(self, index: int, status: StreamStatus) -> None:
        """Update the status indicator for a specific swap button - Optimized"""
        if (not hasattr(self, 'status_labels') or 
            index >= len(self.status_labels)):
            return
        
        label = self.status_labels[index]
        current_color = label.cget("fg")
        
        # Use optimized color mapping
        new_color = Theme.get_status_color(status)
        
        # Only update if color actually changed (prevents unnecessary redraws)
        if current_color != new_color:
            button = self.swap_buttons[index]
            button_bg = button.cget("fg_color")
            label.configure(fg=new_color, bg=button_bg)
    
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
            self._show_warning("Please enter a stream URL")
            return None, None
        
        # Validate URL format
        is_valid, error_msg = ValidationManager.validate_url(url)
        if not is_valid:
            self._show_validation_error(error_msg)
            return None, None
        
        quality = self.quality_var.get()
        return url, quality
    
    def _save_stream_settings(self, url: str, quality: str) -> None:
        """Save stream settings - URL is already validated"""
        self.settings_manager.set("last_url", url)
        self.settings_manager.set("last_quality", quality)
    
    def _execute_stream_action(self, action_func: Callable[[str, str], bool]) -> bool:
        """Execute stream action with validation and settings save"""
        url, quality = self._get_validated_url_and_quality()
        if not url or not quality:
            return False
        
        self._save_stream_settings(url, quality)
        return action_func(url, quality)
    
    def _watch_stream(self) -> None:
        """Watch stream with validation"""
        self._execute_stream_action(self.stream_manager.start_stream)
    
    def _stop_stream(self) -> None:
        """Stop stream"""
        self.stream_manager.stop_stream()
    
    def _switch_stream(self) -> None:
        """Switch to new stream with validation"""
        self._execute_stream_action(self.stream_manager.switch_stream)
    
    def _show_message(self, message_type: str, title: str, message: str) -> None:
        """Unified message display method"""
        message_funcs = {
            "error": messagebox.showerror,
            "warning": messagebox.showwarning,
            "info": messagebox.showinfo
        }
        message_funcs.get(message_type, messagebox.showinfo)(title, message)
    
    def _show_validation_error(self, message: str) -> None:
        """Show validation error message"""
        self._show_message("error", "Invalid URL", message)
    
    def _show_warning(self, message: str) -> None:
        """Show warning message"""
        self._show_message("warning", "Warning", message)
    
    def _show_error(self, title: str, message: str) -> None:
        """Show error message"""
        self._show_message("error", title, message)
    
    def _handle_swap_action(self, action: str, index: int = None) -> None:
        """Unified handler for all swap actions"""
        if action == "add":
            url, _ = self._get_validated_url_and_quality()
            if not url:
                return
            
            if self.quick_swap_manager.has_stream(url):
                return  # Already exists
            
            if self.quick_swap_manager.is_full():
                self._show_warning(f"All {MAX_SWAP_STREAMS} quick swap slots are occupied. Remove a stream to add a new one.")
                return
            
            if self.quick_swap_manager.add_stream(url):
                self._update_swap_buttons()
        
        elif action == "load" and index is not None:
            if not self.quick_swap_manager.is_valid_index(index):
                return
            
            url = self.quick_swap_manager.get_stream(index)
            if not url:
                return
            
            # Update UI and start/switch stream
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
            self.settings_manager.set("last_url", url)
            
            quality = self.quality_var.get()
            if self.stream_manager.is_running():
                self.stream_manager.switch_stream(url, quality)
            else:
                self.stream_manager.start_stream(url, quality)
        
        elif action == "remove" and index is not None:
            if self.quick_swap_manager.is_valid_index(index):
                if self.quick_swap_manager.remove_by_index(index):
                    self._update_swap_buttons()
    
    def _check_streams_status(self) -> None:
        """Check the online status of all quick swap streams"""
        if not self.quick_swap_manager.get_streams():
            self._show_warning("No streams in quick swap to check.")
            return
        
        # Check all streams status
        self.quick_swap_manager.check_all_streams_status(self._on_stream_status_update)
    
    def _on_stream_status_update(self, url: str, status: StreamStatus) -> None:
        """Handle stream status update callback"""
        # Find the index of the stream
        streams = self.quick_swap_manager.get_streams()
        try:
            index = streams.index(url)
            # Update UI from main thread
            self.root.after(0, lambda: self._update_status_indicator(index, status))
        except ValueError:
            # Stream not found in list
            pass
    
    def _add_stream(self) -> None:
        """Add current stream to quick swap"""
        self._handle_swap_action("add")
    
    def _load_swap_stream(self, index: int) -> None:
        """Load a stream from quick swap"""
        self._handle_swap_action("load", index)
    
    def _remove_swap_stream(self, index: int) -> None:
        """Remove a stream from quick swap"""
        self._handle_swap_action("remove", index)
    
    def _update_ui_state(self, is_streaming: bool, streamer_name: str = "") -> None:
        """Update UI state based on streaming status"""
        if is_streaming:
            self.watch_button.grid_remove()
            self.control_row.grid()
            self.root.title(f"{APP_NAME} - Watching {streamer_name}")
        else:
            self.watch_button.grid()
            self.control_row.grid_remove()
            self.root.title(APP_NAME)
    
    def _on_stream_started(self, url: str, quality: str) -> None:
        """Handle stream started event"""
        streamer_name = ValidationManager.extract_streamer_name(url)
        self._update_ui_state(True, streamer_name)
    
    def _on_stream_stopped(self) -> None:
        """Handle stream stopped event"""
        self._update_ui_state(False)
    
    def _on_stream_error(self, error: str) -> None:
        """Handle stream error event"""
        self._update_ui_state(False)
        self._show_error("Stream Error", f"Failed to start stream:\n{error}")
    
    def _safe_cleanup_and_exit(self) -> None:
        """Safely cleanup resources and exit application"""
        try:
            if self.stream_manager.is_running():
                self.stream_manager.stop_stream()
            self.settings_manager.save()
            self.root.destroy()
        except Exception as e:
            _log_error("Error during cleanup", e)
            self.root.destroy()
    
    def _on_closing(self) -> None:
        """Handle application closing with proper cleanup"""
        self._safe_cleanup_and_exit()
    
    def run(self) -> None:
        """Start the application main loop"""
        try:
            self.root.mainloop()
        except Exception as e:
            _log_error("Critical error", e)
            self._show_error("Critical Error", f"Application encountered a critical error:\n{e}")


def main():
    """Main application entry point with error handling"""
    try:
        app = StreaMaski()
        app.run()
    except Exception as e:
        _log_error("Failed to start application", e)
        messagebox.showerror("Startup Error", f"Failed to start {APP_NAME}:\n{e}")


if __name__ == "__main__":
    main()
