@echo off
chcp 65001 >nul
echo ========================================
echo AWS Multi-Account Dashboard Start
echo ========================================

:: Clean temporary files first
for /d %%i in (1.* 2.* 3.* 4.* 5.* 6.* 7.* 8.* 9.*) do (
    if exist "%%i" rd /s /q "%%i" 2>nul
)
for /d %%i in (__pycache__) do (
    if exist "%%i" rd /s /q "%%i" 2>nul
)

:: Python Virtual Environment Check
if exist "venv" (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing required packages...
    pip install -r ../00_공통설정/requirements.txt
)

:: Configuration File Check
if not exist "../00_공통설정/aws_config.json" (
    echo Configuration file not found. Copying template...
    copy "../00_공통설정/aws_config.json.template" "../00_공통설정/aws_config.json"
    echo Please edit aws_config.json file in 00_공통설정 folder and run again.
    pause
    exit /b 1
)

:: Run Multi-Account Dashboard
echo.
echo Starting AWS Multi-Account Health Dashboard...
echo Please access http://localhost:8502 in your browser.
echo.
echo Press Ctrl+C to exit.
echo.

streamlit run aws_multi_dashboard.py --server.port 8502 --server.address localhost

pause