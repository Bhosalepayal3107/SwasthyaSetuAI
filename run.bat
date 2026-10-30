@echo off
cd /d "%~dp0"
echo ========================================================
echo   Starting HealthSahayAI - SwasthyaSetu AI
echo   Local Portal: http://127.0.0.1:5000/
echo ========================================================

if exist ".venv\Scripts\python.exe" (
    echo Using project virtual environment
    ".venv\Scripts\python.exe" app.py
    goto end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    echo Using Python 3.12
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" app.py
    goto end
)

echo Using default python
python app.py

:end
pause
