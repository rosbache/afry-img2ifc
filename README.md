# Image GPS to IFC Marker Exporter

This Python project processes images with GPS coordinates, transforms coordinates from WGS84 to EPSG:5110, and exports 3D markers to IFC format.

## Features

- Extract GPS coordinates, elevation, and date from image EXIF data
- Transform coordinates from WGS84 (EPSG:4326) to EPSG:5110
- Create 3D sphere markers at image locations
- Export markers to IFC format with image references and URLs
- Support for various image formats (JPEG, PNG, TIFF)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

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
- Transform coordinates to EPSG:5110
- Create an IFC file with 3D sphere markers at each image location

## Configuration

Edit `config.py` to customize:
- Input/output paths
- Sphere radius and materials
- URL patterns for hosted images
- Coordinate system parameters

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
```

This is useful for:
- Regenerating IFC files with different settings
- Creating IFC files without access to original images
- Batch processing multiple datasets

## Output

The script generates:
- `output.ifc` - IFC file with 3D markers
- `markers.ifc` - IFC file with 4×4×4 meter cube markers  
- `processed_images.json` - Summary of processed images and coordinates

## Validation Tools

- **`validate_requirements.py`** - Comprehensive validation of IFC requirements
- **`verify_ifc.py`** - Basic IFC file structure verification  
- **`test_ifc_structure.py`** - Test IFC creation with dummy data

## IFC File Specifications

- **Schema**: IFC2x3 (compatible with Solibri and BIMvision)
- **Units**: Meters
- **Markers**: 4×4×4 meter cubes (IfcBuildingElementProxy)
- **Coordinates**: Direct EPSG:5110 placement (no local offsets)
- **Hierarchy**: Project → Site → Building → Storey → Markers
- **Metadata**: Complete image metadata as IFC properties
