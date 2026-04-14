@echo off
REM Cursor versioned backup — keeps last 48 hourly snapshots

set "CURSOR_DB=%APPDATA%\Cursor\User\globalStorage\state.vscdb"
set "BACKUP_DIR=%~dp0snapshots"
set "MAX_KEEP=48"

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Build timestamp using PowerShell (locale-safe)
for /f %%t in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmm"') do set "TS=%%t"

set "FNAME=state_%TS%.vscdb"

if exist "%CURSOR_DB%" (
    copy /Y "%CURSOR_DB%" "%BACKUP_DIR%\%FNAME%" >nul 2>&1
    echo Backed up: %FNAME%
) else (
    echo ERROR: Cursor DB not found at %CURSOR_DB%
    exit /b 1
)

REM Delete oldest files, keep only MAX_KEEP
set /a COUNT=0
for /f "skip=%MAX_KEEP% delims=" %%f in ('dir /b /o-d "%BACKUP_DIR%\state_*.vscdb" 2^>nul') do (
    del /Q "%BACKUP_DIR%\%%f" >nul 2>&1
)

echo Done. Snapshots in: %BACKUP_DIR%
