"""
DualMind - Utility Functions
Common utility functions used across the application
"""

import os
import re
import tempfile
from datetime import datetime
from typing import Optional, List
import urllib.parse

class Utils:
    """Utility functions for DualMind AI"""
    
    @staticmethod
    def validate_youtube_url(url: str) -> bool:
        """
        Validate if the URL is a valid YouTube URL
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid YouTube URL, False otherwise
        """
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=',
            r'(?:https?://)?(?:www\.)?youtu\.be/',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/',
            r'(?:https?://)?(?:m\.)?youtube\.com/watch\?v='
        ]
        
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in youtube_patterns)
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Optional[str]: Video ID if found, None otherwise
        """
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format
        
        Args:
            size_bytes (int): File size in bytes
            
        Returns:
            str: Formatted file size
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        Format duration in human-readable format
        
        Args:
            seconds (int): Duration in seconds
            
        Returns:
            str: Formatted duration (HH:MM:SS or MM:SS)
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """
        Clean filename by removing invalid characters
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Cleaned filename
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove multiple underscores and trim
        filename = re.sub(r'_+', '_', filename).strip('_')
        
        # Limit length
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:96] + ext
        
        return filename
    
    @staticmethod
    def create_temp_file(suffix: str = "", prefix: str = "dualmind_") -> str:
        """
        Create a temporary file path
        
        Args:
            suffix (str): File suffix/extension
            prefix (str): File prefix
            
        Returns:
            str: Temporary file path
        """
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}{timestamp}_{os.getpid()}{suffix}"
        return os.path.join(temp_dir, filename)
    
    @staticmethod
    def ensure_directory(path: str) -> None:
        """
        Ensure directory exists, create if it doesn't
        
        Args:
            path (str): Directory path
        """
        os.makedirs(path, exist_ok=True)
    
    @staticmethod
    def safe_delete_file(file_path: str) -> bool:
        """
        Safely delete a file, ignoring errors
        
        Args:
            file_path (str): Path to file to delete
            
        Returns:
            bool: True if file was deleted, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to maximum length
        
        Args:
            text (str): Text to truncate
            max_length (int): Maximum length
            suffix (str): Suffix to add if truncated
            
        Returns:
            str: Truncated text
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url (str): URL
            
        Returns:
            str: Domain name
        """
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    @staticmethod
    def is_valid_file_path(path: str) -> bool:
        """
        Check if file path is valid and file exists
        
        Args:
            path (str): File path to check
            
        Returns:
            bool: True if valid and exists, False otherwise
        """
        try:
            return os.path.isfile(path) and os.access(path, os.R_OK)
        except:
            return False
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Get file extension from filename
        
        Args:
            filename (str): Filename
            
        Returns:
            str: File extension (including dot)
        """
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def format_timestamp(timestamp: Optional[float] = None) -> str:
        """
        Format timestamp for display
        
        Args:
            timestamp (Optional[float]): Unix timestamp, current time if None
            
        Returns:
            str: Formatted timestamp
        """
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def word_count(text: str) -> int:
        """
        Count words in text
        
        Args:
            text (str): Text to count
            
        Returns:
            int: Word count
        """
        return len(text.split())
    
    @staticmethod
    def estimate_reading_time(text: str, wpm: int = 200) -> str:
        """
        Estimate reading time for text
        
        Args:
            text (str): Text to analyze
            wpm (int): Words per minute reading speed
            
        Returns:
            str: Estimated reading time
        """
        word_count = Utils.word_count(text)
        minutes = word_count / wpm
        
        if minutes < 1:
            return "< 1 minute"
        elif minutes < 60:
            return f"{int(minutes)} minute{'s' if minutes != 1 else ''}"
        else:
            hours = minutes / 60
            return f"{hours:.1f} hour{'s' if hours != 1 else ''}"
