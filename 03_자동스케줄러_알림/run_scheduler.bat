@echo off
chcp 65001 >nul
echo ========================================
echo AWS Health Scheduler Start
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
if not exist "health_config.json" (
    echo Configuration file not found. Copying template...
    copy health_config.json.template health_config.json
    echo Please edit health_config.json file and run again.
    pause
    exit /b 1
)

:: AWS Configuration File Check
if not exist "../00_공통설정/aws_config.json" (
    echo AWS configuration file not found. Copying template...
    copy "../00_공통설정/aws_config.json.template" "../00_공통설정/aws_config.json"
    echo Please edit aws_config.json file in 00_공통설정 folder and run again.
    pause
    exit /b 1
)

:: Run Scheduler
echo.
echo Starting AWS Health Scheduler...
echo Daily check and urgent alert features are activated.
echo.
echo Press Ctrl+C to exit.
echo.

python health_scheduler.py

pause