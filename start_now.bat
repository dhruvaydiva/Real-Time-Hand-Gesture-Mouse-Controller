@echo off
title Virtual Cursor - Starting...
color 0A

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%hand_cursor.py"
set "PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\pythonw.exe"

if not exist "%PYTHON_PATH%" (
    for /f "delims=" %%i in ('where pythonw 2^>nul') do set "PYTHON_PATH=%%i"
)

echo Starting Virtual Cursor silently...
start "" "%PYTHON_PATH%" "%SCRIPT_PATH%"

echo.
echo Virtual Cursor is now running in the background.
echo Press Ctrl+Shift+H to toggle ON/OFF
echo.
timeout /t 3 >nul
