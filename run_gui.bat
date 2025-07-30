@echo off
echo Starting AFRY Image to IFC Converter GUI...
python -m src.gui.main_window
if %errorlevel% neq 0 (
    echo.
    echo There was an error running the application.
    pause
)
