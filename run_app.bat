@echo off
echo Starting FutureAtlas 2050...

REM Start Backend
echo Starting Backend Server...
start "FutureAtlas Backend" cmd /k "cd backend && call venv\Scripts\activate && uvicorn main:app --reload"

REM Start Frontend
echo Starting Frontend Client...
start "FutureAtlas Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Application is starting!
echo Backend will be at: http://localhost:8000
echo Frontend will be at: http://localhost:5173
echo.
pause
