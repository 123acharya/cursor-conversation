@echo off
REM Update backup interval to 10 minutes (task points to auto-backup.bat in THIS folder)
REM Run from the cursor-chat-backups folder. Administrator may be required.

cd /d "%~dp0"
set "BAT=%~dp0auto-backup.bat"
if not exist "%BAT%" (
  echo ERROR: auto-backup.bat not found.
  pause
  exit /b 1
)

echo Updating CursorChatAutoBackup -^> "%BAT%"
echo.

schtasks /delete /tn "CursorChatAutoBackup" /F >nul 2>&1

schtasks /create /tn "CursorChatAutoBackup" /tr "\"%BAT%\"" /sc minute /mo 10 /ru "%USERNAME%" /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Successfully updated scheduled task to run every 10 minutes!
    echo.
    schtasks /query /tn "CursorChatAutoBackup" /fo list | findstr /C:"Repeat: Every"
) else (
    echo.
    echo Error: Failed to update scheduled task.
    echo Please run this script as Administrator.
    pause
)
