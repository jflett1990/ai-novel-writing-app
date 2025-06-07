# Quick Start Guide

Get your AI Novel Writing Application up and running in minutes!

## 🚀 One-Command Setup

Choose your preferred setup method:

### Option 1: Python Setup Script (Recommended - Cross-platform)
```bash
python3 setup.py
```

### Option 2: Bash Script (Linux/macOS)
```bash
./setup.sh
```

### Option 3: Windows Batch Script
```cmd
setup.bat
```

## 📋 Prerequisites

Before running the setup script, ensure you have:

- **Python 3.8+** ([Download](https://python.org/downloads/))
- **Node.js 16+** ([Download](https://nodejs.org/))
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

## ⚡ Manual Setup (if scripts don't work)

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -c "from db.database import init_db; init_db()"
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Environment Configuration
Edit `backend/.env` with your OpenAI API key:
```env
OPENAI_API_KEY=your_actual_api_key_here
```

## 🏃‍♂️ Running the Application

### Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app:app --reload
```

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:3001
- **API Documentation**: http://localhost:8000/docs
- **API**: http://localhost:8000

## 🎯 First Steps

1. **Create a Story**: Click "Create New Story" and fill in the details
2. **Set Complexity**: Choose your writing sophistication level
3. **Generate Outline**: Let AI create a detailed chapter breakdown
4. **Develop Characters**: Generate rich, complex character profiles
5. **Build the World**: Create immersive world elements
6. **Write Chapters**: Generate sophisticated prose with AI assistance

## 🔧 Configuration Options

### AI Provider Options

**OpenAI (Cloud)**:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4
```

**Ollama (Local)**:
```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Complexity Levels
- **Simple**: Clear, accessible storytelling
- **Standard**: Balanced complexity (default)
- **Complex**: Multi-layered narratives
- **Literary**: Artistic, experimental prose

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**"Port already in use"**:
- Backend: Change port with `uvicorn app:app --port 8001`
- Frontend: Change port in `package.json` or use different terminal

**Database errors**:
```bash
cd backend
python -c "from db.database import init_db; init_db()"
```

**OpenAI API errors**:
- Check your API key in `backend/.env`
- Verify you have credits in your OpenAI account
- Ensure the model name is correct (gpt-4, gpt-3.5-turbo, etc.)

### Getting Help

1. Check the [full README](README.md) for detailed documentation
2. Review API docs at http://localhost:8000/docs
3. Open an issue on GitHub for bugs
4. Check your browser console for frontend errors

## 🔒 Security Notes

- **Never commit your `.env` file** to version control
- **Regenerate API keys** if accidentally exposed
- **Use environment variables** for production deployment
- **Keep dependencies updated** for security patches

## 🎉 You're Ready!

Your AI Novel Writing Application is now running with:
- ✅ Sophisticated prompt engineering
- ✅ Anti-generic AI writing safeguards  
- ✅ Character development tools
- ✅ World building features
- ✅ Export functionality
- ✅ Complexity control system

Start creating your masterpiece! 📚✨
