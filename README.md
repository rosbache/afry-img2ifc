# Image GPS to IFC Marker Exporter

This Python project processes images with GPS coordinates, transforms coordinates from WGS84 to any target EPSG code, and exports 3D markers to IFC format with support for both IFC2x3 and IFC4.3 schemas.

## Features

- Extract GPS coordinates, elevation, and date from image EXIF data
- Transform coordinates from WGS84 (EPSG:4326) to any target EPSG code (default: EPSG:5110)
- Create 3D cube markers at image locations
- Export markers to IFC format with image references and URLs
- Support for both IFC2x3 and IFC4.3 schemas
- Proper coordinate system representation in IFC4.3 using EPSG codes
- Support for various image formats (JPEG, PNG, TIFF)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Dependencies

The application relies on the following main libraries:
- `ifcopenshell` - For creating and manipulating IFC files
- `Pillow` (PIL) - For image processing and EXIF data extraction
- `pyproj` - For coordinate system transformations
- `tkinter` - For the graphical user interface

All dependencies are listed in the `requirements.txt` file and will be installed automatically with the pip command above.

## Usage

1. Place your images in the `images/` folder
2. Update the configuration in `config.py` if needed
3. Run the main script:
```bash
python main.py
```

The script will:
- Process all images in the images folder
- Extract GPS coordinates and metadata
- Transform coordinates to the specified target EPSG code
- Create an IFC file with 3D cube markers at each image location
- Apply proper coordinate system settings for IFC4.3 exports

## Configuration

Edit `config.py` to customize:
- Input/output paths
- Target EPSG code for coordinate transformation
- Cube marker radius and materials
- URL patterns for hosted images
- IFC schema version (IFC2x3 or IFC4X3)

## Scripts

### Main Pipeline
- **`main.py`** - Complete image processing pipeline (EXIF → coordinates → IFC)
- **`json_to_ifc.py`** - Standalone IFC generator from processed JSON data

### JSON to IFC Converter

If you already have processed image data in JSON format, you can generate IFC files directly:

```bash
# Auto-detect JSON file
python json_to_ifc.py

# Specify JSON file
python json_to_ifc.py processed_images.json

# Custom output location  
python json_to_ifc.py data.json -o markers.ifc

# Use IFC4.3 schema with EPSG support
python json_to_ifc.py data.json -o markers.ifc -s IFC4X3
```

This is useful for:
- Regenerating IFC files with different settings
- Creating IFC files without access to original images
- Batch processing multiple datasets
- Testing different IFC schemas and coordinate systems

## Output

The script generates:
- `output.ifc` - Default IFC file with 3D markers
- `markers.ifc` - IFC file with 4×4×4 meter cube markers  
- `extracted_images.json` - Summary of processed images and coordinates

## Using the GUI

The application includes a graphical user interface:

```bash
python -m src.gui.main_window
```

The GUI allows you to:
1. Select input image folders
2. Specify the target EPSG code for coordinate transformation
3. Choose between IFC2x3 and IFC4.3 schemas
4. Process images and generate IFC files in a step-by-step workflow

## Validation Tools

- **`validate_requirements.py`** - Comprehensive validation of IFC requirements
- **`verify_ifc.py`** - Basic IFC file structure verification  
- **`test_ifc_structure.py`** - Test IFC creation with dummy data

## Technical Details

### Coordinate System Handling

- Source coordinates are always in WGS84 (EPSG:4326) as provided by GPS
- The application can transform to any target EPSG code (default is EPSG:5110, Norwegian coordinate system)
- For IFC4.3 exports, the EPSG code is properly embedded in the IFC file using:
  - `IfcProjectedCRS` - Represents the target coordinate system
  - `IfcMapConversion` - Connects the project coordinate system to the EPSG reference

### GPS Extraction Process

The application handles various formats of GPS data in EXIF:
1. Extracts GPS coordinates in DMS (Degrees, Minutes, Seconds) format
2. Converts to decimal degrees
3. Transforms to the target coordinate system
4. Applies elevation data if available

## Distribution

To distribute this application to other users without publishing it online, you have several options:

### Option 1: Packaging as a Standalone Executable

You can use PyInstaller to create a standalone executable that includes Python and all dependencies:

```bash
# Install PyInstaller
pip install pyinstaller

# Create a single executable
pyinstaller --onefile --windowed --name afry-img2ifc --icon=resources/icon.ico src/gui/main_window.py

# Or create a directory with all dependencies (often more reliable)
pyinstaller --name afry-img2ifc --windowed --icon=resources/icon.ico src/gui/main_window.py
```

The resulting executable(s) will be in the `dist` folder and can be distributed to users who don't need to install Python.

### Option 2: Using the Included Distribution Files

This repository includes several files to help with distribution:

- `setup.bat` - Installs required dependencies on Windows
- `run_gui.bat` - Launches the graphical user interface
- `run_console.bat` - Runs the command-line version
- `setup.py` - For installing as a local Python package
- `installer.nsi` - NSIS script for creating a Windows installer

To create a distributable package:

1. Clone the repository
2. Include all necessary files (including the `.bat` files)
3. Create a ZIP archive of the contents
4. Instruct users to run `setup.bat` after extracting the ZIP

### Option 3: Creating an Installer

For a more professional distribution, you can create an installer:

1. Use the included NSIS script (`installer.nsi`) to create a Windows installer:
   - Install NSIS (Nullsoft Scriptable Install System) from https://nsis.sourceforge.io/
   - First use PyInstaller to create the application bundle
   - Right-click on `installer.nsi` and select "Compile NSIS Script"
   - The resulting `AFRY_Image2IFC_Setup.exe` can be distributed to users

2. The installer will:
   - Install the application to Program Files
   - Create Start Menu shortcuts
   - Add uninstall support
   - Create desktop shortcuts

This provides the most user-friendly installation experience for non-technical users.

## IFC File Specifications

- **Schemas**: 
  - IFC2x3 (compatible with most viewers like Solibri and BIMvision)
  - IFC4.3 (with proper coordinate system representation)
- **Units**: Meters
- **Markers**: 4×4×4 meter cubes (IfcBuildingElementProxy)
- **Coordinates**: 
  - IFC2x3: Direct placement using transformed coordinates
  - IFC4.3: Proper coordinate system representation using EPSG codes
- **Hierarchy**: Project → Site → Building → Storey → Markers
- **Metadata**: Complete image metadata as IFC properties
- **Document Links**: Image file paths accessible through document references
