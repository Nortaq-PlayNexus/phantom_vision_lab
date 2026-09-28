@echo off
echo PHANTOM VISION LAB
echo ===========================
echo.
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo Error: Application failed to start
    pause
    exit /b 1
)
