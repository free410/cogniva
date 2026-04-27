@echo off
cd /d "%~dp0.."
echo Starting Knowledge Assistant API server...
echo.
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
