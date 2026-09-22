@echo off
echo PHANTOM VISION LAB - Build
echo ===========================
echo.
pip install PySide6 numpy Pillow matplotlib scipy 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)
echo Installing PyInstaller...
pip install pyinstaller 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Could not install PyInstaller
)
echo Building...
pyinstaller --onefile --windowed --name "PhantomVisionLab" --icon="" main.py
if %ERRORLEVEL% EQU 0 (
    echo Build successful: dist\PhantomVisionLab.exe
) else (
    echo Build failed
)
pause
