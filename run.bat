@echo off
echo ========================================
echo   PropStream Explorer - Starting...
echo ========================================
echo.

:: Check for config.json
if not exist "config.json" (
    echo [ERROR] config.json not found!
    echo Please run setup.bat first, then edit config.json with your auth token.
    pause
    exit /b 1
)

:: Check if token is still placeholder
findstr /C:"YOUR_PROPSTREAM_TOKEN_HERE" config.json >nul 2>&1
if not errorlevel 1 (
    echo [ERROR] You need to add your PropStream auth token to config.json
    echo Edit config.json and replace YOUR_PROPSTREAM_TOKEN_HERE with your token.
    pause
    exit /b 1
)

echo Starting Flask API server...
start "PropStream API" cmd /k "python -m flask --app api.server run --port 5000"

:: Wait a moment for API to start
timeout /t 2 /nobreak >nul

echo Starting React web server...
start "PropStream Web" cmd /k "cd web && npm run dev"

:: Wait a moment for web server to start
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   PropStream Explorer is running!
echo ========================================
echo.
echo Opening browser...
start http://localhost:3001

echo.
echo To stop: Close both command windows that opened
echo.
pause
