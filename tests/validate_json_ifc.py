"""
Quick validation script for the JSON-generated IFC file
"""

import ifcopenshell
import sys

def validate_json_ifc():
    """Validate the IFC file generated from JSON"""
    ifc_path = "C:/Users/HTO334/OneDrive - AFRY/Pictures/e105-360 images/test/output/markers_from_json.ifc"
    
    try:
        ifc_file = ifcopenshell.open(ifc_path)
        print(f"✅ Schema: {ifc_file.schema}")
        
        markers = ifc_file.by_type("IfcBuildingElementProxy")
        print(f"✅ Markers: {len(markers)}")
        
        projects = ifc_file.by_type("IfcProject")
        print(f"✅ Projects: {len(projects)}")
        
        if markers:
            first_marker = markers[0]
            print(f"✅ First marker: {first_marker.Name}")
        
        print("✅ JSON-generated IFC file is valid!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    validate_json_ifc()
