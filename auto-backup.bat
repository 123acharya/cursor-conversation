@echo off
REM Auto-backup Cursor chats to Git
cd /d "C:\Users\pc\Desktop\cursor-chat-backups"

REM Copy SpecStory conversations from Desktop projects
for /d %%d in ("C:\Users\pc\Desktop\*") do (
    if exist "%%d\.specstory" (
        if not exist "conversations" mkdir "conversations"
        echo Backing up SpecStory from: %%d
        xcopy /E /I /Y "%%d\.specstory" "conversations\%%~nxd\" >nul 2>&1
    )
)

REM Copy Cursor database (local backup only - not pushed to Git)
REM Database files contain secrets, so they're excluded from Git via .gitignore
set CURSOR_DATA=%APPDATA%\Cursor\User\globalStorage
if exist "%CURSOR_DATA%\state.vscdb" (
    if not exist "databases" mkdir "databases"
    copy /Y "%CURSOR_DATA%\state.vscdb" "databases\state.vscdb" >nul 2>&1
)

REM Copy workspace storage (local backup only - not pushed to Git)
REM Workspace files contain secrets, so they're excluded from Git via .gitignore
if exist "%APPDATA%\Cursor\User\workspaceStorage" (
    if not exist "workspace-storage" mkdir "workspace-storage"
    xcopy /E /I /Y "%APPDATA%\Cursor\User\workspaceStorage" "workspace-storage\" >nul 2>&1
)

REM Git operations
git add -A
git commit -m "Auto-backup: %date% %time%" --allow-empty >nul 2>&1

REM Push to remote if configured
git push origin main >nul 2>&1 || git push origin master >nul 2>&1

REM Sync to OneDrive if available
if exist "%USERPROFILE%\OneDrive" (
    if not exist "%USERPROFILE%\OneDrive\Cursor-Chat-Backups" mkdir "%USERPROFILE%\OneDrive\Cursor-Chat-Backups"
    xcopy /E /I /Y "C:\Users\pc\Desktop\cursor-chat-backups" "%USERPROFILE%\OneDrive\Cursor-Chat-Backups\" >nul 2>&1
)
