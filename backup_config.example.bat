@echo off
REM ============================================================================
REM Copy this file to:  backup_config.bat  (same folder as auto-backup.bat)
REM Then edit paths below. Lines are optional — omit or leave blank for defaults.
REM ============================================================================

REM Where to look for project folders that contain .specstory (each subfolder of this path is checked).
REM Default if unset: %USERPROFILE%\Desktop
REM Example — use another drive or Documents:
REM set "SPECSTORY_ROOT=D:\Dev"
REM set "SPECSTORY_ROOT=%USERPROFILE%\Documents"

REM Optional extra scan roots (uncomment and set):
REM set "SPECSTORY_ROOT2=%USERPROFILE%\Documents"
REM set "SPECSTORY_ROOT3=E:\Projects"
