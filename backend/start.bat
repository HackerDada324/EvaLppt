@echo off
echo.
echo ========================================
echo   Auto PPT Evaluation System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if we're in the backend directory
if not exist "app.py" (
    echo ❌ Please run this script from the backend directory
    echo Current directory should contain app.py
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\Lib\site-packages\flask" (
    echo 📚 Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  No .env file found
    if exist ".env.example" (
        echo 📝 Copying .env.example to .env...
        copy .env.example .env
        echo.
        echo ⚠️  Please edit .env file and add your API keys:
        echo    - GEMINI_API_KEY=your_key_here
        echo.
        echo Press any key to continue with limited functionality...
        pause
    )
)

echo.
echo 🚀 Starting Auto PPT Evaluation Backend...
echo.
echo 📍 Server will be available at: http://localhost:5000
echo 🔍 Health check: http://localhost:5000/api/health
echo 🧪 Test endpoint: http://localhost:5000/api/test
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python app.py

echo.
echo 👋 Server stopped
pause
