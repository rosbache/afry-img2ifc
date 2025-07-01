"""
Standalone IFC generator that uses processed_images.json to create IFC files
This script allows regenerating IFC files from previously processed image data
"""

import json
import os
import sys
import ifcopenshell
import config

# Add src directory to path for importing modules
sys.path.append('src')
from ifc_exporter import IFCExporter


def load_processed_images(json_path: str) -> list:
    """
    Load processed image data from JSON file
    
    Args:
        json_path: Path to the processed_images.json file
        
    Returns:
        List of processed image data dictionaries
    """
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found: {json_path}")
        return []
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {len(data)} processed images from {json_path}")
        return data
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON file: {e}")
        return []
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return []


def validate_image_data(image_data: dict) -> bool:
    """
    Validate that image data contains required fields
    
    Args:
        image_data: Dictionary containing image data
        
    Returns:
        True if data is valid, False otherwise
    """
    required_fields = [
        'filename', 'latitude', 'longitude', 'elevation',
        'image_url', 'transformed_x', 'transformed_y', 'transformed_z'
    ]
    
    for field in required_fields:
        if field not in image_data:
            print(f"❌ Missing required field '{field}' in image data")
            return False
    
    return True


def generate_ifc_from_json(json_path: str, output_path: str = None):
    """
    Generate IFC file from processed images JSON
    
    Args:
        json_path: Path to the processed_images.json file
        output_path: Output path for IFC file (optional, will use default if not provided)
    """
    print("=" * 60)
    print("🏗️  IFC Generator from JSON")
    print("=" * 60)
    
    # Load processed image data
    processed_images = load_processed_images(json_path)
    
    if not processed_images:
        print("❌ No image data to process")
        return False
    
    # Validate image data
    valid_images = []
    for i, image_data in enumerate(processed_images):
        if validate_image_data(image_data):
            valid_images.append(image_data)
        else:
            print(f"❌ Skipping invalid image data at index {i}")
    
    if not valid_images:
        print("❌ No valid image data found")
        return False
    
    print(f"✅ Validated {len(valid_images)} image records")
    
    # Set default output path if not provided
    if output_path is None:
        json_dir = os.path.dirname(json_path)
        output_path = os.path.join(json_dir, "markers_from_json.ifc")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create IFC exporter and generate file
    try:
        print(f"\n🔨 Creating IFC file...")
        print(f"📁 Output: {output_path}")
        
        exporter = IFCExporter()
        exporter.export_markers(valid_images, output_path)
        
        # Verify the output file
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n✅ IFC file created successfully!")
            print(f"📊 File size: {file_size:,} bytes")
            print(f"📍 Markers: {len(valid_images)}")
            
            # Display summary of image locations
            print(f"\n📋 Image Summary:")
            for i, img in enumerate(valid_images, 1):
                print(f"   {i:2d}. {img['filename']}")
                print(f"       GPS: {img['latitude']:.6f}, {img['longitude']:.6f}")
                print(f"       EPSG:5110: {img['transformed_x']:.1f}, {img['transformed_y']:.1f}, {img['transformed_z']:.1f}")
            
            return True
        else:
            print("❌ IFC file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error creating IFC file: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to run the IFC generator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate IFC file from processed_images.json"
    )
    parser.add_argument(
        "json_path",
        help="Path to the processed_images.json file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output path for the IFC file (optional)"
    )
    
    args = parser.parse_args()
    
    # Check if JSON file exists
    if not os.path.exists(args.json_path):
        print(f"❌ JSON file not found: {args.json_path}")
        print("\nUsage examples:")
        print("  python json_to_ifc.py processed_images.json")
        print("  python json_to_ifc.py data/processed_images.json -o output/custom.ifc")
        return 1
    
    # Generate IFC file
    success = generate_ifc_from_json(args.json_path, args.output)
    
    print("=" * 60)
    if success:
        print("🎉 IFC generation completed successfully!")
        print("✅ Ready for use in Solibri and BIMvision")
    else:
        print("❌ IFC generation failed!")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    # If run without arguments, use the default processed_images.json path
    if len(sys.argv) == 1:
        # Try to find processed_images.json in common locations
        possible_paths = [
            "output/processed_images.json",
            config.OUTPUT_PROCESSED_DATA_FILE if hasattr(config, 'OUTPUT_PROCESSED_DATA_FILE') else None,
            "C:/Users/HTO334/OneDrive - AFRY/Pictures/e105-360 images/test/output/processed_images.json"
        ]
        
        json_path = None
        for path in possible_paths:
            if path and os.path.exists(path):
                json_path = path
                break
        
        if json_path:
            print(f"📁 Using found JSON file: {json_path}")
            success = generate_ifc_from_json(json_path)
            exit(0 if success else 1)
        else:
            print("❌ No processed_images.json file found in default locations")
            print("\nUsage:")
            print("  python json_to_ifc.py <path_to_processed_images.json>")
            print("  python json_to_ifc.py processed_images.json -o output.ifc")
            exit(1)
    else:
        exit(main())
