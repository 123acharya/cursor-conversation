@echo off
REM Update backup interval to 10 minutes
REM This script must be run as Administrator

echo Updating CursorChatAutoBackup scheduled task to run every 10 minutes...
echo.

REM Delete existing task
schtasks /delete /tn "CursorChatAutoBackup" /F >nul 2>&1

REM Recreate task with 10-minute interval
schtasks /create /tn "CursorChatAutoBackup" /tr "C:\Users\pc\Desktop\cursor-chat-backups\auto-backup.bat" /sc minute /mo 10 /ru "%USERNAME%" /f

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
