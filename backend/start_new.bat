@echo off
echo 🚀 Starting Auto PPT Evaluation Backend (New Architecture)
echo.

:: Check if virtual environment exists
if exist venv\ (
    echo ✅ Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo ⚠️  No virtual environment found. Consider creating one:
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    echo.
)

:: Set environment variables if not set
if not defined FLASK_ENV (
    set FLASK_ENV=development
)

if not defined FLASK_DEBUG (
    set FLASK_DEBUG=True
)

echo 🔧 Environment: %FLASK_ENV%
echo 🐛 Debug: %FLASK_DEBUG%
echo.

:: Check for required dependencies
python -c "import flask" 2>nul
if errorlevel 1 (
    echo ❌ Flask not found. Please install dependencies:
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)

:: Start the application
echo 🌟 Starting Auto PPT Evaluation System v2.0.0...
echo 📁 Using modular architecture from run.py
echo.
python run.py
