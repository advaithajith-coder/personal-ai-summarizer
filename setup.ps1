$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (!$pythonCommand -or $pythonCommand.Source -like '*WindowsApps*') {
    throw 'Install Python 3.11 or 3.12 from python.org, enable Add Python to PATH, then reopen PowerShell.'
}
& $pythonCommand.Source -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment.' }
& '.venv/Scripts/python.exe' -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
if (!(Test-Path '.env')) { Copy-Item '.env.example' '.env' }
Write-Host 'Setup complete. Edit .env, then run ./start.ps1.'
