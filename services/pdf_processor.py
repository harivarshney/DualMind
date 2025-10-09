"""
PDF Processor Service
Handles PDF document processing and AI summarization
"""

import os
from typing import Optional, List

class PDFProcessor:
    def __init__(self):
        """Initialize the PDF processor"""
        self.max_chunk_size = 4000  # Maximum characters per chunk for AI processing
        
    def summarize_pdf(self, pdf_path: str, progress_callback=None) -> str:
        """
        Extract text from PDF and generate local summary
        
        Args:
            pdf_path (str): Path to the PDF file
            progress_callback (callable): Optional callback for progress updates
            
        Returns:
            str: Generated summary of the PDF content
        """
        
        # Validate file
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF")
            
        # Get file info
        file_size = os.path.getsize(pdf_path)
        file_name = os.path.basename(pdf_path)
        
        try:
            # Step 1: Extract text from PDF
            if progress_callback:
                progress_callback("Extracting text from PDF...")
            text_content = self._extract_text_from_pdf(pdf_path)
            
            # Step 2: Get document info
            if progress_callback:
                progress_callback("Preparing document analysis...")
            document_info = self._get_document_info(text_content)
            
            # Step 3: Generate local summary (desktop processing)
            if progress_callback:
                progress_callback("Analyzing content and generating summary...")
            summary = self._generate_local_summary(text_content)
            
            if progress_callback:
                progress_callback("Formatting final results...")
            
            return self._format_summary(summary, file_name, len(text_content), document_info)
            
        except Exception as e:
            raise Exception(f"Failed to process PDF: {str(e)}")
        
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from PDF file
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            str: Extracted text content
        """
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 is required. Install with: pip install PyPDF2")
        
        text_content = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    try:
                        pdf_reader.decrypt("")  # Try empty password first
                    except:
                        raise Exception("PDF is password protected. Please provide an unprotected PDF.")
                
                total_pages = len(pdf_reader.pages)
                if total_pages == 0:
                    raise Exception("PDF appears to be empty or corrupted.")
                
                # Extract text from all pages
                for page_num in range(total_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text.strip():  # Only add non-empty pages
                            text_content += f"\n--- Page {page_num + 1} ---\n"
                            text_content += page_text.strip() + "\n"
                    except Exception as page_error:
                        print(f"Warning: Could not extract text from page {page_num + 1}: {page_error}")
                        continue
            
            if not text_content.strip():
                raise Exception("No text content could be extracted from the PDF. The PDF might contain only images or be corrupted.")
            
            return text_content.strip()
            
        except Exception as e:
            if "No text content could be extracted" in str(e) or "password protected" in str(e):
                raise e
            else:
                raise Exception(f"Failed to extract text from PDF: {str(e)}")
        
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into manageable chunks for AI processing
        
        Args:
            text (str): Full text content
            
        Returns:
            List[str]: List of text chunks
        """
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > self.max_chunk_size:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks
        
    def _generate_local_summary(self, text_content: str) -> str:
        """
        Generate comprehensive summary with main points and key insights
        
        Args:
            text_content (str): Full text content
            
        Returns:
            str: Generated summary focusing on main points
        """
        if not text_content.strip():
            return "No text content found in the PDF."
        
        # Advanced text analysis and summarization
        sentences = self._split_into_sentences(text_content)
        words = text_content.split()
        
        # Calculate basic statistics
        word_count = len(words)
        sentence_count = len(sentences)
        
        # Extract comprehensive analysis
        key_phrases = self._extract_key_phrases(text_content)
        important_sentences = self._extract_important_sentences(sentences)
        main_points = self._extract_main_points(text_content)
        key_insights = self._extract_key_insights(text_content)
        action_items = self._extract_action_items(text_content)
        
        # Get labels
        labels = self._get_summary_labels()
        
        # Create comprehensive summary focused on main points
        summary = f"""{labels['title']}
{'=' * 60}

📋 MAIN POINTS & KEY TAKEAWAYS:
{self._format_main_points(main_points)}

💡 KEY INSIGHTS:
{self._format_key_insights(key_insights)}

🎯 IMPORTANT CONTENT:
{self._format_important_sentences(important_sentences)}

🔑 CORE TOPICS & KEYWORDS:
{self._format_key_phrases(key_phrases)}

📝 ACTION ITEMS & RECOMMENDATIONS:
{self._format_action_items(action_items)}

📊 DOCUMENT OVERVIEW:
• Total Words: {word_count:,}
• Reading Time: {self._estimate_reading_time(word_count)}
• Content Type: {self._identify_document_type(text_content)}
• Complexity Level: {self._assess_complexity(text_content)}

🏗️ STRUCTURE ANALYSIS:
{self._analyze_structure(text_content)}"""

        return summary
        
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        import re
        from collections import Counter
        
        # Convert to lowercase and remove special characters
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = clean_text.split()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'this', 'that', 'these', 'those', 'i', 'me',
            'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
            'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom',
            'whose', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'
        }
        
        # Filter words
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Get most common words
        word_freq = Counter(filtered_words)
        key_phrases = [word for word, count in word_freq.most_common(10) if count > 1]
        
        return key_phrases
        
    def _extract_important_sentences(self, sentences: List[str]) -> List[str]:
        """Extract the most important sentences with advanced scoring"""
        if not sentences:
            return []
            
        # Score sentences based on multiple factors
        scored_sentences = []
        
        # Keywords that indicate important content
        important_keywords = [
            'important', 'significant', 'key', 'main', 'primary', 'essential', 'critical',
            'conclusion', 'result', 'finding', 'discovery', 'breakthrough', 'analysis',
            'summary', 'overview', 'objective', 'goal', 'purpose', 'recommendation',
            'solution', 'problem', 'issue', 'challenge', 'opportunity', 'benefit',
            'advantage', 'strategy', 'approach', 'method', 'technique', 'process'
        ]
        
        for i, sentence in enumerate(sentences):
            score = 0
            sentence_lower = sentence.lower()
            
            # Length scoring (optimal range)
            if 40 <= len(sentence) <= 250:
                score += 3
            elif 20 <= len(sentence) <= 400:
                score += 2
            elif len(sentence) > 10:
                score += 1
                
            # Position scoring - beginning and conclusion sections are important
            total_sentences = len(sentences)
            if i < total_sentences * 0.15:  # First 15%
                score += 2
            elif i > total_sentences * 0.85:  # Last 15%
                score += 2
            elif total_sentences * 0.4 <= i <= total_sentences * 0.6:  # Middle section
                score += 1
                
            # Keyword scoring
            keyword_count = sum(1 for keyword in important_keywords if keyword in sentence_lower)
            score += keyword_count * 2
            
            # Sentence structure indicators
            if sentence.startswith(('The main', 'The key', 'The primary', 'The most important', 'In conclusion', 'To summarize')):
                score += 3
            if sentence.startswith(('However', 'Therefore', 'Thus', 'Furthermore', 'Moreover', 'Additionally')):
                score += 2
            if '?' in sentence:  # Questions often highlight important points
                score += 1
            if sentence.count(',') > 2:  # Complex sentences often contain more information
                score += 1
                
            # Number and data indicators
            if any(char.isdigit() for char in sentence):
                score += 1
            if any(word in sentence_lower for word in ['percent', '%', 'data', 'statistics', 'study', 'research']):
                score += 2
                
            scored_sentences.append((score, sentence, i))
        
        # Sort by score and return top sentences
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        
        # Select top sentences but ensure diversity (not all from same section)
        selected_sentences = []
        selected_indices = []
        
        for score, sentence, index in scored_sentences:
            if len(selected_sentences) >= 5:  # Limit to 5 important sentences for better focus
                break
            
            # Avoid selecting sentences too close to each other
            if not any(abs(index - sel_idx) < 3 for sel_idx in selected_indices):
                selected_sentences.append(sentence)
                selected_indices.append(index)
        
        return selected_sentences
        
    def _format_key_phrases(self, phrases: List[str]) -> str:
        """Format key phrases for display"""
        if not phrases:
            return "• No significant key phrases identified"
        return '\n'.join([f"• {phrase.title()}" for phrase in phrases[:5]])  # Limit to 5 key phrases
        
    def _format_important_sentences(self, sentences: List[str]) -> str:
        """Format important sentences for display"""
        if not sentences:
            return "• No significant sentences identified"
        
        formatted = []
        for i, sentence in enumerate(sentences[:3], 1):  # Limit to 3 important sentences
            # Clean and truncate if necessary
            clean_sentence = sentence.strip()
            if len(clean_sentence) > 180:
                clean_sentence = clean_sentence[:177] + "..."
            formatted.append(f"• {clean_sentence}")
        
        return '\n'.join(formatted)
        
    def _analyze_structure(self, text: str) -> str:
        """Analyze document structure"""
        pages = text.split("--- Page")
        page_count = len(pages) - 1 if pages[0].strip() == "" else len(pages)
        
        # Look for common document elements
        structure_elements = []
        
        if any(word in text.lower() for word in ['abstract', 'summary']):
            structure_elements.append("Abstract/Summary section")
        if any(word in text.lower() for word in ['introduction', 'background']):
            structure_elements.append("Introduction/Background")
        if any(word in text.lower() for word in ['conclusion', 'results', 'findings']):
            structure_elements.append("Conclusion/Results section")
        if any(word in text.lower() for word in ['reference', 'bibliography', 'citation']):
            structure_elements.append("References/Bibliography")
        if any(word in text.lower() for word in ['table', 'figure', 'chart']):
            structure_elements.append("Tables/Figures present")
            
        structure_info = f"• Document has {page_count} pages\n"
        if structure_elements:
            structure_info += '\n'.join([f"• {element}" for element in structure_elements])
        else:
            structure_info += "• Standard document structure"
            
        return structure_info
        
    def _generate_insights(self, text: str, key_phrases: List[str]) -> str:
        """Generate insights about the document"""
        insights = []
        
        # Document type detection
        if any(word in text.lower() for word in ['research', 'study', 'analysis', 'methodology']):
            insights.append("Appears to be a research or academic document")
        elif any(word in text.lower() for word in ['report', 'summary', 'findings', 'recommendations']):
            insights.append("Appears to be a report or summary document")
        elif any(word in text.lower() for word in ['manual', 'guide', 'instructions', 'how to']):
            insights.append("Appears to be an instructional or guide document")
        else:
            insights.append("General informational document")
            
        # Content complexity
        avg_word_length = sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0
        if avg_word_length > 6:
            insights.append("Content appears technical/specialized")
        elif avg_word_length > 4:
            insights.append("Content appears moderately technical")
        else:
            insights.append("Content appears accessible/general audience")
            
        # Key topics
        if key_phrases:
            insights.append(f"Main focus areas: {', '.join(key_phrases[:3])}")
            
        return '\n'.join([f"• {insight}" for insight in insights])
        
    def _extract_main_points(self, text: str) -> List[str]:
        """Extract main points from the document"""
        sentences = self._split_into_sentences(text)
        main_points = []
        
        # Look for sentences that typically contain main points
        point_indicators = [
            'the main', 'the key', 'the primary', 'the most important', 'the central',
            'in summary', 'in conclusion', 'to conclude', 'overall', 'the purpose',
            'the objective', 'the goal', 'the result', 'the finding', 'the outcome',
            'it is important', 'it is essential', 'it is critical', 'it is necessary',
            'research shows', 'studies indicate', 'evidence suggests', 'data reveals'
        ]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check for main point indicators
            if any(indicator in sentence_lower for indicator in point_indicators):
                if 30 <= len(sentence) <= 300:  # Good length for main points
                    main_points.append(sentence.strip())
                    
            # Look for numbered or bulleted points
            if sentence.strip().startswith(('1.', '2.', '3.', '•', '-', '*')):
                if 20 <= len(sentence) <= 250:
                    main_points.append(sentence.strip())
        
        # If no obvious main points found, use highest scoring sentences
        if len(main_points) < 3:
            important_sentences = self._extract_important_sentences(sentences)
            main_points.extend(important_sentences[:5])
        
        # Remove duplicates and return top points
        seen = set()
        unique_points = []
        for point in main_points:
            if point not in seen and len(point.strip()) > 15:
                seen.add(point)
                unique_points.append(point)
                
        return unique_points[:4]  # Limit to 4 main points
    
    def _extract_key_insights(self, text: str) -> List[str]:
        """Extract key insights and conclusions"""
        sentences = self._split_into_sentences(text)
        insights = []
        
        insight_indicators = [
            'this suggests', 'this indicates', 'this shows', 'this demonstrates',
            'therefore', 'thus', 'hence', 'consequently', 'as a result',
            'it appears', 'it seems', 'evidence shows', 'analysis reveals',
            'findings suggest', 'research indicates', 'studies show',
            'implications', 'significance', 'importance', 'impact'
        ]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            if any(indicator in sentence_lower for indicator in insight_indicators):
                if 25 <= len(sentence) <= 280:
                    insights.append(sentence.strip())
        
        return insights[:3]  # Limit to 3 key insights
    
    def _extract_action_items(self, text: str) -> List[str]:
        """Extract action items and recommendations"""
        sentences = self._split_into_sentences(text)
        actions = []
        
        action_indicators = [
            'should', 'must', 'need to', 'recommend', 'suggest', 'propose',
            'it is recommended', 'it is suggested', 'it is advisable',
            'next steps', 'action items', 'implementation', 'follow up',
            'consider', 'ensure', 'implement', 'establish', 'develop',
            'future work', 'further research', 'next phase'
        ]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            if any(indicator in sentence_lower for indicator in action_indicators):
                if 20 <= len(sentence) <= 250:
                    actions.append(sentence.strip())
        
        return actions[:3]  # Limit to 3 action items
    
    def _identify_document_type(self, text: str) -> str:
        """Identify the type of document"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['research', 'study', 'methodology', 'hypothesis']):
            return "Research Paper/Study"
        elif any(word in text_lower for word in ['report', 'analysis', 'assessment', 'evaluation']):
            return "Report/Analysis"
        elif any(word in text_lower for word in ['manual', 'guide', 'instructions', 'tutorial']):
            return "Manual/Guide"
        elif any(word in text_lower for word in ['proposal', 'plan', 'strategy', 'roadmap']):
            return "Proposal/Plan"
        elif any(word in text_lower for word in ['policy', 'procedure', 'regulation', 'compliance']):
            return "Policy/Procedure"
        else:
            return "General Document"
    
    def _assess_complexity(self, text: str) -> str:
        """Assess the complexity level of the content"""
        words = text.split()
        if not words:
            return "Unknown"
            
        # Calculate average word length
        avg_word_length = sum(len(word.strip('.,!?;:')) for word in words) / len(words)
        
        # Count technical indicators
        technical_terms = sum(1 for word in words if len(word) > 8)
        technical_ratio = technical_terms / len(words) if words else 0
        
        if avg_word_length > 6 or technical_ratio > 0.15:
            return "High (Technical/Specialized)"
        elif avg_word_length > 5 or technical_ratio > 0.08:
            return "Medium (Professional)"
        else:
            return "Low (General Audience)"
    
    def _format_main_points(self, points: List[str]) -> str:
        """Format main points for display"""
        if not points:
            return "• No clear main points identified in the document"
        
        formatted = []
        for i, point in enumerate(points, 1):
            # Clean and truncate if necessary
            clean_point = point.strip().rstrip('.,!?')
            if len(clean_point) > 200:
                clean_point = clean_point[:197] + "..."
            formatted.append(f"{i}. {clean_point}")
        
        return '\n'.join(formatted)
    
    def _format_key_insights(self, insights: List[str]) -> str:
        """Format key insights for display"""
        if not insights:
            return "• Document analysis did not reveal clear insights"
        
        formatted = []
        for insight in insights:
            clean_insight = insight.strip().rstrip('.,!?')
            if len(clean_insight) > 180:
                clean_insight = clean_insight[:177] + "..."
            formatted.append(f"• {clean_insight}")
        
        return '\n'.join(formatted)
    
    def _format_action_items(self, actions: List[str]) -> str:
        """Format action items for display"""
        if not actions:
            return "• No specific action items or recommendations identified"
        
        formatted = []
        for action in actions:
            clean_action = action.strip().rstrip('.,!?')
            if len(clean_action) > 170:
                clean_action = clean_action[:167] + "..."
            formatted.append(f"• {clean_action}")
        
        return '\n'.join(formatted)
            
    def _estimate_reading_time(self, word_count: int) -> str:
        """Estimate reading time based on word count"""
        avg_wpm = 200  # Average reading speed
        minutes = word_count / avg_wpm
        
        # Get time labels
        time_labels = self._get_time_labels()
        
        if minutes < 1:
            return time_labels['less_than_minute']
        elif minutes < 60:
            minutes_int = int(minutes)
            return f"{minutes_int} minute{'s' if minutes_int != 1 else ''}"
        else:
            hours = minutes / 60
            return f"{hours:.1f} hour{'s' if hours != 1 else ''}"
        
    def _format_summary(self, summary: str, filename: str, text_length: int, document_info: dict = None) -> str:
        """Format the summary with metadata"""        
        return f"""PDF Document Summary
{'=' * 50}

📄 Document: {filename}
📊 Original Length: {text_length:,} characters
🌍 Language: English
🕒 Processed: {self._get_current_timestamp()}

Summary:
{'-' * 20}
{summary}

{'=' * 50}"""
        
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for metadata"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get PDF metadata without full processing
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            dict: PDF metadata
        """
        if not os.path.exists(pdf_path):
            return {}
            
        file_stats = os.stat(pdf_path)
        
        # Basic file info (expand with PyPDF2 for more details)
        return {
            "filename": os.path.basename(pdf_path),
            "size_bytes": file_stats.st_size,
            "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
            "modified": self._format_timestamp(file_stats.st_mtime),
            "pages": "Unknown"  # Would require PDF library to determine
        }
        
    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp for display"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate if file is a readable PDF
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            bool: True if valid PDF, False otherwise
        """
        try:
            if not os.path.exists(pdf_path):
                return False
                
            if not pdf_path.lower().endswith('.pdf'):
                return False
                
            # Basic file size check (not empty, not too large)
            file_size = os.path.getsize(pdf_path)
            if file_size == 0 or file_size > 50 * 1024 * 1024:  # 50MB limit
                return False
                
            # Could add more sophisticated PDF validation with PyPDF2
            # import PyPDF2
            # with open(pdf_path, 'rb') as file:
            #     PyPDF2.PdfReader(file)  # Will raise exception if not valid PDF
            
            return True
        except Exception:
            return False
    
    def _get_document_info(self, text: str) -> dict:
        """
        Get basic document information (always English)
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            dict: Document information
        """
        return {"name": "English", "code": "en", "confidence": 1.0}
        
    def _get_summary_labels(self) -> dict:
        """
        Get English labels for summary sections
        
        Returns:
            dict: English labels
        """
        return {
            'title': 'PDF Document Analysis',
            'doc_stats': 'Document Statistics',
            'total_words': 'Total Words',
            'total_sentences': 'Total Sentences',
            'total_characters': 'Total Characters',
            'reading_time': 'Estimated Reading Time',
            'key_phrases': 'Key Phrases',
            'important_content': 'Important Content',
            'content_structure': 'Content Structure',
            'insights': 'Document Insights',
            'main_topics': 'Main Topics'
        }
        
    def _get_time_labels(self) -> dict:
        """
        Get English time labels
        
        Returns:
            dict: English time labels
        """
        return {
            'less_than_minute': 'Less than 1 minute',
            'minutes': 'minutes',
            'hours': 'hours'
        }
