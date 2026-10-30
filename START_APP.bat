@echo off
title HealthSahayAI - SwasthyaSetu AI
cd /d "%~dp0"

echo.
echo ============================================================
echo   HealthSahayAI  ^|  SwasthyaSetu AI
echo   Open browser at:  http://127.0.0.1:5000/
echo ============================================================
echo.

REM Check if .venv Python 3.12 exists (preferred)
if exist ".venv\Scripts\python.exe" (
    echo [OK] Using project virtual environment (.venv - Python 3.12^)
    ".venv\Scripts\python.exe" app.py
    goto done
)

REM Fallback: system Python 3.12 install
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    echo [OK] Using system Python 3.12
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" app.py
    goto done
)

REM Last resort: py launcher
py -3.12 app.py 2>nul
if %ERRORLEVEL% == 0 goto done

echo.
echo [ERROR] Could not find Python 3.12.
echo         Please run:  .venv\Scripts\python.exe app.py
echo.

:done
pause

