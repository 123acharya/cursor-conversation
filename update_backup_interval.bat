@echo off
REM Update scheduled task to 10 min — uses I:\cursor database\auto-backup.bat if present.

set "BAT_I=I:\cursor database\auto-backup.bat"
if exist "%BAT_I%" (
  set "BAT=%BAT_I%"
) else (
  set "BAT=%~dp0auto-backup.bat"
)

if not exist "%BAT%" (
  echo ERROR: auto-backup.bat not found.
  pause
  exit /b 1
)

echo Updating CursorChatAutoBackup -^> "%BAT%"
schtasks /delete /tn "CursorChatAutoBackup" /F >nul 2>&1
schtasks /create /tn "CursorChatAutoBackup" /tr "\"%BAT%\"" /sc minute /mo 10 /ru "%USERNAME%" /f
if %ERRORLEVEL% EQU 0 (
  echo OK.
  schtasks /query /tn "CursorChatAutoBackup" /fo list | findstr /C:"Task To Run" /C:"Repeat: Every"
) else (
  echo FAILED. Run as administrator.
  pause
  exit /b 1
)
pause
