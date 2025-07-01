"""
Main script for processing images with GPS coordinates and exporting to IFC
"""

import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from image_processor import ImageProcessor
from ifc_exporter import IFCExporter
import config


def main():
    """Main processing function"""
    print("=== Image GPS to IFC Marker Exporter ===")
    print()
    
    # Initialize processors
    image_processor = ImageProcessor()
    ifc_exporter = IFCExporter()
    
    # Check if images folder exists
    if not os.path.exists(config.IMAGES_FOLDER):
        print(f"Error: Images folder not found: {config.IMAGES_FOLDER}")
        print("Please create the folder and add your images with GPS data.")
        return
    
    # Create output folder if it doesn't exist
    os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)
    
    # Process images
    print(f"Processing images from: {config.IMAGES_FOLDER}")
    print(f"Supported formats: {', '.join(config.SUPPORTED_FORMATS)}")
    print(f"Coordinate transformation: {config.SOURCE_CRS} -> {config.TARGET_CRS}")
    print()
    
    processed_images = image_processor.process_images_folder(config.IMAGES_FOLDER)
    
    if not processed_images:
        print("No images with GPS data found. Please check:")
        print("1. Images are in the correct folder")
        print("2. Images contain GPS EXIF data")
        print("3. Images are in supported formats")
        return
    
    print()
    print(f"Successfully processed {len(processed_images)} images")
    
    # Save processed data
    image_processor.save_processed_data(processed_images, config.PROCESSED_IMAGES_LOG)
    
    # Export to IFC
    print()
    print("Exporting markers to IFC...")
    try:
        ifc_exporter.export_markers(processed_images, config.OUTPUT_IFC_FILE)
    except Exception as e:
        print(f"Error during IFC export: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("=== Processing Complete ===")
    print(f"Output files:")
    print(f"  IFC file: {config.OUTPUT_IFC_FILE}")
    print(f"  Processed data: {config.PROCESSED_IMAGES_LOG}")
    print()
    print("The IFC file contains 3D sphere markers at each image location.")
    print("Each marker includes:")
    print("- Original GPS coordinates")
    print("- Transformed coordinates (EPSG:5110)")
    print("- Image filename and URL")
    print("- Date taken (if available)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
