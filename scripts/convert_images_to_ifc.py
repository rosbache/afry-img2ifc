#!/usr/bin/env python3
"""
Simple script to convert image GPS data from JSON to IFC file
"""

import os
import sys
from pathlib import Path

# Add the src/core directory to the Python path
script_dir = Path(__file__).parent
src_core_dir = script_dir / "src" / "core"
sys.path.insert(0, str(src_core_dir))

from ifc_exporter import IFCExporter

def main():
    # Define file paths
    json_file = r"C:\Users\HTO334\OneDrive - AFRY\Pictures\hovden\New folder\extracted_images4.json"
    output_file = r"C:\Users\HTO334\OneDrive - AFRY\Pictures\hovden\New folder\image_markers.ifc"
    
    # Optional: Define project settings (can be None)
    project_settings = r"C:\Users\HTO334\OneDrive - AFRY\Pictures\hovden\New folder\project_settings_template.json"
    
    # Choose IFC schema version ("IFC2x3" or "IFC4X3")
    schema = "IFC2x3"  # Change to "IFC4X3" if needed
    
    # Create IFC exporter
    print("Initializing IFC exporter...")
    exporter = IFCExporter()
    
    # Export markers from JSON to IFC
    print(f"Converting {json_file} to {output_file}...")
    try:
        exporter.export_markers_from_json(
            json_file_path=json_file,
            output_path=output_file,
            project_settings_path=project_settings,
            schema=schema
        )
        print("✅ Conversion completed successfully!")
        print(f"📁 Output file: {output_file}")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())