# Cursor versioned backup — keeps last 48 hourly snapshots
$src = "$env:APPDATA\Cursor\User\globalStorage\state.vscdb"
$dir = "I:\cursor database\snapshots"

if (!(Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }

if (!(Test-Path $src)) {
    Write-Error "Cursor DB not found: $src"
    exit 1
}

$ts  = Get-Date -Format "yyyyMMdd_HHmm"
$dst = "$dir\state_$ts.vscdb"

Copy-Item -Path $src -Destination $dst -Force
Write-Host "Backed up: $dst"

# Keep only last 48 snapshots
$files = Get-ChildItem $dir -Filter "state_*.vscdb" | Sort-Object LastWriteTime -Descending
if ($files.Count -gt 48) {
    $files | Select-Object -Skip 48 | Remove-Item -Force
    Write-Host "Removed $($files.Count - 48) old snapshot(s)"
}

Write-Host "Total snapshots: $([Math]::Min($files.Count, 48))"

# Extract all conversations (user + AI) as readable markdown files
$python = "C:\Users\pc\anaconda3\python.exe"
$script = "C:\Users\pc\Desktop\cursor-chat-backups\extract_conversations.py"
if ((Test-Path $python) -and (Test-Path $script)) {
    Write-Host "Extracting conversations to markdown..."
    & $python $script
} else {
    Write-Warning "Skipping extraction: python or script not found"
}
