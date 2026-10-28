$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (!(Test-Path '.venv/Scripts/python.exe')) { throw 'Run setup.ps1 first.' }
if (!(Test-Path '.env')) { throw 'Copy .env.example to .env and fill in your settings first.' }
& '.venv/Scripts/python.exe' -m uvicorn app:app --host 0.0.0.0 --port 8000
