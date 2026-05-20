# Run CLI with project dependencies (avoids system Python missing openpyxl).
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
& "$Root\.venv\Scripts\python.exe" main.py @args
