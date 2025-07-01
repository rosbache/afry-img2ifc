# JSON to IFC Converter

A standalone script that generates IFC files from previously processed image data stored in JSON format.

## Purpose

This script allows you to regenerate IFC files without needing the original images, using only the processed coordinate and metadata information stored in `processed_images.json`.

## Features

- ✅ **Standalone Operation**: No need for original images
- ✅ **Data Validation**: Validates JSON data before processing
- ✅ **Auto-Detection**: Can automatically find JSON files in common locations
- ✅ **IFC2x3 Compatible**: Generates viewer-ready IFC files
- ✅ **Complete Metadata**: Preserves all image metadata and coordinates

## Usage

### Basic Usage (Auto-detect JSON file)
```bash
python json_to_ifc.py
```

### Specify JSON file path
```bash
python json_to_ifc.py path/to/processed_images.json
```

### Specify custom output location
```bash
python json_to_ifc.py processed_images.json -o custom_output.ifc
```

## Input Requirements

The JSON file must contain an array of image data objects with these required fields:

```json
[
  {
    "filename": "image.jpg",
    "latitude": 59.913749,
    "longitude": 10.580113,
    "elevation": 64.844,
    "image_url": "https://domain.com/images/image.jpg",
    "transformed_x": 104481.92,
    "transformed_y": 1213183.52,
    "transformed_z": 64.844
  }
]
```

### Required Fields
- `filename`: Original image filename
- `latitude`: GPS latitude (WGS84)
- `longitude`: GPS longitude (WGS84)
- `elevation`: Elevation in meters
- `image_url`: URL to the image
- `transformed_x`: X coordinate in EPSG:5110
- `transformed_y`: Y coordinate in EPSG:5110
- `transformed_z`: Z coordinate in meters

### Optional Fields
- `date_taken`: Date/time the image was taken
- `filepath`: Original file path

## Output

The script generates:
1. **IFC File**: Complete IFC2x3 file with 4×4×4 meter cube markers
2. **Console Summary**: Details of processed images and coordinates
3. **Validation**: Automatic validation of generated content

## Examples

### Example 1: Using provided test data
```bash
python json_to_ifc.py "C:\Users\HTO334\OneDrive - AFRY\Pictures\e105-360 images\test\output\processed_images.json"
```

### Example 2: Custom output location
```bash
python json_to_ifc.py data.json -o models/markers.ifc
```

## Generated IFC Features

- **Schema**: IFC2x3 (Solibri/BIMvision compatible)
- **Units**: Meters
- **Markers**: 4×4×4 meter cubes (IfcBuildingElementProxy)
- **Hierarchy**: Project → Site → Building → Storey → Markers
- **Coordinates**: Direct EPSG:5110 placement
- **Properties**: Complete image metadata as IFC properties

## Integration

This script uses the same `IFCExporter` class as the main image processing pipeline, ensuring consistent output quality and format.

## Validation

The script includes automatic validation:
- JSON file format and structure
- Required field presence
- Data type validation
- IFC file generation verification

## Error Handling

- Missing or invalid JSON files
- Malformed data structures
- IFC generation errors
- File system permission issues
