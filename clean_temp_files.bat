@echo off
echo Cleaning temporary files...

:: 숫자로 시작하는 임시 폴더들 삭제
for /d %%i in (1.* 2.* 3.* 4.* 5.* 6.* 7.* 8.* 9.*) do (
    if exist "%%i" (
        echo Removing temporary folder: %%i
        rd /s /q "%%i"
    )
)

:: Python 캐시 폴더 삭제
for /d /r . %%i in (__pycache__) do (
    if exist "%%i" (
        echo Removing cache folder: %%i
        rd /s /q "%%i"
    )
)

:: .pyc 파일 삭제
del /s /q *.pyc 2>nul

:: 로그 파일 삭제 (선택사항)
del /q *.log 2>nul

:: 임시 보고서 파일 삭제
del /q aws_health_report_*.json 2>nul

echo Cleanup completed!