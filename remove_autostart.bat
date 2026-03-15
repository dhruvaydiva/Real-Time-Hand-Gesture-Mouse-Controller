@echo off
title Virtual Cursor - Remove Auto Start
color 0C

echo ============================================
echo   VIRTUAL CURSOR - Removing Auto Start
echo ============================================
echo.

schtasks /delete /tn "VirtualCursor" /f >nul 2>&1

if ERRORLEVEL 1 (
    echo [INFO] Task was not found or already removed.
) else (
    echo [OK] Auto-start has been disabled.
    echo      Virtual Cursor will no longer start at login.
)

echo.
pause
