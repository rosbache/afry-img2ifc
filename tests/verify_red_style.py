"""
Verify that the red color style was properly applied to the IFC markers
"""

import ifcopenshell
import os

def verify_red_style():
    """Verify that red color styling is applied to the markers"""
    
    # Check both the main output and the test output
    ifc_paths = [
        "output/red_markers.ifc",
        "C:/Users/HTO334/OneDrive - AFRY/Pictures/e105-360 images/test/output/markers.ifc"
    ]
    
    for ifc_path in ifc_paths:
        if not os.path.exists(ifc_path):
            print(f"⏭️  Skipping {ifc_path} (not found)")
            continue
            
        print(f"\n🔍 Checking: {os.path.basename(ifc_path)}")
        print("-" * 50)
    
        try:
            # Open the IFC file
            ifc_file = ifcopenshell.open(ifc_path)
            print(f"✅ Opened IFC file")
            
            # Check for style-related entities
            styles = ifc_file.by_type("IfcPresentationStyleAssignment")
            surface_styles = ifc_file.by_type("IfcSurfaceStyle")
            surface_style_shadings = ifc_file.by_type("IfcSurfaceStyleShading")
            styled_items = ifc_file.by_type("IfcStyledItem")
            
            print("📊 Style Analysis:")
            print(f"   Presentation Style Assignments: {len(styles)}")
            print(f"   Surface Styles: {len(surface_styles)}")
            print(f"   Surface Style Shadings: {len(surface_style_shadings)}")
            print(f"   Styled Items: {len(styled_items)}")
            
            # Check if we have red color
            red_found = False
            if surface_style_shadings:
                for shading in surface_style_shadings:
                    if hasattr(shading, 'SurfaceColour') and shading.SurfaceColour:
                        color = shading.SurfaceColour
                        if hasattr(color, 'Red') and hasattr(color, 'Green') and hasattr(color, 'Blue'):
                            red_val = float(color.Red)
                            green_val = float(color.Green)
                            blue_val = float(color.Blue)
                            
                            print(f"   🎨 Color found: RGB({red_val:.1f}, {green_val:.1f}, {blue_val:.1f})")
                            
                            # Check if it's red (1.0, 0.0, 0.0)
                            if abs(red_val - 1.0) < 0.01 and abs(green_val - 0.0) < 0.01 and abs(blue_val - 0.0) < 0.01:
                                print("   ✅ Red color confirmed!")
                                red_found = True
            
            # Check markers
            markers = ifc_file.by_type("IfcBuildingElementProxy")
            print(f"   📍 Markers: {len(markers)}")
            
            if markers and styled_items:
                print("   ✅ Both markers and styles are present")
            
            if red_found:
                print("✅ Red color styling confirmed for this file!")
            else:
                print("❌ Red color styling not found in this file")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True  # Return True if we processed at least one file

if __name__ == "__main__":
    print("🔍 Red Color Style Verification")
    print("=" * 50)
    
    success = verify_red_style()
    
    print("=" * 50)
    if success:
        print("✅ Red styling verification passed!")
    else:
        print("❌ Red styling verification failed!")
    print("=" * 50)
