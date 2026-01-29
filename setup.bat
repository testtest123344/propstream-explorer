@echo off
echo ========================================
echo   PropStream Explorer - Setup
echo ========================================
echo.

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.12+ from https://python.org/downloads
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo [OK] Python found

:: Check for Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js 20+ from https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js found

:: Check for config.json
if not exist "config.json" (
    echo.
    echo [WARNING] config.json not found!
    echo Creating template config.json...
    echo Please edit it and add your PropStream auth token.
    (
        echo {
        echo     "auth_token": "YOUR_PROPSTREAM_TOKEN_HERE",
        echo     "base_url": "https://app.propstream.com",
        echo     "max_retries": 3,
        echo     "timeout": 30,
        echo     "min_delay": 0.5,
        echo     "max_delay": 3.0,
        echo     "hourly_limit": 100,
        echo     "daily_limit": 500
        echo }
    ) > config.json
    echo.
    echo [ACTION REQUIRED] Edit config.json and replace YOUR_PROPSTREAM_TOKEN_HERE
    echo with your actual PropStream auth token before running the app.
    echo.
)

:: Install Python dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)
echo [OK] Python dependencies installed

:: Install Node.js dependencies
echo.
echo Installing Node.js dependencies...
cd web
call npm install
if errorlevel 1 (
    echo [ERROR] Failed to install Node.js dependencies
    pause
    exit /b 1
)
cd ..
echo [OK] Node.js dependencies installed

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure config.json has your PropStream auth token
echo 2. Double-click "run.bat" to start the app
echo 3. Open http://localhost:3001 in your browser
echo.
pause
