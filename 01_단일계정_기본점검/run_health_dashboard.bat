@echo off
chcp 65001 >nul
echo ========================================
echo AWS Health Dashboard Start
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

:: Run Streamlit App
echo.
echo Starting AWS Health Dashboard...
echo Please access http://localhost:8501 in your browser.
echo.
echo Press Ctrl+C to exit.
echo.

streamlit run aws_health_dashboard.py --server.port 8501 --server.address localhost

pause