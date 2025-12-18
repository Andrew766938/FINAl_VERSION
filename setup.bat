@echo off
echo ====================================
echo   FINAL_VERSION Setup Script
echo ====================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.12+
    pause
    exit /b 1
)
python --version
echo.

REM Remove old venv if exists
echo [2/5] Removing old virtual environment...
if exist venv (
    rmdir /s /q venv
    echo Old venv removed.
) else (
    echo No old venv found.
)
echo.

REM Create new venv
echo [3/5] Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create venv!
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

REM Activate venv and upgrade pip
echo [4/5] Activating venv and upgrading pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo [5/5] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo.

echo ====================================
echo   Setup completed successfully!
echo ====================================
echo.
echo To activate the virtual environment:
echo   - CMD: venv\Scripts\activate.bat
echo   - PowerShell: .\venv\Scripts\Activate.ps1
echo.
echo To run the application:
echo   uvicorn main:app --reload
echo.
pause
