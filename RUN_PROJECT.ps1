$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Credit Risk Decision Engine - Setup and Run"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest -q
python run_project.py

Write-Host ""
Write-Host "SUCCESS"
Write-Host "Open reports\PROJECT_REPORT.md"
Write-Host "Dashboard file: dashboard\credit_risk_dashboard.csv"
