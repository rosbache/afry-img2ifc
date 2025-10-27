@echo off
echo Building AFRY Image to IFC Converter...

:: Activate virtual environment if it exists, or create it if needed
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing requirements...
    pip install -r requirements.txt
    pip install pyinstaller
)

:: Clean any previous build files
echo Cleaning previous build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Verify all source files exist
echo Verifying source files...
if not exist src\core\image_processor.py (
    echo ERROR: src\core\image_processor.py not found!
    pause
    exit /b 1
)
if not exist src\utils\config.py (
    echo ERROR: src\utils\config.py not found!
    pause
    exit /b 1
)

:: Build the executable using the spec file
echo Building executable with PyInstaller...
pyinstaller --clean afry-img2ifc.spec

echo.
if %ERRORLEVEL% EQU 0 (
    echo Build completed successfully!
    echo The executable is available in dist\afry-img2ifc\afry-img2ifc.exe
    
    :: Test if the executable was actually created
    if exist dist\afry-img2ifc\afry-img2ifc.exe (
        echo Executable found and ready to use.
    ) else (
        echo WARNING: Executable not found in expected location!
    )
) else (
    echo Build failed with error code %ERRORLEVEL%
)

:: Create a test directory structure in the dist folder
echo Creating test output directory...
if not exist dist\afry-img2ifc\output mkdir dist\afry-img2ifc\output

echo.
echo You can now run the application by running dist\afry-img2ifc\afry-img2ifc.exe
echo.

:: Pause to see the results
pause
