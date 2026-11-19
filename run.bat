@echo off
title AI Gig Hunter & Interview Simulator
echo ========================================================
echo Starting AI Gig Hunter & Interview Simulator Platform...
echo ========================================================

cd /d "%~dp0"

if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo Starting FastAPI server at http://127.0.0.1:8000
start "" "http://127.0.0.1:8000"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
