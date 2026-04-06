@echo off
REM Auto-backup Cursor chats to Git — runs from THIS folder (works on any drive after you move it).
cd /d "%~dp0"

REM Optional: backup_config.bat sets SPECSTORY_ROOT, SPECSTORY_ROOT2, SPECSTORY_ROOT3 for .specstory scan paths
if exist "%~dp0backup_config.bat" call "%~dp0backup_config.bat"
if not defined SPECSTORY_ROOT set "SPECSTORY_ROOT=%USERPROFILE%\Desktop"

REM Extract conversations from Cursor database (safe JSON files, no secrets)
python extract_conversations.py >nul 2>&1

REM Copy SpecStory from each configured root (subfolders only)
for /d %%d in ("%SPECSTORY_ROOT%\*") do (
    if exist "%%d\.specstory" (
        if not exist "conversations" mkdir "conversations"
        echo Backing up SpecStory from: %%d
        xcopy /E /I /Y "%%d\.specstory" "conversations\%%~nxd\" >nul 2>&1
    )
)
if defined SPECSTORY_ROOT2 (
    for /d %%d in ("%SPECSTORY_ROOT2%\*") do (
        if exist "%%d\.specstory" (
            if not exist "conversations" mkdir "conversations"
            echo Backing up SpecStory from: %%d
            xcopy /E /I /Y "%%d\.specstory" "conversations\%%~nxd\" >nul 2>&1
        )
    )
)
if defined SPECSTORY_ROOT3 (
    for /d %%d in ("%SPECSTORY_ROOT3%\*") do (
        if exist "%%d\.specstory" (
            if not exist "conversations" mkdir "conversations"
            echo Backing up SpecStory from: %%d
            xcopy /E /I /Y "%%d\.specstory" "conversations\%%~nxd\" >nul 2>&1
        )
    )
)

REM Copy Cursor database (local backup only - not pushed to Git)
set CURSOR_DATA=%APPDATA%\Cursor\User\globalStorage
if exist "%CURSOR_DATA%\state.vscdb" (
    if not exist "databases" mkdir "databases"
    copy /Y "%CURSOR_DATA%\state.vscdb" "databases\state.vscdb" >nul 2>&1
)

REM Copy workspace storage (local backup only - not pushed to Git)
if exist "%APPDATA%\Cursor\User\workspaceStorage" (
    if not exist "workspace-storage" mkdir "workspace-storage"
    xcopy /E /I /Y "%APPDATA%\Cursor\User\workspaceStorage" "workspace-storage\" >nul 2>&1
)

REM Git operations
if exist ".git\index.lock" (
    echo Removing stale Git lock file...
    del /F /Q ".git\index.lock" >nul 2>&1
)

timeout /t 2 /nobreak >nul 2>&1

git add -A
git commit -m "Auto-backup: %date% %time%" --allow-empty >nul 2>&1

git push origin main >nul 2>&1 || git push origin master >nul 2>&1

REM Mirror to OneDrive (folder = wherever this script lives)
if exist "%USERPROFILE%\OneDrive" (
    if not exist "%USERPROFILE%\OneDrive\Cursor-Chat-Backups" mkdir "%USERPROFILE%\OneDrive\Cursor-Chat-Backups"
    xcopy /E /I /Y "%CD%" "%USERPROFILE%\OneDrive\Cursor-Chat-Backups\" >nul 2>&1
)
