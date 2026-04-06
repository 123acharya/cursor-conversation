@echo off
REM Register Task Scheduler to run auto-backup. Prefers I:\cursor database if that copy exists.

set "BAT_I=I:\cursor database\auto-backup.bat"
if exist "%BAT_I%" (
  set "BAT=%BAT_I%"
) else (
  set "BAT=%~dp0auto-backup.bat"
)

if not exist "%BAT%" (
  echo ERROR: auto-backup.bat not found at:
  echo   %BAT_I%
  echo   or next to this script.
  echo Run setup_recovery_drive_I.bat first if you use the I: drive folder.
  pause
  exit /b 1
)

echo Registering task CursorChatAutoBackup -^> "%BAT%"
schtasks /delete /tn "CursorChatAutoBackup" /F >nul 2>&1
schtasks /create /tn "CursorChatAutoBackup" /tr "\"%BAT%\"" /sc minute /mo 10 /ru "%USERNAME%" /f
if %ERRORLEVEL% EQU 0 (
  echo OK. Task runs every 10 minutes.
  schtasks /query /tn "CursorChatAutoBackup" /fo list | findstr /C:"Task To Run" /C:"Repeat: Every"
) else (
  echo FAILED. Try: Run as administrator
  pause
  exit /b 1
)
pause
