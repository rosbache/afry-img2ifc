# Building and Distributing AFRY Image to IFC Converter

This document outlines the steps to build and distribute the AFRY Image to IFC Converter application using PyInstaller.

## Prerequisites

1. Make sure you have all the required packages installed:
   ```
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. If you want to create an installer, install NSIS (Nullsoft Scriptable Install System):
   - Download from: https://nsis.sourceforge.io/Download
   - Install with default settings

## Building the Application

### Automated Build (Recommended)

1. Run the `build_exe.bat` file by double-clicking it or running from command prompt:
   ```
   build_exe.bat
   ```

2. This will:
   - Create or activate a virtual environment
   - Install required dependencies
   - Build the application using PyInstaller
   - Create the application in the `dist/afry-img2ifc` folder

3. The executable will be located at:
   ```
   dist/afry-img2ifc/afry-img2ifc.exe
   ```

### Manual Build

If you prefer to build manually:

1. Ensure you're in a virtual environment with all dependencies installed
2. Run PyInstaller with the spec file:
   ```
   pyinstaller afry-img2ifc.spec
   ```

## Testing the Executable

1. Navigate to the `dist/afry-img2ifc` folder
2. Run `afry-img2ifc.exe`
3. Verify that the application starts without errors
4. Test the main functionality (image processing, IFC export)

## Creating an Installer

To create a Windows installer for distribution:

1. Make sure NSIS is installed
2. Right-click on `installer.nsi` and select "Compile NSIS Script"
   (or run `makensis installer.nsi` from the command line)
3. This will create `AFRY_Image2IFC_Setup.exe` in the project root folder

## Troubleshooting Common Issues

### Missing Modules

If you encounter "ModuleNotFoundError" messages:

1. Check that all required modules are listed in the `hiddenimports` section of `afry-img2ifc.spec`
2. Rebuild using the steps above

### File Not Found Errors

If the application can't find necessary files:

1. Verify that all required files are included in the `added_files` section of `afry-img2ifc.spec`
2. Make sure the output directory exists in the distribution folder

### Debugging

The executable is configured to show a console window for debugging. If you want to hide this window for the final release:

1. Change `console=True` to `console=False` in `afry-img2ifc.spec`
2. Rebuild the application

## Distribution

The final distribution consists of either:

1. The entire `dist/afry-img2ifc` folder (can be zipped for distribution)
2. The `AFRY_Image2IFC_Setup.exe` installer

Users can run the application without installing Python or any dependencies.
