"""
Test script to verify IFC structure creation without requiring images
"""

import os
import sys
sys.path.append('src')

from ifc_exporter import IFCExporter
import config

def test_ifc_creation():
    """Test basic IFC file creation with dummy data"""
    
    # Create dummy image data (similar to what would come from real images)
    dummy_images = [
        {
            'filename': 'test_image_1.jpg',
            'filepath': '/test/path/test_image_1.jpg',
            'latitude': 59.3293,  # Stockholm coordinates
            'longitude': 18.0686,
            'elevation': 50.0,
            'date_taken': '2024:01:15 10:30:00',
            'image_url': 'https://example.com/images/test_image_1.jpg',
            'transformed_x': 674032.5,  # Example EPSG:5110 coordinates
            'transformed_y': 6580821.3,
            'transformed_z': 50.0
        },
        {
            'filename': 'test_image_2.jpg',
            'filepath': '/test/path/test_image_2.jpg',
            'latitude': 59.3300,
            'longitude': 18.0700,
            'elevation': 55.0,
            'date_taken': '2024:01:15 11:00:00',
            'image_url': 'https://example.com/images/test_image_2.jpg',
            'transformed_x': 674142.1,
            'transformed_y': 6580898.7,
            'transformed_z': 55.0
        }
    ]
    
    print("Testing IFC structure creation...")
    
    # Create exporter
    exporter = IFCExporter()
    
    # Test output path
    output_path = os.path.join('output', 'test_structure.ifc')
    
    try:
        # Export markers
        exporter.export_markers(dummy_images, output_path)
        
        print(f"✓ IFC file created successfully at: {output_path}")
        
        # Check file size
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✓ File size: {file_size} bytes")
            
            if file_size > 1000:  # Should be substantial for a valid IFC
                print("✓ File appears to have substantial content")
                return True
            else:
                print("⚠ File seems too small, may be incomplete")
                return False
        else:
            print("✗ Output file was not created")
            return False
            
    except Exception as e:
        print(f"✗ Error during export: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("IFC Structure Test")
    print("=" * 50)
    
    success = test_ifc_creation()
    
    print("=" * 50)
    if success:
        print("✓ Test completed successfully!")
        print("The IFC exporter is working correctly.")
    else:
        print("✗ Test failed!")
        print("There are issues with the IFC exporter.")
    print("=" * 50)
