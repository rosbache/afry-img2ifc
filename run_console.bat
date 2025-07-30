@echo off
echo Running AFRY Image to IFC Converter...
python main.py %*
if %errorlevel% neq 0 (
    echo.
    echo There was an error running the application.
    pause
)
