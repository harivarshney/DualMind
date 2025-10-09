"""
DualMind - PyQt5 Desktop Application
AI-powered YouTube transcription and PDF processing application
"""

import sys
import os
import json
import threading
import time
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QPushButton, QTextEdit, QProgressBar,
                             QFileDialog, QMessageBox, QTabWidget, QLineEdit,
                             QSplitter, QFrame, QGridLayout, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
# Removed QWebEngineView - not needed for our application

# Import your existing services
from services.youtube_processor import YouTubeProcessor
from services.pdf_processor import PDFProcessor
from services.result_exporter import ResultExporter
from services.progress_manager import progress_manager
from services.auto_cleanup import start_cleanup_service, stop_cleanup_service, force_cleanup
from services.storage_monitor import get_storage_status, cleanup_all_temp_files

class ProcessingThread(QThread):
    """Background thread for processing tasks"""
    progress_updated = pyqtSignal(int, str)  # progress, message
    processing_completed = pyqtSignal(str, dict)  # result, metadata
    processing_failed = pyqtSignal(str)  # error message
    
    def __init__(self, task_type, data, parent=None):
        super().__init__(parent)
        self.task_type = task_type  # 'youtube' or 'pdf'
        self.data = data
        self.youtube_processor = YouTubeProcessor()
        self.pdf_processor = PDFProcessor()
        self._stop_requested = False
    
    def request_stop(self):
        """Request thread to stop gracefully"""
        self._stop_requested = True
        
    def run(self):
        """Run the processing task in background"""
        try:
            if self.task_type == 'youtube':
                self._process_youtube()
            elif self.task_type == 'pdf':
                self._process_pdf()
        except Exception as e:
            self.processing_failed.emit(str(e))
    
    def _process_youtube(self):
        """Process YouTube video"""
        url = self.data['url']
        
        try:
            # Step 1: Validate URL
            self.progress_updated.emit(10, "Validating YouTube URL...")
            
            # Step 2: Get video info
            self.progress_updated.emit(20, "Getting video information...")
            video_info = self.youtube_processor.get_video_info(url)
            
            # Step 3: Download and transcribe
            self.progress_updated.emit(40, "Downloading and processing audio...")
            result = self.youtube_processor.transcribe_video(url)
            
            # Step 4: Complete
            self.progress_updated.emit(100, "Processing completed!")
            
            metadata = {
                'type': 'youtube',
                'video_info': video_info,
                'duration': video_info.get('duration', 'Unknown'),
                'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.processing_completed.emit(result, metadata)
            
            # Force immediate cleanup after processing
            force_cleanup()
            cleanup_all_temp_files()
            
        except Exception as e:
            # Cleanup even on failure
            force_cleanup()
            cleanup_all_temp_files()
            self.processing_failed.emit(f"YouTube processing failed: {str(e)}")
    
    def _process_pdf(self):
        """Process PDF file"""
        file_path = self.data['file_path']
        
        try:
            # Step 1: Validate file
            self.progress_updated.emit(10, "Validating PDF file...")
            
            # Step 2: Extract text
            self.progress_updated.emit(30, "Extracting text from PDF...")
            
            # Step 3: Generate summary
            self.progress_updated.emit(60, "Analyzing and generating summary...")
            result = self.pdf_processor.summarize_pdf(file_path)
            
            # Step 4: Complete
            self.progress_updated.emit(100, "Processing completed!")
            
            pdf_info = self.pdf_processor.get_pdf_info(file_path)
            metadata = {
                'type': 'pdf',
                'file_name': os.path.basename(file_path),
                'file_size': pdf_info.get('size', 'Unknown'),
                'pages': pdf_info.get('pages', 'Unknown'),
                'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.processing_completed.emit(result, metadata)
            
            # Force immediate cleanup after processing
            force_cleanup()
            cleanup_all_temp_files()
            
        except Exception as e:
            # Cleanup even on failure
            force_cleanup()
            cleanup_all_temp_files()
            self.processing_failed.emit(f"PDF processing failed: {str(e)}")

class DualMindMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.current_result = ""
        self.current_metadata = {}
        self.result_exporter = ResultExporter()
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("DualMind - AI Desktop Application")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout()
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Input and Controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Results
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([600, 800])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(__file__), "fevicon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            self.setWindowIcon(QIcon())  # Fallback to default
        
    def create_left_panel(self):
        """Create left control panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🧠 DualMind AI")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("AI-Powered PDF Analysis & YouTube Transcription")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #6c757d; margin-bottom: 30px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # YouTube section
        youtube_group = QGroupBox("🎥 YouTube Video Transcription")
        youtube_group.setFont(QFont("Arial", 14, QFont.Bold))
        youtube_layout = QVBoxLayout()
        
        self.youtube_url_input = QLineEdit()
        self.youtube_url_input.setPlaceholderText("Enter YouTube URL here...")
        self.youtube_url_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                font-size: 14px;
                margin-bottom: 10px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        youtube_layout.addWidget(self.youtube_url_input)
        
        self.youtube_process_btn = QPushButton("🎬 Start Transcription")
        self.youtube_process_btn.clicked.connect(self.process_youtube)
        youtube_layout.addWidget(self.youtube_process_btn)
        
        youtube_group.setLayout(youtube_layout)
        layout.addWidget(youtube_group)
        
        # PDF section
        pdf_group = QGroupBox("📄 PDF Document Analysis")
        pdf_group.setFont(QFont("Arial", 14, QFont.Bold))
        pdf_layout = QVBoxLayout()
        
        self.pdf_path_label = QLabel("No file selected")
        self.pdf_path_label.setStyleSheet("color: #6c757d; margin-bottom: 10px;")
        pdf_layout.addWidget(self.pdf_path_label)
        
        pdf_button_layout = QHBoxLayout()
        
        self.pdf_select_btn = QPushButton("📁 Select PDF File")
        self.pdf_select_btn.clicked.connect(self.select_pdf_file)
        pdf_button_layout.addWidget(self.pdf_select_btn)
        
        self.pdf_process_btn = QPushButton("📊 Analyze PDF")
        self.pdf_process_btn.clicked.connect(self.process_pdf)
        self.pdf_process_btn.setEnabled(False)
        pdf_button_layout.addWidget(self.pdf_process_btn)
        
        pdf_layout.addLayout(pdf_button_layout)
        pdf_group.setLayout(pdf_layout)
        layout.addWidget(pdf_group)
        
        # Progress section
        progress_group = QGroupBox("⏳ Processing Status")
        progress_group.setFont(QFont("Arial", 14, QFont.Bold))
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 6px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to process...")
        self.status_label.setStyleSheet("color: #28a745; margin-top: 10px;")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        """Create right results panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Create tab widget for Results
        tab_widget = QTabWidget()
        
        # Results tab
        results_tab = QWidget()
        results_layout = QVBoxLayout()
        
        # Results header
        results_header = QHBoxLayout()
        
        results_title = QLabel("📋 Results")
        results_title.setFont(QFont("Arial", 18, QFont.Bold))
        results_title.setStyleSheet("color: #2c3e50;")
        results_header.addWidget(results_title)
        
        results_header.addStretch()
        
        # Export buttons
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.clicked.connect(self.copy_results)
        self.copy_btn.setEnabled(False)
        results_header.addWidget(self.copy_btn)
        
        self.save_pdf_btn = QPushButton("📄 Save as PDF")
        self.save_pdf_btn.clicked.connect(self.save_as_pdf)
        self.save_pdf_btn.setEnabled(False)
        results_header.addWidget(self.save_pdf_btn)
        
        self.save_word_btn = QPushButton("📝 Save as Word")
        self.save_word_btn.clicked.connect(self.save_as_word)
        self.save_word_btn.setEnabled(False)
        results_header.addWidget(self.save_word_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_results)
        self.clear_btn.setEnabled(False)
        results_header.addWidget(self.clear_btn)
        
        results_layout.addLayout(results_header)
        
        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setPlaceholderText("Results will appear here after processing...")
        results_layout.addWidget(self.results_text)
        
        results_tab.setLayout(results_layout)
        tab_widget.addTab(results_tab, "📋 Results")
        
        layout.addWidget(tab_widget)
        panel.setLayout(layout)
        return panel
    
    def apply_styles(self):
        """Apply consistent styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: #ffffff;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                line-height: 1.4;
            }
            QTabWidget::pane {
                border: 2px solid #e9ecef;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #007bff;
                color: white;
            }
        """)
    
    def select_pdf_file(self):
        """Select PDF file for processing"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)")
        
        if file_path:
            self.selected_pdf_path = file_path
            file_name = os.path.basename(file_path)
            self.pdf_path_label.setText(f"Selected: {file_name}")
            self.pdf_process_btn.setEnabled(True)
    
    def process_youtube(self):
        """Start YouTube processing"""
        url = self.youtube_url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a YouTube URL")
            return
        
        if not self.is_valid_youtube_url(url):
            QMessageBox.warning(self, "Warning", "Please enter a valid YouTube URL")
            return
        
        # Disable buttons during processing
        self.youtube_process_btn.setEnabled(False)
        self.pdf_process_btn.setEnabled(False)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting YouTube transcription...")
        
        # Start processing thread
        self.processing_thread = ProcessingThread('youtube', {'url': url})
        self.processing_thread.progress_updated.connect(self.update_progress)
        self.processing_thread.processing_completed.connect(self.processing_completed)
        self.processing_thread.processing_failed.connect(self.processing_failed)
        self.processing_thread.start()
    
    def process_pdf(self):
        """Start PDF processing"""
        if not hasattr(self, 'selected_pdf_path'):
            QMessageBox.warning(self, "Warning", "Please select a PDF file first")
            return
        
        # Disable buttons during processing
        self.youtube_process_btn.setEnabled(False)
        self.pdf_process_btn.setEnabled(False)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting PDF analysis...")
        
        # Start processing thread
        self.processing_thread = ProcessingThread('pdf', {'file_path': self.selected_pdf_path})
        self.processing_thread.progress_updated.connect(self.update_progress)
        self.processing_thread.processing_completed.connect(self.processing_completed)
        self.processing_thread.processing_failed.connect(self.processing_failed)
        self.processing_thread.start()
    
    def update_progress(self, progress, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    def processing_completed(self, result, metadata):
        """Handle completed processing"""
        self.current_result = result
        self.current_metadata = metadata
        
        # Display results
        self.results_text.setText(result)
        
        # Update status
        self.status_label.setText("✅ Processing completed successfully!")
        self.progress_bar.setValue(100)
        
        # Enable buttons
        self.youtube_process_btn.setEnabled(True)
        self.pdf_process_btn.setEnabled(True)
        
        # Enable export buttons
        self.copy_btn.setEnabled(True)
        self.save_pdf_btn.setEnabled(True)
        self.save_word_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        
        # Show completion message
        QMessageBox.information(self, "Success", 
                              f"{metadata['type'].title()} processing completed successfully!")
    
    def processing_failed(self, error_message):
        """Handle processing failure"""
        # Update status
        self.status_label.setText(f"❌ Processing failed: {error_message}")
        self.progress_bar.setValue(0)
        
        # Enable buttons
        self.youtube_process_btn.setEnabled(True)
        if hasattr(self, 'selected_pdf_path'):
            self.pdf_process_btn.setEnabled(True)
        
        # Show error message
        QMessageBox.critical(self, "Error", f"Processing failed:\n{error_message}")
    
    def copy_results(self):
        """Copy results to clipboard"""
        if self.current_result:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_result)
            self.status_label.setText("📋 Results copied to clipboard!")
    
    def save_as_pdf(self):
        """Save results as PDF"""
        if not self.current_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save as PDF", "", "PDF Files (*.pdf)")
        
        if file_path:
            try:
                self.result_exporter.save_as_pdf(self.current_result, file_path)
                self.status_label.setText(f"📄 Saved as PDF: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Success", "Results saved as PDF successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save PDF:\n{str(e)}")
    
    def save_as_word(self):
        """Save results as Word document"""
        if not self.current_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save as Word", "", "Word Documents (*.docx)")
        
        if file_path:
            try:
                self.result_exporter.save_as_word(self.current_result, file_path)
                self.status_label.setText(f"📝 Saved as Word: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Success", "Results saved as Word document successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save Word document:\n{str(e)}")
    
    def clear_results(self):
        """Clear results and reset interface"""
        reply = QMessageBox.question(self, "Confirm Clear", 
                                   "Are you sure you want to clear the results?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.results_text.clear()
            self.current_result = ""
            self.current_metadata = {}
            
            # Disable export buttons
            self.copy_btn.setEnabled(False)
            self.save_pdf_btn.setEnabled(False)
            self.save_word_btn.setEnabled(False)
            self.clear_btn.setEnabled(False)
            
            self.status_label.setText("Results cleared. Ready to process...")
            self.progress_bar.setValue(0)
    
    def is_valid_youtube_url(self, url):
        """Validate YouTube URL"""
        youtube_patterns = [
            'youtube.com/watch',
            'youtu.be/',
            'youtube.com/embed/',
            'youtube.com/v/'
        ]
        return any(pattern in url.lower() for pattern in youtube_patterns)
    
    def closeEvent(self, event):
        """Handle application close"""
        # Stop any running processing threads immediately
        if hasattr(self, 'processing_thread') and self.processing_thread.isRunning():
            self.processing_thread.terminate()
            self.processing_thread.wait(2000)  # Wait max 2 seconds
        
        # Stop cleanup service quickly
        try:
            stop_cleanup_service()
        except Exception:
            pass  # Ignore cleanup errors during shutdown
        
        # Force immediate shutdown without confirmation for faster closing
        event.accept()
        
        # Use QTimer to force quit after a short delay if needed
        QTimer.singleShot(1000, QApplication.quit)  # Force quit after 1 second

class DualMindApp(QApplication):
    """Main application class"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("DualMind")
        self.setApplicationVersion("2.0")
        self.setOrganizationName("DualMind AI")
        
        # Set application icon for taskbar and window
        icon_path = os.path.join(os.path.dirname(__file__), "fevicon.png")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            
            # Set taskbar icon for Windows
            try:
                import ctypes
                myappid = 'dualmind.ai.transcription.2.0'  # Unique App ID
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception:
                pass  # Continue if Windows-specific code fails
        
        # Create and show main window
        self.main_window = DualMindMainWindow()
        self.main_window.show()

def main():
    """Main entry point"""
    app = DualMindApp(sys.argv)
    
    # Set up signal handlers for clean shutdown
    import signal
    
    def signal_handler(sig, frame):
        print("Shutting down gracefully...")
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Apply dark theme if desired
    # app.setStyle('Fusion')
    # palette = QPalette()
    # palette.setColor(QPalette.Window, QColor(53, 53, 53))
    # app.setPalette(palette)
    
    # Start cleanup service
    start_cleanup_service()
    
    try:
        result = app.exec_()
    finally:
        # Ensure cleanup service stops
        try:
            stop_cleanup_service()
        except Exception:
            pass
    
    sys.exit(result)

if __name__ == "__main__":
    main()