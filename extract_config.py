"""
Simple Image Extractor Configuration
Simplified config for image-only processing
"""

# Default paths - these can be overridden by command line arguments
DEFAULT_IMAGES_FOLDER = "images"
DEFAULT_OUTPUT_FOLDER = "output"

# Image processing settings
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif']

# Coordinate systems for transformation
SOURCE_CRS = "EPSG:4326"  # WGS84 (GPS coordinates)
TARGET_CRS = "EPSG:5110"  # Norwegian coordinate system (modify as needed)

# Processing options
DEFAULT_INCLUDE_NO_GPS = False  # Include images without GPS data by default
DEFAULT_VERBOSE = False  # Verbose output by default

# JSON output formatting
PRETTY_PRINT = True  # Pretty print JSON by default
INDENT_SIZE = 2  # JSON indentation
