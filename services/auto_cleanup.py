"""
Automatic Storage Cleanup Service
Periodically cleans up temporary files to prevent storage bloat
"""

import os
import time
import glob
import threading
import tempfile
from datetime import datetime
from .storage_monitor import storage_monitor

class AutoCleanupService:
    """Automatic cleanup service that runs in background"""
    
    def __init__(self, cleanup_interval=30):  # 30 seconds - very frequent
        self.cleanup_interval = cleanup_interval
        self.running = False
        self.cleanup_thread = None
        
    def start_auto_cleanup(self):
        """Start the automatic cleanup service"""
        if not self.running:
            self.running = True
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
    
    def stop_auto_cleanup(self):
        """Stop the automatic cleanup service"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=2)  # Wait max 2 seconds
    
    def _cleanup_loop(self):
        """Main cleanup loop that runs periodically"""
        while self.running:
            try:
                self.cleanup_temp_files()
                
                # Sleep in smaller chunks to respond to stop signal faster
                for _ in range(int(self.cleanup_interval)):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception:
                # Wait in smaller chunks on error too
                for _ in range(60):
                    if not self.running:
                        break
                    time.sleep(1)
    
    def cleanup_temp_files(self):
        """Clean up temporary files across the system - AGGRESSIVE MODE"""
        cleaned_count = 0
        total_size = 0
        
        try:
            temp_dir = tempfile.gettempdir()
            current_time = time.time()
            
            # More aggressive patterns for temporary files to clean
            cleanup_patterns = [
                # Audio files (all formats)
                os.path.join(temp_dir, "temp_audio_*"),
                os.path.join(temp_dir, "*.wav"),
                os.path.join(temp_dir, "*.mp3"),
                os.path.join(temp_dir, "*.m4a"),
                os.path.join(temp_dir, "*.webm"),
                os.path.join(temp_dir, "*.mp4"),
                os.path.join(temp_dir, "*.aac"),
                os.path.join(temp_dir, "*.flac"),
                os.path.join(temp_dir, "*.ogg"),
                
                # Whisper temporary files
                os.path.join(temp_dir, "whisper_*"),
                os.path.join(temp_dir, "tmp*"),
                os.path.join(temp_dir, "*whisper*"),
                
                # YouTube-dl/yt-dlp temporary files
                os.path.join(temp_dir, "*.tmp"),
                os.path.join(temp_dir, "*.part"),
                os.path.join(temp_dir, "*youtube*"),
                os.path.join(temp_dir, "*ytdl*"),
                
                # DualMind specific files
                os.path.join(temp_dir, "DualMind_*"),
                os.path.join(temp_dir, "dualmind_*"),
                
                # Python temporary files
                os.path.join(temp_dir, "python_*"),
                os.path.join(temp_dir, "*.pyc"),
            ]
            
            for pattern in cleanup_patterns:
                try:
                    files = glob.glob(pattern)
                    for file_path in files:
                        try:
                            if os.path.isfile(file_path):
                                # Very aggressive - clean files older than 30 seconds
                                file_time = os.path.getmtime(file_path)
                                if current_time - file_time > 30:  # 30 seconds for immediate cleanup
                                    file_size = os.path.getsize(file_path)
                                    os.remove(file_path)
                                    cleaned_count += 1
                                    total_size += file_size
                        except Exception:
                            continue
                except Exception:
                    continue
            
            # Also clean up in current working directory
            try:
                cwd_patterns = ["temp_audio_*", "*.wav", "*.mp3", "*.tmp"]
                for pattern in cwd_patterns:
                    files = glob.glob(pattern)
                    for file_path in files:
                        try:
                            if os.path.isfile(file_path):
                                file_time = os.path.getmtime(file_path)
                                if current_time - file_time > 30:  # 30 seconds for immediate cleanup
                                    os.remove(file_path)
                                    cleaned_count += 1
                        except Exception:
                            continue
            except Exception:
                pass
                
        except Exception:
            pass  # Silent failure
    
    def force_cleanup_now(self):
        """Force an immediate cleanup silently"""
        self.cleanup_temp_files()
        
        # Also use storage monitor for aggressive cleanup
        try:
            storage_monitor.force_immediate_cleanup()
        except Exception:
            pass

# Global auto-cleanup service instance
auto_cleanup = AutoCleanupService()

def start_cleanup_service():
    """Start the global auto-cleanup service"""
    auto_cleanup.start_auto_cleanup()

def stop_cleanup_service():
    """Stop the global auto-cleanup service"""
    auto_cleanup.stop_auto_cleanup()

def force_cleanup():
    """Force immediate cleanup"""
    auto_cleanup.force_cleanup_now()