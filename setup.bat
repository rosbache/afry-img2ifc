@echo off
echo Installing AFRY Image to IFC Converter...
echo.

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in the PATH.
    echo Please install Python 3.6 or higher before continuing.
    pause
    exit /b 1
)

:: Install dependencies
echo Installing required packages...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo There was an error installing the required packages.
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo.
echo You can now run the application using:
echo   - run_gui.bat      (for the graphical interface)
echo   - run_console.bat  (for the command-line interface)
echo.
pause
