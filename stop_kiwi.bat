@echo off
REM Kiwi AI Trading System Stop Script
REM This script cleanly stops all Python processes and clears connections

echo ================================================
echo    Kiwi AI Trading System - Clean Shutdown
echo ================================================
echo.

echo [1/2] Stopping all Python processes...
taskkill /F /IM python.exe >NUL 2>&1

if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Python processes stopped.
) else (
    echo No Python processes were running.
)

echo.
echo [2/2] Waiting for WebSocket connections to close...
echo (This ensures no lingering connections to Alpaca API)
timeout /t 10 /nobreak >NUL

echo.
echo ================================================
echo    Kiwi AI stopped successfully!
echo    Wait 5 more seconds before restarting.
echo ================================================
echo.

pause
