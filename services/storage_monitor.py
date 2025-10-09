"""
Storage Monitor Service
Monitors and prevents storage accumulation for DualMind
"""

import os
import glob
import tempfile
import time
from typing import Dict, List

class StorageMonitor:
    """Monitor and prevent storage accumulation"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.monitored_extensions = ['.wav', '.mp3', '.m4a', '.webm', '.mp4', '.tmp', '.part']
        
    def get_storage_usage(self) -> Dict[str, int]:
        """Get current temporary file storage usage"""
        usage = {
            'temp_files_count': 0,
            'temp_files_size_mb': 0,
            'our_files_count': 0,
            'our_files_size_mb': 0
        }
        
        try:
            # Check temporary directory
            for ext in self.monitored_extensions:
                pattern = os.path.join(self.temp_dir, f"*{ext}")
                files = glob.glob(pattern)
                
                for file_path in files:
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        usage['temp_files_count'] += 1
                        usage['temp_files_size_mb'] += file_size / (1024 * 1024)
                        
                        # Check if it's our file
                        filename = os.path.basename(file_path)
                        if any(keyword in filename.lower() for keyword in ['dualmind', 'temp_audio', 'whisper']):
                            usage['our_files_count'] += 1
                            usage['our_files_size_mb'] += file_size / (1024 * 1024)
                            
        except Exception:
            pass
            
        return usage
    
    def force_immediate_cleanup(self) -> Dict[str, int]:
        """Force immediate cleanup of all temporary files"""
        cleaned = {
            'files_removed': 0,
            'mb_freed': 0
        }
        
        try:
            patterns = [
                # All audio formats
                os.path.join(self.temp_dir, "*.wav"),
                os.path.join(self.temp_dir, "*.mp3"),
                os.path.join(self.temp_dir, "*.m4a"),
                os.path.join(self.temp_dir, "*.webm"),
                os.path.join(self.temp_dir, "*.mp4"),
                os.path.join(self.temp_dir, "*.aac"),
                
                # Temporary files
                os.path.join(self.temp_dir, "*.tmp"),
                os.path.join(self.temp_dir, "*.part"),
                os.path.join(self.temp_dir, "temp_audio_*"),
                os.path.join(self.temp_dir, "whisper_*"),
                os.path.join(self.temp_dir, "*dualmind*"),
                
                # Current directory files
                "temp_audio_*",
                "*.wav",
                "*.mp3",
                "*.tmp"
            ]
            
            for pattern in patterns:
                files = glob.glob(pattern)
                for file_path in files:
                    try:
                        if os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            cleaned['files_removed'] += 1
                            cleaned['mb_freed'] += file_size / (1024 * 1024)
                    except Exception:
                        continue
                        
        except Exception:
            pass
            
        return cleaned
    
    def is_storage_accumulating(self) -> bool:
        """Check if storage is accumulating beyond safe limits"""
        usage = self.get_storage_usage()
        
        # Alert if we have more than 50MB or 20 files
        return (usage['our_files_size_mb'] > 50 or 
                usage['our_files_count'] > 20)

# Global storage monitor instance
storage_monitor = StorageMonitor()

def get_storage_status():
    """Get current storage status"""
    return storage_monitor.get_storage_usage()

def cleanup_all_temp_files():
    """Force cleanup of all temporary files"""
    return storage_monitor.force_immediate_cleanup()

def check_storage_health():
    """Check if storage is healthy (not accumulating)"""
    return not storage_monitor.is_storage_accumulating()