Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c """ & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\backup_versioned.bat""", 0, False
Set WshShell = Nothing
