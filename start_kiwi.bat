@echo off
REM Kiwi AI Trading System Startup Script
REM This script ensures clean startup by closing any existing connections

echo ================================================
echo    Kiwi AI Trading System - Clean Startup
echo ================================================
echo.

echo [1/4] Checking for existing Python processes...
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo WARNING: Python processes are running!
    echo Stopping existing processes to avoid connection conflicts...
    taskkill /F /IM python.exe >NUL 2>&1
    echo Waiting 15 seconds for connections to close...
    timeout /t 15 /nobreak >NUL
    echo Done.
) else (
    echo No existing Python processes found.
)

echo.
echo [2/4] Activating virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment!
    echo Please ensure .venv exists. Run: python -m venv .venv
    pause
    exit /b 1
)

echo.
echo [3/4] Checking dependencies...
python -c "import streamlit" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Streamlit not installed!
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo [4/4] Starting Kiwi AI Dashboard...
echo.
echo ================================================
echo    Dashboard will open at http://localhost:8501
echo    Press Ctrl+C to stop
echo ================================================
echo.

streamlit run run_kiwi.py

echo.
echo Kiwi AI stopped.
pause
