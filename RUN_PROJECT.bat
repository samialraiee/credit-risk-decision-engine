@echo off
setlocal
cd /d "%~dp0"

echo ======================================================
echo Credit Risk Decision Engine - Automated Setup and Run
echo ======================================================

set PYTHON_CMD=
where py >nul 2>nul
if %errorlevel%==0 (
    py -3.13 -c "import sys" >nul 2>nul
    if %errorlevel%==0 set PYTHON_CMD=py -3.13

    if not defined PYTHON_CMD (
        py -3.12 -c "import sys" >nul 2>nul
        if %errorlevel%==0 set PYTHON_CMD=py -3.12
    )

    if not defined PYTHON_CMD (
        py -3.11 -c "import sys" >nul 2>nul
        if %errorlevel%==0 set PYTHON_CMD=py -3.11
    )

    if not defined PYTHON_CMD (
        py -3.14 -c "import sys" >nul 2>nul
        if %errorlevel%==0 set PYTHON_CMD=py -3.14
    )
)

if not defined PYTHON_CMD set PYTHON_CMD=python

echo Using Python:
%PYTHON_CMD% --version

if not exist .venv (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :error
)

call .venv\Scripts\activate.bat

echo.
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo Running automated tests...
python -m pip install pytest
python -m pytest -q
if errorlevel 1 goto :error

echo.
echo Running full credit-risk pipeline...
python "%~dp0run_project.py"
if errorlevel 1 goto :error

echo.
echo ======================================================
echo SUCCESS
echo Open reports\PROJECT_REPORT.md
echo Dashboard file: dashboard\credit_risk_dashboard.csv
echo ======================================================
pause
exit /b 0

:error
echo.
echo ======================================================
echo PROJECT DID NOT COMPLETE
echo ======================================================
echo Copy the full error above and send it to ChatGPT.
pause
exit /b 1
