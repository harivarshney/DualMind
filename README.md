# 🧠 DualMind - AI-Powered Content Processor

**Smart transcription and analysis tool for YouTube videos and PDF documents**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)
![Whisper](https://img.shields.io/badge/AI-OpenAI%20Whisper-orange.svg)

## ✨ Features

- 🎥 **YouTube Transcription**: Convert any YouTube video to text with AI
- 📄 **PDF Analysis**: Extract key points, insights, and action items from PDFs
- 🚀 **Fast Processing**: Optimized for long videos (3-4 hours in 15-20 minutes)
- 📝 **Smart Formatting**: Auto-formatted paragraphs and readable output
- 💾 **Export Results**: Save transcriptions and analyses as text files
- 🎨 **Modern GUI**: Clean PyQt5 interface with progress tracking

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- FFmpeg (for audio processing)

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dualmind.git
   cd dualmind
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_qt.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```
   Or use the launcher:
   ```bash
   START_DualMind.bat
   ```

## 📋 Requirements

```
PyQt5>=5.15.0
yt-dlp>=2023.9.5
openai-whisper>=20230918
PyPDF2>=3.0.1
requests>=2.31.0
```

## 🚀 Usage

### YouTube Transcription
1. Launch DualMind
2. Select **YouTube** tab
3. Paste YouTube URL
4. Click **Start Transcription**
5. Wait for processing (progress shown in real-time)
6. Export results when complete

### PDF Analysis
1. Select **PDF** tab
2. Choose your PDF file
3. Click **Analyze PDF**
4. Get structured insights:
   - 📌 Main Points (4 items)
   - 💡 Key Insights (3 items)  
   - ✅ Action Items (3 items)

## 🎯 Key Benefits

- **Complete Transcription**: Processes entire videos without missing content
- **Smart Analysis**: AI-powered extraction of important information
- **User-Friendly**: Simple interface with clear progress indicators
- **Fast Performance**: Optimized processing for large files
- **Professional Output**: Clean, formatted results ready for use

## 🏗️ Project Structure

```
dualmind/
├── main.py                 # Main application
├── services/
│   ├── youtube_processor.py    # YouTube transcription
│   ├── pdf_processor.py        # PDF analysis
│   └── ...                     # Other services
├── utils/
│   └── helpers.py              # Utility functions
├── requirements_qt.txt         # Dependencies
└── README.md                   # This file
```

## 🤖 AI Models Used

- **Whisper Base**: OpenAI's speech recognition model for accurate transcription
- **Custom Analysis**: Smart algorithms for PDF content extraction

## 💡 Tips

- **Long Videos**: The app automatically optimizes processing for videos over 15 minutes
- **PDF Quality**: Higher quality PDFs produce better analysis results
- **Internet**: Required for YouTube downloads and model initialization

## 🔧 Troubleshooting

**Audio Download Issues**: Ensure FFmpeg is installed and in your PATH
**Model Loading**: First run downloads Whisper model (~500MB)
**Memory Usage**: Close other applications for large video processing

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using Python, PyQt5, and OpenAI Whisper**
