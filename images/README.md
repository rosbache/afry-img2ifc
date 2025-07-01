# Sample Images

Place your images with GPS EXIF data in this folder.

## Supported Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tiff, .tif)

## Requirements
Images must contain GPS coordinates in their EXIF metadata, including:
- Latitude and longitude
- Optionally: elevation and timestamp

## Example
After processing, images will be transformed from WGS84 to EPSG:5110 coordinates and exported as 3D sphere markers in an IFC file.

You can test the system by taking photos with a GPS-enabled camera or smartphone that saves location data to the image files.
