@echo off
title Virtual Cursor - Auto Start Setup
color 0A

echo ============================================
echo   VIRTUAL CURSOR - Auto Start Setup
echo ============================================
echo.

REM ── Script location (auto-detected) ──────────────────────────
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%hand_cursor.py"

REM ── Verify hand_cursor.py exists in same folder ───────────────
if not exist "%SCRIPT_PATH%" (
    echo [ERROR] hand_cursor.py not found in this folder.
    echo         Make sure setup_autostart.bat is in the same
    echo         folder as hand_cursor.py
    echo.
    echo         Current folder: %SCRIPT_DIR%
    pause
    exit /b 1
)

echo [OK] Script found: %SCRIPT_PATH%
echo.

REM ── Find pythonw.exe (tries Python 3.10, 3.11, 3.12, PATH) ───
set "PYTHON_PATH="

REM Try Python 3.10 first (packages are installed here)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\pythonw.exe" (
    set "PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\pythonw.exe"
    goto :python_found
)

REM Try Python 3.11
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\pythonw.exe" (
    set "PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\pythonw.exe"
    goto :python_found
)

REM Try Python 3.12
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\pythonw.exe" (
    set "PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\pythonw.exe"
    goto :python_found
)

REM Try system-wide Python installs
if exist "C:\Python310\pythonw.exe" (
    set "PYTHON_PATH=C:\Python310\pythonw.exe"
    goto :python_found
)
if exist "C:\Python311\pythonw.exe" (
    set "PYTHON_PATH=C:\Python311\pythonw.exe"
    goto :python_found
)
if exist "C:\Python312\pythonw.exe" (
    set "PYTHON_PATH=C:\Python312\pythonw.exe"
    goto :python_found
)

REM Try finding pythonw on PATH
for /f "delims=" %%i in ('where pythonw 2^>nul') do (
    set "PYTHON_PATH=%%i"
    goto :python_found
)

REM Nothing found
echo [ERROR] Could not find pythonw.exe anywhere.
echo.
echo         Please open this .bat file in Notepad and
echo         manually set PYTHON_PATH to your pythonw.exe
echo         For example:
echo         set "PYTHON_PATH=C:\Users\Star\AppData\Local\Programs\Python\Python310\pythonw.exe"
echo.
pause
exit /b 1

:python_found
echo [OK] Python found: %PYTHON_PATH%
echo.

REM ── Remove old scheduled task if it exists ────────────────────
schtasks /delete /tn "VirtualCursor" /f >nul 2>&1

REM ── Create Task Scheduler entry ───────────────────────────────
REM  /sc ONLOGON  = trigger: when THIS user logs in
REM  /rl HIGHEST  = run with highest available privileges
REM  /f           = force overwrite if exists
schtasks /create ^
  /tn "VirtualCursor" ^
  /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" ^
  /sc ONLOGON ^
  /ru "%USERNAME%" ^
  /rl HIGHEST ^
  /f

if ERRORLEVEL 1 (
    echo.
    echo [ERROR] Could not create the scheduled task.
    echo.
    echo         SOLUTION: Right-click this file and choose
    echo                   "Run as Administrator"  then try again.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   SUCCESS!
echo.
echo   Virtual Cursor will now automatically
echo   start every time you log into Windows.
echo   No VS Code needed. No clicking needed.
echo.
echo   HOTKEYS (once running):
echo     Ctrl+Shift+H  =  Toggle ON / OFF
echo     Ctrl+Shift+S  =  Sensitivity UP
echo     Ctrl+Shift+F  =  Sensitivity DOWN
echo.
echo   To STOP auto-start:  remove_autostart.bat
echo   To START now:        start_now.bat
echo ============================================
echo.

set /p START_NOW="Start Virtual Cursor right now? (y/n): "
if /i "%START_NOW%"=="y" (
    echo.
    echo Starting Virtual Cursor silently...
    start "" "%PYTHON_PATH%" "%SCRIPT_PATH%"
    echo [OK] Running in background. Check system tray (bottom-right).
)

echo.
pause
