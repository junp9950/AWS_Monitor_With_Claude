@echo off
chcp 65001 >nul
echo ========================================
echo AWS Multi-Account Dashboard Setup
echo ========================================

:: Change to script directory
cd /d "%~dp0"

:: Clean temporary files first
echo Cleaning temporary files...
for /d %%i in (1.* 2.* 3.* 4.* 5.* 6.* 7.* 8.* 9.*) do (
    if exist "%%i" rd /s /q "%%i" 2>nul
)
for /d %%i in (__pycache__) do (
    if exist "%%i" rd /s /q "%%i" 2>nul
)
del /q *.pyc *.log 2>nul

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Remove existing venv if exists
if exist "venv" (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

:: Create new virtual environment
echo Creating new virtual environment...
python -m venv venv

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install packages directly
echo Installing required packages...
pip install boto3>=1.34.0
pip install streamlit>=1.28.0
pip install plotly>=5.17.0
pip install pandas>=2.1.0
pip install schedule>=1.2.0
pip install python-dateutil>=2.8.0
pip install pytz>=2023.3

:: Verify installation
echo.
echo Verifying installation...
python -c "import boto3; print('✅ boto3 installed successfully')"
python -c "import streamlit; print('✅ streamlit installed successfully')"

:: Configuration File Check
if not exist "../00_공통설정/aws_config.json" (
    echo.
    echo ⚠️ Configuration file not found. Copying template...
    copy "../00_공통설정/aws_config.json.template" "../00_공통설정/aws_config.json"
    echo Please edit aws_config.json file in 00_공통설정 folder and run again.
    pause
    exit /b 1
)

:: Run Dashboard
echo.
echo ========================================
echo Starting AWS Multi-Account Dashboard
echo ========================================
echo Please access http://localhost:8502 in your browser.
echo Press Ctrl+C to exit.
echo.

streamlit run aws_multi_dashboard.py --server.port 8502 --server.address localhost

pause