@echo off
echo Starting PropStream Explorer...
echo.
echo Starting Flask API server on http://localhost:5000
start "Flask API" cmd /k "cd /d %~dp0 && python api/server.py"
echo.
echo Waiting for API to start...
timeout /t 3 /nobreak > nul
echo.
echo Starting React frontend on http://localhost:3000
start "React Frontend" cmd /k "cd /d %~dp0web && npm run dev"
echo.
echo ========================================
echo PropStream Explorer is starting up!
echo.
echo   API Server:  http://localhost:5000
echo   Web App:     http://localhost:3000
echo.
echo Open http://localhost:3000 in your browser
echo ========================================
