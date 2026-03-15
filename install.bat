@echo off
title Virtual Cursor - Installer
color 0A

echo ============================================
echo   VIRTUAL CURSOR - Installing Dependencies
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

echo Installing required packages...
echo.
pip install -r requirements.txt

IF ERRORLEVEL 1 (
    echo.
    echo [ERROR] Installation failed. Try running as Administrator.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Installation complete!
echo   Run start.bat to launch Virtual Cursor.
echo ============================================
echo.
pause
