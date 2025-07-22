@echo off
chcp 65001 >nul
echo ========================================
echo AWS Multi-Account Health Check
echo ========================================

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

:: Run Multi-Account Monitor
echo.
echo Starting AWS Multi-Account Health Check...
echo This will check all AWS accounts configured in aws_config.json
echo.

python aws_multi_account_monitor.py

echo.
echo Multi-Account Health Check completed.
echo Check the log file: aws_multi_account_monitor.log
echo Check the report file: aws_health_report_YYYYMMDD_HHMMSS.json
echo.

pause