@echo off
REM AI Novel Writing Application Setup Script for Windows
REM This script sets up the development environment for both backend and frontend

setlocal enabledelayedexpansion

echo ==============================================
echo   AI Novel Writing Application Setup
echo ==============================================
echo.

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python %PYTHON_VERSION% found

REM Check if Node.js is installed
echo [INFO] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 16+ and try again.
    pause
    exit /b 1
)

REM Check Node.js version
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo [SUCCESS] Node.js %NODE_VERSION% found

echo.
echo [INFO] Setting up backend...

REM Setup backend
cd backend

REM Create virtual environment
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt

REM Setup environment file
if not exist ".env" (
    echo [INFO] Creating .env file...
    (
        echo # Database Configuration
        echo DATABASE_URL=sqlite:///./ai_novel_app.db
        echo.
        echo # AI Provider Settings
        echo AI_PROVIDER=openai
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo OPENAI_MODEL=gpt-4
        echo.
        echo # Ollama Settings ^(for local AI^)
        echo OLLAMA_BASE_URL=http://localhost:11434
        echo OLLAMA_MODEL=llama2
        echo.
        echo # API Configuration
        echo API_V1_PREFIX=/api/v1
        echo CORS_ORIGINS=["http://localhost:3001"]
        echo.
        echo # Generation Settings
        echo MAX_CHAPTERS_PER_STORY=50
        echo DEFAULT_CHAPTER_LENGTH=2000
        echo GENERATION_TIMEOUT=300
        echo.
        echo # Writing Complexity
        echo NOVEL_COMPLEXITY=standard
    ) > .env
    echo [WARNING] Please edit backend\.env with your OpenAI API key
)

REM Initialize database
echo [INFO] Initializing database...
python -c "from db.database import init_db; init_db()"

cd ..
echo [SUCCESS] Backend setup complete!

echo.
echo [INFO] Setting up frontend...

REM Setup frontend
cd frontend

REM Install dependencies
echo [INFO] Installing Node.js dependencies...
npm install

cd ..
echo [SUCCESS] Frontend setup complete!

echo.
echo [INFO] Running backend tests...
cd backend
call venv\Scripts\activate.bat
python test_basic.py
cd ..
echo [SUCCESS] Tests completed!

echo.
echo ==============================================
echo   Setup Complete!
echo ==============================================
echo.
echo [SUCCESS] Your AI Novel Writing Application is ready!
echo.
echo Next steps:
echo 1. Edit backend\.env with your OpenAI API key
echo 2. Start the backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app:app --reload
echo 3. Start the frontend: cd frontend ^&^& npm run dev
echo 4. Open http://localhost:3001 in your browser
echo.
echo API Documentation: http://localhost:8000/docs
echo.
echo [WARNING] Remember to keep your API keys secure and never commit them to version control!
echo.
pause
