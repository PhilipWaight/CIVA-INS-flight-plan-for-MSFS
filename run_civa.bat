@echo off
title CIVA INS Macro Processor
color 0B

:: Check if Python is in the path
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

echo Starting CIVA Navigation Processor...
echo.

:: Run your python script (change filename if yours is different)
py CIVA_flightplan.py

echo.
echo Processing complete. CMD window closing.
timeout /t 3