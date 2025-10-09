import os
import tempfile
import subprocess

class YouTubeProcessor:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.model = None
    
    def transcribe_video(self, youtube_url):
        if not self._is_valid_youtube_url(youtube_url):
            raise ValueError("Invalid YouTube URL format")
            
        audio_file = None
        
        try:
            print("📥 Downloading audio...")
            audio_file = self._download_audio(youtube_url)
            
            print("🤖 Starting AI transcription...")
            transcript_result = self._transcribe_audio(audio_file)
            
            print("📝 Formatting results...")
            formatted_result = self._format_transcript(transcript_result, youtube_url)
            
            return formatted_result
            
        except Exception as e:
            raise Exception(f"Failed to transcribe YouTube video: {str(e)}")
            
        finally:
            if audio_file and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except:
                    pass
        
    def _is_valid_youtube_url(self, url):
        return any(p in url.lower() for p in ['youtube.com/watch', 'youtu.be/'])
        
    def _download_audio(self, youtube_url):
        import yt_dlp
        
        audio_file = os.path.join(self.temp_dir, f"temp_audio_{os.getpid()}.wav")
        
        ydl_opts = {
            'format': 'bestaudio/best',  # Get good quality audio for better transcription
            'outtmpl': audio_file.replace('.wav', '.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio', 
                'preferredcodec': 'wav',
            }],
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        return audio_file
        
    def _transcribe_audio(self, audio_file):
        import whisper
        
        print("🚀 Processing audio with optimized settings...")
        
        # Load model once
        if not self.model:
            self.model = whisper.load_model("base")  # Better accuracy than tiny
            
        # Simple, reliable transcription that processes the ENTIRE file
        try:
            # Use optimal settings for complete transcription
            result = self.model.transcribe(
                audio_file,
                task='transcribe',
                fp16=False,
                verbose=None,  # Suppress Whisper's internal progress messages
                word_timestamps=False,  # Disable word-level timestamps for speed
                condition_on_previous_text=True,  # Better context for long audio
                temperature=0,  # Deterministic results
            )
            
            transcript_text = result['text'].strip()
            print(f"✅ Complete transcription finished! ({len(transcript_text):,} characters)")
            
            # Verify we got actual content
            if len(transcript_text) < 50:
                print("⚠️ Warning: Transcription seems too short, but proceeding...")
                
            return {"text": transcript_text, "language": result.get("language", "unknown")}
            
        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            raise
    

        
    def _format_transcript(self, transcript_result, youtube_url):
        text = transcript_result.get("text", "")
        language = transcript_result.get("language", "unknown")
        
        # Format the transcript text for better readability
        formatted_text = self._format_transcript_text(text)
        
        try:
            video_info = self.get_video_info(youtube_url)
            title = video_info.get("title", "YouTube Video")
        except:
            title = "YouTube Video"
            
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        return f"""YouTube Video Transcription
==================================================

Title: {title}
URL: {youtube_url}
Language: {language}
Processed: {timestamp}

Transcript:
------------------------------

{formatted_text}

--------------------------------------------------"""
    
    def _format_transcript_text(self, text):
        """Format transcript text with proper sentence breaks and paragraphs"""
        import re
        
        if not text or not text.strip():
            return "No transcript available."
        
        # Clean up the text first
        text = text.strip()
        
        # Add periods after sentences that don't have proper punctuation
        text = re.sub(r'([a-z])\s+([A-Z])', r'\1. \2', text)
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and format sentences
        formatted_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 3:  # Skip very short fragments
                # Capitalize first letter
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                formatted_sentences.append(sentence)
        
        # Group sentences into paragraphs (every 3-4 sentences)
        paragraphs = []
        current_paragraph = []
        
        for i, sentence in enumerate(formatted_sentences):
            current_paragraph.append(sentence)
            
            # Create a new paragraph every 3-4 sentences or if sentence is long
            if (len(current_paragraph) >= 3 and len(sentence) > 50) or len(current_paragraph) >= 4:
                paragraphs.append('. '.join(current_paragraph) + '.')
                current_paragraph = []
        
        # Add remaining sentences
        if current_paragraph:
            paragraphs.append('. '.join(current_paragraph) + '.')
        
        # Join paragraphs with double line breaks
        return '\n\n'.join(paragraphs)
        
    def get_video_info(self, youtube_url):
        import yt_dlp
        
        ydl_opts = {'quiet': True, 'no_warnings': True}
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            
        return {
            "title": info.get("title", "Unknown Title"),
            "uploader": info.get("uploader", "Unknown Channel"),
        }
