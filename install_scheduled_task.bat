@echo off
REM Create / update Task Scheduler job to run auto-backup from THIS folder (any drive).
REM Run from the folder where auto-backup.bat lives (e.g. after moving to D:\Backups\cursor-chat-backups).
REM May require: Run as administrator

cd /d "%~dp0"
set "BAT=%~dp0auto-backup.bat"
if not exist "%BAT%" (
  echo ERROR: auto-backup.bat not found next to this script.
  pause
  exit /b 1
)

echo Registering task CursorChatAutoBackup -^> "%BAT%"
schtasks /delete /tn "CursorChatAutoBackup" /F >nul 2>&1
schtasks /create /tn "CursorChatAutoBackup" /tr "\"%BAT%\"" /sc minute /mo 10 /ru "%USERNAME%" /f
if %ERRORLEVEL% EQU 0 (
  echo OK. Task runs every 10 minutes. Path: %BAT%
  schtasks /query /tn "CursorChatAutoBackup" /fo list | findstr /C:"Task To Run" /C:"Repeat: Every"
) else (
  echo FAILED. Try: right-click this file -^> Run as administrator
  pause
  exit /b 1
)
pause
