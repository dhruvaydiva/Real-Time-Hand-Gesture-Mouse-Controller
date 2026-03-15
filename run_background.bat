@echo off
title Virtual Cursor - Background Launcher
color 0A

cd /d "%~dp0"

REM ── Find pythonw.exe ──────────────────────────────────────────
set "PYTHON_PATH="

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\pythonw.exe" (
    set "PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\pythonw.exe"
    goto :found
)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\pythonw.exe" (
    set "PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\pythonw.exe"
    goto :found
)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\pythonw.exe" (
    set "PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\pythonw.exe"
    goto :found
)
for /f "delims=" %%i in ('where pythonw 2^>nul') do (
    set "PYTHON_PATH=%%i"
    goto :found
)

echo [ERROR] pythonw.exe not found.
pause
exit /b 1

:found
REM ── Kill any existing instance first ─────────────────────────
taskkill /f /im pythonw.exe >nul 2>&1
timeout /t 1 >nul

REM ── Launch fully detached — survives VS Code closing ─────────
start "" /B "%PYTHON_PATH%" "%~dp0hand_cursor.py"

echo.
echo [OK] Virtual Cursor is running in the background.
echo     It will keep running even if you close VS Code.
echo.
echo     Ctrl+Shift+H  =  Toggle ON / OFF
echo     To stop:  run stop_cursor.bat
echo.
timeout /t 4 >nul
