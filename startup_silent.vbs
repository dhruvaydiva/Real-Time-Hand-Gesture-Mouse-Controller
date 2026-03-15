' ================================================================
'  Virtual Cursor - Silent Auto-Start Launcher (Windows)
'  Runs hand_cursor.py silently at login - no console window popup
'
'  HOW TO SET UP AUTO-START:
'  1. Press  Win + R  and type:   shell:startup   then press Enter
'  2. A folder will open — copy THIS .vbs file into that folder
'  3. Done! Virtual Cursor will start silently every time you log in.
'
'  HOW TO STOP AUTO-START:
'  1. Press  Win + R  and type:   shell:startup   then press Enter
'  2. Delete this .vbs file from the folder
' ================================================================

Dim WshShell
Dim scriptDir
Dim pythonExe
Dim scriptPath
Dim cmd

Set WshShell = CreateObject("WScript.Shell")

' ── EDIT IF PYTHON IS NOT ON PATH ─────────────────────────────
' Default: uses "python" from system PATH
' If it doesn't work, set the full path, for example:
'   pythonExe = "C:\Users\YourName\AppData\Local\Programs\Python\Python311\pythonw.exe"
pythonExe = "pythonw"
' ──────────────────────────────────────────────────────────────

' Auto-detect the folder where this .vbs file lives
scriptDir  = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
scriptPath = scriptDir & "hand_cursor.py"

cmd = """" & pythonExe & """ """ & scriptPath & """"

' Run hidden (0 = no window), don't wait (False)
WshShell.Run cmd, 0, False

WScript.Quit
