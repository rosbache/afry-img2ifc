"""
Configuration settings for the Image GPS to IFC Converter
"""

# Default coordinate reference system (Norwegian)
TARGET_CRS = "EPSG:5110"

# Supported image formats
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.tiff', '.tif', '.png']

# IFC settings
IFC_SCHEMA = "IFC2X3"
IFC_VERSION = "2x3"

# Application settings
APP_NAME = "Image GPS to IFC Converter"
APP_VERSION = "1.0.0"
ORGANIZATION = "AFRY"

# Default project settings template
DEFAULT_PROJECT_SETTINGS = {
    "project_settings": {
        "ifc_project_name": "PROJECT_NAME",
        "ifc_project_description": "Project Description",
        "ifc_site_name": "Site Name",
        "ifc_site_description": "Site Description",
        "ifc_building": "Building Name",
        "ifc_building_description": "Building Description",
        "ifc_building_storey": "Storey Name",
        "ifc_building_storey_description": "Storey Description"
    },
    "owner_information": {
        "person_given_name": "First Name",
        "person_family_name": "Last Name",
        "organization_name": "Organization Name"
    }
}

# Processing settings
INCLUDE_NO_GPS_IMAGES = False
VERBOSE_OUTPUT = False
THREAD_TIMEOUT = 300  # 5 minutes

# GUI settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
DEFAULT_EPSG_CODE = "5110"
