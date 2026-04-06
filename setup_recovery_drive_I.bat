@echo off
REM One-time: copy this entire backup folder to I:\cursor database (creates folder if needed).
REM Run from Desktop copy of cursor-chat-backups, or adjust source. Requires I: drive available.

set "TARGET=I:\cursor database"
if not exist "%TARGET%\" mkdir "%TARGET%"

echo Copying to "%TARGET%" ...
xcopy "%~dp0" "%TARGET%\" /E /I /Y /H >nul
if %ERRORLEVEL% GEQ 1 (
  echo Copy finished with warnings or error. Check that drive I: exists.
  pause
  exit /b 1
)
echo Done. Backups will use "%TARGET%" when auto-backup.bat finds extract_conversations.py there.
echo Next: run install_scheduled_task.bat from "%TARGET%" so Task Scheduler points to I: drive.
pause
