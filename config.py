"""
Configuration settings for the Image GPS to IFC Marker Exporter
"""

import os

# Paths
IMAGES_FOLDER = "C:\\Users\\HTO334\\OneDrive - AFRY\\Pictures\\e105-360 images\\test"
OUTPUT_FOLDER = "C:\\Users\\HTO334\\OneDrive - AFRY\\Pictures\\e105-360 images\\test\\output"
OUTPUT_IFC_FILE = os.path.join(OUTPUT_FOLDER, "markers.ifc")
PROCESSED_IMAGES_LOG = os.path.join(OUTPUT_FOLDER, "processed_images.json")

# Coordinate System Settings
SOURCE_CRS = "EPSG:4326"  # WGS84
TARGET_CRS = "EPSG:5110"  # Norwegian coordinate system

# Marker Settings
SPHERE_RADIUS = 2000.0  # Radius in millimeters (converted to 2m radius = 4x4x4m cube in IFC2x3)
SPHERE_COLOR = (0.8, 0.2, 0.2)  # RGB color (red)
SPHERE_SEGMENTS = 16  # Number of segments for sphere geometry

# URL Settings
# Base URL where images are hosted (modify this to match your hosting)
BASE_IMAGE_URL = "https://your-domain.com/images/"
# URL pattern: {BASE_IMAGE_URL}{filename}

# Processing Settings
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.tiff', '.tif']
REQUIRE_GPS_DATA = True  # Skip images without GPS data
REQUIRE_ELEVATION = False  # Allow images without elevation data (default to 0)

# IFC Settings
IFC_PROJECT_NAME = "GPS Image Markers"
IFC_SITE_NAME = "Image Location Site"
IFC_BUILDING_NAME = "Image Markers Building"
