@echo off
title Virtual Cursor - Stop
color 0C

echo Stopping Virtual Cursor...
taskkill /f /im pythonw.exe /fi "WINDOWTITLE eq Virtual Cursor*" >nul 2>&1
taskkill /f /fi "IMAGENAME eq pythonw.exe" >nul 2>&1

echo Virtual Cursor stopped.
timeout /t 2 >nul
