# 🎓 StudyMate Pro - Multi-AI Study Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**StudyMate Pro** is an advanced AI-powered study assistant that helps students analyze PDF documents and get structured answers using multiple AI models including OpenAI GPT, Google Gemini, and IBM Granite.

## ✨ Features

### 🤖 Multi-AI Integration
- **OpenAI GPT-3.5-turbo**: Advanced language understanding
- **Google Gemini Pro**: Google's cutting-edge AI model  
- **IBM Granite**: Local inference capability
- **Smart Model Selection**: Choose which AI models to use

### 📚 Academic Answer Generation
- **7-Mark Answers**: Structured responses with Introduction → Analysis → Conclusion
- **14-Mark Answers**: Comprehensive responses with Introduction → Analysis → Evaluation → Conclusion
- **Fast Processing**: Optimized for quick, accurate responses
- **Context-Aware**: Answers based on your uploaded PDF content

### 💬 Modern Chat Interface
- **ChatGPT-like UI**: Beautiful, responsive design
- **Chat History**: Persistent conversation tracking
- **Real-time Status**: Live API availability monitoring
- **Grammar Check**: Automatic question improvement
- **Spell Check**: Word suggestions and corrections

### 📄 PDF Processing
- **Smart Text Extraction**: Advanced PDF parsing with PyMuPDF
- **Semantic Search**: Find relevant content using embeddings
- **Context Optimization**: Intelligent content chunking
- **Fast Mode**: Keyword-based fallback for speed

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux
- API keys for desired AI services (optional - has local fallback)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/studymate-pro.git
cd studymate-pro
```

2. **Create virtual environment:**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements_multi_ai.txt
```

4. **Set up environment variables:**
```bash
# Copy the example environment file
cp .env.example .env
# Edit .env and add your API keys (optional)
```

5. **Run the application:**
```bash
# Using the batch file (Windows)
start_studymate.bat

# Or directly with Python
streamlit run app_multi_ai.py
```

6. **Open your browser:**
   - Navigate to `http://localhost:8501`
   - Login with demo account: `demo` / `demo123`

## 🔧 Configuration

### Environment Variables (.env file)

```env
# OpenAI API (optional)
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API (optional)
GOOGLE_API_KEY=your_google_api_key_here

# Application Settings
FAST_MODE=true
DEBUG_MODE=false
```

### Demo Accounts
- **Username:** `demo` **Password:** `demo123`
- **Username:** `student` **Password:** `student123`

## 📖 Usage Guide

### 1. Upload PDF Document
- Click "Upload PDF" in the sidebar
- Wait for processing to complete
- The system will extract text and create embeddings

### 2. Ask Questions
- Type your question in the text area
- Select which AI models to use
- Click "Ask Question" or use quick buttons

### 3. Generate Structured Answers
- **7-Marks Button**: Get concise academic answers
- **14-Marks Button**: Get comprehensive detailed answers
- **Fast AI**: Quick processing with local models

### 4. Review Chat History
- All conversations are saved in your session
- Scroll through previous Q&A pairs
- Export or clear history as needed

## 🏗️ Project Structure

```
studymate-pro/
├── app_multi_ai.py           # Main Streamlit application
├── health_check.py           # Application health monitoring
├── requirements_multi_ai.txt # Python dependencies
├── start_studymate.bat       # Windows launcher script
├── .env.example              # Environment variables template
├── README.md                 # This file
├── LICENSE                   # MIT License
├── ENHANCEMENT_SUMMARY.md    # Development changelog
├── MULTI_AI_GUIDE.md         # Detailed AI integration guide
└── .venv/                    # Virtual environment (not tracked)
```

## 🛠️ Development

### Running in Development Mode
```bash
# Enable debug mode
export DEBUG_MODE=true

# Run with auto-reload
streamlit run app_multi_ai.py --server.runOnSave true
```

### Health Check
```bash
python health_check.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit** for the amazing web app framework
- **OpenAI** for GPT-3.5-turbo API
- **Google** for Gemini Pro API
- **IBM** for Granite model
- **Hugging Face** for transformer models and embeddings

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/studymate-pro/issues) page
2. Run the health check: `python health_check.py`
3. Enable debug mode in `.env` file
4. Create a new issue with detailed information

## 🌟 Star History

If you find StudyMate Pro helpful, please consider giving it a star! ⭐

---

**Made with ❤️ for students worldwide**
