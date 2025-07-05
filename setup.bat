@echo off
echo Starting DealDropper Application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file with your API keys and configuration
    echo.
)

REM Initialize database
echo Initializing database...
python scripts\init_db.py

REM Run tests
echo Running application tests...
python scripts\test_app.py

echo.
echo Setup complete! You can now start the application with:
echo python main.py
echo.
echo Or run the scraper manually with:
echo python scripts\run_scraper.py scrape
echo.
pause
